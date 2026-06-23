"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

import fabricops_kit.fabric_input_output as io
import fabricops_kit.io_core as io_core

from tests.helpers import framework_config

pytestmark = pytest.mark.integration


class _Reader:
    def __init__(self):
        self.calls = []

    def format(self, value):
        self.calls.append(("format", value))
        return self

    def option(self, key, value):
        self.calls.append(("option", key, value))
        return self

    def load(self, path):
        self.calls.append(("load", path))
        return SimpleNamespace(count=lambda: 1, select=lambda *args: SimpleNamespace(collect=lambda: [[b"content"]]))

    def csv(self, path):
        self.calls.append(("csv", path))
        return {"path": path}

    def parquet(self, path):
        self.calls.append(("parquet", path))
        return SimpleNamespace(limit=lambda count: SimpleNamespace(collect=lambda: []))

    def synapsesql(self, table):
        self.calls.append(("synapsesql", table))
        return {"synapsesql": table}


class _Spark:
    def __init__(self):
        self.read = _Reader()
        self.created = []
        self.table_calls = []

    def createDataFrame(self, rows):
        self.created.append(rows)
        return {"created": rows}

    def table(self, table):
        self.table_calls.append(table)
        return {"table": table}


class _Writer:
    def __init__(self):
        self.calls = []

    def mode(self, value):
        self.calls.append(("mode", value))
        return self

    def format(self, value):
        self.calls.append(("format", value))
        return self

    def option(self, key, value):
        self.calls.append(("option", key, value))
        return self

    def partitionBy(self, *columns):  # noqa: N802 - mirrors Spark API
        self.calls.append(("partitionBy", columns))
        return self

    def save(self, path):
        self.calls.append(("save", path))

    def saveAsTable(self, table):  # noqa: N802 - mirrors Spark API
        self.calls.append(("saveAsTable", table))

    def synapsesql(self, table):
        self.calls.append(("synapsesql", table))


class _Frame:
    def __init__(self):
        self.write = _Writer()

    def repartition(self, *args):
        self.repartition_args = args
        return self


def test_lakehouse_read_and_write_helpers_route_to_configured_paths():
    """Verify lakehouse read and write helpers route to configured paths."""
    config = framework_config()
    context = {"config": config, "env": "dev"}
    spark = _Spark()
    frame = _Frame()

    io.read_lakehouse_csv("Files/raw/orders.csv", target="source", spark_session=spark, context=context)
    io.write_lakehouse_table(frame, "orders_clean", target="unified", schema=None, mode="overwrite", partition_by=["status"], options={"overwriteSchema": "true"}, verbose=False, context=context)

    csv_call = next(call for call in spark.read.calls if call[0] == "csv")
    save_call = next(call for call in frame.write.calls if call[0] == "save")
    assert csv_call[1].endswith("/Files/raw/orders.csv")
    assert save_call[1].endswith("/Tables/orders_clean")
    assert ("format", "delta") in frame.write.calls
    assert ("partitionBy", ("status",)) in frame.write.calls


def test_metadata_lakehouse_table_helpers_use_abfss_paths_without_registered_tables():
    """Verify metadata lakehouse table helpers use abfss paths without registered tables."""
    config = framework_config()
    context = {"config": config, "env": "dev"}
    spark = _Spark()
    frame = _Frame()

    read_result = io.read_lakehouse_table("METADATA_GUARDRAIL_RULES", target="metadata", schema=None, spark_session=spark, context=context)
    io.write_lakehouse_table(frame, "METADATA_GUARDRAIL_RULES", target="metadata", schema=None, mode="ignore", verbose=False, context=context)

    expected_path = "abfss://dev-workspace@onelake.dfs.fabric.microsoft.com/dev-lakehouse-item/Tables/METADATA_GUARDRAIL_RULES"
    assert read_result.count() == 1
    assert spark.table_calls == []
    assert ("load", expected_path) in spark.read.calls
    assert ("save", expected_path) in frame.write.calls
    assert not any(call[0] == "saveAsTable" for call in frame.write.calls)
    assert not any(call[0] == "save" and "Unidentified" in call[1] for call in frame.write.calls)


def test_lakehouse_table_helpers_reject_nested_table_paths():
    """Verify lakehouse table helpers reject nested table paths."""
    config = framework_config()
    context = {"config": config, "env": "dev"}

    with pytest.raises(ValueError, match="simple table name"):
        io.write_lakehouse_table(_Frame(), "METADATA_GUARDRAIL_RULES/Unidentified", target="metadata", schema=None, mode="ignore", verbose=False, context=context)


def test_file_readers_validate_source_paths_and_excel_uses_pandas_kwargs(monkeypatch):
    """Verify file readers validate source paths and excel uses pandas kwargs."""
    config = framework_config()
    spark = _Spark()
    captured = {}

    monkeypatch.setattr(
        io_core,
        "_load_pandas",
        lambda: SimpleNamespace(
            read_excel=lambda path, sheet_name=0, **kwargs: captured.setdefault("kwargs", kwargs) or [{"a": 1}]
        ),
    )

    with pytest.raises(ValueError, match="relative_path"):
        io.read_lakehouse_csv("", target="source", spark_session=spark, context={"config": config, "env": "dev"})
    with pytest.raises(ValueError, match="folder/file.parquet"):
        io.read_lakehouse_parquet("orders.parquet", target="source", spark_session=spark, verbose=False, context={"config": config, "env": "dev"})

    io.read_lakehouse_excel("Files/reference/map.xlsx", target="source", sheet_name="Sheet1", spark_session=spark, context={"config": config, "env": "dev"}, skiprows=1)
    assert captured["kwargs"] == {"skiprows": 1}


def test_read_lakehouse_csv_delegates_to_get_path(monkeypatch):
    """Verify CSV reads use the configured path resolver output directly."""
    spark = _Spark()
    calls = {}

    from importlib import import_module

    csv_module = import_module("fabricops_kit.io.read_lakehouse_csv")

    def fake_get_path(relative_path, *, target="source", context=None):
        calls.update({"relative_path": relative_path, "target": target, "context": context})
        return "abfss://configured-target/custom/orders.csv"

    monkeypatch.setattr(csv_module, "get_path", fake_get_path)

    io.read_lakehouse_csv("custom/orders.csv", target="source", spark_session=spark, context={"env": "dev"})

    assert calls == {"relative_path": "custom/orders.csv", "target": "source", "context": {"env": "dev"}}
    assert ("csv", "abfss://configured-target/custom/orders.csv") in spark.read.calls


def test_read_lakehouse_excel_delegates_to_get_path(monkeypatch):
    """Verify Excel reads use the configured path resolver output directly."""
    spark = _Spark()
    calls = {}

    from importlib import import_module

    excel_module = import_module("fabricops_kit.io.read_lakehouse_excel")

    def fake_get_path(relative_path, *, target="source", context=None):
        calls.update({"relative_path": relative_path, "target": target, "context": context})
        return "abfss://configured-target/custom/input.xlsx"

    monkeypatch.setattr(excel_module, "get_path", fake_get_path)
    monkeypatch.setattr(
        io_core,
        "_load_pandas",
        lambda: SimpleNamespace(read_excel=lambda path, sheet_name=0, **kwargs: [{"sheet": sheet_name}]),
    )

    io.read_lakehouse_excel("custom/input.xlsx", target="source", sheet_name="Sheet1", spark_session=spark, context={"env": "dev"})

    assert calls == {"relative_path": "custom/input.xlsx", "target": "source", "context": {"env": "dev"}}
    assert ("load", "abfss://configured-target/custom/input.xlsx") in spark.read.calls


def test_public_file_readers_do_not_call_lakehouse_resolvers(monkeypatch):
    """Verify public file readers do not force lakehouse target resolution."""
    spark = _Spark()
    from importlib import import_module

    csv_module = import_module("fabricops_kit.io.read_lakehouse_csv")
    excel_module = import_module("fabricops_kit.io.read_lakehouse_excel")

    monkeypatch.setattr(csv_module, "get_path", lambda relative_path, *, target="source", context=None: "abfss://configured-target/custom/orders.csv")
    monkeypatch.setattr(excel_module, "get_path", lambda relative_path, *, target="source", context=None: "abfss://configured-target/custom/input.xlsx")
    monkeypatch.setattr(csv_module, "resolve_target_store", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("resolve_target_store should not be called")), raising=False)
    monkeypatch.setattr(csv_module, "resolve_lakehouse_file_location", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("resolve_lakehouse_file_location should not be called")), raising=False)
    monkeypatch.setattr(excel_module, "resolve_target_store", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("resolve_target_store should not be called")), raising=False)
    monkeypatch.setattr(excel_module, "resolve_lakehouse_file_location", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("resolve_lakehouse_file_location should not be called")), raising=False)
    monkeypatch.setattr(io_core, "_load_pandas", lambda: SimpleNamespace(read_excel=lambda path, sheet_name=0, **kwargs: [{"a": 1}]))

    io.read_lakehouse_csv("custom/orders.csv", target="warehouse", spark_session=spark, context={"env": "dev"})
    io.read_lakehouse_excel("custom/input.xlsx", target="warehouse", spark_session=spark, context={"env": "dev"})

    assert ("csv", "abfss://configured-target/custom/orders.csv") in spark.read.calls
    assert ("load", "abfss://configured-target/custom/input.xlsx") in spark.read.calls


def test_read_lakehouse_csv_accepts_non_lakehouse_configured_path_target():
    """Verify readers let get_path resolve non-lakehouse path-like targets."""
    spark = _Spark()
    config = SimpleNamespace(path_config=SimpleNamespace(paths={"dev": {"source": SimpleNamespace(kind="warehouse", path="abfss://configured-export")}}))

    io.read_lakehouse_csv("path/to/orders.csv", target="source", spark_session=spark, context={"config": config, "env": "dev"})

    assert ("csv", "abfss://configured-export/Files/path/to/orders.csv") in spark.read.calls


def test_read_lakehouse_parquet_delegates_to_get_path(monkeypatch):
    """Verify Parquet reads use the configured path resolver output directly."""
    spark = _Spark()
    calls = []
    from importlib import import_module

    parquet_module = import_module("fabricops_kit.io.read_lakehouse_parquet")

    def fake_get_path(relative_path, *, target="source", context=None):
        calls.append((relative_path, target, context))
        return f"abfss://configured-target/{relative_path}"

    monkeypatch.setattr(parquet_module, "get_path", fake_get_path)

    io.read_lakehouse_parquet("custom/orders.parquet", target="source", spark_session=spark, context={"env": "dev"})

    assert calls[:2] == [
        ("custom/orders.parquet", "source", {"env": "dev"}),
        ("custom_tsus/orders.parquet", "source", {"env": "dev"}),
    ]
    assert ("parquet", "abfss://configured-target/custom/orders.parquet") in spark.read.calls


def test_lakehouse_table_read_write_delegate_to_shared_resolver(monkeypatch):
    """Verify lakehouse table public functions use the shared table resolver."""
    spark = _Spark()
    frame = _Frame()
    calls = []
    from importlib import import_module

    read_module = import_module("fabricops_kit.io.read_lakehouse_table")
    write_module = import_module("fabricops_kit.io.write_lakehouse_table")

    def fake_resolver(table_name, *, target, schema=None, context=None):
        calls.append((table_name, target, schema, context))
        return table_name, schema, f"abfss://configured-tables/{target}/{schema or 'default'}/{table_name}"

    monkeypatch.setattr(read_module, "resolve_configured_lakehouse_table", fake_resolver)
    monkeypatch.setattr(write_module, "resolve_configured_lakehouse_table", fake_resolver)

    io.read_lakehouse_table("orders", target="source", schema="dbo", spark_session=spark, context={"env": "dev"})
    io.write_lakehouse_table(frame, "orders_clean", target="unified", schema="curated", mode="overwrite", verbose=False, context={"env": "dev"})

    assert calls == [
        ("orders", "source", "dbo", {"env": "dev"}),
        ("orders_clean", "unified", "curated", {"env": "dev"}),
    ]
    assert ("load", "abfss://configured-tables/source/dbo/orders") in spark.read.calls
    assert ("save", "abfss://configured-tables/unified/curated/orders_clean") in frame.write.calls


def test_warehouse_read_write_delegate_to_shared_resolvers(monkeypatch):
    """Verify warehouse public functions use shared warehouse resolvers."""
    spark = _Spark()
    frame = _Frame()
    calls = []
    store = SimpleNamespace(workspace_id="workspace", item_id="warehouse", name="wh", kind="warehouse")
    from importlib import import_module

    query_module = import_module("fabricops_kit.io.read_warehouse_query")
    table_module = import_module("fabricops_kit.io.read_warehouse_table")
    write_module = import_module("fabricops_kit.io.write_warehouse_table")

    def fake_query_resolver(query, *, target, context=None):
        calls.append(("query", query, target, context))
        return store, query

    def fake_table_resolver(schema, table_name, *, target, context=None):
        calls.append(("table", schema, table_name, target, context))
        return store, schema, table_name, f"wh.{schema}.{table_name}"

    monkeypatch.setattr(query_module, "resolve_configured_warehouse_query_target", fake_query_resolver)
    monkeypatch.setattr(table_module, "resolve_configured_warehouse_table", fake_table_resolver)
    monkeypatch.setattr(write_module, "resolve_configured_warehouse_table", fake_table_resolver)
    monkeypatch.setattr(io_core, "_require_fabric_connector", lambda: SimpleNamespace(WorkspaceId="workspace", DatawarehouseId="warehouse"))

    io.read_warehouse_query("select * from dbo.orders", target="warehouse", spark_session=spark, context={"env": "dev"})
    io.read_warehouse_table("dbo", "orders", target="warehouse", spark_session=spark, context={"env": "dev"})
    io.write_warehouse_table(frame, "dbo", "orders", target="warehouse", mode="overwrite", context={"env": "dev"})

    assert calls == [
        ("query", "select * from dbo.orders", "warehouse", {"env": "dev"}),
        ("table", "dbo", "orders", "warehouse", {"env": "dev"}),
        ("table", "dbo", "orders", "warehouse", {"env": "dev"}),
    ]
    assert ("synapsesql", "select * from dbo.orders") in spark.read.calls
    assert ("synapsesql", "wh.dbo.orders") in spark.read.calls
    assert ("synapsesql", "wh.dbo.orders") in frame.write.calls


def test_public_io_owner_files_do_not_duplicate_resolution_patterns():
    """Verify public IO owner files delegate to shared resolver boundaries."""
    from pathlib import Path

    root = Path(__file__).parents[2]
    owner_files = [
        root / "src/fabricops_kit/io/read_lakehouse_csv.py",
        root / "src/fabricops_kit/io/read_lakehouse_excel.py",
        root / "src/fabricops_kit/io/read_lakehouse_parquet.py",
        root / "src/fabricops_kit/io/read_lakehouse_table.py",
        root / "src/fabricops_kit/io/read_warehouse_query.py",
        root / "src/fabricops_kit/io/read_warehouse_table.py",
        root / "src/fabricops_kit/io/write_lakehouse_table.py",
        root / "src/fabricops_kit/io/write_warehouse_table.py",
    ]
    forbidden = [
        'resolve_target_store(target, "lakehouse"',
        'resolve_target_store(target, "warehouse"',
        "resolve_lakehouse_file_location",
        "_join_lakehouse_area_path",
        "/Tables/",
    ]
    failures = []
    for path in owner_files:
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden:
            if pattern in text:
                failures.append(f"{path.relative_to(root)} contains {pattern}")
    assert failures == []


def test_read_lakehouse_excel_reports_missing_resolved_path():
    """Verify invalid resolved Excel paths fail with a useful path error."""
    config = framework_config()
    spark = _Spark()
    spark.read.load = lambda path: SimpleNamespace(count=lambda: 0)

    with pytest.raises(FileNotFoundError, match="No file found at path: .*missing.xlsx"):
        io.read_lakehouse_excel("missing.xlsx", target="source", spark_session=spark, context={"config": config, "env": "dev"})


def test_warehouse_helpers_fail_clearly_outside_fabric_runtime():
    """Verify warehouse helpers fail clearly outside fabric runtime."""
    config = framework_config()

    with pytest.raises(RuntimeError, match="Microsoft Fabric Spark"):
        io.read_warehouse_table("dbo", "orders", target="warehouse", spark_session=_Spark(), context={"config": config, "env": "dev"})
    with pytest.raises(RuntimeError, match="Microsoft Fabric Spark"):
        io.write_warehouse_table(_Frame(), "dbo", "orders", target="warehouse", context={"config": config, "env": "dev"})
