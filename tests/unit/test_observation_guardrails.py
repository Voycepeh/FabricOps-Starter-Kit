"""Tests for table-id-driven observation Guardrails."""

# ruff: noqa: D103
from __future__ import annotations

import importlib
import inspect

freshness = importlib.import_module("fabricops_kit.pipeline.check_freshness")
stability = importlib.import_module("fabricops_kit.pipeline.check_source_stability")
from fabricops_kit import check_freshness, check_source_stability


def test_governed_guardrail_public_signatures_are_relationship_safe() -> None:
    assert str(inspect.signature(check_freshness)) == (
        "(table_id: str, *, enabled: bool = True, raise_on_failure: bool = False, verbose: bool = True) -> dict"
    )
    assert str(inspect.signature(check_source_stability)) == (
        "(source_table_id: str, *, target_table_id: str, enabled: bool = True, raise_on_failure: bool = False, verbose: bool = True) -> dict"
    )


def test_source_stability_resolves_target_processing(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(stability, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(
        stability,
        "resolve_catalogue_table_identity",
        lambda *args, **kwargs: {"table_id": "target-canonical"},
    )
    monkeypatch.setattr(
        stability,
        "resolve_table_processing_definition",
        lambda *args, **kwargs: {"load_strategy": "append"},
    )
    monkeypatch.setattr(
        stability,
        "check_source_stability_for_target",
        lambda **kwargs: calls.append(kwargs) or {"can_continue": True},
    )
    result = check_source_stability("source-a", target_table_id="target-a")
    assert result["can_continue"] is True
    assert calls == [
        {
            "source_table_id": "source-a",
            "target_table_id": "target-canonical",
            "target_processing": {"load_strategy": "append"},
            "raise_on_failure": False,
        }
    ]
