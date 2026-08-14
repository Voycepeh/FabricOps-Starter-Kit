"""Public source freshness guardrail check."""

from fabricops_kit.config.shared import get_store, resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.pipeline.guardrails_shared import freshness_check_core, load_table_guardrail_rules, select_table_guardrail_rule, write_guardrail_result_row


def check_freshness(
    observation,
) -> dict:
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
    columns = set(getattr(observation, "columns", ()))
    if not columns and isinstance(observation, (list, tuple)) and observation:
        first = observation[0]
        columns = set(first.asDict(recursive=True) if hasattr(first, "asDict") else first)
    observation_evidence = {
        "metadata_table_key", "partition_value", "change_column",
        "max_change_value", "observed_at",
    } <= columns
    if not observation_evidence:
        raise ValueError("observation must be canonical evidence returned by observe_table()")
    rows = observation.collect() if hasattr(observation, "collect") else observation
    if not rows:
        raise ValueError("observation must contain at least one canonical evidence row")
    first = rows[0].asDict(recursive=True) if hasattr(rows[0], "asDict") else dict(rows[0])
    config, env, _context = resolve_fabric_context()
    metadata_table_key = str(first.get("metadata_table_key") or "")
    table_name = str(first.get("source_table") or "")
    rules_df = load_table_guardrail_rules(
        config, env, spark_session=getattr(observation, "sparkSession", None),
    )
    if select_table_guardrail_rule(
        rules_df, guardrail_type="freshness", metadata_table_key=metadata_table_key,
        environment_name=env,
    ) is None:
        raise ValueError(f"No active approved freshness rule exists for {metadata_table_key!r}.")
    result = freshness_check_core(
        observation, rules_df=rules_df, table_name=table_name,
        environment_name=env, metadata_table_key=metadata_table_key,
    )
    if result.get("rule_key"):
        source_target = str(first.get("source_target") or "source")
        source_store_type = str(get_store(config, env, source_target).kind).lower()
        result["metadata_table_key"] = metadata_table_key
        result["expected"] = {"max_lag_days": result.get("freshness_max_lag_days")}
        result["actual"] = {
            "latest_observed_change_value": result.get("latest_value"),
            "required_min_value": result.get("required_min_value"),
        }
        write_guardrail_result_row(
            spark_session=getattr(observation, "sparkSession", None) or get_spark_session(),
            config=config, env=env, run_id=str(first.get("observed_at") or ""),
            dataset_name="", table_name=table_name, store_type=source_store_type,
            layer=source_target, schema_name=first.get("source_schema"),
            guardrail_type="freshness", rule_type=str(result.get("rule_type")),
            result=result, rule_key=str(result["rule_key"]),
        )
    return result
