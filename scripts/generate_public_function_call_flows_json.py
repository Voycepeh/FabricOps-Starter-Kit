"""Generate v2 public-function call-flow JSON data."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generated_artifact_metadata import update_generated_artifact_metadata
from scripts.release_inventory import GROUPS as RELEASE_GROUPS
from scripts.release_inventory import _load_manifest as load_release_manifest

PKG_DIR = ROOT / "src" / "fabricops_kit"
PACKAGE_NAME = "fabricops_kit"
INIT_PATH = PKG_DIR / "__init__.py"
DATA_PATH = ROOT / "docs" / "reference" / "_data" / "public-function-call-flows.json"
SOURCE_JSON_URL = "https://github.com/Voycepeh/FabricOps-Starter-Kit/raw/main/docs/reference/_data/public-function-call-flows.json"
SOURCE_BLOB_BASE_URL = "https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/"
LARGE_WIDTH_THRESHOLD = 10
LARGE_DEPTH_THRESHOLD = 5
METADATA_TABLE_PATTERN = re.compile(r"METADATA_[A-Z0-9_]+")

ARCHITECTURE_VIOLATION_RULES = {
    "Type 1": "Public function calls another public function directly.",
    "Type 2": "Shared function calls a public function directly.",
    "Type 3": "Private function calls a public function directly.",
    "Type 4": "Shared function calls a private function from another file.",
    "Type 5": "Private function calls a private function from another file.",
}
# v1 parity backlog for future focused PRs:
# TODO: Add JSON/YAML AI refactor packet export.
# TODO: Add compatibility mode for legacy function-call-graph consumers.
# TODO: Add a selected public function cleanup packet schema.
# TODO: Polish the dashboard mobile layout.
# TODO: Detect unresolved calls that appear to target local/internal helpers without faking the signal.



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
        return {"type": "Type 1", "detail": ARCHITECTURE_VIOLATION_RULES["Type 1"]}
    if caller_type == "shared_function" and callee_public:
        return {"type": "Type 2", "detail": ARCHITECTURE_VIOLATION_RULES["Type 2"]}
    if caller_type == "private_function" and callee_public:
        return {"type": "Type 3", "detail": ARCHITECTURE_VIOLATION_RULES["Type 3"]}
    if caller_type == "shared_function" and callee_type == "private_function" and different_file:
        return {"type": "Type 4", "detail": ARCHITECTURE_VIOLATION_RULES["Type 4"]}
    if caller_type == "private_function" and callee_type == "private_function" and different_file:
        return {"type": "Type 5", "detail": ARCHITECTURE_VIOLATION_RULES["Type 5"]}
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


def release_manifest_paths(root: Path = ROOT) -> list[Path]:
    """Return release manifest paths in deterministic version order."""
    manifest_dir = root / "docs" / "releases" / "manifests"
    return sorted(manifest_dir.glob("*.yml")) if manifest_dir.exists() else []


def build_lifecycle_contract(root: Path = ROOT) -> dict[str, Any]:
    """Build lifecycle lookup data from release manifests."""
    functions: dict[str, dict[str, Any]] = {}
    metadata_tables: dict[str, dict[str, Any]] = {}
    release_versions: list[str] = []
    for path in release_manifest_paths(root):
        manifest = load_release_manifest(path)
        if manifest is None:
            continue
        version = str(manifest["release_version"])
        release_versions.append(version)
        for item in manifest.get("functions", []):
            qn = item.get("qualified_name")
            if not qn:
                continue
            record = functions.setdefault(qn, {"function_name": item["name"], "qualified_name": qn, "release_history": []})
            status = str(item["status"])
            record["release_history"].append({"version": version, "status": status})
            if status == "live" and not record.get("live_since"):
                record["live_since"] = str(item.get("introduced_in") or version)
            if status == "discontinued":
                record["discontinued_in"] = str(item.get("discontinued_in") or version)
            record["lifecycle_status"] = status
        for item in manifest.get("metadata_tables", []):
            record = metadata_tables.setdefault(item["name"], {"table_name": item["name"], "release_history": []})
            status = str(item["status"])
            record["release_history"].append({"version": version, "status": status})
            if status == "live" and not record.get("live_since"):
                record["live_since"] = str(item.get("introduced_in") or version)
            if status == "discontinued":
                record["discontinued_in"] = str(item.get("discontinued_in") or version)
            record["lifecycle_status"] = status
    functions_by_name = {item["function_name"]: item for item in functions.values()}
    return {"release_versions": release_versions, "functions": functions, "functions_by_name": functions_by_name, "metadata_tables": metadata_tables}


def lifecycle_for_qn(qn: str, lifecycle_contract: dict[str, Any]) -> dict[str, Any]:
    """Return lifecycle fields for a qualified function name."""
    record = lifecycle_contract.get("functions", {}).get(qn) or lifecycle_contract.get("functions_by_name", {}).get(qn.rsplit(".", 1)[-1], {})
    status = record.get("lifecycle_status", "internal")
    return {
        "lifecycle_status": status,
        "live_since": record.get("live_since"),
        "discontinued_in": record.get("discontinued_in"),
        "release_history": record.get("release_history", []),
    }


def metadata_tables_in_node(node: ast.AST) -> set[str]:
    """Return metadata table names mentioned directly in an AST node."""
    tables: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            tables.update(METADATA_TABLE_PATTERN.findall(child.value))
    return tables


def module_metadata_constants(module: ModuleInfo) -> dict[str, str]:
    """Return module-level constants whose values are metadata table names."""
    constants: dict[str, str] = {}
    for node in module.tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            matches = METADATA_TABLE_PATTERN.findall(node.value.value)
            if not matches:
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    constants[target.id] = matches[0]
    return constants


def metadata_tables_in_function(info: FunctionInfo, module: ModuleInfo, constants: dict[str, str]) -> set[str]:
    """Return metadata tables referenced by a function body."""
    tables = metadata_tables_in_node(info.node)
    for child in ast.walk(info.node):
        if isinstance(child, ast.Name) and child.id in constants:
            tables.add(constants[child.id])
    if info.function_name == "setup_metadata_tables":
        tables.update(constants.values())
    return tables



def build_notebook_dependents(function_names: set[str], lifecycle_contract: dict[str, Any], root: Path = ROOT) -> dict[str, list[dict[str, str]]]:
    """Return notebook templates that mention each function name."""
    dependents: dict[str, list[dict[str, str]]] = {name: [] for name in function_names}
    template_status: dict[str, str] = {}
    for path in release_manifest_paths(root):
        manifest = load_release_manifest(path)
        if manifest is None:
            continue
        for item in manifest.get("templates", []):
            template_status[item["name"]] = str(item["status"])
    for notebook_path in sorted((root / "templates" / "notebooks").glob("*.ipynb")):
        text = notebook_path.read_text(encoding="utf-8")
        status = template_status.get(notebook_path.stem, "unknown")
        for name in sorted(function_names):
            if re.search(rf"\b{re.escape(name)}\b", text):
                dependents[name].append({"notebook": notebook_path.stem, "lifecycle_status": status, "source_path": repo_relative(notebook_path, root)})
    return dependents

def relationship_for_function(info: FunctionInfo, table: str) -> str:
    """Classify the relationship between a function and a metadata table."""
    name = info.function_name.lower()
    if name == "setup_metadata_tables":
        return "creates_or_validates"
    if any(token in name for token in ("write", "save", "append", "setup", "render", "author", "enrich", "bootstrap")):
        return "writes_or_manages"
    if any(token in name for token in ("read", "browse", "select", "display")):
        return "reads_or_displays"
    return "references"


def build_metadata_contract_relationships(
    modules: dict[str, ModuleInfo],
    functions: dict[str, FunctionInfo],
    lifecycle_contract: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    """Build function-to-metadata contract relationships from source and release manifests."""
    live_tables = {name for name, item in lifecycle_contract.get("metadata_tables", {}).items() if item.get("lifecycle_status") == "live"}
    relationships: dict[str, list[dict[str, Any]]] = {}
    constants_by_module = {name: module_metadata_constants(module) for name, module in modules.items()}
    for qn, info in functions.items():
        module_name = ".".join(qn.split(".")[:-1])
        module = modules[module_name]
        tables = metadata_tables_in_function(info, module, constants_by_module[module_name])
        rows = []
        for table in sorted(tables):
            metadata_record = lifecycle_contract.get("metadata_tables", {}).get(table, {})
            status = metadata_record.get("lifecycle_status", "unknown")
            rows.append({
                "table_name": table,
                "relationship": relationship_for_function(info, table),
                "metadata_lifecycle_status": status,
                "metadata_live_since": metadata_record.get("live_since"),
                "is_live_metadata_contract": table in live_tables,
                "contract": f"{table} schema v1" if table in lifecycle_contract.get("metadata_tables", {}) else table,
            })
        relationships[qn] = rows
    return relationships


def merge_metadata_relationships(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return deterministic unique metadata relationship rows."""
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        merged[(row["table_name"], row["relationship"])] = row
    return [merged[key] for key in sorted(merged)]


def contract_classification(
    function_type_name: str,
    lifecycle_status: str,
    live_dependents: list[str],
    metadata_relationships: list[dict[str, Any]],
) -> str:
    """Return the release-contract classification for a callable."""
    supports_live_metadata = any(row.get("is_live_metadata_contract") for row in metadata_relationships)
    writes_live_metadata = any(row.get("is_live_metadata_contract") and row.get("relationship") in {"creates_or_validates", "writes_or_manages"} for row in metadata_relationships)
    if lifecycle_status == "discontinued":
        return "discontinued_function"
    if function_type_name in {"private_function", "shared_function"} and live_dependents:
        return "live_critical_internal"
    if lifecycle_status == "live" and writes_live_metadata:
        return "live_function_writing_live_metadata"
    if lifecycle_status == "preview" and supports_live_metadata:
        return "preview_function_supporting_live_contracts"
    if lifecycle_status == "live":
        return "live_public_function"
    if lifecycle_status == "preview":
        return "preview_public_function"
    return "internal_function"


def contract_display(classification: str, lifecycle: dict[str, Any]) -> str:
    """Return compact human-facing contract display text."""
    if classification == "live_public_function":
        return f"Live · Live since {lifecycle.get('live_since')}" if lifecycle.get("live_since") else "Live"
    if classification == "preview_public_function":
        return "Preview"
    if classification == "preview_function_supporting_live_contracts":
        return "Preview · Supports Live contracts"
    if classification == "live_function_writing_live_metadata":
        return "Live · Writes Live metadata"
    if classification == "live_critical_internal":
        return "Live-critical internal"
    if classification == "discontinued_function":
        return f"Discontinued · Last available in {lifecycle.get('discontinued_in')}" if lifecycle.get("discontinued_in") else "Discontinued"
    return "Internal"

def build_payload(root: Path = ROOT, pkg_dir: Path = PKG_DIR, init_path: Path = INIT_PATH) -> dict[str, Any]:
    """Build the v2 JSON payload."""
    modules = discover_modules(pkg_dir)
    functions = discover_functions(modules, root)
    public_names = set(read_public_export_names(init_path))
    public_qns = {qn for qn, info in functions.items() if info.function_name in public_names}
    lifecycle_contract = build_lifecycle_contract(root)
    metadata_relationships_by_qn = build_metadata_contract_relationships(modules, functions, lifecycle_contract)
    notebook_dependents_by_name = build_notebook_dependents({info.function_name for info in functions.values()}, lifecycle_contract, root)
    used_all: set[str] = set()
    public_functions = []
    live_dependents_by_qn: dict[str, set[str]] = {qn: set() for qn in functions}
    pending_flows: list[tuple[str, list[dict[str, Any]], set[str]]] = []
    for root_qn in sorted(public_qns, key=lambda q: (functions[q].function_name, q)):
        flow, used = build_flow(root_qn, modules, functions, public_qns)
        pending_flows.append((root_qn, flow, used))
        root_lifecycle = lifecycle_for_qn(root_qn, lifecycle_contract)
        if root_lifecycle["lifecycle_status"] == "live":
            for item in flow:
                live_dependents_by_qn.setdefault(item["qualified_name"], set()).add(root_qn)

    for root_qn, flow, used in pending_flows:
        used_all.update(used)
        root_info = functions[root_qn]
        for item in flow:
            item_lifecycle = lifecycle_for_qn(item["qualified_name"], lifecycle_contract)
            item_relationships = metadata_relationships_by_qn.get(item["qualified_name"], [])
            item_live_dependents = sorted(live_dependents_by_qn.get(item["qualified_name"], set()))
            item_classification = contract_classification(item["function_type"], item_lifecycle["lifecycle_status"], item_live_dependents, item_relationships)
            item.update(item_lifecycle)
            item["live_dependents"] = item_live_dependents
            item["live_dependent_count"] = len(item_live_dependents)
            item["metadata_contract_relationships"] = item_relationships
            item["notebook_dependents"] = notebook_dependents_by_name.get(item["function_name"], [])
            item["live_notebook_dependents"] = [row for row in item["notebook_dependents"] if row["lifecycle_status"] == "live"]
            item["supports_live_metadata_contracts"] = any(row.get("is_live_metadata_contract") for row in item_relationships)
            item["writes_live_metadata"] = any(row.get("is_live_metadata_contract") and row.get("relationship") in {"creates_or_validates", "writes_or_manages"} for row in item_relationships)
            item["contract_classification"] = item_classification
            item["contract_display"] = contract_display(item_classification, item_lifecycle)
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
        lifecycle = lifecycle_for_qn(root_qn, lifecycle_contract)
        live_dependents = sorted(live_dependents_by_qn.get(root_qn, set()))
        own_relationships = metadata_relationships_by_qn.get(root_qn, [])
        flow_relationships = merge_metadata_relationships([row for item in flow for row in item.get("metadata_contract_relationships", [])])
        classification = contract_classification("public_function", lifecycle["lifecycle_status"], live_dependents, flow_relationships)
        live_critical_dependencies = sorted({item["qualified_name"] for item in flow if item["qualified_name"] != root_qn and item.get("contract_classification") == "live_critical_internal"})
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
            **lifecycle,
            "live_dependents": live_dependents,
            "live_dependent_count": len(live_dependents),
            "contract_classification": classification,
            "contract_display": contract_display(classification, lifecycle),
            "metadata_contract_relationships": own_relationships,
            "transitive_metadata_contract_relationships": flow_relationships,
            "notebook_dependents": notebook_dependents_by_name.get(root_info.function_name, []),
            "live_notebook_dependents": [row for row in notebook_dependents_by_name.get(root_info.function_name, []) if row["lifecycle_status"] == "live"],
            "supports_live_metadata_contracts": any(row.get("is_live_metadata_contract") for row in flow_relationships),
            "writes_live_metadata": any(row.get("is_live_metadata_contract") and row.get("relationship") in {"creates_or_validates", "writes_or_manages"} for row in flow_relationships),
            "live_critical_dependencies": live_critical_dependencies,
            "live_critical_dependency_count": len(live_critical_dependencies),
        })
    defined_functions = [
        function_record(info, public_qns)
        | lifecycle_for_qn(info.qualified_name, lifecycle_contract)
        | {
            "live_dependents": sorted(live_dependents_by_qn.get(info.qualified_name, set())),
            "live_dependent_count": len(live_dependents_by_qn.get(info.qualified_name, set())),
            "metadata_contract_relationships": metadata_relationships_by_qn.get(info.qualified_name, []),
            "notebook_dependents": notebook_dependents_by_name.get(info.function_name, []),
            "live_notebook_dependents": [row for row in notebook_dependents_by_name.get(info.function_name, []) if row["lifecycle_status"] == "live"],
        }
        for info in sorted(functions.values(), key=lambda item: item.qualified_name)
    ]
    for item in defined_functions:
        item_classification = contract_classification(item["function_type"], item["lifecycle_status"], item["live_dependents"], item["metadata_contract_relationships"])
        item["contract_classification"] = item_classification
        item["contract_display"] = contract_display(item_classification, item)
        item["supports_live_metadata_contracts"] = any(row.get("is_live_metadata_contract") for row in item["metadata_contract_relationships"])
        item["writes_live_metadata"] = any(row.get("is_live_metadata_contract") and row.get("relationship") in {"creates_or_validates", "writes_or_manages"} for row in item["metadata_contract_relationships"])
    unused = [unused_record(functions[qn]) for qn in sorted(set(functions) - used_all)]
    return {
        "metadata": {
            "schema": "fabricops_public_function_call_flows_v2",
            "source_json_url": SOURCE_JSON_URL,
            "source": "src/fabricops_kit",
            "public_function_source": "src/fabricops_kit/__init__.py::__all__",
            "lifecycle_source": "docs/releases/manifests/*.yml",
            "metadata_contract_source": "release manifests plus source metadata table references",
            "release_versions": lifecycle_contract["release_versions"],
            "architecture_violation_rules": ARCHITECTURE_VIOLATION_RULES,
            "architecture_violation_signal": "Any Type 1 to Type 5 edge appears in the public function flow.",
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
            "live_public_function_count": sum(1 for item in public_functions if item["lifecycle_status"] == "live"),
            "preview_public_function_count": sum(1 for item in public_functions if item["lifecycle_status"] == "preview"),
            "public_functions_supporting_live_metadata_count": sum(1 for item in public_functions if item["supports_live_metadata_contracts"]),
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


def write_json(payload: dict[str, Any], data_path: Path = DATA_PATH) -> None:
    """Write only the public function call-flow JSON output."""
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if data_path == DATA_PATH:
        update_generated_artifact_metadata(
            artifact_key="public_function_call_flows_json",
            label="Public function call-flow data",
            generator="scripts/generate_public_function_call_flows_json.py",
            output_path="docs/reference/_data/public-function-call-flows.json",
        )


def main() -> None:
    """Generate only the public function call-flow JSON artifact."""
    write_json(build_payload())


if __name__ == "__main__":
    main()
