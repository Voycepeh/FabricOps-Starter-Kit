"""Internal source freshness guardrail check."""

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.pipeline.shared import (
    freshness_check_core,
    get_current_freshness_evidence,
    source_observation_run_id,
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
    verbose: bool = True,
    context=None,
) -> dict:
    """Evaluate the resolved contract stage and return its continuation decision."""
    config, active_workspace_id, context = resolve_fabric_context() if context is None else (context["config"], context["scope_workspace_id"], context)
    spark_session = get_spark_session(context=context)
    requested_table_id = str(table_id).strip()
    contract = resolve_pipeline_data_contract(
        config,
        active_workspace_id,
        requested_table_id,
        context=context,
    )
    if contract is None:
        result = {
            "status": "skipped",
            "can_continue": True,
            "checks": [],
            "reason": "Explicit No Contract selected.",
            "table_id": requested_table_id,
            "workspace_id": active_workspace_id,
        }
        print_guardrail_result(
            "Freshness",
            result,
            verbose=verbose,
            table_id=requested_table_id,
            config=config,
            active_workspace_id=active_workspace_id,
            spark_session=spark_session,
            context=context,
        )
        if verbose:
            print(f"  Reason {result['reason']}")
        return result
    audit = build_runtime_audit_fields(config=config, active_workspace_id=active_workspace_id, runtime_context=context)
    identity = resolve_catalogue_table_identity(
        config,
        active_workspace_id,
        requested_table_id,
        spark_session=spark_session,
        context=context,
    )
    table_id = identity["table_id"]
    rules_df = load_table_guardrail_rules(
        config,
        active_workspace_id,
        spark_session=spark_session,
        table_id=table_id,
        context=context,
    )
    freshness_rule = select_table_guardrail_rule(
        rules_df,
        guardrail_type="freshness",
        table_id=table_id,
        workspace_id=active_workspace_id,
    )
    if freshness_rule is None:
        raise ValueError(f"No active approved freshness rule exists for {table_id!r}.")
    if str(freshness_rule.get("rule_type") or "").strip().lower() == "skip":
        result = freshness_check_core(
            [],
            config=config,
            rules_df=rules_df,
            workspace_id=active_workspace_id,
            table_id=table_id,
        )
        print_guardrail_result(
            "Freshness",
            result,
            verbose=verbose,
            table_id=table_id,
            config=config,
            active_workspace_id=active_workspace_id,
            spark_session=spark_session,
            context=context,
        )
        if verbose:
            print("  No refresh is expected for this source; freshness age evaluation skipped.")
        return result
    evidence = get_current_freshness_evidence(
        workspace_id=active_workspace_id,
        activity_id=source_observation_run_id(context) or str(audit["_activity_id"]),
        table_id=table_id,
    )
    freshness_column = str(evidence["freshness_column"])
    result = freshness_check_core(
        [{freshness_column: evidence.get("latest_value")}],
        config=config,
        rules_df=rules_df,
        workspace_id=active_workspace_id,
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
            active_workspace_id=active_workspace_id,
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

            context=context,
        )
    print_guardrail_result(
        "Freshness",
        result,
        verbose=verbose,
        table_id=table_id,
        config=config,
        active_workspace_id=active_workspace_id,
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
