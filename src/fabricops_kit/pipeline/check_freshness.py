"""Public source freshness guardrail check."""

from datetime import date, datetime

from fabricops_kit.pipeline.guardrails_shared import freshness_check_core


def check_freshness(
    dataframe,
    freshness_column: str | None = None,
    max_lag_days: int | str | None = None,
    severity: str = "blocking",
    *,
    reference_date: date | datetime | str | None = None,
    rules_df=None,
    dataset_name: str = "",
    table_name: str = "",
    environment_name: str = "",
    metadata_table_key: str = "",
) -> dict:
    """Check whether a source satisfies configured freshness intent.

    Parameters
    ----------
    dataframe : Any
        Spark DataFrame or iterable of row-like mappings.
    freshness_column : str, optional
        Column whose maximum date is the latest source observation.
    max_lag_days : int or str, optional
        Maximum permitted lag in days.
    severity : {"blocking", "warning"}, default="blocking"
        Failure behavior for a direct check.
    reference_date : date, datetime, str, optional
        Comparison date, defaulting to today.
    rules_df : DataFrame or iterable of mappings, optional
        Approved rules used instead of direct freshness arguments.
    dataset_name, table_name, environment_name, metadata_table_key : str, optional
        Table identity used to select an approved rule.

    Returns
    -------
    dict
        Structured freshness evidence and continuation decision.

    Examples
    --------
    >>> result = check_freshness(rows, "business_date", 2)

    """
    if rules_df is not None:
        return freshness_check_core(
            dataframe,
            rules_df=rules_df,
            dataset_name=dataset_name,
            table_name=table_name,
            environment_name=environment_name,
            metadata_table_key=metadata_table_key,
            reference_date=reference_date,
        )
    return freshness_check_core(
        dataframe,
        freshness_column,
        max_lag_days,
        severity=severity,
        reference_date=reference_date,
    )
