"""Shared pipeline implementation helpers."""

from __future__ import annotations

import json
from functools import reduce
from typing import Any, Mapping

from fabricops_kit.config.shared import build_audit_timestamp_expr, get_audit_timezone, get_current_audit_timestamp, resolve_fabric_context
from ..io.shared import configured_lakehouse_schema, read_lakehouse_table_core, write_lakehouse_table_core
from ..config.audit import _audit_timestamp_value, build_runtime_audit_fields
from ..config.shared import build_metadata_table_key
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


def build_guardrail_summary_rows(result_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Build compact one-row-per-table guardrail summary rows.

    Parameters
    ----------
    result_bundle : mapping
        Result bundle returned by the governed runtime checks.

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
            "profile_behavior": (result_bundle.get("stability_results") or {}).get(table, {}),
            "dq": (result_bundle.get("dq_results") or {}).get(table, {}),
        }
        catalogue_value = (result_bundle.get("catalogue_status") or {}).get(table, "")
        failed_guardrail = "none"
        status = "passed"
        main_reason = "All blocking guardrails passed."
        for guardrail in ("schema", "freshness", "profile_behavior", "dq"):
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


def orchestrate_table_guardrails(
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
    can check the schema, data freshness, profile changes, and data-quality
    rules, then returns a combined result showing whether the pipeline may
    continue.

    Parameters
    ----------
    table_configs : list of dict
        Source or target table configs. Each config must contain ``key``,
        ``df``, and ``expected_schema``. Optional keys such as
        ``dataset_name``, ``stage``, ``schema_preset``, ``profile_mode``,
        ``profile_behavior_severity``, ``watermark_column``, ``dq_preset``,
        and ``exclude_columns`` control the guardrail behavior.
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
        results, changes results, profile behavior results, DQ results, catalogue status,
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
    Run schema, freshness, changes, profile and DQ checks
        ↓
    Save each guardrail outcome
    ``METADATA_GUARDRAIL_RESULTS``
        ↓
    Combine the table results
        ↓
    Return whether the pipeline can continue

    The returned bundle includes per-table profiles, schema results, freshness
    results, profile-behavior results, DQ results, catalogue status, an
    overall summary, ``can_continue``, and failed tables. ``can_continue=True``
    means no blocking guardrail result requires the pipeline to stop.
    ``can_continue=False`` means the notebook should stop before writing the
    affected output.

    This helper intentionally collects all per-table schema, freshness, changes, profile behavior, and DQ
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
    changes_results: dict[str, Mapping[str, Any]] = {}
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
        if schema_rules_df is not None:
            schema_results[table_key] = schema_check_core(
                dataframe,
                rules_df=schema_rules_df,
                dataset_name=dataset_name,
                table_name=table_name,
                environment_name=env,
                metadata_table_key=metadata_table_key,
            )
        else:
            schema_results[table_key] = schema_check_core(
                dataframe,
                table_config.get("expected_schema", {}),
                preset=table_config.get("schema_preset", "strict"),
            )

        schema_allows_continuation = bool(schema_results[table_key].get("can_continue", True))
        if not schema_allows_continuation:
            freshness_results[table_key] = {
                "status": "skipped", "can_continue": True, "check_type": "freshness",
                "message": "Freshness check skipped because the blocking schema prerequisite failed.",
            }
        elif freshness_rules_df is not None:
            freshness_results[table_key] = freshness_check_core(
                dataframe,
                rules_df=freshness_rules_df,
                dataset_name=dataset_name,
                table_name=table_name,
                environment_name=env,
                metadata_table_key=metadata_table_key,
            )
        else:
            freshness_results[table_key] = freshness_check_core(
                dataframe,
                table_config.get("freshness_column"),
                table_config.get("freshness_max_lag_days"),
                severity=table_config.get("freshness_severity", "blocking"),
            )

        freshness_allows_continuation = bool(freshness_results[table_key].get("can_continue", True))
        changes_enabled = bool(table_config.get("change_key_columns"))
        if not schema_allows_continuation or not freshness_allows_continuation:
            changes_results[table_key] = {
                "status": "skipped", "can_continue": True, "check_type": "changes",
                "guardrail_type": "changes",
                "message": "Changes check skipped because a blocking source prerequisite failed.",
            }
        elif changes_enabled:
            changes_results[table_key] = changes_check_core(
                dataframe,
                table_config.get("previous_dataframe"),
                partition_columns=table_config.get("change_partition_columns"),
                key_columns=table_config.get("change_key_columns"),
                non_key_columns=table_config.get("change_non_key_columns"),
                range_column=table_config.get("change_range_column"),
                source_pattern=table_config.get("source_pattern", "snapshot"),
                comparison_scope=table_config.get("comparison_scope", "complete"),
                refresh_days=table_config.get("refresh_days", 0),
                version_column=table_config.get("version_column"),
                reference_date=table_config.get("change_reference_date"),
                include_row_changes=table_config.get("include_row_changes", False),
            )
        else:
            changes_results[table_key] = {
                "status": "skipped", "can_continue": True, "check_type": "changes",
                "guardrail_type": "changes",
                "message": "Changes check skipped because no logical key columns are configured.",
            }

        profiles[table_key] = build_profile_dataframe(
            dataframe,
            exclude_columns=table_config.get("exclude_columns"),
        )

        prerequisites_allow_continuation = schema_allows_continuation and freshness_allows_continuation

        if prerequisites_allow_continuation:
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
        else:
            stability_results[table_key] = {
                "status": "skipped", "can_continue": True, "check_type": "profile_behavior",
                "message": "Profile behavior skipped because a blocking source prerequisite failed.",
                "profile_evidence_rows": [],
            }

        if not schema_allows_continuation:
            dq_results[table_key] = {
                "status": "skipped", "can_continue": True, "checks": [],
                "message": "DQ guardrail skipped because the blocking schema prerequisite failed.",
            }
        elif table_config.get("dq_preset", "active_rules") == "skip":
            dq_results[table_key] = {
                "status": "skipped",
                "can_continue": True,
                "checks": [],
                "message": "DQ guardrail skipped by preset.",
            }
        else:
            dq_results[table_key] = run_active_dq_guardrail(
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
                ("changes", table_config.get("source_pattern", "snapshot"), changes_results[table_key]),
                ("dq", table_config.get("dq_preset", "active_rules"), dq_results[table_key]),
            ):
                write_guardrail_result_row(
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
                changes_results[table_key],
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
        "changes_results": changes_results,
        "stability_results": stability_results,
        "dq_results": dq_results,
        "catalogue_status": catalogue_status,
        "failed_tables": failed_tables,
    }
    result = {
        "profiles": profiles,
        "schema_results": schema_results,
        "freshness_results": freshness_results,
        "changes_results": changes_results,
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


def is_source_observation(dataframe: Any) -> bool:
    """Return whether a value exposes the normalized observation contract."""
    columns = set(getattr(dataframe, "columns", ()))
    if not columns and isinstance(dataframe, (list, tuple)) and dataframe:
        columns = set(dict(dataframe[0]))
    return SOURCE_OBSERVATION_COLUMNS <= columns


def catalogue_table_identity(
    *, config: Any, env: str, table_id: str, spark_session: Any
) -> dict[str, Any] | None:
    """Resolve physical table attributes from the environment-specific Catalogue row."""
    catalogue = read_lakehouse_table_core(
        "METADATA_DATA_CATALOGUE",
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        spark_session=spark_session,
        context={"config": config, "env": env},
    )
    if hasattr(catalogue, "where"):
        from pyspark.sql import functions as F

        matches = catalogue.where(
            (F.col("environment_name") == env)
            & (F.col("table_id") == table_id)
            & (F.col("metadata_level") == "table")
        )
        if "is_active" in getattr(matches, "columns", ()):
            matches = matches.where(F.col("is_active") == F.lit(True))
        rows = matches.orderBy(F.col("last_profiled_at").desc_nulls_last()).limit(1).collect()
        return rows[0].asDict(recursive=True) if rows else None

    rows = observation_rows(catalogue)
    candidates = [
        row
        for row in rows
        if str(row.get("environment_name") or "") == env
        and str(row.get("table_id") or "") == table_id
        and str(row.get("metadata_level") or "") == "table"
        and row.get("is_active", True) is not False
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda row: str(row.get("last_profiled_at") or ""), reverse=True)
    return candidates[0]


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

def load_table_guardrail_rules(config, env: str, *, spark_session=None):
    """Load guardrail intent from the configured metadata target."""
    try:
        return read_lakehouse_table_core(
            GUARDRAIL_TABLE, target="metadata",
            schema=configured_lakehouse_schema(config, env, "metadata"),
            spark_session=spark_session, context={"config": config, "env": env},
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

def _json_dumps_stable(value) -> str:
    return json.dumps(value, default=str, sort_keys=True, separators=(",", ":"))

def _profile_hash(payload: dict) -> str:
    return hashlib.sha256(_json_dumps_stable(payload).encode("utf-8")).hexdigest()

def _schema_signature(dataframe) -> list[dict[str, str]]:
    columns, types = _actual_schema(dataframe)
    return [{"column_name": column, "data_type": types.get(column, "")} for column in columns]

def _profile_payload_from_profile(profile, *, dataframe=None, watermark_column: str = "", watermark_value: str = "") -> dict:
    normalized = _normalize_profile(profile) or {}
    columns = []
    for column in normalized.get("columns", []) or []:
        if not isinstance(column, dict):
            continue
        columns.append({
            "column_name": _string_value(column.get("column_name")),
            "data_type": _string_value(column.get("data_type")),
            "null_count": _string_value(column.get("null_count")),
            "distinct_count": _string_value(column.get("distinct_count")),
            "min_value": _string_value(column.get("min_value")),
            "max_value": _string_value(column.get("max_value")),
        })
    columns.sort(key=lambda item: item["column_name"])
    return {
        "row_count": _profile_row_count(profile),
        "schema_signature": _schema_signature(dataframe) if dataframe is not None else [],
        "columns": columns,
        "watermark_column": watermark_column or "",
        "watermark_value": watermark_value or "",
    }

def _select_profile_behavior_rule(rules_df, *, dataset_name: str, table_name: str, environment_name: str = "", metadata_table_key: str = "") -> dict | None:
    if rules_df is None:
        return None
    rows = rules_df.collect() if hasattr(rules_df, "collect") else ([rules_df] if isinstance(rules_df, dict) else rules_df)
    candidates = []
    for raw in rows or []:
        row = _row_to_dict(raw)
        if _string_value(_catalogue_value(row, "guardrail_type")).lower() != "profile_behavior":
            continue
        rule_environment = _string_value(_catalogue_value(row, "environment_name"))
        if rule_environment and environment_name and rule_environment != environment_name:
            continue
        if _string_value(_catalogue_value(row, "dataset_name")) != dataset_name:
            continue
        if _string_value(_catalogue_value(row, "table_name")) != table_name:
            continue
        rule_table_key = _string_value(_catalogue_value(row, "metadata_table_key"))
        if metadata_table_key and rule_table_key != metadata_table_key:
            continue
        if not _is_active_guardrail_rule(row):
            continue
        candidates.append(row)
    if not candidates:
        return None
    candidates.sort(key=lambda row: _string_value(_catalogue_value(row, "approved_at", "created_at", "_committed_at")), reverse=True)
    return candidates[0]

def _accepted_profile_rows(catalogue_df, *, environment_name: str, dataset_name: str, table_name: str, watermark_column: str, exclude_run_id: str | None = None) -> list[dict]:
    if catalogue_df is None:
        return []
    rows = catalogue_df.collect() if hasattr(catalogue_df, "collect") else ([catalogue_df] if isinstance(catalogue_df, dict) else catalogue_df)
    candidates = []
    for raw in rows or []:
        row = _row_to_dict(raw)
        if environment_name and _string_value(_catalogue_value(row, "environment_name")) not in {"", environment_name}:
            continue
        if _string_value(_catalogue_value(row, "dataset_name")) != dataset_name:
            continue
        if _string_value(_catalogue_value(row, "table_name", "profiled_table_name")) != table_name:
            continue
        if _string_value(_catalogue_value(row, "guardrail_type", "profile_guardrail_type")) not in {"", "profile_behavior"}:
            continue
        if _string_value(_catalogue_value(row, "watermark_column")) != _string_value(watermark_column):
            continue
        if exclude_run_id and _string_value(_catalogue_value(row, "profile_run_id", "run_id")) == str(exclude_run_id):
            continue
        if _string_value(_catalogue_value(row, "profile_status")).lower() not in {"", "success", "successful", "passed", "accepted"}:
            continue
        status = _string_value(_catalogue_value(row, "stability_status", "profile_behavior_status", "baseline_status")).lower()
        if status not in {"passed", "baseline_created", "accepted", "approved"}:
            continue
        candidates.append(row)
    candidates.sort(key=lambda row: (_string_value(_catalogue_value(row, "watermark_value")), _string_value(_catalogue_value(row, "profiled_at", "created_at")), _string_value(_catalogue_value(row, "profile_run_id", "run_id"))))
    latest = {}
    for row in candidates:
        latest[_string_value(_catalogue_value(row, "watermark_value"))] = row
    return list(latest.values())

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
            preset = {"strict": "strict", "relaxed": "allow_new_columns", "skip": "monitor_only"}.get(rule_type, "allow_new_columns")
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

def _normalize_profile(profile) -> dict | None:
    def row_value(row, *names):
        for name in names:
            if isinstance(row, dict) and name in row:
                return row.get(name)
            if hasattr(row, "asDict"):
                data = row.asDict(recursive=True)
                if name in data:
                    return data.get(name)
            if hasattr(row, name):
                return getattr(row, name)
        return None

    def distribution_payload(value):
        if value in (None, ""):
            return None
        if isinstance(value, dict):
            return value
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return None

    if profile is None:
        return None
    if isinstance(profile, dict) and "columns" in profile:
        return profile
    if hasattr(profile, "collect"):
        return _normalize_profile(profile.collect())
    if isinstance(profile, (list, tuple)):
        rows = list(profile)
        if not rows:
            return None
        first = rows[0]
        row_count = row_value(first, "row_count", "ROW_COUNT", "PROFILED_ROW_COUNT")
        table_name = row_value(first, "table_name", "TABLE_NAME", "PROFILED_TABLE_NAME")
        dataset_name = row_value(first, "dataset_name", "DATASET_NAME")
        profile_stage = row_value(first, "profile_stage", "PROFILE_STAGE", "EVIDENCE_ROLE")
        columns = []
        for row in rows:
            distribution_type = row_value(row, "distribution_type", "DISTRIBUTION_TYPE")
            distribution = distribution_payload(row_value(row, "distribution", "DISTRIBUTION", "distribution_json", "DISTRIBUTION_JSON"))
            column = {
                "column_name": row_value(row, "column_name", "COLUMN_NAME"),
                "data_type": row_value(row, "data_type", "DATA_TYPE"),
                "row_count": row_value(row, "row_count", "ROW_COUNT", "PROFILED_ROW_COUNT"),
                "null_count": row_value(row, "null_count", "NULL_COUNT"),
                "null_pct": row_value(row, "null_pct", "NULL_PCT", "null_percent", "NULL_PERCENT"),
                "distinct_count": row_value(row, "distinct_count", "DISTINCT_COUNT"),
                "distinct_pct": row_value(row, "distinct_pct", "DISTINCT_PCT", "distinct_percent", "DISTINCT_PERCENT"),
                "min_value": row_value(row, "min_value", "MIN_VALUE"),
                "max_value": row_value(row, "max_value", "MAX_VALUE"),
            }
            if distribution_type:
                column["distribution_type"] = distribution_type
            if distribution is not None:
                column["distribution"] = distribution
            columns.append(column)
        return {
            "dataset_name": dataset_name,
            "table_name": table_name,
            "profile_stage": profile_stage,
            "row_count": row_count,
            "columns": columns,
            "profile_status": row_value(first, "profile_status", "PROFILE_STATUS"),
            "baseline_status": row_value(first, "baseline_status", "BASELINE_STATUS"),
            "source_change_signal": distribution_payload(row_value(first, "source_change_signal", "SOURCE_CHANGE_SIGNAL_JSON")),
        }
    return profile

def _row_to_dict(row) -> dict:
    if row is None:
        return {}
    if isinstance(row, dict):
        return dict(row)
    if hasattr(row, "asDict"):
        return row.asDict(recursive=True)
    return {name: getattr(row, name) for name in dir(row) if not name.startswith("_")}

def _guardrail_exclude_columns(exclude_columns: list[str] | set[str] | tuple[str, ...] | None = None) -> set[str]:
    excluded = set(_DEFAULT_STABILITY_EXCLUDE_COLUMNS)
    if exclude_columns:
        excluded.update(str(column) for column in exclude_columns)
    return excluded

def _profile_row_count(profile) -> int | None:
    normalized = _normalize_profile(profile) or {}
    value = normalized.get("row_count")
    if value in (None, ""):
        columns = normalized.get("columns") or []
        if columns:
            first_column = columns[0] or {}
            if isinstance(first_column, dict):
                value = first_column.get("row_count")
    try:
        return int(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None

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

    Notes
    -----
    Freshness is separate from profile behavior. ``profile_mode="skip"`` only
    skips profile behavior enforcement; freshness still runs when configured.

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

def enforce_freshness(
    dataframe,
    freshness_column: str | None,
    max_lag_days: int | str | None,
    severity: str = "blocking",
    *,
    reference_date: date | datetime | str | None = None,
) -> dict:
    """Enforce freshness through the shared freshness-check implementation.

    This established public name remains compatible while
    :func:`check_freshness` provides the check-oriented API.
    """
    return freshness_check_core(
        dataframe,
        freshness_column,
        max_lag_days,
        severity=severity,
        reference_date=reference_date,
    )

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

def enforce_profile_behavior(
    spark,
    dataframe,
    metadata_table: str,
    dataset_name: str,
    table_name: str,
    *,
    stage: str,
    run_id: str,
    profile_mode: str | None = None,
    watermark_column: str | None = None,
    severity: str = "blocking",
    rule_key: str = "profile_behavior_default",
    exclude_columns: list[str] | set[str] | tuple[str, ...] | None = None,
    exclude_run_id: str | None = None,
    config=None,
    env: str | None = None,
    catalogue_df=None,
    current_profile=None,
    write_results: bool = True,
    rules_table: str = "METADATA_GUARDRAIL",
    rules_df=None,
    store_type: str = "lakehouse",
    layer: str = "",
    schema_name: str | None = None,
) -> dict:
    """Enforce profile behavior guardrails using catalogue evidence as baseline.

    Parameters
    ----------
    spark : Any
        Spark session used to read metadata when ``catalogue_df`` is not supplied.
    dataframe : Any
        Spark DataFrame being checked.
    metadata_table : str
        Metadata profiled evidence table, normally ``METADATA_DATA_PROFILED``.
    dataset_name : str
        Dataset identifier used for rule and baseline lookup.
    table_name : str
        Table identifier used for rule and baseline lookup.
    stage : str
        Pipeline stage used in returned evidence.
    run_id : str
        Current pipeline run identifier.
    profile_mode : {"static_data", "changing_data", "skip"}, optional
        Profile behavior mode. Defaults to ``"static_data"`` when no approved
        rule supplies a mode.
    watermark_column : str, optional
        Required for ``changing_data``. Values define independent profile groups.
    severity : {"blocking", "warning"}, default="blocking"
        Blocking failures stop continuation; warning failures report but allow continuation.
    rule_key : str, default="profile_behavior_default"
        Rule identifier written to guardrail result evidence when no approved
        rule row supplies one.
    exclude_columns : list-like, optional
        Business or technical columns to exclude from generated profile
        evidence.
    exclude_run_id : str, optional
        Run identifier to exclude from previous catalogue baseline lookup.
        Defaults to ``run_id``.
    config : object, optional
        Runtime configuration from ``00_env_config`` used to read metadata and
        write result evidence when paired with ``env``.
    env : str, optional
        Environment key used with ``config`` for configured metadata routing.
    catalogue_df : DataFrame or iterable of mappings, optional
        Preloaded ``METADATA_DATA_PROFILED`` evidence.
    current_profile : DataFrame or iterable of mappings, optional
        Current profile evidence for static mode.
    write_results : bool, default=True
        Whether to append runtime outcome rows to
        ``METADATA_GUARDRAIL_RESULTS`` when ``config`` and ``env`` are
        supplied.
    rules_table : str, default="METADATA_GUARDRAIL"
        Metadata table used to load approved profile behavior rules when
        ``rules_df`` is not supplied.
    rules_df : DataFrame or iterable of mappings, optional
        Preloaded guardrail rules. When supplied, no rules-table read is
        performed.
    store_type : str, default="lakehouse"
        Canonical physical store kind used for logical table identity.
    layer : str, optional
        Canonical configured store target used for logical table identity.
        Defaults to ``stage`` when omitted.
    schema_name : str, optional
        Canonical physical schema used for logical table identity.

    Returns
    -------
    dict
        Standard guardrail result plus catalogue profile evidence and comparison
        details suitable for ``METADATA_DATA_PROFILED`` and
        ``METADATA_GUARDRAIL_RESULTS``.

    Notes
    -----
    Baselines are never reset here. Current profile evidence is compared to the
    previous accepted or passed profiled evidence. Intentional blocked changes
    should be reviewed in governance or handled by superseding/resetting the
    relevant guardrail rule.


    """
    if rules_df is None and config is not None and env is not None:
        from fabricops_kit.io.shared import configured_lakehouse_schema, read_lakehouse_table_core
        try:
            rules_df = read_lakehouse_table_core(rules_table, target="metadata", schema=configured_lakehouse_schema(config, env, "metadata"), context={"config": config, "env": env}, spark_session=spark)
        except Exception as exc:
            if not _is_missing_table_error(exc):
                raise

    selected_rule = _select_profile_behavior_rule(rules_df, dataset_name=dataset_name, table_name=table_name, environment_name=env or "", metadata_table_key="")
    if selected_rule:
        rule_key = _string_value(_catalogue_value(selected_rule, "rule_key", "rule_id")) or rule_key
        severity = _catalogue_value(selected_rule, "severity") or severity
        profile_mode = profile_mode or _catalogue_value(selected_rule, "rule_type", "profile_mode")
        rule_parameters = _catalogue_value(selected_rule, "rule_parameters_json") or "{}"
        try:
            rule_parameters = json.loads(rule_parameters) if isinstance(rule_parameters, str) else dict(rule_parameters or {})
        except Exception:
            rule_parameters = {}
        watermark_column = watermark_column or rule_parameters.get("watermark_column") or _catalogue_value(selected_rule, "watermark_column", "column_name")

    mode = str(profile_mode or "static_data").lower().strip()
    normalized_severity = str(severity or "blocking").lower().strip()
    if normalized_severity not in {"blocking", "warning"}:
        raise ValueError("severity must be one of: blocking, warning")
    if mode not in {"static_data", "changing_data", "skip"}:
        raise ValueError("profile_mode must be one of: static_data, changing_data, skip")

    if catalogue_df is None and config is not None and env is not None:
        from fabricops_kit.io.shared import configured_lakehouse_schema, read_lakehouse_table_core
        try:
            catalogue_df = read_lakehouse_table_core(metadata_table, target="metadata", schema=configured_lakehouse_schema(config, env, "metadata"), context={"config": config, "env": env}, spark_session=spark)
        except Exception as exc:
            if _is_missing_table_error(exc):
                catalogue_df = None
            else:
                raise

    environment_name = env or ""
    evidence_rows: list[dict] = []
    if mode == "skip":
        message = "Profile behavior guardrail skipped; other guardrails still apply."
        return _apply_bypass_post_review_warning({"status": "skipped", "can_continue": True, "check_type": "profile_behavior", "guardrail_type": "profile_behavior", "rule_type": "skip", "stability_check_enabled": False, "profile_mode": "skip", "watermark_column": watermark_column or "", "stability_status": "skipped", "stability_can_continue": True, "stability_message": message, "message": message, "profile_evidence_rows": []}, selected_rule)

    effective_exclude_columns = _guardrail_exclude_columns(exclude_columns)
    if mode == "static_data":
        if current_profile is None:
            from fabricops_kit.pipeline.shared import build_profile_dataframe
            current_profile = build_profile_dataframe(dataframe, exclude_columns=effective_exclude_columns)
        payload = _profile_payload_from_profile(current_profile, dataframe=dataframe, watermark_column="", watermark_value="__FULL_TABLE__")
        evidence_rows.append({"watermark_column": "", "watermark_value": "__FULL_TABLE__", "row_count": payload.get("row_count"), "profile_payload_json": _json_dumps_stable(payload), "profile_hash": _profile_hash(payload)})
    else:
        if not watermark_column:
            raise ValueError("watermark_column is required for changing_data profile behavior")
        if not hasattr(dataframe, "filter") or not hasattr(dataframe, "select"):
            raise ValueError("changing_data profile behavior requires a Spark-like DataFrame")
        values = [row[0] for row in dataframe.select(watermark_column).distinct().collect()]
        from fabricops_kit.pipeline.shared import build_profile_dataframe
        for value in sorted(values, key=lambda item: str(item)):
            group_df = dataframe.filter(dataframe[watermark_column] == value)
            group_profile = build_profile_dataframe(group_df, exclude_columns=effective_exclude_columns)
            payload = _profile_payload_from_profile(group_profile, dataframe=group_df, watermark_column=watermark_column, watermark_value=_string_value(value))
            evidence_rows.append({"watermark_column": watermark_column, "watermark_value": _string_value(value), "row_count": payload.get("row_count"), "profile_payload_json": _json_dumps_stable(payload), "profile_hash": _profile_hash(payload)})

    previous = _accepted_profile_rows(catalogue_df, environment_name=environment_name, dataset_name=dataset_name, table_name=table_name, watermark_column=("" if mode == "static_data" else watermark_column or ""), exclude_run_id=exclude_run_id or run_id)
    previous_by_wm = {_string_value(_catalogue_value(row, "watermark_value")): row for row in previous}
    current_by_wm = {row["watermark_value"]: row for row in evidence_rows}
    differences = []
    for wm, baseline in previous_by_wm.items():
        if wm not in current_by_wm:
            differences.append({"difference_type": "missing_watermark_value", "watermark_value": wm})
            continue
        old_hash = _string_value(_catalogue_value(baseline, "profile_hash"))
        new_hash = current_by_wm[wm]["profile_hash"]
        if old_hash and old_hash != new_hash:
            differences.append({"difference_type": "profile_changed", "watermark_value": wm, "expected_profile_hash": old_hash, "actual_profile_hash": new_hash})
    new_groups = [wm for wm in current_by_wm if wm not in previous_by_wm]

    if not previous:
        status = "baseline_created"
        can_continue = True
        message = "No previous accepted profile_behavior evidence was available; current profile establishes the profiled baseline."
    elif differences:
        status = "failed" if normalized_severity == "blocking" else "warning"
        can_continue = normalized_severity == "warning"
        message = "Profile behavior changed versus previous accepted profiled evidence. Review and approve the change in governance, or supersede/reset the relevant guardrail rule if intentional."
    else:
        status = "passed"
        can_continue = True
        message = "Profile behavior guardrail passed."

    result_payload = {"profile_mode": mode, "differences": differences, "new_watermark_values": new_groups, "profile_evidence_rows": evidence_rows}
    result = {
        "status": status,
        "can_continue": can_continue,
        "check_type": "profile_behavior",
        "guardrail_type": "profile_behavior",
        "rule_type": mode,
        "severity": normalized_severity,
        "rule_key": rule_key,
        "stability_check_enabled": True,
        "profile_mode": mode,
        "watermark_column": watermark_column or "",
        "watermark_value": "__FULL_TABLE__" if mode == "static_data" else "",
        "row_count": sum(int(row.get("row_count") or 0) for row in evidence_rows),
        "profile_hash": evidence_rows[0]["profile_hash"] if len(evidence_rows) == 1 else _profile_hash({"groups": evidence_rows}),
        "profile_payload_json": _json_dumps_stable(result_payload),
        "baseline_run_id": _string_value(_catalogue_value(previous[0], "profile_run_id", "run_id")) if previous else "",
        "baseline_row_count": _catalogue_value(previous[0], "row_count") if len(previous) == 1 else None,
        "baseline_watermark_min_value": "",
        "baseline_watermark_max_value": "",
        "stability_status": status,
        "stability_can_continue": can_continue,
        "stability_message": message,
        "stability_difference_summary": json.dumps(differences, default=str, sort_keys=True) if differences else "",
        "message": message,
        "profile_evidence_rows": evidence_rows,
        "expected_value_json": json.dumps({"previous": previous_by_wm}, default=str, sort_keys=True),
        "actual_value_json": json.dumps({"current": current_by_wm}, default=str, sort_keys=True),
        "result_payload_json": json.dumps(result_payload, default=str, sort_keys=True),
    }
    result = _apply_bypass_post_review_warning(result, selected_rule)

    if write_results and config is not None and env is not None:
        try:
                        write_guardrail_result_row(
                spark_session=spark, config=config, env=env, run_id=run_id,
                dataset_name=dataset_name, table_name=table_name,
                store_type=store_type, layer=layer or stage, schema_name=schema_name,
                guardrail_type="profile_behavior", rule_type=mode, result=result, rule_key=rule_key,
            )
        except Exception as exc:
            if not _is_missing_table_error(exc):
                raise
    return result

def _is_missing_table_error(exc: Exception) -> bool:
    text = str(exc).lower()
    patterns = ["not found", "table or view not found", "no such table", "cannot resolve", "missing"]
    return any(pattern in text for pattern in patterns)

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
    target: str,
    store_type: str,
    schema_name: str | None,
    dataset_name: str = "",
    run_id: str = "",
    row_identity_columns: list[str] | None = None,
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
    metadata_table_key = build_metadata_table_key(store_type, target, schema_name, table_name)
    metadata_df = _read_guardrail_rule_metadata(config, env, spark_session=spark_session)
    rules = _load_active_dq_rules(metadata_df, metadata_table_key, env=env, dataset_name=dataset_name or None)
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

def run_active_dq_guardrail(
    dataframe,
    config,
    env,
    dataset_name,
    table_name,
    *,
    spark_session=None,
    run_id: str = "",
    write_results: bool = False,
    store_type: str = "lakehouse",
    layer: str = "",
    schema_name: str | None = None,
) -> dict:
    """Enforce active DQ guardrail rules as a simple pipeline guardrail.

    Parameters
    ----------
    dataframe : Any
        Spark DataFrame to evaluate before the target write. The full DataFrame
        is never filtered or split by this helper.
    config : FrameworkConfig or dict
        Runtime configuration containing the configured metadata lakehouse
        route from ``00_env_config``.
    env : str
        Environment name used to read ``METADATA_GUARDRAIL`` from the
        configured metadata target.
    dataset_name : str
        Dataset identifier used with ``table_name`` to scope active DQ guardrail rules
        when those columns exist in the metadata table.
    table_name : str
        Target table name whose active DQ guardrail rules should be enforced.
    spark_session : pyspark.sql.SparkSession, optional
        Spark session used to read metadata when required by the configured
        storage helper.
    run_id : str, optional
        Pipeline run identifier written to runtime result evidence.
    write_results : bool, default=False
        Whether to append the aggregate DQ runtime outcome to
        ``METADATA_GUARDRAIL_RESULTS`` when a Spark session is available.
    store_type : str, default="lakehouse"
        Canonical physical store kind used for logical table identity.
    layer : str, optional
        Canonical configured store target used for logical table identity.
    schema_name : str, optional
        Canonical physical schema used for logical table identity.

    Returns
    -------
    dict
        Guardrail result with ``status``, ``can_continue``, ``checks``, and
        ``message``. The result also carries the full tagged ``dataframe`` and
        aggregate ``summary`` fields for runtime result evidence.
        Error-severity rule failures return ``status='failed'`` and
        ``can_continue=False``. Warning-severity failures return
        ``status='warning'`` and ``can_continue=True``. Passing or absent rules
        return ``status='passed'`` and ``can_continue=True``.

    Notes
    -----
    This v1 guardrail reads active DQ guardrail rules from
    ``METADATA_GUARDRAIL`` via the configured metadata route and writes the aggregate runtime
    outcome to ``METADATA_GUARDRAIL_RESULTS`` when result writing is enabled. It
    does not quarantine rows, write row-level failure metadata, filter invalid
    rows, send alerts, or partially write targets.

    """
    metadata_df = _read_guardrail_rule_metadata(config, env, spark_session=spark_session)
    metadata_table_key = build_metadata_table_key(store_type, layer, schema_name, table_name)
    rules = _load_active_dq_rules(metadata_df, metadata_table_key, env=env, dataset_name=dataset_name)
    checks = _run_dq_guardrail_checks(dataframe, table_name=table_name, rules=rules) if rules else []
    total_count = int(dataframe.count())
    failed_row_count = 0
    if rules:
        _, F, _ = _spark_sql_helpers()
        failed_columns = [
            F.when(_dq_failed_expression(dataframe, rule), F.lit(1)).otherwise(F.lit(0))
            for rule in rules
        ]
        failed_row = failed_columns[0]
        for column in failed_columns[1:]:
            failed_row = failed_row + column
        failed_rows = dataframe.select(
            F.when(failed_row > F.lit(0), F.lit(1)).otherwise(F.lit(0)).alias("failed")
        )
        failed_row_count = int(
            failed_rows.agg(F.sum("failed").alias("failed_count")).collect()[0]["failed_count"] or 0
        )
    result = _summarize_dq_guardrail(checks)
    if any(str(rule.get("review_status") or "").lower() == "active_pending_governance_review" for rule in rules):
        warning = "Rule is active through approval bypass and requires governance post-review."
        result["reason"] = warning if not result.get("reason") else f"{result.get('reason')} {warning}"
        result["bypass_warning"] = warning
    result["dataframe"] = _dq_tagged_dataframe(dataframe, rules)
    failed_checks = [check for check in checks if not bool(check.get("passed", False))]
    warning_checks = [check for check in failed_checks if check.get("severity") == "warning"]
    error_checks = [check for check in failed_checks if check.get("severity") == "error"]
    result["summary"] = {
        "DQ_STATUS": result["status"],
        "DQ_RULE_COUNT": len(checks),
        "DQ_FAILED_RULE_COUNT": len(failed_checks),
        "DQ_WARNING_RULE_COUNT": len(warning_checks),
        "DQ_ERROR_RULE_COUNT": len(error_checks),
        "DQ_FAILED_ROW_COUNT": failed_row_count,
        "DQ_FAILED_ROW_PERCENT": float(round((failed_row_count / total_count) * 100, 4)) if total_count else 0.0,
        "DQ_CHECKED_AT": get_current_audit_timestamp(config=config, drop_microseconds=False),
    }
    if write_results:
        write_guardrail_result_row(
            spark_session=spark_session,
            config=config,
            env=env,
            run_id=run_id,
            dataset_name=dataset_name,
            table_name=table_name,
            store_type=store_type,
            layer=layer,
            schema_name=schema_name,
            guardrail_type="dq",
            rule_type="active_rules",
            result=result,
            rule_key="dq_active_rules",
        )
    return result

def _prepare_dq_profile_input_rows(*, profile_df=None, df=None, table_name: str, business_context: str = "", config: Any = None):
    """Prepare DQ profile rows from a profile DataFrame or raw DataFrame."""
    if (profile_df is None) == (df is None):
        raise ValueError("Provide exactly one of profile_df or df.")
    if profile_df is None:
        profile_df = build_profile_dataframe(df)
    cols = set(profile_df.columns)
    if {"column_name", "data_type", "row_count", "null_count", "distinct_count"}.issubset(cols):
        return profile_df
    _, F, _ = _spark_sql_helpers()
    return profile_df.select(
        F.col("TABLE_NAME").alias("table_name"),
        F.col("COLUMN_NAME").alias("column_name"),
        F.col("DATA_TYPE").alias("data_type"),
        F.col("ROW_COUNT").alias("row_count"),
        F.col("NULL_COUNT").alias("null_count"),
        F.col("NULL_PERCENT").alias("null_percent"),
        F.col("DISTINCT_COUNT").alias("distinct_count"),
        F.col("DISTINCT_PERCENT").alias("distinct_percent"),
        F.col("MIN_VALUE").alias("min_value"),
        F.col("MAX_VALUE").alias("max_value"),
        F.lit("").alias("observed_values_sample"),
        F.lit(business_context).alias("business_context"),
        F.lit(get_current_audit_timestamp(config=config, drop_microseconds=False)).alias("profile_timestamp"),
    )


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

def _read_dq_rule_metadata(config: Any, env: str, *, spark_session: Any = None):
    frame = load_table_guardrail_rules(config, env, spark_session=spark_session)
    if "guardrail_type" in set(getattr(frame, "columns", [])):
        _, F, _ = _spark_sql_helpers()
        return frame.filter(
            F.lower(F.coalesce(F.col("guardrail_type"), F.lit(""))) == "dq"
        )
    return frame
