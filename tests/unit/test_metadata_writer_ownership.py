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


def _calls_write_lakehouse_table(source: str) -> bool:
    """Return whether source calls write_lakehouse_table directly."""
    tree = ast.parse(source)
    return any(isinstance(node, ast.Call) and getattr(node.func, "id", "") == "write_lakehouse_table" for node in ast.walk(tree))



def test_catalogue_type_normalizer_keeps_only_profile_evidence_casts():
    """Verify catalogue type casts do not include retired result fields."""
    source = _function_source("pipeline.py", "_normalize_catalogue_evidence_types")

    for profile_field in ("row_count", "null_count", "distinct_count", "null_percent", "distinct_percent", "dq_failed_row_percent", "run_timestamp"):
        assert profile_field in source
    for result_field in (
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

    assert _calls_write_lakehouse_table(source)
    assert "metadata_table: str = CATALOGUE_TABLE" in source
    assert "GUARDRAIL_RULES_TABLE" not in source
    assert "GUARDRAIL_RESULTS_TABLE" not in source
    for result_field in ("freshness_status", "stability_status", "dq_status", "source_schema_check", "target_schema_check"):
        assert result_field not in source


def test_runtime_result_writers_target_guardrail_results_only():
    """Verify runtime outcome writers target METADATA_GUARDRAIL_RESULTS only."""
    for path, function_name in [("metadata.py", "_write_guardrail_result_row")]:
        source = _function_source(path, function_name)
        assert _calls_write_lakehouse_table(source)
        assert "METADATA_GUARDRAIL_RESULTS" in source
        assert "CATALOGUE_TABLE" not in source
        assert "GUARDRAIL_RULES_TABLE" not in source


def test_profile_behavior_runtime_writer_targets_results_not_catalogue():
    """Verify profile behavior enforcement writes outcomes to results, not catalogue."""
    source = _function_source("guardrails.py", "enforce_profile_behavior")

    assert '"METADATA_GUARDRAIL_RESULTS"' in source
    assert 'write_lakehouse_table(spark.createDataFrame([result_row])' in source
    assert '"METADATA_DATA_CATALOGUE"' not in source


def test_governance_rule_writer_targets_guardrail_rules_for_dq():
    """Verify table governance commits DQ approvals to guardrail rules."""
    source = _function_source("governance_review.py", "record_table_governance")

    assert "GUARDRAIL_RULES_TABLE" in source
    assert 'guardrail_type="dq"' in source
    assert "CATALOGUE_TABLE" not in source
    assert "GUARDRAIL_RESULTS_TABLE" not in source



def test_runtime_enforcement_functions_route_outcomes_to_results():
    """Verify runtime guardrails expose result-table outcome writes."""
    dq_source = _function_source("governance_review.py", "enforce_dq_rules")
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
    """Verify widget functions do not directly write mixed metadata payloads."""
    dq_widget_source = _function_source("governance_review.py", "widget_review_dq_rules")
    catalogue_widget_source = _function_source("governance_review.py", "widget_select_governance_profile_target")

    assert "METADATA_GUARDRAIL_RULES" in dq_widget_source
    assert "METADATA_DATA_CATALOGUE" in catalogue_widget_source
    assert "read_lakehouse_table" in catalogue_widget_source
    assert "write_lakehouse_table" not in catalogue_widget_source

    for path in SRC.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("widget_"):
                function_source = ast.get_source_segment(source, node) or ""
                assert "write_lakehouse_table" not in function_source, f"{path}:{node.name} writes metadata directly"
                assert "METADATA_DATA_CATALOGUE" not in function_source or "read_lakehouse_table" in function_source
                assert not ("METADATA_DATA_CATALOGUE" in function_source and "METADATA_GUARDRAIL_RESULTS" in function_source)
