"""Public owner for governed pipeline source-read orchestration."""

from __future__ import annotations

from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io import read_lakehouse_table, read_warehouse_query, read_warehouse_table
from fabricops_kit.pipeline.shared import (
    persist_lineage_participation,
    resolve_catalogue_table_identity,
    resolve_pipeline_data_contract,
    resolve_physical_table_identity,
)


def pipeline_read(
    *,
    store: str | None = None,
    schema: str | None = None,
    table_name: str | None = None,
    table_id: str | None = None,
    query: str | None = None,
    verbose: bool = True,
) -> dict[str, Any]:
    """Read one governed pipeline source through the appropriate Fabric store.

    ``pipeline_read`` is the governed pipeline-orchestration equivalent of the
    foundational :func:`read_lakehouse_table`, :func:`read_warehouse_table`,
    and :func:`read_warehouse_query` readers. Describe the governed source
    once; FabricOps resolves its identity and configured store, selects the
    physical reader, and returns the data needed by the notebook. Callers do
    not supply a store type, resolve a canonical table identity first, or
    choose between Lakehouse and Warehouse table readers.

    Parameters
    ----------
    store : str, optional
        Configured source store key, such as ``"source"`` or ``"product"``.
        Supply it with ``table_name`` and optional ``schema`` instead of
        ``table_id``.
    schema : str, optional
        Physical source schema, when the configured store uses schemas.
    table_name : str, optional
        Physical source table name. Required with ``store`` when ``table_id``
        is omitted. ``store``, optional ``schema``, and ``table_name`` form
        one identity form.
    table_id : str, optional
        Canonical registered source identity. This is the alternative identity
        form and is mutually exclusive with ``store``, ``schema``, and
        ``table_name``.
    query : str, optional
        Read-only SQL for a configured Warehouse source. The supplied source
        identity remains the governed source participant even when the result
        is a projection, filter, join, or aggregation. FabricOps does not infer
        arbitrary source identity by parsing SQL. A query may accompany either
        physical coordinates or ``table_id`` when the resolved store is a
        Warehouse.
    verbose : bool, default=True
        Whether to print one concise orchestration message showing the resolved
        Fabric store type, physical table identity, and selected foundational
        reader. This makes the hidden routing understandable without exposing
        workspace IDs, SQL text, contract payloads, or runtime plumbing.

    Returns
    -------
    dict
        A deliberately small result with these fields:

        - ``dataframe``: the Spark DataFrame returned by the selected
          foundational Fabric I/O reader.
        - ``table_id``: the canonical identity of the governed physical source.
        - ``is_query``: whether ``dataframe`` is a custom Warehouse query
          result rather than the complete physical table.
        - ``has_contract``: whether an environment-selected immutable Data
          Contract applies. The contract record itself is not exposed.

    Raises
    ------
    ValueError
        If identity inputs conflict or are incomplete, the source is not
        registered, its configured store kind is unsupported, or a query is
        supplied for a Lakehouse source.

    Notes
    -----
    The governed orchestration performs these mechanical steps:

    1. Resolve the canonical source ``table_id``.
    2. Resolve the configured physical source identity.
    3. Infer whether that configured source is a Lakehouse or Warehouse.
    4. Select and call ``read_lakehouse_table``, ``read_warehouse_table``, or
       ``read_warehouse_query`` as the foundational physical Fabric I/O boundary.
    5. Register source participation in ``METADATA_DATA_LINEAGE`` exactly once.
    6. Return the DataFrame, explicit ``table_id``, and small source metadata
       required by the notebook.

    Higher-level governed pipeline code normally uses ``pipeline_read``.
    Foundational readers remain available for direct lower-level or
    general-purpose Fabric reads that do not need pipeline orchestration.
    ``pipeline_read`` orchestrates governed table sources only. Raw Lakehouse
    Files do not have a canonical ``table_id`` and should continue to use the
    foundational CSV, Excel, JSON, or Parquet readers directly.

    This function does not execute source observation, Freshness, Source
    Stability, Schema, DQ, or Sensitive Data checks. It also does not profile
    data, transform rows, or write a pipeline target. Those meaningful
    engineering decisions remain explicit in ``02_pipeline``.

    With ``verbose=True``, a Warehouse table read reports a line such as
    ``FabricOps Read → Warehouse table 'product.demo.orders' → read_warehouse_table``.

    Examples
    --------
    Read a governed table without knowing whether ``source`` resolves to a
    Lakehouse or Warehouse:

    >>> result = pipeline_read(
    ...     store="source",
    ...     schema="demo",
    ...     table_name="orders",
    ... )
    >>> orders_df = result["dataframe"]
    >>> orders_table_id = result["table_id"]

    Read a governed Warehouse source through project-owned SQL:

    >>> result = pipeline_read(
    ...     store="product",
    ...     schema="demo",
    ...     table_name="order_history",
    ...     query='''
    ...         SELECT customer_id, COUNT(*) AS order_count
    ...         FROM demo.order_history
    ...         GROUP BY customer_id
    ...     ''',
    ... )
    >>> history_df = result["dataframe"]
    >>> result["is_query"]
    True

    The query result is marked as derived so later notebook logic can use
    ``profile_table(dataframe=history_df)`` without registering it as the
    complete physical ``demo.order_history`` source table.

    See Also
    --------
    read_lakehouse_table, read_warehouse_table, read_warehouse_query,
    profile_table

    """
    coordinates = (store, schema, table_name)
    if table_id and any(value is not None for value in coordinates):
        raise ValueError("table_id cannot be combined with store, schema, or table_name.")
    if not table_id and (store is None or table_name is None):
        raise ValueError("Provide table_id or both store and table_name.")

    config, env, context = resolve_fabric_context()
    if table_id:
        identity = resolve_catalogue_table_identity(config, env, table_id, context=context)
    else:
        identity = resolve_physical_table_identity(
            config, env, store=store, schema=schema, table_name=table_name
        )
    store_kind = str(identity.get("store_type") or identity.get("store_kind") or "").lower()
    identity["store_type"] = store_kind
    identity["store_kind"] = store_kind

    if store_kind not in {"lakehouse", "warehouse"}:
        raise ValueError(
            f"Configured source has unsupported store kind {store_kind or '<blank>'!r}; "
            "supported kinds are: lakehouse, warehouse."
        )
    if store_kind == "lakehouse" and query is not None:
        raise ValueError("query is supported only for a configured Warehouse source, not a Lakehouse source.")

    has_contract = resolve_pipeline_data_contract(
        config, env, str(identity["table_id"]), context=context
    ) is not None
    physical_identity = ".".join(
        str(value) for value in (identity.get("store"), identity.get("schema"), identity.get("table_name")) if value
    )
    if store_kind == "lakehouse":
        if verbose:
            print(f"FabricOps Read → Lakehouse table '{physical_identity}' → read_lakehouse_table")
        dataframe = read_lakehouse_table(table_id=str(identity["table_id"]), context=context)
    else:
        if query is not None:
            if verbose:
                print(f"FabricOps Read → Warehouse query on '{physical_identity}' → read_warehouse_query")
            dataframe = read_warehouse_query(query, store=str(identity["store"]), context=context)
        else:
            if verbose:
                print(f"FabricOps Read → Warehouse table '{physical_identity}' → read_warehouse_table")
            dataframe = read_warehouse_table(
                str(identity["schema"]),
                str(identity["table_name"]),
                store=str(identity["store"]),
                context=context,
            )
    persist_lineage_participation(
        table_id=str(identity["table_id"]), pipeline_role="source", context=dict(context)
    )
    return {
        "dataframe": dataframe,
        "table_id": str(identity["table_id"]),
        "is_query": query is not None,
        "has_contract": has_contract,
    }
