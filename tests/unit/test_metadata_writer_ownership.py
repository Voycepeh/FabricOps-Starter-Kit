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


def test_runtime_result_writers_target_guardrail_results_only():
    """Verify runtime outcome writers target METADATA_GUARDRAIL_RESULTS only."""
    for path, function_name in [("pipeline/shared.py", "write_guardrail_result_row")]:
        source = _function_source(path, function_name)
        assert _calls_write_lakehouse_table_core(source)
        assert "METADATA_GUARDRAIL_RESULTS" in source
        assert "GUARDRAIL_TABLE" not in source


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

    assert writer_definitions == ["pipeline/shared.py:write_guardrail_result_row"]
