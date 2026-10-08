"""Unit tests for person-level effective Fabric access resolution."""

from __future__ import annotations

import importlib


def _identity_map(spark):
    return spark.createDataFrame(
        [
            ("user-a", "Alice", "alice@example.com", "User", ""),
            ("user-b", "Bob", "bob@example.com", "User", ""),
            ("group-a", "Data Readers", "", "Group", "SecurityGroup"),
            ("group-b", "Nested Readers", "", "Group", "SecurityGroup"),
            ("group-dl", "Announcements", "", "Group", "DistributionList"),
        ],
        ["object_id", "display_name", "user_principal_name", "principal_type", "group_type"],
    )


def _memberships(spark):
    return spark.createDataFrame(
        [
            ("group-a", "user-a"),
            ("group-a", "group-b"),
            ("group-b", "user-b"),
            ("group-b", "group-a"),
        ],
        ["group_object_id", "member_object_id"],
    )


def _table(item_id="item-a", table_name="orders"):
    return {
        "table_id": f"workspace-a/{item_id}/sales/{table_name}",
        "workspace_id": "workspace-a",
        "workspace_name": "Analytics",
        "item_id": item_id,
        "item_name": "Curated",
        "item_type": "LAKEHOUSE",
        "schema_name": "sales",
        "table_name": table_name,
        "table_path": f"Tables/sales/{table_name}",
        "object_type": "TABLE",
    }


def test_scan_effective_access_is_exposed_from_package_root():
    """Expose the one-call resolver from notebook-friendly import paths."""
    from fabricops_kit import scan_effective_access
    from fabricops_kit.access_scanner import scan_effective_access as package_scan

    assert scan_effective_access is package_scan
    assert scan_effective_access.__module__ == "fabricops_kit.access_scanner.scan_effective_access"


def test_effective_scan_expands_nested_groups_and_consolidates_all_surfaces(monkeypatch, spark_session):
    """Resolve people while preserving overlapping Workspace, SQL, and OneLake grants."""
    module = importlib.import_module("fabricops_kit.access_scanner.scan_effective_access")
    table = _table()
    grants = [
        module._grant(
            table,
            principal_id="group-a",
            principal_type="Group",
            principal_name="Data Readers",
            access_surface="WORKSPACE",
            access_value="READWRITE",
            access_state="GRANT",
            permission_source="WORKSPACE_ROLE",
            role_name="Contributor",
            scope_type="WORKSPACE",
            scope_value="workspace-a",
        ),
        module._grant(
            table,
            principal_id="group-a",
            principal_type="Group",
            principal_name="Data Readers",
            access_surface="SQL",
            access_value="SELECT",
            access_state="GRANT",
            permission_source="VIA_ROLE",
            role_name="report_reader",
            scope_type="SCHEMA",
            scope_value="sales",
        ),
        module._grant(
            table,
            principal_id="user-a",
            principal_type="User",
            principal_name="Alice",
            access_surface="SQL",
            access_value="SELECT",
            access_state="GRANT",
            permission_source="DIRECT_PERMISSION",
            scope_type="OBJECT_OR_COLUMN",
            scope_value="sales.orders",
        ),
        module._grant(
            table,
            principal_id="user-b",
            principal_type="User",
            principal_name="Bob",
            access_surface="ONELAKE",
            access_value="Read",
            access_state="Permit",
            permission_source="ONELAKE_ROLE",
            role_name="RestrictedReaders",
            scope_type="PATH",
            scope_value="Tables/sales/orders",
            restrictions_json='{"rows":["region = SG"]}',
        ),
    ]
    monkeypatch.setattr(
        module,
        "_discover_access_evidence",
        lambda spark: (
            grants,
            [module._coverage("WORKSPACE_ROLE_SCAN_FAILED", "not visible", status="ERROR")],
        ),
    )

    result = module.scan_effective_access(
        identity_map_df=_identity_map(spark_session),
        group_membership_df=_memberships(spark_session),
    )

    rows = {
        (row.person_object_id, row.access_surface): row.asDict(recursive=True)
        for row in result["access"].collect()
    }
    assert rows[("user-a", "WORKSPACE")]["effective_permissions"] == ["READ", "WRITE"]
    assert rows[("user-b", "WORKSPACE")]["inheritance_paths"] == [
        "group-a -> group-b -> user-b"
    ]
    assert rows[("user-a", "SQL")]["contributing_grant_count"] == 2
    assert rows[("user-b", "SQL")]["effective_permissions"] == ["READ"]
    assert rows[("user-b", "ONELAKE")]["is_restricted"] is True
    coverage_codes = {row.reason_code for row in result["coverage"].collect()}
    assert "GROUP_MEMBERSHIP_CYCLE" in coverage_codes
    assert "WORKSPACE_ROLE_SCAN_FAILED" in coverage_codes


def test_effective_scan_reports_unresolved_distribution_and_denied_access(monkeypatch, spark_session):
    """Keep unsupported principals and permission restrictions out of effective access."""
    module = importlib.import_module("fabricops_kit.access_scanner.scan_effective_access")
    table = _table(item_id="warehouse-a", table_name="finance")
    grants = [
        module._grant(
            table,
            principal_id="missing-user",
            principal_type="User",
            principal_name="Unknown",
            access_surface="SQL",
            access_value="SELECT",
            access_state="GRANT",
            permission_source="DIRECT_PERMISSION",
        ),
        module._grant(
            table,
            principal_id="group-dl",
            principal_type="Group",
            principal_name="Announcements",
            access_surface="ONELAKE",
            access_value="Read",
            access_state="Permit",
            permission_source="ONELAKE_ROLE",
        ),
        module._grant(
            table,
            principal_id="user-a",
            principal_type="User",
            principal_name="Alice",
            access_surface="SQL",
            access_value="SELECT",
            access_state="GRANT",
            permission_source="DIRECT_PERMISSION",
        ),
        module._grant(
            table,
            principal_id="user-a",
            principal_type="User",
            principal_name="Alice",
            access_surface="SQL",
            access_value="SELECT",
            access_state="DENY",
            permission_source="DIRECT_PERMISSION",
        ),
    ]
    monkeypatch.setattr(module, "_discover_access_evidence", lambda spark: (grants, []))

    result = module.scan_effective_access(
        identity_map_df=_identity_map(spark_session),
        group_membership_df=_memberships(spark_session),
    )

    assert result["access"].count() == 0
    coverage_codes = {row.reason_code for row in result["coverage"].collect()}
    assert {
        "UNRESOLVED_IDENTITY",
        "GROUP_TYPE_NOT_EXPANDED",
        "PERMISSION_DENY_APPLIED",
    }.issubset(coverage_codes)


def test_workspace_semantics_keep_lakehouse_viewer_sql_access_separate():
    """Keep Viewer SQL access distinct from OneLake file access."""
    module = importlib.import_module("fabricops_kit.access_scanner.scan_effective_access")
    observations = [
        {
            "workspace_id": "workspace-a",
            "principal_id": "user-a",
            "user_type": "USER",
            "user_principal": "alice@example.com",
            "role_name": "Viewer",
            "access_value": "READ",
        }
    ]

    lakehouse_grants = module._workspace_grants([_table()], observations)
    assert len(lakehouse_grants) == 1
    assert lakehouse_grants[0]["access_channels"] == ["SQL"]
    warehouse = {**_table(), "item_type": "WAREHOUSE"}
    warehouse_grants = module._workspace_grants([warehouse], observations)
    assert warehouse_grants[0]["access_channels"] == ["SQL"]


def test_pure_resolution_covers_nested_groups_multiple_grants_and_restrictions():
    """Exercise effective resolution without requiring a local Spark runtime."""
    module = importlib.import_module("fabricops_kit.access_scanner.scan_effective_access")
    identities = {
        row[0]: {
            "object_id": row[0],
            "display_name": row[1],
            "user_principal_name": row[2],
            "principal_type": row[3].upper(),
            "group_type": row[4].upper(),
        }
        for row in [
            ("user-a", "Alice", "alice@example.com", "USER", ""),
            ("user-b", "Bob", "bob@example.com", "USER", ""),
            ("group-a", "Readers", "", "GROUP", "SECURITY_GROUP"),
            ("group-b", "Nested", "", "GROUP", "SECURITY_GROUP"),
            ("group-dl", "Mail", "", "GROUP", "DISTRIBUTION_LIST"),
        ]
    }
    memberships = {
        "group-a": ["user-a", "group-b"],
        "group-b": ["user-b", "group-a"],
    }
    table = _table()
    grants = [
        module._grant(
            table,
            principal_id="group-a",
            principal_type="Group",
            principal_name="Readers",
            access_surface="SQL",
            access_value="SELECT",
            access_state="GRANT",
            permission_source="VIA_ROLE",
            role_name="reader",
        ),
        module._grant(
            table,
            principal_id="user-a",
            principal_type="User",
            principal_name="Alice",
            access_surface="SQL",
            access_value="SELECT",
            access_state="GRANT",
            permission_source="DIRECT_PERMISSION",
        ),
        module._grant(
            table,
            principal_id="user-b",
            principal_type="User",
            principal_name="Bob",
            access_surface="ONELAKE",
            access_value="Read",
            access_state="Permit",
            permission_source="ONELAKE_ROLE",
            restrictions_json='{"columns":["region"]}',
        ),
        module._grant(
            table,
            principal_id="missing",
            principal_type="User",
            principal_name="Unknown",
            access_surface="WORKSPACE",
            access_value="READ",
            access_state="GRANT",
            permission_source="WORKSPACE_ROLE",
        ),
        module._grant(
            table,
            principal_id="group-dl",
            principal_type="Group",
            principal_name="Mail",
            access_surface="ONELAKE",
            access_value="Read",
            access_state="Permit",
            permission_source="ONELAKE_ROLE",
        ),
    ]
    coverage = []

    resolved = module._resolve_grants(
        grants,
        identities=identities,
        memberships=memberships,
        coverage=coverage,
    )
    rows = {
        (row["person_object_id"], row["access_surface"]): row
        for row in module._consolidate(resolved, coverage)
    }

    assert rows[("user-a", "SQL")]["contributing_grant_count"] == 2
    assert rows[("user-b", "SQL")]["inheritance_paths"] == [
        "group-a -> group-b -> user-b"
    ]
    assert rows[("user-b", "ONELAKE")]["is_restricted"] is True
    assert {row["reason_code"] for row in coverage}.issuperset(
        {"GROUP_MEMBERSHIP_CYCLE", "UNRESOLVED_IDENTITY", "GROUP_TYPE_NOT_EXPANDED"}
    )


def test_pure_resolution_reports_incomplete_groups_and_applies_sql_denies():
    """Do not infer people from incomplete groups or permissions removed by deny."""
    module = importlib.import_module("fabricops_kit.access_scanner.scan_effective_access")
    identities = {
        "user-a": {
            "object_id": "user-a",
            "display_name": "Alice",
            "user_principal_name": "alice@example.com",
            "principal_type": "USER",
            "group_type": "",
        },
        "group-a": {
            "object_id": "group-a",
            "display_name": "Readers",
            "user_principal_name": "",
            "principal_type": "GROUP",
            "group_type": "SECURITY_GROUP",
        },
    }
    coverage = []
    assert module._expand_principal(
        "group-a",
        identities=identities,
        memberships={},
        coverage=coverage,
    ) == []

    table = _table()
    grants = [
        module._grant(
            table,
            principal_id="user-a",
            principal_type="User",
            principal_name="Alice",
            access_surface="SQL",
            access_value="SELECT",
            access_state=state,
            permission_source="DIRECT_PERMISSION",
        )
        for state in ("GRANT", "DENY")
    ]
    resolved = module._resolve_grants(
        grants,
        identities=identities,
        memberships={},
        coverage=coverage,
    )

    assert module._consolidate(resolved, coverage) == []
    assert {row["reason_code"] for row in coverage}.issuperset(
        {"GROUP_MEMBERSHIP_INCOMPLETE", "PERMISSION_DENY_APPLIED"}
    )
