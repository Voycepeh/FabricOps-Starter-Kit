"""Lightweight, config-driven steward and data-agreement intake for Fabric notebooks.

The ``00_env_config`` notebook prepares the two metadata tables and widget
configuration. The ``01_da`` notebook then renders steward maintenance before
agreement maintenance. Both tables are append-only and use framework-managed
runtime audit columns.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
import json
from typing import Any

from .fabric_input_output import read_lakehouse_table, write_lakehouse_table
from .metadata import build_runtime_audit_fields

DATA_AGREEMENT_TABLE = "METADATA_DATA_AGREEMENT"
DATA_STEWARD_TABLE = "METADATA_DATA_STEWARD"
_SELECTED_AGREEMENT: dict[str, Any] | None = None
STANDARD_RUNTIME_AUDIT_COLUMNS = [
    "_committed_by", "_committed_at", "_notebook_name", "_workspace_name",
    "_metadata_lakehouse_name", "_activity_id",
]
DATA_STEWARD_VISIBLE_FIELDS = [
    "steward_id", "steward_name", "steward_role", "contact",
    "effective_from", "effective_to", "is_active",
]
DATA_AGREEMENT_VISIBLE_FIELDS = [
    "agreement_name", "domain", "steward_id", "start_date", "expiry_date",
    "business_purpose", "approved_usage",
]
DATA_AGREEMENT_GENERATED_FIELDS = ["agreement_id", "contract_version"]
DATA_STEWARD_FIELDS = DATA_STEWARD_VISIBLE_FIELDS + ["custom_fields_json"] + STANDARD_RUNTIME_AUDIT_COLUMNS
DATA_AGREEMENT_FIELDS = DATA_AGREEMENT_GENERATED_FIELDS + DATA_AGREEMENT_VISIBLE_FIELDS + ["custom_fields_json"] + STANDARD_RUNTIME_AUDIT_COLUMNS
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
    if kind == "data_agreement_widget":
        hidden.update(DATA_AGREEMENT_GENERATED_FIELDS)
    return [field for field in configured if field not in hidden]


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
        common = {"description": str(definition.get("label", key))}
        value = current.get(key)
        if field_type == "textarea":
            widget = widgets.Textarea(value=str(value or ""), **common)
        elif field_type == "select":
            options = list(definition.get("options", []))
            widget = widgets.Dropdown(options=options, value=value if value in options else (options[0] if options else None), **common)
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
    table_schemas = {_table_name(config, "data_steward", DATA_STEWARD_TABLE): _get_data_steward_schema(), _table_name(config, "data_agreement", DATA_AGREEMENT_TABLE): _get_data_agreement_schema()}
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
    if not _to_bool(row.get("is_active")):
        return False
    today = datetime.now(timezone.utc).date()
    try:
        return (not row.get("effective_from") or date.fromisoformat(str(row["effective_from"])[:10]) <= today) and (not row.get("effective_to") or date.fromisoformat(str(row["effective_to"])[:10]) >= today)
    except ValueError as exc:
        raise ValueError(f"{DATA_STEWARD_TABLE} row '{row.get('steward_id', '')}' has an invalid effective date. Use ISO dates.") from exc


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
    return [{**row, "label": f"{row.get('steward_name', '')} | {row.get('steward_role', '')} | {row.get('contact', '')}"} for row in profiles]


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
        User-facing steward values. Reusing ``steward_id`` appends an update.
    custom_fields : dict[str, Any], optional
        Organization-specific configured values.

    Returns
    -------
    dict[str, Any]
        Appended steward row.
    """
    row = {field: values.get(field, "") for field in DATA_STEWARD_VISIBLE_FIELDS}
    row["is_active"] = "true" if _to_bool(row["is_active"]) else "false"
    required = ["steward_id", "steward_name", "steward_role", "contact"]
    missing = [field for field in required if not str(row.get(field) or "").strip()]
    if missing:
        raise ValueError("Missing required steward field(s): " + ", ".join(missing))
    row["effective_from"] = _parse_iso_date(row.get("effective_from"), "effective_from", required=True)
    row["effective_to"] = _parse_iso_date(row.get("effective_to"), "effective_to")
    if row["effective_to"] and row["effective_to"] < row["effective_from"]:
        raise ValueError("effective_to must be on or after effective_from.")
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


def _list_data_agreements(config: Any, env_name: str, *, spark_session: Any = None, active_only: bool = False, missing_ok: bool = False) -> list[dict[str, Any]]:
    """List latest versioned agreements from the configured metadata lakehouse."""
    try:
        rows = read_lakehouse_table(config, env_name, "metadata", _table_name(config, "data_agreement", DATA_AGREEMENT_TABLE), spark_session=spark_session)
    except Exception:
        if missing_ok:
            return []
        raise
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


def _create_or_update_data_agreement(*, spark: Any, config: Any, env_name: str, values: dict[str, Any], selected_agreement: dict[str, Any] | None = None, custom_fields: dict[str, Any] | None = None, committed_by: str | None = None, committed_at: str | None = None, runtime_context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Append a new agreement or a new semantic version of an existing one.

    Reusing ``selected_agreement`` preserves its stable ``agreement_id`` and
    increments the minor version. Runtime audit fields remain backend-managed.
    """
    row = {field: values.get(field, "") for field in DATA_AGREEMENT_VISIBLE_FIELDS}
    if selected_agreement:
        row["agreement_id"] = selected_agreement["agreement_id"]
        row["contract_version"] = _next_minor_version(selected_agreement.get("contract_version"))
    else:
        row["agreement_id"] = str(row.get("agreement_id") or "").strip() or _generate_agreement_id()
        row["contract_version"] = str(row.get("contract_version") or "1.0.0").strip()
    required = ["agreement_id", "contract_version", "agreement_name", "domain", "steward_id", "start_date", "expiry_date", "business_purpose", "approved_usage"]
    missing = [field for field in required if not str(row.get(field) or "").strip()]
    if missing:
        raise ValueError("Missing required agreement field(s): " + ", ".join(missing))
    row["start_date"] = _parse_iso_date(row.get("start_date"), "start_date", required=True)
    row["expiry_date"] = _parse_iso_date(row.get("expiry_date"), "expiry_date", required=True)
    if row["expiry_date"] < row["start_date"]:
        raise ValueError("expiry_date must be on or after start_date.")
    active_steward_ids = {str(item["steward_id"]) for item in _list_data_stewards(config, env_name, spark_session=spark, active_only=True)}
    if str(row["steward_id"]) not in active_steward_ids:
        raise ValueError("steward_id must reference an active data steward.")
    row["custom_fields_json"] = _serialize_custom_fields(custom_fields)
    row.update(build_runtime_audit_fields(config=config, env=env_name, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context))
    _write_row(spark=spark, config=config, env_name=env_name, table=_table_name(config, "data_agreement", DATA_AGREEMENT_TABLE), row=row)
    return row


def _agreement_dropdown_options(rows: Any, *, include_prompt: bool = False) -> list[tuple[str, Any]]:
    """Build latest-version agreement dropdown options."""
    options = [("Select an agreement to update...", None)] if include_prompt else []
    options.extend((f"{row.get('agreement_name', '')} (Latest v{row.get('contract_version', '')}) - {row.get('domain', '')}", row) for row in _latest_agreement_versions(rows))
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
    options = _agreement_dropdown_options(rows)
    if not options:
        raise ValueError("No agreements found. Save a data agreement in notebook 01_da first.")
    dropdown = widgets.Dropdown(options=options, description="Agreement")
    def _on_change(change: dict[str, Any]) -> None:
        global _SELECTED_AGREEMENT
        if change.get("name") == "value" and change.get("new") is not None:
            _SELECTED_AGREEMENT = dict(change["new"])
    dropdown.observe(_on_change, names="value")
    _SELECTED_AGREEMENT = dict(options[0][1])
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
    current = getattr(widget, "value", None)
    if isinstance(current, tuple):
        value = tuple(value or ())
    elif isinstance(current, bool):
        value = _to_bool(value)
    widget.value = value


def _widget_field_value(field: str, value: Any) -> Any:
    """Convert only date fields before passing widget values to persistence."""
    return _to_iso_date(value) if field in {"effective_from", "effective_to", "start_date", "expiry_date"} else value


def _standard_widget(field: str, value: Any = "", *, options: list[Any] | None = None) -> Any:
    import ipywidgets as widgets
    description = field.replace("_", " ").title()
    if options is not None:
        return widgets.Dropdown(options=options, value=value if value in options else (options[0] if options else None), description=description)
    if field in {"effective_from", "effective_to", "start_date", "expiry_date"}:
        return widgets.DatePicker(value=date.fromisoformat(str(value)[:10]) if value else None, description=description)
    if field == "is_active":
        return widgets.Checkbox(value=True if value == "" else _to_bool(value), description=description)
    if field in {"business_purpose", "approved_usage"}:
        return widgets.Textarea(value=str(value or ""), description=description)
    return widgets.Text(value=str(value or ""), description=description)


def _render_maintenance_widget(*, spark: Any, config: Any, env_name: str, kind: str) -> dict[str, Any]:
    import ipywidgets as widgets
    from IPython.display import display
    is_steward = kind == "data_steward_widget"
    existing = _list_data_stewards(config, env_name, spark_session=spark, active_only=False, missing_ok=True) if is_steward else _list_data_agreements(config, env_name, spark_session=spark, missing_ok=True)
    prompt = "Create new steward" if is_steward else "Create new agreement"
    labels = [(prompt, None)] + [((row.get("steward_name") if is_steward else row.get("agreement_name")) or row.get("steward_id") or row.get("agreement_id"), row) for row in existing]
    selected = widgets.Dropdown(options=labels, description="Create / update")
    identity_context = None if is_steward else widgets.HTML(value="Agreement ID and version are generated when saved.")
    widget_config = _widget_config(config, kind)
    fields = _get_widget_visible_fields(config, kind)
    def _steward_options() -> list[tuple[str, str]]:
        return [(f"{row.get('steward_name', '')} | {row.get('steward_role', '')}", row["steward_id"]) for row in _list_data_stewards(config, env_name, spark_session=spark, active_only=True, missing_ok=True)]
    steward_options = None if is_steward else _steward_options()
    form = {field: _standard_widget(field, options=steward_options if field == "steward_id" else None) for field in fields}
    custom = _render_custom_fields(widget_config)
    refresh_stewards = None if is_steward else widgets.Button(description="Refresh active stewards")
    if refresh_stewards is not None:
        def _refresh_stewards(_: Any) -> None:
            form["steward_id"].options = _steward_options()
        refresh_stewards.on_click(_refresh_stewards)
    save = widgets.Button(description="Save")
    output = widgets.Output()
    def _populate(change: dict[str, Any]) -> None:
        row = change.get("new") or {}
        for field, widget in form.items():
            value = row.get(field, "")
            if field in {"effective_from", "effective_to", "start_date", "expiry_date"}:
                value = date.fromisoformat(str(value)[:10]) if value else None
            _set_widget_value(widget, value)
        stored = _deserialize_custom_fields(row.get("custom_fields_json", ""))
        for key, widget in custom.items():
            _set_widget_value(widget, stored.get(key, widget.value))
        if identity_context is not None:
            identity_context.value = (f"Agreement ID: {row.get('agreement_id', '')} | Current version: {row.get('contract_version', '')}" if row else "Agreement ID and version are generated when saved.")
    selected.observe(_populate, names="value")
    def _save(_: Any) -> None:
        with output:
            values = {key: _widget_field_value(key, widget.value) for key, widget in form.items()}
            extras = _collect_custom_fields(widget_config, custom)
            if is_steward:
                row = _create_or_update_data_steward(spark=spark, config=config, env_name=env_name, values=values, custom_fields=extras)
                print(f"Saved data steward {row['steward_id']}.")
            else:
                row = _create_or_update_data_agreement(spark=spark, config=config, env_name=env_name, values=values, selected_agreement=selected.value, custom_fields=extras)
                print(f"Saved data agreement {row['agreement_id']} version {row['contract_version']}.")
    save.on_click(_save)
    controls = [selected]
    if identity_context is not None:
        controls.append(identity_context)
    controls.extend([*form.values(), *custom.values()])
    if refresh_stewards is not None:
        controls.append(refresh_stewards)
    display(widgets.VBox([*controls, save, output]))
    return {"existing_record": selected, "identity_context": identity_context, "fields": form, "custom_fields": custom, "refresh_stewards_button": refresh_stewards, "save_button": save, "output": output}


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
    """Render the two plug-and-play ``01_da`` metadata intake widgets.

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
        Data Steward and dependent Data Agreement widget applications.

    Notes
    -----
    The Data Steward widget is shown first so users can maintain active steward
    assignments before rendering or refreshing the dependent Data Agreement
    widget.
    """
    return {
        "data_steward": render_data_steward_widget(config, env, spark=spark),
        "data_agreement": render_data_agreement_widget(config, env, spark=spark),
    }
