"""Fabric-first profiling utilities for standardized metadata evidence.

This module focuses on producing a stable, metadata-compatible metadata profile from a
Spark DataFrame. The profile can be written to metadata tables and reused as
profile evidence for deterministic data quality rule review.
"""

from __future__ import annotations

from .config import _audit_timestamp_expr, _get_audit_timezone
from ._profiling_resolvers import _get_profiled_columns, _is_min_max_supported_type
from ._profiling_adapters import _build_distribution_summaries

import json
import re
from typing import Any


def profile_dataframe_core(
    df,
    table_name: str,
    *,
    exclude_columns=None,
    run_timestamp_timezone: str | None = None,
    config: Any = None,
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
    run_timestamp_timezone : str, optional
        Explicit IANA time zone used for the ``RUN_TIMESTAMP`` evidence field.
        When omitted, ``config.audit_timezone`` is used and falls back to UTC.
    config : Any, optional
        Framework-like configuration carrying ``audit_timezone`` for audit
        timestamp consistency.
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

    run_timestamp_timezone = _get_audit_timezone(config=config, timezone_name=run_timestamp_timezone)
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
            _audit_timestamp_expr(timezone_name=run_timestamp_timezone).alias("RUN_TIMESTAMP"),
            F.lit(column_name).alias("COLUMN_NAME"),
            F.lit(dtype_map[column_name]).alias("DATA_TYPE"),
            F.lit(row_count).cast("long").alias("ROW_COUNT"),
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


