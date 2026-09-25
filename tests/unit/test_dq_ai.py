"""Tests for governed, transient AI Data Quality suggestions."""

import json

import pytest

from fabricops_kit.widgets.enrichment_shared import (
    build_ai_business_rule_context,
    build_ai_dq_context,
    suggest_business_rule,
    suggest_dq_rules,
    suggest_grain_key,
)

pytestmark = pytest.mark.unit


def _context():
    return build_ai_dq_context({
        "table_id": "internal-id-not-sent",
        "table_name": "orders",
        "schema_name": "sales",
        "layer": "Silver",
        "catalogue_profile_rows": [{
            "column_id": "internal-column-id",
            "column_name": "amount",
            "data_type": "decimal",
            "null_percent": 0,
            "min_value": 0,
            "max_value": 100,
            "frequency_evidence": [{"value": "governed", "count": 2}],
        }],
    })


def test_ai_dq_context_excludes_internal_identifiers_and_raw_rows():
    """Send governed evidence without internal identifiers or raw rows."""
    context = _context()
    text = json.dumps(context)
    assert "internal-id-not-sent" not in text
    assert "internal-column-id" not in text
    assert "raw" not in context["columns"][0]


def test_ai_dq_suggestions_preserve_all_structured_parameters_and_prompt():
    """Preserve every validated parameter and merge configured instructions."""
    captured = {}
    payload = [
        {"rule_type": "completeness", "columns": ["amount"], "parameters": {"maximum_missing_percent": 1, "treat_blank_as_missing": False}, "rationale": "semantic", "selected": True},
        {"rule_type": "value_set", "columns": ["amount"], "parameters": {"mode": "block", "values": [-1]}, "rationale": "sentinel", "selected": False},
        {"rule_type": "range", "columns": ["amount"], "parameters": {"minimum": 0, "maximum": 100, "minimum_inclusive": True, "maximum_inclusive": False}, "rationale": "defined scale", "selected": True},
        {"rule_type": "pattern", "columns": ["amount"], "parameters": {"pattern": "^[0-9]+$"}, "rationale": "structured", "selected": True},
    ]

    def invoke(prompt):
        captured["prompt"] = prompt
        return json.dumps(payload)

    result = suggest_dq_rules(_context(), prompt="Configured governance prompt", invoke=invoke)
    assert result == payload
    assert "Configured governance prompt" in captured["prompt"]
    assert "Allowed rule_type values: completeness, value_set, range, pattern." in captured["prompt"]


def test_ai_dq_ignores_noncanonical_extra_parameters():
    """Ignore extra model-authored fields while preserving canonical DQ inputs."""
    payload = [{
        "rule_type": "pattern",
        "columns": ["amount"],
        "parameters": {
            "pattern": "^[0-9]+$",
            "case_sensitive": True,
            "description": "Digits only",
        },
        "rationale": "Structured identifier.",
        "selected": True,
    }]

    result = suggest_dq_rules(
        _context(), prompt="configured", invoke=lambda _prompt: json.dumps(payload)
    )

    assert result[0]["parameters"] == {"pattern": "^[0-9]+$"}


@pytest.mark.parametrize("rule_type", ["uniqueness", "column_relationship", "custom_expression", "compare", "required_when"])
def test_ai_dq_rejects_nonstandard_families(rule_type):
    """Keep relationship and custom logic outside AI standard suggestions."""
    raw = json.dumps([{"rule_type": rule_type, "columns": ["amount"], "parameters": {}}])
    with pytest.raises(ValueError, match="unsupported rule_type"):
        suggest_dq_rules(_context(), prompt="configured", invoke=lambda _prompt: raw)


def test_ai_dq_rejects_unknown_columns_composite_and_malformed_parameters():
    """Reject suggestions that cannot safely hydrate column controls."""
    cases = [
        [{"rule_type": "pattern", "columns": ["unknown"], "parameters": {"pattern": "x"}}],
        [{"rule_type": "value_set", "columns": ["amount", "other"], "parameters": {"mode": "allow", "values": [1]}}],
        [{"rule_type": "range", "columns": ["amount"], "parameters": {"minimum": 0, "minimum_inclusive": True}}],
        [{"rule_type": "completeness", "columns": ["amount"], "parameters": {"maximum_missing_percent": 0}}],
    ]
    for payload in cases:
        with pytest.raises(ValueError):
            suggest_dq_rules(_context(), prompt="configured", invoke=lambda _prompt, value=payload: json.dumps(value))


def test_ai_grain_key_preserves_candidate_and_warns_about_composite_proof():
    """Keep grain/key advice transient and distinguish profile evidence from validation."""
    context = {
        "table_name": "orders",
        "columns": [
            {"column_name": "order_id", "distinct_percent": 100.0, "null_percent": 0.0},
            {"column_name": "line_id", "distinct_percent": 20.0, "null_percent": 0.0},
        ],
    }
    captured = {}
    payload = {
        "grain": "One row per order line",
        "key_columns": ["order_id", "line_id"],
        "rationale": "Candidate composite key",
    }

    def invoke(prompt):
        captured["prompt"] = prompt
        return json.dumps(payload)

    assert suggest_grain_key(context, prompt="configured", invoke=invoke) == payload
    assert "cannot prove composite uniqueness" in captured["prompt"]


def _business_context():
    return build_ai_business_rule_context({
        "table_name": "orders",
        "schema_name": "sales",
        "layer": "Silver",
        "table_description": "One row per order",
        "columns": [
            {"column_name": "start_date", "data_type": "date", "description": "Start"},
            {"column_name": "end_date", "data_type": "date", "description": "End"},
            {"column_name": "status", "data_type": "string", "description": "Status"},
        ],
    })


def test_business_rule_resolver_prefers_known_column_relationship():
    """Resolve an exact two-column comparison to the canonical known pattern."""
    captured = {}
    payload = {
        "rule_type": "column_relationship",
        "columns": ["end_date", "start_date"],
        "parameters": {"operator": ">="},
        "rationale": "Direct row-by-row comparison.",
    }

    def invoke(prompt):
        captured["prompt"] = prompt
        return json.dumps(payload)

    result = suggest_business_rule(
        _business_context(),
        requirement="End date must be on or after start date.",
        relevant_columns=["start_date", "end_date"],
        prompt="Prefer known FabricOps patterns.",
        invoke=invoke,
    )

    assert result["rule_type"] == "column_relationship"
    assert result["engineering_review_required"] is False
    assert result["parameters"] == {
        "columns": ["end_date", "start_date"],
        "operator": ">=",
        "business_requirement": "End date must be on or after start date.",
    }
    assert "Always prefer column_relationship" in captured["prompt"]


def test_business_rule_resolver_flags_custom_expression_for_engineering_review():
    """Keep custom logic in the existing DQ model while marking it for later review."""
    payload = {
        "rule_type": "custom_expression",
        "columns": ["status", "end_date"],
        "parameters": {
            "expression_language": "pyspark",
            "expression": '(F.col("status") != "Closed") | F.col("end_date").isNotNull()',
        },
        "rationale": "Conditional relationship.",
    }

    result = suggest_business_rule(
        _business_context(),
        requirement="When status is Closed, end date must be populated.",
        relevant_columns=["status", "end_date"],
        prompt="Prefer known FabricOps patterns.",
        invoke=lambda _prompt: json.dumps(payload),
    )

    assert result["rule_type"] == "custom_expression"
    assert result["engineering_review_required"] is True
    assert result["parameters"]["engineering_review_required"] is True
    assert result["parameters"]["business_requirement"] == (
        "When status is Closed, end date must be populated."
    )


def test_business_rule_resolver_rejects_columns_outside_governance_selection():
    """Relevant-column selection is a hard boundary for the AI proposal."""
    payload = {
        "rule_type": "column_relationship",
        "columns": ["end_date", "status"],
        "parameters": {"operator": ">="},
    }

    with pytest.raises(ValueError, match="outside the selected relevant columns"):
        suggest_business_rule(
            _business_context(),
            requirement="End date must be on or after start date.",
            relevant_columns=["start_date", "end_date"],
            prompt="configured",
            invoke=lambda _prompt: json.dumps(payload),
        )
