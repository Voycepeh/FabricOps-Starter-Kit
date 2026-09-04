from __future__ import annotations

from datetime import datetime, timezone
import importlib


AUDIT_FIELDS = {
    "_committed_by": "tester@example.com",
    "_committed_at": datetime(2026, 9, 4, 12, 0, tzinfo=timezone.utc),
    "_workspace_id": "workspace-id",
    "_workspace_name": "workspace",
    "_notebook_id": "notebook-id",
    "_notebook_name": "90_access_inventory",
    "_metadata_lakehouse_name": "metadata_lakehouse",
    "_activity_id": "activity-id",
}


def _catalogue(spark_session):
    return spark_session.createDataFrame(
        [
            {
                "metadata_level": "table",
                "table_id": "table-orders",
                "environment_name": "dev",
                "store_type": "Warehouse",
                "layer": "gold",
                "schema_name": "sales",
                "table_name": "orders",
                "is_active": True,
            },
            {
                "metadata_level": "table",
                "table_id": "table-customers",
                "environment_name": "dev",
                "store_type": "Warehouse",
                "layer": "gold",
                "schema_name": "sales",
                "table_name": "customers",
                "is_active": True,
            },
            {
                "metadata_level": "table",
                "table_id": "table-archive",
                "environment_name": "dev",
                "store_type": "Warehouse",
                "layer": "gold",
                "schema_name": "archive",
                "table_name": "orders_archive",
                "is_active": False,
            },
            {
                "metadata_level": "table",
                "table_id": "table-other-target",
                "environment_name": "dev",
                "store_type": "Warehouse",
                "layer": "silver",
                "schema_name": "sales",
                "table_name": "orders",
                "is_active": True,
            },
        ]
    )


def _observations(spark_session):
    columns = [
        "user_name",
        "user_type",
        "role_name",
        "permission_source",
        "state_desc",
        "permission_name",
        "class_desc",
        "database_name",
        "schema_name",
        "object_name",
        "object_type",
    ]
    rows = [
        ("alice@example.com", "EXTERNAL_USER", None, "Direct Permission", "GRANT", "SELECT", "OBJECT_OR_COLUMN", "GoldWarehouse", "sales", "orders", "USER_TABLE"),
        ("bob@example.com", "EXTERNAL_USER", "reader", "Via Role", "GRANT", "SELECT", "SCHEMA", "GoldWarehouse", "sales", None, None),
        ("carol@example.com", "EXTERNAL_USER", "db_reader", "Via Role", "GRANT", "SELECT", "DATABASE", "GoldWarehouse", None, None, None),
        ("dave@example.com", "EXTERNAL_USER", None, "Direct Permission", "DENY", "SELECT", "OBJECT_OR_COLUMN", "GoldWarehouse", "sales", "not_registered", "USER_TABLE"),
    ]
    return spark_session.createDataFrame(rows, columns)


def test_scan_warehouse_access_maps_table_schema_and_database_scopes(monkeypatch, spark_session):
    module = importlib.import_module("fabricops_kit.access.scan_warehouse_access")
    calls = []

    def fake_read(query, *, target, spark_session=None, context=None, **options):
        calls.append((query, target, context))
        return _observations(spark_session)

    monkeypatch.setattr(module, "read_warehouse_query", fake_read)
    monkeypatch.setattr(
        module,
        "resolve_fabric_context",
        lambda **kwargs: ({"config": "test"}, "dev", {"config": {"config": "test"}, "env": "dev"}),
    )
    monkeypatch.setattr(module, "build_runtime_audit_fields", lambda **kwargs: dict(AUDIT_FIELDS))

    result = module.scan_warehouse_access(
        _catalogue(spark_session),
        targets="gold",
        access_snapshot_id="snapshot-1",
        spark_session=spark_session,
        context={"env": "dev"},
    )

    access_rows = [row.asDict(recursive=True) for row in result["access"].collect()]
    unmatched_rows = [row.asDict(recursive=True) for row in result["unmatched"].collect()]

    by_principal = {}
    for row in access_rows:
        by_principal.setdefault(row["user_principal"], set()).add(row["table_id"])

    assert by_principal["alice@example.com"] == {"table-orders"}
    assert by_principal["bob@example.com"] == {"table-orders", "table-customers"}
    assert by_principal["carol@example.com"] == {"table-orders", "table-customers"}
    assert "dave@example.com" not in by_principal

    assert {row["access_snapshot_id"] for row in access_rows} == {"snapshot-1"}
    assert {row["environment_name"] for row in access_rows} == {"dev"}
    assert all(row["access_id"] for row in access_rows)
    assert all(row["_committed_by"] == "tester@example.com" for row in access_rows)

    assert len(unmatched_rows) == 1
    assert unmatched_rows[0]["user_name"] == "dave@example.com"
    assert unmatched_rows[0]["target"] == "gold"
    assert unmatched_rows[0]["unmatched_reason"] == "not_registered_in_catalogue"

    expected_columns = module.metadata_table_schema_registry()[module.ACCESS_TABLE].fieldNames()
    assert result["access"].columns == expected_columns

    assert len(calls) == 1
    assert calls[0][1] == "gold"
    assert calls[0][0].lstrip().upper().startswith("WITH")
    assert "DECLARE" not in calls[0][0].upper()
    assert "SP_EXECUTESQL" not in calls[0][0].upper()


def test_scan_warehouse_access_scans_each_unique_target(monkeypatch, spark_session):
    module = importlib.import_module("fabricops_kit.access.scan_warehouse_access")
    calls = []

    empty = _observations(spark_session).limit(0)

    def fake_read(query, *, target, spark_session=None, context=None, **options):
        calls.append(target)
        return empty

    monkeypatch.setattr(module, "read_warehouse_query", fake_read)
    monkeypatch.setattr(
        module,
        "resolve_fabric_context",
        lambda **kwargs: ({}, "dev", {"config": {}, "env": "dev"}),
    )
    monkeypatch.setattr(module, "build_runtime_audit_fields", lambda **kwargs: dict(AUDIT_FIELDS))

    result = module.scan_warehouse_access(
        _catalogue(spark_session),
        targets=["gold", "gold", "silver"],
        access_snapshot_id="snapshot-2",
        spark_session=spark_session,
    )

    assert calls == ["gold", "silver"]
    assert result["access"].count() == 0
    assert result["unmatched"].count() == 0
