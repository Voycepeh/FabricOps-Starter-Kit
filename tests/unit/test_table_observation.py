"""Focused tests for lightweight table observation."""
# ruff: noqa: D101, D102, D103, D107
from __future__ import annotations

import importlib
import inspect
import sys
import types

import pytest

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


def run(monkeypatch, current, previous=(), *, kind="warehouse", **arguments):
    queries, persisted = [], []
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {"config": object(), "env": "dev"}))
    monkeypatch.setattr(module, "get_store", lambda *args: types.SimpleNamespace(kind=kind))
    monkeypatch.setattr(module, "get_spark_session", lambda: object())
    monkeypatch.setattr(module, "configured_lakehouse_schema", lambda *args: None)
    monkeypatch.setattr(module, "_load_previous", lambda *args, **kwargs: list(previous))
    monkeypatch.setattr(module, "_persist", lambda rows, **kwargs: persisted.extend(rows))
    monkeypatch.setattr(module, "read_warehouse_query_core", lambda query, **kwargs: queries.append((query, kwargs)) or Frame(current))
    call = dict(table_name="orders", target="source", schema="dbo",
                partition_column="business_date", change_column="modified_at")
    call.update(arguments)
    result = module.observe_table(**call)
    return result, queries, persisted


def test_first_observation_requires_read(monkeypatch):
    result, _, _ = run(monkeypatch, [evidence()])
    assert result["first_observation"] and result["requires_read"]
    assert result["new_partitions"] == ["2026-08-10"]


def test_unchanged_evidence_requires_no_read(monkeypatch):
    previous = [{**evidence(), "is_present": True}]
    result, _, _ = run(monkeypatch, [evidence()], previous)
    assert result["changed_partitions"] == [] and not result["requires_read"]


@pytest.mark.parametrize("current", [
    evidence(count=11),
    evidence(minimum="2026-08-10T07:30:00"),
    evidence(maximum="2026-08-11T00:00:00"),
])
def test_changed_evidence_marks_partition(monkeypatch, current):
    result, _, _ = run(monkeypatch, [current], [{**evidence(), "is_present": True}])
    assert result["changed_partitions"] == ["2026-08-10"]


def test_new_and_removed_partitions(monkeypatch):
    previous = [{**evidence("old"), "is_present": True}]
    result, _, persisted = run(monkeypatch, [evidence("new")], previous)
    assert result["new_partitions"] == ["new"]
    assert result["removed_partitions"] == ["old"]
    assert persisted[-1] == {
        "partition_value": "old",
        "is_present": False,
        "row_count": 0,
        "min_change_value": None,
        "max_change_value": None,
    }


def test_removed_partition_reappearance_is_changed(monkeypatch):
    previous = [{**evidence(), "is_present": False}]
    result, _, _ = run(monkeypatch, [evidence()], previous)
    assert result["changed_partitions"] == ["2026-08-10"]


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


@pytest.mark.parametrize("kwargs", [
    {"table_name": ""}, {"table_name": "bad.name"}, {"partition_column": "bad-name"}, {"change_column": ""},
])
def test_invalid_identity_and_columns(monkeypatch, kwargs):
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (_ for _ in ()).throw(AssertionError()))
    values = dict(table_name="orders", partition_column="day", change_column="modified_at") | kwargs
    with pytest.raises(ValueError): module.observe_table(**values)


def test_warehouse_requires_schema(monkeypatch):
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(module, "get_store", lambda *args: types.SimpleNamespace(kind="warehouse"))
    with pytest.raises(ValueError, match="schema is required"):
        module.observe_table(table_name="orders", partition_column="day", change_column="modified_at")


def test_definition_identity_is_deterministic_and_meaningful(monkeypatch):
    first, _, _ = run(monkeypatch, [evidence()])
    second, _, _ = run(monkeypatch, [evidence()])
    changed, _, _ = run(monkeypatch, [evidence()], change_column="updated_at")
    assert first["observation_definition_id"] == second["observation_definition_id"]
    assert first["observation_definition_id"] != changed["observation_definition_id"]


def test_public_signature_has_no_legacy_or_runtime_plumbing():
    assert str(inspect.signature(module.observe_table)) == "(table_name: 'str', *, target: 'str' = 'source', schema: 'str | None' = None, partition_column: 'str', change_column: 'str') -> 'dict[str, Any]'"


def test_observe_source_is_not_exported():
    import fabricops_kit
    assert not hasattr(fabricops_kit, "observe_source")
    assert "observe_source" not in fabricops_kit.pipeline.__all__


def test_logical_source_target_routes_to_configured_warehouse(monkeypatch):
    result, queries, _ = run(monkeypatch, [evidence()], kind="warehouse")
    assert result["source_id"] == "warehouse:source:dbo:orders"
    assert queries[0][1]["target"] == "source"


def test_logical_source_target_routes_to_configured_lakehouse(monkeypatch):
    captured = []
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {"config": object(), "env": "dev"}))
    monkeypatch.setattr(module, "get_store", lambda *args: types.SimpleNamespace(kind="lakehouse"))
    monkeypatch.setattr(module, "get_spark_session", lambda: object())
    monkeypatch.setattr(module, "configured_lakehouse_schema", lambda *args: None)
    monkeypatch.setattr(module, "_load_previous", lambda *args, **kwargs: [])
    monkeypatch.setattr(module, "_persist", lambda rows, **kwargs: None)
    monkeypatch.setattr(module, "_observe_lakehouse", lambda *args, **kwargs: captured.append(args) or [{**evidence(), "is_present": True}])
    result = module.observe_table(table_name="orders", target="source", schema="dbo", partition_column="business_date", change_column="modified_at")
    assert captured[0][:3] == ("orders", "source", "dbo")
    assert result["source_id"] == "lakehouse:source:dbo:orders"


def test_table_observation_path_contains_no_checksum_or_fingerprint_model():
    source = inspect.getsource(module)
    assert not {"CHECKSUM_AGG", "BINARY_CHECKSUM", "xxhash64", "fingerprint_columns", "range_column"} & set(source.replace("(", " ").split())
    assert "CHECKSUM_AGG" not in source and "BINARY_CHECKSUM" not in source and "xxhash64" not in source
