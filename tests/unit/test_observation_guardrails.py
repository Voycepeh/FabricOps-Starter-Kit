"""Tests for guardrail paths over canonical source-observation evidence."""
# ruff: noqa: D101, D102, D103, D105, D107
from __future__ import annotations

from datetime import UTC, datetime, timedelta
import importlib
import types

import pytest

changes = importlib.import_module("fabricops_kit.pipeline.check_changes")
freshness = importlib.import_module("fabricops_kit.pipeline.check_freshness")
from fabricops_kit import check_changes, check_freshness


def row(partition="a", *, at=None, count=1, minimum="2026-08-13", maximum="2026-08-14", present=True, key="key"):
    return {
        "metadata_table_key": key, "source_target": "source", "source_schema": "dbo",
        "source_table": "orders", "partition_column": "business_date",
        "partition_value": partition, "change_column": "modified_at", "row_count": count,
        "min_change_value": minimum, "max_change_value": maximum, "is_present": present,
        "observed_at": at or datetime(2026, 8, 14, tzinfo=UTC),
    }


class Frame:
    def __init__(self, rows, spark=None):
        self._rows = rows
        self.columns = list(rows[0]) if rows else list(row())
        self.sparkSession = spark

    def collect(self):
        return self._rows

    def __iter__(self):
        return iter(self._rows)


class Spark:
    def __init__(self): self.created = []
    def createDataFrame(self, rows, schema=None):
        frame = Frame(rows, self); self.created.append((frame, schema)); return frame


def configure(monkeypatch, history):
    monkeypatch.setattr(changes, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(changes, "configured_lakehouse_schema", lambda *args: None)
    monkeypatch.setattr(changes, "read_lakehouse_table_core", lambda *args, **kwargs: Frame(history))
    written = []
    monkeypatch.setattr(changes, "write_lakehouse_table_core", lambda frame, *args, **kwargs: written.extend(frame.collect()))
    monkeypatch.setattr(changes, "build_runtime_audit_fields", lambda **kwargs: {})
    monkeypatch.setattr(changes, "write_guardrail_result_row", lambda **kwargs: None)
    monkeypatch.setattr(changes, "get_store", lambda *args: types.SimpleNamespace(kind="warehouse"))
    monkeypatch.setattr(changes, "load_table_guardrail_rules", lambda *args, **kwargs: [{"metadata_table_key": "key", "table_name": "orders", "guardrail_type": "change", "rule_type": "monitor_only", "severity": "blocking", "activation_state": "active", "review_state": "governance_approved", "rule_key": "change_monitor"}])
    return written


def test_first_observation_and_current_snapshot_is_not_its_own_baseline(monkeypatch):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    configure(monkeypatch, [row(at=now)])
    result = check_changes(Frame([row(at=now)], Spark()))
    assert result["first_observation"] is True
    assert result["new_partitions"] == ["a"]
    assert result["status"] == "baseline_created"
    assert result["can_continue"] is True
    assert result["changed"] is False
    assert result["actual"]["changed"] is None
    assert result["guardrail_type"] == "change"


def test_previous_comparable_snapshot_is_selected_and_changes_are_classified(monkeypatch):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    previous = now - timedelta(hours=1)
    history = [row("a", at=previous), row("removed", at=previous), row("unrelated", at=previous, key="other")]
    written = configure(monkeypatch, history)
    result = check_changes(Frame([row("a", at=now, count=2), row("new", at=now)], Spark()))
    assert result["changed_partitions"] == ["a"]
    assert result["new_partitions"] == ["new"]
    assert result["removed_partitions"] == ["removed"]
    assert written[0]["is_present"] is False and written[0]["row_count"] == 0


def test_unchanged_and_reappeared_observations(monkeypatch):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    previous = now - timedelta(hours=1)
    configure(monkeypatch, [row(at=previous)])
    assert check_changes(Frame([row(at=now)], Spark()))["changed"] is False
    configure(monkeypatch, [row(at=previous, present=False)])
    assert check_changes(Frame([row(at=now)], Spark()))["reappeared_partitions"] == ["a"]


@pytest.mark.parametrize(("severity", "status", "can_continue"), [
    ("blocking", "failed", False),
    ("warning", "warning", True),
])
def test_approved_changes_rule_governs_continuation(monkeypatch, severity, status, can_continue):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    configure(monkeypatch, [row(at=now - timedelta(hours=1))])
    result_writes = []
    monkeypatch.setattr(changes, "write_guardrail_result_row", lambda **kwargs: result_writes.append(kwargs))
    approved_rules = [{
        "metadata_table_key": "key", "table_name": "orders", "guardrail_type": "change",
        "rule_type": "no_change_required", "severity": severity, "activation_state": "active",
        "review_state": "governance_approved", "rule_key": f"changes_{severity}",
    }]

    result = check_changes(Frame([row(at=now, count=2)], Spark()), rules_df=approved_rules, metadata_table_key="key")

    assert result["status"] == status
    assert result["can_continue"] is can_continue
    assert result["severity"] == severity
    assert result_writes[0]["guardrail_type"] == "change"
    assert result_writes[0]["store_type"] == "warehouse"


def test_freshness_uses_observed_maximum_without_source_scan():
    result = check_freshness(
        [{"max_change_value": "2026-08-14"}], freshness_column="max_change_value", max_lag_days=0,
        reference_date="2026-08-14",
    )
    assert result["status"] == "passed"
    assert result["freshness_column"] == "max_change_value"


def test_freshness_result_preserves_warehouse_store_type(monkeypatch):
    observed = Frame([row(maximum="2026-08-14")], Spark())
    rules = [{
        "metadata_table_key": "key", "table_name": "orders", "guardrail_type": "freshness", "rule_type": "max_lag_days",
        "rule_parameters_json": '{"max_lag_days": 0}', "severity": "blocking",
        "activation_state": "active", "review_state": "governance_approved", "rule_key": "freshness_rule",
    }]
    writes = []
    monkeypatch.setattr(freshness, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(freshness, "get_store", lambda *args: types.SimpleNamespace(kind="warehouse"))
    monkeypatch.setattr(freshness, "write_guardrail_result_row", lambda **kwargs: writes.append(kwargs))
    result = freshness.check_freshness(observed, rules_df=rules, reference_date="2026-08-14")
    assert result["status"] == "passed"
    assert writes[0]["store_type"] == "warehouse"


def test_freshness_rejects_rule_column_that_differs_from_observation(monkeypatch):
    observed = Frame([row(maximum="2026-08-14")], Spark())
    rules = [{
        "metadata_table_key": "key", "table_name": "orders", "guardrail_type": "freshness", "rule_type": "max_lag_days",
        "rule_parameters_json": '{"freshness_column": "loaded_at", "max_lag_days": 0}',
        "activation_state": "active", "review_state": "governance_approved", "rule_key": "freshness_rule",
    }]
    monkeypatch.setattr(freshness, "resolve_fabric_context", lambda: (object(), "dev", {}))
    with pytest.raises(ValueError, match="does not match change_column 'modified_at'"):
        freshness.check_freshness(observed, rules_df=rules, reference_date="2026-08-14")
