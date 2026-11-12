"""Public owner for the standard governed source lifecycle."""
from __future__ import annotations
from typing import Any
import json
from fabricops_kit.pipeline.check_dq import check_dq
from fabricops_kit.pipeline.check_freshness import check_freshness
from fabricops_kit.pipeline.check_schema import check_schema
from fabricops_kit.pipeline.pipeline_read import pipeline_read
from fabricops_kit.pipeline.shared import (
    ExecutionSummary,
    resolve_file_participant,
    read_file_participant,
    schedule_file_profiling,
    display_profile_presentations,
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


def orchestrate_read(*, store: str, schema: str | None = None, table_name: str | None = None, read_mode: str = "full", query: str | None = None, read_parameters: dict[str, Any] | None = None, target_store: str | None = None, target_schema: str | None = None, target_table_name: str | None = None, verbose: bool = False, dq_diagnostics: str = "sample", relative_path: str | None = None, file_format: str | None = None, read_options: dict[str, Any] | None = None) -> dict[str, Any]:
    """Read a source using the active pipeline's contracts and runtime.

    Define store, schema, table_name and any full/incremental/query options.
    Alternatively select a Lakehouse file, folder or wildcard using relative_path,
    file_format and read_options. Files support full reads only and retain their
    stable Source ID, with no Table ID. Foundational readers remain independent.
    File profiles are calculated in memory per execution (including persistent
    modes), using the pipeline row limit; no table profile snapshot is persisted.
    A replaced file can be read again in a new execution; no exactly-once or
    immutable-file guarantee is provided.
    Spark, execution authority and reporting come from setup_pipeline. The result
    retains its dataframe, canonical Table ID or file Source ID and Guardrail diagnostics. Reads
    register pipeline-level participation for subsequent Writes; this is not
    exact DataFrame lineage. Governed blocks failed contract checks; Dry Run never commits.
    FabricOps resolves source and target Table IDs through configured workspace routing.
    dq_diagnostics accepts sample, none or full for explicit debugging.

    Table profiling uses pipeline-owned settings and shared
    persisted completion history. Full table reads reuse the exact returned DataFrame;
    query and incremental Reads profile the physical source when due, bounded only
    by setup_pipeline(profiling_max_rows=...).
    A restricted query never replaces full-source observations or profile snapshots.
    Disabled or not-due activities cause no separate profiling scan; configured
    Source Observation, Freshness and Source Drift checks retain their physical scope. Successful
    Dry Run retains calculated observations only in the session without consuming
    persisted schedules. Guardrail
    checks run regardless of profiling eligibility.

    When statistical profiling completes, the operation summary is followed by a
    readable profile table even with ``verbose=False``. Native Fabric display has
    a text fallback; the preview shows at most 100 columns and 120 characters per
    text cell. Complete-table, bounded-selection and Dry Run scopes are labelled.
    Skipped or not-due profiling shows no historical results. Presentation reuses
    current aggregates and cannot fail a successful operation. ``verbose=True``
    adds operational diagnostics. Returned profiling structures are unchanged.

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
        Required for incremental reads; Engineering watermark_column captured by Pipeline Activation.
    target_store : str, optional
        Configured target store key; required for incremental reads.
    target_schema : str, optional
        Physical target schema; omit for a schemaless store or configured default.
    target_table_name : str, optional
        Physical target table name; required for incremental reads. The resolved
        target must be an authorized target participant in the active plan.
        Source and target stores may route to different workspaces.
    query : str, optional
        Read-only Spark SQL on a Lakehouse or T-SQL on a Warehouse, for full
        reads only. Lakehouse SQL binds the declared source through configured
        OneLake routing. Simple integer TOP projections can convert to LIMIT;
        complex T-SQL requires native Spark SQL and otherwise raises ValueError.
    relative_path : str, optional
        File, folder or wildcard selector beneath the configured Lakehouse Files root.
        Brace expansion is unsupported because alternatives can escape that root.
        Mutually exclusive with table_name, schema, query and target coordinates.
    file_format : {"csv", "json", "parquet", "excel"}, optional
        Required for file reads. Uses the corresponding foundational reader.
    read_options : dict, optional
        Format-specific reader keyword settings, retained exactly for approval.
        Options cannot override the source location or execution context.
    verbose : bool
        Print concise stage outcomes and summary.
    dq_diagnostics : {"sample", "none", "full"}
        Rule metrics plus bounded examples, no examples, or lazy full failures.

    Returns
    -------
    dict
        Governed source dataframe, execution identity, Guardrail outcomes, read_metrics, profile_result and orchestration_stages.
        ``read_metrics.rows_read`` and the notebook summary describe the exact
        returned scope. For incremental reads this is the target-specific batch,
        never the complete physical Source Observation count.

    Raises RuntimeError when no pipeline is active or a persistent stage fails, and
    ValueError for an invalid operation or inconsistent approved configuration.

    Examples
    --------
    >>> orders = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
    >>> changes = orchestrate_read(
    ...     store="Bronze", schema="demo", table_name="orders", read_mode="incremental",
    ...     target_store="Silver", target_schema="demo", target_table_name="orders_clean",
    ... )

    """
    session = current_pipeline_session()
    spark_session = session.spark
    try:
        read_mode = str(read_mode or "").strip().lower()
        is_file = relative_path is not None or file_format is not None or read_options is not None
        if is_file:
            if table_name is not None or schema is not None or query is not None or read_parameters is not None or any(
                    value is not None for value in (target_store, target_schema, target_table_name)):
                raise ValueError("Select table arguments or file arguments, not both; files do not support queries or incremental targets.")
            if relative_path is None or file_format is None:
                raise ValueError("File reads require relative_path and file_format.")
            file_identity = resolve_file_participant(store=store, relative_path=relative_path,
                file_format=file_format, read_options=read_options, context=session.plan.runtime_context)
            relative_path = file_identity["relative_path"]
            if read_mode != "full":
                raise ValueError("File reads support read_mode='full' only; incremental files are unsupported.")
        elif not isinstance(table_name, str) or not table_name.strip():
            raise ValueError("table_name or a complete file source is required.")
        if read_mode not in {"full", "incremental"}:
            raise ValueError("read_mode must be 'full' or 'incremental'.")
        has_target = any(value is not None for value in (target_store, target_schema, target_table_name))
        if read_mode == "incremental" or has_target:
            if (not isinstance(target_store, str) or not target_store.strip()
                    or not isinstance(target_table_name, str) or not target_table_name.strip()):
                raise ValueError("target_store and target_table_name are required for incremental reads or supplied target coordinates.")
        execution_plan = session.operation_plan("source", locals())
        target_table_id = resolve_table_id(
            store=target_store, schema=target_schema, table_name=target_table_name,
            context=execution_plan.runtime_context,
        ) if has_target else None
    except BaseException:
        session.close(failed=True)
        raise
    arguments = {key: value for key, value in locals().items() if key not in {"session"}}
    with PipelineOperation(execution_plan, "source", arguments) as operation:
        if dq_diagnostics not in {"none", "sample", "full"}:
            raise ValueError("dq_diagnostics must be 'none', 'sample', or 'full'.")
        summary = ExecutionSummary("READ", verbose=verbose)
        presentations = []
        source_name = relative_path if is_file else table_name
        table_id = file_identity["source_id"] if is_file else resolve_table_id(store=store, schema=schema, table_name=table_name, context=execution_plan.runtime_context)
        context = prepare_pipeline_execution([table_id], execution_plan=execution_plan, spark_session=spark_session)
        context = {**context, "_fabricops_suppress_io_log": True}
        if "source" not in context["_pipeline_identities"][table_id]["roles"]:
            raise ValueError("Read requires an explicit source participant.")
        if target_table_id is not None and "target" not in context["_pipeline_identities"].get(target_table_id, {}).get("roles", []):
            raise ValueError("Incremental target must be an explicit target participant in the plan.")
        active = pipeline_guardrail_types(context, table_id)
        labels = [("freshness", "Freshness"), ("schema", "Schema"), ("data_quality", "Data Quality")]
        # A new Read supersedes earlier evidence even if evaluation cannot complete.
        read_types = {kind for kind, _label in labels}
        execution_plan.results[:] = [row for row in execution_plan.results
                                    if (row.get("source_id") or row.get("table_id")) != table_id or row.get("guardrail_type") not in read_types]
        names = ["Read", *[label for kind, label in labels if kind in active]]
        names.append("Profile")
        stages = []
        if verbose:
            print(f"FabricOps READ · {source_name} · {PIPELINE_MODE_NAMES[execution_plan.execution_mode]}")
        print_pipeline_contract(context, table_id, operation="Read", guardrails=[label for kind, label in labels if kind in active], verbose=verbose)
        def run(stage, function):
            result, record = _run_orchestration_stage(operation="READ", name=source_name, index=names.index(stage)+1, total=len(names), stage=stage, function=function, verbose=verbose, allow_blocked=not execution_plan.permits_persistence)
            stages.append(record)
            return result
        source = run("Read", lambda: read_file_participant(file_identity, context=context, spark_session=spark_session)) if is_file else run("Read", lambda: pipeline_read(store=store, schema=schema, table_name=table_name, read_mode=read_mode, query=query, read_parameters=read_parameters, target_table_id=target_table_id, verbose=False, context={**(context or {}), "_spark_session": spark_session}))
        reader_name = source.pop("_reader_name", None)
        metrics = dict(source.get("read_metrics") or {})
        metrics.setdefault("rows_read", None)
        metrics.setdefault("measurement_source", None)
        columns = getattr(source["dataframe"], "columns", None)
        metrics.setdefault("columns", len(columns) if columns is not None else None)
        operation.capture_metrics(metrics)
        if is_file:
            # Persist schema only, not rows or sensitive values, for Governance authoring.
            # This is the schema returned by the successful Engineering reader.
            operation.record["observed_columns_json"] = json.dumps([
                {"column_name": field.name, "data_type": field.dataType.simpleString()}
                for field in source["dataframe"].schema.fields
            ], separators=(",", ":"))
        # Spark reads are lazy, so the orchestration display must not imply that
        # row materialization happened at the physical Read boundary.
        summary.details([("Physical reader", reader_name), ("Columns", metrics["columns"])])
        for recovered in source.get("source_observation_recovery", []):
            summary.details([("Source Observation", recovered["status"].replace("_", " ")), ("Exact batches verified", recovered["batches"])])
        full_observation = source.get("full_source_observation", {})
        if full_observation.get("status") not in {None, "skipped", "disabled", "not_due"}:
            summary.details([("Source Drift observation", full_observation["status"])])
        if source.get("has_data") is False:
            summary.details([("Scope", "Empty incremental scope")])
        dataframe = source["dataframe"]
        if not is_file:
            table_id = source["table_id"]
        skipped = {"status": "skipped", "can_continue": True, "checks": []}
        freshness = run("Freshness", lambda: check_freshness(table_id, dataframe=dataframe, read_mode=read_mode, verbose=False, context={**(context or {}), "_spark_session": spark_session})) if "freshness" in active else dict(skipped)
        schema_result = run("Schema", lambda: check_schema(dataframe, table_id=table_id, verbose=False, context={**(context or {}), "_spark_session": spark_session})) if "schema" in active else dict(skipped)
        dq_result = run("Data Quality", lambda: check_dq(dataframe, table_id=table_id, verbose=False, context={**(context or {}), "_spark_session": spark_session}, diagnostics=dq_diagnostics)) if "data_quality" in active else dict(skipped)
        profile = run("Profile", lambda: schedule_file_profiling(dataframe, source_id=table_id, context=context, presentations=presentations)) if is_file else run("Profile", lambda: schedule_table_profiling(table_id, "read", verbose=verbose, presentations=presentations, context=context, spark_session=spark_session,
            **({"dataframe": dataframe} if read_mode == "full" and query is None and not source.get("is_query") else {})))

        if metrics["rows_read"] is None and read_mode == "full" and not source.get("is_query") and not (is_file and profile.get("profiling_max_rows") is not None):
            metrics["rows_read"] = profile.get("row_count")
        duration = summary.finish([
            ("Source", ".".join(str(part) for part in (store, schema, source_name) if part)),
            ("Read mode", read_mode.title()),
            ("Rows read", metrics["rows_read"]),
            ("Columns", metrics["columns"]),
        ])
        display_profile_presentations(presentations)
        operation.complete(stages, rows_read=metrics.get("rows_read"), metrics=metrics)

        return session.register_source({**source, **execution_result(context, table_id, stages=stages), "published": False, "read_metrics": metrics, "total_duration_seconds": duration, "freshness_result": freshness, "schema_result": schema_result, "dq_result": dq_result, "profile_result": profile, "orchestration_stages": stages})
