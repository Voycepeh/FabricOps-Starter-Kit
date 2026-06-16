"""Table-scoped governance review helpers for ``03_governance`` notebooks."""

from __future__ import annotations

import ast
import importlib
import json
import re
import uuid
from typing import Any, Iterable, Mapping

from .config import DEFAULT_BUSINESS_CONTEXT_PROMPT_TEMPLATE, DEFAULT_DQ_RULE_SUGGESTION_PROMPT_TEMPLATE, DEFAULT_GOVERNANCE_PERSONAL_IDENTIFIER_PROMPT_TEMPLATE, _current_audit_timestamp, _get_audit_timezone
from .fabric_input_output import _configured_lakehouse_schema, read_lakehouse_table, write_lakehouse_table
from .data_profiling import profile_dataframe
from .metadata import _now_utc_iso, _resolve_action_by, _build_metadata_column_key, _build_metadata_table_key, _build_runtime_audit_fields, _build_dq_rule_key, _write_guardrail_result_row
from .data_agreement import DATA_AGREEMENT_TABLE, DATA_AGREEMENT_EVIDENCE_TABLE

CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
COLUMN_CONTEXT_TABLE = "METADATA_COLUMN_CONTEXT"
GUARDRAIL_RULES_TABLE = "METADATA_GUARDRAIL_RULES"
GUARDRAIL_RESULTS_TABLE = "METADATA_GUARDRAIL_RESULTS"
GUARDRAIL_TYPES = ["schema", "freshness", "profile_behavior", "dq"]
GUARDRAIL_REVIEW_STATUSES = ["draft", "proposed", "self_approved", "governance_approved", "bypass_active_pending_review", "rejected", "superseded"]
COLUMN_CLASSIFICATION_TABLE = "METADATA_COLUMN_CLASSIFICATION"
LINEAGE_TABLE = "METADATA_DATA_LINEAGE_TABLE"
PIPELINE_RUNS_TABLE = "METADATA_PIPELINE_RUNS"
GOVERNANCE_REVIEWS_TABLE = "METADATA_GOVERNANCE_REVIEWS"
SUCCESS_STATUSES = {"success", "succeeded", "passed", "complete", "completed", "ok"}
DQ_RULE_TYPES = [
    "not_null",
    "null_rate_below",
    "non_empty_string",
    "unique",
    "unique_combination",
    "accepted_values",
    "not_in_values",
    "between",
    "greater_than",
    "greater_than_or_equal",
    "less_than",
    "less_than_or_equal",
    "regex_match",
    "date_not_future",
    "date_between",
    "freshness",
    "max_age_days",
    "column_pair_equal",
    "column_a_gte_column_b",
    "column_a_gt_column_b",
    "required_when",
    "value_when",
    "expression_true",
]
SENSITIVITY_LABELS = ["classified", "restricted", "public"]
PERSONAL_DATA_CLASSIFICATIONS = ["direct PII", "indirect PII", "none"]
BUSINESS_CONTEXT_PROMPT = DEFAULT_BUSINESS_CONTEXT_PROMPT_TEMPLATE
PDPA_PERSONAL_IDENTIFIER_PROMPT = DEFAULT_GOVERNANCE_PERSONAL_IDENTIFIER_PROMPT_TEMPLATE
DQ_RULE_SUGGESTION_PROMPT = DEFAULT_DQ_RULE_SUGGESTION_PROMPT_TEMPLATE
AI_SUGGESTABLE_DQ_RULE_TYPES = set(DQ_RULE_TYPES)


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


def _canonical_dq_rule_type(rule_type: Any) -> str:
    return str(rule_type or "").strip()


def _normalize_dq_severity(severity: Any) -> str:
    """Normalize guardrail/DQ severity labels for DQ validation."""
    value = str(severity or "warning").strip().lower()
    return "error" if value in {"blocking", "error"} else "warning"


def _approved_review_context(profile_rows: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> tuple[dict[str, dict[str, Any]], str, str, dict[str, Any]]:
    actor = _resolve_action_by(approved_by)
    audit = _build_runtime_audit_fields(config=config, env=env or "", committed_by=actor) if config is not None and env is not None else {}
    return {str(_value(r, "column_name")): r for r in profile_rows}, actor, _now_utc_iso(config), audit


def _approved_column_identity(profile_row: dict[str, Any], review_row: dict[str, Any], *, env: str | None = None) -> dict[str, str]:
    col = str(review_row.get("column_name") or _value(profile_row, "column_name") or ((review_row.get("columns") or [""])[0]))
    env_name = str(_value(profile_row, "environment_name") or review_row.get("environment_name") or env or "")
    dataset = str(_value(profile_row, "dataset_name") or review_row.get("dataset_name") or "")
    table = str(_value(profile_row, "table_name") or review_row.get("table_name") or "")
    return {
        "metadata_column_key": str(_value(profile_row, "metadata_column_key") or review_row.get("metadata_column_key") or _build_metadata_column_key(env_name, dataset, table, col)),
        "metadata_table_key": str(_value(profile_row, "metadata_table_key") or review_row.get("metadata_table_key") or _build_metadata_table_key(env_name, dataset, table)),
        "environment_name": env_name,
        "dataset_name": dataset,
        "table_name": table,
        "column_name": col,
    }


def _spark_types():
    """Return Spark SQL type classes lazily so package import stays lightweight."""
    try:
        from pyspark.sql.types import BooleanType, DoubleType, LongType, StringType, StructField, StructType, TimestampType
    except Exception as exc:  # pragma: no cover - Fabric/runtime dependency guard
        raise RuntimeError("governance metadata schemas require pyspark.sql.types in the active runtime.") from exc
    return BooleanType, DoubleType, LongType, StringType, StructField, StructType, TimestampType


def _validate_schema_field_names(table_name: str, fields: list[tuple[str, Any]]) -> None:
    """Validate that a metadata schema has no case-insensitive duplicates.

    Parameters
    ----------
    table_name : str
        Physical metadata table being prepared.
    fields : list of tuple
        ``(name, data_type)`` pairs used to build a Spark ``StructType``.

    Raises
    ------
    ValueError
        Raised when two or more physical field names collapse to the same
        logical name under Spark/Delta's case-insensitive column resolution.

    """
    logical_names: dict[str, list[str]] = {}
    for name, _data_type in fields:
        logical_names.setdefault(str(name).lower(), []).append(str(name))
    duplicates = {logical: names for logical, names in logical_names.items() if len(names) > 1}
    if duplicates:
        details = "; ".join(f"{logical}: {', '.join(names)}" for logical, names in sorted(duplicates.items()))
        raise ValueError(
            f"{table_name} schema contains case-insensitive duplicate column names: {details}. "
            "Use one canonical physical column name for each logical column before creating the Spark StructType."
        )


def _schema(table_name: str, fields: list[tuple[str, Any]]):
    _validate_schema_field_names(table_name, fields)
    _, _, _, _, StructField, StructType, _ = _spark_types()
    return StructType([StructField(name, data_type, True) for name, data_type in fields])


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
        ("layer", string), ("asset_kind", string), ("pipeline_name", string), ("profile_run_id", string), ("profile_stage", string), ("profile_status", string),
        ("profiled_at", string), ("run_timestamp", timestamp), ("evidence_role", string),
        ("data_type", string), ("row_count", long), ("null_count", long), ("null_percent", double), ("distinct_count", long), ("distinct_percent", double),
        ("min_value", string), ("max_value", string), ("distribution_type", string), ("distribution_json", string),
        ("profile_mode", string), ("watermark_column", string), ("watermark_value", string), ("profile_hash", string), ("profile_payload_json", string),
        ("agreement_id", string), ("contract_version", string), ("notebook_registry_id", string), ("notebook_id", string),
        *audit,
    ]
    return {
        CATALOGUE_TABLE: _schema(CATALOGUE_TABLE, catalogue),
        COLUMN_CONTEXT_TABLE: _schema(COLUMN_CONTEXT_TABLE, [("metadata_column_key", string), ("metadata_table_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("business_context", string), ("notes", string), ("custom_fields_json", string), ("review_status", string), ("approved_by", string), ("approved_at", string), ("ai_suggestion_json", string), *audit]),
        GUARDRAIL_RULES_TABLE: _schema(GUARDRAIL_RULES_TABLE, [("rule_key", string), ("rule_id", string), ("metadata_column_key", string), ("metadata_table_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("guardrail_type", string), ("rule_type", string), ("rule_parameters_json", string), ("severity", string), ("description", string), ("is_active", boolean), ("review_status", string), ("author_role", string), ("created_by", string), ("created_at", string), ("approved_by", string), ("approved_at", string), ("ai_suggestion_json", string), ("action_type", string), ("source_notebook_type", string), ("source_notebook_id", string), ("source_workspace_id", string), ("superseded_by_rule_key", string), ("notes", string), ("approval_required", boolean), ("approval_bypassed", boolean), ("requires_post_review", boolean), ("bypass_reason", string), ("bypassed_by", string), ("bypassed_at", string), ("governance_mode", string), ("approval_policy", string), *audit]),
        GUARDRAIL_RESULTS_TABLE: _schema(GUARDRAIL_RESULTS_TABLE, [("result_id", string), ("run_id", string), ("rule_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("guardrail_type", string), ("rule_type", string), ("status", string), ("can_continue", boolean), ("severity", string), ("reason", string), ("expected_value_json", string), ("actual_value_json", string), ("result_payload_json", string), ("created_at", string), *audit]),
        COLUMN_CLASSIFICATION_TABLE: _schema(COLUMN_CLASSIFICATION_TABLE, [("metadata_column_key", string), ("metadata_table_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("sensitivity_label", string), ("personal_data_classification", string), ("pii_identifier_type", string), ("handling_requirement", string), ("reasoning", string), ("custom_fields_json", string), ("review_status", string), ("approved_by", string), ("approved_at", string), ("ai_suggestion_json", string), *audit]),
        LINEAGE_TABLE: _schema(LINEAGE_TABLE, [("lineage_id", string), ("dataset_name", string), ("run_id", string), ("source_table", string), ("target_table", string), ("source_table_key", string), ("target_table_key", string), ("transformation_steps_json", string), ("created_at", string), *audit]),
        PIPELINE_RUNS_TABLE: _schema(PIPELINE_RUNS_TABLE, [("run_id", string), ("agreement_id", string), ("agreement_contract_version", string), ("notebook_registry_id", string), ("notebook_id", string), ("notebook_type", string), ("pipeline_name", string), ("environment_name", string), ("started_at", string), ("completed_at", string), ("status", string), ("source_count", long), ("target_count", long), ("source_guardrail_status", string), ("target_guardrail_status", string), ("dq_status", string), ("lineage_status", string), ("catalogue_status", string), ("message", string), ("run_summary_json", string), ("created_at", string)]),
        GOVERNANCE_REVIEWS_TABLE: _schema(GOVERNANCE_REVIEWS_TABLE, [("review_id", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("metadata_table_key", string), ("profile_run_id", string), ("profile_stage", string), ("pipeline_run_id", string), ("agreement_id", string), ("agreement_contract_version", string), ("outcome", string), ("blocker_count", long), ("warning_count", long), ("blockers_json", string), ("warnings_json", string), ("evidence_summary_json", string), ("reviewed_at", string), ("reviewed_by", string), ("governance_mode", string), ("approval_policy", string), ("governance_status", string), ("approval_bypass_allowed", boolean), ("requires_post_review", boolean), ("policy_reason", string), ("effective_from", string), ("effective_to", string), *audit]),
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




def _first_present(row: dict[str, Any], names: Iterable[str], default: Any = "") -> Any:
    """Return the first present catalogue value from a list of candidate names."""
    for name in names:
        value = _value(row, name, None)
        if value not in (None, ""):
            return value
    return default


def _profile_sort_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    """Return deterministic newest-first profile ordering fields."""
    return (
        str(_value(row, "profiled_at")),
        str(_value(row, "profile_run_id")),
        str(_value(row, "run_id") or _value(row, "pipeline_run_id")),
        str(_value(row, "profile_stage")),
    )


def _catalogue_physical_identity(row: dict[str, Any]) -> dict[str, str]:
    """Return stable physical table identity without profile stage or pipeline identity."""
    env = str(_first_present(row, ["environment_name", "env_name"]))
    asset_kind = str(_first_present(row, ["asset_kind", "asset_type"]))
    asset_name = str(_first_present(row, ["asset_name", "dataset_name", "lakehouse_name", "warehouse_name"]))
    schema_or_layer = str(_first_present(row, ["schema_name", "layer"]))
    table = str(_value(row, "table_name"))
    table_key = str(_first_present(row, ["physical_asset_id", "metadata_table_key"], ""))
    if not table_key:
        table_key = _build_metadata_table_key(env, asset_name, table)
    return {
        "environment_name": env,
        "asset_kind": asset_kind,
        "asset_name": asset_name,
        "dataset_name": str(_value(row, "dataset_name") or asset_name),
        "schema_or_layer": schema_or_layer,
        "layer": str(_value(row, "layer") or schema_or_layer),
        "schema_name": str(_value(row, "schema_name") or schema_or_layer),
        "table_name": table,
        "metadata_table_key": table_key,
    }


def _catalogue_profile_target_model(catalogue_rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Build dependent governance profile target selector options."""
    rows = [dict(r) for r in catalogue_rows or []]
    if not rows:
        raise ValueError("METADATA_DATA_CATALOGUE has no rows. Run 02_pipeline profiling before 03_governance.")
    has_status = any(any(k.lower() == "profile_status" for k in r) for r in rows)
    table_groups: dict[tuple[str, str, str, str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        ident = _catalogue_physical_identity(row)
        if not ident["table_name"]:
            continue
        key = (ident["environment_name"], ident["asset_kind"], ident["asset_name"], ident["schema_or_layer"], ident["table_name"], ident["metadata_table_key"])
        table_groups.setdefault(key, []).append(row)
    if not table_groups:
        raise ValueError("METADATA_DATA_CATALOGUE has no table profile evidence for governance review.")

    assets: dict[str, dict[str, Any]] = {}
    for key, group in table_groups.items():
        env, kind, asset, schema, table, _table_key = key
        selectable_pool = [r for r in group if _is_success(r)] if has_status else group
        if not selectable_pool:
            continue
        latest = max(selectable_pool, key=_profile_sort_key)
        ident = _catalogue_physical_identity(latest)
        asset_label = " / ".join(part for part in [env, kind or "asset", asset] if part)
        assets.setdefault(asset_label, {"label": asset_label, "schemas": {}})
        schema_label = schema or "-"
        schema_entry = assets[asset_label]["schemas"].setdefault(schema_label, {"label": schema_label, "tables": {}})
        profiles = []
        seen_profiles = set()
        history_profiles = []
        for row in sorted(group, key=_profile_sort_key, reverse=True):
            p_ident = _catalogue_physical_identity(row)
            run_id = str(_value(row, "profile_run_id"))
            stage = str(_value(row, "profile_stage"))
            profiled_at = str(_value(row, "profiled_at"))
            pkey = (run_id, stage, profiled_at)
            if pkey in seen_profiles:
                continue
            seen_profiles.add(pkey)
            pipeline = str(_value(row, "pipeline_name") or _value(row, "notebook_id") or _value(row, "notebook_registry_id") or _value(row, "pipeline_run_id") or _value(row, "run_id"))
            label_parts = [profiled_at or "unknown profile date", f"run {run_id or '-'}"]
            if stage:
                label_parts.append(f"stage {stage}")
            if pipeline:
                label_parts.append(pipeline)
            profile = {**p_ident, "profile_run_id": run_id, "profile_stage": stage, "profiled_at": profiled_at, "profile_status": str(_value(row, "profile_status")), "label": " | ".join(label_parts)}
            if _is_success(row) or not has_status:
                profiles.append(profile)
            else:
                history_profiles.append({**profile, "reviewable": False, "history_only": True})
        default_identity = {**ident, "profile_run_id": str(_value(latest, "profile_run_id")), "profile_stage": str(_value(latest, "profile_stage")), "profiled_at": str(_value(latest, "profiled_at")), "profile_status": str(_value(latest, "profile_status"))}
        schema_entry["tables"][table] = {"label": table, "profiles": profiles, "history_profiles": history_profiles, "default": default_identity}
    if not assets:
        raise ValueError("METADATA_DATA_CATALOGUE has no successful table profile evidence for governance review.")
    return {"assets": assets, "has_status": has_status}


def load_catalogue_profile_rows(config: Any, env: str, selection: dict[str, Any], *, spark_session: Any) -> list[dict[str, Any]]:
    """Load column rows for the selected latest successful profile run."""
    rows = _coerce_rows(read_lakehouse_table(config, env, "metadata", CATALOGUE_TABLE, schema=_configured_lakehouse_schema(config, env, "metadata"), spark_session=spark_session))
    selection_identity = _catalogue_physical_identity(selection)
    filtered = []
    for row in rows:
        row_identity = _catalogue_physical_identity(row)
        if (
            _is_success(row)
            and row_identity == selection_identity
            and str(_value(row, "profile_run_id")) == str(selection["profile_run_id"])
            and str(_value(row, "profile_stage")) == str(selection["profile_stage"])
        ):
            filtered.append(row)
    if not filtered:
        raise ValueError("The selected successful profile has no column rows in METADATA_DATA_CATALOGUE.")
    return filtered


def _build_column_context_records(profile_rows: list[dict[str, Any]], reviewed_rows: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> list[dict[str, Any]]:
    """Build append-only approved business-context records from explicit reviews."""
    profile, actor, now, audit = _approved_review_context(profile_rows, config=config, env=env, approved_by=approved_by)
    rows = []
    for review in reviewed_rows or []:
        if str(review.get("review_status", "approved")).lower() != "approved" or not review.get("commit"):
            continue
        identity = _approved_column_identity(profile.get(str(review.get("column_name")), {}), review, env=env)
        rows.append({
            **identity,
            "business_context": str(review.get("business_context") or ""), "notes": str(review.get("notes") or ""),
            "custom_fields_json": _json(review.get("custom_fields") or review.get("custom_fields_json")), "review_status": "approved",
            "approved_by": actor, "approved_at": now, "ai_suggestion_json": _json(review.get("ai_suggestion_json") or review.get("ai_suggestion")), **audit,
        })
    return rows


def _dq_rule_parameter_payload(rule: dict[str, Any], columns: list[str]) -> dict[str, Any]:
    """Return rule parameters stored inside ``rule_parameters_json``."""
    metadata_fields = {
        "rule_key", "rule_id", "metadata_column_key", "metadata_table_key", "environment_name", "dataset_name",
        "table_name", "column_name", "rule_type", "rule_parameters", "rule_parameters_json", "severity",
        "description", "is_active", "review_status", "approved_by", "approved_at", "ai_suggestion_json",
        "ai_suggestion", "action_type", "commit", "_committed_at", "_committed_by", "_workspace_name",
        "_notebook_name", "_metadata_lakehouse_name", "_activity_id",
    }
    payload: dict[str, Any] = {"columns": columns}
    raw = rule.get("rule_parameters") or rule.get("rule_parameters_json") or {}
    if isinstance(raw, str) and raw.strip():
        try:
            raw = json.loads(raw)
        except Exception:
            raw = {}
    if isinstance(raw, dict):
        payload.update(raw)
    for key, value in rule.items():
        if key not in metadata_fields and value is not None:
            payload[key] = value
    payload["columns"] = columns
    return payload


def _build_dq_rule_records(profile_rows: list[dict[str, Any]], reviewed_rules: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> list[dict[str, Any]]:
    """Build append-only governance-approved DQ-rule records without enforcing them."""
    profile, actor, now, audit = _approved_review_context(profile_rows, config=config, env=env, approved_by=approved_by)
    rows = []
    for rule in reviewed_rules or []:
        if not rule.get("commit"):
            continue
        review_status = str(rule.get("review_status", "governance_approved")).lower()
        action_type = str(rule.get("action_type") or ("created" if rule.get("is_active", True) else "deactivated")).lower()
        if action_type == "delete":
            action_type = "deactivated"
        if action_type not in {"created", "updated", "deactivated", "reactivated"}:
            raise ValueError(f"Unsupported DQ action_type: {action_type}")
        is_active = bool(rule.get("is_active", action_type != "deactivated"))
        if action_type == "deactivated":
            is_active = False
        if action_type == "reactivated":
            is_active = True
        if review_status != "governance_approved":
            continue
        draft = dict(rule)
        draft["rule_type"] = _canonical_dq_rule_type(draft.get("rule_type"))
        if draft["rule_type"] != "expression_true":
            columns = draft.get("columns") or ([draft.get("column_name")] if draft.get("column_name") else [])
            if isinstance(columns, str):
                columns = [c.strip() for c in columns.split(",") if c.strip()]
            draft["columns"] = list(columns or [])
        _validate_dq_rules([draft])
        columns = [str(c) for c in draft.get("columns", [])]
        display_column = str(rule.get("column_name") or ", ".join(columns) or "")
        primary_column = columns[0] if columns else display_column
        identity = _approved_column_identity(profile.get(primary_column, {}), {**rule, "column_name": display_column, "columns": columns}, env=env)
        identity["column_name"] = display_column
        rule_id = str(rule.get("rule_id") or f"{identity['table_name']}.{display_column or 'table'}.{draft['rule_type']}")
        params = _dq_rule_parameter_payload(draft, columns)
        rows.append({
            "rule_key": str(rule.get("rule_key") or _build_dq_rule_key(identity["environment_name"], identity["dataset_name"], identity["table_name"], rule_id)),
            "rule_id": rule_id,
            **identity,
            "guardrail_type": str(rule.get("guardrail_type") or "dq"),
            "rule_type": draft["rule_type"],
            "rule_parameters_json": _json(params),
            "severity": _normalize_dq_severity(draft.get("severity")),
            "description": str(rule.get("description") or ""),
            "is_active": is_active,
            "review_status": str(rule.get("target_review_status") or "governance_approved"),
            "author_role": str(rule.get("author_role") or "governance_reviewer"),
            "created_by": str(rule.get("created_by") or actor),
            "created_at": str(rule.get("created_at") or now),
            "approved_by": str(rule.get("approved_by") or actor),
            "approved_at": str(rule.get("approved_at") or now),
            "ai_suggestion_json": _json(rule.get("ai_suggestion_json") or rule.get("ai_suggestion")),
            "action_type": action_type,
            "source_notebook_type": str(rule.get("source_notebook_type") or "03_governance"),
            "source_notebook_id": str(rule.get("source_notebook_id") or ""),
            "source_workspace_id": str(rule.get("source_workspace_id") or ""),
            "superseded_by_rule_key": str(rule.get("superseded_by_rule_key") or ""),
            "notes": str(rule.get("notes") or ""),
            **audit,
        })
    return rows

def _build_classification_records(profile_rows: list[dict[str, Any]], reviewed_rows: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> list[dict[str, Any]]:
    """Build append-only approved sensitivity and PII classification records."""
    profile, actor, now, audit = _approved_review_context(profile_rows, config=config, env=env, approved_by=approved_by)
    rows = []
    for review in reviewed_rows or []:
        if str(review.get("review_status", "approved")).lower() != "approved" or not review.get("commit"):
            continue
        sensitivity = str(review.get("sensitivity_label") or SENSITIVITY_LABELS[0])
        classification = str(review.get("pii_classification") or review.get("personal_data_classification") or PERSONAL_DATA_CLASSIFICATIONS[-1])
        if sensitivity not in SENSITIVITY_LABELS:
            raise ValueError(f"Unsupported sensitivity_label: {sensitivity}")
        if classification not in PERSONAL_DATA_CLASSIFICATIONS:
            raise ValueError(f"Unsupported personal_data_classification: {classification}")
        identity = _approved_column_identity(profile.get(str(review.get("column_name")), {}), review, env=env)
        rows.append({
            **identity,
            "sensitivity_label": sensitivity, "personal_data_classification": classification,
            "pii_identifier_type": str(review.get("pii_identifier_type") or ""), "handling_requirement": str(review.get("handling_requirement") or ""),
            "reasoning": str(review.get("reasoning") or ""), "custom_fields_json": _json(review.get("custom_fields") or review.get("custom_fields_json")), "review_status": "approved", "approved_by": actor, "approved_at": now,
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
    """Render standalone business-context review guidance for ``03_governance``.

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


def _enrichment_options(config: Any) -> tuple[list[str], list[str], list[dict[str, Any]], list[dict[str, Any]]]:
    """Return configured column metadata enrichment controls."""
    governance = getattr(config, "governance_config", None)
    sensitivity = list(getattr(governance, "sensitivity_labels", None) or SENSITIVITY_LABELS)
    pii = list(getattr(governance, "pii_classifications", None) or PERSONAL_DATA_CLASSIFICATIONS)
    context_fields = list(getattr(governance, "column_context_extra_fields", None) or [])
    classification_fields = list(getattr(governance, "column_classification_extra_fields", None) or [])
    return sensitivity, pii, context_fields, classification_fields


def _render_enrichment_extra_fields(widgets: Any, definitions: list[dict[str, Any]]) -> dict[str, Any]:
    """Render configured enrichment extra fields keyed by field name."""
    controls: dict[str, Any] = {}
    for definition in definitions:
        name = str(definition.get("name") or definition.get("key") or "").strip()
        if not name:
            raise ValueError("Custom enrichment fields require a name.")
        label = str(definition.get("label") or name.replace("_", " ").title())
        field_type = str(definition.get("type") or "text").lower()
        common = {"description": label, "layout": widgets.Layout(width="420px")}
        if field_type == "textarea":
            control = widgets.Textarea(value="", rows=int(definition.get("rows", 2)), **common)
        elif field_type in {"dropdown", "select"}:
            options = list(definition.get("options", []))
            control = widgets.Dropdown(options=options, value=options[0] if options else None, **common)
        else:
            control = widgets.Text(value="", **common)
        controls[name] = control
    return controls


def _collect_enrichment_extra_fields(controls: dict[str, Any]) -> dict[str, Any]:
    """Collect configured enrichment extra-field values."""
    return {name: control.value for name, control in controls.items()}


def _selected_catalogue_rows_for_enrichment(guardrail_state: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return selected column evidence from the guardrail target handover state."""
    rows = [dict(row) for row in guardrail_state.get("catalogue_profile_rows", []) if row.get("column_name")]
    profile_run_id = str(guardrail_state.get("profile_run_id") or "")
    profile_stage = str(guardrail_state.get("profile_stage") or "")
    if profile_run_id:
        rows = [row for row in rows if str(_value(row, "profile_run_id")) == profile_run_id]
    if profile_stage:
        rows = [row for row in rows if str(_value(row, "profile_stage")) == profile_stage]
    deduped: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=_profile_sort_key, reverse=True):
        deduped.setdefault(str(_value(row, "column_name")), row)
    return [deduped[name] for name in sorted(deduped)]


def _write_table_metadata_enrichment_records(
    context_records: list[dict[str, Any]],
    classification_records: list[dict[str, Any]],
    *,
    config: Any,
    env: str,
    spark_session: Any,
) -> None:
    """Write descriptive table metadata enrichment records only."""
    if context_records:
        write_lakehouse_table(
            spark_session.createDataFrame(context_records),
            config,
            env,
            "metadata",
            COLUMN_CONTEXT_TABLE,
            schema=_configured_lakehouse_schema(config, env, "metadata"),
            mode="append",
        )
    if classification_records:
        write_lakehouse_table(
            spark_session.createDataFrame(classification_records),
            config,
            env,
            "metadata",
            COLUMN_CLASSIFICATION_TABLE,
            schema=_configured_lakehouse_schema(config, env, "metadata"),
            mode="append",
        )


def widget_enrich_table_metadata(guardrail_state: Mapping[str, Any], *, config: Any, env: str, spark_session: Any) -> dict[str, Any]:
    """Render one consolidated column metadata enrichment widget.

    Parameters
    ----------
    guardrail_state : Mapping[str, Any]
        Target handover state returned by :func:`widget_select_guardrail_target`.
    config : Any
        Runtime configuration from ``00_env_config`` containing metadata routing
        and enrichment dropdown/custom-field settings.
    env : str
        Environment key used to route metadata writes to the configured
        ``metadata`` target.
    spark_session : Any
        Spark session used to create write DataFrames.

    Returns
    -------
    dict[str, Any]
        Widget state with rendered row controls, record builders, and a save
        callback. Save writes only ``METADATA_COLUMN_CONTEXT`` and
        ``METADATA_COLUMN_CLASSIFICATION`` records.

    Notes
    -----
    This widget enriches descriptive governance metadata for profiled catalogue
    columns. It does not write DQ rules, guardrail results, or catalogue profile
    evidence; runtime DQ remains part of guardrail authoring and review. Custom
    enrichment fields are stored as ``custom_fields_json`` to match the
    schema-safe ``01_agreement`` custom-field pattern without creating dynamic
    physical metadata columns.

    """
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    profile_rows = _selected_catalogue_rows_for_enrichment(guardrail_state)
    if not profile_rows:
        raise ValueError("Selected guardrail target has no column rows in METADATA_DATA_CATALOGUE.")
    sensitivity_options, pii_options, context_defs, classification_defs = _enrichment_options(config)
    row_controls: list[dict[str, Any]] = []
    row_widgets = []
    status = widgets.HTML(value="")

    for row in profile_rows:
        column_name = str(_value(row, "column_name"))
        data_type = str(_value(row, "data_type"))
        context_extra = _render_enrichment_extra_fields(widgets, context_defs)
        classification_extra = _render_enrichment_extra_fields(widgets, classification_defs)
        controls = {
            "column_name": column_name,
            "data_type": data_type,
            "business_context": widgets.Textarea(value="", description="Business context", rows=2, layout=widgets.Layout(width="520px")),
            "sensitivity_label": widgets.Dropdown(options=sensitivity_options, value=sensitivity_options[0], description="Sensitivity", layout=widgets.Layout(width="320px")),
            "pii_classification": widgets.Dropdown(options=pii_options, value=pii_options[-1], description="PII", layout=widgets.Layout(width="320px")),
            "commit": widgets.Checkbox(value=True, description="Commit/save"),
            "context_extra_fields": context_extra,
            "classification_extra_fields": classification_extra,
        }
        row_controls.append(controls)
        row_widgets.append(widgets.VBox([
            widgets.HTML(f"<b>{column_name}</b> <code>{data_type}</code>"),
            controls["business_context"],
            widgets.HBox([controls["sensitivity_label"], controls["pii_classification"], controls["commit"]]),
            *context_extra.values(),
            *classification_extra.values(),
        ]))

    def build_context_records() -> list[dict[str, Any]]:
        reviews = [{
            "column_name": controls["column_name"],
            "business_context": controls["business_context"].value,
            "custom_fields": _collect_enrichment_extra_fields(controls["context_extra_fields"]),
            "review_status": "approved",
            "commit": bool(controls["commit"].value),
        } for controls in row_controls]
        return _build_column_context_records(profile_rows, reviews, config=config, env=env)

    def build_classification_records() -> list[dict[str, Any]]:
        reviews = [{
            "column_name": controls["column_name"],
            "sensitivity_label": controls["sensitivity_label"].value,
            "pii_classification": controls["pii_classification"].value,
            "custom_fields": _collect_enrichment_extra_fields(controls["classification_extra_fields"]),
            "review_status": "approved",
            "commit": bool(controls["commit"].value),
        } for controls in row_controls]
        return _build_classification_records(profile_rows, reviews, config=config, env=env)

    def save(_: Any = None) -> dict[str, list[dict[str, Any]]]:
        context_records = build_context_records()
        classification_records = build_classification_records()
        _write_table_metadata_enrichment_records(
            context_records,
            classification_records,
            config=config,
            env=env,
            spark_session=spark_session,
        )
        status.value = f"Saved {len(context_records)} context rows and {len(classification_records)} classification rows."
        return {"column_context": context_records, "column_classification": classification_records}

    save_button = widgets.Button(description="Save enrichment", button_style="success")
    save_button.on_click(save)
    ip.display(widgets.VBox([widgets.HTML("<h3>Enrich table metadata</h3>"), *row_widgets, save_button, status]))
    return {
        "rows": row_controls,
        "build_context_records": build_context_records,
        "build_classification_records": build_classification_records,
        "save": save,
        "save_button": save_button,
        "status": status,
    }


def _dq_rule_parameters_summary(rule: dict[str, Any]) -> str:
    """Return compact display text for non-identity DQ parameters."""
    params = dict(rule.get("rule_parameters") or {})
    raw = rule.get("rule_parameters_json")
    if raw and not params:
        try:
            params = json.loads(raw) if isinstance(raw, str) else dict(raw)
        except Exception:
            params = {}
    if not params:
        params = {k: v for k, v in rule.items() if k in {
            "max_null_percent", "allowed_values", "blocked_values", "min_value", "max_value", "value",
            "regex_pattern", "max_age_days", "condition", "expected_value", "expression",
        }}
    params.pop("columns", None)
    return ", ".join(f"{k}={v}" for k, v in sorted(params.items()))


def _dq_rule_display_rows(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return table-shaped rows for active and inactive selected-table rules."""
    rows = []
    for rule in rules or []:
        params = rule.get("rule_parameters") or {}
        raw = rule.get("rule_parameters_json")
        if raw and not params:
            try:
                params = json.loads(raw) if isinstance(raw, str) else {}
            except Exception:
                params = {}
        cols = params.get("columns") or rule.get("columns") or rule.get("column_name") or ""
        if isinstance(cols, list):
            cols_display = ", ".join(str(c) for c in cols)
        else:
            cols_display = str(cols)
        rows.append({
            "Rule ID": str(rule.get("rule_id") or ""),
            "Rule type": _canonical_dq_rule_type(rule.get("rule_type")),
            "Column(s)": cols_display,
            "Parameters summary": _dq_rule_parameters_summary(rule),
            "Severity": str(rule.get("severity") or "warning"),
            "Status": "active" if bool(rule.get("is_active", True)) else "inactive",
            "Review status": str(rule.get("review_status") or ""),
            "Approved by": str(rule.get("approved_by") or ""),
            "Approved at": str(rule.get("approved_at") or ""),
            "Last action": str(rule.get("action_type") or ""),
            "Committed at": str(rule.get("_committed_at") or ""),
            "Description": str(rule.get("description") or ""),
        })
    return rows


def _parse_dq_ai_suggestions(response_rows: Any, *, response_col: str = "response", table_name: str | None = None) -> list[dict[str, Any]]:
    """Parse and validate draft AI DQ suggestions without approving them."""
    suggestions = _extract_assignment_payload(response_rows, response_col=response_col, assignment_key="DQ_RULES", table_name=table_name)
    drafts = []
    for index, suggestion in enumerate(suggestions):
        draft = dict(suggestion)
        draft.setdefault("rule_id", f"ai_dq_rule_{index + 1}")
        draft.setdefault("severity", "warning")
        draft.setdefault("description", "AI suggested draft; review before approval.")
        draft["rule_type"] = _canonical_dq_rule_type(draft.get("rule_type"))
        _validate_dq_rules([draft])
        draft["review_status"] = "draft"
        draft["is_active"] = False
        drafts.append(draft)
    return drafts


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



def _latest_row(rows: list[dict[str, Any]], *order_fields: str) -> dict[str, Any] | None:
    """Return the latest row using lexicographic string timestamps/ids."""
    if not rows:
        return None
    return max(rows, key=lambda row: tuple(str(_value(row, field)) for field in order_fields))


def _status_is_failed(value: Any) -> bool:
    return str(value or "").strip().lower() in {"failed", "fail", "error", "errors", "rejected"}


def _status_is_warning(value: Any) -> bool:
    return str(value or "").strip().lower() in {"warning", "warnings", "needs_remediation", "drift"}


def _read_metadata_rows(config: Any, env: str, table: str, *, spark_session: Any) -> list[dict[str, Any]]:
    return _coerce_rows(read_lakehouse_table(config, env, "metadata", table, schema=_configured_lakehouse_schema(config, env, "metadata"), spark_session=spark_session))


def _review_governance_evidence(
    config: Any,
    env: str,
    selection: dict[str, Any],
    *,
    spark_session: Any,
    reviewed_by: str | None = None,
    mode: str = "append",
) -> dict[str, Any]:
    """Review persisted v1 evidence and write a governance outcome row.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Shared ``00_env_config`` configuration used for metadata lakehouse routing.
    env : str
        Environment key in ``config``.
    selection : dict[str, Any]
        Catalogue-table selection returned by ``get_selected_catalogue_table``.
    spark_session : pyspark.sql.SparkSession
        Spark session used to read and write metadata tables.
    reviewed_by : str, optional
        Reviewer identity. Runtime user metadata is used when omitted.
    mode : str, default="append"
        Write mode for ``METADATA_GOVERNANCE_REVIEWS``.

    Returns
    -------
    dict[str, Any]
        Governance review row plus blocker, warning, and evidence details.

    Notes
    -----
    The function intentionally re-reads agreement, catalogue, pipeline-run, and
    evidence metadata from the configured ``metadata`` target so ``03_governance``
    can run in a separate session after ``02_pipeline``.

    """
    profile_rows = load_catalogue_profile_rows(config, env, selection, spark_session=spark_session)
    first_profile = profile_rows[0]
    env_name = str(_value(first_profile, "environment_name") or selection.get("environment_name") or env)
    dataset_name = str(_value(first_profile, "dataset_name") or selection.get("dataset_name") or "")
    table_name = str(_value(first_profile, "table_name") or selection.get("table_name") or "")
    table_key = str(_value(first_profile, "metadata_table_key") or selection.get("metadata_table_key") or _build_metadata_table_key(env_name, dataset_name, table_name))
    profile_run_id = str(_value(first_profile, "profile_run_id") or selection.get("profile_run_id") or "")
    profile_stage = str(_value(first_profile, "profile_stage") or selection.get("profile_stage") or "")
    agreement_id = str(_value(first_profile, "agreement_id") or _value(first_profile, "AGREEMENT_ID") or "")
    agreement_contract_version = str(_value(first_profile, "contract_version") or _value(first_profile, "AGREEMENT_CONTRACT_VERSION") or "")

    all_pipeline_rows = [
        row for row in _read_metadata_rows(config, env, PIPELINE_RUNS_TABLE, spark_session=spark_session)
        if str(_value(row, "environment_name")) == env_name
    ]
    related_pipeline_rows = [
        row for row in all_pipeline_rows
        if not agreement_id or str(_value(row, "agreement_id")) == agreement_id
    ]
    pipeline_rows = [
        row for row in related_pipeline_rows
        if not profile_run_id or str(_value(row, "run_id")) == profile_run_id
    ]
    latest_pipeline = _latest_row(pipeline_rows, "completed_at", "created_at", "run_id")

    agreement_rows = [
        row for row in _read_metadata_rows(config, env, DATA_AGREEMENT_TABLE, spark_session=spark_session)
        if agreement_id and str(_value(row, "agreement_id")) == agreement_id
        and (not agreement_contract_version or str(_value(row, "contract_version")) == agreement_contract_version)
    ]
    attachment_rows = [
        row for row in _read_metadata_rows(config, env, DATA_AGREEMENT_EVIDENCE_TABLE, spark_session=spark_session)
        if agreement_id and str(_value(row, "agreement_id")) == agreement_id
        and (not agreement_contract_version or str(_value(row, "contract_version")) == agreement_contract_version)
    ]

    blockers: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    def _append_once(items: list[dict[str, str]], *, code: str, message: str) -> None:
        if not any(item.get("code") == code for item in items):
            items.append({"code": code, "message": message})

    if not agreement_id:
        _append_once(blockers, code="missing_agreement_id", message="Catalogue evidence is not linked to an agreement.")
    elif not agreement_rows:
        _append_once(blockers, code="missing_agreement_metadata", message="No matching agreement metadata row was found.")
    if latest_pipeline is None:
        _append_once(blockers, code="missing_pipeline_run", message="No matching pipeline run summary was found.")
    elif _status_is_failed(_value(latest_pipeline, "status")):
        _append_once(blockers, code="pipeline_failed", message="Latest pipeline run did not complete successfully.")

    dq_statuses = {str(_value(row, "dq_status") or "").lower() for row in profile_rows}
    dq_error_count = sum(int(_value(row, "dq_error_rule_count", 0) or 0) for row in profile_rows)
    dq_failed_count = sum(int(_value(row, "dq_failed_rule_count", 0) or 0) for row in profile_rows)
    if "failed" in dq_statuses or dq_error_count > 0:
        _append_once(blockers, code="dq_failed", message="Failed DQ evidence blocks approval.")
    elif "warning" in dq_statuses or dq_failed_count > 0:
        _append_once(warnings, code="dq_warning", message="DQ warning evidence requires remediation review.")

    if latest_pipeline is not None:
        pipeline_dq_status = _value(latest_pipeline, "dq_status")
        if _status_is_failed(pipeline_dq_status):
            _append_once(blockers, code="dq_failed", message="Pipeline DQ status blocks approval.")
        elif _status_is_warning(pipeline_dq_status):
            _append_once(warnings, code="dq_warning", message="Pipeline DQ status requires remediation review.")

        for field in ("source_guardrail_status", "target_guardrail_status"):
            status = _value(latest_pipeline, field)
            if _status_is_failed(status):
                blockers.append({"code": f"{field}_failed", "message": f"{field} is {status}; schema drift or guardrail failure is present."})
            elif _status_is_warning(status):
                warnings.append({"code": f"{field}_warning", "message": f"{field} is {status}; schema drift is surfaced for review."})

    outcome = "rejected" if blockers else ("needs_remediation" if warnings else "approved")
    reviewed_at = _now_utc_iso(config)
    actor = _resolve_action_by(reviewed_by)
    audit = _build_runtime_audit_fields(config=config, env=env, committed_by=actor, committed_at=reviewed_at)
    evidence_summary = {
        "agreement_row_count": len(agreement_rows),
        "agreement_attachment_count": len(attachment_rows),
        "profile_column_count": len(profile_rows),
        "pipeline_run_count": len(pipeline_rows),
        "related_pipeline_run_count": len(related_pipeline_rows),
        "prior_pipeline_run_ids": [str(_value(row, "run_id")) for row in related_pipeline_rows if str(_value(row, "run_id")) != profile_run_id],
        "latest_pipeline_run": latest_pipeline or {},
    }
    row = {
        "review_id": f"{profile_run_id or 'profile'}-{uuid.uuid4().hex[:12]}",
        "environment_name": env_name,
        "dataset_name": dataset_name,
        "table_name": table_name,
        "metadata_table_key": table_key,
        "profile_run_id": profile_run_id,
        "profile_stage": profile_stage,
        "pipeline_run_id": str(_value(latest_pipeline or {}, "run_id")),
        "agreement_id": agreement_id,
        "agreement_contract_version": agreement_contract_version,
        "outcome": outcome,
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "blockers_json": json.dumps(blockers, sort_keys=True),
        "warnings_json": json.dumps(warnings, sort_keys=True),
        "evidence_summary_json": json.dumps(evidence_summary, default=str, sort_keys=True),
        "reviewed_at": reviewed_at,
        "reviewed_by": actor,
        **audit,
    }
    write_lakehouse_table(spark_session.createDataFrame([row]), config, env, "metadata", GOVERNANCE_REVIEWS_TABLE, schema=_configured_lakehouse_schema(config, env, "metadata"), mode=mode)
    return {"review": row, "outcome": outcome, "blockers": blockers, "warnings": warnings, "evidence_summary": evidence_summary}

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
    governance_selection: dict[str, Any] | None = None,
    write_governance_review: bool = False,
    mode: str = "append",
) -> dict[str, Any]:
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
        Human-reviewed rows from the governance review workflow. Business context
        and classification rows use ``review_status="approved"``. DQ rule rows
        use ``review_status="governance_approved"``. All rows must set
        ``commit=True`` to be written.
    approved_by : str, optional
        Reviewer identity to stamp on records. When omitted, runtime defaults
        are used.
    governance_selection : dict, optional
        Catalogue selection used to re-read persisted evidence and write a final
        governance outcome row.
    write_governance_review : bool, default=False
        Whether to append a ``METADATA_GOVERNANCE_REVIEWS`` outcome row after
        checking agreement, pipeline, schema/profile, and DQ evidence.
    mode : str, default "append"
        Write mode for metadata table commits.

    Returns
    -------
    dict[str, Any]
        Records written for ``column_context``, ``dq_rules``, and
        ``column_classification`` plus an optional ``governance_review`` outcome.

    Notes
    -----
    This is the v1 governance commit action for ``03_governance`` notebooks. It merges
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
        GUARDRAIL_RULES_TABLE: [dict(record, guardrail_type="dq") for record in dq_rule_records],
        COLUMN_CLASSIFICATION_TABLE: classification_records,
    }
    for table_name, records in writes.items():
        if records:
            write_lakehouse_table(spark_session.createDataFrame(records), config, env, "metadata", table_name, schema=_configured_lakehouse_schema(config, env, "metadata"), mode=mode)

    governance_review = None
    if write_governance_review:
        if governance_selection is None:
            raise ValueError("governance_selection is required when write_governance_review=True.")
        governance_review = _review_governance_evidence(
            config,
            env,
            governance_selection,
            spark_session=spark_session,
            reviewed_by=approved_by,
            mode=mode,
        )

    return {
        "column_context": context_records,
        "dq_rules": dq_rule_records,
        "column_classification": classification_records,
        "governance_review": governance_review,
    }


def _spark_sql_helpers():
    """Return Spark SQL helper modules lazily for DQ runtime helpers."""
    try:
        from pyspark.sql import SparkSession, functions as F
        from pyspark.sql.window import Window
    except Exception as exc:  # pragma: no cover - Fabric/runtime dependency guard
        raise RuntimeError("DQ enforcement helpers require pyspark in the active runtime.") from exc
    return SparkSession, F, Window


def _run_fabric_ai_drafting(prepared_profile_df, *, prompt: str, output_col: str):
    """Run Fabric AI prompt drafting against prepared profile rows."""
    ai = getattr(prepared_profile_df, "ai", None)
    if ai is None or not hasattr(ai, "generate_response"):
        raise RuntimeError("AI drafting requires Fabric DataFrame.ai.generate_response.")
    return prepared_profile_df.ai.generate_response(prompt=prompt, is_prompt_template=True, output_col=output_col)


def _parse_ai_dict_response(text: str) -> dict[str, Any]:
    """Parse JSON/Python-dict AI response text into a dictionary."""
    cleaned = str(text or "").strip()
    match = re.search(r"^[A-Z_]+\s*=\s*(\{.*\})\s*$", cleaned, flags=re.DOTALL)
    if match:
        cleaned = match.group(1)
    if not cleaned:
        return {}
    for loader in (json.loads, ast.literal_eval):
        try:
            obj = loader(cleaned)
        except Exception:
            continue
        if isinstance(obj, dict):
            return obj
    return {}


def _extract_assignment_payload(response_rows, *, response_col: str, assignment_key: str | None = None, table_name: str | None = None) -> list[dict[str, Any]]:
    """Extract dictionary payloads from AI response rows with optional table-key narrowing."""
    out: list[dict[str, Any]] = []
    for row in _coerce_rows(response_rows):
        parsed = _parse_ai_dict_response(row.get(response_col) or row.get("response") or row.get("ai_response") or "")
        if not parsed:
            continue
        payload = parsed.get(assignment_key, parsed) if assignment_key else parsed
        if table_name is not None:
            payload = payload.get(table_name, []) if isinstance(payload, dict) else []
        if isinstance(payload, list):
            out.extend(dict(item) for item in payload if isinstance(item, dict))
        elif isinstance(payload, dict):
            out.append(payload)
    return out


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

        if rtype in {"not_null", "non_empty_string", "required_when"}:
            require_columns(rule, minimum=1)
        elif rtype in {
            "null_rate_below", "unique", "accepted_values", "not_in_values", "between",
            "greater_than", "greater_than_or_equal", "less_than", "less_than_or_equal",
            "regex_match", "date_not_future", "date_between", "freshness", "max_age_days", "value_when",
        }:
            require_columns(rule, count=1)
        elif rtype == "unique_combination":
            require_columns(rule, minimum=2)
        elif rtype in {"column_pair_equal", "column_a_gte_column_b", "column_a_gt_column_b"}:
            require_columns(rule, count=2)
        elif rtype == "expression_true":
            if not str(rule.get("expression") or "").strip():
                raise ValueError(f"DQ rule '{rule['rule_id']}' requires expression.")

        if rtype == "null_rate_below" and rule.get("max_null_percent") is None:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires max_null_percent.")
        if rtype == "accepted_values" and "allowed_values" not in rule:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires allowed_values.")
        if rtype == "not_in_values" and "blocked_values" not in rule:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires blocked_values.")
        if rtype in {"between", "date_between"} and rule.get("min_value") is None and rule.get("max_value") is None:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires min_value or max_value.")
        if rtype in {"greater_than", "greater_than_or_equal", "less_than", "less_than_or_equal"} and rule.get("value") is None:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires value.")
        if rtype == "regex_match" and not str(rule.get("regex_pattern") or ""):
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires regex_pattern.")
        if rtype in {"freshness", "max_age_days"} and rule.get("max_age_days") is None:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires max_age_days.")
        if rtype == "required_when" and not str(rule.get("condition") or "").strip():
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires condition.")
        if rtype == "value_when":
            if not str(rule.get("condition") or "").strip():
                raise ValueError(f"DQ rule '{rule['rule_id']}' requires condition.")
            if "expected_value" not in rule:
                raise ValueError(f"DQ rule '{rule['rule_id']}' requires expected_value.")
    return rules

def _latest_dq_rule_versions(metadata_df, table_name: str, env_name: str | None = None, dataset_name: str | None = None):
    """Resolve latest append-only DQ metadata rows by stable rule identity."""
    _, F, Window = _spark_sql_helpers()
    columns = set(getattr(metadata_df, "columns", []))
    if "rule_key" in columns:
        partition_cols = ["rule_key"]
    elif "rule_id" in columns:
        partition_cols = ["rule_id"]
    else:
        partition_cols = [name for name in ("metadata_table_key", "column_name", "rule_type") if name in columns]
    order_cols = [name for name in ("_committed_at", "approved_at") if name in columns]
    if not partition_cols:
        raise ValueError("DQ metadata must include rule_key or rule identity columns.")
    scoped = metadata_df.filter(F.col("table_name") == table_name) if "table_name" in columns else metadata_df
    if env_name is not None and "environment_name" in columns:
        scoped = scoped.filter(F.col("environment_name") == env_name)
    if dataset_name is not None and "dataset_name" in columns:
        scoped = scoped.filter(F.col("dataset_name") == dataset_name)
    if not order_cols:
        return scoped
    w = Window.partitionBy(*[F.col(name) for name in partition_cols]).orderBy(*[F.col(name).desc_nulls_last() for name in order_cols])
    return scoped.withColumn("_rn", F.row_number().over(w)).filter(F.col("_rn") == 1).drop("_rn")


def _load_active_dq_rules(metadata_df, table_name: str, env_name: str | None = None, dataset_name: str | None = None) -> list[dict[str, Any]]:
    """Load active DQ guardrail rules from append-only metadata rows."""
    _, F, _ = _spark_sql_helpers()
    columns = set(getattr(metadata_df, "columns", []))
    latest = _latest_dq_rule_versions(metadata_df, table_name, env_name=env_name, dataset_name=dataset_name)
    if "is_active" not in columns:
        return []
    latest = latest.filter(F.col("is_active") == True)
    if "action_type" in columns:
        latest = latest.filter(F.lower(F.coalesce(F.col("action_type"), F.lit("created"))) != "deactivated")
    if "review_status" not in columns:
        return []
    latest = latest.filter(F.lower(F.col("review_status")).isin("self_approved", "governance_approved", "bypass_active_pending_review"))

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
                "rule_type": _canonical_dq_rule_type(row.get("rule_type")),
                "columns": rule_columns,
                "severity": _normalize_dq_severity(row.get("severity")),
                "description": str(row.get("description") or ""),
                "review_status": str(row.get("review_status") or ""),
                **params,
            }
        )
    return _validate_dq_rules(rules)



def _dq_failed_expression(df, rule: dict[str, Any]):
    """Build a Spark boolean expression identifying rows that fail one DQ rule."""
    _, F, Window = _spark_sql_helpers()
    rule = _validate_dq_rules([dict(rule)])[0]
    rtype = str(rule["rule_type"])
    cols = [str(column) for column in rule.get("columns", [])]
    dataframe_columns = set(getattr(df, "columns", []))
    missing_columns = [column for column in cols if column not in dataframe_columns]
    expression = str(rule.get("expression") or "")
    if rtype != "expression_true" and missing_columns:
        return F.lit(True)
    col_name = cols[0] if cols else None

    def empty_string(column: str):
        return F.col(column).isNull() | (F.trim(F.col(column).cast("string")) == "")

    def cast_for_compare(column):
        return F.col(column)

    if rtype == "not_null":
        failed = F.col(cols[0]).isNull()
        for c in cols[1:]:
            failed = failed | F.col(c).isNull()
    elif rtype == "null_rate_below":
        total = int(df.count())
        null_count = int(df.filter(F.col(col_name).isNull()).count()) if total else 0
        failed = F.col(col_name).isNull() if total and ((null_count / total) * 100) > float(rule["max_null_percent"]) else F.lit(False)
    elif rtype == "non_empty_string":
        failed = empty_string(cols[0])
        for c in cols[1:]:
            failed = failed | empty_string(c)
    elif rtype in {"unique", "unique_combination"}:
        failed = F.count(F.lit(1)).over(Window.partitionBy(*[F.col(c) for c in cols])) > F.lit(1)
    elif rtype == "accepted_values":
        failed = F.col(col_name).isNotNull() & ~F.col(col_name).isin(list(rule["allowed_values"]))
    elif rtype == "not_in_values":
        failed = F.col(col_name).isNotNull() & F.col(col_name).isin(list(rule["blocked_values"]))
    elif rtype in {"between", "date_between"}:
        value_col = cast_for_compare(col_name)
        cond = F.lit(False)
        if rule.get("min_value") is not None:
            cond = cond | (value_col < F.lit(rule["min_value"]))
        if rule.get("max_value") is not None:
            cond = cond | (value_col > F.lit(rule["max_value"]))
        failed = F.col(col_name).isNotNull() & cond
    elif rtype == "greater_than":
        failed = F.col(col_name).isNotNull() & ~(F.col(col_name) > F.lit(rule["value"]))
    elif rtype == "greater_than_or_equal":
        failed = F.col(col_name).isNotNull() & ~(F.col(col_name) >= F.lit(rule["value"]))
    elif rtype == "less_than":
        failed = F.col(col_name).isNotNull() & ~(F.col(col_name) < F.lit(rule["value"]))
    elif rtype == "less_than_or_equal":
        failed = F.col(col_name).isNotNull() & ~(F.col(col_name) <= F.lit(rule["value"]))
    elif rtype == "regex_match":
        failed = F.col(col_name).isNotNull() & ~F.col(col_name).cast("string").rlike(rule["regex_pattern"])
    elif rtype == "date_not_future":
        failed = F.col(col_name).isNotNull() & (F.to_date(F.col(col_name)) > F.current_date())
    elif rtype in {"freshness", "max_age_days"}:
        failed = F.col(col_name).isNotNull() & (F.to_date(F.col(col_name)) < F.date_sub(F.current_date(), int(rule["max_age_days"])))
    elif rtype == "column_pair_equal":
        failed = ~F.col(cols[0]).eqNullSafe(F.col(cols[1]))
    elif rtype == "column_a_gte_column_b":
        one_null = F.col(cols[0]).isNull() != F.col(cols[1]).isNull()
        both_non_null_and_invalid = F.col(cols[0]).isNotNull() & F.col(cols[1]).isNotNull() & ~(F.col(cols[0]) >= F.col(cols[1]))
        failed = one_null | both_non_null_and_invalid
    elif rtype == "column_a_gt_column_b":
        one_null = F.col(cols[0]).isNull() != F.col(cols[1]).isNull()
        both_non_null_and_invalid = F.col(cols[0]).isNotNull() & F.col(cols[1]).isNotNull() & ~(F.col(cols[0]) > F.col(cols[1]))
        failed = one_null | both_non_null_and_invalid
    elif rtype == "required_when":
        condition = F.expr(str(rule["condition"]))
        missing = empty_string(cols[0])
        for c in cols[1:]:
            missing = missing | empty_string(c)
        failed = condition & missing
    elif rtype == "value_when":
        condition = F.expr(str(rule["condition"]))
        failed = condition & ~F.col(col_name).eqNullSafe(F.lit(rule["expected_value"]))
    elif rtype == "expression_true":
        failed = ~F.expr(expression)
    else:
        raise ValueError(f"Unsupported rule_type: {rtype}")
    return F.coalesce(failed, F.lit(False))

def _dq_check_status(severity: str, failed_count: int) -> str:
    if failed_count <= 0:
        return "passed"
    return "failed" if str(severity).strip().lower() == "error" else "warning"


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
        check_status = _dq_check_status(severity, failed_count)
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


def _dq_failed_row_count(df, rules: list[dict[str, Any]]) -> int:
    """Return the count of rows that failed at least one DQ rule."""
    _, F, _ = _spark_sql_helpers()
    if not rules:
        return 0
    failed_columns = [F.when(_dq_failed_expression(df, rule), F.lit(1)).otherwise(F.lit(0)) for rule in rules]
    failed_row = failed_columns[0]
    for column in failed_columns[1:]:
        failed_row = failed_row + column
    failed_rows = df.select(F.when(failed_row > F.lit(0), F.lit(1)).otherwise(F.lit(0)).alias("failed"))
    return int(failed_rows.agg(F.sum("failed").alias("failed_count")).collect()[0]["failed_count"] or 0)


def _dq_summary(checks: list[dict[str, Any]], total_count: int, failed_row_count: int, *, config: Any = None) -> dict[str, Any]:
    """Build aggregate DQ fields for catalogue/profile evidence."""
    failed_checks = [check for check in checks if not bool(check.get("passed", False))]
    warning_checks = [check for check in failed_checks if check.get("severity") == "warning"]
    error_checks = [check for check in failed_checks if check.get("severity") == "error"]
    status = _summarize_dq_guardrail(checks)["status"]
    return {
        "DQ_STATUS": status,
        "DQ_RULE_COUNT": len(checks),
        "DQ_FAILED_RULE_COUNT": len(failed_checks),
        "DQ_WARNING_RULE_COUNT": len(warning_checks),
        "DQ_ERROR_RULE_COUNT": len(error_checks),
        "DQ_FAILED_ROW_COUNT": failed_row_count,
        "DQ_FAILED_ROW_PERCENT": float(round((failed_row_count / total_count) * 100, 4)) if total_count else 0.0,
        "DQ_CHECKED_AT": _current_audit_timestamp(config=config, drop_microseconds=False),
    }


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
    schema = _configured_lakehouse_schema(config, env, "metadata")
    frame = read_lakehouse_table(config, env, "metadata", GUARDRAIL_RULES_TABLE, schema=schema, spark_session=spark_session)
    if "guardrail_type" in set(getattr(frame, "columns", [])):
        _, F, _ = _spark_sql_helpers()
        return frame.filter(F.lower(F.coalesce(F.col("guardrail_type"), F.lit(""))) == "dq")
    return frame

def enforce_dq_rules(
    dataframe,
    config,
    env,
    dataset_name,
    table_name,
    *,
    spark_session=None,
    run_id: str = "",
    write_results: bool = False,
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
        Environment name used to read ``METADATA_GUARDRAIL_RULES`` from the
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
    ``METADATA_GUARDRAIL_RULES`` via the configured metadata route and writes the aggregate runtime
    outcome to ``METADATA_GUARDRAIL_RESULTS`` when result writing is enabled. It
    does not quarantine rows, write row-level failure metadata, filter invalid
    rows, send alerts, or partially write targets.

    """
    metadata_df = _read_guardrail_rule_metadata(config, env, spark_session=spark_session)
    rules = _load_active_dq_rules(metadata_df, table_name=table_name, env_name=env, dataset_name=dataset_name)
    checks = _run_dq_guardrail_checks(dataframe, table_name=table_name, rules=rules) if rules else []
    total_count = int(dataframe.count())
    failed_row_count = _dq_failed_row_count(dataframe, rules) if rules else 0
    result = _summarize_dq_guardrail(checks)
    if any(str(rule.get("review_status") or "").lower() == "bypass_active_pending_review" for rule in rules):
        warning = "Rule is active through approval bypass and requires governance post-review."
        result["reason"] = warning if not result.get("reason") else f"{result.get('reason')} {warning}"
        result["bypass_warning"] = warning
    result["dataframe"] = _dq_tagged_dataframe(dataframe, rules)
    result["summary"] = _dq_summary(checks, total_count, failed_row_count, config=config)
    if write_results:
        _write_guardrail_result_row(
            spark_session=spark_session,
            config=config,
            env=env,
            run_id=run_id,
            dataset_name=dataset_name,
            table_name=table_name,
            guardrail_type="dq",
            rule_type="active_rules",
            result=result,
            rule_key="dq_active_rules",
        )
    return result


def _prepare_dq_profile_input_rows(*, profile_df=None, df=None, table_name: str, business_context: str = "", config: Any = None):
    """Prepare DQ prompt profile rows from a profile DataFrame or raw DataFrame."""
    if (profile_df is None) == (df is None):
        raise ValueError("Provide exactly one of profile_df or df.")
    if profile_df is None:
        profile_df = profile_dataframe(df, table_name=table_name, config=config)
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
        F.lit(_current_audit_timestamp(config=config, drop_microseconds=False)).alias("profile_timestamp"),
    )


def _draft_dq_rules(*, profile_df=None, df=None, table_name: str, business_context: str = "", prompt_template: str | None = None, output_col: str = "response", config: Any = None) -> list[dict[str, Any]]:
    """Draft candidate DQ rules from metadata profiles or a raw DataFrame fallback."""
    prepared = _prepare_dq_profile_input_rows(profile_df=profile_df, df=df, table_name=table_name, business_context=business_context, config=config)
    responses = _run_fabric_ai_drafting(prepared, prompt=prompt_template or DQ_RULE_SUGGESTION_PROMPT, output_col=output_col)
    candidates = _extract_assignment_payload(responses, response_col=output_col, assignment_key="DQ_RULES", table_name=table_name)
    by_id = {r.get("rule_id"): {**r, "rule_type": _canonical_dq_rule_type(r.get("rule_type"))} for r in candidates if r.get("rule_id")}
    rules = list(by_id.values())
    _validate_dq_rules(rules)
    return rules


def resolve_table_governance_policy(governance_rows: Any, *, environment_name: str = "", dataset_name: str = "", table_name: str = "", metadata_table_key: str = "") -> dict[str, Any]:
    """Return the latest active table-level governance policy.

    Parameters
    ----------
    governance_rows : Any
        Governance review rows or a DataFrame-like object containing rows from
        ``METADATA_GOVERNANCE_REVIEWS``.
    environment_name, dataset_name, table_name, metadata_table_key : str, optional
        Table identity used to filter policy rows.

    Returns
    -------
    dict[str, Any]
        Effective policy. Tables default to ungoverned with no approval
        required unless the latest active policy row marks them governed.

    """
    default = {"governance_mode": "ungoverned", "approval_policy": "no_approval_required", "governance_status": "active", "approval_bypass_allowed": False, "requires_post_review": False}
    rows = []
    for row in _coerce_rows(governance_rows):
        if metadata_table_key and str(row.get("metadata_table_key") or "") not in {"", metadata_table_key}:
            continue
        if environment_name and str(row.get("environment_name") or "") not in {"", environment_name}:
            continue
        if dataset_name and str(row.get("dataset_name") or "") not in {"", dataset_name}:
            continue
        if table_name and str(row.get("table_name") or "") != table_name:
            continue
        if str(row.get("governance_status") or "active").lower() != "active":
            continue
        rows.append(row)
    if not rows:
        return default
    rows.sort(key=lambda row: str(row.get("effective_from") or row.get("reviewed_at") or row.get("_committed_at") or ""), reverse=True)
    latest = rows[0]
    mode = str(latest.get("governance_mode") or "ungoverned").lower()
    policy = str(latest.get("approval_policy") or ("approval_required" if mode == "governed" else "no_approval_required")).lower()
    return {**default, **latest, "governance_mode": mode, "approval_policy": policy, "approval_bypass_allowed": bool(latest.get("approval_bypass_allowed", policy == "approval_required_with_bypass"))}


def guardrail_authoring_status(policy: Mapping[str, Any], *, bypass_reason: str = "", actor: str | None = None, config: Any = None) -> dict[str, Any]:
    """Return rule lifecycle fields for engineering-authored guardrail rules.

    Parameters
    ----------
    policy : mapping
        Effective table governance policy.
    bypass_reason : str, optional
        User-entered justification when bypassing required approval.
    actor : str, optional
        Current user identifier.
    config : Any, optional
        Runtime configuration used for timestamp formatting.

    Returns
    -------
    dict[str, Any]
        Lifecycle fields for a ``METADATA_GUARDRAIL_RULES`` row.

    """
    governed = str(policy.get("governance_mode") or "ungoverned").lower() == "governed"
    if not governed:
        return {"is_active": True, "review_status": "self_approved", "approval_required": False, "approval_bypassed": False, "requires_post_review": False, "author_role": "engineering", "governance_mode": "ungoverned", "approval_policy": "no_approval_required"}
    if bypass_reason:
        return {"is_active": True, "review_status": "bypass_active_pending_review", "approval_required": True, "approval_bypassed": True, "requires_post_review": True, "bypass_reason": bypass_reason, "bypassed_by": _resolve_action_by(actor), "bypassed_at": _now_utc_iso(config), "author_role": "engineering", "governance_mode": "governed", "approval_policy": str(policy.get("approval_policy") or "approval_required_with_bypass")}
    return {"is_active": False, "review_status": "proposed", "approval_required": True, "approval_bypassed": False, "requires_post_review": False, "author_role": "engineering", "governance_mode": "governed", "approval_policy": str(policy.get("approval_policy") or "approval_required")}


def apply_governance_rule_action(rule: Mapping[str, Any], action: str, *, actor: str | None = None, superseded_by_rule_key: str = "", config: Any = None) -> dict[str, Any]:
    """Return an append-only governance action row for a rule.

    Parameters
    ----------
    rule : mapping
        Existing rule row.
    action : str
        One of ``approve``, ``reject``, or ``supersede``.
    actor : str, optional
        Reviewer identity.
    superseded_by_rule_key : str, optional
        Replacement rule key for supersede actions.
    config : Any, optional
        Runtime configuration used for timestamps.

    Returns
    -------
    dict[str, Any]
        Rule row with updated governance lifecycle fields.

    """
    row = dict(rule)
    now = _now_utc_iso(config)
    if action == "approve":
        row.update({"is_active": True, "review_status": "governance_approved", "approved_by": _resolve_action_by(actor), "approved_at": now, "requires_post_review": False})
    elif action == "reject":
        row.update({"is_active": False, "review_status": "rejected"})
    elif action == "supersede":
        row.update({"is_active": False, "review_status": "superseded", "superseded_by_rule_key": superseded_by_rule_key})
    else:
        raise ValueError("action must be one of approve, reject, or supersede")
    return row


def _base_guardrail_rule_record(state: Mapping[str, Any], *, guardrail_type: str, rule_type: str, column_name: str = "", parameters: Mapping[str, Any] | None = None, severity: str = "warning", description: str = "", policy: Mapping[str, Any] | None = None, bypass_reason: str = "", actor: str | None = None, source_notebook_type: str = "02_pipeline", config: Any = None) -> dict[str, Any]:
    """Build one ``METADATA_GUARDRAIL_RULES`` record for widget save actions."""
    env_name = str(state.get("environment_name") or "")
    dataset = str(state.get("dataset_name") or "")
    table = str(state.get("table_name") or "")
    rule_id = f"{table}.{column_name or '_table'}.{guardrail_type}.{rule_type}"
    lifecycle = guardrail_authoring_status(policy or state, bypass_reason=bypass_reason, actor=actor, config=config)
    return {"rule_key": _build_dq_rule_key(env_name, dataset, table, rule_id), "rule_id": rule_id, "metadata_column_key": _build_metadata_column_key(env_name, dataset, table, column_name) if column_name else "", "metadata_table_key": str(state.get("metadata_table_key") or _build_metadata_table_key(env_name, dataset, table)), "environment_name": env_name, "dataset_name": dataset, "table_name": table, "column_name": column_name, "guardrail_type": guardrail_type, "rule_type": rule_type, "rule_parameters_json": json.dumps(parameters or {}, sort_keys=True, default=str), "severity": severity, "description": description, "created_by": _resolve_action_by(actor), "created_at": _now_utc_iso(config), "action_type": "created", "source_notebook_type": source_notebook_type, "source_notebook_id": str(state.get("notebook_id") or ""), **lifecycle}


def _read_metadata_table_or_empty(config: Any, env: str, table_name: str, *, spark_session: Any) -> list[dict[str, Any]]:
    """Read a metadata table and return row dictionaries."""
    try:
        frame = read_lakehouse_table(
            config,
            env,
            "metadata",
            table_name,
            schema=_configured_lakehouse_schema(config, env, "metadata"),
            spark_session=spark_session,
        )
    except Exception as exc:
        if _is_table_not_found_error(exc):
            return []
        raise
    return _coerce_rows(frame)


def _filter_table_rows(rows: Iterable[Mapping[str, Any]], *, environment_name: str, dataset_name: str, table_name: str, metadata_table_key: str = "") -> list[dict[str, Any]]:
    """Return rows matching a selected table identity."""
    filtered = []
    for row in rows:
        item = dict(row)
        if metadata_table_key and str(item.get("metadata_table_key") or "") not in {"", metadata_table_key}:
            continue
        if environment_name and str(item.get("environment_name") or "") not in {"", environment_name}:
            continue
        if dataset_name and str(item.get("dataset_name") or "") not in {"", dataset_name}:
            continue
        if table_name and str(item.get("table_name") or "") != table_name:
            continue
        filtered.append(item)
    return filtered


def _latest_rule(existing_rules: Iterable[Mapping[str, Any]], guardrail_type: str, rule_type: str | None = None, column_name: str | None = None) -> dict[str, Any]:
    """Return the newest matching rule row for widget prepopulation."""
    matches = []
    for row in existing_rules or []:
        item = dict(row)
        if str(item.get("guardrail_type") or "") != guardrail_type:
            continue
        if rule_type is not None and str(item.get("rule_type") or "") != rule_type:
            continue
        if column_name is not None and str(item.get("column_name") or "") != column_name:
            continue
        matches.append(item)
    matches.sort(key=lambda row: str(row.get("created_at") or row.get("approved_at") or row.get("_committed_at") or ""), reverse=True)
    return matches[0] if matches else {}


def _rule_params(rule: Mapping[str, Any]) -> dict[str, Any]:
    """Return parsed rule parameters for widget prepopulation."""
    raw = rule.get("rule_parameters_json") or "{}"
    try:
        return json.loads(raw) if isinstance(raw, str) else dict(raw or {})
    except Exception:
        return {}


def _write_rule_records(records: list[dict[str, Any]], *, config: Any, env: str, spark_session: Any) -> None:
    """Append rule records to ``METADATA_GUARDRAIL_RULES``."""
    if not records:
        return
    write_lakehouse_table(
        spark_session.createDataFrame(records),
        config,
        env,
        "metadata",
        GUARDRAIL_RULES_TABLE,
        schema=_configured_lakehouse_schema(config, env, "metadata"),
        mode="append",
    )


def _write_governance_policy_record(record: dict[str, Any], *, config: Any, env: str, spark_session: Any) -> None:
    """Append a policy row to ``METADATA_GOVERNANCE_REVIEWS``."""
    write_lakehouse_table(
        spark_session.createDataFrame([record]),
        config,
        env,
        "metadata",
        GOVERNANCE_REVIEWS_TABLE,
        schema=_configured_lakehouse_schema(config, env, "metadata"),
        mode="append",
    )


def widget_select_guardrail_target(config: Any, env: str, *, spark_session: Any) -> dict[str, Any]:
    """Render an interactive guardrail target selector and return handover state.

    Parameters
    ----------
    config : Any
        Runtime configuration containing metadata lakehouse routing.
    env : str
        Environment name used to read metadata tables.
    spark_session : Any
        Spark session for metadata reads.

    Returns
    -------
    dict[str, Any]
        Mutable handover state containing table identity, catalogue profile rows,
        existing rules, and effective table governance policy. The returned
        state updates when the user changes the selected target.

    """
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    catalogue = _read_metadata_table_or_empty(config, env, CATALOGUE_TABLE, spark_session=spark_session)
    rules = _read_metadata_table_or_empty(config, env, GUARDRAIL_RULES_TABLE, spark_session=spark_session)
    reviews = _read_metadata_table_or_empty(config, env, GOVERNANCE_REVIEWS_TABLE, spark_session=spark_session)
    if not catalogue:
        raise ValueError("METADATA_DATA_CATALOGUE has no guardrail targets.")

    targets = {}
    for row in catalogue:
        environment_name = str(row.get("environment_name") or env)
        dataset_name = str(row.get("dataset_name") or "")
        table_name = str(row.get("table_name") or "")
        if not table_name:
            continue
        metadata_table_key = str(row.get("metadata_table_key") or _build_metadata_table_key(environment_name, dataset_name, table_name))
        key = (environment_name, dataset_name, table_name, metadata_table_key)
        label = f"{environment_name} / {dataset_name or '(no dataset)'} / {table_name}"
        targets.setdefault(label, key)
    if not targets:
        raise ValueError("METADATA_DATA_CATALOGUE has no table-level guardrail targets.")

    target_dropdown = widgets.Dropdown(options=[(label, value) for label, value in sorted(targets.items())], description="Target", layout=widgets.Layout(width="760px"))
    governance_badge = widgets.HTML()
    profile_preview = widgets.HTML()
    rules_preview = widgets.HTML()
    state: dict[str, Any] = {}

    def refresh(*_: Any) -> None:
        environment_name, dataset_name, table_name, metadata_table_key = target_dropdown.value
        table_rows = _filter_table_rows(catalogue, environment_name=environment_name, dataset_name=dataset_name, table_name=table_name, metadata_table_key=metadata_table_key)
        table_rules = _filter_table_rows(rules, environment_name=environment_name, dataset_name=dataset_name, table_name=table_name, metadata_table_key=metadata_table_key)
        policy = resolve_table_governance_policy(reviews, environment_name=environment_name, dataset_name=dataset_name, table_name=table_name, metadata_table_key=metadata_table_key)
        latest = sorted(table_rows, key=lambda row: str(row.get("profiled_at") or row.get("run_timestamp") or row.get("profile_run_id") or ""), reverse=True)[0]
        columns = sorted({str(row.get("column_name") or "") for row in table_rows if row.get("column_name")})
        state.clear()
        state.update(
            {
                "environment_name": environment_name,
                "dataset_name": dataset_name,
                "table_name": table_name,
                "metadata_table_key": metadata_table_key,
                "profile_run_id": str(latest.get("profile_run_id") or ""),
                "profile_stage": str(latest.get("profile_stage") or ""),
                "columns": columns,
                "catalogue_profile_rows": table_rows,
                "existing_rules": table_rules,
                **policy,
            }
        )
        governance_badge.value = f"<b>Governance:</b> {state['governance_mode']} · <b>Approval policy:</b> {state['approval_policy']} · <b>Bypass allowed:</b> {state['approval_bypass_allowed']}"
        profile_preview.value = f"<b>Profile rows:</b> {len(table_rows)} · <b>Columns:</b> {', '.join(columns) if columns else '(none)'}"
        rules_preview.value = f"<b>Existing guardrail rules:</b> {len(table_rules)}"

    target_dropdown.observe(refresh, names="value")
    refresh()
    state["_controls"] = {"target": target_dropdown, "governance_badge": governance_badge, "profile_preview": profile_preview, "rules_preview": rules_preview}
    ip.display(widgets.VBox([widgets.HTML("<h3>Select guardrail target</h3>"), target_dropdown, governance_badge, profile_preview, rules_preview]))
    return state

def _schema_freshness_profile_records_from_selection(
    state: Mapping[str, Any],
    *,
    selected_columns: Iterable[str],
    schema_mode: str,
    freshness_mode: str,
    freshness_column: str,
    max_lag_days: int | str,
    profile_mode: str,
    watermark_column: str,
    bypass_reason: str = "",
    config: Any = None,
) -> list[dict[str, Any]]:
    """Build schema, freshness, and profile behavior rule rows from selections."""
    if str(profile_mode) == "changing_data" and not str(watermark_column or "").strip():
        raise ValueError("watermark_column is required when profile_mode is changing_data")
    if str(freshness_mode) == "enforce":
        try:
            lag_days = int(max_lag_days)
        except (TypeError, ValueError) as exc:
            raise ValueError("max_lag_days must be a non-negative integer") from exc
        if lag_days < 0:
            raise ValueError("max_lag_days must be a non-negative integer")
    else:
        lag_days = 0
    columns = [str(column) for column in selected_columns]
    data_types = {str(row.get("column_name") or ""): str(row.get("data_type") or "") for row in state.get("catalogue_profile_rows", [])}
    return [
        _base_guardrail_rule_record(
            state,
            guardrail_type="schema",
            rule_type=str(schema_mode),
            parameters={"columns": columns, "data_types": {column: data_types.get(column, "") for column in columns}},
            description="Selected-table schema guardrail",
            bypass_reason=bypass_reason,
            config=config,
        ),
        _base_guardrail_rule_record(
            state,
            guardrail_type="freshness",
            rule_type="max_lag_days" if str(freshness_mode) == "enforce" else "skip",
            parameters={"freshness_column": freshness_column if str(freshness_mode) == "enforce" else "", "max_lag_days": lag_days},
            description="Freshness guardrail",
            bypass_reason=bypass_reason,
            config=config,
        ),
        _base_guardrail_rule_record(
            state,
            guardrail_type="profile_behavior",
            rule_type=str(profile_mode),
            parameters={"watermark_column": watermark_column if str(profile_mode) == "changing_data" else ""},
            description="Profile behavior guardrail",
            bypass_reason=bypass_reason,
            config=config,
        ),
    ]


def widget_author_schema_freshness_profile_rules(
    state: Mapping[str, Any],
    *,
    config: Any = None,
    env: str | None = None,
    spark_session: Any = None,
    bypass_reason: str = "",
    commit: bool = False,
) -> dict[str, Any]:
    """Render interactive schema, freshness, and profile behavior authoring UI.

    Parameters
    ----------
    state : mapping
        Handover state from :func:`widget_select_guardrail_target`.
    config, env, spark_session : Any, optional
        Runtime objects used for save actions.
    bypass_reason : str, optional
        Initial approval-bypass reason.
    commit : bool, default=False
        Whether to save the initial generated records immediately.

    Returns
    -------
    dict[str, Any]
        Widget state containing controls, generated records, and callable
        ``build_records``/``save`` helpers for tests and notebook automation.

    """
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    columns = list(state.get("columns") or [])
    existing_rules = list(state.get("existing_rules") or [])
    schema_rule = _latest_rule(existing_rules, "schema")
    schema_params = _rule_params(schema_rule)
    selected_schema_columns = tuple(column for column in (schema_params.get("columns") or columns) if column in columns)
    freshness_rule = _latest_rule(existing_rules, "freshness")
    freshness_params = _rule_params(freshness_rule)
    profile_rule = _latest_rule(existing_rules, "profile_behavior")
    profile_params = _rule_params(profile_rule)

    schema_columns = widgets.SelectMultiple(options=columns, value=selected_schema_columns or tuple(columns), description="Columns", rows=min(max(len(columns), 4), 12), layout=widgets.Layout(width="420px"))
    schema_mode = widgets.Dropdown(options=["strict", "relaxed", "skip"], value=str(schema_rule.get("rule_type") or "relaxed"), description="Schema mode")
    freshness_mode = widgets.Dropdown(options=["enforce", "skip"], value="skip" if str(freshness_rule.get("rule_type") or "skip") == "skip" else "enforce", description="Freshness")
    freshness_column = widgets.Dropdown(options=[""] + columns, value=str(freshness_params.get("freshness_column") or freshness_rule.get("column_name") or ""), description="Column")
    max_lag = widgets.BoundedIntText(value=int(freshness_params.get("max_lag_days") or 0), min=0, description="Max lag days")
    profile_mode = widgets.Dropdown(options=["static_data", "changing_data", "skip"], value=str(profile_rule.get("rule_type") or "static_data"), description="Profile mode")
    watermark_column = widgets.Dropdown(options=[""] + columns, value=str(profile_params.get("watermark_column") or profile_rule.get("column_name") or ""), description="Watermark")
    bypass_box = widgets.Textarea(value=bypass_reason, description="Bypass reason", layout=widgets.Layout(width="760px", height="70px"))
    preview = widgets.Textarea(description="Preview", disabled=True, layout=widgets.Layout(width="900px", height="220px"))
    message = widgets.HTML()
    records_state: dict[str, Any] = {"records": []}

    governed = str(state.get("governance_mode") or "ungoverned") == "governed"
    primary_label = "Submit for governance approval" if governed else "Save active rules"
    save_button = widgets.Button(description=primary_label, button_style="success")
    bypass_button = widgets.Button(description="Skip approval and activate now", button_style="warning")
    bypass_button.layout.display = "" if governed and bool(state.get("approval_bypass_allowed")) else "none"
    cancel_button = widgets.Button(description="Cancel")

    def build_records(*, use_bypass: bool = False) -> list[dict[str, Any]]:
        reason = bypass_box.value.strip() if use_bypass else ""
        if use_bypass and not reason:
            raise ValueError("Bypass reason is required to skip approval.")
        return _schema_freshness_profile_records_from_selection(
            state,
            selected_columns=list(schema_columns.value),
            schema_mode=schema_mode.value,
            freshness_mode=freshness_mode.value,
            freshness_column=freshness_column.value,
            max_lag_days=max_lag.value,
            profile_mode=profile_mode.value,
            watermark_column=watermark_column.value,
            bypass_reason=reason,
            config=config,
        )

    def refresh_preview(*_: Any) -> None:
        try:
            records_state["records"] = build_records(use_bypass=False)
            preview.value = json.dumps(records_state["records"], indent=2, default=str)
            message.value = ""
        except Exception as exc:
            preview.value = ""
            message.value = f"<b style='color:#b00020'>Validation error:</b> {exc}"

    def save(*, use_bypass: bool = False) -> list[dict[str, Any]]:
        records = build_records(use_bypass=use_bypass)
        records_state["records"] = records
        if spark_session is None or config is None or env is None:
            message.value = "<b>Preview only:</b> config, env, and spark_session are required to save."
            return records
        _write_rule_records(records, config=config, env=env, spark_session=spark_session)
        message.value = f"<b style='color:green'>Saved {len(records)} guardrail rule row(s) to METADATA_GUARDRAIL_RULES.</b>"
        return records

    def cancel(_: Any = None) -> None:
        records_state["records"] = []
        preview.value = ""
        message.value = "<b>Cancelled.</b>"

    for control in (schema_columns, schema_mode, freshness_mode, freshness_column, max_lag, profile_mode, watermark_column, bypass_box):
        control.observe(lambda change: refresh_preview(), names="value")
    save_button.on_click(lambda _: save(use_bypass=False))
    bypass_button.on_click(lambda _: save(use_bypass=True))
    cancel_button.on_click(cancel)
    refresh_preview()
    if commit:
        save(use_bypass=bool(bypass_reason))

    ui = widgets.VBox([
        widgets.HTML("<h3>Author schema, freshness, and profile behavior rules</h3>"),
        widgets.HTML(f"<b>Table:</b> {state.get('dataset_name', '')}.{state.get('table_name', '')} · <b>Governance:</b> {state.get('governance_mode', 'ungoverned')}"),
        widgets.HTML("<h4>Schema guardrail</h4>"),
        widgets.HBox([schema_mode, schema_columns]),
        widgets.HTML("<h4>Freshness guardrail</h4>"),
        widgets.HBox([freshness_mode, freshness_column, max_lag]),
        widgets.HTML("<h4>Profile behavior guardrail</h4>"),
        widgets.HBox([profile_mode, watermark_column]),
        bypass_box,
        preview,
        widgets.HBox([save_button, bypass_button, cancel_button]),
        message,
    ])
    ip.display(ui)
    return {"records": records_state["records"], "controls": {"schema_columns": schema_columns, "schema_mode": schema_mode, "freshness_mode": freshness_mode, "freshness_column": freshness_column, "max_lag": max_lag, "profile_mode": profile_mode, "watermark_column": watermark_column, "bypass_reason": bypass_box}, "build_records": build_records, "save": save, "ui": ui}

def _dq_records_from_selection(
    state: Mapping[str, Any],
    *,
    rule_type: str,
    selected_columns: Iterable[str],
    parameters: Mapping[str, Any] | None = None,
    severity: str = "warning",
    bypass_reason: str = "",
    action_type: str = "created",
    config: Any = None,
) -> list[dict[str, Any]]:
    """Build DQ rule records from selected columns."""
    records = []
    for column in selected_columns:
        record = _base_guardrail_rule_record(
            state,
            guardrail_type="dq",
            rule_type=rule_type,
            column_name=str(column),
            parameters={"columns": [str(column)], **dict(parameters or {})},
            severity=severity,
            description=f"{rule_type} DQ guardrail",
            bypass_reason=bypass_reason,
            config=config,
        )
        record["action_type"] = action_type
        if action_type in {"deactivated", "superseded"}:
            record["is_active"] = False
            record["review_status"] = "superseded" if action_type == "superseded" else "rejected"
        records.append(record)
    return records


def widget_author_dq_rules(
    state: Mapping[str, Any],
    *,
    dq_authoring_mode: str = "manual",
    rule_type: str = "not_null",
    selected_columns: Iterable[str] | None = None,
    parameters: Mapping[str, Any] | None = None,
    severity: str = "warning",
    config: Any = None,
    env: str | None = None,
    spark_session: Any = None,
    bypass_reason: str = "",
    commit: bool = False,
) -> dict[str, Any]:
    """Render interactive manual or AI-assisted DQ rule authoring UI.

    Parameters
    ----------
    state : mapping
        Handover state from :func:`widget_select_guardrail_target`.
    dq_authoring_mode : {"manual", "ai_suggest"}, default="manual"
        Authoring mode selected before the notebook cell runs.
    rule_type : str, default="not_null"
        Initial DQ rule type for manual mode.
    selected_columns : iterable of str, optional
        Initial batch-selected columns. Defaults to all selected table columns.
    parameters : mapping, optional
        Initial JSON rule parameters.
    severity : str, default="warning"
        Initial rule severity.
    config, env, spark_session : Any, optional
        Runtime objects used for AI suggestions and saves.
    bypass_reason : str, optional
        Initial approval-bypass reason.
    commit : bool, default=False
        Whether to save the initial generated records immediately.

    Returns
    -------
    dict[str, Any]
        Widget state containing controls, generated records, suggestions, and
        callable helpers for tests and notebook automation.

    """
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    columns = list(state.get("columns") or [])
    initial_columns = tuple(column for column in (selected_columns or columns) if column in columns)
    existing_rules = list(state.get("existing_rules") or [])
    existing_dq = [row for row in existing_rules if str(row.get("guardrail_type") or "") == "dq"]
    mode = str(dq_authoring_mode or "manual")

    batch_rule_type = widgets.Dropdown(options=DQ_RULE_TYPES, value=rule_type if rule_type in DQ_RULE_TYPES else "not_null", description="Rule type")
    batch_columns = widgets.SelectMultiple(options=columns, value=initial_columns or tuple(columns), description="Columns", rows=min(max(len(columns), 4), 12), layout=widgets.Layout(width="420px"))
    batch_params = widgets.Textarea(value=json.dumps(parameters or {}, indent=2), description="Parameters", layout=widgets.Layout(width="760px", height="90px"))
    batch_severity = widgets.ToggleButtons(options=["warning", "error"], value=severity if severity in {"warning", "error"} else "warning", description="Severity")

    search_column = widgets.Combobox(options=columns, value=columns[0] if columns else "", description="Column")
    individual_rule_type = widgets.Dropdown(options=DQ_RULE_TYPES, value=rule_type if rule_type in DQ_RULE_TYPES else "not_null", description="Rule")
    individual_params = widgets.Textarea(value="{}", description="Parameters", layout=widgets.Layout(width="760px", height="90px"))
    bypass_box = widgets.Textarea(value=bypass_reason, description="Bypass reason", layout=widgets.Layout(width="760px", height="70px"))
    preview = widgets.Textarea(description="Preview", disabled=True, layout=widgets.Layout(width="900px", height="220px"))
    history = widgets.HTML("<pre>" + json.dumps(existing_dq, indent=2, default=str) + "</pre>")
    suggestions_html = widgets.HTML()
    message = widgets.HTML()
    records_state: dict[str, Any] = {"records": [], "suggestions": []}

    governed = str(state.get("governance_mode") or "ungoverned") == "governed"
    primary_label = "Submit for governance approval" if governed else "Save active rules"
    save_batch_button = widgets.Button(description=primary_label, button_style="success")
    save_one_button = widgets.Button(description="Save/update selected rule", button_style="info")
    clear_one_button = widgets.Button(description="Clear / supersede selected rule", button_style="warning")
    bypass_button = widgets.Button(description="Skip approval and activate now", button_style="warning")
    bypass_button.layout.display = "" if governed and bool(state.get("approval_bypass_allowed")) else "none"
    ai_button = widgets.Button(description="Generate AI suggestions")
    ai_button.layout.display = "" if mode == "ai_suggest" else "none"
    approve_ai_button = widgets.Button(description="Approve AI suggestions", button_style="success")
    reject_ai_button = widgets.Button(description="Reject AI suggestions")

    def _batch_parameters() -> dict[str, Any]:
        try:
            return json.loads(batch_params.value or "{}")
        except json.JSONDecodeError as exc:
            raise ValueError("Parameters must be valid JSON") from exc

    def _individual_parameters() -> dict[str, Any]:
        try:
            return json.loads(individual_params.value or "{}")
        except json.JSONDecodeError as exc:
            raise ValueError("Individual parameters must be valid JSON") from exc

    def load_existing_individual(*_: Any) -> None:
        rule = _latest_rule(existing_dq, "dq", individual_rule_type.value, search_column.value)
        params = _rule_params(rule)
        params.pop("columns", None)
        individual_params.value = json.dumps(params, indent=2, default=str)

    def build_batch_records(*, use_bypass: bool = False) -> list[dict[str, Any]]:
        reason = bypass_box.value.strip() if use_bypass else ""
        if use_bypass and not reason:
            raise ValueError("Bypass reason is required to skip approval.")
        return _dq_records_from_selection(state, rule_type=batch_rule_type.value, selected_columns=list(batch_columns.value), parameters=_batch_parameters(), severity=batch_severity.value, bypass_reason=reason, config=config)

    def build_individual_record(*, action_type: str = "created", use_bypass: bool = False) -> list[dict[str, Any]]:
        reason = bypass_box.value.strip() if use_bypass else ""
        if use_bypass and not reason:
            raise ValueError("Bypass reason is required to skip approval.")
        return _dq_records_from_selection(state, rule_type=individual_rule_type.value, selected_columns=[search_column.value], parameters=_individual_parameters(), severity=batch_severity.value, bypass_reason=reason, action_type=action_type, config=config)

    def refresh_preview(*_: Any) -> None:
        try:
            records_state["records"] = build_batch_records(use_bypass=False)
            preview.value = json.dumps(records_state["records"], indent=2, default=str)
            message.value = ""
        except Exception as exc:
            preview.value = ""
            message.value = f"<b style='color:#b00020'>Validation error:</b> {exc}"

    def save_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        records_state["records"] = records
        if spark_session is None or config is None or env is None:
            message.value = "<b>Preview only:</b> config, env, and spark_session are required to save."
            return records
        _write_rule_records(records, config=config, env=env, spark_session=spark_session)
        message.value = f"<b style='color:green'>Saved {len(records)} DQ rule row(s) to METADATA_GUARDRAIL_RULES.</b>"
        return records

    def save_batch(*, use_bypass: bool = False) -> list[dict[str, Any]]:
        return save_records(build_batch_records(use_bypass=use_bypass))

    def save_individual(*, action_type: str = "created", use_bypass: bool = False) -> list[dict[str, Any]]:
        return save_records(build_individual_record(action_type=action_type, use_bypass=use_bypass))

    def suggest_ai(_: Any = None) -> list[dict[str, Any]]:
        profile_rows = list(state.get("catalogue_profile_rows") or [])
        profile_df = spark_session.createDataFrame(profile_rows) if spark_session is not None else profile_rows
        suggestions = _draft_dq_rules(profile_df=profile_df, table_name=str(state.get("table_name") or ""), config=config)
        for suggestion in suggestions:
            suggestion.update({"review_status": "draft", "is_active": False})
        records_state["suggestions"].clear()
        records_state["suggestions"].extend(suggestions)
        suggestions_html.value = "<pre>" + json.dumps(suggestions, indent=2, default=str) + "</pre>"
        message.value = f"<b>Loaded {len(suggestions)} AI draft suggestion(s). Edit and save approved suggestions.</b>"
        return records_state["suggestions"]

    def approve_ai(*, use_bypass: bool = False) -> list[dict[str, Any]]:
        reason = bypass_box.value.strip() if use_bypass else ""
        if use_bypass and not reason:
            raise ValueError("Bypass reason is required to skip approval.")
        records = []
        for suggestion in records_state["suggestions"]:
            suggestion_columns = suggestion.get("columns") or [suggestion.get("column_name") or ""]
            params = {key: value for key, value in suggestion.items() if key not in {"rule_id", "rule_type", "columns", "column_name", "review_status", "is_active"}}
            records.extend(_dq_records_from_selection(state, rule_type=str(suggestion.get("rule_type") or "not_null"), selected_columns=suggestion_columns, parameters=params, severity=batch_severity.value, bypass_reason=reason, config=config))
        return save_records(records)

    def reject_ai(_: Any = None) -> None:
        records_state["suggestions"].clear()
        suggestions_html.value = "<i>AI suggestions rejected; no active rules were saved.</i>"
        message.value = "<b>Rejected AI suggestions.</b>"

    for control in (batch_rule_type, batch_columns, batch_params, batch_severity, bypass_box):
        control.observe(lambda change: refresh_preview(), names="value")
    for control in (search_column, individual_rule_type):
        control.observe(lambda change: load_existing_individual(), names="value")
    save_batch_button.on_click(lambda _: save_batch(use_bypass=False))
    save_one_button.on_click(lambda _: save_individual(action_type="created", use_bypass=False))
    clear_one_button.on_click(lambda _: save_individual(action_type="superseded", use_bypass=False))
    bypass_button.on_click(lambda _: save_batch(use_bypass=True))
    ai_button.on_click(suggest_ai)
    approve_ai_button.on_click(lambda _: approve_ai(use_bypass=False))
    reject_ai_button.on_click(reject_ai)
    load_existing_individual()
    refresh_preview()
    if commit:
        save_batch(use_bypass=bool(bypass_reason))

    ui = widgets.VBox([
        widgets.HTML("<h3>Author DQ rules</h3>"),
        widgets.HTML(f"<b>Mode:</b> {mode} · <b>Table:</b> {state.get('dataset_name', '')}.{state.get('table_name', '')} · <b>Governance:</b> {state.get('governance_mode', 'ungoverned')}"),
        widgets.HTML("<h4>Batch by rule type</h4>"),
        widgets.HBox([batch_rule_type, batch_columns, batch_severity]),
        batch_params,
        widgets.HTML("<h4>Individual rule editing</h4>"),
        widgets.HBox([search_column, individual_rule_type]),
        individual_params,
        widgets.HTML("<h4>Existing rule history</h4>"),
        history,
        ai_button,
        suggestions_html,
        widgets.HBox([approve_ai_button, reject_ai_button]),
        bypass_box,
        preview,
        widgets.HBox([save_batch_button, save_one_button, clear_one_button, bypass_button]),
        message,
    ])
    ip.display(ui)
    return {"records": records_state["records"], "suggestions": records_state["suggestions"], "controls": {"batch_rule_type": batch_rule_type, "batch_columns": batch_columns, "batch_params": batch_params, "search_column": search_column, "individual_rule_type": individual_rule_type, "individual_params": individual_params, "bypass_reason": bypass_box}, "build_batch_records": build_batch_records, "build_individual_record": build_individual_record, "save_batch": save_batch, "save_individual": save_individual, "suggest_ai": suggest_ai, "approve_ai": approve_ai, "reject_ai": reject_ai, "ui": ui}

def build_table_governance_policy_record(state: Mapping[str, Any], *, governance_mode: str, approval_policy: str | None = None, actor: str | None = None, reason: str = "", config: Any = None) -> dict[str, Any]:
    """Build a table-level governance policy row.

    Parameters
    ----------
    state : mapping
        Table identity state containing environment, dataset, table, and table key.
    governance_mode : {"governed", "ungoverned"}
        Desired table governance mode.
    approval_policy : str, optional
        Approval policy. Defaults to approval-required with bypass for governed
        tables and no approval required for ungoverned tables.
    actor : str, optional
        Reviewer identity.
    reason : str, optional
        Human-readable policy reason.
    config : Any, optional
        Runtime configuration used for timestamps.

    Returns
    -------
    dict[str, Any]
        ``METADATA_GOVERNANCE_REVIEWS`` policy row.

    """
    mode = str(governance_mode or "ungoverned").lower()
    if mode not in {"governed", "ungoverned"}:
        raise ValueError("governance_mode must be governed or ungoverned")
    policy = str(approval_policy or ("approval_required_with_bypass" if mode == "governed" else "no_approval_required"))
    now = _now_utc_iso(config)
    return {
        "review_id": str(uuid.uuid4()),
        "environment_name": str(state.get("environment_name") or ""),
        "dataset_name": str(state.get("dataset_name") or ""),
        "table_name": str(state.get("table_name") or ""),
        "metadata_table_key": str(state.get("metadata_table_key") or ""),
        "profile_run_id": str(state.get("profile_run_id") or ""),
        "profile_stage": str(state.get("profile_stage") or ""),
        "outcome": "policy_updated",
        "blocker_count": 0,
        "warning_count": 0,
        "blockers_json": "[]",
        "warnings_json": "[]",
        "evidence_summary_json": json.dumps({"policy_reason": reason}, sort_keys=True),
        "reviewed_at": now,
        "reviewed_by": _resolve_action_by(actor),
        "governance_mode": mode,
        "approval_policy": policy,
        "governance_status": "active",
        "approval_bypass_allowed": policy == "approval_required_with_bypass",
        "requires_post_review": False,
        "policy_reason": reason,
        "effective_from": now,
        "effective_to": "",
    }


def mark_table_governed(state: Mapping[str, Any], *, actor: str | None = None, reason: str = "", approval_policy: str = "approval_required_with_bypass", config: Any = None) -> dict[str, Any]:
    """Return an active governed table policy row."""
    return build_table_governance_policy_record(state, governance_mode="governed", approval_policy=approval_policy, actor=actor, reason=reason, config=config)


def mark_table_ungoverned(state: Mapping[str, Any], *, actor: str | None = None, reason: str = "", config: Any = None) -> dict[str, Any]:
    """Return an active ungoverned table policy row."""
    return build_table_governance_policy_record(state, governance_mode="ungoverned", approval_policy="no_approval_required", actor=actor, reason=reason, config=config)


def widget_review_guardrail_governance(state: Mapping[str, Any], *, config: Any = None, env: str | None = None, spark_session: Any = None) -> dict[str, Any]:
    """Render interactive 03 governance policy and rule-review controls.

    Parameters
    ----------
    state : mapping
        Handover state from :func:`widget_select_guardrail_target`.
    config, env, spark_session : Any, optional
        Runtime objects used for save actions.

    Returns
    -------
    dict[str, Any]
        Widget state with controls and callable action helpers.

    """
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    rules = list(state.get("existing_rules") or [])
    proposed_or_bypassed = [row for row in rules if str(row.get("review_status") or "") in {"proposed", "bypass_active_pending_review"}]
    rule_options = [(f"{row.get('review_status')} · {row.get('guardrail_type')} · {row.get('rule_type')} · {row.get('column_name') or '_table'}", idx) for idx, row in enumerate(proposed_or_bypassed)]
    selected_rule = widgets.Dropdown(options=rule_options or [("No proposed or bypassed rules", -1)], description="Rule", layout=widgets.Layout(width="760px"))
    replacement_key = widgets.Text(description="New rule key", layout=widgets.Layout(width="520px"))
    policy_reason = widgets.Textarea(description="Policy reason", layout=widgets.Layout(width="760px", height="70px"))
    history = widgets.HTML("<pre>" + json.dumps(rules, indent=2, default=str) + "</pre>")
    status = widgets.HTML(f"<b>Current governance:</b> {state.get('governance_mode', 'ungoverned')} · <b>Approval policy:</b> {state.get('approval_policy', 'no_approval_required')}")
    message = widgets.HTML()
    records_state: dict[str, Any] = {"last_record": None}

    governed_button = widgets.Button(description="Mark table governed", button_style="warning")
    ungoverned_button = widgets.Button(description="Mark table ungoverned", button_style="info")
    approve_button = widgets.Button(description="Approve rule", button_style="success")
    reject_button = widgets.Button(description="Reject rule", button_style="danger")
    supersede_button = widgets.Button(description="Supersede rule", button_style="warning")

    def _save_policy(record: dict[str, Any]) -> dict[str, Any]:
        records_state["last_record"] = record
        if spark_session is None or config is None or env is None:
            message.value = "<b>Preview only:</b> config, env, and spark_session are required to save policy."
            return record
        _write_governance_policy_record(record, config=config, env=env, spark_session=spark_session)
        message.value = "<b style='color:green'>Saved table policy row to METADATA_GOVERNANCE_REVIEWS.</b>"
        return record

    def mark_governed(_: Any = None) -> dict[str, Any]:
        record = mark_table_governed(state, reason=policy_reason.value, config=config)
        return _save_policy(record)

    def mark_ungoverned(_: Any = None) -> dict[str, Any]:
        record = mark_table_ungoverned(state, reason=policy_reason.value, config=config)
        return _save_policy(record)

    def _selected_rule_row() -> dict[str, Any]:
        if selected_rule.value == -1:
            raise ValueError("No proposed or bypassed rule is selected.")
        return proposed_or_bypassed[int(selected_rule.value)]

    def save_rule_action(action: str) -> dict[str, Any]:
        row = apply_governance_rule_action(_selected_rule_row(), action, superseded_by_rule_key=replacement_key.value, config=config)
        records_state["last_record"] = row
        if spark_session is None or config is None or env is None:
            message.value = "<b>Preview only:</b> config, env, and spark_session are required to save rule action."
            return row
        _write_rule_records([row], config=config, env=env, spark_session=spark_session)
        message.value = f"<b style='color:green'>Saved {action} rule event to METADATA_GUARDRAIL_RULES.</b>"
        return row

    governed_button.on_click(mark_governed)
    ungoverned_button.on_click(mark_ungoverned)
    approve_button.on_click(lambda _: save_rule_action("approve"))
    reject_button.on_click(lambda _: save_rule_action("reject"))
    supersede_button.on_click(lambda _: save_rule_action("supersede"))

    ui = widgets.VBox([
        widgets.HTML("<h3>Governance policy and guardrail review</h3>"),
        status,
        policy_reason,
        widgets.HBox([governed_button, ungoverned_button]),
        widgets.HTML("<h4>Proposed and bypass-active rules requiring review</h4>"),
        selected_rule,
        replacement_key,
        widgets.HBox([approve_button, reject_button, supersede_button]),
        widgets.HTML("<h4>Rule history by table</h4>"),
        history,
        message,
    ])
    ip.display(ui)
    return {"controls": {"selected_rule": selected_rule, "replacement_key": replacement_key, "policy_reason": policy_reason}, "mark_governed": mark_governed, "mark_ungoverned": mark_ungoverned, "save_rule_action": save_rule_action, "last_record": records_state, "ui": ui}
