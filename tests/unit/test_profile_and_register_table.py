"""Tests for profile_and_register_table orchestration."""

from __future__ import annotations

import importlib
import inspect
import json
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from types import ModuleType

import pytest

from fabricops_kit.config import FabricStore
from fabricops_kit.config.metadata_keys import (
    _build_metadata_column_key as _metadata_column_key,
    _build_metadata_table_key as _metadata_table_key,
)
from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
from fabricops_kit.pipeline import profile_and_register_table as public_profile_and_register_table
from fabricops_kit.pipeline import profile_frequency_distribution
from fabricops_kit.pipeline.profile_and_register_table import (
    CATALOGUE_COLUMNS,
    CATALOGUE_TABLE,
    PROFILED_COLUMNS,
    PROFILED_FREQUENCY_TABLE,
    PROFILED_TABLE,
    _catalogue_dataframe_from_profiled,
    _replace_frequency_rows,
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

    def replace_frequency(*, frequency_df, profiled_df, config, env, spark_session):
        writes.append(
            {
                "df": frequency_df,
                "profiled_df": profiled_df,
                "table_name": "METADATA_DATA_PROFILED_FREQUENCY",
                "target": "metadata",
                "schema": None,
                "context": {"config": config, "env": env},
                "mode": "replace",
            }
        )

    monkeypatch.setattr(module, "write_lakehouse_table_core", write)
    monkeypatch.setattr(module, "_replace_frequency_rows", replace_frequency)
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
    """Verify registration uses the exact-only shared statistical profiler."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")

    assert module.build_profile_dataframe is not None
    assert not hasattr(module, "profile_dataframe")
    assert str(inspect.signature(module.build_profile_dataframe)) == "(df, *, exclude_columns=None)"
    shared_source = inspect.getsource(module.build_profile_dataframe)
    assert "count_distinct" in shared_source
    assert "approx" + "_count_distinct" not in shared_source


def test_profile_registration_call_flow_records_authoritative_frequency_callable():
    """Verify registration directly reuses the required public frequency implementation."""
    payload = json.loads(Path("docs/reference/_data/public-function-call-flows.json").read_text(encoding="utf-8"))
    flow = next(row for row in payload["public_functions"] if row["function_name"] == "profile_and_register_table")
    direct_callees = {
        row["qualified_name"]: row for row in flow["flow"] if row["parent_qualified_name"] == flow["qualified_name"]
    }

    assert "fabricops_kit.pipeline.profile_dataframe.profile_dataframe" not in direct_callees
    assert "fabricops_kit.pipeline.shared.build_profile_dataframe" in direct_callees
    assert "Type 1" not in direct_callees["fabricops_kit.pipeline.shared.build_profile_dataframe"]["violation_types"]

    frequency_callable = "fabricops_kit.pipeline.profile_frequency_distribution.profile_frequency_distribution"
    assert frequency_callable in direct_callees
    assert "Type 1" in direct_callees[frequency_callable]["violation_types"]
    assert "fabricops_kit.pipeline.shared.build_frequency_distribution_dataframe" not in direct_callees


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


def test_profile_and_register_table_empty_frequency_selection_writes_compact_parent_only(
    spark_session, monkeypatch, registered
):
    """Verify an empty selection emits no child rows and retains compact parents."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    monkeypatch.setattr(
        module,
        "profile_frequency_distribution",
        lambda *_args, **_kwargs: pytest.fail("empty selection must not invoke frequency profiling"),
    )

    result = profile_and_register_table(
        _source_df(spark_session),
        profile_role="source",
        target="raw",
        table_name="customers",
        frequency_columns=[],
    )

    assert "frequency_json" not in result.columns
    frequency_write = next(write for write in registered if write["table_name"] == "METADATA_DATA_PROFILED_FREQUENCY")
    assert frequency_write["df"] is None
    assert frequency_write["profiled_df"] is result


def test_profile_and_register_table_writes_normalized_frequency_rows(
    spark_session, monkeypatch, registered
):
    """Verify normalized mapping, stable keys, timestamps, audit fields, and null values."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    source = _source_df(spark_session)
    calls = []

    def frequency(df, *, columns, top_n):
        calls.append((df, columns, top_n))
        return _frequency_df(spark_session)

    monkeypatch.setattr(module, "profile_frequency_distribution", frequency)
    result = profile_and_register_table(
        source,
        profile_role="source",
        target="silver",
        schema="dbo",
        table_name="customers_clean",
        frequency_columns=["customer_type", "country"],
        frequency_top_n=5,
    )

    assert calls == [(source, ["customer_type", "country"], 5)]
    assert "frequency_json" not in result.columns
    frequency_write = next(write for write in registered if write["table_name"] == "METADATA_DATA_PROFILED_FREQUENCY")
    child = frequency_write["df"]
    expected_columns = metadata_table_schema_registry()["METADATA_DATA_PROFILED_FREQUENCY"].fieldNames()
    assert child.columns == expected_columns
    assert "COLUMN_NAME" not in child.columns
    assert "DATA_TYPE" not in child.columns
    parent = {row.column_name: row.asDict() for row in result.collect()}
    rows = {(row.metadata_column_key, row.value): row.asDict() for row in child.collect()}
    country_key = parent["country"]["metadata_column_key"]
    customer_key = parent["customer_type"]["metadata_column_key"]
    assert rows[(customer_key, "A")]["frequency_count"] == 2
    assert rows[(customer_key, "A")]["frequency_percent"] == 66.667
    assert rows[(customer_key, "A")]["frequency_rank"] == 1
    assert rows[(country_key, None)]["profiled_row_count"] == 3
    assert rows[(country_key, None)]["profiled_non_null_count"] == 2
    assert rows[(country_key, None)]["profiled_at"] == parent["country"]["profiled_at"]
    assert set(AUDIT_COLUMNS).issubset(child.columns)


def test_profile_and_register_table_automatic_skips_produce_no_fake_child_rows(
    spark_session, monkeypatch, registered
):
    """Verify high-cardinality and all-null automatic columns remain parent-only."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    source = spark_session.createDataFrame(
        [(1, "A", None), (2, "A", None), (3, "B", None)],
        "identifier long, category string, empty string",
    )
    selected = []

    def frequency(df, *, columns, top_n):
        selected.extend(columns)
        return profile_frequency_distribution(df, columns=columns, top_n=top_n)

    monkeypatch.setattr(module, "profile_frequency_distribution", frequency)
    result = profile_and_register_table(
        source, profile_role="source", target="raw", table_name="automatic"
    )

    assert selected == ["category"]
    assert result.count() == 3
    child = next(write["df"] for write in registered if write["table_name"] == "METADATA_DATA_PROFILED_FREQUENCY")
    parent_keys = {row.column_name: row.metadata_column_key for row in result.collect()}
    child_keys = {row.metadata_column_key for row in child.collect()}
    assert child_keys == {parent_keys["category"]}


def test_profile_and_register_table_explicit_frequency_overrides_threshold(
    spark_session, monkeypatch, registered
):
    """Verify explicit selections continue to override automatic cardinality filtering."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    source = spark_session.createDataFrame([(1,), (2,), (3,)], "identifier long")
    selected = []

    def frequency(df, *, columns, top_n):
        selected.extend(columns)
        return profile_frequency_distribution(df, columns=columns, top_n=top_n)

    monkeypatch.setattr(module, "profile_frequency_distribution", frequency)
    profile_and_register_table(
        source,
        profile_role="source",
        target="raw",
        table_name="explicit",
        frequency_columns=["identifier"],
        frequency_max_distinct_percent=0.0,
    )

    assert selected == ["identifier"]
    child = next(write["df"] for write in registered if write["table_name"] == "METADATA_DATA_PROFILED_FREQUENCY")
    assert child.count() == 3


def test_frequency_replacement_is_scoped_to_exact_column_snapshot(monkeypatch):
    """Verify history remains while obsolete rows in one exact snapshot are replaced."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    stored = []

    class Frame:
        def __init__(self, rows):
            self.rows = rows

        def select(self, *names):
            return Frame([{name: row[name] for name in names} for row in self.rows])

        def dropDuplicates(self):  # noqa: N802
            unique = {(row["metadata_column_key"], row["profiled_at"]): row for row in self.rows}
            return Frame(list(unique.values()))

        def alias(self, _name):
            return self

    class Target:
        def alias(self, _name):
            return self

        def merge(self, snapshots, condition):
            assert condition == (
                "target.metadata_column_key = source.metadata_column_key "
                "AND target.profiled_at = source.profiled_at"
            )
            self.snapshots = {
                (row["metadata_column_key"], row["profiled_at"]) for row in snapshots.rows
            }
            return self

        def whenMatchedDelete(self):  # noqa: N802
            return self

        def execute(self):
            stored[:] = [
                row
                for row in stored
                if (row["metadata_column_key"], row["profiled_at"]) not in self.snapshots
            ]

    class DeltaTable:
        @staticmethod
        def forPath(_spark_session, path):  # noqa: N802
            assert path == "/metadata/frequency"
            return Target()

    delta_module = ModuleType("delta")
    delta_tables_module = ModuleType("delta.tables")
    delta_tables_module.DeltaTable = DeltaTable
    monkeypatch.setitem(sys.modules, "delta", delta_module)
    monkeypatch.setitem(sys.modules, "delta.tables", delta_tables_module)
    monkeypatch.setattr(
        module,
        "resolve_configured_lakehouse_table",
        lambda *_args, **_kwargs: (None, None, None, "/metadata/frequency"),
    )
    monkeypatch.setattr(module, "configured_lakehouse_schema", lambda *_args: None)
    monkeypatch.setattr(
        module,
        "write_lakehouse_table_core",
        lambda frame, *_args, **_kwargs: stored.extend(frame.rows),
    )

    def replace(profiled_at, values):
        parent = Frame([{"metadata_column_key": "column-1", "profiled_at": profiled_at}])
        child = None if values is None else Frame(
            [
                {"metadata_column_key": "column-1", "profiled_at": profiled_at, "value": value}
                for value in values
            ]
        )
        _replace_frequency_rows(
            frequency_df=child,
            profiled_df=parent,
            config=object(),
            env="dev",
            spark_session=object(),
        )

    first_at = datetime(2026, 1, 1)
    second_at = datetime(2026, 1, 2)
    replace(first_at, ["old-history"])
    replace(second_at, ["obsolete", "current"])
    replace(second_at, None)
    assert stored == [
        {"metadata_column_key": "column-1", "profiled_at": first_at, "value": "old-history"}
    ]
    replace(second_at, ["replacement"])

    assert {(row["profiled_at"], row["value"]) for row in stored} == {
        (first_at, "old-history"),
        (second_at, "replacement"),
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
    """Verify lineage uses only the shared audit contract for runtime context."""
    schema = metadata_table_schema_registry()["METADATA_DATA_LINEAGE"]
    assert schema.fieldNames() == [
        "lineage_event_id",
        "metadata_table_key",
        "schema_fingerprint",
        "profile_role",
        "profiled_at",
        "environment_name",
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
    assert fields["metadata_table_key"].nullable is False
    assert fields["schema_fingerprint"].nullable is False
    assert fields["profile_role"].nullable is False
    removed_context = {
        "activity_id",
        "notebook_id",
        "notebook_name",
        "workspace_id",
        "workspace_name",
        "committed_by",
        "metadata_lakehouse_name",
    }
    assert removed_context.isdisjoint(schema.fieldNames())
    assert all(fields[name].nullable is False for name in AUDIT_COLUMNS)
    assert fields["profiled_at"].nullable is False
    assert fields["_committed_at"].nullable is False
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


def test_lineage_writer_uses_audit_context_and_activity_for_idempotent_identity(spark_session, monkeypatch):
    """Verify lineage writes canonical audit context and a stable activity-based event ID."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    profiled_at = datetime(2026, 1, 1, 10, 30)
    committed_at = datetime(2026, 1, 1, 10, 31)
    audit = {
        "_committed_by": "tester",
        "_committed_at": committed_at,
        "_workspace_id": "workspace-1",
        "_workspace_name": "Workspace One",
        "_notebook_id": "notebook-1",
        "_notebook_name": "Notebook One",
        "_metadata_lakehouse_name": "metadata_lh",
        "_activity_id": "activity-1",
    }
    captured = []
    monkeypatch.setattr(module, "build_runtime_audit_fields", lambda **_kwargs: audit)
    monkeypatch.setattr(module, "_upsert_lineage_event", lambda **kwargs: captured.append(kwargs["lineage_df"]))

    arguments = {
        "metadata_table_key": "lakehouse|raw||customers",
        "schema_fingerprint": "schema-1",
        "profile_role": "source",
        "profiled_at": profiled_at,
        "config": object(),
        "env": "dev",
        "context": {},
        "spark_session": spark_session,
    }
    module._write_lineage_participation(**arguments)
    module._write_lineage_participation(**arguments)

    rows = [dataframe.collect()[0].asDict() for dataframe in captured]
    expected_event_id = module._lineage_event_id(
        activity_id=audit["_activity_id"],
        metadata_table_key=arguments["metadata_table_key"],
        schema_fingerprint=arguments["schema_fingerprint"],
        profile_role=arguments["profile_role"],
    )
    assert len(rows) == 2
    assert rows[0] == rows[1]
    assert rows[0]["lineage_event_id"] == expected_event_id
    assert set(rows[0]) == set(metadata_table_schema_registry()["METADATA_DATA_LINEAGE"].fieldNames())
    assert all(rows[0][name] == value for name, value in audit.items())
    assert rows[0]["profiled_at"] == profiled_at
    assert rows[0]["_committed_at"] == committed_at
    assert rows[0]["profiled_at"] != rows[0]["_committed_at"]


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
    assert [write["table_name"] for write in registered] == [
        PROFILED_TABLE,
        PROFILED_FREQUENCY_TABLE,
        CATALOGUE_TABLE,
    ]


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
    assert [write["table_name"] for write in registered] == [PROFILED_TABLE, PROFILED_FREQUENCY_TABLE]


def test_profile_and_register_table_uses_caller_frequency_profile_df_only_for_frequency(
    spark_session, monkeypatch, registered
):
    """Verify alternate frequency input does not change complete-source parent statistics."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    source = spark_session.createDataFrame(
        [(i, "A" if i % 2 == 0 else "B") for i in range(20)], "id long, segment string"
    )
    frequency_source = spark_session.createDataFrame([(100, "A"), (101, "A"), (102, "B")], "id long, segment string")
    seen = []

    def frequency(df, *, columns, top_n):
        seen.append(df)
        return profile_frequency_distribution(df, columns=columns, top_n=top_n)

    monkeypatch.setattr(module, "profile_frequency_distribution", frequency)
    result = profile_and_register_table(
        source,
        profile_role="source",
        target="raw",
        table_name="customers",
        frequency_columns=["segment"],
        frequency_profile_df=frequency_source,
    )

    assert seen == [frequency_source]
    assert {row.column_name: row.row_count for row in result.collect()} == {"id": 20, "segment": 20}
    child = next(write["df"] for write in registered if write["table_name"] == "METADATA_DATA_PROFILED_FREQUENCY")
    assert {row.profiled_row_count for row in child.collect()} == {3}


def test_profile_and_register_table_frequency_profile_df_missing_selected_column_raises(spark_session, registered):
    """Verify alternate frequency input must include explicitly selected columns."""
    source = _source_df(spark_session)
    alternate = source.select("id")
    with pytest.raises(ValueError, match="missing selected frequency columns: country"):
        profile_and_register_table(
            source,
            profile_role="source",
            target="raw",
            table_name="customers",
            frequency_columns=["country"],
            frequency_profile_df=alternate,
        )


def test_profile_and_register_table_empty_selection_does_not_validate_frequency_profile_df(
    spark_session, monkeypatch, registered
):
    """Verify disabled frequency profiling ignores an alternate DataFrame schema."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    monkeypatch.setattr(
        module,
        "profile_frequency_distribution",
        lambda *_args, **_kwargs: pytest.fail("frequency profiler must not run"),
    )
    result = profile_and_register_table(
        _source_df(spark_session),
        profile_role="source",
        target="raw",
        table_name="customers",
        frequency_columns=[],
        frequency_profile_df=spark_session.createDataFrame([(1,)], "other long"),
    )
    assert result.count() == 3


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
