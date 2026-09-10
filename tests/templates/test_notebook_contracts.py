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


def test_02_pipeline_imports_required_public_apis_and_keeps_minimal_state():
    """The canonical pipeline keeps only cross-block state and uses public APIs."""
    source = _notebook_source("02_pipeline.ipynb")
    imports = _cell_by_id("02_pipeline.ipynb", "imports").source

    for name in (
        "read_lakehouse_table",
        "read_warehouse_query",
        "read_pipeline_prep",
        "write_pipeline_prep",
        "write_lakehouse_table",
        "profile_and_register_table",
        "widget_select_data_contract",
        "widget_view_catalogue",
    ):
        assert name in imports

    assert "EXTRACT_PREPS = {}" in imports
    assert "EXTRACT_DFS = {}" in imports
    assert "PIPELINE_SHOULD_RUN = True" in imports

    for removed_state in (
        "SOURCES = {}",
        "SOURCE_PROFILES = {}",
        "SOURCE_RESULTS = {}",
        "TARGETS = {}",
        "TARGET_DFS = {}",
        "TARGET_PREPS = {}",
        "TARGET_PROFILES = {}",
        "TARGET_RESULTS = {}",
    ):
        assert removed_state not in source

    for forbidden in ("globals()", "locals()", "exec(", "source_1_df", "source_2_df", "source_3_df"):
        assert forbidden not in source
    assert "from fabricops_kit.pipeline" not in source
    assert "from fabricops_kit.io" not in source


def test_02_pipeline_renders_notebook_scoped_controls_once():
    """Contract and Catalogue widgets remain notebook-scoped, not identity inputs."""
    source = _notebook_source("02_pipeline.ipynb")
    controls = _cell_by_id("02_pipeline.ipynb", "shared-catalogue").source

    assert source.count("widget_view_catalogue(") == 1
    assert source.count("widget_select_data_contract(") == 1
    assert "VALIDATE_DATA_CONTRACTS = False" in controls
    assert 'widget_view_catalogue(mode="explore"' in controls
    assert 'catalogue_widget["get_selection"]()' not in source
    assert "notebook name" in source


def test_02_pipeline_uses_etl_roles_without_framework_wiring():
    """The user-facing notebook reads as Extract, Transform, and Load."""
    source = _notebook_source("02_pipeline.ipynb")

    for heading in (
        "## EXTRACT 1 — Orders",
        "## EXTRACT 2 — Products",
        "## EXTRACT 3 — Order History",
        "## LOAD 1 — Curated Orders",
    ):
        assert heading in source
    for legacy_role in ("SOURCE_PREPS", "SOURCE_DFS", "SOURCE_NAME", "TARGET_NAME", "TARGET_TABLE_ID"):
        assert legacy_role not in source
    assert "pre_read_results" not in source
    assert "extract_checks" not in source
    assert "target_checks" not in source
    assert "all(result" not in source
    assert source.count("if VALIDATE_DATA_CONTRACTS") == 1
    assert 'read_lakehouse_table(\n        table_id=EXTRACT_TABLE_ID' in source
    assert 'catalogue_widget["show"](table_id=EXTRACT_TABLE_ID)' in source


def test_02_pipeline_prep_resolves_ids_from_small_physical_configs():
    """Engineers provide physical identity while prep owns deterministic table_id."""
    source = _notebook_source("02_pipeline.ipynb")
    for cell_id in ("source-1-config", "source-2-config", "source-3-config", "target-config"):
        assert "TABLE_ID =" not in _cell_by_id("02_pipeline.ipynb", cell_id).source
    for cell_id in ("source-1-run", "source-2-run", "source-3-run"):
        runner = _cell_by_id("02_pipeline.ipynb", cell_id).source
        assert "read_pipeline_prep(" in runner
        assert "source_target=EXTRACT_TARGET" in runner
        assert 'EXTRACT_TABLE_ID = extract_prep["table_id"]' in runner
    target = _cell_by_id("02_pipeline.ipynb", "target-guard").source
    assert "write_pipeline_prep(" in target
    assert "target=LOAD_TARGET" in target
    assert 'LOAD_TABLE_ID = load_prep["target"]["table_id"]' in target
    assert "build_table_id" not in source


def test_02_pipeline_has_explicit_source_readers_without_dispatch_tree():
    """Each source visibly chooses its physical reader without generic dispatch."""
    orders = _cell_by_id("02_pipeline.ipynb", "source-1-run").source
    products = _cell_by_id("02_pipeline.ipynb", "source-2-run").source
    history = _cell_by_id("02_pipeline.ipynb", "source-3-run").source

    assert "read_lakehouse_table(" in orders
    assert 'processing_scope=extract_prep["scope"]' in orders
    assert "read_lakehouse_table(" in products
    assert "read_warehouse_query(" in history
    assert "EXTRACT_QUERY" in history
    assert "SOURCE_READER" not in _notebook_source("02_pipeline.ipynb")
    assert "elif" not in orders + products + history


def test_02_pipeline_keeps_checks_and_profiles_visible_in_order():
    """Prep, checks, physical IO, profiling, storage, and views stay scan-visible."""
    for index in (1, 2, 3):
        runner = _cell_by_id("02_pipeline.ipynb", f"source-{index}-run").source
        assert runner.index("read_pipeline_prep(") < runner.index("extract_df = read_")
        assert runner.index("extract_df = read_") < runner.index("check_schema(")
        assert runner.index("check_schema(") < runner.index("check_dq(")
        assert runner.index("check_dq(") < runner.index("profile_and_register_table(")
        assert runner.index("profile_and_register_table(") < runner.index("EXTRACT_PREPS[EXTRACT]")
        assert 'catalogue_widget["show"](table_id=EXTRACT_TABLE_ID)' in runner
    orders = _cell_by_id("02_pipeline.ipynb", "source-1-run").source
    assert "check_freshness(" in orders
    assert orders.index("check_freshness(") < orders.index("extract_df = read_lakehouse_table(")


def test_02_pipeline_preserves_incremental_orders_and_one_skip_branch():
    """Orders owns bounded incremental work and one obvious downstream skip gate."""
    source = _notebook_source("02_pipeline.ipynb")
    orders_config = _cell_by_id("02_pipeline.ipynb", "source-1-config").source
    orders = _cell_by_id("02_pipeline.ipynb", "source-1-run").source

    assert 'EXTRACT_READ_STRATEGY = "incremental_watermark"' in orders_config
    assert 'EXTRACT_WATERMARK_COLUMN = "modified_datetime"' in orders_config
    assert 'processing_scope=extract_prep["scope"]' in orders
    assert 'PIPELINE_SHOULD_RUN = extract_prep["read_mode"] != "skip"' in orders
    assert source.count('extract_prep["read_mode"] != "skip"') == 1
    for cell_id in ("source-2-run", "source-3-run", "transform", "target-config", "target-guard", "target-prepare", "target-publish", "target-evidence"):
        assert "if PIPELINE_SHOULD_RUN:" in _cell_by_id("02_pipeline.ipynb", cell_id).source


def test_02_pipeline_profile_registration_owns_canonical_vs_diagnostic_scope():
    """One visible profiling API receives enough context to avoid partial replacement."""
    orders = _cell_by_id("02_pipeline.ipynb", "source-1-run").source
    products = _cell_by_id("02_pipeline.ipynb", "source-2-run").source
    history = _cell_by_id("02_pipeline.ipynb", "source-3-run").source
    for runner in (orders, products, history):
        assert "profile_and_register_table(" in runner
        assert 'processing_scope=extract_prep["scope"]' in runner
    assert "complete_table=False" in history
    assert "profile_dataframe(" not in orders + products + history


def test_02_pipeline_transform_is_explicit_project_pyspark():
    """Visible project-owned PySpark consumes all three source outputs."""
    transform = _cell_by_id("02_pipeline.ipynb", "transform").source
    for index in (1, 2, 3):
        assert f"EXTRACT_DFS[{index}]" in transform
    assert transform.count(".join(") == 2
    assert ".withColumn(" in transform


def test_02_pipeline_target_order_is_prep_checks_write_read_profile_view():
    """Target orchestration stays explicit and consumes every preparation value."""
    source = _notebook_source("02_pipeline.ipynb")
    prep = _cell_by_id("02_pipeline.ipynb", "target-guard").source
    checks = _cell_by_id("02_pipeline.ipynb", "target-prepare").source
    publish = _cell_by_id("02_pipeline.ipynb", "target-publish").source
    evidence = _cell_by_id("02_pipeline.ipynb", "target-evidence").source

    assert "source_preps=[" in prep
    for index in (1, 2, 3):
        assert f"EXTRACT_PREPS[{index}]" in prep
    assert "check_schema(" in checks and "check_dq(" in checks
    assert source.index("write_pipeline_prep(") < source.index("check_schema(LOAD_TABLE_ID")
    assert source.index("check_dq(", source.index("# L. Load")) < source.index("write_lakehouse_table(")
    for argument in ('mode=load_prep["mode"]', 'options=load_prep["options"]', 'processing_scope=load_prep["scope"]'):
        assert argument in publish
    assert "repartition_by=4" in publish
    assert "read_lakehouse_table(" in evidence
    assert evidence.index("read_lakehouse_table(") < evidence.index("profile_and_register_table(")
    assert 'catalogue_widget["show"](table_id=LOAD_TABLE_ID)' in evidence
    assert "ThreadPool" not in source and "multiprocessing" not in source


def test_02_pipeline_main_path_is_runnable_not_disabled_preview():
    """Every canonical workflow cell remains active and output-free."""
    notebook = _load_notebook(NOTEBOOK_DIR / "02_pipeline.ipynb")
    required = {
        "shared-catalogue",
        "target-anchor",
        "source-1-config",
        "source-1-run",
        "source-2-config",
        "source-2-run",
        "source-3-config",
        "source-3-run",
        "transform",
        "target-config",
        "target-guard",
        "target-prepare",
        "target-publish",
        "target-evidence",
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
