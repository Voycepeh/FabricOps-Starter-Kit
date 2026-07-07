"""Test standalone Function Call Graph documentation ownership."""

from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_function_call_graph_is_root_owned_and_not_generated() -> None:
    """Verify the guide is top-level documentation and not generator-owned."""
    generator_path = ROOT / "scripts/generate_individual_function_reference_pages.py"
    generator = generator_path.read_text(encoding="utf-8")
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    homepage = (ROOT / "docs/index.md").read_text(encoding="utf-8")

    assert (ROOT / "docs/function-call-graph.md").exists()
    assert "FUNCTION_CALL_GRAPH_PAGE_PATH" not in generator
    assert "def _render_callable_flow_page" not in generator
    assert "Function Call Graph: function-call-graph.md" in mkdocs
    assert "Function Call Graph: reference/function-call-graph.md" not in mkdocs
    assert 'href="function-call-graph/"' in homepage
