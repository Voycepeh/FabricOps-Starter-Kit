"""Focused tests for exact Data Contract preflight validation."""
# ruff: noqa: D101, D102, D103

from __future__ import annotations

import importlib
import inspect

import pytest

from fabricops_kit import validate_data_contract
from fabricops_kit.pipeline import shared

pytestmark = pytest.mark.unit
module = importlib.import_module("fabricops_kit.pipeline.validate_data_contract")


class Spark:
    def createDataFrame(self, rows, schema=None):
        del schema
        return list(rows)


def _install(monkeypatch, *, rules, schema_status="passed", dq_status="passed"):
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
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "prod", {"env": "prod"}))
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


def test_preflight_validates_frozen_inactive_exact_version_and_persists_identity(monkeypatch):
    rules = [
        {"guardrail_type": "schema", "guardrail_rule_id": "schema-1", "guardrail_version": 1},
        {"guardrail_type": "data_quality", "guardrail_rule_id": "dq-1", "guardrail_version": 1},
    ]
    writes = _install(monkeypatch, rules=rules)

    result = validate_data_contract(
        table_id="table-a", contract_id="contract-a", contract_version=2,
        dataframe=object(), spark_session=Spark(), run_id="run-1", verbose=False,
    )

    assert result["can_activate"] is True
    assert result["failed_values"] == "caller-owned-details"
    assert (result["table_id"], result["contract_id"], result["contract_version"]) == ("table-a", "contract-a", 2)
    assert result["environment_name"] == "prod"
    assert all(write["execution_type"] == "preflight" for write in writes)
    assert all(write["table_id"] == "table-a" and write["contract_id"] == "contract-a" for write in writes)


def test_block_failure_blocks_preflight_while_warn_failure_can_activate(monkeypatch):
    rules = [{"guardrail_type": "schema", "guardrail_rule_id": "schema-1", "guardrail_version": 1}]
    _install(monkeypatch, rules=rules, schema_status="failed")
    blocked = validate_data_contract(table_id="table-a", contract_id="contract-a", contract_version=2,
                                     dataframe=object(), spark_session=Spark(), verbose=False)
    assert blocked["can_activate"] is False
    assert blocked["blocked"] == 1

    _install(monkeypatch, rules=rules, schema_status="warning")
    warned = validate_data_contract(table_id="table-a", contract_id="contract-a", contract_version=2,
                                    dataframe=object(), spark_session=Spark(), verbose=False)
    assert warned["can_activate"] is True
    assert warned["warnings"] == 1


def test_operational_rule_is_not_falsely_passed(monkeypatch):
    rules = [{"guardrail_type": "freshness", "guardrail_rule_id": "fresh-1", "guardrail_version": 1, "action": "Warn"}]
    writes = _install(monkeypatch, rules=rules)

    result = validate_data_contract(table_id="table-a", contract_id="contract-a", contract_version=2,
                                    dataframe=object(), spark_session=Spark(), verbose=False)

    assert result["not_evaluated"] == 1
    assert result["can_activate"] is False
    assert result["outcomes"][0]["status"] == "not_evaluated"
    assert result["outcomes"][0]["reason_code"] == "standalone_preflight_context_unavailable"
    assert writes[0]["result"]["status"] == "not_evaluated"


def test_prod_runtime_resolution_still_requires_active_contract(monkeypatch):
    called = []
    monkeypatch.setattr(shared, "resolve_active_data_contract", lambda *a, **k: called.append(k) or {"status": "active"})

    assert shared.resolve_pipeline_data_contract(object(), "prod", "table-a") == {"status": "active"}
    assert called == [{"spark_session": None, "required": True}]


def test_preflight_has_no_business_table_write_path():
    source = inspect.getsource(module)

    assert "pipeline_write(" not in source
    assert "write_lakehouse_table" not in source
