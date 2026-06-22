"""Spark adapters for profiling aggregation and distribution summaries."""

from __future__ import annotations

from typing import Any


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

