"""Real Delta completeness, shared history and conditional source-head acceptance."""
# ruff: noqa: D103
import json
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fabricops_kit.pipeline import shared

pytestmark = pytest.mark.spark


@pytest.fixture
def snapshots(spark_session, monkeypatch, tmp_path):
    pytest.importorskip('delta.tables')
    if 'DeltaSparkSessionExtension' not in spark_session.conf.get('spark.sql.extensions', ''):
        pytest.skip('requires Delta Spark extensions')
    spark_session.conf.set("spark.databricks.delta.snapshotPartitions", "2")
    schema = shared.metadata_table_schema_registry()[shared._PROCESSING_STATE_TABLE]
    path = str(tmp_path / 'configured-metadata' / 'engineering' / 'state')
    spark_session.createDataFrame([], schema).write.format('delta').option('delta.isolationLevel', 'Serializable').save(path)
    sources = {'orders': spark_session.createDataFrame([(1, 'a'), (2, 'b'), (3, 'c')], 'id int, value string')}
    def read(table, **kwargs):
        return spark_session.read.format('delta').load(path) if table == shared._PROCESSING_STATE_TABLE else sources[table]
    def write(frame, table, **kwargs):
        assert table == shared._PROCESSING_STATE_TABLE and kwargs['store'] == 'Metadata' and kwargs['schema'] == 'engineering'
        frame.write.format('delta').mode(kwargs['mode']).options(**(kwargs.get('options') or {})).save(path)
    monkeypatch.setattr(shared, 'read_lakehouse_table', read)
    warehouse = Mock(side_effect=lambda schema, table, **kw: sources[table])
    monkeypatch.setattr(__import__('fabricops_kit.io', fromlist=['read_warehouse_table']), 'read_warehouse_table', warehouse)
    monkeypatch.setattr(shared, 'write_lakehouse_table', write)
    monkeypatch.setattr(shared, 'metadata_table_physical_schema', lambda *a: 'engineering')
    monkeypatch.setattr(shared, 'resolve_configured_lakehouse_table', lambda *a, **kw: (None, None, None, path))
    monkeypatch.setattr(shared, 'pipeline_physical_bindings', lambda identities, config, workspace_id: {
        tid: {'workspace_id': config.get('physical_workspace', 'physical'), 'item_id': config.get('item', 'house'),
            'kind': identity['store_type'], 'schema': identity['schema'], 'table_name': identity['table_name']}
        for tid, identity in identities.items()})
    audit = {field.name: datetime.now(UTC) if field.name == '_committed_at' else 'audit'
        for field in schema if field.name.startswith('_')}
    monkeypatch.setattr(shared, 'build_pipeline_audit_fields', lambda **kw: audit)
    diagnostics = Mock()
    monkeypatch.setattr(shared, '_record_source_drift_result', diagnostics)
    def run(run_id='run', pipeline='pipeline', workspace='workspace', config=None, kind='lakehouse', interval=1, keys=('id',)):
        identity = dict(table_id='orders-id', table_name='orders', store='Bronze', schema='demo', store_type=kind,
            roles=['source'], load_strategy_parameters_json={'key_columns': list(keys)})
        runtime = {'config': config or {}, 'scope_workspace_id': workspace, '_spark_session': spark_session}
        plan = SimpleNamespace(plan_id=run_id, pipeline_id=pipeline, workspace_id=workspace, permits_persistence=True,
            contracts_json='{}', participants_json=json.dumps({'orders-id': identity}), runtime_context=runtime,
            evidence={'source_drift_policy': shared.validate_source_drift_configuration({
                'source_drift_enabled': True, 'source_drift_interval_days': interval}), 'profiling_configuration': {'profiling_max_rows': 1},
                'operations': {}, 'source_drift_decision': {'can_continue': True},
                'final_result': {'status': 'ungoverned_completed', 'boundary_completed': True}})
        return plan, {**runtime, 'execution_plan': plan}, identity
    return SimpleNamespace(run=run, state=lambda: read(shared._PROCESSING_STATE_TABLE), sources=sources,
        warehouse=warehouse, spark=spark_session, path=path, diagnostics=diagnostics)


def expire(snapshots):
    from delta.tables import DeltaTable
    from pyspark.sql import functions as F
    DeltaTable.forPath(snapshots.spark, snapshots.path).update("record_type = 'source_drift_baseline'",
        {'accepted_at': F.lit(datetime.now(UTC) - timedelta(days=2))})


@pytest.mark.parametrize('kind', ['lakehouse', 'warehouse'])
def test_complete_source_first_baseline_shared_schedule_and_exact_changes(snapshots, kind):
    rt = snapshots
    plan, context, identity = rt.run(kind=kind)
    first = shared.observe_full_source(identity, context=context)
    assert first['status'] == 'baseline_pending' and first['added_count'] is None and first['row_count'] == 3
    assert rt.state().where("record_type = 'source_drift_baseline'").count() == 0
    shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
    shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
    assert rt.state().where("record_type = 'source_snapshot_acceptance'").count() == 1
    other, other_context, other_identity = rt.run('other', pipeline='another-pipeline', kind=kind)
    assert shared.observe_full_source(other_identity, context=other_context)['status'] == 'not_due'
    expire(rt)
    rt.sources['orders'] = rt.spark.createDataFrame([(1, 'a'), (2, 'changed'), (4, 'd')], 'id int, value string')
    second, second_context, second_identity = rt.run('second', pipeline='second-pipeline', kind=kind)
    changed = shared.observe_full_source(second_identity, context=second_context)
    assert (changed['added_count'], changed['removed_count'], changed['modified_count']) == (1, 1, 1)
    assert changed['status'] == 'changes_detected' and changed['row_count'] == 3  # Profiling cap=1 never restricts observation.
    assert rt.state().where("record_type = 'source_drift_baseline'").first()['run_id'] == 'run'
    assert 'profiling' not in second.evidence
    if kind == 'warehouse':
        assert rt.warehouse.call_args.args == ('demo', 'orders')


def test_dry_run_diagnostics_never_persist_or_consume_history(snapshots):
    rt = snapshots
    plan, context, identity = rt.run()
    plan.permits_persistence = False
    result = shared.observe_full_source(identity, context=context)
    assert result['status'] == 'baseline_pending' and result['row_count'] == 3
    assert rt.state().count() == 0
    shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
    assert rt.state().count() == 0


@pytest.mark.parametrize('workspace,config', [('other', {}), ('workspace', {'item': 'other'}),
    ('workspace', {'physical_workspace': 'other'})])
def test_physical_source_history_is_isolated(snapshots, workspace, config):
    rt = snapshots
    plan, context, identity = rt.run()
    shared.observe_full_source(identity, context=context)
    shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
    other, other_context, other_identity = rt.run('other', workspace=workspace, config=config)
    assert shared.observe_full_source(other_identity, context=other_context)['status'] == 'baseline_pending'


def test_each_pipeline_uses_its_interval_against_confirmed_completion(snapshots):
    rt = snapshots
    plan, context, identity = rt.run()
    shared.observe_full_source(identity, context=context)
    shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
    expire(rt)
    slow, slow_context, slow_identity = rt.run('weekly', pipeline='weekly', interval=7)
    assert shared.observe_full_source(slow_identity, context=slow_context)['status'] == 'not_due'
    fast, fast_context, fast_identity = rt.run('daily', pipeline='daily')
    assert shared.observe_full_source(fast_identity, context=fast_context)['status'] == 'no_change'


def test_stale_concurrent_acceptance_cannot_overwrite_winner(snapshots):
    rt = snapshots
    older, old_context, identity = rt.run('older', pipeline='A')
    winner, winner_context, _ = rt.run('winner', pipeline='B')
    shared.observe_full_source(identity, context=old_context)
    shared.observe_full_source(identity, context=winner_context)
    shared.accept_pipeline_source_snapshots(winner, spark_session=rt.spark)
    with pytest.raises(Exception, match='baseline advanced concurrently'):
        shared.accept_pipeline_source_snapshots(older, spark_session=rt.spark)
    assert rt.state().where("record_type = 'source_drift_baseline'").first()['run_id'] == 'winner'
    assert rt.state().where("record_type = 'source_snapshot_acceptance'").count() == 1


def test_incomplete_candidate_is_never_accepted(snapshots):
    from delta.tables import DeltaTable
    rt = snapshots
    plan, context, identity = rt.run()
    shared.observe_full_source(identity, context=context)
    DeltaTable.forPath(rt.spark, rt.path).delete("record_type = 'source_row_evidence'")
    with pytest.raises(RuntimeError, match='corrupt or incomplete'):
        shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
    assert rt.state().where("record_type = 'source_drift_baseline'").count() == 0


def test_nonpublishing_write_cannot_accept_source_history(snapshots):
    rt = snapshots
    plan, context, identity = rt.run()
    shared.observe_full_source(identity, context=context)
    identities = json.loads(plan.participants_json)
    identities['target'] = {**identity, 'roles': ['target']}
    plan.participants_json = json.dumps(identities)
    plan.evidence['publication_outcomes'] = {'target': {'status': 'no_unseen_hashes', 'receipt': None}}
    shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
    assert plan.evidence['source_snapshot_acceptance']['status'] == 'not_eligible'
    assert rt.state().where("record_type = 'source_drift_baseline'").count() == 0


def test_stale_parent_rolls_back_all_source_heads_atomically(snapshots):
    rt = snapshots
    older, context, identity = rt.run('multi-source')
    other_identity = {**identity, 'table_id': 'customers-id', 'table_name': 'customers'}
    rt.sources['customers'] = rt.sources['orders']
    older.participants_json = json.dumps({'orders-id': identity, 'customers-id': other_identity})
    shared.observe_full_source(identity, context=context)
    shared.observe_full_source(other_identity, context=context)
    winner, winning_context, _ = rt.run('winner')
    shared.observe_full_source(identity, context=winning_context)
    shared.accept_pipeline_source_snapshots(winner, spark_session=rt.spark)
    with pytest.raises(Exception, match='baseline advanced concurrently'):
        shared.accept_pipeline_source_snapshots(older, spark_session=rt.spark)
    heads = rt.state().where("record_type = 'source_drift_baseline'").collect()
    assert [(row.source_table_id, row.run_id) for row in heads] == [('orders-id', 'winner')]
    assert rt.state().where("record_type = 'source_snapshot_acceptance'").count() == 1


def test_empty_source_can_establish_a_verified_empty_baseline(snapshots):
    rt = snapshots
    rt.sources['orders'] = rt.sources['orders'].limit(0)
    plan, context, identity = rt.run()
    result = shared.observe_full_source(identity, context=context)
    assert result['row_count'] == 0 and result['added_count'] is None
    shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
    assert rt.state().where("record_type = 'source_drift_baseline'").first().row_count == 0


@pytest.mark.parametrize('mode', ['overwrite', 'append_all', 'append_new_only', 'scd1', 'scd2'])
def test_every_required_target_requires_physical_confirmation(snapshots, monkeypatch, mode):
    rt = snapshots
    plan, context, identity = rt.run()
    shared.observe_full_source(identity, context=context)
    plan.participants_json = json.dumps({'orders-id': identity, 'a': {**identity, 'roles': ['target']},
        'b': {**identity, 'roles': ['target']}})
    plan.evidence['publication_outcomes'] = {tid: {'status': 'committed', 'receipt': {'strategy': mode, 'target': tid, 'run_id': plan.plan_id}}
        for tid in ['a', 'b']}
    verify = Mock(side_effect=[True, False])
    monkeypatch.setattr(shared, '_physical_target_has_publication', verify)
    with pytest.raises(RuntimeError, match='publications must be confirmed'):
        shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
    assert rt.state().where("record_type = 'source_drift_baseline'").count() == 0
    verify.side_effect = [True, True]
    shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
    assert rt.state().where("record_type = 'source_drift_baseline'").count() == 1


@pytest.mark.parametrize('verification_available', [True, False])
def test_committed_acceptance_with_lost_acknowledgement_is_not_reported_as_rollback(snapshots, monkeypatch, verification_available):
    rt = snapshots
    plan, context, identity = rt.run()
    shared.observe_full_source(identity, context=context)
    retry = shared.retry_delta_metadata
    def lose_acknowledgement(operation):
        retry(operation)
        if not verification_available:
            monkeypatch.setattr(shared, '_source_snapshot_state', Mock(side_effect=OSError('read-back unavailable')))
        raise OSError('acknowledgement lost')
    monkeypatch.setattr(shared, 'retry_delta_metadata', lose_acknowledgement)
    if verification_available:
        shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
        assert plan.evidence['source_snapshot_acceptance']['status'] == 'accepted'
    else:
        with pytest.raises(RuntimeError, match='outcome is unknown') as raised:
            shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
        assert raised.value.outcome_unknown is True
    assert rt.state().where("record_type = 'source_snapshot_acceptance'").count() == 1
    assert rt.state().where("record_type = 'source_drift_baseline'").count() == 1


def test_prior_execution_publication_cannot_accept_new_source_snapshot(snapshots, monkeypatch):
    rt = snapshots
    plan, context, identity = rt.run('new-execution')
    shared.observe_full_source(identity, context=context)
    plan.participants_json = json.dumps({'orders-id': identity, 'target': {**identity, 'roles': ['target']}})
    plan.evidence['publication_outcomes'] = {'target': {'status': 'committed',
        'receipt': {'run_id': 'original-publication', 'strategy': 'append_new_only'}}}
    verify = Mock(return_value=True)
    monkeypatch.setattr(shared, '_physical_target_has_publication', verify)
    shared.accept_pipeline_source_snapshots(plan, spark_session=rt.spark)
    verify.assert_not_called()
    assert plan.evidence['source_snapshot_acceptance']['status'] == 'not_eligible'
    assert rt.state().where("record_type = 'source_drift_baseline'").count() == 0
