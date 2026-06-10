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
    assert "FabricOps then enriches those source and target entries with framework defaults and DataFrames" in markdown


def test_pipeline_notebook_contains_expected_config_driven_flow_sections():
    markdown, _ = _notebook_sources()
    expected_sections = [
        "## 1. Run `00_env_config`",
        "## 2. Import required functions",
        "## 3. Select data agreement and capture run context",
        "## 4. USER EDIT SECTION — source table configuration",
        "## 5. FRAMEWORK DEFAULTS — source governance settings",
        "## 6. FRAMEWORK PREPARATION — load and enrich source configs",
        "## 7. Optional: inspect a source schema",
        "## 8. Define reusable guardrail orchestration helpers",
        "## 9. Run source guardrails before transformation",
        "## 10. Transform to target DataFrames",
        "## TARGET USER EDIT SECTION — target table configuration",
        "## TARGET FRAMEWORK DEFAULTS — target governance and write settings",
        "## TARGET FRAMEWORK PREPARATION — enrich target configs",
        "## 13. Run target guardrails before writes",
        "## 14. Write target tables",
        "## 15. Capture many-to-many lineage",
        "## 16. Write runtime summary",
    ]
    for section in expected_sections:
        assert section in markdown

    assert "beginner friendly" in markdown
    assert "Schema, stability, and DQ remain separate guardrail concepts" in markdown
    assert "Most users only edit this section for sources" in markdown
    assert "To support multiple source tables, add another dictionary to `SOURCE_TABLES`" in markdown
    assert "source setup configures input tables" in markdown
    assert "transform section creates target DataFrames" in markdown
    assert "target setup configures output tables and write behavior" in markdown
    assert "Most users only edit this target section" in markdown
    assert "To support multiple target tables, add another dictionary to `TARGET_TABLES`" in markdown
    assert "Do not copy profiling, schema, stability, DQ, or catalogue-evidence code" in markdown
    assert "Do not copy profiling, schema, stability, DQ, catalogue-evidence, or write orchestration code" in markdown
    assert "`metadata` = governance evidence lakehouse" in markdown


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
    assert "SOURCE_TABLES = [" in code
    assert '"key": "source_01"' in code
    assert '"layer": "source"' in code
    assert '"table_name": "CHANGE_ME_source_table"' in code
    assert '"stage": "source"' in code
    assert '"watermark_column": "CHANGE_ME_business_date"' in code
    assert '"watermark_value": None' in code
    assert '"expected_schema": {' in code
    assert '"business_date": "date"' in code
    assert '"dq_preset": "approved_rules"' in code
    assert "DEFAULT_SOURCE_SETTINGS = {" in code
    assert '"schema_preset": "allow_new_columns"' in code
    assert '"data_behavior": "changing"' in code
    assert '"stability_check_type": "watermark_slice_hash"' in code
    assert "_SOURCE_TABLES_USER_CONFIG = SOURCE_TABLES" in code
    assert "for source_config in _SOURCE_TABLES_USER_CONFIG:" in code
    assert "**DEFAULT_SOURCE_SETTINGS" in code
    assert "**source_config" in code
    assert '"dataset_name": DATASET_NAME' in code
    assert 'enriched_source["df"] = read_lakehouse_table(' in code
    assert 'enriched_source["layer"],' in code
    assert 'enriched_source["table_name"],' in code
    assert "SOURCE_CONFIG_BY_KEY =" in code
    assert 'SOURCE_01_CONFIG = SOURCE_CONFIG_BY_KEY["source_01"]' in code
    assert "df_source_01 = SOURCE_01_CONFIG[\"df\"]" in code
    assert "for table_config in table_configs:" in code
    assert "source_guardrail_results = run_table_guardrails(" in code
    assert "stop_if_any_guardrail_failed(source_guardrail_results)" in code
    assert code.index("source_guardrail_results = run_table_guardrails(") < code.index("df_target_01 = (")

    user_edit_block = code[code.index("DATASET_NAME = \"CHANGE_ME_dataset\""):code.index("DEFAULT_SOURCE_SETTINGS = {")]
    for inline_comment in [
        "Change: business dataset or domain name",
        "Usually keep: unique source key",
        "Usually keep: configured lakehouse layer",
        "Change: source lakehouse table name",
        "Usually keep: governance stage",
        "Change when using watermark stability",
        "Usually keep None",
        "Change: columns and Spark SQL types",
        "Optional: uncomment to override DEFAULT_SOURCE_SETTINGS",
    ]:
        assert inline_comment in user_edit_block

    assert "`source` = raw/source lakehouse table" in markdown
    assert "`unified` = cleaned/conformed lakehouse table" in markdown
    assert "`product` = curated product or warehouse output" in markdown
    assert "`metadata` = governance evidence lakehouse" in markdown
    assert "not usually selected as a business source table" in markdown

    assert "TARGET_TABLES = [" in code
    assert '"key": "target_01"' in code
    assert '"df": df_target_01' in code
    assert '"layer": "unified"' in code
    assert '"table_name": "CHANGE_ME_target_table"' in code
    assert '"stage": "unified"' in code
    assert '"kind": "lakehouse"' in code
    assert '"write_mode": "overwrite"' in code
    assert "DEFAULT_TARGET_SETTINGS = {" in code
    assert '"schema_preset": "strict"' in code
    assert '"data_behavior": "changing"' in code
    assert '"stability_check_type": "watermark_slice_hash"' in code
    assert '"dq_preset": "approved_rules"' in code
    assert "_TARGET_TABLES_USER_CONFIG = TARGET_TABLES" in code
    assert "for target_config in _TARGET_TABLES_USER_CONFIG:" in code
    assert "**DEFAULT_TARGET_SETTINGS" in code
    assert "**target_config" in code
    assert '"dataset_name": DATASET_NAME' in code
    assert 'enriched_target["target_layer"] = enriched_target.get("target_layer", enriched_target["layer"])' in code
    assert 'enriched_target["target_name"] = enriched_target.get("target_name", enriched_target["table_name"])' in code
    assert 'enriched_target["target_kind"] = enriched_target.get("target_kind", enriched_target.get("kind", "lakehouse"))' in code
    assert "TARGET_CONFIG_BY_KEY =" in code
    assert 'TARGET_01_CONFIG = TARGET_CONFIG_BY_KEY["target_01"]' in code
    assert 'TARGET_01_TABLE_NAME = TARGET_01_CONFIG["table_name"]' in code
    assert "TARGET_01_KEY = \"target_01\"" not in code
    assert "TARGET_01_TABLE_NAME = \"CHANGE_ME_target_table\"" not in code
    assert "TARGET_01_LAYER = \"unified\"" not in code
    assert "TARGET_01_WRITE_MODE = \"overwrite\"" not in code
    assert "TARGET_01_CONFIG = {" not in code
    assert "# TARGET_02_KEY = \"target_02\"" not in code
    assert "# TARGET_02_CONFIG = {" not in code
    assert "TARGET_TABLES = [TARGET_01_CONFIG]" not in code
    assert "# TARGET_TABLES = [TARGET_01_CONFIG, TARGET_02_CONFIG]" not in code
    assert "target_guardrail_results = run_table_guardrails(" in code
    assert "stop_if_any_guardrail_failed(target_guardrail_results)" in code
    assert code.index("target_guardrail_results = run_table_guardrails(") < code.index("target_write_status = {}")
    assert "A blocking schema, stability, or DQ failure prevents every target write" in markdown

    target_user_block = code[code.index("TARGET_TABLES = ["):code.index("DEFAULT_TARGET_SETTINGS = {")]
    for inline_comment in [
        "Usually keep: unique key for target guardrail results and lineage",
        "Usually keep: DataFrame produced in the transformation section",
        "Change if writing to a different configured output layer",
        "Change: output table name to publish",
        "Usually keep aligned with the output layer",
        "Usually keep: use lakehouse",
        "Change only when append/merge behavior is intended",
        "Change: expected schema after transformation",
        "Optional: uncomment any table-specific overrides",
        "Optional: partition Lakehouse output",
    ]:
        assert inline_comment in target_user_block

    assert "source_definitions=source_evidence_definitions" in code
    assert "target_definitions=target_evidence_definitions" in code
    assert '"sources": [SOURCE_01_KEY]' in code
    assert '"targets": [TARGET_01_KEY]' in code
    assert '"operation": f"derive amount band and publish {TARGET_01_TABLE_NAME}"' in code
    assert '"description": f"{SOURCE_01_TABLE_NAME} rows are transformed into {TARGET_01_TABLE_NAME}."' in code

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
