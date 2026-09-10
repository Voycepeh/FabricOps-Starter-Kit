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
            compile(tree, filename=f"{path}:{cell_index}", mode="exec")


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

    assert "SOURCE_PREPS = {}" in imports
    assert "SOURCE_DFS = {}" in imports
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


def test_02_pipeline_renders_shared_widgets_once():
    """Catalogue and Development contract selection are notebook-scoped controls."""
    source = _notebook_source("02_pipeline.ipynb")
    controls = _cell_by_id("02_pipeline.ipynb", "shared-catalogue").source

    assert source.count("widget_view_catalogue(") == 1
    assert source.count("widget_select_data_contract(") == 1
    assert 'catalogue_widget = widget_view_catalogue(' in controls
    assert "VALIDATE_DATA_CONTRACTS = False" in controls
    assert "CONTRACT_SELECTION = (" in controls

    for cell_id in ("source-1-run", "source-2-run", "source-3-run", "target-config"):
        assert 'catalogue_widget["get_selection"]()' in _cell_by_id("02_pipeline.ipynb", cell_id).source


def test_02_pipeline_source_blocks_are_cloneable():
    """Every source uses the same config names and identical execution skeleton."""
    required_names = (
        "SOURCE =",
        "SOURCE_NAME =",
        "SOURCE_STORE_TYPE =",
        "SOURCE_TARGET =",
        "SOURCE_SCHEMA =",
        "SOURCE_TABLE =",
        "SOURCE_READER =",
        "SOURCE_QUERY =",
        "SOURCE_READ_STRATEGY =",
        "SOURCE_WATERMARK_COLUMN =",
        "SOURCE_PARTITION_COLUMN =",
        "SOURCE_DRIVES_PIPELINE =",
    )
    configs = [
        _cell_by_id("02_pipeline.ipynb", f"source-{index}-config").source
        for index in (1, 2, 3)
    ]
    for config in configs:
        for name in required_names:
            assert name in config

    runners = [
        _cell_by_id("02_pipeline.ipynb", f"source-{index}-run").source
        for index in (1, 2, 3)
    ]
    assert runners[0] == runners[1] == runners[2]

    assert 'SOURCE = 1' in configs[0]
    assert 'SOURCE_TABLE = "orders"' in configs[0]
    assert 'SOURCE = 2' in configs[1]
    assert 'SOURCE_TABLE = "products"' in configs[1]
    assert 'SOURCE = 3' in configs[2]
    assert 'SOURCE_TABLE = "order_history"' in configs[2]


def test_02_pipeline_source_runner_supports_lakehouse_and_warehouse_query_reads():
    """The cloneable runner dispatches only from the small source configuration."""
    runner = _cell_by_id("02_pipeline.ipynb", "source-1-run").source
    history_config = _cell_by_id("02_pipeline.ipynb", "source-3-config").source

    assert "read_pipeline_prep(" in runner
    assert "source_table_id=SOURCE_TABLE_ID" in runner
    assert 'SOURCE_READER == "lakehouse_table"' in runner
    assert "read_lakehouse_table(" in runner
    assert 'processing_scope=source_prep["scope"]' in runner
    assert 'SOURCE_READER == "warehouse_query"' in runner
    assert "read_warehouse_query(" in runner

    for column in (
        "customer_id",
        "historical_order_count",
        "historical_net_amount",
        "latest_historical_order_datetime",
    ):
        assert column in history_config
    assert "FROM demo.order_history" in history_config


def test_02_pipeline_keeps_strategy_and_runtime_mode_distinct():
    """Configured strategies remain distinct from runtime modes returned by preparation."""
    source = _notebook_source("02_pipeline.ipynb")
    orders = _cell_by_id("02_pipeline.ipynb", "source-1-config").source
    runner = _cell_by_id("02_pipeline.ipynb", "source-1-run").source

    for strategy in ("full_dataset", "incremental_watermark", "incremental_partition"):
        assert strategy in source
    for runtime_mode in ("full_dataset", "incremental_subset", "skip"):
        assert runtime_mode in source

    assert 'SOURCE_READ_STRATEGY = "incremental_watermark"' in orders
    assert 'SOURCE_WATERMARK_COLUMN = "modified_datetime"' in orders
    assert "target_table_id=TARGET_TABLE_ID if SOURCE_READ_STRATEGY != \"full_dataset\" else None" in runner
    assert 'PIPELINE_SHOULD_RUN = source_prep["read_mode"] != "skip"' in runner


def test_02_pipeline_keeps_only_target_identity_as_an_early_incremental_anchor():
    """The target workflow stays under Load even though incremental prep needs its table_id."""
    source = _notebook_source("02_pipeline.ipynb")
    anchor = _cell_by_id("02_pipeline.ipynb", "target-anchor").source
    target = _cell_by_id("02_pipeline.ipynb", "target-config").source

    assert 'TARGET_TABLE_ID = target_anchor["table_id"]' in anchor
    assert source.index("## Pipeline configuration") < source.index("# E. Extract")
    assert source.index("# L. Load") < source.index("TARGET = 1")
    assert 'target_selection = catalogue_widget["get_selection"]()' in target
    assert 'target_selection["table_id"] != TARGET_TABLE_ID' in target


def test_02_pipeline_orders_drives_skip_without_blocking_cloneable_reference_sources():
    """Orders decides whether downstream physical work runs; other source blocks reuse the same runner."""
    runner = _cell_by_id("02_pipeline.ipynb", "source-1-run").source

    assert "if SOURCE_DRIVES_PIPELINE:" in runner
    assert 'PIPELINE_SHOULD_RUN = source_prep["read_mode"] != "skip"' in runner
    assert "if PIPELINE_SHOULD_RUN:" in runner
    assert "SOURCE_DFS[SOURCE] = None" in runner

    for cell_id in ("transform", "target-guard", "target-prepare", "target-publish", "target-evidence"):
        assert "if PIPELINE_SHOULD_RUN:" in _cell_by_id("02_pipeline.ipynb", cell_id).source


def test_02_pipeline_transformation_consumes_all_sources():
    """Visible project-owned PySpark joins the three numeric source outputs."""
    source = _cell_by_id("02_pipeline.ipynb", "transform").source

    for index in (1, 2, 3):
        assert f"SOURCE_DFS[{index}]" in source
    assert source.count(".join(") == 2
    assert 'on="product_id"' in source
    assert 'on="customer_id"' in source
    assert '"modified_datetime"' in source
    assert "order_net_amount" in source


def test_02_pipeline_profiles_full_sources_without_replacing_partial_profiles():
    """Full table reads may register profiles; slices and query aggregates remain diagnostic."""
    runner = _cell_by_id("02_pipeline.ipynb", "source-1-run").source
    tree = ast.parse(runner)

    assert 'SOURCE_READER == "warehouse_query"' in runner
    assert "profile_dataframe(source_df)" in runner
    assert 'source_prep["read_mode"] == "full_dataset"' in runner
    assert "profile_and_register_table(" in runner

    mode_if = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.If)
        and "read_mode" in ast.unparse(node.test)
        and "full_dataset" in ast.unparse(node.test)
    )
    assert "profile_and_register_table(" in ast.unparse(mode_if.body)
    assert "profile_dataframe(" in ast.unparse(mode_if.orelse)


def test_02_pipeline_prepares_target_before_publication_and_uses_all_values():
    """The target block consumes the exact governed preparation result."""
    source = _notebook_source("02_pipeline.ipynb")
    prepare = _cell_by_id("02_pipeline.ipynb", "target-prepare").source
    publish = _cell_by_id("02_pipeline.ipynb", "target-publish").source

    assert source.index("write_pipeline_prep(") < source.index("write_lakehouse_table(")
    assert "source_preps=[SOURCE_PREPS[1], SOURCE_PREPS[2], SOURCE_PREPS[3]]" in prepare
    assert 'prepared_target_df = target_prep["df"].persist()' in prepare

    for argument in (
        'mode=target_prep["mode"]',
        'options=target_prep["options"]',
        'load_strategy=target_prep["load_strategy"]',
        'load_strategy_parameters=target_prep["load_strategy_parameters"]',
        'processing_scope=target_prep["scope"]',
    ):
        assert argument in publish


def test_02_pipeline_preserves_distributed_write_processing_and_evidence():
    """The writer explicitly repartitions in Spark and produces full-table governed evidence."""
    publish = _cell_by_id("02_pipeline.ipynb", "target-publish").source
    evidence = _cell_by_id("02_pipeline.ipynb", "target-evidence").source
    markdown = _notebook_source("02_pipeline.ipynb")

    assert "profile_dataframe(prepared_target_df)" in publish
    assert "write_lakehouse_table(" in publish
    assert "repartition_by=4" in publish
    assert ".unpersist()" in publish
    assert "read_lakehouse_table(" in evidence
    assert "profile_and_register_table(" in evidence
    assert 'profile_role="target"' in evidence
    assert "METADATA_DATA_CATALOGUE" in markdown
    assert "METADATA_DATA_PROFILED" in markdown
    assert "METADATA_DATA_PROFILED_FREQUENCY" in markdown
    assert "METADATA_DATA_LINEAGE" in markdown
    assert "Python threads" in markdown
    assert "multiple independent writers" in markdown
    assert "ThreadPool" not in markdown
    assert "multiprocessing" not in markdown


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
