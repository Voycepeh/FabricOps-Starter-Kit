"""Public notebook-facing DataFrame profiling callable."""

from __future__ import annotations

from fabricops_kit.pipeline.shared import build_profile_dataframe


def profile_dataframe(df, *, exclude_columns=None, approximate_distinct: bool = True):
    """Calculate column-level profiling statistics for a Spark DataFrame.

    The returned profile includes row and null counts, null percentages,
    distinct counts and percentages, numeric summary statistics, and minimum
    and maximum values for each included input column.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to profile.
    exclude_columns : list[str] or set[str], optional
        Additional caller-selected columns to skip after standard FabricOps
        technical-column exclusions are applied.
    approximate_distinct : bool, default=True
        When True, use Spark ``approx_count_distinct`` for per-column
        cardinality. When False, use exact ``count_distinct``.

    Returns
    -------
    pyspark.sql.DataFrame
        Spark DataFrame containing one profiling row for each column in the
        input DataFrame, excluding FabricOps technical columns and any columns
        supplied through ``exclude_columns``. Returned columns are
        ``COLUMN_NAME`` (input column name), ``DATA_TYPE`` (Spark data type),
        ``ROW_COUNT`` (rows in ``df``), ``NON_NULL_COUNT`` (non-null values),
        ``NULL_COUNT`` (null values), ``NULL_PERCENT`` (null percentage),
        ``DISTINCT_COUNT`` (distinct value count), ``DISTINCT_PERCENT``
        (distinct value percentage), ``MEAN`` (numeric average), ``STDDEV``
        (numeric sample standard deviation), ``MIN_VALUE`` (minimum value as a
        string when supported), ``PERCENTILE_25`` (25th percentile for numeric
        columns), ``MEDIAN`` (50th percentile for numeric columns),
        ``PERCENTILE_75`` (75th percentile for numeric columns), and
        ``MAX_VALUE`` (maximum value as a string when supported).

    Raises
    ------
    ValueError
        If no eligible non-technical columns remain after exclusions.

    """
    return build_profile_dataframe(df, exclude_columns=exclude_columns, approximate_distinct=approximate_distinct)
