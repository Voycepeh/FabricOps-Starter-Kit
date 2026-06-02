"""Lightweight, config-driven steward and data-agreement intake for Fabric notebooks.

The ``00_env_config`` notebook prepares the two metadata tables and widget
configuration. The ``01_da`` notebook then renders steward maintenance before
agreement maintenance. Both tables are append-only and use framework-managed
runtime audit columns.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
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
    "steward_name", "steward_role", "contact", "effective_from", "effective_to",
]
DATA_STEWARD_BACKEND_FIELDS = ["steward_id", "is_active"]
DATA_AGREEMENT_VISIBLE_FIELDS = [
    "agreement_name", "domain", "steward_id", "start_date", "expiry_date",
    "business_purpose", "approved_usage",
]
DATA_AGREEMENT_GENERATED_FIELDS = ["agreement_id", "contract_version"]
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
    "approved_usage": "Approved Usage",
}
_WIDGET_STYLE = {"description_width": "150px"}
_WIDGET_WIDTH = "600px"
_TEXTAREA_HEIGHT = "80px"
DATA_STEWARD_FIELDS = (
    ["steward_id"] + DATA_STEWARD_VISIBLE_FIELDS + ["is_active", "custom_fields_json"] + STANDARD_RUNTIME_AUDIT_COLUMNS
)
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
    if kind == "data_steward_widget":
        hidden.update(DATA_STEWARD_BACKEND_FIELDS)
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
        common = {
            "description": str(definition.get("label", key)),
            "style": _WIDGET_STYLE,
            "layout": _widget_layout(widgets, textarea=field_type == "textarea"),
        }
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


def _is_explicit_false(value: Any) -> bool:
    """Return whether a populated backend flag explicitly disables a row."""
    return value not in (None, "") and not _to_bool(value)


def _active_steward(row: dict[str, Any]) -> bool:
    """Return whether a steward is effective today and not backend-disabled."""
    if _is_explicit_false(row.get("is_active")):
        return False
    today = datetime.now(timezone.utc).date()
    try:
        return (not row.get("effective_from") or date.fromisoformat(str(row["effective_from"])[:10]) <= today) and (
            not row.get("effective_to") or date.fromisoformat(str(row["effective_to"])[:10]) >= today
        )
    except ValueError as exc:
        raise ValueError(
            f"{DATA_STEWARD_TABLE} row '{row.get('steward_id', '')}' has an invalid effective date. Use ISO dates."
        ) from exc


def _build_steward_dropdown_options(active_stewards: Any) -> list[tuple[str, str]]:
    """Build friendly active-steward dropdown options backed by stable IDs."""
    options: list[tuple[str, str]] = []
    for row in _coerce_row_dicts(active_stewards):
        steward_id = str(row.get("steward_id") or "").strip()
        if not steward_id:
            continue
        parts = [str(row.get(field) or "").strip() for field in ("steward_name", "steward_role", "contact")]
        label = " | ".join(part for part in parts if part) or steward_id
        options.append((label, steward_id))
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
    labels = dict(_build_steward_dropdown_options(profiles))
    return [{**row, "label": labels[row["steward_id"]]} for row in profiles]


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


def _generate_steward_id(values: dict[str, Any]) -> str:
    """Return a stable steward ID derived from maintained identity fields."""
    identity = "|".join(
        str(values.get(field) or "").strip().lower() for field in ("steward_name", "contact", "effective_from")
    )
    return "STEW-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12].upper()


def _derive_steward_activity(effective_from: str, effective_to: str) -> str:
    """Return the backend activity flag derived from an effective date range."""
    today = datetime.now(timezone.utc).date().isoformat()
    active = (not effective_from or effective_from <= today) and (not effective_to or effective_to >= today)
    return "true" if active else "false"


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
    row["steward_id"] = str(values.get("steward_id") or "").strip() or _generate_steward_id(row)
    required = ["steward_id", "steward_name", "steward_role", "contact"]
    missing = [field for field in required if not str(row.get(field) or "").strip()]
    if missing:
        raise ValueError("Missing required steward field(s): " + ", ".join(missing))
    row["effective_from"] = _parse_iso_date(row.get("effective_from"), "effective_from")
    row["effective_to"] = _parse_iso_date(row.get("effective_to"), "effective_to")
    if row["effective_to"] and row["effective_to"] < row["effective_from"]:
        raise ValueError("effective_to must be on or after effective_from.")
    row["is_active"] = _derive_steward_activity(row["effective_from"], row["effective_to"])
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


def _load_data_agreement_rows(
    config: Any, env_name: str, *, spark_session: Any = None, missing_ok: bool = False
) -> list[dict[str, Any]]:
    """Load every agreement version from the configured metadata lakehouse."""
    try:
        rows = read_lakehouse_table(
            config,
            env_name,
            "metadata",
            _table_name(config, "data_agreement", DATA_AGREEMENT_TABLE),
            spark_session=spark_session,
        )
    except Exception:
        if missing_ok:
            return []
        raise
    return _coerce_row_dicts(rows)


def _agreement_business_values(row: dict[str, Any]) -> dict[str, Any]:
    """Return comparable agreement values without generated or audit fields."""
    return {field: row.get(field, "") for field in DATA_AGREEMENT_VISIBLE_FIELDS} | {
        "custom_fields_json": _serialize_custom_fields(_deserialize_custom_fields(row.get("custom_fields_json", "")))
    }


def _create_or_update_data_agreement(
    *,
    spark: Any,
    config: Any,
    env_name: str,
    values: dict[str, Any],
    selected_agreement: dict[str, Any] | None = None,
    custom_fields: dict[str, Any] | None = None,
    committed_by: str | None = None,
    committed_at: str | None = None,
    runtime_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Append a new agreement or the next changed version of an existing one."""
    row = {field: values.get(field, "") for field in DATA_AGREEMENT_VISIBLE_FIELDS}
    row["start_date"] = _parse_iso_date(row.get("start_date"), "start_date", required=True)
    row["expiry_date"] = _parse_iso_date(row.get("expiry_date"), "expiry_date", required=True)
    if row["expiry_date"] < row["start_date"]:
        raise ValueError("expiry_date must be on or after start_date.")
    row["custom_fields_json"] = _serialize_custom_fields(custom_fields)
    existing_rows = _load_data_agreement_rows(config, env_name, spark_session=spark, missing_ok=True)
    agreement_id = str(selected_agreement.get("agreement_id") if selected_agreement else "").strip()
    matching_rows = [item for item in existing_rows if str(item.get("agreement_id") or "").strip() == agreement_id]
    latest = (
        max(matching_rows, key=lambda item: _parse_contract_version(item.get("contract_version")))
        if matching_rows
        else selected_agreement
    )
    if selected_agreement:
        row["agreement_id"] = agreement_id
        if latest and _agreement_business_values(row) == _agreement_business_values(latest):
            return {**latest, "_was_appended": False}
        row["contract_version"] = _next_minor_version(latest.get("contract_version") if latest else None)
    else:
        row["agreement_id"] = _generate_agreement_id()
        row["contract_version"] = "1.0.0"
    required = [
        "agreement_id", "contract_version", "agreement_name", "domain", "steward_id",
        "start_date", "expiry_date", "business_purpose", "approved_usage",
    ]
    missing = [field for field in required if not str(row.get(field) or "").strip()]
    if missing:
        raise ValueError("Missing required agreement field(s): " + ", ".join(missing))
    active_steward_ids = {
        str(item["steward_id"])
        for item in _list_data_stewards(config, env_name, spark_session=spark, active_only=True)
    }
    if str(row["steward_id"]) not in active_steward_ids:
        raise ValueError("steward_id must reference an active data steward.")
    duplicate = any(
        str(item.get("agreement_id") or "") == row["agreement_id"]
        and str(item.get("contract_version") or "") == row["contract_version"]
        for item in existing_rows
    )
    if duplicate:
        raise ValueError(
            f"Agreement {row['agreement_id']} version {row['contract_version']} already exists. "
            "Select the existing agreement to create the next version, or create a new agreement."
        )
    row.update(
        build_runtime_audit_fields(
            config=config,
            env=env_name,
            committed_by=committed_by,
            committed_at=committed_at,
            runtime_context=runtime_context,
        )
    )
    _write_row(
        spark=spark,
        config=config,
        env_name=env_name,
        table=_table_name(config, "data_agreement", DATA_AGREEMENT_TABLE),
        row=row,
    )
    return {**row, "_was_appended": True}


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


def _field_label(field: str) -> str:
    """Return a notebook-friendly label for a standard intake field."""
    return FIELD_LABELS.get(field, field.replace("_", " ").title())


def _widget_layout(widgets: Any, *, textarea: bool = False) -> Any:
    """Return a readable Fabric notebook layout for an intake control."""
    return widgets.Layout(width=_WIDGET_WIDTH, height=_TEXTAREA_HEIGHT if textarea else None)


def _dropdown_values(options: list[Any]) -> list[Any]:
    """Return scalar values represented by plain or ``(label, value)`` options."""
    return [option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in options]


def _default_dropdown_value(options: list[Any]) -> Any:
    """Return the first scalar dropdown value, never its display-label tuple."""
    values = _dropdown_values(options)
    return values[0] if values else None


def _set_dropdown_options(dropdown: Any, options: list[Any], *, value: Any = None) -> None:
    """Replace dropdown options while preserving a valid scalar selection."""
    dropdown.options = options
    values = _dropdown_values(options)
    dropdown.value = value if value in values else _default_dropdown_value(options)


def _standard_widget(field: str, value: Any = "", *, options: list[Any] | None = None) -> Any:
    import ipywidgets as widgets
    common = {"description": _field_label(field), "style": _WIDGET_STYLE, "layout": _widget_layout(widgets)}
    if options is not None:
        values = _dropdown_values(options)
        return widgets.Dropdown(
            options=options, value=value if value in values else _default_dropdown_value(options), **common
        )
    if field in {"effective_from", "effective_to", "start_date", "expiry_date"}:
        return widgets.DatePicker(value=date.fromisoformat(str(value)[:10]) if value else None, **common)
    if field == "is_active":
        return widgets.Checkbox(value=True if value == "" else _to_bool(value), **common)
    if field in {"business_purpose", "approved_usage"}:
        common["layout"] = _widget_layout(widgets, textarea=True)
        return widgets.Textarea(value=str(value or ""), **common)
    return widgets.Text(value=str(value or ""), **common)


def _render_maintenance_widget(*, spark: Any, config: Any, env_name: str, kind: str) -> dict[str, Any]:
    import ipywidgets as widgets
    from IPython.display import display
    is_steward = kind == "data_steward_widget"
    prompt = "Create new steward" if is_steward else "Create new agreement"
    record_lookup: dict[str, dict[str, Any]] = {}

    def _load_existing() -> list[dict[str, Any]]:
        if is_steward:
            return _list_data_stewards(config, env_name, spark_session=spark, active_only=False, missing_ok=True)
        return _list_data_agreements(config, env_name, spark_session=spark, missing_ok=True)

    def _record_options(rows: list[dict[str, Any]]) -> list[tuple[str, str | None]]:
        record_lookup.clear()
        options: list[tuple[str, str | None]] = [(prompt, None)]
        for row in rows:
            record_id = str(row.get("steward_id" if is_steward else "agreement_id") or "")
            if not record_id:
                continue
            record_lookup[record_id] = row
            if is_steward:
                label = _build_steward_dropdown_options([row])[0][0]
            else:
                label = f"{row.get('agreement_name') or record_id} ({record_id} / v{row.get('contract_version', '')})"
            options.append((label, record_id))
        return options

    selected = widgets.Dropdown(
        options=_record_options(_load_existing()),
        value=None,
        description="Create / update",
        style=_WIDGET_STYLE,
        layout=_widget_layout(widgets),
    )
    identity_context = None if is_steward else widgets.HTML(value="Agreement ID and version are generated when saved.")
    widget_config = _widget_config(config, kind)
    fields = _get_widget_visible_fields(config, kind)

    def _steward_options() -> list[tuple[str, str]]:
        return _build_steward_dropdown_options(
            _list_data_stewards(config, env_name, spark_session=spark, active_only=True, missing_ok=True)
        )

    steward_options = None if is_steward else _steward_options()
    form = {
        field: _standard_widget(field, options=steward_options if field == "steward_id" else None) for field in fields
    }
    custom = _render_custom_fields(widget_config)
    custom_defaults = {key: widget.value for key, widget in custom.items()}

    def _refresh_stewards(_: Any = None) -> None:
        if not is_steward:
            dropdown = form["steward_id"]
            _set_dropdown_options(dropdown, _steward_options(), value=dropdown.value)

    refresh_stewards = None if is_steward else widgets.Button(description="Refresh active stewards")
    if refresh_stewards is not None:
        refresh_stewards.on_click(_refresh_stewards)
    save = widgets.Button(description="Save")
    output = widgets.Output()
    saved_callbacks: list[Any] = []

    def _populate(change: dict[str, Any]) -> None:
        row = record_lookup.get(change.get("new"), {})
        for field, widget in form.items():
            value = row.get(field, "")
            if field in {"effective_from", "effective_to", "start_date", "expiry_date"}:
                value = date.fromisoformat(str(value)[:10]) if value else None
            if field == "steward_id":
                _set_dropdown_options(widget, list(widget.options), value=value)
            else:
                _set_widget_value(widget, value)
        stored = _deserialize_custom_fields(row.get("custom_fields_json", ""))
        for key, widget in custom.items():
            _set_widget_value(widget, stored.get(key, custom_defaults[key]))
        if identity_context is not None:
            identity_context.value = (
                f"Agreement ID: {row.get('agreement_id', '')} | Current version: {row.get('contract_version', '')} | "
                f"Next version on save: {_next_minor_version(row.get('contract_version'))}"
                if row
                else "Agreement ID and version are generated when saved."
            )

    selected.observe(_populate, names="value")

    def _refresh_existing(saved_row: dict[str, Any]) -> None:
        rows = _load_existing()
        record_id = str(saved_row["steward_id" if is_steward else "agreement_id"])
        rows = [row for row in rows if str(row.get("steward_id" if is_steward else "agreement_id") or "") != record_id]
        rows.append(saved_row)
        _set_dropdown_options(selected, _record_options(rows), value=record_id)
        _populate({"new": record_id})

    def _save(_: Any) -> None:
        save.disabled = True
        output.clear_output(wait=True)
        try:
            with output:
                values = {key: _widget_field_value(key, widget.value) for key, widget in form.items()}
                extras = _collect_custom_fields(widget_config, custom)
                if is_steward:
                    if selected.value:
                        values["steward_id"] = selected.value
                        print(
                            "Saving this change will append a new steward row. Existing rows will not be overwritten."
                        )
                    row = _create_or_update_data_steward(
                        spark=spark, config=config, env_name=env_name, values=values, custom_fields=extras
                    )
                    _refresh_existing(row)
                    for callback in saved_callbacks:
                        callback()
                    print(f"Saved data steward: {row['steward_name']} ({row['steward_id']})")
                else:
                    selected_agreement = record_lookup.get(selected.value)
                    if selected_agreement:
                        print("Saving this change will append a new version. Existing rows will not be overwritten.")
                    row = _create_or_update_data_agreement(
                        spark=spark,
                        config=config,
                        env_name=env_name,
                        values=values,
                        selected_agreement=selected_agreement,
                        custom_fields=extras,
                    )
                    _refresh_existing(row)
                    if row.get("_was_appended") is False:
                        print("No changes detected. Nothing was appended.")
                    else:
                        print(
                            f"Saved data agreement: {row['agreement_name']} "
                            f"({row['agreement_id']} v{row['contract_version']})"
                        )
        finally:
            save.disabled = False

    save.on_click(_save)
    controls = [selected]
    if identity_context is not None:
        controls.append(identity_context)
    controls.extend([*form.values(), *custom.values()])
    if refresh_stewards is not None:
        controls.append(refresh_stewards)
    display(widgets.VBox([*controls, save, output]))
    return {
        "existing_record": selected,
        "record_lookup": record_lookup,
        "identity_context": identity_context,
        "fields": form,
        "custom_fields": custom,
        "refresh_stewards": _refresh_stewards,
        "refresh_stewards_button": refresh_stewards,
        "save_button": save,
        "saved_callbacks": saved_callbacks,
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
    import ipywidgets as widgets
    from IPython.display import display

    display(widgets.HTML(value="<h3>Data Steward</h3><p>Create or update steward records used by agreements.</p>"))
    steward_app = render_data_steward_widget(config, env, spark=spark)
    display(
        widgets.HTML(
            value="<h3>Data Agreement</h3><p>Create or update agreement records linked to active stewards.</p>"
        )
    )
    agreement_app = render_data_agreement_widget(config, env, spark=spark)
    if isinstance(steward_app, dict) and isinstance(agreement_app, dict):
        steward_app.get("saved_callbacks", []).append(agreement_app.get("refresh_stewards", lambda: None))
    return {"data_steward": steward_app, "data_agreement": agreement_app}
