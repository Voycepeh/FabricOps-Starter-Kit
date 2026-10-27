"""Test observations stay in memory until a successful explicit finalization."""
# ruff: noqa: F811
from unittest.mock import Mock

import pytest

from fabricops_kit import setup_pipeline, orchestrate_read, orchestrate_write, finalize_pipeline
from fabricops_kit.pipeline import shared
from tests.unit.test_pipeline_session import runtime  # noqa: F401


def test_read_and_prepared_write_profile_once_then_finalize_without_rescanning(runtime, spark_session, monkeypatch):
    """Use real aggregates and distributions; only runtime and metadata transport are mocked."""
    source = spark_session.createDataFrame([(1, 'private'), (2, 'private'), (3, 'private')], ['id', 'secret'])
    prepared = spark_session.createDataFrame([(10, 'masked'), (20, 'masked')], ['id', 'secret'])
    monkeypatch.setattr(shared, 'get_spark_session', lambda *a, **kw: spark_session)
    monkeypatch.setattr(runtime.read, 'pipeline_read', lambda **kw: {'dataframe': source, 'table_id': 'source'})
    for owner in (runtime.read, runtime.write):
        monkeypatch.setattr(owner, 'schedule_table_profiling', shared.schedule_table_profiling)
    monkeypatch.setattr(shared, 'profiling_completion_history', lambda *a, **kw: {})
    monkeypatch.setattr(shared, 'resolve_catalogue_table_identity', lambda config, env, table_id, **kw: {
        'table_id': table_id, 'store_kind': 'lakehouse', 'store': 'Bronze' if table_id == 'source' else 'Silver',
        'schema': 'demo', 'table_name': table_id})
    monkeypatch.setattr(runtime.write, 'pipeline_guardrail_types', lambda *a: {'sensitive_data'})
    monkeypatch.setattr(runtime.write, 'check_sensitive_data', lambda *a, **kw: {
        'status': 'passed', 'can_continue': True, 'dataframe': prepared, 'support_mapping': None})
    calculate = Mock(wraps=shared.execute_table_profile)
    monkeypatch.setattr(shared, 'execute_table_profile', calculate)
    published = []
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', lambda plan, row, **kw: published.append(row))
    session = setup_pipeline()
    read = orchestrate_read(store='Bronze', schema='demo', table_name='source')
    write = orchestrate_write(source, store='Silver', schema='demo', table_name='target', write_mode='overwrite')
    assert not write['published'] and write['dataframe'] is prepared
    assert calculate.call_count == 2
    assert calculate.call_args_list[0].kwargs['dataframe'] is source
    assert calculate.call_args_list[1].kwargs['dataframe'] is prepared
    assert all(call.kwargs['activities'] == {'standard', 'grain', 'frequency'} for call in calculate.call_args_list)
    assert not published
    for result, count in ((read, 3), (write, 2)):
        profile = result['profile_result']
        assert {'profile', 'frequency_profile', 'activities', 'row_count'} <= profile.keys()
        assert profile['row_count'] == count
        assert profile['activities']['grain']['frequency_profile'] is None
        assert profile['activities']['frequency']['grain_candidates'] == []
    stats = {row.COLUMN_NAME: row for row in write['profile_result']['profile'].collect()}
    assert stats['id'].MIN_VALUE == '10' and stats['id'].MAX_VALUE == '20'
    assert stats['secret'].MIN_VALUE == 'masked'
    assert {row.VALUE for row in write['profile_result']['frequency_profile'].collect()} == {'masked'}
    observations = session.plan.evidence['profile_observations']
    assert [(item['identity']['table_id'], item['trigger']) for item in observations] == [('source', 'read'), ('target', 'write')]
    assert len({item['profile_snapshot_id'] for item in observations}) == 2
    assert all('dataframe' not in item for item in observations)
    save = Mock(return_value={})
    monkeypatch.setattr(shared, '_persist_profile_observation', save)
    result = finalize_pipeline(session)
    assert result['status'] == 'ungoverned_completed'
    assert save.call_count == 2 and calculate.call_count == 2 and len(published) == 1
    assert all('execution_plan' not in call.kwargs['context'] for call in save.call_args_list)
    assert all(event['results_persisted'] and event['pipeline_run_id'] == session.plan.plan_id for event in result['profiling'])
    assert 'profile_observations' not in session.plan.evidence
    finalize_pipeline(session)
    assert save.call_count == 2 and calculate.call_count == 2 and len(published) == 1


@pytest.mark.parametrize('failed', [False, True])
def test_failed_or_incomplete_close_discards_pending_observations(runtime, monkeypatch, failed):
    """An interrupted run cannot retain or publish pending value-bearing aggregates."""
    session = setup_pipeline()
    session.plan.evidence['profile_observations'] = [object()]
    save = Mock(side_effect=AssertionError('must not publish unsuccessful observations'))
    monkeypatch.setattr(shared, '_persist_profile_observation', save)
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', Mock())
    session.close(failed=failed)
    result = finalize_pipeline(session)
    assert result['status'] == ('failed' if failed else 'incomplete')
    assert 'profile_observations' not in session.plan.evidence
    save.assert_not_called()


def test_observation_publication_failure_commits_failed_outcome(runtime, monkeypatch):
    """Metadata failure cannot leave an authoritative successful Test completion."""
    session = setup_pipeline()
    orchestrate_read(store='Bronze', schema='demo', table_name='source')
    session.plan.evidence['profile_observations'] = [{'profile_snapshot_id': 'stable-profile-id'}]
    save = Mock(side_effect=PermissionError('metadata unavailable'))
    monkeypatch.setattr(shared, '_persist_profile_observation', save)
    rows = []
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', lambda plan, row, **kw: rows.append(row))
    from types import SimpleNamespace
    session.report = SimpleNamespace(value='')
    with pytest.raises(RuntimeError, match='finalized as failed'):
        finalize_pipeline(session)
    assert session.plan.run_result['status'] == 'failed' and rows[-1]['status'] == 'failed'
    assert 'failed' in session.report.value
    assert any(item['code'] == 'test_profile_publication_failed' for item in rows[-1]['failures'])
    assert finalize_pipeline(session)['status'] == 'failed'
    save.assert_called_once()


@pytest.mark.parametrize('query', [None, 'SELECT id FROM demo.source'])
def test_test_read_reuses_only_the_unfiltered_source(runtime, monkeypatch, query):
    """A projected query must still profile the complete physical table."""
    setup_pipeline()
    profile = Mock(return_value={'row_count': 2})
    monkeypatch.setattr(runtime.read, 'schedule_table_profiling', profile)
    result = orchestrate_read(store='Bronze', schema='demo', table_name='source', query=query)
    if query is None:
        assert profile.call_args.kwargs['dataframe'] is result['dataframe']
    else:
        assert 'dataframe' not in profile.call_args.kwargs
