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
    production = _code("02_pipeline.ipynb")
    governance = _code("03_governance.ipynb")

    assert "run_table_guardrails" in production
    assert "guardrail_summary" in production
    assert "stop_if_any_guardrail_failed" in production
    assert "write_lakehouse_table" in production or "write_warehouse_table" in production
    assert "write_pipeline_lineage" in production
    assert "write_pipeline_run_summary" in production
    assert "run_summary" in production
    assert "widget_select_catalogue_table" in governance
    assert "widget_review_column_context" in governance
    assert "widget_review_dq_rules" in governance
    assert "widget_review_column_classification" in governance
    assert "record_table_governance" in governance
    assert "write_governance_review=True" in governance


def test_production_template_enforces_guardrails_before_full_dataset_write():
    production = _code("02_pipeline.ipynb")

    source_guardrails = production.index("source_guardrail_results = run_table_guardrails")
    source_stop = production.index("stop_if_any_guardrail_failed(source_guardrail_results)", source_guardrails)
    transformation = production.index("df_target_01 = df_source_01", source_stop)
    target_guardrails = production.index("target_guardrail_results = run_table_guardrails", transformation)
    target_stop = production.index("stop_if_any_guardrail_failed(target_guardrail_results)", target_guardrails)
    target_write = production.index("target_write_status = {}", target_stop)

    assert source_guardrails < source_stop < transformation < target_guardrails < target_stop < target_write
    assert "valid_rows" not in production
    assert "quarantine_rows" not in production
    assert "failure_rows" not in production
    assert "df_output.filter" not in production
    assert "df_output.where" not in production
    assert "run_table_guardrails" in production


def test_guardrail_orchestration_is_imported_and_documents_simple_v1_behavior():
    production = _code("02_pipeline.ipynb")

    assert "def run_table_guardrails(" not in production
    assert "def _table_key(" not in production
    assert "run_table_guardrails," in production
    assert "guardrail_summary," in production
    assert "display(guardrail_summary(source_guardrail_results))" in production
    assert "display(guardrail_summary(target_guardrail_results))" in production
    assert 'target_dq_results = target_guardrail_results["dq_results"]' in production
    assert "target_write_status = {}" in production
    guardrail_docs = (ROOT / "docs" / "how-fabricops-works" / "schema-and-data-drift.md").read_text(encoding="utf-8")
    assert "Warning-severity failure" in guardrail_docs
    assert "Error-severity failure" in guardrail_docs
    assert "blocks before the next critical step" in guardrail_docs

def test_notebook_template_docs_describe_optional_example_notebooks():
    notebook_docs = (ROOT / "docs" / "how-fabricops-works" / "notebook-templates.md").read_text(
        encoding="utf-8"
    )

    assert "## Optional example notebooks" in notebook_docs
    assert "These notebooks are release-specific validation aids." in notebook_docs
    assert "They are not production workflow templates." in notebook_docs
    assert "| `example_pipeline_smoke_test.ipynb` | Validates the pipeline path: source and target guardrails, catalogue evidence, lineage, runtime summary, and a smoke target write. |" in notebook_docs
    assert "| `example_dq_rule_smoke_test.ipynb` | Demonstrates DQ rule evaluation, warning behavior, and error blocking behavior using smoke-test data and rules. |" in notebook_docs


def test_quick_start_links_template_smoke_tests_with_release_specific_wording():
    quick_start = (ROOT / "docs" / "quick-start.md").read_text(encoding="utf-8")
    expected = (
        "*Optional: After running `00_env_config`, you may run the example smoke test notebooks to quickly "
        "understand how the pipeline and DQ rule flows work before adapting the production templates. "
        "Use [`example_pipeline_smoke_test.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/example_pipeline_smoke_test.ipynb) "
        "to validate the pipeline path, including metadata tables, source and target guardrails, evidence "
        "writing, lineage, runtime summary, and target writes. Use [`example_dq_rule_smoke_test.ipynb`]"
        "(https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/example_dq_rule_smoke_test.ipynb) "
        "to understand how DQ rules are "
        "evaluated, how warning rules behave, and how error rules block when enforcement fails. These "
        "examples are aligned to the current release and should be treated as release-specific validation "
        "aids, not production workflow templates.*"
    )

    assert expected in quick_start
    assert (TEMPLATES / "example_pipeline_smoke_test.ipynb").exists()
    assert (TEMPLATES / "example_dq_rule_smoke_test.ipynb").exists()
    assert not (ROOT / "examples" / "notebooks" / "98_pipeline_smoke_test.ipynb").exists()
    assert not (ROOT / "examples" / "notebooks" / "98_dq_rule_smoke_test.ipynb").exists()


def test_smoke_test_example_notebook_exists_and_covers_end_to_end_pattern():
    smoke_notebook = TEMPLATES / "example_pipeline_smoke_test.ipynb"

    assert smoke_notebook.exists()
    smoke_text = smoke_notebook.read_text(encoding="utf-8")
    smoke = _code_from_notebook(smoke_notebook)

    assert "guardrail orchestration" in smoke_text
    for expected in [
        "spark.createDataFrame",
        "SOURCE_01_CONFIG",
        "TARGET_01_CONFIG",
        "SOURCE_TABLES",
        "TARGET_TABLES",
        "run_table_guardrails",
        "write_pipeline_lineage",
        "write_pipeline_run_summary",
        "PASS: FabricOps pipeline smoke test completed.",
    ]:
        assert expected in smoke

    assert "fabricops_smoke_target" in smoke
    assert "TARGET_01_WRITE_MODE = \"overwrite\"" in smoke
    assert "Metadata evidence tables remain append-only" in smoke_text
    for evidence_helper in [
        "write_pipeline_lineage",
        "write_pipeline_run_summary",
    ]:
        assert evidence_helper in smoke
    assert "mode=\"overwrite\"" not in smoke
    assert "mode = \"overwrite\"" not in smoke
    assert "read_lakehouse_csv" not in smoke
    assert "read_lakehouse_excel" not in smoke
    assert "read_lakehouse_parquet" not in smoke

    dq_smoke = _code_from_notebook(TEMPLATES / "example_dq_rule_smoke_test.ipynb")
    assert "mode=\"overwrite\"" not in dq_smoke
    assert "mode = \"overwrite\"" not in dq_smoke


def test_docs_and_templates_do_not_add_dq_failure_table_behavior():
    checked_paths = [
        ROOT / "docs" / "how-fabricops-works" / "schema-and-data-drift.md",
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
