"""Public owner for governed pipeline target-write orchestration."""

from __future__ import annotations

import json
from typing import Any

from fabricops_kit.config.metadata_schemas import (
    coerce_metadata_row_types,
    metadata_table_physical_schema,
    metadata_table_schema_registry,
)
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import resolve_configured_lakehouse_table
from fabricops_kit.pipeline.shared import (
    add_target_audit_fields,
    catalogue_authored_processing,
    resolve_catalogue_table_identity,
    resolve_physical_table_identity,
    resolve_table_processing_definition,
    resolve_target_audit_fields,
)

CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"


def _persist_target_processing(
    *,
    identity: dict[str, Any],
    processing: dict[str, Any],
    audit: dict[str, Any],
    config: Any,
    env: str,
    dataframe: Any,
) -> None:
    """Persist the resolved target processing definition on its Catalogue table row."""
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - depends on Fabric/Delta runtime
        raise RuntimeError(
            "Delta Lake merge support is required to persist target processing metadata."
        ) from exc

    parameter_names = {
        "partition_column",
        "key_columns",
        "effective_column",
        "tracked_columns",
    }
    parameters = {name: processing[name] for name in parameter_names if name in processing}
    row = coerce_metadata_row_types(
        CATALOGUE_TABLE,
        {
            "metadata_level": "table",
            "table_id": str(identity["table_id"]),
            "column_id": None,
            "environment_name": env,
            "store_type": str(identity.get("store_type") or identity.get("store_kind") or "").lower(),
            "layer": str(identity["store"]),
            "schema_name": identity.get("schema"),
            "table_name": str(identity["table_name"]),
            "column_name": None,
            "data_type": None,
            "load_strategy": str(processing["load_strategy"]),
            "load_strategy_parameters_json": json.dumps(
                parameters, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ),
            "first_profiled_at": None,
            "last_profiled_at": None,
            "is_active": True,
            **audit,
        },
    )
    spark_session = dataframe.sparkSession
    source = spark_session.createDataFrame(
        [row], schema=metadata_table_schema_registry()[CATALOGUE_TABLE]
    )
    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        "metadata",
        CATALOGUE_TABLE,
        metadata_table_physical_schema(config, CATALOGUE_TABLE),
        context={"config": config, "env": env},
    )
    target = DeltaTable.forPath(spark_session, path)
    (
        target.alias("target")
        .merge(
            source.alias("source"),
            "target.environment_name = source.environment_name "
            "AND target.metadata_level = 'table' "
            "AND target.table_id = source.table_id "
            "AND target.column_id IS NULL",
        )
        .whenMatchedUpdate(
            set={
                "store_type": "source.store_type",
                "layer": "source.layer",
                "schema_name": "source.schema_name",
                "table_name": "source.table_name",
                "load_strategy": "source.load_strategy",
                "load_strategy_parameters_json": "source.load_strategy_parameters_json",
                "is_active": "true",
                "_committed_by": "source._committed_by",
                "_committed_at": "source._committed_at",
                "_workspace_id": "source._workspace_id",
                "_workspace_name": "source._workspace_name",
                "_notebook_id": "source._notebook_id",
                "_notebook_name": "source._notebook_name",
                "_metadata_lakehouse_name": "source._metadata_lakehouse_name",
                "_activity_id": "source._activity_id",
            }
        )
        .whenNotMatchedInsertAll()
        .execute()
    )


def _delta_literal(value: Any) -> str:
    """Return a safely encoded primitive Delta predicate literal."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int | float):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def _replace_where(partition_column: str, values: list[Any]) -> str:
    """Return a safely quoted Delta partition-replacement predicate."""
    quoted = str(partition_column).replace("`", "``")
    return f"`{quoted}` IN ({', '.join(_delta_literal(value) for value in values)})"


def _write_scope() -> dict[str, Any]:
    """Return the default complete write scope."""
    return {"type": "full_dataset"}


def _source_table_ids(values: list[str] | tuple[str, ...] | None) -> list[str]:
    """Return unique canonical source identities explicitly owned by this target."""
    if not isinstance(values, list | tuple) or not values:
        raise ValueError(
            "source_table_ids must identify the governed sources that feed this target. "
            "FabricOps does not infer source ownership from activity-wide reads or Spark plans."
        )
    source_ids: list[str] = []
    for value in values:
        source_id = str(value).strip() if isinstance(value, str) else ""
        if not source_id:
            raise ValueError("source_table_ids must contain only non-empty canonical table_id strings.")
        if source_id not in source_ids:
            source_ids.append(source_id)
    return source_ids


def _validate_target_writer_ownership(*, table_id: str, processing: dict[str, Any], audit: dict[str, Any]) -> None:
    """Require the current notebook to match the writer frozen in the contract."""
    if processing.get("source") != "data_contract":
        return
    owner_name = str(processing.get("owner_notebook_name") or "").strip()
    if not owner_name:
        raise ValueError(
            f"Data Contract for target table_id {table_id!r} has no owning notebook_name; "
            "freeze the contract from the target's owning pipeline before writing."
        )
    owner_id = str(processing.get("owner_notebook_id") or "").strip()
    current_name = str(audit.get("_notebook_name") or "").strip()
    current_id = str(audit.get("_notebook_id") or "").strip()
    if current_name != owner_name:
        raise ValueError(
            f"Target table_id {table_id!r} is owned by notebook {owner_name!r} "
            f"(contract notebook_id {owner_id!r}); current writer is {current_name or current_id!r} "
            f"(runtime notebook_id {current_id!r}). "
            "One governed target table_id must have one owning pipeline/notebook writer."
        )


def pipeline_write(
    df,
    *,
    store: str | None = None,
    schema: str | None = None,
    table_name: str | None = None,
    table_id: str | None = None,
    load_strategy: str | None = None,
    load_strategy_parameters: dict[str, Any] | None = None,
    source_table_ids: list[str] | tuple[str, ...] | None = None,
    repartition_by=None,
    options: dict[str, Any] | None = None,
    verbose: bool = True,
) -> dict[str, str]:
    """Publish one governed pipeline table target through its configured Fabric store.

    ``pipeline_write`` is the governed pipeline-orchestration equivalent of
    :func:`write_lakehouse_table` and :func:`write_warehouse_table`. Describe
    the governed target once; FabricOps resolves its canonical identity and
    configured store, resolves governed processing from the selected or active
    Data Contract, selects the appropriate physical publication path, and
    commits pipeline-success metadata only after publication succeeds.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Prepared target DataFrame after explicit target checks have passed.
    store : str, optional
        Configured store key. Supply it with ``table_name`` and optional
        ``schema`` instead of ``table_id``.
    schema : str, optional
        Physical target schema when the configured store uses schemas.
    table_name : str, optional
        Physical target table name. Required with ``store`` when ``table_id``
        is omitted.
    table_id : str, optional
        Canonical registered target identity. This identity form is mutually
        exclusive with ``store``, ``schema``, and ``table_name``.
    load_strategy : {"overwrite", "append", "scd1", "scd2"}, optional
        Development-authored processing proposal. Selected or frozen contract
        validation applies in Development, and the active approved Data
        Contract remains authoritative in Production.
    load_strategy_parameters : dict, optional
        Development-authored strategy parameters, such as key, effective,
        tracked, or partition columns, subject to contract validation.
    source_table_ids : list[str] or tuple[str, ...], optional
        Canonical identities of the exact governed sources that feed this
        target publication. Supply identities returned by ``pipeline_read``.
        FabricOps requires this explicit association because activity-wide
        reads and Spark transformation plans cannot reliably identify which
        source subset produced a particular target DataFrame.
    repartition_by : int or str or list[str] or tuple[str, ...], optional
        Optional Spark repartitioning passed to simple physical writes.
    options : dict, optional
        Additional physical writer options for append or overwrite publication.
    verbose : bool, default=True
        Whether to print one concise orchestration message showing the resolved
        Fabric store type, physical table identity, governed strategy, and
        selected foundational writer or governed SCD publication path. This
        explains hidden routing without exposing implementation plumbing.

    Returns
    -------
    dict
        A deliberately small result containing only the canonical ``table_id``.
        Profile the persisted target through an explicit read-back rather than
        treating the input DataFrame as persisted state.

    Raises
    ------
    ValueError
        If identity inputs conflict or are incomplete, ``source_table_ids`` is
        missing or invalid, governed processing is invalid, ownership does not
        match, or the target store is unsupported.

    Notes
    -----
    The governed orchestration performs these mechanical steps:

    1. Resolve the canonical target ``table_id``.
    2. Resolve the configured physical target identity.
    3. Resolve the selected or active Data Contract.
    4. Resolve the governed load strategy and parameters.
    5. Resolve processing scope.
    6. Apply FabricOps target audit fields.
    7. Validate target notebook ownership.
    8. Select the physical Lakehouse or Warehouse publication implementation.
    9. Perform append/overwrite or dedicated SCD processing.
    10. Persist the resolved target load strategy and parameters on the
        table-level ``METADATA_DATA_CATALOGUE`` row.
    11. Only after physical and Catalogue success, commit target Lineage and
        accepted Source Observation/write-success metadata.
    12. Return a small publication result with no hidden profiling state.

    Callers do not provide a store type, manually resolve ``table_id``, choose
    a Lakehouse versus Warehouse writer, construct processing scope or success
    context, or manually commit Lineage or Source Observation metadata. Callers
    provide only the canonical identities of the sources that actually feed
    this target, rather than internal read or preparation dictionaries. This
    keeps multiple target writes in one activity exact and independent.

    With ``verbose=True``, a simple Lakehouse overwrite reports a line such as
    ``FabricOps Write → Lakehouse table 'unified.demo.curated_orders' → overwrite → write_lakehouse_table``.

    This function does not perform transformations, schema checks, DQ checks,
    Sensitive Data Guardrails, or profiling. Those remain explicit notebook
    engineering and governance steps. ``pipeline_write`` publishes governed
    table targets only. Raw Lakehouse Files do not have a canonical FabricOps
    ``table_id``; direct file-output concerns, if supported in future, belong
    outside this governed table orchestration API.

    Examples
    --------
    Publish without knowing whether ``unified`` is a Lakehouse or Warehouse:

    >>> result = pipeline_write(
    ...     prepared_df, store="unified", schema="demo",
    ...     table_name="curated_orders",
    ...     source_table_ids=[orders_result["table_id"]],
    ... )
    >>> result["table_id"]
    'lakehouse:unified:demo:curated_orders'

    Development may propose processing, without bypassing contract authority:

    >>> pipeline_write(
    ...     prepared_df, store="unified", schema="demo",
    ...     table_name="curated_orders", load_strategy="overwrite",
    ...     source_table_ids=[orders_result["table_id"]],
    ... )

    See Also
    --------
    pipeline_read, write_lakehouse_table, write_warehouse_table,
    profile_table

    """
    from fabricops_kit.io import write_lakehouse_table, write_warehouse_table
    from fabricops_kit.io.shared import execute_warehouse_processing
    from fabricops_kit.pipeline.shared import commit_pipeline_write_success, execute_lakehouse_processing

    config, env, context = resolve_fabric_context()
    coordinates = (store, schema, table_name)
    if table_id and any(value is not None for value in coordinates):
        raise ValueError("table_id cannot be combined with store, schema, or table_name.")
    if not table_id and (store is None or table_name is None):
        raise ValueError("Provide table_id or both store and table_name.")

    if table_id:
        identity = resolve_catalogue_table_identity(config, env, table_id, context=context)
        authored = (
            {"load_strategy": load_strategy, **(load_strategy_parameters or {})}
            if load_strategy is not None
            else catalogue_authored_processing(identity)
        )
    else:
        identity = resolve_physical_table_identity(config, env, store=store, schema=schema, table_name=table_name)
        identity["store_type"] = identity["store_kind"]
        authored = {"load_strategy": load_strategy, **(load_strategy_parameters or {})}

    processing = resolve_table_processing_definition(
        config, env, str(identity["table_id"]), context=context, authored_processing=authored
    )
    publication_source_ids = _source_table_ids(source_table_ids)
    scope = _write_scope()
    strategy = str(processing.get("load_strategy") or "")
    store_kind = str(identity.get("store_type") or identity.get("store_kind") or "").lower()
    physical_identity = ".".join(
        str(value) for value in (identity.get("store"), identity.get("schema"), identity.get("table_name")) if value
    )
    physical_options = dict(options or {})
    partition_column = str(processing.get("partition_column") or "")
    if strategy == "overwrite" and partition_column:
        if store_kind != "lakehouse":
            raise ValueError("Partition-scoped overwrite is supported only for Lakehouse targets.")
        if partition_column not in df.columns:
            raise ValueError(f"Target partition column {partition_column!r} is missing from the prepared DataFrame.")
        from pyspark.sql import functions as F

        values = [row[partition_column] for row in df.select(partition_column).distinct().collect()]
        if not values or any(value is None for value in values):
            raise ValueError("Target partition-scoped overwrite requires non-null partition values.")
        if "_partition_bucket" in df.columns:
            raise ValueError("_partition_bucket is a reserved FabricOps technical column and must not be supplied.")
        df = df.withColumn("_partition_bucket", F.col(partition_column))
        scope = {"type": "partition", "column": partition_column, "values": values}
        physical_options["replaceWhere"] = _replace_where("_partition_bucket", values)

    audit = resolve_target_audit_fields(context)
    _validate_target_writer_ownership(table_id=str(identity["table_id"]), processing=processing, audit=audit)
    prepared_df = add_target_audit_fields(df, audit)
    if strategy == "scd2":
        from pyspark.sql import functions as F

        effective = str(processing["effective_column"])
        effective_type = prepared_df.schema[effective].dataType
        prepared_df = (
            prepared_df.withColumn("_effective_from", F.col(effective))
            .withColumn("_effective_to", F.lit(None).cast(effective_type))
            .withColumn("_is_current", F.lit(True))
        )

    if verbose:
        store_label = "Lakehouse" if store_kind == "lakehouse" else "Warehouse"
        if strategy in {"scd1", "scd2"}:
            processing_label = "governed Delta merge" if store_kind == "lakehouse" else "governed Warehouse merge"
            print(f"FabricOps Write → {store_label} table '{physical_identity}' → {strategy.upper()} → {processing_label}")
        else:
            writer_name = "write_lakehouse_table" if store_kind == "lakehouse" else "write_warehouse_table"
            print(f"FabricOps Write → {store_label} table '{physical_identity}' → {strategy} → {writer_name}")

    if store_kind == "lakehouse":
        if strategy in {"append", "overwrite"}:
            write_lakehouse_table(
                prepared_df,
                str(identity["table_name"]),
                store=str(identity["store"]),
                schema=identity.get("schema"),
                mode=strategy,
                repartition_by=repartition_by,
                options=physical_options,
                verbose=False,
                context=context,
            )
        elif strategy in {"scd1", "scd2"}:
            execute_lakehouse_processing(
                prepared_df,
                table_name=str(identity["table_name"]),
                store=str(identity["store"]),
                schema=identity.get("schema"),
                processing=processing,
                scope=scope,
                context=context,
            )
        else:
            raise ValueError(f"Unsupported governed load strategy {strategy!r}.")
    elif store_kind == "warehouse":
        if strategy in {"append", "overwrite"}:
            write_warehouse_table(
                prepared_df,
                str(identity["schema"]),
                str(identity["table_name"]),
                store=str(identity["store"]),
                mode=strategy,
                repartition_by=repartition_by,
                options=physical_options,
                context=context,
            )
        elif strategy in {"scd1", "scd2"}:
            execute_warehouse_processing(
                prepared_df,
                schema=str(identity["schema"]),
                table_name=str(identity["table_name"]),
                store=str(identity["store"]),
                processing=processing,
                context=context,
                options=physical_options,
            )
        else:
            raise ValueError(f"Unsupported governed load strategy {strategy!r}.")
    else:
        raise ValueError(f"Configured store has unsupported kind {store_kind or '<blank>'!r}.")

    _persist_target_processing(
        identity=identity,
        processing=processing,
        audit=audit,
        config=config,
        env=env,
        dataframe=df,
    )
    commit_pipeline_write_success(
        {
            "target_table_id": str(identity["table_id"]),
            "source_table_ids": publication_source_ids,
            "activity_id": audit["_activity_id"],
            "notebook_name": audit["_notebook_name"],
            "notebook_id": audit["_notebook_id"],
            "context": context,
        }
    )
    return {"table_id": str(identity["table_id"])}
