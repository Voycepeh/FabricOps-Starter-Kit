"""Shared pipeline implementation helpers."""

from __future__ import annotations

import json
from functools import reduce
from operator import or_
from typing import Any, Mapping, Sequence

from fabricops_kit.config.shared import build_audit_timestamp_expr, get_audit_timezone, get_current_audit_timestamp, resolve_fabric_context
from ..io.shared import configured_lakehouse_schema, write_lakehouse_table_core
from ..config.audit import _audit_timestamp_value, build_runtime_audit_fields
from ..config.shared import build_metadata_table_key
from ..config.metadata_schemas import coerce_metadata_row_types
from fabricops_kit.pipeline.metadata_evidence import _write_guardrail_result_row


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


def is_min_max_supported_type(data_type: str) -> bool:
    """Return whether min/max aggregation is safe for a Spark type string."""
    value = (data_type or "").lower()
    if any(token in value for token in ("array", "map", "struct", "binary")):
        return False
    return any(
        token in value
        for token in (
            "tinyint",
            "smallint",
            "int",
            "bigint",
            "float",
            "double",
            "decimal",
            "date",
            "timestamp",
            "string",
            "char",
            "varchar",
        )
    )




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

from fabricops_kit.pipeline.guardrails_shared import _run_active_dq_guardrail
from fabricops_kit.pipeline.guardrails_shared import (
    enforce_freshness,
    enforce_freshness_rule,
    enforce_profile_behavior,
    stop_if_failed,
    _check_schema_runtime,
    _check_schema_rule_runtime,
    source_change_rule_config,
)
PROFILED_TABLE = "METADATA_DATA_PROFILED"
CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
LINEAGE_TABLE = "METADATA_DATA_LINEAGE"
GUARDRAIL_RESULTS_TABLE = "METADATA_GUARDRAIL_RESULTS"




# ---------------------------------------------------------------------------
# Public API layer
# ---------------------------------------------------------------------------





def _now_iso(config: Any = None) -> str:
    return get_current_audit_timestamp(config=config)


def _timestamp_value(value: Any = None, config: Any = None):
    """Return a datetime value for metadata timestamp columns."""
    if value:
        from datetime import datetime

        return value if isinstance(value, datetime) else datetime.fromisoformat(str(value))
    return _audit_timestamp_value(config)


def _definition_name(name: str, definition: Mapping[str, Any]) -> str:
    return str(definition.get("table_name") or definition.get("name") or name)


def _summary_status(results: Mapping[str, Mapping[str, Any]]) -> str:
    """Return a roll-up status for guardrail result mappings.

    ``baseline_created`` is non-blocking and rolls up as ``passed``. ``skipped``
    is ignored when other concrete results exist and is returned only when all
    supplied results were skipped.
    """
    statuses = {str(result.get("status", "unknown")).lower() for result in results.values()}
    if not statuses:
        return "not_run"
    concrete = statuses - {"skipped"}
    if not concrete:
        return "skipped"
    if "failed" in concrete:
        return "failed"
    if "warning" in concrete:
        return "warning"
    if concrete <= {"passed", "success", "succeeded", "baseline_created"}:
        return "passed"
    return ",".join(sorted(concrete))


def _runtime_audit_fields(config: Any, env: str, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    runtime_context = None
    if isinstance(context, Mapping):
        runtime_context = context.get("runtime_context") or context.get("audit_runtime_context")
    return build_runtime_audit_fields(config=config, env=env, runtime_context=runtime_context)


def _canonical_catalogue_profile_df(profile_df: Any):
    """Return profile evidence using lowercase catalogue column names only."""
    from pyspark.sql import functions as F

    profile_columns = list(getattr(profile_df, "columns", []) or [])
    by_lower = {str(column).lower(): column for column in profile_columns}
    source_map = {
        "table_name": ("table_name", "TABLE_NAME"),
        "column_name": ("column_name", "COLUMN_NAME"),
        "run_timestamp": ("run_timestamp", "RUN_TIMESTAMP"),
        "data_type": ("data_type", "DATA_TYPE"),
        "row_count": ("row_count", "ROW_COUNT"),
        "null_count": ("null_count", "NULL_COUNT"),
        "null_percent": ("null_percent", "NULL_PERCENT"),
        "distinct_count": ("distinct_count", "DISTINCT_COUNT"),
        "distinct_percent": ("distinct_percent", "DISTINCT_PERCENT"),
        "min_value": ("min_value", "MIN_VALUE"),
        "max_value": ("max_value", "MAX_VALUE"),
        "distribution_type": ("distribution_type", "DISTRIBUTION_TYPE"),
        "distribution_json": ("distribution_json", "DISTRIBUTION_JSON"),
    }
    expressions = []
    for target, candidates in source_map.items():
        source = next((candidate for candidate in candidates if candidate in profile_columns), None)
        if source is None:
            source = next(
                (by_lower[candidate.lower()] for candidate in candidates if candidate.lower() in by_lower), None
            )
        if source is not None:
            expressions.append(F.col(source).alias(target))
    return profile_df.select(*expressions) if expressions else profile_df


def _normalize_catalogue_evidence_types(evidence_df: Any):
    """Cast catalogue evidence columns to the persisted metadata table schema."""
    from pyspark.sql import functions as F

    casts = {
        "row_count": "long",
        "null_count": "long",
        "distinct_count": "long",
        "null_percent": "double",
        "distinct_percent": "double",
        "run_timestamp": "timestamp",
    }
    normalized = evidence_df
    columns = set(getattr(evidence_df, "columns", []) or [])
    for column_name, data_type in casts.items():
        if column_name in columns:
            normalized = normalized.withColumn(column_name, F.col(column_name).cast(data_type))
    return normalized


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
        "change": "Review the observed source changes and apply the configured pipeline policy.",
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
    if guardrail == "change":
        return _result_reason(result) or "Source change check passed."
    if guardrail == "profile_behavior":
        return _profile_behavior_reason(result)
    if guardrail == "dq":
        return _dq_reason(result)
    return _result_reason(result)


def _table_keys(result_bundle: Mapping[str, Any]) -> list[str]:
    """Return stable table keys present in a guardrail result bundle."""
    keys: set[str] = set()
    for name in (
        "schema_results", "freshness_results", "change_results", "stability_results",
        "dq_results", "catalogue_status",
    ):
        value = result_bundle.get(name) or {}
        if isinstance(value, Mapping):
            keys.update(str(key) for key in value)
    return sorted(keys)


def build_guardrail_summary_rows(result_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build compact one-row-per-table guardrail summary rows.

    Parameters
    ----------
    result_bundle : mapping
        Result bundle returned by :func:`run_table_guardrails`.

    Returns
    -------
    list[dict[str, Any]]
        Rows with table, status, failed guardrail, continuation, reason, and
        next action fields for notebook display.

    """
    rows = []
    for table in _table_keys(result_bundle):
        results = {
            "schema": (result_bundle.get("schema_results") or {}).get(table, {}),
            "freshness": (result_bundle.get("freshness_results") or {}).get(table, {}),
            "change": (result_bundle.get("change_results") or {}).get(table, {}),
            "profile_behavior": (result_bundle.get("stability_results") or {}).get(table, {}),
            "dq": (result_bundle.get("dq_results") or {}).get(table, {}),
        }
        catalogue_value = (result_bundle.get("catalogue_status") or {}).get(table, "")
        failed_guardrail = "none"
        status = "passed"
        main_reason = "All blocking guardrails passed."
        for guardrail in ("schema", "freshness", "change", "profile_behavior", "dq"):
            result = results[guardrail]
            if not _result_can_continue(result) or _result_status(result) == "failed":
                failed_guardrail = guardrail
                status = "failed"
                main_reason = _guardrail_reason(guardrail, result)
                break
        else:
            profile_status = _result_status(results["profile_behavior"])
            warning_guardrail = next(
                (name for name, result in results.items() if _result_status(result) == "warning"), ""
            )
            if str(catalogue_value).lower() not in {"", "written", "success", "succeeded"}:
                failed_guardrail = "catalogue"
                status = "failed"
                main_reason = "Catalogue evidence failed to write."
            elif profile_status == "baseline_created":
                main_reason = "Profile behavior baseline created."
            elif warning_guardrail:
                status = "warning"
                failed_guardrail = warning_guardrail
                main_reason = _guardrail_reason(warning_guardrail, results[warning_guardrail])
        can_continue = status != "failed"
        rows.append(
            {
                "table": table,
                "status": status,
                "failed_guardrail": failed_guardrail,
                "can_continue": _yes_no(can_continue),
                "main_reason": main_reason,
                "next_action": _next_action(failed_guardrail, status),
                "schema": _result_status(results["schema"]),
                "freshness": _result_status(results["freshness"]),
                "change": _result_status(results["change"]),
                "profile_behavior": _result_status(results["profile_behavior"]),
                "dq": _result_status(results["dq"]),
                "catalogue": str(catalogue_value or ""),
            }
        )
    return rows


def build_guardrail_detail_rows(result_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build per-table, per-guardrail diagnostic rows."""
    rows = []
    result_groups = {
        "schema": result_bundle.get("schema_results") or {},
        "freshness": result_bundle.get("freshness_results") or {},
        "change": result_bundle.get("change_results") or {},
        "profile_behavior": result_bundle.get("stability_results") or {},
        "dq": result_bundle.get("dq_results") or {},
    }
    for table in _table_keys(result_bundle):
        for guardrail, group in result_groups.items():
            result = group.get(table, {})
            if not result:
                continue
            expected = (
                result.get("expected")
                or result.get("expected_value_json")
                or result.get("required_min_value")
                or result.get("missing_columns")
                or ""
            )
            actual = (
                result.get("actual")
                or result.get("actual_value_json")
                or result.get("latest_value")
                or result.get("unexpected_columns")
                or ""
            )
            rows.append(
                {
                    "table": table,
                    "guardrail": guardrail,
                    "status": _result_status(result),
                    "severity": str(result.get("severity") or result.get("freshness_severity") or "blocking"),
                    "can_continue": _yes_no(_result_can_continue(result)),
                    "reason": _guardrail_reason(guardrail, result),
                    "expected": json.dumps(expected, default=str, sort_keys=True)
                    if isinstance(expected, (dict, list))
                    else str(expected),
                    "actual": json.dumps(actual, default=str, sort_keys=True)
                    if isinstance(actual, (dict, list))
                    else str(actual),
                    "next_action": _next_action(guardrail, _result_status(result)),
                }
            )
    return rows


def _blocking_guardrail_message(summary_rows: list[dict[str, Any]], failed_tables: list[str]) -> str:
    """Return concise blocking failure message for notebook exceptions."""
    if len(failed_tables) == 1:
        table = failed_tables[0]
        row = next((item for item in summary_rows if item.get("table") == table), {})
        guardrail = str(row.get("failed_guardrail") or "guardrail").replace("_", " ")
        reason = str(row.get("main_reason") or "blocking guardrail failed").rstrip(".")
        prefix = f"{guardrail.capitalize()} failed: "
        if reason.lower().startswith(prefix.lower()):
            reason = reason[len(prefix) :]
        return f"Blocking guardrail failure for {table} — {guardrail} failed: {reason}."
    return (
        f"Blocking guardrail failure for {len(failed_tables)} table(s). See guardrail summary table above for details."
    )


def _build_guardrail_blocking_message_from_bundle(result_bundle: Mapping[str, Any]) -> str:
    """Build the concise blocking message for a guardrail result bundle."""
    failed_tables = [str(table) for table in result_bundle.get("failed_tables") or []]
    if not failed_tables:
        return ""
    summary_rows = list(result_bundle.get("summary_rows") or build_guardrail_summary_rows(result_bundle))
    return _blocking_guardrail_message(summary_rows, failed_tables)


def _display_guardrail_results_workflow(
    result_bundle: Mapping[str, Any], mode: str = "summary", spark_session: Any | None = None
) -> Any:
    """Return guardrail results prepared for summary, detailed, or debug display.

    Parameters
    ----------
    result_bundle : mapping
        Result bundle returned by :func:`run_table_guardrails`.
    mode : {"summary", "detailed", "debug"}, default="summary"
        Display mode for notebook output. ``summary`` is compact, ``detailed``
        is per-guardrail diagnostics, and ``debug`` returns raw nested results.
    spark_session : pyspark.sql.SparkSession, optional
        Spark session used to convert summary or detailed rows to a
        display-friendly DataFrame. When omitted, a list of dictionaries is
        returned.

    Returns
    -------
    Any
        Summary rows, detail rows, or raw nested debug object.

    """
    normalized = str(mode or "summary").lower().strip()
    if normalized == "summary":
        rows = build_guardrail_summary_rows(result_bundle)
        return rows if spark_session is None or not rows else spark_session.createDataFrame(rows)
    if normalized == "detailed":
        rows = build_guardrail_detail_rows(result_bundle)
        return rows if spark_session is None or not rows else spark_session.createDataFrame(rows)
    if normalized == "debug":
        return result_bundle.get("summary", result_bundle)
    raise ValueError("mode must be one of: summary, detailed, debug")


def _table_key(table_config: Mapping[str, Any]) -> str:
    return str(table_config["key"])


def _table_name(table_config: Mapping[str, Any]) -> str:
    return str(table_config.get("table_name") or table_config.get("target_name") or table_config["key"])


def _build_guardrail_evidence_definitions(table_configs: list[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """Build catalogue evidence definitions for pipeline table guardrails.

    Parameters
    ----------
    table_configs : list of mapping
        Source or target table configuration dictionaries. Each item must
        include ``key`` and normally includes ``table_name``, ``stage``, and
        optional target write metadata. DataFrame values are intentionally
        omitted from the returned definitions.

    Returns
    -------
    dict[str, dict[str, Any]]
        Definitions keyed by table key, suitable for
        :func:`write_catalogue_evidence`. Target definitions include resolved
        write-layer, kind, and mode fields when the stage is ``target``.

    """
    definitions: dict[str, dict[str, Any]] = {}
    for table_config in table_configs:
        table_key = _table_key(table_config)
        definition = {key: value for key, value in table_config.items() if key != "df"}
        definition["table_name"] = _table_name(table_config)
        fabric_store_target = str(table_config.get("fabric_store_target") or table_config.get("stage") or table_config.get("layer") or "source").strip().lower()
        definition["fabric_store_target"] = fabric_store_target
        definition["stage"] = table_config.get("stage", "target")
        if definition["stage"] == "target":
            definition["layer"] = table_config.get("target_layer", "unified")
            definition["kind"] = table_config.get("target_kind", "lakehouse")
            definition["mode"] = table_config.get("write_mode", "overwrite")
        definitions[table_key] = definition
    return definitions


def _run_table_guardrails_workflow(
    table_configs: list[dict[str, Any]],
    *,
    run_id: str | None = None,
    context: dict[str, Any] | None = None,
    spark_session: Any | None = None,
    agreement_id: str = "",
    agreement_version: str = "",
    table_role: str = "",
    mode: str = "profile",
    stop_on_failure: bool | None = None,
) -> dict[str, Any]:
    """Run approved checks for configured source or target tables.

    Runs the approved checks for each configured source or target table. It
    checks schema first, then freshness and source changes, followed by profile and data-quality
    rules, then returns a combined result showing whether the pipeline may
    continue.

    Parameters
    ----------
    table_configs : list of dict
        Source or target table configs. Each config must contain ``key``,
        ``df``, and ``expected_schema``. Optional keys such as
        ``dataset_name``, ``stage``, ``schema_preset``, ``profile_mode``,
        ``profile_behavior_severity``, ``watermark_column``, ``dq_preset``,
        ``exclude_columns``, ``previous_observation_df``, ``key_columns``,
        ``incremental_column``, ``refresh_days``, ``source_pattern``, and
        ``comparison_scope`` control the guardrail behavior. Source-change
        checking is skipped when no previous observation is supplied.
    run_id : str, optional
        Current pipeline run identifier. When omitted, the active context from
        an active pipeline context is used.
    spark_session : Any, optional
        Spark session used by profile behavior and DQ helpers. When omitted,
        the active context from an active pipeline context is used.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. Pass a dictionary
        such as ``{"config": CONFIG, "env": ENV}`` when no active pipeline
        context exists. When omitted, the helper uses ``FABRIC_CONTEXT``
        initialized by ``00_env_config``.
    agreement_id, agreement_version : str, optional
        Governance agreement context written with catalogue evidence. Omitted
        values are resolved from the active pipeline context when available.
    table_role : {"source", "target"}, optional
        Template-facing table role used to retain source and target definitions
        in the active context for summary defaults.
    mode : {"profile", "enforce"}, default="profile"
        Template-facing mode. ``profile`` defaults to non-blocking display, and
        ``enforce`` defaults to ``stop_on_failure=True``.
    stop_on_failure : bool, optional
        When True, collect all guardrail results and catalogue evidence, then
        stop notebook execution via the standard guardrail stopper if any table
        cannot continue. When omitted, the default is derived from ``mode``.

    Returns
    -------
    dict[str, Any]
        Guardrail result bundle containing profiles, schema results, freshness
        results, source change results, profile behavior results, DQ results, catalogue status,
        evidence definitions, concise ``summary``, ``can_continue``, and
        ``failed_tables``. Results remain separated by table key and guardrail
        type.

    Notes
    -----
    User-facing workflow:

    Prepared table configurations
        ↓
    Load the approved guardrail rules
        ↓
    Run schema, freshness, source change, profile and DQ checks
        ↓
    Save each guardrail outcome
    ``METADATA_GUARDRAIL_RESULTS``
        ↓
    Combine the table results
        ↓
    Return whether the pipeline can continue

    The returned bundle includes per-table profiles, schema results, freshness
    results, source-change results, profile-behavior results, DQ results, catalogue status, an
    overall summary, ``can_continue``, and failed tables. ``can_continue=True``
    means no blocking guardrail result requires the pipeline to stop.
    ``can_continue=False`` means the notebook should stop before writing the
    affected output.

    This helper intentionally collects all per-table schema, freshness, profile behavior, and DQ
    results before reporting blocking failures. DQ results that return an
    annotated DataFrame update the corresponding table config ``df`` in place
    so downstream writes use the checked DataFrame. Metadata reads and writes
    are routed through the configured metadata target by the called helpers.

    """
    from ..widgets.shared import pipeline_active_context

    active = pipeline_active_context()
    if active is not None:
        context = context if context is not None else active.context
        spark_session = spark_session if spark_session is not None else active.spark_session
        run_id = run_id or active.run_id
        agreement_id = agreement_id or active.agreement_id
        agreement_version = agreement_version or active.agreement_version
    if spark_session is None:
        raise ValueError("spark_session is required unless an active pipeline context is established.")
    if not run_id:
        raise ValueError("run_id is required for in-memory profile grouping; use the active pipeline context or pass a real run_id.")
    normalized_mode = str(mode or "profile").lower().strip()
    if normalized_mode not in {"profile", "enforce"}:
        raise ValueError("mode must be one of: profile, enforce.")
    if stop_on_failure is None:
        stop_on_failure = normalized_mode == "enforce"

    config, env, resolved_context = resolve_fabric_context(context=context)
    profiles: dict[str, Any] = {}
    schema_results: dict[str, Mapping[str, Any]] = {}
    freshness_results: dict[str, Mapping[str, Any]] = {}
    change_results: dict[str, Mapping[str, Any]] = {}
    stability_results: dict[str, Mapping[str, Any]] = {}
    dq_results: dict[str, Mapping[str, Any]] = {}
    failed_tables: list[str] = []
    evidence_definitions = _build_guardrail_evidence_definitions(table_configs)

    for table_config in table_configs:
        table_key = _table_key(table_config)
        table_name = _table_name(table_config)
        dataset_name = table_config.get("dataset_name", table_name)
        stage = table_config.get("stage", "target")
        store_type = str(table_config.get("kind") or table_config.get("target_kind") or "lakehouse")
        layer = str(table_config.get("layer") or table_config.get("fabric_store_target") or stage)
        schema_name = table_config.get("schema_name", table_config.get("schema"))
        dataframe = table_config["df"]
        metadata_table_key = build_metadata_table_key(store_type, layer, schema_name, table_name)

        guardrail_rules_df = table_config.get("guardrail_rules_df")
        schema_rules_df = table_config.get("schema_rules_df", guardrail_rules_df)
        freshness_rules_df = table_config.get("freshness_rules_df", guardrail_rules_df)
        change_rules_df = table_config.get("change_rules_df", guardrail_rules_df)
        if schema_rules_df is not None:
            schema_results[table_key] = _check_schema_rule_runtime(
                dataframe,
                schema_rules_df,
                dataset_name=dataset_name,
                table_name=table_name,
                environment_name=env,
                metadata_table_key=metadata_table_key,
            )
        else:
            schema_results[table_key] = _check_schema_runtime(
                dataframe,
                table_config["expected_schema"],
                preset=table_config.get("schema_preset", "strict"),
            )

        if not _result_can_continue(schema_results[table_key]):
            freshness_results[table_key] = {
                "status": "skipped", "can_continue": True,
                "message": "Freshness check skipped because schema validation failed.",
            }
            change_results[table_key] = {
                "status": "skipped", "can_continue": True,
                "message": "Change check skipped because schema validation failed.",
            }
        else:
            if freshness_rules_df is not None:
                freshness_results[table_key] = enforce_freshness_rule(
                    dataframe, freshness_rules_df, dataset_name=dataset_name, table_name=table_name,
                    environment_name=env, metadata_table_key=metadata_table_key,
                )
            else:
                freshness_results[table_key] = enforce_freshness(
                    dataframe, table_config.get("freshness_column"),
                    table_config.get("freshness_max_lag_days"),
                    severity=table_config.get("freshness_severity", "blocking"),
                )

            previous_df = table_config.get("previous_observation_df")
            if not _result_can_continue(freshness_results[table_key]):
                change_results[table_key] = {
                    "status": "skipped", "can_continue": True,
                    "message": "Change check skipped because freshness validation blocked continuation.",
                }
            elif previous_df is None:
                change_results[table_key] = {
                    "status": "skipped", "can_continue": True,
                    "message": "Change check skipped because no previous observation was supplied.",
                }
            else:
                configured_rule = source_change_rule_config(
                    change_rules_df,
                    dataset_name=dataset_name,
                    table_name=table_name,
                    environment_name=env,
                    metadata_table_key=metadata_table_key,
                ) if change_rules_df is not None else None
                change_config = {**table_config, **(configured_rule or {})}
                facts = detect_source_changes_core(
                    dataframe, previous_df,
                    key_columns=change_config.get("key_columns"),
                    incremental_column=change_config.get("incremental_column"),
                    refresh_days=change_config.get("refresh_days", 7),
                    source_pattern=change_config.get("source_pattern", "snapshot"),
                    version_columns=change_config.get("version_columns"),
                    comparison_scope=change_config.get("comparison_scope", "complete"),
                    include_row_changes=change_config.get("include_row_changes", True),
                )
                historical = facts["has_historical_changes"]
                severity = change_config.get("severity", change_config.get("change_severity", "warning"))
                status = "passed"
                if historical:
                    status = "failed" if severity == "blocking" else "warning"
                change_results[table_key] = {
                    **facts,
                    "status": status,
                    "can_continue": not historical or severity != "blocking",
                    "severity": severity,
                    "rule_key": change_config.get("rule_key", "change_default"),
                    "message": "Historical source drift detected." if historical else "Source change check passed.",
                    "actual": {key: value for key, value in facts.items() if key != "row_changes"},
                }

        profiles[table_key] = build_profile_dataframe(
            dataframe, exclude_columns=table_config.get("exclude_columns"),
        )

        stability_results[table_key] = enforce_profile_behavior(
            spark_session,
            dataframe,
            CATALOGUE_TABLE,
            dataset_name,
            table_name,
            stage=stage,
            profile_mode=table_config.get("profile_mode"),
            watermark_column=table_config.get("watermark_column"),
            severity=table_config.get("profile_behavior_severity", table_config.get("severity", "blocking")),
            rule_key=table_config.get("profile_behavior_rule_key", "profile_behavior_default"),
            exclude_columns=table_config.get("exclude_columns"),
            exclude_run_id=run_id,
            config=config,
            env=env,
            current_profile=profiles[table_key],
            write_results=table_config.get("write_profile_behavior_results", True),
            rules_table=table_config.get("profile_behavior_rules_table", "METADATA_GUARDRAIL"),
            rules_df=table_config.get("profile_behavior_rules_df", guardrail_rules_df),
            store_type=store_type,
            layer=layer,
            schema_name=schema_name,
        )

        if table_config.get("dq_preset", "active_rules") == "skip":
            dq_results[table_key] = {
                "status": "skipped",
                "can_continue": True,
                "checks": [],
                "message": "DQ guardrail skipped by preset.",
            }
        else:
            dq_results[table_key] = _run_active_dq_guardrail(
                dataframe,
                config,
                env,
                dataset_name,
                table_name,
                spark_session=spark_session,
                write_results=False,
                store_type=store_type,
                layer=layer,
                schema_name=schema_name,
            )

        if "dataframe" in dq_results[table_key]:
            table_config["df"] = dq_results[table_key]["dataframe"]

        if table_config.get("write_guardrail_results", True) and hasattr(spark_session, "createDataFrame"):
            for guardrail_type, rule_type, guardrail_result in (
                ("schema", table_config.get("schema_preset", "strict"), schema_results[table_key]),
                ("freshness", table_config.get("freshness_column", "freshness"), freshness_results[table_key]),
                ("change", table_config.get("source_pattern", "snapshot"), change_results[table_key]),
                ("dq", table_config.get("dq_preset", "active_rules"), dq_results[table_key]),
            ):
                _write_guardrail_result_row(
                    spark_session=spark_session,
                    config=config,
                    env=env,
                    dataset_name=dataset_name,
                    table_name=table_name,
                    store_type=store_type,
                    layer=layer,
                    schema_name=schema_name,
                    guardrail_type=guardrail_type,
                    rule_type=str(rule_type or guardrail_type),
                    result=guardrail_result,
                )

        table_can_continue = all(
            bool((result or {}).get("can_continue", True))
            for result in (
                schema_results[table_key],
                freshness_results[table_key],
                change_results[table_key],
                stability_results[table_key],
                dq_results[table_key],
            )
        )
        if not table_can_continue:
            failed_tables.append(table_key)

    catalogue_status = write_catalogue_evidence(
        profiles,
        evidence_definitions,
        config=config,
        env=env,
        run_id=run_id,
        context=resolved_context,
        agreement_id=agreement_id,
        agreement_version=agreement_version,
        schema_results=schema_results,
        freshness_results=freshness_results,
        stability_results=stability_results,
        dq_results=dq_results,
    )

    summary = {
        "schema_results": schema_results,
        "freshness_results": freshness_results,
        "change_results": change_results,
        "stability_results": stability_results,
        "dq_results": dq_results,
        "catalogue_status": catalogue_status,
        "failed_tables": failed_tables,
    }
    result = {
        "profiles": profiles,
        "schema_results": schema_results,
        "freshness_results": freshness_results,
        "change_results": change_results,
        "stability_results": stability_results,
        "dq_results": dq_results,
        "catalogue_status": catalogue_status,
        "evidence_definitions": evidence_definitions,
        "summary": summary,
        "can_continue": not failed_tables,
        "failed_tables": failed_tables,
    }
    result["summary_rows"] = build_guardrail_summary_rows(result)
    result["detail_rows"] = build_guardrail_detail_rows(result)
    result["blocking_message"] = _build_guardrail_blocking_message_from_bundle(result)

    normalized_role = str(table_role or "").lower().strip()
    if active is not None and normalized_role in {"source", "target"}:
        if normalized_role == "source":
            active.source_definitions = evidence_definitions
        else:
            active.target_definitions = evidence_definitions

    if stop_on_failure and failed_tables:
        stop_if_failed(
            {
                "status": "failed",
                "can_continue": False,
                "message": result["blocking_message"],
                "failed_tables": failed_tables,
            }
        )

    return result


def write_catalogue_evidence(
    profiles: Mapping[str, Any],
    dataset_definitions: Mapping[str, Mapping[str, Any]],
    *,
    config: Any,
    env: str,
    run_id: str,
    context: Mapping[str, Any] | None = None,
    agreement_id: str = "",
    agreement_version: str = "",
    schema_results: Mapping[str, Mapping[str, Any]] | None = None,
    freshness_results: Mapping[str, Mapping[str, Any]] | None = None,
    stability_results: Mapping[str, Mapping[str, Any]] | None = None,
    dq_results: Mapping[str, Mapping[str, Any]] | None = None,
    metadata_table: str = PROFILED_TABLE,
    mode: str = "append",
) -> dict[str, str]:
    """Write observed profile evidence to the metadata profiled evidence.

    Parameters
    ----------
    profiles : mapping of str to DataFrame
        Profile DataFrames produced by ``profile_dataframe`` for each dataset.
    dataset_definitions : mapping of str to mapping
        Source or target definitions containing table, stage, and layer context.
    config, env : object, str
        Metadata lakehouse route from ``00_env_config``.
    run_id : str
        Required in-process profile grouping identifier. Catalogue rows persist
        execution identity through the canonical ``_activity_id`` audit field.
    context : mapping, optional
        Resolved FabricOps runtime context used to build canonical audit fields.
    agreement_id, agreement_version : str, optional
        Governance context added to each catalogue row.
    schema_results, freshness_results, stability_results, dq_results : mapping, optional
        Runtime guardrail results are accepted by this writer but are not
        written to ``METADATA_DATA_PROFILED``.
    metadata_table : str, default="METADATA_DATA_PROFILED"
        Metadata table to append.
    mode : str, default="append"
        Physical write mode for catalogue evidence.

    Returns
    -------
    dict[str, str]
        Write status keyed by dataset alias.

    """
    from pyspark.sql import functions as F

    del schema_results, freshness_results, dq_results
    audit = _runtime_audit_fields(config, env, context)
    statuses: dict[str, str] = {}
    for name, profile_df in profiles.items():
        definition = dataset_definitions[name]
        table_name = _definition_name(name, definition)
        dataset_name = str(definition.get("dataset_name") or table_name)
        stage = str(definition.get("stage", "target"))
        stability_result = dict((stability_results or {}).get(name) or {})
        base_evidence = _canonical_catalogue_profile_df(profile_df)
        store_type = str(definition.get("kind") or definition.get("target_kind") or "lakehouse")
        layer = str(definition.get("layer") or definition.get("fabric_store_target") or stage)
        schema_name = definition.get("schema_name", definition.get("schema"))
        metadata_table_key = build_metadata_table_key(store_type, layer, schema_name, table_name)
        profile_evidence_rows = list(stability_result.get("profile_evidence_rows") or [])
        if not profile_evidence_rows:
            profile_evidence_rows = [
                {
                    "watermark_column": str(
                        stability_result.get("watermark_column", definition.get("watermark_column", ""))
                    ),
                    "watermark_value": str(
                        stability_result.get(
                            "watermark_value",
                            "__FULL_TABLE__" if str(stability_result.get("profile_mode", "")) == "static_data" else "",
                        )
                    ),
                    "profile_payload_json": str(stability_result.get("profile_payload_json", "")),
                    "profile_hash": str(stability_result.get("profile_hash", "")),
                    "row_count": stability_result.get("row_count"),
                }
            ]
        fabric_store_target = str(definition["fabric_store_target"]).strip().lower()
        additions = {
            "metadata_table_key": metadata_table_key,
            "environment_name": env,
            "dataset_name": dataset_name,
            "table_name": table_name,
            "layer": str(definition.get("layer", "")),
            "fabric_store_target": fabric_store_target,
            "asset_kind": str(definition.get("kind", "lakehouse")),
            "profile_stage": stage,
            "profile_status": "success",
            "profiled_at": _now_iso(config),
            "agreement_id": agreement_id,
            "agreement_version": agreement_version,
            "evidence_role": str(definition.get("evidence_role", f"{stage}_profile")),
            "profile_mode": str(stability_result.get("profile_mode", definition.get("profile_mode", ""))),
            **audit,
        }
        for profile_evidence in profile_evidence_rows:
            evidence = base_evidence
            group_additions = {
                **additions,
                "watermark_column": str(profile_evidence.get("watermark_column", "")),
                "watermark_value": str(profile_evidence.get("watermark_value", "")),
                "profile_payload_json": str(profile_evidence.get("profile_payload_json", "")),
                "profile_hash": str(profile_evidence.get("profile_hash", "")),
            }
            if profile_evidence.get("row_count") not in (None, ""):
                group_additions["row_count"] = profile_evidence.get("row_count")
            for column, value in group_additions.items():
                evidence = evidence.withColumn(column, F.lit(value))
            evidence = evidence.withColumn(
                "metadata_column_key", F.concat_ws("::", F.lit(metadata_table_key), F.col("column_name"))
            )
            evidence = _normalize_catalogue_evidence_types(evidence)
            write_lakehouse_table_core(
                evidence,
                metadata_table,
                target="metadata",
                schema=configured_lakehouse_schema(config, env, "metadata"),
                context={"config": config, "env": env},
                mode=mode,
            )
        statuses[name] = "written"
    return statuses


# Source change detection helpers
PATTERNS = {"snapshot", "incremental_append", "mutable_incremental", "versioned"}
SCOPES = {"complete", "partitions", "partial"}


def _column_names(values: Sequence[str] | None, name: str) -> list[str]:
    if values is None or isinstance(values, str) or not values:
        raise ValueError(f"{name} must be a non-empty sequence of column names.")
    result = [str(value).strip() for value in values]
    if any(not value for value in result) or len(result) != len(set(result)):
        raise ValueError(f"{name} must contain unique, non-empty column names.")
    return result


def _validate(current_df, previous_df, *, key_columns, incremental_column, refresh_days,
              source_pattern, version_columns, comparison_scope):
    keys = _column_names(key_columns, "key_columns")
    versions = [] if version_columns is None else _column_names(version_columns, "version_columns")
    pattern, scope = str(source_pattern).strip().lower(), str(comparison_scope).strip().lower()
    if pattern not in PATTERNS:
        raise ValueError(f"source_pattern must be one of: {', '.join(sorted(PATTERNS))}.")
    if scope not in SCOPES:
        raise ValueError(f"comparison_scope must be one of: {', '.join(sorted(SCOPES))}.")
    if isinstance(refresh_days, bool) or not isinstance(refresh_days, int) or refresh_days <= 0:
        raise ValueError("refresh_days must be a positive integer.")
    if pattern == "versioned" and not versions:
        raise ValueError("version_columns is required when source_pattern='versioned'.")
    if pattern != "versioned" and versions:
        raise ValueError("version_columns is only valid when source_pattern='versioned'.")
    if incremental_column is not None and (not isinstance(incremental_column, str) or not incremental_column.strip()):
        raise ValueError("incremental_column must be a non-empty column name when configured.")
    incremental = incremental_column.strip() if incremental_column else None
    required = keys + versions + ([incremental] if incremental else [])
    for label, frame in (("current_df", current_df), ("previous_df", previous_df)):
        missing = [column for column in required if column not in frame.columns]
        if missing:
            raise ValueError(f"{label} is missing required columns: {', '.join(missing)}.")
    if set(current_df.columns) != set(previous_df.columns):
        raise ValueError("current_df and previous_df must contain the same columns.")
    return keys + versions, pattern, scope, incremental


def _hash(columns):
    from pyspark.sql import functions as F

    encoded = [F.to_json(F.struct(F.col(column).alias("value"))) for column in columns]
    return F.sha2(F.concat_ws("\u001f", *encoded), 256)


def _state(df, identity, incremental):
    from pyspark.sql import functions as F

    attributes = [column for column in sorted(df.columns) if column not in identity]
    result = df.withColumn("key_hash", _hash(identity)).withColumn(
        "non_key_hash", _hash(attributes) if attributes else F.sha2(F.lit(""), 256)
    )
    return result.withColumn("_partition", F.col(incremental) if incremental else F.lit("__FULL_SOURCE__"))


def _assert_keys(state, identity, label):
    from pyspark.sql import functions as F

    if state.where(reduce(or_, (F.col(column).isNull() for column in identity))).limit(1).count():
        raise ValueError(f"{label} contains a null logical key.")
    if state.groupBy("key_hash").count().where(F.col("count") > 1).limit(1).count():
        raise ValueError(f"{label} contains non-unique configured logical keys.")


def _fingerprints(state):
    from pyspark.sql import functions as F

    aggregates = state.groupBy(F.col("_partition").alias("partition_value")).agg(
        F.count("*").alias("row_count"),
        F.min("key_hash").alias("min_key"),
        F.max("key_hash").alias("max_key"),
        F.expr("bit_xor(xxhash64(key_hash, non_key_hash))").alias("row_hash_xor"),
        F.expr("sum(cast(xxhash64(key_hash, non_key_hash) as decimal(38,0)))").alias("row_hash_sum"),
    )
    return aggregates.withColumn(
        "partition_hash",
        F.sha2(
            F.concat_ws("|", "row_count", "min_key", "max_key", "row_hash_xor", "row_hash_sum"),
            256,
        ),
    )


def _one(df, expression):
    return df.agg(expression.alias("value")).first()["value"]


def _detect(current_df, previous_df, *, key_columns, incremental_column, refresh_days,
            source_pattern, version_columns, comparison_scope, include_row_changes):
    from pyspark.sql import functions as F

    identity, pattern, scope, incremental = _validate(
        current_df, previous_df, key_columns=key_columns, incremental_column=incremental_column,
        refresh_days=refresh_days, source_pattern=source_pattern, version_columns=version_columns,
        comparison_scope=comparison_scope,
    )
    current, previous = _state(current_df, identity, incremental), _state(previous_df, identity, incremental)
    _assert_keys(current, identity, "current_df")
    _assert_keys(previous, identity, "previous_df")
    partitions = _fingerprints(current).alias("c").join(_fingerprints(previous).alias("p"), "partition_value", "full")
    new_partitions = [r.partition_value for r in partitions.where(F.col("p.partition_hash").isNull()).collect()]
    missing_valid = scope == "complete"
    missing_partitions = ([r.partition_value for r in partitions.where(F.col("c.partition_hash").isNull()).collect()]
                          if missing_valid else [])
    changed_partitions = [r.partition_value for r in partitions.where(
        F.col("c.partition_hash").isNotNull() & F.col("p.partition_hash").isNotNull()
        & (F.col("c.partition_hash") != F.col("p.partition_hash"))).collect()]
    joined = current.select("key_hash", "non_key_hash", "_partition").alias("c").join(
        previous.select("key_hash", "non_key_hash", "_partition").alias("p"), "key_hash", "full")
    comparable_deletion = F.lit(scope == "complete")
    if scope == "partitions":
        comparable_deletion = F.col("p._partition").isin(
            [row.partition_value for row in _fingerprints(current).select("partition_value").collect()]
        )
    kind = (F.when(F.col("p.non_key_hash").isNull(), "inserted")
            .when(F.col("c.non_key_hash").isNull(),
                  F.when(comparable_deletion, "deleted").otherwise("not_comparable"))
            .when(F.col("c.non_key_hash") != F.col("p.non_key_hash"), "updated").otherwise("unchanged"))
    changes = joined.withColumn("change_type", kind).withColumn(
        "incremental_value", F.coalesce(F.col("c._partition"), F.col("p._partition")))
    source_min = source_max = previous_max = refresh_start = None
    if incremental:
        source_min, source_max = _one(current_df, F.min(incremental)), _one(current_df, F.max(incremental))
        previous_max = _one(previous_df, F.max(incremental))
        if source_max is not None:
            refresh_start = _one(current_df, F.date_sub(F.lit(source_max).cast("date"), refresh_days))
        changes = changes.withColumn("change_recency", F.when(
            F.col("incremental_value").cast("date") >= F.lit(refresh_start), "recent").otherwise("historical"))
    else:
        changes = changes.withColumn("change_recency", F.lit("recent"))
    classified = changes.where(F.col("change_type").isin("inserted", "updated", "deleted"))
    raw_counts = {(r.change_recency, r.change_type): r["count"]
                  for r in classified.groupBy("change_recency", "change_type").count().collect()}
    counts = {when: {kind: raw_counts.get((when, kind), 0) for kind in ("inserted", "updated", "deleted")}
              for when in ("recent", "historical")}
    return {
        "source_pattern": pattern, "comparison_scope": scope, "refresh_days": refresh_days,
        "source_range": {"minimum": source_min, "maximum": source_max},
        "previous_observed_maximum": previous_max,
        "recent_mutable_range": {"start": refresh_start, "end": source_max},
        "new_unseen_range": ({"start_exclusive": previous_max, "end_inclusive": source_max} if incremental else None),
        "historical_comparison_range": ({"before": refresh_start} if incremental else None),
        "partitions_checked": partitions.count(), "new_partitions": new_partitions,
        "changed_partitions": changed_partitions, "missing_partitions": missing_partitions,
        "missing_partition_detection_valid": missing_valid, "recent_changes": counts["recent"],
        "historical_changes": counts["historical"], "row_changes": classified if include_row_changes else None,
        "has_changes": classified.limit(1).count() > 0,
        "has_historical_changes": sum(counts["historical"].values()) > 0,
    }



def detect_source_changes_core(current_df, previous_df, *, key_columns, incremental_column=None, refresh_days=7, source_pattern="snapshot", version_columns=None, comparison_scope="complete", include_row_changes=True):
    """Return source change facts for the guardrail orchestration workflow.

    ``source_pattern`` records the configured storage pattern for read planning;
    ``versioned`` additionally requires version identity columns. Comparison
    completeness and deletion validity are controlled explicitly by
    ``comparison_scope`` rather than inferred from the descriptive pattern.
    ``previous_df`` is orchestration input for this initial capability, not a
    durable observation service.
    """
    return _detect(current_df, previous_df, key_columns=key_columns, incremental_column=incremental_column, refresh_days=refresh_days, source_pattern=source_pattern, version_columns=version_columns, comparison_scope=comparison_scope, include_row_changes=include_row_changes)
