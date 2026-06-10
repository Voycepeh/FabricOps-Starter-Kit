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
        "guardrail_summary",
        "run_table_guardrails",
        "stop_if_any_guardrail_failed",
        "stop_if_failed",
        "write_lakehouse_table",
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
    assert 'target_config["df"]' in code
    assert "RUN_ID = RUN_CONTEXT.run_id" in code
    assert "RUN_CONTEXT.runtime_metadata.get" in code
    assert "SETUP." not in code
    assert "LINEAGE_RELATIONSHIPS" in code
    assert "METADATA_PIPELINE_RUNS" in markdown
    assert "imports existing FabricOps callables for reads, guardrail orchestration, writes" in markdown
    assert "FabricOps then enriches those source and target entries with guardrail defaults, write defaults, and DataFrames" in markdown


def test_pipeline_notebook_contains_expected_config_driven_flow_sections():
    markdown, _ = _notebook_sources()
    expected_sections = [
        "## 1. Run `00_env_config`",
        "## 2. Import required functions",
        "## 3. Select data agreement and capture run context",
        "## 4. USER EDIT SECTION — source table configuration",
        "## 5. Source guardrail defaults",
        "## 6. Load source tables",
        "## 7. Optional: inspect a source schema",
        "## 8. Guardrail orchestration is handled by FabricOps",
        "## 9. Run source guardrails before transformation",
        "## 10. Transform to target DataFrames",
        "## TARGET USER EDIT SECTION — target table configuration",
        "## Target guardrail and write defaults",
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
    assert "These are the default guardrails applied to every source table" in markdown
    assert "This section reads each table listed in `SOURCE_TABLES` and adds the default source guardrails" in markdown
    assert "To use a file or warehouse source, comment out the default Lakehouse table read" in markdown
    assert "To support multiple source tables, add another dictionary to `SOURCE_TABLES`" in markdown
    assert "source setup configures input tables" in markdown
    assert "transform section creates target DataFrames" in markdown
    assert "target setup configures output tables and write behavior" in markdown
    assert "Most users only edit this target section" in markdown
    assert "These are the default guardrails and write options applied to every target table" in markdown
    assert "To support multiple target tables, add another dictionary to `TARGET_TABLES`" in markdown
    assert "Do not copy profiling, schema, stability, DQ, or catalogue-evidence code" in markdown
    assert "Do not copy profiling, schema, stability, DQ, catalogue-evidence, or write orchestration code" in markdown
    assert "`metadata` = governance evidence lakehouse" in markdown
    assert "Most users should not need to customize this orchestration code" in markdown


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
    assert "write_catalogue_evidence(" not in code
    assert code.count("write_pipeline_lineage(") == 1


def test_pipeline_notebook_runs_guardrails_from_source_and_target_config_lists():
    markdown, code = _notebook_sources()

    assert "DATASET_NAME = \"CHANGE_ME_dataset\"" not in code
    assert "DATA_PRODUCT_NAME" not in code
    assert "SOURCE_TABLES = [" in code
    assert '"key": "source_01"' in code
    assert '"layer": "source"' in code
    assert '"table_name": "CHANGE_ME_source_table"' in code
    assert '"watermark_column": "CHANGE_ME_business_date"' in code
    assert '"expected_schema": {' in code
    assert '"business_date": "date"' in code
    assert '"dq_preset": "approved_rules"' in code
    assert "DEFAULT_SOURCE_GUARDRAILS = {" in code
    assert '"schema_preset": "allow_new_columns"' in code
    assert '"data_behavior": "changing"' in code
    assert '"stability_check_type": "watermark_slice_hash"' in code
    for preset_comment in [
        '# Schema preset options:',
        '#   "allow_new_columns" = allow additive columns, block incompatible schema drift',
        '#   "strict" = require the schema to match exactly',
        '#   "monitor_only" = report schema differences without blocking',
        '# Data behavior options:',
        '#   "changing" = source data can change between runs',
        '#   "fixed" = source data is expected to remain stable',
        '# Stability check options:',
        '#   "watermark_slice_hash" = hash one business-date/extract-date slice',
        '#   "full_profile_hash" = hash the full profile',
        '#   "skip" = skip stability enforcement for this table',
        '# DQ preset options:',
        '#   "approved_rules" = enforce approved DQ rules from governance metadata',
        '#   "skip" = skip DQ enforcement for this table',
    ]:
        assert preset_comment in code
    assert "_SOURCE_TABLES_USER_CONFIG = SOURCE_TABLES" in code
    assert "for source_config in _SOURCE_TABLES_USER_CONFIG:" in code
    assert 'dataset_name = source_config.get("dataset_name", source_config["table_name"])' in code
    assert 'stage = source_config.get("stage", source_config["layer"])' in code
    assert 'watermark_value = source_config.get("watermark_value", None)' in code
    assert "**DEFAULT_SOURCE_GUARDRAILS" in code
    assert "**source_config" in code
    assert '"dataset_name": dataset_name' in code
    assert '"stage": stage' in code
    assert '"watermark_value": watermark_value' in code
    assert 'enriched_source["df"] = read_lakehouse_table(' in code
    assert 'enriched_source["layer"],' in code
    assert 'enriched_source["table_name"],' in code
    for read_alternative in [
        '# enriched_source["df"] = read_lakehouse_csv(',
        '# enriched_source["df"] = read_lakehouse_parquet(',
        '# enriched_source["df"] = read_lakehouse_excel(',
        '# enriched_source["df"] = read_warehouse_table(',
        '# enriched_source["df"] = spark.read.table("CHANGE_ME_database.CHANGE_ME_table")',
    ]:
        assert read_alternative in code
    assert '"CHANGE_ME/path/to/file.csv"' in code
    assert '"CHANGE_ME/path/to/file.parquet"' in code
    assert '"CHANGE_ME/path/to/file.xlsx"' in code
    assert '"CHANGE_ME_warehouse_target"' in code
    assert "SOURCE_CONFIG_BY_KEY =" in code
    assert 'SOURCE_01_CONFIG = SOURCE_CONFIG_BY_KEY["source_01"]' not in code
    assert 'df_source_01 = SOURCE_CONFIG_BY_KEY["source_01"]["df"]' in code
    assert 'SOURCE_01_CONFIG["df"]' not in code
    assert "source_guardrail_results = run_table_guardrails(" in code
    assert "stop_if_any_guardrail_failed(source_guardrail_results)" in code
    assert code.index("source_guardrail_results = run_table_guardrails(") < code.index("df_target_01 = (")

    source_user_block = code[code.index("SOURCE_TABLES = ["):code.index("DEFAULT_SOURCE_GUARDRAILS = {")]
    source_default_example = source_user_block[:source_user_block.index("# To add a second source table")]
    for snippet in [
        '"key": "source_01"',
        '"layer": "source"',
        '"table_name": "CHANGE_ME_source_table"',
        '"watermark_column": "CHANGE_ME_business_date"',
        '"expected_schema": {',
    ]:
        assert snippet in source_default_example
    for hidden_beginner_field in [
        "DATASET_NAME",
        '"dataset_name"',
        '"stage"',
        '"watermark_value"',
    ]:
        assert hidden_beginner_field not in source_default_example
    for advanced_override in [
        '"dataset_name": "CHANGE_ME_governance_dataset"',
        '"stage": "source"',
        '"watermark_value": "2026-01-31"',
        '"dq_preset": "approved_rules"',
        '"kind": "lakehouse"',
    ]:
        assert advanced_override in source_user_block

    assert "`source` = raw/source lakehouse table" in markdown
    assert "`unified` = cleaned/conformed lakehouse table" in markdown
    assert "`product` = curated product or warehouse output" in markdown
    assert "`metadata` = governance evidence lakehouse" in markdown
    assert "Most users should not need to customize this orchestration code" in markdown
    assert "not usually selected as a business source table" in markdown
    assert "FabricOps derives the governance `dataset_name` from `table_name`" in markdown
    assert "Advanced override support: add `dataset_name`, `stage`, `watermark_value`, `dq_preset`, or `kind`" in markdown

    assert "TARGET_TABLES = [" in code
    assert '"key": "target_01"' in code
    assert '"df": df_target_01' in code
    assert '"layer": "unified"' in code
    assert '"table_name": "CHANGE_ME_target_table"' in code
    assert '"write_mode": "overwrite"' in code
    assert "DEFAULT_TARGET_GUARDRAILS_AND_WRITE_OPTIONS = {" in code
    assert '"schema_preset": "strict"' in code
    assert '"data_behavior": "changing"' in code
    assert '"stability_check_type": "watermark_slice_hash"' in code
    assert '"dq_preset": "approved_rules"' in code
    for preset_comment in [
        '#   "changing" = target data can change between runs',
        '#   "fixed" = target data is expected to remain stable',
        '# Lakehouse write mode options: "overwrite", "append", "errorifexists", "ignore".',
        '# Warehouse writes use Spark connector modes such as "overwrite" or "append".',
        '# Target kind options:',
        '#   "lakehouse" = write a Lakehouse Delta table',
        '#   "warehouse" = write a Fabric Warehouse table',
    ]:
        assert preset_comment in code
    assert "_TARGET_TABLES_USER_CONFIG = TARGET_TABLES" in code
    assert "for target_config in _TARGET_TABLES_USER_CONFIG:" in code
    assert "**DEFAULT_TARGET_GUARDRAILS_AND_WRITE_OPTIONS" in code
    assert "**target_config" in code
    assert 'dataset_name = target_config.get("dataset_name", target_config["table_name"])' in code
    assert 'stage = target_config.get("stage", target_config["layer"])' in code
    assert 'target_layer = target_config.get("target_layer", target_config["layer"])' in code
    assert 'target_name = target_config.get("target_name", target_config["table_name"])' in code
    assert 'target_kind = target_config.get("target_kind", target_config.get("kind", "lakehouse"))' in code
    assert 'watermark_value = target_config.get("watermark_value", None)' in code
    assert '"dataset_name": dataset_name' in code
    assert '"stage": stage' in code
    assert '"target_layer": target_layer' in code
    assert '"target_name": target_name' in code
    assert '"target_kind": target_kind' in code
    assert '"watermark_value": watermark_value' in code
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

    target_user_block = code[code.index("TARGET_TABLES = ["):code.index("DEFAULT_TARGET_GUARDRAILS_AND_WRITE_OPTIONS = {")]
    target_default_example = target_user_block[:target_user_block.index("# To add a second target table")]
    for snippet in [
        '"key": "target_01"',
        '"df": df_target_01',
        '"layer": "unified"',
        '"table_name": "CHANGE_ME_target_table"',
        '"write_mode": "overwrite"',
        '"watermark_column": "CHANGE_ME_business_date"',
        '"expected_schema": {',
    ]:
        assert snippet in target_default_example
    for hidden_beginner_field in [
        "DATASET_NAME",
        "DATA_PRODUCT_NAME",
        '"dataset_name"',
        '"stage"',
        '"kind"',
        '"watermark_value"',
    ]:
        assert hidden_beginner_field not in target_default_example
    for advanced_override in [
        '"dataset_name": "CHANGE_ME_governance_dataset"',
        '"stage": "product"',
        '"target_layer": "product"',
        '"target_name": "CHANGE_ME_written_table_name"',
        '"target_kind": "warehouse"',
        '"watermark_value": "2026-01-31"',
        '"dq_preset": "approved_rules"',
        '"kind": "warehouse"',
        '"partition_by": ["business_date"]',
    ]:
        assert advanced_override in target_user_block
    assert "uses `lakehouse` as the default target kind" in markdown
    assert "Advanced override support: add `dataset_name`, `stage`, `target_layer`, `target_name`, `target_kind`, `watermark_value`, `dq_preset`, or `kind`" in markdown

    assert "source_definitions=source_evidence_definitions" in code
    assert "target_definitions=target_evidence_definitions" in code
    assert '"sources": ["source_01"]' in code
    assert '"targets": [TARGET_01_KEY]' in code
    assert '"operation": f"derive amount band and publish {TARGET_01_TABLE_NAME}"' in code
    assert '"description": f"{SOURCE_CONFIG_BY_KEY[\'source_01\'][\'table_name\']} rows are transformed into {TARGET_01_TABLE_NAME}."' in code
    assert 'dataset_name=TARGET_01_CONFIG["dataset_name"]' in code

def test_pipeline_notebook_imports_guardrail_orchestration_instead_of_defining_it():
    markdown, code = _notebook_sources()

    for notebook_helper_definition in [
        "def _table_key(",
        "def _table_name(",
        "def _guardrail_can_continue(",
        "def build_guardrail_evidence_definitions(",
        "def run_table_guardrails(",
        "def stop_if_any_guardrail_failed(",
    ]:
        assert notebook_helper_definition not in code

    assert "run_table_guardrails," in code
    assert "guardrail_summary," in code
    assert "stop_if_any_guardrail_failed," in code
    assert "Guardrail orchestration is handled by FabricOps" in markdown
    assert "FabricOps runs profiling, schema validation, stability checks, DQ checks, catalogue evidence" in markdown

    source_display = code[code.index("source_guardrail_results = run_table_guardrails("):code.index("stop_if_any_guardrail_failed(source_guardrail_results)")]
    target_display = code[code.index("target_guardrail_results = run_table_guardrails("):code.index("stop_if_any_guardrail_failed(target_guardrail_results)")]
    for display_block in [source_display, target_display]:
        assert "display(guardrail_summary(" in display_block

    assert "source_dq_results = {}" not in code
    assert "source_profiles =" not in code

def test_pipeline_notebook_uses_package_guardrails_for_catalogue_evidence():
    _, code = _notebook_sources()

    assert "write_catalogue_evidence(" not in code
    assert 'source_evidence_definitions = source_guardrail_results["evidence_definitions"]' in code
    assert 'target_evidence_definitions = target_guardrail_results["evidence_definitions"]' in code
    assert "source_definitions=source_evidence_definitions" in code
    assert "target_definitions=target_evidence_definitions" in code
