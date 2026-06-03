"""Regression checks for copy-ready notebook-template package API usage."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import fabricops_kit

TEMPLATES = Path("templates/notebooks")
DEPENDENT_TEMPLATE_NAMES = (
    "01_da_agreement_template.ipynb",
    "02_ex_agreement_topic.ipynb",
    "03_pc_agreement_pipeline_template.ipynb",
    "04_gov_agreement_dataset_table.ipynb",
)


def _code(name: str) -> str:
    notebook = json.loads((TEMPLATES / name).read_text(encoding="utf-8"))
    return "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"] if cell["cell_type"] == "code")


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
    register = next(node for node in calls if _name(node.func) == "register_current_notebook")
    assert "metadata_path" in {keyword.arg for keyword in register.keywords}
    assert "metadata_store" not in {keyword.arg for keyword in register.keywords}

    source_read = next(
        node for node in calls
        if _name(node.func) == "read_lakehouse_table"
        and len(node.args) >= 4
        and _name(node.args[2]) == "source"
        and _name(node.args[3]) == "table_name"
    )
    assert [_name(argument) for argument in source_read.args[:4]] == ["CONFIG", "ENV", "source", "table_name"]
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
    assert 'AGREEMENT_METADATA_SETUP[\'tables\']' in code
    assert 'AGREEMENT_METADATA_SETUP[\'status\']' in code
    assert 'AGREEMENT_METADATA_SETUP[\'message\']' in code
    assert 'AGREEMENT_METADATA_SETUP[\'active_steward_count\']' in code
    assert 'VALIDATION_MODE == "strict" and AGREEMENT_METADATA_SETUP["status"] != "ready"' in code


def test_01_da_imports_only_high_level_agreement_app_helper():
    imported = _fabricops_imports("01_da_agreement_template.ipynb")
    assert imported <= set(fabricops_kit.__all__)
    assert imported == {"render_agreement_intake_app"}
    assert not (imported & REMOVED_AGREEMENT_CALLABLES)


def test_01_da_renders_framework_managed_intake_app_without_notebook_callback():
    code = _code("01_da_agreement_template.ipynb")
    assert "%run 00_env_config" in code
    assert "from fabricops_kit import render_agreement_intake_app" in code
    assert "agreement_app = render_agreement_intake_app(" in code
    assert "spark=spark" in code
    assert "config=CONFIG" in code
    assert "env=ENV" in code
    assert "def on_commit_clicked" not in code
    assert ".on_click(" not in code


def test_public_all_exposes_small_supported_agreement_api_only():
    supported = {
        "render_agreement_intake_app",
        "render_data_steward_widget",
        "render_data_agreement_widget",
        "setup_data_agreement_tables",
        "select_agreement",
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


def test_downstream_templates_select_agreements_without_loading_internal_helper():
    for template, env_name in (
        ("02_ex_agreement_topic.ipynb", "ENV_NAME"),
        ("03_pc_agreement_pipeline_template.ipynb", "ENV_NAME"),
        ("04_gov_agreement_dataset_table.ipynb", "env_name"),
    ):
        code = _code(template)
        assert "load_agreements" not in code
        assert f"select_agreement(CONFIG, {env_name}, spark_session=spark)" in code


def test_generated_data_agreement_module_page_separates_supported_api_tiers():
    page = Path("docs/api/modules/data_agreement.md").read_text(encoding="utf-8")
    assert "## Intended notebook call flow" in page
    assert "## Primary notebook API" in page
    assert "## Optional advanced customization API" not in page
    assert "## Internal helpers" in page
    assert "### Internal workflow helpers" in page
    assert "### Private implementation helpers" in page
    assert "These non-exported helpers support framework internals and diagnostics." in page
    assert page.index("## Intended notebook call flow") < page.index("## Module manifest")
    assert "## Module overview badges" not in page
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


def test_02_ex_maps_selected_agreement_to_lightweight_versioned_schema():
    code = _code("02_ex_agreement_topic.ipynb")
    for field_name in (
        "agreement_id", "contract_version", "agreement_name", "domain",
        "business_purpose", "approved_usage", "steward_id", "custom_fields_json",
    ):
        assert f'"{field_name}"' in code
    assert 'custom_fields = json.loads(selected_agreement.get("custom_fields_json") or "{}")' in code
    assert '"custom_fields": custom_fields' in code
    for removed_physical_field in (
        "restricted_usage", "source_system", "refresh_frequency",
        "retention_expectation", "allowed_consumer_type", "expected_output",
        "department", "faculty",
    ):
        assert f'selected_agreement.get("{removed_physical_field}"' not in code
    assert "display(agreement_context)" in code
    assert r'business_context=f"Business purpose: {business_purpose}\nApproved usage: {approved_usage}"' in code
    assert "prompt_template=CONFIG.ai_prompt_config.dq_rule_suggestion_prompt_template" in code
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
    assert "from fabricops_kit import setup_data_agreement_tables" in code
    assert "AGREEMENT_METADATA_SETUP = setup_data_agreement_tables(" in code
    assert "spark=spark" in code
    assert "config=CONFIG" in code
    assert "env=ENV" in code
    assert "require_active_steward=False" in code


def test_03_pc_pipeline_template_does_not_import_or_call_load_config():
    assert "load_config" not in _code("03_pc_agreement_pipeline_template.ipynb")
