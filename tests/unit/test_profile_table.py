"""Focused tests for the consolidated profiling API."""

from __future__ import annotations

import importlib
import inspect

import pytest

from fabricops_kit import profile_table


def _rows(dataframe):
    return {row["COLUMN_NAME"]: row.asDict() for row in dataframe.collect()}


def test_profile_table_public_signature_and_removed_symbols():
    """Expose only the consolidated signature."""
    import fabricops_kit
    import fabricops_kit.pipeline as pipeline

    assert str(inspect.signature(profile_table)) == (
        "(*, dataframe=None, store: 'str | None' = None, schema: 'str | None' = None, "
        "table_name: 'str | None' = None, table_id: 'str | None' = None, frequency_columns=None, "
        "frequency_top_n: 'int | None' = None, frequency_max_distinct_percent: 'float | None' = 80.0, "
        "spark_session=None)"
    )
    for name in ("profile_dataframe", "profile_frequency_distribution", "profile_and_register_table"):
        assert not hasattr(fabricops_kit, name)
        assert not hasattr(pipeline, name)


def test_dataframe_only_profiles_without_metadata_writes_and_prints(spark_session, monkeypatch, capsys):
    """Keep identity-free profiling entirely non-persistent."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_table")
    source = spark_session.createDataFrame([(1, "A"), (2, "A"), (None, None)], ["amount", "status"])
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: pytest.fail("must not resolve metadata"))
    monkeypatch.setattr(module, "write_lakehouse_table", lambda *a, **k: pytest.fail("must not write"))

    result = profile_table(dataframe=source, frequency_columns=["status"])

    assert set(result) == {"profile", "frequency_profile"}
    assert _rows(result["profile"])["amount"]["ROW_COUNT"] == 3
    frequency = result["frequency_profile"].collect()
    assert {(row.VALUE, row.FREQUENCY_COUNT) for row in frequency} == {(None, 1), ("A", 2)}
    output = capsys.readouterr().out
    assert "FabricOps Profile" in output
    assert "1. Identity → DataFrame only; no governed table_id" in output
    assert "2. Profiling backend → PySpark" in output
    assert "3. Statistical profile → calculated" in output
    assert "4. Frequency profile → calculated" in output
    assert "5. Metadata persistence → skipped; DataFrame-only profiling does not invent a table_id" in output


def test_dataframe_only_raw_file_shape_does_not_invent_identity(spark_session):
    """Return canonical statistics without identity columns for raw file data."""
    source = spark_session.createDataFrame([("file-row",)], ["raw_value"])
    result = profile_table(dataframe=source, frequency_columns=[])
    assert result["profile"].columns == [
        "COLUMN_NAME", "DATA_TYPE", "ROW_COUNT", "NON_NULL_COUNT", "NULL_COUNT", "NULL_PERCENT",
        "DISTINCT_COUNT", "DISTINCT_PERCENT", "MEAN", "STDDEV", "MIN_VALUE", "PERCENTILE_25",
        "MEDIAN", "PERCENTILE_75", "MAX_VALUE",
    ]
    assert result["frequency_profile"] is None


@pytest.mark.parametrize(
    "kwargs,message",
    [
        ({}, "Provide dataframe"),
        ({"table_id": "x", "store": "source", "table_name": "orders"}, "cannot be combined"),
        ({"store": "source"}, "both store and table_name"),
    ],
)
def test_profile_table_rejects_invalid_identity_forms(kwargs, message):
    """Reject conflicting, incomplete, or absent inputs."""
    with pytest.raises(ValueError, match=message):
        profile_table(**kwargs)


def test_dataframe_plus_identity_does_not_reread(spark_session, monkeypatch, capsys):
    """Associate the supplied frame with identity without a physical read."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_table")
    source = spark_session.createDataFrame([(1,)], ["value"])
    identity = {"table_id": "lakehouse||source||dbo||orders", "store": "source", "schema": "dbo", "table_name": "orders", "store_kind": "lakehouse"}
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: ({}, "dev", {}))
    monkeypatch.setattr(module, "resolve_catalogue_table_identity", lambda *a, **k: dict(identity))
    monkeypatch.setattr(module, "read_lakehouse_table", lambda *a, **k: pytest.fail("must not reread"))
    monkeypatch.setattr(module, "_canonical_profiled_dataframe", lambda profile, **k: profile)
    monkeypatch.setattr(module, "_profile_snapshot_id", lambda **k: "snapshot-activity-1")
    monkeypatch.setattr(module, "_frequency_metadata_dataframe", lambda frequency, **k: frequency)
    monkeypatch.setattr(module, "write_lakehouse_table", lambda *a, **k: None)
    monkeypatch.setattr(module, "metadata_table_physical_schema", lambda *a: None)
    monkeypatch.setattr(module, "_replace_frequency_rows", lambda **k: None)
    monkeypatch.setattr(module, "_replace_snapshot_rows", lambda **k: None)
    monkeypatch.setattr(module, "_stage_catalogue_profile_retry", lambda **k: None)
    monkeypatch.setattr(module, "_catalogue_dataframe_from_profiled", lambda *a, **k: object())
    monkeypatch.setattr(module, "_upsert_catalogue_identities", lambda **k: None)

    result = profile_table(dataframe=source, table_id=identity["table_id"], frequency_columns=[])

    assert result["profile"].count() == 1
    output = capsys.readouterr().out
    assert "1. Table → source.dbo.orders" in output
    assert "   Input → supplied DataFrame" in output
    assert "2. Profiling backend → PySpark" in output
    assert "5. Profile snapshot → created new activity snapshot" in output
    assert "6. Frequency profile metadata → skipped; no frequency profile generated" in output
    assert "7. Catalogue → registered or updated table and column metadata" in output
    assert "existing load strategy and parameters preserved" in output


def test_physical_warehouse_uses_compact_sql_profilers(spark_session, monkeypatch, capsys):
    """Push physical Warehouse statistics and frequencies into SQL, never a full table read."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_table")
    identity = {"table_id": "warehouse||source||dbo||orders", "store": "source", "schema": "dbo", "table_name": "orders", "store_kind": "warehouse"}
    schema_rows = spark_session.createDataFrame(
        [("amount", "int", 10, 0), ("status", "varchar", None, None)],
        ["COLUMN_NAME", "DATA_TYPE", "NUMERIC_PRECISION", "NUMERIC_SCALE"],
    )
    profile_rows = spark_session.createDataFrame(
        [(3, 2, 2, 2.0, 1.414, "1", "3", 2, 1, 0.0, 0.0, "A", "A")],
        [
            "ROW_COUNT", "C0_NON_NULL_COUNT", "C0_DISTINCT_COUNT", "C0_MEAN", "C0_STDDEV",
            "C0_MIN_VALUE", "C0_MAX_VALUE",
            "C1_NON_NULL_COUNT", "C1_DISTINCT_COUNT", "C1_MEAN", "C1_STDDEV",
            "C1_MIN_VALUE", "C1_MAX_VALUE",
        ],
    )
    percentile_rows = spark_session.createDataFrame(
        [(1.0, 2.0, 3.0)],
        ["C0_P25", "C0_P50", "C0_P75"],
    )
    frequency_rows = spark_session.createDataFrame(
        [("status", "string", "A", 2, 66.667, 1, 3, 2), ("status", "string", None, 1, 33.333, 2, 3, 2)],
        ["COLUMN_NAME", "DATA_TYPE", "VALUE", "FREQUENCY_COUNT", "FREQUENCY_PERCENT", "FREQUENCY_RANK", "PROFILED_ROW_COUNT", "PROFILED_NON_NULL_COUNT"],
    )
    queries = []

    def execute(query, **_kwargs):
        queries.append(query)
        if "INFORMATION_SCHEMA.COLUMNS" in query:
            return schema_rows
        if "FREQUENCY_RANK" in query:
            return frequency_rows
        if "PERCENTILE_CONT" in query:
            return percentile_rows
        return profile_rows

    monkeypatch.setattr(module, "resolve_fabric_context", lambda: ({}, "dev", {}))
    monkeypatch.setattr(module, "resolve_catalogue_table_identity", lambda *a, **k: dict(identity))
    monkeypatch.setattr(module, "get_spark_session", lambda: spark_session)
    monkeypatch.setattr(module, "read_warehouse_query", execute)
    monkeypatch.setattr(module, "read_lakehouse_table", lambda *a, **k: pytest.fail("must not use Spark table reader"))
    monkeypatch.setattr(module, "_canonical_profiled_dataframe", lambda profile, **k: profile)
    monkeypatch.setattr(module, "_profile_snapshot_id", lambda **k: "snapshot-activity-1")
    monkeypatch.setattr(module, "_frequency_metadata_dataframe", lambda frequency, **k: frequency)
    monkeypatch.setattr(module, "write_lakehouse_table", lambda *a, **k: None)
    monkeypatch.setattr(module, "metadata_table_physical_schema", lambda *a: None)
    monkeypatch.setattr(module, "_replace_frequency_rows", lambda **k: None)
    monkeypatch.setattr(module, "_replace_snapshot_rows", lambda **k: None)
    monkeypatch.setattr(module, "_stage_catalogue_profile_retry", lambda **k: None)
    monkeypatch.setattr(module, "_catalogue_dataframe_from_profiled", lambda *a, **k: object())
    monkeypatch.setattr(module, "_upsert_catalogue_identities", lambda **k: None)

    result = profile_table(table_id=identity["table_id"], frequency_columns=["status"], frequency_top_n=2)

    assert _rows(result["profile"])["amount"]["NULL_COUNT"] == 1
    assert {(row.VALUE, row.FREQUENCY_RANK) for row in result["frequency_profile"].collect()} == {("A", 1), (None, 2)}
    assert len(queries) == 4
    assert all("SELECT *" not in query.upper() for query in queries)
    assert "ORDINAL_POSITION" not in queries[0]
    assert "ORDER BY" not in queries[0].upper()
    assert "PERCENTILE_CONT" not in queries[1]
    assert "PERCENTILE_CONT(0.5)" in queries[2]
    assert queries[2].count("FROM [dbo].[orders]") == 1
    assert "UNION ALL" not in queries[2]
    assert "FREQUENCY_RANK <= 2" in queries[3]
    assert "NVARCHAR" not in queries[1].upper()
    assert "NVARCHAR" not in queries[2].upper()
    assert "NVARCHAR" not in queries[3].upper()
    assert "CONVERT(VARCHAR(MAX)" in queries[1].upper()
    assert "CONVERT(VARCHAR(MAX)" in queries[3].upper()
    output = capsys.readouterr().out
    assert "2. Profiling backend → Warehouse SQL pushdown" in output
    assert "3. Statistical profile → calculated" in output
    assert "4. Frequency profile → calculated" in output


def test_warehouse_percentile_query_isolated_per_numeric_column():
    """Keep each ordered percentile scope isolated for Fabric Warehouse compatibility."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_table")
    identity = {"store": "Gold", "schema": "demo", "table_name": "customer_summary"}

    query = module._warehouse_percentile_query(
        identity,
        column_name="total_order_net_amount",
        prefix="C2",
    )

    assert query.count("PERCENTILE_CONT") == 3
    assert query.count("ORDER BY CONVERT(float, [total_order_net_amount])") == 3
    assert "SELECT TOP (1)" in query
    assert "C2_P25" in query
    assert "C2_P50" in query
    assert "C2_P75" in query
    assert "CROSS JOIN" not in query
    assert "FROM [demo].[customer_summary]" in query


def test_spark_and_warehouse_profile_backends_produce_equivalent_canonical_metrics(spark_session):
    """Keep canonical profile values equivalent across Spark and Warehouse SQL backends."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_table")
    shared = importlib.import_module("fabricops_kit.pipeline.shared")
    source = spark_session.createDataFrame(
        [(1, "A"), (2, "A"), (3, "B"), (4, "C"), (None, None)],
        "amount int, status string",
    )

    spark_profile = {
        row["COLUMN_NAME"]: row.asDict()
        for row in shared.build_profile_dataframe(source).collect()
    }

    warehouse_wide = spark_session.createDataFrame(
        [(
            5,
            4, 4, 2.5, 1.2909944487358056, "1", "4", 1.75, 2.5, 3.25,
            4, 3, None, None, "A", "C",
        )],
        (
            "ROW_COUNT long, "
            "C0_NON_NULL_COUNT long, C0_DISTINCT_COUNT long, C0_MEAN double, C0_STDDEV double, "
            "C0_MIN_VALUE string, C0_MAX_VALUE string, C0_P25 double, C0_P50 double, C0_P75 double, "
            "C1_NON_NULL_COUNT long, C1_DISTINCT_COUNT long, C1_MEAN double, C1_STDDEV double, "
            "C1_MIN_VALUE string, C1_MAX_VALUE string"
        ),
    )
    warehouse_profile = {
        row["COLUMN_NAME"]: row.asDict()
        for row in module._warehouse_statistical_dataframe(
            warehouse_wide,
            [("amount", "int", "int"), ("status", "string", "varchar")],
            spark_session=spark_session,
            percentile_values={"C0_P25": 1.75, "C0_P50": 2.5, "C0_P75": 3.25},
        ).collect()
    }

    assert set(spark_profile) == set(warehouse_profile)
    for column_name in spark_profile:
        spark_row = spark_profile[column_name]
        warehouse_row = warehouse_profile[column_name]
        assert spark_row.keys() == warehouse_row.keys()
        for metric, spark_value in spark_row.items():
            warehouse_value = warehouse_row[metric]
            if isinstance(spark_value, float) and spark_value is not None:
                assert warehouse_value == pytest.approx(spark_value)
            else:
                assert warehouse_value == spark_value


def test_supplied_dataframe_with_warehouse_identity_stays_in_spark(spark_session, monkeypatch):
    """Treat a custom or incremental Warehouse query result as the exact supplied Spark batch."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_table")
    source = spark_session.createDataFrame([(10,), (None,)], ["amount"])
    identity = {"table_id": "warehouse||source||dbo||orders", "store": "source", "schema": "dbo", "table_name": "orders", "store_kind": "warehouse"}
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: ({}, "dev", {}))
    monkeypatch.setattr(module, "resolve_catalogue_table_identity", lambda *a, **k: dict(identity))
    monkeypatch.setattr(module, "read_warehouse_query", lambda *a, **k: pytest.fail("must profile supplied batch in Spark"))
    monkeypatch.setattr(module, "_canonical_profiled_dataframe", lambda profile, **k: profile)
    monkeypatch.setattr(module, "_profile_snapshot_id", lambda **k: "snapshot-activity-1")
    monkeypatch.setattr(module, "write_lakehouse_table", lambda *a, **k: None)
    monkeypatch.setattr(module, "metadata_table_physical_schema", lambda *a: None)
    monkeypatch.setattr(module, "_replace_frequency_rows", lambda **k: None)
    monkeypatch.setattr(module, "_replace_snapshot_rows", lambda **k: None)
    monkeypatch.setattr(module, "_stage_catalogue_profile_retry", lambda **k: None)
    monkeypatch.setattr(module, "_catalogue_dataframe_from_profiled", lambda *a, **k: object())
    monkeypatch.setattr(module, "_upsert_catalogue_identities", lambda **k: None)

    result = profile_table(dataframe=source, table_id=identity["table_id"], frequency_columns=[])

    assert _rows(result["profile"])["amount"]["ROW_COUNT"] == 2


def test_profile_catalogue_refresh_preserves_target_processing(monkeypatch):
    """Keep table processing fields when structural profiling supplies null values."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_table")
    updates = []

    class Merge:
        def alias(self, _name):
            return self

        def merge(self, *_args):
            return self

        def whenMatchedUpdate(self, *, set):
            updates.append(set)
            return self

        def whenNotMatchedInsertAll(self):
            return self

        def whenNotMatchedBySourceUpdate(self, **_kwargs):
            return self

        def execute(self):
            return None

    class Catalogue:
        def select(self, *_columns):
            return self

        def first(self):
            return {"environment_name": "dev", "table_id": "target-id"}

        def alias(self, _name):
            return self

    import sys
    import types

    delta_module = types.ModuleType("delta")
    tables_module = types.ModuleType("delta.tables")
    tables_module.DeltaTable = type("DeltaTable", (), {"forPath": staticmethod(lambda *_args: Merge())})
    monkeypatch.setitem(sys.modules, "delta", delta_module)
    monkeypatch.setitem(sys.modules, "delta.tables", tables_module)
    monkeypatch.setattr(module, "resolve_configured_lakehouse_table", lambda *_a, **_k: (None, None, None, "/metadata/catalogue"))
    monkeypatch.setattr(module, "metadata_table_physical_schema", lambda *_a: None)

    module._upsert_catalogue_identities(
        catalogue_df=Catalogue(), config={}, env="dev", spark_session=object()
    )

    assert updates[0]["load_strategy"] == "coalesce(source.load_strategy, target.load_strategy)"
    assert updates[0]["load_strategy_parameters_json"] == (
        "coalesce(source.load_strategy_parameters_json, target.load_strategy_parameters_json)"
    )


def test_profile_snapshot_identity_is_stable_per_activity_and_distinct_between_activities(monkeypatch):
    """Use the existing Fabric activity identity as the retry boundary."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_table")
    activity = {"value": "activity-1"}
    monkeypatch.setattr(
        module,
        "build_runtime_audit_fields",
        lambda **_kwargs: {"_activity_id": activity["value"]},
    )

    first = module._profile_snapshot_id(config={}, env="dev", context={}, table_id="table-1")
    retry = module._profile_snapshot_id(config={}, env="dev", context={}, table_id="table-1")
    activity["value"] = "activity-2"
    later = module._profile_snapshot_id(config={}, env="dev", context={}, table_id="table-1")
    other_table = module._profile_snapshot_id(config={}, env="dev", context={}, table_id="table-2")

    assert retry == first
    assert later != first
    assert other_table != later


def test_same_activity_retry_clears_catalogue_completion_before_replacement(
    spark_session, monkeypatch
):
    """Detect a same-activity retry before clearing its Catalogue completion marker."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_table")
    updates = []
    activities = spark_session.createDataFrame(
        [("dev", "table-1", "activity-1")],
        ["environment_name", "table_id", "_activity_id"],
    )
    catalogue = spark_session.createDataFrame(
        [("dev", "table-1", "activity-1")],
        ["environment_name", "table_id", "_activity_id"],
    )

    class Merge:
        def toDF(self):
            return catalogue

        def alias(self, _name):
            return self

        def merge(self, _source, condition):
            assert "target._activity_id = source._activity_id" in condition
            return self

        def whenMatchedUpdate(self, *, set):
            updates.append(set)
            return self

        def execute(self):
            return None

    import sys
    import types

    delta_module = types.ModuleType("delta")
    tables_module = types.ModuleType("delta.tables")
    tables_module.DeltaTable = type("DeltaTable", (), {"forPath": staticmethod(lambda *_args: Merge())})
    monkeypatch.setitem(sys.modules, "delta", delta_module)
    monkeypatch.setitem(sys.modules, "delta.tables", tables_module)
    monkeypatch.setattr(module, "resolve_configured_lakehouse_table", lambda *_a, **_k: (None, None, None, "/catalogue"))
    monkeypatch.setattr(module, "metadata_table_physical_schema", lambda *_a: None)

    is_retry = module._stage_catalogue_profile_retry(
        profiled_df=activities, config={}, env="dev", spark_session=spark_session
    )

    assert is_retry is True
    assert updates == [{"last_profiled_at": "CAST(NULL AS TIMESTAMP)"}]


def test_first_profile_activity_is_not_reported_as_retry(spark_session, monkeypatch):
    """Distinguish a new profiling activity from an idempotent same-activity retry."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_table")
    activities = spark_session.createDataFrame(
        [("dev", "table-1", "activity-2")],
        ["environment_name", "table_id", "_activity_id"],
    )
    catalogue = spark_session.createDataFrame(
        [("dev", "table-1", "activity-1")],
        ["environment_name", "table_id", "_activity_id"],
    )

    class Merge:
        def toDF(self):
            return catalogue

        def alias(self, _name):
            return self

        def merge(self, *_args):
            return self

        def whenMatchedUpdate(self, **_kwargs):
            return self

        def execute(self):
            return None

    import sys
    import types

    delta_module = types.ModuleType("delta")
    tables_module = types.ModuleType("delta.tables")
    tables_module.DeltaTable = type("DeltaTable", (), {"forPath": staticmethod(lambda *_args: Merge())})
    monkeypatch.setitem(sys.modules, "delta", delta_module)
    monkeypatch.setitem(sys.modules, "delta.tables", tables_module)
    monkeypatch.setattr(module, "resolve_configured_lakehouse_table", lambda *_a, **_k: (None, None, None, "/catalogue"))
    monkeypatch.setattr(module, "metadata_table_physical_schema", lambda *_a: None)

    is_retry = module._stage_catalogue_profile_retry(
        profiled_df=activities, config={}, env="dev", spark_session=spark_session
    )

    assert is_retry is False



@pytest.mark.parametrize(
    ("failure_stage", "cleanup_fails"),
    [("frequency", False), ("catalogue", False), ("frequency", True)],
)
def test_failed_governed_profile_removes_uncommitted_snapshot(
    spark_session, monkeypatch, capsys, failure_stage, cleanup_fails
):
    """Do not leave summary rows that could expose a partially persisted snapshot."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_table")
    source = spark_session.createDataFrame([(1,)], ["value"])
    identity = {
        "table_id": "lakehouse||source||dbo||orders", "store": "source",
        "schema": "dbo", "table_name": "orders", "store_kind": "lakehouse",
    }
    events = []
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: ({}, "dev", {}))
    monkeypatch.setattr(module, "resolve_catalogue_table_identity", lambda *a, **k: dict(identity))
    monkeypatch.setattr(module, "_profile_snapshot_id", lambda **k: "snapshot-activity-1")
    monkeypatch.setattr(module, "_canonical_profiled_dataframe", lambda profile, **k: profile)
    monkeypatch.setattr(module, "_frequency_metadata_dataframe", lambda frequency, **k: frequency)
    monkeypatch.setattr(module, "_replace_snapshot_rows", lambda **k: events.append("summary"))
    monkeypatch.setattr(module, "_stage_catalogue_profile_retry", lambda **k: events.append("stage"))
    monkeypatch.setattr(
        module,
        "_replace_frequency_rows",
        lambda **k: (_ for _ in ()).throw(RuntimeError("frequency failed"))
        if failure_stage == "frequency" else events.append("frequency"),
    )
    monkeypatch.setattr(module, "_catalogue_dataframe_from_profiled", lambda *a, **k: object())
    monkeypatch.setattr(
        module,
        "_upsert_catalogue_identities",
        lambda **k: (_ for _ in ()).throw(RuntimeError("catalogue failed"))
        if failure_stage == "catalogue" else events.append("catalogue"),
    )
    def cleanup(**_kwargs):
        events.append("cleanup")
        if cleanup_fails:
            raise RuntimeError("cleanup failed")

    monkeypatch.setattr(module, "_delete_profile_snapshot", cleanup)

    with pytest.raises(RuntimeError, match=failure_stage):
        profile_table(dataframe=source, table_id=identity["table_id"], frequency_columns=["value"])

    assert events[-1] == "cleanup"
    assert "summary" in events
    assert ("frequency" in events) is (failure_stage == "catalogue")
    assert ("cleanup failed" in capsys.readouterr().out) is cleanup_fails
