"""Real Delta snapshot persistence and atomic accepted-head lifecycle."""
# ruff: noqa: D103
import json
from copy import copy
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from fabricops_kit.pipeline import shared

pytestmark = pytest.mark.spark


@pytest.fixture
def delta_runtime(spark_session, monkeypatch, tmp_path):
    if "DeltaSparkSessionExtension" not in spark_session.conf.get("spark.sql.extensions", ""):
        pytest.skip("requires Delta Spark extensions")
    schema = shared.metadata_table_schema_registry()[shared._PROCESSING_STATE_TABLE]
    path = str(tmp_path / "configured-metadata" / "engineering" / "state")
    spark_session.createDataFrame([], schema).write.format("delta").save(path)
    source = spark_session.createDataFrame([(101, "Apple"), (102, "Banana"), (103, "Cherry")], "id int, value string")
    physical = {"orders": source}
    def read(table, **kwargs):
        return spark_session.read.format("delta").load(path) if table == shared._PROCESSING_STATE_TABLE else physical[table]
    def write(frame, table, **kwargs):
        assert table == shared._PROCESSING_STATE_TABLE and kwargs["store"] == "Metadata" and kwargs["schema"] == "engineering"
        frame.write.format("delta").mode(kwargs["mode"]).options(**(kwargs.get("options") or {})).save(path)
    monkeypatch.setattr(shared, "read_lakehouse_table", read)
    monkeypatch.setattr(shared, "write_lakehouse_table", write)
    monkeypatch.setattr(shared, "metadata_table_physical_schema", lambda *args: "engineering")
    monkeypatch.setattr(shared, "resolve_configured_lakehouse_table", lambda *args, **kwargs: (None, None, None, path))
    audit = {f.name: datetime.now(UTC) if f.name == "_committed_at" else "audit" for f in schema if f.name.startswith("_")}
    monkeypatch.setattr(shared, "build_pipeline_audit_fields", lambda **kwargs: audit)
    identity = dict(table_id="orders-id", table_name="orders", store="Bronze", schema="demo", store_type="lakehouse",
                    load_strategy_parameters_json={"key_columns": ["id"]})
    def run(run_id="run", pipeline="pipeline"):
        context = dict(config=object(), scope_workspace_id="workspace", _spark_session=spark_session)
        plan = SimpleNamespace(plan_id=run_id, pipeline_id=pipeline, workspace_id="workspace", contracts_json="{}",
            participants_json=json.dumps({"orders-id": {**identity, "roles": ["source"]}}), permits_persistence=True,
            runtime_context=context, evidence={"operations": {}})
        return plan, {**context, "execution_plan": plan}
    return SimpleNamespace(spark=spark_session, run=run, physical=physical, identity=identity,
                           state=lambda: read(shared._PROCESSING_STATE_TABLE), source=source, path=path)


def test_exact_evidence_persists_and_only_acceptance_advances_head(delta_runtime):
    rt = delta_runtime
    plan, context = rt.run()
    result = shared.observe_full_source(rt.identity, context=context)
    assert result["status"] == "first_observation"
    assert rt.state().where("record_type = 'pipeline_source_baseline'").count() == 0
    assert rt.state().where("record_type = 'source_row_evidence'").count() == 3
    shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
    assert rt.state().where("record_type = 'pipeline_source_baseline'").first()["run_id"] == "run"
    # Acceptance retry retains exactly one immutable acceptance event.
    shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
    assert rt.state().where("record_type = 'source_snapshot_acceptance'").count() == 1
    rt.physical["orders"] = rt.spark.createDataFrame([(101, "Apple"), (102, "Blueberry"), (104, "Durian")], rt.source.schema)
    second, second_context = rt.run("run2")
    result = shared.observe_full_source(rt.identity, context=second_context)
    assert (result["added_count"], result["modified_count"], result["removed_count"]) == (1, 1, 1)
    # Candidate warnings do not replace the accepted head until Finalize accepts.
    assert rt.state().where("record_type = 'pipeline_source_baseline'").first()["run_id"] == "run"
    shared.accept_pipeline_source_snapshots(second, spark_session=rt.spark)
    assert rt.state().where("record_type = 'source_snapshot_acceptance'").count() == 2
    third, third_context = rt.run("run3")
    assert shared.observe_full_source(rt.identity, context=third_context)["status"] == "passed"


def test_concurrent_first_baselines_cannot_overwrite_winner(delta_runtime):
    rt = delta_runtime
    old, old_context = rt.run("old")
    newer, newer_context = rt.run("newer")
    shared.observe_full_source(rt.identity, context=old_context)
    shared.observe_full_source(rt.identity, context=newer_context)
    shared.accept_pipeline_source_snapshots(newer, spark_session=rt.spark)
    with pytest.raises(Exception, match="baseline advanced concurrently"):
        shared.accept_pipeline_source_snapshots(old, spark_session=rt.spark)
    assert rt.state().where("record_type = 'pipeline_source_baseline'").first()["run_id"] == "newer"
    assert rt.state().where("record_type = 'source_snapshot_acceptance'").count() == 1


def test_cross_pipeline_history_is_isolated(delta_runtime):
    rt = delta_runtime
    first, context = rt.run()
    shared.observe_full_source(rt.identity, context=context)
    shared.accept_pipeline_source_snapshots(first, spark_session=rt.spark)
    other, other_context = rt.run("other-run", "other-pipeline")
    assert shared.observe_full_source(rt.identity, context=other_context)["status"] == "first_observation"
    assert other.evidence["source_drift_candidates"]["orders-id"]["pipeline_id"] == "other-pipeline"


def test_incomplete_baseline_fails_instead_of_rebaselining(delta_runtime):
    from delta.tables import DeltaTable
    rt = delta_runtime
    plan, context = rt.run()
    shared.observe_full_source(rt.identity, context=context)
    shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
    DeltaTable.forPath(rt.spark, rt.path).delete("record_type = 'source_row_evidence'")
    _plan, context = rt.run("next")
    with pytest.raises(RuntimeError, match="corrupt or incomplete"):
        shared.observe_full_source(rt.identity, context=context)


def test_additive_snapshot_column_preserves_existing_processing_state(delta_runtime):
    rt = delta_runtime
    schema = shared.metadata_table_schema_registry()[shared._PROCESSING_STATE_TABLE]
    old_schema = type(schema)([field for field in schema if field.name != "snapshot_payload_json"])
    audit = {f.name: datetime.now(UTC) if f.name == "_committed_at" else "audit" for f in old_schema if f.name.startswith("_")}
    original = rt.spark.createDataFrame([dict(record_id="legacy", record_type="source_observation", status="observed",
        pipeline_id="pipeline", workspace_id="workspace", source_table_id="orders-id", **audit)], old_schema)
    original.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(rt.path)
    plan, context = rt.run()
    assert shared.observe_full_source(rt.identity, context=context)["status"] == "first_observation"
    assert "snapshot_payload_json" in rt.state().columns
    retained = rt.state().where("record_id = 'legacy'").select(*original.columns)
    assert retained.exceptAll(original).count() == original.exceptAll(retained).count() == 0


def test_multi_source_acceptance_is_atomic_if_one_parent_is_stale(delta_runtime):
    rt = delta_runtime
    rt.physical["products"] = rt.source
    products = {**rt.identity, "table_id": "products-id", "table_name": "products"}
    stale, stale_context = rt.run("stale")
    winner, winner_context = rt.run("winner")
    shared.observe_full_source(rt.identity, context=stale_context)
    shared.observe_full_source(products, context=stale_context)
    shared.observe_full_source(products, context=winner_context)
    shared.accept_pipeline_source_snapshots(winner, spark_session=rt.spark)
    with pytest.raises(Exception, match="baseline advanced concurrently"):
        shared.accept_pipeline_source_snapshots(stale, spark_session=rt.spark)
    heads = rt.state().where("record_type = 'pipeline_source_baseline'").select("source_table_id", "run_id").collect()
    assert [(row["source_table_id"], row["run_id"]) for row in heads] == [("products-id", "winner")]


def test_simultaneous_baseline_acceptance_has_exactly_one_winner(delta_runtime):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    rt = delta_runtime
    runs = [rt.run("parallel-" + str(index)) for index in range(2)]
    for plan, context in runs:
        shared.observe_full_source(rt.identity, context=context)
    barrier = Barrier(2)
    def accept(run):
        plan, _context = run
        barrier.wait()
        try:
            shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
            return "accepted"
        except Exception:
            return "stale"
    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = list(pool.map(accept, runs))
    assert sorted(statuses) == ["accepted", "stale"]
    assert rt.state().where("record_type = 'pipeline_source_baseline'").count() == 1
    assert rt.state().where("record_type = 'source_snapshot_acceptance'").count() == 1


def test_schema_changes_are_reported_without_inventing_modifications(delta_runtime):
    rt = delta_runtime
    plan, context = rt.run()
    shared.observe_full_source(rt.identity, context=context)
    shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
    from pyspark.sql import functions as F
    rt.physical["orders"] = rt.source.withColumn("new_column", F.lit("new schema"))
    _plan, context = rt.run("schema-change")
    result = shared.observe_full_source(rt.identity, context=context)
    assert result["schema_changed"] and result["status"] == "failed"
    assert result["modified_count"] == 3 and result["removed_count"] == result["ambiguous_count"] == 0
    rt.physical["orders"] = rt.source.drop("value")
    _plan, context = rt.run("removed-column")
    result = shared.observe_full_source(rt.identity, context=context)
    assert result["status"] == "failed" and result["modified_count"] == 3
    assert result["ambiguous_count"] == result["removed_count"] == 0


def test_lost_acceptance_acknowledgement_is_verified_without_replay(delta_runtime, monkeypatch):
    rt = delta_runtime
    first, context = rt.run()
    shared.observe_full_source(rt.identity, context=context)
    shared.accept_pipeline_source_snapshots(first, spark_session=rt.spark)
    second, context = rt.run("lost-ack")
    shared.observe_full_source(rt.identity, context=context)
    original_retry = shared.retry_delta_metadata
    def lose_ack(operation):
        original_retry(operation)
        raise OSError("acknowledgement lost after the atomic head merge")
    monkeypatch.setattr(shared, "retry_delta_metadata", lose_ack)
    shared.accept_pipeline_source_snapshots(second, spark_session=rt.spark)
    assert second.evidence["source_snapshot_acceptance"]["status"] == "accepted"
    assert rt.state().where("record_type = 'source_snapshot_acceptance'").count() == 2


def test_real_read_identity_uses_store_kind_and_catalogue_keys(delta_runtime, monkeypatch):
    rt = delta_runtime
    physical = {key: value for key, value in rt.identity.items() if key not in {"store_type", "load_strategy_parameters_json"}}
    physical["store_kind"] = "lakehouse"
    monkeypatch.setattr(shared, "resolve_catalogue_table_identity", lambda *args, **kwargs: rt.identity)
    plan, context = rt.run()
    assert shared.observe_full_source(physical, context=context)["identity_strategy"] == "key"
    shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
    rt.physical["orders"] = rt.spark.createDataFrame([(101, "Apple"), (102, "Blueberry"), (103, "Cherry")], rt.source.schema)
    _plan, context = rt.run("modified")
    assert shared.observe_full_source(physical, context=context)["modified_count"] == 1


def test_public_observation_persists_bounded_sources_and_consolidated_decision(delta_runtime, monkeypatch, tmp_path):
    import importlib
    from threading import RLock
    from unittest.mock import Mock
    api = importlib.import_module("fabricops_kit.pipeline.observe_source_drift")
    rt = delta_runtime
    results_path = str(tmp_path / "configured-metadata" / "engineering" / "results")
    registry = shared.metadata_table_schema_registry()
    rt.spark.createDataFrame([], registry["METADATA_GUARDRAIL_RESULTS"]).write.format("delta").save(results_path)
    def write(frame, table, **kwargs):
        path = rt.path if table == shared._PROCESSING_STATE_TABLE else results_path
        frame.write.format("delta").mode(kwargs["mode"]).options(**(kwargs.get("options") or {})).save(path)
    monkeypatch.setattr(shared, "write_lakehouse_table", write)
    monkeypatch.setattr(api, "persist_pipeline_run", Mock())
    def activate(run_id):
        plan, context = rt.run(run_id)
        plan.lock, plan.results, plan.execution_mode = RLock(), [], "ungoverned"
        plan.evidence["failures"] = []
        session = SimpleNamespace(plan=plan, spark=rt.spark, sources=[{"table_id": "orders-id"}])
        monkeypatch.setattr(api, "current_pipeline_session", lambda: session)
        return plan
    plan = activate("baseline")
    assert api.observe_source_drift()["status"] == "first_observation"
    shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
    rt.physical["orders"] = rt.spark.createDataFrame([(101, "Apple"), (102, "Blueberry"), (104, "Durian")], rt.source.schema)
    activate("changed-run")
    with pytest.raises(RuntimeError) as error:
        api.observe_source_drift()
    result = error.value.result
    assert (result["added_count"], result["modified_count"], result["removed_count"]) == (1, 1, 1)
    rows = rt.spark.read.format("delta").load(results_path).where("run_id = 'changed-run'").collect()
    assert len(rows) == 2
    summary = next(row for row in rows if row["rule_type"] == "pipeline_observation")
    payload = json.loads(summary["result_payload_json"])
    assert not summary["can_continue"] and payload["decision"] == "blocked"
    assert payload["evaluation_id"] == result["evaluation_id"] and payload["pipeline_id"] == "pipeline"
    assert payload["sources"][0]["table_id"] == "orders-id" and "samples" not in payload["sources"][0]
    source = next(row for row in rows if row["table_id"] == "orders-id")
    evidence = json.loads(source["result_payload_json"])
    assert len(evidence["samples"]["modified"]) == 1
    assert "Blueberry" not in source["result_payload_json"] and "Banana" not in source["result_payload_json"]
