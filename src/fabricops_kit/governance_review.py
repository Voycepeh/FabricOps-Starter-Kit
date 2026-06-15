"""Table-scoped governance review helpers for ``03_governance`` notebooks."""

from __future__ import annotations

import ast
import importlib
import json
import re
import uuid
from typing import Any, Iterable

from .config import DEFAULT_BUSINESS_CONTEXT_PROMPT_TEMPLATE, DEFAULT_DQ_RULE_SUGGESTION_PROMPT_TEMPLATE, DEFAULT_GOVERNANCE_PERSONAL_IDENTIFIER_PROMPT_TEMPLATE, _current_audit_timestamp, _get_audit_timezone
from .fabric_input_output import _configured_lakehouse_schema, read_lakehouse_table, write_lakehouse_table
from .data_profiling import profile_dataframe
from .metadata import _now_utc_iso, _resolve_action_by, _build_metadata_column_key, _build_metadata_table_key, _build_runtime_audit_fields, _build_dq_rule_key
from .data_agreement import DATA_AGREEMENT_TABLE, DATA_AGREEMENT_EVIDENCE_TABLE

CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
COLUMN_CONTEXT_TABLE = "METADATA_COLUMN_CONTEXT"
GUARDRAIL_RULES_TABLE = "METADATA_GUARDRAIL_RULES"
GUARDRAIL_RESULTS_TABLE = "METADATA_GUARDRAIL_RESULTS"
GUARDRAIL_TYPES = ["schema", "freshness", "profile_behavior", "dq"]
GUARDRAIL_REVIEW_STATUSES = ["draft", "proposed", "engineer_approved", "governance_approved", "rejected", "superseded", "inactive"]
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
SENSITIVITY_LABELS = ["public", "internal", "confidential", "restricted"]
PERSONAL_DATA_CLASSIFICATIONS = ["not_personal_data", "direct_identifier", "indirect_identifier", "sensitive_personal_data", "unknown"]
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
        ("source_data_change_check", string), ("target_data_change_check", string), ("profile_baseline_mode", string), ("data_type", string), ("row_count", long), ("null_count", long), ("distinct_count", long),
        ("distribution_type", string), ("distribution_json", string), ("profiled_at", string), ("run_timestamp", timestamp), ("null_percent", double), ("distinct_percent", double), ("min_value", string), ("max_value", string),
        ("agreement_id", string), ("contract_version", string), ("notebook_registry_id", string), ("notebook_id", string), ("evidence_role", string),
        ("source_schema_check", string), ("target_schema_check", string),
        ("stability_check_enabled", boolean), ("load_behavior", string), ("watermark_column", string), ("watermark_value", string),
        ("profile_hash", string), ("profile_payload_json", string),
        ("freshness_column", string), ("freshness_max_lag_days", string), ("freshness_status", string), ("freshness_can_continue", boolean), ("freshness_message", string),
        ("baseline_run_id", string), ("stability_status", string), ("stability_can_continue", boolean), ("stability_message", string), ("stability_difference_summary", string),
        ("source_change_signal_json", string),
        ("dq_status", string), ("dq_rule_count", long), ("dq_failed_rule_count", long), ("dq_warning_rule_count", long), ("dq_error_rule_count", long), ("dq_failed_row_count", long), ("dq_failed_row_percent", double), ("dq_checked_at", string),
        *audit,
    ]
    return {
        CATALOGUE_TABLE: _schema(CATALOGUE_TABLE, catalogue),
        COLUMN_CONTEXT_TABLE: _schema(COLUMN_CONTEXT_TABLE, [("metadata_column_key", string), ("metadata_table_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("business_context", string), ("notes", string), ("review_status", string), ("approved_by", string), ("approved_at", string), ("ai_suggestion_json", string), *audit]),
        GUARDRAIL_RULES_TABLE: _schema(GUARDRAIL_RULES_TABLE, [("rule_key", string), ("rule_id", string), ("metadata_column_key", string), ("metadata_table_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("guardrail_type", string), ("rule_type", string), ("rule_parameters_json", string), ("severity", string), ("description", string), ("is_active", boolean), ("review_status", string), ("author_role", string), ("created_by", string), ("created_at", string), ("approved_by", string), ("approved_at", string), ("ai_suggestion_json", string), ("action_type", string), ("source_notebook_type", string), ("source_notebook_id", string), ("source_workspace_id", string), ("superseded_by_rule_key", string), ("notes", string), *audit]),
        GUARDRAIL_RESULTS_TABLE: _schema(GUARDRAIL_RESULTS_TABLE, [("result_id", string), ("run_id", string), ("rule_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("guardrail_type", string), ("rule_type", string), ("status", string), ("can_continue", boolean), ("severity", string), ("reason", string), ("expected_value_json", string), ("actual_value_json", string), ("result_payload_json", string), ("created_at", string), *audit]),
        COLUMN_CLASSIFICATION_TABLE: _schema(COLUMN_CLASSIFICATION_TABLE, [("metadata_column_key", string), ("metadata_table_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("sensitivity_label", string), ("personal_data_classification", string), ("pii_identifier_type", string), ("handling_requirement", string), ("reasoning", string), ("review_status", string), ("approved_by", string), ("approved_at", string), ("ai_suggestion_json", string), *audit]),
        LINEAGE_TABLE: _schema(LINEAGE_TABLE, [("lineage_id", string), ("dataset_name", string), ("run_id", string), ("source_table", string), ("target_table", string), ("source_table_key", string), ("target_table_key", string), ("transformation_steps_json", string), ("created_at", string), *audit]),
        PIPELINE_RUNS_TABLE: _schema(PIPELINE_RUNS_TABLE, [("run_id", string), ("agreement_id", string), ("agreement_contract_version", string), ("notebook_registry_id", string), ("notebook_id", string), ("notebook_type", string), ("pipeline_name", string), ("environment_name", string), ("started_at", string), ("completed_at", string), ("status", string), ("source_count", long), ("target_count", long), ("source_guardrail_status", string), ("target_guardrail_status", string), ("dq_status", string), ("lineage_status", string), ("catalogue_status", string), ("message", string), ("run_summary_json", string), ("created_at", string)]),
        GOVERNANCE_REVIEWS_TABLE: _schema(GOVERNANCE_REVIEWS_TABLE, [("review_id", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("metadata_table_key", string), ("profile_run_id", string), ("profile_stage", string), ("pipeline_run_id", string), ("agreement_id", string), ("agreement_contract_version", string), ("outcome", string), ("blocker_count", long), ("warning_count", long), ("blockers_json", string), ("warnings_json", string), ("evidence_summary_json", string), ("reviewed_at", string), ("reviewed_by", string), *audit]),
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


def get_selected_catalogue_table(table_selector: Any | None = None) -> dict[str, Any]:
    """Return the catalogue table selected by ``widget_select_governance_profile_target``.

    Parameters
    ----------
    table_selector : ipywidgets.VBox, optional
        Selector returned by ``widget_select_governance_profile_target``. Passing it is
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
    raise ValueError("No catalogue table has been selected. Run widget_select_governance_profile_target first.")


def widget_select_governance_profile_target(config: Any, env: str, *, spark_session: Any):
    """Render dependent selectors for a governed table profile target.

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
    ipywidgets.VBox
        Container with dependent asset, schema/layer, table, and profile-run
        dropdowns. The selected profile row identity is available through
        ``get_selected_catalogue_table``.

    Notes
    -----
    Table identity is based on physical catalogue fields and intentionally
    excludes ``profile_stage`` and pipeline metadata. Source/target stage and
    pipeline values remain visible as profile evidence for the selected table.

    """
    global _SELECTED_CATALOGUE_TABLE
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    rows = _coerce_rows(read_lakehouse_table(config, env, "metadata", CATALOGUE_TABLE, schema=_configured_lakehouse_schema(config, env, "metadata"), spark_session=spark_session))
    model = _catalogue_profile_target_model(rows)
    assets = model["assets"]
    asset_dropdown = widgets.Dropdown(options=list(assets), description="Asset", layout=widgets.Layout(width="760px"))
    schema_dropdown = widgets.Dropdown(description="Schema/layer", layout=widgets.Layout(width="760px"))
    table_dropdown = widgets.Dropdown(description="Table", layout=widgets.Layout(width="760px"))
    profile_dropdown = widgets.Dropdown(description="Profile", layout=widgets.Layout(width="980px"))
    context = widgets.HTML()

    def current_table_entry() -> dict[str, Any]:
        return assets[asset_dropdown.value]["schemas"][schema_dropdown.value]["tables"][table_dropdown.value]

    def apply_selection() -> None:
        global _SELECTED_CATALOGUE_TABLE
        entry = current_table_entry()
        profile_by_label = {p["label"]: p for p in entry["profiles"]}
        selected = profile_by_label.get(profile_dropdown.value) or entry["default"]
        _SELECTED_CATALOGUE_TABLE = dict(selected)
        context.value = (
            f"<b>Selected table:</b> {selected.get('environment_name','')} / {selected.get('asset_name','')} / "
            f"{selected.get('schema_or_layer','') or '-'} / {selected.get('table_name','')}<br/>"
            f"<b>Profile:</b> {selected.get('profiled_at','')} | run {selected.get('profile_run_id','-')} "
            f"| stage {selected.get('profile_stage','-')} | status {selected.get('profile_status','-')}"
        )

    def refresh_profiles(*_: Any) -> None:
        entry = current_table_entry()
        labels = [p["label"] for p in entry["profiles"]]
        profile_dropdown.options = labels
        default = entry["default"]
        default_label = next((p["label"] for p in entry["profiles"] if p["profile_run_id"] == default.get("profile_run_id") and p["profile_stage"] == default.get("profile_stage") and p["profiled_at"] == default.get("profiled_at")), labels[0])
        profile_dropdown.value = default_label
        apply_selection()

    def refresh_tables(*_: Any) -> None:
        tables = assets[asset_dropdown.value]["schemas"][schema_dropdown.value]["tables"]
        table_dropdown.options = sorted(tables)
        table_dropdown.value = table_dropdown.options[0]
        refresh_profiles()

    def refresh_schemas(*_: Any) -> None:
        schemas = assets[asset_dropdown.value]["schemas"]
        schema_dropdown.options = sorted(schemas)
        schema_dropdown.value = schema_dropdown.options[0]
        refresh_tables()

    asset_dropdown.observe(lambda change: refresh_schemas() if change.get("name") == "value" else None, names="value")
    schema_dropdown.observe(lambda change: refresh_tables() if change.get("name") == "value" else None, names="value")
    table_dropdown.observe(lambda change: refresh_profiles() if change.get("name") == "value" else None, names="value")
    profile_dropdown.observe(lambda change: apply_selection() if change.get("name") == "value" else None, names="value")
    refresh_schemas()
    box = widgets.VBox([asset_dropdown, schema_dropdown, table_dropdown, profile_dropdown, context])
    ip.display(box)
    return box


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
            "business_context": str(review.get("business_context") or ""), "notes": str(review.get("notes") or ""), "review_status": "approved",
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
    """Build append-only approved DQ-rule records without enforcing them."""
    profile, actor, now, audit = _approved_review_context(profile_rows, config=config, env=env, approved_by=approved_by)
    rows = []
    for rule in reviewed_rules or []:
        if not rule.get("commit"):
            continue
        review_status = str(rule.get("review_status", "approved")).lower()
        action_type = str(rule.get("action_type") or ("created" if rule.get("is_active", True) else "deactivated")).lower()
        if action_type == "delete":
            action_type = "deactivated"
        if action_type not in {"created", "updated", "deactivated", "reactivated", "approved"}:
            raise ValueError(f"Unsupported DQ action_type: {action_type}")
        is_active = bool(rule.get("is_active", action_type != "deactivated"))
        if action_type == "deactivated":
            is_active = False
        if action_type == "reactivated":
            is_active = True
        if review_status != "approved":
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
            "severity": str(rule.get("severity") or "warning").lower(),
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
        sensitivity = str(review.get("sensitivity_label") or "internal")
        classification = str(review.get("personal_data_classification") or "unknown")
        if sensitivity not in SENSITIVITY_LABELS:
            raise ValueError(f"Unsupported sensitivity_label: {sensitivity}")
        if classification not in PERSONAL_DATA_CLASSIFICATIONS:
            raise ValueError(f"Unsupported personal_data_classification: {classification}")
        identity = _approved_column_identity(profile.get(str(review.get("column_name")), {}), review, env=env)
        rows.append({
            **identity,
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


def _dq_parameter_fields_for_rule_type(rule_type: str) -> list[str]:
    """Return parameter names a reviewer should fill for a rule type."""
    return {
        "null_rate_below": ["max_null_percent"],
        "accepted_values": ["allowed_values"],
        "not_in_values": ["blocked_values"],
        "between": ["min_value", "max_value"],
        "date_between": ["min_value", "max_value"],
        "greater_than": ["value"],
        "greater_than_or_equal": ["value"],
        "less_than": ["value"],
        "less_than_or_equal": ["value"],
        "regex_match": ["regex_pattern"],
        "freshness": ["max_age_days"],
        "max_age_days": ["max_age_days"],
        "required_when": ["condition"],
        "value_when": ["condition", "expected_value"],
        "expression_true": ["expression"],
    }.get(_canonical_dq_rule_type(rule_type), [])


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


def widget_review_dq_rules(
    profile_rows: list[dict[str, Any]],
    *,
    existing_rules: list[dict[str, Any]] | None = None,
    config: Any = None,
    env: str | None = None,
    spark_session: Any = None,
    table_name: str | None = None,
    business_context: str = "",
) -> list[dict[str, Any]]:
    """Render a table-driven DQ-rule review widget for ``03_governance``.

    Parameters
    ----------
    profile_rows : list of dict
        Selected catalogue profile rows containing columns and profile evidence.
    existing_rules : list of dict, optional
        Previously persisted active and inactive DQ guardrail rows for the
        selected table. When supplied, the widget displays them in an editable
        review table. Runtime enforcement reads ``METADATA_GUARDRAIL_RULES``.
    config, env, spark_session : optional
        Runtime objects used only when reviewers click AI suggestion actions.
    table_name : str, optional
        Selected table name. Defaults to the table in ``profile_rows``.
    business_context : str, default=""
        Optional context sent to the Fabric AI suggestion helper.

    Returns
    -------
    list[dict[str, Any]]
        Mutable review list. The widget appends approved create, update,
        deactivation, and reactivation dictionaries to this list; pass it to
        ``record_table_governance`` to persist append-only metadata history.

    """
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    review_rows: list[dict[str, Any]] = []
    columns = [str(_value(row, "column_name")) for row in profile_rows]
    selected_table = table_name or str(_value(profile_rows[0], "table_name") if profile_rows else "")
    rules_table = _dq_rule_display_rows(existing_rules or [])

    table_dropdown = widgets.Dropdown(options=[selected_table] if selected_table else [], value=selected_table or None, description="Table")
    rule_type_dropdown = widgets.Dropdown(options=DQ_RULE_TYPES, value="not_null", description="Rule")
    column_select = widgets.SelectMultiple(options=columns, description="Columns", rows=min(max(len(columns), 4), 12), layout=widgets.Layout(width="420px"))
    severity = widgets.ToggleButtons(options=["warning", "error"], value="warning", description="Severity")
    description = widgets.Textarea(description="Description", layout=widgets.Layout(width="760px", height="70px"))
    params = widgets.Textarea(description="Parameters JSON", value="{}", layout=widgets.Layout(width="760px", height="90px"))
    parameter_guidance = widgets.HTML()
    rule_id = widgets.Text(description="Rule ID", layout=widgets.Layout(width="760px"))
    preview = widgets.Textarea(description="Preview", disabled=True, layout=widgets.Layout(width="900px", height="160px"))
    existing_options = [(f"{r['Rule ID']} · {r['Rule type']} · {r['Column(s)']} · {r['Status']}", i) for i, r in enumerate(rules_table)]
    existing_select = widgets.Dropdown(options=existing_options, description="Edit rule") if existing_options else widgets.HTML("<i>No existing rules supplied for this table.</i>")
    rules_html = widgets.HTML("<pre>" + json.dumps(rules_table, indent=2, default=str) + "</pre>")
    message = widgets.HTML()

    def current_rule(action_type: str = "created") -> dict[str, Any]:
        extra = json.loads(params.value or "{}")
        cols = list(column_select.value)
        draft = {
            "rule_id": rule_id.value or f"{selected_table}_{rule_type_dropdown.value}_{uuid.uuid4().hex[:8]}",
            "rule_type": rule_type_dropdown.value,
            "columns": cols,
            "severity": severity.value,
            "description": description.value,
            "is_active": action_type != "deactivated",
            "review_status": "approved",
            "action_type": action_type,
            "commit": True,
            **extra,
        }
        _validate_dq_rules([draft])
        return draft

    def refresh_parameter_guidance(*_: Any) -> None:
        required = _dq_parameter_fields_for_rule_type(rule_type_dropdown.value)
        if required:
            parameter_guidance.value = f"<b>Required parameters for this rule:</b> {', '.join(required)}"
        else:
            parameter_guidance.value = "<b>No extra parameters required.</b>"

    def refresh_preview(*_: Any) -> None:
        refresh_parameter_guidance()
        try:
            preview.value = json.dumps(current_rule("created"), indent=2, default=str)
            message.value = ""
        except Exception as exc:
            preview.value = ""
            message.value = f"<b>Validation:</b> {exc}"

    def load_existing(_: Any = None) -> None:
        if not existing_options or not hasattr(existing_select, "value"):
            return
        source = (existing_rules or [])[int(existing_select.value)]
        raw = source.get("rule_parameters_json") or "{}"
        try:
            parsed = json.loads(raw) if isinstance(raw, str) else dict(raw)
        except Exception:
            parsed = {}
        cols = parsed.pop("columns", None) or source.get("columns") or source.get("column_name") or []
        if isinstance(cols, str):
            cols = [c.strip() for c in cols.split(",") if c.strip()]
        rule_id.value = str(source.get("rule_id") or "")
        rule_type_dropdown.value = _canonical_dq_rule_type(source.get("rule_type"))
        column_select.value = tuple(c for c in cols if c in columns)
        severity.value = str(source.get("severity") or "warning")
        description.value = str(source.get("description") or "")
        params.value = json.dumps(parsed, indent=2, default=str)
        refresh_preview()

    def append_action(action: str) -> None:
        try:
            review_rows.append(current_rule(action))
            message.value = f"<b>Queued {action}.</b> Pass the returned list to record_table_governance to commit."
        except Exception as exc:
            message.value = f"<b>Cannot queue action:</b> {exc}"

    def suggest_ai(_: Any = None) -> None:
        try:
            prompt = getattr(getattr(config, "ai_prompt_config", None), "dq_rule_suggestion_prompt_template", "") if config is not None else ""
            profile_df = spark_session.createDataFrame(profile_rows) if spark_session is not None and not hasattr(profile_rows, "ai") else profile_rows
            drafts = _draft_dq_rules(profile_df=profile_df, table_name=selected_table, business_context=business_context, prompt_template=prompt, config=config)
            for draft in drafts:
                draft.update({"review_status": "draft", "is_active": False, "commit": False})
            review_rows.extend(drafts)
            message.value = f"<b>Loaded {len(drafts)} AI draft suggestion(s).</b> Review, edit, and mark commit=True before approval."
        except Exception as exc:
            message.value = f"<b>AI suggestion failed:</b> {exc}"

    for control in (rule_type_dropdown, column_select, severity, description, params, rule_id):
        control.observe(lambda change: refresh_preview(), names="value")
    if hasattr(existing_select, "observe"):
        existing_select.observe(lambda change: load_existing(), names="value")

    create_button = widgets.Button(description="Save approved active rule", button_style="success")
    update_button = widgets.Button(description="Update selected rule", button_style="info")
    delete_button = widgets.Button(description="Delete / deactivate", button_style="warning")
    reactivate_button = widgets.Button(description="Reactivate", button_style="success")
    ai_button = widgets.Button(description="AI suggest rules", button_style="")
    create_button.on_click(lambda _: append_action("created"))
    update_button.on_click(lambda _: append_action("updated"))
    delete_button.on_click(lambda _: append_action("deactivated"))
    reactivate_button.on_click(lambda _: append_action("reactivated"))
    ai_button.on_click(suggest_ai)

    refresh_preview()
    ip.display(widgets.VBox([
        widgets.HTML("<h3>DQ rule review</h3><p>Select a table, review columns and existing active/inactive rules, then queue append-only create/update/deactivate/reactivate actions.</p>"),
        table_dropdown,
        widgets.HTML(f"<b>Columns in selected table:</b> {', '.join(columns)}"),
        widgets.HTML("<h4>Existing rules for selected table</h4>"),
        rules_html,
        existing_select,
        widgets.HBox([rule_type_dropdown, column_select]),
        rule_id,
        parameter_guidance,
        params,
        severity,
        description,
        preview,
        widgets.HBox([create_button, update_button, delete_button, reactivate_button, ai_button]),
        message,
    ]))
    return review_rows

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
        Human-approved rows from the governance review workflow. Only rows with
        ``review_status="approved"`` and ``commit=True`` are written.
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


def _draft_business_context(prepared_profile_df, prompt_template: str = BUSINESS_CONTEXT_PROMPT, output_col: str = "ai_business_context_response"):
    """Draft column business-context suggestions with Fabric AI."""
    return _run_fabric_ai_drafting(prepared_profile_df, prompt=prompt_template, output_col=output_col)


def _draft_governance(prepared_profile_df, prompt: str | None = None, output_col: str = "ai_governance_response"):
    """Draft sensitivity and PII classification suggestions with Fabric AI."""
    return _run_fabric_ai_drafting(prepared_profile_df, prompt=prompt or PDPA_PERSONAL_IDENTIFIER_PROMPT, output_col=output_col)


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
        rule.setdefault("description", "")
        rule["rule_type"] = _canonical_dq_rule_type(rule.get("rule_type"))
        rtype = rule["rule_type"]
        if rtype not in DQ_RULE_TYPES:
            raise ValueError(f"DQ rule '{rule['rule_id']}' has unsupported rule_type '{rtype}'.")
        if str(rule.get("severity", "warning")).lower() not in {"warning", "error"}:
            raise ValueError(f"DQ rule '{rule['rule_id']}' severity must be warning or error.")

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
    """Load active approved DQ rules from append-only metadata rows."""
    _, F, _ = _spark_sql_helpers()
    columns = set(getattr(metadata_df, "columns", []))
    latest = _latest_dq_rule_versions(metadata_df, table_name, env_name=env_name, dataset_name=dataset_name)
    if "is_active" in columns:
        latest = latest.filter(F.col("is_active") == True)
    if "action_type" in columns:
        latest = latest.filter(F.lower(F.coalesce(F.col("action_type"), F.lit("created"))) != "deactivated")
    if "review_status" in columns:
        latest = latest.filter(F.lower(F.coalesce(F.col("review_status"), F.lit("governance_approved"))).isin("approved", "engineer_approved", "governance_approved"))

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
                "severity": str(row.get("severity") or "warning"),
                "description": str(row.get("description") or ""),
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
        severity = str(rule.get("severity", "warning")).strip().lower()
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
        if str(rule.get("severity", "warning")).strip().lower() == "error"
    ]
    warning_failures = [
        F.when(_dq_failed_expression(df, rule), F.lit(1)).otherwise(F.lit(0))
        for rule in sorted_rules
        if str(rule.get("severity", "warning")).strip().lower() != "error"
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
        message = "No active approved DQ rules found."
    elif failed_checks:
        message = f"DQ guardrail found {len(failed_checks)} rule failure(s): {status}."
    else:
        message = f"DQ guardrail passed {len(checks)} active approved rule(s)."
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
) -> dict:
    """Enforce active approved DQ rules as a simple pipeline guardrail.

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
        Dataset identifier used with ``table_name`` to scope approved DQ rules
        when those columns exist in the metadata table.
    table_name : str
        Target table name whose approved active DQ rules should be enforced.
    spark_session : pyspark.sql.SparkSession, optional
        Spark session used to read metadata when required by the configured
        storage helper.

    Returns
    -------
    dict
        Guardrail result with ``status``, ``can_continue``, ``checks``, and
        ``message``. The result also carries the full tagged ``dataframe`` and
        aggregate ``summary`` fields for the existing catalogue evidence path.
        Error-severity rule failures return ``status='failed'`` and
        ``can_continue=False``. Warning-severity failures return
        ``status='warning'`` and ``can_continue=True``. Passing or absent rules
        return ``status='passed'`` and ``can_continue=True``.

    Notes
    -----
    This v1 guardrail reads approved active DQ rules from
    ``METADATA_GUARDRAIL_RULES`` via the configured metadata route. It records aggregate rule outcomes only; it
    does not quarantine rows, write row-level failure metadata, filter invalid
    rows, send alerts, or partially write targets.

    """
    metadata_df = _read_guardrail_rule_metadata(config, env, spark_session=spark_session)
    rules = _load_active_dq_rules(metadata_df, table_name=table_name, env_name=env, dataset_name=dataset_name)
    checks = _run_dq_guardrail_checks(dataframe, table_name=table_name, rules=rules) if rules else []
    total_count = int(dataframe.count())
    failed_row_count = _dq_failed_row_count(dataframe, rules) if rules else 0
    result = _summarize_dq_guardrail(checks)
    result["dataframe"] = _dq_tagged_dataframe(dataframe, rules)
    result["summary"] = _dq_summary(checks, total_count, failed_row_count, config=config)
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
