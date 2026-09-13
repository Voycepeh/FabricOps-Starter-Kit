"""Tests for table-id-driven Source Observation Guardrails."""
# ruff: noqa: D103
from __future__ import annotations

from datetime import UTC, datetime
import importlib
import inspect

import pytest

freshness = importlib.import_module("fabricops_kit.pipeline.check_freshness")
stability = importlib.import_module("fabricops_kit.pipeline.check_source_stability")
from fabricops_kit import check_freshness, check_source_stability


def _audit():
    return {"_activity_id": "run-1"}


def test_governed_guardrail_public_signatures_are_table_id_driven() -> None:
    assert str(inspect.signature(check_freshness)) == (
        "(table_id: str, *, enabled: bool = True, raise_on_failure: bool = False) -> dict"
    )
    assert str(inspect.signature(check_source_stability)) == (
        "(table_id: str, *, raise_on_failure: bool = False) -> dict"
    )


def test_freshness_resolves_current_observation_from_table_id(monkeypatch) -> None:
    observation = object()
    captured = {}
    monkeypatch.setattr(freshness, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(freshness, "build_runtime_audit_fields", lambda **kwargs: _audit())
    monkeypatch.setattr(
        freshness,
        "get_current_source_observation",
        lambda **kwargs: captured.update(kwargs) or observation,
    )
    monkeypatch.setattr(freshness, "_is_source_observation", lambda value: value is observation)
    monkeypatch.setattr(freshness, "observation_rows", lambda value: [])
    with pytest.raises(ValueError, match="at least one"):
        check_freshness("source-a")
    assert captured == {"environment_name": "dev", "activity_id": "run-1", "table_id": "source-a"}


def test_source_stability_resolves_current_observation_from_table_id(monkeypatch) -> None:
    observation = object()
    captured = {}
    monkeypatch.setattr(stability, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(stability, "build_runtime_audit_fields", lambda **kwargs: _audit())
    monkeypatch.setattr(
        stability,
        "get_current_source_observation",
        lambda **kwargs: captured.update(kwargs) or observation,
    )
    monkeypatch.setattr(stability, "_is_source_observation", lambda value: value is observation)
    monkeypatch.setattr(stability, "_observation_stability", lambda value: {"can_continue": True})
    assert check_source_stability("source-a")["can_continue"] is True
    assert captured == {"environment_name": "dev", "activity_id": "run-1", "table_id": "source-a"}


def test_source_stability_raise_on_failure(monkeypatch) -> None:
    monkeypatch.setattr(stability, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(stability, "build_runtime_audit_fields", lambda **kwargs: _audit())
    monkeypatch.setattr(stability, "get_current_source_observation", lambda **kwargs: object())
    monkeypatch.setattr(stability, "_is_source_observation", lambda value: True)
    monkeypatch.setattr(
        stability, "_observation_stability", lambda value: {"can_continue": False, "reason": "changed"}
    )
    with pytest.raises(RuntimeError, match="changed"):
        check_source_stability("source-a", raise_on_failure=True)


def test_previous_baseline_is_source_scoped_not_target_scoped() -> None:
    now = datetime(2026, 9, 13, tzinfo=UTC)
    rows = [
        {"source_table_id": "source-a", "environment_name": "dev", "observation_status": "committed", "_committed_at": now, "target_table_id": "target-a"},
        {"source_table_id": "source-b", "environment_name": "dev", "observation_status": "committed", "_committed_at": now, "target_table_id": "target-b"},
    ]
    assert stability._previous_observation(
        rows, source_table_id="source-a", environment_name="dev", committed_at=datetime.max.replace(tzinfo=UTC)
    ) == [rows[0]]
