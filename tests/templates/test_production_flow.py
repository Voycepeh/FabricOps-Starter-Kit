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
        "write_data",
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
    assert "read_data," in production
    assert "read_lakehouse_table," not in production
    assert "read_lakehouse_csv," not in production
    assert "read_lakehouse_parquet," not in production
    assert "read_lakehouse_excel," not in production
    assert "read_warehouse_table," not in production
    assert "display_guardrail_results(source_enforcement_results" in production
    assert "display_guardrail_results(target_enforcement_results" in production
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

    for expected in [
        "## `example_pipeline_demo`",
        "## `example_dq_rule_smoke_test`",
        "No. Demo helper only.",
        "No. Validation helper only.",
        "Generates deterministic demo source tables for the guided demo.",
        "Demonstrates DQ rule evaluation, warning behavior, and blocking behavior in a smoke-test context.",
        "It is not a production delivery notebook.",
        "No production notebook depends on this smoke test.",
    ]:
        assert expected in notebook_docs


def test_guided_demo_links_pipeline_guardrail_demo():
    """Verify guided demo links the step pages for the pipeline guardrail demo."""
    guided_demo = (ROOT / "docs" / "guided-demo.md").read_text(encoding="utf-8")
    create_wheel_page = (ROOT / "docs" / "guided-demo" / "create-wheel.md").read_text(
        encoding="utf-8"
    )
    workspace_page = (ROOT / "docs" / "guided-demo" / "create-fabric-workspace.md").read_text(
        encoding="utf-8"
    )
    lakehouse_page = (ROOT / "docs" / "guided-demo" / "create-lakehouses-warehouse.md").read_text(
        encoding="utf-8"
    )
    env_setup_page = (ROOT / "docs" / "guided-demo" / "run-environment-setup.md").read_text(
        encoding="utf-8"
    )

    for expected in [
        "# FabricOps Guided Demo",
        "## Run sequence",
        "[Create Wheel](guided-demo/create-wheel.md)",
        "[Create Fabric Workspace](guided-demo/create-fabric-workspace.md)",
        "[Create Lakehouses / Warehouse](guided-demo/create-lakehouses-warehouse.md)",
        "[Configure Environment](guided-demo/configure-environment.md)",
        "[Run Environment Setup](guided-demo/run-environment-setup.md)",
        "[Create Agreement](guided-demo/create-agreement.md)",
        "[Run Pipeline](guided-demo/run-pipeline.md)",
        "[Enrich Metadata](guided-demo/enrich-metadata.md)",
        "[Review Guardrails](guided-demo/review-guardrails.md)",
        "[Explore Metadata Outputs](guided-demo/explore-metadata-outputs.md)",
        "METADATA_GUARDRAIL_RULES",
    ]:
        assert expected in guided_demo

    assert "Milestone" not in guided_demo
    assert "milestone" not in guided_demo

    for expected in [
        "# Create Wheel",
        "../setup/create-wheel.md",
        "FabricOps `.whl` file",
    ]:
        assert expected in create_wheel_page

    for expected in [
        "# Create Fabric Workspace",
        "wheel created in [Create Wheel](create-wheel.md)",
        "00_env_config",
        "01_agreement",
        "02_pipeline",
        "03_governance",
        "example_pipeline_demo",
        "99_explore",
    ]:
        assert expected in workspace_page

    for expected in [
        "# Create Lakehouses / Warehouse",
        "metadata_lakehouse",
        "source_lakehouse",
        "unified_lakehouse",
        "product_warehouse",
    ]:
        assert expected in lakehouse_page

    for expected in [
        "# Run Environment Setup",
        "CONFIG",
        "ENV",
        "METADATA_*",
    ]:
        assert expected in env_setup_page

    assert (TEMPLATES / "example_pipeline_demo.ipynb").exists()
    assert (TEMPLATES / "example_dq_rule_smoke_test.ipynb").exists()
    assert not (ROOT / "examples" / "notebooks" / "98_pipeline_demo.ipynb").exists()
    assert not (ROOT / "examples" / "notebooks" / "98_dq_rule_smoke_test.ipynb").exists()


def test_pipeline_demo_example_notebook_exists_and_generates_pipeline_scenarios():
    """Verify pipeline demo example notebook exists and generates pipeline scenarios."""
    demo_notebook = TEMPLATES / "example_pipeline_demo.ipynb"

    assert demo_notebook.exists()
    demo_text = demo_notebook.read_text(encoding="utf-8")
    demo = _code_from_notebook(demo_notebook)

    for expected_text in [
        "source scenario generator",
        "02_pipeline",
        "demo_src_orders_happy",
        "demo_src_customers_happy",
        "demo_src_orders_schema_drift",
        "demo_src_orders_dq_issue",
        "demo_src_orders_stale",
        "demo_src_orders_reload_a",
        "demo_src_orders_reload_b",
    ]:
        assert expected_text in demo_text

    for scenario_table in [
        "demo_src_orders_happy",
        "demo_src_customers_happy",
        "demo_src_orders_schema_drift",
        "demo_src_orders_dq_issue",
        "demo_src_orders_stale",
        "demo_src_orders_reload_a",
        "demo_src_orders_reload_b",
    ]:
        assert scenario_table in demo

    assert "spark.createDataFrame" in demo
    assert "write_data" in demo
    assert '"source",' in demo
    assert "METADATA_GUARDRAIL_RULES" in demo
    for implemented_rule in ["not_null", "accepted_values", "between", "max_age_days", "required_when"]:
        assert f'"rule_type": "{implemented_rule}"' in demo
    assert '"rule_type": "unique"' not in demo
    assert '"rule_type": "greater_than_or_equal"' not in demo
    assert "notebookutils.widgets.text" in demo
    assert "SOURCE_SCHEMA" in demo
    assert "UNIFIED_TARGET_PREFIX" in demo
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
        assert guardrail_field in demo
    assert "scenario_catalogue_df" in demo
    assert "Refusing to write non-demo table" in demo

    for orchestration_concern in [
        "SOURCE_TABLES",
        "TARGET_TABLES",
        "run_table_guardrails",
        "prepare_pipeline_table_configs",
        "write_warehouse_table",
        "write_pipeline_lineage",
        "write_pipeline_run_summary",
        "PASS: FabricOps pipeline demo completed.",
        "def run_table_guardrails(",
        "prepare_source_table_configs",
        "prepare_target_table_configs",
        "write_target_tables",
    ]:
        assert orchestration_concern not in demo

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
        ROOT / "docs" / "guided-demo.md",
        ROOT / "templates" / "notebooks" / "02_pipeline.ipynb",
        ROOT / "templates" / "notebooks" / "03_governance.ipynb",
        ROOT / "templates" / "notebooks" / "example_pipeline_demo.ipynb",
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


def test_example_pipeline_demo_uses_shared_lakehouse_write_helper_without_unidentified_paths():
    """Verify example pipeline demo uses shared lakehouse write helper without unidentified paths."""
    notebook = json.loads(Path("templates/notebooks/example_pipeline_demo.ipynb").read_text(encoding="utf-8"))
    code = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"] if cell.get("cell_type") == "code")

    assert "write_data(" in code
    assert "Unidentified" not in code
    assert "/Tables/" not in code
    assert 'schema="dbo"' not in code
