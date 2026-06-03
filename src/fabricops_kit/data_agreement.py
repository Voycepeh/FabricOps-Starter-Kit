"""Lightweight, config-driven steward and data-agreement intake for Fabric notebooks.

The ``00_env_config`` notebook prepares steward, agreement, and evidence
metadata tables plus widget configuration. The ``01_da`` notebook renders a
tabbed intake app for steward maintenance, agreement maintenance, and optional
agreement evidence upload. Intake tables are append-only and use
framework-managed runtime audit columns.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, timezone
import hashlib
import json
from typing import Any

from .config import DEFAULT_STEWARD_ROLE_OPTIONS
from .fabric_input_output import read_lakehouse_table, write_lakehouse_table
from .metadata import build_runtime_audit_fields

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
AGREEMENT_EVIDENCE_ACCEPT = ",".join(AGREEMENT_EVIDENCE_ALLOWED_EXTENSIONS)
AGREEMENT_EVIDENCE_TYPES = [
    "Signed Agreement", "Email Approval", "Policy Document",
    "Supporting Screenshot", "Other",
]

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
# Backward-compatible internal name retained for existing notebook customizations.
_DATA_STEWARD_FIELDS = DATA_STEWARD_FIELDS


def _get_standard_runtime_audit_columns() -> list[str]:
    """Return backend-only runtime audit columns shared by intake tables.

    Returns
    -------
    list[str]
        A copy of the standard audit-column names.
    """
    return list(STANDARD_RUNTIME_AUDIT_COLUMNS)


def _get_data_steward_schema() -> list[str]:
    """Return the lightweight steward metadata-table schema.

    Returns
    -------
    list[str]
        User-facing, JSON extension, and backend-only audit columns.
    """
    return list(DATA_STEWARD_FIELDS)


def _get_data_agreement_schema() -> list[str]:
    """Return the lightweight versioned agreement metadata-table schema.

    Returns
    -------
    list[str]
        User-facing, JSON extension, and backend-only audit columns.
    """
    return list(DATA_AGREEMENT_FIELDS)


def _get_data_agreement_evidence_schema() -> list[str]:
    """Return the agreement evidence metadata-table schema.

    Returns
    -------
    list[str]
        Agreement/version identity, file reference metadata, and audit columns.
    """
    return list(DATA_AGREEMENT_EVIDENCE_FIELDS)


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


def _table_name(config: Any, key: str, default: str) -> str:
    """Return a configured metadata table name or its lightweight default."""
    tables = _config_value(config, "metadata_tables", {}) or {}
    return str(tables.get(key, default))


def _steward_role_options(config: Any) -> list[str]:
    """Return configured Data Steward role dropdown values."""
    options = _config_value(config, "steward_role_options", DEFAULT_STEWARD_ROLE_OPTIONS)
    return [str(option).strip() for option in (options or []) if str(option).strip()]


def _widget_config(config: Any, kind: str) -> dict[str, Any]:
    defaults = {
        "data_steward_widget": {"visible_columns": DATA_STEWARD_VISIBLE_FIELDS, "custom_fields": []},
        "data_agreement_widget": {"visible_columns": DATA_AGREEMENT_VISIBLE_FIELDS, "custom_fields": []},
    }
    configured = dict(_config_value(config, kind, {}) or {})
    return {**defaults[kind], **configured}


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
    configured = _widget_config(config, kind).get("visible_columns", [])
    hidden = set(_get_standard_runtime_audit_columns()) | {"custom_fields_json"}
    if kind == "data_steward_widget":
        hidden.update({"steward_id", "is_active"})
    if kind == "data_agreement_widget":
        hidden.update(DATA_AGREEMENT_GENERATED_FIELDS)
    return [field for field in configured if field not in hidden]


def _field_label(field: str) -> str:
    """Return a notebook-friendly label for a configured intake field."""
    return FIELD_LABELS.get(field, field.replace("_", " ").title())


def _widget_layout(widgets_module: Any, *, textarea: bool = False) -> Any:
    """Return a wide control layout when running with ipywidgets."""
    layout = getattr(widgets_module, "Layout", None)
    if layout is None:
        return None
    kwargs = {"width": _WIDGET_LAYOUT_WIDTH}
    if textarea:
        kwargs["height"] = _TEXTAREA_HEIGHT
    return layout(**kwargs)


def _widget_common(widgets_module: Any, description: str, *, textarea: bool = False) -> dict[str, Any]:
    """Return common style and layout keyword arguments for form controls."""
    common: dict[str, Any] = {"description": description, "style": dict(_WIDGET_STYLE)}
    layout = _widget_layout(widgets_module, textarea=textarea)
    if layout is not None:
        common["layout"] = layout
    return common


def _option_values(options: list[Any]) -> list[Any]:
    """Return actual values from plain or ``(label, value)`` dropdown options."""
    return [option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in options]


def _default_dropdown_value(options: list[Any], value: Any = None) -> Any:
    """Return a valid dropdown value for plain or labeled tuple options."""
    if not options:
        return None
    values = _option_values(options)
    return value if value in values else values[0]


def _html_escape(value: Any) -> str:
    """Return display-safe HTML text for notebook context snippets."""
    import html
    return html.escape(str(value or ""))


def _selector_context_html(row: dict[str, Any] | None, fields: list[tuple[str, str]]) -> str:
    """Render read-only selected-row context without depending on dropdown labels."""
    if not row:
        return "<em>No record selected.</em>"
    parts = []
    for field, label in fields:
        value = _html_escape(row.get(field, ""))
        parts.append(f"<b>{_html_escape(label)}:</b> {value}")
    return "<br>".join(parts)


def _row_search_text(row: dict[str, Any], *, label: str, value: str, search_fields: list[str] | None = None) -> str:
    """Build normalized searchable text for a selector row."""
    fields = search_fields or sorted(str(key) for key in row)
    values = [label, value]
    values.extend(str(row.get(field) or "") for field in fields)
    return " ".join(values).casefold()


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
                "search": _row_search_text(row, label=display_label, value=value, search_fields=search_fields),
            })

    def _matching_options(query: str) -> list[tuple[str, str]]:
        needle = str(query or "").casefold().strip()
        matches = [item for item in indexed_rows if not needle or needle in item["search"]]
        return [(item["label"], item["value"]) for item in matches[:max_results]]

    def _render_context(value: Any) -> None:
        row = lookup.get(str(value or ""))
        context.value = _selector_context_html(row, context_fields) if context_fields else ""

    def _apply_filter(preferred_value: Any = None) -> None:
        current = str(preferred_value if preferred_value is not None else selector.value or "")
        options = _matching_options(search.value)
        if empty_label is not None:
            options = [(empty_label, ""), *options]
        selector.options = options
        values = _option_values(list(options))
        if current and current in lookup and current not in values and not str(search.value or "").strip():
            row = lookup[current]
            options = [(str(label_fn(row) or current), current), *options]
            values = _option_values(list(options))
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
    import ipywidgets as widgets

    definitions = config.get("custom_fields", []) if isinstance(config, dict) else config
    current = values or {}
    rendered: dict[str, Any] = {}
    for definition in definitions:
        key = str(definition["key"])
        field_type = str(definition.get("type", "text")).lower()
        common = _widget_common(widgets, str(definition.get("label", _field_label(key))), textarea=field_type == "textarea")
        value = current.get(key)
        if field_type == "textarea":
            widget = widgets.Textarea(value=str(value or ""), **common)
        elif field_type == "select":
            options = list(definition.get("options", []))
            widget = widgets.Dropdown(options=options, value=_default_dropdown_value(options, value), **common)
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


def _column_names(rows_or_df: Any) -> list[str]:
    if hasattr(rows_or_df, "columns"):
        return list(rows_or_df.columns)
    rows = _coerce_row_dicts(rows_or_df)
    return list(rows[0]) if rows else []


def _ensure_metadata_tables(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]:
    """Idempotently create or validate lightweight ``01_da`` metadata tables.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Configured metadata lakehouse route from ``00_env_config``.
    env_name : str
        Environment key configured by ``00_env_config``.
    spark : pyspark.sql.SparkSession
        Fabric Spark session used to create empty Delta tables when missing.

    Returns
    -------
    dict[str, Any]
        Setup summary with checked table names.

    Notes
    -----
    Metadata reads and writes always use the configured ``metadata`` target.
    Existing tables with older schemas require a deliberate migration; this
    helper does not destructively overwrite metadata.
    """
    table_schemas = {
        _table_name(config, "data_steward", DATA_STEWARD_TABLE): _get_data_steward_schema(),
        _table_name(config, "data_agreement", DATA_AGREEMENT_TABLE): _get_data_agreement_schema(),
        _table_name(config, "data_agreement_evidence", DATA_AGREEMENT_EVIDENCE_TABLE): _get_data_agreement_evidence_schema(),
    }
    created = []
    for table_name, fields in table_schemas.items():
        try:
            table = read_lakehouse_table(config, env_name, "metadata", table_name, spark_session=spark)
        except Exception:
            empty_df = spark.createDataFrame([{field: "" for field in fields}]).limit(0)
            write_lakehouse_table(empty_df, config, env_name, "metadata", table_name, mode="ignore", overwrite_schema=True)
            table = read_lakehouse_table(config, env_name, "metadata", table_name, spark_session=spark)
            created.append(table_name)
        missing = [field for field in fields if field not in _column_names(table)]
        if missing:
            raise ValueError(f"{table_name} is missing required column(s): {', '.join(missing)}. Migrate the table before rendering 01_da.")
    return {"status": "ready", "tables": list(table_schemas), "created_tables": created}


def setup_data_agreement_tables(*, spark: Any, config: Any, env: str, require_active_steward: bool = False) -> dict[str, Any]:
    """Prepare intake tables and report whether agreement intake has a steward.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session used for idempotent table setup.
    config : FrameworkConfig or dict
        Configuration containing the metadata lakehouse route and table names.
    env : str
        Environment key configured by ``00_env_config``.
    require_active_steward : bool, default=False
        Raise when no active steward exists instead of returning ``not_ready``.

    Returns
    -------
    dict[str, Any]
        Setup status, checked tables, created tables, message, and active count.

    Notes
    -----
    ``00_env_config`` calls this before ``01_da``. Missing tables are created
    empty; no fake steward rows are seeded.
    """
    summary = _ensure_metadata_tables(config, env, spark=spark)
    profiles = _list_data_stewards(config, env, spark_session=spark, active_only=True, missing_ok=True)
    summary["active_steward_count"] = len(profiles)
    if profiles:
        summary["message"] = f"{DATA_STEWARD_TABLE} contains active steward rows. 01_da can render both intake widgets."
    else:
        summary["status"] = "not_ready"
        summary["message"] = f"{DATA_STEWARD_TABLE} has no active steward rows yet. Use the 01_da Data Steward widget to create one before saving an agreement."
        if require_active_steward:
            raise ValueError(summary["message"])
    return summary


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


def _steward_active_value(row: dict[str, Any]) -> str:
    """Derive backend active status from effective dates for saved rows."""
    return "true" if _active_steward({**row, "is_active": row.get("is_active", "")}) else "false"


def _generate_steward_id(values: dict[str, Any]) -> str:
    """Generate a stable public-safe steward identifier from business fields."""
    basis = "|".join(str(values.get(field, "")).strip().lower() for field in ("steward_name", "contact", "effective_from"))
    digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:10]
    return f"STEW-{digest}"


def _build_steward_dropdown_options(active_stewards: Any) -> list[tuple[str, str]]:
    """Build friendly steward dropdown options keyed by ``steward_id``."""
    rows = [row for row in _coerce_row_dicts(active_stewards) if str(row.get("steward_id") or "").strip()]
    base_labels: dict[str, str] = {}
    counts: dict[str, int] = {}
    for row in rows:
        row_id = str(row.get("steward_id") or "").strip()
        parts = [str(row.get(field) or "").strip() for field in ("steward_name", "steward_role", "contact")]
        label = " | ".join(part for part in parts if part) or "Unnamed steward"
        base_labels[row_id] = label
        counts[label] = counts.get(label, 0) + 1

    options = []
    for row in rows:
        row_id = str(row["steward_id"]).strip()
        label = base_labels[row_id]
        if counts[label] > 1 or label == "Unnamed steward":
            label = f"{label} ({row_id})"
        options.append((label, row_id))
    return options


def _list_data_stewards(config: Any, env_name: str, *, spark_session: Any = None, active_only: bool = True, missing_ok: bool = False) -> list[dict[str, Any]]:
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

    Returns
    -------
    list[dict[str, Any]]
        Latest steward rows sorted by stable ID.
    """
    try:
        rows = read_lakehouse_table(config, env_name, "metadata", _table_name(config, "data_steward", DATA_STEWARD_TABLE), spark_session=spark_session)
    except Exception:
        if missing_ok:
            return []
        raise
    latest = _latest_by_key(rows, "steward_id")
    return [row for row in latest if _active_steward(row)] if active_only else latest


def _load_active_data_steward_profiles(*, spark: Any, config: Any, env: str) -> list[dict[str, Any]]:
    """Return active stewards for agreement dropdowns.

    Raises
    ------
    ValueError
        If no currently active steward exists.
    """
    profiles = _list_data_stewards(config, env, spark_session=spark, active_only=True)
    if not profiles:
        raise ValueError(f"{DATA_STEWARD_TABLE} has no active steward rows. Use the Data Steward widget first.")
    labels = dict((value, label) for label, value in _build_steward_dropdown_options(profiles))
    return [{**row, "label": labels.get(str(row.get("steward_id") or ""), "Unnamed steward")} for row in profiles]


def _write_row(*, spark: Any, config: Any, env_name: str, table: str, row: dict[str, Any]) -> None:
    write_lakehouse_table(spark.createDataFrame([row]), config, env_name, "metadata", table, mode="append")


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
    configured_roles = set(_steward_role_options(config))
    legacy_role = str(values.get("_legacy_steward_role") or "").strip()
    selected_steward_id = str(values.get("steward_id") or "").strip()
    if str(row["steward_role"]).strip() not in configured_roles and not (selected_steward_id and legacy_role and str(row["steward_role"]).strip() == legacy_role):
        raise ValueError("steward_role must be one of the configured steward role options.")
    row["effective_from"] = _parse_iso_date(row.get("effective_from"), "effective_from")
    row["effective_to"] = _parse_iso_date(row.get("effective_to"), "effective_to")
    if row["effective_to"] and row["effective_from"] and row["effective_to"] < row["effective_from"]:
        raise ValueError("effective_to must be on or after effective_from.")
    row["steward_id"] = str(values.get("steward_id") or "").strip() or _generate_steward_id(row)
    explicit_active = values.get("is_active")
    row["is_active"] = "false" if explicit_active not in (None, "") and not _to_bool(explicit_active) else _steward_active_value(row)
    row["custom_fields_json"] = _serialize_custom_fields(custom_fields)
    row.update(build_runtime_audit_fields(config=config, env=env_name, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context))
    _write_row(spark=spark, config=config, env_name=env_name, table=_table_name(config, "data_steward", DATA_STEWARD_TABLE), row=row)
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
    latest: dict[str, dict[str, Any]] = {}
    for row in _coerce_row_dicts(rows):
        key = str(row.get("agreement_id") or "").strip()
        if key and (key not in latest or _parse_contract_version(row.get("contract_version")) > _parse_contract_version(latest[key].get("contract_version"))):
            latest[key] = row
    return sorted(latest.values(), key=lambda row: str(row.get("agreement_name") or "").lower())


def _list_all_data_agreement_rows(config: Any, env_name: str, *, spark_session: Any = None, missing_ok: bool = False) -> list[dict[str, Any]]:
    """List all append-only agreement rows from the metadata lakehouse."""
    try:
        rows = read_lakehouse_table(config, env_name, "metadata", _table_name(config, "data_agreement", DATA_AGREEMENT_TABLE), spark_session=spark_session)
    except Exception:
        if missing_ok:
            return []
        raise
    return _coerce_row_dicts(rows)


def _list_data_agreements(config: Any, env_name: str, *, spark_session: Any = None, active_only: bool = False, missing_ok: bool = False) -> list[dict[str, Any]]:
    """List latest versioned agreements from the configured metadata lakehouse."""
    rows = _list_all_data_agreement_rows(config, env_name, spark_session=spark_session, missing_ok=missing_ok)
    agreements = _latest_agreement_versions(rows)
    if not active_only:
        return agreements
    today = datetime.now(timezone.utc).date()
    return [row for row in agreements if (not row.get("start_date") or date.fromisoformat(str(row["start_date"])[:10]) <= today) and (not row.get("expiry_date") or date.fromisoformat(str(row["expiry_date"])[:10]) >= today)]


def _load_agreements(config: Any, env: str, *, spark_session: Any = None, missing_ok: bool = False) -> list[dict[str, Any]]:
    """Load latest agreements; retained as the downstream notebook API."""
    try:
        return _list_data_agreements(config, env, spark_session=spark_session, missing_ok=missing_ok)
    except Exception as exc:
        raise RuntimeError("No agreements found. Run 01_da first.") from exc


def _generate_agreement_id() -> str:
    return "DA-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")


def _to_iso_date(value: Any) -> str:
    if value is None:
        return ""
    return value.date().isoformat() if isinstance(value, datetime) else value.isoformat() if isinstance(value, date) else str(value)


def _resolve_agreement_identity(rows: Any, *, agreement_name: str = "", source_system: str = "", allowed_consumer_type: str = "", mode: str = "create", selected_agreement: dict[str, Any] | None = None) -> dict[str, Any]:
    """Resolve an append-only agreement identity for compatibility callers."""
    del rows, agreement_name, source_system, allowed_consumer_type
    normalized_mode = str(mode or "").strip().lower()
    if normalized_mode == "create":
        return {"agreement_id": _generate_agreement_id(), "contract_version": "1.0.0", "is_new_agreement": True}
    if normalized_mode != "update":
        raise ValueError("mode must be either 'create' or 'update'.")
    if not selected_agreement:
        raise ValueError("Update mode requires selected_agreement.")
    return {"agreement_id": selected_agreement["agreement_id"], "contract_version": _next_minor_version(selected_agreement.get("contract_version")), "is_new_agreement": False}


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
    row.update(build_runtime_audit_fields(config=config, env=env_name, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context))
    _write_row(spark=spark, config=config, env_name=env_name, table=_table_name(config, "data_agreement", DATA_AGREEMENT_TABLE), row=row)
    return row




def _metadata_lakehouse_file_path(config: Any, env_name: str, relative_path: str) -> str:
    """Resolve a metadata lakehouse ``Files/`` relative path to ABFSS."""
    paths = config.path_config.paths if hasattr(config, "path_config") else config.paths
    store = paths[env_name]["metadata"]
    if getattr(store, "kind", "lakehouse") != "lakehouse":
        raise ValueError("The configured metadata target must be a lakehouse to store agreement evidence files.")
    normalized = str(relative_path or "").lstrip("/")
    if normalized.startswith("Files/"):
        normalized = normalized[len("Files/"):]
    return f"{store.root.rstrip('/')}/Files/{normalized}"


def _safe_evidence_file_name(file_name: Any) -> str:
    """Return a folder-safe uploaded evidence file name with an allowed suffix."""
    name = str(file_name or "").replace("\\", "/").split("/")[-1].strip()
    if not name:
        raise ValueError("Uploaded evidence file is missing a file name.")
    safe = "".join(char if char.isalnum() or char in {".", "-", "_", " "} else "_" for char in name).strip()
    if not safe:
        raise ValueError("Uploaded evidence file is missing a file name.")
    suffix = "." + safe.rsplit(".", 1)[-1].lower() if "." in safe else ""
    if suffix not in AGREEMENT_EVIDENCE_ALLOWED_EXTENSIONS:
        allowed = ", ".join(AGREEMENT_EVIDENCE_ALLOWED_EXTENSIONS)
        raise ValueError(f"Unsupported evidence file type. Allowed types: {allowed}.")
    return safe


def _write_evidence_file(*, spark: Any, config: Any, env_name: str, relative_path: str, content: bytes) -> str:
    """Write uploaded evidence bytes to the metadata lakehouse Files area."""
    absolute_path = _metadata_lakehouse_file_path(config, env_name, relative_path)
    jvm = getattr(spark, "_jvm", None)
    jsc = getattr(spark, "_jsc", None)
    if jvm is not None and jsc is not None:
        path = jvm.org.apache.hadoop.fs.Path(absolute_path)
        fs = path.getFileSystem(jsc.hadoopConfiguration())
        parent = path.getParent()
        if parent is not None:
            fs.mkdirs(parent)
        stream = fs.create(path, True)
        try:
            stream.write(bytearray(content))
        finally:
            stream.close()
        return absolute_path

    from pathlib import Path
    local_path = Path(absolute_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_bytes(content)
    return absolute_path


def _uploaded_file_items(uploaded_value: Any) -> list[dict[str, Any]]:
    """Normalize ipywidgets FileUpload values across widget versions."""
    if not uploaded_value:
        return []
    if isinstance(uploaded_value, dict):
        raw_items = list(uploaded_value.values())
    else:
        raw_items = list(uploaded_value)
    items = []
    for item in raw_items:
        data = dict(item)
        content = data.get("content", b"")
        if isinstance(content, memoryview):
            content = content.tobytes()
        elif isinstance(content, bytearray):
            content = bytes(content)
        elif isinstance(content, str):
            content = content.encode("utf-8")
        data["content"] = bytes(content or b"")
        items.append(data)
    return items


def _agreement_version_options(rows: Any, *, include_prompt: bool = True) -> list[tuple[str, str | None]]:
    """Build agreement-version dropdown options keyed by agreement/version."""
    options: list[tuple[str, str | None]] = [("Select an agreement version...", None)] if include_prompt else []
    sorted_rows = sorted(_coerce_row_dicts(rows), key=lambda row: (str(row.get("agreement_name") or "").lower(), str(row.get("agreement_id") or ""), _parse_contract_version(row.get("contract_version"))))
    for row in sorted_rows:
        agreement_id = str(row.get("agreement_id") or "").strip()
        contract_version = str(row.get("contract_version") or "").strip()
        if agreement_id and contract_version:
            key = f"{agreement_id}||{contract_version}"
            options.append((f"{row.get('agreement_name', '') or agreement_id} ({agreement_id} / v{contract_version})", key))
    return options


def _save_agreement_evidence_records(*, spark: Any, config: Any, env_name: str, agreement_id: str, contract_version: str, evidence_type: str, uploaded_files: Any, committed_by: str | None = None, committed_at: str | None = None, runtime_context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Persist uploaded evidence files and append file-reference metadata rows."""
    agreement_id = str(agreement_id or "").strip()
    contract_version = str(contract_version or "").strip()
    if not agreement_id:
        raise ValueError("agreement_id is required before saving agreement evidence.")
    if not contract_version:
        raise ValueError("contract_version is required before saving agreement evidence.")
    files = _uploaded_file_items(uploaded_files)
    if not files:
        raise ValueError("Upload at least one evidence file before saving.")
    evidence_type = str(evidence_type or "Other").strip() or "Other"
    audit = build_runtime_audit_fields(config=config, env=env_name, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context)
    uploaded_at = audit.get("_committed_at") or datetime.now(timezone.utc).isoformat()
    uploaded_by = audit.get("_committed_by") or ""
    prepared_files = []
    for index, uploaded in enumerate(files):
        file_name = _safe_evidence_file_name(uploaded.get("name"))
        content = uploaded.get("content", b"")
        if "." in file_name:
            stem, suffix = file_name.rsplit(".", 1)
            suffix = f".{suffix}"
        else:
            stem, suffix = file_name, ""
        token_basis = f"{uploaded_at}|{index}|{file_name}|".encode("utf-8") + content
        storage_token = hashlib.sha256(token_basis).hexdigest()[:8]
        storage_file_name = f"{stem}__{storage_token}{suffix}"
        prepared_files.append((uploaded, file_name, storage_file_name, content))

    rows: list[dict[str, Any]] = []
    for uploaded, file_name, storage_file_name, content in prepared_files:
        relative_path = f"Files/fabricops/agreement_evidence/{agreement_id}/{contract_version}/{storage_file_name}"
        _write_evidence_file(spark=spark, config=config, env_name=env_name, relative_path=relative_path, content=content)
        row = {
            "agreement_id": agreement_id,
            "contract_version": contract_version,
            "evidence_type": evidence_type,
            "file_name": file_name,
            "file_path": relative_path,
            "mime_type": str(uploaded.get("type") or ""),
            "file_size": str(uploaded.get("size") if uploaded.get("size") is not None else len(content)),
            "uploaded_at": uploaded_at,
            "uploaded_by": uploaded_by,
            **audit,
        }
        _write_row(spark=spark, config=config, env_name=env_name, table=_table_name(config, "data_agreement_evidence", DATA_AGREEMENT_EVIDENCE_TABLE), row=row)
        rows.append(row)
    return rows

def _agreement_dropdown_options(rows: Any, *, include_prompt: bool = False) -> list[tuple[str, Any]]:
    """Build latest-version agreement dropdown options keyed by agreement ID."""
    options = [("Select an agreement to update...", None)] if include_prompt else []
    options.extend((f"{row.get('agreement_name', '')} ({row.get('agreement_id', '')} / v{row.get('contract_version', '')})", row.get("agreement_id")) for row in _latest_agreement_versions(rows))
    return options


def select_agreement(agreement_rows_or_config: Any, env_name: str | None = None, *, spark_session: Any = None) -> Any:
    """Render a downstream agreement selector and retain the selected row.

    Parameters
    ----------
    agreement_rows_or_config : FrameworkConfig or iterable
        Pass ``CONFIG`` in normal notebooks, or provide existing rows for
        compatibility with earlier custom notebooks.
    env_name : str, optional
        Environment key used to load agreements when ``CONFIG`` is supplied.
    spark_session : pyspark.sql.SparkSession, optional
        Fabric Spark session used for configured metadata-table reads.

    Returns
    -------
    ipywidgets.Dropdown
        Displayed latest-version agreement selector.
    """
    import ipywidgets as widgets
    from IPython.display import display
    global _SELECTED_AGREEMENT
    rows = _load_agreements(agreement_rows_or_config, env_name, spark_session=spark_session) if env_name is not None else agreement_rows_or_config
    latest_rows = _latest_agreement_versions(rows)
    options = _agreement_dropdown_options(latest_rows)
    if not options:
        raise ValueError("No agreements found. Save a data agreement in notebook 01_da first.")
    rows_by_id = {str(row.get("agreement_id") or ""): row for row in latest_rows}
    dropdown = widgets.Dropdown(options=options, description="Agreement")
    def _on_change(change: dict[str, Any]) -> None:
        global _SELECTED_AGREEMENT
        if change.get("name") == "value" and change.get("new") is not None:
            _SELECTED_AGREEMENT = dict(rows_by_id[str(change["new"])])
    dropdown.observe(_on_change, names="value")
    _SELECTED_AGREEMENT = dict(rows_by_id[str(options[0][1])])
    display(dropdown)
    return dropdown


def get_selected_agreement() -> dict[str, Any]:
    """Return the agreement selected by :func:`select_agreement`.

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
        raise RuntimeError("No agreement selected. Run select_agreement(...) first.")
    return dict(_SELECTED_AGREEMENT)


def _set_widget_value(widget: Any, value: Any) -> None:
    """Assign a stored value using the widget's expected runtime type."""
    select_value = getattr(widget, "select_value", None)
    if callable(select_value):
        select_value(str(value or ""))
        return
    current = getattr(widget, "value", None)
    if isinstance(current, tuple):
        value = tuple(value or ())
    elif isinstance(current, bool):
        value = _to_bool(value)
    else:
        options = getattr(widget, "options", None)
        if options not in (None, ()):
            value = _default_dropdown_value(list(options), value)
    widget.value = value


def _widget_field_value(field: str, value: Any) -> Any:
    """Convert only date fields before passing widget values to persistence."""
    return _to_iso_date(value) if field in {"effective_from", "effective_to", "start_date", "expiry_date"} else value


def _standard_widget(field: str, value: Any = "", *, options: list[Any] | None = None) -> Any:
    import ipywidgets as widgets
    description = _field_label(field)
    if options is not None:
        return widgets.Dropdown(options=options, value=_default_dropdown_value(options, value), **_widget_common(widgets, description))
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
    import ipywidgets as widgets
    from IPython.display import display
    is_steward = kind == "data_steward_widget"
    prompt = "Create new steward" if is_steward else "Create new agreement"
    widget_config = _widget_config(config, kind)
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

    steward_role_options = [(role, role) for role in _steward_role_options(config)] if is_steward else None
    form = {}
    steward_field_selector = None
    for field in fields:
        if field == "steward_id" and not is_steward:
            steward_rows = _list_data_stewards(config, env_name, spark_session=spark, active_only=True, missing_ok=True)
            steward_field_selector = _render_searchable_selector(
                widgets=widgets,
                label=_field_label(field),
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

    def _populate(change: dict[str, Any]) -> None:
        row_id = change.get("new")
        row = row_lookup.get(row_id, {}) if row_id else {}
        for field, widget in form.items():
            value = row.get(field, "")
            if field == "steward_role" and value:
                option_values = _option_values(list(getattr(widget, "options", [])))
                if value not in option_values:
                    widget.options = [*list(getattr(widget, "options", [])), (str(value), str(value))]
            if field in {"effective_from", "effective_to", "start_date", "expiry_date"}:
                value = date.fromisoformat(str(value)[:10]) if value else None
            _set_widget_value(widget, value)
        stored = _deserialize_custom_fields(row.get("custom_fields_json", ""))
        for key, widget in custom.items():
            _set_widget_value(widget, stored.get(key, widget.value))
        if identity_context is not None:
            identity_context.value = _agreement_identity_text(row if row else None)

    selected.observe(_populate, names="value")
    # Keep lightweight test stubs and older custom notebooks that call the first
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
                values = {key: _widget_field_value(key, widget.value) for key, widget in form.items()}
                extras = _collect_custom_fields(widget_config, custom)
                if is_steward:
                    if selected.value:
                        values["steward_id"] = selected.value
                        values["_legacy_steward_role"] = row_lookup.get(selected.value, {}).get("steward_role", "")
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
        display(container)
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
    import ipywidgets as widgets
    from IPython.display import display

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
    upload = widgets.FileUpload(accept=AGREEMENT_EVIDENCE_ACCEPT, multiple=True, description="Upload evidence")
    refresh = widgets.Button(description="Refresh agreements")
    save = widgets.Button(description="Save evidence")
    output = widgets.Output()

    def _set_empty_state() -> None:
        has_agreement = any(value for _, value in selected.options)
        message.value = "" if has_agreement else "<b>No data agreements found.</b> Save a Data Agreement first, then return here to upload optional evidence."
        upload.disabled = not has_agreement
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
                    uploaded_files=upload.value,
                )
                print(f"Saved {len(rows)} agreement evidence file record(s).")
            except Exception as exc:
                print(f"Error: {exc}")
            finally:
                _set_empty_state()
                if any(value for _, value in selected.options):
                    save.disabled = False

    refresh.on_click(_refresh)
    save.on_click(_save)
    _set_empty_state()
    container = widgets.VBox([message, version_selector["container"], evidence_type, upload, refresh, save, output])
    if display_widget:
        display(container)
    return {
        "container": container,
        "message": message,
        "agreement_version": selected,
        "agreement_version_search": version_selector["search"],
        "agreement_version_context": version_selector["context"],
        "agreement_versions_by_key": row_lookup,
        "evidence_type": evidence_type,
        "file_upload": upload,
        "refresh_agreements_button": refresh,
        "refresh_agreements": _refresh,
        "save_button": save,
        "output": output,
    }

def render_data_steward_widget(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]:
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


def render_data_agreement_widget(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]:
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


def render_agreement_intake_app(*, spark: Any, config: Any, env: str) -> dict[str, Any]:
    """Render the tabbed ``01_da`` metadata intake application.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session used for metadata reads and writes.
    config : FrameworkConfig or dict
        Configuration created by ``00_env_config``.
    env : str
        Environment key configured by ``00_env_config``.

    Returns
    -------
    dict[str, Any]
        Data Steward, Data Agreement, Agreement Evidence, and tab controls.

    Notes
    -----
    The app uses ``ipywidgets.Tab`` so only one intake section is visible at a
    time. The Evidence tab is optional and stores uploaded files in the
    configured metadata lakehouse ``Files`` area while appending file-reference
    rows to ``METADATA_DATA_AGREEMENT_EVIDENCE``.
    """
    import ipywidgets as widgets
    from IPython.display import display

    steward_app = _render_maintenance_widget(spark=spark, config=config, env_name=env, kind="data_steward_widget", display_widget=False)
    agreement_app = _render_maintenance_widget(spark=spark, config=config, env_name=env, kind="data_agreement_widget", display_widget=False)
    evidence_app = _render_agreement_evidence_widget(spark=spark, config=config, env_name=env, display_widget=False)
    callbacks = steward_app.get("after_save_callbacks") if isinstance(steward_app, dict) else None
    agreement_refresh = agreement_app.get("refresh_steward_options") if isinstance(agreement_app, dict) else None
    if isinstance(callbacks, list) and callable(agreement_refresh):
        callbacks.append(lambda row: agreement_refresh(row.get("steward_id") if isinstance(row, dict) else None))
    evidence_refresh = evidence_app.get("refresh_agreements") if isinstance(evidence_app, dict) else None
    agreement_callbacks = agreement_app.get("after_save_callbacks") if isinstance(agreement_app, dict) else None
    if isinstance(agreement_callbacks, list) and callable(evidence_refresh):
        agreement_callbacks.append(lambda row: evidence_refresh())

    sections = [
        widgets.VBox([widgets.HTML(value="<h3>Data Steward</h3><p>Create or update steward records used by agreements.</p>"), steward_app["container"]]),
        widgets.VBox([widgets.HTML(value="<h3>Data Agreement</h3><p>Create or update agreement records linked to active stewards.</p>"), agreement_app["container"]]),
        widgets.VBox([widgets.HTML(value="<h3>Agreement Evidence</h3><p>Optionally upload agreement evidence files for a saved agreement version.</p>"), evidence_app["container"]]),
    ]
    tab = widgets.Tab(children=sections)
    for index, title in enumerate(["Data Steward", "Data Agreement", "Agreement Evidence"]):
        tab.set_title(index, title)
    display(tab)
    return {"data_steward": steward_app, "data_agreement": agreement_app, "agreement_evidence": evidence_app, "tab": tab}
