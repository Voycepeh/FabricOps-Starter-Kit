"""Focused tests for governed AI-assisted DQ authoring."""

import json

import pytest

from fabricops_kit.config.shared import GovernanceConfig
from fabricops_kit.widgets.enrichment_shared import build_ai_dq_context, suggest_dq_rules


def _context():
    return build_ai_dq_context({
        "table_id": "orders", "table_name": "orders", "schema_name": "sales",
        "catalogue_profile_rows": [{
            "column_id": "col-1", "column_name": "order_id", "data_type": "string",
            "description": "Order identifier", "row_count": 10, "null_count": 0,
            "distinct_count": 10, "frequency_evidence": [{"count": 1}],
        }],
    })


def test_dq_ai_config_merges_user_prompts_with_conservative_defaults():
    """User family prompts override defaults without removing other families."""
    config = GovernanceConfig(ai_enrichment={"enabled": True, "dq_prompts": {"range": "Project range policy"}})
    assert config.ai_enrichment["dq_prompts"]["range"] == "Project range policy"
    assert set(config.ai_enrichment["dq_prompts"]) == {
        "completeness", "uniqueness", "value_set", "range", "pattern", "compare",
    }


def test_dq_context_contains_profile_evidence_but_not_internal_identifiers():
    """The assistant receives governed profile evidence rather than raw identifiers."""
    context = _context()
    assert context["columns"][0]["profile_evidence"]["distinct_count"] == 10
    assert "column_id" not in context["columns"][0]


def test_dq_ai_uses_configured_prompts_and_validates_transient_result():
    """Configured prompts are passed through and valid structured output is returned."""
    prompts = GovernanceConfig().ai_enrichment["dq_prompts"]
    captured = []
    result = suggest_dq_rules(_context(), prompts=prompts, invoke=lambda prompt: captured.append(prompt) or json.dumps([{
        "rule_type": "uniqueness", "columns": ["order_id"], "parameters": {},
        "reason": "The description identifies an order identifier.", "selected": True,
    }]))
    assert result[0]["reason"].startswith("The description")
    assert prompts["uniqueness"] in captured[0]
    assert "persisted" in captured[0]


@pytest.mark.parametrize("candidate", [
    {"rule_type": "required_when", "columns": ["order_id"], "parameters": {}},
    {"rule_type": "uniqueness", "columns": ["missing_column"], "parameters": {}},
])
def test_dq_ai_rejects_removed_types_and_unknown_columns(candidate):
    """Unrecognized rule families and Catalogue columns are rejected."""
    with pytest.raises(ValueError):
        suggest_dq_rules(
            _context(), prompts=GovernanceConfig().ai_enrichment["dq_prompts"],
            invoke=lambda _prompt: json.dumps([candidate]),
        )
