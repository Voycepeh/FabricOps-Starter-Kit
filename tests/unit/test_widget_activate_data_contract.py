"""Tests for manual Data Contract activation and frozen rule resolution."""

from __future__ import annotations

import json
import sys
from types import ModuleType

import pytest

from fabricops_kit.pipeline import shared as pipeline_shared
from fabricops_kit.widgets.shared import _contract_activation_changes
from fabricops_kit.widgets import shared as widget_shared
from fabricops_kit.widgets.widget_activate_data_contract import _compact_review, _payload, _selected_contract

pytestmark = pytest.mark.unit


def _contract(version: int, *, status: str = "draft", active: bool = False, table_id: str = "orders", rule: str = "rule-a"):
    payload = {
        "contract": {"contract_id": "contract", "contract_version": version, "status": "draft"},
        "table": {"table_id": table_id, "table_name": "orders", "schema_name": "sales", "columns": [{"column_id": "id", "column_name": "id", "data_type": "long"}]},
        "enrichment": {"table": [], "columns": []},
        "guardrails": [{"guardrail_rule_id": rule, "guardrail_version": version, "guardrail_type": "data_quality", "rule_id": rule, "rule_type": "not_null", "rule_parameters": {"columns": ["id"]}, "action": "Block"}],
        "approved_usages": ["analytics"],
    }
    return {"contract_id": "contract", "contract_version": version, "agreement_id": "agreement" if active else None, "agreement_version": "1" if active else None, "table_id": table_id, "status": status, "is_active": active, "contract_payload_json": json.dumps(payload)}


def test_activation_supersedes_previous_version_without_mutating_frozen_fields():
    """Change only lifecycle fields when a newer frozen version is activated."""
    rows = [_contract(1, status="active", active=True), _contract(2), _contract(3)]
    before = [(row["contract_version"], row["contract_payload_json"]) for row in rows]
    changes = _contract_activation_changes(rows, rows[1], agreement_id="agreement", agreement_version="1")
    assert changes == [
        {"contract_id": "contract", "contract_version": 1, "status": "superseded", "is_active": False},
        {
            "contract_id": "contract", "contract_version": 2,
            "status": "active", "is_active": True,
            "agreement_id": "agreement", "agreement_version": "1",
        },
    ]
    assert rows[2]["status"] == "draft"
    assert [(row["contract_version"], row["contract_payload_json"]) for row in rows] == before


def test_activation_is_idempotent_and_rejected_or_mismatched_versions_fail():
    """Avoid redundant writes and reject ineligible or invalid selections."""
    active = {**_contract(1, status="active", active=True), "agreement_id": "agreement", "agreement_version": "1"}
    assert _contract_activation_changes([active], active, agreement_id="agreement", agreement_version="1") == []
    with pytest.raises(ValueError, match="frozen"):
        _selected_contract([_contract(2, status="rejected")], "orders", "contract", 2)
    with pytest.raises(ValueError, match="does not belong"):
        _selected_contract([_contract(2, table_id="customers")], "orders", "contract", 2)
    with pytest.raises(ValueError, match="does not exist"):
        _selected_contract([], "orders", "contract", 99)


def test_activation_requires_exact_existing_agreement_and_rejects_conflicting_relink(monkeypatch):
    """Validate Agreement linkage before any lifecycle update and fail closed on relink."""
    frozen = _contract(2, status="frozen")
    frames = {
        widget_shared.DATA_CONTRACT_TABLE: _Frame([frozen]),
        "METADATA_DATA_AGREEMENT": _Frame([{"agreement_id": "agreement", "agreement_version": "2"}]),
    }
    monkeypatch.setattr(widget_shared, "read_lakehouse_table_core", lambda name, **_kwargs: frames[name])
    with pytest.raises(ValueError, match="exact Data Agreement"):
        widget_shared.activate_contract_version(
            config=object(), env="dev", table_id="orders", contract_id="contract",
            contract_version=2, agreement_id="", agreement_version="", spark_session=_Spark(),
        )
    with pytest.raises(ValueError, match="does not exist"):
        widget_shared.activate_contract_version(
            config=object(), env="dev", table_id="orders", contract_id="contract",
            contract_version=2, agreement_id="agreement", agreement_version="99", spark_session=_Spark(),
        )

    active = {**_contract(2, status="active", active=True), "agreement_id": "agreement", "agreement_version": "2"}
    frames[widget_shared.DATA_CONTRACT_TABLE] = _Frame([active])
    result = widget_shared.activate_contract_version(
        config=object(), env="dev", table_id="orders", contract_id="contract",
        contract_version=2, agreement_id="agreement", agreement_version="2", spark_session=_Spark(),
    )
    assert result == {
        "changed": False, "contract_id": "contract", "contract_version": 2, "changes": [],
    }
    with pytest.raises(ValueError, match="cannot be relinked"):
        widget_shared.activate_contract_version(
            config=object(), env="dev", table_id="orders", contract_id="contract",
            contract_version=2, agreement_id="other", agreement_version="1", spark_session=_Spark(),
        )


def test_activation_writes_linkage_and_supersedes_atomically(monkeypatch):
    """Persist linkage with the selected activation while preserving the frozen payload."""
    prior = _contract(1, status="active", active=True)
    selected = _contract(2, status="frozen")
    assert selected["agreement_id"] is None
    assert selected["agreement_version"] is None
    frames = {
        widget_shared.DATA_CONTRACT_TABLE: _Frame([prior, selected]),
        "METADATA_DATA_AGREEMENT": _Frame([{"agreement_id": "agreement", "agreement_version": "2"}]),
    }
    monkeypatch.setattr(widget_shared, "read_lakehouse_table_core", lambda name, **_kwargs: frames[name])
    monkeypatch.setattr(widget_shared, "resolve_configured_lakehouse_table", lambda *_args, **_kwargs: (None, None, None, "/contracts"))
    captured = {}

    class _Merge:
        def alias(self, _name): return self
        def merge(self, source, _condition): captured["rows"] = source._rows; return self
        def whenMatchedUpdate(self, *, set): captured["set"] = set; return self
        def execute(self): return None

    delta = ModuleType("delta")
    delta_tables = ModuleType("delta.tables")
    delta_tables.DeltaTable = type("DeltaTable", (), {"forPath": staticmethod(lambda *_args: _Merge())})
    delta.tables = delta_tables
    monkeypatch.setitem(sys.modules, "delta", delta)
    monkeypatch.setitem(sys.modules, "delta.tables", delta_tables)
    payload_before = selected["contract_payload_json"]
    result = widget_shared.activate_contract_version(
        config=object(), env="dev", table_id="orders", contract_id="contract",
        contract_version=2, agreement_id="agreement", agreement_version="2", spark_session=_Spark(),
    )
    assert result["changes"][0]["status"] == "superseded"
    assert result["changes"][1]["agreement_id"] == "agreement"
    assert result["changes"][1]["agreement_version"] == "2"
    assert selected["contract_payload_json"] == payload_before
    assert captured["set"]["agreement_id"].startswith("coalesce")


def test_review_and_guardrails_come_only_from_frozen_payload():
    """Build review and runtime rules from the immutable contract document."""
    row = _contract(1)
    payload = _payload(row)
    assert _compact_review(payload)["schema_columns"] == 1
    contract = {**row, "contract_payload": payload}
    rules = pipeline_shared.contract_guardrail_rows(
        contract, environment_name="prod", table_id="runtime-orders",
    )
    assert rules[0]["guardrail_rule_id"] == "rule-a"
    assert rules[0]["table_id"] == "runtime-orders"
    assert json.loads(rules[0]["rule_parameters_json"]) == {"columns": ["id"]}
    assert "rule_parameters" not in rules[0]


def test_frozen_guardrail_adapter_serializes_heterogeneous_parameters():
    """Keep mixed scalar and list parameters out of Spark schema inference."""
    contract = _contract(1)
    payload = json.loads(contract["contract_payload_json"])
    payload["guardrails"] = [
        {
            "guardrail_rule_id": "conditional", "guardrail_version": 1,
            "guardrail_type": "data_quality", "rule_id": "conditional",
            "rule_type": "required_when",
            "rule_parameters": {
                "columns": ["id"], "condition_column": "status",
                "condition_operator": "=", "condition_value": "open",
            },
            "action": "Warn",
        },
        {
            "guardrail_rule_id": "comparison", "guardrail_version": 1,
            "guardrail_type": "data_quality", "rule_id": "comparison",
            "rule_type": "compare_columns",
            "rule_parameters": {"columns": ["upper", "lower"], "operator": "<="},
            "action": "Block",
        },
    ]
    contract["contract_payload_json"] = json.dumps(payload)

    rules = pipeline_shared.contract_guardrail_rows(
        contract, environment_name="dev", table_id="orders",
    )

    assert all("rule_parameters" not in rule for rule in rules)
    assert json.loads(rules[0]["rule_parameters_json"])["condition_column"] == "status"
    assert json.loads(rules[1]["rule_parameters_json"])["columns"] == ["upper", "lower"]


def _schema_contract(*, rule_type="strict", severity="blocking"):
    contract = _contract(1, status="active", active=True)
    payload = json.loads(contract["contract_payload_json"])
    payload["table"]["columns"] = [
        {"column_id": "id", "column_name": "id", "data_type": "string"},
        {"column_id": "amount", "column_name": "amount", "data_type": "double"},
    ]
    payload["guardrails"] = [{
        "guardrail_rule_id": "schema-rule", "guardrail_version": 1,
        "table_id": "orders", "guardrail_type": "schema", "rule_id": "schema", "rule_type": rule_type,
        "rule_parameters": {"columns": ["stale"], "data_types": {"stale": "long"}},
        "severity": severity,
    }]
    contract["contract_payload_json"] = json.dumps(payload)
    contract["contract_payload"] = payload
    return contract


def test_frozen_schema_adapter_uses_table_columns_over_conflicting_rule_parameters():
    """Synthesize runtime schema parameters exclusively from frozen table.columns."""
    rules = pipeline_shared.contract_guardrail_rows(
        _schema_contract(), environment_name="dev", table_id="orders",
    )
    assert json.loads(rules[0]["rule_parameters_json"]) == {
        "columns": ["id", "amount"], "data_types": {"id": "string", "amount": "double"},
    }


class _SchemaFrame:
    def __init__(self, fields):
        self.dtypes = fields
        self.columns = [name for name, _dtype in fields]


@pytest.mark.parametrize(
    ("rule_type", "fields", "status", "can_continue"),
    [
        ("strict", [("id", "string"), ("amount", "double"), ("extra", "string")], "failed", False),
        ("minimum_required", [("id", "string"), ("amount", "double"), ("extra", "string")], "warning", True),
        ("minimum_required", [("id", "string")], "failed", False),
        ("minimum_required", [("id", "string"), ("amount", "string")], "failed", False),
        ("relaxed", [("id", "string"), ("amount", "double"), ("extra", "string")], "warning", True),
        ("skip", [("id", "long"), ("extra", "string")], "warning", True),
    ],
)
def test_frozen_schema_enforcement_modes(rule_type, fields, status, can_continue):
    """Preserve strict, relaxed, minimum-required, and monitor-only enforcement."""
    rules = pipeline_shared.contract_guardrail_rows(
        _schema_contract(rule_type=rule_type), environment_name="prod", table_id="orders",
    )
    result = pipeline_shared.schema_check_core(
        _SchemaFrame(fields), rules_df=rules, environment_name="prod", table_id="orders",
    )
    assert result["status"] == status
    assert result["can_continue"] is can_continue


@pytest.mark.parametrize(
    ("columns", "message"),
    [
        (None, "missing"),
        ({}, "must be a list"),
        (["id"], "must be an object"),
        ([{"column_id": "id", "column_name": "", "data_type": "string"}], "non-blank"),
        ([{"column_id": "id", "column_name": "id", "data_type": ""}], "non-blank"),
        ([
            {"column_id": "id-1", "column_name": "id", "data_type": "string"},
            {"column_id": "id-2", "column_name": "id", "data_type": "long"},
        ], "duplicate column_name"),
    ],
)
def test_corrupt_frozen_table_columns_fail_without_guardrail_fallback(columns, message):
    """Reject corrupt frozen structure even when stale schema parameters exist."""
    contract = _schema_contract()
    if columns is None:
        del contract["contract_payload"]["table"]["columns"]
    else:
        contract["contract_payload"]["table"]["columns"] = columns
    with pytest.raises(ValueError, match=message):
        pipeline_shared.contract_guardrail_rows(
            contract, environment_name="prod", table_id="orders",
        )


class _Frame:
    def __init__(self, rows):
        self._rows = rows

    def collect(self):
        return self._rows

    def alias(self, _name):
        return self


class _Spark:
    def createDataFrame(self, rows):
        return _Frame(rows)


def test_development_uses_active_contract_guardrails(monkeypatch):
    """Resolve Development Guardrails through the active Data Contract by default."""
    frozen = _contract(1, status="active", active=True, rule="contract-rule")
    monkeypatch.setattr(
        pipeline_shared, "read_lakehouse_table_core", lambda name, **kwargs: _Frame([frozen]),
    )
    resolved = pipeline_shared.load_table_guardrail_rules(
        {}, "dev", spark_session=_Spark(), table_id="orders",
    )
    assert resolved.collect()[0]["guardrail_rule_id"] == "contract-rule"


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
    ).collect()
    assert captured["table_id"] == catalogue_table_id
    assert captured["required"] is True
    assert rules[0]["guardrail_rule_id"] == "frozen-rule"
    assert rules[0]["table_id"] == catalogue_table_id


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


def test_active_resolver_rejects_null_agreement_linkage(monkeypatch):
    """Never allow Production to use an active contract without an exact Agreement."""
    row = _contract(1, status="active", active=True)
    row["agreement_id"] = None
    row["agreement_version"] = None
    monkeypatch.setattr(
        pipeline_shared, "read_lakehouse_table_core", lambda *_args, **_kwargs: _Frame([row])
    )
    with pytest.raises(RuntimeError, match="no exact Data Agreement linkage"):
        pipeline_shared.resolve_active_data_contract({}, "prod", "orders")


@pytest.mark.parametrize("status", ["frozen", "superseded"])
def test_development_exact_override_accepts_non_rejected_frozen_versions(monkeypatch, status):
    """Allow Development to execute an exact frozen or superseded contract."""
    selected = _contract(2, status=status, rule="frozen-rule")
    monkeypatch.setattr(pipeline_shared, "read_lakehouse_table_core", lambda *args, **kwargs: _Frame([selected]))
    rules = pipeline_shared.load_table_guardrail_rules(
        {}, "dev", spark_session=_Spark(), table_id="orders",
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
        "spark_session": _Spark(), "table_id": "orders",
        "context": {"data_contract_overrides": {"orders": {"contract_id": "contract", "contract_version": 2}}},
    }
    with pytest.raises(ValueError, match="frozen"):
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
    """Use frozen rules for default, selected, and Production contract resolution."""
    authoring = _Frame([{"guardrail_rule_id": "rule-b"}])
    frozen = _contract(1, status="active", active=True, rule="rule-a")

    def read(name, **kwargs):
        return authoring if name == pipeline_shared.GUARDRAIL_TABLE else _Frame([frozen])

    monkeypatch.setattr(pipeline_shared, "read_lakehouse_table_core", read)
    dev_default = pipeline_shared.load_table_guardrail_rules(
        {}, "dev", spark_session=_Spark(), table_id="orders", context={},
    )
    assert dev_default.collect()[0]["guardrail_rule_id"] == "rule-a"
    dev_selected = pipeline_shared.load_table_guardrail_rules(
        {}, "dev", spark_session=_Spark(), table_id="orders",
        context={"data_contract_overrides": {"orders": {"contract_id": "contract", "contract_version": 1}}},
    ).collect()
    assert dev_selected[0]["guardrail_rule_id"] == "rule-a"

    # The table-keyed selection must not leak into another table workflow.
    with pytest.raises(ValueError, match="No active Data Contract"):
        pipeline_shared.load_table_guardrail_rules(
            {}, "dev", spark_session=_Spark(), table_id="customers",
            context={"data_contract_overrides": {"orders": {"contract_id": "contract", "contract_version": 1}}},
        )

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
