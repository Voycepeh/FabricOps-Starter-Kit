"""Public completion boundary for a pipeline execution."""

from datetime import datetime, timezone

from fabricops_kit.pipeline.shared import (
    PipelineSession,
    current_pipeline_session,
    publish_pipeline_testing_results,
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


def _operation_summary_rows(result):
    """Project native Pipeline Run operations into display-only table rows."""
    rows = []
    for operation in result.get("operations") or []:
        destination = operation.get("destination") or {}
        schema = destination.get("schema")
        table_name = destination.get("table_name")
        table = ".".join(str(value) for value in (schema, table_name) if value) or operation.get("table_id", "Unknown")
        role = str(operation.get("pipeline_role") or "").lower()
        operation_name = "Read" if role == "source" else "Write" if role == "target" else role.title() or "Operation"
        stages = "; ".join(
            f"{stage.get('stage', 'Stage')}: {stage.get('status', 'Not captured')}"
            for stage in operation.get("stages") or []
        ) or "Not captured"
        duration = _elapsed_seconds(operation.get("started_at"), operation.get("completed_at"))
        rows.append((
            operation_name,
            str(table),
            str(operation.get("status") or "Not captured").replace("_", " ").title(),
            _format_duration(duration),
            stages,
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

    print("\\n" + "=" * 72)
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

    rows = _operation_summary_rows(result)
    if not rows:
        print("No Read/Write operations were recorded.")
        print("=" * 72)
        return

    columns = ["Operation", "Table", "Status", "Duration", "Stages"]
    try:
        operations_frame = pipeline.spark.createDataFrame(rows, schema=columns)
        display(operations_frame)
    except NameError:
        # Keep the function usable outside Fabric notebooks (for example, tests).
        try:
            operations_frame.show(truncate=False)
        except Exception:
            print("Operation details could not be rendered.")
    except Exception:
        # Metadata is already finalized; a presentation failure must not change
        # the execution outcome or make the caller repeat a completed pipeline.
        print("Operation details could not be rendered; the run was finalized.")
    print("=" * 72)


def finalize_pipeline(pipeline=None, *, failed=False):
    """Finalize a Dry Run, Ungoverned or Governed execution accurately.

    Call once after all Reads, transformations and Writes, including read-only
    runs. Pass the session returned by setup_pipeline, or omit it to use the
    current execution. Set failed=True when a project exception was caught.
    A successful Write or cell never completes the whole pipeline by itself.
    Open sessions require the current initialized notebook configuration and
    runtime identity, whether passed explicitly or selected implicitly. Already
    closed sessions retain their recorded outcome for repeat finalization.

    Dry Run returns a session-only summary and persists no target, watermark,
    processing state, profile observation or run metadata. Ungoverned and
    Governed executions persist their real operational outcome. Governed
    finalization also releases its activation reservation. Interrupted runs
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
        A compact operation-level Spark DataFrame is displayed from this snapshot.

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
    >>> pipeline = setup_pipeline(pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52", pipeline_mode="Ungoverned")
    >>> source = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
    >>> pipeline_result = finalize_pipeline(pipeline)

    """
    pipeline = current_pipeline_session() if pipeline is None else pipeline
    if not isinstance(pipeline, PipelineSession):
        raise ValueError("Pass the session returned by setup_pipeline.")
    if not pipeline.owns_current_execution():
        raise RuntimeError("This execution belongs to another task or thread.")
    with pipeline.plan.lock:
        if not pipeline.closed:
            pipeline.validate_current_context()
            pipeline.plan.evidence["boundary_completed"] = not failed
            pipeline.close(failed=failed)
        # Historical Test plans remain finalizable so retained approvals and
        # in-flight upgrades do not require a metadata rewrite.
        if pipeline.plan.execution_mode == "testing":
            publish_pipeline_testing_results(pipeline.plan, spark_session=pipeline.spark)
        result = pipeline.plan.run_result
        # Render from the finalized run snapshot; do not re-read metadata or
        # trigger additional source/target actions just to build the report.
        _print_pipeline_summary(pipeline, result)
        return result
