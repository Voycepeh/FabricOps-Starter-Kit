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
    return Frame([{
        **_row(target="", maximum=maximum),
        "observation_status": "observed",
        "partition_column": "watermark",
        "change_column": "watermark",
    }])


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


def test_incremental_pipeline_read_uses_processing_without_source_drift(monkeypatch):
    identity = {
        "table_id": "source-orders",
        "store_type": "lakehouse",
        "store": "Bronze",
        "schema": "demo",
        "table_name": "orders",
        "load_strategy": "append",
        "load_strategy_parameters_json": '{"watermark_column":"processed_at"}',
    }
    captured = []
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(read_module, "resolve_catalogue_table_identity", lambda *a, **k: identity)
    monkeypatch.setattr(read_module, "resolve_pipeline_data_contract", lambda *a, **k: {"contract_payload": {"table": {"processing": {"load_strategy": "append", "watermark_column": "processed_at"}}}})
    monkeypatch.setattr(read_module, "read_lakehouse_table", lambda *a, **k: "complete-frame")
    monkeypatch.setattr(
        read_module,
        "capture_source_observation",
        lambda **kwargs: captured.append(kwargs) or "progress-observation",
    )
    monkeypatch.setattr(
        read_module,
        "resolve_incremental_source_scope",
        lambda **kwargs: {"type": "watermark", "first_run": False, "has_data": False},
    )
    monkeypatch.setattr(read_module, "_filter_lakehouse_incremental", lambda frame, scope: "empty-frame")

    result = read_module.pipeline_read(
        table_id="source-orders",
        read_mode="incremental",
        target_table_id="target-orders",
        verbose=False,
    )

    assert captured[0]["incremental_columns"] == ("processed_at", "processed_at")
    assert result["dataframe"] == "empty-frame"


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


def test_incremental_columns_come_from_processing_without_source_drift():
    identity = {
        "load_strategy": "append",
        "load_strategy_parameters_json": '{"watermark_column":"processed_at"}',
    }

    assert shared.resolve_incremental_observation_columns(identity, None) == (
        "processed_at",
        "processed_at",
    )


def test_incremental_processing_column_can_differ_from_source_drift():
    contract = {
        "contract_payload": {
            "table": {
                "processing": {
                    "load_strategy": "append",
                    "watermark_column": "processed_at",
                }
            },
            "guardrails": [
                {
                    "guardrail_type": "source_drift",
                    "rule_parameters": {"change_column": "updated_at"},
                }
            ],
        }
    }

    assert shared.resolve_incremental_observation_columns({}, contract) == (
        "processed_at",
        "processed_at",
    )


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


def test_next_activity_recovers_staged_progress_from_materialized_target(monkeypatch):
    """A new scheduled activity accepts durable prior evidence before scoping."""
    staged_a = {
        **_row(target="target-a", maximum="120"),
        "observation_status": "observed",
        "_activity_id": "run-a",
    }
    staged_b = {
        **_row(target="target-b", maximum="90"),
        "observation_status": "observed",
        "_activity_id": "run-a",
    }
    history = [staged_a, staged_b]
    _configure_scope(monkeypatch, history)
    monkeypatch.setattr(
        shared, "build_runtime_audit_fields", lambda **kwargs: {"_activity_id": "run-b"}
    )
    monkeypatch.setattr(
        shared,
        "resolve_catalogue_table_identity",
        lambda _config, _env, table_id, **_kwargs: {"table_id": table_id},
    )
    monkeypatch.setattr(
        shared,
        "_physical_target_has_activity",
        lambda identity, activity_id, **_kwargs: identity["table_id"] == "target-a" and activity_id == "run-a",
    )
    merged = []
    monkeypatch.setattr(
        shared,
        "_merge_source_observation_records",
        lambda records, **_kwargs: merged.extend(records),
    )
    shared._PENDING_SOURCE_OBSERVATIONS.clear()
    shared._PENDING_SOURCE_DRIFT_OBSERVATIONS.clear()
    shared._INCREMENTAL_SOURCE_SCOPES.clear()

    scope_a = shared.resolve_incremental_source_scope(
        source_table_id="source-orders", target_table_id="target-a", observation=_current("130")
    )
    scope_b = shared.resolve_incremental_source_scope(
        source_table_id="source-orders", target_table_id="target-b", observation=_current("130")
    )

    assert scope_a["after"] == "120"
    assert scope_a["through"] == "130"
    assert scope_b["first_run"] is True
    assert {(row["target_table_id"], row["observation_status"]) for row in merged} == {
        ("target-a", "committed")
    }


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
        {
            **_row(target="", maximum="55"),
            "source_table_id": "source-payments",
            "observation_status": "observed",
            "partition_column": "watermark",
            "change_column": "watermark",
        }
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
    current = Frame([
        {
            **history[0],
            "target_table_id": "",
            "observation_status": "observed",
            "content_fingerprint": "new",
            "partition_column": "business_date",
            "change_column": "changed_at",
        },
        {
            **history[1],
            "target_table_id": "",
            "observation_status": "observed",
            "partition_column": "business_date",
            "change_column": "changed_at",
        },
    ])
    result = shared.resolve_incremental_source_scope(
        source_table_id="source-orders", target_table_id="target-a", observation=current
    )
    assert result["type"] == "partitions"
    assert result["values"] == ["2026-01-01"]


def test_partition_scope_includes_removed_partition_as_work(monkeypatch):
    """A removal-only observation remains actionable incremental work."""
    history = [
        {
            **_row(target="target-a", maximum="18"),
            "partition_value": "2026-09-18",
            "content_fingerprint": "removed",
        },
        {
            **_row(target="target-a", maximum="19"),
            "partition_value": "2026-09-19",
            "content_fingerprint": "unchanged",
        },
    ]
    _configure_scope(monkeypatch, history)
    current = Frame([
        {
            **history[1],
            "target_table_id": "",
            "observation_status": "observed",
            "partition_column": "business_date",
            "change_column": "changed_at",
        }
    ])

    result = shared.resolve_incremental_source_scope(
        source_table_id="source-orders",
        target_table_id="target-a",
        observation=current,
    )

    assert result == {
        "type": "partitions",
        "first_run": False,
        "has_data": True,
        "column": "business_date",
        "values": ["2026-09-18"],
        "removed_values": ["2026-09-18"],
    }
    pending = shared._PENDING_SOURCE_OBSERVATIONS[
        ("dev", "run-1", "source-orders", "target-a")
    ]
    assert any(
        row["partition_value"] == "2026-09-18" and row["is_present"] is False
        for row in pending
    )
