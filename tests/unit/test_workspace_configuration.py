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
from fabricops_kit.config.shared import resolve_fabric_context
from tests.unit.test_setup_notebook_store_keys import _config

pytestmark = pytest.mark.unit


class NotebookExit(Exception):
    """Model Fabric notebook.exit stopping the reference notebook."""


@pytest.fixture
def configuration_runtime(monkeypatch):
    """Keep config construction and validation real; simulate only Fabric services."""
    import builtins

    monkeypatch.delattr(builtins, 'FABRIC_CONTEXT', raising=False)
    monkeypatch.delenv('FABRICOPS_CONFIG_WORKSPACE_ID', raising=False)
    monkeypatch.setattr(builtins, 'FABRIC_CONTEXT', None, raising=False)
    runtime = ModuleType('notebookutils.runtime')
    runtime.context = {'currentWorkspaceId': 'dev-ws', 'currentNotebookName': '02_pipeline_orders',
                       'currentRunId': 'caller-run', 'currentNotebookId': 'caller-notebook'}
    nb = ModuleType('notebookutils')
    nb.runtime = runtime
    nb.notebook = SimpleNamespace(exit=lambda payload: (_ for _ in ()).throw(NotebookExit(payload)))
    monkeypatch.setitem(sys.modules, 'notebookutils', nb)
    monkeypatch.setitem(sys.modules, 'notebookutils.runtime', runtime)
    spark = SimpleNamespace(conf=SimpleNamespace(set=Mock()))
    monkeypatch.setattr(importlib.import_module('fabricops_kit.io.shared'), 'get_spark_session', lambda: spark)
    cells = json.loads(Path('templates/notebooks/00_env_config.ipynb').read_text())['cells']

    def run(name, timeout, arguments, *, workspaceId):
        assert name == '00_env_config'
        assert workspaceId in {'central-ws', 'dev-ws', 'governance-ws'}
        namespace = {'spark': spark, **arguments}
        # Reference execution is hosted centrally, while the passed caller ID differs.
        original_workspace = runtime.context['currentWorkspaceId']
        runtime.context['currentWorkspaceId'] = workspaceId
        try:
            for cell in cells:
                if cell['cell_type'] != 'code' or 'parameters' in cell['metadata'].get('tags', []):
                    continue
                source = ''.join(cell['source'])
                source = source.replace('<engineering-development-workspace-id>', 'dev-ws')
                source = source.replace('<engineering-production-workspace-id>', 'prod-ws')
                source = source.replace('workspace_id=""', 'workspace_id="resource-ws"')
                source = source.replace('item_id=""', 'item_id="resource-item"')
                source = source.replace('METADATA_WORKSPACE_ID = ""', 'METADATA_WORKSPACE_ID = "metadata-ws"')
                source = source.replace('METADATA_ITEM_ID = ""', 'METADATA_ITEM_ID = "metadata-item"')
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
    monkeypatch.setenv('FABRICOPS_CONFIG_WORKSPACE_ID', 'central-ws')
    fabric.runtime.context['currentWorkspaceId'] = workspace
    result = setup_notebook()
    assert result.environment == environment
    assert set(result.paths) == {'Bronze', 'Silver', 'Gold', 'Metadata'}
    assert result.paths['Silver'].env == environment
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
    monkeypatch.setenv('FABRICOPS_CONFIG_WORKSPACE_ID', 'central-ws')
    configuration_runtime.runtime.context['currentWorkspaceId'] = 'unregistered'
    with pytest.raises(ValueError, match='Unknown workspace ID'):
        setup_notebook()


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
def test_pipeline_reuses_workspace_initialization(configuration_runtime, monkeypatch, mode):
    monkeypatch.setenv('FABRICOPS_CONFIG_WORKSPACE_ID', 'central-ws')
    shared = importlib.import_module('fabricops_kit.pipeline.shared')
    observed = []

    def start(pipeline_id, pipeline_mode, *, inspector):
        config, env, runtime = resolve_fabric_context()
        observed.append((pipeline_id, pipeline_mode, env, config.path_config.paths[env]['Metadata'].workspace_id))
        return 'session'

    monkeypatch.setattr(shared, 'start_pipeline_session', start)
    result = setup_pipeline(pipeline_mode=mode)
    assert result == 'session'
    assert observed == [('02_pipeline_orders', mode, 'dev', 'metadata-ws')]


def test_duplicate_workspace_assignments_are_rejected(configuration_runtime):
    for cell in configuration_runtime.cells:
        cell['source'] = [line.replace('<engineering-production-workspace-id>', '<engineering-development-workspace-id>')
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
