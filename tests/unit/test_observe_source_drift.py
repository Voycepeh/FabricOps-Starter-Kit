"""Pipeline observation controls, consolidated decisions and execution isolation."""
# ruff: noqa: D103
import importlib
import json
from threading import RLock
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fabricops_kit.pipeline import shared

observe = importlib.import_module("fabricops_kit.pipeline.observe_source_drift")


@pytest.fixture
def runtime(monkeypatch):
    identities = {name: dict(table_id=name, table_name=name + "_readable", store="Bronze", store_type="lakehouse")
                  for name in ("orders", "products", "customers")}
    plan = SimpleNamespace(plan_id="actual-run", pipeline_id="actual-pipeline", workspace_id="actual-workspace",
        evidence={"failures": []}, results=[], lock=RLock(), runtime_context={"config": object()},
        participants_json=json.dumps(identities))
    session = SimpleNamespace(plan=plan, spark=object(), sources=[{"table_id": name} for name in identities])
    monkeypatch.setattr(observe, "current_pipeline_session", lambda: session)
    writes = []
    monkeypatch.setattr(observe, "write_guardrail_result_row", lambda **kwargs: writes.append(kwargs))
    monkeypatch.setattr(observe, "persist_pipeline_run", Mock())
    monkeypatch.setattr(shared, "metadata_table_physical_schema", lambda *args: "actual_engineering")
    return SimpleNamespace(plan=plan, session=session, writes=writes)


def outcome(status="passed"):
    return dict(status=status, added_count=1, modified_count=int(status == "failed"), removed_count=0,
                ambiguous_count=0, reason="Historical source comparison.")


@pytest.mark.parametrize("block", [True, False])
def test_all_sources_evaluated_and_persisted_before_decision(runtime, monkeypatch, capsys, block):
    calls = []
    monkeypatch.setattr(observe, "observe_full_source", lambda identity, **kwargs:
                        calls.append(identity["table_id"]) or outcome("failed" if identity["table_id"] == "orders" else "passed"))
    if block:
        with pytest.raises(RuntimeError) as error:
            observe.observe_source_drift(block=block)
        result = error.value.result
        assert runtime.plan.evidence["failures"] == [{"code": "source_drift_blocked"}]
    else:
        result = observe.observe_source_drift(block=block)
        assert result["status"] == "warning"
    assert calls == ["orders", "products", "customers"]
    assert len(runtime.writes) == 4
    assert runtime.writes[-1]["rule_type"] == "pipeline_observation"
    assert runtime.writes[-1]["result"]["can_continue"] is (not block)
    assert result["can_continue"] is (not block)
    assert result["run_id"] == "actual-run" and result["pipeline_id"] == "actual-pipeline"
    assert result["added_count"] == 3 and result["modified_count"] == 1
    output = capsys.readouterr().out
    assert "orders_readable" in output and "Elapsed:" in output
    assert "actual-run" in output and "actual-pipeline" in output
    query = result["sources"][0]["investigation_query"]
    assert "SELECT *" not in query.upper() and "actual_engineering" in query
    for value in ("actual-run", "actual-pipeline", "actual-workspace", "orders"):
        assert value in query
    compile(query, "investigate", "exec")


@pytest.mark.parametrize("days", [0, -1, True, False, "1", 1.5])
def test_invalid_intervals(days):
    with pytest.raises(ValueError, match="positive integer"):
        observe.observe_source_drift(source_observation_days=days)


@pytest.mark.parametrize("kwargs", [{"block": 1}, {"observe_immediately": "yes"}])
def test_strict_boolean_controls(kwargs):
    with pytest.raises(ValueError, match="booleans"):
        observe.observe_source_drift(**kwargs)


def test_repeated_reads_scan_once_and_not_due_is_skipped(runtime, monkeypatch):
    runtime.session.sources = [{"table_id": "orders"}] * 3
    calls = []
    def check(identity, **kwargs):
        calls.append(kwargs)
        return {**outcome("skipped"), "added_count": None, "modified_count": None, "removed_count": None, "ambiguous_count": None}
    monkeypatch.setattr(observe, "observe_full_source", check)
    result = observe.observe_source_drift(observe_immediately=False, source_observation_days=1)
    assert len(calls) == 1 and not calls[0]["observe_immediately"]
    assert result["status"] == "skipped" and result["added_count"] is None


def test_unavailable_source_is_not_clean_or_accepted(runtime, monkeypatch):
    calls = []
    def check(identity, **kwargs):
        calls.append(identity["table_id"])
        if identity["table_id"] == "products":
            raise PermissionError("private connector details")
        runtime.plan.evidence.setdefault("source_drift_candidates", {})[identity["table_id"]] = {}
        return outcome()
    monkeypatch.setattr(observe, "observe_full_source", check)
    result = observe.observe_source_drift(block=False)
    assert result["status"] == "evaluation_failed" and result["can_continue"]
    assert result["added_count"] is None and len(calls) == 3
    assert runtime.plan.evidence["source_drift_candidates"] == {}
    assert "private connector details" not in json.dumps(result)


def test_read_after_observation_invalidates_coverage(runtime, monkeypatch):
    session = shared.PipelineSession(runtime.plan, object())
    monkeypatch.setattr(session, "refresh", lambda: None)
    runtime.plan.evidence.update(source_drift_results=[{}], source_drift_candidates={"orders": {}})
    session.register_source({"table_id": "products", "execution_plan_id": "actual-run"})
    assert runtime.plan.evidence["source_drift_coverage_invalid"]
    assert runtime.plan.evidence["source_drift_candidates"] == {}
    assert runtime.plan.evidence["source_drift_results"][0]["coverage_superseded_by_read"]


def test_no_sources_reports_skip(runtime):
    runtime.session.sources = []
    assert observe.observe_source_drift()["status"] == "skipped"


def test_setup_owns_no_observation_configuration():
    import inspect
    from fabricops_kit import setup_pipeline
    assert list(inspect.signature(setup_pipeline).parameters) == ["pipeline_mode"]
    with pytest.raises(TypeError):
        setup_pipeline(observe_source=True)


def test_contract_no_longer_accepts_table_source_drift():
    from fabricops_kit.data_contract.shared import GUARDRAIL_TYPES
    assert "source_drift" not in GUARDRAIL_TYPES


def test_processing_state_upgrade_is_strictly_additive():
    from fabricops_kit.config.setup_metadata_tables import _validate_existing_metadata_schema
    schema = shared.metadata_table_schema_registry()[shared._PROCESSING_STATE_TABLE]
    old = type(schema)([f for f in schema if f.name != "snapshot_payload_json"])
    assert _validate_existing_metadata_schema(shared._PROCESSING_STATE_TABLE, old, schema, allow_missing=True) == ["snapshot_payload_json"]
    missing_identity = type(schema)([f for f in old if f.name != "run_id"])
    with pytest.raises(ValueError, match="Incompatible"):
        _validate_existing_metadata_schema(shared._PROCESSING_STATE_TABLE, missing_identity, schema, allow_missing=True)


def test_retired_source_drift_cannot_be_authored(monkeypatch):
    from fabricops_kit.data_contract import shared as contracts
    monkeypatch.setattr(contracts, "build_runtime_audit_fields", lambda **kwargs: {})
    with pytest.raises(ValueError, match="guardrail_type must be"):
        contracts.canonical_guardrail_rule_record({"contract_id": "contract", "contract_version": 1,
            "guardrail_type": "source_drift"}, config=object(), active_workspace_id="workspace")


def test_consolidated_persistence_failure_cannot_accept_history(runtime, monkeypatch):
    def check(identity, **kwargs):
        runtime.plan.evidence.setdefault("source_drift_candidates", {})[identity["table_id"]] = {}
        return outcome()
    monkeypatch.setattr(observe, "observe_full_source", check)
    def persist(**kwargs):
        if kwargs["rule_type"] == "pipeline_observation":
            raise OSError("metadata unavailable")
    monkeypatch.setattr(observe, "write_guardrail_result_row", persist)
    result = observe.observe_source_drift(block=False)
    assert result["status"] == "evaluation_failed" and result["can_continue"]
    assert runtime.plan.evidence["source_drift_candidates"] == {}
    assert "Consolidated result persistence failed" in result["reason"]
