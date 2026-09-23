"""Unit tests for the Fabric workspace-role access scanner."""

from __future__ import annotations

import importlib


def test_scan_workspace_access_is_exposed_from_access_scanner_package():
    """Expose the workspace scanner from the access_scanner package."""
    from fabricops_kit.access_scanner import scan_workspace_access

    assert callable(scan_workspace_access)
    assert scan_workspace_access.__module__ == "fabricops_kit.access_scanner.scan_workspace_access"


def test_workspace_observations_normalize_roles_and_principals():
    """Preserve the workspace role while normalizing its data capability."""
    module = importlib.import_module("fabricops_kit.access_scanner.scan_workspace_access")
    assignments = [
        {
            "id": "assignment-1",
            "role": "Viewer",
            "principal": {
                "id": "user-id",
                "type": "User",
                "displayName": "Alice",
                "userDetails": {"userPrincipalName": "alice@example.com"},
            },
        },
        {
            "id": "assignment-2",
            "role": "Member",
            "principal": {
                "id": "group-id",
                "type": "Group",
                "displayName": "Data Consumers",
            },
        },
    ]

    rows = module._workspace_observations(workspace_id="workspace-id", assignments=assignments)

    assert rows == [
        {
            "workspace_id": "workspace-id",
            "role_assignment_id": "assignment-1",
            "principal_id": "user-id",
            "user_principal": "alice@example.com",
            "user_type": "USER",
            "role_name": "Viewer",
            "access_value": "READ",
            "access_state": "GRANT",
            "permission_source": "WORKSPACE_ROLE",
        },
        {
            "workspace_id": "workspace-id",
            "role_assignment_id": "assignment-2",
            "principal_id": "group-id",
            "user_principal": "Data Consumers",
            "user_type": "GROUP",
            "role_name": "Member",
            "access_value": "READWRITE",
            "access_state": "GRANT",
            "permission_source": "WORKSPACE_ROLE",
        },
    ]


def test_list_workspace_roles_uses_shared_fabric_pagination(monkeypatch):
    """Route workspace role listing through the shared Fabric REST helper."""
    module = importlib.import_module("fabricops_kit.access_scanner.scan_workspace_access")
    calls = []

    def fake_list(url, *, access_token):
        calls.append((url, access_token))
        return [{"id": "assignment-1", "role": "Member", "principal": {"id": "user-id", "type": "User"}}]

    monkeypatch.setattr(module, "list_fabric_pages", fake_list)

    result = module._list_workspace_role_assignments(
        workspace_id="workspace-id",
        access_token="token",
    )

    assert len(result) == 1
    assert calls == [
        (
            "https://api.fabric.microsoft.com/v1/workspaces/workspace-id/roleAssignments",
            "token",
        )
    ]


def test_workspace_roles_expand_across_registered_tables_in_same_workspace(spark_session):
    """Map each workspace role to every scanned registered table in that workspace."""
    module = importlib.import_module("fabricops_kit.access_scanner.scan_workspace_access")
    observations = module._observations_df(
        spark_session,
        [
            {
                "workspace_id": "workspace-a",
                "role_assignment_id": "assignment-1",
                "principal_id": "user-id",
                "user_principal": "alice@example.com",
                "user_type": "USER",
                "role_name": "Viewer",
                "access_value": "READ",
                "access_state": "GRANT",
                "permission_source": "WORKSPACE_ROLE",
            }
        ],
    )
    registered = spark_session.createDataFrame(
        [
            ("table-1", "Silver", "sales", "orders"),
            ("table-2", "Gold", "sales", "customers"),
            ("table-3", "Other", "sales", "hidden"),
        ],
        ["_catalogue_table_id", "_catalogue_target", "_catalogue_schema_name", "_catalogue_table_name"],
    )
    targets = spark_session.createDataFrame(
        [
            ("Silver", "workspace-a"),
            ("Gold", "workspace-a"),
            ("Other", "workspace-b"),
        ],
        ["_catalogue_target", "_target_workspace_id"],
    )

    mapped = module._map_to_catalogue(observations, registered, targets)
    table_ids = {
        row["_catalogue_table_id"]
        for row in mapped.collect()
        if row["_catalogue_table_id"] is not None
    }

    assert table_ids == {"table-1", "table-2"}


def test_shared_access_persistence_always_appends_to_metadata(monkeypatch):
    """Persist every scanner result through the same append-only metadata route."""
    shared = importlib.import_module("fabricops_kit.access_scanner.shared")
    writes = []

    monkeypatch.setattr(shared, "metadata_table_physical_schema", lambda config, table: "engineering")
    monkeypatch.setattr(
        shared,
        "write_lakehouse_table",
        lambda df, table, **kwargs: writes.append((df, table, kwargs)),
    )

    frame = object()
    shared.persist_access_rows(
        frame,
        config={"config": "value"},
        environment_name="dev",
        context={"env": "dev"},
        persist=True,
    )

    assert len(writes) == 1
    assert writes[0][0] is frame
    assert writes[0][1] == "METADATA_DATA_ACCESS"
    assert writes[0][2]["store"] == "Metadata"
    assert writes[0][2]["schema"] == "engineering"
    assert writes[0][2]["mode"] == "append"


def test_shared_access_persistence_can_be_disabled(monkeypatch):
    """Allow notebook authors to inspect a scan without writing metadata."""
    shared = importlib.import_module("fabricops_kit.access_scanner.shared")
    monkeypatch.setattr(
        shared,
        "write_lakehouse_table",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("write should not run")),
    )

    shared.persist_access_rows(
        object(),
        config={},
        environment_name="dev",
        context={},
        persist=False,
    )
