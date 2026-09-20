"""Public owner for governed pipeline source-read orchestration."""

from __future__ import annotations

from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io import read_lakehouse_table, read_warehouse_query, read_warehouse_table
from fabricops_kit.pipeline.shared import (
    capture_source_observation,
    resolve_catalogue_table_identity,
    resolve_incremental_source_scope,
    resolve_incremental_observation_columns,
    resolve_pipeline_data_contract,
    resolve_physical_table_identity,
)


def _warehouse_incremental_query(identity: dict[str, Any], scope: dict[str, Any]) -> str:
    """Build framework-owned SQL pushdown for one resolved incremental scope."""
    schema = str(identity["schema"]).replace("]", "]]")
    table = str(identity["table_name"]).replace("]", "]]")
    scope_type = scope["type"]
    if scope_type == "full":
        return f"SELECT * FROM [{schema}].[{table}]"
    column = str(scope["column"]).replace("]", "]]")
    if scope_type == "watermark":
        value = str(scope["after"]).replace("'", "''")
        return f"SELECT * FROM [{schema}].[{table}] WHERE [{column}] > '{value}'"
    values = ", ".join(
        "'" + str(value).replace("'", "''") + "'" for value in scope["values"]
    )
    if not values:
        return f"SELECT * FROM [{schema}].[{table}] WHERE 1 = 0"
    return f"SELECT * FROM [{schema}].[{table}] WHERE [{column}] IN ({values})"


def _filter_lakehouse_incremental(dataframe: Any, scope: dict[str, Any]) -> Any:
    """Apply a resolved incremental scope while preserving Spark pushdown."""
    if scope["type"] == "full":
        return dataframe
    if not scope["has_data"]:
        return dataframe.limit(0)
    from pyspark.sql import functions as F

    if scope["type"] == "watermark":
        return dataframe.where(F.col(scope["column"]) > F.lit(scope["after"]))
    return dataframe.where(F.col(scope["column"]).isin(scope["values"]))


def pipeline_read(
    *,
    store: str | None = None,
    schema: str | None = None,
    table_name: str | None = None,
    table_id: str | None = None,
    query: str | None = None,
    read_mode: str = "full",
    target_table_id: str | None = None,
    spark_session=None,
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
    read_mode : {"full", "incremental"}, default="full"
        Explicit source read behaviour. ``full`` preserves the complete-source
        read. ``incremental`` resolves unconsumed work from the last Source
        Observation committed for this exact source-to-target relationship.
    target_table_id : str, optional
        Canonical governed target being prepared. It is accepted for both read
        modes so target flows can use one consistent call shape, and is required
        when ``read_mode="incremental"``.
    spark_session : object, optional
        Spark session forwarded to the selected foundational reader instead of relying on notebook-global ``spark``.
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
        - ``read_mode``: the explicit source read mode.
        - ``has_data`` and ``should_process``: whether this read contributes
          unconsumed work. Full reads return ``True`` without triggering a count.
        - ``scope``: a compact summary of the resolved full, bootstrap,
          watermark, or partition scope. Partition scope includes removed
          values that require target reconciliation; no metadata rows are exposed.

    Raises
    ------
    ValueError
        If identity inputs conflict or are incomplete, the source is not
        registered, its configured store kind is unsupported, or a query is
        supplied for a Lakehouse source, incremental mode has no target, or
        project-owned Warehouse SQL is combined with incremental mode.

    Notes
    -----
    The governed orchestration performs these mechanical steps:

    1. Resolve the canonical source ``table_id``.
    2. Resolve the configured physical source identity.
    3. Infer whether that configured source is a Lakehouse or Warehouse.
    4. For incremental reads, observe the complete physical source, resolve the
       last committed state for the exact target, and derive watermark or
       changed-partition scope. A missing baseline deterministically bootstraps
       with a complete read.
    5. Select and call ``read_lakehouse_table``, ``read_warehouse_table``, or
       framework-owned ``read_warehouse_query`` pushdown.
    6. Capture transient current-run Source Observation state without advancing
       accepted progress. Only successful target publication commits it.
    7. Return the DataFrame, explicit ``table_id``, and small source metadata
       required by the notebook.

    Higher-level governed pipeline code normally uses ``pipeline_read``.
    Foundational readers remain available for direct lower-level or
    general-purpose Fabric reads that do not need pipeline orchestration.
    ``pipeline_read`` orchestrates governed table sources only. Raw Lakehouse
    Files do not have a canonical ``table_id`` and should continue to use the
    foundational CSV, Excel, JSON, or Parquet readers directly.

    Incremental Warehouse reads reject caller-owned ``query`` SQL because
    FabricOps cannot safely compose arbitrary SQL with its target-specific
    progress predicate. Source Drift remains a separate compatibility check;
    incremental scope answers only what this target has not consumed.

    This function does not execute Freshness, Source Drift, Schema, DQ, or
    Sensitive Data checks. It also does not profile
    data, transform rows, or write a pipeline target. Those meaningful
    engineering decisions remain explicit in ``02_pipeline`` and
    ``03_incremental_pipeline``.

    With ``verbose=True``, a Warehouse table read reports a line such as
    ``FabricOps Read → Warehouse table 'product.demo.orders' → read_warehouse_table``.

    Examples
    --------
    Read a governed table without knowing whether ``source`` resolves to a
    Lakehouse or Warehouse:

    >>> result = pipeline_read(
    ...     store="Bronze",
    ...     schema="demo",
    ...     table_name="orders",
    ... )
    >>> orders_df = result["dataframe"]
    >>> orders_table_id = result["table_id"]

    Read only work not yet committed for one target:

    >>> result = pipeline_read(
    ...     store="Bronze", schema="demo", table_name="orders",
    ...     read_mode="incremental", target_table_id=target_table_id,
    ... )
    >>> result["should_process"]
    True

    Read a governed Warehouse source through project-owned SQL:

    >>> result = pipeline_read(
    ...     store="Gold",
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
    read_mode = str(read_mode or "").strip().lower()
    if read_mode not in {"full", "incremental"}:
        raise ValueError("read_mode must be 'full' or 'incremental'.")
    if read_mode == "incremental" and not str(target_table_id or "").strip():
        raise ValueError("target_table_id is required when read_mode='incremental'.")
    if read_mode == "incremental" and query is not None:
        raise ValueError("query cannot be combined with read_mode='incremental'; FabricOps owns the incremental predicate.")
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

    canonical_target_id = str(target_table_id).strip() if target_table_id is not None else None

    contract = resolve_pipeline_data_contract(
        config, env, str(identity["table_id"]), context=context
    )
    has_contract = contract is not None
    incremental_columns = (
        resolve_incremental_observation_columns(identity, contract)
        if read_mode == "incremental"
        else None
    )
    store_label = "Lakehouse" if store_kind == "lakehouse" else "Warehouse"
    source_parts = [f"Object: {store_label}", f"Store: {identity['store']}"]
    if identity.get("schema"):
        source_parts.append(f"Schema: {identity['schema']}")
    source_parts.append(f"Table: {identity['table_name']}")
    io_context = {**context, "_fabricops_suppress_io_log": True}
    if store_kind == "lakehouse":
        reader_name = "read_lakehouse_table"
    elif query is not None or read_mode == "incremental":
        reader_name = "read_warehouse_query"
    else:
        reader_name = "read_warehouse_table"

    if verbose:
        contract_label = "selected" if has_contract else "none"
        print("FabricOps Read")
        print(f"1. Source → {' | '.join(source_parts)}")
        print(f"   Identity → {identity['table_id']}")
        print(f"2. Data Contract → {contract_label}")
        print(f"3. Physical read → {reader_name}")

    observation = None
    scope: dict[str, Any] = {"type": "full", "first_run": False}
    if store_kind == "lakehouse":
        complete_dataframe = read_lakehouse_table(str(identity["table_name"]), store=str(identity["store"]), schema=identity.get("schema"), spark_session=spark_session, context=io_context)
        if read_mode == "incremental":
            observation = capture_source_observation(
                table_id=str(identity["table_id"]),
                dataframe=complete_dataframe,
                incremental_columns=incremental_columns,
            )
            scope = resolve_incremental_source_scope(
                source_table_id=str(identity["table_id"]),
                target_table_id=str(canonical_target_id),
                observation=observation,
            )
            dataframe = _filter_lakehouse_incremental(complete_dataframe, scope)
        else:
            dataframe = complete_dataframe
    elif query is not None:
        dataframe = read_warehouse_query(query, store=str(identity["store"]), spark_session=spark_session, context=io_context)
    elif read_mode == "incremental":
        observation = capture_source_observation(
            table_id=str(identity["table_id"]),
            incremental_columns=incremental_columns,
        )
        scope = resolve_incremental_source_scope(
            source_table_id=str(identity["table_id"]),
            target_table_id=str(canonical_target_id),
            observation=observation,
        )
        dataframe = read_warehouse_query(
            _warehouse_incremental_query(identity, scope),
            store=str(identity["store"]),
            spark_session=spark_session,
            context=io_context,
        )
    else:
        dataframe = read_warehouse_table(
            str(identity["schema"]),
            str(identity["table_name"]),
            store=str(identity["store"]),
            spark_session=spark_session,
            context=io_context,
        )

    if has_contract and observation is None:
        observation = capture_source_observation(
            table_id=str(identity["table_id"]), dataframe=dataframe
        )
        observation_label = (
            "captured current-run state"
            if observation is not None
            else "no Source Drift observation configured"
        )
    elif observation is not None:
        scope_label = "bootstrap full read" if scope.get("first_run") else scope["type"]
        observation_label = f"captured; target-specific {scope_label} scope resolved"
    else:
        observation_label = "skipped; no selected Data Contract"

    if verbose:
        print(f"4. Source Observation → {observation_label}")
        print("Result → DataFrame returned; checks, profiling, transformations, and writes remain explicit.")

    return {
        "dataframe": dataframe,
        "table_id": str(identity["table_id"]),
        "is_query": query is not None,
        "has_contract": has_contract,
        "read_mode": read_mode,
        "has_data": bool(scope.get("has_data", True)),
        "should_process": bool(scope.get("has_data", True)),
        "scope": {
            name: value
            for name, value in scope.items()
            if name
            in {
                "type",
                "first_run",
                "has_data",
                "column",
                "after",
                "through",
                "values",
                "removed_values",
            }
        },
    }
