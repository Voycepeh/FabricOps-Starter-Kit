from __future__ import annotations

from pathlib import Path

import pytest

import fabricops_kit
import fabricops_kit.data_agreement as agreement
import fabricops_kit.metadata as metadata
from tests.helpers import FakeSpark, framework_config

pytestmark = pytest.mark.unit


def test_runtime_audit_fields_resolve_fabric_context_and_allow_overrides(fake_notebookutils):
    audit = metadata._build_runtime_audit_fields(
        config=framework_config(),
        env="dev",
        runtime_context={"activityId": "manual-activity"},
    )

    assert audit["_workspace_name"] == "FabricOps Test Workspace"
    assert audit["_committed_by"] == "fabricops.test@example.com"
    assert audit["_metadata_lakehouse_name"] == "lh_metadata_dev"
    assert audit["_activity_id"] == "manual-activity"


def test_notebook_registry_setup_and_registration_use_metadata_route(monkeypatch):
    reads = []
    writes = []

    def read_table(config, env, target, table, **kwargs):
        reads.append((env, target, table))
        if len(reads) == 1:
            raise RuntimeError("missing")
        return [dict.fromkeys(metadata.NOTEBOOK_REGISTRY_FIELDS, "")]

    monkeypatch.setattr(metadata, "read_lakehouse_table", read_table)
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

    spark = FakeSpark()
    setup = metadata._setup_notebook_registry_table(spark=spark, config=framework_config(), env="dev")
    row = metadata._register_current_notebook(
        spark=spark,
        config=framework_config(),
        env="dev",
        agreement_id="DA-1",
        notebook_type="02_pipeline",
        environment_name="dev",
        dataset_name="orders",
        table_name="fact_orders",
    )

    assert setup["created"] is True
    assert list(row) == metadata.NOTEBOOK_REGISTRY_FIELDS
    assert row["notebook_url"] == "https://app.fabric.microsoft.com/groups/workspace-id/notebooks/notebook-id"
    assert [(env, target, table) for _, env, target, table, _ in writes] == [
        ("dev", "metadata", metadata.NOTEBOOK_REGISTRY_TABLE),
        ("dev", "metadata", metadata.NOTEBOOK_REGISTRY_TABLE),
    ]


def test_current_notebook_active_registrations_filters_current_runtime_rows(monkeypatch):
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


def test_metadata_key_builders_are_stable_for_governance_and_dq_rules():
    table_key = metadata._build_metadata_table_key(" DEV ", "Sales", "Orders")
    column_key = metadata._build_metadata_column_key("dev", "sales", "orders", "Order_ID")
    dq_key = metadata._build_dq_rule_key("dev", "sales", "orders", "order_id_required")

    assert table_key == metadata._build_metadata_table_key("dev", "sales", "orders")
    assert column_key == metadata._build_metadata_column_key("DEV", "SALES", "ORDERS", " order_id ")
    assert dq_key == metadata._build_dq_rule_key("DEV", "SALES", "ORDERS", " order_id_required ")
    assert len({table_key, column_key, dq_key}) == 3
    assert all(len(value) == 64 for value in (table_key, column_key, dq_key))


def test_data_agreement_metadata_write_and_read_use_configured_metadata_route(monkeypatch):
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
    deleted_helpers = (
        "_get_notebook_registry_schema",
        "_notebook_registry_base_schema",
        "_default_evidence_types",
        "_build_evidence_row",
        "_extract_columns_from_profile",
        "_normalise_records_by_column",
        "_write_metadata_rows",
        "_write_metadata_rows_legacy",
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


def test_public_v1_callable_list_unchanged_after_metadata_cleanup():
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
        "monitor_data_changes",
        "stop_if_failed",
        "build_lineage_records",
        "widget_select_catalogue_table",
        "get_selected_catalogue_table",
        "load_catalogue_profile_rows",
        "widget_review_column_context",
        "widget_review_dq_rules",
        "widget_review_column_classification",
        "record_table_governance",
    ]
