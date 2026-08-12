"""Detect source changes and describe incremental read ranges."""

from __future__ import annotations

from functools import reduce
from operator import or_
from typing import Any, Sequence

PATTERNS = {"snapshot", "incremental_append", "mutable_incremental", "versioned"}
SCOPES = {"complete", "partitions", "partial"}


def _column_names(values: Sequence[str] | None, name: str) -> list[str]:
    if values is None or isinstance(values, str) or not values:
        raise ValueError(f"{name} must be a non-empty sequence of column names.")
    result = [str(value).strip() for value in values]
    if any(not value for value in result) or len(result) != len(set(result)):
        raise ValueError(f"{name} must contain unique, non-empty column names.")
    return result


def _validate(current_df, previous_df, *, key_columns, incremental_column, refresh_days,
              source_pattern, version_columns, comparison_scope):
    keys = _column_names(key_columns, "key_columns")
    versions = [] if version_columns is None else _column_names(version_columns, "version_columns")
    pattern, scope = str(source_pattern).strip().lower(), str(comparison_scope).strip().lower()
    if pattern not in PATTERNS:
        raise ValueError(f"source_pattern must be one of: {', '.join(sorted(PATTERNS))}.")
    if scope not in SCOPES:
        raise ValueError(f"comparison_scope must be one of: {', '.join(sorted(SCOPES))}.")
    if isinstance(refresh_days, bool) or not isinstance(refresh_days, int) or refresh_days <= 0:
        raise ValueError("refresh_days must be a positive integer.")
    if pattern == "versioned" and not versions:
        raise ValueError("version_columns is required when source_pattern='versioned'.")
    if pattern != "versioned" and versions:
        raise ValueError("version_columns is only valid when source_pattern='versioned'.")
    if incremental_column is not None and (not isinstance(incremental_column, str) or not incremental_column.strip()):
        raise ValueError("incremental_column must be a non-empty column name when configured.")
    incremental = incremental_column.strip() if incremental_column else None
    required = keys + versions + ([incremental] if incremental else [])
    for label, frame in (("current_df", current_df), ("previous_df", previous_df)):
        missing = [column for column in required if column not in frame.columns]
        if missing:
            raise ValueError(f"{label} is missing required columns: {', '.join(missing)}.")
    if set(current_df.columns) != set(previous_df.columns):
        raise ValueError("current_df and previous_df must contain the same columns.")
    return keys + versions, pattern, scope, incremental


def _hash(columns):
    from pyspark.sql import functions as F

    encoded = [F.to_json(F.struct(F.col(column).alias("value"))) for column in columns]
    return F.sha2(F.concat_ws("\u001f", *encoded), 256)


def _state(df, identity, incremental):
    from pyspark.sql import functions as F

    attributes = [column for column in sorted(df.columns) if column not in identity]
    result = df.withColumn("key_hash", _hash(identity)).withColumn(
        "non_key_hash", _hash(attributes) if attributes else F.sha2(F.lit(""), 256)
    )
    return result.withColumn("_partition", F.col(incremental) if incremental else F.lit("__FULL_SOURCE__"))


def _assert_keys(state, identity, label):
    from pyspark.sql import functions as F

    if state.where(reduce(or_, (F.col(column).isNull() for column in identity))).limit(1).count():
        raise ValueError(f"{label} contains a null logical key.")
    if state.groupBy("key_hash").count().where(F.col("count") > 1).limit(1).count():
        raise ValueError(f"{label} contains non-unique configured logical keys.")


def _fingerprints(state):
    from pyspark.sql import functions as F

    return state.groupBy(F.col("_partition").alias("partition_value")).agg(
        F.count("*").alias("row_count"), F.min("key_hash").alias("min_key"), F.max("key_hash").alias("max_key"),
        F.sha2(F.concat_ws("|", F.sort_array(F.collect_list(F.concat_ws(":", "key_hash", "non_key_hash")))), 256)
        .alias("partition_hash"),
    )


def _one(df, expression):
    return df.agg(expression.alias("value")).first()["value"]


def _detect(current_df, previous_df, *, key_columns, incremental_column, refresh_days,
            source_pattern, version_columns, comparison_scope, include_row_changes):
    from pyspark.sql import functions as F

    identity, pattern, scope, incremental = _validate(
        current_df, previous_df, key_columns=key_columns, incremental_column=incremental_column,
        refresh_days=refresh_days, source_pattern=source_pattern, version_columns=version_columns,
        comparison_scope=comparison_scope,
    )
    current, previous = _state(current_df, identity, incremental), _state(previous_df, identity, incremental)
    _assert_keys(current, identity, "current_df")
    _assert_keys(previous, identity, "previous_df")
    partitions = _fingerprints(current).alias("c").join(_fingerprints(previous).alias("p"), "partition_value", "full")
    new_partitions = [r.partition_value for r in partitions.where(F.col("p.partition_hash").isNull()).collect()]
    missing_valid = scope == "complete"
    missing_partitions = ([r.partition_value for r in partitions.where(F.col("c.partition_hash").isNull()).collect()]
                          if missing_valid else [])
    changed_partitions = [r.partition_value for r in partitions.where(
        F.col("c.partition_hash").isNotNull() & F.col("p.partition_hash").isNotNull()
        & (F.col("c.partition_hash") != F.col("p.partition_hash"))).collect()]
    joined = current.select("key_hash", "non_key_hash", "_partition").alias("c").join(
        previous.select("key_hash", "non_key_hash", "_partition").alias("p"), "key_hash", "full")
    comparable_deletion = F.lit(scope == "complete")
    if scope == "partitions":
        comparable_deletion = F.col("p._partition").isin(
            [row.partition_value for row in _fingerprints(current).select("partition_value").collect()]
        )
    kind = (F.when(F.col("p.non_key_hash").isNull(), "inserted")
            .when(F.col("c.non_key_hash").isNull(),
                  F.when(comparable_deletion, "deleted").otherwise("not_comparable"))
            .when(F.col("c.non_key_hash") != F.col("p.non_key_hash"), "updated").otherwise("unchanged"))
    changes = joined.withColumn("change_type", kind).withColumn(
        "incremental_value", F.coalesce(F.col("c._partition"), F.col("p._partition")))
    source_min = source_max = previous_max = refresh_start = None
    if incremental:
        source_min, source_max = _one(current_df, F.min(incremental)), _one(current_df, F.max(incremental))
        previous_max = _one(previous_df, F.max(incremental))
        if source_max is not None:
            refresh_start = _one(current_df, F.date_sub(F.lit(source_max).cast("date"), refresh_days))
        changes = changes.withColumn("change_recency", F.when(
            F.col("incremental_value").cast("date") >= F.lit(refresh_start), "recent").otherwise("historical"))
    else:
        changes = changes.withColumn("change_recency", F.lit("recent"))
    classified = changes.where(F.col("change_type").isin("inserted", "updated", "deleted"))
    raw_counts = {(r.change_recency, r.change_type): r["count"]
                  for r in classified.groupBy("change_recency", "change_type").count().collect()}
    counts = {when: {kind: raw_counts.get((when, kind), 0) for kind in ("inserted", "updated", "deleted")}
              for when in ("recent", "historical")}
    return {
        "source_pattern": pattern, "comparison_scope": scope, "refresh_days": refresh_days,
        "source_range": {"minimum": source_min, "maximum": source_max},
        "previous_observed_maximum": previous_max,
        "recent_mutable_range": {"start": refresh_start, "end": source_max},
        "new_unseen_range": ({"start_exclusive": previous_max, "end_inclusive": source_max} if incremental else None),
        "historical_comparison_range": ({"before": refresh_start} if incremental else None),
        "partitions_checked": partitions.count(), "new_partitions": new_partitions,
        "changed_partitions": changed_partitions, "missing_partitions": missing_partitions,
        "missing_partition_detection_valid": missing_valid, "recent_changes": counts["recent"],
        "historical_changes": counts["historical"], "row_changes": classified if include_row_changes else None,
        "has_changes": classified.limit(1).count() > 0,
        "has_historical_changes": sum(counts["historical"].values()) > 0,
    }


def detect_source_changes(
    current_df: Any,
    previous_df: Any,
    *,
    key_columns: Sequence[str],
    incremental_column: str | None = None,
    refresh_days: int = 7,
    source_pattern: str = "snapshot",
    version_columns: Sequence[str] | None = None,
    comparison_scope: str = "complete",
    include_row_changes: bool = True,
) -> dict[str, Any]:
    """Compare observed source states and describe changes and read ranges.

    Parameters
    ----------
    current_df : pyspark.sql.DataFrame
        Current source state obtained through an existing FabricOps reader.
    previous_df : pyspark.sql.DataFrame
        Previously observed source state with the same columns.
    key_columns : sequence of str
        Non-null columns defining the logical business key.
    incremental_column : str, optional
        Date or timestamp column used for partition and range planning.
    refresh_days : int, default 7
        Positive number of days considered intentionally mutable.
    source_pattern : {"snapshot", "incremental_append", "mutable_incremental", "versioned"}, default "snapshot"
        Explicit source storage pattern, independent of source location or layer.
    version_columns : sequence of str, optional
        Version identity columns required for a ``versioned`` source.
    comparison_scope : {"complete", "partitions", "partial"}, default "complete"
        Comparison completeness. Only ``complete`` permits deletion detection;
        use ``partial`` for a new-only append read.
    include_row_changes : bool, default True
        Whether to include the Spark DataFrame of classified changed rows.

    Returns
    -------
    dict
        Source ranges, deterministic partition facts, change counts and flags.
        The result deliberately contains no target write policy.

    Raises
    ------
    ValueError
        If configuration, columns, null keys, or key uniqueness are invalid.

    Notes
    -----
    This function runs Spark actions in a Fabric-compatible PySpark runtime.
    Absence is a deletion only when ``comparison_scope="complete"``.

    Examples
    --------
    >>> result = detect_source_changes(
    ...     current_df, previous_df, key_columns=["order_id"],
    ...     incremental_column="order_date", refresh_days=30,
    ...     source_pattern="mutable_incremental",
    ... )
    >>> result["has_historical_changes"]
    False

    See Also
    --------
    profile_dataframe
        Profile current DataFrame column statistics.

    """
    return _detect(
        current_df, previous_df, key_columns=key_columns, incremental_column=incremental_column,
        refresh_days=refresh_days, source_pattern=source_pattern, version_columns=version_columns,
        comparison_scope=comparison_scope, include_row_changes=include_row_changes,
    )
