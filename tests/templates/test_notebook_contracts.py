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
from urllib.parse import unquote

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
    trees = tuple(
        tree
        for index, cell_source in _code_cells(NOTEBOOK_DIR / "01_governance.ipynb")
        if (tree := _parse_code_cell(NOTEBOOK_DIR / "01_governance.ipynb", index, cell_source)) is not None
    )
    required_functions = {
        "widget_data_steward",
        "widget_data_agreement",
        "widget_data_contract",
        "widget_activate_pipeline",
    }

    assert required_functions <= {
        node.id
        for tree in trees
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
    }
    direct_calls = [
        node.func.id
        for tree in trees
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    ]
    assert "widget_view_catalogue" not in source
    assert 'mode="explore"' not in source
    assert 'store="Metadata"' not in source
    assert 'TABLE_ID = table_selection["table_id"]' not in source
    assert direct_calls.count("widget_data_contract") == 1
    assert direct_calls.count("widget_activate_pipeline") == 1
    assert "Data Steward" in source
    assert "Data Agreement" in source
    assert "**Table**, **Columns**, and **Review**" in source
    assert "Freezing creates an immutable candidate for Engineering validation" in source
    assert "Governance authoring and Engineering validation intentionally loop" in source
    assert "Accepted packages and decisions persist in `METADATA_PIPELINE_ACTIVATION`" in source
    assert "METADATA_PIPELINE_REGISTRY" in source
    assert "no Engineering session or workspace access is required" in source
    assert "METADATA_PIPELINE_ACTIVATION" in source
    assert "contract_activation = widget_activate_data_contract()" in source
    assert "Each execution workspace has independent approval and deployment versions" in source
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
    step_5 = (ROOT / "docs/guided-demo/05-activate-contracts-and-deploy.md").read_text(encoding="utf-8")
    step_6 = (ROOT / "docs/guided-demo/06-run-governed-pipeline.md").read_text(encoding="utf-8")
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

    assert "# step 5. activate contracts and deploy the notebook" in normalized["step_5"]
    assert "exact effective agreement" in normalized["step_5"]
    assert "physical table workspace" in normalized["step_5"]
    assert "separate governed notebook" in normalized["step_5"]
    assert "never moves schedules" in normalized["step_5"]
    assert "toctou" in normalized["step_5"]
    assert "governed admission remains blocked" in normalized["step_5"]

    assert "# step 6. run the governed pipeline" in normalized["step_6"]
    assert "same pipeline workflow in its approved engineering workspace" in normalized["step_6"]
    assert "separate deployed governed notebook" in normalized["step_6"]
    assert "currently active notebook version" in normalized["step_6"]
    assert "read → transform → write" in normalized["step_6"]

    lifecycle_steps = (
        "author and freeze the data contract",
        "preview and enforce the frozen data contract",
        "activate data contracts and deploy",
        "run the governed pipeline and grant access",
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
    """The reusable template has one active setup, read, write and finalization."""
    notebook = _load_notebook(NOTEBOOK_DIR / "02_pipeline.ipynb")
    trees = [
        (cell, ast.parse(cell.source))
        for cell in notebook.cells
        if cell.cell_type == "code"
    ]

    def calls_for(name):
        return [
            (cell, node)
            for cell, tree in trees
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == name
        ]

    for name in ("setup_pipeline", "orchestrate_read", "orchestrate_write", "finalize_pipeline"):
        assert len(calls_for(name)) == 1, name

    # Initialization is independent of the example, so users may duplicate read/write cells.
    for variable, call in (("sources", "orchestrate_read"), ("writes", "orchestrate_write")):
        initializer = [
            index for index, (cell, tree) in enumerate(trees)
            if len(tree.body) == 1
            and isinstance(tree.body[0], ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == variable for target in tree.body[0].targets)
            and isinstance(tree.body[0].value, ast.Dict)
            and not tree.body[0].value.keys
        ]
        assert len(initializer) == 1, variable
        call_cell = calls_for(call)[0][0]
        call_index = next(index for index, (cell, _) in enumerate(trees) if cell is call_cell)
        assert initializer[0] < call_index

    # Read -> transformed DataFrame -> Write must remain intact without enforcing names.
    read_call = calls_for("orchestrate_read")[0][1]
    write_call = calls_for("orchestrate_write")[0][1]
    assert isinstance(write_call.args[0], ast.Name)
    transformed_name = write_call.args[0].id
    assignments = [
        (cell, node) for cell, tree in trees for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
    ]
    read_results = [
        node.targets[0] for _, node in assignments
        if isinstance(node.value, ast.Call) and node.value is read_call and len(node.targets) == 1
    ]
    assert len(read_results) == 1 and isinstance(read_results[0], ast.Subscript)
    read_key = ast.unparse(read_results[0])
    transforms = [
        node for _, node in assignments
        if any(isinstance(target, ast.Name) and target.id == transformed_name for target in node.targets)
    ]
    assert len(transforms) == 1
    assert read_key in ast.unparse(transforms[0].value)

    # The user-facing examples must stay bounded when previewing results.
    for call_name in ("orchestrate_read", "orchestrate_write"):
        cell = calls_for(call_name)[0][0]
        tree = ast.parse(cell.source)
        previews = [
            node for node in tree.body
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name) and node.value.func.id == "display"
        ]
        assert len(previews) == 1
        assert any(
            isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "limit" and len(node.args) == 1
            and isinstance(node.args[0], ast.Constant) and node.args[0].value == 10
            for node in ast.walk(previews[0])
        )

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
                if preview == "display(write_input.limit(10))":
                    assert path.name == "02B_incremental_append_demo.ipynb"
                    assert 'write_input = writes[' in cell.source
                    assert '["dataframe"]' in cell.source
                    assert "write_input.unpersist()" in cell.source
                else:
                    assert "['dataframe'].limit(10)" in preview
                calls = [node.func.id for node in ast.walk(tree)
                         if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)]
                assert "read_lakehouse_table" not in calls
                assert "read_warehouse_query" not in calls
                assert cell.source.index(f"{orchestrator}(") < cell.source.index("display(")
                if orchestrator == "orchestrate_write" and "relative_path=" not in cell.source:
                    assert all(key in cell.source for key in ("dq_result", "sensitive_result", "support_mapping"))
                    if path.name != "02C_scd_demo.ipynb":
                        assert "# from fabricops_kit import read_" in cell.source
                    assert "pipeline_read" not in cell.source


def test_four_pipeline_notebooks_follow_the_standard_02_layout_and_optional_inspection():
    """Demo variants retain the standard scaffold and its inspection choices."""
    paths = DEMO_NOTEBOOKS
    required_order = [
        "environment-heading",
        "imports",
        "setup-heading",
        "contracts",
        "read-heading",
        "read-setup",
        "read-1-heading",
        "transform-heading",
        "transform",
        "write-heading",
        "write-setup",
        "write-1-heading",
        "finalize-heading",
        "finalize-run",
    ]

    for path in paths:
        notebook = _load_notebook(path)
        cells = {cell.id: cell for cell in notebook.cells}
        positions = [next(i for i, cell in enumerate(notebook.cells) if cell.id == cell_id)
                     for cell_id in required_order]
        assert positions == sorted(positions), path.name
        assert cells["environment-heading"].source.startswith("# 0. Workspace — Setup Notebook")
        setup_cells = [cell for cell in notebook.cells
                       if cell.cell_type == "code" and "setup_pipeline(" in cell.source]
        for cell in setup_cells:
            assert "source_drift_enabled=False" in cell.source
            assert "source_drift_interval_days=1" in cell.source
            assert "source_drift_block=True" in cell.source

        transform_cells = [cell for cell in notebook.cells
                           if cell.cell_type == "code" and cell.id.startswith("transform")]
        for cell in transform_cells:
            transform_tree = ast.parse(cell.source)
            active_transform_displays = [
                node for node in ast.walk(transform_tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "display"
            ]
            assert not active_transform_displays, (path.name, cell.id)
            assert "# display(" in cell.source

        write_cells = [cell for cell in notebook.cells
                       if cell.cell_type == "code" and "orchestrate_write(" in cell.source]
        for cell in write_cells:
            assert cell.source.lstrip().startswith('writes["')
            if 'relative_path=' in cell.source:
                assert 'single_file=' not in cell.source
                assert 'file_format="csv"' in cell.source
                assert 'store="Silver"' in cell.source
                assert 'relative_path="demo/curated_orders.csv"' in cell.source
                assert '# from fabricops_kit import read_lakehouse_csv' in cell.source
                continue
            assert "# Optional: inspect Data Quality diagnostics and caller-managed token mapping." in cell.source
            assert '.get("dq_result")' in cell.source
            assert '.get("sensitive_result")' in cell.source
            assert '.get("support_mapping")' in cell.source
            assert "# Optional: read the final published target after a successful persistent execution." in cell.source
            assert "# from fabricops_kit import read_" in cell.source

        assert all(cell.id != "check-target-counts" for cell in notebook.cells)


def test_02a_preserves_the_full_refresh_pipeline():
    """02A retains the former retail reads, transformation, writes, and inspections."""
    source = _demo_source("02A_full_refresh_demo.ipynb")
    assert "# 02A Full Refresh Demo" in source
    code_source = "\n".join(
        source for _, source in _code_cells(DEMO_NOTEBOOK_DIR / "02A_full_refresh_demo.ipynb")
    )
    assert code_source.count("orchestrate_read(") == 3
    assert code_source.count('read_mode="full"') == 3
    assert code_source.count("= orchestrate_write(") == 3
    assert code_source.count('write_mode="overwrite"') == 3
    assert 'sources=' not in code_source
    assert "FROM demo.order_history" in source
    assert "customer_summary_df" in source
    assert 'display(writes["curated_orders_lakehouse"]["dataframe"].limit(10))' in code_source
    assert 'display(writes["customer_summary_warehouse"]["dataframe"].limit(10))' in code_source
    assert "write_result" not in code_source


def test_02b_has_ordered_independent_incremental_and_full_append_paths():
    """02B binds each independent Read to its intended transformation and target."""
    name = "02B_incremental_append_demo.ipynb"
    notebook = _load_notebook(DEMO_NOTEBOOK_DIR / name)
    source = _demo_source(name)
    ids = [cell.get("id") for cell in notebook.cells]
    ordered = [
        "imports", "demo-day", "read-csv", "contracts", "read-setup", "read-1",
        "transform", "write-1", "finalize-incremental", "setup-full", "read-2",
        "transform-full", "write-2", "finalize-full",
    ]
    assert [ids.index(cell_id) for cell_id in ordered] == sorted(ids.index(cell_id) for cell_id in ordered)
    assert "DEMO_DAY = 1" in _demo_cell(name, "demo-day").source
    assert "inventory_day2.csv" in source and "inventory_day1.csv" not in source
    assert '.dropDuplicates(["movement_id"])' in source
    assert 'mode="overwrite"' in _demo_cell(name, "read-csv").source
    assert source.count("orchestrate_read(") == 2
    assert source.count('read_mode="full"') == 1
    assert source.count('read_mode="incremental"') == 1

    incremental_tree = ast.parse(_demo_cell(name, "read-1").source)
    incremental_call = next(node for node in ast.walk(incremental_tree) if isinstance(node, ast.Call)
                            and isinstance(node.func, ast.Name) and node.func.id == "orchestrate_read")
    incremental_keywords = {keyword.arg: keyword.value for keyword in incremental_call.keywords}
    assert ast.literal_eval(incremental_keywords["read_mode"]) == "incremental"
    assert ast.literal_eval(incremental_keywords["read_parameters"]) == {"watermark_column": "modified_datetime"}
    assert ast.literal_eval(incremental_keywords["target_store"]) == "Silver"
    assert ast.literal_eval(incremental_keywords["target_schema"]) == "demo"
    assert ast.literal_eval(incremental_keywords["target_table_name"]) == "inventory_movements_append_all"
    assert "target_table_id" not in incremental_keywords
    assert "resolve_table_id" not in source

    full_tree = ast.parse(_demo_cell(name, "read-2").source)
    full_call = next(node for node in ast.walk(full_tree) if isinstance(node, ast.Call)
                     and isinstance(node.func, ast.Name) and node.func.id == "orchestrate_read")
    full_keywords = {keyword.arg: keyword.value for keyword in full_call.keywords}
    assert ast.literal_eval(full_keywords["read_mode"]) == "full"
    assert "target_table_id" not in full_keywords and "read_parameters" not in full_keywords

    destinations = []
    expected_inputs = ("incremental_append_all_df", "full_append_new_only_df")
    for cell_id, mode, expected_input in zip(
        ("write-1", "write-2"), ("append_all", "append_new_only"), expected_inputs, strict=True
    ):
        tree = ast.parse(_demo_cell(name, cell_id).source)
        call = next(node for node in ast.walk(tree) if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name) and node.func.id == "orchestrate_write")
        assert len(call.args) == 1 and isinstance(call.args[0], ast.Name)
        assert call.args[0].id == expected_input
        keywords = {keyword.arg: ast.literal_eval(keyword.value) for keyword in call.keywords}
        assert keywords["store"] == "Silver" and keywords["schema"] == "demo"
        assert keywords["write_mode"] == mode
        destinations.append(keywords["table_name"])
    assert destinations == ["inventory_movements_append_all", "inventory_movements_append_new_only"]
    assert 'incremental_append_all_df = transform_inventory(' in source
    assert 'full_append_new_only_df = transform_inventory(' in source
    assert source.count("finalize_pipeline(") == 2
    for cell_id, target in (("write-1", destinations[0]), ("write-2", destinations[1])):
        write = _demo_cell(name, cell_id).source
        assert f'table_name="{target}"' in write
        assert '.orderBy("movement_id").limit(10)' in write
    assert "| 1 | 8 / 8 / 8 | 8 / 8 / 8 | 8 | 8 |" in source
    assert "| 2 | 4 / 4 / 4 | 12 / 12 / 4 | 12 | 12 |" in source
    assert "| 3 | 0 / 0 / 0 | 12 / 12 / 0 | 12 | 12 |" in source


def test_02b_guided_demo_restores_and_resolves_instructional_images():
    """The visual walkthrough remains a tested part of the 02B teaching contract."""
    page = ROOT / "docs/guided-demo/02B-build-and-run-incremental-append-etl.md"
    content = page.read_text(encoding="utf-8")
    references = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", content)
    local_references = [reference for reference in references if not reference.startswith(("http://", "https://", "/"))]
    assert local_references
    missing = [reference for reference in local_references if not (page.parent / unquote(reference)).resolve().is_file()]
    assert not missing
    required = {
        "File Upload.png",
        "Day 1.png", "Incremental_Read_Day1.png", "AppendAll_Day1.png", "Full_Read_Day1.png", "AppendNew_Day1.png",
        "Day 2.png", "Incremental_Read_Day2.png", "AppendAll_Day2.png", "Full_Read_Day2.png", "AppendNew_Day2.png",
        "Day 3.png", "Incremental_Read_Day3.png", "AppendAll_Day3.png", "Full_Read_Day3.png", "AppendNew_Day3.png",
    }
    assert required <= {Path(unquote(reference)).name for reference in local_references}


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
        write = _demo_cell("02C_scd_demo.ipynb", cell_id).source
        assert f'display(writes["{target}"]["dataframe"].limit(10))' in write
        assert "final prepared Write input" in write
        assert "# Optional: read the final published target after a successful persistent execution." in write
        expected_order = '.orderBy("product_id").limit(10)' if cell_id == "write-1" else (
            '.orderBy("product_id", "_effective_from").limit(10)'
        )
        assert expected_order in write
    assert "| 1 | 8 | 8 |" in source
    assert "| 2 | 8 | 9 |" in source
    assert "| 3 | 8 | 10 |" in source


def test_guided_demo_pages_match_the_notebook_split():
    """Plug-and-Play 02 is reusable guidance and Steps 2A-2C point to ready-to-run assets."""
    step_2 = (ROOT / "docs/guided-demo/02-build-and-run-etl.md").read_text(encoding="utf-8")
    step_2a = (ROOT / "docs/guided-demo/02A-full-refresh-demo.md").read_text(encoding="utf-8")
    step_2b = (ROOT / "docs/guided-demo/02B-build-and-run-incremental-append-etl.md").read_text(encoding="utf-8")
    step_2c = (ROOT / "docs/guided-demo/02C-build-and-run-scd-etl.md").read_text(encoding="utf-8")
    step_3 = (ROOT / "docs/guided-demo/03-author-and-freeze-data-contract.md").read_text(encoding="utf-8")

    assert "# Plug-and-Play 02: Pipeline Template" in step_2
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
    # Commented exploratory examples are allowed; executable profiling is not.
    manual_profile_calls = [
        node
        for cell in notebook.cells if cell.cell_type == "code"
        for node in ast.walk(ast.parse(cell.source))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "profile_table"
    ]
    assert not manual_profile_calls
    if notebook_path.name == "02B_incremental_append_demo.ipynb":
        finalize_calls = []
        for code_cell in (cell for cell in notebook.cells if cell.cell_type == "code"):
            tree = ast.parse(code_cell.source)
            finalize_calls.extend(
                node for node in ast.walk(tree) if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name) and node.func.id == "finalize_pipeline"
            )
        assert len(finalize_calls) == 2
        assert all(len(call.args) == 1 for call in finalize_calls)
        source = "\n".join(cell.source for cell in notebook.cells)
        assert "persist_source_observations" not in source
        return
    cell = next(cell for cell in notebook.cells if cell.get("id") == "finalize-run")
    pipeline, result = object(), {"status": "ungoverned_completed"}
    calls = []
    namespace = {"pipeline": pipeline, "finalize_pipeline": lambda value: calls.append(value) or result}
    exec(cell.source, namespace)
    assert calls == [pipeline] and namespace["pipeline_result"] is result
    tree = ast.parse(cell.source)
    assert [node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call)] == ["finalize_pipeline"]
    source = "\n".join("".join(cell.source) for cell in notebook.cells)
    assert "observation_profiles" not in source


def test_02_pipeline_file_write_guidance_matches_automatic_layout_api():
    """The parameter table describes current modes and the internal layout policy."""
    notebook = _load_notebook(NOTEBOOK_DIR / '02_pipeline.ipynb')
    guidance = next(cell.source for cell in notebook.cells if cell.id == 'write-heading')
    assert '| `single_file` |' not in guidance
    assert '| `max_single_file_rows` |' not in guidance
    assert '| `max_single_file_bytes` |' not in guidance
    assert 'one physical file by default' in guidance
    assert '1,000,000 rows' in guidance and '100,000,000 encoded bytes (100 MB)' in guidance
    assert 'exact requested path' in guidance
    assert 'Files: `"overwrite"` or `"append_all"`' in guidance
    assert 'omit the `Files/` prefix' in guidance
    for field in ('output_layout', 'overflow_reason', 'file_count', 'output_bytes', 'publication_status'):
        assert f'`{field}`' in guidance


@pytest.mark.parametrize('relative', [
    'notebooks/02_pipeline.ipynb', 'DemoData/02A_full_refresh_demo.ipynb', 'DemoData/00C_demo_setup.ipynb',
])
def test_living_file_write_callers_use_current_public_keywords(relative):
    """Demo and standard writer calls bind to the public API without removed knobs."""
    import inspect
    from fabricops_kit import orchestrate_write, write_lakehouse_file

    functions = {'orchestrate_write': orchestrate_write, 'write_lakehouse_file': write_lakehouse_file}
    for _, source in _code_cells(ROOT / 'templates' / relative):
        for call in ast.walk(ast.parse(source)):
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id in functions:
                signature = inspect.signature(functions[call.func.id])
                keywords = {keyword.arg: object() for keyword in call.keywords if keyword.arg is not None}
                signature.bind(*[object() for _ in call.args], **keywords)
