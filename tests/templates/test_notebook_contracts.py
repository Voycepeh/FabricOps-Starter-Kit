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


def _notebook_calls(notebook: nbformat.NotebookNode, function_name: str) -> list[tuple[int, ast.Call]]:
    """Return parsed calls to a named function with their cell positions."""
    calls: list[tuple[int, ast.Call]] = []
    for index, cell in enumerate(notebook.cells):
        if cell.cell_type != "code":
            continue
        tree = _parse_code_cell(Path("notebook.ipynb"), index, cell.source)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == function_name:
                calls.append((index, node))
    return calls


def _keyword(call: ast.Call, name: str) -> ast.expr | None:
    """Return a call's keyword value without depending on source formatting or order."""
    return next((keyword.value for keyword in call.keywords if keyword.arg == name), None)


def _assert_name_keyword(call: ast.Call, keyword: str, variable: str) -> None:
    value = _keyword(call, keyword)
    assert isinstance(value, ast.Name) and value.id == variable, (
        f"{keyword} must use configured variable {variable}, not a hardcoded value"
    )


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



def test_02_pipeline_reads_and_profiles_the_configured_source_table():
    """The pipeline reads the configured source identity before profiling it."""
    notebook = _load_notebook(NOTEBOOK_DIR / "02_pipeline.ipynb")
    read_calls = _notebook_calls(notebook, "read_warehouse_query")
    profile_calls = _notebook_calls(notebook, "profile_and_register_table")

    assert len(read_calls) == 1, "pipeline must read its source exactly once"
    assert profile_calls, "pipeline must profile and register a configured table"
    read_index, read_call = read_calls[0]
    query_argument = _keyword(read_call, "query") or (read_call.args[0] if read_call.args else None)
    assert isinstance(query_argument, ast.Name), "source query must come from a named notebook configuration value"
    query = None
    for index, cell in enumerate(notebook.cells[: read_index + 1]):
        if cell.cell_type != "code":
            continue
        tree = _parse_code_cell(NOTEBOOK_DIR / "02_pipeline.ipynb", index, cell.source)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == query_argument.id for target in node.targets)
            ):
                query = node.value
    assert isinstance(query, ast.JoinedStr), "source query must be built from configured identifiers"
    configured_names = {
        value.value.id
        for value in query.values
        if isinstance(value, ast.FormattedValue) and isinstance(value.value, ast.Name)
    }
    assert {"SOURCE_SCHEMA", "SOURCE_TABLE_NAME"} <= configured_names
    assert any(read_index < index for index, _ in profile_calls), "source read must precede its profiling workflow"


def test_02_pipeline_uses_only_the_catalogue_widget():
    """Verify the simplified pipeline uses only the scoped catalogue widget."""
    source = (NOTEBOOK_DIR / "02_pipeline.ipynb").read_text(encoding="utf-8")

    assert "widget_view_pipeline_catalogue" in source
    assert "widget_view_data_contract" not in source
    assert "widget_author_" not in source
    assert "widget_enrich_" not in source


@pytest.mark.parametrize(
    ("notebook_name", "state_name"),
    [
        ("01_agreement.ipynb", "agreement_catalogue_view"),
        ("02_pipeline.ipynb", "pipeline_catalogue_view"),
        ("03_review.ipynb", "governance_catalogue_view"),
        ("99_explore.ipynb", "data_catalogue_view"),
    ],
)
def test_data_contract_views_are_displayed_outside_the_widget(notebook_name, state_name):
    """Each template renders the named, snapshot-scoped views outside the widget."""
    notebook = _load_notebook(NOTEBOOK_DIR / notebook_name)
    source = "\n".join("".join(cell.get("source", [])) for cell in notebook.cells)

    assert f'{state_name}["get_views"]()' in source
    assert 'catalogue_df = views["catalogue"]' in source
    assert 'profile_df = views["profile"]' in source
    assert 'frequency_df = views["frequency"]' in source
    assert "display(catalogue_df)" in source
    assert "display(profile_df)" in source
    assert "display(frequency_df)" in source
    assert "catalogue_df, profile_df" not in source
    assert "METADATA_DATA_PROFILED_FREQUENCY" not in source
    assert 'get("tables"' not in source


def test_01_agreement_registers_one_logical_draft_contract_after_agreement():
    """The agreement notebook reuses agreement state for one logical contract write."""
    notebook = _load_notebook(NOTEBOOK_DIR / "01_agreement.ipynb")
    agreement_index = _cell_index(notebook, "agreement_widget = widget_render_data_agreement")
    contract_index = _cell_index(notebook, "contract_state = widget_register_data_contract")
    calls = _notebook_calls(notebook, "widget_register_data_contract")

    assert len(calls) == 1
    assert agreement_index < contract_index
    call = calls[0][1]
    _assert_name_keyword(call, "agreement", "agreement_widget")
    _assert_name_keyword(call, "schema", "METADATA_SCHEMA")
    _assert_name_keyword(call, "spark_session", "spark")
    assert isinstance(_keyword(call, "target"), ast.Constant) and _keyword(call, "target").value == "metadata"
    assert _keyword(call, "agreement_id") is None
    assert _keyword(call, "metadata_id") is None


def test_02_pipeline_reviews_only_current_notebook_lineage_after_profiling():
    """The pipeline viewer and output remain scoped and notebook-owned."""
    notebook = _load_notebook(NOTEBOOK_DIR / "02_pipeline.ipynb")
    profile_indices = [
        index for index, cell in enumerate(notebook.cells)
        if "profile_and_register_table(" in cell.source and "from fabricops_kit" not in cell.source
    ]
    viewer_index = _cell_index(notebook, "pipeline_catalogue_view = widget_view_pipeline_catalogue")
    output_index = _cell_index(notebook, 'pipeline_catalogue_view["get_views"]()')
    calls = _notebook_calls(notebook, "widget_view_pipeline_catalogue")

    assert len(calls) == 1
    assert max(profile_indices) < viewer_index < output_index
    call = calls[0][1]
    _assert_name_keyword(call, "schema", "METADATA_SCHEMA")
    _assert_name_keyword(call, "spark_session", "spark")
    assert isinstance(_keyword(call, "target"), ast.Constant) and _keyword(call, "target").value == "metadata"
    assert {keyword.arg for keyword in call.keywords}.isdisjoint({"agreement", "steward_id", "metadata_id"})


def test_03_review_uses_steward_agreement_contract_order_and_scope():
    """Governance review resolves its contract strictly through agreement state."""
    notebook = _load_notebook(NOTEBOOK_DIR / "03_review.ipynb")
    steward_index = _cell_index(notebook, "steward_widget = widget_render_data_steward")
    agreement_index = _cell_index(notebook, "agreement_widget = widget_render_data_agreement")
    viewer_index = _cell_index(notebook, "governance_catalogue_view = widget_view_agreement_catalogue")
    output_index = _cell_index(notebook, 'governance_catalogue_view["get_views"]()')
    calls = _notebook_calls(notebook, "widget_view_agreement_catalogue")

    assert steward_index < agreement_index < viewer_index < output_index
    assert len(calls) == 1
    call = calls[0][1]
    _assert_name_keyword(call, "agreement", "agreement_widget")
    _assert_name_keyword(call, "schema", "METADATA_SCHEMA")
    _assert_name_keyword(call, "spark_session", "spark")
    assert isinstance(_keyword(call, "target"), ast.Constant) and _keyword(call, "target").value == "metadata"
    assert {keyword.arg for keyword in call.keywords}.isdisjoint({"agreement_id", "steward_id", "pipeline_scope"})


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
