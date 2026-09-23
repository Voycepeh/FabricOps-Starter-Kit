"""Microsoft Fabric Scheduled Refresh discovery for Data Contract context."""

from __future__ import annotations

from datetime import datetime
import json
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fabricops_kit.config.shared import resolve_runtime_context

_FABRIC_API = "https://api.fabric.microsoft.com/v1"
_FABRIC_AUDIENCE = "pbi"
_NOTEBOOK_JOB_TYPE = "RunNotebook"


def _time_value(value: Any) -> str | None:
    """Return a compact local execution time from an API date-time or time value."""
    text = str(value or "").strip()
    if not text:
        return None
    candidate = text.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(candidate).strftime("%H:%M")
    except ValueError:
        parts = text.split(":")
        return ":".join(parts[:2]) if len(parts) >= 2 else text


def normalize_scheduled_refresh(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize a Fabric Job Scheduler response without retaining raw API fields."""
    raw_schedules = payload.get("value") or []
    if not isinstance(raw_schedules, list):
        raise ValueError("Fabric schedule response 'value' must be a list.")
    schedules = []
    for raw in raw_schedules:
        if not isinstance(raw, Mapping):
            raise ValueError("Fabric schedule entries must be objects.")
        configuration = raw.get("configuration") or {}
        if not isinstance(configuration, Mapping):
            raise ValueError("Fabric schedule configuration must be an object.")
        recurrence = configuration.get("recurrence") or {}
        if not isinstance(recurrence, Mapping):
            raise ValueError("Fabric schedule configuration and recurrence must be objects.")
        time_candidates = (
            configuration.get("times")
            or recurrence.get("times")
            or [configuration.get("startDateTime") or recurrence.get("startDateTime")]
        )
        if not isinstance(time_candidates, list):
            time_candidates = [time_candidates]
        times = [value for value in (_time_value(item) for item in time_candidates) if value]
        frequency = str(
            recurrence.get("frequency")
            or configuration.get("frequency")
            or configuration.get("type")
            or "scheduled"
        ).strip().lower()
        timezone = str(
            configuration.get("localTimeZoneId")
            or configuration.get("timezone")
            or recurrence.get("timezone")
            or "UTC"
        ).strip()
        schedules.append({
            "enabled": bool(raw.get("enabled", True)),
            "frequency": frequency,
            "times": times,
            "timezone": timezone,
        })
    return canonical_scheduled_refresh({
        "status": "configured" if schedules else "not_configured",
        "schedules": schedules,
    })


def canonical_scheduled_refresh(value: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and retain only the normalized Scheduled Refresh contract fields."""
    status = str(value.get("status") or "unavailable").strip().lower()
    if status not in {"configured", "not_configured", "unavailable"}:
        raise ValueError("Scheduled Refresh status is invalid.")
    raw_schedules = value.get("schedules") or []
    if not isinstance(raw_schedules, list):
        raise ValueError("Scheduled Refresh schedules must be a list.")
    schedules = []
    for raw in raw_schedules:
        if not isinstance(raw, Mapping):
            raise ValueError("Scheduled Refresh entries must be objects.")
        times = raw.get("times") or []
        if not isinstance(times, list):
            raise ValueError("Scheduled Refresh times must be a list.")
        schedules.append({
            "enabled": bool(raw.get("enabled", True)),
            "frequency": str(raw.get("frequency") or "scheduled").strip().lower(),
            "times": [str(item).strip() for item in times if str(item).strip()],
            "timezone": str(raw.get("timezone") or "UTC").strip(),
        })
    if status == "configured" and not schedules:
        raise ValueError("Configured Scheduled Refresh metadata requires at least one schedule.")
    if status != "configured" and schedules:
        raise ValueError("Only configured Scheduled Refresh metadata can contain schedules.")
    return {"status": status, "schedules": schedules}


def _fabric_schedules_json(*, workspace_id: str, item_id: str) -> dict[str, Any]:
    """Read one notebook's schedules through Fabric authentication and REST APIs."""
    import notebookutils  # type: ignore

    token = notebookutils.credentials.getToken(_FABRIC_AUDIENCE)
    url = (
        f"{_FABRIC_API}/workspaces/{workspace_id}/items/{item_id}"
        f"/jobs/{_NOTEBOOK_JOB_TYPE}/schedules"
    )
    request = Request(url, headers={"Authorization": f"Bearer {token}"})
    with urlopen(request, timeout=10) as response:  # noqa: S310 - fixed trusted Fabric API host
        return json.loads(response.read().decode("utf-8"))


def discover_scheduled_refresh(
    *, context: Mapping[str, Any] | None = None,
    workspace_id: str | None = None, item_id: str | None = None,
) -> dict[str, Any]:
    """Return non-fatal normalized schedule discovery for the active Fabric notebook."""
    runtime = resolve_runtime_context(context=dict(context or {}))
    resolved_workspace = str(workspace_id or runtime.get("workspace_id") or "").strip()
    resolved_item = str(item_id or runtime.get("notebook_id") or "").strip()
    if not resolved_workspace or not resolved_item:
        return {
            "status": "unavailable", "schedules": [],
            "message": "Scheduled Refresh discovery is unavailable outside a Fabric notebook context.",
        }
    try:
        return normalize_scheduled_refresh(
            _fabric_schedules_json(workspace_id=resolved_workspace, item_id=resolved_item)
        )
    except (ImportError, AttributeError, HTTPError, URLError, OSError, RuntimeError, ValueError, json.JSONDecodeError):
        return {
            "status": "unavailable", "schedules": [],
            "message": "Scheduled Refresh discovery is unavailable for this notebook.",
        }
