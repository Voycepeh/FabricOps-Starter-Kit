"""Shared widget rendering helpers for FabricOps notebook widgets."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field as dataclass_field
from datetime import date, datetime
import hashlib
import json
from typing import Any, Iterable, Mapping
import uuid

from fabricops_kit.config.shared import DEFAULT_STEWARD_ROLE_OPTIONS, get_current_audit_timestamp
from fabricops_kit.io.shared import configured_lakehouse_schema, read_lakehouse_table_core, write_lakehouse_table_core
from fabricops_kit.config.audit import _audit_timestamp_value, _resolve_action_by, build_runtime_audit_fields
from fabricops_kit.config.metadata_keys import _build_dq_rule_key, _build_metadata_column_key, _build_metadata_table_key
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types


_WIDGET_STYLE = {"description_width": "150px"}
_WIDGET_LAYOUT_WIDTH = "600px"
_TEXTAREA_HEIGHT = "80px"


def require_ipywidgets():
    """Return ipywidgets or raise an actionable optional-dependency error."""
    try:
        import ipywidgets as widgets
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "The FabricOps widget feature requires the 'dq-review' extra. "
            'Install with: pip install "fabricops-kit[dq-review]"'
        ) from exc
    return widgets


def widget_common(widgets_module: Any, description: str, *, textarea: bool = False) -> dict[str, Any]:
    """Return common style and layout keyword arguments for form controls."""
    common: dict[str, Any] = {"description": description, "style": dict(_WIDGET_STYLE)}
    layout_class = getattr(widgets_module, "Layout", None)
    if layout_class is not None:
        kwargs = {"width": _WIDGET_LAYOUT_WIDTH}
        if textarea:
            kwargs["height"] = _TEXTAREA_HEIGHT
        common["layout"] = layout_class(**kwargs)
    return common


def _html_escape(value: Any) -> str:
    """Return display-safe HTML text for notebook context snippets."""
    import html

    return html.escape(str(value or ""))


def render_searchable_selector(
    *,
    widgets: Any,
    label: str,
    rows: list[dict[str, Any]],
    label_fn: Callable[[dict[str, Any]], str],
    value_fn: Callable[[dict[str, Any]], str],
    placeholder: str = "Search...",
    max_results: int = 25,
    search_fields: list[str] | None = None,
    context_fields: list[tuple[str, str]] | None = None,
    empty_label: str | None = None,
    selected_value: str | None = None,
) -> dict[str, Any]:
    """Render a table-backed selector with search and stable-value tracking."""
    search = widgets.Text(value="", placeholder=placeholder, **widget_common(widgets, f"Search {label}"))
    selector = widgets.Select(options=[], **widget_common(widgets, label))
    context = widgets.HTML(value="")
    lookup: dict[str, dict[str, Any]] = {}
    indexed_rows: list[dict[str, Any]] = []

    def _set_rows(new_rows: list[dict[str, Any]]) -> None:
        lookup.clear()
        indexed_rows.clear()
        for row in new_rows:
            value = str(value_fn(row) or "")
            if not value:
                continue
            lookup[value] = row
            indexed_rows.append(row)

    def _matches(row: dict[str, Any], query: str) -> bool:
        if not query:
            return True
        fields = search_fields or list(row)
        haystack = " ".join(str(row.get(field, "")) for field in fields).lower()
        return query.lower() in haystack

    def _context_html(row: dict[str, Any] | None) -> str:
        if not row or not context_fields:
            return ""
        parts = [
            f"<b>{_html_escape(field_label)}:</b> {_html_escape(row.get(field, ''))}"
            for field, field_label in context_fields
        ]
        return "<br>".join(parts)

    def _refresh_options(*_: Any) -> None:
        current = str(selector.value or selected_value or "")
        query = str(search.value or "").strip()
        filtered = [row for row in indexed_rows if _matches(row, query)][:max_results]
        options = [(label_fn(row), str(value_fn(row) or "")) for row in filtered]
        if empty_label is not None:
            options = [(empty_label, ""), *options]
        selector.options = options
        values = [value for _, value in options]
        selector.value = current if current in values else (values[0] if values else None)
        context.value = _context_html(lookup.get(str(selector.value or "")))

    def _on_select(change: dict[str, Any]) -> None:
        if change.get("name") == "value":
            context.value = _context_html(lookup.get(str(change.get("new") or "")))

    def _refresh_rows(new_rows: list[dict[str, Any]], selected: str | None = None) -> None:
        nonlocal selected_value
        selected_value = selected
        _set_rows(new_rows)
        _refresh_options()

    search.observe(lambda change: _refresh_options() if change.get("name") == "value" else None, names="value")
    selector.observe(_on_select, names="value")
    _set_rows(rows)
    _refresh_options()
    selector.refresh_rows = _refresh_rows
    container = widgets.VBox([search, selector, context])
    return {"container": container, "search": search, "selector": selector, "context": context, "rows_by_value": lookup}


def render_custom_fields(config: list[dict[str, Any]] | dict[str, Any], *, values: dict[str, Any] | None = None) -> dict[str, Any]:
    """Render organization-specific custom fields from normalized config."""
    widgets = require_ipywidgets()
    fields = config.get("custom_fields", []) if isinstance(config, dict) else config
    rendered: dict[str, Any] = {}
    values = values or {}
    for field in fields or []:
        key = str(field.get("key") or "").strip()
        if not key:
            continue
        label = str(field.get("label") or key.replace("_", " ").title())
        field_type = str(field.get("type") or "text").lower()
        default = values.get(key, field.get("default", ""))
        common = widget_common(widgets, label, textarea=field_type == "textarea")
        if field_type == "textarea":
            rendered[key] = widgets.Textarea(value=str(default or ""), **common)
        elif field_type == "dropdown":
            options = field.get("options", []) or []
            rendered[key] = widgets.Dropdown(options=options, value=default if default in options else (options[0] if options else None), **common)
        elif field_type == "checkbox":
            rendered[key] = widgets.Checkbox(value=bool(default), **common)
        else:
            rendered[key] = widgets.Text(value=str(default or ""), **common)
    return rendered


def standard_widget(field: str, value: Any = "", *, options: list[Any] | None = None) -> Any:
    """Render a standard widget control for a configured field name."""
    widgets = require_ipywidgets()
    description = field.replace("_", " ").title()
    if options is not None:
        default_value = value if value in options else (options[0] if options else None)
        return widgets.Dropdown(options=options, value=default_value, **widget_common(widgets, description))
    if field.endswith("_date") or field in {"effective_from", "effective_to", "start_date", "expiry_date"}:
        return widgets.DatePicker(value=date.fromisoformat(str(value)[:10]) if value else None, **widget_common(widgets, description))
    if field == "is_active":
        return widgets.Checkbox(value=True if value == "" else str(value).strip().lower() in {"1", "true", "yes", "y"}, **widget_common(widgets, description))
    if field in {"business_purpose"}:
        return widgets.Textarea(value=str(value or ""), **widget_common(widgets, description, textarea=True))
    return widgets.Text(value=str(value or ""), **widget_common(widgets, description))



# Widget-owned helper implementations migrated from data_agreement.py.
DATA_AGREEMENT_TABLE = "METADATA_DATA_AGREEMENT"
DATA_AGREEMENT_EVIDENCE_TABLE = "METADATA_DATA_AGREEMENT_EVIDENCE"
DATA_STEWARD_TABLE = "METADATA_DATA_STEWARD"
STANDARD_RUNTIME_AUDIT_COLUMNS = ["_committed_by", "_committed_at", "_workspace_id", "_workspace_name", "_notebook_id", "_notebook_name", "_metadata_lakehouse_name", "_activity_id"]
DATA_STEWARD_VISIBLE_FIELDS = ["steward_name", "steward_role", "contact", "effective_from", "effective_to"]
DATA_STEWARD_BACKEND_FIELDS = ["steward_id", *DATA_STEWARD_VISIBLE_FIELDS, "is_active"]
DATA_AGREEMENT_VISIBLE_FIELDS = ["agreement_name", "domain", "steward_id", "recipient", "start_date", "expiry_date", "business_purpose"]
DATA_AGREEMENT_GENERATED_FIELDS = ["agreement_id", "agreement_version"]
DATA_STEWARD_FIELDS = DATA_STEWARD_BACKEND_FIELDS + ["custom_fields_json"] + STANDARD_RUNTIME_AUDIT_COLUMNS
DATA_AGREEMENT_FIELDS = DATA_AGREEMENT_GENERATED_FIELDS + DATA_AGREEMENT_VISIBLE_FIELDS + ["custom_fields_json"] + STANDARD_RUNTIME_AUDIT_COLUMNS
DATA_AGREEMENT_EVIDENCE_FIELDS = ["agreement_id", "agreement_version", "evidence_type", "file_name", "file_path", "mime_type", "file_size", *STANDARD_RUNTIME_AUDIT_COLUMNS]
AGREEMENT_EVIDENCE_ALLOWED_EXTENSIONS = (".pdf", ".doc", ".docx", ".png", ".jpg", ".jpeg")
AGREEMENT_EVIDENCE_MIME_TYPES = {".pdf": "application/pdf", ".doc": "application/msword", ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
AGREEMENT_EVIDENCE_TYPES = ["Signed Agreement", "Email Approval", "Policy Document", "Supporting Screenshot", "Other"]
WIDGET_CONFIG_DEFAULTS = {"data_steward_widget": {"visible_columns": DATA_STEWARD_VISIBLE_FIELDS, "custom_fields": []}, "data_agreement_widget": {"visible_columns": DATA_AGREEMENT_VISIBLE_FIELDS, "custom_fields": []}}
FIELD_LABELS = {"steward_id": "Steward ID", "steward_name": "Steward Name", "steward_role": "Steward Role", "contact": "Contact", "effective_from": "Effective From", "effective_to": "Effective To", "is_active": "Is Active", "agreement_name": "Agreement Name", "domain": "Domain", "start_date": "Start Date", "expiry_date": "Expiry Date", "business_purpose": "Business Purpose", "recipient": "Recipient / Consumer", "evidence_type": "Evidence Type"}
CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
ENRICHMENT_RULES_TABLE = "METADATA_ENRICHMENT_RULES"
GUARDRAIL_RULES_TABLE = "METADATA_GUARDRAIL_RULES"
GUARDRAIL_RESULTS_TABLE = "METADATA_GUARDRAIL_RESULTS"
GUARDRAIL_TYPES = ["schema", "freshness", "profile_behavior", "dq"]
GUARDRAIL_REVIEW_STATUSES = ["draft", "pending_governance_review", "active_pending_governance_review", "self_approved", "governance_approved", "rejected_by_governance", "superseded", "inactive"]
ACTIVATION_STATES = ["active", "pending", "inactive"]
REVIEW_STATES = ["draft", "pending_governance_review", "active_pending_governance_review", "governance_approved", "rejected_by_governance", "superseded", "inactive"]
SOURCE_NOTEBOOK_TYPES = ["02_pipeline", "03_governance"]
CREATED_BY_ROLES = ["engineering", "governance", "system"]
LINEAGE_TABLE = "METADATA_DATA_LINEAGE"
DATA_ACCESS_TABLE = "METADATA_DATA_ACCESS"
DQ_RULE_TYPES = ["not_null", "null_rate_below", "non_empty_string", "unique", "unique_combination", "accepted_values", "not_in_values", "between", "greater_than", "greater_than_or_equal", "less_than", "less_than_or_equal", "regex_match", "date_not_future", "date_between", "freshness", "max_age_days", "column_pair_equal", "column_a_gte_column_b", "column_a_gt_column_b", "required_when", "value_when", "expression_true"]
SENSITIVITY_LABELS = ["classified", "restricted", "public"]
PERSONAL_DATA_CLASSIFICATIONS = ["direct PII", "indirect PII", "none"]


@dataclass
class PipelineRunContext:
    """Internal runtime context resolved for guided notebook defaults."""

    run_id: str
    pipeline_started_at: str
    pipeline_name: str
    spark_session: Any = None
    metadata_schema: str = ""
    notebook_type: str = "02_pipeline"
    agreement_id: str = ""
    agreement_version: str = ""
    agreement: dict[str, Any] = dataclass_field(default_factory=dict)
    context: dict[str, Any] | None = None
    read_only: bool = False
    source_definitions: dict[str, dict[str, Any]] = dataclass_field(default_factory=dict)
    target_definitions: dict[str, dict[str, Any]] = dataclass_field(default_factory=dict)


_ACTIVE_PIPELINE_CONTEXT: PipelineRunContext | None = None


def set_active_pipeline_context(context: PipelineRunContext) -> None:
    """Store the active pipeline runtime context for downstream helpers."""
    global _ACTIVE_PIPELINE_CONTEXT
    _ACTIVE_PIPELINE_CONTEXT = context


def pipeline_active_context() -> PipelineRunContext | None:
    """Return the active pipeline context when one has been started."""
    return _ACTIVE_PIPELINE_CONTEXT


_SELECTED_AGREEMENT: dict[str, Any] | None = None


def set_selected_agreement(row: dict[str, Any]) -> None:
    """Store the selected agreement row for private widget workflows."""
    global _SELECTED_AGREEMENT
    _SELECTED_AGREEMENT = dict(row)


def _get_selected_agreement_state() -> dict[str, Any] | None:
    """Return the selected agreement row for private widget workflows."""
    return dict(_SELECTED_AGREEMENT) if _SELECTED_AGREEMENT else None


def get_selected_agreement() -> dict[str, Any]:
    """Return the agreement selected by ``runtime context setup``."""
    selected = _get_selected_agreement_state()
    if not selected:
        raise RuntimeError("No agreement selected. Run runtime context setup(select_agreement=True) first.")
    return selected


def serialize_custom_fields(values: dict[str, Any] | None) -> str:
    """Serialize organization-specific intake values to deterministic JSON.

    Parameters
    ----------
    values : dict[str, Any] or None
        Extra values collected from configured custom fields.

    Returns
    -------
    str
        JSON object text suitable for ``custom_fields_json``.

    """
    return json.dumps(values or {}, sort_keys=True, default=to_iso_date)

def deserialize_custom_fields(custom_fields_json: Any) -> dict[str, Any]:
    """Deserialize stored custom-field JSON for widget display.

    Parameters
    ----------
    custom_fields_json : Any
        JSON object text, an existing mapping, or a blank value.

    Returns
    -------
    dict[str, Any]
        Parsed custom field values. Blank input produces an empty mapping.

    Raises
    ------
    ValueError
        If non-blank text is not a JSON object.

    """
    if custom_fields_json in (None, ""):
        return {}
    if isinstance(custom_fields_json, dict):
        return dict(custom_fields_json)
    try:
        values = json.loads(str(custom_fields_json))
    except json.JSONDecodeError as exc:
        raise ValueError("custom_fields_json must be a JSON object.") from exc
    if not isinstance(values, dict):
        raise ValueError("custom_fields_json must be a JSON object.")
    return values

def config_value(config: Any, name: str, default: Any) -> Any:
    """Return a data-agreement widget configuration value."""
    agreement_config = getattr(config, "data_agreement_config", config)
    if isinstance(agreement_config, dict):
        return agreement_config.get(name, default)
    return getattr(agreement_config, name, default)

def get_widget_visible_fields(config: Any, kind: str) -> list[str]:
    """Return configured editable columns without backend audit fields.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Environment configuration containing widget settings.
    kind : {"data_steward_widget", "data_agreement_widget"}
        Widget configuration section to inspect.

    Returns
    -------
    list[str]
        Safe editable fields. Technical audit fields are always excluded.

    """
    configured = {**WIDGET_CONFIG_DEFAULTS[kind], **dict(config_value(config, kind, {}) or {})}.get("visible_columns", [])
    hidden = set(STANDARD_RUNTIME_AUDIT_COLUMNS) | {"custom_fields_json"}
    if kind == "data_steward_widget":
        hidden.update({"steward_id", "is_active"})
    if kind == "data_agreement_widget":
        hidden.update(DATA_AGREEMENT_GENERATED_FIELDS)
    return [field for field in configured if field not in hidden]

def collect_custom_fields(config: list[dict[str, Any]] | dict[str, Any], widgets_by_key: dict[str, Any]) -> dict[str, Any]:
    """Collect and validate configured custom-field widget values.

    Parameters
    ----------
    config : list[dict[str, Any]] or dict[str, Any]
        Custom-field definitions or widget config.
    widgets_by_key : dict[str, ipywidgets.Widget]
        Rendered custom widgets keyed by configured field key.

    Returns
    -------
    dict[str, Any]
        JSON-ready custom values.

    Raises
    ------
    ValueError
        If a required configured field is blank.

    """
    definitions = config.get("custom_fields", []) if isinstance(config, dict) else config
    values: dict[str, Any] = {}
    for definition in definitions:
        key = str(definition["key"])
        value = widgets_by_key[key].value
        if isinstance(value, tuple):
            value = list(value)
        if isinstance(value, (date, datetime)):
            value = to_iso_date(value)
        if definition.get("required") and value in (None, "", []):
            raise ValueError(f"{definition.get('label', key)} is required.")
        values[key] = value
    return values

def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]:
    if rows is None:
        return []
    if hasattr(rows, "collect"):
        rows = rows.collect()
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows]

def _latest_by_key(rows: Any, key: str) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in _coerce_row_dicts(rows):
        value = str(row.get(key) or "").strip()
        if value and (value not in latest or str(row.get("_committed_at") or "") >= str(latest[value].get("_committed_at") or "")):
            latest[value] = row
    return sorted(latest.values(), key=lambda row: str(row.get(key) or "").lower())

def to_bool(value: Any) -> bool:
    """Normalize common notebook and metadata boolean representations.

    Blank values are treated as false. Any non-blank value outside the
    supported true/false spellings raises a clear validation error instead of
    relying on Python string truthiness.
    """
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"", "false", "0", "no", "n"}:
        return False
    raise ValueError(f"Unsupported boolean value: {value!r}. Use true/false, 1/0, yes/no, or y/n.")

def _audit_date(config: Any = None) -> date:
    """Return today in the configured FabricOps audit timezone."""
    return datetime.fromisoformat(get_current_audit_timestamp(config=config)).date()

def active_steward(row: dict[str, Any], config: Any = None) -> bool:
    """Return whether a steward metadata row is active on the audit date."""
    is_active = row.get("is_active")
    if is_active not in (None, "") and not to_bool(is_active):
        return False
    today = _audit_date(config)
    try:
        starts_before_today = not row.get("effective_from") or date.fromisoformat(str(row["effective_from"])[:10]) <= today
        ends_after_today = not row.get("effective_to") or date.fromisoformat(str(row["effective_to"])[:10]) >= today
        return starts_before_today and ends_after_today
    except ValueError as exc:
        raise ValueError(f"{DATA_STEWARD_TABLE} row '{row.get('steward_id', '')}' has an invalid effective date. Use ISO dates.") from exc


def list_data_stewards(config: Any, env: str, *, spark_session: Any = None, active_only: bool = True, missing_ok: bool = False, metadata_schema: str | None = None) -> list[dict[str, Any]]:
    """List latest append-only steward rows from the metadata lakehouse."""
    metadata_tables = config_value(config, "metadata_tables", {}) or {}
    try:
        rows = read_lakehouse_table_core(str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)), target="metadata", schema=metadata_schema, spark_session=spark_session, context={"config": config, "env": env})
    except Exception:
        if missing_ok:
            return []
        raise
    latest = _latest_by_key(rows, "steward_id")
    return [row for row in latest if active_steward(row, config)] if active_only else latest

def write_widget_metadata_row(*, spark: Any, config: Any, env: str, table: str, row: dict[str, Any]) -> None:
    """Append one widget metadata row to the configured metadata target."""
    write_lakehouse_table_core(spark.createDataFrame([coerce_metadata_row_types(table, row)]), table, target="metadata", schema=configured_lakehouse_schema(config, env, "metadata"), context={"config": config, "env": env}, mode="append")

def parse_iso_date(value: Any, field_name: str, *, required: bool = False) -> date | None:
    """Return a date object or raise a clear intake validation error."""
    text = str(value or "").strip()
    if not text:
        if required:
            raise ValueError(f"{field_name} is required.")
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid ISO date (YYYY-MM-DD).") from exc

def _parse_agreement_version(version: Any) -> tuple[int, int, int]:
    """Parse a semantic contract version into a comparable tuple."""
    try:
        parts = str(version or "").strip().split(".")
        return tuple(int(parts[index]) if index < len(parts) else 0 for index in range(3))  # type: ignore[return-value]
    except (TypeError, ValueError):
        return (0, 0, 0)

def _next_minor_version(version: Any) -> str:
    """Return the next minor contract version, defaulting to ``1.0.0``."""
    major, minor, _ = _parse_agreement_version(version)
    return "1.0.0" if major == 0 else f"{major}.{minor + 1}.0"

def latest_agreement_versions(rows: Any) -> list[dict[str, Any]]:
    """Return the latest semantic version for each stable agreement ID."""

    def _agreement_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
        return (
            _parse_agreement_version(row.get("agreement_version")),
            str(row.get("_committed_at") or ""),
            str(row.get("agreement_name") or ""),
            str(row.get("agreement_id") or ""),
        )

    latest: dict[str, dict[str, Any]] = {}
    for row in _coerce_row_dicts(rows):
        key = str(row.get("agreement_id") or "").strip()
        if key and (key not in latest or _agreement_sort_key(row) > _agreement_sort_key(latest[key])):
            latest[key] = row
    return sorted(latest.values(), key=lambda row: (str(row.get("agreement_name") or "").lower(), str(row.get("agreement_id") or "")))

def list_all_data_agreement_rows(config: Any, env: str, *, spark_session: Any = None, missing_ok: bool = False, metadata_schema: str | None = None) -> list[dict[str, Any]]:
    """List all append-only agreement rows from the metadata lakehouse."""
    metadata_tables = config_value(config, "metadata_tables", {}) or {}
    try:
        rows = read_lakehouse_table_core(str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)), target="metadata", schema=metadata_schema or configured_lakehouse_schema(config, env, "metadata"), context={"config": config, "env": env}, spark_session=spark_session)
    except Exception:
        if missing_ok:
            return []
        raise
    return _coerce_row_dicts(rows)

def list_data_agreements(config: Any, env: str, *, spark_session: Any = None, active_only: bool = False, missing_ok: bool = False, metadata_schema: str | None = None) -> list[dict[str, Any]]:
    """List latest versioned agreements from the configured metadata lakehouse."""
    rows = list_all_data_agreement_rows(config, env, spark_session=spark_session, missing_ok=missing_ok, metadata_schema=metadata_schema)
    agreements = latest_agreement_versions(rows)
    if not active_only:
        return agreements
    today = _audit_date(config)
    return [row for row in agreements if (not row.get("start_date") or date.fromisoformat(str(row["start_date"])[:10]) <= today) and (not row.get("expiry_date") or date.fromisoformat(str(row["expiry_date"])[:10]) >= today)]

def to_iso_date(value: Any) -> str:
    """Return a date-like widget value as an ISO string."""
    if value is None:
        return ""
    return value.date().isoformat() if isinstance(value, datetime) else value.isoformat() if isinstance(value, date) else str(value)

def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]:
    if rows_or_df is None:
        return []
    if hasattr(rows_or_df, "collect"):
        rows_or_df = rows_or_df.collect()
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows_or_df]

def _value(row: dict[str, Any], name: str, default: Any = "") -> Any:
    return row.get(name, row.get(name.upper(), default))

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
            "activation_reason": lifecycle.get("activation_reason", ""),
            "activated_by": lifecycle.get("activated_by", ""),
            "activated_at": lifecycle.get("activated_at", ""),
            "requires_governance_review": bool(lifecycle.get("requires_governance_review", False)),
            "approval_policy": lifecycle["approval_policy"],
            "governance_mode": lifecycle["governance_mode"],
            "submitted_by": resolved_actor if lifecycle.get("review_state") == "pending_governance_review" else "",
            "submitted_at": now if lifecycle.get("review_state") == "pending_governance_review" else "",
            "reviewed_by": resolved_actor if lifecycle["review_status"] in {"self_approved", "governance_approved"} else "",
            "reviewed_at": now if lifecycle["review_status"] in {"self_approved", "governance_approved"} else "",
            "review_decision": lifecycle["review_status"],
            "review_comment": str(review.get("review_comment") or ""),
            "bypass_reason": str(lifecycle.get("bypass_reason") or ""),
            "requires_post_review": bool(lifecycle["requires_post_review"]),
            "supersedes_enrichment_rule_id": str(review.get("supersedes_enrichment_rule_id") or ""),
            "effective_from": now if lifecycle["is_active"] else "",
            "effective_to": "",
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
            "rule_version": str(row.get("enrichment_rule_version") or row.get("rule_version") or row.get("_committed_at") or ""),
            "record_type": "enrichment" if row.get("enrichment_rule_id") or row.get("enrichment_type") else "guardrail",
            "rule_type": str(row.get("enrichment_type") or row.get("guardrail_type") or row.get("rule_type") or ""),
            "review_status": str(row.get("review_status") or ""),
            "is_active": bool(row.get("is_active")),
            "submitted_by": str(row.get("submitted_by") or row.get("_committed_by") or ""),
            "submitted_at": str(row.get("submitted_at") or row.get("_committed_at") or ""),
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
    committed_at = _audit_timestamp_value(config)
    actor_value = _resolve_action_by(actor)
    pending = lifecycle.get("review_state") == "pending_governance_review"
    return {"rule_key": _build_dq_rule_key(env, dataset, table, rule_id), "rule_id": rule_id, "metadata_column_key": _build_metadata_column_key(env, dataset, table, column_name) if column_name else "", "metadata_table_key": str(state.get("metadata_table_key") or _build_metadata_table_key(env, dataset, table)), "environment_name": env, "dataset_name": dataset, "table_name": table, "column_name": column_name, "guardrail_type": guardrail_type, "rule_type": rule_type, "rule_parameters_json": json.dumps(parameters or {}, sort_keys=True, default=str), "severity": severity, "description": description, "submitted_by": actor_value if pending else "", "submitted_at": committed_at if pending else "", "reviewed_by": actor_value if lifecycle.get("review_status") == "self_approved" else "", "reviewed_at": committed_at if lifecycle.get("review_status") == "self_approved" else "", "review_decision": lifecycle.get("review_status", ""), "review_comment": "", "supersedes_rule_id": "", "effective_from": committed_at if lifecycle.get("is_active") else "", "effective_to": "", "action_type": "created", "source_notebook_type": source_notebook_type, **lifecycle}

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
    matches.sort(key=lambda row: str(row.get("_committed_at") or ""), reverse=True)
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




# Governance readiness and policy helpers migrated from the retired mixed governance module.



def _is_success(row: dict[str, Any]) -> bool:
    return str(_value(row, "profile_status", "")).strip().lower() in {"success", "succeeded", "passed", "complete", "completed", "ok"}

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
    agreement_version = str(_value(first_profile, "agreement_version") or _value(first_profile, "AGREEMENT_CONTRACT_VERSION") or "")

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
        and (not agreement_version or str(_value(row, "agreement_version")) == agreement_version)
    ]
    attachment_rows = [
        row for row in _read_metadata_rows(config, env, DATA_AGREEMENT_EVIDENCE_TABLE, spark_session=spark_session)
        if agreement_id and str(_value(row, "agreement_id")) == agreement_id
        and (not agreement_version or str(_value(row, "agreement_version")) == agreement_version)
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
        "agreement_version": agreement_version,
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


# DQ authoring record helpers migrated to widget ownership.

def _canonical_dq_rule_type(rule_type: Any) -> str:
    return str(rule_type or "").strip()


def _normalize_dq_severity(severity: Any) -> str:
    value = str(severity or "warning").strip().lower()
    return "error" if value in {"blocking", "error"} else "warning"


def _dq_rule_parameter_payload(rule: dict[str, Any], columns: list[str]) -> dict[str, Any]:
    """Return rule parameters stored inside ``rule_parameters_json``."""
    metadata_fields = {
        "rule_key", "rule_id", "metadata_column_key", "metadata_table_key", "environment_name", "dataset_name",
        "table_name", "column_name", "rule_type", "rule_parameters", "rule_parameters_json", "severity",
        "description", "is_active", "review_status", "approved_by", "approved_at", "suggestion_json",
        "suggestion", "action_type", "commit", "_committed_at", "_committed_by", "_workspace_id", "_workspace_name",
        "_notebook_id", "_notebook_name", "_metadata_lakehouse_name", "_activity_id",
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
        from fabricops_kit.pipeline.guardrails_shared import _validate_dq_rules
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
