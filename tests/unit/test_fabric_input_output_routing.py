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


def test_read_lakehouse_csv_preserves_signature_and_reader_options():
    """Verify read_lakehouse_csv keeps its public contract and Spark CSV behavior."""
    import inspect

    from fabricops_kit.io.read_lakehouse_csv import read_lakehouse_csv

    config = _io_config()
    context = {"config": config, "env": "dev"}
    spark = _Spark()

    result = read_lakehouse_csv(
        "Files/raw/orders.csv",
        target="source",
        spark_session=spark,
        header=False,
        context=context,
        delimiter="|",
        inferSchema=True,
    )

    assert inspect.signature(read_lakehouse_csv) == inspect.signature(io.read_lakehouse_csv)
    assert result == {"path": "abfss://dev-source-workspace@onelake.dfs.fabric.microsoft.com/dev-source-item/Files/raw/orders.csv"}
    assert ("option", "header", False) in spark.read.calls
    assert ("option", "delimiter", "|") in spark.read.calls
    assert ("option", "inferSchema", True) in spark.read.calls
    assert ("csv", "abfss://dev-source-workspace@onelake.dfs.fabric.microsoft.com/dev-source-item/Files/raw/orders.csv") in spark.read.calls


def test_configured_file_path_resolution_normalizes_files_prefix():
    """Verify configured file path resolution keeps existing Files-prefix behavior."""
    from fabricops_kit.io.shared import resolve_configured_file_path

    config = _io_config()
    store, normalized, path = resolve_configured_file_path(
        "source",
        "/Files/raw/orders.csv",
        context={"config": config, "env": "dev"},
    )

    assert store.name == "lh_source_dev"
    assert normalized == "raw/orders.csv"
    assert path == "abfss://dev-source-workspace@onelake.dfs.fabric.microsoft.com/dev-source-item/Files/raw/orders.csv"


def test_csv_path_reader_uses_spark_csv_adapter_options():
    """Verify CSV path reading remains a thin Spark reader adapter."""
    from fabricops_kit.io.shared import read_csv_path

    spark = _Spark()
    result = read_csv_path(spark, "abfss://workspace/item/Files/raw/orders.csv", header=True, options={"sep": ",", "quote": '"'})

    assert result == {"path": "abfss://workspace/item/Files/raw/orders.csv"}
    assert spark.read.calls == [
        ("option", "header", True),
        ("option", "sep", ","),
        ("option", "quote", '"'),
        ("csv", "abfss://workspace/item/Files/raw/orders.csv"),
    ]


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

    from fabricops_kit.io.shared import resolve_lakehouse_table_location

    _table, _schema, path = resolve_lakehouse_table_location(metadata_store, "orders", None)
    assert path.endswith("/Tables/orders")
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




def test_public_io_functions_delegate_to_configured_resolver_boundaries(monkeypatch):
    """Verify public IO functions use the shared configured resolver boundaries."""
    from fabricops_kit.io_core import FabricStore
    import importlib

    csv_owner = importlib.import_module("fabricops_kit.io.read_lakehouse_csv")
    excel_owner = importlib.import_module("fabricops_kit.io.read_lakehouse_excel")
    parquet_owner = importlib.import_module("fabricops_kit.io.read_lakehouse_parquet")
    lakehouse_read_owner = importlib.import_module("fabricops_kit.io.read_lakehouse_table")
    lakehouse_write_owner = importlib.import_module("fabricops_kit.io.write_lakehouse_table")
    warehouse_query_owner = importlib.import_module("fabricops_kit.io.read_warehouse_query")
    warehouse_read_owner = importlib.import_module("fabricops_kit.io.read_warehouse_table")
    warehouse_write_owner = importlib.import_module("fabricops_kit.io.write_warehouse_table")

    calls = []
    store = FabricStore(env="dev", workspace_id="workspace", item_id="item", name="warehouse", kind="warehouse")
    lakehouse_store = FabricStore(env="dev", workspace_id="workspace", item_id="item", name="lakehouse", kind="lakehouse")

    monkeypatch.setattr(csv_owner, "resolve_configured_file_path", lambda target, relative_path, *, context=None: calls.append(("file", target, relative_path, context)) or (lakehouse_store, relative_path, "resolved://csv"))
    monkeypatch.setattr(csv_owner, "read_csv_path", lambda spark, path, *, header, options: calls.append(("csv_reader", path, header, options)) or "csv")
    assert csv_owner.read_lakehouse_csv("raw/orders.csv", target="custom", spark_session=object(), context={"sentinel": True}, header=False, delimiter="|") == "csv"

    monkeypatch.setattr(excel_owner, "resolve_configured_file_path", lambda target, relative_path, *, context=None: calls.append(("file", target, relative_path, context)) or (lakehouse_store, relative_path, "resolved://excel"))
    monkeypatch.setattr(excel_owner, "read_excel_file", lambda spark, path, *, sheet_name, read_excel_kwargs: calls.append(("excel_reader", path, sheet_name, read_excel_kwargs)) or "excel")
    assert excel_owner.read_lakehouse_excel("raw/orders.xlsx", target="custom", spark_session=object(), context={"sentinel": True}, sheet_name="S") == "excel"

    class ParquetFrame:
        def limit(self, _count):
            return self

        def collect(self):
            return []

    class ParquetReader:
        def parquet(self, path):
            calls.append(("parquet_reader", path))
            return ParquetFrame()

    class ParquetSpark:
        read = ParquetReader()

    monkeypatch.setattr(parquet_owner, "resolve_configured_file_path", lambda target, relative_path, *, context=None: calls.append(("file", target, relative_path, context)) or (lakehouse_store, "raw/orders.parquet", "resolved://parquet"))
    assert isinstance(parquet_owner.read_lakehouse_parquet("raw/orders.parquet", target="custom", spark_session=ParquetSpark(), context={"sentinel": True}, verbose=False), ParquetFrame)

    monkeypatch.setattr(lakehouse_read_owner, "resolve_configured_lakehouse_table", lambda target, table_name, schema, *, context=None: calls.append(("lakehouse_table", target, table_name, schema, context)) or (lakehouse_store, table_name, schema, "resolved://table"))
    monkeypatch.setattr(lakehouse_read_owner, "read_delta_path", lambda spark, path: calls.append(("read_delta", path)) or "lakehouse_read")
    assert lakehouse_read_owner.read_lakehouse_table("orders", target="custom", schema="dbo", spark_session=object(), context={"sentinel": True}) == "lakehouse_read"

    frame = _Frame()
    monkeypatch.setattr(lakehouse_write_owner, "resolve_configured_lakehouse_table", lambda target, table_name, schema, *, context=None: calls.append(("lakehouse_table", target, table_name, schema, context)) or (lakehouse_store, table_name, schema, "resolved://write_table"))
    monkeypatch.setattr(lakehouse_write_owner, "write_delta_path", lambda df, path, *, mode, partition_by=None, options=None: calls.append(("write_delta", path, mode, partition_by, options)))
    lakehouse_write_owner.write_lakehouse_table(frame, "orders", target="custom", schema="dbo", mode="overwrite", verbose=False, context={"sentinel": True})

    monkeypatch.setattr(warehouse_query_owner, "resolve_configured_warehouse_query_target", lambda target, *, context=None: calls.append(("warehouse_query", target, context)) or store)
    monkeypatch.setattr(warehouse_query_owner, "read_warehouse_synapsesql", lambda spark, store, sql: calls.append(("warehouse_sql", store.name, sql)) or "query")
    assert warehouse_query_owner.read_warehouse_query("SELECT 1", target="custom", spark_session=object(), context={"sentinel": True}) == "query"

    monkeypatch.setattr(warehouse_read_owner, "resolve_configured_warehouse_table", lambda target, schema, table_name, *, context=None: calls.append(("warehouse_table", target, schema, table_name, context)) or (store, schema, table_name, "warehouse.dbo.orders"))
    monkeypatch.setattr(warehouse_read_owner, "read_warehouse_synapsesql", lambda spark, store, sql: calls.append(("warehouse_read", store.name, sql)) or "warehouse_read")
    assert warehouse_read_owner.read_warehouse_table("dbo", "orders", target="custom", spark_session=object(), context={"sentinel": True}) == "warehouse_read"

    monkeypatch.setattr(warehouse_write_owner, "resolve_configured_warehouse_table", lambda target, schema, table_name, *, context=None: calls.append(("warehouse_table", target, schema, table_name, context)) or (store, schema, table_name, "warehouse.dbo.orders"))
    monkeypatch.setattr(warehouse_write_owner, "write_warehouse_synapsesql", lambda df, store, sql, *, mode: calls.append(("warehouse_write", store.name, sql, mode)))
    warehouse_write_owner.write_warehouse_table(frame, "dbo", "orders", target="custom", mode="overwrite", context={"sentinel": True})

    assert ("csv_reader", "resolved://csv", False, {"delimiter": "|"}) in calls
    assert ("excel_reader", "resolved://excel", "S", {}) in calls
    assert ("parquet_reader", "resolved://parquet") in calls
    assert ("read_delta", "resolved://table") in calls
    assert ("write_delta", "resolved://write_table", "overwrite", None, None) in calls
    assert ("warehouse_query", "custom", {"sentinel": True}) in calls
    assert ("warehouse_read", "warehouse", "warehouse.dbo.orders") in calls
    assert ("warehouse_write", "warehouse", "warehouse.dbo.orders", "overwrite") in calls


def test_public_io_owner_files_do_not_duplicate_stale_resolver_patterns():
    """Verify public IO owner files avoid stale low-level resolver duplication."""
    stale_patterns = (
        'resolve_target_store(target, "lakehouse"',
        'resolve_target_store(target, "warehouse"',
        "resolve_lakehouse_file_location",
        '"/Tables/"',
        '"/Files/"',
        'f"Files/',
        'f"Tables/',
    )
    owner_dir = Path("src/fabricops_kit/io")
    for helper_name in PUBLIC_IO_CALLABLES:
        source = (owner_dir / f"{helper_name}.py").read_text(encoding="utf-8")
        for pattern in stale_patterns:
            assert pattern not in source


def test_public_io_functions_allow_shared_resolvers_to_handle_configured_target(monkeypatch):
    """Verify public functions do not reject logical targets before shared resolution."""
    import importlib

    lakehouse_read_owner = importlib.import_module("fabricops_kit.io.read_lakehouse_table")

    monkeypatch.setattr(lakehouse_read_owner, "resolve_configured_lakehouse_table", lambda target, table_name, schema, *, context=None: (_store(target, "lakehouse", "lh"), table_name, schema, "resolved://table"))
    monkeypatch.setattr(lakehouse_read_owner, "read_delta_path", lambda spark, path: path)

    assert lakehouse_read_owner.read_lakehouse_table("orders", target="configured_alias", spark_session=object()) == "resolved://table"


def test_migrated_io_public_import_paths_remain_stable():
    """Verify migrated IO public functions remain importable from stable paths."""
    import fabricops_kit
    import fabricops_kit.io as owner_package
    import fabricops_kit.fabric_input_output as facade

    for helper_name in PUBLIC_IO_CALLABLES:
        root_func = getattr(fabricops_kit, helper_name)
        facade_func = getattr(facade, helper_name)
        owner_func = getattr(owner_package, helper_name)
        assert root_func is owner_func
        assert facade_func is owner_func


def test_migrated_io_owner_files_have_exactly_one_public_function():
    """Verify every migrated IO owner file defines exactly one public function."""
    owner_dir = Path("src/fabricops_kit/io")
    for helper_name in PUBLIC_IO_CALLABLES:
        path = owner_dir / f"{helper_name}.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        public_defs = [node.name for node in tree.body if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")]
        assert public_defs == [helper_name]


def test_migrated_io_shared_helpers_are_non_underscore_internal_functions():
    """Verify shared IO logic is non-underscore and not one-to-one public mirrors."""
    shared_path = Path("src/fabricops_kit/io/shared.py")
    tree = ast.parse(shared_path.read_text(encoding="utf-8"))
    shared_defs = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]

    for helper_name in PUBLIC_IO_CALLABLES:
        assert f"{helper_name}_shared" not in shared_defs
    shared_internal_defs = [name for name in shared_defs if not name.startswith("_")]
    assert {
        "get_spark_session",
        "read_csv_path",
        "resolve_target_store",
        "resolve_lakehouse_table_location",
        "resolve_lakehouse_file_location",
        "read_warehouse_synapsesql",
        "write_warehouse_synapsesql",
    }.issubset(shared_internal_defs)
    source = shared_path.read_text(encoding="utf-8")
    assert "read_csv_path as read_csv_path_core" not in source
    assert "get_spark," not in source
    assert "reader.csv(path)" in source
    imported_private_io_core_helpers = [
        alias.name
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module in {"..io_core", "fabricops_kit.io_core"}
        for alias in node.names
        if alias.name.startswith("_")
    ]
    assert imported_private_io_core_helpers == []


def test_io_core_keeps_only_metadata_core_and_supported_store_helpers():
    """Verify io_core has no unused Fabric IO public-callable helper shims."""
    source = Path("src/fabricops_kit/io_core.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    defined_functions = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}

    assert defined_functions == {
        "_join_lakehouse_area_path",
        "_resolve_lakehouse_table_identifier",
        "_normalize_table_name",
        "_normalize_schema_name",
        "_normalize_write_mode",
        "_validate_lakehouse_store",
        "_validate_warehouse_store",
        "_validate_dataframe_writer",
        "get_spark",
        "resolve_target_store",
        "_resolve_lakehouse_schema",
        "_resolve_lakehouse_table_path",
        "_resolve_lakehouse_table_location",
        "configured_lakehouse_schema",
        "_read_delta_path",
        "_write_delta_path",
        "read_lakehouse_table_core",
        "write_lakehouse_table_core",
    }
    assert "metadata/governance" in source
    for helper_name in PUBLIC_IO_CALLABLES - {"read_lakehouse_table", "write_lakehouse_table"}:
        assert f"{helper_name}_core" not in defined_functions
    assert "read_csv_path" not in defined_functions
    assert "resolve_lakehouse_file_location" not in defined_functions


def test_callable_architecture_pattern_is_not_user_facing_docs():
    """Verify Fabric IO architecture guidance is not published as a user docs page."""
    assert not Path("docs/reference/callable-architecture.md").exists()
    assert "Callable Architecture Pattern" not in Path("mkdocs.yml").read_text(encoding="utf-8")
    assert "Fabric IO callable file pattern" in Path("AGENTS.md").read_text(encoding="utf-8")


def test_fabric_input_output_is_facade_only_after_io_migration():
    """Verify the legacy fabric_input_output module no longer owns implementations."""
    source = Path("src/fabricops_kit/fabric_input_output.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    defined_functions = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]

    assert defined_functions == []
    assert "from .io import" in source
    assert "Compatibility facade" in source


def test_migrated_io_owner_files_do_not_import_private_helpers():
    """Verify migrated IO owner files do not import cross-file private helpers."""
    owner_dir = Path("src/fabricops_kit/io")
    for helper_name in PUBLIC_IO_CALLABLES:
        tree = ast.parse((owner_dir / f"{helper_name}.py").read_text(encoding="utf-8"))
        imported_names = [alias.name for node in tree.body if isinstance(node, ast.ImportFrom) for alias in node.names]
        assert not any(name.startswith("_") for name in imported_names)
