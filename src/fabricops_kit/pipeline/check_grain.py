"""Internal first-class table Grain enforcement, independent of Data Quality."""

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.pipeline.shared import (
    load_table_guardrail_rules,
    observation_rows,
    print_guardrail_result,
    resolve_catalogue_table_identity,
    resolve_pipeline_data_contract,
    grain_check_core,
    write_guardrail_result_row,
)


def check_grain(dataframe, *, table_id, scope, verbose=True, context=None):
    """Record the selected Grain result before orchestration decides continuation."""
    config, active_workspace_id, context = resolve_fabric_context() if context is None else (context["config"], context["scope_workspace_id"], context)
    spark_session = get_spark_session(dataframe=dataframe, context=context)
    spark = spark_session
    contract = resolve_pipeline_data_contract(config, active_workspace_id, table_id, spark_session=spark, context=context)
    rules = observation_rows(load_table_guardrail_rules(config, active_workspace_id, table_id=table_id, spark_session=spark, context=context)) if contract else []
    grains = [rule for rule in rules if rule.get("guardrail_type") == "grain" and rule.get("is_active", True)]
    if not grains:
        return {"status": "skipped", "can_continue": True, "checks": [], "reason": "Grain is not enforced."}
    if len(grains) != 1:
        raise ValueError("A Data Contract has one Grain definition.")
    rule = grains[0]
    result = grain_check_core(dataframe, rule, scope=scope)
    identity = resolve_catalogue_table_identity(config, active_workspace_id, table_id, spark_session=spark, context=context)
    write_guardrail_result_row(
        spark_session=spark, config=config, active_workspace_id=active_workspace_id, run_id="", dataset_name="",
        table_name=identity["table_name"], store_type=identity["store_type"], layer=identity["store"],
        schema_name=identity["schema"], guardrail_type="grain", rule_type="uniqueness",
        result=result, table_id=table_id, contract_id=contract["contract_id"],
        contract_version=contract["contract_version"], context=context,
    )
    print_guardrail_result("Grain", result, verbose=verbose, table_id=table_id, config=config, active_workspace_id=active_workspace_id, spark_session=spark, context=context)
    return result
