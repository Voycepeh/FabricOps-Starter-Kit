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
        processing={"load_strategy": "overwrite"}, scope={"read_mode": "full_dataset", "scope": {"type": "full_dataset"}},
    )
    assert calls[0][1]["mode"] == "overwrite"
    assert "options" not in calls[0][1]


def test_incremental_overwrite_uses_replace_where(monkeypatch):
    calls = _capture_writes(monkeypatch)
    shared.execute_lakehouse_processing(
        type("Frame", (), {"columns": ["_partition_bucket"]})(), table_name="students", target="unified", schema="dbo",
        processing={"load_strategy": "overwrite", "partition_column": "business_date"},
        scope={"read_mode": "incremental_subset", "scope": {
            "type": "partition", "column": "business_date", "values": ["2026-08-21"],
        }},
    )
    assert calls[0][1]["mode"] == "overwrite"
    assert calls[0][1]["options"] == {"replaceWhere": "`_partition_bucket` IN ('2026-08-21')"}


def test_incremental_overwrite_rejects_unsafe_partition_configuration(monkeypatch):
    calls = _capture_writes(monkeypatch)
    with pytest.raises(ValueError, match="persisted _partition_bucket target state"):
        shared.execute_lakehouse_processing(
            object(), table_name="students", target="unified", schema="dbo",
            processing={"load_strategy": "overwrite", "partition_column": "other_date"},
            scope={"read_mode": "incremental_subset", "scope": {
                "type": "partition", "column": "business_date", "values": ["2026-08-21"],
            }},
        )
    assert calls == []


def test_append_uses_low_level_append_only_after_scope_resolution(monkeypatch):
    calls = _capture_writes(monkeypatch)
    shared.execute_lakehouse_processing(
        object(), table_name="students", target="unified", schema="dbo",
        processing={"load_strategy": "append"},
        scope={"read_mode": "incremental_subset", "scope": {"type": "partition", "column": "business_date", "values": ["2026-08-21"]}},
    )
    assert calls[0][1]["mode"] == "append"


def test_incremental_execution_never_accepts_an_empty_scope(monkeypatch):
    calls = _capture_writes(monkeypatch)
    with pytest.raises(ValueError, match="at least one affected"):
        shared.execute_lakehouse_processing(
            object(), table_name="students", target="unified", schema="dbo",
            processing={"load_strategy": "append"},
            scope={"read_mode": "incremental_subset", "scope": {"type": "partition", "column": "business_date", "values": []}},
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
        scope={"read_mode": "full_dataset", "scope": {"type": "full_dataset"}},
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
        scope={"read_mode": "full_dataset", "scope": {"type": "full_dataset"}}, context={},
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
            scope={"read_mode": "full_dataset", "scope": {"type": "full_dataset"}}, context={},
        )


def test_scd1_merge_is_business_change_aware_and_ignores_audit_columns(monkeypatch, spark_session):
    recorded = {}

    class Merge:
        def whenMatchedUpdateAll(self, *, condition):
            recorded["change"] = condition
            return self

        def whenMatchedUpdate(self, *, set):
            recorded["technical_update"] = set
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
        [(1, "active", 200, "old-audit")],
        ["student_id", "status", "_watermark_value", "_committed_by"],
    )
    shared.execute_lakehouse_processing(
        incoming, table_name="students", target="unified", schema="dbo",
        processing={"load_strategy": "scd1", "key_columns": ["student_id"]},
        scope={"read_mode": "full_dataset", "scope": {"type": "full_dataset"}}, context={},
    )
    assert recorded == {
        "keys": "target.`student_id` <=> source.`student_id`",
        "change": "NOT (target.`status` <=> source.`status`)",
        "technical_update": {
            "_watermark_value": "source.`_watermark_value`",
            "_committed_at": "source.`_committed_at`",
            "_committed_by": "source.`_committed_by`",
            "_activity_id": "source.`_activity_id`",
            "_workspace_id": "source.`_workspace_id`",
            "_notebook_id": "source.`_notebook_id`",
            "_notebook_name": "source.`_notebook_name`",
        },
        "insert": True,
        "executed": True,
    }


def test_scd2_explicit_tracking_rejects_technical_columns():
    with pytest.raises(ValueError, match="only business columns"):
        shared.resolve_scd2_tracked_columns(
            ["student_id", "status", "effective_at", "_committed_at"],
            {"key_columns": ["student_id"], "effective_column": "effective_at", "tracked_columns": ["_committed_at"]},
        )


def test_scd2_identical_business_state_updates_watermark_without_new_version(monkeypatch, spark_session):
    """An unchanged current row takes only the technical SCD2 merge branch."""
    from pyspark.sql import functions as F

    recorded = {"appends": 0}
    current = spark_session.createDataFrame(
        [(1, "active", "2026-08-22", 100, True)],
        ["student_id", "status", "effective_at", "_watermark_value", "_is_current"],
    )

    class Merge:
        def whenMatchedUpdate(self, *, condition, set):
            recorded.setdefault("updates", []).append((condition, set))
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
            recorded["merge_condition"] = condition
            return Merge()

        def toDF(self):
            return current

    _install_delta(monkeypatch, ExistingDelta)
    monkeypatch.setattr(
        shared,
        "write_lakehouse_table_core",
        lambda *_args, **_kwargs: recorded.__setitem__("appends", recorded["appends"] + 1),
    )
    incoming = (
        spark_session.createDataFrame(
            [(1, "active", "2026-08-22", 200)],
            ["student_id", "status", "effective_at", "_watermark_value"],
        )
        .withColumn("_effective_from", F.col("effective_at"))
        .withColumn("_effective_to", F.lit(None).cast("string"))
        .withColumn("_is_current", F.lit(True))
    )

    shared.execute_lakehouse_processing(
        incoming,
        table_name="students",
        target="unified",
        schema="dbo",
        processing={"load_strategy": "scd2", "key_columns": ["student_id"], "effective_column": "effective_at"},
        scope={"read_mode": "incremental_subset", "scope": {
            "type": "watermark", "column": "effective_at", "lower_bound": 100, "upper_bound": 200,
        }},
        context={},
    )

    expire, technical = recorded["updates"]
    assert expire[0] == "NOT (target.`status` <=> source.`status`)"
    assert technical[0] == "NOT (NOT (target.`status` <=> source.`status`))"
    assert technical[1]["_watermark_value"] == "source.`_watermark_value`"
    assert recorded["appends"] == 0


def test_scd2_business_change_replay_creates_exactly_one_new_version(monkeypatch, spark_session):
    """Replaying an already-applied business state does not append another version."""
    from pyspark.sql import functions as F

    history = [{
        "student_id": 1,
        "status": "old",
        "effective_at": "2026-08-21",
        "_watermark_value": 100,
        "_effective_from": "2026-08-21",
        "_effective_to": "9999-12-31",
        "_is_current": True,
    }]
    source_rows = []

    class Merge:
        def whenMatchedUpdate(self, *, condition, set):
            return self

        def execute(self):
            source = source_rows[-1]
            current = next(row for row in history if row["student_id"] == source["student_id"] and row["_is_current"])
            if current["status"] != source["status"]:
                current["_is_current"] = False
                current["_effective_to"] = source["effective_at"]
            else:
                current["_watermark_value"] = source["_watermark_value"]

    class StatefulDelta:
        @staticmethod
        def isDeltaTable(_spark, _path):
            return True

        @staticmethod
        def forPath(_spark, _path):
            return StatefulDelta()

        def alias(self, _name):
            return self

        def merge(self, source, _condition):
            source_rows.append(source.collect()[0].asDict())
            return Merge()

        def toDF(self):
            return spark_session.createDataFrame(history)

    def append_version(frame, *_args, **_kwargs):
        history.extend(row.asDict() for row in frame.collect())

    _install_delta(monkeypatch, StatefulDelta)
    monkeypatch.setattr(shared, "write_lakehouse_table_core", append_version)
    incoming = (
        spark_session.createDataFrame(
            [(1, "new", "2026-08-22", 200)],
            ["student_id", "status", "effective_at", "_watermark_value"],
        )
        .withColumn("_effective_from", F.col("effective_at"))
        .withColumn("_effective_to", F.lit(None).cast("string"))
        .withColumn("_is_current", F.lit(True))
    )
    kwargs = {
        "table_name": "students",
        "target": "unified",
        "schema": "dbo",
        "processing": {"load_strategy": "scd2", "key_columns": ["student_id"], "effective_column": "effective_at"},
        "scope": {"read_mode": "incremental_subset", "scope": {
            "type": "watermark", "column": "effective_at", "lower_bound": 100, "upper_bound": 200,
        }},
        "context": {},
    }

    shared.execute_lakehouse_processing(incoming, **kwargs)
    shared.execute_lakehouse_processing(incoming, **kwargs)

    assert len(history) == 2
    assert sum(bool(row["_is_current"]) for row in history) == 1
    assert [row["status"] for row in history if row["_is_current"]] == ["new"]
