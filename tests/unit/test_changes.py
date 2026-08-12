"""Tests for reusable changes checks."""

import pytest

from fabricops_kit.pipeline import check_changes


CURRENT = [
    {"id": 1, "day": "2026-08-11", "value": "a"},
    {"id": 2, "day": "2026-08-12", "value": "b"},
]


def check(current=CURRENT, previous=None, **kwargs):
    """Run a source check with stable test defaults."""
    return check_changes(
        current,
        CURRENT if previous is None else previous,
        key_columns=["id"],
        partition_columns=["day"],
        range_column="day",
        reference_date="2026-08-12",
        **kwargs,
    )


def test_unchanged_fingerprints_are_order_independent():
    """Fingerprints are insensitive to input row order."""
    result = check(list(reversed(CURRENT)))
    assert result["status"] == "unchanged"
    assert result["partition_observations"] == check()["partition_observations"]


def test_insert_update_recent_and_historical_classification():
    """Changes are counted and split around the mutable window."""
    previous = [
        {"id": 1, "day": "2026-08-01", "value": "old"},
        {"id": 2, "day": "2026-08-12", "value": "old"},
    ]
    current = previous + [{"id": 3, "day": "2026-08-12", "value": "new"}]
    current[0] = {**current[0], "value": "changed"}
    current[1] = {**current[1], "value": "changed"}
    result = check(current, previous, refresh_days=2, source_pattern="mutable_incremental")
    assert (result["inserted_count"], result["updated_count"]) == (1, 2)
    assert (result["recent_changes"], result["historical_changes"]) == (1, 1)


def test_deletion_requires_complete_scope():
    """Incomplete observations never manufacture deletions."""
    partial = check(CURRENT[:1], CURRENT, comparison_scope="partial")
    complete = check(CURRENT[:1], CURRENT, comparison_scope="complete")
    assert partial["deleted_count"] == 0
    assert partial["deletions_provable"] is False
    assert complete["deleted_count"] == 1


@pytest.mark.parametrize("source_pattern", ["snapshot", "incremental_append", "mutable_incremental", "versioned"])
def test_explicit_source_patterns(source_pattern):
    """Every explicit supported source pattern is accepted."""
    assert check(source_pattern=source_pattern)["source_pattern"] == source_pattern


@pytest.mark.parametrize("kwargs", [
    {"source_pattern": "guessed"},
    {"comparison_scope": "unknown"},
    {"refresh_days": -1},
])
def test_invalid_configuration(kwargs):
    """Invalid source behavior configuration is rejected."""
    with pytest.raises(ValueError):
        check(**kwargs)


def test_null_and_duplicate_keys_are_rejected():
    """Logical identities must be non-null and unique."""
    with pytest.raises(ValueError, match="null"):
        check([{**CURRENT[0], "id": None}], [])
    with pytest.raises(ValueError, match="uniquely"):
        check([CURRENT[0], CURRENT[0]], [])
