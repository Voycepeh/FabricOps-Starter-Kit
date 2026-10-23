"""Execution isolation, publication policy and conservative notebook boundaries."""
# ruff: noqa: D103
from contextvars import Context
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import Mock
import importlib
import json

import pytest

from fabricops_kit import setup_pipeline, orchestrate_read, orchestrate_write
from fabricops_kit.pipeline import shared


@pytest.fixture
def runtime(monkeypatch):
    """Keep session, journal and orchestrators real; replace physical runtime boundaries."""
    monkeypatch.setattr(importlib.import_module("fabricops_kit.pipeline.setup_pipeline"), "initialize_notebook",
                        lambda: SimpleNamespace(notebook_name="02_pipeline"))
    config = {}
    spark = SimpleNamespace(conf=SimpleNamespace(get=lambda key: 'test'))
    monkeypatch.setattr(shared, 'resolve_fabric_context', lambda context=None: (config, 'dev', context or {'config': config, 'env': 'dev'}))
    monkeypatch.setattr(shared, 'get_spark_session', lambda *args: spark)
    monkeypatch.setattr(shared, 'build_runtime_audit_fields', lambda **kwargs: {})
    monkeypatch.setattr(shared, 'resolve_physical_table_identity', lambda config, env, **kwargs: {**kwargs, 'table_id': kwargs['table_name']})
    monkeypatch.setattr(shared, 'pipeline_physical_bindings', lambda identities, **kwargs: {key: {'store': value['store'], 'table_name': value['table_name']} for key, value in identities.items()})
    monkeypatch.setattr(shared, 'load_table_guardrail_rules', lambda *args, **kwargs: [])
    monkeypatch.setattr(shared, 'read_lakehouse_table', Mock(side_effect=AssertionError('unexpected metadata read')))
    writes = Mock(side_effect=AssertionError('Test metadata mutation'))
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', writes)
    monkeypatch.setattr(shared, 'write_lakehouse_table', writes)
    import IPython
    monkeypatch.setattr(IPython, 'get_ipython', lambda: None)
    read = importlib.import_module('fabricops_kit.pipeline.orchestrate_read')
    write = importlib.import_module('fabricops_kit.pipeline.orchestrate_write')
    for module in [read, write]:
        monkeypatch.setattr(module, 'resolve_table_id', lambda **kwargs: kwargs['table_name'])
        monkeypatch.setattr(module, 'schedule_table_profiling', lambda *args, **kwargs: {'row_count': 2})
    frame = SimpleNamespace(columns=['id'])
    monkeypatch.setattr(read, 'pipeline_read', lambda **kwargs: {'dataframe': frame, 'table_id': kwargs['table_name']})
    publication = Mock(return_value={'published': False, 'table_id': 'target', 'status': 'passed'})
    monkeypatch.setattr(write, 'pipeline_write', publication)
    token = shared._ACTIVE_PIPELINE.set(None)
    yield SimpleNamespace(spark=spark, writes=writes, read=read, write=write, frame=frame, publication=publication)
    session = shared._ACTIVE_PIPELINE.get()
    if session is not None:
        session.close()
    shared._ACTIVE_PIPELINE.reset(token)


@pytest.mark.parametrize('mode', ['test', 'live', 'Testing', '', None, 'TEST'])
def test_exact_mode_validation(runtime, mode):
    with pytest.raises(ValueError, match='exactly Test or Live'):
        setup_pipeline(pipeline_id='orders', pipeline_mode=mode)


def test_only_pipeline_identity_and_mode_are_setup_arguments(runtime):
    import inspect
    assert list(inspect.signature(setup_pipeline).parameters) == ['pipeline_id', 'pipeline_mode']
    with pytest.raises(TypeError):
        setup_pipeline(pipeline_id='orders', pipeline_mode='Test', testing_writes=True)


def test_headless_test_without_notebook_identity_or_metadata_writes(runtime):
    session = setup_pipeline(pipeline_id='orders', pipeline_mode='Test')
    source = orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    result = orchestrate_write(source['dataframe'], store='Gold', schema='demo', table_name='summary', write_mode='overwrite')
    assert session.plan.notebook_id == ''
    assert result['published'] is False
    assert runtime.publication.call_args.kwargs['context']['execution_plan'].permits_persistence is False
    assert runtime.publication.call_args.kwargs['source_table_ids'] == ['orders']
    runtime.writes.assert_not_called()
    session.close()
    assert session.plan.run_result['status'] == 'incomplete'
    assert not session.sources


def test_multi_read_multi_write_sources_and_no_early_success(runtime):
    session = setup_pipeline(pipeline_id='multi', pipeline_mode='Test')
    for name in ['orders', 'products']:
        orchestrate_read(store='Bronze', schema='demo', table_name=name)
    for name in ['summary', 'history']:
        result = orchestrate_write(runtime.frame, store='Gold', schema='demo', table_name=name, write_mode='overwrite')
        assert result['source_association'] == 'pipeline_participation'
        assert runtime.publication.call_args.kwargs['source_table_ids'] == ['orders', 'products']
        assert not session.plan.evidence['sealed']
    session.cell_completed(SimpleNamespace(error_in_exec=None, error_before_exec=None))
    assert not session.plan.evidence['sealed']
    assert len(session.plan.evidence['operations']) == 4


def test_transformation_failure_and_repeated_setup_clear_sources(runtime):
    first = setup_pipeline(pipeline_id='orders', pipeline_mode='Test')
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    first.cell_completed(SimpleNamespace(error_in_exec=ValueError('bad transform')))
    assert first.closed and not first.sources
    assert first.plan.run_result['status'] == 'failed'
    next_run = setup_pipeline(pipeline_id='orders', pipeline_mode='Test')
    assert next_run.plan.plan_id != first.plan.plan_id and not next_run.sources
    with pytest.raises(RuntimeError, match='closed'):
        first.operation_plan('source', {})


def test_operation_failure_seals_run_and_clears_reads(runtime, monkeypatch):
    session = setup_pipeline(pipeline_id='orders', pipeline_mode='Test')
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    monkeypatch.setattr(runtime.write, 'pipeline_write', Mock(side_effect=RuntimeError('failed write')))
    with pytest.raises(RuntimeError):
        orchestrate_write(runtime.frame, store='Gold', schema='demo', table_name='summary', write_mode='overwrite')
    assert session.closed and not session.sources
    assert session.plan.run_result['status'] == 'failed'


def test_contexts_isolate_same_pipeline_name(runtime):
    contexts = [Context(), Context()]
    sessions = [context.run(setup_pipeline, pipeline_id='same', pipeline_mode='Test') for context in contexts]
    try:
        for index, context in enumerate(contexts):
            context.run(orchestrate_read, store='Bronze', schema='demo', table_name=f'source{index}')
        assert sessions[0].plan.plan_id != sessions[1].plan.plan_id
        assert [source['table_id'] for source in sessions[0].sources] == ['source0']
        assert [source['table_id'] for source in sessions[1].sources] == ['source1']
    finally:
        for context, session in zip(contexts, sessions):
            context.run(session.close)


def test_live_resolves_only_approved_manifest(runtime, monkeypatch):
    activation = importlib.import_module('fabricops_kit.activated_pipeline.shared')
    builder = Mock(side_effect=ValueError('No approved pipeline configuration'))
    monkeypatch.setattr(activation, 'build_live_pipeline_plan', builder)
    with pytest.raises(ValueError, match='No approved'):
        setup_pipeline(pipeline_id='orders', pipeline_mode='Live')
    assert set(builder.call_args.kwargs) == {'pipeline_id', 'context', 'spark_session'}


def test_contract_selection_freezes_at_first_operation(runtime, monkeypatch):
    session = setup_pipeline(pipeline_id='orders', pipeline_mode='Test')
    row = {'table_id': 'orders', 'contract_id': 'frozen', 'contract_version': 2}
    session.frozen_rows = [row]
    session.select_contract('orders', 'frozen', 2)
    payload = {'contract': {'contract_id': 'frozen', 'contract_version': 2, 'status': 'frozen'},
               'table': {'table_id': 'orders', 'columns': []}, 'guardrails': [], 'enrichment': {'table': [], 'columns': []}}
    monkeypatch.setattr(shared, 'resolve_data_contract_version', lambda *args, **kwargs: {
        **row, 'contract_payload_json': json.dumps(payload), 'contract_payload': payload})
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    assert json.loads(session.plan.contracts_json)['orders']['contract_version'] == 2
    with pytest.raises(RuntimeError, match='locked'):
        session.select_contract('orders', no_contract=True)


def test_interactive_contract_controls_and_failure_event(runtime, monkeypatch):
    """Render native widgets and exercise frozen selection and per-cell failure cleanup."""
    import IPython
    from IPython import display as ip
    from tests.unit.test_setup_pipeline import _row
    shell = SimpleNamespace(events=SimpleNamespace(register=Mock(), unregister=Mock()))
    monkeypatch.setattr(IPython, 'get_ipython', lambda: shell)
    displayed = Mock()
    monkeypatch.setattr(ip, 'display', displayed)
    monkeypatch.setattr(shared, 'read_lakehouse_table', lambda *args, **kwargs: SimpleNamespace(collect=lambda: [_row()]))
    session = setup_pipeline(pipeline_id='interactive', pipeline_mode='Test')
    assert any(hasattr(call.args[0], "children") for call in displayed.call_args_list)
    assert '#a4262c' in session.report.value and 'Test' in session.report.value
    session.controls[0].value = 'contract-source\n1'
    assert session.choices['source'] == {'contract_id': 'contract-source', 'contract_version': 1}
    shell.events.register.assert_called_once_with('post_run_cell', session.cell_completed)
    session.cell_completed(SimpleNamespace(error_before_exec=SyntaxError('bad cell')))
    assert session.closed and 'failed' in session.report.value
    shell.events.unregister.assert_called_once_with('post_run_cell', session.cell_completed)


def test_concurrent_async_tasks_do_not_close_an_inherited_execution(runtime):
    import asyncio
    async def scenario():
        parent = setup_pipeline(pipeline_id='same', pipeline_mode='Test')
        async def child(name):
            with pytest.raises(RuntimeError, match='another task'):
                shared.current_pipeline_session()
            session = setup_pipeline(pipeline_id='same', pipeline_mode='Test')
            await asyncio.sleep(0)
            orchestrate_read(store='Bronze', schema='demo', table_name=name)
            assert [row['table_id'] for row in session.sources] == [name]
            assert not parent.closed
            session.close()
            return session.plan.plan_id
        children = await asyncio.gather(child('a'), child('b'))
        assert len(set(children + [parent.plan.plan_id])) == 3
        assert shared.current_pipeline_session() is parent and not parent.closed
        parent.close()
    asyncio.run(scenario())


def test_invalid_participant_closes_execution_before_operation_journal(runtime, monkeypatch):
    session = setup_pipeline(pipeline_id='invalid', pipeline_mode='Test')
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    monkeypatch.setattr(shared, 'resolve_physical_table_identity', Mock(side_effect=ValueError('invalid destination')))
    with pytest.raises(ValueError, match='invalid destination'):
        orchestrate_read(store='Bronze', schema='demo', table_name='invalid')
    assert session.closed and not session.sources
    assert session.plan.run_result['status'] == 'failed'


def test_headless_selection_resolves_and_pins_exact_frozen_payload(runtime, monkeypatch):
    session = setup_pipeline(pipeline_id='headless', pipeline_mode='Test')
    payload = {'contract': {'contract_id':'frozen', 'contract_version':1, 'status':'frozen'},
               'table': {'table_id':'orders', 'columns':[]}, 'guardrails':[], 'enrichment':{'table':[], 'columns':[]}}
    row = {'table_id':'orders', 'contract_id':'frozen', 'contract_version':1,
           'contract_payload_json':json.dumps(payload), 'contract_payload':payload}
    resolver = Mock(return_value=row)
    monkeypatch.setattr(shared, 'resolve_data_contract_version', resolver)
    session.select_contract('orders', 'frozen', 1)
    assert resolver.call_count == 1 and session.selected_contracts['orders']['contract_payload_json'] == row['contract_payload_json']
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    assert json.loads(session.plan.contracts_json)['orders']['contract_version'] == 1


def test_changed_frozen_payload_is_rejected_before_read(runtime, monkeypatch):
    session = setup_pipeline(pipeline_id='changed-contract', pipeline_mode='Test')
    row = {'table_id':'orders', 'contract_id':'frozen', 'contract_version':1, 'contract_payload_json':'original'}
    monkeypatch.setattr(shared, 'resolve_data_contract_version', Mock(return_value=row))
    session.select_contract('orders', 'frozen', 1)
    monkeypatch.setattr(shared, 'resolve_data_contract_version', Mock(return_value={**row,'contract_payload_json':'changed'}))
    with pytest.raises(RuntimeError, match='Frozen contract changed'):
        orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    assert session.closed and session.plan.run_result['status'] == 'failed'


def test_headless_setup_works_without_optional_ipython(runtime, monkeypatch):
    import builtins
    original = builtins.__import__

    def without_ipython(name, *args, **kwargs):
        if name == 'IPython':
            raise ModuleNotFoundError("No module named 'IPython'", name='IPython')
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, '__import__', without_ipython)
    session = setup_pipeline(pipeline_id='headless', pipeline_mode='Test')
    assert shared.current_pipeline_session() is session
    assert session.shell is None


def test_closed_sessions_release_shutdown_callback(runtime, monkeypatch):
    import atexit
    register, unregister = Mock(), Mock()
    monkeypatch.setattr(atexit, 'register', register)
    monkeypatch.setattr(atexit, 'unregister', unregister)
    session = setup_pipeline(pipeline_id='orders', pipeline_mode='Test')
    register.assert_called_once_with(session.close)
    session.close()
    unregister.assert_called_once_with(session.close)


def test_finalization_completes_and_publishes_only_run_metadata(runtime, monkeypatch):
    from fabricops_kit import finalize_pipeline
    committed = []
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', lambda plan, row, **kwargs: committed.append(dict(row)))
    session = setup_pipeline(pipeline_id='orders', pipeline_mode='Test')
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    assert not committed
    result = finalize_pipeline(session)
    assert result['status'] == 'ungoverned_completed'
    assert json.loads(result['operation_summary_json'])['boundary_completed'] is True
    assert session.closed and not session.sources
    assert len(committed) == 1
    assert finalize_pipeline(session) == result and len(committed) == 1
    runtime.writes.assert_not_called()


def test_finalization_records_caught_failure_and_releases_live_reservation(runtime, monkeypatch):
    from fabricops_kit import finalize_pipeline
    activation = importlib.import_module('fabricops_kit.activated_pipeline.shared')
    session = setup_pipeline(pipeline_id='orders', pipeline_mode='Test')
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    session.plan = replace(session.plan, execution_mode='live')
    session.plan.evidence['lease_token'] = session.plan.plan_id
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', Mock())
    release = Mock(side_effect=lambda plan, **kwargs: plan.evidence.pop('lease_token'))
    monkeypatch.setattr(activation, 'release_pipeline_lease', release)
    result = finalize_pipeline(session, failed=True)
    assert result['status'] == 'failed'
    assert json.loads(result['operation_summary_json'])['boundary_completed'] is False
    release.assert_called_once()


def test_finalization_retains_all_diagnostics_and_retries_without_duplicates(runtime, monkeypatch):
    from fabricops_kit import finalize_pipeline
    import sys
    session = setup_pipeline(pipeline_id='orders', pipeline_mode='Test')
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    session.plan.evidence['guardrail_history'] = [{'guardrail_result_id': 'first', 'run_id': session.plan.plan_id}]
    session.plan.results.clear()  # The per-operation lookup may discard earlier results.
    stored = {}
    attempts = []

    class Frame:
        def alias(self, name):
            return self

    class Delta:
        def alias(self, name):
            return self
        def merge(self, frame, condition):
            assert condition == 'target.guardrail_result_id = source.guardrail_result_id'
            return self
        def whenNotMatchedInsertAll(self):
            return self
        def execute(self):
            stored['first'] = True
            attempts.append(True)
            if len(attempts) == 1:
                raise OSError('lost acknowledgement')

    runtime.spark.createDataFrame = Mock(return_value=Frame())
    monkeypatch.setitem(sys.modules, 'delta.tables', SimpleNamespace(DeltaTable=SimpleNamespace(forPath=lambda *args: Delta())))
    monkeypatch.setattr(shared, 'resolve_configured_lakehouse_table', lambda *args, **kwargs: (None, None, None, 'configured/results'))
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', Mock())
    with pytest.raises(OSError, match='lost acknowledgement'):
        finalize_pipeline(session)
    shared._merge_pipeline_run_row.assert_not_called()
    assert session.closed and not session.plan.permits_persistence
    result = finalize_pipeline(session)
    assert len(stored) == 1 and result['status'] == 'ungoverned_completed'
    shared._merge_pipeline_run_row.assert_called_once()
    rows = runtime.spark.createDataFrame.call_args.args[0]
    assert rows[0]['guardrail_result_id'] == 'first'


def test_active_finalization_cannot_be_claimed_from_another_task(runtime):
    from fabricops_kit import finalize_pipeline
    import asyncio

    async def scenario():
        session = setup_pipeline(pipeline_id='orders', pipeline_mode='Test')
        async def child():
            with pytest.raises(RuntimeError, match='another task'):
                finalize_pipeline(session)
        await asyncio.create_task(child())
        assert not session.closed
        session.close()

    asyncio.run(scenario())


def test_finalized_governed_test_can_build_new_activation_manifest(runtime, monkeypatch):
    from fabricops_kit import finalize_pipeline
    from datetime import date, timedelta
    activation = importlib.import_module('fabricops_kit.activated_pipeline.shared')
    session = setup_pipeline(pipeline_id='orders', pipeline_mode='Test')
    payload = {'contract': {'contract_id': 'frozen', 'contract_version': 1, 'status': 'frozen'},
               'table': {'table_id': 'orders', 'columns': []}, 'guardrails': [],
               'enrichment': {'table': [], 'columns': []}}
    row = {'table_id': 'orders', 'contract_id': 'frozen', 'contract_version': 1,
           'status': 'frozen', 'environment_name': 'dev',
           'contract_payload_json': json.dumps(payload), 'contract_payload': payload}
    monkeypatch.setattr(shared, 'resolve_data_contract_version', Mock(return_value=row))
    session.select_contract('orders', 'frozen', 1)
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    committed = []
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', lambda plan, row, **kwargs: committed.append(dict(row)))
    result = finalize_pipeline(session)
    assert result['status'] == 'succeeded' and committed == [result]
    agreement = {'agreement_id': 'agreement', 'agreement_version': '1.0.0',
                 'start_date': date.today().isoformat(), 'expiry_date': (date.today() + timedelta(days=30)).isoformat()}
    records = {'METADATA_PIPELINE_RUN': committed, 'METADATA_DATA_CONTRACT': [row],
               'METADATA_GUARDRAIL_RESULTS': [], 'METADATA_DATA_AGREEMENT': [agreement]}
    monkeypatch.setattr(activation, 'metadata_records', lambda table, **kwargs: records[table])
    monkeypatch.setattr(activation, 'resolve_fabric_context', shared.resolve_fabric_context)
    manifest = activation.tested_pipeline_manifest(testing_run_id=result['run_id'],
        candidate_fingerprint=result['candidate_fingerprint'], pipeline_name='Orders', pipeline_version='1',
        agreement_id='agreement', agreement_version='1.0.0', context={'config': {}, 'env': 'dev'})
    assert manifest['testing_run_id'] == result['run_id']
    assert manifest['candidate']['pipeline_id'] == 'orders'


def test_finalization_requires_durable_audit_before_any_testing_publication(runtime, monkeypatch):
    from fabricops_kit import finalize_pipeline
    session = setup_pipeline(pipeline_id='orders', pipeline_mode='Test')
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    monkeypatch.setattr(shared, 'build_runtime_audit_fields', Mock(side_effect=ValueError('missing audit identity')))
    commit = Mock()
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', commit)
    with pytest.raises(ValueError, match='missing audit identity'):
        finalize_pipeline(session)
    commit.assert_not_called()
    runtime.writes.assert_not_called()
