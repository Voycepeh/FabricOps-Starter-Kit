"""Generate v2 public-function call-flow data and dashboard."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from datetime import UTC, datetime
import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PKG_DIR = ROOT / "src" / "fabricops_kit"
PACKAGE_NAME = "fabricops_kit"
INIT_PATH = PKG_DIR / "__init__.py"
DATA_PATH = ROOT / "docs" / "reference" / "_data" / "public-function-call-flows.json"
DASHBOARD_PATH = ROOT / "docs" / "assets" / "public-function-call-flows-dashboard.html"


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
        max_depth = max(item["depth"] for item in flow)
        signals = calculate_signals(root_info, flow)
        public_functions.append({
            "function_name": root_info.function_name,
            "qualified_name": root_qn,
            "source_path": root_info.source_path,
            "source_start_line": root_info.source_start_line,
            "source_end_line": root_info.source_end_line,
            "flow": flow,
            "direct_call_count": len({item["qualified_name"] for item in direct}),
            "transitive_function_count": len({item["qualified_name"] for item in flow}) - 1,
            "max_depth": max_depth,
            "files_touched": sorted({item["source_path"] for item in flow}),
            "signals": signals,
        })
    defined_functions = [function_record(info, public_qns) for info in sorted(functions.values(), key=lambda item: item.qualified_name)]
    unused = [unused_record(functions[qn]) for qn in sorted(set(functions) - used_all)]
    return {
        "metadata": {
            "schema": "fabricops_public_function_call_flows_v2",
            "generated_at_utc": datetime.now(UTC).isoformat(),
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


def calculate_signals(root_info: FunctionInfo, flow: list[dict[str, Any]]) -> list[str]:
    """Calculate architecture and complexity signals for a public flow."""
    signals = set()
    if any(item["function_type"] == "public_dependency" for item in flow):
        signals.add("public_calls_public")
    if max(item["depth"] for item in flow) > 4:
        signals.add("large_depth")
    if len({item["qualified_name"] for item in flow if item["parent_qualified_name"] == root_info.qualified_name}) > 10:
        signals.add("large_width")
    if any(item["function_type"] == "private_function" and item["source_path"] != root_info.source_path for item in flow):
        signals.add("cross_file_private_dependency")
    return sorted(signals)


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
    }


def render_dashboard(payload: dict[str, Any]) -> str:
    """Render a standalone dashboard HTML document."""
    data = json.dumps(payload, indent=2)
    escaped = html.escape(data)
    return f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><title>Public Function Call Flows</title>
<style>body{{font-family:system-ui,sans-serif;margin:2rem;color:#172033}}.cards{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1rem}}.card{{border:1px solid #d7deea;border-radius:12px;padding:1rem;background:#f8fbff}}.value{{font-size:2rem;font-weight:700}}table{{border-collapse:collapse;width:100%;margin-top:1rem}}th,td{{border-bottom:1px solid #e2e8f0;padding:.55rem;text-align:left;vertical-align:top}}tr.clickable{{cursor:pointer}}tr.clickable:hover{{background:#f1f7ff}}code,.pill{{background:#eef3fb;border-radius:999px;padding:.15rem .45rem}}.tree-row{{font-family:ui-monospace,monospace;margin:.25rem 0}}.signal{{color:#8a3ffc;font-weight:600}}</style></head>
<body><h1>Public Function Call Flows v2</h1>
<div class=\"cards\"><div class=\"card\"><div>Public functions</div><div id=\"card-public\" class=\"value\"></div></div><div class=\"card\"><div>Architecture violations</div><div id=\"card-violations\" class=\"value\"></div></div><div class=\"card\"><div>Large depth / width</div><div id=\"card-large\" class=\"value\"></div></div><div class=\"card\"><div>Defined but not used</div><div id=\"card-unused\" class=\"value\"></div></div></div>
<h2>Public function flows</h2><table><thead><tr><th>Function</th><th>File</th><th>Direct calls</th><th>Transitive functions</th><th>Max depth</th><th>Files touched</th><th>Signals</th></tr></thead><tbody id=\"public-table\"></tbody></table>
<section id=\"selected-flow-panel\"><h2>Selected flow</h2><div id=\"selected-flow\">Select a public function row.</div></section>
<h2>Defined but not used</h2><table><thead><tr><th>Function</th><th>File</th><th>Reason</th></tr></thead><tbody id=\"unused-table\"></tbody></table>
<script id=\"public-function-call-flows-json\" type=\"application/json\">{escaped}</script>
<script>
const DATA = JSON.parse(document.getElementById('public-function-call-flows-json').textContent);
const qs = (id) => document.getElementById(id);
function link(path, line) {{ return `<a href="../../../${{path}}#L${{line}}">${{path}}</a>`; }}
function signals(items) {{ return items.length ? items.map(s => `<span class="signal">${{s}}</span>`).join(', ') : '—'; }}
function renderCards() {{ qs('card-public').textContent = DATA.summary.public_function_count; qs('card-violations').textContent = DATA.public_functions.filter(f => f.signals.includes('public_calls_public') || f.signals.includes('cross_file_private_dependency')).length; qs('card-large').textContent = DATA.public_functions.filter(f => f.signals.includes('large_depth') || f.signals.includes('large_width')).length; qs('card-unused').textContent = DATA.summary.defined_but_not_used_count; }}
function renderPublicTable() {{ qs('public-table').innerHTML = DATA.public_functions.map((f, i) => `<tr class="clickable" data-index="${{i}}"><td><code>${{f.function_name}}</code></td><td>${{link(f.source_path, f.source_start_line)}}</td><td>${{f.direct_call_count}}</td><td>${{f.transitive_function_count}}</td><td>${{f.max_depth}}</td><td>${{f.files_touched.length}}</td><td>${{signals(f.signals)}}</td></tr>`).join(''); document.querySelectorAll('#public-table tr').forEach(row => row.addEventListener('click', () => renderSelected(DATA.public_functions[Number(row.dataset.index)]))); }}
function renderSelected(f) {{ qs('selected-flow').innerHTML = `<h3>${{f.function_name}}</h3>` + f.flow.map(n => `<div class="tree-row" style="padding-left:${{n.depth * 1.5}}rem">${{'└─'.repeat(n.depth)}} [${{n.source_path}}] [${{n.function_type}}] ${{n.function_name}}(...)</div>`).join(''); }}
function renderUnused() {{ qs('unused-table').innerHTML = DATA.defined_but_not_used.map(f => `<tr><td><code>${{f.function_name}}</code></td><td>${{link(f.source_path, f.source_start_line)}}</td><td>${{f.reason}}</td></tr>`).join(''); }}
renderCards(); renderPublicTable(); renderUnused(); if (DATA.public_functions.length) renderSelected(DATA.public_functions[0]);
</script></body></html>"""


def write_outputs(payload: dict[str, Any], data_path: Path = DATA_PATH, dashboard_path: Path = DASHBOARD_PATH) -> None:
    """Write JSON and dashboard outputs."""
    data_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    dashboard_path.write_text(render_dashboard(payload), encoding="utf-8")


def main() -> None:
    """Generate public function call-flow artifacts."""
    write_outputs(build_payload())


if __name__ == "__main__":
    main()
