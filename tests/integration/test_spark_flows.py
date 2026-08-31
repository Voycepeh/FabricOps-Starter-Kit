"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import json

import pytest

from fabricops_kit.config.shared import resolve_runtime_context
from fabricops_kit.pipeline.shared import _load_active_dq_rules
from fabricops_kit.pipeline.shared import stop_if_failed, schema_check_core
from tests.helpers import framework_config

pytestmark = pytest.mark.spark


def runtime_context(**overrides):
    """Return deterministic Fabric runtime audit context for metadata writes."""
    context = {
        "currentWorkspaceId": "test-workspace-id",
        "currentWorkspaceName": "test-workspace",
        "currentNotebookId": "test-notebook-id",
        "currentNotebookName": "02_pipeline_test",
        "activityId": "test-activity-id",
        "userId": "test-user-id",
        "userName": "test.user@example.com",
    }
    for key, value in overrides.items():
        if key == "activity_id":
            context["activityId"] = value
        else:
            context[key] = value
    return context


def resolved_runtime_context(**overrides):
    """Return deterministic canonical runtime identity for audit consumers."""
    return resolve_runtime_context(context=runtime_context(**overrides), active_context={})


def test_spark_schema_validation_and_latest_dq_metadata_are_stable(spark_session):
    """Verify spark schema validation and latest dq metadata are stable."""
    df = spark_session.createDataFrame([{"id": 1, "amount": 10.0, "extra": "new"}])
    schema_result = schema_check_core(df, {"id": "bigint", "amount": "double"}, preset="allow_new_columns")
    metadata_df = spark_session.createDataFrame(
        [
            {
                "table_name": "orders",
                "table_id": "orders-key",
                "rule_key": "orders|required",
                "rule_id": "required",
                "column_name": "id",
                "rule_type": "missing_values",
                "rule_parameters_json": json.dumps({"maximum_null_percent": 0}),
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
                "table_id": "orders-key",
                "rule_key": "orders|required",
                "rule_id": "required",
                "column_name": "id",
                "rule_type": "missing_values",
                "rule_parameters_json": json.dumps({"maximum_null_percent": 0}),
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
    assert _load_active_dq_rules(metadata_df, "orders-key") == []


def test_load_active_dq_rules_reconstructs_current_shape_metadata_row(spark_session):
    """Verify load active dq rules reconstructs current shape metadata row."""
    metadata_df = spark_session.createDataFrame(
        [
            {
                "table_name": "orders",
                "table_id": "orders-key",
                "rule_key": "orders|amount_positive",
                "rule_id": "amount_positive",
                "column_name": "amount",
                "rule_type": "value_range",
                "rule_parameters_json": json.dumps({"minimum": 0, "minimum_inclusive": False}),
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

    assert _load_active_dq_rules(metadata_df, "orders-key") == [
        {
            "rule_id": "amount_positive",
            "guardrail_rule_id": "amount_positive",
            "guardrail_version": 1,
            "rule_key": "orders|amount_positive",
            "rule_type": "value_range",
            "columns": ["amount"],
            "severity": "error",
            "description": "Amount must be non-negative",
            "review_status": "governance_approved",
            "minimum": 0,
            "minimum_inclusive": False,
            "maximum_inclusive": True,
        }
    ]


def test_write_guardrail_result_writes_runtime_outcome_to_results_table(spark_session, monkeypatch):
    """Verify guardrail result writer targets METADATA_GUARDRAIL_RESULTS."""
    from fabricops_kit.config.shared import build_table_id
    from fabricops_kit.pipeline import shared as guardrails_shared

    writes = []
    monkeypatch.setattr(guardrails_shared, "write_lakehouse_table_core", lambda df, table, *, target, context, **kwargs: writes.append((df, context["env"], target, table, kwargs)))

    monkeypatch.setattr(
        "fabricops_kit.config.audit.resolve_runtime_context",
        lambda **_kwargs: resolved_runtime_context(activity_id="activity-result-001"),
    )

    guardrails_shared.write_guardrail_result_row(
        spark_session=spark_session,
        config=framework_config(),
        env="dev",
        run_id="run-1",
        dataset_name="sales",
        table_name="orders",
        store_type="lakehouse",
        layer="raw",
        schema_name=None,
        guardrail_type="freshness",
        rule_type="max_age_days",
        result={"guardrail_rule_id": "freshness-rule", "guardrail_version": 1, "status": "failed", "can_continue": False, "severity": "blocking", "message": "too old"},
        rule_key="freshness_orders",
    )

    assert writes[0][2:4] == ("metadata", "METADATA_GUARDRAIL_RESULTS")
    written_row = writes[0][0].collect()[0].asDict()
    assert written_row["guardrail_rule_id"] == "freshness-rule"
    assert written_row["environment_name"] == "dev"
    assert written_row["status"] == "failed"
    assert written_row["can_continue"] is False
    assert written_row["severity"] == "blocking"
    assert written_row["reason"] == "too old"
    assert written_row["_activity_id"] == "activity-result-001"


def test_check_dq_runtime_persists_rule_summaries_and_failed_row_rule_evidence(spark_session, monkeypatch):
    """Persist one summary per rule and one compact evidence row per failed row/rule."""
    from fabricops_kit.config.shared import build_table_id
    from fabricops_kit.pipeline import shared as guardrails_shared

    table_key = build_table_id("lakehouse", "source", None, "orders")
    dataframe = spark_session.createDataFrame(
        [("one", None, "open", 5, 3), ("two", "x", "closed", 1, 2)],
        "business_id string, required_value string, status string, upper int, lower int",
    )
    metadata = spark_session.createDataFrame([
        {
            "guardrail_rule_id": "gr-required", "rule_key": "required", "rule_id": "required",
            "table_id": table_key,
            "environment_name": "dev", "dataset_name": "sales", "table_name": "orders",
            "guardrail_type": "dq", "rule_type": "required_when", "column_name": "required_value",
            "rule_parameters_json": json.dumps({"columns": ["required_value"], "condition_column": "status", "condition_operator": "=", "condition_value": "open"}),
            "severity": "warning", "description": "required when open", "activation_state": "active",
            "review_state": "governance_approved", "action_type": "created", "_committed_at": "2026-01-01T00:00:00Z",
        },
        {
            "guardrail_rule_id": "gr-compare", "rule_key": "compare", "rule_id": "compare",
            "table_id": table_key,
            "environment_name": "dev", "dataset_name": "sales", "table_name": "orders",
            "guardrail_type": "dq", "rule_type": "compare_columns", "column_name": "upper,lower",
            "rule_parameters_json": json.dumps({"columns": ["upper", "lower"], "operator": "<="}),
            "severity": "error", "description": "upper <= lower", "activation_state": "active",
            "review_state": "governance_approved", "action_type": "created", "_committed_at": "2026-01-01T00:00:00Z",
        },
    ])
    writes = []
    monkeypatch.setattr(guardrails_shared, "read_lakehouse_table_core", lambda *args, **kwargs: metadata)
    monkeypatch.setattr(guardrails_shared, "write_lakehouse_table_core", lambda df, table, **kwargs: writes.append((table, df.collect())))
    monkeypatch.setattr(
        "fabricops_kit.config.audit.resolve_runtime_context",
        lambda **_kwargs: resolved_runtime_context(activity_id="activity-dq-001"),
    )

    result = guardrails_shared.check_dq_runtime(
        dataframe, framework_config(), "dev", "orders", table_id=table_key, target="source", store_type="lakehouse",
        schema_name=None, dataset_name="sales", run_id="run-9", row_identity_columns=["business_id"],
    )

    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert result["run_id"] == "run-9"
    assert result["summary"] == {
        "DQ_STATUS": "failed", "DQ_RULE_COUNT": 2, "DQ_FAILED_RULE_COUNT": 2,
        "DQ_WARNING_RULE_COUNT": 1, "DQ_ERROR_RULE_COUNT": 1, "DQ_FAILED_ROW_COUNT": 1,
        "DQ_FAILED_ROW_PERCENT": 50.0, "DQ_CHECKED_AT": result["summary"]["DQ_CHECKED_AT"],
    }
    summaries = next(rows for table, rows in writes if table == "METADATA_GUARDRAIL_RESULTS")
    evidence = next(rows for table, rows in writes if table == "METADATA_GUARDRAIL_ROW_RESULTS")
    assert len(summaries) == 2
    assert {row.run_id for row in summaries} == {"run-9"}
    assert len(evidence) == 2  # the same source row failed both rules
    assert {row.guardrail_rule_id for row in evidence} == {"gr-required", "gr-compare"}
    assert {row.guardrail_result_id for row in evidence} == {row.guardrail_result_id for row in summaries}
    assert all(json.loads(row.row_identity) == {"business_id": "one"} for row in evidence)
    compare = next(row for row in evidence if row.guardrail_rule_id == "gr-compare")
    assert json.loads(compare.involved_columns_json) == ["upper", "lower"]
    assert json.loads(compare.failed_values_json) == {"upper": 5, "lower": 3}
    conditional = next(row for row in evidence if row.guardrail_rule_id == "gr-required")
    assert json.loads(conditional.involved_columns_json) == ["required_value", "status"]
    assert json.loads(conditional.failed_values_json) == {"required_value": None, "status": "open"}
    assert conditional.run_id == "run-9"


def test_check_dq_runtime_writes_no_row_evidence_when_all_rules_pass(spark_session, monkeypatch):
    """Avoid empty row-evidence writes while retaining a passing rule summary."""
    from fabricops_kit.config.shared import build_table_id
    from fabricops_kit.pipeline import shared as guardrails_shared

    table_key = build_table_id("lakehouse", "source", None, "orders")
    dataframe = spark_session.createDataFrame([("one", "ok")], "row_uuid string, value string")
    metadata = spark_session.createDataFrame([{
        "guardrail_rule_id": "gr-allowed", "rule_key": "allowed", "rule_id": "allowed",
        "table_id": table_key,
        "environment_name": "dev", "table_name": "orders", "guardrail_type": "dq",
        "rule_type": "allowed_values", "column_name": "value",
        "rule_parameters_json": json.dumps({"columns": ["value"], "allowed_values": ["ok"]}),
        "severity": "error", "activation_state": "active", "review_state": "governance_approved",
        "action_type": "created", "_committed_at": "2026-01-01T00:00:00Z",
    }])
    writes = []
    monkeypatch.setattr(guardrails_shared, "read_lakehouse_table_core", lambda *args, **kwargs: metadata)
    monkeypatch.setattr(
        guardrails_shared,
        "write_lakehouse_table_core",
        lambda df, table, **kwargs: writes.append((table, df.collect())),
    )
    activities = iter(("activity-auto-run-1", "activity-auto-run-2"))
    monkeypatch.setattr(
        "fabricops_kit.config.audit.resolve_runtime_context",
        lambda **_kwargs: resolved_runtime_context(activity_id=next(activities)),
    )

    result = guardrails_shared.check_dq_runtime(
        dataframe, framework_config(), "dev", "orders", table_id=table_key, target="source", store_type="lakehouse", schema_name=None,
    )

    assert result["status"] == "passed"
    assert result["run_id"] == "activity-auto-run-1"
    assert result["summary"]["DQ_FAILED_ROW_COUNT"] == 0
    assert [table for table, _rows in writes] == ["METADATA_GUARDRAIL_RESULTS"]
    assert {row.run_id for row in writes[0][1]} == {"activity-auto-run-1"}

    second = guardrails_shared.check_dq_runtime(
        dataframe, framework_config(), "dev", "orders", table_id=table_key, target="source",
        store_type="lakehouse", schema_name=None,
    )
    assert second["run_id"] == "activity-auto-run-2"
    assert {rows[0].run_id for _table, rows in writes} == {
        "activity-auto-run-1", "activity-auto-run-2",
    }
