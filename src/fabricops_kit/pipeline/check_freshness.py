"""Public source freshness guardrail check."""

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.pipeline.guardrails_shared import (
    freshness_check_core,
    load_table_guardrail_rules,
    resolve_change_rule_observation_columns,
    select_table_guardrail_rule,
    write_guardrail_result_row,
)
from fabricops_kit.pipeline.observation_shared import (
    guardrail_compatibility_observation,
    is_source_observation,
    observation_rows,
)


def check_freshness(observation) -> dict:
    """Check whether a source satisfies configured freshness intent.
    
    Parameters
    ----------
    observation : pyspark.sql.DataFrame
        Canonical evidence returned by :func:`observe_table`.
    
    Returns
    -------
    dict
        Structured freshness evidence and continuation decision. Governed
        observation checks append the outcome to ``METADATA_GUARDRAIL_RESULTS``.
    
    Examples
    --------
    >>> observation = observe_table("orders", target="source", schema="dbo")
    >>> result = check_freshness(observation)

    """
    if not is_source_observation(observation):
        raise ValueError("observation must be canonical evidence returned by observe_table()")
    rows = observation_rows(observation)
    if not rows:
        raise ValueError("observation must contain at least one canonical evidence row")
    first = rows[0]
    table_id = str(first.get("table_id") or "")
    environment_name = str(first.get("environment_name") or "")
    if not table_id or not environment_name:
        raise ValueError("observation must contain table_id and environment_name")
    if any(str(row.get("table_id") or "") != table_id for row in rows):
        raise ValueError("observation dataframe must contain one shared table_id")
    if any(str(row.get("environment_name") or "") != environment_name for row in rows):
        raise ValueError("observation dataframe must contain one shared environment_name")

    config, env, _context = resolve_fabric_context()
    if environment_name != env:
        raise ValueError(
            f"observation environment_name {environment_name!r} does not match active environment {env!r}."
        )
    spark_session = getattr(observation, "sparkSession", None) or get_spark_session()
    rules_df = load_table_guardrail_rules(config, env, spark_session=spark_session)
    freshness_rule = select_table_guardrail_rule(
        rules_df,
        guardrail_type="freshness",
        metadata_table_key=table_id,
        environment_name=env,
    )
    if freshness_rule is None:
        raise ValueError(f"No active approved freshness rule exists for {table_id!r}.")
    change_rule = select_table_guardrail_rule(
        rules_df,
        guardrail_type="change",
        metadata_table_key=table_id,
        environment_name=env,
    )
    if change_rule is None:
        raise ValueError(
            f"No active approved source-change rule exists for {table_id!r}; "
            "the observation change column cannot be resolved."
        )
    _partition_column, change_column = resolve_change_rule_observation_columns(change_rule)
    compatibility_observation = guardrail_compatibility_observation(
        observation,
        table_id=table_id,
        change_column=change_column,
    )
    table_name = str(freshness_rule.get("table_name") or change_rule.get("table_name") or "")
    result = freshness_check_core(
        compatibility_observation,
        rules_df=rules_df,
        table_name=table_name,
        environment_name=env,
        metadata_table_key=table_id,
    )
    if result.get("rule_key"):
        result["metadata_table_key"] = table_id  # in-memory Stage 4 compatibility only
        result["expected"] = {"max_lag_days": result.get("freshness_max_lag_days")}
        result["actual"] = {
            "latest_observed_change_value": result.get("latest_value"),
            "required_min_value": result.get("required_min_value"),
        }
        write_guardrail_result_row(
            spark_session=spark_session,
            config=config,
            env=env,
            run_id=str(first.get("observed_at") or ""),
            dataset_name=str(freshness_rule.get("dataset_name") or ""),
            table_name=table_name,
            store_type="",
            layer="",
            schema_name=None,
            guardrail_type="freshness",
            rule_type=str(result.get("rule_type") or ""),
            result=result,
            rule_key=str(result["rule_key"]),
        )
    return result
