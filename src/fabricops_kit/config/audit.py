"""Config-owned audit and Fabric runtime context helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .shared import get_current_audit_timestamp, get_store, resolve_runtime_context


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


def _resolve_action_by(action_by: str | None = None) -> str:
    if action_by:
        return str(action_by)
    context = resolve_runtime_context()
    return str(_context_get(context, "user_name", "user_id") or "unknown")


def _valid_audit_value(value: Any) -> bool:
    """Return whether a required audit value is concrete and non-placeholder."""
    if value is None:
        return False
    text = str(value).strip()
    return bool(text) and text.lower() not in {"none", "unknown", "unknown_notebook"}


def _require_audit_values(values: dict[str, Any]) -> None:
    """Raise one error listing every missing runtime audit field."""
    missing = [key for key, value in values.items() if not _valid_audit_value(value)]
    if missing:
        raise ValueError(
            "Cannot build metadata audit fields. Missing required values:\n"
            f"{', '.join(missing)}.\n\n"
            "Run inside Fabric or provide deterministic runtime_context and\n"
            "metadata_lakehouse_name values."
        )


def build_runtime_audit_fields(
    *,
    config: Any = None,
    env: str | None = None,
    timestamp_field: str = "_committed_at",
    user_field: str = "_committed_by",
    workspace_id_field: str = "_workspace_id",
    workspace_field: str = "_workspace_name",
    notebook_id_field: str = "_notebook_id",
    notebook_field: str = "_notebook_name",
    metadata_lakehouse_field: str = "_metadata_lakehouse_name",
    activity_field: str = "_activity_id",
    committed_by: str | None = None,
    committed_at: str | datetime | None = None,
    metadata_lakehouse_name: str | None = None,
    runtime_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build canonical runtime audit fields for metadata-table rows.

    Parameters
    ----------
    config : FrameworkConfig | dict, optional
        Framework config containing ``path_config.paths[env]["metadata"]``.
    env : str, optional
        Environment key paired with ``config`` when resolving the metadata
        Lakehouse name.
    timestamp_field, user_field, workspace_id_field, workspace_field, notebook_id_field, notebook_field : str
        Output keys for timestamp, user, workspace, and notebook audit values.
    metadata_lakehouse_field, activity_field : str
        Output keys for metadata Lakehouse and Fabric activity audit values.
    committed_by, committed_at, metadata_lakehouse_name : str, optional
        Deterministic audit overrides for local tests and controlled writers.
    runtime_context : dict[str, Any], optional
        Values merged over Fabric runtime context, primarily for tests or
        controlled notebook overrides.

    Returns
    -------
    dict[str, Any]
        Canonical metadata audit values including committed user, timestamp,
        workspace ID/name, notebook ID/name, metadata Lakehouse name, and
        activity ID.

    """
    context = resolve_runtime_context(context=runtime_context)

    def _first_valid(*keys: str) -> Any:
        for key in keys:
            value = _context_get(context, key)
            if _valid_audit_value(value):
                return value
        return None

    if committed_at is None:
        timestamp_value = datetime.fromisoformat(get_current_audit_timestamp(config=config, drop_microseconds=False))
    elif isinstance(committed_at, datetime):
        timestamp_value = committed_at
    else:
        timestamp_value = datetime.fromisoformat(str(committed_at))

    resolved_metadata_lakehouse = metadata_lakehouse_name
    if not _valid_audit_value(resolved_metadata_lakehouse) and config is not None and env is not None:
        resolved_metadata_lakehouse = get_store(config=config, env=env, target="metadata").name

    values = {
        user_field: committed_by if _valid_audit_value(committed_by) else _first_valid("user_name", "user_id"),
        timestamp_field: timestamp_value,
        workspace_id_field: _first_valid("workspace_id"),
        workspace_field: _first_valid("workspace_name"),
        notebook_id_field: _first_valid("notebook_id"),
        notebook_field: _first_valid("notebook_name"),
        metadata_lakehouse_field: resolved_metadata_lakehouse,
        activity_field: _first_valid("activity_id"),
    }
    _require_audit_values(values)
    values[user_field] = str(values[user_field]).strip()
    values[workspace_id_field] = str(values[workspace_id_field]).strip()
    values[workspace_field] = str(values[workspace_field]).strip()
    values[notebook_id_field] = str(values[notebook_id_field]).strip()
    values[notebook_field] = str(values[notebook_field]).strip()
    values[metadata_lakehouse_field] = str(values[metadata_lakehouse_field]).strip()
    values[activity_field] = str(values[activity_field]).strip()
    return values
