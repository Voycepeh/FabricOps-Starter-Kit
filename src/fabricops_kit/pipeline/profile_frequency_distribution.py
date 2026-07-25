"""Public notebook-facing frequency profiling callable."""

from __future__ import annotations

from fabricops_kit.pipeline.shared import FREQUENCY_PROFILE_COLUMNS, build_frequency_distribution_dataframe


def profile_frequency_distribution(df, *, columns=None, top_n: int | None = None):
    """Calculate exact value frequencies for selected Spark DataFrame columns.

    The function profiles the complete DataFrame exactly as supplied by the
    caller and does not perform sampling internally. By default, all
    eligible non-technical scalar columns are selected and every distinct
    value is returned for each selected column, including null. Returned
    values are converted to their string representation,
    ``FREQUENCY_PERCENT`` is calculated from the total number of rows in the
    supplied DataFrame, and rankings are calculated independently for each
    profiled column.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Spark DataFrame to profile exactly as supplied by the caller.
    columns : list[str] or set[str] or tuple[str, ...], optional
        Source columns to profile. When supplied, each named column is
        profiled. When omitted, eligible non-technical scalar columns are
        selected automatically. Array, map, struct, and binary columns are
        excluded from automatic selection.
    top_n : int or None, optional
        Optional maximum ranked frequency rows to retain per profiled column.
        ``None`` returns every distinct value. A positive integer restricts
        output size only; it does not sample the DataFrame or avoid counting
        all distinct values before ranking them.

    Returns
    -------
    pyspark.sql.DataFrame
        A Spark DataFrame containing ranked frequency rows for each selected
        input column. Each row represents one distinct value,
        including null, and contains its count, percentage, rank, source data
        type, total profiled row count, and non-null count. Returned columns
        are ``COLUMN_NAME`` (profiled input column name), ``DATA_TYPE`` (Spark
        data type of the input column), ``VALUE`` (distinct value converted to
        a string; null remains null), ``FREQUENCY_COUNT`` (number of input rows
        containing the value), ``FREQUENCY_PERCENT`` (percentage of all
        supplied DataFrame rows containing the value), ``FREQUENCY_RANK``
        (rank within the profiled column ordered by descending frequency),
        ``PROFILED_ROW_COUNT`` (total number of rows in the supplied
        DataFrame), and ``PROFILED_NON_NULL_COUNT`` (number of non-null rows
        for the profiled column).

    Notes
    -----
    The function performs an exact Spark grouped count over the supplied
    DataFrame for every selected column. ``top_n`` optionally limits the
    returned rows, not the cost of grouping all distinct values. Full
    frequency output may be expensive for identifiers, timestamps, free text,
    and other high-cardinality columns. For large DataFrames,
    explicitly select useful categorical or low-to-medium-cardinality columns
    and generally avoid identifiers, UUIDs, timestamps, free-text fields, and
    columns where most values are unique. For exploratory analysis, callers may
    pass a manually filtered or sampled DataFrame; when they do, the returned
    counts and percentages describe that filtered or sampled input rather than
    the original full DataFrame.

    Raises
    ------
    ValueError
        If ``top_n`` is not greater than zero or a requested column is missing.

    """
    return build_frequency_distribution_dataframe(df, columns=columns, top_n=top_n)
