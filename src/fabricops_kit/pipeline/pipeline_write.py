"""Public owner for governed pipeline target-write orchestration."""

from __future__ import annotations

from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.pipeline.shared import (
    add_target_audit_fields,
    catalogue_authored_processing,
    resolve_catalogue_table_identity,
    resolve_physical_table_identity,
    resolve_table_processing_definition,
    resolve_target_audit_fields,
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
    target: str | None = None,
    schema: str | None = None,
    table_name: str | None = None,
    table_id: str | None = None,
    load_strategy: str | None = None,
    load_strategy_parameters: dict[str, Any] | None = None,
    source_table_ids: list[str] | tuple[str, ...] | None = None,
    repartition_by=None,
    options: dict[str, Any] | None = None,
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
    target : str, optional
        Configured target key. Supply it with ``table_name`` and optional
        ``schema`` instead of ``table_id``.
    schema : str, optional
        Physical target schema when the configured store uses schemas.
    table_name : str, optional
        Physical target table name. Required with ``target`` when ``table_id``
        is omitted.
    table_id : str, optional
        Canonical registered target identity. This identity form is mutually
        exclusive with ``target``, ``schema``, and ``table_name``.
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
    10. Only after physical success, commit target Lineage and accepted Source
        Observation/write-success metadata.
    11. Establish target profile-registration context.
    12. Return a small publication result.

    Callers do not provide a store type, manually resolve ``table_id``, choose
    a Lakehouse versus Warehouse writer, construct processing scope or success
    context, or manually commit Lineage or Source Observation metadata. Callers
    provide only the canonical identities of the sources that actually feed
    this target, rather than internal read or preparation dictionaries. This
    keeps multiple target writes in one activity exact and independent.

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
    ...     prepared_df, target="unified", schema="demo",
    ...     table_name="curated_orders",
    ...     source_table_ids=[orders_result["table_id"]],
    ... )
    >>> result["table_id"]
    'lakehouse:unified:demo:curated_orders'

    Development may propose processing, without bypassing contract authority:

    >>> pipeline_write(
    ...     prepared_df, target="unified", schema="demo",
    ...     table_name="curated_orders", load_strategy="overwrite",
    ...     source_table_ids=[orders_result["table_id"]],
    ... )

    See Also
    --------
    pipeline_read, write_lakehouse_table, write_warehouse_table,
    profile_and_register_table

    """
    from fabricops_kit.io import write_lakehouse_table, write_warehouse_table
    from fabricops_kit.io.shared import execute_warehouse_processing
    from fabricops_kit.pipeline.shared import commit_pipeline_write_success, execute_lakehouse_processing

    config, env, context = resolve_fabric_context()
    coordinates = (target, schema, table_name)
    if table_id and any(value is not None for value in coordinates):
        raise ValueError("table_id cannot be combined with target, schema, or table_name.")
    if not table_id and (target is None or table_name is None):
        raise ValueError("Provide table_id or both target and table_name.")

    if table_id:
        identity = resolve_catalogue_table_identity(config, env, table_id, context=context)
        authored = (
            {"load_strategy": load_strategy, **(load_strategy_parameters or {})}
            if load_strategy is not None
            else catalogue_authored_processing(identity)
        )
    else:
        identity = resolve_physical_table_identity(config, env, target=target, schema=schema, table_name=table_name)
        identity["store_type"] = identity["store_kind"]
        authored = {"load_strategy": load_strategy, **(load_strategy_parameters or {})}

    processing = resolve_table_processing_definition(
        config, env, str(identity["table_id"]), context=context, authored_processing=authored
    )
    publication_source_ids = _source_table_ids(source_table_ids)
    scope = _write_scope()
    strategy = str(processing.get("load_strategy") or "")
    store_kind = str(identity.get("store_type") or identity.get("store_kind") or "").lower()
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

    if store_kind == "lakehouse":
        if strategy in {"append", "overwrite"}:
            write_lakehouse_table(
                prepared_df,
                str(identity["table_name"]),
                target=str(identity["target"]),
                schema=identity.get("schema"),
                mode=strategy,
                repartition_by=repartition_by,
                options=physical_options,
                context=context,
            )
        elif strategy in {"scd1", "scd2"}:
            execute_lakehouse_processing(
                prepared_df,
                table_name=str(identity["table_name"]),
                target=str(identity["target"]),
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
                target=str(identity["target"]),
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
                target=str(identity["target"]),
                processing=processing,
                context=context,
                options=physical_options,
            )
        else:
            raise ValueError(f"Unsupported governed load strategy {strategy!r}.")
    else:
        raise ValueError(f"Configured target has unsupported store kind {store_kind or '<blank>'!r}.")

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
    context["_fabricops_active_profile_registration"] = {
        "profile_role": "target",
        "table": dict(identity),
        "load_strategy": strategy,
        "load_strategy_parameters": {
            name: value
            for name, value in processing.items()
            if name
            not in {
                "load_strategy",
                "source",
                "contract_id",
                "contract_version",
                "owner_notebook_id",
                "owner_notebook_name",
                "processing_mode",
                "authored_processing",
                "governed_processing",
            }
        },
    }
    return {"table_id": str(identity["table_id"])}
