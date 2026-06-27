"""Public owner file for building explicit FabricOps context dictionaries."""

from __future__ import annotations

from typing import Any

from .shared import get_default_fabric_context

_DEFAULT_CONTEXT_ERROR = "No active Fabric context found. Please run 00_env_config before running this notebook."


def get_fabric_context(
    *,
    env: str | None = None,
    config: Any = None,
    workspace_id: str | None = None,
    lakehouse_id: str | None = None,
    workspace_name: str | None = None,
    lakehouse_name: str | None = None,
    **values: Any,
) -> dict[str, Any]:
    """Build a Fabric context from explicit values or the active default.

    Parameters
    ----------
    env : str, optional
        Environment key to use. Defaults to the active ``00_env_config`` value.
    config : Any, optional
        FrameworkConfig or compatible config object. Defaults to the active
        ``00_env_config`` value.
    workspace_id : str, optional
        Workspace ID override for advanced cross-workspace usage.
    lakehouse_id : str, optional
        Lakehouse item ID override for advanced usage.
    workspace_name : str, optional
        Workspace name override.
    lakehouse_name : str, optional
        Lakehouse name override.
    **values
        Additional context values to merge into the returned dictionary.

    Returns
    -------
    dict[str, Any]
        Fabric context dictionary suitable for helper ``context=`` overrides.

    """
    base: dict[str, Any] = {} if config is not None and env is not None else dict(get_default_fabric_context())
    if config is not None:
        base["config"] = config
    if env is not None:
        base["env"] = env
    for key, value in {
        "workspace_id": workspace_id,
        "lakehouse_id": lakehouse_id,
        "workspace_name": workspace_name,
        "lakehouse_name": lakehouse_name,
    }.items():
        if value is not None:
            base[key] = value
    base.update(values)
    if not base.get("config") or not base.get("env"):
        raise RuntimeError(_DEFAULT_CONTEXT_ERROR)
    return base


__all__ = ["get_fabric_context"]
