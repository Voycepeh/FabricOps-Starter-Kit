"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import ast
import json
import re
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
    """Verify pipeline notebook uses minimal public helpers and no pr only wrappers."""
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


def test_pipeline_agreement_selector_passes_metadata_schema():
    """Verify pipeline agreement selector passes metadata schema."""
    _markdown, code, _cells = _notebook_sources()

    selector_block = code[code.index("widget_select_agreement(") : code.index("AGREEMENT = get_selected_agreement()")]
    assert "metadata_schema=METADATA_SCHEMA" in selector_block
    assert "register_notebook=True" in selector_block


def test_pipeline_notebook_contains_final_thin_flow_sections():
    """Verify pipeline notebook contains final thin flow sections."""
    markdown, _code, _cells = _notebook_sources()
    expected_sections = [
        "## 1. Run `00_env_config`",
        "## 2. Import required functions",
        "## 3. Select data agreement and capture run context",
        "## 4. USER EDIT SECTION — read source DataFrames",
        "## 5. USER EDIT SECTION — configure source tables and source guardrails",
        "## 6. Optional: inspect source schemas",
        "## 7. Run source guardrails before transformation",
        "## 8. USER EDIT SECTION — main business transformation logic",
        "## 9. USER EDIT SECTION — configure target tables and target guardrails",
        "## 10. Run target guardrails before writes",
        "## 11. Write target Lakehouse tables",
        "## 12. USER EDIT SECTION — lineage relationships",
        "## 13. Write lineage",
        "## 14. Write runtime summary",
    ]
    for section in expected_sections:
        assert section in markdown

    assert "SOURCE AREA — Steps 4 to 7" in markdown
    assert "TRANSFORMATION AREA — Step 8" in markdown
    assert "TARGET AREA — Steps 9 to 14" in markdown
    assert "Most users should make their business logic changes here" in markdown
    assert "without warehouse write permissions" in markdown
    assert "also add a matching explicit write call in Step 11" in markdown
    assert "prepared configs in `TARGET_CONFIG_BY_KEY` include FabricOps audit columns" in markdown
    assert "with the guardrails and catalogue evidence that belong to that specific source" in markdown
    assert "schema, freshness, DQ, profile" in markdown



def test_source_loading_uses_existing_read_helpers_directly():
    """Verify source loading uses existing read helpers directly."""
    _markdown, code, _cells = _notebook_sources()

    load_block = code[code.index("df_orders = read_lakehouse_table(") : code.index("SOURCE_TABLES = [")]
    assert 'read_lakehouse_table(' in load_block
    assert 'read_lakehouse_csv(' in load_block
    assert 'read_lakehouse_parquet(' in load_block
    assert 'read_lakehouse_excel(' in load_block
    assert 'read_warehouse_table(' in load_block
    assert 'spark.read.table("database.customers")' in load_block
    assert '"source",' in load_block
    assert '"smoke_src_orders_happy",' in load_block
    assert '"smoke_src_customers_happy",' in load_block
    assert 'spark_session=spark' in load_block
    assert 'schema="SmokeTest"' in load_block
    assert "PIPELINE_SOURCE_TABLE_NAME" not in code
    assert "PIPELINE_TARGET_TABLE_NAME" not in code
    assert "PIPELINE_DATASET_NAME" not in code

def test_source_config_defaults_are_reduced_but_advanced_overrides_remain_discoverable():
    """Verify source config defaults are reduced but advanced overrides remain discoverable."""
    _markdown, code, _cells = _notebook_sources()

    assert re.search(r"^DATASET_NAME\s*=", code, re.MULTILINE) is None
    assert "DATA_PRODUCT_NAME" not in code
    assert "SOURCE_TABLES = [" in code
    assert '"key": "orders"' in code
    assert '"key": "customers"' in code
    assert '"layer": "source"' in code
    assert '"df": df_orders' in code
    assert '"df": df_customers' in code
    assert '"table_name": "smoke_src_orders_happy"' in code
    assert '"table_name": "smoke_src_customers_happy"' in code
    assert '"watermark_column": "order_date"' in code
    assert '"watermark_column": "effective_date"' in code

    source_user_block = code[code.index("SOURCE_TABLES = [") : code.index("source_guardrail_results = run_table_guardrails(")]
    source_default_example = source_user_block[: source_user_block.index("# Optional advanced per-table governance overrides")]
    for beginner_field in [
        '"order_id": "bigint"',
        '"customer_id": "bigint"',
        '"order_date": "date"',
        '"ingestion_ts": "timestamp"',
        '"status": "string"',
        '"order_amount": "double"',
        '"country_code": "string"',
    ]:
        assert beginner_field in source_default_example
    assert '"dataset_name"' not in source_default_example
    assert '"stage"' not in source_default_example
    for advanced_override in [
        '"dataset_name": "governance_dataset_override",',
        '"stage": "source"',
        '"dq_preset": "active_rules"',
        '"freshness_column": "order_date"',
        '"freshness_column": "effective_date"',
        '"schema_preset": "allow_new_columns"',
        '"profile_mode": "changing_data"',
    ]:
        assert advanced_override in source_user_block

    assert "SOURCE_TABLES, SOURCE_CONFIG_BY_KEY = prepare_pipeline_table_configs(" in code
    source_prepare_block = code[code.index("SOURCE_TABLES, SOURCE_CONFIG_BY_KEY = prepare_pipeline_table_configs(") : code.index("df_orders = SOURCE_CONFIG_BY_KEY")]
    assert 'table_role="source"' in source_prepare_block
    assert "config=CONFIG" not in source_prepare_block
    assert "env=ENV_NAME" not in source_prepare_block
    assert "spark_session=spark" not in source_prepare_block
    assert 'df_orders = SOURCE_CONFIG_BY_KEY["orders"]["df"]' in code
    assert 'df_customers = SOURCE_CONFIG_BY_KEY["customers"]["df"]' in code


def test_table_configs_include_supported_guardrail_and_write_fields():
    """Verify table configs include supported guardrail and write fields."""
    _markdown, code, _cells = _notebook_sources()

    for field in [
        '"schema_preset": "allow_new_columns"',
        '"schema_preset": "strict"',
        '"profile_mode": "changing_data"',
        '"profile_mode": "static_data"',
        '"freshness_max_lag_days": 1',
        '"freshness_severity": "blocking"',
        '"dq_preset": "active_rules"',
        '"dq_preset": "skip"',
        '"distribution_columns": ["status", "order_amount", "country_code"]',
        '"exclude_columns": None',
        '"write_mode": "overwrite"',
        '"schema": "SmokeTest"',
    ]:
        assert field in code

    assert "DEFAULT_SOURCE_GUARDRAILS = {" not in code
    assert "DEFAULT_TARGET_GUARDRAILS_AND_WRITE_OPTIONS = {" not in code

def test_active_default_source_transform_and_target_schema_are_coherent_many_source():
    """Verify active default source transform and target schema are coherent many source."""
    _markdown, code, _cells = _notebook_sources()

    transform_block = code[code.index("df_orders_enriched = (") : code.index("TARGET_TABLES = [")]
    assert 'df_orders.alias("orders")' in transform_block
    assert '.join(df_customers.alias("customers"), on="customer_id", how="left")' in transform_block
    assert 'F.col("orders.country_code")' in transform_block
    assert 'F.col("customers.customer_country_code")' in transform_block
    assert 'F.coalesce(F.col("customers.country_code"), F.col("orders.country_code"))' not in transform_block
    assert '"order_amount_band"' in transform_block
    assert 'df_orders_summary = (' in transform_block
    assert '.groupBy("customer_segment", "country_code")' in transform_block

    target_user_block = code[code.index("TARGET_TABLES = [") : code.index("target_guardrail_results = run_table_guardrails(")]
    target_default_example = target_user_block[: target_user_block.index("# Optional advanced per-table overrides")]
    for expected_column in [
        '"order_id": "bigint"',
        '"customer_id": "bigint"',
        '"order_date": "date"',
        '"ingestion_ts": "timestamp"',
        '"status": "string"',
        '"order_amount": "double"',
        '"country_code": "string"',
        '"customer_country_code": "string"',
        '"_fabricops_run_id": "string",',
        '"_fabricops_pipeline_name": "string"',
        '"_fabricops_created_at": "string"',
    ]:
        assert expected_column in target_default_example
    assert '"order_amount_band": "string"' in target_default_example
    assert '"key": "orders_enriched"' in target_default_example
    assert '"key": "orders_summary"' in target_default_example
    assert '"table_name": "smoke_unified_orders_enriched"' in target_default_example
    assert '"table_name": "smoke_unified_orders_summary"' in target_default_example
    assert '"dataset_name"' not in target_default_example
    for hidden_beginner_field in ['"stage"', '"target_kind"', '"kind"']:
        assert hidden_beginner_field not in target_default_example

    assert "TARGET_TABLES, TARGET_CONFIG_BY_KEY = prepare_pipeline_table_configs(" in code
    assert 'table_role="target"' in code


def test_guardrails_stop_before_transform_and_writes_via_run_table_guardrails_flag():
    """Verify guardrails stop before transform and writes via run table guardrails flag."""
    _markdown, code, _cells = _notebook_sources()

    source_guardrails = code.index("source_guardrail_results = run_table_guardrails(")
    source_stop_flag = code.index("stop_on_failure=True", source_guardrails)
    transform = code.index("df_orders_enriched = (")
    target_prepare = code.index("TARGET_TABLES, TARGET_CONFIG_BY_KEY = prepare_pipeline_table_configs(")
    target_guardrails = code.index("target_guardrail_results = run_table_guardrails(")
    target_stop_flag = code.index("stop_on_failure=True", target_guardrails)
    target_write = code.index("target_write_status = {}")

    assert source_guardrails < source_stop_flag < transform < target_prepare < target_guardrails < target_stop_flag < target_write
    assert "source_guardrail_display = display_guardrail_results(" in code
    assert "display(source_guardrail_display)" in code
    assert "target_guardrail_display = display_guardrail_results(" in code
    assert "display(target_guardrail_display)" in code

    for runtime_alias in [
        'source_schema_results = source_guardrail_results["schema_results"]',
        'source_freshness_results = source_guardrail_results["freshness_results"]',
        'source_stability_results = source_guardrail_results["stability_results"]',
        'source_dq_results = source_guardrail_results["dq_results"]',
        'source_evidence_definitions = source_guardrail_results["evidence_definitions"]',
        'target_schema_results = target_guardrail_results["schema_results"]',
        'target_freshness_results = target_guardrail_results["freshness_results"]',
        'target_stability_results = target_guardrail_results["stability_results"]',
        'target_dq_results = target_guardrail_results["dq_results"]',
        'target_evidence_definitions = target_guardrail_results["evidence_definitions"]',
    ]:
        assert runtime_alias in code


def test_explicit_target_writes_use_prepared_target_configs_and_lakehouse_helper():
    """Verify explicit target writes use prepared target configs and lakehouse helper."""
    _markdown, code, _cells = _notebook_sources()

    write_block = code[code.index("target_write_options =") : code.index("LINEAGE_RELATIONSHIPS = [")]
    active_write_lines = "\n".join(line for line in write_block.splitlines() if not line.lstrip().startswith("#"))

    assert "for target_config in TARGET_TABLES:" not in write_block
    assert "write_lakehouse_table(" in write_block
    assert "write_warehouse_table(" in write_block
    assert "TARGET_LAYER_SCHEMAS" not in code
    assert 'orders_enriched_target = TARGET_CONFIG_BY_KEY["orders_enriched"]' in write_block
    assert 'orders_summary_target = TARGET_CONFIG_BY_KEY["orders_summary"]' in write_block
    assert 'orders_enriched_target["df"]' in write_block
    assert 'orders_summary_target["df"]' in write_block
    assert 'df_orders_enriched' not in active_write_lines
    assert 'df_orders_summary' not in active_write_lines
    for prepared_field in [
        '["target_layer"]',
        '["target_name"]',
        '.get("schema")',
        '.get("write_mode", "overwrite")',
        '.get("partition_by")',
        '.get("repartition_by")',
        '.get("options", target_write_options)',
    ]:
        assert prepared_field in write_block
    assert 'display(target_write_status)' in write_block
    assert "Optional warehouse example" in write_block
    assert "not part of the default happy path" in write_block
    assert "write_target_tables" not in write_block
    assert "Unsupported target kind" not in write_block


def test_each_default_target_config_has_matching_explicit_write_call():
    """Verify each default target config has matching explicit write call."""
    _markdown, code, _cells = _notebook_sources()

    target_user_block = code[code.index("TARGET_TABLES = [") : code.index("target_guardrail_results = run_table_guardrails(")]
    write_block = code[code.index("target_write_options =") : code.index("LINEAGE_RELATIONSHIPS = [")]
    target_keys = re.findall(r'"key": "([^"]+)"', target_user_block)

    assert target_keys == ["orders_enriched", "orders_summary"]
    for target_key in target_keys:
        variable_name = f"{target_key}_target"
        assert f'{variable_name} = TARGET_CONFIG_BY_KEY["{target_key}"]' in write_block
        assert f'target_write_status["{target_key}"]' in write_block


def test_lineage_and_runtime_summary_still_use_package_evidence_outputs():
    """Verify lineage and runtime summary still use package evidence outputs."""
    _markdown, code, _cells = _notebook_sources()

    assert "write_pipeline_lineage(" in code
    assert "write_pipeline_run_summary(" in code
    assert 'source_definitions=source_evidence_definitions' in code
    assert 'target_definitions=target_evidence_definitions' in code
    assert 'dataset_name=PRIMARY_TARGET_CONFIG["dataset_name"]' in code
    assert '"sources": ["orders", "customers"]' in code
    assert '"targets": ["orders_enriched", "orders_summary"]' in code
    assert "METADATA_PIPELINE_RUNS" in _markdown



def test_pipeline_template_uses_profile_mode_not_load_behavior():
    """Verify pipeline template uses the clean profile_mode contract."""
    _markdown, code, _cells = _notebook_sources()

    assert '"profile_mode"' in code
    assert "load_behavior" not in code

def test_pipeline_template_smoke_keeps_guardrails_inline_per_table():
    """Verify pipeline template smoke keeps guardrails inline per table."""
    _markdown, code, _cells = _notebook_sources()

    assert "DEFAULT_SOURCE_GUARDRAILS" not in code
    assert "DEFAULT_TARGET_GUARDRAILS_AND_WRITE_OPTIONS" not in code

    source_block = code[code.index("SOURCE_TABLES = [") : code.index("SOURCE_TABLES, SOURCE_CONFIG_BY_KEY = prepare_pipeline_table_configs(")]
    target_block = code[code.index("TARGET_TABLES = [") : code.index("TARGET_TABLES, TARGET_CONFIG_BY_KEY = prepare_pipeline_table_configs(")]

    for source_key in ['"key": "orders"', '"key": "customers"']:
        source_entry_start = source_block.index(source_key)
        source_entry = source_block[source_entry_start : source_block.find("    },", source_entry_start)]
        for field in [
            '"schema_preset"',
            '"profile_mode"',
            '"freshness_column"',
            '"freshness_max_lag_days"',
            '"freshness_severity"',
            '"dq_preset"',
            '"distribution_columns"',
            '"exclude_columns"',
            '"expected_schema"',
        ]:
            assert field in source_entry

    for target_key in ['"key": "orders_enriched"', '"key": "orders_summary"']:
        target_entry_start = target_block.index(target_key)
        target_entry = target_block[target_entry_start : target_block.find("    },", target_entry_start)]
        for field in [
            '"write_mode"',
            '"profile_mode"',
            '"schema"',
            '"schema_preset"',
            '"freshness_column"',
            '"freshness_max_lag_days"',
            '"freshness_severity"',
            '"dq_preset"',
            '"distribution_columns"',
            '"exclude_columns"',
            '"expected_schema"',
        ]:
            assert field in target_entry
