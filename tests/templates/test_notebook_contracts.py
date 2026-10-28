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
    } <= names
    assert "99_explore.ipynb" not in names
    assert "02A_data_contract_validation.ipynb" not in names
    assert {"01_agreement.ipynb", "03_review.ipynb"}.isdisjoint(names)


def test_01_governance_supports_the_complete_governance_lifecycle():
    """Governance uses one unified Data Contract workspace without a separate Catalogue picker."""
    source = _notebook_source("01_governance.ipynb")
    required_functions = {
        "widget_render_data_steward",
        "widget_render_data_agreement",
        "widget_data_contract",
        "widget_activate_pipeline",
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
    assert source.count("widget_data_contract()") == 1
    assert source.count("widget_activate_pipeline()") == 1
    assert "Data Steward" in source
    assert "Data Agreement" in source
    assert "**Table**, **Columns**, and **Review**" in source
    assert "Freezing creates an immutable candidate for Engineering validation" in source
    assert "Governance authoring and Engineering validation intentionally loop" in source
    assert "Activation records exact validation, Contract and Agreement references" in source
    assert "METADATA_PIPELINE_REGISTRY" in source
    assert "Observe locally → Govern globally → Preview locally → Activate locally" in source
    assert "complete validation evidence in each target workspace before local activation" in source
    assert "METADATA_ACTIVATION_STATE" not in source
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
    assert "setup_pipeline" not in authoring_cell
    assert "widget_data_contract(" in authoring_cell
    assert "setup_pipeline" not in activation_cell
    assert "widget_activate_pipeline(" in activation_cell
    assert "setup_pipeline" not in source
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

    assert "# step 4. preview and enforce frozen data contracts" in normalized["step_4"]
    assert "dry run" in normalized["step_4"]
    assert "does not register a new pipeline" in normalized["step_4"]
    assert "finalize_pipeline(pipeline)" in normalized["step_4"]
    assert "refuses to write any table that is already governed" in normalized["step_4"]
    assert "incomplete" in normalized["step_4"]

    assert "# step 5. activate data contracts and deploy" in normalized["step_5"]
    assert "exact effective data agreement" in normalized["step_5"]
    assert "review the affected release" in normalized["step_5"]
    assert "fabric or ci tooling" in normalized["step_5"]
    assert "deploy the reviewed notebook" in normalized["step_5"]

    assert "# step 6. run the pipeline in production" in normalized["step_6"]
    assert "same pipeline workflow in the production workspace" in normalized["step_6"]
    assert "activated workspace authority" in normalized["step_6"]
    assert "do not pass an execution-plan argument" in normalized["step_6"]
    assert "read → transform → write" in normalized["step_6"]

    lifecycle_steps = (
        "author and freeze the data contract",
        "preview and enforce the frozen data contract",
        "activate data contracts and deploy",
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
    """The living template keeps one clear Workspace -> Contract -> Read -> Transform -> Write path."""
    source = _notebook_source("02_pipeline.ipynb")
    headings = (
        "# 0. Workspace",
        "# 1. Setup Pipeline",
        "# 2. Read",
        "# 3. Transform",
        "# 4. Write",
    )
    assert [source.index(heading) for heading in headings] == sorted(source.index(heading) for heading in headings)
    code_source = "\n".join(source for _, source in _code_cells(NOTEBOOK_DIR / "02_pipeline.ipynb"))
    assert code_source.count("setup_pipeline(") == 1
    assert code_source.count("orchestrate_read(") == 1
    assert code_source.count("orchestrate_write(") == 1
    assert all(name not in source for name in ("orders", "products", "order_history", "customer_summary"))


def test_02_pipeline_preserves_migration_surfaces_and_lineage_handoff():
    """The standard template keeps stable cells and passes the Read result into the Write."""
    notebook = _load_notebook(NOTEBOOK_DIR / "02_pipeline.ipynb")
    cell_ids = [cell.get("id") for cell in notebook.cells]
    required_order = [
        "contracts",
        "read-setup",
        "read-1",
        "transform",
        "write-setup",
        "write-1",
    ]
    positions = [cell_ids.index(cell_id) for cell_id in required_order]
    assert positions == sorted(positions)

    read = _cell_by_id("02_pipeline.ipynb", "read-1").source
    transform = _cell_by_id("02_pipeline.ipynb", "transform").source
    write = _cell_by_id("02_pipeline.ipynb", "write-1").source
    assert 'sources["source"] = source' in read
    assert 'sources["source"]["dataframe"]' in transform
    assert 'sources=' not in write
    assert "orchestrate_read(" not in transform
    assert "orchestrate_write(" not in transform
    assert "READ_STORE =" not in read
    assert "WRITE_STORE =" not in write


def test_02_pipeline_optional_inspection_stays_outside_orchestration():
    """Bounded previews follow orchestration calls in the same cloneable cells."""
    read = _cell_by_id("02_pipeline.ipynb", "read-1").source
    write = _cell_by_id("02_pipeline.ipynb", "write-1").source
    assert read.index("orchestrate_read(") < read.index('display(sources["source"]["dataframe"].limit(10))')
    assert write.index("orchestrate_write(") < write.index('display(writes["target"]["dataframe"].limit(10))')
    assert '# display(writes["target"].get("dq_result"))' in write


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


def test_four_pipeline_notebooks_have_consistent_bounded_dataframe_inspection():
    """Each pipeline notebook defaults to bounded top-level Read and Write previews."""
    paths = [
        NOTEBOOK_DIR / "02_pipeline.ipynb",
        DEMO_NOTEBOOK_DIR / "02A_full_refresh_demo.ipynb",
        DEMO_NOTEBOOK_DIR / "02B_incremental_append_demo.ipynb",
        DEMO_NOTEBOOK_DIR / "02C_scd_demo.ipynb",
    ]
    for path in paths:
        notebook = _load_notebook(path)
        source = "\n".join(
            cell.source for cell in notebook.cells if cell.cell_type == "code"
        )
        assert "inspect_source" not in source and "inspect_write" not in source
        assert not {"inspect", "execution-plan"}.intersection(cell.id for cell in notebook.cells)
        for cell in notebook.cells:
            if cell.cell_type != "code":
                continue
            for orchestrator in ("orchestrate_read", "orchestrate_write"):
                if f"{orchestrator}(" not in cell.source:
                    continue
                tree = ast.parse(cell.source)
                displays = [node for node in ast.walk(tree) if isinstance(node, ast.Expr)
                            and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name)
                            and node.value.func.id == "display"]
                assert len(displays) == 1, (path.name, cell.id)
                preview = ast.unparse(displays[0])
                assert "['dataframe'].limit(10)" in preview
                assert cell.source.index(f"{orchestrator}(") < cell.source.index("display(")
                if orchestrator == "orchestrate_write":
                    assert all(key in cell.source for key in ("dq_result", "sensitive_result", "support_mapping"))
                    assert "# from fabricops_kit import read_" in cell.source
                    assert "pipeline_read" not in cell.source


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
    assert 'sources=' not in code_source
    assert "FROM demo.order_history" in source
    assert "customer_summary_df" in source
    assert code_source.count('display(write_result["dataframe"].limit(10))') == 2


def test_02b_has_ordered_repeat_safe_incremental_append_flow():
    """02B stages unique movements and always calls both orchestrators in notebook order."""
    notebook = _load_notebook(DEMO_NOTEBOOK_DIR / "02B_incremental_append_demo.ipynb")
    source = _demo_source("02B_incremental_append_demo.ipynb")
    ids = [cell.get("id") for cell in notebook.cells]
    ordered = [
        "imports",
        "demo-day",
        "read-csv",
        "contracts",
        "read-1",
        "transform",
        "write-1",
    ]
    assert [ids.index(cell_id) for cell_id in ordered] == sorted(ids.index(cell_id) for cell_id in ordered)
    assert "DEMO_DAY = 1" in _demo_cell("02B_incremental_append_demo.ipynb", "demo-day").source
    assert "inventory_day2.csv" in source and "inventory_day1.csv" not in source
    assert '.dropDuplicates(["movement_id"])' in source
    assert 'table_name="inventory_movements"' in source
    assert 'mode="overwrite"' in _demo_cell("02B_incremental_append_demo.ipynb", "read-csv").source
    assert 'read_mode="incremental"' in source
    assert 'read_parameters={"watermark_column": "modified_datetime"}' in source
    assert 'table_name="inventory_movements_incremental"' in source
    assert 'write_mode="append"' in source
    assert 'sources=' not in _demo_cell('02B_incremental_append_demo.ipynb', 'write-1').source
    assert "should_process" not in source
    write = _demo_cell("02B_incremental_append_demo.ipynb", "write-1").source
    assert 'display(writes["inventory_movements_incremental"]["dataframe"].limit(10))' in write


def test_02c_has_ordered_full_read_and_two_scd_writes():
    """02C overwrites one Bronze snapshot and sends one governed Read to SCD1 and SCD2."""
    notebook = _load_notebook(DEMO_NOTEBOOK_DIR / "02C_scd_demo.ipynb")
    source = _demo_source("02C_scd_demo.ipynb")
    ids = [cell.get("id") for cell in notebook.cells]
    ordered = [
        "imports",
        "demo-day",
        "read-csv",
        "contracts",
        "read-1",
        "transform",
        "write-1",
        "write-2",
    ]
    assert [ids.index(cell_id) for cell_id in ordered] == sorted(ids.index(cell_id) for cell_id in ordered)
    assert "DEMO_DAY = 1" in source
    assert "products_day{DEMO_DAY}.csv" in source
    assert 'table_name="product_master_updates"' in source
    assert 'mode="overwrite"' in _demo_cell("02C_scd_demo.ipynb", "read-csv").source
    assert source.count("orchestrate_read(") == 1
    assert 'read_mode="full"' in source
    assert 'write_mode="scd1"' in source
    assert 'write_mode="scd2"' in source
    assert 'sources=' not in _demo_cell('02C_scd_demo.ipynb', 'write-1').source
    assert '"key_columns": ["product_id"]' in source
    assert '"effective_column": "modified_datetime"' in source
    assert '"tracked_columns": ["product_category", "list_price"]' in source
    for cell_id, target in (("write-1", "product_master_scd1"), ("write-2", "product_master_scd2")):
        assert f'display(writes["{target}"]["dataframe"].limit(10))' in _demo_cell("02C_scd_demo.ipynb", cell_id).source
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
    assert "00C-prepare-demo-data-with-fabricops-io.md" in step_2b and "inventory_day2.csv" in step_2b
    assert "02C_scd_demo.ipynb" in step_2c
    assert all(f"products_day{day}.csv" in step_2c for day in (2, 3))
    assert "00C-prepare-demo-data-with-fabricops-io.md" in step_2c
    assert "02A-full-refresh-demo.md" in step_3


def test_guided_demo_explains_three_execution_modes():
    """The executable walkthrough defaults to Ungoverned and explains Dry Run governance."""
    step_2a = (ROOT / "docs/guided-demo/02A-full-refresh-demo.md").read_text(encoding="utf-8")
    step_4 = (ROOT / "docs/guided-demo/04-validate-frozen-data-contract.md").read_text(encoding="utf-8")

    assert 'PIPELINE_MODE = "Ungoverned"' in step_2a
    assert "PIPELINE_TESTING_WRITES" not in step_2a
    assert "finalize_pipeline(pipeline)" in step_2a
    assert "Dry Run" in step_4 and "does not register a new pipeline" in step_4
    assert "refuses to write any table that is already governed" in step_4



@pytest.mark.parametrize("notebook_name", [
    "02A_full_refresh_demo.ipynb",
    "02B_incremental_append_demo.ipynb",
    "02C_scd_demo.ipynb",
])
def test_demo_notebooks_start_with_title_and_finalize_after_write(notebook_name: str) -> None:
    """Each independent demo opens with its own title and finalizes all Writes."""
    notebook = _load_notebook(DEMO_NOTEBOOK_DIR / notebook_name)
    ids = [cell.get("id") for cell in notebook.cells]
    assert ids[0] == "title"
    assert notebook.cells[0].cell_type == "markdown"
    assert ids.count("title") == 1
    assert ids[-1] == "finalize-run" and "inspect" not in ids
    last_write = max(
        index for index, cell_id in enumerate(ids)
        if cell_id.startswith("write-") and cell_id not in {"write-inspection", "write-dictionary-inspection-heading"}
    )
    assert ids.index("transform") < last_write


def test_living_templates_and_demos_use_setup_instead_of_run_magic():
    """JSON config notebooks must be loaded through setup, including demo callers."""
    paths = list(NOTEBOOK_DIR.glob('*.ipynb')) + list(Path('templates/DemoData').glob('*.ipynb'))
    for path in paths:
        source = path.read_text(encoding='utf-8')
        assert '%run 00_env_config' not in source, path.name



def test_current_notebook_examples_omit_explicit_spark_arguments():
    """Keep living templates and demo inspection cells on the automatic API."""
    import json
    import re
    from pathlib import Path
    paths = list(Path("templates/notebooks").glob("*.ipynb"))
    paths += list(Path("templates/DemoData").glob("02*.ipynb"))
    for path in paths:
        notebook = json.loads(path.read_text())
        for cell in notebook["cells"]:
            assert not re.search(r"\b(?:spark|spark_session)\s*=\s*spark\b", "".join(cell["source"])), path


@pytest.mark.parametrize("notebook_path", [NOTEBOOK_DIR / "02_pipeline.ipynb", *DEMO_NOTEBOOKS], ids=lambda path: path.name)
def test_finalization_is_one_call_without_manual_observation_profiling(notebook_path):
    """Every maintained 02 variant delegates observation publication to finalization."""
    notebook = _load_notebook(notebook_path)
    cell = next(cell for cell in notebook.cells if cell.get("id") == "finalize-run")
    pipeline, result = object(), {"status": "ungoverned_completed"}
    calls = []
    namespace = {"pipeline": pipeline, "finalize_pipeline": lambda value: calls.append(value) or result}
    exec(cell.source, namespace)
    assert calls == [pipeline] and namespace["pipeline_result"] is result
    tree = ast.parse(cell.source)
    assert [node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call)] == ["finalize_pipeline"]
    source = "\n".join("".join(cell.source) for cell in notebook.cells)
    assert "observation_profiles" not in source and "profile_table(" not in source
