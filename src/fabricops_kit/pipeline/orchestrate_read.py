"""Public owner for the standard governed source lifecycle."""
from __future__ import annotations
from typing import Any
from fabricops_kit.pipeline.check_dq import check_dq
from fabricops_kit.pipeline.check_grain import check_grain
from fabricops_kit.pipeline.check_freshness import check_freshness
from fabricops_kit.pipeline.check_schema import check_schema
from fabricops_kit.pipeline.pipeline_read import pipeline_read
from fabricops_kit.pipeline.profile_table import profile_table
from fabricops_kit.pipeline.shared import (
    ExecutionSummary,
    PipelineOperation,
    execution_result,
    _run_orchestration_stage,
    prepare_pipeline_execution,
    pipeline_guardrail_types,
    print_pipeline_contract,
)
from fabricops_kit.pipeline.resolve_table_id import resolve_table_id


def orchestrate_read(*, execution_plan, store: str, schema: str | None, table_name: str, read_mode: str = "full", query: str | None = None, read_parameters: dict[str, Any] | None = None, target_table_id: str | None = None, grain_discovery_enabled: bool = True, grain_discovery_max_columns: int = 3, grain_discovery_max_candidates: int = 8, frequency_enabled: bool = True, frequency_top_n: int | None = 5, spark_session=None, verbose: bool = True, dq_diagnostics: str = "sample") -> dict[str, Any]:
    """Read real source data under an explicit shared pipeline execution plan.

    Parameters
    ----------
    execution_plan : PipelineExecutionPlan
        Required immutable plan from setup_pipeline in interactive or headless mode.
        Pass the same object to every Read and Write and execute the entire project
        then call finalize_pipeline(plan) for whole-run completion. Testing evaluates
        Freshness, Schema, Grain, Data Quality and Profile. With testing_writes=False,
        ordinary Catalogue/Profile/Source Observation commits are disabled; run
        records and Guardrail diagnostics still persist. Explicit real Testing
        writes permit normal metadata side effects to safe destinations. Live
        enforces one pinned approved revision. Environment names select routing.
        Empty or disabled optional Guardrails add no execution requirement.
        A configured check that cannot execute blocks Live and remains a Testing diagnostic.
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
    grain_discovery_enabled : bool
        Discover candidate Grain keys during full-read profiling; contract Grain checks always run.
    frequency_enabled : bool
        Calculate optional frequency distributions during profiling.
    grain_discovery_max_columns : int
        Positive maximum width of a candidate key.
    grain_discovery_max_candidates : int
        Positive maximum retained candidates at the smallest valid key width.
    frequency_top_n : int, optional
        Maximum frequency values per column.
    spark_session : object, optional
        Spark session shared by all stages.
    verbose : bool
        Print concise stage outcomes and summary.
    dq_diagnostics : {"sample", "none", "full"}
        Rule metrics plus bounded examples, no examples, or lazy full failures.

    Returns
    -------
    dict
        Source dataframe and identity, selected contract, execution_mode,
        applicable_guardrails, diagnostic results, profile, persistence_status,
        publication_status and checks_not_exercised. Testing retains blocking
        rule outcomes for inspection; Live stops on Block. Neither publishes data.

    Raises
    ------
    ValueError
        For an invalid or inconsistent plan, mode, parameters or participant.
    RuntimeError
        For a failed stage, retaining the original exception as its cause.

    Examples
    --------
    >>> source = orchestrate_read(execution_plan=plan, store="Bronze", schema="demo", table_name="orders")

    """
    with PipelineOperation(execution_plan, "source", locals()) as operation:
        read_mode = str(read_mode or "").strip().lower()
        if read_mode not in {"full", "incremental"}:
            raise ValueError("read_mode must be 'full' or 'incremental'.")
        for name, value in (
            ("grain_discovery_max_columns", grain_discovery_max_columns),
            ("grain_discovery_max_candidates", grain_discovery_max_candidates),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer.")
        if dq_diagnostics not in {"none", "sample", "full"}:
            raise ValueError("dq_diagnostics must be 'none', 'sample', or 'full'.")
        summary = ExecutionSummary("READ", verbose=verbose)
        table_id = resolve_table_id(store=store, schema=schema, table_name=table_name, context=execution_plan.runtime_context)
        context = prepare_pipeline_execution([table_id], execution_plan=execution_plan, spark_session=spark_session)
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
        if read_mode == "full":
            names.append("Profile")
        stages = []
        if verbose:
            print(f"FabricOps READ · {table_name} · {execution_plan.execution_mode.title()}")
        print_pipeline_contract(context, table_id, operation="Read", guardrails=[label for kind, label in labels if kind in active], verbose=verbose)
        def run(stage, function):
            result, record = _run_orchestration_stage(operation="READ", name=table_name, index=names.index(stage)+1, total=len(names), stage=stage, function=function, verbose=verbose, allow_blocked=not execution_plan.permits_persistence)
            stages.append(record)
            return result
        source = run("Read", lambda: pipeline_read(store=store, schema=schema, table_name=table_name, read_mode=read_mode, query=query, read_parameters=read_parameters, target_table_id=target_table_id, spark_session=spark_session, verbose=False, context=context))
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
        freshness = run("Freshness", lambda: check_freshness(table_id, spark_session=spark_session, verbose=False, context=context)) if "freshness" in active else dict(skipped)
        schema_result = run("Schema", lambda: check_schema(dataframe, table_id=table_id, spark_session=spark_session, verbose=False, context=context)) if "schema" in active else dict(skipped)
        grain_result = run("Grain", lambda: check_grain(dataframe, table_id=table_id, scope="read_full" if read_mode == "full" else "read_incremental_batch", spark_session=spark_session, verbose=False, context=context)) if "grain" in active else dict(skipped)
        dq_result = run("Data Quality", lambda: check_dq(dataframe, table_id=table_id, spark_session=spark_session, verbose=False, context=context, diagnostics=dq_diagnostics)) if "data_quality" in active else dict(skipped)
        profile_identity = {} if source.get("is_query") else {"store": store, "schema": schema, "table_name": table_name}
        profile = run("Profile", lambda: profile_table(dataframe=dataframe, **profile_identity, grain_discovery_enabled=grain_discovery_enabled, grain_discovery_max_columns=grain_discovery_max_columns, grain_discovery_max_candidates=grain_discovery_max_candidates, frequency_enabled=frequency_enabled, frequency_top_n=frequency_top_n, context=context, spark_session=spark_session)) if read_mode == "full" else dict(skipped, reason="Incremental batch")

        if metrics["rows_read"] is None and read_mode == "full":
            metrics["rows_read"] = profile.get("row_count")
        duration = summary.finish([
            ("Source", ".".join(str(part) for part in (store, schema, table_name) if part)),
            ("Rows read", metrics["rows_read"]), ("Columns", metrics["columns"]),
        ])
        operation.complete(stages)
        return {**source, **execution_result(context, table_id, stages=stages), "published": False, "read_metrics": metrics, "total_duration_seconds": duration, "freshness_result": freshness, "schema_result": schema_result, "grain_result": grain_result, "dq_result": dq_result, "profile_result": profile, "orchestration_stages": stages}
