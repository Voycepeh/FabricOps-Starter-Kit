"""Tests for manual Data Contract activation and frozen rule resolution."""

from __future__ import annotations

import json

import pytest

from fabricops_kit.pipeline import shared as pipeline_shared
from fabricops_kit.widgets.shared import _contract_activation_changes
from fabricops_kit.widgets.widget_activate_data_contract import _compact_review, _payload, _selected_contract

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
    changes = _contract_activation_changes(rows, rows[1])
    assert changes == [
        {"contract_id": "contract", "contract_version": 1, "status": "superseded", "is_active": False},
        {"contract_id": "contract", "contract_version": 2, "status": "active", "is_active": True},
    ]
    assert rows[2]["status"] == "draft"
    assert [(row["contract_version"], row["contract_payload_json"]) for row in rows] == before


def test_activation_is_idempotent_and_rejected_or_mismatched_versions_fail():
    """Avoid redundant writes and reject ineligible or invalid selections."""
    active = _contract(1, status="active", active=True)
    assert _contract_activation_changes([active], active) == []
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
    rules = pipeline_shared.contract_guardrail_rows(
        contract, environment_name="prod", metadata_table_key="runtime-orders",
    )
    assert rules[0]["guardrail_rule_id"] == "rule-a"
    assert rules[0]["metadata_table_key"] == "runtime-orders"
    assert json.loads(rules[0]["rule_parameters_json"]) == {"columns": ["id"]}


class _Frame:
    def __init__(self, rows):
        self._rows = rows

    def collect(self):
        return self._rows


class _Spark:
    def createDataFrame(self, rows):
        return _Frame(rows)


def test_development_uses_mutable_guardrails_even_with_draft_or_active_contracts(monkeypatch):
    """Never consult or pin Development checks to saved Data Contracts."""
    authoring = _Frame([{"guardrail_rule_id": "new-development-rule"}])
    monkeypatch.setattr(pipeline_shared, "read_lakehouse_table_core", lambda name, **kwargs: authoring)
    monkeypatch.setattr(
        pipeline_shared, "resolve_active_data_contract",
        lambda *args, **kwargs: pytest.fail("Development must not resolve a Data Contract"),
    )
    resolved = pipeline_shared.load_table_guardrail_rules(
        {}, "dev", spark_session=_Spark(), table_id="catalogue-orders",
        metadata_table_key="runtime-orders",
    )
    assert resolved is authoring


def test_production_resolves_physical_table_through_catalogue_to_active_contract(monkeypatch):
    """Follow physical identity to Catalogue table_id before loading frozen rules."""
    catalogue_table_id = "canonical-catalogue-orders"
    catalogue = _Frame([{
        "metadata_level": "table", "table_id": catalogue_table_id,
        "environment_name": "prod", "store_type": "lakehouse", "layer": "source",
        "schema_name": "sales", "table_name": "orders", "is_active": True,
    }])
    monkeypatch.setattr(pipeline_shared, "read_lakehouse_table_core", lambda *args, **kwargs: catalogue)
    resolved_id = pipeline_shared.resolve_catalogue_table_id(
        {}, "prod", store_type="lakehouse", layer="source", schema_name="sales",
        table_name="orders", spark_session=_Spark(),
    )
    assert resolved_id == catalogue_table_id

    contract = _contract(3, status="active", active=True, table_id=catalogue_table_id, rule="frozen-rule")
    captured = {}
    def active_contract(_config, _env, table_id, **_kwargs):
        captured["table_id"] = table_id
        captured["required"] = _kwargs["required"]
        return {**contract, "contract_payload": json.loads(contract["contract_payload_json"])}
    monkeypatch.setattr(pipeline_shared, "resolve_active_data_contract", active_contract)
    rules = pipeline_shared.load_table_guardrail_rules(
        {}, "prod", spark_session=_Spark(), table_id=resolved_id,
        metadata_table_key="legacy-runtime-key",
    ).collect()
    assert captured["table_id"] == catalogue_table_id
    assert captured["required"] is True
    assert rules[0]["guardrail_rule_id"] == "frozen-rule"
    assert rules[0]["metadata_table_key"] == "legacy-runtime-key"


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


@pytest.mark.parametrize("status", ["draft", "superseded"])
def test_development_exact_override_accepts_non_rejected_frozen_versions(monkeypatch, status):
    """Allow Development to execute an exact draft or superseded contract."""
    selected = _contract(2, status=status, rule="frozen-rule")
    monkeypatch.setattr(pipeline_shared, "read_lakehouse_table_core", lambda *args, **kwargs: _Frame([selected]))
    rules = pipeline_shared.load_table_guardrail_rules(
        {}, "dev", spark_session=_Spark(), table_id="orders", metadata_table_key="runtime-orders",
        context={"data_contract_overrides": {"orders": {"contract_id": "contract", "contract_version": 2}}},
    ).collect()
    assert rules[0]["guardrail_rule_id"] == "frozen-rule"


@pytest.mark.parametrize(
    "context",
    [
        {"data_contract_overrides": {"orders": {"contract_id": "contract"}}},
        {"data_contract_overrides": {"orders": {"contract_version": 2}}},
    ],
)
def test_development_partial_override_fails_without_guessing(monkeypatch, context):
    """Require both immutable identity fields before reading any rule source."""
    monkeypatch.setattr(
        pipeline_shared, "read_lakehouse_table_core",
        lambda *args, **kwargs: pytest.fail("partial overrides must fail before metadata reads"),
    )
    with pytest.raises(ValueError, match="requires both"):
        pipeline_shared.load_table_guardrail_rules({}, "dev", spark_session=_Spark(), table_id="orders", context=context)


def test_development_exact_override_validates_status_table_and_identity(monkeypatch):
    """Reject unusable, mismatched, missing, and duplicate exact versions."""
    rows = [_contract(2, status="rejected")]
    monkeypatch.setattr(pipeline_shared, "read_lakehouse_table_core", lambda *args, **kwargs: _Frame(rows))
    kwargs = {
        "spark_session": _Spark(), "table_id": "orders", "metadata_table_key": "runtime-orders",
        "context": {"data_contract_overrides": {"orders": {"contract_id": "contract", "contract_version": 2}}},
    }
    with pytest.raises(ValueError, match="Rejected"):
        pipeline_shared.load_table_guardrail_rules({}, "dev", **kwargs)
    rows[:] = [_contract(2, table_id="customers")]
    with pytest.raises(ValueError, match="does not belong"):
        pipeline_shared.load_table_guardrail_rules({}, "dev", **kwargs)
    rows[:] = []
    with pytest.raises(ValueError, match="does not exist"):
        pipeline_shared.load_table_guardrail_rules({}, "dev", **kwargs)
    rows[:] = [_contract(2), _contract(2)]
    with pytest.raises(RuntimeError, match="duplicate"):
        pipeline_shared.load_table_guardrail_rules({}, "dev", **kwargs)


def test_rule_source_matrix_keeps_frozen_rules_immutable_and_prod_ignores_override(monkeypatch):
    """Use mutable Rule B only for default Dev and frozen Rule A for selected/active contracts."""
    authoring = _Frame([{"guardrail_rule_id": "rule-b"}])
    frozen = _contract(1, status="active", active=True, rule="rule-a")

    def read(name, **kwargs):
        return authoring if name == pipeline_shared.GUARDRAIL_TABLE else _Frame([frozen])

    monkeypatch.setattr(pipeline_shared, "read_lakehouse_table_core", read)
    dev_default = pipeline_shared.load_table_guardrail_rules(
        {}, "dev", spark_session=_Spark(), table_id="orders", context={},
    )
    assert dev_default.collect()[0]["guardrail_rule_id"] == "rule-b"
    dev_selected = pipeline_shared.load_table_guardrail_rules(
        {}, "dev", spark_session=_Spark(), table_id="orders",
        context={"data_contract_overrides": {"orders": {"contract_id": "contract", "contract_version": 1}}},
    ).collect()
    assert dev_selected[0]["guardrail_rule_id"] == "rule-a"

    # The table-keyed selection must not leak into another table workflow.
    dev_other_table = pipeline_shared.load_table_guardrail_rules(
        {}, "dev", spark_session=_Spark(), table_id="customers",
        context={"data_contract_overrides": {"orders": {"contract_id": "contract", "contract_version": 1}}},
    ).collect()
    assert dev_other_table[0]["guardrail_rule_id"] == "rule-b"

    authoring._rows[0]["guardrail_rule_id"] = "rule-c"
    assert pipeline_shared.load_table_guardrail_rules(
        {}, "dev", spark_session=_Spark(), table_id="orders",
        context={"data_contract_overrides": {"orders": {"contract_id": "contract", "contract_version": 1}}},
    ).collect()[0]["guardrail_rule_id"] == "rule-a"
    prod = pipeline_shared.load_table_guardrail_rules(
        {}, "prod", spark_session=_Spark(), table_id="orders",
        context={"data_contract_overrides": {"orders": {"contract_id": "ignored", "contract_version": 99}}},
    ).collect()
    assert prod[0]["guardrail_rule_id"] == "rule-a"
