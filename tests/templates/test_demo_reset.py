"""Demo notebook exposes only public functions and one reset switch."""
# ruff: noqa: D103
import ast
from pathlib import Path

import nbformat
import pytest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / 'templates/DemoData/00C_demo_setup.ipynb'
CELLS = {cell.id: cell.source for cell in nbformat.read(NOTEBOOK, as_version=4).cells}
WRITE_EXAMPLE_CELLS = {
    '7c5f1da6-05e4-4a47-b366-44bd98f7efaa',
    '66cfd20c-2601-4b53-8abf-b32fd2b0b8ea',
}


def test_reset_is_one_code_cell_and_false_cannot_write_later_cells():
    notebook = nbformat.read(NOTEBOOK, as_version=4); nbformat.validate(notebook)
    assert [c.id for c in notebook.cells if c.id.startswith('reset') and c.cell_type == 'code'] == ['reset']
    assert CELLS['reset'].startswith('RESET_DEMO = False')
    assert 'orchestrate_demo_reset(reset=RESET_DEMO)' in CELLS['reset']
    assert len(CELLS['reset'].splitlines()) <= 5
    cell_ids = [cell.id for cell in notebook.cells]
    assert cell_ids.index('reset') < cell_ids.index('f301cfb3-3d29-41b5-87b3-28335c93a447')
    for cell in notebook.cells:
        if cell.cell_type != 'code': continue
        compile(cell.source, str(NOTEBOOK), 'exec')
        assert not any(isinstance(node, ast.FunctionDef) for node in ast.walk(ast.parse(cell.source)))
        for node in ast.walk(ast.parse(cell.source)):
            if isinstance(node, ast.ImportFrom) and (node.module or '').startswith('fabricops_kit'):
                assert node.module == 'fabricops_kit'
                import fabricops_kit
                assert all(alias.name in fabricops_kit.__all__ for alias in node.names)
        if cell.id in WRITE_EXAMPLE_CELLS:
            statements = ast.parse(cell.source).body
            assert len(statements) == 1 and isinstance(statements[0], ast.If)
            assert ast.unparse(statements[0].test) == 'RESET_DEMO'
            assert not statements[0].orelse
            exec(cell.source, {'RESET_DEMO': False})
        elif cell.id != 'reset':
            assert 'write_lakehouse_table(' not in cell.source and 'write_warehouse_table(' not in cell.source


def test_demo_calls_every_foundational_io_function():
    from fabricops_kit import IO_EXPORTS

    calls = {
        node.func.id
        for cell in nbformat.read(NOTEBOOK, as_version=4).cells
        if cell.cell_type == 'code'
        for node in ast.walk(ast.parse(cell.source))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert set(IO_EXPORTS) <= calls


@pytest.mark.parametrize('cell_id,kind,store,table,rows', [
    ('7c5f1da6-05e4-4a47-b366-44bd98f7efaa', 'lakehouse', 'Bronze', 'products', 8),
    ('66cfd20c-2601-4b53-8abf-b32fd2b0b8ea', 'warehouse', 'Gold', 'order_history', 180),
])
def test_write_examples_restore_only_the_day1_fixtures(cell_id, kind, store, table, rows):
    fixture = Mock()
    fixture.count.return_value = rows
    persisted = Mock()
    persisted.count.return_value = rows
    sample = Mock()
    sample.count.return_value = 5
    reader = Mock(return_value=fixture)
    writer = Mock()
    table_reader = Mock(return_value=persisted)
    query_reader = Mock(return_value=sample)
    namespace = {
        'RESET_DEMO': True,
        'read_lakehouse_csv': reader,
        f'write_{kind}_table': writer,
        f'read_{kind}_table': table_reader,
        f'read_{kind}_query': query_reader,
        'display': Mock(),
    }
    exec(CELLS[cell_id], namespace)
    reader.assert_called_once_with(f'demo/{table}.csv', store='Bronze', header=True, inferSchema=True)
    writer.assert_called_once_with(fixture, table_name=table, store=store, schema='demo', mode='overwrite')
    table_reader.assert_called_once_with(table_name=table, store=store, schema='demo')
    assert f'FROM demo.{table}' in query_reader.call_args.args[0]
    assert query_reader.call_args.kwargs['store'] == store
    namespace['display'].assert_called_once_with(sample)


def test_demo_file_paths_are_lowercase():
    for path in (ROOT / 'templates/DemoData').glob('*.ipynb'):
        assert 'Demo/' not in path.read_text()



def test_guided_demo_puts_the_single_boolean_reset_before_io_examples():
    page = (ROOT / 'docs/guided-demo/00C-prepare-demo-data-with-fabricops-io.md').read_text()
    assert page.index('## Reset, rerun and validate a package') < page.index('## Read the same Orders')
    assert 'RESET_DEMO = False' in page and 'RESET COMPLETE' in page
    assert 'RESET_CONFIRMATION' not in page and 'EXTRA_DEMO_NOTEBOOK_IDS' not in page
    assert 'all rows in the 14 metadata tables' in page
    assert 'saved submissions' in page and 'manually created' in page
