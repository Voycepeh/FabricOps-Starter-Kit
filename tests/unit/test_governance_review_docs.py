"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

from fabricops_kit.pipeline import guardrails_shared as governance

pytestmark = pytest.mark.unit


def test_governance_review_page_frames_metadata_control_panel():
    """Verify governance review page preserves the governance flow contract."""
    text = Path("docs/notebook-templates-implementation-guide/governance-review.md").read_text(encoding="utf-8")
    normalized = text.lower()

    for required_term in (
        "02_pipeline",
        "03_governance",
        "METADATA_DATA_CATALOGUE",
        "METADATA_GUARDRAIL_RULES",
        "METADATA_GUARDRAIL_RESULTS",
    ):
        assert required_term in text

    assert "enforcement" in normalized
    assert "02_pipeline" in text[text.find("enforcement") if "enforcement" in text else 0 :]
    assert any(
        phrase in normalized
        for phrase in (
            "03_governance` lets reviewers",
            "guardrail decisions",
            "records governance decisions",
            "reviews table governance",
            "reviewers approve",
        )
    )
    assert any(
        concept in normalized
        for concept in ("augment", "enrich", "review", "record", "governance decisions")
    )
    assert "Approved DQ rule catalogue" not in text
    assert "**Rule applies to:**" not in text


def test_dq_rule_index_contains_supported_catalogue():
    """Verify dq rule index contains supported catalogue."""
    text = Path("docs/reference/dq-rules/index.md").read_text(encoding="utf-8")
    assert f"{len(governance.DQ_RULE_TYPES)} native DQ rule types" in text
    for rule_type in governance.DQ_RULE_TYPES:
        assert f"`{rule_type}`" in text
    assert "Great Expectations or dbt" in text
    assert "METADATA_GUARDRAIL_RULES" in text


def test_dq_rule_reference_pages_exist_for_supported_catalogue():
    """Verify dq rule reference pages exist for supported catalogue."""
    docs_dir = Path("docs/reference/dq-rules")
    mkdocs_text = Path("mkdocs.yml").read_text(encoding="utf-8")
    assert f"{len(governance.DQ_RULE_TYPES)} native DQ rule types" in docs_dir.joinpath("index.md").read_text(encoding="utf-8")

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
