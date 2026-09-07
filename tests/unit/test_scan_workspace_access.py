"""Unit tests for the workspace SQL access scanner."""

from __future__ import annotations

from datetime import datetime, timezone
import importlib
from types import SimpleNamespace

import pytest

from fabricops_kit.config.shared import build_table_id


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
                "table_id": build_table_id("warehouse", "warehouse", "sales", "orders"),
                "environment_name": "dev",
                "store_type": "Warehouse",
                "layer": "gold",
                "schema_name": "sales",
                "table_name": "orders",
                "is_active": True,
            },
            {
                "metadata_level": "table",
                "table_id": build_table_id("warehouse", "warehouse", "sales", "customers"),
                "environment_name": "dev",
                "store_type": "Warehouse",
                "layer": "gold",
                "schema_name": "sales",
                "table_name": "customers",
                "is_active": True,
            },
            {
                "metadata_level": "table",
                "table_id": build_table_id("warehouse", "warehouse", "archive", "orders_archive"),
                "environment_name": "dev",
                "store_type": "Warehouse",
                "layer": "gold",
                "schema_name": "archive",
                "table_name": "orders_archive",
                "is_active": False,
            },
            {
                "metadata_level": "table",
                "table_id": build_table_id("lakehouse", "curated_lakehouse", "sales", "orders"),
                "environment_name": "dev",
                "store_type": "Lakehouse",
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


def test_scan_workspace_access_maps_table_schema_and_database_scopes(monkeypatch, spark_session):
    """Map object, schema, and database permissions to governed tables."""
    module = importlib.import_module("fabricops_kit.access.scan_workspace_access")
    calls = []

    def fake_read(query, *, target, spark_session=None, context=None, **options):
        calls.append((query, target, context))
        return _observations(spark_session)

    monkeypatch.setattr(module, "read_sql_endpoint_query_core", fake_read)
    monkeypatch.setattr(
        module,
        "resolve_fabric_context",
        lambda **kwargs: ({"config": "test"}, "dev", {"config": {"config": "test"}, "env": "dev"}),
    )
    monkeypatch.setattr(module, "build_runtime_audit_fields", lambda **kwargs: dict(AUDIT_FIELDS))
    monkeypatch.setattr(module, "_target_store_kinds", lambda *args: {"warehouse": "warehouse"})

    result = module.scan_workspace_access(
        _catalogue(spark_session),
        targets="warehouse",
        access_snapshot_id="snapshot-1",
        spark_session=spark_session,
        context={"env": "dev"},
    )

    access_rows = [row.asDict(recursive=True) for row in result["access"].collect()]
    unmatched_rows = [row.asDict(recursive=True) for row in result["unmatched"].collect()]

    by_principal = {}
    for row in access_rows:
        by_principal.setdefault(row["user_principal"], set()).add(row["table_id"])

    orders_id = build_table_id("warehouse", "warehouse", "sales", "orders")
    customers_id = build_table_id("warehouse", "warehouse", "sales", "customers")
    assert by_principal["alice@example.com"] == {orders_id}
    assert by_principal["bob@example.com"] == {orders_id, customers_id}
    assert by_principal["carol@example.com"] == {orders_id, customers_id}
    assert "dave@example.com" not in by_principal

    assert {row["access_snapshot_id"] for row in access_rows} == {"snapshot-1"}
    assert {row["environment_name"] for row in access_rows} == {"dev"}
    assert all(row["access_id"] for row in access_rows)
    assert all(row["_committed_by"] == "tester@example.com" for row in access_rows)

    assert len(unmatched_rows) == 1
    assert unmatched_rows[0]["user_name"] == "dave@example.com"
    assert unmatched_rows[0]["target"] == "warehouse"
    assert unmatched_rows[0]["unmatched_reason"] == "not_registered_in_catalogue"

    expected_columns = module.metadata_table_schema_registry()[module.ACCESS_TABLE].fieldNames()
    assert result["access"].columns == expected_columns

    assert len(calls) == 1
    assert calls[0][1] == "warehouse"
    assert calls[0][0].lstrip().upper().startswith("WITH")
    assert "DECLARE" not in calls[0][0].upper()
    assert "SP_EXECUTESQL" not in calls[0][0].upper()


def test_scan_workspace_access_scans_each_unique_target(monkeypatch, spark_session):
    """Scan each unique configured workspace data item target once."""
    module = importlib.import_module("fabricops_kit.access.scan_workspace_access")
    calls = []

    empty = _observations(spark_session).limit(0)

    def fake_read(query, *, target, spark_session=None, context=None, **options):
        calls.append(target)
        return empty

    monkeypatch.setattr(module, "read_sql_endpoint_query_core", fake_read)
    monkeypatch.setattr(
        module,
        "resolve_fabric_context",
        lambda **kwargs: ({}, "dev", {"config": {}, "env": "dev"}),
    )
    monkeypatch.setattr(module, "build_runtime_audit_fields", lambda **kwargs: dict(AUDIT_FIELDS))
    monkeypatch.setattr(
        module,
        "_target_store_kinds",
        lambda *args: {"warehouse": "warehouse", "curated_lakehouse": "lakehouse"},
    )

    result = module.scan_workspace_access(
        _catalogue(spark_session),
        targets=["warehouse", "warehouse", "curated_lakehouse"],
        access_snapshot_id="snapshot-2",
        spark_session=spark_session,
    )

    assert calls == ["warehouse", "curated_lakehouse"]
    assert result["access"].count() == 0
    assert result["unmatched"].count() == 0


def test_catalogue_includes_registered_lakehouse_sql_endpoint_tables(spark_session):
    """Do not restrict governed physical tables to Warehouse store types."""
    module = importlib.import_module("fabricops_kit.access.scan_workspace_access")

    tables = module._catalogue_tables(
        _catalogue(spark_session),
        environment_name="dev",
        target_store_kinds={"curated_lakehouse": "lakehouse"},
    )

    assert [row._catalogue_table_id for row in tables.collect()] == [
        build_table_id("lakehouse", "curated_lakehouse", "sales", "orders")
    ]


def test_catalogue_relates_mixed_targets_by_canonical_physical_identity(spark_session):
    """Relate configured item keys independently of medallion layer values."""
    module = importlib.import_module("fabricops_kit.access.scan_workspace_access")

    tables = module._catalogue_tables(
        _catalogue(spark_session),
        environment_name="dev",
        target_store_kinds={"warehouse": "warehouse", "curated_lakehouse": "lakehouse"},
    )

    assert {(row._catalogue_target, row._catalogue_table_id) for row in tables.collect()} == {
        ("warehouse", build_table_id("warehouse", "warehouse", "sales", "orders")),
        ("warehouse", build_table_id("warehouse", "warehouse", "sales", "customers")),
        (
            "curated_lakehouse",
            build_table_id("lakehouse", "curated_lakehouse", "sales", "orders"),
        ),
    }


@pytest.mark.parametrize("kind", ["warehouse", "lakehouse"])
def test_sql_endpoint_reader_supports_configured_physical_data_items(monkeypatch, kind):
    """Address Warehouse and Lakehouse SQL analytics endpoints from configuration."""
    module = importlib.import_module("fabricops_kit.io.shared")
    store = SimpleNamespace(kind=kind)
    calls = []
    monkeypatch.setattr(module, "resolve_fabric_context", lambda **kwargs: (object(), "dev", {}))
    monkeypatch.setattr(module, "get_store", lambda config, env, target: store)
    monkeypatch.setattr(module, "validate_select_query", lambda query: query)
    monkeypatch.setattr(module, "get_spark_session", lambda spark_session: "spark")
    monkeypatch.setattr(
        module,
        "read_warehouse_synapsesql",
        lambda spark, resolved_store, query, options=None: calls.append(
            (spark, resolved_store, query, options)
        ) or "frame",
    )

    assert module.read_sql_endpoint_query_core("SELECT 1", target="item") == "frame"
    assert calls == [("spark", store, "SELECT 1", None)]


def test_sql_endpoint_reader_rejects_unsupported_target_configuration(monkeypatch):
    """Reject configured targets that cannot expose SQL permission catalogue views."""
    module = importlib.import_module("fabricops_kit.io.shared")
    monkeypatch.setattr(module, "resolve_fabric_context", lambda **kwargs: (object(), "dev", {}))
    monkeypatch.setattr(module, "get_store", lambda config, env, target: SimpleNamespace(kind="files"))

    with pytest.raises(ValueError, match="expected a warehouse or lakehouse store"):
        module.read_sql_endpoint_query_core("SELECT 1", target="unsupported")
