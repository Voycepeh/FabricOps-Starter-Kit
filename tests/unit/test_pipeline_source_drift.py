"""Automatic multi-source decisions and publication/finalization boundaries."""
# ruff: noqa: D103, F811
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fabricops_kit import setup_pipeline, orchestrate_read, orchestrate_write, finalize_pipeline
from fabricops_kit.pipeline import shared
from tests.unit.test_pipeline_session import runtime


def result(status='no_change', **values):
    return {'status': status, 'can_continue': True, 'changed': status == 'changes_detected',
        'added_count': 0, 'removed_count': 0,
        'modified_count': 1 if status == 'changes_detected' else 0, 'ambiguous_count': 0, **values}


@pytest.mark.parametrize('block', [True, False])
def test_all_sources_are_decided_before_any_write_and_late_reads_are_rejected(runtime, monkeypatch, block):
    session = setup_pipeline(source_drift_enabled=True, source_drift_block=block)
    observed = session.plan.evidence.setdefault('source_drift_observations', {})
    def read(**kwargs):
        tid = kwargs['table_name']
        observed[tid] = {**result('changes_detected' if tid == 'bad' else 'no_change'), 'table_id': tid}
        return {'table_id': tid, 'dataframe': runtime.frame}
    monkeypatch.setattr(runtime.read, 'pipeline_read', read)
    monkeypatch.setattr(shared, '_record_source_drift_result', Mock())
    orchestrate_read(store='Bronze', schema='demo', table_name='bad', verbose=False)
    orchestrate_read(store='Bronze', schema='demo', table_name='good', verbose=False)
    assert len(session.sources) == 2 and not runtime.publication.called
    if block:
        with pytest.raises(RuntimeError, match='Source Drift blocks publication'):
            orchestrate_write(runtime.frame, store='Silver', schema='demo', table_name='target', write_mode='overwrite', verbose=False)
        runtime.publication.assert_not_called()
    else:
        orchestrate_write(runtime.frame, store='Silver', schema='demo', table_name='target', write_mode='overwrite', verbose=False)
        assert set(session.plan.evidence['source_drift_decision']['source_ids']) == {'good', 'bad'}
        with pytest.raises(RuntimeError, match='all Reads before any Write'):
            orchestrate_read(store='Bronze', schema='demo', table_name='late', verbose=False)
        assert session.plan.evidence['final_result']['status'] == 'failed'


@pytest.mark.parametrize('block', [True, False])
def test_unavailable_observation_prevents_partial_baseline_acceptance(runtime, monkeypatch, block):
    session = setup_pipeline(source_drift_enabled=True, source_drift_block=block)
    monkeypatch.setattr(shared, '_record_source_drift_result', Mock())
    for tid in ['healthy', 'failed']:
        orchestrate_read(store='Bronze', schema='demo', table_name=tid, verbose=False)
    session.plan.evidence['source_drift_observations'] = {
        'healthy': result(table_id='healthy'), 'failed': result('observation_failed', table_id='failed')}
    session.plan.evidence['source_drift_candidates'] = {'healthy': {'observation_id': 'candidate'}}
    if block:
        with pytest.raises(RuntimeError):
            orchestrate_write(runtime.frame, store='Silver', schema='demo', table_name='target', write_mode='overwrite', verbose=False)
        runtime.publication.assert_not_called()
    else:
        orchestrate_write(runtime.frame, store='Silver', schema='demo', table_name='target', write_mode='overwrite', verbose=False)
    assert not session.plan.evidence['source_drift_candidates']


def test_disabled_source_drift_never_reads_or_persists_observation_state(runtime, monkeypatch):
    session = setup_pipeline(profiling_max_rows=1)
    scan = Mock(side_effect=AssertionError('unexpected Source Drift scan'))
    monkeypatch.setattr(shared, '_source_snapshot_state', scan)
    assert shared.observe_full_source({}, context={'execution_plan': session.plan})['status'] == 'disabled'
    assert shared.evaluate_pipeline_source_drift(session.plan)['status'] == 'disabled'
    scan.assert_not_called()


@pytest.mark.parametrize('status', ['failed', 'incomplete'])
def test_baseline_acceptance_requires_successful_lifecycle_status(status):
    plan = SimpleNamespace(permits_persistence=True, evidence={'source_drift_candidates': {'s': {}},
        'final_result': {'status': status, 'boundary_completed': False}, 'source_drift_decision': {'can_continue': True}},
        participants_json=json.dumps({'t': {'roles': ['target'], 'store_type': 'lakehouse'}}), runtime_context={})
    # The gate runs before any physical/Delta mutation.
    if status != 'ungoverned_completed':
        with pytest.raises(RuntimeError, match='whole-run finalization'):
            shared.accept_pipeline_source_snapshots(plan)


@pytest.mark.parametrize('mode', ['overwrite', 'append_all', 'append_new_only', 'scd1', 'scd2'])
@pytest.mark.parametrize('second_fails', [True, False])
def test_multi_target_baselines_wait_for_whole_run_finalization(runtime, monkeypatch, mode, second_fails):
    session = setup_pipeline(source_drift_enabled=True, source_drift_block=False)
    monkeypatch.setattr(shared, '_record_source_drift_result', Mock())
    accept = Mock()
    monkeypatch.setattr(shared, 'accept_pipeline_source_snapshots', accept)
    for tid in ['orders', 'products']:
        orchestrate_read(store='Bronze', schema='demo', table_name=tid, verbose=False)
    session.plan.evidence['source_drift_observations'] = {tid: result('changes_detected', table_id=tid) for tid in ['orders', 'products']}
    session.plan.evidence['source_drift_candidates'] = {tid: {'observation_id': tid} for tid in ['orders', 'products']}
    runtime.publication.return_value = {'published': True, 'table_id': 'first', 'status': 'passed'}
    parameters = {'key_columns': ['id']} if mode in {'scd1', 'scd2'} else None
    if mode == 'scd2':
        parameters['effective_column'] = 'id'
    orchestrate_write(runtime.frame, store='Silver', schema='demo', table_name='first', write_mode=mode,
        write_parameters=parameters, verbose=False)
    accept.assert_not_called()
    if second_fails:
        runtime.publication.side_effect = RuntimeError('second publication failed')
        with pytest.raises(RuntimeError, match='second publication failed'):
            orchestrate_write(runtime.frame, store='Silver', schema='demo', table_name='second', write_mode=mode,
                write_parameters=parameters, verbose=False)
        assert session.plan.evidence['final_result']['status'] == 'failed'
        accept.assert_not_called()
    else:
        orchestrate_write(runtime.frame, store='Silver', schema='demo', table_name='second', write_mode=mode,
            write_parameters=parameters, verbose=False)
        accept.assert_not_called()
        summary = finalize_pipeline(session)
        assert summary['status'] == 'ungoverned_completed'
        accept.assert_called_once_with(session.plan, spark_session=runtime.spark)


@pytest.mark.parametrize('block', [True, False])
def test_declared_unread_source_blocks_even_warning_mode(monkeypatch, block):
    plan = SimpleNamespace(workspace_id='dev', pipeline_id='pipeline', plan_id='run', runtime_context={'config': {}},
        participants_json=json.dumps({'unread': {'roles': ['source']}}), evidence={
            'source_drift_policy': shared.validate_source_drift_configuration({'source_drift_enabled': True, 'source_drift_block': block}),
            'source_drift_candidates': {'healthy': {}}})
    monkeypatch.setattr(shared, '_record_source_drift_result', Mock())
    with pytest.raises(RuntimeError, match='Source Drift blocks publication'):
        shared.evaluate_pipeline_source_drift(plan)
    assert plan.evidence['source_drift_decision']['missing_source_ids'] == ['unread']
    assert plan.evidence['source_drift_candidates'] == {}


@pytest.mark.parametrize('unknown', [True, False])
def test_finalization_reports_acceptance_failure_separately_from_committed_run(runtime, monkeypatch, unknown):
    session = setup_pipeline(source_drift_enabled=True)
    monkeypatch.setattr(shared, '_record_source_drift_result', Mock())
    orchestrate_read(store='Bronze', schema='demo', table_name='orders', verbose=False)
    session.plan.evidence['source_drift_observations'] = {'orders': result(table_id='orders')}
    error = RuntimeError('acceptance could not be confirmed')
    error.outcome_unknown = unknown
    monkeypatch.setattr(shared, 'accept_pipeline_source_snapshots', Mock(side_effect=error))
    runtime.publication.return_value = {'published': True, 'table_id': 'target', 'status': 'passed'}
    orchestrate_write(runtime.frame, store='Silver', schema='demo', table_name='target', write_mode='overwrite', verbose=False)
    summary = finalize_pipeline(session)
    assert summary['status'] == 'ungoverned_completed'
    assert summary['source_drift']['baseline']['status'] == ('acceptance_unknown' if unknown else 'acceptance_failed')
    assert 'source_drift' not in session.plan.evidence['final_result']


@pytest.mark.parametrize('read_mode', ['full', 'incremental'])
@pytest.mark.parametrize('modified', [0, None])
@pytest.mark.parametrize('mode', ['overwrite', 'append_all', 'append_new_only', 'scd1', 'scd2'])
def test_additions_alone_never_block_publication(runtime, monkeypatch, modified, mode, read_mode):
    session = setup_pipeline(source_drift_enabled=True, source_drift_block=True)
    monkeypatch.setattr(shared, '_record_source_drift_result', Mock())
    orchestrate_read(store='Bronze', schema='demo', table_name='orders', read_mode=read_mode,
        read_parameters={'watermark_column': 'id'} if read_mode == 'incremental' else None,
        verbose=False, **({'target_store': 'Silver', 'target_schema': 'demo', 'target_table_name': 'target'}
                          if read_mode == 'incremental' else {}))
    session.plan.evidence['source_drift_observations'] = {'orders': result('changes_detected',
        table_id='orders', added_count=100, removed_count=0, modified_count=modified)}
    parameters = {'key_columns': ['id']} if mode in {'scd1', 'scd2'} else None
    if mode == 'scd2':
        parameters['effective_column'] = 'id'
    orchestrate_write(runtime.frame, store='Silver', schema='demo', table_name='target', write_mode=mode,
        write_parameters=parameters, verbose=False)
    runtime.publication.assert_called_once()
    decision = session.plan.evidence['source_drift_decision']
    assert decision['can_continue'] is True and decision['requires_intervention'] is False
    assert decision['added_count'] == 100


@pytest.mark.parametrize('change', [dict(removed_count=1), dict(modified_count=1), dict(schema_changed=True),
    dict(status='observation_failed')])
def test_additions_do_not_mask_historical_changes_or_unavailable_observations(change):
    assert shared.source_drift_requires_intervention({'added_count': 100, 'removed_count': 0,
        'modified_count': 0, **change}) is True
