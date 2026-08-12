"""Tests for source-side observation and incremental read planning."""

from __future__ import annotations

from datetime import UTC, datetime
import importlib
import sys
import types
from unittest.mock import ANY

import pytest

module = importlib.import_module("fabricops_kit.pipeline.observe_source")


class _Row(dict):
    def asDict(self, recursive=True):  # noqa: N802, ARG002
        return dict(self)


class _CompactFrame:
    def __init__(self, rows):
        self.rows = [_Row(row) for row in rows]

    def collect(self):
        return self.rows


def _source(source_type="warehouse"):
    return {
        "source_type": source_type,
        "target": "warehouse" if source_type == "warehouse" else "source",
        "schema": "dbo",
        "table_name": "orders",
    }


def _run(monkeypatch, current, previous=(), **kwargs):
    persisted = []
    queries = []
    monkeypatch.setattr(module, "get_spark_session", lambda spark: object())
    monkeypatch.setattr(module, "configured_lakehouse_schema", lambda *args: "metadata")
    monkeypatch.setattr(module, "_load_previous", lambda *args, **kwargs: list(previous))
    monkeypatch.setattr(module, "_persist", lambda rows, *args, **kwargs: persisted.extend(rows))
    monkeypatch.setattr(
        module,
        "read_warehouse_query_core",
        lambda query, **options: queries.append(query) or _CompactFrame(current),
    )
    result = module.observe_source(
        _source(), partition_columns=["business_date"], range_column="id",
        fingerprint_columns=["id", "modified_at"], config=object(), env="dev",
        spark_session=object(), **kwargs,
    )
    return result, persisted, queries


def _observation(partition="2026-08-10", checksum=1):
    return {
        "business_date": partition, "row_count": 10, "observed_min": 1,
        "observed_max": 10, "aggregate_checksum": checksum,
    }


def test_first_observation_marks_partitions_new_and_persists(monkeypatch):
    """A missing history marks compact partitions as new and persists them."""
    result, persisted, _queries = _run(monkeypatch, [_observation()])
    assert result["first_observation"] is True
    assert result["new_partitions"] == ["2026-08-10"]
    assert result["requires_read"] is True
    assert persisted == result["observations"]


def test_identical_observation_avoids_read(monkeypatch):
    """A matching latest fingerprint avoids a business-data read."""
    first, _, _ = _run(monkeypatch, [_observation()], persist=False)
    result, _, _ = _run(monkeypatch, [_observation()], previous=first["observations"])
    assert result["requires_read"] is False
    assert result["read_predicate"] is None


def test_changed_and_new_partitions_produce_restricted_plan(monkeypatch):
    """Only changed and unseen partitions appear in the read predicate."""
    old, _, _ = _run(monkeypatch, [_observation(), _observation("2026-08-09")], persist=False)
    current = [_observation(checksum=2), _observation("2026-08-09"), _observation("2026-08-11")]
    result, _, _ = _run(monkeypatch, current, previous=old["observations"])
    assert result["changed_partitions"] == ["2026-08-10"]
    assert result["new_partitions"] == ["2026-08-11"]
    assert "2026-08-09" not in result["read_predicate"]
    assert result["read_predicate"] == "[business_date] IN ('2026-08-10', '2026-08-11')"


def test_warehouse_observation_is_read_only_grouped_pushdown(monkeypatch):
    """Warehouse SQL is a compact, read-only grouped aggregate."""
    result, _, queries = _run(monkeypatch, [_observation()])
    sql = queries[0].upper()
    assert "GROUP BY" in sql and "COUNT_BIG(*)" in sql and "CHECKSUM_AGG" in sql
    assert "SELECT *" not in sql
    assert not any(keyword in sql for keyword in ("INSERT ", "UPDATE ", "DELETE ", "MERGE ", "CREATE ", "ALTER "))
    assert len(result["observations"]) == 1


def test_previous_observation_loads_latest_fabricops_history(monkeypatch):
    """History loading retains the latest FabricOps row per partition."""
    older = _Row(partition_value="p", fingerprint="old", observed_at=datetime(2026, 1, 1, tzinfo=UTC))
    newer = _Row(partition_value="p", fingerprint="new", observed_at=datetime(2026, 1, 2, tzinfo=UTC))

    class _Column:
        def __eq__(self, other):
            return ("eq", other)

        def desc(self):
            return self

    class _History(_CompactFrame):
        source_id = observed_at = _Column()

        def where(self, condition):
            assert condition == ("eq", "warehouse:warehouse:dbo:orders")
            return self

        def orderBy(self, column):  # noqa: N802, ARG002
            return self

        def select(self, *columns):  # noqa: ARG002
            return self

    monkeypatch.setattr(module, "read_lakehouse_table_core", lambda *args, **kwargs: _History([newer, older]))
    rows = module._load_previous(
        "warehouse:warehouse:dbo:orders", spark_session=object(), config=object(),
        env="dev", metadata_schema="metadata",
    )
    assert rows == [newer]


def test_observation_persistence_targets_fabricops_metadata(monkeypatch):
    """Observation rows append only to the configured FabricOps metadata table."""
    writes = []

    class _Spark:
        def createDataFrame(self, rows, schema=None):  # noqa: N802
            assert schema is not None
            return (rows, schema)

    audit = {
        "_committed_by": "tester", "_committed_at": datetime(2026, 1, 1, tzinfo=UTC),
        "_workspace_id": "workspace", "_workspace_name": "Workspace",
        "_notebook_id": "notebook", "_notebook_name": "Notebook",
        "_metadata_lakehouse_name": "Metadata", "_activity_id": "activity",
    }
    monkeypatch.setattr(module, "build_runtime_audit_fields", lambda **kwargs: audit)
    monkeypatch.setattr(
        module, "write_lakehouse_table_core",
        lambda frame, table, **options: writes.append((table, options)),
    )
    module._persist(
        [{"partition_value": "2026-08-10", "row_count": 1, "observed_min": "1", "observed_max": "1", "fingerprint": "hash"}],
        _source(), "warehouse:warehouse:dbo:orders", datetime(2026, 1, 1, tzinfo=UTC),
        spark_session=_Spark(), config=object(), env="dev", metadata_schema="meta",
    )
    assert writes == [(module.OBSERVATION_TABLE, {
        "target": "metadata", "schema": "meta",
        "context": {"config": ANY, "env": "dev"}, "mode": "append",
    })]


@pytest.mark.parametrize("source", [
    {},
    {"source_type": "file"},
    {"source_type": "warehouse", "target": "warehouse", "table_name": "bad.name"},
    {**_source(), "partition_predicate": "1 = 1; DELETE FROM dbo.orders"},
])
def test_invalid_source_configuration_fails_clearly(monkeypatch, source):
    """Missing, unsupported, and unsafe source configurations fail clearly."""
    monkeypatch.setattr(module, "get_spark_session", lambda spark: object())
    with pytest.raises(ValueError):
        module.observe_source(
            source, partition_columns=["day"], range_column="id",
            fingerprint_columns=["id"], config=object(), env="dev", spark_session=object(),
        )


def test_lakehouse_observation_projects_filters_and_aggregates(monkeypatch):
    """Lakehouse work projects, prunes, and aggregates before collection."""
    calls = []

    class _Frame:
        def select(self, *columns):
            calls.append(("select", columns)); return self

        def where(self, predicate):
            calls.append(("where", predicate)); return self

        def groupBy(self, *columns):  # noqa: N802
            calls.append(("groupBy", columns)); return self

        def agg(self, *expressions):
            calls.append(("agg", len(expressions))); return _CompactFrame([{
                "day": "2026-08-10", "row_count": 1, "observed_min": 1,
                "observed_max": 1, "fingerprint_input": 5,
            }])

    class _Expression:
        def cast(self, value): return self
        def alias(self, value): return self

    class _Functions:
        col = lit = staticmethod(lambda *args: _Expression())
        coalesce = xxhash64 = count = min = max = sum = staticmethod(lambda *args: _Expression())

    pyspark = types.ModuleType("pyspark")
    sql = types.ModuleType("pyspark.sql")
    sql.functions = _Functions
    pyspark.sql = sql
    monkeypatch.setitem(sys.modules, "pyspark", pyspark)
    monkeypatch.setitem(sys.modules, "pyspark.sql", sql)
    monkeypatch.setitem(sys.modules, "pyspark.sql.functions", _Functions)
    monkeypatch.setattr(module, "read_lakehouse_table_core", lambda *args, **kwargs: _Frame())
    result = module._observe_lakehouse(
        {**_source("lakehouse"), "partition_predicate": "day >= '2026-08-10'"},
        ["day"], "id", ["id", "modified_at"], spark_session=object(), context={},
    )
    assert calls[:3] == [
        ("select", ("day", "id", "modified_at")),
        ("where", "day >= '2026-08-10'"),
        ("groupBy", ("day",)),
    ]
    assert calls[3] == ("agg", 4)
    assert len(result) == 1
