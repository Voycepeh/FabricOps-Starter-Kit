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


def test_02_pipeline_imports_required_public_apis_and_uses_indexed_state():
    """The canonical Orders pipeline uses only public APIs and named indexed state."""
    source = _notebook_source("02_pipeline.ipynb")
    imports = _cell_by_id("02_pipeline.ipynb", "imports").source

    for name in (
        "read_lakehouse_table", "read_warehouse_query", "read_pipeline_prep",
        "write_pipeline_prep", "write_lakehouse_table", "profile_and_register_table",
    ):
        assert name in imports
    for state in (
        "SOURCES", "SOURCE_PREPS", "SOURCE_DFS", "SOURCE_PROFILES", "SOURCE_RESULTS",
        "TARGETS", "TARGET_DFS", "TARGET_PREPS", "TARGET_PROFILES", "TARGET_RESULTS",
    ):
        assert f"{state} = {{}}" in source
    for forbidden in ("globals()", "locals()", "exec(", "source_1_df", "source_2_df", "source_3_df"):
        assert forbidden not in source
    assert "from fabricops_kit.pipeline" not in source
    assert "from fabricops_kit.io" not in source


def test_02_pipeline_uses_three_registered_managed_sources():
    """Each exact managed source has a canonical selected table identity and preparation."""
    for key in ("orders", "products", "order_history"):
        config = _cell_by_id("02_pipeline.ipynb", f"{key if key != 'order_history' else 'history'}-config").source
        prepare = _cell_by_id("02_pipeline.ipynb", f"{key if key != 'order_history' else 'history'}-prepare").source
        assert '"table_id"' in config
        assert 'selection["table_id"]' in config
        assert "read_pipeline_prep(" in prepare
        assert 'source_table_id=source["table_id"]' in prepare
    assert '"table_name": "orders"' in _cell_by_id("02_pipeline.ipynb", "orders-config").source
    assert '"table_name": "products"' in _cell_by_id("02_pipeline.ipynb", "products-config").source
    assert '"table_name": "order_history"' in _cell_by_id("02_pipeline.ipynb", "history-config").source


def test_02_pipeline_uses_required_physical_readers():
    """Orders and Products use Lakehouse reads while history uses pushed-down Warehouse SQL."""
    orders = _cell_by_id("02_pipeline.ipynb", "orders-read").source
    products = _cell_by_id("02_pipeline.ipynb", "products-read").source
    history = _cell_by_id("02_pipeline.ipynb", "history-read").source

    assert "read_lakehouse_table(" in orders
    assert 'processing_scope=source_prep["scope"]' in orders
    assert "read_lakehouse_table(" in products
    assert 'processing_scope=source_prep["scope"]' in products
    assert "read_warehouse_query(" in history
    for column in ("customer_id", "historical_order_count", "historical_net_amount", "latest_historical_order_datetime"):
        assert column in history
    assert "FROM demo.order_history" in history
    assert "read_warehouse_table(" not in history


def test_02_pipeline_keeps_strategy_and_runtime_mode_distinct():
    """Configured strategies remain distinct from runtime modes returned by preparation."""
    source = _notebook_source("02_pipeline.ipynb")

    for strategy in ("full_dataset", "incremental_watermark", "incremental_partition"):
        assert strategy in source
    for runtime_mode in ("full_dataset", "incremental_subset", "skip"):
        assert runtime_mode in source
    orders = _cell_by_id("02_pipeline.ipynb", "orders-config").source
    assert '"read_strategy": "incremental_watermark"' in orders
    assert '"watermark_column": "modified_datetime"' in orders
    prepare = _cell_by_id("02_pipeline.ipynb", "orders-prepare").source
    assert "target_table_id=CURATED_ORDERS_TABLE_ID" in prepare
    assert 'PIPELINE_SHOULD_RUN = source_prep["read_mode"] != "skip"' in prepare


def test_02_pipeline_uses_orders_to_gate_multi_source_physical_work():
    """An unchanged Orders source skips every physical read and downstream action."""
    for cell_id in (
        "orders-read", "orders-quality", "products-read", "history-read", "transform",
        "target-guard", "target-prepare", "target-publish", "target-evidence",
    ):
        source = _cell_by_id("02_pipeline.ipynb", cell_id).source
        assert "if PIPELINE_SHOULD_RUN:" in source
    assert 'SOURCE_DFS["products"] = None' in _cell_by_id("02_pipeline.ipynb", "products-read").source
    assert 'SOURCE_DFS["order_history"] = None' in _cell_by_id("02_pipeline.ipynb", "history-read").source


def test_02_pipeline_transformation_consumes_all_sources():
    """Visible project-owned PySpark joins all three logical Orders inputs."""
    source = _cell_by_id("02_pipeline.ipynb", "transform").source
    tree = ast.parse(source)
    names = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)}

    assert {"orders", "products", "order_history"} <= names
    assert source.count(".join(") == 2
    assert 'on="product_id"' in source
    assert 'on="customer_id"' in source
    assert '"modified_datetime"' in source
    assert "order_net_amount" in source


def test_02_pipeline_profiles_sources_without_replacing_partial_profiles():
    """Only complete table reads register canonical profiles; slices and query aggregates are diagnostic."""
    orders = _cell_by_id("02_pipeline.ipynb", "orders-quality").source
    products = _cell_by_id("02_pipeline.ipynb", "products-read").source
    history = _cell_by_id("02_pipeline.ipynb", "history-read").source
    tree = ast.parse(orders)
    mode_if = next(node for node in ast.walk(tree) if isinstance(node, ast.If) and "read_mode" in ast.unparse(node.test))

    assert "full_dataset" in ast.unparse(mode_if.test)
    assert "profile_and_register_table(" in ast.unparse(mode_if.body)
    assert "incremental_subset" in ast.unparse(mode_if.orelse)
    assert "profile_dataframe(" in ast.unparse(mode_if.orelse)
    assert "profile_and_register_table(" not in ast.unparse(mode_if.orelse)
    assert "profile_and_register_table(" in products
    assert "profile_dataframe(" in history
    assert "profile_and_register_table(" not in history


def test_02_pipeline_prepares_target_before_publication_and_uses_all_values():
    """The physical writer consumes the authoritative preparation output."""
    notebook_source = _notebook_source("02_pipeline.ipynb")
    prepare = _cell_by_id("02_pipeline.ipynb", "target-prepare").source
    publish = _cell_by_id("02_pipeline.ipynb", "target-publish").source

    assert notebook_source.index("write_pipeline_prep(") < notebook_source.index("write_lakehouse_table(")
    for key in ("orders", "products", "order_history"):
        assert f'SOURCE_PREPS["{key}"]' in prepare
    assert 'prepared_target_df = target_prep["df"].persist()' in prepare
    for argument in (
        'mode=target_prep["mode"]', 'options=target_prep["options"]',
        'load_strategy=target_prep["load_strategy"]',
        'load_strategy_parameters=target_prep["load_strategy_parameters"]',
        'processing_scope=target_prep["scope"]',
    ):
        assert argument in publish


def test_02_pipeline_preserves_spark_parallel_target_processing_and_evidence():
    """Prepared target work stays Spark-distributed and produces full-table governed evidence."""
    prepare = _cell_by_id("02_pipeline.ipynb", "target-prepare").source
    publish = _cell_by_id("02_pipeline.ipynb", "target-publish").source
    evidence = _cell_by_id("02_pipeline.ipynb", "target-evidence").source
    markdown = _notebook_source("02_pipeline.ipynb")

    assert ".persist()" in prepare
    assert "profile_dataframe(prepared_target_df)" in publish
    assert "write_lakehouse_table(" in publish
    assert ".unpersist()" in publish
    assert "read_lakehouse_table(" in evidence
    assert "profile_and_register_table(" in evidence
    assert 'profile_role="target"' in evidence
    assert "METADATA_DATA_CATALOGUE" in markdown
    assert "METADATA_DATA_PROFILED" in markdown
    assert "METADATA_DATA_PROFILED_FREQUENCY" in markdown
    assert "METADATA_DATA_LINEAGE" in markdown
    assert "ThreadPool" not in markdown
    assert "multiprocessing" not in markdown


def test_02_pipeline_surfaces_stable_curated_orders_table_id():
    """The downstream Lakehouse identity is validated and visibly handed to later steps."""
    config = _cell_by_id("02_pipeline.ipynb", "target-config").source
    evidence = _cell_by_id("02_pipeline.ipynb", "target-evidence").source

    assert 'target_selection["store_type"] != "lakehouse"' in config
    assert 'target_selection["layer"] != "unified"' in config
    assert 'target_selection.get("schema_name") != "demo"' in config
    assert 'target_selection["table_name"] != "orders"' in config
    assert 'CURATED_ORDERS_TABLE_ID = target["table_id"]' in config
    assert "Curated Orders table_id" in evidence


def test_02_pipeline_main_path_is_runnable_not_disabled_preview():
    """Every governed workflow cell is active, output-free portable notebook code."""
    notebook = _load_notebook(NOTEBOOK_DIR / "02_pipeline.ipynb")
    required = {
        "target-selection", "orders-config", "orders-prepare", "orders-read", "orders-quality",
        "products-config", "products-prepare", "products-read", "history-config", "history-prepare",
        "history-read", "transform", "target-prepare", "target-publish", "target-evidence",
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
            len(tree.body) == 1 and isinstance(tree.body[0], ast.Expr)
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
