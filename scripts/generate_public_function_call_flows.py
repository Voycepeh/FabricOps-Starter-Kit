"""Generate v2 public-function call-flow data and dashboard."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from datetime import UTC, datetime
import html
import json
from pathlib import Path
from zoneinfo import ZoneInfo
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PKG_DIR = ROOT / "src" / "fabricops_kit"
PACKAGE_NAME = "fabricops_kit"
INIT_PATH = PKG_DIR / "__init__.py"
DATA_PATH = ROOT / "docs" / "reference" / "_data" / "public-function-call-flows.json"
DASHBOARD_PATH = ROOT / "docs" / "assets" / "public-function-call-flows-dashboard.html"
DASHBOARD_DATA_URL = "../reference/_data/public-function-call-flows.json"
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
    for root_qn in sorted(public_qns, key=lambda q: functions[q].function_name):
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


def render_dashboard(
    payload: dict[str, Any] | None = None,
    *,
    embed_json: bool = False,
    data_url: str = DASHBOARD_DATA_URL,
) -> str:
    """Render the dashboard HTML document.

    Parameters
    ----------
    payload : dict[str, Any] | None, optional
        Payload to embed when ``embed_json`` is true. The default published
        dashboard fetches JSON from ``data_url`` instead of embedding it.
    embed_json : bool, default=False
        Whether to embed ``payload`` for standalone/debug use.
    data_url : str, default=DASHBOARD_DATA_URL
        Relative URL used by the published dashboard to fetch v2 JSON.

    """
    embedded_script = ""
    load_expression = f"loadDashboardData('{data_url}')"
    if embed_json:
        if payload is None:
            raise ValueError("payload is required when embed_json is true")
        escaped = html.escape(json.dumps(payload, indent=2))
        embedded_script = f'<script id="public-function-call-flows-json" type="application/json">{escaped}</script>'
        load_expression = "Promise.resolve(JSON.parse(document.getElementById('public-function-call-flows-json').textContent))"

    html_doc = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Public Function Call Flows V2</title>
<style>
body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:0;color:#172033;background:#f8fafc}header,main{max-width:1180px;margin:auto;padding:1rem}.overview-help{color:#475569}.workflow-tabs,.table-actions,.toolbar-row{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;margin:.75rem 0}.workflow-tab{border:1px solid #cbd5e1;background:#fff;border-radius:999px;padding:.55rem .85rem}.workflow-tab.active,.primary-action{background:#1d4ed8;color:#fff;border-color:#1d4ed8}.workflow-panel{display:none}.workflow-panel.active{display:block}.architecture-summary-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(9.5rem,1fr));gap:.5rem;margin:.75rem 0}.architecture-summary-card,.filter-panel,.export-toolbar,.flow-details{padding:.75rem;border:1px solid #dbe3ef;border-radius:.75rem;background:#fff}.architecture-summary-card strong{display:block;font-size:1.55rem}.risk{border-color:#fecaca!important;background:#fef2f2!important}.review{border-color:#fde68a!important;background:#fffbeb!important}.info{border-color:#bfdbfe!important;background:#eff6ff!important}.good{border-color:#bbf7d0!important;background:#f0fdf4!important}.rule-note{border-left:.35rem solid #f59e0b;background:#fffbeb}.filter-panel{display:grid;grid-template-columns:minmax(16rem,1fr) repeat(2,minmax(11rem,15rem)) auto;gap:.55rem;align-items:end}.filter-field{display:flex;flex-direction:column;font-size:.82rem;font-weight:800;gap:.2rem}input,select,button{padding:.43rem .52rem;border:1px solid #cbd5e1;border-radius:.45rem;background:#fff}button{cursor:pointer;font-weight:800;color:#1d4ed8}.table-wrap{overflow-x:auto;background:#fff;border:1px solid #dbe3ef;border-radius:.75rem}table{width:100%;border-collapse:collapse}#publicFlowTable{min-width:1040px}#selectedCallableInventoryTable{min-width:1320px}#definedButNotUsedTable{min-width:960px}th,td{padding:.55rem .65rem;border-bottom:1px solid #e2e8f0;text-align:left;vertical-align:top;font-size:.84rem;overflow-wrap:break-word}th{background:#eef2f7;color:#334155;font-size:.75rem;line-height:1.25;word-break:keep-all}.col-function{min-width:18rem}.col-file{min-width:22rem}.col-select{min-width:7.5rem}.col-type{min-width:7rem}.col-small{min-width:6.5rem}.col-signals{min-width:12rem}.col-parent{min-width:16rem}.col-detail{min-width:20rem}.col-reason{min-width:14rem}.sort-button{border:0;background:transparent;padding:0;color:#1d4ed8;text-align:left}.sort-button:after{content:' ↕';color:#64748b}tr[data-public-flow-row]{cursor:pointer}tr.active,.row-selected{background:#eff6ff}.source-link{color:#1d4ed8;text-decoration:underline}.badge{display:inline-flex;margin:.06rem;padding:.12rem .38rem;border-radius:999px;font-size:.7rem;font-weight:800;background:#e0e7ff;color:#3730a3}.warn{background:#fef3c7;color:#92400e}.danger{background:#fee2e2;color:#991b1b}.muted{background:#f1f5f9;color:#475569}.flow-summary-card{padding:.75rem;border:1px solid #bfdbfe;border-radius:.75rem;background:#eff6ff}.flow-meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(135px,1fr));gap:.5rem}.flow-meta div{padding:.45rem;border:1px solid #e2e8f0;border-radius:.5rem;background:#fff}.flow-tree{border:1px solid #dbe3ef;border-radius:.75rem;padding:.7rem;background:#fff}.tree-node{margin:.32rem 0;padding:.55rem .65rem;border:1px solid #dbe3ef;border-radius:.7rem;background:#fff}.tree-row-main{display:flex;flex-wrap:wrap;align-items:center;gap:.3rem}.tree-function{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-weight:900;color:#1d4ed8}.tree-file{display:inline-flex;padding:.12rem .38rem;border-radius:.38rem;font-size:.7rem;font-weight:800;background:#f1f5f9;color:#475569}.tree-type-public-function{background:#dbeafe;color:#1e40af}.tree-type-public-dependency{background:#ede9fe;color:#5b21b6}.tree-type-shared-function{background:#dcfce7;color:#166534}.tree-type-private-function{background:#f1f5f9;color:#475569}@media(max-width:760px){header,main{padding:.75rem}.filter-panel{grid-template-columns:1fr}}
</style></head><body><header><h1>Public Function Call Flows V2</h1><p class="overview-help">Review deterministic public-function architecture signals, then export one focused AI refactor packet.</p><p class="overview-help"><strong id="generatedTimestamp">Generated: loading…</strong> · Source JSON: <a id="sourceJsonLink" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/raw/main/docs/reference/_data/public-function-call-flows.json" target="_blank" rel="noopener">Download from GitHub</a></p></header><main>
<nav class="workflow-tabs"><button class="workflow-tab active" type="button" data-workflow-tab="architecture">Public function architecture</button><button class="workflow-tab" type="button" data-workflow-tab="orphan">Orphan function cleanup</button></nav>
<section id="architectureWorkflow" class="workflow-panel active"><section class="architecture-summary-cards"><article class="architecture-summary-card info"><span>Public functions</span><strong id="card-public">0</strong></article><article class="architecture-summary-card risk"><span>Architecture violation</span><strong id="card-warnings">0</strong></article><article class="architecture-summary-card review"><span>Large width/depth</span><strong id="card-large">0</strong></article><article class="architecture-summary-card good"><span>Used functions</span><strong id="card-used">0</strong></article><article class="architecture-summary-card info"><span>Defined functions</span><strong id="card-defined">0</strong></article></section>
<section class="flow-details rule-note"><strong>Large width / depth rule:</strong> Width &gt; 10 or Depth &gt; 5. This yellow signal uses <code>large_width_or_depth</code>. Width means number of direct package-local calls from the selected public function. Depth means the deepest nested call path. Scope means total downstream functions reached by the public function flow.</section>
<section class="filter-panel"><label class="filter-field">Search <input id="searchBox" type="search" placeholder="Function, file, signals"></label><label class="filter-field">Signal <select id="signalFilter"><option value="">All signals</option></select></label><span></span><button id="clearFilters" type="button">Clear filters</button></section><section class="table-actions"><strong id="rowCount">0 public functions</strong><small id="dataLoadStatus"></small></section>
<section class="table-wrap"><table id="publicFlowTable"><colgroup><col class="col-function"><col class="col-file"><col class="col-small"><col class="col-small"><col class="col-small"><col class="col-small"><col class="col-signals"></colgroup><thead><tr><th class="col-function"><button class="sort-button" data-sort="function_name" type="button">Function</button></th><th class="col-file"><button class="sort-button" data-sort="source_path" type="button">File</button></th><th class="col-small"><button class="sort-button" data-sort="width" type="button">Width</button></th><th class="col-small"><button class="sort-button" data-sort="scope" type="button">Scope</button></th><th class="col-small"><button class="sort-button" data-sort="depth" type="button">Depth</button></th><th class="col-small"><button class="sort-button" data-sort="files_touched" type="button">Files</button></th><th class="col-signals">Signals</th></tr></thead><tbody id="public-table"></tbody></table></section>
<section id="selected-public-function-panel" class="flow-details"><h2>Selected public function</h2><div id="selectedSummary"></div><h3>Call tree</h3><div id="selected-call-tree" class="flow-tree"></div><h3>Selected callable inventory</h3><section class="filter-panel"><label class="filter-field">Search inventory <input id="inventorySearch" type="search" placeholder="Function, type, file, parent"></label><label class="filter-field">Type <select id="inventoryTypeFilter"><option value="">All types</option></select></label><span></span><button id="clearInventoryFilters" type="button">Clear inventory filters</button></section><div class="table-actions"><button id="selectVisibleInventory" type="button">Select all visible inventory rows</button><button id="clearInventory" type="button">Clear selected inventory rows</button><strong id="inventorySelectedCount">0 selected</strong><small id="inventoryRowCount">0 rows</small></div><div class="table-wrap"><table id="selectedCallableInventoryTable"><colgroup><col class="col-select"><col class="col-function"><col class="col-type"><col class="col-file"><col class="col-small"><col class="col-parent"><col class="col-small"><col class="col-detail"><col class="col-small"><col class="col-small"></colgroup><thead><tr><th class="col-select">Select</th><th class="col-function"><button class="sort-button" data-inventory-sort="function_name" type="button">Function</button></th><th class="col-type"><button class="sort-button" data-inventory-sort="function_type" type="button">Type</button></th><th class="col-file"><button class="sort-button" data-inventory-sort="source_path" type="button">File</button></th><th class="col-small"><button class="sort-button" data-inventory-sort="depth" type="button">Depth</button></th><th class="col-parent"><button class="sort-button" data-inventory-sort="parent_qualified_name" type="button">Parent</button></th><th>Violation</th><th>Violation detail</th><th>Inline candidate</th><th>Promote to shared</th></tr></thead><tbody id="inventoryBody"></tbody></table></div></section>
<section class="export-toolbar"><h2>Export architecture refactor packet</h2><div class="toolbar-row"><button id="downloadPacket" class="primary-action" type="button">Download architecture refactor packet</button><small id="exportStatus"></small></div></section></section>
<section id="orphanWorkflow" class="workflow-panel"><section class="architecture-summary-cards"><article class="architecture-summary-card info"><span>Defined functions</span><strong id="card-orphan-defined">0</strong></article><article class="architecture-summary-card review"><span>Orphan functions</span><strong id="card-orphan-unused">0</strong></article><article class="architecture-summary-card good"><span>Unused percentage</span><strong id="card-unused-percent">0%</strong></article></section><section class="flow-details"><h2>Orphan function cleanup</h2><section class="filter-panel"><label class="filter-field">Search defined but not used <input id="cleanupSearch" type="search" placeholder="Function, file, reason, action"></label><label class="filter-field">Suggested action <select id="cleanupActionFilter"><option value="">All actions</option></select></label><span></span><button id="clearCleanupFilters" type="button">Clear filters</button></section><div class="table-actions"><button id="selectVisibleCleanup" type="button">Select all visible defined-but-not-used rows</button><button id="clearCleanup" type="button">Clear selected cleanup rows</button><strong id="cleanupSelectedCount">0 selected</strong><small id="cleanupRowCount">0 rows</small></div><div class="table-wrap"><table id="definedButNotUsedTable"><colgroup><col class="col-select"><col class="col-function"><col class="col-file"><col class="col-reason"><col class="col-action"></colgroup><thead><tr><th>Select</th><th>Function</th><th>File</th><th>Reason</th><th>Suggested action</th></tr></thead><tbody id="unused-table"></tbody></table></div></section><section class="export-toolbar"><h2>Export orphan cleanup packet</h2><button id="downloadOrphanPacket" type="button">Download orphan cleanup packet</button><small id="orphanExportStatus"></small></section></section>
__EMBEDDED_SCRIPT__
<script>
let DATA=null, selectedPublic=null, publicRows=[], inventoryRows=[], cleanupRows=[], sortKey='function_name', sortDir=1, inventorySortKey='depth', inventorySortDir=1, cleanupSortKey='function_name', cleanupSortDir=1; const selectedInventory=new Set(), selectedCleanup=new Set(); const $=id=>document.getElementById(id); const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function githubSourceUrl(r){return `https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/${esc(r.source_path)}#L${esc(r.source_start_line||1)}`} function functionLink(r){return `<a class="source-link" href="${githubSourceUrl(r)}" target="_blank" rel="noopener"><code>${esc(r.function_name)}</code></a>`} function badges(a){return (a&&a.length)?a.map(x=>`<span class="badge ${x==='architecture_violation'?'danger':'warn'}">${esc(x==='large_width_or_depth'?'Large width/depth':x==='architecture_violation'?'Architecture violation':x)}</span>`).join(' '):'<span class="badge muted">None</span>'}
function violationBadges(n){const values=n.violation_types||[];return values.length?values.map(x=>`<span class="badge danger">${esc(x)}</span>`).join(' '):'<span class="badge muted">None</span>'} function basename(path){return String(path||'').split('/').pop()||path||'—'} function typeLabel(type){return ({public_function:'Public function',public_dependency:'Public dependency',shared_function:'Shared helper',private_function:'Private helper'})[type]||type||'Helper'}
function treeNode(root,node){const typeClass=`tree-type-${String(node.function_type||'helper').replaceAll('_','-')}`;return `<div class="tree-node" style="margin-left:${Math.min((node.depth||0)*.85,4.25)}rem"><div class="tree-row-main"><span>▸</span><a class="tree-function" href="${githubSourceUrl(node)}" target="_blank" rel="noopener">${esc(node.function_name)}(...)</a><span class="badge ${esc(typeClass)}">${esc(typeLabel(node.function_type))}</span><span class="tree-file">${esc(basename(node.source_path))}</span>${(node.violation_types||[]).map(x=>`<span class="badge danger">${esc(x)}</span>`).join(' ')}</div></div>`}
function uniqInventory(flow){const m=new Map();(flow||[]).forEach(n=>{const old=m.get(n.qualified_name); if(!old||n.depth<old.depth)m.set(n.qualified_name,n)}); return [...m.values()].sort((a,b)=>a.depth-b.depth||String(a.source_path).localeCompare(b.source_path)||String(a.function_name).localeCompare(b.function_name))}
function unusedPercentage(s){const defined=s.defined_function_count??(DATA.defined_functions||[]).length, unused=s.defined_but_not_used_count??(DATA.defined_but_not_used||[]).length;return defined?unused/defined*100:0}
function renderCards(){const s=DATA.summary||{}; const defined=s.defined_function_count??DATA.defined_functions.length, unused=s.defined_but_not_used_count??DATA.defined_but_not_used.length; $('card-public').textContent=s.public_function_count??DATA.public_functions.length; $('card-warnings').textContent=DATA.public_functions.filter(f=>f.has_architecture_violation).length; $('card-large').textContent=DATA.public_functions.filter(f=>f.has_large_width_or_depth).length; $('card-used').textContent=s.used_function_count??DATA.used_functions.length; $('card-defined').textContent=defined; $('card-orphan-defined').textContent=defined; $('card-orphan-unused').textContent=unused; $('card-unused-percent').textContent=`${unusedPercentage(s).toFixed(1)}%`}
function setupFilters(){[...new Set(DATA.public_functions.flatMap(f=>f.public_signals||f.signals||[]))].sort().forEach(v=>$('signalFilter').insertAdjacentHTML('beforeend',`<option value="${esc(v)}">${esc(v)}</option>`));[...new Set((DATA.defined_but_not_used||[]).map(f=>f.suggested_action||'review'))].sort().forEach(v=>$('cleanupActionFilter').insertAdjacentHTML('beforeend',`<option value="${esc(v)}">${esc(v)}</option>`))}
function compareRows(key,dir){return (a,b)=>{const av=key==='files_touched'?(a.files_touched||[]).length:a[key]??'',bv=key==='files_touched'?(b.files_touched||[]).length:b[key]??'';return (typeof av==='number'?av-bv:String(av).localeCompare(String(bv)))*dir}}
function filteredPublic(){const q=$('searchBox').value.toLowerCase(), sig=$('signalFilter').value; return DATA.public_functions.filter(f=>(!q||[f.function_name,f.qualified_name,f.source_path,(f.public_signals||f.signals||[]).join(' ')].join(' ').toLowerCase().includes(q))&&(!sig||(f.public_signals||f.signals||[]).includes(sig))).sort(compareRows(sortKey,sortDir))}
function renderPublicTable(){publicRows=filteredPublic(); $('rowCount').textContent=`${publicRows.length} of ${DATA.public_functions.length} public functions`; $('public-table').innerHTML=publicRows.map(f=>`<tr data-public-flow-row="${esc(f.qualified_name)}" class="${selectedPublic&&selectedPublic.qualified_name===f.qualified_name?'active':''}" tabindex="0"><td>${functionLink(f)}</td><td>${esc(f.source_path)}</td><td>${esc(f.width??f.direct_call_count)}</td><td>${esc(f.scope??f.transitive_function_count)}</td><td>${esc(f.depth??f.max_depth)}</td><td>${esc((f.files_touched||[]).length)}</td><td>${badges(f.public_signals||f.signals)}</td></tr>`).join('')}
function selectPublic(qn){selectedPublic=DATA.public_functions.find(f=>f.qualified_name===qn)||DATA.public_functions[0]; selectedInventory.clear(); renderPublicTable(); renderSelected(); updateCounts()}
function refreshInventoryTypeFilter(rows){const current=$('inventoryTypeFilter').value;$('inventoryTypeFilter').innerHTML='<option value="">All types</option>';[...new Set(rows.map(n=>n.function_type||'—'))].sort().forEach(v=>$('inventoryTypeFilter').insertAdjacentHTML('beforeend',`<option value="${esc(v)}">${esc(v)}</option>`));$('inventoryTypeFilter').value=[...$('inventoryTypeFilter').options].some(o=>o.value===current)?current:''}
function filteredInventoryRows(rows){const q=$('inventorySearch').value.toLowerCase(),type=$('inventoryTypeFilter').value;return rows.filter(n=>(!q||[n.function_name,n.qualified_name,n.function_type,n.source_path,n.parent_qualified_name,(n.violation_details||[]).join(' ')].join(' ').toLowerCase().includes(q))&&(!type||(n.function_type||'—')===type)).sort(compareRows(inventorySortKey,inventorySortDir))}
function renderSelected(){const f=selectedPublic;if(!f)return; $('selectedSummary').innerHTML=`<div class="flow-summary-card"><h3>${functionLink(f)}</h3><p><code>${esc(f.qualified_name)}</code> · <span>${esc(f.source_path)}</span></p><div class="flow-meta"><div><strong>${esc(f.width??f.direct_call_count)}</strong><br>Width</div><div><strong>${esc(f.scope??f.transitive_function_count)}</strong><br>Scope</div><div><strong>${esc(f.depth??f.max_depth)}</strong><br>Depth</div><div><strong>${esc((f.files_touched||[]).length)}</strong><br>Files</div></div><p>${badges(f.public_signals||f.signals)}</p></div>`; $('selected-call-tree').innerHTML=(f.flow||[]).map(n=>treeNode(f,n)).join(''); const allRows=uniqInventory(f.flow); refreshInventoryTypeFilter(allRows); inventoryRows=filteredInventoryRows(allRows); $('inventoryRowCount').textContent=`${inventoryRows.length} of ${allRows.length} rows`; $('inventoryBody').innerHTML=inventoryRows.map(n=>`<tr class="${selectedInventory.has(n.qualified_name)?'row-selected':''}"><td><input class="inventory-check" type="checkbox" data-qn="${esc(n.qualified_name)}" ${selectedInventory.has(n.qualified_name)?'checked':''}></td><td>${functionLink(n)}</td><td>${esc(n.function_type)}</td><td>${esc(n.source_path)}</td><td>${esc(n.depth)}</td><td>${esc(n.parent_qualified_name||'—')}</td><td>${violationBadges(n)}</td><td>${esc((n.violation_details||[]).join(' | ')||'—')}</td><td>${n.inline_candidate?'Yes':'No'}</td><td>${n.promote_to_shared_candidate?'Yes':'No'}</td></tr>`).join('')}
function filteredCleanupRows(){const q=$('cleanupSearch').value.toLowerCase(),action=$('cleanupActionFilter').value;return (DATA.defined_but_not_used||[]).filter(n=>(!q||[n.function_name,n.qualified_name,n.source_path,n.reason,n.suggested_action].join(' ').toLowerCase().includes(q))&&(!action||n.suggested_action===action)).sort(compareRows(cleanupSortKey,cleanupSortDir))}
function renderUnused(){cleanupRows=filteredCleanupRows();$('cleanupRowCount').textContent=`${cleanupRows.length} of ${(DATA.defined_but_not_used||[]).length} rows`;$('unused-table').innerHTML=cleanupRows.map(n=>`<tr class="${selectedCleanup.has(n.qualified_name)?'row-selected':''}"><td><input class="cleanup-check" type="checkbox" data-qn="${esc(n.qualified_name)}" ${selectedCleanup.has(n.qualified_name)?'checked':''}></td><td>${functionLink(n)}</td><td>${esc(n.source_path)}</td><td>${esc(n.reason)}</td><td>${esc(n.suggested_action)}</td></tr>`).join('')}
function updateCounts(){ $('inventorySelectedCount').textContent=`${selectedInventory.size} selected`; $('cleanupSelectedCount').textContent=`${selectedCleanup.size} selected`; }
function packet(){const f=selectedPublic; const inv=uniqInventory(f.flow); const selectedInv=selectedInventory.size?inv.filter(n=>selectedInventory.has(n.qualified_name)):inv; return {schema:'fabricops_public_function_call_flow_refactor_packet_v2',generated_at_utc:new Date().toISOString(),signal_rules:{large_width_or_depth:'Width > 10 or Depth > 5',architecture_violation:'Types 1-6 deterministic caller/callee architecture rules'},public_level_signals:f.public_signals||f.signals||[],selected_public_function:{function_name:f.function_name,qualified_name:f.qualified_name,source_path:f.source_path,source_start_line:f.source_start_line,source_end_line:f.source_end_line},selected_flow_summary:{width:f.width,scope:f.scope,depth:f.depth,architecture_violation_count:f.architecture_violation_count,has_large_width_or_depth:f.has_large_width_or_depth,has_architecture_violation:f.has_architecture_violation,files_touched:f.files_touched||[]},selected_flow_functions:f.flow||[],selected_inventory_assets:selectedInv,per_function_violation_details:selectedInv.map(n=>({qualified_name:n.qualified_name,violation_types:n.violation_types||[],violation_details:n.violation_details||[],inline_candidate:!!n.inline_candidate,promote_to_shared_candidate:!!n.promote_to_shared_candidate,distinct_caller_count:n.distinct_caller_count||0})),inline_candidates:selectedInv.filter(n=>n.inline_candidate),promote_to_shared_candidates:selectedInv.filter(n=>n.promote_to_shared_candidate),instructions_for_ai:['Create a focused cleanup PR from this selected public function flow.','Use deterministic signal rules and per-function violation details as the source of truth.','Keep the AI in the loop for planning, but do not replace deterministic findings with generic judgement.','Do not refactor unrelated files.','Do not regenerate unrelated generated docs or old dashboard artifacts.']}}
function orphanPacket(){const s=DATA.summary||{};const selected=selectedCleanup.size?cleanupRows.filter(n=>selectedCleanup.has(n.qualified_name)):cleanupRows;return {schema:'fabricops_orphan_function_cleanup_packet_v1',generated_at_utc:new Date().toISOString(),summary:{defined_function_count:s.defined_function_count??(DATA.defined_functions||[]).length,defined_but_not_used_count:s.defined_but_not_used_count??(DATA.defined_but_not_used||[]).length,unused_percentage:Number(unusedPercentage(s).toFixed(1))},selected_orphan_functions:selected}}
function download(name,text,type){const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([text],{type})); a.download=name; a.click()} function exportPacket(){download('fabricops-public-flow-refactor-packet-v2.json',JSON.stringify(packet(),null,2),'application/json');$('exportStatus').textContent='Downloaded architecture refactor packet.'} function exportOrphanPacket(){download('fabricops-orphan-cleanup-packet-v1.json',JSON.stringify(orphanPacket(),null,2),'application/json');$('orphanExportStatus').textContent='Downloaded orphan cleanup packet.'}
function showWorkflow(name){document.querySelectorAll('[data-workflow-tab]').forEach(b=>b.classList.toggle('active',b.dataset.workflowTab===name));$('architectureWorkflow').classList.toggle('active',name==='architecture');$('orphanWorkflow').classList.toggle('active',name==='orphan')}
document.addEventListener('click',e=>{if(e.target.closest('a'))return; const tab=e.target.closest('[data-workflow-tab]'); if(tab){showWorkflow(tab.dataset.workflowTab);return} const row=e.target.closest('[data-public-flow-row]'); if(row)selectPublic(row.dataset.publicFlowRow)}); document.addEventListener('keydown',e=>{const row=e.target.closest('[data-public-flow-row]'); if(row&&(e.key==='Enter'||e.key===' ')){e.preventDefault();selectPublic(row.dataset.publicFlowRow)}}); ['searchBox','signalFilter'].forEach(id=>$(id).addEventListener('input',renderPublicTable)); ['inventorySearch','inventoryTypeFilter'].forEach(id=>$(id).addEventListener('input',renderSelected)); ['cleanupSearch','cleanupActionFilter'].forEach(id=>$(id).addEventListener('input',renderUnused)); $('clearFilters').onclick=()=>{$('searchBox').value='';$('signalFilter').value='';renderPublicTable()}; $('clearInventoryFilters').onclick=()=>{$('inventorySearch').value='';$('inventoryTypeFilter').value='';renderSelected()}; $('clearCleanupFilters').onclick=()=>{$('cleanupSearch').value='';$('cleanupActionFilter').value='';renderUnused()}; document.querySelectorAll('[data-sort]').forEach(b=>b.onclick=()=>{sortDir=sortKey===b.dataset.sort?-sortDir:1;sortKey=b.dataset.sort;renderPublicTable()}); document.querySelectorAll('[data-inventory-sort]').forEach(b=>b.onclick=()=>{inventorySortDir=inventorySortKey===b.dataset.inventorySort?-inventorySortDir:1;inventorySortKey=b.dataset.inventorySort;renderSelected()}); $('selectVisibleInventory').onclick=()=>{inventoryRows.forEach(n=>selectedInventory.add(n.qualified_name));renderSelected();updateCounts()}; $('clearInventory').onclick=()=>{selectedInventory.clear();renderSelected();updateCounts()}; $('selectVisibleCleanup').onclick=()=>{cleanupRows.forEach(n=>selectedCleanup.add(n.qualified_name));renderUnused();updateCounts()}; $('clearCleanup').onclick=()=>{selectedCleanup.clear();renderUnused();updateCounts()}; document.addEventListener('change',e=>{if(e.target.classList.contains('inventory-check')){e.target.checked?selectedInventory.add(e.target.dataset.qn):selectedInventory.delete(e.target.dataset.qn);renderSelected();updateCounts()} if(e.target.classList.contains('cleanup-check')){e.target.checked?selectedCleanup.add(e.target.dataset.qn):selectedCleanup.delete(e.target.dataset.qn);renderUnused();updateCounts()}}); $('downloadPacket').onclick=()=>exportPacket(); $('downloadOrphanPacket').onclick=()=>exportOrphanPacket();
function validateDashboardData(data,url){if(!data||!Array.isArray(data.public_functions))throw new Error(`Loaded data from ${url} did not include a public_functions array`);return data} function loadDashboardData(dataUrl){const attemptedUrl=new URL(dataUrl,window.location.href).href;return fetch(attemptedUrl).then(response=>{if(!response.ok)throw new Error(`HTTP ${response.status} ${response.statusText} for ${attemptedUrl}`);return response.json().then(data=>validateDashboardData(data,attemptedUrl))})} function showDataLoadError(error){const message=`Failed to load public-function-call-flows.json from ${error&&error.message?error.message:error}`;console.error(message,error);$('dataLoadStatus').textContent=message;$('selectedSummary').innerHTML=`<div class="flow-summary-card risk"><strong>Data-load failure.</strong> ${esc(message)}</div>`} function renderMetadata(){const m=DATA.metadata||{};$('generatedTimestamp').textContent=`Generated: ${m.generated_at_sgt||'timestamp unavailable'}`;if(m.source_json_url)$('sourceJsonLink').href=m.source_json_url} function renderDashboard(data){DATA=data;renderMetadata();renderCards();setupFilters();renderPublicTable();renderUnused();if(DATA.public_functions.length)selectPublic(DATA.public_functions[0]);$('dataLoadStatus').textContent='Loaded public-function-call-flows.json'}
__LOAD_EXPRESSION__.then(renderDashboard).catch(showDataLoadError);
</script></main></body></html>"""
    return html_doc.replace("__EMBEDDED_SCRIPT__", embedded_script).replace("__LOAD_EXPRESSION__", load_expression)


def write_outputs(payload: dict[str, Any], data_path: Path = DATA_PATH, dashboard_path: Path = DASHBOARD_PATH) -> None:
    """Write JSON and dashboard outputs."""
    data_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    dashboard_path.write_text(render_dashboard(), encoding="utf-8")


def main() -> None:
    """Generate public function call-flow artifacts."""
    write_outputs(build_payload())


if __name__ == "__main__":
    main()
