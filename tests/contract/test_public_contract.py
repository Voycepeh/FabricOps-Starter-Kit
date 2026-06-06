from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

import fabricops_kit

pytestmark = pytest.mark.contract

APPROVED_V1_CALLABLES = {
    "setup_notebook",
    "setup_data_agreement_tables",
    "setup_notebook_registry_table",
    "setup_governance_metadata_tables",
    "widget_render_agreement_intake_app",
    "widget_select_agreement",
    "get_selected_agreement",
    "read_lakehouse_table",
    "write_lakehouse_table",
    "read_lakehouse_csv",
    "read_lakehouse_parquet",
    "read_lakehouse_excel",
    "read_warehouse_table",
    "write_warehouse_table",
    "profile_dataframe",
    "validate_schema",
    "monitor_data_changes",
    "stop_if_failed",
    "build_lineage_records",
    "build_handover",
    "render_handover_markdown",
    "widget_select_catalogue_table",
    "get_selected_catalogue_table",
    "load_catalogue_profile_rows",
    "widget_review_table_governance",
    "record_table_governance",
}

REMOVED_LEGACY_ALIASES = {
    "draft_business_context",
    "prepare_business_context_profile_input",
    "extract_column_business_context_suggestions",
    "widget_review_business_context",
    "get_reviewed_business_context_rows",
    "write_business_context",
    "draft_dq_rules",
    "widget_review_dq_rules",
    "get_dq_review_results",
    "write_dq_rules",
    "load_dq_rules",
    "enforce_dq",
    "assert_dq_passed",
    "draft_governance",
    "prepare_governance_input",
    "extract_governance_suggestions",
    "widget_review_governance",
    "write_governance",
    "load_governance",
    "build_column_context_records",
    "commit_column_context",
    "build_dq_rule_records",
    "commit_dq_rules",
    "build_classification_records",
    "commit_column_classification",
    "build_runtime_audit_fields",
    "current_notebook_active_registrations",
    "print_runtime_banner",
    "get_package_version",
}


def _clean_notebook_code(source: str) -> str:
    return "\n".join(line for line in source.splitlines() if not line.lstrip().startswith(("%", "!")))


def _template_called_fabricops_functions() -> set[str]:
    root = Path(__file__).parents[2]
    package_functions = set(APPROVED_V1_CALLABLES) | REMOVED_LEGACY_ALIASES
    calls: set[str] = set()
    for notebook_path in (root / "templates" / "notebooks").glob("*.ipynb"):
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        for cell in notebook.get("cells", []):
            if cell.get("cell_type") != "code":
                continue
            code = _clean_notebook_code("".join(cell.get("source", [])))
            try:
                tree = ast.parse(code)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                func = node.func
                name = func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else None
                if name in package_functions:
                    calls.add(name)
    return calls


def test_root_exports_only_approved_v1_template_callables():
    assert set(fabricops_kit.__all__) == APPROVED_V1_CALLABLES
    assert len(fabricops_kit.__all__) == 26
    assert len(fabricops_kit.__all__) < 71
    for name in fabricops_kit.__all__:
        assert callable(getattr(fabricops_kit, name))


def test_no_legacy_aliases_or_compatibility_wrappers_remain_exported():
    for name in REMOVED_LEGACY_ALIASES:
        assert name not in fabricops_kit.__all__
        assert not hasattr(fabricops_kit, name)


def test_source_public_functions_match_approved_v1_list():
    root = Path(__file__).parents[2]
    public_functions: set[str] = set()
    for path in (root / "src" / "fabricops_kit").glob("*.py"):
        if path.name == "__init__.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                public_functions.add(node.name)
    assert public_functions == APPROVED_V1_CALLABLES


def test_generated_callable_manifest_matches_approved_v1_list():
    root = Path(__file__).parents[2]
    manifest = json.loads((root / "docs" / "reference" / "manifest.json").read_text(encoding="utf-8"))
    manifest_callables = {row["callable_name"] for row in manifest["callables"]}
    assert manifest_callables == APPROVED_V1_CALLABLES


def test_notebook_templates_call_only_approved_v1_surface():
    called = _template_called_fabricops_functions()
    assert called <= APPROVED_V1_CALLABLES
    assert called.isdisjoint(REMOVED_LEGACY_ALIASES)
