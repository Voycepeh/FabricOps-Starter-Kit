"""Generate v2 public-function call-flow JSON data."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from datetime import UTC, datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PKG_DIR = ROOT / "src" / "fabricops_kit"
PACKAGE_NAME = "fabricops_kit"
INIT_PATH = PKG_DIR / "__init__.py"
DATA_PATH = ROOT / "docs" / "reference" / "_data" / "public-function-call-flows.json"
SOURCE_JSON_URL = "https://github.com/Voycepeh/FabricOps-Starter-Kit/raw/main/docs/reference/_data/public-function-call-flows.json"
SOURCE_BLOB_BASE_URL = "https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/"
LARGE_WIDTH_THRESHOLD = 10
LARGE_DEPTH_THRESHOLD = 5
SINGAPORE_TZ = ZoneInfo("Asia/Singapore")

# v1 parity backlog for future focused PRs:
# TODO: Add JSON/YAML AI refactor packet export.
# TODO: Add compatibility mode for legacy function-call-graph consumers.
# TODO: Add a selected public function cleanup packet schema.
# TODO: Polish the dashboard mobile layout.
# TODO: Detect unresolved calls that appear to target local/internal helpers without faking the signal.


def format_singapore_timestamp(value: datetime) -> str:
    """Return a dashboard-friendly Singapore timestamp."""
    sgt_value = value.astimezone(SINGAPORE_TZ)
    hour = sgt_value.strftime("%I").lstrip("0") or "12"
    return f"{sgt_value:%d %b %Y}, {hour}:{sgt_value:%M %p} SGT"


@dataclass(frozen=True)
class FunctionInfo:
    """Top-level function metadata discovered from source."""

    function_name: str
    qualified_name: str
    source_path: str
    source_start_line: int
    source_end_line: int
    node: ast.FunctionDef | ast.AsyncFunctionDef = field(repr=False, compare=False)


@dataclass
class ModuleInfo:
    """Parsed module metadata used for static call resolution."""

    module_name: str
    path: Path
    tree: ast.Module
    imports: dict[str, str]
    module_aliases: dict[str, str]
    dispatch_targets: dict[str, set[str]]


def repo_relative(path: Path, root: Path = ROOT) -> str:
    """Return a POSIX path relative to the repository root."""
    return path.relative_to(root).as_posix()


def module_name_for_path(path: Path, pkg_dir: Path = PKG_DIR) -> str:
    """Return a package qualified module name for a Python file."""
    relative = path.relative_to(pkg_dir).with_suffix("")
    parts = [PACKAGE_NAME, *relative.parts]
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def read_public_export_names(init_path: Path = INIT_PATH) -> list[str]:
    """Read package ``__all__`` export names without executing source."""
    tree = ast.parse(init_path.read_text(encoding="utf-8"))
    constants: dict[str, list[str]] = {}
    exports: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names = [target.id for target in node.targets if isinstance(target, ast.Name)]
            values = literal_string_sequence(node.value, constants)
            for name in names:
                constants[name] = values
                if name == "__all__":
                    exports = values
    return exports


def literal_string_sequence(node: ast.AST, constants: dict[str, list[str]]) -> list[str]:
    """Return strings from literal sequence expressions used by ``__all__``."""
    if isinstance(node, (ast.Tuple, ast.List)):
        values: list[str] = []
        for elt in node.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                values.append(elt.value)
            elif isinstance(elt, ast.Starred):
                values.extend(literal_string_sequence(elt.value, constants))
        return values
    if isinstance(node, ast.Name):
        return constants.get(node.id, [])
    return []


def discover_modules(pkg_dir: Path = PKG_DIR) -> dict[str, ModuleInfo]:
    """Parse package source modules and collect import aliases."""
    modules: dict[str, ModuleInfo] = {}
    for path in sorted(pkg_dir.rglob("*.py")):
        if "tests" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        module_name = module_name_for_path(path, pkg_dir)
        imports, module_aliases = collect_imports(tree, module_name)
        modules[module_name] = ModuleInfo(module_name, path, tree, imports, module_aliases, collect_dispatch_targets(tree))
    return modules


def resolve_relative_module(module: str | None, level: int, current_module: str) -> str | None:
    """Resolve an import module name relative to the current package module."""
    if level == 0:
        return module
    package_parts = current_module.split(".")[:-1]
    base = package_parts[: max(len(package_parts) - level + 1, 1)]
    if module:
        base.extend(module.split("."))
    return ".".join(base)


def collect_imports(tree: ast.Module, module_name: str) -> tuple[dict[str, str], dict[str, str]]:
    """Collect local-name and module-alias imports that target ``fabricops_kit``."""
    imports: dict[str, str] = {}
    module_aliases: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == PACKAGE_NAME or alias.name.startswith(f"{PACKAGE_NAME}."):
                    module_aliases[alias.asname or alias.name.split(".")[-1]] = alias.name
        elif isinstance(node, ast.ImportFrom):
            source_module = resolve_relative_module(node.module, node.level, module_name)
            if not source_module or not source_module.startswith(PACKAGE_NAME):
                continue
            for alias in node.names:
                local = alias.asname or alias.name
                full = f"{source_module}.{alias.name}"
                imports[local] = full
                module_aliases[local] = full
    return imports, module_aliases


def collect_dispatch_targets(tree: ast.Module) -> dict[str, set[str]]:
    """Collect dispatch-map variable names whose values are direct function symbols."""
    targets: dict[str, set[str]] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Dict):
            continue
        names = [target.id for target in node.targets if isinstance(target, ast.Name)]
        values = {value.id for value in node.value.values if isinstance(value, ast.Name)}
        for name in names:
            targets[name] = values
    return targets


def discover_functions(modules: dict[str, ModuleInfo], root: Path = ROOT) -> dict[str, FunctionInfo]:
    """Discover top-level functions only."""
    functions = {}
    for module in modules.values():
        for node in module.tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qn = f"{module.module_name}.{node.name}"
                functions[qn] = FunctionInfo(node.name, qn, repo_relative(module.path, root), node.lineno, node.end_lineno or node.lineno, node)
    return functions


def build_name_index(functions: dict[str, FunctionInfo]) -> dict[str, set[str]]:
    """Build function-name to qualified-name lookup."""
    index: dict[str, set[str]] = {}
    for qn, info in functions.items():
        index.setdefault(info.function_name, set()).add(qn)
    return index


def resolve_call_qns(call: ast.Call, module: ModuleInfo, functions: dict[str, FunctionInfo], name_index: dict[str, set[str]]) -> set[str]:
    """Resolve one AST call to package-local function qualified names."""
    func = call.func
    if isinstance(func, ast.Name):
        if func.id in module.dispatch_targets:
            return {qn for name in module.dispatch_targets[func.id] for qn in resolve_name(name, module, functions, name_index)}
        return resolve_name(func.id, module, functions, name_index)
    if isinstance(func, ast.Subscript) and isinstance(func.value, ast.Name):
        return {qn for name in module.dispatch_targets.get(func.value.id, set()) for qn in resolve_name(name, module, functions, name_index)}
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        module_qn = module.module_aliases.get(func.value.id)
        if module_qn:
            candidate = f"{module_qn}.{func.attr}"
            return {candidate} if candidate in functions else set()
    return set()


def resolve_name(name: str, module: ModuleInfo, functions: dict[str, FunctionInfo], name_index: dict[str, set[str]]) -> set[str]:
    """Resolve a bare function name within a module."""
    imported = module.imports.get(name)
    if imported in functions:
        return {imported}
    same_file = f"{module.module_name}.{name}"
    if same_file in functions:
        return {same_file}
    return set(name_index.get(name, set())) if len(name_index.get(name, set())) == 1 else set()


def called_function_qns(info: FunctionInfo, modules: dict[str, ModuleInfo], functions: dict[str, FunctionInfo], name_index: dict[str, set[str]]) -> set[str]:
    """Return package-local functions called by a function body."""
    module_name = ".".join(info.qualified_name.split(".")[:-1])
    module = modules[module_name]
    calls: set[str] = set()
    for node in ast.walk(info.node):
        if isinstance(node, ast.Call):
            calls.update(resolve_call_qns(node, module, functions, name_index))
    return calls


def function_type(info: FunctionInfo, public_qns: set[str], root_qn: str | None = None) -> str:
    """Classify a discovered function for v2 reporting."""
    if info.qualified_name == root_qn:
        return "public_function"
    if info.qualified_name in public_qns:
        return "public_dependency"
    if info.function_name.startswith("_"):
        return "private_function"
    return "shared_function"


def classify_architecture_violation(caller: FunctionInfo | None, callee: FunctionInfo, caller_type: str | None, callee_type: str) -> dict[str, str] | None:
    """Return a deterministic architecture violation for one caller/callee edge."""
    if caller is None or caller_type is None:
        return None
    caller_public = caller_type in {"public_function", "public_dependency"}
    callee_public = callee_type in {"public_function", "public_dependency"}
    different_file = caller.source_path != callee.source_path
    if caller_public and callee_public:
        return {"type": "Type 1", "detail": "Public function calls another public function directly."}
    if caller_type == "shared_function" and callee_public:
        return {"type": "Type 2", "detail": "Shared function calls public function directly."}
    if caller_type == "private_function" and callee_public:
        return {"type": "Type 3", "detail": "Private function calls public function directly."}
    if caller_type == "shared_function" and callee_type == "private_function" and different_file:
        return {"type": "Type 4", "detail": "Shared function calls private function from another file."}
    if caller_type == "private_function" and callee_type == "private_function" and different_file:
        return {"type": "Type 5", "detail": "Private function calls private function from another file."}
    if caller_type == "private_function" and callee_type == "shared_function":
        return {"type": "Type 6", "detail": "Private function calls shared function directly."}
    return None


def build_flow(root_qn: str, modules: dict[str, ModuleInfo], functions: dict[str, FunctionInfo], public_qns: set[str]) -> tuple[list[dict[str, Any]], set[str]]:
    """Build a depth-first public function call flow."""
    name_index = build_name_index(functions)
    flow: list[dict[str, Any]] = []
    used: set[str] = set()

    def visit(qn: str, depth: int, parent: str | None, stack: set[str]) -> None:
        info = functions[qn]
        parent_info = functions[parent] if parent else None
        caller_type = function_type(parent_info, public_qns, root_qn) if parent_info else None
        current_type = function_type(info, public_qns, root_qn)
        violation = classify_architecture_violation(parent_info, info, caller_type, current_type)
        used.add(qn)
        flow.append({
            "depth": depth,
            "function_name": info.function_name,
            "qualified_name": qn,
            "source_path": info.source_path,
            "source_start_line": info.source_start_line,
            "source_end_line": info.source_end_line,
            "function_type": current_type,
            "parent_qualified_name": parent,
            "edge_type": "root" if parent is None else "direct",
            "architecture_violations": [violation] if violation else [],
            "violation_types": [violation["type"]] if violation else [],
            "violation_details": [violation["detail"]] if violation else [],
            "call_count_from_parent": 0 if parent is None else 1,
            "recursive": qn in stack,
        })
        if qn in stack:
            return
        next_stack = {*stack, qn}
        for child in sorted(called_function_qns(info, modules, functions, name_index)):
            visit(child, depth + 1, qn, next_stack)

    visit(root_qn, 0, None, set())
    enrich_flow_candidates(flow)
    return flow, used


def enrich_flow_candidates(flow: list[dict[str, Any]]) -> None:
    """Add deterministic inline and promote-to-shared candidate fields to flow rows."""
    incoming: dict[str, list[dict[str, Any]]] = {}
    for item in flow:
        if item["parent_qualified_name"]:
            incoming.setdefault(item["qualified_name"], []).append(item)
    for item in flow:
        calls = incoming.get(item["qualified_name"], [])
        distinct_callers = {call["parent_qualified_name"] for call in calls}
        repeated_by_parent = any(sum(1 for call in calls if call["parent_qualified_name"] == parent) > 1 for parent in distinct_callers)
        recursive = any(call.get("recursive") for call in calls) or item.get("recursive", False)
        item["distinct_caller_count"] = len(distinct_callers)
        item["inline_candidate"] = bool(len(distinct_callers) == 1 and len(calls) == 1 and not repeated_by_parent and not recursive)
        item["promote_to_shared_candidate"] = bool(item["function_type"] == "private_function" and len(distinct_callers) > 1)

def build_payload(root: Path = ROOT, pkg_dir: Path = PKG_DIR, init_path: Path = INIT_PATH) -> dict[str, Any]:
    """Build the v2 JSON payload."""
    modules = discover_modules(pkg_dir)
    functions = discover_functions(modules, root)
    public_names = set(read_public_export_names(init_path))
    public_qns = {qn for qn, info in functions.items() if info.function_name in public_names}
    used_all: set[str] = set()
    public_functions = []
    for root_qn in sorted(public_qns, key=lambda q: (functions[q].function_name, q)):
        flow, used = build_flow(root_qn, modules, functions, public_qns)
        used_all.update(used)
        root_info = functions[root_qn]
        direct = [item for item in flow if item["parent_qualified_name"] == root_qn]
        direct_call_count = len({item["qualified_name"] for item in direct})
        max_depth = max(item["depth"] for item in flow)
        architecture_violation_count = sum(len(item.get("architecture_violations", [])) for item in flow)
        has_large_width_or_depth = direct_call_count > LARGE_WIDTH_THRESHOLD or max_depth > LARGE_DEPTH_THRESHOLD
        has_architecture_violation = architecture_violation_count > 0
        public_signals = []
        if has_large_width_or_depth:
            public_signals.append("large_width_or_depth")
        if has_architecture_violation:
            public_signals.append("architecture_violation")
        refactor_signals = calculate_refactor_signals(root_info, flow, direct_call_count, max_depth)
        signals = public_signals
        public_functions.append({
            "function_name": root_info.function_name,
            "qualified_name": root_qn,
            "source_path": root_info.source_path,
            "source_start_line": root_info.source_start_line,
            "source_end_line": root_info.source_end_line,
            "flow": flow,
            "width": direct_call_count,
            "scope": len({item["qualified_name"] for item in flow}) - 1,
            "depth": max_depth,
            "direct_call_count": direct_call_count,
            "transitive_function_count": len({item["qualified_name"] for item in flow}) - 1,
            "max_depth": max_depth,
            "architecture_violation_count": architecture_violation_count,
            "has_large_width_or_depth": has_large_width_or_depth,
            "has_architecture_violation": has_architecture_violation,
            "public_signals": public_signals,
            "files_touched": sorted({item["source_path"] for item in flow}),
            "signals": signals,
            "refactor_signals": refactor_signals,
            "refactor_summary": summarize_refactor_signals(refactor_signals),
        })
    defined_functions = [function_record(info, public_qns) for info in sorted(functions.values(), key=lambda item: item.qualified_name)]
    unused = [unused_record(functions[qn]) for qn in sorted(set(functions) - used_all)]
    generated_at = datetime.now(UTC)
    return {
        "metadata": {
            "schema": "fabricops_public_function_call_flows_v2",
            "generated_at_utc": generated_at.isoformat(),
            "generated_at_sgt": format_singapore_timestamp(generated_at),
            "source_json_url": SOURCE_JSON_URL,
            "source": "src/fabricops_kit",
            "public_function_source": "src/fabricops_kit/__init__.py::__all__",
        },
        "public_functions": public_functions,
        "defined_functions": defined_functions,
        "used_functions": sorted(used_all),
        "defined_but_not_used": unused,
        "summary": {
            "public_function_count": len(public_functions),
            "defined_function_count": len(functions),
            "used_function_count": len(used_all),
            "defined_but_not_used_count": len(unused),
        },
    }


def calculate_refactor_signals(
    root_info: FunctionInfo,
    flow: list[dict[str, Any]],
    direct_call_count: int,
    max_depth: int,
) -> list[dict[str, Any]]:
    """Calculate structured deterministic public-level signals for a public flow."""
    refactor_signals: list[dict[str, Any]] = []
    if direct_call_count > LARGE_WIDTH_THRESHOLD or max_depth > LARGE_DEPTH_THRESHOLD:
        refactor_signals.append({
            "signal": "large_width_or_depth",
            "severity": "warning",
            "message": "Large width/depth rule triggered: Width > 10 or Depth > 5.",
            "evidence": [{"width": direct_call_count, "depth": max_depth}],
        })
    violations = [item for item in flow if item.get("architecture_violations")]
    if violations:
        refactor_signals.append({
            "signal": "architecture_violation",
            "severity": "error",
            "message": "Public flow contains deterministic architecture violation edges.",
            "evidence": [flow_evidence(item) | {"violation_types": item.get("violation_types", []), "violation_details": item.get("violation_details", [])} for item in violations],
        })
    return refactor_signals


def public_signal_label(signal: str) -> str:
    """Return the dashboard label for a public-level signal."""
    return {"large_width_or_depth": "Large width/depth", "architecture_violation": "Architecture violation"}.get(signal, signal)

def flow_evidence(item: dict[str, Any]) -> dict[str, Any]:
    """Return compact evidence for a flow node."""
    return {
        "qualified_name": item["qualified_name"],
        "function_name": item["function_name"],
        "source_path": item["source_path"],
        "source_start_line": item["source_start_line"],
        "source_end_line": item["source_end_line"],
        "function_type": item["function_type"],
        "depth": item["depth"],
    }


def summarize_refactor_signals(refactor_signals: list[dict[str, Any]]) -> str:
    """Return a short human-readable summary for structured refactor signals."""
    if not refactor_signals:
        return "No refactor signals detected."
    signal_names = ", ".join(item["signal"] for item in refactor_signals)
    return f"Review {len(refactor_signals)} refactor signal(s): {signal_names}."


def function_record(info: FunctionInfo, public_qns: set[str]) -> dict[str, Any]:
    """Return a serializable function record."""
    return {
        "function_name": info.function_name,
        "qualified_name": info.qualified_name,
        "source_path": info.source_path,
        "source_start_line": info.source_start_line,
        "source_end_line": info.source_end_line,
        "function_type": function_type(info, public_qns, info.qualified_name if info.qualified_name in public_qns else None),
    }


def unused_record(info: FunctionInfo) -> dict[str, Any]:
    """Return a serializable unused-function record."""
    return {
        "function_name": info.function_name,
        "qualified_name": info.qualified_name,
        "source_path": info.source_path,
        "source_start_line": info.source_start_line,
        "source_end_line": info.source_end_line,
        "reason": "Defined in src but not reached from any public function flow",
        "suggested_action": "review_for_deletion_or_connection",
    }



def preserve_existing_generated_timestamps(payload: dict[str, Any], data_path: Path) -> None:
    """Reuse existing generated timestamps so repeated writes are deterministic."""
    if not data_path.exists():
        return
    try:
        existing = json.loads(data_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    existing_metadata = existing.get("metadata", {})
    metadata = payload.setdefault("metadata", {})
    for key in ("generated_at_utc", "generated_at_sgt"):
        if existing_metadata.get(key):
            metadata[key] = existing_metadata[key]

def write_json(payload: dict[str, Any], data_path: Path = DATA_PATH) -> None:
    """Write only the public function call-flow JSON output."""
    data_path.parent.mkdir(parents=True, exist_ok=True)
    preserve_existing_generated_timestamps(payload, data_path)
    data_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    """Generate only the public function call-flow JSON artifact."""
    write_json(build_payload())


if __name__ == "__main__":
    main()
