from __future__ import annotations

import pandas as pd
import pytest

from fabricops_kit.data_quality import _validate_dq_rules
from fabricops_kit.drift import _check_profile_drift, stop_if_failed, validate_schema

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


def test__validate_dq_rules_accepts_canonical_rules_and_rejects_invalid_shapes():
    valid_rules = [
        {"rule_id": "id_required", "rule_type": "not_null", "columns": ["id"], "severity": "error", "description": "ID required"},
        {
            "rule_id": "status_values",
            "rule_type": "accepted_values",
            "columns": ["status"],
            "allowed_values": ["active", "inactive"],
            "severity": "warning",
            "description": "Known status",
        },
    ]

    assert _validate_dq_rules(valid_rules) == valid_rules
    for invalid in (
        None,
        [{"rule_id": "missing", "rule_type": "not_null", "columns": ["id"]}],
        [{"rule_id": "bad_type", "rule_type": "custom", "columns": ["id"], "severity": "error", "description": "x"}],
        [{"rule_id": "no_cols", "rule_type": "not_null", "columns": [], "severity": "error", "description": "x"}],
    ):
        with pytest.raises(ValueError):
            _validate_dq_rules(invalid)


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
