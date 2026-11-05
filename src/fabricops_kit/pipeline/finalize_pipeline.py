"""Public completion boundary for a pipeline execution."""

from datetime import datetime, timezone

from fabricops_kit.pipeline.shared import (
    PipelineSession,
    current_pipeline_session,
    _ACTIVE_PIPELINE,
    finalize_pipeline_run,
)


def _elapsed_seconds(started_at, completed_at):
    """Return elapsed seconds for two stored timestamps without Spark actions."""
    if started_at is None or completed_at is None:
        return None
    try:
        def parse(value):
            if isinstance(value, datetime):
                return value
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))

        started = parse(started_at)
        completed = parse(completed_at)
        if started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        if completed.tzinfo is None:
            completed = completed.replace(tzinfo=timezone.utc)
        return max(0.0, (completed - started).total_seconds())
    except (TypeError, ValueError, OverflowError):
        return None


def _format_duration(seconds):
    """Format a duration from stored run timestamps for the notebook summary."""
    if seconds is None:
        return "Not captured"
    total = int(round(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def _operation_summary_rows(result, *, pipeline=None):
    """Project finalized operations plus same-run metrics into display-only rows."""
    rows = []
    identities = {}
    runtime_operations = {}
    if pipeline is not None:
        import json

        identities = json.loads(pipeline.plan.participants_json)
        runtime_operations = pipeline.plan.evidence.get("operations", {})

    for operation in result.get("operations") or []:
        identity = identities.get(operation.get("table_id"), {})
        runtime = runtime_operations.get(operation.get("operation_key"), {})
        destination = operation.get("destination") or {}
        role = str(operation.get("pipeline_role") or "").lower()
        is_read = role == "source"
        is_write = role == "target"
        metrics = operation.get("metrics") or runtime.get("metrics") or {}
        rows_read = operation.get("rows_read")
        if rows_read is None:
            rows_read = runtime.get("rows_read")
        if rows_read is None:
            rows_read = metrics.get("rows_read")
        rows_written = operation.get("rows_written")
        if rows_written is None:
            rows_written = runtime.get("rows_written")
        if rows_written is None:
            rows_written = metrics.get("rows_committed")
        table_name = (
            identity.get("table_name")
            or destination.get("table_name")
            or operation.get("table_id")
            or "Unknown"
        )
        rows_read_display = (
            f"{rows_read:,}" if rows_read is not None else "Not captured" if is_read else "—"
        )
        rows_written_display = (
            f"{rows_written:,}"
            if rows_written is not None
            else "Not published"
            if is_write and result.get("execution_mode") == "dry_run"
            else "Not captured"
            if is_write
            else "—"
        )
        def measured(label, name):
            value = metrics.get(name)
            return f"{value:,} {label}" if value is not None else None

        mode = str(operation.get("write_mode") or "").lower()
        if is_read:
            metric_parts = ["Batch returned"] if rows_read is not None else []
        elif mode == "scd1":
            metric_parts = [value for value in (
                measured("processed", "input_rows"), measured("inserted", "rows_inserted"),
                measured("updated", "rows_updated"), measured("unchanged", "rows_unchanged"),
            ) if value]
        elif mode == "scd2":
            metric_parts = [value for value in (
                measured("processed", "input_rows"), measured("versions inserted", "versions_inserted"),
                measured("versions expired", "versions_expired"), measured("unchanged", "rows_unchanged"),
            ) if value]
        else:
            metric_parts = [value for value in (
                measured("processed", "input_rows"), measured("inserted", "rows_inserted"),
            ) if value]
        metrics_display = ", ".join(metric_parts) or ("Not captured" if is_read or is_write else "—")
        rows.append((
            "Read" if is_read else "Write" if is_write else role.title() or "Operation",
            str(identity.get("store") or "Not captured"),
            str(identity.get("schema") or destination.get("schema") or "Not captured"),
            str(table_name),
            str(
                operation.get("read_mode")
                if is_read
                else operation.get("write_mode")
                if is_write
                else "—"
            ),
            rows_read_display,
            rows_written_display,
            metrics_display,
            str(operation.get("status") or "Not captured").replace("_", " ").title(),
            _format_duration(_elapsed_seconds(operation.get("started_at"), operation.get("completed_at"))),
            "; ".join(
                f"{stage.get('stage', 'Stage')}: {stage.get('status', 'Not captured')}"
                for stage in operation.get("stages") or []
            ) or "Not captured",
        ))
    return rows

def _print_pipeline_summary(pipeline, result):
    """Render the finalized run record as a compact notebook summary."""
    operations = result.get("operations") or []
    reads = sum(item.get("pipeline_role") == "source" for item in operations)
    writes = sum(item.get("pipeline_role") == "target" for item in operations)
    duration = _format_duration(_elapsed_seconds(result.get("started_at"), result.get("completed_at")))
    mode = str(result.get("execution_mode") or "Unknown").replace("_", " ").title()
    status = str(result.get("status") or "Unknown").replace("_", " ").upper()

    print("\n" + "=" * 72)
    print(f"FabricOps Pipeline Summary · {status}")
    print(f"Mode: {mode} | Reads: {reads} | Writes: {writes} | Duration: {duration}")
    print(f"Pipeline ID: {result.get('pipeline_id') or pipeline.pipeline_id}")
    print(f"Run ID: {result.get('run_id') or pipeline.plan.plan_id}")

    failures = result.get("failures") or []
    if failures:
        print("Failures:")
        for failure in failures:
            code = failure.get("code") or "unknown"
            exception_type = failure.get("exception_type")
            detail = f" ({exception_type})" if exception_type else ""
            print(f"  - {code}{detail}")

    rows = _operation_summary_rows(result, pipeline=pipeline)
    if not rows:
        print("No Read/Write operations were recorded.")
        print("=" * 72)
        return

    columns = [
        "Operation", "Store", "Schema", "Table", "Mode",
        "Rows read", "Rows written", "Metrics", "Status", "Duration", "Stages",
    ]
    try:
        operations_frame = pipeline.spark.createDataFrame(rows, schema=columns)
        # The Fabric notebook's native display function lives in the active
        # IPython user namespace, not necessarily in this imported module.
        display_function = globals().get("display")
        if not callable(display_function):
            from IPython import get_ipython

            shell = get_ipython()
            display_function = shell.user_ns.get("display") if shell else None
        if callable(display_function):
            display_function(operations_frame)
        else:
            operations_frame.show(truncate=False)
    except Exception:
        # Metadata is already finalized; a presentation failure must not change
        # the execution outcome or make the caller repeat a completed pipeline.
        print("Operation details could not be rendered; the run was finalized.")
    print("=" * 72)


def finalize_pipeline(pipeline=None, *, failed=False):
    """Finalize execution or reopen persisted Engineering deployment/recovery controls.

    Call once after all Reads, transformations and Writes, including read-only
    runs. Pass the session returned by setup_pipeline, or omit it to use the
    current execution. Set failed=True when a project exception was caught.
    To reopen persisted approval/deployment/recovery controls after notebook setup
    in an independent session, omit the session; FabricOps resolves the current
    notebook through the Pipeline Registry. This does not start or finalize a run,
    export a new candidate, deploy or repair automatically.
    A successful Write or cell never completes the whole pipeline by itself.
    Open sessions require the current initialized notebook configuration and
    runtime identity, whether passed explicitly or selected implicitly. Already
    closed sessions retain their recorded outcome for repeat finalization.

    Dry Run returns a session-only summary and persists no target, watermark,
    processing state, profile observation or run metadata. A completed captured
    Dry Run retains complete saved-definition and test claims in Engineering
    Files for independent submission. For a completed captured Dry Run, save a
    saved package for direct Governance selection and display its status plus
    approval refresh, explicit
    deployment and recovery controls below the summary. Repeat finalization on
    the retained session to reopen them; it reuses the package and does not
    repeat the run or deploy automatically. Presentation/export failures are
    reported separately and do not change the finalized outcome. This is not
    Governance approval. Ungoverned and
    Governed executions persist their real operational outcome. Persistent
    finalization also releases this execution's physical publication claims. Interrupted runs
    remain incomplete and are never reported as successful finalization.

    Parameters
    ----------
    pipeline : PipelineSession, optional
        Execution returned by setup_pipeline. Retain it for repeat finalization.
    failed : bool, default=False
        Mark a caught project failure; recorded failures cannot become success.

    Returns
    -------
    dict
        Final execution summary. For persistent modes this is the
        METADATA_PIPELINE_RUN snapshot; Dry Run returns the in-memory equivalent.
        Each operation retains legacy rows_read/rows_written plus its available
        detailed Read or strategy-specific Write metrics. Missing fields on
        historical records remain valid and display as not captured.
        When no session is active, returns the resolved pipeline_id and handoff
        (the displayed controls and their state/actions), without a Run record.

    Raises
    ------
    ValueError
        If pipeline is not a setup_pipeline session or audit identity is missing.
    RuntimeError
        If notebook setup is invalid, runtime identity has changed, another task
        owns the execution, or metadata publication fails. Run and Guardrail IDs
        remain stable for supported publication retries.

    Examples
    --------
    >>> pipeline = setup_pipeline(pipeline_mode="Ungoverned")
    >>> source = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
    >>> pipeline_result = finalize_pipeline(pipeline)
    >>> handoff = finalize_pipeline()

    """
    if pipeline is None:
        active = _ACTIVE_PIPELINE.get()
        if active is not None and not active.closed:
            pipeline = current_pipeline_session()
    if pipeline is None:
        if failed:
            raise ValueError("failed=True requires an active PipelineSession.")
        from fabricops_kit.config.shared import get_default_fabric_context
        from fabricops_kit.activated_pipeline.shared import resolve_pipeline_identity, display_pipeline_handoff
        runtime = get_default_fabric_context(require_notebook_setup=True)
        pipeline_id, identity = resolve_pipeline_identity(context=runtime)
        if identity["role"] != "source":
            pipeline_id = identity["row"]["pipeline_id"]
        return {"pipeline_id": pipeline_id, "handoff": display_pipeline_handoff(pipeline_id=pipeline_id, context=runtime)}
    if not isinstance(pipeline, PipelineSession):
        raise ValueError("Pass the session returned by setup_pipeline.")
    if not pipeline.owns_current_execution():
        raise RuntimeError("This execution belongs to another task or thread.")
    with pipeline.plan.lock:
        if not pipeline.closed:
            pipeline.validate_current_context()
            pipeline.plan.evidence["boundary_completed"] = not failed
            pipeline.close(failed=failed)
        if pipeline.plan.evidence.get("lease_token"):
            finalize_pipeline_run(pipeline.plan, spark_session=pipeline.spark)
        result = pipeline.plan.run_result
        # Render from the finalized run snapshot; do not re-read metadata or
        # trigger additional source/target actions just to build the report.
        _print_pipeline_summary(pipeline, result)
        if (result.get("status") == "dry_run_completed" and
                pipeline.plan.evidence.get("notebook_snapshot") is not None):
            from fabricops_kit.activated_pipeline.shared import display_pipeline_handoff
            try:
                pipeline.plan.evidence["handoff"] = display_pipeline_handoff(
                    pipeline_id=pipeline.pipeline_id, dry_run=pipeline,
                    context=pipeline.plan.runtime_context)
            except Exception as exc:
                print(f"Submission/deployment controls unavailable: {exc}. Run finalize_pipeline(pipeline) again to retry; the run outcome is unchanged.")
        return result
