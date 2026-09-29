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
        "02B_incremental_append_pipeline.ipynb",
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
    assert "same `02_pipeline`" in step_4
    assert "do not edit a frozen version in place" in normalized["step_4"]
    assert "defaults every table to **enforce**" in normalized["step_4"]
    assert "`pipeline_write()` is never reached" in normalized["step_4"]

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


def test_02_pipeline_has_simple_top_level_sequence():
    """The template stays Read -> Transform -> Write without splitting one write across sections."""
    source = _notebook_source("02_pipeline.ipynb")
    headings = ("# 0. Environment", "# 1. Data Contract", "# 2. Full Read", "# 3. Transform", "# 4. Write")
    assert [source.index(heading) for heading in headings] == sorted(source.index(heading) for heading in headings)
    for removed in ("# 4. Target", "# 5. Write Preparation / Guardrails", "# 6. Write", "# 7. Persisted Target Profile"):
        assert removed not in source


def test_02_pipeline_initializes_data_contracts_once_in_plain_language():
    """The contract configuration separates execution mode from environment."""
    source = _notebook_source("02_pipeline.ipynb")
    contracts = _cell_by_id("02_pipeline.ipynb", "contracts-heading").source
    assert "Enforce" in contracts
    assert "Validate" in contracts
    assert "exact frozen candidate picker" in contracts
    assert "CONTRACT_MODE" not in source
    assert "VALIDATE_CONTRACTS" not in source
    assert source.count("widget_select_data_contract(spark_session=spark)") == 1


def test_guided_demo_preserves_default_enforce_flow_and_optional_target_validation():
    """The existing walkthrough remains runnable without changing the selector default."""
    step_2 = (ROOT / "docs/guided-demo/02-build-and-run-etl.md").read_text(encoding="utf-8")
    step_4 = (ROOT / "docs/guided-demo/04-validate-frozen-data-contract.md").read_text(encoding="utf-8")

    assert "defaults every discovered source and target to **Enforce**" in step_2
    assert "no mode change is required for the initial Guided Demo run" in step_2
    assert "same cloneable blocks" in step_2
    assert "switches only the governed target to Validate mode" in step_2
    assert "leave every source table in **Enforce** mode" in step_4
    assert "exact same Schema, Sensitive Data, Source Drift, Data Quality" in step_4
    assert "Validate returns `published=False` and `validation_passed=True`" in step_4
    assert "business target can be written" in step_4


def test_02_pipeline_target_validate_mode_exits_before_business_write():
    """The orchestrator owns validation and the notebook exits on validation-only success."""
    for index in (1, 2):
        block = _cell_by_id("02_pipeline.ipynb", f"write-{index}").source
        assert "contracts=CONTRACTS" in block
        assert 'if not write_result["published"]:' in block
        assert "notebookutils.notebook.exit" in block
        assert block.index("orchestrate_write(") < block.index("notebookutils.notebook.exit")
        assert 'CONTRACTS["validate"]' not in block

def test_02_pipeline_is_full_read_and_full_profile_by_design():
    """The standard orchestrator receives full mode for complete-source profiling."""
    source = _notebook_source("02_pipeline.ipynb")
    code = "\n".join(source for _, source in _code_cells(NOTEBOOK_DIR / "02_pipeline.ipynb"))
    assert "full refresh pipeline template" in source.lower()
    assert "full read → transform → full overwrite" in source
    assert code.count('read_mode="full"') == 3
    assert "READ_MODE =" not in code
    assert source.count("source = orchestrate_read(") == 3
    assert "profile_table(" not in source

def test_02_pipeline_warehouse_example_uses_projection_without_incremental_filter():
    """Order History demonstrates Warehouse SQL projection while keeping a full row scope."""
    block = _cell_by_id("02_pipeline.ipynb", "read-3").source
    assert 'store="Gold"' in block
    assert 'table_name="order_history"' in block
    assert "SELECT" in block
    assert "historical_order_id" in block
    assert "customer_id" in block
    assert "order_datetime" in block
    assert "net_amount" in block
    assert "FROM demo.order_history" in block
    assert "WHERE" not in block
    assert 'query="SELECT historical_order_id, customer_id, order_datetime, net_amount FROM demo.order_history"' in block


def test_02_pipeline_source_dictionary_is_explained():
    """The notebook tells engineers exactly what the multi-source dictionary contains."""
    setup = _cell_by_id("02_pipeline.ipynb", "read-setup").source
    assert "Dictionary used to keep multiple source reads" in setup
    assert "source results for transformation and lineage" in setup
    assert "sources = {}" in setup


def test_02_pipeline_read_blocks_use_standard_orchestration():
    """Every source exposes decisions before one standard orchestrator call."""
    for index, read_name in ((1, "orders"), (2, "products"), (3, "history")):
        block = _cell_by_id("02_pipeline.ipynb", f"read-{index}").source
        call = block.index("orchestrate_read(")
        for name in ("READ_NAME", "READ_STORE", "READ_SCHEMA", "READ_TABLE", "READ_MODE", "READ_QUERY"):
            assert block.index(f"{name} =") < call
        assert f'READ_NAME = "{read_name}"' in block
        assert 'df = source["dataframe"]' in block
        assert "# display(df)" in block
        for expanded in ("pipeline_read(", "check_freshness(", "check_schema(", "check_dq(", "profile_table("):
            assert expanded not in block

def test_02_pipeline_transform_is_plain_pyspark():
    """Project transformation remains ordinary readable PySpark and produces two target DataFrames."""
    transform = _cell_by_id("02_pipeline.ipynb", "transform").source
    assert transform.count(".join(") == 2
    assert ".withColumn(" in transform
    assert "transformed_df = (" in transform
    assert "customer_summary_df = (" in transform
    assert "pipeline_transform" not in transform


def test_02_pipeline_demonstrates_full_refresh_writes_and_parallel_warehouse_write():
    """The full pipeline demo uses overwrite for both outputs and one parallel Warehouse write."""
    write_1 = _cell_by_id("02_pipeline.ipynb", "write-1").source
    write_2 = _cell_by_id("02_pipeline.ipynb", "write-2").source

    assert 'load_strategy="overwrite"' in write_1
    assert "repartition_by=None" in write_1
    assert 'load_strategy="overwrite"' in write_2
    assert "repartition_by=4" in write_2


def test_02_pipeline_write_dictionary_and_two_cloneable_writes():
    """Write blocks expose decisions before one standard orchestrator call."""
    setup = _cell_by_id("02_pipeline.ipynb", "write-setup").source
    assert "writes = {}" in setup
    for index in (1, 2):
        block = _cell_by_id("02_pipeline.ipynb", f"write-{index}").source
        call = block.index("orchestrate_write(")
        for name in ("WRITE_NAME", "WRITE_STORE", "WRITE_SCHEMA", "WRITE_TABLE", "WRITE_LOAD_STRATEGY"):
            assert block.index(f"{name} =") < call
        assert "contracts=CONTRACTS" in block
        assert "# display(WRITE_DATAFRAME)" in block
        for expanded in ("resolve_table_id(", "check_schema(", "check_sensitive_data(", "check_source_drift(", "check_dq(", "check_guardrail_coverage(", "pipeline_write(", "profile_table("):
            assert expanded not in block

def test_02_pipeline_keeps_standard_orchestration_at_public_boundaries():
    """Canonical 02 calls orchestrators without reconstructing their stages."""
    source = _notebook_source("02_pipeline.ipynb")
    assert source.count("source = orchestrate_read(") == 3
    assert source.count("write_result = orchestrate_write(") == 2
    assert "source = pipeline_read(" not in source
    assert "write_result = pipeline_write(" not in source

def test_02_pipeline_optional_display_stays_outside_orchestration():
    """Optional inspection remains explicit notebook code."""
    source = _notebook_source("02_pipeline.ipynb")
    assert source.count('# display(source["dataframe"])') == 3

def test_02_pipeline_main_path_is_runnable_not_disabled_preview():
    """Every required workflow cell contains active parseable code."""
    notebook = _load_notebook(NOTEBOOK_DIR / "02_pipeline.ipynb")
    required = {
        "contracts",
        "read-setup",
        "read-1",
        "read-2",
        "read-3",
        "transform",
        "write-setup",
        "write-1",
        "write-2",
    }
    by_id = {cell.get("id"): cell for cell in notebook.cells}
    for cell_id in required:
        cell = by_id[cell_id]
        assert cell.cell_type == "code"
        assert cell.execution_count is None
        assert not cell.outputs
        ast.parse(cell.source)


def test_02B_incremental_append_pipeline_is_target_aware_and_mixed_mode():
    """The 02B variant keeps one incremental driver and one full supporting source."""
    source = _notebook_source("02B_incremental_append_pipeline.ipynb")
    code = "\n".join(
        source
        for _, source in _code_cells(NOTEBOOK_DIR / "02B_incremental_append_pipeline.ipynb")
    )
    target = _cell_by_id("02B_incremental_append_pipeline.ipynb", "flow-1-target").source
    incremental_read = _cell_by_id(
        "02B_incremental_append_pipeline.ipynb", "flow-1-read-incremental"
    ).source
    assert "# 02B Incremental Append Pipeline" in source
    assert "target_1_table_id = resolve_table_id(" in target
    assert 'read_mode="incremental"' in incremental_read
    assert code.count('read_mode="incremental"') == 1
    assert code.count('read_mode="full"') == 1
    assert source.count("target_table_id=target_1_table_id") >= 2
    assert 'orders_1["should_process"]' in source
    assert "incremental driving source + full supporting source → append target" in source
    assert "target_2" not in source
    assert "METADATA_SOURCE_OBSERVATION" not in source
    assert "spark.sql(" not in source


def test_02B_incremental_append_pipeline_profiles_only_full_source_and_persisted_target():
    """The partial incremental batch never masquerades as a canonical full-table profile."""
    source = _notebook_source("02B_incremental_append_pipeline.ipynb")
    assert 'profile_table(store="Bronze", schema="demo", table_name="orders")' not in source
    assert 'profile_table(store="Bronze", schema="demo", table_name="products")' in source
    assert 'profile_table(table_id=target_1_write["table_id"])' in source
    assert source.index("target_1_write = pipeline_write(") < source.index(
        'target_1_profile = profile_table(table_id=target_1_write["table_id"])'
    )


def test_02B_incremental_append_pipeline_is_one_append_publication_pattern():
    """The 02B variant demonstrates only incremental-read to append publication."""
    source = _notebook_source("02B_incremental_append_pipeline.ipynb")
    assert source.count("target_1_write = pipeline_write(") == 1
    assert source.count("check_source_drift(") == 2
    assert source.count("check_guardrail_coverage(") == 1
    assert 'TARGET_1_LOAD_STRATEGY = "append"' in source
    assert "TARGET_2_LOAD_STRATEGY" not in source
    assert '"scd1"' not in source
    assert '"scd2"' not in source
    assert "separate `02C` or `02D` pipeline variant" in source
    assert "not yet been manually validated in Microsoft Fabric" in source


# Standard 02 migration surfaces: these protect transplantability without snapshotting the notebook.
def test_02_pipeline_preserves_migration_surfaces():
    """Keep configuration and project transformation easy to transplant into a newer template."""
    notebook = _load_notebook(NOTEBOOK_DIR / "02_pipeline.ipynb")
    cell_ids = [cell.get("id") for cell in notebook.cells]
    required_order = [
        "environment",
        "contracts",
        "read-setup",
        "read-1",
        "read-2",
        "read-3",
        "transform",
        "write-setup",
        "write-1",
        "write-2",
    ]
    positions = [cell_ids.index(cell_id) for cell_id in required_order]
    assert positions == sorted(positions)

    transform = _cell_by_id("02_pipeline.ipynb", "transform").source
    assert "pipeline_read(" not in transform
    assert "pipeline_write(" not in transform

    for cell_id in ("read-1", "read-2", "read-3"):
        block = _cell_by_id("02_pipeline.ipynb", cell_id).source
        first_read = block.index("orchestrate_read(")
        for name in ("READ_NAME", "READ_STORE", "READ_SCHEMA", "READ_TABLE", "READ_MODE", "READ_QUERY"):
            assert block.index(f"{name} =") < first_read

    for cell_id in ("write-1", "write-2"):
        block = _cell_by_id("02_pipeline.ipynb", cell_id).source
        first_write = block.index("orchestrate_write(")
        for name in ("WRITE_NAME", "WRITE_STORE", "WRITE_SCHEMA", "WRITE_TABLE", "WRITE_LOAD_STRATEGY"):
            assert block.index(f"{name} =") < first_write


def test_02_pipeline_scaffold_uses_public_fabricops_boundary():
    """Prevent the standard pipeline from depending on private FabricOps implementation modules."""
    for cell_index, source in _code_cells(NOTEBOOK_DIR / "02_pipeline.ipynb"):
        tree = _parse_code_cell(NOTEBOOK_DIR / "02_pipeline.ipynb", cell_index, source)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith("fabricops_kit."), (
                    f"02_pipeline.ipynb cell {cell_index} imports FabricOps internals: {node.module}"
                )
