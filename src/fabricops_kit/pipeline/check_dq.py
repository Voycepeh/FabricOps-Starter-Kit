"""Internal governed data-quality runtime check."""

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.pipeline.shared import (
    check_dq_runtime,
    resolve_catalogue_table_identity,
    resolve_pipeline_data_contract,
    print_guardrail_result,
)


def check_dq(
    dataframe,
    *,
    table_id: str,
    dataset_name: str = "",
    run_id: str = "",
    row_identity_columns: list[str] | None = None,
    spark_session=None,
    verbose: bool = True,
    context=None,
    execution_type="enforce",
    diagnostics="sample",
) -> dict:
    """Evaluate the resolved contract stage and return its continuation decision."""
    config, env, context = resolve_fabric_context() if context is None else (context["config"], context["env"], context)
    if spark_session is None:
        spark_session = getattr(dataframe, "sparkSession", None)
    if spark_session is None:
        spark_session = get_spark_session()
    contract = resolve_pipeline_data_contract(
        config,
        env,
        table_id,
        spark_session=spark_session,
        context=context,
    )
    if contract is None:
        result = {
            "status": "skipped",
            "can_continue": True,
            "checks": [],
            "reason": "No Data Contract selected; Development only.",
            "table_id": table_id,
            "environment_name": env,
        }
        print_guardrail_result(
            "Data Quality",
            result,
            verbose=verbose,
            table_id=table_id,
            config=config,
            env=env,
            spark_session=spark_session,
            context=context,
        )
        if verbose:
            print(f"  Reason {result['reason']}")
        return result
    identity = resolve_catalogue_table_identity(
        config,
        env,
        table_id,
        spark_session=spark_session,
        context=context,
    )
    result = check_dq_runtime(
        dataframe,
        config,
        env,
        identity["table_name"],
        table_id=identity["table_id"],
        store=identity["store"],
        store_type=identity["store_type"],
        schema_name=identity["schema"],
        dataset_name=dataset_name,
        run_id=run_id,
        row_identity_columns=row_identity_columns,
        context=context,
        contract_id=str(contract.get("contract_id") or ""),
        contract_version=int(contract.get("contract_version") or 0),
        execution_type=execution_type,
        diagnostics=diagnostics,
    )
    print_guardrail_result(
        "Data Quality",
        result,
        verbose=verbose,
        table_id=table_id,
        config=config,
        env=env,
        spark_session=spark_session,
        context=context,
    )
    if verbose:
        checks = list(result.get("checks") or [])
        failed = [check for check in checks if str(check.get("status") or "").lower() not in {"passed", "pass"}]
        print(f"  Contract selected; evaluated {len(checks)} active DQ rule(s).")
        print(f"  Rule outcomes {len(checks) - len(failed)} passed, {len(failed)} warning/failed.")
        print("  Evidence appended to METADATA_GUARDRAIL_RESULTS for each evaluated rule.")
        summary = result.get("summary", {})
        print(f"  Applicable rows {summary.get('DQ_PASSED_ROW_PERCENT', 0):.2f}% pass, {summary.get('DQ_FAILED_ROW_PERCENT', 0):.2f}% with violations.")
        print("  Failure examples disabled." if diagnostics == "none" else
              "  Up to 10 examples per rule are stored with summaries; full diagnostics are opt-in.")
    return result
