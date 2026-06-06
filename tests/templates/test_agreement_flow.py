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
    agreement_cells = "\n".join(_code_cells(TEMPLATES / "01_da_agreement_template.ipynb"))

    for cell in _code_cells(TEMPLATES / "00_env_config.ipynb") + _code_cells(TEMPLATES / "01_da_agreement_template.ipynb"):
        ast.parse(_python_cell(cell))
    assert "CONFIG" in env_cells
    assert "setup_data_agreement_tables" in env_cells
    assert "widget_render_agreement_intake_app" in agreement_cells
    assert "widget_render_agreement_evidence" in agreement_cells
