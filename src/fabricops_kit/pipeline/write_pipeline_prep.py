"""Public owner for governed target-write preparation."""

from __future__ import annotations

from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.pipeline.shared import (
    add_target_audit_fields,
    catalogue_authored_processing,
    persist_lineage_participation,
    resolve_catalogue_table_identity,
    resolve_table_processing_definition,
    resolve_target_audit_fields,
)
from fabricops_kit.security.shared import resolve_direct_pii_columns, tokenise_direct_pii


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


def _validate_watermark_progress(df, upper_bound: Any) -> None:
    """Require transformed output to retain the captured source upper watermark."""
    from pyspark.sql import functions as F

    state = df.agg(
        F.count(F.lit(1)).alias("row_count"),
        F.max(F.col("_watermark_value")).alias("maximum_watermark"),
    ).collect()[0]
    if not int(state["row_count"] or 0):
        raise ValueError(
            "incremental_watermark transformed output is empty; target-backed watermark persistence "
            "requires at least one published row carrying the captured upper watermark."
        )
    maximum = state["maximum_watermark"]
    try:
        matches_upper = maximum == upper_bound
    except TypeError as exc:
        raise ValueError(
            "The transformed target watermark cannot be compared with the captured source upper watermark."
        ) from exc
    if not matches_upper:
        raise ValueError(
            f"incremental_watermark transformed output reaches {maximum!r}, but the captured upper watermark "
            f"is {upper_bound!r}; target-backed watermark persistence requires a published row carrying "
            "the captured upper watermark."
        )


def _overwrite_options(
    source_preps: list[dict[str, Any]],
    processing: dict[str, Any],
    store_kind: str,
) -> dict[str, Any]:
    """Return safe overwrite options or reject an unrestricted incremental overwrite."""
    error = (
        "Incremental source processing cannot use unrestricted overwrite because it would replace rows "
        "outside the processed source scope."
    )
    if len(source_preps) != 1:
        raise ValueError(error)
    prep = source_preps[0]
    source_strategy = str((prep.get("source_processing") or {}).get("read_strategy") or "")
    read_mode = prep.get("read_mode")
    scope = prep.get("scope")
    if not isinstance(scope, dict):
        raise ValueError(error)
    if source_strategy == "full_dataset":
        if read_mode == "full_dataset" and scope == {"type": "full_dataset"}:
            return {}
        raise ValueError(error)
    if source_strategy == "incremental_watermark":
        watermark_column = str((prep.get("source_processing") or {}).get("watermark_column") or "")
        first_population = (
            read_mode == "full_dataset"
            and scope.get("type") == "full_dataset"
            and scope.get("watermark_column") == watermark_column
            and scope.get("upper_bound") is not None
            and scope.get("lower_bound") is None
        )
        if first_population:
            return {}
        if store_kind != "lakehouse":
            raise ValueError(error)
        required = (
            read_mode == "incremental_subset"
            and scope.get("type") == "watermark"
            and scope.get("lower_bound") is not None
            and scope.get("upper_bound") is not None
            and scope.get("lower_inclusive") is False
            and scope.get("upper_inclusive") is True
        )
        if not required:
            raise ValueError(error)
        lower = _delta_literal(scope["lower_bound"])
        upper = _delta_literal(scope["upper_bound"])
        return {"replaceWhere": f"`_watermark_value` > {lower} AND `_watermark_value` <= {upper}"}
    if source_strategy == "incremental_partition":
        partition_column = str((prep.get("source_processing") or {}).get("partition_column") or "")
        first_population = (
            read_mode == "full_dataset"
            and scope.get("type") == "full_dataset"
            and scope.get("partition_column") == partition_column
            and scope.get("target_state_empty") is True
        )
        if first_population:
            return {}
        if store_kind != "lakehouse":
            raise ValueError(error)
        values = scope.get("values")
        if (
            read_mode != "incremental_subset"
            or scope.get("type") != "partition"
            or not isinstance(values, list | tuple)
            or not values
            or partition_column != scope.get("column")
        ):
            raise ValueError(error)
        return {"replaceWhere": _replace_where("_partition_bucket", list(values))}
    raise ValueError(error)


def _source_scope(source_preps: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate source preparation and return one truthful target scope."""
    if not source_preps:
        raise ValueError("source_preps must contain at least one read_pipeline_prep result.")
    scopes = []
    for prep in source_preps:
        if not isinstance(prep, dict):
            raise ValueError("source_preps must contain read_pipeline_prep result dictionaries.")
        read_mode = prep.get("read_mode")
        scope = prep.get("scope")
        if read_mode not in {"full_dataset", "incremental_subset"} or not isinstance(scope, dict):
            raise ValueError("Each source prep must contain a non-skipped canonical read_mode and scope.")
        scopes.append({"read_mode": read_mode, "scope": scope})
    if all(scope == scopes[0] for scope in scopes[1:]):
        return scopes[0]
    return {
        "read_mode": "incremental_subset",
        "scope": {"type": "multiple_sources"},
    }


def write_pipeline_prep(
    df,
    *,
    target_table_id: str,
    source_preps: list[dict[str, Any]],
) -> dict[str, Any]:
    """Prepare governed target write inputs without physically writing the target.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Business target DataFrame after target schema and DQ checks pass.
    target_table_id : str
        Canonical registered target identity used to resolve physical target
        metadata and target-owned processing.
    source_preps : list of dict
        Results returned by :func:`read_pipeline_prep` for the sources that fed
        this target. Watermark source values must remain present through
        transformation so target state can be persisted on each row.

    Returns
    -------
    dict
        Tokenised and audited target DataFrame, physical writer mode/options,
        the unchanged resolved processing definition, its prepared scope, and
        target Lineage preparation.

    Raises
    ------
    ValueError
        If preparation is incomplete or an unsafe target/strategy combination
        is requested, or if transformed incremental-watermark output cannot
        persist the captured upper watermark on a target row.

    Notes
    -----
    FabricOps resolves one run-level audit record and adds only compact target
    provenance fields. Direct PII columns are replaced with opaque tokens before
    audit fields are added, and unique reversible mappings are persisted to the
    separately configured, table-isolated ``pii_token_vault`` target. This
    function does not call a Lakehouse or Warehouse writer or commit source
    progress. It persists target Lineage at the governed
    preparation boundary. Lakehouse and Warehouse
    targets use the same governed strategy definition; each writer applies its
    engine-specific physical execution only after this preparation succeeds.
    Overwrite is full-table for an explicitly configured ``full_dataset`` source
    and for the first ``incremental_watermark`` population whose scope retains
    its captured upper bound. Later Lakehouse incremental watermark and
    partition reads require a matching canonical scope and use ``replaceWhere``;
    later Warehouse incremental overwrite is rejected because no equivalent
    scoped replacement is implemented. For incremental-watermark processing,
    including its first ``full_dataset`` population, this function evaluates
    the transformed DataFrame before publication and requires its maximum
    ``_watermark_value`` to equal the captured source upper bound. Empty or
    truncated output fails rather than leaving target-backed progress
    permanently behind the processed window.

    Examples
    --------
    >>> write_prep = write_pipeline_prep(
    ...     transformed_df,
    ...     target_table_id="lakehouse:unified:dbo:students",
    ...     source_preps=[read_prep],
    ... )
    >>> write_prep["mode"]
    'append'

    See Also
    --------
    read_pipeline_prep, write_lakehouse_table, write_warehouse_table

    """
    config, env, context = resolve_fabric_context()
    target_identity = resolve_catalogue_table_identity(config, env, target_table_id, context=context)
    processing = resolve_table_processing_definition(
        config,
        env,
        target_identity["table_id"],
        context=context,
        authored_processing=catalogue_authored_processing(target_identity),
    )
    prepared_scope = _source_scope(source_preps)
    scope = prepared_scope["scope"]
    store_kind = target_identity["store_type"]
    strategy = str(processing.get("load_strategy") or "")
    options = _overwrite_options(source_preps, processing, store_kind) if strategy == "overwrite" else {}
    watermark_preps = [
        prep for prep in source_preps
        if (prep.get("source_processing") or {}).get("read_strategy") == "incremental_watermark"
    ]
    partition_preps = [
        prep for prep in source_preps
        if (prep.get("source_processing") or {}).get("read_strategy") == "incremental_partition"
    ]
    if partition_preps and strategy == "append":
        raise ValueError(
            "incremental_partition with append is unsafe because replay can duplicate rows; "
            "use overwrite, scd1, or scd2."
        )
    if len(partition_preps) > 1:
        raise ValueError("A governed target can derive _partition_bucket from only one incremental_partition source.")
    if watermark_preps and strategy == "append":
        raise ValueError(
            "incremental_watermark with append is unsafe because the processing definition has no "
            "deterministic row identity for replay; use overwrite, scd1, or scd2."
        )
    if len(watermark_preps) > 1:
        raise ValueError("A governed target can derive _watermark_value from only one incremental_watermark source.")
    if watermark_preps:
        watermark_column = str(watermark_preps[0]["source_processing"]["watermark_column"])
        if watermark_column == "_watermark_value":
            raise ValueError("_watermark_value is reserved for FabricOps target watermark state.")
        if "_watermark_value" in df.columns:
            raise ValueError("_watermark_value is a reserved FabricOps technical column and must not be supplied.")
        if watermark_column not in df.columns:
            raise ValueError(
                f"incremental_watermark requires source watermark column {watermark_column!r} to be retained "
                "through transformation until write_pipeline_prep."
            )
        from pyspark.sql import functions as F

        df = df.withColumn("_watermark_value", F.col(watermark_column))
        if scope.get("upper_bound") is not None:
            _validate_watermark_progress(df, scope["upper_bound"])
    if partition_preps:
        partition_column = str(partition_preps[0]["source_processing"]["partition_column"])
        if partition_column == "_partition_bucket":
            raise ValueError("_partition_bucket is reserved for FabricOps target partition state.")
        if "_partition_bucket" in df.columns:
            raise ValueError("_partition_bucket is a reserved FabricOps technical column and must not be supplied.")
        if partition_column not in df.columns:
            raise ValueError(
                f"incremental_partition requires source partition column {partition_column!r} to be retained "
                "through transformation until write_pipeline_prep."
            )
        from pyspark.sql import functions as F

        df = df.withColumn("_partition_bucket", F.col(partition_column))
        if df.where(F.col("_partition_bucket").isNull()).limit(1).count():
            raise ValueError("incremental_partition requires non-null _partition_bucket values on every target row.")
    direct_pii_columns = resolve_direct_pii_columns(
        config,
        env,
        target_identity["table_id"],
        spark_session=getattr(df, "sparkSession", None),
        context=context,
    )
    df = tokenise_direct_pii(
        df,
        config=config,
        env=env,
        table_id=target_identity["table_id"],
        columns=direct_pii_columns,
        spark_session=getattr(df, "sparkSession", None),
        context=context,
    )
    audit = resolve_target_audit_fields(context)
    prepared_df = add_target_audit_fields(df, audit)
    persist_lineage_participation(
        table_id=target_identity["table_id"],
        pipeline_role="target",
        activity_id=audit["_activity_id"],
        context=context,
    )
    if strategy == "scd2":
        from pyspark.sql import functions as F

        effective = str(processing["effective_column"])
        effective_type = prepared_df.schema[effective].dataType
        prepared_df = (
            prepared_df.withColumn("_effective_from", F.col(effective))
            .withColumn("_effective_to", F.lit(None).cast(effective_type))
            .withColumn("_is_current", F.lit(True))
        )

    mode = strategy if strategy in {"overwrite", "append"} else None
    return {
        "df": prepared_df,
        "mode": mode,
        "options": options,
        "load_strategy": strategy,
        "load_strategy_parameters": {
            name: value
            for name, value in processing.items()
            if name not in {"load_strategy", "source", "contract_id", "contract_version"}
        },
        "processing": processing,
        "scope": prepared_scope,
        "target": target_identity,
        "target_kind": store_kind,
        "lineage": {
            "table_id": target_identity["table_id"],
            "pipeline_role": "target",
            "activity_id": audit["_activity_id"],
            "environment_name": env,
        },
    }
