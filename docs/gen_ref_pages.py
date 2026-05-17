"""Generate callable reference pages for MkDocs build."""
from __future__ import annotations

import ast
from pathlib import Path

import mkdocs_gen_files

PACKAGE = "fabricops_kit"
PKG_DIR = Path(__file__).resolve().parents[1] / "src" / PACKAGE
DOCS_METADATA_PATH = PKG_DIR / "docs_metadata.py"


def _read_literal(path: Path, name: str):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        is_assign = isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)
        is_ann = isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name
        if (is_assign or is_ann) and node.value is not None:
            return ast.literal_eval(node.value)
    raise RuntimeError(f"Missing literal {name} in {path}")


def _load_internal_helpers() -> dict[str, list[str]]:
    module_helpers: dict[str, list[str]] = {}
    for module_path in sorted(PKG_DIR.glob("*.py")):
        if module_path.name in {"__init__.py", "docs_metadata.py"}:
            continue
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        helpers = sorted(
            node.name
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name.startswith("_")
        )
        if helpers:
            module_helpers[module_path.stem] = helpers
    return module_helpers


def _module_calls() -> dict[str, dict[str, set[str]]]:
    call_map: dict[str, dict[str, set[str]]] = {}
    for module_path in sorted(PKG_DIR.glob("*.py")):
        if module_path.name in {"__init__.py", "docs_metadata.py"}:
            continue
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        module_name = module_path.stem
        module_functions = {
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        fn_calls: dict[str, set[str]] = {}
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            calls: set[str] = set()
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name):
                        name = child.func.id
                        if name in module_functions:
                            calls.add(f"{PACKAGE}.{module_name}.{name}")
                    elif isinstance(child.func, ast.Attribute) and isinstance(child.func.value, ast.Name):
                        owner = child.func.value.id
                        member = child.func.attr
                        calls.add(f"{PACKAGE}.{owner}.{member}")
            fn_calls[node.name] = calls
        call_map[module_name] = fn_calls
    return call_map


public_symbol_docs = _read_literal(DOCS_METADATA_PATH, "PUBLIC_SYMBOL_DOCS")
internal_helpers_by_module = _load_internal_helpers()
module_call_map = _module_calls()
reverse_refs: dict[str, set[str]] = {}
for module_name, fn_rows in module_call_map.items():
    for caller, callees in fn_rows.items():
        caller_qn = f"{PACKAGE}.{module_name}.{caller}"
        for callee_qn in callees:
            reverse_refs.setdefault(callee_qn, set()).add(caller_qn)

for row in sorted(public_symbol_docs, key=lambda item: item["symbol_name"]):
    if row.get("kind") not in {"function", "class"}:
        continue
    symbol_name = row["symbol_name"]
    module_name = row["module"]
    doc_path = f"api/reference/{symbol_name}.md"
    with mkdocs_gen_files.open(doc_path, "w") as fd:
        fd.write(f"# `{symbol_name}`\n\n")
        fd.write(
            f"- **Template notebook:** `{row.get('template_notebook') or '—'}`\n"
            f"- **Template segment:** {row.get('template_segment') or '—'}\n"
            f"- **Role:** `{row.get('role') or 'optional'}`\n"
            f"- **Module:** `{module_name}`\n\n"
        )
        fd.write("## Callable relationships\n\n")
        symbol_qn = f"{PACKAGE}.{module_name}.{symbol_name}"
        symbol_calls = module_call_map.get(module_name, {}).get(symbol_name, set())
        helper_calls = sorted(c for c in symbol_calls if c.startswith(f"{PACKAGE}.{module_name}._"))
        cross_module_calls = sorted(c for c in symbol_calls if c.startswith(f"{PACKAGE}.") and not c.startswith(f"{PACKAGE}.{module_name}."))
        referenced_by = sorted(reverse_refs.get(symbol_qn, set()))
        if helper_calls or cross_module_calls or referenced_by:
            fd.write("| Relationship | Callables |\n")
            fd.write("|---|---|\n")
            fd.write(f"| Internal helpers used | {', '.join(f'`{c}`' for c in helper_calls) or '—'} |\n")
            fd.write(f"| Cross-module calls | {', '.join(f'`{c}`' for c in cross_module_calls) or '—'} |\n")
            fd.write(f"| Referenced by | {', '.join(f'`{c}`' for c in referenced_by) or '—'} |\n\n")
        fd.write("See the static [Callable Map](../../../reference/callable-map/) for module dependencies, helper relationships, and cross-module calls.\n\n")
        fd.write(f"::: {PACKAGE}.{module_name}.{symbol_name}\n")
        fd.write("    options:\n")
        fd.write("      show_root_heading: false\n")
        fd.write("      show_source: true\n")
        fd.write("      docstring_style: numpy\n")
        fd.write("      docstring_section_style: table\n")


for module_name, helpers in internal_helpers_by_module.items():
    for helper_name in helpers:
        doc_path = f"api/reference/internal/{module_name}/{helper_name}.md"
        with mkdocs_gen_files.open(doc_path, "w") as fd:
            fd.write(f"# `{helper_name}`\n\n")
            fd.write('<div class="api-status-block">\n')
            fd.write('  <span class="api-chip api-chip-internal">Internal helper</span>\n')
            fd.write('  <div class="api-chip-subtitle">This page documents an internal implementation helper, not a primary public API.</div>\n')
            fd.write('</div>\n\n')
            fd.write(f"::: {PACKAGE}.{module_name}.{helper_name}\n")
            fd.write("    options:\n")
            fd.write("      show_root_heading: false\n")
            fd.write("      show_source: true\n")
            fd.write("      docstring_style: numpy\n")
            fd.write("      docstring_section_style: table\n")

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as fd:
    fd.write("- [Reference Home](index.md)\n")
    if internal_helpers_by_module:
        fd.write("- Internal Helpers\n")
        for module_name, helpers in sorted(internal_helpers_by_module.items()):
            fd.write(f"  - {module_name}\n")
            for helper_name in helpers:
                fd.write(f"    - [{helper_name}](../api/reference/internal/{module_name}/{helper_name}.md)\n")
