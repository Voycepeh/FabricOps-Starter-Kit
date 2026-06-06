from __future__ import annotations

import pytest

from fabricops_kit.drift import validate_schema
from fabricops_kit.governance_review import _assert_dq_passed, _enforce_dq, _load_active_dq_rules

pytestmark = pytest.mark.spark


def test_spark_schema_validation_allows_new_columns_in_monitoring_flow(spark_session):
    df = spark_session.createDataFrame([{"id": 1, "amount": 10.0, "extra": "new"}])
    schema_result = validate_schema(df, {"id": "bigint", "amount": "double"}, preset="allow_new_columns")

    assert schema_result["status"] == "warning"
    assert schema_result["can_continue"] is True


def test_spark_migrated_dq_enforcement_splits_valid_quarantine_and_failure_rows(spark_session):
    df = spark_session.createDataFrame([{"id": "1", "amount": 10.0}, {"id": None, "amount": 20.0}, {"id": "", "amount": 30.0}])
    rules = [
        {
            "rule_id": "id_required",
            "rule_type": "not_null",
            "columns": ["id"],
            "severity": "error",
            "description": "ID required",
        }
    ]

    result = _enforce_dq(df, table_name="orders", rules=rules, row_id_columns=["amount"], dq_run_id="dq-run")

    assert result.valid_rows.count() == 1
    assert result.quarantine_rows.count() == 2
    assert result.failure_rows.count() == 2
    assert result.rule_results.collect()[0]["status"] == "FAIL"
    with pytest.raises(ValueError, match="Data quality failed"):
        _assert_dq_passed(result)


def test_spark_migrated_dq_loading_uses_latest_active_governance_metadata(spark_session):
    metadata_df = spark_session.createDataFrame(
        [
            {
                "table_name": "orders",
                "rule_key": "orders|required",
                "rule_id": "id_required",
                "rule_type": "not_null",
                "column_name": "id",
                "rule_parameters_json": "{}",
                "severity": "error",
                "description": "Required",
                "is_active": True,
                "action_type": "approved",
                "approved_at": "2026-01-01T00:00:00Z",
            },
            {
                "table_name": "orders",
                "rule_key": "orders|inactive",
                "rule_id": "inactive",
                "rule_type": "not_null",
                "column_name": "amount",
                "rule_parameters_json": "{}",
                "severity": "warning",
                "description": "Inactive",
                "is_active": False,
                "action_type": "deactivated",
                "approved_at": "2026-01-02T00:00:00Z",
            },
        ]
    )

    active_rules = _load_active_dq_rules(metadata_df, table_name="orders")

    assert active_rules == [{"rule_id": "id_required", "rule_type": "not_null", "columns": ["id"], "severity": "error", "description": "Required"}]


def test_spark_migrated_dq_enforcement_detects_accepted_values_and_value_ranges(spark_session):
    df = spark_session.createDataFrame(
        [
            {"id": "1", "status": "active", "amount": 10.0},
            {"id": "2", "status": "inactive", "amount": -1.0},
            {"id": "3", "status": "unknown", "amount": 500.0},
        ]
    )
    rules = [
        {
            "rule_id": "status_known",
            "rule_type": "accepted_values",
            "columns": ["status"],
            "allowed_values": ["active", "inactive"],
            "severity": "warning",
            "description": "Known status",
        },
        {
            "rule_id": "amount_range",
            "rule_type": "value_range",
            "columns": ["amount"],
            "lower_bound": 0,
            "upper_bound": 100,
            "severity": "warning",
            "description": "Amount range",
        },
    ]

    result = _enforce_dq(df, table_name="orders", rules=rules, row_id_columns=["id"], dq_run_id="dq-run")
    failure_rows = result.failure_rows.collect()
    rule_results = {row["rule_id"]: row for row in result.rule_results.collect()}

    assert hasattr(result, "rules")
    assert hasattr(result, "rule_results")
    assert hasattr(result, "valid_rows")
    assert hasattr(result, "quarantine_rows")
    assert hasattr(result, "failure_rows")
    assert result.valid_rows.count() == 1
    assert result.quarantine_rows.count() == 2
    assert {row["rule_id"] for row in failure_rows} == {"status_known", "amount_range"}
    assert rule_results["status_known"]["status"] == "FAIL"
    assert rule_results["amount_range"]["failed_count"] == 2
    _assert_dq_passed(result)


def test_spark_migrated_dq_warning_severity_does_not_block(spark_session):
    df = spark_session.createDataFrame([{"id": None}, {"id": "1"}])
    result = _enforce_dq(
        df,
        table_name="orders",
        rules=[{"rule_id": "id_recommended", "rule_type": "not_null", "columns": ["id"], "severity": "warning", "description": "ID recommended"}],
    )

    assert result.failure_rows.count() == 1
    _assert_dq_passed(result)
