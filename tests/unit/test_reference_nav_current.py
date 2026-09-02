"""Navigation contract tests for the current public documentation structure."""

from pathlib import Path


ROOT = Path(__file__).parents[2]


def test_resources_reference_nav_matches_current_structure() -> None:
    """Verify reference pages remain grouped under Resources & Reference."""
    mkdocs_text = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "  - Resources & Reference:" in mkdocs_text
    assert "      - Notebook Templates: notebook-templates.md" in mkdocs_text
    assert "      - FabricOps Engineering Guide: reference/engineering-cheat-sheet.md" in mkdocs_text
    assert "      - Glossary: glossary.md" in mkdocs_text
    assert "      - Metadata Tables:" in mkdocs_text
    assert "          - Overview: reference/metadata.md" in mkdocs_text
    assert "      - Functions:" in mkdocs_text
    assert "          - Function Reference: reference/index.md" in mkdocs_text
    assert "          - Call Flow Dashboard: assets/public-function-call-flows-dashboard.html" in mkdocs_text
    assert "          - Function Call Graph: function-call-graph.md" in mkdocs_text
    assert "      - DQ Rules:" in mkdocs_text
    assert "          - Overview: reference/dq-rules/index.md" in mkdocs_text
    assert "api/reference/" not in mkdocs_text
