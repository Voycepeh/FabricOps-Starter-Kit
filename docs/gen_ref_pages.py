"""Generate non-public helper pages for MkDocs builds.

Public callable reference pages are committed generated artifacts under
``docs/api/reference/<function>.md``. This hook intentionally does not generate
public callable pages so MkDocs cannot create a duplicate virtual page or
overwrite the canonical layout during a build.
"""
from __future__ import annotations

import ast
from pathlib import Path

import mkdocs_gen_files

PACKAGE = "fabricops_kit"
PKG_DIR = Path(__file__).resolve().parents[1] / "src" / PACKAGE
SKIPPED_PACKAGE_MODULE_FILES = {"__init__.py"}


def _build_module_members() -> dict[str, set[str]]:
    """Return top-level documented members by source module."""
    module_members: dict[str, set[str]] = {}
    for path in sorted(PKG_DIR.glob("*.py")):
        if path.name in SKIPPED_PACKAGE_MODULE_FILES:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        module_members[path.stem] = {
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        }
    return module_members


modules = _build_module_members()

for module_name, callable_names in sorted(modules.items()):
    for helper_name in sorted(name for name in callable_names if name.startswith("_")):
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
