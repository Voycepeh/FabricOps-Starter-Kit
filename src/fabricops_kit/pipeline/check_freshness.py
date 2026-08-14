"""Public source freshness guardrail check."""

from datetime import date, datetime

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.pipeline.guardrails_shared import freshness_check_core, load_table_guardrail_rules, select_table_guardrail_rule, write_guardrail_result_row


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
        Approved rules used instead of direct freshness arguments. Canonical
        observation input loads the active rule automatically when omitted.
    dataset_name, table_name, environment_name, metadata_table_key : str, optional
        Table identity used to select an approved rule.

    Returns
    -------
    dict
        Structured freshness evidence and continuation decision. Governed
        observation checks append the outcome to ``METADATA_GUARDRAIL_RESULTS``.

    Examples
    --------
    >>> result = check_freshness(rows, "business_date", 2)

    """
    columns = set(getattr(dataframe, "columns", ()))
    if not columns and isinstance(dataframe, (list, tuple)) and dataframe:
        first = dataframe[0]
        columns = set(first.asDict(recursive=True) if hasattr(first, "asDict") else first)
    observation_evidence = {
        "metadata_table_key", "partition_value", "change_column",
        "max_change_value", "observed_at",
    } <= columns
    rows = dataframe.collect() if observation_evidence and hasattr(dataframe, "collect") else dataframe
    first = rows[0].asDict(recursive=True) if observation_evidence and rows and hasattr(rows[0], "asDict") else (dict(rows[0]) if observation_evidence and rows else {})
    if observation_evidence:
        config, env, _context = resolve_fabric_context()
        metadata_table_key = str(first.get("metadata_table_key") or "")
        table_name = str(first.get("source_table") or table_name)
        environment_name = env
    if observation_evidence and rules_df is None:
        rules_df = load_table_guardrail_rules(config, env, spark_session=getattr(dataframe, "sparkSession", None))
        if select_table_guardrail_rule(rules_df, guardrail_type="freshness", metadata_table_key=metadata_table_key, environment_name=env) is None:
            raise ValueError(f"No active approved freshness rule exists for {metadata_table_key!r}.")
    if rules_df is not None:
        result = freshness_check_core(
            dataframe,
            rules_df=rules_df,
            dataset_name=dataset_name,
            table_name=table_name,
            environment_name=environment_name,
            metadata_table_key=metadata_table_key,
            reference_date=reference_date,
        )
        if observation_evidence and result.get("rule_key"):
            result["metadata_table_key"] = metadata_table_key
            result["expected"] = {"max_lag_days": result.get("freshness_max_lag_days")}
            result["actual"] = {"latest_observed_change_value": result.get("latest_value"), "required_min_value": result.get("required_min_value")}
            write_guardrail_result_row(
                spark_session=getattr(dataframe, "sparkSession", None) or get_spark_session(), config=config,
                env=env, run_id=str(first.get("observed_at") or ""), dataset_name=dataset_name,
                table_name=table_name, store_type="lakehouse", layer=str(first.get("source_target") or "source"),
                schema_name=first.get("source_schema"), guardrail_type="freshness",
                rule_type=str(result.get("rule_type")), result=result, rule_key=str(result["rule_key"]),
            )
        return result
    return freshness_check_core(
        dataframe,
        "max_change_value" if observation_evidence else freshness_column,
        max_lag_days,
        severity=severity,
        reference_date=reference_date,
    )
