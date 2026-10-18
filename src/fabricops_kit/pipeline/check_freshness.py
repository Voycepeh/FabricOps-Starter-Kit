"""Internal source freshness guardrail check."""

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.pipeline.shared import (
    freshness_check_core,
    get_current_freshness_evidence,
    load_table_guardrail_rules,
    resolve_catalogue_table_identity,
    resolve_pipeline_data_contract,
    select_table_guardrail_rule,
)
from fabricops_kit.pipeline.shared import write_guardrail_result_row
from fabricops_kit.pipeline.shared import (
    print_guardrail_result,
)


def check_freshness(
    table_id: str,
    *,
    spark_session=None,
    verbose: bool = True,
    context=None,
    execution_type="enforce",
) -> dict:
    """Evaluate the resolved contract stage and return its continuation decision."""
    config, env, context = resolve_fabric_context() if context is None else (context["config"], context["env"], context)
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
        print_guardrail_result(
            "Freshness",
            result,
            verbose=verbose,
            table_id=requested_table_id,
            config=config,
            env=env,
            spark_session=spark_session,
            context=context,
        )
        if verbose:
            print(f"  Reason {result['reason']}")
        return result
    audit = build_runtime_audit_fields(config=config, env=env, runtime_context=context)
    spark_session = get_spark_session() if spark_session is None else spark_session
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
    if str(freshness_rule.get("rule_type") or "").strip().lower() == "skip":
        result = freshness_check_core(
            [],
            rules_df=rules_df,
            environment_name=env,
            table_id=table_id,
        )
        print_guardrail_result(
            "Freshness",
            result,
            verbose=verbose,
            table_id=table_id,
            config=config,
            env=env,
            spark_session=spark_session,
            context=context,
        )
        if verbose:
            print("  No refresh is expected for this source; freshness age evaluation skipped.")
        return result
    evidence = get_current_freshness_evidence(
        environment_name=env,
        activity_id=str(audit["_activity_id"]),
        table_id=table_id,
    )
    freshness_column = str(evidence["freshness_column"])
    result = freshness_check_core(
        [{freshness_column: evidence.get("latest_value")}],
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
            run_id=str(evidence.get("_activity_id") or ""),
            dataset_name="",
            table_name=str(identity.get("table_name") or ""),
            store_type="",
            layer="",
            schema_name=None,
            guardrail_type="freshness",
            rule_type=str(result.get("rule_type") or ""),
            result=result,
            table_id=table_id,
            contract_id=str(freshness_rule.get("contract_id") or ""),
            contract_version=int(freshness_rule.get("contract_version") or 0),
            execution_type=execution_type,
            context=context,
        )
    print_guardrail_result(
        "Freshness",
        result,
        verbose=verbose,
        table_id=table_id,
        config=config,
        env=env,
        spark_session=spark_session,
        context=context,
    )
    if verbose:
        print(
            f"  Rule {result.get('guardrail_rule_id', '')} v{result.get('guardrail_version', 1)} from the selected Data Contract."
        )
        print(f"  Freshness column {freshness_column} from the active Freshness rule.")
        print(
            f"  Expected max lag {result.get('freshness_max_lag_days')} day(s); "
            f"latest observed={result.get('latest_value')}, required minimum={result.get('required_min_value')}."
        )
        print("  Evidence appended to METADATA_GUARDRAIL_RESULTS.")
    return result
