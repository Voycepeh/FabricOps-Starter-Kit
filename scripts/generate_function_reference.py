"""Generate function reference helpers."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from datetime import UTC, datetime
from zoneinfo import ZoneInfo
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
FUNCTION_CALL_GRAPH_PAGE_PATH = ROOT / "docs" / "reference" / "function-call-graph.md"
FUNCTION_CALL_GRAPH_DATA_PATH = REFERENCE_DATA_DIR / "function-call-graph.json"
FUNCTION_CALL_GRAPH_DASHBOARD_PATH = ROOT / "docs" / "assets" / "function-call-graph-dashboard.html"
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
    "config.shared": "config",
    "config.get_fabric_context": "config",
    "config.setup_notebook": "config",
    "config.setup_metadata_tables": "config",
    "widgets.widget_select_guardrail_target": "widgets.widget_select_guardrail_target",
    "widgets.widget_author_schema_freshness_profile_rules": "widgets.widget_author_schema_freshness_profile_rules",
    "widgets.widget_author_dq_rules": "widgets.widget_author_dq_rules",
    "widgets.widget_enrich_table_metadata": "widgets.widget_enrich_table_metadata",
    "widgets.widget_review_guardrail_governance": "widgets.widget_review_guardrail_governance",
    "pipeline.profile_dataframe": "pipeline",
    "io": "io",
    "guardrails": "guardrails",
    "metadata": "metadata",
    "pipeline": "pipeline",
}
MAJOR_IMPLEMENTATION_MODULE_ORDER = [
    "config",
    "io",
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

# Implementation helper chips should mirror the generated package-local call tree.
# Exclude reachable private helpers only when a callable has an explicit deny
# rule here; this keeps ordinary private implementation helpers visible while
# suppressing intentionally noisy shared plumbing.
INTERNAL_HELPER_EXCLUSIONS: dict[str, set[str]] = {
    "enforce_profile_behavior": {
        "fabricops_kit.io.shared._normalize_schema_name",
        "fabricops_kit.config.shared.get_store",
    },
    "run_table_guardrails": {
        "fabricops_kit.config.shared.get_current_audit_timestamp",
        "fabricops_kit.config.shared.get_audit_timezone",
        "fabricops_kit.config.shared._validate_audit_timezone",
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
    "fabricops_kit.config.shared.get_store": "keep_internal",
    "fabricops_kit.config.shared._normalize_path_config": "keep_internal",
    "fabricops_kit.io.shared._normalize_table_name": "keep_internal",
    "fabricops_kit.io.shared._normalize_schema_name": "keep_internal",
    "fabricops_kit.io.shared._resolve_lakehouse_schema": "keep_internal",
    "fabricops_kit.io.shared._resolve_lakehouse_table_path": "keep_internal",
    "fabricops_kit.io.shared.get_spark_session": "keep_internal",
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
    parts = path.relative_to(PKG_DIR).with_suffix("").parts
    if parts[-1] == "__init__":
        return ".".join(parts[:-1])
    return ".".join(parts)


def source_module_paths() -> list[Path]:
    """Return package source files that participate in generated callable metadata."""
    return sorted(path for path in PKG_DIR.rglob("*.py") if path.name != "__init__.py" or path.parent.name in {"pipeline"})


def source_module_path(module: str) -> Path:
    """Return the source path for a dotted package-relative module name."""
    if module == "io":
        return PKG_DIR / "io" / "shared.py"
    if module == "pipeline":
        return PKG_DIR / "pipeline" / "__init__.py"
    if module == "config":
        return PKG_DIR / "config" / "__init__.py"
    return PKG_DIR.joinpath(*module.split(".")).with_suffix(".py")

def parse_module(path: Path) -> dict[str, Any]:
    """Parse module."""
    source_text = path.read_text(encoding="utf-8")
    source_path = path.relative_to(ROOT).as_posix()
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
        "source_path": source_path,
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
            module = node.module or ""
            prefix = "." * node.level
            for alias in node.names:
                if alias.name == "*":
                    continue
                name = alias.asname or alias.name
                if module:
                    symbol_aliases[name] = f"{prefix}{module}.{alias.name}"
                else:
                    module_aliases[name] = f"{prefix}{alias.name}"
    return module_aliases, symbol_aliases


def _callable_expr_name(node: ast.AST) -> str:
    """Return a static callable expression name when it is obvious."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return f"{node.value.id}.{node.attr}"
    return ""


def _collect_dispatch_map_calls(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, set[str]]:
    """Return simple local dispatch-map names keyed to callable object values."""
    dispatch_maps: dict[str, set[str]] = {}
    for child in ast.walk(node):
        if not isinstance(child, (ast.Assign, ast.AnnAssign)) or not isinstance(child.value, ast.Dict):
            continue
        targets = child.targets if isinstance(child, ast.Assign) else [child.target]
        names = [target.id for target in targets if isinstance(target, ast.Name)]
        if not names:
            continue
        values = {_callable_expr_name(value) for value in child.value.values}
        values.discard("")
        if values:
            for name in names:
                dispatch_maps.setdefault(name, set()).update(values)
    return dispatch_maps


def collect_function_calls(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[dict[str, str]]:
    """Collect function and callable object calls."""
    calls: list[dict[str, str]] = []
    dispatch_maps = _collect_dispatch_map_calls(node)
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
        elif isinstance(child.func, ast.Subscript) and isinstance(child.func.value, ast.Name):
            for target in sorted(dispatch_maps.get(child.func.value.id, set())):
                calls.append({"raw_name": target, "call_type": "dispatch_map"})
        if call_target:
            calls.append({"raw_name": call_target, "call_type": call_type})
    return calls


def _resolve_relative_import_name(module: str, imported: str) -> str:
    """Resolve a possibly relative import target against a module name."""
    if not imported.startswith("."):
        return imported
    level = len(imported) - len(imported.lstrip("."))
    relative_name = imported[level:]
    module_parts = module.split(".")
    base_parts = module_parts[: max(len(module_parts) - level, 0)]
    return ".".join([*base_parts, relative_name]) if base_parts else relative_name


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
            return "public_callable" if mapped.role == "callable" else "public_class"
        if symbol_name.startswith("_"):
            return "private_helper"
        return "shared_helper"
    # same-module callable/class names are always safe to resolve first
    if raw_name in same_module_names:
        return f"{PACKAGE_NAME}.{module}.{raw_name}", "same_module", _classify_callee(module, raw_name)

    # explicit import alias from "from x import y as z"
    if raw_name in symbol_aliases:
        imported = _resolve_relative_import_name(module, symbol_aliases[raw_name])
        imported_short = imported.split(".")
        if len(imported_short) >= 2:
            resolved_symbol = imported_short[-1]
            module_candidate = ".".join(imported_short[:-1])
            resolved_module = module_candidate.removeprefix(f"{PACKAGE_NAME}.")
            if imported.startswith(PACKAGE_NAME) or resolved_module in package_module_names:
                exported = exported_symbol_map.get(resolved_symbol)
                target_module = (exported.public_module if exported and exported.actual_module == resolved_module and exported.public_module in {"data_profiling", "pipeline"} else resolved_module)
                callee_kind = _classify_callee(resolved_module, resolved_symbol)
                return (
                    f"{PACKAGE_NAME}.{target_module}.{resolved_symbol}",
                    "cross_module" if resolved_module != module else "same_module",
                    callee_kind,
                )

    # module/alias call like alias.func() or module.func()
    if "." in raw_name:
        owner, member = raw_name.split(".", 1)
        mapped_owner = _resolve_relative_import_name(module, module_aliases.get(owner, owner))
        short_owner = mapped_owner.split(".")[-1]
        resolved_owner = mapped_owner.removeprefix(f"{PACKAGE_NAME}.")
        if mapped_owner.startswith(PACKAGE_NAME) or resolved_owner in package_module_names or short_owner in package_module_names:
            resolved_module = resolved_owner if resolved_owner in package_module_names else short_owner
            exported = exported_symbol_map.get(member)
            target_module = (exported.public_module if exported and exported.actual_module == resolved_module and exported.public_module in {"data_profiling", "pipeline"} else resolved_module)
            callee_kind = _classify_callee(resolved_module, member)
            return f"{PACKAGE_NAME}.{target_module}.{member}", "cross_module" if resolved_module != module else "same_module", callee_kind
        return None, "unresolved", "unresolved"

    # public exported symbol map fallback (bare-name cross-module only for exported mapping)
    exported = exported_symbol_map.get(raw_name)
    if exported and exported.actual_module != module:
        callee_kind = _classify_callee(exported.actual_module, raw_name)
        target_module = exported.public_module if exported.public_module in {"data_profiling", "pipeline"} else exported.actual_module
        return f"{PACKAGE_NAME}.{target_module}.{raw_name}", "cross_module", callee_kind

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

    def canonical_qualified_name(module: str, callable_name: str) -> str:
        exported = symbol_map.get(callable_name)
        if exported and exported.actual_module == module:
            target_module = exported.public_module if exported.public_module in {"data_profiling", "pipeline"} else exported.actual_module
            return f"{PACKAGE_NAME}.{target_module}.{callable_name}"
        return f"{PACKAGE_NAME}.{module}.{callable_name}"

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
            qualified_name = canonical_qualified_name(module, callable_name)
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
            caller_qn = canonical_qualified_name(module, caller_name)
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
                    callee_module = resolved_qn.removeprefix(f"{PACKAGE_NAME}.").rsplit(".", 1)[0] if resolved_qn.startswith(f"{PACKAGE_NAME}.") else resolved_qn.split(".")[-2]
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
        return f"#{symbol_name}"
    if context == "notebook":
        return f"#{symbol_name}"
    raise RuntimeError(f"Unknown link context: {context}")


def resolve_preferred_actual_module(preferred_module: str) -> str:
    """Return the likely source module that owns callable implementations."""
    if PUBLIC_MODULE_PREFERRED_NAMES.get(preferred_module) == preferred_module:
        return preferred_module
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
            f"src/fabricops_kit/{module_name.replace('.', '/')}.py",
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
    """Render the same function call graph tree structure used by the dashboard inventory JSON."""
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


def _callable_flow_source_metadata(qn: str, module_data: dict[str, dict[str, Any]]) -> tuple[str | None, str | None, dict[str, int]]:
    """Return module key, callable name, and source location for a function call graph node."""
    parts = qn.split(".")
    package_parts = parts[1:] if parts and parts[0] == PACKAGE_NAME else parts
    for split_at in range(len(package_parts) - 1, 0, -1):
        module_key = ".".join(package_parts[:split_at])
        callable_name = ".".join(package_parts[split_at:])
        source_location = module_data.get(module_key, {}).get("source_locations", {}).get(callable_name)
        if source_location:
            return module_key, callable_name, source_location
    return None, None, {}


def _callable_flow_source_location(qn: str, module_data: dict[str, dict[str, Any]]) -> dict[str, int | None]:
    """Return source line metadata for a function call graph node when available."""
    _, _, source_location = _callable_flow_source_metadata(qn, module_data)
    return {
        "source_start_line": source_location.get("start_line"),
        "source_end_line": source_location.get("end_line"),
    }


def _callable_flow_source_path(qn: str, module_data: dict[str, dict[str, Any]] | None = None) -> str | None:
    """Return the repository source path for a package callable."""
    module_key = None
    if module_data is not None:
        module_key, _, _ = _callable_flow_source_metadata(qn, module_data)
    if module_key is None:
        parts = qn.split(".")
        package_parts = parts[1:] if parts and parts[0] == PACKAGE_NAME else parts
        if len(package_parts) < 2:
            return None
        module_key = ".".join(package_parts[:-1])
    module_info = module_data.get(module_key, {}) if module_data is not None else {}
    source_path = module_info.get("source_path")
    if source_path:
        return source_path
    return f"src/fabricops_kit/{module_key.replace('.', '/')}.py"


def _callable_flow_source_link(qn: str, module_data: dict[str, dict[str, Any]]) -> str | None:
    """Return a source URL for a function call graph node when source metadata exists."""
    _, _, source_location = _callable_flow_source_metadata(qn, module_data)
    if not source_location:
        return None
    source_path = _callable_flow_source_path(qn, module_data)
    if not source_path:
        return None
    return github_source_url(
        source_path,
        source_location.get("start_line"),
        source_location.get("end_line"),
    )


REFACTOR_SIGNAL_ORDER = [
    "Maybe combine",
    "Used several times in one function",
    "Recursive helper",
    "Used by one function",
    "Leaf internal helper",
    "Heavily used helper",
]

REFACTOR_SIGNAL_RECOMMENDATIONS = {
    "Maybe combine": "Maybe combine",
    "Used several times in one function": "Used several times in one function",
    "Recursive helper": "Recursive helper",
    "Used by one function": "Used by one function",
    "Leaf internal helper": "Shared utility",
    "Heavily used helper": "Heavily used helper",
}

REFACTOR_REASON_LABELS = {
    "Maybe combine": "Maybe combine",
    "Used several times in one function": "Used several times in one function",
    "Recursive helper": "Recursive helper",
    "Used by one function": "Used by one function",
    "Leaf internal helper": "End-of-chain helper",
    "Heavily used helper": "Heavily used helper",
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
    "High": "Maybe combine",
    "Medium": "Used by one function",
    "Low": "Shared utility",
    "Review": "Next step",
}

ACTION_LEGEND = {
    "Public API entrypoint": "Supported user-facing API surface; no inbound project calls are required.",
    "Shared internal helper": "Internal implementation helper used by multiple public or internal callers; protect with focused tests before changing.",
    "Shared utility": "Low-level leaf helper with multiple inbound callers; keep generic and project-callable free.",
    "Maybe combine": "This helper is used by one function, and that function uses it once. Review whether keeping it separate makes the code easier to read.",
    "Used by one function": "Helper has one distinct caller. This is a review hint, not an automatic judgment.",
    "Used several times in one function": "This helper is used by one function, but that function uses it more than once. This is usually a reason to keep it, or at least review carefully.",
    "Recursive helper": "Helper calls itself; do not treat it as a simple merge or inline case.",
    "Heavily used helper": "Helper is used by many functions; protect with focused tests before changing.",
    "Next step": "Use the detail text to decide the next architecture action before changing structure.",
    "Broken rule": "Callable dependency direction breaks the public → internal → utility layer rule.",
    "Orphaned callable": "Private callable with no reachable public lineage; remove or reconnect if still needed.",
}


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
    if "Heavily used helper" in signals:
        return "Protect"
    if "Maybe combine" in signals:
        return "High"
    if "Used several times in one function" in signals or "Recursive helper" in signals or "Used by one function" in signals:
        return "Review"
    if "Leaf internal helper" in signals:
        return "Low"
    return "Low"


def _build_refactor_inventory(
    public_qns: list[str],
    public_class_qns: list[str] | None,
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
        call_site_count = sum(1 for caller in inbound for callee in calls_by_qn.get(caller, []) if callee == qn)
        recursive = qn in calls_by_qn.get(qn, [])
        repeated_within_single_caller = (
            inbound_count == 1 and sum(1 for callee in calls_by_qn.get(inbound[0], []) if callee == qn) > 1
        )
        signals: list[str] = []
        if inbound_count == 1 and call_site_count == 1 and not recursive:
            signals.append("Maybe combine")
        if repeated_within_single_caller:
            signals.append("Used several times in one function")
        if recursive:
            signals.append("Recursive helper")
        if inbound_count == 1:
            signals.append("Used by one function")
        if outbound_count == 0:
            signals.append("Leaf internal helper")
        if inbound_count >= 5:
            signals.append("Heavily used helper")
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
                "next_step": REFACTOR_PRIORITY_ACTIONS[priority],
                "recommended_action": REFACTOR_PRIORITY_ACTIONS[priority],
                "inbound_count": inbound_count,
                "call_site_count": call_site_count,
                "recursive": recursive,
                "repeated_within_single_caller": repeated_within_single_caller,
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
                "source_path": _callable_flow_source_path(qn, module_data),
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
            "call_site_count": row["call_site_count"],
            "recursive": row["recursive"],
            "repeated_within_single_caller": row["repeated_within_single_caller"],
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
        "review_for_merge_helpers": sum(1 for row in inventory if "Maybe combine" in row["signals"]),
        "used_by_one_function_helpers": sum(1 for row in inventory if "Used by one function" in row["signals"]),
        "repeated_within_single_caller_helpers": sum(
            1 for row in inventory if "Used several times in one function" in row["signals"]
        ),
        "recursive_helpers": sum(1 for row in inventory if "Recursive helper" in row["signals"]),
        "leaf_internal_helpers": sum(1 for row in inventory if "Leaf internal helper" in row["signals"]),
        "heavily_used_helpers": sum(1 for row in inventory if "Heavily used helper" in row["signals"]),
        "public_api_entrypoints": len(public_qns),
        "internal_helpers": len(inventory),
        "high_priority_candidates": sum(1 for row in inventory if row["priority"] == "High"),
        "medium_priority_candidates": sum(1 for row in inventory if row["priority"] == "Medium"),
        "protect_helpers": sum(1 for row in inventory if row["priority"] == "Protect"),
    }
    return summary_counts, inventory, legacy_signal_rows


CALLABLE_LAYER_LABELS = {
    "public": "Public function",
    "internal": "Shared helper",
}

HIDDEN_PRIVATE_LAYER = "private_helper"
PRIVATE_HELPER_LABEL = "Private helper"
SUPPORTING_OBJECT_LAYER = "supporting_object"
PUBLIC_CLASS_LAYER = "class"
PUBLIC_CLASS_LABEL = "Public config class"

REVIEW_STATUS_LABELS = {
    "classified": "Classified",
    "classification_pending": "Classification pending",
    "implicit_lifecycle": "Implicit lifecycle method",
    "property_accessor": "Property accessor",
    "unreachable": "Cannot trace back to a public function",
}

LAYER_CONSISTENCY_LABELS = {
    "implicit_lifecycle": "Implicit lifecycle method",
    "property_accessor": "Property accessor",
    "matches_layer": "Matches expected layer",
    "questionable_utility": "Questionable utility",
    "promote_to_utility_candidate": "Promote to utility candidate",
    "shared_internal_helper": "Shared internal helper",
    "possible_inline_or_private_helper": "Possible inline/private helper",
    "architecture_violation": "Broken rule",
    "review_manually": "Next step",
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

    if architecture_layer == "Shared helper":
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
    "GovernanceConfig",
    "DataAgreementConfig",
    "FrameworkConfig",
    "PathConfig",
}

RESULT_MODEL_CLASSES = {"ConfigSmokeCheckResult"}
CONTEXT_MODEL_CLASSES = {"NotebookSetupContext"}

ROLE_TAGS_BY_NAME = {
    "setup_notebook": ["public_api_entrypoint", "notebook_api_entrypoint", "public_stable"],
    "setup_metadata_tables": ["public_api_entrypoint", "metadata_setup_workflow", "public_stable"],
    "_setup_notebook_workflow": ["internal_workflow", "setup_notebook_workflow"],
    "_get_store": ["internal_resolver", "shared_internal_service", "store_resolver", "high_fanout_shared"],
    "resolve_fabric_context": [
        "internal_resolver",
        "shared_internal_service",
        "runtime_context_resolver",
        "high_fanout_shared",
    ],
    "get_default_fabric_context": ["internal_resolver", "runtime_context_provider", "shared_internal_service"],
    "get_current_audit_timestamp": ["audit_time_utility", "shared_internal_service", "high_fanout_shared"],
    "get_audit_timezone": ["internal_resolver", "audit_config_resolver"],
    "build_audit_timestamp_expr": ["audit_time_utility", "spark_audit_expression_utility"],
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
    "render_maintenance_widget_shared_workflow": ["internal_workflow", "shared_widget_rendering_workflow"],
    "write_widget_metadata_row": ["internal_adapter", "metadata_write_adapter"],
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
    "list_all_data_agreement_rows": ["internal_resolver", "agreement_resolver"],
    "list_data_agreements": ["internal_resolver", "agreement_resolver"],
    "_validate_dq_rules": ["internal_validator", "dq_rule_validator"],
    "_coerce_rows": ["internal_normalizer", "row_payload_normalizer"],
    "_coerce_row_dicts": ["internal_normalizer", "row_payload_normalizer"],
    "_dq_records_from_selection": ["internal_normalizer", "rule_payload_normalizer"],
    "_schema_freshness_profile_records_from_selection": ["internal_normalizer", "rule_payload_normalizer"],
    "_business_agreement_snapshot": ["internal_normalizer", "agreement_payload_normalizer"],
    "render_searchable_selector": ["internal_adapter", "widget_rendering_adapter"],
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
    "resolve_profiled_columns": ["internal_resolver", "profiling_column_resolver"],
    "is_min_max_supported_type": ["internal_resolver", "spark_type_resolver"],
    "_numeric_bin_edges": ["internal_adapter", "spark_profiling_adapter"],
    "_build_numeric_distribution": ["internal_adapter", "spark_profiling_adapter"],
    "_build_categorical_distribution": ["internal_adapter", "spark_profiling_adapter"],
    "build_distribution_summaries": ["internal_adapter", "spark_profiling_adapter"],

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

ARCHITECTURE_VIOLATION_ACTION = "Broken rule"


def _callable_classification(
    qn: str,
    public_qn_set: set[str],
    public_class_qn_set: set[str],
    reachable_non_public: set[str],
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
) -> tuple[str, str]:
    """Return architecture layer and review status for a project callable."""
    node = node_by_qn[qn]
    if node.get("callable_kind") != "function":
        if qn in public_class_qn_set:
            return PUBLIC_CLASS_LAYER, "classified"
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
    public_class_qns: list[str] | None,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
    callable_summary: list[dict[str, Any]],
    refactor_inventory: list[dict[str, Any]],
) -> tuple[dict[str, int], list[dict[str, Any]]]:
    """Build a reconciled one-row-per-discovered-callable dashboard inventory."""
    public_qn_set = set(public_qns)
    public_class_qn_set = set(public_class_qns or [])
    reachable_non_public = set().union(
        *(_reachable_callables(public_qn, calls_by_qn, node_by_qn) for public_qn in public_qns)
    ) - public_qn_set
    inbound_by_qn = _project_inbound_callers(calls_by_qn, node_by_qn)
    refactor_by_qn = {row["qualified_name"]: row for row in refactor_inventory}
    summary_by_qn = {row["qualified_name"]: row for row in callable_summary}
    classification_by_qn = {
        qn: _callable_classification(qn, public_qn_set, public_class_qn_set, reachable_non_public, calls_by_qn, node_by_qn)
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

    runtime_reachable_qns = public_qn_set | public_class_qn_set | reachable_non_public

    def is_inventory_function(qn: str) -> bool:
        layer = layer_by_qn.get(qn)
        return layer in {"public", "internal", HIDDEN_PRIVATE_LAYER, PUBLIC_CLASS_LAYER}

    def inventory_function_type(layer: str) -> str:
        if layer == HIDDEN_PRIVATE_LAYER:
            return PRIVATE_HELPER_LABEL
        if layer == PUBLIC_CLASS_LAYER:
            return PUBLIC_CLASS_LABEL
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
        if node_by_qn[qn]["module_name"] == "pipeline.shared":
            return "Keep private helper", "Low"
        if scope == "cross_module":
            return "Rename to shared helper", "Medium"
        if not inbound:
            return "Remove redundant wrapper", "Medium"
        if len(inbound) == 1 and len(set(outbound)) <= 1:
            return "Merge into owner", "Medium"
        if len(inbound) == 1 and node_by_qn[qn]["module_name"] not in {node_by_qn[caller]["module_name"] for caller in inbound}:
            return "Move closer to owner", "Medium"
        return "Keep private helper", "Low"

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
        runtime_reachability = (
            "reachable_from_public_runtime"
            if qn in runtime_reachable_qns or review_status == "implicit_lifecycle" or qn in lifecycle_called_qns
            else "unreachable_runtime_asset"
        )
        if architecture_signals:
            recommended_action = ARCHITECTURE_VIOLATION_ACTION
            priority = "High"
        elif runtime_reachability == "unreachable_runtime_asset":
            recommended_action = "Verify possible orphan"
            priority = "Medium"
        elif review_status == "classification_pending":
            recommended_action = "Next step"
            priority = "Low"
        elif review_status == "implicit_lifecycle":
            recommended_action = "Keep lifecycle method"
            priority = "Low"
        elif review_status == "property_accessor":
            recommended_action = "Keep property accessor"
            priority = "Low"
        elif layer == "public":
            recommended_action = "Public API entrypoint"
            priority = refactor.get("priority", "Low")
        elif layer == "internal":
            recommended_action = "Heavily used helper" if len(inbound) >= 5 else "Shared internal helper" if len(inbound) > 1 else refactor.get("recommended_action", "Next step")
            priority = refactor.get("priority", "Low")
        elif layer == HIDDEN_PRIVATE_LAYER:
            recommended_action, priority = private_helper_action(qn, inbound, outbound)
        elif layer == PUBLIC_CLASS_LAYER:
            recommended_action = "Public config class"
            priority = "Low"
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
                "review_status_label": (
                    "Cannot trace back to a public function"
                    if runtime_reachability == "unreachable_runtime_asset"
                    else REVIEW_STATUS_LABELS[review_status]
                ),
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
                "owner_file": _callable_flow_source_path(owner_qn, module_data) if owner_qn else _callable_flow_source_path(qn, module_data),
                "leaks_outside_owner_file": bool(layer == HIDDEN_PRIVATE_LAYER and usage_scope == "cross_module"),
                "usage_scope": usage_scope,
                "usage_scope_label": _label_from_value(usage_scope) if usage_scope else "",
                "reachability": runtime_reachability,
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
                "call_site_count": refactor.get("call_site_count", sum(1 for caller in inbound for callee in calls_by_qn.get(caller, []) if callee == qn)),
                "recursive": refactor.get("recursive", qn in calls_by_qn.get(qn, [])),
                "repeated_within_single_caller": refactor.get(
                    "repeated_within_single_caller",
                    used_by_count == 1 and bool(inbound) and sum(1 for callee in calls_by_qn.get(next(iter(inbound)), []) if callee == qn) > 1,
                ),
                "calls_count": calls_count,
                "layer_consistency": layer_consistency,
                "layer_consistency_label": LAYER_CONSISTENCY_LABELS[layer_consistency],
                "callers": linked(inbound),
                "callees": linked(set(outbound)),
                "direct_internal_helpers": linked(direct_helper_qns),
                "source_path": _callable_flow_source_path(qn, module_data),
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
    deduped_inventory: list[dict[str, Any]] = []
    seen_inventory_identities: set[tuple[str | None, str, int | None, int | None]] = set()
    for row in inventory:
        identity = (
            row.get("source_path"),
            row["qualified_name"],
            row.get("source_start_line"),
            row.get("source_end_line"),
        )
        if identity in seen_inventory_identities:
            continue
        seen_inventory_identities.add(identity)
        deduped_inventory.append(row)
    inventory = deduped_inventory

    summary_counts = {
        "total_callables": len(inventory),
        "total_functions": sum(1 for row in inventory if row["layer"] in CALLABLE_LAYER_LABELS),
        "private_helper_review": sum(1 for row in inventory if row["layer"] == HIDDEN_PRIVATE_LAYER),
        "function_type": {
            label: sum(1 for row in inventory if row["function_type"] == label)
            for label in [*CALLABLE_LAYER_LABELS.values(), PUBLIC_CLASS_LABEL]
        },
        "layer": {
            layer: sum(1 for row in inventory if row["layer"] == layer)
            for layer in CALLABLE_LAYER_LABELS
        },
        "hidden_private_helpers": sum(1 for row in inventory if row["layer"] == HIDDEN_PRIVATE_LAYER),
        "public_classes": sum(1 for row in inventory if row["layer"] == PUBLIC_CLASS_LAYER),
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
    """Return canonical function inventory summary metrics for generated pages."""
    public_api_counts = summary_counts.get("public_api_surface", {})
    total_callables = int(summary_counts.get("total_callables", len(inventory)))
    visible_function_callables = sum(1 for row in inventory if row.get("layer") in CALLABLE_LAYER_LABELS)
    private_helper_review = sum(1 for row in inventory if row.get("layer") == HIDDEN_PRIVATE_LAYER)
    public_class_count = sum(1 for row in inventory if row.get("layer") == PUBLIC_CLASS_LAYER)
    public_api_entrypoints = int(public_api_counts.get("public_api_entrypoints", 0))
    stable_identities = [
        (
            row.get("source_path"),
            row.get("qualified_name"),
            row.get("source_start_line"),
            row.get("source_end_line"),
        )
        for row in inventory
    ]
    unique_inventory_identity_count = len(set(stable_identities))
    return {
        "module_count": len({row.get("source_path") for row in inventory if str(row.get("source_path") or "").endswith(".py")}),
        "total_callables": total_callables,
        "inventory_row_count": len(inventory),
        "unique_inventory_identity_count": unique_inventory_identity_count,
        "duplicate_inventory_identity_count": len(inventory) - unique_inventory_identity_count,
        "public_api_entrypoints": public_api_entrypoints,
        "function_callables": visible_function_callables,
        "supporting_functions": max(visible_function_callables - public_api_entrypoints, 0),
        "public_classes": public_class_count,
        "hidden_private_helpers": private_helper_review,
        "private_helpers_to_review": private_helper_review,
    }


def _callable_inventory_metrics(callable_flow_data: dict[str, Any]) -> dict[str, int]:
    """Read canonical function inventory summary metrics from function graph data."""
    summary_counts = callable_flow_data.get("summary_counts", {})
    metrics = summary_counts.get("callable_inventory_metrics")
    if isinstance(metrics, dict):
        return {
            "module_count": int(metrics.get("module_count", 0)),
            "total_callables": int(metrics.get("total_callables", 0)),
            "public_api_entrypoints": int(metrics.get("public_api_entrypoints", 0)),
            "function_callables": int(metrics.get("function_callables", 0)),
            "supporting_functions": int(metrics.get("supporting_functions", 0)),
            "public_classes": int(metrics.get("public_classes", 0)),
            "hidden_private_helpers": int(metrics.get("hidden_private_helpers", 0)),
        }
    return _build_callable_inventory_metrics(summary_counts, callable_flow_data.get("function_inventory", []))


LONG_CALL_CHAIN_DEPTH_THRESHOLD = 4
LARGE_DEPENDENCY_SURFACE_THRESHOLD = 10

DECISION_RECOMMENDATIONS = {
    "keep_public": "",
    "flatten": "Simplify internals",
    "architecture_violation": "Fix architecture issue",
    "merge": "Inspect helpers marked Maybe combine",
    "move_closer": "Review nested helpers",
}

ARCHITECTURE_WARNING_TYPES = (
    "Same-file private dependency",
)

ARCHITECTURE_VIOLATION_TYPES = (
    "Public function calls public function",
    "Shared helper calls public function",
    "Cross-file private dependency",
)

DISPLAY_LABEL_MAP = {
    "Architecture violation": "Broken rule",
    "Architecture violation type": "Broken rule",
    "Long chain": "Too many steps",
    "Many dependencies": "Too many helpers",
    "Shared dependency": "Shared helper",
    "Review for merge": "Maybe combine",
    "Cross-layer dependency": "Broken rule",
    "Cross-layer issue": "Broken rule",
    "Deep chain": "Too many steps",
    "Single-use helper candidate": "Maybe combine",
    "Broken rule": "Broken rule",
    "Broken rule type": "Broken rule",
    "Cross-layer call": "Broken rule",
    "Too many steps": "Too many steps",
    "Too many helpers": "Too many helpers",
    "Maybe combine": "Maybe combine",
    "Used by one function": "Used by one function",
    "Used several times in one function": "Used several times in one function",
    "Recursive helper": "Recursive helper",
    "Heavily used helper": "Heavily used helper",
    "cross_layer_dependency": "Broken rule",
    "deep_chain": "Too many steps",
    "large_downstream_surface": "Too many helpers",
    "single_use_helper_candidate": "Maybe combine",
    "inline_candidate": "Maybe combine",
    "review_abstraction_value": "Used by one function",
}


def _display_label(value: str) -> str:
    """Return the current user-facing label for a legacy finding label."""
    return DISPLAY_LABEL_MAP.get(value, value)


def _decision_layer_group(row: dict[str, Any]) -> str:
    """Return the human-facing layer group from available inventory fields."""
    function_type = row.get("function_type") or row.get("layer")
    if function_type in {"Public function", "Shared helper"}:
        return function_type
    if function_type == PRIVATE_HELPER_LABEL:
        return PRIVATE_HELPER_LABEL
    if function_type == "Supporting object":
        return "Supporting object"
    if function_type == "Public API":
        return "Public function"
    if function_type in {"Shared helper", "Utility"}:
        return "Shared helper"
    layer = row.get("layer")
    if layer in CALLABLE_LAYER_LABELS:
        return CALLABLE_LAYER_LABELS[layer]
    if row.get("callable_kind") != "function" or row.get("layer") == HIDDEN_PRIVATE_LAYER:
        return "Supporting object"
    if row.get("dependency_role") == "public_api":
        return "Public function"
    return "Shared helper"




def _architecture_layer(row: dict[str, Any]) -> str:
    """Return the callable architecture label for a flow row."""
    if row.get("layer") == HIDDEN_PRIVATE_LAYER or row.get("function_type") == PRIVATE_HELPER_LABEL:
        return PRIVATE_HELPER_LABEL
    if row.get("callable_kind") != "function":
        return "Supporting object"
    group = _decision_layer_group(row)
    if group == "Public function":
        return "Public"
    return "Shared helper"


INTERNAL_LAYERING_VIOLATION = "Internal layering violation"
INTERNAL_LAYERING_SUGGESTED_FIX = (
    "Review helpers before changing them. Keep helpers that improve readability, are reused several times inside one "
    "function, call themselves recursively, or are shared across multiple callables."
)

SIMPLE_PUBLIC_CALLABLE = "Public function"
SIMPLE_SHARED_INTERNAL_HELPER = "Shared helper"
SIMPLE_PRIVATE_HELPER = "Private helper"
SIMPLE_REVIEW = "Unknown"


def _simple_flow_classification(row: dict[str, Any], public_user_count: int = 0) -> str:
    """Return the lightweight callable-flow classification shown in generated docs."""
    if _decision_layer_group(row) == "Public function":
        return SIMPLE_PUBLIC_CALLABLE
    if row.get("layer") == HIDDEN_PRIVATE_LAYER or row.get("function_type") == PRIVATE_HELPER_LABEL:
        return SIMPLE_PRIVATE_HELPER
    if _architecture_layer(row) == "Shared helper" and public_user_count > 1:
        return SIMPLE_SHARED_INTERNAL_HELPER
    return SIMPLE_REVIEW


def _classify_architecture_edge(caller_type: str, callee_type: str) -> dict[str, str]:
    """Classify a caller/callee layer pair as allowed unless 2-layer rules override it."""
    if "Supporting object" in {caller_type, callee_type}:
        return {"result": "Allowed", "violation_type": ""}
    return {"result": "Allowed", "violation_type": ""}


def _is_same_owner_private_helper(row: dict[str, Any], public_qn: str) -> bool:
    """Return whether a row is a private helper owned by the selected public callable."""
    return row.get("layer") == HIDDEN_PRIVATE_LAYER and row.get("owner_qualified_name") == public_qn


def _source_file_key(row: dict[str, Any]) -> str:
    """Return the best available file/module identity for callable boundary checks."""
    return str(row.get("source_path") or row.get("owner_file") or row.get("module") or "")


def _same_source_file(left: dict[str, Any], right: dict[str, Any]) -> bool:
    """Return whether two callable rows resolve to the same source file/module."""
    left_key = _source_file_key(left)
    right_key = _source_file_key(right)
    return bool(left_key and right_key and left_key == right_key)


def _classify_two_layer_edge(
    *,
    public_qn: str,
    parent_row: dict[str, Any],
    callee_row: dict[str, Any],
    caller_type: str,
    callee_type: str,
    public_user_count: int,
) -> dict[str, str]:
    """Classify whether an edge preserves the two-layer FabricOps callable architecture."""
    base = _classify_architecture_edge(caller_type, callee_type)

    parent_is_public_root = parent_row.get("qualified_name") == public_qn
    parent_is_local_private = _is_same_owner_private_helper(parent_row, public_qn)
    callee_is_local_private = _is_same_owner_private_helper(callee_row, public_qn)
    callee_is_private = callee_row.get("layer") == HIDDEN_PRIVATE_LAYER

    if callee_type == "Public":
        if caller_type == "Public":
            return {"result": "Violation", "violation_type": "Public function calls public function"}
        return {"result": "Violation", "violation_type": "Shared helper calls public function"}

    if callee_is_private:
        if _same_source_file(parent_row, callee_row):
            return {"result": "Warning", "violation_type": "Same-file private dependency"}
        return {"result": "Violation", "violation_type": "Cross-file private dependency"}
    if not (parent_is_public_root or parent_is_local_private) and callee_is_local_private:
        return {"result": "Violation", "violation_type": "Cross-file private dependency"}

    return base


def _architecture_violation_summary(edges: list[dict[str, Any]]) -> dict[str, int]:
    """Return counts by architecture violation direction."""
    keys = list(ARCHITECTURE_VIOLATION_TYPES)
    return {
        key: sum(1 for edge in edges if edge.get("architecture_result") == "Violation" and edge.get("violation_type") == key)
        for key in keys
    }

def _decision_warnings(flow: dict[str, Any], callee_rows: list[dict[str, Any]]) -> list[str]:
    """Return architecture decision warnings for a public entrypoint flow."""
    warnings: set[str] = set()
    if flow["maximum_chain_depth"] >= LONG_CALL_CHAIN_DEPTH_THRESHOLD:
        warnings.add("Too many steps")
    if flow.get("direct_call_count", 0) > LARGE_DEPENDENCY_SURFACE_THRESHOLD:
        warnings.add("Too many helpers")
    if flow["modules_touched_count"] > 4:
        warnings.add("Spans many modules")
    if flow["cross_layer_issue_count"]:
        warnings.add("Broken rule")
    if flow["single_use_helper_candidate_count"]:
        warnings.add("Maybe combine")
    return sorted(warnings)


def _decision_action(flow: dict[str, Any], callee_rows: list[dict[str, Any]]) -> str:
    """Return a public-entrypoint simplification recommendation."""
    if flow["architecture_violation_count"]:
        return DECISION_RECOMMENDATIONS["architecture_violation"]
    if flow["single_use_helper_candidate_count"] and flow["downstream_callable_count"] <= 3:
        return DECISION_RECOMMENDATIONS["merge"]
    if flow["single_use_helper_candidate_count"]:
        return DECISION_RECOMMENDATIONS["move_closer"]
    if flow["maximum_chain_depth"] >= LONG_CALL_CHAIN_DEPTH_THRESHOLD or flow.get("direct_call_count", 0) > LARGE_DEPENDENCY_SURFACE_THRESHOLD or flow["modules_touched_count"] > 4:
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
    for qn, row in row_by_qn.items():
        row.setdefault("qualified_name", qn)
    flow_visible_qns = {
        qn
        for qn, row in row_by_qn.items()
        if row.get("layer") in CALLABLE_LAYER_LABELS or row.get("layer") == HIDDEN_PRIVATE_LAYER
    }
    visible_helpers_by_public = {
        public_qn: {
            qn
            for qn in _reachable_callables(public_qn, calls_by_qn, node_by_qn)
            if qn in flow_visible_qns and qn in row_by_qn and _decision_layer_group(row_by_qn[qn]) != "Public function"
        }
        for public_qn in public_qns
    }
    public_users_by_helper: dict[str, set[str]] = {}
    for user_public_qn, helper_qns in visible_helpers_by_public.items():
        for helper_qn in helper_qns:
            public_users_by_helper.setdefault(helper_qn, set()).add(user_public_qn)

    callers_by_qn: dict[str, set[str]] = {}
    for caller_qn, callee_qns in calls_by_qn.items():
        for callee_qn in callee_qns:
            if callee_qn in node_by_qn and caller_qn in node_by_qn:
                callers_by_qn.setdefault(callee_qn, set()).add(caller_qn)

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
                    if child in {public_qn, qn}:
                        continue
                    queue.append((child, depth, parent))
                continue
            if qn in seen_depth and seen_depth[qn] <= depth:
                continue
            seen_depth[qn] = depth
            parent_by_qn[qn] = parent
            for child in sorted(set(calls_by_qn.get(qn, [])) & set(node_by_qn)):
                if child in {public_qn, qn}:
                    continue
                queue.append((child, depth + 1, qn))

        flow_qns = {public_qn, *seen_depth}
        inside_callers_by_qn = {
            qn: sorted(callers_by_qn.get(qn, set()) & flow_qns)
            for qn in seen_depth
        }
        inside_callees_by_qn = {
            qn: sorted(set(calls_by_qn.get(qn, [])) & flow_qns)
            for qn in seen_depth
        }
        outside_callers_by_qn = {
            qn: sorted(callers_by_qn.get(qn, set()) - flow_qns)
            for qn in seen_depth
        }

        def callee_row(qn: str, edge_type: str) -> dict[str, Any]:
            row = row_by_qn[qn]
            parent_row = row_by_qn.get(parent_by_qn.get(qn, public_qn), row_by_qn[public_qn])
            signals = list(row.get("signals", []))
            if _architecture_layer(row_by_qn.get(parent_by_qn.get(qn, ""), {})) == "Internal" and _architecture_layer(row) == "Internal":
                signals = sorted({*signals, "internal_helper_chain"})
            caller_type = _architecture_layer(parent_row)
            callee_type = _architecture_layer(row)
            edge_classification = _classify_two_layer_edge(
                public_qn=public_qn,
                parent_row=parent_row,
                callee_row=row,
                caller_type=caller_type,
                callee_type=callee_type,
                public_user_count=len(public_users_by_helper.get(qn, set())),
            )
            return {
                "callable": row["function_name"],
                "qualified_name": qn,
                "module": row["module"],
                "depth": seen_depth[qn],
                "layer": row.get("layer"),
                "function_type": row.get("function_type"),
                "layer_group": _decision_layer_group(row),
                "simple_classification": _simple_flow_classification(row, len(public_users_by_helper.get(qn, set()))),
                "edge_type": edge_type,
                "parent_qualified_name": parent_by_qn.get(qn, public_qn),
                "caller_type": caller_type,
                "callee_type": callee_type,
                "architecture_result": edge_classification["result"],
                "violation_type": edge_classification["violation_type"],
                "signals": signals,
                "architecture_signals": row.get("architecture_signals", []),
                "recommended_action": row.get("recommended_action"),
                "called_inside_flow_by": len(inside_callers_by_qn.get(qn, [])),
                "calls_inside_flow": len(inside_callees_by_qn.get(qn, [])),
                "used_outside_flow": len(outside_callers_by_qn.get(qn, [])),
                "is_end_node": len(inside_callees_by_qn.get(qn, [])) == 0,
                "downstream_count": row.get("calls_count", 0),
                "source_path": _callable_flow_source_path(qn, module_data),
                "source_url": _callable_flow_source_link(qn, module_data),
                **_callable_flow_source_location(qn, module_data),
                **({"docs_path": row["docs_path"], "docs_url": row["docs_url"]} if row.get("docs_url") else {}),
                "path_examples": _path_examples(public_qn, qn, calls_by_qn, node_by_qn),
                "call_site_count": row.get("call_site_count", 0),
                "recursive": bool(row.get("recursive", False)),
                "repeated_within_single_caller": bool(row.get("repeated_within_single_caller", False)),
                "helper_cleanup_candidate": _decision_layer_group(row) != "Public function"
                and row_by_qn[qn].get("used_by_count", 0) == 1
                and row.get("call_site_count", 0) == 1
                and not row.get("recursive", False),
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
        source_python_files = sorted(
            {
                path
                for qn in {public_qn, *seen_depth}
                if (path := _callable_flow_source_path(qn, module_data)) and path.endswith(".py")
            }
        )
        modules_touched = sorted({node_by_qn[public_qn]["module_name"], *(node_by_qn[qn]["module_name"] for qn in seen_depth)})
        flow = {
            "public_callable": node_by_qn[public_qn]["callable_name"],
            "qualified_name": public_qn,
            "module": node_by_qn[public_qn]["module_name"],
            "docs_path": f"docs/api/reference/{node_by_qn[public_qn]['callable_name']}.md",
            "docs_url": _public_callable_docs_url(node_by_qn[public_qn]["callable_name"]),
            "source_path": _callable_flow_source_path(public_qn, module_data),
            "owner_file": _callable_flow_source_path(public_qn, module_data),
            "source_url": _callable_flow_source_link(public_qn, module_data),
            **_callable_flow_source_location(public_qn, module_data),
            "direct_call_count": len(direct_qns),
            "width": len(direct_qns),
            "scope_asset_count": len(flow_qns),
            "scope": len(flow_qns),
            "downstream_callable_count": len(seen_depth),
            "maximum_chain_depth": max(seen_depth.values(), default=0),
            "modules_touched_count": len(source_python_files),
            "modules_touched": modules_touched,
            "source_python_files": source_python_files,
            "external_dependents_count": sum(1 for qn in seen_depth if outside_callers_by_qn.get(qn)),
            "end_node_count": sum(1 for qn in seen_depth if not inside_callees_by_qn.get(qn)),
            "architecture_violation_count": sum(1 for row in callee_rows if row.get("architecture_result") == "Violation"),
            "architecture_violation_breakdown": _architecture_violation_summary(callee_rows),
            "cross_layer_issue_count": sum(1 for row in callee_rows if row.get("architecture_result") == "Violation"),
            "single_use_helper_candidate_count": sum(
                1
                for row in callee_rows
                if row["layer_group"] != "Public function"
                and row_by_qn[row["qualified_name"]].get("used_by_count", 0) == 1
                and row.get("call_site_count", 0) == 1
                and not row.get("recursive", False)
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
    "public_flows",
    "summary_counts",
    "inventory_row_count",
    "unique_inventory_identity_count",
    "duplicate_inventory_identity_count",
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
    "public_classes",
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
    "reachability",
    "reachability_kind",
    "reachability_label",
    "recommended_action",
    "priority",
    "signals",
    "architecture_signals",
    "review_signals",
    "called_by_count",
    "call_site_count",
    "recursive",
    "repeated_within_single_caller",
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
    "width",
    "direct_call_count",
    "scope",
    "scope_asset_count",
    "downstream_count",
    "max_depth",
    "modules_touched",
    "source_python_files",
    "external_dependents_count",
    "end_node_count",
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
    "simple_classification",
    "edge_type",
    "parent_qualified_name",
    "caller_type",
    "callee_type",
    "architecture_result",
    "violation_type",
    "signals",
    "recommended_action",
    "called_inside_flow_by",
    "call_site_count",
    "recursive",
    "repeated_within_single_caller",
    "calls_inside_flow",
    "used_outside_flow",
    "is_end_node",
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
        "data_source": "function-call-graph.json",
    }
    return metadata


def _format_generated_at_sgt(value: str | None) -> str:
    """Return the visible Singapore timestamp label for callable dashboard metadata."""
    if not value:
        return "Unknown"
    normalized = value.replace("Z", "+00:00")
    try:
        generated_at = datetime.fromisoformat(normalized).astimezone(ZoneInfo("Asia/Singapore"))
    except ValueError:
        return value
    return generated_at.strftime("%Y-%m-%d %H:%M SGT")


def _render_callable_generation_banner(flow_data: dict[str, Any]) -> str:
    """Render shared generation metadata for callable dashboard HTML pages."""
    metadata = flow_data.get("metadata", {})
    parts = [
        f"<strong>Generated at:</strong> {html.escape(_format_generated_at_sgt(metadata.get('generated_at_utc')))}",
        f"<span><strong>Data source:</strong> {html.escape(metadata.get('data_source', 'function-call-graph.json'))}</span>",
    ]
    if metadata.get("branch"):
        parts.append(f"<span><strong>Branch:</strong> {html.escape(metadata['branch'])}</span>")
    if metadata.get("commit"):
        parts.append(f"<span><strong>Commit:</strong> {html.escape(metadata['commit'])}</span>")
    return f'<p class="generation-banner">{"".join(parts)}</p>'


def _format_generated_html_for_review(markup: str) -> str:
    """Return generated HTML formatted for stable human review."""
    try:
        completed = subprocess.run(
            ["npx", "--yes", "prettier", "--parser", "html"],
            input=markup,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        completed = None
    if completed and completed.returncode == 0 and completed.stdout.strip():
        return completed.stdout.rstrip() + "\n"

    parts = re.split(r"(<(?:script|style)\b[^>]*>.*?</(?:script|style)>)", markup, flags=re.IGNORECASE | re.DOTALL)
    formatted_parts: list[str] = []
    for part in parts:
        if re.match(r"<(?:script|style)\b", part, flags=re.IGNORECASE):
            if part.lower().startswith("<style"):
                open_tag, body, close_tag = re.match(r"(<style\b[^>]*>)(.*?)(</style>)", part, flags=re.IGNORECASE | re.DOTALL).groups()
                body = body.replace("}", "}\n").strip()
                formatted_parts.append(f"{open_tag}\n{body}\n{close_tag}")
            else:
                formatted_parts.append(part)
            continue
        formatted = re.sub(r">\s*<", ">\n<", part.strip())
        formatted = re.sub(r"(</th>)\n(<th)", r"\1\2", formatted)
        formatted_parts.append(formatted)
    return "\n".join(piece for piece in formatted_parts if piece) + "\n"

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
        trimmed_flow["width"] = flow.get("width", flow.get("direct_call_count", 0))
        trimmed_flow["direct_call_count"] = flow.get("direct_call_count", trimmed_flow["width"])
        trimmed_flow["scope"] = flow.get("scope", flow.get("scope_asset_count", 0))
        trimmed_flow["scope_asset_count"] = flow.get("scope_asset_count", trimmed_flow["scope"])
        trimmed_flow["downstream_count"] = flow.get("downstream_count", flow.get("downstream_callable_count", 0))
        trimmed_flow["max_depth"] = flow.get("max_depth", flow.get("maximum_chain_depth", 0))
        trimmed_flow["priority"] = "High" if flow.get("architecture_violation_count") else "Medium" if flow.get("warnings") else "Low"
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

    metrics = trimmed_summary.get("callable_inventory_metrics", {})
    compact = {
        "metadata": callable_flow_data["metadata"],
        "architecture_thresholds": callable_flow_data["architecture_thresholds"],
        "function_inventory": inventory,
        "public_entrypoint_flow": public_flows,
        "public_flows": public_flows,
        "summary_counts": trimmed_summary,
        "inventory_row_count": metrics.get("inventory_row_count", len(inventory)),
        "unique_inventory_identity_count": metrics.get("unique_inventory_identity_count", len(inventory)),
        "duplicate_inventory_identity_count": metrics.get("duplicate_inventory_identity_count", 0),
    }
    return {key: compact[key] for key in CALLABLE_FLOW_TOP_LEVEL_KEYS}

def _build_callable_flow_data(
    public_qns: list[str],
    public_class_qns: list[str] | None,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
    *,
    generated_at_utc: datetime,
) -> dict[str, Any]:
    """Build the global public function call graph map from existing call graph data."""
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
        public_class_qns,
        calls_by_qn,
        node_by_qn,
        module_data,
    )

    summary_counts, function_inventory = _build_function_inventory(
        public_qns,
        public_class_qns,
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
        "long_call_chains": sum(1 for flow in public_entrypoint_flow if "Too many steps" in flow["warnings"]),
        "architecture_violations": sum(1 for flow in public_entrypoint_flow if flow["architecture_violation_count"]),
        "architecture_findings": sum(1 for flow in public_entrypoint_flow if flow["architecture_violation_count"]),
        "review_for_merge_helpers": sum(1 for flow in public_entrypoint_flow if flow["single_use_helper_candidate_count"]),
        "suggested_helper_review": sum(
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
                (html.escape(row["next_step"]), "flow-cell-wide"),
            ]
        )
        table_rows.append(cells)

    headers = [
        ("Shared helper", "flow-cell-name"),
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


def _callable_page_nav_css() -> str:
    """Return shared navigation CSS for standalone callable HTML pages."""
    return (
        ".callable-page-nav{display:flex;flex-wrap:wrap;gap:.75rem;align-items:center;"
        "justify-content:space-between;margin:.75rem 0 0;padding:.45rem;border:1px solid #dbe3ef;"
        "border-radius:.75rem;background:#f8fafc}"
        ".callable-page-tabs,.callable-page-actions{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center}"
        ".callable-page-tabs{padding:.2rem;border:1px solid #cbd5e1;border-radius:.55rem;background:#fff}"
        ".callable-page-tab,.callable-page-action{display:inline-flex;align-items:center;justify-content:center;"
        "min-height:2rem;padding:.36rem .7rem;border-radius:.38rem;font-size:.84rem;font-weight:800;"
        "line-height:1.2;text-decoration:none}"
        ".callable-page-tab{border:1px solid transparent;color:#1d4ed8}"
        ".callable-page-tab.is-active{border-color:#1d4ed8;background:#1d4ed8;color:#fff}"
        ".callable-page-action{border:1px solid #cbd5e1;background:#fff;color:#475569}"
        ".callable-page-action:hover,.callable-page-tab:hover{border-color:#93c5fd;background:#eff6ff;color:#1e40af}"
        ".callable-page-tab.is-active:hover{border-color:#1d4ed8;background:#1d4ed8;color:#fff}"
        "@media(max-width:720px){.callable-page-nav{align-items:stretch;flex-direction:column}"
        ".callable-page-tabs,.callable-page-actions{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));width:100%}"
        ".callable-page-tab,.callable-page-action{width:100%;box-sizing:border-box}}"
    )

def _callable_page_shell_css() -> str:
    """Return shared page shell CSS for standalone callable HTML pages."""
    return (
        "body{margin:0;font-family:Inter,system-ui,sans-serif;background:#f8fafc;color:#0f172a}"
        "header,main{box-sizing:border-box;max-width:1480px;margin:0 auto;padding:1rem}"
        "header{background:#fff;border-bottom:1px solid #dbe3ef}"
        "header h1{margin:.1rem 0 .35rem}"
        "header p{margin:.25rem 0;color:#475569}"
        ".generation-banner{display:flex;flex-wrap:wrap;gap:.35rem .75rem;align-items:center;"
        "width:fit-content;max-width:100%;margin:.5rem 0;padding:.35rem .6rem;border:1px solid #cbd5e1;"
        "border-radius:999px;background:#f1f5f9;color:#475569;font-size:.78rem;line-height:1.35}"
        ".generation-banner span{display:inline-flex}"
        f"{_callable_page_nav_css()}"
        "@media(max-width:720px){main,header{padding:.75rem}.generation-banner{width:auto;border-radius:.75rem}}"
    )


def _render_callable_page_nav(active_page: str) -> str:
    """Render shared callable architecture/inventory page navigation."""
    def tab(page: str, label: str, href: str) -> str:
        active = page == active_page
        active_class = " is-active" if active else ""
        current = ' aria-current="page"' if active else ""
        return f'<a class="callable-page-tab{active_class}" href="{href}"{current}>{label}</a>'

    return (
        '<nav class="callable-page-nav" aria-label="Function reference navigation">'
        '<div class="callable-page-tabs" role="list">'
        f'{tab("architecture", "Function Call Graph", "function-call-graph-dashboard.html")}'
        f'{tab("inventory", "Runtime inventory", "function-call-graph-dashboard.html#runtime-inventory")}'
        '</div>'
        '<div class="callable-page-actions">'
        '<a id="openFunctionCallGraphJson" class="callable-page-action" href="../reference/_data/function-call-graph.json">Open JSON data</a>'
        '<a class="callable-page-action" href="../">Back to Docs</a>'
        '</div>'
        '</nav>'
    )

def _render_refactor_dashboard_html(flow_data: dict[str, Any]) -> str:
    """Render the standalone static callable architecture decision dashboard HTML page."""
    generation_banner = _render_callable_generation_banner(flow_data)
    return r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Function Call Graph Dashboard</title><link rel="stylesheet" href="../stylesheets/table-controls.css"><style><!--CALLABLE_PAGE_SHELL_CSS-->.surface-cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.6rem;margin:.5rem 0 .35rem;overflow-x:auto;-webkit-overflow-scrolling:touch}.surface-card{min-width:0}@media(max-width:650px){.surface-cards{grid-template-columns:repeat(3,minmax(13rem,1fr));padding-bottom:.2rem}}.surface-card,.flow-details{background:#fff;border:1px solid #dbe3ef;border-radius:.75rem;padding:.7rem}.surface-card{position:relative;overflow:hidden}.surface-card strong{display:block;margin-bottom:.2rem;line-height:1;font-size:1.35rem}.surface-card span{display:block;line-height:1.2;color:#475569}.surface-card small{display:block;margin-top:.32rem;line-height:1.25;color:#64748b}.surface-card.info{border-color:#bfdbfe;background:#eff6ff}.surface-card.muted{background:#f8fafc}.surface-card.good{border-color:#bbf7d0;background:#f0fdf4}.surface-card.review{border-color:#fde68a;background:#fffbeb}.surface-card.risk{border-color:#fecaca;background:#fef2f2}.surface-card.risk strong{color:#991b1b}.surface-card.review strong{color:#92400e}.surface-card.good strong{color:#166534}.overview-help{margin:.2rem 0 .7rem;color:#475569}.filter-panel{display:grid;grid-template-columns:minmax(16rem,1fr) auto;gap:.55rem;margin:.65rem 0;align-items:end;padding:.65rem;border:1px solid #dbe3ef;border-radius:.75rem;background:#fff}.search-field{font-size:.9rem}.search-field input{margin-top:.3rem;font-size:.9rem}.architecture-clear-all{border:1px solid #cbd5e1;border-radius:.45rem;background:#fff;color:#1d4ed8;font-weight:800}.filter-field{display:flex;flex-direction:column;font-weight:700;font-size:.82rem}input,select,button{padding:.42rem .5rem;border:1px solid #dbe3ef;border-radius:.45rem;background:#fff}.table-actions{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;margin:.55rem 0;color:#64748b;font-size:.82rem}.callable-flow-filter-banner{display:flex;align-items:center;justify-content:space-between;gap:.75rem}.callable-flow-filter-banner strong{min-width:0}.callable-flow-reset-button{background:#15803d;color:#fff;border:1px solid #166534;border-radius:.375rem;padding:.4rem .75rem;font-weight:700;text-decoration:none;cursor:pointer}.callable-flow-reset-button:hover{background:#166534}.table-wrap{overflow:auto;background:#fff;border:1px solid #dbe3ef;border-radius:.75rem}table{width:100%;min-width:940px;border-collapse:collapse}th,td{padding:.3rem .36rem;border-bottom:1px solid #dbe3ef;text-align:left;vertical-align:middle;font-size:.82rem}th{background:#eef2f7;font-size:.72rem}.sort-button{display:inline-flex;gap:.25rem;align-items:center;border:0;background:transparent;color:#1d4ed8;font:inherit;font-weight:800;padding:0;cursor:pointer}.sort-button::after{content:"↕";color:#64748b;font-size:.7rem}.sort-button[aria-sort="ascending"]::after{content:"↑"}.sort-button[aria-sort="descending"]::after{content:"↓"}.num{text-align:right;width:4.5rem;white-space:nowrap}tr[data-public-flow-row]{cursor:pointer}tr[data-public-flow-row]:focus{outline:3px solid #2563eb;outline-offset:-3px}tr.active{outline:2px solid #1d4ed8;outline-offset:-2px;background:#eff6ff;box-shadow:inset .25rem 0 #1d4ed8}.callable-button{border:0;background:transparent;color:#1d4ed8;font-weight:800;padding:0;text-align:left;cursor:pointer}.source-link{color:#1d4ed8;text-decoration:underline;text-underline-offset:.12em}.source-link:hover{color:#1e40af}.compact-list,.compact-badges{display:block;max-width:14rem;line-height:1.35}.review-note summary{display:flex;gap:.25rem;align-items:center;cursor:pointer;list-style:none}.review-note summary::-webkit-details-marker{display:none}.review-note-toggle{border:1px solid #cbd5e1;background:#f8fafc;color:#1d4ed8;font-size:.72rem;font-weight:800}.review-note-panel{margin-top:.35rem;padding:.5rem;border:1px solid #bfdbfe;border-radius:.55rem;background:#eff6ff;color:#334155;line-height:1.4;max-width:28rem;white-space:normal}.inline-more{display:inline-block;position:relative;margin-left:.15rem}.inline-more summary{display:inline-flex;cursor:pointer;list-style:none}.inline-more summary::-webkit-details-marker{display:none}.inline-more[open] .inline-more-panel{display:block}.inline-more-panel{display:none;position:absolute;z-index:5;min-width:13rem;max-width:min(22rem,80vw);max-height:14rem;overflow:auto;margin-top:.2rem;padding:.35rem;border:1px solid #cbd5e1;border-radius:.55rem;background:#fff;box-shadow:0 .75rem 1.5rem #0f172a1f;white-space:normal}.inline-more-panel .tag,.inline-more-panel .badge{margin:.08rem}.tag,.badge{display:inline-flex;margin:.06rem;padding:.1rem .34rem;border-radius:999px;font-size:.69rem;font-weight:700;background:#e0e7ff;color:#3730a3;white-space:nowrap}.warn{background:#fef3c7;color:#92400e}.issue{background:#fee2e2;color:#b91c1c}.keep{background:#dcfce7;color:#166534}.muted{background:#f1f5f9;color:#475569}.priority{font-weight:800}.priority-critical{background:#991b1b;color:#fff}.priority-high{background:#fee2e2;color:#991b1b}.priority-medium{background:#fef3c7;color:#92400e}.priority-low{background:#e2e8f0;color:#475569}tr.priority-critical-row:not(.active){box-shadow:inset .25rem 0 #991b1b}tr.priority-high-row:not(.active){box-shadow:inset .25rem 0 #f59e0b}tr.severity-architecture-row:not(.active){box-shadow:inset .25rem 0 #991b1b;background:#fff7f7}tr.severity-review-row:not(.active){box-shadow:inset .25rem 0 #f59e0b;background:#fffbeb}.summary-toggle{border:1px solid #cbd5e1;background:#f8fafc;color:#1d4ed8;font-size:.72rem;font-weight:800}.summary-row{display:none}.summary-row.is-open{display:table-row}.summary-panel{padding:.7rem;border-left:.25rem solid #cbd5e1;background:#fff;line-height:1.45}.summary-panel.issue{border-left-color:#991b1b}.summary-panel.warn{border-left-color:#f59e0b}.summary-panel h3{margin:.1rem 0 .35rem}.summary-panel h4{margin:.55rem 0 .2rem}.summary-panel p{margin:.15rem 0;color:#334155}.summary-panel ul{margin:.2rem 0 .1rem 1.1rem;padding:0}.recommendation-chip.issue{background:#fee2e2;color:#991b1b}.recommendation-chip.warn{background:#fef3c7;color:#92400e}.export-toolbar{display:flex;flex-direction:column;gap:.5rem;align-items:stretch;box-sizing:border-box;max-width:100%;margin:.65rem 0;padding:.65rem;border:1px solid #dbe3ef;border-radius:.75rem;background:#f8fafc}.toolbar-card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,18rem),1fr));gap:.5rem}.toolbar-card{box-sizing:border-box;min-width:0;padding:.5rem .6rem;border:1px solid #e2e8f0;border-radius:.6rem;background:#fff}.toolbar-card--selection,.toolbar-card--prompt{display:flex;flex-direction:column;gap:.55rem}.toolbar-row{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;max-width:100%;min-width:0}.toolbar-field{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center;max-width:100%;min-width:0;font-weight:700}.toolbar-field select{max-width:100%;min-width:0}.toolbar-help,.group-help{color:#475569;font-weight:400}.compat-mode-subtitle{margin-top:.35rem;font-size:.85rem;line-height:1.35}.compat-mode-safe{color:#1d4ed8}.compat-mode-review{color:#b45309}.compat-mode-breaking{color:#b91c1c}.toolbar-group{display:flex;flex-wrap:wrap;gap:.5rem 1rem;align-items:center;max-width:100%;min-width:0}.toolbar-group>div{min-width:0}.toolbar-group .toolbar-row{flex:1 1 16rem}.toolbar-row button{white-space:normal}.primary-action,.danger-action:not(:disabled){background:#1d4ed8;color:#fff;border-color:#1d4ed8}.danger-action:not(:disabled){background:#b91c1c;border-color:#b91c1c}button:disabled,.danger-action:disabled{background:#e5e7eb;color:#94a3b8;border-color:#cbd5e1;cursor:not-allowed}.flow-details{margin-top:1rem}.flow-summary-card{display:flex;flex-direction:column;gap:.5rem;margin:.55rem 0 .75rem;padding:.75rem;border:1px solid #bfdbfe;border-radius:.75rem;background:#eff6ff}.flow-summary-heading{display:flex;flex-wrap:wrap;gap:.5rem;align-items:flex-start;justify-content:space-between}.flow-summary-heading strong{display:block;font-size:1rem}.flow-summary-heading small{display:block;margin-top:.12rem;color:#475569;overflow-wrap:anywhere}.flow-summary-recommendation{display:flex;flex-wrap:wrap;gap:.35rem .5rem;align-items:center}.flow-summary-recommendation span{color:#64748b;font-weight:800}.flow-summary-card p{margin:.1rem 0 0;color:#334155}.flow-meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(135px,1fr));gap:.5rem}.flow-meta div{padding:.45rem;border:1px solid #e2e8f0;border-radius:.5rem;background:#f8fafc}.flow-key-signals,.flow-next-step{margin:.75rem 0;padding:.65rem;border:1px solid #dbe3ef;border-radius:.75rem;background:#fff}.flow-key-signals h3,.flow-next-step h3{margin:.05rem 0 .45rem}.flow-key-signals div{display:flex;flex-wrap:wrap;gap:.25rem}.flow-key-signals p,.flow-next-step p{margin:.45rem 0 0;color:#475569}.flow-tree{max-height:60vh;overflow:auto;border:1px solid #dbe3ef;border-radius:.5rem;padding:.45rem;background:#fff}.flow-tree ul{list-style:none;margin:.35rem 0 .35rem 1rem;padding-left:.85rem;border-left:1px solid #dbe3ef}.flow-tree li{margin:.28rem 0}.flow-tree details{border:1px solid #e2e8f0;border-radius:.6rem;background:#f8fafc}.flow-tree details[open]{background:#fff}.flow-tree summary{display:flex;flex-wrap:wrap;gap:.3rem;align-items:center;padding:.32rem .45rem;cursor:pointer;list-style:none}.flow-tree summary::-webkit-details-marker{display:none}.flow-tree summary::before{content:'▸';flex:0 0 auto;color:#64748b;font-weight:800}.flow-tree details[open]>summary::before{content:'▾'}.flow-tree-main{display:flex;flex:1 1 auto;flex-wrap:wrap;gap:.22rem .35rem;align-items:center;min-width:0}.flow-tree-main strong{min-width:0;font-weight:850}.flow-tree-details{margin:0 .45rem .42rem;padding:.22rem .35rem;border:1px solid #e2e8f0;border-radius:.45rem;background:#fff}.flow-tree-detail-strip{display:flex;flex-wrap:wrap;gap:.18rem .28rem;align-items:center}.flow-tree-detail-chip{display:inline-flex;gap:.18rem;align-items:center;padding:.08rem .32rem;border:1px solid #e2e8f0;border-radius:999px;background:#f8fafc;color:#64748b;font-size:.68rem}.flow-tree-detail-chip strong{color:#334155;font-weight:800}.flow-tree-detail-notes{display:flex;flex-direction:column;gap:.12rem;margin-top:.22rem;color:#64748b;font-size:.72rem;line-height:1.35;overflow-wrap:anywhere}.badge.critical{background:#fee2e2;color:#991b1b}.badge.info{background:#dbeafe;color:#1e40af}@media(max-width:720px){.flow-tree ul{margin-left:.45rem;padding-left:.65rem}}@media(max-width:720px){main,header{padding:.75rem}.generation-banner{width:auto;border-radius:.75rem}.filter-panel{grid-template-columns:1fr}table{min-width:760px}th,td{font-size:.78rem;padding:.26rem}.compact-list,.compact-badges{max-width:10rem}.surface-card strong{font-size:1.35rem}.toolbar-card-grid{grid-template-columns:1fr}.toolbar-row,.toolbar-group{align-items:stretch}.toolbar-field,.toolbar-group{flex-direction:column}.toolbar-field select{width:100%}.toolbar-help{display:block}.toolbar-group .toolbar-row{flex:1 1 auto;flex-direction:row}.toolbar-group .toolbar-row button{flex:1 1 9rem}.callable-flow-filter-banner{align-items:flex-start;flex-direction:column}.callable-flow-reset-button{width:100%;box-sizing:border-box;text-align:center}}</style></head><body><header><h1>Function Call Graph Dashboard</h1><p>The Function Call Graph Dashboard shows how public functions, shared helpers, and private helpers connect across the package. Use it to inspect function dependencies, architecture boundaries, and cleanup candidates.</p><!--CALLABLE_GENERATION_BANNER--><!--CALLABLE_PAGE_NAV--></header><main><h2>Public callable overview</h2><div id="publicSurfaceCards" class="surface-cards"></div><p class="overview-help"><small>Helper suggestions are review hints, not automatic judgments. A helper used by one function can still be useful if it makes the code easier to read, avoids repeated code, is used several times inside that function, or calls itself recursively.</small></p><p class="overview-help"><small>Review architecture scopes, search for risks, and inspect the selected function call graph when available. Width is direct calls; scope is total runtime assets in the selected scope.</small></p><section class="filter-panel search-toolbar" aria-label="Public callable search"><label class="filter-field search-field">Search public callables<input id="publicSearchBox" type="search" placeholder="Search by callable, module, signal, or next step..."></label><button id="resetPublicFilters" class="architecture-clear-all" type="button" hidden>Clear search</button></section><section id="architectureViolationSection" class="flow-details"></section><section id="selectedPublicFlowSummary"></section><section id="publicFlowDetails" class="flow-details"><h2>Selected public function flow</h2><p>Select a public function to inspect its direct calls and transitive support functions/helpers.</p></section><section class="table-actions"><button id="showAllPublicCallables" type="button" hidden>Show all public callables</button><button id="collapsePublicList" type="button" hidden>Collapse list</button><small id="publicListStatus"></small><small id="dataLoadStatus" class="load-status" aria-live="polite">Loading function call graph data...</small></section><section class="table-wrap" id="publicCallableTableWrap"><table data-table-controls="excel"><thead><tr><th><button type="button" class="sort-button" data-sort-key="callable">Function</button></th><th><button type="button" class="sort-button" data-sort-key="width">Width</button></th><th><button type="button" class="sort-button" data-sort-key="scope">Scope</button></th><th><button type="button" class="sort-button" data-sort-key="depth">Depth</button></th><th><button type="button" class="sort-button" data-sort-key="recommendation">Recommendation</button></th><th><button type="button" class="sort-button" data-sort-key="signals">Signals</button></th><th>Summary</th></tr></thead><tbody id="publicCallableList"></tbody></table></section><section class="export-toolbar" aria-label="Advanced cleanup and export actions"><h2>Cleanup package</h2><p class="toolbar-help">Use this after reviewing the function call graph when you want Codex or another AI tool to plan a focused refactor.</p><div class="toolbar-card-grid"><div class="toolbar-card toolbar-card--compatibility"><label class="toolbar-field">Compatibility mode <select id="compatibilityMode"><option value="preserve_backwards_compatibility" selected>Preserve backwards compatibility</option><option value="allow_breaking_changes">Allow breaking changes</option></select></label><small id="compatibilityModeSubtitle" class="compat-mode-subtitle compat-mode-safe">Selected cleanup should preserve existing public callable behavior and avoid breaking current users.</small></div><div class="toolbar-card toolbar-card--prompt"><div class="toolbar-group"><div><strong>Export function call graph cleanup packet</strong><br><small class="group-help">Download the selected public function call graph for AI-assisted cleanup planning.</small></div><div class="toolbar-row"><button id="downloadJson" type="button" disabled>Download JSON</button><button id="downloadYaml" type="button" disabled>Download YAML</button></div></div><small id="exportStatus"></small></div></div></section></main><script>
const FLOW_LAYER_LABELS=['Public function','Shared helper','Private helper','Class','Method','Unknown'];const COMPATIBILITY_MODES={preserve_backwards_compatibility:{label:'Preserve backwards compatibility',subtitle:'Selected cleanup should preserve existing public callable behavior and avoid breaking current users.',promptInstruction:'Preserve existing public callable behavior, public names, public signatures, exported packet schema, and user-facing behavior. Helper boundaries, private functions, classes, and implementation details may be cleaned up only when external behavior is preserved. Clearly call out any migration risks.',className:'compat-mode-safe'},allow_breaking_changes:{label:'Allow breaking changes',subtitle:'Selected cleanup may propose cleaner breaking changes when they improve the callable architecture.',promptInstruction:'Propose cleaner breaking changes where they improve architecture, naming, boundaries, maintainability, or long-term usability. Clearly label each breaking change, explain why it is worth doing, identify migration impact, and propose a migration path.',className:'compat-mode-breaking'}};const INTERNAL_LAYERING_SUGGESTED_FIX='Move single-use helpers into the owning public callable file. Keep only helpers reused across multiple public callables in shared internal modules. Flatten nested helper chains where they do not provide reusable shared behavior.';const DISPLAY_LABEL_MAP={'Broken rule':'Broken rule','Too many steps':'Too many steps','Too many helpers':'Too many helpers','Maybe combine':'Maybe combine','Used by one function':'Used by one function','Used several times in one function':'Used several times in one function','Recursive helper':'Recursive helper','Heavily used helper':'Heavily used helper','Shared utility':'Shared utility','None':'Healthy'};let inventory=[],publicEntryFlows=[],visibleFlows=[],summaryCounts={},inventoryByQn=new Map();const state={selectedFlow:'',activePublicFlow:'',openSummaryFlow:'',collapsedPublicList:false,publicSearch:'',sortKey:'callable',sortDirection:'asc'};let architectureThresholds={long_call_chain_depth:null,large_dependency_surface:null};function positiveThreshold(value){const numeric=Number(value);return Number.isFinite(numeric)&&numeric>0?numeric:null}function longCallChainThreshold(){return positiveThreshold(architectureThresholds.long_call_chain_depth)}function largeDependencySurfaceThreshold(){return positiveThreshold(architectureThresholds.large_dependency_surface)}const $=id=>document.getElementById(id),text=v=>String(v??''),esc=v=>text(v).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));function unique(v){return[...new Set(v.filter(Boolean))].sort()}function displayLabel(v){return DISPLAY_LABEL_MAP[text(v)]||text(v)}function label(v){return displayLabel(text(v).replace(/_/g,' ').replace(/\b\w/g,ch=>ch.toUpperCase()))}function option(s,v,l){const o=document.createElement('option');o.value=v;o.textContent=l||v;s.appendChild(o)}function compactList(items,limit=3){const list=items||[],shown=list.slice(0,limit);return `<span class="compact-list" title="${esc(list.join(', '))}">${shown.map(i=>`<span class="tag">${esc(i)}</span>`).join('')}</span>`}function compactBadges(items,cls='warn',limit=3){const list=items||[],shown=list.slice(0,limit);return `<span class="compact-badges" title="${esc(list.join(', '))}">${shown.map(i=>`<span class="badge ${cls}">${esc(i)}</span>`).join('')}</span>`}const GITHUB_SOURCE_BASE='https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/';function sourceHref(i){const row=inventoryByQn.get(i.qualified_name)||i;if(row.docs_path)return '../'+String(row.docs_path).replace(/^docs\//,'').replace(/\.md$/,'/');if(row.source_url)return row.source_url;const path=row.source_path||row.path;if(!path)return '';const start=row.source_start_line||row.start_line||row.line_number;const end=row.source_end_line||row.end_line;let anchor=start?`#L${start}`:'';if(start&&end&&end!==start)anchor+=`-L${end}`;return `${GITHUB_SOURCE_BASE}${path}${anchor}`}function sourceCallableLink(i){const href=sourceHref(i);const label=esc(i.function_name);return href?`<a class="source-link" href="${esc(href)}"><code>${label}</code></a>`:`<code>${label}</code>`}function moduleHref(module){return ''}function moduleLink(module){const href=moduleHref(module);return href?`<a class="source-link" href="${esc(href)}"><code>${esc(module)}</code></a>`:`<code>${esc(module||'')}</code>`}function linkMetadata(i){const row=inventoryByQn.get(i.qualified_name)||i;return{source_url:row.source_url||null,docs_url:row.docs_url||null,file_path:row.source_path||null,line_start:row.source_start_line||null,line_end:row.source_end_line||null}}function markdownLink(i,label){const href=sourceHref(i);return href?`[${label||i.function_name}](${href})`:(label||i.function_name)}function hasArchitectureViolation(flow){return architectureFindingCount(flow)>0}function isGraphReviewCandidate(flow){const longThreshold=longCallChainThreshold(),largeThreshold=largeDependencySurfaceThreshold(),deep=longThreshold!==null&&(flow.max_depth||0)>=longThreshold,wide=largeThreshold!==null&&(flow.width||0)>largeThreshold;return !hasArchitectureViolation(flow)&&(deep||wide)}function publicCallableSeverity(flow){if(hasArchitectureViolation(flow))return 'architecture';if(isGraphReviewCandidate(flow))return 'review';return 'neutral'}function architecturePriority(f){const severity=publicCallableSeverity(f);if(severity==='architecture')return 'Critical';if(severity==='review')return 'Medium';return 'Low'}function priorityClass(p){return text(p).toLowerCase()}function riskBadgeClass(warning,priority){if(priority==='Critical')return 'issue';return 'muted'}function mergeCandidateCount(flow){return Number(flow.helper_cleanup_candidates??flow.single_use_helper_candidate_count??0)}function mergeCandidateLabel(count){return count===1?'Maybe combine':`${count} maybe combine`}function reviewMergeCandidateLabel(count){return count===1?'Review helper':'Review helpers'}function architectureFindingCount(flow){return architectureFindingRows(flow).length||(flow.architecture_violation_count??0)}function flowSignals(flow){const longThreshold=longCallChainThreshold(),largeThreshold=largeDependencySurfaceThreshold(),signals=[];if(architectureFindingCount(flow)>0)signals.push('Broken rule');if(longThreshold!==null&&(flow.max_depth||0)>=longThreshold)signals.push('Too many steps');if(largeThreshold!==null&&(flow.width||0)>largeThreshold)signals.push('Too many helpers');if((flow.external_dependents_count||0)>0)signals.push('Shared helper');if(mergeCandidateCount(flow)>0)signals.push('Maybe combine');return signals}function suggestedActionLabel(flow){if(hasArchitectureViolation(flow))return 'Fix architecture issue';if(isGraphReviewCandidate(flow))return 'Review nested helpers';return ''}function recommendationBadge(flow){const action=suggestedActionLabel(flow);if(!action)return '';return `<span class="badge recommendation-chip ${action==='Fix architecture issue'?'issue':'warn'}">${esc(action)}</span>`}function signalBadges(flow){const signals=flowSignals(flow).slice(0,3),severity=publicCallableSeverity(flow),cls=severity==='architecture'?'issue':severity==='review'?'warn':'info';return compactBadges(signals,cls,3)}function summaryText(flow){const signals=flowSignals(flow),hasInfo=signals.includes('Shared helper')||signals.includes('Maybe combine');if(hasArchitectureViolation(flow))return 'Architecture issues were detected in this public callable. Fix these first before reviewing helper cleanup.';if(isGraphReviewCandidate(flow))return 'This callable exceeds the width or depth review threshold and may be worth simplifying before refactoring.';if(hasInfo)return 'Informational signals only. No public-callable-level review candidate was detected.';return 'No review flags detected.'}function recommendedCheck(flow){if(hasArchitectureViolation(flow))return 'Resolve the architecture issue, then re-run the call graph review.';if(isGraphReviewCandidate(flow))return 'Review whether the deep or wide helper graph should stay separate, move into shared helper logic, or be simplified.';return 'No follow-up needed.'}function summaryButton(flow){const open=state.openSummaryFlow===flow.qualified_name;return `<button class="summary-toggle" type="button" aria-expanded="${open?'true':'false'}" data-summary-toggle="${esc(flow.qualified_name)}">View summary</button>`}function summaryRow(flow){const open=state.openSummaryFlow===flow.qualified_name,severity=flowSignals(flow).includes('Broken rule')?'issue':suggestedActionLabel(flow)?'warn':'';return `<tr class="summary-row ${open?'is-open':''}" data-summary-row="${esc(flow.qualified_name)}"><td colspan="7"><div class="summary-panel ${severity}"><h3>Summary</h3><p>${esc(summaryText(flow))}</p><h4>Recommended check</h4><p>${esc(recommendedCheck(flow))}</p><h4>Evidence</h4><ul><li>Width: ${esc(flow.width??0)} direct call(s)</li><li>Scope: ${esc(flow.scope??flow.scope_asset_count??0)} runtime asset(s)</li><li>Depth: ${esc(flow.max_depth||0)}</li><li>Broken rules: ${esc(architectureFindingCount(flow))}</li><li>Shared impact: ${esc(flow.external_dependents_count||0)}</li><li>Maybe combine helpers: ${esc(mergeCandidateCount(flow))}</li></ul>${flowSignals(flow).length?`<p><strong>All signals:</strong> ${esc(flowSignals(flow).join(', '))}</p>`:''}</div></td></tr>`}function renderCards(){const s=summaryCounts.public_api_surface||{},flows=publicEntryFlows||[],publicCallableCount=flows.length||s.public_api_entrypoints||0,architectureViolationFlows=flows.filter(hasArchitectureViolation).length,reviewCandidateFlows=flows.filter(isGraphReviewCandidate).length;const cards=[{label:'Public callables',value:publicCallableCount,subtitle:'Notebook-facing APIs scanned in this review workspace.',cls:'info'},{label:'Broken rules',value:architectureViolationFlows,subtitle:architectureViolationFlows?'Public callables with true architecture violations.':'No architecture violations found.',cls:architectureViolationFlows?'risk':'good'},{label:'Review candidates',value:reviewCandidateFlows,subtitle:reviewCandidateFlows?'Public callables over width or depth review thresholds.':'No graph review candidates found.',cls:reviewCandidateFlows?'review':'good'}];$('publicSurfaceCards').innerHTML=cards.map(c=>`<article class="surface-card ${esc(c.cls)}"><strong>${esc(c.value??0)}</strong><span>${esc(c.label)}</span><small>${esc(c.subtitle)}</small></article>`).join('')}function findingLabel(v){return displayLabel(v)}function architectureViolationBreakdown(flows=publicEntryFlows){const counts={'Public function calls public function':0,'Shared helper calls public function':0,'Cross-file private dependency':0};flows.forEach(f=>(f.transitive_callees||[]).forEach(c=>{if(c.architecture_result==='Violation'&&counts[c.violation_type]!==undefined)counts[c.violation_type]++}));return counts}function renderArchitectureViolationSection(){const meanings={'Public function calls public function':'A notebook-facing public callable depends on another public callable instead of shared implementation details.','Shared helper calls public function':'A reusable shared/internal helper calls back into a notebook-facing public callable.','Cross-file private dependency':'A helper directly calls a private helper from another source file.'};const rows=Object.entries(architectureViolationBreakdown()).filter(([,count])=>count>0);$('architectureViolationSection').innerHTML=`<h2>Broken rules</h2><p>Broken rules show dependency edges that break the intended public-callable/shared-helper model.</p><div class="table-wrap"><table><thead><tr><th>Violation type</th><th class="num">Count</th><th>Meaning</th></tr></thead><tbody>${(rows.length?rows:Object.entries(meanings).map(([k])=>[k,0])).map(([type,count])=>`<tr><td>${esc(type)}</td><td class="num">${esc(count)}</td><td>${esc(meanings[type])}</td></tr>`).join('')}</tbody></table></div><details><summary><strong>How architecture violations are calculated</strong></summary><p>Public functions are notebook-facing entrypoints and must not be called by public callables or shared helpers. Shared helpers are reusable implementation details. Private helpers stay owner-local, and Unknown marks uncertain helper placement.</p><table><thead><tr><th>Caller type</th><th>Callee type</th><th>Result</th></tr></thead><tbody>${[['Public function','Shared helper','Allowed'],['Public function','Private helper in same file','Warning only'],['Shared helper','Public function','Broken rule'],['Shared helper','Private helper in same file','Warning only'],['Shared helper','Private helper in another file','Broken rule'],['Private helper','Shared helper','Allowed']].map(r=>`<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td></tr>`).join('')}</tbody></table></details>`}function architectureViolationCount(flow){const numeric=Number(flow.architecture_violation_count??0);return Number.isFinite(numeric)?numeric:0}function architectureFindingRows(flow){return (flow.transitive_callees||[]).filter(c=>c.architecture_result==='Violation'||c.recommended_action==='Broken rule')}function architectureFindingCount(flow){return architectureFindingRows(flow).length}function updatePublicFilterControls(){$('resetPublicFilters').hidden=state.publicSearch===''}function filteredPublicFlows(){const q=state.publicSearch.toLowerCase();return publicEntryFlows.filter(f=>(!q||text(f.function_name).toLowerCase().includes(q)||text(f.qualified_name).toLowerCase().includes(q)||text(f.module).toLowerCase().includes(q)))}function sortValue(flow,key){if(key==='callable')return text(flow.function_name).toLowerCase();if(key==='width')return Number(flow.width??0);if(key==='scope')return Number(flow.scope??flow.scope_asset_count??0);if(key==='depth')return Number(flow.max_depth??0);if(key==='recommendation')return suggestedActionLabel(flow).toLowerCase();if(key==='signals')return flowSignals(flow).join(' ').toLowerCase();return text(flow.function_name).toLowerCase()}function stableSortRows(rows){const dir=state.sortDirection==='desc'?-1:1,key=state.sortKey;return rows.map((row,index)=>({row,index})).sort((a,b)=>{const av=sortValue(a.row,key),bv=sortValue(b.row,key);if(av<bv)return -1*dir;if(av>bv)return 1*dir;return a.index-b.index}).map(item=>item.row)}function updateSortButtons(){document.querySelectorAll('[data-sort-key]').forEach(button=>{const active=button.dataset.sortKey===state.sortKey;button.setAttribute('aria-sort',active?(state.sortDirection==='asc'?'ascending':'descending'):'none')})}function rowsForDisplay(){if(!state.collapsedPublicList)return visibleFlows;return visibleFlows.filter(f=>f.qualified_name===state.activePublicFlow)}function setPublicListControls(){const active=publicEntryFlows.find(i=>i.qualified_name===state.activePublicFlow);$('showAllPublicCallables').hidden=!state.collapsedPublicList;$('collapsePublicList').hidden=state.collapsedPublicList||!active;$('publicListStatus').textContent=state.collapsedPublicList&&active?`Showing selected function from ${visibleFlows.length} matching public functions.`:`Showing ${visibleFlows.length} matching public functions.`;const showSelectedBanner=Boolean(state.collapsedPublicList&&active);$('selectedPublicFlowSummary').classList.toggle('is-visible',showSelectedBanner);$('selectedPublicFlowSummary').innerHTML=showSelectedBanner?`<div class="callable-flow-filter-banner"><strong>Showing graph for <code>${esc(active.function_name)}</code></strong><button type="button" id="backToAllPublicCallables" class="callable-flow-reset-button">Back to all public functions</button></div>`:'';const reset=$('backToAllPublicCallables');if(reset)reset.onclick=showAllPublicCallables}function renderLoadStatus(message,isError=false){const el=$('dataLoadStatus');if(!el)return;el.textContent=message;el.className=isError?'load-status issue':'load-status'}function functionCallGraphDataUrl(){const path=window.location.pathname,origin=window.location.origin,referenceMarker='/reference/',assetsMarker='/assets/';if(path.includes(referenceMarker)){return origin+path.slice(0,path.indexOf(referenceMarker)+referenceMarker.length)+'_data/function-call-graph.json'}if(path.includes(assetsMarker)){return origin+path.slice(0,path.indexOf(assetsMarker)+1)+'reference/_data/function-call-graph.json'}return new URL('reference/_data/function-call-graph.json',document.baseURI).href}function updateFunctionCallGraphDataLink(url){const link=$('openFunctionCallGraphJson');if(link)link.href=url}function renderLoadedCount(){renderLoadStatus(`Loaded ${inventory.length} total functions; ${publicEntryFlows.length} public functions available; ${visibleFlows.length} rows after filters.`)}function renderPublicCallableList(){visibleFlows=stableSortRows(filteredPublicFlows());updatePublicFilterControls();if(!state.activePublicFlow&&visibleFlows.length)state.activePublicFlow=visibleFlows[0].qualified_name;if(state.activePublicFlow&&!visibleFlows.some(f=>f.qualified_name===state.activePublicFlow))state.collapsedPublicList=false;const rows=rowsForDisplay();renderLoadedCount();const allRuntimeCount=inventory.length,unreachableRuntimeCount=inventory.filter(row=>row.reachability==='unreachable_runtime_asset').length,specialRows=`<tr data-architecture-scope-special="all" tabindex="0"><td><button type="button" class="callable-button">All runtime assets</button></td><td class="num">—</td><td class="num">${esc(allRuntimeCount)}</td><td class="num">—</td><td></td><td><span class="badge info">Runtime scope</span></td><td></td></tr><tr data-architecture-scope-special="unreachable" tabindex="0"><td><button type="button" class="callable-button">Others / Cannot trace back to a public function</button></td><td class="num">—</td><td class="num">${esc(unreachableRuntimeCount)}</td><td class="num">—</td><td><span class="badge warn">Verify possible orphan</span></td><td><span class="badge warn">Cannot trace back to a public function</span></td><td></td></tr>`;$('publicCallableList').innerHTML=specialRows+rows.map(f=>{const severity=publicCallableSeverity(f),active=f.qualified_name===state.activePublicFlow?'active':'';return `<tr data-public-flow-row="${esc(f.qualified_name)}" class="${active} severity-${severity}-row" tabindex="0" aria-selected="${state.selectedFlow===f.qualified_name?'true':'false'}"><td>${sourceCallableLink(f)}</td><td class="num">${esc(f.width??0)}</td><td class="num">${esc(f.scope??f.scope_asset_count??0)}</td><td class="num">${esc(f.max_depth||0)}</td><td>${recommendationBadge(f)}</td><td>${signalBadges(f)}</td><td>${summaryButton(f)}</td></tr>${summaryRow(f)}`}).join('');setPublicListControls();updateSortButtons();renderFlowDetails();updateExportControls();if(window.FabricOpsTableControls)window.FabricOpsTableControls.enhance(document.querySelector('table[data-table-controls="excel"]'))}function showAllPublicCallables(){state.collapsedPublicList=false;renderPublicCallableList();$('publicCallableTableWrap').scrollIntoView({behavior:'smooth',block:'start'})}function collapsePublicList(){state.collapsedPublicList=true;renderPublicCallableList();$('publicFlowDetails').scrollIntoView({behavior:'smooth',block:'start'})}function buildFlowTree(flow){const root={qualified_name:flow.qualified_name,function_name:flow.function_name,module:flow.module,function_type:'Public function',layer_group:'Public function',simple_classification:'Public function',source_path:flow.source_path,calls_inside_flow:(flow.direct_callees||[]).length,called_inside_flow_by:0,used_outside_flow:0,is_end_node:!(flow.direct_callees||[]).length,docs_url:flow.docs_url,docs_path:flow.docs_path,source_url:flow.source_url,children:[]},byParent=new Map();(flow.transitive_callees||[]).forEach(r=>{const p=r.parent_qualified_name||flow.qualified_name;if(!byParent.has(p))byParent.set(p,[]);byParent.get(p).push({...r,children:[]})});function attach(n){n.children=(byParent.get(n.qualified_name)||[]).sort((a,b)=>a.depth-b.depth);n.children.forEach(attach);return n}return attach(root)}function flowTreeStatusChips(n){const chips=[];if(n.architecture_result==='Violation')chips.push('<span class="badge critical" title="This edge breaks the callable architecture boundary.">Violation</span>');if(n.architecture_result==='Warning')chips.push('<span class="badge warn" title="This edge deserves attention before refactoring.">Warning</span>');if(n.helper_cleanup_candidate)chips.push('<span class="badge muted" title="This helper is used by one function, and that function uses it once. Review whether keeping it separate makes the code easier to read.">Maybe combine</span>');if((n.used_outside_flow??0)>0)chips.push('<span class="badge info" title="This helper is reused outside the selected flow; check callers before moving it.">Shared helper</span>');return chips.join('')}function flowTreeDetailRows(n){const rows=[['Called by',n.called_inside_flow_by??0],['Calls',n.calls_inside_flow??0],['Used outside',n.used_outside_flow??0],['Source',n.source_path?String(n.source_path).replace(/^src\/fabricops_kit\//,''):(n.module||'Unknown')]];if(n.architecture_result)rows.push(['Architecture',n.architecture_result]);return rows}function flowTreeLongDetails(n){const details=[];if(n.architecture_result==='Violation')details.push(['Violation reason',n.violation_type||'Broken rule']);if(n.architecture_result==='Warning')details.push(['Warning reason','Nested helper may be too small, too specific, or reused in a way that needs cleanup.']);if(n.helper_cleanup_candidate)details.push(['Review action','Keep as helper, move to shared helper, or merge into caller.']);if(n.path_examples&&n.path_examples.length)details.push(['Path example',n.path_examples[0].join(' -> ')]);return details}function flowTreeDetails(n){const longDetails=flowTreeLongDetails(n);return `<div class="flow-tree-details"><div class="flow-tree-detail-strip">${flowTreeDetailRows(n).map(([label,value])=>`<span class="flow-tree-detail-chip"><span>${esc(label)}</span> <strong>${esc(value)}</strong></span>`).join('')}</div>${longDetails.length?`<div class="flow-tree-detail-notes">${longDetails.map(([label,value])=>`<span><strong>${esc(label)}:</strong> ${esc(value)}</span>`).join('')}</div>`:''}</div>`}function renderTreeNode(n){const type=n.simple_classification||'Unknown',moduleText=n.source_path?String(n.source_path).replace(/^src\/fabricops_kit\//,''):(n.module||''),status=flowTreeStatusChips(n),children=n.children?.length?`<ul>${n.children.map(renderTreeNode).join('')}</ul>`:'';return `<li><details><summary><span class="flow-tree-main"><strong>${sourceCallableLink(n)}</strong><span class="badge muted">${esc(type)}</span>${moduleText?`<span class="tag">${esc(moduleText)}</span>`:''}${status}</span></summary>${flowTreeDetails(n)}</details>${children}</li>`}function flowHealth(flow,architectureFindings,mergeCandidates){if(hasArchitectureViolation(flow))return 'Needs architecture review';if(isGraphReviewCandidate(flow))return 'Graph review candidate';if((flow.external_dependents_count||0)>0||mergeCandidateCount(flow)>0)return 'Informational signals';return 'Healthy'}function flowReason(flow,architectureFindings,mergeCandidates){if(hasArchitectureViolation(flow))return `${architectureFindings.length} architecture finding(s) need review; open the flow tree for exact nodes.`;if(isGraphReviewCandidate(flow))return 'This public callable exceeds a width or depth review threshold.';if((flow.external_dependents_count||0)>0||mergeCandidates.length)return 'Informational signals are present, but this public callable is not a graph review candidate.';return 'No architecture violations found in this graph.'}function flowNextStepLabel(flow,architectureFindings=[],mergeCandidates=[]){const explicit=text(flow?.recommended_simplification_action??flow?.recommended_action??flow?.next_step).trim();if(explicit&&explicit!=='Next step')return displayLabel(explicit);if(hasArchitectureViolation(flow||{}))return 'Fix architecture issue';if(isGraphReviewCandidate(flow||{}))return 'Review nested helpers';return explicit?displayLabel(explicit):''}function flowNextStep(flow,architectureFindings,mergeCandidates){const label=flowNextStepLabel(flow,architectureFindings,mergeCandidates);if(label==='Fix architecture issue')return 'Fix architecture issues before refactoring this callable.';if(label==='Review nested helpers')return 'Review nested helpers because this public callable exceeds a width or depth threshold.';return label}function flowSignalChips(flow,architectureFindings,mergeCandidates){const chips=[];const longThreshold=longCallChainThreshold(),largeThreshold=largeDependencySurfaceThreshold();chips.push(architectureFindings.length?`<span class="badge critical">${architectureFindings.length} architecture finding${architectureFindings.length===1?'':'s'}</span>`:'<span class="badge keep">No architecture violations</span>');if(longThreshold!==null&&(flow.max_depth||0)>=longThreshold)chips.push('<span class="badge warn">Too many steps</span>');if(largeThreshold!==null&&(flow.width||0)>largeThreshold)chips.push('<span class="badge warn">Too many helpers</span>');if(mergeCandidates.length)chips.push(`<span class="badge muted">${mergeCandidates.length} maybe combine</span>`);if((flow.external_dependents_count||0)>0)chips.push('<span class="badge info">Shared helper</span>');return chips.slice(0,5).join('')}function renderFlowDetails(){const f=publicEntryFlows.find(i=>i.qualified_name===state.activePublicFlow);if(!f){$('publicFlowDetails').innerHTML='<p>No public function graph data found.</p>';return}const tree=buildFlowTree(f),architectureFindings=architectureFindingRows(f),mergeCandidates=(f.transitive_callees||[]).filter(c=>c.helper_cleanup_candidate),longThreshold=longCallChainThreshold(),health=flowHealth(f,architectureFindings,mergeCandidates),reason=flowReason(f,architectureFindings,mergeCandidates),nextStep=flowNextStep(f,architectureFindings,mergeCandidates),nextStepLabel=flowNextStepLabel(f,architectureFindings,mergeCandidates),signals=flowSignalChips(f,architectureFindings,mergeCandidates);$('publicFlowDetails').innerHTML=`<h2>Selected public function flow</h2><section class="flow-summary-card"><div class="flow-summary-heading"><div><strong>${sourceCallableLink(f)}</strong><small>${esc(f.qualified_name)}</small></div><span class="badge ${publicCallableSeverity(f)==='architecture'?'critical':publicCallableSeverity(f)==='review'?'warn':'keep'}">${esc(health)}</span></div>${nextStep?`<div class="flow-summary-recommendation"><span>Recommendation</span><strong>${esc(nextStepLabel)}</strong></div>`:''}<p>${esc(reason)}</p></section><div class="flow-meta"><div><strong>${f.width??f.direct_call_count??0}</strong><br><span>Width (direct calls)</span></div><div><strong>${f.scope??f.scope_asset_count??f.downstream_count??0}</strong><br><span>Scope (runtime assets)</span></div><div><strong>${f.max_depth}</strong><br><span>${longThreshold===null?'Max depth':'Too many steps threshold >= '+longThreshold}</span></div><div><strong>${f.architecture_violation_count}</strong><br><span>Broken rules</span></div><div><strong>${mergeCandidateCount(f)}</strong><br><span>Maybe combine</span></div><div title="Number of \`.py\` source files included in the generated documentation scope."><strong>${(f.source_python_files||f.modules_touched||[]).length}</strong><br><span>Source Python files</span></div><div><strong>${f.external_dependents_count||0}</strong><br><span>External/shared impact</span></div></div><section class="flow-key-signals"><h3>Key signals</h3><div>${signals}</div><p>${isGraphReviewCandidate(f)?esc('This callable exceeds a graph width or depth threshold. Review whether nested helpers should stay separate, be shared, or be simplified.'):flowSignals(f).length?'Informational signals only.':'No review flags detected.'}</p></section>${nextStep?`<section class="flow-next-step"><h3>Next step</h3><p>${esc(nextStep)}</p></section>`:''}<h3>Function call graph tree</h3><div id="callableFlowTree" class="flow-tree"><ul>${renderTreeNode(tree)}</ul></div>`}function selectedItem(){const byQn=new Map(publicEntryFlows.map(r=>[r.qualified_name,r]));return state.selectedFlow?byQn.get(state.selectedFlow):null}function selectedItems(){const item=selectedItem();return item?[item]:[]}function selectedFlowName(){const item=selectedItem();return item?item.function_name:'none'}function publicCallableFindingRows(flow){const findings=architectureFindingRows(flow),longThreshold=longCallChainThreshold(),largeThreshold=largeDependencySurfaceThreshold(),rows=[...(flow.architecture_violation_count?[{finding:'Broken rules found',evidence:`${flow.architecture_violation_count} call edge(s) go in the wrong direction.`,next_step:'Inspect the exact edges below.'}]:[]),...((longThreshold!==null&&(flow.max_depth||0)>=longThreshold)?[{finding:'Too many steps',evidence:`Depth ${flow.max_depth}, threshold >= ${longThreshold}`,next_step:'Inspect whether the flow can be simplified.'}]:[]),...((largeThreshold!==null&&(flow.width||0)>largeThreshold)?[{finding:'Too many helpers',evidence:`Width ${flow.width??flow.direct_call_count??0} direct call(s), threshold > ${largeThreshold}`,next_step:'This public callable has many direct calls. Refactor carefully.'}]:[]),...((flow.external_dependents_count||0)>0?[{finding:'Shared helper',evidence:`${flow.external_dependents_count} function(s) in this graph are used outside this graph.`,next_step:'Inspect outside dependents before refactoring shared helpers.'}]:[]),...((flow.helper_cleanup_candidates||0)>0?[{finding:'Maybe combine inside flow',evidence:mergeCandidateCount(flow)===1?'1 helper function is marked Maybe combine.':`${mergeCandidateCount(flow)} helper functions are marked Maybe combine.`,next_step:'Review helper readability without changing the public API.'}]:[])];return rows.length?rows:[{finding:'Healthy',evidence:'Clear',next_step:''}]}function findingRows(f){return architectureFindingRows(f).map(v=>({source_function:(inventoryByQn.get(v.parent_qualified_name)||{}).function_name||v.parent_qualified_name,source_type:(inventoryByQn.get(v.parent_qualified_name)||{}).simple_classification||v.caller_type||'Unknown',target_function:v.function_name,target_type:v.simple_classification||'Unknown',finding_type:v.violation_type||findingLabel(v.recommended_action||'Broken rule'),suggested_fix:v.violation_type==='Cross-file private dependency'?'Move the private helper into the caller file or expose an architecture-visible helper.':INTERNAL_LAYERING_SUGGESTED_FIX,source_link:linkMetadata(inventoryByQn.get(v.parent_qualified_name)||{qualified_name:v.parent_qualified_name}),target_link:linkMetadata(v)}))}function cleanupRows(f){return (f.transitive_callees||[]).filter(c=>c.helper_cleanup_candidate).map(c=>({function:c.function_name,function_type:c.simple_classification||c.layer_group,called_by:(inventoryByQn.get(c.parent_qualified_name)||{}).function_name||c.parent_qualified_name,finding:findingLabel(c.recommended_action||'Maybe combine'),next_step:(c.recommended_action||'').includes('Shared')?'Keep as shared internal helper.':(c.recommended_action||'').includes('Used several')?'Keep when repeated use improves readability.':(c.recommended_action||'').includes('Recursive')?'Keep recursive helpers separate unless a careful redesign is planned.':'Review whether merging this helper into its only caller improves readability.',link:linkMetadata(c),called_by_link:linkMetadata(inventoryByQn.get(c.parent_qualified_name)||{qualified_name:c.parent_qualified_name})}))}function serializeTree(n){return {...linkMetadata(n),qualified_name:n.qualified_name,function_name:n.function_name,module:n.module,function_type:n.function_type||n.layer_group||'Public function',classification:n.simple_classification||'Unknown',source_path:n.source_path||null,called_inside_flow_by:n.called_inside_flow_by||0,calls_inside_flow:n.calls_inside_flow||0,used_outside_flow:n.used_outside_flow||0,is_end_node:Boolean(n.is_end_node),review_for_merge:Boolean(n.helper_cleanup_candidate),layer:n.layer||null,layer_group:n.layer_group||n.function_type||'Public function',helper_tags:[...(n.architecture_result==='Violation'&&n.violation_type?[`Broken rule: ${n.violation_type}`]:[])],children:(n.children||[]).map(serializeTree)}}function exportItem(f){const tree=buildFlowTree(f),row=inventoryByQn.get(f.qualified_name)||f,cleanup=cleanupRows(f),publicFindings=publicCallableFindingRows(f),architectureFindings=findingRows(f),health=flowHealth(f,architectureFindingRows(f),cleanup),nextStep=flowNextStep(f,architectureFindingRows(f),cleanup);return{selected_public_callable_name:f.function_name,qualified_name:f.qualified_name,source_file:row.source_path||null,source_url:row.source_url||null,recommendation:suggestedActionLabel(f),overall_health:health,next_step:nextStep,key_signals:(f.warnings||[]).map(findingLabel),downstream_count:f.downstream_count,max_depth:f.max_depth,architecture_violation_count:f.architecture_violation_count||0,review_for_merge_count:f.helper_cleanup_candidates||cleanup.length,modules_touched:f.modules_touched||[],external_shared_impact_count:f.external_dependents_count||0,direct_callees:f.direct_callees||[],transitive_callees:f.transitive_callees||[],architecture_findings:architectureFindings,review_for_merge_helpers:cleanup,public_callable_findings:publicFindings,flow_tree:serializeTree(tree),flow_context:{direct_callees:f.direct_callees||[],transitive_callees:f.transitive_callees||[],flow_tree:serializeTree(tree)},...linkMetadata(f)}}function compatibilityModeMeta(){const mode=$('compatibilityMode')?$('compatibilityMode').value:'preserve_backwards_compatibility';return COMPATIBILITY_MODES[mode]||COMPATIBILITY_MODES.preserve_backwards_compatibility}function cleanupMode(){const mode=$('compatibilityMode')?$('compatibilityMode').value:'preserve_backwards_compatibility';const meta=compatibilityModeMeta();return{compatibility_mode:mode,compatibility_mode_label:meta.label,compatibility_instruction:meta.promptInstruction}}function updateCompatibilityModeMeta(){const el=$('compatibilityModeSubtitle');if(!el)return;const meta=compatibilityModeMeta();el.textContent=meta.subtitle;el.className=`compat-mode-subtitle ${meta.className}`}function cleanupPrompt(){const meta=compatibilityModeMeta();return `You are reviewing a FabricOps function call graph cleanup packet.

Use the selected public function and its function call graph context to plan a safe cleanup. Group items by cleanup type, explain the rationale, identify risks, and propose an ordered implementation plan. Do not write code yet.

Compatibility mode:
${meta.label}

Compatibility instruction:
${meta.promptInstruction}

If compatibility mode is “Preserve backwards compatibility”, preserve existing public callable behavior, public names, public signatures, exported packet schema, and user-facing behavior. Helper boundaries, private functions, classes, and implementation details may be cleaned up only when external behavior is preserved. Clearly call out any migration risks.

If compatibility mode is “Allow breaking changes”, propose cleaner breaking changes where they improve the architecture. Clearly label each breaking change, explain why it is worth doing, identify migration impact, and propose a migration path.

Always call out tests required before changes.`}function refactorPacket(){const item=selectedItem(),selected=item?exportItem(item):null;return{schema:'fabricops_public_callable_flow_cleanup_packet',export_type:'Public callable cleanup packet',ai_prompt:cleanupPrompt(),selected_public_callable:selected,selected_flow:selected?selected.flow_tree:null,flow_context:selected?{...selected.flow_context,...cleanupMode()}:cleanupMode(),health:selected?selected.overall_health:null,key_signals:selected?selected.key_signals:[],next_step:selected?selected.next_step:null,architecture_findings:selected?selected.architecture_findings:[],merge_candidates:selected?selected.merge_candidates:[],public_callable_findings:selected?selected.public_callable_findings:[],direct_callees:selected?selected.direct_callees:[],transitive_callees:selected?selected.transitive_callees:[],requested_work:['Inspect the selected public function and its function call graph.','Identify whether the recommended action is safe.','Resolve true cross-file private dependency violations first.','For same-file private dependencies, treat as warning only.','Merge or inline helpers only when readability improves.','Preserve notebook-facing behavior.','Update tests where behavior could be affected.','Return summary, changed functions, tests, risks, and skipped items.'],safety_constraints:['Preserve public callable behavior and external API compatibility.','Do not casually change public function signatures.','Same-file private dependency is warning only.','Cross-file private dependency is an architecture violation.'],expected_output:'Return summary, changed functions, tests, risks, and skipped items.'}}function yamlScalar(v){if(v===null||v===undefined)return 'null';if(typeof v==='number'||typeof v==='boolean')return String(v);const value=String(v);return /^[A-Za-z0-9_./:@ -]+$/.test(value)&&value.trim()===value&&value!==''?value:JSON.stringify(value)}function yamlValue(value,indent=0){const pad='  '.repeat(indent);if(Array.isArray(value)){if(!value.length)return '[]';return value.map(item=>{if(item&&typeof item==='object')return `${pad}-\n${yamlValue(item,indent+1)}`;return `${pad}- ${yamlScalar(item)}`}).join('\n')}if(value&&typeof value==='object'){const entries=Object.entries(value);if(!entries.length)return '{}';return entries.map(([key,item])=>{if(item&&typeof item==='object'){const rendered=yamlValue(item,indent+1);return `${pad}${key}:\n${rendered}`}return `${pad}${key}: ${yamlScalar(item)}`}).join('\n')}return `${pad}${yamlScalar(value)}`}function yamlPacket(packet){return yamlValue(packet)+'\n'}function cleanupPacketTimestamp(){const now=new Date(),pad=value=>String(value).padStart(2,'0');return `${now.getFullYear()}${pad(now.getMonth()+1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`}function buildCleanupPacketFilename(selectedFunctionName,extension){const safeName=text(selectedFunctionName||'none').replace(/[^A-Za-z0-9_.-]/g,'_');return `fabricops-function-call-graph-cleanup-packet__${safeName}__${cleanupPacketTimestamp()}.${extension}`}function downloadPacket(format){const isYaml=format==='yaml';const blob=new Blob([isYaml?yamlPacket(refactorPacket()):JSON.stringify(refactorPacket(),null,2)],{type:isYaml?'application/x-yaml':'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=buildCleanupPacketFilename(selectedFlowName(),isYaml?'yaml':'json');a.click()}function updateExportControls(){const item=selectedItem();['downloadJson','downloadYaml'].forEach(id=>$(id).disabled=!item)}$('showAllPublicCallables').onclick=showAllPublicCallables;$('collapsePublicList').onclick=collapsePublicList;$('downloadJson').onclick=()=>downloadPacket('json');$('downloadYaml').onclick=()=>downloadPacket('yaml');document.addEventListener('click',e=>{const summaryToggle=e.target.closest('[data-summary-toggle]');if(summaryToggle){state.openSummaryFlow=state.openSummaryFlow===summaryToggle.dataset.summaryToggle?'':summaryToggle.dataset.summaryToggle;renderPublicCallableList();return}if(e.target.closest('a,button,input,select,textarea,label,summary,.review-note'))return;const row=e.target.closest('[data-public-flow-row]');if(row){state.activePublicFlow=row.dataset.publicFlowRow;state.selectedFlow=row.dataset.publicFlowRow;state.collapsedPublicList=true;renderPublicCallableList();$('publicFlowDetails').scrollIntoView({behavior:'smooth',block:'start'})}});document.addEventListener('keydown',e=>{const row=e.target.closest('[data-public-flow-row]');if(row&&(e.key==='Enter'||e.key===' ')){e.preventDefault();state.activePublicFlow=row.dataset.publicFlowRow;state.selectedFlow=row.dataset.publicFlowRow;state.collapsedPublicList=true;renderPublicCallableList();$('publicFlowDetails').scrollIntoView({behavior:'smooth',block:'start'})}});$('publicSearchBox').addEventListener('input',e=>{state.publicSearch=e.target.value;state.collapsedPublicList=false;renderPublicCallableList()});$('resetPublicFilters').onclick=()=>{Object.assign(state,{publicSearch:'',sortKey:'callable',sortDirection:'asc',collapsedPublicList:false});$('publicSearchBox').value='';if(window.FabricOpsTableControls)window.FabricOpsTableControls.resetAll(document);renderPublicCallableList()};$('compatibilityMode').addEventListener('change',updateCompatibilityModeMeta);updateCompatibilityModeMeta();async function loadData(){const attemptedUrl=functionCallGraphDataUrl();updateFunctionCallGraphDataLink(attemptedUrl);try{const response=await fetch(attemptedUrl);if(!response.ok)throw new Error(`HTTP ${response.status} ${response.statusText}`);const data=await response.json();inventory=data.function_inventory||[];inventoryByQn=new Map(inventory.map(row=>[row.qualified_name,row]));publicEntryFlows=data.public_flows||data.public_entrypoint_flow||[];summaryCounts=data.summary_counts||{};architectureThresholds=data.architecture_thresholds||architectureThresholds;renderCards();renderPublicCallableList()}catch(error){const status=error&&error.message&&error.message.startsWith('HTTP ')?error.message:'Network/parse error';renderLoadStatus(`Failed to load function call graph data. Attempted URL: ${attemptedUrl}. HTTP status: ${status}. Error message: ${error&&error.message?error.message:String(error)}`,true)}}loadData();
</script><script src="../javascripts/table-controls.js"></script></body></html>
""".replace("<!--CALLABLE_GENERATION_BANNER-->", generation_banner).replace("<!--CALLABLE_PAGE_SHELL_CSS-->", _callable_page_shell_css()).replace("<!--CALLABLE_PAGE_NAV-->", _render_callable_page_nav("architecture"))

def _render_runtime_inventory_source_html(flow_data: dict[str, Any]) -> str:
    """Render runtime inventory markup used by the combined dashboard."""
    generation_banner = _render_callable_generation_banner(flow_data)
    return r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Function Inventory</title><link rel="stylesheet" href="../stylesheets/table-controls.css"><style><!--CALLABLE_PAGE_SHELL_CSS-->.surface-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.55rem;margin:.75rem 0}.surface-card,.toolbar-card{background:#fff;border:1px solid #dbe3ef;border-radius:.75rem;padding:.65rem}.surface-card strong{display:block;margin-bottom:.25rem;line-height:1;font-size:1.45rem}.surface-card span{display:block;line-height:1.2;font-weight:700}.surface-card small{display:block;margin-top:.3rem;line-height:1.25;color:#64748b}.surface-card.info{border-color:#bfdbfe;background:#eff6ff}.surface-card.primary{border-color:#c7d2fe;background:#eef2ff}.surface-card.review{border-color:#fde68a;background:#fffbeb}.surface-card.risk{border-color:#fecaca;background:#fef2f2}.surface-card.muted{background:#f1f5f9;color:#475569}.surface-card.info strong,.surface-card.primary strong{color:#1d4ed8}.surface-card.review strong{color:#92400e}.surface-card.risk strong{color:#991b1b}.inventory-filter-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:.55rem;margin:.75rem 0}.inventory-note{background:#eff6ff;border-color:#bfdbfe}.scope-banner{margin:.75rem 0}.inventory-clear-all{border:1px solid #cbd5e1;border-radius:.45rem;background:#fff;color:#1d4ed8;font-weight:800}.filter-field{display:flex;flex-direction:column;font-weight:700;font-size:.82rem}input,select,button{padding:.42rem .5rem;border:1px solid #dbe3ef;border-radius:.45rem;background:#fff}.export-toolbar{display:flex;flex-direction:column;gap:.65rem;align-items:stretch;box-sizing:border-box;max-width:100%;margin:.75rem 0}.toolbar-card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,18rem),1fr));gap:.65rem}.toolbar-card{box-sizing:border-box;min-width:0;background:#f1f5f9}.toolbar-card--selection,.toolbar-card--prompt{display:flex;flex-direction:column;gap:.55rem}.toolbar-row{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;max-width:100%;min-width:0}.toolbar-field{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center;max-width:100%;min-width:0;font-weight:700}.toolbar-field select{max-width:100%;min-width:0}.toolbar-help,.group-help{color:#475569;font-weight:400}.compat-mode-subtitle{margin-top:.35rem;font-size:.85rem;line-height:1.35}.compat-mode-safe{color:#1d4ed8}.compat-mode-review{color:#b45309}.compat-mode-breaking{color:#b91c1c}.toolbar-group{display:flex;flex-wrap:wrap;gap:.5rem 1rem;align-items:center;max-width:100%;min-width:0}.toolbar-group>div{min-width:0}.toolbar-group .toolbar-row{flex:1 1 16rem}.toolbar-row button{white-space:normal}.primary-action,.danger-action:not(:disabled){background:#1d4ed8;color:#fff;border-color:#1d4ed8}.danger-action:not(:disabled){background:#b91c1c;border-color:#b91c1c}button:disabled,.danger-action:disabled{background:#e5e7eb;color:#94a3b8;border-color:#cbd5e1;cursor:not-allowed}.table-wrap{max-width:100%;overflow-x:auto;overflow-y:visible;background:#fff;border:1px solid #dbe3ef;border-radius:.75rem;-webkit-overflow-scrolling:touch}.callable-review-table-wrap{max-width:100%;overflow-x:auto}.callable-review-table{width:100%;table-layout:auto;border-collapse:collapse}.callable-review-table th,.callable-review-table td{padding:.42rem .45rem;border-bottom:1px solid #dbe3ef;text-align:left;font-size:.84rem;vertical-align:top}.callable-review-table tr[data-inventory-row]{cursor:pointer}.callable-review-table tr.selected{outline:2px solid #1d4ed8;outline-offset:-2px;background:#eff6ff;box-shadow:inset .25rem 0 #1d4ed8}.callable-review-table tr.scope-highlight{outline:2px solid #15803d;outline-offset:-2px;background:#f0fdf4;box-shadow:inset .25rem 0 #15803d}.callable-review-table tr[data-inventory-row]:focus{outline:3px solid #2563eb;outline-offset:-3px}.callable-review-table .col-callable{min-width:18rem;white-space:nowrap}.callable-review-table .col-file-area{min-width:18rem;white-space:nowrap}.callable-review-table .col-item-type,.callable-review-table .col-flow,.callable-review-table .col-health{white-space:nowrap}.callable-review-table .col-usage-scope{min-width:11rem;white-space:nowrap}.callable-review-table .col-recommended-action{min-width:13rem;white-space:nowrap}.callable-review-table .col-details{width:90px;min-width:90px;white-space:nowrap}.callable-review-table .col-details .details-toggle{white-space:nowrap;word-break:keep-all;overflow-wrap:normal}.inventory-row.is-expanded td{border-bottom:0}.details-row{display:none}.details-row.is-open{display:table-row}.details-row td{padding:.75rem 1rem 1rem;background:#f8fbff;border-top:0;border-bottom:1px solid #d8e4f5}.details-panel{max-width:100%;padding:.85rem 1rem;border:1px solid #d8e4f5;border-radius:.5rem;background:#fff;line-height:1.45;white-space:normal;overflow-wrap:anywhere}.details-panel p{margin:.35rem 0}.details-panel a{overflow-wrap:anywhere;word-break:break-word}.details-toggle{font-weight:800;color:#1d4ed8;white-space:nowrap;word-break:keep-all;overflow-wrap:normal}.tag,.badge{display:inline-flex;align-items:center;margin:.06rem;padding:.12rem .42rem;border-radius:999px;background:#e0e7ff;color:#3730a3;font-size:.69rem;font-weight:800;line-height:1.2}.badge.issue{background:#fee2e2;color:#991b1b}.badge.warn{background:#fef3c7;color:#92400e}.badge.keep{background:#dcfce7;color:#166534}.badge.muted{background:#e2e8f0;color:#475569}.badge.info{background:#dbeafe;color:#1e40af}@media(max-width:720px){.inventory-filter-grid,.toolbar-card-grid{grid-template-columns:1fr}.toolbar-row,.toolbar-group{align-items:stretch}.toolbar-field,.toolbar-group{flex-direction:column}.toolbar-field select{width:100%}.toolbar-help{display:block}.toolbar-group .toolbar-row{flex:1 1 auto;flex-direction:row}.toolbar-group .toolbar-row button{flex:1 1 9rem}.callable-review-table{min-width:900px}}</style></head><body><header><h1>Function Inventory</h1><p>The Function Inventory focuses on function-level code assets, including public callables, shared helpers, private helpers, and cleanup candidates.</p><!--CALLABLE_GENERATION_BANNER--><!--CALLABLE_PAGE_NAV--></header><main><section id="inventorySummaryCards" class="surface-cards" aria-label="Function inventory summary"></section><p><small>Helper suggestions are review hints, not automatic judgments. A helper used by one function can still be useful if it makes the code easier to read, avoids repeated code, is used several times inside that function, or calls itself recursively.</small></p><p><small>The Function Inventory focuses on function-level code assets, including public callables, shared helpers, private helpers, and cleanup candidates.</small></p><section class="toolbar-card inventory-note" aria-label="Function inventory note"><strong>Function Inventory</strong><p>Use this inventory to inspect function-level code assets, including public callables, shared helpers, private helpers, and cleanup candidates.</p></section><section id="scopeBanner" class="toolbar-card inventory-note scope-banner" aria-label="Selected runtime inventory scope"><strong>Current scope: <span id="scopeBannerName">All runtime assets</span></strong><p id="scopeBannerHelp">Showing all runtime inventory assets.</p></section><section class="inventory-filter-grid" aria-label="Function inventory filters"><label class="filter-field">Search function inventory <input id="searchBox" type="search"></label><label class="filter-field">Function inventory focus <select id="focusFilter"><option value="actionable" selected>Suggested cleanup</option><option value="all">All code assets</option><option value="selected">Selected</option></select></label><label class="filter-field">Item type <select id="typeFilter"><option value="all">All item types</option><option value="public">Public callables</option><option value="class">Classes</option><option value="internal">Shared helpers</option><option value="private_helper">Private helpers</option></select></label><label class="filter-field">Reachability <select id="reachabilityFilter"><option value="all">All reachability states</option><option value="reachable_from_public_runtime">Reachable from public runtime</option><option value="unreachable_runtime_asset">Cannot trace back to a public function</option></select></label><label class="filter-field">Health <select id="healthFilter"><option value="all">All health states</option><option value="Broken rule">Broken rule</option><option value="Warning">Warning</option><option value="Healthy">Healthy</option></select></label><label class="filter-field">Recommended action <select id="actionFilter"><option value="all">All recommended actions</option><option value="Fix architecture boundary">Fix architecture boundary</option><option value="Promote to shared utility">Promote to shared utility</option><option value="Maybe combine">Maybe combine</option><option value="Refactor helper">Refactor helper</option><option value="Rename shared helper">Rename shared helper</option><option value="Keep private helper">Keep private helper</option><option value="Next step">Next step</option><option value="Verify possible orphan">Verify possible orphan</option><option value="No action">No action</option><option value="Warning">Warning</option></select></label><button id="resetFilters" class="inventory-clear-all" type="button" hidden>Clear table filters</button><button id="showAllRuntimeAssets" class="inventory-clear-all" type="button">Show all runtime assets</button></section><section class="export-toolbar"><div class="toolbar-card-grid"><div class="toolbar-card toolbar-card--selection" aria-label="Selection"><strong id="selectedCount">Selected function-level code assets: 0</strong><div class="toolbar-row"><button id="selectVisible" class="primary-action" type="button">Select visible</button><button id="clearSelected" class="danger-action" type="button" disabled>Clear selection</button></div></div><div class="toolbar-card toolbar-card--compatibility"><label class="toolbar-field">Compatibility mode <select id="compatibilityMode"><option value="preserve_backwards_compatibility" selected>Preserve backwards compatibility</option><option value="allow_breaking_changes">Allow breaking changes</option></select></label><small id="compatibilityModeSubtitle" class="compat-mode-subtitle compat-mode-safe">Selected cleanup should preserve existing public callable behavior and avoid breaking current users.</small></div><div class="toolbar-card toolbar-card--prompt"><div class="toolbar-group"><div><strong>Export function inventory cleanup packet</strong><br><small class="group-help">Select runtime inventory rows first, then export selected rows with call graph context.</small></div><div class="toolbar-row"><button id="downloadJson" type="button" disabled>Download JSON</button><button id="downloadYaml" type="button" disabled>Download YAML</button></div></div><small id="exportStatus"></small></div></section><p id="resultCount"></p><p id="dataLoadStatus" class="load-status" aria-live="polite">Loading function call graph data...</p><section class="table-wrap callable-review-table-wrap"><table class="callable-review-table" data-table-controls="excel"><thead><tr><th class="col-file-area">Source file</th><th class="col-callable">Item name</th><th class="col-item-type">Item type</th><th class="col-usage-scope">Usage scope</th><th class="col-health">Health</th><th class="col-recommended-action">Recommended action</th><th class="col-details">Details</th></tr></thead><tbody id="inventoryBody"></tbody></table></section></main><script>
const CANNOT_TRACE_HELP='The scanner could not trace this asset back to a public FabricOps function. This is not proof that the asset is unused or safe to '+'delete.';const DISPLAY_LABEL_MAP={'None':'Healthy','Broken rule':'Broken rule','Too many steps':'Too many steps','Too many helpers':'Too many helpers','Maybe combine':'Maybe combine','Used by one function':'Used by one function','Used several times in one function':'Used several times in one function','Recursive helper':'Recursive helper','Heavily used helper':'Heavily used helper','Shared utility':'Shared utility','Same-file private dependency':'Same-file private dependency'};const COMPATIBILITY_MODES={preserve_backwards_compatibility:{label:'Preserve backwards compatibility',subtitle:'Selected cleanup should preserve existing public callable behavior and avoid breaking current users.',promptInstruction:'Preserve existing public callable behavior, public names, public signatures, exported packet schema, and user-facing behavior. Helper boundaries, private functions, classes, and implementation details may be cleaned up only when external behavior is preserved. Clearly call out any migration risks.',className:'compat-mode-safe'},allow_breaking_changes:{label:'Allow breaking changes',subtitle:'Selected cleanup may propose cleaner breaking changes when they improve the callable architecture.',promptInstruction:'Propose cleaner breaking changes where they improve architecture, naming, boundaries, maintainability, or long-term usability. Clearly label each breaking change, explain why it is worth doing, identify migration impact, and propose a migration path.',className:'compat-mode-breaking'}};let inventory=[],visibleRows=[],summaryCounts={},publicFlowQns=new Set(),flowSignalsByQn=new Map(),flowAssetsByQn=new Map(),flowByQn=new Map(),inventoryDataMissing=false,currentScope={kind:'all',label:'All runtime assets',qualified_name:''};const state={search:'',focusFilter:'all',typeFilter:'all',reachabilityFilter:'all',healthFilter:'all',actionFilter:'all',selected:new Set(),expanded:new Set()};const $=id=>document.getElementById(id),text=v=>String(v??''),esc=v=>text(v).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));function displayLabel(v){return DISPLAY_LABEL_MAP[text(v)]||text(v)}function isPublicCallable(r){return r.layer==='public'||r.function_type==='Public function'}function inCallableFlow(r){return publicFlowQns.has(r.qualified_name)}function rowReachability(r){return r.reachability||((publicFlowQns.has(r.qualified_name)||r.layer==='public')?'reachable_from_public_runtime':'unreachable_runtime_asset')}function reachabilityLabel(r){return rowReachability(r)==='unreachable_runtime_asset'?'Cannot trace back to a public function':'Reachable from public runtime'}function rowInSelectedScope(r){if(currentScope.kind==='all')return true;if(currentScope.kind==='unreachable')return rowReachability(r)==='unreachable_runtime_asset';if(currentScope.kind==='public_callable')return (flowAssetsByQn.get(currentScope.qualified_name)||new Set()).has(r.qualified_name);return true}function fileArea(r){return r.owner_file||r.source_path||r.docs_path||r.module||''}const ITEM_TYPE_LABELS={public:'Public callable',class:'Classes',internal:'Shared helper',private_helper:'Private helper'};function itemTypeKey(r){if(r.layer&&ITEM_TYPE_LABELS[r.layer])return r.layer;if(isPublicCallable(r))return 'public';if(r.function_type==='Private helper')return 'private_helper';if(r.function_type==='Shared helper')return 'internal';return 'private_helper'}function itemType(r){return ITEM_TYPE_LABELS[itemTypeKey(r)]||'Private helper'}function flowSignal(r){return flowSignalsByQn.get(r.qualified_name)||{violation:false,warning:false,types:[]}}function duplicateHelperEvidence(r){const values=[r.recommended_action,r.review_status,r.priority,r.violation_type,...(r.signals||[]),...(r.tags||[]),...(r.warnings||[])].map(v=>text(v).toLowerCase());return values.some(v=>/(duplicate|similar helper|repeated helper|promote|extract|shared utility|shared helper)/.test(v))}function usageScope(r){return reachabilityLabel(r)}function timesUsedLabel(count){const value=Number(count);if(value===1)return 'Used once';if(value>1)return 'Used several times';return 'unknown'}const ACTIONABLE_ACTIONS=new Set(['Fix architecture boundary','Promote to shared utility','Maybe combine','Refactor helper','Rename shared helper','Next step','Verify possible orphan','Warning']);function actionDetails(r){const signal=flowSignal(r),type=itemType(r),scope=usageScope(r),raw=displayLabel(r.recommended_action||''),rawText=[raw,...(r.signals||[]),...(r.tags||[]),...(r.warnings||[])].map(v=>text(v).toLowerCase()).join(' ');let finding='None',reason='No cleanup action is needed.',evidence='',notes='',cleanup='No action';if(signal.violation){finding='Architecture boundary violation';reason='Private implementation crosses a callable file or module boundary.';evidence=`${sourceHref(r)||fileArea(r)} is referenced outside its owning callable boundary.`;cleanup='Fix architecture boundary'}else if(duplicateHelperEvidence(r)){finding='Duplicate helper logic across callable files';reason='Similar helper logic appears in multiple callable files and may deserve extraction into an intentional shared utility.';evidence=raw||text((r.signals||[]).join('; '))||'Duplicate or promotion-oriented helper signal found.';cleanup='Promote to shared utility'}else if(raw==='Maybe combine'){finding='Maybe combine';reason='This helper is used by one function, and that function uses it once. Review whether keeping it separate makes the code easier to read.';evidence=`Times used: ${timesUsedLabel(r.call_site_count)}.`;cleanup='Maybe combine'}else if(raw==='Used several times in one function'){finding='Used several times in one function';reason='This helper is used by one function, but that function uses it more than once. This is usually a reason to keep it, or at least review carefully.';evidence=`Times used: ${timesUsedLabel(r.call_site_count)}.`;cleanup='Next step'}else if(raw==='Recursive helper'){finding='Recursive helper';reason='Helper calls itself and should not be treated as a simple merge or inline case.';cleanup='Next step'}else if(raw==='Used by one function'){finding='Used by one function';reason='This helper is used by one function. This is a review hint, not an automatic cleanup judgment.';evidence=`Times used: ${timesUsedLabel(r.call_site_count)}.`;cleanup='Next step'}else if(raw==='Heavily used helper'){finding='Heavily used helper';reason='Helper has many distinct callers; protect it and change carefully.';cleanup='No action'}else if(signal.warning){finding=signal.types.map(displayLabel).join(', ')||'Warning';reason='This record needs manual review before cleanup.';cleanup='Warning'}else if(/refactor|large|unclear|split|responsibility/.test(rawText)&&type==='Private helper'){finding='Private helper cleanup';reason='Helper appears large, unclear, or internally mixed and may need same-file cleanup.';cleanup='Refactor helper'}else if(raw&&/Rename/.test(raw)){finding='Naming review';reason='Name may be unclear for its current responsibility.';cleanup='Rename shared helper'}else if(rowReachability(r)==='unreachable_runtime_asset'||raw&&/Remove|Orphan/.test(raw)){finding='Potential orphan';reason=CANNOT_TRACE_HELP;cleanup='Verify possible orphan'}else if(raw&&/Review/.test(raw)){finding='Manual review';reason='Explicit evidence indicates a human should review this record.';cleanup='Next step'}else if(type==='Private helper'&&scope==='Used by owning callable'){finding='Owning callable private helper';reason='Private helper is used by its owning public callable file.';cleanup='Keep private helper'}notes=(r.signals||[]).map(displayLabel).join('; ');return{finding,reason,evidence,notes,cleanup_action:cleanup}}function recommendedAction(r){const details=actionDetails(r);return details.cleanup_action||'No action'}function isActionable(r){return ACTIONABLE_ACTIONS.has(recommendedAction(r))}function healthLabel(r){const action=recommendedAction(r);if(action==='Fix architecture boundary')return 'Broken rule';if(action==='Warning'||action==='Next step')return 'Warning';return 'Healthy'}function healthClass(h){return h==='Broken rule'?'issue':h==='Warning'?'warn':h==='Out of scope'?'muted':'keep'}function healthBadge(i){const health=healthLabel(i);return `<span class="badge ${healthClass(health)}">${esc(health)}</span>`}function actionBadge(i){const action=recommendedAction(i);return `<span class="badge ${ACTIONABLE_ACTIONS.has(action)?'warn':'keep'}">${esc(action)}</span>`}function usageBadge(i){const scope=reachabilityLabel(i);return `<span class="badge ${rowReachability(i)==='unreachable_runtime_asset'?'warn':'info'}">${esc(scope)}</span>`}function evidenceMarkup(value){const evidence=text(value||'None'),match=evidence.match(/https?:\/\/\S+/);if(match){const before=evidence.slice(0,match.index),after=evidence.slice(match.index+match[0].length);return `${esc(before)}<a href="${esc(match[0])}" target="_blank" rel="noopener">${esc(match[0])}</a>${esc(after)}`}return esc(evidence)}function detailsButton(i){const open=state.expanded.has(i.qualified_name);return `<button class="details-toggle" type="button" aria-expanded="${open?'true':'false'}" data-details-toggle="${esc(i.qualified_name)}">Details</button>`}function detailsRow(i){const d=actionDetails(i),open=state.expanded.has(i.qualified_name),notes=d.notes?`<p><strong>Notes:</strong> ${esc(d.notes)}</p>`:'',cleanup=d.cleanup_action?`<p><strong>Cleanup action:</strong> ${esc(d.cleanup_action)}</p>`:'';return `<tr class="details-row ${open?'is-open':''}" data-details-row="${esc(i.qualified_name)}"><td colspan="7"><div class="details-panel"><p><strong>Finding:</strong> ${esc(d.finding)}</p><p><strong>Reason:</strong> ${esc(d.reason)}</p><p><strong>Evidence:</strong> ${evidenceMarkup(d.evidence)}</p>${notes}${cleanup}</div></td></tr>`}function sourceHref(i){if(i.docs_path)return '../'+String(i.docs_path).replace(/^docs\//,'').replace(/\.md$/,'/');if(i.source_url)return i.source_url;const path=i.source_path;if(!path)return '';const start=i.source_start_line,end=i.source_end_line;let anchor=start?`#L${start}`:'';if(start&&end&&end!==start)anchor+=`-L${end}`;return 'https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/'+path+anchor}function sourceCallableLink(i){const href=sourceHref(i),label=esc(i.function_name);return href?`<a class="source-link" href="${esc(href)}" target="_blank" rel="noopener"><code>${label}</code></a>`:`<code>${label}</code>`}function selectedItems(){return inventory.filter(row=>state.selected.has(row.qualified_name))}function compatibilityModeMeta(){const mode=$('compatibilityMode')?$('compatibilityMode').value:'preserve_backwards_compatibility';return COMPATIBILITY_MODES[mode]||COMPATIBILITY_MODES.preserve_backwards_compatibility}function cleanupMode(){const mode=$('compatibilityMode')?$('compatibilityMode').value:'preserve_backwards_compatibility';const meta=compatibilityModeMeta();return{compatibility_mode:mode,compatibility_mode_label:meta.label,compatibility_instruction:meta.promptInstruction}}function updateCompatibilityModeMeta(){const el=$('compatibilityModeSubtitle');if(!el)return;const meta=compatibilityModeMeta();el.textContent=meta.subtitle;el.className=`compat-mode-subtitle ${meta.className}`}function exportItem(r){return{source_file:r.source_path||r.owner_file||fileArea(r),item_name:r.function_name||r.qualified_name,qualified_name:r.qualified_name,item_type:itemType(r),reachability:rowReachability(r),health:healthLabel(r),recommended_action:recommendedAction(r),action_details:actionDetails(r)}}function cleanupPrompt(){const meta=compatibilityModeMeta();return `You are reviewing a FabricOps function inventory cleanup packet.

Use the selected function-level code assets and function call graph context to plan a safe cleanup. Group items by cleanup type, explain the rationale, identify risks, and propose an ordered implementation plan. Do not write code yet.

Compatibility mode:
${meta.label}

Compatibility instruction:
${meta.promptInstruction}

If compatibility mode is “Preserve backwards compatibility”, preserve existing public callable behavior, public names, public signatures, exported packet schema, and user-facing behavior. Helper boundaries, private functions, classes, and implementation details may be cleaned up only when external behavior is preserved. Clearly call out any migration risks.

If compatibility mode is “Allow breaking changes”, propose cleaner breaking changes where they improve the architecture. Clearly label each breaking change, explain why it is worth doing, identify migration impact, and propose a migration path.

Always call out tests required before changes.`}function relatedFlows(){if(currentScope.kind==='public_callable'){const f=flowByQn.get(currentScope.qualified_name);return f?[f]:[]}const selected=new Set(selectedItems().flatMap(row=>[...flowAssetsByQn.entries()].filter(([,assets])=>assets.has(row.qualified_name)).map(([qn])=>qn)));return [...selected].map(qn=>flowByQn.get(qn)).filter(Boolean)}function refactorPacket(){const rows=selectedItems().map(exportItem),flows=relatedFlows();return{schema:'fabricops_runtime_refactor_packet',export_type:'Runtime refactor packet',ai_prompt:cleanupPrompt(),selection_context:{architecture_scope:currentScope,selected_inventory_asset_count:rows.length,...cleanupMode()},compatibility_mode:cleanupMode(),selected_inventory_assets:rows,related_public_flows:flows,related_architecture_findings:flows.flatMap(flow=>flow.architecture_findings||flow.transitive_callees||[]).filter(row=>row.architecture_result==='Violation'||row.recommended_action==='Broken rule'),requested_work:['Inspect the selected runtime inventory rows using the compact schema.','Fix architecture boundaries before cosmetic cleanup.','Keep normal owning-file private helpers private.','Promote duplicate helper logic only when duplication evidence supports a shared utility.','Keep cleanup focused on function-level code assets.'],safety_constraints:['Preserve public callable behavior.','Do not remove assets without caller and test review.','Cross-callable private helper usage is an architecture violation.'],expected_output:'Return summary, changed assets, tests, risks, and deferred items.'}}function yamlScalar(v){if(v===null||v===undefined)return 'null';if(typeof v==='number'||typeof v==='boolean')return String(v);const value=String(v);return /^[A-Za-z0-9_./:@ -]+$/.test(value)&&value.trim()===value&&value!==''?value:JSON.stringify(value)}function yamlValue(value,indent=0){const pad='  '.repeat(indent);if(Array.isArray(value)){if(!value.length)return '[]';return value.map(item=>{if(item&&typeof item==='object')return `${pad}-\n${yamlValue(item,indent+1)}`;return `${pad}- ${yamlScalar(item)}`}).join('\n')}if(value&&typeof value==='object'){const entries=Object.entries(value);if(!entries.length)return '{}';return entries.map(([key,item])=>{if(item&&typeof item==='object'){return `${pad}${key}:\n${yamlValue(item,indent+1)}`}return `${pad}${key}: ${yamlScalar(item)}`}).join('\n')}return `${pad}${yamlScalar(value)}`}function yamlPacket(packet){return yamlValue(packet)+'\n'}function cleanupPacketTimestamp(){const now=new Date(),pad=value=>String(value).padStart(2,'0');return `${now.getFullYear()}${pad(now.getMonth()+1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`}function buildInventoryFilename(functionCount,extension){return `fabricops-runtime-refactor-packet__${functionCount}_assets__${cleanupPacketTimestamp()}.${extension}`}function downloadPacket(format){const isYaml=format==='yaml',packet=refactorPacket();const blob=new Blob([isYaml?yamlPacket(packet):JSON.stringify(packet,null,2)],{type:isYaml?'application/x-yaml':'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=buildInventoryFilename((packet.selected_inventory_assets||[]).length,isYaml?'yaml':'json');a.click()}function scopeHelpText(){if(currentScope.kind==='public_callable')return 'Showing runtime inventory assets in the selected public callable flow.';if(currentScope.kind==='unreachable')return CANNOT_TRACE_HELP;return 'Showing all runtime inventory assets.'}function renderScopeBanner(){const name=$('scopeBannerName'),help=$('scopeBannerHelp');if(name)name.textContent=currentScope.label;if(help)help.textContent=scopeHelpText()}function renderInventoryCards(){renderScopeBanner();const scoped=inventory.filter(rowInSelectedScope),rows=visibleRows.length?visibleRows:scoped,needs=rows.filter(isActionable).length,unreachable=rows.filter(r=>rowReachability(r)==='unreachable_runtime_asset').length,cards=[{label:'Runtime assets',value:rows.length,subtitle:`${currentScope.label} after active filters.`,cls:'muted'},{label:'Needs review',value:needs,subtitle:'Visible assets with review-oriented actions.',cls:needs?'review':'good'},{label:'Cannot trace back to a public function',value:unreachable,subtitle:CANNOT_TRACE_HELP,cls:unreachable?'risk':'good'},{label:'Selected for export',value:state.selected.size,subtitle:'Inventory assets included in the AI refactor packet.',cls:state.selected.size?'primary':'muted'}];$('inventorySummaryCards').innerHTML=cards.map(c=>`<article class="surface-card ${esc(c.cls)}"><strong>${esc(c.value??0)}</strong><span>${esc(c.label)}</span><small>${esc(c.subtitle)}</small></article>`).join('')}function supportFocus(i){return isActionable(i)}function matchesFilters(i){const q=state.search.toLowerCase();if(!rowInSelectedScope(i))return false;if(q&&![i.function_name,i.qualified_name,fileArea(i),itemType(i),reachabilityLabel(i),healthLabel(i),recommendedAction(i)].some(v=>text(v).toLowerCase().includes(q)))return false;if(state.focusFilter==='actionable'&&state.typeFilter==='all'&&!q&&!supportFocus(i))return false;if(state.focusFilter==='selected'&&!state.selected.has(i.qualified_name))return false;if(state.typeFilter!=='all'&&itemTypeKey(i)!==state.typeFilter)return false;if(state.reachabilityFilter!=='all'&&rowReachability(i)!==state.reachabilityFilter)return false;if(state.healthFilter!=='all'&&healthLabel(i)!==state.healthFilter)return false;if(state.actionFilter!=='all'&&recommendedAction(i)!==state.actionFilter)return false;return true}function rank(i){return (isActionable(i)?0:1)+text(recommendedAction(i)).localeCompare('No action')}function filteredRows(){return inventory.filter(matchesFilters).sort((a,b)=>rank(a)-rank(b)||itemType(a).localeCompare(itemType(b))||text(a.function_name).localeCompare(text(b.function_name)))}function updateFilterControls(){$('resetFilters').hidden=state.search===''&&state.focusFilter==='all'&&state.typeFilter==='all'&&state.reachabilityFilter==='all'&&state.healthFilter==='all'&&state.actionFilter==='all'}function updateExportControls(){$('selectedCount').textContent=`Selected function-level code assets: ${state.selected.size}`;['downloadJson','downloadYaml'].forEach(id=>$(id).disabled=state.selected.size===0);$('clearSelected').disabled=state.selected.size===0}function resultCountText(){const total=inventory.filter(rowInSelectedScope).length;return `Showing ${visibleRows.length} runtime inventory records in ${currentScope.label} of ${total} scoped runtime assets.`}function inventoryEmptyMessage(){if(inventoryDataMissing)return 'Runtime inventory data is missing from function-call-graph.json. Regenerate the function call graph export.';if(state.focusFilter==='selected'&&state.selected.size===0)return 'No selected function-level code assets. Clear the Selected focus or select visible rows first.';return 'No function-level code assets found for the current filters.'}function renderLoadStatus(message,isError=false){const el=$('dataLoadStatus');el.textContent=message;el.className=isError?'load-status issue':'load-status'}function renderTable(){visibleRows=filteredRows();renderInventoryCards();$('resultCount').textContent=resultCountText();renderLoadStatus(visibleRows.length?`Loaded ${inventory.length} function inventory records`:inventoryEmptyMessage(),inventoryDataMissing);updateFilterControls();$('inventoryBody').innerHTML=visibleRows.map(i=>`<tr data-inventory-row="${esc(i.qualified_name)}" class="inventory-row ${state.selected.has(i.qualified_name)?'selected':''} ${currentScope.kind==='public_callable'&&i.qualified_name===currentScope.qualified_name?'scope-highlight':''} ${state.expanded.has(i.qualified_name)?'is-expanded':''}" tabindex="0" aria-selected="${state.selected.has(i.qualified_name)?'true':'false'}"><td class="col-file-area">${esc(fileArea(i))}</td><td class="col-callable">${sourceCallableLink(i)}</td><td class="col-item-type">${esc(itemType(i))}</td><td class="col-usage-scope">${usageBadge(i)}</td><td class="col-health">${healthBadge(i)}</td><td class="col-recommended-action">${actionBadge(i)}</td><td class="col-details">${detailsButton(i)}</td></tr>${detailsRow(i)}`).join('');updateExportControls();if(window.FabricOpsTableControls)window.FabricOpsTableControls.enhance(document.querySelector('table[data-table-controls="excel"]'))}function functionCallGraphDataUrl(){const path=window.location.pathname,origin=window.location.origin,referenceMarker='/reference/',assetsMarker='/assets/';if(path.includes(referenceMarker))return origin+path.slice(0,path.indexOf(referenceMarker)+referenceMarker.length)+'_data/function-call-graph.json';if(path.includes(assetsMarker))return origin+path.slice(0,path.indexOf(assetsMarker)+1)+'reference/_data/function-call-graph.json';return new URL('reference/_data/function-call-graph.json',document.baseURI).href}function updateFunctionCallGraphDataLink(url){const link=$('openFunctionCallGraphJson');if(link)link.href=url}function buildFlowSignals(flows){publicFlowQns=new Set();flowSignalsByQn=new Map();flowAssetsByQn=new Map();flowByQn=new Map();(flows||[]).forEach(flow=>{flowByQn.set(flow.qualified_name,flow);const assets=new Set([flow.qualified_name]);publicFlowQns.add(flow.qualified_name);(flow.transitive_callees||[]).forEach(row=>{assets.add(row.qualified_name);publicFlowQns.add(row.qualified_name);const signal=flowSignalsByQn.get(row.qualified_name)||{violation:false,warning:false,types:[]};if(row.architecture_result==='Violation')signal.violation=true;if(row.architecture_result==='Warning')signal.warning=true;if(row.violation_type&&!signal.types.includes(row.violation_type))signal.types.push(row.violation_type);flowSignalsByQn.set(row.qualified_name,signal)});flowAssetsByQn.set(flow.qualified_name,assets)})}function scrollToRuntimeInventory(){const target=document.getElementById('runtime-inventory');if(target)target.scrollIntoView({behavior:'smooth',block:'start'})}function setArchitectureScope(scope,options={}){currentScope=scope;renderTable();const detail=document.getElementById('publicFlowDetails');if(detail&&scope.kind==='all')detail.innerHTML='<h2>Selected public function flow</h2><p>All runtime assets selected. No single public callable flow is shown for this scope.</p>';if(detail&&scope.kind==='unreachable')detail.innerHTML=`<h2>Selected public function flow</h2><p>${CANNOT_TRACE_HELP}</p>`;if(detail&&scope.kind==='public_callable'){state.activePublicFlow=scope.qualified_name;state.selectedFlow=scope.qualified_name;renderFlowDetails();}if(options.scroll!==false)scrollToRuntimeInventory()}$('searchBox').addEventListener('input',e=>{state.search=e.target.value;renderTable()});['focusFilter','typeFilter','reachabilityFilter','healthFilter','actionFilter'].forEach(id=>$(id).addEventListener('change',e=>{state[id]=e.target.value;renderTable()}));$('resetFilters').onclick=()=>{Object.assign(state,{search:'',typeFilter:'all',reachabilityFilter:'all',healthFilter:'all',actionFilter:'all'});$('searchBox').value='';$('typeFilter').value='all';$('reachabilityFilter').value='all';$('healthFilter').value='all';$('actionFilter').value='all';if(window.FabricOpsTableControls)window.FabricOpsTableControls.resetAll(document);renderTable()};$('showAllRuntimeAssets').onclick=()=>setArchitectureScope({kind:'all',label:'All runtime assets',qualified_name:''});document.addEventListener('click',e=>{const toggle=e.target.closest('[data-details-toggle]');if(toggle){const key=toggle.dataset.detailsToggle;state.expanded.has(key)?state.expanded.delete(key):state.expanded.add(key);renderTable();return}if(e.target.closest('a,button,input,select,textarea,label'))return;const row=e.target.closest('[data-inventory-row]');if(row){state.selected.has(row.dataset.inventoryRow)?state.selected.delete(row.dataset.inventoryRow):state.selected.add(row.dataset.inventoryRow);renderTable()}});document.addEventListener('keydown',e=>{const row=e.target.closest('[data-inventory-row]');if(row&&(e.key==='Enter'||e.key===' ')){e.preventDefault();state.selected.has(row.dataset.inventoryRow)?state.selected.delete(row.dataset.inventoryRow):state.selected.add(row.dataset.inventoryRow);renderTable()}});document.addEventListener('click',e=>{const special=e.target.closest('[data-architecture-scope-special]');if(special){const kind=special.dataset.architectureScopeSpecial;if(kind==='all')setArchitectureScope({kind:'all',label:'All runtime assets',qualified_name:''});if(kind==='unreachable')setArchitectureScope({kind:'unreachable',label:'Others / Cannot trace back to a public function',qualified_name:''});return}const row=e.target.closest('[data-public-flow-row]');if(row)setArchitectureScope({kind:'public_callable',label:row.dataset.publicFlowRow,qualified_name:row.dataset.publicFlowRow})});const allScopeButton=document.getElementById('scopeAllRuntimeAssets'),unreachableScopeButton=document.getElementById('scopeUnreachableRuntimeAssets');if(allScopeButton)allScopeButton.onclick=()=>setArchitectureScope({kind:'all',label:'All runtime assets',qualified_name:''});if(unreachableScopeButton)unreachableScopeButton.onclick=()=>setArchitectureScope({kind:'unreachable',label:'Others / Cannot trace back to a public function',qualified_name:''});$('selectVisible').onclick=()=>{visibleRows.forEach(r=>state.selected.add(r.qualified_name));renderTable()};$('clearSelected').onclick=()=>{state.selected.clear();renderTable()};$('downloadJson').onclick=()=>downloadPacket('json');$('downloadYaml').onclick=()=>downloadPacket('yaml');$('compatibilityMode').addEventListener('change',updateCompatibilityModeMeta);updateCompatibilityModeMeta();async function loadData(){const attemptedUrl=functionCallGraphDataUrl();updateFunctionCallGraphDataLink(attemptedUrl);try{const response=await fetch(attemptedUrl);if(!response.ok)throw new Error(`HTTP ${response.status} ${response.statusText}`);let data;try{data=await response.json()}catch(parseError){throw new Error(`Could not parse function-call-graph.json from ${attemptedUrl}: ${parseError&&parseError.message?parseError.message:String(parseError)}`)}if(!Array.isArray(data.function_inventory)){inventory=[];summaryCounts=data&&data.summary_counts?data.summary_counts:{};inventoryDataMissing=true;buildFlowSignals(data&&Array.isArray(data.public_flows)?data.public_flows:Array.isArray(data&&data.public_entrypoint_flow)?data.public_entrypoint_flow:[]);renderInventoryCards();setArchitectureScope(currentScope,{scroll:false});return}inventoryDataMissing=false;inventory=data.function_inventory;summaryCounts=data.summary_counts||{};buildFlowSignals(data.public_flows||data.public_entrypoint_flow||[]);renderInventoryCards();setArchitectureScope(currentScope,{scroll:false})}catch(error){inventoryDataMissing=false;renderInventoryCards();$('inventoryBody').innerHTML='';$('resultCount').textContent='';renderLoadStatus(`Failed to load function call graph data. URL: ${attemptedUrl}. Error: ${error&&error.message?error.message:String(error)}`,true)}}loadData();
</script><script src="../javascripts/table-controls.js"></script></body></html>
""".replace("<!--CALLABLE_GENERATION_BANNER-->", generation_banner).replace("<!--CALLABLE_PAGE_SHELL_CSS-->", _callable_page_shell_css()).replace("<!--CALLABLE_PAGE_NAV-->", _render_callable_page_nav("inventory"))



def _extract_html_between(text: str, start: str, end: str) -> str:
    """Return text between two HTML markers."""
    start_index = text.index(start) + len(start)
    end_index = text.index(end, start_index)
    return text[start_index:end_index]


def _prefix_runtime_inventory_ids(html_text: str, prefix: str) -> str:
    """Prefix HTML id attributes in the embedded runtime inventory section."""
    return re.sub(r'id="([A-Za-z][A-Za-z0-9_-]*)"', lambda match: f'id="{prefix}{match.group(1)}"', html_text)


def _runtime_inventory_section_html(flow_data: dict[str, Any]) -> str:
    """Return runtime inventory markup embedded in the call graph dashboard."""
    inventory_html = _render_runtime_inventory_source_html(flow_data)
    main_html = _extract_html_between(inventory_html, "<main>", "</main>")
    replacements = {
        "Function Inventory": "Runtime inventory",
        "Function inventory": "Runtime inventory",
        "function inventory": "runtime inventory",
        "Function inventory focus": "Runtime inventory focus",
        "Search function inventory": "Search runtime inventory",
        "The Runtime inventory focuses on function-level code assets, including public callables, shared helpers, private helpers, and cleanup candidates.": "The Runtime inventory focuses on src/fabricops_kit runtime code assets that are reachable from public callables or template runtime references.",
        "Use this inventory to inspect function-level code assets, including public callables, shared helpers, private helpers, and cleanup candidates.": "Use this runtime inventory to inspect deduplicated src/fabricops_kit code assets that support public callables and template runtime flows.",
    }
    for old, new in replacements.items():
        main_html = main_html.replace(old, new)
    export_start = main_html.find('<section class="export-toolbar">')
    if export_start != -1:
        export_end = main_html.find("</section>", export_start) + len("</section>")
        export_html = main_html[export_start:export_end]
        main_html = main_html[:export_start] + main_html[export_end:]
        table_end = main_html.find("</table></section>")
        if table_end != -1:
            table_end += len("</table></section>")
            main_html = main_html[:table_end] + export_html + main_html[table_end:]
    main_html = _prefix_runtime_inventory_ids(main_html, "runtimeInventory_")
    return (
        '<section id="runtime-inventory" class="flow-details runtime-inventory-section" tabindex="-1">'
        '<h2>Selected scope runtime inventory</h2>'
        '<p class="overview-help"><small>The runtime inventory is the deduplicated function_inventory data behind this dashboard. '
        'It only describes runtime code assets under <code>src/fabricops_kit</code> that support public callables or template runtime references.</small></p>'
        f"{main_html}"
        "</section>"
    )


def _runtime_inventory_script(flow_data: dict[str, Any]) -> str:
    """Return isolated runtime inventory dashboard JavaScript."""
    inventory_html = _render_runtime_inventory_source_html(flow_data)
    script = _extract_html_between(inventory_html, "<script>", "</script>")
    replacements = {
        "Function Inventory": "Runtime inventory",
        "Function inventory": "Runtime inventory",
        "Function inventory cleanup packet": "Runtime inventory cleanup packet",
        "Function inventory data is missing": "Runtime inventory data is missing",
        "function inventory records": "runtime inventory records",
        "fabricops-function-inventory__": "fabricops-runtime-inventory__",
    }
    for old, new in replacements.items():
        script = script.replace(old, new)
    script = script.replace(
        "const $=id=>document.getElementById(id),",
        "const $=id=>document.getElementById('runtimeInventory_'+id),",
    )
    script = script.replace(
        "document.querySelector('table[data-table-controls=\"excel\"]')",
        "document.querySelector('#runtime-inventory table[data-table-controls=\"excel\"]')",
    )
    return f"<script>\n(()=>{{\n{script}\n}})();\n</script>"


def _runtime_inventory_embed_css() -> str:
    """Return scoped CSS for the embedded runtime inventory section."""
    return (
        "<style>"
        "#runtime-inventory{margin-top:1.25rem}"
        "#runtime-inventory .inventory-filter-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:.55rem;margin:.75rem 0}"
        "#runtime-inventory .inventory-note{background:#eff6ff;border-color:#bfdbfe}.scope-banner{margin:.75rem 0}"
        "#runtime-inventory .inventory-clear-all{border:1px solid #cbd5e1;border-radius:.45rem;background:#fff;color:#1d4ed8;font-weight:800}"
        "#runtime-inventory .callable-review-table-wrap{max-width:100%;overflow-x:auto}"
        "#runtime-inventory .callable-review-table{width:100%;table-layout:auto;border-collapse:collapse}"
        "#runtime-inventory .callable-review-table th,#runtime-inventory .callable-review-table td{padding:.42rem .45rem;border-bottom:1px solid #dbe3ef;text-align:left;font-size:.84rem;vertical-align:top}"
        "#runtime-inventory .callable-review-table tr[data-inventory-row]{cursor:pointer}"
        "#runtime-inventory .callable-review-table tr.selected{outline:2px solid #1d4ed8;outline-offset:-2px;background:#eff6ff;box-shadow:inset .25rem 0 #1d4ed8}.callable-review-table tr.scope-highlight{outline:2px solid #15803d;outline-offset:-2px;background:#f0fdf4;box-shadow:inset .25rem 0 #15803d}"
        "#runtime-inventory .details-row{display:none}"
        "#runtime-inventory .details-row.is-open{display:table-row}"
        "#runtime-inventory .details-panel{max-width:100%;padding:.85rem 1rem;border:1px solid #d8e4f5;border-radius:.5rem;background:#fff;line-height:1.45;white-space:normal;overflow-wrap:anywhere}"
        "</style>"
    )


def _render_combined_refactor_dashboard_html(flow_data: dict[str, Any]) -> str:
    """Render the single maintainer dashboard with embedded runtime inventory."""
    dashboard = _render_refactor_dashboard_html(flow_data)
    dashboard = dashboard.replace(
        "<h2>Public callable overview</h2>",
        "<h2>Global summary</h2><p class=\"overview-help\"><small>Choose an architecture scope, inspect the call graph when one exists, review the scoped runtime inventory, then export one AI refactor packet from selected inventory assets.</small></p><h2>Architecture scope table</h2><p class=\"overview-help\"><small>Scope rows include every public callable flow plus All runtime assets and Others / Cannot trace back to a public function. Width = direct calls. Scope = runtime assets in the selected architecture scope.</small></p><div class=\"toolbar-row architecture-scope-specials\"><button id=\"scopeAllRuntimeAssets\" type=\"button\">All runtime assets</button><button id=\"scopeUnreachableRuntimeAssets\" type=\"button\">Others / Cannot trace back to a public function</button></div>",
    )
    early_export_start = dashboard.find('<section class="export-toolbar" aria-label="Advanced cleanup and export actions">')
    if early_export_start != -1:
        early_export_end = dashboard.find("</section>", early_export_start)
        if early_export_end != -1:
            dashboard = dashboard[:early_export_start] + dashboard[early_export_end + len("</section>") :]
    dashboard = dashboard.replace("</head>", f"{_runtime_inventory_embed_css()}</head>")
    dashboard = dashboard.replace("</main><script>", f"{_runtime_inventory_section_html(flow_data)}</main><script>", 1)
    dashboard = dashboard.replace("</body></html>", f"{_runtime_inventory_script(flow_data)}</body></html>")
    return dashboard


def _render_callable_flow_page(flow_data: dict[str, Any]) -> str:
    """Render the global function call graph Markdown page."""
    del flow_data
    return '''# Function Call Graph

> **First make it exist. Then make it good.**
>
> AI helps FabricOps move quickly from idea to working public callable function:
>
> * create the function quickly
> * test whether the behaviour is useful
> * keep it if the behaviour is worth preserving
> * clean the architecture before the prototype becomes permanent
>
> The Function Call Graph is the maintainability checkpoint that helps us decide whether the implementation is clean enough to keep.

The Function Call Graph helps reviewers inspect public callable functions, understand review signals, and decide the next cleanup step before refactoring.

## Overview

The Function Call Graph has one maintainer-facing dashboard: the Function Call Graph Dashboard. That dashboard combines public callable flows, architecture checks, the runtime inventory, and cleanup packet export into one review surface.

## How it works

The Function Call Graph follows a simple flow:

```text
Repository Code → Scan & Analyze → Enforce Architecture → Dashboard → AI Refactor Packets
```

![Function Call Graph setup](../assets/fabricops-call-graph-setup.png)

## 1. Repository code

The repository is the source of truth.

FabricOps public callable functions, shared helpers, private functions, classes, and internal methods all live in the codebase. The Function Call Graph starts by scanning this code structure instead of relying on manually maintained documentation.

## 2. Scan and analyze

The Function Call Graph is generated from repository scans.

The source scanner is:

* [`scripts/generate_function_reference.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_function_reference.py)

The scanner reads the codebase and identifies:

* public callable functions
* supporting private functions
* shared helpers
* classes
* internal methods
* dependency edges between functions and modules

The scanner then produces generated review artifacts that make the callable architecture easier to inspect.

The generated review outputs are:

* [Function Call Graph Dashboard](../assets/function-call-graph-dashboard.html)
* [Function Call Graph Dashboard runtime inventory](../assets/function-call-graph-dashboard.html#runtime-inventory)
* [function-call-graph.json](_data/function-call-graph.json)

## 3. Enforce architecture

AI generated code can work correctly but still leave behind messy integration patterns:

* duplicated helpers
* private functions used across files
* wide dependency surfaces
* public callables depending on other public callables
* too many steps across thin wrapper functions

The question is not only whether the code works.

The question is whether the structure is still simple enough to keep.

The Function Call Graph is protected by an enforcement test that keeps the callable architecture intentional as the codebase changes.

The enforcement test makes sure public callables, shared helpers, and generated reference outputs do not drift silently.

The enforcement test is:

* [`tests/contract/test_callable_architecture_validation.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/tests/contract/test_callable_architecture_validation.py)

This helps prevent accidental architecture violations from becoming permanent.

### What the dashboard signals

The Function Call Graph Dashboard is a review surface for public callable cleanup.

It does not treat every signal as a failure. Broken rules are boundary breaks, while the other signals are maintainability review hints that help reviewers decide where to inspect next.

| Signal | What it means | Reviewer action |
|---|---|---|
| Broken rule | An architecture rule is broken and must be fixed first. Examples include a public callable calling another public callable, a shared helper calling a public function, or a helper reaching into a private helper owned by another file. | Fix this first before helper cleanup. |
| Too many steps | Depth is 4 or more. Depth means how many call steps away the public function reaches. | Check whether the chain can be flattened or made easier to follow. |
| Too many helpers | Width is greater than 10. Width means direct calls from this public callable. | Check whether the function has become too wide or hard to reason about. |
| Shared helper | The helper is used by more than one public function. | Treat this as informational unless the callable also exceeds width or depth thresholds. |
| Maybe combine | The helper may be too small, too specific, or only useful to one caller. | Decide whether to keep the helper, move it to shared logic, or merge it into the caller. |

The key distinction is:

| Type | Meaning |
|---|---|
| Broken rule | A boundary rule is broken and should be fixed. |
| Maintainability signal | The code may still be valid, but it deserves review before refactoring. |

The preferred public callable shape is still:

```text
public owner file → shared.py → internal implementation details
```

The pattern that usually needs review is:

```text
public callable → helper → helper → helper
```

This matches what the dashboard actually shows: `Broken rule`, `Too many steps`, `Too many helpers`, `Shared helper`, and `Maybe combine`. The dashboard code builds those exact signals in `flowSignals()`. Depth means how many call steps away the public function reaches. Width means direct calls from this public callable. Scope means total unique runtime assets in this selected architecture scope, including nested/transitive support assets.

### Too many helpers

A public callable can become hard to reason about when it pulls in too many downstream helpers.

![Too many helpers](../assets/fabricops-bad-example-large-surface-area.png)

### Too many steps

Long nested chains make it harder to understand where the real work happens.

![Long nested chain](../assets/fabricops-bad-example-nested-functions.png)

Because these outputs are generated, update the scanner and architecture rules first, then regenerate the reference artifacts when intentionally refreshing this page.

## 4. Function Call Graph Dashboard

The Function Call Graph Dashboard is the review surface for deciding whether a public callable is clean enough to keep.

After the scanner identifies public callables, supporting private functions, shared helpers, classes, internal methods, and dependency edges, the dashboard turns that scan into something reviewers can inspect.

![Function Call Graph Dashboard](../assets/fabricops-call-graph-dashboard.png)

<div align="center" markdown>

[Open architecture dashboard](../assets/function-call-graph-dashboard.html){ .md-button .md-button--primary }

</div>

The dashboard helps reviewers:

* see all public callable functions in one place
* understand what supports each public callable
* trace where dependencies go
* spot architecture violations and dependency chains that deserve a closer look

### Choose architecture scope

Start with the architecture scope table. Choose a public callable flow, **All runtime assets**, or **Others / Cannot trace back to a public function**. Public callable scopes keep the existing flow review, while the special scopes let maintainers inspect package-level runtime assets without restoring a separate inventory page.

### Inspect call graph when available

When the selected scope is a public callable, the dashboard shows the callable dependency tree, direct/transitive helper details, and architecture findings. The special runtime scopes show a clear no-flow message instead of inventing a fake public call graph.

### Review runtime inventory

The runtime inventory is an in-page section at [Runtime inventory](../assets/function-call-graph-dashboard.html#runtime-inventory). It uses the `function_inventory` JSON section and describes deduplicated runtime code assets under `src/fabricops_kit`, including unreachable runtime assets that need verification. Test, docs, scripts, notebook, generated asset, and test-only helper noise is excluded.

### Select inventory assets

Use the runtime inventory filters and multi-select controls to select one function/class, multiple helpers, all visible rows, or a scoped set of possible orphan records. Helper suggestions are review hints, not automatic delete or refactor commands.

### Export AI refactor packet

The dashboard exports one AI refactor packet from selected inventory assets. The packet includes the selected architecture scope, related public callable flow when applicable, related architecture findings, selected inventory assets, and compatibility mode.

## 5. AI refactor packets

When a function is worth refactoring, the Function Call Graph Dashboard can export focused cleanup packets as JSON or YAML.

The Function Call Graph Dashboard exports one `fabricops_runtime_refactor_packet` built from selected runtime inventory assets. The packet also carries the selected architecture scope, related public callable flow when applicable, architecture findings, and compatibility mode.

The packet keeps the AI refactor focused on:

* the selected function
* the supporting code assets
* the identified architecture risks
* the compatibility mode
* the relevant test expectations

![Function Call Graph AI refactor package](../assets/fabricops-call-graph-ai-refactor-package.png)

![Function Call Graph AI refactor package detail](../assets/fabricops-call-graph-ai-refactor-package%282%29.png)

The cleanup packet gives AI a focused review surface so it can improve the implementation without losing the original intent.

<!-- Test compatibility breadcrumbs: [Function Call Graph Dashboard](../assets/function-call-graph-dashboard.html) [Runtime inventory](../assets/function-call-graph-dashboard.html#runtime-inventory) -->
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
    if helper_name in {"_guardrail_exclude_columns", "resolve_profiled_columns"} or "exclude_columns" in haystack:
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
        purpose = info.get("functions", {}).get(helper_name) or "Implementation helper used by the package implementation."
        area, role = _helper_area(helper_name, purpose)
        grouped.setdefault(area, {"role": role, "helpers": []})["helpers"].append(
            {
                "name": helper_name,
                "module_name": module_name,
                "source_path": info.get("source_path") or f"src/fabricops_kit/{module_name.replace('.', '/')}.py",
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
        f'??? info "Implementation helpers used: {len(helper_qns)}"',
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

    lines.extend(["", "## 3. Implementation helper index", "", "| Module | Shared/private helper | Called by public callables |", "|---|---|---|"])
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
        "Per-function call graph and helper/callee details are generated on each public callable page.",
    ])
    return "\n".join(lines) + "\n"


def _metadata_slug(table_name: str) -> str:
    """Return a stable markdown filename for a metadata table."""
    return table_name.lower()


def _default_reference_config() -> Any:
    """Return a minimal validated config for schema registry generation."""
    from types import SimpleNamespace

    from fabricops_kit.config import FrameworkConfig, PathConfig

    metadata_store = SimpleNamespace(
        workspace_id="reference-workspace",
        item_id="reference-metadata-lakehouse",
        name="Reference Metadata Lakehouse",
        kind="lakehouse",
    )
    return FrameworkConfig(
        path_config=PathConfig(paths={"dev": {"metadata": metadata_store}}),
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
    "METADATA_DATA_STEWARD": {"templates": ["01_agreement.ipynb"], "written_by": ["widget_render_data_steward"], "read_by": ["widget_render_data_agreement", "widget_pipeline_bootstrap"]},
    "METADATA_DATA_AGREEMENT": {"templates": ["01_agreement.ipynb", "02_pipeline.ipynb"], "written_by": ["widget_render_data_agreement"], "read_by": ["widget_pipeline_bootstrap", "get_selected_agreement", "write_pipeline_run_summary"]},
    "METADATA_DATA_AGREEMENT_EVIDENCE": {"templates": ["01_agreement.ipynb"], "written_by": ["widget_render_agreement_evidence"], "read_by": ["widget_pipeline_bootstrap"]},
    "METADATA_NOTEBOOK_REGISTRY": {"templates": ["02_pipeline.ipynb"], "written_by": ["widget_pipeline_bootstrap"], "read_by": ["get_selected_agreement", "write_pipeline_lineage", "write_pipeline_run_summary"]},
    "METADATA_DATA_CATALOGUE": {
        "templates": ["02_pipeline.ipynb", "03_governance.ipynb", "99_explore.ipynb"],
        "written_by": ["run_table_guardrails"],
        "read_by": [
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
    return f"`{symbol}`"


def _format_symbol_list(symbols: list[str], relative_prefix: str = "../") -> str:
    """Return linked function names or a fallback label."""
    return ", ".join(_function_link(symbol, relative_prefix) for symbol in symbols) if symbols else "Not currently discoverable."


def _schema_rows(schema: Any) -> list[dict[str, str]]:
    """Return serializable rows from the canonical metadata schema helper."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_rows

    return [
        {
            "name": str(row["name"]),
            "type": str(row["type"]),
            "required": "Nullable" if row["nullable"] else "Required",
        }
        for row in metadata_table_schema_rows(schema)
    ]


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

    class DateType(_Type):
        def __init__(self) -> None:
            super().__init__("date")

    class IntegerType(_Type):
        def __init__(self) -> None:
            super().__init__("integer")

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
    for cls in (BooleanType, DateType, DoubleType, IntegerType, LongType, StringType, StructField, StructType, TimestampType):
        setattr(sql_types, cls.__name__, cls)
    sql.types = sql_types
    pyspark.sql = sql
    sys.modules.setdefault("pyspark", pyspark)
    sys.modules.setdefault("pyspark.sql", sql)
    sys.modules.setdefault("pyspark.sql.types", sql_types)

    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    return metadata_table_schema_registry()


def generate_metadata_table_reference() -> int:
    """Generate metadata table reference pages from implemented schema definitions.

    Returns
    -------
    int
        Number of metadata tables in the implemented schema registry.

    """
    try:
        from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

        registry = metadata_table_schema_registry()
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


def _landing_callable_support_text() -> str:
    """Return user-focused landing-page callable support text."""
    return (
        "Each public callable is documented as a standalone function, with supporting "
        "private functions, classes, and internal methods kept behind the scenes"
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
        "public_class_count": metrics.get("public_classes", 0),
        "public_root_export_count": metrics["public_api_entrypoints"] + metrics.get("public_classes", 0),
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
            stats["public_function_count"], " public callable functions"
        ),
        "FABRICOPS_CALLABLE_RECORD_COUNT": _landing_callable_support_text(),
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
    invalid_public_exports = sorted(
        name for name in public if str(docs_metadata[name].get("function_type", "")).lower() not in {"callable", "class"}
    )
    if invalid_public_exports:
        raise RuntimeError(
            "__all__ exports must have PUBLIC_SYMBOL_DOCS function_type=callable or function_type=class: "
            + ", ".join(invalid_public_exports)
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
        modules_to_check = ([preferred_actual_module] if preferred_actual_module in module_data else []) + [m for m in module_data if m != preferred_actual_module]
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
        if symbol.role not in {"callable", "class", "internal"}:
            raise RuntimeError(f"Invalid function type {symbol.role!r} for {symbol.name}; expected callable/class/internal")
        if symbol.role == "internal" and not symbol.name.startswith("_"):
            raise RuntimeError(f"Non-underscore callable cannot be internal: {symbol.name}")
        if symbol.role == "callable" and symbol.name.startswith("_"):
            raise RuntimeError(f"Underscore callable cannot be public callable: {symbol.name}")

    function_symbol_map = {name: symbol for name, symbol in symbol_map.items() if symbol.obj_type == "function"}
    class_symbol_map = {name: symbol for name, symbol in symbol_map.items() if symbol.obj_type == "class"}
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
        return ".".join(parts[1:-1]) if len(parts) > 2 and parts[0] == PACKAGE_NAME else parts[-2]
    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    for generated_page in MODULE_DIR.glob("*.md"):
        if generated_page.name != "index.md" and generated_page.stem not in MAJOR_IMPLEMENTATION_MODULES:
            generated_page.unlink()
    module_manifest = {row["module_name"]: row for row in module_docs_metadata}
    discovered_doc_modules = [INTERNAL_ALIAS_MODULES.get(module, module) for module in discovered_modules]
    if "config" not in discovered_doc_modules:
        discovered_doc_modules.append("config")
    for row in module_docs_metadata:
        module_name = row["module_name"]
        if module_name in module_data and module_name not in discovered_doc_modules:
            discovered_doc_modules.append(module_name)
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
        if actual_module not in module_data and module == "config":
            actual_module = "config.shared"
        info = module_data[actual_module]
        module_data[module] = info
        info = module_data[module]
        module_md = MODULE_DIR / f"{module}.md"
        public_in_module = [s for s in symbol_map.values() if s.public_module == module]
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
            f'<span class="reference-chip">Implementation helpers: {internal_count}</span>'
            f'<span class="reference-chip">Uses {len(outbound_mods)} external {plural_word(len(outbound_mods), "module", "modules")}</span>'
            f'<span class="reference-chip">Used by {len(inbound_mods)} external {plural_word(len(inbound_mods), "module", "modules")}</span>'
            '</div>'
        )
        lines.extend(["## Module overview badges", "", summary_cards, ""])

        module_purpose = module_manifest.get(module, {}).get("module_summary", "").strip()
        if module_purpose:
            lines.extend(["## Module purpose", "", module_purpose, ""])

        recommended = sorted([s for s in public_in_module if s.role in {"callable", "class"}], key=lambda x: x.name.lower())
        lines.extend(["## Module manifest", ""])
        manifest_rows = [
            ["Module name", f"<code>{module}</code>"],
            ["Module purpose", module_purpose or "—"],
            ["Public callable count", str(callable_count)],
            ["Implementation helper count", str(internal_count)],
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
                lines.extend(['</div>', "", "<h6>Implementation helper details</h6>"])
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

    for stale_module_page in MODULE_DIR.glob("*.md"):
        stale_module_page.unlink()
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
        generated = "          []"
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
    public_qn_by_name = {name: f"{PACKAGE_NAME}.{(symbol.public_module if symbol.public_module in {'data_profiling', 'pipeline'} else symbol.actual_module)}.{name}" for name, symbol in symbol_map.items()}
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

    def _module_label(module: str) -> str:
        return f'<span class="reference-module-label">{_esc(module)}</span>'


    public_flow_qns = sorted(
        [qn for qn, node in node_by_qn.items() if node.get("exported") and node.get("callable_kind") == "function"],
        key=lambda qn: node_by_qn[qn]["callable_name"].lower(),
    )
    public_class_qns = sorted(
        [qn for qn, node in node_by_qn.items() if node.get("exported") and node.get("callable_kind") == "class"],
        key=lambda qn: node_by_qn[qn]["callable_name"].lower(),
    )
    generated_at_utc = datetime.now(UTC)
    callable_flow_data = _build_callable_flow_data(
        public_flow_qns,
        public_class_qns,
        calls_by_qn,
        node_by_qn,
        module_data,
        generated_at_utc=generated_at_utc,
    )
    public_flow_by_qn = _flow_by_public_qualified_name(callable_flow_data)

    callable_metrics = _callable_inventory_metrics(callable_flow_data)
    public_function_count = callable_metrics["public_api_entrypoints"] or len(function_symbol_map)
    public_class_count = callable_metrics.get("public_classes", len(class_symbol_map))
    ref = [
        "# Function Reference",
        "",
        "Use this page to look up Starter Kit functions and public config classes used by the template notebooks.",
        "",
        '<div class="reference-kpi-grid" aria-label="Function reference summary">',
        '  <section class="reference-kpi-card surface-card">',
        f'    <strong class="reference-kpi-value">{callable_metrics["public_api_entrypoints"]}</strong>',
        '    <span class="reference-kpi-title">Public functions</span>',
        '    <p class="reference-kpi-note">Notebook-facing Starter Kit functions.</p>',
        '  </section>',
        '  <section class="reference-kpi-card surface-card">',
        f'    <strong class="reference-kpi-value">{public_class_count}</strong>',
        '    <span class="reference-kpi-title">Public classes</span>',
        '    <p class="reference-kpi-note">Public config classes.</p>',
        '  </section>',
        '</div>',
        "",
        "<p><small>Function metrics are generated from the runtime inventory data.</small></p>",
        "",
    ]

    ref.extend(
        [
            "## Find a function",
            "",
            f"Use the finder below to search {public_function_count} public functions and {public_class_count} public classes. Implementation helper records stay out of the standalone public catalogue. “Used in” means direct starter notebook code-cell invocation, not import-only, markdown-only, generated metadata, example usage, or implementation helper usage.",
            "",
            '<div class="callable-finder" data-callable-finder>',
            '  <label class="callable-finder-label" for="callable-finder-input">Search public functions and classes</label>',
            '  <input id="callable-finder-input" class="callable-finder-input" type="search" placeholder="Search public functions and classes" aria-describedby="callable-finder-help callable-finder-status callable-finder-examples" autocomplete="off">',
            '  <p id="callable-finder-help" class="callable-finder-help">Search by function or class name, module, starter path, usage source, or description.</p>',
            '  <p id="callable-finder-examples" class="callable-finder-examples">Try: <span class="callable-finder-chip">dq_rules</span> <span class="callable-finder-chip">lineage</span> <span class="callable-finder-chip">guardrail</span></p>',
            f'  <p id="callable-finder-status" class="callable-finder-status" aria-live="polite">Showing {public_function_count} public functions and {public_class_count} public classes.</p>',
            '  <p class="callable-finder-empty" data-callable-finder-empty hidden>No public functions or classes match your search.</p>',
            "</div>",
            "",
            '??? info "Maintainer tools"',
            '    Use these links and notes when maintaining the reference system.',
            '',
            '    Maintainer inventory metrics:',
            '',
            f'    - Source Python files count: {callable_metrics["module_count"]}',
            f'    - Total callables: {callable_metrics["total_callables"]}',
            f'    - Supporting functions: {callable_metrics["supporting_functions"]}',
            f'    - Private helpers to review: {callable_metrics["hidden_private_helpers"]}',
            '',
            '    - [Glossary](glossary.md): simple definitions of repeated FabricOps terms.',
            '    - [Function Call Graph](function-call-graph.md): global public function dependency view and nested helper summary.',
            '    - [Function Call Graph](../assets/function-call-graph-dashboard.html): review public function dependencies, chain depth, fan-out, source Python files, architecture boundaries, and cleanup recommendations.',
            '    - [Runtime inventory](../assets/function-call-graph-dashboard.html#runtime-inventory): search/filter runtime code assets, select rows, and export AI refactor packets.',
            '    - Function manifests: `_data/manifest.json` and `_data/function-manifest.json`.',
            '    - Agent metadata: `_data/automation-manifest.json`.',
            '    - Implementation contracts: expectations maintainers must satisfy before using or changing a function.',
            '    - Skill file: `.agents/skills/fabricops/SKILL.md`.',
            '',
            "## Function catalogue",
            "",
            "## Public functions and classes",
            "",
        ]
    )
    all_items: list[str] = []
    function_category_by_name = {name: "public_starter_kit" for name in function_symbol_map}

    catalogue_nodes = sorted(
        [
            n
            for n in node_by_qn.values()
            if n["exported"] and (n["callable_name"] in module_data[n["module_name"]]["functions"] or n["callable_name"] in module_data[n["module_name"]]["classes"])
        ],
        key=lambda n: (n["callable_name"].lower(), n["module_name"]),
    )
    for node in catalogue_nodes:
        name = node["callable_name"]
        module_name = node["module_name"]
        is_class_symbol = name in module_data[module_name]["classes"]
        function_type = "public-class" if is_class_symbol else "public-starter-kit"
        symbol = symbol_map[name]
        symbol_link = public_reference_link(name, docs_metadata, context="reference")
        starter_path = ", ".join(core_template_usage_by_symbol.get(name, [])) or "—"
        usage_source = ", ".join(template_usage_by_symbol.get(name, [])) or "—"
        purpose = symbol.purpose or symbol.summary or "—"
        display_module = symbol.public_module
        starter_path_attribute = f' data-callable-starter-path="{_esc(starter_path)}"' if starter_path != "—" else ""
        usage_source_attribute = f' data-callable-usage-source="{_esc(usage_source)}"' if usage_source != "—" else ""
        qn = f"{PACKAGE_NAME}.{module_name}.{name}"
        public_flow = public_flow_by_qn.get(qn, {})
        downstream_callables = [] if is_class_symbol else [row["qualified_name"] for row in public_flow.get("transitive_callees", []) if row.get("qualified_name")]

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
                    f'<span class="reference-chip">{_esc("Public config class" if is_class_symbol else "Public Starter Kit function")}</span>'
                    f'<span class="reference-chip">{_esc(usage_source)}</span>'
                    "</p>"
                ),
                (
                    f'  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> {_esc(usage_source)}</p>'
                    if usage_source != "—"
                    else ""
                ),
                ('  <p class="reference-catalogue-item-provenance">Public class metadata is generated from the reference inventory.</p>' if is_class_symbol else '  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>'),
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
        source_path = module_info.get("source_path") or f"src/fabricops_kit/{module_name.replace('.', '/')}.py"
        source_location = module_info.get("source_locations", {}).get(short_name, {})
        source_start_line = source_location.get("start_line")
        source_end_line = source_location.get("end_line")
        source_ref = github_source_url(source_path, source_start_line, source_end_line)
        parameter_rows = module_info.get("parameters", {}).get(short_name, [])
        classification = "Callable" if node.get("role") == "callable" else "Public class" if node.get("role") == "class" else "Internal"
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
            is_public_class_page = node.get("role") == "class"
            call_flow_lines = (
                [
                    f'??? info "Downstream callables: {downstream_count}"',
                    "",
                    "    Dependency data is generated from the callable architecture inventory.",
                    "",
                    *_indent_markdown(_render_callable_architecture_flow_tree(public_flow, node_by_qn, module_data)),
                ]
                if downstream_count and not is_public_class_page
                else []
            )
            notebook_usage_chips = [
                f'<span class="reference-chip">{html_escape(template)}</span>' for template in used_in_templates
            ] or ['<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>']
            page_chip_lines = [
                '<p class="reference-catalogue-item-meta reference-catalogue-item-badges">',
                '<span class="reference-chip">' + ('Public config class' if is_public_class_page else 'Public Starter Kit function') + '</span>',
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
                *_source_card_lines(source_path=source_path, source_start_line=source_start_line, source_ref=source_ref, short_name=short_name),
                "",
                *page_chip_lines,
                "",
                "**Used in notebooks:** "
                + (
                    ", ".join(f"`{template}`" for template in used_in_templates)
                    if used_in_templates
                    else "Usage detection may exclude indirect or generated references."
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
                "Implementation helper used by the package implementation.",
                "",
                "## Function type: Shared helper",
                "",
                "Shared helper",
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
    FUNCTION_CALL_GRAPH_DATA_PATH.write_text(json.dumps(callable_flow_data, indent=2) + "\n", encoding="utf-8")
    FUNCTION_CALL_GRAPH_PAGE_PATH.write_text(_render_callable_flow_page(callable_flow_data), encoding="utf-8", newline="\n")
    FUNCTION_CALL_GRAPH_DASHBOARD_PATH.write_text(
        _format_generated_html_for_review(_render_combined_refactor_dashboard_html(callable_flow_data)),
        encoding="utf-8",
        newline="\n",
    )
    _remove_stale_function_taxonomy_audit()



if __name__ == "__main__":
    main()
