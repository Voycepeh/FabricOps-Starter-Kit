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



def test_widget_modules_do_not_import_legacy_agreement_or_governance_modules():
    """Verify widget modules do not depend on retired agreement/governance owners."""
    blocked_modules = {"fabricops_kit.data_agreement", "fabricops_kit.governance_review", "fabricops_kit.data_agreement_shared", "fabricops_kit.governance_shared"}
    blocked_package_names = {"data_agreement", "governance_review", "data_agreement_shared", "governance_shared"}
    violations = []
    for path in (SRC / "widgets").glob("*.py"):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module in blocked_modules:
                    violations.append(f"{path}:{node.lineno} imports from {node.module}")
                if node.module == "fabricops_kit":
                    imported = {alias.name for alias in node.names}
                    blocked = sorted(imported & blocked_package_names)
                    if blocked:
                        violations.append(f"{path}:{node.lineno} imports {', '.join(blocked)} from fabricops_kit")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in blocked_modules:
                        violations.append(f"{path}:{node.lineno} imports {alias.name}")

    assert violations == []




def test_widget_sources_do_not_use_dynamic_legacy_imports():
    """Verify widget files do not hide legacy owner dependencies in dynamic imports."""
    blocked_fragments = [
        "fabricops_kit.data_agreement",
        "fabricops_kit.governance_review",
        "__import__(",
        "importlib.import_module(\"fabricops_kit.data_agreement\")",
        "importlib.import_module(\"fabricops_kit.governance_review\")",
    ]
    violations = []
    for path in (SRC / "widgets").glob("*.py"):
        source = path.read_text(encoding="utf-8")
        for fragment in blocked_fragments:
            if fragment in source:
                violations.append(f"{path}: contains {fragment}")
    assert violations == []


def test_widgets_shared_does_not_define_legacy_module_loaders():
    """Verify widgets/shared.py does not define legacy owner module loader helpers."""
    source = (SRC / "widgets" / "shared.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    function_names = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    assert "_legacy_data_agreement_module" not in function_names
    assert "_legacy_governance_module" not in function_names


def test_legacy_proxy_shared_modules_do_not_exist():
    """Verify cleanup does not introduce proxy modules for retired owners."""
    assert not (SRC / "data_agreement_shared.py").exists()
    assert not (SRC / "governance_shared.py").exists()


def test_widgets_shared_does_not_define_legacy_getattr_fallbacks():
    """Verify widget shared helpers do not expose module-level legacy fallbacks."""
    source = (SRC / "widgets" / "shared.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    assert all(not (isinstance(node, ast.FunctionDef) and node.name == "__getattr__") for node in tree.body)


def _calls_write_lakehouse_table_core(source: str) -> bool:
    """Return whether source calls write_lakehouse_table_core directly."""
    tree = ast.parse(source)
    return any(isinstance(node, ast.Call) and getattr(node.func, "id", "") == "write_lakehouse_table_core" for node in ast.walk(tree))



def test_catalogue_type_normalizer_keeps_only_profile_evidence_casts():
    """Verify catalogue type casts do not include retired result fields."""
    source = _function_source("pipeline/shared.py", "_normalize_catalogue_evidence_types")

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

def test_catalogue_writer_targets_profiled_only():
    """Verify legacy evidence writer writes observed evidence to profiled only."""
    source = _function_source("pipeline/shared.py", "write_catalogue_evidence")

    assert _calls_write_lakehouse_table_core(source)
    assert "metadata_table: str = PROFILED_TABLE" in source
    assert "GUARDRAIL_TABLE" not in source
    assert "GUARDRAIL_RESULTS_TABLE" not in source
    for result_field in ("freshness_status", "stability_status", "dq_status", "source_schema_check", "target_schema_check"):
        assert result_field not in source


def test_runtime_result_writers_target_guardrail_results_only():
    """Verify runtime outcome writers target METADATA_GUARDRAIL_RESULTS only."""
    for path, function_name in [("pipeline/guardrails_shared.py", "write_guardrail_result_row")]:
        source = _function_source(path, function_name)
        assert _calls_write_lakehouse_table_core(source)
        assert "METADATA_GUARDRAIL_RESULTS" in source
        assert "GUARDRAIL_TABLE" not in source


def test_profile_behavior_runtime_writer_targets_results_not_catalogue():
    """Verify profile behavior enforcement writes outcomes to results, not catalogue."""
    source = _function_source("pipeline/guardrails_shared.py", "enforce_profile_behavior")

    assert "write_guardrail_result_row" in source
    assert "profile_evidence_rows" in source
    assert '"METADATA_DATA_CATALOGUE"' not in source



def test_runtime_enforcement_functions_route_outcomes_to_results():
    """Verify runtime guardrails expose result-table outcome writes."""
    dq_source = _function_source("pipeline/guardrails_shared.py", "run_active_dq_guardrail")
    pipeline_source = _function_source("pipeline/shared.py", "orchestrate_table_guardrails")

    assert "write_guardrail_result_row" in dq_source
    assert "write_results" in dq_source
    assert 'guardrail_type="dq"' in dq_source
    for guardrail_type in ('"schema"', '"freshness"', '"dq"'):
        assert guardrail_type in pipeline_source
    assert "write_guardrail_result_row" in pipeline_source


def test_guardrail_result_writer_has_single_shared_implementation():
    """Verify guardrail result writing is consolidated in the shared guardrail implementation."""
    writer_definitions = []
    for path in SRC.rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        writer_definitions.extend(
            f"{path.relative_to(SRC).as_posix()}:{node.name}"
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "write_guardrail_result_row"
        )

    assert writer_definitions == ["pipeline/guardrails_shared.py:write_guardrail_result_row"]
