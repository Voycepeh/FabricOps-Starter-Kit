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

    monkeypatch.setattr(changes, "load_table_guardrail_rules", lambda *args, **kwargs: approved_rules)
    result = check_changes(Frame([row(at=now, count=2)], Spark()))

    assert result["status"] == status
    assert result["can_continue"] is can_continue
    assert result["severity"] == severity
    assert result_writes[0]["guardrail_type"] == "change"
    assert result_writes[0]["store_type"] == "warehouse"


def test_freshness_rejects_non_observation_input():
    with pytest.raises(ValueError, match="canonical evidence"):
        check_freshness([{"max_change_value": "2026-08-14"}])


def test_freshness_rejects_incomplete_observation_identity():
    incomplete = row()
    del incomplete["source_table"]

    with pytest.raises(ValueError, match="canonical evidence"):
        check_freshness([incomplete])


def test_freshness_result_preserves_warehouse_store_type(monkeypatch):
    observed = Frame([row(maximum="2999-08-14")], Spark())
    rules = [{
        "metadata_table_key": "key", "table_name": "orders", "guardrail_type": "freshness", "rule_type": "max_lag_days",
        "rule_parameters_json": '{"max_lag_days": 0}', "severity": "blocking",
        "activation_state": "active", "review_state": "governance_approved", "rule_key": "freshness_rule",
    }]
    writes = []
    monkeypatch.setattr(freshness, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(freshness, "get_store", lambda *args: types.SimpleNamespace(kind="warehouse"))
    monkeypatch.setattr(freshness, "write_guardrail_result_row", lambda **kwargs: writes.append(kwargs))
    monkeypatch.setattr(freshness, "load_table_guardrail_rules", lambda *args, **kwargs: rules)
    result = freshness.check_freshness(observed)
    assert result["status"] == "passed"
    assert writes[0]["store_type"] == "warehouse"


def test_freshness_rejects_rule_column_that_differs_from_observation(monkeypatch):
    observed = Frame([row(maximum="2999-08-14")], Spark())
    rules = [{
        "metadata_table_key": "key", "table_name": "orders", "guardrail_type": "freshness", "rule_type": "max_lag_days",
        "rule_parameters_json": '{"freshness_column": "loaded_at", "max_lag_days": 0}',
        "activation_state": "active", "review_state": "governance_approved", "rule_key": "freshness_rule",
    }]
    monkeypatch.setattr(freshness, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(freshness, "load_table_guardrail_rules", lambda *args, **kwargs: rules)
    with pytest.raises(ValueError, match="does not match change_column 'modified_at'"):
        freshness.check_freshness(observed)


@pytest.mark.parametrize(("behaviour", "expected_pattern", "expected_status"), [
    ("Incremental append", "incremental_append", "failed"),
    ("Snapshot overwrite", "snapshot", "passed"),
])
def test_authored_change_behaviour_drives_observation_runtime_semantics(monkeypatch, behaviour, expected_pattern, expected_status):
    """Use the authored source pattern during canonical observation comparison."""
    import json

    now = datetime(2026, 8, 14, tzinfo=UTC)
    configure(monkeypatch, [row(at=now - timedelta(hours=1))])
    rules = [{
        "metadata_table_key": "key", "table_name": "orders", "guardrail_type": "change",
        "rule_type": "monitor_only", "rule_parameters_json": json.dumps({"change_behaviour": behaviour}),
        "severity": "blocking", "activation_state": "active", "review_state": "authored",
        "configuration_version": 2, "rule_key": "authored_change_rule",
    }]
    monkeypatch.setattr(changes, "load_table_guardrail_rules", lambda *args, **kwargs: rules)
    result = check_changes(Frame([row(at=now, count=2)], Spark()))
    assert result["source_pattern"] == expected_pattern
    assert result["pattern_semantics"] == ("append_only" if expected_pattern == "incremental_append" else "full_state")
    assert result["status"] == expected_status
    assert result["append_violation_count"] == (1 if expected_pattern == "incremental_append" else 0)


def test_changes_requires_active_approved_change_rule(monkeypatch):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    configure(monkeypatch, [row(at=now - timedelta(hours=1))])
    monkeypatch.setattr(changes, "load_table_guardrail_rules", lambda *args, **kwargs: [])

    with pytest.raises(ValueError, match="No active approved change rule exists for 'key'"):
        check_changes(Frame([row(at=now)], Spark()))


def test_governed_guardrail_public_signatures_are_minimal():
    import inspect
    from fabricops_kit import check_schema

    assert str(inspect.signature(check_schema)) == "(table_name: str, *, target: str = 'source', schema: str | None = None) -> dict"
    assert str(inspect.signature(check_freshness)) == "(observation) -> dict"
    assert str(inspect.signature(check_changes)) == "(observation) -> dict"


def test_schema_resolves_table_rule_and_writes_governed_result(monkeypatch):
    schema_module = importlib.import_module("fabricops_kit.pipeline.check_schema")
    frame = types.SimpleNamespace(limit=lambda count: types.SimpleNamespace(columns=["id"]))
    config = object()
    store = types.SimpleNamespace(kind="lakehouse")
    rules = [{"rule_key": "schema_rule"}]
    writes = []
    core_calls = []

    monkeypatch.setattr(schema_module, "resolve_fabric_context", lambda: (config, "dev", {"active": True}))
    monkeypatch.setattr(schema_module, "get_store", lambda *args: store)
    monkeypatch.setattr(schema_module, "get_spark_session", lambda: "spark")
    monkeypatch.setattr(schema_module, "resolve_lakehouse_table_location", lambda *args: ("orders", "dbo", "path"))
    monkeypatch.setattr(schema_module, "read_lakehouse_table_core", lambda *args, **kwargs: frame)
    monkeypatch.setattr(schema_module, "build_metadata_table_key", lambda *args: "lakehouse||source||dbo||orders")
    monkeypatch.setattr(schema_module, "load_table_guardrail_rules", lambda *args, **kwargs: rules)
    monkeypatch.setattr(schema_module, "select_table_guardrail_rule", lambda *args, **kwargs: rules[0])

    def fake_core(dataframe, **kwargs):
        core_calls.append((dataframe, kwargs))
        return {"status": "passed", "can_continue": True, "rule_key": "schema_rule", "rule_type": "required_columns"}

    monkeypatch.setattr(schema_module, "schema_check_core", fake_core)
    monkeypatch.setattr(schema_module, "write_guardrail_result_row", lambda **kwargs: writes.append(kwargs))

    result = schema_module.check_schema("orders", target="source", schema="dbo")

    assert result["status"] == "passed"
    assert core_calls[0][1]["metadata_table_key"] == "lakehouse||source||dbo||orders"
    assert writes[0]["guardrail_type"] == "schema"
    assert writes[0]["table_name"] == "orders"
