from types import SimpleNamespace

import fabricops_kit.fabric_input_output as fio
from fabricops_kit.fabric_input_output import FabricStore


def _config():
    store = FabricStore(env="dev", workspace_id="workspace", item_id="source-item", name="lh_source_dev", kind="lakehouse")
    return SimpleNamespace(paths={"dev": {"source": store}})


class _BinaryFrame:
    def count(self):
        return 1

    def select(self, column):
        assert column == "content"
        return self

    def collect(self):
        return [[b"placeholder xlsx bytes"]]


class _Reader:
    def __init__(self):
        self.format_name = None
        self.options = {}
        self.loaded_path = None

    def format(self, name):
        self.format_name = name
        return self

    def option(self, key, value):
        self.options[key] = value
        return self

    def load(self, path):
        self.loaded_path = path
        return _BinaryFrame()


class _Spark:
    def __init__(self):
        self.read = _Reader()
        self.created_from = None

    def createDataFrame(self, pandas_df):
        self.created_from = pandas_df
        return {"spark_df_from": pandas_df}


def test_read_lakehouse_excel_passes_pandas_read_excel_kwargs(monkeypatch):
    spark = _Spark()
    read_calls = []
    expected_pdf = {"columns": ["Publication Title", "Year"]}

    def fake_read_excel(path, **kwargs):
        read_calls.append((path, kwargs))
        return expected_pdf

    monkeypatch.setattr(fio.pd, "read_excel", fake_read_excel)

    result = fio.read_lakehouse_excel(
        _config(),
        "dev",
        "source",
        "Files/Publications_at_the_National_University_of_Singapore_2020_-_2026.xlsx",
        sheet_name=0,
        spark_session=spark,
        skiprows=1,
        header=0,
        usecols="A:D",
        dtype={"Year": "string"},
        nrows=20,
    )

    assert spark.read.format_name == "binaryFile"
    assert spark.read.options == {"recursiveFileLookup": "false"}
    assert spark.read.loaded_path.endswith("/Files/Publications_at_the_National_University_of_Singapore_2020_-_2026.xlsx")
    assert len(read_calls) == 1
    _, kwargs = read_calls[0]
    assert kwargs == {
        "sheet_name": 0,
        "skiprows": 1,
        "header": 0,
        "usecols": "A:D",
        "dtype": {"Year": "string"},
        "nrows": 20,
    }
    assert spark.created_from is expected_pdf
    assert result == {"spark_df_from": expected_pdf}
