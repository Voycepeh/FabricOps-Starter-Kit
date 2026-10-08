"""Unit tests for person-level effective Fabric access resolution."""

from __future__ import annotations

import importlib

import pytest


def _module():
    return importlib.import_module("fabricops_kit.access_scanner.scan_effective_access")


def _table(item_id="item-a", table_name="orders", item_type="LAKEHOUSE"):
    return {
        "table_id": f"workspace-a/{item_id}/sales/{table_name}",
        "workspace_id": "workspace-a",
        "workspace_name": "Analytics",
        "item_id": item_id,
        "item_name": "Curated",
        "item_type": item_type,
        "schema_name": "sales",
        "table_name": table_name,
        "table_path": f"Tables/sales/{table_name}",
        "object_type": "TABLE",
    }


def _identities():
    return {
        "user-a": {"object_id": "user-a", "display_name": "Alice", "user_principal_name": "alice@example.com", "principal_type": "USER", "group_type": ""},
        "user-b": {"object_id": "user-b", "display_name": "Bob", "user_principal_name": "bob@example.com", "principal_type": "USER", "group_type": ""},
        "group-a": {"object_id": "group-a", "display_name": "Readers", "user_principal_name": "", "principal_type": "GROUP", "group_type": "SECURITY_GROUP"},
        "group-b": {"object_id": "group-b", "display_name": "Nested readers", "user_principal_name": "", "principal_type": "GROUP", "group_type": "SECURITY_GROUP"},
        "group-dl": {"object_id": "group-dl", "display_name": "Announcements", "user_principal_name": "", "principal_type": "GROUP", "group_type": "DISTRIBUTION_LIST"},
    }


def _memberships():
    return {"group-a": ["user-a", "group-b"], "group-b": ["user-b", "group-a"]}


def _item_access(
    principal_id="user-a",
    *,
    permissions=("READ",),
    source="DIRECT_ITEM_SHARE",
    role_name="",
    principal_type="User",
    item_id="item-a",
):
    return {
        "workspace_id": "workspace-a",
        "item_id": item_id,
        "item_type": "LAKEHOUSE",
        "principal_object_id": principal_id,
        "principal_type": principal_type,
        "principal_name": principal_id,
        "item_access_permissions": list(permissions),
        "item_access_source": source,
        "role_name": role_name,
        "access_verification_status": "CONFIRMED",
    }


def _grant(
    *,
    principal_id="user-a",
    principal_type="User",
    surface="SQL",
    state="GRANT",
    value="SELECT",
    restriction="{}",
    item_id="item-a",
):
    module = _module()
    return module._grant(
        _table(item_id=item_id),
        principal_id=principal_id,
        principal_type=principal_type,
        principal_name=principal_id,
        access_surface=surface,
        access_value=value,
        access_state=state,
        permission_source="DIRECT_PERMISSION" if surface == "SQL" else "ONELAKE_ROLE",
        restrictions_json=restriction,
    )


def _resolve(
    grants,
    *,
    item_access=(),
    mode="DELEGATED_IDENTITY",
    complete=True,
    identities=None,
    memberships=None,
):
    module = _module()
    coverage = []
    resolved = module._resolve_grants(
        list(grants),
        item_access=list(item_access),
        sql_modes={"item-a": mode},
        item_visibility_complete=complete,
        identities=identities or _identities(),
        memberships=_memberships() if memberships is None else memberships,
        coverage=coverage,
    )
    return module._consolidate(resolved, coverage), coverage


def _default_reader_role(*, item_access=("ReadAll",), constraints=None):
    return {
        "name": "DefaultReader",
        "members": {"fabricItemMembers": [{"sourcePath": "workspace-a/item-a", "itemAccess": list(item_access)}]},
        "decisionRules": [
            {
                "effect": "Permit",
                "permission": [
                    {"attributeName": "Path", "attributeValueIncludedIn": ["Tables/*"]},
                    {"attributeName": "Action", "attributeValueIncludedIn": ["Read"]},
                ],
                "constraints": constraints or {},
            }
        ],
    }


def test_scan_effective_access_is_exposed_from_package_root():
    """Expose the one-call resolver from notebook-friendly import paths."""
    from fabricops_kit import scan_effective_access
    from fabricops_kit.access_scanner import scan_effective_access as package_scan

    assert scan_effective_access is package_scan
    assert scan_effective_access.__module__ == "fabricops_kit.access_scanner.scan_effective_access"


def test_workspace_viewer_uses_normal_default_reader_inheritance():
    """Confirm Viewer table access only when the DefaultReader baseline is intact."""
    module = _module()
    coverage = []
    status = module._default_reader_status(
        workspace_id="workspace-a", item_id="item-a", item_name="Curated",
        roles=[_default_reader_role()], coverage=coverage,
    )
    observations = [{"workspace_id": "workspace-a", "principal_id": "user-a", "user_type": "User", "user_principal": "Alice", "role_name": "Viewer"}]
    grants = module._workspace_grants(
        [_table()], observations, default_reader_status={"item-a": status},
        sql_modes={"item-a": "USER_IDENTITY"},
    )
    rows, _ = _resolve(
        grants, item_access=module._workspace_item_access([_table()], observations),
        mode="USER_IDENTITY",
    )
    assert rows[0]["access_verification_status"] == "CONFIRMED"
    assert rows[0]["effective_permissions"] == ["READ"]
    assert rows[0]["data_access_source"] == "ONELAKE_DEFAULT_READER"
    assert rows[0]["access_channels"] == ["ONELAKE", "SQL"]
    assert coverage == []


@pytest.mark.parametrize("role", ["Admin", "Member", "Contributor"])
def test_elevated_workspace_roles_retain_confirmed_access(role):
    """Keep elevated Workspace-derived item and data access confirmed."""
    module = _module()
    observations = [{"workspace_id": "workspace-a", "principal_id": "user-a", "user_type": "User", "user_principal": "Alice", "role_name": role}]
    grants = module._workspace_grants([_table()], observations)
    rows, _ = _resolve(grants, item_access=module._workspace_item_access([_table()], observations))
    assert rows[0]["access_verification_status"] == "CONFIRMED"
    assert rows[0]["effective_permissions"] == ["READ", "WRITE"]
    assert rows[0]["item_access_permissions"] == ["READ", "READALL", "READDATA", "WRITE"]
    assert rows[0]["channel_permissions_json"] == '{"ONELAKE":["READ","WRITE"],"SQL":["READ"]}'


def test_workspace_viewer_with_applicable_sql_permission_is_confirmed():
    """Combine Viewer item access with SQL data permission in delegated mode."""
    rows, _ = _resolve([_grant()], item_access=[_item_access(source="WORKSPACE_ROLE")])
    assert rows[0]["access_verification_status"] == "CONFIRMED"
    assert rows[0]["effective_permissions"] == ["READ"]


def test_direct_item_read_without_data_permission_is_not_effective():
    """Do not turn item Read alone into table-level access."""
    rows, coverage = _resolve([], item_access=[_item_access()])
    assert rows == []
    assert "ITEM_ACCESS_WITHOUT_DATA_PERMISSION" in {row["reason_code"] for row in coverage}


def test_direct_item_read_with_sql_select_is_confirmed():
    """Confirm SQL access when both item Read and SELECT are established."""
    rows, _ = _resolve([_grant()], item_access=[_item_access()])
    assert rows[0]["access_verification_status"] == "CONFIRMED"
    assert rows[0]["item_access_source"] == "DIRECT_ITEM_SHARE"


def test_item_readdata_supplies_broad_sql_data_permission():
    """Recognize Read plus ReadData as inherited SQL table access."""
    module = _module()
    access = _item_access(permissions=("READ", "READDATA"))
    grants = module._item_permission_grants(
        [_table()], [access], {"item-a": "DELEGATED_IDENTITY"}
    )
    rows, _ = _resolve(grants, item_access=[access])
    assert rows[0]["access_verification_status"] == "CONFIRMED"
    assert rows[0]["data_access_source"] == "ITEM_READDATA"


def test_sql_select_with_unverified_item_access_is_not_confirmed():
    """Preserve a visible SQL grant as unverified when item access is not enumerable."""
    rows, coverage = _resolve([_grant()], complete=False)
    assert rows[0]["access_verification_status"] == "UNVERIFIED"
    assert rows[0]["effective_permissions"] == []
    assert rows[0]["observed_permissions"] == ["READ"]
    assert "ITEM_ACCESS_UNVERIFIED" in {row["reason_code"] for row in coverage}


def test_sql_select_with_known_missing_item_access_is_not_effective():
    """Reject a SQL grant when complete evidence proves item Read is absent."""
    rows, coverage = _resolve([_grant()], complete=True)
    assert rows[0]["access_verification_status"] == "NOT_EFFECTIVE"
    assert rows[0]["effective_permissions"] == []
    assert "DATA_PERMISSION_NOT_EFFECTIVE" in {row["reason_code"] for row in coverage}


def test_direct_item_sharing_through_security_group_resolves_people():
    """Apply group-carried item access to group-carried SQL permission."""
    rows, _ = _resolve(
        [_grant(principal_id="group-a", principal_type="Group")],
        item_access=[_item_access("group-a", principal_type="Group")],
    )
    assert {row["person_object_id"] for row in rows} == {"user-a", "user-b"}
    assert {row["access_verification_status"] for row in rows} == {"CONFIRMED"}


def test_multiple_grants_remain_separate_in_provenance():
    """Consolidate the outcome without collapsing contributing grant paths."""
    rows, _ = _resolve(
        [_grant(), _grant(principal_id="group-a", principal_type="Group")],
        item_access=[_item_access(), _item_access("group-a", principal_type="Group")],
    )
    alice = next(row for row in rows if row["person_object_id"] == "user-a")
    assert alice["contributing_grant_count"] >= 2
    assert "group-a -> user-a" in alice["inheritance_paths"]


def test_nested_group_inheritance_preserves_each_path():
    """Preserve nested group paths while stopping cycles."""
    rows, coverage = _resolve(
        [_grant(principal_id="group-a", principal_type="Group")],
        item_access=[_item_access("group-a", principal_type="Group")],
    )
    bob = next(row for row in rows if row["person_object_id"] == "user-b")
    assert "group-a -> group-b -> user-b" in bob["inheritance_paths"]
    assert "group-a -> group-b -> user-b" in bob["item_inheritance_paths"]
    assert "GROUP_MEMBERSHIP_CYCLE" in {row["reason_code"] for row in coverage}


def test_distribution_lists_and_unresolved_principals_are_not_people():
    """Do not expand distribution lists or invent unresolved identities."""
    grants = [
        _grant(principal_id="group-dl", principal_type="Group"),
        _grant(principal_id="missing-user"),
    ]
    rows, coverage = _resolve(
        grants,
        item_access=[_item_access("group-dl", principal_type="Group")],
    )
    assert rows == []
    assert {row["reason_code"] for row in coverage}.issuperset(
        {"GROUP_TYPE_NOT_EXPANDED", "UNRESOLVED_IDENTITY"}
    )


def test_onelake_explicit_role_requires_item_read():
    """Confirm explicit OneLake membership only with applicable item access."""
    rows, _ = _resolve(
        [_grant(surface="ONELAKE", state="Permit", value="Read")],
        item_access=[_item_access()],
    )
    assert rows[0]["access_verification_status"] == "CONFIRMED"
    assert rows[0]["access_surface"] == "ONELAKE"


def test_onelake_virtual_membership_honors_source_and_permission_combination():
    """Do not equate Read with a selector requiring both Read and ReadAll."""
    selector = _grant(
        principal_id="fabric-item:workspace-a/item-a:Read+ReadAll",
        principal_type="FABRIC_ITEM_MEMBERS", surface="ONELAKE", state="Permit", value="Read",
    )
    rows, coverage = _resolve([selector], item_access=[_item_access(permissions=("READ",))])
    assert rows == []
    assert "ITEM_PERMISSION_SELECTOR_UNRESOLVED" in {row["reason_code"] for row in coverage}
    rows, _ = _resolve([selector], item_access=[_item_access(permissions=("READ", "READALL"))])
    assert rows[0]["access_verification_status"] == "CONFIRMED"


def test_sql_delegated_identity_mode_uses_sql_permissions():
    """Use SQL grants for table access in delegated identity mode."""
    rows, _ = _resolve([_grant()], item_access=[_item_access()], mode="DELEGATED_IDENTITY")
    assert rows[0]["sql_access_mode"] == "DELEGATED_IDENTITY"
    assert rows[0]["effective_permissions"] == ["READ"]


def test_sql_user_identity_mode_uses_onelake_not_sql_table_grants():
    """Keep SQL table grants non-effective when OneLake governs the endpoint."""
    sql_rows, _ = _resolve([_grant()], item_access=[_item_access()], mode="USER_IDENTITY")
    assert sql_rows[0]["access_verification_status"] == "NOT_EFFECTIVE"
    assert sql_rows[0]["effective_permissions"] == []
    onelake_rows, _ = _resolve(
        [_grant(surface="ONELAKE", state="Permit", value="Read")],
        item_access=[_item_access()], mode="USER_IDENTITY",
    )
    assert onelake_rows[0]["access_verification_status"] == "CONFIRMED"
    assert onelake_rows[0]["access_channels"] == ["ONELAKE", "SQL"]


def test_unavailable_sql_access_mode_remains_unverified():
    """Do not guess delegated mode when supported metadata is inconclusive."""
    rows, coverage = _resolve([_grant()], item_access=[_item_access()], mode="UNVERIFIED")
    assert rows[0]["access_verification_status"] == "UNVERIFIED"
    assert rows[0]["effective_permissions"] == []
    assert "ITEM_ACCESS_UNVERIFIED" in {row["reason_code"] for row in coverage}


def test_sql_access_mode_detection_uses_only_supported_evidence():
    """OLS role names and SQL rows are not authoritative Lakehouse mode evidence."""
    module = _module()
    assert module._sql_access_mode({"type": "Warehouse"}, []) == "DELEGATED_IDENTITY"
    for observed in (
        {"sql_access_mode": "USER_IDENTITY"},
        {"sql_access_mode": "DELEGATED_IDENTITY"},
        {"role_name": "OLS_Reader"},
        {"sql_access_mode": "UNVERIFIED"},
    ):
        assert module._sql_access_mode({"type": "Lakehouse"}, [observed]) == "UNVERIFIED"


def test_sql_deny_overrides_the_corresponding_sql_grant():
    """Apply a table-level SQL DENY to the corresponding grant."""
    rows, coverage = _resolve([_grant(), _grant(state="DENY")], item_access=[_item_access()])
    assert rows[0]["access_verification_status"] == "NOT_EFFECTIVE"
    assert rows[0]["effective_permissions"] == []
    assert "PERMISSION_DENY_APPLIED" in {row["reason_code"] for row in coverage}


def test_onelake_and_sql_column_restrictions_remain_auditable():
    """Retain row and column restrictions without presenting unrestricted access."""
    grants = [
        _grant(surface="ONELAKE", state="Permit", value="Read", restriction='{"rows":["region = SG"],"columns":["amount"]}'),
        _grant(restriction='{"column":"amount"}'),
    ]
    rows, _ = _resolve(grants, item_access=[_item_access()])
    assert {row["access_surface"] for row in rows} == {"ONELAKE", "SQL"}
    assert all(row["is_restricted"] for row in rows)
    assert all("restrictions" in row["contributing_grants_json"] for row in rows)


def test_default_reader_contradiction_is_reported_and_not_confirmed():
    """Downgrade Viewer access when observed DefaultReader differs from baseline."""
    module = _module()
    coverage = []
    status = module._default_reader_status(
        workspace_id="workspace-a", item_id="item-a", item_name="Curated",
        roles=[_default_reader_role(item_access=("Read",))], coverage=coverage,
    )
    assert status == "NOT_EFFECTIVE"
    assert "DEFAULT_READER_BASELINE_CONTRADICTION" in {row["reason_code"] for row in coverage}


def test_discovery_uses_caller_visible_fabric_and_sql_evidence(monkeypatch):
    """Mock supported APIs while preserving direct-item visibility limitations."""
    module = _module()

    class Row:
        def __init__(self, **values):
            self.values = values

        def asDict(self, recursive=True):
            return dict(self.values)

    class Frame:
        def __init__(self, rows):
            self.rows = rows

        def toLocalIterator(self):
            return iter(self.rows)

    def pages(url, **kwargs):
        if url.endswith("/workspaces"):
            return [{"id": "workspace-a", "displayName": "Analytics"}]
        if url.endswith("/roleAssignments"):
            return [{"principal": {"id": "user-a", "type": "User"}, "role": "Viewer"}]
        if url.endswith("/items"):
            return [{"id": "item-a", "displayName": "Curated", "type": "Lakehouse"}]
        if url.endswith("/tables"):
            return [{"name": "orders", "location": "/Tables/sales/orders", "type": "Managed"}]
        if url.endswith("/dataAccessRoles"):
            return [_default_reader_role()]
        raise AssertionError(url)

    def sql_query(spark, **kwargs):
        query = kwargs["query"]
        if query == module.SQL_ACCESS_QUERY:
            return Frame(
                [
                    Row(
                        principal_id="user-a", user_name="Alice", user_type="User",
                        role_name="", permission_source="Direct Permission",
                        state_desc="GRANT", permission_name="SELECT",
                        class_desc="OBJECT_OR_COLUMN", schema_name="sales",
                        object_name="orders", column_name="",
                    )
                ]
            )
        raise AssertionError(query)

    monkeypatch.setattr(module, "fabric_access_token", lambda: "token")
    monkeypatch.setattr(module, "list_fabric_pages", pages)
    monkeypatch.setattr(
        module,
        "search_fabric_catalog",
        lambda **kwargs: [
            {
                "id": "item-a",
                "displayName": "Curated",
                "type": "Lakehouse",
                "hierarchy": {
                    "workspace": {"id": "workspace-a", "displayName": "Analytics"}
                },
            }
        ],
    )
    monkeypatch.setattr(module, "read_discovered_sql_endpoint_query", sql_query)

    grants, item_access, modes, complete, coverage = module._discover_access_evidence(object())
    assert modes == {"item-a": "UNVERIFIED"}
    assert "SQL_ACCESS_MODE_UNVERIFIED" in {row["reason_code"] for row in coverage}
    assert complete is False
    assert item_access[0]["item_access_permissions"] == ["READ", "READALL"]
    assert {grant["access_surface"] for grant in grants} == {"WORKSPACE", "ONELAKE", "SQL"}
    assert "ITEM_PERMISSION_ENUMERATION_UNAVAILABLE" in {
        row["reason_code"] for row in coverage
    }


def _identity_map(spark):
    return spark.createDataFrame(
        [("user-a", "Alice", "alice@example.com", "User", "")],
        ["object_id", "display_name", "user_principal_name", "principal_type", "group_type"],
    )


def _membership_map(spark):
    return spark.createDataFrame(
        [("unused-group", "user-a")], ["group_object_id", "member_object_id"]
    )


def test_public_result_exposes_verification_and_partial_visibility(monkeypatch, spark_session):
    """Keep incomplete API visibility explicit in both public result DataFrames."""
    module = _module()
    coverage = [module._coverage("ITEM_PERMISSION_ENUMERATION_UNAVAILABLE", "not enumerable", scope_type="ITEM")]
    monkeypatch.setattr(
        module,
        "_discover_access_evidence",
        lambda spark: ([_grant()], [], {"item-a": "DELEGATED_IDENTITY"}, False, coverage),
    )
    result = module.scan_effective_access(
        identity_map_df=_identity_map(spark_session),
        group_membership_df=_membership_map(spark_session),
    )
    access = result["access"].collect()[0].asDict(recursive=True)
    assert access["access_verification_status"] == "UNVERIFIED"
    assert access["effective_permissions"] == []
    assert access["observed_permissions"] == ["READ"]
    assert "ITEM_PERMISSION_ENUMERATION_UNAVAILABLE" in {
        row.reason_code for row in result["coverage"].collect()
    }
