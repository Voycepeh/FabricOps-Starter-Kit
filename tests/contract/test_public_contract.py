from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import fabricops_kit

pytestmark = pytest.mark.contract

APPROVED_V1_CALLABLES = {
    "setup_notebook",
    "setup_metadata_tables",
    "widget_render_data_steward",
    "widget_render_data_agreement",
    "widget_render_agreement_evidence",
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
    "enforce_freshness",
    "enforce_profile_behavior",
    "stop_if_failed",
    "enforce_dq_rules",
    "prepare_pipeline_table_configs",
    "run_table_guardrails",
    "write_catalogue_evidence",
    "write_pipeline_lineage",
    "write_pipeline_run_summary",
    "widget_select_catalogue_table",
    "get_selected_catalogue_table",
    "load_catalogue_profile_rows",
    "widget_review_column_context",
    "widget_review_dq_rules",
    "widget_review_column_classification",
    "record_table_governance",
}

REMOVED_LEGACY_ALIASES = {
    "monitor_data_changes",
    "display_schema_profile",
    "print_schema_guardrail_config",
    "widget_review_table_governance",
    "widget_render_agreement_intake_app",
    "setup_governance_metadata_tables",
    "setup_notebook_registry_table",
    "setup_data_agreement_tables",
    "draft_business_context",
    "prepare_business_context_profile_input",
    "extract_column_business_context_suggestions",
    "widget_review_business_context",
    "get_reviewed_business_context_rows",
    "write_business_context",
    "draft_dq_rules",
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
    assert len(fabricops_kit.__all__) == 32
    assert len(fabricops_kit.__all__) < 71
    for name in fabricops_kit.__all__:
        assert callable(getattr(fabricops_kit, name))


def test_removed_aliases_are_not_exported():
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


def test_removed_summary_module_is_not_part_of_v1_surface():
    root = Path(__file__).parents[2]
    deleted_symbols = {"build" + "_hand" + "over", "render" + "_hand" + "over_markdown"}

    assert not (root / "src" / "fabricops_kit" / ("hand" + "over.py")).exists()
    for name in deleted_symbols:
        assert name not in fabricops_kit.__all__
        assert not hasattr(fabricops_kit, name)

    scanned_suffixes = {".py", ".md", ".yml", ".yaml", ".json", ".ipynb"}
    offenders: list[str] = []
    for base in [root / "src", root / "templates", root / "docs"]:
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in scanned_suffixes:
                continue
            text = path.read_text(encoding="utf-8")
            for needle in ["fabricops_kit." + "hand" + "over", "_build" + "_hand" + "over_record", *deleted_symbols]:
                if needle in text:
                    offenders.append(f"{path.relative_to(root)} references {needle}")
    assert offenders == []


def test_template_function_map_matches_actual_template_calls_and_pages():
    root = Path(__file__).parents[2]
    manifest = json.loads((root / "docs" / "reference" / "manifest.json").read_text(encoding="utf-8"))
    manifest_callables = {row["callable_name"] for row in manifest["callables"]}
    called = _template_called_fabricops_functions()

    assert manifest_callables == APPROVED_V1_CALLABLES
    assert called <= manifest_callables
    assert {"prepare_pipeline_table_configs", "run_table_guardrails", "write_pipeline_lineage", "write_pipeline_run_summary"} <= called
    for callable_name in manifest_callables:
        canonical_page = root / "docs" / "api" / "reference" / f"{callable_name}.md"
        legacy_page = root / "docs" / "reference" / "callables" / f"{callable_name}.md"
        assert canonical_page.exists()
        assert not legacy_page.exists(), f"{legacy_page} duplicates canonical full-content page"


def test_generated_module_docs_surface_only_active_v1_modules():
    root = Path(__file__).parents[2]
    expected_modules = {
        "config",
        "data_agreement",
        "governance_review",
        "data_profiling",
        "fabric_input_output",
        "data_lineage",
        "guardrails",
        "metadata",
        "pipeline",
    }
    module_docs = {path.stem for path in (root / "docs" / "api" / "modules").glob("*.md") if path.stem != "index"}
    assert module_docs == expected_modules


def test_required_v1_imports_and_prompt_constants_remain_available():
    from fabricops_kit import read_lakehouse_excel, setup_metadata_tables, setup_notebook
    from fabricops_kit.governance_review import BUSINESS_CONTEXT_PROMPT, PDPA_PERSONAL_IDENTIFIER_PROMPT

    assert callable(setup_notebook)
    assert callable(setup_metadata_tables)
    assert callable(read_lakehouse_excel)
    assert BUSINESS_CONTEXT_PROMPT
    assert PDPA_PERSONAL_IDENTIFIER_PROMPT


def test_reference_generation_script_succeeds_for_template_map_and_module_docs():
    root = Path(__file__).parents[2]
    env = {**os.environ, "PYTHONPATH": str(root / "src")}
    result = subprocess.run(
        [sys.executable, "scripts/generate_function_reference.py"],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (root / "docs" / "reference" / "template-function-map.md").exists()
    assert (root / "docs" / "api" / "modules" / "config.md").exists()
