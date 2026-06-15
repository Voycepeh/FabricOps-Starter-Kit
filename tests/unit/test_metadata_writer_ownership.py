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
    for path, function_name in [
        ("pipeline.py", "_write_guardrail_result_row"),
        ("governance_review.py", "_write_guardrail_result_row"),
    ]:
        source = _function_source(path, function_name)
        assert _calls_write_lakehouse_table(source)
        assert "GUARDRAIL_RESULTS_TABLE" in source
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

def test_widget_functions_do_not_write_mixed_guardrail_metadata():
    """Verify widget functions do not directly write catalogue/rule/result metadata."""
    for path in SRC.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("widget_"):
                function_source = ast.get_source_segment(source, node) or ""
                assert "write_lakehouse_table" not in function_source, f"{path}:{node.name} writes metadata directly"
                assert "METADATA_DATA_CATALOGUE" not in function_source or "read_lakehouse_table" in function_source
