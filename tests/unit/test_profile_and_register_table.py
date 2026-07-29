"""Tests for profile_and_register_table orchestration."""

from __future__ import annotations

import importlib
import inspect
import json
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from fabricops_kit.config import FabricStore
from fabricops_kit.config.metadata_keys import (
    _build_metadata_column_key as _metadata_column_key,
    _build_metadata_table_key as _metadata_table_key,
)
from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
from fabricops_kit.pipeline import profile_and_register_table as public_profile_and_register_table
from fabricops_kit.pipeline.profile_and_register_table import (
    CATALOGUE_COLUMNS,
    CATALOGUE_TABLE,
    PROFILED_COLUMNS,
    PROFILED_TABLE,
    _catalogue_dataframe_from_profiled,
    _resolve_physical_identity,
    _schema_fingerprint,
    profile_and_register_table,
)

AUDIT_COLUMNS = [
    "_committed_by",
    "_committed_at",
    "_workspace_id",
    "_workspace_name",
    "_notebook_id",
    "_notebook_name",
    "_metadata_lakehouse_name",
    "_activity_id",
]


def test_logical_table_and_column_keys_are_environment_independent():
    """Verify logical keys use canonical table coordinates, never runtime context."""
    dev_key = _metadata_table_key("lakehouse", "silver", "dbo", "orders")
    prod_key = _metadata_table_key("lakehouse", "silver", "dbo", "orders")

    assert dev_key == prod_key
    assert dev_key != _metadata_table_key("warehouse", "silver", "dbo", "orders")
    assert dev_key != _metadata_table_key("lakehouse", "gold", "dbo", "orders")
    assert dev_key != _metadata_table_key("lakehouse", "silver", "sales", "orders")
    assert dev_key != _metadata_table_key("lakehouse", "silver", "dbo", "customers")
    assert _metadata_column_key(dev_key, "Order_ID") == _metadata_column_key(prod_key, " order_id ")
    assert _metadata_column_key(dev_key, "order_id") != _metadata_column_key(dev_key, "amount")
    assert _metadata_column_key(dev_key, "order_id") != _metadata_column_key(
        _metadata_table_key("lakehouse", "silver", "dbo", "customers"), "order_id"
    )


def test_schema_fingerprint_uses_only_existing_ordered_schema_content(spark_session):
    """Verify schema identity ignores observations while retaining the existing schema rule."""
    from pyspark.sql import types as T

    base_schema = T.StructType(
        [T.StructField("order_id", T.LongType(), False), T.StructField("amount", T.DoubleType(), True)]
    )
    dev = spark_session.createDataFrame([(1, 1.0)], schema=base_schema)
    prod = spark_session.createDataFrame([(99, 900.0)], schema=base_schema)

    assert _schema_fingerprint(dev) == _schema_fingerprint(prod)
    assert _schema_fingerprint(dev) != _schema_fingerprint(
        spark_session.createDataFrame([(1, 1.0)], "id long, amount double")
    )
    assert _schema_fingerprint(dev) != _schema_fingerprint(
        spark_session.createDataFrame([(1, "1.0")], "order_id long, amount string")
    )
    assert _schema_fingerprint(dev) != _schema_fingerprint(
        spark_session.createDataFrame([(1.0, 1)], "amount double, order_id long")
    )
    nullable_only = T.StructType(
        [T.StructField("order_id", T.LongType(), True), T.StructField("amount", T.DoubleType(), True)]
    )
    assert _schema_fingerprint(dev) == _schema_fingerprint(
        spark_session.createDataFrame([(1, 1.0)], schema=nullable_only)
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
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")

    writes = []
    resolved_context = {
        "config": object(),
        "env": "dev",
        "activityId": "activity-1",
        "currentWorkspaceId": "workspace-1",
        "currentWorkspaceName": "Workspace One",
        "currentNotebookId": "notebook-1",
        "currentNotebookName": "Notebook One",
        "userName": "tester",
    }
    monkeypatch.setattr(
        module,
        "resolve_fabric_context",
        lambda: (resolved_context["config"], resolved_context["env"], resolved_context),
    )
    monkeypatch.setattr(
        module,
        "get_store",
        lambda config, env, target: FabricStore(
            env=env,
            workspace_id="workspace-1",
            item_id=f"{target}-1",
            name=target,
            kind="warehouse" if target == "warehouse" else "lakehouse",
            schema="dbo" if target == "warehouse" else None,
        ),
    )
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
        writes.append(
            {"df": df, "table_name": table_name, "target": target, "schema": schema, "context": context, "mode": mode}
        )

    def upsert_catalogue(*, catalogue_df, config, env, spark_session):
        writes.append(
            {
                "df": catalogue_df,
                "table_name": CATALOGUE_TABLE,
                "target": "metadata",
                "schema": None,
                "context": {"config": config, "env": env},
                "mode": "upsert",
            }
        )

    def upsert_lineage(*, lineage_df, config, env, spark_session):
        writes.append(
            {
                "df": lineage_df,
                "table_name": "METADATA_DATA_LINEAGE",
                "target": "metadata",
                "schema": None,
                "context": {"config": config, "env": env},
                "mode": "upsert",
            }
        )

    monkeypatch.setattr(module, "write_lakehouse_table_core", write)
    monkeypatch.setattr(module, "_upsert_catalogue_identities", upsert_catalogue)
    monkeypatch.setattr(module, "_upsert_lineage_event", upsert_lineage)
    return writes


def test_profile_and_register_table_is_public_export():
    """Verify the helper is exported from the pipeline package."""
    assert public_profile_and_register_table is profile_and_register_table


def test_old_profile_registration_api_is_removed():
    """Verify the breaking rename leaves no old export or import module."""
    import fabricops_kit
    import fabricops_kit.pipeline as pipeline

    assert not hasattr(fabricops_kit, "profile_and_register_dataframe")
    assert not hasattr(pipeline, "profile_and_register_dataframe")
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("fabricops_kit.pipeline.profile_and_register_dataframe")


def test_profile_and_register_table_imports_shared_profiler_directly():
    """Verify registration has no dependency on the public profiling wrapper."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")

    assert module.build_profile_dataframe is not None
    assert not hasattr(module, "profile_dataframe")


def test_profile_registration_call_flow_has_no_public_profiling_edge():
    """Verify the committed architecture contract records the shared call seam."""
    payload = json.loads(Path("docs/reference/_data/public-function-call-flows.json").read_text(encoding="utf-8"))
    flow = next(row for row in payload["public_functions"] if row["function_name"] == "profile_and_register_table")
    direct_callees = {
        row["qualified_name"]: row for row in flow["flow"] if row["parent_qualified_name"] == flow["qualified_name"]
    }

    assert "fabricops_kit.pipeline.profile_dataframe.profile_dataframe" not in direct_callees
    assert "fabricops_kit.pipeline.shared.build_profile_dataframe" in direct_callees
    assert "Type 1" not in direct_callees["fabricops_kit.pipeline.shared.build_profile_dataframe"]["violation_types"]

    frequency_json = next(
        row
        for row in flow["flow"]
        if row["qualified_name"] == "fabricops_kit.pipeline.profile_and_register_table._frequency_json_dataframe"
    )
    frequency_callees = {
        row["qualified_name"]
        for row in flow["flow"]
        if row["parent_qualified_name"] == frequency_json["qualified_name"]
    }
    assert (
        "fabricops_kit.pipeline.profile_frequency_distribution.profile_frequency_distribution" not in frequency_callees
    )
    assert "fabricops_kit.pipeline.shared.build_frequency_distribution_dataframe" in frequency_callees


def test_profile_and_register_table_signature_requires_profile_role():
    """Verify catalogue registration accepts role as a required API seam."""
    parameters = inspect.signature(profile_and_register_table).parameters
    assert list(parameters) == [
        "df",
        "profile_role",
        "target",
        "table_name",
        "schema",
        "frequency_columns",
        "frequency_top_n",
        "frequency_max_distinct_percent",
        "frequency_profile_df",
    ]
    assert parameters["profile_role"].default is inspect.Parameter.empty
    assert parameters["frequency_top_n"].default is None
    assert str(parameters["frequency_top_n"].annotation) == "int | None"
    assert parameters["frequency_max_distinct_percent"].default == 80.0
    assert str(parameters["frequency_max_distinct_percent"].annotation) == "float | None"


def test_resolved_identity_uses_active_environment_and_configured_lakehouse(monkeypatch):
    """Derive environment, kind, layer, configured schema, and normalized table."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    store = FabricStore("dev", "workspace", "item", "Unified", "lakehouse", True, "dbo")
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {"env": "dev"}))
    monkeypatch.setattr(module, "get_store", lambda config, env, target: store)

    role, target, table, schema, kind, _config, env, _context = _resolve_physical_identity(
        profile_role=" Source ", target=" Unified ", schema=None, table_name="customers"
    )

    assert (role, target, table, schema, kind, env) == ("source", "unified", "customers", "dbo", "lakehouse", "dev")


def test_resolved_identity_uses_configured_warehouse_default(monkeypatch):
    """Derive a Warehouse identity and its configured default schema."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    store = FabricStore("dev", "workspace", "item", "Product", "warehouse", schema="sales")
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {"env": "dev"}))
    monkeypatch.setattr(module, "get_store", lambda config, env, target: store)

    identity = _resolve_physical_identity(profile_role="target", target="product", schema=None, table_name="orders")

    assert identity[1:5] == ("product", "orders", "sales", "warehouse")


@pytest.mark.parametrize(
    ("store", "message"),
    [
        (SimpleNamespace(kind="warehouse", schema=None), "schema is required for Warehouse"),
        (SimpleNamespace(kind="lakehouse", schema_enabled=True, schema=None), "schema is required for schema-enabled"),
        (SimpleNamespace(kind="kusto"), "unsupported store kind 'kusto'"),
    ],
)
def test_resolved_identity_rejects_invalid_configured_store(monkeypatch, store, message):
    """Fail clearly for missing required schemas and unsupported stores."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {"env": "dev"}))
    monkeypatch.setattr(module, "get_store", lambda config, env, target: store)

    with pytest.raises(ValueError, match=message):
        _resolve_physical_identity(profile_role="source", target="source", schema=None, table_name="orders")


def test_removed_identity_arguments_are_rejected():
    """Do not retain compatibility arguments for the breaking API change."""
    for name in ("environment_name", "store_type", "layer", "schema_name"):
        with pytest.raises(TypeError, match=name):
            profile_and_register_table(
                object(), profile_role="source", target="source", table_name="orders", **{name: "old"}
            )


@pytest.mark.parametrize("role", ["source", "target", " Source ", " TARGET "])
def test_profile_and_register_table_accepts_source_and_target_roles(spark_session, monkeypatch, registered, role):
    """Verify source and target role values are accepted but not persisted."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")

    monkeypatch.setattr(module, "build_profile_dataframe", lambda df: _profile_df(spark_session))
    result = profile_and_register_table(
        _source_df(spark_session),
        profile_role=role,
        target="raw",
        table_name="customers",
    )

    assert "profile_role" not in result.columns


def test_profile_and_register_table_requires_profile_role(spark_session, registered):
    """Verify profile_role is required by the public helper signature."""
    with pytest.raises(TypeError, match="profile_role"):
        profile_and_register_table(
            _source_df(spark_session),
            target="raw",
            table_name="customers",
        )


@pytest.mark.parametrize(
    ("target", "kind", "schema"), [("silver", "lakehouse", None), ("warehouse", "warehouse", "dbo")]
)
def test_profile_and_register_table_derives_supported_store_types(
    spark_session, monkeypatch, registered, target, kind, schema
):
    """Verify configured store kinds and target layers are persisted."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")

    monkeypatch.setattr(module, "build_profile_dataframe", lambda df: _profile_df(spark_session))
    result = profile_and_register_table(
        _source_df(spark_session),
        profile_role="target",
        target=target,
        schema=schema,
        table_name="customers_clean",
    )

    rows = result.select("environment_name", "store_type", "layer", "schema_name").distinct().collect()
    assert [(row.environment_name, row.store_type, row.layer, row.schema_name) for row in rows] == [
        ("dev", kind, target, schema)
    ]
    assert "is_sampled" not in result.columns


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"profile_role": "input"}, "profile_role must be one of"),
        ({"target": " "}, "target must be a non-empty string"),
        ({"table_name": ""}, "table_name must be a non-empty string"),
        ({"schema": ""}, "schema must be a non-empty identifier"),
    ],
)
def test_profile_and_register_table_rejects_invalid_required_inputs(spark_session, registered, kwargs, message):
    """Verify invalid store and required string inputs fail clearly."""
    params = {
        "profile_role": "source",
        "target": "raw",
        "schema": None,
        "table_name": "customers",
    }
    params.update(kwargs)
    with pytest.raises(ValueError, match=message):
        profile_and_register_table(_source_df(spark_session), **params)


@pytest.mark.parametrize("threshold", [-0.1, 100.1, float("nan"), float("inf"), -float("inf")])
def test_profile_and_register_table_rejects_invalid_frequency_threshold(spark_session, registered, threshold):
    """Verify automatic frequency threshold validation fails clearly."""
    with pytest.raises(ValueError, match="frequency_max_distinct_percent must be finite and between 0.0 and 100.0"):
        profile_and_register_table(
            _source_df(spark_session),
            profile_role="source",
            target="raw",
            table_name="customers",
            frequency_max_distinct_percent=threshold,
        )


def test_profile_and_register_table_skips_frequency_for_empty_columns(spark_session, monkeypatch, registered):
    """Verify no frequency profiling occurs for an explicit empty frequency column list."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")

    calls = {"profile": 0, "frequency": 0, "df": None}

    def profile(df):
        calls["profile"] += 1
        calls["df"] = df
        return _profile_df(spark_session)

    def frequency(*_args, **_kwargs):
        calls["frequency"] += 1
        raise AssertionError("frequency profiling should not run")

    source = _source_df(spark_session)
    monkeypatch.setattr(module, "build_profile_dataframe", profile)
    monkeypatch.setattr(module, "build_frequency_distribution_dataframe", frequency)

    result = profile_and_register_table(
        source,
        profile_role="source",
        target="raw",
        table_name="customers",
        frequency_columns=[],
    )

    assert calls == {"profile": 1, "frequency": 0, "df": source}
    assert "profile_role" not in result.columns
    assert "profiled_at" in result.columns
    assert result.where("frequency_json is not null").count() == 0
    assert result.count() == 3


def test_profile_and_register_table_default_and_explicit_frequency_json_integration(spark_session, registered):
    """Verify default threshold, explicit columns, disabled threshold, and empty skip semantics."""
    source = spark_session.createDataFrame(
        [(i, "A" if i % 2 == 0 else "B", "US" if i % 3 == 0 else "GB") for i in range(25)],
        "id long, customer_type string, country string",
    )

    default_result = profile_and_register_table(
        source,
        profile_role="source",
        target="raw",
        table_name="customers",
    )
    default_rows = {row.column_name: row.asDict() for row in default_result.collect()}
    assert set(default_rows) == {"id", "customer_type", "country"}
    id_skip = json.loads(default_rows["id"]["frequency_json"])
    assert id_skip == {
        "status": "skipped",
        "reason": "high_cardinality",
        "distinct_percent": 100.0,
        "threshold_percent": 80.0,
        "message": "Frequency profiling skipped because distinct percentage exceeded 80%.",
    }
    assert "values" in json.loads(default_rows["customer_type"]["frequency_json"])
    assert "values" in json.loads(default_rows["country"]["frequency_json"])

    selected_result = profile_and_register_table(
        source,
        profile_role="source",
        target="raw",
        table_name="customers",
        frequency_columns=["id"],
    )
    selected_rows = {row.column_name: row.asDict() for row in selected_result.collect()}
    assert selected_rows["customer_type"]["frequency_json"] is None
    assert selected_rows["country"]["frequency_json"] is None
    selected_frequency = json.loads(selected_rows["id"]["frequency_json"])
    assert len(selected_frequency["values"]) == 25
    assert selected_frequency["source_row_count"] == 25
    assert selected_frequency["profiled_row_count"] == 25
    assert selected_frequency["profiled_non_null_count"] == 25
    assert selected_frequency["frequency_scope"] == "full_source"

    unbounded_result = profile_and_register_table(
        source,
        profile_role="source",
        target="raw",
        table_name="customers",
        frequency_max_distinct_percent=None,
    )
    unbounded_rows = {row.column_name: row.asDict() for row in unbounded_result.collect()}
    assert len(json.loads(unbounded_rows["id"]["frequency_json"])["values"]) == 25

    skipped_result = profile_and_register_table(
        source,
        profile_role="source",
        target="raw",
        table_name="customers",
        frequency_columns=[],
    )
    assert skipped_result.where("frequency_json is not null").count() == 0
    assert skipped_result.count() == 3


def test_profile_and_register_table_threshold_boundary_and_all_null_json(spark_session, registered):
    """Verify automatic 80% boundary, high-cardinality skip JSON, and all-null skip JSON."""
    source = spark_session.createDataFrame(
        [(i % 8, i % 9, None) for i in range(10)],
        "at_threshold int, above_threshold int, all_null string",
    )

    result = profile_and_register_table(
        source,
        profile_role="source",
        target="raw",
        table_name="thresholds",
    )

    rows = {row.column_name: row.asDict() for row in result.collect()}
    assert "values" in json.loads(rows["at_threshold"]["frequency_json"])
    assert json.loads(rows["above_threshold"]["frequency_json"]) == {
        "status": "skipped",
        "reason": "high_cardinality",
        "distinct_percent": 90.0,
        "threshold_percent": 80.0,
        "message": "Frequency profiling skipped because distinct percentage exceeded 80%.",
    }
    assert json.loads(rows["all_null"]["frequency_json"]) == {
        "status": "skipped",
        "reason": "no_non_null_values",
        "distinct_percent": None,
        "threshold_percent": 80.0,
        "message": "Frequency profiling skipped because the column contains no non-null values.",
    }


def test_profile_and_register_table_reuses_profile_for_automatic_frequency_selection(
    spark_session, monkeypatch, registered
):
    """Verify automatic selection uses one profile pass and one frequency call."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    source = _source_df(spark_session)
    calls = {"profile": 0, "frequency": 0, "frequency_kwargs": None}

    def profile(df):
        calls["profile"] += 1
        assert df is source
        return _profile_df(spark_session)

    def frequency(df, *, columns, top_n):
        calls["frequency"] += 1
        calls["frequency_kwargs"] = {"columns": columns, "top_n": top_n, "df_is_source": df is source}
        quoted_columns = ", ".join(repr(column) for column in columns)
        return _frequency_df(spark_session).where(f"COLUMN_NAME in ({quoted_columns})")

    monkeypatch.setattr(module, "build_profile_dataframe", profile)
    monkeypatch.setattr(module, "build_frequency_distribution_dataframe", frequency)

    result = profile_and_register_table(
        source,
        profile_role="source",
        target="raw",
        table_name="customers",
    )

    assert calls == {
        "profile": 1,
        "frequency": 1,
        "frequency_kwargs": {"columns": ["customer_type"], "top_n": None, "df_is_source": True},
    }
    rows = {row.column_name: row.asDict() for row in result.collect()}
    assert json.loads(rows["id"]["frequency_json"])["reason"] == "high_cardinality"
    country_skip = json.loads(rows["country"]["frequency_json"])
    assert country_skip == {
        "status": "skipped",
        "reason": "high_cardinality",
        "distinct_percent": 100.0,
        "threshold_percent": 80.0,
        "message": "Frequency profiling skipped because distinct percentage exceeded 80%.",
    }


def test_profile_and_register_table_uses_unrounded_cardinality_for_threshold(
    spark_session, monkeypatch, registered
):
    """Verify a column just above 80% is skipped even when display percentage rounds to 80.0."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    source = spark_session.createDataFrame([(1, 1), (2, 2)], "at_threshold long, just_above long")
    profile_schema = "COLUMN_NAME string, DATA_TYPE string, ROW_COUNT long, NON_NULL_COUNT long, NULL_COUNT long, NULL_PERCENT double, DISTINCT_COUNT long, DISTINCT_PERCENT double, MEAN double, STDDEV double, MIN_VALUE string, PERCENTILE_25 double, MEDIAN double, PERCENTILE_75 double, MAX_VALUE string"
    profile_rows = spark_session.createDataFrame(
        [
            (
                "at_threshold",
                "bigint",
                1_000_000,
                1_000_000,
                0,
                0.0,
                800_000,
                80.0,
                None,
                None,
                "1",
                None,
                None,
                None,
                "800000",
            ),
            (
                "just_above",
                "bigint",
                1_000_000,
                1_000_000,
                0,
                0.0,
                800_004,
                80.0004,
                None,
                None,
                "1",
                None,
                None,
                None,
                "800004",
            ),
        ],
        profile_schema,
    )
    calls = {"profile": 0, "frequency": 0, "frequency_kwargs": None}

    def profile(df):
        calls["profile"] += 1
        return profile_rows

    def frequency(df, *, columns, top_n):
        calls["frequency"] += 1
        calls["frequency_kwargs"] = {"columns": columns, "top_n": top_n}
        return spark_session.createDataFrame(
            [("at_threshold", "bigint", "1", 1, 100.0, 1, 1_000_000, 1_000_000)],
            "COLUMN_NAME string, DATA_TYPE string, VALUE string, FREQUENCY_COUNT long, FREQUENCY_PERCENT double, FREQUENCY_RANK int, PROFILED_ROW_COUNT long, PROFILED_NON_NULL_COUNT long",
        )

    monkeypatch.setattr(module, "build_profile_dataframe", profile)
    monkeypatch.setattr(module, "build_frequency_distribution_dataframe", frequency)

    result = profile_and_register_table(
        source,
        profile_role="source",
        target="raw",
        table_name="threshold_rounding",
    )

    assert calls == {"profile": 1, "frequency": 1, "frequency_kwargs": {"columns": ["at_threshold"], "top_n": None}}
    rows = {row.column_name: row.asDict() for row in result.collect()}
    assert "values" in json.loads(rows["at_threshold"]["frequency_json"])
    assert json.loads(rows["just_above"]["frequency_json"]) == {
        "status": "skipped",
        "reason": "high_cardinality",
        "distinct_percent": 80.0,
        "threshold_percent": 80.0,
        "message": "Frequency profiling skipped because distinct percentage exceeded 80%.",
    }


def test_profile_and_register_table_builds_frequency_json_and_writes_profiled_and_catalogue(
    spark_session, monkeypatch, registered
):
    """Verify output contract, frequency JSON, deterministic keys, and writer usage."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")

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

    monkeypatch.setattr(module, "build_profile_dataframe", profile)
    monkeypatch.setattr(module, "build_frequency_distribution_dataframe", frequency)

    result = profile_and_register_table(
        source,
        profile_role="source",
        target="silver",
        schema="dbo",
        table_name="customers_clean",
        frequency_columns=("customer_type", "country"),
        frequency_top_n=5,
    )

    assert calls == {
        "profile": 1,
        "frequency": 1,
        "frequency_kwargs": {"columns": ["customer_type", "country"], "top_n": 5, "df_is_source": True},
        "sample": 0,
    }
    assert [write["table_name"] for write in registered] == [PROFILED_TABLE, CATALOGUE_TABLE, "METADATA_DATA_LINEAGE"]
    assert registered[0] == {
        "df": result,
        "table_name": PROFILED_TABLE,
        "target": "metadata",
        "schema": None,
        "context": {"config": registered[0]["context"]["config"], "env": "dev"},
        "mode": "append",
    }
    assert registered[1]["table_name"] == CATALOGUE_TABLE
    assert registered[1]["mode"] == "upsert"
    assert registered[1]["df"].columns == CATALOGUE_COLUMNS
    assert registered[1]["df"].count() == 3
    assert registered[2]["context"]["env"] == "dev"
    lineage_schema = metadata_table_schema_registry()["METADATA_DATA_LINEAGE"]
    assert [(f.name, type(f.dataType).__name__, f.nullable) for f in registered[2]["df"].schema.fields] == [
        (f.name, type(f.dataType).__name__, f.nullable) for f in lineage_schema.fields
    ]
    assert result.columns == PROFILED_COLUMNS
    expected_schema = metadata_table_schema_registry()[PROFILED_TABLE]
    assert [(f.name, type(f.dataType).__name__) for f in result.schema.fields] == [
        (f.name, type(f.dataType).__name__) for f in expected_schema.fields
    ]
    assert "profile_role" not in result.columns
    assert set(AUDIT_COLUMNS).issubset(result.columns)
    assert [name for name, dtype in result.dtypes if dtype == "timestamp"] == ["profiled_at", "_committed_at"]

    rows = {row.column_name: row.asDict() for row in result.collect()}
    assert rows["id"]["frequency_json"] is None
    customer_frequency = json.loads(rows["customer_type"]["frequency_json"])
    country_frequency = json.loads(rows["country"]["frequency_json"])
    assert [value["rank"] for value in customer_frequency["values"]] == [1, 2]
    assert [value["value"] for value in customer_frequency["values"]] == ["A", "B"]
    assert [value["value"] for value in country_frequency["values"]] == ["US", None]
    assert "is_sampled" not in rows["country"]

    expected_environment = "dev"
    expected_store_type = "lakehouse"
    expected_layer = "silver"
    expected_schema = "dbo"
    expected_table = "customers_clean"
    expected_table_key = _metadata_table_key(
        expected_store_type,
        expected_layer,
        expected_schema,
        expected_table,
    )
    assert {row["metadata_table_key"] for row in rows.values()} == {expected_table_key}
    assert {
        (
            row["environment_name"],
            row["store_type"],
            row["layer"],
            row["schema_name"],
            row["table_name"],
        )
        for row in rows.values()
    } == {(expected_environment, expected_store_type, expected_layer, expected_schema, expected_table)}
    assert rows["country"]["metadata_column_key"] == _metadata_column_key(expected_table_key, "country")
    assert rows["country"]["metadata_column_key"] != rows["customer_type"]["metadata_column_key"]
    assert expected_table_key != _metadata_table_key(
        expected_store_type,
        expected_layer,
        None,
        expected_table,
    )

    catalogue_rows = registered[1]["df"].collect()
    assert {row.metadata_column_key for row in catalogue_rows} == {row["metadata_column_key"] for row in rows.values()}
    assert all(row.row_count is None if hasattr(row, "row_count") else True for row in catalogue_rows)

    lineage_rows = registered[2]["df"].collect()
    assert len(lineage_rows) == 1
    lineage = lineage_rows[0].asDict()
    assert lineage["metadata_table_key"] == expected_table_key
    assert lineage["profile_role"] == "source"
    assert lineage["activity_id"] == "activity-1"
    assert lineage["workspace_id"] == "workspace-1"
    assert lineage["notebook_id"] == "notebook-1"
    assert lineage["_activity_id"] == "activity-1"
    assert lineage["_workspace_id"] == "workspace-1"
    assert lineage["_notebook_id"] == "notebook-1"
    assert lineage["_committed_by"] == "tester"

    source_role_result = profile_and_register_table(
        source,
        profile_role="source",
        target="silver",
        schema="dbo",
        table_name="customers_clean",
        frequency_columns=None,
    )
    assert {row.metadata_table_key for row in source_role_result.select("metadata_table_key").collect()} == {
        expected_table_key
    }


def test_profiled_schema_matches_detailed_profile_contract_without_profile_role():
    """Verify profiled schema remains the detailed physical profile contract."""
    schema = metadata_table_schema_registry()[PROFILED_TABLE]
    assert schema.fieldNames() == PROFILED_COLUMNS
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
        "frequency_json",
        "schema_fingerprint",
        "profiled_at",
        "_committed_by",
        "_committed_at",
        "_workspace_id",
        "_workspace_name",
        "_notebook_id",
        "_notebook_name",
        "_metadata_lakehouse_name",
        "_activity_id",
    ]
    assert "profile_role" not in schema.fieldNames()


def test_catalogue_schema_is_narrow_identity_contract():
    """Verify catalogue schema contains identity columns without profiling statistics."""
    schema = metadata_table_schema_registry()[CATALOGUE_TABLE]
    assert schema.fieldNames() == CATALOGUE_COLUMNS
    assert schema.fieldNames() == [
        "metadata_table_key",
        "metadata_column_key",
        "schema_fingerprint",
        "environment_name",
        "store_type",
        "layer",
        "schema_name",
        "table_name",
        "column_name",
        "data_type",
        "_committed_by",
        "_committed_at",
        "_workspace_id",
        "_workspace_name",
        "_notebook_id",
        "_notebook_name",
        "_metadata_lakehouse_name",
        "_activity_id",
    ]
    assert {
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
        "frequency_json",
        "profiled_at",
    }.isdisjoint(schema.fieldNames())


def test_catalogue_dataframe_from_profiled_deduplicates_identity_rows(spark_session):
    """Verify duplicate profiled observations produce unique catalogue identities."""
    schema = metadata_table_schema_registry()[PROFILED_TABLE]
    rows = [
        {name: None for name in schema.fieldNames()},
        {name: None for name in schema.fieldNames()},
        {name: None for name in schema.fieldNames()},
        {name: None for name in schema.fieldNames()},
    ]
    base = {
        "metadata_table_key": "table-1",
        "environment_name": "dev",
        "store_type": "lakehouse",
        "layer": "raw",
        "schema_name": None,
        "table_name": "orders",
        "data_type": "string",
        "row_count": 10,
        "non_null_count": 10,
        "null_count": 0,
        "null_percent": 0.0,
        "distinct_count": 10,
        "distinct_percent": 100.0,
        "schema_fingerprint": "schema-1",
        "profiled_at": datetime(2026, 1, 1),
        "_committed_by": "tester",
        "_committed_at": datetime(2026, 1, 1),
        "_workspace_id": "workspace-1",
        "_workspace_name": "Workspace One",
        "_notebook_id": "notebook-1",
        "_notebook_name": "Notebook One",
        "_metadata_lakehouse_name": "metadata_lh",
        "_activity_id": "activity-1",
    }
    rows[0].update(base | {"metadata_column_key": "col-1", "column_name": "id"})
    rows[1].update(base | {"metadata_column_key": "col-1", "column_name": "id", "row_count": 20})
    rows[2].update(base | {"metadata_column_key": "col-2", "column_name": "name"})
    rows[3].update(base | {"environment_name": "prod", "metadata_column_key": "col-1", "column_name": "id"})
    profiled_df = spark_session.createDataFrame(rows, schema=schema)

    catalogue_df = _catalogue_dataframe_from_profiled(profiled_df)

    assert catalogue_df.columns == CATALOGUE_COLUMNS
    assert catalogue_df.count() == 3
    assert {row.environment_name for row in catalogue_df.collect()} == {"dev", "prod"}
    assert {row.metadata_column_key for row in catalogue_df.collect()} == {"col-1", "col-2"}


def test_lineage_schema_is_table_participation_contract():
    """Verify lineage keeps exactly one unprefixed runtime identity contract."""
    schema = metadata_table_schema_registry()["METADATA_DATA_LINEAGE"]
    assert schema.fieldNames() == [
        "lineage_event_id",
        "activity_id",
        "notebook_id",
        "notebook_name",
        "workspace_id",
        "workspace_name",
        "metadata_table_key",
        "schema_fingerprint",
        "profile_role",
        "profiled_at",
        "committed_by",
        "environment_name",
        "metadata_lakehouse_name",
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
    assert fields["lineage_event_id"].nullable is False
    assert fields["activity_id"].nullable is False
    assert fields["metadata_table_key"].nullable is False
    assert fields["schema_fingerprint"].nullable is False
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
    }
    assert obsolete.isdisjoint(schema.fieldNames())


def test_lineage_upsert_failure_does_not_append_duplicate(spark_session, monkeypatch, registered):
    """Verify failed lineage upserts are not converted to non-idempotent appends."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    monkeypatch.setattr(module, "build_profile_dataframe", lambda df: _profile_df(spark_session))

    def fail_upsert(*, lineage_df, config, env, spark_session):
        raise RuntimeError("merge failed")

    monkeypatch.setattr(module, "_upsert_lineage_event", fail_upsert)
    expected_key = _metadata_table_key("lakehouse", "raw", None, "customers")
    with pytest.raises(
        RuntimeError,
        match=f"Profile and catalogue registration succeeded but lineage registration failed.*{expected_key}.*source",
    ):
        profile_and_register_table(
            _source_df(spark_session),
            profile_role="source",
            target="raw",
            table_name="customers",
        )
    assert [write["table_name"] for write in registered] == [PROFILED_TABLE, CATALOGUE_TABLE]


def test_lineage_is_not_attempted_when_profiled_write_fails(spark_session, monkeypatch, registered):
    """Verify profiled evidence write failure stops before catalogue and lineage registration."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    monkeypatch.setattr(module, "build_profile_dataframe", lambda df: _profile_df(spark_session))

    def fail_profiled(*_args, **_kwargs):
        raise ValueError("profiled boom")

    monkeypatch.setattr(module, "write_lakehouse_table_core", fail_profiled)
    with pytest.raises(ValueError, match="profiled boom"):
        profile_and_register_table(
            _source_df(spark_session),
            profile_role="source",
            target="raw",
            table_name="customers",
        )


def test_catalogue_upsert_failure_does_not_fall_back_to_append(spark_session, monkeypatch, registered):
    """Verify failed catalogue upserts are not converted to append writes."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    monkeypatch.setattr(module, "build_profile_dataframe", lambda df: _profile_df(spark_session))

    def fail_catalogue_upsert(*, catalogue_df, config, env, spark_session):
        raise RuntimeError("catalogue merge failed")

    monkeypatch.setattr(module, "_upsert_catalogue_identities", fail_catalogue_upsert)
    with pytest.raises(RuntimeError, match="catalogue merge failed"):
        profile_and_register_table(
            _source_df(spark_session),
            profile_role="source",
            target="raw",
            table_name="customers",
        )
    assert [write["table_name"] for write in registered] == [PROFILED_TABLE]


def test_profile_and_register_table_uses_caller_frequency_profile_df_only_for_frequency(
    spark_session, monkeypatch, registered
):
    """Verify a caller frequency DataFrame affects only frequency evidence."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    source = spark_session.createDataFrame(
        [(i, "A" if i % 2 == 0 else "B") for i in range(20)], "id long, segment string"
    )
    frequency_source = spark_session.createDataFrame(
        [(0, "A", "extra"), (1, "A", "extra"), (2, "B", "extra")], "id long, segment string, extra string"
    )
    calls = {"profile_is_source": None, "frequency_df_is_frequency_source": None, "schema_df_is_source": []}
    original_schema_fingerprint = module._schema_fingerprint
    original_frequency_distribution = module.build_frequency_distribution_dataframe

    def schema_fingerprint(df):
        calls["schema_df_is_source"].append(df is source)
        return original_schema_fingerprint(df)

    def profile(df):
        calls["profile_is_source"] = df is source
        return spark_session.createDataFrame(
            [
                ("id", "bigint", 20, 20, 0, 0.0, 20, 100.0, None, None, "0", None, None, None, "19"),
                ("segment", "string", 20, 20, 0, 0.0, 2, 10.0, None, None, "A", None, None, None, "B"),
            ],
            "COLUMN_NAME string, DATA_TYPE string, ROW_COUNT long, NON_NULL_COUNT long, NULL_COUNT long, NULL_PERCENT double, DISTINCT_COUNT long, DISTINCT_PERCENT double, MEAN double, STDDEV double, MIN_VALUE string, PERCENTILE_25 double, MEDIAN double, PERCENTILE_75 double, MAX_VALUE string",
        )

    def frequency(df, *, columns, top_n):
        calls["frequency_df_is_frequency_source"] = df is frequency_source
        return original_frequency_distribution(df, columns=columns, top_n=top_n)

    monkeypatch.setattr(module, "_schema_fingerprint", schema_fingerprint)
    monkeypatch.setattr(module, "build_profile_dataframe", profile)
    monkeypatch.setattr(module, "build_frequency_distribution_dataframe", frequency)

    result = profile_and_register_table(
        source,
        profile_role="source",
        target="raw",
        table_name="customers",
        frequency_columns=["segment"],
        frequency_profile_df=frequency_source,
    )

    rows = {row.column_name: row.asDict() for row in result.collect()}
    frequency_json = json.loads(rows["segment"]["frequency_json"])
    assert calls["profile_is_source"] is True
    assert calls["frequency_df_is_frequency_source"] is True
    assert calls["schema_df_is_source"] and all(calls["schema_df_is_source"])
    assert rows["segment"]["row_count"] == 20
    assert frequency_json["source_row_count"] == 20
    assert frequency_json["profiled_row_count"] == 3
    assert frequency_json["profiled_non_null_count"] == 3
    assert frequency_json["frequency_scope"] == "caller_provided"
    assert [value["value"] for value in frequency_json["values"]] == ["A", "B"]
    assert {write["table_name"] for write in registered} == {PROFILED_TABLE, CATALOGUE_TABLE, "METADATA_DATA_LINEAGE"}
    assert registered[1]["df"].select("table_name").distinct().collect()[0].table_name == "customers"


def test_profile_and_register_table_default_frequency_scope_uses_full_source(spark_session, registered):
    """Verify omitting frequency_profile_df preserves full-source frequency profiling."""
    source = spark_session.createDataFrame(
        [(i, "A" if i % 2 == 0 else "B") for i in range(8)], "id long, segment string"
    )

    result = profile_and_register_table(
        source,
        profile_role="source",
        target="raw",
        table_name="customers",
        frequency_columns=["segment"],
    )

    rows = {row.column_name: row.asDict() for row in result.collect()}
    frequency_json = json.loads(rows["segment"]["frequency_json"])
    assert frequency_json["source_row_count"] == 8
    assert frequency_json["profiled_row_count"] == 8
    assert frequency_json["profiled_non_null_count"] == 8
    assert frequency_json["frequency_scope"] == "full_source"


def test_profile_and_register_table_frequency_profile_df_missing_selected_column_raises(spark_session, registered):
    """Verify caller-provided frequency DataFrames must contain selected frequency columns."""
    source = spark_session.createDataFrame([(1, "A")], "id long, segment string")
    frequency_source = spark_session.createDataFrame([(1, "extra")], "id long, extra string")

    with pytest.raises(ValueError, match="frequency_profile_df is missing selected frequency columns: segment"):
        profile_and_register_table(
            source,
            profile_role="source",
            target="raw",
            table_name="customers",
            frequency_columns=["segment"],
            frequency_profile_df=frequency_source,
        )


def test_profile_and_register_table_empty_frequency_columns_does_not_validate_frequency_profile_df(
    spark_session, monkeypatch, registered
):
    """Verify frequency_columns=[] skips frequency profiling without touching caller frequency input."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    calls = {"validate": 0, "frequency": 0}

    def validate(*_args, **_kwargs):
        calls["validate"] += 1
        raise AssertionError("frequency_profile_df should not be validated")

    def frequency(*_args, **_kwargs):
        calls["frequency"] += 1
        raise AssertionError("frequency profiling should not run")

    monkeypatch.setattr(module, "_validate_frequency_profile_dataframe", validate)
    monkeypatch.setattr(module, "build_frequency_distribution_dataframe", frequency)

    result = profile_and_register_table(
        _source_df(spark_session),
        profile_role="source",
        target="raw",
        table_name="customers",
        frequency_columns=[],
        frequency_profile_df=object(),
    )

    assert calls == {"validate": 0, "frequency": 0}
    assert result.where("frequency_json is not null").count() == 0


def test_profile_and_register_table_automatic_selection_uses_full_profile_with_frequency_profile_df(
    spark_session, monkeypatch, registered
):
    """Verify automatic cardinality filtering still uses the full statistical profile."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    source = _source_df(spark_session)
    frequency_source = spark_session.createDataFrame([("A", "US"), ("B", "GB")], "customer_type string, country string")
    calls = {"frequency_columns": None}

    def profile(df):
        assert df is source
        return _profile_df(spark_session)

    original_frequency_distribution = module.build_frequency_distribution_dataframe

    def frequency(df, *, columns, top_n):
        assert df is frequency_source
        calls["frequency_columns"] = columns
        return original_frequency_distribution(df, columns=columns, top_n=top_n)

    monkeypatch.setattr(module, "build_profile_dataframe", profile)
    monkeypatch.setattr(module, "build_frequency_distribution_dataframe", frequency)

    result = profile_and_register_table(
        source,
        profile_role="source",
        target="raw",
        table_name="customers",
        frequency_profile_df=frequency_source,
    )

    rows = {row.column_name: row.asDict() for row in result.collect()}
    assert calls["frequency_columns"] == ["customer_type"]
    assert json.loads(rows["customer_type"]["frequency_json"])["frequency_scope"] == "caller_provided"
    assert json.loads(rows["id"]["frequency_json"])["reason"] == "high_cardinality"


def test_validate_frequency_profile_dataframe_rejects_incompatible_session():
    """Verify safely detectable incompatible Spark sessions fail clearly."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")

    class FakeSchema:
        fields = []

    class FakeDataFrame:
        schema = FakeSchema()

        def __init__(self, session):
            self.sparkSession = session

    with pytest.raises(ValueError, match="frequency_profile_df must use the same Spark session as df"):
        module._validate_frequency_profile_dataframe(FakeDataFrame(object()), FakeDataFrame(object()), [])
