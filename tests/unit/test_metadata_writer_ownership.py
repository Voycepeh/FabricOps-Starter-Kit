"""Source-level checks for metadata writer table ownership."""

from __future__ import annotations

import ast
from pathlib import Path

SRC = Path("src/fabricops_kit")


def _function_source(path: str, function_name: str) -> str:
    """Return source text for a top-level function."""
    source = (SRC / path).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.get_source_segment(source, node) or ""
    raise AssertionError(f"{function_name} not found in {path}")



def test_widget_modules_do_not_import_private_agreement_or_governance_helpers():
    """Verify widget modules do not import private helpers from retired owner modules."""
    blocked_modules = {"fabricops_kit.data_agreement", "fabricops_kit.governance_review"}
    violations = []
    for path in (SRC / "widgets").glob("*.py"):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module in blocked_modules:
                private_names = [alias.name for alias in node.names if alias.name.startswith("_")]
                if private_names:
                    violations.append(f"{path}:{node.lineno} imports {', '.join(private_names)} from {node.module}")

    assert violations == []

def _calls_write_lakehouse_table_core(source: str) -> bool:
    """Return whether source calls write_lakehouse_table_core directly."""
    tree = ast.parse(source)
    return any(isinstance(node, ast.Call) and getattr(node.func, "id", "") == "write_lakehouse_table_core" for node in ast.walk(tree))



def test_catalogue_type_normalizer_keeps_only_profile_evidence_casts():
    """Verify catalogue type casts do not include retired result fields."""
    source = _function_source("pipeline.py", "_normalize_catalogue_evidence_types")

    for profile_field in ("row_count", "null_count", "distinct_count", "null_percent", "distinct_percent", "run_timestamp"):
        assert profile_field in source
    for result_field in (
        "dq_failed_row_percent",
        "dq_rule_count",
        "dq_failed_rule_count",
        "dq_warning_rule_count",
        "dq_error_rule_count",
        "dq_failed_row_count",
        "stability_check_enabled",
        "freshness_can_continue",
        "stability_can_continue",
    ):
        assert result_field not in source

def test_catalogue_writer_targets_catalogue_only():
    """Verify catalogue writer writes observed evidence to catalogue only."""
    source = _function_source("pipeline.py", "write_catalogue_evidence")

    assert _calls_write_lakehouse_table_core(source)
    assert "metadata_table: str = CATALOGUE_TABLE" in source
    assert "GUARDRAIL_RULES_TABLE" not in source
    assert "GUARDRAIL_RESULTS_TABLE" not in source
    for result_field in ("freshness_status", "stability_status", "dq_status", "source_schema_check", "target_schema_check"):
        assert result_field not in source


def test_runtime_result_writers_target_guardrail_results_only():
    """Verify runtime outcome writers target METADATA_GUARDRAIL_RESULTS only."""
    for path, function_name in [("metadata.py", "_write_guardrail_result_row")]:
        source = _function_source(path, function_name)
        assert _calls_write_lakehouse_table_core(source)
        assert "METADATA_GUARDRAIL_RESULTS" in source
        assert "GUARDRAIL_RULES_TABLE" not in source


def test_profile_behavior_runtime_writer_targets_results_not_catalogue():
    """Verify profile behavior enforcement writes outcomes to results, not catalogue."""
    source = _function_source("guardrails.py", "enforce_profile_behavior")

    assert "_write_guardrail_result_row" in source
    assert "profile_evidence_rows" in source
    assert '"METADATA_DATA_CATALOGUE"' not in source


def test_governance_rule_writer_targets_guardrail_rules_for_dq():
    """Verify table governance commits DQ approvals to guardrail rules."""
    source = _function_source("governance_review.py", "record_table_governance")

    assert "GUARDRAIL_RULES_TABLE" in source
    assert "ENRICHMENT_RULES_TABLE" in source
    assert "GUARDRAIL_RESULTS_TABLE" not in source



def test_runtime_enforcement_functions_route_outcomes_to_results():
    """Verify runtime guardrails expose result-table outcome writes."""
    dq_source = _function_source("governance_review.py", "_run_active_dq_guardrail")
    pipeline_source = _function_source("pipeline.py", "run_table_guardrails")

    assert "_write_guardrail_result_row" in dq_source
    assert "write_results" in dq_source
    assert 'guardrail_type="dq"' in dq_source
    for guardrail_type in ('"schema"', '"freshness"', '"dq"'):
        assert guardrail_type in pipeline_source
    assert "_write_guardrail_result_row" in pipeline_source


def test_guardrail_result_writer_has_single_shared_implementation():
    """Verify guardrail result writing is consolidated in metadata utilities."""
    writer_definitions = []
    for path in SRC.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        writer_definitions.extend(
            f"{path.name}:{node.name}"
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "_write_guardrail_result_row"
        )

    assert writer_definitions == ["metadata.py:_write_guardrail_result_row"]

def test_widget_functions_do_not_write_mixed_guardrail_metadata():
    """Verify widget wrappers delegate and workflows keep metadata ownership."""
    workflow_by_wrapper = {
        "widget_select_guardrail_target": "_guardrail_target_selection_widget_workflow",
        "widget_author_schema_freshness_profile_rules": "_schema_freshness_profile_rule_authoring_widget_workflow",
        "widget_author_dq_rules": "_dq_rule_authoring_widget_workflow",
        "widget_review_guardrail_governance": "_guardrail_governance_review_widget_workflow",
    }
    workflow_sources = {
        workflow_name: _function_source(f"widgets/{wrapper_name}.py", workflow_name)
        for wrapper_name, workflow_name in workflow_by_wrapper.items()
    }

    selector_source = workflow_sources["_guardrail_target_selection_widget_workflow"]
    schema_widget_source = workflow_sources["_schema_freshness_profile_rule_authoring_widget_workflow"]
    dq_widget_source = workflow_sources["_dq_rule_authoring_widget_workflow"]
    review_widget_source = workflow_sources["_guardrail_governance_review_widget_workflow"]

    assert "CATALOGUE_TABLE" in selector_source
    assert "GUARDRAIL_RULES_TABLE" in selector_source
    assert "ENRICHMENT_RULES_TABLE" in selector_source
    assert "_read_metadata_table_or_empty" in selector_source
    assert "_write_rule_records" in schema_widget_source
    assert "_write_rule_records" in dq_widget_source
    assert "_write_rule_records" in review_widget_source
    assert "_write_enrichment_records" in review_widget_source
    assert "_write_governance_policy_record" not in review_widget_source
    assert "METADATA_GOVERNANCE_REVIEWS" not in review_widget_source

    for source in (schema_widget_source, dq_widget_source, review_widget_source):
        assert "CATALOGUE_TABLE" not in source
        assert "GUARDRAIL_RESULTS_TABLE" not in source
        assert "write_lakehouse_table_core" not in source

    for wrapper_name, workflow_name in workflow_by_wrapper.items():
        wrapper_source = _function_source(f"widgets/{wrapper_name}.py", wrapper_name)
        wrapper_tree = ast.parse(wrapper_source)
        wrapper_def = next(node for node in wrapper_tree.body if isinstance(node, ast.FunctionDef))
        wrapper_calls = {node.func.id for node in ast.walk(wrapper_def) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        wrapper_returns = [node for node in ast.walk(wrapper_def) if isinstance(node, ast.Return)]

        assert workflow_name in wrapper_calls
        assert len(wrapper_returns) == 1
        assert "write_lakehouse_table_core" not in wrapper_source
        assert "_write_rule_records" not in wrapper_source
        assert "_write_enrichment_records" not in wrapper_source
        assert "CATALOGUE_TABLE" not in wrapper_source
        assert "GUARDRAIL_RULES_TABLE" not in wrapper_source
        assert "GUARDRAIL_RESULTS_TABLE" not in wrapper_source
        assert "ENRICHMENT_RULES_TABLE" not in wrapper_source

    for path in SRC.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("widget_"):
                function_source = ast.get_source_segment(source, node) or ""
                assert "write_lakehouse_table_core" not in function_source, f"{path}:{node.name} writes metadata directly"
