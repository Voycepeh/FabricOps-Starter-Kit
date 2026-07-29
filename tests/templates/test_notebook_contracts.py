"""Portable contract tests for FabricOps notebook templates.

CI validates notebook file integrity, Python syntax, and public import
compatibility. Full execution against lakehouses, warehouses, Spark, Fabric
widgets, notebook utilities, and workspace context is not reproducible in GitHub
Actions. Successful manual execution by the maintainer in Microsoft Fabric is
the authoritative integration test for runtime behaviour.
"""

from __future__ import annotations

import ast
from collections.abc import Iterable
from pathlib import Path

import nbformat
import pytest

pytestmark = pytest.mark.contract

ROOT = Path(__file__).parents[2]
NOTEBOOK_DIR = ROOT / "templates" / "notebooks"
NOTEBOOKS = tuple(sorted(NOTEBOOK_DIR.glob("*.ipynb")))


def _load_notebook(path: Path) -> nbformat.NotebookNode:
    return nbformat.read(path, as_version=4)


def _code_cells(path: Path) -> Iterable[tuple[int, str]]:
    notebook = _load_notebook(path)
    for index, cell in enumerate(notebook.cells):
        if cell.cell_type == "code":
            yield index, cell.source


def _portable_python_source(source: str) -> str | None:
    """Return Python source for syntax checks, or None for cell magics."""
    lines = source.splitlines()
    if any(line.lstrip().startswith("%%") for line in lines):
        return None
    portable_lines = [
        line
        for line in lines
        if not line.lstrip().startswith(("%", "!"))
    ]
    return "\n".join(portable_lines).strip() or "pass"


def _parse_code_cell(path: Path, cell_index: int, source: str) -> ast.Module | None:
    portable_source = _portable_python_source(source)
    if portable_source is None:
        return None
    try:
        return ast.parse(portable_source, filename=f"{path}:{cell_index}")
    except SyntaxError as exc:  # pragma: no cover - assertion path includes notebook context.
        raise AssertionError(f"Invalid Python syntax in {path.name} cell {cell_index}: {exc}") from exc


def _fabricops_imported_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "fabricops_kit":
            names.update(alias.name for alias in node.names if alias.name != "*")
    return names


def _fabricops_aliases(tree: ast.Module) -> set[str]:
    aliases: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "fabricops_kit":
                    aliases.add(alias.asname or "fabricops_kit")
    return aliases


def _fabricops_attribute_references(tree: ast.Module) -> set[str]:
    aliases = _fabricops_aliases(tree)
    references: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id in aliases
        ):
            references.add(node.attr)
    return references


@pytest.mark.parametrize("notebook_path", NOTEBOOKS, ids=lambda path: path.name)
def test_template_notebooks_are_valid_and_code_cells_compile(notebook_path: Path):
    """Validate committed template notebooks and portable Python syntax."""
    notebook = _load_notebook(notebook_path)
    nbformat.validate(notebook)

    for cell_index, source in _code_cells(notebook_path):
        tree = _parse_code_cell(notebook_path, cell_index, source)
        if tree is not None:
            compile(tree, filename=f"{notebook_path}:{cell_index}", mode="exec")

@pytest.mark.parametrize("notebook_path", NOTEBOOKS, ids=lambda path: path.name)
def test_template_notebook_fabricops_public_references_exist(notebook_path: Path):
    """Verify notebooks do not reference stale public fabricops_kit names."""
    import fabricops_kit

    missing: list[str] = []
    for cell_index, source in _code_cells(notebook_path):
        tree = _parse_code_cell(notebook_path, cell_index, source)
        if tree is None:
            continue
        referenced_names = _fabricops_imported_names(tree) | _fabricops_attribute_references(tree)
        missing.extend(
            f"cell {cell_index}: {name}"
            for name in sorted(referenced_names)
            if not hasattr(fabricops_kit, name)
        )

    assert not missing, f"Missing fabricops_kit public references in {notebook_path.name}: {missing}"



def test_02_pipeline_presents_the_v02_table_workflow():
    """Verify 02_pipeline contains only the focused v0.2 table workflow."""
    source = (NOTEBOOK_DIR / "02_pipeline.ipynb").read_text(encoding="utf-8")

    assert "profile_and_register_table" in source
    assert "profile_and_register_dataframe" not in source
    assert source.count("# Planned for v0.3.0") == 2
    assert "read_warehouse_query" in source
    assert "SELECT * FROM {SOURCE_SCHEMA}.{SOURCE_TABLE_NAME}" in source
    assert "prepare_pipeline_table_configs" not in source
    assert "run_table_guardrails" not in source


def test_02_pipeline_uses_only_the_contract_widget():
    """Verify the simplified pipeline uses only the requested contract widget."""
    source = (NOTEBOOK_DIR / "02_pipeline.ipynb").read_text(encoding="utf-8")

    assert "widget_view_data_contract" in source
    assert "widget_author_" not in source
    assert "widget_enrich_" not in source


@pytest.mark.parametrize(
    ("notebook_name", "state_name"),
    [
        ("01_agreement.ipynb", "agreement_contract_view"),
        ("02_pipeline.ipynb", "pipeline_contract_view"),
        ("03_review.ipynb", "review_contract_view"),
        ("99_explore.ipynb", "data_contract_view"),
    ],
)
def test_data_contract_views_are_displayed_outside_the_widget(notebook_name, state_name):
    """Each template renders refreshed views in a separate rerunnable cell."""
    notebook = _load_notebook(NOTEBOOK_DIR / notebook_name)
    source = "\n".join("".join(cell.get("source", [])) for cell in notebook.cells)

    assert "Select a dataset above, then rerun this cell" in source
    assert f'{state_name}["get_views"]()' in source
    assert 'for table_name, frame in metadata_views["tables"].items()' in source
    assert 'print("Sorted by _committed_at descending")' in source
    assert "display(frame)" in source
