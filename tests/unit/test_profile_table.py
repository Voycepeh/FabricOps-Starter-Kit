"""Focused tests for the consolidated profiling API."""

from __future__ import annotations

from tests.helpers import call_with_spark

import importlib
import inspect
import json
from unittest.mock import Mock

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
        "table_name: 'str | None' = None, table_id: 'str | None' = None, grain_discovery_enabled: 'bool' = True, grain_discovery_max_columns: 'int' = 3, grain_discovery_max_candidates: 'int' = 8, frequency_columns=None, "
        "frequency_enabled: 'bool' = True, frequency_top_n: 'int | None' = 5, frequency_max_distinct_percent: 'float | None' = 80.0, "
        "context=None, verbose: 'bool' = True)"
    )
    for name in ("profile_dataframe", "profile_frequency_distribution", "profile_and_register_table"):
        assert not hasattr(fabricops_kit, name)
        assert not hasattr(pipeline, name)


def test_dataframe_only_profiles_without_metadata_writes_and_prints(spark_session, monkeypatch, capsys):
    """Keep identity-free profiling entirely non-persistent."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")
    source = spark_session.createDataFrame([(1, "A"), (2, "A"), (None, None)], ["amount", "status"])
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: pytest.fail("must not resolve metadata"))
    monkeypatch.setattr(module, "write_lakehouse_table", lambda *a, **k: pytest.fail("must not write"))

    result = profile_table(dataframe=source, frequency_columns=["status"])

    assert set(result) == {"profile", "frequency_profile", "row_count"}
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
    module = importlib.import_module("fabricops_kit.pipeline.shared")
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
    module = importlib.import_module("fabricops_kit.pipeline.shared")
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
    query_contexts = []

    def execute(query, **kwargs):
        queries.append(query)
        query_contexts.append(kwargs.get("context"))
        if "INFORMATION_SCHEMA.COLUMNS" in query:
            return schema_rows
        if "FREQUENCY_RANK" in query:
            return frequency_rows
        if "PERCENTILE_CONT" in query:
            return percentile_rows
        return profile_rows

    monkeypatch.setattr(module, "resolve_fabric_context", lambda: ({}, "dev", {}))
    monkeypatch.setattr(module, "resolve_catalogue_table_identity", lambda *a, **k: dict(identity))
    monkeypatch.setattr(module, "get_spark_session", lambda *_args, **_kwargs: spark_session)
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

    assert result["row_count"] == 3
    assert _rows(result["profile"])["amount"]["NULL_COUNT"] == 1
    assert {(row.VALUE, row.FREQUENCY_RANK) for row in result["frequency_profile"].collect()} == {("A", 1), (None, 2)}
    assert len(queries) == 5
    assert all(context and context.get("_fabricops_suppress_io_log") is True for context in query_contexts)
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



def test_profile_key_candidates_prefer_smallest_unique_single_column(spark_session):
    """Return proven single-column keys without testing wider combinations."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")
    shared = importlib.import_module("fabricops_kit.pipeline.shared")
    source = spark_session.createDataFrame(
        [(1, "A"), (2, "A"), (3, "B")],
        ["order_line_id", "status"],
    )

    candidates = module._spark_profile_key_candidates(
        source, shared.build_profile_dataframe(source)
    )

    assert candidates == [{
        "columns": ["order_line_id"],
        "column_count": 1,
        "row_count": 3,
        "distinct_count": 3,
        "uniqueness_percent": 100.0,
        "null_count": 0,
    }]


def test_profile_key_candidates_find_smallest_composite_key(spark_session):
    """Test pairs only when no single column is unique and stop at the first valid width."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")
    shared = importlib.import_module("fabricops_kit.pipeline.shared")
    source = spark_session.createDataFrame(
        [(1, "A"), (1, "B"), (2, "A"), (2, "B")],
        ["order_id", "product_id"],
    )

    candidates = module._spark_profile_key_candidates(
        source, shared.build_profile_dataframe(source)
    )

    assert candidates == [{
        "columns": ["order_id", "product_id"],
        "column_count": 2,
        "row_count": 4,
        "distinct_count": 4,
        "uniqueness_percent": 100.0,
        "null_count": 0,
    }]


def test_profile_key_candidates_allow_snapshot_metadata_in_composite_key(spark_session):
    """Allow technical snapshot columns when the data proves they form the row grain."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")
    shared = importlib.import_module("fabricops_kit.pipeline.shared")
    source = spark_session.createDataFrame(
        [
            (1, "2026-10-01", "batch"),
            (1, "2026-10-02", "batch"),
            (2, "2026-10-01", "batch"),
            (2, "2026-10-02", "batch"),
        ],
        ["product_id", "_committed_at", "_activity_id"],
    )

    candidates = module._spark_profile_key_candidates(
        source, shared.build_profile_dataframe(source)
    )

    assert candidates[0]["columns"] == ["_committed_at", "product_id"]
    assert candidates[0]["uniqueness_percent"] == 100.0



def test_profile_key_candidates_do_not_use_an_arbitrary_top_eight_shortlist(spark_session):
    """Evaluate all eligible columns rather than limiting discovery to a shortlist."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")
    shared = importlib.import_module("fabricops_kit.pipeline.shared")
    rows = [
        ("A", "B", "C", "D", "E", "F", "G", "H", 1, 1),
        ("A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2", 1, 2),
        ("A3", "B3", "C3", "D3", "E3", "F3", "G3", "H3", 2, 1),
        ("A", "B", "C", "D", "E", "F", "G", "H", 2, 2),
    ]
    source = spark_session.createDataFrame(
        rows,
        [
            "description_a", "description_b", "description_c", "description_d",
            "description_e", "description_f", "description_g", "description_h",
            "order_id", "line_number",
        ],
    )

    candidates = module._spark_profile_key_candidates(
        source, shared.build_profile_dataframe(source)
    )

    assert candidates
    assert candidates[0]["column_count"] == 2
    assert candidates[0]["uniqueness_percent"] == 100.0


def test_profile_key_candidates_use_data_not_column_name_heuristics(spark_session):
    """Test arbitrary null-free columns instead of requiring identifier-like names."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")
    shared = importlib.import_module("fabricops_kit.pipeline.shared")
    source = spark_session.createDataFrame(
        [
            ("A", "X"),
            ("A", "Y"),
            ("B", "X"),
            ("B", "Y"),
        ],
        ["product_category", "product_name"],
    )

    candidates = module._spark_profile_key_candidates(
        source, shared.build_profile_dataframe(source)
    )

    assert candidates == [{
        "columns": ["product_category", "product_name"],
        "column_count": 2,
        "row_count": 4,
        "distinct_count": 4,
        "uniqueness_percent": 100.0,
        "null_count": 0,
    }]


def test_key_candidate_evidence_distinguishes_resolved_and_unresolved():
    """Persist explicit discovery status instead of overloading an empty JSON array."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")
    resolved = module._key_candidate_evidence([
        {
            "columns": ["order_id", "line_number"],
            "column_count": 2,
            "row_count": 4,
            "distinct_count": 4,
            "uniqueness_percent": 100.0,
            "null_count": 0,
        }
    ])
    unresolved = module._key_candidate_evidence([])

    assert resolved["status"] == "resolved"
    assert resolved["max_combination_width"] == 3
    assert resolved["candidates"][0]["columns"] == ["order_id", "line_number"]
    assert unresolved == {
        "status": "unresolved",
        "max_combination_width": 3,
        "candidates": [],
    }


def test_warehouse_percentile_query_isolated_per_numeric_column():
    """Keep each ordered percentile scope isolated for Fabric Warehouse compatibility."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")
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
    module = importlib.import_module("fabricops_kit.pipeline.shared")
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


@pytest.mark.parametrize(
    ("sql_type", "precision", "scale", "expected"),
    [
        ("bit", None, None, "boolean"),
        ("smallint", None, None, "smallint"),
        ("int", None, None, "int"),
        ("bigint", None, None, "bigint"),
        ("tinyint", None, None, "smallint"),
        ("real", None, None, "float"),
        ("float", None, None, "double"),
        ("decimal", 18, 2, "decimal(18,2)"),
        ("numeric", 38, 10, "decimal(38,10)"),
        ("date", None, None, "date"),
        ("datetime2", None, None, "timestamp"),
        ("datetimeoffset", None, None, "timestamp"),
        ("varchar", None, None, "string"),
        ("nvarchar", None, None, "string"),
        ("time", None, None, "string"),
        ("varbinary", None, None, "binary"),
        ("uniqueidentifier", None, None, "binary"),
    ],
)
def test_warehouse_type_name_uses_pyspark_canonical_types(
    sql_type, precision, scale, expected
):
    """Normalize Warehouse physical types to the PySpark schema vocabulary."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")
    row = {
        "DATA_TYPE": sql_type,
        "NUMERIC_PRECISION": precision,
        "NUMERIC_SCALE": scale,
    }

    assert module._warehouse_type_name(row) == expected


def test_supplied_dataframe_with_warehouse_identity_stays_in_spark(spark_session, monkeypatch):
    """Treat a custom or incremental Warehouse query result as the exact supplied Spark batch."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")
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
    module = importlib.import_module("fabricops_kit.pipeline.shared")
    updates = []

    class Merge:
        def alias(self, _name):
            return self

        def merge(self, *_args):
            return self

        def whenMatchedUpdate(self, *, set):
            updates.append(set)
            return self

        def whenNotMatchedInsert(self, *, values):
            return self

        def whenNotMatchedBySourceUpdate(self, **_kwargs):
            return self

        def execute(self):
            return None

    class Catalogue:
        def select(self, *_columns):
            return self

        def first(self):
            return {"workspace_id": "dev", "table_id": "target-id"}

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
        catalogue_df=Catalogue(), config={}, active_workspace_id="dev", spark_session=object()
    )

    assert updates[0]["profile_key_candidates_json"] == (
        "coalesce(source.profile_key_candidates_json, target.profile_key_candidates_json)"
    )
    assert updates[0]["load_strategy"] == "coalesce(source.load_strategy, target.load_strategy)"
    assert updates[0]["load_strategy_parameters_json"] == (
        "coalesce(source.load_strategy_parameters_json, target.load_strategy_parameters_json)"
    )


def test_profile_registration_rejects_partition_processing_parameter():
    """Target registration no longer authors partition-based incremental processing."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")

    with pytest.raises(ValueError, match="partition_column"):
        module._processing_definition(
            "target",
            "overwrite",
            {"partition_column": "business_date"},
        )


def test_profile_snapshot_identity_is_stable_per_activity_and_distinct_between_activities(monkeypatch):
    """Use the existing Fabric activity identity as the retry boundary."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")
    activity = {"value": "activity-1"}
    monkeypatch.setattr(
        module,
        "build_runtime_audit_fields",
        lambda **_kwargs: {"_activity_id": activity["value"]},
    )

    first = module._profile_snapshot_id(config={}, active_workspace_id="dev", context={}, table_id="table-1")
    retry = module._profile_snapshot_id(config={}, active_workspace_id="dev", context={}, table_id="table-1")
    activity["value"] = "activity-2"
    later = module._profile_snapshot_id(config={}, active_workspace_id="dev", context={}, table_id="table-1")
    other_table = module._profile_snapshot_id(config={}, active_workspace_id="dev", context={}, table_id="table-2")

    assert retry == first
    assert later != first
    assert other_table != later


def test_same_activity_retry_clears_catalogue_completion_before_replacement(
    spark_session, monkeypatch
):
    """Detect a same-activity retry before clearing its Catalogue completion marker."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")
    updates = []
    activities = spark_session.createDataFrame(
        [("dev", "table-1", "activity-1")],
        ["workspace_id", "table_id", "_activity_id"],
    )
    catalogue = spark_session.createDataFrame(
        [("dev", "table-1", "activity-1")],
        ["workspace_id", "table_id", "_activity_id"],
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
        profiled_df=activities, config={}, active_workspace_id="dev", spark_session=spark_session
    )

    assert is_retry is True
    assert updates == [{"last_profiled_at": "CAST(NULL AS TIMESTAMP)"}]


def test_first_profile_activity_is_not_reported_as_retry(spark_session, monkeypatch):
    """Distinguish a new profiling activity from an idempotent same-activity retry."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")
    activities = spark_session.createDataFrame(
        [("dev", "table-1", "activity-2")],
        ["workspace_id", "table_id", "_activity_id"],
    )
    catalogue = spark_session.createDataFrame(
        [("dev", "table-1", "activity-1")],
        ["workspace_id", "table_id", "_activity_id"],
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
        profiled_df=activities, config={}, active_workspace_id="dev", spark_session=spark_session
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
    module = importlib.import_module("fabricops_kit.pipeline.shared")
    source = spark_session.createDataFrame([(1,)], ["value"])
    identity = {
        "table_id": "lakehouse||source||dbo||orders", "store": "source",
        "schema": "dbo", "table_name": "orders", "store_kind": "lakehouse",
    }
    events = []
    cached = []

    def canonical(profile, **kwargs):
        cached.append(profile)
        return profile

    monkeypatch.setattr(module, "resolve_fabric_context", lambda: ({}, "dev", {}))
    monkeypatch.setattr(module, "resolve_catalogue_table_identity", lambda *a, **k: dict(identity))
    monkeypatch.setattr(module, "_profile_snapshot_id", lambda **k: "snapshot-activity-1")
    monkeypatch.setattr(module, "_canonical_profiled_dataframe", canonical)
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

    assert cached and not cached[0].is_cached
    assert events[-1] == "cleanup"
    assert "summary" in events
    assert ("frequency" in events) is (failure_stage == "catalogue")
    assert ("cleanup failed" in capsys.readouterr().out) is cleanup_fails


def test_profile_table_frequency_top_n_defaults_to_five():
    """Ensure profiling entry points default to Top 5 frequencies."""
    import inspect
    from fabricops_kit.pipeline.profile_table import profile_table
    from fabricops_kit.pipeline.orchestrate_read import orchestrate_read
    from fabricops_kit.pipeline.orchestrate_write import orchestrate_write

    for function in (profile_table,):
        assert inspect.signature(function).parameters["frequency_top_n"].default == 5
        assert inspect.signature(function).parameters["frequency_enabled"].default is True
        assert inspect.signature(function).parameters["grain_discovery_enabled"].default is True
        assert inspect.signature(function).parameters["grain_discovery_max_columns"].default == 3
        assert inspect.signature(function).parameters["grain_discovery_max_candidates"].default == 8


def test_profile_table_frequency_disabled_skips_column_selection():
    """Ensure table-wide frequency profiling can be disabled."""
    import inspect
    from fabricops_kit.pipeline.profile_table import profile_table

    assert "frequency_enabled" in inspect.signature(profile_table).parameters


@pytest.mark.parametrize("backend", ["lakehouse", "warehouse"])
@pytest.mark.parametrize("frequency_enabled", [False, True])
def test_grain_discovery_can_be_disabled_and_reenabled_independently(
    monkeypatch, backend, frequency_enabled
):
    """Skip discovery work while retaining candidates and ordinary profiling."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")
    identity = {"table_id": "table-id", "store": "source", "schema": "dbo",
                "table_name": "orders", "store_kind": backend}
    frame, profile = Mock(), Mock()
    profile.cache.return_value = profile
    profile.select.return_value.first.return_value = {"row_count": 2}
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: ({}, "dev", {}))
    monkeypatch.setattr(module, "resolve_catalogue_table_identity", lambda *a, **k: dict(identity))
    monkeypatch.setattr(module, "build_profile_dataframe", Mock(return_value=profile))
    selection = Mock(side_effect=lambda df, stats, columns, threshold: ["status"] if columns is None else columns)
    monkeypatch.setattr(module, "_selected_frequency_columns", selection)
    frequency = Mock(return_value=Mock())
    monkeypatch.setattr(module, "build_frequency_distribution_dataframe", frequency)
    warehouse = Mock(return_value=(profile, None, [("id", "long", "bigint")]))
    monkeypatch.setattr(module, "_warehouse_profile_dataframes", warehouse)
    candidates = [{"columns": ["id"], "row_count": 2}]
    spark_discovery, warehouse_discovery = Mock(return_value=candidates), Mock(return_value=candidates)
    monkeypatch.setattr(module, "_spark_profile_key_candidates", spark_discovery)
    monkeypatch.setattr(module, "_warehouse_profile_key_candidates", warehouse_discovery)
    monkeypatch.setattr(module, "_canonical_profiled_dataframe", lambda *a, **k: profile)
    monkeypatch.setattr(module, "_profile_snapshot_id", lambda **k: "snapshot")
    for name in ("_stage_catalogue_profile_retry", "_replace_snapshot_rows",
                 "_replace_frequency_rows", "_frequency_metadata_dataframe", "_upsert_catalogue_identities"):
        monkeypatch.setattr(module, name, Mock())
    catalogue = Mock()
    monkeypatch.setattr(module, "_catalogue_dataframe_from_profiled", catalogue)
    discovery = warehouse_discovery if backend == "warehouse" else spark_discovery
    kwargs = {} if backend == "warehouse" else {"dataframe": frame}
    for enabled in (True, False, True):
        discovery.reset_mock()
        result = call_with_spark(object(), profile_table, table_id="table-id",
                               grain_discovery_enabled=enabled, grain_discovery_max_columns=2,
                               grain_discovery_max_candidates=1, frequency_enabled=frequency_enabled, **kwargs)
        assert result["profile"] is profile
        assert discovery.call_count == int(enabled)
        evidence = catalogue.call_args.kwargs["profile_key_candidates_json"]
        if enabled:
            assert evidence["candidates"] == candidates
            assert evidence["status"] == "resolved"
            assert evidence["max_combination_width"] == 2
            assert discovery.call_args.kwargs["max_columns"] == 2
            assert discovery.call_args.kwargs["max_candidates"] == 1
        else:
            assert evidence is None  # Catalogue merge preserves the previous result.
    if backend == "warehouse":
        assert warehouse.call_args.kwargs["frequency_columns"] == (None if frequency_enabled else [])
        spark_discovery.assert_not_called()
    else:
        assert frequency.call_count == (3 if frequency_enabled else 0)
        warehouse_discovery.assert_not_called()


@pytest.mark.parametrize("max_columns", [1, 2, 3])
def test_spark_discovery_respects_maximum_key_width(spark_session, max_columns):
    """A triple-only key stays unresolved when the caller limits the search to pairs."""
    from itertools import product

    module = importlib.import_module("fabricops_kit.pipeline.shared")
    frame = spark_session.createDataFrame(list(product(range(2), repeat=3)), ["a", "b", "c"])
    candidates = module._spark_profile_key_candidates(frame, None, max_columns=max_columns)
    assert [candidate["columns"] for candidate in candidates] == ([["a", "b", "c"]] if max_columns == 3 else [])


@pytest.mark.parametrize("single_column_keys", [False, True])
def test_spark_discovery_respects_candidate_limit(spark_session, single_column_keys):
    """Limit suggestions for both single and composite keys at the smallest valid width."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")
    rows = [(0, 0, 0), (1, 1, 1)] if single_column_keys else [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]
    frame = spark_session.createDataFrame(rows, ["a", "b", "c"])
    candidates = module._spark_profile_key_candidates(frame, None, max_candidates=1)
    assert len(candidates) == 1
    assert candidates[0]["columns"] == (["a"] if single_column_keys else ["a", "b"])


@pytest.mark.parametrize("max_columns,expected_queries", [(1, 1), (2, 4), (3, 5)])
def test_warehouse_discovery_respects_maximum_key_width(monkeypatch, max_columns, expected_queries):
    """Do not issue SQL for combinations wider than the caller's limit."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")
    summary = {"ROW_COUNT": 8, **{f"C{i}_{metric}": value for i in range(3)
               for metric, value in [("NON_NULL_COUNT", 8), ("DISTINCT_COUNT", 2)]}}
    responses = [summary, *[{"DISTINCT_COUNT": 4}] * 3, {"DISTINCT_COUNT": 8}]
    query = Mock(side_effect=[Mock(collect=Mock(return_value=[row])) for row in responses])
    monkeypatch.setattr(module, "read_warehouse_query", query)
    candidates = module._warehouse_profile_key_candidates(
        {"store": "Gold", "schema": "dbo", "table_name": "orders"}, None,
        spark_session=object(), context={}, warehouse_columns=[(col, "long", "bigint") for col in "abc"],
        max_columns=max_columns,
    )
    assert query.call_count == expected_queries
    assert [candidate["columns"] for candidate in candidates] == ([["a", "b", "c"]] if max_columns == 3 else [])


@pytest.mark.parametrize("single_column_keys", [False, True])
def test_warehouse_discovery_stops_after_candidate_limit(monkeypatch, single_column_keys):
    """Stop querying once enough valid smallest-width candidates have been found."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")
    summary = {"ROW_COUNT": 4, **{f"C{i}_{metric}": value for i in range(3)
               for metric, value in [("NON_NULL_COUNT", 4), ("DISTINCT_COUNT", 4 if single_column_keys else 2)]}}
    responses = [summary] if single_column_keys else [summary, {"DISTINCT_COUNT": 4}]
    query = Mock(side_effect=[Mock(collect=Mock(return_value=[row])) for row in responses])
    monkeypatch.setattr(module, "read_warehouse_query", query)
    candidates = module._warehouse_profile_key_candidates(
        {"store": "Gold", "schema": "dbo", "table_name": "orders"}, None,
        spark_session=object(), context={}, warehouse_columns=[(col, "long", "bigint") for col in "abc"],
        max_columns=3, max_candidates=1,
    )
    assert len(candidates) == 1
    assert candidates[0]["columns"] == (["a"] if single_column_keys else ["a", "b"])
    assert query.call_count == len(responses)


@pytest.mark.parametrize("entrypoint", ["profile_table"])
@pytest.mark.parametrize("parameter", ["grain_discovery_max_columns", "grain_discovery_max_candidates"])
@pytest.mark.parametrize("value", [0, -1, True, 1.5, "2", None])
def test_discovery_limits_are_validated_before_any_work(monkeypatch, entrypoint, parameter, value):
    """Reject invalid limits even when discovery is disabled, before metadata or data I/O."""
    from types import SimpleNamespace
    module = importlib.import_module("fabricops_kit.pipeline.shared" if entrypoint == "profile_table" else f"fabricops_kit.pipeline.{entrypoint}")
    boundary = "resolve_fabric_context" if entrypoint == "profile_table" else "prepare_pipeline_execution"
    prepare = Mock(side_effect=AssertionError("must validate before work"))
    monkeypatch.setattr(module, boundary, prepare)
    kwargs = dict(store="Silver", schema="dbo", table_name="orders", grain_discovery_enabled=False)
    if entrypoint.startswith("orchestrate_"):
        from contextlib import nullcontext
        monkeypatch.setattr(module, "PipelineOperation", lambda _plan, _role, arguments: nullcontext(Mock(arguments=arguments)))
        monkeypatch.setattr(module, "current_pipeline_session", lambda: SimpleNamespace(spark=None, sources=[], operation_plan=lambda *args: None))
    if entrypoint == "orchestrate_write":
        kwargs.update(dataframe=object(), write_mode="overwrite")
    with pytest.raises(ValueError, match=f"{parameter} must be a positive integer"):
        (profile_table if entrypoint == "profile_table" else getattr(module, entrypoint))(**kwargs, **{parameter: value})
    prepare.assert_not_called()


@pytest.mark.parametrize("max_columns,expected_count", [(3, 0), (4, 1)])
def test_warehouse_discovery_can_search_beyond_previous_width_limit(monkeypatch, max_columns, expected_count):
    """A caller can explicitly opt into a four-column search."""
    module = importlib.import_module("fabricops_kit.pipeline.shared")
    summary = {"ROW_COUNT": 16, **{f"C{i}_{metric}": value for i in range(4)
               for metric, value in [("NON_NULL_COUNT", 16), ("DISTINCT_COUNT", 2)]}}
    responses = [summary, *[{"DISTINCT_COUNT": 4}] * 6, *[{"DISTINCT_COUNT": 8}] * 4, {"DISTINCT_COUNT": 16}]
    query = Mock(side_effect=[Mock(collect=Mock(return_value=[row])) for row in responses])
    monkeypatch.setattr(module, "read_warehouse_query", query)
    candidates = module._warehouse_profile_key_candidates(
        {"store": "Gold", "schema": "dbo", "table_name": "orders"}, None,
        spark_session=object(), context={}, warehouse_columns=[(col, "long", "bigint") for col in "abcd"],
        max_columns=max_columns,
    )
    assert len(candidates) == expected_count
    assert query.call_count == 11 + expected_count
    if candidates:
        assert candidates[0]["columns"] == ["a", "b", "c", "d"]
