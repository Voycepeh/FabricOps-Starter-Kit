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
    dataframe=None,
    read_mode="full",
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
    table_id = requested_table_id
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
    import json
    from fabricops_kit.pipeline.shared import collect_freshness_evidence, evaluate_freshness_evidence, validate_freshness_parameters
    parameters = validate_freshness_parameters(json.loads(freshness_rule["rule_parameters_json"]))
    if identity.get("source_type") == "file":
        from fabricops_kit.io.shared import resolve_configured_file_path
        from fabricops_kit.pipeline.shared import file_participant_source
        _, _, path = resolve_configured_file_path(identity["store"], identity["relative_path"], context=context)
        evidence = (collect_freshness_evidence(parameters, dataframe=dataframe,
            source={**file_participant_source(identity), "resolved_path": path}, spark_session=spark_session)
            if parameters["evaluation_scope"] == "full_dataset" else
            {"evidence_method": parameters["evidence_method"], "evaluation_scope": parameters["evaluation_scope"],
             "outcome": "unavailable", "reason": "Incremental batch scope is unavailable for full file Reads."})
    elif parameters["evaluation_scope"] == "incremental_batch":
        evidence = collect_freshness_evidence(parameters,
            dataframe=dataframe if read_mode == "incremental" else None,
            source={"source_type": "table", "table_id": table_id}, spark_session=spark_session)
    else:
        try:
            evidence = get_current_freshness_evidence(workspace_id=active_workspace_id,
                activity_id=source_observation_run_id(context) or str(audit["_activity_id"]), table_id=table_id)
        except ValueError:
            evidence = {"evidence_method": parameters["evidence_method"], "evaluation_scope": parameters["evaluation_scope"],
                        "outcome": "unavailable", "reason": "No current-run Source Observation is available."}
    result = evaluate_freshness_evidence(evidence, parameters, action=freshness_rule["action"])
    result.update(guardrail_rule_id=freshness_rule["guardrail_rule_id"],
                  guardrail_version=freshness_rule.get("guardrail_version", 1))
    if result.get("guardrail_rule_id"):
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
        print(f"  Evidence method {parameters['evidence_method']}; scope {parameters['evaluation_scope']}; outcome {result['evidence_outcome']}.")
        print("  Evidence appended to METADATA_GUARDRAIL_RESULTS.")
    return result
