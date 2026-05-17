"""Canonical Spark/Fabric data-quality workflow helpers for notebook users."""

from __future__ import annotations

import ast
import importlib
import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql import SparkSession
from .data_profiling import profile_dataframe
from .fabric_input_output import write_lakehouse_table
from .metadata import build_dq_rule_key, build_metadata_column_key, build_metadata_table_key, _now_utc_iso, _resolve_action_by

AI_SUGGESTABLE_DQ_RULE_TYPES = {"not_null", "unique_key", "accepted_values", "value_range", "regex_format"}


@dataclass
class DQEnforcementResult:
    """Structured DQ enforcement output for notebook-first usage."""

    rules: list[dict[str, Any]]
    rule_results: Any
    valid_rows: Any
    quarantine_rows: Any
    failure_rows: Any


def _profile_for_dq(df, table_name: str, business_context: str = "", sample_value_limit: int = 20):
    """Profile a Spark DataFrame into one row per source column for DQ rule suggestion.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Source Spark DataFrame.
    table_name : str
        Logical table name to include in profile rows.
    business_context : str, default=""
        Domain context carried into profile rows and AI prompts.
    sample_value_limit : int, default=20
        Maximum number of distinct non-null sample values per column.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark profile DataFrame with one row per input column.
    """
    row_count = df.count()
    rows = []
    for column_name, data_type in df.dtypes:
        null_count = df.filter(F.col(column_name).isNull()).count()
        distinct_count = df.select(column_name).distinct().count()
        min_value = None
        max_value = None
        if data_type in {"int", "bigint", "double", "float", "date", "timestamp"} or data_type.startswith("decimal"):
            mm = df.select(F.min(F.col(column_name)).cast("string").alias("min_value"), F.max(F.col(column_name)).cast("string").alias("max_value")).collect()[0]
            min_value, max_value = mm["min_value"], mm["max_value"]
        observed = [str(r[column_name]) for r in df.select(column_name).where(F.col(column_name).isNotNull()).distinct().limit(sample_value_limit).collect()]
        rows.append({"table_name": table_name, "column_name": column_name, "data_type": data_type, "row_count": int(row_count), "null_count": int(null_count), "null_percent": round((null_count / row_count) * 100, 4) if row_count else 0.0, "distinct_count": int(distinct_count), "distinct_percent": round((distinct_count / row_count) * 100, 4) if row_count else 0.0, "min_value": min_value, "max_value": max_value, "observed_values_sample": ", ".join(observed), "business_context": business_context, "profile_timestamp": datetime.now(timezone.utc).isoformat()})
    return df.sparkSession.createDataFrame(rows)


def _suggest_dq_rules(profile_df, prompt_template: str | None = None, output_col: str = "response"):
    """Generate row-wise AI DQ suggestions using Fabric AI Functions.

    Parameters
    ----------
    profile_df : pyspark.sql.DataFrame
        Output of :func:`_profile_for_dq`.
    prompt_template : str | None, optional
        Prompt template from ``config.ai_prompt_config.dq_rule_suggestion_prompt_template``.
    output_col : str, default="response"
        Output column for AI text responses.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame including AI response text.
    """
    if not prompt_template:
        raise ValueError("Missing dq_rule_suggestion_prompt_template. Define it in AIPromptConfig from 00_env_config or pass prompt_template explicitly.")
    active_prompt = prompt_template
    return profile_df.ai.generate_response(prompt=active_prompt, output_col=output_col)


def _parse_dq_rules_dict_from_text(text: str) -> dict[str, list[dict[str, Any]]]:
    cleaned = str(text or "").strip()
    match = re.search(r"DQ_RULES\s*=\s*(\{.*\})", cleaned, flags=re.DOTALL)
    payload = match.group(1) if match else cleaned
    try:
        parsed = ast.literal_eval(payload)
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}



def _prepare_dq_profile_rows_with_context(profile_rows: list[dict], table_name: str, column_contexts: list[dict]) -> list[dict]:
    """Join approved column business context into profile rows before DQ AI suggestion."""
    context_lookup = {r["column_name"]: r for r in column_contexts or [] if r.get("column_name")}
    out = []
    for row in profile_rows:
        c = row.get("column_name")
        approved_ctx = (context_lookup.get(c) or {}).get("approved_business_context")
        if not approved_ctx:
            continue
        out.append({**row, "table_name": table_name, "approved_business_context": approved_ctx})
    return out


def _attach_rule_metadata_keys(candidate_rules: list[dict], environment_name: str, dataset_name: str, table_name: str) -> list[dict]:
    """Attach deterministic metadata keys to candidate DQ rules."""
    out = []
    for rule in candidate_rules or []:
        cols = rule.get("columns", [])
        out.append(
            {
                **rule,
                "environment_name": environment_name,
                "dataset_name": dataset_name,
                "table_name": table_name,
                "metadata_table_key": build_metadata_table_key(environment_name, dataset_name, table_name),
                "metadata_column_keys": [build_metadata_column_key(environment_name, dataset_name, table_name, c) for c in cols],
                "rule_key": build_dq_rule_key(environment_name, dataset_name, table_name, rule.get("rule_id")),
            }
        )
    return out


def _extract_dq_rules(response_df, table_name: str, response_col: str = "response") -> list[dict[str, Any]]:
    """Extract notebook-shaped AI responses and deduplicate candidate DQ rules by ``rule_id``."""
    candidates: list[dict[str, Any]] = []
    for row in response_df.select(response_col).collect():
        candidates.extend(_parse_dq_rules_dict_from_text(row[response_col]).get(table_name, []))
    deduped: dict[str, dict[str, Any]] = {}
    for rule in candidates:
        rid = rule.get("rule_id")
        if rid:
            deduped[rid] = rule
    return list(deduped.values())


def _suggest_dq_rules_with_fabric_ai(prepared_profile_df, prompt_template: str, output_col: str = "ai_dq_response"):
    """Run Fabric AI to draft DQ rules from prepared profile rows.

    Parameters
    ----------
    prepared_profile_df : pyspark.sql.DataFrame
        Prepared profile rows (including approved business context) for prompt execution.
    prompt_template : str
        Prompt template text, usually from ``CONFIG.ai_prompt_config.dq_rule_suggestion_prompt_template``.
    output_col : str, default=\"ai_dq_response\"
        Response column for AI output text.

    Returns
    -------
    pyspark.sql.DataFrame
        Input DataFrame enriched with AI response output.
    """
    ai = getattr(prepared_profile_df, "ai", None)
    if ai is None or not hasattr(ai, "generate_response"):
        raise RuntimeError("_suggest_dq_rules_with_fabric_ai requires Fabric DataFrame.ai.generate_response.")
    return prepared_profile_df.ai.generate_response(prompt=prompt_template, is_prompt_template=True, output_col=output_col)


def _extract_candidate_rules_from_responses(response_rows, table_name: str, response_col: str = "ai_dq_response") -> list[dict[str, Any]]:
    """Extract candidate DQ rules from Spark/list AI responses.

    Parameters
    ----------
    response_rows : pyspark.sql.DataFrame | list[dict]
        AI response rows containing a DQ rules dictionary payload.
    table_name : str
        Target table key used to select rules from ``DQ_RULES`` payload.
    response_col : str, default=\"ai_dq_response\"
        Response column name containing AI text.

    Returns
    -------
    list[dict[str, Any]]
        Deduplicated candidate DQ rules.
    """
    if hasattr(response_rows, "select"):
        return _extract_dq_rules(response_rows, table_name=table_name, response_col=response_col)
    candidates: list[dict[str, Any]] = []
    for row in response_rows or []:
        text = row.get(response_col) or row.get("response") or ""
        candidates.extend(_parse_dq_rules_dict_from_text(text).get(table_name, []))
    by_id = {r.get("rule_id"): r for r in candidates if r.get("rule_id")}
    return list(by_id.values())



def _approved_dq_rules_from_review_rows(review_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return approved canonical DQ rules from notebook review rows."""
    approved: list[dict[str, Any]] = []
    for row in review_rows or []:
        if str(row.get("approval_status", "")).lower() != "approved":
            continue
        payload = row.get("proposed_rule_payload") or "{}"
        approved.append(json.loads(payload) if isinstance(payload, str) else dict(payload))
    return approved


def validate_dq_rules(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate canonical DQ rules before enforcement.

    Notes
    -----
    Supported canonical ``rule_type`` values are ``not_null``, ``unique_key``,
    ``accepted_values``, ``value_range``, and ``regex_format``.

    Raises
    ------
    ValueError
        If a rule type, severity, column binding, or required field is invalid.
    """
    if not isinstance(rules, list):
        raise ValueError("DQ rules must be a list of dictionaries.")
    required = {"rule_id", "rule_type", "columns", "severity", "description"}
    for i, rule in enumerate(rules):
        if not isinstance(rule, dict):
            raise ValueError(f"DQ rule at index {i} must be a dictionary.")
        missing = required.difference(rule)
        if missing:
            raise ValueError(f"DQ rule '{rule.get('rule_id', i)}' is missing fields: {sorted(missing)}")
        if rule["rule_type"] not in AI_SUGGESTABLE_DQ_RULE_TYPES:
            raise ValueError(f"DQ rule '{rule['rule_id']}' has unsupported rule_type '{rule['rule_type']}'.")
        if str(rule["severity"]).lower() not in {"warning", "error"}:
            raise ValueError(f"DQ rule '{rule['rule_id']}' severity must be warning or error.")
        cols = rule.get("columns")
        if not isinstance(cols, list) or not cols:
            raise ValueError(f"DQ rule '{rule['rule_id']}' columns must be a non-empty list.")
        if rule["rule_type"] in {"not_null", "accepted_values", "value_range", "regex_format"} and len(cols) != 1:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires exactly one column.")
        if rule["rule_type"] == "accepted_values" and "allowed_values" not in rule:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires allowed_values.")
        if rule["rule_type"] == "value_range" and "lower_bound" not in rule and "upper_bound" not in rule:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires lower_bound or upper_bound.")
        if rule["rule_type"] == "regex_format" and "regex_pattern" not in rule:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires regex_pattern.")
    return rules


def _build_dq_rule_history(spark, table_name: str, approved_rules: list[dict], action_by: str | None = None, rule_source: str = "ai_widget_approval", action_reason: str = "Approved after human review."):
    """Build append-only active metadata rows for approved DQ rules.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Active Spark session used to create metadata DataFrame.
    table_name : str
        Logical table name for the governed rules.
    approved_rules : list[dict]
        Human-approved canonical DQ rules to append as active versions.
    action_by : str | None, optional
        Actor identity for audit tracking. When omitted, resolved from
        ``notebookutils.runtime.context`` using ``userName``, then ``userId``,
        then ``"unknown"``.
    rule_source : str, default="ai_widget_approval"
        Source label for audit tracking.
    action_reason : str, default="Approved after human review."
        Human-readable reason for approval action.

    Returns
    -------
    pyspark.sql.DataFrame
        Append-only metadata rows with ``is_active=True`` and ``action_type=approved``.
    """
    ts = datetime.now(timezone.utc).isoformat(); rows = []
    resolved_action_by = _resolve_action_by(action_by)
    for rule in approved_rules:
        cols = rule.get("columns", [])
        rows.append({"table_name": table_name, "rule_id": str(rule["rule_id"]), "rule_type": str(rule["rule_type"]), "columns": ",".join(cols), "rule_key": f"{table_name}|{rule['rule_id']}|{rule['rule_type']}|{','.join(cols)}", "is_active": True, "action_type": "approved", "action_by": resolved_action_by, "action_ts": ts, "action_reason": action_reason, "rule_source": rule_source, "rule_json": json.dumps(rule)})
    return spark.createDataFrame(rows)


def _build_dq_rule_deactivations(spark, table_name: str, deactivations: list[dict], action_by: str | None = None, rule_source: str = "rule_deactivation_widget"):
    """Build append-only inactive metadata rows for governed DQ rule deactivation.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Active Spark session used to create metadata DataFrame.
    table_name : str
        Logical table name for the governed rules.
    deactivations : list[dict]
        Items shaped as ``{"rule": <rule dict>, "action_reason": <str>}``.
    action_by : str | None, optional
        Actor identity for audit tracking. When omitted, resolved from
        ``notebookutils.runtime.context`` using ``userName``, then ``userId``,
        then ``"unknown"``.
    rule_source : str, default="rule_deactivation_widget"
        Source label for audit tracking.

    Returns
    -------
    pyspark.sql.DataFrame
        Append-only metadata rows with ``is_active=False`` and ``action_type=deactivated``.

    Raises
    ------
    ValueError
        If any deactivation record has an empty reason.
    """
    ts = datetime.now(timezone.utc).isoformat(); rows = []
    resolved_action_by = _resolve_action_by(action_by)
    for item in deactivations:
        reason = str(item["action_reason"]).strip(); rule = item["rule"]
        if not reason:
            raise ValueError(f"Deactivation reason is required for rule '{rule['rule_id']}'.")
        cols = rule.get("columns", [])
        rows.append({"table_name": table_name, "rule_id": str(rule["rule_id"]), "rule_type": str(rule["rule_type"]), "columns": ",".join(cols), "rule_key": f"{table_name}|{rule['rule_id']}|{rule['rule_type']}|{','.join(cols)}", "is_active": False, "action_type": "deactivated", "action_by": resolved_action_by, "action_ts": ts, "action_reason": reason, "rule_source": rule_source, "rule_json": json.dumps(rule)})
    return spark.createDataFrame(rows)


def _latest_dq_rule_versions(metadata_df, table_name: str):
    """Resolve latest metadata row per rule key."""
    w = Window.partitionBy("rule_key").orderBy(F.col("action_ts").desc())
    return metadata_df.filter(F.col("table_name") == table_name).withColumn("_rn", F.row_number().over(w)).filter(F.col("_rn") == 1).drop("_rn")


def _load_active_dq_rules(metadata_df, table_name: str) -> list[dict[str, Any]]:
    """Load latest active approved rules from append-only metadata history.

    Parameters
    ----------
    metadata_df : pyspark.sql.DataFrame
        Append-only metadata table containing active and inactive versions.
    table_name : str
        Logical table name to resolve.

    Returns
    -------
    list[dict[str, Any]]
        Latest active rule payloads deserialized from ``rule_json``.

    Notes
    -----
    Latest-version resolution is done per ``rule_key``; a newer inactive version suppresses older active versions.
    """
    rows = _latest_dq_rule_versions(metadata_df, table_name).filter(F.col("is_active") == True).select("rule_json").collect()
    return [json.loads(r["rule_json"]) for r in rows]


# removed public metadata-row loader
def _load_active_dq_rule_metadata(metadata_df, table_name: str):
    """Return latest active metadata rows for governance review screens.

    Parameters
    ----------
    metadata_df : pyspark.sql.DataFrame
        Append-only metadata table containing active and inactive versions.
    table_name : str
        Logical table name to resolve.

    Returns
    -------
    pyspark.sql.DataFrame
        Latest active metadata versions per ``rule_key``.
    """
    return _latest_dq_rule_versions(metadata_df, table_name).filter(F.col("is_active") == True)


def _split_dq_rows(df, rules: list[dict[str, Any]], dq_run_id: str | None = None, row_id_columns: list[str] | None = None):
    """Split source rows into valid rows, quarantine rows, and one-row-per-failure evidence.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Source Spark DataFrame to evaluate.
    rules : list[dict[str, Any]]
        Canonical approved DQ rules to enforce.
    dq_run_id : str | None, optional
        Optional run identifier; auto-generated when omitted.
    row_id_columns : list[str] | None, optional
        Optional stable business-key columns used for deterministic row IDs.

    Returns
    -------
    tuple[pyspark.sql.DataFrame, pyspark.sql.DataFrame, pyspark.sql.DataFrame]
        ``(valid_rows, quarantine_rows, quarantine_failure_evidence)``.

    Raises
    ------
    ValueError
        If rules fail canonical DQ validation.

    Notes
    -----
    A single source row may generate multiple failure-evidence rows when multiple rules fail.
    """
    validate_dq_rules(rules)
    dq_run_id = dq_run_id or str(uuid.uuid4())
    run_ts = datetime.now(timezone.utc).isoformat()
    if row_id_columns:
        df_with_ids = df.withColumn("dq_row_id", F.sha2(F.concat_ws("||", *[F.coalesce(F.col(c).cast("string"), F.lit("<NULL>")) for c in row_id_columns]), 256))
    else:
        df_with_ids = df.withColumn("dq_row_id", F.sha2(F.concat_ws("||", *[F.coalesce(F.col(c).cast("string"), F.lit("<NULL>")) for c in df.columns], F.monotonically_increasing_id().cast("string")), 256))
    working = df_with_ids.withColumn("dq_run_id", F.lit(dq_run_id))
    failure_dfs = []
    for rule in rules:
        rid, rtype, cols = str(rule["rule_id"]), str(rule["rule_type"]), rule["columns"]
        col_name = cols[0] if cols else None
        if rtype == "not_null":
            failed = F.col(col_name).isNull() | (F.trim(F.col(col_name).cast("string")) == "")
        elif rtype == "unique_key":
            dup_col = f"__dq_duplicate_count_{rid}"; working = working.withColumn(dup_col, F.count(F.lit(1)).over(Window.partitionBy(*[F.col(c) for c in cols]))); failed = F.col(dup_col) > F.lit(1)
        elif rtype == "accepted_values":
            failed = F.col(col_name).isNotNull() & ~F.col(col_name).isin(rule["allowed_values"])
        elif rtype == "value_range":
            cond = F.lit(False)
            if rule.get("lower_bound") is not None:
                cond = cond | (F.col(col_name).cast("double") < F.lit(float(rule["lower_bound"])))
            if rule.get("upper_bound") is not None:
                cond = cond | (F.col(col_name).cast("double") > F.lit(float(rule["upper_bound"])))
            failed = F.col(col_name).isNotNull() & cond
        elif rtype == "regex_format":
            failed = F.col(col_name).isNotNull() & ~F.col(col_name).rlike(rule["regex_pattern"])
        else:
            continue
        failure_dfs.append(working.filter(F.coalesce(failed, F.lit(False))).select(F.col("dq_run_id"), F.col("dq_row_id"), F.lit(rid).alias("rule_id"), F.lit(rtype).alias("rule_type"), F.lit(",".join(cols)).alias("failed_columns"), F.lit(str(rule.get("severity", "warning"))).alias("severity"), F.lit(str(rule.get("description", ""))).alias("description"), F.lit(run_ts).alias("dq_failed_ts")))
        if rtype == "unique_key":
            working = working.drop(dup_col)
    if not failure_dfs:
        empty = df.sparkSession.createDataFrame([], "dq_run_id string, dq_row_id string, dq_quarantine_id string, rule_id string, rule_type string, failed_columns string, severity string, description string, dq_failed_ts string")
        return working, working.limit(0), empty
    failures = failure_dfs[0]
    for x in failure_dfs[1:]:
        failures = failures.unionByName(x)
    quarantine_ids = failures.select("dq_run_id", "dq_row_id").distinct().withColumn("dq_quarantine_id", F.sha2(F.concat_ws("||", F.col("dq_run_id"), F.col("dq_row_id")), 256))
    failures = failures.join(quarantine_ids, on=["dq_run_id", "dq_row_id"], how="left").select("dq_run_id", "dq_row_id", "dq_quarantine_id", "rule_id", "rule_type", "failed_columns", "severity", "description", "dq_failed_ts")
    quarantine_rows = working.join(quarantine_ids, on=["dq_run_id", "dq_row_id"], how="inner").withColumn("dq_quarantine_ts", F.lit(run_ts))
    valid = working.join(quarantine_ids.select("dq_run_id", "dq_row_id"), on=["dq_run_id", "dq_row_id"], how="left_anti")
    return valid, quarantine_rows, failures


def _run_dq_rules(df, table_name: str, rules: list[dict[str, Any]]):
    """Run canonical DQ rules and return Spark rule-level PASS/FAIL evidence for all rules.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Source Spark DataFrame to evaluate.
    table_name : str
        Logical table name included in output evidence rows.
    rules : list[dict[str, Any]]
        Canonical approved DQ rules to enforce.

    Returns
    -------
    pyspark.sql.DataFrame
        Rule-level evidence including PASS and FAIL rows for every approved rule.

    Raises
    ------
    ValueError
        If rules fail canonical DQ validation.
    """
    validate_dq_rules(rules)
    _, _, failures = _split_dq_rows(df, rules)
    total = df.count()
    failure_counts = {r["rule_id"]: int(r["failed_count"]) for r in failures.groupBy("rule_id").agg(F.count(F.lit(1)).alias("failed_count")).collect()}
    rows = []
    for rule in rules:
        failed_count = failure_counts.get(rule["rule_id"], 0)
        rows.append({"table_name": table_name, "rule_id": rule["rule_id"], "rule_type": rule["rule_type"], "columns": ",".join(rule["columns"]), "severity": str(rule["severity"]).lower(), "status": "PASS" if failed_count == 0 else "FAIL", "failed_count": int(failed_count), "total_count": int(total), "failed_percent": float(round((failed_count / total) * 100, 4)) if total else 0.0, "description": rule.get("description", ""), "run_timestamp": datetime.now(timezone.utc).isoformat()})
    return df.sparkSession.createDataFrame(rows)


def assert_dq_passed(dq_result_df) -> None:
    """Raise only after evidence materialization when error-severity rules fail.

    Parameters
    ----------
    dq_result_df : pyspark.sql.DataFrame
        Materialized rule-level DQ results DataFrame.

    Raises
    ------
    ValueError
        If any row has ``severity=error`` and ``status=FAIL``.
    """
    if dq_result_df.filter("lower(severity) = 'error' AND status = 'FAIL'").count() > 0:
        raise ValueError("Data quality failed for error-severity rules.")



def _prepare_dq_profile_input_rows(*, profile_df=None, df=None, table_name: str, business_context: str = ""):
    if (profile_df is None) == (df is None):
        raise ValueError("Provide exactly one of profile_df or df.")
    if profile_df is None:
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


def draft_dq_rules(*, profile_df=None, df=None, table_name: str, business_context: str = "", prompt_template: str | None = None, output_col: str = "response") -> list[dict[str, Any]]:
    """Draft candidate DQ rules from metadata profiles or raw DataFrame fallback."""
    prepared = _prepare_dq_profile_input_rows(profile_df=profile_df, df=df, table_name=table_name, business_context=business_context)
    responses = _suggest_dq_rules(prepared, prompt_template=prompt_template, output_col=output_col)
    return _extract_dq_rules(responses, table_name=table_name, response_col=output_col)


def write_dq_rules(approved_rules, *, table_name: str, metadata_path, metadata_table: str = "METADATA_DQ_RULES", action_by: str | None = None, rule_source: str = "ai_widget_approval", action_reason: str = "Approved after human review.", mode: str = "append"):
    """Validate, build, and persist approved DQ rules."""
    validate_dq_rules(approved_rules)
    spark = SparkSession.getActiveSession()
    if spark is None:
        raise ValueError("write_dq_rules requires an active SparkSession.")
    history_df = _build_dq_rule_history(spark, table_name=table_name, approved_rules=approved_rules, action_by=action_by, rule_source=rule_source, action_reason=action_reason)
    write_lakehouse_table(history_df, metadata_path, metadata_table, mode=mode)
    return history_df


def enforce_dq(df, *, table_name: str, rules=None, metadata_df=None, row_id_columns: list[str] | None = None, dq_run_id: str | None = None) -> DQEnforcementResult:
    """Enforce approved DQ rules and return structured deterministic outputs."""
    if rules is None and metadata_df is None:
        raise ValueError("Provide rules or metadata_df.")
    active_rules = rules or _load_active_dq_rules(metadata_df, table_name=table_name)
    validate_dq_rules(active_rules)
    rule_results = _run_dq_rules(df, table_name=table_name, rules=active_rules)
    valid_rows, quarantine_rows, failure_rows = _split_dq_rows(df, active_rules, dq_run_id=dq_run_id, row_id_columns=row_id_columns)
    return DQEnforcementResult(active_rules, rule_results, valid_rows, quarantine_rows, failure_rows)


def _build_dq_rules_metadata_df(spark, approved_rules: list[dict], action_by: str | None = None, action_reason: str = "Approved by reviewer", rule_source: str = "dq_review_widget"):
    """Build approved DQ metadata rows as a Spark DataFrame."""
    rows = []
    now = _now_utc_iso()
    actor = _resolve_action_by(action_by)
    for rule in approved_rules or []:
        rows.append(
            {
                "environment_name": rule.get("environment_name"),
                "dataset_name": rule.get("dataset_name"),
                "table_name": rule.get("table_name"),
                "metadata_table_key": rule.get("metadata_table_key"),
                "metadata_column_keys": rule.get("metadata_column_keys"),
                "rule_key": rule.get("rule_key"),
                "rule_id": rule.get("rule_id"),
                "rule_type": rule.get("rule_type"),
                "columns": rule.get("columns"),
                "severity": rule.get("severity"),
                "description": rule.get("description"),
                "rule_json": json.dumps(rule, sort_keys=True),
                "is_active": True,
                "action_type": "approved",
                "action_by": actor,
                "action_ts": now,
                "action_reason": action_reason,
                "rule_source": rule_source,
            }
        )
    return spark.createDataFrame(rows)


def _build_dq_rule_deactivation_metadata_df(spark, rejected_rules: list[dict], action_by: str | None = None, action_reason: str = "Rejected by reviewer", rule_source: str = "dq_review_widget"):
    rows = []
    now = _now_utc_iso()
    actor = _resolve_action_by(action_by)
    for rule in rejected_rules or []:
        rows.append(
            {
                "environment_name": rule.get("environment_name"),
                "dataset_name": rule.get("dataset_name"),
                "table_name": rule.get("table_name"),
                "metadata_table_key": rule.get("metadata_table_key"),
                "metadata_column_keys": rule.get("metadata_column_keys"),
                "rule_key": rule.get("rule_key"),
                "rule_id": rule.get("rule_id"),
                "rule_type": rule.get("rule_type"),
                "columns": rule.get("columns"),
                "severity": rule.get("severity"),
                "description": rule.get("description"),
                "rule_json": json.dumps(rule, sort_keys=True),
                "is_active": False,
                "action_type": "rejected",
                "action_by": actor,
                "action_ts": now,
                "action_reason": action_reason,
                "rule_source": rule_source,
            }
        )
    return spark.createDataFrame(rows)


def _require_ipywidgets() -> tuple[object, object]:
    widgets = importlib.import_module("ipywidgets")
    ipy_display = importlib.import_module("IPython.display").display
    return widgets, ipy_display
APPROVED_RULES_FROM_WIDGET = []
REJECTED_RULES_FROM_WIDGET = []


def review_dq_rules(candidate_rules, table_name: str):
    """Review AI-suggested DQ rules sequentially with explicit approve/reject decisions.

    Parameters
    ----------
    candidate_rules : list[dict]
        Candidate rule dictionaries extracted from AI responses.
    table_name : str
        Logical table name displayed in the widget header.

    Returns
    -------
    None
        Displays an interactive widget and updates module-level review result lists.

    Raises
    ------
    ImportError
        If ``ipywidgets`` is unavailable in the current runtime.

    Notes
    -----
    Approved and rejected outputs are stored in
    ``APPROVED_RULES_FROM_WIDGET`` and ``REJECTED_RULES_FROM_WIDGET``.
    """
    widgets, ipy_display = _require_ipywidgets()
    global APPROVED_RULES_FROM_WIDGET, REJECTED_RULES_FROM_WIDGET

    APPROVED_RULES_FROM_WIDGET.clear()
    REJECTED_RULES_FROM_WIDGET.clear()

    state = {"index": 0}

    title = widgets.HTML(
        value=f"<h4 style='margin:0;'>Human approval for AI-suggested DQ rules: {table_name}</h4>"
    )

    progress_label = widgets.HTML()
    rule_summary = widgets.HTML()

    severity_dropdown = widgets.Dropdown(
        options=["warning", "error"],
        description="Severity",
        layout=widgets.Layout(width="320px"),
    )

    description_box = widgets.Textarea(
        description="Description",
        layout=widgets.Layout(width="780px", height="80px"),
    )

    extras_box = widgets.Textarea(
        description="Extras JSON",
        layout=widgets.Layout(width="780px", height="100px"),
    )

    approve_button = widgets.Button(
        description="Approve",
        button_style="success",
        layout=widgets.Layout(width="220px"),
    )

    reject_button = widgets.Button(
        description="Reject",
        button_style="danger",
        layout=widgets.Layout(width="220px"),
    )

    undo_button = widgets.Button(
        description="Undo Last",
        button_style="warning",
        layout=widgets.Layout(width="220px"),
    )

    status = widgets.HTML()

    form_box = widgets.VBox(
        [
            severity_dropdown,
            description_box,
            extras_box,
            widgets.HBox([approve_button, reject_button, undo_button]),
        ]
    )

    def current_rule():
        idx = state["index"]
        if idx >= len(candidate_rules):
            return None
        return candidate_rules[idx]

    def load_current_rule():
        rule = current_rule()

        progress_label.value = (
            f"<b>Progress:</b> {state['index']} / {len(candidate_rules)} "
            f"&nbsp; | &nbsp; <b>Approved:</b> {len(APPROVED_RULES_FROM_WIDGET)} "
            f"&nbsp; | &nbsp; <b>Rejected:</b> {len(REJECTED_RULES_FROM_WIDGET)}"
        )

        if rule is None:
            total_reviewed = len(APPROVED_RULES_FROM_WIDGET) + len(REJECTED_RULES_FROM_WIDGET)

            rule_summary.value = f"""
            <div style="
                border:1px solid #d1e7dd;
                background:#f0fff4;
                padding:14px;
                border-radius:8px;
                margin-top:8px;
            ">
                <div style="font-size:18px; font-weight:700; color:#166534; margin-bottom:6px;">
                    ✅ Review complete
                </div>
                <div><b>Table:</b> {table_name}</div>
                <div><b>Total rules reviewed:</b> {total_reviewed} / {len(candidate_rules)}</div>
                <div><b>Approved:</b> {len(APPROVED_RULES_FROM_WIDGET)}</div>
                <div><b>Rejected:</b> {len(REJECTED_RULES_FROM_WIDGET)}</div>
                <div style="margin-top:10px; color:#444;">
                    Next step: store <b>APPROVED_RULES_FROM_WIDGET</b> into the metadata table.
                </div>
            </div>
            """

            form_box.layout.display = "none"

            if total_reviewed != len(candidate_rules):
                status.value = (
                    f"<span style='color:#b91c1c; font-weight:600;'>"
                    f"Warning: reviewed {total_reviewed} of {len(candidate_rules)} rules."
                    f"</span>"
                )
            else:
                status.value = (
                    "<span style='color:#166534; font-weight:600;'>"
                    "Approved rules are ready for metadata storage."
                    "</span>"
                )
            return

        rule_id = rule.get("rule_id", "")
        rule_type = rule.get("rule_type", "")
        columns = rule.get("columns", [])

        rule_summary.value = f"""
        <div style="
            border:1px solid #e5e7eb;
            background:#fafafa;
            padding:12px;
            border-radius:8px;
            margin-top:8px;
        ">
            <div style="font-weight:700; margin-bottom:8px;">Rule {state['index'] + 1} of {len(candidate_rules)}</div>
            <div><b>Rule ID:</b> <code>{rule_id}</code></div>
            <div><b>Rule type:</b> <code>{rule_type}</code></div>
            <div><b>Columns:</b> <code>{columns}</code></div>
        </div>
        """

        severity_value = str(rule.get("severity", "warning"))
        severity_dropdown.value = severity_value if severity_value in ["warning", "error"] else "warning"
        description_box.value = str(rule.get("description", ""))

        extras = {
            k: v
            for k, v in rule.items()
            if k not in {"rule_id", "rule_type", "columns", "severity", "description"}
        }
        extras_box.value = json.dumps(extras, indent=2) if extras else "{}"

        form_box.layout.display = ""
        status.value = ""

    def build_current_rule_from_widget():
        rule = current_rule()
        if rule is None:
            status.value = "<span style='color:red'>No current rule to review.</span>"
            return None

        edited_rule = dict(rule)

        try:
            extras = json.loads(extras_box.value or "{}")
            if not isinstance(extras, dict):
                raise ValueError("Extras JSON must be a dictionary.")
        except Exception as exc:
            status.value = f"<span style='color:red'><b>Invalid Extras JSON:</b> {exc}</span>"
            return None

        edited_rule["severity"] = severity_dropdown.value
        edited_rule["description"] = description_box.value

        for key, value in extras.items():
            edited_rule[key] = value

        return edited_rule

    def approve_clicked(_):
        rule = build_current_rule_from_widget()
        if rule is None:
            return

        APPROVED_RULES_FROM_WIDGET.append(rule)
        state["index"] += 1
        load_current_rule()

    def reject_clicked(_):
        rule = build_current_rule_from_widget()
        if rule is None:
            return

        REJECTED_RULES_FROM_WIDGET.append(rule)
        state["index"] += 1
        load_current_rule()

    def undo_clicked(_):
        if state["index"] == 0:
            status.value = "<span style='color:orange'>Nothing to undo.</span>"
            return

        state["index"] -= 1
        current_id = candidate_rules[state["index"]].get("rule_id")

        APPROVED_RULES_FROM_WIDGET[:] = [
            r for r in APPROVED_RULES_FROM_WIDGET if r.get("rule_id") != current_id
        ]
        REJECTED_RULES_FROM_WIDGET[:] = [
            r for r in REJECTED_RULES_FROM_WIDGET if r.get("rule_id") != current_id
        ]

        load_current_rule()

    approve_button.on_click(approve_clicked)
    reject_button.on_click(reject_clicked)
    undo_button.on_click(undo_clicked)

    ui = widgets.VBox(
        [
            title,
            progress_label,
            rule_summary,
            form_box,
            status,
        ],
        layout=widgets.Layout(
            border="1px solid #ddd",
            padding="12px",
            width="850px",
        ),
    )

    load_current_rule()
    ipy_display(ui)


def run_dq_rule_review_widget(
    candidate_rules: list[dict[str, Any]],
    *,
    table_name: str,
    environment_name: str | None = None,
    dataset_name: str | None = None,
) -> None:
    """Launch the canonical DQ review widget for analyst validation.

    Parameters
    ----------
    candidate_rules : list[dict[str, Any]]
        Candidate DQ rules generated by existing AI-assist helpers.
    table_name : str
        Logical table name used for governed DQ metadata.
    environment_name : str | None, optional
        Optional environment key attached to returned rules.
    dataset_name : str | None, optional
        Optional dataset key attached to returned rules.

    Returns
    -------
    None
        Displays the review widget and stores user actions in module-level state.

    Notes
    -----
    This function intentionally does not return review outcomes synchronously.
    In notebook workflows, call :func:`get_dq_review_results` after the
    analyst has completed widget interactions.
    """
    review_dq_rules(candidate_rules, table_name=table_name)


def get_dq_review_results(
    *,
    table_name: str,
    environment_name: str | None = None,
    dataset_name: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Collect current approved/rejected DQ review results from widget state.

    Parameters
    ----------
    table_name : str
        Logical table name used for governed DQ metadata.
    environment_name : str | None, optional
        Optional environment key attached to returned rules.
    dataset_name : str | None, optional
        Optional dataset key attached to returned rules.

    Returns
    -------
    dict[str, list[dict[str, Any]]]
        ``{"approved_rules": [...], "rejected_rules": [...]}`` reflecting
        current widget-reviewed state.
    """
    approved = list(APPROVED_RULES_FROM_WIDGET)
    rejected = list(REJECTED_RULES_FROM_WIDGET)
    if environment_name and dataset_name:
        approved = _attach_rule_metadata_keys(approved, environment_name, dataset_name, table_name)
        rejected = _attach_rule_metadata_keys(rejected, environment_name, dataset_name, table_name)
    return {"approved_rules": approved, "rejected_rules": rejected}


def load_dq_rules(metadata_df, *, table_name: str) -> list[dict[str, Any]]:
    """Load latest active approved DQ rules from append-only metadata history.

    Parameters
    ----------
    metadata_df : pyspark.sql.DataFrame
        Metadata table containing DQ rule history rows.
    table_name : str
        Logical table name to resolve.

    Returns
    -------
    list[dict[str, Any]]
        Canonical approved rule payloads suitable for pipeline enforcement.
    """
    return _load_active_dq_rules(metadata_df=metadata_df, table_name=table_name)



DEACTIVATED_RULES_FROM_WIDGET = []
KEPT_ACTIVE_RULES_FROM_WIDGET = []

def review_dq_rule_deactivations(active_rules, table_name: str):
    """Review active DQ rules one at a time for governed deactivation actions.

    Parameters
    ----------
    active_rules : list[dict]
        Active rule dictionaries loaded from rule metadata.
    table_name : str
        Logical table name displayed in the widget header.

    Returns
    -------
    None
        Displays an interactive widget and updates module-level review result lists.

    Raises
    ------
    ImportError
        If ``ipywidgets`` is unavailable in the current runtime.

    Notes
    -----
    Decisions are explicit per rule: keep active or deactivate. Deactivation requires a reason.
    Deactivation outputs are stored in ``DEACTIVATED_RULES_FROM_WIDGET`` and
    kept outputs are stored in ``KEPT_ACTIVE_RULES_FROM_WIDGET``.
    """
    widgets, ipy_display = _require_ipywidgets()
    global DEACTIVATED_RULES_FROM_WIDGET, KEPT_ACTIVE_RULES_FROM_WIDGET
    DEACTIVATED_RULES_FROM_WIDGET = []
    KEPT_ACTIVE_RULES_FROM_WIDGET = []

    state = {"index": 0}
    title = widgets.HTML(value=f"<h4 style='margin:0;'>DQ rule deactivation review: {table_name}</h4>")
    progress = widgets.HTML()
    summary = widgets.HTML()
    reason_box = widgets.Textarea(description="Reason", placeholder="Required when deactivating", layout=widgets.Layout(width="780px", height="90px"))
    keep_button = widgets.Button(description="Keep Active", button_style="success", layout=widgets.Layout(width="220px"))
    deactivate_button = widgets.Button(description="Deactivate", button_style="danger", layout=widgets.Layout(width="220px"))
    undo_button = widgets.Button(description="Undo Last", button_style="warning", layout=widgets.Layout(width="220px"))
    status = widgets.HTML()

    form_box = widgets.VBox([reason_box, widgets.HBox([keep_button, deactivate_button, undo_button])])

    def current_rule():
        if state["index"] >= len(active_rules):
            return None
        return active_rules[state["index"]]

    def refresh():
        rule = current_rule()
        progress.value = f"<b>Progress:</b> {state['index']} / {len(active_rules)} &nbsp;|&nbsp; <b>Kept:</b> {len(KEPT_ACTIVE_RULES_FROM_WIDGET)} &nbsp;|&nbsp; <b>Deactivated:</b> {len(DEACTIVATED_RULES_FROM_WIDGET)}"
        if rule is None:
            form_box.layout.display = "none"
            summary.value = f"<div style='border:1px solid #d1e7dd;background:#f0fff4;padding:14px;border-radius:8px;margin-top:8px;'><div style='font-size:18px;font-weight:700;color:#166534;margin-bottom:6px;'>✅ Deactivation review complete</div><div><b>Table:</b> {table_name}</div><div><b>Reviewed:</b> {len(KEPT_ACTIVE_RULES_FROM_WIDGET)+len(DEACTIVATED_RULES_FROM_WIDGET)} / {len(active_rules)}</div><div><b>Kept active:</b> {len(KEPT_ACTIVE_RULES_FROM_WIDGET)}</div><div><b>Deactivated:</b> {len(DEACTIVATED_RULES_FROM_WIDGET)}</div></div>"
            status.value = "<span style='color:#166534; font-weight:600;'>Deactivation review decisions are ready for metadata append.</span>"
            return
        summary.value = f"<div style='border:1px solid #e5e7eb;background:#fafafa;padding:12px;border-radius:8px;margin-top:8px;'><div style='font-weight:700;margin-bottom:8px;'>Rule {state['index']+1} of {len(active_rules)}</div><div><b>Rule ID:</b> <code>{rule.get('rule_id','')}</code></div><div><b>Rule type:</b> <code>{rule.get('rule_type','')}</code></div><div><b>Columns:</b> <code>{rule.get('columns',[])}</code></div></div>"
        reason_box.value = ""
        form_box.layout.display = ""
        status.value = ""

    def keep_clicked(_):
        rule=current_rule()
        if rule is None: return
        KEPT_ACTIVE_RULES_FROM_WIDGET.append(rule)
        state['index'] += 1
        refresh()

    def deactivate_clicked(_):
        rule=current_rule()
        if rule is None: return
        reason=str(reason_box.value).strip()
        if not reason:
            status.value = "<span style='color:red'><b>Deactivation reason is required.</b></span>"
            return
        DEACTIVATED_RULES_FROM_WIDGET.append({"rule": rule, "action_reason": reason})
        state['index'] += 1
        refresh()

    def undo_clicked(_):
        if state['index']==0:
            status.value = "<span style='color:orange'>Nothing to undo.</span>"
            return
        state['index'] -= 1
        rid = active_rules[state['index']].get('rule_id')
        KEPT_ACTIVE_RULES_FROM_WIDGET[:] = [r for r in KEPT_ACTIVE_RULES_FROM_WIDGET if r.get('rule_id') != rid]
        DEACTIVATED_RULES_FROM_WIDGET[:] = [r for r in DEACTIVATED_RULES_FROM_WIDGET if r.get('rule',{}).get('rule_id') != rid]
        refresh()

    keep_button.on_click(keep_clicked)
    deactivate_button.on_click(deactivate_clicked)
    undo_button.on_click(undo_clicked)

    ui = widgets.VBox([title, progress, summary, form_box, status], layout=widgets.Layout(border="1px solid #ddd", padding="12px", width="850px"))
    refresh()
    ipy_display(ui)
