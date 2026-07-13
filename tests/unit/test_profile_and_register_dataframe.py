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
    runtime_context = {
        "activityId": "activity-1",
        "currentWorkspaceId": "workspace-1",
        "currentWorkspaceName": "Workspace One",
        "currentNotebookId": "notebook-1",
        "currentNotebookName": "Notebook One",
        "userName": "tester",
    }
    monkeypatch.setattr(module, "resolve_fabric_context", lambda env: (object(), env, {"config": object(), "env": env, "runtime_context": runtime_context}))
    monkeypatch.setattr(module, "configured_lakehouse_schema", lambda config, env, target: None)
    monkeypatch.setattr(
        module,
        "build_runtime_audit_fields",
        lambda *, config, env, runtime_context=None: {
            "_committed_by": runtime_context["userName"],
            "_committed_at": "2026-01-01T00:00:00",
            "_workspace_id": runtime_context["currentWorkspaceId"],
            "_workspace_name": runtime_context["currentWorkspaceName"],
            "_notebook_id": runtime_context["currentNotebookId"],
            "_notebook_name": runtime_context["currentNotebookName"],
            "_metadata_lakehouse_name": "metadata_lh",
            "_activity_id": runtime_context["activityId"],
        },
    )

    def write(df, table_name, *, target, schema, context, mode):
        writes.append({"df": df, "table_name": table_name, "target": target, "schema": schema, "context": context, "mode": mode})

    monkeypatch.setattr(module, "write_lakehouse_table_core", write)
    return writes


def test_profile_and_register_dataframe_is_public_export():
    """Verify the helper is exported from the pipeline package."""
    assert public_profile_and_register_dataframe is profile_and_register_dataframe


def test_profile_and_register_dataframe_signature_requires_profile_role():
    """Verify catalogue registration accepts role as a required API seam."""
    parameters = inspect.signature(profile_and_register_dataframe).parameters
    assert list(parameters) == [
        "df",
        "profile_role",
        "environment_name",
        "store_type",
        "layer",
        "table_name",
        "schema_name",
        "frequency_columns",
        "frequency_top_n",
        "is_sampled",
    ]
    assert parameters["profile_role"].default is inspect.Parameter.empty


@pytest.mark.parametrize("role", ["source", "target", " Source ", " TARGET "])
def test_profile_and_register_dataframe_accepts_source_and_target_roles(spark_session, monkeypatch, registered, role):
    """Verify source and target role values are accepted but not persisted."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_dataframe")

    monkeypatch.setattr(module, "profile_dataframe", lambda df: _profile_df(spark_session))
    result = profile_and_register_dataframe(
        _source_df(spark_session),
        profile_role=role,
        environment_name="dev",
        store_type="lakehouse",
        layer="raw",
        table_name="customers",
    )

    assert "profile_role" not in result.columns


def test_profile_and_register_dataframe_requires_profile_role(spark_session, registered):
    """Verify profile_role is required by the public helper signature."""
    with pytest.raises(TypeError, match="profile_role"):
        profile_and_register_dataframe(
            _source_df(spark_session),
            environment_name="dev",
            store_type="lakehouse",
            layer="raw",
            table_name="customers",
        )


@pytest.mark.parametrize("store_type", ["lakehouse", "warehouse", " Warehouse "])
def test_profile_and_register_dataframe_accepts_supported_store_types(spark_session, monkeypatch, registered, store_type):
    """Verify accepted store types are normalized and persisted."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_dataframe")

    monkeypatch.setattr(module, "profile_dataframe", lambda df: _profile_df(spark_session))
    result = profile_and_register_dataframe(
        _source_df(spark_session),
        profile_role="target",
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
        ({"profile_role": "input"}, "profile_role must be one of"),
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
        "profile_role": "source",
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
        profile_role="source",
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
        profile_role="source",
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
    assert [write["table_name"] for write in registered] == [CATALOGUE_TABLE, "METADATA_DATA_LINEAGE_TABLE"]
    assert registered[0] == {
        "df": result,
        "table_name": CATALOGUE_TABLE,
        "target": "metadata",
        "schema": None,
        "context": {"config": registered[0]["context"]["config"], "env": "dev"},
        "mode": "append",
    }
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

    lineage_rows = registered[1]["df"].collect()
    assert len(lineage_rows) == 1
    lineage = lineage_rows[0].asDict()
    assert lineage["metadata_table_key"] == expected_table_key
    assert lineage["profile_role"] == "source"
    assert lineage["_activity_id"] == "activity-1"
    assert lineage["_workspace_id"] == "workspace-1"
    assert lineage["_notebook_id"] == "notebook-1"

    source_role_result = profile_and_register_dataframe(
        source,
        profile_role="source",
        environment_name="dev",
        store_type="warehouse",
        layer="silver",
        schema_name="dbo",
        table_name="customers_clean",
        frequency_columns=None,
    )
    assert {row.metadata_table_key for row in source_role_result.select("metadata_table_key").collect()} == {expected_table_key}


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


def test_lineage_schema_is_table_participation_contract():
    """Verify lineage keeps only participation fields plus canonical audit fields."""
    schema = metadata_table_schema_registry()["METADATA_DATA_LINEAGE_TABLE"]
    assert schema.fieldNames() == [
        "metadata_table_key",
        "profile_role",
        "_committed_by",
        "_committed_at",
        "_workspace_id",
        "_workspace_name",
        "_notebook_id",
        "_notebook_name",
        "_metadata_lakehouse_name",
        "_activity_id",
    ]
    fields = {field.name: field for field in schema.fields}
    assert type(fields["metadata_table_key"].dataType).__name__ == "StringType"
    assert type(fields["profile_role"].dataType).__name__ == "StringType"
    assert fields["metadata_table_key"].nullable is False
    assert fields["profile_role"].nullable is False
    obsolete = {
        "lineage_id",
        "dataset_name",
        "source_table",
        "target_table",
        "source_table_key",
        "target_table_key",
        "source_metadata_table_key",
        "target_metadata_table_key",
        "transformation_steps_json",
        "activity_id",
    }
    assert obsolete.isdisjoint(schema.fieldNames())


def test_lineage_is_not_attempted_when_catalogue_write_fails(spark_session, monkeypatch, registered):
    """Verify catalogue write failure stops before lineage registration."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_dataframe")
    monkeypatch.setattr(module, "profile_dataframe", lambda df: _profile_df(spark_session))

    def fail_catalogue(*_args, **_kwargs):
        raise ValueError("catalogue boom")

    monkeypatch.setattr(module, "write_lakehouse_table_core", fail_catalogue)
    with pytest.raises(ValueError, match="catalogue boom"):
        profile_and_register_dataframe(
            _source_df(spark_session),
            profile_role="source",
            environment_name="dev",
            store_type="lakehouse",
            layer="raw",
            table_name="customers",
        )


def test_lineage_failure_reports_partial_write_state(spark_session, monkeypatch, registered):
    """Verify lineage write failures explain the catalogue snapshot was already written."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_dataframe")
    monkeypatch.setattr(module, "profile_dataframe", lambda df: _profile_df(spark_session))

    def write(df, table_name, *, target, schema, context, mode):
        registered.append({"df": df, "table_name": table_name, "target": target, "schema": schema, "context": context, "mode": mode})
        if table_name == "METADATA_DATA_LINEAGE_TABLE":
            raise ValueError("lineage boom")

    monkeypatch.setattr(module, "write_lakehouse_table_core", write)
    expected_key = _metadata_table_key("dev", "lakehouse", "raw", None, "customers")
    with pytest.raises(RuntimeError, match=f"Catalogue registration succeeded but lineage registration failed.*{expected_key}.*source"):
        profile_and_register_dataframe(
            _source_df(spark_session),
            profile_role="source",
            environment_name="dev",
            store_type="lakehouse",
            layer="raw",
            table_name="customers",
        )
    assert [write["table_name"] for write in registered] == [CATALOGUE_TABLE, "METADATA_DATA_LINEAGE_TABLE"]
