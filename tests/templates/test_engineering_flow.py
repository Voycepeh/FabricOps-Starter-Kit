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


def test_explore_template_is_read_only_context_aware_sequence():
    """Verify 99_explore follows read-only context-aware exploration flow."""
    notebook = json.loads((TEMPLATES / "99_explore.ipynb").read_text(encoding="utf-8"))
    markdown = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"] if cell.get("cell_type") == "markdown")
    code = _code("99_explore.ipynb")

    expected_sections = [
        "## 01 Configure environment",
        "## 02 Import functions",
        "## 03 Select agreement",
        "## 04 Read source",
        "## 05 Fetch latest metadata catalogue",
        "## 06 Optional profile, no write",
        "## 07 Self exploration",
    ]
    positions = [markdown.index(section) for section in expected_sections]
    assert positions == sorted(positions)

    assert "01_agreement` → `02_pipeline` → `03_governance" in markdown
    assert "read-only" in markdown
    assert "does **not** approve" in markdown
    assert "%run 00_env_config" in code
    assert "AGREEMENT_CONTEXT = widget_select_agreement(" in code
    assert "select_agreement=True" not in code
    assert "register_notebook=False" in code
    assert "read_only=True" in code
    assert 'notebook_type="99_explore"' in code
    assert "AGREEMENT = AGREEMENT_CONTEXT.agreement" in code
    assert "get_latest_metadata_catalogue(" in code
    assert "latest_catalogue" in code
    assert "RUN_PROFILE = True" in code
    assert "profile_dataframe(" in code
    assert "display(source_df.limit(100))" in code

    forbidden = [
        "write_data(",
        "write_lakehouse_table(",
        "write_pipeline_run_summary(",
        "run_table_guardrails(",
        "_run_active_dq_guardrail(",
        "widget_review_guardrail_governance(",
        "widget_enrich_table_metadata(",
        "register_notebook=True",
        "run_parallel(",
        "dataset_name =",
        "topic =",
    ]
    for item in forbidden:
        assert item not in code


def test_dq_rule_smoke_test_uses_supported_guardrail_path():
    """Verify DQ smoke-test notebook no longer uses stale public DQ helper."""
    code = _code("example_dq_rule_smoke_test.ipynb")

    assert "run_table_guardrails(" in code
    stale_helper = "enforce" + "_dq_rules"
    assert stale_helper not in code
