"""Typed file metadata identity, writer and operation-boundary regressions."""
# ruff: noqa: D103, F811
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock
import hashlib
import importlib
import json
import sys

import pytest

from fabricops_kit import setup_pipeline, orchestrate_read, orchestrate_write, finalize_pipeline
from fabricops_kit.data_contract.shared import file_source_identity, current_catalogue_observations
from fabricops_kit.pipeline import shared
from tests.unit.test_pipeline_session import runtime  # noqa: F401
from tests.unit.test_unified_file_read import files  # noqa: F401






def test_file_selector_identity_and_active_catalogue_grain():
    def identity(**kw):
        return file_source_identity(**{**dict(asset_workspace_id="w", item_id="i", relative_path="a/./b.csv", file_format="csv"), **kw})
    source = identity()
    assert source["table_id"] == identity(relative_path="a/b.csv", file_format="json")["table_id"]
    assert len({source["table_id"], identity(asset_workspace_id="other")["table_id"], identity(item_id="other")["table_id"]}) == 3
    rows = [dict(asset_type="FILE", table_id=identity(relative_path=path)["table_id"],
                 asset_workspace_id="w", is_active=True) for path in ("a.csv", "b.csv")]
    rows += [dict(asset_type="TABLE", asset_workspace_id="w", table_id="legacy", is_active=True)]
    assert len(current_catalogue_observations(rows)) == 3
    rows[0]["is_active"] = False
    assert len(current_catalogue_observations(rows)) == 2


@pytest.fixture
def writer(monkeypatch):
    audit = {"_workspace_id": "notebook-workspace", "_activity_id": "fabric-activity", "_notebook_id": "writer-notebook", "_notebook_name": "Writer", "_committed_at": datetime(2026, 1, 1)}
    monkeypatch.setattr(shared, "validate_metadata_merge", Mock())
    spark, merge = Mock(), Mock()
    merge.alias.return_value = merge
    merge.merge.return_value = merge
    merge.whenMatchedUpdate.return_value = merge
    merge.whenNotMatchedInsert.return_value = merge
    frame = Mock()
    frame.alias.return_value = frame
    spark.createDataFrame.return_value = frame
    delta = SimpleNamespace(forPath=Mock(return_value=merge))
    monkeypatch.setitem(sys.modules, "delta.tables", SimpleNamespace(DeltaTable=delta))
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda context=None: ({}, "execution-workspace", {"config": {}, **(context or {})}))
    monkeypatch.setattr(shared, "resolve_asset_workspace_name", lambda *a, **kw: "Physical Workspace")
    monkeypatch.setattr(shared, "build_pipeline_audit_fields", lambda **kw: dict(audit))
    monkeypatch.setattr(shared, "get_spark_session", lambda **kw: spark)
    monkeypatch.setattr(shared, "_require_catalogue_assets", Mock())
    monkeypatch.setattr(shared, "metadata_table_physical_schema", lambda *a: "configured_engineering")
    monkeypatch.setattr(shared, "resolve_configured_lakehouse_table", lambda *a, **kw: (*a, "configured-path"))
    identity = {**file_source_identity(asset_workspace_id="physical", item_id="lakehouse", relative_path="a.csv", file_format="csv"), "store": "Bronze"}
    return SimpleNamespace(spark=spark, merge=merge, delta=delta, identity=identity)




def test_file_catalogue_preserves_first_observation_and_extension_fields(writer):
    shared.persist_file_catalogue(writer.identity, context={})
    row = writer.spark.createDataFrame.call_args.args[0][0]
    assert row["columns_json"] is None
    assert row["table_id"] == writer.identity["table_id"]
    assert row["asset_workspace_id"] == "physical" and row["item_id"] == "lakehouse"
    assert row["first_observed_at"] == row["last_observed_at"]
    updates = writer.merge.whenMatchedUpdate.call_args.kwargs["set"]
    assert updates["first_observed_at"] == "coalesce(target.first_observed_at, source.first_observed_at)"
    assert "extension" not in updates


@pytest.mark.parametrize("mode", ["Dry Run", "Ungoverned"])
def test_multiple_file_reads_persist_before_table_write_and_finalize(files, mode):
    session = setup_pipeline(pipeline_mode=mode)
    first = orchestrate_read(store="Bronze", relative_path="a.csv", file_format="csv")
    second = orchestrate_read(store="Bronze", relative_path="b.csv", file_format="csv")
    expected = 0 if mode == "Dry Run" else 2
    assert files.catalogue.call_count == expected
    source_operations = shared.pipeline_run_row(session.plan, status="incomplete")["operations"]
    assert {op["table_id"] for op in source_operations} == {first["table_id"], second["table_id"]}
    assert all(op["status"] == "succeeded" for op in source_operations)
    orchestrate_write(first["dataframe"], store="Gold", schema="demo", table_name="summary", write_mode="overwrite")
    result = finalize_pipeline(session)
    finalize_pipeline(session)
    assert files.catalogue.call_count == expected
    assert len([op for op in result["operations"] if op.get("asset_type") == "FILE"]) == 2


def test_failed_read_and_metadata_failure_do_not_report_success(files):
    session = setup_pipeline(pipeline_mode="Ungoverned")
    files.catalogue.side_effect = PermissionError("denied")
    with pytest.raises(RuntimeError, match="persistence failed"):
        orchestrate_read(store="Bronze", relative_path="a.csv", file_format="csv")
    assert session.closed
    assert next(iter(session.plan.evidence["operations"].values()))["status"] == "failed"


def test_failed_file_read_does_not_register_success(files):
    session = setup_pipeline(pipeline_mode='Ungoverned')
    files.readers['csv'].side_effect = OSError('unreadable')
    with pytest.raises(RuntimeError, match='unreadable'):
        orchestrate_read(store='Bronze', relative_path='a.csv', file_format='csv')
    assert session.closed
    files.catalogue.assert_not_called()


@pytest.mark.parametrize("metadata_fails", [False, True])
def test_table_source_to_file_target_uses_shared_activity(files, monkeypatch, metadata_fails):
    import importlib
    io = importlib.import_module('fabricops_kit.io')
    monkeypatch.setattr(io, 'write_lakehouse_file', lambda *a, **kw: {
        'published': True, 'publication_status': 'published', 'resolved_path': 'output',
        'write_metrics': {}, 'output_layout': 'single_file', 'overflow_occurred': False, 'overflow_reason': None})
    monkeypatch.setattr(shared, 'schedule_file_profiling', lambda *a, **kw: {'row_count': 2})
    session = setup_pipeline(pipeline_mode='Ungoverned')
    source = orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    if metadata_fails:
        files.catalogue.side_effect = PermissionError('denied')
        with pytest.raises(RuntimeError, match='persistence failed') as caught:
            orchestrate_write(source['dataframe'], store='Gold', relative_path='export.csv', file_format='csv', write_mode='overwrite')
        assert caught.value.published is True and caught.value.failed_stage == 'File metadata'
        assert session.closed
        return
    orchestrate_write(source['dataframe'], store='Gold', relative_path='export.csv', file_format='csv', write_mode='overwrite')
    result = finalize_pipeline(session)
    finalize_pipeline(session)
    sources = [op for op in result['operations'] if op['pipeline_role'] == 'source']
    targets = [op for op in result['operations'] if op['pipeline_role'] == 'target']
    assert len(sources) == len(targets) == 1
    assert sources[0]['table_id'] == 'orders'
    assert targets[0]['asset_type'] == "FILE" and targets[0]['table_id'].startswith('file:')
    assert targets[0]['publication_status'] == 'published'
    assert all(op['status'] == 'succeeded' for op in result['operations'])


def test_retained_profiling_json_does_not_gain_file_fields():
    from fabricops_kit.config.metadata_schemas import decode_metadata_row, coerce_metadata_row_types, encode_metadata_row
    event = {'context_key': 'table', 'activity': 'standard', 'status': 'passed'}
    legacy = decode_metadata_row('METADATA_PIPELINE_RUN', {'profiling': [event]})
    assert 'table_id' not in legacy['profiling'][0] and 'asset_type' not in legacy['profiling'][0]
    assert coerce_metadata_row_types('METADATA_PIPELINE_RUN', legacy) == legacy
    physical = {'profiling': json.dumps([event], indent=2)}
    assert encode_metadata_row('METADATA_PIPELINE_RUN', physical) == physical


def test_profile_consumers_load_file_columns_and_activity_participation(monkeypatch):
    from fabricops_kit.data_contract import shared as contracts
    source_id = 'file:selector'
    from fabricops_kit.config.shared import build_column_id
    column_id = build_column_id(source_id, 'id')
    profile = {'column_name': 'id', 'table_id': source_id, 'column_id': column_id,
        'asset_workspace_id': 'physical', 'profile_id': 'profile', 'profile_snapshot_id': 'snapshot',
        'row_count': 2, '_committed_at': datetime(2026, 1, 1)}
    frequency = {'table_id': source_id, 'column_id': column_id, 'column_name': 'id', 'asset_workspace_id': 'physical',
        'profile_id': 'profile', 'profile_snapshot_id': 'snapshot', 'frequency_rank': 1,
        'value': '1', 'frequency_count': 1, 'frequency_percent': 50.0}
    metadata = {'METADATA_DATA_PROFILED': [profile, {**profile, 'table_id': 'file:other'}],
        'METADATA_DATA_PROFILED_FREQUENCY': [frequency],
        }
    participation = [dict(table_id=source_id, pipeline_role=role, execution_workspace_id='execution',
        pipeline_id='pipeline', run_id='run', operation_status='succeeded', run_status='succeeded',
        _notebook_name='pipeline', operation_completed_at=datetime(2026, 1, 1)) for role in ('source', 'target')]
    monkeypatch.setattr(contracts, 'get_asset_pipeline_participation', lambda **kw: participation)
    monkeypatch.setattr(contracts, 'read_lakehouse_table', lambda name, **kw: metadata[name])
    monkeypatch.setattr(contracts, '_scoped_rows', lambda rows, *filters: rows)
    arguments = dict(config={}, active_workspace_id='physical', spark_session=object(), table_id=source_id)
    column = contracts.get_column_profile_context(**arguments, column_id=column_id)
    assert column['profile'] == profile and column['values'][0]['value'] == '1'
    asset = contracts.get_asset_runtime_context(**arguments)
    assert asset['writer_count'] == asset['reader_count'] == 1
    assert asset['profile_contexts'][column_id] == column
    assert set(asset['column_profiles']) == {column_id}


def test_file_profile_commit_rechecks_persistence_policy():
    plan = SimpleNamespace(execution_mode='dry_run', permits_persistence=False,
        evidence={'pending_file_profiles': {('file:test', 'read'): {}}})
    with pytest.raises(RuntimeError, match='Dry Run cannot commit file profiles'):
        shared._persist_file_profile({'table_id': 'file:test'}, operation='read', context={'execution_plan': plan})


def test_file_catalogue_registers_deterministic_columns(writer):
    from fabricops_kit.config.shared import build_column_id
    shared.persist_file_catalogue(writer.identity, context={}, columns=[
        {"column_name": "id", "data_type": "bigint"}, {"column_name": "name", "data_type": "string"}])
    rows = writer.spark.createDataFrame.call_args.args[0]
    assert len(rows) == 1
    assert rows[0]["table_id"] == writer.identity["table_id"] and rows[0]["asset_type"] == "FILE"
    columns = json.loads(rows[0]["columns_json"])
    assert [row["column_id"] for row in columns] == [
        build_column_id(writer.identity["table_id"], name) for name in ("id", "name")]


@pytest.mark.parametrize('mode', ['Dry Run', 'Ungoverned'])
def test_file_lineage_survives_run_finalization(files, monkeypatch, spark_session, mode):
    """Real Spark file Read ancestry reaches the file Write and its finalized Run."""
    from fabricops_kit.pipeline.shared import column_lineage_rows
    import importlib
    monkeypatch.setattr(shared, 'publish_column_lineage', lambda run, **kw: {'status': 'published', 'row_count': len(shared.column_lineage_rows(run)), 'source_run_sha256': shared._metadata_hash(shared._column_lineage_snapshot(run))})
    incoming = spark_session.createDataFrame([(1, 12)], 'id long, amount long')
    files.readers['csv'].return_value = incoming
    monkeypatch.setattr(importlib.import_module('fabricops_kit.io'), 'write_lakehouse_file', lambda *a, **kw: {
        'published': True, 'publication_status': 'published', 'resolved_path': 'output',
        'write_metrics': {}, 'output_layout': 'single_file', 'overflow_occurred': False, 'overflow_reason': None})
    monkeypatch.setattr(shared, 'schedule_file_profiling', lambda *a, **kw: {'row_count': 1})
    session = setup_pipeline(pipeline_mode=mode)
    source = orchestrate_read(store='Bronze', relative_path='input.csv', file_format='csv')
    orchestrate_write(source['dataframe'].selectExpr('amount * 2 AS total'), store='Gold',
        relative_path='output.csv', file_format='csv', write_mode='overwrite')
    record = finalize_pipeline(session)
    target = next(op for op in record['operations'] if op['pipeline_role'] == 'target')
    assert target['lineage']['status'] == 'complete', target['lineage']
    rows = column_lineage_rows(record)
    assert any(row['source_table_id'] == source['table_id'] and row['source_column_name'] == 'amount'
        and row['target_column_name'] == 'total' and row['dependency_type'] == 'VALUE' for row in rows)
    assert all(row['source_asset_type'] == row['target_asset_type'] == 'FILE' for row in rows)
    assert session.plan.lineage == {}


@pytest.mark.parametrize("mode", ["overwrite", "append_all"])
@pytest.mark.parametrize("schedule_status", ["configured", "not_configured", "unavailable"])
def test_file_catalogue_records_writer_and_reads_preserve_it(writer, monkeypatch, mode, schedule_status):
    schedule = {"status": schedule_status, "schedules": []}
    discover = Mock(return_value=schedule)
    monkeypatch.setattr(shared, "writer_scheduled_refresh", discover)
    shared.persist_file_catalogue(writer.identity, context={}, write_mode=mode)
    row = writer.spark.createDataFrame.call_args.args[0][0]
    assert row["load_strategy"] == mode
    assert row["writer_workspace_id"] == "notebook-workspace"
    assert row["writer_notebook_id"] == "writer-notebook"
    assert row["writer_notebook_name"] == "Writer"
    assert json.loads(row["scheduled_refresh_json"]) == schedule
    assert all(value is None for value in json.loads(row["load_strategy_parameters_json"]).values())
    assert row.get("schema_name") is None
    discover.assert_called_once()
    shared.persist_file_catalogue(writer.identity, context={})
    updates = writer.merge.whenMatchedUpdate.call_args.kwargs["set"]
    assert not set(updates) & {"load_strategy", "load_strategy_parameters_json", "scheduled_refresh_json",
        "writer_workspace_id", "writer_notebook_id", "writer_notebook_name"}
    discover.assert_called_once()


def test_file_read_schema_is_in_catalogue_without_extra_run_payload(files):
    field = SimpleNamespace(name="id", dataType=SimpleNamespace(simpleString=lambda: "int"))
    files.runtime.frame.schema = SimpleNamespace(fields=[field])
    session = setup_pipeline(pipeline_mode="Ungoverned")
    orchestrate_read(store="Bronze", relative_path="a.csv", file_format="csv")
    assert files.catalogue.call_args.kwargs["columns"] == [{"column_name": "id", "data_type": "int"}]
    run = finalize_pipeline(session)
    assert run["operations"][0].get("observed_columns_json") is None


@pytest.mark.parametrize("mode", ["Dry Run", "Ungoverned"])
def test_file_writer_definition_is_forwarded_only_after_publication(files, monkeypatch, mode):
    io = importlib.import_module("fabricops_kit.io")
    monkeypatch.setattr(io, "write_lakehouse_file", lambda *a, **kw: {
        "published": True, "publication_status": "published", "resolved_path": "output", "write_metrics": {}})
    monkeypatch.setattr(shared, "schedule_file_profiling", lambda *a, **kw: {"status": "disabled"})
    session = setup_pipeline(pipeline_mode=mode)
    orchestrate_write(files.runtime.frame, store="Silver", relative_path="a.csv", file_format="csv", write_mode="overwrite")
    if mode == "Dry Run":
        files.catalogue.assert_not_called()
    else:
        assert files.catalogue.call_args.kwargs["write_mode"] == "overwrite"
    finalize_pipeline(session)


@pytest.mark.parametrize("disabled", [False, True])
def test_file_profile_skips_and_failures_use_shared_event_fields(monkeypatch, disabled):
    source_id = "file:test"
    plan = SimpleNamespace(plan_id="run", workspace_id="execution", permits_persistence=True,
        runtime_context={"_pipeline_bindings": {source_id: {
            "asset_workspace_id": "physical", "item_id": "item", "relative_path": "a.csv"}}},
        evidence={"profiling_configuration": {"profiling_enabled": not disabled}})
    build = Mock(side_effect=RuntimeError("calculation failed"))
    monkeypatch.setattr(shared, "build_profile_dataframe", build)
    arguments = dict(source_id=source_id, context={"execution_plan": plan}, presentations=[])
    if disabled:
        assert shared.schedule_file_profiling(object(), **arguments)["status"] == "disabled"
        build.assert_not_called()
    else:
        with pytest.raises(RuntimeError, match="calculation failed"):
            shared.schedule_file_profiling(object(), **arguments)
    events = plan.evidence["profiling"]
    assert all(event["workspace_id"] == "execution" and event["asset_workspace_id"] == "physical"
        and event["physical"]["table_name"] == "a.csv" and event["executed_at"] for event in events)
    assert not any(event["status"] == "passed" for event in events)
    assert {event["activity"] for event in events if event["status"] == "skipped"} == (
        {"standard", "grain", "frequency"} if disabled else {"grain", "frequency"})
    if not disabled:
        assert events[-1]["status"] == "failed" and events[-1]["reason"] == "RuntimeError"


def test_failed_file_profile_persistence_does_not_mark_catalogue_complete(monkeypatch):
    source_id = "file:test"
    pending = {"profile": Mock(), "frequency": None, "activities": ["standard"],
        "scope": {}, "result": {"row_count": 1, "results_persisted": False}, "executed_at": "start"}
    plan = SimpleNamespace(plan_id="run", workspace_id="execution", execution_mode="ungoverned",
        permits_persistence=True, runtime_context={},
        evidence={"pending_file_profiles": {(source_id, "read"): pending}})
    monkeypatch.setattr(shared, "_canonical_profiled_dataframe", Mock())
    monkeypatch.setattr(shared, "_require_catalogue_assets", Mock())
    monkeypatch.setattr(shared, "_replace_snapshot_rows", Mock(side_effect=RuntimeError("write failed")))
    marker = Mock()
    monkeypatch.setattr(shared, "merge_catalogue_asset", marker)
    with pytest.raises(RuntimeError, match="write failed"):
        shared._persist_file_profile({"table_id": source_id, "asset_workspace_id": "physical", "relative_path": "a.csv"},
            operation="read", context={"execution_plan": plan, "config": {}})
    marker.assert_not_called()
    assert pending["result"]["results_persisted"] is False
    assert plan.evidence["profiling"][-1]["status"] == "failed"
    assert not plan.evidence.get("file_profiles")
