"""Shared widget rendering helpers for FabricOps notebook widgets."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime
import hashlib
import json
from typing import Any, Iterable, Mapping
import uuid

from fabricops_kit.config.shared import DEFAULT_STEWARD_ROLE_OPTIONS, get_current_audit_timestamp
from fabricops_kit.io.shared import configured_lakehouse_schema, read_lakehouse_table_core, write_lakehouse_table_core
from fabricops_kit.metadata import _audit_timestamp_value, _build_dq_rule_key, _build_metadata_column_key, _build_metadata_table_key, build_runtime_audit_fields, _resolve_action_by, coerce_metadata_row_types


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


def _render_custom_fields(config: list[dict[str, Any]] | dict[str, Any], *, values: dict[str, Any] | None = None) -> dict[str, Any]:
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


def _standard_widget(field: str, value: Any = "", *, options: list[Any] | None = None) -> Any:
    """Render a standard widget control for a configured field name."""
    widgets = require_ipywidgets()
    description = field.replace("_", " ").title()
    if options is not None:
        default_value = value if value in options else (options[0] if options else None)
        return widgets.Dropdown(options=options, value=default_value, **widget_common(widgets, description))
    if field.endswith("_date") or field in {"effective_from", "effective_to", "start_date", "expiry_date"}:
        return widgets.DatePicker(value=date.fromisoformat(str(value)[:10]) if value else None, **widget_common(widgets, description))
    if field.startswith("approved_usage_") or field == "is_active":
        return widgets.Checkbox(value=True if value == "" else str(value).strip().lower() in {"1", "true", "yes", "y"}, **widget_common(widgets, description))
    if field in {"business_purpose"}:
        return widgets.Textarea(value=str(value or ""), **widget_common(widgets, description, textarea=True))
    return widgets.Text(value=str(value or ""), **widget_common(widgets, description))



# Widget-owned helper implementations migrated from data_agreement.py and governance_review.py.
DATA_AGREEMENT_TABLE = "METADATA_DATA_AGREEMENT"
DATA_AGREEMENT_EVIDENCE_TABLE = "METADATA_DATA_AGREEMENT_EVIDENCE"
DATA_STEWARD_TABLE = "METADATA_DATA_STEWARD"
STANDARD_RUNTIME_AUDIT_COLUMNS = ["_committed_by", "_committed_at", "_notebook_name", "_workspace_name", "_metadata_lakehouse_name", "_activity_id"]
DATA_STEWARD_VISIBLE_FIELDS = ["steward_name", "steward_role", "contact", "effective_from", "effective_to"]
DATA_STEWARD_BACKEND_FIELDS = ["steward_id", *DATA_STEWARD_VISIBLE_FIELDS, "is_active"]
DATA_AGREEMENT_VISIBLE_FIELDS = ["agreement_name", "domain", "steward_id", "recipient", "start_date", "expiry_date", "business_purpose", "approved_usage_internal", "approved_usage_external", "approved_usage_research"]
DATA_AGREEMENT_GENERATED_FIELDS = ["agreement_id", "contract_version"]
DATA_STEWARD_FIELDS = DATA_STEWARD_BACKEND_FIELDS + ["custom_fields_json"] + STANDARD_RUNTIME_AUDIT_COLUMNS
DATA_AGREEMENT_FIELDS = DATA_AGREEMENT_GENERATED_FIELDS + DATA_AGREEMENT_VISIBLE_FIELDS + ["custom_fields_json"] + STANDARD_RUNTIME_AUDIT_COLUMNS
DATA_AGREEMENT_EVIDENCE_FIELDS = ["agreement_id", "contract_version", "evidence_type", "file_name", "file_path", "mime_type", "file_size", "uploaded_at", "uploaded_by", *STANDARD_RUNTIME_AUDIT_COLUMNS]
AGREEMENT_EVIDENCE_ALLOWED_EXTENSIONS = (".pdf", ".doc", ".docx", ".png", ".jpg", ".jpeg")
AGREEMENT_EVIDENCE_MIME_TYPES = {".pdf": "application/pdf", ".doc": "application/msword", ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
AGREEMENT_EVIDENCE_TYPES = ["Signed Agreement", "Email Approval", "Policy Document", "Supporting Screenshot", "Other"]
_WIDGET_CONFIG_DEFAULTS = {"data_steward_widget": {"visible_columns": DATA_STEWARD_VISIBLE_FIELDS, "custom_fields": []}, "data_agreement_widget": {"visible_columns": DATA_AGREEMENT_VISIBLE_FIELDS, "custom_fields": []}}
FIELD_LABELS = {"steward_id": "Steward ID", "steward_name": "Steward Name", "steward_role": "Steward Role", "contact": "Contact", "effective_from": "Effective From", "effective_to": "Effective To", "is_active": "Is Active", "agreement_name": "Agreement Name", "domain": "Domain", "start_date": "Start Date", "expiry_date": "Expiry Date", "business_purpose": "Business Purpose", "recipient": "Recipient / Consumer", "approved_usage_internal": "Approved Usage - Internal", "approved_usage_external": "Approved Usage - External", "approved_usage_research": "Approved Usage - Research", "evidence_type": "Evidence Type"}
CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
ENRICHMENT_RULES_TABLE = "METADATA_ENRICHMENT_RULES"
GUARDRAIL_RULES_TABLE = "METADATA_GUARDRAIL_RULES"
DQ_RULE_TYPES = ["not_null", "null_rate_below", "non_empty_string", "unique", "unique_combination", "accepted_values", "not_in_values", "between", "greater_than", "greater_than_or_equal", "less_than", "less_than_or_equal", "regex_match", "date_not_future", "date_between", "freshness", "max_age_days", "column_pair_equal", "column_a_gte_column_b", "column_a_gt_column_b", "required_when", "value_when", "expression_true"]
SENSITIVITY_LABELS = ["classified", "restricted", "public"]
PERSONAL_DATA_CLASSIFICATIONS = ["direct PII", "indirect PII", "none"]


def _serialize_custom_fields(values: dict[str, Any] | None) -> str:
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
    return json.dumps(values or {}, sort_keys=True, default=_to_iso_date)

def _deserialize_custom_fields(custom_fields_json: Any) -> dict[str, Any]:
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

def _get_widget_visible_fields(config: Any, kind: str) -> list[str]:
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
    configured = {**_WIDGET_CONFIG_DEFAULTS[kind], **dict(config_value(config, kind, {}) or {})}.get("visible_columns", [])
    hidden = set(STANDARD_RUNTIME_AUDIT_COLUMNS) | {"custom_fields_json"}
    if kind == "data_steward_widget":
        hidden.update({"steward_id", "is_active"})
    if kind == "data_agreement_widget":
        hidden.update(DATA_AGREEMENT_GENERATED_FIELDS)
    return [field for field in configured if field not in hidden]

def _collect_custom_fields(config: list[dict[str, Any]] | dict[str, Any], widgets_by_key: dict[str, Any]) -> dict[str, Any]:
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
            value = _to_iso_date(value)
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

def _to_bool(value: Any) -> bool:
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

def _active_steward(row: dict[str, Any], config: Any = None) -> bool:
    is_active = row.get("is_active")
    if is_active not in (None, "") and not _to_bool(is_active):
        return False
    today = _audit_date(config)
    try:
        starts_before_today = not row.get("effective_from") or date.fromisoformat(str(row["effective_from"])[:10]) <= today
        ends_after_today = not row.get("effective_to") or date.fromisoformat(str(row["effective_to"])[:10]) >= today
        return starts_before_today and ends_after_today
    except ValueError as exc:
        raise ValueError(f"{DATA_STEWARD_TABLE} row '{row.get('steward_id', '')}' has an invalid effective date. Use ISO dates.") from exc

def _generate_steward_id(values: dict[str, Any]) -> str:
    """Generate a stable public-safe steward identifier from business fields."""
    basis = "|".join(str(values.get(field, "")).strip().lower() for field in ("steward_name", "contact", "effective_from"))
    digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:10]
    return f"STEW-{digest}"

def _list_data_stewards(config: Any, env: str, *, spark_session: Any = None, active_only: bool = True, missing_ok: bool = False, metadata_schema: str | None = None) -> list[dict[str, Any]]:
    """List latest append-only steward rows from the metadata lakehouse.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Metadata lakehouse configuration.
    env : str
        Configured environment key.
    spark_session : pyspark.sql.SparkSession, optional
        Fabric Spark session.
    active_only : bool, default=True
        Return only currently effective active steward assignments.
    missing_ok : bool, default=False
        Return an empty list when the table is not available.
    metadata_schema : str or None, default=None
        Optional schema override for metadata table reads.

    Returns
    -------
    list[dict[str, Any]]
        Latest steward rows sorted by stable ID.

    """
    metadata_tables = config_value(config, "metadata_tables", {}) or {}
    try:
        rows = read_lakehouse_table_core(str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)), target="metadata", schema=metadata_schema, spark_session=spark_session, context={"config": config, "env": env})
    except Exception:
        if missing_ok:
            return []
        raise
    latest = _latest_by_key(rows, "steward_id")
    return [row for row in latest if _active_steward(row, config)] if active_only else latest

def write_widget_metadata_row(*, spark: Any, config: Any, env: str, table: str, row: dict[str, Any]) -> None:
    """Append one widget metadata row to the configured metadata target."""
    write_lakehouse_table_core(spark.createDataFrame([coerce_metadata_row_types(table, row)]), table, target="metadata", schema=configured_lakehouse_schema(config, env, "metadata"), context={"config": config, "env": env}, mode="append")

def _parse_iso_date(value: Any, field_name: str, *, required: bool = False) -> date | None:
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

def _create_or_update_data_steward(*, spark: Any, config: Any, env: str, values: dict[str, Any], custom_fields: dict[str, Any] | None = None, committed_by: str | None = None, committed_at: str | None = None, runtime_context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Append a created or updated steward assignment with runtime audit fields.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session.
    config : FrameworkConfig or dict
        Metadata configuration.
    env : str
        Configured environment key.
    values : dict[str, Any]
        User-facing steward values. Reusing ``steward_id`` appends an update;
        omitting it creates a backend-generated stable steward identifier.
    custom_fields : dict[str, Any], optional
        Organization-specific configured values.
    committed_by : str or None, default=None
        Optional identity recorded with the steward update.
    committed_at : str or None, default=None
        Optional timestamp recorded with the steward update.
    runtime_context : dict[str, Any] or None, default=None
        Optional runtime metadata recorded with the steward update.

    Returns
    -------
    dict[str, Any]
        Appended steward row.

    """
    row = {field: values.get(field, "") for field in DATA_STEWARD_VISIBLE_FIELDS}
    required = ["steward_name", "steward_role", "contact"]
    missing = [field for field in required if not str(row.get(field) or "").strip()]
    if missing:
        raise ValueError("Missing required steward field(s): " + ", ".join(missing))
    configured_roles = {
        str(option).strip()
        for option in (config_value(config, "steward_role_options", DEFAULT_STEWARD_ROLE_OPTIONS) or [])
        if str(option).strip()
    }
    existing_role = str(values.get("_existing_steward_role") or "").strip()
    selected_steward_id = str(values.get("steward_id") or "").strip()
    if str(row["steward_role"]).strip() not in configured_roles and not (selected_steward_id and existing_role and str(row["steward_role"]).strip() == existing_role):
        raise ValueError("steward_role must be one of the configured steward role options.")
    row["effective_from"] = _parse_iso_date(row.get("effective_from"), "effective_from")
    row["effective_to"] = _parse_iso_date(row.get("effective_to"), "effective_to")
    if row["effective_to"] and row["effective_from"] and row["effective_to"] < row["effective_from"]:
        raise ValueError("effective_to must be on or after effective_from.")
    row["steward_id"] = str(values.get("steward_id") or "").strip() or _generate_steward_id(row)
    explicit_active = values.get("is_active")
    if explicit_active not in (None, "") and not _to_bool(explicit_active):
        row["is_active"] = False
    else:
        row["is_active"] = bool(_active_steward({**row, "is_active": row.get("is_active", "")}, config))
    row["custom_fields_json"] = _serialize_custom_fields(custom_fields)
    row.update(build_runtime_audit_fields(config=config, env=env, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context))
    metadata_tables = config_value(config, "metadata_tables", {}) or {}
    write_widget_metadata_row(spark=spark, config=config, env=env, table=str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)), row=row)
    return row

def _parse_contract_version(version: Any) -> tuple[int, int, int]:
    """Parse a semantic contract version into a comparable tuple."""
    try:
        parts = str(version or "").strip().split(".")
        return tuple(int(parts[index]) if index < len(parts) else 0 for index in range(3))  # type: ignore[return-value]
    except (TypeError, ValueError):
        return (0, 0, 0)

def _next_minor_version(version: Any) -> str:
    """Return the next minor contract version, defaulting to ``1.0.0``."""
    major, minor, _ = _parse_contract_version(version)
    return "1.0.0" if major == 0 else f"{major}.{minor + 1}.0"

def latest_agreement_versions(rows: Any) -> list[dict[str, Any]]:
    """Return the latest semantic version for each stable agreement ID."""

    def _agreement_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
        return (
            _parse_contract_version(row.get("contract_version")),
            str(row.get("_committed_at") or row.get("updated_at") or row.get("uploaded_at") or ""),
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

def _generate_agreement_id(config: Any = None) -> str:
    value = datetime.fromisoformat(get_current_audit_timestamp(config=config, drop_microseconds=False))
    return "DA-" + value.strftime("%Y%m%d-%H%M%S-%f")

def _to_iso_date(value: Any) -> str:
    if value is None:
        return ""
    return value.date().isoformat() if isinstance(value, datetime) else value.isoformat() if isinstance(value, date) else str(value)

def _business_agreement_snapshot(row: dict[str, Any]) -> dict[str, Any]:
    """Return user-facing agreement values used to detect business changes."""
    snapshot = {field: row.get(field, "") for field in DATA_AGREEMENT_VISIBLE_FIELDS}
    snapshot["custom_fields_json"] = _serialize_custom_fields(_deserialize_custom_fields(row.get("custom_fields_json", "")))
    return snapshot

def _create_or_update_data_agreement(*, spark: Any, config: Any, env: str, values: dict[str, Any], selected_agreement: dict[str, Any] | None = None, custom_fields: dict[str, Any] | None = None, committed_by: str | None = None, committed_at: str | None = None, runtime_context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Append a new agreement or a new semantic version of an existing one.

    Reusing ``selected_agreement`` preserves its stable ``agreement_id`` and
    increments from the latest stored version. Runtime audit fields remain
    backend-managed.
    """
    row = {field: values.get(field, "") for field in DATA_AGREEMENT_VISIBLE_FIELDS}
    existing_rows = list_all_data_agreement_rows(config, env, spark_session=spark, missing_ok=True)
    selected_id = str((selected_agreement or {}).get("agreement_id") or "").strip()
    if selected_id:
        same_agreement = [item for item in existing_rows if str(item.get("agreement_id") or "").strip() == selected_id]
        latest = max(same_agreement, key=lambda item: _parse_contract_version(item.get("contract_version")), default=selected_agreement)
        row["agreement_id"] = selected_id
        row["contract_version"] = _next_minor_version(latest.get("contract_version"))
    else:
        latest = None
        row["agreement_id"] = str(row.get("agreement_id") or "").strip() or _generate_agreement_id(config)
        row["contract_version"] = str(row.get("contract_version") or "1.0.0").strip()
    required = ["agreement_id", "contract_version", "agreement_name", "domain", "steward_id", "recipient", "start_date", "expiry_date", "business_purpose"]
    missing = [field for field in required if not str(row.get(field) or "").strip()]
    if missing:
        raise ValueError("Missing required agreement field(s): " + ", ".join(missing))
    usage_fields = ["approved_usage_internal", "approved_usage_external", "approved_usage_research"]
    if not any(str(row.get(field) or "").strip() for field in usage_fields):
        raise ValueError("At least one approved usage field is required: internal, external, or research.")
    row["start_date"] = _parse_iso_date(row.get("start_date"), "start_date", required=True)
    row["expiry_date"] = _parse_iso_date(row.get("expiry_date"), "expiry_date", required=True)
    if row["expiry_date"] < row["start_date"]:
        raise ValueError("expiry_date must be on or after start_date.")
    active_steward_ids = {str(item["steward_id"]) for item in _list_data_stewards(config, env, spark_session=spark, active_only=True)}
    if str(row["steward_id"]) not in active_steward_ids:
        raise ValueError("steward_id must reference an active data steward.")
    row["custom_fields_json"] = _serialize_custom_fields(custom_fields)
    if latest is not None:
        new_snapshot = _business_agreement_snapshot(row)
        latest_snapshot = _business_agreement_snapshot(latest)
        if new_snapshot == latest_snapshot:
            return {**latest, "_fabricops_no_change": True, "_fabricops_message": "No changes detected. Nothing was appended."}
    if any(str(item.get("agreement_id") or "").strip() == row["agreement_id"] and str(item.get("contract_version") or "").strip() == row["contract_version"] for item in existing_rows):
        raise ValueError(f"Agreement {row['agreement_id']} version {row['contract_version']} already exists. Select the existing agreement to create the next version, or create a new agreement.")
    row.update(build_runtime_audit_fields(config=config, env=env, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context))
    metadata_tables = config_value(config, "metadata_tables", {}) or {}
    write_widget_metadata_row(spark=spark, config=config, env=env, table=str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)), row=row)
    return row

def _agreement_identity_text(row: dict[str, Any] | None) -> str:
    """Return read-only agreement version context for the notebook form."""
    if not row:
        return "Agreement ID and version are generated when saved."
    current_version = str(row.get("contract_version") or "")
    return (
        f"Agreement ID: {row.get('agreement_id', '')}<br>"
        f"Current version: {current_version}<br>"
        f"Next version on save: {_next_minor_version(current_version)}<br>"
        "Saving this change will append a new version. Existing rows will not be overwritten."
    )

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


# Widget workflow implementations migrated from data_agreement.py.
def render_maintenance_widget_shared_workflow(*, spark: Any, config: Any, env: str, kind: str, display_widget: bool = True) -> dict[str, Any]:
    """Render the shared steward or data-agreement maintenance widget workflow."""
    widgets = require_ipywidgets()
    from IPython import display as ip

    is_steward = kind == "data_steward_widget"
    prompt = "Create new steward" if is_steward else "Create new agreement"
    widget_config = {**_WIDGET_CONFIG_DEFAULTS[kind], **dict(config_value(config, kind, {}) or {})}
    fields = _get_widget_visible_fields(config, kind)
    after_save_callbacks: list[Any] = []
    row_lookup: dict[str, dict[str, Any]] = {}

    def _row_id(row: dict[str, Any]) -> str:
        return str(row.get("steward_id" if is_steward else "agreement_id") or "").strip()

    def _existing_rows() -> list[dict[str, Any]]:
        return _list_data_stewards(config, env, spark_session=spark, active_only=False, missing_ok=True) if is_steward else list_data_agreements(config, env, spark_session=spark, missing_ok=True)

    def _existing_rows_for_selector() -> list[dict[str, Any]]:
        rows = _existing_rows()
        return [row for row in rows if _row_id(row)]

    def _refresh_lookup(rows: list[dict[str, Any]]) -> None:
        row_lookup.clear()
        row_lookup.update({_row_id(row): row for row in rows if _row_id(row)})

    def _steward_label(row: dict[str, Any]) -> str:
        parts = [str(row.get(field) or "").strip() for field in ("steward_name", "steward_role", "contact")]
        return " | ".join(part for part in parts if part) or str(row.get("steward_id") or "Unnamed steward")

    def _agreement_label(row: dict[str, Any]) -> str:
        row_id = _row_id(row)
        return f"{row.get('agreement_name', '') or row_id} ({row_id} / v{row.get('contract_version', '')})"

    existing_rows = _existing_rows_for_selector()
    _refresh_lookup(existing_rows)
    selected_selector = render_searchable_selector(
        widgets=widgets,
        label="Create / update",
        rows=existing_rows,
        label_fn=_steward_label if is_steward else _agreement_label,
        value_fn=_row_id,
        placeholder="Search stewards..." if is_steward else "Search agreements...",
        search_fields=["steward_name", "steward_role", "contact", "steward_id"] if is_steward else ["agreement_name", "agreement_id", "contract_version", "domain", "recipient"],
        context_fields=[
            ("steward_name", "Steward name"), ("steward_role", "Role"), ("contact", "Contact"), ("steward_id", "Steward ID"),
        ] if is_steward else [
            ("agreement_name", "Agreement name"), ("agreement_id", "Agreement ID"), ("contract_version", "Current version"), ("recipient", "Recipient"),
        ],
        empty_label=prompt,
    )
    selected = selected_selector["selector"]
    identity_context = None if is_steward else widgets.HTML(value=_agreement_identity_text(None))

    roles = [str(option).strip() for option in (config_value(config, "steward_role_options", DEFAULT_STEWARD_ROLE_OPTIONS) or []) if str(option).strip()]
    steward_role_options = [(role, role) for role in roles] if is_steward else None
    form = {}
    steward_field_selector = None
    for field in fields:
        if field == "steward_id" and not is_steward:
            steward_rows = _list_data_stewards(config, env, spark_session=spark, active_only=True, missing_ok=True)
            steward_field_selector = render_searchable_selector(
                widgets=widgets,
                label=FIELD_LABELS.get(field, field.replace("_", " ").title()),
                rows=steward_rows,
                label_fn=_steward_label,
                value_fn=lambda row: str(row.get("steward_id") or "").strip(),
                placeholder="Search stewards...",
                search_fields=["steward_name", "steward_role", "contact", "steward_id"],
                context_fields=[("steward_name", "Steward name"), ("steward_role", "Role"), ("contact", "Contact"), ("steward_id", "Steward ID")],
            )
            form[field] = steward_field_selector["selector"]
        else:
            form[field] = _standard_widget(
                field,
                options=steward_role_options if field == "steward_role" else None,
            )
    custom = _render_custom_fields(widget_config)

    def _refresh_existing_options(selected_id: str | None = None) -> None:
        rows = _existing_rows_for_selector()
        _refresh_lookup(rows)
        selected.refresh_rows(rows, selected_id if selected_id in row_lookup else "")

    def _refresh_steward_dropdown(selected_id: str | None = None) -> None:
        if "steward_id" in form:
            current = selected_id or form["steward_id"].value
            rows = _list_data_stewards(config, env, spark_session=spark, active_only=True, missing_ok=True)
            form["steward_id"].refresh_rows(rows, str(current or ""))

    refresh_stewards = None if is_steward else widgets.Button(description="Refresh active stewards")
    if refresh_stewards is not None:
        refresh_stewards.on_click(lambda _: _refresh_steward_dropdown())
    save = widgets.Button(description="Save")
    output = widgets.Output()

    def _apply_widget_value(widget: Any, value: Any) -> None:
        select_value = getattr(widget, "select_value", None)
        if callable(select_value):
            select_value(str(value or ""))
            return
        current = getattr(widget, "value", None)
        if isinstance(current, tuple):
            widget.value = tuple(value or ())
        elif isinstance(current, bool):
            widget.value = _to_bool(value)
        else:
            options = list(getattr(widget, "options", []) or [])
            option_values = [option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in options]
            widget.value = value if not option_values or value in option_values else option_values[0]

    def _populate(change: dict[str, Any]) -> None:
        row_id = change.get("new")
        row = row_lookup.get(row_id, {}) if row_id else {}
        for field, widget in form.items():
            value = row.get(field, "")
            if field == "steward_role" and value:
                option_values = [option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in list(getattr(widget, "options", []))]
                if value not in option_values:
                    widget.options = [*list(getattr(widget, "options", [])), (str(value), str(value))]
            if field in {"effective_from", "effective_to", "start_date", "expiry_date"}:
                value = date.fromisoformat(str(value)[:10]) if value else None
            _apply_widget_value(widget, value)
        stored = _deserialize_custom_fields(row.get("custom_fields_json", ""))
        for key, widget in custom.items():
            _apply_widget_value(widget, stored.get(key, widget.value))
        if identity_context is not None:
            identity_context.value = _agreement_identity_text(row if row else None)

    selected.observe(_populate, names="value")
    # Keep lightweight test stubs and custom notebooks that call the first
    # registered callback exercising the population path; real ipywidgets still
    # receives the same observers.
    callbacks = getattr(selected, "callbacks", None)
    if isinstance(callbacks, list) and callbacks:
        callbacks.insert(0, callbacks.pop())

    def _clear_output() -> None:
        clear = getattr(output, "clear_output", None)
        if clear is not None:
            clear(wait=True)

    def _save(_: Any) -> None:
        save.disabled = True
        _clear_output()
        with output:
            try:
                values = {
                    key: _to_iso_date(widget.value) if key in {"effective_from", "effective_to", "start_date", "expiry_date"} else widget.value
                    for key, widget in form.items()
                }
                extras = _collect_custom_fields(widget_config, custom)
                if is_steward:
                    if selected.value:
                        values["steward_id"] = selected.value
                        values["_existing_steward_role"] = row_lookup.get(selected.value, {}).get("steward_role", "")
                    row = _create_or_update_data_steward(spark=spark, config=config, env=env, values=values, custom_fields=extras)
                    _refresh_existing_options(row["steward_id"])
                    for callback in after_save_callbacks:
                        callback(row)
                    print(f"Saved data steward: {row.get('steward_name', '')} ({row['steward_id']})")
                else:
                    selected_row = row_lookup.get(selected.value) if selected.value else None
                    row = _create_or_update_data_agreement(spark=spark, config=config, env=env, values=values, selected_agreement=selected_row, custom_fields=extras)
                    if row.get("_fabricops_no_change"):
                        print(row.get("_fabricops_message", "No changes detected. Nothing was appended."))
                    else:
                        print(f"Saved data agreement: {row.get('agreement_name', '')} ({row['agreement_id']} v{row['contract_version']})")
                    _refresh_existing_options(row["agreement_id"])
                    if not row.get("_fabricops_no_change"):
                        for callback in after_save_callbacks:
                            callback(row)
                    if identity_context is not None:
                        identity_context.value = _agreement_identity_text(row)
            except Exception as exc:
                print(f"Error: {exc}")
            finally:
                save.disabled = False

    save.on_click(_save)
    controls = [selected_selector["container"]]
    if identity_context is not None:
        controls.append(identity_context)
    for field in fields:
        if field == "steward_id" and steward_field_selector is not None:
            controls.append(steward_field_selector["container"])
        else:
            controls.append(form[field])
    controls.extend([*custom.values()])
    if refresh_stewards is not None:
        controls.append(refresh_stewards)
    container = widgets.VBox([*controls, save, output])
    if display_widget:
        ip.display(container)
    return {
        "container": container,
        "existing_record": selected,
        "existing_record_search": selected_selector["search"],
        "existing_record_context": selected_selector["context"],
        "existing_records_by_id": row_lookup,
        "identity_context": identity_context,
        "fields": form,
        "custom_fields": custom,
        "refresh_stewards_button": refresh_stewards,
        "refresh_existing_options": _refresh_existing_options,
        "refresh_steward_options": _refresh_steward_dropdown,
        "after_save_callbacks": after_save_callbacks,
        "save_button": save,
        "output": output,
    }
