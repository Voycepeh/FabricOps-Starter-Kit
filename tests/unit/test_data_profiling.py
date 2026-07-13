"""Test public Spark profiling callables."""

from __future__ import annotations

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

    profile = profile_dataframe(df, exclude_columns=["id"], approximate_distinct=False)
    rows = _profile_rows(profile)

    assert profile.columns == PROFILE_COLUMNS
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
    assert rows["amount"]["PERCENTILE_25"] == "10.0"
    assert rows["amount"]["MEDIAN"] == "20.0"
    assert rows["amount"]["PERCENTILE_75"] == "40.0"
    assert rows["amount"]["MAX_VALUE"] == "40.0"
    assert rows["category"]["MEAN"] is None
    assert rows["category"]["PERCENTILE_25"] is None
    assert rows["category"]["MIN_VALUE"] == "a"
    assert rows["category"]["MAX_VALUE"] == "b"


def test_profile_dataframe_approximate_default_and_public_signature():
    """Verify root imports and breaking cleanup of the public signature."""
    from fabricops_kit import profile_dataframe as root_profile_dataframe
    from fabricops_kit import profile_frequency_distribution as root_frequency

    assert root_profile_dataframe is profile_dataframe
    assert root_frequency is profile_frequency_distribution
    assert str(inspect.signature(profile_dataframe)) == "(df, *, exclude_columns=None, approximate_distinct: 'bool' = True)"
    assert str(inspect.signature(profile_frequency_distribution)) == "(df, *, columns=None, top_n: 'int' = 20)"


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
    assert profile_dataframe(df, approximate_distinct=False).count() == 2


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


def test_profile_frequency_distribution_default_scalar_selection_and_rank_reset(spark_session):
    """Verify defaults exclude complex columns and rank independently per column."""
    df = spark_session.createDataFrame(
        [Row(status="open", flag=True, tags=["a"], attrs={"k": "v"}, nested=Row(a=1), blob=bytes([1])), Row(status="closed", flag=True, tags=["b"], attrs={"k": "w"}, nested=Row(a=2), blob=bytes([2]))]
    )

    rows = [row.asDict() for row in profile_frequency_distribution(df, top_n=1).collect()]

    assert {row["COLUMN_NAME"] for row in rows} == {"status", "flag"}
    assert {row["FREQUENCY_RANK"] for row in rows} == {1}
    assert {row["VALUE"] for row in rows} == {"closed", "true"}


def test_profile_frequency_distribution_validation_and_empty_schema(spark_session):
    """Verify frequency validation and empty DataFrame behavior."""
    df = spark_session.createDataFrame([(1, "a")], ["id", "status"])

    with pytest.raises(ValueError, match="top_n must be greater than zero"):
        profile_frequency_distribution(df, top_n=0)
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
