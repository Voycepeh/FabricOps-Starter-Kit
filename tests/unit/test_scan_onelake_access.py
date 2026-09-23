"""Unit tests for the OneLake Security access scanner."""

from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest


def test_scan_onelake_access_is_exposed_from_access_scanner_package():
    """Expose the implemented OneLake scanner from the access_scanner package."""
    from fabricops_kit.access_scanner import scan_onelake_access

    assert callable(scan_onelake_access)
    assert scan_onelake_access.__module__ == "fabricops_kit.access_scanner.scan_onelake_access"


def test_role_observations_preserve_entra_and_default_reader_membership():
    """Keep explicit principals separate from automatic item-access selectors."""
    module = importlib.import_module("fabricops_kit.access_scanner.scan_onelake_access")
    roles = [
        {
            "id": "role-1",
            "name": "FabricOpsEngineer",
            "kind": "Policy",
            "eTag": "etag",
            "decisionRules": [
                {
                    "effect": "Permit",
                    "permission": [
                        {"attributeName": "Path", "attributeValueIncludedIn": ["Tables/sales/orders"]},
                        {"attributeName": "Action", "attributeValueIncludedIn": ["Read", "ReadWrite"]},
                    ],
                    "constraints": {"rows": [{"tablePath": "/Tables/sales/orders", "value": "region = 'SG'"}]},
                }
            ],
            "members": {
                "microsoftEntraMembers": [
                    {"objectId": "user-object-id", "objectType": "User", "tenantId": "tenant-id"}
                ],
                "fabricItemMembers": [
                    {"itemAccess": ["ReadAll"], "sourcePath": "workspace-id/item-id"}
                ],
            },
        }
    ]

    rows = module._role_observations(
        target="Silver",
        workspace_id="workspace-id",
        item_id="item-id",
        roles=roles,
    )

    assert len(rows) == 4
    assert {row["user_principal"] for row in rows} == {
        "user-object-id",
        "fabric-item:workspace-id/item-id:ReadAll",
    }
    assert {row["access_value"] for row in rows} == {"Read", "ReadWrite"}
    assert {row["permission_source"] for row in rows} == {
        "ONELAKE_ROLE",
        "ONELAKE_ITEM_ACCESS_SELECTOR",
    }
    assert all('"rows"' in row["constraints_json"] for row in rows)


def test_list_data_access_roles_uses_shared_fabric_pagination(monkeypatch):
    """Route OneLake role listing through the shared Fabric REST helper."""
    module = importlib.import_module("fabricops_kit.access_scanner.scan_onelake_access")
    calls = []

    def fake_list(url, *, access_token):
        calls.append((url, access_token))
        return [{"name": "A"}, {"name": "B"}]

    monkeypatch.setattr(module, "list_fabric_pages", fake_list)

    roles = module._list_data_access_roles(
        workspace_id="workspace-id",
        item_id="item-id",
        access_token="token",
    )

    assert [role["name"] for role in roles] == ["A", "B"]
    assert calls == [
        (
            "https://api.fabric.microsoft.com/v1/workspaces/workspace-id/items/item-id/dataAccessRoles",
            "token",
        )
    ]


def test_map_to_catalogue_supports_table_schema_and_all_data_paths(spark_session):
    """Map exact table paths, schema wildcards, and all-data roles to tables."""
    module = importlib.import_module("fabricops_kit.access_scanner.scan_onelake_access")
    observations = module._observations_df(
        spark_session,
        [
            {
                "_target": "Silver",
                "workspace_id": "workspace-id",
                "item_id": "item-id",
                "role_name": "Exact",
                "user_principal": "user-1",
                "user_type": "USER",
                "permission_source": "ONELAKE_ROLE",
                "access_state": "Permit",
                "access_value": "ReadWrite",
                "path": "Tables/sales/orders",
            },
            {
                "_target": "Silver",
                "workspace_id": "workspace-id",
                "item_id": "item-id",
                "role_name": "Schema",
                "user_principal": "user-2",
                "user_type": "USER",
                "permission_source": "ONELAKE_ROLE",
                "access_state": "Permit",
                "access_value": "Read",
                "path": "Tables/sales/*",
            },
            {
                "_target": "Silver",
                "workspace_id": "workspace-id",
                "item_id": "item-id",
                "role_name": "All",
                "user_principal": "user-3",
                "user_type": "USER",
                "permission_source": "ONELAKE_ROLE",
                "access_state": "Permit",
                "access_value": "Read",
                "path": "*",
            },
            {
                "_target": "Silver",
                "workspace_id": "workspace-id",
                "item_id": "item-id",
                "role_name": "Files",
                "user_principal": "user-4",
                "user_type": "USER",
                "permission_source": "ONELAKE_ROLE",
                "access_state": "Permit",
                "access_value": "Read",
                "path": "Files/raw/*",
            },
        ],
    )
    catalogue = spark_session.createDataFrame(
        [
            ("table-orders", "Silver", "sales", "orders"),
            ("table-customers", "Silver", "sales", "customers"),
        ],
        ["_catalogue_table_id", "_catalogue_target", "_catalogue_schema_name", "_catalogue_table_name"],
    )

    mapped = module._map_to_catalogue(observations, catalogue)
    counts = {
        row["role_name"]: row["count"]
        for row in mapped.groupBy("role_name").count().collect()
    }

    assert counts == {"Exact": 1, "Schema": 2, "All": 2, "Files": 1}
    files = mapped.filter("role_name = 'Files'").collect()[0]
    assert files["_catalogue_table_id"] is None


def test_scan_onelake_access_rejects_warehouse_target_before_auth(monkeypatch):
    """Reject unsupported stores without requesting a token or calling Fabric REST."""
    module = importlib.import_module("fabricops_kit.access_scanner.scan_onelake_access")
    monkeypatch.setattr(
        module,
        "resolve_fabric_context",
        lambda **kwargs: (object(), "dev", {"config": object(), "env": "dev"}),
    )
    monkeypatch.setattr(module, "target_store_kinds", lambda *args: {"Gold": "warehouse"})
    monkeypatch.setattr(
        module,
        "fabric_access_token",
        lambda *args, **kwargs: pytest.fail("token should not be requested"),
    )

    with pytest.raises(ValueError, match="Lakehouse targets only"):
        module.scan_onelake_access(SimpleNamespace(), targets="Gold")


def test_request_json_rejects_unexpected_host_before_sending_token(monkeypatch):
    """Never forward a Fabric bearer token to an arbitrary continuation host."""
    shared = importlib.import_module("fabricops_kit.access_scanner.shared")
    monkeypatch.setattr(shared, "urlopen", lambda *args, **kwargs: pytest.fail("network must not be called"))

    with pytest.raises(RuntimeError, match="unexpected host"):
        shared.request_fabric_json("https://example.com/steal-token", access_token="secret")
