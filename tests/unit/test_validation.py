from __future__ import annotations

import pandas as pd
import pytest

from fabricops_kit.drift import _check_profile_drift, stop_if_failed, validate_schema
from fabricops_kit.governance_review import (
    _extract_candidate_rules_from_responses,
    _extract_column_context_suggestions,
    _extract_governance_suggestions,
    _parse_ai_dict_response,
    _parse_dq_rules_dict_from_text,
    _validate_dq_rules,
)

pytestmark = pytest.mark.unit


def test_validate_schema_supports_strict_allow_new_and_monitor_modes():
    df = pd.DataFrame({"id": [1, 2], "amount": [10.0, 20.0], "new_col": ["x", "y"]})
    expected = {"id": "bigint", "amount": "double"}

    strict = validate_schema(df, expected, preset="strict")
    allow_new = validate_schema(df, expected, preset="allow_new_columns")
    monitor = validate_schema(df[["id"]], expected, preset="monitor_only")

    assert strict["status"] == "failed"
    assert strict["can_continue"] is False
    assert allow_new["status"] == "warning"
    assert allow_new["can_continue"] is True
    assert monitor["status"] == "warning"
    assert monitor["can_continue"] is True
    with pytest.raises(ValueError, match="preset"):
        validate_schema(df, expected, preset="unknown")



def test_dq_ai_response_parsing_candidate_extraction_and_validation_are_migrated():
    response_text = """DQ_RULES = {
        'orders': [
            {'rule_id': 'id_required', 'rule_type': 'not_null', 'columns': ['id'], 'severity': 'error', 'description': 'ID required'},
            {'rule_id': 'id_required', 'rule_type': 'not_null', 'columns': ['id'], 'severity': 'error', 'description': 'Duplicate should dedupe'},
            {'rule_id': 'status_known', 'rule_type': 'accepted_values', 'columns': ['status'], 'allowed_values': ['active'], 'severity': 'warning', 'description': 'Known status'}
        ]
    }"""

    parsed = _parse_dq_rules_dict_from_text(response_text)
    candidates = _extract_candidate_rules_from_responses([{"ai_dq_response": response_text}], table_name="orders")
    validated = _validate_dq_rules(candidates)

    assert "orders" in parsed
    assert {rule["rule_id"] for rule in candidates} == {"id_required", "status_known"}
    assert validated[0]["columns"]
    with pytest.raises(ValueError, match="unsupported rule_type"):
        _validate_dq_rules([{"rule_id": "bad", "rule_type": "future", "columns": ["id"], "severity": "warning", "description": "x"}])


def test_business_context_ai_response_parsing_and_suggestion_extraction_are_migrated():
    response_text = "BUSINESS_CONTEXT = {'column_name': 'amount', 'business_context': 'Approved payment amount', 'notes': 'numeric'}"

    parsed = _parse_ai_dict_response(response_text, marker="BUSINESS_CONTEXT")
    suggestions = _extract_column_context_suggestions([{"ai_business_context_response": response_text}])

    assert parsed["column_name"] == "amount"
    assert suggestions == [{"column_name": "amount", "business_context": "Approved payment amount", "notes": "numeric"}]


def test_governance_ai_response_parsing_and_classification_extraction_are_migrated():
    response_text = """GOVERNANCE_CONTEXT = {
        'column_name': 'customer_id',
        'personal_data_classification': 'indirect_identifier',
        'sensitivity_label': 'confidential',
        'reasoning': 'Identifier-like customer key'
    }"""

    suggestions = _extract_governance_suggestions([{"ai_governance_response": response_text}])

    assert suggestions == [
        {
            "column_name": "customer_id",
            "personal_data_classification": "indirect_identifier",
            "sensitivity_label": "confidential",
            "reasoning": "Identifier-like customer key",
        }
    ]

def test_monitor_data_changes_uses_profile_baselines_without_blocking_first_observation():
    current = {
        "row_count": 100,
        "columns": [{"column_name": "status", "null_percent": 0.0, "distinct_count": 2}],
    }
    baseline = {
        "row_count": 100,
        "columns": [{"column_name": "status", "null_percent": 0.0, "distinct_count": 2}],
    }

    first = _check_profile_drift(current, baseline_profile=None)
    changed = _check_profile_drift(current, baseline_profile=baseline)

    assert first["status"] == "no_baseline"
    assert first["can_continue"] is True
    assert changed["status"] in {"warning", "failed", "passed"}
    with pytest.raises(Exception):
        stop_if_failed({"can_continue": False, "status": "failed", "message": "blocked"})


def test_drift_public_surface_keeps_compatibility_exceptions_unexported():
    import fabricops_kit
    import fabricops_kit.drift as drift

    public_drift_callables = {"validate_schema", "monitor_data_changes", "stop_if_failed"}
    exported_from_drift = {
        name
        for name in fabricops_kit.__all__
        if getattr(fabricops_kit, name).__module__ == "fabricops_kit.drift"
    }

    assert exported_from_drift == public_drift_callables
    assert "UnsupportedDataFrameEngineError" not in fabricops_kit.__all__
    assert "IncrementalSafetyError" not in fabricops_kit.__all__
    assert not hasattr(fabricops_kit, "UnsupportedDataFrameEngineError")
    assert not hasattr(fabricops_kit, "IncrementalSafetyError")

    assert issubclass(drift.UnsupportedDataFrameEngineError, ValueError)
    assert issubclass(drift.IncrementalSafetyError, Exception)
    assert not hasattr(drift, "_check_partition_drift")
    assert not hasattr(drift, "_build_partition_snapshot")
