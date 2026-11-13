"""Public owner for the standard governed target lifecycle."""
from __future__ import annotations
from typing import Any, Iterable
from datetime import UTC, datetime
from fabricops_kit.pipeline.check_dq import check_dq
from fabricops_kit.pipeline.check_schema import check_schema
from fabricops_kit.pipeline.check_sensitive_data import check_sensitive_data
from fabricops_kit.pipeline.pipeline_write import pipeline_write
from fabricops_kit.pipeline.resolve_table_id import resolve_table_id
from fabricops_kit.pipeline.shared import (
    ExecutionSummary,
    participant_id,
    display_profile_presentations,
    current_pipeline_session,
    schedule_table_profiling,
    evaluate_pipeline_source_drift,
    skip_table_profiling,
    PipelineOperation,
    execution_result,
    tested_contract_identities,
    source_guardrail_results,
    _run_orchestration_stage,
    prepare_pipeline_execution,
    pipeline_guardrail_types,
    print_pipeline_contract,
    PIPELINE_MODE_NAMES,
)


def orchestrate_write(dataframe: Any, *, store: str, schema: str | None = None, table_name: str | None = None, write_mode: str, write_parameters: dict[str, Any] | None = None, repartition_by: int | None = None, existing_mapping=None, verbose: bool = False, dq_diagnostics: str = "sample", relative_path: str | None = None, file_format: str | None = None, write_options: dict[str, Any] | None = None, single_file: bool = False, max_single_file_rows: int = 1000000, max_single_file_bytes: int = 134217728) -> dict[str, Any]:
    """Evaluate or publish a target using the active pipeline's runtime.

    Define the dataframe, destination, write_mode and processing parameters.
    Select either store/schema/table_name for tables or store/relative_path/file_format
    for Lakehouse Files. File modes are errorifexists, overwrite, append and ignore;
    table-only append_all, Append New Only and SCD strategies are rejected for files.
    Files support Dry Run and Ungoverned; Governed file targets fail closed because
    current Pipeline Promotion authorizes only file Reads. No file Table ID or
    table Data Contract is manufactured. Protected file destinations and overlapping
    folders remain blocked in Ungoverned mode. Incremental checkpoint publication
    is table-only; file writes require Full Read sources.

    File profiling uses the supplied DataFrame and setup_pipeline settings, remains
    session-local, and persists no table profile snapshots. File overwrite profiles
    its supplied input before publication so lazy reads of the target remain valid.
    A bounded profile cannot
    establish complete row counts. Ignored output is never reported as published.
    File options, physical location, publication status and available filesystem
    metrics are retained in METADATA_PIPELINE_RUN operations. File targets do not
    receive table audit columns, row hashes, SCD processing or table lineage.
    A successful file Write leaves the pipeline open for finalize_pipeline().
    All reads registered in this execution are associated with this target as
    pipeline participants, not proven transformation dependencies. File participation
    is returned under source_ids and retained separately from source_table_ids in
    Run operations; it never manufactures table lineage. Dry Run evaluates
    processing and applicable Guardrails without publishing or committing metadata.
    Ungoverned writes without contract checks but cannot target an already governed
    table. Governed requires activated contracts, ownership and a pinned revision.
    Advanced repartitioning, Sensitive Data mapping and DQ diagnostics remain
    available. The result includes publication metrics and Guardrail diagnostics.
    A successful Write does not imply successful completion of the notebook.

    Dry Run profiles the prepared DataFrame in memory without publishing the target.
    Persistent table writes profile the physical target after successful publication,
    bounded only by setup_pipeline(profiling_max_rows=...).
    Pipeline-owned settings apply independently of selected Contracts; Dry Run observations
    do not consume persisted schedules. Guardrail checks run regardless
    of profiling eligibility.

    When statistical profiling completes, the operation summary is followed by a
    readable profile table even with ``verbose=False``. Native Fabric display has
    a text fallback; the preview shows at most 100 columns and 120 characters per
    text cell. Complete-table, bounded-selection and Dry Run scopes are labelled.
    Skipped or not-due profiling shows no historical results. Presentation reuses
    current aggregates and cannot fail a successful operation. ``verbose=True``
    adds operational diagnostics. Returned profiling structures are unchanged.

    Parameters
    ----------
    dataframe : object
        Transformed Spark DataFrame; Sensitive Data treatment prepares the input.
    store : str
        Configured target store key.
    schema : str or None
        Explicit physical table schema; pass None for a schemaless store or omit for files.
    table_name : str
        Physical target table name; omit for file destinations.
    write_mode : str
        Table strategies: overwrite, append_all, append_new_only, scd1, scd2,
        captured exactly by Pipeline Activation. File modes: errorifexists,
        overwrite, append, ignore.
    relative_path : str, optional
        Exact destination beneath the configured Lakehouse Files area.
    file_format : {"csv", "parquet", "json"}, optional
        Required with relative_path. JSON is newline-delimited.
    write_options : dict, optional
        Spark file writer options. Cannot override destination, mode or layout.
    single_file : bool, default=False
        Opt into one named artifact; default output is a Spark dataset folder.
    max_single_file_rows : int, default=1000000
        Bounded count safeguard before single-file staging.
    max_single_file_bytes : int, default=134217728
        Encoded-byte safeguard before single-file publication. Coalescing uses
        one executor; these caps do not bound its working memory. Single CSV/JSON
        is uncompressed. See write_lakehouse_file for filesystem limitations.
    write_parameters : dict, optional
        Strategy parameters including SCD key_columns and SCD2 effective_column.
    existing_mapping : object, optional
        Caller-managed Sensitive Data mapping; incompatible with a configured vault.
        Existing assignments are reused. The returned sensitive_result.support_mapping
        remains caller-owned; persist it only in persistent workflows, then unpersist() its
        cache after consumption. A configured restricted mapping store is read-only
        during Dry Run and reused/updated during persistent writes. Failures release the cache.
    repartition_by : int, optional
        Physical write partition count for persistent modes.
    verbose : bool
        Print concise stages and outcome when True; the execution widget reports automatically by default.
    dq_diagnostics : {"sample", "none", "full"}
        Exact metrics with bounded samples, no samples or lazy full violations.

    Returns
    -------
    dict
        Final prepared Write input under ``dataframe``, selected contract, execution identity, validation results,
        write metrics, publication state and profiling outcome. Per-source
        Source Drift results remain under ``source_drift_results``; the independent
        pipeline decision is under ``source_drift_decision``. Dry Run returns
        processing diagnostics without publication; persistent modes return the
        actual publication outcome. The DataFrame includes Sensitive Data treatment,
        row hash and target audit columns, plus SCD2 lifecycle columns where applicable.
        Append New Only returns only rows submitted for insertion. SCD previews
        represent processing input, not the reconstructed post-merge destination.
        Persistent modes return an eagerly materialized, caller-owned snapshot of
        the exact physical writer input. It remains inspectable after publication;
        call ``result["dataframe"].unpersist()`` when inspection is complete.
        File results instead return the supplied DataFrame without caching or
        table preparation, a source_id, resolved_path and filesystem write_metrics.
        ``rows_committed`` measures this attempt; ``total_target_rows`` is the
        destination total where profiling provides it.

    Raises RuntimeError when no pipeline is active or a persistent stage fails, and
    ValueError for an invalid operation or inconsistent approved configuration.

    Examples
    --------
    >>> result = orchestrate_write(dataframe=final_df, store="Silver",
    ...     relative_path="Exports/orders.parquet", file_format="parquet", write_mode="overwrite")
    >>> result = orchestrate_write(summary_df, store="Gold", schema="demo",
    ...     table_name="customer_summary", write_mode="overwrite")

    """
    session = current_pipeline_session()
    spark_session = session.spark
    try:
        is_file = relative_path is not None or file_format is not None or write_options is not None or single_file
        if is_file:
            from fabricops_kit.io.shared import validate_file_write, repartition_dataframe_for_write
            if table_name is not None or schema is not None or write_parameters is not None or existing_mapping is not None:
                raise ValueError("Select table destination/processing arguments or file arguments, not both.")
            if relative_path is None or file_format is None:
                raise ValueError("File writes require relative_path and file_format.")
            if session.plan.execution_mode == "governed":
                raise ValueError("Governed file targets require explicit destination authorization; file-target Pipeline Promotion is not supported.")
            write_mode, write_options = validate_file_write(relative_path, file_format, write_mode, write_options,
                single_file=single_file, repartition_by=repartition_by,
                max_single_file_rows=max_single_file_rows, max_single_file_bytes=max_single_file_bytes)
            if repartition_by is not None and (type(repartition_by) is not int or repartition_by < 1):
                raise ValueError("Orchestrated repartition_by must be a positive integer.")
            repartition_dataframe_for_write(dataframe, repartition_by)
        elif not table_name:
            raise ValueError("table_name or a complete file destination is required.")
        execution_plan = session.operation_plan("target", locals())
    except BaseException:
        session.close(failed=True)
        raise
    sources = tuple(session.sources)
    arguments = {key: value for key, value in locals().items() if key not in {"session"}}
    with PipelineOperation(execution_plan, "target", arguments) as operation:
        sources = operation.arguments["sources"]
        if dq_diagnostics not in {"none", "sample", "full"}:
            raise ValueError("dq_diagnostics must be 'none', 'sample', or 'full'.")
        if is_file:
            return _write_file(dataframe, operation=operation, execution_plan=execution_plan, sources=sources,
                store=store, relative_path=relative_path, file_format=file_format, write_mode=write_mode,
                write_options=write_options, repartition_by=repartition_by, single_file=single_file,
                max_single_file_rows=max_single_file_rows, max_single_file_bytes=max_single_file_bytes,
                verbose=verbose, spark_session=spark_session)
        summary = ExecutionSummary("WRITE", verbose=verbose)
        presentations = []
        target = ".".join(str(part) for part in (store, schema, table_name) if part)
        sources = list(sources)
        if any(source.get("execution_plan_id") != execution_plan.plan_id for source in sources):
            raise ValueError("Every source must be a Read result from the same execution plan.")
        participant_ids = [participant_id(source) for source in sources]
        source_ids = [source["table_id"] for source in sources if source.get("table_id")]
        file_source_ids = [source["source_id"] for source in sources if source.get("source_type") == "file"]
        target_id = resolve_table_id(store=store, schema=schema, table_name=table_name, context=execution_plan.runtime_context)
        context = prepare_pipeline_execution([target_id, *participant_ids], execution_plan=execution_plan, spark_session=spark_session)
        context = {**context, "_fabricops_suppress_io_log": True}
        if any("source" not in context["_pipeline_identities"][source_id]["roles"] for source_id in participant_ids):
            raise ValueError("Every contributing source must have an explicit source role in the plan.")
        if "target" not in context["_pipeline_identities"][target_id]["roles"]:
            raise ValueError("Write requires an explicit target participant.")
        active = pipeline_guardrail_types(context, target_id)
        drift_decision = evaluate_pipeline_source_drift(execution_plan, verbose=verbose, spark_session=spark_session)
        drift_by_source = {row["table_id"]: row for row in drift_decision.get("sources", [])}
        source_checks = source_guardrail_results(context, sources)
        names = []
        if "sensitive_data" in active:
            names.append("Sensitive Data")
        if "schema" in active:
            names.append("Schema")
        if "data_quality" in active:
            names.append("Data Quality")
        if not execution_plan.permits_persistence:
            names.extend(["Processing", "Profile"])
        else:
            names.extend(["Write", "Profile"])
        stages = []
        if verbose:
            print(f"FabricOps WRITE · {table_name} · {PIPELINE_MODE_NAMES[execution_plan.execution_mode]}")
        print_pipeline_contract(context, target_id, operation="Write", guardrails=[name for name in names if name not in {"Write", "Profile", "Processing"}], verbose=verbose)
        def run(stage, function):
            result, record = _run_orchestration_stage(operation="WRITE", name=table_name, index=names.index(stage)+1, total=len(names), stage=stage, function=function, verbose=verbose, allow_blocked=not execution_plan.permits_persistence)
            stages.append(record)
            return result
        skipped = {"status": "skipped", "can_continue": True, "checks": []}
        sensitive = {**skipped, "dataframe": dataframe, "support_mapping": None}
        try:
            if "sensitive_data" in active:
                sensitive = run("Sensitive Data", lambda: check_sensitive_data(dataframe, table_id=target_id, existing_mapping=existing_mapping, verbose=False, context={**(context or {}), "_spark_session": spark_session}))
            prepared = sensitive["dataframe"]
            schema_result = run("Schema", lambda: check_schema(prepared, table_id=target_id, verbose=False, context={**(context or {}), "_spark_session": spark_session})) if "schema" in active else dict(skipped)
            dq_result = run("Data Quality", lambda: check_dq(prepared, table_id=target_id, verbose=False, context={**(context or {}), "_spark_session": spark_session}, diagnostics=dq_diagnostics)) if "data_quality" in active else dict(skipped)
            common_results = {
                "table_id": target_id,
                **execution_result(context, target_id, stages=stages),
                "schema_result": schema_result,
                "sensitive_result": sensitive,
                "source_drift_results": [drift_by_source.get(source_id, dict(skipped)) for source_id in source_ids],
                "source_drift_decision": drift_decision,
                "dq_result": dq_result,
                "source_guardrail_results": source_checks,
                "source_association": "pipeline_participation",
                "source_ids": file_source_ids,
                "orchestration_stages": stages,
            }
            if not execution_plan.permits_persistence:
                def evaluate_processing():
                    try:
                        return pipeline_write(
                            prepared, store=store, schema=schema, table_name=table_name,
                            load_strategy=write_mode, load_strategy_parameters=write_parameters,
                            source_table_ids=source_ids, repartition_by=repartition_by, verbose=False, context={**(context or {}), "_spark_session": spark_session},
                        )
                    except ValueError as exc:
                        return {"table_id": target_id, "strategy": write_mode, "published": False,
                                "status": "blocked", "can_continue": False,
                                "write_metrics": {"rows_committed": None, "measurement_source": "dry_run"},
                                "dry_run": {"status": "blocked", "reason": str(exc), "fully_evaluated": [],
                                            "simulated": [], "not_verified": ["target preparation and publication"]}}
                dry_run = run("Processing", evaluate_processing)
                profile = run("Profile", lambda: schedule_table_profiling(target_id, "write", verbose=verbose, presentations=presentations, dataframe=prepared, context=context, spark_session=spark_session))
                metrics = dict(dry_run.get("write_metrics") or {})
                for key in ("input_rows", "rows_committed", "total_target_rows", "rows_inserted", "rows_updated", "rows_unchanged", "versions_inserted", "versions_expired", "measurement_source"):
                    metrics.setdefault(key, None)
                if metrics["input_rows"] is None:
                    metrics["input_rows"] = profile.get("row_count")
                columns = getattr(prepared, "columns", None)
                metrics.setdefault("input_columns", len(columns) if columns is not None else None)
                operation.capture_metrics(metrics)
                passed = all(item["can_continue"] for item in source_checks) and all(stage["status"] != "blocked" for stage in [
                    *stages, *(stage for source in sources for stage in source.get("orchestration_stages", []))
                ])
                duration = summary.finish([("Mode", "Dry Run"), ("Target", target),
                                           ("Checks passed", passed), ("Published", "No"), ("Persistence", "Disabled")])
                display_profile_presentations(presentations)
                operation.complete(stages, metrics=metrics)
                return {**common_results, **dry_run, "dataframe": dry_run.get("dataframe", prepared), "published": False,
                        "publication_status": "not_published", "profile_result": profile,
                        "write_metrics": metrics,
                        "validation_passed": passed, "testing_completed_at": datetime.now(UTC).isoformat(),
                        "tested_contracts": tested_contract_identities(context, [target_id, *participant_ids]),
                        "total_duration_seconds": duration}
            write_result = run("Write", lambda: pipeline_write(prepared, store=store, schema=schema, table_name=table_name, load_strategy=write_mode, load_strategy_parameters=write_parameters, source_table_ids=source_ids, repartition_by=repartition_by, verbose=False, context={**(context or {}), "_spark_session": spark_session}))
            published = write_result.get("published", True)
            publication_status = write_result.get("publication_status", "published")
            metrics = dict(write_result.get("write_metrics") or {})
            for key in ("input_rows", "rows_committed", "total_target_rows", "rows_inserted", "rows_updated", "rows_unchanged", "versions_inserted", "versions_expired", "measurement_source"):
                metrics.setdefault(key, None)
            strategy = write_result.get("strategy", write_mode)
            columns = getattr(prepared, "columns", None)
            metrics.setdefault("input_columns", len(columns) if columns is not None else None)
            operation.capture_metrics(metrics)
            try:
                profile = (run("Profile", lambda: schedule_table_profiling(write_result["table_id"], "write", verbose=verbose, presentations=presentations, context=context, spark_session=spark_session))
                           if published else skip_table_profiling(target_id, "write", "No successful publication", context=context, spark_session=spark_session))
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
            if profile.get("row_count") is not None:
                metrics["total_target_rows"] = profile["row_count"]
            load_status = (
                "Already loaded"
                if publication_status in {"already_applied", "metadata_recovered"}
                else "Skipped — no new data"
                if publication_status in {"empty_incremental_scope", "no_unseen_hashes"}
                else "Loaded"
                if published
                else "Not loaded"
            )
            fields = [
                ("Target", target),
                ("Strategy", strategy.replace("_", " ").title()),
                ("Load status", load_status),
                ("Rows processed", metrics["input_rows"]),
            ]
            if strategy == "scd1":
                fields.extend((label, metrics[key]) for label, key in (("Rows inserted", "rows_inserted"), ("Rows updated", "rows_updated"), ("Rows unchanged", "rows_unchanged")))
            elif strategy == "scd2":
                fields.extend((label, metrics[key]) for label, key in (("Versions inserted", "versions_inserted"), ("Versions expired", "versions_expired"), ("Rows unchanged", "rows_unchanged")))
            elif strategy in {"append_all", "append_new_only"}:
                fields.extend((label, metrics[key]) for label, key in (("Rows inserted", "rows_inserted"), ("Rows committed", "rows_committed")))
            else:
                fields.append(("Rows committed", metrics["rows_committed"]))
            duration = summary.finish(fields)
            display_profile_presentations(presentations)
            operation.complete(
                stages,
                rows_written=metrics.get("rows_committed"),
                metrics=metrics,
            )
            return {**common_results, **write_result, "write_metrics": metrics, "total_duration_seconds": duration, "dataframe": write_result.get("dataframe", prepared), "published": published, "publication_status": publication_status, "profile_result": profile}
        except Exception:
            mapping = sensitive.get("support_mapping")
            if mapping is not None:
                mapping.unpersist()
            raise


def _write_file(dataframe, *, operation, execution_plan, sources, store, relative_path, file_format,
                write_mode, write_options, repartition_by, single_file, max_single_file_rows,
                max_single_file_bytes, verbose, spark_session):
    """Publish an admitted exact file destination under the existing run boundary."""
    from fabricops_kit.io import write_lakehouse_file
    from fabricops_kit.io.shared import resolve_configured_file_path
    from fabricops_kit.pipeline.shared import resolve_file_write_participant, schedule_file_profiling
    identity = resolve_file_write_participant(store=store, relative_path=relative_path,
        file_format=file_format, context=execution_plan.runtime_context)
    target_id = identity["source_id"]
    if any(source.get("execution_plan_id") != execution_plan.plan_id for source in sources):
        raise ValueError("Every source must be a Read result from the same execution plan.")
    context = prepare_pipeline_execution([target_id, *[participant_id(source) for source in sources]],
        execution_plan=execution_plan, spark_session=spark_session)
    context = {**context, "_fabricops_suppress_io_log": True}
    if context["_pipeline_contracts"].get(target_id) is not None:
        raise ValueError("File targets cannot use table or read-source contracts.")
    checks = source_guardrail_results(context, sources)
    drift = evaluate_pipeline_source_drift(execution_plan, verbose=verbose, spark_session=spark_session)
    if execution_plan.permits_persistence and (any(not row["can_continue"] for row in checks)
                                               or drift.get("can_continue") is False):
        raise ValueError("Source Guardrails block file publication.")
    if any(source.get("read_mode") == "incremental" for source in sources):
        raise ValueError("File targets do not support incremental checkpoint publication; use Full Read sources.")
    summary = ExecutionSummary("WRITE", verbose=verbose)
    presentations, stages = [], []
    def run(name, function):
        result, record = _run_orchestration_stage(operation="WRITE", name=relative_path,
            index=len(stages)+1, total=2, stage=name, function=function, verbose=verbose,
            allow_blocked=not execution_plan.permits_persistence)
        stages.append(record)
        return result
    _, _, path = resolve_configured_file_path(store, relative_path, context=context)
    profile = None
    if execution_plan.permits_persistence and write_mode == "overwrite":
        # The supplied input may lazily read files that publication replaces.
        try:
            profile = run("Profile", lambda: schedule_file_profiling(dataframe, source_id=target_id, context=context,
                presentations=presentations, operation="write"))
        except RuntimeError as exc:
            exc.published = False
            exc.failed_stage = "Profile"
            raise
    if execution_plan.permits_persistence:
        result = run("Write", lambda: write_lakehouse_file(dataframe, relative_path, store=store,
            file_format=file_format, mode=write_mode, write_options=write_options,
            repartition_by=repartition_by, single_file=single_file,
            max_single_file_rows=max_single_file_rows, max_single_file_bytes=max_single_file_bytes,
            verbose=False, context=context))
    else:
        result = run("Processing", lambda: {"published": False, "publication_status": "not_published",
            "resolved_path": path, "relative_path": relative_path, "write_metrics": {"rows_committed": None,
            "measurement_source": "dry_run"}, "dry_run": {"status": "passed",
            "not_verified": ["destination permissions, collisions, size limits and publication"]}})
    operation.record.update(output_path=result["resolved_path"], publication_status=result["publication_status"])
    metrics = {**result["write_metrics"], "input_columns": len(dataframe.columns)}
    operation.capture_metrics(metrics)
    if profile is None:
        try:
            profile = run("Profile", lambda: schedule_file_profiling(dataframe, source_id=target_id, context=context,
                presentations=presentations, operation="write"))
        except RuntimeError as exc:
            exc.published = result["published"]
            exc.write_metrics = dict(metrics)
            exc.failed_stage = "Profile"
            raise
    if profile.get("profiling_max_rows") is None:
        metrics["input_rows"] = profile.get("row_count")
    operation.complete(stages, metrics=metrics)
    duration = summary.finish([("Target", f"{store}/Files/{relative_path}"),
        ("Mode", PIPELINE_MODE_NAMES[execution_plan.execution_mode]), ("Published", result["published"])])
    display_profile_presentations(presentations)
    return {**execution_result(context, target_id, stages=stages), **result, "source_type": "file",
        "source_id": target_id, "dataframe": dataframe, "write_mode": write_mode,
        "file_format": file_format, "output_layout": "single_file" if single_file else "dataset_folder",
        "validation_passed": all(row["can_continue"] for row in checks) and drift.get("can_continue", True)
            and all(stage.get("status") != "blocked" for source in sources for stage in source.get("orchestration_stages", [])),
        "tested_contracts": tested_contract_identities(context, [participant_id(source) for source in sources]),
        **({"testing_completed_at": datetime.now(UTC).isoformat()} if not execution_plan.permits_persistence else {}),
        "source_drift_results": [row for row in drift.get("sources", []) if row.get("table_id") in
            {source.get("table_id") for source in sources if source.get("table_id")}],
        "source_table_ids": [source["table_id"] for source in sources if source.get("table_id")],
        "source_ids": [source["source_id"] for source in sources if source.get("source_type") == "file"],
        "source_association": "pipeline_participation", "source_guardrail_results": checks,
        "source_drift_decision": drift, "profile_result": profile, "write_metrics": metrics,
        "orchestration_stages": stages, "total_duration_seconds": duration}
