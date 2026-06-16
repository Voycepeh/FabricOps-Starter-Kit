"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import json

import pytest

from fabricops_kit.governance_review import _load_active_dq_rules, _prepare_dq_profile_input_rows, enforce_dq_rules
from fabricops_kit.guardrails import stop_if_failed, validate_schema
from tests.helpers import framework_config

pytestmark = pytest.mark.spark


def test_prepare_dq_profile_input_rows_uses_configured_audit_timezone(spark_session):
    """Verify prepare dq profile input rows uses configured audit timezone."""
    config = framework_config()
    object.__setattr__(config, "audit_timezone", "Asia/Singapore")
    profile_df = spark_session.createDataFrame(
        [
            {
                "TABLE_NAME": "orders",
                "COLUMN_NAME": "order_id",
                "DATA_TYPE": "string",
                "ROW_COUNT": 1,
                "NULL_COUNT": 0,
                "NULL_PERCENT": 0.0,
                "DISTINCT_COUNT": 1,
                "DISTINCT_PERCENT": 100.0,
                "MIN_VALUE": "A",
                "MAX_VALUE": "A",
            }
        ]
    )

    row = _prepare_dq_profile_input_rows(
        profile_df=profile_df,
        table_name="orders",
        business_context="test context",
        config=config,
    ).collect()[0].asDict()

    assert row["profile_timestamp"].endswith("+08:00")
    assert row["business_context"] == "test context"


def test_prepare_dq_profile_input_rows_defaults_to_utc_without_config(spark_session):
    """Verify prepare dq profile input rows defaults to utc without config."""
    profile_df = spark_session.createDataFrame(
        [
            {
                "TABLE_NAME": "orders",
                "COLUMN_NAME": "order_id",
                "DATA_TYPE": "string",
                "ROW_COUNT": 1,
                "NULL_COUNT": 0,
                "NULL_PERCENT": 0.0,
                "DISTINCT_COUNT": 1,
                "DISTINCT_PERCENT": 100.0,
                "MIN_VALUE": "A",
                "MAX_VALUE": "A",
            }
        ]
    )

    row = _prepare_dq_profile_input_rows(profile_df=profile_df, table_name="orders").collect()[0].asDict()

    assert row["profile_timestamp"].endswith("+00:00")


def test_spark_schema_validation_and_latest_dq_metadata_are_stable(spark_session):
    """Verify spark schema validation and latest dq metadata are stable."""
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
                "review_status": "governance_approved",
                "approved_by": "a",
                "approved_at": "2026-01-01T00:00:00Z",
                "action_type": "created",
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
                "review_status": "governance_approved",
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
    """Verify load active dq rules reconstructs current shape metadata row."""
    metadata_df = spark_session.createDataFrame(
        [
            {
                "table_name": "orders",
                "rule_key": "orders|amount_positive",
                "rule_id": "amount_positive",
                "column_name": "amount",
                "rule_type": "greater_than",
                "rule_parameters_json": json.dumps({"value": 0}),
                "severity": "error",
                "description": "Amount must be non-negative",
                "is_active": True,
                "review_status": "governance_approved",
                "approved_by": "reviewer@example.com",
                "approved_at": "2026-01-03T00:00:00Z",
                "action_type": "created",
                "_committed_at": "2026-01-03T00:00:01Z",
                "_committed_by": "reviewer@example.com",
            }
        ]
    )

    assert _load_active_dq_rules(metadata_df, table_name="orders") == [
        {
            "rule_id": "amount_positive",
            "rule_type": "greater_than",
            "columns": ["amount"],
            "severity": "error",
            "description": "Amount must be non-negative",
            "review_status": "governance_approved",
            "value": 0,
        }
    ]


def test_load_active_dq_rules_reconstructs_current_governance_metadata(spark_session, monkeypatch):
    """Verify load active dq rules reconstructs current governance metadata."""
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
                "rule_type": "greater_than",
                "columns": ["amount"],
                "value": 0,
                "severity": "error",
                "description": "Amount must be non-negative",
                "commit": True,
            }
        ],
        approved_by="reviewer@example.com",
    )

    assert [table for table, _ in writes] == [governance.GUARDRAIL_RULES_TABLE]
    assert writes[0][1].collect()[0]["guardrail_type"] == "dq"
    loaded = governance._load_active_dq_rules(writes[0][1], table_name="orders")

    assert loaded == [
        {
            "rule_id": "amount_positive",
            "rule_type": "greater_than",
            "columns": ["amount"],
            "severity": "error",
            "description": "Amount must be non-negative",
            "review_status": "governance_approved",
            "value": 0,
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
    """Verify enforce dq rules returns passed when no active rules."""
    import fabricops_kit.governance_review as governance

    df = spark_session.createDataFrame([{"order_id": "A", "status": "active", "amount": 10.0}])
    metadata_df = _dq_metadata_df(spark_session, [])
    monkeypatch.setattr(governance, "read_lakehouse_table", lambda *args, **kwargs: metadata_df)

    result = enforce_dq_rules(df, object(), "dev", "sales", "orders", spark_session=spark_session)

    assert result["status"] == "passed"
    assert result["can_continue"] is True
    assert result["checks"] == []
    assert result["message"] == "No active guardrail DQ rules found."
    assert result["summary"]["DQ_RULE_COUNT"] == 0
    assert {"_dq_check_status", "_dq_failed_rules"}.issubset(result["dataframe"].columns)



def test_enforce_dq_rules_result_write_toggle_targets_results(spark_session, monkeypatch):
    """Verify DQ enforcement writes result rows only when enabled."""
    import fabricops_kit.governance_review as governance
    import fabricops_kit.metadata as metadata

    df = spark_session.createDataFrame([{"order_id": "A", "status": "active", "amount": 10.0}])
    metadata_df = _dq_metadata_df(spark_session, [])
    writes = []
    monkeypatch.setattr(governance, "read_lakehouse_table", lambda *args, **kwargs: metadata_df)
    monkeypatch.setattr(metadata, "write_lakehouse_table", lambda df, config, env, target, table, **kwargs: writes.append((df, env, target, table, kwargs)))

    enforce_dq_rules(df, object(), "dev", "sales", "orders", spark_session=spark_session, run_id="run-1", write_results=False)
    assert writes == []

    enforce_dq_rules(df, object(), "dev", "sales", "orders", spark_session=spark_session, run_id="run-2", write_results=True)

    assert writes[0][2:4] == ("metadata", "METADATA_GUARDRAIL_RESULTS")
    row = writes[0][0].collect()[0].asDict()
    assert row["guardrail_type"] == "dq"
    assert row["run_id"] == "run-2"
    assert row["status"] == "passed"

def test_enforce_dq_rules_warning_failure_can_continue(spark_session, monkeypatch):
    """Verify enforce dq rules warning failure can continue."""
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
                "review_status": "governance_approved",
                "approved_by": "reviewer@example.com",
                "approved_at": "2026-01-03T00:00:00Z",
                "action_type": "created",
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



def test_enforce_dq_rules_warning_failure_adds_technical_columns_and_preserves_rows(spark_session, monkeypatch):
    """Verify enforce dq rules warning failure adds technical columns and preserves rows."""
    import fabricops_kit.governance_review as governance

    df = spark_session.createDataFrame(
        [
            {"order_id": "A", "status": "invalid", "amount": -1.0},
            {"order_id": "B", "status": "active", "amount": 10.0},
        ]
    )
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
                "review_status": "governance_approved",
                "approved_by": "reviewer@example.com",
                "approved_at": "2026-01-03T00:00:00Z",
                "action_type": "created",
                "_committed_at": "2026-01-03T00:00:01Z",
                "_committed_by": "reviewer@example.com",
            },
            {
                "environment_name": "dev",
                "dataset_name": "sales",
                "table_name": "orders",
                "rule_key": "orders|amount_positive",
                "rule_id": "amount_positive",
                "column_name": "amount",
                "rule_type": "greater_than",
                "rule_parameters_json": json.dumps({"value": 0}),
                "severity": "warning",
                "description": "Positive amount",
                "is_active": True,
                "review_status": "governance_approved",
                "approved_by": "reviewer@example.com",
                "approved_at": "2026-01-03T00:00:00Z",
                "action_type": "created",
                "_committed_at": "2026-01-03T00:00:01Z",
                "_committed_by": "reviewer@example.com",
            },
        ],
    )
    monkeypatch.setattr(governance, "read_lakehouse_table", lambda *args, **kwargs: metadata_df)

    result = enforce_dq_rules(df, object(), "dev", "sales", "orders", spark_session=spark_session)
    tagged_rows = {row["order_id"]: row.asDict() for row in result["dataframe"].collect()}

    assert result["status"] == "warning"
    assert result["can_continue"] is True
    assert result["dataframe"].count() == df.count()
    assert tagged_rows["A"]["_dq_check_status"] == "warning"
    assert tagged_rows["A"]["_dq_failed_rules"] == "amount_positive,status_known"
    assert tagged_rows["B"]["_dq_check_status"] == "passed"
    assert tagged_rows["B"]["_dq_failed_rules"] == ""
    assert result["summary"]["DQ_FAILED_RULE_COUNT"] == 2
    assert result["summary"]["DQ_WARNING_RULE_COUNT"] == 2
    assert result["summary"]["DQ_ERROR_RULE_COUNT"] == 0
    assert result["summary"]["DQ_FAILED_ROW_COUNT"] == 1
    assert result["summary"]["DQ_FAILED_ROW_PERCENT"] == 50.0


def test_enforce_dq_rules_error_failure_blocks(spark_session, monkeypatch):
    """Verify enforce dq rules error failure blocks."""
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
                "review_status": "governance_approved",
                "approved_by": "reviewer@example.com",
                "approved_at": "2026-01-03T00:00:00Z",
                "action_type": "created",
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
    """Verify enforce dq rules mixed warning and error failures return failed."""
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
                "review_status": "governance_approved",
                "approved_by": "reviewer@example.com",
                "approved_at": "2026-01-03T00:00:00Z",
                "action_type": "created",
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
                "review_status": "governance_approved",
                "approved_by": "reviewer@example.com",
                "approved_at": "2026-01-03T00:00:00Z",
                "action_type": "created",
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
    """Verify enforce dq rules supports current v1 metadata shape."""
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
                "review_status": "governance_approved",
                "approved_by": "reviewer@example.com",
                "approved_at": "2026-01-03T00:00:00Z",
                "action_type": "created",
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


def test_write_catalogue_evidence_writes_profile_evidence_without_result_fields(spark_session, monkeypatch):
    """Verify catalogue evidence excludes runtime guardrail result fields."""
    from fabricops_kit.data_profiling import profile_dataframe
    from fabricops_kit import pipeline

    writes = []
    monkeypatch.setattr(pipeline, "write_lakehouse_table", lambda df, config, env, target, table, **kwargs: writes.append((df, env, target, table, kwargs)))
    df = spark_session.createDataFrame([(1, "open")], "id int, status string")
    profile_df = profile_dataframe(df, "orders")

    result = pipeline.write_catalogue_evidence(
        {"orders": profile_df},
        {"orders": {"dataset_name": "sales", "table_name": "orders", "stage": "source", "profile_mode": "static_data"}},
        config={},
        env="dev",
        run_id="run-1",
        stability_results={"orders": {"status": "baseline_created", "can_continue": True, "stability_check_enabled": True, "profile_mode": "static_data", "stability_status": "baseline_created", "stability_can_continue": True}},
    )

    assert result == {"orders": "written"}
    assert writes[0][2:4] == ("metadata", "METADATA_DATA_CATALOGUE")
    assert writes[0][4]["mode"] == "append"
    assert "stability_status" not in writes[0][0].columns
    assert "freshness_status" not in writes[0][0].columns
    assert "dq_status" not in writes[0][0].columns
    assert "profile_mode" in writes[0][0].columns
    assert "load_behavior" not in writes[0][0].columns



def test_write_guardrail_result_writes_runtime_outcome_to_results_table(spark_session, monkeypatch):
    """Verify guardrail result writer targets METADATA_GUARDRAIL_RESULTS."""
    from fabricops_kit import metadata

    writes = []
    monkeypatch.setattr(metadata, "write_lakehouse_table", lambda df, config, env, target, table, **kwargs: writes.append((df, env, target, table, kwargs)))

    metadata._write_guardrail_result_row(
        spark_session=spark_session,
        config={},
        env="dev",
        run_id="run-1",
        dataset_name="sales",
        table_name="orders",
        guardrail_type="freshness",
        rule_type="max_age_days",
        result={"status": "failed", "can_continue": False, "severity": "blocking", "message": "too old"},
        rule_key="freshness_orders",
    )

    assert writes[0][2:4] == ("metadata", "METADATA_GUARDRAIL_RESULTS")
    written_row = writes[0][0].collect()[0].asDict()
    assert written_row["guardrail_type"] == "freshness"
    assert written_row["status"] == "failed"
    assert written_row["can_continue"] is False

def test_write_catalogue_evidence_persists_each_profile_behavior_watermark(spark_session, monkeypatch):
    """Verify changing-data catalogue writes retain per-watermark baseline fields."""
    from fabricops_kit import pipeline
    from fabricops_kit.data_profiling import profile_dataframe

    writes = []
    monkeypatch.setattr(
        pipeline,
        "write_lakehouse_table",
        lambda df, config, env, target, table, **kwargs: writes.append((df, env, target, table, kwargs)),
    )
    df = spark_session.createDataFrame([(1, "2026-06-14"), (2, "2026-06-15")], "id int, business_date string")
    profile_df = profile_dataframe(df, "orders")

    result = pipeline.write_catalogue_evidence(
        {"orders": profile_df},
        {"orders": {"dataset_name": "sales", "table_name": "orders", "stage": "source", "profile_mode": "changing_data"}},
        config={},
        env="dev",
        run_id="run-1",
        stability_results={
            "orders": {
                "status": "baseline_created",
                "can_continue": True,
                "stability_check_enabled": True,
                "profile_mode": "changing_data",
                "stability_status": "baseline_created",
                "stability_can_continue": True,
                "profile_evidence_rows": [
                    {
                        "watermark_column": "business_date",
                        "watermark_value": "2026-06-14",
                        "profile_payload_json": '{"watermark_value":"2026-06-14"}',
                        "profile_hash": "hash-2026-06-14",
                        "row_count": 1,
                    },
                    {
                        "watermark_column": "business_date",
                        "watermark_value": "2026-06-15",
                        "profile_payload_json": '{"watermark_value":"2026-06-15"}',
                        "profile_hash": "hash-2026-06-15",
                        "row_count": 1,
                    },
                ],
            }
        },
    )

    assert result == {"orders": "written"}
    assert len(writes) == 2
    persisted = [write[0].select("watermark_column", "watermark_value", "profile_payload_json", "profile_hash").first().asDict() for write in writes]
    assert persisted == [
        {
            "watermark_column": "business_date",
            "watermark_value": "2026-06-14",
            "profile_payload_json": '{"watermark_value":"2026-06-14"}',
            "profile_hash": "hash-2026-06-14",
        },
        {
            "watermark_column": "business_date",
            "watermark_value": "2026-06-15",
            "profile_payload_json": '{"watermark_value":"2026-06-15"}',
            "profile_hash": "hash-2026-06-15",
        },
    ]
