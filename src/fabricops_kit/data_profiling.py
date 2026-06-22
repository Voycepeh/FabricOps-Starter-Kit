"""Fabric-first profiling utilities for standardized metadata evidence.

This public facade preserves notebook-facing profiling imports while delegating
the implementation to role-organized private profiling internals.
"""

from __future__ import annotations

from typing import Any

from ._profiling_workflows import profile_dataframe_core as _profile_dataframe_workflow


# ---------------------------------------------------------------------------
# Internal workflow compatibility layer
# ---------------------------------------------------------------------------

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
    """Delegate profiling to the owning private profiling workflow.

    Parameters
    ----------
    df : Any
        Spark DataFrame to profile.
    table_name : str
        Logical table name written into each profile row.
    exclude_columns : list[str] or set[str], optional
        Additional columns to skip, on top of standard technical columns.
    run_timestamp_timezone : str, optional
        Explicit IANA time zone used for profile evidence timestamps.
    config : Any, optional
        Framework-like configuration carrying audit settings.
    include_distributions : bool, default=False
        Whether to include distribution metadata.
    distribution_columns : list[str] or set[str] or tuple[str, ...], optional
        Columns to profile with distributions.
    distribution_bin_edges : dict[str, list[float]], optional
        Explicit numeric bin edges by column.
    categorical_categories : dict[str, list[str]], optional
        Explicit categorical values by column.
    categorical_top_n : int, default=20
        Maximum categorical values to include when inferred.

    Returns
    -------
    Any
        Metadata-compatible profile DataFrame.

    """
    return _profile_dataframe_workflow(
        df,
        table_name,
        exclude_columns=exclude_columns,
        run_timestamp_timezone=run_timestamp_timezone,
        config=config,
        include_distributions=include_distributions,
        distribution_columns=distribution_columns,
        distribution_bin_edges=distribution_bin_edges,
        categorical_categories=categorical_categories,
        categorical_top_n=categorical_top_n,
    )


# ---------------------------------------------------------------------------
# Public API layer
# ---------------------------------------------------------------------------

def profile_dataframe(
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
        Additional columns to skip, on top of standard technical columns.
    run_timestamp_timezone : str, optional
        Explicit IANA time zone used for profile evidence timestamps.
    config : Any, optional
        Framework-like configuration carrying audit settings.
    include_distributions : bool, default=False
        Whether to include distribution metadata.
    distribution_columns : list[str] or set[str] or tuple[str, ...], optional
        Columns to profile with distributions.
    distribution_bin_edges : dict[str, list[float]], optional
        Explicit numeric bin edges by column.
    categorical_categories : dict[str, list[str]], optional
        Explicit categorical values by column.
    categorical_top_n : int, default=20
        Maximum categorical values to include when inferred.

    Returns
    -------
    pyspark.sql.DataFrame
        Metadata-compatible profile DataFrame.

    """
    return profile_dataframe_core(
        df,
        table_name,
        exclude_columns=exclude_columns,
        run_timestamp_timezone=run_timestamp_timezone,
        config=config,
        include_distributions=include_distributions,
        distribution_columns=distribution_columns,
        distribution_bin_edges=distribution_bin_edges,
        categorical_categories=categorical_categories,
        categorical_top_n=categorical_top_n,
    )
