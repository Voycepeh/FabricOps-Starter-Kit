"""Contract tests for FabricOps notebook templates."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import nbformat

from fabricops_kit import __all__ as FABRICOPS_PUBLIC_EXPORTS

ROOT = Path(__file__).parents[2]
NOTEBOOK_DIR = ROOT / "templates" / "notebooks"


def _notebook(name: str):
    return nbformat.read(NOTEBOOK_DIR / name, as_version=4)


def _cell_by_id(name: str, cell_id: str):
    notebook = _notebook(name)
    return next(cell for cell in notebook.cells if cell.get("id") == cell_id)


def _code(name: str) -> str:
    return "\n".join(cell.source for cell in _notebook(name).cells if cell.cell_type == "code")


def _markdown(name: str) -> str:
    return "\n".join(cell.source for cell in _notebook(name).cells if cell.cell_type == "markdown")


def test_template_notebooks_are_valid_and_code_cells_compile():
    """Every committed notebook is valid nbformat and every Python code cell compiles."""
    for path in NOTEBOOK_DIR.glob("*.ipynb"):
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        for cell in notebook.cells:
            if cell.cell_type != "code":
                continue
            source = cell.source
            if source.lstrip().startswith("%"):
                continue
            compile(source, str(path), "exec")


def test_template_notebook_fabricops_public_references_exist():
    """Public FabricOps names imported by templates remain root exported."""
    exports = set(FABRICOPS_PUBLIC_EXPORTS)
    for path in NOTEBOOK_DIR.glob("*.ipynb"):
        notebook = nbformat.read(path, as_version=4)
        for cell in notebook.cells:
            if cell.cell_type != "code":
                continue
            try:
                tree = ast.parse(cell.source)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module == "fabricops_kit":
                    for alias in node.names:
                        assert alias.name in exports, f"{path.name} imports missing public API {alias.name}"


def test_00_env_config_uses_setup_notebook():
    """Environment template stays centered on setup_notebook."""
    code = _code("00_env_config.ipynb")
    assert "setup_notebook" in code
    assert "FrameworkConfig" in code


def test_01_governance_contains_governance_workflow():
    """Governance template exposes steward, agreement and contract authoring workflow."""
    code = _code("01_governance.ipynb")
    for name in (
        "widget_render_data_steward",
        "widget_render_data_agreement",
        "widget_author_data_contract",
        "widget_activate_data_contract",
    ):
        assert name in code


def test_02_pipeline_imports_current_public_pipeline_api():
    """Pipeline template imports only the current public pipeline surface it uses."""
    imports = _cell_by_id("02_pipeline.ipynb", "imports").source
    for name in (
        "check_dq",
        "check_freshness",
        "check_guardrail_coverage",
        "check_schema",
        "check_sensitive_data",
        "check_source_drift",
        "pipeline_read",
        "pipeline_write",
        "profile_table",
        "resolve_table_id",
        "widget_select_data_contract",
    ):
        assert name in imports
    assert "widget_view_catalogue" not in imports


def test_02_pipeline_is_full_read_template():
    """Pipeline template explicitly represents full reads with target-side processing strategies."""
    title = _cell_by_id("02_pipeline.ipynb", "title").source
    read_heading = _cell_by_id("02_pipeline.ipynb", "read-heading").source
    assert "Full Read Pipeline Template" in title
    assert "reads one complete governed source" in read_heading
    assert "source-side incremental reads" in read_heading


def test_02_pipeline_has_cloneable_source_dictionary():
    """Pipeline template stores multiple named source results for later transform/write use."""
    setup = _cell_by_id("02_pipeline.ipynb", "read-setup").source
    assert "sources = {}" in setup
    assert "READ_NAME" in setup
    assert "pipeline_read() result" in setup


def test_02_pipeline_contract_selection_precedes_reads():
    """Contract selection remains before governed reads."""
    notebook = _notebook("02_pipeline.ipynb")
    ids = [cell.get("id") for cell in notebook.cells]
    assert ids.index("contracts") < ids.index("read-setup")
    contracts = _cell_by_id("02_pipeline.ipynb", "contracts").source
    assert "widget_select_data_contract" in contracts


def test_02_pipeline_contains_three_demo_reads():
    """Demo template includes the intended Lakehouse and Warehouse source examples."""
    code = _code("02_pipeline.ipynb")
    assert 'READ_NAME = "orders"' in code
    assert 'READ_NAME = "products"' in code
    assert 'READ_NAME = "history"' in code
    assert 'READ_STORE = "source"' in code
    assert 'READ_STORE = "product"' in code


def test_02_pipeline_has_two_cloneable_write_blocks():
    """Pipeline template demonstrates separate target flows for Lakehouse and Warehouse outputs."""
    code = _code("02_pipeline.ipynb")
    assert 'WRITE_NAME = "curated_orders_lakehouse"' in code
    assert 'WRITE_NAME = "customer_summary_warehouse"' in code
    assert 'WRITE_STORE = "unified"' in code
    assert 'WRITE_STORE = "product"' in code


def test_02_pipeline_write_blocks_include_target_guardrails_and_profile():
    """Each write block retains the explicit target guardrail/write/profile sequence."""
    for index in (1, 2):
        block = _cell_by_id("02_pipeline.ipynb", f"write-{index}").source
        for fragment in (
            "resolve_table_id(",
            "check_schema(WRITE_DATAFRAME,",
            "check_sensitive_data(WRITE_DATAFRAME,",
            "check_source_drift(",
            "check_guardrail_coverage(",
            "pipeline_write(",
            "profile_table(table_id=written_table_id)",
        ):
            assert fragment in block


def test_02_pipeline_read_blocks_are_cloneable_and_explicit():
    """Every source block repeats the explicit governed full-read workflow."""
    for index, read_name in ((1, "orders"), (2, "products"), (3, "history")):
        block = _cell_by_id("02_pipeline.ipynb", f"read-{index}").source
        for fragment in (
            f'READ_NAME = "{read_name}"',
            "source = pipeline_read(",
            'df = source["dataframe"]',
            'table_id = source["table_id"]',
            "check_freshness(",
            "check_schema(df,",
            "check_dq(df,",
            'dq_df = dq_result.get("dataframe", df)',
            'dq_failed_values = dq_result.get("failed_values")',
            "profile_table(table_id=table_id)",
            "sources[READ_NAME] = source",
            "# display(df)",
            '# display(profile_result["profile"])',
            "# display(dq_df)",
            "# display(dq_failed_values)",
        ):
            assert fragment in block
        assert "report_check" not in block
        assert "METADATA_GUARDRAIL_RESULTS" not in block


def test_02_pipeline_transform_is_plain_pyspark():
    """Project transformation remains ordinary readable PySpark and produces two target DataFrames."""
    transform = _cell_by_id("02_pipeline.ipynb", "transform").source
    assert transform.count(".join(") == 2
    assert ".withColumn(" in transform
    assert "transformed_df = (" in transform
    assert "customer_summary_df = (" in transform


def test_02_pipeline_optional_displays_are_commented():
    """Display calls remain opt-in examples rather than runtime defaults."""
    code = _code("02_pipeline.ipynb")
    for line in code.splitlines():
        if "display(" in line:
            assert line.lstrip().startswith("#"), line


def test_99_explore_is_read_only_support_notebook():
    """Explore template stays consumer-oriented and does not expose write functions."""
    code = _code("99_explore.ipynb")
    markdown = _markdown("99_explore.ipynb")
    assert "pipeline_write" not in code
    assert "write_lakehouse_table" not in code
    assert "write_warehouse_table" not in code
    assert "read" in markdown.lower()


def test_notebook_json_is_deterministic_enough_for_source_control():
    """Notebook files stay parseable JSON with no unexpected top-level shape."""
    for path in NOTEBOOK_DIR.glob("*.ipynb"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert "cells" in payload
        assert "metadata" in payload
        assert payload["nbformat"] == 4
