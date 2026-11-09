"""Exact distributed source history comparisons without raw business-row retention."""
# ruff: noqa: D103
import json
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from fabricops_kit.pipeline import shared

pytestmark = pytest.mark.spark


def compare(spark, before, after, keys=("id",), schema="id int, value string"):
    previous, pm = shared.source_snapshot_projection(spark.createDataFrame(before, schema), keys)
    current, cm = shared.source_snapshot_projection(spark.createDataFrame(after, schema), keys)
    return shared.compare_source_snapshot_evidence(current, previous, keyed=bool(pm["keys"] and pm["keys"] == cm["keys"]))


@pytest.mark.parametrize("after, expected", [
    ([(101, "Apple"), (102, "Banana"), (103, "Cherry")], (0, 0, 0)),
    ([(101, "Apple"), (102, "Banana"), (103, "Cherry"), (104, "Durian")], (1, 0, 0)),
    ([(101, "Apple"), (102, "Blueberry"), (103, "Cherry")], (0, 1, 0)),
    ([(101, "Apple"), (102, "Banana")], (0, 0, 1)),
    ([(101, "Apple"), (102, "Blueberry"), (104, "Durian")], (1, 1, 1)),
    ([], (0, 0, 3)),
])
def test_exact_historical_counts(spark_session, after, expected):
    result = compare(spark_session, [(101, "Apple"), (102, "Banana"), (103, "Cherry")], after)
    assert tuple(result[k] for k in ("added_count", "modified_count", "removed_count")) == expected
    assert result["ambiguous_count"] == 0


@pytest.mark.parametrize("keys, before, after, expected", [
    ((), [(1, "a")], [(1, "b")], (1, 1)),
    (("missing",), [(1, "a")], [(1, "b")], (1, 1)),
    (("id",), [(None, "a")], [(None, "b")], (1, 1)),
    (("id",), [(1, "a"), (1, "a")], [(1, "a")], (0, 1)),
    ((), [(1, None), (1, None)], [(1, None), (1, None), (2, None)], (1, 0)),
])
def test_ambiguous_identity_preserves_multiplicity(spark_session, keys, before, after, expected):
    result = compare(spark_session, before, after, keys)
    assert (result["added_count"], result["removed_count"]) == expected
    assert result["modified_count"] == 0
    assert result["ambiguous_count"] == expected[1]


def test_nulls_column_order_and_no_raw_samples(spark_session):
    df = spark_session.createDataFrame([(1, None), (2, "sensitive secret")], "id int, value string")
    before, _ = shared.source_snapshot_projection(df, ["id"])
    after, _ = shared.source_snapshot_projection(df.select("value", "id"), ["id"])
    result = shared.compare_source_snapshot_evidence(after, before, keyed=True)
    assert result["modified_count"] == result["removed_count"] == 0
    changed, _ = shared.source_snapshot_projection(df.where("id = 1"), ["id"])
    result = shared.compare_source_snapshot_evidence(changed, before, keyed=True)
    assert "sensitive secret" not in json.dumps(result)
    assert len(result["samples"]["removed"][0]["identity_hash"]) == 64


def test_samples_are_bounded_with_exact_counts(spark_session):
    result = compare(spark_session, [(i, "secret") for i in range(25)], [])
    assert result["removed_count"] == 25
    assert len(result["samples"]["removed"]) == 10
    assert "secret" not in json.dumps(result)


@pytest.fixture
def runtime(spark_session, monkeypatch):
    plan = SimpleNamespace(plan_id="run", pipeline_id="pipeline", workspace_id="workspace", contracts_json="{}",
                           permits_persistence=True, evidence={})
    context = {"execution_plan": plan, "config": object(), "scope_workspace_id": "workspace", "_spark_session": spark_session}
    schema = shared.metadata_table_schema_registry()[shared._PROCESSING_STATE_TABLE]
    state = spark_session.createDataFrame([], schema)
    captured = []
    monkeypatch.setattr(shared, "_source_snapshot_state", lambda context: state)
    monkeypatch.setattr(shared, "build_pipeline_audit_fields", lambda **kw: {"_committed_at": datetime.now(UTC)})
    monkeypatch.setattr(shared, "_persist_source_snapshot", lambda evidence, header, **kw: captured.append((evidence.collect(), header)))
    identity = dict(table_id="source", table_name="orders", store="Bronze", store_type="lakehouse", schema="demo",
                    load_strategy_parameters_json={"key_columns": ["id"]})
    return SimpleNamespace(plan=plan, context=context, identity=identity, captured=captured, schema=schema,
                           set_state=lambda value: None)


def test_first_snapshot_is_only_candidate(runtime, spark_session):
    frame = spark_session.createDataFrame([(1, "a")], "id int, value string")
    result = shared.observe_full_source(runtime.identity, dataframe=frame, context=runtime.context)
    assert result["status"] == "first_observation" and result["historical_checked"] is False
    assert runtime.plan.evidence["source_drift_candidates"]["source"]["status"] == "observed"
    assert runtime.captured[0][1]["record_type"] == "source_snapshot"


def test_corrupt_manifest_is_unavailable(runtime, spark_session, monkeypatch):
    head = dict(record_id="head", record_type="pipeline_source_baseline", status="committed", source_table_id="source",
                observation_id="missing", observed_at=datetime.now(UTC), accepted_at=datetime.now(UTC), workspace_id="workspace", **{f.name: datetime.now(UTC) if f.name == "_committed_at" else "audit" for f in runtime.schema if not f.nullable and f.name.startswith("_")})
    monkeypatch.setattr(shared, "_source_snapshot_state", lambda context: spark_session.createDataFrame([head], runtime.schema))
    with pytest.raises(RuntimeError, match="manifest"):
        shared.observe_full_source(runtime.identity, context=runtime.context)


def test_not_due_does_not_read_physical_source(runtime, spark_session, monkeypatch):
    head = dict(record_id="head", record_type="pipeline_source_baseline", status="committed", source_table_id="source",
                observation_id="accepted", workspace_id="workspace", observed_at=datetime.now(UTC), accepted_at=datetime.now(UTC), **{f.name: datetime.now(UTC) if f.name == "_committed_at" else "audit" for f in runtime.schema if not f.nullable and f.name.startswith("_")})
    monkeypatch.setattr(shared, "_source_snapshot_state", lambda context: spark_session.createDataFrame([head], runtime.schema))
    monkeypatch.setattr(shared, "read_lakehouse_table", lambda *a, **kw: pytest.fail("physical scan"))
    result = shared.observe_full_source(runtime.identity, context=runtime.context, observe_immediately=False, source_observation_days=1)
    assert result["status"] == "skipped" and result["added_count"] is None


def test_first_empty_source_captures_a_complete_empty_candidate(runtime, spark_session):
    frame = spark_session.createDataFrame([], "id int, value string")
    result = shared.observe_full_source(runtime.identity, dataframe=frame, context=runtime.context)
    assert result["status"] == "first_observation"
    assert result["added_count"] == result["removed_count"] == 0
    header = runtime.plan.evidence["source_drift_candidates"]["source"]
    assert json.loads(header["snapshot_payload_json"])["totals"]["rows"] == 0


def test_business_columns_cannot_collide_with_hash_projection_names(spark_session):
    before = spark_session.createDataFrame([(1, "stable", "old")], "id int, _content_hash string, `dotted.value` string")
    after = spark_session.createDataFrame([(1, "stable", "new")], before.schema)
    old, old_meta = shared.source_snapshot_projection(before, ["_content_hash"])
    new, new_meta = shared.source_snapshot_projection(after, ["_content_hash"])
    result = shared.compare_source_snapshot_evidence(new, old, keyed=True)
    assert result["modified_count"] == 1 and result["removed_count"] == result["added_count"] == 0
    assert old_meta["keys"] == new_meta["keys"] == ["_content_hash"]


def test_nested_column_order_does_not_fabricate_historical_changes(spark_session):
    from pyspark.sql import functions as F
    source = spark_session.createDataFrame([(1, "a", 2)], "id int, text string, number int")
    first = source.select("id", F.struct("text", "number").alias("payload"))
    reordered = source.select("id", F.struct("number", "text").alias("payload"))
    previous, _ = shared.source_snapshot_projection(first, ["id"])
    current, _ = shared.source_snapshot_projection(reordered, ["id"])
    result = shared.compare_source_snapshot_evidence(current, previous, keyed=True)
    assert result["ambiguous_count"] == result["modified_count"] == result["removed_count"] == result["added_count"] == 0
