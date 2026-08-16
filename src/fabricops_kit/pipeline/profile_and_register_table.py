"""Public notebook-facing DataFrame profile registration callable."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Sequence
from uuid import uuid4

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_identity import build_column_id, build_table_id
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.config.shared import get_store, resolve_fabric_context
from fabricops_kit.io.shared import (
    configured_lakehouse_schema,
    resolve_configured_lakehouse_table,
    resolve_lakehouse_table_location,
    resolve_warehouse_table_location,
    write_lakehouse_table_core,
)
from fabricops_kit.pipeline.shared import build_frequency_distribution_dataframe, build_profile_dataframe

PROFILED_TABLE = "METADATA_DATA_PROFILED"
PROFILED_FREQUENCY_TABLE = "METADATA_DATA_PROFILED_FREQUENCY"
CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
LINEAGE_TABLE = "METADATA_DATA_LINEAGE"
PROFILED_COLUMNS = metadata_table_schema_registry()[PROFILED_TABLE].fieldNames()
PROFILED_FREQUENCY_COLUMNS = metadata_table_schema_registry()[PROFILED_FREQUENCY_TABLE].fieldNames()
CATALOGUE_COLUMNS = metadata_table_schema_registry()[CATALOGUE_TABLE].fieldNames()


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


def _resolve_physical_identity(*, profile_role: Any, target: Any, schema: Any, table_name: Any):
    """Resolve and validate one configured physical table identity."""
    normalized_role = _normalize_choice(profile_role, "profile_role", {"source", "target"})
    normalized_target = _require_non_empty_string(target, "target").lower()
    normalized_table = _require_non_empty_string(table_name, "table_name")
    config, env, context = resolve_fabric_context()
    store = get_store(config, env, normalized_target)
    store_kind = str(getattr(store, "kind", "")).strip().lower()

    if store_kind == "lakehouse":
        if schema == "":
            raise ValueError("schema must be a non-empty identifier when supplied.")
        if getattr(store, "schema_enabled", False) and schema is None and not getattr(store, "schema", None):
            raise ValueError(
                f"schema is required for schema-enabled Lakehouse target '{normalized_target}'; "
                "pass schema or configure a default schema."
            )
        normalized_table, normalized_schema, _path = resolve_lakehouse_table_location(store, normalized_table, schema)
        if getattr(store, "schema_enabled", False) and normalized_schema is None:
            raise ValueError(
                f"schema is required for schema-enabled Lakehouse target '{normalized_target}'; "
                "pass schema or configure a default schema."
            )
    elif store_kind == "warehouse":
        configured_schema = schema if schema is not None else getattr(store, "schema", None)
        if configured_schema is None or not str(configured_schema).strip():
            raise ValueError(
                f"schema is required for Warehouse target '{normalized_target}'; "
                "pass schema or configure a default schema."
            )
        normalized_schema, normalized_table, _object_name = resolve_warehouse_table_location(
            store, configured_schema, normalized_table
        )
    else:
        raise ValueError(
            f"Target '{normalized_target}' has unsupported store kind {store_kind or '<blank>'!r}; "
            "supported kinds are: lakehouse, warehouse."
        )

    return normalized_role, normalized_target, normalized_table, normalized_schema, store_kind, config, env, context


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
        audit_columns["_committed_at"].alias("profiled_at"),
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
    identities = profiled_df.select("column_id", "data_type", "profile_id", "profile_snapshot_id", "profiled_at")
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
        identities.profiled_at.cast("timestamp").alias("profiled_at"),
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
):
    """Return one table row and one row for each observed column asset."""
    from pyspark.sql import functions as F

    first = profiled_df.select(
        "table_id",
        "environment_name",
        "profiled_at",
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
        "first_profiled_at": first["profiled_at"],
        "last_profiled_at": first["profiled_at"],
        "is_active": True,
        **audit,
    }
    rows = [
        coerce_metadata_row_types(
            CATALOGUE_TABLE,
            {**common, "metadata_level": "table", "column_id": None, "column_name": None},
        )
    ]
    profiled_ids = {row.column_id for row in profiled_df.select("column_id").collect()}
    for field in source_df.schema.fields:
        column_id = build_column_id(first["table_id"], field.name)
        if column_id not in profiled_ids:
            continue
        rows.append(
            coerce_metadata_row_types(
                CATALOGUE_TABLE,
                {**common, "metadata_level": "column", "column_id": column_id, "column_name": field.name},
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
    recorded_at: Any,
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
            "recorded_at": recorded_at,
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
    target,
    table_name,
    schema=None,
    frequency_columns=None,
    frequency_top_n: int | None = None,
    frequency_max_distinct_percent: float | None = 80.0,
    frequency_profile_df=None,
):
    """Profile a Spark DataFrame and register normalized FabricOps metadata.

    One profiling invocation creates a shared ``profile_snapshot_id``. Each
    eligible column receives one ``profile_id`` in ``METADATA_DATA_PROFILED``.
    Its frequency distribution is produced in the same workflow and stored
    separately as flattened rows in ``METADATA_DATA_PROFILED_FREQUENCY`` to
    avoid embedding a large JSON distribution in the compact profile row.

    Stable ``table_id`` and ``column_id`` values are environment-independent;
    ``environment_name`` keeps Development and Production observations
    separate. Catalogue writes use that environment-aware grain, and Lineage
    records whether the table participated as a pipeline source or target.
    """
    (
        normalized_profile_role,
        normalized_target,
        normalized_table,
        normalized_schema,
        normalized_store_type,
        config,
        env,
        context,
    ) = _resolve_physical_identity(profile_role=profile_role, target=target, schema=schema, table_name=table_name)
    selected_frequency_columns = None if frequency_columns is None else list(frequency_columns)
    if frequency_max_distinct_percent is not None and (
        not math.isfinite(frequency_max_distinct_percent)
        or not 0.0 <= frequency_max_distinct_percent <= 100.0
    ):
        raise ValueError("frequency_max_distinct_percent must be finite and between 0.0 and 100.0 when supplied.")

    profile_df = build_profile_dataframe(df)
    table_id = build_table_id(normalized_store_type, normalized_target, normalized_schema, normalized_table)
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
            recorded_at=profiled_df.select("profiled_at").first()["profiled_at"],
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
