"""Tests for Stage 2 profile_and_register_table orchestration."""
# ruff: noqa: D103

from __future__ import annotations

import importlib
import inspect
import json
import sys
from datetime import datetime
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from fabricops_kit.config import FabricStore
from fabricops_kit.config.shared import build_column_id, build_table_id
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


def test_logical_table_and_column_ids_are_environment_independent():
    """Stable asset IDs depend on logical coordinates, not runtime environment."""
    dev_id = build_table_id("lakehouse", "silver", "dbo", "orders")
    prod_id = build_table_id("lakehouse", "silver", "dbo", "orders")

    assert dev_id == prod_id
    assert dev_id != build_table_id("warehouse", "silver", "dbo", "orders")
    assert dev_id != build_table_id("lakehouse", "gold", "dbo", "orders")
    assert dev_id != build_table_id("lakehouse", "silver", "sales", "orders")
    assert dev_id != build_table_id("lakehouse", "silver", "dbo", "customers")
    assert build_column_id(dev_id, "Order_ID") == build_column_id(prod_id, " order_id ")
    assert build_column_id(dev_id, "order_id") != build_column_id(dev_id, "amount")


def test_schema_fingerprint_remains_internal_for_deferred_contract_support(spark_session):
    """Keep the legacy schema helper stable without persisting it in Stage 2 facts."""
    from pyspark.sql import types as T

    base_schema = T.StructType(
        [T.StructField("order_id", T.LongType(), False), T.StructField("amount", T.DoubleType(), True)]
    )
    dev = spark_session.createDataFrame([(1, 1.0)], schema=base_schema)
    prod = spark_session.createDataFrame([(99, 900.0)], schema=base_schema)
    assert _schema_fingerprint(dev) == _schema_fingerprint(prod)
    assert _schema_fingerprint(dev) != _schema_fingerprint(
        spark_session.createDataFrame([(1, "1.0")], "order_id long, amount string")
    )


def _source_df(spark_session):
    return spark_session.createDataFrame(
        [(1, "A", "US"), (2, "A", None), (3, "B", "GB")],
        "id long, customer_type string, country string",
    )


def _profile_df(spark_session):
    return spark_session.createDataFrame(
        [
            ("id", "bigint", 3, 3, 0, 0.0, 3, 100.0, 2.0, 1.0, "1", 1.0, 2.0, 3.0, "3"),
            ("customer_type", "string", 3, 3, 0, 0.0, 2, 66.667, None, None, "A", None, None, None, "B"),
            ("country", "string", 3, 2, 1, 33.333, 2, 66.667, None, None, "GB", None, None, None, "US"),
        ],
        "COLUMN_NAME string, DATA_TYPE string, ROW_COUNT long, NON_NULL_COUNT long, NULL_COUNT long, "
        "NULL_PERCENT double, DISTINCT_COUNT long, DISTINCT_PERCENT double, MEAN double, STDDEV double, "
        "MIN_VALUE string, PERCENTILE_25 double, MEDIAN double, PERCENTILE_75 double, MAX_VALUE string",
    )


def _frequency_df(spark_session):
    return spark_session.createDataFrame(
        [
            ("customer_type", "string", "B", 1, 33.333, 2, 3, 3),
            ("country", "string", None, 1, 33.333, 2, 3, 2),
            ("customer_type", "string", "A", 2, 66.667, 1, 3, 3),
            ("country", "string", "US", 1, 33.333, 1, 3, 2),
        ],
        "COLUMN_NAME string, DATA_TYPE string, VALUE string, FREQUENCY_COUNT long, FREQUENCY_PERCENT double, "
        "FREQUENCY_RANK int, PROFILED_ROW_COUNT long, PROFILED_NON_NULL_COUNT long",
    )


@pytest.fixture
def registered(monkeypatch):
    """Patch Fabric context and persistence seams while retaining Spark transformations."""
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
        writes.append({"df": df, "table_name": table_name, "mode": mode})

    def upsert_catalogue(*, catalogue_df, config, env, spark_session):
        writes.append({"df": catalogue_df, "table_name": CATALOGUE_TABLE, "mode": "upsert"})

    def upsert_lineage(*, lineage_df, config, env, spark_session):
        writes.append({"df": lineage_df, "table_name": "METADATA_DATA_LINEAGE", "mode": "upsert"})

    def replace_frequency(*, frequency_df, profiled_df, config, env, spark_session):
        writes.append(
            {
                "df": frequency_df,
                "profiled_df": profiled_df,
                "table_name": PROFILED_FREQUENCY_TABLE,
                "mode": "replace",
            }
        )

    monkeypatch.setattr(module, "write_lakehouse_table_core", write)
    monkeypatch.setattr(module, "_replace_frequency_rows", replace_frequency)
    monkeypatch.setattr(module, "_upsert_catalogue_identities", upsert_catalogue)
    monkeypatch.setattr(module, "_upsert_lineage_event", upsert_lineage)
    return writes


def test_profile_and_register_table_is_public_export():
    assert public_profile_and_register_table is profile_and_register_table


def test_profile_and_register_table_imports_shared_profilers_directly():
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    assert module.build_profile_dataframe is not None
    assert module.build_frequency_distribution_dataframe is not None
    assert not hasattr(module, "profile_dataframe")


def test_profile_registration_call_flow_records_shared_frequency_implementation():
    payload = json.loads(Path("docs/reference/_data/public-function-call-flows.json").read_text(encoding="utf-8"))
    flow = next(row for row in payload["public_functions"] if row["function_name"] == "profile_and_register_table")
    direct_callees = {
        row["qualified_name"]: row for row in flow["flow"] if row["parent_qualified_name"] == flow["qualified_name"]
    }
    assert "fabricops_kit.pipeline.shared.build_profile_dataframe" in direct_callees
    assert "fabricops_kit.pipeline.shared.build_frequency_distribution_dataframe" in direct_callees


def test_profile_and_register_table_signature_requires_profile_role():
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


def test_resolved_identity_uses_active_environment_and_configured_lakehouse(monkeypatch):
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    store = FabricStore("dev", "workspace", "item", "Unified", "lakehouse", True, "dbo")
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {"env": "dev"}))
    monkeypatch.setattr(module, "get_store", lambda config, env, target: store)
    identity = _resolve_physical_identity(
        profile_role=" Source ", target=" Unified ", schema=None, table_name="customers"
    )
    assert identity[:5] == ("source", "unified", "customers", "dbo", "lakehouse")
    assert identity[6] == "dev"


def test_resolved_identity_uses_configured_warehouse_default(monkeypatch):
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
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {"env": "dev"}))
    monkeypatch.setattr(module, "get_store", lambda config, env, target: store)
    with pytest.raises(ValueError, match=message):
        _resolve_physical_identity(profile_role="source", target="source", schema=None, table_name="orders")


@pytest.mark.parametrize("role", ["source", "target", " Source ", " TARGET "])
def test_profile_and_register_table_accepts_source_and_target_roles(spark_session, monkeypatch, registered, role):
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    monkeypatch.setattr(module, "build_profile_dataframe", lambda df: _profile_df(spark_session))
    result = profile_and_register_table(
        _source_df(spark_session), profile_role=role, target="raw", table_name="customers"
    )
    assert "profile_role" not in result.columns
    lineage = next(write["df"] for write in registered if write["table_name"] == "METADATA_DATA_LINEAGE")
    assert lineage.collect()[0].pipeline_role == role.strip().lower()


@pytest.mark.parametrize(("target", "kind", "schema"), [("silver", "lakehouse", None), ("warehouse", "warehouse", "dbo")])
def test_profile_and_register_table_derives_physical_identity_into_catalogue(
    spark_session, monkeypatch, registered, target, kind, schema
):
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    monkeypatch.setattr(module, "build_profile_dataframe", lambda df: _profile_df(spark_session))
    result = profile_and_register_table(
        _source_df(spark_session),
        profile_role="target",
        target=target,
        schema=schema,
        table_name="customers_clean",
    )
    assert {"table_id", "column_id", "environment_name"}.issubset(result.columns)
    assert {"store_type", "layer", "schema_name", "table_name", "column_name"}.isdisjoint(result.columns)
    catalogue = next(write["df"] for write in registered if write["table_name"] == CATALOGUE_TABLE)
    table_row = next(row for row in catalogue.collect() if row.metadata_level == "table")
    assert (table_row.environment_name, table_row.store_type, table_row.layer, table_row.schema_name) == (
        "dev", kind, target, schema or ""
    )


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
    params = {"profile_role": "source", "target": "raw", "schema": None, "table_name": "customers"}
    params.update(kwargs)
    with pytest.raises(ValueError, match=message):
        profile_and_register_table(_source_df(spark_session), **params)


@pytest.mark.parametrize("threshold", [-0.1, 100.1, float("nan"), float("inf"), -float("inf")])
def test_profile_and_register_table_rejects_invalid_frequency_threshold(spark_session, registered, threshold):
    with pytest.raises(ValueError, match="frequency_max_distinct_percent must be finite and between 0.0 and 100.0"):
        profile_and_register_table(
            _source_df(spark_session),
            profile_role="source",
            target="raw",
            table_name="customers",
            frequency_max_distinct_percent=threshold,
        )


def test_profile_and_register_table_empty_frequency_selection_writes_compact_profile_only(
    spark_session, monkeypatch, registered
):
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    monkeypatch.setattr(
        module,
        "build_frequency_distribution_dataframe",
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
    frequency_write = next(write for write in registered if write["table_name"] == PROFILED_FREQUENCY_TABLE)
    assert frequency_write["df"] is None
    assert frequency_write["profiled_df"] is result


def test_profile_and_register_table_writes_frequency_rows_for_same_logical_profile(
    spark_session, monkeypatch, registered
):
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    source = _source_df(spark_session)
    monkeypatch.setattr(module, "build_frequency_distribution_dataframe", lambda *_args, **_kwargs: _frequency_df(spark_session))
    result = profile_and_register_table(
        source,
        profile_role="source",
        target="silver",
        schema="dbo",
        table_name="customers_clean",
        frequency_columns=["customer_type", "country"],
        frequency_top_n=5,
    )
    child = next(write["df"] for write in registered if write["table_name"] == PROFILED_FREQUENCY_TABLE)
    assert child.columns == metadata_table_schema_registry()[PROFILED_FREQUENCY_TABLE].fieldNames()
    assert {"table_id", "column_id", "environment_name"}.isdisjoint(child.columns)
    parent_by_profile = {row.profile_id: row.asDict() for row in result.collect()}
    assert {row.profile_id for row in child.collect()} <= set(parent_by_profile)
    assert {row.profile_snapshot_id for row in child.collect()} == {row.profile_snapshot_id for row in result.collect()}
    for row in child.collect():
        assert row.profiled_at == parent_by_profile[row.profile_id]["profiled_at"]
    assert set(AUDIT_COLUMNS).issubset(child.columns)


def test_profile_and_register_table_automatic_skips_high_cardinality_frequency(
    spark_session, monkeypatch, registered
):
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    source = spark_session.createDataFrame(
        [(1, "A", None), (2, "A", None), (3, "B", None)],
        "identifier long, category string, empty string",
    )
    selected = []

    def frequency(df, *, columns, top_n):
        selected.extend(columns)
        return profile_frequency_distribution(df, columns=columns, top_n=top_n)

    monkeypatch.setattr(module, "build_frequency_distribution_dataframe", frequency)
    result = profile_and_register_table(source, profile_role="source", target="raw", table_name="automatic")
    assert selected == ["category"]
    child = next(write["df"] for write in registered if write["table_name"] == PROFILED_FREQUENCY_TABLE)
    category_id = build_column_id(result.collect()[0].table_id, "category")
    category_profile_ids = {row.profile_id for row in result.collect() if row.column_id == category_id}
    assert {row.profile_id for row in child.collect()} == category_profile_ids


def test_frequency_replacement_is_scoped_to_profile_snapshot(monkeypatch):
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    stored = []

    class Frame:
        def __init__(self, rows): self.rows = rows
        def select(self, *names): return Frame([{name: row[name] for name in names} for row in self.rows])
        def dropDuplicates(self):  # noqa: N802
            unique = {row["profile_snapshot_id"]: row for row in self.rows}
            return Frame(list(unique.values()))
        def alias(self, _name): return self

    class Target:
        def alias(self, _name): return self
        def merge(self, snapshots, condition):
            assert condition == "target.profile_snapshot_id = source.profile_snapshot_id"
            self.snapshots = {row["profile_snapshot_id"] for row in snapshots.rows}
            return self
        def whenMatchedDelete(self):  # noqa: N802
            return self
        def execute(self):
            stored[:] = [row for row in stored if row["profile_snapshot_id"] not in self.snapshots]

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
    monkeypatch.setattr(module, "write_lakehouse_table_core", lambda frame, *_args, **_kwargs: stored.extend(frame.rows))

    def replace(snapshot, values):
        parent = Frame([{"profile_snapshot_id": snapshot}])
        child = None if values is None else Frame(
            [{"profile_snapshot_id": snapshot, "value": value} for value in values]
        )
        _replace_frequency_rows(
            frequency_df=child, profiled_df=parent, config=object(), env="dev", spark_session=object()
        )

    replace("snapshot-1", ["history"])
    replace("snapshot-2", ["obsolete"])
    replace("snapshot-2", ["replacement"])
    assert stored == [
        {"profile_snapshot_id": "snapshot-1", "value": "history"},
        {"profile_snapshot_id": "snapshot-2", "value": "replacement"},
    ]


def test_profiled_schema_matches_stage2_contract():
    assert metadata_table_schema_registry()[PROFILED_TABLE].fieldNames() == PROFILED_COLUMNS
    assert PROFILED_COLUMNS[:5] == [
        "profile_id", "profile_snapshot_id", "table_id", "column_id", "environment_name"
    ]
    assert {
        "metadata_table_key", "metadata_column_key", "store_type", "layer", "schema_name",
        "table_name", "column_name", "schema_fingerprint", "profile_role",
    }.isdisjoint(PROFILED_COLUMNS)


def test_catalogue_schema_is_environment_aware_asset_contract():
    assert metadata_table_schema_registry()[CATALOGUE_TABLE].fieldNames() == CATALOGUE_COLUMNS
    assert CATALOGUE_COLUMNS[:12] == [
        "metadata_level", "table_id", "column_id", "environment_name", "store_type", "layer",
        "schema_name", "table_name", "column_name", "first_profiled_at", "last_profiled_at", "is_active",
    ]
    assert {"metadata_id", "metadata_key", "metadata_table_key", "metadata_column_key"}.isdisjoint(CATALOGUE_COLUMNS)


def test_catalogue_dataframe_contains_table_and_column_assets(spark_session, monkeypatch, registered):
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    monkeypatch.setattr(module, "build_profile_dataframe", lambda df: _profile_df(spark_session))
    source = _source_df(spark_session)
    profiled = profile_and_register_table(
        source, profile_role="source", target="raw", table_name="customers", frequency_columns=[]
    )
    catalogue = next(write["df"] for write in registered if write["table_name"] == CATALOGUE_TABLE)
    rows = catalogue.collect()
    assert len(rows) == 4
    assert [row.metadata_level for row in rows].count("table") == 1
    assert [row.metadata_level for row in rows].count("column") == 3
    table_id = profiled.collect()[0].table_id
    assert {row.table_id for row in rows} == {table_id}
    assert {row.environment_name for row in rows} == {"dev"}


def test_catalogue_builder_requires_physical_identity_explicitly(spark_session):
    source = _source_df(spark_session)
    schema = metadata_table_schema_registry()[PROFILED_TABLE]
    table_id = build_table_id("lakehouse", "raw", None, "customers")
    rows = []
    for field in source.schema.fields:
        row = {name: None for name in schema.fieldNames()}
        row.update(
            {
                "profile_id": f"profile-{field.name}",
                "profile_snapshot_id": "snapshot-1",
                "table_id": table_id,
                "column_id": build_column_id(table_id, field.name),
                "environment_name": "dev",
                "data_type": field.dataType.simpleString(),
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
        )
        rows.append(row)
    profiled = spark_session.createDataFrame(rows, schema=schema)
    catalogue = _catalogue_dataframe_from_profiled(
        profiled,
        source_df=source,
        store_type="lakehouse",
        layer="raw",
        schema_name=None,
        table_name="customers",
    )
    assert catalogue.columns == CATALOGUE_COLUMNS
    assert catalogue.count() == 4


def test_lineage_schema_is_pipeline_participation_contract():
    fields = metadata_table_schema_registry()["METADATA_DATA_LINEAGE"].fieldNames()
    assert fields[:6] == [
        "lineage_id", "table_id", "profile_snapshot_id", "environment_name", "pipeline_role", "recorded_at"
    ]
    assert {"lineage_event_id", "metadata_table_key", "schema_fingerprint", "profile_role", "profiled_at"}.isdisjoint(fields)


def test_lineage_writer_uses_activity_for_idempotent_identity(spark_session, monkeypatch):
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    recorded_at = datetime(2026, 1, 1, 10, 30)
    audit = {
        "_committed_by": "tester",
        "_committed_at": datetime(2026, 1, 1, 10, 31),
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
        "table_id": "table-1",
        "profile_snapshot_id": "snapshot-1",
        "pipeline_role": "source",
        "recorded_at": recorded_at,
        "config": object(),
        "env": "dev",
        "context": {},
        "spark_session": spark_session,
    }
    module._write_lineage_participation(**arguments)
    module._write_lineage_participation(**arguments)
    rows = [dataframe.collect()[0].asDict() for dataframe in captured]
    assert rows[0] == rows[1]
    assert rows[0]["lineage_id"] == module._lineage_id(
        activity_id="activity-1", table_id="table-1", profile_snapshot_id="snapshot-1", pipeline_role="source"
    )
    assert rows[0]["recorded_at"] == recorded_at


def test_lineage_upsert_failure_does_not_append_duplicate(spark_session, monkeypatch, registered):
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    monkeypatch.setattr(module, "build_profile_dataframe", lambda df: _profile_df(spark_session))
    monkeypatch.setattr(
        module,
        "_upsert_lineage_event",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("merge failed")),
    )
    expected_id = build_table_id("lakehouse", "raw", None, "customers")
    with pytest.raises(RuntimeError, match=expected_id):
        profile_and_register_table(
            _source_df(spark_session), profile_role="source", target="raw", table_name="customers"
        )
    assert [write["table_name"] for write in registered] == [PROFILED_TABLE, PROFILED_FREQUENCY_TABLE, CATALOGUE_TABLE]


def test_profile_write_failure_stops_before_catalogue_and_lineage(spark_session, monkeypatch, registered):
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    monkeypatch.setattr(module, "build_profile_dataframe", lambda df: _profile_df(spark_session))
    monkeypatch.setattr(
        module,
        "write_lakehouse_table_core",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("profiled boom")),
    )
    with pytest.raises(ValueError, match="profiled boom"):
        profile_and_register_table(
            _source_df(spark_session), profile_role="source", target="raw", table_name="customers"
        )


def test_catalogue_upsert_failure_does_not_fall_back_to_append(spark_session, monkeypatch, registered):
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    monkeypatch.setattr(module, "build_profile_dataframe", lambda df: _profile_df(spark_session))
    monkeypatch.setattr(
        module,
        "_upsert_catalogue_identities",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("catalogue merge failed")),
    )
    with pytest.raises(RuntimeError, match="catalogue merge failed"):
        profile_and_register_table(
            _source_df(spark_session), profile_role="source", target="raw", table_name="customers"
        )


def test_profile_and_register_table_uses_caller_frequency_profile_df_only_for_frequency(
    spark_session, monkeypatch, registered
):
    module = importlib.import_module("fabricops_kit.pipeline.profile_and_register_table")
    source = spark_session.createDataFrame(
        [(i, "A" if i % 2 == 0 else "B") for i in range(20)], "id long, segment string"
    )
    frequency_source = spark_session.createDataFrame([(100, "A"), (101, "A"), (102, "B")], "id long, segment string")
    seen = []

    def frequency(df, *, columns, top_n):
        seen.append(df)
        return profile_frequency_distribution(df, columns=columns, top_n=top_n)

    monkeypatch.setattr(module, "build_frequency_distribution_dataframe", frequency)
    result = profile_and_register_table(
        source,
        profile_role="source",
        target="raw",
        table_name="customers",
        frequency_columns=["segment"],
        frequency_profile_df=frequency_source,
    )
    assert seen == [frequency_source]
    assert {row.row_count for row in result.collect()} == {20}
    child = next(write["df"] for write in registered if write["table_name"] == PROFILED_FREQUENCY_TABLE)
    assert {row.profiled_row_count for row in child.collect()} == {3}


def test_profile_and_register_table_frequency_profile_df_missing_selected_column_raises(spark_session, registered):
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
