"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

import fabricops_kit
import fabricops_kit.data_agreement as agreement
import fabricops_kit.metadata as metadata
from tests.helpers import FakeSpark, framework_config

pytestmark = pytest.mark.unit


def test_runtime_audit_fields_resolve_fabric_context_and_allow_overrides(fake_notebookutils):
    """Verify runtime audit fields resolve fabric context and allow overrides."""
    audit = metadata._build_runtime_audit_fields(
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
        metadata,
        "write_lakehouse_table",
        lambda df, config, env, target, table, **kwargs: writes.append((df, env, target, table, kwargs)),
    )
    monkeypatch.setattr(
        metadata,
        "_runtime_context",
        lambda: {
            "currentWorkspaceId": "workspace-id",
            "currentWorkspaceName": "Workspace Name",
            "currentNotebookId": "notebook-id",
            "currentNotebookName": "02_pipeline_orders_pipeline",
            "userName": "user@example.com",
            "userId": "user-id",
        },
    )

    row = metadata._register_current_notebook(
        spark=FakeSpark(),
        config=framework_config(),
        env="dev",
        agreement_id="DA-1",
        notebook_type="02_pipeline",
        environment_name="dev",
        dataset_name="orders",
        table_name="fact_orders",
    )

    assert list(row) == metadata.NOTEBOOK_REGISTRY_FIELDS
    assert row["notebook_url"] == "https://app.fabric.microsoft.com/groups/workspace-id/notebooks/notebook-id"
    assert [(env, target, table) for _, env, target, table, _ in writes] == [
        ("dev", "metadata", metadata.NOTEBOOK_REGISTRY_TABLE),
    ]


def test_current_notebook_active_registrations_filters_current_runtime_rows(monkeypatch):
    """Verify current notebook active registrations filters current runtime rows."""
    rows = [
        {
            "agreement_id": "DA-1",
            "registration_id": "r1",
            "registered_at": "2026-01-02T00:00:00Z",
            "notebook_id": "notebook-id",
            "notebook_name": "02_pipeline_orders",
            "registration_status": "active",
            "notebook_type": "02_pipeline",
            "environment_name": "dev",
            "registration_role": "primary",
        },
        {
            "agreement_id": "DA-2",
            "registration_id": "r2",
            "registered_at": "2026-01-01T00:00:00Z",
            "notebook_id": "notebook-id",
            "notebook_name": "02_pipeline_orders",
            "registration_status": "superseded",
            "notebook_type": "02_pipeline",
            "environment_name": "dev",
            "registration_role": "primary",
        },
        {
            "agreement_id": "DA-3",
            "registration_id": "r3",
            "registered_at": "2026-01-03T00:00:00Z",
            "notebook_id": "other",
            "notebook_name": "02_pipeline_other",
            "registration_status": "active",
            "notebook_type": "02_pipeline",
            "environment_name": "dev",
            "registration_role": "primary",
        },
    ]
    monkeypatch.setattr(metadata, "_runtime_context", lambda: {"currentNotebookId": "notebook-id"})
    monkeypatch.setattr(metadata, "read_lakehouse_table", lambda *args, **kwargs: rows)

    active = metadata._current_notebook_active_registrations(
        object(), config=framework_config(), env="dev", notebook_type="02_pipeline", environment_name="dev", registration_role="primary"
    )

    assert len(active) == 1
    assert active[0]["notebook_id"] == "notebook-id"


def test_notebook_registry_read_requires_configured_metadata_route():
    """Verify notebook registry read requires configured metadata route."""
    class Spark:
        def table(self, table):
            raise AssertionError(f"notebook registry must not call spark.table: {table}")

    with pytest.raises(ValueError, match="config and env are required"):
        metadata._load_notebook_registry(Spark(), missing_ok=True)


def test_metadata_key_builders_are_stable_for_governance_and_dq_rules():
    """Verify metadata key builders are stable for governance and dq rules."""
    table_key = metadata._build_metadata_table_key(" DEV ", "Sales", "Orders")
    column_key = metadata._build_metadata_column_key("dev", "sales", "orders", "Order_ID")
    dq_key = metadata._build_dq_rule_key("dev", "sales", "orders", "order_id_required")

    assert table_key == metadata._build_metadata_table_key("dev", "sales", "orders")
    assert column_key == metadata._build_metadata_column_key("DEV", "SALES", "ORDERS", " order_id ")
    assert dq_key == metadata._build_dq_rule_key("DEV", "SALES", "ORDERS", " order_id_required ")
    assert len({table_key, column_key, dq_key}) == 3
    assert all(len(value) == 64 for value in (table_key, column_key, dq_key))


def test_data_agreement_metadata_write_and_read_use_configured_metadata_route(monkeypatch):
    """Verify data agreement metadata write and read use configured metadata route."""
    writes = []
    steward_rows = []

    def write_table(df, config, env, target, table, **kwargs):
        writes.append((table, df.rows, env, target, kwargs))
        if table == agreement.DATA_STEWARD_TABLE:
            steward_rows.extend(df.rows)

    def read_table(config, env, target, table, **kwargs):
        assert (env, target) == ("dev", "metadata")
        if table == agreement.DATA_STEWARD_TABLE:
            return steward_rows
        return []

    monkeypatch.setattr(agreement, "write_lakehouse_table", write_table)
    monkeypatch.setattr(agreement, "read_lakehouse_table", read_table)

    steward = agreement._create_or_update_data_steward(
        spark=FakeSpark(),
        config=framework_config(),
        env_name="dev",
        values={
            "steward_name": "Ops Steward",
            "steward_role": "Data Owner",
            "contact": "ops@example.com",
            "effective_from": "2026-01-01",
            "is_active": "true",
        },
        committed_by="reviewer@example.com",
        committed_at="2026-01-02T00:00:00+00:00",
    )

    read_back = agreement._list_data_stewards(framework_config(), "dev", spark_session=FakeSpark())

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
        if path.name == "metadata.py":
            continue
        text = path.read_text(encoding="utf-8")
        for helper in deleted_helpers:
            if helper in text:
                offenders.append(f"{path.name}:{helper}")

    assert offenders == []


def test_public_callable_list_includes_guardrail_authoring_helpers_after_metadata_cleanup():
    """Verify public callable list includes guardrail authoring helpers."""
    assert fabricops_kit.__all__ == [
        "setup_notebook",
        "setup_metadata_tables",
        "widget_render_data_steward",
        "widget_render_data_agreement",
        "widget_render_agreement_evidence",
    "widget_select_agreement",
    "get_selected_agreement",
        "read_lakehouse_table",
        "write_lakehouse_table",
        "read_lakehouse_csv",
        "read_lakehouse_parquet",
        "read_lakehouse_excel",
        "read_warehouse_table",
        "write_warehouse_table",
        "profile_dataframe",
        "validate_schema",
        "validate_schema_rule",
        "enforce_freshness",
        "enforce_freshness_rule",
        "enforce_profile_behavior",
        "stop_if_failed",
        "enforce_dq_rules",
        "display_guardrail_results",
        "prepare_pipeline_table_configs",
        "run_table_guardrails",
        "write_catalogue_evidence",
        "write_pipeline_lineage",
        "write_pipeline_run_summary",
        "widget_select_guardrail_target",
        "widget_enrich_table_metadata",
        "widget_author_schema_freshness_profile_rules",
        "widget_author_dq_rules",
        "widget_review_guardrail_governance",
    ]
