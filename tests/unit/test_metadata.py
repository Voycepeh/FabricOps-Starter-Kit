from __future__ import annotations

import pytest

import fabricops_kit.metadata as metadata
from tests.helpers import FakeSpark, framework_config

pytestmark = pytest.mark.unit


def test_runtime_audit_fields_resolve_fabric_context_and_allow_overrides(fake_notebookutils):
    audit = metadata.build_runtime_audit_fields(
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
        return [dict.fromkeys(metadata.get_notebook_registry_schema(), "")]

    monkeypatch.setattr(metadata, "read_lakehouse_table", read_table)
    monkeypatch.setattr(metadata, "write_lakehouse_table", lambda df, config, env, target, table, **kwargs: writes.append((df, env, target, table, kwargs)))
    monkeypatch.setattr(
        metadata,
        "_runtime_context",
        lambda: {
            "currentWorkspaceId": "workspace-id",
            "currentWorkspaceName": "Workspace Name",
            "currentNotebookId": "notebook-id",
            "currentNotebookName": "03_pc_orders_pipeline",
            "userName": "user@example.com",
            "userId": "user-id",
        },
    )

    spark = FakeSpark()
    setup = metadata.setup_notebook_registry_table(spark=spark, config=framework_config(), env="dev")
    row = metadata.register_current_notebook(
        spark=spark,
        config=framework_config(),
        env="dev",
        agreement_id="DA-1",
        notebook_type="03_pc",
        environment_name="dev",
        dataset_name="orders",
        table_name="fact_orders",
    )

    assert setup["created"] is True
    assert list(row) == metadata.get_notebook_registry_schema()
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
            "notebook_name": "03_pc_orders",
            "registration_status": "active",
            "notebook_type": "03_pc",
            "environment_name": "dev",
            "registration_role": "primary",
        },
        {
            "agreement_id": "DA-2",
            "registration_id": "r2",
            "registered_at": "2026-01-01T00:00:00Z",
            "notebook_id": "notebook-id",
            "notebook_name": "03_pc_orders",
            "registration_status": "superseded",
            "notebook_type": "03_pc",
            "environment_name": "dev",
            "registration_role": "primary",
        },
        {
            "agreement_id": "DA-3",
            "registration_id": "r3",
            "registered_at": "2026-01-03T00:00:00Z",
            "notebook_id": "other",
            "notebook_name": "03_pc_other",
            "registration_status": "active",
            "notebook_type": "03_pc",
            "environment_name": "dev",
            "registration_role": "primary",
        },
    ]
    monkeypatch.setattr(metadata, "_runtime_context", lambda: {"currentNotebookId": "notebook-id"})
    monkeypatch.setattr(metadata, "read_lakehouse_table", lambda *args, **kwargs: rows)

    active = metadata.current_notebook_active_registrations(
        object(), config=framework_config(), env="dev", notebook_type="03_pc", environment_name="dev", registration_role="primary"
    )

    assert len(active) == 1
    assert active[0]["notebook_id"] == "notebook-id"
