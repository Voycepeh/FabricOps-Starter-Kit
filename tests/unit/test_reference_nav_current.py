"""Navigation contract tests for the current public documentation structure."""

from pathlib import Path


ROOT = Path(__file__).parents[2]


def test_resources_reference_nav_matches_current_structure() -> None:
    """Verify download/use assets and reference docs remain clearly grouped."""
    mkdocs_text = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "  - Download FabricOps:" in mkdocs_text
    assert "      - Releases (Python package):" in mkdocs_text
    assert (
        "      - Notebook Templates: "
        "https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks"
        in mkdocs_text
    )
    assert (
        "      - Demo Assets: "
        "https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/DemoData"
        in mkdocs_text
    )
    assert "  - Reference Documentation:" in mkdocs_text
    assert "      - Function Reference: reference/index.md" in mkdocs_text
    assert "      - Data Quality Rules:" in mkdocs_text
    assert "          - Overview: reference/dq-rules/index.md" in mkdocs_text
    assert "      - Metadata Tables:" in mkdocs_text
    assert "          - Overview: reference/metadata.md" in mkdocs_text
    assert "      - Glossary: glossary.md" in mkdocs_text
    assert "      - Call Flow: function-call-graph.md" not in mkdocs_text
    assert "      - FabricOps Engineering: reference/engineering-cheat-sheet.md" not in mkdocs_text
    assert "      - Call Flow Dashboard Architecture: function-call-graph.md" in mkdocs_text
    assert "      - Functions:" not in mkdocs_text
    assert "Call Flow Dashboard: assets/public-function-call-flows-dashboard.html" not in mkdocs_text
    assert "api/reference/" not in mkdocs_text
