#!/usr/bin/env python3
"""Audit possible orphan callables against generated call graph closure.

This script is intentionally read-only for runtime source. It compares the
function-call-graph export with source/reference searches and writes an audit
JSON file for maintainer review.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GRAPH = ROOT / "docs/reference/_data/function-call-graph.json"
DEFAULT_OUTPUT = ROOT / "docs/reference/_data/callable-orphan-audit.json"
FABRIC_PATTERNS = (
    "pyspark", "SparkSession", "mssparkutils", "notebookutils", "synapsesql",
    "delta", "lakehouse", "warehouse", "dbutils",
)
DYNAMIC_PATTERNS = (
    "dispatch", "getattr", "globals()[", "locals()[", "callback", "on_click",
    "observe(", "functools.partial", "partial(", "lambda", "property",
)
EXPECTED_KEYS = (
    "qualified_name", "function_name", "module", "source_path", "source_start_line",
    "source_end_line", "callable_kind", "layer", "function_type", "reachability",
    "reachability_label", "current_recommended_action", "current_signals",
    "graph_dependency_count", "graph_dependencies", "standalone_compile_status",
    "missing_dependency_names", "missing_dependency_evidence", "source_references_count",
    "source_references", "template_references_count", "template_references",
    "test_references_count", "test_references", "docs_metadata_referenced",
    "docs_references_count", "docs_references", "likely_classification", "suggested_next_action",
)


@dataclass(frozen=True)
class NodeRef:
    """Source location for a callable AST node."""

    path: Path
    node: ast.AST
    parent: ast.AST | None


def load_graph(path: Path) -> dict[str, Any]:
    """Load a generated function-call-graph JSON document."""
    return json.loads(path.read_text(encoding="utf-8"))


def src_path(path_text: str) -> Path:
    """Resolve a graph source path relative to the repository root."""
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def index_source_nodes(src_root: Path | None = None) -> dict[tuple[str, str], NodeRef]:
    """Index top-level functions, classes, and class methods by path and name."""
    src_root = src_root or ROOT / "src/fabricops_kit"
    index: dict[tuple[str, str], NodeRef] = {}
    for path in src_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        rel = path.relative_to(ROOT).as_posix()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                index[(rel, node.name)] = NodeRef(path, node, None)
                if isinstance(node, ast.ClassDef):
                    for child in node.body:
                        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            index[(rel, child.name)] = NodeRef(path, child, node)
    return index


def module_imports(path: Path) -> list[ast.stmt]:
    """Return import statements from a Python module."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]


def callable_dependencies(row: dict[str, Any], inventory_by_qn: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Return local dependencies listed by the graph for one callable row."""
    deps: list[dict[str, Any]] = []
    seen: set[str] = set()
    stack = list(row.get("callees") or [])
    while stack:
        dep = stack.pop(0)
        qn = dep.get("qualified_name")
        if not qn or qn in seen:
            continue
        seen.add(qn)
        inv = inventory_by_qn.get(qn, dep)
        if str(inv.get("source_path", dep.get("source_path", ""))).startswith("src/fabricops_kit"):
            deps.append(inv | {"qualified_name": qn, "function_name": dep.get("function_name") or inv.get("function_name")})
            stack.extend(inv.get("callees") or [])
    return deps


def names_loaded(nodes: list[ast.AST]) -> set[str]:
    """Collect loaded Name identifiers from AST nodes."""
    return {n.id for node in nodes for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}


def defined_names(nodes: list[ast.AST]) -> set[str]:
    """Collect names defined by imports and top-level callable nodes."""
    names = set(dir(builtins)) | {"Any", "Path", "pd", "F", "T"}
    for node in nodes:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Import):
            names |= {alias.asname or alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            names |= {alias.asname or alias.name for alias in node.names if alias.name != "*"}
    return names


def compile_status(row: dict[str, Any], deps: list[dict[str, Any]], index: dict[tuple[str, str], NodeRef]) -> tuple[str, list[str], list[str]]:
    """Compile an isolated module made from imports, target node, and graph dependencies."""
    source = row.get("source_path", "")
    ref = index.get((source, row.get("function_name", "")))
    if ref is None:
        return "missing_source_dependency", [row.get("function_name", "")], [f"Target source node not found in {source}"]
    text = ref.path.read_text(encoding="utf-8")
    if ref.parent is not None or row.get("callable_kind") in {"method", "property"}:
        return "skipped_class_or_method_context", [], ["Callable is a class member and may require class context"]
    if any(pat.lower() in text.lower() for pat in FABRIC_PATTERNS):
        return "skipped_fabric_runtime", [], ["Source module mentions Fabric/Spark runtime patterns"]
    target_and_deps: list[ast.AST] = [ref.node]
    missing: list[str] = []
    evidence: list[str] = []
    for dep in deps:
        dep_ref = index.get((dep.get("source_path", ""), dep.get("function_name", "")))
        if dep_ref is None or dep_ref.parent is not None:
            missing.append(dep.get("function_name", ""))
            evidence.append(f"Graph dependency source not extractable: {dep.get('qualified_name')}")
        else:
            target_and_deps.append(dep_ref.node)
    imports = module_imports(ref.path)
    body = imports + [ast.fix_missing_locations(ast.parse(ast.unparse(n)).body[0]) for n in target_and_deps]
    module = ast.fix_missing_locations(ast.Module(body=body, type_ignores=[]))
    try:
        compile(module, f"<callable-orphan-audit:{row.get('qualified_name')}>", "exec")
    except SyntaxError as exc:
        return "syntax_or_extraction_error", missing, evidence + [str(exc)]
    missing_names = sorted((names_loaded(target_and_deps) - defined_names(body)) & inventory_by_source(index))
    missing.extend(n for n in missing_names if n not in missing)
    if missing:
        return "missing_source_dependency", missing, evidence
    return "compiled_with_graph_closure", [], evidence


def inventory_by_source(index: dict[tuple[str, str], NodeRef]) -> set[dict[str, str]]:
    """Return index rows as simple dictionaries for name matching."""
    return {name for _, name in index}


def reference_matches(needles: list[str], roots: list[Path]) -> list[dict[str, Any]]:
    """Search literal references in text-like files under selected roots."""
    results: list[dict[str, Any]] = []
    suffixes = {".py", ".md", ".ipynb"}
    for root in roots:
        if not root.exists():
            continue
        paths = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix in suffixes]
        for path in paths:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for lineno, line in enumerate(text.splitlines(), 1):
                if any(n and n in line for n in needles):
                    results.append({"path": path.relative_to(ROOT).as_posix(), "line": lineno, "text": line.strip()[:240]})
                    break
    return results


def classify(row: dict[str, Any], status: str, missing: list[str], refs: dict[str, list[dict[str, Any]]], docs_meta: bool, deps: list[dict[str, Any]], source_text: str) -> tuple[str, str]:
    """Classify one audit record and suggest a next action."""
    has_src_refs = len(refs["source"]) > 1
    dynamic = any(p.lower() in source_text.lower() for p in DYNAMIC_PATTERNS)
    fabric = any(p.lower() in source_text.lower() for p in FABRIC_PATTERNS)
    if status == "compiled_with_graph_closure" and row.get("reachability") != "unreachable_runtime_asset":
        return "graph_ok_reachable_shape", "No orphan action; reachable shape compiles."
    if fabric or status == "skipped_fabric_runtime":
        return "fabric_runtime_dependency", "Review as Fabric/runtime-only support before any cleanup."
    if status == "skipped_class_or_method_context":
        return "class_or_method_context", "Review with the owning class lifecycle rather than as a standalone function."
    if dynamic:
        return "dynamic_dispatch_or_callback", "Inspect dynamic dispatch/callback paths before changing code."
    if status == "missing_source_dependency" or (has_src_refs and not deps):
        return "scanner_resolution_gap", "Improve scanner edge resolution or manually verify source references."
    only_tests = refs["tests"] and not has_src_refs and not refs["templates"] and not docs_meta and not refs["docs"]
    if only_tests and row.get("layer") != "public" and not deps:
        return "test_only_source_candidate", "Review whether this helper belongs in tests or should remain as tested support."
    if docs_meta and not has_src_refs and not refs["templates"]:
        return "docs_metadata_only", "Review docs metadata registration before considering cleanup."
    if row.get("reachability") == "unreachable_runtime_asset" and status == "compiled_with_graph_closure":
        return "truly_unreferenced_candidate", "Safe-to-investigate deletion candidate; do not delete without owner review."
    return "needs_manual_review", "Manually inspect references and runtime usage."


def audit(graph_path: Path, output_path: Path, limit: int | None = None) -> list[dict[str, Any]]:
    """Run the callable orphan audit and write JSON records."""
    graph = load_graph(graph_path)
    inventory = graph.get("function_inventory", [])
    inventory_by_qn = {r.get("qualified_name", ""): r for r in inventory}
    index = index_source_nodes()
    targets = [r for r in inventory if r.get("reachability") == "unreachable_runtime_asset" or r.get("recommended_action") == "Verify possible orphan"]
    if limit:
        targets = targets[:limit]
    records = []
    docs_meta_text = (ROOT / "scripts/reference_docs_metadata.py").read_text(encoding="utf-8", errors="ignore") if (ROOT / "scripts/reference_docs_metadata.py").exists() else ""
    for row in targets:
        deps = callable_dependencies(row, inventory_by_qn)
        status, missing, evidence = compile_status(row, deps, index)
        needles = [row.get("function_name", ""), row.get("qualified_name", "")]
        refs = {
            "source": reference_matches(needles, [ROOT / "src/fabricops_kit"]),
            "templates": reference_matches(needles, [ROOT / "templates"]),
            "tests": reference_matches(needles, [ROOT / "tests"]),
            "docs": reference_matches(needles, [ROOT / "docs"]),
        }
        source_file = src_path(row.get("source_path", ""))
        source_text = source_file.read_text(encoding="utf-8", errors="ignore") if source_file.exists() else ""
        docs_meta = any(n and n in docs_meta_text for n in needles)
        classification, action = classify(row, status, missing, refs, docs_meta, deps, source_text)
        record = {
            "qualified_name": row.get("qualified_name", ""), "function_name": row.get("function_name", ""),
            "module": row.get("module", ""), "source_path": row.get("source_path", ""),
            "source_start_line": row.get("source_start_line"), "source_end_line": row.get("source_end_line"),
            "callable_kind": row.get("callable_kind", ""), "layer": row.get("layer", ""),
            "function_type": row.get("function_type", ""), "reachability": row.get("reachability", ""),
            "reachability_label": row.get("reachability_label", ""),
            "current_recommended_action": row.get("recommended_action", ""), "current_signals": row.get("signals", []),
            "graph_dependency_count": len(deps), "graph_dependencies": [d.get("qualified_name", "") for d in deps],
            "standalone_compile_status": status, "missing_dependency_names": missing, "missing_dependency_evidence": evidence,
            "source_references_count": len(refs["source"]), "source_references": refs["source"],
            "template_references_count": len(refs["templates"]), "template_references": refs["templates"],
            "test_references_count": len(refs["tests"]), "test_references": refs["tests"],
            "docs_metadata_referenced": docs_meta, "docs_references_count": len(refs["docs"]), "docs_references": refs["docs"],
            "likely_classification": classification, "suggested_next_action": action,
        }
        records.append({k: record[k] for k in EXPECTED_KEYS})
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"summary": summarize(records), "records": records}, indent=2) + "\n", encoding="utf-8")
    print_summary(records, output_path)
    return records


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Build grouped audit counts."""
    return {
        "record_count": len(records),
        "by_compile_status": dict(Counter(r["standalone_compile_status"] for r in records)),
        "by_classification": dict(Counter(r["likely_classification"] for r in records)),
        "safe_to_investigate_deletion_count": sum(1 for r in records if r["likely_classification"] == "truly_unreferenced_candidate"),
    }


def print_summary(records: list[dict[str, Any]], output_path: Path) -> None:
    """Print a concise grouped console summary."""
    summary = summarize(records)
    print(f"Audited {summary['record_count']} possible orphan callables")
    print("Compile status:")
    for key, value in summary["by_compile_status"].items():
        print(f"  - {key}: {value}")
    print("Classification:")
    for key, value in summary["by_classification"].items():
        print(f"  - {key}: {value}")
    print(f"Safe-to-investigate deletion candidates: {summary['safe_to_investigate_deletion_count']}")
    print(f"Wrote {output_path.relative_to(ROOT)}")


def main() -> None:
    """Parse CLI arguments and run the audit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    audit(args.graph if args.graph.is_absolute() else ROOT / args.graph, args.output if args.output.is_absolute() else ROOT / args.output, args.limit)


if __name__ == "__main__":
    main()
