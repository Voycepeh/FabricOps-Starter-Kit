"""Regression checks for copy-ready notebook-template package API usage."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import fabricops_kit

TEMPLATES = Path("templates/notebooks")


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
        "source_systems=(",
        "refresh_frequencies=(",
        "allowed_consumer_types=(",
        "expected_outputs=(",
        "renewal_options=(",
        "default_values={",
    ):
        assert configured_default in code
    assert "data_agreement_config=DATA_AGREEMENT_CONFIG" in code
    assert 'CONFIG.path_config.paths[ENV]["metadata"]' in json.loads((TEMPLATES / "00_env_config.ipynb").read_text(encoding="utf-8"))["cells"][1]["source"][2]


def test_00_env_config_bootstraps_agreement_tables_and_reports_steward_readiness():
    code = _code("00_env_config.ipynb")
    assert "setup_data_agreement_tables(spark=spark, config=CONFIG, env=ENV)" in code
    assert "load_active_data_steward_profiles(spark=spark, config=CONFIG, env=ENV)" in code
    assert "CONFIG.path_config.paths[ENV]['unified'].name" in code
    assert "CONFIG.path_config.paths[ENV]['product'].name" in code
    assert "agreement metadata tables created/checked" in code
    assert "01_da cannot render until real steward rows are added with is_active = true" in code
    assert 'VALIDATION_MODE == "strict" and STEWARD_READINESS_STATUS != "ready"' in code
    assert "No fake steward profiles are seeded." in code


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
    for lower_level_helper in (
        "create_agreement_form",
        "read_agreement_form",
        "collect_agreement_metadata",
        "commit_agreement_metadata",
        "load_agreements",
        "setup_data_agreement_tables",
    ):
        assert lower_level_helper not in code
        assert lower_level_helper in fabricops_kit.__all__


def test_generated_function_manifest_excludes_removed_agreement_callables():
    manifest = json.loads(Path("docs/reference/function-manifest.json").read_text(encoding="utf-8"))
    manifest_text = json.dumps(manifest)
    for callable_name in REMOVED_AGREEMENT_CALLABLES:
        assert callable_name not in manifest_text


def test_02_ex_maps_selected_agreement_to_current_versioned_schema():
    code = _code("02_ex_agreement_topic.ipynb")
    for field_name in (
        "agreement_id",
        "contract_version",
        "agreement_name",
        "business_purpose",
        "approved_usage",
        "restricted_usage",
        "data_steward_name",
        "data_steward_email",
        "domain",
        "department",
        "faculty",
        "source_system",
        "refresh_frequency",
        "retention_expectation",
        "allowed_consumer_type",
        "expected_output",
    ):
        assert f'"{field_name}"' in code
    assert 'business_purpose = selected_agreement.get("business_purpose") or selected_agreement.get("business_context", "")' in code
    assert '"data_steward": {' in code
    assert "display(agreement_context)" in code
    assert 'business_context=f"Business purpose: {business_purpose}\\nApproved usage: {approved_usage}"' in code
    assert "prompt_template=CONFIG.ai_prompt_config.dq_rule_suggestion_prompt_template" in code
    assert "CONFIG.ai_prompt_config.dq_rule_candidate_template" not in code
    assert 'business_context = selected_agreement.get("business_context", "")' not in code
    assert 'ownership = selected_agreement.get("ownership", "")' not in code
    assert 'print(f"business_context:' not in code
    assert 'print(f"ownership:' not in code
