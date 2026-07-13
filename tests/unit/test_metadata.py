"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

import fabricops_kit
import fabricops_kit.widgets.shared as agreement
import fabricops_kit.widgets.widget_render_data_steward as steward_widget
from fabricops_kit.config import audit as audit_helpers
from fabricops_kit.config import metadata_keys
from fabricops_kit.widgets import notebook_registry
from tests.helpers import FakeSpark, framework_config

pytestmark = pytest.mark.unit


def test_runtime_audit_fields_resolve_fabric_context_and_allow_overrides(fake_notebookutils):
    """Verify runtime audit fields resolve fabric context and allow overrides."""
    audit = audit_helpers.build_runtime_audit_fields(
        config=framework_config(),
        env="dev",
        runtime_context={"activityId": "manual-activity"},
    )

    assert audit["_workspace_name"] == "FabricOps Test Workspace"
    assert audit["_committed_by"] == "fabricops.test@example.com"
    assert audit["_metadata_lakehouse_name"] == "lh_metadata_dev"
    assert audit["_activity_id"] == "manual-activity"


def test_notebook_registration_uses_configured_metadata_route(monkeypatch):
    """Verify notebook registration uses configured metadata route."""
    writes = []

    monkeypatch.setattr(
        notebook_registry,
        "write_lakehouse_table_core",
        lambda df, table, *, target, context, **kwargs: writes.append((df, context["env"], target, table, kwargs)),
    )
    monkeypatch.setattr(
        notebook_registry,
        "_runtime_context",
        lambda: {
            "currentWorkspaceId": "workspace-id",
            "currentWorkspaceName": "Workspace Name",
            "currentNotebookId": "notebook-id",
            "currentNotebookName": "02_pipeline_orders_pipeline",
            "userName": "user@example.com",
            "userId": "user-id",
            "activityId": "activity-id",
        },
    )

    row = notebook_registry.register_current_notebook(
        spark=FakeSpark(),
        config=framework_config(),
        env="dev",
        agreement_id="DA-1",
        notebook_type="02_pipeline",
        environment_name="dev",
        dataset_name="orders",
        table_name="fact_orders",
    )

    assert list(row) == notebook_registry.NOTEBOOK_REGISTRY_FIELDS
    assert row["notebook_url"] == "https://app.fabric.microsoft.com/groups/workspace-id/notebooks/notebook-id"
    assert [(env, target, table) for _, env, target, table, _ in writes] == [
        ("dev", "metadata", notebook_registry.NOTEBOOK_REGISTRY_TABLE),
    ]


def test_current_notebook_active_registrations_filters_current_runtime_rows(monkeypatch):
    """Verify current notebook active registrations filters current runtime rows."""
    rows = [
        {
            "agreement_id": "DA-1",
            "agreement_version": "1.0.0",
            "_committed_at": "2026-01-02T00:00:00Z",
            "_notebook_id": "notebook-id",
            "_notebook_name": "02_pipeline_orders",
            "registration_status": "active",
            "notebook_type": "02_pipeline",
            "environment_name": "dev",
            "registration_role": "primary",
        },
        {
            "agreement_id": "DA-2",
            "agreement_version": "1.0.0",
            "_committed_at": "2026-01-01T00:00:00Z",
            "_notebook_id": "notebook-id",
            "_notebook_name": "02_pipeline_orders",
            "registration_status": "superseded",
            "notebook_type": "02_pipeline",
            "environment_name": "dev",
            "registration_role": "primary",
        },
        {
            "agreement_id": "DA-3",
            "agreement_version": "1.0.0",
            "_committed_at": "2026-01-03T00:00:00Z",
            "_notebook_id": "other",
            "_notebook_name": "02_pipeline_other",
            "registration_status": "active",
            "notebook_type": "02_pipeline",
            "environment_name": "dev",
            "registration_role": "primary",
        },
    ]
    monkeypatch.setattr(notebook_registry, "_runtime_context", lambda: {"currentNotebookId": "notebook-id"})
    monkeypatch.setattr(notebook_registry, "read_lakehouse_table_core", lambda *args, **kwargs: rows)

    active = notebook_registry.current_notebook_active_registrations(
        object(), config=framework_config(), env="dev", notebook_type="02_pipeline", environment_name="dev", registration_role="primary"
    )

    assert len(active) == 1
    assert active[0]["_notebook_id"] == "notebook-id"


def test_notebook_registry_read_requires_configured_metadata_route():
    """Verify notebook registry read requires configured metadata route."""
    class Spark:
        def table(self, table):
            raise AssertionError(f"notebook registry must not call spark.table: {table}")

    with pytest.raises(ValueError, match="config and env are required"):
        notebook_registry._load_notebook_registry(Spark(), missing_ok=True)


def test_metadata_key_builders_are_stable_for_governance_and_dq_rules():
    """Verify metadata key builders are stable for governance and dq rules."""
    table_key = metadata_keys._build_metadata_table_key(" DEV ", "Sales", "Orders")
    column_key = metadata_keys._build_metadata_column_key("dev", "sales", "orders", "Order_ID")
    dq_key = metadata_keys._build_dq_rule_key("dev", "sales", "orders", "order_id_required")

    assert table_key == metadata_keys._build_metadata_table_key("dev", "sales", "orders")
    assert column_key == metadata_keys._build_metadata_column_key("DEV", "SALES", "ORDERS", " order_id ")
    assert dq_key == metadata_keys._build_dq_rule_key("DEV", "SALES", "ORDERS", " order_id_required ")
    assert len({table_key, column_key, dq_key}) == 3
    assert all(len(value) == 64 for value in (table_key, column_key, dq_key))


def test_data_agreement_metadata_write_and_read_use_configured_metadata_route(monkeypatch):
    """Verify data agreement metadata write and read use configured metadata route."""
    writes = []
    steward_rows = []

    def write_table(df, table, *, target, context, **kwargs):
        assert context["env"] == "dev"
        assert target == "metadata"
        writes.append((table, df.rows, context["env"], target, kwargs))
        if table == agreement.DATA_STEWARD_TABLE:
            steward_rows.extend(df.rows)

    def read_table(table, *, target, context, **kwargs):
        assert (context["env"], target) == ("dev", "metadata")
        if table == agreement.DATA_STEWARD_TABLE:
            return steward_rows
        return []

    monkeypatch.setattr(agreement, "write_lakehouse_table_core", write_table)
    monkeypatch.setattr(agreement, "read_lakehouse_table_core", read_table)

    steward = steward_widget._create_or_update_data_steward(
        spark=FakeSpark(),
        config=framework_config(),
        env="dev",
        values={
            "steward_name": "Ops Steward",
            "steward_role": "Data Owner",
            "contact": "ops@example.com",
            "effective_from": "2026-01-01",
            "is_active": "true",
        },
        committed_by="reviewer@example.com",
        committed_at="2026-01-02T00:00:00+00:00",
        runtime_context={
            "currentWorkspaceId": "workspace-id",
            "currentWorkspaceName": "Workspace",
            "currentNotebookId": "notebook-id",
            "currentNotebookName": "01_agreement",
            "activityId": "activity-id",
        },
    )

    read_back = agreement.list_data_stewards(framework_config(), "dev", spark_session=FakeSpark())

    assert steward["steward_id"]
    assert read_back == [steward]
    assert writes[0][0] == agreement.DATA_STEWARD_TABLE
    assert writes[0][2:4] == ("dev", "metadata")


def test_deleted_metadata_helpers_are_not_referenced_by_active_modules():
    """Verify deleted metadata helpers are not referenced by active modules."""
    deleted_helpers = (
        "_get" + "_notebook_registry_schema",
        "_notebook_registry_base_schema",
        "_default_evidence_types",
        "_build_evidence_row",
        "_extract_columns_from_profile",
        "_normalise_records_by_column",
        "_write_metadata_rows",
        "_write_metadata_rows" + "_leg" + "acy",
        "_write_column_business_context",
        "_write_column_governance_context",
        "_latest_registration_events",
    )
    root = Path(__file__).parents[2] / "src" / "fabricops_kit"
    offenders = []
    for path in root.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for helper in deleted_helpers:
            if helper in text:
                offenders.append(f"{path.name}:{helper}")

    assert offenders == []


def test_public_callable_list_includes_guardrail_authoring_helpers_after_metadata_cleanup():
    """Verify public callable list includes guardrail authoring helpers."""
    expected_public_callables = [
        'FabricStore',
        'PathConfig',
        'GovernanceConfig',
        'DataAgreementConfig',
        'FrameworkConfig',
        'ConfigSmokeCheckResult',
        'NotebookSetupContext',
        'setup_notebook',
        'setup_metadata_tables',
        'read_lakehouse_table',
        'write_lakehouse_table',
        'read_lakehouse_csv',
        'read_lakehouse_parquet',
        'read_lakehouse_excel',
        'read_warehouse_table',
        'read_warehouse_query',
        'write_warehouse_table',
    'profile_and_register_dataframe',
        'profile_dataframe',
        'profile_frequency_distribution',
        'display_guardrail_results',
        'prepare_pipeline_table_configs',
        'run_table_guardrails',
        'write_pipeline_run_summary',
        'widget_render_data_steward',
        'widget_render_data_agreement',
        'widget_render_agreement_evidence',
        'widget_pipeline_bootstrap',
        'widget_select_guardrail_target',
        'widget_enrich_table_metadata',
        'widget_author_schema_freshness_profile_rules',
        'widget_browse_metadata_catalogue',
        'widget_author_dq_rules',
        'widget_review_guardrail_governance',
    ]
    assert fabricops_kit.__all__ == expected_public_callables
    assert len(fabricops_kit.__all__) == len(expected_public_callables)
    assert "widget_pipeline_bootstrap" in fabricops_kit.__all__
    assert "get_selected_agreement" not in fabricops_kit.__all__


def test_runtime_audit_fields_support_explicit_non_fabric_context():
    """Verify injected runtime context supports local audit resolution."""
    audit = audit_helpers.build_runtime_audit_fields(
        committed_by="test.user@example.com",
        committed_at="2026-07-08T12:00:00+08:00",
        metadata_lakehouse_name="test_metadata",
        runtime_context={
            "currentWorkspaceId": "workspace-id",
            "currentWorkspaceName": "test-workspace",
            "currentNotebookId": "notebook-id",
            "currentNotebookName": "02_pipeline_test",
            "activityId": "activity-id",
        },
    )

    assert list(audit) == [
        "_committed_by",
        "_committed_at",
        "_workspace_id",
        "_workspace_name",
        "_notebook_id",
        "_notebook_name",
        "_metadata_lakehouse_name",
        "_activity_id",
    ]
    assert audit["_committed_at"].isoformat() == "2026-07-08T12:00:00+08:00"
    assert audit["_metadata_lakehouse_name"] == "test_metadata"


def test_runtime_audit_fields_support_legacy_runtime_aliases():
    """Verify runtime alias fields resolve workspace and notebook identity."""
    audit = audit_helpers.build_runtime_audit_fields(
        committed_by="user@example.com",
        committed_at="2026-07-08T12:00:00+00:00",
        metadata_lakehouse_name="metadata",
        runtime_context={
            "workspaceId": "workspace-id",
            "workspaceName": "workspace-name",
            "notebookId": "notebook-id",
            "notebookName": "notebook-name",
            "activityId": "activity-id",
        },
    )

    assert audit["_workspace_id"] == "workspace-id"
    assert audit["_workspace_name"] == "workspace-name"
    assert audit["_notebook_id"] == "notebook-id"
    assert audit["_notebook_name"] == "notebook-name"


def test_runtime_audit_fields_report_all_missing_and_reject_unknown():
    """Verify invalid audit placeholders fail with one complete error."""
    with pytest.raises(ValueError) as exc:
        audit_helpers.build_runtime_audit_fields(
            committed_by="unknown",
            metadata_lakehouse_name=" ",
            runtime_context={"currentWorkspaceId": "None", "currentNotebookName": "unknown_notebook"},
        )

    message = str(exc.value)
    for field in [
        "_committed_by",
        "_workspace_id",
        "_workspace_name",
        "_notebook_id",
        "_notebook_name",
        "_metadata_lakehouse_name",
        "_activity_id",
    ]:
        assert field in message


def test_guardrail_result_write_fails_before_persistence_when_audit_missing(monkeypatch):
    """Verify metadata result writes fail before persistence when audit cannot resolve."""
    from fabricops_kit.pipeline import metadata_evidence

    monkeypatch.setattr(
        metadata_evidence,
        "write_lakehouse_table_core",
        lambda *_args, **_kwargs: pytest.fail("metadata write should not run without audit fields"),
    )

    with pytest.raises(ValueError, match="Cannot build metadata audit fields"):
        metadata_evidence._write_guardrail_result_row(
            spark_session=FakeSpark(),
            config=framework_config(),
            env="dev",
            run_id="run-1",
            dataset_name="sales",
            table_name="orders",
            guardrail_type="schema",
            rule_type="schema",
            result={"status": "failed"},
        )
