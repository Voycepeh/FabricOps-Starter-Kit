"""Contracts for the lightweight DQ rule documentation."""

from pathlib import Path

from fabricops_kit.pipeline import shared as governance


def test_dq_rule_index_contains_exact_supported_catalogue():
    """Keep the human-facing index aligned with the canonical runtime vocabulary."""
    text = Path("docs/reference/dq-rules/index.md").read_text(encoding="utf-8")
    assert f"{len(governance.DQ_RULE_TYPES)} lightweight DQ rule types" in text
    for rule_type in governance.DQ_RULE_TYPES:
        assert f"`{rule_type}`" in text
    assert "METADATA_GUARDRAIL" in text
    assert "arbitrary Python" in text
    assert "Freshness is a dedicated guardrail" in text


def test_only_supported_rule_pages_are_in_current_navigation():
    """Remove obsolete rule pages and navigation entries rather than keeping aliases."""
    docs_dir = Path("docs/reference/dq-rules")
    mkdocs_text = Path("mkdocs.yml").read_text(encoding="utf-8")
    expected_pages = {rule_type.replace("_", "-") + ".md" for rule_type in governance.DQ_RULE_TYPES}
    actual_pages = {path.name for path in docs_dir.glob("*.md")} - {"index.md"}

    assert actual_pages == expected_pages
    for page_name in expected_pages:
        assert f"reference/dq-rules/{page_name}" in mkdocs_text
