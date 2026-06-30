"""Table-scoped governance review helpers for ``03_governance`` notebooks."""

from __future__ import annotations

import importlib
import json
import re
import uuid
from typing import Any, Iterable, Mapping

from .config.shared import get_audit_timezone, get_current_audit_timestamp, resolve_fabric_context
from .io.shared import configured_lakehouse_schema, read_lakehouse_table_core, write_lakehouse_table_core
from .data_profiling.shared import profile_dataframe_core
from .metadata import _audit_timestamp_value, _now_audit_timestamp, _resolve_action_by, _build_metadata_column_key, _build_metadata_table_key, build_runtime_audit_fields, _build_dq_rule_key, _write_guardrail_result_row, coerce_metadata_row_types
from .widgets.shared import DATA_AGREEMENT_TABLE, DATA_AGREEMENT_EVIDENCE_TABLE

CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
ENRICHMENT_RULES_TABLE = "METADATA_ENRICHMENT_RULES"
GUARDRAIL_RULES_TABLE = "METADATA_GUARDRAIL_RULES"
GUARDRAIL_RESULTS_TABLE = "METADATA_GUARDRAIL_RESULTS"
GUARDRAIL_TYPES = ["schema", "freshness", "profile_behavior", "dq"]
ACTIVATION_STATES = ["active", "pending", "inactive"]
REVIEW_STATES = ["draft", "pending_governance_review", "active_pending_governance_review", "governance_approved", "rejected_by_governance", "superseded", "inactive"]
SOURCE_NOTEBOOK_TYPES = ["02_pipeline", "03_governance"]
CREATED_BY_ROLES = ["engineering", "governance", "system"]
GUARDRAIL_REVIEW_STATUSES = ["draft", "pending_governance_review", "active_pending_governance_review", "self_approved", "governance_approved", "rejected_by_governance", "superseded", "inactive"]
LINEAGE_TABLE = "METADATA_DATA_LINEAGE_TABLE"
PIPELINE_RUNS_TABLE = "METADATA_PIPELINE_RUNS"
DATA_ACCESS_TABLE = "METADATA_DATA_ACCESS"
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


def _catalogue_lookup_value(row: Mapping[str, Any], *names: str) -> Any:
    """Return the first non-empty present catalogue lookup value."""
    fallback = ""
    for name in names:
        if name in row:
            value = row[name]
            if value not in (None, ""):
                return value
            fallback = value
        upper = name.upper()
        if upper in row:
            value = row[upper]
            if value not in (None, ""):
                return value
            fallback = value
    return fallback


def _latest_metadata_catalogue_lookup_workflow(
    *,
    table_name: str,
    agreement: Mapping[str, Any] | None = None,
    metadata_schema: str | None = None,
    spark_session: Any = None,
    context: dict[str, Any] | None = None,
) -> Any:
    """Return the latest metadata catalogue rows for an exploratory table lookup.

    Parameters
    ----------
    table_name : str
        Source table name to look up in ``METADATA_DATA_CATALOGUE``.
    agreement : mapping, optional
        Selected agreement context from :func:`get_selected_agreement`. When an
        agreement id or contract version is present, matching catalogue rows are
        preferred.
    metadata_schema : str, optional
        Explicit metadata Lakehouse schema from ``00_env_config``. When omitted,
        the configured metadata schema is resolved from the active context.
    spark_session : Any, optional
        Spark session used to read metadata and return display-friendly rows.
    context : dict, optional
        Advanced FabricOps context override. Defaults to the active
        ``FABRIC_CONTEXT`` initialized by ``00_env_config``.

    Returns
    -------
    Any
        A Spark DataFrame when ``spark_session`` can create one; otherwise a
        list of dictionaries. Existing catalogue rows are limited to the latest
        profile group for the table. Missing metadata returns one friendly
        ``not_found`` row instead of raising.

    Notes
    -----
    This helper is read-only. It reads ``METADATA_DATA_CATALOGUE`` from the
    configured metadata target and does not write audit, approval, guardrail, or
    pipeline metadata.

    """
    config, env, resolved_context = resolve_fabric_context(context=context)
    requested_table = str(table_name or "").strip()
    if not requested_table:
        raise ValueError("table_name is required to look up metadata catalogue context.")
    agreement = dict(agreement or {})
    agreement_id = str(agreement.get("agreement_id") or "").strip()
    contract_version = str(agreement.get("agreement_contract_version") or agreement.get("contract_version") or "").strip()

    def _friendly_row(message: str) -> list[dict[str, Any]]:
        return [{"status": "not_found", "table_name": requested_table, "message": message}]

    try:
        catalogue_df = read_lakehouse_table_core(
            CATALOGUE_TABLE,
            target="metadata",
            schema=metadata_schema or configured_lakehouse_schema(config, env, "metadata"),
            context=resolved_context,
            spark_session=spark_session,
        )
        rows = _coerce_rows(catalogue_df)
    except Exception:
        rows = []

    matches = [
        row
        for row in rows
        if str(_catalogue_lookup_value(row, "table_name", "profiled_table_name") or "").strip() == requested_table
    ]
    if agreement_id:
        agreement_matches = [row for row in matches if str(_catalogue_lookup_value(row, "agreement_id") or "").strip() == agreement_id]
        if agreement_matches:
            matches = agreement_matches
    if contract_version:
        version_matches = [
            row
            for row in matches
            if str(_catalogue_lookup_value(row, "agreement_contract_version", "contract_version") or "").strip() == contract_version
        ]
        if version_matches:
            matches = version_matches

    if not matches:
        output_rows = _friendly_row(f"No metadata catalogue rows found for {requested_table}. Run 02_pipeline profiling to create governed catalogue evidence.")
    else:
        latest_key = max(
            str(_catalogue_lookup_value(row, "profiled_at", "run_timestamp", "created_at", "_committed_at", "profile_run_id") or "")
            for row in matches
        )
        output_rows = [
            row
            for row in matches
            if str(_catalogue_lookup_value(row, "profiled_at", "run_timestamp", "created_at", "_committed_at", "profile_run_id") or "") == latest_key
        ]

    if spark_session is not None and hasattr(spark_session, "createDataFrame"):
        return spark_session.createDataFrame(output_rows)
    return output_rows


def _canonical_dq_rule_type(rule_type: Any) -> str:
    return str(rule_type or "").strip()


def _normalize_dq_severity(severity: Any) -> str:
    """Normalize guardrail/DQ severity labels for DQ validation."""
    value = str(severity or "warning").strip().lower()
    return "error" if value in {"blocking", "error"} else "warning"


def _approved_review_context(profile_rows: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> tuple[dict[str, dict[str, Any]], str, str, dict[str, Any]]:
    actor = _resolve_action_by(approved_by)
    audit = build_runtime_audit_fields(config=config, env=env or "", committed_by=actor) if config is not None and env is not None else {}
    return {str(_value(r, "column_name")): r for r in profile_rows}, actor, _audit_timestamp_value(config), audit


def _approved_column_identity(profile_row: dict[str, Any], review_row: dict[str, Any], *, env: str | None = None) -> dict[str, str]:
    col = str(review_row.get("column_name") or _value(profile_row, "column_name") or ((review_row.get("columns") or [""])[0]))
    environment = str(_value(profile_row, "environment_name") or review_row.get("environment_name") or env or "")
    dataset = str(_value(profile_row, "dataset_name") or review_row.get("dataset_name") or "")
    table = str(_value(profile_row, "table_name") or review_row.get("table_name") or "")
    return {
        "metadata_column_key": str(_value(profile_row, "metadata_column_key") or review_row.get("metadata_column_key") or _build_metadata_column_key(environment, dataset, table, col)),
        "metadata_table_key": str(_value(profile_row, "metadata_table_key") or review_row.get("metadata_table_key") or _build_metadata_table_key(environment, dataset, table)),
        "environment_name": environment,
        "dataset_name": dataset,
        "table_name": table,
        "column_name": col,
    }


def _spark_types():
    """Return Spark SQL type classes lazily so package import stays lightweight."""
    try:
        from pyspark.sql.types import BooleanType, DoubleType, LongType, StringType, StructField, StructType, TimestampType
    except Exception:  # pragma: no cover - local docs/tests may run without PySpark
        class BooleanType:
            pass

        class DoubleType:
            pass

        class LongType:
            pass

        class StringType:
            pass

        class TimestampType:
            pass

        class StructField:
            def __init__(self, name, dataType, nullable=True):  # noqa: N803 - mirrors Spark API
                self.name = name
                self.dataType = dataType
                self.nullable = nullable

        class StructType:
            def __init__(self, fields=None):
                self.fields = list(fields or [])

            def fieldNames(self):  # noqa: N802 - mirrors Spark API
                return [field.name for field in self.fields]

    return BooleanType, DoubleType, LongType, StringType, StructField, StructType, TimestampType


def _check_metadata_schema_field_names(table_name: str, fields: list[tuple[str, Any]]) -> None:
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
    _check_metadata_schema_field_names(table_name, fields)
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
        ("governance_mode", string), ("approval_policy", string), ("bypass_allowed", boolean), ("policy_reason", string), ("policy_updated_by", string), ("policy_updated_at", string),
        ("agreement_id", string), ("contract_version", string), ("notebook_registry_id", string), ("notebook_id", string),
        *audit,
    ]
    return {
        CATALOGUE_TABLE: _schema(CATALOGUE_TABLE, catalogue),
        ENRICHMENT_RULES_TABLE: _schema(ENRICHMENT_RULES_TABLE, [("enrichment_rule_id", string), ("enrichment_rule_version", string), ("enrichment_rule_key", string), ("metadata_table_key", string), ("metadata_column_key", string), ("table_name", string), ("column_name", string), ("enrichment_scope", string), ("enrichment_type", string), ("enrichment_payload_json", string), ("business_name", string), ("business_description", string), ("business_meaning", string), ("column_description", string), ("classification", string), ("sensitivity_label", string), ("pii_flag", boolean), ("pii_type", string), ("data_domain", string), ("data_owner", string), ("data_steward", string), ("usage_notes", string), ("quality_notes", string), ("review_status", string), ("review_state", string), ("activation_state", string), ("is_active", boolean), ("created_by_role", string), ("source_notebook_type", string), ("source_notebook_id", string), ("activation_reason", string), ("activated_by", string), ("activated_at", string), ("requires_governance_review", boolean), ("approval_policy", string), ("governance_mode", string), ("submitted_by", string), ("submitted_at", string), ("reviewed_by", string), ("reviewed_at", string), ("review_decision", string), ("review_comment", string), ("bypass_reason", string), ("requires_post_review", boolean), ("supersedes_enrichment_rule_id", string), ("supersedes_record_id", string), ("superseded_by_record_id", string), ("effective_from", string), ("effective_to", string), ("created_at", string), ("created_by", string), ("updated_at", string), ("updated_by", string), ("run_id", string), ("notebook_id", string), ("notebook_registry_id", string), *audit]),
        GUARDRAIL_RULES_TABLE: _schema(GUARDRAIL_RULES_TABLE, [("rule_key", string), ("rule_id", string), ("metadata_column_key", string), ("metadata_table_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("guardrail_type", string), ("rule_type", string), ("rule_parameters_json", string), ("severity", string), ("description", string), ("activation_state", string), ("is_active", boolean), ("review_status", string), ("review_state", string), ("created_by_role", string), ("author_role", string), ("created_by", string), ("created_at", string), ("approved_by", string), ("approved_at", string), ("suggestion_json", string), ("action_type", string), ("source_notebook_type", string), ("source_notebook_id", string), ("source_workspace_id", string), ("activation_reason", string), ("activated_by", string), ("activated_at", string), ("superseded_by_rule_key", string), ("notes", string), ("approval_required", boolean), ("approval_bypassed", boolean), ("requires_governance_review", boolean), ("requires_post_review", boolean), ("bypass_reason", string), ("bypassed_by", string), ("bypassed_at", string), ("governance_mode", string), ("approval_policy", string), ("submitted_by", string), ("submitted_at", string), ("reviewed_by", string), ("reviewed_at", string), ("review_decision", string), ("review_comment", string), ("supersedes_rule_id", string), ("supersedes_record_id", string), ("superseded_by_record_id", string), ("effective_from", string), ("effective_to", string), *audit]),
        GUARDRAIL_RESULTS_TABLE: _schema(GUARDRAIL_RESULTS_TABLE, [("result_id", string), ("run_id", string), ("rule_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("guardrail_type", string), ("rule_type", string), ("status", string), ("can_continue", boolean), ("severity", string), ("reason", string), ("expected_value_json", string), ("actual_value_json", string), ("result_payload_json", string), ("created_at", string), *audit]),
        LINEAGE_TABLE: _schema(LINEAGE_TABLE, [("lineage_id", string), ("dataset_name", string), ("run_id", string), ("source_table", string), ("target_table", string), ("source_table_key", string), ("target_table_key", string), ("transformation_steps_json", string), ("created_at", string), *audit]),
        PIPELINE_RUNS_TABLE: _schema(PIPELINE_RUNS_TABLE, [("run_id", string), ("agreement_id", string), ("agreement_contract_version", string), ("notebook_registry_id", string), ("notebook_id", string), ("notebook_type", string), ("pipeline_name", string), ("environment_name", string), ("started_at", string), ("completed_at", string), ("status", string), ("source_count", long), ("target_count", long), ("source_guardrail_status", string), ("target_guardrail_status", string), ("dq_status", string), ("lineage_status", string), ("catalogue_status", string), ("message", string), ("run_summary_json", string), ("created_at", string)]),
        DATA_ACCESS_TABLE: _schema(DATA_ACCESS_TABLE, [("user_principal", string), ("role_name", string), ("permission", string), ("access_purpose", string), ("approval_status", string), ("access_scope", string), ("table_id", string), ("metadata_table_key", string), ("metadata_column_key", string), ("granted_date", string), ("expires_at", string), ("approved_by", string), ("approved_at", string), ("notes", string), *audit]),
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


def _catalogue_physical_identity(row: dict[str, Any]) -> dict[str, str]:
    """Return stable physical table identity without profile stage or pipeline identity."""
    env = str(_first_present(row, ["environment_name", "env"]))
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


def load_catalogue_profile_rows(config: Any, env: str, selection: dict[str, Any], *, spark_session: Any) -> list[dict[str, Any]]:
    """Load column rows for the selected latest successful profile run."""
    rows = _coerce_rows(read_lakehouse_table_core(CATALOGUE_TABLE, target="metadata", schema=configured_lakehouse_schema(config, env, "metadata"), context={"config": config, "env": env}, spark_session=spark_session))
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


def _dq_rule_parameter_payload(rule: dict[str, Any], columns: list[str]) -> dict[str, Any]:
    """Return rule parameters stored inside ``rule_parameters_json``."""
    metadata_fields = {
        "rule_key", "rule_id", "metadata_column_key", "metadata_table_key", "environment_name", "dataset_name",
        "table_name", "column_name", "rule_type", "rule_parameters", "rule_parameters_json", "severity",
        "description", "is_active", "review_status", "approved_by", "approved_at", "suggestion_json",
        "suggestion", "action_type", "commit", "_committed_at", "_committed_by", "_workspace_name",
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
            "suggestion_json": _json(rule.get("suggestion_json") or rule.get("suggestion")),
            "action_type": action_type,
            "source_notebook_type": str(rule.get("source_notebook_type") or "03_governance"),
            "source_notebook_id": str(rule.get("source_notebook_id") or ""),
            "source_workspace_id": str(rule.get("source_workspace_id") or ""),
            "superseded_by_rule_key": str(rule.get("superseded_by_rule_key") or ""),
            "notes": str(rule.get("notes") or ""),
            **audit,
        })
    return rows

def _json(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True)


def _enrichment_options(config: Any) -> tuple[list[str], list[str], list[dict[str, Any]], list[dict[str, Any]]]:
    """Return configured column metadata enrichment controls."""
    governance = getattr(config, "governance_config", None)
    sensitivity = list(getattr(governance, "sensitivity_labels", None) or SENSITIVITY_LABELS)
    pii = list(getattr(governance, "pii_classifications", None) or PERSONAL_DATA_CLASSIFICATIONS)
    context_widget = getattr(governance, "enrichment_context_widget", None) or {}
    classification_widget = getattr(governance, "enrichment_classification_widget", None) or {}
    context_fields = list(context_widget.get("custom_fields", []) or [])
    classification_fields = list(classification_widget.get("custom_fields", []) or [])
    return sensitivity, pii, context_fields, classification_fields


def _render_enrichment_extra_fields(widgets: Any, definitions: list[dict[str, Any]]) -> dict[str, Any]:
    """Render configured enrichment extra fields keyed by field key."""
    controls: dict[str, Any] = {}
    for definition in definitions:
        key = str(definition.get("key") or "").strip()
        if not key:
            raise ValueError("Custom enrichment fields require a key.")
        label = str(definition.get("label") or key.replace("_", " ").title())
        field_type = str(definition.get("type") or "text").lower()
        common = {"description": label, "layout": widgets.Layout(width="420px")}
        if field_type == "textarea":
            control = widgets.Textarea(value="", rows=int(definition.get("rows", 2)), **common)
        elif field_type in {"dropdown", "select"}:
            options = list(definition.get("options", []))
            control = widgets.Dropdown(options=options, value=options[0] if options else None, **common)
        else:
            control = widgets.Text(value="", **common)
        controls[key] = control
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

    def profile_sort_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
        return (
            str(_value(row, "profiled_at")),
            str(_value(row, "profile_run_id")),
            str(_value(row, "run_id") or _value(row, "pipeline_run_id")),
            str(_value(row, "profile_stage")),
        )

    for row in sorted(rows, key=profile_sort_key, reverse=True):
        deduped.setdefault(str(_value(row, "column_name")), row)
    return [deduped[name] for name in sorted(deduped)]


def _enrichment_payload_from_review(review: Mapping[str, Any]) -> dict[str, Any]:
    """Return the JSON enrichment payload carried by an enrichment rule."""
    return {
        "business_name": str(review.get("business_name") or ""),
        "business_description": str(review.get("business_description") or review.get("business_context") or ""),
        "business_meaning": str(review.get("business_meaning") or ""),
        "column_description": str(review.get("column_description") or ""),
        "classification": str(review.get("classification") or review.get("sensitivity_label") or ""),
        "sensitivity_label": str(review.get("sensitivity_label") or ""),
        "pii_flag": bool(review.get("pii_flag") or str(review.get("pii_classification") or review.get("personal_data_classification") or "").lower() not in {"", "none"}),
        "pii_type": str(review.get("pii_type") or review.get("pii_identifier_type") or review.get("pii_classification") or ""),
        "data_domain": str(review.get("data_domain") or ""),
        "data_owner": str(review.get("data_owner") or ""),
        "data_steward": str(review.get("data_steward") or ""),
        "usage_notes": str(review.get("usage_notes") or review.get("notes") or ""),
        "quality_notes": str(review.get("quality_notes") or review.get("reasoning") or ""),
        "custom_fields": review.get("custom_fields") or review.get("custom_fields_json") or {},
    }


def build_enrichment_rule_records(
    profile_rows: list[dict[str, Any]],
    reviewed_rows: list[dict[str, Any]],
    *,
    state: Mapping[str, Any] | None = None,
    config: Any = None,
    env: str | None = None,
    actor: str | None = None,
    bypass_reason: str = "",
    action: str = "submit",
    source_notebook_type: str = "02_pipeline",
    created_by_role: str = "engineering",
) -> list[dict[str, Any]]:
    """Build append-only ``METADATA_ENRICHMENT_RULES`` rows.

    Parameters
    ----------
    profile_rows : list of dict
        Selected ``METADATA_DATA_CATALOGUE`` column evidence.
    reviewed_rows : list of dict
        Enrichment payload rows to persist when ``commit`` is true.
    state : Mapping[str, Any], optional
        Selected table state carrying governance mode and approval policy.
    config : Any, optional
        Runtime configuration used for timestamps and audit fields.
    env : str, optional
        Environment name used in metadata keys and audit fields.
    actor : str, optional
        User responsible for authoring the enrichment records.
    bypass_reason : str, optional
        Required reason when bypassing approval for governed tables.
    action : {"draft", "submit", "apply_now"}, default="submit"
        Authoring action that determines activation and review lifecycle.
    source_notebook_type : {"02_pipeline", "03_governance"}, default="02_pipeline"
        Notebook type that authored the record.
    created_by_role : {"engineering", "governance", "system"}, default="engineering"
        Role that authored the record.

    Returns
    -------
    list of dict
        Rows ready to append to ``METADATA_ENRICHMENT_RULES``.

    """
    profile, resolved_actor, now, audit = _approved_review_context(profile_rows, config=config, env=env, approved_by=actor)
    lifecycle = guardrail_authoring_status(
        state or {},
        bypass_reason=bypass_reason,
        actor=resolved_actor,
        config=config,
        action=action,
        source_notebook_type=source_notebook_type,
        created_by_role=created_by_role,
    )
    rows = []
    for review in reviewed_rows or []:
        if not review.get("commit", True):
            continue
        identity = _approved_column_identity(profile.get(str(review.get("column_name")), {}), review, env=env)
        payload = _enrichment_payload_from_review(review)
        rule_id = str(review.get("enrichment_rule_id") or f"{identity['metadata_table_key']}.{identity['column_name'] or '_table'}.enrichment.{uuid.uuid4().hex[:12]}")
        row = {
            "enrichment_rule_id": rule_id,
            "enrichment_rule_version": str(review.get("enrichment_rule_version") or now),
            "enrichment_rule_key": str(review.get("enrichment_rule_key") or _build_dq_rule_key(identity["environment_name"], identity["dataset_name"], identity["table_name"], rule_id)),
            "metadata_table_key": identity["metadata_table_key"],
            "metadata_column_key": identity["metadata_column_key"],
            "table_name": identity["table_name"],
            "column_name": identity["column_name"],
            "enrichment_scope": "column" if identity["column_name"] else "table",
            "enrichment_type": str(review.get("enrichment_type") or "metadata_enrichment"),
            "enrichment_payload_json": _json(payload),
            "business_name": payload["business_name"],
            "business_description": payload["business_description"],
            "business_meaning": payload["business_meaning"],
            "column_description": payload["column_description"],
            "classification": payload["classification"],
            "sensitivity_label": payload["sensitivity_label"],
            "pii_flag": payload["pii_flag"],
            "pii_type": payload["pii_type"],
            "data_domain": payload["data_domain"],
            "data_owner": payload["data_owner"],
            "data_steward": payload["data_steward"],
            "usage_notes": payload["usage_notes"],
            "quality_notes": payload["quality_notes"],
            "review_status": lifecycle["review_status"],
            "review_state": lifecycle.get("review_state", lifecycle["review_status"]),
            "activation_state": lifecycle.get("activation_state", "active" if lifecycle["is_active"] else "inactive"),
            "is_active": lifecycle["is_active"],
            "created_by_role": lifecycle.get("created_by_role", "engineering"),
            "source_notebook_type": lifecycle.get("source_notebook_type", "02_pipeline"),
            "source_notebook_id": str(review.get("source_notebook_id") or (state or {}).get("notebook_id") or ""),
            "activation_reason": lifecycle.get("activation_reason", ""),
            "activated_by": lifecycle.get("activated_by", ""),
            "activated_at": lifecycle.get("activated_at", ""),
            "requires_governance_review": bool(lifecycle.get("requires_governance_review", False)),
            "approval_policy": lifecycle["approval_policy"],
            "governance_mode": lifecycle["governance_mode"],
            "submitted_by": resolved_actor,
            "submitted_at": now,
            "reviewed_by": resolved_actor if lifecycle["review_status"] in {"self_approved", "governance_approved"} else "",
            "reviewed_at": now if lifecycle["review_status"] in {"self_approved", "governance_approved"} else "",
            "review_decision": lifecycle["review_status"],
            "review_comment": str(review.get("review_comment") or ""),
            "bypass_reason": str(lifecycle.get("bypass_reason") or ""),
            "requires_post_review": bool(lifecycle["requires_post_review"]),
            "supersedes_enrichment_rule_id": str(review.get("supersedes_enrichment_rule_id") or ""),
            "effective_from": now if lifecycle["is_active"] else "",
            "effective_to": "",
            "created_at": now,
            "created_by": resolved_actor,
            "updated_at": now,
            "updated_by": resolved_actor,
            "run_id": str(review.get("run_id") or (state or {}).get("run_id") or ""),
            "notebook_id": str(review.get("notebook_id") or (state or {}).get("notebook_id") or ""),
            "notebook_registry_id": str(review.get("notebook_registry_id") or (state or {}).get("notebook_registry_id") or ""),
            **audit,
        }
        rows.append(row)
    return rows


def _write_table_metadata_enrichment_records(records: list[dict[str, Any]], *, config: Any, env: str, spark_session: Any) -> None:
    """Append descriptive enrichment intent only to ``METADATA_ENRICHMENT_RULES``."""
    if records:
        write_lakehouse_table_core(
            spark_session.createDataFrame([coerce_metadata_row_types(ENRICHMENT_RULES_TABLE, record) for record in records]),
            ENRICHMENT_RULES_TABLE,
            target="metadata",
            schema=configured_lakehouse_schema(config, env, "metadata"),
            context={"config": config, "env": env},
            mode="append",
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
    return _coerce_rows(read_lakehouse_table_core(table, target="metadata", schema=configured_lakehouse_schema(config, env, "metadata"), context={"config": config, "env": env}, spark_session=spark_session))


def _evaluate_governance_readiness(
    config: Any,
    env: str,
    selection: dict[str, Any],
    *,
    spark_session: Any,
    reviewed_by: str | None = None,
) -> dict[str, Any]:
    """Evaluate persisted evidence readiness without writing a metadata table.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Shared ``00_env_config`` configuration used for metadata lakehouse routing.
    env : str
        Environment key in ``config``.
    selection : dict[str, Any]
        Catalogue-table selection returned by ``get_selected_catalogue_table``.
    spark_session : pyspark.sql.SparkSession
        Spark session used to read metadata tables.
    reviewed_by : str, optional
        Reviewer identity. Runtime user metadata is used when omitted.

    Returns
    -------
    dict[str, Any]
        Readiness summary row plus blocker, warning, and evidence details.

    Notes
    -----
    The function intentionally re-reads agreement, catalogue, pipeline-run, and
    evidence metadata from the configured ``metadata`` target so review notebooks can run in a separate session after ``02_pipeline``.

    """
    profile_rows = load_catalogue_profile_rows(config, env, selection, spark_session=spark_session)
    first_profile = profile_rows[0]
    environment = str(_value(first_profile, "environment_name") or selection.get("environment_name") or env)
    dataset_name = str(_value(first_profile, "dataset_name") or selection.get("dataset_name") or "")
    table_name = str(_value(first_profile, "table_name") or selection.get("table_name") or "")
    table_key = str(_value(first_profile, "metadata_table_key") or selection.get("metadata_table_key") or _build_metadata_table_key(environment, dataset_name, table_name))
    profile_run_id = str(_value(first_profile, "profile_run_id") or selection.get("profile_run_id") or "")
    profile_stage = str(_value(first_profile, "profile_stage") or selection.get("profile_stage") or "")
    agreement_id = str(_value(first_profile, "agreement_id") or _value(first_profile, "AGREEMENT_ID") or "")
    agreement_contract_version = str(_value(first_profile, "contract_version") or _value(first_profile, "AGREEMENT_CONTRACT_VERSION") or "")

    all_pipeline_rows = [
        row for row in _read_metadata_rows(config, env, PIPELINE_RUNS_TABLE, spark_session=spark_session)
        if str(_value(row, "environment_name")) == environment
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
    reviewed_at = _audit_timestamp_value(config)
    actor = _resolve_action_by(reviewed_by)
    audit = build_runtime_audit_fields(config=config, env=env, committed_by=actor, committed_at=reviewed_at)
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
        "environment_name": env,
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
    return {"review": row, "outcome": outcome, "blockers": blockers, "warnings": warnings, "evidence_summary": evidence_summary}

def record_table_governance(
    config: Any,
    env: str,
    profile_rows: list[dict[str, Any]],
    *,
    spark_session: Any,
    enrichment_reviews: list[dict[str, Any]] | None = None,
    guardrail_rule_reviews: list[dict[str, Any]] | None = None,
    approved_by: str | None = None,
    readiness_selection: dict[str, Any] | None = None,
    evaluate_readiness: bool = False,
    mode: str = "append",
) -> dict[str, Any]:
    """Persist governed enrichment and guardrail rule intent.

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
    enrichment_reviews : list of dict, optional
        Human-reviewed enrichment payload rows. Committed rows are written only
        to ``METADATA_ENRICHMENT_RULES``.
    guardrail_rule_reviews : list of dict, optional
        Human-reviewed guardrail rule rows. DQ rows use
        ``review_status="governance_approved"`` and are written only to
        ``METADATA_GUARDRAIL_RULES``.
    approved_by : str, optional
        Reviewer identity to stamp on records. When omitted, runtime defaults
        are used.
    readiness_selection : dict, optional
        Catalogue selection used to evaluate non-persistent readiness evidence.
    evaluate_readiness : bool, default=False
        Whether to return a readiness summary after checking agreement,
        pipeline, schema/profile, and DQ evidence. No metadata table is written.
    mode : str, default "append"
        Write mode for metadata table commits.

    Returns
    -------
    dict[str, Any]
        Records written for ``enrichment_rules`` and ``guardrail_rules`` plus an
        optional non-persistent ``readiness_summary``.

    """
    enrichment_records = build_enrichment_rule_records(
        profile_rows,
        enrichment_reviews or [],
        state={"governance_mode": "governed", "approval_policy": "approval_required"},
        config=config,
        env=env,
        actor=approved_by,
    )
    actor = _resolve_action_by(approved_by)
    reviewed_at = _audit_timestamp_value(config)
    for record in enrichment_records:
        record.update({
            "activation_state": "active",
            "review_state": "governance_approved",
            "review_status": "governance_approved",
            "is_active": True,
            "requires_governance_review": False,
            "requires_post_review": False,
            "reviewed_by": actor,
            "reviewed_at": reviewed_at,
            "review_decision": "approved",
            "activated_by": record.get("activated_by") or actor,
            "activated_at": record.get("activated_at") or reviewed_at,
            "effective_from": record.get("effective_from") or reviewed_at,
            "source_notebook_type": "03_governance",
            "created_by_role": record.get("created_by_role") or "governance",
            "updated_by": actor,
            "updated_at": reviewed_at,
        })
    guardrail_records = _build_dq_rule_records(
        profile_rows,
        guardrail_rule_reviews or [],
        config=config,
        env=env,
        approved_by=approved_by,
    )
    writes = {
        ENRICHMENT_RULES_TABLE: enrichment_records,
        GUARDRAIL_RULES_TABLE: [dict(record, guardrail_type=record.get("guardrail_type") or "dq") for record in guardrail_records],
    }
    for table_name, records in writes.items():
        if records:
            write_lakehouse_table_core(spark_session.createDataFrame([coerce_metadata_row_types(table_name, record) for record in records]), table_name, target="metadata", schema=configured_lakehouse_schema(config, env, "metadata"), context={"config": config, "env": env}, mode=mode)

    readiness_summary = None
    if evaluate_readiness:
        if readiness_selection is None:
            raise ValueError("readiness_selection is required when evaluate_readiness=True.")
        readiness_summary = _evaluate_governance_readiness(
            config,
            env,
            readiness_selection,
            spark_session=spark_session,
            reviewed_by=approved_by,
        )

    return {
        "enrichment_rules": enrichment_records,
        "guardrail_rules": guardrail_records,
        "readiness_summary": readiness_summary,
    }
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

def _latest_dq_rule_versions(metadata_df, table_name: str, env: str | None = None, dataset_name: str | None = None):
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
    if env is not None and "environment_name" in columns:
        scoped = scoped.filter(F.col("environment_name") == env)
    if dataset_name is not None and "dataset_name" in columns:
        scoped = scoped.filter(F.col("dataset_name") == dataset_name)
    if not order_cols:
        return scoped
    w = Window.partitionBy(*[F.col(name) for name in partition_cols]).orderBy(*[F.col(name).desc_nulls_last() for name in order_cols])
    return scoped.withColumn("_rn", F.row_number().over(w)).filter(F.col("_rn") == 1).drop("_rn")


def _load_active_dq_rules(metadata_df, table_name: str, env: str | None = None, dataset_name: str | None = None) -> list[dict[str, Any]]:
    """Load active DQ guardrail rules from append-only metadata rows."""
    _, F, _ = _spark_sql_helpers()
    columns = set(getattr(metadata_df, "columns", []))
    latest = _latest_dq_rule_versions(metadata_df, table_name, env=env, dataset_name=dataset_name)
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
        "DQ_CHECKED_AT": get_current_audit_timestamp(config=config, drop_microseconds=False),
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
    schema = configured_lakehouse_schema(config, env, "metadata")
    frame = read_lakehouse_table_core(GUARDRAIL_RULES_TABLE, target="metadata", schema=schema, spark_session=spark_session, context={"config": config, "env": env})
    if "guardrail_type" in set(getattr(frame, "columns", [])):
        _, F, _ = _spark_sql_helpers()
        return frame.filter(F.lower(F.coalesce(F.col("guardrail_type"), F.lit(""))) == "dq")
    return frame

def _run_active_dq_guardrail(
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
    rules = _load_active_dq_rules(metadata_df, table_name=table_name, env=env, dataset_name=dataset_name)
    checks = _run_dq_guardrail_checks(dataframe, table_name=table_name, rules=rules) if rules else []
    total_count = int(dataframe.count())
    failed_row_count = _dq_failed_row_count(dataframe, rules) if rules else 0
    result = _summarize_dq_guardrail(checks)
    if any(str(rule.get("review_status") or "").lower() == "active_pending_governance_review" for rule in rules):
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
    """Prepare DQ profile rows from a profile DataFrame or raw DataFrame."""
    if (profile_df is None) == (df is None):
        raise ValueError("Provide exactly one of profile_df or df.")
    if profile_df is None:
        profile_df = profile_dataframe_core(df, table_name=table_name, config=config)
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


def resolve_table_governance_policy(governance_rows: Any, *, environment_name: str = "", dataset_name: str = "", table_name: str = "", metadata_table_key: str = "") -> dict[str, Any]:
    """Return the latest active table-level governance policy.

    Parameters
    ----------
    governance_rows : Any
        Catalogue rows or selected target state rows containing table governance policy fields.
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
    bypass_allowed = bool(latest.get("approval_bypass_allowed", latest.get("bypass_allowed", policy == "approval_required_with_bypass")))
    return {**default, **latest, "governance_mode": mode, "approval_policy": policy, "approval_bypass_allowed": bypass_allowed, "bypass_allowed": bypass_allowed}



def _is_no_approval_required(policy: Mapping[str, Any]) -> bool:
    """Return whether policy allows active records without formal review."""
    return str(policy.get("governance_mode") or "ungoverned").lower() == "ungoverned" or str(policy.get("approval_policy") or "").lower() == "no_approval_required"


def _assert_governance_review_context(source_notebook_type: str) -> None:
    """Block formal review outside the ``03_governance`` notebook context."""
    if source_notebook_type != "03_governance":
        raise PermissionError("Formal governance review actions are only allowed from 03_governance.")


def _lifecycle_fields(*, activation_state: str, review_state: str, actor: str, now: str, created_by_role: str = "engineering", source_notebook_type: str = "02_pipeline", activation_reason: str = "", requires_governance_review: bool = False, requires_post_review: bool = False) -> dict[str, Any]:
    """Build standardized lifecycle fields for enrichment and guardrail rows."""
    active = activation_state == "active"
    fields = {
        "activation_state": activation_state,
        "is_active": active,
        "review_state": review_state,
        "review_status": review_state,
        "created_by_role": created_by_role,
        "source_notebook_type": source_notebook_type,
        "activation_reason": activation_reason,
        "requires_governance_review": requires_governance_review,
        "requires_post_review": requires_post_review,
    }
    if active:
        fields.update({"activated_by": actor, "activated_at": now, "effective_from": now})
    return fields


def _authoring_lifecycle(policy: Mapping[str, Any], *, action: str = "save", actor: str | None = None, bypass_reason: str = "", source_notebook_type: str = "02_pipeline", created_by_role: str = "engineering", config: Any = None) -> dict[str, Any]:
    """Return lifecycle fields for authoring save, draft, submit, and apply-now actions."""
    now = _audit_timestamp_value(config)
    resolved = _resolve_action_by(actor)
    if action == "draft":
        return _lifecycle_fields(activation_state="inactive", review_state="draft", actor=resolved, now=now, created_by_role=created_by_role, source_notebook_type=source_notebook_type)
    if _is_no_approval_required(policy):
        return _lifecycle_fields(activation_state="active", review_state="self_approved", actor=resolved, now=now, created_by_role=created_by_role, source_notebook_type=source_notebook_type)
    if action in {"apply_now", "bypass"} or bypass_reason:
        fields = _lifecycle_fields(activation_state="active", review_state="active_pending_governance_review", actor=resolved, now=now, created_by_role=created_by_role, source_notebook_type=source_notebook_type, activation_reason="engineering_apply_now", requires_governance_review=True, requires_post_review=True)
        fields.update({"bypass_reason": bypass_reason, "approval_bypassed": True, "bypassed_by": resolved, "bypassed_at": now})
        return fields
    return _lifecycle_fields(activation_state="pending", review_state="pending_governance_review", actor=resolved, now=now, created_by_role=created_by_role, source_notebook_type=source_notebook_type, requires_governance_review=True)

def guardrail_authoring_status(policy: Mapping[str, Any], *, bypass_reason: str = "", actor: str | None = None, config: Any = None, action: str = "save", source_notebook_type: str = "02_pipeline", created_by_role: str = "engineering") -> dict[str, Any]:
    """Return lifecycle fields for authored guardrail and enrichment records.

    Parameters
    ----------
    policy : mapping
        Effective table governance policy.
    bypass_reason : str, optional
        Justification for immediate application when review is still required.
    actor : str, optional
        Current user identifier.
    config : Any, optional
        Runtime configuration used for timestamp formatting.
    action : {"save", "draft", "submit", "apply_now"}, default="save"
        Authoring action selected by the notebook user.
    source_notebook_type : {"02_pipeline", "03_governance"}, default="02_pipeline"
        Notebook type that created the record.
    created_by_role : {"engineering", "governance", "system"}, default="engineering"
        Role that created the record.

    Returns
    -------
    dict[str, Any]
        Lifecycle fields for metadata rows.

    """
    lifecycle = _authoring_lifecycle(policy, action=action, actor=actor, bypass_reason=bypass_reason, source_notebook_type=source_notebook_type, created_by_role=created_by_role, config=config)
    lifecycle.setdefault("approval_required", bool(lifecycle.get("requires_governance_review")))
    lifecycle.setdefault("approval_bypassed", bool(lifecycle.get("activation_reason") == "engineering_apply_now"))
    lifecycle.setdefault("author_role", created_by_role)
    lifecycle.setdefault("governance_mode", str(policy.get("governance_mode") or "ungoverned"))
    lifecycle.setdefault("approval_policy", str(policy.get("approval_policy") or ("no_approval_required" if _is_no_approval_required(policy) else "approval_required")))
    return lifecycle

def _record_identity(row: Mapping[str, Any]) -> str:
    """Return the stable lifecycle record identity for rule or enrichment rows."""
    return str(row.get("enrichment_rule_id") or row.get("rule_id") or row.get("enrichment_rule_key") or row.get("rule_key") or "")


def apply_governance_rule_action(rule: Mapping[str, Any], action: str, *, actor: str | None = None, superseded_by_rule_key: str = "", replacement: Mapping[str, Any] | None = None, source_notebook_type: str = "03_governance", config: Any = None) -> dict[str, Any] | list[dict[str, Any]]:
    """Return append-only governance action row(s) for a guardrail rule.

    Parameters
    ----------
    rule : mapping
        Existing rule row from ``METADATA_GUARDRAIL_RULES``.
    action : str
        One of ``approve``, ``approve_and_activate``, ``reject``, ``replace``,
        ``deactivate``, or legacy ``supersede``.
    actor : str, optional
        Reviewer identity.
    superseded_by_rule_key : str, optional
        Replacement rule key for supersede/replace actions.
    replacement : mapping, optional
        Replacement rule values when action is ``replace``.
    source_notebook_type : str, default="03_governance"
        Must be ``03_governance`` for formal review decisions.
    config : Any, optional
        Runtime configuration used for timestamps.

    Returns
    -------
    dict or list of dict
        One review row, or old/new rows for ``replace``.

    """
    _assert_governance_review_context(source_notebook_type)
    row = dict(rule)
    now = _audit_timestamp_value(config)
    reviewer = _resolve_action_by(actor)
    legacy_supersede = action == "supersede"
    action = "replace" if legacy_supersede else action
    common = {"source_notebook_type": "03_governance", "created_by_role": "governance", "reviewed_by": reviewer, "reviewed_at": now, "review_comment": str(row.get("review_comment") or ""), "requires_governance_review": False, "requires_post_review": False}
    if action in {"approve", "approve_and_activate"}:
        row.update(common | {"activation_state": "active", "is_active": True, "review_state": "governance_approved", "review_status": "governance_approved", "approved_by": reviewer, "approved_at": now, "review_decision": "approved", "activated_by": row.get("activated_by") or reviewer, "activated_at": row.get("activated_at") or now, "effective_from": row.get("effective_from") or now})
    elif action == "reject":
        row.update(common | {"activation_state": "inactive", "is_active": False, "review_state": "rejected_by_governance", "review_status": "rejected_by_governance", "review_decision": "rejected", "effective_to": now})
    elif action == "deactivate":
        row.update(common | {"activation_state": "inactive", "is_active": False, "review_state": "inactive", "review_status": "inactive", "review_decision": "deactivated", "effective_to": now})
    elif action == "replace":
        new = dict(row)
        new.update(dict(replacement or {}))
        new_id = str((replacement or {}).get("rule_id") or superseded_by_rule_key or f"{_record_identity(row)}.replacement.{uuid.uuid4().hex[:8]}")
        new_key = str(superseded_by_rule_key or (replacement or {}).get("rule_key") or f"{row.get('rule_key') or _record_identity(row)}:{uuid.uuid4().hex[:8]}")
        old = dict(row)
        old.update(common | {"activation_state": "inactive", "is_active": False, "review_state": "superseded", "review_status": "superseded", "review_decision": "superseded", "superseded_by_record_id": new_id, "superseded_by_rule_key": new_key, "effective_to": now})
        new.update(common | {"rule_id": new_id, "rule_key": new_key, "activation_state": "active", "is_active": True, "review_state": "governance_approved", "review_status": "governance_approved", "approved_by": reviewer, "approved_at": now, "review_decision": "approved", "activated_by": reviewer, "activated_at": now, "effective_from": now, "effective_to": "", "supersedes_record_id": _record_identity(row), "supersedes_rule_id": str(row.get("rule_id") or "")})
        return old if legacy_supersede else [old, new]
    else:
        raise ValueError("action must be one of approve, approve_and_activate, reject, replace, deactivate, or supersede")
    return row

def apply_governance_enrichment_action(record: Mapping[str, Any], action: str, *, actor: str | None = None, supersedes_enrichment_rule_id: str = "", replacement: Mapping[str, Any] | None = None, source_notebook_type: str = "03_governance", config: Any = None) -> dict[str, Any] | list[dict[str, Any]]:
    """Return append-only governance action row(s) for enrichment intent.

    Parameters
    ----------
    record : mapping
        Existing enrichment row from ``METADATA_ENRICHMENT_RULES``.
    action : str
        One of ``approve``, ``approve_and_activate``, ``reject``, ``replace``,
        ``deactivate``, legacy ``supersede``, or ``clear_post_review``.
    actor : str, optional
        Reviewer identity.
    supersedes_enrichment_rule_id : str, optional
        Replacement identity for legacy callers.
    replacement : mapping, optional
        Replacement enrichment values when action is ``replace``.
    source_notebook_type : str, default="03_governance"
        Must be ``03_governance`` for formal review decisions.
    config : Any, optional
        Runtime configuration used for timestamps.

    Returns
    -------
    dict or list of dict
        One review row, or old/new rows for ``replace``.

    """
    _assert_governance_review_context(source_notebook_type)
    row = dict(record)
    now = _audit_timestamp_value(config)
    reviewer = _resolve_action_by(actor)
    legacy_supersede = action == "supersede"
    action = "replace" if legacy_supersede else action
    common = {"source_notebook_type": "03_governance", "created_by_role": "governance", "reviewed_by": reviewer, "reviewed_at": now, "updated_by": reviewer, "updated_at": now, "requires_governance_review": False, "requires_post_review": False}
    if action in {"approve", "approve_and_activate"}:
        row.update(common | {"activation_state": "active", "is_active": True, "review_state": "governance_approved", "review_status": "governance_approved", "rule_status": "governance_approved", "review_decision": "approved", "activated_by": row.get("activated_by") or reviewer, "activated_at": row.get("activated_at") or now, "effective_from": row.get("effective_from") or now})
    elif action == "reject":
        row.update(common | {"activation_state": "inactive", "is_active": False, "review_state": "rejected_by_governance", "review_status": "rejected_by_governance", "rule_status": "rejected_by_governance", "review_decision": "rejected", "effective_to": now})
    elif action == "deactivate":
        row.update(common | {"activation_state": "inactive", "is_active": False, "review_state": "inactive", "review_status": "inactive", "rule_status": "inactive", "review_decision": "deactivated", "effective_to": now})
    elif action == "clear_post_review":
        row.update(common | {"review_decision": "post_review_cleared"})
    elif action == "replace":
        new = dict(row)
        new.update(dict(replacement or {}))
        old_id = _record_identity(row)
        new_id = str((replacement or {}).get("enrichment_rule_id") or supersedes_enrichment_rule_id or f"{old_id}.replacement.{uuid.uuid4().hex[:8]}")
        old = dict(row)
        old.update(common | {"activation_state": "inactive", "is_active": False, "review_state": "superseded", "review_status": "superseded", "rule_status": "superseded", "review_decision": "superseded", "superseded_by_record_id": new_id, "effective_to": now})
        new.update(common | {"enrichment_rule_id": new_id, "activation_state": "active", "is_active": True, "review_state": "governance_approved", "review_status": "governance_approved", "rule_status": "governance_approved", "review_decision": "approved", "activated_by": reviewer, "activated_at": now, "effective_from": now, "effective_to": "", "supersedes_record_id": old_id, "supersedes_enrichment_rule_id": old_id})
        return old if legacy_supersede else [old, new]
    else:
        raise ValueError("action must be one of approve, approve_and_activate, reject, replace, deactivate, supersede, or clear_post_review")
    return row

def load_rule_review_history(rows: Iterable[Mapping[str, Any]], *, metadata_table_key: str = "", metadata_column_key: str = "", table_name: str = "", column_name: str = "") -> list[dict[str, Any]]:
    """Return approval history derived from append-only rule rows.

    Parameters
    ----------
    rows : iterable of mapping
        Rows from ``METADATA_ENRICHMENT_RULES`` or ``METADATA_GUARDRAIL_RULES``.
    metadata_table_key, metadata_column_key, table_name, column_name : str, optional
        Optional filters for the selected table or column.

    Returns
    -------
    list of dict
        History rows ordered by submitted or created timestamp.

    """
    history: list[dict[str, Any]] = []
    for raw in rows or []:
        row = dict(raw)
        if metadata_table_key and str(row.get("metadata_table_key") or row.get("table_key") or "") not in {"", metadata_table_key}:
            continue
        if metadata_column_key and str(row.get("metadata_column_key") or row.get("column_key") or "") not in {"", metadata_column_key}:
            continue
        if table_name and str(row.get("table_name") or "") != table_name:
            continue
        if column_name and str(row.get("column_name") or "") not in {"", column_name}:
            continue
        history.append({
            "rule_id": str(row.get("enrichment_rule_id") or row.get("rule_id") or ""),
            "rule_version": str(row.get("enrichment_rule_version") or row.get("rule_version") or row.get("created_at") or ""),
            "record_type": "enrichment" if row.get("enrichment_rule_id") or row.get("enrichment_type") else "guardrail",
            "rule_type": str(row.get("enrichment_type") or row.get("guardrail_type") or row.get("rule_type") or ""),
            "review_status": str(row.get("review_status") or ""),
            "is_active": bool(row.get("is_active")),
            "submitted_by": str(row.get("submitted_by") or row.get("created_by") or ""),
            "submitted_at": str(row.get("submitted_at") or row.get("created_at") or ""),
            "reviewed_by": str(row.get("reviewed_by") or row.get("approved_by") or ""),
            "reviewed_at": str(row.get("reviewed_at") or row.get("approved_at") or ""),
            "decision": str(row.get("review_decision") or row.get("review_status") or ""),
            "comment": str(row.get("review_comment") or row.get("notes") or ""),
            "bypass_reason": str(row.get("bypass_reason") or ""),
            "requires_post_review": bool(row.get("requires_post_review")),
            "superseded_reference": str(row.get("supersedes_enrichment_rule_id") or row.get("supersedes_rule_id") or row.get("superseded_by_rule_key") or ""),
        })
    history.sort(key=lambda item: (item["submitted_at"], item["rule_id"]))
    return history

def _write_enrichment_records(records: list[dict[str, Any]], *, config: Any, env: str, spark_session: Any) -> None:
    """Append records to ``METADATA_ENRICHMENT_RULES``."""
    _write_table_metadata_enrichment_records(records, config=config, env=env, spark_session=spark_session)

def _base_guardrail_rule_record(state: Mapping[str, Any], *, guardrail_type: str, rule_type: str, column_name: str = "", parameters: Mapping[str, Any] | None = None, severity: str = "warning", description: str = "", policy: Mapping[str, Any] | None = None, bypass_reason: str = "", actor: str | None = None, action: str = "submit", source_notebook_type: str = "02_pipeline", created_by_role: str = "engineering", config: Any = None) -> dict[str, Any]:
    """Build one ``METADATA_GUARDRAIL_RULES`` record for widget save actions."""
    env = str(state.get("environment_name") or "")
    dataset = str(state.get("dataset_name") or "")
    table = str(state.get("table_name") or "")
    rule_id = f"{table}.{column_name or '_table'}.{guardrail_type}.{rule_type}"
    lifecycle = guardrail_authoring_status(
        policy or state,
        bypass_reason=bypass_reason,
        actor=actor,
        config=config,
        action=action,
        source_notebook_type=source_notebook_type,
        created_by_role=created_by_role,
    )
    created_at = _audit_timestamp_value(config)
    created_by = _resolve_action_by(actor)
    return {"rule_key": _build_dq_rule_key(env, dataset, table, rule_id), "rule_id": rule_id, "metadata_column_key": _build_metadata_column_key(env, dataset, table, column_name) if column_name else "", "metadata_table_key": str(state.get("metadata_table_key") or _build_metadata_table_key(env, dataset, table)), "environment_name": env, "dataset_name": dataset, "table_name": table, "column_name": column_name, "guardrail_type": guardrail_type, "rule_type": rule_type, "rule_parameters_json": json.dumps(parameters or {}, sort_keys=True, default=str), "severity": severity, "description": description, "created_by": created_by, "created_at": created_at, "submitted_by": created_by, "submitted_at": created_at, "reviewed_by": created_by if lifecycle.get("review_status") == "self_approved" else "", "reviewed_at": created_at if lifecycle.get("review_status") == "self_approved" else "", "review_decision": lifecycle.get("review_status", ""), "review_comment": "", "supersedes_rule_id": "", "effective_from": created_at if lifecycle.get("is_active") else "", "effective_to": "", "action_type": "created", "source_notebook_type": source_notebook_type, "source_notebook_id": str(state.get("notebook_id") or ""), **lifecycle}


def _read_metadata_table_or_empty(config: Any, env: str, table_name: str, *, spark_session: Any) -> list[dict[str, Any]]:
    """Read a metadata table and return row dictionaries."""
    try:
        frame = read_lakehouse_table_core(
            table_name,
            target="metadata",
            schema=configured_lakehouse_schema(config, env, "metadata"),
            context={"config": config, "env": env},
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
    write_lakehouse_table_core(
        spark_session.createDataFrame([coerce_metadata_row_types(GUARDRAIL_RULES_TABLE, record) for record in records]),
        GUARDRAIL_RULES_TABLE,
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
        mode="append",
    )



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
    action: str = "submit",
    source_notebook_type: str = "02_pipeline",
    created_by_role: str = "engineering",
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
            action=action,
            source_notebook_type=source_notebook_type,
            created_by_role=created_by_role,
            config=config,
        ),
        _base_guardrail_rule_record(
            state,
            guardrail_type="freshness",
            rule_type="max_lag_days" if str(freshness_mode) == "enforce" else "skip",
            parameters={"freshness_column": freshness_column if str(freshness_mode) == "enforce" else "", "max_lag_days": lag_days},
            description="Freshness guardrail",
            bypass_reason=bypass_reason,
            action=action,
            source_notebook_type=source_notebook_type,
            created_by_role=created_by_role,
            config=config,
        ),
        _base_guardrail_rule_record(
            state,
            guardrail_type="profile_behavior",
            rule_type=str(profile_mode),
            parameters={"watermark_column": watermark_column if str(profile_mode) == "changing_data" else ""},
            description="Profile behavior guardrail",
            bypass_reason=bypass_reason,
            action=action,
            source_notebook_type=source_notebook_type,
            created_by_role=created_by_role,
            config=config,
        ),
    ]



def _dq_records_from_selection(
    state: Mapping[str, Any],
    *,
    rule_type: str,
    selected_columns: Iterable[str],
    parameters: Mapping[str, Any] | None = None,
    severity: str = "warning",
    bypass_reason: str = "",
    action_type: str = "created",
    action: str = "submit",
    source_notebook_type: str = "02_pipeline",
    created_by_role: str = "engineering",
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
            action=action,
            source_notebook_type=source_notebook_type,
            created_by_role=created_by_role,
            config=config,
        )
        record["action_type"] = action_type
        if action_type in {"deactivated", "superseded"}:
            record["is_active"] = False
            record["review_status"] = "superseded" if action_type == "superseded" else "rejected"
        records.append(record)
    return records



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
        table governance policy dictionary for catalogue-backed selected state.

    """
    mode = str(governance_mode or "ungoverned").lower()
    if mode not in {"governed", "ungoverned"}:
        raise ValueError("governance_mode must be governed or ungoverned")
    policy = str(approval_policy or ("approval_required_with_bypass" if mode == "governed" else "no_approval_required"))
    now = _audit_timestamp_value(config)
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






# ---------------------------------------------------------------------------
# Public API wrappers
# ---------------------------------------------------------------------------

def get_latest_metadata_catalogue(
    *,
    table_name: str,
    agreement: Mapping[str, Any] | None = None,
    metadata_schema: str | None = None,
    spark_session: Any = None,
    context: dict[str, Any] | None = None,
) -> Any:
    """Return the latest metadata catalogue rows for an exploratory table lookup."""
    return _latest_metadata_catalogue_lookup_workflow(
        table_name=table_name,
        agreement=agreement,
        metadata_schema=metadata_schema,
        spark_session=spark_session,
        context=context,
    )
