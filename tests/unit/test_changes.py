"""Tests for reusable changes checks."""

import pytest
import inspect

from fabricops_kit.pipeline import guardrails_shared


CURRENT = [
    {"id": 1, "day": "2026-08-11", "value": "a"},
    {"id": 2, "day": "2026-08-12", "value": "b"},
]


def check(current=CURRENT, previous=None, **kwargs):
    """Run a source check with stable test defaults."""
    return guardrails_shared.changes_check_core(
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
    assert (result["recent_changes"], result["historical_changes"]) == (2, 1)


def test_deletion_requires_complete_scope():
    """Incomplete observations never manufacture deletions."""
    partial = check(CURRENT[:1], CURRENT, comparison_scope="partial")
    complete = check(CURRENT[:1], CURRENT, comparison_scope="complete")
    assert partial["deleted_count"] == 0
    assert partial["deletions_provable"] is False
    assert complete["deleted_count"] == 1


@pytest.mark.parametrize("source_pattern", ["snapshot", "incremental_append", "mutable_incremental"])
def test_explicit_source_patterns(source_pattern):
    """Every explicit supported source pattern is accepted."""
    assert check(source_pattern=source_pattern)["source_pattern"] == source_pattern


def test_unchanged_partitions_bypass_row_comparison(monkeypatch):
    """An unchanged partition stops after the fingerprint tier."""
    monkeypatch.setattr(
        guardrails_shared,
        "_local_row_comparison",
        lambda *args, **kwargs: pytest.fail("row comparison must not run"),
    )
    assert check()["changed"] is False


def test_partition_scope_proves_deletions_only_inside_supplied_partitions():
    """Partition scope detects local deletions without deleting omitted partitions."""
    previous = [
        {"id": 1, "day": "2026-08-11", "value": "a"},
        {"id": 2, "day": "2026-08-11", "value": "b"},
        {"id": 3, "day": "2026-08-12", "value": "c"},
    ]
    result = check([previous[0]], previous, comparison_scope="partitions")
    assert result["deleted_count"] == 1
    assert result["deletions_provable"] is True


def test_incremental_append_never_infers_deletions_and_flags_updates():
    """Append sources distinguish overlapping mutations from absent history."""
    previous = [{"id": 1, "day": "2026-08-12", "value": "old"}, {"id": 2, "day": "2026-08-12", "value": "old"}]
    current = [{"id": 1, "day": "2026-08-12", "value": "changed"}]
    result = check(current, previous, source_pattern="incremental_append")
    assert result["updated_count"] == 1
    assert result["deleted_count"] == 0
    assert result["append_violation_count"] == 1


def test_versioned_uses_latest_version_per_key():
    """Versioned sources compare the explicitly latest logical records."""
    previous = [{"id": 1, "day": "2026-08-12", "version": 1, "value": "old"}]
    current = [
        {"id": 1, "day": "2026-08-12", "version": 1, "value": "old"},
        {"id": 1, "day": "2026-08-12", "version": 2, "value": "new"},
    ]
    result = check(current, previous, source_pattern="versioned", version_column="version")
    assert result["pattern_semantics"] == "latest_version_per_key"
    assert result["updated_count"] == 1


def test_version_only_increment_is_not_a_business_update():
    """A newer version with identical business content is unchanged by default."""
    previous = [{"id": 1, "day": "2026-08-12", "version": 1, "value": "same"}]
    current = [{"id": 1, "day": "2026-08-12", "version": 2, "value": "same"}]
    result = check(current, previous, source_pattern="versioned", version_column="version")
    assert result["updated_count"] == 0


def test_explicit_version_content_detects_version_only_update():
    """Callers may explicitly treat the version field as row content."""
    previous = [{"id": 1, "day": "2026-08-12", "version": 1, "value": "same"}]
    current = [{"id": 1, "day": "2026-08-12", "version": 2, "value": "same"}]
    result = check(
        current,
        previous,
        source_pattern="versioned",
        version_column="version",
        non_key_columns=["day", "value", "version"],
    )
    assert result["updated_count"] == 1


def test_mutable_incremental_surfaces_historical_mutation():
    """Mutable incremental semantics explicitly flag changes outside the window."""
    previous = [{"id": 1, "day": "2026-07-01", "value": "old"}]
    current = [{"id": 1, "day": "2026-07-01", "value": "corrected"}]
    result = check(current, previous, source_pattern="mutable_incremental", refresh_days=7)
    assert result["historical_mutation_detected"] is True


def test_local_fallback_has_no_spark_collect_path():
    """The local fallback cannot collect an entire Spark source."""
    assert ".collect(" not in inspect.getsource(guardrails_shared._local_source_rows)


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
