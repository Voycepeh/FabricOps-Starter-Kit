"""Tests for governed target load execution boundaries."""
# ruff: noqa: D103

from __future__ import annotations

import sys
from types import ModuleType

import pytest

from fabricops_kit.pipeline import shared

pytestmark = pytest.mark.unit


def _capture_writes(monkeypatch):
    calls = []
    monkeypatch.setattr(shared, "write_lakehouse_table_core", lambda *args, **kwargs: calls.append((args, kwargs)))
    monkeypatch.setattr(shared, "resolve_target_audit_fields", lambda _context: {})
    monkeypatch.setattr(shared, "add_target_audit_fields", lambda df, _audit: df)
    return calls


AUDIT = {
    "_committed_at": "2026-08-22T00:00:00+00:00",
    "_committed_by": "engineer@example.com",
    "_activity_id": "activity-1",
    "_workspace_id": "workspace-1",
    "_notebook_id": "notebook-1",
    "_notebook_name": "02_pipeline",
}


def test_full_overwrite_uses_full_table_overwrite(monkeypatch):
    calls = _capture_writes(monkeypatch)
    shared.execute_lakehouse_processing(
        object(), table_name="students", target="unified", schema="dbo",
        processing={"load_strategy": "overwrite"}, scope={"read_strategy": "full"},
    )
    assert calls[0][1]["mode"] == "overwrite"
    assert "options" not in calls[0][1]


def test_incremental_overwrite_uses_replace_where(monkeypatch):
    calls = _capture_writes(monkeypatch)
    shared.execute_lakehouse_processing(
        object(), table_name="students", target="unified", schema="dbo",
        processing={"load_strategy": "overwrite", "partition_column": "business_date"},
        scope={
            "read_strategy": "incremental", "partition_column": "business_date",
            "partition_values": ["2026-08-21"],
        },
    )
    assert calls[0][1]["mode"] == "overwrite"
    assert calls[0][1]["options"] == {"replaceWhere": "`business_date` IN ('2026-08-21')"}


def test_incremental_overwrite_rejects_unsafe_partition_configuration(monkeypatch):
    calls = _capture_writes(monkeypatch)
    with pytest.raises(ValueError, match="matching safe target partition"):
        shared.execute_lakehouse_processing(
            object(), table_name="students", target="unified", schema="dbo",
            processing={"load_strategy": "overwrite", "partition_column": "other_date"},
            scope={
                "read_strategy": "incremental", "partition_column": "business_date",
                "partition_values": ["2026-08-21"],
            },
        )
    assert calls == []


def test_append_uses_low_level_append_only_after_scope_resolution(monkeypatch):
    calls = _capture_writes(monkeypatch)
    shared.execute_lakehouse_processing(
        object(), table_name="students", target="unified", schema="dbo",
        processing={"load_strategy": "append"},
        scope={"read_strategy": "incremental", "partition_values": ["2026-08-21"]},
    )
    assert calls[0][1]["mode"] == "append"


def test_incremental_execution_never_accepts_an_empty_scope(monkeypatch):
    calls = _capture_writes(monkeypatch)
    with pytest.raises(ValueError, match="at least one affected"):
        shared.execute_lakehouse_processing(
            object(), table_name="students", target="unified", schema="dbo",
            processing={"load_strategy": "append"},
            scope={"read_strategy": "incremental", "partition_values": []},
        )
    assert calls == []


@pytest.mark.parametrize(("strategy", "mode"), [("overwrite", "overwrite"), ("append", "append")])
def test_normal_writes_add_one_consistent_compact_audit_record(monkeypatch, spark_session, strategy, mode):
    calls = []
    resolutions = []
    monkeypatch.setattr(shared, "write_lakehouse_table_core", lambda *args, **kwargs: calls.append((args, kwargs)))
    monkeypatch.setattr(
        shared, "resolve_target_audit_fields",
        lambda context: resolutions.append(context) or AUDIT,
    )
    incoming = spark_session.createDataFrame([(1, "active"), (2, "inactive")], ["student_id", "status"])
    shared.execute_lakehouse_processing(
        incoming, table_name="students", target="unified", schema="dbo",
        processing={"load_strategy": strategy},
        scope={"read_strategy": "full", "partition_values": []},
        context={"activity_id": "activity-1"},
    )
    rows = calls[0][0][0].collect()
    assert calls[0][1]["mode"] == mode
    assert resolutions == [{"activity_id": "activity-1"}]
    assert all({name: row[name] for name in AUDIT} == AUDIT for row in rows)


def test_target_audit_resolution_reuses_canonical_audit_builder(monkeypatch):
    calls = []
    monkeypatch.setattr(shared, "build_runtime_audit_fields", lambda **kwargs: calls.append(kwargs) or {
        **AUDIT, "_workspace_name": "Workspace", "_metadata_lakehouse_name": "Metadata",
    })
    context = {"config": "config", "env": "dev", "activity_id": "activity-1"}
    assert shared.resolve_target_audit_fields(context) == AUDIT
    assert calls == [{"config": "config", "env": "dev", "runtime_context": context}]


def _install_delta(monkeypatch, delta_table):
    package = ModuleType("delta")
    tables = ModuleType("delta.tables")
    tables.DeltaTable = delta_table
    package.tables = tables
    monkeypatch.setitem(sys.modules, "delta", package)
    monkeypatch.setitem(sys.modules, "delta.tables", tables)
    monkeypatch.setattr(shared, "resolve_configured_lakehouse_table", lambda *args, **kwargs: (None, None, None, "/target"))
    monkeypatch.setattr(shared, "resolve_target_audit_fields", lambda _context: AUDIT)


def test_scd2_first_load_adds_audit_and_standard_lifecycle_columns(monkeypatch, spark_session):
    from pyspark.sql import functions as F

    class MissingDelta:
        @staticmethod
        def isDeltaTable(_spark, _path):
            return False

    calls = []
    _install_delta(monkeypatch, MissingDelta)
    monkeypatch.setattr(shared, "write_lakehouse_table_core", lambda *args, **kwargs: calls.append((args, kwargs)))
    incoming = spark_session.createDataFrame(
        [(1, "active", "2026-08-22")], ["student_id", "status", "effective_at"]
    ).withColumn("_effective_from", F.col("effective_at")).withColumn(
        "_effective_to", F.lit(None).cast("string")
    ).withColumn("_is_current", F.lit(True))
    shared.execute_lakehouse_processing(
        incoming, table_name="students", target="unified", schema="dbo",
        processing={"load_strategy": "scd2", "key_columns": ["student_id"], "effective_column": "effective_at"},
        scope={"read_strategy": "full"}, context={},
    )
    row = calls[0][0][0].collect()[0].asDict()
    assert row["_effective_from"] == "2026-08-22"
    assert row["_effective_to"] is None
    assert row["_is_current"] is True
    assert {name: row[name] for name in AUDIT} == AUDIT


def test_scd_duplicate_incoming_business_keys_are_rejected(monkeypatch, spark_session):
    class MissingDelta:
        @staticmethod
        def isDeltaTable(_spark, _path):
            return False

    _install_delta(monkeypatch, MissingDelta)
    incoming = spark_session.createDataFrame([(1, "a"), (1, "b")], ["student_id", "status"])
    with pytest.raises(ValueError, match="duplicate business keys"):
        shared.execute_lakehouse_processing(
            incoming, table_name="students", target="unified", schema="dbo",
            processing={"load_strategy": "scd1", "key_columns": ["student_id"]},
            scope={"read_strategy": "full"}, context={},
        )


def test_scd1_merge_is_business_change_aware_and_ignores_audit_columns(monkeypatch, spark_session):
    recorded = {}

    class Merge:
        def whenMatchedUpdateAll(self, *, condition):
            recorded["change"] = condition
            return self

        def whenNotMatchedInsertAll(self):
            recorded["insert"] = True
            return self

        def execute(self):
            recorded["executed"] = True

    class ExistingDelta:
        @staticmethod
        def isDeltaTable(_spark, _path):
            return True

        @staticmethod
        def forPath(_spark, _path):
            return ExistingDelta()

        def alias(self, _name):
            return self

        def merge(self, _source, condition):
            recorded["keys"] = condition
            return Merge()

    _install_delta(monkeypatch, ExistingDelta)
    incoming = spark_session.createDataFrame(
        [(1, "active", "old-audit")], ["student_id", "status", "_committed_by"]
    )
    shared.execute_lakehouse_processing(
        incoming, table_name="students", target="unified", schema="dbo",
        processing={"load_strategy": "scd1", "key_columns": ["student_id"]},
        scope={"read_strategy": "full"}, context={},
    )
    assert recorded == {
        "keys": "target.`student_id` <=> source.`student_id`",
        "change": "NOT (target.`status` <=> source.`status`)",
        "insert": True,
        "executed": True,
    }


def test_scd2_explicit_tracking_rejects_technical_columns():
    with pytest.raises(ValueError, match="only business columns"):
        shared._resolve_scd2_tracked_columns(
            ["student_id", "status", "effective_at", "_committed_at"],
            {"key_columns": ["student_id"], "effective_column": "effective_at", "tracked_columns": ["_committed_at"]},
        )
