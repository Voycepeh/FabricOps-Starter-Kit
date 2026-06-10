from __future__ import annotations

from pathlib import Path

import pytest

import fabricops_kit.governance_review as governance

pytestmark = pytest.mark.unit


def test_governance_review_page_documents_dq_catalogue_and_boundaries():
    text = Path("docs/how-fabricops-works/governance-review.md").read_text(encoding="utf-8")
    assert "Approved DQ rule catalogue" in text
    for rule_type in governance.DQ_RULE_TYPES:
        assert f"`{rule_type}`" in text
    assert "`value_when`" in text
    assert "severity=\"error\"" in text
    assert "severity=\"warning\"" in text
    assert "Schema guardrails are separate" in text
    assert "Source stability is separate" in text


def test_dq_rule_reference_pages_exist_for_supported_catalogue():
    docs_dir = Path("docs/reference/dq-rules")
    mkdocs_text = Path("mkdocs.yml").read_text(encoding="utf-8")
    assert "23 native DQ rule types" in docs_dir.joinpath("index.md").read_text(encoding="utf-8")

    for rule_type in governance.DQ_RULE_TYPES:
        page_name = rule_type.replace("_", "-") + ".md"
        page_path = docs_dir / page_name
        assert page_path.exists(), f"Missing DQ rule reference page for {rule_type}"
        page_text = page_path.read_text(encoding="utf-8")
        assert f"rule_type: {rule_type}" in page_text
        applies_section = page_text.split("## Rule applies to", 1)[1].split("## Parameters", 1)[0]
        assert "Data applicability:" in applies_section
        assert "Example column(s) on this page:" in applies_section
        assert not applies_section.strip().startswith("`")
        for heading in (
            "What this rule does",
            "When to use it",
            "Rule applies to",
            "Parameters",
            "Example rule definition",
            "Sample input data",
            "Rows that pass",
            "Rows that fail",
            "Notes",
            "Related rules",
        ):
            assert f"## {heading}" in page_text
        assert f"reference/dq-rules/{page_name}" in mkdocs_text

    expression_text = docs_dir.joinpath("expression-true.md").read_text(encoding="utf-8")
    assert "expression_true — Custom expression" in expression_text
