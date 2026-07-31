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


def _cell_index(notebook: nbformat.NotebookNode, text: str) -> int:
    """Return the index of the single cell containing text."""
    matches = [index for index, cell in enumerate(notebook.cells) if text in cell.source]
    assert len(matches) == 1, f"Expected one cell containing {text!r}, found {matches}"
    return matches[0]


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


def test_02_pipeline_uses_only_the_catalogue_widget():
    """Verify the simplified pipeline uses only the scoped catalogue widget."""
    source = (NOTEBOOK_DIR / "02_pipeline.ipynb").read_text(encoding="utf-8")

    assert "widget_view_pipeline_catalogue" in source
    assert "widget_view_data_contract" not in source
    assert "widget_author_" not in source
    assert "widget_enrich_" not in source


@pytest.mark.parametrize(("notebook_name", "state_name"), [("99_explore.ipynb", "data_catalogue_view")])
def test_data_contract_views_are_displayed_outside_the_widget(notebook_name, state_name):
    """Each template renders refreshed views in a separate rerunnable cell."""
    notebook = _load_notebook(NOTEBOOK_DIR / notebook_name)
    source = "\n".join("".join(cell.get("source", [])) for cell in notebook.cells)

    assert f'{state_name}["get_views"]()' in source
    assert "display(catalogue_df)" in source
    assert "display(profile_df)" in source
    assert 'get("tables"' not in source


def test_01_agreement_registers_one_logical_draft_contract_after_agreement():
    """The agreement notebook reuses agreement state for one logical contract write."""
    notebook = _load_notebook(NOTEBOOK_DIR / "01_agreement.ipynb")
    source = "\n".join(cell.source for cell in notebook.cells)
    agreement_index = _cell_index(notebook, "agreement_widget = widget_render_data_agreement")
    contract_index = _cell_index(notebook, "contract_state = widget_register_data_contract")
    contract_source = notebook.cells[contract_index].source

    assert "widget_register_data_contract" in source
    assert agreement_index < contract_index
    assert "agreement=agreement_widget" in contract_source
    assert 'target="metadata"' in contract_source
    assert "schema=METADATA_SCHEMA" in contract_source
    assert "spark_session=spark" in contract_source
    assert "agreement_id=" not in contract_source
    assert "metadata_id" not in contract_source
    assert source.count("widget_render_data_agreement(") == 1
    assert source.count("widget_register_data_contract(") == 1
    assert "logical `metadata_table_key`" in source
    assert "rather than duplicated for each environment" in source


def test_02_pipeline_reviews_only_current_notebook_lineage_after_profiling():
    """The pipeline viewer and output remain scoped and notebook-owned."""
    notebook = _load_notebook(NOTEBOOK_DIR / "02_pipeline.ipynb")
    source = "\n".join(cell.source for cell in notebook.cells)
    profile_indices = [
        index for index, cell in enumerate(notebook.cells)
        if "profile_and_register_table(" in cell.source and "from fabricops_kit" not in cell.source
    ]
    viewer_index = _cell_index(notebook, "pipeline_catalogue_view = widget_view_pipeline_catalogue")
    output_index = _cell_index(notebook, 'pipeline_catalogue_view["get_views"]()')
    viewer_source = notebook.cells[viewer_index].source
    output_source = notebook.cells[output_index].source

    assert "widget_view_pipeline_catalogue" in source
    assert max(profile_indices) < viewer_index < output_index
    assert 'target="metadata"' in viewer_source
    assert "schema=METADATA_SCHEMA" in viewer_source
    assert "spark_session=spark" in viewer_source
    assert "agreement" not in viewer_source
    assert "steward_id" not in viewer_source
    assert "metadata_id" not in viewer_source
    assert source.count("widget_view_pipeline_catalogue(") == 1
    assert "catalogue_df, profile_df" in output_source
    assert "Source" in source and "Target" in source


def test_03_review_uses_steward_agreement_contract_order_and_scope():
    """Governance review resolves its contract strictly through agreement state."""
    notebook = _load_notebook(NOTEBOOK_DIR / "03_review.ipynb")
    source = "\n".join(cell.source for cell in notebook.cells)
    steward_index = _cell_index(notebook, "steward_widget = widget_render_data_steward")
    agreement_index = _cell_index(notebook, "agreement_widget = widget_render_data_agreement")
    viewer_index = _cell_index(notebook, "governance_catalogue_view = widget_view_agreement_catalogue")
    output_index = _cell_index(notebook, 'governance_catalogue_view["get_views"]()')
    viewer_source = notebook.cells[viewer_index].source
    output_source = notebook.cells[output_index].source

    assert steward_index < agreement_index < viewer_index < output_index
    assert "agreement=agreement_widget" in viewer_source
    assert 'target="metadata"' in viewer_source
    assert "schema=METADATA_SCHEMA" in viewer_source
    assert "spark_session=spark" in viewer_source
    assert "agreement_id" not in viewer_source
    assert "steward_id" not in viewer_source
    assert "pipeline_scope" not in viewer_source
    assert source.count("widget_render_data_agreement(") == 1
    assert source.count("widget_view_agreement_catalogue(") == 1
    assert "catalogue_df, profile_df" in output_source
    assert "only linked logical datasets are visible" in source
    assert "Contract membership is shared across Development and Production" in source
    assert "observations remain separate" in source


@pytest.mark.parametrize("notebook_name", ["01_agreement.ipynb", "02_pipeline.ipynb", "03_review.ipynb"])
def test_data_contract_workflow_cells_are_clean(notebook_name):
    """New contract workflow code cells have deterministic, output-free state."""
    notebook = _load_notebook(NOTEBOOK_DIR / notebook_name)
    contract_cells = [
        cell for cell in notebook.cells
        if cell.cell_type == "code"
        and ("widget_register_data_contract(" in cell.source or "widget_view_data_contract(" in cell.source
             or '["get_views"]()' in cell.source)
        and "from fabricops_kit" not in cell.source
    ]
    assert contract_cells
    assert all(cell.execution_count is None for cell in contract_cells)
    assert all(not cell.outputs for cell in contract_cells)
