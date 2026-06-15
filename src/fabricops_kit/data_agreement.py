"""Lightweight, config-driven steward and data-agreement intake for Fabric notebooks.

The ``00_env_config`` notebook prepares steward, agreement, and evidence
metadata tables plus widget configuration. The ``01_agreement`` notebook renders
standalone steward, agreement, and optional evidence widgets. Intake tables
are append-only and use framework-managed runtime audit columns.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, timezone
import hashlib
import json
import re
import sys
from typing import Any

from .config import DEFAULT_STEWARD_ROLE_OPTIONS
from .fabric_input_output import _configured_lakehouse_schema, read_lakehouse_table, write_lakehouse_table
from .metadata import _build_runtime_audit_fields, _current_notebook_active_registrations, _register_current_notebook

DATA_AGREEMENT_TABLE = "METADATA_DATA_AGREEMENT"
DATA_AGREEMENT_EVIDENCE_TABLE = "METADATA_DATA_AGREEMENT_EVIDENCE"
DATA_STEWARD_TABLE = "METADATA_DATA_STEWARD"
_SELECTED_AGREEMENT: dict[str, Any] | None = None
STANDARD_RUNTIME_AUDIT_COLUMNS = [
    "_committed_by", "_committed_at", "_notebook_name", "_workspace_name",
    "_metadata_lakehouse_name", "_activity_id",
]
DATA_STEWARD_VISIBLE_FIELDS = [
    "steward_name", "steward_role", "contact", "effective_from", "effective_to",
]
DATA_STEWARD_BACKEND_FIELDS = ["steward_id", *DATA_STEWARD_VISIBLE_FIELDS, "is_active"]
DATA_AGREEMENT_VISIBLE_FIELDS = [
    "agreement_name", "domain", "steward_id", "recipient", "start_date", "expiry_date",
    "business_purpose", "approved_usage_internal", "approved_usage_external",
    "approved_usage_research",
]
DATA_AGREEMENT_GENERATED_FIELDS = ["agreement_id", "contract_version"]
DATA_STEWARD_FIELDS = DATA_STEWARD_BACKEND_FIELDS + ["custom_fields_json"] + STANDARD_RUNTIME_AUDIT_COLUMNS
DATA_AGREEMENT_FIELDS = DATA_AGREEMENT_GENERATED_FIELDS + DATA_AGREEMENT_VISIBLE_FIELDS + ["custom_fields_json"] + STANDARD_RUNTIME_AUDIT_COLUMNS
DATA_AGREEMENT_EVIDENCE_FIELDS = [
    "agreement_id", "contract_version", "evidence_type", "file_name", "file_path",
    "mime_type", "file_size", "uploaded_at", "uploaded_by",
    *STANDARD_RUNTIME_AUDIT_COLUMNS,
]
AGREEMENT_EVIDENCE_ALLOWED_EXTENSIONS = (".pdf", ".doc", ".docx", ".png", ".jpg", ".jpeg")
AGREEMENT_EVIDENCE_MIME_TYPES = {
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}
AGREEMENT_EVIDENCE_TYPES = [
    "Signed Agreement", "Email Approval", "Policy Document",
    "Supporting Screenshot", "Other",
]


def _require_ipywidgets():
    """Return ipywidgets or raise an actionable optional-dependency error."""
    try:
        import ipywidgets as widgets
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "The data agreement widget feature requires the 'dq-review' extra. "
            'Install with: pip install "fabricops-kit[dq-review]"'
        ) from exc
    return widgets

FIELD_LABELS = {
    "steward_id": "Steward ID",
    "steward_name": "Steward Name",
    "steward_role": "Steward Role",
    "contact": "Contact",
    "effective_from": "Effective From",
    "effective_to": "Effective To",
    "is_active": "Is Active",
    "agreement_name": "Agreement Name",
    "domain": "Domain",
    "start_date": "Start Date",
    "expiry_date": "Expiry Date",
    "business_purpose": "Business Purpose",
    "recipient": "Recipient / Consumer",
    "approved_usage_internal": "Approved Usage - Internal",
    "approved_usage_external": "Approved Usage - External",
    "approved_usage_research": "Approved Usage - Research",
    "evidence_type": "Evidence Type",
}
_WIDGET_STYLE = {"description_width": "150px"}
_WIDGET_LAYOUT_WIDTH = "600px"
_TEXTAREA_HEIGHT = "80px"
_WIDGET_CONFIG_DEFAULTS = {
    "data_steward_widget": {"visible_columns": DATA_STEWARD_VISIBLE_FIELDS, "custom_fields": []},
    "data_agreement_widget": {"visible_columns": DATA_AGREEMENT_VISIBLE_FIELDS, "custom_fields": []},
}


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


def _config_value(config: Any, name: str, default: Any) -> Any:
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
    configured = {**_WIDGET_CONFIG_DEFAULTS[kind], **dict(_config_value(config, kind, {}) or {})}.get("visible_columns", [])
    hidden = set(STANDARD_RUNTIME_AUDIT_COLUMNS) | {"custom_fields_json"}
    if kind == "data_steward_widget":
        hidden.update({"steward_id", "is_active"})
    if kind == "data_agreement_widget":
        hidden.update(DATA_AGREEMENT_GENERATED_FIELDS)
    return [field for field in configured if field not in hidden]


def _widget_common(widgets_module: Any, description: str, *, textarea: bool = False) -> dict[str, Any]:
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


def _render_searchable_selector(
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
    """Render a table-backed selector with search and stable-value tracking.

    The visible label may be friendly and long, while the selection value remains
    the stable key produced by ``value_fn``. The returned ``selector`` is the
    select control used by persistence code, and its ``value`` is never replaced
    with the display label.
    """
    search = widgets.Text(value="", placeholder=placeholder, **_widget_common(widgets, f"Search {label}"))
    selector = widgets.Select(options=[], **_widget_common(widgets, label))
    context = widgets.HTML(value="")
    lookup: dict[str, dict[str, Any]] = {}
    indexed_rows: list[dict[str, Any]] = []

    def _set_rows(new_rows: list[dict[str, Any]]) -> None:
        lookup.clear()
        indexed_rows.clear()
        for row in new_rows:
            value = str(value_fn(row) or "").strip()
            if not value:
                continue
            display_label = str(label_fn(row) or value)
            lookup[value] = row
            indexed_rows.append({
                "row": row,
                "label": display_label,
                "value": value,
                "search": " ".join(
                    [display_label, value, *(str(row.get(field) or "") for field in (search_fields or sorted(str(key) for key in row)))]
                ).casefold(),
            })

    def _matching_options(query: str) -> list[tuple[str, str]]:
        needle = str(query or "").casefold().strip()
        matches = [item for item in indexed_rows if not needle or needle in item["search"]]
        return [(item["label"], item["value"]) for item in matches[:max_results]]

    def _render_context(value: Any) -> None:
        row = lookup.get(str(value or ""))
        context.value = "<br>".join(
            f"<b>{_html_escape(field_label)}:</b> {_html_escape(row.get(field, ''))}"
            for field, field_label in context_fields
        ) if row and context_fields else ("<em>No record selected.</em>" if context_fields else "")

    def _apply_filter(preferred_value: Any = None) -> None:
        current = str(preferred_value if preferred_value is not None else selector.value or "")
        options = _matching_options(search.value)
        if empty_label is not None:
            options = [(empty_label, ""), *options]
        selector.options = options
        values = [option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in options]
        if current and current in lookup and current not in values and not str(search.value or "").strip():
            row = lookup[current]
            options = [(str(label_fn(row) or current), current), *options]
            values = [option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in options]
        non_empty_values = [value for value in values if value]
        if current in values and (current or not str(search.value or "").strip()):
            selector.value = current
        elif non_empty_values:
            selector.value = non_empty_values[0]
        elif values:
            selector.value = values[0]
        else:
            selector.value = None
        _render_context(selector.value)

    def _on_search(change: dict[str, Any]) -> None:
        if change.get("name") == "value":
            _apply_filter(selector.value)

    def _on_select(change: dict[str, Any]) -> None:
        if change.get("name") == "value":
            _render_context(change.get("new"))

    def _refresh_rows(new_rows: list[dict[str, Any]], selected: str | None = None) -> None:
        _set_rows(new_rows)
        _apply_filter(selected)

    def _select_value(value: str | None) -> None:
        _apply_filter(str(value or ""))

    search.observe(_on_search, names="value")
    selector.observe(_on_select, names="value")
    _refresh_rows(rows, selected_value)
    container = widgets.VBox([search, selector, context])
    selector.search_box = search
    selector.context_html = context
    selector.refresh_rows = _refresh_rows
    selector.select_value = _select_value
    selector.rows_by_value = lookup
    return {
        "container": container,
        "search": search,
        "selector": selector,
        "context": context,
        "rows_by_value": lookup,
        "refresh_rows": _refresh_rows,
    }

def _render_custom_fields(config: list[dict[str, Any]] | dict[str, Any], *, values: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create widgets for configured organization-specific fields.

    Parameters
    ----------
    config : list[dict[str, Any]] or dict[str, Any]
        Custom-field definitions or a widget config containing ``custom_fields``.
    values : dict[str, Any], optional
        Previously stored values used to prefill update forms.

    Returns
    -------
    dict[str, ipywidgets.Widget]
        Widgets keyed by custom-field key.

    Notes
    -----
    Supported field types are ``text``, ``textarea``, ``select``,
    ``multiselect``, ``date``, and ``boolean``.

    """
    widgets = _require_ipywidgets()

    definitions = config.get("custom_fields", []) if isinstance(config, dict) else config
    current = values or {}
    rendered: dict[str, Any] = {}
    for definition in definitions:
        key = str(definition["key"])
        field_type = str(definition.get("type", "text")).lower()
        label = str(definition.get("label", FIELD_LABELS.get(key, key.replace("_", " ").title())))
        common = _widget_common(widgets, label, textarea=field_type == "textarea")
        value = current.get(key)
        if field_type == "textarea":
            widget = widgets.Textarea(value=str(value or ""), **common)
        elif field_type == "select":
            options = list(definition.get("options", []))
            option_values = [option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in options]
            default_value = value if value in option_values else option_values[0] if option_values else None
            widget = widgets.Dropdown(options=options, value=default_value, **common)
        elif field_type == "multiselect":
            widget = widgets.SelectMultiple(options=list(definition.get("options", [])), value=tuple(value or ()), **common)
        elif field_type == "date":
            widget = widgets.DatePicker(value=date.fromisoformat(str(value)[:10]) if value else None, **common)
        elif field_type == "boolean":
            widget = widgets.Checkbox(value=_to_bool(value), **common)
        elif field_type == "text":
            widget = widgets.Text(value=str(value or ""), **common)
        else:
            raise ValueError(f"Unsupported custom field type: {field_type}")
        rendered[key] = widget
    return rendered


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


def _active_steward(row: dict[str, Any]) -> bool:
    is_active = row.get("is_active")
    if is_active not in (None, "") and not _to_bool(is_active):
        return False
    today = datetime.now(timezone.utc).date()
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


def _list_data_stewards(config: Any, env_name: str, *, spark_session: Any = None, active_only: bool = True, missing_ok: bool = False, metadata_schema: str | None = None) -> list[dict[str, Any]]:
    """List latest append-only steward rows from the metadata lakehouse.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Metadata lakehouse configuration.
    env_name : str
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
    metadata_tables = _config_value(config, "metadata_tables", {}) or {}
    try:
        rows = read_lakehouse_table(config, env_name, "metadata", str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)), schema=metadata_schema, spark_session=spark_session)
    except Exception:
        if missing_ok:
            return []
        raise
    latest = _latest_by_key(rows, "steward_id")
    return [row for row in latest if _active_steward(row)] if active_only else latest


def _write_row(*, spark: Any, config: Any, env_name: str, table: str, row: dict[str, Any]) -> None:
    write_lakehouse_table(spark.createDataFrame([row]), config, env_name, "metadata", table, schema=_configured_lakehouse_schema(config, env_name, "metadata"), mode="append")


def _parse_iso_date(value: Any, field_name: str, *, required: bool = False) -> str:
    """Return an ISO date string or raise a clear intake validation error."""
    text = str(value or "").strip()
    if not text:
        if required:
            raise ValueError(f"{field_name} is required.")
        return ""
    try:
        return date.fromisoformat(text[:10]).isoformat()
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid ISO date (YYYY-MM-DD).") from exc


def _create_or_update_data_steward(*, spark: Any, config: Any, env_name: str, values: dict[str, Any], custom_fields: dict[str, Any] | None = None, committed_by: str | None = None, committed_at: str | None = None, runtime_context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Append a created or updated steward assignment with runtime audit fields.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session.
    config : FrameworkConfig or dict
        Metadata configuration.
    env_name : str
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
        for option in (_config_value(config, "steward_role_options", DEFAULT_STEWARD_ROLE_OPTIONS) or [])
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
        row["is_active"] = "false"
    else:
        row["is_active"] = "true" if _active_steward({**row, "is_active": row.get("is_active", "")}) else "false"
    row["custom_fields_json"] = _serialize_custom_fields(custom_fields)
    row.update(_build_runtime_audit_fields(config=config, env=env_name, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context))
    metadata_tables = _config_value(config, "metadata_tables", {}) or {}
    _write_row(spark=spark, config=config, env_name=env_name, table=str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)), row=row)
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


def _latest_agreement_versions(rows: Any) -> list[dict[str, Any]]:
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


def _list_all_data_agreement_rows(config: Any, env_name: str, *, spark_session: Any = None, missing_ok: bool = False, metadata_schema: str | None = None) -> list[dict[str, Any]]:
    """List all append-only agreement rows from the metadata lakehouse."""
    metadata_tables = _config_value(config, "metadata_tables", {}) or {}
    try:
        rows = read_lakehouse_table(config, env_name, "metadata", str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)), schema=metadata_schema or _configured_lakehouse_schema(config, env_name, "metadata"), spark_session=spark_session)
    except Exception:
        if missing_ok:
            return []
        raise
    return _coerce_row_dicts(rows)


def _list_data_agreements(config: Any, env_name: str, *, spark_session: Any = None, active_only: bool = False, missing_ok: bool = False, metadata_schema: str | None = None) -> list[dict[str, Any]]:
    """List latest versioned agreements from the configured metadata lakehouse."""
    rows = _list_all_data_agreement_rows(config, env_name, spark_session=spark_session, missing_ok=missing_ok, metadata_schema=metadata_schema)
    agreements = _latest_agreement_versions(rows)
    if not active_only:
        return agreements
    today = datetime.now(timezone.utc).date()
    return [row for row in agreements if (not row.get("start_date") or date.fromisoformat(str(row["start_date"])[:10]) <= today) and (not row.get("expiry_date") or date.fromisoformat(str(row["expiry_date"])[:10]) >= today)]


def _generate_agreement_id() -> str:
    return "DA-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")


def _to_iso_date(value: Any) -> str:
    if value is None:
        return ""
    return value.date().isoformat() if isinstance(value, datetime) else value.isoformat() if isinstance(value, date) else str(value)


def _business_agreement_snapshot(row: dict[str, Any]) -> dict[str, Any]:
    """Return user-facing agreement values used to detect business changes."""
    snapshot = {field: row.get(field, "") for field in DATA_AGREEMENT_VISIBLE_FIELDS}
    snapshot["custom_fields_json"] = _serialize_custom_fields(_deserialize_custom_fields(row.get("custom_fields_json", "")))
    return snapshot


def _create_or_update_data_agreement(*, spark: Any, config: Any, env_name: str, values: dict[str, Any], selected_agreement: dict[str, Any] | None = None, custom_fields: dict[str, Any] | None = None, committed_by: str | None = None, committed_at: str | None = None, runtime_context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Append a new agreement or a new semantic version of an existing one.

    Reusing ``selected_agreement`` preserves its stable ``agreement_id`` and
    increments from the latest stored version. Runtime audit fields remain
    backend-managed.
    """
    row = {field: values.get(field, "") for field in DATA_AGREEMENT_VISIBLE_FIELDS}
    existing_rows = _list_all_data_agreement_rows(config, env_name, spark_session=spark, missing_ok=True)
    selected_id = str((selected_agreement or {}).get("agreement_id") or "").strip()
    if selected_id:
        same_agreement = [item for item in existing_rows if str(item.get("agreement_id") or "").strip() == selected_id]
        latest = max(same_agreement, key=lambda item: _parse_contract_version(item.get("contract_version")), default=selected_agreement)
        row["agreement_id"] = selected_id
        row["contract_version"] = _next_minor_version(latest.get("contract_version"))
    else:
        latest = None
        row["agreement_id"] = str(row.get("agreement_id") or "").strip() or _generate_agreement_id()
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
    active_steward_ids = {str(item["steward_id"]) for item in _list_data_stewards(config, env_name, spark_session=spark, active_only=True)}
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
    row.update(_build_runtime_audit_fields(config=config, env=env_name, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context))
    metadata_tables = _config_value(config, "metadata_tables", {}) or {}
    _write_row(spark=spark, config=config, env_name=env_name, table=str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)), row=row)
    return row


def _get_notebookutils() -> Any:
    """Return a notebookutils-like object when the Fabric runtime exposes one."""
    candidate = globals().get("notebookutils")
    if candidate is not None:
        return candidate
    for module_name in ("notebookutils", "mssparkutils"):
        candidate = sys.modules.get(module_name)
        if candidate is not None:
            return candidate
    return None


def _prepare_evidence_file_references(paths_value: Any) -> list[dict[str, str]]:
    """Parse and validate manually supplied evidence file paths before writes."""
    utils = _get_notebookutils()
    fs = getattr(utils, "fs", None) if utils is not None else None
    exists = getattr(fs, "exists", None) if fs is not None else None
    list_dir = getattr(fs, "ls", None) if fs is not None else None

    references: list[dict[str, str]] = []
    for raw_line in str(paths_value or "").splitlines():
        path = re.sub(r"^(?:[-*]\s*|\d+\.\s*)", "", raw_line.strip()).strip()
        if not path:
            continue
        if not path.startswith("Files/"):
            raise ValueError(f"Evidence file path must start with Files/: {path}")

        file_name = path.replace("\\", "/").rsplit("/", 1)[-1].strip()
        if not file_name:
            raise ValueError(f"Evidence file path must include a file name: {path}")
        suffix = "." + file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
        if suffix not in AGREEMENT_EVIDENCE_ALLOWED_EXTENSIONS:
            allowed = ", ".join(AGREEMENT_EVIDENCE_ALLOWED_EXTENSIONS)
            raise ValueError(f"Unsupported evidence file type for {path}. Allowed types: {allowed}.")
        if callable(exists) and not bool(exists(path)):
            raise ValueError(f"Evidence file path does not exist: {path}")

        file_size = ""
        if callable(list_dir):
            normalized = path.rstrip("/")
            parent = normalized.rsplit("/", 1)[0] if "/" in normalized else ""
            try:
                items = list_dir(parent)
            except Exception:
                items = []
            for item in items:
                item_path = str(getattr(item, "path", "") or getattr(item, "name", "") or "")
                item_name = item_path.rstrip("/").rsplit("/", 1)[-1]
                if item_path.rstrip("/") == normalized or item_name == file_name:
                    size = getattr(item, "size", "")
                    file_size = "" if size is None else str(size)
                    break

        references.append({
            "file_name": file_name,
            "file_path": path,
            "mime_type": AGREEMENT_EVIDENCE_MIME_TYPES.get(suffix, ""),
            "file_size": file_size,
        })

    if not references:
        raise ValueError("Paste at least one evidence file path before saving.")
    return references

def _save_agreement_evidence_records(*, spark: Any, config: Any, env_name: str, agreement_id: str, contract_version: str, evidence_type: str, evidence_file_paths: Any, committed_by: str | None = None, committed_at: str | None = None, runtime_context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Append manually uploaded evidence file-reference metadata rows."""
    agreement_id = str(agreement_id or "").strip()
    contract_version = str(contract_version or "").strip()
    if not agreement_id:
        raise ValueError("agreement_id is required before saving agreement evidence.")
    if not contract_version:
        raise ValueError("contract_version is required before saving agreement evidence.")
    evidence_type = str(evidence_type or "Other").strip() or "Other"
    file_references = _prepare_evidence_file_references(evidence_file_paths)
    audit = _build_runtime_audit_fields(config=config, env=env_name, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context)
    uploaded_at = audit.get("_committed_at") or _current_audit_timestamp(config=config, drop_microseconds=False)
    uploaded_by = audit.get("_committed_by") or ""

    metadata_tables = _config_value(config, "metadata_tables", {}) or {}
    rows: list[dict[str, Any]] = []
    for reference in file_references:
        row = {
            "agreement_id": agreement_id,
            "contract_version": contract_version,
            "evidence_type": evidence_type,
            "file_name": reference["file_name"],
            "file_path": reference["file_path"],
            "mime_type": reference["mime_type"],
            "file_size": reference["file_size"],
            "uploaded_at": uploaded_at,
            "uploaded_by": uploaded_by,
            **audit,
        }
        _write_row(spark=spark, config=config, env_name=env_name, table=str(metadata_tables.get("data_agreement_evidence", DATA_AGREEMENT_EVIDENCE_TABLE)), row=row)
        rows.append(row)
    return rows


def widget_select_agreement(agreement_rows_or_config: Any, env_name: str | None = None, *, spark_session: Any = None, metadata_schema: str | None = None, register_notebook: bool = False, notebook_type: str | None = None, environment_name: str | None = None, dataset_name: str | None = None, table_name: str | None = None, topic: str | None = None, pipeline_name: str | None = None) -> Any:
    """Render a downstream agreement selector and retain the selected row.

    Parameters
    ----------
    agreement_rows_or_config : FrameworkConfig or iterable
        Pass ``CONFIG`` in normal notebooks, or provide preloaded agreement
        rows when the caller already has them available.
    env_name : str, optional
        Environment key used to load agreements when ``CONFIG`` is supplied.
    spark_session : pyspark.sql.SparkSession, optional
        Fabric Spark session used for configured metadata-table reads.
    metadata_schema : str, optional
        Explicit metadata Lakehouse schema override. Pass ``METADATA_SCHEMA``
        from ``00_env_config`` in schema-enabled Lakehouses so agreement reads
        and notebook registration use the same metadata route.
    register_notebook : bool, default=False
        When True, render registration status and a button that links the
        current notebook to the selected agreement.
    notebook_type, environment_name, dataset_name, table_name, topic, pipeline_name : str, optional
        Workflow metadata passed to ``_register_current_notebook`` when
        ``register_notebook`` is enabled.

    Returns
    -------
    ipywidgets.Select
        Displayed searchable latest-version agreement selector control. Its
        ``value`` remains the stable ``agreement_id`` for existing callers.
        When registration is enabled, registration widgets are attached as
        attributes on the selector for advanced notebook automation.

    """
    widgets = _require_ipywidgets()
    from IPython import display as ip

    global _SELECTED_AGREEMENT
    if env_name is not None:
        try:
            rows = _list_data_agreements(agreement_rows_or_config, env_name, spark_session=spark_session, metadata_schema=metadata_schema)
        except Exception as exc:
            raise RuntimeError("No agreements found. Run 01_agreement first.") from exc
    else:
        rows = agreement_rows_or_config
    latest_rows = _latest_agreement_versions(rows)
    if not latest_rows:
        raise ValueError("No agreements found. Save a data agreement in notebook 01_agreement first.")
    rows_by_id = {str(row.get("agreement_id") or "").strip(): row for row in latest_rows if str(row.get("agreement_id") or "").strip()}

    def _agreement_label(row: dict[str, Any]) -> str:
        agreement_id = str(row.get("agreement_id") or "").strip()
        return f"{row.get('agreement_name', '') or agreement_id} ({agreement_id} / v{row.get('contract_version', '')})"

    selector_parts = _render_searchable_selector(
        widgets=widgets,
        label="Agreement",
        rows=latest_rows,
        label_fn=_agreement_label,
        value_fn=lambda row: str(row.get("agreement_id") or "").strip(),
        placeholder="Search agreements...",
        search_fields=["agreement_name", "agreement_id", "contract_version", "domain", "recipient"],
        context_fields=[("agreement_name", "Agreement name"), ("agreement_id", "Agreement ID"), ("contract_version", "Current version"), ("recipient", "Recipient")],
    )
    selector = selector_parts["selector"]

    def _on_change(change: dict[str, Any]) -> None:
        global _SELECTED_AGREEMENT
        if change.get("name") == "value" and change.get("new") is not None:
            selected_row = rows_by_id.get(str(change["new"]))
            if selected_row is not None:
                _SELECTED_AGREEMENT = dict(selected_row)

    selector.observe(_on_change, names="value")
    if selector.value in rows_by_id:
        _SELECTED_AGREEMENT = dict(rows_by_id[str(selector.value)])
    selector.search_box = selector_parts["search"]
    selector.context_html = selector_parts["context"]

    registration_status = None
    registration_action = None
    register_button = None
    registration_output = None
    active_rows: list[dict[str, Any]] = []
    active_primary_rows: list[dict[str, Any]] = []

    def _selected_row() -> dict[str, Any] | None:
        return rows_by_id.get(str(selector.value or ""))

    def _status_message() -> str:
        selected = _selected_row()
        if not selected:
            return "Select an agreement before registering this notebook."
        selected_id = str(selected.get("agreement_id") or "")
        selected_version = str(selected.get("contract_version") or "")
        same_active = [row for row in active_rows if str(row.get("agreement_id") or "") == selected_id and str(row.get("agreement_contract_version") or "") == selected_version]
        same_primary = [row for row in same_active if str(row.get("registration_role") or "primary") == "primary"]
        other = [row for row in active_primary_rows if row not in same_primary]
        if same_primary:
            return f"Registration status: already registered to {selected_id} version {selected_version} as the primary active agreement."
        if same_active:
            role = str(same_active[0].get("registration_role") or "additional")
            return f"Registration status: already registered to {selected_id} version {selected_version} as an active {role} agreement link."
        if other:
            current = other[0]
            current_version = str(current.get("agreement_contract_version") or "unknown version")
            return f"Registration status: this notebook is already registered to {current.get('agreement_id', '')} version {current_version}. Choose how to handle the selected agreement."
        return "Registration status: not registered to an active agreement."

    def _refresh_registration_status(*_: Any) -> None:
        if registration_status is None:
            return
        registration_status.value = _html_escape(_status_message())

    if register_notebook:
        if env_name is None or spark_session is None:
            raise ValueError("widget_select_agreement(..., register_notebook=True) requires CONFIG, env_name, and spark_session.")
        config = agreement_rows_or_config
        active_rows = _current_notebook_active_registrations(
            spark_session,
            config=config,
            env=env_name,
            metadata_schema=metadata_schema,
            notebook_type=notebook_type,
            environment_name=environment_name or env_name,
        )
        active_primary_rows = [row for row in active_rows if str(row.get("registration_role") or "primary") == "primary"]
        registration_status = widgets.HTML(value="")
        registration_action = widgets.ToggleButtons(
            options=["Cancel", "Replace active registration", "Add another agreement link"],
            value="Cancel",
            description="If already linked",
        )
        register_button = widgets.Button(description="Register notebook", button_style="primary")
        registration_output = widgets.Output()

        def _register(_: Any = None) -> None:
            selected = _selected_row()
            if registration_output is not None:
                registration_output.clear_output()
            if not selected:
                if registration_status is not None:
                    registration_status.value = "Select an agreement before registering this notebook."
                return
            selected_id = str(selected.get("agreement_id") or "")
            selected_version = str(selected.get("contract_version") or "")
            same_active = [row for row in active_rows if str(row.get("agreement_id") or "") == selected_id and str(row.get("agreement_contract_version") or "") == selected_version]
            same_primary = [row for row in same_active if str(row.get("registration_role") or "primary") == "primary"]
            other = [row for row in active_primary_rows if row not in same_primary]
            if same_active:
                role = str(same_active[0].get("registration_role") or "primary")
                if registration_status is not None:
                    registration_status.value = _html_escape(f"Notebook is already registered to {selected_id} version {selected_version} as an active {role} agreement link; no duplicate was created.")
                return

            role = "primary"
            if other:
                choice = getattr(registration_action, "value", "Cancel")
                if choice == "Cancel":
                    if registration_status is not None:
                        registration_status.value = "Registration canceled. Existing active registration was not changed."
                    return
                if choice == "Add another agreement link":
                    role = "additional"
                elif choice == "Replace active registration":
                    role = "primary"
                else:
                    return

            new_row = _register_current_notebook(
                spark_session,
                config=config,
                env=env_name,
                agreement_id=selected_id,
                contract_version=selected_version,
                registration_role=role,
                registration_status="active",
                metadata_schema=metadata_schema,
                notebook_type=notebook_type,
                environment_name=environment_name or env_name,
                dataset_name=dataset_name,
                table_name=table_name,
                topic=topic,
                pipeline_name=pipeline_name,
            )
            if other and role == "primary":
                superseded_at = _current_audit_timestamp(config=config, drop_microseconds=False)
                for previous in other:
                    _register_current_notebook(
                        spark_session,
                        config=config,
                        env=env_name,
                        agreement_id=previous.get("agreement_id"),
                        contract_version=previous.get("agreement_contract_version"),
                        registration_role=previous.get("registration_role") or "primary",
                        registration_status="superseded",
                        metadata_schema=metadata_schema,
                        registration_id=previous.get("registration_id"),
                        superseded_at=superseded_at,
                        superseded_by_registration_id=new_row.get("registration_id"),
                        notebook_type=previous.get("notebook_type") or notebook_type,
                        environment_name=previous.get("environment_name") or environment_name or env_name,
                        dataset_name=previous.get("dataset_name") or dataset_name,
                        table_name=previous.get("table_name") or table_name,
                        topic=previous.get("topic") or topic,
                        pipeline_name=previous.get("pipeline_name") or pipeline_name,
                    )
                for previous in other:
                    if previous in active_rows:
                        active_rows.remove(previous)
                active_rows.append(new_row)
                active_primary_rows[:] = [new_row]
                message = f"Replaced active registration with {selected_id} version {selected_version}. Previous registration history remains in the audit trail."
            elif role == "additional":
                active_rows.append(new_row)
                message = f"Added additional agreement link to {selected_id} version {selected_version}. Existing primary registration remains active."
            else:
                active_rows.append(new_row)
                active_primary_rows[:] = [new_row]
                message = f"Registered notebook to {selected_id} version {selected_version}."
            if registration_status is not None:
                registration_status.value = _html_escape(message)

        register_button.on_click(_register)
        selector.observe(lambda change: _refresh_registration_status() if change.get("name") == "value" else None, names="value")
        _refresh_registration_status()
        selector.registration_status = registration_status
        selector.registration_action = registration_action
        selector.register_button = register_button
        selector.registration_output = registration_output
        selector.container = widgets.VBox([selector_parts["container"], registration_status, registration_action, register_button, registration_output])
    else:
        selector.container = selector_parts["container"]
    ip.display(selector.container)
    return selector


def get_selected_agreement() -> dict[str, Any]:
    """Return the agreement selected by :func:`widget_select_agreement`.

    Returns
    -------
    dict[str, Any]
        Selected latest-version agreement row.

    Raises
    ------
    RuntimeError
        If no selector has established a selected agreement.

    """
    if not _SELECTED_AGREEMENT:
        raise RuntimeError("No agreement selected. Run widget_select_agreement(...) first.")
    return dict(_SELECTED_AGREEMENT)


def _standard_widget(field: str, value: Any = "", *, options: list[Any] | None = None) -> Any:
    widgets = _require_ipywidgets()
    description = FIELD_LABELS.get(field, field.replace("_", " ").title())
    if options is not None:
        option_values = [option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in options]
        default_value = value if value in option_values else option_values[0] if option_values else None
        return widgets.Dropdown(options=options, value=default_value, **_widget_common(widgets, description))
    if field in {"effective_from", "effective_to", "start_date", "expiry_date"}:
        return widgets.DatePicker(value=date.fromisoformat(str(value)[:10]) if value else None, **_widget_common(widgets, description))
    if field == "is_active":
        return widgets.Checkbox(value=True if value == "" else _to_bool(value), **_widget_common(widgets, description))
    if field in {"business_purpose", "approved_usage_internal", "approved_usage_external", "approved_usage_research"}:
        return widgets.Textarea(value=str(value or ""), **_widget_common(widgets, description, textarea=True))
    return widgets.Text(value=str(value or ""), **_widget_common(widgets, description))


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


def _render_maintenance_widget(*, spark: Any, config: Any, env_name: str, kind: str, display_widget: bool = True) -> dict[str, Any]:
    widgets = _require_ipywidgets()
    from IPython import display as ip

    is_steward = kind == "data_steward_widget"
    prompt = "Create new steward" if is_steward else "Create new agreement"
    widget_config = {**_WIDGET_CONFIG_DEFAULTS[kind], **dict(_config_value(config, kind, {}) or {})}
    fields = _get_widget_visible_fields(config, kind)
    after_save_callbacks: list[Any] = []
    row_lookup: dict[str, dict[str, Any]] = {}

    def _row_id(row: dict[str, Any]) -> str:
        return str(row.get("steward_id" if is_steward else "agreement_id") or "").strip()

    def _existing_rows() -> list[dict[str, Any]]:
        return _list_data_stewards(config, env_name, spark_session=spark, active_only=False, missing_ok=True) if is_steward else _list_data_agreements(config, env_name, spark_session=spark, missing_ok=True)

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
    selected_selector = _render_searchable_selector(
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

    roles = [str(option).strip() for option in (_config_value(config, "steward_role_options", DEFAULT_STEWARD_ROLE_OPTIONS) or []) if str(option).strip()]
    steward_role_options = [(role, role) for role in roles] if is_steward else None
    form = {}
    steward_field_selector = None
    for field in fields:
        if field == "steward_id" and not is_steward:
            steward_rows = _list_data_stewards(config, env_name, spark_session=spark, active_only=True, missing_ok=True)
            steward_field_selector = _render_searchable_selector(
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
            rows = _list_data_stewards(config, env_name, spark_session=spark, active_only=True, missing_ok=True)
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
                    row = _create_or_update_data_steward(spark=spark, config=config, env_name=env_name, values=values, custom_fields=extras)
                    _refresh_existing_options(row["steward_id"])
                    for callback in after_save_callbacks:
                        callback(row)
                    print(f"Saved data steward: {row.get('steward_name', '')} ({row['steward_id']})")
                else:
                    selected_row = row_lookup.get(selected.value) if selected.value else None
                    row = _create_or_update_data_agreement(spark=spark, config=config, env_name=env_name, values=values, selected_agreement=selected_row, custom_fields=extras)
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


def _render_agreement_evidence_widget(*, spark: Any, config: Any, env_name: str, display_widget: bool = True) -> dict[str, Any]:
    """Render optional agreement evidence upload controls."""
    widgets = _require_ipywidgets()
    from IPython import display as ip

    row_lookup: dict[str, dict[str, Any]] = {}

    def _agreement_rows() -> list[dict[str, Any]]:
        return _list_all_data_agreement_rows(config, env_name, spark_session=spark, missing_ok=True)

    def _version_key(row: dict[str, Any]) -> str:
        agreement_id = str(row.get("agreement_id") or "").strip()
        contract_version = str(row.get("contract_version") or "").strip()
        return f"{agreement_id}||{contract_version}" if agreement_id and contract_version else ""

    def _version_label(row: dict[str, Any]) -> str:
        key = _version_key(row)
        return f"{row.get('agreement_name', '') or row.get('agreement_id', '')} ({row.get('agreement_id', '')} / v{row.get('contract_version', '')})" if key else ""

    def _selector_rows() -> list[dict[str, Any]]:
        row_lookup.clear()
        rows = [row for row in _agreement_rows() if _version_key(row)]
        row_lookup.update({_version_key(row): row for row in rows})
        return rows

    message = widgets.HTML(value="")
    version_selector = _render_searchable_selector(
        widgets=widgets,
        label="Agreement Version",
        rows=_selector_rows(),
        label_fn=_version_label,
        value_fn=_version_key,
        placeholder="Search agreement versions...",
        search_fields=["agreement_name", "agreement_id", "contract_version", "domain", "recipient"],
        context_fields=[("agreement_name", "Agreement name"), ("agreement_id", "Agreement ID"), ("contract_version", "Contract version"), ("recipient", "Recipient")],
        empty_label="Select an agreement version...",
    )
    selected = version_selector["selector"]
    evidence_type = widgets.Dropdown(options=[(item, item) for item in AGREEMENT_EVIDENCE_TYPES], **_widget_common(widgets, "Evidence Type"))
    evidence_file_paths = widgets.Textarea(
        placeholder=(
            "Files/fabricops/agreement_evidence/<agreement_id>/<contract_version>/signed_agreement.pdf\n"
            "Files/fabricops/agreement_evidence/<agreement_id>/<contract_version>/email_approval.pdf"
        ),
        **_widget_common(widgets, "Evidence File Paths"),
    )
    instructions = widgets.HTML(
        value=(
            "Upload evidence files manually to the metadata lakehouse Files area, "
            "then paste one Files/... path per line."
        )
    )
    refresh = widgets.Button(description="Refresh agreements")
    save = widgets.Button(description="Save evidence")
    output = widgets.Output()

    def _set_empty_state() -> None:
        has_agreement = any(value for _, value in selected.options)
        message.value = "" if has_agreement else "<b>No data agreements found.</b> Save a Data Agreement first, then return here to upload optional evidence."
        evidence_file_paths.disabled = not has_agreement
        save.disabled = not has_agreement

    def _refresh(_: Any = None) -> None:
        current = str(selected.value or "")
        rows = _selector_rows()
        selected.refresh_rows(rows, current if current in row_lookup else "")
        _set_empty_state()

    def _clear_output() -> None:
        clear = getattr(output, "clear_output", None)
        if clear is not None:
            clear(wait=True)

    def _save(_: Any) -> None:
        save.disabled = True
        _clear_output()
        with output:
            try:
                selected_row = row_lookup.get(selected.value or "")
                if not selected_row:
                    raise ValueError("Select an agreement version before saving evidence.")
                rows = _save_agreement_evidence_records(
                    spark=spark,
                    config=config,
                    env_name=env_name,
                    agreement_id=str(selected_row.get("agreement_id") or ""),
                    contract_version=str(selected_row.get("contract_version") or ""),
                    evidence_type=str(evidence_type.value or "Other"),
                    evidence_file_paths=evidence_file_paths.value,
                )
                print(f"Saved {len(rows)} agreement evidence file reference row(s).")
            except Exception as exc:
                print(f"Error: {exc}")
            finally:
                _set_empty_state()
                if any(value for _, value in selected.options):
                    save.disabled = False

    refresh.on_click(_refresh)
    save.on_click(_save)
    _set_empty_state()
    container = widgets.VBox([message, version_selector["container"], evidence_type, instructions, evidence_file_paths, refresh, save, output])
    if display_widget:
        ip.display(container)
    return {
        "container": container,
        "message": message,
        "agreement_version": selected,
        "agreement_version_search": version_selector["search"],
        "agreement_version_context": version_selector["context"],
        "agreement_versions_by_key": row_lookup,
        "evidence_type": evidence_type,
        "evidence_file_paths": evidence_file_paths,
        "instructions": instructions,
        "refresh_agreements_button": refresh,
        "refresh_agreements": _refresh,
        "save_button": save,
        "output": output,
    }


def widget_render_agreement_evidence(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]:
    """Render standalone agreement evidence upload controls.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Configuration containing agreement metadata routing and evidence table
        settings.
    env_name : str
        Environment key configured by ``00_env_config``.
    spark : pyspark.sql.SparkSession
        Fabric Spark session used for metadata reads, file writes, and
        append-only evidence metadata writes.

    Returns
    -------
    dict[str, Any]
        Rendered controls for selecting an agreement version, pasting
        metadata lakehouse evidence file paths, refreshing agreement options,
        and saving evidence metadata rows.

    Notes
    -----
    This public wrapper is intended for the separate-widget ``01_agreement`` layout.
    Evidence files must be uploaded manually to the metadata lakehouse
    ``Files`` area first. The widget appends one file-reference row per
    pasted ``Files/...`` path to ``METADATA_DATA_AGREEMENT_EVIDENCE`` and
    does not read or write binary file content.

    """
    return _render_agreement_evidence_widget(
        spark=spark,
        config=config,
        env_name=env_name,
    )


def widget_render_data_steward(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]:
    """Render append-only data steward create/update maintenance.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Configuration containing steward widget fields and metadata routing.
    env_name : str
        Environment key configured by ``00_env_config``.
    spark : pyspark.sql.SparkSession
        Fabric Spark session used for metadata reads and append-only writes.

    Returns
    -------
    dict[str, Any]
        Rendered widget controls keyed for notebook customization.

    """
    return _render_maintenance_widget(spark=spark, config=config, env_name=env_name, kind="data_steward_widget")


def widget_render_data_agreement(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]:
    """Render append-only agreement create/update maintenance using active stewards.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Configuration containing agreement widget fields and metadata routing.
    env_name : str
        Environment key configured by ``00_env_config``.
    spark : pyspark.sql.SparkSession
        Fabric Spark session used for metadata reads and append-only writes.

    Returns
    -------
    dict[str, Any]
        Rendered controls, including read-only generated-identifier context.

    """
    return _render_maintenance_widget(spark=spark, config=config, env_name=env_name, kind="data_agreement_widget")

