"""Execute the shared config template across a simulated Fabric notebook boundary."""
# ruff: noqa: D103
from contextlib import redirect_stdout
from dataclasses import asdict
from io import StringIO
import importlib
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import pytest

from fabricops_kit import setup_notebook, setup_pipeline
from fabricops_kit.config.shared import resolve_fabric_context, resolve_runtime_context
from fabricops_kit.io.shared import get_spark_session as central_spark_resolver
from tests.unit.test_setup_notebook_store_keys import _config

pytestmark = pytest.mark.unit


class NotebookExit(Exception):
    """Model Fabric notebook.exit stopping the reference notebook."""


@pytest.fixture(params=["attribute", "submodule"])
def configuration_runtime(monkeypatch, request):
    """Keep config construction and validation real; simulate only Fabric services."""
    import builtins

    monkeypatch.delattr(builtins, 'FABRIC_CONTEXT', raising=False)
    monkeypatch.setattr(builtins, 'FABRIC_CONTEXT', None, raising=False)
    runtime = ModuleType('notebookutils.runtime')
    runtime.context = {'currentWorkspaceId': 'dev-ws', 'currentNotebookName': '02_pipeline_orders',
                       'currentRunId': 'caller-run', 'currentNotebookId': 'caller-notebook',
                       'currentWorkspaceName': 'Engineering', 'environmentWorkspaceId': 'environment-ws'}
    nb = ModuleType('notebookutils')
    nb.runtime = runtime
    nb.notebook = SimpleNamespace(exit=lambda payload: (_ for _ in ()).throw(NotebookExit(payload)))
    monkeypatch.setitem(sys.modules, 'notebookutils', nb)
    if request.param == "submodule":
        monkeypatch.setitem(sys.modules, 'notebookutils.runtime', runtime)
    else:
        monkeypatch.delitem(sys.modules, 'notebookutils.runtime', raising=False)
    spark = SimpleNamespace(conf=SimpleNamespace(set=Mock()))
    monkeypatch.setattr(importlib.import_module('fabricops_kit.io.shared'), 'get_spark_session', lambda *_args, **_kwargs: spark)
    cells = json.loads(Path('templates/notebooks/00_env_config.ipynb').read_text())['cells']

    settings = SimpleNamespace(environments=None, governance_environment='')

    def run(name, timeout, arguments, *, workspace):
        assert name == '00_env_config'
        assert workspace in {'central-ws', 'dev-ws', 'metadata-ws'}
        namespace = {'spark': spark, **arguments}
        # Reference execution is hosted centrally, while the passed caller ID differs.
        original_workspace = runtime.context.get('currentWorkspaceId')
        runtime.context['currentWorkspaceId'] = workspace
        try:
            for cell in cells:
                if cell['cell_type'] != 'code' or 'parameters' in cell['metadata'].get('tags', []):
                    continue
                source = ''.join(cell['source'])
                for placeholder, value in {
                    '<DEV_WORKSPACE_ID>': 'dev-ws', '<TEST_WORKSPACE_ID>': 'test-ws',
                    '<PROD_WORKSPACE_ID>': 'prod-ws', '<GOVERNANCE_WORKSPACE_ID>': 'metadata-ws',
                    '<METADATA_ITEM_ID>': 'metadata-item', '<BRONZE_ITEM_ID>': 'bronze-item',
                    '<SILVER_ITEM_ID>': 'silver-item', '<GOLD_ITEM_ID>': 'gold-item',
                    '<BRONZE_NAME>': 'lh_Bronze', '<SILVER_NAME>': 'lh_Silver', '<GOLD_NAME>': 'wh_Gold',
                }.items():
                    source = source.replace(placeholder, value)
                # This fixture exercises configuration loading, not metadata deployment.
                source = source.replace('INITIALIZE_METADATA = True', 'INITIALIZE_METADATA = False')
                source = source.replace('GOVERNANCE_ENVIRONMENT = ""',
                                        f'GOVERNANCE_ENVIRONMENT = {settings.governance_environment!r}')
                if settings.environments is not None:
                    source = source.replace('ENVIRONMENT_WORKSPACES = ENGINEERING_WORKSPACES',
                        f'ENGINEERING_WORKSPACES = {{k: v for k, v in ENGINEERING_WORKSPACES.items() if k in {settings.environments!r}}}\n'
                        'ENV_ITEMS = {k: v for k, v in ENV_ITEMS.items() if k in ENGINEERING_WORKSPACES}\n'
                        'ENVIRONMENT_WORKSPACES = ENGINEERING_WORKSPACES')
                # Fabric keeps child output in its execution snapshot.
                with redirect_stdout(StringIO()):
                    exec(compile(source, '<00_env_config>', 'exec'), namespace)
        except NotebookExit as exc:
            return exc.args[0]
        finally:
            runtime.context['currentWorkspaceId'] = original_workspace
        raise AssertionError('Config notebook must exit with JSON')

    nb.notebook.run = Mock(side_effect=run)
    return SimpleNamespace(runtime=runtime, notebook=nb.notebook, spark=spark, cells=cells, settings=settings)


@pytest.mark.parametrize('workspace, environment', [('dev-ws', 'dev'), ('prod-ws', 'prod')])
def test_engineering_loads_central_config_for_caller_workspace(configuration_runtime, monkeypatch, workspace, environment):
    fabric = configuration_runtime
    fabric.runtime.context['currentWorkspaceId'] = workspace
    result = setup_notebook(config_workspace_id="central-ws")
    assert result.environment == environment
    assert set(result.paths) == {'Bronze', 'Silver', 'Gold', 'Metadata'}
    assert result.paths['Silver'].env == environment
    assert result.paths['Gold'].name == 'wh_Gold'
    assert result.paths['Metadata'].workspace_id == 'metadata-ws'
    assert result.run_id == 'caller-run'
    config, env, context = resolve_fabric_context()
    assert env == environment and config.path_config.paths[env]['Gold'].kind == 'warehouse'
    assert context['runtime_metadata']['workspace_id'] == workspace
    fabric.notebook.run.assert_called_once_with('00_env_config', 120, {'caller_workspace_id': workspace}, workspace='central-ws')
    fabric.spark.conf.set.assert_called_once_with('spark.sql.session.timeZone', config.audit_timezone)


def test_governance_loads_its_separate_local_deployment(configuration_runtime):
    fabric = configuration_runtime
    fabric.runtime.context.update(currentWorkspaceId='metadata-ws', currentNotebookName='01_governance')
    fabric.settings.environments = ['dev']
    assert setup_notebook().environment == 'dev'
    fabric.notebook.run.assert_called_once_with(
        '00_env_config', 120, {'caller_workspace_id': 'metadata-ws'}, workspace='metadata-ws')


def test_unknown_workspace_is_rejected_by_central_notebook(configuration_runtime, monkeypatch):
    configuration_runtime.runtime.context['currentWorkspaceId'] = 'unregistered'
    with pytest.raises(ValueError, match='Unknown workspace ID'):
        setup_notebook(config_workspace_id='central-ws')


def test_missing_runtime_workspace_fails_before_notebook_execution(configuration_runtime):
    configuration_runtime.runtime.context.pop('currentWorkspaceId')
    with pytest.raises(RuntimeError, match='currentWorkspaceId'):
        setup_notebook()
    configuration_runtime.notebook.run.assert_not_called()


@pytest.mark.parametrize('change, message', [
    ({'workspace_id': 'other'}, 'does not match'),
    ({'env': 'missing'}, 'No configured paths'),
])
def test_invalid_response_reuses_validation(configuration_runtime, change, message):
    configuration_runtime.notebook.run.side_effect = None
    configuration_runtime.notebook.run.return_value = json.dumps({
        'workspace_id': 'dev-ws', 'env': 'dev', 'config': asdict(_config()), **change,
    })
    with pytest.raises(ValueError, match=message):
        setup_notebook()


@pytest.mark.parametrize('mode', ['Test', 'Live'])
@pytest.mark.parametrize('config_workspace', [None, 'central-ws'])
def test_pipeline_reuses_workspace_initialization(configuration_runtime, monkeypatch, capsys, mode, config_workspace):
    shared = importlib.import_module('fabricops_kit.pipeline.shared')
    monkeypatch.setattr(shared, 'resolve_pipeline_registration', lambda identity, **kwargs: {'pipeline_id': '8f32a471-6c91-4b7e-9d13-2f0c947eab52', 'resolution': 'Recovered'})
    monkeypatch.setattr(shared, 'get_spark_session', lambda *_args, **_kwargs: configuration_runtime.spark)
    monkeypatch.setattr(shared.PipelineSession, 'refresh', lambda self: None)
    if mode == 'Live':
        live = importlib.import_module('fabricops_kit.activated_pipeline.shared')
        def approved(**kwargs):
            config, env, runtime = resolve_fabric_context()
            return shared.PipelineExecutionPlan('live', env, 'caller-notebook', 'approved-run',
                                               '{}', '{}', '{}', runtime, pipeline_id=kwargs['pipeline_id'])
        monkeypatch.setattr(live, 'build_live_pipeline_plan', approved)
    import IPython
    monkeypatch.setattr(IPython, 'get_ipython', lambda: None)
    token = shared._ACTIVE_PIPELINE.set(None)
    session = None
    try:
        notebook = setup_notebook(config_workspace_id=config_workspace)
        notebook_output = capsys.readouterr().out
        session = setup_pipeline(pipeline_mode=mode)
        assert session.plan.environment == 'dev'
        assert session.plan.pipeline_id == '8f32a471-6c91-4b7e-9d13-2f0c947eab52'
        assert session.plan.runtime_context['config'].path_config.paths['dev']['Metadata'].workspace_id == 'metadata-ws'
        configuration_runtime.notebook.run.assert_called_once_with(
            '00_env_config', 120, {'caller_workspace_id': 'dev-ws'}, workspace=config_workspace or 'dev-ws')
        assert session.plan.runtime_context['runtime_metadata']['workspace_id'] == 'dev-ws'
        if mode == 'Test':
            first = session
            session = setup_pipeline(pipeline_mode=mode)
            assert first.closed
            assert session.plan.plan_id != first.plan.plan_id
            assert session.plan.runtime_context['config'] is first.plan.runtime_context['config']
            assert configuration_runtime.notebook.run.call_count == 1
        from fabricops_kit import __version__
        output = capsys.readouterr().out
        assert notebook_output.count(f'FabricOps v{__version__}') == 1
        assert f'FabricOps v{__version__}' not in output
        assert session.plan.runtime_context['_notebook_setup']['result'] is notebook
        location = 'cross-workspace' if config_workspace else 'same-workspace'
        assert f'Configuration: 00_env_config ({location}; workspace: {config_workspace or "dev-ws"})' in notebook_output
        assert 'Environment: dev' in notebook_output
        assert 'Readiness: ready' in notebook_output
        assert 'Configuration:' not in output
        assert 'Readiness:' not in output
    finally:
        if session is not None:
            import atexit
            atexit.unregister(session.close)
        shared._ACTIVE_PIPELINE.reset(token)


def test_duplicate_workspace_assignments_are_rejected(configuration_runtime):
    for cell in configuration_runtime.cells:
        cell['source'] = [line.replace('<PROD_WORKSPACE_ID>', '<DEV_WORKSPACE_ID>')
                          for line in cell['source']]
    with pytest.raises(ValueError, match='strict 1:1 mapping'):
        setup_notebook()


def test_setup_replaces_stale_notebook_namespace_context(configuration_runtime, monkeypatch):
    import IPython

    shell = SimpleNamespace(user_ns={'FABRIC_CONTEXT': {'config': _config(), 'env': 'stale'}})
    monkeypatch.setattr(IPython, 'get_ipython', lambda: shell)
    result = setup_notebook()
    assert result.environment == 'dev'
    assert resolve_fabric_context()[1] == 'dev'
    assert shell.user_ns['FABRIC_CONTEXT']['runtime_metadata']['workspace_id'] == 'dev-ws'


def test_default_loading_uses_current_workspace(configuration_runtime):
    result = setup_notebook()
    assert result.environment == 'dev'
    configuration_runtime.notebook.run.assert_called_once_with(
        '00_env_config', 120, {'caller_workspace_id': 'dev-ws'}, workspace='dev-ws')



def test_attribute_only_runtime_reproduces_fabric_import_behavior(configuration_runtime):
    import notebookutils

    if 'notebookutils.runtime' not in sys.modules:
        with pytest.raises(ModuleNotFoundError):
            exec('import notebookutils.runtime')
    assert notebookutils.runtime.context['currentWorkspaceId'] == 'dev-ws'
    result = setup_notebook()
    assert result.runtime_metadata['workspace_id'] == 'dev-ws'
    assert result.workspace_name == 'Engineering'
    assert resolve_runtime_context(active_context={})['workspace_id'] == 'dev-ws'


@pytest.mark.parametrize('context', [None, {}])
def test_unavailable_or_empty_runtime_context(configuration_runtime, context):
    configuration_runtime.runtime.context = context
    message = 'context is unavailable' if context is None else 'currentWorkspaceId'
    with pytest.raises(RuntimeError, match=message):
        setup_notebook()
    configuration_runtime.notebook.run.assert_not_called()
    # Explicit configuration remains usable outside automatic workspace loading.
    assert setup_notebook(_config(), env='dev').environment == 'dev'


def test_environment_workspace_never_substitutes_for_caller(configuration_runtime):
    configuration_runtime.runtime.context.pop('currentWorkspaceId')
    with pytest.raises(RuntimeError, match='currentWorkspaceId'):
        setup_notebook(config_workspace_id='central-ws')
    configuration_runtime.notebook.run.assert_not_called()


def test_outside_fabric_has_distinct_error(monkeypatch):
    monkeypatch.setitem(sys.modules, 'notebookutils', None)
    with pytest.raises(RuntimeError, match='Outside Microsoft Fabric'):
        setup_notebook()
    result = setup_notebook(_config(), env='dev')
    assert result.runtime_metadata['runtime_available'] is False


@pytest.mark.parametrize('failure', [ImportError('private detail'), RuntimeError('private detail'),
                                    ModuleNotFoundError('private detail', name='runtime_dependency')])
def test_unexpected_import_failure_is_not_missing_workspace(monkeypatch, failure):
    import builtins

    original_import = builtins.__import__

    def import_module(name, *args, **kwargs):
        if name == 'notebookutils':
            raise failure
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, '__import__', import_module)
    with pytest.raises(RuntimeError, match='notebookutils import failed') as error:
        setup_notebook()
    assert 'private detail' not in str(error.value)
    assert error.value.__suppress_context__


@pytest.mark.parametrize('field', ['runtime', 'context', 'currentWorkspaceId'])
def test_unexpected_context_access_failure(configuration_runtime, monkeypatch, field):
    class BrokenContext:
        def __getattr__(self, key):
            raise RuntimeError('private detail')

    if field == 'runtime':
        monkeypatch.setitem(sys.modules, 'notebookutils', BrokenContext())
    elif field == 'context':
        sys.modules['notebookutils'].runtime = BrokenContext()
    else:
        configuration_runtime.runtime.context = BrokenContext()
    with pytest.raises(RuntimeError, match='Fabric runtime context') as error:
        setup_notebook()
    assert 'private detail' not in str(error.value)
    configuration_runtime.notebook.run.assert_not_called()


@pytest.mark.parametrize('config_workspace', [None, 'central-ws'])
def test_config_notebook_execution_failure(configuration_runtime, config_workspace):
    configuration_runtime.notebook.run.side_effect = RuntimeError('private detail')
    location = 'cross-workspace' if config_workspace else 'same-workspace'
    with pytest.raises(RuntimeError, match=location + ' 00_env_config execution failed') as error:
        setup_notebook(config_workspace_id=config_workspace)
    assert 'private detail' not in str(error.value)
    assert 'access' not in str(error.value)


@pytest.mark.parametrize('config_workspace', [None, 'central-ws'])
@pytest.mark.parametrize('failure', [
    TypeError("run() got an unexpected keyword argument 'workspaceId'. Did you mean 'workspace'?"),
    AttributeError("notebook API has no attribute 'run'"),
    ValueError('Unknown workspace ID'),
])
def test_config_notebook_api_errors_propagate(configuration_runtime, config_workspace, failure):
    configuration_runtime.notebook.run.side_effect = failure
    with pytest.raises(type(failure)) as error:
        setup_notebook(config_workspace_id=config_workspace)
    assert error.value is failure
    configuration_runtime.notebook.run.assert_called_once_with(
        '00_env_config', 120, {'caller_workspace_id': 'dev-ws'}, workspace=config_workspace or 'dev-ws')


def test_invalid_config_notebook_json(configuration_runtime):
    configuration_runtime.notebook.run.side_effect = None
    configuration_runtime.notebook.run.return_value = 'private detail'
    with pytest.raises(ValueError, match='invalid configuration JSON'):
        setup_notebook()



def test_missing_runtime_attribute(configuration_runtime):
    del sys.modules['notebookutils'].runtime
    with pytest.raises(RuntimeError, match='context is unavailable'):
        setup_notebook()
    configuration_runtime.notebook.run.assert_not_called()


@pytest.mark.parametrize('shape', ['attributes', 'getter'])
def test_runtime_context_supports_object_and_getter_shapes(configuration_runtime, shape):
    values = configuration_runtime.runtime.context
    if shape == 'attributes':
        context = SimpleNamespace(**values)
    else:
        context = SimpleNamespace(get=values.get)
    configuration_runtime.runtime.context = context
    # Explicit config isolates metadata extraction from the notebook-boundary simulation.
    result = setup_notebook(_config(), env='dev')
    assert result.runtime_metadata['workspace_id'] == 'dev-ws'
    assert result.workspace_name == 'Engineering'
    assert resolve_runtime_context(active_context={})['workspace_id'] == 'dev-ws'


@pytest.mark.parametrize('config_workspace', [None, 'central-ws'])
@pytest.mark.parametrize('caller_workspace', ['dev-ws', ' DEV-WS '])
def test_setup_summary_is_visible_without_child_notebook_output(configuration_runtime, capsys, config_workspace, caller_workspace):
    from fabricops_kit import __version__

    configuration_runtime.runtime.context['currentWorkspaceId'] = caller_workspace
    raw = asdict(_config())
    stores = raw['path_config']['paths'].pop('dev')
    raw['path_config']['paths']['POC'] = stores
    for store in stores.values():
        store['env'] = 'POC'
    stores['Gold']['name'] = 'wh_Gold'
    raw['audit_timezone'] = 'Asia/Singapore'
    configuration_runtime.notebook.run.side_effect = None
    configuration_runtime.notebook.run.return_value = json.dumps({
        'workspace_id': 'dev-ws', 'env': 'POC', 'config': raw,
    })

    result = setup_notebook(config_workspace_id=config_workspace, required_targets=['Gold', 'Metadata'])

    output = capsys.readouterr().out
    assert output.count(f'FabricOps v{__version__}') == 1
    assert 'Docs, examples, releases & support:' in output
    assert 'https://github.com/Voycepeh/FabricOps-Starter-Kit' in output
    location = 'cross-workspace' if config_workspace else 'same-workspace'
    assert f'Configuration: 00_env_config ({location}; workspace: {config_workspace or "dev-ws"})' in output
    assert 'Caller workspace: Engineering (dev-ws)' in output
    assert 'Notebook: 02_pipeline_orders' in output
    assert 'Run ID: caller-run' in output
    assert 'Environment: POC' in output
    assert 'Audit timezone: Asia/Singapore' in output
    assert 'Metadata schemas: governance=governance, engineering=engineering' in output
    assert '- Gold: wh_Gold (warehouse;' in output
    assert '- Metadata: Metadata (lakehouse; schema: governance; workspace: workspace)' in output
    assert '- Bronze:' not in output
    assert 'Readiness: ready' in output
    assert 'abfss://' not in output
    assert 'path_config' not in output
    assert result.environment == 'POC'
    configuration_runtime.spark.conf.set.assert_called_once_with('spark.sql.session.timeZone', 'Asia/Singapore')


def test_failed_config_load_does_not_print_success_summary(configuration_runtime, capsys):
    configuration_runtime.notebook.run.side_effect = RuntimeError('execution failed')
    with pytest.raises(RuntimeError, match='00_env_config execution failed'):
        setup_notebook()
    assert capsys.readouterr().out == ''


@pytest.mark.parametrize("selected", ["", "test", "missing"])
def test_governance_multiple_environments_require_configured_choice(configuration_runtime, selected):
    fabric = configuration_runtime
    fabric.runtime.context['currentWorkspaceId'] = 'metadata-ws'
    fabric.settings.governance_environment = selected
    if selected == 'test':
        result = setup_notebook(required_targets=['Metadata'])
        assert result.environment == 'test'
        assert set(result.paths) == {'Metadata'}
        assert resolve_fabric_context()[0].path_config.paths['test']['Silver'].workspace_id == 'test-ws'
    else:
        with pytest.raises(ValueError, match='GOVERNANCE_ENVIRONMENT'):
            setup_notebook(required_targets=['Metadata'])


def test_governance_summary_filters_targets_without_restricting_config(configuration_runtime, capsys):
    fabric = configuration_runtime
    fabric.runtime.context['currentWorkspaceId'] = 'metadata-ws'
    fabric.settings.environments = ['dev']
    result = setup_notebook(required_targets=['Metadata'])
    output = capsys.readouterr().out
    assert set(result.paths) == {'Metadata'}
    assert '- Metadata:' in output
    assert all(f'- {name}:' not in output for name in ['Bronze', 'Silver', 'Gold'])
    assert set(resolve_fabric_context()[0].path_config.paths['dev']) == {'Bronze', 'Silver', 'Gold', 'Metadata'}


def test_setup_uses_namespace_session_once_for_readiness_and_timezone(configuration_runtime, monkeypatch):
    from fabricops_kit.io import shared as io
    spark = configuration_runtime.spark
    spark.sql = Mock()
    import_module = Mock(side_effect=lambda name: SimpleNamespace(
        SparkSession=SimpleNamespace(getActiveSession=lambda: None)) if name == 'pyspark.sql'
        else SimpleNamespace(get_ipython=lambda: SimpleNamespace(user_ns={'spark': spark})))
    monkeypatch.setattr(io, 'import_module', import_module)
    actual_resolver = Mock(wraps=central_spark_resolver)
    monkeypatch.setattr(io, 'get_spark_session', actual_resolver)
    result = setup_notebook(required_targets=['Metadata'])
    actual_resolver.assert_called_once_with()
    check = next(c for c in result.validation_results if c.name == 'spark_session')
    assert check.status == 'pass'
    spark.conf.set.assert_called_once_with('spark.sql.session.timeZone', 'UTC')


def test_governance_config_runs_directly_without_caller_parameter(configuration_runtime):
    """Running 00_env_config in Governance uses its real runtime workspace."""
    fabric = configuration_runtime
    fabric.settings.environments = ['dev']
    payload = json.loads(fabric.notebook.run('00_env_config', 120, {'caller_workspace_id': ''}, workspace='metadata-ws'))
    assert payload['workspace_id'] == 'metadata-ws'
    assert payload['env'] == 'dev'
    assert payload['config']['path_config']['paths']['dev']['Metadata']['workspace_id'] == 'metadata-ws'


def test_engineering_workspace_mapping_precedes_governance_choice(configuration_runtime):
    """The Governance selector never redirects an Engineering caller."""
    configuration_runtime.settings.governance_environment = 'prod'
    assert setup_notebook(config_workspace_id='central-ws').environment == 'dev'


def test_pipeline_requires_setup_notebook_even_with_manual_config(configuration_runtime, monkeypatch):
    """A raw shared context is not proof that notebook validation completed."""
    import builtins
    shared = importlib.import_module('fabricops_kit.pipeline.shared')
    registration = Mock()
    monkeypatch.setattr(shared, 'resolve_pipeline_registration', registration)
    monkeypatch.setattr(builtins, 'FABRIC_CONTEXT', {'config': _config(), 'env': 'dev'})
    with pytest.raises(RuntimeError, match=r'Call setup_notebook\(\)'):
        setup_pipeline()
    configuration_runtime.notebook.run.assert_not_called()
    registration.assert_not_called()


@pytest.mark.parametrize('field', ['currentWorkspaceId', 'currentNotebookId', 'currentRunId'])
def test_pipeline_rejects_context_from_a_previous_execution(configuration_runtime, monkeypatch, field):
    """Changing the caller identity cannot reuse its old workspace configuration."""
    setup_notebook()
    configuration_runtime.runtime.context[field] = 'another-execution'
    shared = importlib.import_module('fabricops_kit.pipeline.shared')
    registration = Mock()
    monkeypatch.setattr(shared, 'resolve_pipeline_registration', registration)
    with pytest.raises(RuntimeError, match=r'Call setup_notebook\(\) again'):
        setup_pipeline()
    assert configuration_runtime.notebook.run.call_count == 1
    registration.assert_not_called()


@pytest.mark.parametrize('change', ['env', 'config', 'readiness'])
def test_pipeline_rejects_invalid_initialized_configuration(configuration_runtime, change):
    """A replaced environment, configuration or failed readiness requires fresh setup."""
    result = setup_notebook()
    from fabricops_kit.config.shared import get_default_fabric_context
    context = get_default_fabric_context()
    if change == 'readiness':
        from dataclasses import replace
        context['_notebook_setup']['result'] = replace(result, readiness_status='not_ready')
    else:
        context[change] = 'different'
    with pytest.raises(RuntimeError, match=r'Call setup_notebook\(\) successfully'):
        setup_pipeline()
    assert configuration_runtime.notebook.run.call_count == 1


def test_failed_notebook_reload_invalidates_previous_setup(configuration_runtime):
    """A failed config load cannot leave the last successful configuration eligible."""
    setup_notebook()
    configuration_runtime.notebook.run.side_effect = RuntimeError('config unavailable')
    with pytest.raises(RuntimeError, match='00_env_config execution failed'):
        setup_notebook()
    with pytest.raises(RuntimeError, match=r'Call setup_notebook\(\)'):
        setup_pipeline()
    assert configuration_runtime.notebook.run.call_count == 2


def test_explicit_setup_publishes_configuration_without_loading_notebook(configuration_runtime):
    """Local and advanced explicit configuration publishes the same initialized state."""
    from fabricops_kit.config.shared import get_default_fabric_context
    supplied = _config()
    result = setup_notebook(supplied, env='dev', config_workspace_id='ignored')
    active = get_default_fabric_context(require_notebook_setup=True)
    assert active['config'] is supplied
    assert active['env'] == 'dev'
    assert active['_notebook_setup']['result'] is result
    configuration_runtime.notebook.run.assert_not_called()


def test_setup_pipeline_rejects_configuration_workspace_parameter(configuration_runtime):
    """Configuration workspace selection belongs only to the notebook stage."""
    with pytest.raises(TypeError, match='config_workspace_id'):
        setup_pipeline(config_workspace_id='central-ws')
    configuration_runtime.notebook.run.assert_not_called()



def test_failed_setup_output_does_not_publish_a_ready_context(configuration_runtime, monkeypatch):
    """A failed setup stage cannot publish state that pipeline setup treats as ready."""
    setup_notebook()
    config = importlib.import_module('fabricops_kit.config.shared')
    monkeypatch.setattr(config, '_print_notebook_setup_summary', Mock(side_effect=RuntimeError('display failed')))
    with pytest.raises(RuntimeError, match='display failed'):
        setup_notebook(_config(), env='dev')
    with pytest.raises(RuntimeError, match=r'Call setup_notebook\(\)'):
        setup_pipeline()
    assert configuration_runtime.notebook.run.call_count == 1


@pytest.mark.parametrize('notebook_namespace', [False, True])
@pytest.mark.parametrize('failure', ['validation', 'display', 'session_close'])
def test_failed_setup_blocks_all_default_io_without_blocking_explicit_context(
        configuration_runtime, monkeypatch, notebook_namespace, failure):
    """A failed setup cannot recover old config through either published binding or CONFIG/ENV."""
    import builtins
    import IPython
    from fabricops_kit.config import shared as config_shared
    from fabricops_kit.pipeline import shared as pipeline_shared
    from fabricops_kit.io.shared import resolve_configured_lakehouse_table

    supplied = _config()
    shell = SimpleNamespace(user_ns={'CONFIG': supplied, 'ENV': 'dev'}) if notebook_namespace else None
    monkeypatch.setattr(IPython, 'get_ipython', lambda: shell)
    monkeypatch.setattr(config_shared, '_print_notebook_setup_summary', Mock())
    setup_notebook(supplied, env='dev')
    # Keep distinct copies to ensure both publication locations are invalidated.
    builtins.FABRIC_CONTEXT = dict(builtins.FABRIC_CONTEXT)
    if failure == 'display':
        monkeypatch.setattr(config_shared, '_print_notebook_setup_summary', Mock(side_effect=RuntimeError('display failed')))
    if failure == 'session_close':
        monkeypatch.setattr(pipeline_shared, 'close_current_pipeline_session', Mock(side_effect=RuntimeError('close failed')))
    with pytest.raises((ValueError, RuntimeError)):
        setup_notebook(supplied, env='dev', required_targets=['missing'] if failure == 'validation' else None)
    with pytest.raises(RuntimeError, match=r'Call setup_notebook\(\)'):
        config_shared.get_default_fabric_context()
    with pytest.raises(RuntimeError, match=r'Call setup_notebook\(\)'):
        resolve_fabric_context()
    with pytest.raises(RuntimeError, match=r'Call setup_notebook\(\)'):
        resolve_configured_lakehouse_table('Bronze', 'orders', None)
    # Advanced callers can still deliberately supply config and environment.
    config, env, _ = resolve_fabric_context(config=supplied, env='dev')
    assert config is supplied and env == 'dev'
    store, _, _, _ = resolve_configured_lakehouse_table('Bronze', 'orders', None,
        context={'config': supplied, 'env': 'dev'})
    assert store.workspace_id == 'workspace'
    configuration_runtime.notebook.run.assert_not_called()
