"""Regression tests for target-aware incremental pipeline state."""
# ruff: noqa: D102, D103, D107

from __future__ import annotations

from datetime import UTC, datetime
from importlib import import_module

import pytest

from fabricops_kit.pipeline import shared

read_module = import_module("fabricops_kit.pipeline.pipeline_read")


class Frame:
    """Small collectable test frame."""

    def __init__(self, rows=()):
        self.rows = list(rows)

    def collect(self):
        return self.rows


def _row(*, target: str, maximum: str, committed_at: int = 1):
    return {
        "observation_id": f"observation-{target}-{maximum}",
        "source_table_id": "source-orders",
        "target_table_id": target,
        "environment_name": "dev",
        "partition_value": maximum,
        "row_count": 1,
        "min_change_value": maximum,
        "max_change_value": maximum,
        "content_fingerprint": f"hash-{maximum}",
        "is_present": True,
        "observation_status": "committed",
        "_committed_at": datetime(2026, 1, committed_at, tzinfo=UTC),
    }


def _current(maximum: str):
    return Frame([{**_row(target="", maximum=maximum), "observation_status": "observed"}])


def _configure_scope(monkeypatch, history):
    shared._PENDING_SOURCE_OBSERVATIONS.clear()
    shared._INCREMENTAL_SOURCE_SCOPES.clear()
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda context=None: (object(), "dev", {}))
    monkeypatch.setattr(
        shared,
        "build_runtime_audit_fields",
        lambda **kwargs: {"_activity_id": "run-1"},
    )
    monkeypatch.setattr(shared, "metadata_table_physical_schema", lambda *args: "engineering")
    monkeypatch.setattr(shared, "read_lakehouse_table", lambda *args, **kwargs: Frame(history))
    monkeypatch.setattr(shared, "load_table_guardrail_rules", lambda *args, **kwargs: [object()])
    monkeypatch.setattr(shared, "select_table_guardrail_rule", lambda *args, **kwargs: object())
    monkeypatch.setattr(
        shared,
        "resolve_source_drift_observation_columns",
        lambda rule: ("watermark", "watermark"),
    )


def test_incremental_read_requires_target_before_context_resolution(monkeypatch):
    monkeypatch.setattr(
        read_module,
        "resolve_fabric_context",
        lambda: pytest.fail("target validation must happen before runtime access"),
    )
    with pytest.raises(ValueError, match="target_table_id is required"):
        read_module.pipeline_read(table_id="source-orders", read_mode="incremental")


def test_full_read_keeps_complete_read_contract(monkeypatch):
    identity = {
        "table_id": "source-orders",
        "store_type": "lakehouse",
        "store": "Bronze",
        "schema": "demo",
        "table_name": "orders",
    }
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(read_module, "resolve_catalogue_table_identity", lambda *args, **kwargs: identity)
    monkeypatch.setattr(read_module, "resolve_pipeline_data_contract", lambda *args, **kwargs: None)
    monkeypatch.setattr(read_module, "read_lakehouse_table", lambda *args, **kwargs: "complete-frame")
    result = read_module.pipeline_read(table_id="source-orders", read_mode="full", verbose=False)
    assert result["dataframe"] == "complete-frame"
    assert result["read_mode"] == "full"
    assert result["should_process"] is True
    assert result["scope"] == {"type": "full", "first_run": False}


def test_first_incremental_run_bootstraps_with_complete_scope(monkeypatch):
    _configure_scope(monkeypatch, [])
    result = shared.resolve_incremental_source_scope(
        source_table_id="source-orders",
        target_table_id="target-a",
        observation=_current("120"),
    )
    assert result["type"] == "full"
    assert result["first_run"] is True
    assert result["has_data"] is True


def test_same_source_resolves_isolated_target_watermarks(monkeypatch):
    _configure_scope(monkeypatch, [_row(target="target-a", maximum="120"), _row(target="target-b", maximum="100")])
    target_a = shared.resolve_incremental_source_scope(
        source_table_id="source-orders", target_table_id="target-a", observation=_current("120")
    )
    target_b = shared.resolve_incremental_source_scope(
        source_table_id="source-orders", target_table_id="target-b", observation=_current("120")
    )
    assert target_a["after"] == "120"
    assert target_a["has_data"] is False
    assert target_b["after"] == "100"
    assert target_b["through"] == "120"
    assert target_b["has_data"] is True


def test_numeric_watermarks_are_ordered_numerically(monkeypatch):
    _configure_scope(monkeypatch, [_row(target="target-a", maximum="9")])
    result = shared.resolve_incremental_source_scope(
        source_table_id="source-orders", target_table_id="target-a", observation=_current("100")
    )
    assert result["has_data"] is True
    assert result["after"] == "9"
    assert result["through"] == "100"


def test_project_query_cannot_bypass_incremental_contract():
    with pytest.raises(ValueError, match="query cannot be combined"):
        read_module.pipeline_read(
            table_id="source-orders",
            query="SELECT * FROM dbo.orders",
            read_mode="incremental",
            target_table_id="target-a",
        )


def test_multiple_incremental_sources_are_staged_independently(monkeypatch):
    _configure_scope(monkeypatch, [])
    shared.resolve_incremental_source_scope(
        source_table_id="source-orders", target_table_id="target-a", observation=_current("120")
    )
    current_payments = Frame([
        {**_row(target="", maximum="55"), "source_table_id": "source-payments", "observation_status": "observed"}
    ])
    shared.resolve_incremental_source_scope(
        source_table_id="source-payments", target_table_id="target-a", observation=current_payments
    )
    assert set(
        shared.incremental_publication_scopes(
            environment_name="dev",
            activity_id="run-1",
            target_table_id="target-a",
            source_table_ids=["source-orders", "source-payments", "source-products"],
        ).keys()
    ) == {"source-orders", "source-payments"}


def test_partition_scope_selects_only_changed_partitions(monkeypatch):
    history = [
        {**_row(target="target-a", maximum="10"), "partition_value": "2026-01-01", "content_fingerprint": "old"},
        {**_row(target="target-a", maximum="20"), "partition_value": "2026-01-02", "content_fingerprint": "same"},
    ]
    _configure_scope(monkeypatch, history)
    monkeypatch.setattr(
        shared,
        "resolve_source_drift_observation_columns",
        lambda rule: ("business_date", "changed_at"),
    )
    current = Frame([
        {**history[0], "target_table_id": "", "observation_status": "observed", "content_fingerprint": "new"},
        {**history[1], "target_table_id": "", "observation_status": "observed"},
    ])
    result = shared.resolve_incremental_source_scope(
        source_table_id="source-orders", target_table_id="target-a", observation=current
    )
    assert result["type"] == "partitions"
    assert result["values"] == ["2026-01-01"]
