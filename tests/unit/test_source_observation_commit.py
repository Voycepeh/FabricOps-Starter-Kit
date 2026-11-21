"""Tests for post-write Source Observation acceptance."""
# ruff: noqa: D102, D103, D107

from datetime import UTC, datetime
from fabricops_kit.pipeline import shared



def _observation(source, *, target="target-x", notebook="02_pipeline"):
    return {
        "observation_id": f"{source}-observation",
        "source_table_id": source,
        "target_table_id": target,
        "workspace_id": "dev",
        "partition_value": "2026-09-11",
        "row_count": 1,
        "min_change_value": "2026-09-11",
        "max_change_value": "2026-09-11",
        "content_fingerprint": f"fingerprint-{source}",
        "is_present": True,
        "record_type": "source_observation", "status": "observed",
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
        "context": {"config": object(), "scope_workspace_id": "dev"},
        "publication": {"batch_id": "batch", "activity_id": "run-1", "committed_at": "2026-09-11T02:00:00+00:00",
                        "input_rows": 1, "strategy": "append", "run_id": None},
        "observation_snapshot": shared.snapshot_pipeline_write_observations(
            workspace_id="dev", activity_id="run-1", target_table_id=target, source_table_ids=list(sources),
        ),
    }


def _configure_commit(monkeypatch, observations=None):
    observations = observations or [_observation("source-a"), _observation("source-b")]
    written = []
    publications = []
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda context=None: (object(), "dev", {}))
    monkeypatch.setattr(shared, "_CURRENT_TABLE_IDENTITIES", {
        "source-a": {"table_name": "source_orders"},
        "source-b": {"table_name": "source_customers"},
        "target-x": {"table_name": "target_orders"},
    })
    shared._PENDING_SOURCE_OBSERVATIONS.clear()
    for observation in observations:
        shared._PENDING_SOURCE_OBSERVATIONS[("dev", "run-1", observation["source_table_id"], "target-x")] = [observation]
    monkeypatch.setattr(shared, "metadata_table_physical_schema", lambda *args: None)
    monkeypatch.setattr(shared, "build_runtime_audit_fields", lambda **kwargs: _audit())
    monkeypatch.setattr(shared, "_merge_source_observation_records", lambda records, **kw: written.extend(records))
    monkeypatch.setattr(shared, "record_pipeline_publication",
        lambda table_id, status, **kwargs: publications.append((table_id, status)))
    return written, publications


def test_successful_write_commits_one_observation_per_source(monkeypatch):
    written, publications = _configure_commit(monkeypatch)
    records = shared.commit_pipeline_write_success(_context())
    assert {(row["source_table_id"], row["status"]) for row in records if row["record_type"] != "publication_receipt"} == {
        ("source-a", "committed"), ("source-b", "committed")
    }
    assert written == records
    assert {(row["source_table_name"], row["target_table_name"]) for row in records if row["record_type"] != "publication_receipt"} == {
        ("source_orders", "target_orders"), ("source_customers", "target_orders")
    }
    assert publications == [("target-x", "committed")]


def test_source_free_write_finalizes_target_publications_without_source_observations(monkeypatch):
    """The documented source-free target must finalize without invented sources."""
    from fabricops_kit.pipeline.pipeline_write import _source_table_ids

    assert _source_table_ids([]) == []
    written, publications = _configure_commit(monkeypatch)
    staged = shared.stage_pipeline_write_observations(_context(sources=()))
    accepted = shared.commit_pipeline_write_success(_context(sources=()))
    assert [r["record_type"] for r in accepted] == ["publication_receipt"]
    assert staged[0]["record_id"] == accepted[0]["record_id"]
    assert len(written) == 2
    assert publications == [("target-x", "committed")]


def test_write_stages_target_specific_observation_before_publication(monkeypatch):
    written, publications = _configure_commit(monkeypatch, [_observation("source-a")])

    records = shared.stage_pipeline_write_observations(
        _context(sources=("source-a",))
    )

    assert publications == []
    assert written == records
    assert records[0]["target_table_id"] == "target-x"
    assert records[0]["status"] == "staged"
    assert records[0]["_activity_id"] == "run-1"


def test_write_without_source_drift_still_commits_publications(monkeypatch):
    written, publications = _configure_commit(monkeypatch, [_observation("source-a")])
    records = shared.commit_pipeline_write_success(_context(sources=("source-b",)))
    assert [r["record_type"] for r in records] == ["publication_receipt"]
    assert written == records
    assert publications == [("target-x", "committed")]


def test_successful_write_commits_only_incremental_progress(monkeypatch):
    observation = _observation("source-a")
    written, _ = _configure_commit(monkeypatch, [observation])

    records = shared.commit_pipeline_write_success(
        _context(sources=("source-a",))
    )

    assert [row["record_type"] for row in records] == [
        "publication_receipt", "incremental_checkpoint",
    ]
    assert {row["status"] for row in records} == {"committed"}
    assert written == records


def test_physical_notebook_id_is_diagnostic_only(monkeypatch):
    written, _ = _configure_commit(monkeypatch, [_observation("source-a")])
    context = {**_context(sources=("source-a",)), "notebook_id": "production-physical-id"}
    shared.commit_pipeline_write_success(context)
    assert written[0]["status"] == "committed"


def test_partial_multi_target_failure_commits_only_successful_boundary(monkeypatch):
    """One successful target must not advance a failed sibling target."""
    observation = _observation("source-a")
    written, _ = _configure_commit(monkeypatch, [observation])
    failed_target_key = ("dev", "run-1", "source-a", "target-b")
    shared._PENDING_SOURCE_OBSERVATIONS[failed_target_key] = [observation]

    records = shared.commit_pipeline_write_success(
        _context(target="target-x", sources=("source-a",))
    )

    assert [(row["target_table_id"], row["max_change_value"]) for row in records if row["record_type"] != "publication_receipt"] == [
        ("target-x", "2026-09-11")
    ]
    assert written == records
    assert failed_target_key in shared._PENDING_SOURCE_OBSERVATIONS
    assert not any(row["target_table_id"] == "target-b" for row in written)


def test_finalization_keeps_the_snapshot_staged_for_the_physical_batch(monkeypatch):
    """A later same-session read cannot be committed by an older target write."""
    prior = _observation('source-a')
    written, _ = _configure_commit(monkeypatch, [prior])
    success = _context(sources=('source-a',))
    key = ('dev', 'run-1', 'source-a', 'target-x')
    newer = {**prior, 'observation_id': 'newer', 'max_change_value': '2026-09-12'}
    shared._PENDING_SOURCE_OBSERVATIONS[key] = [newer]
    records = shared.commit_pipeline_write_success(success)
    assert [r['max_change_value'] for r in records if r['record_type'] != 'publication_receipt'] == ['2026-09-11']
    assert shared._PENDING_SOURCE_OBSERVATIONS[key] == [newer]
    assert written == records


def test_processing_history_scope_keeps_complete_receipt_packages(spark_session):
    """Filter unrelated workspaces and targets before collecting, keeping receipts with no source ID."""
    from copy import deepcopy
    records = [
        {"record_id": "receipt", "record_type": "publication_receipt", "status": "committed",
         "workspace_id": "dev", "target_table_id": "target", "publication_id": "publication"},
        {"record_id": "checkpoint", "record_type": "incremental_checkpoint", "status": "committed",
         "workspace_id": "dev", "target_table_id": "target", "source_table_id": "source", "publication_id": "publication"},
        {"record_id": "unrelated-workspace", "record_type": "unsupported", "workspace_id": "other", "target_table_id": "target"},
        {"record_id": "unrelated-target", "record_type": "unsupported", "workspace_id": "dev", "target_table_id": "other"},
    ]
    records = [{**_audit(), "status": "committed", **row} for row in records]
    frame = spark_session.createDataFrame(records, shared.processing_state_schema())
    for history in (deepcopy(records), frame):
        scoped = shared._processing_state_rows(history, workspace_id="dev", target_table_id="target")
        assert {row["record_id"] for row in scoped} == {"receipt", "checkpoint"}
        assert next(row for row in scoped if row["record_id"] == "receipt").get("source_table_id") is None
