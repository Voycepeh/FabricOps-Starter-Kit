#!/usr/bin/env python3
"""Reproducible local Spark simulation for FabricOps row-hash research.

This script is deliberately independent of FabricOps runtime write paths. It
uses synthetic data and Parquet targets so it can be run locally or adapted to
a Fabric notebook without changing production behaviour.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable


TECHNICAL_COLUMNS = {
    "_activity_id",
    "_committed_at",
    "_committed_by",
    "_effective_from",
    "_effective_to",
    "_is_current",
    "_notebook_id",
    "_notebook_name",
    "_row_hash",
    "_workspace_id",
}
CASES = ("unchanged", "changed_1", "changed_10", "new", "deleted", "duplicates", "reordered")
PARTITION_CASES = ("unchanged", "changed_day", "late_update", "missing_rows")


def parse_args() -> argparse.Namespace:
    """Parse command-line benchmark configuration."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scales", default="100000,1000000", help="Comma-separated row counts.")
    parser.add_argument("--cases", default=",".join(CASES), help="Comma-separated comparison cases.")
    parser.add_argument("--shuffle-partitions", type=int, default=8)
    parser.add_argument("--local-threads", type=int, default=2)
    parser.add_argument("--work-dir", type=Path, help="New directory for temporary benchmark data.")
    parser.add_argument("--output", type=Path, required=True, help="JSON results path.")
    parser.add_argument("--keep-work-dir", action="store_true")
    parser.add_argument("--correctness-only", action="store_true")
    parser.add_argument("--skip-partition-tiers", action="store_true")
    return parser.parse_args()


def canonical_value(column: Any, datatype: Any) -> Any:
    """Canonicalize nested maps and structs using deterministic field ordering."""
    from pyspark.sql import functions as F
    from pyspark.sql.types import ArrayType, MapType, StructType

    if isinstance(datatype, MapType):
        return F.array_sort(
            F.transform(
                F.map_entries(column),
                lambda entry: F.struct(
                    canonical_value(entry["key"], datatype.keyType).alias("key"),
                    canonical_value(entry["value"], datatype.valueType).alias("value"),
                ),
            )
        )
    if isinstance(datatype, ArrayType):
        return F.transform(column, lambda item: canonical_value(item, datatype.elementType))
    if isinstance(datatype, StructType):
        fields = sorted(datatype.fields, key=lambda field: field.name)
        return F.when(column.isNull(), F.lit(None)).otherwise(
            F.struct(
                *[
                    canonical_value(column[field.name], field.dataType).alias(field.name)
                    for field in fields
                ]
            )
        )
    return column


def business_columns(dataframe: Any) -> list[str]:
    """Return deterministic business columns eligible for hashing."""
    return sorted(
        name
        for name in dataframe.columns
        if name not in TECHNICAL_COLUMNS and not name.startswith("_fabricops_") and not name.startswith("_dq_")
    )


def row_hash_expression(dataframe: Any) -> Any:
    """Build the canonical SHA-256 Spark expression for one row."""
    from pyspark.sql import functions as F

    names = business_columns(dataframe)
    encoded = F.to_json(
        F.struct(
            *[
                canonical_value(F.col(f"`{name}`"), dataframe.schema[name].dataType).alias(name)
                for name in names
            ]
        ),
        options={"ignoreNullFields": "false", "timeZone": "UTC"},
    )
    return F.sha2(encoded, 256)


def with_row_hash(dataframe: Any) -> Any:
    """Add the canonical technical row-hash column."""
    return dataframe.withColumn("_row_hash", row_hash_expression(dataframe))


def aggregate_row_hashes(dataframe: Any, hash_column: str = "_row_hash") -> dict[str, Any]:
    """Compute the current PublicationBatch-style bounded multiset aggregate."""
    from pyspark.sql import functions as F

    totals = dataframe.agg(
        F.count("*").alias("rows"),
        *[
            F.coalesce(
                F.sum(F.conv(F.substring(hash_column, offset, 16), 16, 10).cast("decimal(38,0)")),
                F.lit(0).cast("decimal(38,0)"),
            ).alias(f"h{offset}")
            for offset in (1, 17, 33, 49)
        ],
    ).first().asDict()
    return {key: str(value) if key != "rows" else int(value) for key, value in totals.items()}


def partition_fingerprints(dataframe: Any, partition_column: str = "partition_day") -> dict[int, dict[str, Any]]:
    """Return bounded order-independent row-hash aggregates by partition."""
    from pyspark.sql import functions as F

    hashed = with_row_hash(dataframe)
    grouped = hashed.groupBy(partition_column).agg(
        F.count("*").alias("rows"),
        *[
            F.coalesce(
                F.sum(F.conv(F.substring("_row_hash", offset, 16), 16, 10).cast("decimal(38,0)")),
                F.lit(0).cast("decimal(38,0)"),
            ).alias(f"h{offset}")
            for offset in (1, 17, 33, 49)
        ],
    )
    return {
        int(row[partition_column]): {
            name: int(row[name]) if name == "rows" else str(row[name])
            for name in ("rows", "h1", "h17", "h33", "h49")
        }
        for row in grouped.collect()
    }


def batch_fingerprint(dataframe: Any, *, prehashed: bool) -> str:
    """Return a bounded order-independent fingerprint of a DataFrame."""
    hashed = dataframe if prehashed else with_row_hash(dataframe)
    totals = aggregate_row_hashes(hashed)
    boundary = {
        "schema": [
            (name, dataframe.schema[name].dataType.jsonValue()) for name in business_columns(dataframe)
        ],
        "content": totals,
    }
    return hashlib.sha256(json.dumps(boundary, sort_keys=True, default=str).encode()).hexdigest()


def synthetic_data(spark: Any, rows: int) -> Any:
    """Create a deterministic, typed synthetic business dataset."""
    from pyspark.sql import functions as F

    return (
        spark.range(rows, numPartitions=max(2, min(32, rows // 50_000)))
        .select(
            F.col("id").alias("customer_id"),
            F.floor(F.col("id") / F.lit(1000)).cast("long").alias("watermark"),
            F.format_string("customer-%08d", F.col("id")).alias("name"),
            ((F.col("id") % 100_000) / F.lit(100)).cast("decimal(18,4)").alias("amount"),
            F.timestamp_micros(F.lit(1_700_000_000_000_000) + F.col("id") * 1_000_000).alias("event_ts"),
            F.when((F.col("id") % 11) == 0, F.lit(None)).otherwise(F.format_string("note-%d", F.col("id") % 17)).alias("nullable_note"),
            F.struct(
                F.format_string("C%03d", F.col("id") % 251).alias("code"),
                F.array((F.col("id") % 2).cast("int"), (F.col("id") % 3).cast("int")).alias("flags"),
            ).alias("details"),
            F.create_map(
                F.lit("region"), F.format_string("R%d", F.col("id") % 7),
                F.lit("tier"), F.format_string("T%d", F.col("id") % 4),
            ).alias("attributes"),
        )
    )


def changed_case(base: Any, case: str, rows: int) -> Any:
    """Return one deterministic change case derived from a base snapshot."""
    from pyspark.sql import functions as F

    if case == "unchanged":
        return base
    if case == "changed_1":
        return base.withColumn(
            "amount", F.when((F.col("customer_id") % 100) == 0, F.col("amount") + F.lit(1)).otherwise(F.col("amount"))
        )
    if case == "changed_10":
        return base.withColumn(
            "amount", F.when((F.col("customer_id") % 10) == 0, F.col("amount") + F.lit(1)).otherwise(F.col("amount"))
        )
    if case == "new":
        return base.unionByName(synthetic_data(base.sparkSession, rows + max(1, rows // 100)).where(F.col("customer_id") >= rows))
    if case == "deleted":
        return base.where((F.col("customer_id") % 100) != 0)
    if case == "duplicates":
        return base.unionByName(base.where((F.col("customer_id") % 100) == 0))
    if case == "reordered":
        return base.repartition(max(2, base.rdd.getNumPartitions()), (F.col("customer_id") % 97))
    raise ValueError(f"Unknown case: {case}")


def partition_case(base: Any, case: str) -> Any:
    """Return one deterministic 30-day snapshot change case."""
    from pyspark.sql import functions as F

    if case == "unchanged":
        return base
    if case == "changed_day":
        return base.withColumn(
            "amount",
            F.when(F.col("partition_day") == 29, F.col("amount") + F.lit(1)).otherwise(F.col("amount")),
        )
    if case == "late_update":
        return base.withColumn(
            "amount",
            F.when(
                (F.col("partition_day") == 5) & ((F.col("customer_id") % 10) == 0),
                F.col("amount") + F.lit(1),
            ).otherwise(F.col("amount")),
        )
    if case == "missing_rows":
        return base.where(
            ~((F.col("partition_day") == 10) & ((F.col("customer_id") % 100) == 0))
        )
    raise ValueError(f"Unknown partition case: {case}")


def directory_bytes(path: Path) -> int:
    """Return total physical bytes below a local target directory."""
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file()) if path.exists() else 0


class Recorder:
    """Time operations and associate them with Spark event-log job groups."""

    def __init__(self, spark: Any):
        """Initialize an empty recorder for one Spark session."""
        self.spark = spark
        self.records: list[dict[str, Any]] = []
        self.counter = 0

    def run(self, scale: int, scenario: str, phase: str, case: str, operation: Callable[[], dict[str, Any]]) -> dict[str, Any]:
        """Run and record one benchmark operation."""
        self.counter += 1
        group = f"row-hash-{scale}-{self.counter:04d}"
        self.spark.sparkContext.setJobGroup(group, f"{scenario}/{phase}/{case}", interruptOnCancel=True)
        started = time.perf_counter()
        status = "passed"
        try:
            values = operation()
        except Exception as exc:  # record the failure before propagating
            status = "failed"
            values = {"error": f"{type(exc).__name__}: {exc}"}
            raise
        finally:
            elapsed = time.perf_counter() - started
            self.spark.sparkContext.setLocalProperty("spark.jobGroup.id", None)
        record = {
            "job_group": group,
            "scale": scale,
            "scenario": scenario,
            "phase": phase,
            "case": case,
            "status": status,
            "elapsed_seconds": round(elapsed, 6),
            **values,
        }
        self.records.append(record)
        return record


def reject_duplicate_keys(dataframe: Any) -> bool:
    """Return whether a snapshot contains duplicate business keys."""
    from pyspark.sql import functions as F

    return dataframe.groupBy("customer_id").count().where(F.col("count") > 1).limit(1).count() > 0


def compare_by_key_hash(source: Any, target: Any) -> dict[str, int | bool]:
    """Compare two complete snapshots by business key and canonical row hash."""
    from pyspark.sql import functions as F

    if reject_duplicate_keys(source):
        return {"duplicate_keys_rejected": True, "rows_scanned": source.count() + target.count(), "rows_written": 0}
    source_hash = with_row_hash(source).select("customer_id", F.col("_row_hash").alias("source_hash"))
    target_hash = with_row_hash(target).select("customer_id", F.col("_row_hash").alias("target_hash"))
    summary = (
        source_hash.join(target_hash, "customer_id", "full")
        .agg(
            F.sum(F.when(F.col("target_hash").isNull(), 1).otherwise(0)).alias("inserted"),
            F.sum(F.when(F.col("source_hash").isNull(), 1).otherwise(0)).alias("deleted"),
            F.sum(
                F.when(
                    F.col("source_hash").isNotNull()
                    & F.col("target_hash").isNotNull()
                    & (F.col("source_hash") != F.col("target_hash")),
                    1,
                ).otherwise(0)
            ).alias("updated"),
        )
        .first()
        .asDict()
    )
    values = {name: int(value or 0) for name, value in summary.items()}
    return {**values, "duplicate_keys_rejected": False, "rows_scanned": source.count() + target.count(), "rows_written": 0}


def compare_source_to_persisted_target_hash(source: Any, target: Any) -> dict[str, int | bool]:
    """Hash an un-hashed source while reusing the target's persisted row hash."""
    from pyspark.sql import functions as F

    if reject_duplicate_keys(source):
        return {
            "duplicate_keys_rejected": True,
            "source_rows_scanned": source.count(),
            "target_rows_scanned": target.count(),
            "rows_scanned": source.count() + target.count(),
            "rows_written": 0,
        }
    source_hash = with_row_hash(source).select(
        "customer_id", F.col("_row_hash").alias("source_hash")
    )
    target_hash = target.select(
        "customer_id", F.col("_row_hash").alias("target_hash")
    )
    summary = (
        source_hash.join(target_hash, "customer_id", "full")
        .agg(
            F.sum(F.when(F.col("target_hash").isNull(), 1).otherwise(0)).alias("inserted"),
            F.sum(F.when(F.col("source_hash").isNull(), 1).otherwise(0)).alias("deleted"),
            F.sum(
                F.when(
                    F.col("source_hash").isNotNull()
                    & F.col("target_hash").isNotNull()
                    & (F.col("source_hash") != F.col("target_hash")),
                    1,
                ).otherwise(0)
            ).alias("updated"),
        )
        .first()
        .asDict()
    )
    source_rows = source.count()
    target_rows = target.count()
    values = {name: int(value or 0) for name, value in summary.items()}
    return {
        **values,
        "duplicate_keys_rejected": False,
        "source_rows_scanned": source_rows,
        "target_rows_scanned": target_rows,
        "rows_scanned": source_rows + target_rows,
        "rows_written": 0,
    }


def disappeared_key_count(source: Any, target: Any, *, complete_snapshot: bool) -> int:
    """Count missing target keys only for an explicitly complete snapshot."""
    if not complete_snapshot:
        return 0
    return target.select("customer_id").join(
        source.select("customer_id"), "customer_id", "left_anti"
    ).count()


def transformed_partition(dataframe: Any) -> Any:
    """Apply a deterministic CPU-visible stand-in for downstream transformation."""
    from pyspark.sql import functions as F

    return dataframe.withColumn(
        "_fabricops_benchmark_score",
        F.sha2(
            F.concat_ws(
                "|",
                F.col("customer_id").cast("string"),
                F.col("name"),
                F.col("amount").cast("string"),
            ),
            256,
        ),
    )


def correctness_checks(spark: Any) -> dict[str, Any]:
    """Run deterministic serialization and change-semantics checks."""
    from decimal import Decimal
    from pyspark.sql import Row, functions as F, types as T

    schema = T.StructType(
        [
            T.StructField("key", T.LongType()),
            T.StructField("nullable", T.StringType()),
            T.StructField("event_ts", T.TimestampType()),
            T.StructField("amount", T.DecimalType(18, 4)),
            T.StructField("nested", T.StructType([T.StructField("z", T.StringType()), T.StructField("a", T.IntegerType())])),
            T.StructField("mapping", T.MapType(T.StringType(), T.StringType())),
        ]
    )
    instant = datetime(2026, 1, 2, 3, 4, 5, 123456, tzinfo=UTC)
    left = spark.createDataFrame([Row(1, None, instant, Decimal("12.3400"), Row("last", 7), {"b": "2", "a": "1"})], schema)
    reordered = left.select("mapping", "nested", "amount", "event_ts", "nullable", "key")
    technical = left.withColumn("_committed_at", F.current_timestamp()).withColumn("_activity_id", F.lit("different"))
    map_reordered = left.withColumn(
        "mapping", F.create_map(F.lit("a"), F.lit("1"), F.lit("b"), F.lit("2"))
    )
    left_hash = with_row_hash(left).first()["_row_hash"]
    reordered_hash = with_row_hash(reordered).first()["_row_hash"]
    technical_hash = with_row_hash(technical).first()["_row_hash"]
    duplicate = left.unionByName(left)
    duplicate_aggregate = aggregate_row_hashes(with_row_hash(duplicate))
    single_aggregate = aggregate_row_hashes(with_row_hash(left))

    target = with_row_hash(synthetic_data(spark, 10)).select("customer_id", "_row_hash")
    changed = with_row_hash(changed_case(synthetic_data(spark, 10), "changed_10", 10)).select("customer_id", "_row_hash")
    updates = changed.alias("s").join(target.alias("t"), "customer_id").where(F.col("s._row_hash") != F.col("t._row_hash")).count()
    asymmetric = compare_source_to_persisted_target_hash(
        changed_case(synthetic_data(spark, 10), "changed_10", 10), target
    )
    incomplete = synthetic_data(spark, 10).where(F.col("customer_id") >= 5)
    complete_target = synthetic_data(spark, 10)
    partition_base = synthetic_data(spark, 300).withColumn(
        "partition_day", F.floor(F.col("customer_id") * F.lit(30) / F.lit(300)).cast("int")
    )
    base_partitions = partition_fingerprints(partition_base)

    def changed_partition_values(case: str) -> list[int]:
        observed = partition_fingerprints(partition_case(partition_base, case))
        return sorted(
            day
            for day in set(base_partitions) | set(observed)
            if base_partitions.get(day) != observed.get(day)
        )

    # Minimal history transition: close the old current row and insert the new current row.
    history = spark.createDataFrame([(1, "old", datetime(2026, 1, 1), None, True)], "key long, value string, _effective_from timestamp, _effective_to timestamp, _is_current boolean")
    incoming = spark.createDataFrame([(1, "new", datetime(2026, 1, 2))], "key long, value string, effective_at timestamp")
    old_hash = with_row_hash(history.select("key", "value")).first()["_row_hash"]
    new_hash = with_row_hash(incoming.select("key", "value")).first()["_row_hash"]
    scd2_valid = old_hash != new_hash and incoming.first()["effective_at"] > history.first()["_effective_from"]

    checks = {
        "null_timestamp_decimal_nested_stable": left_hash == with_row_hash(map_reordered).first()["_row_hash"],
        "top_level_column_order_independent": left_hash == reordered_hash,
        "technical_columns_excluded": left_hash == technical_hash,
        "duplicate_multiplicity_preserved": duplicate_aggregate["rows"] == 2 and duplicate_aggregate != single_aggregate,
        "business_key_hash_detects_update": updates == 1,
        "unhashed_source_reuses_persisted_target_hash": asymmetric.get("updated") == 1,
        "scd1_update_count_correct": updates == 1,
        "scd2_history_transition_valid": scd2_valid,
        "incomplete_snapshot_deletion_requires_complete_scope": (
            disappeared_key_count(incomplete, complete_target, complete_snapshot=False) == 0
            and disappeared_key_count(incomplete, complete_target, complete_snapshot=True) == 5
        ),
        "partition_fingerprint_isolates_changed_day": changed_partition_values("changed_day") == [29],
        "partition_fingerprint_finds_late_update": changed_partition_values("late_update") == [5],
        "partition_fingerprint_finds_missing_rows": changed_partition_values("missing_rows") == [10],
        "publication_retry_checkpoint_guarantees": "audited from production tests; not reimplemented by this simulation",
        "lakehouse_warehouse_hash_representation": "lowercase SHA-256 hex string (64 characters)",
    }
    checks["all_executable_checks_passed"] = all(value is True for value in checks.values() if isinstance(value, bool))
    return checks


def run_partition_tiers(
    spark: Any,
    recorder: Recorder,
    scale_root: Path,
    source_path: Path,
    rows: int,
) -> dict[str, Any]:
    """Benchmark full, partition, and simulated change-metadata detection tiers."""
    from pyspark import StorageLevel
    from pyspark.sql import functions as F

    root = scale_root / "partition_tiers"
    snapshots = root / "snapshots"
    outputs = root / "outputs"
    baseline_path = snapshots / "baseline"
    base = spark.read.parquet(str(source_path)).withColumn(
        "partition_day",
        F.least(F.lit(29), F.floor(F.col("customer_id") * F.lit(30) / F.lit(rows))).cast("int"),
    )
    base.write.mode("overwrite").partitionBy("partition_day").parquet(str(baseline_path))
    for case in PARTITION_CASES:
        case_path = snapshots / case
        partition_case(spark.read.parquet(str(baseline_path)), case).write.mode("overwrite").partitionBy(
            "partition_day"
        ).parquet(str(case_path))

    benchmark_storage = StorageLevel.DISK_ONLY
    baseline = spark.read.parquet(str(baseline_path)).persist(benchmark_storage)
    baseline.count()
    try:
        baseline_batch_fingerprint = batch_fingerprint(baseline, prehashed=False)
        baseline_partition_fingerprints = partition_fingerprints(baseline)
    finally:
        baseline.unpersist()

    candidates_by_case = {
        "unchanged": [],
        "changed_day": [29],
        "late_update": [5],
        "missing_rows": [10],
    }

    def _write_partition_output(frame: Any, path: Path) -> None:
        frame.write.mode("overwrite").partitionBy("partition_day").parquet(str(path))

    for case in PARTITION_CASES:
        snapshot_path = snapshots / case

        def full_dataset(case: str = case, snapshot_path: Path = snapshot_path) -> dict[str, Any]:
            total_started = time.perf_counter()
            read_started = time.perf_counter()
            frame = spark.read.parquet(str(snapshot_path)).persist(benchmark_storage)
            source_rows = frame.count()
            read_seconds = time.perf_counter() - read_started
            transformed = None
            try:
                hash_started = time.perf_counter()
                fingerprint = batch_fingerprint(frame, prehashed=False)
                hash_seconds = time.perf_counter() - hash_started
                changed = fingerprint != baseline_batch_fingerprint
                transform_seconds = 0.0
                write_seconds = 0.0
                rows_written = 0
                if changed:
                    transform_started = time.perf_counter()
                    transformed = transformed_partition(frame).persist(benchmark_storage)
                    rows_written = transformed.count()
                    transform_seconds = time.perf_counter() - transform_started
                    write_started = time.perf_counter()
                    _write_partition_output(transformed, outputs / "full" / case)
                    write_seconds = time.perf_counter() - write_started
                return {
                    "detection_level": "full_dataset_fingerprint",
                    "changed_partitions": list(range(30)) if changed else [],
                    "source_rows_scanned": source_rows,
                    "target_rows_scanned": 0,
                    "rows_scanned": source_rows,
                    "rows_transformed": rows_written,
                    "rows_written": rows_written,
                    "read_seconds": round(read_seconds, 6),
                    "hash_seconds": round(hash_seconds, 6),
                    "row_compare_seconds": 0.0,
                    "transform_seconds": round(transform_seconds, 6),
                    "write_seconds": round(write_seconds, 6),
                    "total_pipeline_seconds": round(time.perf_counter() - total_started, 6),
                }
            finally:
                if transformed is not None:
                    transformed.unpersist()
                frame.unpersist()

        recorder.run(rows, "partition_tier_full_fingerprint", "partition_pipeline", case, full_dataset)

        def partition_selective(case: str = case, snapshot_path: Path = snapshot_path) -> dict[str, Any]:
            total_started = time.perf_counter()
            read_started = time.perf_counter()
            frame = spark.read.parquet(str(snapshot_path)).persist(benchmark_storage)
            source_rows = frame.count()
            read_seconds = time.perf_counter() - read_started
            transformed = None
            try:
                hash_started = time.perf_counter()
                current = partition_fingerprints(frame)
                hash_seconds = time.perf_counter() - hash_started
                changed_partitions = sorted(
                    day
                    for day in set(current) | set(baseline_partition_fingerprints)
                    if current.get(day) != baseline_partition_fingerprints.get(day)
                )
                transform_seconds = 0.0
                write_seconds = 0.0
                rows_written = 0
                if changed_partitions:
                    transform_started = time.perf_counter()
                    transformed = transformed_partition(
                        frame.where(F.col("partition_day").isin(changed_partitions))
                    ).persist(benchmark_storage)
                    rows_written = transformed.count()
                    transform_seconds = time.perf_counter() - transform_started
                    write_started = time.perf_counter()
                    _write_partition_output(transformed, outputs / "partition" / case)
                    write_seconds = time.perf_counter() - write_started
                return {
                    "detection_level": "partition_fingerprint_full_scan",
                    "changed_partitions": changed_partitions,
                    "source_rows_scanned": source_rows,
                    "target_rows_scanned": 0,
                    "rows_scanned": source_rows,
                    "rows_transformed": rows_written,
                    "rows_written": rows_written,
                    "read_seconds": round(read_seconds, 6),
                    "hash_seconds": round(hash_seconds, 6),
                    "row_compare_seconds": 0.0,
                    "transform_seconds": round(transform_seconds, 6),
                    "write_seconds": round(write_seconds, 6),
                    "total_pipeline_seconds": round(time.perf_counter() - total_started, 6),
                }
            finally:
                if transformed is not None:
                    transformed.unpersist()
                frame.unpersist()

        recorder.run(
            rows,
            "partition_tier_partition_fingerprint",
            "partition_pipeline",
            case,
            partition_selective,
        )

        def candidate_selective(case: str = case, snapshot_path: Path = snapshot_path) -> dict[str, Any]:
            total_started = time.perf_counter()
            candidate_partitions = candidates_by_case[case]
            if not candidate_partitions:
                return {
                    "detection_level": "simulated_change_metadata",
                    "candidate_metadata": "simulated; not a Delta CDF measurement",
                    "candidate_partitions": [],
                    "changed_partitions": [],
                    "source_rows_scanned": 0,
                    "target_rows_scanned": 0,
                    "rows_scanned": 0,
                    "rows_transformed": 0,
                    "rows_written": 0,
                    "inserted": 0,
                    "updated": 0,
                    "deleted": 0,
                    "read_seconds": 0.0,
                    "hash_seconds": 0.0,
                    "row_compare_seconds": 0.0,
                    "transform_seconds": 0.0,
                    "write_seconds": 0.0,
                    "total_pipeline_seconds": round(time.perf_counter() - total_started, 6),
                }
            read_started = time.perf_counter()
            source = spark.read.parquet(str(snapshot_path)).where(
                F.col("partition_day").isin(candidate_partitions)
            ).persist(benchmark_storage)
            source_rows = source.count()
            target = spark.read.parquet(str(baseline_path)).where(
                F.col("partition_day").isin(candidate_partitions)
            ).persist(benchmark_storage)
            target_rows = target.count()
            read_seconds = time.perf_counter() - read_started
            transformed = None
            try:
                hash_started = time.perf_counter()
                current = partition_fingerprints(source)
                changed_partitions = sorted(
                    day
                    for day in candidate_partitions
                    if current.get(day) != baseline_partition_fingerprints.get(day)
                )
                hash_seconds = time.perf_counter() - hash_started
                comparison = {"inserted": 0, "updated": 0, "deleted": 0}
                row_compare_seconds = 0.0
                transform_seconds = 0.0
                write_seconds = 0.0
                rows_written = 0
                if changed_partitions:
                    compare_started = time.perf_counter()
                    comparison = compare_by_key_hash(source, target)
                    row_compare_seconds = time.perf_counter() - compare_started
                    transform_started = time.perf_counter()
                    transformed = transformed_partition(source).persist(benchmark_storage)
                    rows_written = transformed.count()
                    transform_seconds = time.perf_counter() - transform_started
                    write_started = time.perf_counter()
                    _write_partition_output(transformed, outputs / "candidate" / case)
                    write_seconds = time.perf_counter() - write_started
                return {
                    "detection_level": "simulated_change_metadata_then_partition_then_row",
                    "candidate_metadata": "simulated; not a Delta CDF measurement",
                    "candidate_partitions": candidate_partitions,
                    "changed_partitions": changed_partitions,
                    "source_rows_scanned": source_rows,
                    "target_rows_scanned": target_rows,
                    "rows_scanned": source_rows + target_rows,
                    "rows_transformed": rows_written,
                    "rows_written": rows_written,
                    "inserted": int(comparison.get("inserted") or 0),
                    "updated": int(comparison.get("updated") or 0),
                    "deleted": int(comparison.get("deleted") or 0),
                    "read_seconds": round(read_seconds, 6),
                    "hash_seconds": round(hash_seconds, 6),
                    "row_compare_seconds": round(row_compare_seconds, 6),
                    "transform_seconds": round(transform_seconds, 6),
                    "write_seconds": round(write_seconds, 6),
                    "total_pipeline_seconds": round(time.perf_counter() - total_started, 6),
                }
            finally:
                if transformed is not None:
                    transformed.unpersist()
                source.unpersist()
                target.unpersist()

        recorder.run(
            rows,
            "partition_tier_candidate_metadata",
            "partition_pipeline",
            case,
            candidate_selective,
        )

    return {
        "partition_count": 30,
        "cases": list(PARTITION_CASES),
        "candidate_metadata": "simulated candidate partition list; no Delta runtime was available",
        "partition_source_bytes": directory_bytes(baseline_path),
    }


def run_scale(
    spark: Any,
    recorder: Recorder,
    root: Path,
    rows: int,
    cases: list[str],
    *,
    skip_partition_tiers: bool,
) -> dict[str, Any]:
    """Run the configured benchmark matrix for one scale."""
    from pyspark.sql import functions as F

    scale_root = root / str(rows)
    source_path = scale_root / "source"
    baseline_target = scale_root / "baseline_target"
    current_target = scale_root / "current_target"
    hashed_target = scale_root / "hashed_target"
    delta_path = scale_root / "detected_changes"
    comparison_hashed_target = scale_root / "comparison_target_with_hash"

    synthetic_data(spark, rows).write.mode("overwrite").parquet(str(source_path))
    with_row_hash(spark.read.parquet(str(source_path))).select(
        "customer_id", "_row_hash"
    ).write.mode("overwrite").parquet(str(comparison_hashed_target))
    def overwrite(target: Path, frame: Any) -> dict[str, Any]:
        frame.write.mode("overwrite").parquet(str(target))
        return {"rows_scanned": rows, "rows_written": frame.count(), "target_bytes": directory_bytes(target)}

    recorder.run(rows, "full_read_overwrite_no_hash", "first_load", "unchanged", lambda: overwrite(baseline_target, spark.read.parquet(str(source_path))))
    recorder.run(rows, "full_read_overwrite_no_hash", "unchanged_rerun", "unchanged", lambda: overwrite(baseline_target, spark.read.parquet(str(source_path))))
    recorder.run(rows, "full_read_overwrite_no_hash", "changed_rerun", "changed_1", lambda: overwrite(baseline_target, changed_case(spark.read.parquet(str(source_path)), "changed_1", rows)))
    baseline_bytes = directory_bytes(baseline_target)

    current_state: dict[str, str] = {}

    def current_publication(frame: Any) -> dict[str, Any]:
        from pyspark import StorageLevel

        prepared = frame.persist(StorageLevel.MEMORY_AND_DISK)
        try:
            fingerprint = batch_fingerprint(prepared, prehashed=False)
            skip = current_state.get("fingerprint") == fingerprint
            written = 0
            if not skip:
                prepared.write.mode("overwrite").parquet(str(current_target))
                written = prepared.count()
                current_state["fingerprint"] = fingerprint
            return {"fingerprint": fingerprint, "publication_skipped": skip, "rows_scanned": rows, "rows_written": written, "target_bytes": directory_bytes(current_target)}
        finally:
            prepared.unpersist()

    recorder.run(rows, "current_batch_fingerprint", "first_load", "unchanged", lambda: current_publication(spark.read.parquet(str(source_path))))
    recorder.run(rows, "current_batch_fingerprint", "unchanged_rerun", "unchanged", lambda: current_publication(spark.read.parquet(str(source_path))))
    recorder.run(rows, "current_batch_fingerprint", "changed_rerun", "changed_1", lambda: current_publication(changed_case(spark.read.parquet(str(source_path)), "changed_1", rows)))

    hashed_state: dict[str, str] = {}

    def persisted_hash_publication(frame: Any) -> dict[str, Any]:
        from pyspark import StorageLevel

        hashed = with_row_hash(frame).persist(StorageLevel.MEMORY_AND_DISK)
        try:
            fingerprint = batch_fingerprint(hashed, prehashed=True)
            skip = hashed_state.get("fingerprint") == fingerprint
            written = 0
            if not skip:
                hashed.write.mode("overwrite").parquet(str(hashed_target))
                written = hashed.count()
                hashed_state["fingerprint"] = fingerprint
            return {"fingerprint": fingerprint, "publication_skipped": skip, "rows_scanned": rows, "rows_written": written, "target_bytes": directory_bytes(hashed_target)}
        finally:
            hashed.unpersist()

    recorder.run(rows, "persisted_row_hash_fingerprint", "first_load", "unchanged", lambda: persisted_hash_publication(spark.read.parquet(str(source_path))))
    recorder.run(rows, "persisted_row_hash_fingerprint", "unchanged_rerun", "unchanged", lambda: persisted_hash_publication(spark.read.parquet(str(source_path))))
    recorder.run(rows, "persisted_row_hash_fingerprint", "changed_rerun", "changed_1", lambda: persisted_hash_publication(changed_case(spark.read.parquet(str(source_path)), "changed_1", rows)))
    hashed_bytes = directory_bytes(hashed_target)

    target = spark.read.parquet(str(source_path))
    target_with_persisted_hash = spark.read.parquet(str(comparison_hashed_target))
    for case in cases:
        candidate = changed_case(spark.read.parquet(str(source_path)), case, rows)
        recorder.run(rows, "business_key_row_hash_compare", "comparison", case, lambda candidate=candidate: compare_by_key_hash(candidate, target))
        recorder.run(
            rows,
            "source_no_hash_target_persisted_hash_compare",
            "comparison",
            case,
            lambda candidate=candidate: compare_source_to_persisted_target_hash(
                candidate, target_with_persisted_hash
            ),
        )

    cutoff = max(0, rows - max(1, rows // 10))

    def watermark_incremental() -> dict[str, Any]:
        incremental = spark.read.parquet(str(source_path)).where(F.col("customer_id") >= cutoff)
        incremental.write.mode("overwrite").parquet(str(delta_path))
        count = incremental.count()
        return {"rows_scanned": rows, "rows_written": count, "watermark_after": cutoff - 1, "watermark_through": rows - 1}

    recorder.run(rows, "watermark_incremental", "changed_rerun", "new", watermark_incremental)

    for percentage_case in ("changed_1", "changed_10"):
        source = changed_case(spark.read.parquet(str(source_path)), percentage_case, rows)

        def scd1(source: Any = source, case: str = percentage_case) -> dict[str, Any]:
            source_h = with_row_hash(source).select("customer_id", "_row_hash", *[name for name in source.columns if name != "customer_id"])
            target_h = with_row_hash(target).select("customer_id", F.col("_row_hash").alias("target_hash"))
            changes = source_h.join(target_h, "customer_id", "left").where(F.col("target_hash").isNull() | (F.col("_row_hash") != F.col("target_hash"))).drop("target_hash")
            changes.write.mode("overwrite").parquet(str(delta_path / f"scd1-{case}"))
            count = changes.count()
            return {"rows_scanned": rows * 2, "rows_written": count, "updates": count}

        recorder.run(rows, "hash_based_scd1", "changed_rerun", percentage_case, scd1)

        def scd2(source: Any = source, case: str = percentage_case) -> dict[str, Any]:
            source_h = with_row_hash(source).select("customer_id", "_row_hash", "event_ts")
            target_h = with_row_hash(target).select("customer_id", F.col("_row_hash").alias("target_hash"), F.col("event_ts").alias("old_event_ts"))
            changes = source_h.join(target_h, "customer_id").where(F.col("_row_hash") != F.col("target_hash"))
            expired = changes.select("customer_id", F.lit("expired").alias("version_action"), F.col("event_ts").alias("effective_at"))
            inserted = changes.select("customer_id", F.lit("inserted").alias("version_action"), F.col("event_ts").alias("effective_at"))
            mutations = expired.unionByName(inserted)
            mutations.write.mode("overwrite").parquet(str(delta_path / f"scd2-{case}"))
            count = changes.count()
            return {"rows_scanned": rows * 2, "rows_written": count * 2, "versions_expired": count, "versions_inserted": count}

        recorder.run(rows, "hash_based_scd2", "changed_rerun", percentage_case, scd2)

    partition_summary = (
        None
        if skip_partition_tiers
        else run_partition_tiers(spark, recorder, scale_root, source_path, rows)
    )

    return {
        "rows": rows,
        "baseline_target_bytes": baseline_bytes,
        "row_hash_target_bytes": hashed_bytes,
        "row_hash_storage_overhead_bytes": hashed_bytes - baseline_bytes,
        "row_hash_storage_overhead_percent": round((hashed_bytes / baseline_bytes - 1) * 100, 4) if baseline_bytes else None,
        "partition_tiers": partition_summary,
    }


def parse_event_logs(event_dir: Path) -> dict[str, dict[str, int]]:
    """Aggregate successful Spark task metrics by spark.jobGroup.id."""
    stage_groups: dict[int, set[str]] = {}
    metrics: dict[str, dict[str, int]] = {}
    files = [path for path in event_dir.rglob("*") if path.is_file()]
    events: list[dict[str, Any]] = []
    for path in files:
        try:
            with path.open("r", encoding="utf-8") as handle:
                events.extend(json.loads(line) for line in handle if line.strip())
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    for event in events:
        if event.get("Event") != "SparkListenerJobStart":
            continue
        properties = event.get("Properties") or {}
        group = properties.get("spark.jobGroup.id")
        if not group:
            continue
        item = metrics.setdefault(group, {"spark_jobs": 0, "spark_stages": 0, "spark_tasks": 0, "input_bytes": 0, "input_records": 0, "output_bytes": 0, "output_records": 0, "shuffle_read_bytes": 0, "shuffle_write_bytes": 0, "executor_run_time_ms": 0})
        item["spark_jobs"] += 1
        for stage in event.get("Stage IDs", []):
            stage_groups.setdefault(int(stage), set()).add(group)
    completed_stages: set[tuple[str, int]] = set()
    for event in events:
        if event.get("Event") != "SparkListenerTaskEnd" or event.get("Task End Reason", {}).get("Reason") != "Success":
            continue
        stage = int(event.get("Stage ID", -1))
        task_metrics = event.get("Task Metrics") or {}
        for group in stage_groups.get(stage, ()):
            item = metrics[group]
            item["spark_tasks"] += 1
            item["executor_run_time_ms"] += int(task_metrics.get("Executor Run Time", 0) or 0)
            input_metrics = task_metrics.get("Input Metrics") or {}
            output_metrics = task_metrics.get("Output Metrics") or {}
            shuffle_read = task_metrics.get("Shuffle Read Metrics") or {}
            shuffle_write = task_metrics.get("Shuffle Write Metrics") or {}
            item["input_bytes"] += int(input_metrics.get("Bytes Read", 0) or 0)
            item["input_records"] += int(input_metrics.get("Records Read", 0) or 0)
            item["output_bytes"] += int(output_metrics.get("Bytes Written", 0) or 0)
            item["output_records"] += int(output_metrics.get("Records Written", 0) or 0)
            item["shuffle_read_bytes"] += int(shuffle_read.get("Remote Bytes Read", 0) or 0) + int(shuffle_read.get("Local Bytes Read", 0) or 0)
            item["shuffle_write_bytes"] += int(shuffle_write.get("Shuffle Bytes Written", 0) or 0)
            completed_stages.add((group, stage))
    for group, stage in completed_stages:
        metrics[group]["spark_stages"] += 1
    return metrics


def main() -> None:
    """Run correctness checks, benchmarks, event parsing, and JSON output."""
    args = parse_args()
    # Keep local workers on the same interpreter as the driver. Managed notebook
    # runtimes normally set these already; local multi-Python images may not.
    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)
    scales = [int(value) for value in args.scales.split(",") if value.strip()]
    cases = [value.strip() for value in args.cases.split(",") if value.strip()]
    unknown = sorted(set(cases) - set(CASES))
    if unknown:
        raise SystemExit(f"Unknown cases: {', '.join(unknown)}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.work_dir is None
    root = Path(tempfile.mkdtemp(prefix="fabricops-row-hash-")) if temporary else args.work_dir.resolve()
    if not temporary:
        if root.exists():
            raise SystemExit(f"--work-dir must not already exist: {root}")
        root.mkdir(parents=True)
    event_dir = root / "spark-events"
    event_dir.mkdir()

    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder.master(f"local[{args.local_threads}]")
        .appName("FabricOps row hashing benchmark")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.adaptive.enabled", "false")
        .config("spark.sql.shuffle.partitions", str(args.shuffle_partitions))
        .config("spark.eventLog.enabled", "true")
        .config("spark.eventLog.compress", "false")
        .config("spark.eventLog.dir", event_dir.as_uri())
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    recorder = Recorder(spark)
    started_at = datetime.now(UTC)
    scale_summaries: list[dict[str, Any]] = []
    try:
        correctness = correctness_checks(spark)
        if not args.correctness_only:
            for rows in scales:
                scale_summaries.append(
                    run_scale(
                        spark,
                        recorder,
                        root,
                        rows,
                        cases,
                        skip_partition_tiers=args.skip_partition_tiers,
                    )
                )
    finally:
        spark.stop()

    event_metrics = parse_event_logs(event_dir)
    for record in recorder.records:
        record.update(event_metrics.get(record["job_group"], {}))
    result = {
        "disclaimer": "Synthetic local Spark results; not Microsoft Fabric capacity benchmarks.",
        "started_at": started_at.isoformat(),
        "completed_at": datetime.now(UTC).isoformat(),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "spark": spark.version,
            "logical_cpus": os.cpu_count(),
            "local_threads": args.local_threads,
            "shuffle_partitions": args.shuffle_partitions,
        },
        "configuration": {"scales": scales, "cases": cases},
        "correctness": correctness,
        "scale_summaries": scale_summaries,
        "measurements": recorder.records,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not args.keep_work_dir:
        shutil.rmtree(root)


if __name__ == "__main__":
    main()
