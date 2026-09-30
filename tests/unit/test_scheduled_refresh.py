"""Tests for non-fatal Microsoft Fabric Scheduled Refresh discovery."""

from urllib.error import HTTPError
import json

from fabricops_kit.data_contract import scheduled_refresh


def _context() -> dict[str, str]:
    return {"workspace_id": "workspace-id", "notebook_id": "notebook-id"}


def test_fabric_boundary_uses_notebook_token_and_item_schedule_endpoint(
    monkeypatch, fake_notebookutils,
):
    """Use Fabric notebook authentication without duplicating credential handling."""
    captured = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps({"value": []}).encode()

    def get_token(audience):
        captured["audience"] = audience
        return "token"

    def open_request(request, timeout):
        captured.update(url=request.full_url, authorization=request.headers["Authorization"], timeout=timeout)
        return Response()

    fake_notebookutils.credentials.getToken = get_token
    monkeypatch.setattr(scheduled_refresh, "urlopen", open_request)

    result = scheduled_refresh._fabric_schedules_json(
        workspace_id="workspace-id", item_id="notebook-id",
    )

    assert result == {"value": []}
    assert captured == {
        "audience": "pbi",
        "url": "https://api.fabric.microsoft.com/v1/workspaces/workspace-id/items/notebook-id/jobs/RunNotebook/schedules",
        "authorization": "Bearer token", "timeout": 10,
    }


def test_discovers_one_daily_schedule_with_local_timezone(monkeypatch):
    """Normalize one enabled daily schedule without exposing raw API properties."""
    monkeypatch.setattr(scheduled_refresh, "resolve_runtime_context", lambda **_kwargs: _context())
    monkeypatch.setattr(scheduled_refresh, "_fabric_schedules_json", lambda **_kwargs: {
        "value": [{
            "id": "raw-schedule-id", "enabled": True,
            "configuration": {
                "startDateTime": "2026-09-23T08:00:00",
                "localTimeZoneId": "Asia/Singapore",
                "recurrence": {"frequency": "Daily", "interval": 1},
            },
        }],
    })

    result = scheduled_refresh.discover_scheduled_refresh(context={})

    assert result == {
        "status": "configured",
        "schedules": [{
            "enabled": True, "frequency": "daily", "times": ["08:00"],
            "timezone": "Asia/Singapore",
        }],
    }
    assert "raw-schedule-id" not in str(result)


def test_no_schedule_is_a_calm_configured_result(monkeypatch):
    """An empty Fabric response means no schedule rather than discovery failure."""
    monkeypatch.setattr(scheduled_refresh, "resolve_runtime_context", lambda **_kwargs: _context())
    monkeypatch.setattr(scheduled_refresh, "_fabric_schedules_json", lambda **_kwargs: {"value": []})

    assert scheduled_refresh.discover_scheduled_refresh() == {
        "status": "not_configured", "schedules": [],
    }


def test_multiple_and_disabled_schedules_are_all_preserved(monkeypatch):
    """Discovery retains every normalized schedule and its enabled state."""
    monkeypatch.setattr(scheduled_refresh, "resolve_runtime_context", lambda **_kwargs: _context())
    monkeypatch.setattr(scheduled_refresh, "_fabric_schedules_json", lambda **_kwargs: {"value": [
        {
            "enabled": False,
            "configuration": {
                "times": ["06:30", "18:30"], "timezone": "UTC",
                "recurrence": {"frequency": "Daily"},
            },
        },
        {
            "enabled": True,
            "configuration": {
                "startDateTime": "2026-09-28T09:15:00",
                "localTimeZoneId": "Europe/London",
                "recurrence": {"frequency": "Weekly"},
            },
        },
    ]})

    result = scheduled_refresh.discover_scheduled_refresh()

    assert len(result["schedules"]) == 2
    assert result["schedules"][0] == {
        "enabled": False, "frequency": "daily", "times": ["06:30", "18:30"],
        "timezone": "UTC",
    }
    assert result["schedules"][1]["frequency"] == "weekly"


def test_missing_context_and_api_failure_are_non_fatal(monkeypatch):
    """Local execution and Fabric authorization failures return unavailable state."""
    monkeypatch.setattr(scheduled_refresh, "resolve_runtime_context", lambda **_kwargs: {})
    missing = scheduled_refresh.discover_scheduled_refresh()
    assert missing["status"] == "unavailable"

    monkeypatch.setattr(scheduled_refresh, "resolve_runtime_context", lambda **_kwargs: _context())
    monkeypatch.setattr(
        scheduled_refresh, "_fabric_schedules_json",
        lambda **_kwargs: (_ for _ in ()).throw(HTTPError("url", 403, "Forbidden", {}, None)),
    )
    unavailable = scheduled_refresh.discover_scheduled_refresh()
    assert unavailable["status"] == "unavailable"
    assert unavailable["schedules"] == []
