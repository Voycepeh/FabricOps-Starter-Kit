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
    return expression.value.value


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


def test_02_pipeline_uses_only_read_only_pipeline_widgets():
    """Verify the pipeline uses scoped, read-only widgets only."""
    source = _notebook_source("02_pipeline.ipynb")

    assert "widget_view_catalogue" in source
    assert "widget_select_data_contract" in source
    assert 'mode="pipeline"' in source
    assert "widget_view_data_contract" not in source
    assert "widget_author_" not in source
    assert "widget_enrich_" not in source
    assert "widget_activate_data_contract" not in source


def test_02_pipeline_preview_selects_validation_source_before_guardrail_execution():
    """Keep table-scoped contract selection ahead of Preview Guardrail execution."""
    source = _preview_payload("02_pipeline.ipynb", "preview-extract")

    source_selector = source.index("source_validation = widget_select_data_contract(")
    target_selector = source.index("target_validation = widget_select_data_contract(")
    schema_check = source.index("schema_result = check_schema(", source_selector)
    freshness_check = source.index("freshness_result = check_freshness(", schema_check)
    row_check = source.index("dq_result = check_dq(", freshness_check)

    assert source_selector < target_selector < schema_check < freshness_check < row_check
    assert 'SOURCE_TABLE_NAME, target=SOURCE_TARGET, schema=SOURCE_SCHEMA' in source
    assert source.count("widget_select_data_contract(") == 2
    assert 'read_prep["changes"]' in source
    assert "activate_contract_version" not in source
    assert "METADATA_DATA_CONTRACT" not in source


def test_02_pipeline_reuses_catalogue_selection_for_guardrail_evidence():
    """Preview review keeps one selector and the five selected-dataset surfaces."""
    source = _preview_payload("02_pipeline.ipynb", "preview-review")

    assert source.count("widget_view_catalogue(") == 1
    assert 'pipeline_catalogue_view["get_views"]()' in source
    for name in ("catalogue", "profile", "frequency", "guardrail_results", "guardrail_row_results"):
        assert f'display(views["{name}"])' in source
    assert "display_guardrail_results" not in source
    assert "run_table_guardrails" not in source
    assert "run_active_dq_guardrail" not in source


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


def test_02_pipeline_preview_catalogue_views_are_kept_inside_disabled_review_block():
    """Pipeline catalogue review stays visible but non-executing in Preview."""
    source = _preview_payload("02_pipeline.ipynb", "preview-review")

    assert 'pipeline_catalogue_view["get_views"]()' in source
    assert 'display(views["catalogue"])' in source
    assert 'display(views["profile"])' in source
    assert 'display(views["frequency"])' in source


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


def test_02_pipeline_preview_observes_before_read_and_profiles_after_row_checks():
    """Keep the Preview pre-read and row-level post-read source boundary explicit."""
    source = _preview_payload("02_pipeline.ipynb", "preview-extract")

    observation = source.index("read_prep = read_pipeline_prep(")
    schema_check = source.index("schema_result = check_schema(", observation)
    freshness_check = source.index("freshness_result = check_freshness(", schema_check)
    full_read = source.index("source_df = read_lakehouse_table(", observation)
    row_checks = source.index("dq_result = check_dq(", full_read)
    profile = source.index("source_profile_df = profile_and_register_table(", row_checks)

    assert observation < schema_check < freshness_check < full_read < row_checks < profile
    assert 'SOURCE_TARGET = "source"' in source
    assert 'SOURCE_SCHEMA = "dbo"' in source
    assert 'SOURCE_TABLE_NAME = "student_enrolment"' in source

    tree = ast.parse(source)
    skip_if = next(
        node for node in tree.body
        if isinstance(node, ast.If)
        and "read_strategy" in ast.unparse(node.test)
        and "skip" in ast.unparse(node.test)
    )
    assert "read_lakehouse_table(" not in "\n".join(ast.unparse(node) for node in skip_if.body)
    assert "read_lakehouse_table(" in "\n".join(ast.unparse(node) for node in skip_if.orelse)
    assert "check_dq(" in "\n".join(ast.unparse(node) for node in skip_if.orelse)

    run_body = skip_if.orelse
    incremental_if = next(
        node for node in run_body
        if isinstance(node, ast.If) and "incremental" in ast.unparse(node.test)
    )
    full_if = next(
        node for node in run_body
        if isinstance(node, ast.If) and "full" in ast.unparse(node.test)
    )
    assert "source_df.where(" in ast.unparse(incremental_if)
    assert "profile_and_register_table(" not in ast.unparse(incremental_if)
    assert "profile_and_register_table(" in ast.unparse(full_if.body)
    assert "source_profile_df = None" in ast.unparse(full_if.orelse)


def test_02_pipeline_profiles_complete_persisted_target_after_every_write():
    """Keep Live target profiling after the write and complete target read."""
    source = _notebook_source("02_pipeline.ipynb")

    write = source.index("write_lakehouse_table(")
    persisted_read = source.index("target_df = read_lakehouse_table(", write)
    target_profile = source.index("target_profile_df = profile_and_register_table(", persisted_read)

    assert write < persisted_read < target_profile


def test_02_pipeline_uses_one_governed_lakehouse_processing_definition():
    """Use public Preview prep boundaries while keeping physical IO visible."""
    extract = _preview_payload("02_pipeline.ipynb", "preview-extract")
    load = _preview_payload("02_pipeline.ipynb", "preview-load")
    source = f"{extract}\n{load}"

    assert 'TARGET_LOAD_STRATEGY = "scd1"' in source
    assert 'TARGET_LOAD_PARAMETERS = {"key_columns": ["student_id"]}' in source
    assert source.count("read_pipeline_prep(") == 1
    assert source.count("write_pipeline_prep(") == 1
    assert "from fabricops_kit.pipeline.shared" not in source
    assert "_resolve_processing_scope" not in source
    assert "_apply_load_strategy" not in source
    assert source.index("read_pipeline_prep(") < source.index("source_df = read_lakehouse_table(")
    assert source.index("check_schema(") < source.index("source_df = read_lakehouse_table(")
    assert 'read_prep["read_strategy"] == "skip"' in source
    assert 'read_prep["read_strategy"] == "incremental"' in source
    assert 'load_strategy=write_prep["load_strategy"]' in source
    assert 'load_strategy_parameters=write_prep["load_strategy_parameters"]' in source
    assert 'processing_scope=write_prep["scope"]' in source
    assert "load_strategy=TARGET_LOAD_STRATEGY" in source
    assert "load_strategy_parameters=TARGET_LOAD_PARAMETERS" in source
    assert "write_strategy" not in source


def test_02_pipeline_maturity_contract_keeps_live_expanded_and_preview_disabled():
    """Live examples stay runnable while Preview blocks stay collapsed and inert."""
    notebook = _load_notebook(NOTEBOOK_DIR / "02_pipeline.ipynb")
    by_id = {cell.get("id"): cell for cell in notebook.cells}

    preview_ids = {"preview-extract", "preview-load", "preview-review"}
    live_ids = {"run-env", "imports", "read-csv", "transform", "live-lakehouse-load"}

    for cell_id in preview_ids:
        cell = by_id[cell_id]
        assert cell.cell_type == "code"
        assert cell.metadata.get("collapsed") is True
        tree = ast.parse(cell.source)
        assert len(tree.body) == 1
        assert isinstance(tree.body[0], ast.Expr)
        assert isinstance(tree.body[0].value, ast.Constant)
        assert isinstance(tree.body[0].value.value, str)

    for cell_id in live_ids:
        cell = by_id[cell_id]
        assert cell.cell_type == "code"
        assert cell.metadata.get("collapsed") is False

    assert "write_warehouse_table(" in _notebook_source("02_pipeline.ipynb")
