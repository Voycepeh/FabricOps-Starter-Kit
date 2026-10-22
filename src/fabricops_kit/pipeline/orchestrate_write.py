"""Public owner for the standard governed target lifecycle."""
from __future__ import annotations
from typing import Any, Iterable
from datetime import UTC, datetime
from fabricops_kit.pipeline.check_dq import check_dq
from fabricops_kit.pipeline.check_grain import check_grain
from fabricops_kit.pipeline.check_schema import check_schema
from fabricops_kit.pipeline.check_sensitive_data import check_sensitive_data
from fabricops_kit.pipeline.check_source_drift import check_source_drift
from fabricops_kit.pipeline.pipeline_write import pipeline_write
from fabricops_kit.pipeline.profile_table import profile_table
from fabricops_kit.pipeline.resolve_table_id import resolve_table_id
from fabricops_kit.pipeline.shared import (
    ExecutionSummary,
    current_pipeline_session,
    PipelineOperation,
    execution_result,
    tested_contract_identities,
    source_guardrail_results,
    _run_orchestration_stage,
    prepare_pipeline_execution,
    pipeline_guardrail_types,
    print_pipeline_contract,
)


def orchestrate_write(dataframe: Any, *, store: str, schema: str | None, table_name: str, write_mode: str, write_parameters: dict[str, Any] | None = None, repartition_by: int | None = None, grain_discovery_enabled: bool = True, grain_discovery_max_columns: int = 3, grain_discovery_max_candidates: int = 8, frequency_enabled: bool = True, frequency_top_n: int | None = 5, existing_mapping=None, verbose: bool = False, dq_diagnostics: str = "sample") -> dict[str, Any]:
    """Evaluate or publish a target using the active pipeline's runtime.

    Define the dataframe, destination, write_mode and processing parameters.
    All reads registered in this execution are associated with this target as
    pipeline participants, not proven transformation dependencies. Test evaluates
    processing and Guardrails without publishing or committing metadata. Live
    requires approved contracts, ownership, destinations and a pinned revision.
    Advanced repartitioning, Sensitive Data mapping and DQ diagnostics remain
    available. The result includes publication metrics and Guardrail diagnostics.
    A successful Write does not imply successful completion of the notebook.

    Raises RuntimeError when no pipeline is active or a Live stage fails, and
    ValueError for an invalid operation or inconsistent approved configuration.

    Examples
    --------
    >>> result = orchestrate_write(summary_df, store="Gold", schema="demo",
    ...     table_name="customer_summary", write_mode="overwrite")

    """
    session = current_pipeline_session()
    spark_session = session.spark
    try:
        execution_plan = session.operation_plan("target", locals())
    except BaseException:
        session.close(failed=True)
        raise
    sources = tuple(session.sources)
    arguments = {key: value for key, value in locals().items() if key not in {"session"}}
    with PipelineOperation(execution_plan, "target", arguments) as operation:
        sources = operation.arguments["sources"]
        for name, value in (
            ("grain_discovery_max_columns", grain_discovery_max_columns),
            ("grain_discovery_max_candidates", grain_discovery_max_candidates),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer.")
        if dq_diagnostics not in {"none", "sample", "full"}:
            raise ValueError("dq_diagnostics must be 'none', 'sample', or 'full'.")
        summary = ExecutionSummary("WRITE", verbose=verbose)
        target = ".".join(str(part) for part in (store, schema, table_name) if part)
        sources = list(sources)
        if any(source.get("execution_plan_id") != execution_plan.plan_id for source in sources):
            raise ValueError("Every source must be a Read result from the same execution plan.")
        source_ids = [source["table_id"] for source in sources]
        target_id = resolve_table_id(store=store, schema=schema, table_name=table_name, context=execution_plan.runtime_context)
        context = prepare_pipeline_execution([target_id, *source_ids], execution_plan=execution_plan, spark_session=spark_session)
        if any("source" not in context["_pipeline_identities"][source_id]["roles"] for source_id in source_ids):
            raise ValueError("Every contributing source must have an explicit source role in the plan.")
        if "target" not in context["_pipeline_identities"][target_id]["roles"]:
            raise ValueError("Write requires an explicit target participant.")
        active = pipeline_guardrail_types(context, target_id)
        drift_ids = [source_id for source_id in source_ids if "source_drift" in pipeline_guardrail_types(context, source_id)]
        source_checks = source_guardrail_results(context, sources)
        names = []
        if "schema" in active:
            names.append("Schema")
        if "sensitive_data" in active:
            names.append("Sensitive Data")
        if drift_ids:
            names.append("Source Drift")
        if "grain" in active:
            names.append("Grain")
        if "data_quality" in active:
            names.append("Data Quality")
        if not execution_plan.permits_persistence:
            names.append("Processing")
        else:
            names.extend(["Write", "Profile"])
        stages = []
        if verbose:
            print(f"FabricOps WRITE · {table_name} · {execution_plan.execution_mode.title()}")
        print_pipeline_contract(context, target_id, operation="Write", guardrails=[name for name in names if name not in {"Write", "Profile", "Processing"}], verbose=verbose)
        def run(stage, function):
            result, record = _run_orchestration_stage(operation="WRITE", name=table_name, index=names.index(stage)+1, total=len(names), stage=stage, function=function, verbose=verbose, allow_blocked=not execution_plan.permits_persistence)
            stages.append(record)
            return result
        skipped = {"status": "skipped", "can_continue": True, "checks": []}
        sensitive = {**skipped, "dataframe": dataframe, "support_mapping": None}
        try:
            schema_result = run("Schema", lambda: check_schema(dataframe, table_id=target_id, spark_session=spark_session, verbose=False, context=context)) if "schema" in active else dict(skipped)
            if "sensitive_data" in active:
                sensitive = run("Sensitive Data", lambda: check_sensitive_data(dataframe, table_id=target_id, existing_mapping=existing_mapping, spark_session=spark_session, verbose=False, context=context))
            prepared = sensitive["dataframe"]
            evaluated_drift = run("Source Drift", lambda: [check_source_drift(source_id, target_table_id=target_id, spark_session=spark_session, verbose=False, context=context) for source_id in drift_ids]) if drift_ids else []
            drift_by_source = dict(zip(drift_ids, evaluated_drift, strict=True))
            drift = [drift_by_source.get(source_id, dict(skipped)) for source_id in source_ids]
            grain_result = run("Grain", lambda: check_grain(prepared, table_id=target_id, scope="write_prepared_input", spark_session=spark_session, verbose=False, context=context)) if "grain" in active else dict(skipped)
            dq_result = run("Data Quality", lambda: check_dq(prepared, table_id=target_id, spark_session=spark_session, verbose=False, context=context, diagnostics=dq_diagnostics)) if "data_quality" in active else dict(skipped)
            common_results = {
                "table_id": target_id,
                **execution_result(context, target_id, stages=stages),
                "schema_result": schema_result,
                "sensitive_result": sensitive,
                "source_drift_results": drift,
                "grain_result": grain_result,
                "dq_result": dq_result,
                "source_guardrail_results": source_checks,
                "source_association": "pipeline_participation",
                "orchestration_stages": stages,
            }
            if not execution_plan.permits_persistence:
                def evaluate_processing():
                    try:
                        return pipeline_write(
                            prepared, store=store, schema=schema, table_name=table_name,
                            load_strategy=write_mode, load_strategy_parameters=write_parameters,
                            source_table_ids=source_ids, repartition_by=repartition_by, spark_session=spark_session, verbose=False, context=context,
                        )
                    except ValueError as exc:
                        return {"table_id": target_id, "strategy": write_mode, "published": False,
                                "status": "blocked", "can_continue": False,
                                "write_metrics": {"rows_committed": 0, "measurement_source": "dry_run"},
                                "dry_run": {"status": "blocked", "reason": str(exc), "fully_evaluated": [],
                                            "simulated": [], "not_verified": ["target preparation and publication"]}}
                dry_run = run("Processing", evaluate_processing)
                profile = profile_table(verbose=False, dataframe=prepared, frequency_enabled=frequency_enabled,
                                        frequency_top_n=frequency_top_n, context=context, spark_session=spark_session)
                passed = all(item["can_continue"] for item in source_checks) and all(stage["status"] != "blocked" for stage in [
                    *stages, *(stage for source in sources for stage in source.get("orchestration_stages", []))
                ])
                duration = summary.finish([("Mode", "Testing"), ("Target", target),
                                           ("Checks passed", passed), ("Published", "No"), ("Persistence", "Disabled")])
                operation.complete(stages)
                return {**common_results, **dry_run, "dataframe": prepared, "published": False,
                        "publication_status": "not_published", "profile_result": profile,
                        "validation_passed": passed, "testing_completed_at": datetime.now(UTC).isoformat(),
                        "tested_contracts": tested_contract_identities(context, [target_id, *source_ids]),
                        "total_duration_seconds": duration}
            write_result = run("Write", lambda: pipeline_write(prepared, store=store, schema=schema, table_name=table_name, load_strategy=write_mode, load_strategy_parameters=write_parameters, source_table_ids=source_ids, repartition_by=repartition_by, spark_session=spark_session, verbose=False, context=context))
            published = write_result.get("published", True)
            publication_status = write_result.get("publication_status", "published")
            metrics = dict(write_result.get("write_metrics") or {})
            for key in ("input_rows", "rows_committed", "total_target_rows", "rows_inserted", "rows_updated", "rows_unchanged", "versions_inserted", "versions_expired", "measurement_source"):
                metrics.setdefault(key, None)
            strategy = write_result.get("strategy", write_mode)
            columns = getattr(prepared, "columns", None)
            metrics.setdefault("input_columns", len(columns) if columns is not None else None)
            summary.details([("Strategy", strategy.title()), ("Target", target), ("Rows committed", metrics["rows_committed"]), ("Columns", metrics["input_columns"])])
            try:
                profile = run("Profile", lambda: profile_table(verbose=False, table_id=write_result["table_id"], grain_discovery_enabled=grain_discovery_enabled, grain_discovery_max_columns=grain_discovery_max_columns, grain_discovery_max_candidates=grain_discovery_max_candidates, frequency_enabled=frequency_enabled, frequency_top_n=frequency_top_n, context=context, spark_session=spark_session))
            except RuntimeError as exc:
                exc.published = published
                exc.table_id = write_result["table_id"]
                exc.write_metrics = dict(metrics)
                exc.failed_stage = "Profile"
                message = ("Target publication and checkpoint finalization already succeeded; Profile failed afterwards."
                           if published else "The empty incremental scope was not published; Profile failed afterwards.")
                exc.args = (f"{exc} {message}",)
                if verbose:
                    print(message)
                raise
            metrics["total_target_rows"] = profile.get("row_count")
            fields = [("Target", target), ("Strategy", strategy.title()), ("Published", "Yes" if published else "No"), ("Publication", publication_status.replace("_", " ")), ("Rows committed", metrics["rows_committed"])]
            if strategy == "scd1":
                fields.extend((label, metrics[key]) for label, key in (("Rows inserted", "rows_inserted"), ("Rows updated", "rows_updated"), ("Rows unchanged", "rows_unchanged")))
            elif strategy == "scd2":
                fields.extend((label, metrics[key]) for label, key in (("Versions inserted", "versions_inserted"), ("Versions expired", "versions_expired"), ("Rows unchanged", "rows_unchanged")))
            duration = summary.finish(fields)
            operation.complete(stages)
            return {**common_results, **write_result, "write_metrics": metrics, "total_duration_seconds": duration, "dataframe": prepared, "published": published, "publication_status": publication_status, "profile_result": profile}
        except Exception:
            mapping = sensitive.get("support_mapping")
            if mapping is not None:
                mapping.unpersist()
            raise
