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
