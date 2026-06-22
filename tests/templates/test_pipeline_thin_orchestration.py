"""Contract tests for the 02_pipeline notebook template."""

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


def test_pipeline_notebook_uses_existing_public_helpers_without_pr_only_wrappers():
    """Verify the template uses existing FabricOps helpers and no invented wrappers."""
    markdown, code, _ = _notebook_sources()

    for helper in [
        "prepare_pipeline_table_configs",
        "run_table_guardrails",
        "write_lakehouse_table",
        "write_pipeline_lineage",
        "write_pipeline_run_summary",
        "widget_author_schema_freshness_profile_rules",
        "widget_author_dq_rules",
        "widget_enrich_table_metadata",
        "widget_review_guardrail_governance",
    ]:
        assert helper in code

    for forbidden in [
        "prepare_source_table_configs",
        "prepare_target_table_configs",
        "write_target_tables",
        "write_targets_parallel",
        "guardrail_summary",
        "stop_if_any_guardrail_failed",
        "build_guardrail_evidence_definitions",
        "def run_table_guardrails(",
        "validate_schema(",
        "validate_schema_rule(",
    ]:
        assert forbidden not in code

    assert "widget-led" in markdown or "widgets" in markdown


def test_pipeline_agreement_selector_registers_notebook_context():
    """Verify pipeline startup selects and registers agreement context."""
    _markdown, code, _cells = _notebook_sources()

    assert "PIPELINE = start_pipeline_run(" in code
    start_block = code[code.index("PIPELINE = start_pipeline_run(") : code.index("# SOURCE AREA") if "# SOURCE AREA" in code else code.index("source_table = ")]
    assert 'notebook_type="02_pipeline"' in start_block
    assert "select_agreement=True" in start_block
    assert "register_notebook=True" in start_block
    assert "AGREEMENT_ID" not in code
    assert "NOTEBOOK_REGISTRY_ID" not in code

def test_pipeline_notebook_contains_widget_led_flow_sections():
    """Verify the template documents the intended simplified flow."""
    markdown, _code, _cells = _notebook_sources()
    expected_sections = [
        "## 1. Run `00_env_config`",
        "## 2. Import required functions",
        "## 3. Select agreement and capture run context",
        "## Optional bootstrap from Warehouse to Source Lakehouse Delta",
        "## 4. USER EDIT SECTION — read source DataFrames",
        "## 5. USER EDIT SECTION — register source DataFrames only",
        "## 6. Profile source data",
        "## 7. USER EDIT SECTION — transform source DataFrames into pipeline outputs",
        "## 8. USER EDIT SECTION — register pipeline outputs only",
        "## 9. Profile pipeline outputs",
        "## 10. Optional enrichment and guardrail widgets",
        "## 11. Guardrail enforcement gate",
        "## 12. USER EDIT SECTION — configure output write settings",
        "## 13. Write pipeline output Lakehouse tables",
        "## 14. Optional warehouse write example",
        "## 15. USER EDIT SECTION — lineage relationships",
        "## 16. Write lineage metadata",
        "## 17. Write runtime summary",
    ]
    for section in expected_sections:
        assert section in markdown

    assert "Do not define schema, freshness, profile behaviour, DQ" in markdown
    assert "If any blocking source or pipeline output guardrail fails" in markdown
    assert "Write settings belong after the guardrail gate" in markdown


def test_pipeline_notebook_contains_disabled_warehouse_bootstrap_guidance():
    """Verify the Warehouse bootstrap example is explicit, safe, and disabled."""
    markdown, code, _cells = _notebook_sources()
    bootstrap_block = code[code.index("RUN_WAREHOUSE_TO_LAKEHOUSE_BOOTSTRAP = False") : code.index("source_table = ")]

    assert "Optional bootstrap from Warehouse to Source Lakehouse Delta" in markdown
    assert "Lakehouse Delta for Spark processing" in markdown
    assert "Warehouse connector path" in markdown
    assert "performance impact for large tables" in markdown
    assert "Warehouse → Source Lakehouse Delta → PySpark transforms → Unified/Product Delta → optional Warehouse publish" in markdown
    assert "RUN_WAREHOUSE_TO_LAKEHOUSE_BOOTSTRAP = False" in bootstrap_block
    for setting in [
        "WAREHOUSE_TARGET",
        "WAREHOUSE_SCHEMA",
        "WAREHOUSE_TABLE",
        "SOURCE_LAKEHOUSE_TARGET",
        "SOURCE_LAKEHOUSE_TABLE",
        "SOURCE_LAKEHOUSE_SCHEMA",
        "PARALLEL_LOAD_COLUMN",
        "LOAD_MODE",
        "LOWER_BOUND",
        "UPPER_BOUND",
        "CHUNK_SIZE",
        "OUTPUT_PARTITION_COLUMNS",
    ]:
        assert setting in bootstrap_block

    for helper in [
        "read_warehouse_query(",
        "read_warehouse_table(",
        "write_lakehouse_table(",
    ]:
        assert helper in bootstrap_block

    assert "if not PARALLEL_LOAD_COLUMN:" in bootstrap_block
    assert "Set PARALLEL_LOAD_COLUMN before running Warehouse to Lakehouse bootstrap" in bootstrap_block
    assert "Only use this for small reference or ad hoc tables" in bootstrap_block
    assert "use chunked incremental loading or Fabric Copy activity" in bootstrap_block
    assert "not direct Warehouse reads" in bootstrap_block
    assert "read_data(" not in code
    assert "write_data(" not in code
    assert 'format="warehouse"' not in code
    assert "format = \"warehouse\"" not in code


def test_source_loading_uses_read_lakehouse_table():
    """Verify source loading examples use the read_lakehouse_table orchestrator."""
    _markdown, code, _cells = _notebook_sources()

    load_block = code[code.index("df_orders = read_lakehouse_table(") : code.index("SOURCE_TABLES = [")]
    assert "read_lakehouse_table(" in load_block
    for low_level_helper in [
        "read_warehouse_table(",
    ]:
        assert low_level_helper not in load_block
    for helper in [
        'read_lakehouse_csv(',
        'read_lakehouse_parquet(',
        'read_lakehouse_excel(',
        'read_warehouse_query(',
    ]:
        assert helper in load_block
    assert '"source"' in load_block
    assert '"demo_src_orders_happy"' in load_block
    assert '"demo_src_customers_happy"' in load_block
    assert "spark_session=spark" in load_block
    assert 'schema="DemoTest"' in load_block


def test_source_and_target_registration_are_key_and_dataframe_only():
    """Verify registration cells no longer contain guardrail authoring knobs."""
    _markdown, code, _cells = _notebook_sources()

    source_block = code[code.index("SOURCE_TABLES = [") : code.index("source_profile_results = run_table_guardrails(")]
    target_block = code[code.index("TARGET_TABLES = [") : code.index("target_profile_results = run_table_guardrails(")]

    for block, keys in [(source_block, ["orders", "customers"]), (target_block, ["orders_enriched", "orders_summary"] )]:
        for key in keys:
            assert f'"key": "{key}"' in block
        assert '"df":' in block
        for field in [
            '"schema_preset"',
            '"profile_mode"',
            '"freshness_column"',
            '"freshness_max_lag_days"',
            '"dq_preset"',
            '"distribution_columns"',
            '"exclude_columns"',
            '"expected_schema"',
            '"write_mode"',
            '"schema"',
            '"target_name"',
        ]:
            assert field not in block

    assert "SOURCE_TABLES, SOURCE_CONFIG_BY_KEY = prepare_pipeline_table_configs(" in source_block
    assert "TARGET_TABLES, TARGET_CONFIG_BY_KEY = prepare_pipeline_table_configs(" in target_block
    assert 'table_role="source"' in source_block
    assert 'table_role="target"' in target_block


def test_transform_and_target_write_settings_are_separate_from_registration():
    """Verify business transform output is registered before write settings are applied."""
    _markdown, code, _cells = _notebook_sources()

    transform = code.index("df_orders_enriched = (")
    target_register = code.index("TARGET_TABLES = [", transform)
    target_profile = code.index("target_profile_results = run_table_guardrails(", target_register)
    widget_step = code.index("selected_guardrail_target = widget_select_guardrail_target(", target_profile)
    enforcement_gate = code.index("source_enforcement_results = run_table_guardrails(", widget_step)
    write_settings = code.index("TARGET_WRITE_SETTINGS = {", enforcement_gate)
    target_write = code.index("target_write_status = {}", write_settings)

    assert transform < target_register < target_profile < widget_step < enforcement_gate < write_settings < target_write
    assert '"target_name": "demo_unified_orders_enriched"' in code[write_settings:target_write]
    assert '"write_mode": "overwrite"' in code[write_settings:target_write]
    assert '"options": {"overwriteSchema": "true"}' in code[write_settings:target_write]


def test_guardrail_gate_stops_before_target_writes():
    """Verify source and target enforcement block before write settings and writes."""
    _markdown, code, _cells = _notebook_sources()

    source_enforcement = code.index("source_enforcement_results = run_table_guardrails(")
    target_enforcement = code.index("target_enforcement_results = run_table_guardrails(", source_enforcement)
    write_settings = code.index("TARGET_WRITE_SETTINGS = {", target_enforcement)
    target_write = code.index("target_write_status = {}", write_settings)

    assert source_enforcement < target_enforcement < write_settings < target_write
    assert "run_table_guardrails stops the notebook when blocking source guardrails fail" in code
    assert "run_table_guardrails stops the notebook when blocking target guardrails fail" in code
    assert "display_guardrail_results(source_enforcement_results" in code
    assert "display_guardrail_results(target_enforcement_results" in code


def test_explicit_target_writes_use_prepared_target_configs_and_real_helpers():
    """Verify writes use prepared target configs and the existing write helpers."""
    _markdown, code, _cells = _notebook_sources()

    write_block = code[code.index("target_write_status = {}") : code.index("LINEAGE_RELATIONSHIPS = [")]
    assert "write_lakehouse_table(" in write_block
    assert "write_targets_parallel" not in write_block
    assert "TARGET_CONFIG_BY_KEY.items()" in write_block
    for prepared_field in [
        '["df"]',
        '.get("target_layer", "unified")',
        '["target_name"]',
        '.get("schema")',
        '.get("write_mode", "overwrite")',
        '.get("partition_by")',
        '.get("repartition_by")',
        '.get("options")',
    ]:
        assert prepared_field in write_block


def test_optional_warehouse_write_example_uses_warehouse_callable():
    """Verify optional Warehouse publication uses the explicit warehouse writer."""
    _markdown, code, _cells = _notebook_sources()
    warehouse_block = code[code.index("# orders_summary_target = TARGET_CONFIG_BY_KEY") : code.index("LINEAGE_RELATIONSHIPS = [")]

    assert "# write_warehouse_table(" in warehouse_block
    assert 'target="warehouse"' in warehouse_block
    assert 'format="warehouse"' not in warehouse_block
    assert "write_lakehouse_table(\n#     orders_summary_target" not in warehouse_block


def test_lineage_and_runtime_summary_still_use_package_evidence_outputs():
    """Verify lineage and runtime summary remain package evidence writes."""
    markdown, code, _cells = _notebook_sources()

    assert "write_pipeline_lineage(" in code
    assert "write_pipeline_run_summary(" in code
    assert '"sources": ["orders", "customers"]' not in code
    assert '"targets": ["orders_enriched", "orders_summary"]' not in code
    assert "source_profile_results" in code
    assert "target_profile_results" in code
    assert "source_enforcement_results" in code
    assert "target_enforcement_results" in code
    assert "source_guardrail_results=source_enforcement_results" in code
    assert "target_guardrail_results=target_enforcement_results" in code
    assert "runtime summary" in markdown.lower()


def test_pipeline_template_uses_widget_authoring_not_inline_schema_config():
    """Verify schema and DQ authoring moved to widgets instead of registration dictionaries."""
    _markdown, code, _cells = _notebook_sources()

    assert "widget_author_schema_freshness_profile_rules(" in code
    assert "widget_author_dq_rules(" in code
    assert "load_behavior" not in code
    registration_text = code[code.index("SOURCE_TABLES = [") : code.index("TARGET_WRITE_SETTINGS = {")]
    for forbidden in ['"schema_preset"', '"expected_schema"', '"dq_preset"']:
        assert forbidden not in registration_text


def test_default_target_config_has_matching_write_settings():
    """Verify each target key has a matching post-gate write setting."""
    _markdown, code, _cells = _notebook_sources()

    target_user_block = code[code.index("TARGET_TABLES = [") : code.index("TARGET_TABLES, TARGET_CONFIG_BY_KEY = prepare_pipeline_table_configs(")]
    write_settings_block = code[code.index("TARGET_WRITE_SETTINGS = {") : code.index("for key, write_settings")]
    target_keys = re.findall(r'"key": "([^"]+)"', target_user_block)

    assert target_keys == ["orders_enriched", "orders_summary"]
    for target_key in target_keys:
        assert f'"{target_key}": {{' in write_settings_block
        assert "target_name" in write_settings_block
        assert "write_mode" in write_settings_block


def test_run_table_guardrails_calls_use_template_friendly_defaults():
    """Verify run_table_guardrails calls use mode and table role defaults."""
    _markdown, _code, cells = _notebook_sources()
    calls = []
    for cell in cells:
        tree = ast.parse("\n".join(line for line in cell.splitlines() if not line.lstrip().startswith("%")))
        calls.extend(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "run_table_guardrails"
        )

    assert len(calls) == 4
    expected = [("source", "profile"), ("target", "profile"), ("source", "enforce"), ("target", "enforce")]
    for call, (table_role, mode) in zip(calls, expected):
        assert len(call.args) == 1
        keyword_values = {keyword.arg: keyword.value for keyword in call.keywords}
        assert isinstance(keyword_values["table_role"], ast.Constant)
        assert keyword_values["table_role"].value == table_role
        assert isinstance(keyword_values["mode"], ast.Constant)
        assert keyword_values["mode"].value == mode
        assert "run_id" not in keyword_values
        assert "spark_session" not in keyword_values
        assert "metadata_schema" not in keyword_values
        assert "stop_on_failure" not in keyword_values

def test_template_examples_use_default_context_not_framework_plumbing():
    """Verify common template examples do not expose repeated framework plumbing."""
    _markdown, code, _cells = _notebook_sources()
    forbidden = [
        "config=CONFIG",
        "env=ENV",
        "context=custom_context",
        "workspace_id=",
        "lakehouse_id=",
        "read_lakehouse_table(CONFIG",
        "write_lakehouse_table(\n        CONFIG",
    ]
    bootstrap_block = code[: code.index("source_table = ")]
    read_config_block = code[code.index("source_table = ") : code.index("df_orders = read_lakehouse_table(")]
    load_block = code[code.index("df_orders = read_lakehouse_table(") : code.index("SOURCE_TABLES = [")]

    assert all(item not in code for item in forbidden)
    assert "source_table" not in bootstrap_block
    assert "customer_table" not in bootstrap_block
    assert "source_table" in read_config_block
    assert "customer_table" in read_config_block
    assert "target_table = " not in code
    assert "primary_key = " not in code
    assert 'read_lakehouse_csv(' in load_block
    assert 'read_lakehouse_excel(' in load_block
    assert 'read_lakehouse_parquet(' in load_block
    assert 'read_warehouse_query(' in load_block
