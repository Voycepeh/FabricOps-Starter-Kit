"""Contract tests for production notebook template behavior."""

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


def _calls_by_name(code: str) -> dict[str, list[ast.Call]]:
    tree = ast.parse("\n".join(line for line in code.splitlines() if not line.lstrip().startswith("%")))
    calls: dict[str, list[ast.Call]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            calls.setdefault(node.func.id, []).append(node)
    return calls


def test_production_and_governance_templates_cover_output_summary_and_review_flows():
    """Verify production and governance templates cover output summary and review flows."""
    production = _code("02_pipeline.ipynb")
    governance = _code("03_governance.ipynb")

    for expected in [
        "run_table_guardrails",
        "prepare_pipeline_table_configs",
        "write_lakehouse_table",
        "write_pipeline_lineage",
        "write_pipeline_run_summary",
        "runtime_summary_result",
        "widget_author_schema_freshness_profile_rules",
        "widget_author_dq_rules",
        "widget_enrich_table_metadata",
        "widget_review_guardrail_governance",
    ]:
        assert expected in production
    assert "widget_select_guardrail_target" in governance
    assert "widget_enrich_table_metadata" in governance
    assert governance.index("widget_select_guardrail_target") < governance.index("widget_enrich_table_metadata") < governance.index("widget_review_guardrail_governance")
    assert "widget_select_governance_" + "profile_target" not in governance
    assert "widget_review_" + "dq_rules" not in governance


def test_governance_template_uses_widget_signatures_and_governance_authoring_stamp():
    """Verify 03_governance uses public widget signatures and governance authorship stamps."""
    governance = _code("03_governance.ipynb")
    calls = _calls_by_name(governance)
    context_only_widgets = [
        "widget_select_guardrail_target",
        "widget_enrich_table_metadata",
        "widget_author_schema_freshness_profile_rules",
        "widget_author_dq_rules",
        "widget_review_guardrail_governance",
    ]

    for widget_name in context_only_widgets:
        assert widget_name in calls
        for call in calls[widget_name]:
            keyword_names = {keyword.arg for keyword in call.keywords}
            assert "config" not in keyword_names
            assert "env" not in keyword_names

    for widget_name in [
        "widget_author_schema_freshness_profile_rules",
        "widget_author_dq_rules",
    ]:
        keyword_values = {
            keyword.arg: ast.literal_eval(keyword.value)
            for keyword in calls[widget_name][0].keywords
            if keyword.arg in {"source_notebook_type", "created_by_role"}
        }
        assert keyword_values == {
            "source_notebook_type": "03_governance",
            "created_by_role": "governance",
        }


def test_production_template_enforces_guardrails_before_full_dataset_write():
    """Verify production template enforces guardrails before full dataset write."""
    production = _code("02_pipeline.ipynb")

    source_profile = production.index("source_profile_results = run_table_guardrails")
    transformation = production.index("df_orders_enriched = (", source_profile)
    target_profile = production.index("target_profile_results = run_table_guardrails", transformation)
    widget_curation = production.index("selected_guardrail_target = widget_select_guardrail_target", target_profile)
    source_enforcement = production.index("source_enforcement_results = run_table_guardrails", widget_curation)
    target_enforcement = production.index("target_enforcement_results = run_table_guardrails", source_enforcement)
    write_settings = production.index("TARGET_WRITE_SETTINGS = {", target_enforcement)
    target_write = production.index("target_write_status = {}", write_settings)

    assert source_profile < transformation < target_profile < widget_curation < source_enforcement
    assert source_enforcement < target_enforcement < write_settings < target_write
    assert "valid_rows" not in production
    assert "quarantine_rows" not in production
    assert "failure_rows" not in production
    assert "df_output.filter" not in production
    assert "df_output.where" not in production


def test_guardrail_orchestration_is_imported_and_documents_simple_v1_behavior():
    """Verify guardrail orchestration uses package helpers and no local implementation."""
    production = _code("02_pipeline.ipynb")

    assert "def run_table_guardrails(" not in production
    assert "def _table_key(" not in production
    assert "run_table_guardrails," in production
    assert "prepare_pipeline_table_configs," in production
    assert "read_lakehouse_table," in production
    assert "read_lakehouse_csv," in production
    assert "read_lakehouse_parquet," in production
    assert "read_lakehouse_excel," in production
    assert "read_warehouse_query," in production
    assert "display_guardrail_results(source_enforcement_results" in production
    assert "display_guardrail_results(target_enforcement_results" in production
    assert "target_write_status = {}" in production
    assert "_load_source_dataframe" not in production
    assert "_read_source_dataframe" not in production
    assert "read_type" not in production
    guardrail_docs = (ROOT / "docs" / "guided-demo" / "run-pipeline.md").read_text(encoding="utf-8")
    assert "Warning-severity failure" in guardrail_docs
    assert "Error-severity failure" in guardrail_docs
    assert "blocks before the next critical step" in guardrail_docs


def test_notebook_template_docs_describe_optional_example_notebooks():
    """Verify notebook template docs describe optional example notebooks."""
    notebook_docs = (ROOT / "docs" / "notebook-templates-implementation-guide" / "index.md").read_text(
        encoding="utf-8"
    )

    for expected in [
        "template-card",
        "Download all template notebooks from this GitHub folder",
        "## [`example_pipeline_demo`]",
        "## [`example_dq`]",
        "Generates deterministic demo source tables and demo-scoped rule intent for the Guided Demo pipeline run.",
        "Demonstrates supported DQ rule outcomes in a smoke-test context",
        "It is not a production delivery notebook.",
            ]:
        assert expected in notebook_docs


def test_guided_demo_links_pipeline_guardrail_demo():
    """Verify guided demo links the step pages for the pipeline guardrail demo."""
    guided_demo = (ROOT / "docs" / "guided-demo.md").read_text(encoding="utf-8")
    setup_page = (ROOT / "docs" / "guided-demo" / "setup-fabric-artifacts.md").read_text(
        encoding="utf-8"
    )
    env_setup_page = (ROOT / "docs" / "guided-demo" / "run-environment-setup.md").read_text(
        encoding="utf-8"
    )

    for expected in [
        "# FabricOps Guided Demo",
        "## Run sequence",
        "METADATA_GUARDRAIL_RULES",
    ]:
        assert expected in guided_demo

    for expected_link in [
        "(guided-demo/setup-fabric-artifacts.md)",
        "(guided-demo/run-environment-setup.md)",
        "(guided-demo/create-agreement.md)",
        "(guided-demo/run-pipeline.md)",
        "(guided-demo/review-guardrails.md)",
        "(guided-demo/explore-metadata-outputs.md)",
    ]:
        assert expected_link in guided_demo

    for expected_label in [
        "[Register Agreement](guided-demo/create-agreement.md)",
        "[Run Example Pipeline Demo](guided-demo/run-pipeline.md)",
        "[Run Pipeline](guided-demo/run-pipeline.md)",
        "[Review Governance](guided-demo/review-guardrails.md)",
        "[Explore Metadata](guided-demo/explore-metadata-outputs.md)",
    ]:
        assert expected_label in guided_demo

    assert "Milestone" not in guided_demo
    assert "milestone" not in guided_demo

    for expected in [
        "# Setup Fabric Artifacts",
        "metadata_lakehouse",
        "source_lakehouse",
        "unified_lakehouse",
        "product_warehouse",
        "00_env_config",
        "01_agreement",
        "02_pipeline",
        "03_governance",
        "example_pipeline_demo",
        "99_explore",
        "published FabricOps release wheel",
        "Release Guide",
    ]:
        assert expected in setup_page

    for expected in [
        "# Run Environment Setup",
        "00_env_config",
        "metadata tables",
    ]:
        assert expected in env_setup_page
