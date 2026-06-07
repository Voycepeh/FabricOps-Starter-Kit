from __future__ import annotations

import json

import pytest

from fabricops_kit.governance_review import _enforce_dq, _load_active_dq_rules, enforce_dq_rules
from fabricops_kit.drift import stop_if_failed, validate_schema

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



def _dq_metadata_df(spark_session, rows):
    schema = (
        "environment_name string, dataset_name string, table_name string, rule_key string, rule_id string, "
        "column_name string, rule_type string, rule_parameters_json string, severity string, description string, "
        "is_active boolean, review_status string, approved_by string, approved_at string, action_type string, "
        "_committed_at string, _committed_by string"
    )
    return spark_session.createDataFrame(rows, schema=schema)


def test_enforce_dq_rules_returns_passed_when_no_active_rules(spark_session, monkeypatch):
    import fabricops_kit.governance_review as governance

    df = spark_session.createDataFrame([{"order_id": "A", "status": "active", "amount": 10.0}])
    metadata_df = _dq_metadata_df(spark_session, [])
    monkeypatch.setattr(governance, "read_lakehouse_table", lambda *args, **kwargs: metadata_df)

    result = enforce_dq_rules(df, object(), "dev", "sales", "orders", spark_session=spark_session)

    assert result == {
        "status": "passed",
        "can_continue": True,
        "checks": [],
        "message": "No active approved DQ rules found.",
    }


def test_enforce_dq_rules_warning_failure_can_continue(spark_session, monkeypatch):
    import fabricops_kit.governance_review as governance

    df = spark_session.createDataFrame([{"order_id": "A", "status": "invalid", "amount": 10.0}])
    metadata_df = _dq_metadata_df(
        spark_session,
        [
            {
                "environment_name": "dev",
                "dataset_name": "sales",
                "table_name": "orders",
                "rule_key": "orders|status_known",
                "rule_id": "status_known",
                "column_name": "status",
                "rule_type": "accepted_values",
                "rule_parameters_json": json.dumps({"allowed_values": ["active", "inactive"]}),
                "severity": "warning",
                "description": "Known status",
                "is_active": True,
                "review_status": "approved",
                "approved_by": "reviewer@example.com",
                "approved_at": "2026-01-03T00:00:00Z",
                "action_type": "approved",
                "_committed_at": "2026-01-03T00:00:01Z",
                "_committed_by": "reviewer@example.com",
            }
        ],
    )
    monkeypatch.setattr(governance, "read_lakehouse_table", lambda *args, **kwargs: metadata_df)

    result = enforce_dq_rules(df, object(), "dev", "sales", "orders", spark_session=spark_session)

    assert result["status"] == "warning"
    assert result["can_continue"] is True
    assert result["checks"][0]["status"] == "warning"
    assert result["checks"][0]["failed_count"] == 1
    assert result["checks"][0]["total_count"] == 1
    assert result["checks"][0]["failed_percent"] == 100.0


def test_enforce_dq_rules_error_failure_blocks(spark_session, monkeypatch):
    import fabricops_kit.governance_review as governance

    df = spark_session.createDataFrame([(None, "active", 10.0)], "order_id string, status string, amount double")
    metadata_df = _dq_metadata_df(
        spark_session,
        [
            {
                "environment_name": "dev",
                "dataset_name": "sales",
                "table_name": "orders",
                "rule_key": "orders|order_id_required",
                "rule_id": "order_id_required",
                "column_name": "order_id",
                "rule_type": "not_null",
                "rule_parameters_json": "{}",
                "severity": "error",
                "description": "Required",
                "is_active": True,
                "review_status": "approved",
                "approved_by": "reviewer@example.com",
                "approved_at": "2026-01-03T00:00:00Z",
                "action_type": "approved",
                "_committed_at": "2026-01-03T00:00:01Z",
                "_committed_by": "reviewer@example.com",
            }
        ],
    )
    monkeypatch.setattr(governance, "read_lakehouse_table", lambda *args, **kwargs: metadata_df)

    result = enforce_dq_rules(df, object(), "dev", "sales", "orders", spark_session=spark_session)

    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert result["checks"][0]["status"] == "failed"
    with pytest.raises(Exception, match="Guardrail blocked execution"):
        stop_if_failed(result)


def test_enforce_dq_rules_mixed_warning_and_error_failures_return_failed(spark_session, monkeypatch):
    import fabricops_kit.governance_review as governance

    df = spark_session.createDataFrame([(None, "invalid", 10.0)], "order_id string, status string, amount double")
    metadata_df = _dq_metadata_df(
        spark_session,
        [
            {
                "environment_name": "dev",
                "dataset_name": "sales",
                "table_name": "orders",
                "rule_key": "orders|order_id_required",
                "rule_id": "order_id_required",
                "column_name": "order_id",
                "rule_type": "not_null",
                "rule_parameters_json": "{}",
                "severity": "error",
                "description": "Required",
                "is_active": True,
                "review_status": "approved",
                "approved_by": "reviewer@example.com",
                "approved_at": "2026-01-03T00:00:00Z",
                "action_type": "approved",
                "_committed_at": "2026-01-03T00:00:01Z",
                "_committed_by": "reviewer@example.com",
            },
            {
                "environment_name": "dev",
                "dataset_name": "sales",
                "table_name": "orders",
                "rule_key": "orders|status_known",
                "rule_id": "status_known",
                "column_name": "status",
                "rule_type": "accepted_values",
                "rule_parameters_json": json.dumps({"allowed_values": ["active", "inactive"]}),
                "severity": "warning",
                "description": "Known status",
                "is_active": True,
                "review_status": "approved",
                "approved_by": "reviewer@example.com",
                "approved_at": "2026-01-03T00:00:00Z",
                "action_type": "approved",
                "_committed_at": "2026-01-03T00:00:01Z",
                "_committed_by": "reviewer@example.com",
            },
        ],
    )
    monkeypatch.setattr(governance, "read_lakehouse_table", lambda *args, **kwargs: metadata_df)

    result = enforce_dq_rules(df, object(), "dev", "sales", "orders", spark_session=spark_session)

    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert {check["status"] for check in result["checks"]} == {"failed", "warning"}


def test_enforce_dq_rules_supports_current_v1_metadata_shape(spark_session, monkeypatch):
    import fabricops_kit.governance_review as governance

    df = spark_session.createDataFrame([{"order_id": "A", "status": "active", "amount": 10.0, "email": "a@example.com"}])
    metadata_df = _dq_metadata_df(
        spark_session,
        [
            {
                "environment_name": "dev",
                "dataset_name": "sales",
                "table_name": "orders",
                "rule_key": "orders|email_format",
                "rule_id": "email_format",
                "column_name": "email",
                "rule_type": "not_null",
                "rule_parameters_json": "{}",
                "severity": "error",
                "description": "Email format",
                "is_active": True,
                "review_status": "approved",
                "approved_by": "reviewer@example.com",
                "approved_at": "2026-01-03T00:00:00Z",
                "action_type": "approved",
                "_committed_at": "2026-01-03T00:00:01Z",
                "_committed_by": "reviewer@example.com",
            }
        ],
    )
    monkeypatch.setattr(governance, "read_lakehouse_table", lambda *args, **kwargs: metadata_df)

    result = enforce_dq_rules(df, object(), "dev", "sales", "orders", spark_session=spark_session)

    assert result["status"] == "passed"
    assert result["can_continue"] is True
    assert result["checks"][0]["rule_type"] == "not_null"
