"""Behavioral tests for write-side source-to-target stability."""
# ruff: noqa: D103
from __future__ import annotations

from datetime import UTC, datetime, timedelta
import json

import pytest

from fabricops_kit.pipeline import shared


NOW = datetime(2026, 9, 13, tzinfo=UTC)


def row(*, target="", count=2, at=NOW, status="observed"):
    return {
        "observation_id": "snapshot",
        "source_table_id": "source",
        "target_table_id": target,
        "environment_name": "dev",
        "partition_value": "p1",
        "row_count": count,
        "min_change_value": "1",
        "max_change_value": "2",
        "content_fingerprint": f"fingerprint-{count}",
        "is_present": True,
        "observation_status": status,
        "_committed_at": at,
        "_activity_id": "run",
    }


def rule():
    return {
        "guardrail_rule_id": "stability",
        "guardrail_version": 1,
        "table_id": "source",
        "environment_name": "dev",
        "guardrail_type": "source_stability",
        "rule_type": "historical_mutation",
        "rule_parameters_json": json.dumps({"partition_column": "partition", "change_column": "changed"}),
        "action": "Block",
        "is_active": True,
    }


def configure(monkeypatch, history):
    shared._CURRENT_SOURCE_OBSERVATIONS.clear()
    shared._PENDING_SOURCE_OBSERVATIONS.clear()
    shared.set_current_source_observation(
        environment_name="dev", activity_id="run", table_id="source", observation=[row()]
    )
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda context=None: (object(), "dev", {}))
    monkeypatch.setattr(shared, "build_runtime_audit_fields", lambda **kwargs: {"_activity_id": "run"})
    monkeypatch.setattr(shared, "metadata_table_physical_schema", lambda *args: None)
    monkeypatch.setattr(shared, "read_lakehouse_table", lambda *args, **kwargs: history)
    monkeypatch.setattr(shared, "load_table_guardrail_rules", lambda *args, **kwargs: [rule()])
    monkeypatch.setattr(shared, "write_guardrail_result_row", lambda **kwargs: None)


def test_target_baselines_and_load_strategies_are_independent(monkeypatch):
    history = [
        row(target="target-append", count=1, at=NOW - timedelta(hours=1), status="committed"),
        row(target="target-overwrite", count=1, at=NOW - timedelta(hours=1), status="committed"),
    ]
    configure(monkeypatch, history)
    with pytest.raises(RuntimeError, match="append"):
        shared.check_source_stability_for_target(
            source_table_id="source", target_table_id="target-append",
            target_processing={"load_strategy": "append"},
        )
    result = shared.check_source_stability_for_target(
        source_table_id="source", target_table_id="target-overwrite",
        target_processing={"load_strategy": "overwrite"},
    )
    assert result["can_continue"] is True
    assert result["target_table_id"] == "target-overwrite"


def test_success_for_one_target_does_not_advance_another(monkeypatch):
    configure(monkeypatch, [])
    shared.check_source_stability_for_target(
        source_table_id="source", target_table_id="target-a",
        target_processing={"load_strategy": "append"},
    )
    assert ("dev", "run", "source", "target-a") in shared._PENDING_SOURCE_OBSERVATIONS
    assert ("dev", "run", "source", "target-b") not in shared._PENDING_SOURCE_OBSERVATIONS


def test_same_read_snapshot_is_reusable_for_two_targets(monkeypatch):
    configure(monkeypatch, [])
    first = shared.get_current_source_observation(
        environment_name="dev", activity_id="run", table_id="source"
    )
    for target in ("target-a", "target-b"):
        shared.check_source_stability_for_target(
            source_table_id="source", target_table_id=target,
            target_processing={"load_strategy": "append"},
        )
    assert shared.get_current_source_observation(
        environment_name="dev", activity_id="run", table_id="source"
    ) is first
    assert {key[-1] for key in shared._PENDING_SOURCE_OBSERVATIONS} == {"target-a", "target-b"}
