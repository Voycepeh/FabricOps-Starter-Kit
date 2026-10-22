"""Shared eligibility, claim ownership and independent profiling schedules."""
# ruff: noqa: D103
import copy
import importlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import Lock
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fabricops_kit.pipeline import shared

NOW = datetime(2026, 10, 23, 9, tzinfo=UTC)


@pytest.fixture
def metadata(monkeypatch):
    state = {'format': 'fabricops.table-profiling.v1', 'policies': {}, 'history': {}}
    store = {'token': '0', 'state': state, 'commits': 0}
    lock = Lock()
    context = {'config': {}, 'env': 'dev', '_pipeline_identities': {
        'orders': {'table_id': 'orders', 'store': 'Bronze', 'schema': 'demo', 'table_name': 'orders'}},
        'execution_plan': SimpleNamespace(plan_id='A', permits_persistence=True)}
    monkeypatch.setattr(shared, 'resolve_fabric_context', lambda context=None: (context['config'], context['env'], context))
    monkeypatch.setattr(shared, 'pipeline_physical_bindings', lambda identities, config, environment: {
        'orders': {'workspace_id': config.get('workspace', 'workspace'), 'item_id': config.get('item', 'lakehouse'),
                   'kind': 'lakehouse', 'schema': 'demo', 'table_name': 'orders'}})
    def read(**kwargs):
        with lock:
            return store['token'], copy.deepcopy(store['state'])
    def commit(state, *, expected_token, **kwargs):
        with lock:
            if expected_token != store['token']:
                raise shared.ProfilingConflict('stale token')
            store['state'] = copy.deepcopy(state)
            store['commits'] += 1
            store['token'] = str(store['commits'])
            return store['token']
    monkeypatch.setattr(shared, 'read_table_profiling_state', read)
    monkeypatch.setattr(shared, 'commit_table_profiling_state', commit)
    return SimpleNamespace(store=store, context=context, read=read, commit=commit)


def test_three_independent_defaults():
    policy = shared.default_profiling_policy()
    assert policy == {'standard': {'frequency':'interval','days':1,'trigger':'read_or_write'},
                      'grain': {'frequency':'first','trigger':'read_or_write'},
                      'frequency': {'frequency':'first','trigger':'read_or_write'}}
    assert shared.validate_profiling_policy(policy) == policy
    policy['standard']['days'] = 8
    assert shared.default_profiling_policy()['standard']['days'] == 1


@pytest.mark.parametrize('days', [0,-1,True,1.2,'1',None])
def test_interval_requires_positive_integer(days):
    policy = shared.default_profiling_policy()
    policy['standard']['days'] = days
    with pytest.raises(ValueError, match='positive integer'):
        shared.validate_profiling_policy(policy)


@pytest.mark.parametrize('frequency', ['disabled','on_demand','daily','weekly','monthly','yearly'])
def test_only_three_frequencies(frequency):
    policy = shared.default_profiling_policy()
    policy['grain']['frequency'] = frequency
    with pytest.raises(ValueError):
        shared.validate_profiling_policy(policy)


@pytest.mark.parametrize('trigger,operation,expected', [
    ('read','read',True),('read','write',False),('write','read',False),('write','write',True),
    ('read_or_write','read',True),('read_or_write','write',True)])
def test_independent_operation_triggers(trigger,operation,expected):
    assert shared.profiling_due({'frequency':'every','trigger':trigger}, {}, operation, NOW) is expected


@pytest.mark.parametrize('frequency,days,elapsed,due', [
    ('every',None,0,True),('first',None,100,False),('interval',1,0.9,False),
    ('interval',1,1,True),('interval',7,6.99,False),('interval',7,7,True),('interval',30,30,True)])
def test_elapsed_success_intervals(frequency,days,elapsed,due):
    settings = {'frequency':frequency,'trigger':'read_or_write', **({'days':days} if days else {})}
    history = {'last_success':NOW.isoformat(),'last_attempt':(NOW+timedelta(days=elapsed)).isoformat()}
    assert shared.profiling_due(settings,history,'read',NOW+timedelta(days=elapsed)) is due


def test_multiple_pipelines_share_success_and_activities_are_independent(metadata):
    a = shared.claim_table_profile('orders','standard','read',context=metadata.context,now=NOW)
    shared.maintain_table_profile_claim(a,context=metadata.context,complete=True,now=NOW+timedelta(seconds=10))
    pipeline_b = {**metadata.context,'execution_plan':SimpleNamespace(plan_id='B',permits_persistence=True)}
    assert shared.claim_table_profile('orders','standard','write',context=pipeline_b,now=NOW+timedelta(hours=1)) is None
    grain = shared.claim_table_profile('orders','grain','read',context=pipeline_b,now=NOW)
    frequency = shared.claim_table_profile('orders','frequency','write',context=pipeline_b,now=NOW)
    assert grain and frequency
    assert shared.claim_table_profile('orders','standard','read',context=pipeline_b,now=NOW+timedelta(days=1,seconds=11))


def test_first_only_success_never_repeats(metadata):
    claim = shared.claim_table_profile('orders','grain','read',context=metadata.context,now=NOW)
    shared.maintain_table_profile_claim(claim,context=metadata.context,complete=True,now=NOW)
    assert shared.claim_table_profile('orders','grain','write',context=metadata.context,now=NOW+timedelta(days=365)) is None


@pytest.mark.parametrize('frequency', ['every','first','interval'])
def test_failed_profiles_remain_due(metadata,frequency):
    policy = shared.default_profiling_policy()
    policy['standard'] = {'frequency':frequency,'trigger':'read_or_write',**({'days':1} if frequency=='interval' else {})}
    shared.save_table_profiling_policy('orders',policy,expected_token='0',context=metadata.context)
    claim = shared.claim_table_profile('orders','standard','write',context=metadata.context,now=NOW)
    shared.maintain_table_profile_claim(claim,context=metadata.context,complete=False,now=NOW)
    assert shared.claim_table_profile('orders','standard','read',context=metadata.context,now=NOW)
    entry=metadata.store['state']['history'][claim['key']]['activities']['standard']
    assert entry['last_status']=='failed' and 'last_success' not in entry


def test_environment_and_physical_contexts_do_not_suppress_each_other(metadata):
    contexts = [metadata.context,{**metadata.context,'env':'prod'},
                {**metadata.context,'config':{'workspace':'other'}}, {**metadata.context,'config':{'item':'other'}}]
    claims = [shared.claim_table_profile('orders','grain','read',context=context,now=NOW) for context in contexts]
    assert len({claim['key'] for claim in claims}) == 4


def test_concurrent_claims_have_one_owner(metadata):
    with ThreadPoolExecutor(8) as pool:
        claims=list(pool.map(lambda _: shared.claim_table_profile('orders','standard','read',context=metadata.context,now=NOW),range(24)))
    assert sum(claim is not None for claim in claims)==1


def test_interrupted_claim_expires_and_stale_owner_cannot_complete(metadata):
    abandoned=shared.claim_table_profile('orders','frequency','read',context=metadata.context,now=NOW)
    assert shared.claim_table_profile('orders','frequency','read',context=metadata.context,now=NOW+timedelta(seconds=299)) is None
    recovered=shared.claim_table_profile('orders','frequency','read',context=metadata.context,now=NOW+timedelta(seconds=301))
    assert recovered['token'] != abandoned['token']
    with pytest.raises(shared.ProfilingConflict):
        shared.maintain_table_profile_claim(abandoned,context=metadata.context,complete=True,now=NOW+timedelta(seconds=302))
    shared.maintain_table_profile_claim(recovered,context=metadata.context,complete=True,now=NOW+timedelta(seconds=302))


def test_renewal_preserves_expensive_active_work(metadata):
    claim=shared.claim_table_profile('orders','grain','read',context=metadata.context,now=NOW)
    shared.maintain_table_profile_claim(claim,context=metadata.context,now=NOW+timedelta(seconds=250))
    assert shared.claim_table_profile('orders','grain','read',context=metadata.context,now=NOW+timedelta(seconds=301)) is None


def test_schedule_runs_persisted_table_without_filtered_dataframe(metadata,monkeypatch):
    profiler=Mock(return_value={'row_count':100})
    monkeypatch.setattr(importlib.import_module('fabricops_kit.pipeline.profile_table'),'execute_table_profile',profiler)
    result=shared.schedule_table_profiling('orders','read',context=metadata.context)
    assert set(result['activities'])==set(shared.PROFILING_ACTIVITIES)
    assert profiler.call_count==3
    for call in profiler.call_args_list:
        assert call.kwargs['table_id']=='orders' and 'dataframe' not in call.kwargs
        assert len(call.kwargs['activities'])==1
    assert all('last_success' in entry for entry in next(iter(metadata.store['state']['history'].values()))['activities'].values())
    profiler.reset_mock()
    shared.schedule_table_profiling('orders','write',context=metadata.context)
    profiler.assert_not_called()


def test_test_diagnostics_never_claim_or_advance_shared_history(metadata,monkeypatch):
    context={**metadata.context,'execution_plan':SimpleNamespace(plan_id='Test',permits_persistence=False)}
    profiler=Mock(return_value={'row_count':100})
    monkeypatch.setattr(importlib.import_module('fabricops_kit.pipeline.profile_table'),'execute_table_profile',profiler)
    before=copy.deepcopy(metadata.store)
    result=shared.schedule_table_profiling('orders','read',context=context)
    assert result['persistence_status']=='disabled' and metadata.store==before
    with pytest.raises(RuntimeError,match='Test cannot claim'):
        shared.claim_table_profile('orders','standard','read',context=context)


def test_profiler_failure_does_not_consume_schedule(metadata,monkeypatch):
    monkeypatch.setattr(importlib.import_module('fabricops_kit.pipeline.profile_table'),'execute_table_profile',Mock(side_effect=RuntimeError('profile failed')))
    with pytest.raises(RuntimeError,match='profile failed'):
        shared.schedule_table_profiling('orders','write',context=metadata.context)
    entry=next(iter(metadata.store['state']['history'].values()))['activities']['standard']
    assert entry['last_status']=='failed' and 'last_success' not in entry and 'claim' not in entry


def test_policy_save_does_not_modify_history_and_stale_save_fails(metadata):
    policy=shared.default_profiling_policy();policy['grain']={'frequency':'every','trigger':'write'}
    shared.save_table_profiling_policy('orders',policy,expected_token='0',context=metadata.context)
    assert metadata.store['state']['policies']['orders']==policy and not metadata.store['state']['history']
    with pytest.raises(shared.ProfilingConflict):
        shared.save_table_profiling_policy('orders',policy,expected_token='0',context=metadata.context)


def test_native_authoring_controls_save_only_operational_policy(metadata,monkeypatch):
    import ipywidgets as widgets
    module=importlib.import_module('fabricops_kit.widgets.widget_data_contract')
    monkeypatch.setattr(shared,'profiling_context_key',lambda *args,**kwargs:('physical',{}))
    section=module._profiling_section(widgets,'orders',context=metadata.context,spark_session=None)
    grain=section.profiling_controls['grain']
    assert grain['frequency'].value=='first' and grain['days'].layout.display=='none'
    grain['frequency'].value='interval'
    assert grain['days'].layout.display==''
    grain['days'].value=7
    grain['trigger'].value='write'
    section.profiling_save.click()
    assert metadata.store['state']['policies']['orders']['grain']=={'frequency':'interval','days':7,'trigger':'write'}
    assert not metadata.store['state']['history']
    assert set(metadata.store['state'])=={'format','policies','history'}


def test_native_authoring_rejects_invalid_days_without_a_commit(metadata,monkeypatch):
    import ipywidgets as widgets
    module=importlib.import_module('fabricops_kit.widgets.widget_data_contract')
    monkeypatch.setattr(shared,'profiling_context_key',lambda *args,**kwargs:('physical',{}))
    section=module._profiling_section(widgets,'orders',context=metadata.context,spark_session=None)
    section.profiling_controls['standard']['days'].value=0
    section.profiling_save.click()
    assert metadata.store['commits']==0
    assert 'positive integer' in section.children[-1].value


@pytest.mark.parametrize('activity', ['standard','grain','frequency'])
def test_real_profiler_activities_publish_independent_metadata(activity,spark_session,monkeypatch):
    """Calculate real Spark profiles while observing each physical mutation boundary."""
    module=importlib.import_module('fabricops_kit.pipeline.profile_table')
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


# Retain real transport functions for focused serializable-CAS boundary tests.
_REAL_READ_STATE = shared.read_table_profiling_state
_REAL_COMMIT_STATE = shared.commit_table_profiling_state


@pytest.mark.parametrize('lost_ack', [False, True])
def test_delta_cas_uses_configured_metadata_and_confirms_lost_ack(metadata,monkeypatch,lost_ack):
    """Exercise real CAS construction/read-back with only Delta transport simulated."""
    import sys
    durable={'row':{'state_id':'central','token':'0','snapshot_json':json.dumps(metadata.store['state'])}}
    calls=[]
    class Frame:
        def __init__(self,rows):self.rows=rows
        def alias(self,name):return self
        def collect(self):return copy.deepcopy(self.rows)
    class Merge:
        def alias(self,name):return self
        def merge(self,frame,condition):
            assert condition=='target.state_id = source.state_id'
            self.row=frame.rows[0]
            return self
        def whenMatchedUpdate(self,*,set):
            self.changes=set
            return self
        def execute(self):
            assert 'CASE WHEN target.token' in self.changes['token']
            if "target.token = '"+durable['row']['token']+"'" not in self.changes['token']:
                raise RuntimeError('stale profiling state')
            durable['row']=copy.deepcopy(self.row)
            if lost_ack:raise OSError('lost acknowledgement')
    spark=SimpleNamespace(sql=lambda query:calls.append(query),createDataFrame=lambda rows,schema:Frame(rows))
    monkeypatch.setitem(sys.modules,'delta.tables',SimpleNamespace(DeltaTable=SimpleNamespace(forPath=lambda spark,path:Merge())))
    monkeypatch.setattr(shared,'get_spark_session',lambda supplied=None:spark)
    monkeypatch.setattr(shared,'build_runtime_audit_fields',lambda **kwargs:{})
    monkeypatch.setattr(shared,'resolve_configured_lakehouse_table',lambda *args,**kwargs:(None,None,None,'configured/profiling'))
    monkeypatch.setattr(shared,'read_lakehouse_table',lambda table,**kwargs:Frame([durable['row']]))
    monkeypatch.setattr(shared,'read_table_profiling_state',_REAL_READ_STATE)
    monkeypatch.setattr(shared,'commit_table_profiling_state',_REAL_COMMIT_STATE)
    state=copy.deepcopy(metadata.store['state']);state['policies']['orders']=shared.default_profiling_policy()
    token=shared.commit_table_profiling_state(state,expected_token='0',context=metadata.context)
    assert token==durable['row']['token'] and json.loads(durable['row']['snapshot_json'])==state
    assert any('Serializable' in query and 'configured/profiling' in query for query in calls)
    with pytest.raises(shared.ProfilingConflict):
        shared.commit_table_profiling_state(state,expected_token='0',context=metadata.context)


def test_every_write_runs_again_after_each_success(metadata):
    policy=shared.default_profiling_policy()
    policy['standard']={'frequency':'every','trigger':'write'}
    shared.save_table_profiling_policy('orders',policy,expected_token='0',context=metadata.context)
    assert shared.claim_table_profile('orders','standard','read',context=metadata.context,now=NOW) is None
    tokens=[]
    for index in range(3):
        claim=shared.claim_table_profile('orders','standard','write',context=metadata.context,now=NOW+timedelta(seconds=index))
        tokens.append(claim['token'])
        shared.maintain_table_profile_claim(claim,context=metadata.context,complete=True,now=NOW+timedelta(seconds=index))
    assert len(set(tokens))==3


def test_real_commit_boundary_rejects_test_before_delta_access(metadata):
    context={**metadata.context,'execution_plan':SimpleNamespace(permits_persistence=False)}
    with pytest.raises(RuntimeError,match='Test cannot commit'):
        _REAL_COMMIT_STATE(metadata.store['state'],expected_token='0',context=context)


def test_later_activity_failure_preserves_earlier_success_history(metadata,monkeypatch):
    profiler=Mock(side_effect=[{'row_count':100},RuntimeError('grain failed')])
    monkeypatch.setattr(importlib.import_module('fabricops_kit.pipeline.profile_table'),'execute_table_profile',profiler)
    with pytest.raises(RuntimeError,match='grain failed'):
        shared.schedule_table_profiling('orders','read',context=metadata.context)
    activities=next(iter(metadata.store['state']['history'].values()))['activities']
    assert activities['standard']['last_status']=='succeeded' and activities['standard']['last_success']
    assert activities['grain']['last_status']=='failed' and 'last_success' not in activities['grain']
    assert 'frequency' not in activities
