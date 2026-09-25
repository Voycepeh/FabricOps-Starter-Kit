"""Focused tests for exact Data Contract validation."""
# ruff: noqa: D101, D102, D103

from __future__ import annotations

import importlib
import inspect

import pytest

from fabricops_kit.pipeline import shared
from fabricops_kit.pipeline.validate_data_contract import _validate_data_contract

pytestmark = pytest.mark.unit
module = importlib.import_module("fabricops_kit.pipeline.validate_data_contract")


class Spark:
    def createDataFrame(self, rows, schema=None):
        del schema
        return list(rows)


def _install(monkeypatch, *, rules, schema_status="passed", dq_status="passed", environment="prod"):
    writes = []
    contract = {
        "contract_id": "contract-a",
        "contract_version": 2,
        "status": "frozen",
        "contract_payload": {"contract": {}, "table": {}, "guardrails": []},
    }
    identity = {
        "table_id": "table-a", "store": "Silver", "store_type": "lakehouse",
        "schema": "dbo", "table_name": "orders",
    }
    monkeypatch.setattr(
        module,
        "resolve_fabric_context",
        lambda: (object(), environment, {"env": environment}),
    )
    monkeypatch.setattr(module, "build_runtime_audit_fields", lambda **kwargs: {"_activity_id": "activity-1"})
    monkeypatch.setattr(module, "resolve_catalogue_table_identity", lambda *a, **k: identity)
    monkeypatch.setattr(module, "resolve_data_contract_version", lambda *a, **k: contract)
    monkeypatch.setattr(module, "contract_guardrail_rows", lambda *a, **k: rules)
    monkeypatch.setattr(module, "schema_check_core", lambda *a, **k: {
        "guardrail_rule_id": "schema-1", "guardrail_version": 1,
        "status": schema_status, "can_continue": schema_status != "failed",
        "severity": "blocking", "rule_type": "strict",
    })
    monkeypatch.setattr(module, "check_dq_runtime", lambda *a, **k: {
        "checks": [{"guardrail_rule_id": "dq-1", "status": dq_status}],
        "failed_values": "caller-owned-details", "run_id": "run-1",
    })
    monkeypatch.setattr(module, "write_guardrail_result_row", lambda **kwargs: writes.append(kwargs))
    return writes


@pytest.mark.parametrize("environment", ["dev", "prod"])
def test_validate_mode_accepts_frozen_inactive_exact_version_and_persists_identity(monkeypatch, environment):
    rules = [
        {"guardrail_type": "schema", "guardrail_rule_id": "schema-1", "guardrail_version": 1},
        {"guardrail_type": "data_quality", "guardrail_rule_id": "dq-1", "guardrail_version": 1},
    ]
    writes = _install(monkeypatch, rules=rules, environment=environment)

    result = _validate_data_contract(
        table_id="table-a", contract_id="contract-a", contract_version=2,
        dataframe=object(), spark_session=Spark(), run_id="run-1", verbose=False,
    )

    assert result["validation_passed"] is True
    assert result["failed_values"] == "caller-owned-details"
    assert (result["table_id"], result["contract_id"], result["contract_version"]) == ("table-a", "contract-a", 2)
    assert result["environment_name"] == environment
    assert all(write["execution_type"] == "validate" for write in writes)
    assert all(write["table_id"] == "table-a" and write["contract_id"] == "contract-a" for write in writes)


def test_block_failure_fails_validation_while_warn_failure_preserves_success(monkeypatch):
    rules = [{"guardrail_type": "schema", "guardrail_rule_id": "schema-1", "guardrail_version": 1}]
    _install(monkeypatch, rules=rules, schema_status="failed")
    blocked = _validate_data_contract(table_id="table-a", contract_id="contract-a", contract_version=2,
                                     dataframe=object(), spark_session=Spark(), verbose=False)
    assert blocked["validation_passed"] is False
    assert blocked["blocked"] == 1

    _install(monkeypatch, rules=rules, schema_status="warning")
    warned = _validate_data_contract(table_id="table-a", contract_id="contract-a", contract_version=2,
                                    dataframe=object(), spark_session=Spark(), verbose=False)
    assert warned["validation_passed"] is True
    assert warned["warnings"] == 1


def test_enforcement_only_freshness_is_neither_passed_nor_activation_blocking(monkeypatch):
    rules = [
        {"guardrail_type": "schema", "guardrail_rule_id": "schema-1", "guardrail_version": 1},
        {"guardrail_type": "data_quality", "guardrail_rule_id": "dq-1", "guardrail_version": 1},
        {"guardrail_type": "freshness", "guardrail_rule_id": "fresh-1", "guardrail_version": 1, "action": "Block"},
    ]
    writes = _install(monkeypatch, rules=rules)

    result = _validate_data_contract(table_id="table-a", contract_id="contract-a", contract_version=2,
                                    dataframe=object(), spark_session=Spark(), verbose=False)

    assert result["passed"] == 2
    assert result["not_applicable"] == 1
    assert result["validation_passed"] is True
    freshness = next(outcome for outcome in result["outcomes"] if outcome.get("guardrail_type") == "freshness")
    assert freshness["status"] == "not_applicable"
    assert freshness["validation_applicability"] == "enforcement_only"
    assert freshness["reason_code"] == "enforcement_context_required"
    assert writes[-1]["result"]["status"] == "not_applicable"


def test_prod_enforcement_resolution_still_requires_active_contract(monkeypatch):
    called = []
    monkeypatch.setattr(shared, "resolve_active_data_contract", lambda *a, **k: called.append(k) or {"status": "active"})

    assert shared.resolve_pipeline_data_contract(object(), "prod", "table-a") == {"status": "active"}
    assert called == [{"spark_session": None, "required": True}]


def test_validation_has_no_business_table_write_path():
    source = inspect.getsource(module)

    assert "pipeline_write(" not in source
    assert "write_lakehouse_table" not in source


def test_validation_service_is_internal_not_a_package_export():
    """Keep contract validation orchestration behind the Pipeline template."""
    import fabricops_kit
    import fabricops_kit.pipeline

    assert "validate_data_contract" not in fabricops_kit.__all__
    assert "validate_data_contract" not in fabricops_kit.pipeline.__all__
