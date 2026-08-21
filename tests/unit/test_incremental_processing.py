"""Planner contract tests."""
# ruff: noqa: D103
import pytest

from fabricops_kit import plan_incremental_processing


def result(**values):
    base = {
        "changed": True,
        "first_observation": False,
        "new_partitions": [],
        "changed_partitions": [],
        "removed_partitions": [],
        "reappeared_partitions": [],
        "partition_column": "snapshot_date",
    }
    return {**base, **values}


@pytest.mark.parametrize("strategy", ["overwrite", "append", "scd1", "scd2"])
def test_first_observation_is_full(strategy):
    kwargs = {"key_columns": ["id"]} if strategy in {"scd1", "scd2"} else {}
    if strategy == "scd2":
        kwargs["effective_column"] = "modified_at"
    plan = plan_incremental_processing(result(first_observation=True), strategy, **kwargs)
    assert plan["read_strategy"] == "full"


@pytest.mark.parametrize("strategy", ["overwrite", "append", "scd1", "scd2"])
def test_unchanged_skips(strategy):
    kwargs = {"key_columns": ["id"]} if strategy in {"scd1", "scd2"} else {}
    if strategy == "scd2":
        kwargs["effective_column"] = "modified_at"
    assert plan_incremental_processing(result(changed=False), strategy, **kwargs)["read_strategy"] == "skip"


def test_append_accepts_only_new_partitions():
    plan = plan_incremental_processing(result(new_partitions=["2026-01-01"]), "append")
    assert plan["partition_values"] == ["2026-01-01"]
    with pytest.raises(ValueError, match="duplicate"):
        plan_incremental_processing(result(changed_partitions=["2026-01-01"]), "append")
    with pytest.raises(ValueError, match="duplicate"):
        plan_incremental_processing(result(reappeared_partitions=["2026-01-01"]), "append")


def test_overwrite_partition_and_full_fallback():
    evidence = result(changed_partitions=["2026-01-01"])
    scoped = plan_incremental_processing(evidence, "overwrite", partition_column="snapshot_date")
    assert (scoped["read_strategy"], scoped["partition_values"]) == ("incremental", ["2026-01-01"])
    assert plan_incremental_processing(evidence, "overwrite")["read_strategy"] == "full"


def test_keys_and_effective_column_are_required():
    with pytest.raises(ValueError, match="key_columns"):
        plan_incremental_processing(result(), "scd1")
    with pytest.raises(ValueError, match="effective_column"):
        plan_incremental_processing(result(), "scd2", key_columns=["id"])


@pytest.mark.parametrize("strategy", ["append", "scd1", "scd2"])
def test_removed_partitions_are_rejected(strategy):
    kwargs = {"key_columns": ["id"]} if strategy in {"scd1", "scd2"} else {}
    if strategy == "scd2":
        kwargs["effective_column"] = "modified_at"
    with pytest.raises(ValueError, match="removed"):
        plan_incremental_processing(result(removed_partitions=["old"]), strategy, **kwargs)


def test_removed_partition_forces_safe_full_overwrite():
    plan = plan_incremental_processing(
        result(removed_partitions=["old"]), "overwrite", partition_column="snapshot_date"
    )
    assert plan["read_strategy"] == "full"
