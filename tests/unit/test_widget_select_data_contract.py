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
        "table": {"table_id": table_id, "schema_name": "demo", "table_name": "orders", "columns": [{"column_name": "id"}]},
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


def _render(monkeypatch, rows, *, env="dev"):
    state_context = {"config": object(), "env": env}
    monkeypatch.setattr(module, "resolve_fabric_context", lambda context=None: (state_context["config"], env, state_context))
    monkeypatch.setattr(module, "get_spark_session", lambda _spark=None: object())
    monkeypatch.setattr(module, "get_store", lambda *_args: _Store())
    monkeypatch.setattr(module, "resolve_lakehouse_table_location", lambda *_args: ("orders", "demo", "path"))
    monkeypatch.setattr(module, "resolve_catalogue_table_id", lambda *_args, **_kwargs: "table-a")
    monkeypatch.setattr(module, "read_lakehouse_table_core", lambda *_args, **_kwargs: _Frame(rows))
    monkeypatch.setattr(module, "get_default_fabric_context", lambda: state_context)
    monkeypatch.setattr(module, "require_ipywidgets", lambda: (_ for _ in ()).throw(ModuleNotFoundError()))
    return state_context, module.widget_select_data_contract("orders", schema="demo")


def test_default_and_exact_selection_feed_active_context(monkeypatch):
    """Default clears overrides and exact selection updates the active context."""
    context, state = _render(monkeypatch, [_row(4), _row(3, status="active")])

    assert context["data_contract_id"] is None
    assert context["data_contract_version"] is None
    state["select"]("contract-a", 3)
    assert context["data_contract_id"] == "contract-a"
    assert context["data_contract_version"] == 3
    assert state["review"]["guardrail_details"][0]["rule_id"] == "frozen-rule"


def test_rejected_contract_cannot_become_override(monkeypatch):
    """Rejected lifecycle rows cannot enter runtime context."""
    context, state = _render(monkeypatch, [_row(5, status="rejected")])

    with pytest.raises(ValueError, match="Rejected"):
        state["select"]("contract-a", 5)
    assert context["data_contract_id"] is None


def test_production_never_accepts_manual_override(monkeypatch):
    """Production remains automatic even when a version is requested."""
    context, state = _render(monkeypatch, [_row(3, status="active")], env="prod")

    state["select"]("contract-a", 3)
    assert context["data_contract_id"] is None
    assert context["data_contract_version"] is None
    assert state["message"] == "Production uses the active Data Contract automatically."
