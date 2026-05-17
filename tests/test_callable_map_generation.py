from __future__ import annotations

import ast
from pathlib import Path

from scripts.generate_function_reference import main as generate_reference

ROOT = Path(__file__).resolve().parents[1]
INIT_FILE = ROOT / "src" / "fabricops_kit" / "__init__.py"
CALLABLE_MAP_FILE = ROOT / "docs" / "reference" / "callable-map.md"


def public_exports() -> list[str]:
    tree = ast.parse(INIT_FILE.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
            return [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant)]
    raise AssertionError("__all__ missing")


def test_callable_map_outputs_are_generated() -> None:
    generate_reference()
    assert CALLABLE_MAP_FILE.exists()


def test_callable_map_markdown_sections_present() -> None:
    generate_reference()
    content = CALLABLE_MAP_FILE.read_text(encoding="utf-8")
    assert "# Callable Map" in content
    assert "## 1. Module dependency graph" in content
    assert "```mermaid" in content
    assert "## 2. Module relationship summary" in content
    assert "## 3. Public callables grouped by module" in content
    assert "## 4. Internal helper index" in content
    assert "## 5. Cross-module FabricOps calls" in content
    assert "## 6. Module dependency summary" in content


def test_callable_map_excludes_iframe_and_script_tags() -> None:
    generate_reference()
    content = CALLABLE_MAP_FILE.read_text(encoding="utf-8")
    assert "<iframe" not in content
    assert "<script" not in content


def test_callable_map_contains_non_trivial_module_edges() -> None:
    generate_reference()
    content = CALLABLE_MAP_FILE.read_text(encoding="utf-8")
    assert (
        "data_quality --> metadata" in content
        or "fabric_input_output --> config" in content
    )


def test_callable_map_includes_relationship_tables() -> None:
    generate_reference()
    content = CALLABLE_MAP_FILE.read_text(encoding="utf-8")
    assert "| Module | Internal helper | Called by public callables |" in content
    assert "| Caller | Callee | Callee kind |" in content


def test_callable_map_excludes_noisy_calls() -> None:
    generate_reference()
    content = CALLABLE_MAP_FILE.read_text(encoding="utf-8")
    assert "widgets.Button" not in content
    assert "json.dumps" not in content
    assert ".append" not in content
    assert ".get" not in content
