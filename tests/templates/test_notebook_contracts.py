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
    portable_lines = [line for line in lines if not line.lstrip().startswith(("%", "!"))]
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
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id in aliases:
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
            f"cell {cell_index}: {name}" for name in sorted(referenced_names) if not hasattr(fabricops_kit, name)
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

    assert required_functions <= {
        node.id
        for tree in (
            _parse_code_cell(NOTEBOOK_DIR / "01_governance.ipynb", index, source)
            for index, source in _code_cells(NOTEBOOK_DIR / "01_governance.ipynb")
        )
        if tree is not None
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
    }
    assert 'store="metadata"' in source
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


def test_02_pipeline_is_a_sequential_engineering_notebook():
    """The visible workflow follows the authoritative full-read engineering sequence."""
    source = _notebook_source("02_pipeline.ipynb")
    headings = (
        "# 0. Environment",
        "# 1. Data Contract",
        "# 2. Full Read",
        "# 3. Transform",
        "# 4. Target",
        "# 5. Write Preparation / Guardrails",
        "# 6. Write",
        "# 7. Persisted Target Profile",
    )
    assert [source.index(heading) for heading in headings] == sorted(source.index(heading) for heading in headings)


def test_02_pipeline_initializes_data_contracts_once_in_plain_language():
    """The contract selector runs once and explains environment behavior."""
    source = _notebook_source("02_pipeline.ipynb")
    contracts = _cell_by_id("02_pipeline.ipynb", "contracts-heading").source
    assert "Select the Data Contracts to test with this pipeline." in contracts
    assert "Production automatically uses activated Data Contracts." in contracts
    assert source.count("widget_select_data_contract()") == 1


def test_02_pipeline_is_full_read_and_full_profile_by_design():
    """The default pipeline reads and profiles complete governed sources."""
    source = _notebook_source("02_pipeline.ipynb")
    assert "full-read pipeline template" in source
    assert "source-side incremental reads" in source
    assert "PROFILE_SCOPE" not in source
    assert "PROCESSING_SCOPE" not in source
    assert source.count("profile_table(table_id=table_id)") == 3
    assert "profile_table(dataframe=df, table_id=table_id)" not in source


def test_02_pipeline_read_blocks_are_cloneable_and_explicit():
    """Every source block repeats the explicit governed full-read workflow."""
    for index, read_name in ((1, "orders"), (2, "products"), (3, "history")):
        block = _cell_by_id("02_pipeline.ipynb", f"read-{index}").source
        for fragment in (
            f'READ_NAME = "{read_name}"',
            "READ_STORE =",
            "READ_SCHEMA =",
            "READ_TABLE =",
            "READ_QUERY =",
            "source = pipeline_read(",
            'df = source["dataframe"]',
            'table_id = source["table_id"]',
            "check_freshness(",
            "check_schema(df,",
            "check_dq(df,",
            "profile_table(table_id=table_id)",
            "sources[READ_NAME] = source",
        ):
            assert fragment in block
        assert "report_check" not in block
        assert "Rule source:" not in block
        assert "METADATA_GUARDRAIL_RESULTS" not in block


def test_02_pipeline_transform_is_plain_pyspark():
    """Project transformation remains ordinary readable PySpark."""
    transform = _cell_by_id("02_pipeline.ipynb", "transform").source
    assert transform.count(".join(") == 2
    assert ".withColumn(" in transform
    assert "pipeline_transform" not in transform


def test_02_pipeline_target_and_write_guardrails_are_explicit():
    """Target checks precede publication and use only its declared source subset."""
    target = _cell_by_id("02_pipeline.ipynb", "pipeline-target").source
    checks = _cell_by_id("02_pipeline.ipynb", "write-preparation").source
    write = _cell_by_id("02_pipeline.ipynb", "write-1").source
    profile = _cell_by_id("02_pipeline.ipynb", "write-profile").source
    assert "WRITE_DATAFRAME = transformed_df" in target
    assert 'WRITE_SOURCE_NAMES = ("orders", "products", "history")' in target
    assert "write_sources = [sources[name] for name in WRITE_SOURCE_NAMES]" in target
    assert "target_table_id = resolve_table_id(" in target
    stages = ("check_schema(", "check_sensitive_data(", "check_source_drift(", "check_dq(")
    assert [checks.index(stage) for stage in stages] == sorted(checks.index(stage) for stage in stages)
    assert 'prepared_df = sensitive_result["dataframe"]' in checks
    assert "for source in write_sources:" in checks
    assert "check_dq(\n    prepared_df," in checks
    assert "pipeline_write(\n    prepared_df," in write
    assert 'source_table_ids=[source["table_id"] for source in write_sources]' in write
    assert 'profile_table(table_id=write_result["table_id"])' in profile
    assert checks.count("check_source_drift(") == 1
    for index in (1, 2, 3):
        assert "check_source_drift(" not in _cell_by_id(
            "02_pipeline.ipynb", f"read-{index}"
        ).source


def test_02_pipeline_keeps_orchestration_out_of_public_boundaries():
    """Read, checks, profiling, and write remain separate notebook calls."""
    source = _notebook_source("02_pipeline.ipynb")
    assert source.count("source = pipeline_read(") == 3
    assert source.count("write_result = pipeline_write(") == 1
    assert "report_check" not in source
    assert "run_all_checks" not in source
    for hidden in ("read_lakehouse_table", "read_warehouse_table", "write_lakehouse_table", "write_warehouse_table"):
        assert hidden not in source


def test_02_pipeline_main_path_is_runnable_not_disabled_preview():
    """Every required workflow cell contains active parseable code."""
    notebook = _load_notebook(NOTEBOOK_DIR / "02_pipeline.ipynb")
    required = {
        "contracts",
        "pipeline-target",
        "read-setup",
        "read-1",
        "read-2",
        "read-3",
        "transform",
        "write-preparation",
        "write-1",
        "write-profile",
    }
    by_id = {cell.get("id"): cell for cell in notebook.cells}
    for cell_id in required:
        cell = by_id[cell_id]
        assert cell.cell_type == "code"
        assert cell.execution_count is None
        assert not cell.outputs
        ast.parse(cell.source)
