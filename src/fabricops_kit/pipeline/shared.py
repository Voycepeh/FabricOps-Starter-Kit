"""Shared pipeline implementation helpers."""

from __future__ import annotations

import json
from typing import Any, Mapping

from fabricops_kit.config.shared import build_audit_timestamp_expr, get_audit_timezone, get_current_audit_timestamp, resolve_fabric_context
from ..io.shared import configured_lakehouse_schema, write_lakehouse_table_core
from ..config.audit import _audit_timestamp_value, build_runtime_audit_fields
from ..config.metadata_keys import _build_metadata_table_key
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


def _numeric_bin_edges(df, column_name: str, *, bin_count: int = 10) -> list[float]:
    values = df.select(column_name).where(f"`{column_name}` is not null")
    try:
        quantiles = values.approxQuantile(column_name, [i / bin_count for i in range(bin_count + 1)], 0.01)
    except Exception:
        return []
    edges: list[float] = []
    for value in quantiles:
        if value is not None and (not edges or float(value) > edges[-1]):
            edges.append(float(value))
    return edges if len(edges) >= 2 else []


def _build_numeric_distribution(df, column_name: str, edges: list[float]) -> dict[str, list[float] | list[int]] | None:
    from pyspark.sql import functions as F

    cleaned_edges: list[float] = []
    for edge in edges:
        value = float(edge)
        if not cleaned_edges or value > cleaned_edges[-1]:
            cleaned_edges.append(value)
    if len(cleaned_edges) < 2:
        return None

    bucket_expr = None
    numeric_value = F.col(column_name).cast("double")
    for index, (lower, upper) in enumerate(zip(cleaned_edges[:-1], cleaned_edges[1:])):
        if index == 0:
            condition = numeric_value < F.lit(upper)
        elif index == len(cleaned_edges) - 2:
            condition = numeric_value >= F.lit(lower)
        else:
            condition = (numeric_value >= F.lit(lower)) & (numeric_value < F.lit(upper))
        bucket_expr = F.when(condition, F.lit(index)) if bucket_expr is None else bucket_expr.when(condition, F.lit(index))

    bucketed = df.where(F.col(column_name).isNotNull()).select(bucket_expr.alias("_profile_bucket"))
    rows = bucketed.where(F.col("_profile_bucket").isNotNull()).groupBy("_profile_bucket").count().collect()
    counts = [0 for _ in range(len(cleaned_edges) - 1)]
    for row in rows:
        bucket = int(row["_profile_bucket"])
        if 0 <= bucket < len(counts):
            counts[bucket] = int(row["count"])
    return {"bin_edges": cleaned_edges, "bin_counts": counts}


def _build_categorical_distribution(
    df,
    column_name: str,
    *,
    top_n: int = 20,
    categories: list[str] | set[str] | tuple[str, ...] | None = None,
) -> dict[str, Any] | None:
    from pyspark.sql import functions as F

    non_null = df.where(F.col(column_name).isNotNull())
    total_count = int(non_null.agg(F.count(F.lit(1)).alias("total_count")).collect()[0]["total_count"])
    if total_count == 0:
        return None

    if categories is not None:
        selected_categories = [str(category) for category in categories]
        if not selected_categories:
            return {"category_counts": {}, "other_count": total_count, "new_categories": []}
        grouped = non_null.groupBy(F.col(column_name).cast("string").alias("_profile_category")).count()
        rows = grouped.where(F.col("_profile_category").isin(selected_categories)).collect()
        category_counts = {category: 0 for category in selected_categories}
        for row in rows:
            category_counts[str(row["_profile_category"])] = int(row["count"])
        kept_count = int(sum(category_counts.values()))
        new_rows = grouped.where(~F.col("_profile_category").isin(selected_categories)).orderBy(F.col("count").desc(), F.col("_profile_category").asc()).limit(top_n).collect()
        return {
            "category_counts": category_counts,
            "other_count": max(total_count - kept_count, 0),
            "new_categories": [str(row["_profile_category"]) for row in new_rows],
        }

    grouped = non_null.groupBy(F.col(column_name).cast("string").alias("_profile_category")).count().orderBy(F.col("count").desc(), F.col("_profile_category").asc())
    rows = grouped.limit(top_n).collect()
    if not rows:
        return None
    category_counts = {str(row["_profile_category"]): int(row["count"]) for row in rows}
    return {"category_counts": category_counts, "other_count": max(total_count - int(sum(category_counts.values())), 0)}


def build_distribution_summaries(
    df,
    eligible_columns: list[str],
    dtype_map: dict[str, str],
    *,
    include_distributions: bool,
    distribution_columns: list[str] | set[str] | tuple[str, ...] | None,
    distribution_bin_edges: dict[str, list[float]] | None,
    categorical_categories: dict[str, list[str]] | None,
    categorical_top_n: int,
) -> dict[str, tuple[str, dict[str, Any]]]:
    """Build optional numeric and categorical distribution summaries."""
    if not include_distributions:
        return {}

    selected = set(distribution_columns) if distribution_columns is not None else set(eligible_columns)
    summaries: dict[str, tuple[str, dict[str, Any]]] = {}
    for column_name in eligible_columns:
        if column_name not in selected:
            continue
        lowered_type = (dtype_map[column_name] or "").lower()
        if any(token in lowered_type for token in ("tinyint", "smallint", "int", "bigint", "float", "double", "decimal")):
            edges = (distribution_bin_edges or {}).get(column_name) or _numeric_bin_edges(df, column_name)
            distribution = _build_numeric_distribution(df, column_name, edges)
            if distribution is not None:
                summaries[column_name] = ("numeric", distribution)
        elif any(token in lowered_type for token in ("string", "char", "varchar", "boolean")):
            distribution = _build_categorical_distribution(df, column_name, top_n=categorical_top_n, categories=(categorical_categories or {}).get(column_name))
            if distribution is not None:
                summaries[column_name] = ("categorical", distribution)
    return summaries


def profile_dataframe_core(
    df,
    table_name: str,
    *,
    exclude_columns=None,
    run_timestamp_timezone: str | None = None,
    config: Any = None,
    include_distributions: bool = False,
    distribution_columns: list[str] | set[str] | tuple[str, ...] | None = None,
    distribution_bin_edges: dict[str, list[float]] | None = None,
    categorical_categories: dict[str, list[str]] | None = None,
    categorical_top_n: int = 20,
):
    """Build canonical DQ-ready profiling rows from a Spark DataFrame."""
    from pyspark.sql import functions as F

    run_timestamp_timezone = get_audit_timezone(config=config, timezone_name=run_timestamp_timezone)
    eligible_columns = resolve_profiled_columns(df, exclude_columns=exclude_columns)
    if not eligible_columns:
        raise ValueError("No eligible non-technical columns found for metadata profiling.")

    dtype_map = dict(df.dtypes)
    row_count = int(df.count())
    distributions = build_distribution_summaries(
        df,
        eligible_columns,
        dtype_map,
        include_distributions=include_distributions,
        distribution_columns=distribution_columns,
        distribution_bin_edges=distribution_bin_edges,
        categorical_categories=categorical_categories,
        categorical_top_n=categorical_top_n,
    )

    agg_exprs = []
    for column_name in eligible_columns:
        agg_exprs.append(F.sum(F.col(column_name).isNull().cast("int")).alias(f"{column_name}_NULL_COUNT"))
        agg_exprs.append(F.countDistinct(F.col(column_name)).alias(f"{column_name}_DISTINCT_COUNT"))
        if is_min_max_supported_type(dtype_map[column_name]):
            agg_exprs.append(F.min(F.col(column_name)).alias(f"{column_name}_MIN"))
            agg_exprs.append(F.max(F.col(column_name)).alias(f"{column_name}_MAX"))

    agg_df = df.agg(*agg_exprs)
    denominator = F.lit(row_count if row_count > 0 else 1).cast("double")

    rows = []
    for column_name in eligible_columns:
        select_exprs = [
            F.lit(table_name).alias("TABLE_NAME"),
            build_audit_timestamp_expr(timezone_name=run_timestamp_timezone).alias("RUN_TIMESTAMP"),
            F.lit(column_name).alias("COLUMN_NAME"),
            F.lit(dtype_map[column_name]).alias("DATA_TYPE"),
            F.lit(row_count).cast("long").alias("ROW_COUNT"),
            F.coalesce(F.col(f"{column_name}_NULL_COUNT"), F.lit(0)).cast("long").alias("NULL_COUNT"),
            F.round((F.coalesce(F.col(f"{column_name}_NULL_COUNT"), F.lit(0)).cast("double") / denominator) * 100, 3).alias("NULL_PERCENT"),
            F.coalesce(F.col(f"{column_name}_DISTINCT_COUNT"), F.lit(0)).cast("long").alias("DISTINCT_COUNT"),
            F.round((F.coalesce(F.col(f"{column_name}_DISTINCT_COUNT"), F.lit(0)).cast("double") / denominator) * 100, 3).alias("DISTINCT_PERCENT"),
            F.col(f"{column_name}_MIN").cast("string").alias("MIN_VALUE") if f"{column_name}_MIN" in agg_df.columns else F.lit(None).cast("string").alias("MIN_VALUE"),
            F.col(f"{column_name}_MAX").cast("string").alias("MAX_VALUE") if f"{column_name}_MAX" in agg_df.columns else F.lit(None).cast("string").alias("MAX_VALUE"),
        ]
        if include_distributions:
            distribution_type, distribution_payload = distributions.get(column_name, (None, None))
            select_exprs.extend(
                [
                    F.lit(distribution_type).cast("string").alias("DISTRIBUTION_TYPE"),
                    F.lit(json.dumps(distribution_payload, sort_keys=True) if distribution_payload is not None else None).cast("string").alias("DISTRIBUTION_JSON"),
                ]
            )
        rows.append(agg_df.select(*select_exprs))

    out = rows[0]
    for next_row in rows[1:]:
        out = out.unionByName(next_row)
    return out

from fabricops_kit.pipeline.guardrails_shared import _run_active_dq_guardrail
from fabricops_kit.pipeline.guardrails_shared import (
    enforce_freshness,
    enforce_freshness_rule,
    enforce_profile_behavior,
    stop_if_failed,
    _check_schema_runtime,
    _check_schema_rule_runtime,
)
CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
LINEAGE_TABLE = "METADATA_DATA_LINEAGE_TABLE"
METADATA_PIPELINE_RUNS_TABLE = "METADATA_PIPELINE_RUNS"
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


def _runtime_audit_fields(config: Any, env: str) -> dict[str, str]:
    try:
        return build_runtime_audit_fields(config=config, env=env)
    except Exception:
        return {
            "_committed_at": _timestamp_value(config=config),
            "_committed_by": "unknown",
            "_workspace_name": "",
            "_notebook_name": "",
            "_metadata_lakehouse_name": "",
            "_activity_id": "",
        }


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


def _prepare_pipeline_table_configs_workflow(
    table_configs: list[dict[str, Any]],
    default_settings: Mapping[str, Any],
    *,
    table_role: str,
    run_id: str = "",
    pipeline_name: str = "",
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """Prepare source or target table configs for a pipeline notebook.

    Parameters
    ----------
    table_configs : list of dict
        User-authored table config dictionaries from ``SOURCE_TABLES`` or
        ``TARGET_TABLES``.
    default_settings : mapping
        Default guardrails, and for targets write options, merged before each
        table config. Table-specific values take precedence.
    table_role : {"source", "target"}
        Role-specific preparation mode. Source mode validates that each config
        already includes a DataFrame; target mode adds FabricOps audit columns
        and derives write metadata.
    run_id : str, optional
        Pipeline run identifier used for target audit columns. Required for
        target role.
    pipeline_name : str, optional
        Pipeline name used for target audit columns. Required for target role.

    Returns
    -------
    tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]
        Enriched table configs and a lookup keyed by table ``key``.

    Raises
    ------
    ValueError
        If ``table_role`` is not ``"source"`` or ``"target"``.

    Notes
    -----
    Source configs derive ``dataset_name`` from ``table_name`` and ``stage`` from
    ``layer``. Source
    DataFrames must be loaded directly in the notebook with the existing
    FabricOps read helpers and supplied in each source config as ``df``.

    Target configs derive ``dataset_name``, ``stage``, ``target_layer``,
    ``target_name``, and ``target_kind`` unless overridden, then add standard
    FabricOps audit columns.

    """
    normalized_role = str(table_role or "").lower().strip()
    if normalized_role not in {"source", "target"}:
        raise ValueError("table_role must be 'source' or 'target'.")

    enriched_tables: list[dict[str, Any]] = []
    for table_config in table_configs:
        merged_config = {**default_settings, **table_config}
        dataset_name = merged_config.get("dataset_name", merged_config["table_name"])
        stage = merged_config.get("stage", merged_config["layer"])
        if normalized_role == "source":
            if "df" not in merged_config:
                table_key = merged_config.get("key", merged_config.get("table_name", "<unknown>"))
                raise ValueError(
                    "Source table config "
                    f"{table_key!r} must include a pre-loaded DataFrame in the 'df' key. "
                    "Load the source with read_lakehouse_table, read_lakehouse_csv, "
                    "read_lakehouse_parquet, read_lakehouse_excel, read_warehouse_table, "
                    "or spark.read.table before calling prepare_pipeline_table_configs."
                )
            enriched_table = {
                **merged_config,
                "dataset_name": dataset_name,
                "stage": stage,
            }
        else:
            from pyspark.sql import functions as F

            target_layer = merged_config.get("target_layer", merged_config["layer"])
            target_name = merged_config.get("target_name", merged_config["table_name"])
            target_kind = merged_config.get("target_kind", merged_config.get("kind", "lakehouse"))
            audit_created_at = get_current_audit_timestamp(
                config=merged_config.get("config", default_settings.get("config"))
            )
            audited_df = (
                merged_config["df"]
                .withColumn("_fabricops_run_id", F.lit(run_id))
                .withColumn("_fabricops_pipeline_name", F.lit(pipeline_name))
                .withColumn("_fabricops_created_at", F.lit(audit_created_at))
            )
            enriched_table = {
                **merged_config,
                "df": audited_df,
                "dataset_name": dataset_name,
                "stage": stage,
                "target_layer": target_layer,
                "target_name": target_name,
                "target_kind": target_kind,
            }
        enriched_tables.append(enriched_table)

    return enriched_tables, {table_config["key"]: table_config for table_config in enriched_tables}


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
    agreement_contract_version: str = "",
    notebook_registry_id: str = "",
    notebook_id: str = "",
    pipeline_name: str = "",
    table_role: str = "",
    mode: str = "profile",
    stop_on_failure: bool | None = None,
) -> dict[str, Any]:
    """Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails.

    Parameters
    ----------
    table_configs : list of dict
        Source or target table configs. Each config must contain ``key``,
        ``df``, and ``expected_schema``. Optional keys such as
        ``dataset_name``, ``stage``, ``schema_preset``, ``profile_mode``,
        ``profile_behavior_severity``, ``watermark_column``, ``dq_preset``,
        ``distribution_columns``, and ``exclude_columns`` control the guardrail
        behavior.
    run_id : str, optional
        Current pipeline run identifier. When omitted, the active context from
        :func:`widget_pipeline_bootstrap` is used.
    spark_session : Any, optional
        Spark session used by profile behavior and DQ helpers. When omitted,
        the active context from :func:`widget_pipeline_bootstrap` is used.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.
    agreement_id, agreement_contract_version, notebook_registry_id, notebook_id, pipeline_name : str, optional
        Governance context written with catalogue evidence. Omitted values are
        resolved from the active context when available.
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
        results, profile behavior results, DQ results, catalogue status, evidence definitions, concise
        ``summary``, ``can_continue``, and ``failed_tables``. Results remain
        separated by table key and guardrail type.

    Notes
    -----
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
        run_id = run_id or active.run_id
        spark_session = spark_session if spark_session is not None else active.spark_session
        pipeline_name = pipeline_name or active.pipeline_name
        notebook_id = notebook_id or active.notebook_id
        notebook_registry_id = notebook_registry_id or active.notebook_registry_id
        agreement_id = agreement_id or active.agreement_id
        agreement_contract_version = agreement_contract_version or active.agreement_contract_version
    if not run_id:
        raise ValueError("run_id is required unless widget_pipeline_bootstrap has established an active context.")
    if spark_session is None:
        raise ValueError("spark_session is required unless widget_pipeline_bootstrap has established an active context.")
    normalized_mode = str(mode or "profile").lower().strip()
    if normalized_mode not in {"profile", "enforce"}:
        raise ValueError("mode must be one of: profile, enforce.")
    if stop_on_failure is None:
        stop_on_failure = normalized_mode == "enforce"

    config, env, resolved_context = resolve_fabric_context(context=context)
    profiles: dict[str, Any] = {}
    schema_results: dict[str, Mapping[str, Any]] = {}
    freshness_results: dict[str, Mapping[str, Any]] = {}
    stability_results: dict[str, Mapping[str, Any]] = {}
    dq_results: dict[str, Mapping[str, Any]] = {}
    failed_tables: list[str] = []
    evidence_definitions = _build_guardrail_evidence_definitions(table_configs)

    for table_config in table_configs:
        table_key = _table_key(table_config)
        table_name = _table_name(table_config)
        dataset_name = table_config.get("dataset_name", table_name)
        stage = table_config.get("stage", "target")
        dataframe = table_config["df"]

        profiles[table_key] = profile_dataframe_core(
            dataframe,
            table_name=table_name,
            # profile_dataframe automatically excludes FabricOps/DQ technical annotation columns
            # and unions those defaults with any table-specific exclude_columns.
            exclude_columns=table_config.get("exclude_columns"),
            include_distributions=True,
            distribution_columns=table_config.get("distribution_columns"),
            config=config,
            run_timestamp_timezone=table_config.get("run_timestamp_timezone"),
        )

        guardrail_rules_df = table_config.get("guardrail_rules_df")
        schema_rules_df = table_config.get("schema_rules_df", guardrail_rules_df)
        freshness_rules_df = table_config.get("freshness_rules_df", guardrail_rules_df)
        if schema_rules_df is not None:
            schema_results[table_key] = _check_schema_rule_runtime(
                dataframe,
                schema_rules_df,
                dataset_name=dataset_name,
                table_name=table_name,
                environment_name=env,
                metadata_table_key=_build_metadata_table_key(env, dataset_name, table_name),
            )
        else:
            schema_results[table_key] = _check_schema_runtime(
                dataframe,
                table_config["expected_schema"],
                preset=table_config.get("schema_preset", "strict"),
            )

        if freshness_rules_df is not None:
            freshness_results[table_key] = enforce_freshness_rule(
                dataframe,
                freshness_rules_df,
                dataset_name=dataset_name,
                table_name=table_name,
                environment_name=env,
                metadata_table_key=_build_metadata_table_key(env, dataset_name, table_name),
            )
        else:
            freshness_results[table_key] = enforce_freshness(
                dataframe,
                table_config.get("freshness_column"),
                table_config.get("freshness_max_lag_days"),
                severity=table_config.get("freshness_severity", "blocking"),
            )

        stability_results[table_key] = enforce_profile_behavior(
            spark_session,
            dataframe,
            CATALOGUE_TABLE,
            dataset_name,
            table_name,
            stage=stage,
            run_id=run_id,
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
            rules_table=table_config.get("profile_behavior_rules_table", "METADATA_GUARDRAIL_RULES"),
            rules_df=table_config.get("profile_behavior_rules_df", guardrail_rules_df),
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
                run_id=run_id,
                write_results=False,
            )

        if "dataframe" in dq_results[table_key]:
            table_config["df"] = dq_results[table_key]["dataframe"]

        if table_config.get("write_guardrail_results", True) and hasattr(spark_session, "createDataFrame"):
            for guardrail_type, rule_type, guardrail_result in (
                ("schema", table_config.get("schema_preset", "strict"), schema_results[table_key]),
                ("freshness", table_config.get("freshness_column", "freshness"), freshness_results[table_key]),
                ("dq", table_config.get("dq_preset", "active_rules"), dq_results[table_key]),
            ):
                _write_guardrail_result_row(
                    spark_session=spark_session,
                    config=config,
                    env=env,
                    run_id=run_id,
                    dataset_name=dataset_name,
                    table_name=table_name,
                    guardrail_type=guardrail_type,
                    rule_type=str(rule_type or guardrail_type),
                    result=guardrail_result,
                )

        table_can_continue = all(
            bool((result or {}).get("can_continue", True))
            for result in (
                schema_results[table_key],
                freshness_results[table_key],
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
        agreement_id=agreement_id,
        agreement_contract_version=agreement_contract_version,
        notebook_registry_id=notebook_registry_id,
        notebook_id=notebook_id,
        pipeline_name=pipeline_name,
        schema_results=schema_results,
        freshness_results=freshness_results,
        stability_results=stability_results,
        dq_results=dq_results,
    )

    summary = {
        "schema_results": schema_results,
        "freshness_results": freshness_results,
        "stability_results": stability_results,
        "dq_results": dq_results,
        "catalogue_status": catalogue_status,
        "failed_tables": failed_tables,
    }
    result = {
        "profiles": profiles,
        "schema_results": schema_results,
        "freshness_results": freshness_results,
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
    agreement_id: str = "",
    agreement_contract_version: str = "",
    notebook_registry_id: str = "",
    notebook_id: str = "",
    pipeline_name: str = "",
    schema_results: Mapping[str, Mapping[str, Any]] | None = None,
    freshness_results: Mapping[str, Mapping[str, Any]] | None = None,
    stability_results: Mapping[str, Mapping[str, Any]] | None = None,
    dq_results: Mapping[str, Mapping[str, Any]] | None = None,
    metadata_table: str = CATALOGUE_TABLE,
    mode: str = "append",
) -> dict[str, str]:
    """Write observed profile evidence to the metadata data catalogue.

    Parameters
    ----------
    profiles : mapping of str to DataFrame
        Profile DataFrames produced by ``profile_dataframe`` for each dataset.
    dataset_definitions : mapping of str to mapping
        Source or target definitions containing table, stage, and layer context.
    config, env : object, str
        Metadata lakehouse route from ``00_env_config``.
    run_id : str, optional
        Pipeline run identifier. When omitted, the active context from
        :func:`widget_pipeline_bootstrap` is used.
    agreement_id, agreement_contract_version, notebook_registry_id, notebook_id, pipeline_name : str, optional
        Governance context added to each catalogue row.
    schema_results, freshness_results, stability_results, dq_results : mapping, optional
        Runtime guardrail results are accepted by this writer but are not
        written to ``METADATA_DATA_CATALOGUE``.
    metadata_table : str, default="METADATA_DATA_CATALOGUE"
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
    audit = _runtime_audit_fields(config, env)
    statuses: dict[str, str] = {}
    for name, profile_df in profiles.items():
        definition = dataset_definitions[name]
        table_name = _definition_name(name, definition)
        dataset_name = str(definition.get("dataset_name") or table_name)
        stage = str(definition.get("stage", "target"))
        stability_result = dict((stability_results or {}).get(name) or {})
        base_evidence = _canonical_catalogue_profile_df(profile_df)
        metadata_table_key = _build_metadata_table_key(env, dataset_name, table_name)
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
        fabric_store_target = str(
            definition.get(
                "fabric_store_target",
                definition.get("target_layer", definition.get("layer", "")),
            )
        ).strip().lower()
        additions = {
            "metadata_table_key": metadata_table_key,
            "environment_name": env,
            "dataset_name": dataset_name,
            "table_name": table_name,
            "layer": str(definition.get("layer", "")),
            "fabric_store_target": fabric_store_target,
            "asset_kind": str(definition.get("kind", "lakehouse")),
            "pipeline_name": pipeline_name,
            "profile_run_id": run_id,
            "profile_stage": stage,
            "profile_status": "success",
            "profiled_at": _now_iso(config),
            "agreement_id": agreement_id,
            "contract_version": agreement_contract_version,
            "notebook_registry_id": notebook_registry_id,
            "notebook_id": notebook_id,
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


def _write_pipeline_lineage_workflow(
    *,
    spark: Any,
    run_id: str,
    context: dict[str, Any] | None = None,
    source_definitions: Mapping[str, Mapping[str, Any]],
    target_definitions: Mapping[str, Mapping[str, Any]],
    relationships: list[Mapping[str, Any]] | None = None,
    dataset_name: str = "",
    agreement_id: str = "",
    agreement_contract_version: str = "",
    notebook_registry_id: str = "",
    notebook_id: str = "",
    pipeline_name: str = "",
    metadata_table: str = LINEAGE_TABLE,
    mode: str = "append",
) -> dict[str, Any]:
    """Write many-to-many source-to-target lineage evidence.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Spark session used to create lineage rows.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.
    run_id : str, optional
        Pipeline run identifier. When omitted, the active context from
        :func:`widget_pipeline_bootstrap` is used.
    source_definitions, target_definitions : mapping
        Source and target definitions keyed by alias.
    relationships : list of mapping, optional
        Many-to-many lineage relationships. Each item may contain ``sources``,
        ``targets``, ``operation``, and ``description``. When omitted, every
        source is linked to every target.
    dataset_name, agreement_id, agreement_contract_version, notebook_registry_id, notebook_id, pipeline_name : str, optional
        Governance context embedded in lineage payloads.
    metadata_table : str, default="METADATA_DATA_LINEAGE_TABLE"
        Metadata lineage table.
    mode : str, default="append"
        Write mode for lineage evidence.

    Returns
    -------
    dict[str, Any]
        Status, row count, and written rows.

    """
    config, env, resolved_context = resolve_fabric_context(context=context)
    audit = _runtime_audit_fields(config, env)
    created_at = _timestamp_value(config=config)
    if relationships is None:
        relationships = [
            {
                "sources": list(source_definitions),
                "targets": list(target_definitions),
                "operation": "pipeline_transform",
                "description": "User-defined pipeline transformation.",
            }
        ]
    rows: list[dict[str, Any]] = []
    sequence = 0
    for relationship in relationships:
        for source_alias in relationship.get("sources", []):
            for target_alias in relationship.get("targets", []):
                sequence += 1
                source_table = _definition_name(str(source_alias), source_definitions[str(source_alias)])
                target_table = _definition_name(str(target_alias), target_definitions[str(target_alias)])
                payload = {
                    "run_id": run_id,
                    "agreement_id": agreement_id,
                    "agreement_contract_version": agreement_contract_version,
                    "notebook_registry_id": notebook_registry_id,
                    "notebook_id": notebook_id,
                    "pipeline_name": pipeline_name,
                    "source_alias": source_alias,
                    "target_alias": target_alias,
                    "operation": relationship.get("operation", "pipeline_transform"),
                    "description": relationship.get("description", ""),
                }
                rows.append(
                    {
                        "lineage_id": f"{run_id}_{sequence}",
                        "dataset_name": dataset_name
                        or str(target_definitions[str(target_alias)].get("dataset_name") or target_table),
                        "run_id": run_id,
                        "source_table": source_table,
                        "target_table": target_table,
                        "source_table_key": _build_metadata_table_key(
                            env,
                            str(source_definitions[str(source_alias)].get("dataset_name") or source_table),
                            source_table,
                        ),
                        "target_table_key": _build_metadata_table_key(
                            env,
                            str(target_definitions[str(target_alias)].get("dataset_name") or target_table),
                            target_table,
                        ),
                        "transformation_steps_json": json.dumps(payload, default=str, sort_keys=True),
                        "created_at": created_at,
                        **audit,
                    }
                )
    if rows:
        write_lakehouse_table_core(
            spark.createDataFrame([coerce_metadata_row_types(metadata_table, row) for row in rows]),
            metadata_table,
            target="metadata",
            schema=configured_lakehouse_schema(config, env, "metadata"),
            context=resolved_context,
            mode=mode,
        )
    return {"status": "written" if rows else "skipped", "row_count": len(rows), "rows": rows}


def _write_pipeline_run_summary_workflow(
    *,
    spark: Any | None = None,
    run_id: str | None = None,
    context: dict[str, Any] | None = None,
    agreement_id: str = "",
    agreement_contract_version: str = "",
    notebook_registry_id: str = "",
    notebook_id: str = "",
    notebook_type: str = "02_pipeline",
    pipeline_name: str = "",
    started_at: str | None = None,
    completed_at: str | None = None,
    status: str = "completed",
    source_definitions: Mapping[str, Mapping[str, Any]] | None = None,
    target_definitions: Mapping[str, Mapping[str, Any]] | None = None,
    source_schema_results: Mapping[str, Mapping[str, Any]] | None = None,
    target_schema_results: Mapping[str, Mapping[str, Any]] | None = None,
    source_freshness_results: Mapping[str, Mapping[str, Any]] | None = None,
    target_freshness_results: Mapping[str, Mapping[str, Any]] | None = None,
    source_stability_results: Mapping[str, Mapping[str, Any]] | None = None,
    target_stability_results: Mapping[str, Mapping[str, Any]] | None = None,
    source_dq_results: Mapping[str, Mapping[str, Any]] | None = None,
    target_dq_results: Mapping[str, Mapping[str, Any]] | None = None,
    lineage_status: str = "not_run",
    catalogue_status: str = "not_run",
    message: str = "",
    source_guardrail_results: Mapping[str, Any] | None = None,
    target_guardrail_results: Mapping[str, Any] | None = None,
    target_write_status: Mapping[str, Any] | None = None,
    lineage_result: Mapping[str, Any] | None = None,
    metadata_table: str = METADATA_PIPELINE_RUNS_TABLE,
    mode: str = "append",
) -> dict[str, Any]:
    """Write a pipeline runtime summary to metadata.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession, optional
        Spark session used to create the one-row summary DataFrame. When omitted,
        the active context from :func:`widget_pipeline_bootstrap` is used.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.
    run_id : str, optional
        Pipeline run identifier. When omitted, the active context from
        :func:`widget_pipeline_bootstrap` is used.
    agreement_id, agreement_contract_version, notebook_registry_id, notebook_id, notebook_type, pipeline_name : str, optional
        Agreement and notebook registry context.
    started_at, completed_at : str, optional
        Runtime timestamps. Defaults to current UTC time when omitted.
    status : str, default="completed"
        Overall pipeline status.
    source_definitions, target_definitions : mapping, optional
        Dataset definitions used to compute source and target counts.
    source_schema_results, target_schema_results, source_freshness_results, target_freshness_results, source_stability_results, target_stability_results, source_dq_results, target_dq_results : mapping, optional
        Guardrail result dictionaries included in the JSON summary.
    lineage_status, catalogue_status, message : str, optional
        Evidence write statuses and support message.
    source_guardrail_results, target_guardrail_results : mapping, optional
        Template-facing guardrail result bundles returned by
        :func:`run_table_guardrails`. When supplied, schema, freshness, profile
        behavior, DQ, catalogue, and status fields are derived automatically.
    target_write_status, lineage_result : mapping, optional
        Template-facing write and lineage outcomes included in the run summary.
    metadata_table : str, default="METADATA_PIPELINE_RUNS"
        Metadata table that stores runtime summaries.
    mode : str, default="append"
        Write mode for the runtime summary row.

    Returns
    -------
    dict[str, Any]
        The summary row that was written.

    Notes
    -----
    The row is written via ``write_lakehouse_table(..., metadata_table,
    target="metadata", context=resolved_context, mode="append")`` so runtime
    evidence never relies on a default attached lakehouse.

    """
    from ..widgets.shared import pipeline_active_context

    active = pipeline_active_context()
    if active is not None:
        context = context if context is not None else active.context
        spark = spark if spark is not None else active.spark_session
        run_id = run_id or active.run_id
        agreement_id = agreement_id or active.agreement_id
        agreement_contract_version = agreement_contract_version or active.agreement_contract_version
        notebook_registry_id = notebook_registry_id or active.notebook_registry_id
        notebook_id = notebook_id or active.notebook_id
        notebook_type = notebook_type or active.notebook_type
        pipeline_name = pipeline_name or active.pipeline_name
        started_at = started_at or active.pipeline_started_at
        source_definitions = source_definitions or active.source_definitions
        target_definitions = target_definitions or active.target_definitions
    if spark is None:
        raise ValueError("spark is required unless widget_pipeline_bootstrap has established an active context.")
    if not run_id:
        raise ValueError("run_id is required unless widget_pipeline_bootstrap has established an active context.")

    source_guardrail_results = source_guardrail_results or {}
    target_guardrail_results = target_guardrail_results or {}
    source_schema_results = source_schema_results or source_guardrail_results.get("schema_results")
    target_schema_results = target_schema_results or target_guardrail_results.get("schema_results")
    source_freshness_results = source_freshness_results or source_guardrail_results.get("freshness_results")
    target_freshness_results = target_freshness_results or target_guardrail_results.get("freshness_results")
    source_stability_results = source_stability_results or source_guardrail_results.get("stability_results")
    target_stability_results = target_stability_results or target_guardrail_results.get("stability_results")
    source_dq_results = source_dq_results or source_guardrail_results.get("dq_results")
    target_dq_results = target_dq_results or target_guardrail_results.get("dq_results")
    source_definitions = source_definitions or source_guardrail_results.get("evidence_definitions")
    target_definitions = target_definitions or target_guardrail_results.get("evidence_definitions")
    if lineage_result is not None:
        lineage_status = str(lineage_result.get("status", lineage_status))
    if source_guardrail_results or target_guardrail_results:
        if status == "completed":
            status = (
                "succeeded"
                if all(
                    bool(result.get("can_continue", True))
                    for result in (source_guardrail_results, target_guardrail_results)
                )
                else "failed"
            )
        if catalogue_status == "not_run" and any(
            result.get("catalogue_status") for result in (source_guardrail_results, target_guardrail_results)
        ):
            catalogue_status = "written"
    if target_write_status and not message:
        message = json.dumps({"target_write_status": target_write_status}, default=str, sort_keys=True)

    config, env, resolved_context = resolve_fabric_context(context=context)
    audit = _runtime_audit_fields(config, env)
    completed = _timestamp_value(completed_at, config=config)
    started = _timestamp_value(started_at, config=config) if started_at else completed
    sources = source_definitions or {}
    targets = target_definitions or {}
    source_guardrail_status = _summary_status(
        {**(source_schema_results or {}), **(source_freshness_results or {}), **(source_stability_results or {})}
    )
    target_guardrail_status = _summary_status(
        {**(target_schema_results or {}), **(target_freshness_results or {}), **(target_stability_results or {})}
    )
    dq_status = _summary_status({**(source_dq_results or {}), **(target_dq_results or {})})
    run_summary = {
        "source_schema_results": source_schema_results or {},
        "target_schema_results": target_schema_results or {},
        "source_freshness_results": source_freshness_results or {},
        "target_freshness_results": target_freshness_results or {},
        "source_stability_results": source_stability_results or {},
        "target_stability_results": target_stability_results or {},
        "source_dq_results": source_dq_results or {},
        "target_dq_results": target_dq_results or {},
        "source_tables": [_definition_name(name, definition) for name, definition in sources.items()],
        "target_tables": [_definition_name(name, definition) for name, definition in targets.items()],
        "target_write_status": dict(target_write_status or {}),
        "lineage_result": dict(lineage_result or {}),
    }
    row = {
        "run_id": run_id or str(uuid4()),
        "agreement_id": agreement_id,
        "agreement_contract_version": agreement_contract_version,
        "notebook_registry_id": notebook_registry_id,
        "notebook_id": notebook_id,
        "notebook_type": notebook_type,
        "pipeline_name": pipeline_name,
        "environment_name": env,
        "started_at": started,
        "completed_at": completed,
        "status": status,
        "source_count": len(sources),
        "target_count": len(targets),
        "source_guardrail_status": source_guardrail_status,
        "target_guardrail_status": target_guardrail_status,
        "dq_status": dq_status,
        "lineage_status": lineage_status,
        "catalogue_status": catalogue_status,
        "message": message,
        "run_summary_json": json.dumps(run_summary, default=str, sort_keys=True),
        "created_at": _timestamp_value(config=config),
        **audit,
    }
    write_lakehouse_table_core(
        spark.createDataFrame([coerce_metadata_row_types(metadata_table, row)]),
        metadata_table,
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        context=resolved_context,
        mode=mode,
    )
    return row
