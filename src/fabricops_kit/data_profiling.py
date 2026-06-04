"""Fabric-first profiling utilities for standardized metadata evidence.

This module focuses on producing a stable, metadata-compatible metadata profile from a
Spark DataFrame. The profile can be written to metadata tables and reused as
AI-ready context for deterministic data quality rule hinting.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import re
from typing import Any



EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_RE = re.compile(r"^[+()\-\s0-9]{7,}$")


_DEFAULT_PROFILE_EXCLUDE_COLUMNS = {
    "_pipeline_run_id",
    "_pipeline_name",
    "_pipeline_environment",
    "_source_table",
    "_record_loaded_timestamp",
    "_notebook_name",
    "_loaded_by",
    # Legacy technical columns retained so profiles exclude outputs from older templates.
    "_source_system",
    "_source_extract_timestamp",
    "_watermark_value",
    "_partition_bucket",
    "_sample_bucket",
    "_row_ingest_id",
    "_business_key_hash",
    "_row_hash",
    "pipeline_ts",
    "notebook_name",
    "loaded_by",
    "p_bucket",
    "sample_bucket",
    "row_ingest_id",
    "ingest_run_id",
    "pipeline_run_id",
    "loaded_at",
    "run_ingest_id",
}



def _get_profiled_columns(df, exclude_columns: list[str] | set[str] | None = None) -> list[str]:
    """Return non-technical column names from a Spark DataFrame.

    Parameters
    ----------
    df : Any
        Spark DataFrame-like object with a ``dtypes`` attribute.
    exclude_columns : list[str] | set[str] | None, optional
        Additional columns to exclude from profiling.

    Returns
    -------
    list[str]
        Eligible business columns to profile.
    """
    excluded = set(_DEFAULT_PROFILE_EXCLUDE_COLUMNS)
    if exclude_columns:
        excluded.update(exclude_columns)
    return [name for name, _dtype in df.dtypes if name not in excluded]


def _is_min_max_supported_type(data_type: str) -> bool:
    """Return whether min/max aggregation is safe for a Spark type string."""
    value = (data_type or "").lower()
    unsupported = ("array", "map", "struct", "binary")
    if any(token in value for token in unsupported):
        return False
    supported = (
        "tinyint",
        "smallint",
        "int",
        "bigint",
        "float",
        "double",
        "decimal",
        "date",
        "timestamp",
        "string",
        "char",
        "varchar",
    )
    return any(token in value for token in supported)


def profile_dataframe(
    df,
    table_name: str,
    *,
    exclude_columns=None,
    run_timestamp_timezone="Asia/Singapore",
):
    """Build canonical DQ-ready profiling rows from a Spark DataFrame."""
    from pyspark.sql import functions as F


    eligible_columns = _get_profiled_columns(df, exclude_columns=exclude_columns)
    if not eligible_columns:
        raise ValueError("No eligible non-technical columns found for metadata profiling.")

    dtype_map = dict(df.dtypes)
    row_count = int(df.count())

    agg_exprs = []
    for column_name in eligible_columns:
        agg_exprs.append(F.sum(F.col(column_name).isNull().cast("int")).alias(f"{column_name}_NULL_COUNT"))
        agg_exprs.append(F.countDistinct(F.col(column_name)).alias(f"{column_name}_DISTINCT_COUNT"))
        if _is_min_max_supported_type(dtype_map[column_name]):
            agg_exprs.append(F.min(F.col(column_name)).alias(f"{column_name}_MIN"))
            agg_exprs.append(F.max(F.col(column_name)).alias(f"{column_name}_MAX"))

    agg_df = df.agg(*agg_exprs)
    denominator = F.lit(row_count if row_count > 0 else 1).cast("double")

    rows = []
    for column_name in eligible_columns:
        rows.append(
            agg_df.select(
                F.lit(table_name).alias("TABLE_NAME"),
                F.from_utc_timestamp(F.current_timestamp(), run_timestamp_timezone).alias("RUN_TIMESTAMP"),
                F.lit(column_name).alias("COLUMN_NAME"),
                F.lit(dtype_map[column_name]).alias("DATA_TYPE"),
                F.lit(row_count).alias("ROW_COUNT"),
                F.coalesce(F.col(f"{column_name}_NULL_COUNT"), F.lit(0)).cast("long").alias("NULL_COUNT"),
                F.round((F.coalesce(F.col(f"{column_name}_NULL_COUNT"), F.lit(0)).cast("double") / denominator) * 100, 3).alias("NULL_PERCENT"),
                F.coalesce(F.col(f"{column_name}_DISTINCT_COUNT"), F.lit(0)).cast("long").alias("DISTINCT_COUNT"),
                F.round((F.coalesce(F.col(f"{column_name}_DISTINCT_COUNT"), F.lit(0)).cast("double") / denominator) * 100, 3).alias("DISTINCT_PERCENT"),
                F.col(f"{column_name}_MIN").cast("string").alias("MIN_VALUE") if f"{column_name}_MIN" in agg_df.columns else F.lit(None).cast("string").alias("MIN_VALUE"),
                F.col(f"{column_name}_MAX").cast("string").alias("MAX_VALUE") if f"{column_name}_MAX" in agg_df.columns else F.lit(None).cast("string").alias("MAX_VALUE"),
            )
        )

    out = rows[0]
    for next_row in rows[1:]:
        out = out.unionByName(next_row)
    return out


