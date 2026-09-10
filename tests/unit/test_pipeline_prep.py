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


def _identity(table_id="warehouse:source:dbo:student_source", *, store_type="warehouse"):
    return {
        "table_id": table_id,
        "store_type": store_type,
        "target": "source" if ":source:" in table_id else "unified",
        "schema": "dbo",
        "table_name": table_id.rsplit(":", 1)[-1],
        "load_strategy": "overwrite",
        "load_strategy_parameters_json": "{}",
    }


def _patch_source_identity(monkeypatch, identity=None):
    resolved = identity or _identity()
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: ("config", "dev", {}))
    monkeypatch.setattr(
        read_module,
        "resolve_catalogue_table_identity",
        lambda _config, _env, table_id, **_kwargs: resolved if table_id == resolved["table_id"] else pytest.fail(table_id),
    )
    monkeypatch.setattr(read_module, "persist_lineage_participation", lambda **_kwargs: "lineage-id")
    return resolved


def _patch_target_processing(monkeypatch, processing, *, store_type="lakehouse"):
    identity = _identity("lakehouse:unified:dbo:students", store_type=store_type)
    monkeypatch.setattr(write_module, "resolve_fabric_context", lambda: ("config", "dev", {}))
    monkeypatch.setattr(write_module, "resolve_catalogue_table_identity", lambda *_args, **_kwargs: identity)
    monkeypatch.setattr(write_module, "catalogue_authored_processing", lambda value: {"load_strategy": value["load_strategy"]})
    monkeypatch.setattr(write_module, "resolve_table_processing_definition", lambda *_args, **_kwargs: processing)
    monkeypatch.setattr(write_module, "persist_lineage_participation", lambda **_kwargs: "lineage-id")
    monkeypatch.setattr(write_module, "resolve_target_audit_fields", lambda _context: {
        "_committed_at": "2026-08-22T00:00:00Z", "_committed_by": "engineer",
        "_activity_id": "activity", "_workspace_id": "workspace",
        "_notebook_id": "notebook", "_notebook_name": "02_pipeline",
    })
    return identity


def test_read_prep_resolves_registered_source_and_registers_lineage(monkeypatch):
    identity = _patch_source_identity(monkeypatch)
    lineage = []
    monkeypatch.setattr(read_module, "persist_lineage_participation", lambda **kwargs: lineage.append(kwargs))

    result = read_module.read_pipeline_prep(source_table_id=identity["table_id"])

    assert result == {"table_id": identity["table_id"], "source": identity}
    assert lineage == [{"table_id": identity["table_id"], "pipeline_role": "source", "context": {}}]


def test_read_prep_resolves_physical_lakehouse_and_warehouse_sources(monkeypatch):
    resolved = []
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: ("config", "dev", {}))
    monkeypatch.setattr(read_module, "persist_lineage_participation", lambda **_kwargs: None)
    monkeypatch.setattr(
        read_module,
        "resolve_physical_table_identity",
        lambda _config, _env, **coordinates: resolved.append(coordinates)
        or _identity(
            f"{coordinates['target']}:{coordinates['schema']}:{coordinates['table_name']}",
            store_type="warehouse" if coordinates["target"] == "warehouse" else "lakehouse",
        ),
    )

    lakehouse = read_module.read_pipeline_prep(
        source_target="source", source_schema="dbo", source_table="orders"
    )
    warehouse = read_module.read_pipeline_prep(
        source_target="warehouse", source_schema="dbo", source_table="customers"
    )

    assert lakehouse["source"]["store_kind"] == "lakehouse"
    assert warehouse["source"]["store_kind"] == "warehouse"
    assert resolved == [
        {"target": "source", "schema": "dbo", "table_name": "orders"},
        {"target": "warehouse", "schema": "dbo", "table_name": "customers"},
    ]


def test_read_prep_requires_source_identity():
    with pytest.raises(ValueError, match="source_table_id or both source_target"):
        read_module.read_pipeline_prep()


def test_read_prep_rejects_unknown_source_table_id(monkeypatch):
    lineage = []
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: ("config", "dev", {}))
    monkeypatch.setattr(
        read_module,
        "resolve_catalogue_table_identity",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("No active registered Catalogue table")),
    )
    monkeypatch.setattr(read_module, "persist_lineage_participation", lambda **kwargs: lineage.append(kwargs))
    with pytest.raises(ValueError, match="No active registered Catalogue table"):
        read_module.read_pipeline_prep(source_table_id="wrong")
    assert lineage == []


def test_read_prep_has_no_incremental_read_arguments():
    from inspect import signature

    parameters = signature(read_module.read_pipeline_prep).parameters
    removed = {
        "source_read_strategy", "target_table_id", "target_target", "target_schema", "target_table",
        "source_watermark_column", "source_partition_column",
    }
    assert parameters.keys().isdisjoint(removed)


@pytest.mark.parametrize(("strategy", "mode"), [("overwrite", "overwrite"), ("append", "append"), ("scd1", None)])
def test_write_prep_resolves_target_processing(monkeypatch, spark_session, strategy, mode):
    processing = {"load_strategy": strategy}
    if strategy == "scd1":
        processing["key_columns"] = ["student_id"]
    identity = _patch_target_processing(monkeypatch, processing)
    frame = spark_session.createDataFrame([(1, "active")], ["student_id", "status"])
    source_prep = {"table_id": "warehouse:source:dbo:students", "source": {}}

    result = write_module.write_pipeline_prep(
        frame, target_table_id=identity["table_id"], source_preps=[source_prep]
    )

    assert result["target"] is identity
    assert result["processing"] is processing
    assert result["mode"] == mode
    assert result["load_strategy"] == strategy
    assert "_committed_at" in result["df"].columns


def test_write_prep_adds_scd2_lifecycle_for_warehouse(monkeypatch, spark_session):
    processing = {"load_strategy": "scd2", "key_columns": ["student_id"], "effective_column": "effective_at"}
    identity = _patch_target_processing(monkeypatch, processing, store_type="warehouse")
    frame = spark_session.createDataFrame([(1, "active", "2026-08-22")], ["student_id", "status", "effective_at"])
    result = write_module.write_pipeline_prep(
        frame,
        target_table_id=identity["table_id"],
        source_preps=[{"table_id": "warehouse:source:dbo:students", "source": {}}],
    )
    assert result["mode"] is None
    assert result["target_kind"] == "warehouse"
    assert {"_effective_from", "_effective_to", "_is_current"} <= set(result["df"].columns)


def test_write_prep_preserves_target_partition_overwrite(monkeypatch, spark_session):
    processing = {"load_strategy": "overwrite", "partition_column": "business_date"}
    identity = _patch_target_processing(monkeypatch, processing)
    frame = spark_session.createDataFrame([(1, "2026-09-09"), (2, "2026-09-10")], ["id", "business_date"])

    result = write_module.write_pipeline_prep(
        frame,
        target_table_id=identity["table_id"],
        source_preps=[{"table_id": "warehouse:source:dbo:orders", "source": {}}],
    )

    assert set(result["scope"]["scope"]["values"]) == {"2026-09-09", "2026-09-10"}
    assert {row["_partition_bucket"] for row in result["df"].select("_partition_bucket").collect()} == {
        "2026-09-09", "2026-09-10",
    }
    assert "replaceWhere" in result["options"]


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




def test_public_writers_have_no_completion_context():
    """Persistent checkpoint completion is not part of either writer API."""
    import inspect

    assert "completion_context" not in inspect.signature(lakehouse_writer.write_lakehouse_table).parameters
    assert "completion_context" not in inspect.signature(warehouse_writer.write_warehouse_table).parameters
