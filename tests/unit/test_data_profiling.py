"""Test public Spark profiling callables."""

from __future__ import annotations

import importlib
import inspect
from datetime import date, datetime

import pytest
from pyspark.sql import Row

from fabricops_kit.pipeline import profile_dataframe, profile_frequency_distribution

pytestmark = [pytest.mark.unit, pytest.mark.spark]

PROFILE_COLUMNS = [
    "COLUMN_NAME",
    "DATA_TYPE",
    "ROW_COUNT",
    "NON_NULL_COUNT",
    "NULL_COUNT",
    "NULL_PERCENT",
    "DISTINCT_COUNT",
    "DISTINCT_PERCENT",
    "MEAN",
    "STDDEV",
    "MIN_VALUE",
    "PERCENTILE_25",
    "MEDIAN",
    "PERCENTILE_75",
    "MAX_VALUE",
]


def test_profile_dataframe_delegates_to_shared_profiler(monkeypatch):
    """Verify the public wrapper passes its inputs to the shared profiler."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_dataframe")
    source = object()
    expected = object()
    calls = []

    def build(df, *, exclude_columns=None):
        calls.append((df, exclude_columns))
        return expected

    monkeypatch.setattr(module, "build_profile_dataframe", build)

    assert module.profile_dataframe(source, exclude_columns={"audit"}) is expected
    assert calls == [(source, {"audit"})]


FREQUENCY_COLUMNS = [
    "COLUMN_NAME",
    "DATA_TYPE",
    "VALUE",
    "FREQUENCY_COUNT",
    "FREQUENCY_PERCENT",
    "FREQUENCY_RANK",
    "PROFILED_ROW_COUNT",
    "PROFILED_NON_NULL_COUNT",
]


def _profile_rows(profile):
    return {row["COLUMN_NAME"]: row.asDict() for row in profile.collect()}


def test_profile_dataframe_output_order_counts_exclusions_and_numeric_stats(spark_session):
    """Verify structural profile output, exclusions, counts, and numeric stats."""
    df = spark_session.createDataFrame(
        [
            (1, 10.0, "b", "skip"),
            (2, 20.0, "a", "skip"),
            (3, None, "a", "skip"),
            (4, 40.0, None, "skip"),
        ],
        ["id", "amount", "category", "_pipeline_run_id"],
    )

    profile = profile_dataframe(df, exclude_columns=["id"])
    rows = _profile_rows(profile)

    assert profile.columns == PROFILE_COLUMNS
    dtypes = dict(profile.dtypes)
    assert dtypes["MEAN"] == "double"
    assert dtypes["STDDEV"] == "double"
    assert dtypes["PERCENTILE_25"] == "double"
    assert dtypes["MEDIAN"] == "double"
    assert dtypes["PERCENTILE_75"] == "double"
    assert dtypes["MIN_VALUE"] == "string"
    assert dtypes["MAX_VALUE"] == "string"
    assert set(rows) == {"amount", "category"}
    assert rows["amount"]["ROW_COUNT"] == 4
    assert rows["amount"]["NON_NULL_COUNT"] == 3
    assert rows["amount"]["NULL_COUNT"] == 1
    assert rows["amount"]["NULL_PERCENT"] == 25.0
    assert rows["amount"]["DISTINCT_COUNT"] == 3
    assert rows["amount"]["DISTINCT_PERCENT"] == 75.0
    assert rows["amount"]["MEAN"] == pytest.approx(70 / 3)
    assert rows["amount"]["STDDEV"] == pytest.approx(15.2752523165)
    assert rows["amount"]["MIN_VALUE"] == "10.0"
    assert rows["amount"]["PERCENTILE_25"] == 10.0
    assert rows["amount"]["MEDIAN"] == 20.0
    assert rows["amount"]["PERCENTILE_75"] == 40.0
    assert rows["amount"]["MAX_VALUE"] == "40.0"
    assert rows["category"]["MEAN"] is None
    assert rows["category"]["PERCENTILE_25"] is None
    assert rows["category"]["MIN_VALUE"] == "a"
    assert rows["category"]["MAX_VALUE"] == "b"


def test_profile_dataframe_exact_distinct_counts_at_scale_with_duplicates_and_nulls(spark_session):
    """Verify exact cardinality, percentage bounds, duplicates, and null exclusion."""
    from pyspark.sql import functions as F

    df = spark_session.range(100_000).select(
        F.col("id").alias("unique_value"),
        (F.col("id") % 10).alias("duplicate_value"),
        F.when((F.col("id") % 2) == 0, F.lit(None)).otherwise(F.lit("present")).alias("nullable_value"),
    )

    rows = _profile_rows(profile_dataframe(df))

    assert rows["unique_value"]["DISTINCT_COUNT"] == 100_000
    assert rows["unique_value"]["DISTINCT_PERCENT"] == 100.0
    assert rows["duplicate_value"]["DISTINCT_COUNT"] == 10
    assert rows["duplicate_value"]["DISTINCT_PERCENT"] == 0.01
    assert rows["nullable_value"]["NON_NULL_COUNT"] == 50_000
    assert rows["nullable_value"]["NULL_COUNT"] == 50_000
    assert rows["nullable_value"]["DISTINCT_COUNT"] == 1
    assert rows["nullable_value"]["DISTINCT_PERCENT"] == 0.001
    assert all(row["DISTINCT_COUNT"] <= row["ROW_COUNT"] for row in rows.values())
    assert all(row["DISTINCT_PERCENT"] <= 100.0 for row in rows.values())


def test_profile_dataframe_exact_only_public_signature():
    """Verify root imports and breaking cleanup of the public signature."""
    from fabricops_kit import profile_dataframe as root_profile_dataframe
    from fabricops_kit import profile_frequency_distribution as root_frequency

    assert root_profile_dataframe is profile_dataframe
    assert root_frequency is profile_frequency_distribution
    assert str(inspect.signature(profile_dataframe)) == "(df, *, exclude_columns=None)"
    removed_parameter = "approximate_" + "distinct"
    with pytest.raises(TypeError, match=removed_parameter):
        profile_dataframe(object(), **{removed_parameter: True})
    assert str(inspect.signature(profile_frequency_distribution)) == "(df, *, columns=None, top_n: 'int | None' = None)"


def test_profile_dataframe_date_timestamp_complex_and_empty_behavior(spark_session):
    """Verify temporal min/max, complex columns, unsupported metrics, and empty eligibility."""
    df = spark_session.createDataFrame(
        [
            Row(event_date=date(2026, 1, 1), event_ts=datetime(2026, 1, 1, 1, 0), tags=["a"], attrs={"k": "v"}, nested=Row(a=1), blob=bytes([1])),
            Row(event_date=date(2026, 1, 3), event_ts=datetime(2026, 1, 2, 1, 0), tags=["b"], attrs={"k": "w"}, nested=Row(a=2), blob=bytes([2])),
        ]
    )

    rows = _profile_rows(profile_dataframe(df))

    assert rows["event_date"]["MIN_VALUE"] == "2026-01-01"
    assert rows["event_date"]["MAX_VALUE"] == "2026-01-03"
    assert rows["event_ts"]["MIN_VALUE"].startswith("2026-01-01 01:00:00")
    assert rows["event_ts"]["MAX_VALUE"].startswith("2026-01-02 01:00:00")
    for column in ["tags", "attrs", "nested", "blob"]:
        assert rows[column]["MEAN"] is None
        assert rows[column]["MIN_VALUE"] is None
        assert rows[column]["MAX_VALUE"] is None

    technical = spark_session.createDataFrame([("run-1", "ok")], ["_pipeline_run_id", "_dq_check_status"])
    with pytest.raises(ValueError, match="No eligible non-technical columns"):
        profile_dataframe(technical)


def test_profile_dataframe_uses_consolidated_aggregation_not_dataframe_count(spark_session, monkeypatch):
    """Verify profile_dataframe does not call a separate DataFrame.count action."""
    df = spark_session.createDataFrame([(1, 10.0), (2, 20.0)], ["id", "amount"])

    def forbidden_count():
        raise AssertionError("DataFrame.count should not be called by profile_dataframe")

    monkeypatch.setattr(df, "count", forbidden_count)
    assert profile_dataframe(df).count() == 2


def test_profile_frequency_distribution_requested_columns_top_n_ranking_and_percentages(spark_session):
    """Verify requested frequency profiling output, ranking, percentages, and nulls."""
    df = spark_session.createDataFrame(
        [("b", 1), ("a", 1), ("a", 2), (None, 2), ("b", 3)],
        ["status", "code"],
    )

    rows = [row.asDict() for row in profile_frequency_distribution(df, columns=["status"], top_n=3).collect()]

    assert rows[0].keys() == set(FREQUENCY_COLUMNS)
    assert [row["COLUMN_NAME"] for row in rows] == ["status", "status", "status"]
    assert [(row["VALUE"], row["FREQUENCY_COUNT"], row["FREQUENCY_RANK"]) for row in rows] == [("a", 2, 1), ("b", 2, 2), (None, 1, 3)]
    assert rows[0]["FREQUENCY_PERCENT"] == 40.0
    assert rows[0]["PROFILED_ROW_COUNT"] == 5
    assert rows[0]["PROFILED_NON_NULL_COUNT"] == 4


def test_profile_frequency_distribution_default_scalar_selection_all_values_and_rank_reset(spark_session):
    """Verify default full scalar profiling, exclusions, nulls, and per-column ranks."""
    rows_in = [
        Row(status="open" if i % 2 == 0 else "closed", code=i, flag=True, _pipeline_run_id="run", tags=["a"], attrs={"k": "v"}, nested=Row(a=1), blob=bytes([1]))
        for i in range(25)
    ]
    rows_in.append(Row(status=None, code=25, flag=False, _pipeline_run_id="run", tags=["b"], attrs={"k": "w"}, nested=Row(a=2), blob=bytes([2])))
    df = spark_session.createDataFrame(rows_in)

    rows = [row.asDict() for row in profile_frequency_distribution(df).collect()]

    assert {row["COLUMN_NAME"] for row in rows} == {"status", "code", "flag"}
    assert sum(1 for row in rows if row["COLUMN_NAME"] == "code") == 26
    status_rows = sorted((row for row in rows if row["COLUMN_NAME"] == "status"), key=lambda row: row["FREQUENCY_RANK"])
    assert [(row["VALUE"], row["FREQUENCY_COUNT"], row["FREQUENCY_PERCENT"], row["FREQUENCY_RANK"]) for row in status_rows] == [
        ("open", 13, 50.0, 1),
        ("closed", 12, 46.154, 2),
        (None, 1, 3.846, 3),
    ]
    assert {row["PROFILED_ROW_COUNT"] for row in rows} == {26}
    assert {row["PROFILED_NON_NULL_COUNT"] for row in status_rows} == {25}
    assert sorted(row["FREQUENCY_RANK"] for row in rows if row["COLUMN_NAME"] == "code") == list(range(1, 27))


def test_profile_frequency_distribution_explicit_top_n_still_limits_each_column(spark_session):
    """Verify explicit top_n limits output per profiled column."""
    df = spark_session.createDataFrame([(i, "x" if i % 2 == 0 else "y") for i in range(10)], ["code", "status"])

    rows = [row.asDict() for row in profile_frequency_distribution(df, top_n=3).collect()]

    assert {row["COLUMN_NAME"] for row in rows} == {"code", "status"}
    assert sum(1 for row in rows if row["COLUMN_NAME"] == "code") == 3
    assert sum(1 for row in rows if row["COLUMN_NAME"] == "status") == 2
    assert max(row["FREQUENCY_RANK"] for row in rows) == 3


def test_profile_frequency_distribution_validation_and_empty_schema(spark_session):
    """Verify frequency validation and empty DataFrame behavior."""
    df = spark_session.createDataFrame([(1, "a")], ["id", "status"])

    with pytest.raises(ValueError, match="top_n must be greater than zero"):
        profile_frequency_distribution(df, top_n=0)
    with pytest.raises(ValueError, match="top_n must be greater than zero"):
        profile_frequency_distribution(df, top_n=-1)
    with pytest.raises(ValueError, match="Requested columns do not exist"):
        profile_frequency_distribution(df, columns=["missing"])

    empty = spark_session.createDataFrame([], "id int, status string")
    result = profile_frequency_distribution(empty, columns=["status"])
    assert result.columns == FREQUENCY_COLUMNS
    assert result.collect() == []


def test_profile_frequency_distribution_does_not_sample_or_collect_raw_values():
    """Verify frequency implementation leaves sampling and raw value collection to callers."""
    source = inspect.getsource(profile_frequency_distribution)

    assert ".sample(" not in source
    assert ".collect(" not in source
    assert "toPandas" not in source
    assert "freqItems" not in source


def test_obsolete_distribution_helpers_are_absent():
    """Verify obsolete distribution machinery was deleted."""
    import fabricops_kit.pipeline.shared as shared

    for name in ["_numeric_bin_edges", "_build_numeric_distribution", "_build_categorical_distribution", "build_distribution_summaries"]:
        assert not hasattr(shared, name)


def test_public_profilers_remain_generic_stage2_inputs(spark_session):
    """Keep Stage 2 metadata identity and runtime context out of public profiler outputs."""
    df = spark_session.createDataFrame([(1, "open"), (2, "closed")], ["id", "status"])

    profile_columns = set(profile_dataframe(df).columns)
    frequency_columns = set(profile_frequency_distribution(df, columns=["status"]).columns)
    metadata_owned_columns = {
        "profile_id",
        "profile_snapshot_id",
        "frequency_id",
        "table_id",
        "column_id",
        "environment_name",
        "profiled_at",
        "_committed_by",
        "_committed_at",
        "_workspace_id",
        "_workspace_name",
        "_notebook_id",
        "_notebook_name",
        "_metadata_lakehouse_name",
        "_activity_id",
    }

    assert profile_columns == set(PROFILE_COLUMNS)
    assert frequency_columns == set(FREQUENCY_COLUMNS)
    assert profile_columns.isdisjoint(metadata_owned_columns)
    assert frequency_columns.isdisjoint(metadata_owned_columns)
