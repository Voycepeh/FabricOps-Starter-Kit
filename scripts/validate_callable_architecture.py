"""Validate callable architecture outputs and source-level boundaries.

During active refactoring, architecture cleanup findings are warnings by default
while structural contract violations still fail CI. Run this script with
``--strict`` after cleanup work to promote warnings to failures.
"""

from __future__ import annotations

import ast
import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src" / "fabricops_kit"
CALLABLE_FLOW_PATH = ROOT / "docs" / "reference" / "_data" / "callable-flow.json"
OWNERSHIP_PLAN_PATH = ROOT / "docs" / "reference" / "_data" / "public-function-ownership-plan.json"
DASHBOARD_PATH = ROOT / "docs" / "assets" / "callable-functions-dashboard.html"
INVENTORY_PATH = ROOT / "docs" / "assets" / "callable-functions-inventory.html"

VISIBLE_FUNCTION_TYPES = {"Public function", "Shared helper"}
PRIVATE_HELPER_TYPE = "Private helper"
PUBLIC_FLOW_CALLEE_TYPES = {"Public", "Shared helper", PRIVATE_HELPER_TYPE}
ALLOWED_ARCHITECTURE_WARNING_TYPES = {"Same-file private dependency"}
ALLOWED_ARCHITECTURE_VIOLATION_TYPES = {"Cross-file private dependency"}
LEGACY_ARCHITECTURE_VIOLATION_TYPES = {
    "Public -> Public",
    "Internal -> Public",
    "Shared helper calls public callable",
    "Cross-callable private dependency",
    "Single-use shared helper",
    "Hidden nested helper chain",
}
VISIBLE_LAYERS = {"public", "internal"}
PRIVATE_HELPER_LAYER = "private_helper"
OLD_VISIBLE_LAYER_LABELS = {"Public API", "Utility", "Adapter", "Workflow", "Private"}
CALLABLE_FILE_PATTERN = "Public callable file -> domain shared helper -> same-file private helper"
DOMAIN_SHARED_HELPER_FILES = {"src/fabricops_kit/io/shared.py"}


@dataclass(frozen=True)
class SourceFunction:
    """Top-level function discovered from source code."""

    qualified_name: str
    module: str
    name: str
    layer: str
    node: ast.FunctionDef | ast.AsyncFunctionDef
    imports: dict[str, str]
    path: Path


@dataclass(frozen=True)
class ValidationResult:
    """Classified callable architecture validation findings."""

    failures: list[str]
    warnings: list[str]


WARNING_PREFIXES = (
    "Private helper imported outside owner file:",
    "Private helper called outside owner file:",
    "One-to-one public pass-through helper should be inlined",
    "Shared helper is underscore-prefixed but used by multiple public function files:",
)


def classify_source_finding(message: str) -> str:
    """Return the enforcement class for a source-level finding.

    The intended callable pattern is ``Public callable file -> domain shared
    helper -> same-file private helper``. Public-to-internal shared helper
    calls are allowed, internal shared helpers may use same-file private
    helpers, and cross-file private helper usage stays a strict source-level
    finding. During cleanup, the existing CLI reports these source findings as
    warnings unless strict mode is requested.
    """
    if message.startswith(WARNING_PREFIXES):
        return "warning"
    return "failure"


def classify_generated_finding(message: str) -> str:
    """Return the enforcement class for a generated-data finding."""
    if message.startswith("Unsupported architecture warning type:"):
        return "failure"
    return "failure"


def _print_group(title: str, items: list[str], *, stream: object = sys.stdout) -> None:
    print(title, file=stream)
    if items:
        for item in items:
            print(f"- {item}", file=stream)
    else:
        print("- None", file=stream)


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


def _imports_for_module(tree: ast.Module, current_module: str) -> dict[str, str]:
    imports: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("fabricops_kit"):
                    imports[alias.asname or alias.name.split(".")[-1]] = alias.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                current_parts = current_module.split(".")
                package_parts = current_parts[:-node.level]
                module_parts = [*package_parts, *([module] if module else [])]
                module = ".".join(part for part in module_parts if part)
            if module.startswith("fabricops_kit"):
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    imports[alias.asname or alias.name] = f"{module}.{alias.name}"
    return imports


def _source_functions() -> dict[str, SourceFunction]:
    public_exports = _load_public_exports()
    functions: dict[str, SourceFunction] = {}
    for path in sorted(SRC_DIR.rglob("*.py")):
        if ".ipynb_checkpoints" in path.parts:
            continue
        module = _module_name(path)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = _imports_for_module(tree, module)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qn = f"{module}.{node.name}"
                if node.name.startswith("_"):
                    layer = PRIVATE_HELPER_LAYER
                elif node.name in public_exports:
                    layer = "public"
                else:
                    layer = "internal"
                functions[qn] = SourceFunction(qn, module, node.name, layer, node, imports, path)
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




def _matching_public_passthrough_name(function_name: str, public_names: set[str]) -> str | None:
    """Return the public function name mirrored by a one-to-one shared/core wrapper."""
    for suffix in ("_shared", "_core"):
        if function_name.endswith(suffix):
            candidate = function_name[: -len(suffix)]
            if candidate in public_names:
                return candidate
    return None


def _is_direct_passthrough(fn: SourceFunction) -> bool:
    """Return whether a function only returns or calls a single implementation function."""
    executable = [
        node
        for node in fn.node.body
        if not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str))
    ]
    if len(executable) != 1:
        return False
    node = executable[0]
    if isinstance(node, ast.Return) and isinstance(node.value, ast.Call):
        return True
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        return True
    return False

def _load_ownership_plan() -> dict[str, Any]:
    if not OWNERSHIP_PLAN_PATH.exists():
        return {"migration_files": {}, "facade_files": []}
    return json.loads(OWNERSHIP_PLAN_PATH.read_text(encoding="utf-8"))


def _relative_source_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _public_owner_file(path: Path) -> str:
    return _relative_source_path(path)


def _owning_public_file_for_helper(
    helper_qn: str,
    inbound_by_qn: dict[str, set[str]],
    functions: dict[str, SourceFunction],
) -> str:
    helper = functions[helper_qn]
    public_callers = [functions[caller] for caller in inbound_by_qn.get(helper_qn, set()) if functions[caller].layer == "public"]
    same_file_public_callers = [caller for caller in public_callers if caller.path == helper.path]
    candidates = same_file_public_callers or public_callers
    if not candidates:
        return _public_owner_file(helper.path)
    return _public_owner_file(sorted(candidates, key=lambda item: (str(item.path), item.name))[0].path)


def _source_call_edges(
    functions: dict[str, SourceFunction],
    by_module_name: dict[tuple[str, str], str],
) -> dict[str, set[str]]:
    edges: dict[str, set[str]] = {qn: set() for qn in functions}
    for fn in functions.values():
        for call in ast.walk(fn.node):
            if isinstance(call, ast.Call):
                callee_qn = _resolve_call(call, fn, functions, by_module_name)
                if callee_qn:
                    edges[fn.qualified_name].add(callee_qn)
    return edges

def _source_failures() -> list[str]:
    failures: list[str] = []
    functions = _source_functions()
    by_module_name = {(fn.module, fn.name): qn for qn, fn in functions.items()}
    call_edges = _source_call_edges(functions, by_module_name)
    inbound_by_qn: dict[str, set[str]] = {qn: set() for qn in functions}
    for caller, callees in call_edges.items():
        for callee in callees:
            inbound_by_qn.setdefault(callee, set()).add(caller)

    ownership_plan = _load_ownership_plan()
    completed_migrations = ownership_plan.get("completed_migrations") or {}
    enforced_owner_roots = [
        ROOT / migration["owner_package"]
        for migration in completed_migrations.values()
        if migration.get("owner_package")
    ]

    def enforces_helper_boundary(helper: SourceFunction) -> bool:
        if not enforced_owner_roots:
            return True
        return any(helper.path == root or root in helper.path.parents for root in enforced_owner_roots)
    migration_files = set((ownership_plan.get("migration_files") or {}).keys())
    facade_files = set(ownership_plan.get("facade_files") or []) | {"src/fabricops_kit/__init__.py"}

    public_by_file: dict[str, list[SourceFunction]] = {}
    for fn in functions.values():
        if fn.layer == "public":
            public_by_file.setdefault(_public_owner_file(fn.path), []).append(fn)

    for completed_file, migration in completed_migrations.items():
        if migration.get("status") == "facade_only" and completed_file in public_by_file:
            names = ", ".join(sorted(fn.name for fn in public_by_file[completed_file]))
            failures.append(f"Completed migration facade still defines public functions: {completed_file} ({names})")

    for source_path, public_functions in public_by_file.items():
        if len(public_functions) > 1 and source_path not in facade_files and source_path not in migration_files:
            names = ", ".join(sorted(fn.name for fn in public_functions))
            failures.append(f"Public function file contains multiple public functions: {source_path} ({names})")

    for fn in functions.values():
        if fn.name.startswith("_") and fn.layer != PRIVATE_HELPER_LAYER:
            failures.append(f"Architecture-visible internal function is underscore-prefixed: {fn.qualified_name}")
        if fn.name.startswith("_") and fn.layer == "public":
            failures.append(f"Public function is underscore-prefixed: {fn.qualified_name}")

        for local_name, imported_qn in fn.imports.items():
            if imported_qn in functions and functions[imported_qn].layer == PRIVATE_HELPER_LAYER and enforces_helper_boundary(functions[imported_qn]):
                owner_file = _owning_public_file_for_helper(imported_qn, inbound_by_qn, functions)
                if _relative_source_path(fn.path) != owner_file:
                    failures.append(
                        "Private helper imported outside owner file: "
                        f"{fn.qualified_name} imports {imported_qn} as {local_name}"
                    )

        for callee_qn in call_edges.get(fn.qualified_name, set()):
            callee = functions[callee_qn]
            if callee.layer == PRIVATE_HELPER_LAYER and enforces_helper_boundary(callee) and fn.path != callee.path:
                failures.append(f"Private helper called outside owner file: {fn.qualified_name} -> {callee.qualified_name}")
            if fn.layer == "public" and callee.layer == "public":
                failures.append(f"Public function calls public function: {fn.qualified_name} -> {callee.qualified_name}")
            if fn.layer == "internal" and callee.layer == "public":
                failures.append(f"Shared helper calls public function: {fn.qualified_name} -> {callee.qualified_name}")

    public_names = {fn.name for fn in functions.values() if fn.layer == "public"}
    migrated_public_names = {
        name
        for migration in completed_migrations.values()
        for name in migration.get("public_functions", [])
    }
    for qn, fn in functions.items():
        mirrored_public_name = _matching_public_passthrough_name(fn.name, public_names)
        if mirrored_public_name not in migrated_public_names:
            continue
        if not mirrored_public_name:
            continue
        public_callers = [functions[caller] for caller in inbound_by_qn.get(qn, set()) if functions[caller].layer == "public"]
        if len(public_callers) == 1 and public_callers[0].name == mirrored_public_name and _is_direct_passthrough(fn):
            failures.append(
                "One-to-one public pass-through helper should be inlined into the owner file: "
                f"{public_callers[0].qualified_name} -> {fn.qualified_name}"
            )

    for helper_qn, helper in functions.items():
        if helper.layer != PRIVATE_HELPER_LAYER or not enforces_helper_boundary(helper):
            continue
        public_owner_files = {
            _public_owner_file(functions[caller].path)
            for caller in inbound_by_qn.get(helper_qn, set())
            if functions[caller].layer == "public"
        }
        if len(public_owner_files) > 1:
            failures.append(
                "Shared helper is underscore-prefixed but used by multiple public function files: "
                f"{helper_qn} ({', '.join(sorted(public_owner_files))})"
            )
    return failures

def _generated_failures(flow: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    inventory = flow.get("function_inventory", [])
    summary = flow.get("summary_counts", {})
    public_surface = summary.get("public_api_surface", {})
    metrics = summary.get("callable_inventory_metrics", {})

    public_rows = [row for row in inventory if row.get("function_type") == "Public function"]
    internal_rows = [row for row in inventory if row.get("function_type") == "Shared helper"]
    private_rows = [row for row in inventory if str(row.get("function_name", "")).split(".")[-1].startswith("_") or row.get("layer") == PRIVATE_HELPER_LAYER]

    for row in inventory:
        qn = str(row.get("qualified_name", ""))
        name = str(row.get("function_name", ""))
        function_type = row.get("function_type")
        layer = row.get("layer")
        if name.split(".")[-1].startswith("_"):
            if function_type != PRIVATE_HELPER_TYPE or layer != PRIVATE_HELPER_LAYER:
                failures.append(f"Private helper is counted as Public/Shared helper architecture row: {qn}")
            if row.get("architecture_signals") or row.get("recommended_action") == "Architecture violation":
                failures.append(f"Private helper contributes architecture violations: {qn}")
        elif function_type not in VISIBLE_FUNCTION_TYPES:
            failures.append(f"Non Public/Shared helper function type emitted for visible function {qn}: {function_type!r}")
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
        failures.append("Visible layer counts do not match Public/Shared helper inventory rows")
    if function_type_counts.get("Public function") != len(public_rows):
        failures.append("Private helpers are mixed into Public function counts")
    if function_type_counts.get("Shared helper") != len(internal_rows):
        failures.append("Private helpers are mixed into Shared helper counts")
    if metrics.get("function_callables") != len(public_rows) + len(internal_rows):
        failures.append("Private helpers are counted in default function callable metrics")
    if metrics.get("private_helpers_to_review", 0) != len(private_rows):
        failures.append("Private helper review metric does not match private helper inventory rows")
    if public_surface.get("public_api_entrypoints") != len(public_rows):
        failures.append("Public API Surface entrypoint count does not match visible public functions")
    if "boundary_violations" in public_surface:
        failures.append("public_api_surface still emits boundary_violations instead of architecture_violation_count/architecture_violations")

    architecture_violation_edges = 0
    architecture_violation_flows = 0
    for flow_row in flow.get("public_entrypoint_flow", []):
        flow_violation_edges = 0
        for callee in flow_row.get("transitive_callees", []):
            if callee.get("function_type") == "Supporting object" or callee.get("layer") == "supporting_object":
                failures.append(f"Supporting object surfaced in public flow: {callee.get('qualified_name')}")
            if callee.get("callee_type") not in PUBLIC_FLOW_CALLEE_TYPES:
                failures.append(f"Non callable-layer callee type in public flow: {callee.get('qualified_name')}={callee.get('callee_type')!r}")
            if callee.get("architecture_result") == "Warning":
                warning_type = callee.get("violation_type")
                if warning_type not in ALLOWED_ARCHITECTURE_WARNING_TYPES:
                    failures.append(f"Unsupported architecture warning type: {warning_type!r}")
            if callee.get("architecture_result") == "Violation":
                architecture_violation_edges += 1
                flow_violation_edges += 1
                violation_type = callee.get("violation_type")
                if violation_type in LEGACY_ARCHITECTURE_VIOLATION_TYPES:
                    failures.append(f"Legacy architecture violation type emitted: {violation_type!r}")
                elif violation_type not in ALLOWED_ARCHITECTURE_VIOLATION_TYPES:
                    failures.append(f"Unsupported architecture violation type: {violation_type!r}")
        if flow_row.get("architecture_violation_count", 0) != flow_violation_edges:
            failures.append(
                "Public flow architecture violation count does not match violation rows: "
                f"{flow_row.get('qualified_name')} has {flow_row.get('architecture_violation_count')} count and {flow_violation_edges} row(s)"
            )
        if flow_violation_edges:
            architecture_violation_flows += 1
    if public_surface.get("architecture_violations", 0) != architecture_violation_flows:
        failures.append("Public API Surface architecture violation count does not match public flow violation rows")

    dashboard_text = DASHBOARD_PATH.read_text(encoding="utf-8")
    inventory_text = INVENTORY_PATH.read_text(encoding="utf-8")
    if "Boundary violations" in dashboard_text or "boundary_violations" in dashboard_text:
        failures.append("Legacy boundary wording remains in dashboard default UI")
    for legacy_type in LEGACY_ARCHITECTURE_VIOLATION_TYPES:
        if legacy_type in dashboard_text or legacy_type in inventory_text:
            failures.append(f"Legacy architecture violation wording remains in dashboard assets: {legacy_type}")
    for label in ("Utility ->", "Adapter layer", "Workflow layer", "Private layer"):
        if label in dashboard_text or label in inventory_text:
            failures.append(f"Old architecture wording remains in dashboard assets: {label}")
    return failures


def _failures(flow: dict[str, Any]) -> list[str]:
    """Return all blocking generated and source validation failures.

    Kept for tests that exercise generated-data blocking contracts directly.
    Cleanup-only source findings are exposed through ``validate`` warnings.
    """
    return [*_generated_failures(flow), *_source_failures()]


def validate(flow: dict[str, Any] | None = None) -> ValidationResult:
    """Return classified architecture validation findings."""
    if flow is None:
        try:
            flow = _load_flow()
        except (OSError, json.JSONDecodeError) as exc:
            return ValidationResult(failures=[f"callable-flow.json cannot be loaded or parsed: {exc}"], warnings=[])

    failures = [finding for finding in _generated_failures(flow) if classify_generated_finding(finding) == "failure"]
    warnings: list[str] = []
    for finding in _source_failures():
        if classify_source_finding(finding) == "warning":
            warnings.append(finding)
        else:
            failures.append(finding)
    return ValidationResult(failures=failures, warnings=warnings)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="Promote cleanup warnings to failures.")
    parser.add_argument("--json", action="store_true", help="Print a structured JSON summary.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run callable architecture validation."""
    args = _parser().parse_args(argv)
    result = validate()
    exit_code = 1 if result.failures or (args.strict and result.warnings) else 0

    if args.json:
        print(json.dumps({**asdict(result), "strict": args.strict, "exit_code": exit_code}, indent=2))
        return exit_code

    if exit_code:
        print("Callable architecture validation failed.", file=sys.stderr)
        _print_group("Blocking failures:", result.failures, stream=sys.stderr)
        warning_title = "Warnings promoted to failures:" if args.strict else "Warnings:"
        _print_group(warning_title, result.warnings, stream=sys.stderr)
    elif result.warnings:
        print("Callable architecture validation completed with warnings.")
        _print_group("Blocking failures:", result.failures)
        _print_group("Warnings:", result.warnings)
    else:
        print("Callable architecture validation passed.")
        _print_group("Blocking failures:", result.failures)
        _print_group("Warnings:", result.warnings)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
