"""Verify which DQ percentages are meaningful and reject misplaced tolerances."""

import pytest

from fabricops_kit.pipeline.shared import dq_tolerance_parameter, _validate_dq_rules


@pytest.mark.parametrize("kind,mode,field", [
    ("completeness", "", "maximum_missing_percent"),
    ("conditional_completeness", "", "maximum_missing_percent"),
    ("uniqueness", "", "maximum_failure_percent"),
    ("value_set", "allow", "maximum_failure_percent"),
    ("conditional_values", "allow", "maximum_failure_percent"),
    ("value_set", "block", None), ("conditional_values", "block", None),
    *[(kind, "", "maximum_failure_percent") for kind in ("range", "pattern", "column_relationship", "custom_expression")],
    *[(kind, "", None) for kind in ("schema", "grain", "sensitive_data", "freshness", "source_drift")],
])
def test_percentage_policy_is_specific_to_rule_semantics(kind, mode, field):
    """Structural checks and prohibited values must not gain an arbitrary row tolerance."""
    assert dq_tolerance_parameter(kind, mode) == field


@pytest.mark.parametrize("value", [-1, 101, float("nan"), float("inf"), True])
def test_row_tolerance_rejects_invalid_percentages(value):
    """Invalid values must not silently weaken a rule."""
    with pytest.raises(ValueError, match="percentage"):
        _validate_dq_rules([{
            "rule_type": "range", "columns": ["amount"], "minimum": 0,
            "maximum_failure_percent": value,
        }])


@pytest.mark.parametrize("rule", [
    {"rule_type": "value_set", "mode": "block", "values": ["forbidden"], "maximum_failure_percent": 1},
    {"rule_type": "conditional_values", "columns": ["status", "value"], "condition_operator": "=",
     "condition_value": "active", "mode": "block", "values": ["forbidden"], "maximum_failure_percent": 0},
    {"rule_type": "uniqueness", "minimum_unique_percent": 98, "maximum_failure_percent": 2},
    {"rule_type": "completeness", "maximum_missing_percent": 1,
     "treat_blank_as_missing": False, "maximum_failure_percent": 2},
])
def test_incompatible_percentage_fields_are_rejected(rule):
    """Do not accept two different meanings of percentage for the same rule."""
    with pytest.raises(ValueError, match="does not support"):
        _validate_dq_rules([{"columns": ["value"], **rule}])


def test_old_rules_without_generic_tolerance_remain_strict():
    """An existing range rule must not acquire a permissive default."""
    rule = _validate_dq_rules([{"rule_type": "range", "columns": ["value"], "minimum": 0}])[0]
    assert rule["maximum_failure_percent"] == 0
