"""Public notebook-facing DataFrame profile registration callable."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Mapping, Sequence
from uuid import uuid4

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.shared import build_column_id
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import (
    configured_lakehouse_schema,
    resolve_configured_lakehouse_table,
    write_lakehouse_table_core,
)
from fabricops_kit.pipeline.shared import (
    build_frequency_distribution_dataframe,
    build_profile_dataframe,
    resolve_physical_table_identity,
)

PROFILED_TABLE = "METADATA_DATA_PROFILED"
PROFILED_FREQUENCY_TABLE = "METADATA_DATA_PROFILED_FREQUENCY"
CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
LINEAGE_TABLE = "METADATA_DATA_LINEAGE"
PROFILED_COLUMNS = metadata_table_schema_registry()[PROFILED_TABLE].fieldNames()
PROFILED_FREQUENCY_COLUMNS = metadata_table_schema_registry()[PROFILED_FREQUENCY_TABLE].fieldNames()
CATALOGUE_COLUMNS = metadata_table_schema_registry()[CATALOGUE_TABLE].fieldNames()
LOAD_STRATEGIES = {"overwrite", "append", "scd1", "scd2"}


def _require_non_empty_string(value: Any, name: str) -> str:
    """Return a stripped required string or raise a clear validation error."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string.")
    return value.strip()


def _normalize_choice(value: Any, name: str, allowed: set[str]) -> str:
    """Return a normalized allowed choice or raise a clear validation error."""
    normalized = _require_non_empty_string(value, name).lower()
    if normalized not in allowed:
        choices = ", ".join(sorted(allowed))
        raise ValueError(f"{name} must be one of: {choices}.")
    return normalized


def _processing_definition(
    profile_role: str,
    load_strategy: Any,
    load_strategy_parameters: Any,
) -> tuple[str | None, str | None]:
    """Validate and canonically serialize one table-owned processing definition."""
    supplied = load_strategy is not None or load_strategy_parameters is not None
    if profile_role == "source":
        if supplied:
            raise ValueError("Source registration does not accept target processing arguments.")
        return None, None
    if load_strategy is None:
        if load_strategy_parameters is not None:
            raise ValueError("load_strategy is required when load_strategy_parameters is supplied.")
        return None, None
    strategy = _normalize_choice(load_strategy, "load_strategy", LOAD_STRATEGIES)
    if load_strategy_parameters is None:
        parameters: dict[str, Any] = {}
    elif not isinstance(load_strategy_parameters, dict):
        raise ValueError("load_strategy_parameters must be a mapping when supplied.")
    else:
        parameters = dict(load_strategy_parameters)
    allowed = {
        "overwrite": {"partition_column"},
        "append": set(),
        "scd1": {"key_columns"},
        "scd2": {"key_columns", "effective_column", "tracked_columns"},
    }[strategy]
    unexpected = sorted(set(parameters) - allowed)
    if unexpected:
        raise ValueError(f"{strategy} does not accept processing parameters: {', '.join(unexpected)}.")
    for name in ("key_columns", "tracked_columns"):
        if name in parameters:
            values = parameters[name]
            if not isinstance(values, (list, tuple)) or not values:
                raise ValueError(f"{name} must be a non-empty sequence of column names.")
            parameters[name] = [_require_non_empty_string(value, name) for value in values]
    for name in ("partition_column", "effective_column"):
        if name in parameters:
            parameters[name] = _require_non_empty_string(parameters[name], name)
    if strategy in {"scd1", "scd2"} and "key_columns" not in parameters:
        raise ValueError(f"{strategy} requires key_columns.")
    if strategy == "scd2" and "effective_column" not in parameters:
        raise ValueError("scd2 requires effective_column.")
    return strategy, json.dumps(parameters, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _validate_processing_columns(df: Any, parameters_json: str | None) -> None:
    """Require every authored processing column name to exist in the target schema."""
    if parameters_json is None:
        return
    parameters = json.loads(parameters_json)
    available = {str(field.name) for field in df.schema.fields}
    referenced = []
    for name in ("partition_column", "effective_column"):
        if parameters.get(name):
            referenced.append(str(parameters[name]))
    for name in ("key_columns", "tracked_columns"):
        referenced.extend(str(value) for value in parameters.get(name, []))
    missing = sorted(set(referenced) - available)
    if missing:
        raise ValueError(f"Processing definition references columns not present in df: {', '.join(missing)}.")


def _schema_fingerprint(df: Any) -> str:
    """Return the legacy environment-independent ordered-schema fingerprint.

    The Stage 2 profile/catalogue model no longer persists this value, but the
    helper remains internal while the Data Contract redesign is intentionally
    deferred to Stage 5.
    """
    fields = [
        {"name": str(field.name).strip(), "type": field.dataType.simpleString()}
        for field in getattr(getattr(df, "schema", None), "fields", [])
    ]
    return hashlib.sha256(
        json.dumps({"fields": fields}, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


def _validate_resolved_identity(table: Any, *, config: Any, env: str) -> dict[str, str | None]:
    """Validate a caller-supplied identity against the active Fabric config."""
    if not isinstance(table, Mapping):
        raise ValueError("table must be a canonical table identity mapping.")
    required = {"table_id", "target", "schema", "table_name", "store_kind"}
    missing = sorted(required - set(table))
    if missing:
        raise ValueError(f"table identity is missing required fields: {', '.join(missing)}.")
    resolved = resolve_physical_table_identity(
        config,
        env,
        target=table["target"],
        schema=table["schema"],
        table_name=table["table_name"],
    )
    supplied = {name: table[name] for name in required}
    if supplied != resolved:
        raise ValueError(
            "table identity is inconsistent with the canonical identity resolved from the active Fabric config."
        )
    return resolved


def _lineage_id(*, activity_id: str, table_id: str, profile_snapshot_id: str, pipeline_role: str) -> str:
    """Return the deterministic runtime lineage identity."""
    payload = {
        "activity_id": _require_non_empty_string(activity_id, "activity_id"),
        "table_id": _require_non_empty_string(table_id, "table_id"),
        "profile_snapshot_id": _require_non_empty_string(profile_snapshot_id, "profile_snapshot_id"),
        "pipeline_role": _normalize_choice(pipeline_role, "pipeline_role", {"source", "target"}),
    }
    return hashlib.sha256(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


def _validate_frequency_profile_dataframe(source_df, frequency_profile_df, selected_columns: Sequence[str]):
    """Return the frequency DataFrame after validating caller-provided scope."""
    if frequency_profile_df is None:
        return source_df, "full_source"
    source_session = getattr(source_df, "sparkSession", None)
    frequency_session = getattr(frequency_profile_df, "sparkSession", None)
    if source_session is not None and frequency_session is not None and source_session is not frequency_session:
        raise ValueError("frequency_profile_df must use the same Spark session as df.")
    fields = getattr(getattr(frequency_profile_df, "schema", None), "fields", None)
    if fields is None:
        raise ValueError("frequency_profile_df must be a Spark DataFrame-like object with a schema.")
    available_columns = {field.name for field in fields}
    missing_columns = [column for column in selected_columns if column not in available_columns]
    if missing_columns:
        raise ValueError(f"frequency_profile_df is missing selected frequency columns: {', '.join(missing_columns)}")
    return frequency_profile_df, "caller_provided"


def _scalar_frequency_columns(df, candidate_columns: Sequence[str]) -> list[str]:
    """Return candidate columns whose Spark types are scalar frequency types."""
    from pyspark.sql.types import ArrayType, BinaryType, MapType, StructType

    fields = {field.name: field for field in df.schema.fields}
    return [
        name
        for name in candidate_columns
        if name in fields and not isinstance(fields[name].dataType, ArrayType | MapType | StructType | BinaryType)
    ]


def _automatic_frequency_columns(
    profile_df, *, scalar_columns: Sequence[str], threshold_percent: float | None
) -> list[str]:
    """Return automatic scalar columns that pass the frequency cardinality guard."""
    from pyspark.sql import functions as F

    non_null_count = F.col("NON_NULL_COUNT").cast("double")
    distinct_count = F.col("DISTINCT_COUNT").cast("double")
    raw_cardinality_percent = (distinct_count / non_null_count) * 100
    eligible = profile_df.where(F.col("COLUMN_NAME").isin(list(scalar_columns))).where(
        F.col("NON_NULL_COUNT").cast("long") > 0
    )
    if threshold_percent is not None:
        eligible = eligible.where(raw_cardinality_percent <= F.lit(float(threshold_percent)))
    return [row.COLUMN_NAME for row in eligible.select("COLUMN_NAME").collect()]


def _selected_frequency_columns(
    source_df, profile_df, frequency_columns: Sequence[str] | None, threshold_percent: float | None
) -> list[str]:
    """Return explicitly requested or automatically eligible frequency columns."""
    if frequency_columns is not None:
        return list(frequency_columns)
    profiled_columns = [row.COLUMN_NAME for row in profile_df.select("COLUMN_NAME").collect()]
    scalar_columns = _scalar_frequency_columns(source_df, profiled_columns)
    return _automatic_frequency_columns(profile_df, scalar_columns=scalar_columns, threshold_percent=threshold_percent)


def _audit_literal_columns(*, config: Any, env: str, runtime_context: dict[str, Any]) -> dict[str, Any]:
    """Return Spark literals for the canonical runtime audit field set."""
    from pyspark.sql import functions as F

    audit = build_runtime_audit_fields(config=config, env=env, runtime_context=runtime_context)
    return {
        "_committed_by": F.lit(audit["_committed_by"]).cast("string"),
        "_committed_at": F.lit(audit["_committed_at"]).cast("timestamp"),
        "_workspace_id": F.lit(audit["_workspace_id"]).cast("string"),
        "_workspace_name": F.lit(audit["_workspace_name"]).cast("string"),
        "_notebook_id": F.lit(audit["_notebook_id"]).cast("string"),
        "_notebook_name": F.lit(audit["_notebook_name"]).cast("string"),
        "_metadata_lakehouse_name": F.lit(audit["_metadata_lakehouse_name"]).cast("string"),
        "_activity_id": F.lit(audit["_activity_id"]).cast("string"),
    }


def _canonical_profiled_dataframe(
    profile_df,
    *,
    config: Any,
    env: str,
    runtime_context: dict[str, Any],
    environment_name: str,
    table_id: str,
    profile_snapshot_id: str,
):
    """Map statistical profiler output to the normalized Profile schema."""
    from pyspark.sql import functions as F
    from pyspark.sql import types as T

    column_id_udf = F.udf(lambda column_name: build_column_id(table_id, column_name), T.StringType())
    audit_columns = _audit_literal_columns(config=config, env=env, runtime_context=runtime_context)
    base = profile_df.select(
        F.col("COLUMN_NAME").alias("_column_name"),
        F.col("DATA_TYPE").alias("data_type"),
        F.col("ROW_COUNT").cast("long").alias("row_count"),
        F.col("NON_NULL_COUNT").cast("long").alias("non_null_count"),
        F.col("NULL_COUNT").cast("long").alias("null_count"),
        F.col("NULL_PERCENT").cast("double").alias("null_percent"),
        F.col("DISTINCT_COUNT").cast("long").alias("distinct_count"),
        F.col("DISTINCT_PERCENT").cast("double").alias("distinct_percent"),
        F.col("MEAN").cast("double").alias("mean_value"),
        F.col("STDDEV").cast("double").alias("stddev_value"),
        F.col("MIN_VALUE").cast("string").alias("min_value"),
        F.col("PERCENTILE_25").cast("double").alias("percentile_25_value"),
        F.col("MEDIAN").cast("double").alias("median_value"),
        F.col("PERCENTILE_75").cast("double").alias("percentile_75_value"),
        F.col("MAX_VALUE").cast("string").alias("max_value"),
    )
    return base.select(
        F.expr("uuid()").cast("string").alias("profile_id"),
        F.lit(profile_snapshot_id).cast("string").alias("profile_snapshot_id"),
        F.lit(table_id).cast("string").alias("table_id"),
        column_id_udf(F.col("_column_name")).alias("column_id"),
        F.lit(environment_name).cast("string").alias("environment_name"),
        F.col("data_type").cast("string"),
        "row_count",
        "non_null_count",
        "null_count",
        "null_percent",
        "distinct_count",
        "distinct_percent",
        "mean_value",
        "stddev_value",
        "min_value",
        "percentile_25_value",
        "median_value",
        "percentile_75_value",
        "max_value",
        *[column.alias(name) for name, column in audit_columns.items()],
    ).select(*PROFILED_COLUMNS)


def _frequency_metadata_dataframe(
    frequency_df,
    *,
    profiled_df,
    table_id: str,
    config: Any,
    env: str,
    runtime_context: dict[str, Any],
):
    """Map flattened frequency output to the same logical column profile."""
    from pyspark.sql import functions as F
    from pyspark.sql import types as T

    column_id_udf = F.udf(lambda column_name: build_column_id(table_id, column_name), T.StringType())
    identities = profiled_df.select("column_id", "data_type", "profile_id", "profile_snapshot_id")
    joined = frequency_df.withColumn("_column_id", column_id_udf(F.col("COLUMN_NAME"))).join(
        identities,
        (F.col("_column_id") == identities.column_id) & (frequency_df.DATA_TYPE == identities.data_type),
        "inner",
    )
    audit_columns = _audit_literal_columns(config=config, env=env, runtime_context=runtime_context)
    return joined.select(
        F.expr("uuid()").cast("string").alias("frequency_id"),
        identities.profile_id.cast("string").alias("profile_id"),
        identities.profile_snapshot_id.cast("string").alias("profile_snapshot_id"),
        F.col("VALUE").cast("string").alias("value"),
        F.col("FREQUENCY_COUNT").cast("long").alias("frequency_count"),
        F.col("FREQUENCY_PERCENT").cast("double").alias("frequency_percent"),
        F.col("FREQUENCY_RANK").cast("integer").alias("frequency_rank"),
        F.col("PROFILED_ROW_COUNT").cast("long").alias("profiled_row_count"),
        F.col("PROFILED_NON_NULL_COUNT").cast("long").alias("profiled_non_null_count"),
        *[column.alias(name) for name, column in audit_columns.items()],
    ).select(*PROFILED_FREQUENCY_COLUMNS)


def _replace_frequency_rows(
    *, frequency_df: Any | None, profiled_df: Any, config: Any, env: str, spark_session: Any
) -> None:
    """Replace flattened Frequency rows only for the current profiling snapshot."""
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - depends on Fabric/Delta runtime
        raise RuntimeError(
            "Delta Lake support is required for replacement METADATA_DATA_PROFILED_FREQUENCY writes."
        ) from exc
    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        "metadata",
        PROFILED_FREQUENCY_TABLE,
        configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
    )
    snapshots = profiled_df.select("profile_snapshot_id").dropDuplicates()
    (
        DeltaTable.forPath(spark_session, path)
        .alias("target")
        .merge(snapshots.alias("source"), "target.profile_snapshot_id = source.profile_snapshot_id")
        .whenMatchedDelete()
        .execute()
    )
    if frequency_df is not None:
        write_lakehouse_table_core(
            frequency_df,
            PROFILED_FREQUENCY_TABLE,
            target="metadata",
            schema=configured_lakehouse_schema(config, env, "metadata"),
            context={"config": config, "env": env},
            mode="append",
        )


def _catalogue_dataframe_from_profiled(
    profiled_df,
    *,
    source_df: Any,
    store_type: str,
    layer: str,
    schema_name: str | None,
    table_name: str,
    load_strategy: str | None = None,
    load_strategy_parameters_json: str | None = None,
):
    """Return one table row and one row for each observed column asset."""
    from pyspark.sql import functions as F

    first = profiled_df.select(
        "table_id",
        "environment_name",
        "_committed_by",
        "_committed_at",
        "_workspace_id",
        "_workspace_name",
        "_notebook_id",
        "_notebook_name",
        "_metadata_lakehouse_name",
        "_activity_id",
    ).first()
    if first is None:
        return profiled_df.sparkSession.createDataFrame([], schema=metadata_table_schema_registry()[CATALOGUE_TABLE])
    audit = {name: first[name] for name in CATALOGUE_COLUMNS if name.startswith("_")}
    common = {
        "table_id": first["table_id"],
        "environment_name": first["environment_name"],
        "store_type": store_type,
        "layer": layer,
        "schema_name": schema_name,
        "table_name": table_name,
        "first_profiled_at": first["_committed_at"],
        "last_profiled_at": first["_committed_at"],
        "is_active": True,
        **audit,
    }
    rows = [
        coerce_metadata_row_types(
            CATALOGUE_TABLE,
            {
                **common,
                "metadata_level": "table",
                "column_id": None,
                "column_name": None,
                "data_type": None,
                "load_strategy": load_strategy,
                "load_strategy_parameters_json": load_strategy_parameters_json,
            },
        )
    ]
    for field in source_df.schema.fields:
        column_id = build_column_id(first["table_id"], field.name)
        rows.append(
            coerce_metadata_row_types(
                CATALOGUE_TABLE,
                {
                    **common,
                    "metadata_level": "column",
                    "column_id": column_id,
                    "column_name": field.name,
                    "data_type": field.dataType.simpleString(),
                    "load_strategy": None,
                    "load_strategy_parameters_json": None,
                },
            )
        )
    return profiled_df.sparkSession.createDataFrame(rows, schema=metadata_table_schema_registry()[CATALOGUE_TABLE])


def _upsert_catalogue_identities(*, catalogue_df: Any, config: Any, env: str, spark_session: Any) -> None:
    """Upsert Catalogue rows by environment-aware asset grain and deactivate missing columns."""
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - depends on Fabric/Delta runtime
        raise RuntimeError(
            "Delta Lake merge support is required for idempotent METADATA_DATA_CATALOGUE writes."
        ) from exc
    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        "metadata",
        CATALOGUE_TABLE,
        configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
    )
    first = catalogue_df.select("environment_name", "table_id").first()
    if first is None:
        return
    environment_name = str(first["environment_name"]).replace("'", "''")
    table_id = str(first["table_id"]).replace("'", "''")
    target = DeltaTable.forPath(spark_session, path)
    (
        target.alias("target")
        .merge(
            catalogue_df.alias("source"),
            "target.environment_name = source.environment_name "
            "AND target.metadata_level = source.metadata_level "
            "AND target.table_id = source.table_id "
            "AND coalesce(target.column_id, '') = coalesce(source.column_id, '')",
        )
        .whenMatchedUpdate(
            set={
                "store_type": "source.store_type",
                "layer": "source.layer",
                "schema_name": "source.schema_name",
                "table_name": "source.table_name",
                "column_name": "source.column_name",
                "data_type": "source.data_type",
                "load_strategy": "coalesce(source.load_strategy, target.load_strategy)",
                "load_strategy_parameters_json": (
                    "coalesce(source.load_strategy_parameters_json, target.load_strategy_parameters_json)"
                ),
                "last_profiled_at": "source.last_profiled_at",
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
        .whenNotMatchedBySourceUpdate(
            condition=(
                f"target.environment_name = '{environment_name}' AND target.table_id = '{table_id}' "
                "AND target.metadata_level = 'column' AND target.is_active = true"
            ),
            set={"is_active": "false"},
        )
        .execute()
    )


def _write_lineage_participation(
    *,
    table_id: str,
    profile_snapshot_id: str,
    pipeline_role: str,
    config: Any,
    env: str,
    context: dict[str, Any],
    spark_session: Any,
) -> None:
    """Write one idempotent source/target lineage participation record."""
    normalized_table_id = _require_non_empty_string(table_id, "table_id")
    normalized_snapshot = _require_non_empty_string(profile_snapshot_id, "profile_snapshot_id")
    normalized_role = _normalize_choice(pipeline_role, "pipeline_role", {"source", "target"})
    audit = build_runtime_audit_fields(config=config, env=env, runtime_context=context)
    row = coerce_metadata_row_types(
        LINEAGE_TABLE,
        {
            "lineage_id": _lineage_id(
                activity_id=audit["_activity_id"],
                table_id=normalized_table_id,
                profile_snapshot_id=normalized_snapshot,
                pipeline_role=normalized_role,
            ),
            "table_id": normalized_table_id,
            "profile_snapshot_id": normalized_snapshot,
            "environment_name": env,
            "pipeline_role": normalized_role,
            **audit,
        },
    )
    lineage_df = spark_session.createDataFrame([row], schema=metadata_table_schema_registry()[LINEAGE_TABLE])
    _upsert_lineage_event(lineage_df=lineage_df, config=config, env=env, spark_session=spark_session)


def _upsert_lineage_event(*, lineage_df: Any, config: Any, env: str, spark_session: Any) -> None:
    """Upsert Lineage rows by environment and lineage_id."""
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - depends on Fabric/Delta runtime
        raise RuntimeError("Delta Lake merge support is required for idempotent METADATA_DATA_LINEAGE writes.") from exc
    _store, _table_value, _schema_value, path = resolve_configured_lakehouse_table(
        "metadata",
        LINEAGE_TABLE,
        configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
    )
    (
        DeltaTable.forPath(spark_session, path)
        .alias("target")
        .merge(
            lineage_df.alias("source"),
            "target.environment_name = source.environment_name AND target.lineage_id = source.lineage_id",
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )


def profile_and_register_table(
    df,
    *,
    profile_role,
    table=None,
    target=None,
    table_name=None,
    schema=None,
    load_strategy=None,
    load_strategy_parameters=None,
    frequency_columns=None,
    frequency_top_n: int | None = None,
    frequency_max_distinct_percent: float | None = 80.0,
    frequency_profile_df=None,
):
    """Profile a supplied Spark DataFrame and save its metadata records.
    
    The notebook supplies a Spark DataFrame and the table identity that the
    DataFrame represents. FabricOps calculates one profiling result row for
    each eligible column, saves a new profiling snapshot, creates stable table
    and column IDs, updates or adds catalogue records, records whether the
    table was used as an input or produced as an output, and returns the
    profiling result to the notebook.
    
    The original business DataFrame is not written, sampled, re-read, or
    changed by this function. All metadata writes go to the metadata lakehouse
    configured in ``00_env_config`` for the active environment.
    
    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to profile exactly as supplied by the caller. The
        helper does not sample, re-read, or mutate this DataFrame.
    profile_role : {"source", "target"}
        Records whether the profiled asset participated in the notebook
        activity as an input or an output: ``source`` for an activity input and
        ``target`` for an activity output. The value is recorded as ``pipeline_role`` in
        ``METADATA_DATA_LINEAGE`` rather than in ``METADATA_DATA_PROFILED`` or
        ``METADATA_DATA_CATALOGUE``.
    table : mapping, optional
        Canonical resolved table identity returned as ``read_pipeline_prep()``
        ``source`` or ``target``. Supply this instead of ``target``, ``schema``,
        and ``table_name`` to reuse the already resolved identity.
    target : str, optional
        Configured FabricStore target key. Its normalized key becomes the
        physical identity's layer and its store kind determines whether the
        asset is a Lakehouse or Warehouse table. Required when ``table`` is
        not supplied.
    table_name : str, optional
        Physical table name of the business asset being profiled. This
        identifies the asset and does not redirect metadata writes. Required
        when ``table`` is not supplied.
    schema : str, optional
        Physical schema name, or ``None`` to use the configured store default.
        Classic or schema-disabled Lakehouses preserve ``None``.
    load_strategy : {"overwrite", "append", "scd1", "scd2"}, optional
        Current target load strategy. Valid only when ``profile_role="target"``.
    load_strategy_parameters : dict, optional
        Strategy parameters. ``scd1`` requires ``key_columns``; ``scd2``
        requires ``key_columns`` and ``effective_column`` and optionally accepts
        ``tracked_columns``; ``overwrite`` optionally accepts
        ``partition_column``; ``append`` accepts no parameters.
    frequency_columns : sequence of str, optional
        Selected columns whose flattened frequency rows should be persisted.
        ``None`` profiles eligible non-technical scalar columns. An empty
        sequence skips frequency profiling entirely and writes no child rows.
        Requested columns should also be eligible for the main statistical
        profile.
    frequency_top_n : int or None, optional
        Optional number of ranked values to retain per selected frequency
        column. ``None`` retains every distinct value.
    frequency_max_distinct_percent : float or None, default=80.0
        Automatic frequency-profiling safeguard used only when
        ``frequency_columns=None``. Columns whose distinct-per-non-null
        percentage is greater than this threshold are skipped and produce no
        child frequency rows. Values must be between ``0.0`` and ``100.0``
        when supplied. ``None`` disables the high-cardinality threshold;
        all-null automatic columns remain skipped. Explicit
        ``frequency_columns`` selections override this threshold.
    frequency_profile_df : pyspark.sql.DataFrame, optional
        Optional caller-provided Spark DataFrame to use only for frequency
        distribution calculation. ``None`` preserves full-source frequency
        profiling. When supplied, it must contain every selected frequency
        column, may contain extra columns, and must use a compatible Spark
        session when this can be determined. The caller is responsible for
        preparing, persisting, refreshing, and governing this DataFrame; this
        function does not verify whether it is random, representative, sampled,
        persisted, or otherwise suitable for the caller's purpose.
    
    Returns
    -------
    pyspark.sql.DataFrame
        A Spark DataFrame containing one canonical profiling record for each
        eligible column in the supplied DataFrame. This is the same DataFrame
        appended to ``METADATA_DATA_PROFILED`` and includes stable table and column identity, profiling snapshot identity,
        compact statistical metrics, environment identity, and runtime audit fields. Flattened child frequency rows, generated catalogue rows,
        and the lineage event are not returned.
    
    Raises
    ------
    ValueError
        If the role, target, configured store, schema, or table identity is invalid.
    RuntimeError
        If Delta replacement support is unavailable, or lineage registration
        fails after profile and catalogue registration succeed.
    
    Notes
    -----
    Processing flow:
    
    1. Build a statistical profile against the complete supplied DataFrame to
       produce one statistical profile row per eligible input column.
    2. Use that statistical profile to choose automatic frequency columns
       when ``frequency_columns=None``: eligible scalar columns at or below
       ``frequency_max_distinct_percent`` are profiled, high-cardinality
       columns and all-null columns produce no child frequency rows. Explicit non-empty
       ``frequency_columns`` bypass this threshold, while
       ``frequency_columns=[]`` skips frequency profiling entirely.
    3. Produce flattened frequency rows for the selected columns using the
       same calculation exposed by ``profile_frequency_distribution``.
    4. Resolve each frequency row to its parent ``profile_id`` and shared
       ``profile_snapshot_id``.
    5. Save the compact profiling snapshot to ``METADATA_DATA_PROFILED``.
    6. Replace rows for the exact ``profile_snapshot_id`` child snapshot and
    write the normalized rows to
       ``METADATA_DATA_PROFILED_FREQUENCY``.
    7. Create stable table and column IDs, then update matching catalogue
       records or add new records in ``METADATA_DATA_CATALOGUE``.
    8. Record whether the table was used as an input or produced as an output
       in ``METADATA_DATA_LINEAGE``.
    9. Return only the compact parent Spark DataFrame written to
       ``METADATA_DATA_PROFILED``.
    
    User-facing workflow:
    
    Supplied DataFrame
        ↓
    Calculate column statistics and value frequencies
        ↓
    Save compact summary and flattened frequency snapshots
    ``METADATA_DATA_PROFILED`` + ``METADATA_DATA_PROFILED_FREQUENCY``
        ↓
    Create stable table and column IDs
        ↓
    Update existing catalogue records or add new ones
    ``METADATA_DATA_CATALOGUE``
        ↓
    Record whether the table was used as an input or output
        ↓
    ``METADATA_DATA_LINEAGE``
        ↓
    Return the profiling result to the notebook
    
    Frequency snapshot behavior:
    
    * Every eligible statistical profile row remains in the compact parent
      result whether or not that column produces child frequency rows.
    * ``frequency_columns=None`` automatically profiles eligible non-technical
      scalar columns whose distinct-per-non-null percentage is less than or
      equal to ``frequency_max_distinct_percent``. The default threshold is
      ``80.0`` percent.
    * Automatically selected columns above the threshold and all-null automatic
      columns produce no child frequency rows. No fake skipped values are stored.
    * ``frequency_max_distinct_percent=None`` disables the high-cardinality
      threshold for automatic columns.
    * Only columns listed in a non-empty ``frequency_columns`` sequence receive
      generated frequency evidence; explicit selections override the automatic
      threshold. Other profiled columns produce no child rows.
    * ``frequency_columns=[]`` skips frequency profiling entirely and writes no
      child rows for the current snapshot.
    * ``frequency_profile_df=None`` profiles frequencies against the complete
      supplied source DataFrame. When a caller supplies ``frequency_profile_df``,
      frequency counts, percentages, ranks, profiled row counts, and profiled
      non-null counts describe that caller-provided DataFrame. The compact
      parent statistics still describe the complete source DataFrame.
    * ``frequency_top_n`` restricts persisted child rows only when supplied. It
      limits output rows after grouped counts are calculated and does not
      reduce grouping cost.
    * Frequency values are ordered deterministically by rank.
    * Historical parent and child rows join through ``profile_id``. Replacement
      is scoped to the current ``profile_snapshot_id``, so earlier snapshots remain intact.
    
    ``METADATA_DATA_PROFILED`` receives one appended row per eligible input
    DataFrame column. Repeated executions create additional profiling
    snapshots, and the returned DataFrame is the same compact DataFrame
    appended to this table. Its logical field groups are:
    
    * Identity fields: ``profile_id``, ``profile_snapshot_id``, ``table_id``,
      ``column_id``, ``environment_name``, ``data_type``.
    * Statistical fields: ``row_count``, ``non_null_count``, ``null_count``,
      ``null_percent``, ``distinct_count``, ``distinct_percent``,
      ``mean_value``, ``stddev_value``, ``min_value``,
      ``percentile_25_value``, ``median_value``, ``percentile_75_value``,
      ``max_value``.
    * Audit fields: ``_committed_by``, ``_committed_at``, ``_workspace_id``,
      ``_workspace_name``, ``_notebook_id``, ``_notebook_name``,
      ``_metadata_lakehouse_name``, ``_activity_id``.
    
    ``METADATA_DATA_PROFILED`` saves a new compact profiling snapshot. One row
    is saved for each eligible DataFrame column. ``METADATA_DATA_PROFILED_FREQUENCY``
    saves one flattened row per returned distinct value. Earlier parent and child snapshots are retained. Frequency rows link to
    their parent through ``profile_id`` and share the same ``profile_snapshot_id``.
    
    ``METADATA_DATA_CATALOGUE`` stores table and column records, not profiling
    measurements. FabricOps creates a stable ID for the table and each column,
    then checks whether the same logical asset already exists in the active
    environment. If a matching record exists, it is updated. Otherwise, a new
    record is added. Matching uses ``environment_name + metadata_level + table_id
    + column_id``. ``table_id`` and ``column_id`` are stable logical identities
    shared across environments, while ``environment_name`` keeps Development and
    Production observations separate. Column rows store the current source schema
    ``data_type``. A type change updates that value without changing the column
    identity or deactivating the column. Column catalogue rows that disappear from a
    new profile are retained but marked inactive rather than silently deleted.
    
    ``METADATA_DATA_LINEAGE`` records whether the table was used as an input
    or produced as an output during the current notebook activity. A
    ``profile_role="source"`` value means the DataFrame was used as an input.
    A ``profile_role="target"`` value means the DataFrame was produced as an
    output. Lineage-specific fields are ``lineage_id``, ``table_id``,
    ``profile_snapshot_id``, ``environment_name``, and ``pipeline_role``. The
    standard eight underscore audit fields are the execution-context contract,
    and ``_committed_at`` is the authoritative timestamp for the lineage event.
    ``lineage_id`` is deterministically derived from ``_activity_id``,
    ``table_id``, ``profile_snapshot_id``, and ``pipeline_role``.
    
    What the notebook receives: a Spark DataFrame containing one profiling
    result row for each eligible column.
    
    What FabricOps saves:
    
    * ``METADATA_DATA_PROFILED``: a new compact profiling snapshot.
    * ``METADATA_DATA_PROFILED_FREQUENCY``: flattened frequency rows linked by
      ``profile_id`` and grouped by ``profile_snapshot_id``.
    * ``METADATA_DATA_CATALOGUE``: updated or newly added table and column
      records.
    * ``METADATA_DATA_LINEAGE``: the current source or target activity.
    
    Statistical profiling records describe the complete DataFrame supplied
    during the notebook activity. If ``frequency_profile_df`` is supplied,
    only generated frequency evidence uses that DataFrame. The function does not claim or
    verify that the caller-provided DataFrame is sampled, random,
    representative, persisted, or governed; those responsibilities stay with
    the upstream ingestion or notebook workflow.
    
    The physical identity is the caller-selected configured table identity;
    an arbitrary DataFrame does not prove that table exists. Profile a source
    after a successful complete-table read, and profile a target only after
    its write has succeeded and the persisted target has been confirmed.
    
    Profile and catalogue registration occur before lineage registration. If
    lineage registration fails after those writes succeed, the function raises
    a ``RuntimeError`` explaining that profile and catalogue registration
    succeeded but lineage registration failed. Guardrail execution is a
    separate workflow.
    
    This Stage 2 redesign changes the physical schemas for Catalogue, Profile,
    Profile Frequency, Lineage, and Source Observation. Existing development
    metadata tables may need recreation through the established setup flow; no
    compatibility or automatic migration layer is provided.

    """
    normalized_profile_role = _normalize_choice(profile_role, "profile_role", {"source", "target"})
    config, env, context = resolve_fabric_context()
    if table is not None:
        if target is not None or schema is not None or table_name is not None:
            raise ValueError("table cannot be combined with target, schema, or table_name.")
        identity = _validate_resolved_identity(table, config=config, env=env)
    else:
        identity = resolve_physical_table_identity(
            config, env, target=target, schema=schema, table_name=table_name
        )
    normalized_target = identity["target"]
    normalized_table = identity["table_name"]
    normalized_schema = identity["schema"]
    normalized_store_type = identity["store_kind"]
    normalized_load_strategy, write_parameters_json = _processing_definition(
        normalized_profile_role, load_strategy, load_strategy_parameters
    )
    _validate_processing_columns(df, write_parameters_json)
    selected_frequency_columns = None if frequency_columns is None else list(frequency_columns)
    if frequency_max_distinct_percent is not None and (
        not math.isfinite(frequency_max_distinct_percent)
        or not 0.0 <= frequency_max_distinct_percent <= 100.0
    ):
        raise ValueError("frequency_max_distinct_percent must be finite and between 0.0 and 100.0 when supplied.")

    profile_df = build_profile_dataframe(df)
    table_id = identity["table_id"]
    profile_snapshot_id = str(uuid4())
    profiled_df = _canonical_profiled_dataframe(
        profile_df,
        config=config,
        env=env,
        runtime_context=context,
        environment_name=env,
        table_id=table_id,
        profile_snapshot_id=profile_snapshot_id,
    )
    # Spark uuid() is non-deterministic across re-evaluation. Materialize the
    # parent once so Frequency receives the exact persisted profile_id values.
    profiled_df = profiled_df.cache()
    profiled_df.count()

    selected_columns = _selected_frequency_columns(
        df, profile_df, selected_frequency_columns, frequency_max_distinct_percent
    )
    frequency_metadata_df = None
    if selected_columns:
        frequency_source_df, _frequency_scope = _validate_frequency_profile_dataframe(
            df, frequency_profile_df, selected_columns
        )
        frequency_df = build_frequency_distribution_dataframe(
            frequency_source_df, columns=selected_columns, top_n=frequency_top_n
        )
        frequency_metadata_df = _frequency_metadata_dataframe(
            frequency_df,
            profiled_df=profiled_df,
            table_id=table_id,
            config=config,
            env=env,
            runtime_context=context,
        )

    write_lakehouse_table_core(
        profiled_df,
        PROFILED_TABLE,
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
        mode="append",
    )
    _replace_frequency_rows(
        frequency_df=frequency_metadata_df,
        profiled_df=profiled_df,
        config=config,
        env=env,
        spark_session=df.sparkSession,
    )
    catalogue_df = _catalogue_dataframe_from_profiled(
        profiled_df,
        source_df=df,
        store_type=normalized_store_type,
        layer=normalized_target,
        schema_name=normalized_schema,
        table_name=normalized_table,
        load_strategy=normalized_load_strategy,
        load_strategy_parameters_json=write_parameters_json,
    )
    _upsert_catalogue_identities(
        catalogue_df=catalogue_df,
        config=config,
        env=env,
        spark_session=df.sparkSession,
    )
    try:
        _write_lineage_participation(
            table_id=table_id,
            profile_snapshot_id=profile_snapshot_id,
            pipeline_role=normalized_profile_role,
            config=config,
            env=env,
            context=context,
            spark_session=df.sparkSession,
        )
    except Exception as exc:
        raise RuntimeError(
            "Profile and catalogue registration succeeded but lineage registration failed "
            f"for table_id={table_id!r} and pipeline_role={normalized_profile_role!r}."
        ) from exc
    return profiled_df
