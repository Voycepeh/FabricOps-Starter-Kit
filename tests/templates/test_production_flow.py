"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.contract

ROOT = Path(__file__).parents[2]
TEMPLATES = ROOT / "templates" / "notebooks"


def _code_from_notebook(path: Path) -> str:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    cells = ["".join(cell.get("source", [])) for cell in notebook["cells"] if cell.get("cell_type") == "code"]
    for cell in cells:
        ast.parse("\n".join(line for line in cell.splitlines() if not line.lstrip().startswith("%")))
    return "\n".join(cells)


def _code(path: str) -> str:
    return _code_from_notebook(TEMPLATES / path)


def test_production_and_governance_templates_cover_output_summary_and_review_flows():
    """Verify production and governance templates cover output summary and review flows."""
    production = _code("02_pipeline.ipynb")
    governance = _code("03_governance.ipynb")

    assert "run_table_guardrails" in production
    assert "prepare_pipeline_table_configs" in production
    assert "write_lakehouse_table" in production
    assert "write_warehouse_table" in production
    assert "write_pipeline_lineage" in production
    assert "write_pipeline_run_summary" in production
    assert "run_summary" in production
    assert "widget_select_governance_profile_target" in governance
    assert "widget_select_catalogue_table" not in governance
    assert "widget_review_column_context" in governance
    assert "widget_review_dq_rules" in governance
    assert "widget_review_column_classification" in governance
    assert "record_table_governance" in governance
    assert "write_governance_review=True" in governance


def test_production_template_enforces_guardrails_before_full_dataset_write():
    """Verify production template enforces guardrails before full dataset write."""
    production = _code("02_pipeline.ipynb")

    source_guardrails = production.index("source_guardrail_results = run_table_guardrails")
    source_stop_flag = production.index("stop_on_failure=False", source_guardrails)
    source_display = production.index("display(source_guardrail_display)", source_stop_flag)
    source_stop = production.index("stop_if_failed({", source_display)
    transformation = production.index("df_orders_enriched = (", source_stop)
    target_guardrails = production.index("target_guardrail_results = run_table_guardrails", transformation)
    target_stop_flag = production.index("stop_on_failure=False", target_guardrails)
    target_display = production.index("display(target_guardrail_display)", target_stop_flag)
    target_stop = production.index("stop_if_failed({", target_display)
    target_write = production.index("target_write_status = {}", target_stop)

    assert source_guardrails < source_stop_flag < source_display < source_stop < transformation
    assert target_guardrails < target_stop_flag < target_display < target_stop < target_write
    assert "valid_rows" not in production
    assert "quarantine_rows" not in production
    assert "failure_rows" not in production
    assert "df_output.filter" not in production
    assert "df_output.where" not in production
    assert "run_table_guardrails" in production


def test_guardrail_orchestration_is_imported_and_documents_simple_v1_behavior():
    """Verify guardrail orchestration is imported and documents simple v1 behavior."""
    production = _code("02_pipeline.ipynb")

    assert "def run_table_guardrails(" not in production
    assert "def _table_key(" not in production
    assert "run_table_guardrails," in production
    assert "prepare_pipeline_table_configs," in production
    assert "read_lakehouse_table," in production
    assert "read_lakehouse_csv," in production
    assert "read_lakehouse_parquet," in production
    assert "read_lakehouse_excel," in production
    assert "read_warehouse_table," in production
    assert "source_guardrail_display = display_guardrail_results(" in production
    assert "display(source_guardrail_display)" in production
    assert "target_guardrail_display = display_guardrail_results(" in production
    assert "display(target_guardrail_display)" in production
    assert 'target_dq_results = target_guardrail_results["dq_results"]' in production
    assert "target_write_status = {}" in production
    assert "_load_source_dataframe" not in production
    assert "_read_source_dataframe" not in production
    assert "read_type" not in production
    guardrail_docs = (ROOT / "docs" / "how-fabricops-works" / "pipeline-guardrails.md").read_text(encoding="utf-8")
    assert "Warning-severity failure" in guardrail_docs
    assert "Error-severity failure" in guardrail_docs
    assert "blocks before the next critical step" in guardrail_docs

def test_notebook_template_docs_describe_optional_example_notebooks():
    """Verify notebook template docs describe optional example notebooks."""
    notebook_docs = (ROOT / "docs" / "how-fabricops-works" / "notebook-templates.md").read_text(
        encoding="utf-8"
    )

    assert "## Optional example notebooks" in notebook_docs
    assert "These notebooks are release-specific validation aids." in notebook_docs
    assert "They are not production workflow templates." in notebook_docs
    assert "| `example_pipeline_smoke_test.ipynb` | Generates deterministic `smoke_` source scenario tables for the real `02_pipeline` template to demonstrate happy path, schema, DQ, freshness, and load-behaviour guardrails. |" in notebook_docs
    assert "| `example_dq_rule_smoke_test.ipynb` | Demonstrates DQ rule evaluation, warning behavior, and error blocking behavior using smoke-test data and rules. |" in notebook_docs


def test_quick_start_links_optional_pipeline_guardrail_demo():
    """Verify quick start links optional pipeline guardrail demo."""
    quick_start = (ROOT / "docs" / "quick-start.md").read_text(encoding="utf-8")

    for expected in [
        "## Optional: run the pipeline guardrail demo",
        "not part of the mandatory first-run setup",
        "example_pipeline_smoke_test.ipynb",
        "source_lakehouse",
        "02_pipeline",
        "unified_lakehouse",
        "example_pipeline_smoke_test.ipynb` only generates scenario data",
        "example_dq_rule_smoke_test.ipynb",
    ]:
        assert expected in quick_start

    for scenario_table in [
        "smoke_src_orders_happy",
        "smoke_src_orders_schema_drift",
        "smoke_src_orders_dq_issue",
        "smoke_src_orders_stale",
        "smoke_src_orders_reload_a",
        "smoke_src_orders_reload_b",
    ]:
        assert scenario_table in quick_start

    assert (TEMPLATES / "example_pipeline_smoke_test.ipynb").exists()
    assert (TEMPLATES / "example_dq_rule_smoke_test.ipynb").exists()
    assert not (ROOT / "examples" / "notebooks" / "98_pipeline_smoke_test.ipynb").exists()
    assert not (ROOT / "examples" / "notebooks" / "98_dq_rule_smoke_test.ipynb").exists()


def test_smoke_test_example_notebook_exists_and_generates_pipeline_scenarios():
    """Verify smoke test example notebook exists and generates pipeline scenarios."""
    smoke_notebook = TEMPLATES / "example_pipeline_smoke_test.ipynb"

    assert smoke_notebook.exists()
    smoke_text = smoke_notebook.read_text(encoding="utf-8")
    smoke = _code_from_notebook(smoke_notebook)

    for expected_text in [
        "source scenario generator",
        "02_pipeline",
        "smoke_src_orders_happy",
        "smoke_src_customers_happy",
        "smoke_src_orders_schema_drift",
        "smoke_src_orders_dq_issue",
        "smoke_src_orders_stale",
        "smoke_src_orders_reload_a",
        "smoke_src_orders_reload_b",
    ]:
        assert expected_text in smoke_text

    for scenario_table in [
        "smoke_src_orders_happy",
        "smoke_src_customers_happy",
        "smoke_src_orders_schema_drift",
        "smoke_src_orders_dq_issue",
        "smoke_src_orders_stale",
        "smoke_src_orders_reload_a",
        "smoke_src_orders_reload_b",
    ]:
        assert scenario_table in smoke

    assert "spark.createDataFrame" in smoke
    assert "write_lakehouse_table" in smoke
    assert '"source",' in smoke
    assert "METADATA_GUARDRAIL_RULES" in smoke
    for guardrail_field in [
        "guardrail_type",
        "author_role",
        "created_by",
        "created_at",
        "source_notebook_type",
        "source_notebook_id",
        "source_workspace_id",
        "superseded_by_rule_key",
        "notes",
    ]:
        assert guardrail_field in smoke
    assert "scenario_catalogue_df" in smoke
    assert "Refusing to write non-smoke table" in smoke

    for orchestration_concern in [
        "SOURCE_TABLES",
        "TARGET_TABLES",
        "run_table_guardrails",
        "prepare_pipeline_table_configs",
        "write_warehouse_table",
        "write_pipeline_lineage",
        "write_pipeline_run_summary",
        "PASS: FabricOps pipeline smoke test completed.",
        "def run_table_guardrails(",
        "prepare_source_table_configs",
        "prepare_target_table_configs",
        "write_target_tables",
    ]:
        assert orchestration_concern not in smoke

    dq_smoke = _code_from_notebook(TEMPLATES / "example_dq_rule_smoke_test.ipynb")
    assert "METADATA_GUARDRAIL_RULES" in dq_smoke
    for guardrail_field in [
        "guardrail_type",
        "author_role",
        "created_by",
        "created_at",
        "source_notebook_type",
        "source_notebook_id",
        "source_workspace_id",
        "superseded_by_rule_key",
        "notes",
    ]:
        assert guardrail_field in dq_smoke
    assert "mode=\"overwrite\"" not in dq_smoke
    assert "mode = \"overwrite\"" not in dq_smoke


def test_docs_and_templates_do_not_add_dq_failure_table_behavior():
    """Verify docs and templates do not add dq failure table behavior."""
    checked_paths = [
        ROOT / "docs" / "how-fabricops-works" / "pipeline-guardrails.md",
        ROOT / "docs" / "how-fabricops-works" / "governance-review.md",
        ROOT / "docs" / "how-fabricops-works" / "notebook-templates.md",
        ROOT / "docs" / "how-fabricops-works" / "metadata-tables.md",
        ROOT / "docs" / "quick-start.md",
        ROOT / "templates" / "notebooks" / "02_pipeline.ipynb",
        ROOT / "templates" / "notebooks" / "03_governance.ipynb",
        ROOT / "templates" / "notebooks" / "example_pipeline_smoke_test.ipynb",
        ROOT / "templates" / "notebooks" / "example_dq_rule_smoke_test.ipynb",
    ]
    forbidden = [
        "METADATA_DQ_FAILURE",
        "METADATA_DQ_FAILURES",
        "DQ failure metadata table",
        "DQ failure metadata tables",
        "row-level failure table",
        "row-level failure tables",
        "quarantine table",
        "quarantine tables",
        "quarantine_rows",
        "failure_rows",
        "valid_rows",
    ]
    offenders = []
    for path in checked_paths:
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for needle in forbidden:
            if needle.lower() in lowered:
                offenders.append(f"{path.relative_to(ROOT)} contains {needle}")

    assert offenders == []


def test_example_pipeline_smoke_test_uses_shared_lakehouse_write_helper_without_unidentified_paths():
    """Verify example pipeline smoke test uses shared lakehouse write helper without unidentified paths."""
    import json
    from pathlib import Path

    notebook = json.loads(Path("templates/notebooks/example_pipeline_smoke_test.ipynb").read_text(encoding="utf-8"))
    code = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"] if cell.get("cell_type") == "code")

    assert "write_lakehouse_table(" in code
    assert "Unidentified" not in code
    assert "/Tables/" not in code
    assert 'schema="dbo"' not in code
