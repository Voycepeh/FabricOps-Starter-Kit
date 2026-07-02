"""Tests for the callable orphan audit script."""

from __future__ import annotations

import json
from pathlib import Path

import scripts.audit_callable_orphans as audit_script


def _write(path: Path, text: str) -> None:
    """Write text after creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _graph(row: dict[str, object]) -> dict[str, object]:
    """Build a minimal function-call-graph document."""
    return {"function_inventory": [row], "public_entrypoint_flow": []}


def test_load_graph_reads_synthetic_function_call_graph(tmp_path: Path) -> None:
    """Verify synthetic function-call-graph JSON can be loaded."""
    graph_path = tmp_path / "function-call-graph.json"
    graph = _graph({"qualified_name": "fabricops_kit.a.orphan", "function_name": "orphan"})
    graph_path.write_text(json.dumps(graph), encoding="utf-8")

    assert audit_script.load_graph(graph_path) == graph


def test_audit_classifies_test_only_source_candidate(tmp_path: Path, monkeypatch) -> None:
    """Verify unreferenced source functions used only by tests are flagged."""
    monkeypatch.setattr(audit_script, "ROOT", tmp_path)
    _write(tmp_path / "src/fabricops_kit/a.py", "def helper():\n    return 1\n")
    _write(tmp_path / "tests/test_a.py", "from fabricops_kit.a import helper\n\ndef test_helper():\n    assert helper() == 1\n")
    graph_path = tmp_path / "docs/reference/_data/function-call-graph.json"
    output_path = tmp_path / "docs/reference/_data/callable-orphan-audit.json"
    row = {
        "qualified_name": "fabricops_kit.a.helper",
        "function_name": "helper",
        "module": "a",
        "source_path": "src/fabricops_kit/a.py",
        "source_start_line": 1,
        "source_end_line": 2,
        "callable_kind": "function",
        "layer": "private_helper",
        "function_type": "Private helper",
        "reachability": "unreachable_runtime_asset",
        "reachability_label": "Unknown / possible entrypoint",
        "recommended_action": "Verify possible orphan",
        "signals": [],
        "callees": [],
    }
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    graph_path.write_text(json.dumps(_graph(row)), encoding="utf-8")

    records = audit_script.audit(graph_path, output_path)

    assert records[0]["likely_classification"] == "test_only_source_candidate"
    assert records[0]["test_references_count"] == 1
    assert set(audit_script.EXPECTED_KEYS) == set(records[0])


def test_audit_classifies_scanner_gap_for_missing_graph_dependency(tmp_path: Path, monkeypatch) -> None:
    """Verify source calls absent from graph dependencies are scanner gaps."""
    monkeypatch.setattr(audit_script, "ROOT", tmp_path)
    _write(tmp_path / "src/fabricops_kit/a.py", "def missing_dep():\n    return 1\n\ndef helper():\n    return missing_dep()\n")
    graph_path = tmp_path / "docs/reference/_data/function-call-graph.json"
    output_path = tmp_path / "docs/reference/_data/callable-orphan-audit.json"
    row = {
        "qualified_name": "fabricops_kit.a.helper",
        "function_name": "helper",
        "module": "a",
        "source_path": "src/fabricops_kit/a.py",
        "callable_kind": "function",
        "layer": "private_helper",
        "function_type": "Private helper",
        "reachability": "unreachable_runtime_asset",
        "reachability_label": "Unknown / possible entrypoint",
        "recommended_action": "Verify possible orphan",
        "signals": [],
        "callees": [],
    }
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    graph_path.write_text(json.dumps(_graph(row)), encoding="utf-8")

    records = audit_script.audit(graph_path, output_path)

    assert records[0]["standalone_compile_status"] == "missing_source_dependency"
    assert records[0]["missing_dependency_names"] == ["missing_dep"]
    assert records[0]["likely_classification"] == "scanner_resolution_gap"


def test_audit_compiles_without_executing_runtime_function(tmp_path: Path, monkeypatch) -> None:
    """Verify the audit compiles but does not call candidate functions."""
    monkeypatch.setattr(audit_script, "ROOT", tmp_path)
    _write(tmp_path / "src/fabricops_kit/a.py", "def helper():\n    raise RuntimeError('must not execute')\n")
    graph_path = tmp_path / "docs/reference/_data/function-call-graph.json"
    output_path = tmp_path / "docs/reference/_data/callable-orphan-audit.json"
    row = {
        "qualified_name": "fabricops_kit.a.helper",
        "function_name": "helper",
        "module": "a",
        "source_path": "src/fabricops_kit/a.py",
        "callable_kind": "function",
        "layer": "private_helper",
        "function_type": "Private helper",
        "reachability": "unreachable_runtime_asset",
        "reachability_label": "Unknown / possible entrypoint",
        "recommended_action": "Verify possible orphan",
        "signals": [],
        "callees": [],
    }
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    graph_path.write_text(json.dumps(_graph(row)), encoding="utf-8")

    records = audit_script.audit(graph_path, output_path)

    assert records[0]["standalone_compile_status"] == "compiled_with_graph_closure"


def test_unrelated_fabric_text_in_same_file_does_not_force_runtime_classification(tmp_path: Path, monkeypatch) -> None:
    """Verify Fabric text outside the extracted closure does not force runtime classification."""
    monkeypatch.setattr(audit_script, "ROOT", tmp_path)
    _write(
        tmp_path / "src/fabricops_kit/a.py",
        "from pyspark.sql import SparkSession\n\n"
        "def fabric_only():\n"
        "    return SparkSession.builder.getOrCreate()\n\n"
        "def pure_helper():\n"
        "    return 1\n",
    )
    graph_path = tmp_path / "docs/reference/_data/function-call-graph.json"
    output_path = tmp_path / "build/reports/callable-orphan-audit.json"
    row = {
        "qualified_name": "fabricops_kit.a.pure_helper",
        "function_name": "pure_helper",
        "module": "a",
        "source_path": "src/fabricops_kit/a.py",
        "callable_kind": "function",
        "layer": "private_helper",
        "function_type": "Private helper",
        "reachability": "unreachable_runtime_asset",
        "reachability_label": "Unknown / possible entrypoint",
        "recommended_action": "Verify possible orphan",
        "signals": [],
        "callees": [],
    }
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    graph_path.write_text(json.dumps(_graph(row)), encoding="utf-8")

    records = audit_script.audit(graph_path, output_path)

    assert records[0]["standalone_compile_status"] == "compiled_with_graph_closure"
    assert records[0]["likely_classification"] == "truly_unreferenced_candidate"


def test_default_output_path_is_not_generated_reference_data() -> None:
    """Verify the default audit output stays out of generated reference data."""
    relative_output = audit_script.DEFAULT_OUTPUT.relative_to(audit_script.ROOT).as_posix()

    assert relative_output == "build/reports/callable-orphan-audit.json"
    assert not relative_output.startswith("docs/reference/_data/")
