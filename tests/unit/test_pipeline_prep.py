"""Tests for the public pipeline preparation boundary."""
# ruff: noqa: D103

from __future__ import annotations

from importlib import import_module
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.unit

read_module = import_module("fabricops_kit.pipeline.read_pipeline_prep")
write_module = import_module("fabricops_kit.pipeline.write_pipeline_prep")
lakehouse_writer = import_module("fabricops_kit.io.write_lakehouse_table")


def _identity(*_args, target, schema, table_name):
    kind = "warehouse" if target == "warehouse" else "lakehouse"
    return {
        "table_id": f"{kind}:{target}:{schema}:{table_name}",
        "target": target,
        "schema": schema,
        "table_name": table_name,
        "store_kind": kind,
    }


def test_full_dataset_does_not_observe_or_read_checkpoint(monkeypatch):
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: ("config", "dev", {}))
    monkeypatch.setattr(read_module, "resolve_physical_table_identity", _identity)
    monkeypatch.setattr(read_module, "_observe_table_core", lambda *_args, **_kwargs: pytest.fail("observation"))
    monkeypatch.setattr(read_module, "_checkpoint_value", lambda *_args, **_kwargs: pytest.fail("checkpoint"))
    monkeypatch.setattr(read_module, "resolve_table_processing_definition", lambda *_args, **_kwargs: {"load_strategy": "overwrite", "source": "current_authoring"})
    result = read_module.read_pipeline_prep(
        "reference_codes", "reference_codes", source_read_strategy="full_dataset", load_strategy="overwrite",
    )
    assert result["source_processing"] == {"read_strategy": "full_dataset"}
    assert result["read_mode"] == "full_dataset"
    assert result["scope"] == {"type": "full_dataset"}


@pytest.mark.parametrize(("previous", "upper", "expected_mode"), [
    (None, "2026-08-26 12:00", "full_dataset"),
    ("2026-08-26 12:00", "2026-08-26 12:00", "skip"),
    ("2026-08-26 10:00", "2026-08-26 12:00", "incremental_subset"),
])
def test_watermark_scope_is_bounded_and_candidate_is_not_committed(monkeypatch, previous, upper, expected_mode):
    monkeypatch.setattr(read_module, "_checkpoint_value", lambda *_args, **_kwargs: previous)
    monkeypatch.setattr(read_module, "_source_upper_watermark", lambda *_args, **_kwargs: (upper, "string"))
    monkeypatch.setattr(read_module, "_coerce_checkpoint", lambda value, *_args, **_kwargs: value)
    result = read_module._watermark_scope(
        {"table_id": "warehouse:source:dbo:bookings"}, "modified_datetime",
        config="config", env="dev", spark_session="spark", context={},
    )
    assert result["read_mode"] == expected_mode
    assert result["candidate_checkpoint"]["status"] == "candidate"
    if expected_mode == "incremental_subset":
        assert result["scope"]["lower_inclusive"] is False
        assert result["scope"]["upper_inclusive"] is True
        assert result["scope"]["lower_bound"] == previous
        assert result["scope"]["upper_bound"] == upper


def test_read_prep_observes_changes_and_resolves_processing_once(monkeypatch):
    observation = SimpleNamespace(sparkSession="spark")
    changes = {
        "changed": True, "first_observation": False, "new_partitions": ["2026-08-22"],
        "changed_partitions": [], "removed_partitions": [], "reappeared_partitions": [],
        "partition_column": "snapshot_date",
    }
    processing_calls = []
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: ("config", "dev", {"data_contract_overrides": {}}))
    monkeypatch.setattr(read_module, "resolve_physical_table_identity", _identity)
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
        source_read_strategy="incremental_partition", source_partition_column="snapshot_date",
        load_strategy="scd1", load_strategy_parameters={"key_columns": ["student_id"]},
    )
    assert result["observation"] is observation
    assert result["changes"] is changes
    assert result["read_mode"] == "incremental_subset"
    assert result["scope"]["values"] == ["2026-08-22"]
    assert result["source"]["table_name"] == "student_source"
    assert result["target"]["table_name"] == "students"
    assert len(processing_calls) == 1
    assert processing_calls[0][1]["authored_processing"] == {
        "load_strategy": "scd1", "key_columns": ["student_id"],
    }


def test_read_prep_warehouse_overwrite_forces_full_scope(monkeypatch):
    observation = SimpleNamespace(sparkSession="spark")
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: ("config", "prod", {}))
    monkeypatch.setattr(read_module, "resolve_physical_table_identity", _identity)
    monkeypatch.setattr(read_module, "_observe_table_core", lambda *args, **kwargs: observation)
    monkeypatch.setattr(read_module, "_observation_changes", lambda _value: {
        "changed": True, "first_observation": False, "new_partitions": ["2026-08-22"],
        "changed_partitions": [], "removed_partitions": [], "reappeared_partitions": [],
        "partition_column": "snapshot_date",
    })
    monkeypatch.setattr(read_module, "resolve_table_processing_definition", lambda *args, **kwargs: {
        "load_strategy": "overwrite", "partition_column": "snapshot_date",
        "source": "data_contract", "contract_id": "c", "contract_version": 1,
    })
    result = read_module.read_pipeline_prep(
        "student_source", "students", source_target="warehouse", source_schema="dbo",
        target="warehouse", schema="dbo", source_read_strategy="incremental_partition",
        source_partition_column="snapshot_date", load_strategy="append",
    )
    assert result["read_mode"] == "full_dataset"
    assert result["scope"] == {"type": "full_dataset"}


@pytest.mark.parametrize(("strategy", "mode"), [("overwrite", "overwrite"), ("append", "append"), ("scd1", None)])
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
    read_prep = {"processing": processing, "read_mode": "full_dataset", "scope": {"type": "full_dataset"}}
    result = write_module.write_pipeline_prep(frame, read_prep)
    assert result["processing"] is processing
    assert result["mode"] == mode
    assert result["options"] == {}
    assert result["load_strategy"] == strategy
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
    read_prep = {"processing": processing, "read_mode": "full_dataset", "scope": {"type": "full_dataset"}}
    monkeypatch.setattr(write_module, "get_store", lambda *_args: SimpleNamespace(kind="lakehouse"))
    result = write_module.write_pipeline_prep(frame, read_prep)
    assert {"_effective_from", "_effective_to", "_is_current"} <= set(result["df"].columns)
    monkeypatch.setattr(write_module, "get_store", lambda *_args: SimpleNamespace(kind="warehouse"))
    with pytest.raises(ValueError, match="Warehouse scd2"):
        write_module.write_pipeline_prep(frame, read_prep, target="warehouse")


def test_read_prep_preserves_warehouse_overwrite_skip(monkeypatch):
    observation = SimpleNamespace(sparkSession="spark")
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: ("config", "prod", {}))
    monkeypatch.setattr(read_module, "resolve_physical_table_identity", _identity)
    monkeypatch.setattr(read_module, "_observe_table_core", lambda *args, **kwargs: observation)
    monkeypatch.setattr(read_module, "_observation_changes", lambda _value: {
        "changed": False, "first_observation": False, "new_partitions": [],
        "changed_partitions": [], "removed_partitions": [], "reappeared_partitions": [],
        "partition_column": "snapshot_date",
    })
    monkeypatch.setattr(read_module, "resolve_table_processing_definition", lambda *args, **kwargs: {
        "load_strategy": "overwrite", "source": "data_contract", "contract_id": "c", "contract_version": 1,
    })
    result = read_module.read_pipeline_prep(
        "student_source", "students", source_target="warehouse", source_schema="dbo",
        target="warehouse", schema="dbo", source_read_strategy="incremental_partition",
        source_partition_column="snapshot_date", load_strategy="append",
    )
    assert result["read_mode"] == "skip"


def test_lakehouse_writer_exposes_scd_strategy_without_fake_append_mode(monkeypatch):
    calls = []
    monkeypatch.setattr(lakehouse_writer, "validate_dataframe_writer", lambda _df: None)
    shared = import_module("fabricops_kit.pipeline.shared")
    monkeypatch.setattr(shared, "execute_lakehouse_processing", lambda *args, **kwargs: calls.append((args, kwargs)))
    lakehouse_writer.write_lakehouse_table(
        object(), "students", mode=None, load_strategy="scd1",
        load_strategy_parameters={"key_columns": ["student_id"]},
        processing_scope={"read_mode": "full_dataset", "scope": {"type": "full_dataset"}},
    )
    assert calls[0][1]["processing"] == {"load_strategy": "scd1", "key_columns": ["student_id"]}
    with pytest.raises(ValueError, match="mode must be None"):
        lakehouse_writer.write_lakehouse_table(
            object(), "students", mode="append", load_strategy="scd1",
            load_strategy_parameters={"key_columns": ["student_id"]},
            processing_scope={"read_mode": "full_dataset", "scope": {"type": "full_dataset"}},
        )
