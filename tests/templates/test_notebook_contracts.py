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
DEMO_NOTEBOOK_DIR = ROOT / "templates" / "DemoData"
NOTEBOOKS = tuple(sorted(NOTEBOOK_DIR.glob("*.ipynb")))
DEMO_NOTEBOOKS = tuple(sorted(DEMO_NOTEBOOK_DIR.glob("02*.ipynb")))


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
    except SyntaxError as exc:  # pragma: no cover
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
    assert {
        "00_env_config.ipynb",
        "01_governance.ipynb",
        "02_pipeline.ipynb",
        "99_explore.ipynb",
    } <= names
    assert "02A_data_contract_validation.ipynb" not in names
    assert {"01_agreement.ipynb", "03_review.ipynb"}.isdisjoint(names)


def test_01_governance_supports_the_complete_governance_lifecycle():
    """Governance uses one unified Data Contract workspace without a separate Catalogue picker."""
    source = _notebook_source("01_governance.ipynb")
    required_functions = {
        "widget_render_data_steward",
        "widget_render_data_agreement",
        "widget_data_contract",
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
    assert "widget_view_catalogue" not in source
    assert 'mode="explore"' not in source
    assert 'store="Metadata"' not in source
    assert 'TABLE_ID = table_selection["table_id"]' not in source
    assert source.count("widget_data_contract(spark_session=spark)") == 1
    assert source.count("widget_activate_data_contract(spark_session=spark)") == 1
    assert "Data Steward" in source
    assert "Data Agreement" in source
    assert "**Table**, **Columns**, and **Review**" in source
    assert "Freezing creates an immutable candidate for Engineering validation" in source
    assert "Governance authoring and Engineering validation intentionally loop" in source
    assert "Activation makes that contract the governed Production definition" in source
    assert "does **not** promote or deploy `02_pipeline`" in source
    for demoted_widget in (
        "widget_enrich_table_metadata",
        "widget_author_guardrails",
        "widget_author_dq_rules",
        "widget_register_data_contract",
    ):
        assert demoted_widget not in source
        assert f"fabricops_kit.widgets.{demoted_widget}" not in source
    authoring_cell = _cell_by_id("01_governance.ipynb", "contract-author").source
    activation_cell = _cell_by_id("01_governance.ipynb", "activation-widget").source
    assert "widget_select_data_contract" not in authoring_cell
    assert "widget_data_contract(" in authoring_cell
    assert "widget_select_data_contract" not in activation_cell
    assert "widget_activate_data_contract(" in activation_cell
    assert "widget_select_data_contract" not in source
    assert "METADATA_SCHEMA" not in source

def test_guided_demo_uses_the_frozen_contract_first_lifecycle():
    """Guided Demo Steps 3–6 preserve lifecycle order and responsibility boundaries."""
    step_3 = (ROOT / "docs/guided-demo/03-author-and-freeze-data-contract.md").read_text(encoding="utf-8")
    step_4 = (ROOT / "docs/guided-demo/04-validate-frozen-data-contract.md").read_text(encoding="utf-8")
    step_5 = (ROOT / "docs/guided-demo/05-activate-data-contract-and-promote.md").read_text(encoding="utf-8")
    step_6 = (ROOT / "docs/guided-demo/06-run-production.md").read_text(encoding="utf-8")
    overview = (ROOT / "docs/guided-demo.md").read_text(encoding="utf-8")

    normalized = {
        "step_3": step_3.casefold(),
        "step_4": step_4.casefold(),
        "step_5": step_5.casefold(),
        "step_6": step_6.casefold(),
        "overview": overview.casefold(),
    }

    assert "# step 3. author and freeze the data contract" in normalized["step_3"]
    assert "widget_data_contract" in step_3
    assert "freezing does not activate" in normalized["step_3"]
    assert "immutable data contract" in normalized["step_3"]

    assert "# step 4. validate the frozen data contract" in normalized["step_4"]
    assert "select the exact frozen candidate version" in normalized["step_4"]
    assert "same `02A_full_refresh_demo` notebook" in step_4
    assert "do not edit a frozen version in place" in normalized["step_4"]
    assert "defaults every table to **enforce**" in normalized["step_4"]
    assert "pipeline_write()" in normalized["step_4"]
    assert "is never reached" in normalized["step_4"]

    assert "# step 5. activate the data contract and promote to production" in normalized["step_5"]
    assert "link the data agreement" in normalized["step_5"]
    assert "activate the data contract" in normalized["step_5"]
    assert "fabric deployment pipeline" in normalized["step_5"]
    assert "deploy it to the production stage" in normalized["step_5"]

    assert "# step 6. run the pipeline in production" in normalized["step_6"]
    assert "same tested workflow in the production environment" in normalized["step_6"]
    assert "production automatically resolves the single active data contract" in normalized["step_6"]
    assert "read → transform → write" in normalized["step_6"]

    lifecycle_steps = (
        "author and freeze the data contract",
        "validate the frozen data contract",
        "activate the data contract and promote",
        "run the pipeline in production",
    )
    lifecycle_positions = [normalized["overview"].index(step) for step in lifecycle_steps]
    assert lifecycle_positions == sorted(lifecycle_positions)


def _demo_source(notebook_name: str) -> str:
    notebook = _load_notebook(DEMO_NOTEBOOK_DIR / notebook_name)
    return "\n".join(cell.source for cell in notebook.cells)


def _demo_cell(notebook_name: str, cell_id: str) -> nbformat.NotebookNode:
    notebook = _load_notebook(DEMO_NOTEBOOK_DIR / notebook_name)
    return next(cell for cell in notebook.cells if cell.get("id") == cell_id)


@pytest.mark.parametrize("notebook_path", DEMO_NOTEBOOKS, ids=lambda path: path.name)
def test_demo_notebooks_are_valid_and_use_public_fabricops_apis(notebook_path: Path):
    """Demo notebooks are valid JSON, compile locally, and import supported public names."""
    import fabricops_kit

    notebook = _load_notebook(notebook_path)
    nbformat.validate(notebook)
    missing: list[str] = []
    for cell_index, source in _code_cells(notebook_path):
        tree = _parse_code_cell(notebook_path, cell_index, source)
        if tree is None:
            continue
        compile(tree, filename=f"{notebook_path}:{cell_index}", mode="exec")
        references = _fabricops_imported_names(tree) | _fabricops_attribute_references(tree)
        missing.extend(
            f"cell {cell_index}: {name}"
            for name in sorted(references)
            if not hasattr(fabricops_kit, name)
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith("fabricops_kit."), (
                    f"{notebook_path.name} cell {cell_index} imports FabricOps internals: {node.module}"
                )
    assert not missing, f"Missing public references in {notebook_path.name}: {missing}"


def test_02_pipeline_is_a_small_reusable_scaffold():
    """The living template keeps one clear Environment -> Contract -> Read -> Transform -> Write path."""
    source = _notebook_source("02_pipeline.ipynb")
    headings = (
        "# 0. Environment",
        "# 1. Data Contract",
        "# 2. Governed Read",
        "# 3. PySpark Transform",
        "# 4. Governed Write",
    )
    assert [source.index(heading) for heading in headings] == sorted(source.index(heading) for heading in headings)
    assert source.count("widget_select_data_contract(spark_session=spark)") == 1
    code_source = "\n".join(source for _, source in _code_cells(NOTEBOOK_DIR / "02_pipeline.ipynb"))
    assert code_source.count("orchestrate_read(") == 1
    assert code_source.count("orchestrate_write(") == 1
    assert all(name not in source for name in ("orders", "products", "order_history", "customer_summary"))


def test_02_pipeline_preserves_migration_surfaces_and_lineage_handoff():
    """The standard template keeps stable cells and passes the Read result into the Write."""
    notebook = _load_notebook(NOTEBOOK_DIR / "02_pipeline.ipynb")
    cell_ids = [cell.get("id") for cell in notebook.cells]
    required_order = [
        "environment",
        "contracts",
        "read-setup",
        "read-1",
        "read-inspection",
        "transform",
        "write-setup",
        "write-1",
        "write-inspection",
    ]
    positions = [cell_ids.index(cell_id) for cell_id in required_order]
    assert positions == sorted(positions)

    read = _cell_by_id("02_pipeline.ipynb", "read-1").source
    transform = _cell_by_id("02_pipeline.ipynb", "transform").source
    write = _cell_by_id("02_pipeline.ipynb", "write-1").source
    assert 'sources["source"] = source' in read
    assert 'sources["source"]["dataframe"]' in transform
    assert 'sources=[sources["source"]]' in write
    assert "orchestrate_read(" not in transform
    assert "orchestrate_write(" not in transform
    assert "READ_STORE =" not in read
    assert "WRITE_STORE =" not in write


def test_02_pipeline_optional_inspection_stays_outside_orchestration():
    """Optional displays remain commented and separate from Read and Write calls."""
    read_inspection = _cell_by_id("02_pipeline.ipynb", "read-inspection").source
    write_inspection = _cell_by_id("02_pipeline.ipynb", "write-inspection").source
    assert '# display(sources["source"]["dataframe"])' in read_inspection
    assert '# display(writes["target"]["schema_result"])' in write_inspection
    assert "display(" not in _cell_by_id("02_pipeline.ipynb", "read-1").source
    assert "display(" not in _cell_by_id("02_pipeline.ipynb", "write-1").source


def test_02_pipeline_scaffold_uses_public_fabricops_boundary():
    """The standard scaffold does not depend on private FabricOps modules."""
    for cell_index, source in _code_cells(NOTEBOOK_DIR / "02_pipeline.ipynb"):
        tree = _parse_code_cell(NOTEBOOK_DIR / "02_pipeline.ipynb", cell_index, source)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith("fabricops_kit."), (
                    f"02_pipeline.ipynb cell {cell_index} imports FabricOps internals: {node.module}"
                )


def test_02a_preserves_the_full_refresh_pipeline():
    """02A retains the former retail reads, transformation, writes, and inspections."""
    source = _demo_source("02A_full_refresh_demo.ipynb")
    assert "# 02A Full Refresh Demo" in source
    code_source = "\n".join(
        source for _, source in _code_cells(DEMO_NOTEBOOK_DIR / "02A_full_refresh_demo.ipynb")
    )
    assert code_source.count("orchestrate_read(") == 3
    assert code_source.count('read_mode="full"') == 3
    assert code_source.count("write_result = orchestrate_write(") == 2
    assert code_source.count('write_mode="overwrite"') == 2
    assert 'sources=[sources["orders"], sources["products"], sources["history"]]' in source
    assert "FROM demo.order_history" in source
    assert "customer_summary_df" in source
    assert 'display(writes[inspect_write]["schema_result"])' in source


def test_02b_has_ordered_repeat_safe_incremental_append_flow():
    """02B stages unique movements and always calls both orchestrators in notebook order."""
    notebook = _load_notebook(DEMO_NOTEBOOK_DIR / "02B_incremental_append_demo.ipynb")
    source = _demo_source("02B_incremental_append_demo.ipynb")
    ids = [cell.get("id") for cell in notebook.cells]
    ordered = [
        "environment",
        "imports",
        "demo-day",
        "read-csv",
        "write-bronze",
        "contracts",
        "read-1",
        "transform",
        "write-1",
        "inspect",
    ]
    assert [ids.index(cell_id) for cell_id in ordered] == sorted(ids.index(cell_id) for cell_id in ordered)
    assert "DEMO_DAY = 1" in _demo_cell("02B_incremental_append_demo.ipynb", "demo-day").source
    assert "inventory_day1.csv" in source and "inventory_day2.csv" in source
    assert '.dropDuplicates(["movement_id"])' in source
    assert 'table_name="inventory_movements"' in source
    assert 'mode="overwrite"' in _demo_cell("02B_incremental_append_demo.ipynb", "write-bronze").source
    assert 'read_mode="incremental"' in source
    assert 'read_parameters={"watermark_column": "modified_datetime"}' in source
    assert 'table_name="inventory_movements_incremental"' in source
    assert 'write_mode="append"' in source
    assert 'sources=[sources["inventory_movements"]]' in source
    assert "should_process" not in source


def test_02c_has_ordered_full_read_and_two_scd_writes():
    """02C overwrites one Bronze snapshot and sends one governed Read to SCD1 and SCD2."""
    notebook = _load_notebook(DEMO_NOTEBOOK_DIR / "02C_scd_demo.ipynb")
    source = _demo_source("02C_scd_demo.ipynb")
    ids = [cell.get("id") for cell in notebook.cells]
    ordered = [
        "environment",
        "imports",
        "demo-day",
        "read-csv",
        "write-bronze",
        "contracts",
        "read-1",
        "transform",
        "sequence-check",
        "write-1",
        "write-2",
        "inspect",
    ]
    assert [ids.index(cell_id) for cell_id in ordered] == sorted(ids.index(cell_id) for cell_id in ordered)
    assert "DEMO_DAY = 1" in source
    assert "products_day{DEMO_DAY}.csv" in source
    assert 'table_name="product_master_updates"' in source
    assert 'mode="overwrite"' in _demo_cell("02C_scd_demo.ipynb", "write-bronze").source
    assert source.count("orchestrate_read(") == 1
    assert 'read_mode="full"' in source
    assert 'write_mode="scd1"' in source
    assert 'write_mode="scd2"' in source
    assert source.count('sources=[sources["product_master"]]') == 2
    assert '"key_columns": ["product_id"]' in source
    assert '"effective_column": "modified_datetime"' in source
    assert '"tracked_columns": ["product_category", "list_price"]' in source
    assert "allowed_existing_versions = {2: {8, 9}, 3: {9, 10}}[DEMO_DAY]" in source
    assert "| 1 | 8 | 8 |" in source
    assert "| 2 | 8 | 9 |" in source
    assert "| 3 | 8 | 10 |" in source


def test_guided_demo_pages_match_the_notebook_split():
    """Step 2 is reusable guidance and Steps 2A-2C point to ready-to-run assets."""
    step_2 = (ROOT / "docs/guided-demo/02-build-and-run-etl.md").read_text(encoding="utf-8")
    step_2a = (ROOT / "docs/guided-demo/02A-full-refresh-demo.md").read_text(encoding="utf-8")
    step_2b = (ROOT / "docs/guided-demo/02B-build-and-run-incremental-append-etl.md").read_text(encoding="utf-8")
    step_2c = (ROOT / "docs/guided-demo/02C-build-and-run-scd-etl.md").read_text(encoding="utf-8")
    step_3 = (ROOT / "docs/guided-demo/03-author-and-freeze-data-contract.md").read_text(encoding="utf-8")

    assert "# Step 2. Build a Pipeline" in step_2
    assert "02_pipeline.ipynb" in step_2
    assert "orders" not in step_2.casefold()
    assert "# Step 2A. Run the Full Refresh Demo" in step_2a
    assert "02A_full_refresh_demo.ipynb" in step_2a
    assert "02B_incremental_append_demo.ipynb" in step_2b
    assert "inventory_day1.csv" in step_2b and "inventory_day2.csv" in step_2b
    assert "02C_scd_demo.ipynb" in step_2c
    assert all(f"products_day{day}.csv" in step_2c for day in (1, 2, 3))
    assert "02A-full-refresh-demo.md" in step_3


def test_guided_demo_preserves_initial_unselected_flow_and_optional_target_validation():
    """The executable 02A walkthrough keeps the initial unselected run and later target validation."""
    step_2a = (ROOT / "docs/guided-demo/02A-full-refresh-demo.md").read_text(encoding="utf-8")
    step_4 = (ROOT / "docs/guided-demo/04-validate-frozen-data-contract.md").read_text(encoding="utf-8")

    assert "there is no Data Contract yet" in step_2a
    assert "leave the selection unchanged" in step_2a
    assert "Contract-backed checks will return as skipped" in step_2a
    assert "leave every source table in **Enforce** mode" in step_4
    assert "choose **Validate** only for the target" in step_4
    assert "Validate returns `published=False` and `validation_passed=True`" in step_4
