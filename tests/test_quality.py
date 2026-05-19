import pytest

from fabricops_kit.data_quality import (
    _approved_dq_rules_from_review_rows,
    _extract_candidate_rules_from_responses,
    _parse_dq_rules_dict_from_text,
    _prepare_dq_profile_rows_with_context,
    validate_dq_rules,
)


def test_parse_dq_rules_dict_from_text_accepts_plain_and_prefixed_payloads():
    plain = '{"orders": [{"rule_id": "r1"}]}'
    prefixed = 'DQ_RULES = {"orders": [{"rule_id": "r2"}]}'

    assert _parse_dq_rules_dict_from_text(plain)["orders"][0]["rule_id"] == "r1"
    assert _parse_dq_rules_dict_from_text(prefixed)["orders"][0]["rule_id"] == "r2"


def test_prepare_dq_profile_rows_with_context_keeps_only_approved_context_rows():
    profile_rows = [
        {"column_name": "id", "data_type": "string"},
        {"column_name": "status", "data_type": "string"},
    ]
    contexts = [
        {"column_name": "id", "approved_business_context": "Order identifier"},
        {"column_name": "status", "approved_business_context": ""},
    ]

    prepared = _prepare_dq_profile_rows_with_context(profile_rows, table_name="orders", column_contexts=contexts)

    assert len(prepared) == 1
    assert prepared[0]["column_name"] == "id"
    assert prepared[0]["table_name"] == "orders"
    assert prepared[0]["approved_business_context"] == "Order identifier"


def test_extract_candidate_rules_from_list_responses_deduplicates_by_rule_id():
    responses = [
        {"ai_dq_response": 'DQ_RULES = {"orders": [{"rule_id": "r1", "rule_type": "not_null"}]}'},
        {"ai_dq_response": 'DQ_RULES = {"orders": [{"rule_id": "r1", "rule_type": "not_null"}, {"rule_id": "r2", "rule_type": "regex_format"}]}'},
    ]

    rules = _extract_candidate_rules_from_responses(responses, table_name="orders")
    ids = {r["rule_id"] for r in rules}

    assert ids == {"r1", "r2"}


def test_approved_dq_rules_from_review_rows_returns_only_approved_payloads():
    rows = [
        {"approval_status": "approved", "proposed_rule_payload": '{"rule_id": "r1"}'},
        {"approval_status": "rejected", "proposed_rule_payload": '{"rule_id": "r2"}'},
    ]

    approved = _approved_dq_rules_from_review_rows(rows)

    assert approved == [{"rule_id": "r1"}]


def test_validate_dq_rules_accepts_canonical_rules_and_rejects_invalid_ones():
    valid_rules = [
        {
            "rule_id": "r1",
            "rule_type": "not_null",
            "columns": ["id"],
            "severity": "warning",
            "description": "id must be present",
        },
        {
            "rule_id": "r2",
            "rule_type": "value_range",
            "columns": ["amount"],
            "severity": "error",
            "description": "amount in range",
            "lower_bound": 0,
        },
    ]

    assert validate_dq_rules(valid_rules) == valid_rules

    with pytest.raises(ValueError):
        validate_dq_rules(
            [
                {
                    "rule_id": "bad",
                    "rule_type": "accepted_values",
                    "columns": ["status"],
                    "severity": "warning",
                    "description": "missing allowed values",
                }
            ]
        )
