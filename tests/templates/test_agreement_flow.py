from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.contract

TEMPLATES = Path(__file__).parents[2] / "templates" / "notebooks"


def _code_cells(path: Path) -> list[str]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    return ["".join(cell.get("source", [])) for cell in notebook["cells"] if cell.get("cell_type") == "code"]


def _python_cell(cell: str) -> str:
    return "\n".join(line for line in cell.splitlines() if not line.lstrip().startswith("%"))


def test_environment_and_agreement_templates_have_executable_public_workflow_cells():
    env_cells = "\n".join(_code_cells(TEMPLATES / "00_env_config.ipynb"))
    agreement_cells = "\n".join(_code_cells(TEMPLATES / "01_agreement.ipynb"))

    for cell in _code_cells(TEMPLATES / "00_env_config.ipynb") + _code_cells(TEMPLATES / "01_agreement.ipynb"):
        ast.parse(_python_cell(cell))
    assert "CONFIG" in env_cells
    assert "setup_metadata_tables" in env_cells
    assert "RUN_CONTEXT = setup_notebook" in env_cells
    assert "check_naming_convention" not in env_cells
    assert 'AGREEMENT_METADATA_SETUP = METADATA_TABLE_SETUP["data_agreement"]' in env_cells
    assert "widget_render_data_steward" in agreement_cells
    assert "widget_render_data_agreement" in agreement_cells
    assert "widget_render_agreement_evidence" in agreement_cells


def test_template_notebook_filenames_follow_v1_delivery_order():
    expected = [
        "00_env_config.ipynb",
        "01_agreement.ipynb",
        "02_pipeline.ipynb",
        "03_governance.ipynb",
        "99_explore.ipynb",
        "example_dq_rule_smoke_test.ipynb",
        "example_pipeline_smoke_test.ipynb",
    ]

    assert sorted(path.name for path in TEMPLATES.glob("*.ipynb")) == expected


def test_templates_do_not_reintroduce_old_numbered_stage_references():
    stale_terms = ("01" + "_da", "02" + "_ex", "03" + "_pc", "04" + "_gov", "03" + "_pipeline", "02" + "_explore")
    combined = "\n".join(path.read_text(encoding="utf-8") for path in TEMPLATES.glob("*.ipynb"))

    assert not any(term in combined for term in stale_terms)
