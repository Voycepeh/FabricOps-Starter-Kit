"""Execute current demo cells with physical Fabric/Spark boundaries replaced."""
import ast
import inspect
from pathlib import Path
from unittest.mock import MagicMock, Mock
from types import SimpleNamespace

import nbformat
import pytest

ROOT = Path(__file__).resolve().parents[2]
DEMOS = [ROOT/'templates/notebooks/02_pipeline.ipynb', *sorted((ROOT/'templates/DemoData').glob('02*.ipynb'))]



@pytest.mark.parametrize('path', DEMOS, ids=lambda path: path.stem)
def test_four_stage_pipeline_executes_all_reads_and_writes(path):
    """Independent demo notebooks retain their ETL and avoid lifecycle plumbing."""
    notebook = nbformat.read(path, as_version=4)
    frame = MagicMock()
    reads, writes = [], []
    notebook_setup = Mock()
    sessions = [SimpleNamespace(), SimpleNamespace()]
    setup = Mock(side_effect=sessions)
    def read(**kwargs):
        assert not {'execution_plan', 'spark_session'}.intersection(kwargs)
        assert kwargs.get('verbose') is True
        reads.append(kwargs.get('relative_path') or kwargs['table_name'])
        return {'dataframe': frame, **({'source_id': 'file:orders', 'source_type': 'file'} if kwargs.get('relative_path') else {'table_name': kwargs['table_name']})}
    def write(dataframe, **kwargs):
        assert not {'execution_plan', 'sources', 'spark_session'}.intersection(kwargs)
        writes.append((kwargs['table_name'], kwargs['write_mode']))
        return {'dataframe': dataframe, 'published': False}
    namespace = {'F': MagicMock(), 'spark': object(), 'setup_pipeline': setup, 'setup_notebook': notebook_setup,
                 'orchestrate_read': read, 'orchestrate_write': write, 'finalize_pipeline': Mock(return_value={'execution_mode': 'ungoverned', 'status': 'ungoverned_completed'}),
                 'read_lakehouse_table': Mock(return_value=MagicMock()),
                 'display': Mock()}
    for cell in notebook.cells:
        if cell.cell_type != 'code':
            continue
        tree = ast.parse(cell.source)
        tree.body = [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom))]
        exec(compile(tree, f'{path.name}:{cell.id}', 'exec'), namespace)
    expected_sessions = 2 if path.stem == '02B_incremental_append_demo' else 1
    assert namespace['finalize_pipeline'].call_count == expected_sessions
    assert [call.args[0] for call in namespace['finalize_pipeline'].call_args_list] == sessions[:expected_sessions]
    notebook_setup.assert_called_once_with()
    observation = dict(source_drift_enabled=False, source_drift_interval_days=1, source_drift_block=True)
    if path.stem == '02_pipeline':
        from fabricops_kit.pipeline.shared import validate_pipeline_profiling
        observation.update(validate_pipeline_profiling())
    assert setup.call_count == expected_sessions
    assert all(call.kwargs == {'pipeline_mode': 'Ungoverned', **observation} for call in setup.call_args_list)
    expected = {
        '02_pipeline': (1, ['overwrite']),
        '02A_full_refresh_demo': (3, ['overwrite','overwrite']),
        '02B_incremental_append_demo': (2, ['append_all','append_new_only']),
        '02C_scd_demo': (1, ['scd1','scd2']),
    }
    count, modes = expected[path.stem]
    assert len(reads) == count and [mode for name, mode in writes] == modes
    if path.stem == '02A_full_refresh_demo':
        assert reads == ['demo/orders.csv', 'products', 'order_history']



@pytest.mark.parametrize('path', DEMOS, ids=lambda path: path.stem)
def test_notebooks_keep_user_owned_transform_surface(path):
    """Every example preserves explicit operations around an isolated transformation cell."""
    notebook = nbformat.read(path, as_version=4)
    ids = [cell.id for cell in notebook.cells]
    stages = ['contracts','read-heading','transform','write-heading']
    assert [ids.index(stage) for stage in stages] == sorted(ids.index(stage) for stage in stages)
    assert not {'execution-plan','inspect'}.intersection(ids)
    calls = {}
    for cell in notebook.cells:
        if cell.cell_type != 'code' or cell.id == 'workspace_id':
            continue
        for node in ast.walk(ast.parse(cell.source)):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                calls.setdefault(node.func.id, []).append(node)
    assert len(calls['setup_notebook']) == 1
    expected_executions = 2 if path.stem == '02B_incremental_append_demo' else 1
    assert len(calls['setup_pipeline']) == expected_executions
    assert len(calls['finalize_pipeline']) == expected_executions
    assert ids.index('finalize-run') > ids.index('write-heading')
    expected_setup = {'pipeline_mode', 'source_drift_enabled', 'source_drift_interval_days', 'source_drift_block'}
    if path.stem == '02_pipeline':
        expected_setup |= {'profiling_enabled', 'profiling_interval_days', 'profiling_max_rows', 'grain_discovery_enabled', 'frequency_enabled'}
    assert all({arg.arg for arg in call.keywords} == expected_setup for call in calls['setup_pipeline'])
    transform = next(cell.source for cell in notebook.cells if cell.id == 'transform')
    assert 'orchestrate_' not in transform


@pytest.mark.parametrize('path', DEMOS, ids=lambda path: path.stem)
def test_notebook_orchestrator_calls_match_public_signatures(path):
    """Keep runnable Read/Write templates synchronized with their real public APIs."""
    from fabricops_kit.pipeline.orchestrate_read import orchestrate_read
    from fabricops_kit.pipeline.orchestrate_write import orchestrate_write

    accepted = {
        'orchestrate_read': set(inspect.signature(orchestrate_read).parameters),
        'orchestrate_write': set(inspect.signature(orchestrate_write).parameters),
    }
    notebook = nbformat.read(path, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type != 'code':
            continue
        for node in ast.walk(ast.parse(cell.source)):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            valid = accepted.get(node.func.id)
            if valid is None:
                continue
            invalid = {arg.arg for arg in node.keywords} - valid
            assert not invalid, f"{path.name}:{cell.id} passes unsupported {node.func.id} options: {sorted(invalid)}"
