"""Public owner for governed pipeline source-read orchestration."""

from __future__ import annotations

from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io import read_lakehouse_table, read_warehouse_query, read_warehouse_table
from fabricops_kit.pipeline.shared import (
    persist_lineage_participation,
    resolve_catalogue_table_identity,
    resolve_physical_table_identity,
)


def pipeline_read(
    *,
    target: str | None = None,
    schema: str | None = None,
    table_name: str | None = None,
    table_id: str | None = None,
    query: str | None = None,
) -> dict[str, Any]:
    """Read one governed pipeline source through its configured Fabric store.

    Parameters
    ----------
    target : str, optional
        Configured source target key. Supply it with ``table_name`` instead of
        ``table_id``.
    schema : str, optional
        Physical source schema, when the configured store uses schemas.
    table_name : str, optional
        Physical source table name. Required with ``target`` when ``table_id``
        is omitted.
    table_id : str, optional
        Canonical registered source identity. Mutually exclusive with
        ``target``, ``schema``, and ``table_name``.
    query : str, optional
        Read-only SQL for a configured Warehouse source. The supplied source
        identity remains the governed Lineage participant; FabricOps does not
        infer table identity by parsing SQL.

    Returns
    -------
    dict
        A small result containing ``dataframe``, canonical ``table_id``, and
        ``is_query``. ``is_query`` distinguishes a derived Warehouse query
        result from a complete physical-table read.

    Raises
    ------
    ValueError
        If identity inputs conflict or are incomplete, the source is not
        registered, its configured store kind is unsupported, or a query is
        supplied for a Lakehouse source.

    Notes
    -----
    This orchestration resolves canonical and physical source identity,
    registers source participation in ``METADATA_DATA_LINEAGE`` exactly once,
    establishes source profile-registration context, and delegates the
    physical read to the foundational Fabric I/O API. It does not run source
    observation, freshness, stability, schema, DQ, or profiling checks.

    Examples
    --------
    >>> result = pipeline_read(target="source", schema="sales", table_name="orders")
    >>> orders_df = result["dataframe"]
    >>> result["table_id"]
    'lakehouse:source:sales:orders'

    See Also
    --------
    read_lakehouse_table, read_warehouse_table, read_warehouse_query,
    profile_and_register_table

    """
    coordinates = (target, schema, table_name)
    if table_id and any(value is not None for value in coordinates):
        raise ValueError("table_id cannot be combined with target, schema, or table_name.")
    if not table_id and (target is None or table_name is None):
        raise ValueError("Provide table_id or both target and table_name.")

    config, env, context = resolve_fabric_context()
    if table_id:
        identity = resolve_catalogue_table_identity(config, env, table_id, context=context)
    else:
        identity = resolve_physical_table_identity(
            config, env, target=target, schema=schema, table_name=table_name
        )
    store_kind = str(identity.get("store_type") or identity.get("store_kind") or "").lower()
    identity["store_type"] = store_kind
    identity["store_kind"] = store_kind

    if store_kind == "lakehouse":
        if query is not None:
            raise ValueError("query is supported only for a configured Warehouse source, not a Lakehouse source.")
        dataframe = read_lakehouse_table(table_id=str(identity["table_id"]), context=context)
    elif store_kind == "warehouse":
        if query is not None:
            dataframe = read_warehouse_query(query, target=str(identity["target"]), context=context)
        else:
            dataframe = read_warehouse_table(
                str(identity["schema"]),
                str(identity["table_name"]),
                target=str(identity["target"]),
                context=context,
            )
    else:
        raise ValueError(
            f"Configured source has unsupported store kind {store_kind or '<blank>'!r}; "
            "supported kinds are: lakehouse, warehouse."
        )

    persist_lineage_participation(
        table_id=str(identity["table_id"]), pipeline_role="source", context=dict(context)
    )
    context["_fabricops_active_profile_registration"] = {
        "profile_role": "source",
        "table": dict(identity),
    }
    return {
        "dataframe": dataframe,
        "table_id": str(identity["table_id"]),
        "is_query": query is not None,
    }
