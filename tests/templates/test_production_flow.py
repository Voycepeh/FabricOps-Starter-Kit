from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.contract

TEMPLATES = Path(__file__).parents[2] / "templates" / "notebooks"


def _code(path: str) -> str:
    notebook = json.loads((TEMPLATES / path).read_text(encoding="utf-8"))
    cells = ["".join(cell.get("source", [])) for cell in notebook["cells"] if cell.get("cell_type") == "code"]
    for cell in cells:
        ast.parse("\n".join(line for line in cell.splitlines() if not line.lstrip().startswith("%")))
    return "\n".join(cells)


def test_production_and_governance_templates_cover_output_summary_and_review_flows():
    production = _code("02_pipeline.ipynb")
    governance = _code("03_review.ipynb")

    assert "run_schema_guardrails" in production
    assert "run_data_drift_guardrails" in production
    assert "run_dq_guardrails" in production
    assert "write_pipeline_targets" in production
    assert "write_pipeline_lineage" in production
    assert "write_pipeline_run_summary" in production
    assert "run_summary" in production
    assert "widget_select_catalogue_table" in governance
    assert "widget_review_column_context" in governance
    assert "widget_review_dq_rules" in governance
    assert "widget_review_column_classification" in governance
    assert "record_table_governance" in governance


def test_production_template_enforces_dq_before_full_dataset_write():
    production = _code("02_pipeline.ipynb")

    source_dq_call = production.index("source_dq_results = run_dq_guardrails(")
    target_dq_call = production.index("target_dq_results = run_dq_guardrails(")
    target_dq_stop = production.index("stop_if_failed(result)", target_dq_call)
    target_dataframe_assignment = production.index('target_dfs[target_name] = result["dataframe"]')
    target_write = production.index("target_write_status = write_pipeline_targets(")

    assert source_dq_call < target_dq_call < target_dq_stop < target_dataframe_assignment < target_write
    assert "valid_rows" not in production
    assert "quarantine_rows" not in production
    assert "failure_rows" not in production
    assert "df_output.filter" not in production
    assert "df_output.where" not in production
    assert "dq_results=target_dq_results" in production


def test_dq_section_prints_result_and_documents_simple_v1_behavior():
    production = _code("02_pipeline.ipynb")

    dq_call = production.index("target_dq_results = run_dq_guardrails(")
    dq_print = production.index("print(result)", dq_call)
    dq_stop = production.index("stop_if_failed(result)", dq_call)

    assert dq_call < dq_print < dq_stop
    assert "Warning severity writes full data" in production
    assert "error severity stops before write" in production
    assert "No row filtering in v1." in production


def test_docs_and_templates_do_not_add_dq_failure_table_behavior():
    root = Path(__file__).parents[2]
    checked_paths = [
        root / "docs" / "how-fabricops-works" / "schema-and-data-drift.md",
        root / "docs" / "how-fabricops-works" / "governance-review.md",
        root / "docs" / "how-fabricops-works" / "notebook-templates.md",
        root / "docs" / "how-fabricops-works" / "metadata-tables.md",
        root / "docs" / "quick-start.md",
        root / "templates" / "notebooks" / "02_pipeline.ipynb",
        root / "templates" / "notebooks" / "03_review.ipynb",
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
                offenders.append(f"{path.relative_to(root)} contains {needle}")

    assert offenders == []
