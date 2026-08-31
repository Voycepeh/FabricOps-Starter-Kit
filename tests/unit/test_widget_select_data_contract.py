"""Tests for the read-only Development Data Contract selector."""

from __future__ import annotations

import json

import pytest

import fabricops_kit.widgets.widget_select_data_contract as module
from fabricops_kit.widgets.widget_select_data_contract import _contract_options, _contract_review


def _row(version: int, *, table_id: str = "table-a", status: str = "draft") -> dict:
    payload = {
        "contract": {"contract_id": "contract-a", "contract_version": version},
        "agreement": {"agreement_name": "Product Agreement", "agreement_version": 2},
        "table": {"table_id": table_id, "schema_name": "demo", "table_name": "orders", "columns": [{"column_name": "id"}], "processing": {"load_strategy": "scd1", "key_columns": ["id"]}},
        "guardrails": [{"guardrail_type": "dq", "rule_id": "frozen-rule"}],
        "approved_usages": ["Analytics"],
    }
    return {
        "contract_id": "contract-a",
        "contract_version": version,
        "table_id": table_id,
        "status": status,
        "is_active": status == "active",
        "contract_payload_json": json.dumps(payload),
    }


def test_contract_options_are_table_scoped_and_newest_first():
    """Only matching versions are offered in deterministic descending order."""
    rows = [_row(2, status="superseded"), _row(4), _row(3, status="active"), _row(99, table_id="table-b")]

    options = _contract_options(rows, "table-a")

    assert [row["contract_version"] for row in options] == [4, 3, 2]
    assert [row["status"] for row in options] == ["draft", "active", "superseded"]


def test_contract_review_uses_only_frozen_payload():
    """Preview values come from the immutable payload."""
    selected = _row(4)
    review = _contract_review(selected)

    # Mutable authoring metadata is deliberately absent from this operation.
    assert review["guardrails"] == {"dq": 1}
    assert review["guardrail_details"][0]["rule_id"] == "frozen-rule"
    assert review["schema_columns"] == 1
    assert review["processing"]["load_strategy"] == "scd1"


def test_contract_review_rejects_payload_identity_mismatch():
    """Frozen payload identity must agree with its metadata row."""
    selected = _row(4)
    payload = json.loads(selected["contract_payload_json"])
    payload["table"]["table_id"] = "wrong-table"
    selected["contract_payload_json"] = json.dumps(payload)

    with pytest.raises(ValueError, match="table_id does not match"):
        _contract_review(selected)


class _Frame:
    def __init__(self, rows):
        self.rows = rows

    def collect(self):
        return self.rows


class _Store:
    kind = "lakehouse"


def _render(monkeypatch, rows, *, env="dev", overrides=None):
    state_context = {"config": object(), "env": env, "data_contract_overrides": dict(overrides or {})}
    monkeypatch.setattr(module, "resolve_fabric_context", lambda context=None: (state_context["config"], env, state_context))
    monkeypatch.setattr(module, "get_spark_session", lambda _spark=None: object())
    monkeypatch.setattr(module, "configured_lakehouse_schema", lambda *_args: "governance")
    def read_contracts(*_args, **kwargs):
        assert kwargs["schema"] == "governance"
        return _Frame(rows)

    monkeypatch.setattr(module, "read_lakehouse_table_core", read_contracts)
    monkeypatch.setattr(module, "resolve_active_data_contract", lambda *_args, **_kwargs: rows[0] if rows else None)
    monkeypatch.setattr(module, "get_default_fabric_context", lambda: state_context)
    monkeypatch.setattr(module, "require_ipywidgets", lambda: (_ for _ in ()).throw(ModuleNotFoundError()))
    return state_context, module.widget_select_data_contract(table_id="table-a")


def test_default_and_exact_selection_feed_active_context(monkeypatch):
    """Default clears overrides and exact selection updates the active context."""
    context, state = _render(monkeypatch, [_row(4), _row(3, status="active")])

    assert context["data_contract_overrides"] == {}
    state["select"]("contract-a", 3)
    assert context["data_contract_overrides"] == {
        "table-a": {"contract_id": "contract-a", "contract_version": 3},
    }
    assert state["review"]["guardrail_details"][0]["rule_id"] == "frozen-rule"


def test_selection_updates_only_its_table_entry(monkeypatch):
    """Selecting or clearing table A preserves table B's independent override."""
    table_b = {"table-b": {"contract_id": "contract-b", "contract_version": 2}}
    context, state = _render(monkeypatch, [_row(3, status="active")], overrides=table_b)

    state["select"]("contract-a", 3)
    assert context["data_contract_overrides"]["table-b"] == table_b["table-b"]
    state["select"]()
    assert context["data_contract_overrides"] == table_b


def test_rejected_contract_cannot_become_override(monkeypatch):
    """Rejected lifecycle rows cannot enter runtime context."""
    context, state = _render(monkeypatch, [_row(5, status="rejected")])

    with pytest.raises(ValueError, match="Rejected"):
        state["select"]("contract-a", 5)
    assert context["data_contract_overrides"] == {}


def test_production_never_accepts_manual_override(monkeypatch):
    """Production remains automatic even when a version is requested."""
    context, state = _render(monkeypatch, [_row(3, status="active")], env="prod")

    state["select"]("contract-a", 3)
    assert context["data_contract_overrides"] == {}
    assert state["message"] == "Using active Data Contract v3"


def test_selector_exposes_only_canonical_identity():
    """Remove all physical-coordinate selector parameters."""
    import inspect
    parameters = inspect.signature(module.widget_select_data_contract).parameters
    assert "table_id" in parameters
    assert {"table_name", "target", "schema"}.isdisjoint(parameters)
    with pytest.raises(ValueError, match="table_id must be a non-empty"):
        module.widget_select_data_contract(table_id=" ")


def test_production_requires_active_contract(monkeypatch):
    """Never fall back to current authoring or latest contract in Production."""
    state_context = {"config": object(), "env": "prod", "data_contract_overrides": {}}
    monkeypatch.setattr(module, "resolve_fabric_context", lambda context=None: (state_context["config"], "prod", state_context))
    monkeypatch.setattr(module, "get_spark_session", lambda _spark=None: object())
    monkeypatch.setattr(module, "configured_lakehouse_schema", lambda *_args: "governance")
    monkeypatch.setattr(module, "resolve_active_data_contract", lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("missing")))
    with pytest.raises(ValueError, match="Production requires an active Data Contract"):
        module.widget_select_data_contract(table_id="table-a")
