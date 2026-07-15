"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import ast
import inspect
import sys
import types
from pathlib import Path

import pytest

from fabricops_kit.config import PathConfig
from fabricops_kit.config import FabricStore
import fabricops_kit.io as io
from tests.integration.test_storage_io import _Frame, _Spark, _Writer


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


def _store(
    target: str, kind: str, name: str, *, schema_enabled: bool = False, schema: str | None = None
) -> FabricStore:
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

        expected_path = (
            f"abfss://dev-{target}-workspace@onelake.dfs.fabric.microsoft.com/dev-{target}-item/Tables/orders"
        )
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

    io.write_lakehouse_table(
        frame,
        "metadata_orders",
        target="metadata",
        schema=None,
        mode="overwrite",
        options={"overwriteSchema": "true"},
        verbose=False,
        context=context,
    )

    expected_path = (
        "abfss://dev-metadata-workspace@onelake.dfs.fabric.microsoft.com/dev-metadata-item/Tables/metadata_orders"
    )
    assert ("mode", "overwrite") in frame.write.calls
    assert ("format", "delta") in frame.write.calls
    assert ("option", "overwriteSchema", "true") in frame.write.calls
    assert ("save", expected_path) in frame.write.calls
    assert not any(call[0] == "saveAsTable" for call in frame.write.calls)


def test_read_lakehouse_table_forwards_delta_reader_options():
    """Verify Lakehouse table reads pass options to Spark Delta reader."""
    config = _io_config()
    context = {"config": config, "env": "dev"}
    spark = _Spark()

    io.read_lakehouse_table(
        "orders",
        target="unified",
        schema=None,
        spark_session=spark,
        context=context,
        mergeSchema=True,
        timestampAsOf="2026-01-01T00:00:00Z",
    )

    expected_path = "abfss://dev-unified-workspace@onelake.dfs.fabric.microsoft.com/dev-unified-item/Tables/orders"
    assert ("format", "delta") in spark.read.calls
    assert ("option", "mergeSchema", True) in spark.read.calls
    assert ("option", "timestampAsOf", "2026-01-01T00:00:00Z") in spark.read.calls
    assert ("load", expected_path) in spark.read.calls


def test_lakehouse_file_readers_build_configured_files_paths():
    """Verify lakehouse file readers build configured files paths."""
    config = _io_config()
    context = {"config": config, "env": "dev"}
    spark = _Spark()

    io.read_lakehouse_csv("Files/raw/orders.csv", target="source", spark_session=spark, context=context)
    io.read_lakehouse_parquet(
        "curated/orders.parquet", target="unified", spark_session=spark, verbose=False, context=context
    )

    assert (
        "csv",
        "abfss://dev-source-workspace@onelake.dfs.fabric.microsoft.com/dev-source-item/Files/raw/orders.csv",
    ) in spark.read.calls
    assert (
        "parquet",
        "abfss://dev-unified-workspace@onelake.dfs.fabric.microsoft.com/dev-unified-item/Files/curated/orders.parquet",
    ) in spark.read.calls


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
    assert result == {
        "path": "abfss://dev-source-workspace@onelake.dfs.fabric.microsoft.com/dev-source-item/Files/raw/orders.csv"
    }
    assert ("option", "header", False) in spark.read.calls
    assert ("option", "delimiter", "|") in spark.read.calls
    assert ("option", "inferSchema", True) in spark.read.calls
    assert (
        "csv",
        "abfss://dev-source-workspace@onelake.dfs.fabric.microsoft.com/dev-source-item/Files/raw/orders.csv",
    ) in spark.read.calls


def test_read_lakehouse_parquet_accepts_root_and_nested_paths_with_options():
    """Verify Parquet file reads accept root and nested paths and forward options."""
    config = _io_config()
    context = {"config": config, "env": "dev"}
    root_spark = _Spark()
    nested_spark = _Spark()

    io.read_lakehouse_parquet(
        "customers.parquet",
        target="source",
        spark_session=root_spark,
        verbose=False,
        context=context,
        mergeSchema=True,
        recursiveFileLookup=True,
    )
    io.read_lakehouse_parquet(
        "input/customers.parquet",
        target="source",
        spark_session=nested_spark,
        verbose=False,
        context=context,
        mergeSchema=True,
    )

    root_path = "abfss://dev-source-workspace@onelake.dfs.fabric.microsoft.com/dev-source-item/Files/customers.parquet"
    nested_path = (
        "abfss://dev-source-workspace@onelake.dfs.fabric.microsoft.com/dev-source-item/Files/input/customers.parquet"
    )
    assert ("parquet", root_path) in root_spark.read.calls
    assert ("option", "mergeSchema", True) in root_spark.read.calls
    assert ("option", "recursiveFileLookup", True) in root_spark.read.calls
    assert ("parquet", nested_path) in nested_spark.read.calls
    assert ("option", "mergeSchema", True) in nested_spark.read.calls


def test_read_lakehouse_parquet_forwards_options_to_fallback():
    """Verify Parquet fallback reads use the same Spark reader options."""
    config = _io_config()
    context = {"config": config, "env": "dev"}

    class FallbackFrame:
        def limit(self, _count):
            return self

        def collect(self):
            return []

    class FallbackReader:
        def __init__(self):
            self.calls = []
            self.parquet_count = 0

        def option(self, key, value):
            self.calls.append(("option", key, value))
            return self

        def parquet(self, path):
            self.calls.append(("parquet", path))
            self.parquet_count += 1
            if self.parquet_count == 1:
                raise RuntimeError("timestamp precision failure")
            return FallbackFrame()

    class FallbackSpark:
        def __init__(self):
            self.read = FallbackReader()

    spark = FallbackSpark()

    result = io.read_lakehouse_parquet(
        "customers.parquet",
        target="source",
        spark_session=spark,
        verbose=False,
        context=context,
        mergeSchema=True,
    )

    assert isinstance(result, FallbackFrame)
    assert (
        "parquet",
        "abfss://dev-source-workspace@onelake.dfs.fabric.microsoft.com/dev-source-item/Files/customers.parquet",
    ) in spark.read.calls
    assert (
        "parquet",
        "abfss://dev-source-workspace@onelake.dfs.fabric.microsoft.com/dev-source-item/Files/customers_tsus.parquet",
    ) in spark.read.calls
    assert spark.read.calls.count(("option", "mergeSchema", True)) == 2


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
    result = read_csv_path(
        spark, "abfss://workspace/item/Files/raw/orders.csv", header=True, options={"sep": ",", "quote": '"'}
    )

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
        DatabaseName = "database_name"

    constants_module = types.ModuleType("com.microsoft.spark.fabric.Constants")
    constants_module.Constants = Constants
    monkeypatch.setitem(sys.modules, "com", types.ModuleType("com"))
    monkeypatch.setitem(sys.modules, "com.microsoft", types.ModuleType("com.microsoft"))
    monkeypatch.setitem(sys.modules, "com.microsoft.spark", types.ModuleType("com.microsoft.spark"))
    monkeypatch.setitem(sys.modules, "com.microsoft.spark.fabric", types.ModuleType("com.microsoft.spark.fabric"))
    monkeypatch.setitem(sys.modules, "com.microsoft.spark.fabric.Constants", constants_module)

    spark = _Spark()
    frame = _Frame()
    read_result = io.read_warehouse_table(
        "dbo",
        "orders",
        target="warehouse",
        spark_session=spark,
        context=context,
        queryTimeout="60",
    )
    io.write_warehouse_table(
        frame,
        "dbo",
        "orders",
        target="warehouse",
        mode="overwrite",
        options={"batchsize": "5000"},
        context=context,
    )

    assert read_result == {"synapsesql": "wh_product_dev.dbo.orders"}
    assert ("option", "workspace_id", "dev-warehouse-workspace") in spark.read.calls
    assert ("option", "datawarehouse_id", "dev-warehouse-item") in spark.read.calls
    assert ("option", "database_name", "wh_product_dev") in spark.read.calls
    assert ("option", "queryTimeout", "60") in spark.read.calls
    assert ("mode", "overwrite") in frame.write.calls
    assert ("option", "workspace_id", "dev-warehouse-workspace") in frame.write.calls
    assert ("option", "datawarehouse_id", "dev-warehouse-item") in frame.write.calls
    assert ("option", "batchsize", "5000") in frame.write.calls
    assert ("synapsesql", "wh_product_dev.dbo.orders") in frame.write.calls
    assert not any(call[0] == "saveAsTable" for call in frame.write.calls)
    assert spark.table_calls == []


class _WarehouseRepartitionFrame:
    """Track Warehouse write repartition behavior."""

    def __init__(self, name: str = "original", repartitioned=None):
        self.name = name
        self.repartitioned = repartitioned
        self.repartition_calls = []
        self.write = _Writer()

    def repartition(self, *partitions):
        """Return the configured repartitioned frame."""
        self.repartition_calls.append(partitions)
        return self.repartitioned


def test_write_warehouse_table_repartition_none_preserves_original_frame(monkeypatch):
    """Verify Warehouse writes skip repartitioning when repartition is None."""
    import importlib

    warehouse_write_owner = importlib.import_module("fabricops_kit.io.write_warehouse_table")
    original = _WarehouseRepartitionFrame()
    written = []
    store = _store("warehouse", "warehouse", "wh_product_dev")

    monkeypatch.setattr(
        warehouse_write_owner,
        "resolve_configured_warehouse_table",
        lambda target, schema, table_name, *, context=None: (store, schema, table_name, "wh_product_dev.dbo.orders"),
    )
    monkeypatch.setattr(
        warehouse_write_owner,
        "write_warehouse_synapsesql",
        lambda df, store, sql, *, mode, options=None: written.append((df, store, sql, mode, options)),
    )

    warehouse_write_owner.write_warehouse_table(
        original,
        "dbo",
        "orders",
        target="warehouse",
        mode="overwrite",
        options={"batchsize": "5000"},
        context={"sentinel": True},
    )

    assert original.repartition_calls == []
    assert written == [(original, store, "wh_product_dev.dbo.orders", "overwrite", {"batchsize": "5000"})]


@pytest.mark.parametrize(
    ("repartition_by", "expected_repartition_call"),
    [
        (8, (8,)),
        ("academic_year", ("academic_year",)),
        (["academic_year", "faculty"], ("academic_year", "faculty")),
        (("academic_year", "faculty"), ("academic_year", "faculty")),
    ],
)
def test_write_warehouse_table_repartition_by_parity_writes_repartitioned_frame(
    monkeypatch, repartition_by, expected_repartition_call
):
    """Verify Warehouse writes mirror Lakehouse repartition_by handling."""
    import importlib

    warehouse_write_owner = importlib.import_module("fabricops_kit.io.write_warehouse_table")
    repartitioned = _WarehouseRepartitionFrame("repartitioned")
    original = _WarehouseRepartitionFrame(repartitioned=repartitioned)
    written = []
    store = _store("warehouse", "warehouse", "wh_product_dev")

    monkeypatch.setattr(
        warehouse_write_owner,
        "resolve_configured_warehouse_table",
        lambda target, schema, table_name, *, context=None: (store, schema, table_name, "wh_product_dev.dbo.orders"),
    )
    monkeypatch.setattr(
        warehouse_write_owner,
        "write_warehouse_synapsesql",
        lambda df, store, sql, *, mode, options=None: written.append((df, store, sql, mode, options)),
    )

    warehouse_write_owner.write_warehouse_table(
        original,
        "dbo",
        "orders",
        target="product",
        mode="overwrite",
        repartition_by=repartition_by,
        options={"batchsize": "5000"},
        context={"sentinel": True},
    )

    assert original.repartition_calls == [expected_repartition_call]
    assert written == [(repartitioned, store, "wh_product_dev.dbo.orders", "overwrite", {"batchsize": "5000"})]


def test_write_lakehouse_table_docstring_examples_cover_small_and_large_writes():
    """Verify Lakehouse help text distinguishes Spark repartitioning and Delta partitioning."""
    from fabricops_kit.io.write_lakehouse_table import write_lakehouse_table

    doc = inspect.getdoc(write_lakehouse_table)

    assert doc is not None
    assert "COUNTRY_REGION_MAPPING" in doc
    assert "millions of rows" in doc
    assert "repartition_by=32" in doc
    assert 'repartition_by=["academic_year", "semester"]' in doc
    assert 'partition_by=["academic_year"]' in doc
    assert "df.repartition(number)" in doc
    assert "df.repartition(*columns)" in doc


def test_write_warehouse_table_docstring_examples_cover_small_and_large_writes():
    """Verify Warehouse help text documents Spark repartitioning without physical partitions."""
    from fabricops_kit.io.write_warehouse_table import write_warehouse_table

    doc = inspect.getdoc(write_warehouse_table)
    normalized = " ".join(doc.split()) if doc else ""

    assert doc is not None
    assert "DIM_DEPARTMENT" in doc
    assert "millions of rows" in doc
    assert "repartition_by=32" in doc
    assert "df.repartition(number)" in doc
    assert "df.repartition(*columns)" in doc
    assert "does not create physical Warehouse table partitions" in normalized


def test_legacy_io_facade_module_is_deleted():
    """Verify the legacy IO facade file is deleted."""
    assert not (Path("src/fabricops_kit") / ("fabric_input_" + "output.py")).exists()


def test_explicit_io_callables_are_public_exports_with_stable_signatures():
    """Verify IO callables stay importable from root and IO package exports."""
    import importlib

    import fabricops_kit

    for helper_name in PUBLIC_IO_CALLABLES:
        owner_module = importlib.import_module(f"fabricops_kit.io.{helper_name}")
        owner_callable = getattr(owner_module, helper_name)
        root_callable = getattr(fabricops_kit, helper_name)
        io_callable = getattr(io, helper_name)

        assert helper_name in fabricops_kit.__all__
        assert helper_name in io.__all__
        assert callable(root_callable)
        assert callable(io_callable)
        assert inspect.signature(root_callable) == inspect.signature(owner_callable)
        assert inspect.signature(io_callable) == inspect.signature(owner_callable)


def test_lakehouse_table_read_with_explicit_schema_uses_schema_physical_path():
    """Verify lakehouse table read with explicit schema uses schema physical path."""
    config = _io_config()
    context = {"config": config, "env": "dev"}
    spark = _Spark()

    io.read_lakehouse_table(
        "METADATA_GUARDRAIL", target="metadata", schema="METADATA", spark_session=spark, context=context
    )

    expected_path = "abfss://dev-metadata-workspace@onelake.dfs.fabric.microsoft.com/dev-metadata-item/Tables/METADATA/METADATA_GUARDRAIL"
    assert ("load", expected_path) in spark.read.calls
    assert spark.table_calls == []


def test_lakehouse_table_write_with_explicit_schema_uses_schema_physical_path():
    """Verify lakehouse table write with explicit schema uses schema physical path."""
    config = _io_config()
    context = {"config": config, "env": "dev"}
    frame = _Frame()

    io.write_lakehouse_table(
        frame,
        "METADATA_GUARDRAIL",
        target="metadata",
        schema="METADATA",
        mode="overwrite",
        options={"overwriteSchema": "true"},
        verbose=False,
        context=context,
    )

    expected_path = "abfss://dev-metadata-workspace@onelake.dfs.fabric.microsoft.com/dev-metadata-item/Tables/METADATA/METADATA_GUARDRAIL"
    assert ("save", expected_path) in frame.write.calls
    assert not any(call[0] == "saveAsTable" for call in frame.write.calls)


def test_lakehouse_schema_enabled_target_routes_paths_and_identifiers_from_config():
    """Verify lakehouse schema enabled target routes paths and identifiers from config."""
    config = _schema_io_config()
    context = {"config": config, "env": "dev"}
    spark = _Spark()
    frame = _Frame()

    io.read_lakehouse_table("orders", target="source", schema="src", spark_session=spark, context=context)
    io.write_lakehouse_table(
        frame,
        "METADATA_GUARDRAIL",
        target="metadata",
        schema="meta",
        mode="overwrite",
        options={"overwriteSchema": "true"},
        verbose=False,
        context=context,
    )
    metadata_store = config.paths["dev"]["metadata"]

    assert (
        "load",
        "abfss://dev-source-workspace@onelake.dfs.fabric.microsoft.com/dev-source-item/Tables/src/orders",
    ) in spark.read.calls
    assert (
        "save",
        "abfss://dev-metadata-workspace@onelake.dfs.fabric.microsoft.com/dev-metadata-item/Tables/meta/METADATA_GUARDRAIL",
    ) in frame.write.calls
    from fabricops_kit.io.shared import _resolve_lakehouse_table_identifier

    assert (
        _resolve_lakehouse_table_identifier(metadata_store, "METADATA_GUARDRAIL", "meta")
        == "meta.METADATA_GUARDRAIL"
    )


def test_lakehouse_schema_disabled_target_routes_legacy_paths_and_identifiers():
    """Verify lakehouse schema disabled target routes legacy paths and identifiers."""
    config = _io_config()
    metadata_store = config.paths["dev"]["metadata"]

    from fabricops_kit.io.shared import resolve_lakehouse_table_location

    _table, _schema, path = resolve_lakehouse_table_location(metadata_store, "orders", None)
    assert path.endswith("/Tables/orders")
    from fabricops_kit.io.shared import _resolve_lakehouse_table_identifier

    assert _resolve_lakehouse_table_identifier(metadata_store, "orders") == "orders"


@pytest.mark.parametrize("schema", ["", "bad-name", "METADATA.TABLE", "META/DATA", "1META"])
def test_lakehouse_table_schema_validation_rejects_unsafe_names(schema):
    """Verify lakehouse table schema validation rejects unsafe names."""
    with pytest.raises(ValueError):
        io.read_lakehouse_table(
            "TABLE",
            target="metadata",
            schema=schema,
            spark_session=_Spark(),
            context={"config": _io_config(), "env": "dev"},
        )


@pytest.mark.parametrize("table", ["schema.table", "bad/name", "bad-name", "1TABLE", ""])
def test_lakehouse_table_validation_rejects_unsafe_names(table):
    """Verify lakehouse table validation rejects unsafe names."""
    with pytest.raises(ValueError):
        io.read_lakehouse_table(
            table,
            target="metadata",
            schema=None,
            spark_session=_Spark(),
            context={"config": _io_config(), "env": "dev"},
        )


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

    expected_path = (
        "abfss://dev-unified-workspace@onelake.dfs.fabric.microsoft.com/dev-unified-item/Tables/orders_clean"
    )
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
        DatabaseName = "database_name"

    constants_module = types.ModuleType("com.microsoft.spark.fabric.Constants")
    constants_module.Constants = Constants
    monkeypatch.setitem(sys.modules, "com", types.ModuleType("com"))
    monkeypatch.setitem(sys.modules, "com.microsoft", types.ModuleType("com.microsoft"))
    monkeypatch.setitem(sys.modules, "com.microsoft.spark", types.ModuleType("com.microsoft.spark"))
    monkeypatch.setitem(sys.modules, "com.microsoft.spark.fabric", types.ModuleType("com.microsoft.spark.fabric"))
    monkeypatch.setitem(sys.modules, "com.microsoft.spark.fabric.Constants", constants_module)

    spark = _Spark()
    result = io.read_warehouse_query(
        "SELECT order_id FROM dbo.orders WHERE status = 'OPEN'",
        target="warehouse",
        spark_session=spark,
        context=context,
        queryTimeout="60",
    )

    assert result == {"synapsesql": "SELECT order_id FROM dbo.orders WHERE status = 'OPEN'"}
    assert ("option", "workspace_id", "dev-warehouse-workspace") in spark.read.calls
    assert ("option", "datawarehouse_id", "dev-warehouse-item") in spark.read.calls
    assert ("option", "database_name", "wh_product_dev") in spark.read.calls
    assert ("option", "queryTimeout", "60") in spark.read.calls

    with pytest.raises(ValueError, match="non-empty SQL SELECT"):
        io.read_warehouse_query("", target="warehouse", spark_session=spark, context=context)
    with pytest.raises(ValueError, match="SELECT statement"):
        io.read_warehouse_query("DELETE FROM dbo.orders", target="warehouse", spark_session=spark, context=context)


def test_public_io_functions_delegate_to_configured_resolver_boundaries(monkeypatch):
    """Verify public IO functions use the shared configured resolver boundaries."""
    from fabricops_kit.config import FabricStore
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
    lakehouse_store = FabricStore(
        env="dev", workspace_id="workspace", item_id="item", name="lakehouse", kind="lakehouse"
    )

    monkeypatch.setattr(
        csv_owner,
        "resolve_configured_file_path",
        lambda target, relative_path, *, context=None: (
            calls.append(("file", target, relative_path, context)) or (lakehouse_store, relative_path, "resolved://csv")
        ),
    )
    monkeypatch.setattr(
        csv_owner,
        "read_csv_path",
        lambda spark, path, *, header, options: calls.append(("csv_reader", path, header, options)) or "csv",
    )
    assert (
        csv_owner.read_lakehouse_csv(
            "raw/orders.csv",
            target="custom",
            spark_session=object(),
            context={"sentinel": True},
            header=False,
            delimiter="|",
        )
        == "csv"
    )

    monkeypatch.setattr(
        excel_owner,
        "resolve_configured_file_path",
        lambda target, relative_path, *, context=None: (
            calls.append(("file", target, relative_path, context))
            or (lakehouse_store, relative_path, "resolved://excel")
        ),
    )
    monkeypatch.setattr(
        excel_owner,
        "read_excel_file",
        lambda spark, path, *, sheet_name, read_excel_kwargs: (
            calls.append(("excel_reader", path, sheet_name, read_excel_kwargs)) or "excel"
        ),
    )
    assert (
        excel_owner.read_lakehouse_excel(
            "raw/orders.xlsx", target="custom", spark_session=object(), context={"sentinel": True}, sheet_name="S"
        )
        == "excel"
    )

    class ParquetFrame:
        def limit(self, _count):
            return self

        def collect(self):
            return []

    class ParquetReader:
        def option(self, key, value):
            calls.append(("parquet_option", key, value))
            return self

        def parquet(self, path):
            calls.append(("parquet_reader", path))
            return ParquetFrame()

    class ParquetSpark:
        read = ParquetReader()

    monkeypatch.setattr(
        parquet_owner,
        "resolve_configured_file_path",
        lambda target, relative_path, *, context=None: (
            calls.append(("file", target, relative_path, context))
            or (lakehouse_store, "raw/orders.parquet", "resolved://parquet")
        ),
    )
    assert isinstance(
        parquet_owner.read_lakehouse_parquet(
            "raw/orders.parquet",
            target="custom",
            spark_session=ParquetSpark(),
            context={"sentinel": True},
            verbose=False,
            mergeSchema=True,
        ),
        ParquetFrame,
    )

    monkeypatch.setattr(
        lakehouse_read_owner,
        "resolve_configured_lakehouse_table",
        lambda target, table_name, schema, *, context=None: (
            calls.append(("lakehouse_table", target, table_name, schema, context))
            or (lakehouse_store, table_name, schema, "resolved://table")
        ),
    )
    monkeypatch.setattr(
        lakehouse_read_owner,
        "read_delta_path",
        lambda spark, path, *, options=None: calls.append(("read_delta", path, options)) or "lakehouse_read",
    )
    assert (
        lakehouse_read_owner.read_lakehouse_table(
            "orders",
            target="custom",
            schema="dbo",
            spark_session=object(),
            context={"sentinel": True},
            mergeSchema=True,
        )
        == "lakehouse_read"
    )

    frame = _Frame()
    monkeypatch.setattr(
        lakehouse_write_owner,
        "resolve_configured_lakehouse_table",
        lambda target, table_name, schema, *, context=None: (
            calls.append(("lakehouse_table", target, table_name, schema, context))
            or (lakehouse_store, table_name, schema, "resolved://write_table")
        ),
    )
    monkeypatch.setattr(
        lakehouse_write_owner,
        "write_delta_path",
        lambda df, path, *, mode, partition_by=None, options=None: calls.append(
            ("write_delta", path, mode, partition_by, options)
        ),
    )
    lakehouse_write_owner.write_lakehouse_table(
        frame, "orders", target="custom", schema="dbo", mode="overwrite", verbose=False, context={"sentinel": True}
    )

    monkeypatch.setattr(
        warehouse_query_owner,
        "resolve_configured_warehouse_query_target",
        lambda target, *, context=None: calls.append(("warehouse_query", target, context)) or store,
    )
    monkeypatch.setattr(
        warehouse_query_owner,
        "read_warehouse_synapsesql",
        lambda spark, store, sql, *, options=None: calls.append(("warehouse_sql", store.name, sql, options)) or "query",
    )
    assert (
        warehouse_query_owner.read_warehouse_query(
            "SELECT 1", target="custom", spark_session=object(), context={"sentinel": True}, queryTimeout="60"
        )
        == "query"
    )

    monkeypatch.setattr(
        warehouse_read_owner,
        "resolve_configured_warehouse_table",
        lambda target, schema, table_name, *, context=None: (
            calls.append(("warehouse_table", target, schema, table_name, context))
            or (store, schema, table_name, "warehouse.dbo.orders")
        ),
    )
    monkeypatch.setattr(
        warehouse_read_owner,
        "read_warehouse_synapsesql",
        lambda spark, store, sql, *, options=None: (
            calls.append(("warehouse_read", store.name, sql, options)) or "warehouse_read"
        ),
    )
    assert (
        warehouse_read_owner.read_warehouse_table(
            "dbo",
            "orders",
            target="custom",
            spark_session=object(),
            context={"sentinel": True},
            queryTimeout="60",
        )
        == "warehouse_read"
    )

    monkeypatch.setattr(
        warehouse_write_owner,
        "resolve_configured_warehouse_table",
        lambda target, schema, table_name, *, context=None: (
            calls.append(("warehouse_table", target, schema, table_name, context))
            or (store, schema, table_name, "warehouse.dbo.orders")
        ),
    )
    monkeypatch.setattr(
        warehouse_write_owner,
        "write_warehouse_synapsesql",
        lambda df, store, sql, *, mode, options=None: calls.append(("warehouse_write", store.name, sql, mode, options)),
    )
    warehouse_write_owner.write_warehouse_table(
        frame,
        "dbo",
        "orders",
        target="custom",
        mode="overwrite",
        options={"batchsize": "5000"},
        context={"sentinel": True},
    )

    assert ("csv_reader", "resolved://csv", False, {"delimiter": "|"}) in calls
    assert ("excel_reader", "resolved://excel", "S", {}) in calls
    assert ("parquet_option", "mergeSchema", True) in calls
    assert ("parquet_reader", "resolved://parquet") in calls
    assert ("read_delta", "resolved://table", {"mergeSchema": True}) in calls
    assert ("write_delta", "resolved://write_table", "overwrite", None, None) in calls
    assert ("warehouse_query", "custom", {"sentinel": True}) in calls
    assert ("warehouse_sql", "warehouse", "SELECT 1", {"queryTimeout": "60"}) in calls
    assert ("warehouse_read", "warehouse", "warehouse.dbo.orders", {"queryTimeout": "60"}) in calls
    assert ("warehouse_write", "warehouse", "warehouse.dbo.orders", "overwrite", {"batchsize": "5000"}) in calls


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

    monkeypatch.setattr(
        lakehouse_read_owner,
        "resolve_configured_lakehouse_table",
        lambda target, table_name, schema, *, context=None: (
            _store(target, "lakehouse", "lh"),
            table_name,
            schema,
            "resolved://table",
        ),
    )
    monkeypatch.setattr(lakehouse_read_owner, "read_delta_path", lambda spark, path, *, options=None: path)

    assert (
        lakehouse_read_owner.read_lakehouse_table("orders", target="configured_alias", spark_session=object())
        == "resolved://table"
    )


def test_migrated_io_public_import_paths_remain_stable():
    """Verify migrated IO public functions remain importable from stable paths."""
    import fabricops_kit
    import fabricops_kit.io as owner_package
    import fabricops_kit as facade

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
        public_defs = [
            node.name for node in tree.body if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
        ]
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


def test_io_core_module_is_deleted_after_fabric_io_shared_migration():
    """Verify no wrapper-on-wrapper IO core module remains after migration."""
    assert not Path("src/fabricops_kit/io_core.py").exists()


def test_no_source_imports_io_core_after_shared_migration():
    """Verify source files import IO helpers from their real owner modules."""
    offenders = []
    for path in Path("src/fabricops_kit").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and "io_core" in node.module:
                offenders.append(f"{path}:{node.lineno}:{node.module}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if "io_core" in alias.name:
                        offenders.append(f"{path}:{node.lineno}:{alias.name}")
    assert offenders == []


def test_callable_architecture_pattern_is_not_user_facing_docs():
    """Verify Fabric IO architecture guidance is not published as a user docs page."""
    assert not Path("docs/reference/callable-architecture.md").exists()
    assert "callable-architecture.md" not in Path("mkdocs.yml").read_text(encoding="utf-8")
    assert "Fabric IO callable file pattern" in Path("AGENTS.md").read_text(encoding="utf-8")


def test_no_code_imports_legacy_io_facade_module():
    """Verify code and template files do not import the deleted legacy facade."""
    roots = [Path("src"), Path("tests"), Path("templates"), Path("docs")]
    offenders = []
    for root in roots:
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".md", ".ipynb", ".json", ".yml"}:
                if "fabricops_kit." + "fabric_input_" + "output" in path.read_text(encoding="utf-8"):
                    offenders.append(str(path))
    assert offenders == []


def test_migrated_io_owner_files_do_not_import_private_helpers():
    """Verify migrated IO owner files do not import cross-file private helpers."""
    owner_dir = Path("src/fabricops_kit/io")
    for helper_name in PUBLIC_IO_CALLABLES:
        tree = ast.parse((owner_dir / f"{helper_name}.py").read_text(encoding="utf-8"))
        imported_names = [alias.name for node in tree.body if isinstance(node, ast.ImportFrom) for alias in node.names]
        assert not any(name.startswith("_") for name in imported_names)


class _TrackedFrame:
    """Minimal Spark-like DataFrame that records repartition usage."""

    def __init__(self, name="original", columns=None):
        self.name = name
        self.columns = list(columns or ["academic_year", "semester", "status"])
        self.write = _Writer()
        self.repartition_calls = []

    def repartition(self, *args):
        self.repartition_calls.append(args)
        child = _TrackedFrame(name=f"{self.name}.repartitioned", columns=self.columns)
        child.parent = self
        child.repartition_args = args
        return child


def test_write_lakehouse_table_repartition_contract(monkeypatch):
    """Verify lakehouse writes use supported repartition forms before Delta writes."""
    import importlib

    owner = importlib.import_module("fabricops_kit.io.write_lakehouse_table")
    store = _store("data", "lakehouse", "lh_data_dev")
    writes = []
    monkeypatch.setattr(
        owner,
        "resolve_configured_lakehouse_table",
        lambda target, table_name, schema, *, context=None: (store, table_name, schema, "resolved://lakehouse/table"),
    )
    monkeypatch.setattr(
        owner,
        "write_delta_path",
        lambda df, path, *, mode, partition_by=None, options=None: writes.append(
            {"df": df, "path": path, "mode": mode, "partition_by": partition_by, "options": options}
        ),
    )

    original = _TrackedFrame()
    owner.write_lakehouse_table(original, "orders", target="data", mode="overwrite", verbose=False)
    assert original.repartition_calls == []
    assert writes[-1]["df"] is original

    for repartition_by, expected in [
        (32, (32,)),
        ("academic_year", ("academic_year",)),
        (["academic_year", "semester"], ("academic_year", "semester")),
        (("academic_year", "semester"), ("academic_year", "semester")),
    ]:
        frame = _TrackedFrame()
        owner.write_lakehouse_table(
            frame,
            "orders",
            target="data",
            mode="overwrite",
            partition_by=["academic_year"],
            repartition_by=repartition_by,
            verbose=False,
        )
        assert frame.repartition_calls == [expected]
        assert writes[-1]["df"] is not frame
        assert writes[-1]["df"].repartition_args == expected
        assert writes[-1]["partition_by"] == ["academic_year"]

    frame = _TrackedFrame()
    owner.write_lakehouse_table(
        frame,
        "orders",
        target="data",
        mode="overwrite",
        partition_by=["academic_year"],
        repartition_by=32,
        verbose=False,
    )
    assert frame.repartition_calls == [(32,)]
    assert writes[-1]["partition_by"] == ["academic_year"]
    assert writes[-1]["df"].repartition_args == (32,)

    for invalid in (0, -1, [], (), {"academic_year"}, (32, "academic_year")):
        with pytest.raises(ValueError, match="repartition_by"):
            owner.write_lakehouse_table(
                _TrackedFrame(), "orders", target="data", repartition_by=invalid, verbose=False
            )
    with pytest.raises(ValueError, match="do not exist"):
        owner.write_lakehouse_table(
            _TrackedFrame(columns=["academic_year"]),
            "orders",
            target="data",
            repartition_by="missing_column",
            verbose=False,
        )


def test_write_warehouse_table_repartition_contract(monkeypatch):
    """Verify warehouse writes pass the repartitioned DataFrame to the connector."""
    import importlib

    owner = importlib.import_module("fabricops_kit.io.write_warehouse_table")
    store = _store("warehouse", "warehouse", "wh_data_dev")
    writes = []
    monkeypatch.setattr(
        owner,
        "resolve_configured_warehouse_table",
        lambda target, schema, table_name, *, context=None: (
            store,
            schema,
            table_name,
            f"{store.name}.{schema}.{table_name}",
        ),
    )
    monkeypatch.setattr(
        owner,
        "write_warehouse_synapsesql",
        lambda df, store, sql, *, mode, options=None: writes.append(
            {"df": df, "store": store, "sql": sql, "mode": mode, "options": options}
        ),
    )

    original = _TrackedFrame()
    owner.write_warehouse_table(original, "dbo", "orders", target="warehouse", mode="append")
    assert original.repartition_calls == []
    assert writes[-1]["df"] is original

    for repartition_by, expected in [
        (32, (32,)),
        ("academic_year", ("academic_year",)),
        (["academic_year", "semester"], ("academic_year", "semester")),
        (("academic_year", "semester"), ("academic_year", "semester")),
    ]:
        frame = _TrackedFrame()
        owner.write_warehouse_table(
            frame,
            "dbo",
            "orders",
            target="warehouse",
            mode="append",
            repartition_by=repartition_by,
            options={"batchsize": "5000"},
        )
        assert frame.repartition_calls == [expected]
        assert writes[-1]["df"] is not frame
        assert writes[-1]["df"].repartition_args == expected
        assert writes[-1]["options"] == {"batchsize": "5000"}

    for invalid in (0, -1, [], (), {"academic_year"}, (32, "academic_year")):
        with pytest.raises(ValueError, match="repartition_by"):
            owner.write_warehouse_table(_TrackedFrame(), "dbo", "orders", target="warehouse", repartition_by=invalid)
    with pytest.raises(ValueError, match="do not exist"):
        owner.write_warehouse_table(
            _TrackedFrame(columns=["academic_year"]),
            "dbo",
            "orders",
            target="warehouse",
            repartition_by="missing_column",
        )
