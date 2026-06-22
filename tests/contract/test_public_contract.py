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
LEGACY_APPROVED_V1_CALLABLES = {
    "setup_notebook",
    "setup_metadata_tables",
    "widget_render_data_steward",
    "widget_render_data_agreement",
    "widget_render_agreement_evidence",
    "read_lakehouse_table",
    "write_lakehouse_table",
    "read_lakehouse_csv",
    "read_lakehouse_parquet",
    "read_lakehouse_excel",
    "read_warehouse_table",
    "read_warehouse_query",
    "write_warehouse_table",
    "profile_dataframe",
    "get_latest_metadata_catalogue",
    "display_guardrail_results",
    "prepare_pipeline_table_configs",
    "run_table_guardrails",
    "start_pipeline_run",
    "write_pipeline_lineage",
    "write_pipeline_run_summary",
    "widget_select_guardrail_target",
    "widget_enrich_table_metadata",
    "widget_author_schema_freshness_profile_rules",
    "widget_author_dq_rules",
    "widget_review_guardrail_governance",
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
    """Verify the release public API contract keeps exactly 26 functions."""
    message = (
        "The supported public API surface must remain exactly 26 functions during "
        "the release refactor. Update SUPPORTED_PUBLIC_API and the release docs "
        "intentionally if this changes."
    )

    assert len(SUPPORTED_PUBLIC_API) == 26, message
    assert len(set(SUPPORTED_PUBLIC_API)) == 26
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


def test_supported_public_api_matches_generated_inventory_classification():
    """Verify contract entries remain generated Callable inventory entries."""
    root = Path(__file__).parents[2]
    function_manifest = json.loads(
        (root / "docs" / "reference" / "_data" / "function-manifest.json").read_text(encoding="utf-8")
    )
    callable_flow = json.loads(
        (root / "docs" / "reference" / "_data" / "callable-flow.json").read_text(encoding="utf-8")
    )

    manifest_public = {row["qualified_name"] for row in function_manifest if row.get("classification") == "Callable"}
    flow_public = {
        row["qualified_name"]
        for row in callable_flow["function_inventory"]
        if row.get("layer") == "public" or row.get("function_type") == "Public Starter Kit function"
    }

    assert manifest_public == APPROVED_V1_QUALIFIED_CALLABLES
    assert flow_public == APPROVED_V1_QUALIFIED_CALLABLES


def test_supported_public_api_signature_snapshot_is_lightweight_and_stable():
    """Verify public signatures keep the same parameter names and required flags."""
    root = Path(__file__).parents[2]
    function_manifest = json.loads(
        (root / "docs" / "reference" / "_data" / "function-manifest.json").read_text(encoding="utf-8")
    )
    source_locations = {row["qualified_name"]: row for row in function_manifest}

    snapshots = {}
    for qualified_name in SUPPORTED_PUBLIC_API:
        module_name, function_name = qualified_name.rsplit(".", maxsplit=1)
        function = getattr(importlib.import_module(module_name), function_name)
        snapshots[qualified_name] = _signature_snapshot(function)

    assert snapshots == {
        "fabricops_kit.config.setup_metadata_tables": {
            "parameters": [
                {"name": "spark", "kind": "KEYWORD_ONLY", "required": True},
                {"name": "config", "kind": "KEYWORD_ONLY", "required": True},
                {"name": "env", "kind": "KEYWORD_ONLY", "required": True},
                {"name": "metadata_schema", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "require_active_steward", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.config.setup_notebook": {
            "parameters": [
                {"name": "config", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "env", "kind": "POSITIONAL_OR_KEYWORD", "required": False},
                {"name": "required_targets", "kind": "POSITIONAL_OR_KEYWORD", "required": False},
                {"name": "notebook_name", "kind": "POSITIONAL_OR_KEYWORD", "required": False},
                {"name": "run_id_prefix", "kind": "POSITIONAL_OR_KEYWORD", "required": False},
                {"name": "local_fallback_name", "kind": "POSITIONAL_OR_KEYWORD", "required": False},
            ]
        },
        "fabricops_kit.data_agreement.widget_render_agreement_evidence": {
            "parameters": [
                {"name": "spark", "kind": "KEYWORD_ONLY", "required": True},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.data_agreement.widget_render_data_agreement": {
            "parameters": [
                {"name": "spark", "kind": "KEYWORD_ONLY", "required": True},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.data_agreement.widget_render_data_steward": {
            "parameters": [
                {"name": "spark", "kind": "KEYWORD_ONLY", "required": True},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.data_profiling.profile_dataframe": {
            "parameters": [
                {"name": "df", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "table_name", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "exclude_columns", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "run_timestamp_timezone", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "config", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "include_distributions", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "distribution_columns", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "distribution_bin_edges", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "categorical_categories", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "categorical_top_n", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.fabric_input_output.read_lakehouse_csv": {
            "parameters": [
                {"name": "relative_path", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "target", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "spark_session", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "header", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "options", "kind": "VAR_KEYWORD", "required": True},
            ]
        },
        "fabricops_kit.fabric_input_output.read_lakehouse_excel": {
            "parameters": [
                {"name": "relative_path", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "target", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "sheet_name", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "spark_session", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "read_excel_kwargs", "kind": "VAR_KEYWORD", "required": True},
            ]
        },
        "fabricops_kit.fabric_input_output.read_lakehouse_parquet": {
            "parameters": [
                {"name": "relative_path", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "target", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "verbose", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "spark_session", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.fabric_input_output.read_lakehouse_table": {
            "parameters": [
                {"name": "table_name", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "target", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "schema", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "spark_session", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.fabric_input_output.read_warehouse_query": {
            "parameters": [
                {"name": "query", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "target", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "spark_session", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.fabric_input_output.read_warehouse_table": {
            "parameters": [
                {"name": "schema", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "table_name", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "target", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "spark_session", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.fabric_input_output.write_lakehouse_table": {
            "parameters": [
                {"name": "df", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "table_name", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "target", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "schema", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "mode", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "partition_by", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "repartition_by", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "options", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "verbose", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.fabric_input_output.write_warehouse_table": {
            "parameters": [
                {"name": "df", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "schema", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "table_name", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "target", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "mode", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.governance_review.get_latest_metadata_catalogue": {
            "parameters": [
                {"name": "table_name", "kind": "KEYWORD_ONLY", "required": True},
                {"name": "agreement", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "metadata_schema", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "spark_session", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.governance_review.widget_author_dq_rules": {
            "parameters": [
                {"name": "state", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "dq_authoring_mode", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "rule_type", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "selected_columns", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "parameters", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "severity", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "spark_session", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "bypass_reason", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "source_notebook_type", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "created_by_role", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "commit", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.governance_review.widget_author_schema_freshness_profile_rules": {
            "parameters": [
                {"name": "state", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "spark_session", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "bypass_reason", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "source_notebook_type", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "created_by_role", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "commit", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.governance_review.widget_enrich_table_metadata": {
            "parameters": [
                {"name": "guardrail_state", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "spark_session", "kind": "KEYWORD_ONLY", "required": True},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "source_notebook_type", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "created_by_role", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.governance_review.widget_review_guardrail_governance": {
            "parameters": [
                {"name": "state", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "spark_session", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.governance_review.widget_select_guardrail_target": {
            "parameters": [
                {"name": "spark_session", "kind": "KEYWORD_ONLY", "required": True},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.pipeline.display_guardrail_results": {
            "parameters": [
                {"name": "result_bundle", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "mode", "kind": "POSITIONAL_OR_KEYWORD", "required": False},
                {"name": "spark_session", "kind": "POSITIONAL_OR_KEYWORD", "required": False},
            ]
        },
        "fabricops_kit.pipeline.prepare_pipeline_table_configs": {
            "parameters": [
                {"name": "table_configs", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "default_settings", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "table_role", "kind": "KEYWORD_ONLY", "required": True},
                {"name": "run_id", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "pipeline_name", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.pipeline.run_table_guardrails": {
            "parameters": [
                {"name": "table_configs", "kind": "POSITIONAL_OR_KEYWORD", "required": True},
                {"name": "run_id", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "spark_session", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "agreement_id", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "agreement_contract_version", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "notebook_registry_id", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "notebook_id", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "pipeline_name", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "table_role", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "mode", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "stop_on_failure", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.pipeline.start_pipeline_run": {
            "parameters": [
                {"name": "notebook_type", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "select_agreement", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "register_notebook", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "read_only", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "run_context", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "spark_session", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "metadata_schema", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "pipeline_name", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.pipeline.write_pipeline_lineage": {
            "parameters": [
                {"name": "spark", "kind": "KEYWORD_ONLY", "required": True},
                {"name": "run_id", "kind": "KEYWORD_ONLY", "required": True},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "source_definitions", "kind": "KEYWORD_ONLY", "required": True},
                {"name": "target_definitions", "kind": "KEYWORD_ONLY", "required": True},
                {"name": "relationships", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "dataset_name", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "agreement_id", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "agreement_contract_version", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "notebook_registry_id", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "notebook_id", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "pipeline_name", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "metadata_table", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "mode", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
        "fabricops_kit.pipeline.write_pipeline_run_summary": {
            "parameters": [
                {"name": "spark", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "run_id", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "context", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "agreement_id", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "agreement_contract_version", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "notebook_registry_id", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "notebook_id", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "notebook_type", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "pipeline_name", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "started_at", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "completed_at", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "status", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "source_definitions", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "target_definitions", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "source_schema_results", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "target_schema_results", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "source_freshness_results", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "target_freshness_results", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "source_stability_results", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "target_stability_results", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "source_dq_results", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "target_dq_results", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "lineage_status", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "catalogue_status", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "message", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "source_guardrail_results", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "target_guardrail_results", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "target_write_status", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "lineage_result", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "metadata_table", "kind": "KEYWORD_ONLY", "required": False},
                {"name": "mode", "kind": "KEYWORD_ONLY", "required": False},
            ]
        },
    }

    assert set(snapshots) <= set(source_locations)


def test_root_exports_only_approved_v1_template_callables():
    """Verify root exports only approved v1 template callables."""
    assert set(fabricops_kit.__all__) == APPROVED_V1_CALLABLES
    assert len(fabricops_kit.__all__) == len(APPROVED_V1_CALLABLES)
    for name in fabricops_kit.__all__:
        assert callable(getattr(fabricops_kit, name))


def test_removed_aliases_are_not_exported():
    """Verify removed aliases are not exported."""
    for name in REMOVED_LEGACY_ALIASES:
        assert name not in fabricops_kit.__all__
        assert not hasattr(fabricops_kit, name)


def test_root_public_exports_match_approved_v1_list():
    """Verify root public exports match approved v1 list."""
    assert set(fabricops_kit.__all__) == APPROVED_V1_CALLABLES
    for removed in {
        "apply_governance_rule_action",
        "build_guardrail_detail_rows",
        "build_guardrail_summary_rows",
        "build_table_governance_policy_record",
        "guardrail_authoring_status",
        "load_catalogue_profile_rows",
        "mark_table_governed",
        "mark_table_ungoverned",
        "record_table_governance",
        "resolve_table_governance_policy",
        "widget_review_enrichment_rules",
        "widget_review_enrichment_rules",
        "widget_review_dq_rules",
        "widget_select_governance_profile_target",
        "get_selected_catalogue_table",
    }:
        assert removed not in fabricops_kit.__all__


def test_generated_callable_manifest_matches_approved_v1_list():
    """Verify generated callable manifest matches approved v1 list."""
    root = Path(__file__).parents[2]
    manifest = json.loads((root / "docs" / "reference" / "_data" / "manifest.json").read_text(encoding="utf-8"))
    manifest_callables = {row["callable_name"] for row in manifest["callables"]}
    assert manifest_callables == APPROVED_V1_CALLABLES


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

    assert manifest_callables == APPROVED_V1_CALLABLES
    assert called <= manifest_callables
    assert {
        "prepare_pipeline_table_configs",
        "run_table_guardrails",
        "write_pipeline_lineage",
        "write_pipeline_run_summary",
    } <= called
    for callable_name in manifest_callables:
        canonical_page = root / "docs" / "api" / "reference" / f"{callable_name}.md"
        legacy_page = root / "docs" / "reference" / "callables" / f"{callable_name}.md"
        assert canonical_page.exists()
        assert not legacy_page.exists(), f"{legacy_page} duplicates canonical full-content page"


def test_generated_module_docs_surface_only_active_v1_modules():
    """Verify generated module docs surface only active v1 modules."""
    root = Path(__file__).parents[2]
    expected_modules = {
        "config",
        "data_agreement",
        "governance_review",
        "data_profiling",
        "fabric_input_output",
        "io_core",
        "guardrails",
        "metadata",
        "pipeline",
    }
    module_docs = {path.stem for path in (root / "docs" / "api" / "modules").glob("*.md") if path.stem != "index"}
    assert module_docs == expected_modules


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


def test_reference_generation_script_succeeds_for_reference_and_module_docs():
    """Verify reference generation script succeeds without restoring removed pages."""
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
    assert not (root / "docs" / "reference" / "template-function-map.md").exists()
    assert (root / "docs" / "api" / "modules" / "config.md").exists()
