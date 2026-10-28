"""Public completion boundary for a pipeline execution."""

from fabricops_kit.pipeline.shared import (
    PipelineSession,
    current_pipeline_session,
    publish_pipeline_testing_results,
)


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
        if pipeline.report is None:
            print(f"FabricOps Pipeline · {pipeline.plan.run_result['status']}\nPipeline ID: {pipeline.pipeline_id}")
        return pipeline.plan.run_result
