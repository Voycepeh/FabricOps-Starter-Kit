"""Tests for profile_and_register_dataframe orchestration."""

from __future__ import annotations

import importlib
import inspect
import json

import pytest

from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
from fabricops_kit.pipeline import profile_and_register_dataframe as public_profile_and_register_dataframe
from fabricops_kit.pipeline.profile_and_register_dataframe import (
    CATALOGUE_COLUMNS,
    CATALOGUE_TABLE,
    _metadata_column_key,
    _metadata_table_key,
    profile_and_register_dataframe,
)


def _source_df(spark_session):
    """Return a small Spark source DataFrame."""
    return spark_session.createDataFrame(
        [(1, "A", "US"), (2, "A", None), (3, "B", "GB")],
        "id long, customer_type string, country string",
    )


def _profile_df(spark_session):
    """Return lower-level profiler output rows."""
    return spark_session.createDataFrame(
        [
            ("id", "bigint", 3, 3, 0, 0.0, 3, 100.0, 2.0, 1.0, "1", 1.0, 2.0, 3.0, "3"),
            ("customer_type", "string", 3, 3, 0, 0.0, 2, 66.667, None, None, "A", None, None, None, "B"),
            ("country", "string", 3, 2, 1, 33.333, 2, 66.667, None, None, "GB", None, None, None, "US"),
        ],
        "COLUMN_NAME string, DATA_TYPE string, ROW_COUNT long, NON_NULL_COUNT long, NULL_COUNT long, NULL_PERCENT double, DISTINCT_COUNT long, DISTINCT_PERCENT double, MEAN double, STDDEV double, MIN_VALUE string, PERCENTILE_25 double, MEDIAN double, PERCENTILE_75 double, MAX_VALUE string",
    )


def _frequency_df(spark_session):
    """Return lower-level frequency profiler output rows deliberately out of order."""
    return spark_session.createDataFrame(
        [
            ("customer_type", "string", "B", 1, 33.333, 2, 3, 3),
            ("country", "string", None, 1, 33.333, 2, 3, 2),
            ("customer_type", "string", "A", 2, 66.667, 1, 3, 3),
            ("country", "string", "US", 1, 33.333, 1, 3, 2),
        ],
        "COLUMN_NAME string, DATA_TYPE string, VALUE string, FREQUENCY_COUNT long, FREQUENCY_PERCENT double, FREQUENCY_RANK int, PROFILED_ROW_COUNT long, PROFILED_NON_NULL_COUNT long",
    )


@pytest.fixture
def registered(monkeypatch):
    """Patch Fabric context and catalogue writer for profile registration tests."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_dataframe")

    writes = []
    monkeypatch.setattr(module, "resolve_fabric_context", lambda env: (object(), env, {"config": object(), "env": env}))
    monkeypatch.setattr(module, "configured_lakehouse_schema", lambda config, env, target: None)

    def write(df, table_name, *, target, schema, context, mode):
        writes.append({"df": df, "table_name": table_name, "target": target, "schema": schema, "context": context, "mode": mode})

    monkeypatch.setattr(module, "write_lakehouse_table_core", write)
    return writes


def test_profile_and_register_dataframe_is_public_export():
    """Verify the helper is exported from the pipeline package."""
    assert public_profile_and_register_dataframe is profile_and_register_dataframe


def test_profile_and_register_dataframe_signature_has_no_profile_role():
    """Verify catalogue registration does not accept source or target role."""
    parameters = inspect.signature(profile_and_register_dataframe).parameters
    assert list(parameters) == [
        "df",
        "environment_name",
        "store_type",
        "layer",
        "table_name",
        "schema_name",
        "frequency_columns",
        "frequency_top_n",
        "is_sampled",
    ]
    assert "profile_role" not in parameters


@pytest.mark.parametrize("store_type", ["lakehouse", "warehouse", " Warehouse "])
def test_profile_and_register_dataframe_accepts_supported_store_types(spark_session, monkeypatch, registered, store_type):
    """Verify accepted store types are normalized and persisted."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_dataframe")

    monkeypatch.setattr(module, "profile_dataframe", lambda df: _profile_df(spark_session))
    result = profile_and_register_dataframe(
        _source_df(spark_session),
        environment_name="dev",
        store_type=store_type,
        layer="silver",
        table_name="customers_clean",
        is_sampled=True,
    )

    rows = result.select("store_type", "schema_name", "is_sampled").distinct().collect()
    assert [(row.store_type, row.schema_name, row.is_sampled) for row in rows] == [(store_type.strip().lower(), None, True)]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"store_type": "delta"}, "store_type must be one of"),
        ({"environment_name": ""}, "environment_name must be a non-empty string"),
        ({"layer": " "}, "layer must be a non-empty string"),
        ({"table_name": ""}, "table_name must be a non-empty string"),
        ({"schema_name": ""}, "schema_name must be a non-empty string"),
    ],
)
def test_profile_and_register_dataframe_rejects_invalid_required_inputs(spark_session, registered, kwargs, message):
    """Verify invalid store and required string inputs fail clearly."""
    params = {
        "environment_name": "dev",
        "store_type": "lakehouse",
        "layer": "raw",
        "schema_name": None,
        "table_name": "customers",
    }
    params.update(kwargs)
    with pytest.raises(ValueError, match=message):
        profile_and_register_dataframe(_source_df(spark_session), **params)


@pytest.mark.parametrize("frequency_columns", [None, []])
def test_profile_and_register_dataframe_skips_frequency_when_not_requested(spark_session, monkeypatch, registered, frequency_columns):
    """Verify no frequency profiling occurs for None or empty frequency columns."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_dataframe")

    calls = {"profile": 0, "frequency": 0, "df": None}

    def profile(df):
        calls["profile"] += 1
        calls["df"] = df
        return _profile_df(spark_session)

    def frequency(*_args, **_kwargs):
        calls["frequency"] += 1
        raise AssertionError("frequency profiling should not run")

    source = _source_df(spark_session)
    monkeypatch.setattr(module, "profile_dataframe", profile)
    monkeypatch.setattr(module, "profile_frequency_distribution", frequency)

    result = profile_and_register_dataframe(
        source,
        environment_name="dev",
        store_type="lakehouse",
        layer="raw",
        table_name="customers",
        frequency_columns=frequency_columns,
        is_sampled=False,
    )

    assert calls == {"profile": 1, "frequency": 0, "df": source}
    assert "profile_role" not in result.columns
    assert "profiled_at" not in result.columns
    assert result.where("frequency_json is not null").count() == 0
    assert result.count() == 3


def test_profile_and_register_dataframe_builds_frequency_json_and_writes_catalogue(spark_session, monkeypatch, registered):
    """Verify output contract, frequency JSON, deterministic keys, and writer usage."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_dataframe")

    calls = {"profile": 0, "frequency": 0, "frequency_kwargs": None, "sample": 0}
    source = _source_df(spark_session)
    original_sample = getattr(source, "sample")

    def sample_tracker(*args, **kwargs):
        calls["sample"] += 1
        return original_sample(*args, **kwargs)

    source.sample = sample_tracker

    def profile(df):
        calls["profile"] += 1
        assert df is source
        assert profile.__module__ == __name__
        return _profile_df(spark_session)

    def frequency(df, *, columns, top_n):
        calls["frequency"] += 1
        calls["frequency_kwargs"] = {"columns": columns, "top_n": top_n, "df_is_source": df is source}
        assert frequency.__module__ == __name__
        return _frequency_df(spark_session)

    monkeypatch.setattr(module, "profile_dataframe", profile)
    monkeypatch.setattr(module, "profile_frequency_distribution", frequency)

    result = profile_and_register_dataframe(
        source,
        environment_name="dev",
        store_type="warehouse",
        layer="silver",
        schema_name="dbo",
        table_name="customers_clean",
        frequency_columns=("customer_type", "country"),
        frequency_top_n=5,
        is_sampled=True,
    )

    assert calls == {
        "profile": 1,
        "frequency": 1,
        "frequency_kwargs": {"columns": ["customer_type", "country"], "top_n": 5, "df_is_source": True},
        "sample": 0,
    }
    assert registered == [
        {
            "df": result,
            "table_name": CATALOGUE_TABLE,
            "target": "metadata",
            "schema": None,
            "context": {"config": registered[0]["context"]["config"], "env": "dev"},
            "mode": "append",
        }
    ]
    assert result.columns == CATALOGUE_COLUMNS
    expected_schema = metadata_table_schema_registry()[CATALOGUE_TABLE]
    assert [(f.name, type(f.dataType).__name__) for f in result.schema.fields] == [
        (f.name, type(f.dataType).__name__) for f in expected_schema.fields
    ]
    assert {"profile_role", "profiled_at", "_committed_by", "_workspace_name", "_activity_id"}.isdisjoint(result.columns)
    assert [name for name, dtype in result.dtypes if dtype == "timestamp"] == ["_committed_at"]

    rows = {row.column_name: row.asDict() for row in result.collect()}
    assert rows["id"]["frequency_json"] is None
    customer_frequency = json.loads(rows["customer_type"]["frequency_json"])
    country_frequency = json.loads(rows["country"]["frequency_json"])
    assert [value["rank"] for value in customer_frequency["values"]] == [1, 2]
    assert [value["value"] for value in customer_frequency["values"]] == ["A", "B"]
    assert [value["value"] for value in country_frequency["values"]] == ["US", None]
    assert rows["country"]["is_sampled"] is True

    expected_table_key = _metadata_table_key("dev", "warehouse", "silver", "dbo", "customers_clean")
    assert {row["metadata_table_key"] for row in rows.values()} == {expected_table_key}
    assert rows["country"]["metadata_column_key"] == _metadata_column_key(expected_table_key, "country")
    assert rows["country"]["metadata_column_key"] != rows["customer_type"]["metadata_column_key"]
    assert expected_table_key != _metadata_table_key("dev", "warehouse", "silver", None, "customers_clean")


def test_catalogue_schema_matches_main_contract_without_profile_role():
    """Verify catalogue schema remains the canonical physical profile contract."""
    schema = metadata_table_schema_registry()[CATALOGUE_TABLE]
    assert schema.fieldNames() == CATALOGUE_COLUMNS
    assert schema.fieldNames() == [
        "metadata_table_key",
        "metadata_column_key",
        "environment_name",
        "store_type",
        "layer",
        "schema_name",
        "table_name",
        "column_name",
        "data_type",
        "row_count",
        "non_null_count",
        "null_count",
        "null_percent",
        "distinct_count",
        "distinct_percent",
        "mean_value",
        "stddev_value",
        "min_value",
        "percentile_25_value",
        "median_value",
        "percentile_75_value",
        "max_value",
        "is_sampled",
        "frequency_json",
        "_committed_at",
    ]
    assert "profile_role" not in schema.fieldNames()
