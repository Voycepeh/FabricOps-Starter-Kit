"""Test FabricOps behavior and reference contracts."""

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


def test_engineering_template_runs_supported_ingestion_quality_and_metadata_flow():
    """Verify engineering template runs supported ingestion quality and metadata flow."""
    code = _code("99_explore.ipynb")

    assert "%run 00_env_config" in code
    assert "widget_select_" + "agreement" not in code
    assert any(reader in code for reader in ("read_lakehouse_table", "read_lakehouse_csv", "read_lakehouse_parquet", "read_lakehouse_excel"))
    assert "profile_dataframe" in code
    assert ".show(" in code
