"""Focused tests for the Stage 4D table-guardrail orchestrator."""

from __future__ import annotations

import importlib

import pytest

pytestmark = pytest.mark.unit


class _TaggedFrame:
    def __init__(self):
        self.filters: list[str] = []

    def filter(self, expression: str):
        filtered = _TaggedFrame()
        filtered.filters = [*self.filters, expression]
        return filtered


def test_run_table_guardrails_delegates_and_splits_blocking_dq_rows(monkeypatch):
    runtime = importlib.import_module("fabricops_kit.pipeline.run_table_guardrails")
    dataframe = object()
    observation = object()
    tagged = _TaggedFrame()
    calls: list[tuple] = []

    monkeypatch.setattr(
        runtime,
        "check_schema",
        lambda table_name, **kwargs: calls.append(("schema", table_name, kwargs))
        or {"status": "passed", "can_continue": True},
    )
    monkeypatch.setattr(
        runtime,
        "check_freshness",
        lambda value: calls.append(("freshness", value))
        or {"status": "warning", "can_continue": True},
    )
    monkeypatch.setattr(
        runtime,
        "check_changes",
        lambda value: calls.append(("changes", value))
        or {"status": "passed", "can_continue": True},
    )
    monkeypatch.setattr(
        runtime,
        "check_dq",
        lambda value, table_name, **kwargs: calls.append(("dq", value, table_name, kwargs))
        or {"status": "passed", "can_continue": True, "dataframe": tagged},
    )

    result = runtime.run_table_guardrails(
        dataframe,
        "orders",
        target="source",
        schema="dbo",
        observation=observation,
        dataset_name="sales",
        run_id="run-1",
        row_identity_columns=["order_id"],
    )

    assert result["status"] == "warning"
    assert result["can_continue"] is True
    assert result["observation"] is observation
    assert result["dataframe"] is tagged
    assert result["quarantine_dataframe"].filters[-1] == "_dq_check_status = 'failed'"
    assert result["passing_dataframe"].filters[-1] == "_dq_check_status <> 'failed' OR _dq_check_status IS NULL"
    assert [call[0] for call in calls] == ["schema", "freshness", "changes", "dq"]
    assert calls[0][2]["dataframe"] is dataframe
    assert calls[3][3]["row_identity_columns"] == ["order_id"]


def test_run_table_guardrails_collects_observation_when_not_supplied(monkeypatch):
    runtime = importlib.import_module("fabricops_kit.pipeline.run_table_guardrails")
    dataframe = object()
    observation = object()
    tagged = _TaggedFrame()
    observed: list[tuple] = []

    monkeypatch.setattr(
        runtime,
        "observe_table",
        lambda table_name, **kwargs: observed.append((table_name, kwargs)) or observation,
    )
    monkeypatch.setattr(runtime, "check_schema", lambda *args, **kwargs: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(runtime, "check_freshness", lambda value: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(runtime, "check_changes", lambda value: {"status": "passed", "can_continue": True})
    monkeypatch.setattr(
        runtime,
        "check_dq",
        lambda *args, **kwargs: {"status": "failed", "can_continue": False, "dataframe": tagged},
    )

    result = runtime.run_table_guardrails(dataframe, "orders", target="source", schema="dbo")

    assert observed == [("orders", {"target": "source", "schema": "dbo"})]
    assert result["status"] == "failed"
    assert result["can_continue"] is False
