"""Generate callable reference pages for MkDocs build."""
from __future__ import annotations

import ast
from pathlib import Path

import mkdocs_gen_files

PACKAGE = "fabricops_kit"
PKG_DIR = Path(__file__).resolve().parents[1] / "src" / PACKAGE
DOCS_METADATA_PATH = Path(__file__).resolve().parents[1] / "scripts" / "reference_docs_metadata.py"
SKIPPED_PACKAGE_MODULE_FILES = {"__init__.py"}
NOISE_ATTRS = {"append", "clear", "get", "items", "on_click"}
NOISE_CALLS = {
    "json.dumps",
    "json.loads",
    "widgets.Button",
    "widgets.Dropdown",
    "widgets.HBox",
    "widgets.VBox",
    "widgets.HTML",
}
DEPENDENCY_METADATA_PATH = Path(__file__).resolve().parents[1] / "docs" / "reference" / "dependency-metadata.json"


def _read_literal(path: Path, name: str):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        is_assign = isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)
        is_ann = isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name
        if (is_assign or is_ann) and node.value is not None:
            return ast.literal_eval(node.value)
    raise RuntimeError(f"Missing literal {name} in {path}")


def _first_sentence(doc: str | None) -> str:
    if not doc:
        return ""
    line = doc.strip().splitlines()[0].strip()
    return line


def _parse_exports() -> set[str]:
    tree = ast.parse((PKG_DIR / "__init__.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
            if isinstance(node.value, ast.List):
                return {elt.value for elt in node.value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)}
    raise RuntimeError("Missing __all__")


def _build_index():
    modules: dict[str, dict[str, str]] = {}
    imports: dict[str, tuple[dict[str, str], dict[str, str]]] = {}
    for p in sorted(PKG_DIR.glob("*.py")):
        if p.name in SKIPPED_PACKAGE_MODULE_FILES:
            continue
        tree = ast.parse(p.read_text(encoding="utf-8"))
        mod = p.stem
        functions = {}
        for n in tree.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                functions[n.name] = _first_sentence(ast.get_docstring(n))
        modules[mod] = functions
        mod_alias, sym_alias = {}, {}
        for n in tree.body:
            if isinstance(n, ast.Import):
                for a in n.names:
                    mod_alias[a.asname or a.name] = a.name
            elif isinstance(n, ast.ImportFrom) and n.module:
                for a in n.names:
                    if a.name != "*":
                        sym_alias[a.asname or a.name] = f"{n.module}.{a.name}"
        imports[mod] = (mod_alias, sym_alias)
    return modules, imports


def _resolve_call(raw: str, module: str, same_names: set[str], mod_alias: dict[str, str], sym_alias: dict[str, str], exports: set[str], modules: dict[str, dict[str, str]]) -> str | None:
    if raw in same_names:
        return f"{PACKAGE}.{module}.{raw}"
    if raw in sym_alias:
        path = sym_alias[raw]
        parts = path.split(".")
        if len(parts) >= 2 and (path.startswith(PACKAGE) or parts[-2] in modules):
            return f"{PACKAGE}.{parts[-2]}.{parts[-1]}"
    if "." in raw:
        owner, member = raw.split(".", 1)
        if member in NOISE_ATTRS or raw in NOISE_CALLS:
            return None
        mapped = mod_alias.get(owner, owner)
        short = mapped.split(".")[-1]
        if mapped.startswith(PACKAGE) or short in modules:
            return f"{PACKAGE}.{short}.{member}"
        return None
    if raw in exports:
        for m, names in modules.items():
            if raw in names:
                return f"{PACKAGE}.{m}.{raw}"
    return None


def _collect_calls(modules, imports, exports):
    call_map = {m: {} for m in modules}
    reverse: dict[str, set[str]] = {}
    for p in sorted(PKG_DIR.glob("*.py")):
        if p.name in SKIPPED_PACKAGE_MODULE_FILES:
            continue
        mod = p.stem
        tree = ast.parse(p.read_text(encoding="utf-8"))
        same_names = set(modules[mod])
        mod_alias, sym_alias = imports[mod]
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            caller_qn = f"{PACKAGE}.{mod}.{node.name}"
            resolved = set()
            for child in ast.walk(node):
                if not isinstance(child, ast.Call):
                    continue
                raw = ""
                if isinstance(child.func, ast.Name):
                    raw = child.func.id
                elif isinstance(child.func, ast.Attribute):
                    if isinstance(child.func.value, ast.Name):
                        raw = f"{child.func.value.id}.{child.func.attr}"
                    else:
                        raw = child.func.attr
                if raw in NOISE_CALLS or raw.endswith(".append"):
                    continue
                target = _resolve_call(raw, mod, same_names, mod_alias, sym_alias, exports, modules)
                if target:
                    resolved.add(target)
                    reverse.setdefault(target, set()).add(caller_qn)
            call_map[mod][node.name] = resolved
    return call_map, reverse


public_symbol_docs = _read_literal(DOCS_METADATA_PATH, "PUBLIC_SYMBOL_DOCS")
dependency_metadata = {}
if DEPENDENCY_METADATA_PATH.exists():
    import json
    dependency_metadata = json.loads(DEPENDENCY_METADATA_PATH.read_text(encoding="utf-8"))
exports = _parse_exports()
modules, imports = _build_index()
module_call_map, reverse_refs = _collect_calls(modules, imports, exports)


def _parts(qualified_name: str) -> tuple[str, str]:
    parts = qualified_name.split(".")
    return parts[-2], parts[-1]


def _is_public_callable(symbol: str) -> bool:
    return symbol in exports


def _callable_href(qualified_name: str) -> str:
    module_name, callable_name = _parts(qualified_name)
    if _is_public_callable(callable_name):
        return f"../{callable_name}/"
    return f"../internal/{module_name}/{callable_name}/"


def _callable_label(qualified_name: str, *, current_module: str | None = None) -> str:
    module_name, callable_name = _parts(qualified_name)
    if current_module and module_name == current_module:
        return callable_name
    return f"{module_name}.{callable_name}"


def _module_link(module_name: str) -> str:
    """Return a safe module-page link when a module reference page exists."""
    if module_name in modules:
        return f'<a class="reference-module-link" href="../../modules/{module_name}/"><code>{module_name}</code></a>'
    return f"<code>{module_name}</code>"


def _relationship_chip(qualified_name: str, current_module: str) -> str:
    module_name, callable_name = _parts(qualified_name)
    return (
        f'<a class="reference-chip" href="{_callable_href(qualified_name)}" '
        f'title="{qualified_name}"><code>{callable_name if module_name == current_module else f"{module_name}.{callable_name}"}</code></a>'
    )


def _source_anchor(module_name: str, symbol_name: str) -> str:
    return f'<a href="../../modules/{module_name}/#{symbol_name}">{module_name} module</a>'

for row in sorted(public_symbol_docs, key=lambda item: item["symbol_name"]):
    if row.get("kind") not in {"function", "class"}:
        continue
    symbol_name = row["symbol_name"]
    module_name = row["module"]
    if symbol_name not in exports:
        raise RuntimeError(f"Metadata symbol not exported: {symbol_name}")
    if symbol_name not in modules.get(module_name, {}):
        raise RuntimeError(f"Public export missing required docs metadata/module ownership: {symbol_name} in {module_name}")
    doc_path = f"api/reference/{symbol_name}.md"
    qn = f"{PACKAGE}.{module_name}.{symbol_name}"
    dep = dependency_metadata.get("callables", {}).get(qn, {})
    dep_calls = sorted(dep.get("calls", []))
    dep_used_by = sorted(dep.get("used_by", []))
    calls = dep_calls or sorted(module_call_map.get(module_name, {}).get(symbol_name, set()))
    referenced_by = dep_used_by or sorted(reverse_refs.get(qn, set()))

    with mkdocs_gen_files.open(doc_path, "w") as fd:
        fd.write(f"# `{symbol_name}`\n\n")

        outbound_count = int(dep.get("calls_count", len(calls)))
        inbound_count = int(dep.get("used_by_count", len(referenced_by)))
        classification = str(dep.get("classification", row.get("function_type", "callable"))).capitalize()

        fd.write('<p class="reference-page-meta">')
        fd.write(f'Module: {_module_link(module_name)}')
        fd.write(" · ")
        fd.write(f'Classification: <span class="reference-chip reference-chip-role reference-chip-{classification.lower()}">{classification}</span>')
        fd.write("</p>\n\n")

        outbound_edges = sorted(set(calls))
        inbound_edges = sorted(set(referenced_by))
        purpose = row.get("purpose") or row.get("summary_override") or modules.get(module_name, {}).get(symbol_name, "") or "No summary available."
        fd.write("## Purpose\n\n")
        fd.write(f"{purpose}\n\n")
        fd.write("## At a glance\n\n")
        fd.write("| Item | Value |\n")
        fd.write("| --- | --- |\n")
        fd.write(f"| Module | {_module_link(module_name)} |\n")
        fd.write(f"| Classification | <span class=\"reference-chip reference-chip-role reference-chip-{classification.lower()}\">{classification}</span> |\n")
        fd.write(f"| Source file | <code>src/fabricops_kit/{module_name}.py</code> (<a href=\"../../modules/{module_name}/#{symbol_name}\">{module_name} module source</a>) |\n")
        fd.write(f"| Used by count | {inbound_count} |\n")
        fd.write(f"| Calls count | {outbound_count} |\n\n")

        fd.write('??? info "AI manifest"\n\n')
        fd.write("    ```yaml\n")
        fd.write(f"    name: {symbol_name}\n")
        fd.write(f"    qualified_name: {qn}\n")
        fd.write(f"    module: {module_name}\n")
        fd.write(f"    classification: {classification}\n")
        fd.write(f"    source_file: src/fabricops_kit/{module_name}.py\n")
        fd.write(f"    source_ref: ../../modules/{module_name}/#{symbol_name}\n")
        fd.write(f"    used_by_count: {inbound_count}\n")
        fd.write(f"    calls_count: {outbound_count}\n")
        fd.write("    ```\n\n")

        if inbound_edges:
            fd.write("\n## Used by\n")
            for c in inbound_edges[:30]:
                fd.write(f"- {_relationship_chip(c, module_name)}\n")
            fd.write("\n")
        if outbound_edges:
            fd.write("## Calls\n")
            for c in outbound_edges[:30]:
                fd.write(f"- {_relationship_chip(c, module_name)}\n")
            fd.write("\n")
        if not inbound_edges and not outbound_edges:
            fd.write("_No related function links detected._\n")

        fd.write('\n???+ note "Function details and source"\n\n')
        fd.write(f"    ::: {PACKAGE}.{module_name}.{symbol_name}\n")
        fd.write("        options:\n")
        fd.write("          show_root_heading: false\n")
        fd.write("          show_source: true\n")
        fd.write("          docstring_style: numpy\n")
        fd.write("          docstring_section_style: table\n")

for module_name, callable_docs in sorted(modules.items()):
    for helper_name in sorted(name for name in callable_docs if name.startswith("_")):
        helper_doc_path = f"api/reference/internal/{module_name}/{helper_name}.md"
        with mkdocs_gen_files.open(helper_doc_path, "w") as fd:
            fd.write(f"# `{helper_name}`\n\n")
            fd.write("Internal helper notice\n\n")
            fd.write(f"::: {PACKAGE}.{module_name}.{helper_name}\n")
            fd.write("    options:\n")
            fd.write("      show_root_heading: false\n")
            fd.write("      show_source: true\n")
            fd.write("      docstring_style: numpy\n")
            fd.write("      docstring_section_style: table\n")
