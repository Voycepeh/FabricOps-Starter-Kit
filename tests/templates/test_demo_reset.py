"""Demo notebook exposes only public functions and one reset switch."""
# ruff: noqa: D103
import ast
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / 'templates/DemoData/00C_demo_setup.ipynb'
CELLS = {cell.id: cell.source for cell in nbformat.read(NOTEBOOK, as_version=4).cells}


def test_reset_is_one_code_cell_and_false_cannot_write_later_cells():
    notebook = nbformat.read(NOTEBOOK, as_version=4); nbformat.validate(notebook)
    assert [c.id for c in notebook.cells if c.id.startswith('reset') and c.cell_type == 'code'] == ['reset']
    assert CELLS['reset'].startswith('RESET_DEMO = False')
    assert 'orchestrate_demo_reset(reset=RESET_DEMO)' in CELLS['reset']
    assert len(CELLS['reset'].splitlines()) <= 5
    for cell in notebook.cells:
        if cell.cell_type != 'code': continue
        compile(cell.source, str(NOTEBOOK), 'exec')
        assert not any(isinstance(node, ast.FunctionDef) for node in ast.walk(ast.parse(cell.source)))
        for node in ast.walk(ast.parse(cell.source)):
            if isinstance(node, ast.ImportFrom) and (node.module or '').startswith('fabricops_kit'):
                assert node.module == 'fabricops_kit'
                import fabricops_kit
                assert all(alias.name in fabricops_kit.__all__ for alias in node.names)
        if cell.id != 'reset':
            assert 'write_lakehouse_table(' not in cell.source and 'write_warehouse_table(' not in cell.source


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
