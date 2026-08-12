"""Focused source change detection tests."""

from datetime import date, timedelta

import pytest

from fabricops_kit.pipeline import detect_source_changes


def _df(spark, rows):
    return spark.createDataFrame(rows, "id long, event_date date, value string")


def _result(spark, previous, current, **kwargs):
    return detect_source_changes(
        _df(spark, current),
        _df(spark, previous),
        key_columns=["id"],
        incremental_column="event_date",
        source_pattern="mutable_incremental",
        **kwargs,
    )


def test_order_does_not_change_fingerprint(spark_session):
    """Physical row ordering does not produce partition drift."""
    rows = [(1, date(2026, 8, 12), "a"), (2, date(2026, 8, 12), "b")]
    result = _result(spark_session, rows, list(reversed(rows)))
    assert result["changed_partitions"] == []
    assert result["has_changes"] is False


def test_new_append_range_and_recent_late_insert(spark_session):
    """New ranges and late-arriving records are reported as recent."""
    previous = [(1, date(2026, 8, 1), "a"), (2, date(2026, 8, 11), "b")]
    current = [*previous, (3, date(2026, 8, 12), "c"), (4, date(2026, 8, 9), "late")]
    result = _result(spark_session, previous, current)
    assert result["previous_observed_maximum"] == date(2026, 8, 11)
    assert result["new_unseen_range"] == {
        "start_exclusive": date(2026, 8, 11), "end_inclusive": date(2026, 8, 12)
    }
    assert result["recent_changes"]["inserted"] == 2
    assert result["historical_changes"]["inserted"] == 0


def test_updates_insertions_and_deletions_are_classified_by_window(spark_session):
    """Complete states classify all supported row changes by age."""
    maximum = date(2026, 8, 12)
    previous = [
        (1, maximum, "old"), (2, maximum - timedelta(days=40), "old"),
        (3, maximum - timedelta(days=45), "gone"), (9, maximum, "anchor"),
    ]
    current = [
        (1, maximum, "new"), (2, maximum - timedelta(days=40), "new"),
        (4, maximum - timedelta(days=50), "backfill"), (9, maximum, "anchor"),
    ]
    result = _result(spark_session, previous, current)
    assert result["recent_changes"] == {"inserted": 0, "updated": 1, "deleted": 0}
    assert result["historical_changes"] == {"inserted": 1, "updated": 1, "deleted": 1}
    assert result["has_historical_changes"] is True


@pytest.mark.parametrize(
    ("refresh_days", "age", "expected"),
    [(30, 20, "recent"), (30, 40, "historical"), (90, 80, "recent")],
)
def test_refresh_window_accepts_arbitrary_positive_values(spark_session, refresh_days, age, expected):
    """The recent window works for arbitrary positive day counts."""
    maximum = date(2026, 8, 12)
    previous = [(1, maximum - timedelta(days=age), "old"), (2, maximum, "anchor")]
    current = [(1, maximum - timedelta(days=age), "new"), (2, maximum, "anchor")]
    result = _result(spark_session, previous, current, refresh_days=refresh_days)
    assert result[f"{expected}_changes"]["updated"] == 1


def test_partial_append_read_does_not_report_deletions(spark_session):
    """Missing old keys in a partial read are not deletions."""
    previous = [(1, date(2026, 8, 11), "old")]
    current = [(2, date(2026, 8, 12), "new")]
    result = _result(spark_session, previous, current, comparison_scope="partial")
    assert result["recent_changes"]["deleted"] == 0
    assert result["missing_partitions"] == []
    assert result["missing_partition_detection_valid"] is False


@pytest.mark.parametrize("refresh_days", [0, -1])
def test_invalid_refresh_days(spark_session, refresh_days):
    """Non-positive recent windows are rejected."""
    rows = [(1, date(2026, 8, 12), "a")]
    with pytest.raises(ValueError, match="positive integer"):
        _result(spark_session, rows, rows, refresh_days=refresh_days)


def test_invalid_columns_pattern_keys_and_version_semantics(spark_session):
    """Ambiguous configuration and logical identities are rejected."""
    rows = [(1, date(2026, 8, 12), "a")]
    frame = _df(spark_session, rows)
    with pytest.raises(ValueError, match="missing required columns"):
        detect_source_changes(frame, frame, key_columns=["missing"])
    with pytest.raises(ValueError, match="missing required columns"):
        detect_source_changes(frame, frame, key_columns=["id"], incremental_column="missing")
    with pytest.raises(ValueError, match="source_pattern"):
        detect_source_changes(frame, frame, key_columns=["id"], source_pattern="bronze")
    with pytest.raises(ValueError, match="version_columns is required"):
        detect_source_changes(frame, frame, key_columns=["id"], source_pattern="versioned")

    duplicate = _df(spark_session, [*rows, (1, date(2026, 8, 13), "b")])
    with pytest.raises(ValueError, match="non-unique"):
        detect_source_changes(duplicate, frame, key_columns=["id"])
    null_key = _df(spark_session, [(None, date(2026, 8, 12), "a")])
    with pytest.raises(ValueError, match="null logical key"):
        detect_source_changes(null_key, frame, key_columns=["id"])


def test_versioned_source_uses_key_and_version_identity(spark_session):
    """Versioned rows use the configured composite version identity."""
    previous = _df(spark_session, [(1, date(2026, 8, 11), "v1")])
    current = _df(spark_session, [(1, date(2026, 8, 11), "v1"), (1, date(2026, 8, 12), "v2")])
    result = detect_source_changes(
        current, previous, key_columns=["id"], version_columns=["event_date"],
        incremental_column="event_date", source_pattern="versioned",
    )
    assert result["recent_changes"]["inserted"] == 1
