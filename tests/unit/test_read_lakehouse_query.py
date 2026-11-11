"""Contract tests for the standalone Lakehouse query entry point."""

from unittest.mock import Mock

import pytest

from fabricops_kit.io.read_lakehouse_query import read_lakehouse_query


def test_query_reuses_configured_source_and_existing_translator(monkeypatch):
    from fabricops_kit.io import read_lakehouse_query as public_reader
    import importlib

    module = importlib.import_module("fabricops_kit.io.read_lakehouse_query")
    pipeline = importlib.import_module("fabricops_kit.pipeline.pipeline_read")
    spark = Mock()
    frame = Mock()
    translator = Mock(return_value=frame)
    monkeypatch.setattr(module, "get_spark_session", lambda **kw: spark)
    monkeypatch.setattr(
        module, "resolve_configured_lakehouse_table",
        lambda *a, **kw: (Mock(), "orders", "demo", "/resolved/delta/path"),
    )
    monkeypatch.setattr(pipeline, "_lakehouse_query", translator)

    result = public_reader(
        "SELECT TOP (5) * FROM demo.orders",
        table_name="orders", schema="demo", store="Bronze",
        context={"_fabricops_suppress_io_log": True},
    )

    assert result is frame
    translator.assert_called_once_with(
        "SELECT TOP (5) * FROM demo.orders",
        {"store": "Bronze", "schema": "demo", "table_name": "orders"},
        context={"_fabricops_suppress_io_log": True},
        spark_session=spark,
    )


def test_query_requires_table_name():
    with pytest.raises(ValueError, match="table_name is required"):
        read_lakehouse_query("SELECT 1", table_name="")
