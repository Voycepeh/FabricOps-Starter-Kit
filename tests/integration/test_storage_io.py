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


class _Spark:
    def __init__(self):
        self.read = _Reader()
        self.created = []

    def createDataFrame(self, rows):
        self.created.append(rows)
        return {"created": rows}


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


class _Frame:
    def __init__(self):
        self.write = _Writer()

    def repartition(self, *args):
        self.repartition_args = args
        return self


def test_lakehouse_read_and_write_helpers_route_to_configured_paths():
    config = framework_config()
    spark = _Spark()
    frame = _Frame()

    io.read_lakehouse_csv(config, "dev", "source", "Files/raw/orders.csv", spark_session=spark)
    io.write_lakehouse_table(frame, config, "dev", "unified", "orders_clean", mode="overwrite", partition_by=["status"])

    csv_call = next(call for call in spark.read.calls if call[0] == "csv")
    save_call = next(call for call in frame.write.calls if call[0] == "save")
    assert csv_call[1].endswith("/Files/raw/orders.csv")
    assert save_call[1].endswith("/Tables/orders_clean")
    assert ("format", "delta") in frame.write.calls
    assert ("partitionBy", ("status",)) in frame.write.calls


def test_file_readers_validate_source_paths_and_excel_uses_pandas_kwargs(monkeypatch):
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
    config = framework_config()

    with pytest.raises(RuntimeError, match="Microsoft Fabric Spark"):
        io.read_warehouse_table(config, "dev", "warehouse", "dbo", "orders", spark_session=_Spark())
    with pytest.raises(RuntimeError, match="Microsoft Fabric Spark"):
        io.write_warehouse_table(_Frame(), config, "dev", "warehouse", "dbo", "orders")
