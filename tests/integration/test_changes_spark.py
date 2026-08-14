"""Distributed Spark coverage for changes checks."""

import pytest

from fabricops_kit.pipeline import guardrails_shared

pytestmark = pytest.mark.spark


def test_spark_unchanged_partitions_bypass_deep_comparison(spark_session, monkeypatch):
    """Matching distributed fingerprints do not invoke the row join tier."""
    rows = [{"id": 1, "day": "2026-08-12", "value": "a"}]
    current = spark_session.createDataFrame(rows)
    previous = spark_session.createDataFrame(rows)
    monkeypatch.setattr(
        guardrails_shared,
        "_spark_row_comparison",
        lambda *args, **kwargs: pytest.fail("deep Spark comparison must not run"),
    )
    result = guardrails_shared.changes_check_core(
        current,
        previous,
        partition_columns=["day"],
        key_columns=["id"],
        range_column="day",
        reference_date="2026-08-12",
    )
    assert result["changed"] is False


def test_spark_changes_are_aggregated_without_collecting_source_rows(spark_session):
    """Spark inputs produce distributed inserted, updated, and deleted counts."""
    previous = spark_session.createDataFrame([
        {"id": 1, "day": "2026-08-12", "value": "old"},
        {"id": 2, "day": "2026-08-12", "value": "deleted"},
    ])
    current = spark_session.createDataFrame([
        {"id": 1, "day": "2026-08-12", "value": "new"},
        {"id": 3, "day": "2026-08-12", "value": "inserted"},
    ])
    result = guardrails_shared.changes_check_core(
        current,
        previous,
        partition_columns=["day"],
        key_columns=["id"],
        range_column="day",
        reference_date="2026-08-12",
    )
    assert (result["inserted_count"], result["updated_count"], result["deleted_count"]) == (1, 1, 1)
