"""Portable contract tests for FabricOps notebook templates.

CI validates notebook file integrity, Python syntax, and public import
compatibility. Full execution against lakehouses, warehouses, Spark, Fabric
widgets, notebook utilities, and workspace context is not reproducible in GitHub
Actions. Successful manual execution by the maintainer in Microsoft Fabric is
the authoritative integration test for runtime behaviour.
"""

from __future__ import annotations

import ast
import re
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
    """Governance uses the unified, table-scoped Data Contract authoring path."""
    source = _notebook_source("01_governance.ipynb")
    required_functions = {
        "widget_render_data_steward",
        "widget_render_data_agreement",
        "widget_view_catalogue",
        "widget_author_data_contract",
        "widget_activate_data_contract",
    }

    assert required_functions <= {node.id for tree in (
        _parse_code_cell(NOTEBOOK_DIR / "01_governance.ipynb", index, source)
        for index, source in _code_cells(NOTEBOOK_DIR / "01_governance.ipynb")
    ) if tree is not None for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert 'target="metadata"' in source
    assert 'mode="explore"' in source
    assert 'TABLE_ID = table_selection["table_id"]' in source
    assert 'contract_authoring["table_id"] == TABLE_ID' in source
    assert "Data Steward" in source
    assert "Data Agreement" in source
    for demoted_widget in (
        "widget_enrich_table_metadata",
        "widget_author_guardrails",
        "widget_author_dq_rules",
        "widget_register_data_contract",
    ):
        assert demoted_widget not in source
        assert f"fabricops_kit.widgets.{demoted_widget}" not in source
    authoring_cell = _cell_by_id("01_governance.ipynb", "contract-author").source
    assert "widget_select_data_contract" not in authoring_cell
    assert "widget_activate_data_contract" not in authoring_cell
    assert "widget_activate_data_contract(" in _cell_by_id("01_governance.ipynb", "activation-widget").source
    assert "METADATA_SCHEMA" not in source


def test_guided_demo_uses_the_frozen_contract_first_lifecycle():
    """Guided Demo Steps 3–6 preserve lifecycle order and responsibility boundaries."""
    step_3 = (ROOT / "docs/guided-demo/03-enrich-guardrails.md").read_text(encoding="utf-8")
    step_4 = (ROOT / "docs/guided-demo/04-run-pipeline-with-guardrails.md").read_text(encoding="utf-8")
    step_5 = (ROOT / "docs/guided-demo/05-create-data-contract.md").read_text(encoding="utf-8")
    step_6 = (ROOT / "docs/guided-demo/06-promote-to-production.md").read_text(encoding="utf-8")
    overview = (ROOT / "docs/guided-demo.md").read_text(encoding="utf-8")

    assert "Author and Freeze the Data Contract" in step_3
    assert "widget_author_data_contract" in step_3
    assert "Data Agreement is not linked in this step" in step_3
    assert "Select and Validate the Data Contract" in step_4
    assert "widget_select_data_contract" in step_4
    assert "Selection is not activation" in step_4
    assert "Link the Data Agreement and Activate" in step_5
    assert "widget_activate_data_contract" in step_5
    assert "not a technical activation gate" in step_5
    assert "Promote and Run Production" in step_6
    assert "Production never falls back to mutable authoring metadata" in step_6
    assert "Author → Freeze → Select → Validate → Link Data Agreement → Activate → Promote → Run Production" in overview


def test_02_pipeline_is_a_minimal_read_transform_write_template():
    """The visible workflow uses engineering vocabulary and only necessary shared state."""
    source = _notebook_source("02_pipeline.ipynb")
    for heading in ("# 0. Environment", "# 1. Data Contracts", "# 2. Read", "# 3. Transform", "# 4. Write"):
        assert heading in source
    for legacy in ("Extract", "EXTRACT_", "Load", "LOAD_NAME", "LOAD_TABLE_ID", "READ_NAME", "WRITE_NAME"):
        assert legacy not in source
    assert "READ_PREPS = {}" in source
    assert "READ_DFS = {}" in source
    assert "WRITE_PREPS" not in source and "WRITE_DFS" not in source
    assert "How to read the blocks" not in source


def test_02_pipeline_initializes_data_contracts_once_in_plain_language():
    """Development selects contracts once while Production behavior is stated plainly."""
    source = _notebook_source("02_pipeline.ipynb")
    contracts = _cell_by_id("02_pipeline.ipynb", "contracts-heading").source
    assert "Select the Data Contracts to test with this pipeline." in contracts
    assert "Production automatically uses activated Data Contracts." in contracts
    assert source.count("widget_select_data_contract()") == 1
    assert "CONTRACTS = widget_select_data_contract()" in source
    assert "VALIDATE_DATA_CONTRACTS" not in source


def test_02_pipeline_lakehouse_read_blocks_are_cloneable():
    """Lakehouse Reads are complete, structurally identical copy/paste units."""
    reads = [_cell_by_id("02_pipeline.ipynb", f"read-{index}").source for index in (1, 2)]
    normalized = []
    for index, block in enumerate(reads, start=1):
        for setting in ("READ", "READ_TARGET", "READ_SCHEMA", "READ_TABLE"):
            assert f"{setting} =" in block
        for stage in (
            "read_pipeline_prep(", "read_lakehouse_table(", "check_schema(", "check_dq(",
            "observe_table(", "check_freshness(", "check_source_stability(",
            "profile_and_register_table(read_df)", "READ_PREPS[READ]", "READ_DFS[READ]",
            'catalogue_widget["show"](table_id=READ_TABLE_ID)',
        ):
            assert stage in block
        normalized.append(re.sub(r'READ = [12]|READ_TABLE = "(?:orders|products)"', "CONFIG", block))
    assert normalized[0] == normalized[1]


def test_02_pipeline_custom_query_uses_diagnostic_profile():
    """An aggregate query cannot overwrite canonical full-table profile metadata."""
    history = _cell_by_id("02_pipeline.ipynb", "read-3").source
    assert "read_warehouse_query(" in history
    assert "profile_dataframe(read_df)" in history
    assert "profile_and_register_table(" not in history
    assert "complete_table=False" not in history


def test_02_pipeline_omits_obsolete_and_safe_default_plumbing():
    """The template omits incremental Read state and defaults resolved by FabricOps."""
    source = _notebook_source("02_pipeline.ipynb")
    for removed in (
        "PIPELINE_SHOULD_RUN", "source_read_strategy=", "source_watermark_column=",
        "progress_target", "processing_scope=read_prep", "enabled=", "spark_session=",
        "profile_role=", "table=read_prep",
    ):
        assert removed not in source
    assert source.count("read_lakehouse_table(table_id=READ_TABLE_ID)") == 2


def test_02_pipeline_transform_is_explicit_project_pyspark():
    """Visible project-owned PySpark consumes all three source outputs."""
    transform = _cell_by_id("02_pipeline.ipynb", "transform").source
    for index in (1, 2, 3):
        assert f"READ_DFS[{index}]" in transform
    assert transform.count(".join(") == 2
    assert ".withColumn(" in transform


def test_02_pipeline_write_is_one_complete_copyable_block():
    """Write identity, preparation, checks, publication, and registration stay together."""
    config = _cell_by_id("02_pipeline.ipynb", "pipeline-target").source
    block = _cell_by_id("02_pipeline.ipynb", "write-1").source
    for setting in (
        "WRITE_TARGET", "WRITE_SCHEMA", "WRITE_TABLE", "WRITE_LOAD_STRATEGY",
        "WRITE_LOAD_STRATEGY_PARAMETERS",
    ):
        assert f"{setting} =" in config
    assert "resolve_table_id(" in config
    assert "load_strategy=WRITE_LOAD_STRATEGY" in block
    assert "load_strategy_parameters=WRITE_LOAD_STRATEGY_PARAMETERS" in block
    stages = [
        "write_pipeline_prep(", "check_schema(", "check_dq(", "check_sensitive_data(",
        'if not sensitive_result["can_continue"]', 'sensitive_result["dataframe"]', "write_lakehouse_table(",
        "published_df = read_lakehouse_table(", "profile_and_register_table(published_df)",
        'catalogue_widget["show"](table_id=WRITE_TABLE_ID)',
    ]
    assert all(stage in block for stage in stages)
    assert [block.index(stage) for stage in stages] == sorted(block.index(stage) for stage in stages)


def test_02_pipeline_main_path_is_runnable_not_disabled_preview():
    """Every canonical workflow cell remains active and output-free."""
    notebook = _load_notebook(NOTEBOOK_DIR / "02_pipeline.ipynb")
    required = {
        "contracts",
        "pipeline-target",
        "read-1",
        "read-2",
        "read-3",
        "transform",
        "write-1",
    }
    by_id = {cell.get("id"): cell for cell in notebook.cells}

    for cell_id in required:
        cell = by_id[cell_id]
        assert cell.cell_type == "code"
        assert cell.metadata.get("collapsed") is False
        assert cell.execution_count is None
        assert not cell.outputs
        tree = ast.parse(cell.source)
        assert not (
            len(tree.body) == 1
            and isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, ast.Constant)
            and isinstance(tree.body[0].value.value, str)
        )
    assert "Preview —" not in _notebook_source("02_pipeline.ipynb")


@pytest.mark.parametrize(
    ("notebook_name", "state_name"),
    [
        ("01_governance.ipynb", "catalogue_widget"),
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
