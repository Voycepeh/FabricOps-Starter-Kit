"""Public deterministic changes check."""

from datetime import date, datetime

from fabricops_kit.pipeline.guardrails_shared import changes_check_core


def check_changes(
    dataframe,
    previous_dataframe=None,
    *,
    partition_columns: list[str] | tuple[str, ...] | None = None,
    key_columns: list[str] | tuple[str, ...] | None = None,
    non_key_columns: list[str] | tuple[str, ...] | None = None,
    range_column: str | None = None,
    source_pattern: str = "snapshot",
    comparison_scope: str = "complete",
    refresh_days: int = 0,
    version_column: str | None = None,
    reference_date: date | datetime | str | None = None,
    include_row_changes: bool = False,
) -> dict:
    """Describe deterministic row and partition changes since an observation.

    Parameters
    ----------
    dataframe : DataFrame or iterable of mappings
        Current source observation.
    previous_dataframe : DataFrame or iterable of mappings, optional
        Previous comparable source observation.
    partition_columns : sequence of str, optional
        Columns defining cheap partition fingerprints.
    key_columns : sequence of str
        Non-null columns that uniquely identify a logical row.
    non_key_columns : sequence of str, optional
        Columns whose content identifies an update. Defaults to all non-key
        columns, except that a versioned source's ``version_column`` is used
        only for latest-record resolution unless explicitly included here.
    range_column : str, optional
        Date, timestamp, or ordered range column used for recent and unseen
        range classification.
    source_pattern : {"snapshot", "incremental_append", "mutable_incremental", "versioned"}
        Explicit source behavior; it is never inferred from table naming.
    comparison_scope : {"complete", "partitions", "partial"}
        Completeness of the current observation. ``complete`` can prove global
        deletions, ``partitions`` can prove deletions only inside supplied
        complete partitions, and ``partial`` never infers deletions.
    refresh_days : int, default=0
        Number of days in the expected mutable window. Zero means only values
        dated on ``reference_date`` are recent.
    version_column : str, optional
        Column used to select the latest row per logical key. Required when
        ``source_pattern="versioned"``.
    reference_date : date, datetime, str, optional
        End of the recent mutable window.
    include_row_changes : bool, default=False
        Include deterministic key hashes grouped by change classification.

    Returns
    -------
    dict
        Structured changes summary, partition observations, counts, and
        observed ranges. This function does not merge or write target data.

    Raises
    ------
    ValueError
        If configuration is invalid or logical keys are null, missing, or
        duplicated.

    Examples
    --------
    >>> result = check_changes(current, previous, key_columns=["id"])
    >>> result["changed"]
    True

    """
    return changes_check_core(
        dataframe,
        previous_dataframe,
        partition_columns=partition_columns,
        key_columns=key_columns,
        non_key_columns=non_key_columns,
        range_column=range_column,
        source_pattern=source_pattern,
        comparison_scope=comparison_scope,
        refresh_days=refresh_days,
        version_column=version_column,
        reference_date=reference_date,
        include_row_changes=include_row_changes,
    )
