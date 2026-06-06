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


def test_production_and_governance_templates_cover_output_handover_and_review_flows():
    production = _code("03_pc_agreement_pipeline_template.ipynb")
    governance = _code("04_gov_dataset_table.ipynb")

    assert "validate_schema" in production
    assert "monitor_data_changes" in production
    assert "write_lakehouse_table" in production or "write_warehouse_table" in production
    assert "build_lineage_records" in production
    assert "run_summary" in production
    assert "widget_select_catalogue_table" in governance
    assert "widget_review_table_governance" in governance
    assert "record_table_governance" in governance
    assert "record_table_governance" in governance
    assert "record_table_governance" in governance
