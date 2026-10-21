"""Whole-pipeline activation and unattended Live with real identity logic."""
# ruff: noqa: D103, F811
from __future__ import annotations
import copy
import importlib
import json
from dataclasses import replace
from pathlib import Path
from threading import Lock
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor

import pytest

from fabricops_kit import activate_pipeline, package_activated_pipeline, verify_pipeline_deployment, setup_pipeline, finalize_pipeline, set_pipeline_active
from fabricops_kit.activated_pipeline import shared as service
from fabricops_kit.pipeline import shared as pipeline
from tests.unit.test_pipeline_run_evidence import runtime  # noqa: F401 - reusable simulated Delta fixture


@pytest.fixture
def approved_runtime(runtime, monkeypatch, tmp_path):
    """Simulate only transport/transaction boundaries and actual Fabric definition fetch."""
    make, operation, saved, writes, failure = runtime
    executable = tmp_path / 'project.ipynb'
    executable.write_text('{"cells":[{"cell_type":"code","source":["transform()"]}]}')
    from fabricops_kit.pipeline.shared import notebook_executable_fingerprint
    digest = notebook_executable_fingerprint(executable.read_bytes())
    context = {"config": {}, "env": "canary", "notebook_id": "notebook", "notebook_name": "pipeline", "workspace_id": "workspace"}
    monkeypatch.setattr('fabricops_kit.pipeline.shared.deployed_notebook_fingerprint', lambda runtime: digest)
    monkeypatch.setattr(service, 'resolve_fabric_context', lambda context=None: (context.get('config', {}), context.get('env', 'canary'), dict(context or {})))
    monkeypatch.setattr(pipeline, 'resolve_fabric_context', service.resolve_fabric_context)
    store = SimpleNamespace(workspace_id='workspace', item_id='lakehouse', kind='lakehouse')
    monkeypatch.setattr(service, 'get_store', lambda *a, **kw: store)
    contracts, versions, rules = [], [], []
    agreement = {'agreement_id':'agreement', 'agreement_version':'1.0', 'agreement_name':'Example', 'start_date':'2020-01-01', 'expiry_date':'2099-01-01'}
    def records(table, **kwargs):
        return {'METADATA_PIPELINE_RUN': list(saved.values()), 'METADATA_DATA_CONTRACT': contracts,
                'METADATA_ACTIVATED_PIPELINE': versions, 'METADATA_GUARDRAIL_RESULTS': rules,
                'METADATA_DATA_AGREEMENT': [agreement]}[table]
    monkeypatch.setattr(service, 'metadata_records', records)
    monkeypatch.setattr(service, 'build_runtime_audit_fields', lambda **kw: {})
    transaction = Lock()
    def commit(row, *, expected_active_id, **kw):
        with transaction:
            active = [item for item in versions if item['pipeline_id'] == row['pipeline_id'] and item.get('is_active')]
            if (active[0]['activated_pipeline_id'] if active else None) != expected_active_id:
                raise ValueError('Concurrent activation or explicit switching required')
            existing = [item for item in versions if item['pipeline_id'] == row['pipeline_id'] and item['pipeline_version'] == row['pipeline_version']]
            if existing and existing[0]['manifest_json'] != row['manifest_json']:
                raise ValueError('Immutable version collision')
            for item in active:
                item['is_active'] = False
            if existing:
                existing[0]['is_active'] = row['is_active']
            else:
                versions.append(copy.deepcopy(row))
    monkeypatch.setattr(service, 'commit_pipeline_activation', commit)
    monkeypatch.setattr(importlib.import_module('fabricops_kit.activated_pipeline.set_pipeline_active'), 'commit_pipeline_activation', commit)
    monkeypatch.setattr(importlib.import_module('fabricops_kit.activated_pipeline.set_pipeline_active'), 'metadata_records', records)
    def candidate(roles=('source',), **kwargs):
        plan = make(roles=roles, executable=digest)
        identities = json.loads(plan.participants_json)
        frozen = {}
        for key, item in identities.items():
            payload = {'contract': {'contract_id':'contract-'+key,'contract_version':1,'status':'frozen'},
                       'table': {'table_id':key,'columns':[], 'processing':{'load_strategy':'overwrite'},
                                 'writer': {'notebook_id':'notebook','notebook_name':'pipeline'}}, 'guardrails': []}
            contract = {'contract_id':'contract-'+key,'contract_version':1,'status':'frozen','table_id':key,
                        'environment_name':'canary', 'contract_payload_json':pipeline.canonical_candidate_json(payload)}
            frozen[key] = contract
            if contract not in contracts:
                contracts.append(contract)
        plan = replace(plan, contracts_json=pipeline.canonical_candidate_json(frozen), evidence={})
        pipeline.persist_pipeline_run(plan)
        for index in range(len(roles)):
            operation(plan,index)
        run = finalize_pipeline(plan)
        run.update(_workspace_id='workspace', _notebook_id='notebook')
        saved[plan.plan_id] = run
        return plan, run
    def approve(run, version='1', **kwargs):
        return activate_pipeline(testing_run_id=run['run_id'], candidate_fingerprint=run['candidate_fingerprint'],
            pipeline_name='Orders', pipeline_version=version, agreement_id='agreement', agreement_version='1.0',
            executable_path=str(executable), governance_confirmed=True, context=context, **kwargs)
    def deploy(row, roles=('source',)):
        destination = tmp_path / row['activated_pipeline_id']
        package_activated_pipeline(row['activated_pipeline_id'], destination=destination, executable_path=executable, context=context)
        sources = [{'store':'Bronze','schema':'physical','table_name':f'table{i}','logical_id':f'asset{i}'} for i,role in enumerate(roles) if role=='source']
        targets = [{'store':'Silver','schema':'physical','table_name':f'table{i}','logical_id':f'asset{i}'} for i,role in enumerate(roles) if role=='target']
        verify_pipeline_deployment(deployment_path=destination, authority_environment='canary', sources=sources,targets=targets,context=context)
        return destination, sources, targets
    return SimpleNamespace(candidate=candidate, approve=approve, deploy=deploy, context=context, executable=executable,
        versions=versions, contracts=contracts, rules=rules, saved=saved, operation=operation, agreement=agreement, digest=digest)


def test_approval_requires_complete_testing_and_exact_candidate(approved_runtime):
    state=approved_runtime
    _,run=state.candidate()
    for field,value in [('status','incomplete'),('status','failed'),('execution_mode','bootstrap'),('completed_at',None),('candidate_fingerprint','changed')]:
        original=run[field];run[field]=value
        with pytest.raises(ValueError): state.approve(run)
        run[field]=original
    row=state.approve(run)
    assert row['is_active'] and row['testing_run_id']==run['run_id']
    assert service.validate_manifest(row)['candidate']==json.loads(run['candidate_json'])


def test_missing_operations_and_blocking_diagnostics_cannot_authorize(approved_runtime):
    state=approved_runtime
    _,run=state.candidate(('source','target'))
    original=run['operation_summary_json']
    summary=json.loads(original);summary['operations'].pop('target:asset1')
    run['operation_summary_json']=pipeline.canonical_candidate_json(summary)
    with pytest.raises(ValueError,match='operation evidence'): state.approve(run)
    run['operation_summary_json']=original
    state.rules.append({'run_id':run['run_id'],'execution_type':'testing','can_continue':False})
    with pytest.raises(ValueError,match='blocking'): state.approve(run)


@pytest.mark.parametrize('change',['code','contract','configuration','dependency','agreement'])
def test_changed_requirements_cannot_activate(approved_runtime,change):
    state=approved_runtime
    _,run=state.candidate()
    if change=='code': state.executable.write_text('changed')
    if change=='contract': state.contracts[0]['contract_payload_json']='{}'
    if change=='configuration':
        summary=json.loads(run['operation_summary_json']);summary['operations']['source:asset0']['configuration']={'changed':True}
        run['operation_summary_json']=pipeline.canonical_candidate_json(summary)
    if change=='dependency':
        candidate=json.loads(run['candidate_json']);candidate['dependencies']={'missing-library':{'required':'1.0','observed':'1.0'}}
        run['candidate_json']=pipeline.canonical_candidate_json(candidate);run['candidate_fingerprint']=service.manifest_digest(candidate)
    if change=='agreement': state.agreement['agreement_version']='2.0'
    with pytest.raises(ValueError): state.approve(run)


def test_headless_service_requires_explicit_confirmation(approved_runtime):
    state=approved_runtime
    _,run=state.candidate()
    with pytest.raises(ValueError,match='confirmation'):
        activate_pipeline(testing_run_id=run['run_id'],candidate_fingerprint=run['candidate_fingerprint'],pipeline_name='Orders',pipeline_version='1',
            agreement_id='agreement',agreement_version='1.0',executable_path=state.executable,context=state.context)


def test_concurrent_activation_and_explicit_switching(approved_runtime):
    state=approved_runtime
    _,run=state.candidate()
    def approve(version):
        try: return state.approve(run,version)
        except ValueError: return None
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(approve,['1','2']))
    assert sum(result is not None for result in results)==1
    assert sum(row['is_active'] for row in state.versions)==1
    active=next(row for row in state.versions if row['is_active'])
    second=state.approve(run,'3',expected_active_id=active['activated_pipeline_id'])
    assert sum(row['is_active'] for row in state.versions)==1
    set_pipeline_active(second['activated_pipeline_id'],active=False,expected_active_id=second['activated_pipeline_id'],governance_confirmed=True,context=state.context)
    assert not any(row['is_active'] for row in state.versions)
    set_pipeline_active(active['activated_pipeline_id'],active=True,expected_active_id=None,governance_confirmed=True,context=state.context)
    assert sum(row['is_active'] for row in state.versions)==1
    assert state.approve(run,active['pipeline_version'],expected_active_id=active['activated_pipeline_id'])['activated_pipeline_id']==active['activated_pipeline_id']


def test_read_only_repeated_unattended_live_uses_saved_selection(approved_runtime):
    state=approved_runtime
    _,run=state.candidate()
    row=state.approve(run)
    root,sources,targets=state.deploy(row)
    params=dict(execution_mode='live',pipeline_id='orders',deployment_path=root,sources=sources,targets=targets,configuration={},context=state.context)
    with pytest.raises(ValueError,match='No saved'): setup_pipeline(**params)
    first=setup_pipeline(**params,activated_pipeline_id=row['activated_pipeline_id'])
    state.operation(first,0)
    result=finalize_pipeline(first)
    assert result['status']=='succeeded' and result['activated_pipeline_id']==row['activated_pipeline_id']
    second=setup_pipeline(**params)
    state.operation(second,0)
    assert finalize_pipeline(second)['status']=='succeeded' and first.plan_id!=second.plan_id
    with pytest.raises(ValueError,match='rejects manual'): setup_pipeline(**params,selections={})


@pytest.mark.parametrize('change',['manifest','artifact','binding','approval','selection','configuration','actual_notebook','dependency'])
def test_live_fails_closed_without_bootstrap_fallback(approved_runtime,monkeypatch,change):
    state=approved_runtime
    _,run=state.candidate()
    row=state.approve(run)
    root,sources,targets=state.deploy(row)
    params=dict(execution_mode='live',pipeline_id='orders',deployment_path=root,sources=sources,targets=targets,configuration={},context=state.context)
    plan=setup_pipeline(**params,activated_pipeline_id=row['activated_pipeline_id'])
    if change=='manifest':
        body=json.loads((root/'approved.json').read_text());body['manifest_json']=body['manifest_json'].replace('Orders','Tampered');(root/'approved.json').write_text(json.dumps(body))
    if change=='artifact': (root/'executable.bin').write_bytes(b'changed')
    if change=='binding': state.context['workspace_id']='elsewhere'
    if change=='approval': state.versions[0]['is_active']=False
    if change=='selection': next(root.glob('*.selection.json')).write_text('{"activated_pipeline_id":"other"}')
    if change=='actual_notebook': monkeypatch.setattr('fabricops_kit.pipeline.shared.deployed_notebook_fingerprint',lambda runtime:'f'*64)
    if change=='dependency': monkeypatch.setattr('importlib.metadata.version',lambda name:'changed')
    with pytest.raises(ValueError):
        if change=='configuration': state.operation(plan,0,read_mode='incremental')
        else: setup_pipeline(**params)


def test_packaging_is_deterministic_and_activation_does_not_deploy(approved_runtime):
    state=approved_runtime
    _,run=state.candidate(('source','source','target','target'))
    row=state.approve(run)
    root=state.executable.parent/'bundle'
    assert not root.exists()
    package_activated_pipeline(row['activated_pipeline_id'],destination=root,executable_path=state.executable,context=state.context)
    before={path.name:path.read_bytes() for path in root.iterdir()}
    package_activated_pipeline(row['activated_pipeline_id'],destination=root,executable_path=state.executable,context=state.context)
    assert before=={path.name:path.read_bytes() for path in root.iterdir()}
    assert set(before)=={'approved.json','executable.bin'}


def test_external_transformation_configuration_is_part_of_candidate_identity(approved_runtime):
    state=approved_runtime
    plan,run=state.candidate()
    changed=replace(plan,configuration_json='{"threshold":10}')
    assert pipeline.pipeline_candidate(changed)[1]!=run['candidate_fingerprint']
    row=state.approve(run)
    root,sources,targets=state.deploy(row)
    with pytest.raises(ValueError,match='identity mismatch'):
        setup_pipeline(execution_mode='live',pipeline_id='orders',deployment_path=root,sources=sources,targets=targets,
            configuration={'threshold':10},activated_pipeline_id=row['activated_pipeline_id'],context=state.context)


def test_notebook_identity_excludes_bindings_and_outputs_but_covers_code():
    original={'cells':[{'cell_type':'code','source':['print(1)'],'outputs':[{'text':'before'}],'execution_count':1}], 'metadata':{'lakehouse_id':'dev'}}
    renamed=copy.deepcopy(original);renamed['metadata']={'lakehouse_id':'prod','notebook_name':'renamed'};renamed['cells'][0]['outputs']=[]
    assert pipeline.notebook_executable_fingerprint(json.dumps(original))==pipeline.notebook_executable_fingerprint(json.dumps(renamed))
    renamed['cells'][0]['source']=['print(2)']
    assert pipeline.notebook_executable_fingerprint(json.dumps(original))!=pipeline.notebook_executable_fingerprint(json.dumps(renamed))
    renamed['cells'][0]['source']=['%run undeclared_helper']
    with pytest.raises(ValueError,match='helper notebooks'):
        pipeline.notebook_executable_fingerprint(json.dumps(renamed))


def test_actual_fabric_notebook_definition_is_observed(monkeypatch):
    import base64
    import sys
    content=b'{"cells":[{"cell_type":"code","source":["print(1)"]}]}'
    payload={'definition':{'parts':[{'path':'notebook-content.ipynb','payloadType':'InlineBase64','payload':base64.b64encode(content).decode()}]}}
    monkeypatch.setitem(sys.modules,'notebookutils',SimpleNamespace(credentials=SimpleNamespace(getToken=lambda audience:'test-token')))
    calls=[]
    class Response:
        status=200
        headers={}
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self):return json.dumps(payload).encode()
    def transport(request,timeout):
        calls.append(request)
        return Response()
    monkeypatch.setattr('urllib.request.urlopen',transport)
    result=pipeline.deployed_notebook_fingerprint({'workspace_id':'00000000-0000-0000-0000-000000000001','notebook_id':'00000000-0000-0000-0000-000000000002'})
    assert result==pipeline.notebook_executable_fingerprint(content)
    assert calls[0].method=='POST' and calls[0].full_url.endswith('getDefinition?format=ipynb')


def test_multiple_inputs_outputs_live_records_the_approved_version(approved_runtime):
    state=approved_runtime
    roles=('source','source','target','target')
    _,run=state.candidate(roles)
    row=state.approve(run)
    root,sources,targets=state.deploy(row,roles)
    live=setup_pipeline(execution_mode='live',pipeline_id='orders',deployment_path=root,sources=sources,targets=targets,
        configuration={},activated_pipeline_id=row['activated_pipeline_id'],context=state.context)
    for index in range(len(roles)):
        state.operation(live,index)
    result=finalize_pipeline(live)
    assert result['status']=='succeeded' and result['activated_pipeline_id']==row['activated_pipeline_id']
    assert len(json.loads(result['operation_summary_json'])['operations'])==4


def test_physical_environment_copies_keep_portable_executable_identity(approved_runtime,monkeypatch):
    state=approved_runtime
    _,run=state.candidate()
    row=state.approve(run)
    root,sources,targets=state.deploy(row)
    state.context.update(env='production',notebook_id='cloned-notebook')
    # The approved definition remains immutable and references its exact source contract.
    (root/'deployment.json').unlink()
    monkeypatch.setattr(pipeline,'resolve_physical_table_identity',lambda config,env,**kw:{**kw,'table_id':'cloned-'+kw['table_name']})
    verify_pipeline_deployment(deployment_path=root,authority_environment='canary',sources=sources,targets=targets,context=state.context)
    live=setup_pipeline(execution_mode='live',pipeline_id='orders',deployment_path=root,sources=sources,targets=targets,
        configuration={},activated_pipeline_id=row['activated_pipeline_id'],context=state.context)
    assert set(json.loads(live.participants_json))=={'cloned-table0'}
    assert json.loads(live.contracts_json)['cloned-table0']['table_id']=='table0'


def test_native_activation_transport_uses_one_serializable_guarded_merge(monkeypatch):
    import sys
    from unittest.mock import Mock
    original=service.commit_pipeline_activation
    spark=Mock()
    frame=Mock();spark.createDataFrame.return_value=frame
    delta=Mock()
    delta.alias.return_value=delta
    delta.merge.return_value=delta
    delta.whenMatchedUpdate.return_value=delta
    delta.whenNotMatchedInsertAll.return_value=delta
    delta.whenNotMatchedBySourceUpdate.return_value=delta
    monkeypatch.setitem(sys.modules,'delta.tables',SimpleNamespace(DeltaTable=SimpleNamespace(forPath=lambda *a:delta)))
    monkeypatch.setattr(service,'get_spark_session',lambda supplied=None:spark)
    monkeypatch.setattr(service,'resolve_fabric_context',lambda context=None:({},'dev',{}))
    monkeypatch.setattr(service,'resolve_configured_lakehouse_table',lambda *a,**kw:('Metadata',service.ACTIVATED_TABLE,'governance','configured-path'))
    row={'activated_pipeline_id':'version','pipeline_id':'orders','pipeline_version':'1','is_active':True,'manifest_json':'{}'}
    original(row,expected_active_id='previous',context={})
    assert 'Serializable' in spark.sql.call_args.args[0]
    assert 'target.pipeline_id' in delta.merge.call_args.args[1]
    assert 'target.pipeline_version' in delta.merge.call_args.args[1]
    assert set(delta.whenMatchedUpdate.call_args.kwargs['set'])=={'is_active'}
    conditional=delta.whenNotMatchedBySourceUpdate.call_args.kwargs
    assert 'target.is_active = true' in conditional['condition']
    assert 'previous' in conditional['set']['is_active'] and 'raise_error' in conditional['set']['is_active']
    delta.execute.assert_called_once()


def test_saved_selection_does_not_follow_a_new_active_version(approved_runtime):
    state=approved_runtime
    _,run=state.candidate()
    first=state.approve(run)
    root,sources,targets=state.deploy(first)
    parameters=dict(execution_mode='live',pipeline_id='orders',deployment_path=root,sources=sources,targets=targets,configuration={},context=state.context)
    setup_pipeline(**parameters,activated_pipeline_id=first['activated_pipeline_id'])
    selection=next(root.glob('*.selection.json')).read_bytes()
    state.approve(run,'2',expected_active_id=first['activated_pipeline_id'])
    with pytest.raises(ValueError,match='inactive'):setup_pipeline(**parameters)
    assert next(root.glob('*.selection.json')).read_bytes()==selection


def test_bootstrap_cannot_bypass_existing_approval_in_another_environment(approved_runtime,monkeypatch):
    state=approved_runtime
    _,run=state.candidate()
    state.approve(run)
    # Frozen rows live in the Testing environment; Production has none locally.
    from tests.unit.test_data_contract_resolution import RecordingFrame
    monkeypatch.setattr(pipeline,'read_lakehouse_table',lambda name,**kw: RecordingFrame(state.versions if name=='METADATA_ACTIVATED_PIPELINE' else []))
    state.context['env']='production'
    with pytest.raises(ValueError,match='Bootstrap cannot bypass'):
        setup_pipeline(pipeline_id='orders',sources=[{'store':'Bronze','schema':'physical','table_name':'table0'}],targets=[],context=state.context)
    state.versions[0]['is_active']=False
    with pytest.raises(ValueError,match='Bootstrap cannot bypass'):
        setup_pipeline(pipeline_id='orders',sources=[{'store':'Bronze','schema':'physical','table_name':'table0'}],targets=[],context=state.context)


def test_live_rejects_multiple_active_metadata_versions(approved_runtime):
    state=approved_runtime
    _,run=state.candidate()
    first=state.approve(run)
    second=state.approve(run,'2',expected_active_id=first['activated_pipeline_id'])
    state.versions[0]['is_active']=True
    with pytest.raises(ValueError,match='multiple active'):
        service.activation_version(second['activated_pipeline_id'],context=state.context)


def test_missing_stage_cannot_be_replaced_by_success_status(approved_runtime):
    state=approved_runtime
    _,run=state.candidate()
    summary=json.loads(run['operation_summary_json'])
    summary['operations']['source:asset0']['stages']=[]
    run['operation_summary_json']=pipeline.canonical_candidate_json(summary)
    with pytest.raises(ValueError,match='operation evidence'):
        state.approve(run)


def test_stale_switch_after_explicit_deactivation_is_rejected(approved_runtime):
    state=approved_runtime
    _,run=state.candidate()
    active=state.approve(run)
    set_pipeline_active(active['activated_pipeline_id'],active=False,expected_active_id=active['activated_pipeline_id'],governance_confirmed=True,context=state.context)
    with pytest.raises(ValueError,match='changed|switching'):
        state.approve(run,'2',expected_active_id=active['activated_pipeline_id'])


@pytest.mark.parametrize('failure', ['changed', 'unavailable'])
@pytest.mark.parametrize('already_bound', [False, True])
def test_deployment_verification_checks_actual_fabric_notebook_before_binding(approved_runtime, monkeypatch, failure, already_bound):
    state = approved_runtime
    _, run = state.candidate()
    row = state.approve(run)
    destination = state.executable.parent / 'unverified'
    package_activated_pipeline(row['activated_pipeline_id'], destination=destination,
        executable_path=state.executable, context=state.context)
    sources = [{'store':'Bronze', 'schema':'physical', 'table_name':'table0', 'logical_id':'asset0'}]
    if already_bound:
        verify_pipeline_deployment(deployment_path=destination, authority_environment='canary',
            sources=sources, targets=[], context=state.context)
    binding_path = destination / 'deployment.json'
    before = binding_path.read_bytes() if already_bound else None
    calls = []
    def observe(runtime):
        calls.append(runtime['notebook_id'])
        if failure == 'unavailable':
            raise RuntimeError('Fabric notebook export unavailable')
        return 'f' * 64
    monkeypatch.setattr(pipeline, 'deployed_notebook_fingerprint', observe)
    with pytest.raises((ValueError, RuntimeError), match='Fabric notebook'):
        verify_pipeline_deployment(deployment_path=destination, authority_environment='canary',
            sources=sources, targets=[], context=state.context)
    assert calls == ['notebook']
    assert (binding_path.read_bytes() if binding_path.exists() else None) == before
    assert not list(destination.glob('*.selection.json'))


@pytest.mark.parametrize('configuration', [{'schema':'changed'}, {'transform':[{'table_name':'changed'}]}])
def test_live_rejects_changed_project_fields_named_like_bindings(approved_runtime, configuration):
    state = approved_runtime
    _, run = state.candidate()
    row = state.approve(run)
    root, sources, targets = state.deploy(row)
    with pytest.raises(ValueError, match='identity mismatch'):
        setup_pipeline(execution_mode='live', pipeline_id='orders', deployment_path=root,
            sources=sources, targets=targets, configuration=configuration,
            activated_pipeline_id=row['activated_pipeline_id'], context=state.context)
