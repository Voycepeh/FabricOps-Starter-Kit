"""Public owner for governed source-read preparation."""

from __future__ import annotations

from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.pipeline.shared import (
    persist_lineage_participation,
    resolve_catalogue_table_identity,
    resolve_physical_table_identity,
)


def read_pipeline_prep(
    source_table_id: str | None = None,
    *,
    source_target: str | None = None,
    source_schema: str | None = None,
    source_table: str | None = None,
) -> dict[str, Any]:
    """Resolve and register one governed source before physically reading it.

    Parameters
    ----------
    source_table_id : str, optional
        Canonical identity of one registered source table. Omit it and supply
        ``source_target``, ``source_schema``, and ``source_table`` to resolve
        the same identity deterministically from configured physical identity.
    source_target : str, optional
        Configured source target key. Mutually exclusive with ``source_table_id``.
    source_schema : str, optional
        Physical source schema, when the configured store uses schemas.
    source_table : str, optional
        Physical source table name. Required with ``source_target`` when
        ``source_table_id`` is omitted.

    Returns
    -------
    dict
        Canonical ``table_id`` and resolved physical ``source`` identity. The
        resolved table is also recorded as source Lineage for the current
        activity.

    Raises
    ------
    ValueError
        If the source identity is incomplete, conflicting, or is not registered.

    Notes
    -----
    This preparation boundary identifies the source and registers its Lineage;
    it does not read business rows or make incremental-processing decisions.
    Use the resolved ``table_id`` with :func:`read_lakehouse_table`, or use the
    resolved source coordinates when reading a Warehouse query.

    Examples
    --------
    >>> prep = read_pipeline_prep(
    ...     source_target="source",
    ...     source_schema="dbo",
    ...     source_table="bookings",
    ... )
    >>> prep["table_id"]
    'warehouse:source:dbo:bookings'

    See Also
    --------
    write_pipeline_prep, read_lakehouse_table, read_warehouse_table

    """
    if not source_table_id and (source_target is None or source_table is None):
        raise ValueError("Provide source_table_id or both source_target and source_table.")
    config, env, context = resolve_fabric_context()
    source_coordinates = (source_target, source_schema, source_table)
    if source_table_id and any(value is not None for value in source_coordinates):
        raise ValueError("source_table_id cannot be combined with source_target, source_schema, or source_table.")
    if source_table_id:
        source_identity = resolve_catalogue_table_identity(config, env, source_table_id, context=context)
    else:
        source_identity = resolve_physical_table_identity(
            config, env, target=source_target, schema=source_schema, table_name=source_table
        )
    source_identity["store_type"] = source_identity.get("store_type") or source_identity["store_kind"]
    source_identity["store_kind"] = source_identity["store_type"]
    persist_lineage_participation(
        table_id=str(source_identity["table_id"]),
        pipeline_role="source",
        context=dict(context),
    )
    context["_fabricops_active_profile_registration"] = {
        "profile_role": "source",
        "table": dict(source_identity),
    }
    return {"table_id": source_identity["table_id"], "source": source_identity}
