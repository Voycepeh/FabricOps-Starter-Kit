"""Tests for guardrail paths over normalized source-observation evidence."""
# ruff: noqa: D101, D102, D103, D105, D107
from __future__ import annotations

from datetime import UTC, datetime, timedelta
import importlib
import types

import pytest

changes = importlib.import_module("fabricops_kit.pipeline.check_changes")
freshness = importlib.import_module("fabricops_kit.pipeline.check_freshness")
from fabricops_kit import check_changes, check_freshness


def row(
    partition="a",
    *,
    at=None,
    count=1,
    minimum="2026-08-13",
    maximum="2026-08-14",
    present=True,
    table_id="key",
    environment_name="dev",
    observation_id="observation-1",
    activity_id="activity-1",
):
    return {
        "observation_id": observation_id,
        "table_id": table_id,
        "environment_name": environment_name,
        "partition_value": partition,
        "row_count": count,
        "min_change_value": minimum,
        "max_change_value": maximum,
        "is_present": present,
        "_committed_at": at or datetime(2026, 8, 14, tzinfo=UTC),
        "_activity_id": activity_id,
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


def change_rule(*, severity="blocking", rule_type="monitor_only", behaviour=None):
    parameters = (
        '{"partition_column":"business_date","change_column":"modified_at"}'
        if behaviour is None
        else f'{{"partition_column":"business_date","change_column":"modified_at","change_behaviour":"{behaviour}"}}'
    )
    return {
        "table_id": "key",
        "table_name": "orders",
        "environment_name": "dev",
        "guardrail_type": "change",
        "rule_type": rule_type,
        "rule_parameters_json": parameters,
        "severity": severity,
        "is_active": True,
        "guardrail_rule_id": f"change_{rule_type}_{severity}",
        "guardrail_version": 1,
        "rule_id": f"change_{rule_type}_{severity}",
    }


def freshness_rule(*, freshness_column="modified_at", max_lag_days=0):
    return {
        "table_id": "key",
        "table_name": "orders",
        "environment_name": "dev",
        "guardrail_type": "freshness",
        "rule_type": "max_lag_days",
        "rule_parameters_json": (
            f'{{"freshness_column":"{freshness_column}","max_lag_days":{max_lag_days}}}'
        ),
        "severity": "blocking",
        "is_active": True,
        "guardrail_rule_id": "freshness_rule",
        "guardrail_version": 1,
        "rule_id": "freshness_rule",
    }


def _audit(at=None, activity_id="activity-tombstone"):
    return {
        "_committed_by": "tester@example.com",
        "_committed_at": at or datetime(2026, 8, 14, tzinfo=UTC),
        "_workspace_id": "workspace-id",
        "_workspace_name": "workspace-name",
        "_notebook_id": "notebook-id",
        "_notebook_name": "02_pipeline",
        "_metadata_lakehouse_name": "metadata",
        "_activity_id": activity_id,
    }


def configure_changes(monkeypatch, history, rules=None):
    monkeypatch.setattr(changes, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(changes, "configured_lakehouse_schema", lambda *args: None)
    monkeypatch.setattr(changes, "read_lakehouse_table_core", lambda *args, **kwargs: Frame(history))
    written = []
    monkeypatch.setattr(changes, "write_lakehouse_table_core", lambda frame, *args, **kwargs: written.extend(frame.collect()))
    monkeypatch.setattr(changes, "build_runtime_audit_fields", lambda **kwargs: _audit())
    monkeypatch.setattr(changes, "write_guardrail_result_row", lambda **kwargs: None)
    monkeypatch.setattr(changes, "load_table_guardrail_rules", lambda *args, **kwargs: rules or [change_rule()])
    monkeypatch.setattr(changes, "resolve_catalogue_table_identity", lambda *args, **kwargs: {
        "table_id": args[2], "store_type": "lakehouse", "target": "source", "schema": "dbo",
        "table_name": "orders", "load_strategy": "overwrite", "load_strategy_parameters_json": "{}",
    })
    monkeypatch.setattr(changes, "resolve_table_processing_definition", lambda *args, **kwargs: {
        "load_strategy": "overwrite", "source": "current_authoring",
    })
    return written


def configure_freshness(monkeypatch, rules=None):
    configured_rules = rules or [freshness_rule(), change_rule()]
    monkeypatch.setattr(freshness, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(freshness, "get_spark_session", lambda: Spark())
    monkeypatch.setattr(freshness, "load_table_guardrail_rules", lambda *args, **kwargs: configured_rules)
    monkeypatch.setattr(freshness, "write_guardrail_result_row", lambda **kwargs: None)
    monkeypatch.setattr(freshness, "resolve_catalogue_table_identity", lambda *args, **kwargs: {
        "table_id": args[2], "store_type": "lakehouse", "target": "source", "schema": "dbo", "table_name": "orders",
    })


def test_first_observation_and_current_snapshot_is_not_its_own_baseline(monkeypatch):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    configure_changes(monkeypatch, [row(at=now)])
    result = check_changes(Frame([row(at=now)], Spark()))
    assert result["first_observation"] is True
    assert result["new_partitions"] == ["a"]


def test_observation_checks_pass_development_contract_context_to_rule_loader(monkeypatch):
    """Route freshness and changes through the shared context-aware rule loader."""
    now = datetime(2026, 8, 14, tzinfo=UTC)
    context = {"data_contract_overrides": {"table-a": {"contract_id": "contract-a", "contract_version": 2}}}
    captured = {}

    configure_freshness(monkeypatch)
    monkeypatch.setattr(freshness, "resolve_fabric_context", lambda: (object(), "dev", context))
    def load_freshness(*args, **kwargs):
        captured["freshness"] = kwargs
        return [freshness_rule(), change_rule()]

    monkeypatch.setattr(freshness, "load_table_guardrail_rules", load_freshness)
    freshness.check_freshness(Frame([row(at=now)], Spark()))

    configure_changes(monkeypatch, [row(at=now)])
    monkeypatch.setattr(changes, "resolve_fabric_context", lambda: (object(), "dev", context))
    def load_changes(*args, **kwargs):
        captured["changes"] = kwargs
        return [change_rule()]

    monkeypatch.setattr(changes, "load_table_guardrail_rules", load_changes)
    check_changes(Frame([row(at=now)], Spark()))
    assert captured["freshness"]["context"] is context
    assert captured["changes"]["context"] is context


def test_previous_comparable_snapshot_is_selected_by_table_and_environment(monkeypatch):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    previous = now - timedelta(hours=1)
    history = [
        row("a", at=previous),
        row("removed", at=previous),
        row("unrelated", at=previous, table_id="other"),
        row("prod", at=previous, environment_name="prod"),
    ]
    written = configure_changes(monkeypatch, history)
    result = check_changes(
        Frame(
            [
                row("a", at=now, count=2, observation_id="current"),
                row("new", at=now, observation_id="current"),
            ],
            Spark(),
        )
    )
    assert result["changed_partitions"] == ["a"]
    assert result["new_partitions"] == ["new"]
    assert result["removed_partitions"] == ["removed"]
    assert written[0]["is_present"] is False and written[0]["row_count"] == 0
    assert written[0]["environment_name"] == "dev"


def test_unchanged_and_reappeared_observations(monkeypatch):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    previous = now - timedelta(hours=1)
    configure_changes(monkeypatch, [row(at=previous)])
    assert check_changes(Frame([row(at=now)], Spark()))["changed"] is False
    configure_changes(monkeypatch, [row(at=previous, present=False)])
    assert check_changes(Frame([row(at=now)], Spark()))["reappeared_partitions"] == ["a"]


@pytest.mark.parametrize(
    ("severity", "status", "can_continue"),
    [("blocking", "failed", False), ("warning", "warning", True)],
)
def test_approved_changes_rule_governs_continuation(monkeypatch, severity, status, can_continue):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    rules = [change_rule(severity=severity, rule_type="no_change_required")]
    configure_changes(monkeypatch, [row(at=now - timedelta(hours=1))], rules)
    result_writes = []
    monkeypatch.setattr(changes, "write_guardrail_result_row", lambda **kwargs: result_writes.append(kwargs))
    result = check_changes(Frame([row(at=now, count=2)], Spark()))
    assert result["status"] == status
    assert result["can_continue"] is can_continue
    assert result["severity"] == severity
    assert result["guardrail_version"] == 1
    assert result_writes[0]["guardrail_type"] == "change"


def test_changes_rejects_cross_environment_observation(monkeypatch):
    monkeypatch.setattr(changes, "resolve_fabric_context", lambda: (object(), "dev", {}))
    with pytest.raises(ValueError, match="does not match active environment"):
        check_changes(Frame([row(environment_name="prod")], Spark()))


def test_freshness_rejects_non_observation_input():
    with pytest.raises(ValueError, match="canonical evidence"):
        check_freshness([{"max_change_value": "2026-08-14"}])


def test_freshness_rejects_incomplete_observation_identity():
    incomplete = row()
    del incomplete["table_id"]
    with pytest.raises(ValueError, match="canonical evidence"):
        check_freshness([incomplete])


def test_freshness_uses_change_rule_only_to_resolve_observation_column(monkeypatch):
    observed = Frame([row(maximum="2999-08-14")], Spark())
    configure_freshness(monkeypatch)
    result = freshness.check_freshness(observed)
    assert result["status"] == "passed"
    assert result["guardrail_version"] == 1


def test_freshness_rejects_rule_column_that_differs_from_observation(monkeypatch):
    observed = Frame([row(maximum="2999-08-14")], Spark())
    configure_freshness(monkeypatch, [freshness_rule(freshness_column="loaded_at"), change_rule()])
    with pytest.raises(ValueError, match="does not match change_column 'modified_at'"):
        freshness.check_freshness(observed)


@pytest.mark.parametrize(
    ("behaviour", "expected_pattern", "expected_status"),
    [("Incremental append", "incremental_append", "failed"), ("Snapshot overwrite", "snapshot", "passed")],
)
def test_authored_change_behaviour_drives_observation_runtime_semantics(
    monkeypatch, behaviour, expected_pattern, expected_status
):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    rules = [change_rule(behaviour=behaviour)]
    configure_changes(monkeypatch, [row(at=now - timedelta(hours=1))], rules)
    result = check_changes(Frame([row(at=now, count=2)], Spark()))
    assert result["source_pattern"] == expected_pattern
    assert result["pattern_semantics"] == (
        "append_only" if expected_pattern == "incremental_append" else "full_state"
    )
    assert result["status"] == expected_status


def test_changes_requires_active_change_rule(monkeypatch):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    configure_changes(monkeypatch, [row(at=now - timedelta(hours=1))], rules=[])
    monkeypatch.setattr(changes, "load_table_guardrail_rules", lambda *args, **kwargs: [])
    with pytest.raises(ValueError, match="No active approved change rule exists for 'key'"):
        check_changes(Frame([row(at=now)], Spark()))


def test_governed_guardrail_public_signatures_are_minimal():
    import inspect
    from fabricops_kit import check_schema

    assert str(inspect.signature(check_schema)) == "(table_id: str, *, dataframe=None) -> dict"
    assert str(inspect.signature(check_freshness)) == "(observation, *, table_id: str | None = None) -> dict"
    assert str(inspect.signature(check_changes)) == "(observation, *, table_id: str | None = None) -> dict"


def test_schema_resolves_table_rule_and_writes_governed_result(monkeypatch):
    schema_module = importlib.import_module("fabricops_kit.pipeline.check_schema")
    frame = types.SimpleNamespace(limit=lambda count: types.SimpleNamespace(columns=["id"]))
    config = object()
    store = types.SimpleNamespace(kind="lakehouse")
    rules = [{
        "guardrail_rule_id": "schema_rule",
        "guardrail_version": 2,
        "table_id": "lakehouse||source||dbo||orders",
        "guardrail_type": "schema",
        "is_active": True,
    }]
    writes = []
    core_calls = []

    monkeypatch.setattr(schema_module, "resolve_fabric_context", lambda: (config, "dev", {"active": True}))
    monkeypatch.setattr(schema_module, "get_store", lambda *args: store)
    monkeypatch.setattr(schema_module, "get_spark_session", lambda: "spark")
    monkeypatch.setattr(schema_module, "resolve_catalogue_table_identity", lambda *args, **kwargs: {
        "table_id": "catalogue-orders", "store_type": "lakehouse", "target": "source", "schema": "dbo", "table_name": "orders",
    })
    monkeypatch.setattr(schema_module, "resolve_lakehouse_table_location", lambda *args: ("orders", "dbo", "path"))
    monkeypatch.setattr(schema_module, "read_lakehouse_table_core", lambda *args, **kwargs: frame)
    loader_calls = []
    monkeypatch.setattr(
        schema_module, "load_table_guardrail_rules",
        lambda *args, **kwargs: loader_calls.append(kwargs) or rules,
    )
    monkeypatch.setattr(schema_module, "select_table_guardrail_rule", lambda *args, **kwargs: rules[0])

    def fake_core(dataframe, **kwargs):
        core_calls.append((dataframe, kwargs))
        return {"status": "passed", "can_continue": True, "guardrail_rule_id": "schema_rule", "rule_type": "required_columns"}

    monkeypatch.setattr(schema_module, "schema_check_core", fake_core)
    monkeypatch.setattr(schema_module, "write_guardrail_result_row", lambda **kwargs: writes.append(kwargs))
    result = schema_module.check_schema("catalogue-orders")
    assert result["status"] == "passed"
    assert result["guardrail_version"] == 2
    assert core_calls[0][1]["table_id"] == "catalogue-orders"
    assert writes[0]["guardrail_type"] == "schema"
    assert writes[0]["table_name"] == "orders"
    assert writes[0]["result"]["guardrail_version"] == 2
    assert loader_calls[0]["context"] == {"active": True}


def test_schema_uses_supplied_dataframe_without_changing_governed_identity(monkeypatch):
    schema_module = importlib.import_module("fabricops_kit.pipeline.check_schema")
    incoming = types.SimpleNamespace(columns=["id"])
    config = object()
    store = types.SimpleNamespace(kind="warehouse", schema="dbo")
    rules = [{
        "guardrail_rule_id": "schema_rule",
        "guardrail_version": 1,
        "table_id": "warehouse||product||sales||orders",
        "guardrail_type": "schema",
        "is_active": True,
    }]
    core_calls = []

    monkeypatch.setattr(schema_module, "resolve_fabric_context", lambda: (config, "prod", {}))
    monkeypatch.setattr(schema_module, "get_store", lambda *args: store)
    monkeypatch.setattr(schema_module, "get_spark_session", lambda: "spark")
    monkeypatch.setattr(schema_module, "resolve_warehouse_table_location", lambda *args: ("sales", "orders", "path"))
    monkeypatch.setattr(
        schema_module,
        "read_warehouse_query_core",
        lambda *args, **kwargs: pytest.fail("the persisted table must not be read"),
    )
    monkeypatch.setattr(schema_module, "resolve_catalogue_table_identity", lambda *args, **kwargs: {
        "table_id": "catalogue-orders", "store_type": "warehouse", "target": "product", "schema": "sales", "table_name": "orders",
    })
    monkeypatch.setattr(schema_module, "load_table_guardrail_rules", lambda *args, **kwargs: rules)
    monkeypatch.setattr(schema_module, "select_table_guardrail_rule", lambda *args, **kwargs: rules[0])
    monkeypatch.setattr(schema_module, "write_guardrail_result_row", lambda **kwargs: None)

    def fake_core(dataframe, **kwargs):
        core_calls.append((dataframe, kwargs))
        return {"status": "passed", "can_continue": True, "guardrail_rule_id": "schema_rule", "rule_type": "strict"}

    monkeypatch.setattr(schema_module, "schema_check_core", fake_core)
    schema_module.check_schema("catalogue-orders", dataframe=incoming)
    assert core_calls == [(
        incoming,
        {
            "rules_df": rules,
            "table_name": "orders",
            "environment_name": "prod",
            "table_id": "catalogue-orders",
        },
    )]


def test_schema_delegates_blocking_to_the_existing_guardrail_gate(monkeypatch):
    schema_module = importlib.import_module("fabricops_kit.pipeline.check_schema")
    result = {
        "status": "failed",
        "can_continue": False,
        "guardrail_rule_id": "rule",
        "guardrail_version": 1,
        "rule_type": "strict",
        "table_id": "governed-orders",
        "guardrail_type": "schema",
        "is_active": True,
    }
    events = []
    monkeypatch.setattr(schema_module, "resolve_fabric_context", lambda: (object(), "prod", {}))
    monkeypatch.setattr(schema_module, "get_store", lambda *args: types.SimpleNamespace(kind="lakehouse"))
    monkeypatch.setattr(schema_module, "get_spark_session", lambda: "spark")
    monkeypatch.setattr(schema_module, "resolve_lakehouse_table_location", lambda *args: ("orders", "dbo", "path"))
    monkeypatch.setattr(schema_module, "resolve_catalogue_table_identity", lambda *args, **kwargs: {
        "table_id": "catalogue-orders", "store_type": "lakehouse", "target": "product", "schema": "dbo", "table_name": "orders",
    })
    monkeypatch.setattr(schema_module, "load_table_guardrail_rules", lambda *args, **kwargs: [result])
    monkeypatch.setattr(schema_module, "select_table_guardrail_rule", lambda *args, **kwargs: result)
    monkeypatch.setattr(schema_module, "schema_check_core", lambda *args, **kwargs: result.copy())
    monkeypatch.setattr(schema_module, "write_guardrail_result_row", lambda **kwargs: events.append("recorded"))
    monkeypatch.setattr(schema_module, "stop_if_failed", lambda checked: events.append(("gate", checked["can_continue"])))
    schema_module.check_schema("catalogue-orders", dataframe=object())
    assert events == ["recorded", ("gate", False)]
