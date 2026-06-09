"""Fabric-first profiling utilities for standardized metadata evidence.

This module focuses on producing a stable, metadata-compatible metadata profile from a
Spark DataFrame. The profile can be written to metadata tables and reused as
AI-ready context for deterministic data quality rule hinting.
"""

from __future__ import annotations

import json
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
    "_dq_check_status",
    "_dq_failed_rules",
    # Technical columns excluded from profile outputs.
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
    "_fabricops_run_id",
    "_fabricops_pipeline_name",
    "_fabricops_created_at",
    "_dq_check_status",
    "_dq_failed_rules",
}
_DEFAULT_PROFILE_EXCLUDE_PREFIXES = ("_fabricops_", "_dq_")


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
    return [
        name
        for name, _dtype in df.dtypes
        if name not in excluded and not any(str(name).startswith(prefix) for prefix in _DEFAULT_PROFILE_EXCLUDE_PREFIXES)
    ]


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


def _numeric_bin_edges(df, column_name: str, *, bin_count: int = 10) -> list[float]:
    values = df.select(column_name).where(f"`{column_name}` is not null")
    try:
        quantiles = values.approxQuantile(column_name, [i / bin_count for i in range(bin_count + 1)], 0.01)
    except Exception:
        return []
    edges: list[float] = []
    for value in quantiles:
        if value is not None and (not edges or float(value) > edges[-1]):
            edges.append(float(value))
    return edges if len(edges) >= 2 else []


def _build_numeric_distribution(df, column_name: str, edges: list[float]) -> dict[str, list[float] | list[int]] | None:
    from pyspark.sql import functions as F

    cleaned_edges: list[float] = []
    for edge in edges:
        value = float(edge)
        if not cleaned_edges or value > cleaned_edges[-1]:
            cleaned_edges.append(value)
    if len(cleaned_edges) < 2:
        return None

    bucket_expr = None
    numeric_value = F.col(column_name).cast("double")
    for index, (lower, upper) in enumerate(zip(cleaned_edges[:-1], cleaned_edges[1:])):
        if index == 0:
            condition = numeric_value < F.lit(upper)
        elif index == len(cleaned_edges) - 2:
            condition = numeric_value >= F.lit(lower)
        else:
            condition = (numeric_value >= F.lit(lower)) & (numeric_value < F.lit(upper))
        bucket_expr = F.when(condition, F.lit(index)) if bucket_expr is None else bucket_expr.when(condition, F.lit(index))

    bucketed = df.where(F.col(column_name).isNotNull()).select(bucket_expr.alias("_profile_bucket"))
    rows = bucketed.where(F.col("_profile_bucket").isNotNull()).groupBy("_profile_bucket").count().collect()
    counts = [0 for _ in range(len(cleaned_edges) - 1)]
    for row in rows:
        bucket = int(row["_profile_bucket"])
        if 0 <= bucket < len(counts):
            counts[bucket] = int(row["count"])
    return {"bin_edges": cleaned_edges, "bin_counts": counts}


def _build_categorical_distribution(df, column_name: str, *, top_n: int = 20, categories: list[str] | set[str] | tuple[str, ...] | None = None) -> dict[str, Any] | None:
    from pyspark.sql import functions as F

    non_null = df.where(F.col(column_name).isNotNull())
    total_count = int(non_null.agg(F.count(F.lit(1)).alias("total_count")).collect()[0]["total_count"])
    if total_count == 0:
        return None

    if categories is not None:
        selected_categories = [str(category) for category in categories]
        if not selected_categories:
            return {"category_counts": {}, "other_count": total_count, "new_categories": []}
        grouped = non_null.groupBy(F.col(column_name).cast("string").alias("_profile_category")).count()
        rows = grouped.where(F.col("_profile_category").isin(selected_categories)).collect()
        category_counts = {category: 0 for category in selected_categories}
        for row in rows:
            category_counts[str(row["_profile_category"])] = int(row["count"])
        kept_count = int(sum(category_counts.values()))
        new_rows = grouped.where(~F.col("_profile_category").isin(selected_categories)).orderBy(F.col("count").desc(), F.col("_profile_category").asc()).limit(top_n).collect()
        return {
            "category_counts": category_counts,
            "other_count": max(total_count - kept_count, 0),
            "new_categories": [str(row["_profile_category"]) for row in new_rows],
        }

    grouped = (
        non_null
        .groupBy(F.col(column_name).cast("string").alias("_profile_category"))
        .count()
        .orderBy(F.col("count").desc(), F.col("_profile_category").asc())
    )
    rows = grouped.limit(top_n).collect()
    if not rows:
        return None
    category_counts = {str(row["_profile_category"]): int(row["count"]) for row in rows}
    kept_count = int(sum(category_counts.values()))
    other_count = max(total_count - kept_count, 0)
    return {"category_counts": category_counts, "other_count": other_count}


def _build_distribution_summaries(
    df,
    eligible_columns: list[str],
    dtype_map: dict[str, str],
    *,
    include_distributions: bool,
    distribution_columns: list[str] | set[str] | tuple[str, ...] | None,
    distribution_bin_edges: dict[str, list[float]] | None,
    categorical_categories: dict[str, list[str]] | None,
    categorical_top_n: int,
) -> dict[str, tuple[str, dict[str, Any]]]:
    if not include_distributions:
        return {}

    selected = set(distribution_columns) if distribution_columns is not None else set(eligible_columns)
    summaries: dict[str, tuple[str, dict[str, Any]]] = {}
    for column_name in eligible_columns:
        if column_name not in selected:
            continue
        data_type = dtype_map[column_name]
        lowered_type = (data_type or "").lower()
        if any(token in lowered_type for token in ("tinyint", "smallint", "int", "bigint", "float", "double", "decimal")):
            edges = (distribution_bin_edges or {}).get(column_name) or _numeric_bin_edges(df, column_name)
            distribution = _build_numeric_distribution(df, column_name, edges)
            if distribution is not None:
                summaries[column_name] = ("numeric", distribution)
        elif any(token in lowered_type for token in ("string", "char", "varchar", "boolean")):
            distribution = _build_categorical_distribution(df, column_name, top_n=categorical_top_n, categories=(categorical_categories or {}).get(column_name))
            if distribution is not None:
                summaries[column_name] = ("categorical", distribution)
    return summaries


def profile_dataframe(
    df,
    table_name: str,
    *,
    exclude_columns=None,
    run_timestamp_timezone="Asia/Singapore",
    include_distributions: bool = False,
    distribution_columns: list[str] | set[str] | tuple[str, ...] | None = None,
    distribution_bin_edges: dict[str, list[float]] | None = None,
    categorical_categories: dict[str, list[str]] | None = None,
    categorical_top_n: int = 20,
):
    """Build canonical DQ-ready profiling rows from a Spark DataFrame.

    Parameters
    ----------
    df : Any
        Spark DataFrame to profile.
    table_name : str
        Logical table name written into each profile row.
    exclude_columns : list[str] or set[str], optional
        Additional columns to skip, on top of the standard technical columns.
    run_timestamp_timezone : str, default="Asia/Singapore"
        Time zone used for the ``RUN_TIMESTAMP`` evidence field.
    include_distributions : bool, default=False
        When true, add lightweight distribution summaries for suitable numeric
        and categorical columns. The default preserves the existing lightweight
        profile shape and behavior.
    distribution_columns : list[str] or set[str] or tuple[str, ...], optional
        Optional allow-list of important columns for distribution summaries.
        ``None`` profiles every suitable business column.
    distribution_bin_edges : dict[str, list[float]], optional
        Optional numeric bin edges keyed by column name. Pass baseline edges to
        make the current profile directly comparable with a previous profile.
    categorical_categories : dict[str, list[str]], optional
        Optional baseline category vocabulary keyed by column name. When
        supplied, those categories are counted explicitly and all other non-null
        values are rolled into ``other_count`` so the current profile remains
        comparable with the baseline.
    categorical_top_n : int, default=20
        Maximum number of non-null category values to keep per categorical
        column before rolling the remainder into ``other_count``.

    Returns
    -------
    Any
        Spark DataFrame containing one profile row per eligible business
        column. Existing columns are preserved; distribution-enabled runs also
        include ``DISTRIBUTION_TYPE`` and ``DISTRIBUTION_JSON``.

    Notes
    -----
    Distribution profiling only collects aggregated Spark results such as
    quantiles, bucket counts, and grouped category counts. It does not collect
    complete datasets to the driver.
    """
    from pyspark.sql import functions as F

    eligible_columns = _get_profiled_columns(df, exclude_columns=exclude_columns)
    if not eligible_columns:
        raise ValueError("No eligible non-technical columns found for metadata profiling.")

    dtype_map = dict(df.dtypes)
    row_count = int(df.count())
    distributions = _build_distribution_summaries(
        df,
        eligible_columns,
        dtype_map,
        include_distributions=include_distributions,
        distribution_columns=distribution_columns,
        distribution_bin_edges=distribution_bin_edges,
        categorical_categories=categorical_categories,
        categorical_top_n=categorical_top_n,
    )

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
        select_exprs = [
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
        ]
        if include_distributions:
            distribution_type, distribution_payload = distributions.get(column_name, (None, None))
            select_exprs.extend(
                [
                    F.lit(distribution_type).cast("string").alias("DISTRIBUTION_TYPE"),
                    F.lit(json.dumps(distribution_payload, sort_keys=True) if distribution_payload is not None else None).cast("string").alias("DISTRIBUTION_JSON"),
                ]
            )
        rows.append(agg_df.select(*select_exprs))

    out = rows[0]
    for next_row in rows[1:]:
        out = out.unionByName(next_row)
    return out
