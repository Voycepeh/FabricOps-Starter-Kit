"""Execute current demo cells with physical Fabric/Spark boundaries replaced."""
import ast
import inspect
from pathlib import Path
from unittest.mock import MagicMock, Mock

import nbformat
import pytest

ROOT = Path(__file__).resolve().parents[2]
DEMOS = [ROOT/'templates/notebooks/02_pipeline.ipynb', *sorted((ROOT/'templates/DemoData').glob('02*.ipynb'))]


@pytest.mark.parametrize('path', DEMOS, ids=lambda path: path.stem)
def test_four_stage_pipeline_executes_all_reads_and_writes(path):
    """Independent demo notebooks retain their ETL and avoid lifecycle plumbing."""
    frame = MagicMock()
    reads, writes = [], []
    setup = Mock(return_value=object())
    def read(**kwargs):
        assert not {'execution_plan', 'spark_session', 'verbose'}.intersection(kwargs)
        reads.append(kwargs['table_name'])
        return {'dataframe': frame, 'table_name': kwargs['table_name']}
    def write(dataframe, **kwargs):
        assert not {'execution_plan', 'sources', 'spark_session'}.intersection(kwargs)
        writes.append((kwargs['table_name'], kwargs['write_mode']))
        return {'dataframe': dataframe, 'published': False}
    namespace = {'F': MagicMock(), 'spark': object(), 'setup_pipeline': setup,
                 'orchestrate_read': read, 'orchestrate_write': write, 'finalize_pipeline': Mock(),
                 'resolve_table_id': Mock(return_value='incremental-target'), 'display': Mock()}
    notebook = nbformat.read(path, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == 'code' and cell.id not in {'environment','imports'}:
            exec(compile(cell.source, f'{path.name}:{cell.id}', 'exec'), namespace)
    namespace['finalize_pipeline'].assert_called_once_with(setup.return_value)
    setup.assert_called_once_with(pipeline_id=None, pipeline_mode='Test')
    expected = {
        '02_pipeline': (1, ['overwrite']),
        '02A_full_refresh_demo': (3, ['overwrite','overwrite']),
        '02B_incremental_append_demo': (1, ['append']),
        '02C_scd_demo': (1, ['scd1','scd2']),
    }
    count, modes = expected[path.stem]
    assert len(reads) == count and [mode for name, mode in writes] == modes


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
        if cell.cell_type != 'code' or cell.id == 'environment':
            continue
        for node in ast.walk(ast.parse(cell.source)):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                calls.setdefault(node.func.id, []).append(node)
    assert len(calls['setup_pipeline']) == 1
    assert len(calls['finalize_pipeline']) == 1
    assert ids.index('finalize-run') > ids.index('write-heading')
    assert {arg.arg for arg in calls['setup_pipeline'][0].keywords} == {'pipeline_id','pipeline_mode'}
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
