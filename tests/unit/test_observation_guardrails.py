"""Tests for table-id-driven observation Guardrails."""

# ruff: noqa: D103
from __future__ import annotations

import importlib
import inspect
from datetime import UTC, datetime

import pytest

freshness = importlib.import_module("fabricops_kit.pipeline.check_freshness")
drift = importlib.import_module("fabricops_kit.pipeline.check_source_drift")
from fabricops_kit import check_freshness, check_source_drift
from fabricops_kit.pipeline import shared


def test_governed_guardrail_public_signatures_are_relationship_safe() -> None:
    assert str(inspect.signature(check_freshness)) == (
        "(table_id: str, *, enabled: bool = True, raise_on_failure: bool = False, spark_session=None, verbose: bool = True) -> dict"
    )
    assert str(inspect.signature(check_source_drift)) == (
        "(source_table_id: str, *, target_table_id: str, enabled: bool = True, raise_on_failure: bool = False, spark_session=None, verbose: bool = True) -> dict"
    )


def test_source_drift_resolves_source_processing(monkeypatch) -> None:
    calls = []
    processing_table_ids = []
    monkeypatch.setattr(drift, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(
        drift,
        "resolve_catalogue_table_identity",
        lambda _config, _env, table_id, **kwargs: {
            "table_id": f"canonical-{table_id}",
            "load_strategy": "append" if table_id == "source-a" else None,
            "load_strategy_parameters_json": "{}",
        },
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
    result = check_source_drift(
        "source-a", target_table_id="target-a", spark_session="spark", verbose=False
    )
    assert result["can_continue"] is True
    assert calls == [
        {
            "source_table_id": "canonical-source-a",
            "target_table_id": "canonical-target-a",
            "source_processing": {"load_strategy": "append"},
            "spark_session": "spark",
            "raise_on_failure": False,
        }
    ]
    assert processing_table_ids == ["canonical-source-a"]


def test_source_drift_uses_contract_strategy_for_unmanaged_source(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(drift, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(
        drift,
        "resolve_catalogue_table_identity",
        lambda _config, _env, table_id, **kwargs: {
            "table_id": f"canonical-{table_id}",
            "load_strategy": None,
            "load_strategy_parameters_json": "{}",
        },
    )
    monkeypatch.setattr(
        drift,
        "resolve_pipeline_data_contract",
        lambda *args, **kwargs: {
            "contract_id": "contract",
            "contract_payload": {
                "table": {
                    "processing": {
                        "load_strategy": "scd2",
                        "key_columns": ["id"],
                        "effective_column": "effective_at",
                    }
                }
            },
        },
    )
    monkeypatch.setattr(
        drift,
        "resolve_table_processing_definition",
        lambda *args, **kwargs: pytest.fail("unmanaged sources must not use FabricOps writer processing"),
    )
    monkeypatch.setattr(
        drift,
        "check_source_drift_for_target",
        lambda **kwargs: calls.append(kwargs) or {"can_continue": True},
    )

    result = check_source_drift(
        "source-a", target_table_id="target-a", spark_session="spark", verbose=False
    )

    assert result["can_continue"] is True
    assert calls[0]["source_processing"] == {
        "load_strategy": "scd2",
        "key_columns": ["id"],
        "effective_column": "effective_at",
    }


def test_source_drift_requires_contract_strategy_for_unmanaged_source(monkeypatch) -> None:
    monkeypatch.setattr(drift, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(
        drift,
        "resolve_catalogue_table_identity",
        lambda _config, _env, table_id, **kwargs: {
            "table_id": f"canonical-{table_id}",
            "load_strategy": None,
            "load_strategy_parameters_json": "{}",
        },
    )
    monkeypatch.setattr(
        drift,
        "resolve_pipeline_data_contract",
        lambda *args, **kwargs: {
            "contract_id": "contract",
            "contract_payload": {"table": {"processing": {}}},
        },
    )

    with pytest.raises(ValueError, match="selected Data Contract has no valid processing definition"):
        check_source_drift(
            "source-a", target_table_id="target-a", spark_session="spark", verbose=False
        )


def test_explicit_source_drift_check_still_requires_its_rule(monkeypatch) -> None:
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(
        shared,
        "build_runtime_audit_fields",
        lambda **kwargs: {"_activity_id": "run-1"},
    )
    monkeypatch.setattr(shared, "load_table_guardrail_rules", lambda *a, **k: [])

    with pytest.raises(ValueError, match="No active approved Source Drift rule"):
        shared.check_source_drift_for_target(
            source_table_id="source-a",
            target_table_id="target-a",
            source_processing={"load_strategy": "append"},
        )


def _freshness_rule(column: str) -> dict:
    return {
        "guardrail_type": "freshness",
        "table_id": "source-a",
        "is_active": True,
        "rule_type": "max_age",
        "rule_parameters_json": (
            '{"freshness_column":"' + column + '","maximum_age":1,"maximum_age_unit":"days"}'
        ),
        "action": "Block",
        "guardrail_rule_id": "freshness-rule",
        "guardrail_version": 1,
    }


def _run_freshness(monkeypatch, *, freshness_column: str, drift_column: str | None):
    rules = [_freshness_rule(freshness_column)]
    if drift_column:
        rules.append(
            {
                "guardrail_type": "source_drift",
                "rule_parameters_json": (
                    '{"partition_column":"partition_date","change_column":"'
                    + drift_column
                    + '"}'
                ),
            }
        )
    monkeypatch.setattr(freshness, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(freshness, "resolve_pipeline_data_contract", lambda *a, **k: {"contract_id": "c"})
    monkeypatch.setattr(freshness, "build_runtime_audit_fields", lambda **k: {"_activity_id": "run-1"})
    monkeypatch.setattr(freshness, "get_spark_session", lambda: object())
    monkeypatch.setattr(
        freshness,
        "resolve_catalogue_table_identity",
        lambda *a, **k: {"table_id": "source-a"},
    )
    monkeypatch.setattr(freshness, "load_table_guardrail_rules", lambda *a, **k: rules)
    monkeypatch.setattr(
        freshness,
        "select_table_guardrail_rule",
        lambda _rules, *, guardrail_type, **_k: next(
            (rule for rule in rules if rule["guardrail_type"] == guardrail_type), None
        ),
    )
    monkeypatch.setattr(
        freshness,
        "get_current_freshness_evidence",
        lambda **k: {
            "freshness_column": freshness_column,
            "latest_value": datetime.now(UTC).isoformat(),
            "_activity_id": "run-1",
        },
    )
    monkeypatch.setattr(freshness, "write_guardrail_result_row", lambda **k: None)
    return check_freshness("source-a", verbose=False)


def test_freshness_does_not_require_source_drift(monkeypatch) -> None:
    result = _run_freshness(
        monkeypatch, freshness_column="arrived_at", drift_column=None
    )
    assert result["status"] == "passed"
    assert result["freshness_column"] == "arrived_at"


def test_freshness_uses_its_own_column_when_source_drift_differs(monkeypatch) -> None:
    result = _run_freshness(
        monkeypatch, freshness_column="arrived_at", drift_column="changed_at"
    )
    assert result["status"] == "passed"
    assert result["freshness_column"] == "arrived_at"


def test_freshness_and_source_drift_can_share_a_column(monkeypatch) -> None:
    result = _run_freshness(
        monkeypatch, freshness_column="changed_at", drift_column="changed_at"
    )
    assert result["status"] == "passed"
    assert result["freshness_column"] == "changed_at"


class _Store:
    key = "Bronze"
    schema_enabled = False


def _configure_observation_capture(monkeypatch, rules):
    shared._CURRENT_FRESHNESS_EVIDENCE.clear()
    shared._CURRENT_SOURCE_OBSERVATIONS.clear()
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(shared, "get_spark_session", lambda: object())
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
    monkeypatch.setattr(
        shared,
        "resolve_source_drift_observation_columns",
        lambda _rule: (_ for _ in ()).throw(AssertionError("Source Drift was resolved")),
    )

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
    monkeypatch.setattr(
        shared,
        "resolve_freshness_observation_column",
        lambda _rule: (_ for _ in ()).throw(AssertionError("Freshness column was resolved")),
    )

    assert shared.capture_source_observation(table_id="source-a", dataframe=[]) is None
    with pytest.raises(ValueError, match="No current freshness evidence"):
        shared.get_current_freshness_evidence(
            environment_name="dev", activity_id="run-1", table_id="source-a"
        )


def test_freshness_capture_uses_freshness_rule_column(monkeypatch) -> None:
    rule = _freshness_rule("arrived_at")
    _configure_observation_capture(monkeypatch, [rule])

    assert shared.capture_source_observation(
        table_id="source-a",
        dataframe=[{"arrived_at": "2026-09-20", "changed_at": "2020-01-01"}],
    ) is None
    evidence = shared.get_current_freshness_evidence(
        environment_name="dev", activity_id="run-1", table_id="source-a"
    )
    assert evidence["freshness_column"] == "arrived_at"
    assert evidence["latest_value"] == "2026-09-20"
