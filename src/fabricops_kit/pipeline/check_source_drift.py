"""Internal Source Drift Guardrail check for a source-to-target relationship."""

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.pipeline.shared import (
    check_source_drift_for_target,
    resolve_catalogue_table_identity,
    resolve_pipeline_data_contract,
    resolve_table_processing_definition,
    validated_processing,
    print_guardrail_result,
)


def check_source_drift(
    source_table_id: str,
    *,
    target_table_id: str,
    spark_session=None,
    verbose: bool = True,
    context=None,
) -> dict:
    """Evaluate the resolved contract stage and return its continuation decision."""
    config, env, context = resolve_fabric_context() if context is None else (context["config"], context["env"], context)
    spark_session = get_spark_session() if spark_session is None else spark_session
    contract = resolve_pipeline_data_contract(
        config,
        env,
        str(source_table_id).strip(),
        spark_session=spark_session,
        context=context,
    )
    if contract is None:
        result = {
            "status": "skipped",
            "can_continue": True,
            "checks": [],
            "reason": "Explicit No Contract selected.",
            "source_table_id": str(source_table_id).strip(),
            "target_table_id": str(target_table_id).strip(),
            "environment_name": env,
        }
        print_guardrail_result(
            "Source Drift",
            result,
            verbose=verbose,
            source_table_id=str(source_table_id).strip(),
            target_table_id=str(target_table_id).strip(),
            config=config,
            env=env,
            spark_session=spark_session,
            context=context,
        )
        if verbose:
            print(f"  Reason {result['reason']}")
        return result
    source = resolve_catalogue_table_identity(
        config, env, source_table_id, spark_session=spark_session, context=context
    )
    target = resolve_catalogue_table_identity(
        config, env, target_table_id, spark_session=spark_session, context=context
    )
    source_load_strategy = str(source.get("load_strategy") or "").strip().lower()
    processing_origin = "FabricOps Catalogue"
    if source_load_strategy:
        parameters = {name: value for name, value in (source.get("load_strategy_parameters_json") or {}).items()
                      if value is not None}
        authored_processing = {"load_strategy": source_load_strategy, **parameters}
        source_processing = resolve_table_processing_definition(
            config,
            env,
            str(source["table_id"]),
            spark_session=spark_session,
            context=context,
            authored_processing=authored_processing,
        )
    else:
        payload = contract.get("contract_payload") or {}
        table_payload = payload.get("table") if isinstance(payload, dict) else None
        processing = table_payload.get("processing") if isinstance(table_payload, dict) else None
        try:
            source_processing = validated_processing(processing)
        except ValueError as exc:
            raise ValueError(
                "Source Drift cannot determine the source load strategy. "
                "This source has no FabricOps-written load strategy in the Catalogue "
                "and its selected Data Contract has no valid processing definition."
            ) from exc
        source_load_strategy = str(source_processing["load_strategy"]).lower()
        processing_origin = "Data Contract"
    result = check_source_drift_for_target(
        source_table_id=str(source["table_id"]),
        target_table_id=str(target["table_id"]),
        source_processing=source_processing,
        spark_session=spark_session,
        context=context,

    )
    print_guardrail_result(
        "Source Drift",
        result,
        verbose=verbose,
        source_table_id=source_table_id,
        target_table_id=str(target["table_id"]),
        config=config,
        env=env,
        spark_session=spark_session,
        context=context,
    )
    if verbose:
        print(
            f"  Source processing {str(source_processing.get('load_strategy') or '').upper()} from {processing_origin}."
        )
        print(
            f"  Comparison scope {result.get('comparison_scope', 'configured')} against the last accepted source-to-target baseline."
        )
        print(
            "  Changes "
            f"inserted={result.get('inserted_count', 0)}, "
            f"updated={result.get('updated_count', 0)}, "
            f"deleted={result.get('deleted_count', 0)}, "
            f"recent={result.get('recent_changes', 0)}, "
            f"historical={result.get('historical_changes', 0)}."
        )
        print("  Accepted baseline is committed only after pipeline_write() succeeds.")
    return result
