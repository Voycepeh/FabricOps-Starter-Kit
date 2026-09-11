"""Tests for notebook-scoped immutable Data Contract selection."""

from __future__ import annotations

import inspect
import json

import pytest

import fabricops_kit.widgets.widget_select_data_contract as module
from fabricops_kit.widgets.widget_select_data_contract import _contract_options, _contract_review


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


def _render(monkeypatch, rows, *, env="dev", pairs=None, overrides=None, active=None):
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
    monkeypatch.setattr(module, "read_lakehouse_table_core", lambda *_args, **_kwargs: _Frame(rows))
    monkeypatch.setattr(module, "resolve_active_data_contract", lambda _c, _e, tid, **_kwargs: (active or {})[tid])
    monkeypatch.setattr(module, "get_default_fabric_context", lambda: context_obj)
    monkeypatch.setattr(module, "require_ipywidgets", lambda: (_ for _ in ()).throw(ModuleNotFoundError()))
    return context_obj, module.widget_select_data_contract(context=context_obj)


def test_contract_options_are_table_scoped_immutable_and_newest_first():
    """Filter lifecycle states and unrelated tables."""
    rows = [_row(2, status="superseded"), _row(4, status="draft"), _row(3, status="active"), _row(5), _row(6, status="rejected"), _row(99, table_id="table-b")]
    assert [row["contract_version"] for row in _contract_options(rows, "table-a")] == [5, 3, 2]


def test_contract_review_uses_only_frozen_payload():
    """Build reviews from immutable table payload content."""
    review = _contract_review(_row(4))
    assert review["guardrails"] == {"data_quality": 1}
    assert review["processing"]["load_strategy"] == "scd1"
    assert "agreement" not in review


def test_selector_resolves_multiple_lineage_tables_and_preserves_roles(monkeypatch):
    """Discover and independently select every notebook Lineage table."""
    rows = [_row(3), _row(2, table_id="table-b")]
    context, state = _render(monkeypatch, rows)
    assert state["notebook"]["notebook_id"] == "notebook-1"
    assert state["lineage_tables"] == [
        {"pipeline_role": "Source", "table_id": "table-a"},
        {"pipeline_role": "Target", "table_id": "table-b"},
    ]
    state["select"]("table-a", "contract-table-a", 3)
    state["select"]("table-b", "contract-table-b", 2)
    assert context["data_contract_overrides"] == {
        "table-a": {"contract_id": "contract-table-a", "contract_version": 3},
        "table-b": {"contract_id": "contract-table-b", "contract_version": 2},
    }


def test_selection_isolated_and_unrelated_contracts_not_available(monkeypatch):
    """Prevent selection from leaking across table identities."""
    context, state = _render(monkeypatch, [_row(3), _row(9, table_id="unrelated"), _row(2, table_id="table-b")])
    with pytest.raises(ValueError, match="not linked"):
        state["select"]("unrelated", "contract-unrelated", 9)
    with pytest.raises(ValueError, match="not available"):
        state["select"]("table-a", "contract-table-b", 2)
    assert context["data_contract_overrides"] == {}


def test_missing_frozen_version_runs_unvalidated_in_development(monkeypatch):
    """Allow Development lineage tables to remain without a selected contract."""
    context, state = _render(monkeypatch, [_row(1, status="draft"), _row(2, table_id="table-b")])
    assert state["tables"]["table-a"]["versions"] == []
    assert state["resolved_contracts"] == {}
    assert context["data_contract_overrides"] == {}
    assert "running unvalidated" in state["message"]


def test_production_resolves_each_active_contract_and_ignores_overrides(monkeypatch):
    """Resolve active Production versions and clear Development overrides."""
    active = {"table-a": _row(3, status="active", active=True), "table-b": _row(2, table_id="table-b", status="active", active=True)}
    context, state = _render(monkeypatch, [], env="prod", overrides={"table-a": {"contract_id": "wrong", "contract_version": 99}}, active=active)
    assert context["data_contract_overrides"] == {}
    assert state["resolved_contracts"]["table-a"]["contract_version"] == 3
    assert state["resolved_contracts"]["table-b"]["contract_version"] == 2
    with pytest.raises(ValueError, match="resolved automatically"):
        state["select"]("table-a", "contract-table-a", 3)


def test_production_zero_active_fails_clearly(monkeypatch):
    """Fail Production when a discovered table has no active version."""
    monkeypatch.setattr(module, "resolve_active_data_contract", lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("missing")))
    context = {"config": object(), "env": "prod", "notebook_id": "n", "data_contract_overrides": {}}
    monkeypatch.setattr(module, "resolve_fabric_context", lambda context=None: (context_obj["config"], "prod", context_obj))
    context_obj = context
    monkeypatch.setattr(module, "get_spark_session", lambda _spark=None: object())
    monkeypatch.setattr(module, "metadata_table_physical_schema", lambda *_args: "engineering")
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
    monkeypatch.setattr(module, "resolve_notebook_lineage_tables", lambda **_kwargs: ([('Target', 'table-a')], {"notebook_name": "02_pipeline"}))
    with pytest.raises(RuntimeError, match="multiple active"):
        module.widget_select_data_contract(context=context)
