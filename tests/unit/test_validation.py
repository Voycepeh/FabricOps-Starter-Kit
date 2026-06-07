from __future__ import annotations

import pandas as pd
import pytest

from fabricops_kit.governance_review import _validate_dq_rules
from fabricops_kit.drift import _check_profile_drift, monitor_data_changes, stop_if_failed, validate_schema

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


def test_monitor_data_changes_returns_guardrail_wrapper_shape(monkeypatch):
    import fabricops_kit.data_profiling as data_profiling

    profile_rows = [
        {
            "TABLE_NAME": "orders",
            "COLUMN_NAME": "status",
            "DATA_TYPE": "string",
            "ROW_COUNT": 100,
            "NULL_COUNT": 0,
            "NULL_PERCENT": 0.0,
            "DISTINCT_COUNT": 2,
            "DISTINCT_PERCENT": 2.0,
        }
    ]

    class FakeSpark:
        def table(self, _metadata_table):
            raise RuntimeError("table not found")

    monkeypatch.setattr(data_profiling, "profile_dataframe", lambda *args, **kwargs: profile_rows)
    result = monitor_data_changes(
        FakeSpark(),
        object(),
        "METADATA_DATA_CATALOGUE",
        "sales",
        "orders",
        stage="target",
        preset="monitor_changing_data",
    )

    assert set(result) == {"profile", "profile_payload", "baseline", "result"}
    assert result["profile"] == profile_rows
    assert result["profile_payload"]["columns"][0]["column_name"] == "status"
    assert result["baseline"] is None
    assert result["result"]["status"] == "no_baseline"
    assert result["result"]["can_continue"] is True
    assert result["result"]["preset"] == "monitor_changing_data"


def test_stop_if_failed_blocks_only_failed_guardrail_results():
    stop_if_failed({"can_continue": True, "status": "warning", "message": "observed"})
    stop_if_failed({"result": {"can_continue": True, "status": "passed"}})

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
