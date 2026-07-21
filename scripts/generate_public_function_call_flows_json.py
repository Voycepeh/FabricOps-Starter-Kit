"""Generate v2 public-function call-flow JSON data."""

from __future__ import annotations

import ast
import copy
from dataclasses import dataclass, field
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generated_artifact_metadata import update_generated_artifact_metadata
from scripts.release_inventory import load_release_manifests
PKG_DIR = ROOT / "src" / "fabricops_kit"
PACKAGE_NAME = "fabricops_kit"
INIT_PATH = PKG_DIR / "__init__.py"
DATA_PATH = ROOT / "docs" / "reference" / "_data" / "public-function-call-flows.json"
MANIFESTS_DIR = ROOT / "docs" / "releases" / "manifests"
SOURCE_JSON_URL = "https://github.com/Voycepeh/FabricOps-Starter-Kit/raw/main/docs/reference/_data/public-function-call-flows.json"
SOURCE_BLOB_BASE_URL = "https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/"
LARGE_WIDTH_THRESHOLD = 10
LARGE_DEPTH_THRESHOLD = 5
ARCHITECTURE_VIOLATION_RULES = {
    "Type 1": "Public function calls another public function directly.",
    "Type 2": "Shared function calls a public function directly.",
    "Type 3": "Private function calls a public function directly.",
    "Type 4": "Shared function calls a private function from another file.",
    "Type 5": "Private function calls a private function from another file.",
}
PUBLIC_LIFECYCLE_STATUSES = {"live", "preview", "discontinued"}
PUBLIC_CALLABLE_TYPES = {"public_function", "widget_function"}
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


@dataclass(frozen=True)
class ReleaseFunctionLifecycle:
    """Release-manifest lifecycle metadata for a public function."""

    lifecycle_status: str
    live_since: str | None
    discontinued_in: str | None
    release_history: tuple[dict[str, str], ...]
    release_versions: tuple[str, ...]


def repo_relative(path: Path, root: Path = ROOT) -> str:
    """Return a POSIX path relative to the repository root."""
    return path.relative_to(root).as_posix()


def read_function_lifecycle(manifests_dir: Path = MANIFESTS_DIR) -> tuple[dict[str, ReleaseFunctionLifecycle], list[str]]:
    """Read public-function lifecycle metadata from release manifests only."""
    manifests = load_release_manifests(manifests_dir)
    versions = [str(manifest.get("release_version", "")) for manifest in manifests if manifest.get("release_version")]
    history_by_qn: dict[str, list[dict[str, str]]] = {}
    live_since_by_qn: dict[str, str] = {}
    discontinued_by_qn: dict[str, str] = {}
    for manifest in manifests:
        version = str(manifest.get("release_version", ""))
        for item in manifest.get("functions", []):
            qn = item.get("qualified_name")
            status = item.get("status")
            if not qn or status not in PUBLIC_LIFECYCLE_STATUSES:
                continue
            history_by_qn.setdefault(str(qn), []).append({"version": version, "status": str(status)})
            if status == "live" and str(qn) not in live_since_by_qn:
                live_since_by_qn[str(qn)] = str(item.get("live_since") or item.get("introduced_in") or version)
            if status == "discontinued":
                discontinued_by_qn[str(qn)] = str(item.get("discontinued_in") or version)
    lifecycle = {}
    for qn, history in history_by_qn.items():
        latest = history[-1]["status"]
        lifecycle[qn] = ReleaseFunctionLifecycle(
            lifecycle_status=latest,
            live_since=live_since_by_qn.get(qn),
            discontinued_in=discontinued_by_qn.get(qn),
            release_history=tuple(history),
            release_versions=tuple(item["version"] for item in history),
        )
    for manifest in manifests:
        for item in manifest.get("functions", []):
            qn = item.get("qualified_name")
            name = item.get("name")
            if qn in lifecycle and name:
                lifecycle.setdefault(str(name), lifecycle[str(qn)])
    return lifecycle, versions


def validate_public_lifecycle_entries(
    functions: dict[str, FunctionInfo],
    public_qns: set[str],
    lifecycle_by_qn: dict[str, ReleaseFunctionLifecycle],
    release_versions: list[str],
    unreleased_preview_names: set[str] | None = None,
) -> None:
    """Fail when release manifests omit a callable except current unreleased previews."""
    if not release_versions:
        return
    preview_names = unreleased_preview_names or set()
    missing = [
        qn
        for qn in sorted(public_qns, key=lambda item: (functions[item].function_name, item))
        if qn not in lifecycle_by_qn and functions[qn].function_name not in lifecycle_by_qn and functions[qn].function_name not in preview_names
    ]
    if missing:
        raise ValueError("Public callable missing from release manifests:\n" + "\n".join(missing))


def current_preview_public_api_names() -> set[str]:
    """Return function names currently listed as preview public API entries."""
    from fabricops_kit.public_api import PREVIEW_PUBLIC_API

    return {str(item).split(".")[-1] for item in PREVIEW_PUBLIC_API}


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
    path_parts = PurePosixPath(info.source_path).parts
    in_widget_package = any(
        path_parts[index : index + 2] == ("fabricops_kit", "widgets")
        for index in range(len(path_parts) - 1)
    )
    is_public = info.qualified_name in public_qns
    if (
        is_public
        and in_widget_package
        and info.function_name.startswith("widget_")
    ):
        return "widget_function"
    if info.qualified_name == root_qn:
        return "public_function"
    if info.qualified_name in public_qns:
        return "public_dependency"
    if info.function_name.startswith("_"):
        return "private_function"
    return "shared_function"


def classify_architecture_violation(
    caller: FunctionInfo | None,
    callee: FunctionInfo,
    caller_type: str | None,
    callee_type: str,
    *,
    callee_is_public: bool | None = None,
) -> dict[str, str] | None:
    """Return a deterministic architecture violation for one caller/callee edge."""
    if caller is None or caller_type is None:
        return None
    caller_public = caller_type in PUBLIC_CALLABLE_TYPES or caller_type == "public_dependency"
    if callee_is_public is not None:
        callee_public = callee_is_public
    else:
        callee_public = callee_type in PUBLIC_CALLABLE_TYPES or callee_type == "public_dependency"
    different_file = caller.source_path != callee.source_path
    if caller_type == "widget_function" and callee_public:
        return None
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
        violation = classify_architecture_violation(
            parent_info,
            info,
            caller_type,
            current_type,
            callee_is_public=qn in public_qns,
        )
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


def public_lifecycle(qn: str, function_name: str, lifecycle_by_qn: dict[str, ReleaseFunctionLifecycle]) -> ReleaseFunctionLifecycle:
    """Return manifest lifecycle metadata for a public callable."""
    return lifecycle_by_qn.get(qn) or lifecycle_by_qn.get(function_name) or ReleaseFunctionLifecycle("preview", None, None, tuple(), tuple())


def lifecycle_fields(lifecycle: ReleaseFunctionLifecycle) -> dict[str, Any]:
    """Return common serializable lifecycle fields."""
    return {
        "lifecycle_status": lifecycle.lifecycle_status,
        "live_since": lifecycle.live_since,
        "discontinued_in": lifecycle.discontinued_in,
        "release_history": list(lifecycle.release_history),
        "release_versions": list(lifecycle.release_versions),
    }


def public_contract_classification(status: str) -> str:
    """Return the public contract classification for a lifecycle status."""
    return {
        "live": "live_public_function",
        "preview": "preview_public_function",
        "discontinued": "discontinued_public_function",
    }[status]


def public_contract_display(lifecycle: ReleaseFunctionLifecycle) -> str:
    """Return display text for a public callable lifecycle."""
    if lifecycle.lifecycle_status == "live":
        return f"Live · Live since {lifecycle.live_since}" if lifecycle.live_since else "Live"
    if lifecycle.lifecycle_status == "discontinued":
        return f"Discontinued · Last available in {lifecycle.discontinued_in}" if lifecycle.discontinued_in else "Discontinued"
    return "Preview"


def calculate_live_impact(
    public_functions: list[dict[str, Any]],
    public_qns: set[str],
    live_public_qns: set[str],
    preview_public_qns: set[str],
) -> dict[str, dict[str, Any]]:
    """Calculate direct/transitive Live dependency impact for every callable node."""
    impact: dict[str, dict[str, set[str] | bool | str]] = {}
    preview_reached: set[str] = set()
    for public_function in public_functions:
        root_qn = public_function["qualified_name"]
        is_live = root_qn in live_public_qns
        is_preview = root_qn in preview_public_qns
        for row in public_function["flow"]:
            qn = row["qualified_name"]
            record = impact.setdefault(qn, {"direct": set(), "transitive": set(), "preview": False})
            if is_preview:
                preview_reached.add(qn)
                record["preview"] = True
            if is_live and qn != root_qn and qn not in public_qns:
                target = "direct" if row["parent_qualified_name"] == root_qn else "transitive"
                record[target].add(root_qn)  # type: ignore[union-attr]
    normalized: dict[str, dict[str, Any]] = {}
    for qn, record in impact.items():
        direct_set = record["direct"]  # type: ignore[assignment]
        transitive_set = record["transitive"] - direct_set  # type: ignore[operator]
        direct = sorted(direct_set)  # type: ignore[arg-type]
        transitive = sorted(transitive_set)  # type: ignore[arg-type]
        supports_live = bool(direct or transitive)
        if qn in live_public_qns:
            level = "direct_public_contract"
        elif direct:
            level = "direct_live_dependency"
        elif transitive:
            level = "transitive_live_dependency"
        elif qn in preview_reached:
            level = "preview_only"
        else:
            level = "none"
        normalized[qn] = {
            "direct_live_dependents": direct,
            "direct_live_dependent_count": len(direct),
            "transitive_live_dependents": transitive,
            "transitive_live_dependent_count": len(transitive),
            "supports_live_contract": supports_live or qn in live_public_qns,
            "live_impact_level": level,
        }
    return normalized


def internal_contract_classification(impact: dict[str, Any]) -> str:
    """Return contract classification for a non-public callable."""
    if impact["supports_live_contract"]:
        return "live_critical_internal"
    if impact["live_impact_level"] == "preview_only":
        return "preview_only_internal"
    return "internal_function"


def internal_contract_display(classification: str) -> str:
    """Return display text for a non-public callable classification."""
    return {
        "live_critical_internal": "Live-critical internal",
        "preview_only_internal": "Preview-only internal",
        "internal_function": "Internal",
    }[classification]


def enrich_rows_with_contract(
    rows: list[dict[str, Any]],
    impact_by_qn: dict[str, dict[str, Any]],
    public_qns: set[str],
    lifecycle_by_qn: dict[str, ReleaseFunctionLifecycle],
) -> None:
    """Add lifecycle and Live-impact contract fields to flow rows."""
    for row in rows:
        qn = row["qualified_name"]
        impact = impact_by_qn.get(qn, {})
        row.update({
            "direct_live_dependents": impact.get("direct_live_dependents", []),
            "direct_live_dependent_count": impact.get("direct_live_dependent_count", 0),
            "transitive_live_dependents": impact.get("transitive_live_dependents", []),
            "transitive_live_dependent_count": impact.get("transitive_live_dependent_count", 0),
            "supports_live_contract": impact.get("supports_live_contract", False),
            "live_impact_level": impact.get("live_impact_level", "none"),
        })
        if qn in public_qns:
            lifecycle = public_lifecycle(qn, row["function_name"], lifecycle_by_qn)
            row.update(lifecycle_fields(lifecycle))
            row["contract_classification"] = public_contract_classification(lifecycle.lifecycle_status)
            row["contract_display"] = public_contract_display(lifecycle)
        else:
            row["lifecycle_status"] = "internal"
            row["live_since"] = None
            row["discontinued_in"] = None
            row["release_history"] = []
            row["release_versions"] = []
            row["contract_classification"] = internal_contract_classification(row)
            row["contract_display"] = internal_contract_display(row["contract_classification"])


def _signature_from_node(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Return a compact source signature for a function record."""
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    returns = f" -> {ast.unparse(node.returns)}" if node.returns is not None else ""
    return f"{prefix} {node.name}({ast.unparse(node.args)}){returns}"


def _first_sentence(doc: str | None) -> str:
    """Return the first sentence from a docstring."""
    if not doc:
        return ""
    line = doc.strip().splitlines()[0].strip()
    return line.split(".")[0].strip() + ("." if "." in line else "")


def _docstring_sections(doc: str | None) -> dict[str, str]:
    """Extract simple NumPy-style docstring sections for frozen references."""
    if not doc:
        return {}
    lines = doc.strip().splitlines()
    sections: dict[str, list[str]] = {}
    current: str | None = None
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        next_line = lines[index + 1].strip() if index + 1 < len(lines) else ""
        if line and next_line and set(next_line) <= {"-"} and len(next_line) >= 3:
            current = line.lower().replace(" ", "_")
            sections[current] = []
            index += 2
            continue
        if current is not None:
            sections[current].append(lines[index].rstrip())
        index += 1
    return {key: "\n".join(value).strip() for key, value in sections.items() if "\n".join(value).strip()}


def _parameter_doc_metadata(parameters_section: str) -> dict[str, dict[str, str]]:
    """Return first-paragraph NumPy-style parameter docs keyed by name."""
    docs: dict[str, dict[str, Any]] = {}
    current: str | None = None
    for raw_line in parameters_section.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if not line.startswith(" ") and " : " in line:
            name, type_part = stripped.split(" : ", 1)
            current = name.split(",")[0].strip()
            docs[current] = {"type": type_part.strip(), "description_lines": []}
            continue
        if current is not None:
            docs[current]["description_lines"].append(stripped)
    return {
        name: {"type": str(values.get("type", "")).strip(), "description": " ".join(values.get("description_lines", [])).strip()}
        for name, values in docs.items()
    }


def _documentation_fields(info: FunctionInfo) -> dict[str, Any]:
    """Return user-facing documentation fields frozen into a public record."""
    doc = ast.get_docstring(info.node)
    sections = _docstring_sections(doc)
    param_docs = _parameter_doc_metadata(sections.get("parameters", ""))
    positional = [arg for arg in [*info.node.args.posonlyargs, *info.node.args.args] if arg.arg not in {"self", "cls"}]
    positional_required = len(positional) - len(info.node.args.defaults)
    parameters: list[dict[str, str]] = []

    def row(arg: ast.arg, required: bool) -> dict[str, str]:
        doc_row = param_docs.get(arg.arg, {})
        annotation = ast.unparse(arg.annotation) if arg.annotation is not None else ""
        return {
            "name": arg.arg,
            "required": "Yes" if required else "No",
            "type": annotation or doc_row.get("type", ""),
            "description": doc_row.get("description", "Not documented yet") or "Not documented yet",
        }

    for index, arg in enumerate(positional):
        parameters.append(row(arg, index < positional_required))
    for arg, default in zip(info.node.args.kwonlyargs, info.node.args.kw_defaults):
        parameters.append(row(arg, default is None))
    return {
        "signature": _signature_from_node(info.node),
        "summary": _first_sentence(doc) or "No summary available.",
        "parameters": parameters,
        "returns_documentation": sections.get("returns", "Not documented yet"),
        "raises_documentation": sections.get("raises", "Not documented yet"),
        "examples": sections.get("examples", "Not documented yet"),
        "usage_notes": sections.get("notes", ""),
        "public_import_path": f"fabricops_kit.{info.function_name}",
    }

def build_payload(root: Path = ROOT, pkg_dir: Path = PKG_DIR, init_path: Path = INIT_PATH, manifests_dir: Path | None = None) -> dict[str, Any]:
    """Build the v2 JSON payload."""
    manifests_dir = manifests_dir or root / "docs" / "releases" / "manifests"
    modules = discover_modules(pkg_dir)
    functions = discover_functions(modules, root)
    public_names = set(read_public_export_names(init_path))
    public_qns = {qn for qn, info in functions.items() if info.function_name in public_names}
    lifecycle_by_qn, release_versions = read_function_lifecycle(manifests_dir)
    validate_public_lifecycle_entries(functions, public_qns, lifecycle_by_qn, release_versions, current_preview_public_api_names())
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
        lifecycle = public_lifecycle(root_qn, root_info.function_name, lifecycle_by_qn)
        live_dependencies = sorted({item["qualified_name"] for item in flow if item["qualified_name"] != root_qn and item["qualified_name"] not in public_qns})
        public_functions.append({
            "function_name": root_info.function_name,
            "qualified_name": root_qn,
            "source_path": root_info.source_path,
            "source_start_line": root_info.source_start_line,
            "source_end_line": root_info.source_end_line,
            **_documentation_fields(root_info),
            **lifecycle_fields(lifecycle),
            "contract_classification": public_contract_classification(lifecycle.lifecycle_status),
            "contract_display": public_contract_display(lifecycle),
            "contract_risk": lifecycle.lifecycle_status,
            "live_critical_dependency_count": len(live_dependencies) if lifecycle.lifecycle_status == "live" else 0,
            "live_critical_dependencies": live_dependencies if lifecycle.lifecycle_status == "live" else [],
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
    live_public_qns = {item["qualified_name"] for item in public_functions if item["lifecycle_status"] == "live"}
    preview_public_qns = {item["qualified_name"] for item in public_functions if item["lifecycle_status"] == "preview"}
    impact = calculate_live_impact(public_functions, public_qns, live_public_qns, preview_public_qns)
    for public_function in public_functions:
        enrich_rows_with_contract(public_function["flow"], impact, public_qns, lifecycle_by_qn)
    defined_functions = [function_record(info, public_qns, lifecycle_by_qn, impact) for info in sorted(functions.values(), key=lambda item: item.qualified_name)]
    unused = [unused_record(functions[qn]) for qn in sorted(set(functions) - used_all)]
    release_contract = {
        "release_versions": release_versions,
        "latest_release_version": release_versions[-1] if release_versions else None,
        "live_public_function_count": len(live_public_qns),
        "preview_public_function_count": len(preview_public_qns),
        "discontinued_public_function_count": sum(1 for item in public_functions if item["lifecycle_status"] == "discontinued"),
        "live_critical_internal_count": sum(1 for qn, item in impact.items() if qn not in public_qns and item["supports_live_contract"]),
    }
    return {
        "metadata": {
            "schema": "fabricops_public_function_call_flows_v2",
            "source_json_url": SOURCE_JSON_URL,
            "source": "src/fabricops_kit",
            "public_function_source": "src/fabricops_kit/__init__.py::__all__",
            "architecture_violation_rules": ARCHITECTURE_VIOLATION_RULES,
            "architecture_violation_signal": "Any Type 1 to Type 5 edge appears in the public function flow.",
        },
        "public_functions": public_functions,
        "defined_functions": defined_functions,
        "used_functions": sorted(used_all),
        "defined_but_not_used": unused,
        "release_contract": release_contract,
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


def function_record(
    info: FunctionInfo,
    public_qns: set[str],
    lifecycle_by_qn: dict[str, ReleaseFunctionLifecycle],
    impact_by_qn: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Return a serializable function record."""
    record = {
        "function_name": info.function_name,
        "qualified_name": info.qualified_name,
        "source_path": info.source_path,
        "source_start_line": info.source_start_line,
        "source_end_line": info.source_end_line,
        "function_type": function_type(info, public_qns, info.qualified_name if info.qualified_name in public_qns else None),
    }
    impact = impact_by_qn.get(info.qualified_name, {})
    record.update({
        "direct_live_dependents": impact.get("direct_live_dependents", []),
        "direct_live_dependent_count": impact.get("direct_live_dependent_count", 0),
        "transitive_live_dependents": impact.get("transitive_live_dependents", []),
        "transitive_live_dependent_count": impact.get("transitive_live_dependent_count", 0),
        "supports_live_contract": impact.get("supports_live_contract", False),
        "live_impact_level": impact.get("live_impact_level", "none"),
    })
    if info.qualified_name in public_qns:
        lifecycle = public_lifecycle(info.qualified_name, info.function_name, lifecycle_by_qn)
        record.update(lifecycle_fields(lifecycle))
        record["contract_classification"] = public_contract_classification(lifecycle.lifecycle_status)
        record["contract_display"] = public_contract_display(lifecycle)
    else:
        record.update({"lifecycle_status": "internal", "live_since": None, "discontinued_in": None, "release_history": [], "release_versions": []})
        record["contract_classification"] = internal_contract_classification(record)
        record["contract_display"] = internal_contract_display(record["contract_classification"])
    return record


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



def freeze_release_payload(payload: dict[str, Any], *, release_version: str, source_ref: str) -> dict[str, Any]:
    """Return a Live-only release-specific call-flow payload from generated source data."""
    frozen = copy.deepcopy(payload)
    live_public: list[dict[str, Any]] = []
    live_roots: set[str] = set()
    for row in frozen.get("public_functions", []):
        history = row.get("release_history") or []
        release_status = next((item.get("status") for item in history if str(item.get("version")) == release_version), None)
        if release_status == "live":
            row["lifecycle_status"] = "live"
            row["release_version"] = release_version
            row["source_ref"] = source_ref
            row["release_history"] = [item for item in history if str(item.get("version")) == release_version]
            live_public.append(row)
            live_roots.add(str(row.get("qualified_name")))
    frozen["public_functions"] = live_public
    retained_qns = {
        str(flow_row.get("qualified_name"))
        for public_row in live_public
        for flow_row in public_row.get("flow", [])
        if flow_row.get("qualified_name")
    }
    retained_qns.update(live_roots)
    frozen["defined_functions"] = [
        row for row in frozen.get("defined_functions", [])
        if row.get("qualified_name") in retained_qns
    ]
    frozen["used_functions"] = sorted(qn for qn in frozen.get("used_functions", []) if qn in retained_qns)
    frozen["defined_but_not_used"] = [
        row for row in frozen.get("defined_but_not_used", [])
        if row.get("qualified_name") in retained_qns
    ]
    live_critical_internal_count = sum(
        1
        for row in frozen["defined_functions"]
        if row.get("function_type") not in PUBLIC_CALLABLE_TYPES and row.get("contract_classification") == "live_critical_internal"
    )
    frozen["release_contract"] = {
        "release_versions": [release_version],
        "latest_release_version": release_version,
        "live_public_function_count": len(live_public),
        "preview_public_function_count": 0,
        "discontinued_public_function_count": 0,
        "live_critical_internal_count": live_critical_internal_count,
        "source_ref": source_ref,
        "frozen": True,
    }
    frozen["metadata"] = dict(frozen.get("metadata", {})) | {
        "release_version": release_version,
        "source_ref": source_ref,
        "contract_kind": "frozen_release_live_only",
    }
    frozen["summary"] = {
        "public_function_count": len(live_public),
        "defined_function_count": len(frozen["defined_functions"]),
        "used_function_count": len(frozen["used_functions"]),
        "defined_but_not_used_count": len(frozen["defined_but_not_used"]),
    }
    return frozen

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
