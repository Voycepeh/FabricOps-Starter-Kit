"""Contract policy, shared scheduling, durable completion and claim recovery."""
# ruff: noqa: D103
import copy
import importlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import Lock
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fabricops_kit.pipeline import shared
from fabricops_kit.activated_pipeline import shared as activation

REAL_HISTORY = shared.profiling_completion_history

NOW = datetime(2026, 10, 23, 9, tzinfo=UTC)


@pytest.fixture
def metadata(monkeypatch):
    store = {'token': '0', 'state': json.loads(activation.empty_activation_state()), 'commits': 0}
    lock = Lock()
    rows = {'METADATA_PIPELINE_RUN': {}, 'METADATA_DATA_PROFILED': [], 'METADATA_DATA_PROFILED_FREQUENCY': []}
    def context(run_id='A', **overrides):
        return {'config': {}, 'env': 'dev', '_pipeline_identities': {
            'orders': {'table_id': 'orders', 'store': 'Bronze', 'schema': 'demo', 'table_name': 'orders'}},
            '_pipeline_contracts': {'orders': None},
            'execution_plan': SimpleNamespace(plan_id=run_id, permits_persistence=True, evidence={}), **overrides}
    monkeypatch.setattr(shared, 'resolve_fabric_context', lambda context=None: (context['config'], context['env'], context))
    monkeypatch.setattr(shared, 'pipeline_physical_bindings', lambda identities, config, environment: {
        table_id: {'workspace_id': config.get('workspace', 'workspace'), 'item_id': config.get('item', 'lakehouse'),
                   'kind': 'lakehouse', 'schema': identity['schema'], 'table_name': identity['table_name']}
        for table_id, identity in identities.items()})
    def read(**kwargs):
        with lock:
            return store['token'], copy.deepcopy(store['state'])
    def commit(state, *, expected_token, **kwargs):
        with lock:
            if expected_token != store['token']:
                raise RuntimeError('stale token')
            store['state'] = copy.deepcopy(state)
            store['commits'] += 1
            store['token'] = str(store['commits'])
            return store['token']
    monkeypatch.setattr(activation, 'read_activation_state', read)
    monkeypatch.setattr(activation, 'commit_activation_state', commit)
    history_reads = []
    def history(table_id, *, context, activity=None, **kwargs):
        history_reads.append(activity)
        key, _descriptor = shared.profiling_context_key(table_id, context=context)
        result_ids = {kind: {row['profile_snapshot_id'] for row in rows[table]
                            if row['table_id'] == table_id and row['environment_name'] == context['env']}
                      for kind, table in [('standard', 'METADATA_DATA_PROFILED'), ('frequency', 'METADATA_DATA_PROFILED_FREQUENCY')]}
        completed = {}
        for run in rows['METADATA_PIPELINE_RUN'].values():
            if run['environment_name'] != context['env']:
                continue
            for event in json.loads(run['operation_summary_json']).get('profiling', []):
                kind = event['activity']
                if event.get('context_key') != key or event['status'] != 'passed' or not event.get('results_persisted'):
                    continue
                if activity is not None and activity != kind:
                    continue
                if kind != 'grain' and not (kind == 'frequency' and event.get('empty_result')) and event.get('profile_snapshot_id') not in result_ids[kind]:
                    continue
                if event.get('completed_at', '') > completed.get(kind, {}).get('last_success', ''):
                    completed[kind] = {'last_success': event['completed_at']}
        return completed
    monkeypatch.setattr(shared, 'profiling_completion_history', history)
    def persist(plan, **kwargs):
        if plan.permits_persistence:
            rows['METADATA_PIPELINE_RUN'][plan.plan_id] = {
                'run_id': plan.plan_id, 'environment_name': next((outcome['environment'] for outcome in plan.evidence.get('profiling', [])), 'dev'), 'operation_summary_json': json.dumps({'profiling': plan.evidence.get('profiling', [])})}
    monkeypatch.setattr(shared, 'persist_pipeline_run', persist)
    def execute(*, table_id, context, activities, **kwargs):
        activity = next(iter(activities))
        if shared.persistence_permitted(context) and activity != 'grain':
            table = 'METADATA_DATA_PROFILED' if activity == 'standard' else 'METADATA_DATA_PROFILED_FREQUENCY'
            rows[table].append({'table_id': table_id, 'environment_name': context['env'],
                                'profile_snapshot_id': context['_profile_snapshot_id']})
        return {'row_count': 100}
    profiler = Mock(side_effect=execute)
    monkeypatch.setattr(shared, 'execute_table_profile', profiler)
    return SimpleNamespace(store=store, context=context(), make_context=context, rows=rows,
                           profiler=profiler, execute=execute, commit=commit, history_reads=history_reads)


def policy(context, activity, settings):
    proposed = shared.default_profiling_policy()
    proposed[activity] = settings
    context['_pipeline_contracts']['orders'] = {'contract_payload_json': json.dumps({'profiling': proposed})}


def test_independent_defaults_and_validation():
    expected = {'standard': {'frequency': 'interval', 'days': 1, 'trigger': 'read_or_write'},
                'grain': {'frequency': 'first', 'trigger': 'read_or_write'},
                'frequency': {'frequency': 'first', 'trigger': 'read_or_write'}}
    assert shared.validate_profiling_policy(shared.default_profiling_policy()) == expected
    for value in (0, -1, True, 1.2, '1', None):
        invalid = copy.deepcopy(expected)
        invalid['standard']['days'] = value
        with pytest.raises(ValueError, match='positive integer'):
            shared.validate_profiling_policy(invalid)
    assert shared.default_profiling_policy() == expected


@pytest.mark.parametrize('frequency', ['every', 'first', 'interval'])
@pytest.mark.parametrize('trigger', ['read', 'write', 'read_or_write'])
def test_all_schedule_combinations(frequency, trigger):
    settings = {'frequency': frequency, 'trigger': trigger, **({'days': 2} if frequency == 'interval' else {})}
    for operation in ('read', 'write'):
        matching = trigger in (operation, 'read_or_write')
        assert shared.profiling_due(settings, {}, operation, NOW) is matching
        recent = {'last_success': (NOW - timedelta(days=1)).isoformat()}
        assert shared.profiling_due(settings, recent, operation, NOW) is (matching and frequency == 'every')
        older = {'last_success': (NOW - timedelta(days=2)).isoformat()}
        assert shared.profiling_due(settings, older, operation, NOW) is (matching and frequency != 'first')


def test_shared_history_survives_a_new_pipeline_and_process(metadata):
    shared.schedule_table_profiling('orders', 'read', context=metadata.context)
    assert metadata.profiler.call_count == 3
    metadata.profiler.reset_mock()
    other = metadata.make_context('other-pipeline')
    result = shared.schedule_table_profiling('orders', 'write', context=other)
    metadata.profiler.assert_not_called()
    assert result['activities']['standard']['reason'] == 'interval_not_elapsed'
    assert result['activities']['grain']['reason'] == 'already_completed'
    assert not metadata.store['state']['profiling_claims']
    assert set(metadata.store['state']) == {'format', 'environments', 'profiling_claims'}
    assert len(metadata.rows['METADATA_PIPELINE_RUN']) == 2


def test_environment_and_physical_destinations_are_independent(metadata):
    shared.schedule_table_profiling('orders', 'read', context=metadata.context)
    for index, overrides in enumerate(({'env': 'prod'}, {'config': {'workspace': 'other'}}, {'config': {'item': 'other'}},
        {'_pipeline_identities': {'orders': {**metadata.context['_pipeline_identities']['orders'], 'schema': 'other'}}},
        {'_pipeline_identities': {'orders': {**metadata.context['_pipeline_identities']['orders'], 'table_name': 'other'}}})):
        shared.schedule_table_profiling('orders', 'read', context=metadata.make_context(str(index), **overrides))
    assert metadata.profiler.call_count == 18


def test_concurrent_claims_have_one_owner(metadata):
    with ThreadPoolExecutor(8) as pool:
        claims = list(pool.map(lambda _: shared.claim_table_profile('orders', 'standard', 'read', context=metadata.context, now=NOW), range(24)))
    assert sum('token' in claim for claim in claims) == 1


def test_expired_claim_recovers_and_fences_stale_owner(metadata):
    abandoned = shared.claim_table_profile('orders', 'frequency', 'read', context=metadata.context, now=NOW)
    assert shared.claim_table_profile('orders', 'frequency', 'read', context=metadata.context, now=NOW + timedelta(seconds=299))['status'] == 'skipped'
    recovered = shared.claim_table_profile('orders', 'frequency', 'read', context=metadata.context, now=NOW + timedelta(seconds=301))
    assert recovered['token'] != abandoned['token']
    with pytest.raises(shared.ProfilingConflict, match='expired or belongs'):
        shared.maintain_table_profile_claim(abandoned, context=metadata.context, complete=True, now=NOW + timedelta(seconds=302))
    shared.maintain_table_profile_claim(recovered, context=metadata.context, complete=True, now=NOW + timedelta(seconds=302))
    shared.maintain_table_profile_claim(recovered, context=metadata.context, complete=False, now=NOW + timedelta(seconds=302))
    assert 'token' in shared.claim_table_profile('orders', 'frequency', 'read', context=metadata.context, now=NOW + timedelta(seconds=303))


def test_renewal_keeps_long_running_activity_reserved(metadata):
    claim = shared.claim_table_profile('orders', 'grain', 'read', context=metadata.context, now=NOW)
    shared.maintain_table_profile_claim(claim, context=metadata.context, now=NOW + timedelta(seconds=250))
    assert shared.claim_table_profile('orders', 'grain', 'read', context=metadata.context, now=NOW + timedelta(seconds=301))['status'] == 'skipped'


def test_failure_after_results_persist_does_not_consume_interval(metadata):
    def fail(**kwargs):
        metadata.execute(**kwargs)
        raise RuntimeError('after persistence')
    metadata.profiler.side_effect = fail
    with pytest.raises(RuntimeError, match='after persistence'):
        shared.schedule_table_profiling('orders', 'write', context=metadata.context)
    assert metadata.rows['METADATA_DATA_PROFILED']
    assert shared.profiling_completion_history('orders', context=metadata.context) == {}
    assert metadata.context['execution_plan'].evidence['profiling'][-1]['status'] == 'failed'
    assert shared.claim_table_profile('orders', 'standard', 'write', context=metadata.context)


def test_later_failure_preserves_earlier_success(metadata):
    def execute(**kwargs):
        if kwargs['activities'] == {'grain'}:
            raise RuntimeError('grain failed')
        return metadata.execute(**kwargs)
    metadata.profiler.side_effect = execute
    with pytest.raises(RuntimeError, match='grain failed'):
        shared.schedule_table_profiling('orders', 'read', context=metadata.context)
    assert set(shared.profiling_completion_history('orders', context=metadata.context)) == {'standard'}
    outcomes = metadata.context['execution_plan'].evidence['profiling']
    assert outcomes[-1]['status'] == 'failed' and outcomes[-1]['activity'] == 'grain'
    assert outcomes[1]['status'] == 'passed' and outcomes[1]['activity'] == 'standard'


def test_result_rows_are_required_for_nonempty_completion(metadata):
    shared.schedule_table_profiling('orders', 'read', context=metadata.context)
    metadata.rows['METADATA_DATA_PROFILED'].clear()
    metadata.rows['METADATA_DATA_PROFILED_FREQUENCY'].clear()
    assert set(shared.profiling_completion_history('orders', context=metadata.context)) == {'grain'}


def test_empty_frequency_has_durable_marker(metadata):
    def execute(**kwargs):
        return {'row_count': 100, 'empty_result': True} if kwargs['activities'] == {'frequency'} else metadata.execute(**kwargs)
    metadata.profiler.side_effect = execute
    shared.schedule_table_profiling('orders', 'read', context=metadata.context)
    assert not metadata.rows['METADATA_DATA_PROFILED_FREQUENCY']
    assert 'frequency' in shared.profiling_completion_history('orders', context=metadata.context)


def test_read_only_testing_does_not_consume_schedule(metadata):
    metadata.context['execution_plan'].permits_persistence = False
    before = copy.deepcopy(metadata.store)
    result = shared.schedule_table_profiling('orders', 'read', context=metadata.context)
    assert result['persistence_status'] == 'disabled' and result['row_count'] == 100
    assert metadata.store == before and not metadata.rows['METADATA_PIPELINE_RUN']
    with pytest.raises(RuntimeError, match='Test cannot claim'):
        shared.claim_table_profile('orders', 'standard', 'read', context=metadata.context)


def test_every_write_and_frozen_policy_are_exact(metadata):
    policy(metadata.context, 'standard', {'frequency': 'every', 'trigger': 'write'})
    original = copy.deepcopy(metadata.context['_pipeline_contracts'])
    shared.schedule_table_profiling('orders', 'read', context=metadata.context)
    assert metadata.profiler.call_count == 2
    shared.schedule_table_profiling('orders', 'write', context=metadata.context)
    shared.schedule_table_profiling('orders', 'write', context=metadata.context)
    assert metadata.profiler.call_count == 4
    assert metadata.context['_pipeline_contracts'] == original


def test_multiple_tables_keep_independent_outcomes_in_one_run(metadata):
    metadata.context['_pipeline_identities']['customers'] = {'table_id': 'customers', 'store': 'Bronze', 'schema': 'demo', 'table_name': 'customers'}
    shared.schedule_table_profiling('orders', 'read', context=metadata.context)
    shared.schedule_table_profiling('customers', 'write', context=metadata.context)
    assert len(metadata.rows['METADATA_PIPELINE_RUN']) == 1
    saved = json.loads(metadata.rows['METADATA_PIPELINE_RUN']['A']['operation_summary_json'])['profiling']
    passed = [outcome for outcome in saved if outcome['status'] == 'passed']
    assert len(passed) == 6 and {outcome['table_id'] for outcome in passed} == {'orders', 'customers'}
    assert all(outcome['physical']['table_name'] == outcome['table_id'] for outcome in passed)


def test_draft_controls_follow_contract_save_and_frozen_is_read_only():
    import ipywidgets as widgets
    module = importlib.import_module('fabricops_kit.widgets.widget_data_contract')
    payload = {'profiling': shared.default_profiling_policy()}
    edits = []
    section = module._profiling_section(widgets, payload, editable=True, on_change=edits.append)
    grain = section.profiling_controls['grain']
    grain['frequency'].value = 'interval'
    grain['days'].value = 7
    grain['trigger'].value = 'write'
    assert edits[-1]['grain'] == {'frequency': 'interval', 'days': 7, 'trigger': 'write'}
    assert grain['days'].layout.display == ''
    assert payload['profiling']['grain']['frequency'] == 'first'
    frozen = module._profiling_section(widgets, {'profiling': edits[-1]}, editable=False, on_change=edits.append)
    assert all(control.disabled for values in frozen.profiling_controls.values() for control in values.values())


@pytest.mark.parametrize('activity', ['standard','grain','frequency'])
def test_real_profiler_activities_publish_independent_metadata(activity,spark_session,monkeypatch):
    """Calculate real Spark profiles while observing each physical mutation boundary."""
    module=importlib.import_module('fabricops_kit.pipeline.shared')
    frame=spark_session.createDataFrame([(1,'A'),(2,'A'),(3,'B')],['id','category'])
    identity={'table_id':'orders','store':'Bronze','schema':'demo','table_name':'orders','store_kind':'lakehouse'}
    monkeypatch.setattr(module,'resolve_catalogue_table_identity',lambda *args,**kwargs:dict(identity))
    reader=Mock(return_value=frame)
    monkeypatch.setattr(module,'read_lakehouse_table',reader)
    monkeypatch.setattr(module,'_profile_snapshot_id',lambda **kwargs:'claim-snapshot')
    # Keep aggregate/distribution/grain calculations real, replace metadata transport.
    monkeypatch.setattr(module,'_canonical_profiled_dataframe',lambda profile,**kwargs: profile.withColumnRenamed('ROW_COUNT','row_count'))
    monkeypatch.setattr(module,'_frequency_metadata_dataframe',lambda frequency,**kwargs:frequency)
    monkeypatch.setattr(module,'_catalogue_dataframe_from_profiled',lambda *args,**kwargs:object())
    spies={}
    for name in ['_replace_snapshot_rows','_replace_frequency_rows','_upsert_catalogue_identities','_persist_grain_candidates','_stage_catalogue_profile_retry']:
        spies[name]=Mock(return_value=False)
        monkeypatch.setattr(module,name,spies[name])
    result=module.execute_table_profile(table_id='orders',context={'config':{},'env':'dev'},
        spark_session=spark_session,activities={activity},verbose=False)
    assert reader.call_args.kwargs['table_id']=='orders' and result['row_count']==3
    assert spies['_replace_snapshot_rows'].called is (activity=='standard')
    assert spies['_upsert_catalogue_identities'].called is (activity=='standard')
    assert spies['_persist_grain_candidates'].called is (activity=='grain')
    assert spies['_replace_frequency_rows'].called is (activity=='frequency')
    if activity=='frequency':
        rows=spies['_replace_frequency_rows'].call_args.kwargs['frequency_df'].collect()
        assert rows and all(row.profile_id is None for row in rows)
    if result.get('profile') is not None:
        result['profile'].unpersist()




def test_run_commit_failure_does_not_leave_in_memory_success_as_durable_history(metadata, monkeypatch):
    def persist(plan, **kwargs):
        if any(event['status'] == 'passed' for event in plan.evidence.get('profiling', [])):
            plan.evidence['persistence_failed'] = True
            raise RuntimeError('run commit failed')
        metadata.rows['METADATA_PIPELINE_RUN'][plan.plan_id] = {
            'environment_name': 'dev', 'operation_summary_json': json.dumps({'profiling': plan.evidence.get('profiling', [])})}
    monkeypatch.setattr(shared, 'persist_pipeline_run', persist)
    with pytest.raises(RuntimeError, match='run commit failed'):
        shared.schedule_table_profiling('orders', 'read', context=metadata.context)
    assert metadata.rows['METADATA_DATA_PROFILED']
    assert shared.profiling_completion_history('orders', context=metadata.context) == {}


def test_metadata_outage_is_not_reported_as_a_legitimate_skip(metadata, monkeypatch):
    monkeypatch.setattr(activation, 'commit_activation_state', Mock(side_effect=OSError('unavailable')))
    with pytest.raises(shared.ProfilingConflict, match='could not be confirmed'):
        shared.claim_table_profile('orders', 'standard', 'read', context=metadata.context)
    metadata.profiler.assert_not_called()


def test_slow_retry_rechecks_expiry(metadata, monkeypatch):
    claim = shared.claim_table_profile('orders', 'standard', 'read', context=metadata.context, now=NOW)
    times = iter([NOW, NOW + timedelta(seconds=301)])
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None): return next(times)
    monkeypatch.setattr(shared, 'datetime', Clock)
    def contend(*args, **kwargs):
        metadata.store['token'] = 'changed'
        raise RuntimeError('contention')
    monkeypatch.setattr(activation, 'commit_activation_state', Mock(side_effect=contend))
    with pytest.raises(shared.ProfilingConflict, match='expired'):
        shared.maintain_table_profile_claim(claim, context=metadata.context, complete=True)
    activation.commit_activation_state.assert_called_once()


def test_no_publication_records_all_skips_without_claims(metadata):
    result = shared.skip_table_profiling('orders', 'write', 'No successful publication', context=metadata.context)
    assert len(result['activities']) == 3
    assert metadata.store['commits'] == 0
    assert shared.profiling_completion_history('orders', context=metadata.context) == {}


def test_profiling_failure_releases_cached_output(metadata, monkeypatch):
    cached = Mock()
    def execute(**kwargs): return {**metadata.execute(**kwargs), 'profile': cached}
    metadata.profiler.side_effect = execute
    monkeypatch.setattr(shared, 'maintain_table_profile_claim', Mock(side_effect=shared.ProfilingConflict('lost lease')))
    with pytest.raises(shared.ProfilingConflict, match='lost lease'):
        shared.schedule_table_profiling('orders', 'read', context=metadata.context)
    cached.unpersist.assert_called_once_with()
    assert shared.profiling_completion_history('orders', context=metadata.context) == {}


def test_failed_journal_write_cannot_leak_into_a_later_snapshot(metadata, monkeypatch):
    persist = shared.persist_pipeline_run
    failed = []
    def fail_once(plan, **kwargs):
        if not failed and plan.evidence.get('profiling', [{}])[-1].get('status') == 'passed':
            failed.append(True)
            plan.evidence['persistence_failed'] = True
            raise RuntimeError('journal commit failed')
        return persist(plan, **kwargs)
    monkeypatch.setattr(shared, 'persist_pipeline_run', fail_once)
    with pytest.raises(RuntimeError, match='journal commit failed'):
        shared.schedule_table_profiling('orders', 'read', context=metadata.context)
    shared.persist_pipeline_run(metadata.context['execution_plan'])
    assert shared.profiling_completion_history('orders', context=metadata.context) == {}
    assert not any(event['status'] == 'passed' for event in metadata.context['execution_plan'].evidence['profiling'])


def test_final_completion_cas_rejects_replaced_owner(metadata, monkeypatch):
    maintain = shared.maintain_table_profile_claim
    def replace_owner(claim, **kwargs):
        if kwargs.get('complete') is True:
            metadata.store['state']['profiling_claims'][claim['claim_key']]['token'] = 'replacement'
        return maintain(claim, **kwargs)
    monkeypatch.setattr(shared, 'maintain_table_profile_claim', replace_owner)
    with pytest.raises(shared.ProfilingConflict, match='belongs to another'):
        shared.schedule_table_profiling('orders', 'read', context=metadata.context)
    assert shared.profiling_completion_history('orders', context=metadata.context) == {}


def test_completion_keeps_reservation_until_run_commit(metadata, monkeypatch):
    persist = shared.persist_pipeline_run
    observed = []
    def inspect(plan, **kwargs):
        event = plan.evidence.get('profiling', [{}])[-1]
        if event.get('status') == 'passed':
            owned = metadata.store['state']['profiling_claims'][event['context_key'] + ':' + event['activity']]
            observed.append(owned['completed_at'] == event['completed_at'])
        return persist(plan, **kwargs)
    monkeypatch.setattr(shared, 'persist_pipeline_run', inspect)
    shared.schedule_table_profiling('orders', 'read', context=metadata.context)
    assert observed == [True, True, True]
    assert not metadata.store['state']['profiling_claims']


def test_claim_checks_history_once_per_activity_and_not_for_mismatched_triggers(metadata):
    shared.schedule_table_profiling('orders', 'read', context=metadata.context)
    assert metadata.history_reads == ['standard', 'grain', 'frequency']
    metadata.history_reads.clear()
    policy(metadata.context, 'standard', {'frequency': 'every', 'trigger': 'write'})
    shared.schedule_table_profiling('orders', 'read', context=metadata.context)
    assert metadata.history_reads == ['grain', 'frequency']


@pytest.mark.parametrize('activity', [None, 'standard', 'grain', 'frequency'])
def test_history_filters_and_aggregates_in_spark(metadata, spark_session, monkeypatch, activity):
    shared.schedule_table_profiling('orders', 'read', context=metadata.context)
    completed = shared.profiling_completion_history('orders', context=metadata.context)
    metadata.rows['METADATA_PIPELINE_RUN']['unrelated'] = {
        'run_id': 'unrelated', 'environment_name': 'dev', 'operation_summary_json': json.dumps({'profiling': [
            {'context_key': 'other-destination', 'activity': 'standard', 'status': 'passed',
             'results_persisted': True, 'profile_snapshot_id': 'other-snapshot', 'completed_at': '2099-01-01T00:00:00+00:00'},
            {'context_key': shared.profiling_context_key('orders', context=metadata.context)[0],
             'activity': 'standard', 'status': 'passed', 'results_persisted': True,
             'profile_snapshot_id': 'missing-snapshot', 'completed_at': '2099-01-01T00:00:00+00:00'}]})}
    metadata.rows['METADATA_DATA_PROFILED'].append({'table_id': 'orders', 'environment_name': 'dev', 'profile_snapshot_id': 'other-snapshot'})
    tables = {table: spark_session.createDataFrame(
        [{**row, 'record_type': 'run', 'run_details_json': row['operation_summary_json']} for row in rows.values()] if isinstance(rows, dict) else rows,
        'run_id string, environment_name string, record_type string, run_details_json string' if table == 'METADATA_PIPELINE_RUN'
        else 'table_id string, environment_name string, profile_snapshot_id string')
        for table, rows in metadata.rows.items()}
    reads = []
    def reader(table, **kwargs):
        reads.append(table)
        return tables[table]
    monkeypatch.setattr(shared, 'read_lakehouse_table', reader)
    monkeypatch.setattr(shared, 'metadata_table_physical_schema', lambda *args: 'engineering')
    actual = REAL_HISTORY('orders', context=metadata.context, spark_session=spark_session, activity=activity)
    assert actual == ({activity: completed[activity]} if activity is not None else completed)
    assert len(reads) == (3 if activity is None else 1 if activity == 'grain' else 2)
