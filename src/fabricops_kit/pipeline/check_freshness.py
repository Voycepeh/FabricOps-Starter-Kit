"""Public source freshness guardrail check."""

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.pipeline.shared import (
    freshness_check_core,
    load_table_guardrail_rules,
    resolve_source_drift_observation_columns,
    resolve_catalogue_table_identity,
    resolve_pipeline_data_contract,
    select_table_guardrail_rule,
)
from fabricops_kit.pipeline.shared import write_guardrail_result_row
from fabricops_kit.pipeline.shared import (
    guardrail_compatibility_observation,
    observation_rows,
    get_current_source_observation,
    print_guardrail_result,
)

_OBSERVATION_COLUMNS = {
    "observation_id",
    "source_table_id",
    "target_table_id",
    "environment_name",
    "partition_value",
    "row_count",
    "min_change_value",
    "max_change_value",
    "is_present",
    "observation_status",
    "_committed_at",
    "_activity_id",
}


def _is_source_observation(observation) -> bool:
    columns = set(getattr(observation, "columns", ()))
    if not columns and isinstance(observation, (list, tuple)) and observation:
        columns = set(dict(observation[0]))
    return _OBSERVATION_COLUMNS <= columns


def check_freshness(
    table_id: str,
    *,
    enabled: bool = True,
    raise_on_failure: bool = False,
    verbose: bool = True,
) -> dict:
    """Check whether a source satisfies configured freshness intent.
    
    Parameters
    ----------
    table_id : str
        Canonical governed source identity returned by :func:`pipeline_read`.
    enabled : bool, default=True
        Explicitly disable this check when ``False``. Normally omit this value;
        FabricOps enforces the resolved pipeline Data Contract automatically.
    raise_on_failure : bool, default=False
        Raise ``RuntimeError`` when a blocking freshness result cannot continue.
    verbose : bool, default=True
        Print the concise normalized check outcome when ``True``.
    
    Returns
    -------
    dict
        Structured freshness evidence and continuation decision. Governed
        observation checks append the outcome to ``METADATA_GUARDRAIL_RESULTS``.

    Raises
    ------
    ValueError
        If the observation or configured freshness rule is invalid.
    RuntimeError
        If ``raise_on_failure=True`` and a blocking freshness result cannot
        continue.

    Notes
    -----
    Production resolves expectations from the active Data Contract. Development
    uses an explicitly selected immutable version, or safely skips when none is
    selected.
    
    Examples
    --------
    >>> result = check_freshness(source_result["table_id"])

    """
    if not enabled:
        result = {"status": "skipped", "can_continue": True, "checks": []}
        print_guardrail_result("Freshness", result, verbose=verbose, table_id=table_id)
        if verbose:
            print("  Evaluation skipped by caller; no freshness rule evaluated or evidence written.")
        return result
    config, env, context = resolve_fabric_context()
    requested_table_id = str(table_id).strip()
    contract = resolve_pipeline_data_contract(
        config,
        env,
        requested_table_id,
        context=context,
    )
    if contract is None:
        result = {
            "status": "skipped",
            "can_continue": True,
            "checks": [],
            "reason": "No Data Contract selected; Development only.",
            "table_id": requested_table_id,
            "environment_name": env,
        }
        print_guardrail_result("Freshness", result, verbose=verbose, table_id=requested_table_id)
        if verbose:
            print(f"  Reason {result['reason']}")
        return result


    audit = build_runtime_audit_fields(config=config, env=env, runtime_context=context)
    observation = get_current_source_observation(
        environment_name=env,
        activity_id=str(audit["_activity_id"]),
        table_id=requested_table_id,
    )
    if not _is_source_observation(observation):
        raise ValueError("pipeline_read() captured invalid source observation state")
    rows = observation_rows(observation)
    if not rows:
        raise ValueError("observation must contain at least one canonical evidence row")
    first = rows[0]
    observed_table_id = str(first.get("source_table_id") or "")
    environment_name = str(first.get("environment_name") or "")
    if not observed_table_id or not environment_name:
        raise ValueError("observation must contain source_table_id and environment_name")
    if any(str(row.get("source_table_id") or "") != observed_table_id for row in rows):
        raise ValueError("observation dataframe must contain one shared source_table_id")
    if any(str(row.get("environment_name") or "") != environment_name for row in rows):
        raise ValueError("observation dataframe must contain one shared environment_name")

    if environment_name != env:
        raise ValueError(
            f"observation environment_name {environment_name!r} does not match active environment {env!r}."
        )
    spark_session = getattr(observation, "sparkSession", None) or get_spark_session()
    if requested_table_id != observed_table_id:
        raise ValueError(f"table_id {requested_table_id!r} does not match observation table_id {observed_table_id!r}.")
    identity = resolve_catalogue_table_identity(
        config,
        env,
        requested_table_id,
        spark_session=spark_session,
        context=context,
    )
    table_id = identity["table_id"]
    rules_df = load_table_guardrail_rules(
        config,
        env,
        spark_session=spark_session,
        table_id=table_id,
        context=context,
    )
    freshness_rule = select_table_guardrail_rule(
        rules_df,
        guardrail_type="freshness",
        table_id=table_id,
        environment_name=env,
    )
    if freshness_rule is None:
        raise ValueError(f"No active approved freshness rule exists for {table_id!r}.")
    change_rule = select_table_guardrail_rule(
        rules_df,
        guardrail_type="source_drift",
        table_id=table_id,
        environment_name=env,
    )
    if change_rule is None:
        raise ValueError(
            f"No active approved Source Drift rule exists for {table_id!r}; "
            "the observation change column cannot be resolved."
        )
    _partition_column, change_column = resolve_source_drift_observation_columns(change_rule)
    compatibility_observation = guardrail_compatibility_observation(
        observation,
        table_id=table_id,
        change_column=change_column,
    )
    result = freshness_check_core(
        compatibility_observation,
        rules_df=rules_df,
        environment_name=env,
        table_id=table_id,
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
    print_guardrail_result("Freshness", result, verbose=verbose, table_id=table_id)
    if verbose:
        print(
            f"  Rule {result.get('guardrail_rule_id', '')} v{result.get('guardrail_version', 1)} from the selected Data Contract."
        )
        print(f"  Observation change column {change_column} from current-run Source Observation state.")
        print(
            f"  Expected max lag {result.get('freshness_max_lag_days')} day(s); "
            f"latest observed={result.get('latest_value')}, required minimum={result.get('required_min_value')}."
        )
        print("  Evidence appended to METADATA_GUARDRAIL_RESULTS.")
    if raise_on_failure and not result["can_continue"]:
        raise RuntimeError(f"A blocking freshness Guardrail failed for table_id {table_id!r}.")
    return result
