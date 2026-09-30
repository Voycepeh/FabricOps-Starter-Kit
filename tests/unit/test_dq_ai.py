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


def test_ai_grain_uses_profiled_key_without_asking_model_to_choose_it():
    """Keep key discovery deterministic and ask AI only for business grain wording."""
    context = {
        "table_name": "orders",
        "profile_key_candidates": [{
            "columns": ["order_id", "line_id"],
            "uniqueness_percent": 100.0,
            "null_count": 0,
        }],
        "columns": [
            {"column_name": "order_id", "distinct_percent": 50.0, "null_percent": 0.0},
            {"column_name": "line_id", "distinct_percent": 20.0, "null_percent": 0.0},
        ],
    }
    captured = {}
    payload = {
        "grain": "One row represents a single product line within an order.",
        "rationale": "The profiled key indicates order-line grain.",
    }

    def invoke(prompt):
        captured["prompt"] = prompt
        return json.dumps(payload)

    result = suggest_grain_key(context, prompt="configured", invoke=invoke)

    assert result["grain"] == payload["grain"]
    assert result["key_columns"] == ["order_id", "line_id"]
    assert result["rationale"] == payload["rationale"]
    assert "already been determined deterministically" in captured["prompt"]
    assert "Do not choose, replace, expand, or reinterpret the key columns." in captured["prompt"]


def _business_context():
    return build_ai_business_rule_context({
        "table_name": "orders",
        "schema_name": "sales",
        "layer": "Silver",
        "table_description": "One row per order",
        "columns": [
            {
                "column_name": "start_date",
                "data_type": "date",
                "description": "Order start date",
                "profile": {"null_percent": 0, "example_values": ["2026-09-01"]},
            },
            {
                "column_name": "end_date",
                "data_type": "date",
                "description": "Order end date",
                "profile": {"null_percent": 0, "example_values": ["2026-09-02"]},
            },
            {
                "column_name": "status",
                "data_type": "string",
                "description": "Order workflow status",
                "profile": {"distinct_count": 3, "example_values": ["Open", "Closed"]},
            },
        ],
        "existing_dq_rules": [{
            "rule_type": "completeness",
            "columns": ["status"],
            "parameters": {
                "maximum_missing_percent": 0,
                "treat_blank_as_missing": True,
            },
        }],
    })


def test_business_rule_context_includes_profile_and_existing_rules():
    """Give natural-language authoring enough governed context to infer columns and avoid duplicates."""
    context = _business_context()

    assert context["table_name"] == "orders"
    assert context["columns"][0]["profile"]["null_percent"] == 0
    assert context["columns"][2]["profile"]["example_values"] == ["Open", "Closed"]
    assert context["existing_dq_rules"][0]["rule_type"] == "completeness"


def test_business_rule_resolver_prefers_known_column_relationship():
    """Resolve an exact two-column comparison to the canonical known pattern."""
    captured = {}
    payload = [{
        "requirement": "End date must be on or after start date.",
        "rule_type": "column_relationship",
        "columns": ["end_date", "start_date"],
        "parameters": {"operator": ">="},
        "rationale": "Direct row-by-row comparison.",
    }]

    def invoke(prompt):
        captured["prompt"] = prompt
        return json.dumps(payload)

    result = suggest_business_rule(
        _business_context(),
        requirement="End date must be on or after start date.",
        relevant_columns=["start_date", "end_date"],
        prompt="Prefer known FabricOps patterns.",
        invoke=invoke,
    )[0]

    assert result["rule_type"] == "column_relationship"
    assert result["engineering_review_required"] is False
    assert result["parameters"] == {
        "columns": ["end_date", "start_date"],
        "operator": ">=",
        "business_requirement": "End date must be on or after start date.",
    }
    assert "one or more atomic rule objects" in captured["prompt"]


def test_business_rule_resolver_infers_columns_without_manual_selection():
    """An empty optional column constraint lets AI map business terms using governed context."""
    captured = {}
    payload = [{
        "requirement": "End date must be on or after start date.",
        "rule_type": "column_relationship",
        "columns": ["end_date", "start_date"],
        "parameters": {"operator": ">="},
        "rationale": "Resolved from governed column descriptions.",
    }]

    def invoke(prompt):
        captured["prompt"] = prompt
        return json.dumps(payload)

    result = suggest_business_rule(
        _business_context(),
        requirement="End date must be on or after start date.",
        prompt="configured",
        invoke=invoke,
    )[0]

    assert result["columns"] == ["end_date", "start_date"]
    assert "Optional column constraint selected by Governance:\n[]" in captured["prompt"]
    assert "infer the required columns from the full governed context" in captured["prompt"]


def test_business_rule_resolver_decomposes_compound_requirement():
    """One business statement may compile to several independently enforceable DQ rules."""
    payload = [
        {
            "requirement": "End date must be on or after start date.",
            "rule_type": "column_relationship",
            "columns": ["end_date", "start_date"],
            "parameters": {"operator": ">="},
            "rationale": "Independent date ordering condition.",
        },
        {
            "requirement": "Status must be Open or Closed.",
            "rule_type": "value_set",
            "columns": ["status"],
            "parameters": {"mode": "allow", "values": ["Open", "Closed"]},
            "rationale": "Independent governed status condition.",
        },
    ]

    result = suggest_business_rule(
        _business_context(),
        requirement=(
            "End date must be on or after start date and status must be Open or Closed."
        ),
        prompt="configured",
        invoke=lambda _prompt: json.dumps(payload),
    )

    assert [rule["rule_type"] for rule in result] == [
        "column_relationship", "value_set"
    ]
    assert result[0]["parameters"]["business_requirement"] == payload[0]["requirement"]
    assert result[1]["parameters"]["business_requirement"] == payload[1]["requirement"]


def test_business_rule_resolver_accepts_every_canonical_noncustom_pattern():
    """Use Custom Expression only after every canonical DQ family has been considered."""
    cases = [
        ("completeness", ["status"], {
            "maximum_missing_percent": 0,
            "treat_blank_as_missing": True,
        }),
        ("uniqueness", ["start_date", "end_date"], {}),
        ("value_set", ["status"], {"mode": "allow", "values": ["Open", "Closed"]}),
        ("range", ["start_date"], {
            "minimum": "2020-01-01",
            "maximum": None,
            "minimum_inclusive": True,
            "maximum_inclusive": True,
        }),
        ("pattern", ["status"], {"pattern": "^[A-Za-z]+$"}),
        ("column_relationship", ["end_date", "start_date"], {"operator": ">="}),
    ]

    for rule_type, columns, parameters in cases:
        payload = [{
            "requirement": "Governed requirement.",
            "rule_type": rule_type,
            "columns": columns,
            "parameters": parameters,
            "rationale": "Canonical FabricOps pattern.",
        }]
        result = suggest_business_rule(
            _business_context(),
            requirement="Governed requirement.",
            relevant_columns=columns,
            prompt="Prefer known FabricOps patterns.",
            invoke=lambda _prompt, value=payload: json.dumps(value),
        )[0]
        assert result["rule_type"] == rule_type
        assert result["engineering_review_required"] is False
        assert result["parameters"]["columns"] == columns


@pytest.mark.parametrize(
    ("rule_type", "requirement", "parameters"),
    [
        (
            "conditional_completeness",
            "When status is Approved, end date must be populated.",
            {
                "condition_operator": "=",
                "condition_value": "Approved",
                "treat_blank_as_missing": True,
            },
        ),
        (
            "conditional_values",
            "When status is Closed, end date must be one of the governed values.",
            {
                "condition_operator": "=",
                "condition_value": "Closed",
                "mode": "allow",
                "values": ["2026-01-01"],
            },
        ),
    ],
)
def test_business_rule_resolver_prefers_known_conditional_patterns(
    rule_type, requirement, parameters
):
    """Do not send known conditional patterns to Custom Expression review."""
    payload = [{
        "requirement": requirement,
        "rule_type": rule_type,
        "columns": ["status", "end_date"],
        "parameters": parameters,
        "rationale": "Known conditional pattern.",
    }]

    result = suggest_business_rule(
        _business_context(),
        requirement=requirement,
        relevant_columns=["status", "end_date"],
        prompt="Prefer known FabricOps patterns.",
        invoke=lambda _prompt: json.dumps(payload),
    )[0]

    assert result["rule_type"] == rule_type
    assert result["engineering_review_required"] is False
    assert result["parameters"]["business_requirement"] == requirement


def test_business_rule_resolver_flags_custom_expression_for_engineering_review():
    """Keep custom logic in the existing DQ model while marking it for later review."""
    payload = [{
        "requirement": "When status is Closed, end date must be populated.",
        "rule_type": "custom_expression",
        "columns": ["status", "end_date"],
        "parameters": {
            "expression_language": "pyspark",
            "expression": '(F.col("status") != "Closed") | F.col("end_date").isNotNull()',
        },
        "rationale": "Conditional relationship.",
    }]

    result = suggest_business_rule(
        _business_context(),
        requirement="When status is Closed, end date must be populated.",
        relevant_columns=["status", "end_date"],
        prompt="Prefer known FabricOps patterns.",
        invoke=lambda _prompt: json.dumps(payload),
    )[0]

    assert result["rule_type"] == "custom_expression"
    assert result["engineering_review_required"] is True
    assert result["parameters"]["engineering_review_required"] is True
    assert result["parameters"]["business_requirement"] == (
        "When status is Closed, end date must be populated."
    )


def test_business_rule_resolver_rejects_columns_outside_governance_selection():
    """An explicit optional column selection acts as a hard generation boundary."""
    payload = [{
        "requirement": "End date must be on or after start date.",
        "rule_type": "column_relationship",
        "columns": ["end_date", "status"],
        "parameters": {"operator": ">="},
    }]

    with pytest.raises(ValueError, match="outside the selected constraint"):
        suggest_business_rule(
            _business_context(),
            requirement="End date must be on or after start date.",
            relevant_columns=["start_date", "end_date"],
            prompt="configured",
            invoke=lambda _prompt: json.dumps(payload),
        )


def test_business_rule_resolver_rejects_single_object_response():
    """The AI contract is explicitly one-or-more atomic rules, never an ambiguous single object."""
    payload = {
        "rule_type": "value_set",
        "columns": ["status"],
        "parameters": {"mode": "allow", "values": ["Open", "Closed"]},
    }

    with pytest.raises(ValueError, match="non-empty JSON array"):
        suggest_business_rule(
            _business_context(),
            requirement="Status must be Open or Closed.",
            prompt="configured",
            invoke=lambda _prompt: json.dumps(payload),
        )
