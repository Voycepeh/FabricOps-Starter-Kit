from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.contract

ROOT = Path(__file__).parents[2]
PIPELINE_NOTEBOOK = ROOT / "templates" / "notebooks" / "02_pipeline.ipynb"


def _notebook_sources() -> tuple[str, str, list[str]]:
    notebook = json.loads(PIPELINE_NOTEBOOK.read_text(encoding="utf-8"))
    markdown_cells = ["".join(cell.get("source", [])) for cell in notebook["cells"] if cell.get("cell_type") == "markdown"]
    code_cells = ["".join(cell.get("source", [])) for cell in notebook["cells"] if cell.get("cell_type") == "code"]
    for cell in code_cells:
        ast.parse("\n".join(line for line in cell.splitlines() if not line.lstrip().startswith("%")))
    return "\n".join(markdown_cells), "\n".join(code_cells), code_cells


def test_pipeline_notebook_uses_minimal_public_helpers_and_no_pr_only_wrappers():
    markdown, code, _ = _notebook_sources()

    for helper in [
        "prepare_pipeline_table_configs",
        "run_table_guardrails",
        "write_lakehouse_table",
        "write_warehouse_table",
        "write_pipeline_lineage",
        "write_pipeline_run_summary",
    ]:
        assert helper in code

    for forbidden in [
        "prepare_source_table_configs",
        "prepare_target_table_configs",
        "write_target_tables",
        "guardrail_summary",
        "stop_if_any_guardrail_failed",
        "build_guardrail_evidence_definitions",
        "write_catalogue_evidence",
        "_load_source_dataframe",
        "_read_source_dataframe",
        "_source_read_type",
        "read_type",
        "def _table_key(",
        "def _table_name(",
        "def run_table_guardrails(",
    ]:
        assert forbidden not in code

    assert "write_catalogue_evidence" not in code
    assert "through `run_table_guardrails`" in markdown


def test_pipeline_notebook_contains_final_thin_flow_sections():
    markdown, _code, _cells = _notebook_sources()
    expected_sections = [
        "## 1. Run `00_env_config`",
        "## 2. Import required functions",
        "## 3. Select data agreement and capture run context",
        "## 4. USER EDIT SECTION — load source DataFrames",
        "## 5. USER EDIT SECTION — source guardrail configuration",
        "## 6. Source guardrail defaults",
        "## 7. Prepare source table configs",
        "## 8. Optional: inspect a source schema",
        "## 9. Run source guardrails before transformation",
        "## 10. USER EDIT SECTION — DIY transformations",
        "## 11. USER EDIT SECTION — target table configuration",
        "## 12. Target guardrail and write defaults",
        "## 13. Prepare target table configs",
        "## 14. Run target guardrails before writes",
        "## 15. Write target tables",
        "## 16. USER EDIT SECTION — lineage relationships",
        "## 17. Write lineage",
        "## 18. Write runtime summary",
    ]
    for section in expected_sections:
        assert section in markdown

    assert "This is the only section where most users write business transformation logic" in markdown
    assert "Keep this section visible because it is the point where data is published" in markdown
    assert "These are the default guardrails applied to every source table" in markdown
    assert "These are the default guardrails and write options applied to every target table" in markdown



def test_source_loading_uses_existing_read_helpers_directly():
    _markdown, code, _cells = _notebook_sources()

    load_block = code[code.index("df_source_01 = read_lakehouse_table(") : code.index("SOURCE_TABLES = [")]
    assert 'read_lakehouse_table(' in load_block
    assert 'read_lakehouse_csv(' in load_block
    assert 'read_lakehouse_parquet(' in load_block
    assert 'read_lakehouse_excel(' in load_block
    assert 'read_warehouse_table(' in load_block
    assert 'spark.read.table("CHANGE_ME_database.CHANGE_ME_table")' in load_block
    assert '"source",' in load_block
    assert '"CHANGE_ME_source_table",' in load_block
    assert 'spark_session=spark' in load_block

def test_source_config_defaults_are_reduced_but_advanced_overrides_remain_discoverable():
    _markdown, code, _cells = _notebook_sources()

    assert "DATASET_NAME =" not in code
    assert "DATA_PRODUCT_NAME" not in code
    assert "SOURCE_TABLES = [" in code
    assert '"key": "source_01"' in code
    assert '"layer": "source"' in code
    assert '"df": df_source_01' in code
    assert '"table_name": "CHANGE_ME_source_table"' in code
    assert '"watermark_column": "business_date"' in code

    source_user_block = code[code.index("SOURCE_TABLES = [") : code.index("DEFAULT_SOURCE_GUARDRAILS = {")]
    source_default_example = source_user_block[: source_user_block.index("# To add a second source table")]
    for beginner_field in [
        '"customer_id": "bigint"',
        '"business_date": "date"',
        '"event_ts": "string"',
        '"status": "string"',
        '"amount": "double"',
        '"email": "string"',
        '"country_code": "string"',
    ]:
        assert beginner_field in source_default_example
    for hidden_beginner_field in ['"dataset_name"', '"stage"', '"watermark_value"']:
        assert hidden_beginner_field not in source_default_example
    for advanced_override in [
        '"dataset_name": "CHANGE_ME_governance_dataset"',
        '"stage": "source"',
        '"watermark_value": "2026-01-31"',
        '"dq_preset": "approved_rules"',
    ]:
        assert advanced_override in source_user_block

    assert "SOURCE_TABLES, SOURCE_CONFIG_BY_KEY = prepare_pipeline_table_configs(" in code
    source_prepare_block = code[code.index("SOURCE_TABLES, SOURCE_CONFIG_BY_KEY = prepare_pipeline_table_configs(") : code.index("df_source_01 = SOURCE_CONFIG_BY_KEY")]
    assert 'table_role="source"' in source_prepare_block
    assert "config=CONFIG" not in source_prepare_block
    assert "env=ENV_NAME" not in source_prepare_block
    assert "spark_session=spark" not in source_prepare_block
    assert 'df_source_01 = SOURCE_CONFIG_BY_KEY["source_01"]["df"]' in code


def test_guardrail_default_sections_include_supported_preset_comments():
    _markdown, code, _cells = _notebook_sources()

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
        '# Write mode options for Lakehouse targets:',
        '#   "overwrite" = replace the target table',
        '#   "append" = add rows to the target table',
        '#   "errorifexists" = fail if the target table already exists',
        '#   "ignore" = skip the write if the target table already exists',
        '# Target kind options:',
        '#   "lakehouse" = write a Lakehouse Delta table',
        '#   "warehouse" = write a Fabric Warehouse table',
    ]:
        assert preset_comment in code

    assert "DEFAULT_SOURCE_GUARDRAILS = {" in code
    assert "DEFAULT_TARGET_GUARDRAILS_AND_WRITE_OPTIONS = {" in code


def test_active_default_source_transform_and_target_schema_are_coherent_passthrough():
    _markdown, code, _cells = _notebook_sources()

    transform_block = code[code.index("# DIY your transformations here.") : code.index("TARGET_TABLES = [")]
    assert "df_target_01 = df_source_01" in transform_block
    assert '"amount_band"' in transform_block  # commented example only

    target_user_block = code[code.index("TARGET_TABLES = [") : code.index("DEFAULT_TARGET_GUARDRAILS_AND_WRITE_OPTIONS = {")]
    target_default_example = target_user_block[: target_user_block.index("# To add a second target table")]
    for expected_column in [
        '"customer_id": "bigint"',
        '"business_date": "date"',
        '"event_ts": "string"',
        '"status": "string"',
        '"amount": "double"',
        '"email": "string"',
        '"country_code": "string"',
        '"_fabricops_run_id": "string"',
        '"_fabricops_pipeline_name": "string"',
        '"_fabricops_created_at": "string"',
    ]:
        assert expected_column in target_default_example
    assert '"amount_band": "string"' not in target_default_example
    for hidden_beginner_field in ['"dataset_name"', '"stage"', '"target_kind"', '"watermark_value"', '"kind"']:
        assert hidden_beginner_field not in target_default_example

    assert "TARGET_TABLES, TARGET_CONFIG_BY_KEY = prepare_pipeline_table_configs(" in code
    assert 'table_role="target"' in code


def test_guardrails_stop_before_transform_and_writes_via_run_table_guardrails_flag():
    _markdown, code, _cells = _notebook_sources()

    source_guardrails = code.index("source_guardrail_results = run_table_guardrails(")
    source_stop_flag = code.index("stop_on_failure=True", source_guardrails)
    transform = code.index("df_target_01 = df_source_01")
    target_prepare = code.index("TARGET_TABLES, TARGET_CONFIG_BY_KEY = prepare_pipeline_table_configs(")
    target_guardrails = code.index("target_guardrail_results = run_table_guardrails(")
    target_stop_flag = code.index("stop_on_failure=True", target_guardrails)
    target_write = code.index("target_write_status = {}")

    assert source_guardrails < source_stop_flag < transform < target_prepare < target_guardrails < target_stop_flag < target_write
    assert 'display(source_guardrail_results["summary"])' in code
    assert 'display(target_guardrail_results["summary"])' in code

    for runtime_alias in [
        'source_schema_results = source_guardrail_results["schema_results"]',
        'source_stability_results = source_guardrail_results["stability_results"]',
        'source_dq_results = source_guardrail_results["dq_results"]',
        'source_evidence_definitions = source_guardrail_results["evidence_definitions"]',
        'target_schema_results = target_guardrail_results["schema_results"]',
        'target_stability_results = target_guardrail_results["stability_results"]',
        'target_dq_results = target_guardrail_results["dq_results"]',
        'target_evidence_definitions = target_guardrail_results["evidence_definitions"]',
    ]:
        assert runtime_alias in code


def test_explicit_target_write_loop_uses_existing_write_helpers_and_checked_dataframes():
    _markdown, code, _cells = _notebook_sources()

    write_block = code[code.index("target_write_status = {}") : code.index("LINEAGE_RELATIONSHIPS = [")]
    assert "for target_config in TARGET_TABLES:" in write_block
    assert "write_lakehouse_table(" in write_block
    assert "write_warehouse_table(" in write_block
    assert 'target_config["df"]' in write_block
    assert "write_target_tables" not in write_block
    assert "Unsupported target kind" in write_block


def test_lineage_and_runtime_summary_still_use_package_evidence_outputs():
    _markdown, code, _cells = _notebook_sources()

    assert "write_pipeline_lineage(" in code
    assert "write_pipeline_run_summary(" in code
    assert 'source_definitions=source_evidence_definitions' in code
    assert 'target_definitions=target_evidence_definitions' in code
    assert 'dataset_name=TARGET_01_CONFIG["dataset_name"]' in code
    assert "METADATA_PIPELINE_RUNS" in _markdown
