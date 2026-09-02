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


def _cell_by_id(notebook_name: str, cell_id: str) -> nbformat.NotebookNode:
    notebook = _load_notebook(NOTEBOOK_DIR / notebook_name)
    return next(cell for cell in notebook.cells if cell.get("id") == cell_id)


def _preview_payload(notebook_name: str, cell_id: str) -> str:
    """Return Python stored inside one disabled triple-quoted Preview code cell."""
    cell = _cell_by_id(notebook_name, cell_id)
    assert cell.cell_type == "code"
    assert cell.metadata.get("collapsed") is True
    tree = ast.parse(cell.source)
    assert len(tree.body) == 1
    expression = tree.body[0]
    assert isinstance(expression, ast.Expr)
    assert isinstance(expression.value, ast.Constant)
    assert isinstance(expression.value.value, str)
    payload_lines = expression.value.value.splitlines()
    while payload_lines and not payload_lines[0].strip():
        payload_lines = payload_lines[1:]
    if payload_lines and payload_lines[0].lstrip().startswith("PREVIEW "):
        payload_lines = payload_lines[1:]
    return "\n".join(payload_lines).lstrip()


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


def _notebook_source(notebook_name: str) -> str:
    notebook = _load_notebook(NOTEBOOK_DIR / notebook_name)
    return "\n".join(cell.source for cell in notebook.cells)


def test_official_governance_workflow_inventory():
    """The active templates expose one persistent Governance entry point."""
    names = {path.name for path in NOTEBOOKS}

    assert {"00_env_config.ipynb", "01_governance.ipynb", "02_pipeline.ipynb", "99_explore.ipynb"} <= names
    assert {"01_agreement.ipynb", "03_review.ipynb"}.isdisjoint(names)


def test_01_governance_supports_the_complete_governance_lifecycle():
    """Governance retains the durable capabilities from both former templates."""
    source = _notebook_source("01_governance.ipynb")
    required_functions = {
        "widget_render_data_steward",
        "widget_render_data_agreement",
        "widget_register_data_contract",
        "widget_view_catalogue",
        "widget_enrich_table_metadata",
        "widget_author_guardrails",
        "widget_author_dq_rules",
    }

    assert required_functions <= {node.id for tree in (
        _parse_code_cell(NOTEBOOK_DIR / "01_governance.ipynb", index, source)
        for index, source in _code_cells(NOTEBOOK_DIR / "01_governance.ipynb")
    ) if tree is not None for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert 'target="metadata"' in source
    assert 'mode="agreement"' in source
    assert "METADATA_SCHEMA" not in source


def test_02_pipeline_uses_public_cloneable_governed_blocks():
    """The canonical template keeps governed source, transform, and target steps visible."""
    source = _notebook_source("02_pipeline.ipynb")

    assert _cell_by_id("02_pipeline.ipynb", "source-prepare").source.count("read_pipeline_prep(") == 1
    assert _cell_by_id("02_pipeline.ipynb", "target-prepare").source.count("write_pipeline_prep(") == 1
    assert 'processing_scope=source_prep["scope"]' in source
    assert 'completion_context' not in source
    assert 'target_prep["completion"]' not in source
    for state in (
        "SOURCES", "SOURCE_PREPS", "SOURCE_DFS", "SOURCE_PROFILES", "SOURCE_RESULTS",
        "TARGETS", "TARGET_DFS", "TARGET_PREPS", "TARGET_RESULTS", "TARGET_CONTRACTS",
    ):
        assert f"{state} = {{}}" in source
    assert "globals()" not in source
    assert "locals()" not in source
    assert "exec(" not in source
    assert "run_pipeline(" not in source
    assert "build_table_id(" not in source
    assert "commit_pipeline_checkpoint(" not in source
    assert "from fabricops_kit.pipeline.shared" not in source
    assert "from fabricops_kit.io.shared" not in source


def test_02_pipeline_uses_canonical_source_strategy_and_read_mode_terms():
    """Keep configured strategies distinct from execution-time read modes."""
    source = _notebook_source("02_pipeline.ipynb")

    for strategy in ("full_dataset", "incremental_watermark", "incremental_partition"):
        assert strategy in source
    for read_mode in ("skip", "full_dataset", "incremental_subset"):
        assert read_mode in source
    assert 'read_prep["read_strategy"]' not in source
    assert "source_1_df.where(" not in source
    assert ".isin(" not in source


def test_02_pipeline_dispatches_registered_source_readers_from_catalogue():
    """Keep both physical registered-table readers explicit and Catalogue-driven."""
    config = _cell_by_id("02_pipeline.ipynb", "source-config").source
    read = _cell_by_id("02_pipeline.ipynb", "source-read").source

    assert '"store_type": source_selection["store_type"]' in config
    assert 'SOURCE_DFS[SOURCE] = read_warehouse_table(' in read
    assert 'SOURCE_DFS[SOURCE] = read_lakehouse_table(' in read
    assert 'processing_scope=source_prep["scope"]' in read


def test_02_pipeline_selects_registered_target_and_data_contract_by_table_id():
    """Resolve the target from Catalogue metadata before selecting its Data Contract."""
    source = _notebook_source("02_pipeline.ipynb")
    selection = _cell_by_id("02_pipeline.ipynb", "target-selection").source
    contract = _cell_by_id("02_pipeline.ipynb", "target-contract").source

    assert 'widget_view_catalogue(' in selection
    assert 'mode="explore"' in selection
    assert 'target_selection = target_catalogue["get_selection"]()' in selection
    assert '"table_id": target_selection["table_id"]' in selection
    assert "<canonical table_id already created in FabricOps metadata>" not in source
    assert "TARGET_CONTRACTS[TARGET] = widget_select_data_contract(" in contract
    assert 'table_id=target["table_id"]' in contract
    assert 'target_table_id=target["table_id"]' in source
    assert "TARGET_LOAD_STRATEGY" not in source


def test_02_pipeline_skips_physical_and_downstream_work_safely():
    """The runnable path must not read, transform, or publish after a skip decision."""
    notebook = _load_notebook(NOTEBOOK_DIR / "02_pipeline.ipynb")
    by_id = {cell.get("id"): cell for cell in notebook.cells}

    prepare = by_id["source-prepare"].source
    read = by_id["source-read"].source
    transform = by_id["transform"].source
    target_prepare = by_id["target-prepare"].source
    publish = by_id["target-publish"].source

    assert 'SHOULD_RUN = source_prep["read_mode"] != "skip"' in prepare
    assert "if not SHOULD_RUN:" in read
    assert "read_warehouse_table(" in read
    assert "if SHOULD_RUN:" in transform
    assert "if SHOULD_RUN:" in target_prepare
    assert "if SHOULD_RUN:" in publish


def test_02_pipeline_profiles_full_sources_without_registering_incremental_slices():
    """Only a complete physical source can replace the canonical source profile."""
    source = _cell_by_id("02_pipeline.ipynb", "source-quality").source
    tree = ast.parse(source)

    mode_if = next(
        node for node in ast.walk(tree)
        if isinstance(node, ast.If) and "read_mode" in ast.unparse(node.test)
    )
    assert "full_dataset" in ast.unparse(mode_if.test)
    assert "profile_and_register_table(" in ast.unparse(mode_if.body)
    assert "incremental_subset" in ast.unparse(mode_if.orelse)
    assert "profile_dataframe(" in ast.unparse(mode_if.orelse)
    assert "profile_and_register_table(" not in ast.unparse(mode_if.orelse)


def test_02_pipeline_passes_all_prepared_lakehouse_writer_values():
    """Publication consumes the exact governed preparation fields without completion plumbing."""
    source = _cell_by_id("02_pipeline.ipynb", "target-publish").source

    for argument in (
        'mode=target_prep["mode"]',
        'options=target_prep["options"]',
        'load_strategy=target_prep["load_strategy"]',
        'load_strategy_parameters=target_prep["load_strategy_parameters"]',
        'processing_scope=target_prep["scope"]',
    ):
        assert argument in source


def test_02_pipeline_separates_source_and_target_ownership():
    """Target selection begins after Transform and each side uses its canonical table ID."""
    source = _notebook_source("02_pipeline.ipynb")
    extract = source.split("# E. Extract", 1)[1].split("# T. Transform", 1)[0]
    source_prepare = _cell_by_id("02_pipeline.ipynb", "source-prepare").source
    target_guard = _cell_by_id("02_pipeline.ipynb", "target-guard").source

    assert "TARGET" not in extract
    assert 'source_table_id=source["table_id"]' in source_prepare
    assert 'check_schema(table_id=source["table_id"])' in source_prepare
    assert 'table_id=source["table_id"]' in source_prepare
    assert 'table_id=target["table_id"]' in target_guard
    assert 'check_dq(' in target_guard


def test_02_pipeline_documents_cloneable_integer_blocks_and_publication_caution():
    """One source and target are active while indexed cloning remains truthful."""
    source = _notebook_source("02_pipeline.ipynb")

    assert "SOURCE = 1" in source
    assert "TARGET = 1" in source
    assert "SOURCE = 2" in source
    assert "TARGET = 2" in source
    assert "SOURCE_DFS[1]" in source
    assert "SOURCE_DFS[2]" in source
    assert "TARGET_DFS[2] = summary_df" in source
    assert "FabricOps recommends one governed target per pipeline" in source
    assert "independently committed" in source
    assert "not automatically rolled back together" in source
    for obsolete in ("source_1_df", "source_2_df", "SOURCE_1_TABLE_NAME", "TARGET_1_TABLE_NAME"):
        assert obsolete not in source


def test_02_pipeline_keeps_raw_files_outside_registered_table_semantics():
    """Raw reader alternatives need no manufactured table identity or changes check."""
    source = _cell_by_id("02_pipeline.ipynb", "optional-source-examples").source

    for reader in ("read_lakehouse_csv(", "read_lakehouse_excel(", "read_lakehouse_parquet("):
        assert reader in source
    assert "table_id" not in source
    assert "check_changes(" not in source


def test_02_pipeline_keeps_main_governed_path_runnable():
    """The canonical workflow is expanded rather than stored in disabled Preview strings."""
    notebook = _load_notebook(NOTEBOOK_DIR / "02_pipeline.ipynb")
    governed_ids = {
        "target-selection", "source-config", "source-prepare", "source-read", "source-quality",
        "transform", "target-prepare", "target-publish",
    }
    by_id = {cell.get("id"): cell for cell in notebook.cells}

    for cell_id in governed_ids:
        cell = by_id[cell_id]
        assert cell.cell_type == "code"
        assert cell.metadata.get("collapsed") is False
        tree = ast.parse(cell.source)
        assert not (
            len(tree.body) == 1
            and isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, ast.Constant)
            and isinstance(tree.body[0].value.value, str)
        )

    source = _notebook_source("02_pipeline.ipynb")
    assert "Preview —" not in source
    assert "write_warehouse_table(" in source


@pytest.mark.parametrize(
    ("notebook_name", "state_name"),
    [
        ("01_governance.ipynb", "agreement_catalogue_view"),
        ("99_explore.ipynb", "data_catalogue_view"),
    ],
)
def test_catalogue_views_are_displayed_outside_the_widget(notebook_name, state_name):
    """Live catalogue workflows render their snapshot-scoped views in Fabric cells."""
    source = _notebook_source(notebook_name)
    views_name = "views"

    assert f'{state_name}["get_views"]()' in source
    assert f'catalogue_df = {views_name}["catalogue"]' in source
    assert f'profile_df = {views_name}["profile"]' in source
    assert f'frequency_df = {views_name}["frequency"]' in source
    assert "display(catalogue_df)" in source
    assert "display(profile_df)" in source
    assert "display(frequency_df)" in source

def test_governance_workflow_cells_are_output_free():
    """Committed Governance workflow cells do not retain Fabric execution state."""
    notebook = _load_notebook(NOTEBOOK_DIR / "01_governance.ipynb")
    workflow_cells = [
        cell for cell in notebook.cells
        if cell.cell_type == "code" and "widget_" in cell.source and "from fabricops_kit" not in cell.source
    ]

    assert workflow_cells
    assert all(cell.execution_count is None for cell in workflow_cells)
    assert all(not cell.outputs for cell in workflow_cells)
