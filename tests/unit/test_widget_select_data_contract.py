"""Tests for notebook-scoped immutable Data Contract selection."""

from __future__ import annotations

import inspect
import json

import pytest

import fabricops_kit.widgets.widget_select_data_contract as module
from fabricops_kit.pipeline import shared as pipeline_shared
from fabricops_kit.widgets.widget_select_data_contract import (
    _contract_options,
    _contract_review,
    _validation_contract_options,
)


def _row(version: int, *, table_id: str = "table-a", status: str = "frozen", active: bool = False) -> dict:
    payload = {
        "contract": {"contract_id": f"contract-{table_id}", "contract_version": version},
        "table": {"table_id": table_id, "schema_name": "demo", "table_name": table_id, "columns": [{"column_name": "id"}], "processing": {"load_strategy": "scd1", "key_columns": ["id"]}},
        "guardrails": [{"guardrail_type": "data_quality", "rule_id": f"rule-{table_id}"}],
        "enrichment": {"table": [], "columns": []},
    }
    return {
        "contract_id": f"contract-{table_id}", "contract_version": version,
        "table_id": table_id, "status": status, "is_active": active,
        "contract_payload_json": json.dumps(payload),
    }


class _Frame:
    def __init__(self, rows): self.rows = rows
    def collect(self): return self.rows


def _render(monkeypatch, rows, *, env="dev", pairs=None, overrides=None, active=None, catalogue_rows=None):
    context = {
        "config": object(), "env": env, "notebook_id": "notebook-1",
        "workspace_id": "workspace-1", "data_contract_overrides": dict(overrides or {}),
    }
    monkeypatch.setattr(module, "resolve_fabric_context", lambda context=None: (context_obj["config"], env, context_obj))
    context_obj = context
    monkeypatch.setattr(module, "get_spark_session", lambda _spark=None: object())
    monkeypatch.setattr(module, "metadata_table_physical_schema", lambda *_args: "engineering")
    monkeypatch.setattr(module, "resolve_notebook_lineage_tables", lambda **_kwargs: (
        [("Source", "table-a"), ("Target", "table-b")] if pairs is None else pairs,
        {"notebook_id": "notebook-1", "workspace_id": "workspace-1", "environment_name": env},
    ))
    def _read(table_name, *_args, **_kwargs):
        if table_name == "METADATA_DATA_CATALOGUE":
            return _Frame(catalogue_rows or [])
        return _Frame(rows)

    monkeypatch.setattr(module, "read_lakehouse_table", _read)
    monkeypatch.setattr(module, "resolve_active_data_contract", lambda _c, _e, tid, **_kwargs: (active or {})[tid])
    monkeypatch.setattr(module, "get_default_fabric_context", lambda: context_obj)
    monkeypatch.setattr(module, "require_ipywidgets", lambda: (_ for _ in ()).throw(ModuleNotFoundError()))
    return context_obj, module.widget_select_data_contract(context=context_obj)


def test_contract_options_are_table_scoped_immutable_and_newest_first():
    """Filter lifecycle states and unrelated tables."""
    rows = [
        _row(2), _row(4, status="draft"), _row(3), _row(5),
        _row(6, status="rejected"), _row(99, table_id="table-b"),
    ]
    assert [row["contract_version"] for row in _contract_options(rows, "table-a")] == [5, 3, 2]
    assert [row["contract_version"] for row in _validation_contract_options(rows, "table-a")] == [5, 3, 2]


def test_contract_review_uses_only_frozen_payload():
    """Build reviews from immutable table payload content."""
    review = _contract_review(_row(4))
    assert review["guardrails"] == {"data_quality": 1}
    assert review["processing"]["load_strategy"] == "scd1"
    assert "agreement" not in review


def test_contract_review_hydrates_source_refresh_expectations():
    """Expose recurring and static source refresh expectations from frozen Freshness rules."""
    recurring = _row(4)
    recurring_payload = json.loads(recurring["contract_payload_json"])
    recurring_payload["guardrails"].append({
        "guardrail_type": "freshness",
        "rule_type": "freshness",
        "is_active": True,
        "rule_parameters": {
            "refresh_expectation": "recurring",
            "expected_refresh_frequency": 6,
            "expected_refresh_unit": "hours",
        },
    })
    recurring["contract_payload_json"] = json.dumps(recurring_payload)
    assert _contract_review(recurring)["expected_refresh"] == {
        "mode": "recurring", "frequency": 6, "unit": "hours",
    }

    static = _row(5)
    static_payload = json.loads(static["contract_payload_json"])
    static_payload["guardrails"].append({
        "guardrail_type": "freshness",
        "rule_type": "skip",
        "is_active": True,
        "rule_parameters": {"refresh_expectation": "static"},
    })
    static["contract_payload_json"] = json.dumps(static_payload)
    assert _contract_review(static)["expected_refresh"] == {"mode": "static"}


def test_selector_resolves_multiple_lineage_tables_and_preserves_roles(monkeypatch):
    """Discover and independently select every notebook Lineage table."""
    rows = [_row(3), _row(2, table_id="table-b")]
    catalogue_rows = [
        {
            "environment_name": "dev", "metadata_level": "table", "is_active": True,
            "table_id": "table-a", "layer": "Bronze", "schema_name": "demo", "table_name": "orders",
        },
        {
            "environment_name": "dev", "metadata_level": "table", "is_active": True,
            "table_id": "table-b", "layer": "Silver", "schema_name": "demo", "table_name": "curated_orders",
        },
    ]
    context, state = _render(monkeypatch, rows, catalogue_rows=catalogue_rows)
    assert state["notebook"]["notebook_id"] == "notebook-1"
    assert state["lineage_tables"] == [
        {"pipeline_role": "Source", "table_id": "table-a"},
        {"pipeline_role": "Target", "table_id": "table-b"},
    ]
    assert state["tables"]["table-a"]["display_name"] == "Bronze / demo / orders"
    assert state["tables"]["table-b"]["display_name"] == "Silver / demo / curated_orders"
    assert state["tables"]["table-a"]["mode"] == "enforce"
    assert state["tables"]["table-b"]["mode"] == "enforce"
    state["set_mode"]("table-b", "validate", "contract-table-b", 2)
    assert context["data_contract_overrides"] == {}
    assert state["tables"]["table-a"]["mode"] == "enforce"
    assert state["tables"]["table-b"]["mode"] == "validate"
    assert state["tables"]["table-b"]["contract_version"] == 2


def test_selection_isolated_and_unrelated_contracts_not_available(monkeypatch):
    """Prevent selection from leaking across table identities."""
    context, state = _render(monkeypatch, [_row(3), _row(9, table_id="unrelated"), _row(2, table_id="table-b")])
    with pytest.raises(ValueError, match="not linked"):
        state["set_mode"]("unrelated", "validate", "contract-unrelated", 9)
    with pytest.raises(ValueError, match="not available"):
        state["set_mode"]("table-b", "validate", "contract-table-a", 3)
    assert context["data_contract_overrides"] == {}


def test_development_mode_switch_keeps_validation_candidate_out_of_enforcement(monkeypatch):
    """A frozen validation candidate never becomes an enforcement override."""
    context, state = _render(
        monkeypatch, [_row(2), _row(1, table_id="table-b")], pairs=[("Target", "table-a")],
    )
    monkeypatch.setattr(
        pipeline_shared, "resolve_data_contract_version",
        lambda *_args, **_kwargs: {"contract_id": "contract-table-a", "contract_version": 2},
    )

    assert pipeline_shared.resolve_pipeline_data_contract(object(), "dev", "table-a", context=context) is None
    state["set_mode"]("table-a", "validate", "contract-table-a", 2)
    assert pipeline_shared.resolve_pipeline_data_contract(object(), "dev", "table-a", context=context) is None
    assert state["tables"]["table-a"]["mode"] == "validate"
    state["set_mode"]("table-a", "enforce")
    assert state["tables"]["table-a"]["mode"] == "enforce"
    assert "table-a" not in state["resolved_contracts"]


def test_validation_operation_uses_selected_target_candidate(monkeypatch):
    """Route later DataFrame validation through the selector's exact candidate state."""
    _context, state = _render(
        monkeypatch, [_row(2)], pairs=[("Target", "table-a")],
    )
    calls = []
    monkeypatch.setattr(
        module,
        "_validate_data_contract",
        lambda **kwargs: calls.append(kwargs) or {"validation_passed": True},
    )
    state["set_mode"]("table-a", "validate", "contract-table-a", 2)

    result = state["validate"](
        table_id="table-a", dataframe="target-df", spark_session="spark", run_id="run-1",
    )

    assert result == {"validation_passed": True}
    assert calls == [{
        "table_id": "table-a", "contract_id": "contract-table-a", "contract_version": 2,
        "dataframe": "target-df", "spark_session": "spark", "run_id": "run-1", "verbose": True,
    }]


def test_initialization_and_deselect_clear_every_runtime_context(monkeypatch):
    """Clear stale overrides symmetrically across explicit, active, and default contexts."""
    explicit = {"data_contract_overrides": {"table-a": {"contract_id": "stale", "contract_version": 1}}}
    active_context = {"data_contract_overrides": {"table-a": {"contract_id": "stale", "contract_version": 1}}}
    default_context = {"data_contract_overrides": {"table-a": {"contract_id": "stale", "contract_version": 1}}}
    active = type("Active", (), {"context": active_context})()
    monkeypatch.setattr(module, "pipeline_active_context", lambda: active)
    monkeypatch.setattr(module, "get_default_fabric_context", lambda: default_context)

    module._clear_overrides(explicit)
    assert explicit["data_contract_overrides"] == {}
    assert active_context["data_contract_overrides"] == {}
    assert default_context["data_contract_overrides"] == {}


def test_missing_frozen_version_runs_unvalidated_in_development(monkeypatch):
    """Allow Development lineage tables to remain without a selected contract."""
    context, state = _render(monkeypatch, [_row(1, status="draft"), _row(2, table_id="table-b")])
    assert state["tables"]["table-a"]["versions"] == []
    assert state["resolved_contracts"] == {}
    assert context["data_contract_overrides"] == {}
    assert "each table can enforce" in state["message"]


def test_production_supports_active_enforcement_and_frozen_validation_per_table(monkeypatch):
    """Production defaults to active enforcement but allows exact frozen validation."""
    active = {
        "table-a": _row(3, active=True),
        "table-b": _row(2, table_id="table-b", active=True),
    }
    frozen = [_row(4), _row(5, table_id="table-b")]
    context, state = _render(monkeypatch, frozen, env="prod", overrides={"table-a": {"contract_id": "wrong", "contract_version": 99}}, active=active)
    assert context["data_contract_overrides"] == {}
    assert state["resolved_contracts"]["table-a"]["contract_version"] == 3
    assert state["resolved_contracts"]["table-b"]["contract_version"] == 2
    state["set_mode"]("table-b", "validate", "contract-table-b", 5)
    assert state["tables"]["table-a"]["mode"] == "enforce"
    assert state["tables"]["table-b"]["mode"] == "validate"
    assert state["tables"]["table-b"]["contract_version"] == 5
    assert context["data_contract_overrides"] == {}


def test_production_zero_active_fails_clearly(monkeypatch):
    """Fail Production when a discovered table has no active version."""
    monkeypatch.setattr(module, "resolve_active_data_contract", lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("missing")))
    context = {"config": object(), "env": "prod", "notebook_id": "n", "data_contract_overrides": {}}
    monkeypatch.setattr(module, "resolve_fabric_context", lambda context=None: (context_obj["config"], "prod", context_obj))
    context_obj = context
    monkeypatch.setattr(module, "get_spark_session", lambda _spark=None: object())
    monkeypatch.setattr(module, "metadata_table_physical_schema", lambda *_args: "engineering")
    monkeypatch.setattr(module, "read_lakehouse_table", lambda *_args, **_kwargs: _Frame([]))
    monkeypatch.setattr(module, "resolve_notebook_lineage_tables", lambda **_kwargs: ([('Target', 'table-a')], {}))
    with pytest.raises(ValueError, match="exactly one active"):
        module.widget_select_data_contract(context=context)


def test_selector_no_longer_accepts_manual_table_id():
    """Keep notebook discovery as the only normal selector scope."""
    parameters = inspect.signature(module.widget_select_data_contract).parameters
    assert "table_id" not in parameters
    assert set(parameters) == {"spark_session", "context"}
    assert "Current authoring" not in inspect.getsource(module.widget_select_data_contract)


def test_development_with_no_lineage_initializes_empty_context(monkeypatch):
    """Allow the first Development baseline run before Lineage exists."""
    context, state = _render(monkeypatch, [], pairs=[])
    assert state["lineage_tables"] == []
    assert state["resolved_contracts"] == {}
    assert context["data_contract_overrides"] == {}


def test_production_multiple_active_contracts_fail_with_context(monkeypatch):
    """Keep multiple-active integrity failures closed in Production."""
    monkeypatch.setattr(
        module, "resolve_active_data_contract",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("multiple active versions")),
    )
    context = {"config": object(), "env": "prod", "notebook_id": "02-pipeline", "data_contract_overrides": {}}
    monkeypatch.setattr(module, "resolve_fabric_context", lambda context=None: (context_obj["config"], "prod", context_obj))
    context_obj = context
    monkeypatch.setattr(module, "get_spark_session", lambda _spark=None: object())
    monkeypatch.setattr(module, "metadata_table_physical_schema", lambda *_args: "engineering")
    monkeypatch.setattr(module, "read_lakehouse_table", lambda *_args, **_kwargs: _Frame([]))
    monkeypatch.setattr(module, "resolve_notebook_lineage_tables", lambda **_kwargs: ([('Target', 'table-a')], {"notebook_name": "02_pipeline"}))
    with pytest.raises(RuntimeError, match="multiple active"):
        module.widget_select_data_contract(context=context)
