from __future__ import annotations

import json

import pytest

from fabricops_kit.governance_review import _enforce_dq, _load_active_dq_rules
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
                "rule_id": "required",
                "column_name": "id",
                "rule_type": "not_null",
                "rule_parameters_json": "{}",
                "severity": "error",
                "description": "Required",
                "is_active": True,
                "review_status": "approved",
                "approved_by": "a",
                "approved_at": "2026-01-01T00:00:00Z",
                "action_type": "approved",
                "_committed_at": "2026-01-01T00:00:01Z",
                "_committed_by": "a",
            },
            {
                "table_name": "orders",
                "rule_key": "orders|required",
                "rule_id": "required",
                "column_name": "id",
                "rule_type": "not_null",
                "rule_parameters_json": "{}",
                "severity": "error",
                "description": "Required",
                "is_active": False,
                "review_status": "approved",
                "approved_by": "b",
                "approved_at": "2026-01-02T00:00:00Z",
                "action_type": "deactivated",
                "_committed_at": "2026-01-02T00:00:01Z",
                "_committed_by": "b",
            },
        ]
    )

    assert schema_result["status"] == "warning"
    assert _load_active_dq_rules(metadata_df, table_name="orders") == []


def test_load_active_dq_rules_reconstructs_current_shape_metadata_row(spark_session):
    metadata_df = spark_session.createDataFrame(
        [
            {
                "table_name": "orders",
                "rule_key": "orders|amount_positive",
                "rule_id": "amount_positive",
                "column_name": "amount",
                "rule_type": "value_range",
                "rule_parameters_json": json.dumps({"lower_bound": 0}),
                "severity": "error",
                "description": "Amount must be non-negative",
                "is_active": True,
                "review_status": "approved",
                "approved_by": "reviewer@example.com",
                "approved_at": "2026-01-03T00:00:00Z",
                "action_type": "approved",
                "_committed_at": "2026-01-03T00:00:01Z",
                "_committed_by": "reviewer@example.com",
            }
        ]
    )

    assert _load_active_dq_rules(metadata_df, table_name="orders") == [
        {
            "rule_id": "amount_positive",
            "rule_type": "value_range",
            "columns": ["amount"],
            "severity": "error",
            "description": "Amount must be non-negative",
            "lower_bound": 0,
        }
    ]


def test_load_active_dq_rules_reconstructs_current_governance_metadata(spark_session, monkeypatch):
    import fabricops_kit.governance_review as governance
    from tests.helpers import framework_config

    writes = []
    monkeypatch.setattr(governance, "write_lakehouse_table", lambda df, config, env, target, table, **kwargs: writes.append((table, df)))
    profile_rows = [
        {
            "environment_name": "dev",
            "dataset_name": "sales",
            "table_name": "orders",
            "column_name": "amount",
            "metadata_table_key": "dev|sales|orders",
            "metadata_column_key": "dev|sales|orders|amount",
        }
    ]

    governance.record_table_governance(
        framework_config(),
        "dev",
        profile_rows,
        spark_session=spark_session,
        dq_rule_reviews=[
            {
                "rule_id": "amount_positive",
                "column_name": "amount",
                "rule_type": "value_range",
                "rule_parameters": {"lower_bound": 0},
                "severity": "error",
                "description": "Amount must be non-negative",
                "commit": True,
            }
        ],
        approved_by="reviewer@example.com",
    )

    assert [table for table, _ in writes] == [governance.DQ_RULES_TABLE]
    loaded = governance._load_active_dq_rules(writes[0][1], table_name="orders")

    assert loaded == [
        {
            "rule_id": "amount_positive",
            "rule_type": "value_range",
            "columns": ["amount"],
            "severity": "error",
            "description": "Amount must be non-negative",
            "lower_bound": 0,
        }
    ]
