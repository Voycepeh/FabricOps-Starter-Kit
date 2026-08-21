"""Tests for manual Data Contract activation and frozen rule resolution."""

from __future__ import annotations

import json

import pytest

from fabricops_kit.pipeline import shared as pipeline_shared
from fabricops_kit.widgets.widget_activate_data_contract import _activation_states, _compact_review, _payload, _selected_contract

pytestmark = pytest.mark.unit


def _contract(version: int, *, status: str = "draft", active: bool = False, table_id: str = "orders", rule: str = "rule-a"):
    payload = {
        "contract": {"contract_id": "contract", "contract_version": version, "status": "draft"},
        "agreement": {"agreement_id": "agreement", "agreement_version": "1", "agreement_name": "Orders"},
        "table": {"table_id": table_id, "table_name": "orders", "schema_name": "sales", "columns": [{"column_name": "id", "data_type": "long"}]},
        "enrichment": {"table": [], "columns": []},
        "guardrails": [{"guardrail_rule_id": rule, "guardrail_version": version, "guardrail_type": "dq", "rule_id": rule, "rule_type": "not_null", "rule_parameters": {"columns": ["id"]}, "severity": "error"}],
        "approved_usages": ["analytics"],
    }
    return {"contract_id": "contract", "contract_version": version, "table_id": table_id, "status": status, "is_active": active, "contract_payload_json": json.dumps(payload)}


def test_activation_supersedes_previous_version_without_mutating_frozen_fields():
    """Change only lifecycle fields when a newer frozen version is activated."""
    rows = [_contract(1, status="active", active=True), _contract(2), _contract(3)]
    before = [(row["contract_version"], row["contract_payload_json"]) for row in rows]
    changes = _activation_states(rows, rows[1])
    assert changes == [
        {"contract_id": "contract", "contract_version": 1, "status": "superseded", "is_active": False},
        {"contract_id": "contract", "contract_version": 2, "status": "active", "is_active": True},
    ]
    assert rows[2]["status"] == "draft"
    assert [(row["contract_version"], row["contract_payload_json"]) for row in rows] == before


def test_activation_is_idempotent_and_rejected_or_mismatched_versions_fail():
    """Avoid redundant writes and reject ineligible or invalid selections."""
    active = _contract(1, status="active", active=True)
    assert _activation_states([active], active) == []
    with pytest.raises(ValueError, match="Rejected"):
        _selected_contract([_contract(2, status="rejected")], "orders", "contract", 2)
    with pytest.raises(ValueError, match="does not belong"):
        _selected_contract([_contract(2, table_id="customers")], "orders", "contract", 2)
    with pytest.raises(ValueError, match="does not exist"):
        _selected_contract([], "orders", "contract", 99)


def test_review_and_guardrails_come_only_from_frozen_payload():
    """Build review and runtime rules from the immutable contract document."""
    row = _contract(1)
    payload = _payload(row)
    assert _compact_review(payload)["schema_columns"] == 1
    contract = {**row, "contract_payload": payload}
    rules = pipeline_shared.contract_guardrail_rows(contract, environment_name="prod")
    assert rules[0]["guardrail_rule_id"] == "rule-a"
    assert json.loads(rules[0]["rule_parameters_json"]) == {"columns": ["id"]}


class _Frame:
    def __init__(self, rows):
        self._rows = rows

    def collect(self):
        return self._rows


def test_active_resolver_handles_zero_one_and_multiple_without_selecting_newest(monkeypatch):
    """Honor only explicit activation and reject ambiguous metadata state."""
    rows = [_contract(1, status="active", active=True), _contract(2)]
    monkeypatch.setattr(pipeline_shared, "read_lakehouse_table_core", lambda *args, **kwargs: _Frame(rows))
    resolved = pipeline_shared.resolve_active_data_contract({}, "prod", "orders")
    assert resolved["contract_version"] == 1
    rows[1].update(status="active", is_active=True)
    with pytest.raises(RuntimeError, match="multiple active"):
        pipeline_shared.resolve_active_data_contract({}, "prod", "orders")
    rows[:] = [_contract(2)]
    with pytest.raises(ValueError, match="No active"):
        pipeline_shared.resolve_active_data_contract({}, "prod", "orders", required=False)
    rows[:] = [_contract(2, table_id="customers")]
    assert pipeline_shared.resolve_active_data_contract({}, "prod", "orders", required=False) is None
    with pytest.raises(ValueError, match="No active"):
        pipeline_shared.resolve_active_data_contract({}, "prod", "orders")
