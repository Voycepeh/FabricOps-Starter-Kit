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
