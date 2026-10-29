"""Public owner for the standard governed source lifecycle."""
from __future__ import annotations
from typing import Any
from fabricops_kit.pipeline.check_dq import check_dq
from fabricops_kit.pipeline.check_grain import check_grain
from fabricops_kit.pipeline.check_freshness import check_freshness
from fabricops_kit.pipeline.check_schema import check_schema
from fabricops_kit.pipeline.pipeline_read import pipeline_read
from fabricops_kit.pipeline.shared import (
    ExecutionSummary,
    current_pipeline_session,
    schedule_table_profiling,
    PipelineOperation,
    execution_result,
    _run_orchestration_stage,
    prepare_pipeline_execution,
    pipeline_guardrail_types,
    print_pipeline_contract,
    PIPELINE_MODE_NAMES,
)
from fabricops_kit.pipeline.resolve_table_id import resolve_table_id


def orchestrate_read(*, store: str, schema: str | None, table_name: str, read_mode: str = "full", query: str | None = None, read_parameters: dict[str, Any] | None = None, target_table_id: str | None = None, verbose: bool = False, dq_diagnostics: str = "sample") -> dict[str, Any]:
    """Read a source using the active pipeline's contracts and runtime.

    Define store, schema, table_name and any full/incremental/query options.
    Spark, execution authority and reporting come from setup_pipeline. The result
    retains its dataframe, canonical Table ID and Guardrail diagnostics. Reads
    register pipeline-level participation for subsequent Writes; this is not
    exact DataFrame lineage. Governed blocks failed contract checks; Dry Run never commits.
    target_table_id preserves incremental checkpoint and SCD processing support.
    dq_diagnostics accepts sample, none or full for explicit debugging.

    Profiling uses the complete source with frozen contract policies and shared
    persisted completion history. Dry Run reuses an unfiltered full Read DataFrame; query
    and incremental Reads still profile the complete physical source. Successful
    Dry Run retains calculated observations only in the session without consuming
    persisted schedules. Guardrail
    checks run regardless of profiling eligibility.

    Parameters
    ----------
    store : str
        Configured source store key.
    schema : str or None
        Explicit physical schema; pass None for a schemaless store.
    table_name : str
        Physical source table name.
    read_mode : {"full", "incremental"}
        Full reads profile the source; incremental reads retain checkpoint bounds.
    read_parameters : dict, optional
        Incremental watermark_column; must agree with the selected contract.
    target_table_id : str, optional
        Required target for incremental reads, also a participant in the plan.
    query : str, optional
        Read-only Warehouse query, supported for full reads only.
    verbose : bool
        Print concise stage outcomes and summary.
    dq_diagnostics : {"sample", "none", "full"}
        Rule metrics plus bounded examples, no examples, or lazy full failures.

    Returns
    -------
    dict
        Governed source dataframe, execution identity, Guardrail outcomes, read_metrics, profile_result and orchestration_stages.

    Raises RuntimeError when no pipeline is active or a persistent stage fails, and
    ValueError for an invalid operation or inconsistent approved configuration.

    Examples
    --------
    >>> orders = orchestrate_read(store="Bronze", schema="demo", table_name="orders")

    """
    session = current_pipeline_session()
    spark_session = session.spark
    try:
        execution_plan = session.operation_plan("source", locals())
    except BaseException:
        session.close(failed=True)
        raise
    arguments = {key: value for key, value in locals().items() if key not in {"session"}}
    with PipelineOperation(execution_plan, "source", arguments) as operation:
        read_mode = str(read_mode or "").strip().lower()
        if read_mode not in {"full", "incremental"}:
            raise ValueError("read_mode must be 'full' or 'incremental'.")
        if dq_diagnostics not in {"none", "sample", "full"}:
            raise ValueError("dq_diagnostics must be 'none', 'sample', or 'full'.")
        summary = ExecutionSummary("READ", verbose=verbose)
        table_id = resolve_table_id(store=store, schema=schema, table_name=table_name, context=execution_plan.runtime_context)
        context = prepare_pipeline_execution([table_id], execution_plan=execution_plan, spark_session=spark_session)
        context = {**context, "_fabricops_suppress_io_log": True}
        if "source" not in context["_pipeline_identities"][table_id]["roles"]:
            raise ValueError("Read requires an explicit source participant.")
        if target_table_id is not None and (
            target_table_id not in context["_pipeline_identities"]
            or "target" not in context["_pipeline_identities"][target_table_id]["roles"]
        ):
            raise ValueError("Incremental target must be an explicit target participant in the plan.")
        active = pipeline_guardrail_types(context, table_id)
        labels = [("freshness", "Freshness"), ("schema", "Schema"), ("grain", "Grain"), ("data_quality", "Data Quality")]
        # A new Read supersedes earlier evidence even if evaluation cannot complete.
        read_types = {kind for kind, _label in labels}
        execution_plan.results[:] = [row for row in execution_plan.results
                                    if row.get("table_id") != table_id or row.get("guardrail_type") not in read_types]
        names = ["Read", *[label for kind, label in labels if kind in active]]
        names.append("Profile")
        stages = []
        if verbose:
            print(f"FabricOps READ · {table_name} · {PIPELINE_MODE_NAMES[execution_plan.execution_mode]}")
        print_pipeline_contract(context, table_id, operation="Read", guardrails=[label for kind, label in labels if kind in active], verbose=verbose)
        def run(stage, function):
            result, record = _run_orchestration_stage(operation="READ", name=table_name, index=names.index(stage)+1, total=len(names), stage=stage, function=function, verbose=verbose, allow_blocked=not execution_plan.permits_persistence)
            stages.append(record)
            return result
        source = run("Read", lambda: pipeline_read(store=store, schema=schema, table_name=table_name, read_mode=read_mode, query=query, read_parameters=read_parameters, target_table_id=target_table_id, verbose=False, context={**(context or {}), "_spark_session": spark_session}))
        reader_name = source.pop("_reader_name", None)
        metrics = dict(source.get("read_metrics") or {})
        metrics.setdefault("rows_read", None)
        columns = getattr(source["dataframe"], "columns", None)
        metrics.setdefault("columns", len(columns) if columns is not None else None)
        summary.details([("Physical reader", reader_name), ("Rows read", metrics["rows_read"]), ("Columns", metrics["columns"])])
        for recovered in source.get("source_observation_recovery", []):
            summary.details([("Source Observation", recovered["status"].replace("_", " ")), ("Exact batches verified", recovered["batches"])])
        if source.get("has_data") is False:
            summary.details([("Scope", "Empty incremental scope")])
        dataframe, table_id = source["dataframe"], source["table_id"]
        skipped = {"status": "skipped", "can_continue": True, "checks": []}
        freshness = run("Freshness", lambda: check_freshness(table_id, verbose=False, context={**(context or {}), "_spark_session": spark_session})) if "freshness" in active else dict(skipped)
        schema_result = run("Schema", lambda: check_schema(dataframe, table_id=table_id, verbose=False, context={**(context or {}), "_spark_session": spark_session})) if "schema" in active else dict(skipped)
        grain_result = run("Grain", lambda: check_grain(dataframe, table_id=table_id, scope="read_full" if read_mode == "full" else "read_incremental_batch", verbose=False, context={**(context or {}), "_spark_session": spark_session})) if "grain" in active else dict(skipped)
        dq_result = run("Data Quality", lambda: check_dq(dataframe, table_id=table_id, verbose=False, context={**(context or {}), "_spark_session": spark_session}, diagnostics=dq_diagnostics)) if "data_quality" in active else dict(skipped)
        profile = run("Profile", lambda: schedule_table_profiling(table_id, "read", context=context, spark_session=spark_session,
            **({"dataframe": dataframe} if not execution_plan.permits_persistence and read_mode == "full" and query is None and not source.get("is_query") else {})))

        if metrics["rows_read"] is None and read_mode == "full" and not source.get("is_query"):
            metrics["rows_read"] = profile.get("row_count")
        duration = summary.finish([
            ("Source", ".".join(str(part) for part in (store, schema, table_name) if part)),
            ("Rows read", metrics["rows_read"]), ("Columns", metrics["columns"]),
        ])
        operation.complete(stages)
        return session.register_source({**source, **execution_result(context, table_id, stages=stages), "published": False, "read_metrics": metrics, "total_duration_seconds": duration, "freshness_result": freshness, "schema_result": schema_result, "grain_result": grain_result, "dq_result": dq_result, "profile_result": profile, "orchestration_stages": stages})
