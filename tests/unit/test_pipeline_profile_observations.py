"""Dry Run profiling never publishes prepared business aggregates."""
# ruff: noqa: F811
from unittest.mock import Mock

import pytest

from fabricops_kit import setup_pipeline, orchestrate_read, orchestrate_write, finalize_pipeline
from fabricops_kit.pipeline import shared
from tests.unit.test_pipeline_session import runtime  # noqa: F401


@pytest.mark.parametrize("max_rows", [None, 1])
def test_read_and_prepared_write_profile_once_then_finalize_without_rescanning(runtime, spark_session, monkeypatch, max_rows):
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
    session = setup_pipeline(pipeline_mode="Dry Run", grain_discovery_enabled=True, frequency_enabled=True, profiling_max_rows=max_rows)
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
        assert profile['row_count'] == (count if max_rows is None else None)
        assert profile['profiled_row_count'] == (count if max_rows is None else 1)
        assert profile['activities']['grain']['frequency_profile'] is None
        assert profile['activities']['frequency']['grain_candidates'] == []
    stats = {row.COLUMN_NAME: row for row in write['profile_result']['profile'].collect()}
    assert stats['id'].MIN_VALUE == '10' and stats['id'].MAX_VALUE == ('20' if max_rows is None else '10')
    assert stats['secret'].MIN_VALUE == 'masked'
    if max_rows is None:
        assert {row.VALUE for row in write['profile_result']['frequency_profile'].collect()} == {'masked'}
    else:
        assert write['profile_result']['frequency_profile'] is None  # 100% distinct in one selected row.
    assert 'profile_observations' not in session.plan.evidence
    save = Mock(return_value={})
    monkeypatch.setattr(shared, '_persist_profile_observation', save)
    result = finalize_pipeline(session)
    assert result['status'] == 'dry_run_completed'
    assert save.call_count == 0 and calculate.call_count == 2 and not published
    assert all(not event['results_persisted'] for event in result['profiling'])
    assert 'profile_observations' not in session.plan.evidence
    finalize_pipeline(session)
    assert save.call_count == 0 and calculate.call_count == 2 and not published


@pytest.mark.parametrize('failed', [False, True])
def test_failed_or_incomplete_close_discards_pending_observations(runtime, monkeypatch, failed):
    """An interrupted run cannot retain or publish pending value-bearing aggregates."""
    session = setup_pipeline(pipeline_mode="Dry Run", grain_discovery_enabled=True, frequency_enabled=True)
    session.plan.evidence['profile_observations'] = [object()]
    save = Mock(side_effect=AssertionError('must not publish unsuccessful observations'))
    monkeypatch.setattr(shared, '_persist_profile_observation', save)
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', Mock())
    session.close(failed=failed)
    result = finalize_pipeline(session)
    assert result['status'] == ('failed' if failed else 'incomplete')
    assert 'profile_observations' not in session.plan.evidence
    save.assert_not_called()


def test_dry_run_finalization_never_publishes_profile_observations(runtime, monkeypatch):
    """Dry Run profile observations remain session-only."""
    session = setup_pipeline(pipeline_mode="Dry Run", grain_discovery_enabled=True, frequency_enabled=True)
    orchestrate_read(store='Bronze', schema='demo', table_name='source')
    session.plan.evidence['profile_observations'] = [{'profile_snapshot_id': 'stable-profile-id'}]
    save = Mock(side_effect=PermissionError('metadata unavailable'))
    monkeypatch.setattr(shared, '_persist_profile_observation', save)
    rows = []
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', lambda plan, row, **kw: rows.append(row))
    from types import SimpleNamespace
    session.report = SimpleNamespace(value='')
    result = finalize_pipeline(session)
    assert result['status'] == 'dry_run_completed'
    assert not rows
    assert 'dry_run_completed' in session.report.value
    assert finalize_pipeline(session) == result
    save.assert_not_called()


@pytest.mark.parametrize('query', [None, 'SELECT id FROM demo.source'])
def test_test_read_reuses_only_the_unfiltered_source(runtime, monkeypatch, query):
    """A projected query must still profile the complete physical table."""
    setup_pipeline(pipeline_mode="Dry Run", grain_discovery_enabled=True, frequency_enabled=True)
    profile = Mock(return_value={'row_count': 2})
    monkeypatch.setattr(runtime.read, 'schedule_table_profiling', profile)
    result = orchestrate_read(store='Bronze', schema='demo', table_name='source', query=query)
    if query is None:
        assert profile.call_args.kwargs['dataframe'] is result['dataframe']
    else:
        assert 'dataframe' not in profile.call_args.kwargs


def test_disabled_bounded_profiling_does_not_disable_or_sample_guardrails(runtime, monkeypatch):
    """Read boundary checks receive the original input even with a profiling bound."""
    setup_pipeline(pipeline_mode='Dry Run', profiling_enabled=False, profiling_max_rows=1)
    monkeypatch.setattr(runtime.read, 'pipeline_guardrail_types', lambda *a: {'schema', 'grain', 'data_quality'})
    monkeypatch.setattr(runtime.read, 'schedule_table_profiling', shared.schedule_table_profiling)
    monkeypatch.setattr(shared, 'profiling_completion_history', lambda *a, **kw: {})
    calculate = Mock(side_effect=AssertionError('profiling disabled'))
    monkeypatch.setattr(shared, 'execute_table_profile', calculate)
    checks = []
    for name in ('check_schema', 'check_dq'):
        check = Mock(return_value={'status': 'passed', 'can_continue': True, 'checks': []})
        monkeypatch.setattr(runtime.read, name, check)
        checks.append(check)
    result = orchestrate_read(store='Bronze', schema='demo', table_name='source')
    assert result['dataframe'] is runtime.frame
    for check in checks:
        assert check.call_args.args[0] is runtime.frame
    calculate.assert_not_called()
