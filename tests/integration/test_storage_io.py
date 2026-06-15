"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

import fabricops_kit.fabric_input_output as io

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
    spark = _Spark()
    frame = _Frame()

    io.read_lakehouse_csv(config, "dev", "source", "Files/raw/orders.csv", spark_session=spark)
    io.write_lakehouse_table(frame, config, "dev", "unified", "orders_clean", schema=None, mode="overwrite", partition_by=["status"], options={"overwriteSchema": "true"}, verbose=False)

    csv_call = next(call for call in spark.read.calls if call[0] == "csv")
    save_call = next(call for call in frame.write.calls if call[0] == "save")
    assert csv_call[1].endswith("/Files/raw/orders.csv")
    assert save_call[1].endswith("/Tables/orders_clean")
    assert ("format", "delta") in frame.write.calls
    assert ("partitionBy", ("status",)) in frame.write.calls


def test_metadata_lakehouse_table_helpers_use_abfss_paths_without_registered_tables():
    """Verify metadata lakehouse table helpers use abfss paths without registered tables."""
    config = framework_config()
    spark = _Spark()
    frame = _Frame()

    read_result = io.read_lakehouse_table(config, "dev", "metadata", "METADATA_DQ_RULES", schema=None, spark_session=spark)
    io.write_lakehouse_table(frame, config, "dev", "metadata", "METADATA_DQ_RULES", schema=None, mode="ignore", verbose=False)

    expected_path = "abfss://dev-workspace@onelake.dfs.fabric.microsoft.com/dev-lakehouse-item/Tables/METADATA_DQ_RULES"
    assert read_result.count() == 1
    assert spark.table_calls == []
    assert ("load", expected_path) in spark.read.calls
    assert ("save", expected_path) in frame.write.calls
    assert not any(call[0] == "saveAsTable" for call in frame.write.calls)
    assert not any(call[0] == "save" and "Unidentified" in call[1] for call in frame.write.calls)


def test_lakehouse_table_helpers_reject_nested_table_paths():
    """Verify lakehouse table helpers reject nested table paths."""
    config = framework_config()

    with pytest.raises(ValueError, match="simple table name"):
        io.write_lakehouse_table(_Frame(), config, "dev", "metadata", "METADATA_DQ_RULES/Unidentified", schema=None, mode="ignore", verbose=False)


def test_file_readers_validate_source_paths_and_excel_uses_pandas_kwargs(monkeypatch):
    """Verify file readers validate source paths and excel uses pandas kwargs."""
    config = framework_config()
    spark = _Spark()
    captured = {}

    monkeypatch.setattr(io.pd, "read_excel", lambda path, sheet_name=0, **kwargs: captured.setdefault("kwargs", kwargs) or [{"a": 1}])

    with pytest.raises(ValueError, match="relative_path"):
        io.read_lakehouse_csv(config, "dev", "source", "", spark_session=spark)
    with pytest.raises(ValueError, match="folder/file.parquet"):
        io.read_lakehouse_parquet(config, "dev", "source", "orders.parquet", spark_session=spark, verbose=False)

    io.read_lakehouse_excel(config, "dev", "source", "Files/reference/map.xlsx", sheet_name="Sheet1", spark_session=spark, skiprows=1)
    assert captured["kwargs"] == {"skiprows": 1}


def test_warehouse_helpers_fail_clearly_outside_fabric_runtime():
    """Verify warehouse helpers fail clearly outside fabric runtime."""
    config = framework_config()

    with pytest.raises(RuntimeError, match="Microsoft Fabric Spark"):
        io.read_warehouse_table(config, "dev", "warehouse", "dbo", "orders", spark_session=_Spark())
    with pytest.raises(RuntimeError, match="Microsoft Fabric Spark"):
        io.write_warehouse_table(_Frame(), config, "dev", "warehouse", "dbo", "orders")
