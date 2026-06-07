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

    assert "validate_schema" in production
    assert "monitor_data_changes" in production
    assert "enforce_dq_rules" in production
    assert "write_lakehouse_table" in production or "write_warehouse_table" in production
    assert "build_lineage_records" in production
    assert "run_summary" in production
    assert "widget_select_catalogue_table" in governance
    assert "widget_review_column_context" in governance
    assert "widget_review_dq_rules" in governance
    assert "widget_review_column_classification" in governance
    assert "record_table_governance" in governance



def test_production_template_enforces_dq_before_full_dataset_write():
    production = _code("02_pipeline.ipynb")

    dq_call = production.index("dq_result = enforce_dq_rules(")
    dq_stop = production.index("stop_if_failed(dq_result)")
    dq_print = production.index("dq_result", dq_call + 1)
    dq_dataframe_assignment = production.index("df_output = dq_result[\"dataframe\"]")
    lakehouse_write = production.index("write_lakehouse_table(df_output")
    warehouse_write = production.index("write_warehouse_table(df_output")

    assert dq_call < dq_print < dq_stop < dq_dataframe_assignment < lakehouse_write
    assert dq_call < dq_stop < dq_dataframe_assignment < warehouse_write
    assert "valid_rows" not in production
    assert "quarantine_rows" not in production
    assert "failure_rows" not in production
    assert "df_output.filter" not in production
    assert "df_output.where" not in production
    assert "dq_summary=dq_result.get(\"summary\")" in production
