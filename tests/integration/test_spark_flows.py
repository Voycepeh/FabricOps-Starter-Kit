from __future__ import annotations

import json

import pytest

from fabricops_kit.governance_review import _enforce_dq, _load_dq_rules
from fabricops_kit.drift import validate_schema

pytestmark = pytest.mark.spark


def test_spark_dq_enforcement_splits_valid_quarantine_and_failure_rows(spark_session):
    df = spark_session.createDataFrame(
        [
            {"order_id": "A", "status": "active", "amount": 10.0},
            {"order_id": "B", "status": "invalid", "amount": 20.0},
            {"order_id": None, "status": "active", "amount": -1.0},
        ]
    )
    rules = [
        {"rule_id": "order_id_required", "rule_type": "not_null", "columns": ["order_id"], "severity": "error", "description": "Required"},
        {
            "rule_id": "status_known",
            "rule_type": "accepted_values",
            "columns": ["status"],
            "allowed_values": ["active", "inactive"],
            "severity": "warning",
            "description": "Known status",
        },
        {"rule_id": "amount_positive", "rule_type": "value_range", "columns": ["amount"], "lower_bound": 0, "severity": "error", "description": "Positive"},
    ]

    result = _enforce_dq(df, table_name="orders", rules=rules, row_id_columns=["order_id"], dq_run_id="dq-run")

    assert result.valid_rows.count() == 1
    assert result.quarantine_rows.count() == 2
    assert result.failure_rows.count() == 3


def test_spark_schema_validation_and_latest_dq_metadata_are_stable(spark_session):
    df = spark_session.createDataFrame([{"id": 1, "amount": 10.0, "extra": "new"}])
    schema_result = validate_schema(df, {"id": "bigint", "amount": "double"}, preset="allow_new_columns")
    metadata_df = spark_session.createDataFrame(
        [
            {
                "table_name": "orders",
                "rule_key": "orders|required",
                "is_active": True,
                "action_ts": "2026-01-01T00:00:00Z",
                "action_type": "approved",
                "action_by": "a",
                "rule_source": "review",
                "rule_json": json.dumps({"rule_id": "required", "rule_type": "not_null", "columns": ["id"], "severity": "error", "description": "Required"}),
            },
            {
                "table_name": "orders",
                "rule_key": "orders|required",
                "is_active": False,
                "action_ts": "2026-01-02T00:00:00Z",
                "action_type": "deactivated",
                "action_by": "b",
                "rule_source": "review",
                "rule_json": json.dumps({"rule_id": "required", "rule_type": "not_null", "columns": ["id"], "severity": "error", "description": "Required"}),
            },
        ]
    )

    assert schema_result["status"] == "warning"
    assert _load_dq_rules(metadata_df, table_name="orders") == []
