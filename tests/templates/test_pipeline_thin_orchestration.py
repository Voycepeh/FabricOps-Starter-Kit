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
        "enforce_catalogue_stability",
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
        "run_source_stability_guardrails",
        "run_dq_guardrails",
        "add_runtime_audit_columns",
        "write_pipeline_targets",
    ]:
        assert removed_wrapper not in code

    assert "SOURCE_DEFINITIONS" not in code
    assert "SOURCE_DATASETS" not in code
    assert "TARGET_DEFINITIONS" not in code
    assert "TARGET_DATASETS" not in code
    assert "USE_SAMPLE_DATA" not in code
    assert "sample_agreement_dataset" not in code
    assert "Files/sample/minimal_source.csv" not in code
    assert "SOURCE_TABLES" in code
    assert "TARGET_TABLES" in code
    assert 'table_config["df"]' in code
    assert 'target_config["df"]' in code
    assert "RUN_ID = RUN_CONTEXT.run_id" in code
    assert "RUN_CONTEXT.runtime_metadata.get" in code
    assert "SETUP." not in code
    assert "LINEAGE_RELATIONSHIPS" in code
    assert "METADATA_PIPELINE_RUNS" in markdown
    assert "imports existing FabricOps callables directly for reads, profiling, guardrails, writes" in markdown
    assert "FabricOps then orchestrates profiling, schema validation, stability enforcement, DQ enforcement" in markdown


def test_pipeline_notebook_contains_expected_config_driven_flow_sections():
    markdown, _ = _notebook_sources()
    expected_sections = [
        "## 1. Run `00_env_config`",
        "## 2. Import required functions",
        "## 3. Select data agreement and capture run context",
        "## 4. Source DataFrame/config blocks",
        "## 5. Collect source configs",
        "## 6. Define reusable guardrail orchestration helpers",
        "## 7. Run source guardrails before transformation",
        "## 8. Transform to target DataFrames",
        "## 9. Target DataFrame/config blocks",
        "## 10. Collect target configs",
        "## 11. Run target guardrails before writes",
        "## 12. Write target tables",
        "## 13. Capture many-to-many lineage",
        "## 14. Write runtime summary",
    ]
    for section in expected_sections:
        assert section in markdown

    assert "Users clone only DataFrame/config blocks" in markdown
    assert "Schema, stability, and DQ remain separate guardrail concepts" in markdown
    assert "Do not copy profiling, schema, stability, DQ, or catalogue-evidence code" in markdown
    assert "Do not copy profiling, schema, stability, DQ, catalogue-evidence, or write orchestration code" in markdown


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
    assert code.count("write_catalogue_evidence(") == 1
    assert "catalogue_status = write_catalogue_evidence(" in code
    assert code.count("write_pipeline_lineage(") == 1


def test_pipeline_notebook_runs_guardrails_from_source_and_target_config_lists():
    markdown, code = _notebook_sources()

    assert "DATASET_NAME = \"CHANGE_ME_dataset\"" in code
    assert "df_source_01 = read_lakehouse_table(" in code
    assert "SOURCE_01_CONFIG = {" in code
    assert "# df_source_02 = read_lakehouse_csv(" in code
    assert "# SOURCE_02_CONFIG = {" in code
    assert "SOURCE_TABLES = [SOURCE_01_CONFIG]" in code
    assert "# SOURCE_TABLES = [SOURCE_01_CONFIG, SOURCE_02_CONFIG]" in code
    assert "for table_config in table_configs:" in code
    assert "source_guardrail_results = run_table_guardrails(" in code
    assert "stop_if_any_guardrail_failed(source_guardrail_results)" in code
    assert code.index("source_guardrail_results = run_table_guardrails(") < code.index("df_target_01 = (")

    source_block = code[code.index("SOURCE_01_CONFIG = {"):code.index("# Source 02 example")]
    for required_field in [
        '"key"',
        '"df"',
        '"dataset_name"',
        '"table_name"',
        '"stage": "source"',
        '"schema_preset"',
        '"data_behavior"',
        '"stability_check_type"',
        '"watermark_column"',
        '"watermark_value"',
        '"dq_preset"',
        '"expected_schema"',
        '"distribution_columns"',
        '"exclude_columns"',
    ]:
        assert required_field in source_block

    assert "df_target_01 = (" in code
    assert "TARGET_01_CONFIG = {" in code
    assert "# TARGET_02_CONFIG = {" in code
    assert "TARGET_TABLES = [TARGET_01_CONFIG]" in code
    assert "# TARGET_TABLES = [TARGET_01_CONFIG, TARGET_02_CONFIG]" in code
    assert "target_guardrail_results = run_table_guardrails(" in code
    assert "stop_if_any_guardrail_failed(target_guardrail_results)" in code
    assert code.index("target_guardrail_results = run_table_guardrails(") < code.index("target_write_status = {}")
    assert "A blocking schema, stability, or DQ failure prevents every target write" in markdown

    target_block = code[code.index("TARGET_01_CONFIG = {"):code.index("# Target 02 example")]
    for required_field in [
        '"key"',
        '"df"',
        '"dataset_name"',
        '"target_name"',
        '"target_layer"',
        '"target_kind"',
        '"write_mode"',
        '"schema_preset"',
        '"data_behavior"',
        '"stability_check_type"',
        '"watermark_column"',
        '"watermark_value"',
        '"dq_preset"',
        '"expected_schema"',
        '"distribution_columns"',
        '"partition_by"',
        '"repartition_by"',
        '"overwrite_schema"',
    ]:
        assert required_field in target_block

    assert "source_definitions=source_evidence_definitions" in code
    assert "target_definitions=target_evidence_definitions" in code
    assert '"sources": ["source_01"]' in code
    assert '"targets": ["target_01"]' in code
    assert "CHANGE_ME_source_table rows are transformed into CHANGE_ME_target_table" in code


def test_pipeline_notebook_collects_separate_guardrail_results_before_stopping():
    _, code = _notebook_sources()

    assert "def run_table_guardrails(" in code
    assert "def stop_if_any_guardrail_failed(guardrail_results):" in code
    assert "profiles = {}" in code
    assert "schema_results = {}" in code
    assert "stability_results = {}" in code
    assert "dq_results = {}" in code
    assert "failed_tables = []" in code
    assert '"profiles": profiles' in code
    assert '"schema_results": schema_results' in code
    assert '"stability_results": stability_results' in code
    assert '"dq_results": dq_results' in code
    assert '"catalogue_status": catalogue_status' in code
    assert '"can_continue": not failed_tables' in code
    assert '"failed_tables": failed_tables' in code

    helper_body = code[code.index("def run_table_guardrails("):code.index("def stop_if_any_guardrail_failed")]
    assert helper_body.index("profile_dataframe(") < helper_body.index("validate_schema(")
    assert helper_body.index("validate_schema(") < helper_body.index("enforce_catalogue_stability(")
    assert helper_body.index("enforce_catalogue_stability(") < helper_body.index("enforce_dq_rules(")
    assert helper_body.index("enforce_dq_rules(") < helper_body.index("write_catalogue_evidence(")
    assert "stop_if_failed(" not in helper_body

    source_display = code[code.index("source_guardrail_results = run_table_guardrails("):code.index("stop_if_any_guardrail_failed(source_guardrail_results)")]
    target_display = code[code.index("target_guardrail_results = run_table_guardrails("):code.index("stop_if_any_guardrail_failed(target_guardrail_results)")]
    for display_block in [source_display, target_display]:
        assert '"schema_results"' in display_block
        assert '"stability_results"' in display_block
        assert '"dq_results"' in display_block
        assert '"failed_tables"' in display_block


def test_pipeline_notebook_writes_catalogue_evidence_with_governance_context():
    _, code = _notebook_sources()

    evidence_call = code[code.index("catalogue_status = write_catalogue_evidence("):code.index("return {", code.index("catalogue_status = write_catalogue_evidence("))]
    for context_field in [
        "run_id=run_id",
        "agreement_id=agreement_id",
        "agreement_contract_version=agreement_contract_version",
        "notebook_registry_id=notebook_registry_id",
        "notebook_id=notebook_id",
        "pipeline_name=pipeline_name",
        "schema_results=schema_results",
        "stability_results=stability_results",
        "dq_results=dq_results",
    ]:
        assert context_field in evidence_call
