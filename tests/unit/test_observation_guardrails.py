"""Tests for guardrail paths over normalized source-observation evidence."""
# ruff: noqa: D101, D102, D103, D105, D107
from __future__ import annotations

from datetime import UTC, datetime, timedelta
import importlib
import json
import types

import pytest

stability = importlib.import_module("fabricops_kit.pipeline.check_source_stability")
freshness = importlib.import_module("fabricops_kit.pipeline.check_freshness")
from fabricops_kit import check_source_stability, check_freshness


def row(
    partition="a",
    *,
    at=None,
    count=1,
    minimum="2026-08-13",
    maximum="2026-08-14",
    present=True,
    table_id="key",
    target_table_id="target",
    environment_name="dev",
    observation_id="observation-1",
    activity_id="activity-1",
    fingerprint="fingerprint-1",
    status="observed",
    notebook_name="02_pipeline",
):
    return {
        "observation_id": observation_id,
        "source_table_id": table_id,
        "target_table_id": target_table_id,
        "environment_name": environment_name,
        "partition_value": partition,
        "row_count": count,
        "min_change_value": minimum,
        "max_change_value": maximum,
        "content_fingerprint": fingerprint,
        "is_present": present,
        "observation_status": status,
        "_committed_at": at or datetime(2026, 8, 14, tzinfo=UTC),
        "_activity_id": activity_id,
        "_notebook_name": notebook_name,
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


def stability_rule(*, severity="blocking"):
    parameters = json.dumps({
        "partition_column": "business_date",
        "change_column": "modified_at",
    })
    return {
        "table_id": "key",
        "table_name": "orders",
        "environment_name": "dev",
        "guardrail_type": "source_stability",
        "rule_type": "historical_mutation",
        "rule_parameters_json": parameters,
        "action": "Block" if severity == "blocking" else "Warn",
        "is_active": True,
        "guardrail_rule_id": f"source_stability_{severity}",
        "guardrail_version": 1,
        "rule_id": f"source_stability_{severity}",
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


def configure_stability(
    monkeypatch,
    history,
    rules=None,
    *,
    load_strategy="append",
    accepted_observation_id="auto",
    consumption_notebook="02_pipeline",
    consumption_target="target",
):
    monkeypatch.setattr(stability, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(stability, "metadata_table_physical_schema", lambda *args: None)
    def read_metadata(table_name, *args, **kwargs):
        del table_name, args, kwargs
        selected = None
        if history and accepted_observation_id == "auto":
            selected = min(history, key=lambda value: value["_committed_at"])["observation_id"]
        elif accepted_observation_id is not None:
            selected = accepted_observation_id
        return Frame([
            {
                **value,
                "observation_status": "committed" if value["observation_id"] == selected else "observed",
                "target_table_id": consumption_target if value["observation_id"] == selected else value["target_table_id"],
                "_notebook_name": consumption_notebook if value["observation_id"] == selected else value["_notebook_name"],
            }
            for value in history
        ])
    monkeypatch.setattr(stability, "read_lakehouse_table_core", read_metadata)
    written = []
    monkeypatch.setattr(stability, "write_lakehouse_table_core", lambda frame, *args, **kwargs: written.extend(frame.collect()))
    monkeypatch.setattr(stability, "build_runtime_audit_fields", lambda **kwargs: _audit())
    monkeypatch.setattr(stability, "write_guardrail_result_row", lambda **kwargs: None)
    monkeypatch.setattr(stability, "load_table_guardrail_rules", lambda *args, **kwargs: rules or [stability_rule()])
    monkeypatch.setattr(stability, "resolve_catalogue_table_identity", lambda *args, **kwargs: {
        "table_id": args[2], "store_type": "lakehouse", "target": "source", "schema": "dbo",
        "table_name": "orders", "load_strategy": "overwrite", "load_strategy_parameters_json": "{}",
    })
    monkeypatch.setattr(
        stability,
        "resolve_table_processing_definition",
        lambda *args, **kwargs: {"load_strategy": load_strategy, "source": "data_contract"},
    )
    return written


def configure_freshness(monkeypatch, rules=None):
    configured_rules = rules or [freshness_rule(), stability_rule()]
    monkeypatch.setattr(freshness, "resolve_pipeline_data_contract", lambda *args, **kwargs: {"contract_id": "contract"})
    monkeypatch.setattr(freshness, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(freshness, "get_spark_session", lambda: Spark())
    monkeypatch.setattr(freshness, "load_table_guardrail_rules", lambda *args, **kwargs: configured_rules)
    monkeypatch.setattr(freshness, "write_guardrail_result_row", lambda **kwargs: None)
    monkeypatch.setattr(freshness, "resolve_catalogue_table_identity", lambda *args, **kwargs: {
        "table_id": args[2], "store_type": "lakehouse", "target": "source", "schema": "dbo", "table_name": "orders",
    })


def test_first_observation_and_current_snapshot_is_not_its_own_baseline(monkeypatch):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    configure_stability(monkeypatch, [row(at=now)])
    result = check_source_stability(Frame([row(at=now)], Spark()), target_table_id="target")
    assert result["first_observation"] is True
    assert result["new_partitions"] == ["a"]


def test_raw_observation_does_not_become_accepted_baseline(monkeypatch):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    configure_stability(
        monkeypatch,
        [row(at=now - timedelta(hours=1), observation_id="unconsumed")],
        accepted_observation_id=None,
    )
    result = check_source_stability(
        Frame([row(at=now, observation_id="current")], Spark()),
        target_table_id="target",
    )
    assert result["first_observation"] is True


def test_latest_failed_observation_is_ignored_for_last_consumed_baseline(monkeypatch):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    history = [
        row(at=now - timedelta(hours=2), count=1, observation_id="accepted"),
        row(at=now - timedelta(hours=1), count=2, observation_id="failed"),
    ]
    configure_stability(monkeypatch, history, accepted_observation_id="accepted")
    result = check_source_stability(
        Frame([row(at=now, count=2, observation_id="current")], Spark()),
        target_table_id="target",
    )
    assert result["changed_partitions"] == ["a"]
    assert result["historical_mutation"] is True


@pytest.mark.parametrize(
    ("consumption_notebook", "consumption_target"),
    [("other_pipeline", "target"), ("02_pipeline", "other-target")],
)
def test_consumption_baselines_are_isolated_by_notebook_and_target(
    monkeypatch, consumption_notebook, consumption_target
):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    configure_stability(
        monkeypatch,
        [row(at=now - timedelta(hours=1), observation_id="other-consumer")],
        consumption_notebook=consumption_notebook,
        consumption_target=consumption_target,
    )
    result = check_source_stability(
        Frame([row(at=now, observation_id="current")], Spark()),
        target_table_id="target",
    )
    assert result["first_observation"] is True


def test_observation_checks_pass_development_contract_context_to_rule_loader(monkeypatch):
    """Route freshness and changes through the shared context-aware rule loader."""
    now = datetime(2026, 8, 14, tzinfo=UTC)
    context = {"data_contract_overrides": {"table-a": {"contract_id": "contract-a", "contract_version": 2}}}
    captured = {}

    configure_freshness(monkeypatch)
    monkeypatch.setattr(freshness, "resolve_fabric_context", lambda: (object(), "dev", context))
    def load_freshness(*args, **kwargs):
        captured["freshness"] = kwargs
        return [freshness_rule(), stability_rule()]

    monkeypatch.setattr(freshness, "load_table_guardrail_rules", load_freshness)
    freshness.check_freshness(Frame([row(at=now)], Spark()))

    configure_stability(monkeypatch, [row(at=now)])
    monkeypatch.setattr(stability, "resolve_fabric_context", lambda: (object(), "dev", context))
    def load_stability(*args, **kwargs):
        captured["source_stability"] = kwargs
        return [stability_rule()]

    monkeypatch.setattr(stability, "load_table_guardrail_rules", load_stability)
    check_source_stability(Frame([row(at=now)], Spark()), target_table_id="target")
    assert captured["freshness"]["context"] is context
    assert captured["source_stability"]["context"] is context


def test_previous_comparable_snapshot_is_selected_by_table_and_environment(monkeypatch):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    previous = now - timedelta(hours=1)
    history = [
        row("a", at=previous),
        row("removed", at=previous),
        row("unrelated", at=previous, table_id="other"),
        row("prod", at=previous, environment_name="prod"),
    ]
    written = configure_stability(monkeypatch, history)
    result = check_source_stability(
        Frame(
            [
                row("a", at=now, count=2, observation_id="current"),
                row("new", at=now, observation_id="current"),
            ],
            Spark(),
        ),
        target_table_id="target",
    )
    assert result["changed_partitions"] == ["a"]
    assert result["new_partitions"] == ["new"]
    assert result["removed_partitions"] == ["removed"]
    assert written[0]["is_present"] is False and written[0]["row_count"] == 0
    assert written[0]["environment_name"] == "dev"


def test_unchanged_and_reappeared_observations(monkeypatch):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    previous = now - timedelta(hours=1)
    configure_stability(monkeypatch, [row(at=previous)])
    assert check_source_stability(Frame([row(at=now)], Spark()), target_table_id="target")["changed"] is False
    configure_stability(monkeypatch, [row(at=previous, present=False)])
    assert check_source_stability(Frame([row(at=now)], Spark()), target_table_id="target")["reappeared_partitions"] == ["a"]


def test_append_allows_new_source_data(monkeypatch):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    previous = now - timedelta(hours=1)
    configure_stability(monkeypatch, [row("existing", at=previous)])
    result = check_source_stability(
        Frame(
            [
                row("existing", at=now, observation_id="current"),
                row("new", at=now, observation_id="current"),
            ],
            Spark(),
        ),
        target_table_id="target",
    )
    assert result["new_partitions"] == ["new"]
    assert result["historical_mutation"] is False
    assert result["status"] == "passed"
    assert result["can_continue"] is True


@pytest.mark.parametrize(
    ("severity", "status", "can_continue"),
    [("blocking", "failed", False), ("warning", "warning", True)],
)
def test_append_rejects_historical_mutation(monkeypatch, severity, status, can_continue):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    rules = [stability_rule(severity=severity)]
    configure_stability(monkeypatch, [row(at=now - timedelta(hours=1))], rules)
    result_writes = []
    monkeypatch.setattr(stability, "write_guardrail_result_row", lambda **kwargs: result_writes.append(kwargs))
    result = check_source_stability(Frame([row(at=now, count=2)], Spark()), target_table_id="target")
    assert result["status"] == status
    assert result["can_continue"] is can_continue
    assert result["severity"] == severity
    assert result["guardrail_version"] == 1
    assert result_writes[0]["guardrail_type"] == "source_stability"


def test_content_fingerprint_detects_mutation_when_counts_and_ranges_match(monkeypatch):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    configure_stability(
        monkeypatch,
        [row(at=now - timedelta(hours=1), fingerprint="before")],
    )
    result = check_source_stability(
        Frame([row(at=now, observation_id="current", fingerprint="after")], Spark()),
        target_table_id="target",
    )
    assert result["changed_partitions"] == ["a"]
    assert result["historical_mutation"] is True
    assert result["status"] == "failed"


def test_source_stability_rejects_cross_environment_observation(monkeypatch):
    monkeypatch.setattr(stability, "resolve_fabric_context", lambda: (object(), "dev", {}))
    with pytest.raises(ValueError, match="does not match active environment"):
        check_source_stability(Frame([row(environment_name="prod")], Spark()), target_table_id="target")


def test_freshness_rejects_non_observation_input():
    with pytest.raises(ValueError, match="canonical evidence"):
        check_freshness([{"max_change_value": "2026-08-14"}])


def test_freshness_rejects_incomplete_observation_identity():
    incomplete = row()
    del incomplete["source_table_id"]
    with pytest.raises(ValueError, match="canonical evidence"):
        check_freshness([incomplete])


def test_freshness_uses_stability_rule_only_to_resolve_observation_column(monkeypatch):
    observed = Frame([row(maximum="2999-08-14")], Spark())
    configure_freshness(monkeypatch)
    result = freshness.check_freshness(observed)
    assert result["status"] == "passed"
    assert result["guardrail_version"] == 1


def test_freshness_rejects_rule_column_that_differs_from_observation(monkeypatch):
    observed = Frame([row(maximum="2999-08-14")], Spark())
    configure_freshness(monkeypatch, [freshness_rule(freshness_column="loaded_at"), stability_rule()])
    with pytest.raises(ValueError, match="does not match change_column 'modified_at'"):
        freshness.check_freshness(observed)


@pytest.mark.parametrize("load_strategy", ["overwrite", "scd1", "scd2"])
def test_historical_mutation_is_compatible_with_reconciling_strategies(monkeypatch, load_strategy):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    rules = [stability_rule()]
    configure_stability(
        monkeypatch,
        [row(at=now - timedelta(hours=1))],
        rules,
        load_strategy=load_strategy,
    )

    result = check_source_stability(Frame([row(at=now, count=2)], Spark()), target_table_id="target")

    assert result["status"] == "passed"
    assert result["historical_mutation"] is True
    assert result["load_strategy"] == load_strategy
    assert "source_pattern" not in result
    assert "change_behaviour" not in json.loads(rules[0]["rule_parameters_json"])
    assert "expected_change" not in json.loads(rules[0]["rule_parameters_json"])


def test_source_stability_requires_active_rule(monkeypatch):
    now = datetime(2026, 8, 14, tzinfo=UTC)
    configure_stability(monkeypatch, [row(at=now - timedelta(hours=1))], rules=[])
    monkeypatch.setattr(stability, "load_table_guardrail_rules", lambda *args, **kwargs: [])
    with pytest.raises(ValueError, match="No active approved Source Stability rule exists for 'key'"):
        check_source_stability(Frame([row(at=now)], Spark()), target_table_id="target")


def test_governed_guardrail_public_signatures_are_minimal():
    import inspect
    from fabricops_kit import check_schema

    assert str(inspect.signature(check_schema)) == "(table_id: str, *, dataframe=None, enabled: bool = True, raise_on_failure: bool = False) -> dict"
    assert str(inspect.signature(check_freshness)) == "(observation, *, table_id: str | None = None, enabled: bool = True, raise_on_failure: bool = False) -> dict"


def test_guardrail_checks_can_skip_before_contract_metadata_exists():
    from fabricops_kit import check_schema

    assert check_schema("orders", enabled=False)["can_continue"] is True
    assert check_freshness(None, enabled=False)["can_continue"] is True


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
    monkeypatch.setattr(schema_module, "resolve_pipeline_data_contract", lambda *args, **kwargs: {"contract_id": "contract"})
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
    monkeypatch.setattr(schema_module, "resolve_pipeline_data_contract", lambda *args, **kwargs: {"contract_id": "contract"})
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


def test_schema_can_raise_on_blocking_result(monkeypatch):
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
    monkeypatch.setattr(schema_module, "resolve_pipeline_data_contract", lambda *args, **kwargs: {"contract_id": "contract"})
    monkeypatch.setattr(schema_module, "resolve_lakehouse_table_location", lambda *args: ("orders", "dbo", "path"))
    monkeypatch.setattr(schema_module, "resolve_catalogue_table_identity", lambda *args, **kwargs: {
        "table_id": "catalogue-orders", "store_type": "lakehouse", "target": "product", "schema": "dbo", "table_name": "orders",
    })
    monkeypatch.setattr(schema_module, "load_table_guardrail_rules", lambda *args, **kwargs: [result])
    monkeypatch.setattr(schema_module, "select_table_guardrail_rule", lambda *args, **kwargs: result)
    monkeypatch.setattr(schema_module, "schema_check_core", lambda *args, **kwargs: result.copy())
    monkeypatch.setattr(schema_module, "write_guardrail_result_row", lambda **kwargs: events.append("recorded"))
    returned = schema_module.check_schema("catalogue-orders", dataframe=object())
    assert returned["can_continue"] is False
    assert events == ["recorded"]

    with pytest.raises(RuntimeError, match="blocking schema Guardrail"):
        schema_module.check_schema("catalogue-orders", dataframe=object(), raise_on_failure=True)
