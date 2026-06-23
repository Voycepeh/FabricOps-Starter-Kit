"""Generate function reference helpers."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from datetime import UTC, datetime
import html
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
PKG_DIR = ROOT / "src" / "fabricops_kit"
PACKAGE_NAME = "fabricops_kit"
INIT_PATH = PKG_DIR / "__init__.py"
DOCS_METADATA_PATH = ROOT / "scripts" / "reference_docs_metadata.py"
REFERENCE_PATH = ROOT / "docs" / "reference" / "index.md"
REFERENCE_DATA_DIR = ROOT / "docs" / "reference" / "_data"
MODULE_DIR = ROOT / "docs" / "api" / "modules"
MKDOCS_PATH = ROOT / "mkdocs.yml"
DEPENDENCY_METADATA_PATH = REFERENCE_DATA_DIR / "dependency-metadata.json"
CALL_GRAPH_PAGE_PATH = ROOT / "docs" / "reference" / "call-graph.md"
CALLABLE_REFERENCE_DIR = ROOT / "docs" / "api" / "reference"
LEGACY_CALLABLE_REFERENCE_DIR = ROOT / "docs" / "reference" / "callables"
INTERNAL_REFERENCE_DIR = ROOT / "docs" / "reference" / "internal"
MANIFEST_PATH = REFERENCE_DATA_DIR / "manifest.json"
AGENT_MANIFEST_PATH = REFERENCE_DATA_DIR / "automation-manifest.json"
FUNCTION_MANIFEST_PATH = REFERENCE_DATA_DIR / "function-manifest.json"
REFACTOR_SIGNALS_PATH = REFERENCE_DATA_DIR / "refactor-signals.json"
CALLABLE_FLOW_PAGE_PATH = ROOT / "docs" / "reference" / "callable-flow.md"
CALLABLE_FLOW_DATA_PATH = REFERENCE_DATA_DIR / "callable-flow.json"
REFACTOR_DASHBOARD_PATH = ROOT / "docs" / "assets" / "callable-functions-dashboard.html"
REFACTOR_INVENTORY_PATH = ROOT / "docs" / "assets" / "callable-functions-inventory.html"
CALLABLE_SURFACE_AUDIT_PATH = REFERENCE_DATA_DIR / "callable-surface-audit.json"
FUNCTION_TAXONOMY_AUDIT_PATH = REFERENCE_DATA_DIR / "function-taxonomy-audit.json"
GLOSSARY_SOURCE_PATH = REFERENCE_DATA_DIR / "glossary.json"
GLOSSARY_PAGE_PATH = ROOT / "docs" / "reference" / "glossary.md"
LANDING_PAGE_PATH = ROOT / "docs" / "index.md"
LANDING_STATS_PATH = REFERENCE_DATA_DIR / "landing-stats.json"

METADATA_REFERENCE_DIR = ROOT / "docs" / "reference" / "metadata"
METADATA_REFERENCE_OVERVIEW = ROOT / "docs" / "reference" / "metadata.md"
GITHUB_REPO_URL = "https://github.com/Voycepeh/FabricOps-Starter-Kit"
DEFAULT_SOURCE_REF = "main"
GENERATE_INTERNAL_REFERENCE_PAGES_ENV = "FABRICOPS_GENERATE_INTERNAL_REFERENCE_PAGES"
CORE_TEMPLATE_KEYS = {"00_env_config", "01_agreement", "02_pipeline", "03_governance", "99_explore"}

def plural_word(count: int, singular: str, plural: str) -> str:
    """Return singular or plural text for a count."""
    return singular if count == 1 else plural


def markdown_anchor(value: str) -> str:
    """Return a Material for MkDocs-compatible heading anchor."""
    anchor = re.sub(r"[^a-z0-9 -]", "", value.lower())
    return re.sub(r"[ -]+", "-", anchor).strip("-")



PUBLIC_MODULE_PREFERRED_NAMES = {
    "config": "config",
    "data_agreement": "data_agreement",
    "governance_review": "governance_review",
    "data_profiling": "data_profiling",
    "fabric_input_output": "fabric_input_output",
    "guardrails": "guardrails",
    "metadata": "metadata",
    "pipeline": "pipeline",
}
MAJOR_IMPLEMENTATION_MODULE_ORDER = [
    "config",
    "data_agreement",
    "governance_review",
    "data_profiling",
    "fabric_input_output",
    "io",
    "io_core",
    "guardrails",
    "metadata",
    "pipeline",
]
MAJOR_IMPLEMENTATION_MODULES = set(MAJOR_IMPLEMENTATION_MODULE_ORDER)
INTERNAL_MODULE_BLACKLIST = {"_utils"}
INTERNAL_ALIAS_MODULES = {}

# Callable reference pages are generated from src/fabricops_kit/__init__.py::__all__.
# Keep __all__ as the canonical notebook-facing public callable surface;
# PUBLIC_SYMBOL_DOCS supplies metadata for those exports and may retain extra
# internal helper metadata for relationship details.

# Internal helper chips should mirror the generated package-local call tree.
# Exclude reachable private helpers only when a callable has an explicit deny
# rule here; this keeps ordinary private implementation helpers visible while
# suppressing intentionally noisy shared plumbing.
INTERNAL_HELPER_EXCLUSIONS: dict[str, set[str]] = {
    "enforce_profile_behavior": {
        "fabricops_kit.fabric_input_output._normalize_schema_name",
        "fabricops_kit.config._get_store",
    },
    "run_table_guardrails": {
        "fabricops_kit.config._current_audit_timestamp",
        "fabricops_kit.config._get_audit_timezone",
        "fabricops_kit.config._validate_audit_timezone",
    },
}


SCHEMA_RUNTIME_INTERNAL_HELPERS = {
    f"{PACKAGE_NAME}.guardrails._check_schema_runtime",
    f"{PACKAGE_NAME}.guardrails._check_schema_rule_runtime",
}


def _is_public_reference_qn(qn: str, node_by_qn: dict[str, dict[str, Any]]) -> bool:
    """Return whether a qualified name should appear in public relationship lists."""
    return bool(node_by_qn.get(qn, {}).get("exported"))


def _hide_from_public_relationships(qn: str) -> bool:
    """Return whether an internal helper should be hidden from public relationship chips."""
    return qn in SCHEMA_RUNTIME_INTERNAL_HELPERS


INTERNAL_HELPER_AUDIT_DECISIONS = {
    "fabricops_kit.config._get_store": "keep_internal",
    "fabricops_kit.config._normalize_path_config": "keep_internal",
    "fabricops_kit.fabric_input_output._normalize_table_name": "keep_internal",
    "fabricops_kit.fabric_input_output._normalize_schema_name": "keep_internal",
    "fabricops_kit.fabric_input_output._resolve_lakehouse_schema": "keep_internal",
    "fabricops_kit.fabric_input_output._resolve_lakehouse_table_path": "keep_internal",
    "fabricops_kit.fabric_input_output._get_spark": "keep_internal",
}

INTERNAL_HELPER_AUDIT_RATIONALE = {
    "keep_internal": "Repeated usage alone is not enough for public utility status; this underscore-prefixed helper exposes implementation plumbing or normalized runtime details rather than a stable user-facing task.",
    "already_covered_by_existing_public_utility": "The direct user-facing need is already covered by an existing public utility, so the helper should stay private.",
    "promote_to_public_utility_candidate": "The helper appears to have stable user-facing behavior, understandable parameters, and return values that can be documented without leaking implementation details.",
}

@dataclass
class Symbol:
    """Symbol metadata container."""

    name: str
    actual_module: str
    public_module: str
    obj_type: str
    summary: str
    role: str = "callable"
    purpose: str = ""


def first_sentence(doc: str | None) -> str:
    """Return the first sentence."""
    if not doc:
        return ""
    line = doc.strip().splitlines()[0].strip()
    return line.split(".")[0].strip() + ("." if "." in line else "")


def _assert_non_placeholder_summary(symbol_name: str, field_name: str, text: str) -> None:
    """Fail fast when placeholder-style summary text is detected."""
    normalized = text.strip()
    if normalized.startswith("Execute the `"):
        raise RuntimeError(f"{symbol_name} has placeholder {field_name}: {normalized}")
    if "Input parameter `" in normalized:
        raise RuntimeError(f"{symbol_name} has placeholder {field_name}: {normalized}")


def _signature_from_node(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> str:
    """Return a compact source signature for a function or class."""
    if isinstance(node, ast.ClassDef):
        bases = [ast.unparse(base) for base in node.bases]
        return f"class {node.name}({', '.join(bases)})" if bases else f"class {node.name}"
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    returns = f" -> {ast.unparse(node.returns)}" if node.returns is not None else ""
    return f"{prefix} {node.name}({ast.unparse(node.args)}){returns}"


def _docstring_sections(doc: str | None) -> dict[str, str]:
    """Extract simple NumPy-style docstring sections without changing behavior."""
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
    """Return first-paragraph NumPy-style parameter docs keyed by parameter name."""
    docs: dict[str, dict[str, Any]] = {}
    current: str | None = None
    for raw_line in parameters_section.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if not line.startswith(" ") and " : " in line:
            names_part, type_part = stripped.split(" : ", 1)
            names = names_part.split(",")
            current = names[0].strip()
            docs[current] = {"type": type_part.strip(), "description_lines": []}
            continue
        if current is not None:
            docs[current]["description_lines"].append(stripped)
    return {
        name: {"type": str(values.get("type", "")).strip(), "description": " ".join(values.get("description_lines", [])).strip()}
        for name, values in docs.items()
    }


def _clean_parameter_type(type_text: str) -> str:
    """Return a compact parameter type label for definition-list rendering."""
    cleaned = type_text.replace("``", "").strip()
    for suffix in (", optional", ", default=None", ", default = None"):
        cleaned = cleaned.replace(suffix, "")
    return cleaned.strip()


def _parameter_rows_from_node(node: ast.FunctionDef | ast.AsyncFunctionDef, parameters_section: str) -> list[dict[str, str]]:
    """Return compact parameter metadata for generated callable input sections."""
    docs = _parameter_doc_metadata(parameters_section)
    positional = [arg for arg in [*node.args.posonlyargs, *node.args.args] if arg.arg not in {"self", "cls"}]
    positional_required = len(positional) - len(node.args.defaults)
    rows: list[dict[str, str]] = []

    def _row(arg: ast.arg, required: bool) -> dict[str, str]:
        doc = docs.get(arg.arg, {})
        annotation = ast.unparse(arg.annotation) if arg.annotation is not None else ""
        return {
            "name": arg.arg,
            "required": "Yes" if required else "No",
            "type": _clean_parameter_type(annotation or doc.get("type", "")),
            "description": doc.get("description", PLACEHOLDER) or PLACEHOLDER,
        }

    for index, arg in enumerate(positional):
        rows.append(_row(arg, index < positional_required))
    for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
        rows.append(_row(arg, default is None))
    return rows


def _is_dataclass_class(node: ast.ClassDef) -> bool:
    """Return whether a class node is decorated as a dataclass."""
    return any(
        (isinstance(decorator, ast.Name) and decorator.id == "dataclass")
        or (isinstance(decorator, ast.Attribute) and decorator.attr == "dataclass")
        or (
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Name)
            and decorator.func.id == "dataclass"
        )
        or (
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Attribute)
            and decorator.func.attr == "dataclass"
        )
        for decorator in node.decorator_list
    )


def _is_property_method(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return whether a function node is decorated as a property accessor."""
    return any(
        (isinstance(decorator, ast.Name) and decorator.id == "property")
        or (isinstance(decorator, ast.Attribute) and decorator.attr == "property")
        for decorator in node.decorator_list
    )



def source_module_name(path: Path) -> str:
    """Return a dotted package-relative source module name."""
    return ".".join(path.relative_to(PKG_DIR).with_suffix("").parts)


def source_module_paths() -> list[Path]:
    """Return package source files that participate in generated callable metadata."""
    return sorted(path for path in PKG_DIR.rglob("*.py") if path.name != "__init__.py")


def source_module_path(module: str) -> Path:
    """Return the source path for a dotted package-relative module name."""
    if module == "io":
        return PKG_DIR / "io" / "shared.py"
    return PKG_DIR.joinpath(*module.split(".")).with_suffix(".py")

def parse_module(path: Path) -> dict[str, Any]:
    """Parse module."""
    source_text = path.read_text(encoding="utf-8")
    tree = ast.parse(source_text)
    functions: dict[str, str] = {}
    classes: dict[str, str] = {}
    constants: dict[str, str] = {}
    calls: dict[str, set[str]] = {}
    used_by: dict[str, set[str]] = {}
    signatures: dict[str, str] = {}
    doc_sections: dict[str, dict[str, str]] = {}
    source_locations: dict[str, dict[str, int]] = {}
    parameters: dict[str, list[dict[str, str]]] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node)
            functions[node.name] = first_sentence(doc)
            signatures[node.name] = _signature_from_node(node)
            sections = _docstring_sections(doc)
            doc_sections[node.name] = sections
            source_locations[node.name] = {"start_line": node.lineno, "end_line": getattr(node, "end_lineno", node.lineno)}
            parameters[node.name] = _parameter_rows_from_node(node, sections.get("parameters", ""))
            called = set()
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name):
                        called.add(child.func.id)
                    elif isinstance(child.func, ast.Attribute):
                        called.add(child.func.attr)
            calls[node.name] = called
        elif isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node)
            classes[node.name] = first_sentence(doc)
            signatures[node.name] = _signature_from_node(node)
            sections = _docstring_sections(doc)
            doc_sections[node.name] = sections
            source_locations[node.name] = {"start_line": node.lineno, "end_line": getattr(node, "end_lineno", node.lineno)}
            for child in node.body:
                if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                method_name = f"{node.name}.{child.name}"
                method_doc = ast.get_docstring(child)
                functions[method_name] = first_sentence(method_doc)
                signatures[method_name] = _signature_from_node(child)
                method_sections = _docstring_sections(method_doc)
                doc_sections[method_name] = method_sections
                source_locations[method_name] = {
                    "start_line": child.lineno,
                    "end_line": getattr(child, "end_lineno", child.lineno),
                }
                parameters[method_name] = _parameter_rows_from_node(child, method_sections.get("parameters", ""))
                called = set()
                for grandchild in ast.walk(child):
                    if isinstance(grandchild, ast.Call):
                        if isinstance(grandchild.func, ast.Name):
                            called.add(grandchild.func.id)
                        elif isinstance(grandchild.func, ast.Attribute):
                            if isinstance(grandchild.func.value, ast.Name) and grandchild.func.value.id in {"self", "cls"}:
                                called.add(f"{node.name}.{grandchild.func.attr}")
                            else:
                                called.add(grandchild.func.attr)
                calls[method_name] = called
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    constants[target.id] = ""
        elif isinstance(node, ast.AnnAssign):
            target = node.target
            if isinstance(target, ast.Name) and target.id.isupper():
                constants[target.id] = ""
    names = set(functions) | set(classes)
    for caller, callees in calls.items():
        for callee in names:
            if callee in callees:
                used_by.setdefault(callee, set()).add(caller)
    return {
        "functions": functions,
        "classes": classes,
        "constants": constants,
        "calls": calls,
        "used_by": used_by,
        "signatures": signatures,
        "doc_sections": doc_sections,
        "source_locations": source_locations,
        "parameters": parameters,
    }


def parse_import_aliases(nodes: list[ast.stmt]) -> tuple[dict[str, str], dict[str, str]]:
    """Parse import aliases."""
    module_aliases: dict[str, str] = {}
    symbol_aliases: dict[str, str] = {}
    for node in nodes:
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name
                module_aliases[name] = alias.name
        elif isinstance(node, ast.ImportFrom):
            if not node.module:
                continue
            for alias in node.names:
                if alias.name == "*":
                    continue
                name = alias.asname or alias.name
                symbol_aliases[name] = f"{node.module}.{alias.name}"
    return module_aliases, symbol_aliases


def collect_function_calls(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[dict[str, str]]:
    """Collect function and callable object calls."""
    calls: list[dict[str, str]] = []
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        call_target = ""
        call_type = "unknown"
        if isinstance(child.func, ast.Name):
            call_target = child.func.id
            call_type = "name"
        elif isinstance(child.func, ast.Attribute):
            attr = child.func.attr
            if isinstance(child.func.value, ast.Name):
                call_target = f"{child.func.value.id}.{attr}"
            else:
                call_target = attr
            call_type = "attribute"
        if call_target:
            calls.append({"raw_name": call_target, "call_type": call_type})
    return calls


def resolve_call_target(
    module: str,
    raw_name: str,
    module_aliases: dict[str, str],
    symbol_aliases: dict[str, str],
    same_module_names: set[str],
    exported_symbol_map: dict[str, Symbol],
    package_module_names: set[str],
) -> tuple[str | None, str, str]:
    """Resolve call target."""
    def _classify_callee(module_name: str, symbol_name: str) -> str:
        mapped = exported_symbol_map.get(symbol_name)
        if mapped and mapped.actual_module == module_name:
            return "public_export"
        if symbol_name.startswith("_"):
            return "internal_helper"
        return "internal_callable"
    # same-module callable/class names are always safe to resolve first
    if raw_name in same_module_names:
        return f"{PACKAGE_NAME}.{module}.{raw_name}", "same_module", _classify_callee(module, raw_name)

    # explicit import alias from "from x import y as z"
    if raw_name in symbol_aliases:
        imported = symbol_aliases[raw_name]
        imported_short = imported.split(".")
        if len(imported_short) >= 2 and (imported.startswith(PACKAGE_NAME) or imported_short[-2] in package_module_names):
            resolved_module = imported_short[-2]
            resolved_symbol = imported_short[-1]
            callee_kind = _classify_callee(resolved_module, resolved_symbol)
            return (
                f"{PACKAGE_NAME}.{resolved_module}.{resolved_symbol}",
                "cross_module" if resolved_module != module else "same_module",
                callee_kind,
            )

    # module/alias call like alias.func() or module.func()
    if "." in raw_name:
        owner, member = raw_name.split(".", 1)
        mapped_owner = module_aliases.get(owner, owner)
        short_owner = mapped_owner.split(".")[-1]
        if mapped_owner.startswith(PACKAGE_NAME) or short_owner in package_module_names:
            resolved_module = short_owner if short_owner in package_module_names else mapped_owner.rsplit(".", 1)[-1]
            callee_kind = _classify_callee(resolved_module, member)
            return f"{PACKAGE_NAME}.{resolved_module}.{member}", "cross_module" if resolved_module != module else "same_module", callee_kind
        return None, "unresolved", "unresolved"

    # public exported symbol map fallback (bare-name cross-module only for exported mapping)
    exported = exported_symbol_map.get(raw_name)
    if exported and exported.actual_module != module:
        callee_kind = _classify_callee(exported.actual_module, raw_name)
        return f"{PACKAGE_NAME}.{exported.actual_module}.{raw_name}", "cross_module", callee_kind

    return None, "unresolved", "unresolved"


def build_callable_graph(
    module_data: dict[str, dict[str, Any]],
    symbol_map: dict[str, Symbol],
    public_exports: list[str],
    docs_metadata: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Build callable graph."""
    package_modules = {m for m in module_data if m not in {"docs_metadata"}}
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    node_keys: set[tuple[str, str]] = set()
    module_summaries: list[dict[str, Any]] = []
    calls_modules: dict[str, set[str]] = {m: set() for m in package_modules}
    called_by_modules: dict[str, set[str]] = {m: set() for m in package_modules}

    for module, info in module_data.items():
        module_tree = ast.parse(source_module_path(module).read_text(encoding="utf-8"))
        module_aliases, symbol_aliases = parse_import_aliases(list(getattr(module_tree, "body", [])))
        functions = info.get("functions", {})
        classes = info.get("classes", {})
        exported_names = {name for name, sym in symbol_map.items() if sym.actual_module == module}
        same_module_names = set(functions) | set(classes)
        dataclass_post_init_methods = {
            f"{class_node.name}.__post_init__"
            for class_node in module_tree.body
            if isinstance(class_node, ast.ClassDef) and _is_dataclass_class(class_node)
            for child in class_node.body
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == "__post_init__"
        }
        property_accessor_methods = {
            f"{class_node.name}.{child.name}"
            for class_node in module_tree.body
            if isinstance(class_node, ast.ClassDef)
            for child in class_node.body
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_property_method(child)
        }
        for callable_name in sorted(set(functions) | set(classes)):
            role = str(
                docs_metadata.get(callable_name, {}).get("function_type")
                or "internal"
            ).lower()
            exported = callable_name in exported_names
            if not exported and role not in {"callable", "internal"}:
                role = "internal"
            qualified_name = f"{PACKAGE_NAME}.{module}.{callable_name}"
            key = (module, callable_name)
            if key not in node_keys:
                node_keys.add(key)
                nodes.append(
                    {
                        "callable_name": callable_name,
                        "module_name": module,
                        "qualified_name": qualified_name,
                        "role": role if exported else "internal",
                        "exported": exported,
                        "is_underscore": callable_name.split(".")[-1].startswith("_"),
                        "callable_kind": (
                            "class"
                            if callable_name in classes
                            else "implicit_lifecycle_method"
                            if callable_name in dataclass_post_init_methods
                            else "property_accessor"
                            if callable_name in property_accessor_methods
                            else "callable_object"
                            if callable_name.endswith(".__call__")
                            else "method"
                            if "." in callable_name
                            else "function"
                        ),
                    }
                )

        callable_nodes: list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]] = []
        for node in module_tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                callable_nodes.append((node.name, node))
            elif isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        callable_nodes.append((f"{node.name}.{child.name}", child))
        for caller_name, node in callable_nodes:
            caller_qn = f"{PACKAGE_NAME}.{module}.{caller_name}"
            local_module_aliases, local_symbol_aliases = parse_import_aliases(
                [n for n in ast.walk(node) if isinstance(n, (ast.Import, ast.ImportFrom))]
            )
            merged_module_aliases = {**module_aliases, **local_module_aliases}
            merged_symbol_aliases = {**symbol_aliases, **local_symbol_aliases}
            for call in collect_function_calls(node):
                raw_name = call["raw_name"]
                if raw_name.startswith(("self.", "cls.")) and "." in caller_name:
                    raw_name = f"{caller_name.rsplit('.', 1)[0]}.{raw_name.split('.', 1)[1]}"
                resolved_qn, edge_type, callee_kind = resolve_call_target(
                    module, raw_name, merged_module_aliases, merged_symbol_aliases, same_module_names, symbol_map, package_modules
                )
                edge = {
                    "caller_qualified_name": caller_qn,
                    "callee_qualified_name": resolved_qn,
                    "callee_raw_name": raw_name if resolved_qn is None else None,
                    "edge_type": edge_type,
                    "callee_kind": callee_kind,
                }
                edges.append(edge)
                if resolved_qn and edge_type in {"same_module", "cross_module"}:
                    callee_module = resolved_qn.split(".")[1] if resolved_qn.startswith(f"{PACKAGE_NAME}.") else resolved_qn.split(".")[-2]
                    if callee_module != module:
                        calls_modules[module].add(callee_module)
                        called_by_modules[callee_module].add(module)

        public_count = len([name for name in exported_names if not name.startswith("_")])
        helper_count = len([name for name in functions if name.startswith("_")])
        module_summaries.append(
            {
                "module": module,
                "calls_modules": sorted(calls_modules.get(module, set())),
                "called_by_modules": sorted(called_by_modules.get(module, set())),
                "public_callable_count": public_count,
                "internal_helper_count": helper_count,
            }
        )
    return nodes, edges, sorted(module_summaries, key=lambda x: x["module"])


def parse_public_exports() -> list[str]:
    """Parse public exports."""
    tree = ast.parse(INIT_PATH.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
            if isinstance(node.value, ast.List):
                return [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)]
    raise RuntimeError("Could not parse __all__ from __init__.py")



def public_callable_names() -> set[str]:
    """Return notebook-facing public callables from canonical __all__ exports."""
    return set(parse_public_exports())


def parse_docs_metadata() -> dict[str, dict[str, Any]]:
    """Parse docs metadata."""
    namespace = runpy.run_path(str(DOCS_METADATA_PATH))
    rows = namespace.get("PUBLIC_SYMBOL_DOCS")
    if not isinstance(rows, list):
        raise RuntimeError("Could not parse PUBLIC_SYMBOL_DOCS from reference_docs_metadata.py")
    seen = set()
    out = {}
    for row in rows:
        name = row["symbol_name"]
        if name in seen:
            raise RuntimeError(f"Duplicate PUBLIC_SYMBOL_DOCS symbol_name detected: {name}")
        seen.add(name)
        out[name] = row
    return out


def parse_template_flow_docs() -> list[dict[str, Any]]:
    """Parse template flow docs."""
    tree = ast.parse(DOCS_METADATA_PATH.read_text(encoding="utf-8"))
    for node in tree.body:
        is_assign = isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "TEMPLATE_FLOW_DOCS" for t in node.targets
        )
        is_annassign = isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "TEMPLATE_FLOW_DOCS"
        if (is_assign or is_annassign) and node.value is not None:
            return ast.literal_eval(node.value)
    raise RuntimeError("Could not parse TEMPLATE_FLOW_DOCS from reference_docs_metadata.py")


def parse_module_docs_metadata() -> list[dict[str, Any]]:
    """Parse module docs metadata."""
    tree = ast.parse(DOCS_METADATA_PATH.read_text(encoding="utf-8"))
    for node in tree.body:
        is_assign = isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "MODULE_DOCS_METADATA" for t in node.targets
        )
        is_annassign = isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "MODULE_DOCS_METADATA"
        if (is_assign or is_annassign) and node.value is not None:
            return ast.literal_eval(node.value)
    raise RuntimeError("Could not parse MODULE_DOCS_METADATA from reference_docs_metadata.py")



def parse_glossary_metadata() -> dict[str, dict[str, Any]]:
    """Return glossary metadata keyed by normalized canonical terms and aliases."""
    if not GLOSSARY_SOURCE_PATH.exists():
        return {}
    entries = json.loads(GLOSSARY_SOURCE_PATH.read_text(encoding="utf-8"))
    glossary: dict[str, dict[str, Any]] = {}
    required_fields = {
        "term",
        "aliases",
        "category",
        "short_definition",
        "long_definition",
        "preferred_usage",
        "avoid_usage",
    }
    for entry in entries:
        missing = sorted(required_fields - set(entry))
        term = str(entry.get("term", "")).strip()
        if not term:
            raise RuntimeError("Glossary entries must include a term.")
        if missing:
            raise RuntimeError(f"Glossary entry {term!r} is missing: {', '.join(missing)}")
        if not entry.get("short_definition") or not entry.get("long_definition"):
            raise RuntimeError(f"Glossary entry {term!r} must include short and long definitions.")
        aliases = entry.get("aliases")
        if not isinstance(aliases, list):
            raise RuntimeError(f"Glossary entry {term!r} aliases must be a list.")
        canonical_key = term.lower()
        if canonical_key in glossary:
            raise RuntimeError(f"Duplicate glossary term or alias: {term}")
        glossary[canonical_key] = entry
        for alias in aliases:
            alias_key = str(alias).strip().lower()
            if not alias_key:
                continue
            if alias_key in glossary:
                raise RuntimeError(f"Duplicate glossary term or alias: {alias}")
            glossary[alias_key] = entry
    return glossary


def _render_glossary_page(glossary: dict[str, dict[str, Any]]) -> None:
    """Render the public glossary page from structured glossary metadata."""
    lines = [
        "# FabricOps glossary",
        "",
        "Searchable source of truth for FabricOps documentation wording and page-level glossary references.",
        "",
    ]
    canonical_entries = list({id(entry): entry for entry in glossary.values()}.values())
    for category in sorted({str(entry["category"]) for entry in canonical_entries}):
        lines.extend([f"## {category}", ""])
        category_entries = [entry for entry in canonical_entries if entry["category"] == category]
        lines.append('<div class="glossary-definition-list">')
        lines.append("")
        for entry in sorted(category_entries, key=lambda row: row["term"].lower()):
            term = str(entry["term"])
            lines.extend(
                [
                    f'<section class="glossary-definition-card" id="{markdown_anchor(term)}">',
                    f'<h2>{term}</h2>',
                    f"<p>{entry['long_definition']}</p>",
                ]
            )
            if entry.get("aliases"):
                lines.append(
                    f'<p class="glossary-definition-meta"><strong>Aliases:</strong> '
                    f"{', '.join(f'`{item}`' for item in entry['aliases'])}</p>"
                )
            lines.extend(
                [
                    f'<p class="glossary-definition-meta"><strong>Preferred usage:</strong> {entry["preferred_usage"]}</p>',
                    f'<p class="glossary-definition-meta"><strong>Avoid usage:</strong> {entry["avoid_usage"]}</p>',
                    "</section>",
                    "",
                ]
            )
        lines.extend(["</div>", ""])
    GLOSSARY_PAGE_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")



def _render_related_guides(related_guides: list[dict[str, str]]) -> list[str]:
    """Render conceptual documentation links for a callable page."""
    if not related_guides:
        return []

    lines = ["## See also", ""]
    seen: set[tuple[str, str]] = set()
    for guide in related_guides:
        title = str(guide.get("title", "")).strip()
        path = str(guide.get("path", "")).strip()
        if not title or not path:
            raise RuntimeError("related_guides entries must include both title and path")
        key = (title, path)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"- [{title}]({path})")
    lines.append("")
    return lines

def _render_key_terms(glossary_terms: list[str], glossary: dict[str, dict[str, Any]]) -> list[str]:
    """Render compact glossary-backed key terms for a callable page."""
    if not glossary_terms:
        return []
    lines: list[str] = ['<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">']
    seen: set[str] = set()
    for term in glossary_terms:
        key = term.lower()
        entry = glossary.get(key)
        if entry is None:
            raise RuntimeError(f"Callable references unknown glossary term: {term}")
        canonical_key = str(entry["term"]).lower()
        if canonical_key in seen:
            continue
        seen.add(canonical_key)
        term_text = str(entry["term"])
        display_term = term_text if "_" in term_text else term_text.capitalize()
        anchor = markdown_anchor(str(entry["term"]))
        lines.append(
            f'<span class="glossary-chip">'
            f'<span class="glossary-chip-label">{display_term}</span>'
            f'<span class="glossary-chip-definition">{entry["short_definition"]}</span> '
            f'<a href="../../../reference/glossary/#{anchor}">Full definition</a></span>'
        )
    lines.extend(["</div>", "", "See the [full glossary](../../../reference/glossary/) for more FabricOps terms."])
    return lines


def _metadata_parameter_overrides(value: Any) -> dict[str, str]:
    """Return parameter descriptions supplied by callable metadata."""
    if isinstance(value, dict):
        return {str(key): str(item) for key, item in value.items()}
    return {}


def _markdown_table_cell(text: str) -> str:
    """Escape characters that would otherwise split a Markdown table cell."""
    return text.replace("|", r"\|").replace("\n", "<br>")


def _render_parameter_definitions(parameter_rows: list[dict[str, str]], parameter_overrides: dict[str, str]) -> list[str]:
    """Render parameters as a compact API-reference Markdown table."""
    if not parameter_rows:
        return ["No parameters."]
    lines = ["| Parameter | Type | Required | Description |", "| --- | --- | --- | --- |"]
    for row in parameter_rows:
        name = row["name"]
        required_label = "Yes" if row.get("required") == "Yes" else "No"
        type_text = _markdown_table_cell(row.get("type", "").strip() or "—")
        meaning = _markdown_table_cell(parameter_overrides.get(name, row.get("description", PLACEHOLDER)))
        lines.append(f"| `{name}` | `{type_text}` | {required_label} | {meaning} |")
    return lines


def _validate_preferred_example(short_name: str, signature: str, example: str) -> None:
    """Fail when a documented example obviously conflicts with the source signature."""
    if not example.strip():
        return
    try:
        parsed = ast.parse(example)
    except SyntaxError as exc:
        raise RuntimeError(f"{short_name} preferred_example is not valid Python: {exc}") from exc

    calls = [node for node in ast.walk(parsed) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == short_name]
    if not calls:
        return

    keyword_only_match = re.search(rf"def {re.escape(short_name)}\(\*, (?P<body>.*)\)", signature)
    if keyword_only_match is None:
        return

    valid_keyword_names = {
        token.split(":", 1)[0].split("=", 1)[0].strip()
        for token in keyword_only_match.group("body").split(",")
        if token.strip()
    }
    for call in calls:
        if call.args:
            raise RuntimeError(f"{short_name} preferred_example must use keyword arguments for keyword-only parameters.")
        unknown_keywords = {kw.arg for kw in call.keywords if kw.arg is not None} - valid_keyword_names
        if unknown_keywords:
            names = ", ".join(sorted(unknown_keywords))
            raise RuntimeError(f"{short_name} preferred_example uses parameters not in the signature: {names}")


def _render_preferred_example(short_name: str, signature: str, metadata: dict[str, Any]) -> str:
    """Return a validated preferred example for the callable reference page."""
    example = _documented_text(metadata.get("preferred_example"))
    if example != PLACEHOLDER:
        _validate_preferred_example(short_name, signature, example)
    return example

def _read_template_source(template_path: str) -> str:
    """Return searchable source text from a starter notebook/template file."""
    path = ROOT / template_path
    if not path.exists():
        return ""
    if path.suffix == ".ipynb":
        try:
            notebook = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return path.read_text(encoding="utf-8")
        chunks: list[str] = []
        for cell in notebook.get("cells", []):
            source = cell.get("source", "")
            chunks.append("".join(source) if isinstance(source, list) else str(source))
        return "\n".join(chunks)
    return path.read_text(encoding="utf-8")


def _python_source_for_template_analysis(source_text: str) -> str:
    """Return parseable Python source for notebook call analysis."""
    lines: list[str] = []
    for line in source_text.splitlines():
        if line.lstrip().startswith(("%", "!")):
            lines.append(f"# {line}")
        else:
            lines.append(line)
    return "\n".join(lines)


def _direct_public_template_symbols(template_path: str, public_symbols: set[str]) -> list[str]:
    """Return public package callables directly called by a notebook template."""
    path = ROOT / template_path
    if not path.exists():
        return []
    source_text = _read_template_source(template_path)
    if path.suffix == ".ipynb":
        try:
            notebook = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            notebook = {"cells": []}
        code_chunks: list[str] = []
        for cell in notebook.get("cells", []):
            if cell.get("cell_type") != "code":
                continue
            source = cell.get("source", "")
            code_chunks.append("".join(source) if isinstance(source, list) else str(source))
        source_text = "\n".join(code_chunks)
    if not source_text:
        return []
    try:
        tree = ast.parse(_python_source_for_template_analysis(source_text))
    except SyntaxError as exc:
        raise RuntimeError(f"Could not parse template for function map validation: {template_path}") from exc

    imported_symbol_by_name: dict[str, str] = {}
    package_aliases: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith(PACKAGE_NAME):
            for alias in node.names:
                if alias.name in public_symbols:
                    imported_symbol_by_name[alias.asname or alias.name] = alias.name
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == PACKAGE_NAME:
                    package_aliases.add(alias.asname or alias.name)

    direct_symbols: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id in imported_symbol_by_name:
            direct_symbols.add(imported_symbol_by_name[func.id])
        elif (
            isinstance(func, ast.Attribute)
            and func.attr in public_symbols
            and isinstance(func.value, ast.Name)
            and func.value.id in package_aliases
        ):
            direct_symbols.add(func.attr)

    return sorted(direct_symbols)


def _derive_template_usage(
    template_flow_docs: list[dict[str, Any]],
    symbol_map: dict[str, Symbol],
    node_by_qn: dict[str, dict[str, Any]],
    calls_by_qn: dict[str, list[str]],
) -> dict[str, list[str]]:
    """Map public callable names to starter templates that directly call them."""
    del node_by_qn, calls_by_qn
    template_order = {flow["notebook_key"]: index for index, flow in enumerate(template_flow_docs)}
    usage: dict[str, set[str]] = {name: set() for name in symbol_map}

    for flow in template_flow_docs:
        notebook_key = flow["notebook_key"]
        direct_symbols = set(_direct_public_template_symbols(flow.get("template_path", ""), set(symbol_map)))
        for symbol in direct_symbols:
            usage.setdefault(symbol, set()).add(notebook_key)

    return {
        symbol: sorted(notebooks, key=lambda notebook: (template_order.get(notebook, len(template_order)), notebook))
        for symbol, notebooks in usage.items()
    }


def _derive_template_usage_by_kind(
    template_flow_docs: list[dict[str, Any]],
    symbol_map: dict[str, Symbol],
) -> tuple[dict[str, list[str]], dict[str, list[str]], dict[str, bool]]:
    """Return direct core calls, example calls, and import-only template usage."""
    template_order = {flow["notebook_key"]: index for index, flow in enumerate(template_flow_docs)}
    core_usage: dict[str, set[str]] = {name: set() for name in symbol_map}
    example_usage: dict[str, set[str]] = {name: set() for name in symbol_map}
    imported_symbols: dict[str, bool] = {name: False for name in symbol_map}
    public_symbols = set(symbol_map)

    for flow in template_flow_docs:
        notebook_key = flow["notebook_key"]
        template_path = flow.get("template_path", "")
        direct_symbols = set(_direct_public_template_symbols(template_path, public_symbols))
        source_text = _read_template_source(template_path)
        for symbol in public_symbols:
            if re.search(rf"\b{re.escape(symbol)}\b", source_text) and symbol not in direct_symbols:
                imported_symbols[symbol] = True
        target = core_usage if notebook_key in CORE_TEMPLATE_KEYS else example_usage
        for symbol in direct_symbols:
            target.setdefault(symbol, set()).add(notebook_key)

    def _sorted_usage(usage: dict[str, set[str]]) -> dict[str, list[str]]:
        return {
            symbol: sorted(notebooks, key=lambda notebook: (template_order.get(notebook, len(template_order)), notebook))
            for symbol, notebooks in usage.items()
        }

    return _sorted_usage(core_usage), _sorted_usage(example_usage), imported_symbols


def generate_internal_reference_pages() -> bool:
    """Return whether standalone internal helper pages should be generated."""
    return os.environ.get(GENERATE_INTERNAL_REFERENCE_PAGES_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


def internal_helper_link(actual_module: str, helper: str) -> str:
    """Return module-page-relative link target for an internal helper page."""
    return f"../../reference/internal/{actual_module}_{helper}/"


def public_reference_link(
    symbol: str,
    docs_metadata: dict[str, dict[str, Any]],
    *,
    context: str = "module",
) -> str:
    """Return context-relative link target for a public callable page."""
    if symbol not in docs_metadata:
        raise RuntimeError(f"Missing PUBLIC_SYMBOL_DOCS entry for exported symbol: {symbol}")
    if context == "module":
        return f"../reference/{symbol}/"
    if context == "reference":
        return f"../api/reference/{symbol}/"
    if context == "template_map":
        return f"../api/reference/{symbol}/"
    if context == "notebook":
        return f"../api/reference/{symbol}/"
    raise RuntimeError(f"Unknown link context: {context}")


def callable_docs_link(
    symbol_name: str,
    module: str,
    docs_metadata: dict[str, dict[str, Any]],
    *,
    context: str = "module",
    source_module: str | None = None,
) -> str:
    """Return a safe docs link for a public callable."""
    if symbol_name in docs_metadata and symbol_name in public_callable_names():
        return public_reference_link(symbol_name, docs_metadata, context=context)
    if context == "module":
        if source_module and module != source_module:
            return f"{module}/#{symbol_name}"
        return f"#{symbol_name}"
    if context == "reference":
        return f"../../api/modules/{module}/#{symbol_name}"
    if context == "notebook":
        return f"../../api/modules/{module}/#{symbol_name}"
    raise RuntimeError(f"Unknown link context: {context}")


def resolve_preferred_actual_module(preferred_module: str) -> str:
    """Return the likely source module that owns callable implementations."""
    return next((actual for actual, public_name in PUBLIC_MODULE_PREFERRED_NAMES.items() if public_name == preferred_module), preferred_module)


def canonical_public_module(module_name: str) -> str:
    """Return the canonical docs/public module name for metadata and manifests."""
    return PUBLIC_MODULE_PREFERRED_NAMES.get(module_name, module_name)




def render_html_table(headers: list[str], rows: list[list[str]], *, table_class: str = "") -> list[str]:
    """Render html table."""
    class_attr = f' class="{table_class}"' if table_class else ""
    lines = [f"<table{class_attr}>", "  <thead>", "    <tr>"]
    for header in headers:
        lines.append(f"      <th>{header}</th>")
    lines.extend(["    </tr>", "  </thead>", "  <tbody>"])
    for row in rows:
        lines.append("    <tr>")
        for idx, cell in enumerate(row):
            label_attr = f' data-label="{html_escape(headers[idx])}"' if table_class in {"reference-template-table", "reference-function-table"} else ""
            lines.append(f"      <td{label_attr}>{cell}</td>")
        lines.append("    </tr>")
    lines.extend(["  </tbody>", "</table>"])
    return lines


def github_source_ref() -> str:
    """Return the stable GitHub ref used by generated source links.

    Generated documentation is published independently from local working trees.
    A local commit SHA can 404 after publishing when it has not been pushed or
    is otherwise unreachable from GitHub, so generated links default to
    ``main``. Release automation may set ``GITHUB_SOURCE_REF`` or
    ``FABRICOPS_SOURCE_REF`` only when it can guarantee the ref is reachable.
    """
    for variable in ("GITHUB_SOURCE_REF", "FABRICOPS_SOURCE_REF"):
        explicit_ref = os.environ.get(variable, "").strip()
        if explicit_ref:
            return explicit_ref
    return DEFAULT_SOURCE_REF


def github_source_url(source_path: str, start_line: int | None = None, end_line: int | None = None) -> str:
    """Return a GitHub blob URL for a source file and optional line span."""
    anchor = ""
    if start_line:
        anchor = f"#L{start_line}"
        if end_line and end_line != start_line:
            anchor += f"-L{end_line}"
    return f"{GITHUB_REPO_URL}/blob/{github_source_ref()}/{source_path}{anchor}"


def markdown_details(summary: str, body_lines: list[str], *, class_name: str = "reference-detail") -> list[str]:
    """Render a collapsed Markdown details block."""
    return [f'<details class="{class_name}">', f"<summary>{html_escape(summary)}</summary>", "", *body_lines, "", "</details>"]


def html_escape(text: str) -> str:
    """Escape text for generated inline HTML snippets."""
    return (
        text.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def function_chip(name: str, href: str) -> str:
    """Return a clickable function chip for generated docs tables."""
    return f'<a class="function-chip" href="{html_escape(href)}"><code>{html_escape(name)}</code></a>'


def _display_source_path(source_path: str) -> str:
    """Return the package-relative source path used in compact source cards."""
    return source_path.removeprefix("src/")


def _source_card_lines(
    *,
    source_path: str,
    source_start_line: int | None,
    source_ref: str,
    short_name: str,
) -> list[str]:
    """Render a compact source location card with a visible GitHub action."""
    display_path = _display_source_path(source_path)
    line_suffix = f":{source_start_line}" if source_start_line else ""
    return [
        '<div class="reference-source-card" markdown="1">',
        "**Source**",
        "",
        f"`{display_path}{line_suffix}`",
        "",
        f'<a class="reference-source-link" href="{source_ref}">View on GitHub</a>',
        "</div>",
    ]


PLACEHOLDER = "Not documented yet"


def _metadata_text(value: Any) -> str:
    """Render metadata values as markdown-friendly text."""
    if value is None or value == "":
        return PLACEHOLDER
    if isinstance(value, dict):
        return "\n".join(f"- `{key}`: {item}" for key, item in value.items()) or PLACEHOLDER
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value) or PLACEHOLDER
    return str(value)


def _documented_text(*values: Any) -> str:
    """Return the first documented text value or a standard placeholder."""
    for value in values:
        text = _metadata_text(value)
        if text != PLACEHOLDER:
            return text
    return PLACEHOLDER


def _code_block(text: str) -> str:
    """Return a fenced Python block for generated reference pages."""
    return f"```python\n{text}\n```"


def _split_top_level_csv(text: str) -> list[str]:
    """Split a comma-separated string while respecting bracketed type expressions."""
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    quote: str | None = None
    escape = False
    for char in text:
        if quote:
            current.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            continue
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth = max(0, depth - 1)
        if char == "," and depth == 0:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
        else:
            current.append(char)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def _format_api_signature(signature: str, *, max_inline_length: int = 88) -> str:
    """Return a compact, readable API-definition signature for callable pages."""
    cleaned = signature.strip()
    if not cleaned or len(cleaned) <= max_inline_length or not cleaned.startswith(("def ", "async def ")):
        return cleaned

    match = re.match(r"(?P<prefix>async def|def) (?P<name>\w+)\((?P<body>.*)\)(?P<returns>\s*->\s*.+)?$", cleaned)
    if not match:
        return cleaned

    args = _split_top_level_csv(match.group("body"))
    returns = (match.group("returns") or "").strip()
    rendered_args: list[str] = []
    for arg in args:
        if arg == "*":
            continue
        rendered_args.append(f"    {arg},")
    suffix = f" {returns}" if returns else ""
    return "\n".join([f"{match.group('prefix')} {match.group('name')}(", *rendered_args, f"){suffix}:"])


def _reference_code_block(text: str, *, class_name: str) -> list[str]:
    """Return a styled Markdown-in-HTML code block for callable reference pages."""
    if not text:
        return [PLACEHOLDER]
    return [
        f'<div class="{class_name}" markdown="1">',
        "",
        _code_block(text),
        "",
        "</div>",
    ]


def _bullet_lines(text: str) -> list[str]:
    """Return short markdown bullets for human-facing guidance text."""
    cleaned = text.strip()
    if not cleaned:
        return [f"- {PLACEHOLDER}"]
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    if len(lines) > 1:
        return [line if line.startswith(("- ", "* ")) else f"- {line}" for line in lines]
    return [cleaned if cleaned.startswith(("- ", "* ")) else f"- {cleaned}"]


def _ai_contract_block(
    *,
    required_context: str,
    inputs: str,
    output: str,
    side_effects: str,
    failure_modes: str,
    verification: str,
) -> str:
    """Render a compact structured implementation contract."""
    return "\n".join(
        [
            f"- **required_context:** {required_context}",
            f"- **inputs:** {inputs}",
            f"- **output:** {output}",
            f"- **side_effects:** {side_effects}",
            f"- **failure_modes:** {failure_modes}",
            f"- **verification:** {verification}",
        ]
    )


def _related_function_links(
    related: list[str],
    node_by_qn: dict[str, dict[str, Any]],
    docs_metadata: dict[str, dict[str, Any]],
) -> list[str]:
    """Render related function links for callable and internal pages."""
    rows: list[str] = []
    for item in related:
        qn = item if item.startswith(f"{PACKAGE_NAME}.") else next(
            (candidate_qn for candidate_qn, candidate_node in node_by_qn.items() if candidate_node["callable_name"] == item),
            item,
        )
        node = node_by_qn.get(qn)
        label = qn
        if node and node.get("exported"):
            href = f"{node['callable_name']}/"
        elif node and generate_internal_reference_pages():
            href = f"../internal/{node['module_name']}_{node['callable_name']}/"
        elif node:
            rows.append(f"- `{label}`")
            continue
        elif item in docs_metadata and item in public_callable_names():
            href = f"../{item}/"
            label = item
        else:
            rows.append(f"- `{label}`")
            continue
        rows.append(f'- <a href="{href}"><code>{label}</code></a>')
    return rows



def _is_internal_helper_qn(qn: str, node_by_qn: dict[str, dict[str, Any]]) -> bool:
    """Return whether a qualified name identifies an internal helper node."""
    node = node_by_qn.get(qn, {})
    return bool(node) and not node.get("exported") and node.get("callable_name", "").startswith("_")


def _collect_internal_helper_descendants(
    root_qn: str,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
) -> list[str]:
    """Return private helper qualified names reachable through the full call tree."""
    seen: set[str] = set()
    helpers: list[str] = []

    def visit(qn: str) -> None:
        for callee in sorted(set(calls_by_qn.get(qn, []))):
            if callee in seen or callee not in node_by_qn:
                continue
            seen.add(callee)
            if _is_internal_helper_qn(callee, node_by_qn):
                helpers.append(callee)
            visit(callee)

    visit(root_qn)
    return helpers


def _callable_flow_internal_helper_qns(
    root_qn: str,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
) -> list[str]:
    """Return sorted internal helper qualified names for callable-flow output."""
    root_name = node_by_qn.get(root_qn, {}).get("callable_name", "")
    excluded_helpers = INTERNAL_HELPER_EXCLUSIONS.get(root_name, set())
    helper_qns = {
        helper_qn
        for helper_qn in _collect_internal_helper_descendants(root_qn, calls_by_qn, node_by_qn)
        if helper_qn not in excluded_helpers
    }
    return sorted(
        helper_qns,
        key=lambda qn: (node_by_qn[qn]["module_name"], node_by_qn[qn]["callable_name"].lower(), qn),
    )


def _call_tree_link(
    qn: str,
    root_qn: str,
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
) -> str | None:
    """Return the generated docs or source URL for a call-tree node when available."""
    node = node_by_qn.get(qn)
    if not node:
        return None
    if qn == root_qn:
        return None
    if node.get("exported"):
        return f"../{node['callable_name']}/"
    module_name = node.get("module_name")
    callable_name = node.get("callable_name")
    if module_name and callable_name and module_name in module_data:
        source_location = module_data.get(module_name, {}).get("source_locations", {}).get(callable_name, {})
        return github_source_url(
            f"src/fabricops_kit/{module_name}.py",
            source_location.get("start_line"),
            source_location.get("end_line"),
        )
    return None


def _call_tree_label(
    qn: str,
    root_qn: str,
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
    *,
    recursive: bool = False,
) -> str:
    """Render one call-tree callable label, linking package callables when possible."""
    node = node_by_qn.get(qn)
    name = node.get("callable_name", qn) if node else qn
    label = f"<code>{html_escape(name)}(...)</code>"
    href = _call_tree_link(qn, root_qn, node_by_qn, module_data)
    if href:
        label = f'<a href="{html_escape(href)}">{label}</a>'
    if recursive:
        label += ' <span class="reference-call-tree-note">(recursive)</span>'
    return label


def _render_clickable_call_tree(
    root_qn: str,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
) -> list[str]:
    """Render the full reachable package call tree with recursion protection."""
    lines = [
        '<div class="reference-call-tree" role="tree">',
        f'  <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span>{_call_tree_label(root_qn, root_qn, node_by_qn, module_data)}</div>',
    ]

    def children(qn: str) -> list[str]:
        return sorted(
            {c for c in calls_by_qn.get(qn, []) if c in node_by_qn},
            key=lambda c: (0 if _is_internal_helper_qn(c, node_by_qn) else 1, node_by_qn[c]["callable_name"].lower(), c),
        )

    def visit(qn: str, prefix: str, ancestors: set[str]) -> None:
        child_qns = children(qn)
        for index, child in enumerate(child_qns):
            connector = "└── " if index == len(child_qns) - 1 else "├── "
            recursive = child in ancestors
            lines.append(
                f'  <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">{html_escape(prefix + connector)}</span>{_call_tree_label(child, root_qn, node_by_qn, module_data, recursive=recursive)}</div>'
            )
            if not recursive:
                extension = "    " if index == len(child_qns) - 1 else "│   "
                visit(child, prefix + extension, ancestors | {child})

    visit(root_qn, "", {root_qn})
    lines.append("</div>")
    return lines


def _helper_area_mismatch_signal(helper_name: str, purpose: str, assigned_area: str) -> tuple[str, str, str] | None:
    """Return a wrong-area signal only when name, purpose, and assignment disagree."""
    name_area, _ = _helper_area(helper_name, "")
    purpose_area, _ = _helper_area("", purpose)
    if (
        name_area != "Other"
        and purpose_area != "Other"
        and assigned_area != "Other"
        and len({assigned_area, name_area, purpose_area}) == 3
    ):
        return assigned_area, name_area, purpose_area
    return None



def _remove_stale_function_taxonomy_audit() -> None:
    """Remove the retired taxonomy audit generated for the old public model."""
    FUNCTION_TAXONOMY_AUDIT_PATH.unlink(missing_ok=True)


def _flow_by_public_qualified_name(callable_flow_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return callable architecture flow records keyed by public qualified name."""
    return {
        flow["qualified_name"]: flow
        for flow in callable_flow_data.get("public_entrypoint_flow", [])
        if flow.get("qualified_name")
    }


def _render_callable_architecture_flow_tree(
    flow: dict[str, Any],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
) -> list[str]:
    """Render the same callable flow tree structure used by the dashboard inventory JSON."""
    root_qn = flow["qualified_name"]
    by_parent: dict[str, list[dict[str, Any]]] = {}
    for row in flow.get("transitive_callees", []):
        parent_qn = row.get("parent_qualified_name") or root_qn
        by_parent.setdefault(parent_qn, []).append(row)

    lines = [
        '<div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">',
        f'  <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span>{_call_tree_label(root_qn, root_qn, node_by_qn, module_data)}</div>',
    ]

    def sort_key(row: dict[str, Any]) -> tuple[int, str, str, str]:
        return (
            int(row.get("depth") or 0),
            str(row.get("module") or ""),
            str(row.get("callable") or "").lower(),
            str(row.get("qualified_name") or ""),
        )

    def visit(parent_qn: str, prefix: str, ancestors: set[str]) -> None:
        child_rows = sorted(by_parent.get(parent_qn, []), key=sort_key)
        for index, child_row in enumerate(child_rows):
            child_qn = child_row.get("qualified_name")
            if not child_qn:
                continue
            connector = "└── " if index == len(child_rows) - 1 else "├── "
            recursive = child_qn in ancestors
            lines.append(
                f'  <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">{html_escape(prefix + connector)}</span>{_call_tree_label(child_qn, root_qn, node_by_qn, module_data, recursive=recursive)}</div>'
            )
            if not recursive:
                extension = "    " if index == len(child_rows) - 1 else "│   "
                visit(child_qn, prefix + extension, ancestors | {child_qn})

    visit(root_qn, "", {root_qn})
    lines.append("</div>")
    return lines


def _collect_refactor_signals(
    root_qn: str,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
    *,
    excluded_helpers: set[str] | None = None,
) -> dict[str, Any]:
    """Return structured maintainability signals discovered from the full call tree."""
    excluded_helpers = excluded_helpers or set()

    def children(qn: str) -> list[str]:
        return sorted(
            {c for c in calls_by_qn.get(qn, []) if c in node_by_qn},
            key=lambda c: node_by_qn[c]["callable_name"].lower(),
        )

    occurrences: dict[str, int] = {}
    deep_chains: list[list[str]] = []

    def walk(qn: str, path: list[str]) -> None:
        if len(path) > 5:
            deep_chains.append(path)
        for child in children(qn):
            if child not in excluded_helpers:
                occurrences[child] = occurrences.get(child, 0) + 1
            if child not in path:
                walk(child, [*path, child])

    walk(root_qn, [root_qn])

    repeated_helpers = sorted(
        (
            (qn, count)
            for qn, count in occurrences.items()
            if count > 1 and _is_internal_helper_qn(qn, node_by_qn)
        ),
        key=lambda item: (-item[1], node_by_qn[item[0]]["callable_name"].lower()),
    )
    single_delegate_helpers = sorted(
        qn
        for qn in occurrences
        if (
            _is_internal_helper_qn(qn, node_by_qn)
            and len(children(qn)) == 1
            and _is_internal_helper_qn(children(qn)[0], node_by_qn)
        )
    )

    area_mismatch_signals: list[tuple[str, str, str, str, str]] = []
    for qn in occurrences:
        if not _is_internal_helper_qn(qn, node_by_qn):
            continue
        node = node_by_qn[qn]
        module_name = node["module_name"]
        helper_name = node["callable_name"]
        purpose = module_data[module_name].get("functions", {}).get(helper_name) or ""
        assigned_area, _ = _helper_area(helper_name, purpose)
        signal = _helper_area_mismatch_signal(helper_name, purpose, assigned_area)
        if signal:
            name_area: str
            purpose_area: str
            assigned_area, name_area, purpose_area = signal
            area_mismatch_signals.append((helper_name, qn, assigned_area, name_area, purpose_area))

    helper_qns = [
        helper_qn
        for helper_qn in _collect_internal_helper_descendants(root_qn, calls_by_qn, node_by_qn)
        if helper_qn not in excluded_helpers
    ]
    return {
        "qualified_name": root_qn,
        "unique_internal_helper_count": len(helper_qns),
        "repeated_helpers": [
            {
                "helper": node_by_qn[qn]["callable_name"],
                "qualified_name": qn,
                "branch_count": count,
            }
            for qn, count in repeated_helpers[:12]
        ],
        "deep_call_chains": [
            {
                "depth": len(path) - 1,
                "chain": path,
            }
            for path in deep_chains[:8]
        ],
        "single_delegate_helpers": [
            {
                "helper": node_by_qn[qn]["callable_name"],
                "qualified_name": qn,
                "delegates_to": node_by_qn[children(qn)[0]]["callable_name"],
                "delegates_to_qualified_name": children(qn)[0],
            }
            for qn in single_delegate_helpers[:12]
        ],
        "possible_grouping_mismatches": [
            {
                "area": assigned_area,
                "reason": (
                    f"`{helper_name}` is grouped as `{assigned_area}`, but its name suggests "
                    f"`{name_area}` while its summary suggests `{purpose_area}`."
                ),
                "helpers": [
                    {
                        "helper": helper_name,
                        "qualified_name": qn,
                        "name_area": name_area,
                        "purpose_area": purpose_area,
                    }
                ],
            }
            for helper_name, qn, assigned_area, name_area, purpose_area in sorted(
                area_mismatch_signals,
                key=lambda item: (item[2].lower(), item[0].lower()),
            )[:8]
        ],
    }


def _render_refactor_signals(
    signals: dict[str, Any],
    node_by_qn: dict[str, dict[str, Any]],
) -> list[str]:
    """Render structured maintainability signals as human-readable Markdown."""

    def label(qn: str) -> str:
        return node_by_qn[qn]["callable_name"]

    lines = ["### Refactor signals", ""]
    lines.append(
        "These generated hints point maintainers to call-tree shapes worth reviewing; "
        "they are not automatic refactor requirements."
    )
    lines.append("")

    lines.append("**Helpers appearing in multiple branches**")
    lines.append("")
    lines.extend(
        [
            f"- `{item['helper']}` appears in {item['branch_count']} branches."
            for item in signals["repeated_helpers"]
        ]
        or ["- None detected in the reachable package-local call tree."]
    )
    lines.extend(["", "**Call chains deeper than 4 levels**", ""])
    lines.extend(
        [
            f"- {' → '.join(f'`{label(item)}`' for item in chain['chain'])}"
            for chain in signals["deep_call_chains"]
        ]
        or ["- None detected."]
    )
    lines.extend(["", "**Helpers that only call one package-local helper**", ""])
    lines.extend(
        [
            f"- `{item['helper']}` only delegates to `{item['delegates_to']}`."
            for item in signals["single_delegate_helpers"]
        ]
        or ["- None detected."]
    )
    lines.extend(["", "**Helpers grouped into possibly wrong areas**", ""])
    lines.extend(
        [f"- {item['reason']}" for item in signals["possible_grouping_mismatches"]]
        or ["- None detected from helper names, doc summaries, and module placement."]
    )
    return lines


def _reachable_callables(
    root_qn: str,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
) -> set[str]:
    """Return package-local callable qualified names reachable from a root."""
    reachable: set[str] = set()

    def visit(qn: str, ancestors: set[str]) -> None:
        for child in sorted(set(calls_by_qn.get(qn, []))):
            if child not in node_by_qn or child in ancestors:
                continue
            reachable.add(child)
            visit(child, ancestors | {child})

    visit(root_qn, {root_qn})
    return reachable


def _deepest_call_chain_depth(
    root_qn: str,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
) -> int:
    """Return the deepest package-local call-chain depth below the root."""

    def depth(qn: str, ancestors: set[str]) -> int:
        child_depths = [
            1 + depth(child, ancestors | {child})
            for child in sorted(set(calls_by_qn.get(qn, [])))
            if child in node_by_qn and child not in ancestors
        ]
        return max(child_depths, default=0)

    return depth(root_qn, {root_qn})


def _callable_flow_source_location(qn: str, module_data: dict[str, dict[str, Any]]) -> dict[str, int | None]:
    """Return source line metadata for a callable flow node when available."""
    parts = qn.split(".")
    module_name = parts[1] if len(parts) > 2 and parts[0] == PACKAGE_NAME else parts[-2]
    callable_name = ".".join(parts[2:]) if len(parts) > 2 and parts[0] == PACKAGE_NAME else parts[-1]
    source_location = module_data.get(module_name, {}).get("source_locations", {}).get(callable_name, {})
    return {
        "source_start_line": source_location.get("start_line"),
        "source_end_line": source_location.get("end_line"),
    }


def _callable_flow_source_link(qn: str, module_data: dict[str, dict[str, Any]]) -> str | None:
    """Return a source URL for a callable flow node when source metadata exists."""
    parts = qn.split(".")
    module_name = parts[1] if len(parts) > 2 and parts[0] == PACKAGE_NAME else parts[-2]
    callable_name = ".".join(parts[2:]) if len(parts) > 2 and parts[0] == PACKAGE_NAME else parts[-1]
    source_location = module_data.get(module_name, {}).get("source_locations", {}).get(callable_name, {})
    if not source_location:
        return None
    return github_source_url(
        f"src/fabricops_kit/{module_name}.py",
        source_location.get("start_line"),
        source_location.get("end_line"),
    )


REFACTOR_SIGNAL_ORDER = [
    "Thin wrapper candidate",
    "Single-use internal helper",
    "Leaf internal helper",
    "High-fanout helper",
]

REFACTOR_SIGNAL_RECOMMENDATIONS = {
    "Thin wrapper candidate": "Merge candidate",
    "Single-use internal helper": "Review abstraction",
    "Leaf internal helper": "Shared utility",
    "High-fanout helper": "Shared internal helper",
}

REFACTOR_REASON_LABELS = {
    "Thin wrapper candidate": "Likely wrapper / inline candidate",
    "Single-use internal helper": "Used by only one function",
    "Leaf internal helper": "End-of-chain helper",
    "High-fanout helper": "Used by many functions",
    "public_calls_public": "Public calls public",
    "internal_calls_public": "Internal calls public",
    "internal_workflow_calls_internal_workflow": "Internal workflow calls internal workflow",
    "utility_calls_workflow": "Utility calls workflow",
    "validator_calls_workflow": "Validator calls workflow",
    "resolver_calls_workflow": "Resolver calls workflow",
    "model_calls_workflow": "Model calls workflow",
    "allowed_internal_role_call": "Allowed internal role call",
    "implicit_lifecycle_reachability": "Implicit lifecycle reachability",
    "utility_calls_project_callable": "Utility calls project callable",
    "callee_classification_pending": "Callee classification pending",
    "callee_unreachable": "Callee unreachable",
}

REFACTOR_PRIORITY_ORDER = {
    "High": 0,
    "Medium": 1,
    "Low": 2,
    "Review": 3,
    "Protect": 4,
}

REFACTOR_PRIORITY_ACTIONS = {
    "Protect": "Shared internal helper",
    "High": "Merge candidate",
    "Medium": "Review abstraction",
    "Low": "Shared utility",
    "Review": "Review manually",
}

ACTION_LEGEND = {
    "Public API entrypoint": "Supported user-facing API surface; no inbound project calls are required.",
    "Shared internal helper": "Internal implementation helper used by multiple public or internal callers; protect with focused tests before changing.",
    "Shared utility": "Low-level leaf helper with multiple inbound callers; keep generic and project-callable free.",
    "Merge candidate": "Small helper or single-use utility; consider flattening into its caller after checking readability.",
    "Review abstraction": "Helper used by only one function; verify the name, boundary, and test value justify keeping it separate.",
    "Review manually": "No clear automated recommendation; inspect intent before changing structure.",
    "Architecture violation": "Callable dependency direction breaks the public → internal → utility layer rule.",
    "Orphaned callable": "Private callable with no reachable public lineage; remove or reconnect if still needed.",
}


def _callable_flow_source_path(qn: str) -> str | None:
    """Return the repository source path for a package callable."""
    parts = qn.split(".")
    if len(parts) < 3:
        return None
    module_name = parts[1] if parts[0] == PACKAGE_NAME else parts[-2]
    return f"src/fabricops_kit/{module_name}.py"


def _project_inbound_callers(
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
) -> dict[str, set[str]]:
    """Return project-local inbound callers for each callable qualified name."""
    inbound: dict[str, set[str]] = {qn: set() for qn in node_by_qn}
    for caller_qn, callees in calls_by_qn.items():
        if caller_qn not in node_by_qn:
            continue
        for callee_qn in set(callees):
            if callee_qn in node_by_qn:
                inbound.setdefault(callee_qn, set()).add(caller_qn)
    return inbound


def _refactor_priority(signals: list[str]) -> str:
    """Return the dashboard priority for an aggregated helper signal list."""
    if "High-fanout helper" in signals:
        return "Protect"
    if "Thin wrapper candidate" in signals:
        return "High"
    if "Single-use internal helper" in signals:
        return "Medium"
    if "Leaf internal helper" in signals:
        return "Low"
    return "Review"


def _build_refactor_inventory(
    public_qns: list[str],
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
) -> tuple[dict[str, int], list[dict[str, Any]], list[dict[str, Any]]]:
    """Build one aggregated refactor inventory row per internal helper."""
    inbound_by_qn = _project_inbound_callers(calls_by_qn, node_by_qn)
    signal_index = {name: index for index, name in enumerate(REFACTOR_SIGNAL_ORDER)}
    inventory: list[dict[str, Any]] = []

    def sorted_qns(qns: set[str]) -> list[str]:
        return sorted(
            qns,
            key=lambda item: (node_by_qn[item]["module_name"], node_by_qn[item]["callable_name"].lower()),
        )

    def outbound_project_calls(qn: str) -> list[str]:
        return sorted_qns({callee for callee in calls_by_qn.get(qn, []) if callee in node_by_qn})

    def public_lineage(qn: str) -> list[dict[str, str]]:
        lineage: list[dict[str, str]] = []
        for public_qn in public_qns:
            if qn not in _reachable_callables(public_qn, calls_by_qn, node_by_qn):
                continue
            callable_name = node_by_qn[public_qn]["callable_name"]
            lineage.append(
                {
                    "callable": callable_name,
                    "qualified_name": public_qn,
                    "module": node_by_qn[public_qn]["module_name"],
                    "docs_url": _public_callable_docs_url(callable_name),
                }
            )
        return sorted(lineage, key=lambda item: item["callable"].lower())

    def helper_depth(qn: str) -> int | None:
        depths: list[int] = []
        for public_qn in public_qns:
            queue: list[tuple[str, int]] = [(public_qn, 0)]
            seen = {public_qn}
            while queue:
                current_qn, depth = queue.pop(0)
                if current_qn == qn:
                    depths.append(depth)
                    break
                for callee_qn in calls_by_qn.get(current_qn, []):
                    if callee_qn not in node_by_qn or callee_qn in seen:
                        continue
                    seen.add(callee_qn)
                    queue.append((callee_qn, depth + 1))
        return min(depths) if depths else None

    for qn in sorted_qns(set(node_by_qn)):
        if not _is_internal_helper_qn(qn, node_by_qn):
            continue
        inbound = sorted_qns(inbound_by_qn.get(qn, set()))
        outbound = outbound_project_calls(qn)
        inbound_count = len(inbound)
        outbound_count = len(outbound)
        signals: list[str] = []
        if inbound_count == 1 and outbound_count == 1:
            signals.append("Thin wrapper candidate")
        if inbound_count == 1:
            signals.append("Single-use internal helper")
        if outbound_count == 0:
            signals.append("Leaf internal helper")
        if inbound_count >= 5:
            signals.append("High-fanout helper")
        signals.sort(key=lambda signal: signal_index[signal])
        priority = _refactor_priority(signals)
        node = node_by_qn[qn]
        inventory.append(
            {
                "function": node["callable_name"],
                "module": node["module_name"],
                "qualified_name": qn,
                "is_internal": True,
                "signals": signals,
                "priority": priority,
                "suggested_action": REFACTOR_PRIORITY_ACTIONS[priority],
                "recommended_action": REFACTOR_PRIORITY_ACTIONS[priority],
                "inbound_count": inbound_count,
                "outbound_project_call_count": outbound_count,
                "nesting_level": helper_depth(qn),
                "public_entrypoint_lineage": public_lineage(qn),
                "used_by": [
                    {
                        "function": node_by_qn[caller]["callable_name"],
                        "module": node_by_qn[caller]["module_name"],
                        "qualified_name": caller,
                        "source_url": _callable_flow_source_link(caller, module_data),
                    }
                    for caller in inbound
                ],
                "calls": [
                    {
                        "function": node_by_qn[callee]["callable_name"],
                        "module": node_by_qn[callee]["module_name"],
                        "qualified_name": callee,
                        "source_url": _callable_flow_source_link(callee, module_data),
                    }
                    for callee in outbound
                ],
                "source_path": _callable_flow_source_path(qn),
                "source_url": _callable_flow_source_link(qn, module_data),
                **_callable_flow_source_location(qn, module_data),
            }
        )

    inventory.sort(
        key=lambda row: (REFACTOR_PRIORITY_ORDER[row["priority"]], row["module"], row["function"].lower())
    )
    legacy_signal_rows = [
        {
            "function": row["function"],
            "module": row["module"],
            "qualified_name": row["qualified_name"],
            "is_internal": row["is_internal"],
            "inbound_count": row["inbound_count"],
            "outbound_project_call_count": row["outbound_project_call_count"],
            "signal": signal,
            "recommendation": REFACTOR_SIGNAL_RECOMMENDATIONS[signal],
            "used_by": row["used_by"],
            "calls": row["calls"],
            "source_path": row["source_path"],
            "source_url": row["source_url"],
        }
        for row in inventory
        for signal in row["signals"]
    ]
    legacy_signal_rows.sort(
        key=lambda row: (
            signal_index[row["signal"]],
            row["module"],
            row["function"].lower(),
        )
    )
    summary_counts = {
        "thin_wrapper_candidates": sum(
            1 for row in inventory if "Thin wrapper candidate" in row["signals"]
        ),
        "single_use_internal_helpers": sum(
            1 for row in inventory if "Single-use internal helper" in row["signals"]
        ),
        "leaf_internal_helpers": sum(1 for row in inventory if "Leaf internal helper" in row["signals"]),
        "high_fanout_helpers": sum(1 for row in inventory if "High-fanout helper" in row["signals"]),
        "public_api_entrypoints": len(public_qns),
        "internal_helpers": len(inventory),
        "high_priority_candidates": sum(1 for row in inventory if row["priority"] == "High"),
        "medium_priority_candidates": sum(1 for row in inventory if row["priority"] == "Medium"),
        "protect_helpers": sum(1 for row in inventory if row["priority"] == "Protect"),
    }
    return summary_counts, inventory, legacy_signal_rows


CALLABLE_LAYER_LABELS = {
    "public": "Public function",
    "internal": "Internal function",
}

HIDDEN_PRIVATE_LAYER = "private_helper"
PRIVATE_HELPER_LABEL = "Private helper"
SUPPORTING_OBJECT_LAYER = "supporting_object"

REVIEW_STATUS_LABELS = {
    "classified": "Classified",
    "classification_pending": "Classification pending",
    "implicit_lifecycle": "Implicit lifecycle method",
    "property_accessor": "Property accessor",
    "unreachable": "Unreachable",
}

LAYER_CONSISTENCY_LABELS = {
    "implicit_lifecycle": "Implicit lifecycle method",
    "property_accessor": "Property accessor",
    "matches_layer": "Matches expected layer",
    "questionable_utility": "Questionable utility",
    "promote_to_utility_candidate": "Promote to utility candidate",
    "shared_internal_helper": "Shared internal helper",
    "possible_inline_or_private_helper": "Possible inline/private helper",
    "architecture_violation": "Architecture violation",
    "review_manually": "Review manually",
}

LAYER_CONSISTENCY_SIGNALS = {
    "implicit_lifecycle": "Implicit lifecycle method",
    "property_accessor": "Property accessor",
    "questionable_utility": "Utility but low reuse",
    "promote_to_utility_candidate": "Promote candidate",
    "shared_internal_helper": "Shared helper",
    "possible_inline_or_private_helper": "Possible inline/private helper",
    "architecture_violation": "Layer assignment needs review",
    "review_manually": "Layer assignment needs review",
}


def _classify_layer_consistency(
    *,
    architecture_layer: str,
    callable_kind: str,
    used_by_count: int,
    calls_count: int,
    has_architecture_violation: bool,
) -> str:
    """Return whether observed call graph usage supports the assigned layer."""
    if callable_kind == "implicit_lifecycle_method":
        return "implicit_lifecycle"
    if callable_kind == "property_accessor":
        return "property_accessor"

    if has_architecture_violation:
        return "architecture_violation"

    if architecture_layer == "Internal function":
        if used_by_count >= 5:
            return "promote_to_utility_candidate"
        if used_by_count >= 2:
            return "shared_internal_helper"
        if used_by_count <= 1 and callable_kind == "function":
            return "possible_inline_or_private_helper"
        return "matches_layer"

    if architecture_layer == "Public function":
        return "matches_layer"

    return "review_manually"


CONFIG_MODEL_CLASSES = {
    "NotebookRuntimeConfig",
    "QualityConfig",
    "GovernanceConfig",
    "DataAgreementConfig",
    "ReviewWorkflowConfig",
    "LineageConfig",
    "FrameworkConfig",
    "PathConfig",
}

RESULT_MODEL_CLASSES = {"ConfigSmokeCheckResult"}
CONTEXT_MODEL_CLASSES = {"NotebookSetupContext"}

ROLE_TAGS_BY_NAME = {
    "setup_notebook": ["public_api_entrypoint", "notebook_api_entrypoint", "public_stable"],
    "setup_metadata_tables": ["public_api_entrypoint", "metadata_setup_workflow", "public_stable"],
    "_setup_notebook_workflow": ["internal_workflow", "setup_notebook_workflow"],
    "_setup_metadata_tables_workflow": ["internal_workflow", "metadata_setup_workflow"],
    "_get_store": ["internal_resolver", "shared_internal_service", "store_resolver", "high_fanout_shared"],
    "resolve_fabric_context": [
        "internal_resolver",
        "shared_internal_service",
        "runtime_context_resolver",
        "high_fanout_shared",
    ],
    "get_default_fabric_context": ["internal_resolver", "runtime_context_provider", "shared_internal_service"],
    "_current_audit_timestamp": ["audit_time_utility", "shared_internal_service", "high_fanout_shared"],
    "_get_audit_timezone": ["internal_resolver", "audit_config_resolver"],
    "_audit_timestamp_expr": ["audit_time_utility", "spark_audit_expression_utility"],
    "_validate_framework_config": ["internal_validator", "config_validator"],
    "_validate_metadata_table_registration": ["internal_validator", "metadata_table_registration_validator"],
    "_validate_audit_timezone": ["utility_validator", "low_level_utility"],
    "_validate_notebook_name": ["utility_validator", "local_leaf_helper"],
    "_normalize_path_config": ["internal_normalizer", "path_config_normalizer"],
    "_normalize_widget_config": ["internal_normalizer", "widget_config_normalizer"],
    "_get_metadata_table_schema_registry": ["registry_builder", "metadata_schema_registry_builder"],
    "_metadata_schema_field_names": ["schema_utility"],
    "_string_metadata_schema": ["schema_utility", "local_leaf_helper"],
    "_resolve_metadata_schema": ["internal_resolver", "metadata_schema_resolver"],
    "_get_active_metadata_tables": ["internal_resolver", "metadata_registry_query"],
    "_setup_metadata_table_registry": ["internal_adapter", "metadata_registry_write_adapter"],
    "_detect_nested_metadata_delta_folders": ["internal_validator", "storage_guardrail_validator"],
    "_run_config_smoke_tests": ["internal_validator", "setup_smoke_test_validator"],
    "_check_spark_session": ["spark_runtime_probe", "utility_function"],
    "_get_fabric_runtime_metadata": ["fabric_runtime_probe", "internal_adapter"],
    "_list_data_stewards": ["internal_resolver", "data_steward_resolver"],
    "widget_render_agreement_evidence": ["public_api_entrypoint", "widget_entrypoint", "public_stable"],
    "widget_render_data_agreement": ["public_api_entrypoint", "widget_entrypoint", "public_stable"],
    "widget_render_data_steward": ["public_api_entrypoint", "widget_entrypoint", "public_stable"],
    "get_latest_metadata_catalogue": ["public_api_entrypoint", "metadata_lookup_entrypoint", "public_stable"],
    "widget_author_dq_rules": ["public_api_entrypoint", "widget_entrypoint", "public_stable"],
    "widget_author_schema_freshness_profile_rules": ["public_api_entrypoint", "widget_entrypoint", "public_stable"],
    "widget_enrich_table_metadata": ["public_api_entrypoint", "widget_entrypoint", "public_stable"],
    "widget_review_guardrail_governance": ["public_api_entrypoint", "widget_entrypoint", "public_stable"],
    "widget_select_guardrail_target": ["public_api_entrypoint", "widget_entrypoint", "public_stable"],
    "_render_agreement_evidence_widget_workflow": ["internal_workflow", "agreement_evidence_widget_workflow"],
    "_latest_metadata_catalogue_lookup_workflow": ["internal_workflow", "metadata_catalogue_lookup_workflow"],
    "_table_metadata_enrichment_widget_workflow": ["internal_workflow", "widget_workflow"],
    "_schema_freshness_profile_rule_authoring_widget_workflow": ["internal_workflow", "widget_workflow"],
    "_dq_rule_authoring_widget_workflow": ["internal_workflow", "widget_workflow"],
    "_guardrail_target_selection_widget_workflow": ["internal_workflow", "widget_workflow"],
    "_guardrail_governance_review_widget_workflow": ["internal_workflow", "widget_workflow"],
    "_render_maintenance_widget_shared_workflow": ["internal_workflow", "shared_widget_rendering_workflow"],
    "_write_row": ["internal_adapter", "metadata_write_adapter"],
    "_save_agreement_evidence_records": ["internal_adapter", "metadata_write_adapter"],
    "_write_table_metadata_enrichment_records": ["internal_adapter", "metadata_write_adapter"],
    "_write_enrichment_records": ["internal_adapter", "metadata_write_adapter"],
    "_write_rule_records": ["internal_adapter", "metadata_write_adapter"],
    "_read_metadata_table_or_empty": ["internal_adapter", "metadata_read_adapter"],
    "_read_metadata_rows": ["internal_adapter", "metadata_read_adapter"],
    "_get_governance_metadata_schemas": ["internal_resolver", "governance_metadata_schema_resolver"],
    "_latest_row": ["internal_resolver", "latest_metadata_row_resolver"],
    "_latest_rule": ["internal_resolver", "rule_catalogue_resolver"],
    "_active_steward": ["internal_resolver", "active_steward_resolver"],
    "_list_all_data_agreement_rows": ["internal_resolver", "agreement_resolver"],
    "_list_data_agreements": ["internal_resolver", "agreement_resolver"],
    "_validate_dq_rules": ["internal_validator", "dq_rule_validator"],
    "_coerce_rows": ["internal_normalizer", "row_payload_normalizer"],
    "_coerce_row_dicts": ["internal_normalizer", "row_payload_normalizer"],
    "_dq_records_from_selection": ["internal_normalizer", "rule_payload_normalizer"],
    "_schema_freshness_profile_records_from_selection": ["internal_normalizer", "rule_payload_normalizer"],
    "_business_agreement_snapshot": ["internal_normalizer", "agreement_payload_normalizer"],
    "_render_searchable_selector": ["internal_adapter", "widget_rendering_adapter"],
    "_selected_catalogue_rows_for_enrichment": ["internal_resolver", "catalogue_table_resolver"],
    "build_enrichment_rule_records": ["internal_normalizer", "rule_payload_normalizer"],
    "_build_metadata_table_key": ["utility_function", "metadata_key_formatter"],
    "apply_governance_enrichment_action": ["internal_normalizer", "rule_payload_normalizer"],
    "apply_governance_rule_action": ["internal_normalizer", "rule_payload_normalizer"],
    "load_rule_review_history": ["internal_resolver", "rule_catalogue_resolver"],

    # Fabric IO public entrypoints and role-organized internals.
    "read_lakehouse_table": ["public_api_entrypoint", "public_stable", "fabric_io_entrypoint"],
    "write_lakehouse_table": ["public_api_entrypoint", "public_stable", "fabric_io_entrypoint"],
    "read_lakehouse_csv": ["public_api_entrypoint", "public_stable", "fabric_io_entrypoint"],
    "read_lakehouse_parquet": ["public_api_entrypoint", "public_stable", "fabric_io_entrypoint"],
    "read_lakehouse_excel": ["public_api_entrypoint", "public_stable", "fabric_io_entrypoint"],
    "read_warehouse_table": ["public_api_entrypoint", "public_stable", "fabric_io_entrypoint"],
    "read_warehouse_query": ["public_api_entrypoint", "public_stable", "fabric_io_entrypoint"],
    "write_warehouse_table": ["public_api_entrypoint", "public_stable", "fabric_io_entrypoint"],
    "read_lakehouse_table_core": ["internal_workflow", "io_workflow", "lakehouse_read_workflow"],
    "write_lakehouse_table_core": ["internal_workflow", "io_workflow", "lakehouse_write_workflow"],
    "read_lakehouse_csv_core": ["internal_workflow", "io_workflow", "lakehouse_file_read_workflow"],
    "read_lakehouse_parquet_core": ["internal_workflow", "io_workflow", "lakehouse_file_read_workflow"],
    "read_lakehouse_excel_core": ["internal_workflow", "io_workflow", "lakehouse_file_read_workflow"],
    "read_warehouse_table_core": ["internal_workflow", "io_workflow", "warehouse_read_workflow"],
    "read_warehouse_query_core": ["internal_workflow", "io_workflow", "warehouse_read_workflow"],
    "write_warehouse_table_core": ["internal_workflow", "io_workflow", "warehouse_write_workflow"],
    "_resolve_target_store": ["internal_resolver", "store_resolver", "fabric_io_resolver"],
    "_resolve_lakehouse_schema": ["internal_resolver", "lakehouse_schema_resolver", "fabric_io_resolver"],
    "_resolve_lakehouse_table_path": ["internal_resolver", "lakehouse_table_path_resolver", "fabric_io_resolver"],
    "_lakehouse_file_path": ["internal_resolver", "lakehouse_file_path_resolver", "fabric_io_resolver"],
    "_resolve_lakehouse_table_location": ["internal_resolver", "lakehouse_table_path_resolver", "fabric_io_resolver"],
    "_resolve_lakehouse_file_location": ["internal_resolver", "lakehouse_file_path_resolver", "fabric_io_resolver"],
    "_resolve_warehouse_table_location": ["internal_resolver", "warehouse_table_resolver", "fabric_io_resolver"],
    "configured_lakehouse_schema": ["internal_resolver", "lakehouse_schema_resolver", "fabric_io_resolver"],
    "_normalize_table_name": ["internal_validator", "name_validator", "fabric_io_validator"],
    "_normalize_schema_name": ["internal_validator", "name_validator", "fabric_io_validator"],
    "_normalize_write_mode": ["internal_validator", "write_mode_validator", "fabric_io_validator"],
    "_validate_lakehouse_store": ["internal_validator", "store_validator", "fabric_io_validator"],
    "_validate_warehouse_store": ["internal_validator", "store_validator", "fabric_io_validator"],
    "_validate_relative_path": ["internal_validator", "file_path_validator", "fabric_io_validator"],
    "_validate_select_query": ["internal_validator", "sql_query_validator", "fabric_io_validator"],
    "_validate_dataframe_writer": ["internal_validator", "dataframe_validator", "fabric_io_validator"],
    "_require_fabric_connector": ["internal_adapter", "fabric_connector_adapter"],
    "_read_delta_path": ["internal_adapter", "spark_read_adapter"],
    "_read_csv_path": ["internal_adapter", "spark_read_adapter"],
    "_write_delta_path": ["internal_adapter", "spark_write_adapter"],
    "_read_warehouse_synapsesql": ["internal_adapter", "fabric_warehouse_adapter"],
    "_write_warehouse_synapsesql": ["internal_adapter", "fabric_warehouse_adapter"],
    "_read_excel_file": ["internal_adapter", "pandas_excel_adapter"],
    "_convert_single_parquet_ns_to_us": ["internal_adapter", "parquet_timestamp_adapter"],
    "_join_lakehouse_area_path": ["utility_function", "path_join_utility"],
    "_build_warehouse_object_name": ["utility_function", "warehouse_name_formatter"],
    "_resolve_lakehouse_table_identifier": ["utility_function", "lakehouse_table_formatter"],

    # Profiling public entrypoint and role-organized internals.
    "profile_dataframe": ["public_api_entrypoint", "profiling_entrypoint", "public_stable"],
    "profile_dataframe_core": ["internal_workflow", "profiling_workflow"],
    "_get_profiled_columns": ["internal_resolver", "profiling_column_resolver"],
    "_is_min_max_supported_type": ["internal_resolver", "spark_type_resolver"],
    "_numeric_bin_edges": ["internal_adapter", "spark_profiling_adapter"],
    "_build_numeric_distribution": ["internal_adapter", "spark_profiling_adapter"],
    "_build_categorical_distribution": ["internal_adapter", "spark_profiling_adapter"],
    "_build_distribution_summaries": ["internal_adapter", "spark_profiling_adapter"],

    # Guardrail support internals.
    "_check_schema_rule_runtime": ["internal_workflow", "schema_guardrail_workflow"],
    "_check_schema_runtime": ["internal_validator", "schema_expectation_validator"],
    "enforce_freshness_rule": ["internal_workflow", "freshness_guardrail_workflow"],
    "enforce_freshness": ["internal_workflow", "freshness_guardrail_workflow"],
    "enforce_profile_behavior": ["internal_workflow", "profile_behavior_guardrail_workflow"],
    "_select_table_guardrail_rule": ["internal_resolver", "guardrail_rule_resolver"],
    "_select_profile_behavior_rule": ["internal_resolver", "guardrail_rule_resolver"],
    "_accepted_profile_rows": ["internal_resolver", "profile_baseline_resolver"],
    "_actual_schema": ["internal_resolver", "dataframe_schema_resolver"],
    "_max_column_value": ["internal_adapter", "spark_schema_adapter"],
    "_normalize_datatype": ["internal_normalizer", "schema_result_normalizer"],
    "_normalize_profile": ["internal_normalizer", "profile_payload_normalizer"],
    "_profile_payload_from_profile": ["internal_normalizer", "evidence_payload_normalizer"],
    "_guardrail_exclude_columns": ["internal_resolver", "threshold_config_resolver"],
    "_apply_bypass_post_review_warning": ["internal_normalizer", "guardrail_result_normalizer"],
    "_catalogue_value": ["utility_function", "metadata_value_utility"],
    "_string_value": ["utility_function", "status_message_utility"],
    "_is_active_guardrail_rule": ["internal_validator", "guardrail_rule_validator"],
    "_rule_review_status": ["internal_resolver", "guardrail_rule_resolver"],
    "_parse_rule_parameters": ["internal_resolver", "threshold_config_resolver"],
    "_row_to_dict": ["internal_normalizer", "row_payload_normalizer"],
    "_json_dumps_stable": ["utility_function", "payload_formatter"],
    "_profile_hash": ["utility_function", "payload_hash_utility"],
    "_schema_signature": ["internal_normalizer", "schema_result_normalizer"],
    "_profile_row_count": ["internal_resolver", "profile_payload_resolver"],
    "_coerce_date": ["utility_function", "timestamp_utility"],
    "_iso_date_value": ["utility_function", "timestamp_utility"],
    "_is_missing_table_error": ["utility_function", "error_classification_utility"],
}

REACHABILITY_LABELS = {
    "public_entrypoint": "Public entrypoint",
    "directly_reachable": "Reachable from public API",
    "implicit_lifecycle_reachable": "Lifecycle reachable",
    "unknown_or_entrypoint": "Unknown / possible entrypoint",
    "unreachable_candidate": "Possible unused",
}

ROLE_GROUP_LABELS = {
    "public_entrypoint": "Public entrypoint",
    "workflow": "Workflow",
    "resolver": "Resolver",
    "normalizer": "Normalizer",
    "validator": "Validator",
    "adapter": "Adapter",
    "utility": "Utility",
    "model_class": "Model class",
    "registry_builder": "Registry builder",
    "lifecycle_method": "Lifecycle method",
    "property_method": "Property method",
    "other": "Other",
}


def _callable_role_group(tags: list[str]) -> str:
    """Return the broad role group shown in maintainer dashboard filters."""
    if any(tag in {"public_api_entrypoint", "notebook_api_entrypoint"} for tag in tags):
        return "public_entrypoint"
    if "lifecycle_method" in tags:
        return "lifecycle_method"
    if "property_method" in tags:
        return "property_method"
    if any(tag.endswith("_model_class") or tag == "model_class" for tag in tags):
        return "model_class"
    if any("registry" in tag and ("builder" in tag or "catalog" in tag) for tag in tags):
        return "registry_builder"
    if any("workflow" in tag for tag in tags):
        return "workflow"
    if any("resolver" in tag for tag in tags):
        return "resolver"
    if any("normalizer" in tag for tag in tags):
        return "normalizer"
    if any("validator" in tag for tag in tags):
        return "validator"
    if any("adapter" in tag for tag in tags):
        return "adapter"
    if any("utility" in tag or tag.endswith("_probe") or tag == "shared_internal_service" for tag in tags):
        return "utility"
    return "other"


def _label_from_value(value: str) -> str:
    """Return a compact human-readable label for generated dashboard values."""
    return value.replace("_", " ").strip().capitalize() if value else ""

def _callable_role_tags(
    qn: str,
    node: dict[str, Any],
    layer: str,
    review_status: str,
    *,
    is_called_by_lifecycle: bool = False,
) -> list[str]:
    """Return refined role tags for a callable without changing runtime behavior."""
    name = node["callable_name"]
    base_name = name.split(".")[0]
    kind = node.get("callable_kind", "unknown")
    tags: list[str] = []
    if kind == "implicit_lifecycle_method":
        tags.extend(["lifecycle_method", "implicit_lifecycle_reachable", "keep_lifecycle_method"])
    elif kind == "property_accessor":
        tags.append("property_method")
    elif kind == "class":
        if base_name in CONFIG_MODEL_CLASSES:
            tags.append("config_model_class")
            if base_name == "FrameworkConfig":
                tags.append("root_config_model")
            if base_name == "PathConfig":
                tags.append("path_config_model")
        elif base_name in RESULT_MODEL_CLASSES:
            tags.append("result_model_class")
        elif base_name in CONTEXT_MODEL_CLASSES:
            tags.append("context_model_class")
        else:
            tags.append(
                "config_model_class"
                if base_name.endswith("Config")
                else "context_model_class"
                if base_name.endswith("Context")
                else "result_model_class"
                if base_name.endswith("Result")
                else "instance_method"
            )
    elif layer == "public":
        tags.append("public_api_entrypoint")
    tags.extend(ROLE_TAGS_BY_NAME.get(name, []))
    if not tags:
        if name.startswith("_validate"):
            tags.append("internal_validator")
        elif name.startswith("_normalize"):
            tags.append("internal_normalizer")
        elif name.startswith(("_resolve", "resolve_", "_get", "get_default")):
            tags.append("internal_resolver")
        elif layer == "utility":
            tags.append("utility_function")
        elif layer == "internal":
            tags.append("internal_workflow")
        else:
            tags.append("instance_method" if kind == "method" else "utility_function")
    if is_called_by_lifecycle:
        tags.append("implicit_lifecycle_reachable")
    if review_status == "unreachable":
        tags.append("unreachable_candidate")
    return list(dict.fromkeys(tags))


def _primary_dependency_role(tags: list[str]) -> str:
    """Return the primary dependency role used by architecture rules."""
    order = [
        "public_api_entrypoint",
        "notebook_api_entrypoint",
        "internal_workflow",
        "utility_function",
        "utility_validator",
        "internal_validator",
        "internal_normalizer",
        "internal_resolver",
        "internal_adapter",
        "config_model_class",
        "result_model_class",
        "context_model_class",
        "lifecycle_method",
        "schema_utility",
        "audit_time_utility",
        "spark_runtime_probe",
        "fabric_runtime_probe",
        "shared_internal_service",
    ]
    return next((role for role in order if role in tags), tags[0] if tags else "unknown")


def _role_dependency_signals(caller_role: str, callee_role: str) -> list[str]:
    """Return role-based architecture signals for a project-local call edge."""
    if caller_role == "internal_workflow" and callee_role == "internal_workflow":
        return ["internal_workflow_calls_internal_workflow"]
    utility_roles = {
        "utility_function",
        "audit_time_utility",
        "schema_utility",
        "spark_runtime_probe",
        "fabric_runtime_probe",
    }
    if caller_role in utility_roles and callee_role == "internal_workflow":
        return ["utility_calls_workflow"]
    if caller_role in {"utility_validator", "internal_validator"} and callee_role == "internal_workflow":
        return ["validator_calls_workflow"]
    if caller_role == "internal_resolver" and callee_role == "internal_workflow":
        return ["resolver_calls_workflow"]
    if caller_role in {"config_model_class", "result_model_class", "context_model_class"} and callee_role == "internal_workflow":
        return ["model_calls_workflow"]
    allowed_callers = {"public_api_entrypoint", "notebook_api_entrypoint", "internal_workflow", "lifecycle_method"}
    allowed_callees = {
        "internal_workflow",
        "utility_function",
        "utility_validator",
        "internal_validator",
        "internal_normalizer",
        "internal_resolver",
        "internal_adapter",
        "config_model_class",
        "result_model_class",
        "context_model_class",
        "schema_utility",
        "audit_time_utility",
        "spark_runtime_probe",
        "fabric_runtime_probe",
    }
    if caller_role in allowed_callers and callee_role in allowed_callees:
        return ["allowed_internal_role_call"]
    return []

ARCHITECTURE_VIOLATION_ACTION = "Architecture violation"


def _callable_classification(
    qn: str,
    public_qn_set: set[str],
    reachable_non_public: set[str],
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
) -> tuple[str, str]:
    """Return architecture layer and review status for a project callable."""
    node = node_by_qn[qn]
    if node.get("callable_kind") != "function":
        return SUPPORTING_OBJECT_LAYER, "classified"
    if node.get("is_underscore"):
        return HIDDEN_PRIVATE_LAYER, "classified"
    if qn in public_qn_set:
        return "public", "classified"
    layer = "internal"
    if qn not in reachable_non_public:
        review_status = "unreachable" if node.get("is_underscore") else "classification_pending"
        return layer, review_status
    return layer, "classified"


def _architecture_dependency_signals(caller_layer: str, callee_layer: str) -> list[str]:
    """Return callable-layer dependency violation signals for a classified project-local edge."""
    if caller_layer == "public" and callee_layer == "public":
        return ["public_calls_public"]
    if caller_layer == "internal" and callee_layer == "public":
        return ["internal_calls_public"]
    return []


def _dependency_review_signals(callee_review_status: str) -> list[str]:
    """Return review-only signals for edges into pending or unreachable callables."""
    if callee_review_status == "classification_pending":
        return ["callee_classification_pending"]
    if callee_review_status == "unreachable":
        return ["callee_unreachable"]
    return []


def _build_function_inventory(
    public_qns: list[str],
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
    callable_summary: list[dict[str, Any]],
    refactor_inventory: list[dict[str, Any]],
) -> tuple[dict[str, int], list[dict[str, Any]]]:
    """Build a reconciled one-row-per-discovered-callable dashboard inventory."""
    public_qn_set = set(public_qns)
    reachable_non_public = set().union(
        *(_reachable_callables(public_qn, calls_by_qn, node_by_qn) for public_qn in public_qns)
    ) - public_qn_set
    inbound_by_qn = _project_inbound_callers(calls_by_qn, node_by_qn)
    refactor_by_qn = {row["qualified_name"]: row for row in refactor_inventory}
    summary_by_qn = {row["qualified_name"]: row for row in callable_summary}
    classification_by_qn = {
        qn: _callable_classification(qn, public_qn_set, reachable_non_public, calls_by_qn, node_by_qn)
        for qn in node_by_qn
    }
    for qn, callers in inbound_by_qn.items():
        if classification_by_qn[qn][1] == "unreachable" and any(
            node_by_qn[caller].get("callable_kind") == "implicit_lifecycle_method" for caller in callers
        ):
            classification_by_qn[qn] = (classification_by_qn[qn][0], "classified")
    layer_by_qn = {qn: classification[0] for qn, classification in classification_by_qn.items()}
    review_status_by_qn = {qn: classification[1] for qn, classification in classification_by_qn.items()}

    def is_visible_architecture_function(qn: str) -> bool:
        return layer_by_qn.get(qn) in {"public", "internal"}

    def is_inventory_function(qn: str) -> bool:
        return layer_by_qn.get(qn) in {"public", "internal", HIDDEN_PRIVATE_LAYER}

    def inventory_function_type(layer: str) -> str:
        if layer == HIDDEN_PRIVATE_LAYER:
            return PRIVATE_HELPER_LABEL
        return CALLABLE_LAYER_LABELS[layer]

    def private_helper_usage_scope(qn: str, inbound: set[str]) -> str:
        if not inbound:
            return "unused"
        helper_module = node_by_qn[qn]["module_name"]
        inbound_modules = {node_by_qn[caller]["module_name"] for caller in inbound if caller in node_by_qn}
        return "same_module" if inbound_modules <= {helper_module} else "cross_module"

    def private_helper_owner(qn: str, inbound: set[str]) -> str:
        visible_callers = [caller for caller in inbound if is_visible_architecture_function(caller)]
        candidates = visible_callers or [caller for caller in inbound if caller in node_by_qn]
        if not candidates:
            return ""
        return sorted(candidates, key=lambda item: (node_by_qn[item]["module_name"], node_by_qn[item]["callable_name"].lower()))[0]

    def private_helper_action(qn: str, inbound: set[str], outbound: list[str]) -> tuple[str, str]:
        scope = private_helper_usage_scope(qn, inbound)
        if node_by_qn[qn]["module_name"] == "_profiling_adapters":
            return "Keep private helper", "Review"
        if scope == "cross_module":
            return "Rename to internal function", "Medium"
        if not inbound:
            return "Remove redundant wrapper", "Medium"
        if len(inbound) == 1 and len(set(outbound)) <= 1:
            return "Merge into owner", "Medium"
        if len(inbound) == 1 and node_by_qn[qn]["module_name"] not in {node_by_qn[caller]["module_name"] for caller in inbound}:
            return "Move closer to owner", "Medium"
        return "Keep private helper", "Review"

    lifecycle_called_qns = {
        qn
        for qn, callers in inbound_by_qn.items()
        if any(node_by_qn[caller].get("callable_kind") == "implicit_lifecycle_method" for caller in callers)
    }
    role_tags_by_qn = {
        qn: _callable_role_tags(
            qn,
            node_by_qn[qn],
            layer_by_qn[qn],
            review_status_by_qn[qn],
            is_called_by_lifecycle=qn in lifecycle_called_qns,
        )
        for qn in node_by_qn
    }
    dependency_role_by_qn = {qn: _primary_dependency_role(tags) for qn, tags in role_tags_by_qn.items()}

    def linked(qns: list[str] | set[str]) -> list[dict[str, str]]:
        return [
            {
                "function": node_by_qn[qn]["callable_name"],
                "module": node_by_qn[qn]["module_name"],
                "qualified_name": qn,
                "source_url": _callable_flow_source_link(qn, module_data),
                **(
                    {
                        "docs_path": f"docs/api/reference/{node_by_qn[qn]['callable_name']}.md",
                        "docs_url": _public_callable_docs_url(node_by_qn[qn]["callable_name"]),
                    }
                    if qn in public_qn_set
                    else {}
                ),
                "layer": layer_by_qn.get(qn, "internal"),
                "review_status": review_status_by_qn.get(qn, "classification_pending"),
                "callable_kind": node_by_qn[qn].get("callable_kind", "unknown"),
                "callable_role": role_tags_by_qn.get(qn, []),
                "dependency_role": dependency_role_by_qn.get(qn, "unknown"),
            }
            for qn in sorted(qns, key=lambda item: (node_by_qn[item]["module_name"], node_by_qn[item]["callable_name"].lower()))
            if qn in node_by_qn and is_inventory_function(qn)
        ]

    inventory: list[dict[str, Any]] = []
    for qn in sorted(node_by_qn, key=lambda item: (node_by_qn[item]["module_name"], node_by_qn[item]["callable_name"].lower(), item)):
        if not is_inventory_function(qn):
            continue
        node = node_by_qn[qn]
        layer = layer_by_qn[qn]
        function_type = inventory_function_type(layer)
        refactor = refactor_by_qn.get(qn, {})
        public_summary = summary_by_qn.get(qn, {})
        outbound = [callee for callee in calls_by_qn.get(qn, []) if callee in node_by_qn]
        inbound = inbound_by_qn.get(qn, set())
        direct_helper_qns = {item["qualified_name"] for item in public_summary.get("direct_internal_helpers", [])}
        review_status = review_status_by_qn[qn]
        callable_kind = node.get("callable_kind", "unknown")
        architecture_signals = sorted({
            signal
            for callee in outbound
            if is_visible_architecture_function(qn)
            and is_visible_architecture_function(callee)
            and review_status_by_qn.get(callee, "classification_pending") == "classified"
            for signal in _architecture_dependency_signals(layer, layer_by_qn.get(callee, "internal"))
        })
        allowed_role_signals = sorted({
            signal
            for callee in outbound
            if review_status_by_qn.get(callee, "classification_pending") == "classified"
            for signal in _role_dependency_signals(
                dependency_role_by_qn[qn],
                dependency_role_by_qn.get(callee, "internal_workflow"),
            )
            if signal == "allowed_internal_role_call"
        })
        review_signals = sorted({
            signal
            for callee in outbound
            for signal in _dependency_review_signals(review_status_by_qn.get(callee, "classification_pending"))
        })
        used_by_count = len(inbound)
        calls_count = len(set(outbound))
        layer_consistency = _classify_layer_consistency(
            architecture_layer=function_type,
            callable_kind=callable_kind,
            used_by_count=used_by_count,
            calls_count=calls_count,
            has_architecture_violation=bool(architecture_signals),
        )
        consistency_signal = LAYER_CONSISTENCY_SIGNALS.get(layer_consistency)
        utility_dependency_signal = None
        callable_role_detail = role_tags_by_qn[qn]
        callable_role_group = _callable_role_group(callable_role_detail)
        reachability_kind = (
            "public_entrypoint"
            if qn in public_qn_set
            else "implicit_lifecycle_reachable"
            if review_status == "implicit_lifecycle" or qn in lifecycle_called_qns
            else "unreachable_candidate"
            if review_status == "unreachable"
            else "directly_reachable"
            if used_by_count
            else "unknown_or_entrypoint"
        )
        signals = [
            *architecture_signals,
            *allowed_role_signals,
            *(
                ["implicit_lifecycle_reachability"]
                if "implicit_lifecycle_reachable" in role_tags_by_qn[qn]
                else []
            ),
            *review_signals,
            *refactor.get("signals", []),
            *([consistency_signal] if consistency_signal else []),
            *([utility_dependency_signal] if utility_dependency_signal else []),
        ]
        if architecture_signals:
            recommended_action = ARCHITECTURE_VIOLATION_ACTION
            priority = "High"
        elif review_status == "unreachable":
            recommended_action = "Orphaned callable"
            priority = "Medium"
        elif review_status == "classification_pending":
            recommended_action = "Review manually"
            priority = "Review"
        elif review_status == "implicit_lifecycle":
            recommended_action = "Keep lifecycle method"
            priority = "Review"
        elif review_status == "property_accessor":
            recommended_action = "Keep property accessor"
            priority = "Review"
        elif layer == "public":
            recommended_action = "Public API entrypoint"
            priority = refactor.get("priority", "Review")
        elif layer == "internal":
            recommended_action = "Shared internal helper" if len(inbound) > 1 else refactor.get("recommended_action", "Review manually")
            priority = refactor.get("priority", "Review")
        elif layer == HIDDEN_PRIVATE_LAYER:
            recommended_action, priority = private_helper_action(qn, inbound, outbound)
        owner_qn = private_helper_owner(qn, inbound) if layer == HIDDEN_PRIVATE_LAYER else ""
        usage_scope = private_helper_usage_scope(qn, inbound) if layer == HIDDEN_PRIVATE_LAYER else ""
        inventory.append(
            {
                "function_name": node["callable_name"],
                "qualified_name": qn,
                "module": node["module_name"],
                "function_type": function_type,
                "layer": layer,
                "review_status": review_status,
                "review_status_label": REVIEW_STATUS_LABELS[review_status],
                "callable_kind": callable_kind,
                "visibility": "public" if qn in public_qn_set else "private" if node.get("is_underscore") else "internal",
                "callable_role": callable_role_detail,
                "callable_role_group": callable_role_group,
                "callable_role_group_label": ROLE_GROUP_LABELS[callable_role_group],
                "callable_role_detail": callable_role_detail,
                "callable_role_detail_label": ", ".join(_label_from_value(role) for role in callable_role_detail),
                "architectural_role": dependency_role_by_qn[qn],
                "dependency_role": dependency_role_by_qn[qn],
                "owner_qualified_name": owner_qn,
                "owner_function": node_by_qn[owner_qn]["callable_name"] if owner_qn else "",
                "owner_module": node_by_qn[owner_qn]["module_name"] if owner_qn else "",
                "owner_file": _callable_flow_source_path(owner_qn) if owner_qn else _callable_flow_source_path(qn),
                "leaks_outside_owner_file": bool(layer == HIDDEN_PRIVATE_LAYER and usage_scope == "cross_module"),
                "usage_scope": usage_scope,
                "usage_scope_label": _label_from_value(usage_scope) if usage_scope else "",
                "reachability_kind": reachability_kind,
                "reachability_label": REACHABILITY_LABELS[reachability_kind],
                "change_risk": priority,
                "refined_recommended_action": recommended_action,
                "recommended_action": recommended_action,
                "priority": priority,
                "signals": signals,
                "architecture_signals": architecture_signals,
                "review_signals": review_signals,
                "used_by_count": used_by_count,
                "called_by_count": used_by_count,
                "calls_count": calls_count,
                "layer_consistency": layer_consistency,
                "layer_consistency_label": LAYER_CONSISTENCY_LABELS[layer_consistency],
                "callers": linked(inbound),
                "callees": linked(set(outbound)),
                "direct_internal_helpers": linked(direct_helper_qns),
                "source_path": _callable_flow_source_path(qn),
                "source_url": _callable_flow_source_link(qn, module_data),
                **_callable_flow_source_location(qn, module_data),
                **(
                    {
                        "docs_path": f"docs/api/reference/{node['callable_name']}.md",
                        "docs_url": _public_callable_docs_url(node["callable_name"]),
                    }
                    if qn in public_qn_set
                    else {}
                ),
                "deepest_call_chain_depth": public_summary.get("deepest_call_chain_depth") or refactor.get("nesting_level"),
                "repeated_helper_count": public_summary.get("repeated_helper_count", 0),
            }
        )
    summary_counts = {
        "total_callables": len(inventory),
        "total_functions": sum(1 for row in inventory if row["layer"] in CALLABLE_LAYER_LABELS),
        "private_helper_review": sum(1 for row in inventory if row["layer"] == HIDDEN_PRIVATE_LAYER),
        "function_type": {
            label: sum(1 for row in inventory if row["function_type"] == label)
            for label in CALLABLE_LAYER_LABELS.values()
        },
        "layer": {
            layer: sum(1 for row in inventory if row["layer"] == layer)
            for layer in CALLABLE_LAYER_LABELS
        },
        "hidden_private_helpers": sum(1 for qn, layer in layer_by_qn.items() if layer == HIDDEN_PRIVATE_LAYER),
        "supporting_objects": sum(1 for qn, layer in layer_by_qn.items() if layer == SUPPORTING_OBJECT_LAYER),
        "review_status": {
            status: sum(1 for row in inventory if row["review_status"] == status)
            for status in REVIEW_STATUS_LABELS
        },
        "callable_kind": {
            label: sum(1 for row in inventory if row["callable_kind"] == label and row["layer"] in CALLABLE_LAYER_LABELS)
            for label in sorted({row["callable_kind"] for row in inventory if row["layer"] in CALLABLE_LAYER_LABELS})
        },
        "callable_role_group": {
            label: sum(1 for row in inventory if row["callable_role_group"] == label)
            for label in sorted({row["callable_role_group"] for row in inventory})
        },
        "callable_role_detail": {
            label: sum(1 for row in inventory if label in row["callable_role_detail"])
            for label in sorted({role for row in inventory for role in row["callable_role_detail"]})
        },
        "callable_role": {
            label: sum(1 for row in inventory if label in row["callable_role"])
            for label in sorted({role for row in inventory for role in row["callable_role"]})
        },
        "dependency_role": {
            label: sum(1 for row in inventory if row["dependency_role"] == label)
            for label in sorted({row["dependency_role"] for row in inventory})
        },
        "recommended_action": {
            label: sum(1 for row in inventory if row["recommended_action"] == label)
            for label in sorted({row["recommended_action"] for row in inventory})
        },
        "layer_consistency": {
            label: sum(1 for row in inventory if row["layer_consistency"] == label)
            for label in LAYER_CONSISTENCY_LABELS
        },
    }
    return summary_counts, inventory


def _build_callable_inventory_metrics(
    summary_counts: dict[str, Any], inventory: list[dict[str, Any]]
) -> dict[str, int]:
    """Return canonical callable inventory summary metrics for generated pages."""
    public_api_counts = summary_counts.get("public_api_surface", {})
    total_callables = int(summary_counts.get("total_callables", len(inventory)))
    visible_function_callables = sum(1 for row in inventory if row.get("layer") in CALLABLE_LAYER_LABELS)
    private_helper_review = sum(1 for row in inventory if row.get("layer") == HIDDEN_PRIVATE_LAYER)
    public_api_entrypoints = int(public_api_counts.get("public_api_entrypoints", 0))
    return {
        "module_count": len({row.get("module") for row in inventory if row.get("module")}),
        "total_callables": total_callables,
        "public_api_entrypoints": public_api_entrypoints,
        "function_callables": visible_function_callables,
        "supporting_functions": max(visible_function_callables - public_api_entrypoints, 0),
        "non_function_records": int(summary_counts.get("supporting_objects", 0)),
        "hidden_private_helpers": int(summary_counts.get("hidden_private_helpers", 0)),
        "private_helpers_to_review": private_helper_review,
    }


def _callable_inventory_metrics(callable_flow_data: dict[str, Any]) -> dict[str, int]:
    """Read canonical callable inventory summary metrics from callable flow data."""
    summary_counts = callable_flow_data.get("summary_counts", {})
    metrics = summary_counts.get("callable_inventory_metrics")
    if isinstance(metrics, dict):
        return {
            "module_count": int(metrics.get("module_count", 0)),
            "total_callables": int(metrics.get("total_callables", 0)),
            "public_api_entrypoints": int(metrics.get("public_api_entrypoints", 0)),
            "function_callables": int(metrics.get("function_callables", 0)),
            "supporting_functions": int(metrics.get("supporting_functions", 0)),
            "non_function_records": int(metrics.get("non_function_records", 0)),
            "hidden_private_helpers": int(metrics.get("hidden_private_helpers", 0)),
        }
    return _build_callable_inventory_metrics(summary_counts, callable_flow_data.get("function_inventory", []))


LONG_CALL_CHAIN_DEPTH_THRESHOLD = 4
LARGE_DEPENDENCY_SURFACE_THRESHOLD = 10

DECISION_RECOMMENDATIONS = {
    "keep_public": "Keep public",
    "flatten": "Keep public but simplify internals",
    "architecture_violation": "Review architecture violation",
    "merge": "Review merge candidates",
    "move_closer": "Move helper closer to caller",
}

ARCHITECTURE_VIOLATION_MEANINGS = {
    "Public -> Public": "Public function is calling another public notebook-facing API.",
    "Internal -> Public": "Internal function is calling a notebook-facing public API.",
}

DISPLAY_LABEL_MAP = {
    "Cross-layer dependency": "Architecture violation",
    "Cross-layer issue": "Architecture violation",
    "Deep chain": "Long call chain",
    "Single-use helper candidate": "Merge candidate",
    "Architecture violation": "Architecture violation",
    "Architecture violation type": "Architecture violation",
    "Cross-layer call": "Architecture violation",
    "Long call chain": "Long call chain",
    "Large dependency surface": "Large dependency surface",
    "Merge candidate": "Merge candidate",
    "Review abstraction": "Review abstraction",
    "cross_layer_dependency": "Architecture violation",
    "deep_chain": "Long call chain",
    "large_downstream_surface": "Large dependency surface",
    "single_use_helper_candidate": "Merge candidate",
    "inline_candidate": "Merge candidate",
    "review_abstraction_value": "Review abstraction",
}


def _display_label(value: str) -> str:
    """Return the current user-facing label for a legacy finding label."""
    return DISPLAY_LABEL_MAP.get(value, value)


def _decision_layer_group(row: dict[str, Any]) -> str:
    """Return the human-facing layer group from available inventory fields."""
    function_type = row.get("function_type") or row.get("layer")
    if function_type in {"Public function", "Internal function"}:
        return function_type
    if function_type == PRIVATE_HELPER_LABEL:
        return PRIVATE_HELPER_LABEL
    if function_type == "Supporting object":
        return "Supporting object"
    if function_type == "Public API":
        return "Public function"
    if function_type in {"Internal helper", "Utility"}:
        return "Internal function"
    layer = row.get("layer")
    if layer in CALLABLE_LAYER_LABELS:
        return CALLABLE_LAYER_LABELS[layer]
    if row.get("callable_kind") != "function" or row.get("layer") == HIDDEN_PRIVATE_LAYER:
        return "Supporting object"
    if row.get("dependency_role") == "public_api":
        return "Public function"
    return "Internal function"




def _architecture_layer(row: dict[str, Any]) -> str:
    """Return the two-layer function architecture label for a flow row."""
    if row.get("callable_kind") != "function" or row.get("layer") == HIDDEN_PRIVATE_LAYER:
        return "Supporting object"
    group = _decision_layer_group(row)
    if group == "Public function":
        return "Public"
    return "Internal"


def _classify_architecture_edge(caller_type: str, callee_type: str) -> dict[str, str]:
    """Classify a caller/callee layer pair as allowed, review, or violation."""
    direction = f"{caller_type} -> {callee_type}"
    if "Supporting object" in {caller_type, callee_type}:
        return {"result": "Allowed", "violation_type": ""}
    if direction in ARCHITECTURE_VIOLATION_MEANINGS or direction == "Public -> Public":
        return {"result": "Violation", "violation_type": direction}
    return {"result": "Allowed", "violation_type": ""}


def _architecture_violation_summary(edges: list[dict[str, Any]]) -> dict[str, int]:
    """Return counts by architecture violation direction."""
    return {
        key: sum(1 for edge in edges if edge.get("architecture_result") == "Violation" and edge.get("violation_type") == key)
        for key in ARCHITECTURE_VIOLATION_MEANINGS
    }

def _decision_warnings(flow: dict[str, Any], callee_rows: list[dict[str, Any]]) -> list[str]:
    """Return architecture decision warnings for a public entrypoint flow."""
    warnings: set[str] = set()
    if flow["maximum_chain_depth"] >= LONG_CALL_CHAIN_DEPTH_THRESHOLD:
        warnings.add("Long call chain")
    if flow["downstream_callable_count"] >= LARGE_DEPENDENCY_SURFACE_THRESHOLD:
        warnings.add("Large dependency surface")
    if flow["modules_touched_count"] > 4:
        warnings.add("Spans many modules")
    if flow["cross_layer_issue_count"]:
        warnings.add("Architecture violation")
    if any("internal_workflow_chain" in row["signals"] for row in callee_rows):
        warnings.add("Cross-module internal chain")
    if flow["single_use_helper_candidate_count"]:
        warnings.add("Merge candidates found")
    return sorted(warnings)


def _decision_action(flow: dict[str, Any], callee_rows: list[dict[str, Any]]) -> str:
    """Return a public-entrypoint simplification recommendation."""
    if flow["architecture_violation_count"]:
        return DECISION_RECOMMENDATIONS["architecture_violation"]
    if flow["single_use_helper_candidate_count"] and flow["downstream_callable_count"] <= 3:
        return DECISION_RECOMMENDATIONS["merge"]
    if flow["single_use_helper_candidate_count"]:
        return DECISION_RECOMMENDATIONS["move_closer"]
    if flow["maximum_chain_depth"] >= LONG_CALL_CHAIN_DEPTH_THRESHOLD or flow["downstream_callable_count"] >= LARGE_DEPENDENCY_SURFACE_THRESHOLD or flow["modules_touched_count"] > 4:
        return DECISION_RECOMMENDATIONS["flatten"]
    return DECISION_RECOMMENDATIONS["keep_public"]


def _path_examples(
    root_qn: str,
    target_qn: str,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
    limit: int = 3,
) -> list[list[str]]:
    """Return up to ``limit`` readable root-to-target callable path examples."""
    examples: list[list[str]] = []

    def visit(qn: str, path: list[str]) -> None:
        if len(examples) >= limit or len(path) > 12:
            return
        if qn == target_qn:
            examples.append([node_by_qn[item]["callable_name"] for item in path])
            return
        for child in sorted(set(calls_by_qn.get(qn, [])) & set(node_by_qn)):
            if child in path:
                continue
            visit(child, [*path, child])

    visit(root_qn, [root_qn])
    return examples[:limit]


def _build_public_entrypoint_flow(
    public_qns: list[str],
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
    function_inventory: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build flat public-entrypoint flow records for the decision dashboard."""
    row_by_qn = {row["qualified_name"]: row for row in function_inventory}
    flow_visible_qns = {qn for qn, row in row_by_qn.items() if row.get("layer") in CALLABLE_LAYER_LABELS}
    flows: list[dict[str, Any]] = []
    for public_qn in public_qns:
        seen_depth: dict[str, int] = {}
        parent_by_qn: dict[str, str] = {}
        visited_hidden: set[tuple[str, str]] = set()
        queue: list[tuple[str, int, str]] = [
            (callee, 1, public_qn)
            for callee in sorted(set(calls_by_qn.get(public_qn, [])) & set(node_by_qn))
        ]
        while queue:
            qn, depth, parent = queue.pop(0)
            if qn not in row_by_qn or qn not in flow_visible_qns:
                hidden_key = (qn, parent)
                if hidden_key in visited_hidden:
                    continue
                visited_hidden.add(hidden_key)
                for child in sorted(set(calls_by_qn.get(qn, [])) & set(node_by_qn)):
                    if child == public_qn:
                        continue
                    queue.append((child, depth, parent))
                continue
            if qn in seen_depth and seen_depth[qn] <= depth:
                continue
            seen_depth[qn] = depth
            parent_by_qn[qn] = parent
            for child in sorted(set(calls_by_qn.get(qn, [])) & set(node_by_qn)):
                if child == public_qn:
                    continue
                queue.append((child, depth + 1, qn))

        def callee_row(qn: str, edge_type: str) -> dict[str, Any]:
            row = row_by_qn[qn]
            parent_row = row_by_qn.get(parent_by_qn.get(qn, public_qn), row_by_qn[public_qn])
            signals = list(row.get("signals", []))
            if row.get("dependency_role") == "internal_workflow" and row_by_qn.get(parent_by_qn.get(qn, ""), {}).get("dependency_role") == "internal_workflow":
                signals = sorted({*signals, "internal_workflow_chain"})
            caller_type = _architecture_layer(parent_row)
            callee_type = _architecture_layer(row)
            edge_classification = _classify_architecture_edge(caller_type, callee_type)
            return {
                "callable": row["function_name"],
                "qualified_name": qn,
                "module": row["module"],
                "depth": seen_depth[qn],
                "layer": row.get("layer"),
                "function_type": row.get("function_type"),
                "layer_group": _decision_layer_group(row),
                "callable_role": row.get("callable_role", []),
                "dependency_role": row.get("dependency_role"),
                "edge_type": edge_type,
                "parent_qualified_name": parent_by_qn.get(qn, public_qn),
                "caller_type": caller_type,
                "callee_type": callee_type,
                "architecture_result": edge_classification["result"],
                "violation_type": edge_classification["violation_type"],
                "signals": signals,
                "architecture_signals": row.get("architecture_signals", []),
                "recommended_action": row.get("recommended_action"),
                "downstream_count": row.get("calls_count", 0),
                "source_path": _callable_flow_source_path(qn),
                "source_url": _callable_flow_source_link(qn, module_data),
                **_callable_flow_source_location(qn, module_data),
                **({"docs_path": row["docs_path"], "docs_url": row["docs_url"]} if row.get("docs_url") else {}),
                "path_examples": _path_examples(public_qn, qn, calls_by_qn, node_by_qn),
                "helper_cleanup_candidate": _decision_layer_group(row) == "Internal function"
                and row_by_qn[qn].get("used_by_count", 0) <= 1,
            }

        direct_qns = sorted(
            (qn for qn, depth in seen_depth.items() if depth == 1),
            key=lambda qn: (node_by_qn[qn]["module_name"], node_by_qn[qn]["callable_name"].lower(), qn),
        )
        transitive_qns = sorted(
            seen_depth,
            key=lambda qn: (seen_depth[qn], node_by_qn[qn]["module_name"], node_by_qn[qn]["callable_name"].lower(), qn),
        )
        callee_rows = [callee_row(qn, "transitive" if seen_depth[qn] > 1 else "direct") for qn in transitive_qns]
        modules_touched = sorted({node_by_qn[public_qn]["module_name"], *(node_by_qn[qn]["module_name"] for qn in seen_depth)})
        flow = {
            "public_callable": node_by_qn[public_qn]["callable_name"],
            "qualified_name": public_qn,
            "module": node_by_qn[public_qn]["module_name"],
            "docs_path": f"docs/api/reference/{node_by_qn[public_qn]['callable_name']}.md",
            "docs_url": _public_callable_docs_url(node_by_qn[public_qn]["callable_name"]),
            "source_path": _callable_flow_source_path(public_qn),
            "owner_file": _callable_flow_source_path(public_qn),
            "source_url": _callable_flow_source_link(public_qn, module_data),
            **_callable_flow_source_location(public_qn, module_data),
            "downstream_callable_count": len(seen_depth),
            "maximum_chain_depth": max(seen_depth.values(), default=0),
            "modules_touched_count": len(modules_touched),
            "modules_touched": modules_touched,
            "architecture_violation_count": sum(1 for row in callee_rows if row.get("architecture_result") == "Violation"),
            "architecture_violation_breakdown": _architecture_violation_summary(callee_rows),
            "cross_layer_issue_count": sum(1 for row in callee_rows if row.get("architecture_result") == "Violation"),
            "single_use_helper_candidate_count": sum(
                1
                for row in callee_rows
                if row["layer_group"] != "Public function"
                and row_by_qn[row["qualified_name"]].get("used_by_count", 0) <= 1
            ),
            "recommended_simplification_action": "",
            "warnings": [],
            "direct_callees": [callee_row(qn, "direct") for qn in direct_qns],
            "transitive_callees": callee_rows,
            "private_helper_review_items": [
                row
                for row in function_inventory
                if row.get("layer") == HIDDEN_PRIVATE_LAYER and row.get("owner_qualified_name") == public_qn
            ],
        }
        flow["recommended_simplification_action"] = _decision_action(flow, callee_rows)
        flow["warnings"] = _decision_warnings(flow, callee_rows)
        flows.append(flow)
    return flows



CALLABLE_FLOW_TOP_LEVEL_KEYS = (
    "metadata",
    "architecture_thresholds",
    "function_inventory",
    "public_entrypoint_flow",
    "summary_counts",
)

CALLABLE_FLOW_SUMMARY_KEYS = (
    "total_callables",
    "function_type",
    "layer",
    "review_status",
    "callable_kind",
    "callable_role_group",
    "dependency_role",
    "recommended_action",
    "public_api_surface",
    "callable_inventory_metrics",
    "private_helper_review",
)

FUNCTION_INVENTORY_DASHBOARD_KEYS = (
    "qualified_name",
    "function_name",
    "module",
    "source_path",
    "owner_file",
    "source_url",
    "source_start_line",
    "source_end_line",
    "function_type",
    "layer",
    "review_status",
    "review_status_label",
    "callable_kind",
    "callable_role",
    "callable_role_group",
    "callable_role_group_label",
    "callable_role_detail",
    "callable_role_detail_label",
    "dependency_role",
    "owner_qualified_name",
    "owner_function",
    "owner_module",
    "leaks_outside_owner_file",
    "usage_scope",
    "usage_scope_label",
    "reachability_kind",
    "reachability_label",
    "recommended_action",
    "priority",
    "signals",
    "architecture_signals",
    "review_signals",
    "called_by_count",
    "calls_count",
    "callers",
    "callees",
    "docs_path",
    "docs_url",
)

PUBLIC_ENTRYPOINT_FLOW_DASHBOARD_KEYS = (
    "qualified_name",
    "function_name",
    "module",
    "docs_path",
    "docs_url",
    "source_path",
    "owner_file",
    "source_url",
    "source_start_line",
    "source_end_line",
    "priority",
    "recommended_simplification_action",
    "warnings",
    "downstream_count",
    "max_depth",
    "modules_touched",
    "architecture_violation_count",
    "architecture_violation_breakdown",
    "helper_cleanup_candidates",
    "direct_callees",
    "transitive_callees",
    "private_helper_review_items",
)

PUBLIC_FLOW_CALLEE_DASHBOARD_KEYS = (
    "qualified_name",
    "function_name",
    "module",
    "depth",
    "function_type",
    "layer",
    "layer_group",
    "dependency_role",
    "edge_type",
    "parent_qualified_name",
    "caller_type",
    "callee_type",
    "architecture_result",
    "violation_type",
    "signals",
    "recommended_action",
    "downstream_count",
    "source_path",
    "source_url",
    "source_start_line",
    "source_end_line",
    "docs_path",
    "docs_url",
    "path_examples",
    "helper_cleanup_candidate",
)


def _callable_flow_source_context() -> dict[str, str]:
    """Return safe Git source context for generated callable-flow assets."""
    context: dict[str, str] = {}
    commands = (
        ("commit", ["git", "rev-parse", "--short", "HEAD"]),
        ("branch", ["git", "branch", "--show-current"]),
    )
    for key, command in commands:
        try:
            value = subprocess.check_output(
                command,
                cwd=ROOT,
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            continue
        if value:
            context[key] = value
    return context


def _callable_flow_metadata(generated_at_utc: datetime) -> dict[str, Any]:
    """Return generation metadata shared by callable-flow JSON and HTML assets."""
    metadata: dict[str, Any] = {
        "generated_at_utc": generated_at_utc.isoformat().replace("+00:00", "Z"),
        "data_source": "callable-flow.json",
    }
    metadata.update(_callable_flow_source_context())
    return metadata


def _format_generated_at_utc(value: str | None) -> str:
    """Return the visible UTC timestamp label for callable dashboard metadata."""
    if not value:
        return "Unknown"
    normalized = value.replace("Z", "+00:00")
    try:
        generated_at = datetime.fromisoformat(normalized).astimezone(UTC)
    except ValueError:
        return value
    return generated_at.strftime("%Y-%m-%d %H:%M UTC")


def _render_callable_generation_banner(flow_data: dict[str, Any]) -> str:
    """Render shared generation metadata for callable dashboard HTML pages."""
    metadata = flow_data.get("metadata", {})
    parts = [
        f"<strong>Generated at:</strong> {html.escape(_format_generated_at_utc(metadata.get('generated_at_utc')))}",
        f"<span><strong>Data source:</strong> {html.escape(metadata.get('data_source', 'callable-flow.json'))}</span>",
    ]
    if metadata.get("branch"):
        parts.append(f"<span><strong>Branch:</strong> {html.escape(metadata['branch'])}</span>")
    if metadata.get("commit"):
        parts.append(f"<span><strong>Commit:</strong> {html.escape(metadata['commit'])}</span>")
    return f'<p class="generation-banner">{"".join(parts)}</p>'

def _dashboard_contract_row(row: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    """Return ``row`` trimmed to the public dashboard data contract."""
    return {key: row[key] for key in keys if key in row}


def _trim_callable_flow_dashboard_contract(callable_flow_data: dict[str, Any]) -> dict[str, Any]:
    """Return compact callable-flow JSON consumed by generated dashboards."""
    summary_counts = callable_flow_data["summary_counts"]
    public_surface = dict(summary_counts.get("public_api_surface", {}))
    public_surface.pop("deep_chains", None)
    public_surface.pop("cross_layer_issues", None)
    public_surface.pop("single_use_helper_candidates", None)
    trimmed_summary = {
        key: summary_counts[key]
        for key in CALLABLE_FLOW_SUMMARY_KEYS
        if key in summary_counts
    }
    trimmed_summary["public_api_surface"] = public_surface

    inventory = [
        _dashboard_contract_row(row, FUNCTION_INVENTORY_DASHBOARD_KEYS)
        for row in callable_flow_data["function_inventory"]
    ]

    public_flows = []
    for flow in callable_flow_data["public_entrypoint_flow"]:
        trimmed_flow = dict(flow)
        trimmed_flow["function_name"] = flow.get("function_name", flow.get("public_callable"))
        trimmed_flow["downstream_count"] = flow.get("downstream_count", flow.get("downstream_callable_count", 0))
        trimmed_flow["max_depth"] = flow.get("max_depth", flow.get("maximum_chain_depth", 0))
        trimmed_flow["priority"] = "High" if flow.get("architecture_violation_count") else "Review" if flow.get("warnings") else "Low"
        trimmed_flow["helper_cleanup_candidates"] = flow.get("helper_cleanup_candidates", flow.get("single_use_helper_candidate_count", 0))
        trimmed_flow["private_helper_review_items"] = [
            _dashboard_contract_row(item, FUNCTION_INVENTORY_DASHBOARD_KEYS)
            for item in flow.get("private_helper_review_items", [])
        ]
        trimmed_flow["direct_callees"] = [
            _dashboard_contract_row({**callee, "function_name": callee.get("function_name", callee.get("callable"))}, PUBLIC_FLOW_CALLEE_DASHBOARD_KEYS)
            for callee in flow.get("direct_callees", [])
        ]
        trimmed_flow["transitive_callees"] = [
            _dashboard_contract_row({**callee, "function_name": callee.get("function_name", callee.get("callable"))}, PUBLIC_FLOW_CALLEE_DASHBOARD_KEYS)
            for callee in flow.get("transitive_callees", [])
        ]
        public_flows.append(_dashboard_contract_row(trimmed_flow, PUBLIC_ENTRYPOINT_FLOW_DASHBOARD_KEYS))

    compact = {
        "metadata": callable_flow_data["metadata"],
        "architecture_thresholds": callable_flow_data["architecture_thresholds"],
        "function_inventory": inventory,
        "public_entrypoint_flow": public_flows,
        "summary_counts": trimmed_summary,
    }
    return {key: compact[key] for key in CALLABLE_FLOW_TOP_LEVEL_KEYS}

def _build_callable_flow_data(
    public_qns: list[str],
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
    *,
    generated_at_utc: datetime,
) -> dict[str, Any]:
    """Build the global public callable flow map from existing call graph data."""
    public_qn_set = set(public_qns)
    reachable_by_public: dict[str, set[str]] = {}
    helpers_by_public: dict[str, set[str]] = {}
    public_dependencies: dict[str, list[dict[str, str]]] = {}
    helper_users: dict[str, set[str]] = {}
    summary: list[dict[str, Any]] = []

    for public_qn in public_qns:
        public_name = node_by_qn[public_qn]["callable_name"]
        reachable = _reachable_callables(public_qn, calls_by_qn, node_by_qn)
        reachable_by_public[public_qn] = reachable
        helper_qns = set(_callable_flow_internal_helper_qns(public_qn, calls_by_qn, node_by_qn))
        helpers_by_public[public_qn] = helper_qns
        for helper_qn in helper_qns:
            helper_users.setdefault(helper_qn, set()).add(public_qn)
        public_deps = sorted(
            (qn for qn in reachable if qn in public_qn_set and qn != public_qn),
            key=lambda qn: node_by_qn[qn]["callable_name"].lower(),
        )
        public_dependencies[public_name] = [
            {
                "callable": node_by_qn[dep_qn]["callable_name"],
                "qualified_name": dep_qn,
                "module": node_by_qn[dep_qn]["module_name"],
                "docs_path": f"docs/api/reference/{node_by_qn[dep_qn]['callable_name']}.md",
                "docs_url": _public_callable_docs_url(node_by_qn[dep_qn]['callable_name']),
            }
            for dep_qn in public_deps
        ]

    shared_helper_qns = {helper_qn for helper_qn, users in helper_users.items() if len(users) > 1}
    for public_qn in public_qns:
        public_name = node_by_qn[public_qn]["callable_name"]
        direct_helpers = sorted(
            {
                qn
                for qn in calls_by_qn.get(public_qn, [])
                if qn in node_by_qn
                and qn not in INTERNAL_HELPER_EXCLUSIONS.get(public_name, set())
                and _is_internal_helper_qn(qn, node_by_qn)
            },
            key=lambda qn: (node_by_qn[qn]["module_name"], node_by_qn[qn]["callable_name"].lower()),
        )
        refactor_signals = _collect_refactor_signals(
            public_qn,
            calls_by_qn,
            node_by_qn,
            module_data,
            excluded_helpers=INTERNAL_HELPER_EXCLUSIONS.get(public_name, set()),
        )
        summary.append(
            {
                "callable": public_name,
                "qualified_name": public_qn,
                "module": node_by_qn[public_qn]["module_name"],
                "docs_path": f"docs/api/reference/{public_name}.md",
                "docs_url": _public_callable_docs_url(public_name),
                "unique_internal_helper_count": len(helpers_by_public[public_qn]),
                "unique_internal_helpers": [
                    {
                        "helper": node_by_qn[helper_qn]["callable_name"],
                        "qualified_name": helper_qn,
                        "module": node_by_qn[helper_qn]["module_name"],
                        "source_url": _callable_flow_source_link(helper_qn, module_data),
                    }
                    for helper_qn in _callable_flow_internal_helper_qns(public_qn, calls_by_qn, node_by_qn)
                ],
                "direct_internal_helpers": [
                    {
                        "helper": node_by_qn[helper_qn]["callable_name"],
                        "qualified_name": helper_qn,
                        "module": node_by_qn[helper_qn]["module_name"],
                        "source_url": _callable_flow_source_link(helper_qn, module_data),
                    }
                    for helper_qn in direct_helpers
                ],
                "deepest_call_chain_depth": _deepest_call_chain_depth(public_qn, calls_by_qn, node_by_qn),
                "repeated_helper_count": len(refactor_signals["repeated_helpers"]),
                "calls_public_callable": bool(public_dependencies[public_name]),
                "public_callables_called": public_dependencies[public_name],
                "shared_helper_overlap_count": len(helpers_by_public[public_qn] & shared_helper_qns),
            }
        )

    _, refactor_inventory, _ = _build_refactor_inventory(
        public_qns,
        calls_by_qn,
        node_by_qn,
        module_data,
    )

    summary_counts, function_inventory = _build_function_inventory(
        public_qns,
        calls_by_qn,
        node_by_qn,
        module_data,
        summary,
        refactor_inventory,
    )
    public_entrypoint_flow = _build_public_entrypoint_flow(
        public_qns,
        calls_by_qn,
        node_by_qn,
        module_data,
        function_inventory,
    )
    summary_counts["public_api_surface"] = {
        "public_api_entrypoints": len(public_entrypoint_flow),
        "long_call_chains": sum(1 for flow in public_entrypoint_flow if "Long call chain" in flow["warnings"]),
        "deep_chains": sum(1 for flow in public_entrypoint_flow if "Long call chain" in flow["warnings"]),
        "architecture_violations": sum(1 for flow in public_entrypoint_flow if flow["architecture_violation_count"]),
        "architecture_findings": sum(1 for flow in public_entrypoint_flow if flow["architecture_violation_count"]),
        "cross_layer_issues": sum(1 for flow in public_entrypoint_flow if flow["architecture_violation_count"]),
        "merge_candidates": sum(1 for flow in public_entrypoint_flow if flow["single_use_helper_candidate_count"]),
        "single_use_helper_candidates": sum(1 for flow in public_entrypoint_flow if flow["single_use_helper_candidate_count"]),
        "suggested_inline_or_privatize": sum(
            1
            for flow in public_entrypoint_flow
            if flow["recommended_simplification_action"]
            in {DECISION_RECOMMENDATIONS["merge"], DECISION_RECOMMENDATIONS["move_closer"]}
        ),
    }
    summary_counts["callable_inventory_metrics"] = _build_callable_inventory_metrics(summary_counts, function_inventory)

    full_contract = {
        "metadata": _callable_flow_metadata(generated_at_utc),
        "function_inventory": function_inventory,
        "public_entrypoint_flow": public_entrypoint_flow,
        "summary_counts": summary_counts,
        "architecture_thresholds": {
            "long_call_chain_depth": LONG_CALL_CHAIN_DEPTH_THRESHOLD,
            "large_dependency_surface": LARGE_DEPENDENCY_SURFACE_THRESHOLD,
        },
    }
    return _trim_callable_flow_dashboard_contract(full_contract)


def _public_callable_docs_url(callable_name: str) -> str:
    """Return the callable-flow relative URL for a public API reference page."""
    return f"../../api/reference/{callable_name}/"


def _render_link(label: str, url: str | None = None, *, code: bool = True) -> str:
    """Render an HTML link or code span for generated callable-flow tables."""
    text = html.escape(label)
    inner = f"<code>{text}</code>" if code else text
    if not url:
        return inner
    return f'<a href="{html.escape(url, quote=True)}">{inner}</a>'


def _render_refactor_inventory_items(items: list[dict[str, Any]]) -> str:
    """Render compact linked callable names for refactor inventory table cells."""
    return ", ".join(
        _render_link(item.get("function") or item.get("callable", "—"), item.get("source_url") or item.get("docs_url"))
        for item in items
    ) or "—"


def _render_refactor_inventory_table(
    rows: list[dict[str, Any]],
    *,
    include_counts: bool = True,
) -> list[str]:
    """Render refactor inventory rows for dashboard and collapsible sections."""
    table_rows: list[list[tuple[str, str]]] = []
    for row in rows:
        cells = [
            (_render_link(row["function"], row.get("source_url")), "flow-cell-name"),
            (_render_link(row["module"], code=True), "flow-cell-module"),
            (_render_link(row["qualified_name"], code=True), "flow-cell-qualified"),
            (
                ", ".join(html.escape(REFACTOR_REASON_LABELS.get(signal, signal)) for signal in row["signals"]) or "—",
                "flow-cell-wide",
            ),
            (_render_refactor_inventory_items(row["used_by"]), "flow-cell-wide"),
            (_render_refactor_inventory_items(row["calls"]), "flow-cell-wide"),
        ]
        if include_counts:
            cells.extend(
                [
                    (str(row["inbound_count"]), "flow-cell-number"),
                    (str(row["outbound_project_call_count"]), "flow-cell-number"),
                    ("—" if row.get("nesting_level") is None else str(row["nesting_level"]), "flow-cell-number"),
                ]
            )
        cells.extend(
            [
                (_render_refactor_inventory_items(row.get("public_entrypoint_lineage", [])), "flow-cell-wide"),
                (html.escape(row["suggested_action"]), "flow-cell-wide"),
            ]
        )
        table_rows.append(cells)

    headers = [
        ("Internal helper", "flow-cell-name"),
        ("Module", "flow-cell-module"),
        ("Qualified name", "flow-cell-qualified"),
        ("Recommended action / priority", "flow-cell-wide"),
        ("Called by", "flow-cell-wide"),
        ("Calls", "flow-cell-wide"),
    ]
    if include_counts:
        headers.extend(
            [
                ("Inbound", "flow-cell-number"),
                ("Outbound", "flow-cell-number"),
                ("Depth", "flow-cell-number"),
            ]
        )
    headers.extend(
        [
            ("Public entrypoint lineage", "flow-cell-wide"),
            ("Recommended action", "flow-cell-wide"),
        ]
    )
    return _render_flow_table(headers, table_rows)


def _render_flow_table(headers: list[tuple[str, str]], rows: list[list[tuple[str, str]]]) -> list[str]:
    """Render a horizontally scrollable callable-flow table."""
    lines = [
        '<div class="callable-flow-table-wrap" markdown="0">',
        '<table class="callable-flow-table">',
        '<thead>',
        '<tr>',
    ]
    for label, class_name in headers:
        lines.append(f'<th class="{class_name}">{html.escape(label)}</th>')
    lines.extend(['</tr>', '</thead>', '<tbody>'])
    for row in rows:
        lines.append('<tr>')
        for value, class_name in row:
            lines.append(f'<td class="{class_name}">{value}</td>')
        lines.extend(['</tr>'])
    lines.extend(['</tbody>', '</table>', '</div>'])
    return lines

def _render_refactor_dashboard_html(flow_data: dict[str, Any]) -> str:
    """Render the standalone static callable architecture decision dashboard HTML page."""
    generation_banner = _render_callable_generation_banner(flow_data)
    return r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Callable Architecture</title><link rel="stylesheet" href="../stylesheets/table-controls.css"><style>body{margin:0;font-family:Inter,system-ui,sans-serif;background:#f8fafc;color:#0f172a}header,main{max-width:1480px;margin:0 auto;padding:1rem}header{background:#fff;border-bottom:1px solid #dbe3ef}.generation-banner{display:flex;flex-wrap:wrap;gap:.35rem .75rem;align-items:center;width:fit-content;max-width:100%;margin:.5rem 0;padding:.35rem .6rem;border:1px solid #cbd5e1;border-radius:999px;background:#f1f5f9;color:#475569;font-size:.78rem;line-height:1.35}.generation-banner span{display:inline-flex}.surface-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.65rem}@media(max-width:650px){.surface-cards{grid-template-columns:repeat(2,minmax(0,1fr))}}.surface-card,.flow-details,.selected-summary{background:#fff;border:1px solid #dbe3ef;border-radius:.75rem;padding:.8rem}.surface-card{position:relative;overflow:hidden}.surface-card strong{display:block;margin-bottom:.25rem;line-height:1;font-size:1.65rem}.surface-card span{display:block;line-height:1.2;color:#475569}.surface-card small{display:block;margin-top:.32rem;line-height:1.25;color:#64748b}.surface-card.info{border-color:#bfdbfe;background:#eff6ff}.surface-card.muted{background:#f8fafc}.surface-card.good{border-color:#bbf7d0;background:#f0fdf4}.surface-card.review{border-color:#fde68a;background:#fffbeb}.surface-card.risk{border-color:#fecaca;background:#fef2f2}.surface-card.risk strong{color:#991b1b}.surface-card.review strong{color:#92400e}.surface-card.good strong{color:#166534}.filter-panel{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:.55rem;margin:.8rem 0;align-items:end}.quick-filter-bar{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;margin:.65rem 0}.quick-filter-chip{border:1px solid #cbd5e1;border-radius:999px;background:#f8fafc;color:#1d4ed8;font-weight:800;cursor:pointer}.quick-filter-chip.is-active{background:#1d4ed8;color:#fff;border-color:#1d4ed8}.architecture-clear-all{border:1px solid #cbd5e1;border-radius:.45rem;background:#fff;color:#1d4ed8;font-weight:800}.filter-field{display:flex;flex-direction:column;font-weight:700;font-size:.8rem}input,select,button{padding:.42rem .5rem;border:1px solid #dbe3ef;border-radius:.45rem;background:#fff}.table-actions{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;margin:.75rem 0}.selected-summary{display:none;background:#eff6ff}.selected-summary.is-visible{display:block}.callable-flow-filter-banner{display:flex;align-items:center;justify-content:space-between;gap:.75rem}.callable-flow-filter-banner strong{min-width:0}.callable-flow-reset-button{background:#15803d;color:#fff;border:1px solid #166534;border-radius:.375rem;padding:.4rem .75rem;font-weight:700;text-decoration:none;cursor:pointer}.callable-flow-reset-button:hover{background:#166534}.table-wrap{overflow:auto;background:#fff;border:1px solid #dbe3ef;border-radius:.75rem}table{width:100%;min-width:940px;border-collapse:collapse}th,td{padding:.3rem .36rem;border-bottom:1px solid #dbe3ef;text-align:left;vertical-align:middle;font-size:.82rem}th{background:#eef2f7;font-size:.72rem}.sort-button{display:inline-flex;gap:.25rem;align-items:center;border:0;background:transparent;color:#1d4ed8;font:inherit;font-weight:800;padding:0;cursor:pointer}.sort-button::after{content:"↕";color:#64748b;font-size:.7rem}.sort-button[aria-sort="ascending"]::after{content:"↑"}.sort-button[aria-sort="descending"]::after{content:"↓"}.num{text-align:right;width:4.5rem;white-space:nowrap}tr.active{outline:2px solid #1d4ed8;outline-offset:-2px;background:#eff6ff}.callable-button{border:0;background:transparent;color:#1d4ed8;font-weight:800;padding:0;text-align:left;cursor:pointer}.source-link{color:#1d4ed8;text-decoration:underline;text-underline-offset:.12em}.source-link:hover{color:#1e40af}.compact-list,.compact-badges{display:block;max-width:14rem;line-height:1.35}.inline-more{display:inline-block;position:relative;margin-left:.15rem}.inline-more summary{display:inline-flex;cursor:pointer;list-style:none}.inline-more summary::-webkit-details-marker{display:none}.inline-more[open] .inline-more-panel{display:block}.inline-more-panel{display:none;position:absolute;z-index:5;min-width:13rem;max-width:min(22rem,80vw);max-height:14rem;overflow:auto;margin-top:.2rem;padding:.35rem;border:1px solid #cbd5e1;border-radius:.55rem;background:#fff;box-shadow:0 .75rem 1.5rem #0f172a1f;white-space:normal}.inline-more-panel .tag,.inline-more-panel .badge{margin:.08rem}.tag,.badge{display:inline-flex;margin:.06rem;padding:.1rem .34rem;border-radius:999px;font-size:.69rem;font-weight:700;background:#e0e7ff;color:#3730a3;white-space:nowrap}.warn{background:#fef3c7;color:#92400e}.issue{background:#fee2e2;color:#b91c1c}.keep{background:#dcfce7;color:#166534}.muted{background:#f1f5f9;color:#475569}.priority{font-weight:800}.priority-critical{background:#991b1b;color:#fff}.priority-high{background:#fee2e2;color:#991b1b}.priority-medium{background:#fef3c7;color:#92400e}.priority-low{background:#e2e8f0;color:#475569}tr.priority-critical-row{background:#fff1f2}tr.priority-high-row{background:#fff7ed}tr.priority-critical-row:not(.active){box-shadow:inset .25rem 0 #991b1b}tr.priority-high-row:not(.active){box-shadow:inset .25rem 0 #f97316}.export-toolbar{display:flex;flex-direction:column;gap:.65rem;align-items:stretch;box-sizing:border-box;max-width:100%;margin:.75rem 0}.toolbar-card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,18rem),1fr));gap:.65rem}.toolbar-card{box-sizing:border-box;min-width:0;padding:.65rem .75rem;border:1px solid #dbe3ef;border-radius:.75rem;background:#f1f5f9}.toolbar-card--selection,.toolbar-card--prompt{display:flex;flex-direction:column;gap:.55rem}.toolbar-row{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;max-width:100%;min-width:0}.toolbar-field{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center;max-width:100%;min-width:0;font-weight:700}.toolbar-field select{max-width:100%;min-width:0}.toolbar-help,.group-help{color:#475569;font-weight:400}.toolbar-group{display:flex;flex-wrap:wrap;gap:.5rem 1rem;align-items:center;max-width:100%;min-width:0}.toolbar-group>div{min-width:0}.toolbar-group .toolbar-row{flex:1 1 16rem}.toolbar-row button{white-space:normal}.primary-action,.danger-action:not(:disabled){background:#1d4ed8;color:#fff;border-color:#1d4ed8}.danger-action:not(:disabled){background:#b91c1c;border-color:#b91c1c}button:disabled,.danger-action:disabled{background:#e5e7eb;color:#94a3b8;border-color:#cbd5e1;cursor:not-allowed}.manual-copy{width:100%;min-height:7rem}.flow-details{margin-top:1rem}.flow-meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(135px,1fr));gap:.5rem}.flow-meta div{padding:.45rem;border:1px solid #e2e8f0;border-radius:.5rem;background:#f8fafc}.flow-tree{max-height:60vh;overflow:auto;border:1px solid #dbe3ef;border-radius:.5rem;padding:.4rem}.flow-tree ul{list-style:none;margin:.2rem 0 .2rem 1rem;padding-left:.8rem;border-left:1px solid #dbe3ef}@media(max-width:720px){main,header{padding:.75rem}.generation-banner{width:auto;border-radius:.75rem}table{min-width:760px}th,td{font-size:.78rem;padding:.26rem}.compact-list,.compact-badges{max-width:10rem}.surface-card strong{font-size:1.35rem}.toolbar-card-grid{grid-template-columns:1fr}.toolbar-row,.toolbar-group{align-items:stretch}.toolbar-field,.toolbar-group{flex-direction:column}.toolbar-field select{width:100%}.toolbar-help{display:block}.toolbar-group .toolbar-row{flex:1 1 auto;flex-direction:row}.toolbar-group .toolbar-row button{flex:1 1 9rem}.callable-flow-filter-banner{align-items:flex-start;flex-direction:column}.callable-flow-reset-button{width:100%;box-sizing:border-box;text-align:center}}</style></head><body><header><h1>Callable Architecture</h1><p>High-level triage for notebook-facing public APIs, dependency depth, and architecture risk.</p><!--CALLABLE_GENERATION_BANNER--><p><a href="callable-functions-inventory.html">Inventory</a> - <a href="../reference/_data/callable-flow.json">Open JSON data</a></p></header><main><h2>Decision mode: Public API Surface</h2><div id="publicSurfaceCards" class="surface-cards"></div><p><small>Architecture metrics summarize public entrypoint flow risk. Use Inventory for helper-level cleanup details.</small></p><section class="filter-panel" aria-label="Architecture quick controls"><label class="filter-field">Callable search<input id="decisionSearchBox" type="search"></label><button id="resetDecisionFilters" class="architecture-clear-all" type="button" hidden>Clear all filters</button></section><section class="quick-filter-bar" aria-label="Architecture quick filters"><button type="button" class="quick-filter-chip is-active" data-architecture-quick-filter="all">All</button><button type="button" class="quick-filter-chip" data-architecture-quick-filter="high_priority">High priority</button><button type="button" class="quick-filter-chip" data-architecture-quick-filter="architecture_violations">Architecture violations</button><button type="button" class="quick-filter-chip" data-architecture-quick-filter="long_flows">Long flows</button><button type="button" class="quick-filter-chip" data-architecture-quick-filter="healthy">Healthy</button><button type="button" class="quick-filter-chip" data-architecture-quick-filter="selected">Selected</button></section><section id="architectureViolationSection" class="flow-details"></section><section class="export-toolbar"><div class="toolbar-card-grid"><div class="toolbar-card toolbar-card--selection" aria-label="Selection"><strong id="selectedCount">Selected: 0 callables</strong><div class="toolbar-row"><button id="selectVisible" class="primary-action" type="button">Select visible</button><button id="clearSelected" class="danger-action" type="button" disabled>Clear selection</button></div></div><div class="toolbar-card toolbar-card--compatibility"><label class="toolbar-field">Compatibility mode <select id="compatibilityMode"><option value="internal_cleanup" selected>Internal cleanup</option><option value="stable_api_safe">Stable API safe</option><option value="development_breaking_allowed">Development breaking allowed</option></select><small class="toolbar-help">Sets the API safety assumptions for generated refactor packages.</small></label></div></div><div class="toolbar-card toolbar-card--prompt"><div class="toolbar-group"><div><strong>AI prompt</strong><br><small class="group-help">Export selected callables for AI-assisted refactor planning.</small></div><div class="toolbar-row"><button id="copyJson" type="button" disabled>Copy JSON</button><button id="copyMarkdown" type="button" disabled>Copy Markdown</button><button id="downloadJson" type="button" disabled>Download JSON</button></div></div><small id="exportStatus"></small><textarea id="manualCopy" class="manual-copy" hidden readonly></textarea></div></section><section id="selectedPublicFlowSummary" class="selected-summary"></section><section class="table-actions"><button id="showAllPublicCallables" type="button" hidden>Show all public callables</button><button id="collapsePublicList" type="button" hidden>Collapse list</button><small id="publicListStatus"></small><small id="dataLoadStatus" class="load-status" aria-live="polite">Loading callable-flow data...</small></section><section class="table-wrap" id="publicCallableTableWrap"><table data-table-controls="excel"><thead><tr><th>Select</th><th>Priority</th><th><button type="button" class="sort-button" data-sort-key="callable">Public callable</button></th><th><button type="button" class="sort-button" data-sort-key="module">Module</button></th><th><button type="button" class="sort-button" data-sort-key="findings">Findings</button></th><th>Review note</th><th><button type="button" class="sort-button" data-sort-key="suggested_action">Suggested action</button></th><th class="num"><button type="button" class="sort-button" data-sort-key="downstream">Downstream</button></th><th class="num"><button type="button" class="sort-button" data-sort-key="depth">Depth</button></th></tr></thead><tbody id="publicCallableList"></tbody></table></section><section id="publicFlowDetails" class="flow-details"><p>Select a public callable to inspect its flow.</p></section></main><script>
const DISPLAY_LABEL_MAP={'Architecture violation':'Architecture violation','Long call chain':'Long call chain','Large dependency surface':'Large dependency surface','Merge candidate':'Merge candidate','Review abstraction':'Review abstraction','Shared utility':'Shared utility','None':'Healthy','Merge candidates found':'Merge candidate found'};let inventory=[],publicEntryFlows=[],visibleFlows=[],summaryCounts={},inventoryByQn=new Map();const state={selected:new Set(),activePublicFlow:'',collapsedPublicList:false,decisionSearch:'',quickFilter:'all',sortKey:'callable',sortDirection:'asc'};let architectureThresholds={long_call_chain_depth:null,large_dependency_surface:null};function positiveThreshold(value){const numeric=Number(value);return Number.isFinite(numeric)&&numeric>0?numeric:null}function longCallChainThreshold(){return positiveThreshold(architectureThresholds.long_call_chain_depth)}function largeDependencySurfaceThreshold(){return positiveThreshold(architectureThresholds.large_dependency_surface)}const $=id=>document.getElementById(id),text=v=>String(v??''),esc=v=>text(v).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));function unique(v){return[...new Set(v.filter(Boolean))].sort()}function displayLabel(v){return DISPLAY_LABEL_MAP[text(v)]||text(v)}function label(v){return displayLabel(text(v).replace(/_/g,' ').replace(/\b\w/g,ch=>ch.toUpperCase()))}function option(s,v,l){const o=document.createElement('option');o.value=v;o.textContent=l||v;s.appendChild(o)}function moreDetails(hidden,render){return hidden.length?`<details class="inline-more"><summary><span class="tag">+${hidden.length} more</span></summary><span class="inline-more-panel">${hidden.map(render).join('')}</span></details>`:''}function compactList(items,limit=3){const list=items||[],shown=list.slice(0,limit),hidden=list.slice(limit);return `<span class="compact-list" title="${esc(list.join(', '))}">${shown.map(i=>`<span class="tag">${esc(i)}</span>`).join('')}${moreDetails(hidden,i=>`<span class="tag">${esc(i)}</span>`)}</span>`}function compactBadges(items,cls='warn',limit=2){const list=items||[];if(!list.length)return '<span class="badge keep">Healthy</span>';const shown=list.slice(0,limit),hidden=list.slice(limit);return `<span class="compact-badges" title="${esc(list.join(', '))}">${shown.map(i=>`<span class="badge ${cls}">${esc(i)}</span>`).join('')}${moreDetails(hidden,i=>`<span class="badge ${cls}">${esc(i)}</span>`)}</span>`}const GITHUB_SOURCE_BASE='https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/';function sourceHref(i){const row=inventoryByQn.get(i.qualified_name)||i;if(row.docs_path)return '../'+String(row.docs_path).replace(/^docs\//,'').replace(/\.md$/,'/');if(row.source_url)return row.source_url;const path=row.source_path||row.path;if(!path)return '';const start=row.source_start_line||row.start_line||row.line_number;const end=row.source_end_line||row.end_line;let anchor=start?`#L${start}`:'';if(start&&end&&end!==start)anchor+=`-L${end}`;return `${GITHUB_SOURCE_BASE}${path}${anchor}`}function sourceCallableLink(i){const href=sourceHref(i);const label=esc(i.function_name);return href?`<a class="source-link" href="${esc(href)}"><code>${label}</code></a>`:`<code>${label}</code>`}function moduleHref(module){return module?`../api/modules/${module}/`:''}function moduleLink(module){const href=moduleHref(module);return href?`<a class="source-link" href="${esc(href)}"><code>${esc(module)}</code></a>`:`<code>${esc(module||'')}</code>`}function linkMetadata(i){const row=inventoryByQn.get(i.qualified_name)||i;return{source_url:row.source_url||null,docs_url:row.docs_url||null,file_path:row.source_path||null,line_start:row.source_start_line||null,line_end:row.source_end_line||null}}function markdownLink(i,label){const href=sourceHref(i);return href?`[${label||i.function_name}](${href})`:(label||i.function_name)}function architecturePriority(f){const violations=(f.architecture_violation_count??0)>0,longThreshold=longCallChainThreshold(),largeThreshold=largeDependencySurfaceThreshold(),deep=longThreshold!==null&&(f.max_depth||0)>=longThreshold,down=f.downstream_count||0,large=largeThreshold!==null&&down>=largeThreshold;if((violations&&deep)||(largeThreshold!==null&&down>=largeThreshold*5))return 'Critical';if(violations||(largeThreshold!==null&&down>=largeThreshold*2.5))return 'High';if(deep||large)return 'Medium';return 'Low'}function priorityClass(p){return text(p).toLowerCase()}function riskBadgeClass(warning,priority){if(priority==='Critical'||priority==='High')return 'issue';return 'muted'}function mergeCandidateCount(flow){return Number(flow.helper_cleanup_candidates??flow.single_use_helper_candidate_count??0)}function mergeCandidateLabel(count){return count===1?'Merge candidate found':`${count} merge candidates found`}function reviewMergeCandidateLabel(count){return count===1?'Review merge candidate':'Review merge candidates'}function suggestedActionLabel(flow){const action=flow.recommended_simplification_action||'Keep public';if(action==='Review merge candidates')return reviewMergeCandidateLabel(mergeCandidateCount(flow));return action}function whyReview(flow){const reasons=[];const violations=flow.architecture_violation_count??0,longThreshold=longCallChainThreshold(),largeThreshold=largeDependencySurfaceThreshold(),mergeCount=mergeCandidateCount(flow);if(violations)reasons.push(`Contains ${violations} architecture violations.`);if(longThreshold!==null&&(flow.max_depth||0)>=longThreshold)reasons.push(`Depth is ${flow.max_depth}; threshold is >= ${longThreshold}.`);if(largeThreshold!==null&&(flow.downstream_count||0)>=largeThreshold)reasons.push(`Has ${flow.downstream_count} downstream functions; threshold is >= ${largeThreshold}.`);if(mergeCount>0)reasons.push(mergeCount===1?'Contains 1 merge candidate inside this flow.':`Contains ${mergeCount} merge candidates inside this flow.`);return reasons.length?reasons.join(' '):'Clear'}function renderCards(){const s=summaryCounts.public_api_surface||{},flows=publicEntryFlows||[],publicCallableCount=flows.length||s.public_api_entrypoints||0,highPriority=flows.filter(f=>['Critical','High'].includes(architecturePriority(f))).length,architectureViolationFlows=flows.filter(f=>architectureFindingCount(f)>0||architectureViolationCount(f)>0).length,longFlowCount=flows.filter(f=>{const threshold=longCallChainThreshold();return threshold===null?(f.warnings||[]).includes('Long call chain'):(f.max_depth||0)>=threshold}).length,shortenableFlowCount=flows.filter(f=>(f.helper_cleanup_candidates??f.single_use_helper_candidate_count??0)>0||(f.transitive_callees||[]).some(c=>c.helper_cleanup_candidate)).length;const cards=[{label:'Public callables scanned',value:publicCallableCount,subtitle:'Notebook-facing APIs included in this decision view.',cls:'info'},{label:'High-priority public callables',value:highPriority,subtitle:'Public APIs to review first.',cls:highPriority?'risk':'good'},{label:'Architecture violations',value:architectureViolationFlows,subtitle:'Public callable flows with architecture violations.',cls:architectureViolationFlows?'risk':'good'},{label:'Long public flows',value:longFlowCount,subtitle:'Public callable flows whose depth exceeds the threshold.',cls:longFlowCount?'review':'good'},{label:'Public flows that can be shortened',value:shortenableFlowCount,subtitle:'Public callable flows with internal helpers that may be simplified, merged, or moved closer to their caller.',cls:shortenableFlowCount?'review':'good'}];$('publicSurfaceCards').innerHTML=cards.map(c=>`<article class="surface-card ${esc(c.cls)}"><strong>${esc(c.value??0)}</strong><span>${esc(c.label)}</span><small>${esc(c.subtitle)}</small></article>`).join('')}function findingLabel(v){return displayLabel(v)}function architectureViolationBreakdown(flows=publicEntryFlows){const counts={'Public -> Public':0,'Internal -> Public':0};flows.forEach(f=>(f.transitive_callees||[]).forEach(c=>{if(c.architecture_result==='Violation'&&counts[c.violation_type]!==undefined)counts[c.violation_type]++}));return counts}function renderArchitectureViolationSection(){const meanings={'Public -> Public':'Public function is calling another public notebook-facing API.','Internal -> Public':'Internal function is calling a notebook-facing public API.'};const rows=Object.entries(architectureViolationBreakdown()).filter(([,count])=>count>0);$('architectureViolationSection').innerHTML=`<h2>Architecture violations</h2><p>Architecture violation: a call goes in the wrong direction between Public and Internal function layers.</p><div class="table-wrap"><table><thead><tr><th>Violation type</th><th class="num">Count</th><th>Meaning</th></tr></thead><tbody>${(rows.length?rows:Object.entries(meanings).map(([k])=>[k,0])).map(([type,count])=>`<tr><td>${esc(type)}</td><td class="num">${esc(count)}</td><td>${esc(meanings[type])}</td></tr>`).join('')}</tbody></table></div><details><summary><strong>How architecture violations are calculated</strong></summary><p>Public functions are notebook-facing entrypoints. Internal functions are implementation details. Supporting objects are allowed dependencies and are not counted as architecture violations.</p><table><thead><tr><th>Caller type</th><th>Callee type</th><th>Result</th></tr></thead><tbody>${[['Public','Public','Violation'],['Public','Internal','Allowed'],['Internal','Internal','Allowed'],['Internal','Public','Violation'],['Public','Supporting object','Allowed'],['Internal','Supporting object','Allowed']].map(r=>`<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td></tr>`).join('')}</tbody></table></details>`}const DOWNSTREAM_BANDS=[['downstream_0','0',v=>v===0],['downstream_1_2','1–2',v=>v>=1&&v<=2],['downstream_3_5','3–5',v=>v>=3&&v<=5],['downstream_6_10','6–10',v=>v>=6&&v<=10],['downstream_gt_10','>10',v=>v>10]];const DEPTH_BANDS=[['depth_0_1','0–1',v=>v>=0&&v<=1],['depth_2_3','2–3',v=>v>=2&&v<=3],['depth_4_5','4–5',v=>v>=4&&v<=5],['depth_gte_6','>=6',v=>v>=6]];const ISSUE_BANDS=[['issues_0','No violations',v=>v===0],['issues_1','1 violation',v=>v===1],['issues_gte_2','2+ violations',v=>v>=2]];const ISSUE_BOOLEAN_BANDS=[['issues_0','No violations',v=>v===0],['issues_gte_1','1+ violations',v=>v>=1]];function architectureViolationCount(flow){const value=flow.architecture_violation_count;if(typeof value==='boolean')return value?1:0;const numeric=Number(value??0);return Number.isFinite(numeric)?numeric:0}function architectureFindingRows(flow){return (flow.transitive_callees||[]).filter(c=>c.architecture_result==='Violation'||c.recommended_action==='Architecture violation')}function publicCallableFindingRows(flow){const findings=architectureFindingRows(flow),longThreshold=longCallChainThreshold(),largeThreshold=largeDependencySurfaceThreshold(),rows=[...(flow.architecture_violation_count?[{finding:'Architecture violations found',evidence:`${flow.architecture_violation_count} call edge(s) go in the wrong direction.`,suggested_action:'Review the exact edges below.'}]:[]),...((findings.length>architectureViolationCount(flow))?[{finding:'Helper-level architecture findings found',evidence:`${findings.length-architectureViolationCount(flow)} helper-level architecture finding(s) are visible in this flow.`,suggested_action:'Review the architecture findings table and helper tags below.'}]:[]),...((longThreshold!==null&&(flow.max_depth||0)>=longThreshold)?[{finding:'Long call chain',evidence:`Depth ${flow.max_depth}, threshold >= ${longThreshold}`,suggested_action:'Review whether the flow can be simplified.'}]:[]),...((largeThreshold!==null&&(flow.downstream_count||0)>=largeThreshold)?[{finding:'Large dependency surface',evidence:`${flow.downstream_count} downstream functions, threshold >= ${largeThreshold}`,suggested_action:'Many functions depend on this flow. Refactor carefully.'}]:[]),...((flow.helper_cleanup_candidates||0)>0?[{finding:mergeCandidateLabel(mergeCandidateCount(flow))+' inside flow',evidence:mergeCandidateCount(flow)===1?'1 helper function may be a merge candidate.':`${mergeCandidateCount(flow)} helper functions may be merge candidates.`,suggested_action:reviewMergeCandidateLabel(mergeCandidateCount(flow))+' without merging away the public API.'}]:[])];return rows.length?rows:[{finding:'Healthy',evidence:'Clear',suggested_action:'Keep public'}]}function architectureFindingCount(flow){return architectureFindingRows(flow).length}function metricValue(flow,metric){if(metric==='downstream')return Number(flow.downstream_count??0);if(metric==='depth')return Number(flow.max_depth??0);return architectureFindingCount(flow)}function issueBandsForRows(rows){return rows.some(flow=>typeof flow.architecture_violation_count==='number')?ISSUE_BANDS:ISSUE_BOOLEAN_BANDS}function matchesBand(flow,bandValue,bands,metric){if(!bandValue)return true;const band=bands.find(([value])=>value===bandValue);return band?band[2](metricValue(flow,metric)):true}function matchesQuickFilter(flow){if(state.quickFilter==='high_priority')return ['Critical','High'].includes(architecturePriority(flow));if(state.quickFilter==='architecture_violations')return architectureFindingCount(flow)>0||architectureViolationCount(flow)>0;if(state.quickFilter==='long_flows'){const threshold=longCallChainThreshold();return threshold!==null&&(flow.max_depth||0)>=threshold}if(state.quickFilter==='healthy')return architectureFindingCount(flow)===0&&architectureViolationCount(flow)===0&&!(flow.warnings||[]).length;if(state.quickFilter==='selected')return state.selected.has(flow.qualified_name);return true}function updateQuickFilterChips(){document.querySelectorAll('[data-architecture-quick-filter]').forEach(button=>button.classList.toggle('is-active',button.dataset.architectureQuickFilter===state.quickFilter));$('resetDecisionFilters').hidden=state.decisionSearch===''&&state.quickFilter==='all'}function filteredPublicFlows(){const q=state.decisionSearch.toLowerCase();return publicEntryFlows.filter(f=>(!q||text(f.function_name).toLowerCase().includes(q)||text(f.qualified_name).toLowerCase().includes(q)||text(f.module).toLowerCase().includes(q))&&matchesQuickFilter(f))}function sortValue(flow,key){if(key==='callable')return text(flow.function_name).toLowerCase();if(key==='module')return text(flow.module).toLowerCase();if(key==='findings')return (flow.warnings||[]).map(findingLabel).join(' ').toLowerCase()||'healthy';if(key==='suggested_action')return suggestedActionLabel(flow).toLowerCase();if(key==='downstream')return Number(flow.downstream_count??0);if(key==='depth')return Number(flow.max_depth??0);return text(flow.function_name).toLowerCase()}function stableSortRows(rows){const dir=state.sortDirection==='desc'?-1:1,key=state.sortKey;return rows.map((row,index)=>({row,index})).sort((a,b)=>{const av=sortValue(a.row,key),bv=sortValue(b.row,key);if(av<bv)return -1*dir;if(av>bv)return 1*dir;return a.index-b.index}).map(item=>item.row)}function updateSortButtons(){document.querySelectorAll('[data-sort-key]').forEach(button=>{const active=button.dataset.sortKey===state.sortKey;button.setAttribute('aria-sort',active?(state.sortDirection==='asc'?'ascending':'descending'):'none')})}function rowsForDisplay(){if(!state.collapsedPublicList)return visibleFlows;return visibleFlows.filter(f=>f.qualified_name===state.activePublicFlow)}function setPublicListControls(){const active=publicEntryFlows.find(i=>i.qualified_name===state.activePublicFlow);$('showAllPublicCallables').hidden=!state.collapsedPublicList;$('collapsePublicList').hidden=state.collapsedPublicList||!active;$('publicListStatus').textContent=state.collapsedPublicList&&active?`Showing selected callable from ${visibleFlows.length} matching public callables.`:`Showing ${visibleFlows.length} matching public callables.`;const showSelectedBanner=Boolean(state.collapsedPublicList&&active);$('selectedPublicFlowSummary').classList.toggle('is-visible',showSelectedBanner);$('selectedPublicFlowSummary').innerHTML=showSelectedBanner?`<div class="callable-flow-filter-banner"><strong>Showing flow for <code>${esc(active.function_name)}</code></strong><button type="button" id="backToAllPublicCallables" class="callable-flow-reset-button">Back to all public callables</button></div>`:'';const reset=$('backToAllPublicCallables');if(reset)reset.onclick=showAllPublicCallables}function renderLoadStatus(message,isError=false){const el=$('dataLoadStatus');if(!el)return;el.textContent=message;el.className=isError?'load-status issue':'load-status'}function callableFlowDataUrl(){const path=window.location.pathname,origin=window.location.origin,referenceMarker='/reference/',assetsMarker='/assets/';if(path.includes(referenceMarker)){return origin+path.slice(0,path.indexOf(referenceMarker)+referenceMarker.length)+'_data/callable-flow.json'}if(path.includes(assetsMarker)){return origin+path.slice(0,path.indexOf(assetsMarker)+1)+'reference/_data/callable-flow.json'}return new URL('reference/_data/callable-flow.json',document.baseURI).href}function renderLoadedCount(){renderLoadStatus(`Loaded ${inventory.length} total callables; ${publicEntryFlows.length} public callables available; ${visibleFlows.length} rows after filters.`)}function renderPublicCallableList(){visibleFlows=stableSortRows(filteredPublicFlows());updateQuickFilterChips();if(!state.activePublicFlow&&visibleFlows.length)state.activePublicFlow=visibleFlows[0].qualified_name;if(state.activePublicFlow&&!visibleFlows.some(f=>f.qualified_name===state.activePublicFlow))state.collapsedPublicList=false;const rows=rowsForDisplay();renderLoadedCount();$('publicCallableList').innerHTML=rows.map(f=>{const p=architecturePriority(f),pc=priorityClass(p),strong=p==='Critical'||p==='High',active=f.qualified_name===state.activePublicFlow?'active':'';return `<tr data-public-flow-row="${esc(f.qualified_name)}" class="${active} ${strong?'priority-'+pc+'-row':''}"><td><input type="checkbox" data-select-row="${esc(f.qualified_name)}" ${state.selected.has(f.qualified_name)?'checked':''}></td><td><span class="badge priority priority-${pc}">${esc(p)}</span></td><td>${sourceCallableLink(f)} <button type="button" class="callable-button" data-public-flow="${esc(f.qualified_name)}">Inspect flow</button></td><td>${moduleLink(f.module)}</td><td>${compactBadges((f.warnings||[]).map(findingLabel),riskBadgeClass('',p))}</td><td>${esc(whyReview(f))}</td><td><span class="badge ${suggestedActionLabel(f)==='Keep public'?'keep':'muted'}">${esc(suggestedActionLabel(f))}</span></td><td class="num">${f.downstream_count}</td><td class="num">${f.max_depth}</td></tr>`}).join('');setPublicListControls();updateSortButtons();renderFlowDetails();updateExportControls();if(window.FabricOpsTableControls)window.FabricOpsTableControls.enhance(document.querySelector('table[data-table-controls="excel"]'))}function showAllPublicCallables(){state.collapsedPublicList=false;renderPublicCallableList();$('publicCallableTableWrap').scrollIntoView({behavior:'smooth',block:'start'})}function collapsePublicList(){state.collapsedPublicList=true;renderPublicCallableList();$('publicFlowDetails').scrollIntoView({behavior:'smooth',block:'start'})}function buildFlowTree(flow){const root={qualified_name:flow.qualified_name,function_name:flow.function_name,module:flow.module,docs_url:flow.docs_url,docs_path:flow.docs_path,source_url:flow.source_url,children:[]},byParent=new Map();(flow.transitive_callees||[]).forEach(r=>{const p=r.parent_qualified_name||flow.qualified_name;if(!byParent.has(p))byParent.set(p,[]);byParent.get(p).push({...r,children:[]})});function attach(n){n.children=(byParent.get(n.qualified_name)||[]).sort((a,b)=>a.depth-b.depth);n.children.forEach(attach);return n}return attach(root)}function renderTreeNode(n){const violation=n.architecture_result==='Violation'&&n.violation_type?` <span class="badge issue">Architecture violation: ${esc(n.violation_type)}</span>`:'';const action=n.recommended_action?` <span class="tag">${esc(findingLabel(n.recommended_action))}</span>`:'';return `<li><strong>${sourceCallableLink(n)}</strong> <small>${esc(n.module||'')}</small>${violation}${action}${n.children?.length?`<ul>${n.children.map(renderTreeNode).join('')}</ul>`:''}</li>`}function renderFlowDetails(){const f=publicEntryFlows.find(i=>i.qualified_name===state.activePublicFlow);if(!f){$('publicFlowDetails').innerHTML='<p>No public entrypoint flow data found.</p>';return}const tree=buildFlowTree(f),violations=(f.transitive_callees||[]).filter(c=>c.architecture_result==='Violation'),architectureFindings=architectureFindingRows(f),longThreshold=longCallChainThreshold(),largeThreshold=largeDependencySurfaceThreshold(),mergeCandidates=(f.transitive_callees||[]).filter(c=>c.helper_cleanup_candidate),publicFindings=publicCallableFindingRows(f);$('publicFlowDetails').innerHTML=`<h2>Callable flow</h2><p><strong>Selected callable:</strong> ${sourceCallableLink(f)} <small>${esc(f.qualified_name)}</small></p><p><strong>Recommendation:</strong> <span class="badge ${suggestedActionLabel(f)==='Keep public'?'keep':'warn'}">${esc(suggestedActionLabel(f))}</span></p><p>${compactBadges((f.warnings||[]).map(findingLabel),'warn',99)}</p><div class="flow-meta"><div><strong>${f.downstream_count}</strong><br><span>Downstream count</span></div><div><strong>${f.max_depth}</strong><br><span>${longThreshold===null?'Depth; long call chain threshold unavailable':`Depth; long call chain threshold >= ${longThreshold}`}</span></div><div><strong>${f.architecture_violation_count}</strong><br><span>Architecture violations</span></div><div><strong>${(f.modules_touched||[]).length}</strong><br><span>Modules touched</span></div></div><h3>Public callable findings</h3><div class="table-wrap"><table><thead><tr><th>Finding</th><th>Evidence</th><th>Suggested action</th></tr></thead><tbody>${publicFindings.map(r=>`<tr><td>${esc(r.finding)}</td><td>${esc(r.evidence)}</td><td>${esc(r.suggested_action)}</td></tr>`).join('')}</tbody></table></div><h3>Architecture findings inside this flow</h3><div class="table-wrap"><table><thead><tr><th>Source function</th><th>Source type</th><th>Target function</th><th>Target type</th><th>Finding type</th><th>Suggested fix</th></tr></thead><tbody>${(architectureFindings.length?architectureFindings:[{}]).map(v=>v.qualified_name?`<tr><td>${sourceCallableLink(inventoryByQn.get(v.parent_qualified_name)||{qualified_name:v.parent_qualified_name,function_name:v.parent_qualified_name})}</td><td>${esc(v.caller_type||'Helper')}</td><td>${sourceCallableLink(v)}</td><td>${esc(v.callee_type||v.layer_group||v.function_type||'Helper')}</td><td>${esc(v.violation_type||findingLabel(v.recommended_action||'Architecture violation'))}</td><td>${esc(v.violation_type==='Internal -> Public'?'Move shared logic behind an internal helper, then let the public API call that helper.':v.violation_type==='Public -> Public'?'Move the shared implementation behind an internal helper so each public API remains an entrypoint.':'Review function placement and keep supporting objects out of violation counts.')}</td></tr>`:'<tr><td colspan="6">No architecture findings found in this flow.</td></tr>').join('')}</tbody></table></div><h3>Internal helper cleanup candidates</h3><div class="table-wrap"><table><thead><tr><th>Function</th><th>Function type</th><th>Called by</th><th>Finding</th><th>Suggested action</th></tr></thead><tbody>${(mergeCandidates.length?mergeCandidates:[{}]).map(c=>c.qualified_name?`<tr><td>${sourceCallableLink(c)}</td><td>${esc(c.layer_group)}</td><td>${sourceCallableLink(inventoryByQn.get(c.parent_qualified_name)||{qualified_name:c.parent_qualified_name,function_name:c.parent_qualified_name})}</td><td>${esc(findingLabel(c.recommended_action||'Merge candidate'))}</td><td>${esc((c.recommended_action||'').includes('Shared')?'Keep as shared internal helper.':(c.recommended_action||'').includes('Review')?'Keep only if the helper improves readability or reuse.':'Consider merging into parent.')}</td></tr>`:'<tr><td colspan="5">No internal helper cleanup candidates found.</td></tr>').join('')}</tbody></table></div><p><strong>direct callees</strong> are included in the flow tree.</p><h3>Flow tree</h3><div id="callableFlowTree" class="flow-tree"><ul>${renderTreeNode(tree)}</ul></div>`}function selectedItems(){const byQn=new Map(publicEntryFlows.map(r=>[r.qualified_name,r]));return[...state.selected].map(q=>byQn.get(q)).filter(Boolean)}function findingRows(f){return architectureFindingRows(f).map(v=>({source_function:(inventoryByQn.get(v.parent_qualified_name)||{}).function_name||v.parent_qualified_name,source_type:v.caller_type||'Helper',target_function:v.function_name,target_type:v.callee_type||v.layer_group||v.function_type||'Helper',finding_type:v.violation_type||findingLabel(v.recommended_action||'Architecture violation'),suggested_fix:v.violation_type==='Internal -> Public'?'Move shared logic behind an internal helper, then let the public API call that helper.':v.violation_type==='Public -> Public'?'Move the shared implementation behind an internal helper so each public API remains an entrypoint.':'Review function placement and keep supporting objects out of violation counts.',source_link:linkMetadata(inventoryByQn.get(v.parent_qualified_name)||{qualified_name:v.parent_qualified_name}),target_link:linkMetadata(v)}))}function cleanupRows(f){return (f.transitive_callees||[]).filter(c=>c.helper_cleanup_candidate).map(c=>({function:c.function_name,function_type:c.layer_group,called_by:(inventoryByQn.get(c.parent_qualified_name)||{}).function_name||c.parent_qualified_name,finding:findingLabel(c.recommended_action||'Merge candidate'),suggested_action:(c.recommended_action||'').includes('Shared')?'Keep as shared internal helper.':(c.recommended_action||'').includes('Review')?'Keep only if the helper improves readability or reuse.':'Consider merging into parent.',link:linkMetadata(c),called_by_link:linkMetadata(inventoryByQn.get(c.parent_qualified_name)||{qualified_name:c.parent_qualified_name})}))}function serializeTree(n){return {...linkMetadata(n),qualified_name:n.qualified_name,function_name:n.function_name,module:n.module,function_type:n.function_type||n.layer_group||'Public function',helper_tags:[...(n.architecture_result==='Violation'&&n.violation_type?[`Architecture violation: ${n.violation_type}`]:[]),...(n.recommended_action?[findingLabel(n.recommended_action)]:[])],children:(n.children||[]).map(serializeTree)}}function exportItem(f){const tree=buildFlowTree(f),row=inventoryByQn.get(f.qualified_name)||f,cleanup=cleanupRows(f),publicFindings=publicCallableFindingRows(f);return{selected_public_callable_name:f.function_name,function_name:f.function_name,qualified_name:f.qualified_name,module:f.module,module_docs_url:moduleHref(f.module)||null,callable_type:row.function_type||row.callable_kind||'Public function',recommendation:suggestedActionLabel(f),tags:f.warnings||[],findings:f.warnings||[],why_review:whyReview(f),depth:f.max_depth,call_depth:f.max_depth,downstream_count:f.downstream_count,modules_touched:f.modules_touched||[],architecture_violation_count:f.architecture_violation_count||0,merge_shortening_candidate_count:f.helper_cleanup_candidates||cleanup.length,public_callable_findings:publicFindings,architecture_findings:findingRows(f),internal_helper_cleanup_candidates:cleanup,flow_tree:serializeTree(tree),...linkMetadata(f)}}const COMPATIBILITY_INSTRUCTIONS={internal_cleanup:'Preserve public API behavior while allowing internal cleanup.',stable_api_safe:'Avoid breaking notebook-facing APIs.',development_breaking_allowed:'Breaking changes require updated callers, tests, and docs.'};function refactorContext(callables){const mode=$('compatibilityMode').value;return{compatibility_mode:mode,compatibility_instruction:COMPATIBILITY_INSTRUCTIONS[mode],planning_only:true}}function batchAccounting(callables){return{selected_callable_count:callables.length,planned_batch_count:callables.length,batch_id:null,batch_scope:'selected / handled / remaining counts',batch_strategy:'Completion accounting required in PR description',completed_or_refactored_count:null,remaining_selected_count:null,deferred_selected_callables:[]}}function refactorPacket(){const callables=selectedItems().map(exportItem);return{schema:'fabricops_callable_refactor_packet',callables,functions:callables,batch_accounting:batchAccounting(callables),refactor_context:refactorContext(callables),planning_instructions:['Group functions by refactor action before proposing code changes.','Identify helpers that can be merged into parent callables and helpers that should remain separate.','Identify architecture violations, explain why they matter, and propose safe fixes.','Preserve public API behavior and avoid changing notebook-facing callable signatures unless compatibility mode explicitly allows it.','Use public callable findings, architecture violation rows, internal helper cleanup candidates, and flow tree tags as grounding evidence.','Propose an ordered implementation plan, list tests required before and after refactor, and call out migration risks.'],required_tests:['Run relevant unit tests for changed helpers before and after refactor.','Run compile and docs checks when generated references or docs change.'],final_output_required:['Write the final output as instructions that can be pasted into Codex, Claude Code, Cursor, or another coding agent.','Produce a PR execution plan for a coding agent targeting the main branch.','Preserve public API behavior and avoid changing notebook-facing callable signatures unless compatibility mode allows it.','Group refactor actions by helper/function.','Identify architecture violations to address.','Identify helpers to merge, move, or keep.','List implementation steps in order.','List tests to add, update, and run.','Define acceptance criteria.','Call out risks and rollback notes.','Do not write code yet and do not generate a patch.'],ai_prompt:'Review selected public callable flows with the included callable-level evidence and produce a coding-agent PR execution plan.'}}function treeMarkdown(n,level=0){const pad='  '.repeat(level);const tags=(n.helper_tags||[]).length?` — ${(n.helper_tags||[]).join(', ')}`:'';return `${pad}- ${markdownLink(n,n.function_name)} (${n.qualified_name})${tags}${(n.children||[]).length?'\n'+n.children.map(c=>treeMarkdown(c,level+1)).join('\n'):''}`}function callableMarkdown(item){return [`### ${markdownLink(item,item.selected_public_callable_name)}`,`- Fully qualified name: ${item.qualified_name}` ,`- Module: ${item.module_docs_url?`[${item.module}](${item.module_docs_url})`:item.module}`,`- Callable type: ${item.callable_type}`,`- Recommendation: ${item.recommendation}`,`- Tags: ${(item.tags||item.findings||[]).join(', ')||'None'}`,`- Why review: ${item.why_review}`,`- Downstream count: ${item.downstream_count}`,`- Call depth: ${item.call_depth}`,`- Modules touched: ${(item.modules_touched||[]).join(', ')||'None'}`,`- Architecture violation count: ${item.architecture_violation_count??0}`,`- Merge/shortening candidate count: ${item.merge_shortening_candidate_count}`,`- Architecture findings: ${(item.architecture_findings||[]).length}`,`- Internal helper cleanup candidates: ${(item.internal_helper_cleanup_candidates||[]).length}`,'#### Public callable findings',...((item.public_callable_findings||[]).map(f=>`- ${f.finding}: ${f.evidence}; ${f.suggested_action}`)),'#### Architecture findings',...((item.architecture_findings||[]).map(f=>`- ${f.source_function} (${f.source_type}) -> ${f.target_function} (${f.target_type}): ${f.finding_type}; ${f.suggested_fix}`)), '#### Internal helper cleanup candidates',...((item.internal_helper_cleanup_candidates||[]).map(c=>`- ${c.function} (${c.function_type}), called by ${c.called_by}: ${c.finding}; ${c.suggested_action}`)),'#### Full nested flow tree',treeMarkdown(item.flow_tree)].join('\n')}function markdownPacket(packet){return `# Callable refactor packet

## Objective
Review selected FabricOps callables for maintainability and decision-ready architecture cleanup.

## Architecture intent
Keep public API flow clear, simplify long call chains, and reduce confusing architecture violations.

## Compatibility mode
- selected mode: ${packet.refactor_context.compatibility_mode}
- instruction: ${packet.refactor_context.compatibility_instruction}

## Selected callables
${packet.callables.map(callableMarkdown).join('\n')}

## Requested work
Review each callable and preserve expected public behavior unless the selected mode allows otherwise.

## Output required from AI
Return summary, changed callables, tests, risks, follow-up items, and accounting.

## Batch accounting
- Selected callable count: ${packet.batch_accounting.selected_callable_count}
- Planned batch count: ${packet.batch_accounting.planned_batch_count}
- Remaining selected count: fill in after implementation

## Final output required
Write the final output as instructions that can be pasted into Codex, Claude Code, Cursor, or another coding agent. Produce a PR execution plan for a coding agent targeting the main branch. Preserve public API behavior and avoid changing notebook-facing callable signatures unless the selected compatibility mode explicitly allows it. Group refactor actions by helper/function; identify architecture violations to address; identify helpers to merge, move, or keep; list implementation steps in order; list tests to add, update, and run; define acceptance criteria; and call out risks and rollback notes. Do not write code yet and do not generate a patch.
`;}async function copyExport(format){const packet=refactorPacket();const v=format==='markdown'?markdownPacket(packet):JSON.stringify(packet,null,2);try{await navigator.clipboard.writeText(v);$('exportStatus').textContent=`Copied ${format}.`;$('manualCopy').hidden=true}catch(e){$('manualCopy').hidden=false;$('manualCopy').value=v;$('exportStatus').textContent='Clipboard unavailable; copy from the text area.'}}function downloadJson(){const blob=new Blob([JSON.stringify(refactorPacket(),null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='fabricops-callable-refactor-packet.json';a.click()}function updateExportControls(){$('selectedCount').textContent=`Selected: ${state.selected.size} callables`;['copyJson','copyMarkdown','downloadJson'].forEach(id=>$(id).disabled=state.selected.size===0);$('clearSelected').disabled=state.selected.size===0}$('showAllPublicCallables').onclick=showAllPublicCallables;$('collapsePublicList').onclick=collapsePublicList;$('selectVisible').onclick=()=>{visibleFlows.forEach(f=>state.selected.add(f.qualified_name));renderPublicCallableList()};$('clearSelected').onclick=()=>{state.selected.clear();renderPublicCallableList()};$('copyJson').onclick=()=>copyExport('json');$('copyMarkdown').onclick=()=>copyExport('markdown');$('downloadJson').onclick=downloadJson;document.addEventListener('click',e=>{const b=e.target.closest('[data-public-flow]');if(b){state.activePublicFlow=b.dataset.publicFlow;state.collapsedPublicList=true;renderPublicCallableList();$('publicFlowDetails').scrollIntoView({behavior:'smooth',block:'start'})}});document.addEventListener('change',e=>{const r=e.target.closest('[data-select-row]');if(r){r.checked?state.selected.add(r.dataset.selectRow):state.selected.delete(r.dataset.selectRow);updateExportControls()}});$('decisionSearchBox').addEventListener('input',e=>{state.decisionSearch=e.target.value;state.collapsedPublicList=false;renderPublicCallableList()});document.addEventListener('click',e=>{const chip=e.target.closest('[data-architecture-quick-filter]');if(!chip)return;state.quickFilter=chip.dataset.architectureQuickFilter;state.collapsedPublicList=false;renderPublicCallableList()});$('resetDecisionFilters').onclick=()=>{Object.assign(state,{decisionSearch:'',quickFilter:'all',sortKey:'callable',sortDirection:'asc',collapsedPublicList:false});$('decisionSearchBox').value='';if(window.FabricOpsTableControls)window.FabricOpsTableControls.resetAll(document);renderPublicCallableList()};async function loadData(){const attemptedUrl=callableFlowDataUrl();try{const response=await fetch(attemptedUrl);if(!response.ok)throw new Error(`HTTP ${response.status} ${response.statusText}`);const data=await response.json();inventory=data.function_inventory||[];inventoryByQn=new Map(inventory.map(row=>[row.qualified_name,row]));publicEntryFlows=data.public_entrypoint_flow||[];summaryCounts=data.summary_counts||{};architectureThresholds=data.architecture_thresholds||architectureThresholds;renderCards();renderPublicCallableList()}catch(error){const status=error&&error.message&&error.message.startsWith('HTTP ')?error.message:'Network/parse error';renderLoadStatus(`Failed to load callable-flow data. Attempted URL: ${attemptedUrl}. HTTP status: ${status}. Error message: ${error&&error.message?error.message:String(error)}`,true)}}loadData();
</script><script src="../javascripts/table-controls.js"></script></body></html>
""".replace("<!--CALLABLE_GENERATION_BANNER-->", generation_banner)

def _render_refactor_inventory_html(flow_data: dict[str, Any]) -> str:
    """Render the standalone static raw callable inventory HTML page."""
    generation_banner = _render_callable_generation_banner(flow_data)
    return r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Callable Inventory</title><link rel="stylesheet" href="../stylesheets/table-controls.css"><style>body{margin:0;font-family:Inter,system-ui,sans-serif;background:#f8fafc;color:#0f172a}header,main{max-width:1500px;margin:0 auto;padding:1rem}.generation-banner{display:flex;flex-wrap:wrap;gap:.35rem .75rem;align-items:center;width:fit-content;max-width:100%;margin:.5rem 0;padding:.35rem .6rem;border:1px solid #cbd5e1;border-radius:999px;background:#f1f5f9;color:#475569;font-size:.78rem;line-height:1.35}.generation-banner span{display:inline-flex}.surface-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.55rem;margin:.75rem 0}.surface-card{background:#fff;border:1px solid #dbe3ef;border-radius:.75rem;padding:.65rem}.surface-card strong{display:block;margin-bottom:.25rem;line-height:1;font-size:1.45rem}.surface-card span{display:block;line-height:1.2;font-weight:700}.surface-card small{display:block;margin-top:.3rem;line-height:1.25;color:#64748b}.surface-card.info{border-color:#bfdbfe;background:#eff6ff}.surface-card.primary{border-color:#c7d2fe;background:#eef2ff}.surface-card.secondary{background:#f8fafc}.surface-card.muted{background:#f1f5f9;color:#475569}.surface-card.info strong,.surface-card.primary strong{color:#1d4ed8}.surface-card.muted strong{color:#475569}.filter-panel{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:.55rem}.quick-filter-bar{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;margin:.65rem 0}.quick-filter-chip{border:1px solid #cbd5e1;border-radius:999px;background:#f8fafc;color:#1d4ed8;font-weight:800;cursor:pointer}.quick-filter-chip.is-active{background:#1d4ed8;color:#fff;border-color:#1d4ed8}.inventory-clear-all{border:1px solid #cbd5e1;border-radius:.45rem;background:#fff;color:#1d4ed8;font-weight:800}.filter-field{display:flex;flex-direction:column;font-weight:700;font-size:.82rem}input,select,button{padding:.42rem .5rem;border:1px solid #dbe3ef;border-radius:.45rem;background:#fff}.export-toolbar{display:flex;flex-direction:column;gap:.65rem;align-items:stretch;box-sizing:border-box;max-width:100%;margin:.75rem 0}.toolbar-card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,18rem),1fr));gap:.65rem}.toolbar-card{box-sizing:border-box;min-width:0;padding:.65rem .75rem;border:1px solid #dbe3ef;border-radius:.75rem;background:#f1f5f9}.toolbar-card--selection,.toolbar-card--prompt{display:flex;flex-direction:column;gap:.55rem}.toolbar-row{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;max-width:100%;min-width:0}.toolbar-field{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center;max-width:100%;min-width:0;font-weight:700}.toolbar-field select{max-width:100%;min-width:0}.toolbar-help,.group-help{color:#475569;font-weight:400}.toolbar-group{display:flex;flex-wrap:wrap;gap:.5rem 1rem;align-items:center;max-width:100%;min-width:0}.toolbar-group>div{min-width:0}.toolbar-group .toolbar-row{flex:1 1 16rem}.toolbar-row button{white-space:normal}.primary-action,.danger-action:not(:disabled){background:#1d4ed8;color:#fff;border-color:#1d4ed8}.danger-action:not(:disabled){background:#b91c1c;border-color:#b91c1c}button:disabled,.danger-action:disabled{background:#e5e7eb;color:#94a3b8;border-color:#cbd5e1;cursor:not-allowed}.table-wrap{overflow:auto;background:#fff;border:1px solid #dbe3ef}table{width:100%;min-width:1500px;border-collapse:collapse}th,td{padding:.42rem .45rem;border-bottom:1px solid #dbe3ef;text-align:left;font-size:.84rem;vertical-align:top}.tag,.badge{display:inline-flex;align-items:center;margin:.06rem;padding:.12rem .42rem;border-radius:999px;background:#e0e7ff;color:#3730a3;font-size:.69rem;font-weight:800;line-height:1.2}.badge.issue{background:#fee2e2;color:#991b1b}.badge.warn{background:#fef3c7;color:#92400e}.badge.keep{background:#dcfce7;color:#166534}.badge.muted{background:#e2e8f0;color:#475569}.priority-high{background:#fee2e2;color:#991b1b}.priority-medium,.priority-review{background:#fef3c7;color:#92400e}.priority-low{background:#e0f2fe;color:#075985}.priority-protect{background:#dcfce7;color:#166534}.priority-help ul{margin:.35rem 0 .15rem 1.1rem;padding:0}.priority-help li{margin:.12rem 0}.manual-copy{width:100%;min-height:8rem}@media(max-width:720px){main,header{padding:.75rem}.generation-banner{width:auto;border-radius:.75rem}.toolbar-card-grid{grid-template-columns:1fr}.toolbar-row,.toolbar-group{align-items:stretch}.toolbar-field,.toolbar-group{flex-direction:column}.toolbar-field select{width:100%}.toolbar-help{display:block}.toolbar-group .toolbar-row{flex:1 1 auto;flex-direction:row}.toolbar-group .toolbar-row button{flex:1 1 9rem}}</style></head><body><header><h1>Callable Inventory</h1><p>Search callables, inspect health signals, and export focused AI refactor plans.</p><!--CALLABLE_GENERATION_BANNER--><p><a href="callable-functions-dashboard.html">Architecture</a> - <a href="../reference/_data/callable-flow.json">Open JSON data</a></p></header><main><section id="inventorySummaryCards" class="surface-cards" aria-label="Callable inventory summary"></section><p><small>Callable metrics are generated from the callable inventory data.</small></p><section class="filter-panel" aria-label="Inventory quick controls"><label class="filter-field">Search all callables <input id="searchBox" type="search"></label><button id="resetFilters" class="inventory-clear-all" type="button" hidden>Clear all filters</button></section><section class="quick-filter-bar" aria-label="Quick filters"><button type="button" class="quick-filter-chip is-active" data-quick-filter="all">All</button><button type="button" class="quick-filter-chip" data-quick-filter="public_api">Public API</button><button type="button" class="quick-filter-chip" data-quick-filter="supporting">Supporting</button><button type="button" class="quick-filter-chip" data-quick-filter="review_candidates">Review candidates</button><button type="button" class="quick-filter-chip" data-quick-filter="healthy">Healthy</button><button type="button" class="quick-filter-chip" data-quick-filter="selected">Selected</button></section><section class="toolbar-card architecture-note" aria-label="Architecture inventory note"><strong>Architecture inventory</strong><p>Use this inventory to find public callables, supporting helpers, health signals, and refactor candidates.</p></section><section class="export-toolbar"><div class="toolbar-card-grid"><div class="toolbar-card toolbar-card--selection" aria-label="Selection"><strong id="selectedCount">Selected: 0 callables</strong><div class="toolbar-row"><button id="selectVisible" class="primary-action" type="button">Select visible</button><button id="clearSelected" class="danger-action" type="button" disabled>Clear selection</button></div></div><div class="toolbar-card toolbar-card--compatibility"><label class="toolbar-field">Compatibility mode <select id="compatibilityMode"><option value="internal_cleanup" selected>Internal cleanup</option><option value="stable_api_safe">Stable API safe</option><option value="development_breaking_allowed">Development breaking allowed</option></select><small class="toolbar-help">Sets the API safety assumptions for generated refactor packages.</small></label></div></div><div class="toolbar-card toolbar-card--prompt"><div class="toolbar-group"><div><strong>AI prompt</strong><br><small class="group-help">Export selected callables for AI-assisted refactor planning.</small></div><div class="toolbar-row"><button id="copyJson" type="button" disabled>Copy JSON</button><button id="copyMarkdown" type="button" disabled>Copy Markdown</button><button id="downloadJson" type="button" disabled>Download JSON</button></div></div><small id="exportStatus"></small><textarea id="manualCopy" class="manual-copy" hidden readonly></textarea></div></section><p id="resultCount"></p><p id="dataLoadStatus" class="load-status" aria-live="polite">Loading callable-flow data...</p><section class="table-wrap"><table data-table-controls="excel"><thead><tr><th>Select<br><input id="selectAllVisible" type="checkbox"></th><th>Callable</th><th>File / Area</th><th>Public API</th><th>Health</th><th>Finding</th><th>Review note</th><th>Suggested action</th><th>Downstream</th><th>Depth</th></tr></thead><tbody id="inventoryBody"></tbody></table></section></main><script>
const DISPLAY_LABEL_MAP={'None':'Healthy','Architecture violation':'Architecture violation','Long call chain':'Long call chain','Large dependency surface':'Large dependency surface','Merge candidate':'Merge candidate','Review abstraction':'Review abstraction','Shared utility':'Shared utility'};let inventory=[],visibleRows=[],summaryCounts={};const state={search:'',quickFilter:'all',selected:new Set()};const $=id=>document.getElementById(id),text=v=>String(v??''),esc=v=>text(v).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));const COMPATIBILITY_INSTRUCTIONS={internal_cleanup:'Preserve public API behavior. Internal helpers may be renamed, moved, privatized, inlined, or simplified when tests and callers remain valid.',stable_api_safe:'Treat public behavior and documented contracts as stable. Prefer additive or internal-only changes and avoid breaking notebook-facing APIs.',development_breaking_allowed:'Breaking changes are allowed only when they clearly simplify the design; update callers, tests, and documentation in the same change.'};function selectedItems(){return inventory.filter(row=>state.selected.has(row.qualified_name))}function publicStatus(r){return r.layer==='public'||r.function_type==='Public function'?'Public':'Supporting'}function fileArea(r){return r.owner_file||r.source_path||r.docs_path||r.module||''}function healthLabel(r){const action=displayLabel(r.recommended_action||'None'),priority=text(r.priority||'');return ['Keep public','Shared utility','Shared internal helper','Protect public API','Healthy'].includes(action)&&!['High','Medium','Review'].includes(priority)?'Healthy':'Review candidate'}function findingLabelForRow(r){const action=displayLabel(r.recommended_action||'None');return action==='Healthy'?'Healthy':action}function reviewNote(r){const signals=r.signals||[];return signals.length?signals.join(', '):'Clear'}function downstreamCount(r){return Number(r.called_by_count??0)}function depthValue(r){return Number(r.calls_count??0)}function exportItem(r){return{qualified_name:r.qualified_name,function_name:r.function_name,callable:r.function_name,file_area:fileArea(r),public_api:publicStatus(r),health:healthLabel(r),finding:findingLabelForRow(r),review_note:reviewNote(r),suggested_action:displayLabel(r.recommended_action||'Keep public'),downstream_count:downstreamCount(r),depth:depthValue(r),source_url:r.source_url,signals:r.signals}}function refactorContext(callables){const mode=$('compatibilityMode').value;return{compatibility_mode:mode,compatibility_instruction:COMPATIBILITY_INSTRUCTIONS[mode]}}function batchAccounting(callables){return{selected_callable_count:callables.length,planned_batch_count:callables.length,completed_or_refactored_count:'fill in after implementation',remaining_selected_count:'fill in after implementation',deferred_selected_callables:'fill in after implementation'}}function refactorPacket(){const callables=selectedItems().map(exportItem);return{schema:'fabricops_callable_refactor_packet',callables,functions:callables,batch_accounting:batchAccounting(callables),refactor_context:refactorContext(callables),ai_prompt:'Review selected callables'}}function mdField(label,value){const v=Array.isArray(value)?value.join(', '):(value??'');return `- ${label}: ${v||'None'}`}function callableMarkdown(item){return [`### ${item.qualified_name}`,mdField('callable',item.callable||item.function_name),mdField('file_area',item.file_area),mdField('public_api',item.public_api),mdField('health',item.health),mdField('finding',item.finding),mdField('review_note',item.review_note),mdField('suggested_action',item.suggested_action),mdField('downstream_count',item.downstream_count),mdField('depth',item.depth),mdField('source_url',item.source_url),mdField('signals',item.signals)].join('
')}function markdownPacket(packet){return `# Callable refactor packet\n\n## Objective\nReview and refactor the selected FabricOps callables to improve maintainability, simplify long call chains, review architecture findings, and preserve expected public behavior.\n\n## Architecture intent\n- Keep the public API surface small and clear.\n- Public API callables may be heavier if that makes the code easier to follow.\n- Prefer public functions calling internal functions; supporting objects may be used freely.\n- Avoid long helper chains.\n- Merge small helper into parent when readability improves.\n- Move helpers closer to their caller when they are not genuinely reusable.\n- Keep genuinely shared utilities stable and generic.\n- Do not casually change public API behavior.\n\n## Compatibility mode\n- selected mode: ${packet.refactor_context.compatibility_mode}\n- instruction: ${packet.refactor_context.compatibility_instruction}\n\n## Selected callables\n${packet.callables.map(callableMarkdown).join('\n\n')}\n\n## Requested work\nFor each selected callable:\n1. Inspect the callable and its direct/downstream dependencies.\n2. Decide whether to keep public, flatten internals, merge candidates, move helper closer to caller, or review architecture findings.\n3. Preserve external behavior unless compatibility mode explicitly allows breaking changes.\n4. Prefer simpler, flatter code over long helper chains.\n5. Keep supporting helper tags descriptive without treating them as architecture layers.\n6. Update or add tests where needed.\n7. Avoid broad unrelated refactors.\n\n## Output required from AI\nReturn:\n- Summary of changes\n- Callables changed\n- Callables intentionally left unchanged\n- Tests added/updated\n- Risks\n- Remaining follow-up items\n- Batch accounting: completed, deferred, remaining\n\n## Batch accounting\n- selected_callable_count: ${packet.batch_accounting.selected_callable_count}\n- planned_batch_count: ${packet.batch_accounting.planned_batch_count}\n- completed_or_refactored_count: fill in after implementation\n- remaining_selected_count: fill in after implementation\n- deferred_selected_callables: fill in after implementation\n`;}async function copyExport(format){const packet=refactorPacket();const value=format==='markdown'?markdownPacket(packet):JSON.stringify(packet,null,2);try{await navigator.clipboard.writeText(value);$('exportStatus').textContent=`Copied ${format}.`;$('manualCopy').hidden=true}catch(e){$('manualCopy').hidden=false;$('manualCopy').value=value;$('exportStatus').textContent='Clipboard unavailable; copy from the text area.'}}function downloadJson(){const blob=new Blob([JSON.stringify(refactorPacket(),null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='fabricops-callable-refactor-packet.json';a.click()}function unique(v){return[...new Set(v.filter(Boolean))].sort()}function displayLabel(v){return DISPLAY_LABEL_MAP[text(v)]||text(v)}function label(v){return displayLabel(text(v).replace(/_/g,' ').replace(/\b\w/g,ch=>ch.toUpperCase()))}function option(s,v,l){const o=document.createElement('option');o.value=v;o.textContent=l||v;s.appendChild(o)}const GITHUB_SOURCE_BASE='https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/';function sourceHref(i){if(i.docs_path)return '../'+String(i.docs_path).replace(/^docs\//,'').replace(/\.md$/,'/');if(i.source_url)return i.source_url;const path=i.source_path;if(!path)return '';const start=i.source_start_line;const end=i.source_end_line;let anchor=start?`#L${start}`:'';if(start&&end&&end!==start)anchor+=`-L${end}`;return GITHUB_SOURCE_BASE+path+anchor}function sourceCallableLink(i){const href=sourceHref(i);const label=esc(i.function_name);return href?`<a class="source-link" href="${esc(href)}" target="_blank" rel="noopener"><code>${label}</code></a>`:`<code>${label}</code>`}function renderInventoryCards(){const total=inventory.length,publicCount=inventory.filter(i=>publicStatus(i)==='Public').length,supportingCount=total-publicCount,reviewCount=inventory.filter(i=>healthLabel(i)==='Review candidate').length,healthyCount=inventory.filter(i=>healthLabel(i)==='Healthy').length,cards=[{label:'Total callables',value:total,subtitle:'All callables in the architecture inventory.',cls:'info'},{label:'Public callables',value:publicCount,subtitle:'Notebook-facing API entrypoints.',cls:'primary'},{label:'Supporting callables',value:supportingCount,subtitle:'Helpers and implementation callables.',cls:'secondary'},{label:'Review candidates',value:reviewCount,subtitle:'Callables with findings or refactor signals.',cls:reviewCount?'review':'secondary'},{label:'Healthy callables',value:healthyCount,subtitle:'Callables with clear health signals.',cls:'muted'}];$('inventorySummaryCards').innerHTML=cards.map(c=>`<article class="surface-card ${esc(c.cls)}"><strong>${esc(c.value??0)}</strong><span>${esc(c.label)}</span><small>${esc(c.subtitle)}</small></article>`).join('')}function populateFilters(){}function matchesQuickFilter(i){if(state.quickFilter==='public_api')return publicStatus(i)==='Public';if(state.quickFilter==='supporting')return publicStatus(i)==='Supporting';if(state.quickFilter==='review_candidates')return healthLabel(i)==='Review candidate';if(state.quickFilter==='healthy')return healthLabel(i)==='Healthy';if(state.quickFilter==='selected')return state.selected.has(i.qualified_name);return true}function filteredRows(){const q=state.search.toLowerCase();return inventory.filter(i=>(!q||text(i.function_name).toLowerCase().includes(q)||text(i.qualified_name).toLowerCase().includes(q)||text(fileArea(i)).toLowerCase().includes(q))&&matchesQuickFilter(i))}function updateQuickFilterChips(){document.querySelectorAll('[data-quick-filter]').forEach(button=>button.classList.toggle('is-active',button.dataset.quickFilter===state.quickFilter));$('resetFilters').hidden=state.search===''&&state.quickFilter==='all'}function updateExportControls(){$('selectedCount').textContent=`Selected: ${state.selected.size} callables`;['copyJson','copyMarkdown','downloadJson'].forEach(id=>$(id).disabled=state.selected.size===0);$('clearSelected').disabled=state.selected.size===0;if($('selectAllVisible'))$('selectAllVisible').checked=visibleRows.length>0&&visibleRows.every(r=>state.selected.has(r.qualified_name))}function resultCountText(){const total=summaryCounts.total_callables??inventory.length;return `Showing ${visibleRows.length} callable records of ${total} total discovered callable records.`}function healthBadge(i){const health=healthLabel(i);return `<span class="badge ${health==='Healthy'?'keep':'warn'}">${esc(health)}</span>`}function findingBadge(i){const finding=findingLabelForRow(i);return `<span class="badge ${finding==='Healthy'?'keep':'warn'}">${esc(finding)}</span>`}function suggestedActionCell(i){const action=displayLabel(i.recommended_action||'Keep public');return esc(action)}function renderLoadStatus(message,isError=false){$('dataLoadStatus').textContent=message;$('dataLoadStatus').classList.toggle('error',Boolean(isError))}function renderTable(){visibleRows=filteredRows();$('resultCount').textContent=resultCountText();renderLoadStatus(visibleRows.length?`Loaded ${inventory.length} callable records`:(inventory.length?'No callable records match current filters':'Loading callable-flow data...'));updateQuickFilterChips();$('inventoryBody').innerHTML=visibleRows.map(i=>`<tr><td><input type="checkbox" data-select-row="${esc(i.qualified_name)}" ${state.selected.has(i.qualified_name)?'checked':''}></td><td>${sourceCallableLink(i)}</td><td>${esc(fileArea(i))}</td><td>${esc(publicStatus(i))}</td><td>${healthBadge(i)}</td><td>${findingBadge(i)}</td><td>${esc(reviewNote(i))}</td><td>${suggestedActionCell(i)}</td><td>${esc(downstreamCount(i))}</td><td>${esc(depthValue(i))}</td></tr>`).join('');updateExportControls();if(window.FabricOpsTableControls)window.FabricOpsTableControls.enhance(document.querySelector('table[data-table-controls="excel"]'))}$('searchBox').addEventListener('input',e=>{state.search=e.target.value;renderTable()});document.addEventListener('click',e=>{const chip=e.target.closest('[data-quick-filter]');if(!chip)return;state.quickFilter=chip.dataset.quickFilter;renderTable()});$('resetFilters').onclick=()=>{state.search='';state.quickFilter='all';$('searchBox').value='';if(window.FabricOpsTableControls)window.FabricOpsTableControls.resetAll(document);renderTable()};document.addEventListener('change',e=>{const r=e.target.closest('[data-select-row]');if(r){r.checked?state.selected.add(r.dataset.selectRow):state.selected.delete(r.dataset.selectRow);updateExportControls()}});$('selectAllVisible').onchange=e=>{e.target.checked?visibleRows.forEach(r=>state.selected.add(r.qualified_name)):visibleRows.forEach(r=>state.selected.delete(r.qualified_name));renderTable()};$('selectVisible').onclick=()=>{visibleRows.forEach(r=>state.selected.add(r.qualified_name));renderTable()};$('clearSelected').onclick=()=>{state.selected.clear();renderTable()};$('copyJson').onclick=()=>copyExport('json');$('copyMarkdown').onclick=()=>copyExport('markdown');$('downloadJson').onclick=downloadJson;async function loadData(){const attemptedUrl='../reference/_data/callable-flow.json';try{const response=await fetch(attemptedUrl);if(!response.ok)throw new Error(`HTTP ${response.status} ${response.statusText}`);const data=await response.json();inventory=data.function_inventory||[];summaryCounts=data.summary_counts||{};renderInventoryCards();populateFilters();renderTable()}catch(error){renderInventoryCards();renderLoadStatus(`Failed to load callable-flow data: ${error&&error.message?error.message:String(error)}`,true)}}loadData();
</script><script src="../javascripts/table-controls.js"></script></body></html>
""".replace("<!--CALLABLE_GENERATION_BANNER-->", generation_banner)

def _render_callable_flow_page(flow_data: dict[str, Any]) -> str:
    """Render the global callable flow Markdown page."""
    del flow_data
    return '''# Callable Flow Dashboard

AI coding tools make it easy to add callables quickly. That speed is useful, but it can also create too many entry points, thin wrapper callables, nested helpers, and uncontrolled dependencies. The Callable Flow Dashboard exists to make those relationships visible before the codebase becomes hard to maintain.

<div align="center" markdown="1">

[Architecture](../assets/callable-functions-dashboard.html){ .md-button .md-button--primary }
[Inventory](../assets/callable-functions-inventory.html){ .md-button }

</div>


## Why callable flow matters

FabricOps keeps notebook-facing APIs small and explainable. A callable should have a clear role in the role-aware callable model:

```text
Public functions → Internal functions (supporting objects allowed)
```

Callable review is function-layer focused. Internal-to-internal calls are valid, public functions may call internal functions, and supporting objects are allowed dependencies. The current classifier still keeps helper tags such as adapters, validators, utilities, model classes, lifecycle methods, property accessors, reachability kinds, and dependency roles for review context, but those tags are not architecture layers.

The intent is:

- Public functions should remain stable notebook-facing surfaces.
- Internal functions may orchestrate implementation helpers.
- Classes, dataclasses, enums, constants, protocols, config objects, validators, resolvers, adapters, utilities, models, lifecycle methods, and property accessors are supporting context rather than architecture layers.
- Architecture violations are limited to public-function-to-public-function and internal-function-to-public-function call edges.

This keeps public callables stable, lets purposeful internal implementation roles collaborate, and avoids treating object usage as a boundary issue.

## How the dashboard is generated

The dashboard is built from repository scans that inspect callable definitions and relationships. The scan produces compact dashboard contract data in [`_data/callable-flow.json`](_data/callable-flow.json), containing only fields used by the Architecture and Inventory dashboards for caller and callee relationships, roles, reachability, reuse, layer consistency, and refactor recommendations.

Because the dashboard is generated from the codebase, it is a maintenance aid rather than a separate source of truth. Use it to decide where to inspect source code, update docstrings, flatten helper chains, or preserve shared helpers carefully.

## What the dashboard detects

Use the dashboard signals to find patterns that deserve review:

- workflow-to-workflow coupling
- utilities depending on project workflows
- validators/resolvers/models depending upward on workflows
- unknown or classification-pending roles
- unreachable or orphan candidates
- thin wrapper or inline candidates
- single-use helpers that need abstraction review
- high fanout helpers that should be protected
- implicit lifecycle and property accessor methods that should not be treated as ordinary orphans

## Refactor signals

Refactor signals are warnings generated from the callable graph. They do not automatically mean the code is wrong. Instead, they help guard against architecture drift from the role-aware callable model and identify where cleanup should be reviewed before changes are made.

### EG. Pointless wrapper

![Possible wrapper or inline candidates](../assets/fabricops-bad-example-pointless-wrapper-functions.png)

*Guardrail: Warn when a helper appears to add little abstraction value. Single-use or thin wrapper callables may still be valid, but they should earn their place through clearer naming, validation, readability, or reuse.*

### EG. Large dependency surface

![Large dependency surface](../assets/fabricops-bad-example-large-surface-area.png)

*Guardrail: Warn when a public callable depends on many nested helpers. This may be valid orchestration, but it increases the chance that a small helper change breaks a wider workflow.*

### EG. Messy callable dependency

![Public callable dependency](../assets/fabricops-bad-example-function-dependancy.png)

*Guardrail: Warn when one public callable depends on another public callable. Public callables should usually be entry points. Shared logic should usually move into an internal workflow, service, adapter, validator, resolver, normalizer, or utility according to its role.*

### EG. Nested helper chain

![Nested helper chain](../assets/fabricops-bad-example-nested-functions.png)

*Guardrail: Repeated workflow-to-workflow chains or upward dependency patterns need review because they make orchestration harder to reason about. Allowed internal role calls can be valid when validators, resolvers, normalizers, adapters, services, utilities, models, lifecycle hooks, or property accessors support the intended lower-level direction.*

## Selecting refactor candidates

![Selecting refactor candidates](../assets/fabricops-select-refactor-candidates.png)

*Selecting a focused cleanup set.*

The dashboard supports selecting callables with refactor signals so users can build a focused cleanup set. This narrows review to specific architecture guardrails instead of asking AI tools to reason over the whole codebase at once.

## Exporting an AI refactor prompt

![Exporting an AI refactor prompt](../assets/fabricops-select-refactor-candidates-prompt-export.png)

*Exporting a structured AI refactor packet.*

Selected callables can be exported as a structured AI refactor packet. The export keeps callable_role_detail, dependency_role, callable kind, counts, raw classifications, compatibility mode, safety constraints, batch accounting, completion accounting, and expected output available for advanced review so AI tools can reason from architecture context instead of guessing from isolated code snippets.

## Inventory terms

- Role group = broad job of the callable.
- Role detail = specific detected purpose.
- Reachability = whether it can be reached from public or notebook-facing API.
- Findings / Signal = review hints or actions, not automatic refactor commands.
- Priority = triage order, not a guarantee something must be changed.

??? example "Example exported AI refactor packet"

    ```text
    FabricOps callable refactor packet

    Prompt for AI

    Review the assigned function layer against the usage evidence. Architecture findings use only function-to-function calls: public functions should not call public functions, and internal functions should not call public functions. Do not treat classes, dataclasses, enums, constants, protocols, config objects, lifecycle hooks, property accessors, or other supporting objects as architecture-layer violations. Respect compatibility mode, batch accounting, and completion accounting.

    Refactor context

    Compatibility mode: Internal cleanup

    Batch accounting

    Selected callables: 1
    Planned batch count: 1
    Completed/refactored count: fill in after implementation
    Remaining selected count: fill in after implementation

    Selected callables

    Callable 1: _audit_timestamp_expr

    Qualified name: fabricops_kit.config._audit_timestamp_expr
    Module: config
    Kind: function
    Layer: Internal function
    Callable role: internal_adapter, shared_internal_service
    Architectural role: shared_internal_service
    Reachability kind: public_api_reachable
    Dependency role: shared_internal_service
    Change risk: Medium
    Refined recommended action: Review role-aware dependency direction
    Used by count: 1
    Calls count: 1
    Layer consistency: Role-aware review needed
    Layer consistency key: role_review
    Review status: Classified
    Review status key: classified
    Recommended action: Architecture violation
    Architecture signals: workflow_calls_workflow
    Review signals: allowed_internal_role_call
    Callers:
    - profile_dataframe (data_profiling)
    Callees:
    - _get_audit_timezone (config)
    Direct internal helpers:
    - _get_audit_timezone (config)
    ```

## Conclusion

The Callable Flow Dashboard is not only a dependency viewer. It is an architecture guardrail for keeping FabricOps maintainable as the kit grows. The main rule is function-layer focused: public functions should remain stable notebook-facing surfaces, public functions may call internal functions, and internal functions should not call public functions. Supporting objects and helper role tags provide review context without becoming architecture layers or boundary violations.

The exported refactor packet gives AI tools enough context to reason safely from the call graph instead of guessing from isolated code snippets. This makes the workflow useful for planned refactors, code review, and future architecture governance.
'''


def _indent_markdown(lines: list[str], spaces: int = 4) -> list[str]:
    """Indent every physical Markdown line for MkDocs Material blocks."""
    prefix = " " * spaces
    indented: list[str] = []
    for item in lines:
        physical_lines = item.split("\n")
        indented.extend("" if line == "" else f"{prefix}{line}" for line in physical_lines)
    return indented


def _helper_area(helper_name: str, purpose: str) -> tuple[str, str]:
    """Return the implementation area and plain-English role for an internal helper."""
    haystack = f"{helper_name} {purpose}".lower()
    if helper_name in {"_guardrail_exclude_columns", "_get_profiled_columns"} or "exclude_columns" in haystack:
        return "Column handling", "Select, exclude, and normalize column names used by the callable."
    if helper_name in {
        "_catalogue_value",
        "_comparable_value",
        "_is_greater_than",
        "_is_less_than",
        "_latest_catalogue_behavior_profile_row",
        "_profile_row_count",
        "_profile_watermark_bounds",
        "_row_to_dict",
        "_string_value",
    }:
        return "Profile comparison", "Compare current evidence with accepted profile values and behavior baselines."
    if any(token in haystack for token in ("audit", "timestamp", "timezone")):
        return "Audit timestamp", "Resolve and stamp audit time consistently."
    if any(
        token in haystack
        for token in ("metadata", "load", "table", "database", "registered", "warehouse", "lakehouse")
    ):
        return "Metadata loading", "Load and identify the metadata or table context needed by the callable."
    if any(token in haystack for token in ("valid", "required", "check", "ensure")):
        return "Validation", "Validate inputs and guard conditions before the workflow continues."
    if any(token in haystack for token in ("parse", "normalise", "normalize", "canonical", "json", "name")):
        return "Rule parsing", "Normalize stored or user-provided values before applying rules."
    if any(token in haystack for token in ("rule", "condition", "evaluate", "sql", "dq", "expectation")):
        return "Rule evaluation", "Convert configured rules into executable checks and evaluation results."
    if any(token in haystack for token in ("summary", "summar", "status", "failed", "message", "result")):
        return "Result summary", "Build final statuses, counts, and messages for the caller."
    if any(token in haystack for token in ("spark", "fabric", "session")):
        return "Fabric or Spark access", "Access Fabric or Spark runtime services used by the implementation."
    return "Other", "Support lower-level implementation details that do not fit the main helper areas."


def _ordered_helper_areas(area_names: Iterable[str]) -> list[str]:
    """Sort helper areas in the documented reference order."""
    preferred = [
        "Audit timestamp",
        "Metadata loading",
        "Validation",
        "Rule parsing",
        "Profile comparison",
        "Column handling",
        "Rule evaluation",
        "Result summary",
        "Fabric or Spark access",
        "Other",
    ]
    rank = {name: index for index, name in enumerate(preferred)}
    return sorted(area_names, key=lambda name: (rank.get(name, len(preferred)), name.lower()))


def _helper_area_purposes(area_names: list[str]) -> str:
    """Return a compact human-readable list of grouped helper purposes."""
    labels = [name.lower() for name in area_names]
    if not labels:
        return "implementation support"
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} and {labels[1]}"
    return f"{', '.join(labels[:-1])}, and {labels[-1]}"


def _helper_chip(helper: dict[str, Any]) -> str:
    """Return a wrapped, clickable helper chip for grouped implementation summaries."""
    source_location = helper["source_location"]
    source_url = github_source_url(
        helper["source_path"],
        source_location.get("start_line"),
        source_location.get("end_line"),
    )
    return (
        f'<a class="reference-helper-chip" href="{html_escape(source_url)}">'
        f'<code>{html_escape(helper["name"])}</code>'
        "</a>"
    )


def _render_helper_group_cards(grouped: dict[str, dict[str, Any]], area_order: list[str]) -> list[str]:
    """Render internal helpers as responsive grouped cards instead of a wide table."""
    lines = ['<div class="reference-helper-groups">']
    for area in area_order:
        helpers = grouped[area]["helpers"]
        lines.extend(
            [
                '  <section class="reference-helper-group">',
                f'    <h4>{html_escape(area)}</h4>',
                f'    <p>{html_escape(grouped[area]["role"])}</p>',
                '    <div class="reference-helper-chip-wrap">',
            ]
        )
        for helper in helpers:
            lines.append(f"      {_helper_chip(helper)}")
        lines.extend(["    </div>", "  </section>"])
    lines.append("</div>")
    return lines


def _helper_group_summary_lines(
    root_qn: str,
    helper_qns: list[str],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
) -> list[str]:
    """Render grouped helper cards for internal helpers used by a callable."""
    root_name = node_by_qn[root_qn]["callable_name"]
    helper_count = len(helper_qns)
    if not helper_qns:
        return [
            (
                f"This callable uses 0 internal helpers; `{root_name}` does not have package-local "
                "helper descendants in the generated call graph."
            ),
            "",
            '<div class="reference-helper-groups">',
            '  <section class="reference-helper-group reference-helper-group-empty">',
            '    <h4>No internal helpers detected</h4>',
            '    <p>This callable does not have package-local helper descendants in the generated call graph.</p>',
            "  </section>",
            "</div>",
        ]

    grouped: dict[str, dict[str, Any]] = {}
    for helper_qn in helper_qns:
        helper_node = node_by_qn[helper_qn]
        helper_name = helper_node["callable_name"]
        module_name = helper_node["module_name"]
        info = module_data[module_name]
        purpose = info.get("functions", {}).get(helper_name) or "Internal helper used by the package implementation."
        area, role = _helper_area(helper_name, purpose)
        grouped.setdefault(area, {"role": role, "helpers": []})["helpers"].append(
            {
                "name": helper_name,
                "module_name": module_name,
                "source_path": f"src/fabricops_kit/{module_name}.py",
                "source_location": info.get("source_locations", {}).get(helper_name, {}),
            }
        )

    area_order = _ordered_helper_areas(grouped)
    for area in area_order:
        grouped[area]["helpers"] = sorted(grouped[area]["helpers"], key=lambda item: item["name"].lower())

    return [
        f"This callable uses {helper_count} internal helpers for {_helper_area_purposes(area_order)}.",
        "",
        *_render_helper_group_cards(grouped, area_order),
    ]


def _render_nested_helper_section(
    root_qn: str,
    helper_qns: list[str],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
) -> list[str]:
    """Render a collapsed grouped summary for internal helpers used by a callable."""
    return [
        f'??? info "Internal helpers used: {len(helper_qns)}"',
        "",
        *_indent_markdown(_helper_group_summary_lines(root_qn, helper_qns, node_by_qn, module_data)),
    ]


def function_chip_wrap(chips: list[str]) -> str:
    """Return a mobile-friendly chip wrapper for a generated docs table cell."""
    if not chips:
        return "—"
    return '<span class="function-chip-wrap">' + "".join(chips) + "</span>"


def parse_simple_yaml(path: Path) -> dict[str, dict[str, Any]]:
    """Parse a small YAML subset used for function usage overrides."""
    data: dict[str, dict[str, Any]] = {}
    current_key: str | None = None
    current_list_key: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            if not line.endswith(":"):
                continue
            current_key = line[:-1].strip()
            data[current_key] = {}
            current_list_key = None
            continue
        if current_key is None:
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            if current_list_key:
                data[current_key].setdefault(current_list_key, []).append(stripped[2:].strip())
            continue
        if ":" in stripped:
            key, value = [p.strip() for p in stripped.split(":", 1)]
            if value == "":
                data[current_key][key] = []
                current_list_key = key
            else:
                data[current_key][key] = value
                current_list_key = None
    return data

def render_callable_map_page(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], module_summary: list[dict[str, Any]]) -> str:
    """Render callable map page."""
    module_edges = sorted(
        {
            (e["caller_qualified_name"].split(".")[-2], e["callee_qualified_name"].split(".")[-2])
            for e in edges
            if e["callee_qualified_name"] and e["edge_type"] == "cross_module"
        }
    )
    public_nodes = sorted([n for n in nodes if n["exported"]], key=lambda x: (x["module_name"], x["callable_name"]))
    helper_nodes = sorted([n for n in nodes if n["callable_name"].startswith("_")], key=lambda x: (x["module_name"], x["callable_name"]))
    cross_edges = sorted(
        [e for e in edges if e["callee_qualified_name"] and e["edge_type"] == "cross_module"],
        key=lambda x: (x["caller_qualified_name"], x["callee_qualified_name"]),
    )

    lines = [
        "# Callable Map (Developer Diagnostic)",
        "",
        "This page is generated from FabricOps source code using static AST parsing.",
        "",
        "> Developer diagnostic only. Primary user documentation now lives on Function Reference and module pages.",
        "",
        "## 1. Module dependency graph (diagnostic)",
        "",
        "```mermaid",
        "flowchart LR",
    ]
    for caller, callee in module_edges:
        lines.append(f"  {caller} --> {callee}")

    lines.extend(["```", "", "## 2. Public callables grouped by module", ""])
    by_mod: dict[str, list[str]] = {}
    for node in public_nodes:
        by_mod.setdefault(node["module_name"], []).append(node["callable_name"])
    for mod in sorted(by_mod):
        lines.append(f"- `{mod}`: " + ", ".join(f"`{n}`" for n in sorted(by_mod[mod])))

    ref_by: dict[str, set[str]] = {}
    for edge in edges:
        if edge["callee_qualified_name"]:
            ref_by.setdefault(edge["callee_qualified_name"], set()).add(edge["caller_qualified_name"])

    lines.extend(["", "## 3. Internal helper index", "", "| Module | Internal helper | Called by public callables |", "|---|---|---|"])
    public_qns = {n["qualified_name"] for n in public_nodes}
    for node in helper_nodes:
        qn = node["qualified_name"]
        callers = sorted([x for x in ref_by.get(qn, set()) if x in public_qns])
        lines.append(
            f"| `{node['module_name']}` | `{node['callable_name']}` | "
            f"{', '.join(f'`{x}`' for x in callers) or '—'} |"
        )

    lines.extend(["", "## 4. Cross-module FabricOps calls", "", "| Caller | Callee | Callee kind |", "|---|---|---|"])
    for edge in cross_edges:
        lines.append(
            f"| `{edge['caller_qualified_name']}` | `{edge['callee_qualified_name']}` | `{edge['callee_kind']}` |"
        )

    lines.extend([
        "",
        "## 5. Notes",
        "",
        "Per-function callable flows and helper/callee details are generated on each public callable page.",
    ])
    return "\n".join(lines) + "\n"


def _metadata_slug(table_name: str) -> str:
    """Return a stable markdown filename for a metadata table."""
    return table_name.lower()


def _default_reference_config() -> Any:
    """Return a minimal validated config for schema registry generation."""
    from types import SimpleNamespace

    from fabricops_kit.config import FrameworkConfig, NotebookRuntimeConfig, PathConfig

    metadata_store = SimpleNamespace(
        workspace_id="reference-workspace",
        item_id="reference-metadata-lakehouse",
        name="Reference Metadata Lakehouse",
        kind="lakehouse",
    )
    return FrameworkConfig(
        path_config=PathConfig(paths={"dev": {"metadata": metadata_store}}),
        notebook_runtime_config=NotebookRuntimeConfig(),
    )


_METADATA_TABLE_PURPOSES = {
    "METADATA_DATA_STEWARD": "Active and historical data steward records used by agreement intake.",
    "METADATA_DATA_AGREEMENT": "Agreement records that describe approved use, steward, recipient, and lifecycle context.",
    "METADATA_DATA_AGREEMENT_EVIDENCE": "Supporting agreement files and evidence metadata captured during agreement intake.",
    "METADATA_NOTEBOOK_REGISTRY": "Active notebook registration records linking notebooks to agreement, environment, dataset, and pipeline context.",
    "METADATA_DATA_CATALOGUE": "Observed table and column profile evidence. This is runtime evidence, not approved guardrail intent.",
    "METADATA_ENRICHMENT_RULES": "Append-only enrichment and business metadata intent authored and reviewed through governance workflows.",
    "METADATA_GUARDRAIL_RULES": "Approved or pending schema, freshness, profile behavior, and DQ guardrail intent.",
    "METADATA_GUARDRAIL_RESULTS": "Runtime guardrail outcomes written by pipeline enforcement.",
    "METADATA_DATA_LINEAGE_TABLE": "Source-to-target lineage evidence written by pipeline runs.",
    "METADATA_PIPELINE_RUNS": "Pipeline run summary evidence for execution, guardrail, lineage, and catalogue status.",
    "METADATA_DATA_ACCESS": "Externally collected access inventory for workspace, object, schema, and table access review.",
}

_METADATA_TABLE_RELATIONSHIPS = {
    "METADATA_DATA_STEWARD": {"templates": ["01_agreement.ipynb"], "written_by": ["widget_render_data_steward"], "read_by": ["widget_render_data_agreement", "widget_select_agreement"]},
    "METADATA_DATA_AGREEMENT": {"templates": ["01_agreement.ipynb", "02_pipeline.ipynb"], "written_by": ["widget_render_data_agreement"], "read_by": ["widget_select_agreement", "get_selected_agreement", "write_pipeline_run_summary"]},
    "METADATA_DATA_AGREEMENT_EVIDENCE": {"templates": ["01_agreement.ipynb"], "written_by": ["widget_render_agreement_evidence"], "read_by": ["widget_select_agreement"]},
    "METADATA_NOTEBOOK_REGISTRY": {"templates": ["02_pipeline.ipynb"], "written_by": ["widget_select_agreement"], "read_by": ["get_selected_agreement", "write_pipeline_lineage", "write_pipeline_run_summary"]},
    "METADATA_DATA_CATALOGUE": {
        "templates": ["02_pipeline.ipynb", "03_governance.ipynb", "99_explore.ipynb"],
        "written_by": ["run_table_guardrails"],
        "read_by": [
            "get_latest_metadata_catalogue",
            "widget_select_guardrail_target",
            "widget_review_guardrail_governance",
            "run_table_guardrails",
        ],
    },
    "METADATA_ENRICHMENT_RULES": {"templates": ["02_pipeline.ipynb", "03_governance.ipynb"], "written_by": ["widget_enrich_table_metadata", "widget_review_guardrail_governance"], "read_by": ["widget_review_guardrail_governance"]},
    "METADATA_GUARDRAIL_RULES": {"templates": ["02_pipeline.ipynb", "03_governance.ipynb"], "written_by": ["widget_author_schema_freshness_profile_rules", "widget_author_dq_rules", "widget_review_guardrail_governance"], "read_by": ["run_table_guardrails", "widget_review_guardrail_governance"]},
    "METADATA_GUARDRAIL_RESULTS": {"templates": ["02_pipeline.ipynb"], "written_by": ["run_table_guardrails"], "read_by": ["display_guardrail_results", "widget_review_guardrail_governance"]},
    "METADATA_DATA_LINEAGE_TABLE": {"templates": ["02_pipeline.ipynb"], "written_by": ["write_pipeline_lineage"], "read_by": ["widget_review_guardrail_governance"]},
    "METADATA_PIPELINE_RUNS": {"templates": ["02_pipeline.ipynb"], "written_by": ["write_pipeline_run_summary"], "read_by": ["widget_review_guardrail_governance"]},
    "METADATA_DATA_ACCESS": {"templates": ["External access-log inventory collection, not a FabricOps notebook template."], "written_by": [], "read_by": [], "related_step": "External inventory ingestion / governance access review."},
}


def _function_link(symbol: str, relative_prefix: str = "../") -> str:
    """Return a markdown link to a public page or module anchor for internal support."""
    if symbol in public_callable_names():
        return f"[`{symbol}`]({relative_prefix}api/reference/{symbol}.md)"
    metadata = parse_docs_metadata().get(symbol, {})
    module_name = canonical_public_module(str(metadata.get("module") or "data_agreement"))
    return f"[`{symbol}`]({relative_prefix}api/modules/{module_name}.md#{markdown_anchor(symbol)})"


def _format_symbol_list(symbols: list[str], relative_prefix: str = "../") -> str:
    """Return linked function names or a fallback label."""
    return ", ".join(_function_link(symbol, relative_prefix) for symbol in symbols) if symbols else "Not currently discoverable."


def _schema_rows(schema: Any) -> list[dict[str, str]]:
    """Return serializable rows from a Spark StructType-like object."""
    rows = []
    for field in getattr(schema, "fields", []):
        data_type = getattr(field, "dataType", "")
        if hasattr(data_type, "simpleString"):
            data_type_label = data_type.simpleString()
        else:
            data_type_label = str(data_type)
        rows.append({"name": str(field.name), "type": data_type_label, "required": "Nullable" if getattr(field, "nullable", True) else "Required"})
    return rows


def _metadata_registry_without_pyspark() -> dict[str, Any]:
    """Return schema registry with small Spark type stand-ins when PySpark is unavailable."""
    import sys
    import types

    class _Type:
        def __init__(self, label: str) -> None:
            self._label = label

        def simpleString(self) -> str:
            return self._label

    class StringType(_Type):
        def __init__(self) -> None:
            super().__init__("string")

    class LongType(_Type):
        def __init__(self) -> None:
            super().__init__("bigint")

    class DoubleType(_Type):
        def __init__(self) -> None:
            super().__init__("double")

    class BooleanType(_Type):
        def __init__(self) -> None:
            super().__init__("boolean")

    class TimestampType(_Type):
        def __init__(self) -> None:
            super().__init__("timestamp")

    class StructField:
        def __init__(self, name: str, dataType: Any, nullable: bool = True) -> None:
            self.name = name
            self.dataType = dataType
            self.nullable = nullable

    class StructType:
        def __init__(self, fields: list[Any]) -> None:
            self.fields = fields

        def fieldNames(self) -> list[str]:
            return [field.name for field in self.fields]

    pyspark = types.ModuleType("pyspark")
    sql = types.ModuleType("pyspark.sql")
    sql_types = types.ModuleType("pyspark.sql.types")
    for cls in (BooleanType, DoubleType, LongType, StringType, StructField, StructType, TimestampType):
        setattr(sql_types, cls.__name__, cls)
    sql.types = sql_types
    pyspark.sql = sql
    sys.modules.setdefault("pyspark", pyspark)
    sys.modules.setdefault("pyspark.sql", sql)
    sys.modules.setdefault("pyspark.sql.types", sql_types)

    from fabricops_kit.config import _get_metadata_table_schema_registry

    return _get_metadata_table_schema_registry(_default_reference_config())


def generate_metadata_table_reference() -> int:
    """Generate metadata table reference pages from implemented schema definitions.

    Returns
    -------
    int
        Number of metadata tables in the implemented schema registry.

    """
    try:
        from fabricops_kit.config import _get_metadata_table_schema_registry

        registry = _get_metadata_table_schema_registry(_default_reference_config())
    except RuntimeError as exc:
        if "pyspark.sql.types" not in str(exc):
            raise
        registry = _metadata_registry_without_pyspark()
    METADATA_REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    for old_page in METADATA_REFERENCE_DIR.glob("*.md"):
        old_page.unlink()

    index_lines = [
        "# List of Metadata Tables",
        "",
        "These pages are generated from the implemented metadata setup schema registry used by `00_env_config`.",
        "",
        '<figure class="metadata-model-image">',
        '  <img src="../../assets/fabricops-metadata-model.png" alt="FabricOps metadata model" />',
        "</figure>",
        "",
        '<div class="grid cards" markdown>',
        "",
    ]
    for table_name in sorted(registry):
        rel = _METADATA_TABLE_RELATIONSHIPS.get(table_name, {})
        templates = str(rel.get("related_step") or ", ".join(rel.get("templates", [])) or "Not currently discoverable.")
        purpose = _METADATA_TABLE_PURPOSES.get(table_name, "Implemented metadata table prepared by `00_env_config`.")
        slug = _metadata_slug(table_name)
        index_lines.extend(
            [
                f"-   **[{table_name}](metadata/{slug}.md)**",
                "",
                f"    {purpose}",
                "",
                f"    `{templates}`",
                "",
            ]
        )

        page = [
            f"# {table_name}",
            "",
            f"**Purpose:** {purpose}",
            "",
            "## Starter Kit usage",
            "",
            f"- **Written by notebook/template:** {', '.join(rel.get('templates', [])) or 'Not currently discoverable.'}",
            f"- **Written by function or widget:** {_format_symbol_list(rel.get('written_by', []), '../../')}",
            f"- **Read by function or widget:** {_format_symbol_list(rel.get('read_by', []), '../../')}",
            f"- **Related template step:** {rel.get('related_step') or ', '.join(rel.get('templates', [])) or 'Not currently discoverable.'}",
            "",
            "## Implemented schema",
            "",
            "| Column name | Data type | Nullable / required |",
            "| --- | --- | --- |",
        ]
        for row in _schema_rows(registry[table_name]):
            page.append(f"| `{row['name']}` | `{row['type']}` | {row['required']} |")
        page.extend(["", "## Related function reference", ""])
        symbols = sorted(set(rel.get("written_by", []) + rel.get("read_by", [])))
        if symbols:
            page.extend(f"- {_function_link(symbol, '../../')}" for symbol in symbols)
        else:
            page.append("- Not currently discoverable.")
        (METADATA_REFERENCE_DIR / f"{slug}.md").write_text("\n".join(page) + "\n", encoding="utf-8")

    index_lines.append("</div>")
    METADATA_REFERENCE_OVERVIEW.write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    return len(registry)


def _landing_count_text(count: int, label: str) -> str:
    """Return count text with aligned number and label markup."""
    return f"<strong>{count}</strong><span>{label}</span>"


def _landing_callable_support_text(supporting_functions: int, non_function_records: int) -> str:
    """Return landing-page callable support text from canonical inventory metrics."""
    return (
        f"Supported by <strong>{supporting_functions}</strong><span> functions and </span>"
        f"<strong>{non_function_records}</strong><span> non-function records</span>"
    )


def generate_landing_stats(
    *,
    public_exports: list[str],
    function_manifest: list[dict[str, Any]],
    metadata_table_count: int,
    callable_flow_data: dict[str, Any],
) -> dict[str, int]:
    """Write landing-page count data derived from canonical generated sources."""
    del function_manifest
    metrics = _callable_inventory_metrics(callable_flow_data)
    stats = {
        "public_function_count": metrics["public_api_entrypoints"],
        "total_callable_records": metrics["total_callables"],
        "function_callable_count": metrics["function_callables"],
        "supporting_function_count": metrics["supporting_functions"],
        "non_function_record_count": metrics["non_function_records"],
        "module_count": metrics["module_count"],
        "metadata_table_count": metadata_table_count,
    }
    LANDING_STATS_PATH.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    return stats


def update_landing_page_counts(stats: dict[str, int]) -> None:
    """Replace stable landing-page count tokens with generated count text."""
    text = LANDING_PAGE_PATH.read_text(encoding="utf-8")
    replacements = {
        "FABRICOPS_PUBLIC_FUNCTION_COUNT": _landing_count_text(
            stats["public_function_count"], " public callables"
        ),
        "FABRICOPS_CALLABLE_RECORD_COUNT": _landing_callable_support_text(
            stats["supporting_function_count"], stats["non_function_record_count"]
        ),
        "FABRICOPS_METADATA_TABLE_COUNT": _landing_count_text(stats["metadata_table_count"], "metadata tables"),
    }
    for token_name, value in replacements.items():
        start = f"<!-- {token_name} -->"
        end = f"<!-- /{token_name} -->"
        pattern = re.compile(f"{re.escape(start)}.*?{re.escape(end)}")
        replacement = f"{start}{value}{end}"
        text, count = pattern.subn(replacement, text, count=1)
        if count != 1:
            raise RuntimeError(f"Landing page is missing generated count token block: {token_name}")
    LANDING_PAGE_PATH.write_text(text, encoding="utf-8", newline="\n")

def main() -> None:
    """Run the command-line workflow."""
    REFERENCE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    public = parse_public_exports()
    module_data = {source_module_name(p): parse_module(p) for p in source_module_paths()}
    if "io.shared" in module_data:
        module_data["io"] = module_data["io.shared"]

    source_modules = set(module_data)
    discovered_modules = [module for module in MAJOR_IMPLEMENTATION_MODULE_ORDER if module in source_modules]

    docs_metadata = parse_docs_metadata()
    template_flow_docs = parse_template_flow_docs()
    module_docs_metadata = parse_module_docs_metadata()
    glossary = parse_glossary_metadata()
    _render_glossary_page(glossary)
    metadata_table_count = generate_metadata_table_reference()

    missing_metadata = sorted(name for name in public if name not in docs_metadata)
    if missing_metadata:
        raise RuntimeError("Missing PUBLIC_SYMBOL_DOCS entries for __all__ exports: " + ", ".join(missing_metadata))
    non_callable_exports = sorted(
        name for name in public if str(docs_metadata[name].get("function_type", "")).lower() != "callable"
    )
    if non_callable_exports:
        raise RuntimeError(
            "__all__ is the canonical callable surface; exported symbols must have "
            "PUBLIC_SYMBOL_DOCS function_type=callable: " + ", ".join(non_callable_exports)
        )
    unknown_glossary_terms = sorted(
        {term for metadata in docs_metadata.values() for term in metadata.get("glossary_terms", []) if term.lower() not in glossary}
    )
    if unknown_glossary_terms:
        raise RuntimeError("PUBLIC_SYMBOL_DOCS references unknown glossary terms: " + ", ".join(unknown_glossary_terms))

    # PUBLIC_SYMBOL_DOCS may retain metadata for internalized helpers so generated
    # implementation relationship details remain useful on public parent pages.

    symbol_map: dict[str, Symbol] = {}
    function_symbol_map: dict[str, Symbol] = {}
    for name in public:
        preferred_module = canonical_public_module(docs_metadata[name]["module"])
        preferred_actual_module = resolve_preferred_actual_module(preferred_module)
        modules_to_check = [preferred_actual_module] + [m for m in module_data if m != preferred_actual_module]
        for module in modules_to_check:
            info = module_data[module]
            if name in info["functions"]:
                symbol_map[name] = Symbol(name, module, preferred_module, "function", info["functions"][name])
                break
            if name in info["classes"]:
                symbol_map[name] = Symbol(name, module, preferred_module, "class", info["classes"][name])
                break
            if name in info["constants"]:
                symbol_map[name] = Symbol(name, module, preferred_module, "constant", info["constants"][name])
                break
        if name not in symbol_map:
            raise RuntimeError(f"Could not resolve exported symbol {name} to a module-level function/class.")

    for symbol in symbol_map.values():
        meta = docs_metadata[symbol.name]
        if meta["kind"] != symbol.obj_type:
            raise RuntimeError(f"Metadata kind mismatch for {symbol.name}: expected {symbol.obj_type}, found {meta['kind']}")
        symbol.summary = meta.get("summary_override") or symbol.summary
        symbol.purpose = meta.get("purpose") or symbol.summary or "—"
        enforce_placeholder_guard = symbol.actual_module in {"config", "ai"}
        if enforce_placeholder_guard and symbol.summary:
            _assert_non_placeholder_summary(symbol.name, "summary", symbol.summary)
        if enforce_placeholder_guard and symbol.purpose and symbol.purpose != "—":
            _assert_non_placeholder_summary(symbol.name, "purpose", symbol.purpose)
        symbol_role = meta.get("function_type")
        if not symbol_role:
            raise RuntimeError(f"Missing explicit function_type for {symbol.name} in PUBLIC_SYMBOL_DOCS")
        symbol.role = str(symbol_role).lower()
        if symbol.role not in {"callable", "internal"}:
            raise RuntimeError(f"Invalid function type {symbol.role!r} for {symbol.name}; expected callable/internal")
        if symbol.role == "internal" and not symbol.name.startswith("_"):
            raise RuntimeError(f"Non-underscore callable cannot be internal: {symbol.name}")
        if symbol.role == "callable" and symbol.name.startswith("_"):
            raise RuntimeError(f"Underscore callable cannot be public callable: {symbol.name}")

    function_symbol_map = {name: symbol for name, symbol in symbol_map.items() if symbol.obj_type == "function"}
    nodes, edges, _ = build_callable_graph(module_data, symbol_map, public, docs_metadata)
    node_lookup = {n["qualified_name"]: n for n in nodes}
    core_template_usage_by_symbol, example_template_usage_by_symbol, imported_only_by_symbol = _derive_template_usage_by_kind(template_flow_docs, symbol_map)
    template_usage_by_symbol = {
        name: [*core_template_usage_by_symbol.get(name, []), *example_template_usage_by_symbol.get(name, [])]
        for name in symbol_map
    }
    def _is_callable_edge(edge: dict[str, Any]) -> bool:
        callee = edge.get("callee_qualified_name")
        if not callee:
            return False
        caller = edge["caller_qualified_name"]
        if caller not in node_lookup or callee not in node_lookup:
            return False
        caller_node = node_lookup[caller]
        callee_node = node_lookup[callee]
        return (
            caller_node["callable_name"] in module_data[caller_node["module_name"]]["functions"]
            and callee_node["callable_name"] in module_data[callee_node["module_name"]]["functions"]
        )

    def _label(qn: str) -> str:
        return qn.split(".")[-1]

    def _module_name(qn: str) -> str:
        parts = qn.split(".")
        return parts[1] if len(parts) > 2 and parts[0] == PACKAGE_NAME else parts[-2]
    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    for generated_page in MODULE_DIR.glob("*.md"):
        if generated_page.name != "index.md" and generated_page.stem not in MAJOR_IMPLEMENTATION_MODULES:
            generated_page.unlink()
    module_manifest = {row["module_name"]: row for row in module_docs_metadata}
    discovered_doc_modules = [INTERNAL_ALIAS_MODULES.get(module, module) for module in discovered_modules]
    module_index_lines = [
        "# Implementation Module Catalogue",
        "",
        "Implementation Modules document only current major source boundaries for package maintainers and internal helper traceability, not every `.py` file in `src/fabricops_kit`.",
        "",
        "Zero-callable modules are hidden unless explicitly allowlisted as major internal plumbing. `metadata` is allowlisted as shared internal plumbing because it owns metadata keys, audit fields, and persistence helpers used by multiple workflows. The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is surfaced through the Function Reference catalogue.",
        "",
    ]
    all_doc_modules = discovered_doc_modules
    for module in all_doc_modules:
        actual_module = next((k for k,v in PUBLIC_MODULE_PREFERRED_NAMES.items() if v==module), module)
        info = module_data[actual_module]
        module_data[module] = info
        info = module_data[module]
        module_md = MODULE_DIR / f"{module}.md"
        public_in_module = [s for s in function_symbol_map.values() if s.public_module == module]
        is_internal_only = not public_in_module
        title = f"# `{module}` module" if not is_internal_only else f"# `{module}` module (internal)"
        module_visibility = module_manifest.get(module, {}).get("visibility", "public")
        if module_visibility == "public":
            status_banner = '<div class="api-status-block">\n  <span class="api-chip api-chip-module">Module overview</span>\n</div>'
        elif public_in_module:
            status_banner = (
                '<div class="api-status-block">\n'
                '  <span class="api-chip api-chip-internal">Advanced supporting module</span>\n'
                '  <div class="api-chip-subtitle">Used by reference docs but not promoted as a primary notebook module.</div>\n'
                '</div>'
            )
        elif is_internal_only:
            status_banner = (
                '<div class="api-status-block">\n'
                '  <span class="api-chip api-chip-internal">Internal-only module</span>\n'
                '  <div class="api-chip-subtitle">Not intended as a primary user-facing API surface.</div>\n'
                '</div>'
            )
        else:
            status_banner = (
                '<div class="api-status-block">\n'
                '  <span class="api-chip api-chip-internal">Internal-only module</span>\n'
                '</div>'
            )
        lines = [
            title,
            "",
            status_banner,
            "",
            "Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.",
            "",
            "The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.",
            "",
        ]
        module_nodes = [n for n in nodes if n["module_name"] == actual_module]
        callable_count = len([n for n in module_nodes if n["role"] == "callable"])
        internal_count = len([n for n in module_nodes if n["callable_name"].startswith("_")])
        outbound_mods = sorted({
            e["callee_qualified_name"].split(".")[-2]
            for e in edges
            if e.get("callee_qualified_name")
            and e["caller_qualified_name"].split(".")[-2] == actual_module
            and e["callee_qualified_name"].split(".")[-2] != actual_module
        })
        inbound_mods = sorted({
            e["caller_qualified_name"].split(".")[-2]
            for e in edges
            if e.get("callee_qualified_name")
            and e["callee_qualified_name"].split(".")[-2] == actual_module
            and e["caller_qualified_name"].split(".")[-2] != actual_module
        })
        summary_cards = (
            '<div class="module-summary-cards">'
            f'<span class="reference-chip">Callable count: {callable_count}</span>'
            f'<span class="reference-chip">Internal helpers: {internal_count}</span>'
            f'<span class="reference-chip">Uses {len(outbound_mods)} external {plural_word(len(outbound_mods), "module", "modules")}</span>'
            f'<span class="reference-chip">Used by {len(inbound_mods)} external {plural_word(len(inbound_mods), "module", "modules")}</span>'
            '</div>'
        )
        lines.extend(["## Module overview badges", "", summary_cards, ""])

        module_purpose = module_manifest.get(module, {}).get("module_summary", "").strip()
        if module_purpose:
            lines.extend(["## Module purpose", "", module_purpose, ""])

        recommended = sorted([s for s in public_in_module if s.role == "callable"], key=lambda x: x.name.lower())
        lines.extend(["## Module manifest", ""])
        manifest_rows = [
            ["Module name", f"<code>{module}</code>"],
            ["Module purpose", module_purpose or "—"],
            ["Public callable count", str(callable_count)],
            ["Internal helper count", str(internal_count)],
            ["Used by external module count", str(len(inbound_mods))],
            ["Uses external module count", str(len(outbound_mods))],
            ["External modules using this module", ", ".join(f"<code>{m}</code>" for m in inbound_mods) or "—"],
            ["External modules this module uses", ", ".join(f"<code>{m}</code>" for m in outbound_mods) or "—"],
        ]
        lines.extend(render_html_table(["Field", "Value"], manifest_rows))
        lines.append("")

        if public_in_module:
            def _public_callable_rows(symbols: list[Symbol], tier: str) -> list[list[str]]:
                rows: list[list[str]] = []
                for symbol in symbols:
                    related = sorted([c for c in info["calls"].get(symbol.name, set()) if c in info["functions"] and c.startswith("_")])
                    callable_link = callable_docs_link(symbol.name, module, docs_metadata, source_module=actual_module)
                    rows.append([
                        f'<a href="{callable_link}"><code>{symbol.name}</code></a>',
                        tier,
                        symbol.obj_type,
                        symbol.summary or "—",
                        ', '.join(f'<code>{r}</code> (internal)' for r in related) or "—",
                    ])
                return rows

            lines.extend(["## Public callables", ""])
            public_rows = _public_callable_rows(recommended, "Callable")
            if not public_rows:
                public_rows.append(["—", "—", "—", "No public exports in this module.", "—"])
            lines.extend(['<div class="module-table-scroll">'])
            lines.extend(render_html_table(["Callable", "Tier", "Type", "Summary", "Related helpers"], public_rows))
            lines.extend(['</div>'])
        else:
            lines.extend(["## Public callables", "", "No public exports in this module."])

        lines.extend(["", "## Module relationships", ""])
        lines.extend(["", "### Callable relationships", ""])
        internal_fns = sorted([f for f in info["functions"] if f.startswith("_")])
        module_edges = [
            (e["caller_qualified_name"], e["callee_qualified_name"])
            for e in edges
            if _is_callable_edge(e) and (_module_name(e["caller_qualified_name"]) == actual_module or _module_name(e["callee_qualified_name"]) == actual_module)
        ]
        module_edge_pairs = sorted(set(module_edges))
        inside_rows = [(s, d) for s, d in module_edge_pairs if _module_name(s) == actual_module and _module_name(d) == actual_module]
        used_by_rows = [(s, d) for s, d in module_edge_pairs if _module_name(s) != actual_module and _module_name(d) == actual_module and not _hide_from_public_relationships(s)]
        uses_rows = [(s, d) for s, d in module_edge_pairs if _module_name(s) == actual_module and _module_name(d) != actual_module and not _hide_from_public_relationships(d)]
        if module_edge_pairs:
            lines.extend(["", "#### Inside this module", ""])
            lines.append('<section class="callable-relationship-card">')
            lines.append(f"<h5>{module}</h5>")
            public_names = sorted([p.name for p in public_in_module])
            internal_names = sorted([f for f in info["functions"] if f.startswith("_")])
            for heading, names in [("Public callables", public_names)]:
                lines.append(f"<h6>{heading}</h6>")
                if not names:
                    lines.append("<p>None.</p>")
                    continue
                lines.append('<ul class="callable-relationship-rows">')
                for name in names:
                    src_qn = f"fabricops_kit.{actual_module}.{name}"
                    callees = sorted([d for s, d in inside_rows if s == src_qn], key=lambda q: _label(q))
                    src_link = callable_docs_link(name, actual_module, docs_metadata, source_module=actual_module)
                    lines.append("<li>")
                    lines.append(f'<a class="reference-chip" href="{src_link}"><code>{name}</code></a>')
                    lines.append(" <span class=\"callable-relationship-uses\">uses:</span>")
                    if callees:
                        callee_links = ", ".join(
                            (f'<a class="reference-chip" href="{callable_docs_link(dst_qn.split(".")[-1], _module_name(dst_qn), docs_metadata, source_module=actual_module)}"><code>{_label(dst_qn)}</code></a>' if node_lookup.get(dst_qn, {}).get("exported") else f'<span class="reference-chip"><code>{_label(dst_qn)}</code></span>')
                            for dst_qn in callees
                        )
                        lines.append(callee_links)
                    else:
                        lines.append("<span>None.</span>")
                    lines.append("</li>")
                lines.append("</ul>")
            lines.append("</section>")
            lines.extend(["", "### Related internal helpers", ""])
            if internal_fns:
                lines.extend(["<details>", "<summary>Show internal helpers</summary>", ""])
                helper_rows: list[list[str]] = []
                for helper in internal_fns:
                    users = sorted([u for u in info["used_by"].get(helper, set()) if u in {p.name for p in public_in_module}])
                    users_links = ", ".join(
                        f'<a href="{callable_docs_link(u, module, docs_metadata, source_module=actual_module)}"><code>{u}</code></a>' for u in users
                    ) or "—"
                    helper_rows.append([f'<code>{helper}</code>', users_links])
                lines.extend(['<div class="module-table-scroll">'])
                lines.extend(render_html_table(["Helper", "Related public callables"], helper_rows))
                lines.extend(['</div>', "", "<h6>Internal helpers details</h6>"])
                lines.append('<ul class="callable-relationship-rows">')
                for name in internal_names:
                    src_qn = f"fabricops_kit.{actual_module}.{name}"
                    callees = sorted([d for s, d in inside_rows if s == src_qn], key=lambda q: _label(q))
                    lines.append("<li>")
                    lines.append(f'<span class="reference-chip"><code>{name}</code></span>')
                    if callees:
                        callee_links = ", ".join(
                            (f'<a class="reference-chip" href="{callable_docs_link(dst_qn.split(".")[-1], _module_name(dst_qn), docs_metadata, source_module=actual_module)}"><code>{_label(dst_qn)}</code></a>' if node_lookup.get(dst_qn, {}).get("exported") else f'<span class="reference-chip"><code>{_label(dst_qn)}</code></span>')
                            for dst_qn in callees
                        )
                        lines.append(" <span class=\"callable-relationship-uses\">uses:</span>")
                        lines.append(callee_links)
                    lines.append("</li>")
                lines.append("</ul>")
                lines.append("</details>")
            else:
                lines.append("No module-level internal helpers detected.")
            lines.extend(["", "### External callers", ""])
            if not used_by_rows:
                lines.append("None.")
            else:
                callers_by_module: dict[str, list[str]] = {}
                for src_qn, _ in used_by_rows:
                    callers_by_module.setdefault(_module_name(src_qn), []).append(src_qn)
                for src_module in sorted(callers_by_module):
                    lines.append(f"**{src_module}**")
                    chips = ", ".join(
                        f'<a class="reference-chip" href="{callable_docs_link(src_qn.split(".")[-1], _module_name(src_qn), docs_metadata, source_module=actual_module)}"><code>{_label(src_qn)}</code></a>'
                        for src_qn in sorted(set(callers_by_module[src_module]))
                    )
                    lines.append(chips)
                    lines.append("")
            lines.extend(["### External callees", ""])
            if not uses_rows:
                lines.append("None.")
            else:
                callees_by_module: dict[str, list[str]] = {}
                for _, dst_qn in uses_rows:
                    callees_by_module.setdefault(_module_name(dst_qn), []).append(dst_qn)
                for dst_module in sorted(callees_by_module):
                    lines.append(f"**{dst_module}**")
                    chips = ", ".join(
                        f'<a class="reference-chip" href="{callable_docs_link(dst_qn.split(".")[-1], _module_name(dst_qn), docs_metadata, source_module=actual_module)}"><code>{_label(dst_qn)}</code></a>'
                        for dst_qn in sorted(set(callees_by_module[dst_module]))
                    )
                    lines.append(chips)
                    lines.append("")
        else:
            lines.append("No callable relationships detected for this module.")
        if public_in_module:
            for s in sorted([x for x in public_in_module if x.role == "callable"], key=lambda x: x.name.lower()):
                expected_target = callable_docs_link(s.name, module, docs_metadata, source_module=actual_module)
                expected_href = f'href="{expected_target}"'
                expected_md_link = f"[`{s.name}`]({expected_target})"
                if not any((expected_md_link in line) or (expected_href in line) for line in lines):
                    raise RuntimeError(f"Missing callable table link for {module}.{s.name}")
                if f"../../api/reference/{module}/{s.name}.md" in "\n".join(lines):
                    raise RuntimeError(
                        f"Found obsolete module-path public link for {module}.{s.name}; expected public reference slug path."
                    )
        for helper in internal_fns:
            expected_helper_code = f"<code>{helper}</code>"
            if not any(expected_helper_code in line for line in lines):
                raise RuntimeError(f"Missing internal helper summary for {module}.{helper}")
        if any("## Public callable details" in line for line in lines):
            raise RuntimeError(f"Public callable details section should not be rendered for {module}")
        if any("## Full module API" in line for line in lines):
            raise RuntimeError(f"Full module API section should not be rendered for {module}")
        if any(line.strip().startswith("::: fabricops_kit.") for line in lines):
            raise RuntimeError(f"Mkdocstrings directives should not be rendered on module page for {module}")
        module_md.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
        module_index_lines.append(f"- [`{module}`]({module}.md)")

    (MODULE_DIR / "index.md").write_text("\n".join(module_index_lines) + "\n", encoding="utf-8", newline="\n")
    discovered_set = set(discovered_doc_modules)
    module_sidebar_rows = [row for row in module_docs_metadata if row.get("sidebar_include")]
    module_sidebar_groups: dict[str, list[str]] = {}
    for row in module_sidebar_rows:
        module_name = row["module_name"]
        if module_name not in discovered_set:
            raise RuntimeError(f"Template sidebar module is missing in src/fabricops_kit: {module_name}")
        module_sidebar_groups.setdefault(row["sidebar_group"], []).append(module_name)

    mkdocs_text = MKDOCS_PATH.read_text(encoding="utf-8")
    function_start_marker = "          # AUTO-GENERATED-FUNCTIONS-START"
    function_end_marker = "          # AUTO-GENERATED-FUNCTIONS-END"
    if function_start_marker in mkdocs_text and function_end_marker in mkdocs_text:
        before, rest = mkdocs_text.split(function_start_marker, 1)
        _middle, after = rest.split(function_end_marker, 1)
        mkdocs_text = before + function_start_marker + "\n" + function_end_marker + after

    start_marker = "          # AUTO-GENERATED-MODULES-START"
    end_marker = "      # AUTO-GENERATED-MODULES-END"
    if start_marker in mkdocs_text and end_marker in mkdocs_text:
        generated_lines = []
        for modules in module_sidebar_groups.values():
            for module in modules:
                generated_lines.append(f"          - {module}: api/modules/{module}.md")
        generated = "\n".join(generated_lines)
        before, rest = mkdocs_text.split(start_marker, 1)
        middle, after = rest.split(end_marker, 1)
        mkdocs_text = before + start_marker + "\n" + generated + "\n" + end_marker + after

    MKDOCS_PATH.write_text(mkdocs_text, encoding="utf-8", newline="\n")

    nodes, edges, module_summary = build_callable_graph(module_data, symbol_map, public, docs_metadata)
    node_by_qn = {n["qualified_name"]: n for n in nodes}
    calls_by_qn: dict[str, list[str]] = {}
    used_by_qn: dict[str, list[str]] = {}
    for e in edges:
        caller = e["caller_qualified_name"]
        callee = e.get("callee_qualified_name")
        if not callee:
            continue
        calls_by_qn.setdefault(caller, []).append(callee)
        used_by_qn.setdefault(callee, []).append(caller)
    manifest_rows = []
    known_modules = set(discovered_doc_modules)
    for s in sorted(function_symbol_map.values(), key=lambda x: x.name.lower()):
        canonical_module = canonical_public_module(s.public_module)
        if canonical_module not in known_modules:
            raise RuntimeError(f"Callable {s.name} resolved to module_name without generated page: {canonical_module!r}.")
        module_meta = module_manifest.get(canonical_module, {"visibility": "public", "sidebar_include": True, "module_summary": "", "sidebar_group": "Modules"})
        callable_role = s.role
        manifest_rows.append(
            {
                "module_name": canonical_module,
                "visibility": module_meta["visibility"],
                "module_summary": module_meta["module_summary"],
                "sidebar_group": module_meta["sidebar_group"],
                "sidebar_include": module_meta["sidebar_include"],
                "callable_name": s.name,
                "callable_visibility": module_meta["visibility"],
                "callable_type": callable_role,
                "callable_role": callable_role,
                "template_notebook": docs_metadata[s.name].get("template_notebook"),
                "template_segment": docs_metadata[s.name].get("template_segment"),
                "used_in_templates": template_usage_by_symbol.get(s.name, []),
            }
        )
    manifest_modules = []
    for module in discovered_doc_modules:
        meta = module_manifest.get(module, {})
        manifest_modules.append({
            "module_name": module,
            "visibility": meta.get("visibility", "public"),
            "module_summary": meta.get("module_summary", ""),
            "sidebar_group": meta.get("sidebar_group", "Modules"),
            "sidebar_include": meta.get("sidebar_include", True),
        })
    manifest_modules = sorted(manifest_modules, key=lambda row: row["module_name"])
    manifest_rows = sorted(manifest_rows, key=lambda row: (row["module_name"], row["callable_name"]))
    MANIFEST_PATH.write_text(json.dumps({"modules": manifest_modules, "callables": manifest_rows}, indent=2) + "\n", encoding="utf-8")
    dependency_callables: dict[str, dict[str, Any]] = {}
    for qn in sorted(node_by_qn):
        node = node_by_qn[qn]
        deps = sorted(set(calls_by_qn.get(qn, [])))
        internal_helpers = [d for d in deps if d.startswith(f"{PACKAGE_NAME}.{node['module_name']}._")]
        used_by = sorted(set(used_by_qn.get(qn, [])))
        used_in_templates = template_usage_by_symbol.get(node["callable_name"], []) if node["exported"] else []
        dependency_callables[qn] = {
            "qualified_name": qn,
            "short_name": node["callable_name"],
            "module": node["module_name"],
            "callable": node["callable_name"],
            "docs_url": (
                f"/FabricOps-Starter-Kit/reference/{node['callable_name']}/"
                if node["exported"]
                else (
                    f"/FabricOps-Starter-Kit/reference/internal/{node['module_name']}_{node['callable_name']}/"
                    if generate_internal_reference_pages()
                    else None
                )
            ),
            "classification": node["role"],
            "calls": deps,
            "calls_count": len(deps),
            "used_by": used_by,
            "used_by_count": len(used_by),
            "used_in_templates": used_in_templates,
            "internal_helpers_used": internal_helpers,
            "internal_helper_count": len(internal_helpers),
        }
    dependency_modules: dict[str, dict[str, Any]] = {}
    for module in sorted({n["module_name"] for n in nodes}):
        module_nodes = [n for n in nodes if n["module_name"] == module]
        callable_count = sum(1 for n in module_nodes if n["role"] == "callable")
        internal = sum(1 for n in module_nodes if n["callable_name"].startswith("_"))
        out_mods, in_mods = set(), set()
        for e in edges:
            callee = e.get("callee_qualified_name")
            if not callee:
                continue
            src_mod = e["caller_qualified_name"].split(".")[-2]
            dst_mod = callee.split(".")[-2]
            if src_mod == module and dst_mod != module:
                out_mods.add(dst_mod)
            if dst_mod == module and src_mod != module:
                in_mods.add(src_mod)
        dependency_modules[module] = {
            "callable_count": callable_count,
            "internal_count": internal,
            "outbound_modules": sorted(out_mods),
            "inbound_modules": sorted(in_mods),
            "outbound_count": len(out_mods),
            "inbound_count": len(in_mods),
        }
    public_qn_by_name = {name: f"{PACKAGE_NAME}.{symbol.actual_module}.{name}" for name, symbol in symbol_map.items()}
    internalized_public_helpers = {
        "read_lakehouse_csv",
        "read_lakehouse_excel",
        "read_lakehouse_parquet",
        "read_lakehouse_table",
        "read_warehouse_table",
        "write_lakehouse_table",
        "write_warehouse_table",
        "stop_if_failed",
        "enforce_freshness",
        "enforce_freshness_rule",
        "enforce_profile_behavior",
        "write_catalogue_evidence",
    }
    audit_names = set(docs_metadata) | set(public) | internalized_public_helpers
    audit_rows = []
    for name in sorted(audit_names, key=str.lower):
        symbol = symbol_map.get(name)
        if symbol is not None:
            qn = public_qn_by_name[name]
        else:
            module_name = str(docs_metadata.get(name, {}).get("module", ""))
            qn = f"{PACKAGE_NAME}.{resolve_preferred_actual_module(module_name)}.{name}" if module_name else ""
        internal_public_callers = sorted({
            node_by_qn[caller]["callable_name"]
            for caller in used_by_qn.get(qn, [])
            if node_by_qn.get(caller, {}).get("exported")
        }) if qn else []
        in_root_exports = name in public
        if core_template_usage_by_symbol.get(name):
            decision = "template_called_public"
        elif in_root_exports and example_template_usage_by_symbol.get(name):
            decision = "advanced_public_helper"
        elif in_root_exports:
            decision = "advanced_public_helper"
        elif name in internalized_public_helpers:
            decision = "convert_to_internal"
        else:
            decision = "remove_export"
        audit_rows.append({
            "function": name,
            "in_root_exports": in_root_exports,
            "directly_called_in_core_templates": core_template_usage_by_symbol.get(name, []),
            "directly_called_in_example_templates": example_template_usage_by_symbol.get(name, []),
            "imported_only_in_templates": bool(imported_only_by_symbol.get(name)),
            "called_only_internally_by_public_helper": internal_public_callers,
            "has_standalone_reference_page": in_root_exports,
            "decision": decision,
        })
    CALLABLE_SURFACE_AUDIT_PATH.write_text(json.dumps(audit_rows, indent=2) + "\n", encoding="utf-8")

    dependency_callables_sorted = {k: dependency_callables[k] for k in sorted(dependency_callables)}
    dependency_modules_sorted = {k: dependency_modules[k] for k in sorted(dependency_modules)}
    DEPENDENCY_METADATA_PATH.write_text(
        json.dumps({"callables": dependency_callables_sorted, "modules": dependency_modules_sorted}, indent=2) + "\n",
        encoding="utf-8",
    )

    template_paths_in_metadata = {flow.get("template_path") for flow in template_flow_docs}
    missing_template_paths = sorted(
        str(path.relative_to(ROOT))
        for path in (ROOT / "templates" / "notebooks").glob("*.ipynb")
        if str(path.relative_to(ROOT)) not in template_paths_in_metadata
    )
    if missing_template_paths:
        missing = ", ".join(missing_template_paths)
        raise RuntimeError(f"TEMPLATE_FLOW_DOCS is missing notebook templates: {missing}")

    public_symbol_names = set(symbol_map)
    for flow in template_flow_docs:
        expected_symbols = [
            symbol
            for segment in flow["segments"]
            for symbol in segment["symbols"]
        ]
        actual_symbols = _direct_public_template_symbols(flow.get("template_path", ""), public_symbol_names)
        if set(expected_symbols) != set(actual_symbols):
            expected = ", ".join(sorted(expected_symbols)) or "(none)"
            actual = ", ".join(actual_symbols) or "(none)"
            raise RuntimeError(
                "TEMPLATE_FLOW_DOCS symbols must match direct public callable usage in "
                f"{flow.get('template_path')}: expected metadata [{expected}], actual notebook calls [{actual}]"
            )
    starter_symbol_to_notebooks: dict[str, set[str]] = {}
    for flow in template_flow_docs:
        notebook_key = flow["notebook_key"]
        for segment in flow["segments"]:
            for symbol in segment["symbols"]:
                if symbol not in symbol_map:
                    raise RuntimeError(f"TEMPLATE_FLOW_DOCS references unknown symbol: {symbol}")
                starter_symbol_to_notebooks.setdefault(symbol, set()).add(notebook_key)

    def _esc(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    def _html_table(
        table_class: str,
        headers: list[str],
        rows: list[list[str]],
        *,
        row_attrs: list[dict[str, str]] | None = None,
    ) -> list[str]:
        lines = [f'<table class="{table_class}">', "  <thead>", "    <tr>"]
        for header in headers:
            lines.append(f"      <th>{_esc(header)}</th>")
        lines.extend(["    </tr>", "  </thead>", "  <tbody>"])
        for row_index, row in enumerate(rows):
            attr_text = ""
            if row_attrs and row_index < len(row_attrs):
                attrs = row_attrs[row_index]
                attr_text = "".join(f' {key}="{_esc(value)}"' for key, value in attrs.items())
            lines.append(f"    <tr{attr_text}>")
            for idx, cell in enumerate(row):
                lines.append(f'      <td data-label="{_esc(headers[idx])}">{cell}</td>')
            lines.append("    </tr>")
        lines.extend(["  </tbody>", "</table>"])
        return lines

    def _anchor(href: str, text: str, *, code: bool = False) -> str:
        content = f"<code>{_esc(text)}</code>" if code else _esc(text)
        return f'<a href="{_esc(href)}">{content}</a>'

    def _module_link(module: str, *, base_prefix: str = "../") -> str:
        return (
            f'<a class="reference-module-link" href="{_esc(base_prefix)}api/modules/{_esc(module)}/" '
            f'title="Open {module} module page" aria-label="Open {module} module page">{_esc(module)}</a>'
        )


    public_flow_qns = sorted(
        [qn for qn, node in node_by_qn.items() if node.get("exported")],
        key=lambda qn: node_by_qn[qn]["callable_name"].lower(),
    )
    generated_at_utc = datetime.now(UTC)
    callable_flow_data = _build_callable_flow_data(
        public_flow_qns,
        calls_by_qn,
        node_by_qn,
        module_data,
        generated_at_utc=generated_at_utc,
    )
    public_flow_by_qn = _flow_by_public_qualified_name(callable_flow_data)

    callable_metrics = _callable_inventory_metrics(callable_flow_data)
    public_function_count = callable_metrics["public_api_entrypoints"] or len(function_symbol_map)
    ref = [
        "# Function Reference",
        "",
        "Use this page to look up Starter Kit functions used by the template notebooks.",
        "",
        '<div class="reference-kpi-grid" aria-label="Function reference summary">',
        '  <section class="reference-kpi-card surface-card">',
        f'    <strong class="reference-kpi-value">{callable_metrics["module_count"]}</strong>',
        '    <span class="reference-kpi-title">Modules</span>',
        '    <p class="reference-kpi-note">Code areas represented.</p>',
        '  </section>',
        '  <section class="reference-kpi-card surface-card">',
        f'    <strong class="reference-kpi-value">{callable_metrics["total_callables"]}</strong>',
        '    <span class="reference-kpi-title">Total callables</span>',
        '    <p class="reference-kpi-note">Complete discovered callable inventory.</p>',
        '  </section>',
        '  <section class="reference-kpi-card surface-card">',
        f'    <strong class="reference-kpi-value">{callable_metrics["public_api_entrypoints"]}</strong>',
        '    <span class="reference-kpi-title">Public API</span>',
        '    <p class="reference-kpi-note">Notebook-facing entrypoints.</p>',
        '  </section>',
        '  <section class="reference-kpi-card surface-card">',
        f'    <strong class="reference-kpi-value">{callable_metrics["supporting_functions"]}</strong>',
        '    <span class="reference-kpi-title">Supporting functions</span>',
        '    <p class="reference-kpi-note">Internal functions behind the public API.</p>',
        '  </section>',
        '  <section class="reference-kpi-card surface-card">',
        f'    <strong class="reference-kpi-value">{callable_metrics["hidden_private_helpers"]}</strong>',
        '    <span class="reference-kpi-title">Private helpers to review</span>',
        '    <p class="reference-kpi-note">Excluded from default architecture counts.</p>',
        '  </section>',
        '</div>',
        "",
        "<p><small>Callable metrics are generated from the callable inventory data.</small></p>",
        "",
    ]

    ref.extend(
        [
            "## Find a function",
            "",
            f"Use the finder below to look up the {public_function_count} public Starter Kit functions. Internal helper records stay out of the standalone public catalogue. “Used in” means direct starter notebook code-cell invocation, not import-only, markdown-only, generated metadata, example usage, or internal helper usage.",
            "",
            '<div class="callable-finder" data-callable-finder>',
            '  <label class="callable-finder-label" for="callable-finder-input">Search functions</label>',
            '  <input id="callable-finder-input" class="callable-finder-input" type="search" placeholder="Search public functions" aria-describedby="callable-finder-help callable-finder-status callable-finder-examples" autocomplete="off">',
            '  <p id="callable-finder-help" class="callable-finder-help">Search by function name, module, starter path, usage source, or description.</p>',
            '  <p id="callable-finder-examples" class="callable-finder-examples">Try: <span class="callable-finder-chip">dq_rules</span> <span class="callable-finder-chip">lineage</span> <span class="callable-finder-chip">guardrail</span></p>',
            f'  <p id="callable-finder-status" class="callable-finder-status" aria-live="polite">Showing {public_function_count} public Starter Kit functions.</p>',
            '  <p class="callable-finder-empty" data-callable-finder-empty hidden>No functions match your search.</p>',
            "</div>",
            "",
            '??? info "Maintainer tools"',
            '    Use these links and notes when maintaining the reference system.',
            '',
            '    - [Glossary](glossary.md): simple definitions of repeated FabricOps terms.',
            '    - [Public callable flow map](callable-flow.md): global public callable dependency view and nested internal helper summary.',
            '    - [Architecture](../assets/callable-functions-dashboard.html): review public API shape, chain depth, fan-out, modules touched, cross-layer warnings, and flattening recommendations.',
            '    - [Inventory](../assets/callable-functions-inventory.html): search/filter all callables, select rows, and export AI refactor packets.',
            '    - [Implementation modules](../api/modules/): source ownership, module-level dependencies, and utility/internal relationships.',
            '    - Function manifests: `_data/manifest.json` and `_data/function-manifest.json`.',
            '    - Agent metadata: `_data/automation-manifest.json`.',
            '    - Implementation contracts: expectations maintainers must satisfy before using or changing a function.',
            '    - Skill file: `.agents/skills/fabricops/SKILL.md`.',
            '',
            "## Function catalogue",
            "",
            "## Functions",
            "",
        ]
    )
    all_items: list[str] = []
    function_category_by_name = {name: "public_starter_kit" for name in function_symbol_map}

    catalogue_nodes = sorted(
        [
            n
            for n in node_by_qn.values()
            if n["exported"] and n["callable_name"] in module_data[n["module_name"]]["functions"]
        ],
        key=lambda n: (n["callable_name"].lower(), n["module_name"]),
    )
    for node in catalogue_nodes:
        name = node["callable_name"]
        module_name = node["module_name"]
        function_type = "public-starter-kit"
        symbol = function_symbol_map[name]
        symbol_link = public_reference_link(name, docs_metadata, context="reference")
        starter_path = ", ".join(core_template_usage_by_symbol.get(name, [])) or "—"
        usage_source = ", ".join(template_usage_by_symbol.get(name, [])) or "—"
        purpose = symbol.purpose or symbol.summary or "—"
        display_module = symbol.public_module
        starter_path_attribute = f' data-callable-starter-path="{_esc(starter_path)}"' if starter_path != "—" else ""
        usage_source_attribute = f' data-callable-usage-source="{_esc(usage_source)}"' if usage_source != "—" else ""
        qn = f"{PACKAGE_NAME}.{module_name}.{name}"
        public_flow = public_flow_by_qn.get(qn, {})
        downstream_callables = [row["qualified_name"] for row in public_flow.get("transitive_callees", []) if row.get("qualified_name")]

        def _catalogue_relationship_list(items: list[str]) -> str:
            rows = []
            for item in items:
                related_node = node_by_qn.get(item, {})
                short = related_node.get("callable_name") or item.split(".")[-1]
                if related_node.get("exported"):
                    href = public_reference_link(short, docs_metadata, context="reference")
                    rows.append(f'<li><a href="{_esc(href)}"><code>{_esc(short)}</code></a></li>')
                else:
                    rows.append(f'<li><code>{_esc(short)}</code></li>')
            return "<ul>" + "".join(rows) + "</ul>"

        def _catalogue_count_details(singular_label: str, plural_label: str, items: list[str]) -> str:
            count = len(items)
            if count == 0:
                return ""
            label = singular_label if count == 1 else plural_label
            return (
                '    <details class="reference-count-details"><summary>'
                f'<span class="reference-chip reference-chip-count">{_esc(label.format(count=count))}</span>'
                "</summary>"
                + _catalogue_relationship_list(items)
                + "</details>"
            )

        all_items.extend(
            [
                (
                    f'<article id="{_esc(module_name)}-{_esc(name)}" class="reference-catalogue-item" '
                    f'data-callable-row="true" data-callable-name="{_esc(name)}" '
                    f'data-callable-module="{_esc(display_module)}"'
                    f'{starter_path_attribute}'
                    f'{usage_source_attribute} '
                    f'data-function-type="{_esc(function_type)}" '
                    f'data-callable-purpose="{_esc(purpose)}">'
                ),
                f'  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="{_esc(symbol_link)}"><code>{_esc(name)}</code></a></h3>',
                f'  <p class="reference-catalogue-item-purpose">{_esc(purpose)}</p>',
                (
                    '  <p class="reference-catalogue-item-meta reference-catalogue-item-badges">'
                    f'{_module_link(display_module)}'
                    f'<span class="reference-chip">Public Starter Kit function</span>'
                    f'<span class="reference-chip">{_esc(usage_source)}</span>'
                    "</p>"
                ),
                (
                    f'  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> {_esc(usage_source)}</p>'
                    if usage_source != "—"
                    else ""
                ),
                '  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>',
                '  <div class="reference-catalogue-item-counts">',
                _catalogue_count_details("Downstream callables: {count}", "Downstream callables: {count}", downstream_callables),
                "  </div>",
                "</article>",
            ]
        )
    ref.extend(['<div class="reference-catalogue-list">', *all_items, "</div>"])

    ref.append("")
    REFERENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REFERENCE_PATH.write_text("\n".join(ref) + "\n", encoding="utf-8", newline="\n")

    generate_internal_pages = generate_internal_reference_pages()
    CALLABLE_REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    LEGACY_CALLABLE_REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    INTERNAL_REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    for generated_page in [
        *CALLABLE_REFERENCE_DIR.glob("*.md"),
        *LEGACY_CALLABLE_REFERENCE_DIR.glob("*.md"),
        *INTERNAL_REFERENCE_DIR.glob("*.md"),
    ]:
        generated_page.unlink()
    agent_manifest: list[dict[str, Any]] = []
    function_manifest: list[dict[str, Any]] = []
    refactor_signals_manifest: dict[str, dict[str, Any]] = {}
    for qn, node in sorted(node_by_qn.items()):
        short_name = node["callable_name"]
        module_name = node["module_name"]
        raw_deps = sorted(set(calls_by_qn.get(qn, [])))
        raw_used_by = sorted(set(used_by_qn.get(qn, [])))
        deps = [d for d in raw_deps if not _hide_from_public_relationships(d)] if node["exported"] else raw_deps
        used_by = [u for u in raw_used_by if not _hide_from_public_relationships(u)] if node["exported"] else raw_used_by
        metadata = docs_metadata.get(short_name, {})
        module_info = module_data[module_name]
        doc_sections = module_info.get("doc_sections", {}).get(short_name, {})
        signature = module_info.get("signatures", {}).get(short_name, "")
        summary = metadata.get("summary_override") or ""
        docs_path = f"api/reference/{short_name}.md" if node["exported"] else (
            f"reference/internal/{module_name}_{short_name}.md" if generate_internal_pages else None
        )
        source_path = f"src/fabricops_kit/{module_name}.py"
        source_location = module_info.get("source_locations", {}).get(short_name, {})
        source_start_line = source_location.get("start_line")
        source_end_line = source_location.get("end_line")
        source_ref = github_source_url(source_path, source_start_line, source_end_line)
        parameter_rows = module_info.get("parameters", {}).get(short_name, [])
        classification = "Callable" if node.get("role") == "callable" else "Internal"
        purpose = summary or module_info["functions"].get(short_name) or module_info["classes"].get(short_name) or "No summary available."
        rel_module = canonical_public_module(module_name)
        metadata_related = list(metadata.get("related_functions", []))
        relationship_related = [*used_by, *deps]
        rendered_parameters = _documented_text(metadata.get("parameters"), doc_sections.get("parameters"))
        rendered_returns = _documented_text(metadata.get("returns"), doc_sections.get("returns"))
        rendered_return_interpretation = _documented_text(metadata.get("return_interpretation"))
        rendered_raises = _documented_text(metadata.get("raises"), doc_sections.get("raises"))
        rendered_common_failure_causes = _documented_text(metadata.get("common_failure_causes"))
        rendered_side_effects = _documented_text(metadata.get("side_effects"))
        rendered_fabric_context = _documented_text(
            metadata.get("fabric_context"),
            f"Starter template: `{metadata.get('template_notebook')}`; segment: `{metadata.get('template_segment')}`."
            if metadata.get("template_notebook")
            else None,
        )
        rendered_ai_verification = _documented_text(metadata.get("ai_verification"))
        def _fmt_links(items: list[str]) -> list[str]:
            out = []
            for item in items:
                n = node_by_qn.get(item, {})
                if not n:
                    continue
                if n.get("exported"):
                    href = f"{n['callable_name']}/"
                    out.append(f'- <a href="{href}"><code>{item}</code></a>')
                elif n.get("callable_name", "").startswith("_") and generate_internal_reference_pages():
                    href = f"../internal/{n['module_name']}_{n['callable_name']}/"
                    out.append(f'- <a href="{href}"><code>{item}</code></a>')
                else:
                    out.append(f"- `{item}`")
            return out

        if node["exported"]:
            parameter_overrides = _metadata_parameter_overrides(metadata.get("parameters"))
            input_lines = _render_parameter_definitions(parameter_rows, parameter_overrides)
            public_flow = public_flow_by_qn.get(qn, {})
            refactor_signals = _collect_refactor_signals(
                qn,
                calls_by_qn,
                node_by_qn,
                module_data,
                excluded_helpers=INTERNAL_HELPER_EXCLUSIONS.get(short_name, set()),
            )
            refactor_signals_manifest[short_name] = refactor_signals
            used_in_templates = template_usage_by_symbol.get(short_name, [])
            downstream_count = int(public_flow.get("downstream_count") or 0)
            call_flow_lines = (
                [
                    f'??? info "Downstream callables: {downstream_count}"',
                    "",
                    "    Dependency data is generated from the callable architecture inventory.",
                    "",
                    *_indent_markdown(_render_callable_architecture_flow_tree(public_flow, node_by_qn, module_data)),
                ]
                if downstream_count
                else []
            )
            notebook_usage_chips = [
                f'<span class="reference-chip">{html_escape(template)}</span>' for template in used_in_templates
            ] or ['<span class="reference-chip">No starter notebook usage detected</span>']
            page_chip_lines = [
                '<p class="reference-catalogue-item-meta reference-catalogue-item-badges">',
                f'<span class="reference-chip">Module: <code>{html_escape(rel_module)}</code></span>',
                '<span class="reference-chip">Public Starter Kit function</span>',
                *notebook_usage_chips,
                '</p>',
            ]
            human_use_when = _documented_text(metadata.get("when_to_use"))
            human_do_not_use = _documented_text(metadata.get("do_not_use_when"))
            expanded_purpose = _documented_text(metadata.get("expanded_purpose"))
            usage_guidance_lines: list[str] = []
            usage_guidance_body: list[str] = []
            if human_use_when != PLACEHOLDER:
                usage_guidance_body.extend(["### Use when", "", *_bullet_lines(human_use_when), ""])
            if human_do_not_use != PLACEHOLDER:
                usage_guidance_body.extend(["### Do not use when", "", *_bullet_lines(human_do_not_use), ""])
            if expanded_purpose != PLACEHOLDER:
                usage_guidance_body.extend(["### Additional context", "", expanded_purpose])
            if usage_guidance_body:
                usage_guidance_lines = ["## Usage guidance", "", *usage_guidance_body, ""]
            key_term_lines = _render_key_terms(list(metadata.get("glossary_terms", [])), glossary)
            glossary_section_lines: list[str] = []
            if key_term_lines:
                glossary_terms = list(dict.fromkeys(metadata.get("glossary_terms", [])))
                glossary_body = (
                    markdown_details("Glossary terms", key_term_lines, class_name="reference-glossary-details")
                    if len(glossary_terms) > 5
                    else key_term_lines
                )
                glossary_section_lines = ["## Glossary", "", *glossary_body, ""]
            related_guide_lines = _render_related_guides(list(metadata.get("related_guides", [])))
            see_also_lines = related_guide_lines if related_guide_lines else ["## See also", "", "No related guides documented.", ""]
            preferred_example = _render_preferred_example(short_name, signature, metadata)
            return_interpretation_lines = (
                ["### Return interpretation", "", rendered_return_interpretation, ""]
                if metadata.get("return_interpretation")
                else []
            )
            common_failure_cause_lines = (
                ["### Common failure causes", "", rendered_common_failure_causes, ""]
                if metadata.get("common_failure_causes")
                else []
            )
            lines = [
                f"# {short_name}",
                "",
                *call_flow_lines,
                "",
                purpose,
                "",
                *page_chip_lines,
                "",
                "**Used in notebooks:** "
                + (
                    ", ".join(f"`{template}`" for template in used_in_templates)
                    if used_in_templates
                    else "Not currently detected in starter notebooks."
                ),
                "",
                *usage_guidance_lines,
                "",
                "## Signature",
                "",
                *_reference_code_block(_format_api_signature(signature), class_name="reference-api-definition"),
                "",
                *(
                    [
                        "## Example usage",
                        "",
                        *(
                            _reference_code_block(preferred_example, class_name="reference-example-usage")
                            if preferred_example != PLACEHOLDER
                            else ["Example usage not documented yet."]
                        ),
                        "",
                    ]
                ),
                "## Parameters",
                "",
                *input_lines,
                "",
                "## Returns",
                "",
                rendered_returns,
                "",
                *return_interpretation_lines,
                "## Raises / Errors",
                "",
                rendered_raises,
                "",
                *common_failure_cause_lines,
                *glossary_section_lines,
                *see_also_lines,
            ]
        else:
            lines = [
                f"# {short_name}",
                "",
                f"**Module:** `{module_name}`",
                "**Layer:** Internal",
                "",
                "## Status",
                "",
                "Internal helper used by the package implementation.",
                "",
                "## Function type: Internal helper",
                "",
                "Internal helper",
                "",
                "## Direct use: No",
                "",
                "Do not call this helper directly from notebooks; use the public callable helpers instead.",
                "",
                "## Used by",
                "",
            ]
            lines.extend(_fmt_links(used_by) if used_by else [PLACEHOLDER])
            lines.extend([
                "",
                "## Purpose",
                "",
                purpose,
                "",
                "## Signature if available",
                "",
                _code_block(_format_api_signature(signature)) if signature else PLACEHOLDER,
                "",
                "## Side effects",
                "",
                rendered_side_effects,
                "",
                "## Maintainer notes",
                "",
                "Maintain this helper through the owning implementation module and keep generated references in sync.",
                "",
                "## Implementation contract",
                "",
                _documented_text(metadata.get("ai_verification"), "Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks."),
                "",
                "## Function manifest",
                "",
                f"- Fully qualified function name: `{qn}`",
                f"- Short name: `{short_name}`",
                f"- Module: `{module_name}`",
                "- Layer: Internal",
                f"- Related module: `{rel_module}`",
                f"- Source file path: `{source_path}`",
                f'- Source reference: <a href="{source_ref}">View source on GitHub</a>',
                f"- Used by references count: {len(used_by)}",
                f"- Calls references count: {len(deps)}",
            ])

        if not node["exported"]:
            if used_by:
                lines.extend(["", "## Used by references", *(_fmt_links(used_by))])
            if deps:
                lines.extend(["", "## Calls references", *(_fmt_links(deps))])
            if not used_by and not deps:
                lines.extend(["", "_No used-by or calls references detected._"])

        if node["exported"]:
            (CALLABLE_REFERENCE_DIR / f"{short_name}.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        elif generate_internal_pages:
            (INTERNAL_REFERENCE_DIR / f"{module_name}_{short_name}.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

        record_used_in_templates = template_usage_by_symbol.get(short_name, []) if node["exported"] else []
        record_when_to_use = metadata.get("when_to_use") if node["exported"] else None
        manifest_category = function_category_by_name.get(short_name, "internal-private" if short_name.startswith("_") else "utility")
        function_manifest.append({"id": qn, "name": short_name, "qualified_name": qn, "module": module_name, "classification": classification, "function_category": manifest_category, "usage_sources": record_used_in_templates, "inbound": used_by, "outbound": deps, "used_in_templates": record_used_in_templates, "glossary_terms": list(metadata.get("glossary_terms", [])) if node["exported"] else [], "expanded_purpose": metadata.get("expanded_purpose") if node["exported"] else None, "when_to_use": record_when_to_use, "return_interpretation": metadata.get("return_interpretation") if node["exported"] else None, "common_failure_causes": metadata.get("common_failure_causes", []) if node["exported"] else [], "related_guides": list(metadata.get("related_guides", [])) if node["exported"] else [], "source_path": source_path, "source_start_line": source_start_line, "source_end_line": source_end_line, "source_url": source_ref, "docs_path": docs_path, "summary": purpose})
        agent_manifest.append({
            "name": short_name,
            "qualified_name": qn,
            "module": module_name,
            "type": "callable" if node["exported"] else "internal",
            "role": node.get("role", "internal"),
            "function_category": manifest_category,
            "inbound": used_by,
            "outbound": deps,
            "used_in_templates": record_used_in_templates,
            "glossary_terms": list(metadata.get("glossary_terms", [])) if node["exported"] else [],
            "expanded_purpose": metadata.get("expanded_purpose") if node["exported"] else None,
            "when_to_use": record_when_to_use,
            "source_file": source_path,
            "source_start_line": source_start_line,
            "source_end_line": source_end_line,
            "source_url": source_ref,
            "docs_path": docs_path,
            "summary": purpose,
            "use_when": _documented_text(metadata.get("when_to_use"), metadata.get("use_when"), metadata.get("purpose"), purpose) if node["exported"] else PLACEHOLDER,
            "do_not_use_when": _documented_text(metadata.get("do_not_use_when")),
            "required_context": rendered_fabric_context,
            "inputs": rendered_parameters,
            "output": rendered_returns,
            "return_interpretation": rendered_return_interpretation,
            "side_effects": rendered_side_effects,
            "failure_modes": rendered_raises,
            "common_failure_causes": rendered_common_failure_causes,
            "related_guides": list(metadata.get("related_guides", [])) if node["exported"] else [],
            "preferred_example": _documented_text(metadata.get("preferred_example")),
            "verification": rendered_ai_verification,
            "related_functions": metadata_related or [item.split(".")[-1] for item in relationship_related],
        })
    AGENT_MANIFEST_PATH.write_text(json.dumps(agent_manifest, indent=2) + "\n", encoding="utf-8")
    FUNCTION_MANIFEST_PATH.write_text(json.dumps(function_manifest, indent=2) + "\n", encoding="utf-8")
    landing_stats = generate_landing_stats(
        public_exports=public,
        function_manifest=function_manifest,
        metadata_table_count=metadata_table_count,
        callable_flow_data=callable_flow_data,
    )
    update_landing_page_counts(landing_stats)
    REFACTOR_SIGNALS_PATH.write_text(
        json.dumps(refactor_signals_manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    CALLABLE_FLOW_DATA_PATH.write_text(json.dumps(callable_flow_data, indent=2) + "\n", encoding="utf-8")
    CALLABLE_FLOW_PAGE_PATH.write_text(_render_callable_flow_page(callable_flow_data), encoding="utf-8", newline="\n")
    REFACTOR_DASHBOARD_PATH.write_text(_render_refactor_dashboard_html(callable_flow_data), encoding="utf-8", newline="\n")
    REFACTOR_INVENTORY_PATH.write_text(_render_refactor_inventory_html(callable_flow_data), encoding="utf-8", newline="\n")
    _remove_stale_function_taxonomy_audit()



if __name__ == "__main__":
    main()
