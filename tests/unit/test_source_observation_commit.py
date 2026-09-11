"""Tests for post-write Source Observation acceptance."""
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


def _observation(source, *, target="target-x", notebook="02_pipeline", status="observed"):
    return {
        "observation_id": f"{source}-observation",
        "source_table_id": source,
        "target_table_id": target,
        "environment_name": "dev",
        "partition_value": "2026-09-11",
        "row_count": 1,
        "min_change_value": "2026-09-11",
        "max_change_value": "2026-09-11",
        "content_fingerprint": f"fingerprint-{source}",
        "is_present": True,
        "observation_status": status,
        "_committed_at": datetime(2026, 9, 11, 1, tzinfo=UTC),
        "_activity_id": "run-1",
        "_notebook_name": notebook,
    }


def _audit():
    return {
        "_committed_by": "engineer@example.com",
        "_committed_at": datetime(2026, 9, 11, 2, tzinfo=UTC),
        "_workspace_id": "workspace",
        "_workspace_name": "Development",
        "_notebook_id": "physical-id",
        "_notebook_name": "02_pipeline",
        "_metadata_lakehouse_name": "metadata",
        "_activity_id": "run-1",
    }


def _context(*, target="target-x", sources=("source-a", "source-b"), notebook="02_pipeline"):
    return {
        "target_table_id": target,
        "source_table_ids": list(sources),
        "activity_id": "run-1",
        "notebook_name": notebook,
        "notebook_id": "physical-id",
    }


def _configure_commit(monkeypatch, observations=None):
    observations = observations or [_observation("source-a"), _observation("source-b")]
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


def test_successful_write_commits_one_observation_per_source(monkeypatch):
    written, lineage = _configure_commit(monkeypatch)
    records = shared.commit_pipeline_write_success(_context())
    assert {(row["source_table_id"], row["observation_status"]) for row in records} == {
        ("source-a", "committed"), ("source-b", "committed")
    }
    assert written == records
    assert lineage == [{
        "table_id": "target-x", "pipeline_role": "target", "activity_id": "run-1", "context": {}
    }]


@pytest.mark.parametrize(
    ("context", "observations"),
    [
        (_context(target="target-y", sources=("source-a",)), [_observation("source-a", target="target-x")]),
        (_context(sources=("source-a",), notebook="02_pipeline_b"), [_observation("source-a", notebook="02_pipeline")]),
    ],
)
def test_unrelated_target_or_notebook_observation_is_not_committed(monkeypatch, context, observations):
    written, lineage = _configure_commit(monkeypatch, observations)
    with pytest.raises(ValueError, match="No source observation"):
        shared.commit_pipeline_write_success(context)
    assert written == []
    assert lineage == []


def test_physical_notebook_id_is_diagnostic_only(monkeypatch):
    written, _ = _configure_commit(monkeypatch, [_observation("source-a")])
    context = {**_context(sources=("source-a",)), "notebook_id": "production-physical-id"}
    shared.commit_pipeline_write_success(context)
    assert written[0]["observation_status"] == "committed"


def test_lakehouse_failure_does_not_accept_observation(monkeypatch):
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


def test_lakehouse_success_accepts_observation_after_physical_write(monkeypatch):
    events = []
    monkeypatch.setattr(lakehouse, "validate_dataframe_writer", lambda df: None)
    monkeypatch.setattr(lakehouse, "resolve_configured_lakehouse_table", lambda *args, **kwargs: (None, "orders", None, "/orders"))
    monkeypatch.setattr(lakehouse, "normalize_write_mode", lambda mode: mode)
    monkeypatch.setattr(lakehouse, "repartition_dataframe_for_write", lambda df, value: df)
    monkeypatch.setattr(lakehouse, "write_delta_path", lambda *args, **kwargs: events.append("physical"))
    monkeypatch.setattr(shared, "commit_pipeline_write_success", lambda context: events.append("metadata"))
    lakehouse.write_lakehouse_table(object(), "orders", mode="append", verbose=False, success_context=_context())
    assert events == ["physical", "metadata"]


def test_warehouse_failure_does_not_accept_observation(monkeypatch):
    committed = []
    monkeypatch.setattr(warehouse, "validate_dataframe_writer", lambda df: None)
    monkeypatch.setattr(warehouse, "repartition_dataframe_for_write", lambda df, value: df)
    monkeypatch.setattr(warehouse, "resolve_configured_warehouse_table", lambda *args, **kwargs: (object(), "dbo", "orders", "dbo.orders"))
    monkeypatch.setattr(warehouse, "write_warehouse_synapsesql", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("write failed")))
    monkeypatch.setattr(shared, "commit_pipeline_write_success", lambda context: committed.append(context))
    with pytest.raises(RuntimeError, match="write failed"):
        warehouse.write_warehouse_table(object(), "dbo", "orders", success_context=_context())
    assert committed == []


def test_warehouse_success_accepts_observation_after_physical_write(monkeypatch):
    events = []
    monkeypatch.setattr(warehouse, "validate_dataframe_writer", lambda df: None)
    monkeypatch.setattr(warehouse, "repartition_dataframe_for_write", lambda df, value: df)
    monkeypatch.setattr(warehouse, "resolve_configured_warehouse_table", lambda *args, **kwargs: (object(), "dbo", "orders", "dbo.orders"))
    monkeypatch.setattr(warehouse, "write_warehouse_synapsesql", lambda *args, **kwargs: events.append("physical"))
    monkeypatch.setattr(shared, "commit_pipeline_write_success", lambda context: events.append("metadata"))
    warehouse.write_warehouse_table(object(), "dbo", "orders", success_context=_context())
    assert events == ["physical", "metadata"]
