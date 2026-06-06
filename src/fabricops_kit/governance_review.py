"""Table-scoped governance review helpers for ``04_gov`` notebooks."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from datetime import datetime, timezone
import importlib
import json
import re
from typing import Any, Iterable
import uuid

from .fabric_input_output import read_lakehouse_table, write_lakehouse_table
from .metadata import _now_utc_iso, _resolve_action_by, _build_metadata_column_key, _build_metadata_table_key, _build_runtime_audit_fields, _build_dq_rule_key

CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
COLUMN_CONTEXT_TABLE = "METADATA_COLUMN_CONTEXT"
DQ_RULES_TABLE = "METADATA_DQ_RULES"
COLUMN_CLASSIFICATION_TABLE = "METADATA_COLUMN_CLASSIFICATION"
LINEAGE_TABLE = "METADATA_DATA_LINEAGE_TABLE"
SUCCESS_STATUSES = {"success", "succeeded", "passed", "complete", "completed", "ok"}
DQ_RULE_TYPES = ["not_null", "unique", "accepted_values", "value_range", "regex", "datatype", "referential_integrity", "custom_expression"]
AI_SUGGESTABLE_DQ_RULE_TYPES = {"not_null", "unique_key", "accepted_values", "value_range", "regex_format"}
SENSITIVITY_LABELS = ["public", "internal", "confidential", "restricted"]
PERSONAL_DATA_CLASSIFICATIONS = ["not_personal_data", "direct_identifier", "indirect_identifier", "sensitive_personal_data", "unknown"]

_SELECTED_CATALOGUE_TABLE: dict[str, Any] | None = None


def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]:
    if rows_or_df is None:
        return []
    if hasattr(rows_or_df, "collect"):
        rows_or_df = rows_or_df.collect()
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows_or_df]


def _value(row: dict[str, Any], name: str, default: Any = "") -> Any:
    return row.get(name, row.get(name.upper(), default))


def _is_success(row: dict[str, Any]) -> bool:
    return str(_value(row, "profile_status", "")).strip().lower() in SUCCESS_STATUSES




@dataclass
class DQEnforcementResult:
    """Structured DQ enforcement output retained for future production wiring.

    The class is intentionally internal while v1.0.0 keeps the root public
    callable surface unchanged. It allows tests and future pipeline work to
    exercise migrated DQ enforcement without restoring ``data_quality.py`` as a
    standalone implementation module.
    """

    rules: list[dict[str, Any]]
    rule_results: Any
    valid_rows: Any
    quarantine_rows: Any
    failure_rows: Any


def _spark_functions():
    """Import Spark SQL helper modules lazily so package import stays light."""
    try:
        from pyspark.sql import functions as F
        from pyspark.sql.window import Window
    except Exception as exc:  # pragma: no cover - runtime dependency guard
        raise RuntimeError("DQ drafting/enforcement helpers require pyspark in the active runtime.") from exc
    return F, Window


def _parse_jsonish(value: Any) -> dict[str, Any]:
    if value in (None, ""):
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except Exception:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _parse_dq_rules_dict_from_text(text: str) -> dict[str, list[dict[str, Any]]]:
    """Parse an AI response containing a ``DQ_RULES`` dictionary payload."""
    cleaned = str(text or "").strip()
    match = re.search(r"DQ_RULES\s*=\s*(\{.*\})", cleaned, flags=re.DOTALL)
    payload = match.group(1) if match else cleaned
    for parser in (ast.literal_eval, json.loads):
        try:
            parsed = parser(payload)
        except Exception:
            continue
        if isinstance(parsed, dict):
            return parsed
    return {}


def _extract_dq_rules(response_df: Any, table_name: str, response_col: str = "response") -> list[dict[str, Any]]:
    """Extract and deduplicate AI-suggested candidate DQ rules from a Spark DataFrame."""
    candidates: list[dict[str, Any]] = []
    for row in response_df.select(response_col).collect():
        row_dict = row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
        candidates.extend(_parse_dq_rules_dict_from_text(row_dict.get(response_col, "")).get(table_name, []))
    by_id = {rule.get("rule_id"): rule for rule in candidates if rule.get("rule_id")}
    return list(by_id.values())


def _extract_candidate_rules_from_responses(response_rows: Any, table_name: str, response_col: str = "ai_dq_response") -> list[dict[str, Any]]:
    """Extract candidate DQ rules from Spark or list-based AI responses."""
    if hasattr(response_rows, "select"):
        return _extract_dq_rules(response_rows, table_name=table_name, response_col=response_col)
    candidates: list[dict[str, Any]] = []
    for row in response_rows or []:
        row_dict = row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
        text = row_dict.get(response_col) or row_dict.get("response") or ""
        candidates.extend(_parse_dq_rules_dict_from_text(text).get(table_name, []))
    by_id = {rule.get("rule_id"): rule for rule in candidates if rule.get("rule_id")}
    return list(by_id.values())


def _prepare_dq_profile_rows_with_context(profile_rows: list[dict[str, Any]], table_name: str, column_contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Join approved column business context into profile rows before DQ AI suggestion."""
    context_lookup = {str(row.get("column_name")): row for row in column_contexts or [] if row.get("column_name")}
    out: list[dict[str, Any]] = []
    for row in profile_rows or []:
        column_name = str(row.get("column_name") or row.get("COLUMN_NAME") or "")
        context = context_lookup.get(column_name) or {}
        approved_context = context.get("approved_business_context") or context.get("business_context")
        if approved_context:
            out.append({**row, "table_name": table_name, "approved_business_context": approved_context})
    return out


def _suggest_dq_rules_with_fabric_ai(prepared_profile_df: Any, prompt_template: str, output_col: str = "ai_dq_response") -> Any:
    """Run Fabric AI to draft DQ rules from prepared profile rows."""
    ai = getattr(prepared_profile_df, "ai", None)
    if ai is None or not hasattr(ai, "generate_response"):
        raise RuntimeError("_suggest_dq_rules_with_fabric_ai requires Fabric DataFrame.ai.generate_response.")
    return prepared_profile_df.ai.generate_response(prompt=prompt_template, is_prompt_template=True, output_col=output_col)


def _prepare_dq_profile_input_rows(*, profile_df: Any = None, df: Any = None, table_name: str, business_context: str = "") -> Any:
    """Prepare profile rows from a profile DataFrame or raw DataFrame for DQ AI drafting."""
    if (profile_df is None) == (df is None):
        raise ValueError("Provide exactly one of profile_df or df.")
    F, _ = _spark_functions()
    if profile_df is None:
        from .data_profiling import profile_dataframe
        profile_df = profile_dataframe(df, table_name=table_name)
    cols = set(profile_df.columns)
    if {"column_name", "data_type", "row_count", "null_count", "distinct_count"}.issubset(cols):
        return profile_df
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
        F.lit(datetime.now(timezone.utc).isoformat()).alias("profile_timestamp"),
    )


def _suggest_dq_rules(profile_df: Any, prompt_template: str | None = None, output_col: str = "response") -> Any:
    """Generate row-wise AI DQ suggestions using Fabric AI Functions."""
    if not prompt_template:
        raise ValueError("Missing dq_rule_suggestion_prompt_template. Define it in AIPromptConfig or pass prompt_template explicitly.")
    ai = getattr(profile_df, "ai", None)
    if ai is None or not hasattr(ai, "generate_response"):
        raise RuntimeError("_suggest_dq_rules requires Fabric DataFrame.ai.generate_response.")
    return profile_df.ai.generate_response(prompt=prompt_template, output_col=output_col)


def _draft_dq_rules(*, profile_df: Any = None, df: Any = None, table_name: str, business_context: str = "", prompt_template: str | None = None, output_col: str = "response") -> list[dict[str, Any]]:
    """Draft candidate DQ rules from metadata profiles or raw DataFrame fallback."""
    prepared = _prepare_dq_profile_input_rows(profile_df=profile_df, df=df, table_name=table_name, business_context=business_context)
    responses = _suggest_dq_rules(prepared, prompt_template=prompt_template, output_col=output_col)
    return _extract_dq_rules(responses, table_name=table_name, response_col=output_col)


def _normalise_enforcement_rule(rule: dict[str, Any]) -> dict[str, Any]:
    """Return a canonical enforcement rule from governance or legacy metadata shapes."""
    out = dict(rule)
    parameters = _parse_jsonish(out.pop("rule_parameters_json", None))
    parameters.update(_parse_jsonish(out.get("rule_parameters")))
    for key, value in parameters.items():
        out.setdefault(key, value)
    if "columns" not in out or not out.get("columns"):
        column_name = out.get("column_name") or out.get("COLUMN_NAME")
        if column_name:
            out["columns"] = [str(column_name)]
    if isinstance(out.get("columns"), str):
        out["columns"] = [c.strip() for c in str(out["columns"]).split(",") if c.strip()]
    rule_type = str(out.get("rule_type") or "").strip()
    aliases = {"unique": "unique_key", "regex": "regex_format"}
    out["rule_type"] = aliases.get(rule_type, rule_type)
    out.setdefault("severity", "warning")
    out.setdefault("description", "")
    return out


def _validate_dq_rules(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate canonical DQ rules before migrated DQ enforcement helpers run."""
    if not isinstance(rules, list):
        raise ValueError("DQ rules must be a list of dictionaries.")
    required = {"rule_id", "rule_type", "columns", "severity", "description"}
    normalised = [_normalise_enforcement_rule(rule) if isinstance(rule, dict) else rule for rule in rules]
    for index, rule in enumerate(normalised):
        if not isinstance(rule, dict):
            raise ValueError(f"DQ rule at index {index} must be a dictionary.")
        missing = required.difference(rule)
        if missing:
            raise ValueError(f"DQ rule '{rule.get('rule_id', index)}' is missing fields: {sorted(missing)}")
        if rule["rule_type"] not in AI_SUGGESTABLE_DQ_RULE_TYPES:
            raise ValueError(f"DQ rule '{rule['rule_id']}' has unsupported rule_type '{rule['rule_type']}'.")
        if str(rule["severity"]).lower() not in {"warning", "error"}:
            raise ValueError(f"DQ rule '{rule['rule_id']}' severity must be warning or error.")
        columns = rule.get("columns")
        if not isinstance(columns, list) or not columns:
            raise ValueError(f"DQ rule '{rule['rule_id']}' columns must be a non-empty list.")
        if rule["rule_type"] in {"not_null", "accepted_values", "value_range", "regex_format"} and len(columns) != 1:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires exactly one column.")
        if rule["rule_type"] == "accepted_values" and "allowed_values" not in rule:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires allowed_values.")
        if rule["rule_type"] == "value_range" and "lower_bound" not in rule and "upper_bound" not in rule:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires lower_bound or upper_bound.")
        if rule["rule_type"] == "regex_format" and "regex_pattern" not in rule:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires regex_pattern.")
    return normalised


def _row_to_dict(row: Any) -> dict[str, Any]:
    return row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _dq_rule_sort_key(row: dict[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        str(row.get("action_ts") or row.get("approved_at") or row.get("_committed_at") or ""),
        str(row.get("action_type") or ""),
        str(row.get("approved_by") or row.get("action_by") or ""),
        str(row.get("rule_source") or ""),
        str(row.get("rule_json") or row.get("rule_parameters_json") or ""),
    )


def _latest_dq_rule_versions(metadata_df: Any, table_name: str) -> list[dict[str, Any]]:
    """Resolve latest DQ metadata rows per rule key from legacy or v1 metadata shapes."""
    rows = [_row_to_dict(row) for row in metadata_df.collect()]
    by_key: dict[str, dict[str, Any]] = {}
    for row in rows:
        if str(row.get("table_name") or row.get("TABLE_NAME") or "") != table_name:
            continue
        key = str(row.get("rule_key") or row.get("RULE_KEY") or row.get("rule_id") or "")
        if not key:
            continue
        current = by_key.get(key)
        if current is None or _dq_rule_sort_key(row) >= _dq_rule_sort_key(current):
            by_key[key] = row
    return list(by_key.values())


def _rule_from_metadata_row(row: dict[str, Any]) -> dict[str, Any]:
    if row.get("rule_json"):
        parsed = json.loads(row["rule_json"])
        if isinstance(parsed, dict):
            return _normalise_enforcement_rule(parsed)
    params = _parse_jsonish(row.get("rule_parameters_json"))
    rule = {
        "rule_id": row.get("rule_id"),
        "rule_type": row.get("rule_type"),
        "columns": [row.get("column_name")] if row.get("column_name") else row.get("columns"),
        "severity": row.get("severity") or "warning",
        "description": row.get("description") or "",
        **params,
    }
    return _normalise_enforcement_rule(rule)


def _load_active_dq_rules(metadata_df: Any, table_name: str) -> list[dict[str, Any]]:
    """Load latest active approved DQ rules from append-only metadata history."""
    active_rules: list[dict[str, Any]] = []
    for row in _latest_dq_rule_versions(metadata_df, table_name):
        action_type = str(row.get("action_type") or "approved").lower()
        if not _truthy(row.get("is_active")) or action_type in {"deactivated", "rejected", "inactive"}:
            continue
        active_rules.append(_rule_from_metadata_row(row))
    return _validate_dq_rules(active_rules)


def _load_active_dq_rule_metadata(metadata_df: Any, table_name: str) -> list[dict[str, Any]]:
    """Return latest active DQ metadata rows for future review screens."""
    return [row for row in _latest_dq_rule_versions(metadata_df, table_name) if _truthy(row.get("is_active"))]


def _split_dq_rows(df: Any, rules: list[dict[str, Any]], dq_run_id: str | None = None, row_id_columns: list[str] | None = None) -> tuple[Any, Any, Any]:
    """Split rows into valid, quarantine, and one-row-per-failure evidence DataFrames."""
    F, Window = _spark_functions()
    rules = _validate_dq_rules(rules)
    dq_run_id = dq_run_id or str(uuid.uuid4())
    run_ts = datetime.now(timezone.utc).isoformat()
    if row_id_columns:
        df_with_ids = df.withColumn("dq_row_id", F.sha2(F.concat_ws("||", *[F.coalesce(F.col(column).cast("string"), F.lit("<NULL>")) for column in row_id_columns]), 256))
    else:
        df_with_ids = df.withColumn("dq_row_id", F.sha2(F.concat_ws("||", *[F.coalesce(F.col(column).cast("string"), F.lit("<NULL>")) for column in df.columns], F.monotonically_increasing_id().cast("string")), 256))
    working = df_with_ids.withColumn("dq_run_id", F.lit(dq_run_id))
    failure_dfs = []
    for rule in rules:
        rule_id = str(rule["rule_id"])
        rule_type = str(rule["rule_type"])
        columns = rule["columns"]
        column_name = columns[0] if columns else None
        if rule_type == "not_null":
            failed = F.col(column_name).isNull() | (F.trim(F.col(column_name).cast("string")) == "")
        elif rule_type == "unique_key":
            dup_col = f"__dq_duplicate_count_{rule_id}"
            working = working.withColumn(dup_col, F.count(F.lit(1)).over(Window.partitionBy(*[F.col(column) for column in columns])))
            failed = F.col(dup_col) > F.lit(1)
        elif rule_type == "accepted_values":
            failed = F.col(column_name).isNotNull() & ~F.col(column_name).isin(rule["allowed_values"])
        elif rule_type == "value_range":
            condition = F.lit(False)
            if rule.get("lower_bound") is not None:
                condition = condition | (F.col(column_name).cast("double") < F.lit(float(rule["lower_bound"])))
            if rule.get("upper_bound") is not None:
                condition = condition | (F.col(column_name).cast("double") > F.lit(float(rule["upper_bound"])))
            failed = F.col(column_name).isNotNull() & condition
        elif rule_type == "regex_format":
            failed = F.col(column_name).isNotNull() & ~F.col(column_name).rlike(rule["regex_pattern"])
        else:
            continue
        failure_dfs.append(
            working.filter(F.coalesce(failed, F.lit(False))).select(
                F.col("dq_run_id"),
                F.col("dq_row_id"),
                F.lit(rule_id).alias("rule_id"),
                F.lit(rule_type).alias("rule_type"),
                F.lit(",".join(columns)).alias("failed_columns"),
                F.lit(str(rule.get("severity", "warning"))).alias("severity"),
                F.lit(str(rule.get("description", ""))).alias("description"),
                F.lit(run_ts).alias("dq_failed_ts"),
            )
        )
        if rule_type == "unique_key":
            working = working.drop(dup_col)
    if not failure_dfs:
        empty = df.sparkSession.createDataFrame([], "dq_run_id string, dq_row_id string, dq_quarantine_id string, rule_id string, rule_type string, failed_columns string, severity string, description string, dq_failed_ts string")
        return working, working.limit(0), empty
    failures = failure_dfs[0]
    for failure_df in failure_dfs[1:]:
        failures = failures.unionByName(failure_df)
    quarantine_ids = failures.select("dq_run_id", "dq_row_id").distinct().withColumn("dq_quarantine_id", F.sha2(F.concat_ws("||", F.col("dq_run_id"), F.col("dq_row_id")), 256))
    failures = failures.join(quarantine_ids, on=["dq_run_id", "dq_row_id"], how="left").select("dq_run_id", "dq_row_id", "dq_quarantine_id", "rule_id", "rule_type", "failed_columns", "severity", "description", "dq_failed_ts")
    quarantine_rows = working.join(quarantine_ids, on=["dq_run_id", "dq_row_id"], how="inner").withColumn("dq_quarantine_ts", F.lit(run_ts))
    valid_rows = working.join(quarantine_ids.select("dq_run_id", "dq_row_id"), on=["dq_run_id", "dq_row_id"], how="left_anti")
    return valid_rows, quarantine_rows, failures


def _run_dq_rules(df: Any, table_name: str, rules: list[dict[str, Any]]) -> Any:
    """Run DQ rules and return rule-level PASS/FAIL evidence for all rules."""
    F, _ = _spark_functions()
    rules = _validate_dq_rules(rules)
    _, _, failures = _split_dq_rows(df, rules)
    total = df.count()
    failure_counts = {row["rule_id"]: int(row["failed_count"]) for row in failures.groupBy("rule_id").agg(F.count(F.lit(1)).alias("failed_count")).collect()}
    rows = []
    for rule in rules:
        failed_count = failure_counts.get(rule["rule_id"], 0)
        rows.append({
            "table_name": table_name,
            "rule_id": rule["rule_id"],
            "rule_type": rule["rule_type"],
            "columns": ",".join(rule["columns"]),
            "severity": str(rule["severity"]).lower(),
            "status": "PASS" if failed_count == 0 else "FAIL",
            "failed_count": int(failed_count),
            "total_count": int(total),
            "failed_percent": float(round((failed_count / total) * 100, 4)) if total else 0.0,
            "description": rule.get("description", ""),
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
        })
    return df.sparkSession.createDataFrame(rows)


def _enforce_dq(df: Any, *, table_name: str, rules: list[dict[str, Any]] | None = None, metadata_df: Any = None, row_id_columns: list[str] | None = None, dq_run_id: str | None = None) -> DQEnforcementResult:
    """Enforce approved DQ rules and return structured deterministic outputs."""
    if rules is None and metadata_df is None:
        raise ValueError("Provide rules or metadata_df.")
    active_rules = rules or _load_active_dq_rules(metadata_df, table_name=table_name)
    active_rules = _validate_dq_rules(active_rules)
    rule_results = _run_dq_rules(df, table_name=table_name, rules=active_rules)
    valid_rows, quarantine_rows, failure_rows = _split_dq_rows(df, active_rules, dq_run_id=dq_run_id, row_id_columns=row_id_columns)
    return DQEnforcementResult(active_rules, rule_results, valid_rows, quarantine_rows, failure_rows)


def _assert_dq_passed(dq_result: Any) -> None:
    """Raise when error-severity DQ rules fail after evidence materialization."""
    result_df = dq_result.rule_results if isinstance(dq_result, DQEnforcementResult) else dq_result
    if result_df.filter("lower(severity) = 'error' AND status = 'FAIL'").count() > 0:
        raise ValueError("Data quality failed for error-severity rules.")

def _spark_types():
    """Return Spark SQL type classes lazily so package import stays lightweight."""
    try:
        from pyspark.sql.types import BooleanType, DoubleType, LongType, StringType, StructField, StructType, TimestampType
    except Exception as exc:  # pragma: no cover - Fabric/runtime dependency guard
        raise RuntimeError("governance metadata schemas require pyspark.sql.types in the active runtime.") from exc
    return BooleanType, DoubleType, LongType, StringType, StructField, StructType, TimestampType


def _schema(fields: list[tuple[str, Any]]):
    _, _, _, _, StructField, StructType, _ = _spark_types()
    return StructType([StructField(name, data_type, True) for name, data_type in fields])


def _schema_field_names(schema: Any) -> list[str]:
    if hasattr(schema, "fieldNames"):
        return list(schema.fieldNames())
    return [field.name for field in getattr(schema, "fields", [])]


def _get_governance_metadata_schemas() -> dict[str, Any]:
    """Return typed Spark schemas prepared by ``00_env_config`` for governance.

    Returns
    -------
    dict[str, pyspark.sql.types.StructType]
        Physical metadata table names mapped to explicit nullable Spark schemas.

    Notes
    -----
    The bootstrap creates empty Delta tables with these explicit schemas instead
    of inferring all columns from empty strings. It does not seed data,
    duplicate pipeline configuration, or create a data-contract table.
    """
    BooleanType, DoubleType, LongType, StringType, _, _, TimestampType = _spark_types()
    string = StringType()
    long = LongType()
    double = DoubleType()
    boolean = BooleanType()
    timestamp = TimestampType()
    audit = [("_committed_at", string), ("_committed_by", string), ("_workspace_name", string), ("_notebook_name", string), ("_metadata_lakehouse_name", string), ("_activity_id", string)]
    catalogue = [
        ("metadata_table_key", string), ("metadata_column_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string),
        ("layer", string), ("asset_kind", string), ("pipeline_name", string), ("profile_run_id", string), ("profile_stage", string), ("profile_status", string), ("baseline_status", string),
        ("source_data_change_check", string), ("profile_baseline_mode", string), ("data_type", string), ("row_count", long), ("null_count", long), ("distinct_count", long),
        ("distribution_type", string), ("distribution_json", string), ("profiled_at", string), ("null_percent", double), ("distinct_percent", double), ("min_value", string), ("max_value", string),
        ("agreement_id", string), ("contract_version", string),
        ("TABLE_NAME", string), ("RUN_TIMESTAMP", timestamp), ("COLUMN_NAME", string), ("DATA_TYPE", string), ("ROW_COUNT", long), ("NULL_COUNT", long), ("NULL_PERCENT", double), ("DISTINCT_COUNT", long), ("DISTINCT_PERCENT", double), ("MIN_VALUE", string), ("MAX_VALUE", string), ("DISTRIBUTION_TYPE", string), ("DISTRIBUTION_JSON", string),
        ("AGREEMENT_ID", string), ("AGREEMENT_CONTRACT_VERSION", string), ("NOTEBOOK_REGISTRY_ID", string), ("NOTEBOOK_ID", string), ("PROFILE_RUN_ID", string), ("ENVIRONMENT_NAME", string), ("DATASET_NAME", string), ("PIPELINE_NAME", string), ("EVIDENCE_ROLE", string), ("PROFILE_STAGE", string), ("PROFILE_STATUS", string), ("BASELINE_STATUS", string), ("SOURCE_SCHEMA_CHECK", string), ("TARGET_SCHEMA_CHECK", string), ("SOURCE_DATA_CHANGE_CHECK", string), ("TARGET_DATA_CHANGE_CHECK", string), ("SOURCE_CHANGE_SIGNAL_JSON", string), ("LAYER", string), ("ASSET_KIND", string), ("PROFILED_TABLE_NAME", string), ("PROFILED_ROW_COUNT", long),
        *audit,
    ]
    return {
        CATALOGUE_TABLE: _schema(catalogue),
        COLUMN_CONTEXT_TABLE: _schema([("metadata_column_key", string), ("metadata_table_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("business_context", string), ("notes", string), ("review_status", string), ("approved_by", string), ("approved_at", string), ("ai_suggestion_json", string), *audit]),
        DQ_RULES_TABLE: _schema([("rule_key", string), ("rule_id", string), ("metadata_column_key", string), ("metadata_table_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("rule_type", string), ("rule_parameters_json", string), ("severity", string), ("description", string), ("is_active", boolean), ("review_status", string), ("approved_by", string), ("approved_at", string), ("ai_suggestion_json", string), ("action_type", string), *audit]),
        COLUMN_CLASSIFICATION_TABLE: _schema([("metadata_column_key", string), ("metadata_table_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("sensitivity_label", string), ("personal_data_classification", string), ("pii_identifier_type", string), ("handling_requirement", string), ("reasoning", string), ("review_status", string), ("approved_by", string), ("approved_at", string), ("ai_suggestion_json", string), *audit]),
        LINEAGE_TABLE: _schema([("lineage_id", string), ("dataset_name", string), ("run_id", string), ("source_table", string), ("target_table", string), ("source_table_key", string), ("target_table_key", string), ("transformation_steps_json", string), ("created_at", string), *audit]),
    }


def _is_table_not_found_error(exc: Exception) -> bool:
    """Return whether a Spark/read exception clearly means the table is absent."""
    error_class_getter = getattr(exc, "getErrorClass", None)
    try:
        error_class = str(error_class_getter() or "") if callable(error_class_getter) else ""
    except Exception:
        error_class = ""
    if error_class.upper() in {"PATH_NOT_FOUND", "TABLE_OR_VIEW_NOT_FOUND", "DELTA_TABLE_NOT_FOUND"}:
        return True
    message = str(exc).lower()
    not_found_markers = (
        "path does not exist",
        "path_not_found",
        "table_or_view_not_found",
        "table not found",
        "no such file or directory",
        "doesn't exist",
        "does not exist",
    )
    non_not_found_markers = ("permission", "access denied", "unauthorized", "forbidden", "authentication", "credential", "malformed", "invalid configuration")
    return any(marker in message for marker in not_found_markers) and not any(marker in message for marker in non_not_found_markers)


def _setup_governance_metadata_tables(*, spark: Any, config: Any, env: str) -> dict[str, Any]:
    """Create or validate governance metadata tables via the configured route.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Spark session used to create empty metadata tables when missing.
    config : FrameworkConfig or dict
        ``00_env_config`` configuration that contains the ``metadata`` target.
    env : str
        Environment key to prepare.

    Returns
    -------
    dict[str, Any]
        Setup status, checked tables, and newly created tables.
    """
    created: list[str] = []
    schemas = _get_governance_metadata_schemas()
    for table_name, schema in schemas.items():
        try:
            table = read_lakehouse_table(config, env, "metadata", table_name, spark_session=spark)
        except Exception as exc:
            if not _is_table_not_found_error(exc):
                raise RuntimeError(f"Unable to read governance metadata table {table_name!r}; not attempting creation because the error was not a confirmed table-not-found condition.") from exc
            empty_df = spark.createDataFrame([], schema=schema)
            write_lakehouse_table(empty_df, config, env, "metadata", table_name, mode="ignore", overwrite_schema=True)
            table = read_lakehouse_table(config, env, "metadata", table_name, spark_session=spark)
            created.append(table_name)
        columns = list(getattr(table, "columns", [])) or (list(_coerce_rows(table)[0]) if _coerce_rows(table) else [])
        fields = _schema_field_names(schema)
        missing = [field for field in fields if field not in columns]
        if missing:
            raise ValueError(f"{table_name} is missing required column(s): {', '.join(missing)}. Migrate the table before running 04_gov.")
    return {"status": "ready", "tables": list(schemas), "created_tables": created}


def _catalogue_table_options(catalogue_rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return one option per logical table using its latest successful profile.

    Parameters
    ----------
    catalogue_rows : iterable of dict
        Rows from ``METADATA_DATA_CATALOGUE``.

    Returns
    -------
    list[dict[str, Any]]
        Stable table selections sorted by display label.

    Raises
    ------
    ValueError
        If there are no catalogue rows or no successful profile rows.
    """
    rows = [dict(r) for r in catalogue_rows or []]
    if not rows:
        raise ValueError("METADATA_DATA_CATALOGUE has no rows. Run 03_pc profiling before 04_gov.")
    successes = [r for r in rows if _is_success(r)]
    if not successes:
        raise ValueError("METADATA_DATA_CATALOGUE has no successful profile evidence for governance review.")
    latest: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in successes:
        env = str(_value(row, "environment_name"))
        dataset = str(_value(row, "dataset_name"))
        table = str(_value(row, "table_name"))
        key = (env, dataset, table)
        current = latest.get(key)
        sort_key = (str(_value(row, "profiled_at")), str(_value(row, "profile_run_id")), str(_value(row, "profile_stage")))
        if current is None or sort_key > current["_sort_key"]:
            latest[key] = {"row": row, "_sort_key": sort_key}
    options = []
    for (env, dataset, table), item in latest.items():
        row = item["row"]
        table_key = str(_value(row, "metadata_table_key") or _build_metadata_table_key(env, dataset, table))
        profile_run_id = str(_value(row, "profile_run_id"))
        profile_stage = str(_value(row, "profile_stage"))
        layer = str(_value(row, "layer"))
        asset_kind = str(_value(row, "asset_kind"))
        label = f"{env} / {dataset} / {layer or '-'} / {asset_kind or '-'} / {table} / {profile_stage or '-'} / {profile_run_id}"
        options.append({
            "label": label,
            "value": json.dumps({"environment_name": env, "dataset_name": dataset, "table_name": table, "metadata_table_key": table_key, "profile_run_id": profile_run_id, "profile_stage": profile_stage, "layer": layer, "asset_kind": asset_kind, "profiled_at": str(_value(row, "profiled_at"))}, sort_keys=True),
            "environment_name": env, "dataset_name": dataset, "table_name": table, "metadata_table_key": table_key,
            "profile_run_id": profile_run_id, "profile_stage": profile_stage, "layer": layer, "asset_kind": asset_kind, "profiled_at": str(_value(row, "profiled_at")),
        })
    return sorted(options, key=lambda r: r["label"])


def get_selected_catalogue_table(table_selector: Any | None = None) -> dict[str, Any]:
    """Return the catalogue table selected by ``widget_select_catalogue_table``.

    Parameters
    ----------
    table_selector : ipywidgets.Combobox, optional
        Selector returned by ``widget_select_catalogue_table``. Passing it is
        optional because the widget also maintains module-level selection state.

    Returns
    -------
    dict[str, Any]
        Stable table identity used by ``load_catalogue_profile_rows``.
    """
    if _SELECTED_CATALOGUE_TABLE is not None:
        return dict(_SELECTED_CATALOGUE_TABLE)
    raw_value = getattr(table_selector, "value", None) if table_selector is not None else None
    if raw_value:
        try:
            parsed = json.loads(str(raw_value))
            if isinstance(parsed, dict):
                return dict(parsed)
        except json.JSONDecodeError:
            pass
    raise ValueError("No catalogue table has been selected. Run widget_select_catalogue_table first.")


def widget_select_catalogue_table(config: Any, env: str, *, spark_session: Any):
    """Render a searchable selector for latest successful catalogue tables.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Runtime config containing the metadata lakehouse route.
    env : str
        Environment used to read ``METADATA_DATA_CATALOGUE``.
    spark_session : pyspark.sql.SparkSession
        Spark session used for the catalogue read.

    Returns
    -------
    ipywidgets.Combobox
        Searchable selector whose value stores stable JSON identity.
    """
    global _SELECTED_CATALOGUE_TABLE
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    rows = _coerce_rows(read_lakehouse_table(config, env, "metadata", CATALOGUE_TABLE, spark_session=spark_session))
    options = _catalogue_table_options(rows)
    by_label = {o["label"]: o for o in options}
    combo = widgets.Combobox(placeholder="Search profiled tables", options=[o["label"] for o in options], description="Table", ensure_option=True, layout=widgets.Layout(width="980px"))
    context = widgets.HTML()

    def select(label: str) -> None:
        global _SELECTED_CATALOGUE_TABLE
        option = by_label.get(label) or options[0]
        _SELECTED_CATALOGUE_TABLE = {k: option[k] for k in ["environment_name", "dataset_name", "table_name", "metadata_table_key", "profile_run_id", "profile_stage", "layer", "asset_kind", "profiled_at"]}
        context.value = f"<b>Selected table:</b> {_SELECTED_CATALOGUE_TABLE['environment_name']} / {_SELECTED_CATALOGUE_TABLE['dataset_name']} / {_SELECTED_CATALOGUE_TABLE['table_name']}<br/><b>Profile run:</b> {_SELECTED_CATALOGUE_TABLE['profile_run_id']} ({_SELECTED_CATALOGUE_TABLE['profile_stage']})"

    def on_change(change: dict[str, Any]) -> None:
        if change.get("name") == "value" and change.get("new") in by_label:
            select(change["new"])

    combo.observe(on_change, names="value")
    combo.value = options[0]["label"]
    select(combo.value)
    ip.display(widgets.VBox([combo, context]))
    return combo


def load_catalogue_profile_rows(config: Any, env: str, selection: dict[str, Any], *, spark_session: Any) -> list[dict[str, Any]]:
    """Load column rows for the selected latest successful profile run."""
    rows = _coerce_rows(read_lakehouse_table(config, env, "metadata", CATALOGUE_TABLE, spark_session=spark_session))
    filtered = []
    for row in rows:
        table_key = str(
            _value(row, "metadata_table_key")
            or _build_metadata_table_key(
                _value(row, "environment_name"),
                _value(row, "dataset_name"),
                _value(row, "table_name"),
            )
        )
        if (
            _is_success(row)
            and str(_value(row, "environment_name")) == str(selection["environment_name"])
            and str(_value(row, "dataset_name")) == str(selection["dataset_name"])
            and str(_value(row, "table_name")) == str(selection["table_name"])
            and str(_value(row, "profile_run_id")) == str(selection["profile_run_id"])
            and str(_value(row, "profile_stage")) == str(selection["profile_stage"])
            and table_key == str(selection["metadata_table_key"])
        ):
            filtered.append(row)
    if not filtered:
        raise ValueError("The selected successful profile has no column rows in METADATA_DATA_CATALOGUE.")
    return filtered


def _build_column_context_records(profile_rows: list[dict[str, Any]], reviewed_rows: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> list[dict[str, Any]]:
    """Build append-only approved business-context records from explicit reviews."""
    profile = {str(_value(r, "column_name")): r for r in profile_rows}
    actor = _resolve_action_by(approved_by)
    now = _now_utc_iso()
    audit = _build_runtime_audit_fields(config=config, env=env or "", committed_by=actor) if config is not None and env is not None else {}
    rows = []
    for review in reviewed_rows or []:
        if str(review.get("review_status", "approved")).lower() != "approved" or not review.get("commit"):
            continue
        col = str(review.get("column_name"))
        p = profile.get(col, {})
        env_name = str(_value(p, "environment_name") or review.get("environment_name") or env or "")
        dataset = str(_value(p, "dataset_name") or review.get("dataset_name") or "")
        table = str(_value(p, "table_name") or review.get("table_name") or "")
        rows.append({
            "metadata_column_key": str(_value(p, "metadata_column_key") or review.get("metadata_column_key") or _build_metadata_column_key(env_name, dataset, table, col)),
            "metadata_table_key": str(_value(p, "metadata_table_key") or review.get("metadata_table_key") or _build_metadata_table_key(env_name, dataset, table)),
            "environment_name": env_name, "dataset_name": dataset, "table_name": table, "column_name": col,
            "business_context": str(review.get("business_context") or ""), "notes": str(review.get("notes") or ""), "review_status": "approved",
            "approved_by": actor, "approved_at": now, "ai_suggestion_json": _json(review.get("ai_suggestion_json") or review.get("ai_suggestion")), **audit,
        })
    return rows


def _build_dq_rule_records(profile_rows: list[dict[str, Any]], reviewed_rules: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> list[dict[str, Any]]:
    """Build append-only approved DQ-rule records without enforcing them."""
    actor = _resolve_action_by(approved_by)
    now = _now_utc_iso()
    audit = _build_runtime_audit_fields(config=config, env=env or "", committed_by=actor) if config is not None and env is not None else {}
    profile = {str(_value(r, "column_name")): r for r in profile_rows}
    rows = []
    for rule in reviewed_rules or []:
        if str(rule.get("review_status", "approved")).lower() != "approved" or not rule.get("commit"):
            continue
        rule_type = str(rule.get("rule_type") or "")
        if rule_type not in DQ_RULE_TYPES:
            raise ValueError(f"Unsupported rule_type: {rule_type}")
        col = str(rule.get("column_name") or "")
        p = profile.get(col, {})
        env_name = str(_value(p, "environment_name") or rule.get("environment_name") or env or "")
        dataset = str(_value(p, "dataset_name") or rule.get("dataset_name") or "")
        table = str(_value(p, "table_name") or rule.get("table_name") or "")
        rule_id = str(rule.get("rule_id") or f"{table}.{col}.{rule_type}")
        rows.append({
            "rule_key": _build_dq_rule_key(env_name, dataset, table, rule_id), "rule_id": rule_id,
            "metadata_column_key": str(_value(p, "metadata_column_key") or rule.get("metadata_column_key") or _build_metadata_column_key(env_name, dataset, table, col)),
            "metadata_table_key": str(_value(p, "metadata_table_key") or rule.get("metadata_table_key") or _build_metadata_table_key(env_name, dataset, table)),
            "environment_name": env_name, "dataset_name": dataset, "table_name": table, "column_name": col,
            "rule_type": rule_type, "rule_parameters_json": _json(rule.get("rule_parameters") or rule.get("rule_parameters_json") or {}),
            "severity": str(rule.get("severity") or "warning"), "description": str(rule.get("description") or ""), "is_active": bool(rule.get("is_active", True)),
            "review_status": "approved", "approved_by": actor, "approved_at": now, "ai_suggestion_json": _json(rule.get("ai_suggestion_json") or rule.get("ai_suggestion")), "action_type": "approved", **audit,
        })
    return rows


def _build_classification_records(profile_rows: list[dict[str, Any]], reviewed_rows: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> list[dict[str, Any]]:
    """Build append-only approved sensitivity and PII classification records."""
    actor = _resolve_action_by(approved_by)
    now = _now_utc_iso()
    audit = _build_runtime_audit_fields(config=config, env=env or "", committed_by=actor) if config is not None and env is not None else {}
    profile = {str(_value(r, "column_name")): r for r in profile_rows}
    rows = []
    for review in reviewed_rows or []:
        if str(review.get("review_status", "approved")).lower() != "approved" or not review.get("commit"):
            continue
        sensitivity = str(review.get("sensitivity_label") or "internal")
        classification = str(review.get("personal_data_classification") or "unknown")
        if sensitivity not in SENSITIVITY_LABELS:
            raise ValueError(f"Unsupported sensitivity_label: {sensitivity}")
        if classification not in PERSONAL_DATA_CLASSIFICATIONS:
            raise ValueError(f"Unsupported personal_data_classification: {classification}")
        col = str(review.get("column_name"))
        p = profile.get(col, {})
        env_name = str(_value(p, "environment_name") or review.get("environment_name") or env or "")
        dataset = str(_value(p, "dataset_name") or review.get("dataset_name") or "")
        table = str(_value(p, "table_name") or review.get("table_name") or "")
        rows.append({
            "metadata_column_key": str(_value(p, "metadata_column_key") or review.get("metadata_column_key") or _build_metadata_column_key(env_name, dataset, table, col)),
            "metadata_table_key": str(_value(p, "metadata_table_key") or review.get("metadata_table_key") or _build_metadata_table_key(env_name, dataset, table)),
            "environment_name": env_name, "dataset_name": dataset, "table_name": table, "column_name": col,
            "sensitivity_label": sensitivity, "personal_data_classification": classification,
            "pii_identifier_type": str(review.get("pii_identifier_type") or ""), "handling_requirement": str(review.get("handling_requirement") or ""),
            "reasoning": str(review.get("reasoning") or ""), "review_status": "approved", "approved_by": actor, "approved_at": now,
            "ai_suggestion_json": _json(review.get("ai_suggestion_json") or review.get("ai_suggestion")), **audit,
        })
    return rows


def _json(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True)


def _display_review_guidance(title: str, profile_rows: list[dict[str, Any]], instructions: str) -> list[dict[str, Any]]:
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    columns = [str(_value(row, "column_name")) for row in profile_rows]
    html = widgets.HTML(
        f"<h3>{title}</h3>"
        f"<p>{instructions}</p>"
        f"<p><b>Columns loaded:</b> {', '.join(columns)}</p>"
        "<p>Return value is an editable list scaffold. Add reviewed dictionaries, set "
        "<code>review_status='approved'</code> and <code>commit=True</code>, then pass the list to "
        "<code>record_table_governance</code>.</p>"
    )
    ip.display(html)
    return []


def widget_review_column_context(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Render standalone business-context review guidance for ``04_gov``.

    Parameters
    ----------
    profile_rows : list of dict
        Selected column profile evidence from ``load_catalogue_profile_rows``.

    Returns
    -------
    list[dict[str, Any]]
        Empty editable review list. Add approved context rows before calling
        ``record_table_governance``.
    """
    return _display_review_guidance(
        "Business context review",
        profile_rows,
        "Describe human-approved business meaning for each column. AI suggestions, if used, are advisory only.",
    )


def widget_review_dq_rules(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Render standalone DQ-rule review guidance for ``04_gov``.

    Parameters
    ----------
    profile_rows : list of dict
        Selected column profile evidence from ``load_catalogue_profile_rows``.

    Returns
    -------
    list[dict[str, Any]]
        Empty editable review list. Add approved rule dictionaries before
        calling ``record_table_governance``.
    """
    return _display_review_guidance(
        "DQ rule review",
        profile_rows,
        "Author human-approved DQ rules for selected columns. These records are governance evidence and are not automatically enforced by 03_pc.",
    )


def widget_review_column_classification(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Render standalone sensitivity and PII classification review guidance.

    Parameters
    ----------
    profile_rows : list of dict
        Selected column profile evidence from ``load_catalogue_profile_rows``.

    Returns
    -------
    list[dict[str, Any]]
        Empty editable review list. Add approved classification dictionaries
        before calling ``record_table_governance``.
    """
    return _display_review_guidance(
        "Sensitivity and PII classification review",
        profile_rows,
        "Review sensitivity labels, personal-data classifications, identifier types, and handling requirements.",
    )


def record_table_governance(
    config: Any,
    env: str,
    profile_rows: list[dict[str, Any]],
    *,
    spark_session: Any,
    context_reviews: list[dict[str, Any]] | None = None,
    dq_rule_reviews: list[dict[str, Any]] | None = None,
    classification_reviews: list[dict[str, Any]] | None = None,
    approved_by: str | None = None,
    mode: str = "append",
) -> dict[str, list[dict[str, Any]]]:
    """Persist approved table-governance review evidence.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Shared ``00_env_config`` configuration that routes metadata writes to
        the configured metadata lakehouse target.
    env : str
        Environment key in ``config``.
    profile_rows : list of dict
        Column-profile rows loaded for the selected catalogue table.
    spark_session : pyspark.sql.SparkSession
        Spark session used to create DataFrames for metadata writes.
    context_reviews, dq_rule_reviews, classification_reviews : list of dict, optional
        Human-approved rows from the governance review workflow. Only rows with
        ``review_status="approved"`` and ``commit=True`` are written.
    approved_by : str, optional
        Reviewer identity to stamp on records. When omitted, runtime defaults
        are used.
    mode : str, default "append"
        Write mode for metadata table commits.

    Returns
    -------
    dict[str, list[dict[str, Any]]]
        Records written for ``column_context``, ``dq_rules``, and
        ``column_classification``.

    Notes
    -----
    This is the v1 governance commit action for ``04_gov`` notebooks. It merges
    the previous row-builder and per-table commit helpers into one explicit
    human approval step while preserving configured metadata lakehouse routing.
    """
    context_records = _build_column_context_records(
        profile_rows,
        context_reviews or [],
        config=config,
        env=env,
        approved_by=approved_by,
    )
    dq_rule_records = _build_dq_rule_records(
        profile_rows,
        dq_rule_reviews or [],
        config=config,
        env=env,
        approved_by=approved_by,
    )
    classification_records = _build_classification_records(
        profile_rows,
        classification_reviews or [],
        config=config,
        env=env,
        approved_by=approved_by,
    )
    writes = {
        COLUMN_CONTEXT_TABLE: context_records,
        DQ_RULES_TABLE: dq_rule_records,
        COLUMN_CLASSIFICATION_TABLE: classification_records,
    }
    for table_name, records in writes.items():
        if records:
            write_lakehouse_table(spark_session.createDataFrame(records), config, env, "metadata", table_name, mode=mode)

    return {
        "column_context": context_records,
        "dq_rules": dq_rule_records,
        "column_classification": classification_records,
    }
