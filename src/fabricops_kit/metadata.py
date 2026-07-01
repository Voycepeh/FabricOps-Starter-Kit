"""Metadata utilities."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import date, datetime
from typing import Any
from .config.metadata_schemas import metadata_table_schema_registry
from .config.shared import get_current_audit_timestamp, get_store
from .io.shared import configured_lakehouse_schema, write_lakehouse_table_core

def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]:
    if rows is None:
        return []
    if hasattr(rows, "collect"):
        rows = rows.collect()
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows]



def _audit_timestamp_value(config: Any = None) -> datetime:
    """Return a datetime audit value using FABRICOPS_AUDIT_TIMEZONE."""
    return datetime.fromisoformat(get_current_audit_timestamp(config=config, drop_microseconds=False))


def _coerce_metadata_value(value: Any, type_name: str) -> Any:
    """Coerce one metadata value to the Python type expected by the setup schema."""
    if value in (None, ""):
        return None if type_name in {"TimestampType", "DateType", "BooleanType", "LongType", "DoubleType"} else ""
    if type_name == "TimestampType":
        return value if isinstance(value, datetime) else datetime.fromisoformat(str(value))
    if type_name == "DateType":
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value)[:10])
    if type_name == "BooleanType":
        if isinstance(value, bool):
            return value
        normalized = str(value).strip().lower()
        if normalized in {"true", "1", "yes", "y"}:
            return True
        if normalized in {"false", "0", "no", "n"}:
            return False
        return bool(value)
    if type_name == "LongType":
        return int(value)
    if type_name == "DoubleType":
        return float(value)
    return value


def coerce_metadata_row_types(table_name: str, row: dict[str, Any]) -> dict[str, Any]:
    """Return a metadata row with values aligned to the bootstrap schema types."""
    try:
        schema = metadata_table_schema_registry().get(table_name)
    except Exception:
        schema = None
    if schema is None:
        return dict(row)
    coerced = dict(row)
    for field in getattr(schema, "fields", []):
        if field.name in coerced:
            coerced[field.name] = _coerce_metadata_value(coerced[field.name], type(field.dataType).__name__)
    return coerced

def _now_audit_timestamp(config: Any = None) -> str:
    """Return the current audit timestamp using FABRICOPS_AUDIT_TIMEZONE."""
    return get_current_audit_timestamp(config=config, drop_microseconds=False)


def _resolve_action_by(action_by: str | None = None) -> str:
    if action_by:
        return str(action_by)
    context = _runtime_context()
    return str(_context_get(context, "userName", "userId") or "unknown")


def _stable_metadata_key(*parts: Any) -> str:
    normalized = "|".join(str(part or "").strip().lower() for part in parts)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _build_metadata_table_key(environment_name, dataset_name, table_name) -> str:
    return _stable_metadata_key(environment_name, dataset_name, table_name)


def _build_metadata_column_key(environment_name, dataset_name, table_name, column_name) -> str:
    return _stable_metadata_key(environment_name, dataset_name, table_name, column_name)



def _write_guardrail_result_row(
    *,
    spark_session: Any,
    config: Any,
    env: str,
    run_id: str,
    dataset_name: str,
    table_name: str,
    guardrail_type: str,
    rule_type: str,
    result: dict[str, Any],
    rule_key: str = "",
    column_name: str = "",
    results_table: str = "METADATA_GUARDRAIL_RESULTS",
) -> None:
    """Append one runtime guardrail outcome to ``METADATA_GUARDRAIL_RESULTS``."""
    if spark_session is None or not hasattr(spark_session, "createDataFrame"):
        return
    audit = build_runtime_audit_fields(config=config, env=env)
    row = {
        "result_id": str(uuid.uuid4()),
        "run_id": str(run_id or ""),
        "rule_key": str(rule_key or result.get("rule_key") or f"{guardrail_type}_default"),
        "environment_name": env,
        "dataset_name": dataset_name,
        "table_name": table_name,
        "column_name": column_name,
        "guardrail_type": guardrail_type,
        "rule_type": rule_type,
        "status": str(result.get("status") or "not_run"),
        "can_continue": bool(result.get("can_continue", True)),
        "severity": str(result.get("severity") or "blocking"),
        "reason": str(result.get("message") or result.get("reason") or ""),
        "expected_value_json": json.dumps(result.get("expected") or result.get("expected_value_json") or {}, default=str, sort_keys=True),
        "actual_value_json": json.dumps(result.get("actual") or result.get("actual_value_json") or {}, default=str, sort_keys=True),
        "result_payload_json": json.dumps({key: value for key, value in result.items() if key != "dataframe"}, default=str, sort_keys=True),
        "created_at": _audit_timestamp_value(config),
        **audit,
    }
    context = {"config": config, "env": env}
    write_lakehouse_table_core(
        spark_session.createDataFrame([coerce_metadata_row_types(results_table, row)]),
        results_table,
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        context=context,
        mode="append",
    )

def _build_dq_rule_key(environment_name, dataset_name, table_name, rule_id) -> str:
    return _stable_metadata_key(environment_name, dataset_name, table_name, rule_id)


def _context_get(context: Any, *keys: str) -> Any:
    for key in keys:
        try:
            if isinstance(context, dict):
                value = context.get(key)
            else:
                getter = getattr(context, "get", None)
                value = getter(key) if callable(getter) else None
        except Exception:
            value = None
        if value is not None:
            return value
    return None


def _safe_str(value: Any) -> str:
    return "" if value is None else str(value)


def _runtime_context() -> dict[str, Any]:
    try:
        import notebookutils  # type: ignore
    except Exception:
        return {}

    runtime = getattr(notebookutils, "runtime", None)
    context = getattr(runtime, "context", None)
    if context is None:
        return {}

    keys = [
        "currentWorkspaceId",
        "currentWorkspaceName",
        "currentNotebookId",
        "currentNotebookName",
        "workspaceId",
        "workspaceName",
        "notebookId",
        "notebookName",
        "userId",
        "userName",
        "activityId",
    ]
    return {key: _context_get(context, key) for key in keys}


def build_runtime_audit_fields(
    *,
    config: Any = None,
    env: str | None = None,
    timestamp_field: str = "_committed_at",
    user_field: str = "_committed_by",
    workspace_field: str = "_workspace_name",
    notebook_field: str = "_notebook_name",
    metadata_lakehouse_field: str = "_metadata_lakehouse_name",
    activity_field: str = "_activity_id",
    committed_by: str | None = None,
    committed_at: str | None = None,
    runtime_context: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Build reusable framework-managed audit fields for metadata-table rows.

    Parameters
    ----------
    config : FrameworkConfig | dict, optional
        Framework config containing ``path_config.paths[env]["metadata"]``.
    env : str, optional
        Environment key paired with ``config``.
    timestamp_field, user_field, workspace_field, notebook_field : str
        Output keys for timestamp, user, workspace, and notebook audit values.
    metadata_lakehouse_field, activity_field : str
        Output keys for metadata lakehouse and Fabric activity audit values.
    committed_by, committed_at : str, optional
        Deterministic audit overrides. When omitted, values resolve from Fabric
        runtime context and the configured audit timezone timestamp.
    runtime_context : dict[str, Any], optional
        Values merged over :func:`_runtime_context`, primarily for tests or
        controlled notebook overrides.

    Returns
    -------
    dict[str, str]
        Framework-managed metadata audit values keyed by the supplied field
        names.

    Notes
    -----
    DataFrame runtime audit columns and metadata-table audit fields both use
    underscore-prefixed names. This helper centralizes the metadata-table
    convention so notebooks can reuse runtime context when adding dataframe
    audit columns inline.

    """
    context = {**_runtime_context(), **(runtime_context or {})}

    def _first_non_blank(*keys: str) -> Any:
        for key in keys:
            value = _context_get(context, key)
            if value is not None and str(value).strip():
                return value
        return None

    metadata_lakehouse_name = ""
    if config is not None and env is not None:
        try:
            metadata_lakehouse_name = _safe_str(get_store(config=config, env=env, target="metadata").name)
        except ValueError:
            metadata_lakehouse_name = ""
    return {
        user_field: _safe_str(committed_by).strip()
        if committed_by and _safe_str(committed_by).strip()
        else _safe_str(_first_non_blank("userName", "userId") or "unknown"),
        timestamp_field: datetime.fromisoformat(str(committed_at))
        if committed_at
        else datetime.fromisoformat(get_current_audit_timestamp(config=config)),
        workspace_field: _safe_str(_first_non_blank("currentWorkspaceName", "workspaceName") or ""),
        notebook_field: _safe_str(_first_non_blank("currentNotebookName", "notebookName") or ""),
        metadata_lakehouse_field: metadata_lakehouse_name,
        activity_field: _safe_str(_first_non_blank("activityId") or ""),
    }


