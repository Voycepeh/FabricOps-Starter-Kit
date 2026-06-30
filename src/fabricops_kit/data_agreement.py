"""Lightweight, config-driven steward and data-agreement intake for Fabric notebooks.

The ``00_env_config`` notebook prepares steward, agreement, and evidence
metadata tables plus widget configuration. The ``01_agreement`` notebook renders
standalone steward, agreement, and optional evidence widgets. Intake tables
are append-only and use framework-managed runtime audit columns.
"""

from __future__ import annotations

from datetime import date, datetime
import hashlib
import json
import re
import sys
from typing import Any

from .agreement_selection_state import get_selected_agreement_state
from .config.shared import DEFAULT_STEWARD_ROLE_OPTIONS, get_current_audit_timestamp, resolve_fabric_context
from .io.shared import configured_lakehouse_schema, read_lakehouse_table_core, write_lakehouse_table_core
from .metadata import _build_runtime_audit_fields, coerce_metadata_row_types

DATA_AGREEMENT_TABLE = "METADATA_DATA_AGREEMENT"
DATA_AGREEMENT_EVIDENCE_TABLE = "METADATA_DATA_AGREEMENT_EVIDENCE"
DATA_STEWARD_TABLE = "METADATA_DATA_STEWARD"
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

_WIDGET_CONFIG_DEFAULTS = {
    "data_steward_widget": {"visible_columns": DATA_STEWARD_VISIBLE_FIELDS, "custom_fields": []},
    "data_agreement_widget": {"visible_columns": DATA_AGREEMENT_VISIBLE_FIELDS, "custom_fields": []},
}
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
    metadata_tables = _config_value(config, "metadata_tables", {}) or {}
    try:
        rows = read_lakehouse_table_core(str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)), target="metadata", schema=metadata_schema, spark_session=spark_session, context={"config": config, "env": env})
    except Exception:
        if missing_ok:
            return []
        raise
    latest = _latest_by_key(rows, "steward_id")
    return [row for row in latest if _active_steward(row, config)] if active_only else latest


def _write_row(*, spark: Any, config: Any, env: str, table: str, row: dict[str, Any]) -> None:
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
        row["is_active"] = False
    else:
        row["is_active"] = bool(_active_steward({**row, "is_active": row.get("is_active", "")}, config))
    row["custom_fields_json"] = _serialize_custom_fields(custom_fields)
    row.update(_build_runtime_audit_fields(config=config, env=env, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context))
    metadata_tables = _config_value(config, "metadata_tables", {}) or {}
    _write_row(spark=spark, config=config, env=env, table=str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)), row=row)
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


def _list_all_data_agreement_rows(config: Any, env: str, *, spark_session: Any = None, missing_ok: bool = False, metadata_schema: str | None = None) -> list[dict[str, Any]]:
    """List all append-only agreement rows from the metadata lakehouse."""
    metadata_tables = _config_value(config, "metadata_tables", {}) or {}
    try:
        rows = read_lakehouse_table_core(str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)), target="metadata", schema=metadata_schema or configured_lakehouse_schema(config, env, "metadata"), context={"config": config, "env": env}, spark_session=spark_session)
    except Exception:
        if missing_ok:
            return []
        raise
    return _coerce_row_dicts(rows)


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
    existing_rows = _list_all_data_agreement_rows(config, env, spark_session=spark, missing_ok=True)
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
    row.update(_build_runtime_audit_fields(config=config, env=env, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context))
    metadata_tables = _config_value(config, "metadata_tables", {}) or {}
    _write_row(spark=spark, config=config, env=env, table=str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)), row=row)
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

def _save_agreement_evidence_records(*, spark: Any, config: Any, env: str, agreement_id: str, contract_version: str, evidence_type: str, evidence_file_paths: Any, committed_by: str | None = None, committed_at: str | None = None, runtime_context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Append manually uploaded evidence file-reference metadata rows."""
    agreement_id = str(agreement_id or "").strip()
    contract_version = str(contract_version or "").strip()
    if not agreement_id:
        raise ValueError("agreement_id is required before saving agreement evidence.")
    if not contract_version:
        raise ValueError("contract_version is required before saving agreement evidence.")
    evidence_type = str(evidence_type or "Other").strip() or "Other"
    file_references = _prepare_evidence_file_references(evidence_file_paths)
    audit = _build_runtime_audit_fields(config=config, env=env, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context)
    uploaded_at = audit.get("_committed_at") or datetime.fromisoformat(get_current_audit_timestamp(config=config, drop_microseconds=False))
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
        _write_row(spark=spark, config=config, env=env, table=str(metadata_tables.get("data_agreement_evidence", DATA_AGREEMENT_EVIDENCE_TABLE)), row=row)
        rows.append(row)
    return rows


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
    selected = get_selected_agreement_state()
    if not selected:
        raise RuntimeError("No agreement selected. Run widget_select_agreement(...) first.")
    return selected


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




