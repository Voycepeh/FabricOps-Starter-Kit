"""Public source freshness guardrail check."""

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.pipeline.guardrail_metadata import (
    freshness_check_core,
    load_table_guardrail_rules,
    resolve_change_rule_observation_columns,
    select_table_guardrail_rule,
)
from fabricops_kit.pipeline.guardrail_results import write_guardrail_result_row
from fabricops_kit.pipeline.shared import (
    guardrail_compatibility_observation,
    observation_rows,
)

_OBSERVATION_COLUMNS = {
    "observation_id",
    "table_id",
    "environment_name",
    "partition_value",
    "row_count",
    "min_change_value",
    "max_change_value",
    "is_present",
    "_committed_at",
    "_activity_id",
}


def _is_source_observation(observation) -> bool:
    columns = set(getattr(observation, "columns", ()))
    if not columns and isinstance(observation, (list, tuple)) and observation:
        columns = set(dict(observation[0]))
    return _OBSERVATION_COLUMNS <= columns


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
    if not _is_source_observation(observation):
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
    result = freshness_check_core(
        compatibility_observation,
        rules_df=rules_df,
        environment_name=env,
        metadata_table_key=table_id,
    )
    if result.get("guardrail_rule_id"):
        result["expected"] = {"max_lag_days": result.get("freshness_max_lag_days")}
        result["actual"] = {
            "latest_observed_change_value": result.get("latest_value"),
            "required_min_value": result.get("required_min_value"),
        }
        write_guardrail_result_row(
            spark_session=spark_session,
            config=config,
            env=env,
            run_id=str(first.get("_activity_id") or ""),
            dataset_name="",
            table_name="",
            store_type="",
            layer="",
            schema_name=None,
            guardrail_type="freshness",
            rule_type=str(result.get("rule_type") or ""),
            result=result,
        )
    return result
