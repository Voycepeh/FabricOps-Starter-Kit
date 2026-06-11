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


def _signature_from_node(node: ast.AST, source_text: str) -> str:
    """Return the source signature line for a function or class node."""
    segment = ast.get_source_segment(source_text, node) or ""
    if isinstance(node, ast.ClassDef):
        for line in segment.splitlines():
            stripped = line.strip()
            if stripped.startswith("class "):
                return stripped.rstrip(":")
        return f"class {node.name}"
    header_lines: list[str] = []
    for line in segment.splitlines():
        header_lines.append(line.strip())
        if line.rstrip().endswith(":"):
            break
    return " ".join(header_lines).rstrip(":")


def _parse_exports() -> set[str]:
    tree = ast.parse((PKG_DIR / "__init__.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
            if isinstance(node.value, ast.List):
                return {elt.value for elt in node.value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)}
    raise RuntimeError("Missing __all__")


def _build_index():
    modules: dict[str, dict[str, str]] = {}
    source_metadata: dict[str, dict[str, dict[str, str | int | None]]] = {}
    imports: dict[str, tuple[dict[str, str], dict[str, str]]] = {}
    for p in sorted(PKG_DIR.glob("*.py")):
        if p.name in SKIPPED_PACKAGE_MODULE_FILES:
            continue
        source_text = p.read_text(encoding="utf-8")
        tree = ast.parse(source_text)
        mod = p.stem
        functions = {}
        source_metadata[mod] = {}
        for n in tree.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                functions[n.name] = _first_sentence(ast.get_docstring(n))
                source_metadata[mod][n.name] = {
                    "signature": _signature_from_node(n, source_text),
                    "source": ast.get_source_segment(source_text, n),
                    "start_line": getattr(n, "lineno", None),
                    "end_line": getattr(n, "end_lineno", None),
                }
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
    return modules, source_metadata, imports


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
modules, source_metadata, imports = _build_index()
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


def _direct_calls(qualified_name: str) -> list[str]:
    module_name, callable_name = _parts(qualified_name)
    manifest_calls = dependency_metadata.get("callables", {}).get(qualified_name, {}).get("calls", [])
    fallback_calls = module_call_map.get(module_name, {}).get(callable_name, set())
    return sorted(set(manifest_calls or fallback_calls))


def _is_internal_helper(qualified_name: str) -> bool:
    _, callable_name = _parts(qualified_name)
    return callable_name.startswith("_") or callable_name not in exports


def _collect_internal_helpers(qualified_name: str) -> list[str]:
    helpers: set[str] = set()
    visited: set[str] = set()

    def visit(current_qn: str) -> None:
        if current_qn in visited:
            return
        visited.add(current_qn)
        for child_qn in _direct_calls(current_qn):
            if child_qn not in visited:
                if _is_internal_helper(child_qn):
                    helpers.add(child_qn)
                visit(child_qn)

    visit(qualified_name)
    return sorted(helpers, key=lambda item: (_parts(item)[0], _parts(item)[1]))


def _render_call_flow(qualified_name: str, *, max_depth: int = 6) -> str:
    _, root_name = _parts(qualified_name)
    lines = [f"{root_name}(...)"]

    def children(current_qn: str) -> list[str]:
        return sorted(
            _direct_calls(current_qn),
            key=lambda item: (0 if _is_internal_helper(item) else 1, _parts(item)[1].lower(), item),
        )

    def visit(current_qn: str, prefix: str, ancestors: set[str], depth: int) -> None:
        child_qns = children(current_qn)
        if depth >= max_depth:
            if child_qns:
                lines.append(f"{prefix}└── …")
            return
        for index, child_qn in enumerate(child_qns):
            _, child_name = _parts(child_qn)
            connector = "└── " if index == len(child_qns) - 1 else "├── "
            suffix = " (recursive)" if child_qn in ancestors else ""
            lines.append(f"{prefix}{connector}{child_name}(...){suffix}")
            if child_qn not in ancestors:
                extension = "    " if index == len(child_qns) - 1 else "│   "
                visit(child_qn, prefix + extension, ancestors | {child_qn}, depth + 1)

    visit(qualified_name, "", {qualified_name}, 0)
    return "```text\n" + "\n".join(lines) + "\n```"


def _render_internal_helper_details(root_qn: str) -> list[str]:
    _, root_name = _parts(root_qn)
    helper_qns = _collect_internal_helpers(root_qn)
    if not helper_qns:
        return ["_No internal helper calls detected._"]

    lines: list[str] = []
    for helper_qn in helper_qns:
        helper_module, helper_name = _parts(helper_qn)
        metadata = source_metadata.get(helper_module, {}).get(helper_name, {})
        signature = str(metadata.get("signature") or f"{helper_name}(...)")
        source_path = f"src/{PACKAGE}/{helper_module}.py"
        start_line = metadata.get("start_line")
        end_line = metadata.get("end_line")
        line_suffix = f" lines {start_line}-{end_line}" if start_line and end_line else ""
        source = str(metadata.get("source") or "")
        purpose = modules.get(helper_module, {}).get(helper_name) or "Internal helper used by the package implementation."
        lines.extend(
            [
                f"### `{signature}`",
                "",
                purpose,
                "",
                "**Helper source path**",
                "",
                f"- `{source_path}`{line_suffix}",
                "",
                "**Helper code excerpt**",
                "",
                "```python",
                source or "# Source excerpt unavailable.",
                "```",
                "",
                "**Used here because**",
                "",
                f"`{root_name}` reaches `{helper_name}` in its implementation path.",
                "",
                "**Modify this if**",
                "",
                f"Change `{helper_name}` when the shared implementation behavior it provides to `{root_name}` or another caller needs to change.",
                "",
            ]
        )
    return lines


def _render_implementation_details(root_qn: str) -> list[str]:
    return [
        "## Implementation details",
        "",
        "### Call flow",
        "",
        _render_call_flow(root_qn),
        "",
        "### Internal helpers used by this callable",
        "",
        *_render_internal_helper_details(root_qn),
    ]


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

        for implementation_line in _render_implementation_details(qn):
            fd.write(f"{implementation_line}\n")

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
