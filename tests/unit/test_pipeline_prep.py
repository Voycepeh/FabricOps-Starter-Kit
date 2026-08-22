"""Tests for the public pipeline preparation boundary."""
# ruff: noqa: D103

from __future__ import annotations

from importlib import import_module
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.unit

read_module = import_module("fabricops_kit.pipeline.read_pipeline_prep")
write_module = import_module("fabricops_kit.pipeline.write_pipeline_prep")


def test_read_prep_observes_changes_and_resolves_processing_once(monkeypatch):
    observation = SimpleNamespace(sparkSession="spark")
    changes = {
        "changed": True, "first_observation": False, "new_partitions": ["2026-08-22"],
        "changed_partitions": [], "removed_partitions": [], "reappeared_partitions": [],
        "partition_column": "snapshot_date",
    }
    processing_calls = []
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: ("config", "dev", {"data_contract_overrides": {}}))
    monkeypatch.setattr(read_module, "get_store", lambda *_args: SimpleNamespace(kind="lakehouse"))
    monkeypatch.setattr(read_module, "resolve_lakehouse_table_location", lambda *_args: ("students", "dbo", "/target"))
    monkeypatch.setattr(read_module, "_observe_table_core", lambda *args, **kwargs: observation)
    monkeypatch.setattr(read_module, "_observation_changes", lambda value: changes if value is observation else pytest.fail())
    monkeypatch.setattr(
        read_module, "resolve_table_processing_definition",
        lambda *args, **kwargs: processing_calls.append((args, kwargs)) or {
            "load_strategy": "scd1", "key_columns": ["student_id"], "source": "current_authoring",
        },
    )
    result = read_module.read_pipeline_prep(
        "student_source", "students", source_schema="dbo", schema="dbo",
        load_strategy="scd1", load_strategy_parameters={"key_columns": ["student_id"]},
    )
    assert result["observation"] is observation
    assert result["changes"] is changes
    assert result["read_strategy"] == "incremental"
    assert result["partition_values"] == ["2026-08-22"]
    assert len(processing_calls) == 1
    assert processing_calls[0][1]["authored_processing"] == {
        "load_strategy": "scd1", "key_columns": ["student_id"],
    }


def test_read_prep_warehouse_overwrite_forces_full_scope(monkeypatch):
    observation = SimpleNamespace(sparkSession="spark")
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: ("config", "prod", {}))
    monkeypatch.setattr(read_module, "get_store", lambda *_args: SimpleNamespace(kind="warehouse", schema="dbo"))
    monkeypatch.setattr(read_module, "resolve_warehouse_table_location", lambda *_args: ("dbo", "students", "dbo.students"))
    monkeypatch.setattr(read_module, "_observe_table_core", lambda *args, **kwargs: observation)
    monkeypatch.setattr(read_module, "_observation_changes", lambda _value: {
        "changed": True, "first_observation": False, "new_partitions": ["2026-08-22"],
        "changed_partitions": [], "removed_partitions": [], "reappeared_partitions": [],
        "partition_column": "snapshot_date",
    })
    monkeypatch.setattr(read_module, "resolve_table_processing_definition", lambda *args, **kwargs: {
        "load_strategy": "overwrite", "source": "data_contract", "contract_id": "c", "contract_version": 1,
    })
    result = read_module.read_pipeline_prep(
        "student_source", "students", source_target="warehouse", source_schema="dbo",
        target="warehouse", schema="dbo", load_strategy="append",
    )
    assert result["read_strategy"] == "full"
    assert result["partition_column"] is None


@pytest.mark.parametrize(("strategy", "mode"), [("overwrite", "overwrite"), ("append", "append"), ("scd1", "append")])
def test_write_prep_adds_audit_and_reuses_exact_processing(monkeypatch, spark_session, strategy, mode):
    processing = {"load_strategy": strategy}
    if strategy == "scd1":
        processing["key_columns"] = ["student_id"]
    monkeypatch.setattr(write_module, "resolve_fabric_context", lambda: ("config", "dev", {}))
    monkeypatch.setattr(write_module, "get_store", lambda *_args: SimpleNamespace(kind="lakehouse"))
    monkeypatch.setattr(write_module, "resolve_target_audit_fields", lambda _context: {
        "_committed_at": "2026-08-22T00:00:00Z", "_committed_by": "engineer",
        "_activity_id": "activity", "_workspace_id": "workspace",
        "_notebook_id": "notebook", "_notebook_name": "02_pipeline",
    })
    frame = spark_session.createDataFrame([(1, "active")], ["student_id", "status"])
    read_prep = {"processing": processing, "read_strategy": "full", "partition_values": []}
    result = write_module.write_pipeline_prep(frame, read_prep)
    assert result["processing"] is processing
    assert result["mode"] == mode
    assert result["options"] == {}
    assert "_committed_at" in result["df"].columns


def test_write_prep_adds_scd2_lifecycle_and_rejects_warehouse_scd(monkeypatch, spark_session):
    processing = {"load_strategy": "scd2", "key_columns": ["student_id"], "effective_column": "effective_at"}
    monkeypatch.setattr(write_module, "resolve_fabric_context", lambda: ("config", "dev", {}))
    monkeypatch.setattr(write_module, "resolve_target_audit_fields", lambda _context: {
        "_committed_at": "2026-08-22T00:00:00Z", "_committed_by": "engineer",
        "_activity_id": "activity", "_workspace_id": "workspace",
        "_notebook_id": "notebook", "_notebook_name": "02_pipeline",
    })
    frame = spark_session.createDataFrame([(1, "active", "2026-08-22")], ["student_id", "status", "effective_at"])
    read_prep = {"processing": processing, "read_strategy": "full", "partition_values": []}
    monkeypatch.setattr(write_module, "get_store", lambda *_args: SimpleNamespace(kind="lakehouse"))
    result = write_module.write_pipeline_prep(frame, read_prep)
    assert {"_effective_from", "_effective_to", "_is_current"} <= set(result["df"].columns)
    monkeypatch.setattr(write_module, "get_store", lambda *_args: SimpleNamespace(kind="warehouse"))
    with pytest.raises(ValueError, match="Warehouse scd2"):
        write_module.write_pipeline_prep(frame, read_prep, target="warehouse")
