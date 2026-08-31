"""Shared pipeline implementation helpers."""

from __future__ import annotations

import json
from functools import reduce
from typing import Any, Mapping

from fabricops_kit.config.shared import get_audit_timezone, get_current_audit_timestamp, resolve_fabric_context
from ..io.shared import (
    configured_lakehouse_schema,
    get_spark_session,
    read_lakehouse_table_core,
    resolve_configured_lakehouse_table,
    resolve_lakehouse_table_location,
    resolve_warehouse_table_location,
    write_lakehouse_table_core,
)
from ..config.audit import _audit_timestamp_value, build_runtime_audit_fields
from ..config.shared import build_metadata_table_key, build_table_id, get_store
from ..config.metadata_schemas import coerce_metadata_row_types


_DEFAULT_PROFILE_EXCLUDE_COLUMNS = {
    "_pipeline_run_id",
    "_pipeline_name",
    "_pipeline_environment",
    "_source_table",
    "_record_loaded_timestamp",
    "_notebook_name",
    "_loaded_by",
    "_dq_check_status",
    "_dq_failed_rules",
    "_source_system",
    "_source_extract_timestamp",
    "_watermark_value",
    "_partition_bucket",
    "_sample_bucket",
    "_row_ingest_id",
    "_business_key_hash",
    "_row_hash",
    "pipeline_ts",
    "ingested_at_utc",
    "notebook_name",
    "loaded_by",
    "p_bucket",
    "sample_bucket",
    "row_ingest_id",
    "ingest_run_id",
    "pipeline_run_id",
    "loaded_at",
    "run_ingest_id",
    "_fabricops_run_id",
    "_fabricops_pipeline_name",
    "_fabricops_created_at",
    "_dq_check_status",
    "_dq_failed_rules",
}
_DEFAULT_PROFILE_EXCLUDE_PREFIXES = ("_fabricops_", "_dq_")
_TARGET_AUDIT_COLUMNS = (
    "_committed_at",
    "_committed_by",
    "_activity_id",
    "_workspace_id",
    "_notebook_id",
    "_notebook_name",
)
_SCD2_LIFECYCLE_COLUMNS = ("_effective_from", "_effective_to", "_is_current")
_TARGET_TECHNICAL_COLUMNS = {
    *_DEFAULT_PROFILE_EXCLUDE_COLUMNS,
    *_TARGET_AUDIT_COLUMNS,
    *_SCD2_LIFECYCLE_COLUMNS,
}


_PARTITION_CHECKPOINT_TABLE = "METADATA_SOURCE_PARTITION_CHECKPOINT"
_WATERMARK_CHECKPOINT_TABLE = "METADATA_SOURCE_WATERMARK_CHECKPOINT"


def complete_source_processing(
    completion_context: Mapping[str, Any] | None,
    *,
    context: dict[str, Any] | None = None,
) -> None:
    """Persist governed source progress using the physical writer's Fabric context."""
    if completion_context is None:
        return
    sources = completion_context.get("sources") if isinstance(completion_context, Mapping) else None
    if not isinstance(sources, list):
        raise ValueError("completion_context must contain a sources list from write_pipeline_prep().")
    config, env, resolved_context = resolve_fabric_context(context=context)
    audit = build_runtime_audit_fields(config=config, env=env, runtime_context=resolved_context)
    spark = get_spark_session()
    metadata_schema = configured_lakehouse_schema(config, env, "metadata")
    from ..config.metadata_schemas import metadata_table_schema_registry

    for source in sources:
        kind = source.get("type") if isinstance(source, Mapping) else None
        if kind == "watermark":
            identity = source.get("source")
            processing = source.get("source_processing")
            candidate = source.get("candidate")
            if (
                not isinstance(identity, Mapping)
                or not isinstance(processing, Mapping)
                or not isinstance(candidate, Mapping)
                or processing.get("read_strategy") != "incremental_watermark"
                or candidate.get("status") != "candidate"
                or candidate.get("column") != processing.get("watermark_column")
                or candidate.get("value") is None
            ):
                raise ValueError("Invalid governed watermark completion context.")
            table_name = _WATERMARK_CHECKPOINT_TABLE
            record = {
                "environment_name": env,
                "table_id": identity.get("table_id"),
                "watermark_column": candidate["column"],
                "watermark_value": str(candidate["value"]),
                **audit,
            }
        elif kind == "partition":
            if source.get("environment_name") != env or not source.get("table_id") or not source.get("observation_id"):
                raise ValueError("Invalid governed partition completion context.")
            table_name = _PARTITION_CHECKPOINT_TABLE
            record = {
                "environment_name": env,
                "table_id": source["table_id"],
                "observation_id": source["observation_id"],
                **audit,
            }
        else:
            raise ValueError("Unknown governed source completion type.")
        frame = spark.createDataFrame(
            [coerce_metadata_row_types(table_name, record)],
            schema=metadata_table_schema_registry()[table_name],
        )
        write_lakehouse_table_core(
            frame,
            table_name,
            target="metadata",
            schema=metadata_schema,
            context=resolved_context,
            mode="append",
        )


def resolve_physical_table_identity(
    config: Any,
    env: str,
    *,
    target: Any,
    schema: Any,
    table_name: Any,
) -> dict[str, str | None]:
    """Resolve one configured table to its canonical physical identity."""
    if not isinstance(target, str) or not target.strip():
        raise ValueError("target must be a non-empty string.")
    if not isinstance(table_name, str) or not table_name.strip():
        raise ValueError("table_name must be a non-empty string.")
    normalized_target = target.strip().lower()
    store = get_store(config, env, normalized_target)
    store_kind = str(getattr(store, "kind", "")).strip().lower()
    if store_kind == "lakehouse":
        if getattr(store, "schema_enabled", False) and schema is None and not getattr(store, "schema", None):
            raise ValueError(
                f"schema is required for schema-enabled Lakehouse target '{normalized_target}'; "
                "pass schema or configure a default schema."
            )
        normalized_table, normalized_schema, _path = resolve_lakehouse_table_location(
            store, table_name, schema
        )
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
            store, configured_schema, table_name
        )
    else:
        raise ValueError(
            f"Target '{normalized_target}' has unsupported store kind {store_kind or '<blank>'!r}; "
            "supported kinds are: lakehouse, warehouse."
        )
    return {
        "table_id": build_table_id(store_kind, normalized_target, normalized_schema, normalized_table),
        "target": normalized_target,
        "schema": normalized_schema,
        "table_name": normalized_table,
        "store_kind": store_kind,
    }


def resolve_profiled_columns(df, exclude_columns: list[str] | set[str] | None = None) -> list[str]:
    """Return non-technical column names from a Spark DataFrame."""
    excluded = set(_DEFAULT_PROFILE_EXCLUDE_COLUMNS)
    if exclude_columns:
        excluded.update(exclude_columns)
    return [
        name
        for name, _dtype in df.dtypes
        if name not in excluded and not any(str(name).startswith(prefix) for prefix in _DEFAULT_PROFILE_EXCLUDE_PREFIXES)
    ]


FREQUENCY_PROFILE_COLUMNS = [
    "COLUMN_NAME",
    "DATA_TYPE",
    "VALUE",
    "FREQUENCY_COUNT",
    "FREQUENCY_PERCENT",
    "FREQUENCY_RANK",
    "PROFILED_ROW_COUNT",
    "PROFILED_NON_NULL_COUNT",
]


def build_frequency_distribution_dataframe(df, *, columns=None, top_n: int | None = None):
    """Return exact value-frequency rows for selected Spark DataFrame columns."""
    from pyspark.sql import functions as F
    from pyspark.sql import types as T
    from pyspark.sql.types import ArrayType, BinaryType, MapType, StructType
    from pyspark.sql.window import Window

    if top_n is not None and top_n <= 0:
        raise ValueError("top_n must be greater than zero when supplied.")

    fields = {field.name: field for field in df.schema.fields}
    if columns is None:
        selected_columns = [
            name
            for name in resolve_profiled_columns(df)
            if not isinstance(fields[name].dataType, ArrayType | MapType | StructType | BinaryType)
        ]
    else:
        selected_columns = list(columns)
        missing = [name for name in selected_columns if name not in fields]
        if missing:
            raise ValueError(f"Requested columns do not exist: {', '.join(missing)}")

    if not selected_columns:
        schema = T.StructType(
            [
                T.StructField("COLUMN_NAME", T.StringType(), False),
                T.StructField("DATA_TYPE", T.StringType(), False),
                T.StructField("VALUE", T.StringType(), True),
                T.StructField("FREQUENCY_COUNT", T.LongType(), False),
                T.StructField("FREQUENCY_PERCENT", T.DoubleType(), True),
                T.StructField("FREQUENCY_RANK", T.IntegerType(), False),
                T.StructField("PROFILED_ROW_COUNT", T.LongType(), False),
                T.StructField("PROFILED_NON_NULL_COUNT", T.LongType(), False),
            ]
        )
        return df.sparkSession.createDataFrame([], schema)

    def column(name: str):
        return F.col(f"`{name.replace('`', '``')}`")

    metric_exprs = [F.count(F.lit(1)).cast("long").alias("PROFILED_ROW_COUNT")]
    for column_name in selected_columns:
        metric_exprs.append(
            F.count(column(column_name)).cast("long").alias(f"__{column_name}__PROFILED_NON_NULL_COUNT")
        )
    metrics_df = df.agg(*metric_exprs)
    row_count = F.col("PROFILED_ROW_COUNT")
    branches = []
    rank_window = Window.orderBy(F.col("FREQUENCY_COUNT").desc(), F.col("VALUE").asc_nulls_first())
    for column_name in selected_columns:
        value = column(column_name).cast("string")
        grouped = (
            df.groupBy(value.alias("VALUE"))
            .agg(F.count(F.lit(1)).cast("long").alias("FREQUENCY_COUNT"))
            .crossJoin(metrics_df)
            .withColumn(
                "FREQUENCY_PERCENT",
                F.when(row_count == 0, F.lit(0.0)).otherwise(
                    F.round((F.col("FREQUENCY_COUNT").cast("double") / row_count.cast("double")) * 100, 3)
                ),
            )
            .withColumn("FREQUENCY_RANK", F.row_number().over(rank_window))
        )
        if top_n is not None:
            grouped = grouped.where(F.col("FREQUENCY_RANK") <= F.lit(top_n))
        branches.append(
            grouped.select(
                F.lit(column_name).alias("COLUMN_NAME"),
                F.lit(fields[column_name].dataType.simpleString()).alias("DATA_TYPE"),
                F.col("VALUE"),
                F.col("FREQUENCY_COUNT"),
                F.col("FREQUENCY_PERCENT"),
                F.col("FREQUENCY_RANK"),
                F.col("PROFILED_ROW_COUNT"),
                F.col(f"__{column_name}__PROFILED_NON_NULL_COUNT").alias("PROFILED_NON_NULL_COUNT"),
            ).select(*FREQUENCY_PROFILE_COLUMNS)
        )

    return reduce(lambda left, right: left.unionByName(right), branches).select(*FREQUENCY_PROFILE_COLUMNS)


PROFILE_DATAFRAME_COLUMNS = [
    "COLUMN_NAME",
    "DATA_TYPE",
    "ROW_COUNT",
    "NON_NULL_COUNT",
    "NULL_COUNT",
    "NULL_PERCENT",
    "DISTINCT_COUNT",
    "DISTINCT_PERCENT",
    "MEAN",
    "STDDEV",
    "MIN_VALUE",
    "PERCENTILE_25",
    "MEDIAN",
    "PERCENTILE_75",
    "MAX_VALUE",
]


def _profile_column_expr(name: str):
    """Return a safely quoted Spark column expression."""
    from pyspark.sql import functions as F

    return F.col(f"`{name.replace('`', '``')}`")


def _profile_percent_expr(numerator, denominator):
    """Return a rounded percentage expression protected against zero rows."""
    from pyspark.sql import functions as F

    return F.when(denominator == 0, F.lit(0.0)).otherwise(F.round((numerator.cast("double") / denominator.cast("double")) * F.lit(100.0), 3))


def build_profile_dataframe(df, *, exclude_columns=None):
    """Return structural and statistical profile rows for a Spark DataFrame."""
    from pyspark.sql import functions as F
    from pyspark.sql.types import DateType, NumericType, StringType, TimestampType

    eligible_columns = resolve_profiled_columns(df, exclude_columns=exclude_columns)
    if not eligible_columns:
        raise ValueError("No eligible non-technical columns found for metadata profiling.")

    fields = {field.name: field for field in df.schema.fields}
    agg_exprs = [F.count(F.lit(1)).cast("long").alias("__ROW_COUNT")]

    for column_name in eligible_columns:
        col = _profile_column_expr(column_name)
        data_type = fields[column_name].dataType
        prefix = f"__{column_name}__"
        agg_exprs.extend([
            F.count(col).cast("long").alias(f"{prefix}NON_NULL_COUNT"),
            F.sum(col.isNull().cast("long")).cast("long").alias(f"{prefix}NULL_COUNT"),
            F.count_distinct(col).cast("long").alias(f"{prefix}DISTINCT_COUNT"),
        ])
        if isinstance(data_type, NumericType):
            agg_exprs.extend([
                F.avg(col).cast("double").alias(f"{prefix}MEAN"),
                F.stddev_samp(col).cast("double").alias(f"{prefix}STDDEV"),
                F.min(col).cast("string").alias(f"{prefix}MIN_VALUE"),
                F.percentile_approx(col, [0.25, 0.5, 0.75]).alias(f"{prefix}PERCENTILES"),
                F.max(col).cast("string").alias(f"{prefix}MAX_VALUE"),
            ])
        elif isinstance(data_type, DateType | TimestampType | StringType):
            agg_exprs.extend([
                F.min(col).cast("string").alias(f"{prefix}MIN_VALUE"),
                F.max(col).cast("string").alias(f"{prefix}MAX_VALUE"),
            ])

    agg_df = df.agg(*agg_exprs)
    row_count = F.col("__ROW_COUNT")
    rows = []
    for column_name in eligible_columns:
        data_type = fields[column_name].dataType
        prefix = f"__{column_name}__"
        non_null_count = F.coalesce(F.col(f"{prefix}NON_NULL_COUNT"), F.lit(0)).cast("long")
        null_count = F.coalesce(F.col(f"{prefix}NULL_COUNT"), F.lit(0)).cast("long")
        distinct_count = F.coalesce(F.col(f"{prefix}DISTINCT_COUNT"), F.lit(0)).cast("long")
        percentile = F.col(f"{prefix}PERCENTILES") if isinstance(data_type, NumericType) else None
        supports_min_max = isinstance(data_type, NumericType | DateType | TimestampType | StringType)
        rows.append(agg_df.select(
            F.lit(column_name).alias("COLUMN_NAME"),
            F.lit(data_type.simpleString()).alias("DATA_TYPE"),
            row_count.cast("long").alias("ROW_COUNT"),
            non_null_count.alias("NON_NULL_COUNT"),
            null_count.alias("NULL_COUNT"),
            _profile_percent_expr(null_count, row_count).alias("NULL_PERCENT"),
            distinct_count.alias("DISTINCT_COUNT"),
            _profile_percent_expr(distinct_count, row_count).alias("DISTINCT_PERCENT"),
            (F.col(f"{prefix}MEAN") if isinstance(data_type, NumericType) else F.lit(None).cast("double")).alias("MEAN"),
            (F.col(f"{prefix}STDDEV") if isinstance(data_type, NumericType) else F.lit(None).cast("double")).alias("STDDEV"),
            (F.col(f"{prefix}MIN_VALUE") if supports_min_max else F.lit(None).cast("string")).alias("MIN_VALUE"),
            (percentile.getItem(0).cast("double") if percentile is not None else F.lit(None).cast("double")).alias("PERCENTILE_25"),
            (percentile.getItem(1).cast("double") if percentile is not None else F.lit(None).cast("double")).alias("MEDIAN"),
            (percentile.getItem(2).cast("double") if percentile is not None else F.lit(None).cast("double")).alias("PERCENTILE_75"),
            (F.col(f"{prefix}MAX_VALUE") if supports_min_max else F.lit(None).cast("string")).alias("MAX_VALUE"),
        ))

    out = rows[0]
    for row in rows[1:]:
        out = out.unionByName(row)
    return out.select(*PROFILE_DATAFRAME_COLUMNS)

PROFILED_TABLE = "METADATA_DATA_PROFILED"
CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
LINEAGE_TABLE = "METADATA_DATA_LINEAGE"
GUARDRAIL_RESULTS_TABLE = "METADATA_GUARDRAIL_RESULTS"
DATA_CONTRACT_TABLE = "METADATA_DATA_CONTRACT"




# ---------------------------------------------------------------------------
# Public API layer
# ---------------------------------------------------------------------------







def _yes_no(value: Any) -> str:
    """Return notebook-friendly yes/no text."""
    return "yes" if bool(value) else "no"


def _result_status(result: Mapping[str, Any] | None) -> str:
    """Return a normalized guardrail result status."""
    return str(
        (result or {}).get("status")
        or (result or {}).get("freshness_status")
        or (result or {}).get("stability_status")
        or "not_run"
    ).lower()


def _result_can_continue(result: Mapping[str, Any] | None) -> bool:
    """Return whether a guardrail result can continue."""
    if not result:
        return True
    return bool(
        result.get("can_continue", result.get("freshness_can_continue", result.get("stability_can_continue", True)))
    )


def _result_reason(result: Mapping[str, Any] | None) -> str:
    """Return the clearest human-readable reason from a result."""
    if not result:
        return ""
    return str(
        result.get("reason")
        or result.get("message")
        or result.get("freshness_message")
        or result.get("stability_message")
        or ""
    )


def _next_action(guardrail: str, status: str) -> str:
    """Return concise user action guidance for a guardrail result."""
    if status in {"passed", "baseline_created", "skipped", "warning"}:
        return "Continue." if status != "warning" else "Review detailed mode when convenient."
    actions = {
        "schema": "Fix source data or update expected_schema.",
        "freshness": "Refresh source data or adjust freshness rule.",
        "profile_behavior": "Review source change or approve reset in governance.",
        "dq": "Review failed DQ rules and source data.",
        "catalogue": "Check metadata lakehouse write configuration and permissions.",
    }
    return actions.get(guardrail, "Review detailed mode.")


def _schema_reason(result: Mapping[str, Any]) -> str:
    missing = result.get("missing_columns") or []
    unexpected = result.get("unexpected_columns") or []
    mismatches = result.get("datatype_mismatches") or []
    parts = []
    if missing:
        parts.append("missing column " + ", ".join(map(str, missing)))
    if unexpected:
        parts.append("unexpected column " + ", ".join(map(str, unexpected)))
    if mismatches:
        parts.append(f"{len(mismatches)} datatype mismatch(es)")
    return "Schema failed: " + "; ".join(parts) + "." if parts else "Schema failed."


def _freshness_reason(result: Mapping[str, Any]) -> str:
    column = result.get("freshness_column") or "freshness column"
    if _result_status(result) == "failed":
        return f"Freshness failed: latest {column} is older than allowed lag."
    return _result_reason(result) or "Freshness check passed."


def _profile_behavior_reason(result: Mapping[str, Any]) -> str:
    status = _result_status(result)
    if status == "baseline_created":
        return "Profile behavior baseline created."
    differences = result.get("differences") or []
    if not differences and result.get("stability_difference_summary"):
        try:
            differences = json.loads(str(result.get("stability_difference_summary") or "[]"))
        except json.JSONDecodeError:
            differences = []
    if status == "failed" or differences:
        for diff in differences:
            diff_type = str(diff.get("difference_type") or "")
            watermark = str(diff.get("watermark_value") or "")
            if diff_type == "missing_watermark_value":
                return f"Profile behavior failed: previous watermark group {watermark} disappeared."
            if diff_type == "profile_changed" and watermark and watermark != "__FULL_TABLE__":
                return f"Profile behavior failed: previous watermark group {watermark} changed."
            if diff_type == "profile_changed":
                return "Profile behavior failed: static data changed from accepted baseline."
        return "Profile behavior failed: static data changed from accepted baseline."
    new_groups = result.get("new_watermark_values") or []
    if new_groups:
        return "Profile behavior passed: new watermark accepted."
    return _result_reason(result) or "Profile behavior guardrail passed."


def _dq_reason(result: Mapping[str, Any]) -> str:
    checks = result.get("checks") or []
    blocking = [
        check
        for check in checks
        if str(check.get("status") or "").lower() in {"failed", "error"}
        and str(check.get("severity") or "warning").lower() in {"error", "blocking"}
    ]
    warnings = [
        check
        for check in checks
        if str(check.get("status") or "").lower() in {"failed", "error", "warning"}
        and str(check.get("severity") or "warning").lower() not in {"error", "blocking"}
    ]
    if blocking:
        return f"DQ failed: {len(blocking)} blocking DQ rule(s) failed."
    if warnings:
        return f"DQ warning: {len(warnings)} warning DQ rule(s) failed."
    return _result_reason(result) or "DQ guardrail passed."


def _guardrail_reason(guardrail: str, result: Mapping[str, Any]) -> str:
    """Return plain-language reason text for one guardrail."""
    if guardrail == "schema":
        return (
            _schema_reason(result)
            if _result_status(result) == "failed"
            else (_result_reason(result) or "Schema validation passed.")
        )
    if guardrail == "freshness":
        return _freshness_reason(result)
    if guardrail == "profile_behavior":
        return _profile_behavior_reason(result)
    if guardrail == "dq":
        return _dq_reason(result)
    return _result_reason(result)


def _table_keys(result_bundle: Mapping[str, Any]) -> list[str]:
    """Return stable table keys present in a guardrail result bundle."""
    keys: set[str] = set()
    for name in ("schema_results", "freshness_results", "stability_results", "dq_results", "catalogue_status"):
        value = result_bundle.get(name) or {}
        if isinstance(value, Mapping):
            keys.update(str(key) for key in value)
    return sorted(keys)


SOURCE_OBSERVATION_COLUMNS = frozenset(
    {
        "observation_id",
        "table_id",
        "environment_name",
        "partition_value",
        "row_count",
        "min_change_value",
        "max_change_value",
        "is_present",
        "observed_at",
    }
)


def observation_rows(dataframe: Any) -> list[dict[str, Any]]:
    """Return canonical observation rows as dictionaries."""
    values = dataframe.collect() if hasattr(dataframe, "collect") else dataframe
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in values or []]


def guardrail_compatibility_observation(
    observation: Any, *, table_id: str, change_column: str
) -> Any:
    """Add temporary in-memory aliases required by the Stage 4 Guardrail model."""
    if hasattr(observation, "withColumn"):
        from pyspark.sql import functions as F

        return observation.withColumn("metadata_table_key", F.lit(table_id)).withColumn(
            "change_column", F.lit(change_column)
        )
    return [
        {**row, "metadata_table_key": table_id, "change_column": change_column}
        for row in observation_rows(observation)
    ]


# ---------------------------------------------------------------------------
# Guardrail shared implementation
# ---------------------------------------------------------------------------

import hashlib

import re

from datetime import date, datetime, timedelta

from decimal import Decimal

from uuid import uuid4

from fabricops_kit.config.shared import is_table_not_found_error

def write_guardrail_result_row(
    *,
    spark_session: Any,
    config: Any,
    env: str,
    run_id: str,
    dataset_name: str,
    table_name: str,
    store_type: str,
    layer: str,
    schema_name: str | None = None,
    guardrail_type: str,
    rule_type: str,
    result: dict[str, Any],
    rule_key: str = "",
    column_name: str = "",
    results_table: str = "METADATA_GUARDRAIL_RESULTS",
) -> None:
    """Append one runtime outcome for one exact Guardrail revision."""
    del dataset_name, table_name, store_type, layer, schema_name, guardrail_type, rule_type, rule_key, column_name
    if spark_session is None or not hasattr(spark_session, "createDataFrame"):
        return
    guardrail_rule_id = str(result.get("guardrail_rule_id") or "").strip()
    if not guardrail_rule_id:
        return
    guardrail_version = int(result.get("guardrail_version") or 0)
    if guardrail_version <= 0:
        raise ValueError("guardrail_version is required to persist a Guardrail result.")
    audit = build_runtime_audit_fields(config=config, env=env)
    resolved_run_id = str(run_id or "").strip() or str(audit["_activity_id"])
    payload = {key: value for key, value in result.items() if key != "dataframe"}
    row = {
        "guardrail_result_id": str(uuid4()),
        "guardrail_rule_id": guardrail_rule_id,
        "guardrail_version": guardrail_version,
        "run_id": resolved_run_id,
        "environment_name": env,
        "status": str(result.get("status") or "not_run"),
        "can_continue": bool(result.get("can_continue", True)),
        "severity": str(result.get("severity") or "blocking"),
        "reason": str(result.get("reason") or result.get("message") or ""),
        "result_payload_json": json.dumps(payload, default=str, sort_keys=True, separators=(",", ":")),
        **audit,
    }
    write_lakehouse_table_core(
        spark_session.createDataFrame([coerce_metadata_row_types(results_table, row)]),
        results_table,
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
        mode="append",
    )

_DEFAULT_STABILITY_EXCLUDE_COLUMNS = {
    "_fabricops_run_id",
    "_fabricops_pipeline_name",
    "_fabricops_created_at",
    "_dq_check_status",
    "_dq_failed_rules",
}

_DEFAULT_STABILITY_EXCLUDE_PREFIXES = ("_fabricops_", "_dq_")

_ACTIVE_RULE_REVIEW_STATUSES = {"authored", "self_approved", "governance_approved", "active_pending_governance_review"}

_BYPASS_POST_REVIEW_WARNING = "Rule is active through approval bypass and requires governance post-review."

GUARDRAIL_TABLE = "METADATA_GUARDRAIL"

GUARDRAIL_CHANGE_BEHAVIOURS = ("No changes expected", "Incremental append", "Snapshot overwrite")

_GUARDRAIL_CHANGE_BEHAVIOUR_MAPPING = {
    "No changes expected": ("no_change_required", "snapshot"),
    "Incremental append": ("monitor_only", "incremental_append"),
    "Snapshot overwrite": ("monitor_only", "snapshot"),
}

DQ_RULE_TYPES = [
    "missing_values",
    "blank_text",
    "unique_values",
    "unique_combination",
    "allowed_values",
    "blocked_values",
    "value_range",
    "text_pattern",
    "required_when",
    "conditional_value",
    "compare_columns",
]

DQ_COMPARISON_OPERATORS = ("=", "!=", ">", ">=", "<", "<=")

_SOURCE_PATTERNS = {"snapshot", "incremental_append", "mutable_incremental", "versioned"}

_COMPARISON_SCOPES = {"complete", "partitions", "partial"}

def _is_spark_dataframe(dataframe) -> bool:
    """Return whether a value exposes the Spark DataFrame contract used here."""
    return dataframe is not None and hasattr(dataframe, "sparkSession") and hasattr(dataframe, "schema")

def _local_source_rows(dataframe) -> list[dict]:
    """Return local row mappings without accepting Spark DataFrames."""
    if _is_spark_dataframe(dataframe):
        raise TypeError("Spark DataFrames must use the distributed changes implementation")
    if dataframe is None:
        return []
    rows = [dataframe] if isinstance(dataframe, dict) else dataframe
    return [_row_to_dict(row) for row in rows]

def _stable_source_value(value):
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _stable_source_value(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [_stable_source_value(item) for item in value]
    return value

def _source_hash(payload) -> str:
    encoded = json.dumps(_stable_source_value(payload), sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

def _validate_changes_configuration(source_pattern, comparison_scope, refresh_days, version_column):
    pattern = str(source_pattern).strip().lower()
    scope = str(comparison_scope).strip().lower()
    if pattern not in _SOURCE_PATTERNS:
        raise ValueError("source_pattern must be one of: snapshot, incremental_append, mutable_incremental, versioned")
    if scope not in _COMPARISON_SCOPES:
        raise ValueError("comparison_scope must be one of: complete, partitions, partial")
    if isinstance(refresh_days, bool):
        raise ValueError("refresh_days must be a non-negative integer")
    try:
        window_days = int(refresh_days)
    except (TypeError, ValueError) as exc:
        raise ValueError("refresh_days must be a non-negative integer") from exc
    if window_days < 0:
        raise ValueError("refresh_days must be a non-negative integer")
    if pattern == "versioned" and not str(version_column or "").strip():
        raise ValueError("version_column is required when source_pattern='versioned'")
    return pattern, scope, window_days

def _partition_identity(row, partitions):
    return tuple(row.get(column) for column in partitions) if partitions else ("__FULL_SOURCE__",)

def _local_latest_versions(rows, keys, version_column):
    latest = {}
    for row in rows:
        identity = tuple(row.get(column) for column in keys)
        if any(value is None for value in identity):
            raise ValueError("logical key columns must not contain null values")
        version = row.get(version_column)
        if version is None:
            raise ValueError("version_column must not contain null values")
        if identity not in latest or version > latest[identity].get(version_column):
            latest[identity] = row
        elif version == latest[identity].get(version_column):
            raise ValueError("version_column must uniquely order versions for each logical key")
    return list(latest.values())

def _validate_local_logical_keys(rows, keys):
    seen = set()
    for row in rows:
        identity = tuple(row.get(column) for column in keys)
        if any(value is None for value in identity):
            raise ValueError("logical key columns must not contain null values")
        key_hash = _source_hash(identity)
        if key_hash in seen:
            raise ValueError("logical key columns must uniquely identify rows")
        seen.add(key_hash)

def _local_partition_observations(rows, partitions, range_column, all_columns):
    grouped = {}
    for row in rows:
        grouped.setdefault(_partition_identity(row, partitions), []).append(row)
    observations = []
    for partition, members in sorted(grouped.items(), key=lambda item: str(item[0])):
        values = [row.get(range_column) for row in members if range_column and row.get(range_column) is not None]
        row_hashes = sorted(_source_hash([(column, row.get(column)) for column in all_columns]) for row in members)
        observations.append({
            "partition": dict(zip(partitions, partition, strict=True)) if partitions else {},
            "row_count": len(members),
            "min_value": _stable_source_value(min(values)) if values else None,
            "max_value": _stable_source_value(max(values)) if values else None,
            "fingerprint": _source_hash(row_hashes),
            "_partition_id": _source_hash(partition),
        })
    return observations

def _changed_partition_sets(current_observations, previous_observations, scope):
    current = {item["_partition_id"]: item for item in current_observations}
    previous = {item["_partition_id"]: item for item in previous_observations}
    changed = {key for key in current.keys() & previous.keys() if current[key]["fingerprint"] != previous[key]["fingerprint"]}
    new = current.keys() - previous.keys()
    missing = previous.keys() - current.keys() if scope == "complete" else set()
    return changed, set(new), set(missing)

def _classify_change_date(value, recent_start):
    observed = _coerce_date(value)
    return "recent" if observed is not None and observed >= recent_start else "historical"

def _local_row_comparison(current, previous, *, relevant_current_partitions, relevant_previous_partitions,
                          partitions, keys, content_columns, range_column, scope, pattern, recent_start):
    current = [row for row in current if _source_hash(_partition_identity(row, partitions)) in relevant_current_partitions]
    previous = [row for row in previous if _source_hash(_partition_identity(row, partitions)) in relevant_previous_partitions]

    def keyed(rows):
        output = {}
        for row in rows:
            identity = tuple(row.get(column) for column in keys)
            if any(value is None for value in identity):
                raise ValueError("logical key columns must not contain null values")
            key_hash = _source_hash(identity)
            if key_hash in output:
                raise ValueError("logical key columns must uniquely identify rows")
            output[key_hash] = (row, _source_hash([(column, row.get(column)) for column in content_columns]))
        return output

    current_by_key, previous_by_key = keyed(current), keyed(previous)
    inserted = sorted(set(current_by_key) - set(previous_by_key))
    shared = set(current_by_key) & set(previous_by_key)
    updated = sorted(key for key in shared if current_by_key[key][1] != previous_by_key[key][1])
    deletion_allowed = scope in {"complete", "partitions"} and pattern != "incremental_append"
    deleted = sorted(set(previous_by_key) - set(current_by_key)) if deletion_allowed else []
    changes = {"inserted": inserted, "updated": updated, "deleted": deleted}
    recent, historical = [], []
    for change_type, hashes in changes.items():
        source = previous_by_key if change_type == "deleted" else current_by_key
        for key_hash in hashes:
            classified = {"key_hash": key_hash, "change_type": change_type}
            if range_column:
                target = recent if _classify_change_date(source[key_hash][0].get(range_column), recent_start) == "recent" else historical
                target.append(classified)
    return changes, recent, historical

def _spark_column(name):
    from pyspark.sql import functions as F
    return F.col(f"`{str(name).replace('`', '``')}`")

def _spark_canonical_hash(columns):
    from pyspark.sql import functions as F
    struct = F.struct(*[_spark_column(column).alias(str(column)) for column in columns])
    return F.sha2(F.to_json(struct, {"ignoreNullFields": "false"}), 256)

def _spark_resolve_versions(dataframe, keys, version_column):
    from pyspark.sql import functions as F
    from pyspark.sql.window import Window
    if dataframe.filter(_spark_column(version_column).isNull()).limit(1).count():
        raise ValueError("version_column must not contain null values")
    window = Window.partitionBy(*[_spark_column(column) for column in keys]).orderBy(_spark_column(version_column).desc())
    ranked = dataframe.withColumn("__fabricops_version_rank", F.dense_rank().over(window))
    if ranked.filter(F.col("__fabricops_version_rank") == 1).groupBy(*keys).count().filter(F.col("count") > 1).limit(1).count():
        raise ValueError("version_column must uniquely order versions for each logical key")
    return ranked.filter(F.col("__fabricops_version_rank") == 1).drop("__fabricops_version_rank")

def _validate_spark_logical_keys(dataframe, keys):
    from functools import reduce
    from pyspark.sql import functions as F
    null_key = reduce(lambda left, right: left | right, [_spark_column(column).isNull() for column in keys])
    if dataframe.filter(null_key).limit(1).count():
        raise ValueError("logical key columns must not contain null values")
    if dataframe.groupBy(*keys).count().filter(F.col("count") > 1).limit(1).count():
        raise ValueError("logical key columns must uniquely identify rows")

def _spark_partition_frame(dataframe, partitions, range_column, all_columns):
    from pyspark.sql import functions as F
    partition_id = _spark_canonical_hash(partitions) if partitions else F.lit(_source_hash(("__FULL_SOURCE__",)))
    row_hash = _spark_canonical_hash(all_columns)
    prepared = dataframe.withColumn("__fabricops_partition_id", partition_id).withColumn("__fabricops_row_hash", row_hash)
    grouping = ["__fabricops_partition_id", *partitions]
    aggregates = [
        F.count(F.lit(1)).alias("row_count"),
        F.min("__fabricops_row_hash").alias("__min_hash"),
        F.max("__fabricops_row_hash").alias("__max_hash"),
        F.sum(F.xxhash64("__fabricops_row_hash").cast("decimal(38,0)")).alias("__hash_sum"),
    ]
    if range_column:
        aggregates.extend([F.min(_spark_column(range_column)).alias("min_value"), F.max(_spark_column(range_column)).alias("max_value")])
    grouped = prepared.groupBy(*grouping).agg(*aggregates)
    grouped = grouped.withColumn(
        "fingerprint",
        F.sha2(F.concat_ws("|", F.col("row_count"), F.col("__min_hash"), F.col("__max_hash"), F.col("__hash_sum")), 256),
    )
    return prepared.drop("__fabricops_row_hash"), grouped

def _collect_spark_observations(grouped, partitions):
    from pyspark.sql import functions as F
    rows = grouped.select("__fabricops_partition_id", *partitions, "row_count", "min_value" if "min_value" in grouped.columns else F.lit(None).alias("min_value"), "max_value" if "max_value" in grouped.columns else F.lit(None).alias("max_value"), "fingerprint").collect()
    return [{
        "partition": {column: _stable_source_value(row[column]) for column in partitions},
        "row_count": row["row_count"],
        "min_value": _stable_source_value(row["min_value"]),
        "max_value": _stable_source_value(row["max_value"]),
        "fingerprint": row["fingerprint"],
        "_partition_id": row["__fabricops_partition_id"],
    } for row in rows]

def _spark_row_comparison(current, previous, *, relevant_current_partitions, relevant_previous_partitions,
                          keys, content_columns, range_column, scope, pattern, recent_start, include_row_changes):
    from pyspark.sql import functions as F
    current = current.filter(F.col("__fabricops_partition_id").isin(sorted(relevant_current_partitions)))
    previous = previous.filter(F.col("__fabricops_partition_id").isin(sorted(relevant_previous_partitions)))
    current = current.withColumn("key_hash", _spark_canonical_hash(keys)).withColumn("non_key_hash", _spark_canonical_hash(content_columns))
    previous = previous.withColumn("key_hash", _spark_canonical_hash(keys)).withColumn("non_key_hash", _spark_canonical_hash(content_columns))
    for dataframe in (current, previous):
        if dataframe.groupBy("key_hash").count().filter(F.col("count") > 1).limit(1).count():
            raise ValueError("logical key columns must uniquely identify rows")
    current_rows = current.select("key_hash", "non_key_hash", *([_spark_column(range_column).alias("range_value")] if range_column else [F.lit(None).alias("range_value")]))
    previous_rows = previous.select("key_hash", "non_key_hash", *([_spark_column(range_column).alias("range_value")] if range_column else [F.lit(None).alias("range_value")]))
    joined = current_rows.alias("c").join(previous_rows.alias("p"), "key_hash", "full_outer")
    deletion_allowed = scope in {"complete", "partitions"} and pattern != "incremental_append"
    classified = joined.withColumn("change_type", F.when(F.col("p.non_key_hash").isNull(), "inserted").when(F.col("c.non_key_hash").isNull() & F.lit(deletion_allowed), "deleted").when(F.col("c.non_key_hash") != F.col("p.non_key_hash"), "updated"))
    classified = classified.filter(F.col("change_type").isNotNull())
    change_date = F.coalesce(F.col("c.range_value"), F.col("p.range_value")).cast("date")
    classified = classified.withColumn("age_class", F.when(change_date >= F.lit(recent_start), "recent").otherwise("historical") if range_column else F.lit(None).cast("string"))
    counts = {row["change_type"]: row["count"] for row in classified.groupBy("change_type").count().collect()}
    ages = {row["age_class"]: row["count"] for row in classified.filter(F.col("age_class").isNotNull()).groupBy("age_class").count().collect()}
    row_changes = {"inserted": [], "updated": [], "deleted": [], "recent": [], "historical": []}
    if include_row_changes:
        for row in classified.select("key_hash", "change_type", "age_class").collect():
            row_changes[row["change_type"]].append(row["key_hash"])
            if row["age_class"]:
                row_changes[row["age_class"]].append({"key_hash": row["key_hash"], "change_type": row["change_type"]})
    return counts, ages, row_changes

def _strip_internal_observation_fields(observations):
    return [{key: value for key, value in item.items() if not key.startswith("_")} for item in observations]

def _changes_content_columns(columns, keys, non_key_columns, pattern, version_column):
    """Resolve content columns without treating version metadata as business data."""
    if non_key_columns is not None:
        return tuple(non_key_columns)
    return tuple(
        column
        for column in columns
        if column not in keys and not (pattern == "versioned" and column == version_column)
    )

def changes_check_core(
    dataframe,
    previous_dataframe=None,
    *,
    partition_columns: list[str] | tuple[str, ...] | None = None,
    key_columns: list[str] | tuple[str, ...] | None = None,
    non_key_columns: list[str] | tuple[str, ...] | None = None,
    range_column: str | None = None,
    source_pattern: str = "snapshot",
    comparison_scope: str = "complete",
    refresh_days: int = 0,
    version_column: str | None = None,
    reference_date: date | datetime | str | None = None,
    include_row_changes: bool = False,
) -> dict:
    """Compare current and previous observations using tiered deterministic checks."""
    pattern, scope, refresh_days = _validate_changes_configuration(source_pattern, comparison_scope, refresh_days, version_column)
    keys = tuple(key_columns or ())
    if not keys:
        raise ValueError("key_columns must contain at least one logical key column")
    partitions = tuple(partition_columns or ([range_column] if range_column else []))
    today = _coerce_date(reference_date) if reference_date is not None else date.today()
    if today is None:
        raise ValueError("reference_date must be a date, datetime, or ISO date string")
    recent_start = today - timedelta(days=refresh_days)
    spark_mode = _is_spark_dataframe(dataframe)
    if spark_mode != _is_spark_dataframe(previous_dataframe) and previous_dataframe is not None:
        raise ValueError("current and previous observations must both be Spark DataFrames or both be local iterables")

    if spark_mode:
        current = dataframe
        previous = previous_dataframe if previous_dataframe is not None else dataframe.sparkSession.createDataFrame([], dataframe.schema)
        columns = sorted(set(current.columns) | set(previous.columns))
        required = (*partitions, *keys, *((version_column,) if version_column else ()))
        missing = [column for column in required if column not in columns]
        if missing:
            raise ValueError(f"Configured changes columns do not exist: {', '.join(missing)}")
        content_columns = _changes_content_columns(columns, keys, non_key_columns, pattern, version_column)
        if pattern == "versioned":
            current, previous = _spark_resolve_versions(current, keys, version_column), _spark_resolve_versions(previous, keys, version_column)
        _validate_spark_logical_keys(current, keys)
        _validate_spark_logical_keys(previous, keys)
        current_prepared, current_grouped = _spark_partition_frame(current, partitions, range_column, columns)
        previous_prepared, previous_grouped = _spark_partition_frame(previous, partitions, range_column, columns)
        current_observations = _collect_spark_observations(current_grouped, partitions)
        previous_observations = _collect_spark_observations(previous_grouped, partitions)
    else:
        current, previous = _local_source_rows(dataframe), _local_source_rows(previous_dataframe)
        columns = sorted({str(column) for row in current + previous for column in row})
        required = (*partitions, *keys, *((version_column,) if version_column else ()))
        missing = [column for column in required if column not in columns]
        if missing:
            raise ValueError(f"Configured changes columns do not exist: {', '.join(missing)}")
        content_columns = _changes_content_columns(columns, keys, non_key_columns, pattern, version_column)
        if pattern == "versioned":
            current, previous = _local_latest_versions(current, keys, version_column), _local_latest_versions(previous, keys, version_column)
        _validate_local_logical_keys(current, keys)
        _validate_local_logical_keys(previous, keys)
        current_observations = _local_partition_observations(current, partitions, range_column, columns)
        previous_observations = _local_partition_observations(previous, partitions, range_column, columns)

    changed_ids, new_ids, missing_ids = _changed_partition_sets(current_observations, previous_observations, scope)
    current_ids = changed_ids | new_ids
    previous_ids = changed_ids | (missing_ids if scope == "complete" else set())
    if scope == "partitions":
        previous_ids = changed_ids
    row_changes = {"inserted": [], "updated": [], "deleted": [], "recent": [], "historical": []}
    counts = {"inserted": 0, "updated": 0, "deleted": 0}
    ages = {"recent": 0, "historical": 0}
    if current_ids or previous_ids:
        if spark_mode:
            counts, ages, row_changes = _spark_row_comparison(
                current_prepared, previous_prepared, relevant_current_partitions=current_ids,
                relevant_previous_partitions=previous_ids, keys=keys, content_columns=content_columns,
                range_column=range_column, scope=scope, pattern=pattern, recent_start=recent_start,
                include_row_changes=include_row_changes,
            )
        else:
            changes, recent, historical = _local_row_comparison(
                current, previous, relevant_current_partitions=current_ids,
                relevant_previous_partitions=previous_ids, partitions=partitions, keys=keys,
                content_columns=content_columns, range_column=range_column, scope=scope,
                pattern=pattern, recent_start=recent_start,
            )
            counts = {name: len(values) for name, values in changes.items()}
            ages = {"recent": len(recent), "historical": len(historical)}
            row_changes = {**changes, "recent": recent, "historical": historical}

    current_values = [item["min_value"] for item in current_observations if item["min_value"] is not None] + [item["max_value"] for item in current_observations if item["max_value"] is not None]
    previous_values = [item["min_value"] for item in previous_observations if item["min_value"] is not None] + [item["max_value"] for item in previous_observations if item["max_value"] is not None]
    previous_max = max(previous_values) if previous_values else None
    unseen_values = [value for value in current_values if previous_max is None or value > previous_max]
    changed = bool(changed_ids or new_ids or missing_ids)
    current_by_id = {item["_partition_id"]: item for item in current_observations}
    result = {
        "status": "changed" if changed else "unchanged", "can_continue": True,
        "check_type": "changes", "guardrail_type": "changes", "changed": changed,
        "source_pattern": pattern, "comparison_scope": scope,
        "pattern_semantics": {"snapshot": "full_state", "incremental_append": "append_only", "mutable_incremental": "mutable_window", "versioned": "latest_version_per_key"}[pattern],
        "partition_observations": _strip_internal_observation_fields(current_observations),
        "changed_partitions": [current_by_id[key]["partition"] for key in sorted(changed_ids)],
        "new_partitions": [current_by_id[key]["partition"] for key in sorted(new_ids)],
        "recent_changes": ages.get("recent", 0), "historical_changes": ages.get("historical", 0),
        "inserted_count": counts.get("inserted", 0), "updated_count": counts.get("updated", 0),
        "deleted_count": counts.get("deleted", 0),
        "deletions_provable": scope == "complete" or (scope == "partitions" and bool(partitions)),
        "append_violation_count": counts.get("updated", 0) if pattern == "incremental_append" else 0,
        "historical_mutation_detected": pattern == "mutable_incremental" and ages.get("historical", 0) > 0,
        "current_observed_range": {"min": min(current_values) if current_values else None, "max": max(current_values) if current_values else None},
        "previous_observed_range": {"min": min(previous_values) if previous_values else None, "max": previous_max},
        "recent_mutable_range": {"start": recent_start.isoformat(), "end": today.isoformat(), "refresh_days": refresh_days},
        "new_unseen_range": {"min": min(unseen_values) if unseen_values else None, "max": max(unseen_values) if unseen_values else None},
        "message": "Source changes detected." if changed else "Source is unchanged.",
    }
    if include_row_changes:
        result["row_changes"] = row_changes
    return result

def _rule_review_status(row: dict) -> str:
    return _string_value(_catalogue_value(row, "review_state", "review_status")).lower()

def _is_active_guardrail_rule(row: dict) -> bool:
    activation_state = _string_value(_catalogue_value(row, "activation_state")).lower()
    if activation_state:
        if activation_state != "active":
            return False
    elif _catalogue_value(row, "is_active") is not True:
        return False
    review_status = _rule_review_status(row)
    return not review_status or review_status in _ACTIVE_RULE_REVIEW_STATUSES

def _parse_rule_parameters(row: dict) -> dict:
    raw = _catalogue_value(row, "rule_parameters_json") or "{}"
    try:
        return json.loads(raw) if isinstance(raw, str) else dict(raw or {})
    except Exception:
        return {}

def _select_table_guardrail_rule(rules_df, *, guardrail_type: str, dataset_name: str, table_name: str, environment_name: str = "", metadata_table_key: str = "") -> dict | None:
    if rules_df is None:
        return None
    rows = rules_df.collect() if hasattr(rules_df, "collect") else ([rules_df] if isinstance(rules_df, dict) else rules_df)
    candidates = []
    for raw in rows or []:
        row = _row_to_dict(raw)
        if _string_value(_catalogue_value(row, "guardrail_type")).lower() != guardrail_type:
            continue
        rule_environment = _string_value(_catalogue_value(row, "environment_name"))
        if rule_environment and environment_name and rule_environment != environment_name:
            continue
        if dataset_name and _string_value(_catalogue_value(row, "dataset_name")) != dataset_name:
            continue
        if table_name and _string_value(_catalogue_value(row, "table_name")) != table_name:
            continue
        rule_table_key = _string_value(_catalogue_value(row, "table_id", "metadata_table_key"))
        if metadata_table_key and rule_table_key != metadata_table_key:
            continue
        if not _is_active_guardrail_rule(row):
            continue
        candidates.append(row)
    if not candidates:
        return None
    candidates.sort(key=lambda row: (int(_catalogue_value(row, "configuration_version") or 0), _string_value(_catalogue_value(row, "approved_at", "created_at", "_committed_at"))), reverse=True)
    return candidates[0]

def _contract_payload(row: dict[str, Any]) -> dict[str, Any]:
    """Return and minimally validate one frozen Data Contract payload."""
    try:
        payload = json.loads(str(row.get("contract_payload_json") or ""))
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Active Data Contract contract_payload_json is invalid JSON.") from exc
    contract = payload.get("contract") if isinstance(payload, dict) else None
    table = payload.get("table") if isinstance(payload, dict) else None
    if not isinstance(contract, dict) or not isinstance(table, dict):
        raise ValueError("Active Data Contract payload must identify its contract and table.")
    if str(contract.get("contract_id") or "") != str(row.get("contract_id") or ""):
        raise ValueError("Active Data Contract payload contract_id does not match its version row.")
    if int(contract.get("contract_version") or 0) != int(row.get("contract_version") or 0):
        raise ValueError("Active Data Contract payload contract_version does not match its version row.")
    if str(table.get("table_id") or "") != str(row.get("table_id") or ""):
        raise ValueError("Active Data Contract payload table_id does not match its version row.")
    return payload


def resolve_active_data_contract(config, env: str, table_id: str, *, spark_session=None, required: bool = True) -> dict[str, Any] | None:
    """Resolve the unambiguous active frozen contract for one logical table."""
    try:
        frame = read_lakehouse_table_core(
            DATA_CONTRACT_TABLE, target="metadata",
            schema=configured_lakehouse_schema(config, env, "metadata"),
            spark_session=spark_session, context={"config": config, "env": env},
        )
    except Exception as exc:
        if is_table_not_found_error(exc) and not required:
            return None
        if is_table_not_found_error(exc):
            raise ValueError("No Data Contracts exist; Governance must register and activate one first.") from exc
        raise
    rows = [_row_to_dict(row) for row in frame.collect()]
    matching = [row for row in rows if str(row.get("table_id") or "") == str(table_id)]
    active = [row for row in matching if row.get("is_active") is True]
    if len(active) > 1:
        raise RuntimeError(f"Data Contract integrity error: {table_id!r} has multiple active versions.")
    if not active:
        if required or matching:
            raise ValueError(f"No active Data Contract exists for {table_id!r}; Governance must activate one first.")
        return None
    row = dict(active[0])
    if str(row.get("status") or "").lower() != "active":
        raise RuntimeError(f"Data Contract integrity error: active version for {table_id!r} does not have status='active'.")
    row["contract_payload"] = _contract_payload(row)
    return row


def _resolve_data_contract_version(
    config,
    env: str,
    table_id: str,
    contract_id: str,
    contract_version: Any,
    *,
    spark_session=None,
    context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve and validate one exact immutable Data Contract version."""
    try:
        requested_version = int(contract_version)
    except (TypeError, ValueError) as exc:
        raise ValueError("data_contract_version must identify an exact integer version.") from exc
    try:
        frame = read_lakehouse_table_core(
            DATA_CONTRACT_TABLE,
            target="metadata",
            schema=configured_lakehouse_schema(config, env, "metadata"),
            spark_session=spark_session,
            context=context or {"config": config, "env": env},
        )
    except Exception as exc:
        if is_table_not_found_error(exc):
            raise ValueError(
                f"Data Contract {contract_id!r} version {requested_version} does not exist."
            ) from exc
        raise
    rows = [_row_to_dict(row) for row in frame.collect()]
    matches = [
        row for row in rows
        if str(row.get("contract_id") or "") == contract_id
        and int(row.get("contract_version") or 0) == requested_version
    ]
    if not matches:
        raise ValueError(f"Data Contract {contract_id!r} version {requested_version} does not exist.")
    if len(matches) > 1:
        raise RuntimeError(
            f"Data Contract integrity error: {contract_id!r} version {requested_version} has duplicate version rows."
        )
    row = dict(matches[0])
    if str(row.get("table_id") or "") != table_id:
        raise ValueError(
            f"Data Contract {contract_id!r} version {requested_version} does not belong to table_id {table_id!r}."
        )
    if str(row.get("status") or "").strip().lower() == "rejected":
        raise ValueError(f"Rejected Data Contract {contract_id!r} version {requested_version} cannot be used for Development testing.")
    row["contract_payload"] = _contract_payload(row)
    return row


def resolve_catalogue_table_id(
    config,
    env: str,
    *,
    store_type: str,
    layer: str,
    schema_name: str | None,
    table_name: str,
    spark_session=None,
) -> str:
    """Resolve one physical runtime table to its canonical Catalogue identity."""
    frame = read_lakehouse_table_core(
        CATALOGUE_TABLE, target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        spark_session=spark_session, context={"config": config, "env": env},
    )
    expected = tuple(str(value or "").strip().lower() for value in (store_type, layer, schema_name, table_name))
    matches = []
    for raw in frame.collect():
        row = _row_to_dict(raw)
        actual = tuple(str(row.get(name) or "").strip().lower() for name in ("store_type", "layer", "schema_name", "table_name"))
        if (
            str(row.get("environment_name") or "") == env
            and (str(row.get("metadata_level") or "").lower() == "table" or not row.get("column_id"))
            and row.get("is_active") is not False
            and actual == expected
        ):
            matches.append(str(row.get("table_id") or ""))
    identities = sorted(set(value for value in matches if value))
    if not identities:
        raise ValueError(
            f"No active Catalogue table matches Production runtime table {table_name!r}; "
            "profile and register the table before enforcing its Data Contract."
        )
    if len(identities) > 1:
        raise RuntimeError(f"Catalogue integrity error: Production runtime table {table_name!r} resolves to multiple table_id values.")
    return identities[0]


def resolve_catalogue_table_identity(
    config,
    env: str,
    table_id: str,
    *,
    spark_session=None,
    context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve one active registered Catalogue table by canonical table identity."""
    canonical_id = str(table_id or "").strip()
    if not canonical_id:
        raise ValueError("table_id must be a non-empty canonical FabricOps table identity.")
    frame = read_lakehouse_table_core(
        CATALOGUE_TABLE,
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        spark_session=spark_session,
        context=context or {"config": config, "env": env},
    )
    matches = []
    for raw in frame.collect():
        row = _row_to_dict(raw)
        if (
            str(row.get("environment_name") or "") == env
            and str(row.get("table_id") or "").strip() == canonical_id
            and str(row.get("metadata_level") or "").strip().lower() == "table"
            and not str(row.get("column_id") or "").strip()
            and row.get("is_active") is not False
        ):
            matches.append(row)
    if not matches:
        raise ValueError(
            f"No active registered Catalogue table exists for table_id {canonical_id!r} "
            f"in environment {env!r}."
        )
    if len(matches) != 1:
        raise RuntimeError(
            f"Catalogue integrity error: table_id {canonical_id!r} resolves to "
            f"{len(matches)} active table identities."
        )
    row = dict(matches[0])
    required = ("store_type", "layer", "table_name")
    missing = [name for name in required if not str(row.get(name) or "").strip()]
    if missing:
        raise ValueError(
            f"Catalogue table_id {canonical_id!r} is not a registered table identity; "
            f"missing {', '.join(missing)}."
        )
    store_type = str(row["store_type"]).strip().lower()
    if store_type not in {"lakehouse", "warehouse"}:
        raise ValueError(
            f"Catalogue table_id {canonical_id!r} has unsupported store_type {store_type!r}."
        )
    return {
        **row,
        "table_id": canonical_id,
        "store_type": store_type,
        "target": str(row["layer"]).strip().lower(),
        "schema": str(row.get("schema_name") or "").strip() or None,
        "table_name": str(row["table_name"]).strip(),
    }


def catalogue_authored_processing(identity: Mapping[str, Any]) -> dict[str, Any]:
    """Return current processing authoring from a Catalogue table identity."""
    strategy = str(identity.get("load_strategy") or "").strip()
    raw = identity.get("load_strategy_parameters_json") or "{}"
    try:
        parameters = json.loads(raw) if isinstance(raw, str) else dict(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("Catalogue load_strategy_parameters_json must be a JSON object.") from exc
    if not isinstance(parameters, dict):
        raise ValueError("Catalogue load_strategy_parameters_json must be a JSON object.")
    return {"load_strategy": strategy, **parameters}


def contract_guardrail_rows(contract: dict[str, Any], *, environment_name: str, metadata_table_key: str) -> list[dict[str, Any]]:
    """Adapt frozen contract Guardrails to the existing runtime rule shape."""
    payload = contract.get("contract_payload") or _contract_payload(contract)
    table = payload.get("table")
    if not isinstance(table, dict) or "columns" not in table:
        raise ValueError("Active Data Contract table.columns is missing.")
    columns = table["columns"]
    if not isinstance(columns, list):
        raise ValueError("Active Data Contract table.columns must be a list.")
    expected_schema: dict[str, str] = {}
    for index, column in enumerate(columns):
        if not isinstance(column, dict):
            raise ValueError(f"Active Data Contract table.columns[{index}] must be an object.")
        column_id = str(column.get("column_id") or "").strip()
        column_name = str(column.get("column_name") or "").strip()
        data_type = str(column.get("data_type") or "").strip()
        if not column_id or not column_name or not data_type:
            raise ValueError(
                f"Active Data Contract table.columns[{index}] must define non-blank column_id, column_name, and data_type."
            )
        if column_name in expected_schema:
            raise ValueError(f"Active Data Contract table.columns contains duplicate column_name {column_name!r}.")
        expected_schema[column_name] = data_type
    rules = payload.get("guardrails")
    if not isinstance(rules, list):
        raise ValueError("Active Data Contract guardrails must be a list.")
    adapted = []
    for raw in rules:
        if not isinstance(raw, dict):
            raise ValueError("Active Data Contract contains an invalid Guardrail definition.")
        params = raw.get("rule_parameters") or {}
        if not isinstance(params, dict):
            raise ValueError("Active Data Contract Guardrail rule_parameters must be an object.")
        if str(raw.get("guardrail_type") or "").strip().lower() == "schema":
            params = {
                **{
                    name: value for name, value in params.items()
                    if name not in {"columns", "data_types", "selected_columns", "expected_data_types"}
                },
                "columns": list(expected_schema),
                "data_types": expected_schema,
            }
        adapted.append({
            **raw,
            "metadata_table_key": metadata_table_key,
            "environment_name": environment_name,
            "rule_parameters_json": json.dumps(params, sort_keys=True),
            "is_active": True,
            "activation_state": "active",
            "review_status": "governance_approved",
            "configuration_version": int(raw.get("guardrail_version") or 1),
        })
    return adapted


def validated_processing(processing: Any) -> dict[str, Any]:
    """Return a valid frozen/current processing definition."""
    if not isinstance(processing, dict):
        raise ValueError("Data Contract processing definition is missing or malformed.")
    strategy = str(processing.get("load_strategy") or "").strip().lower()
    if strategy not in {"overwrite", "append", "scd1", "scd2"}:
        raise ValueError("Processing definition has an invalid load_strategy.")
    definition = {**processing, "load_strategy": strategy}
    allowed = {
        "overwrite": {"load_strategy", "partition_column", "source", "contract_id", "contract_version"},
        "append": {"load_strategy", "source", "contract_id", "contract_version"},
        "scd1": {"load_strategy", "key_columns", "source", "contract_id", "contract_version"},
        "scd2": {
            "load_strategy", "key_columns", "effective_column", "tracked_columns",
            "source", "contract_id", "contract_version",
        },
    }[strategy]
    unexpected = sorted(set(definition) - allowed)
    if unexpected:
        raise ValueError(f"Processing definition for {strategy} contains unsupported fields: {', '.join(unexpected)}.")
    for name in ("key_columns", "tracked_columns"):
        if name not in definition:
            continue
        values = definition[name]
        if not isinstance(values, list | tuple) or not values or any(
            not isinstance(value, str) or not value.strip() for value in values
        ):
            raise ValueError(f"Processing definition {name} must be a non-empty sequence of column names.")
        definition[name] = [value.strip() for value in values]
    if strategy in {"scd1", "scd2"} and "key_columns" not in definition:
        raise ValueError(f"Processing definition for {strategy} requires key_columns.")
    for name in ("partition_column", "effective_column"):
        if name in definition and (not isinstance(definition[name], str) or not definition[name].strip()):
            raise ValueError(f"Processing definition {name} must be a non-empty column name.")
        if name in definition:
            definition[name] = definition[name].strip()
    if strategy == "scd2" and "effective_column" not in definition:
        raise ValueError("Processing definition for scd2 requires effective_column.")
    return definition


def resolve_table_processing_definition(
    config,
    env: str,
    table_id: str,
    *,
    spark_session=None,
    context: Mapping[str, Any] | None = None,
    authored_processing: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve authored or frozen table processing through the contract-source model."""
    runtime_context = context or {}
    contract = None
    if env == "prod":
        contract = resolve_active_data_contract(config, env, table_id, spark_session=spark_session, required=True)
    else:
        overrides = runtime_context.get("data_contract_overrides") or {}
        if not isinstance(overrides, Mapping):
            raise ValueError("data_contract_overrides must be a mapping keyed by canonical table_id.")
        selected = overrides.get(table_id) or {}
        if not isinstance(selected, Mapping):
            raise ValueError(f"Development Data Contract override for {table_id!r} must be a mapping.")
        contract_id = str(selected.get("contract_id") or "").strip()
        version = selected.get("contract_version")
        if bool(contract_id) != bool(str(version or "").strip()):
            raise ValueError("Development Data Contract override requires both contract_id and contract_version.")
        if contract_id:
            contract = _resolve_data_contract_version(
                config, env, table_id, contract_id, version,
                spark_session=spark_session, context=context,
            )
    if contract is not None:
        payload = contract.get("contract_payload") or _contract_payload(contract)
        definition = validated_processing((payload.get("table") or {}).get("processing"))
        return {
            **definition,
            "source": "data_contract",
            "contract_id": contract["contract_id"],
            "contract_version": int(contract["contract_version"]),
        }
    if authored_processing is None:
        raise ValueError("Development current authoring requires an authored processing definition.")
    definition = validated_processing(dict(authored_processing))
    return {**definition, "source": "current_authoring"}


def _sql_literal(value: Any) -> str:
    """Return a Delta predicate literal for a primitive partition value."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int | float):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def resolve_scd2_tracked_columns(columns: list[str], processing: Mapping[str, Any]) -> list[str]:
    """Return explicit or default business columns used to detect SCD2 changes."""
    explicit = processing.get("tracked_columns")
    if explicit:
        invalid = sorted(
            name for name in explicit
            if name not in columns
            or name in {*processing["key_columns"], processing["effective_column"], *_TARGET_TECHNICAL_COLUMNS}
            or name.startswith(_DEFAULT_PROFILE_EXCLUDE_PREFIXES)
        )
        if invalid:
            raise ValueError(f"SCD2 tracked_columns must contain only business columns: {', '.join(invalid)}.")
        return list(explicit)
    excluded = {
        *processing["key_columns"],
        processing["effective_column"],
        *_TARGET_TECHNICAL_COLUMNS,
    }
    return [
        name for name in columns
        if name not in excluded and not name.startswith(_DEFAULT_PROFILE_EXCLUDE_PREFIXES)
    ]


def resolve_scd1_business_columns(columns: list[str], key_columns: list[str]) -> list[str]:
    """Return non-key business columns eligible for SCD change detection."""
    return [
        name for name in columns
        if name not in {*key_columns, *_TARGET_TECHNICAL_COLUMNS}
        and not name.startswith(_DEFAULT_PROFILE_EXCLUDE_PREFIXES)
    ]


def resolve_target_audit_fields(context: Mapping[str, Any] | None) -> dict[str, Any]:
    """Resolve one compact, run-consistent audit record for business target rows."""
    runtime_context = dict(context or {})
    values = build_runtime_audit_fields(
        config=runtime_context.get("config"),
        env=runtime_context.get("env"),
        runtime_context=runtime_context,
    )
    return {name: values[name] for name in _TARGET_AUDIT_COLUMNS}


def add_target_audit_fields(df, audit_fields: Mapping[str, Any]):
    """Add resolved operational audit literals to incoming target rows."""
    from pyspark.sql import functions as F

    result = df
    for name in _TARGET_AUDIT_COLUMNS:
        result = result.withColumn(name, F.lit(audit_fields[name]))
    return result


def execute_lakehouse_processing(
    df,
    *,
    table_name: str,
    target: str,
    schema: str | None,
    processing: Mapping[str, Any],
    scope: Mapping[str, Any],
    context: Mapping[str, Any] | None = None,
) -> None:
    """Apply one already-resolved governed load definition to a Lakehouse target."""
    strategy = validated_processing(dict(processing))["load_strategy"]
    read_mode = scope.get("read_mode")
    runtime_scope = scope.get("scope")
    if read_mode == "skip":
        return
    if read_mode not in {"full_dataset", "incremental_subset"} or not isinstance(runtime_scope, Mapping):
        raise ValueError("Processing scope must use skip, full_dataset, or incremental_subset.")
    values = list(runtime_scope.get("values") or [])
    if read_mode == "incremental_subset" and runtime_scope.get("type") == "partition" and not values:
        raise ValueError("Incremental partition processing requires at least one affected partition value.")

    columns = set(getattr(df, "columns", ()))
    persisted_df = df
    if not set(_TARGET_AUDIT_COLUMNS) <= columns:
        persisted_df = add_target_audit_fields(df, resolve_target_audit_fields(context))

    if strategy == "append":
        write_lakehouse_table_core(persisted_df, table_name, target=target, schema=schema, mode="append", context=context)
        return
    if strategy == "overwrite":
        if read_mode == "full_dataset":
            write_lakehouse_table_core(persisted_df, table_name, target=target, schema=schema, mode="overwrite", context=context)
            return
        partition_column = processing.get("partition_column")
        if not partition_column or partition_column != runtime_scope.get("column"):
            raise ValueError("Incremental overwrite requires matching safe target partition configuration.")
        predicate = f"`{str(partition_column).replace('`', '``')}` IN ({', '.join(_sql_literal(v) for v in values)})"
        write_lakehouse_table_core(
            persisted_df, table_name, target=target, schema=schema, mode="overwrite", context=context,
            options={"replaceWhere": predicate},
        )
        return

    from delta.tables import DeltaTable
    from pyspark.sql import functions as F

    _store, _table, _schema, path = resolve_configured_lakehouse_table(target, table_name, schema, context=context)
    keys = list(processing["key_columns"])
    duplicate = persisted_df.groupBy(*keys).count().where(F.col("count") > 1).limit(1).count()
    if duplicate:
        raise ValueError("Incoming target scope contains duplicate business keys.")
    if not DeltaTable.isDeltaTable(df.sparkSession, path):
        write_lakehouse_table_core(persisted_df, table_name, target=target, schema=schema, mode="overwrite", context=context)
        return
    delta = DeltaTable.forPath(df.sparkSession, path)
    condition = " AND ".join(f"target.`{key}` <=> source.`{key}`" for key in keys)
    if strategy == "scd1":
        business_columns = resolve_scd1_business_columns(list(df.columns), keys)
        change = " OR ".join(f"NOT (target.`{name}` <=> source.`{name}`)" for name in business_columns) or "FALSE"
        (
            delta.alias("target").merge(persisted_df.alias("source"), condition)
            .whenMatchedUpdateAll(condition=change).whenNotMatchedInsertAll().execute()
        )
        return

    effective = str(processing["effective_column"])
    tracked = resolve_scd2_tracked_columns(list(df.columns), processing)
    current_column, end_column = "_is_current", "_effective_to"
    current_rows = delta.toDF().where(F.col(current_column))
    if current_rows.groupBy(*keys).count().where(F.col("count") > 1).limit(1).count():
        raise RuntimeError("SCD2 target contains multiple current records for one or more business keys.")
    change = " OR ".join(f"NOT (target.`{name}` <=> source.`{name}`)" for name in tracked) or "FALSE"
    expire = (
        delta.alias("target").merge(persisted_df.alias("source"), condition + f" AND target.`{current_column}` = TRUE")
        .whenMatchedUpdate(condition=change, set={current_column: "false", end_column: f"source.`{effective}`"})
    )
    expire.execute()
    current = delta.toDF().where(F.col(current_column)).select(*keys, *tracked)
    incoming = persisted_df.join(current, on=keys, how="left_anti")
    if incoming.limit(1).count():
        write_lakehouse_table_core(incoming, table_name, target=target, schema=schema, mode="append", context=context)


def load_table_guardrail_rules(
    config,
    env: str,
    *,
    spark_session=None,
    table_id: str = "",
    metadata_table_key: str = "",
    context: Mapping[str, Any] | None = None,
):
    """Resolve the environment's single Guardrail rule source."""
    if env == "prod":
        if not table_id:
            raise ValueError("Production Guardrail resolution requires a canonical Catalogue table_id.")
        contract = resolve_active_data_contract(config, env, table_id, spark_session=spark_session, required=True)
        rows = contract_guardrail_rows(
            contract,
            environment_name=env,
            metadata_table_key=metadata_table_key or table_id,
        )
        return spark_session.createDataFrame(rows) if rows else []
    runtime_context = context or {}
    overrides = runtime_context.get("data_contract_overrides") or {}
    if not isinstance(overrides, Mapping):
        raise ValueError("data_contract_overrides must be a mapping keyed by canonical table_id.")
    selected_override = overrides.get(table_id) or {}
    if not isinstance(selected_override, Mapping):
        raise ValueError(f"Development Data Contract override for {table_id!r} must be a mapping.")
    contract_id = str(selected_override.get("contract_id") or "").strip()
    raw_version = selected_override.get("contract_version")
    contract_version = str(raw_version or "").strip()
    if bool(contract_id) != bool(contract_version):
        raise ValueError(
            "Development Data Contract override requires both contract_id and contract_version."
        )
    if contract_id:
        if not table_id:
            raise ValueError("Development Data Contract override requires a canonical Catalogue table_id.")
        contract = _resolve_data_contract_version(
            config, env, table_id, contract_id, contract_version,
            spark_session=spark_session, context=context,
        )
        rows = contract_guardrail_rows(
            contract,
            environment_name=env,
            metadata_table_key=metadata_table_key or table_id,
        )
        return spark_session.createDataFrame(rows) if rows else []
    try:
        return read_lakehouse_table_core(
            GUARDRAIL_TABLE, target="metadata",
            schema=configured_lakehouse_schema(config, env, "metadata"),
            spark_session=spark_session, context=context or {"config": config, "env": env},
        )
    except Exception as exc:
        if is_table_not_found_error(exc):
            raise ValueError("No guardrail rules exist; Governance must author and activate the required rule first.") from exc
        raise

def select_table_guardrail_rule(rules_df, *, guardrail_type: str, metadata_table_key: str, environment_name: str = "") -> dict | None:
    """Select the latest active approved table rule by canonical identity."""
    return _select_table_guardrail_rule(
        rules_df, guardrail_type=guardrail_type, dataset_name="", table_name="",
        environment_name=environment_name, metadata_table_key=metadata_table_key,
    )

def resolve_change_rule_observation_columns(rule: dict) -> tuple[str, str]:
    """Return validated observation columns from an active source-change rule."""
    parameters = _parse_rule_parameters(rule)
    resolved = []
    for name in ("partition_column", "change_column"):
        value = str(parameters.get(name) or "").strip()
        if not value:
            raise ValueError(f"Active source-change rule is invalid: {name} is missing.")
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
            raise ValueError(f"Active source-change rule is invalid: {name} must be a simple identifier.")
        resolved.append(value)
    return resolved[0], resolved[1]

def evaluate_changes_guardrail(
    result: dict,
    *,
    rules_df,
    dataset_name: str = "",
    table_name: str = "",
    environment_name: str = "",
    metadata_table_key: str = "",
) -> dict:
    """Apply approved change intent to an observation comparison result."""
    rule = _select_table_guardrail_rule(
        rules_df, guardrail_type="change", dataset_name=dataset_name,
        table_name=table_name, environment_name=environment_name,
        metadata_table_key=metadata_table_key,
    )
    if not rule:
        raise ValueError(
            f"No active approved source-change rule exists for {metadata_table_key!r}; "
            "Governance must author and activate one first."
        )
    params = _parse_rule_parameters(rule)
    behaviour = _string_value(params.get("change_behaviour"))
    if behaviour:
        rule_type, source_pattern = resolve_guardrail_change_behaviour(behaviour)
    else:
        rule_type = _string_value(params.get("expected_change") or _catalogue_value(rule, "rule_type") or "monitor_only").lower()
        source_pattern = _string_value(params.get("source_pattern") or result.get("source_pattern") or "snapshot").lower()
    severity = _string_value(_catalogue_value(rule, "severity") or "blocking").lower()
    if severity not in {"blocking", "warning"}:
        raise ValueError("severity must be one of: blocking, warning")
    result.update({
        "rule_type": rule_type,
        "source_pattern": source_pattern,
        "severity": severity,
        "rule_key": _string_value(_catalogue_value(rule, "rule_key", "rule_id")),
        "guardrail_rule_id": _string_value(_catalogue_value(rule, "guardrail_rule_id", "rule_id")),
        "guardrail_version": int(_catalogue_value(rule, "guardrail_version", "configuration_version") or 1),
        "rule_id": _string_value(_catalogue_value(rule, "rule_id")),
    })
    if rule_type not in {"change_required", "no_change_required", "monitor_only"}:
        raise ValueError("expected_change must be one of: change_required, no_change_required, monitor_only")
    changed = bool(result.get("changed"))
    result["expected"] = {"expected_change": rule_type}
    result["actual"] = {
        "changed": changed,
        **{name: result.get(name, []) for name in ("new_partitions", "changed_partitions", "removed_partitions", "reappeared_partitions")},
    }
    if result.get("first_observation"):
        result.update(
            status="baseline_created",
            can_continue=True,
            changed=False,
            reason="First observation baseline created; change intent was not evaluated.",
        )
        result["actual"]["changed"] = None
        result["message"] = result["reason"]
        return _apply_bypass_post_review_warning(result, rule)
    append_violation = source_pattern == "incremental_append" and int(result.get("append_violation_count") or 0) > 0
    passed = not append_violation and (rule_type == "monitor_only" or (rule_type == "change_required" and changed) or (rule_type == "no_change_required" and not changed))
    if passed:
        result.update(status="passed", can_continue=True, reason=f"Source change expectation {rule_type!r} satisfied.")
    else:
        blocking = severity == "blocking"
        result.update(status="failed" if blocking else "warning", can_continue=not blocking, reason=f"Source change expectation {rule_type!r} was not satisfied.")
    result["message"] = result["reason"]
    return _apply_bypass_post_review_warning(result, rule)

def resolve_guardrail_change_behaviour(change_behaviour: str) -> tuple[str, str]:
    """Translate one widget change behaviour into canonical runtime concepts."""
    try:
        return _GUARDRAIL_CHANGE_BEHAVIOUR_MAPPING[str(change_behaviour)]
    except KeyError as exc:
        raise ValueError(f"change_behaviour must be one of: {', '.join(GUARDRAIL_CHANGE_BEHAVIOURS)}") from exc

def _apply_bypass_post_review_warning(result: dict, rule: dict | None) -> dict:
    if rule and _rule_review_status(rule) == "active_pending_governance_review":
        reason = str(result.get("reason") or result.get("message") or "")
        message = _BYPASS_POST_REVIEW_WARNING if not reason else f"{reason} {_BYPASS_POST_REVIEW_WARNING}"
        result["reason"] = message
        result["message"] = message
        result["bypass_warning"] = _BYPASS_POST_REVIEW_WARNING
    return result

class SchemaDriftError(Exception):
    """Raised when a guardrail check is configured to stop execution.

    Notes
    -----
    This exception is shared by schema-check workflows so notebook callers
    have one failure type to catch when they choose fail-fast behavior.

    """

def _normalize_datatype(data_type) -> str:
    raw = str(data_type).strip().lower()
    raw = re.sub(r"\s+", "", raw)

    decimal_match = re.search(r"decimaltype\((\d+),(\d+)\)|decimal\((\d+),(\d+)\)", raw)
    if decimal_match:
        precision = decimal_match.group(1) or decimal_match.group(3)
        scale = decimal_match.group(2) or decimal_match.group(4)
        return f"decimal({precision},{scale})"

    aliases = {
        "integertype()": "int",
        "integertype": "int",
        "integer": "int",
        "int32": "int",
        "int": "int",
        "longtype()": "bigint",
        "longtype": "bigint",
        "long": "bigint",
        "int64": "bigint",
        "bigint": "bigint",
        "stringtype()": "string",
        "stringtype": "string",
        "str": "string",
        "object": "string",
        "string": "string",
        "datetype()": "date",
        "datetype": "date",
        "date": "date",
        "timestamptype()": "timestamp",
        "timestamptype": "timestamp",
        "timestamp": "timestamp",
        "datetime64[ns]": "timestamp",
        "doubletype()": "double",
        "doubletype": "double",
        "double": "double",
        "float64": "double",
        "floattype()": "float",
        "floattype": "float",
        "float32": "float",
        "float": "float",
        "booleantype()": "boolean",
        "booleantype": "boolean",
        "bool": "boolean",
        "boolean": "boolean",
    }
    return aliases.get(raw, raw)

def _actual_schema(df) -> tuple[list[str], dict[str, str]]:
    schema = getattr(df, "schema", None)
    if schema is not None and hasattr(schema, "fields"):
        columns = [str(field.name) for field in schema.fields]
        types = {str(field.name): _normalize_datatype(getattr(field, "dataType", "")) for field in schema.fields}
        return columns, types

    dtypes = getattr(df, "dtypes", None)
    if dtypes is not None:
        dtype_items = dtypes.items() if hasattr(dtypes, "items") else dtypes
        types = {str(name): _normalize_datatype(dtype) for name, dtype in dtype_items}
        columns = [str(column) for column in getattr(df, "columns", list(types))]
        return columns, types

    columns = [str(column) for column in getattr(df, "columns", [])]
    return columns, {}







_SCHEMA_PRESETS = {"strict", "allow_new_columns", "monitor_only"}

def _guardrail_schema_check_base(
    dataframe,
    expected_schema: dict[str, str] | None = None,
    *,
    preset: str = "strict",
    rules_df=None,
    dataset_name: str = "",
    table_name: str = "",
    environment_name: str = "",
    metadata_table_key: str = "",
) -> dict:
    """Apply an internal runtime schema check for the governed runtime checks.

    This helper is not a notebook-facing callable. It preserves runtime schema
    enforcement for widget-led guardrail flows without exposing a public schema
    validation API.

    Parameters
    ----------
    dataframe : Any
        Spark, pandas, or dataframe-like object with schema metadata.
    expected_schema : dict[str, str]
        Mapping of required column names to expected datatype strings.
    preset : {"strict", "allow_new_columns", "monitor_only"}, default="strict"
        Schema validation intent. ``strict`` blocks missing columns, datatype
        changes, and unexpected columns. ``allow_new_columns`` blocks missing
        columns and datatype changes while reporting additional columns as a
        warning. ``monitor_only`` reports all differences without blocking.
    rules_df : DataFrame or iterable of mappings, optional
        Approved schema rules used instead of ``expected_schema``.
    dataset_name : str, optional
        Dataset identity used to select an approved rule.
    table_name : str, optional
        Table identity used to select an approved rule.
    environment_name : str, optional
        Environment identity used to select an approved rule.
    metadata_table_key : str, optional
        Canonical table identity used to select an approved rule.

    Returns
    -------
    dict
        Standard guardrail result with ``status``, ``can_continue``,
        ``checks``, and ``message`` plus detailed schema difference fields.

    Raises
    ------
    ValueError
        If ``preset`` is not one of the supported schema presets.

    Notes
    -----
    This private helper is called by the governed runtime checks only. Notebook
    authors should use widget-authored rules and the guardrail gate instead of
    calling schema validation helpers directly.

    """
    rule = None
    rule_type = ""
    severity = "blocking"
    if rules_df is None and expected_schema is not None and not isinstance(expected_schema, dict):
        rules_df, expected_schema = expected_schema, None
    if rules_df is not None:
        rule = _select_table_guardrail_rule(rules_df, guardrail_type="schema", dataset_name=dataset_name, table_name=table_name, environment_name=environment_name, metadata_table_key=metadata_table_key)
        if not rule:
            expected_schema, preset = {}, "monitor_only"
        else:
            params = _parse_rule_parameters(rule)
            expected = params.get("data_types") or params.get("expected_data_types") or {}
            selected_columns = params.get("columns") or params.get("selected_columns") or list(expected)
            expected_schema = {column: expected.get(column, "") for column in selected_columns}
            rule_type = _string_value(_catalogue_value(rule, "rule_type") or "relaxed").lower()
            preset = {"strict": "strict", "minimum_required": "allow_new_columns", "relaxed": "allow_new_columns", "skip": "monitor_only"}.get(rule_type, "allow_new_columns")
            severity = _string_value(_catalogue_value(rule, "severity") or "blocking").lower()
    elif expected_schema is None:
        raise ValueError("expected_schema is required when rules_df is not supplied")

    normalized_preset = str(preset).lower()
    if normalized_preset not in _SCHEMA_PRESETS:
        raise ValueError("preset must be one of: strict, allow_new_columns, monitor_only")
    if severity not in {"blocking", "warning"}:
        raise ValueError("severity must be one of: blocking, warning")

    actual_columns, actual_types = _actual_schema(dataframe)
    actual_set = set(actual_columns)
    expected_names = [str(column) for column in expected_schema]
    expected_set = set(expected_names)

    missing_columns = [column for column in expected_names if column not in actual_set]
    datatype_mismatches = []
    for column, expected_type in expected_schema.items():
        column_name = str(column)
        if column_name in actual_set and column_name in actual_types:
            expected = _normalize_datatype(expected_type)
            actual = actual_types[column_name]
            if actual != expected:
                datatype_mismatches.append({"column": column_name, "expected": expected, "actual": actual})

    checks = []
    for column in missing_columns:
        checks.append({"check": "missing_column", "column": column, "status": "failed", "passed": False})
    for mismatch in datatype_mismatches:
        checks.append({"check": "datatype_mismatch", **mismatch, "status": "failed", "passed": False})
    actual_unexpected = [column for column in actual_columns if str(column) not in expected_set]
    for column in actual_unexpected:
        checks.append({"check": "unexpected_column", "column": column, "status": "warning" if normalized_preset == "allow_new_columns" else "failed", "passed": normalized_preset == "allow_new_columns"})

    blocking = bool(missing_columns or datatype_mismatches)
    if normalized_preset == "strict":
        blocking = blocking or bool(actual_unexpected)
    if normalized_preset == "monitor_only":
        status = "warning" if checks else "passed"
        can_continue = True
    elif blocking:
        status = "failed"
        can_continue = False
    elif normalized_preset == "allow_new_columns" and actual_unexpected:
        status = "warning"
        can_continue = True
    else:
        status = "passed"
        can_continue = True
    if status == "failed" and severity == "warning":
        status = "warning"
        can_continue = True

    message = (
        "Schema validation passed."
        if status == "passed"
        else f"Schema validation {status}: {len(missing_columns)} missing, {len(actual_unexpected)} unexpected, {len(datatype_mismatches)} datatype mismatch(es)."
    )
    result = {
        "status": status,
        "can_continue": can_continue,
        "checks": checks,
        "message": message,
        "missing_columns": missing_columns,
        "unexpected_columns": actual_unexpected,
        "datatype_mismatches": datatype_mismatches,
        "preset": normalized_preset,
        "severity": severity,
    }
    if rule is not None:
        result.update({"guardrail_type": "schema", "rule_type": rule_type, "rule_key": _string_value(_catalogue_value(rule, "rule_key", "rule_id"))})
        return _apply_bypass_post_review_warning(result, rule)
    return result

def _row_to_dict(row) -> dict:
    if row is None:
        return {}
    if isinstance(row, dict):
        return dict(row)
    if hasattr(row, "asDict"):
        return row.asDict(recursive=True)
    return {name: getattr(row, name) for name in dir(row) if not name.startswith("_")}



def _max_column_value(dataframe, column_name: str):
    if dataframe is None or not column_name:
        return None
    if hasattr(dataframe, "agg"):
        from pyspark.sql import functions as F

        rows = dataframe.agg(F.max(F.col(column_name)).alias("latest_value")).collect()
        if not rows:
            return None
        row = rows[0]
        if isinstance(row, dict):
            return row.get("latest_value")
        if hasattr(row, "asDict"):
            return row.asDict().get("latest_value")
        try:
            return row["latest_value"]
        except Exception:
            return getattr(row, "latest_value", None)
    if isinstance(dataframe, dict):
        values = [dataframe.get(column_name)]
    else:
        values = []
        for row in dataframe or []:
            if isinstance(row, dict):
                values.append(row.get(column_name))
            elif hasattr(row, "asDict"):
                values.append(row.asDict().get(column_name))
            else:
                values.append(getattr(row, column_name, None))
    values = [value for value in values if value not in (None, "")]
    return max(values) if values else None

def _coerce_date(value) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None

def _coerce_datetime(value) -> datetime | None:
    """Return a timezone-naive comparison datetime for freshness values."""
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=None) if value.tzinfo else value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    try:
        parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
        return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed
    except ValueError:
        return None

def _iso_date_value(value) -> str:
    parsed = _coerce_date(value)
    return parsed.isoformat() if parsed is not None else ("" if value is None else str(value))

def freshness_check_core(
    dataframe,
    freshness_column: str | None = None,
    max_lag_days: int | str | None = None,
    severity: str = "blocking",
    *,
    reference_date: date | datetime | str | None = None,
    rules_df=None,
    dataset_name: str = "",
    table_name: str = "",
    environment_name: str = "",
    metadata_table_key: str = "",
) -> dict:
    """Enforce that a DataFrame contains recent enough data.

    Parameters
    ----------
    dataframe : Any
        Spark DataFrame or iterable of row-like mappings to check.
    freshness_column : str or None
        Column whose maximum value represents the latest available data date.
        When omitted, the freshness guardrail is skipped.
    max_lag_days : int or str or None
        Maximum allowed lag, in days, between ``reference_date`` and the latest
        value in ``freshness_column``. Required when ``freshness_column`` is set.
    severity : {"blocking", "warning"}, default="blocking"
        Whether stale data blocks continuation or returns a non-blocking warning.
    reference_date : date, datetime, str, optional
        Date used as "today" for comparison. Defaults to the current local date.
    rules_df : DataFrame or iterable of mappings, optional
        Approved freshness rules used instead of direct arguments.
    dataset_name : str, optional
        Dataset identity used to select an approved rule.
    table_name : str, optional
        Table identity used to select an approved rule.
    environment_name : str, optional
        Environment identity used to select an approved rule.
    metadata_table_key : str, optional
        Canonical table identity used to select an approved rule.

    Returns
    -------
    dict
        Standard guardrail result with ``status``, ``can_continue``,
        ``check_type``, latest value, required minimum value, and message.

    """
    rule = None
    rule_type = ""
    max_age_seconds = None
    if rules_df is None and freshness_column is not None and not isinstance(freshness_column, str):
        rules_df, freshness_column = freshness_column, None
    if rules_df is not None:
        rule = _select_table_guardrail_rule(rules_df, guardrail_type="freshness", dataset_name=dataset_name, table_name=table_name, environment_name=environment_name, metadata_table_key=metadata_table_key)
        if rule:
            params = _parse_rule_parameters(rule)
            rule_type = _string_value(_catalogue_value(rule, "rule_type") or "max_lag_days").lower()
            if rule_type != "skip":
                freshness_column = params.get("freshness_column") or params.get("column_name") or _catalogue_value(rule, "column_name")
                if params.get("maximum_age") not in (None, ""):
                    unit = str(params.get("maximum_age_unit") or "days").lower()
                    factors = {"minutes": 60, "hours": 3600, "days": 86400}
                    if unit not in factors:
                        raise ValueError("maximum_age_unit must be minutes, hours, or days")
                    max_age_seconds = float(params["maximum_age"]) * factors[unit]
                else:
                    max_lag_days = params.get("max_lag_days")
                    max_age_seconds = None
                severity = _catalogue_value(rule, "severity") or "blocking"

    dataframe_columns = set(getattr(dataframe, "columns", ()))
    if not dataframe_columns and isinstance(dataframe, (list, tuple)) and dataframe:
        dataframe_columns = set(_row_to_dict(dataframe[0]))
    observation_evidence = {"metadata_table_key", "partition_value", "change_column", "max_change_value", "_committed_at"} <= dataframe_columns
    if observation_evidence and rule_type != "skip":
        rows = dataframe.collect() if hasattr(dataframe, "collect") else dataframe
        change_columns = {_string_value(_catalogue_value(_row_to_dict(row), "change_column")) for row in rows or []}
        change_columns.discard("")
        if len(change_columns) != 1:
            raise ValueError("Observation evidence must contain one authoritative change_column.")
        observation_change_column = next(iter(change_columns))
        configured_freshness_column = str(freshness_column or "").strip()
        if configured_freshness_column and configured_freshness_column != observation_change_column:
            raise ValueError(
                "Active freshness rule is invalid for observation evidence: "
                f"freshness_column {configured_freshness_column!r} does not match change_column {observation_change_column!r}."
            )
        freshness_column = "max_change_value"
    column = str(freshness_column or "").strip()
    normalized_severity = str(severity or "blocking").lower().strip()
    if normalized_severity not in {"blocking", "warning"}:
        raise ValueError("severity must be one of: blocking, warning")

    base_result = {
        "status": "skipped",
        "can_continue": True,
        "check_type": "freshness",
        "freshness_column": column,
        "freshness_max_lag_days": "" if max_lag_days in (None, "") else max_lag_days,
        "freshness_severity": normalized_severity,
        "latest_value": "",
        "required_min_value": "",
        "freshness_status": "skipped",
        "freshness_can_continue": True,
        "freshness_message": "Freshness check skipped because no freshness column is configured.",
        "message": "Freshness check skipped because no freshness column is configured.",
    }
    if rule is not None:
        base_result.update({
            "guardrail_type": "freshness",
            "rule_type": rule_type,
            "rule_key": _string_value(_catalogue_value(rule, "rule_key", "rule_id")),
            "guardrail_rule_id": _string_value(_catalogue_value(rule, "guardrail_rule_id", "rule_id")),
            "guardrail_version": int(_catalogue_value(rule, "guardrail_version", "configuration_version") or 1),
            "rule_id": _string_value(_catalogue_value(rule, "rule_id")),
        })
    if not column:
        return _apply_bypass_post_review_warning(base_result, rule)
    if max_age_seconds is None and (max_lag_days is None or str(max_lag_days).strip() == ""):
        raise ValueError("max_lag_days is required when freshness_column is set")
    lag_days = int(max_lag_days or 0)
    if lag_days < 0:
        raise ValueError("max_lag_days must be greater than or equal to zero")
    base_result["freshness_max_lag_days"] = lag_days

    reference = _coerce_datetime(reference_date) if reference_date is not None else datetime.now()
    if reference is None:
        raise ValueError("reference_date must be a date, datetime, or ISO date string")
    required_min = reference - timedelta(seconds=max_age_seconds) if max_age_seconds is not None else reference - timedelta(days=lag_days)
    latest_raw = _max_column_value(dataframe, column)
    latest_date = _coerce_datetime(latest_raw)
    latest_display = _coerce_datetime(latest_raw).isoformat() if max_age_seconds is not None and _coerce_datetime(latest_raw) else _iso_date_value(latest_raw)
    required_display = required_min.isoformat() if max_age_seconds is not None else required_min.date().isoformat()
    base_result.update(latest_value=latest_display, required_min_value=required_display)

    if latest_date is not None and latest_date >= required_min:
        message = "Freshness check passed."
        base_result.update(
            status="passed",
            can_continue=True,
            freshness_status="passed",
            freshness_can_continue=True,
            freshness_message=message,
            message=message,
        )
        return _apply_bypass_post_review_warning(base_result, rule)

    message = f"Freshness check failed: latest {column} is older than allowed lag."
    status = "failed" if normalized_severity == "blocking" else "warning"
    can_continue = normalized_severity == "warning"
    base_result.update(
        status=status,
        can_continue=can_continue,
        freshness_status=status,
        freshness_can_continue=can_continue,
        freshness_message=message,
        message=message,
    )
    return _apply_bypass_post_review_warning(base_result, rule)


def _catalogue_value(row: dict, *names: str):
    for name in names:
        if name in row:
            return row.get(name)
        upper = name.upper()
        if upper in row:
            return row.get(upper)
        lower = name.lower()
        for key, value in row.items():
            if str(key).lower() == lower:
                return value
    return None

def _string_value(value) -> str:
    return "" if value is None else str(value)



def stop_if_failed(result) -> None:
    """Stop notebook execution when a guardrail result is blocking.

    Parameters
    ----------
    result : dict
        Direct schema, freshness, profile behavior, or DQ guardrail result.

    Raises
    ------
    SchemaDriftError
        If the resolved result has ``can_continue=False``.

    """
    resolved = (result or {}).get("result") if isinstance(result, dict) and "result" in result else result
    resolved = resolved or {}
    if bool(resolved.get("can_continue", True)):
        return
    status = resolved.get("status", "failed")
    detail = resolved.get("message") or resolved.get("summary") or "Guardrail blocked execution."
    raise SchemaDriftError(f"Guardrail blocked execution with status: {status}. {detail}")

def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]:
    if rows_or_df is None:
        return []
    if hasattr(rows_or_df, "collect"):
        rows_or_df = rows_or_df.collect()
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows_or_df]

def _canonical_dq_rule_type(rule_type: Any) -> str:
    return str(rule_type or "").strip()

def _normalize_dq_severity(severity: Any) -> str:
    """Normalize guardrail/DQ severity labels for DQ validation."""
    value = str(severity or "warning").strip().lower()
    return "error" if value in {"blocking", "error"} else "warning"

def _spark_sql_helpers():
    """Return Spark SQL helper modules lazily for DQ runtime helpers."""
    try:
        from pyspark.sql import SparkSession, functions as F
        from pyspark.sql.window import Window
    except Exception as exc:  # pragma: no cover - Fabric/runtime dependency guard
        raise RuntimeError("DQ enforcement helpers require pyspark in the active runtime.") from exc
    return SparkSession, F, Window

def _validate_dq_rules(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate canonical DQ rules before loading or enforcement."""
    if not isinstance(rules, list):
        raise ValueError("DQ rules must be a list of dictionaries.")

    optional_common = {"severity", "description", "rule_id", "is_active", "review_status"}
    del optional_common  # Documents intentionally accepted fields for callers and tests.

    def require_columns(rule: dict[str, Any], count: int | None = None, *, minimum: int | None = None) -> list[str]:
        cols = rule.get("columns")
        if isinstance(cols, str):
            cols = [c.strip() for c in cols.split(",") if c.strip()]
            rule["columns"] = cols
        if not isinstance(cols, list) or not cols or not all(str(c).strip() for c in cols):
            raise ValueError(f"DQ rule '{rule.get('rule_id', '?')}' columns must be a non-empty list.")
        cols = [str(c).strip() for c in cols]
        rule["columns"] = cols
        if count is not None and len(cols) != count:
            raise ValueError(f"DQ rule '{rule.get('rule_id', '?')}' requires exactly {count} column(s).")
        if minimum is not None and len(cols) < minimum:
            raise ValueError(f"DQ rule '{rule.get('rule_id', '?')}' requires at least {minimum} column(s).")
        return cols

    for i, rule in enumerate(rules):
        if not isinstance(rule, dict):
            raise ValueError(f"DQ rule at index {i} must be a dictionary.")
        rule.setdefault("rule_id", f"dq_rule_{i + 1}")
        rule.setdefault("severity", "warning")
        rule["severity"] = _normalize_dq_severity(rule.get("severity"))
        rule.setdefault("description", "")
        rule["rule_type"] = _canonical_dq_rule_type(rule.get("rule_type"))
        rtype = rule["rule_type"]
        if rtype not in DQ_RULE_TYPES:
            raise ValueError(f"DQ rule '{rule['rule_id']}' has unsupported rule_type '{rtype}'.")

        if rtype in {"blank_text", "required_when"}:
            require_columns(rule, minimum=1)
        elif rtype in {
            "missing_values", "unique_values", "allowed_values", "blocked_values", "value_range", "text_pattern", "conditional_value",
        }:
            require_columns(rule, count=1)
        elif rtype == "unique_combination":
            require_columns(rule, minimum=2)
        elif rtype == "compare_columns":
            require_columns(rule, count=2)

        if rtype == "missing_values":
            if rule.get("maximum_null_percent") is None:
                raise ValueError(f"DQ rule '{rule['rule_id']}' requires maximum_null_percent.")
            threshold = float(rule["maximum_null_percent"])
            if not 0 <= threshold <= 100:
                raise ValueError(f"DQ rule '{rule['rule_id']}' maximum_null_percent must be between 0 and 100.")
            rule["maximum_null_percent"] = threshold
        if rtype == "allowed_values" and "allowed_values" not in rule:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires allowed_values.")
        if rtype == "blocked_values" and "blocked_values" not in rule:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires blocked_values.")
        if rtype == "value_range":
            if rule.get("minimum") is None and rule.get("maximum") is None:
                raise ValueError(f"DQ rule '{rule['rule_id']}' requires minimum or maximum.")
            rule["minimum_inclusive"] = bool(rule.get("minimum_inclusive", True))
            rule["maximum_inclusive"] = bool(rule.get("maximum_inclusive", True))
        if rtype == "text_pattern" and not str(rule.get("pattern") or ""):
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires pattern.")
        if rtype in {"required_when", "conditional_value"}:
            if not str(rule.get("condition_column") or "").strip():
                raise ValueError(f"DQ rule '{rule['rule_id']}' requires condition_column.")
            if str(rule.get("condition_operator") or "") not in DQ_COMPARISON_OPERATORS:
                raise ValueError(f"DQ rule '{rule['rule_id']}' has unsupported condition_operator.")
            if "condition_value" not in rule:
                raise ValueError(f"DQ rule '{rule['rule_id']}' requires condition_value.")
        if rtype == "conditional_value":
            if "expected_value" not in rule:
                raise ValueError(f"DQ rule '{rule['rule_id']}' requires expected_value.")
        if rtype == "compare_columns":
            if rule["columns"][0] == rule["columns"][1]:
                raise ValueError(f"DQ rule '{rule['rule_id']}' requires two different columns.")
            if str(rule.get("operator") or "") not in DQ_COMPARISON_OPERATORS:
                raise ValueError(f"DQ rule '{rule['rule_id']}' has unsupported operator.")
    return rules

def _load_active_dq_rules(metadata_df, metadata_table_key: str, env: str | None = None, dataset_name: str | None = None) -> list[dict[str, Any]]:
    """Load active DQ guardrail rules from append-only metadata rows."""
    _, F, Window = _spark_sql_helpers()
    columns = set(getattr(metadata_df, "columns", []))
    if "rule_key" in columns:
        partition_columns = ["rule_key"]
    elif "rule_id" in columns:
        partition_columns = ["rule_id"]
    else:
        partition_columns = [name for name in ("metadata_table_key", "column_name", "rule_type") if name in columns]
    if not partition_columns:
        raise ValueError("DQ metadata must include rule_key or rule identity columns.")
    if "metadata_table_key" not in columns:
        raise ValueError("DQ metadata must include metadata_table_key for canonical table scoping.")
    latest = metadata_df.filter(F.col("metadata_table_key") == metadata_table_key)
    if "guardrail_type" in columns:
        latest = latest.filter(F.lower(F.col("guardrail_type")).isin("dq", "quality"))
    if env is not None and "environment_name" in columns:
        latest = latest.filter(F.col("environment_name") == env)
    if dataset_name is not None and "dataset_name" in columns:
        latest = latest.filter(F.col("dataset_name") == dataset_name)
    order_columns = [name for name in ("_committed_at", "approved_at") if name in columns]
    if order_columns:
        window = Window.partitionBy(*[F.col(name) for name in partition_columns]).orderBy(
            *[F.col(name).desc_nulls_last() for name in order_columns]
        )
        latest = latest.withColumn("_rn", F.row_number().over(window)).filter(F.col("_rn") == 1).drop("_rn")
    if "activation_state" in columns:
        latest = latest.filter(F.lower(F.coalesce(F.col("activation_state"), F.lit(""))) == "active")
    elif "is_active" in columns:
        latest = latest.filter(F.col("is_active") == True)
    else:
        return []
    if "action_type" in columns:
        latest = latest.filter(F.lower(F.coalesce(F.col("action_type"), F.lit("created"))) != "deactivated")
    if "review_state" in columns and "review_status" in columns:
        review_expr = F.coalesce(F.col("review_state"), F.col("review_status"))
    elif "review_state" in columns:
        review_expr = F.col("review_state")
    elif "review_status" in columns:
        review_expr = F.col("review_status")
    else:
        return []
    latest = latest.filter(F.lower(F.coalesce(review_expr, F.lit(""))).isin("self_approved", "governance_approved", "active_pending_governance_review"))

    rules: list[dict[str, Any]] = []
    for row in _coerce_rows(latest.collect()):
        params_raw = row.get("rule_parameters_json") or "{}"
        try:
            params = json.loads(params_raw) if isinstance(params_raw, str) else dict(params_raw)
        except Exception:
            params = {}
        columns_value = params.get("columns") or row.get("columns") or row.get("column_name")
        if isinstance(columns_value, str):
            rule_columns = [c.strip() for c in columns_value.split(",") if c.strip()]
        else:
            rule_columns = list(columns_value or [])
        params = {k: v for k, v in params.items() if k != "columns"}
        rules.append(
            {
                "rule_id": str(row.get("rule_id") or ""),
                "guardrail_rule_id": str(row.get("guardrail_rule_id") or row.get("rule_id") or ""),
                "guardrail_version": int(row.get("guardrail_version") or row.get("configuration_version") or 1),
                "rule_key": str(row.get("rule_key") or row.get("rule_id") or ""),
                "rule_type": _canonical_dq_rule_type(row.get("rule_type")),
                "columns": rule_columns,
                "severity": _normalize_dq_severity(row.get("severity")),
                "description": str(row.get("description") or ""),
                "review_status": str(row.get("review_status") or ""),
                **params,
            }
        )
    return _validate_dq_rules(rules)

def check_dq_runtime(
    dataframe,
    config,
    env: str,
    table_name: str,
    *,
    table_id: str,
    target: str,
    store_type: str,
    schema_name: str | None,
    dataset_name: str = "",
    run_id: str = "",
    row_identity_columns: list[str] | None = None,
    context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate governed DQ rules and persist rule summaries and failed-row evidence."""
    spark_session = getattr(dataframe, "sparkSession", None)
    if spark_session is None or not hasattr(spark_session, "createDataFrame"):
        raise RuntimeError("check_dq requires a Spark DataFrame in the active Microsoft Fabric runtime.")
    source_columns = list(getattr(dataframe, "columns", []))
    identities = list(row_identity_columns or [])
    if not identities:
        identities = [name for name in ("row_uuid", "_row_uuid", "row_id") if name in source_columns][:1]
    missing_identities = [name for name in identities if name not in source_columns]
    if missing_identities:
        raise ValueError(f"row_identity_columns not found in dataframe: {', '.join(missing_identities)}")
    metadata_table_key = table_id
    metadata_df = load_table_guardrail_rules(
        config, env, spark_session=spark_session, table_id=table_id,
        metadata_table_key=metadata_table_key, context=context,
    )
    rules = (
        []
        if isinstance(metadata_df, list) and not metadata_df
        else _load_active_dq_rules(metadata_df, metadata_table_key, env=env, dataset_name=dataset_name or None)
    )
    checks = _run_dq_guardrail_checks(dataframe, table_name, rules) if rules else []
    result = _summarize_dq_guardrail(checks)
    result["dataframe"] = _dq_tagged_dataframe(dataframe, rules)
    total_count = int(dataframe.count())
    failed_rule_count = sum(not check["passed"] for check in checks)
    failed_row_count = 0
    if rules:
        _, F, _ = _spark_sql_helpers()
        any_failure = F.lit(False)
        for rule in rules:
            any_failure = any_failure | _dq_failed_expression(dataframe, rule)
        failed_row_count = int(dataframe.filter(any_failure).count())
    result["summary"] = {
        "DQ_STATUS": result["status"],
        "DQ_RULE_COUNT": len(checks),
        "DQ_FAILED_RULE_COUNT": failed_rule_count,
        "DQ_WARNING_RULE_COUNT": sum(check["status"] == "warning" for check in checks),
        "DQ_ERROR_RULE_COUNT": sum(check["status"] == "failed" for check in checks),
        "DQ_FAILED_ROW_COUNT": failed_row_count,
        "DQ_FAILED_ROW_PERCENT": float(round((failed_row_count / total_count) * 100, 4)) if total_count else 0.0,
        "DQ_CHECKED_AT": get_current_audit_timestamp(config=config, drop_microseconds=False),
    }
    if not rules:
        return result

    audit = build_runtime_audit_fields(config=config, env=env)
    resolved_run_id = str(run_id or "").strip() or str(audit["_activity_id"]).strip()
    result["run_id"] = resolved_run_id
    check_by_id = {check["rule_id"]: check for check in checks}
    result_ids = {rule["rule_id"]: str(uuid4()) for rule in rules}
    summary_rows = []
    for rule in rules:
        check = check_by_id[rule["rule_id"]]
        summary_rows.append({
            "guardrail_result_id": result_ids[rule["rule_id"]],
            "guardrail_rule_id": rule["guardrail_rule_id"],
            "guardrail_version": rule["guardrail_version"],
            "result_id": str(uuid4()),
            "run_id": resolved_run_id,
            "rule_key": rule["rule_key"],
            "metadata_table_key": metadata_table_key,
            "environment_name": env,
            "dataset_name": dataset_name,
            "table_name": table_name,
            "column_name": ",".join(rule["columns"]),
            "guardrail_type": "dq",
            "rule_type": rule["rule_type"],
            "status": check["status"],
            "can_continue": check["status"] != "failed",
            "severity": rule["severity"],
            "reason": "Rule passed." if check["passed"] else f"{check['failed_count']} row(s) failed {rule['rule_type']}.",
            "expected_value_json": json.dumps({key: value for key, value in rule.items() if key not in {"description", "guardrail_rule_id", "rule_id", "rule_key", "severity"}}, default=str, sort_keys=True),
            "actual_value_json": json.dumps({"failed_count": check["failed_count"], "failed_percent": check["failed_percent"], "total_count": check["total_count"]}, sort_keys=True),
            "result_payload_json": json.dumps(check, default=str, sort_keys=True),
            **audit,
        })
    context = {"config": config, "env": env}
    write_lakehouse_table_core(
        spark_session.createDataFrame([coerce_metadata_row_types("METADATA_GUARDRAIL_RESULTS", row) for row in summary_rows]),
        "METADATA_GUARDRAIL_RESULTS", target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"), context=context, mode="append",
    )

    _, F, _ = _spark_sql_helpers()
    if identities:
        row_identity = F.to_json(
            F.struct(*[F.col(name).alias(name) for name in identities]),
            {"ignoreNullFields": "false"},
        )
    else:
        canonical_row = F.to_json(
            F.struct(*[F.col(name).alias(name) for name in sorted(source_columns)]),
            {"ignoreNullFields": "false"},
        )
        row_identity = F.sha2(canonical_row, 256)
    evidence_frames = []
    for rule in rules:
        involved = list(dict.fromkeys([*rule["columns"], str(rule.get("condition_column") or "")]))
        involved = [name for name in involved if name and name in source_columns]
        details = {key: value for key, value in rule.items() if key not in {"description", "guardrail_rule_id", "rule_id", "rule_key", "severity"}}
        evidence_frames.append(dataframe.filter(_dq_failed_expression(dataframe, rule)).select(
            F.expr("uuid()").alias("guardrail_row_result_id"),
            F.lit(result_ids[rule["rule_id"]]).alias("guardrail_result_id"),
            F.lit(rule["guardrail_rule_id"]).alias("guardrail_rule_id"),
            F.lit(metadata_table_key).alias("metadata_table_key"), F.lit(env).alias("environment_name"),
            F.lit(dataset_name).alias("dataset_name"), F.lit(table_name).alias("table_name"),
            row_identity.alias("row_identity"), F.lit(rule["rule_type"]).alias("rule_type"),
            F.lit(json.dumps(involved)).alias("involved_columns_json"),
            F.to_json(
                F.struct(*[F.col(name).alias(name) for name in involved]),
                {"ignoreNullFields": "false"},
            ).alias("failed_values_json"),
            F.lit(json.dumps(details, default=str, sort_keys=True)).alias("rule_details_json"),
            F.lit(f"Row failed {rule['rule_type']} rule {rule['rule_id']}.").alias("failure_reason"),
            F.lit(resolved_run_id).alias("run_id"),
            *[F.lit(value).cast("timestamp" if key == "_committed_at" else "string").alias(key) for key, value in audit.items()],
        ))
    evidence = evidence_frames[0]
    for frame in evidence_frames[1:]:
        evidence = evidence.unionByName(frame)
    if evidence.limit(1).count():
        write_lakehouse_table_core(
            evidence, "METADATA_GUARDRAIL_ROW_RESULTS", target="metadata",
            schema=configured_lakehouse_schema(config, env, "metadata"), context=context, mode="append",
        )
    return result

def _dq_failed_expression(df, rule: dict[str, Any]):
    """Build a Spark boolean expression identifying rows that fail one DQ rule."""
    _, F, Window = _spark_sql_helpers()
    rule = _validate_dq_rules([dict(rule)])[0]
    rtype = str(rule["rule_type"])
    cols = [str(column) for column in rule.get("columns", [])]
    dataframe_columns = set(getattr(df, "columns", []))
    missing_columns = [column for column in cols if column not in dataframe_columns]
    condition_column = str(rule.get("condition_column") or "")
    if condition_column and condition_column not in dataframe_columns:
        missing_columns.append(condition_column)
    if missing_columns:
        return F.lit(True)
    col_name = cols[0] if cols else None

    def empty_string(column: str):
        return F.col(column).isNull() | (F.trim(F.col(column).cast("string")) == "")

    def compare(left, operator: str, right):
        if operator == "=":
            return left.eqNullSafe(right)
        if operator == "!=":
            return ~left.eqNullSafe(right)
        if operator == ">":
            return left > right
        if operator == ">=":
            return left >= right
        if operator == "<":
            return left < right
        return left <= right

    if rtype == "missing_values":
        total = int(df.count())
        null_count = int(df.filter(F.col(col_name).isNull()).count()) if total else 0
        failed = F.col(col_name).isNull() if total and ((null_count / total) * 100) > float(rule["maximum_null_percent"]) else F.lit(False)
    elif rtype == "blank_text":
        failed = empty_string(cols[0])
        for c in cols[1:]:
            failed = failed | empty_string(c)
    elif rtype in {"unique_values", "unique_combination"}:
        failed = F.count(F.lit(1)).over(Window.partitionBy(*[F.col(c) for c in cols])) > F.lit(1)
    elif rtype == "allowed_values":
        failed = F.col(col_name).isNotNull() & ~F.col(col_name).isin(list(rule["allowed_values"]))
    elif rtype == "blocked_values":
        failed = F.col(col_name).isNotNull() & F.col(col_name).isin(list(rule["blocked_values"]))
    elif rtype == "value_range":
        value_col = F.col(col_name)
        cond = F.lit(False)
        if rule.get("minimum") is not None:
            minimum = F.lit(rule["minimum"])
            cond = cond | (value_col < minimum if rule["minimum_inclusive"] else value_col <= minimum)
        if rule.get("maximum") is not None:
            maximum = F.lit(rule["maximum"])
            cond = cond | (value_col > maximum if rule["maximum_inclusive"] else value_col >= maximum)
        failed = F.col(col_name).isNotNull() & cond
    elif rtype == "text_pattern":
        failed = F.col(col_name).isNotNull() & ~F.col(col_name).cast("string").rlike(rule["pattern"])
    elif rtype == "compare_columns":
        left = F.col(cols[0])
        right = F.col(cols[1])
        failed = ~compare(left, rule["operator"], right)
        if rule["operator"] in {">", ">=", "<", "<="}:
            one_null = left.isNull() != right.isNull()
            failed = one_null | (left.isNotNull() & right.isNotNull() & failed)
    elif rtype == "required_when":
        condition = compare(F.col(condition_column), rule["condition_operator"], F.lit(rule["condition_value"]))
        missing = empty_string(cols[0])
        for c in cols[1:]:
            missing = missing | empty_string(c)
        failed = condition & missing
    elif rtype == "conditional_value":
        condition = compare(F.col(condition_column), rule["condition_operator"], F.lit(rule["condition_value"]))
        failed = condition & ~F.col(col_name).eqNullSafe(F.lit(rule["expected_value"]))
    else:
        raise ValueError(f"Unsupported rule_type: {rtype}")
    return F.coalesce(failed, F.lit(False))

def _run_dq_guardrail_checks(df, table_name: str, rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Run DQ rules and return notebook guardrail check dictionaries."""
    _, F, _ = _spark_sql_helpers()
    _validate_dq_rules(rules)
    total = int(df.count())
    checks: list[dict[str, Any]] = []
    dataframe_columns = set(getattr(df, "columns", []))
    for rule in rules:
        failed_rows = df.select(
            F.when(_dq_failed_expression(df, rule), F.lit(1)).otherwise(F.lit(0)).alias("failed")
        )
        failed_count = int(
            failed_rows.agg(F.sum("failed").alias("failed_count")).collect()[0]["failed_count"] or 0
        )
        severity = _normalize_dq_severity(rule.get("severity"))
        columns = [str(column) for column in rule.get("columns", [])]
        check_status = "passed" if failed_count <= 0 else ("failed" if severity == "error" else "warning")
        check = {
            "check": "dq_rule",
            "table_name": table_name,
            "rule_id": str(rule.get("rule_id") or ""),
            "rule_type": str(rule.get("rule_type") or ""),
            "columns": columns,
            "severity": severity,
            "status": check_status,
            "passed": failed_count == 0,
            "failed_count": failed_count,
            "total_count": total,
            "failed_percent": float(round((failed_count / total) * 100, 4)) if total else 0.0,
            "description": str(rule.get("description") or ""),
        }
        missing_columns = [column for column in columns if column not in dataframe_columns]
        if missing_columns:
            check["missing_columns"] = missing_columns
        checks.append(check)
    return checks

def _dq_tagged_dataframe(df, rules: list[dict[str, Any]]):
    """Return the full DataFrame tagged with failed DQ rule IDs and row status."""
    _, F, _ = _spark_sql_helpers()
    sorted_rules = sorted(rules or [], key=lambda rule: str(rule.get("rule_id") or ""))
    failed_rule_columns = [
        F.when(_dq_failed_expression(df, rule), F.lit(str(rule.get("rule_id") or "")))
        for rule in sorted_rules
    ]
    failed_rules = F.concat_ws(",", *failed_rule_columns) if failed_rule_columns else F.lit("")
    error_failures = [
        F.when(_dq_failed_expression(df, rule), F.lit(1)).otherwise(F.lit(0))
        for rule in sorted_rules
        if _normalize_dq_severity(rule.get("severity")) == "error"
    ]
    warning_failures = [
        F.when(_dq_failed_expression(df, rule), F.lit(1)).otherwise(F.lit(0))
        for rule in sorted_rules
        if _normalize_dq_severity(rule.get("severity")) != "error"
    ]
    error_count = error_failures[0] if error_failures else F.lit(0)
    for failure in error_failures[1:]:
        error_count = error_count + failure
    warning_count = warning_failures[0] if warning_failures else F.lit(0)
    for failure in warning_failures[1:]:
        warning_count = warning_count + failure
    return (
        df.withColumn("_dq_failed_rules", failed_rules)
        .withColumn(
            "_dq_check_status",
            F.when(error_count > F.lit(0), F.lit("failed"))
            .when(warning_count > F.lit(0), F.lit("warning"))
            .otherwise(F.lit("passed")),
        )
    )

def _summarize_dq_guardrail(checks: list[dict[str, Any]]) -> dict[str, Any]:
    if any(check.get("status") == "failed" for check in checks):
        status = "failed"
        can_continue = False
    elif any(check.get("status") == "warning" for check in checks):
        status = "warning"
        can_continue = True
    else:
        status = "passed"
        can_continue = True
    failed_checks = [check for check in checks if check.get("status") in {"warning", "failed"}]
    if not checks:
        message = "No active guardrail DQ rules found."
    elif failed_checks:
        message = f"DQ guardrail found {len(failed_checks)} rule failure(s): {status}."
    else:
        message = f"DQ guardrail passed {len(checks)} active guardrail rule(s)."
    return {"status": status, "can_continue": can_continue, "checks": checks, "message": message}

def _read_guardrail_rule_metadata(config, env, *, spark_session=None):
    """Read current DQ guardrail rules from the configured metadata target."""
    schema = configured_lakehouse_schema(config, env, "metadata")
    frame = read_lakehouse_table_core(GUARDRAIL_TABLE, target="metadata", schema=schema, spark_session=spark_session, context={"config": config, "env": env})
    if "guardrail_type" in set(getattr(frame, "columns", [])):
        _, F, _ = _spark_sql_helpers()
        return frame.filter(F.lower(F.coalesce(F.col("guardrail_type"), F.lit(""))) == "dq")
    return frame

# ---------------------------------------------------------------------------
# Canonical Guardrail rule/runtime adapters
# ---------------------------------------------------------------------------

GUARDRAIL_ROW_RESULTS_TABLE = "METADATA_GUARDRAIL_ROW_RESULTS"

def _stable_json(value: Any) -> str:
    return json.dumps(value, default=str, sort_keys=True, separators=(",", ":"))

def _parse_parameters(row: Mapping[str, Any]) -> dict[str, Any]:
    raw = row.get("rule_parameters_json") or "{}"
    try:
        return json.loads(raw) if isinstance(raw, str) else dict(raw or {})
    except (TypeError, json.JSONDecodeError):
        return {}

def canonical_guardrail_rule_record(
    record: Mapping[str, Any],
    *,
    config: Any,
    env: str,
) -> dict[str, Any]:
    """Return one authored rule using only the canonical physical contract."""
    audit = build_runtime_audit_fields(config=config, env=env)
    parameters = _parse_parameters(record)
    return {
        "guardrail_rule_id": str(record.get("guardrail_rule_id") or ""),
        "guardrail_version": int(record.get("guardrail_version") or 1),
        "table_id": str(record.get("table_id") or ""),
        "column_id": str(record.get("column_id") or ""),
        "environment_name": str(record.get("environment_name") or env),
        "guardrail_type": str(record.get("guardrail_type") or ""),
        "rule_id": str(record.get("rule_id") or ""),
        "rule_type": str(record.get("rule_type") or ""),
        "rule_parameters_json": _stable_json(parameters),
        "severity": str(record.get("severity") or "warning"),
        "is_active": bool(record.get("is_active", True)),
        **audit,
    }

def _select_rule(
    rules_df: Any,
    *,
    guardrail_type: str,
    table_id: str,
    environment_name: str = "",
) -> dict[str, Any] | None:
    if rules_df is None:
        return None
    rows = (
        rules_df.collect()
        if hasattr(rules_df, "collect")
        else ([rules_df] if isinstance(rules_df, dict) else rules_df)
    )
    candidates: list[dict[str, Any]] = []
    for raw in rows or []:
        row = _row_to_dict(raw)
        if str(row.get("guardrail_type") or "").lower() != guardrail_type.lower():
            continue
        if str(row.get("table_id") or "") != table_id:
            continue
        rule_environment = str(row.get("environment_name") or "")
        if environment_name and rule_environment != environment_name:
            continue
        if row.get("is_active") is not True:
            continue
        candidates.append(row)
    if not candidates:
        return None
    candidates.sort(
        key=lambda row: (
            int(row.get("guardrail_version") or 0),
            str(row.get("_committed_at") or ""),
        ),
        reverse=True,
    )
    return candidates[0]

def schema_check_core(
    dataframe: Any,
    expected_schema: dict[str, str] | None = None,
    *,
    preset: str = "strict",
    rules_df: Any = None,
    dataset_name: str = "",
    table_name: str = "",
    environment_name: str = "",
    metadata_table_key: str = "",
) -> dict[str, Any]:
    """Evaluate schema intent using the canonical Guardrail rule contract."""
    del dataset_name, table_name
    if rules_df is None:
        return _guardrail_schema_check_base(dataframe, expected_schema, preset=preset)
    rule = _select_rule(
        rules_df,
        guardrail_type="schema",
        table_id=metadata_table_key,
        environment_name=environment_name,
    )
    if rule is None:
        return _guardrail_schema_check_base(dataframe, {}, preset="monitor_only")
    params = _parse_parameters(rule)
    expected = params.get("data_types") or {}
    selected_columns = params.get("columns") or list(expected)
    expected_schema = {
        str(column): str(expected.get(column, "")) for column in selected_columns
    }
    rule_type = str(rule.get("rule_type") or "relaxed").lower()
    resolved_preset = {
        "strict": "strict",
        "minimum_required": "allow_new_columns",
        "relaxed": "allow_new_columns",
        "skip": "monitor_only",
    }.get(rule_type, "allow_new_columns")
    result = _guardrail_schema_check_base(dataframe, expected_schema, preset=resolved_preset)
    severity = str(rule.get("severity") or "blocking").lower()
    if result.get("status") == "failed" and severity == "warning":
        result["status"] = "warning"
        result["can_continue"] = True
    result.update(
        guardrail_type="schema",
        guardrail_rule_id=str(rule.get("guardrail_rule_id") or ""),
        guardrail_version=int(rule.get("guardrail_version") or 1),
        rule_id=str(rule.get("rule_id") or ""),
        rule_type=rule_type,
        severity=severity,
    )
    return result
