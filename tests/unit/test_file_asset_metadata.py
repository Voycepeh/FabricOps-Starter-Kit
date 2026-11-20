"""Typed file metadata identity, writer and operation-boundary regressions."""
# ruff: noqa: D103, F811
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock
import hashlib
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
        return file_source_identity(**{**dict(workspace_id="w", item_id="i", relative_path="a/./b.csv", file_format="csv"), **kw})
    source = identity()
    assert source["source_id"] == identity(relative_path="a/b.csv", file_format="json")["source_id"]
    assert len({source["source_id"], identity(workspace_id="other")["source_id"], identity(item_id="other")["source_id"]}) == 3
    rows = [dict(asset_type="FILE", table_id=identity(relative_path=path)["source_id"],
                 workspace_id="w", is_active=True) for path in ("a.csv", "b.csv")]
    rows += [dict(asset_type="TABLE", workspace_id="w", table_id="legacy", is_active=True)]
    assert len(current_catalogue_observations(rows)) == 3
    rows[0]["is_active"] = False
    assert len(current_catalogue_observations(rows)) == 2


@pytest.fixture
def writer(monkeypatch):
    audit = {"_workspace_id": "notebook-workspace", "_activity_id": "fabric-activity", "_committed_at": datetime(2026, 1, 1)}
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
    identity = {**file_source_identity(workspace_id="physical", item_id="lakehouse", relative_path="a.csv", file_format="csv"), "store": "Bronze"}
    return SimpleNamespace(spark=spark, merge=merge, delta=delta, identity=identity)




def test_file_catalogue_preserves_first_observation_and_extension_fields(writer):
    shared.persist_file_catalogue(writer.identity, context={})
    row = writer.spark.createDataFrame.call_args.args[0][0]
    assert row["columns_json"] is None
    assert row["table_id"] == writer.identity["source_id"]
    assert row["workspace_id"] == "physical" and row["item_id"] == "lakehouse"
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
    assert {op["source_id"] for op in source_operations} == {first["source_id"], second["source_id"]}
    assert all(op["status"] == "succeeded" for op in source_operations)
    orchestrate_write(first["dataframe"], store="Gold", schema="demo", table_name="summary", write_mode="overwrite")
    result = finalize_pipeline(session)
    finalize_pipeline(session)
    assert files.catalogue.call_count == expected
    assert len([op for op in result["operations"] if op.get("source_id")]) == 2


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
    assert targets[0]['source_type'] == 'file' and targets[0]['source_id'].startswith('file:')
    assert targets[0]['publication_status'] == 'published'
    assert all(op['status'] == 'succeeded' for op in result['operations'])


def test_retained_profiling_json_does_not_gain_file_fields():
    from fabricops_kit.config.metadata_schemas import decode_metadata_row, coerce_metadata_row_types, encode_metadata_row
    event = {'context_key': 'table', 'activity': 'standard', 'status': 'passed'}
    legacy = decode_metadata_row('METADATA_PIPELINE_RUN', {'profiling': [event]})
    assert 'source_id' not in legacy['profiling'][0] and 'asset_type' not in legacy['profiling'][0]
    assert coerce_metadata_row_types('METADATA_PIPELINE_RUN', legacy) == legacy
    physical = {'profiling': json.dumps([event], indent=2)}
    assert encode_metadata_row('METADATA_PIPELINE_RUN', physical) == physical


def test_profile_consumers_load_file_columns_and_activity_participation(monkeypatch):
    from fabricops_kit.data_contract import shared as contracts
    source_id = 'file:selector'
    from fabricops_kit.config.shared import build_column_id
    column_id = build_column_id(source_id, 'id')
    profile = {'column_name': 'id', 'table_id': source_id, 'column_id': column_id,
        'workspace_id': 'physical', 'profile_id': 'profile', 'profile_snapshot_id': 'snapshot',
        'row_count': 2, '_committed_at': datetime(2026, 1, 1)}
    frequency = {'table_id': source_id, 'column_id': column_id, 'column_name': 'id', 'workspace_id': 'physical',
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
        shared._persist_file_profile({'source_id': 'file:test'}, operation='read', context={'execution_plan': plan})


def test_file_catalogue_registers_deterministic_columns(writer):
    from fabricops_kit.config.shared import build_column_id
    shared.persist_file_catalogue(writer.identity, context={}, columns=[
        {"column_name": "id", "data_type": "bigint"}, {"column_name": "name", "data_type": "string"}])
    rows = writer.spark.createDataFrame.call_args.args[0]
    assert len(rows) == 1
    assert rows[0]["table_id"] == writer.identity["source_id"] and rows[0]["asset_type"] == "FILE"
    columns = json.loads(rows[0]["columns_json"])
    assert [row["column_id"] for row in columns] == [
        build_column_id(writer.identity["source_id"], name) for name in ("id", "name")]
