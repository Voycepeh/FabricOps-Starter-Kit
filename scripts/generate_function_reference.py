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
    "data_lineage": "data_lineage",
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
    "io_core",
    "data_lineage",
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
        module_tree = ast.parse((PKG_DIR / f"{module}.py").read_text(encoding="utf-8"))
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
    "Thin wrapper candidate": "Inline candidate",
    "Single-use internal helper": "Review abstraction value",
    "Leaf internal helper": "Stable utility",
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
    "High": "Inline candidate",
    "Medium": "Review abstraction value",
    "Low": "Stable utility",
    "Review": "Review manually",
}

ACTION_LEGEND = {
    "Public API entrypoint": "Supported user-facing API surface; no inbound project calls are required.",
    "Shared internal helper": "Internal implementation helper used by multiple public or internal callers; protect with focused tests before changing.",
    "Stable utility": "Low-level leaf helper with multiple inbound callers; keep generic and project-callable free.",
    "Inline candidate": "Small helper or single-use utility; consider flattening into its caller after checking readability.",
    "Review abstraction value": "Helper used by only one function; verify the name, boundary, and test value justify keeping it separate.",
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
    "public": "Public API",
    "internal": "Internal helper",
    "utility": "Utility",
}

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
    "stable_utility": "Stable utility",
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

    if architecture_layer == "Utility":
        if used_by_count >= 3 and calls_count == 0:
            return "stable_utility"
        if used_by_count <= 1:
            return "questionable_utility"
        if calls_count > 0:
            return "review_manually"
        return "matches_layer"

    if architecture_layer == "Internal helper":
        if used_by_count >= 5:
            return "promote_to_utility_candidate"
        if used_by_count >= 2:
            return "shared_internal_helper"
        if used_by_count <= 1 and callable_kind == "function":
            return "possible_inline_or_private_helper"
        return "matches_layer"

    if architecture_layer == "Public API":
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

    # Pipeline public entrypoints and role-organized internals.
    "start_pipeline_run": ["public_api_entrypoint", "pipeline_entrypoint", "public_stable"],
    "prepare_pipeline_table_configs": ["public_api_entrypoint", "pipeline_entrypoint", "public_stable"],
    "run_table_guardrails": ["public_api_entrypoint", "pipeline_entrypoint", "public_stable"],
    "display_guardrail_results": ["public_api_entrypoint", "pipeline_entrypoint", "public_stable"],
    "write_pipeline_lineage": ["public_api_entrypoint", "pipeline_entrypoint", "public_stable"],
    "write_pipeline_run_summary": ["public_api_entrypoint", "pipeline_entrypoint", "public_stable"],
    "_start_pipeline_run_workflow": ["internal_workflow", "pipeline_workflow", "run_start_workflow"],
    "_prepare_pipeline_table_configs_workflow": [
        "internal_workflow",
        "pipeline_workflow",
        "table_config_preparation_workflow",
    ],
    "_run_table_guardrails_workflow": ["internal_workflow", "pipeline_workflow", "guardrail_execution_workflow"],
    "_display_guardrail_results_workflow": ["internal_workflow", "pipeline_workflow", "guardrail_display_workflow"],
    "_write_pipeline_lineage_workflow": ["internal_workflow", "pipeline_workflow", "lineage_write_workflow"],
    "_write_pipeline_run_summary_workflow": ["internal_workflow", "pipeline_workflow", "run_summary_write_workflow"],
    "_active_pipeline_context": ["internal_resolver", "pipeline_context_resolver"],
    "_runtime_audit_fields": ["internal_resolver", "audit_field_resolver"],
    "_build_guardrail_evidence_definitions": ["internal_normalizer", "table_config_normalizer"],
    "_canonical_catalogue_profile_df": ["internal_normalizer", "catalogue_payload_normalizer"],
    "_normalize_catalogue_evidence_types": ["internal_normalizer", "catalogue_payload_normalizer"],
    "build_guardrail_summary_rows": ["internal_normalizer", "display_payload_normalizer"],
    "build_guardrail_detail_rows": ["internal_normalizer", "display_payload_normalizer"],
    "_add_audit_columns": ["internal_normalizer", "audit_field_normalizer"],
    "_definition_name": ["utility_function", "table_identity_formatter"],
    "_table_key": ["utility_function", "table_identity_formatter"],
    "_table_name": ["utility_function", "table_identity_formatter"],
    "_now_iso": ["utility_function", "timestamp_helper"],
    "_summary_status": ["utility_function", "status_mapping_helper"],
    "_result_status": ["utility_function", "status_mapping_helper"],
    "_result_can_continue": ["utility_function", "status_mapping_helper"],
    "_result_reason": ["utility_function", "message_formatter"],
    "_next_action": ["utility_function", "message_formatter"],
    "_schema_reason": ["utility_function", "message_formatter"],
    "_freshness_reason": ["utility_function", "message_formatter"],
    "_profile_behavior_reason": ["utility_function", "message_formatter"],
    "_dq_reason": ["utility_function", "message_formatter"],
    "_guardrail_reason": ["utility_function", "message_formatter"],
    "_table_keys": ["utility_function", "dict_list_helper"],
    "_blocking_guardrail_message": ["utility_function", "message_formatter"],
    "_build_guardrail_blocking_message_from_bundle": ["internal_normalizer", "display_payload_normalizer"],
    "write_catalogue_evidence": ["internal_adapter", "metadata_write_adapter"],

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
}

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
    if qn in public_qn_set:
        return "public", "classified"
    node = node_by_qn[qn]
    if node.get("callable_kind") == "implicit_lifecycle_method":
        return "internal", "implicit_lifecycle"
    if node.get("callable_kind") == "property_accessor":
        return "internal", "property_accessor"
    outbound_project = {callee for callee in calls_by_qn.get(qn, []) if callee in node_by_qn}
    layer = "utility" if node.get("is_underscore") and not outbound_project else "internal"
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
    if caller_layer == "utility" and callee_layer in {"public", "internal", "utility"}:
        return ["utility_calls_project_callable"]
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
                "layer": layer_by_qn.get(qn, "internal"),
                "review_status": review_status_by_qn.get(qn, "classification_pending"),
                "callable_kind": node_by_qn[qn].get("callable_kind", "unknown"),
                "callable_role": role_tags_by_qn.get(qn, []),
                "dependency_role": dependency_role_by_qn.get(qn, "unknown"),
            }
            for qn in sorted(qns, key=lambda item: (node_by_qn[item]["module_name"], node_by_qn[item]["callable_name"].lower()))
            if qn in node_by_qn
        ]

    inventory: list[dict[str, Any]] = []
    for qn in sorted(node_by_qn, key=lambda item: (node_by_qn[item]["module_name"], node_by_qn[item]["callable_name"].lower(), item)):
        node = node_by_qn[qn]
        layer = layer_by_qn[qn]
        function_type = CALLABLE_LAYER_LABELS[layer]
        refactor = refactor_by_qn.get(qn, {})
        public_summary = summary_by_qn.get(qn, {})
        outbound = [callee for callee in calls_by_qn.get(qn, []) if callee in node_by_qn]
        inbound = inbound_by_qn.get(qn, set())
        direct_helper_qns = {item["qualified_name"] for item in public_summary.get("direct_internal_helpers", [])}
        review_status = review_status_by_qn[qn]
        architecture_signals = sorted({
            signal
            for callee in outbound
            if review_status_by_qn.get(callee, "classification_pending") == "classified"
            for signal in _role_dependency_signals(
                dependency_role_by_qn[qn],
                dependency_role_by_qn.get(callee, "internal_workflow"),
            )
            if signal != "allowed_internal_role_call"
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
        callable_kind = node.get("callable_kind", "unknown")
        layer_consistency = _classify_layer_consistency(
            architecture_layer=function_type,
            callable_kind=callable_kind,
            used_by_count=used_by_count,
            calls_count=calls_count,
            has_architecture_violation=bool(architecture_signals),
        )
        consistency_signal = LAYER_CONSISTENCY_SIGNALS.get(layer_consistency)
        utility_dependency_signal = "Utility has outgoing dependencies" if function_type == "Utility" and calls_count > 0 else None
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
        elif layer == "utility":
            recommended_action = "Stable utility" if len(inbound) > 1 else "Inline candidate"
            priority = refactor.get("priority", "Low")
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
                "callable_role": role_tags_by_qn[qn],
                "architectural_role": dependency_role_by_qn[qn],
                "dependency_role": dependency_role_by_qn[qn],
                "reachability_kind": (
                    "public_entrypoint"
                    if qn in public_qn_set
                    else "implicit_lifecycle_reachable"
                    if review_status == "implicit_lifecycle" or qn in lifecycle_called_qns
                    else "unreachable_candidate"
                    if review_status == "unreachable"
                    else "directly_reachable"
                    if used_by_count
                    else "unknown_or_entrypoint"
                ),
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
                "deepest_call_chain_depth": public_summary.get("deepest_call_chain_depth") or refactor.get("nesting_level"),
                "repeated_helper_count": public_summary.get("repeated_helper_count", 0),
            }
        )
    summary_counts = {
        "total_callables": len(inventory),
        "total_functions": len(inventory),
        "function_type": {
            label: sum(1 for row in inventory if row["function_type"] == label)
            for label in CALLABLE_LAYER_LABELS.values()
        },
        "layer": {
            layer: sum(1 for row in inventory if row["layer"] == layer)
            for layer in CALLABLE_LAYER_LABELS
        },
        "review_status": {
            status: sum(1 for row in inventory if row["review_status"] == status)
            for status in REVIEW_STATUS_LABELS
        },
        "callable_kind": {
            label: sum(1 for row in inventory if row["callable_kind"] == label)
            for label in sorted({row["callable_kind"] for row in inventory})
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

def _build_callable_flow_data(
    public_qns: list[str],
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
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

    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "function_inventory": function_inventory,
        "summary_counts": summary_counts,
    }


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
    """Render the standalone static callable functions dashboard HTML page."""
    del flow_data
    return r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Callable Inventory and Refactor Signals</title>
  <style>
    :root { color-scheme: light; --border:#e2e8f0; --muted:#526070; --bg:#f8fafc; --blue:#2563eb; --red:#dc2626; --yellow:#a16207; --green:#15803d; --grey:#64748b; --soft:#ffffff; }
    * { box-sizing: border-box; }
    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; color: #1f2937; background: #fff; }
    header, main { max-width: none; margin: 0 auto; padding: 1rem; }
    header { border-bottom: 1px solid var(--border); background: linear-gradient(180deg,#fff,#f8fafc); }
    h1 { margin: 0 0 .35rem; } a { color: #0f5db8; }
    .summary-tree { margin:.5rem 0 .85rem; padding:.75rem; border:1px solid var(--border); border-radius:.9rem; background:#f8fafc; box-shadow:0 1px 2px rgba(15,23,42,.05); }
    .summary-tree h2 { margin:0 0 .55rem; font-size:1rem; color:#0f172a; } .summary-tree h3 { margin:.75rem 0 .35rem; padding:.35rem .45rem; border-left:4px solid #94a3b8; border-radius:.35rem; background:#e2e8f0; font-size:.76rem; color:#1e293b; text-transform:uppercase; letter-spacing:.075em; }
    .summary-tree h3.needs-action { border-left-color:var(--red); background:#fef2f2; color:#7f1d1d; } .summary-tree h3.protect-stable { border-left-color:var(--green); background:#f0fdf4; color:#14532d; } .summary-tree h3.diagnostic { border-left-color:var(--blue); background:#eff6ff; color:#1e3a8a; }
    .summary-tree ul { list-style:none; margin:0; padding:0; } .summary-tree li { margin:.16rem 0; }
    .summary-tree details { margin:.55rem 0 0; border:1px solid #dbe4ee; border-radius:.7rem; background:#fff; } .summary-tree details summary { padding:.45rem .55rem; border-radius:.7rem; color:#334155; font-size:.76rem; font-weight:800; text-transform:uppercase; letter-spacing:.065em; cursor:pointer; } .summary-tree details[open] summary { border-bottom:1px solid #e2e8f0; border-radius:.7rem .7rem 0 0; background:#f8fafc; } .summary-tree details ul { padding:.35rem; }
    .summary-total { margin:0 0 .65rem; } .summary-total .tree-row { align-items:center; padding:.65rem .75rem; border:1px solid #bfdbfe; background:linear-gradient(135deg,#eff6ff,#fff); box-shadow:inset 0 0 0 1px rgba(37,99,235,.04); } .summary-total .tree-row span { font-weight:800; color:#1e3a8a; } .summary-total .tree-row strong { font-size:1.35rem; color:#1d4ed8; }
    .tree-row { width:100%; display:flex; justify-content:space-between; align-items:center; gap:1rem; padding:.38rem .5rem; border:1px solid transparent; border-radius:.55rem; background:transparent; color:#1f2937; text-align:left; transition:background-color .12s ease,border-color .12s ease,box-shadow .12s ease,transform .12s ease; }
    .tree-row:hover, .tree-row:focus-visible { background:#e2e8f0; border-color:#cbd5e1; box-shadow:0 0 0 3px rgba(37,99,235,.12); outline:0; } .tree-row:active { transform:translateY(1px); } .tree-row.active { background:#dbeafe; border-color:#60a5fa; box-shadow:0 0 0 3px rgba(37,99,235,.14); } .tree-row strong { font-weight:800; font-variant-numeric:tabular-nums; }
    .tree-row.needs-action { border-left:4px solid var(--red); background:#fff7f7; } .tree-row.needs-action strong { color:#b91c1c; } .tree-row.needs-action:hover, .tree-row.needs-action:focus-visible, .tree-row.needs-action.active { background:#fee2e2; border-color:#fecaca; border-left-color:var(--red); }
    .tree-row.protect-stable { border-left:4px solid #86efac; background:#f8fff9; } .tree-row.protect-stable strong { color:#166534; } .tree-row.protect-stable:hover, .tree-row.protect-stable:focus-visible, .tree-row.protect-stable.active { background:#dcfce7; border-color:#bbf7d0; border-left-color:#22c55e; }
    .tree-row.diagnostic { border-left:4px solid #93c5fd; background:#f8fafc; color:#334155; } .tree-row.diagnostic strong { color:#1d4ed8; } .tree-row.diagnostic:hover, .tree-row.diagnostic:focus-visible, .tree-row.diagnostic.active { background:#eff6ff; border-color:#bfdbfe; border-left-color:#60a5fa; }
    .tree-row.zero-count { color:#64748b; opacity:.62; } .tree-row.zero-count strong { color:#64748b; }
    .helper-text { color: var(--muted); margin: .5rem 0 1rem; }
    .filter-panel { display: grid; grid-template-columns: minmax(240px, 1.3fr) repeat(8, minmax(130px, .7fr)) auto; gap: .55rem; align-items: end; margin: .75rem 0 1rem; padding: .75rem; border: 1px solid var(--border); border-radius: .9rem; background: #f1f5f9; }
    .filter-field { min-width: 0; display:grid; gap:.25rem; font-weight:700; }
    .filter-field select, .filter-field input { width:100%; box-sizing:border-box; }
    small, .hint { color: var(--muted); } input, select, button { font: inherit; padding: .48rem .6rem; border: 1px solid var(--border); border-radius: .55rem; background: #fff; } button { cursor:pointer; }
    .export-toolbar { display:flex; flex-wrap:wrap; gap:.5rem; align-items:center; margin:.75rem 0; padding:.55rem .65rem; border:1px solid var(--border); border-radius:.8rem; background:#f1f5f9; } .export-toolbar strong{margin-right:auto;} .compat-field{display:flex; align-items:center; gap:.35rem; font-weight:700; white-space:nowrap;} .compat-field select{padding:.35rem .5rem;} .compat-help{flex-basis:100%; margin-left:auto;} .export-toolbar button:disabled{opacity:.45; cursor:not-allowed;} .manual-copy { width:100%; min-height:8rem; margin-top:.5rem; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; } .legend { margin:.75rem 0 1rem; } .legend summary { cursor:pointer; font-weight:700; color:#334155; } .legend-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap:.5rem; margin-top:.6rem; } .legend-grid div { border:1px solid var(--border); border-radius:.7rem; padding:.65rem; background:#fff; }
    .table-wrap { overflow-x:auto; overflow-y:visible; border:1px solid var(--border); border-radius:.75rem; background:#fff; max-width:100%; }
    table { width:100%; border-collapse:separate; border-spacing:0; min-width:1180px; table-layout:fixed; }
    th, td { min-width:0; padding:.34rem .4rem; border-bottom:1px solid var(--border); text-align:left; vertical-align:top; overflow:hidden; overflow-wrap:anywhere; line-height:1.2; }
    th { background:var(--bg); position:sticky; top:0; z-index:1; font-size:.78rem; vertical-align:bottom; }
    th button { border:0; background:transparent; font-weight:800; padding:0; text-align:left; }
    .col-select { width:2.5rem; text-align:center; } .col-callable { width:12rem; } .col-module { width:10rem; } .col-role { width:16rem; } .col-reach { width:10rem; } .col-action { width:12rem; } .col-risk { width:7rem; } .col-used-by, .col-calls { width:5rem; }
    .num { text-align:right; white-space:nowrap; font-variant-numeric:tabular-nums; }
    .chip-wrap { display:flex; flex-wrap:wrap; align-items:flex-start; gap:.12rem .16rem; min-width:0; max-width:100%; }
    .tag,.badge { display:inline-flex; align-items:center; max-width:100%; min-width:0; margin:0; padding:.08rem .28rem; border-radius:999px; font-size:.68rem; font-weight:700; line-height:1.1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; vertical-align:middle; }
    .tag { background:#eef2ff; color:#3730a3; } .badge.high { background:#fee2e2; color:#991b1b; } .badge.medium { background:#fef3c7; color:#92400e; } .badge.protect { background:#dcfce7; color:#166534; } .badge.review { background:#e2e8f0; color:#334155; } .badge.public { background:#dbeafe; color:#1e40af; } .badge.internal { background:#dcfce7; color:#166534; } .badge.unreachable { background:#f1f5f9; color:#475569; }
    .details td { background:#f8fafc; overflow:visible; } .details-panel { border:1px solid var(--border); border-radius:.75rem; background:#fff; padding:.7rem; } .details-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap:.7rem; } .details ul { margin:0; padding-left:1.15rem; } code { white-space:normal; } .action-cell{white-space:nowrap; min-width:0; padding:.22rem .38rem;} .function-name code{font-size:.86rem;} .signal-reason{margin:0 0 .55rem; padding:.45rem .55rem; background:#f8fafc; border-radius:.55rem;} .notes-cell{font-size:.76rem; color:var(--muted);} .qualified-cell code,.module-cell code{font-size:.75rem;}
    @media (max-width: 1100px) { .filter-panel { grid-template-columns: repeat(2, minmax(220px, 1fr)); } .filter-field.search { grid-column: 1 / -1; } table { min-width: 1180px; } }
    @media (max-width: 640px) { header, main { padding:.75rem; } .filter-panel { grid-template-columns: 1fr; } .filter-field.search { grid-column:auto; } .export-toolbar, .compat-field { align-items:stretch; flex-direction:column; } .export-toolbar strong { margin-right:0; } table { min-width: 1180px; } .tag,.badge { max-width:9rem; } }
  </style>
</head>
<body>
<header>
  <h1>Callable Inventory and Refactor Signals</h1>
  <p>Browse discovered callables by action, protection value, and classification health so maintainers can review the riskiest work first.</p>
  <p><a href="../reference/callable-flow/">Back to Callable Functions Flow</a> · <a href="../reference/_data/callable-flow.json">Open JSON data</a></p>
</header>
<main>
  <section id="summaryTree" class="summary-tree" aria-label="Function summary tree"></section>
  <p class="helper-text"><strong>Architecture review</strong> means dependency direction may break the public -&gt; workflow -&gt; utility/model rule. <strong>Protect</strong> means high fanout, public, lifecycle, or model callables should not be casually refactored. <strong>Inline candidate</strong> means possible cleanup only if readability improves and tests exist.</p>
  <section class="filter-panel" aria-label="Inventory filters">
    <label class="filter-field search">Callable <input id="searchBox" type="search" placeholder="Search callables"></label>
    <label class="filter-field">Kind <select id="kindFilter"><option value="">All kinds</option></select></label>
    <label class="filter-field">Layer <select id="typeFilter"><option value="">All layers</option></select></label>
    <label class="filter-field">Review status <select id="reviewStatusFilter"><option value="">All review statuses</option></select></label>
    <label class="filter-field">Module <select id="moduleFilter"><option value="">All modules</option></select></label>
    <label class="filter-field">Recommended action <select id="signalFilter"><option value="">All recommended actions</option></select></label>
    <label class="filter-field">Callable role <select id="callableRoleFilter"><option value="">All callable roles</option></select></label>
    <label class="filter-field">Dependency role <select id="dependencyRoleFilter"><option value="">All dependency roles</option></select></label>
    <label class="filter-field">Reachability <select id="reachabilityFilter"><option value="">All reachability kinds</option></select></label>
    <button type="button" id="resetFilters">Reset</button>
  </section>
  <details class="legend" id="actionLegend"><summary>How signals are classified</summary><div class="legend-grid" id="actionLegendGrid"></div></details>
  <section class="export-toolbar" aria-label="Refactor packet export controls">
    <strong id="selectedCount">Selected: 0 callables</strong>
    <label class="compat-field">Compatibility mode <select id="compatibilityMode"><option value="stable_api_safe">Stable API safe</option><option value="internal_cleanup" selected>Internal cleanup</option><option value="development_breaking_allowed">Development, breaking changes allowed</option></select></label>
    <small id="compatibilityHelp" class="compat-help">Balanced default: preserve external behavior, but allow internal helper names, signatures, and boundaries to change when justified.</small>
    <button type="button" id="selectVisible">Select visible</button>
    <button type="button" id="clearSelected">Clear selection</button>
    <button type="button" id="copyJson" disabled>Copy JSON</button>
    <button type="button" id="copyMarkdown" disabled>Copy Markdown</button>
    <button type="button" id="downloadJson" disabled>Download JSON</button>
    <small id="exportStatus" role="status" aria-live="polite">Select at least one callable to export.</small>
    <textarea id="manualCopy" class="manual-copy" hidden readonly aria-label="Manual copy refactor packet"></textarea>
  </section>
  <p id="resultCount"></p>
  <section class="table-wrap" aria-label="Combined callable inventory"><table><thead><tr><th class="col-select"><input id="selectAllVisible" type="checkbox" aria-label="Select all visible rows"></th><th class="col-callable"><button type="button" data-sort="function_name">Callable</button></th><th class="col-module"><button type="button" data-sort="module">Module</button></th><th class="col-role">Role</th><th class="col-reach"><button type="button" data-sort="reachability_kind">Reachability</button></th><th class="col-action">Recommended action</th><th class="col-risk"><button type="button" data-sort="priority">Risk</button></th><th class="col-used-by num"><button type="button" data-sort="used_by_count">Callers</button></th><th class="col-calls num"><button type="button" data-sort="calls_count">Callees</button></th></tr></thead><tbody id="inventoryBody"></tbody></table></section>
</main>
<script>
let inventory = []; let summary = {}; const actionLegend = {
  "Public API entrypoint": "Supported user-facing API surface; no inbound project calls are required.",
  "Shared internal helper": "Internal implementation helper used by multiple public or internal callers; protect with focused tests before changing.",
  "Stable utility": "Low-level leaf helper with multiple inbound callers; keep generic and project-callable free.",
  "Inline candidate": "Small helper or single-use utility; consider flattening into its caller after checking readability.",
  "Review abstraction value": "Helper used by only one function; verify the name, boundary, and test value justify keeping it separate.",
  "Review manually": "No clear automated recommendation; inspect intent before changing structure.",
  "Architecture violation": "Callable dependency direction breaks the public → internal → utility layer rule.",
  "Orphaned callable": "Private callable with no reachable public lineage; remove or reconnect if still needed."
}; const layerConsistencyLabels = {
  matches_layer: "Matches expected layer",
  stable_utility: "Stable utility",
  questionable_utility: "Questionable utility",
  promote_to_utility_candidate: "Promote to utility candidate",
  shared_internal_helper: "Shared internal helper",
  possible_inline_or_private_helper: "Possible inline/private helper",
  architecture_violation: "Architecture violation",
  review_manually: "Review manually"
}; const signalTooltips = {
  "Utility but low reuse": "This callable is classified as Utility, but is used by 0–1 discovered callables. Review whether it should remain a shared utility or be demoted to an internal/private helper.",
  "Internal helper with high reuse": "This callable is classified as Internal helper, but is used by many callables. Review whether it should become a stable utility or remain a shared domain helper.",
  "Utility has outgoing dependencies": "This callable is classified as Utility, but calls other discovered callables. Review whether it violates the expected low-level utility dependency rule.",
  "Layer assignment needs review": "Layer assignment needs review against observed call graph usage.",
  "Promote candidate": "Internal helper with high reuse; review whether it should become a utility.",
  "Shared helper": "Internal helper reused by multiple callables; protect or promote intentionally."
}; const reasonLabels = {
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
  "Utility but low reuse": "Utility but low reuse",
  "Internal helper with high reuse": "Internal helper with high reuse",
  "Utility has outgoing dependencies": "Utility has outgoing dependencies",
  "Layer assignment needs review": "Layer assignment needs review",
  "Promote candidate": "Promote candidate",
  "Shared helper": "Shared helper"
};

const AI_PROMPT = 'You are reviewing a FabricOps callable refactor packet. Use the selected callables and call graph metadata to plan a safe cleanup. Group callables by refactor type, explain the rationale, identify risks, and propose an ordered implementation plan. Do not write code yet. Respect the compatibility mode in this packet. If compatibility_mode is stable_api_safe, preserve public API compatibility and call out migration risks. If compatibility_mode is internal_cleanup, preserve external behavior but allow internal signatures and helper boundaries to change when justified. If compatibility_mode is development_breaking_allowed, propose cleaner breaking changes where they improve the design. Batch accounting: report how many callables were selected, how many are intended for the current batch, how many were actually refactored in the PR, which selected callables were deferred, why each deferred group was deferred, and what the next suggested batch should be. Do not imply that all selected callables were refactored unless they were actually changed. If this PR handles only a subset, clearly label it as a batch and list the remaining selected callables as deferred. Completion accounting required in PR description: include selected / handled / remaining counts in the PR body and fill completed_or_refactored_count after implementation if it was unknown at export time. Always call out tests required before changes. Review the assigned layer against the usage evidence. Do not assume that a Utility layer is correct when used_by_count is low, and do not assume that a highly reused Internal helper must remain internal.';
const refactorGuidance = {
  'Inline candidate': ['inline_candidate', 'Likely small helper or wrapper. Consider inlining only if it improves readability and does not duplicate validation logic.'],
  'Merge candidate': ['merge_candidate', 'Likely adjacent helper responsibility. Review whether this should be consolidated with related helpers.'],
  'Review abstraction value': ['abstraction_review', 'Single-use helper. Check whether the boundary improves naming, testing, validation, or readability.'],
  'Review manually': ['manual_review', 'Automated signal is inconclusive. Inspect intent, callers, and tests before recommending changes.'],
  'Public API entrypoint': ['public_entrypoint', 'Supported public API. Preserve notebook-facing behavior and avoid hidden orchestration chains.'],
  'Stable utility': ['stable_utility', 'Leaf utility. Keep generic and free of project-callable dependencies.'],
  'Shared internal helper': ['shared_internal_helper', 'Shared implementation helper. Refactor only with focused tests and caller review.'],
  'Architecture violation': ['architecture_violation', 'Dependency direction breaks the public → internal → utility rule. Review before cleanup.'],
  'Orphaned callable': ['orphaned_callable', 'No public lineage. Remove or reconnect if still needed.']
};
const compatibilityModes = {
  stable_api_safe: {label:'Stable API safe', description:'Most conservative: preserve public APIs and notebook-facing behavior. Recommend only safe internal cleanup.', instruction:'Preserve public API compatibility. Any breaking change must be called out as a migration risk.', safety_constraints:['Preserve public API compatibility','Call out any breaking change as a migration risk','Avoid changing notebook facing behavior without explicit approval']},
  internal_cleanup: {label:'Internal cleanup', description:'Balanced default: preserve external behavior, but allow internal helper names, signatures, and boundaries to change when justified.', instruction:'Preserve notebook facing and external behavior, but internal helper signatures, names, and module boundaries can change if justified.', safety_constraints:['Preserve external behavior','Internal helper names, signatures, and module boundaries may change if justified','Identify impacted callers before recommending changes']},
  development_breaking_allowed: {label:'Development, breaking changes allowed', description:'Most flexible: breaking changes are allowed when they simplify new or experimental code.', instruction:'Selected callables are new, experimental, or not live yet. Breaking changes are allowed when they simplify the design, improve naming, remove weak abstractions, or make the API cleaner.', safety_constraints:['Breaking changes are allowed if they simplify the design','Prefer cleaner names, simpler boundaries, and fewer weak abstractions','Still call out affected callers and tests']}
};
const priorityRank = {High:0, Medium:1, Review:2, Low:3, Protect:4}; const actionRank = {'Architecture violation':0, 'Orphaned callable':1, 'Inline candidate':2, 'Review manually':3, 'Review abstraction value':4, 'Shared internal helper':5, 'Stable utility':6, 'Public API entrypoint':7}; const state = {search:'', type:'', kind:'', review_status:'', module:'', signal:'', consistency:'', callable_role:'', dependency_role:'', reachability_kind:'', compatibility_mode:'internal_cleanup', sortKey:'action_first', sortDir:1, expanded:new Set(), selected:new Set(), activeTree:'', openSummarySections:new Set()};
const $ = (id) => document.getElementById(id); const text = (v) => String(v ?? ''); const esc = (v) => text(v).replace(/[&<>"']/g, (ch) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
function unique(v) { return [...new Set(v.filter(Boolean))].sort((a,b)=>a.localeCompare(b)); } function option(s,v) { const o=document.createElement('option'); o.value=v; o.textContent=v; s.appendChild(o); }
function countBy(predicate) { return inventory.filter(predicate).length; }
function summaryCount(group, label, predicate) { return inventory.length ? countBy(predicate) : (summary[group]?.[label] ?? 0); }
function hasRole(i, role) { return (i.callable_role || []).includes(role); }
function actionPredicate(label) { return (i) => i.recommended_action===label || (label==='Manual review' && i.recommended_action==='Review manually'); }
const USER_FACING_RECOMMENDED_ACTIONS=['Architecture violation','Inline candidate','Review abstraction value','Review manually','Public API entrypoint','Stable utility','Shared internal helper','Orphaned callable','Unreachable candidate'];
function rolePredicate(role) { return (i) => hasRole(i, role) || i.dependency_role===role; }
function syncTreeActive() { if(!state.type && !state.kind && !state.review_status && !state.module && !state.signal && !state.consistency && !state.callable_role && !state.dependency_role && !state.reachability_kind) state.activeTree = state.activeTree === 'total' ? 'total' : ''; else state.activeTree = ''; }
function treeButton(key, label, value, tone='') { const count=value ?? 0; const classes=['tree-row', tone, state.activeTree===key?'active':'', count===0?'zero-count':''].filter(Boolean).join(' '); return `<li><button type="button" class="${classes}" data-tree="${esc(key)}"><span>${esc(label)}</span><strong>${esc(count)}</strong></button></li>`; }
function countSignal(signal) { return countBy(i=>(i.architecture_signals || []).includes(signal) || (i.review_signals || []).includes(signal) || (i.signals || []).includes(signal)); }
function summarySectionKey(title) { return text(title).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''); }
function renderCountSection(title, rows) { const key=summarySectionKey(title); const open=state.openSummarySections.has(key)?' open':''; return `<details class="legend" data-summary-section="${esc(key)}"${open}><summary data-summary-header="${esc(key)}">${esc(title)}</summary><ul>${rows.join('')}</ul></details>`; }
function renderTreeSummary() {
  const needs=[['action:Architecture violation','Architecture review', actionPredicate('Architecture violation')], ['action:Orphaned callable','Orphan candidates', actionPredicate('Orphaned callable')], ['action:Inline candidate','Inline candidates', actionPredicate('Inline candidate')], ['action:Review manually','Manual review', actionPredicate('Manual review')]];
  const protect=[['role:public_api_entrypoint','Public API entrypoints', rolePredicate('public_api_entrypoint')], ['role:shared_internal_service','Shared internal services', rolePredicate('shared_internal_service')], ['role:config_model_class','Config model classes', rolePredicate('config_model_class')], ['role:result_context_model','Result/context model classes', i=>hasRole(i,'result_model_class') || hasRole(i,'context_model_class') || i.dependency_role==='result_model_class' || i.dependency_role==='context_model_class'], ['role:lifecycle_method','Lifecycle methods', rolePredicate('lifecycle_method')], ['action:Stable utility','Stable utilities', actionPredicate('Stable utility')]];
  const health=[['role:unknown','Unknown role', rolePredicate('unknown')], ['role:unreachable_candidate','Unreachable candidate', rolePredicate('unreachable_candidate')], ['reach:classification_pending','Classification pending', i=>i.reachability_kind==='classification_pending' || i.review_status==='classification_pending'], ['signal:allowed_internal_role_call','Allowed internal role calls', i=>(i.architecture_signals || []).includes('allowed_internal_role_call')]];
  const grouped=(title, rows, tone)=>`<h3 class="${esc(tone)}">${esc(title)}</h3><ul>${rows.map(([key,label,pred])=>treeButton(key,label,countBy(pred),tone)).join('')}</ul>`;
  const layers=unique([...Object.keys(summary.function_type || {}), ...inventory.map(i=>i.function_type)]).map(label=>treeButton(`type:${label}`, label, summaryCount('function_type', label, i=>i.function_type===label), 'diagnostic'));
  const kinds=unique([...Object.keys(summary.callable_kind || {}), ...inventory.map(i=>i.callable_kind)]).map(label=>treeButton(`kind:${label}`, text(label).replace(/^./, c=>c.toUpperCase()), summaryCount('callable_kind', label, i=>i.callable_kind===label), 'diagnostic'));
  const consistency=Object.entries(layerConsistencyLabels).filter(([key])=>(summary.layer_consistency?.[key] ?? countBy(i=>i.layer_consistency===key))>0).map(([key,label])=>treeButton(`consistency:${key}`, label, summaryCount('layer_consistency', key, i=>i.layer_consistency===key), 'diagnostic'));
  const raw=unique([...inventory.flatMap(i=>i.architecture_signals || []), ...inventory.flatMap(i=>i.review_signals || []), ...inventory.flatMap(i=>i.signals || [])]).map(sig=>treeButton(`signal:${sig}`, reasonLabels[sig] || sig, countSignal(sig), 'diagnostic'));
  $('summaryTree').innerHTML=`<h2>Action-oriented summary</h2><ul class="summary-total">${treeButton('total','Total callables', inventory.length || summary.total_callables || summary.total_functions || 0)}</ul>${grouped('Needs action', needs, 'needs-action')}${grouped('Protect / keep stable', protect, 'protect-stable')}${grouped('Classification health', health, 'diagnostic')}${renderCountSection('Layer counts', layers)}${renderCountSection('Callable kind counts', kinds)}${renderCountSection('Layer consistency counts', consistency)}${renderCountSection('Raw signal counts', raw)}`;
}
function renderLegend() { $('actionLegendGrid').innerHTML=`<div><strong>Kind</strong><p class="hint">Kind describes what the object is structurally: function, class, or method.</p></div><div><strong>Layer</strong><p class="hint">Layer describes the intended architecture role: Public API, Internal helper, or Utility.</p></div><div><strong>Usage evidence</strong><p class="hint">Used by count shows how many discovered callables call this callable. Calls count shows how many discovered callables this callable calls.</p></div><div><strong>Layer consistency</strong><p class="hint">Layer consistency compares the assigned layer against the observed call graph. A utility should normally be broadly reusable, low level, and dependency safe. A utility with low reuse, or an internal helper with high reuse, is marked for layer review instead of being automatically accepted.</p></div><div><strong>Recommended action</strong><p class="hint">Recommended action is the cleanup suggestion used for review and export.</p></div>`+Object.entries(actionLegend).map(([l,d])=>`<div><span class="badge review">${esc(l)}</span><p class="hint">${esc(d)}</p></div>`).join(''); }
function populateRecommendedActionFilter() { const present=new Set(inventory.map(i=>i.recommended_action).filter(Boolean)); USER_FACING_RECOMMENDED_ACTIONS.filter(v=>present.has(v)).forEach(v=>option($('signalFilter'),v)); }
function populateFilters() { unique(inventory.map(i=>i.callable_kind)).forEach(v=>option($('kindFilter'), text(v).replace(/^./, c=>c.toUpperCase()))); ['Public API','Internal helper','Utility'].forEach(v=>option($('typeFilter'),v)); ['Classified','Classification pending','Implicit lifecycle method','Property accessor','Unreachable'].forEach(v=>option($('reviewStatusFilter'),v)); unique(inventory.map(i=>i.module)).forEach(v=>option($('moduleFilter'),v)); populateRecommendedActionFilter(); unique(inventory.flatMap(i=>i.callable_role || [])).forEach(v=>option($('callableRoleFilter'),v)); unique(inventory.map(i=>i.dependency_role)).forEach(v=>option($('dependencyRoleFilter'),v)); unique(inventory.map(i=>i.reachability_kind)).forEach(v=>option($('reachabilityFilter'),v)); }
function filteredRows() { const q=state.search.trim().toLowerCase(); return inventory.filter(i=>(!q || text(i.function_name).toLowerCase().includes(q)) && (!state.kind || i.callable_kind===state.kind.toLowerCase()) && (!state.type || i.function_type===state.type) && (!state.review_status || i.review_status_label===state.review_status) && (!state.module || i.module===state.module) && (!state.signal || i.recommended_action===state.signal) && (!state.callable_role || (i.callable_role || []).includes(state.callable_role)) && (!state.dependency_role || i.dependency_role===state.dependency_role) && (!state.reachability_kind || i.reachability_kind===state.reachability_kind) && (!state.consistency || i.layer_consistency===state.consistency)); }
function signalReason(i) { const signals=(i.signals || []).map(s=>reasonLabels[s] || s); if(i.recommended_action && actionLegend[i.recommended_action]) return `${i.recommended_action}: ${actionLegend[i.recommended_action]}`; if(signals.length) return signals.join(', '); return 'No automated signal reason is available yet.'; }
function compare(a,b) { const k=state.sortKey; if(k==='action_first') return ((priorityRank[a.priority]??9)-(priorityRank[b.priority]??9))*state.sortDir || ((actionRank[a.recommended_action]??9)-(actionRank[b.recommended_action]??9))*state.sortDir || text(a.module).localeCompare(text(b.module)) || text(a.function_name).localeCompare(text(b.function_name)); if(k==='priority') return ((priorityRank[a.priority]??9)-(priorityRank[b.priority]??9))*state.sortDir || a.function_name.localeCompare(b.function_name); if(typeof a[k]==='number') return (a[k]-b[k])*state.sortDir; return text(a[k]).localeCompare(text(b[k]))*state.sortDir; }
function linkedList(items) { return items.length ? `<ul>${items.map(i=>`<li><a href="${esc(i.source_url || '#')}">${esc(i.function)}</a> <small>(${esc(i.module)})</small></li>`).join('')}</ul>` : '<p>—</p>'; }
function chips(item) { const content=(item.signals || []).map(s=>`<span class="tag" title="${esc(signalTooltips[s] || reasonLabels[s] || s)}">${esc(reasonLabels[s] || s)}</span>`).join('') || `<span class="badge review" title="${esc(item.recommended_action)}">${esc(item.recommended_action)}</span>`; return `<span class="chip-wrap">${content}</span>`; }
function exportFilters() { return {callable:state.search, kind:state.kind, layer:state.type, review_status:state.review_status, module:state.module, recommended_action:state.signal, callable_role:state.callable_role, dependency_role:state.dependency_role, reachability_kind:state.reachability_kind}; }
function guidanceFor(action) { return refactorGuidance[action] || ['manual_review', 'Automated signal is inconclusive. Inspect intent, callers, and tests before recommending changes.']; }
function exportItem(i) { const [refactor_type, refactor_guidance]=guidanceFor(i.recommended_action); return {function_name:i.function_name, qualified_name:i.qualified_name, module:i.module, function_type:i.function_type, layer:i.layer, callable_kind:i.callable_kind, visibility:i.visibility, architecture_signals:i.architecture_signals || [], review_signals:i.review_signals || [], review_status:i.review_status, review_status_label:i.review_status_label, callable_role:i.callable_role || [], architectural_role:i.architectural_role, reachability_kind:i.reachability_kind, dependency_role:i.dependency_role, change_risk:i.change_risk, refined_recommended_action:i.refined_recommended_action, recommended_action:i.recommended_action, priority:i.priority, signals:i.signals || [], signal_reason:signalReason(i), refactor_type, refactor_guidance, used_by_count:i.used_by_count ?? i.called_by_count, called_by_count:i.called_by_count, calls_count:i.calls_count, layer_consistency:i.layer_consistency, layer_consistency_label:i.layer_consistency_label || layerConsistencyLabels[i.layer_consistency], callers:i.callers || [], callees:i.callees || [], direct_internal_helpers:i.direct_internal_helpers || [], source_path:i.source_path, source_url:i.source_url, deepest_call_chain_depth:i.deepest_call_chain_depth, repeated_helper_count:i.repeated_helper_count}; }
function selectedItems() { const byId=new Map(inventory.map(i=>[i.qualified_name,i])); return [...state.selected].map(id=>byId.get(id)).filter(Boolean); }
function compatibilityContext() { return compatibilityModes[state.compatibility_mode] || compatibilityModes.internal_cleanup; }
function refactorContext(callables) { const compatibility=compatibilityContext(); return {selected_callable_actions:unique(callables.map(fn=>fn.recommended_action)), refactor_intent:'Plan safe cleanup for selected FabricOps helper callables.', refactor_mode:'planning_only', compatibility_mode:state.compatibility_mode, compatibility_instruction:compatibility.instruction, likely_refactor_actions:['Inline thin wrappers where readability improves','Merge adjacent helpers with overlapping responsibility','Keep helpers separate when naming, validation boundaries, or tests justify the abstraction'], safety_constraints:compatibility.safety_constraints, expected_ai_output:['Group selected callables by refactor type','Explain which callables are safe cleanup candidates','Identify callables that should not be refactored yet','Propose an ordered refactor plan','Report selected, intended batch, actually refactored, deferred, and remaining callable counts','List risks and required tests','Do not produce code changes unless explicitly requested']}; }
function batchAccounting(callables) { const selectedCount=callables.length; return {selected_count:selectedCount, selected_callable_count:selectedCount, planned_batch_count:selectedCount, batch_id:'batch-1', batch_scope:'All selected callables by default; narrow this before implementation when a smaller safe batch is intended.', batch_strategy:'Single batch by default. If implementation handles only a subset, group deferred selected callables by risk, ownership, or dependency order.', completed_or_refactored_count:null, remaining_selected_count:null, deferred_selected_callables:[]}; }
function refactorPacket() { const callables=selectedItems().map(exportItem), accounting=batchAccounting(callables); return {export_type:'fabricops_callable_refactor_packet', generated_from:'Callable Inventory and Refactor Signals', ...accounting, filters:exportFilters(), refactor_context:refactorContext(callables), batch_accounting:accounting, ai_prompt:AI_PROMPT, callables, functions:callables}; }
function markdownList(label, items) { return [label, ...items.map(item=>`- ${item}`)]; }
function markdownPacket() { const packet=refactorPacket(), ctx=packet.refactor_context, acct=packet.batch_accounting; const lines=['FabricOps callable refactor packet','','Prompt for AI','',packet.ai_prompt,'','Refactor context','',`Intent: ${ctx.refactor_intent}`,'','Mode: Planning only.','',`Compatibility mode: ${compatibilityContext().label}`,'','Compatibility instruction:',ctx.compatibility_instruction,'','Batch accounting','',`Selected callables: ${acct.selected_callable_count}`,`Planned batch count: ${acct.planned_batch_count}`,`Batch ID: ${acct.batch_id}`,`Batch scope: ${acct.batch_scope}`,`Batch strategy: ${acct.batch_strategy}`,`Completed/refactored count: fill in after implementation`, 'Remaining selected count: fill in after implementation','Deferred selected callables: none by default before implementation; list any selected callables not handled in this PR.','', 'Completion accounting required in PR description','', 'Include selected / handled / remaining counts in the PR body. Do not imply that all selected callables were refactored unless they were actually changed. If this PR handles only a subset, clearly label it as a batch and list the remaining selected callables as deferred. Explain why each deferred group was deferred and recommend the next batch.','',...markdownList('Selected callable actions:', ctx.selected_callable_actions), '', ...markdownList('Likely refactor actions:', ctx.likely_refactor_actions), '', ...markdownList('Safety constraints:', ctx.safety_constraints), '', ...markdownList('Expected AI output:', ctx.expected_ai_output), '', 'Selected callables', '']; packet.callables.forEach((fn,idx)=>{ lines.push(`Callable ${idx+1}: ${fn.function_name}`,'',`Qualified name: ${fn.qualified_name}`,`Module: ${fn.module}`,`Kind: ${fn.callable_kind}`,`Layer: ${fn.function_type}`,`Used by count: ${fn.used_by_count}`,`Calls count: ${fn.calls_count}`,`Layer consistency: ${fn.layer_consistency_label || fn.layer_consistency}`,`Review status: ${fn.review_status_label || fn.review_status}` ,`Recommended action: ${fn.recommended_action}`,`Priority: ${fn.priority}`,`Refactor type: ${fn.refactor_type}`,`Refactor guidance: ${fn.refactor_guidance}`,`Signal reason: ${fn.signal_reason}`,`Caller count: ${fn.called_by_count}`,`Callee count: ${fn.calls_count}`,'','Callers:',...(fn.callers.length?fn.callers.map(c=>`- ${c.function} (${c.module}) ${c.source_path || ''}`):['- —']),'','Callees:',...(fn.callees.length?fn.callees.map(c=>`- ${c.function} (${c.module}) ${c.source_path || ''}`):['- —']),'','Direct internal helpers:',...(fn.direct_internal_helpers.length?fn.direct_internal_helpers.map(h=>`- ${h.function} (${h.module}) ${h.source_path || ''}`):['- —']),'',`Source path: ${fn.source_path || 'Source unavailable'}`,`Source URL: ${fn.source_url || 'Source unavailable'}`,''); }); return lines.join('\n'); }
function showManualCopy(textValue) { const area=$('manualCopy'); area.hidden=false; area.value=textValue; area.focus(); area.select(); }
async function copyExport(format) { const items=selectedItems(); if(!items.length){ $('exportStatus').textContent='Select at least one callable to export.'; return; } const output=format==='json'?JSON.stringify(refactorPacket(), null, 2):markdownPacket(); if(navigator.clipboard?.writeText){ await navigator.clipboard.writeText(output); $('manualCopy').hidden=true; $('exportStatus').textContent=`Copied ${format.toUpperCase()} for ${items.length} callables.`; } else { showManualCopy(output); $('exportStatus').textContent='Clipboard unavailable. Copy the refactor packet from the text box.'; } }
function downloadJson() { const items=selectedItems(); if(!items.length){ $('exportStatus').textContent='Select at least one callable to export.'; return; } const stamp=new Date().toISOString().replace(/[-:]/g,'').replace(/T/,'_').slice(0,15); const blob=new Blob([JSON.stringify(refactorPacket(), null, 2)], {type:'application/json'}); const link=document.createElement('a'); link.href=URL.createObjectURL(blob); link.download=`fabricops_refactor_packet_${stamp}.json`; link.click(); URL.revokeObjectURL(link.href); $('exportStatus').textContent=`Downloaded JSON for ${items.length} callables.`; }
function renderExportToolbar(rows) { const selected=selectedItems().length, visible=rows.filter(i=>state.selected.has(i.qualified_name)).length; $('selectedCount').textContent=`Selected: ${selected} callables${selected && visible!==selected?`, ${visible} visible`:''}`; ['copyJson','copyMarkdown','downloadJson'].forEach(id=>$(id).disabled=!selected); const allVisible=rows.length>0 && rows.every(i=>state.selected.has(i.qualified_name)); const selectAll=$('selectAllVisible'); selectAll.checked=allVisible; selectAll.indeterminate=!allVisible && rows.some(i=>state.selected.has(i.qualified_name)); }
function renderTable() { const rows=filteredRows().sort(compare); renderExportToolbar(rows); $('resultCount').textContent=`Showing ${rows.length} of ${inventory.length} discovered callables.`; $('inventoryBody').innerHTML=rows.map(i=>{ const id=i.qualified_name; return `<tr><td class="col-select"><input type="checkbox" data-select-row="${esc(id)}" aria-label="Select ${esc(i.function_name)}" ${state.selected.has(id)?'checked':''}></td><td class="col-callable function-name" title="${esc(i.qualified_name)}"><a href="${esc(i.source_url || '#')}"><code>${esc(i.function_name)}</code></a><br><small>${esc(i.callable_kind)} · ${esc(i.review_status_label || i.review_status)}</small></td><td class="col-module module-cell"><code>${esc(i.module)}</code></td><td class="col-role"><span class="chip-wrap">${(i.callable_role || [i.dependency_role || 'unknown']).map(r=>`<span class="tag">${esc(r)}</span>`).join('')}</span></td><td class="col-reach"><span class="badge review">${esc(i.reachability_kind || 'unknown')}</span></td><td class="col-action"><span class="chip-wrap"><span class="badge review" title="${esc(signalReason(i))}">${esc(i.recommended_action)}</span></span></td><td class="col-risk"><span class="badge review">${esc(i.priority || i.change_risk || 'Review')}</span></td><td class="col-used-by num">${esc(i.used_by_count ?? i.called_by_count)}</td><td class="col-calls num">${esc(i.calls_count)}</td></tr>`; }).join(''); }
function updateCompatibilityHelp() { $('compatibilityHelp').textContent=compatibilityContext().description; }
function update() { syncTreeActive(); renderTreeSummary(); renderTable(); } function resetFilters() { state.search=state.type=state.kind=state.review_status=state.module=state.signal=state.consistency=state.callable_role=state.dependency_role=state.reachability_kind=''; state.activeTree=''; ['searchBox','kindFilter','typeFilter','reviewStatusFilter','moduleFilter','signalFilter','callableRoleFilter','dependencyRoleFilter','reachabilityFilter'].forEach(id=>$(id).value=''); update(); }
function applyTree(key) { if(key.startsWith('role:')) { resetFilters(); state.callable_role=key.slice(5); $('callableRoleFilter').value=state.callable_role; state.activeTree=key; update(); return; } if(key.startsWith('reach:')) { resetFilters(); state.reachability_kind=key.slice(6); $('reachabilityFilter').value=state.reachability_kind; state.activeTree=key; update(); return; } if(key.startsWith('signal:')) { resetFilters(); state.activeTree=key; update(); return; } state.search=''; state.type=''; state.kind=''; state.review_status=''; state.module=''; state.signal=''; state.consistency=''; state.activeTree=key; $('searchBox').value=''; if(key.startsWith('type:')) state.type=key.slice(5); if(key.startsWith('kind:')) state.kind=key.slice(5); if(key.startsWith('review:')) state.review_status=key.slice(7); if(key.startsWith('action:')) state.signal=key.slice(7); if(key.startsWith('consistency:')) state.consistency=key.slice(12); $('kindFilter').value=state.kind ? state.kind[0].toUpperCase()+state.kind.slice(1) : ''; $('typeFilter').value=state.type; $('reviewStatusFilter').value=state.review_status; $('moduleFilter').value=state.module; $('signalFilter').value=state.signal; update(); }
$('searchBox').addEventListener('input', e=>{state.search=e.target.value; update();});
$('kindFilter').addEventListener('change', e=>{state.kind=e.target.value.toLowerCase(); state.activeTree=''; update();}); $('typeFilter').addEventListener('change', e=>{state.type=e.target.value; state.activeTree=''; update();}); $('reviewStatusFilter').addEventListener('change', e=>{state.review_status=e.target.value; state.activeTree=''; update();}); $('moduleFilter').addEventListener('change', e=>{state.module=e.target.value; state.activeTree=''; update();}); $('compatibilityMode').addEventListener('change', e=>{state.compatibility_mode=e.target.value; updateCompatibilityHelp();}); $('selectVisible').addEventListener('click', ()=>{filteredRows().forEach(i=>state.selected.add(i.qualified_name)); renderTable();}); $('clearSelected').addEventListener('click', ()=>{state.selected.clear(); renderTable(); $('exportStatus').textContent='Selection cleared.';}); $('copyJson').addEventListener('click', ()=>copyExport('json').catch(e=>{$('exportStatus').textContent=`Unable to copy JSON: ${e.message}`;})); $('copyMarkdown').addEventListener('click', ()=>copyExport('markdown').catch(e=>{$('exportStatus').textContent=`Unable to copy Markdown: ${e.message}`;})); $('downloadJson').addEventListener('click', downloadJson); $('selectAllVisible').addEventListener('change', e=>{const rows=filteredRows(); rows.forEach(i=>e.target.checked?state.selected.add(i.qualified_name):state.selected.delete(i.qualified_name)); renderTable();}); $('signalFilter').addEventListener('change', e=>{state.signal=e.target.value; state.activeTree=''; update();}); $('callableRoleFilter').addEventListener('change', e=>{state.callable_role=e.target.value; state.activeTree=''; update();}); $('dependencyRoleFilter').addEventListener('change', e=>{state.dependency_role=e.target.value; state.activeTree=''; update();}); $('reachabilityFilter').addEventListener('change', e=>{state.reachability_kind=e.target.value; state.activeTree=''; update();}); $('resetFilters').addEventListener('click', resetFilters);
document.addEventListener('click', e=>{ const sort=e.target.closest('[data-sort]'); if(sort){ const k=sort.dataset.sort; state.sortDir=state.sortKey===k?state.sortDir*-1:1; state.sortKey=k; update(); } const toggle=e.target.closest('[data-toggle]'); if(toggle){ const id=toggle.dataset.toggle; state.expanded.has(id)?state.expanded.delete(id):state.expanded.add(id); renderTable(); } const rowSelect=e.target.closest('[data-select-row]'); if(rowSelect){ rowSelect.checked?state.selected.add(rowSelect.dataset.selectRow):state.selected.delete(rowSelect.dataset.selectRow); renderTable(); } const tree=e.target.closest('[data-tree]'); if(tree){ e.stopPropagation(); applyTree(tree.dataset.tree); } });
document.addEventListener('toggle', e=>{ const section=e.target.closest?.('[data-summary-section]'); if(!section) return; section.open?state.openSummarySections.add(section.dataset.summarySection):state.openSummarySections.delete(section.dataset.summarySection); }, true);
async function loadData() { try { const response=await fetch('../reference/_data/callable-flow.json'); if(!response.ok) throw new Error(`HTTP ${response.status}`); const data=await response.json(); inventory=data.function_inventory || data.refactor_inventory || []; summary=data.summary_counts || {}; renderTreeSummary(); renderLegend(); updateCompatibilityHelp(); populateFilters(); renderTable(); } catch(error) { $('resultCount').textContent=`Unable to load callable-flow JSON: ${error.message}`; } } loadData();
</script>
</body>
</html>
"""


def _render_callable_flow_page(flow_data: dict[str, Any]) -> str:
    """Render the global callable flow Markdown page."""
    del flow_data
    return '''# Callable Flow Dashboard

AI coding tools make it easy to add callables quickly. That speed is useful, but it can also create too many entry points, thin wrapper callables, nested helpers, and uncontrolled dependencies. The Callable Flow Dashboard exists to make those relationships visible before the codebase becomes hard to maintain.

<div align="center" markdown="1">

[Open the interactive Callable Flow Dashboard](../assets/callable-functions-dashboard.html){ .md-button .md-button--primary }

</div>


## Why callable flow matters

FabricOps keeps notebook-facing APIs small and explainable. A callable should have a clear role in the callable hierarchy:

```text
Public callables → Internal helpers → Utility callables
```

The dependency rule is intentionally simple: a callable may call lower layers, but not the same layer or higher layers.

- Public callables may call internal helpers and utility callables.
- Internal helpers may call utility callables.
- Utility callables should be self-contained and should not call shared project callables.

This keeps public callables as stable entry points, internal helpers as reusable implementation details, and utility callables as low-risk building blocks.

## How the dashboard is generated

The dashboard is built from repository scans that inspect callable definitions and relationships. The scan produces callable relationship metadata in [`_data/callable-flow.json`](_data/callable-flow.json), and the visual dashboard uses that JSON to show caller and callee relationships, depth, reuse, and refactor recommendations.

Because the dashboard is generated from the codebase, it is a maintenance aid rather than a separate source of truth. Use it to decide where to inspect source code, update docstrings, flatten helper chains, or preserve shared helpers carefully.

## What the dashboard detects

Use the dashboard signals to find patterns that deserve review:

- public callables calling public callables
- internal helpers with too many dependencies
- deep nested helper chains
- low-value wrapper or inline candidates
- highly reused helpers that should be preserved carefully
- callables used by only one caller
- large dependency surfaces

## Refactor signals

Refactor signals are warnings generated from the callable graph. They do not automatically mean the code is wrong. Instead, they help guard against architecture drift from the intended public → internal → utility hierarchy and identify where cleanup should be reviewed before changes are made.

### EG. Pointless wrapper

![Possible wrapper or inline candidates](../assets/fabricops-bad-example-pointless-wrapper-functions.png)

*Guardrail: Warn when a helper appears to add little abstraction value. Single-use or thin wrapper callables may still be valid, but they should earn their place through clearer naming, validation, readability, or reuse.*

### EG. Large dependency surface

![Large dependency surface](../assets/fabricops-bad-example-large-surface-area.png)

*Guardrail: Warn when a public callable depends on many nested helpers. This may be valid orchestration, but it increases the chance that a small helper change breaks a wider workflow.*

### EG. Messy callable dependency

![Public callable dependency](../assets/fabricops-bad-example-function-dependancy.png)

*Guardrail: Warn when one public callable depends on another public callable. Public callables should usually be entry points. Shared logic should usually move into an internal helper or utility callable.*

### EG. Nested helper chain

![Nested helper chain](../assets/fabricops-bad-example-nested-functions.png)

*Guardrail: Warn when internal helpers repeatedly call other internal helpers. This makes the architecture harder to reason about and should be flattened where the extra layer does not add validation, naming, or reuse value.*

## Selecting refactor candidates

![Selecting refactor candidates](../assets/fabricops-select-refactor-candidates.png)

*Selecting a focused cleanup set.*

The dashboard supports selecting callables with refactor signals so users can build a focused cleanup set. This narrows review to specific architecture guardrails instead of asking AI tools to reason over the whole codebase at once.

## Exporting an AI refactor prompt

![Exporting an AI refactor prompt](../assets/fabricops-select-refactor-candidates-prompt-export.png)

*Exporting a structured AI refactor packet.*

Selected callables can be exported as a structured AI refactor packet. The export gives AI tools the callable layer, call graph context, recommended action, compatibility mode, safety constraints, and expected output so they can reason from architecture context instead of guessing from isolated code snippets.

??? example "Example exported AI refactor packet"

    ```text
    FabricOps callable refactor packet

    Prompt for AI

    You are reviewing a FabricOps callable refactor packet. Use the selected callables and call graph metadata to plan a safe cleanup. Group callables by refactor type, explain the rationale, identify risks, and propose an ordered implementation plan. Do not write code yet. Respect the compatibility mode in this packet. If compatibility_mode is stable_api_safe, preserve public API compatibility and call out migration risks. If compatibility_mode is internal_cleanup, preserve external behavior but allow internal signatures and helper boundaries to change when justified. If compatibility_mode is development_breaking_allowed, propose cleaner breaking changes where they improve the design. Batch accounting: report how many callables were selected, how many are intended for the current batch, how many were actually refactored in the PR, which selected callables were deferred, why each deferred group was deferred, and what the next suggested batch should be. Do not imply that all selected callables were refactored unless they were actually changed. If this PR handles only a subset, clearly label it as a batch and list the remaining selected callables as deferred. Completion accounting required in PR description: include selected / handled / remaining counts in the PR body and fill completed_or_refactored_count after implementation if it was unknown at export time. Always call out tests required before changes.

    Refactor context

    Intent: Plan safe cleanup for selected FabricOps helper callables.

    Mode: Planning only.

    Compatibility mode: Internal cleanup

    Batch accounting

    Selected callables: 1
    Planned batch count: 1
    Batch ID: batch-1
    Batch scope: All selected callables by default; narrow this before implementation when a smaller safe batch is intended.
    Batch strategy: Single batch by default. If implementation handles only a subset, group deferred selected callables by risk, ownership, or dependency order.
    Completed/refactored count: fill in after implementation
    Remaining selected count: fill in after implementation
    Deferred selected callables: none by default before implementation; list any selected callables not handled in this PR.

    Completion accounting required in PR description

    Include selected / handled / remaining counts in the PR body. Do not imply that all selected callables were refactored unless they were actually changed. If this PR handles only a subset, clearly label it as a batch and list the remaining selected callables as deferred. Explain why each deferred group was deferred and recommend the next batch.

    Selected callable actions:
    - Architecture violation

    Safety constraints:
    - Preserve external behavior
    - Internal helper names, signatures, and module boundaries may change if justified
    - Identify impacted callers before recommending changes

    Expected AI output:
    - Group selected callables by refactor type
    - Explain which callables are safe cleanup candidates
    - Identify callables that should not be refactored yet
    - Propose an ordered refactor plan
    - Report selected, intended batch, actually refactored, deferred, and remaining callable counts
    - List risks and required tests
    - Do not produce code changes unless explicitly requested

    Selected callables

    Callable 1: _audit_timestamp_expr

    Qualified name: fabricops_kit.config._audit_timestamp_expr
    Module: config
    Layer: Internal helper
    Recommended action: Architecture violation
    Priority: High
    Signal reason: Architecture violation: Callable dependency direction breaks the public → internal → utility layer rule.
    Callers:
    - profile_dataframe (data_profiling)

    Callees:
    - _get_audit_timezone (config)

    Source path: src/fabricops_kit/config.py
    ```

## Conclusion

The Callable Flow Dashboard is not only a dependency viewer. It is an architecture guardrail for keeping FabricOps maintainable as the kit grows.

The main rule is simple: public callables should orchestrate, internal helpers should contain reusable workflow logic, and utility callables should stay small, stable, and dependency-light. When a callable breaks this direction, depends on too many nested helpers, or creates repeated helper chains, the dashboard should flag it for review before cleanup.

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


def _landing_count_text(count: int, singular: str, plural: str | None = None) -> str:
    """Return count text with simple singular/plural wording."""
    label = singular if count == 1 else (plural or f"{singular}s")
    return f"{count} {label}"


def generate_landing_stats(
    *,
    public_exports: list[str],
    function_manifest: list[dict[str, Any]],
    metadata_table_count: int,
) -> dict[str, int]:
    """Write landing-page count data derived from canonical generated sources."""
    public_names = set(public_exports)
    public_function_count = len(public_names)
    supporting_internal_function_count = sum(
        1
        for entry in function_manifest
        if entry.get("qualified_name") and entry.get("name") not in public_names
    )
    stats = {
        "public_function_count": public_function_count,
        "supporting_internal_function_count": supporting_internal_function_count,
        "metadata_table_count": metadata_table_count,
    }
    LANDING_STATS_PATH.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    return stats


def update_landing_page_counts(stats: dict[str, int]) -> None:
    """Replace stable landing-page count tokens with generated count text."""
    text = LANDING_PAGE_PATH.read_text(encoding="utf-8")
    replacements = {
        "FABRICOPS_PUBLIC_FUNCTION_COUNT": _landing_count_text(
            stats["public_function_count"], "public Starter Kit function"
        ),
        "FABRICOPS_INTERNAL_FUNCTION_COUNT": _landing_count_text(
            stats["supporting_internal_function_count"], "supporting internal function"
        ),
        "FABRICOPS_METADATA_TABLE_COUNT": _landing_count_text(stats["metadata_table_count"], "metadata table"),
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
    module_data = {p.stem: parse_module(p) for p in PKG_DIR.glob("*.py") if p.name != "__init__.py"}

    source_modules = {p.stem for p in PKG_DIR.glob("*.py") if p.name != "__init__.py"}
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

    supporting_internal_count = len([
        node for node in node_by_qn.values()
        if not node.get("exported") and node["callable_name"] in module_data[node["module_name"]]["functions"]
    ])

    public_function_count = len(function_symbol_map)
    ref = [
        "# Function Reference",
        "",
        "Use this page to look up Starter Kit functions used by the template notebooks.",
        "",
        '<div class="reference-kpi-grid" aria-label="Function reference summary">',
        '  <section class="reference-kpi-card">',
        f'    <p class="reference-kpi-value">{public_function_count}</p>',
        '    <h2 class="reference-kpi-title">Public functions</h2>',
        '    <p class="reference-kpi-note">Notebook-facing entry points used by starter templates.</p>',
        '  </section>',
        '  <section class="reference-kpi-card">',
        f'    <p class="reference-kpi-value">{supporting_internal_count}</p>',
        '    <h2 class="reference-kpi-title">Supporting internal functions</h2>',
        '    <p class="reference-kpi-note">Maintainer helpers tracked for source navigation.</p>',
        '  </section>',
        '</div>',
        "",
    ]

    ref.extend(
        [
            "## Find a function",
            "",
            f"Use the finder below to look up the {public_function_count} public Starter Kit functions. Supporting internal functions stay out of the standalone public catalogue. “Used in” means direct starter notebook code-cell invocation, not import-only, markdown-only, generated metadata, example usage, or internal helper usage.",
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
        dependency_meta = dependency_callables.get(qn, {})
        calls = [item for item in dependency_meta.get("calls", []) if not _hide_from_public_relationships(item)]
        called_public = [item for item in calls if node_by_qn.get(item, {}).get("exported")]
        nested_internal_helpers = _callable_flow_internal_helper_qns(qn, calls_by_qn, node_by_qn)

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
                '  <div class="reference-catalogue-item-counts">',
                _catalogue_count_details("Calls {count} public function", "Calls {count} public functions", called_public),
                _catalogue_count_details("Calls {count} nested helper function", "Calls {count} nested helper functions", nested_internal_helpers),
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
            helper_qns = [
                helper_qn
                for helper_qn in _collect_internal_helper_descendants(qn, calls_by_qn, node_by_qn)
                if helper_qn not in INTERNAL_HELPER_EXCLUSIONS.get(short_name, set())
            ]
            refactor_signals = _collect_refactor_signals(
                qn,
                calls_by_qn,
                node_by_qn,
                module_data,
                excluded_helpers=INTERNAL_HELPER_EXCLUSIONS.get(short_name, set()),
            )
            refactor_signals_manifest[short_name] = refactor_signals
            used_in_templates = template_usage_by_symbol.get(short_name, [])
            helper_count = len(helper_qns)
            helper_word = "function" if helper_count == 1 else "functions"
            call_flow_lines = (
                [
                    f'??? info "Uses {helper_count} internal helper {helper_word}"',
                    "",
                    *_indent_markdown(_render_clickable_call_tree(qn, calls_by_qn, node_by_qn, module_data)),
                ]
                if helper_count
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
    )
    update_landing_page_counts(landing_stats)
    REFACTOR_SIGNALS_PATH.write_text(
        json.dumps(refactor_signals_manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    public_flow_qns = sorted(
        [qn for qn, node in node_by_qn.items() if node.get("exported")],
        key=lambda qn: node_by_qn[qn]["callable_name"].lower(),
    )
    callable_flow_data = _build_callable_flow_data(public_flow_qns, calls_by_qn, node_by_qn, module_data)
    CALLABLE_FLOW_DATA_PATH.write_text(json.dumps(callable_flow_data, indent=2) + "\n", encoding="utf-8")
    CALLABLE_FLOW_PAGE_PATH.write_text(_render_callable_flow_page(callable_flow_data), encoding="utf-8", newline="\n")
    REFACTOR_DASHBOARD_PATH.write_text(_render_refactor_dashboard_html(callable_flow_data), encoding="utf-8", newline="\n")
    _remove_stale_function_taxonomy_audit()



if __name__ == "__main__":
    main()
