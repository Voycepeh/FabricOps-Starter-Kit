"""Tests for table-id-driven observation Guardrails."""

# ruff: noqa: D103
from __future__ import annotations

import importlib
import inspect

freshness = importlib.import_module("fabricops_kit.pipeline.check_freshness")
drift = importlib.import_module("fabricops_kit.pipeline.check_source_drift")
from fabricops_kit import check_freshness, check_source_drift


def test_governed_guardrail_public_signatures_are_relationship_safe() -> None:
    assert str(inspect.signature(check_freshness)) == (
        "(table_id: str, *, enabled: bool = True, raise_on_failure: bool = False, verbose: bool = True) -> dict"
    )
    assert str(inspect.signature(check_source_drift)) == (
        "(source_table_id: str, *, target_table_id: str, enabled: bool = True, raise_on_failure: bool = False, verbose: bool = True) -> dict"
    )


def test_source_drift_resolves_source_processing(monkeypatch) -> None:
    calls = []
    processing_table_ids = []
    monkeypatch.setattr(drift, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(
        drift,
        "resolve_catalogue_table_identity",
        lambda _config, _env, table_id, **kwargs: {"table_id": f"canonical-{table_id}"},
    )
    monkeypatch.setattr(
        drift,
        "resolve_table_processing_definition",
        lambda _config, _env, table_id, **kwargs: processing_table_ids.append(table_id)
        or {"load_strategy": "append"},
    )
    monkeypatch.setattr(
        drift, "resolve_pipeline_data_contract", lambda *args, **kwargs: {"contract_id": "contract"}
    )
    monkeypatch.setattr(
        drift,
        "check_source_drift_for_target",
        lambda **kwargs: calls.append(kwargs) or {"can_continue": True},
    )
    result = check_source_drift("source-a", target_table_id="target-a", verbose=False)
    assert result["can_continue"] is True
    assert calls == [
        {
            "source_table_id": "canonical-source-a",
            "target_table_id": "canonical-target-a",
            "source_processing": {"load_strategy": "append"},
            "raise_on_failure": False,
        }
    ]
    assert processing_table_ids == ["canonical-source-a"]
