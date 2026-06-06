
"""Regression checks for copy-ready notebook-template package API usage."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.contract

import ast
import json
from pathlib import Path

import fabricops_kit

TEMPLATES = Path("templates/notebooks")
DEPENDENT_TEMPLATE_NAMES = (
    "01_da_agreement_template.ipynb",
    "02_ex_agreement_topic.ipynb",
    "03_pc_agreement_pipeline_template.ipynb",
    "04_gov_dataset_table.ipynb",
)


def _code(name: str) -> str:
    notebook = json.loads((TEMPLATES / name).read_text(encoding="utf-8"))
    return "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"] if cell["cell_type"] == "code")


def _template_text(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


def _tree(name: str) -> ast.Module:
    source = "\n".join(line for line in _code(name).splitlines() if not line.lstrip().startswith("%"))
    return ast.parse(source)


def _name(node: ast.AST) -> str | None:
    return node.id if isinstance(node, ast.Name) else node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def test_00_env_config_defines_env_name_alias():
    assert "ENV_NAME = ENV" in _code("00_env_config.ipynb")


def test_dependent_templates_run_fabric_config_bootstrap_directly():
    for name in DEPENDENT_TEMPLATE_NAMES:
        notebook = json.loads((TEMPLATES / name).read_text(encoding="utf-8"))
        code_cells = ["".join(cell.get("source", [])) for cell in notebook["cells"] if cell["cell_type"] == "code"]
        assert sum(line.strip() == "%run 00_env_config" for source in code_cells for line in source.splitlines()) == 1
        assert not any("# %run 00_env_config" in source for source in code_cells)
        assert not any("FabricOps config is not loaded" in source for source in code_cells)


def test_02_ex_imports_only_public_fabricops_kit_functions():
    imported = {
        alias.name
        for node in _tree("02_ex_agreement_topic.ipynb").body
        if isinstance(node, ast.ImportFrom) and node.module == "fabricops_kit"
        for alias in node.names
    }
    assert imported <= set(fabricops_kit.__all__)
    assert "_build_dq_rule_deactivation_metadata_df" not in imported


def test_02_ex_register_and_source_read_calls_match_public_signatures():
    calls = [node for node in ast.walk(_tree("02_ex_agreement_topic.ipynb")) if isinstance(node, ast.Call)]
    selector = next(node for node in calls if _name(node.func) == "widget_select_agreement")
    keyword_names = {keyword.arg for keyword in selector.keywords}
    assert "register_notebook" in keyword_names
    assert "spark_session" in keyword_names
    assert "metadata_path" not in keyword_names
    assert "metadata_store" not in keyword_names

    source_read = next(
        node for node in calls
        if _name(node.func) == "read_lakehouse_table"
        and len(node.args) >= 4
        and _name(node.args[2]) == "source"
        and _name(node.args[3]) == "table_name"
    )
    assert [_name(argument) for argument in source_read.args[:4]] == ["CONFIG", "ENV_NAME", "source", "table_name"]
    assert {_name(keyword.value) for keyword in source_read.keywords if keyword.arg == "spark_session"} == {"spark"}


def test_03_pc_warehouse_reads_match_public_signature():
    calls = [node for node in ast.walk(_tree("03_pc_agreement_pipeline_template.ipynb")) if isinstance(node, ast.Call) and _name(node.func) == "read_warehouse_table"]
    assert calls
    for call in calls:
        assert [_name(argument) for argument in call.args[:5]] in (
            ["CONFIG", "ENV_NAME", "SOURCE_LAYER", "dbo", "SOURCE_TABLE"],
            ["CONFIG", "ENV_NAME", "TARGET_LAYER", "dbo", "TARGET_TABLE"],
        )
        assert {_name(keyword.value) for keyword in call.keywords if keyword.arg == "spark_session"} == {"spark"}


REMOVED_AGREEMENT_CALLABLES = {
    "create_agreement_widgets",
    "_agreement_widget_specs",
    "_get_fabric_widgets",
    "_widget_dropdown",
    "_widget_text",
    "_build_agreement_record",
    "_normalise_widget_values",
    "_normalize_widget_values",
    "_read_agreement_widget_values",
    "_record_base",
    "_resolve_committed_at",
    "_safe_table_prefix",
    "_write_record",
    "_latest_distinct_agreements",
    "_agreement_option_label",
}


def _fabricops_imports(name: str) -> set[str]:
    return {
        alias.name
        for node in _tree(name).body
        if isinstance(node, ast.ImportFrom) and node.module == "fabricops_kit"
        for alias in node.names
    }


def test_00_env_config_exposes_shared_config_and_data_agreement_defaults():
    code = _code("00_env_config.ipynb")
    assert 'ENV = "dev"' in code
    assert "ENV_NAME = ENV" in code
    assert "DATA_AGREEMENT_CONFIG = DataAgreementConfig(" in code
    for configured_default in (
        "metadata_tables={",
        "steward_role_options=[",
        '"Data Owner"',
        '"Governance Reviewer"',
        "data_steward_widget={",
        "data_agreement_evidence",
        "METADATA_DATA_AGREEMENT_EVIDENCE",
        "data_agreement_widget={",
        '"custom_fields": [',
        '"key": "group"',
        '"key": "consumer_group"',
    ):
        assert configured_default in code
    assert "data_agreement_config=DATA_AGREEMENT_CONFIG" in code
    assert "CONFIG.path_config.paths[ENV]['metadata']" in code


def test_00_env_config_bootstraps_agreement_tables_and_reports_steward_readiness():
    code = _code("00_env_config.ipynb")
    assert "AGREEMENT_METADATA_SETUP = setup_data_agreement_tables(" in code
    assert "spark=spark" in code
    assert "config=CONFIG" in code
    assert "env=ENV" in code
    assert "require_active_steward=False" in code
    assert "CONFIG.path_config.paths[ENV]['unified'].name" in code
    assert "CONFIG.path_config.paths[ENV]['product'].name" in code
    assert "01_da metadata tables created/checked" in code
    assert "METADATA_DATA_AGREEMENT_EVIDENCE" in code
    assert 'AGREEMENT_METADATA_SETUP[\'tables\']' in code
    assert 'AGREEMENT_METADATA_SETUP[\'status\']' in code
    assert 'AGREEMENT_METADATA_SETUP[\'message\']' in code
    assert 'AGREEMENT_METADATA_SETUP[\'active_steward_count\']' in code
    assert 'VALIDATION_MODE == "strict" and AGREEMENT_METADATA_SETUP["status"] != "ready"' in code


def test_01_da_imports_only_public_agreement_layout_helpers():
    imported = _fabricops_imports("01_da_agreement_template.ipynb")
    assert imported <= set(fabricops_kit.__all__)
    assert imported == {
        "widget_render_agreement_evidence",
        "widget_render_agreement_intake_app",
        "widget_render_data_agreement",
        "widget_render_data_steward",
    }
    assert not (imported & REMOVED_AGREEMENT_CALLABLES)


def test_01_da_renders_framework_managed_ab_layouts_without_notebook_callback():
    code = _code("01_da_agreement_template.ipynb")
    assert "%run 00_env_config" in code
    assert "widget_render_agreement_intake_app" in code
    assert "agreement_app = widget_render_agreement_intake_app(" in code
    assert "steward_widget = widget_render_data_steward(" in code
    assert "agreement_widget = widget_render_data_agreement(" in code
    assert "evidence_widget = widget_render_agreement_evidence(" in code
    assert "spark=spark" in code
    assert "config=CONFIG" in code
    assert "env=ENV" in code
    assert "env_name=ENV" in code
    assert "def on_commit_clicked" not in code
    assert ".on_click(" not in code


def test_public_all_exposes_small_supported_agreement_api_only():
    supported = {
        "widget_render_agreement_intake_app",
        "widget_render_data_steward",
        "widget_render_data_agreement",
        "widget_render_agreement_evidence",
        "setup_data_agreement_tables",
        "widget_select_agreement",
        "get_selected_agreement",
    }
    helper_style_names = {
        "load_agreements", "ensure_metadata_tables", "get_data_steward_schema",
        "get_data_agreement_schema", "get_standard_runtime_audit_columns",
        "serialize_custom_fields", "deserialize_custom_fields", "render_custom_fields",
        "collect_custom_fields", "get_widget_visible_fields", "list_data_stewards",
        "list_data_agreements", "create_or_update_data_steward",
        "create_or_update_data_agreement", "create_agreement_form",
        "read_agreement_form", "collect_agreement_metadata", "commit_agreement_metadata",
    }
    exported = set(fabricops_kit.__all__)
    assert supported <= exported
    assert not (helper_style_names & exported)


def test_downstream_templates_widget_select_agreements_without_loading_internal_helper():
    for template in ("02_ex_agreement_topic.ipynb", "03_pc_agreement_pipeline_template.ipynb"):
        code = _code(template)
        assert "load_agreements" not in code
        assert "widget_select_agreement(" in code
        assert "register_notebook=True" in code


def test_04_gov_selects_catalogue_table_without_mandatory_agreement():
    code = _code("04_gov_dataset_table.ipynb")
    assert "load_agreements" not in code
    assert "widget_select_catalogue_table(CONFIG, env_name, spark_session=spark)" in code
    assert "get_selected_catalogue_table()" in code
    assert "widget_select_agreement(" not in code
    assert "get_selected_agreement" not in code
    assert "register_current_notebook" not in code
    assert "agreement_id" not in code
    assert "contract_version" not in code


def test_generated_data_agreement_module_page_separates_supported_api_tiers():
    page = Path("docs/api/modules/data_agreement.md").read_text(encoding="utf-8")
    assert "## Module purpose" in page
    assert "## Public callables" in page
    assert "## Module overview badges" in page
    assert "## Module manifest" in page
    assert page.index("## Module purpose") < page.index("## Module manifest")
    for helper_name in (
        "_agreement_dropdown_options",
        "_latest_agreement_versions",
        "_load_active_data_steward_profiles",
        "_next_minor_version",
        "_parse_contract_version",
        "_resolve_agreement_identity",
        "_serialize_custom_fields",
        "_list_data_stewards",
    ):
        assert f"internal/data_agreement/{helper_name}/" in page


def test_generated_function_manifest_excludes_removed_agreement_callables():
    manifest = json.loads(Path("docs/reference/function-manifest.json").read_text(encoding="utf-8"))
    manifest_text = json.dumps(manifest)
    for callable_name in REMOVED_AGREEMENT_CALLABLES:
        assert callable_name not in manifest_text


def test_02_ex_includes_excel_option_without_claiming_csv_skiprows_support():
    code = _code("02_ex_agreement_topic.ipynb")
    template_text = _template_text("02_ex_agreement_topic.ipynb")
    assert "read_lakehouse_excel" in code
    assert "# Option E: Lakehouse Excel file" in template_text
    assert "#     skiprows=2," in template_text
    assert "#     header=0," in template_text
    assert "skiprows=2 skips the first two rows" in template_text
    assert "header=0 means the first remaining row becomes the column header" in template_text
    assert "Excel reads are intended for small reference files, mapping files, and manually maintained inputs" in template_text
    assert "read_lakehouse_csv does not currently support" in template_text
    csv_section = template_text.split("# Option C: Lakehouse CSV file", 1)[1].split("# Option D: Lakehouse Parquet file", 1)[0]
    assert "skiprows=" not in csv_section


def test_02_ex_uses_widget_registration_without_advanced_metadata_sections():
    code = _code("02_ex_agreement_topic.ipynb")
    template_text = _template_text("02_ex_agreement_topic.ipynb")
    assert "register_notebook=True" in code
    assert "Register notebook" not in code  # button label is owned by the package widget, not the template
    assert "register_current_notebook(" not in code
    assert "agreement_context =" not in code
    assert "display(agreement_context)" not in code
    assert "custom_fields_json" not in code
    assert "get_selected_agreement" not in code
    assert "selected_agreement" not in code
    for advanced_section in (
        "Agreement-aware read-only metadata",
        "Existing approved DQ rules",
        "Existing governance/classification metadata",
        "Existing notebook registry / prior evidence",
        "AI-assisted DQ flow",
        "Findings",
        "Handoff notes",
    ):
        assert advanced_section not in template_text
    for removed_callable in (
        "load_dq_rules",
        "draft_dq_rules",
        "run_dq_rule_review_widget",
        "get_dq_review_results",
        "write_dq_rules",
        "widget_review_dq_rule_deactivations",
        "load_governance",
        "load_notebook_registry",
    ):
        assert removed_callable not in code
    assert "prompt_template=CONFIG.ai_prompt_config.dq_rule_suggestion_prompt_template" not in code
    assert "CONFIG.ai_prompt_config.dq_rule_candidate_template" not in code


def test_00_env_config_keeps_bootstrap_flow_without_load_config():
    code = _code("00_env_config.ipynb")
    assert "load_config" not in code
    assert "RUN_CONTEXT = setup_notebook(" in code
    assert 'VALIDATION_MODE = "warn"' in code
    assert 'REQUIRED_TARGETS = ["source", "unified", "product", "metadata"]' in code
    assert "DATA_STEWARD_REQUIRED_FIELDS" not in code
    assert "DATA_STEWARD_SYSTEM_FIELDS" not in code
    assert "validate_data_agreement_prerequisites" not in code
    assert "from fabricops_kit import setup_data_agreement_tables, setup_notebook_registry_table" in code
    assert "AGREEMENT_METADATA_SETUP = setup_data_agreement_tables(" in code
    assert "NOTEBOOK_REGISTRY_SETUP = setup_notebook_registry_table(" in code
    assert "spark=spark" in code
    assert "config=CONFIG" in code
    assert "env=ENV" in code
    assert "require_active_steward=False" in code



def test_03_pc_uses_agreement_widget_registration_without_manual_registration():
    code = _code("03_pc_agreement_pipeline_template.ipynb")
    tree = _tree("03_pc_agreement_pipeline_template.ipynb")
    imported = {
        alias.name
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module == "fabricops_kit"
        for alias in node.names
    }
    assert "widget_select_agreement" in imported
    assert "get_selected_agreement" in imported
    assert "current_notebook_active_registrations" in imported
    assert "build_runtime_audit_fields" in imported
    assert "add_runtime_audit_columns" not in imported
    assert "standardize_columns" not in imported
    assert "register_current_notebook" not in imported
    assert "register_current_notebook(" not in code
    assert "get_selected_agreement(" in code
    assert "current_notebook_active_registrations(" in code
    assert "custom_fields_json" not in code

    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and _name(node.func) == "widget_select_agreement"]
    assert len(calls) == 1
    selector = calls[0]
    keyword_values = {keyword.arg: _name(keyword.value) for keyword in selector.keywords}
    assert [_name(argument) for argument in selector.args[:2]] == ["CONFIG", "ENV_NAME"]
    raw_keywords = {keyword.arg: keyword.value for keyword in selector.keywords}
    assert keyword_values["spark_session"] == "spark"
    assert isinstance(raw_keywords["register_notebook"], ast.Constant)
    assert raw_keywords["register_notebook"].value is True
    assert keyword_values["notebook_type"] == "03_pc"
    assert keyword_values["environment_name"] == "ENV_NAME"
    assert keyword_values["dataset_name"] == "DATASET_NAME"
    assert keyword_values["table_name"] == "TABLE_NAME"
    assert keyword_values["topic"] == "TOPIC"
    assert keyword_values["pipeline_name"] == "PIPELINE_NAME"


def test_03_pc_pipeline_template_does_not_import_or_call_load_config():
    assert "load_config" not in _code("03_pc_agreement_pipeline_template.ipynb")


def test_03_pc_base_pipeline_defers_governance_enforcement():
    code = _code("03_pc_agreement_pipeline_template.ipynb")
    template_text = _template_text("03_pc_agreement_pipeline_template.ipynb")
    for removed in (
        "METADATA_DQ_RULES",
        "enforce_dq",
        "DQ_PUBLISH_MODE",
        "same_table_with_flags",
        "split_valid_quarantine",
        "fail_on_invalid",
        "QUARANTINE",
        "build_handover",
        "render_handover_markdown",
        "build_lineage_handover_markdown",
        "PUBLISHED_PROFILE",
    ):
        assert removed not in code
    assert "METADATA_DATA_CATALOGUE" in code
    assert "METADATA_DATA_CATALOGUE_COLUMN" not in code
    assert ".withColumn(\"metadata_table_key\"" in code
    assert ".withColumn(\"metadata_column_key\"" in code
    assert ".withColumn(\"profile_status\", F.lit(\"success\"))" in code
    assert "METADATA_DATA_LINEAGE_TABLE" in code
    assert 'write_lakehouse_table(lineage_df, CONFIG, ENV_NAME, "metadata", LINEAGE_TABLE' in code
    assert "read_lakehouse_csv" in code
    assert "read_lakehouse_parquet" in code
    assert "build_runtime_audit_fields(" in code
    assert "add_runtime_audit_columns" not in code
    assert "standardize_columns" not in code
    assert "df_output = (" in code
    assert '.withColumn("_pipeline_run_id", F.lit(RUN_ID))' in code
    assert '.withColumn("_loaded_by", F.lit(audit_fields.get("_committed_by", "")))' in code
    for specialized in (
        "_business_key_hash",
        "_row_hash",
        "_partition_bucket",
        "_sample_bucket",
        "_watermark_value",
        "_row_ingest_id",
        "bucket_column=",
    ):
        assert specialized not in code
    assert "Optional large table write pattern" in template_text
    assert "partition_by=LARGE_TABLE_PARTITION_COLUMNS" in code
    assert "repartition_by=LARGE_TABLE_REPARTITION_BY" in code
    assert "# LARGE_TABLE_REPARTITION_BY = 2000" in code
    assert "does not read DQ rules" in template_text


def test_00_env_config_bootstraps_governance_metadata_tables():
    code = _code("00_env_config.ipynb")
    assert "setup_governance_metadata_tables" in code
    assert "GOVERNANCE_METADATA_SETUP = setup_governance_metadata_tables(" in code
    for table in (
        "METADATA_DATA_CATALOGUE",
        "METADATA_COLUMN_CONTEXT",
        "METADATA_DQ_RULES",
        "METADATA_COLUMN_CLASSIFICATION",
        "METADATA_DATA_LINEAGE_TABLE",
    ):
        assert table in code or table in fabricops_kit.get_governance_metadata_schemas()


def test_removed_catalogue_and_profile_tables_are_not_referenced():
    haystack = "\n".join(path.read_text(encoding="utf-8") for root in [Path("src"), Path("templates"), Path("docs"), Path("scripts")] for path in root.rglob("*.py") if root.name != "templates")
    haystack += "\n".join(path.read_text(encoding="utf-8") for path in Path("templates/notebooks").glob("*.ipynb"))
    for removed in ("METADATA_PROFILE_ROWS", "METADATA_DATA_CATALOGUE_TABLE", "METADATA_DATA_CATALOGUE_COLUMN", "METADATA_DATA_CONTRACT"):
        assert removed not in haystack


def test_04_gov_imports_only_supported_public_apis_and_does_not_enforce_rules():
    imported = _fabricops_imports("04_gov_dataset_table.ipynb")
    assert imported <= set(fabricops_kit.__all__)
    code = _code("04_gov_dataset_table.ipynb")
    assert "METADATA_DATA_CATALOGUE" in code or "load_catalogue_profile_rows" in code
    assert "enforce_dq" not in code
    assert "assert_dq_passed" not in code
