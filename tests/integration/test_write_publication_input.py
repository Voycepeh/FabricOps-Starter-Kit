"""Final publication inputs and metrics with real Spark preparation and cache cleanup."""
# ruff: noqa: D103
from datetime import UTC, datetime
from importlib import import_module
from types import SimpleNamespace

import pytest

from fabricops_kit.pipeline import shared

writer = import_module("fabricops_kit.pipeline.pipeline_write")
io = import_module("fabricops_kit.io")

pytestmark = pytest.mark.spark


def _persistent_rdd_ids(spark):
    """Track cache identities without relying on unrelated RDDs surviving JVM GC."""
    iterator = spark.sparkContext._jsc.sc().getPersistentRDDs().keysIterator()
    identities = set()
    while iterator.hasNext():
        identities.add(int(iterator.next()))
    return identities


@pytest.fixture
def publication_input_runtime(monkeypatch, spark_session):
    """Exercise batch materialization while isolating Fabric transport and metadata."""
    state = SimpleNamespace(strategy="overwrite", store_type="warehouse",
                            confirmed=False, fail=None, native=None, received=None,
                            incoming=None, target=None)
    context = {"config": object(), "scope_workspace_id": "dev"}
    audit = dict(_committed_at=datetime.now(UTC), _committed_by="tester", _activity_id="activity",
                 _workspace_id="workspace", _workspace_name="workspace", _notebook_id="notebook",
                 _notebook_name="02_pipeline", _metadata_lakehouse_name="Metadata")
    def identity(*args, **kwargs):
        return dict(table_id="target", table_name="target", store="Silver", schema="demo",
                    store_type=state.store_type, store_kind=state.store_type)
    def processing(*args, **kwargs):
        return {"load_strategy": state.strategy, **({"key_columns": ["id"]} if state.strategy.startswith("scd") else {}),
                **({"effective_column": "modified", "tracked_columns": ["value"]} if state.strategy == "scd2" else {})}
    def publish(frame, *args, context=None, **kwargs):
        state.received = frame
        state.metrics = (context or {}).get("_fabricops_write_metrics", {})
        assert state.metrics.get("rows_committed") is None
        if state.fail == "physical":
            raise RuntimeError("physical publication failed")
        if state.strategy == "append_new_only":
            state.target = state.incoming
        state.confirmed = True
        metrics = (context or {}).get("_fabricops_write_metrics", {})
        if state.native is not None:
            metrics.update(rows_committed=state.native, measurement_source="delta_commit")
    monkeypatch.setattr(writer, "resolve_physical_table_identity", identity)
    monkeypatch.setattr(writer, "resolve_target_audit_fields", lambda c: audit)
    monkeypatch.setattr(writer, "resolve_table_processing_definition", processing)
    monkeypatch.setattr(writer, "_persist_target_processing", lambda **kw: None)
    monkeypatch.setattr(writer, "_writer_scheduled_refresh", lambda **kw: {})
    monkeypatch.setattr(shared, "read_lakehouse_table", lambda *a, **kw: [])
    monkeypatch.setattr(shared, "metadata_table_physical_schema", lambda *a: None)
    monkeypatch.setattr(shared, "_find_applied_publication", lambda *a, **kw: None)
    monkeypatch.setattr(shared, "_physical_target_has_publication", lambda *a, **kw: state.confirmed and state.fail != "confirmation")
    monkeypatch.setattr(shared, "stage_pipeline_write_observations", lambda *a: None)
    monkeypatch.setattr(shared, "commit_pipeline_write_success", lambda *a: None)
    monkeypatch.setattr(io, "write_lakehouse_table", publish)
    monkeypatch.setattr(io, "write_warehouse_table", publish)
    monkeypatch.setattr(shared, "execute_lakehouse_processing", publish)
    monkeypatch.setattr(import_module("fabricops_kit.io.shared"), "execute_warehouse_processing", publish)
    incoming = spark_session.createDataFrame([(1, "masked", 1), (2, "masked", 2)], "id int, value string, modified int")
    state.target = incoming.where("id = 1")
    def target_hashes(*a, cache_hashes=False, **kw):
        hashes = shared.add_row_hash(state.target).select("_row_hash")
        return hashes.persist() if cache_hashes else hashes
    monkeypatch.setattr(writer, "validate_target_row_hash", target_hashes)
    def run(frame=incoming):
        state.incoming = frame
        return writer.pipeline_write(frame, store="Silver", schema="demo", table_name="target",
                                     source_table_ids=[], verbose=False, context=context)
    return state, context, incoming, run


@pytest.mark.parametrize("store_type", ["lakehouse", "warehouse"])
@pytest.mark.parametrize("strategy", ["overwrite", "append_all", "append_new_only", "scd1", "scd2"])
def test_final_input_is_writer_input_and_usable_after_cleanup(publication_input_runtime, spark_session, store_type, strategy):
    state, _, incoming, run = publication_input_runtime
    state.store_type, state.strategy = store_type, strategy
    caches = _persistent_rdd_ids(spark_session)
    result = run()
    frame = result["dataframe"]
    assert frame is state.received
    assert set(incoming.columns) | {"_row_hash", "_committed_at", "_activity_id"} <= set(frame.columns)
    assert sorted(r.id for r in frame.limit(10).collect()) == ([2] if strategy == "append_new_only" else [1, 2])
    assert {r.value for r in frame.collect()} == {"masked"}
    if strategy == "scd2":
        assert {"_effective_from", "_effective_to", "_is_current"} <= set(frame.columns)
        assert all(r._effective_from == r.modified and r._effective_to is None and r._is_current for r in frame.collect())
    assert _persistent_rdd_ids(spark_session) - caches
    metrics = result["write_metrics"]
    assert metrics["input_rows"] == 2
    assert metrics["total_target_rows"] is None
    expected = (1 if strategy == "append_new_only" else 2) if store_type == "warehouse" and not strategy.startswith("scd") else None
    assert metrics["rows_committed"] == expected
    if strategy.startswith("scd"):
        assert all(metrics[k] is None for k in ("rows_inserted", "rows_updated", "versions_inserted", "versions_expired"))
    frame.unpersist(blocking=True)
    assert _persistent_rdd_ids(spark_session) <= caches


def test_append_new_only_snapshot_survives_target_change(publication_input_runtime, spark_session):
    state, _, _, run = publication_input_runtime
    incoming = spark_session.createDataFrame(
        [(value, f"value-{value}", value) for value in range(12)],
        "id int, value string, modified int",
    )
    state.strategy = "append_new_only"
    state.target = incoming.where("id < 8")

    result = run(incoming)
    state.target = incoming
    submitted = result["dataframe"]

    assert submitted.count() == 4
    assert sorted(row.id for row in submitted.collect()) == [8, 9, 10, 11]
    assert submitted.count() == 4
    assert result["write_metrics"]["input_rows"] == 12
    assert result["write_metrics"]["rows_inserted"] == 4
    assert result["write_metrics"]["rows_committed"] == 4
    submitted.unpersist(blocking=True)


@pytest.mark.parametrize("failure", ["physical", "confirmation"])
def test_failure_never_finalizes_and_cleans_caches(publication_input_runtime, monkeypatch, spark_session, failure):
    state, _, _, run = publication_input_runtime
    state.strategy, state.fail = "append_new_only", failure
    from unittest.mock import Mock
    finalize = Mock()
    monkeypatch.setattr(shared, "commit_pipeline_write_success", finalize)
    caches = _persistent_rdd_ids(spark_session)
    with pytest.raises(RuntimeError) as raised:
        run()
    assert not getattr(raised.value, "published", False)
    assert getattr(raised.value, "write_metrics", {}).get("rows_committed") is None
    assert state.metrics["rows_committed"] is None
    finalize.assert_not_called()
    assert _persistent_rdd_ids(spark_session) <= caches


@pytest.mark.parametrize("store_type", ["lakehouse", "warehouse"])
def test_native_metrics_take_priority(publication_input_runtime, store_type):
    state, _, _, run = publication_input_runtime
    state.store_type, state.native = store_type, 7
    result = run()
    assert result["write_metrics"]["rows_committed"] == 7
    assert result["write_metrics"]["measurement_source"] == "delta_commit"


def test_dry_run_returns_prepared_input_without_publication(publication_input_runtime):
    state, context, _, run = publication_input_runtime
    context["execution_plan"] = SimpleNamespace(permits_persistence=False)
    result = run()
    assert result["published"] is False
    assert result["write_metrics"]["rows_committed"] is None
    assert state.received is None
    assert {"_row_hash", "_committed_at"} <= set(result["dataframe"].columns)
    assert len(result["dataframe"].limit(10).collect()) == 2


def test_no_unseen_hashes_returns_empty_input_and_zero_commits(publication_input_runtime, spark_session):
    state, _, incoming, run = publication_input_runtime
    state.strategy = "append_new_only"
    caches = _persistent_rdd_ids(spark_session)
    result = run(incoming.where("id = 1"))
    assert result["published"] is False
    assert result["publication_status"] == "no_unseen_hashes"
    assert result["dataframe"].collect() == []
    assert result["write_metrics"]["rows_committed"] == 0
    assert state.received is None
    result["dataframe"].unpersist(blocking=True)
    assert _persistent_rdd_ids(spark_session) <= caches


def test_empty_incremental_scope_returns_usable_prepared_input(publication_input_runtime, monkeypatch):
    state, _, incoming, run = publication_input_runtime
    state.strategy = "append_all"
    monkeypatch.setattr(writer, "incremental_publication_scopes", lambda **kw: {"source": {"has_data": False}})
    result = run(incoming.limit(0))
    assert result["publication_status"] == "empty_incremental_scope"
    assert result["dataframe"].collect() == []
    assert {"_row_hash", "_committed_at"} <= set(result["dataframe"].columns)
    assert result["write_metrics"]["rows_committed"] == 0
    result["dataframe"].unpersist(blocking=True)


def test_metadata_failure_preserves_confirmed_warehouse_metrics(publication_input_runtime, monkeypatch):
    _, _, _, run = publication_input_runtime
    def fail(*args):
        raise RuntimeError("metadata finalization failed")
    monkeypatch.setattr(shared, "commit_pipeline_write_success", fail)
    with pytest.raises(RuntimeError) as raised:
        run()
    assert raised.value.published is True
    assert raised.value.write_metrics["rows_committed"] == 2
    assert raised.value.failed_stage == "Metadata finalization"


def test_already_loaded_append_returns_no_new_insertions(publication_input_runtime, monkeypatch):
    state, _, _, run = publication_input_runtime
    state.strategy, state.confirmed = "append_new_only", True
    enter = shared.PublicationBatch.__enter__
    def applied(batch):
        enter(batch)
        batch.already_applied = True
        return batch
    monkeypatch.setattr(shared.PublicationBatch, "__enter__", applied)
    result = run()
    assert result["publication_status"] == "already_applied"
    assert result["dataframe"].collect() == []
    assert result["write_metrics"]["rows_committed"] == 0
    assert state.received is None
    result["dataframe"].unpersist(blocking=True)
