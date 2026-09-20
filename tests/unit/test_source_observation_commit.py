"""Tests for post-write Source Observation acceptance."""
# ruff: noqa: D102, D103, D107

from datetime import UTC, datetime

import pytest

from fabricops_kit.pipeline import shared



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
        "_metadata_lakehouse_name": "Metadata",
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
    shared._CURRENT_SOURCE_OBSERVATIONS.clear()
    shared._PENDING_SOURCE_OBSERVATIONS.clear()
    shared._PENDING_SOURCE_DRIFT_OBSERVATIONS.clear()
    for observation in observations:
        shared.set_current_source_observation(environment_name="dev", activity_id="run-1", table_id=observation["source_table_id"], observation=Frame([observation]))
        shared._PENDING_SOURCE_OBSERVATIONS[("dev", "run-1", observation["source_table_id"], "target-x")] = [observation]
    monkeypatch.setattr(shared, "metadata_table_physical_schema", lambda *args: None)
    monkeypatch.setattr(shared, "build_runtime_audit_fields", lambda **kwargs: _audit())
    monkeypatch.setattr(shared, "get_spark_session", Spark)
    monkeypatch.setattr(shared, "write_lakehouse_table", lambda frame, *args, **kwargs: written.extend(frame.collect()))
    monkeypatch.setattr(shared, "persist_lineage_participation", lambda **kwargs: lineage.append(kwargs))
    return written, lineage


def test_successful_write_commits_one_observation_per_source(monkeypatch):
    written, lineage = _configure_commit(monkeypatch)
    records = shared.commit_pipeline_write_success(_context())
    assert {(row["source_table_id"], row["observation_status"]) for row in records} == {
        ("source-a", "committed"), ("source-b", "committed")
    }
    assert written == records
    assert [(item["table_id"], item["pipeline_role"]) for item in lineage] == [
        ("source-a", "source"),
        ("source-b", "source"),
        ("target-x", "target"),
    ]


def test_write_without_source_drift_still_commits_lineage(monkeypatch):
    written, lineage = _configure_commit(monkeypatch, [_observation("source-a")])
    records = shared.commit_pipeline_write_success(_context(sources=("source-b",)))
    assert records == []
    assert written == []
    assert [(item["table_id"], item["pipeline_role"]) for item in lineage] == [
        ("source-b", "source"),
        ("target-x", "target"),
    ]


def test_successful_write_commits_progress_and_source_drift_independently(monkeypatch):
    observation = _observation("source-a")
    written, _ = _configure_commit(monkeypatch, [observation])
    shared._PENDING_SOURCE_DRIFT_OBSERVATIONS[
        ("dev", "run-1", "source-a", "target-x")
    ] = [{**observation, "partition_value": "drift-partition"}]

    records = shared.commit_pipeline_write_success(
        _context(sources=("source-a",))
    )

    assert [row["observation_status"] for row in records] == [
        "committed",
        "drift_committed",
    ]
    assert written == records


def test_physical_notebook_id_is_diagnostic_only(monkeypatch):
    written, _ = _configure_commit(monkeypatch, [_observation("source-a")])
    context = {**_context(sources=("source-a",)), "notebook_id": "production-physical-id"}
    shared.commit_pipeline_write_success(context)
    assert written[0]["observation_status"] == "committed"


def test_partial_multi_target_failure_commits_only_successful_boundary(monkeypatch):
    """One successful target must not advance a failed sibling target."""
    observation = _observation("source-a")
    written, _ = _configure_commit(monkeypatch, [observation])
    failed_target_key = ("dev", "run-1", "source-a", "target-b")
    shared._PENDING_SOURCE_OBSERVATIONS[failed_target_key] = [observation]

    records = shared.commit_pipeline_write_success(
        _context(target="target-x", sources=("source-a",))
    )

    assert [(row["target_table_id"], row["max_change_value"]) for row in records] == [
        ("target-x", "2026-09-11")
    ]
    assert written == records
    assert failed_target_key in shared._PENDING_SOURCE_OBSERVATIONS
    assert not any(row["target_table_id"] == "target-b" for row in written)
