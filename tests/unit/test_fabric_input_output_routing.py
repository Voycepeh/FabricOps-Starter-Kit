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
    "read_warehouse_query",
}

DELETED_INTERNAL_HELPERS = {
    "_get_fabric_runtime_context",
    "_check_naming_convention",
    "_seed_minimal_sample_source_table",
    "_registered_table_identifier",
    "_uses_registered_metadata_table",
    "_current_database_matches",
    "_qualified_table_name",
}

DELETED_INTERNAL_CLASSES = {"_PandasProxy"}


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
    context = {"config": config, "env": "dev"}

    for target in ("source", "unified", "product"):
        spark = _Spark()
        io.read_lakehouse_table("orders", target=target, schema=None, spark_session=spark, context=context)

        expected_path = f"abfss://dev-{target}-workspace@onelake.dfs.fabric.microsoft.com/dev-{target}-item/Tables/orders"
        assert ("format", "delta") in spark.read.calls
        assert ("load", expected_path) in spark.read.calls

    metadata_spark = _Spark()
    io.read_lakehouse_table("orders", target="metadata", schema=None, spark_session=metadata_spark, context=context)
    metadata_path = "abfss://dev-metadata-workspace@onelake.dfs.fabric.microsoft.com/dev-metadata-item/Tables/orders"
    assert ("format", "delta") in metadata_spark.read.calls
    assert ("load", metadata_path) in metadata_spark.read.calls
    assert metadata_spark.table_calls == []


def test_lakehouse_table_write_routes_to_configured_store():
    """Verify lakehouse table write routes to configured store."""
    config = _io_config()
    context = {"config": config, "env": "dev"}
    frame = _Frame()

    io.write_lakehouse_table(frame, "metadata_orders", target="metadata", schema=None, mode="overwrite", options={"overwriteSchema": "true"}, verbose=False, context=context)

    expected_path = "abfss://dev-metadata-workspace@onelake.dfs.fabric.microsoft.com/dev-metadata-item/Tables/metadata_orders"
    assert ("mode", "overwrite") in frame.write.calls
    assert ("format", "delta") in frame.write.calls
    assert ("save", expected_path) in frame.write.calls
    assert not any(call[0] == "saveAsTable" for call in frame.write.calls)


def test_lakehouse_file_readers_build_configured_files_paths():
    """Verify lakehouse file readers build configured files paths."""
    config = _io_config()
    context = {"config": config, "env": "dev"}
    spark = _Spark()

    io.read_lakehouse_csv("Files/raw/orders.csv", target="source", spark_session=spark, context=context)
    io.read_lakehouse_parquet("curated/orders.parquet", target="unified", spark_session=spark, verbose=False, context=context)

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
    context = {"config": config, "env": "dev"}

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
    read_result = io.read_warehouse_table("dbo", "orders", target="warehouse", spark_session=spark, context=context)
    io.write_warehouse_table(frame, "dbo", "orders", target="warehouse", mode="overwrite", context=context)

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
    defined_classes = {node.name for node in tree.body if isinstance(node, ast.ClassDef)}
    referenced_names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}

    assert DELETED_INTERNAL_HELPERS.isdisjoint(defined_functions)
    assert DELETED_INTERNAL_CLASSES.isdisjoint(defined_classes)
    assert DELETED_INTERNAL_HELPERS.isdisjoint(referenced_names)
    assert DELETED_INTERNAL_CLASSES.isdisjoint(referenced_names)


def test_explicit_io_callables_are_root_exports():
    """Verify explicit IO callables are root exports."""
    import fabricops_kit

    for helper_name in PUBLIC_IO_CALLABLES:
        assert helper_name in fabricops_kit.__all__
        assert callable(getattr(fabricops_kit, helper_name))
        assert callable(getattr(io, helper_name))


def test_lakehouse_table_read_with_explicit_schema_uses_schema_physical_path():
    """Verify lakehouse table read with explicit schema uses schema physical path."""
    config = _io_config()
    context = {"config": config, "env": "dev"}
    spark = _Spark()

    io.read_lakehouse_table("METADATA_GUARDRAIL_RULES", target="metadata", schema="METADATA", spark_session=spark, context=context)

    expected_path = "abfss://dev-metadata-workspace@onelake.dfs.fabric.microsoft.com/dev-metadata-item/Tables/METADATA/METADATA_GUARDRAIL_RULES"
    assert ("load", expected_path) in spark.read.calls
    assert spark.table_calls == []


def test_lakehouse_table_write_with_explicit_schema_uses_schema_physical_path():
    """Verify lakehouse table write with explicit schema uses schema physical path."""
    config = _io_config()
    context = {"config": config, "env": "dev"}
    frame = _Frame()

    io.write_lakehouse_table(frame, "METADATA_GUARDRAIL_RULES", target="metadata", schema="METADATA", mode="overwrite", options={"overwriteSchema": "true"}, verbose=False, context=context)

    expected_path = "abfss://dev-metadata-workspace@onelake.dfs.fabric.microsoft.com/dev-metadata-item/Tables/METADATA/METADATA_GUARDRAIL_RULES"
    assert ("save", expected_path) in frame.write.calls
    assert not any(call[0] == "saveAsTable" for call in frame.write.calls)


def test_lakehouse_schema_enabled_target_routes_paths_and_identifiers_from_config():
    """Verify lakehouse schema enabled target routes paths and identifiers from config."""
    config = _schema_io_config()
    context = {"config": config, "env": "dev"}
    spark = _Spark()
    frame = _Frame()

    io.read_lakehouse_table("orders", target="source", schema="src", spark_session=spark, context=context)
    io.write_lakehouse_table(frame, "METADATA_GUARDRAIL_RULES", target="metadata", schema="meta", mode="overwrite", options={"overwriteSchema": "true"}, verbose=False, context=context)
    metadata_store = config.paths["dev"]["metadata"]

    assert ("load", "abfss://dev-source-workspace@onelake.dfs.fabric.microsoft.com/dev-source-item/Tables/src/orders") in spark.read.calls
    assert ("save", "abfss://dev-metadata-workspace@onelake.dfs.fabric.microsoft.com/dev-metadata-item/Tables/meta/METADATA_GUARDRAIL_RULES") in frame.write.calls
    assert io._resolve_lakehouse_table_identifier(metadata_store, "METADATA_GUARDRAIL_RULES", "meta") == "meta.METADATA_GUARDRAIL_RULES"


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
        io.read_lakehouse_table("TABLE", target="metadata", schema=schema, spark_session=_Spark(), context={"config": _io_config(), "env": "dev"})


@pytest.mark.parametrize("table", ["schema.table", "bad/name", "bad-name", "1TABLE", ""])
def test_lakehouse_table_validation_rejects_unsafe_names(table):
    """Verify lakehouse table validation rejects unsafe names."""
    with pytest.raises(ValueError):
        io.read_lakehouse_table(table, target="metadata", schema=None, spark_session=_Spark(), context={"config": _io_config(), "env": "dev"})


def test_read_lakehouse_table_defaults_to_active_context(monkeypatch):
    """Verify lakehouse reads can default to the active Fabric context."""
    import builtins

    monkeypatch.setattr(builtins, "FABRIC_CONTEXT", {"config": _io_config(), "env": "dev"}, raising=False)
    spark = _Spark()

    io.read_lakehouse_table("orders", spark_session=spark)

    expected_path = "abfss://dev-source-workspace@onelake.dfs.fabric.microsoft.com/dev-source-item/Tables/orders"
    assert ("load", expected_path) in spark.read.calls


def test_write_lakehouse_table_defaults_to_active_context(monkeypatch):
    """Verify lakehouse writes can default to the active Fabric context."""
    import builtins

    monkeypatch.setattr(builtins, "FABRIC_CONTEXT", {"config": _io_config(), "env": "dev"}, raising=False)
    frame = _Frame()

    io.write_lakehouse_table(frame, "orders_clean", mode="overwrite", verbose=False)

    expected_path = "abfss://dev-unified-workspace@onelake.dfs.fabric.microsoft.com/dev-unified-item/Tables/orders_clean"
    assert ("save", expected_path) in frame.write.calls


def test_missing_active_context_has_clear_error(monkeypatch):
    """Verify missing 00_env_config state raises a clear action message."""
    import builtins
    import pytest

    monkeypatch.delattr(builtins, "FABRIC_CONTEXT", raising=False)

    with pytest.raises(RuntimeError, match="Please run 00_env_config"):
        io.read_lakehouse_table("orders", spark_session=_Spark())


def test_read_warehouse_query_validates_and_uses_connector(monkeypatch):
    """Verify warehouse query pushdown validates SQL and builds connector calls."""
    config = _io_config()
    context = {"config": config, "env": "dev"}

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
    result = io.read_warehouse_query("SELECT order_id FROM dbo.orders WHERE status = 'OPEN'", target="warehouse", spark_session=spark, context=context)

    assert result == {"synapsesql": "SELECT order_id FROM dbo.orders WHERE status = 'OPEN'"}
    assert ("option", "workspace_id", "dev-warehouse-workspace") in spark.read.calls
    assert ("option", "datawarehouse_id", "dev-warehouse-item") in spark.read.calls

    with pytest.raises(ValueError, match="non-empty SQL SELECT"):
        io.read_warehouse_query("", target="warehouse", spark_session=spark, context=context)
    with pytest.raises(ValueError, match="SELECT statement"):
        io.read_warehouse_query("DELETE FROM dbo.orders", target="warehouse", spark_session=spark, context=context)


def test_fabric_io_architecture_call_boundaries():
    """Verify Fabric IO public, core, and utility call boundaries."""
    source = Path("src/fabricops_kit/fabric_input_output.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    public = {
        "read_lakehouse_table",
        "write_lakehouse_table",
        "read_lakehouse_csv",
        "read_lakehouse_parquet",
        "read_lakehouse_excel",
        "read_warehouse_table",
        "read_warehouse_query",
        "write_warehouse_table",
    }
    internal = {name for name in functions if name.startswith("_read_") or name.startswith("_write_")}
    utility = {
        "_get_spark",
        "_normalize_table_name",
        "_normalize_schema_name",
        "_normalize_write_mode",
        "_resolve_lakehouse_table_path",
        "_resolve_lakehouse_table_identifier",
        "_lakehouse_file_path",
        "_validate_lakehouse_store",
        "_validate_warehouse_store",
        "_validate_relative_path",
        "_require_fabric_connector",
        "_build_warehouse_object_name",
        "_convert_single_parquet_ns_to_us",
    }
    fabricops_callables = public | internal | utility

    def calls(node):
        return {call.func.id for call in ast.walk(node) if isinstance(call, ast.Call) and isinstance(call.func, ast.Name)}

    for name in public:
        assert calls(functions[name]).isdisjoint(public - {name})
    for name in internal:
        assert calls(functions[name]).isdisjoint(public)
        assert calls(functions[name]).isdisjoint(internal - {name})
    for name in utility:
        assert calls(functions[name]).isdisjoint(fabricops_callables - {name})
