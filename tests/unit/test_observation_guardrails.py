"""Tests for table-id-driven observation Guardrails."""

# ruff: noqa: D103
from __future__ import annotations

from tests.helpers import call_with_spark

import importlib
import inspect
from datetime import UTC, datetime

import pytest

freshness = importlib.import_module("fabricops_kit.pipeline.check_freshness")
from fabricops_kit.pipeline.check_freshness import check_freshness
from fabricops_kit.pipeline import shared


def test_governed_guardrail_public_signatures_are_relationship_safe() -> None:
    for check in (check_freshness,):
        parameters = inspect.signature(check).parameters
        assert "enabled" not in parameters
        assert "raise_on_failure" not in parameters
        assert "context" in parameters
        assert "execution_type" not in parameters










def _freshness_rule() -> dict:
    return {
        "guardrail_type": "freshness",
        "table_id": "source-a",
        "is_active": True,
        "rule_type": "max_age",
        "rule_parameters_json": (
            '{"evidence_method":"metadata","evaluation_scope":"full_dataset",'
            '"maximum_age":1,"maximum_age_unit":"days"}'
        ),
        "action": "Block",
        "guardrail_rule_id": "freshness-rule",
        "guardrail_version": 1,
    }


def _run_freshness(monkeypatch, *, drift_column: str | None):
    rules = [_freshness_rule()]
    if drift_column:
        rules.append({
            "guardrail_type": "source_drift",
            "rule_parameters_json": (
                '{"partition_column":"partition_date","change_column":"'
                + drift_column + '"}'
            ),
        })
    monkeypatch.setattr(freshness, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(freshness, "resolve_pipeline_data_contract", lambda *a, **k: {"contract_id": "c"})
    monkeypatch.setattr(freshness, "build_runtime_audit_fields", lambda **k: {"_activity_id": "run-1"})
    monkeypatch.setattr(freshness, "get_spark_session", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(
        freshness, "resolve_catalogue_table_identity",
        lambda *a, **k: {"table_id": "source-a"},
    )
    monkeypatch.setattr(freshness, "load_table_guardrail_rules", lambda *a, **k: rules)
    monkeypatch.setattr(
        freshness, "select_table_guardrail_rule",
        lambda _rules, *, guardrail_type, **_k: next(
            (rule for rule in rules if rule["guardrail_type"] == guardrail_type), None
        ),
    )
    monkeypatch.setattr(
        freshness, "get_current_freshness_evidence",
        lambda **k: {
            "evidence_method": "metadata", "evaluation_scope": "full_dataset",
            "outcome": "available", "latest_value": datetime.now(UTC).isoformat(),
            "_activity_id": "run-1",
        },
    )
    monkeypatch.setattr(freshness, "write_guardrail_result_row", lambda **k: None)
    return check_freshness("source-a", verbose=False)


@pytest.mark.parametrize("drift_column", [None, "changed_at"])
def test_metadata_freshness_does_not_depend_on_source_drift(monkeypatch, drift_column):
    result = _run_freshness(monkeypatch, drift_column=drift_column)
    assert result["status"] == "passed"
    assert result["actual"]["evidence_method"] == "metadata"
    assert "freshness_column" not in result["actual"]


class _Store:
    key = "Bronze"
    schema_enabled = False


def _configure_observation_capture(monkeypatch, rules):
    shared._CURRENT_FRESHNESS_EVIDENCE.clear()
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(shared, "get_spark_session", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(
        shared,
        "resolve_catalogue_table_identity",
        lambda *a, **k: {
            "table_id": "source-a",
            "store": "Bronze",
            "schema": None,
            "table_name": "orders",
            "store_type": "lakehouse",
        },
    )
    monkeypatch.setattr(shared, "get_store", lambda *a: _Store())
    monkeypatch.setattr(
        shared,
        "resolve_lakehouse_table_location",
        lambda *_a: ("orders", None, "/orders"),
    )
    monkeypatch.setattr(shared, "load_table_guardrail_rules", lambda *a, **k: rules)
    monkeypatch.setattr(
        shared,
        "select_table_guardrail_rule",
        lambda _rules, *, guardrail_type, **_k: next(
            (rule for rule in rules if rule["guardrail_type"] == guardrail_type), None
        ),
    )
    monkeypatch.setattr(
        shared,
        "build_runtime_audit_fields",
        lambda **k: {"_activity_id": "run-1", "_committed_at": datetime.now(UTC)},
    )


def test_observation_capture_without_source_drift_is_optional(monkeypatch) -> None:
    _configure_observation_capture(monkeypatch, [{"guardrail_type": "schema"}])

    assert shared.capture_source_observation(table_id="source-a", dataframe=[]) is None


def test_static_source_skips_freshness_evidence_capture(monkeypatch) -> None:
    """No-refresh-expected sources do not require or capture a freshness timestamp."""
    rule = {
        "guardrail_type": "freshness",
        "table_id": "source-a",
        "is_active": True,
        "rule_type": "skip",
        "rule_parameters_json": '{"refresh_expectation":"static"}',
        "action": "Warn",
        "guardrail_rule_id": "freshness-static",
        "guardrail_version": 1,
    }
    _configure_observation_capture(monkeypatch, [rule])

    assert shared.capture_source_observation(table_id="source-a", dataframe=[]) is None
    with pytest.raises(ValueError, match="No current freshness evidence"):
        shared.get_current_freshness_evidence(
            workspace_id="dev", activity_id="run-1", table_id="source-a"
        )


def test_freshness_capture_uses_delta_metadata_not_dataframe(monkeypatch):
    """Source Observation reads physical history, not user-supplied date columns."""
    rule = _freshness_rule()
    _configure_observation_capture(monkeypatch, [rule])
    monkeypatch.setattr(shared, "collect_freshness_evidence", lambda parameters, **kwargs: {
        "evidence_method": "metadata", "evaluation_scope": "full_dataset",
        "outcome": "available", "latest_value": "2026-09-20T00:00:00+00:00",
        "source": kwargs["source"], "scan_required": False,
    })
    assert shared.capture_source_observation(
        table_id="source-a",
        dataframe=[{"arrived_at": "2026-09-20", "changed_at": "2020-01-01"}],
    ) is None
    evidence = shared.get_current_freshness_evidence(
        workspace_id="dev", activity_id="run-1", table_id="source-a",
    )
    assert evidence["evidence_method"] == "metadata"
    assert evidence["source"]["resolved_path"] == "/orders"
    assert evidence["scan_required"] is False
