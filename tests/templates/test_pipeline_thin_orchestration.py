from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.contract

ROOT = Path(__file__).parents[2]
PIPELINE_NOTEBOOK = ROOT / "templates" / "notebooks" / "02_pipeline.ipynb"


def _notebook_sources() -> tuple[str, str]:
    notebook = json.loads(PIPELINE_NOTEBOOK.read_text(encoding="utf-8"))
    markdown = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"] if cell.get("cell_type") == "markdown")
    code_cells = ["".join(cell.get("source", [])) for cell in notebook["cells"] if cell.get("cell_type") == "code"]
    for cell in code_cells:
        ast.parse("\n".join(line for line in cell.splitlines() if not line.lstrip().startswith("%")))
    return markdown, "\n".join(code_cells)


def test_pipeline_notebook_uses_existing_public_apis_and_metadata_helpers():
    markdown, code = _notebook_sources()

    for helper in [
        "read_lakehouse_csv",
        "profile_dataframe",
        "validate_schema",
        "monitor_data_changes",
        "enforce_dq_rules",
        "stop_if_failed",
        "write_lakehouse_table",
        "write_catalogue_evidence",
        "write_pipeline_lineage",
        "write_pipeline_run_summary",
    ]:
        assert helper in code
    for removed_wrapper in [
        "read_pipeline_sources",
        "profile_pipeline_datasets",
        "run_schema_guardrails",
        "run_data_drift_guardrails",
        "run_dq_guardrails",
        "add_runtime_audit_columns",
        "write_pipeline_targets",
    ]:
        assert removed_wrapper not in code

    assert "SOURCE_DEFINITIONS" in code
    assert "TARGET_DEFINITIONS" in code
    assert "RUN_ID = RUN_CONTEXT.run_id" in code
    assert "RUN_CONTEXT.runtime_metadata.get" in code
    assert "SETUP." not in code
    assert "LINEAGE_RELATIONSHIPS" in code
    assert "METADATA_PIPELINE_RUNS" in markdown


def test_pipeline_notebook_contains_expected_high_level_flow_sections():
    markdown, _ = _notebook_sources()
    expected_sections = [
        "## 1. Run `00_env_config`",
        "## 2. Import required functions",
        "## 3. Select data agreement and register notebook",
        "## 4. Define and read many source datasets",
        "## 5. Profile each source DataFrame",
        "## 6. Check each source schema",
        "## 7. Check each source for data drift",
        "## 8. Check each source with DQ guardrails",
        "## 9. Write source catalogue evidence",
        "## 10. User-defined transformation section",
        "## 11. Define target DataFrames and add audit columns",
        "## 12. Check each target schema",
        "## 13. Check each target for data drift",
        "## 14. Check each target with DQ guardrails",
        "## 15. Write target catalogue evidence",
        "## 16. Write target tables",
        "## 17. Capture many-to-many lineage",
        "## 18. Write runtime summary",
    ]
    for section in expected_sections:
        assert section in markdown


def test_pipeline_notebook_hides_manual_catalogue_and_lineage_plumbing():
    _, code = _notebook_sources()

    forbidden_visible_plumbing = [
        "lineage_rows = []",
        "for row in lineage_records",
        "json.dumps(payload",
        "withColumn(\"DQ_STATUS\"",
        "withColumn(\"metadata_table_key\"",
        "spark.createDataFrame(lineage_rows)",
    ]
    for snippet in forbidden_visible_plumbing:
        assert snippet not in code

    assert "from fabricops_kit.pipeline import _write_catalogue_evidence" not in code
    assert "_write_catalogue_evidence(" not in code
    assert code.count("write_catalogue_evidence(") == 2
    assert code.count("write_pipeline_lineage(") == 1


def test_pipeline_notebook_supports_many_sources_and_many_targets_by_definition():
    _, code = _notebook_sources()

    assert "for source_name, source_definition in SOURCE_DEFINITIONS.items()" in code
    assert "source_dfs[\"source_alias\"]" in code
    assert code.index("raise ValueError(f\"Unsupported source kind") < code.index("df_minimal_source = source_dfs[\"minimal_source\"]")
    assert "target_dfs = {" in code
    assert code.index("target_profiles = {}") < code.index("for target_name, target_df in target_dfs.items():", code.index("target_profiles = {}")) < code.index("write_catalogue_evidence(\n    target_profiles")
    assert "Add more sources" in code
    assert "Add more targets" in code
    assert "\"sources\": [" in code
    assert "\"targets\": [" in code
