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
    activation = importlib.import_module("fabricops_kit.activated_pipeline.shared")
    monkeypatch.setattr(activation, "guard_ungoverned_write", lambda *args, **kwargs: None)
    config = {}
    context = {'config': config, 'scope_workspace_id': 'dev', 'notebook_id': '00000000-0000-4000-8000-000000000001'}
    monkeypatch.setattr(shared, 'get_default_fabric_context', lambda **kwargs: context)
    spark = SimpleNamespace(conf=SimpleNamespace(get=lambda key: 'test'))
    monkeypatch.setattr(shared, 'resolve_fabric_context', lambda context=None: (config, 'dev', context or {'config': config, 'scope_workspace_id': 'dev'}))
    monkeypatch.setattr(shared, 'get_spark_session', lambda *args, **_kwargs: spark)
    activation_identity = importlib.import_module('fabricops_kit.activated_pipeline.shared')
    monkeypatch.setattr(activation_identity, 'resolve_pipeline_identity', lambda **kwargs: (context['notebook_id'], {'role': 'source', 'row': None}))
    monkeypatch.setattr(shared, 'build_runtime_audit_fields', lambda **kwargs: {'_workspace_id': 'workspace', '_notebook_id': 'notebook'})
    monkeypatch.setattr(shared, 'resolve_physical_table_identity', lambda config, active_workspace_id, **kwargs: {**kwargs, 'table_id': kwargs['table_name']})
    monkeypatch.setattr(shared, 'pipeline_physical_bindings', lambda identities, **kwargs: {key: {'workspace_id': 'dev', 'item_id': value['store'], 'kind': 'lakehouse', 'schema': value.get('schema'), 'table_name': value['table_name']} for key, value in identities.items()})
    monkeypatch.setattr(shared, 'load_table_guardrail_rules', lambda *args, **kwargs: [])
    monkeypatch.setattr(shared, 'read_lakehouse_table', Mock(side_effect=AssertionError('unexpected metadata read')))
    writes = Mock()
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


def test_dry_run_executes_without_target_or_operational_writes(runtime):
    from fabricops_kit import finalize_pipeline

    session = setup_pipeline(pipeline_mode="Dry Run")
    source = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
    result = orchestrate_write(source["dataframe"], store="Gold", schema="demo",
                               table_name="summary", write_mode="overwrite")
    summary = finalize_pipeline(session)

    assert result["published"] is False
    assert result["persistence_status"] == "disabled"
    assert summary["execution_mode"] == "dry_run"
    assert summary["status"] == "dry_run_completed"
    runtime.writes.assert_not_called()


def test_ungoverned_executes_without_contracts_and_persists(runtime, monkeypatch):
    from fabricops_kit import finalize_pipeline

    saved = []
    monkeypatch.setattr(shared, "_merge_pipeline_run_row", lambda plan, row, **kwargs: saved.append(dict(row)))
    runtime.publication.return_value = {"published": True, "table_id": "summary", "status": "passed"}
    session = setup_pipeline(pipeline_mode="Ungoverned")
    source = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
    result = orchestrate_write(source["dataframe"], store="Gold", schema="demo",
                               table_name="summary", write_mode="overwrite")
    summary = finalize_pipeline(session)

    assert result["published"] is True
    assert summary["execution_mode"] == "ungoverned"
    assert summary["status"] == "ungoverned_completed"
    assert saved and all(not any(item.get("contract_id") for item in row["operations"]) for row in saved)


def test_ungoverned_rechecks_and_blocks_a_governed_target(runtime, monkeypatch):
    activation = importlib.import_module("fabricops_kit.activated_pipeline.shared")
    def blocked(*args, **kwargs):
        raise ValueError("Ungoverned cannot write governed table 'summary'")
    monkeypatch.setattr(activation, "guard_ungoverned_write", blocked)
    monkeypatch.setattr(shared, "_merge_pipeline_run_row", lambda *args, **kwargs: None)

    setup_pipeline(pipeline_mode="Ungoverned")
    source = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
    with pytest.raises(ValueError, match="Ungoverned cannot write governed table 'summary'"):
        orchestrate_write(source["dataframe"], store="Gold", schema="demo",
                          table_name="summary", write_mode="overwrite")


@pytest.mark.parametrize('mode', ['test', 'live', 'Testing', '', None, 'TEST'])
def test_exact_mode_validation(runtime, mode):
    with pytest.raises(ValueError, match='Dry Run, Ungoverned or Governed'):
        setup_pipeline(pipeline_mode=mode)


def test_setup_arguments_remove_registration_and_rebind(runtime):
    import inspect
    assert list(inspect.signature(setup_pipeline).parameters) == ["pipeline_mode", "observe_source", "source_observation_days"]
    for removed in ("new_pipeline", "previous_workspace_id", "previous_notebook_id"):
        with pytest.raises(TypeError):
            setup_pipeline(**{removed: True})
    with pytest.raises(TypeError):
        setup_pipeline()
    with pytest.raises(RuntimeError, match="signed-in Fabric"):
        setup_pipeline(pipeline_mode="Governed")


def test_headless_test_without_notebook_identity_or_metadata_writes(runtime):
    runtime_context = shared.get_default_fabric_context()
    runtime_context['notebook_id'] = None
    session = setup_pipeline(pipeline_mode='Dry Run')
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
    session = setup_pipeline(pipeline_mode='Dry Run')
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
    first = setup_pipeline(pipeline_mode='Dry Run')
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    first.cell_completed(SimpleNamespace(error_in_exec=ValueError('bad transform')))
    assert first.closed and not first.sources
    assert first.plan.run_result['status'] == 'failed'
    next_run = setup_pipeline(pipeline_mode='Dry Run')
    assert next_run.plan.plan_id != first.plan.plan_id and not next_run.sources
    with pytest.raises(RuntimeError, match='closed'):
        first.operation_plan('source', {})


def test_operation_failure_seals_run_and_clears_reads(runtime, monkeypatch):
    session = setup_pipeline(pipeline_mode='Dry Run')
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    monkeypatch.setattr(runtime.write, 'pipeline_write', Mock(side_effect=RuntimeError('failed write')))
    with pytest.raises(RuntimeError):
        orchestrate_write(runtime.frame, store='Gold', schema='demo', table_name='summary', write_mode='overwrite')
    assert session.closed and not session.sources
    assert session.plan.run_result['status'] == 'failed'


def test_contexts_isolate_same_pipeline_name(runtime):
    contexts = [Context(), Context()]
    sessions = [context.run(setup_pipeline, pipeline_mode='Dry Run') for context in contexts]
    try:
        for index, context in enumerate(contexts):
            context.run(orchestrate_read, store='Bronze', schema='demo', table_name=f'source{index}')
        assert sessions[0].plan.plan_id != sessions[1].plan.plan_id
        assert [source['table_id'] for source in sessions[0].sources] == ['source0']
        assert [source['table_id'] for source in sessions[1].sources] == ['source1']
    finally:
        for context, session in zip(contexts, sessions):
            context.run(session.close)




def test_contract_selection_freezes_at_first_operation(runtime, monkeypatch):
    session = setup_pipeline(pipeline_mode='Dry Run')
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
    monkeypatch.setattr(ip, 'update_display', displayed)
    monkeypatch.setattr(shared, 'read_lakehouse_table', lambda *args, **kwargs: SimpleNamespace(collect=lambda: [_row()]))
    session = setup_pipeline(pipeline_mode='Dry Run')
    assert any(hasattr(call.args[0], "children") for call in displayed.call_args_list)
    assert '#986f0b' in session.report.value and 'Dry Run' in session.report.value
    session.controls[0].value = 'contract-source\n1'
    assert session.choices['source'] == {'contract_id': 'contract-source', 'contract_version': 1}
    shell.events.register.assert_called_once_with('post_run_cell', session.cell_completed)
    session.cell_completed(SimpleNamespace(error_before_exec=SyntaxError('bad cell')))
    assert session.closed and 'failed' in session.report.value
    shell.events.unregister.assert_called_once_with('post_run_cell', session.cell_completed)


def test_concurrent_async_tasks_do_not_close_an_inherited_execution(runtime):
    import asyncio
    async def scenario():
        parent = setup_pipeline(pipeline_mode='Dry Run')
        async def child(name):
            with pytest.raises(RuntimeError, match='another task'):
                shared.current_pipeline_session()
            session = setup_pipeline(pipeline_mode='Dry Run')
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
    session = setup_pipeline(pipeline_mode='Dry Run')
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    monkeypatch.setattr(shared, 'resolve_physical_table_identity', Mock(side_effect=ValueError('invalid destination')))
    with pytest.raises(ValueError, match='invalid destination'):
        orchestrate_read(store='Bronze', schema='demo', table_name='invalid')
    assert session.closed and not session.sources
    assert session.plan.run_result['status'] == 'failed'


def test_headless_selection_resolves_and_pins_exact_frozen_payload(runtime, monkeypatch):
    session = setup_pipeline(pipeline_mode='Dry Run')
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
    session = setup_pipeline(pipeline_mode='Dry Run')
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
    session = setup_pipeline(pipeline_mode='Dry Run')
    assert shared.current_pipeline_session() is session
    assert session.shell is None


def test_closed_sessions_release_shutdown_callback(runtime, monkeypatch):
    import atexit
    register, unregister = Mock(), Mock()
    monkeypatch.setattr(atexit, 'register', register)
    monkeypatch.setattr(atexit, 'unregister', unregister)
    session = setup_pipeline(pipeline_mode='Dry Run')
    register.assert_called_once_with(session.close)
    session.close()
    unregister.assert_called_once_with(session.close)


def test_dry_run_finalization_remains_session_only(runtime, monkeypatch):
    from fabricops_kit import finalize_pipeline
    committed = []
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', lambda plan, row, **kwargs: committed.append(dict(row)))
    session = setup_pipeline(pipeline_mode='Dry Run')
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    assert not committed
    result = finalize_pipeline(session)
    assert result['status'] == 'dry_run_completed'
    assert result['boundary_completed'] is True
    assert session.closed and not session.sources
    assert not committed
    assert finalize_pipeline(session) == result and not committed
    runtime.writes.assert_not_called()


def test_finalization_records_caught_failure_and_releases_publication_claim(runtime, monkeypatch):
    from fabricops_kit import finalize_pipeline
    activation = importlib.import_module('fabricops_kit.activated_pipeline.shared')
    session = setup_pipeline(pipeline_mode='Dry Run')
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    session.plan = replace(session.plan, execution_mode='ungoverned')
    session.plan.evidence['lease_token'] = session.plan.plan_id
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', Mock())
    release = Mock(side_effect=lambda plan, **kwargs: plan.evidence.pop('lease_token'))
    monkeypatch.setattr(activation, 'release_pipeline_lease', release)
    result = finalize_pipeline(session, failed=True)
    assert result['status'] == 'failed'
    assert result['boundary_completed'] is False
    release.assert_called_once()




def test_active_finalization_cannot_be_claimed_from_another_task(runtime):
    from fabricops_kit import finalize_pipeline
    import asyncio

    async def scenario():
        session = setup_pipeline(pipeline_mode='Dry Run')
        async def child():
            with pytest.raises(RuntimeError, match='another task'):
                finalize_pipeline(session)
        await asyncio.create_task(child())
        assert not session.closed
        session.close()

    asyncio.run(scenario())






def test_missing_configuration_closes_previous_execution(runtime, monkeypatch):
    previous = setup_pipeline(pipeline_mode='Dry Run')
    previous.sources.append({'table_id': 'previous-source'})

    def unavailable(**kwargs):
        raise RuntimeError('Call setup_notebook() first')

    monkeypatch.setattr(shared, 'get_default_fabric_context', unavailable)
    with pytest.raises(RuntimeError, match='Call setup_notebook'):
        setup_pipeline(pipeline_mode='Dry Run')
    assert previous.closed
    assert previous.sources == []
    with pytest.raises(RuntimeError, match='Run setup_pipeline'):
        shared.current_pipeline_session()


def test_setup_and_finalization_display_the_registered_uuid(runtime, capsys, monkeypatch):
    """The returned context and both notebook summaries expose the permanent ID."""
    from fabricops_kit import finalize_pipeline
    session = setup_pipeline(pipeline_mode='Dry Run')
    assert session.pipeline_id == session.plan.pipeline_id
    output = capsys.readouterr().out
    assert f'Pipeline ID: {session.pipeline_id}' in output
    assert 'Save this Pipeline ID' not in output
    assert 'Notebook ID:' in output
    assert 'Mode: Dry Run' in output
    assert 'Workspace:' not in output
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', lambda *args, **kwargs: None)
    finalize_pipeline(session)
    assert f'Pipeline ID: {session.pipeline_id}' in capsys.readouterr().out
    runtime.writes.assert_not_called()




def test_notebook_reload_closes_pipeline_and_uses_fresh_configuration(runtime, monkeypatch, fake_notebookutils):
    """Repeated explicit setup closes its pipeline even when the next setup fails."""
    from fabricops_kit import setup_notebook
    from fabricops_kit.config.shared import get_default_fabric_context
    from tests.unit.test_setup_notebook_store_keys import _config
    monkeypatch.setattr(shared, 'get_default_fabric_context', get_default_fabric_context)
    original = _config()
    setup_notebook(original, workspace_id='dev')
    first = setup_pipeline()
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    fresh = _config()
    setup_notebook(fresh, workspace_id='dev')
    assert first.closed and not first.sources
    second = setup_pipeline()
    assert second.plan.runtime_context['config'] is fresh
    assert second.plan.plan_id != first.plan.plan_id
    with pytest.raises(ValueError):
        setup_notebook(fresh, workspace_id='dev', required_targets=['missing'])
    assert second.closed
    with pytest.raises(RuntimeError, match=r'Call setup_notebook\(\)'):
        setup_pipeline()


def test_active_session_rejects_changed_runtime_before_read(runtime, monkeypatch, fake_notebookutils):
    """An already active pipeline cannot operate with another notebook's context."""
    from fabricops_kit import setup_notebook
    from fabricops_kit.config.shared import get_default_fabric_context
    from tests.unit.test_setup_notebook_store_keys import _config
    monkeypatch.setattr(shared, 'get_default_fabric_context', get_default_fabric_context)
    setup_notebook(_config(), workspace_id='dev')
    session = setup_pipeline()
    fake_notebookutils.context['currentWorkspaceId'] = 'different-workspace'
    with pytest.raises(RuntimeError, match='Notebook execution changed'):
        orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    assert session.closed and not session.plan.evidence['operations']


@pytest.mark.parametrize('field', ['currentWorkspaceId', 'currentNotebookId', 'currentRunId'])
@pytest.mark.parametrize('explicit', [False, True])
@pytest.mark.parametrize('mode', ['Dry Run', 'Governed'])
def test_finalization_checks_runtime_identity_for_explicit_and_active_sessions(
        runtime, monkeypatch, fake_notebookutils, field, explicit, mode):
    """Neither finalization form can claim completion for a stale notebook execution."""
    from fabricops_kit import setup_notebook, finalize_pipeline
    from fabricops_kit.config.shared import get_default_fabric_context
    from tests.unit.test_setup_notebook_store_keys import _config
    monkeypatch.setattr(shared, 'get_default_fabric_context', get_default_fabric_context)
    committed = []
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', lambda plan, row, **kwargs: committed.append(dict(row)))
    setup_notebook(_config(), workspace_id='dev')
    pipeline = setup_pipeline(pipeline_mode='Dry Run')
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    release = Mock(side_effect=lambda plan, **kwargs: plan.evidence.pop('lease_token'))
    if mode == 'Governed':
        pipeline.plan = replace(pipeline.plan, execution_mode='governed', pipeline_version=1,
            promotion_id='reviewed', governed_notebook_id=pipeline.plan.notebook_id)
        pipeline.plan.evidence['lease_token'] = pipeline.plan.plan_id
        activation = importlib.import_module('fabricops_kit.activated_pipeline.shared')
        monkeypatch.setattr(activation, 'release_pipeline_lease', release)
    fake_notebookutils.context[field] = 'another-execution'
    with pytest.raises(RuntimeError, match='Notebook execution changed'):
        finalize_pipeline(pipeline) if explicit else finalize_pipeline()
    assert pipeline.closed and pipeline.plan.run_result['boundary_completed'] is False
    assert all(row['boundary_completed'] is False for row in committed)
    if mode == 'Dry Run':
        assert not committed
    else:
        release.assert_called_once()


def test_closed_finalization_remains_idempotent_after_setup_is_invalidated(runtime, monkeypatch, fake_notebookutils):
    """Completed results and publication retries remain available through the saved session."""
    from fabricops_kit import setup_notebook, finalize_pipeline
    from fabricops_kit.config.shared import get_default_fabric_context
    from tests.unit.test_setup_notebook_store_keys import _config
    monkeypatch.setattr(shared, 'get_default_fabric_context', get_default_fabric_context)
    committed = []
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', lambda plan, row, **kwargs: committed.append(dict(row)))
    setup_notebook(_config(), workspace_id='dev')
    pipeline = setup_pipeline()
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    result = finalize_pipeline(pipeline)
    assert result['boundary_completed'] is True and committed[-1]['status'] == 'ungoverned_completed'
    commit_count = len(committed)
    fake_notebookutils.context['currentRunId'] = 'another-run'
    with pytest.raises(ValueError):
        setup_notebook(_config(), workspace_id='dev', required_targets=['missing'])
    assert finalize_pipeline(pipeline) == result
    assert len(committed) == commit_count


def test_finalize_emits_compact_summary_even_when_report_widget_exists(runtime, capsys):
    """The final outcome is visible when notebook assignment suppresses the return value."""
    from fabricops_kit import finalize_pipeline

    session = setup_pipeline(pipeline_mode="Ungoverned")
    session.report = SimpleNamespace(value='')

    result = finalize_pipeline(session)
    output = capsys.readouterr().out

    status = result["status"].replace("_", " ").upper()
    assert f"FabricOps Pipeline Summary · {status}" in output
    assert f"Pipeline ID: {session.pipeline_id}" in output
    assert f"Run ID: {session.plan.plan_id}" in output


def test_public_finalize_retries_remaining_claims_after_partial_release(runtime, monkeypatch):
    """A closed session retries cleanup without replaying its durable Run or touching successors."""
    from fabricops_kit import finalize_pipeline
    from fabricops_kit.activated_pipeline import shared as authority
    session = setup_pipeline(pipeline_mode='Dry Run')
    orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    session.plan = replace(session.plan, execution_mode='ungoverned')
    claims = [{'table_name': 'A'}, {'table_name': 'B'}]
    session.plan.evidence.update(lease_token=session.plan.plan_id, publication_claims=claims)
    committed = Mock()
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', committed)
    released, fail = [], [True]
    def release(owner, target, **kwargs):
        assert kwargs['release'] is True
        name = target['table_name']
        if name == 'B' and fail[0]:
            fail[0] = False
            raise RuntimeError('release conflict')
        released.append(name)
    monkeypatch.setattr(authority, 'publication_claim', release)
    with pytest.raises(RuntimeError, match='release conflict'):
        finalize_pipeline(session)
    assert session.closed and released == ['A']
    result = finalize_pipeline(session)
    assert result['status'] == 'ungoverned_completed'
    assert released == ['A', 'B']
    committed.assert_called_once()
    assert 'lease_token' not in session.plan.evidence


@pytest.mark.parametrize("ui_fails", [False, True])
def test_finalize_displays_captured_submission_without_repeating_run(runtime, monkeypatch, capsys, ui_fails):
    """Finalize preserves the summary and reopens handoff without redoing operations."""
    from fabricops_kit import finalize_pipeline
    from fabricops_kit.activated_pipeline import shared as authority
    session = setup_pipeline(pipeline_mode="Dry Run")
    orchestrate_read(store="Bronze", schema="demo", table_name="orders")
    session.plan.evidence["notebook_snapshot"] = b"captured saved notebook"
    persist = Mock(return_value="dry-run.json")
    monkeypatch.setattr(authority, "persist_engineering_dry_run", persist)
    ui = Mock(side_effect=RuntimeError("UI unavailable")) if ui_fails else Mock(return_value={"widget": "handoff"})
    monkeypatch.setattr(authority, "display_pipeline_handoff", ui)
    first = finalize_pipeline(session)
    second = finalize_pipeline(session)
    assert first == second and first["status"] == "dry_run_completed"
    persist.assert_called_once()
    assert ui.call_count == 2
    assert ui.call_args.kwargs["dry_run"] is session
    runtime.writes.assert_not_called()
    if ui_fails:
        assert "run outcome is unchanged" in capsys.readouterr().out
    else:
        assert session.plan.evidence["handoff"] == {"widget": "handoff"}


@pytest.mark.parametrize("failed", [False, True])
def test_finalize_without_eligible_capture_never_opens_deployment(runtime, monkeypatch, failed):
    """Failed or uncaptured execution cannot export an approval candidate."""
    from fabricops_kit import finalize_pipeline
    from fabricops_kit.activated_pipeline import shared as authority
    session = setup_pipeline(pipeline_mode="Dry Run")
    orchestrate_read(store="Bronze", schema="demo", table_name="orders")
    ui = Mock()
    monkeypatch.setattr(authority, "display_pipeline_handoff", ui)
    finalize_pipeline(session, failed=failed)
    ui.assert_not_called()


def test_finalize_reopens_persisted_handoff_without_execution(runtime, monkeypatch):
    """An independent Engineering kernel needs no prior Dry Run session to deploy/recover."""
    from fabricops_kit import finalize_pipeline
    from fabricops_kit.activated_pipeline import shared as authority
    from tests.unit.test_activated_pipeline import PIPELINE_ID
    ui = Mock(return_value={"widget": "persisted approvals"})
    monkeypatch.setattr(authority, "display_pipeline_handoff", ui)
    assert shared._ACTIVE_PIPELINE.get() is None
    assert finalize_pipeline() == {"pipeline_id": PIPELINE_ID, "handoff": {"widget": "persisted approvals"}}
    ui.assert_called_once_with(pipeline_id=PIPELINE_ID)
    assert shared._ACTIVE_PIPELINE.get() is None
    runtime.writes.assert_not_called()
    with pytest.raises(ValueError):
        finalize_pipeline(failed=True)
    with pytest.raises(ValueError):
        finalize_pipeline(object())
    with pytest.raises(ValueError):
        finalize_pipeline()
