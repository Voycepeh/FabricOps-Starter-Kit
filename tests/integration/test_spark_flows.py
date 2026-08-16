"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import json

import pytest

from fabricops_kit.config.shared import resolve_runtime_context
from fabricops_kit.pipeline.guardrails_shared import _load_active_dq_rules, _prepare_dq_profile_input_rows, run_active_dq_guardrail
from fabricops_kit.pipeline.guardrails_shared import stop_if_failed, schema_check_core
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
    schema_result = schema_check_core(df, {"id": "bigint", "amount": "double"}, preset="allow_new_columns")
    metadata_df = spark_session.createDataFrame(
        [
            {
                "table_name": "orders",
                "metadata_table_key": "orders-key",
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
                "metadata_table_key": "orders-key",
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
                "metadata_table_key": "orders-key",
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


def test_load_active_dq_rules_reconstructs_current_governance_metadata(spark_session, monkeypatch):
    """Verify load active dq rules reconstructs current governance metadata."""
    from fabricops_kit.pipeline import guardrails_shared as dq_runtime
    from fabricops_kit.widgets import shared as governance_authoring
    from tests.helpers import framework_config

    writes = []
    monkeypatch.setattr(
        governance_authoring,
        "write_lakehouse_table_core",
        lambda df, table, *, target, context, **kwargs: writes.append((table, df)),
    )
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

    monkeypatch.setattr(
        "fabricops_kit.config.audit.resolve_runtime_context",
        lambda **_kwargs: resolved_runtime_context(),
    )
    config = framework_config()

    governance_authoring.record_table_governance(
        config,
        "dev",
        profile_rows,
        spark_session=spark_session,
        guardrail_rule_reviews=[
            {
                "rule_id": "amount_positive",
                "column_name": "amount",
                "rule_type": "value_range",
                "columns": ["amount"],
                "minimum": 0,
                "minimum_inclusive": False,
                "severity": "error",
                "description": "Amount must be non-negative",
                "commit": True,
            }
        ],
        approved_by="reviewer@example.com",
    )

    assert [table for table, _ in writes] == [governance_authoring.GUARDRAIL_TABLE]
    persisted = writes[0][1].collect()[0]
    assert persisted["guardrail_type"] == "dq"
    loaded = dq_runtime._load_active_dq_rules(writes[0][1], persisted["metadata_table_key"])

    assert loaded == [
        {
            "rule_id": "amount_positive",
            "guardrail_rule_id": persisted["rule_id"],
            "rule_key": persisted["rule_key"],
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



def _dq_metadata_df(spark_session, rows):
    from fabricops_kit.config.shared import build_metadata_table_key

    schema = (
        "environment_name string, dataset_name string, table_name string, metadata_table_key string, rule_key string, rule_id string, "
        "column_name string, rule_type string, rule_parameters_json string, severity string, description string, "
        "is_active boolean, review_status string, approved_by string, approved_at string, action_type string, "
        "_committed_at string, _committed_by string"
    )
    table_key = build_metadata_table_key("lakehouse", "", None, "orders")
    return spark_session.createDataFrame(
        [{**row, "metadata_table_key": row.get("metadata_table_key", table_key)} for row in rows],
        schema=schema,
    )


def test_run_active_dq_guardrail_returns_passed_when_no_active_rules(spark_session, monkeypatch):
    """Verify the internal active DQ guardrail returns passed when no active rules."""
    from fabricops_kit.pipeline import guardrails_shared as governance

    df = spark_session.createDataFrame([{"order_id": "A", "status": "active", "amount": 10.0}])
    metadata_df = _dq_metadata_df(spark_session, [])
    monkeypatch.setattr(governance, "read_lakehouse_table_core", lambda *args, **kwargs: metadata_df)

    result = run_active_dq_guardrail(df, object(), "dev", "sales", "orders", spark_session=spark_session)

    assert result["status"] == "passed"
    assert result["can_continue"] is True
    assert result["checks"] == []
    assert result["message"] == "No active guardrail DQ rules found."
    assert result["summary"]["DQ_RULE_COUNT"] == 0
    assert {"_dq_check_status", "_dq_failed_rules"}.issubset(result["dataframe"].columns)



def test_run_active_dq_guardrail_result_write_toggle_targets_results(spark_session, monkeypatch):
    """Verify DQ enforcement writes result rows only when enabled."""
    from fabricops_kit.pipeline import guardrails_shared as governance

    df = spark_session.createDataFrame([{"order_id": "A", "status": "active", "amount": 10.0}])
    metadata_df = _dq_metadata_df(spark_session, [])
    writes = []
    monkeypatch.setattr(governance, "read_lakehouse_table_core", lambda *args, **kwargs: metadata_df)
    monkeypatch.setattr(governance, "write_lakehouse_table_core", lambda df, table, *, target, context, **kwargs: writes.append((df, context["env"], target, table, kwargs)))

    config = framework_config()
    monkeypatch.setattr(
        "fabricops_kit.config.audit.resolve_runtime_context",
        lambda **_kwargs: resolved_runtime_context(activity_id="activity-dq-001"),
    )

    run_active_dq_guardrail(df, config, "dev", "sales", "orders", spark_session=spark_session, run_id="activity-dq-001", write_results=False)
    assert writes == []

    monkeypatch.setattr(
        "fabricops_kit.config.audit.resolve_runtime_context",
        lambda **_kwargs: resolved_runtime_context(activity_id="activity-dq-002"),
    )
    run_active_dq_guardrail(df, config, "dev", "sales", "orders", spark_session=spark_session, run_id="activity-dq-002", write_results=True)

    assert writes[0][2:4] == ("metadata", "METADATA_GUARDRAIL_RESULTS")
    row = writes[0][0].collect()[0].asDict()
    assert row["guardrail_type"] == "dq"
    assert row["_activity_id"] == "activity-dq-002"
    assert row["status"] == "passed"

def test_run_active_dq_guardrail_warning_failure_can_continue(spark_session, monkeypatch):
    """Verify the internal active DQ guardrail warning failure can continue."""
    from fabricops_kit.pipeline import guardrails_shared as governance

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
                "rule_type": "allowed_values",
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
    monkeypatch.setattr(governance, "read_lakehouse_table_core", lambda *args, **kwargs: metadata_df)

    result = run_active_dq_guardrail(df, object(), "dev", "sales", "orders", spark_session=spark_session)

    assert result["status"] == "warning"
    assert result["can_continue"] is True
    assert result["checks"][0]["status"] == "warning"
    assert result["checks"][0]["failed_count"] == 1
    assert result["checks"][0]["total_count"] == 1
    assert result["checks"][0]["failed_percent"] == 100.0



def test_run_active_dq_guardrail_warning_failure_adds_technical_columns_and_preserves_rows(spark_session, monkeypatch):
    """Verify the internal active DQ guardrail warning failure adds technical columns and preserves rows."""
    from fabricops_kit.pipeline import guardrails_shared as governance

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
                "rule_type": "allowed_values",
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
                "rule_type": "value_range",
                "rule_parameters_json": json.dumps({"minimum": 0, "minimum_inclusive": False}),
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
    monkeypatch.setattr(governance, "read_lakehouse_table_core", lambda *args, **kwargs: metadata_df)

    result = run_active_dq_guardrail(df, object(), "dev", "sales", "orders", spark_session=spark_session)
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


def test_run_active_dq_guardrail_error_failure_blocks(spark_session, monkeypatch):
    """Verify the internal active DQ guardrail error failure blocks."""
    from fabricops_kit.pipeline import guardrails_shared as governance

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
                "rule_type": "missing_values",
                "rule_parameters_json": json.dumps({"maximum_null_percent": 0}),
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
    monkeypatch.setattr(governance, "read_lakehouse_table_core", lambda *args, **kwargs: metadata_df)

    result = run_active_dq_guardrail(df, object(), "dev", "sales", "orders", spark_session=spark_session)

    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert result["checks"][0]["status"] == "failed"
    with pytest.raises(Exception, match="Guardrail blocked execution"):
        stop_if_failed(result)


def test_run_active_dq_guardrail_mixed_warning_and_error_failures_return_failed(spark_session, monkeypatch):
    """Verify the internal active DQ guardrail mixed warning and error failures return failed."""
    from fabricops_kit.pipeline import guardrails_shared as governance

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
                "rule_type": "missing_values",
                "rule_parameters_json": json.dumps({"maximum_null_percent": 0}),
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
                "rule_type": "allowed_values",
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
    monkeypatch.setattr(governance, "read_lakehouse_table_core", lambda *args, **kwargs: metadata_df)

    result = run_active_dq_guardrail(df, object(), "dev", "sales", "orders", spark_session=spark_session)

    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert {check["status"] for check in result["checks"]} == {"failed", "warning"}


def test_run_active_dq_guardrail_supports_current_v1_metadata_shape(spark_session, monkeypatch):
    """Verify the internal active DQ guardrail supports current v1 metadata shape."""
    from fabricops_kit.pipeline import guardrails_shared as governance

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
                "rule_type": "missing_values",
                "rule_parameters_json": json.dumps({"maximum_null_percent": 0}),
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
    monkeypatch.setattr(governance, "read_lakehouse_table_core", lambda *args, **kwargs: metadata_df)

    result = run_active_dq_guardrail(df, object(), "dev", "sales", "orders", spark_session=spark_session)

    assert result["status"] == "passed"
    assert result["can_continue"] is True
    assert result["checks"][0]["rule_type"] == "missing_values"


def test_write_catalogue_evidence_writes_profile_evidence_without_result_fields(spark_session, monkeypatch):
    """Verify catalogue evidence excludes runtime guardrail result fields."""
    from fabricops_kit.pipeline import profile_dataframe
    from fabricops_kit.pipeline import shared as pipeline_shared

    writes = []
    monkeypatch.setattr(
        pipeline_shared,
        "write_lakehouse_table_core",
        lambda df, table, *, target, context, **kwargs: writes.append((df, context["env"], target, table, kwargs)),
    )
    df = spark_session.createDataFrame([(1, "open")], "id int, status string")
    profile_df = profile_dataframe(df)

    result = pipeline_shared.write_catalogue_evidence(
        {"orders": profile_df},
        {"orders": {"dataset_name": "sales", "table_name": "orders", "stage": "source", "fabric_store_target": "source", "profile_mode": "static_data"}},
        config=framework_config(),
        env="dev",
        run_id="run-1",
        context={"runtime_context": runtime_context(activity_id="activity-profile-001")},
        stability_results={"orders": {"status": "baseline_created", "can_continue": True, "stability_check_enabled": True, "profile_mode": "static_data", "stability_status": "baseline_created", "stability_can_continue": True}},
    )

    assert result == {"orders": "written"}
    assert writes[0][2:4] == ("metadata", "METADATA_DATA_PROFILED")
    assert writes[0][4]["mode"] == "append"
    assert "stability_status" not in writes[0][0].columns
    assert "freshness_status" not in writes[0][0].columns
    assert "dq_status" not in writes[0][0].columns
    assert "profile_mode" in writes[0][0].columns
    assert "load_behavior" not in writes[0][0].columns



def test_write_catalogue_evidence_writes_explicit_fabric_store_target(spark_session, monkeypatch):
    """Verify catalogue evidence writes only the canonical FabricStore target."""
    from fabricops_kit.pipeline import profile_dataframe
    from fabricops_kit.pipeline import shared as pipeline_shared

    writes = []
    monkeypatch.setattr(
        pipeline_shared,
        "write_lakehouse_table_core",
        lambda df, table, *, target, context, **kwargs: writes.append((df, context["env"], target, table, kwargs)),
    )
    df = spark_session.createDataFrame([(1, "open")], "id int, status string")
    profile_df = profile_dataframe(df)
    definitions = {
        "explicit": {
            "dataset_name": "sales",
            "table_name": "orders",
            "stage": "source",
            "fabric_store_target": " Product ",
            "target_layer": "Unified",
            "layer": "raw",
        }
    }

    result = pipeline_shared.write_catalogue_evidence(
        {"explicit": profile_df},
        definitions,
        config=framework_config(),
        env="dev",
        run_id="run-1",
        context={"runtime_context": runtime_context(activity_id="activity-profile-002")},
    )

    assert result == {"explicit": "written"}
    row = writes[0][0].select("table_name", "fabric_store_target").first().asDict()
    assert row == {"table_name": "orders", "fabric_store_target": "product"}


def test_write_catalogue_evidence_does_not_fallback_to_layer_fields(spark_session, monkeypatch):
    """Verify writer requires fabric_store_target instead of target_layer/layer fallbacks."""
    from fabricops_kit.pipeline import profile_dataframe
    from fabricops_kit.pipeline import shared as pipeline_shared

    monkeypatch.setattr(pipeline_shared, "write_lakehouse_table_core", lambda *args, **kwargs: None)
    df = spark_session.createDataFrame([(1,)], "id int")
    profile_df = profile_dataframe(df)

    with pytest.raises(KeyError):
        pipeline_shared.write_catalogue_evidence(
            {"target_layer_only": profile_df},
            {"target_layer_only": {"table_name": "orders", "target_layer": "product", "layer": "raw"}},
            config=framework_config(),
            env="dev",
            run_id="run-1",
            context={"runtime_context": runtime_context(activity_id="activity-profile-003")},
        )


def test_write_guardrail_result_writes_runtime_outcome_to_results_table(spark_session, monkeypatch):
    """Verify guardrail result writer targets METADATA_GUARDRAIL_RESULTS."""
    from fabricops_kit.config.shared import build_metadata_table_key
    from fabricops_kit.pipeline import guardrails_shared

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
        result={"status": "failed", "can_continue": False, "severity": "blocking", "message": "too old"},
        rule_key="freshness_orders",
    )

    assert writes[0][2:4] == ("metadata", "METADATA_GUARDRAIL_RESULTS")
    written_row = writes[0][0].collect()[0].asDict()
    expected_table_key = build_metadata_table_key("lakehouse", "raw", None, "orders")
    assert written_row["metadata_table_key"] == expected_table_key
    assert written_row["environment_name"] == "dev"
    assert written_row["guardrail_type"] == "freshness"
    assert written_row["status"] == "failed"
    assert written_row["can_continue"] is False
    assert written_row["severity"] == "blocking"
    assert written_row["reason"] == "too old"
    assert written_row["_activity_id"] == "activity-result-001"

def test_write_catalogue_evidence_persists_each_profile_behavior_watermark(spark_session, monkeypatch):
    """Verify changing-data catalogue writes retain per-watermark baseline fields."""
    from fabricops_kit.pipeline import profile_dataframe
    from fabricops_kit.pipeline import shared as pipeline_shared

    writes = []
    monkeypatch.setattr(
        pipeline_shared,
        "write_lakehouse_table_core",
        lambda df, table, *, target, context, **kwargs: writes.append((df, context["env"], target, table, kwargs)),
    )
    df = spark_session.createDataFrame([(1, "2026-06-14"), (2, "2026-06-15")], "id int, business_date string")
    profile_df = profile_dataframe(df)

    result = pipeline_shared.write_catalogue_evidence(
        {"orders": profile_df},
        {"orders": {"dataset_name": "sales", "table_name": "orders", "stage": "source", "fabric_store_target": "source", "profile_mode": "changing_data"}},
        config=framework_config(),
        env="dev",
        run_id="run-1",
        context={"runtime_context": runtime_context(activity_id="activity-profile-004")},
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


def test_check_dq_runtime_persists_rule_summaries_and_failed_row_rule_evidence(spark_session, monkeypatch):
    """Persist one summary per rule and one compact evidence row per failed row/rule."""
    from fabricops_kit.config.shared import build_metadata_table_key
    from fabricops_kit.pipeline import guardrails_shared

    table_key = build_metadata_table_key("lakehouse", "source", None, "orders")
    dataframe = spark_session.createDataFrame(
        [("one", None, "open", 5, 3), ("two", "x", "closed", 1, 2)],
        "business_id string, required_value string, status string, upper int, lower int",
    )
    metadata = spark_session.createDataFrame([
        {
            "guardrail_rule_id": "gr-required", "rule_key": "required", "rule_id": "required",
            "metadata_table_key": table_key,
            "environment_name": "dev", "dataset_name": "sales", "table_name": "orders",
            "guardrail_type": "dq", "rule_type": "required_when", "column_name": "required_value",
            "rule_parameters_json": json.dumps({"columns": ["required_value"], "condition_column": "status", "condition_operator": "=", "condition_value": "open"}),
            "severity": "warning", "description": "required when open", "activation_state": "active",
            "review_state": "governance_approved", "action_type": "created", "_committed_at": "2026-01-01T00:00:00Z",
        },
        {
            "guardrail_rule_id": "gr-compare", "rule_key": "compare", "rule_id": "compare",
            "metadata_table_key": table_key,
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
        dataframe, framework_config(), "dev", "orders", target="source", store_type="lakehouse",
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
    from fabricops_kit.config.shared import build_metadata_table_key
    from fabricops_kit.pipeline import guardrails_shared

    table_key = build_metadata_table_key("lakehouse", "source", None, "orders")
    dataframe = spark_session.createDataFrame([("one", "ok")], "row_uuid string, value string")
    metadata = spark_session.createDataFrame([{
        "guardrail_rule_id": "gr-allowed", "rule_key": "allowed", "rule_id": "allowed",
        "metadata_table_key": table_key,
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
        dataframe, framework_config(), "dev", "orders", target="source", store_type="lakehouse", schema_name=None,
    )

    assert result["status"] == "passed"
    assert result["run_id"] == "activity-auto-run-1"
    assert result["summary"]["DQ_FAILED_ROW_COUNT"] == 0
    assert [table for table, _rows in writes] == ["METADATA_GUARDRAIL_RESULTS"]
    assert {row.run_id for row in writes[0][1]} == {"activity-auto-run-1"}

    second = guardrails_shared.check_dq_runtime(
        dataframe, framework_config(), "dev", "orders", target="source",
        store_type="lakehouse", schema_name=None,
    )
    assert second["run_id"] == "activity-auto-run-2"
    assert {rows[0].run_id for _table, rows in writes} == {
        "activity-auto-run-1", "activity-auto-run-2",
    }
