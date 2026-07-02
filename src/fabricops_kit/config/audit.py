"""Config-owned audit and Fabric runtime context helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .shared import get_current_audit_timestamp, get_store


def _audit_timestamp_value(config: Any = None) -> datetime:
    """Return a datetime audit value using FABRICOPS_AUDIT_TIMEZONE."""
    return datetime.fromisoformat(get_current_audit_timestamp(config=config, drop_microseconds=False))


def _now_audit_timestamp(config: Any = None) -> str:
    """Return the current audit timestamp using FABRICOPS_AUDIT_TIMEZONE."""
    return get_current_audit_timestamp(config=config, drop_microseconds=False)


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


def _resolve_action_by(action_by: str | None = None) -> str:
    if action_by:
        return str(action_by)
    context = _runtime_context()
    return str(_context_get(context, "userName", "userId") or "unknown")


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
