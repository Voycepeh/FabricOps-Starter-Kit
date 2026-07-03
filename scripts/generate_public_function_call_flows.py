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
SINGAPORE_TZ = ZoneInfo("Asia/Singapore")

# v1 parity backlog for future focused PRs:
# TODO: Add JSON/YAML AI refactor packet export.
# TODO: Add compatibility mode for legacy function-call-graph consumers.
# TODO: Add a selected public function cleanup packet schema.
# TODO: Revisit source/docs link behavior once the v2 dashboard route is published.
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


def build_flow(root_qn: str, modules: dict[str, ModuleInfo], functions: dict[str, FunctionInfo], public_qns: set[str]) -> tuple[list[dict[str, Any]], set[str]]:
    """Build a depth-first public function call flow."""
    name_index = build_name_index(functions)
    flow: list[dict[str, Any]] = []
    used: set[str] = set()

    def visit(qn: str, depth: int, parent: str | None, stack: set[str]) -> None:
        info = functions[qn]
        used.add(qn)
        flow.append({
            "depth": depth,
            "function_name": info.function_name,
            "qualified_name": qn,
            "source_path": info.source_path,
            "source_start_line": info.source_start_line,
            "source_end_line": info.source_end_line,
            "function_type": function_type(info, public_qns, root_qn),
            "parent_qualified_name": parent,
            "edge_type": "root" if parent is None else "direct",
        })
        if qn in stack:
            return
        next_stack = {*stack, qn}
        for child in sorted(called_function_qns(info, modules, functions, name_index)):
            visit(child, depth + 1, qn, next_stack)

    visit(root_qn, 0, None, set())
    return flow, used


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
        refactor_signals = calculate_refactor_signals(root_info, flow, direct_call_count, max_depth)
        signals = [item["signal"] for item in refactor_signals]
        public_functions.append({
            "function_name": root_info.function_name,
            "qualified_name": root_qn,
            "source_path": root_info.source_path,
            "source_start_line": root_info.source_start_line,
            "source_end_line": root_info.source_end_line,
            "flow": flow,
            "direct_call_count": direct_call_count,
            "transitive_function_count": len({item["qualified_name"] for item in flow}) - 1,
            "max_depth": max_depth,
            "files_touched": sorted({item["source_path"] for item in flow}),
            "signals": signals,
            "refactor_signals": refactor_signals,
            "refactor_summary": summarize_refactor_signals(refactor_signals),
            "suggested_refactor_action": suggest_refactor_action(refactor_signals),
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
    """Calculate structured refactor signals for a public flow."""
    refactor_signals: list[dict[str, Any]] = []
    public_dependencies = [item for item in flow if item["function_type"] == "public_dependency"]
    if public_dependencies:
        refactor_signals.append({
            "signal": "public_calls_public",
            "severity": "warning",
            "message": "Public function flow reaches another exported public function; review architecture boundaries.",
            "evidence": [flow_evidence(item) for item in public_dependencies],
        })

    if max_depth > 4:
        deepest = [item for item in flow if item["depth"] == max_depth]
        refactor_signals.append({
            "signal": "large_depth",
            "severity": "warning",
            "message": f"Public function flow reaches depth {max_depth}; consider splitting or extracting clearer helpers.",
            "evidence": [{"max_depth": max_depth}, *[flow_evidence(item) for item in deepest]],
        })

    if direct_call_count > 10:
        direct_children = [item for item in flow if item["parent_qualified_name"] == root_info.qualified_name]
        refactor_signals.append({
            "signal": "large_width",
            "severity": "warning",
            "message": f"Public function has {direct_call_count} direct package-local calls; review orchestration width.",
            "evidence": [flow_evidence(item) for item in direct_children],
        })

    cross_file_private = [
        item
        for item in flow
        if item["function_type"] == "private_function" and item["source_path"] != root_info.source_path
    ]
    if cross_file_private:
        refactor_signals.append({
            "signal": "cross_file_private_dependency",
            "severity": "warning",
            "message": "Public function flow reaches private helpers in another file; consider a shared non-private helper boundary.",
            "evidence": [flow_evidence(item) for item in cross_file_private],
        })

    return refactor_signals


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


def suggest_refactor_action(refactor_signals: list[dict[str, Any]]) -> str:
    """Return the highest-priority suggested refactor action."""
    signals = {item["signal"] for item in refactor_signals}
    if "unresolved_internal_call" in signals:
        return "review_unresolved_internal_call"
    if "public_calls_public" in signals:
        return "review_public_calls_public"
    if "cross_file_private_dependency" in signals:
        return "review_cross_file_private_dependency"
    if "large_depth" in signals or "large_width" in signals:
        return "split_large_flow"
    return "no_action"


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
body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:0;color:#172033;background:#f8fafc}header,main{max-width:1180px;margin:auto;padding:1rem}h1{margin-bottom:.25rem}.overview-help{color:#475569}.architecture-summary-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(9.5rem,1fr));gap:.5rem;margin:.75rem 0}.architecture-summary-card{padding:.65rem;border:1px solid #dbe3ef;border-radius:.75rem;background:#fff}.architecture-summary-card strong{display:block;font-size:1.55rem}.risk{border-color:#fecaca!important;background:#fef2f2!important}.review{border-color:#fde68a!important;background:#fffbeb!important}.info{border-color:#bfdbfe!important;background:#eff6ff!important}.good{border-color:#bbf7d0!important;background:#f0fdf4!important}.filter-panel,.export-toolbar,.flow-details{margin:.75rem 0;padding:.75rem;border:1px solid #dbe3ef;border-radius:.75rem;background:#fff}.filter-panel{display:grid;grid-template-columns:minmax(16rem,1fr) repeat(2,minmax(11rem,15rem)) auto;gap:.55rem;align-items:end}.filter-field{display:flex;flex-direction:column;font-size:.82rem;font-weight:800;gap:.2rem}input,select,button{padding:.43rem .52rem;border:1px solid #cbd5e1;border-radius:.45rem;background:#fff}button{cursor:pointer;font-weight:800;color:#1d4ed8}.primary-action{background:#1d4ed8;color:#fff;border-color:#1d4ed8}.table-actions,.toolbar-row{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;margin:.55rem 0}.table-wrap{overflow-x:auto;overflow-y:hidden;background:#fff;border:1px solid #dbe3ef;border-radius:.75rem;-webkit-overflow-scrolling:touch}table{width:100%;border-collapse:collapse;table-layout:auto}#publicFlowTable{min-width:1180px}#selectedCallableInventoryTable{min-width:1060px}#definedButNotUsedTable{min-width:1120px}th,td{padding:.55rem .65rem;border-bottom:1px solid #e2e8f0;text-align:left;vertical-align:top;font-size:.84rem;white-space:normal;overflow-wrap:break-word;word-break:normal}th{background:#eef2f7;color:#334155;font-size:.75rem;line-height:1.25;white-space:normal;overflow-wrap:normal;word-break:keep-all}td code{white-space:normal;overflow-wrap:break-word;word-break:break-word}.col-function{min-width:18rem}.col-file{min-width:22rem}.col-select{min-width:7.5rem}.col-type{min-width:7rem}.col-small{min-width:6.5rem;width:6.5rem}.col-signals{min-width:12rem}.col-action{min-width:13rem}.col-parent{min-width:16rem}.col-reason{min-width:14rem}col.col-function{width:18rem}col.col-file{width:22rem}col.col-select{width:7.5rem}col.col-type{width:7rem}col.col-small{width:6.5rem}col.col-signals{width:12rem}col.col-action{width:13rem}col.col-parent{width:16rem}col.col-reason{width:14rem}.sort-button{border:0;background:transparent;padding:0;color:#1d4ed8;text-align:left;line-height:1.25;white-space:normal;overflow-wrap:normal;word-break:keep-all}.sort-button:after{content:' ↕';color:#64748b;white-space:nowrap}tr[data-public-flow-row]{cursor:pointer}tr[data-public-flow-row]:focus{outline:3px solid #2563eb;outline-offset:-3px}tr.active{outline:2px solid #1d4ed8;outline-offset:-2px;background:#eff6ff;box-shadow:inset .25rem 0 #1d4ed8}.source-link{color:#1d4ed8;text-decoration:underline;overflow-wrap:break-word;word-break:break-word}.badge{display:inline-flex;margin:.06rem;padding:.12rem .38rem;border-radius:999px;font-size:.7rem;font-weight:800;background:#e0e7ff;color:#3730a3}.warn{background:#fef3c7;color:#92400e}.muted{background:#f1f5f9;color:#475569}.flow-summary-card{padding:.75rem;border:1px solid #bfdbfe;border-radius:.75rem;background:#eff6ff}.flow-meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(135px,1fr));gap:.5rem}.flow-meta div{padding:.45rem;border:1px solid #e2e8f0;border-radius:.5rem;background:#fff}.flow-tree{overflow-x:hidden;border:1px solid #dbe3ef;border-radius:.5rem;padding:.65rem;background:#fff}.tree-row{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;line-height:1.45;margin:.2rem 0;white-space:normal;overflow-wrap:break-word;word-break:break-word}.tree-path{display:block;color:#64748b;font-family:system-ui;font-size:.76rem;overflow-wrap:break-word;word-break:break-word}.export-toolbar{background:#f8fafc}.toolbar-card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,18rem),1fr));gap:.5rem}.toolbar-card{padding:.6rem;border:1px solid #e2e8f0;border-radius:.65rem;background:#fff}.row-selected{background:#eff6ff}@media(max-width:760px){header,main{padding:.75rem}.filter-panel{grid-template-columns:1fr;padding:.65rem}.table-wrap{margin-left:-.25rem;margin-right:-.25rem;border-radius:.55rem}th,td{font-size:.78rem;padding:.48rem .55rem}.col-function{min-width:16rem}.col-file{min-width:20rem}.tree-row{padding-left:min(var(--tree-indent,0rem),3.5rem)!important}}
</style></head><body><header><h1>Public Function Call Flows V2</h1><p class="overview-help">Public functions are roots; selected flow shows nested package-local functions; defined-but-not-used is a cleanup candidate list.</p><p class="overview-help"><strong id="generatedTimestamp">Generated: loading…</strong> · Source JSON: <a id="sourceJsonLink" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/raw/main/docs/reference/_data/public-function-call-flows.json" target="_blank" rel="noopener">Download from GitHub</a></p></header><main>
<section class="architecture-summary-cards" aria-label="Public function call-flow summary"><article class="architecture-summary-card info"><span>Public functions</span><strong id="card-public">0</strong></article><article class="architecture-summary-card risk"><span>Architecture violations / refactor warnings</span><strong id="card-warnings">0</strong></article><article class="architecture-summary-card review"><span>Large depth / width</span><strong id="card-large">0</strong></article><article class="architecture-summary-card review"><span>Defined but not used</span><strong id="card-unused">0</strong></article><article class="architecture-summary-card good"><span>Used functions</span><strong id="card-used">0</strong></article><article class="architecture-summary-card info"><span>Defined functions</span><strong id="card-defined">0</strong></article></section>
<section class="filter-panel" aria-label="Search and filters"><label class="filter-field">Search <input id="searchBox" type="search" placeholder="Function, file, signals, action"></label><label class="filter-field">Signal <select id="signalFilter"><option value="">All signals</option></select></label><label class="filter-field">Suggested action <select id="actionFilter"><option value="">All actions</option></select></label><button id="clearFilters" type="button">Clear filters</button></section>
<section class="table-actions"><strong id="rowCount">0 public functions</strong><small id="dataLoadStatus" aria-live="polite"></small></section>
<section class="table-wrap"><table id="publicFlowTable"><colgroup><col class="col-function"><col class="col-file"><col class="col-small"><col class="col-small"><col class="col-small"><col class="col-small"><col class="col-signals"><col class="col-action"></colgroup><thead><tr><th class="col-function"><button class="sort-button" data-sort="function_name" type="button">Function</button></th><th class="col-file"><button class="sort-button" data-sort="source_path" type="button">File</button></th><th class="col-small"><button class="sort-button" data-sort="direct_call_count" type="button">Direct calls</button></th><th class="col-small"><button class="sort-button" data-sort="transitive_function_count" type="button">Transitive functions</button></th><th class="col-small"><button class="sort-button" data-sort="max_depth" type="button">Max depth</button></th><th class="col-small"><button class="sort-button" data-sort="files_touched" type="button">Files touched</button></th><th class="col-signals">Signals</th><th class="col-action"><button class="sort-button" data-sort="suggested_refactor_action" type="button">Suggested action</button></th></tr></thead><tbody id="public-table"></tbody></table></section>
<section id="selected-public-function-panel" class="flow-details"><h2>Selected public function</h2><div id="selectedSummary">Select a public function row.</div><h2>Selected call tree</h2><div id="selected-call-tree" class="flow-tree"></div><h2>Selected callable inventory</h2><section class="filter-panel" aria-label="Selected callable inventory filters"><label class="filter-field">Search selected inventory <input id="inventorySearch" type="search" placeholder="Function, type, file, parent"></label><label class="filter-field">Function type <select id="inventoryTypeFilter"><option value="">All types</option></select></label><button id="clearInventoryFilters" type="button">Clear filters</button></section><div class="table-actions"><button id="selectVisibleInventory" type="button">Select all visible selected-inventory rows</button><button id="clearInventory" type="button">Clear selected inventory rows</button><strong id="inventorySelectedCount">0 selected</strong><small id="inventoryRowCount">0 rows</small></div><div class="table-wrap"><table id="selectedCallableInventoryTable"><colgroup><col class="col-select"><col class="col-function"><col class="col-type"><col class="col-file"><col class="col-small"><col class="col-parent"></colgroup><thead><tr><th class="col-select">Select checkbox</th><th class="col-function"><button class="sort-button" data-inventory-sort="function_name" type="button">Function</button></th><th class="col-type"><button class="sort-button" data-inventory-sort="function_type" type="button">Type</button></th><th class="col-file"><button class="sort-button" data-inventory-sort="source_path" type="button">File</button></th><th class="col-small"><button class="sort-button" data-inventory-sort="depth" type="button">Depth</button></th><th class="col-parent"><button class="sort-button" data-inventory-sort="parent_qualified_name" type="button">Parent</button></th></tr></thead><tbody id="inventoryBody"></tbody></table></div></section>
<section class="export-toolbar"><h2>Export AI refactor packet</h2><div class="toolbar-row"><button id="downloadPacket" class="primary-action" type="button">Download AI refactor packet</button><small id="exportStatus"></small></div></section>
<section class="flow-details"><h2>Defined but not used</h2><section class="filter-panel" aria-label="Defined but not used filters"><label class="filter-field">Search defined but not used <input id="cleanupSearch" type="search" placeholder="Function, file, reason, action"></label><label class="filter-field">Suggested action <select id="cleanupActionFilter"><option value="">All actions</option></select></label><button id="clearCleanupFilters" type="button">Clear filters</button></section><div class="table-actions"><button id="selectVisibleCleanup" type="button">Select all visible defined-but-not-used rows</button><button id="clearCleanup" type="button">Clear selected cleanup rows</button><strong id="cleanupSelectedCount">0 selected</strong><small id="cleanupRowCount">0 rows</small></div><div class="table-wrap"><table id="definedButNotUsedTable"><colgroup><col class="col-select"><col class="col-function"><col class="col-type"><col class="col-file"><col class="col-reason"><col class="col-action"></colgroup><thead><tr><th class="col-select">Select checkbox</th><th class="col-function"><button class="sort-button" data-cleanup-sort="function_name" type="button">Function</button></th><th class="col-type"><button class="sort-button" data-cleanup-sort="function_type" type="button">Type</button></th><th class="col-file"><button class="sort-button" data-cleanup-sort="source_path" type="button">File</button></th><th class="col-reason"><button class="sort-button" data-cleanup-sort="reason" type="button">Reason</button></th><th class="col-action"><button class="sort-button" data-cleanup-sort="suggested_action" type="button">Suggested action</button></th></tr></thead><tbody id="unused-table"></tbody></table></div></section>
__EMBEDDED_SCRIPT__
<script>
let DATA=null, selectedPublic=null, publicRows=[], inventoryRows=[], cleanupRows=[], sortKey='function_name', sortDir=1, inventorySortKey='depth', inventorySortDir=1, cleanupSortKey='function_name', cleanupSortDir=1; const selectedInventory=new Set(), selectedCleanup=new Set(); const $=id=>document.getElementById(id); const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function sourceLink(r){return `<a class="source-link" href="../../../${esc(r.source_path)}#L${esc(r.source_start_line||1)}" target="_blank" rel="noopener">${esc(r.source_path)}</a>`} function badges(a){return (a&&a.length)?a.map(x=>`<span class="badge warn">${esc(x)}</span>`).join(' '):'<span class="badge muted">none</span>'}
function uniqInventory(flow){const m=new Map();(flow||[]).forEach(n=>{const old=m.get(n.qualified_name); if(!old||n.depth<old.depth)m.set(n.qualified_name,n)}); return [...m.values()].sort((a,b)=>a.depth-b.depth||String(a.source_path).localeCompare(b.source_path)||String(a.function_name).localeCompare(b.function_name))}
function renderCards(){const s=DATA.summary||{}; $('card-public').textContent=s.public_function_count??DATA.public_functions.length; $('card-warnings').textContent=DATA.public_functions.filter(f=>(f.refactor_signals||[]).length).length; $('card-large').textContent=DATA.public_functions.filter(f=>(f.signals||[]).some(x=>x==='large_depth'||x==='large_width')).length; $('card-unused').textContent=s.defined_but_not_used_count??DATA.defined_but_not_used.length; $('card-used').textContent=s.used_function_count??DATA.used_functions.length; $('card-defined').textContent=s.defined_function_count??DATA.defined_functions.length}
function setupFilters(){[...new Set(DATA.public_functions.flatMap(f=>f.signals||[]))].sort().forEach(v=>$('signalFilter').insertAdjacentHTML('beforeend',`<option value="${esc(v)}">${esc(v)}</option>`));[...new Set(DATA.public_functions.map(f=>f.suggested_refactor_action||'no_action'))].sort().forEach(v=>$('actionFilter').insertAdjacentHTML('beforeend',`<option value="${esc(v)}">${esc(v)}</option>`));[...new Set((DATA.defined_but_not_used||[]).map(f=>f.suggested_action||'review'))].sort().forEach(v=>$('cleanupActionFilter').insertAdjacentHTML('beforeend',`<option value="${esc(v)}">${esc(v)}</option>`))}
function sortValue(row,key){return key==='files_touched'?(row.files_touched||[]).length:row[key]??''}
function compareRows(key,dir){return (a,b)=>{const av=sortValue(a,key),bv=sortValue(b,key);return (typeof av==='number'?av-bv:String(av).localeCompare(String(bv)))*dir}}
function refreshInventoryTypeFilter(rows){const current=$('inventoryTypeFilter').value;$('inventoryTypeFilter').innerHTML='<option value="">All types</option>';[...new Set(rows.map(n=>n.function_type||'—'))].sort().forEach(v=>$('inventoryTypeFilter').insertAdjacentHTML('beforeend',`<option value="${esc(v)}">${esc(v)}</option>`));$('inventoryTypeFilter').value=[...$('inventoryTypeFilter').options].some(o=>o.value===current)?current:''}
function filteredPublic(){const q=$('searchBox').value.toLowerCase(), sig=$('signalFilter').value, act=$('actionFilter').value; return DATA.public_functions.filter(f=>(!q||[f.function_name,f.qualified_name,f.source_path,(f.signals||[]).join(' '),f.suggested_refactor_action].join(' ').toLowerCase().includes(q))&&(!sig||(f.signals||[]).includes(sig))&&(!act||f.suggested_refactor_action===act)).sort((a,b)=>{const av=sortKey==='files_touched'?(a.files_touched||[]).length:a[sortKey], bv=sortKey==='files_touched'?(b.files_touched||[]).length:b[sortKey]; return (typeof av==='number'?av-bv:String(av).localeCompare(String(bv)))*sortDir})}
function renderPublicTable(){publicRows=filteredPublic(); $('rowCount').textContent=`${publicRows.length} of ${DATA.public_functions.length} public functions`; $('public-table').innerHTML=publicRows.map((f,i)=>`<tr data-public-flow-row="${esc(f.qualified_name)}" class="${selectedPublic&&selectedPublic.qualified_name===f.qualified_name?'active':''}" tabindex="0" aria-selected="${selectedPublic&&selectedPublic.qualified_name===f.qualified_name?'true':'false'}"><td><code>${esc(f.function_name)}</code></td><td>${sourceLink(f)}</td><td>${esc(f.direct_call_count)}</td><td>${esc(f.transitive_function_count)}</td><td>${esc(f.max_depth)}</td><td>${esc((f.files_touched||[]).length)}</td><td>${badges(f.signals)}</td><td>${esc(f.suggested_refactor_action)}</td></tr>`).join('')}
function selectPublic(qn){selectedPublic=DATA.public_functions.find(f=>f.qualified_name===qn)||DATA.public_functions[0]; selectedInventory.clear(); renderPublicTable(); renderSelected(); updateCounts()}
function filteredInventoryRows(rows){const q=$('inventorySearch').value.toLowerCase(),type=$('inventoryTypeFilter').value;return rows.filter(n=>(!q||[n.function_name,n.qualified_name,n.function_type,n.source_path,n.parent_qualified_name].join(' ').toLowerCase().includes(q))&&(!type||(n.function_type||'—')===type)).sort(compareRows(inventorySortKey,inventorySortDir))}
function renderSelected(){const f=selectedPublic;if(!f)return; $('selectedSummary').innerHTML=`<div class="flow-summary-card"><h3>${esc(f.function_name)}</h3><p><code>${esc(f.qualified_name)}</code> · ${sourceLink(f)}</p><div class="flow-meta"><div><strong>${esc(f.direct_call_count)}</strong><br>direct calls</div><div><strong>${esc(f.transitive_function_count)}</strong><br>transitive functions</div><div><strong>${esc(f.max_depth)}</strong><br>max depth</div><div><strong>${esc((f.files_touched||[]).length)}</strong><br>files touched</div></div><p><strong>Suggested refactor action:</strong> ${esc(f.suggested_refactor_action)}</p><p><strong>Refactor summary:</strong> ${esc(f.refactor_summary)}</p><p>${badges(f.signals)}</p></div>`; $('selected-call-tree').innerHTML=(f.flow||[]).map(n=>`<div class="tree-row" style="--tree-indent:${Math.min(n.depth*.9,5)}rem;padding-left:var(--tree-indent)"><span class="badge muted">${esc(n.function_type)}</span> ${esc(n.function_name)}(...)<span class="tree-path">${esc(n.source_path)}</span></div>`).join(''); const allRows=uniqInventory(f.flow); refreshInventoryTypeFilter(allRows); inventoryRows=filteredInventoryRows(allRows); $('inventoryRowCount').textContent=`${inventoryRows.length} of ${allRows.length} rows`; $('inventoryBody').innerHTML=inventoryRows.map(n=>`<tr class="${selectedInventory.has(n.qualified_name)?'row-selected':''}"><td><input class="inventory-check" type="checkbox" data-qn="${esc(n.qualified_name)}" ${selectedInventory.has(n.qualified_name)?'checked':''}></td><td><code>${esc(n.function_name)}</code></td><td>${esc(n.function_type)}</td><td>${sourceLink(n)}</td><td>${esc(n.depth)}</td><td>${esc(n.parent_qualified_name||'—')}</td></tr>`).join('')}
function filteredCleanupRows(){const q=$('cleanupSearch').value.toLowerCase(),action=$('cleanupActionFilter').value;return (DATA.defined_but_not_used||[]).filter(n=>(!q||[n.function_name,n.qualified_name,n.source_path,n.reason,n.suggested_action].join(' ').toLowerCase().includes(q))&&(!action||n.suggested_action===action)).sort(compareRows(cleanupSortKey,cleanupSortDir))}
function renderUnused(){cleanupRows=filteredCleanupRows();$('cleanupRowCount').textContent=`${cleanupRows.length} of ${(DATA.defined_but_not_used||[]).length} rows`;$('unused-table').innerHTML=cleanupRows.map(n=>`<tr class="${selectedCleanup.has(n.qualified_name)?'row-selected':''}"><td><input class="cleanup-check" type="checkbox" data-qn="${esc(n.qualified_name)}" ${selectedCleanup.has(n.qualified_name)?'checked':''}></td><td><code>${esc(n.function_name)}</code></td><td>${esc(n.function_type||'—')}</td><td>${sourceLink(n)}</td><td>${esc(n.reason)}</td><td>${esc(n.suggested_action)}</td></tr>`).join('')}
function updateCounts(){ $('inventorySelectedCount').textContent=`${selectedInventory.size} selected`; $('cleanupSelectedCount').textContent=`${selectedCleanup.size} selected`; }
function packet(){const f=selectedPublic; const inv=uniqInventory(f.flow); const selectedInv=selectedInventory.size?inv.filter(n=>selectedInventory.has(n.qualified_name)):inv; return {schema:'fabricops_public_function_call_flow_refactor_packet_v2',generated_at_utc:new Date().toISOString(),selected_public_function:{function_name:f.function_name,qualified_name:f.qualified_name,source_path:f.source_path,source_start_line:f.source_start_line,source_end_line:f.source_end_line},selected_flow_summary:{direct_call_count:f.direct_call_count,transitive_function_count:f.transitive_function_count,max_depth:f.max_depth,files_touched:f.files_touched||[],signals:f.signals||[],refactor_summary:f.refactor_summary,suggested_refactor_action:f.suggested_refactor_action},selected_flow_functions:f.flow||[],selected_inventory_assets:selectedInv,selected_defined_but_not_used:(DATA.defined_but_not_used||[]).filter(n=>selectedCleanup.has(n.qualified_name)),refactor_signals:f.refactor_signals||[],instructions_for_ai:['Create a focused cleanup PR from this selected public function flow.','Use the selected public function flow as the source of truth.','Default to breaking cleanup: remove obsolete helpers instead of preserving compatibility wrappers.','Do not refactor unrelated files.','Do not regenerate unrelated generated docs or old dashboard artifacts.']}}
function download(name,text,type){const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([text],{type})); a.download=name; a.click()} function exportPacket(){download('fabricops-public-flow-refactor-packet-v2.json',JSON.stringify(packet(),null,2),'application/json');$('exportStatus').textContent='Downloaded AI refactor packet.'}
document.addEventListener('click',e=>{if(e.target.closest('a'))return; const row=e.target.closest('[data-public-flow-row]'); if(row)selectPublic(row.dataset.publicFlowRow)}); document.addEventListener('keydown',e=>{const row=e.target.closest('[data-public-flow-row]'); if(row&&(e.key==='Enter'||e.key===' ')){e.preventDefault();selectPublic(row.dataset.publicFlowRow)}}); ['searchBox','signalFilter','actionFilter'].forEach(id=>$(id).addEventListener('input',renderPublicTable)); ['inventorySearch','inventoryTypeFilter'].forEach(id=>$(id).addEventListener('input',renderSelected)); ['cleanupSearch','cleanupActionFilter'].forEach(id=>$(id).addEventListener('input',renderUnused)); $('clearFilters').onclick=()=>{$('searchBox').value='';$('signalFilter').value='';$('actionFilter').value='';renderPublicTable()}; $('clearInventoryFilters').onclick=()=>{$('inventorySearch').value='';$('inventoryTypeFilter').value='';renderSelected()}; $('clearCleanupFilters').onclick=()=>{$('cleanupSearch').value='';$('cleanupActionFilter').value='';renderUnused()}; document.querySelectorAll('[data-sort]').forEach(b=>b.onclick=()=>{sortDir=sortKey===b.dataset.sort?-sortDir:1;sortKey=b.dataset.sort;renderPublicTable()}); document.querySelectorAll('[data-inventory-sort]').forEach(b=>b.onclick=()=>{inventorySortDir=inventorySortKey===b.dataset.inventorySort?-inventorySortDir:1;inventorySortKey=b.dataset.inventorySort;renderSelected()}); document.querySelectorAll('[data-cleanup-sort]').forEach(b=>b.onclick=()=>{cleanupSortDir=cleanupSortKey===b.dataset.cleanupSort?-cleanupSortDir:1;cleanupSortKey=b.dataset.cleanupSort;renderUnused()}); $('selectVisibleInventory').onclick=()=>{inventoryRows.forEach(n=>selectedInventory.add(n.qualified_name));renderSelected();updateCounts()}; $('clearInventory').onclick=()=>{selectedInventory.clear();renderSelected();updateCounts()}; $('selectVisibleCleanup').onclick=()=>{cleanupRows.forEach(n=>selectedCleanup.add(n.qualified_name));renderUnused();updateCounts()}; $('clearCleanup').onclick=()=>{selectedCleanup.clear();renderUnused();updateCounts()}; document.addEventListener('change',e=>{if(e.target.classList.contains('inventory-check')){e.target.checked?selectedInventory.add(e.target.dataset.qn):selectedInventory.delete(e.target.dataset.qn);renderSelected();updateCounts()} if(e.target.classList.contains('cleanup-check')){e.target.checked?selectedCleanup.add(e.target.dataset.qn):selectedCleanup.delete(e.target.dataset.qn);renderUnused();updateCounts()}}); $('downloadPacket').onclick=()=>exportPacket();
function validateDashboardData(data,url){if(!data||!Array.isArray(data.public_functions))throw new Error(`Loaded data from ${url} did not include a public_functions array`);return data}
function loadDashboardData(dataUrl){const attemptedUrl=new URL(dataUrl,window.location.href).href;return fetch(attemptedUrl).then(response=>{if(!response.ok)throw new Error(`HTTP ${response.status} ${response.statusText} for ${attemptedUrl}`);return response.json().then(data=>validateDashboardData(data,attemptedUrl))})}
function showDataLoadError(error){const message=`Failed to load public-function-call-flows.json from ${error&&error.message?error.message:error}`;console.error(message,error);$('dataLoadStatus').textContent=message;$('dataLoadStatus').style.color='#b91c1c';$('selectedSummary').innerHTML=`<div class="flow-summary-card risk"><strong>Data-load failure.</strong> ${esc(message)}</div>`}
function renderMetadata(){const m=DATA.metadata||{};$('generatedTimestamp').textContent=`Generated: ${m.generated_at_sgt||'timestamp unavailable'}`;if(m.source_json_url)$('sourceJsonLink').href=m.source_json_url}
function renderDashboard(data){DATA=data;renderMetadata();renderCards();setupFilters();renderPublicTable();renderUnused();if(DATA.public_functions.length)selectPublic(DATA.public_functions[0]);$('dataLoadStatus').textContent='Loaded public-function-call-flows.json'}
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
