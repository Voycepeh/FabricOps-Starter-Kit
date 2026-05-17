"""Generate callable reference pages for MkDocs build."""
from __future__ import annotations

import ast
from pathlib import Path

import mkdocs_gen_files

PACKAGE = "fabricops_kit"
PKG_DIR = Path(__file__).resolve().parents[1] / "src" / PACKAGE
DOCS_METADATA_PATH = PKG_DIR / "docs_metadata.py"
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
        if p.name in {"__init__.py", "docs_metadata.py"}:
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
        if p.name in {"__init__.py", "docs_metadata.py"}:
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
    dep_internal_helpers = sorted(dep.get("internal_helpers_used", []))
    calls = dep_calls or sorted(module_call_map.get(module_name, {}).get(symbol_name, set()))
    helper_calls = dep_internal_helpers or [c for c in calls if c.startswith(f"{PACKAGE}.{module_name}._")]
    cross = [c for c in calls if c.startswith(f"{PACKAGE}.") and not c.startswith(f"{PACKAGE}.{module_name}.")]
    referenced_by = dep_used_by or sorted(reverse_refs.get(qn, set()))

    with mkdocs_gen_files.open(doc_path, "w") as fd:
        fd.write(f"# `{symbol_name}`\n\n")

        calls_count = int(dep.get("calls_count", len(calls)))
        used_by_count = int(dep.get("used_by_count", len(referenced_by)))
        internal_helper_count = int(dep.get("internal_helper_count", len(helper_calls)))
        classification = str(dep.get("classification", row.get("role", "optional"))).capitalize()

        fd.write("## Dependency metadata\n\n")
        fd.write(f"- Module: `{module_name}`\n")
        fd.write(f"- Classification: {classification}\n")
        fd.write(f"- Calls: {calls_count}\n")
        fd.write(f"- Used By: {used_by_count}\n")
        fd.write(f"- Internal Helpers: {internal_helper_count}\n\n")

        def link(c):
            m, n = c.split(".")[-2], c.split(".")[-1]
            if n in exports:
                return f"[`{n}`](../{n}/)"
            return f"[`{n}`](../internal/{m}/{n}/)"

        def _dep_details(title: str, items: list[str]) -> None:
            fd.write(f"<details>\n<summary>{title}</summary>\n\n")
            if not items:
                fd.write("None\n")
            else:
                for item in items:
                    fd.write(f"- {link(item)}\n")
            fd.write("\n</details>\n\n")

        _dep_details("Calls", calls)
        _dep_details("Used By", referenced_by)
        _dep_details("Internal Helpers Used", helper_calls)

        has_relationships = bool(helper_calls or cross or referenced_by)
        flow_edges = helper_calls + cross
        relationship_rows = []
        if helper_calls:
            relationship_rows.append(("Internal helpers used", ', '.join(link(c) for c in helper_calls)))
        if cross:
            relationship_rows.append(("Cross-module FabricOps calls", ', '.join(link(c) for c in cross)))
        if referenced_by:
            referenced_by_links: list[str] = []
            for c in referenced_by:
                m, n = c.split(".")[-2], c.split(".")[-1]
                if n in exports:
                    referenced_by_links.append(f"[`{n}`](../{n}/)")
                else:
                    referenced_by_links.append(f"`{PACKAGE}.{m}.{n}`")
            relationship_rows.append(("Referenced by", ', '.join(referenced_by_links)))

        src_to_dst = {}
        dst_from_src = {}
        for edge in flow_edges:
            src_to_dst.setdefault(symbol_name, set()).add(edge)
            dst_from_src.setdefault(edge, set()).add(symbol_name)
        show_mermaid = any(len(v) >= 2 for v in src_to_dst.values()) or any(len(v) >= 2 for v in dst_from_src.values())

        if show_mermaid and flow_edges:
            fd.write("## Callable flow\n\n")
            fd.write("```mermaid\nflowchart TD\n")
            for target in flow_edges[:20]:
                fd.write(f"  {symbol_name} --> {target.split('.')[-1]}\n")
            fd.write("```\n\n")

        if relationship_rows:
            fd.write("## Callable relationships\n\n| Relationship | Callables |\n|---|---|\n")
            for label, values in relationship_rows:
                fd.write(f"| {label} | {values} |\n")
            fd.write("\n")

        if flow_edges:
            fd.write("## Function flow details\n\n| Step | Callable | Purpose |\n|---:|---|---|\n")
            for i, c in enumerate(flow_edges[:20], start=1):
                m, n = c.split(".")[-2], c.split(".")[-1]
                purpose = modules.get(m, {}).get(n) or n.replace("_", " ").capitalize()
                fd.write(f"| {i} | {link(c)} | {purpose} |\n")
            fd.write("\n")

        fd.write(f"::: {PACKAGE}.{module_name}.{symbol_name}\n")
        fd.write("    options:\n")
        fd.write("      show_root_heading: false\n")
        fd.write("      show_source: true\n")
        fd.write("      docstring_style: numpy\n")
        fd.write("      docstring_section_style: table\n")

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
