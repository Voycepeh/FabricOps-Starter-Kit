"""Validate callable architecture outputs and source-level boundaries."""

from __future__ import annotations

import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src" / "fabricops_kit"
CALLABLE_FLOW_PATH = ROOT / "docs" / "reference" / "_data" / "callable-flow.json"
DASHBOARD_PATH = ROOT / "docs" / "assets" / "callable-functions-dashboard.html"
INVENTORY_PATH = ROOT / "docs" / "assets" / "callable-functions-inventory.html"

VISIBLE_FUNCTION_TYPES = {"Public function", "Internal function"}
PRIVATE_HELPER_TYPE = "Private helper"
VISIBLE_LAYERS = {"public", "internal"}
PRIVATE_HELPER_LAYER = "private_helper"
OLD_VISIBLE_LAYER_LABELS = {"Public API", "Internal helper", "Utility", "Adapter", "Workflow", "Private"}


@dataclass(frozen=True)
class SourceFunction:
    """Top-level function discovered from source code."""

    qualified_name: str
    module: str
    name: str
    layer: str
    node: ast.FunctionDef | ast.AsyncFunctionDef
    imports: dict[str, str]


def _load_flow() -> dict[str, Any]:
    return json.loads(CALLABLE_FLOW_PATH.read_text(encoding="utf-8"))


def _module_name(path: Path) -> str:
    relative = path.relative_to(SRC_DIR).with_suffix("")
    parts = [part for part in relative.parts if part != "__init__"]
    return "fabricops_kit" if not parts else "fabricops_kit." + ".".join(parts)


def _load_public_exports() -> set[str]:
    init_path = SRC_DIR / "__init__.py"
    tree = ast.parse(init_path.read_text(encoding="utf-8"))
    exports: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets):
            if isinstance(node.value, (ast.List, ast.Tuple)):
                exports.update(item.value for item in node.value.elts if isinstance(item, ast.Constant) and isinstance(item.value, str))
    return exports


def _imports_for_module(tree: ast.Module) -> dict[str, str]:
    imports: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("fabricops_kit"):
                    imports[alias.asname or alias.name.split(".")[-1]] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith("fabricops_kit"):
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    imports[alias.asname or alias.name] = f"{node.module}.{alias.name}"
    return imports


def _source_functions() -> dict[str, SourceFunction]:
    public_exports = _load_public_exports()
    functions: dict[str, SourceFunction] = {}
    for path in sorted(SRC_DIR.rglob("*.py")):
        if ".ipynb_checkpoints" in path.parts:
            continue
        module = _module_name(path)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = _imports_for_module(tree)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qn = f"{module}.{node.name}"
                if node.name.startswith("_"):
                    layer = PRIVATE_HELPER_LAYER
                elif node.name in public_exports:
                    layer = "public"
                else:
                    layer = "internal"
                functions[qn] = SourceFunction(qn, module, node.name, layer, node, imports)
    return functions


def _resolve_call(call: ast.Call, caller: SourceFunction, functions: dict[str, SourceFunction], by_module_name: dict[tuple[str, str], str]) -> str | None:
    func = call.func
    if isinstance(func, ast.Name):
        same_module = by_module_name.get((caller.module, func.id))
        if same_module:
            return same_module
        imported = caller.imports.get(func.id)
        if imported in functions:
            return imported
        return None
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        imported_module = caller.imports.get(func.value.id)
        if imported_module:
            return by_module_name.get((imported_module, func.attr)) or (f"{imported_module}.{func.attr}" if f"{imported_module}.{func.attr}" in functions else None)
    return None


def _source_failures() -> list[str]:
    failures: list[str] = []
    functions = _source_functions()
    by_module_name = {(fn.module, fn.name): qn for qn, fn in functions.items()}
    for fn in functions.values():
        if fn.name.startswith("_") and fn.layer != PRIVATE_HELPER_LAYER:
            failures.append(f"Architecture-visible internal function is underscore-prefixed: {fn.qualified_name}")
        if fn.name.startswith("_") and fn.layer == "public":
            failures.append(f"Public function is underscore-prefixed: {fn.qualified_name}")
        if fn.layer == PRIVATE_HELPER_LAYER:
            continue
        for call in ast.walk(fn.node):
            if not isinstance(call, ast.Call):
                continue
            callee_qn = _resolve_call(call, fn, functions, by_module_name)
            if not callee_qn:
                continue
            callee = functions[callee_qn]
            if callee.layer == PRIVATE_HELPER_LAYER:
                continue
            if fn.layer == "public" and callee.layer == "public":
                failures.append(f"Public function calls public function: {fn.qualified_name} -> {callee.qualified_name}")
            if fn.layer == "internal" and callee.layer == "public":
                failures.append(f"Internal function calls public function: {fn.qualified_name} -> {callee.qualified_name}")
    return failures


def _generated_failures(flow: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    inventory = flow.get("function_inventory", [])
    summary = flow.get("summary_counts", {})
    public_surface = summary.get("public_api_surface", {})
    metrics = summary.get("callable_inventory_metrics", {})

    public_rows = [row for row in inventory if row.get("function_type") == "Public function"]
    internal_rows = [row for row in inventory if row.get("function_type") == "Internal function"]
    private_rows = [row for row in inventory if str(row.get("function_name", "")).split(".")[-1].startswith("_") or row.get("layer") == PRIVATE_HELPER_LAYER]

    for row in inventory:
        qn = str(row.get("qualified_name", ""))
        name = str(row.get("function_name", ""))
        function_type = row.get("function_type")
        layer = row.get("layer")
        if name.split(".")[-1].startswith("_"):
            if function_type != PRIVATE_HELPER_TYPE or layer != PRIVATE_HELPER_LAYER:
                failures.append(f"Private helper is counted as Public/Internal architecture row: {qn}")
            if row.get("architecture_signals") or row.get("recommended_action") == "Architecture violation":
                failures.append(f"Private helper contributes architecture violations: {qn}")
        elif function_type not in VISIBLE_FUNCTION_TYPES:
            failures.append(f"Non Public/Internal function type emitted for visible function {qn}: {function_type!r}")
        if function_type in VISIBLE_FUNCTION_TYPES and layer not in VISIBLE_LAYERS:
            failures.append(f"Visible function type has non public/internal layer for {qn}: {layer!r}")
        if function_type in OLD_VISIBLE_LAYER_LABELS or layer in OLD_VISIBLE_LAYER_LABELS:
            failures.append(f"Old architecture layer label emitted for {qn}: {function_type!r}/{layer!r}")
        if row.get("callable_kind") != "function":
            failures.append(f"Supporting object emitted as architecture inventory row: {qn}")

    function_type_counts = summary.get("function_type", {})
    if any(key in function_type_counts for key in OLD_VISIBLE_LAYER_LABELS | {PRIVATE_HELPER_TYPE}):
        failures.append("Private/old architecture labels are present in summary_counts.function_type")
    if set(function_type_counts) - VISIBLE_FUNCTION_TYPES:
        failures.append(f"Unexpected visible function type counts: {sorted(function_type_counts)}")
    if summary.get("layer", {}) != {
        "public": len(public_rows),
        "internal": len(internal_rows),
    }:
        failures.append("Visible layer counts do not match Public/Internal inventory rows")
    if function_type_counts.get("Public function") != len(public_rows):
        failures.append("Private helpers are mixed into Public function counts")
    if function_type_counts.get("Internal function") != len(internal_rows):
        failures.append("Private helpers are mixed into Internal function counts")
    if metrics.get("function_callables") != len(public_rows) + len(internal_rows):
        failures.append("Private helpers are counted in default function callable metrics")
    if metrics.get("private_helpers_to_review", 0) != len(private_rows):
        failures.append("Private helper review metric does not match private helper inventory rows")
    if public_surface.get("public_api_entrypoints") != len(public_rows):
        failures.append("Public API Surface entrypoint count does not match visible public functions")
    if "boundary_violations" in public_surface:
        failures.append("public_api_surface still emits boundary_violations instead of architecture_violation_count/architecture_violations")

    architecture_violation_edges = 0
    for flow_row in flow.get("public_entrypoint_flow", []):
        for callee in [*flow_row.get("direct_callees", []), *flow_row.get("transitive_callees", [])]:
            name = str(callee.get("callable", ""))
            if name.split(".")[-1].startswith("_") or callee.get("layer") == PRIVATE_HELPER_LAYER:
                failures.append(f"Private helper surfaced in default public flow: {flow_row.get('qualified_name')} -> {callee.get('qualified_name')}")
            if callee.get("callee_type") not in {"Public", "Internal"}:
                failures.append(f"Non Public/Internal callee type in public flow: {callee.get('qualified_name')}={callee.get('callee_type')!r}")
            if callee.get("architecture_result") == "Violation":
                architecture_violation_edges += 1
                if callee.get("violation_type") not in {"Public -> Public", "Internal -> Public"}:
                    failures.append(f"Unsupported architecture violation type: {callee.get('violation_type')!r}")
    if public_surface.get("architecture_violations", 0) > architecture_violation_edges:
        failures.append("Private helpers appear to contribute to Public API Surface architecture violation counts")

    dashboard_text = DASHBOARD_PATH.read_text(encoding="utf-8")
    inventory_text = INVENTORY_PATH.read_text(encoding="utf-8")
    if "Boundary violations" in dashboard_text or "boundary_violations" in dashboard_text:
        failures.append("Legacy boundary wording remains in dashboard default UI")
    for label in ("Utility ->", "Adapter layer", "Workflow layer", "Private layer"):
        if label in dashboard_text or label in inventory_text:
            failures.append(f"Old architecture wording remains in dashboard assets: {label}")
    return failures


def _failures(flow: dict[str, Any]) -> list[str]:
    return [*_generated_failures(flow), *_source_failures()]


def main() -> int:
    """Run callable architecture validation."""
    failures = _failures(_load_flow())
    if failures:
        print("Callable architecture validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("Callable architecture validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
