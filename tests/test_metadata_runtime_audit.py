import pytest

pytestmark = pytest.mark.fabric
from types import SimpleNamespace

import fabricops_kit.metadata as metadata
from fabricops_kit.fabric_input_output import FabricStore


def _config():
    store = FabricStore(env="dev", workspace_id="workspace", item_id="metadata-item", name="metadata", kind="lakehouse")
    return SimpleNamespace(path_config=SimpleNamespace(paths={"dev": {"metadata": store}}))


def test_build_runtime_audit_fields_prefers_user_name_and_resolves_fabric_context(monkeypatch):
    monkeypatch.setattr(metadata, "_runtime_context", lambda: {
        "userName": "fabric.user@example.com",
        "userId": "fabric-user-id",
        "currentWorkspaceName": "Current Workspace",
        "workspaceName": "Fallback Workspace",
        "currentNotebookName": "01_da_orders",
        "notebookName": "fallback_notebook",
        "activityId": "activity-123",
    })

    fields = metadata.build_runtime_audit_fields(committed_at="2026-01-01T00:00:00+00:00")

    assert fields == {
        "_committed_by": "fabric.user@example.com",
        "_committed_at": "2026-01-01T00:00:00+00:00",
        "_workspace_name": "Current Workspace",
        "_notebook_name": "01_da_orders",
        "_metadata_lakehouse_name": "",
        "_activity_id": "activity-123",
    }


def test_build_runtime_audit_fields_falls_back_to_user_id_and_merges_override(monkeypatch):
    monkeypatch.setattr(metadata, "_runtime_context", lambda: {
        "userName": "",
        "userId": "fabric-user-id",
        "workspaceName": "Fallback Workspace",
        "notebookName": "fallback_notebook",
    })

    fields = metadata.build_runtime_audit_fields(runtime_context={"activityId": "override-activity"}, committed_at="timestamp")

    assert fields["_committed_by"] == "fabric-user-id"
    assert fields["_workspace_name"] == "Fallback Workspace"
    assert fields["_notebook_name"] == "fallback_notebook"
    assert fields["_activity_id"] == "override-activity"


def test_build_runtime_audit_fields_defaults_blank_user_to_unknown(monkeypatch):
    monkeypatch.setattr(metadata, "_runtime_context", lambda: {"userName": "", "userId": ""})

    fields = metadata.build_runtime_audit_fields(committed_at="timestamp")

    assert fields["_committed_by"] == "unknown"


def test_build_runtime_audit_fields_resolves_metadata_lakehouse_and_explicit_overrides(monkeypatch):
    monkeypatch.setattr(metadata, "_runtime_context", lambda: {"userName": "runtime-user"})

    fields = metadata.build_runtime_audit_fields(
        config=_config(),
        env="dev",
        committed_by="override-user",
        committed_at="override-timestamp",
    )

    assert fields["_committed_by"] == "override-user"
    assert fields["_committed_at"] == "override-timestamp"
    assert fields["_metadata_lakehouse_name"] == "metadata"


def test_build_runtime_audit_fields_supports_custom_output_names(monkeypatch):
    monkeypatch.setattr(metadata, "_runtime_context", lambda: {})

    fields = metadata.build_runtime_audit_fields(
        timestamp_field="created_at",
        user_field="created_by",
        workspace_field="workspace",
        notebook_field="notebook",
        metadata_lakehouse_field="metadata_lakehouse",
        activity_field="activity",
        committed_by="user",
        committed_at="timestamp",
    )

    assert fields == {
        "created_by": "user",
        "created_at": "timestamp",
        "workspace": "",
        "notebook": "",
        "metadata_lakehouse": "",
        "activity": "",
    }
