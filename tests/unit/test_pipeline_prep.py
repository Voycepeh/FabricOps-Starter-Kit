"""Tests for the public pipeline preparation boundary."""
# ruff: noqa: D103

from __future__ import annotations

from importlib import import_module
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.unit

read_module = import_module("fabricops_kit.pipeline.read_pipeline_prep")
shared_module = import_module("fabricops_kit.pipeline.shared")
warehouse_writer = import_module("fabricops_kit.io.write_warehouse_table")
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
    monkeypatch.setattr(read_module, "_successful_partition_observation_id", lambda *args, **kwargs: None)
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
    monkeypatch.setattr(read_module, "_source_upper_watermark", lambda *_args, **_kwargs: {
        "upper_watermark": upper, "data_type": "string", "row_count": 1,
        "non_null_count": 1, "distinct_count": 1,
    })
    monkeypatch.setattr(read_module, "_coerce_checkpoint", lambda value, *_args, **_kwargs: value)
    result = read_module._watermark_scope(
        {"table_id": "warehouse:source:dbo:bookings"}, "modified_datetime",
        config="config", env="dev", spark_session="spark", context={},
    )
    assert result["read_mode"] == expected_mode
    if expected_mode == "skip":
        assert result["candidate_checkpoint"] is None
    else:
        assert result["candidate_checkpoint"]["status"] == "candidate"
    if expected_mode == "incremental_subset":
        assert result["scope"]["lower_inclusive"] is False
        assert result["scope"]["upper_inclusive"] is True
        assert result["scope"]["lower_bound"] == previous
        assert result["scope"]["upper_bound"] == upper


def test_watermark_rejects_duplicate_values_that_can_hide_late_rows(monkeypatch):
    monkeypatch.setattr(read_module, "_checkpoint_value", lambda *_args, **_kwargs: "2026-08-26 10:00")
    monkeypatch.setattr(read_module, "_source_upper_watermark", lambda *_args, **_kwargs: {
        "upper_watermark": "2026-08-26 12:00", "data_type": "string", "row_count": 2,
        "non_null_count": 2, "distinct_count": 1,
    })
    with pytest.raises(ValueError, match="globally unique"):
        read_module._watermark_scope(
            {"table_id": "warehouse:source:dbo:bookings"}, "modified_datetime",
            config="config", env="dev", spark_session="spark", context={},
        )


def test_checkpoint_advances_only_after_successful_target_write(monkeypatch):
    writes = []
    completion = {"sources": [{
        "type": "watermark",
        "source": {"table_id": "warehouse:source:dbo:bookings"},
        "source_processing": {"read_strategy": "incremental_watermark", "watermark_column": "modified_datetime"},
        "candidate": {"status": "candidate", "column": "modified_datetime", "value": "2026-08-26 12:00"},
    }]}
    audit = {
        "_committed_by": "engineer", "_committed_at": "2026-08-26T12:01:00",
        "_workspace_id": "workspace", "_workspace_name": "workspace",
        "_notebook_id": "notebook", "_notebook_name": "02_pipeline",
        "_metadata_lakehouse_name": "metadata", "_activity_id": "activity",
    }
    monkeypatch.setattr(shared_module, "resolve_fabric_context", lambda **_kwargs: ("config", "dev", {}))
    monkeypatch.setattr(shared_module, "build_runtime_audit_fields", lambda **_kwargs: audit)
    monkeypatch.setattr(shared_module, "get_spark_session", lambda: SimpleNamespace(
        createDataFrame=lambda rows, schema=None: {"rows": rows, "schema": schema}
    ))
    monkeypatch.setattr(shared_module, "coerce_metadata_row_types", lambda _table, row: row)
    monkeypatch.setattr(shared_module, "configured_lakehouse_schema", lambda *_args: "metadata")
    monkeypatch.setattr(shared_module, "write_lakehouse_table_core", lambda frame, *args, **kwargs: writes.append((args[0], frame["rows"][0])))

    shared_module.complete_source_processing(completion)
    assert writes[0][0] == "METADATA_SOURCE_WATERMARK_CHECKPOINT"
    assert writes[0][1]["watermark_value"] == "2026-08-26 12:00"

    shared_module.complete_source_processing({"sources": [{
        "type": "partition", "environment_name": "dev", "table_id": "source",
        "observation_id": "published-observation",
    }]})
    assert writes[1][0] == "METADATA_SOURCE_PARTITION_CHECKPOINT"
    assert writes[1][1]["observation_id"] == "published-observation"


def test_checkpoint_persistence_failure_surfaces_after_physical_write(monkeypatch):
    events = []
    monkeypatch.setattr(lakehouse_writer, "validate_dataframe_writer", lambda _df: None)
    monkeypatch.setattr(lakehouse_writer, "resolve_configured_lakehouse_table", lambda *args, **kwargs: (None, None, None, "path"))
    monkeypatch.setattr(lakehouse_writer, "write_delta_path", lambda *args, **kwargs: events.append("write"))
    monkeypatch.setattr(shared_module, "complete_source_processing", lambda _context, **_kwargs: (_ for _ in ()).throw(RuntimeError("checkpoint failed")))
    with pytest.raises(RuntimeError, match="checkpoint failed"):
        lakehouse_writer.write_lakehouse_table(object(), "target", verbose=False, completion_context={"sources": []})
    assert events == ["write"]


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
    monkeypatch.setattr(read_module, "_successful_partition_observation_id", lambda *args, **kwargs: None)
    monkeypatch.setattr(read_module, "_observe_table_core", lambda *args, **kwargs: observation)
    monkeypatch.setattr(read_module, "_observation_changes", lambda value, **_kwargs: changes if value is observation else pytest.fail())
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
    monkeypatch.setattr(read_module, "_successful_partition_observation_id", lambda *args, **kwargs: None)
    monkeypatch.setattr(read_module, "_observe_table_core", lambda *args, **kwargs: observation)
    monkeypatch.setattr(read_module, "_observation_changes", lambda _value, **_kwargs: {
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
    monkeypatch.setattr(read_module, "_successful_partition_observation_id", lambda *args, **kwargs: None)
    monkeypatch.setattr(read_module, "_observe_table_core", lambda *args, **kwargs: observation)
    monkeypatch.setattr(read_module, "_observation_changes", lambda _value, **_kwargs: {
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

@pytest.mark.parametrize("strategy", ["overwrite", "append", "scd1", "scd2"])
def test_lakehouse_governed_completion_runs_after_each_supported_write(monkeypatch, strategy):
    events = []
    monkeypatch.setattr(lakehouse_writer, "validate_dataframe_writer", lambda _df: None)
    monkeypatch.setattr(shared_module, "complete_source_processing", lambda completion, **_kwargs: events.append(("complete", completion)))
    completion = {"sources": [{"type": "watermark"}]}
    if strategy in {"scd1", "scd2"}:
        monkeypatch.setattr(import_module("fabricops_kit.pipeline.shared"), "execute_lakehouse_processing", lambda *args, **kwargs: events.append(("write", strategy)))
        lakehouse_writer.write_lakehouse_table(
            object(), "target", mode=None, load_strategy=strategy,
            processing_scope={"read_mode": "full_dataset", "scope": {"type": "full_dataset"}},
            completion_context=completion,
        )
    else:
        monkeypatch.setattr(lakehouse_writer, "resolve_configured_lakehouse_table", lambda *args, **kwargs: (None, None, None, "path"))
        monkeypatch.setattr(lakehouse_writer, "write_delta_path", lambda *args, **kwargs: events.append(("write", strategy)))
        lakehouse_writer.write_lakehouse_table(
            object(), "target", mode=strategy, load_strategy=strategy,
            processing_scope={"read_mode": "full_dataset", "scope": {"type": "full_dataset"}},
            completion_context=completion, verbose=False,
        )
    assert events == [("write", strategy), ("complete", completion)]


@pytest.mark.parametrize("mode", ["append", "overwrite"])
def test_warehouse_completion_runs_after_supported_write(monkeypatch, mode):
    events = []
    monkeypatch.setattr(warehouse_writer, "validate_dataframe_writer", lambda _df: None)
    monkeypatch.setattr(warehouse_writer, "repartition_dataframe_for_write", lambda df, _value: df)
    monkeypatch.setattr(warehouse_writer, "resolve_configured_warehouse_table", lambda *args, **kwargs: ("store", "dbo", "target", "dbo.target"))
    monkeypatch.setattr(warehouse_writer, "write_warehouse_synapsesql", lambda *args, **kwargs: events.append("write"))
    monkeypatch.setattr(shared_module, "complete_source_processing", lambda _context, **_kwargs: events.append("complete"))
    warehouse_writer.write_warehouse_table(object(), "dbo", "target", mode=mode, completion_context={"sources": []})
    assert events == ["write", "complete"]


def test_writer_failure_never_attempts_completion(monkeypatch):
    monkeypatch.setattr(warehouse_writer, "validate_dataframe_writer", lambda _df: None)
    monkeypatch.setattr(warehouse_writer, "repartition_dataframe_for_write", lambda df, _value: df)
    monkeypatch.setattr(warehouse_writer, "resolve_configured_warehouse_table", lambda *args, **kwargs: ("store", "dbo", "target", "dbo.target"))
    monkeypatch.setattr(warehouse_writer, "write_warehouse_synapsesql", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("write failed")))
    monkeypatch.setattr(shared_module, "complete_source_processing", lambda _context, **_kwargs: pytest.fail("completion"))
    with pytest.raises(RuntimeError, match="write failed"):
        warehouse_writer.write_warehouse_table(object(), "dbo", "target", completion_context={"sources": []})


def test_ungoverned_writer_does_not_resolve_completion_state(monkeypatch):
    monkeypatch.setattr(lakehouse_writer, "validate_dataframe_writer", lambda _df: None)
    monkeypatch.setattr(lakehouse_writer, "resolve_configured_lakehouse_table", lambda *args, **kwargs: (None, None, None, "path"))
    monkeypatch.setattr(lakehouse_writer, "write_delta_path", lambda *args, **kwargs: None)
    monkeypatch.setattr(shared_module, "complete_source_processing", lambda _context, **_kwargs: pytest.fail("checkpoint"))
    lakehouse_writer.write_lakehouse_table(object(), "target", verbose=False)


def test_partition_retry_compares_with_last_successful_observation():
    history = [
        {"observation_id": "successful", "table_id": "source", "environment_name": "dev", "_committed_at": 1},
        {"observation_id": "failed-run", "table_id": "source", "environment_name": "dev", "_committed_at": 2},
    ]
    previous = import_module("fabricops_kit.pipeline.check_changes")._previous_observation(
        history, table_id="source", environment_name="dev", committed_at=3,
        observation_id="successful",
    )
    assert [row["observation_id"] for row in previous] == ["successful"]


def test_explicit_writer_context_is_reused_for_checkpoint_completion(monkeypatch):
    explicit_context = {"config": "prod-config", "env": "prod", "marker": "explicit"}
    resolved_context = {**explicit_context, "resolved": True}
    observed = {}

    monkeypatch.setattr(lakehouse_writer, "validate_dataframe_writer", lambda _df: None)
    monkeypatch.setattr(
        lakehouse_writer,
        "resolve_configured_lakehouse_table",
        lambda *args, context=None, **kwargs: (
            observed.setdefault("target_context", context), None, None, "prod-path"
        ),
    )
    monkeypatch.setattr(lakehouse_writer, "write_delta_path", lambda *args, **kwargs: None)

    def resolve_context(*, context=None, **_kwargs):
        observed["completion_input_context"] = context
        assert context is explicit_context
        return "prod-config", "prod", resolved_context

    monkeypatch.setattr(shared_module, "resolve_fabric_context", resolve_context)
    monkeypatch.setattr(shared_module, "build_runtime_audit_fields", lambda **_kwargs: {
        "_committed_by": "engineer", "_committed_at": "2026-08-26T12:01:00",
        "_workspace_id": "workspace", "_workspace_name": "workspace",
        "_notebook_id": "notebook", "_notebook_name": "02_pipeline",
        "_metadata_lakehouse_name": "metadata", "_activity_id": "activity",
    })
    monkeypatch.setattr(shared_module, "get_spark_session", lambda: SimpleNamespace(
        createDataFrame=lambda rows, schema=None: {"rows": rows, "schema": schema}
    ))
    monkeypatch.setattr(shared_module, "coerce_metadata_row_types", lambda _table, row: row)
    monkeypatch.setattr(shared_module, "configured_lakehouse_schema", lambda config, env, _target: (
        observed.setdefault("metadata_identity", (config, env)) or "metadata"
    ))
    monkeypatch.setattr(
        shared_module,
        "write_lakehouse_table_core",
        lambda *_args, context=None, **_kwargs: observed.setdefault("checkpoint_context", context),
    )

    lakehouse_writer.write_lakehouse_table(
        object(),
        "target",
        context=explicit_context,
        completion_context={"sources": [{
            "type": "watermark",
            "source": {"table_id": "lakehouse:source:dbo:bookings"},
            "source_processing": {
                "read_strategy": "incremental_watermark",
                "watermark_column": "modified_datetime",
            },
            "candidate": {
                "status": "candidate",
                "column": "modified_datetime",
                "value": "2026-08-26 12:00",
            },
        }]},
        verbose=False,
    )

    assert observed["target_context"] is explicit_context
    assert observed["completion_input_context"] is explicit_context
    assert observed["metadata_identity"] == ("prod-config", "prod")
    assert observed["checkpoint_context"] is resolved_context
