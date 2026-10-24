"""Execute the shared config template across a simulated Fabric notebook boundary."""
# ruff: noqa: D103
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import pytest

from fabricops_kit import setup_notebook, setup_pipeline
from fabricops_kit.config.shared import resolve_fabric_context, resolve_runtime_context
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
    monkeypatch.setattr(importlib.import_module('fabricops_kit.io.shared'), 'get_spark_session', lambda: spark)
    cells = json.loads(Path('templates/notebooks/00_env_config.ipynb').read_text())['cells']

    def run(name, timeout, arguments, *, workspaceId):
        assert name == '00_env_config'
        assert workspaceId in {'central-ws', 'dev-ws', 'governance-ws'}
        namespace = {'spark': spark, **arguments}
        # Reference execution is hosted centrally, while the passed caller ID differs.
        original_workspace = runtime.context.get('currentWorkspaceId')
        runtime.context['currentWorkspaceId'] = workspaceId
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
                if workspaceId == 'governance-ws':
                    source = source.replace('"dev-ws"', '"governance-ws"')
                exec(compile(source, '<00_env_config>', 'exec'), namespace)
        except NotebookExit as exc:
            return exc.args[0]
        finally:
            runtime.context['currentWorkspaceId'] = original_workspace
        raise AssertionError('Config notebook must exit with JSON')

    nb.notebook.run = Mock(side_effect=run)
    return SimpleNamespace(runtime=runtime, notebook=nb.notebook, spark=spark, cells=cells)


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
    fabric.notebook.run.assert_called_once_with('00_env_config', 120, {'caller_workspace_id': workspace}, workspaceId='central-ws')
    fabric.spark.conf.set.assert_called_once_with('spark.sql.session.timeZone', config.audit_timezone)


def test_governance_loads_its_separate_local_deployment(configuration_runtime):
    fabric = configuration_runtime
    fabric.runtime.context.update(currentWorkspaceId='governance-ws', currentNotebookName='01_governance')
    assert setup_notebook().environment == 'dev'
    assert fabric.notebook.run.call_args.kwargs['workspaceId'] == 'governance-ws'


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
def test_pipeline_reuses_workspace_initialization(configuration_runtime, monkeypatch, mode, config_workspace):
    shared = importlib.import_module('fabricops_kit.pipeline.shared')
    monkeypatch.setattr(shared, 'get_spark_session', lambda: configuration_runtime.spark)
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
        session = setup_pipeline(pipeline_mode=mode, config_workspace_id=config_workspace)
        assert session.plan.environment == 'dev'
        assert session.plan.pipeline_id == '02_pipeline_orders'
        assert session.plan.runtime_context['config'].path_config.paths['dev']['Metadata'].workspace_id == 'metadata-ws'
        configuration_runtime.notebook.run.assert_called_once_with(
            '00_env_config', 120, {'caller_workspace_id': 'dev-ws'}, workspaceId=config_workspace or 'dev-ws')
        assert session.plan.runtime_context['runtime_metadata']['workspace_id'] == 'dev-ws'
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
    assert configuration_runtime.notebook.run.call_args.kwargs['workspaceId'] == 'dev-ws'



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
