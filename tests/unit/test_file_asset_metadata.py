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


def test_released_table_hash_and_typed_file_identity():
    values = {"activity_id": "activity", "table_id": "orders", "pipeline_role": "source"}
    released = hashlib.sha256(json.dumps(values, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert shared.lineage_id(**values) == released
    first = shared.lineage_id(activity_id="activity", asset_type="FILE", table_id="orders", pipeline_role="source")
    assert first != released
    assert first != shared.lineage_id(activity_id="other", asset_type="FILE", table_id="orders", pipeline_role="source")
    assert first != shared.lineage_id(activity_id="activity", asset_type="FILE", table_id="orders", pipeline_role="target")
    assert first == shared.lineage_id(activity_id="activity", asset_type="FILE", table_id="orders", pipeline_role="source")


@pytest.mark.parametrize("ids", [dict(table_id=""), dict(asset_type="OTHER", table_id="t")])
def test_lineage_rejects_invalid_identity(ids):
    with pytest.raises(ValueError, match="canonical table_id"):
        shared.lineage_id(activity_id="a", pipeline_role="source", **ids)


def test_file_selector_identity_and_active_catalogue_grain():
    def identity(**kw):
        return file_source_identity(**{**dict(workspace_id="w", item_id="i", relative_path="a/./b.csv", file_format="csv"), **kw})
    source = identity()
    assert source["source_id"] == identity(relative_path="a/b.csv", file_format="json")["source_id"]
    assert len({source["source_id"], identity(workspace_id="other")["source_id"], identity(item_id="other")["source_id"]}) == 3
    rows = [dict(asset_type="FILE", table_id=identity(relative_path=path)["source_id"],
                 metadata_level="file", workspace_id="w", is_active=True) for path in ("a.csv", "b.csv")]
    rows += [dict(metadata_level="table", workspace_id="w", table_id="legacy", is_active=True)]
    assert len(current_catalogue_observations(rows)) == 3
    rows[0]["is_active"] = False
    assert len(current_catalogue_observations(rows)) == 2


@pytest.fixture
def writer(monkeypatch):
    audit = {"_activity_id": "fabric-activity", "_committed_at": datetime(2026, 1, 1)}
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
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda context=None: ({}, "execution-workspace", context or {}))
    monkeypatch.setattr(shared, "build_pipeline_audit_fields", lambda **kw: dict(audit))
    monkeypatch.setattr(shared, "get_spark_session", lambda **kw: spark)
    monkeypatch.setattr(shared, "metadata_table_physical_schema", lambda *a: "configured_engineering")
    monkeypatch.setattr(shared, "resolve_configured_lakehouse_table", lambda *a, **kw: (*a, "configured-path"))
    identity = {**file_source_identity(workspace_id="physical", item_id="lakehouse", relative_path="a.csv", file_format="csv"), "store": "Bronze"}
    return SimpleNamespace(spark=spark, merge=merge, delta=delta, identity=identity)


@pytest.mark.parametrize("role", ["source", "target"])
def test_file_lineage_writer_has_exact_identity_and_activity(writer, role):
    source = writer.identity
    identifier = shared.persist_lineage_participation(asset_type="FILE", table_id=source["source_id"],
        file_identity=source, pipeline_role=role, context={})
    row = writer.spark.createDataFrame.call_args.args[0][0]
    assert row["lineage_id"] == identifier
    assert row["table_id"] == source["source_id"] and row["table_name"] == "a.csv"
    assert "source_id" not in row and row["asset_type"] == "FILE"
    assert row["_activity_id"] == "fabric-activity" and row["asset_name"] == "Bronze/Files/a.csv"
    assert writer.delta.forPath.call_args.args[1] == "configured-path"
    assert "lineage_id" in writer.merge.merge.call_args.args[1]


def test_file_catalogue_preserves_first_observation_and_extension_fields(writer):
    shared.persist_file_catalogue(writer.identity, context={})
    row = writer.spark.createDataFrame.call_args.args[0][0]
    assert row["column_id"] is None
    assert row["table_id"] == writer.identity["source_id"]
    assert row["workspace_id"] == "physical" and row["item_id"] == "lakehouse"
    assert row["first_observed_at"] == row["last_observed_at"]
    updates = writer.merge.whenMatchedUpdate.call_args.kwargs["set"]
    assert "first_observed_at" not in updates and "extension" not in updates


@pytest.mark.parametrize("mode", ["Dry Run", "Ungoverned"])
def test_multiple_file_reads_persist_before_table_write_and_finalize(files, mode):
    session = setup_pipeline(pipeline_mode=mode)
    first = orchestrate_read(store="Bronze", relative_path="a.csv", file_format="csv")
    second = orchestrate_read(store="Bronze", relative_path="b.csv", file_format="csv")
    expected = 0 if mode == "Dry Run" else 2
    assert files.lineage.call_count == files.catalogue.call_count == expected
    if expected:
        assert {call.kwargs["table_id"] for call in files.lineage.call_args_list} == {first["source_id"], second["source_id"]}
        assert all(call.kwargs["context"]["execution_plan"].plan_id == session.plan.plan_id for call in files.lineage.call_args_list)
    orchestrate_write(first["dataframe"], store="Gold", schema="demo", table_name="summary", write_mode="overwrite")
    result = finalize_pipeline(session)
    finalize_pipeline(session)
    assert files.lineage.call_count == expected
    assert len([op for op in result["operations"] if op.get("source_id")]) == 2


def test_failed_read_and_metadata_failure_do_not_report_success(files):
    session = setup_pipeline(pipeline_mode="Ungoverned")
    files.catalogue.side_effect = PermissionError("denied")
    with pytest.raises(RuntimeError, match="persistence failed"):
        orchestrate_read(store="Bronze", relative_path="a.csv", file_format="csv")
    assert session.closed
    assert next(iter(session.plan.evidence["operations"].values()))["status"] == "failed"
    files.lineage.assert_not_called()


def test_failed_file_read_does_not_register_success(files):
    session = setup_pipeline(pipeline_mode='Ungoverned')
    files.readers['csv'].side_effect = OSError('unreadable')
    with pytest.raises(RuntimeError, match='unreadable'):
        orchestrate_read(store='Bronze', relative_path='a.csv', file_format='csv')
    assert session.closed
    files.catalogue.assert_not_called()
    files.lineage.assert_not_called()


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
        files.lineage.assert_not_called()
        return
    orchestrate_write(source['dataframe'], store='Gold', relative_path='export.csv', file_format='csv', write_mode='overwrite')
    calls = [call.kwargs for call in files.lineage.call_args_list]
    assert len(calls) == 2
    assert calls[0]['asset_type'] == 'FILE' and calls[0]['pipeline_role'] == 'target'
    assert calls[1]['table_id'] == 'orders' and calls[1]['pipeline_role'] == 'source'
    assert calls[0]['context'] is calls[1]['context']
    finalize_pipeline(session)
    finalize_pipeline(session)
    assert files.lineage.call_count == 2


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
        'METADATA_DATA_LINEAGE': [dict(table_id=source_id, pipeline_role=role, workspace_id='execution',
            _notebook_name='pipeline', _committed_at=datetime(2026, 1, 1)) for role in ('source', 'target')]}
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
    writer.merge.whenNotMatchedBySourceUpdate.return_value = writer.merge
    shared.persist_file_catalogue(writer.identity, context={}, columns=[
        {'column_name': 'id', 'data_type': 'bigint'}, {'column_name': 'name', 'data_type': 'string'}])
    rows = writer.spark.createDataFrame.call_args.args[0]
    assert len(rows) == 3
    assert {row['metadata_level'] for row in rows} == {'file', 'column'}
    assert all(row['table_id'] == writer.identity['source_id'] and row['asset_type'] == 'FILE' for row in rows)
    assert rows[1]['column_id'] == build_column_id(writer.identity['source_id'], 'id')
    assert rows[2]['column_id'] == build_column_id(writer.identity['source_id'], 'name')
    writer.merge.whenNotMatchedBySourceUpdate.assert_called_once()
