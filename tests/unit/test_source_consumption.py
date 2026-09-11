"""Tests for post-write source-consumption state."""
# ruff: noqa: D102, D103, D107

from datetime import UTC, datetime
import importlib

import pytest

from fabricops_kit.pipeline import shared

lakehouse = importlib.import_module("fabricops_kit.io.write_lakehouse_table")
warehouse = importlib.import_module("fabricops_kit.io.write_warehouse_table")


class Frame:
    """Minimal local metadata frame."""

    def __init__(self, rows):
        self.rows = rows

    def collect(self):
        return self.rows


class Spark:
    """Capture metadata frame creation."""

    def createDataFrame(self, rows, schema=None):  # noqa: N802, ARG002
        return Frame(rows)


def _audit():
    return {
        "_committed_by": "engineer@example.com",
        "_committed_at": datetime(2026, 9, 11, tzinfo=UTC),
        "_workspace_id": "workspace",
        "_workspace_name": "Development",
        "_notebook_id": "physical-id",
        "_notebook_name": "02_pipeline",
        "_metadata_lakehouse_name": "metadata",
        "_activity_id": "run-1",
    }


def _context(*, target="target-x", sources=("source-a", "source-b")):
    return {
        "target_table_id": target,
        "source_table_ids": list(sources),
        "activity_id": "run-1",
        "notebook_name": "02_pipeline",
        "notebook_id": "physical-id",
    }


def _configure_commit(monkeypatch):
    observations = [
        {"table_id": "source-a", "environment_name": "dev", "observation_id": "a1", "_activity_id": "run-1", "_committed_at": datetime(2026, 9, 11, 1, tzinfo=UTC)},
        {"table_id": "source-b", "environment_name": "dev", "observation_id": "b1", "_activity_id": "run-1", "_committed_at": datetime(2026, 9, 11, 1, tzinfo=UTC)},
    ]
    written = []
    lineage = []
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda context=None: (object(), "dev", {}))
    monkeypatch.setattr(shared, "read_lakehouse_table_core", lambda *args, **kwargs: Frame(observations))
    monkeypatch.setattr(shared, "metadata_table_physical_schema", lambda *args: None)
    monkeypatch.setattr(shared, "build_runtime_audit_fields", lambda **kwargs: _audit())
    monkeypatch.setattr(shared, "get_spark_session", Spark)
    monkeypatch.setattr(shared, "write_lakehouse_table_core", lambda frame, *args, **kwargs: written.extend(frame.collect()))
    monkeypatch.setattr(shared, "persist_lineage_participation", lambda **kwargs: lineage.append(kwargs))
    return written, lineage


def test_successful_write_commits_one_baseline_per_source(monkeypatch):
    written, lineage = _configure_commit(monkeypatch)
    records = shared.commit_pipeline_write_success(_context())
    assert {(row["source_table_id"], row["observation_id"]) for row in records} == {
        ("source-a", "a1"), ("source-b", "b1")
    }
    assert written == records
    assert lineage == [{
        "table_id": "target-x", "pipeline_role": "target", "activity_id": "run-1", "context": {}
    }]


def test_relationship_key_keeps_targets_independent(monkeypatch):
    written, _ = _configure_commit(monkeypatch)
    first = shared.commit_pipeline_write_success(_context(target="target-x", sources=("source-a",)))[0]
    second = shared.commit_pipeline_write_success(_context(target="target-y", sources=("source-a",)))[0]
    assert first["source_consumption_id"] != second["source_consumption_id"]
    assert {row["target_table_id"] for row in written} == {"target-x", "target-y"}


def test_relationship_key_keeps_logical_notebooks_independent(monkeypatch):
    _configure_commit(monkeypatch)
    first_context = _context(sources=("source-a",))
    second_context = {**first_context, "notebook_name": "02_pipeline_b"}
    first = shared.commit_pipeline_write_success(first_context)[0]
    second = shared.commit_pipeline_write_success(second_context)[0]
    assert first["source_consumption_id"] != second["source_consumption_id"]


def test_physical_notebook_id_is_not_part_of_logical_consumption_key(monkeypatch):
    _configure_commit(monkeypatch)
    first_context = _context(sources=("source-a",))
    promoted_context = {**first_context, "notebook_id": "production-physical-id"}
    first = shared.commit_pipeline_write_success(first_context)[0]
    promoted = shared.commit_pipeline_write_success(promoted_context)[0]
    assert first["source_consumption_id"] == promoted["source_consumption_id"]


def test_lakehouse_failure_does_not_commit_success_metadata(monkeypatch):
    committed = []
    monkeypatch.setattr(lakehouse, "validate_dataframe_writer", lambda df: None)
    monkeypatch.setattr(lakehouse, "resolve_configured_lakehouse_table", lambda *args, **kwargs: (None, "orders", None, "/orders"))
    monkeypatch.setattr(lakehouse, "normalize_write_mode", lambda mode: mode)
    monkeypatch.setattr(lakehouse, "repartition_dataframe_for_write", lambda df, value: df)
    monkeypatch.setattr(lakehouse, "write_delta_path", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("write failed")))
    monkeypatch.setattr(shared, "commit_pipeline_write_success", lambda context: committed.append(context))
    with pytest.raises(RuntimeError, match="write failed"):
        lakehouse.write_lakehouse_table(object(), "orders", mode="append", verbose=False, success_context=_context())
    assert committed == []


def test_lakehouse_success_commits_after_physical_write(monkeypatch):
    events = []
    monkeypatch.setattr(lakehouse, "validate_dataframe_writer", lambda df: None)
    monkeypatch.setattr(lakehouse, "resolve_configured_lakehouse_table", lambda *args, **kwargs: (None, "orders", None, "/orders"))
    monkeypatch.setattr(lakehouse, "normalize_write_mode", lambda mode: mode)
    monkeypatch.setattr(lakehouse, "repartition_dataframe_for_write", lambda df, value: df)
    monkeypatch.setattr(lakehouse, "write_delta_path", lambda *args, **kwargs: events.append("physical"))
    monkeypatch.setattr(shared, "commit_pipeline_write_success", lambda context: events.append("metadata"))
    lakehouse.write_lakehouse_table(object(), "orders", mode="append", verbose=False, success_context=_context())
    assert events == ["physical", "metadata"]


def test_warehouse_failure_does_not_commit_success_metadata(monkeypatch):
    committed = []
    monkeypatch.setattr(warehouse, "validate_dataframe_writer", lambda df: None)
    monkeypatch.setattr(warehouse, "repartition_dataframe_for_write", lambda df, value: df)
    monkeypatch.setattr(warehouse, "resolve_configured_warehouse_table", lambda *args, **kwargs: (object(), "dbo", "orders", "dbo.orders"))
    monkeypatch.setattr(warehouse, "write_warehouse_synapsesql", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("write failed")))
    monkeypatch.setattr(shared, "commit_pipeline_write_success", lambda context: committed.append(context))
    with pytest.raises(RuntimeError, match="write failed"):
        warehouse.write_warehouse_table(object(), "dbo", "orders", success_context=_context())
    assert committed == []


def test_warehouse_success_commits_after_physical_write(monkeypatch):
    events = []
    monkeypatch.setattr(warehouse, "validate_dataframe_writer", lambda df: None)
    monkeypatch.setattr(warehouse, "repartition_dataframe_for_write", lambda df, value: df)
    monkeypatch.setattr(warehouse, "resolve_configured_warehouse_table", lambda *args, **kwargs: (object(), "dbo", "orders", "dbo.orders"))
    monkeypatch.setattr(warehouse, "write_warehouse_synapsesql", lambda *args, **kwargs: events.append("physical"))
    monkeypatch.setattr(shared, "commit_pipeline_write_success", lambda context: events.append("metadata"))
    warehouse.write_warehouse_table(object(), "dbo", "orders", success_context=_context())
    assert events == ["physical", "metadata"]
