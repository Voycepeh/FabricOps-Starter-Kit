"""Focused tests for lightweight table observation."""
# ruff: noqa: D101, D102, D103, D107
from __future__ import annotations

import importlib
import inspect
import sys
import types

import pytest

from fabricops_kit.config.shared import build_table_id

module = importlib.import_module("fabricops_kit.pipeline.observe_table")


class Row(dict):
    def asDict(self, recursive=True):  # noqa: N802, ARG002
        return dict(self)


class Frame:
    def __init__(self, rows): self.rows = [Row(row) for row in rows]
    def collect(self): return self.rows


def evidence(
    partition="2026-08-10",
    count=10,
    minimum="2026-08-10T08:00:00",
    maximum="2026-08-10T12:00:00",
):
    return {
        "partition_value": partition,
        "row_count": count,
        "min_change_value": minimum,
        "max_change_value": maximum,
    }


def run(monkeypatch, current, *, kind="warehouse", persist_spy=None, **arguments):
    queries, persisted = [], []
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {"config": object(), "env": "dev"}))
    monkeypatch.setattr(module, "get_store", lambda *args: types.SimpleNamespace(kind=kind, schema=None, schema_enabled=False))
    monkeypatch.setattr(module, "resolve_warehouse_table_location", lambda store, schema, table: (schema, table, f"Store.{schema}.{table}"))
    monkeypatch.setattr(module, "resolve_lakehouse_table_location", lambda store, table, schema: (table, schema, f"/Tables/{table}"))
    monkeypatch.setattr(module, "get_spark_session", lambda: object())
    monkeypatch.setattr(module, "configured_lakehouse_schema", lambda *args: None)
    monkeypatch.setattr(module, "load_table_guardrail_rules", lambda *args, **kwargs: [object()])
    monkeypatch.setattr(module, "select_table_guardrail_rule", lambda *args, **kwargs: {"rule_parameters_json": '{"partition_column":"business_date","change_column":"modified_at"}'})
    monkeypatch.setattr(
        module, "_persist",
        lambda rows, **kwargs: (persisted.extend(rows), persist_spy and persist_spy(rows, kwargs), Frame(rows))[2],
    )
    monkeypatch.setattr(module, "read_warehouse_query_core", lambda query, **kwargs: queries.append((query, kwargs)) or Frame(current))
    call = dict(table_name="orders", target="source", schema="dbo")
    call.update(arguments)
    result = module.observe_table(**call)
    return result, queries, persisted


def test_observe_table_returns_persisted_evidence_without_judgement(monkeypatch):
    result, _, persisted = run(monkeypatch, [evidence()])
    assert isinstance(result, Frame)
    assert result.collect() == persisted
    source = inspect.getsource(module.observe_table)
    for decision in ("new_partitions", "changed_partitions", "removed_partitions", "requires_read", "read_predicate"):
        assert decision not in source
    assert "_load_previous" not in inspect.getsource(module)


def test_warehouse_aggregation_is_pushed_down(monkeypatch):
    _, queries, _ = run(monkeypatch, [evidence()])
    sql = queries[0][0]
    assert "COUNT_BIG(*)" in sql
    assert "MIN([modified_at])" in sql
    assert "MAX([modified_at])" in sql
    assert "GROUP BY [business_date]" in sql
    assert "SELECT *" not in sql


def test_lakehouse_projects_only_observation_columns(monkeypatch):
    calls = []

    class SparkFrame:
        def select(self, *columns): calls.append(("select", columns)); return self
        def groupBy(self, *columns): calls.append(("groupBy", columns)); return self  # noqa: N802
        def agg(self, *expressions): calls.append(("agg", len(expressions))); return self
        def collect(self): return [Row(evidence())]

    class Expr:
        def alias(self, name): return self

    class Functions:
        col = lit = count = min = max = staticmethod(lambda *args: Expr())

    pyspark = types.ModuleType("pyspark"); sql = types.ModuleType("pyspark.sql")
    sql.functions = Functions; pyspark.sql = sql
    monkeypatch.setitem(sys.modules, "pyspark", pyspark); monkeypatch.setitem(sys.modules, "pyspark.sql", sql)
    monkeypatch.setitem(sys.modules, "pyspark.sql.functions", Functions)
    monkeypatch.setattr(module, "read_lakehouse_table_core", lambda *args, **kwargs: SparkFrame())
    module._observe_lakehouse("orders", "source", None, "business_date", "modified_at", spark_session=object(), context={})
    assert calls[0] == ("select", ("business_date", "modified_at"))
    assert calls[1] == ("groupBy", ("business_date",))
    assert calls[2] == ("agg", 3)


@pytest.mark.parametrize("kwargs", [{"table_name": ""}, {"table_name": "bad.name"}])
def test_invalid_identity_and_columns(monkeypatch, kwargs):
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (_ for _ in ()).throw(AssertionError()))
    values = dict(table_name="orders") | kwargs
    with pytest.raises(ValueError):
        module.observe_table(**values)


def test_warehouse_requires_schema(monkeypatch):
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(module, "get_store", lambda *args: types.SimpleNamespace(kind="warehouse"))
    with pytest.raises(ValueError, match="schema is required"):
        module.observe_table(table_name="orders")


def test_invalid_active_change_rule_has_actionable_error(monkeypatch):
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(module, "get_store", lambda *args: types.SimpleNamespace(kind="warehouse", schema="dbo"))
    monkeypatch.setattr(module, "resolve_warehouse_table_location", lambda store, schema, table: (schema, table, "Store.dbo.orders"))
    monkeypatch.setattr(module, "get_spark_session", lambda: object())
    monkeypatch.setattr(module, "load_table_guardrail_rules", lambda *args, **kwargs: [object()])
    monkeypatch.setattr(module, "select_table_guardrail_rule", lambda *args, **kwargs: {"rule_parameters_json": "not-json"})
    with pytest.raises(ValueError, match="Active source-change rule is invalid: partition_column is missing"):
        module.observe_table(table_name="orders")


def test_table_id_is_deterministic_and_independent_of_observation_columns(monkeypatch):
    captured = []
    run(monkeypatch, [evidence()], persist_spy=lambda rows, kwargs: captured.append(kwargs))
    run(monkeypatch, [evidence()], persist_spy=lambda rows, kwargs: captured.append(kwargs))
    assert captured[0]["table_id"] == captured[1]["table_id"]
    assert captured[0]["observation_id"] != captured[1]["observation_id"]


def test_public_signature_has_no_legacy_or_runtime_plumbing():
    assert str(inspect.signature(module.observe_table)) == "(table_name: 'str', *, target: 'str' = 'source', schema: 'str | None' = None) -> 'Any'"


def test_observe_source_is_not_exported():
    import fabricops_kit
    assert not hasattr(fabricops_kit, "observe_source")
    assert "observe_source" not in fabricops_kit.pipeline.__all__


def test_logical_source_target_routes_to_configured_warehouse(monkeypatch):
    captured = []
    _, queries, _ = run(monkeypatch, [evidence()], kind="warehouse", persist_spy=lambda rows, kwargs: captured.append(kwargs))
    assert captured[0]["table_id"] == build_table_id("warehouse", "source", "dbo", "orders")
    assert queries[0][1]["target"] == "source"


def test_logical_source_target_routes_to_configured_lakehouse(monkeypatch):
    captured = []
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {"config": object(), "env": "dev"}))
    monkeypatch.setattr(module, "get_store", lambda *args: types.SimpleNamespace(kind="lakehouse", schema=None, schema_enabled=False))
    monkeypatch.setattr(module, "resolve_lakehouse_table_location", lambda store, table, schema: (table, schema, f"/Tables/{table}"))
    monkeypatch.setattr(module, "get_spark_session", lambda: object())
    monkeypatch.setattr(module, "configured_lakehouse_schema", lambda *args: None)
    monkeypatch.setattr(module, "load_table_guardrail_rules", lambda *args, **kwargs: [object()])
    monkeypatch.setattr(module, "select_table_guardrail_rule", lambda *args, **kwargs: {"rule_parameters_json": '{"partition_column":"business_date","change_column":"modified_at"}'})
    monkeypatch.setattr(module, "_observe_lakehouse", lambda *args, **kwargs: captured.append(args) or [{**evidence(), "is_present": True}])
    identities = []
    monkeypatch.setattr(module, "_persist", lambda rows, **kwargs: identities.append(kwargs) or Frame(rows))
    module.observe_table(table_name="orders", target="source", schema="dbo")
    assert captured[0][:3] == ("orders", "source", "dbo")
    assert identities[0]["table_id"] == build_table_id("lakehouse", "source", "dbo", "orders")


def test_table_observation_path_contains_no_checksum_or_fingerprint_model():
    source = inspect.getsource(module)
    assert not {"CHECKSUM_AGG", "BINARY_CHECKSUM", "xxhash64", "fingerprint_columns", "range_column"} & set(source.replace("(", " ").split())
    assert "CHECKSUM_AGG" not in source and "BINARY_CHECKSUM" not in source and "xxhash64" not in source
    assert "source_id" not in source and "observation_definition_id" not in source


def test_observation_id_matches_profile_registration_builder(monkeypatch):
    captured = []
    run(monkeypatch, [evidence()], kind="warehouse", persist_spy=lambda rows, kwargs: captured.append(kwargs))
    expected_table_id = build_table_id("warehouse", "source", "dbo", "orders")
    assert captured[0]["table_id"] == expected_table_id


def test_successful_observation_persists_canonical_identity_without_rule_definition(monkeypatch):
    persisted = []
    run(monkeypatch, [evidence()], kind="warehouse", persist_spy=lambda rows, kwargs: persisted.append((rows, kwargs)))
    rows, identity = persisted[0]
    assert rows == [{**evidence(), "is_present": True}]
    assert identity["table_id"] == build_table_id("warehouse", "source", "dbo", "orders")
    assert identity["observation_id"]
    assert "metadata_table_key" not in identity
    assert "partition_column" not in identity
    assert "change_column" not in identity
    assert "guardrail_rule_version_id" not in identity


def test_failed_observation_does_not_persist(monkeypatch):
    persisted = []
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(module, "get_store", lambda *args: types.SimpleNamespace(kind="warehouse", schema="dbo"))
    monkeypatch.setattr(module, "resolve_warehouse_table_location", lambda store, schema, table: (schema, table, "Store.dbo.orders"))
    monkeypatch.setattr(module, "get_spark_session", lambda: object())
    monkeypatch.setattr(module, "configured_lakehouse_schema", lambda *args: None)
    monkeypatch.setattr(module, "load_table_guardrail_rules", lambda *args, **kwargs: [object()])
    monkeypatch.setattr(module, "select_table_guardrail_rule", lambda *args, **kwargs: {"rule_parameters_json": '{"partition_column":"business_date","change_column":"modified_at"}'})
    monkeypatch.setattr(module, "read_warehouse_query_core", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("source failed")))
    monkeypatch.setattr(module, "_persist", lambda rows, **kwargs: persisted.extend(rows))
    with pytest.raises(RuntimeError, match="source failed"):
        module.observe_table(table_name="orders")
    assert persisted == []


def test_metadata_schema_matches_table_observation_contract():
    names = module.metadata_table_schema_registry()[module.OBSERVATION_TABLE].fieldNames()
    assert names[:9] == [
        "observation_id",
        "table_id",
        "environment_name",
        "partition_value",
        "row_count",
        "min_change_value",
        "max_change_value",
        "is_present",
        "observed_at",
    ]
    assert {"metadata_table_key", "partition_column", "change_column", "guardrail_rule_version_id"}.isdisjoint(names)
