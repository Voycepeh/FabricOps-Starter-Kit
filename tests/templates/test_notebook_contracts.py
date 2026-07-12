"""Portable contract tests for FabricOps notebook templates.

CI validates notebook file integrity, Python syntax, and public import
compatibility. CI may perform limited sequential execution with Fabric services
stubbed. Full execution against lakehouses, warehouses, Spark, Fabric widgets,
notebook utilities, and workspace context is not reproducible in GitHub Actions.
Successful manual execution by the maintainer in Microsoft Fabric is the
authoritative integration test.
"""

from __future__ import annotations

import ast
from collections.abc import Iterable
from pathlib import Path
import types
from unittest.mock import Mock

import pytest

nbformat = pytest.importorskip("nbformat")

pytestmark = pytest.mark.contract

ROOT = Path(__file__).parents[2]
NOTEBOOK_DIR = ROOT / "templates" / "notebooks"
NOTEBOOKS = tuple(sorted(NOTEBOOK_DIR.glob("*.ipynb")))

FABRIC_ONLY_TOKENS = (
    "spark",
    "notebookutils",
    "mssparkutils",
    "display(",
    "ip.display(",
    "read_lakehouse_",
    "write_lakehouse_",
    "read_warehouse_",
    "write_warehouse_",
    "widget_",
    "run_table_guardrails(",
    "profile_dataframe(",
    "prepare_pipeline_table_configs(",
    "write_pipeline_lineage(",
    "write_pipeline_run_summary(",
)


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


def _requires_fabric_runtime(source: str) -> bool:
    if any(line.lstrip().startswith(("%run", "%%", "!")) for line in source.splitlines()):
        return True
    return any(token in source for token in FABRIC_ONLY_TOKENS)


def _execution_namespace() -> dict[str, object]:
    fabric_utils = types.SimpleNamespace(
        notebook=types.SimpleNamespace(run=Mock(name="notebook.run")),
        fs=Mock(name="fs"),
    )
    return {
        "__name__": "__fabricops_template_contract__",
        "spark": Mock(name="spark"),
        "notebookutils": fabric_utils,
        "mssparkutils": fabric_utils,
        "display": Mock(name="display"),
    }


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


@pytest.mark.parametrize("notebook_path", NOTEBOOKS, ids=lambda path: path.name)
def test_template_notebook_portable_cells_execute_sequentially(notebook_path: Path):
    """Execute portable code cells in order while skipping Fabric-only boundaries."""
    namespace = _execution_namespace()
    executed_cells: list[int] = []
    skipped_cells: list[int] = []

    for cell_index, source in _code_cells(notebook_path):
        tree = _parse_code_cell(notebook_path, cell_index, source)
        if tree is None or _requires_fabric_runtime(source):
            skipped_cells.append(cell_index)
            continue
        try:
            exec(compile(tree, filename=f"{notebook_path}:{cell_index}", mode="exec"), namespace)
        except (ImportError, ModuleNotFoundError) as exc:
            if exc.name in {"notebookutils", "mssparkutils", "pyspark", "IPython", "ipywidgets"}:
                skipped_cells.append(cell_index)
                continue
            raise AssertionError(f"Import failed in {notebook_path.name} cell {cell_index}: {exc}") from exc
        except NameError as exc:
            raise AssertionError(f"Undefined name in {notebook_path.name} cell {cell_index}: {exc}") from exc
        executed_cells.append(cell_index)

    assert executed_cells or skipped_cells
