"""Internal preparation-first Sensitive Data Guardrail enforcement."""

from __future__ import annotations

from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.pipeline.shared import (
    check_sensitive_data_rules,
    load_table_guardrail_rules,
    observation_rows,
    resolve_pipeline_data_contract,
    resolve_catalogue_table_identity,
    write_guardrail_result_row,
    print_guardrail_result,
)


def check_sensitive_data(
    dataframe,
    *,
    table_id: str,
    run_id: str = "",
    existing_mapping=None,
    verbose: bool = True,
    context=None,
) -> dict:
    """Evaluate the resolved contract stage and return its continuation decision."""
    config, env, context = resolve_fabric_context() if context is None else (context["config"], context["env"], context)
    spark_session = get_spark_session(dataframe=dataframe, context=context)
    contract = resolve_pipeline_data_contract(config, env, table_id, spark_session=spark_session, context=context)
    if contract is None:
        result = {
            "status": "skipped",
            "can_continue": True,
            "dataframe": dataframe,
            "support_mapping": None,
            "checks": [],
            "reason": "Explicit No Contract selected.",
        }
        print_guardrail_result(
            "Sensitive Data",
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
    identity = resolve_catalogue_table_identity(config, env, table_id, spark_session=spark_session, context=context)
    rules = [
        row
        for row in observation_rows(
            load_table_guardrail_rules(
                config,
                env,
                spark_session=spark_session,
                table_id=identity["table_id"],
                context=context,
            )
        )
        if str(row.get("guardrail_type") or "").strip().lower() == "sensitive_data"
        and row.get("is_active", True) is not False
    ]
    result = check_sensitive_data_rules(
        dataframe,
        rules=rules,
        identity=identity,
        config=config,
        env=env,
        spark_session=spark_session,
        run_id=run_id,
        existing_mapping=existing_mapping,

        context=context,
    )
    print_guardrail_result(
        "Sensitive Data",
        result,
        verbose=verbose,
        table_id=table_id,
        config=config,
        env=env,
        spark_session=spark_session,
        context=context,
    )
    if verbose:
        checks = result["checks"]
        treatments = [str(check.get("treatment") or "unknown") for check in checks]
        print(f"  Contract selected; evaluated {len(checks)} active Sensitive Data rule(s).")
        print(f"  Treatments applied/evaluated: {', '.join(treatments) if treatments else 'none'}.")
        print("  Evidence appended to METADATA_GUARDRAIL_RESULTS without raw sensitive values.")
        print(
            "  Token mapping reused and persisted in the configured restricted store."
            if result.get("mapping_persisted") else
            "  Token support mapping returned to caller; Validate never persists mappings."
            if result["support_mapping"] is not None
            else "  No token support mapping produced."
        )
    return result
