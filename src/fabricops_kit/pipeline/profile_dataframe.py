"""Public notebook-facing DataFrame profiling callable."""

from __future__ import annotations

from fabricops_kit.pipeline.shared import build_profile_dataframe


def profile_dataframe(df, *, exclude_columns=None, approximate_distinct: bool = True):
    """Return structural and statistical profile rows for a Spark DataFrame.

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
        Spark DataFrame with one row per eligible source column and the
        documented profiling columns.

    Raises
    ------
    ValueError
        If no eligible non-technical columns remain after exclusions.

    """
    return build_profile_dataframe(df, exclude_columns=exclude_columns, approximate_distinct=approximate_distinct)
