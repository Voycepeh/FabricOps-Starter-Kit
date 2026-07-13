"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import ast
import importlib
import inspect
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import fabricops_kit
from fabricops_kit.public_api import SUPPORTED_PUBLIC_API

pytestmark = pytest.mark.contract

APPROVED_V1_CALLABLES = {qualified_name.rsplit(".", maxsplit=1)[-1] for qualified_name in SUPPORTED_PUBLIC_API}
APPROVED_V1_QUALIFIED_CALLABLES = set(SUPPORTED_PUBLIC_API)
APPROVED_V1_QUALIFIED_FUNCTIONS = {
    name for name in APPROVED_V1_QUALIFIED_CALLABLES if not name.rsplit(".", maxsplit=1)[-1][0].isupper()
}
CONFIG_PUBLIC_FUNCTION_QUALIFIED_NAMES = set()
CONFIG_PUBLIC_MODEL_QUALIFIED_NAMES = {
    "fabricops_kit.config.shared.FabricStore",
    "fabricops_kit.config.shared.PathConfig",
    "fabricops_kit.config.shared.GovernanceConfig",
    "fabricops_kit.config.shared.DataAgreementConfig",
    "fabricops_kit.config.shared.FrameworkConfig",
    "fabricops_kit.config.shared.ConfigSmokeCheckResult",
    "fabricops_kit.config.shared.NotebookSetupContext",
}
LEGACY_APPROVED_V1_CALLABLES = {
    "setup_notebook",
    "read_lakehouse_table",
    "write_lakehouse_table",
    "read_lakehouse_csv",
    "read_lakehouse_parquet",
    "read_lakehouse_excel",
    "read_warehouse_table",
    "read_warehouse_query",
    "write_warehouse_table",
}

REMOVED_LEGACY_ALIASES = {
    "validate_schema",
    "validate_schema_rule",
    "monitor_data_changes",
    "display_schema_profile",
    "print_schema_guardrail_config",
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
    "build_enrichment_rules_records",
    "commit_enrichment_rules",
    "build_dq_rule_records",
    "commit_dq_rules",
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


def _signature_snapshot(function):
    signature = inspect.signature(function)
    parameters = []
    for parameter in signature.parameters.values():
        parameters.append(
            {
                "name": parameter.name,
                "kind": parameter.kind.name,
                "required": parameter.default is inspect.Parameter.empty,
            }
        )
    return {"parameters": parameters}


def test_supported_public_api_contract_has_release_count_and_stable_names():
    """Verify the v0.1.0 Live public API contract includes setup and Fabric I/O functions."""
    message = (
        "The supported public API surface for v0.1.0 must remain setup_notebook "
        "plus the eight Live Fabric I/O functions. Update SUPPORTED_PUBLIC_API "
        "and release docs intentionally if this changes."
    )

    assert len(SUPPORTED_PUBLIC_API) == 9, message
    assert len(set(SUPPORTED_PUBLIC_API)) == 9
    assert APPROVED_V1_CALLABLES == LEGACY_APPROVED_V1_CALLABLES


def test_supported_public_api_imports_are_callable_and_root_exported():
    """Verify every contract entry imports, is callable, and remains root exported."""
    for qualified_name in SUPPORTED_PUBLIC_API:
        module_name, function_name = qualified_name.rsplit(".", maxsplit=1)
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)

        assert callable(function), f"{qualified_name} must be callable"
        assert function_name in fabricops_kit.__all__
        assert getattr(fabricops_kit, function_name) is function


def test_supported_public_api_matches_generated_call_flow_contract():
    """Verify contract entries remain generated v2 callable-flow entries."""
    root = Path(__file__).parents[2]
    callable_flow = json.loads(
        (root / "docs" / "reference" / "_data" / "public-function-call-flows.json").read_text(encoding="utf-8")
    )
    dashboard_path = root / "docs" / "assets" / "public-function-call-flows-dashboard.html"

    flow_public = {row["function_name"] for row in callable_flow["public_functions"]}

    assert dashboard_path.exists()
    assert callable_flow["metadata"]["schema"] == "fabricops_public_function_call_flows_v2"
    assert {name.rsplit(".", maxsplit=1)[-1] for name in APPROVED_V1_QUALIFIED_FUNCTIONS}.issubset(flow_public)


def test_setup_notebook_lifecycle_metadata_is_live_since_v010():
    """Verify setup_notebook is recorded as Live in the v0.1.0 lifecycle metadata."""
    root = Path(__file__).parents[2]
    callable_flow = json.loads(
        (root / "docs" / "reference" / "_data" / "public-function-call-flows.json").read_text(encoding="utf-8")
    )

    setup_row = next(row for row in callable_flow["public_functions"] if row["function_name"] == "setup_notebook")

    assert setup_row["lifecycle_status"] == "live"
    assert setup_row["live_since"] == "0.1.0"
    assert setup_row["release_history"] == [{"status": "live", "version": "0.1.0"}]


def test_supported_public_api_signature_snapshot_is_lightweight_and_stable():
    """Verify Live public signatures are importable and snapshot keys stay focused."""
    snapshots = {}
    for qualified_name in SUPPORTED_PUBLIC_API:
        module_name, function_name = qualified_name.rsplit(".", maxsplit=1)
        function = getattr(importlib.import_module(module_name), function_name)
        snapshots[qualified_name] = _signature_snapshot(function)

    assert set(snapshots) == APPROVED_V1_QUALIFIED_CALLABLES
    assert all(snapshot["parameters"] for snapshot in snapshots.values())


def test_generated_callable_manifest_matches_approved_v1_list():
    """Verify generated callable manifest matches approved v1 list."""
    root = Path(__file__).parents[2]
    manifest = json.loads((root / "docs" / "reference" / "_data" / "manifest.json").read_text(encoding="utf-8"))
    manifest_callables = {row["callable_name"] for row in manifest["callables"]}
    assert (APPROVED_V1_CALLABLES - {"widget_browse_metadata_catalogue"}).issubset(manifest_callables)


def test_notebook_templates_call_only_approved_v1_surface():
    """Verify notebook templates call only approved v1 surface."""
    called = _template_called_fabricops_functions()
    assert called <= APPROVED_V1_CALLABLES
    assert called.isdisjoint(REMOVED_LEGACY_ALIASES)


def test_removed_summary_module_is_not_part_of_v1_surface():
    """Verify removed summary module is not part of v1 surface."""
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
    """Verify template function map matches actual template calls and pages."""
    root = Path(__file__).parents[2]
    manifest = json.loads((root / "docs" / "reference" / "_data" / "manifest.json").read_text(encoding="utf-8"))
    manifest_callables = {row["callable_name"] for row in manifest["callables"]}
    called = _template_called_fabricops_functions()

    assert (APPROVED_V1_CALLABLES - {"widget_browse_metadata_catalogue"}).issubset(manifest_callables)
    assert called <= manifest_callables | {"widget_browse_metadata_catalogue"}
    for callable_name in manifest_callables:
        canonical_page = root / "docs" / "api" / "reference" / f"{callable_name}.md"
        legacy_page = root / "docs" / "reference" / "callables" / f"{callable_name}.md"
        assert canonical_page.exists()
        assert not legacy_page.exists(), f"{legacy_page} duplicates canonical full-content page"


def test_generated_module_docs_are_not_public_surface():
    """Verify generated module docs are no longer part of the public docs surface."""
    root = Path(__file__).parents[2]
    stale_modules = {
        "config",
        "data_agreement",
        "governance_review",
        "pipeline",
        "io",
        "guardrails",
        "metadata",
        "pipeline",
    }
    module_dir = root / "docs" / "api" / "modules"
    module_docs = (
        set() if not module_dir.exists() else {path.stem for path in module_dir.glob("*.md") if path.stem != "index"}
    )
    mkdocs_text = (root / "mkdocs.yml").read_text(encoding="utf-8")

    assert module_docs == set()
    assert not any((module_dir / f"{module}.md").exists() for module in stale_modules)
    assert "api/modules/" not in mkdocs_text


def test_required_v1_imports_remain_available_and_prompt_helpers_are_not_exported():
    """Verify required v1 imports remain and prompt helpers are not exported."""
    from fabricops_kit import read_lakehouse_table, setup_metadata_tables, setup_notebook

    assert callable(setup_notebook)
    assert callable(setup_metadata_tables)
    assert callable(read_lakehouse_table)
    forbidden = {
        "AIPromptConfig",
        "draft_dq_rules",
        "BUSINESS_CONTEXT_PROMPT",
        "PDPA_PERSONAL_IDENTIFIER_PROMPT",
        "DQ_RULE_SUGGESTION_PROMPT",
    }
    assert forbidden.isdisjoint(set(fabricops_kit.__all__))
    for name in forbidden:
        assert not hasattr(fabricops_kit, name)


def test_individual_reference_generation_script_succeeds_without_module_docs():
    """Verify individual reference generation succeeds without restoring removed pages."""
    root = Path(__file__).parents[2]
    env = {**os.environ, "PYTHONPATH": str(root / "src")}
    call_flow_json = root / "docs" / "reference" / "_data" / "public-function-call-flows.json"
    dashboard_html = root / "docs" / "assets" / "public-function-call-flows-dashboard.html"
    call_flow_before = call_flow_json.read_text(encoding="utf-8")
    dashboard_before = dashboard_html.read_text(encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "scripts/generate_individual_function_reference_pages.py"],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert call_flow_json.read_text(encoding="utf-8") == call_flow_before
    assert dashboard_html.read_text(encoding="utf-8") == dashboard_before
    assert not (root / "docs" / "reference" / "template-function-map.md").exists()
    public_function_page = root / "docs" / "api" / "reference" / "read_lakehouse_csv.md"
    mkdocs_text = (root / "mkdocs.yml").read_text(encoding="utf-8")

    assert public_function_page.exists()
    function_text = public_function_page.read_text(encoding="utf-8")
    assert '<div class="reference-source-card" markdown="1">' in function_text
    assert 'reference-lifecycle-chip-prominent">Live</span>' in function_text
    assert 'Live since 0.1.0' in (root / "docs" / "api" / "reference" / "read_lakehouse_excel.md").read_text(encoding="utf-8")
    preview_text = (root / "docs" / "api" / "reference" / "setup_metadata_tables.md").read_text(encoding="utf-8")
    assert 'reference-lifecycle-chip-prominent">Preview</span>' in preview_text
    assert "not part of the supported Live release contract" in preview_text
    assert "backward-compatibility guarantees" in preview_text
    assert "Live since —" not in preview_text
    assert "Changes to its signature, behaviour" not in preview_text
    assert "<summary>Maintainer architecture details</summary>" in function_text
    assert function_text.rfind("## Contract impact") > function_text.find("## See also")
    assert "| Contract classification | Live public function |" in function_text
    assert "| Contract risk | Live |" in function_text
    assert "| Live-critical dependencies |" in function_text
    assert "Direct Live dependents" not in function_text
    assert "Transitive Live dependents" not in function_text
    assert "### Live-critical dependencies" in function_text
    assert function_text.rfind("### Live-critical dependencies") > function_text.find("<summary>Maintainer architecture details</summary>")
    assert '<code>fabricops_kit.config.shared.resolve_fabric_context</code>' in function_text
    assert "Open Live contract call flow" in function_text
    assert "../../../assets/public-function-call-flows-dashboard.html?function=read_lakehouse_csv" in function_text
    reference_index = (root / "docs" / "reference" / "index.md").read_text(encoding="utf-8")
    assert "Lifecycle" in reference_index
    assert "Live since 0.1.0" in reference_index
    assert "api-chip-module" not in function_text
    assert not (root / "docs" / "api" / "modules" / "config.md").exists()
    assert "api/modules/config.md" not in mkdocs_text


def test_lifecycle_reference_helpers_render_discontinued_and_missing_data() -> None:
    """Verify lifecycle helper output for discontinued and missing contract rows."""
    generator = importlib.import_module("scripts.generate_individual_function_reference_pages")
    discontinued = {
        "qualified_name": "fabricops_kit.old.old_function",
        "lifecycle_status": "Discontinued",
        "discontinued_in": "0.3.0",
        "contract_display": "Historical public callable",
        "live_critical_dependency_count": 0,
        "direct_live_dependent_count": 0,
        "transitive_live_dependent_count": 0,
    }

    header = "\n".join(generator._lifecycle_header_lines(discontinued))
    impact = "\n".join(
        generator._contract_impact_lines(discontinued, docs_metadata={}, public_page_names=set())
    )

    assert "Discontinued" in header
    assert "Discontinued in 0.3.0" in header
    assert "no longer part of the current supported public contract" in header
    assert "| Discontinued in | 0.3.0 |" in impact
    assert "| Contract risk | — |" in impact
    assert "Direct Live dependents" not in impact
    assert "Transitive Live dependents" not in impact
    with pytest.raises(RuntimeError, match="Public function reference lifecycle data missing for"):
        generator._lifecycle_status({"qualified_name": "fabricops_kit.io.read_lakehouse_excel.read_lakehouse_excel"})


def test_package_root_all_exports_are_importable() -> None:
    """Verify every package-root export supports notebook-friendly imports."""
    for name in fabricops_kit.__all__:
        namespace: dict[str, object] = {}
        exec(f"from fabricops_kit import {name}", namespace)
        assert namespace[name] is getattr(fabricops_kit, name)


def test_package_root_expected_public_names_are_present() -> None:
    """Verify expected notebook-friendly package-root names are exported."""
    expected_names = {
        "setup_notebook",
        "setup_metadata_tables",
        "read_lakehouse_table",
        "read_lakehouse_excel",
        "write_lakehouse_table",
        "profile_dataframe",
        "run_table_guardrails",
        "write_pipeline_lineage",
        "write_pipeline_run_summary",
        "widget_pipeline_bootstrap",
        "widget_render_data_steward",
        "widget_render_data_agreement",
        "widget_render_agreement_evidence",
    }

    assert expected_names <= set(fabricops_kit.__all__)


def test_package_root_widget_exports_are_lazy() -> None:
    """Verify package-root import does not eagerly import widget modules."""
    code = """
import sys
import fabricops_kit
widget_modules = [
    "fabricops_kit.widgets.widget_author_dq_rules",
    "fabricops_kit.widgets.widget_author_schema_freshness_profile_rules",
    "fabricops_kit.widgets.widget_enrich_table_metadata",
    "fabricops_kit.widgets.widget_pipeline_bootstrap",
    "fabricops_kit.widgets.widget_render_agreement_evidence",
    "fabricops_kit.widgets.widget_render_data_agreement",
    "fabricops_kit.widgets.widget_render_data_steward",
    "fabricops_kit.widgets.widget_review_guardrail_governance",
    "fabricops_kit.widgets.widget_select_guardrail_target",
]
assert not any(name in sys.modules for name in widget_modules), sorted(name for name in widget_modules if name in sys.modules)
value = fabricops_kit.widget_render_data_agreement
assert callable(value)
assert fabricops_kit.__dict__["widget_render_data_agreement"] is value
assert "fabricops_kit.widgets.widget_render_data_agreement" in sys.modules
assert "fabricops_kit.widgets.widget_author_dq_rules" not in sys.modules
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2] / "src")
    result = subprocess.run([sys.executable, "-c", code], env=env, text=True, capture_output=True, check=False)

    assert result.returncode == 0, result.stderr or result.stdout
