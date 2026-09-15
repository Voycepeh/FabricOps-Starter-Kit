"""Tests for pre-write Guardrail lifecycle readiness."""
# ruff: noqa: D103

from importlib import import_module

import pytest

pytestmark = pytest.mark.unit

coverage_module = import_module("fabricops_kit.pipeline.check_guardrail_coverage")


def _rule(rule_id: str, guardrail_type: str) -> dict:
    return {
        "guardrail_rule_id": rule_id,
        "guardrail_type": guardrail_type,
        "is_active": True,
    }


def _patch_runtime(monkeypatch, *, contracts, rules, evidence=None, env="dev"):
    monkeypatch.setattr(coverage_module, "resolve_fabric_context", lambda: ("config", env, {}))
    monkeypatch.setattr(coverage_module, "get_spark_session", lambda: "spark")
    monkeypatch.setattr(
        coverage_module,
        "resolve_catalogue_table_identity",
        lambda _config, _env, table_id, **_kwargs: {"table_name": table_id},
    )
    monkeypatch.setattr(
        coverage_module,
        "resolve_pipeline_data_contract",
        lambda _config, _env, table_id, **_kwargs: contracts.get(table_id),
    )
    monkeypatch.setattr(
        coverage_module,
        "load_table_guardrail_rules",
        lambda _config, _env, *, table_id, **_kwargs: rules.get(table_id, []),
    )
    monkeypatch.setattr(
        coverage_module,
        "build_runtime_audit_fields",
        lambda **_kwargs: {"_activity_id": "activity-1"},
    )
    monkeypatch.setattr(
        coverage_module,
        "_current_activity_results",
        lambda **_kwargs: list(evidence or []),
    )


def test_development_baseline_skips_when_no_contracts_are_selected(monkeypatch):
    _patch_runtime(monkeypatch, contracts={}, rules={})

    result = coverage_module.check_guardrail_coverage(
        target_table_id="target",
        source_table_ids=["source"],
        verbose=False,
    )

    assert result["status"] == "skipped"
    assert result["can_continue"] is True
    assert result["reason"] == "No Data Contracts selected; Development baseline run."


def test_selected_contracts_need_only_one_applicable_guardrail_each(monkeypatch):
    rules = {
        "source": [_rule("source-schema", "schema")],
        "target": [_rule("target-schema", "schema")],
    }
    evidence = [
        {"guardrail_rule_id": "source-schema"},
        {"guardrail_rule_id": "target-schema"},
    ]
    _patch_runtime(
        monkeypatch,
        contracts={"source": {"contract_id": "source-contract"}, "target": {"contract_id": "target-contract"}},
        rules=rules,
        evidence=evidence,
    )

    result = coverage_module.check_guardrail_coverage(
        target_table_id="target",
        source_table_ids=["source"],
        verbose=False,
    )

    assert result["status"] == "passed"
    assert result["can_continue"] is True
    assert [item["applicable_guardrail_count"] for item in result["readiness"]] == [1, 1]


def test_selected_contract_without_any_active_guardrail_is_not_ready(monkeypatch):
    _patch_runtime(
        monkeypatch,
        contracts={"source": {"contract_id": "source-contract"}, "target": {"contract_id": "target-contract"}},
        rules={"source": [], "target": [_rule("target-schema", "schema")]},
        evidence=[{"guardrail_rule_id": "target-schema"}],
    )

    with pytest.raises(RuntimeError, match="source / no active Guardrail"):
        coverage_module.check_guardrail_coverage(
            target_table_id="target",
            source_table_ids=["source"],
            verbose=False,
        )


def test_partial_contract_selection_is_not_lifecycle_ready(monkeypatch):
    _patch_runtime(
        monkeypatch,
        contracts={"target": {"contract_id": "target-contract"}},
        rules={"target": [_rule("target-schema", "schema")]},
        evidence=[{"guardrail_rule_id": "target-schema"}],
    )

    with pytest.raises(RuntimeError, match="source / no selected Data Contract"):
        coverage_module.check_guardrail_coverage(
            target_table_id="target",
            source_table_ids=["source"],
            verbose=False,
        )


def test_data_quality_uses_canonical_guardrail_type_and_requires_evidence(monkeypatch):
    _patch_runtime(
        monkeypatch,
        contracts={"source": {"contract_id": "source-contract"}, "target": {"contract_id": "target-contract"}},
        rules={
            "source": [_rule("source-dq", "data_quality")],
            "target": [_rule("target-dq", "data_quality")],
        },
        evidence=[{"guardrail_rule_id": "source-dq"}],
    )

    with pytest.raises(RuntimeError, match="target / Data Quality not evaluated"):
        coverage_module.check_guardrail_coverage(
            target_table_id="target",
            source_table_ids=["source"],
            verbose=False,
        )


def test_source_drift_evidence_is_scoped_to_the_target(monkeypatch):
    _patch_runtime(
        monkeypatch,
        contracts={"source": {"contract_id": "source-contract"}, "target": {"contract_id": "target-contract"}},
        rules={
            "source": [_rule("source-drift", "source_drift")],
            "target": [_rule("target-schema", "schema")],
        },
        evidence=[
            {
                "guardrail_rule_id": "source-drift",
                "result_payload_json": '{"source_table_id":"source","target_table_id":"other-target"}',
            },
            {"guardrail_rule_id": "target-schema"},
        ],
    )

    with pytest.raises(RuntimeError, match="source / Source Drift not evaluated"):
        coverage_module.check_guardrail_coverage(
            target_table_id="target",
            source_table_ids=["source"],
            verbose=False,
        )
