"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import ast
import inspect
import sys
import types
from pathlib import Path

from fabricops_kit.config import PathConfig
from fabricops_kit.fabric_input_output import FabricStore
import fabricops_kit.fabric_input_output as io
from tests.integration.test_storage_io import _Frame, _Spark


PUBLIC_IO_CALLABLES = {
    "read_lakehouse_table",
    "write_lakehouse_table",
    "read_lakehouse_csv",
    "read_lakehouse_parquet",
    "read_lakehouse_excel",
    "read_warehouse_table",
    "write_warehouse_table",
}

DELETED_INTERNAL_HELPERS = {
    "_get_fabric_runtime_context",
    "_check_naming_convention",
    "_seed_minimal_sample_source_table",
    "_registered_table_identifier",
    "_uses_registered_metadata_table",
    "_current_database_matches",
}


def _store(target: str, kind: str, name: str, *, schema_enabled: bool = False, schema: str | None = None) -> FabricStore:
    return FabricStore(
        env="dev",
        workspace_id=f"dev-{target}-workspace",
        item_id=f"dev-{target}-item",
        name=name,
        kind=kind,
        schema_enabled=schema_enabled,
        schema=schema,
    )


def _io_config() -> PathConfig:
    return PathConfig(
        paths={
            "dev": {
                "source": _store("source", "lakehouse", "lh_source_dev"),
                "unified": _store("unified", "lakehouse", "lh_unified_dev"),
                "product": _store("product", "lakehouse", "lh_product_dev"),
                "metadata": _store("metadata", "lakehouse", "lh_metadata_dev"),
                "warehouse": _store("warehouse", "warehouse", "wh_product_dev"),
            }
        }
    )


def _schema_io_config() -> PathConfig:
    return PathConfig(
        paths={
            "dev": {
                "source": _store("source", "lakehouse", "lh_source_dev", schema_enabled=True, schema="src"),
                "unified": _store("unified", "lakehouse", "lh_unified_dev", schema_enabled=True, schema="dbo"),
                "metadata": _store("metadata", "lakehouse", "lh_metadata_dev", schema_enabled=True, schema="meta"),
            }
        }
    )


def test_lakehouse_table_read_routes_every_configured_lakehouse_store():
    """Verify lakehouse table read routes every configured lakehouse store."""
    config = _io_config()

    for target in ("source", "unified", "product"):
        spark = _Spark()
        io.read_lakehouse_table(config, "dev", target, "orders", schema=None, spark_session=spark)

        expected_path = f"abfss://dev-{target}-workspace@onelake.dfs.fabric.microsoft.com/dev-{target}-item/Tables/orders"
        assert ("format", "delta") in spark.read.calls
        assert ("load", expected_path) in spark.read.calls

    metadata_spark = _Spark()
    io.read_lakehouse_table(config, "dev", "metadata", "orders", schema=None, spark_session=metadata_spark)
    metadata_path = "abfss://dev-metadata-workspace@onelake.dfs.fabric.microsoft.com/dev-metadata-item/Tables/orders"
    assert ("format", "delta") in metadata_spark.read.calls
    assert ("load", metadata_path) in metadata_spark.read.calls
    assert metadata_spark.table_calls == []


def test_lakehouse_table_write_routes_to_configured_store():
    """Verify lakehouse table write routes to configured store."""
    config = _io_config()
    frame = _Frame()

    io.write_lakehouse_table(frame, config, "dev", "metadata", "metadata_orders", schema=None, mode="overwrite", options={"overwriteSchema": "true"}, verbose=False)

    expected_path = "abfss://dev-metadata-workspace@onelake.dfs.fabric.microsoft.com/dev-metadata-item/Tables/metadata_orders"
    assert ("mode", "overwrite") in frame.write.calls
    assert ("format", "delta") in frame.write.calls
    assert ("save", expected_path) in frame.write.calls
    assert not any(call[0] == "saveAsTable" for call in frame.write.calls)


def test_lakehouse_file_readers_build_configured_files_paths():
    """Verify lakehouse file readers build configured files paths."""
    config = _io_config()
    spark = _Spark()

    io.read_lakehouse_csv(config, "dev", "source", "Files/raw/orders.csv", spark_session=spark)
    io.read_lakehouse_parquet(config, "dev", "unified", "curated/orders.parquet", spark_session=spark, verbose=False)

    assert ("csv", "abfss://dev-source-workspace@onelake.dfs.fabric.microsoft.com/dev-source-item/Files/raw/orders.csv") in spark.read.calls
    assert ("parquet", "abfss://dev-unified-workspace@onelake.dfs.fabric.microsoft.com/dev-unified-item/Files/curated/orders.parquet") in spark.read.calls


def test_lakehouse_excel_remains_exposed_and_callable():
    """Verify lakehouse excel remains exposed and callable."""
    assert hasattr(io, "read_lakehouse_excel")
    assert callable(io.read_lakehouse_excel)
    assert inspect.signature(io.read_lakehouse_excel).parameters["relative_path"]


def test_warehouse_helpers_build_configured_query(monkeypatch):
    """Verify warehouse helpers build configured query."""
    config = _io_config()

    class Constants:
        WorkspaceId = "workspace_id"
        DatawarehouseId = "datawarehouse_id"

    constants_module = types.ModuleType("com.microsoft.spark.fabric.Constants")
    constants_module.Constants = Constants
    monkeypatch.setitem(sys.modules, "com", types.ModuleType("com"))
    monkeypatch.setitem(sys.modules, "com.microsoft", types.ModuleType("com.microsoft"))
    monkeypatch.setitem(sys.modules, "com.microsoft.spark", types.ModuleType("com.microsoft.spark"))
    monkeypatch.setitem(sys.modules, "com.microsoft.spark.fabric", types.ModuleType("com.microsoft.spark.fabric"))
    monkeypatch.setitem(sys.modules, "com.microsoft.spark.fabric.Constants", constants_module)

    spark = _Spark()
    frame = _Frame()
    read_result = io.read_warehouse_table(config, "dev", "warehouse", "dbo", "orders", spark_session=spark)
    io.write_warehouse_table(frame, config, "dev", "warehouse", "dbo", "orders", mode="overwrite")

    assert read_result == {"synapsesql": "wh_product_dev.dbo.orders"}
    assert ("option", "workspace_id", "dev-warehouse-workspace") in spark.read.calls
    assert ("option", "datawarehouse_id", "dev-warehouse-item") in spark.read.calls
    assert ("mode", "overwrite") in frame.write.calls
    assert ("option", "workspace_id", "dev-warehouse-workspace") in frame.write.calls
    assert ("option", "datawarehouse_id", "dev-warehouse-item") in frame.write.calls
    assert ("synapsesql", "wh_product_dev.dbo.orders") in frame.write.calls
    assert not any(call[0] == "saveAsTable" for call in frame.write.calls)
    assert spark.table_calls == []


def test_deleted_internal_helpers_are_absent_and_unreferenced():
    """Verify deleted internal helpers are absent and unreferenced."""
    source = Path("src/fabricops_kit/fabric_input_output.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    defined_functions = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    referenced_names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}

    assert DELETED_INTERNAL_HELPERS.isdisjoint(defined_functions)
    assert DELETED_INTERNAL_HELPERS.isdisjoint(referenced_names)


def test_public_v1_io_callable_list_remains_unchanged():
    """Verify public v1 io callable list remains unchanged."""
    public_functions = {
        name
        for name, value in vars(io).items()
        if inspect.isfunction(value) and value.__module__ == io.__name__ and not name.startswith("_")
    }

    assert public_functions == PUBLIC_IO_CALLABLES


def test_lakehouse_table_read_with_explicit_schema_uses_schema_physical_path():
    """Verify lakehouse table read with explicit schema uses schema physical path."""
    config = _io_config()
    spark = _Spark()

    io.read_lakehouse_table(config, "dev", "metadata", "METADATA_GUARDRAIL_RULES", schema="METADATA", spark_session=spark)

    expected_path = "abfss://dev-metadata-workspace@onelake.dfs.fabric.microsoft.com/dev-metadata-item/Tables/METADATA/METADATA_GUARDRAIL_RULES"
    assert ("load", expected_path) in spark.read.calls
    assert spark.table_calls == []


def test_lakehouse_table_write_with_explicit_schema_uses_schema_physical_path():
    """Verify lakehouse table write with explicit schema uses schema physical path."""
    config = _io_config()
    frame = _Frame()

    io.write_lakehouse_table(frame, config, "dev", "metadata", "METADATA_GUARDRAIL_RULES", schema="METADATA", mode="overwrite", options={"overwriteSchema": "true"}, verbose=False)

    expected_path = "abfss://dev-metadata-workspace@onelake.dfs.fabric.microsoft.com/dev-metadata-item/Tables/METADATA/METADATA_GUARDRAIL_RULES"
    assert ("save", expected_path) in frame.write.calls
    assert not any(call[0] == "saveAsTable" for call in frame.write.calls)


def test_lakehouse_schema_enabled_target_routes_paths_and_identifiers_from_config():
    """Verify lakehouse schema enabled target routes paths and identifiers from config."""
    config = _schema_io_config()
    spark = _Spark()
    frame = _Frame()

    io.read_lakehouse_table(config, "dev", "source", "orders", schema="src", spark_session=spark)
    io.write_lakehouse_table(frame, config, "dev", "metadata", "METADATA_GUARDRAIL_RULES", schema="meta", mode="overwrite", options={"overwriteSchema": "true"}, verbose=False)
    metadata_store = config.paths["dev"]["metadata"]

    assert ("load", "abfss://dev-source-workspace@onelake.dfs.fabric.microsoft.com/dev-source-item/Tables/src/orders") in spark.read.calls
    assert ("save", "abfss://dev-metadata-workspace@onelake.dfs.fabric.microsoft.com/dev-metadata-item/Tables/meta/METADATA_GUARDRAIL_RULES") in frame.write.calls
    assert io._resolve_lakehouse_table_identifier(metadata_store, "METADATA_GUARDRAIL_RULES") == "meta.METADATA_GUARDRAIL_RULES"


def test_lakehouse_schema_disabled_target_routes_legacy_paths_and_identifiers():
    """Verify lakehouse schema disabled target routes legacy paths and identifiers."""
    config = _io_config()
    metadata_store = config.paths["dev"]["metadata"]

    assert io._resolve_lakehouse_table_path(metadata_store, "orders").endswith("/Tables/orders")
    assert io._resolve_lakehouse_table_identifier(metadata_store, "orders") == "orders"


import pytest


@pytest.mark.parametrize("schema", ["", "bad-name", "METADATA.TABLE", "META/DATA", "1META"])
def test_lakehouse_table_schema_validation_rejects_unsafe_names(schema):
    """Verify lakehouse table schema validation rejects unsafe names."""
    with pytest.raises(ValueError):
        io.read_lakehouse_table(_io_config(), "dev", "metadata", "TABLE", schema=schema, spark_session=_Spark())


@pytest.mark.parametrize("table", ["schema.table", "bad/name", "bad-name", "1TABLE", ""])
def test_lakehouse_table_validation_rejects_unsafe_names(table):
    """Verify lakehouse table validation rejects unsafe names."""
    with pytest.raises(ValueError):
        io.read_lakehouse_table(_io_config(), "dev", "metadata", table, schema=None, spark_session=_Spark())
