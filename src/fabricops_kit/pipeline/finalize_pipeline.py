"""Public completion and Testing-result publication boundary for a pipeline."""

from fabricops_kit.pipeline.shared import (
    PipelineSession,
    current_pipeline_session,
    publish_pipeline_testing_results,
)


def finalize_pipeline(pipeline=None, *, failed=False):
    """Finalize execution and commit the complete Test or Live outcome.

    Call once after all Reads, transformations and Writes, including read-only
    runs. Pass the session returned by setup_pipeline, or omit it to use the
    current execution. Set failed=True when a project exception was caught.
    A successful Write or cell never completes the whole pipeline by itself.
    Open sessions require the current initialized notebook configuration and
    runtime identity, whether passed explicitly or selected implicitly. Already
    closed sessions retain their recorded outcome for repeat finalization.

    Test Read/Write operations do not commit business or operational metadata.
    Explicit finalization commits the complete Test run and Guardrail results
    for Governance review. Successful Test finalization also saves the already
    calculated observations to METADATA_DATA_CATALOGUE, METADATA_DATA_PROFILED
    and METADATA_DATA_PROFILED_FREQUENCY for Data Contract authoring, without
    repeating the profiling scans or publishing business data.
    Failed and incomplete runs do not publish profiling observations. The activation
    widget reads the committed run and Guardrail records. Complete governed Testing can then be approved. Failed, partial and No Contract
    runs cannot authorize activation. Live finalization releases its reservation
    after recording the final outcome. Interrupted runs remain incomplete.

    Parameters
    ----------
    pipeline : PipelineSession, optional
        Execution returned by setup_pipeline. Retain it for repeat finalization.
    failed : bool, default=False
        Mark a caught project failure; recorded failures cannot become success.

    Returns
    -------
    dict
        Final METADATA_PIPELINE_RUN snapshot. Repeating with the same session
        returns the original result without additional successful commits.

    Raises
    ------
    ValueError
        If pipeline is not a setup_pipeline session or audit identity is missing.
    RuntimeError
        If notebook setup is invalid, runtime identity has changed, another task
        owns the execution, or metadata publication fails. Run and Guardrail IDs
        remain stable for supported publication retries. A Test profile-publication
        failure records a failed outcome and requires a new Test execution.

    Examples
    --------
    >>> pipeline = setup_pipeline(pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52", pipeline_mode="Test")
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
        if pipeline.plan.execution_mode == "testing":
            try:
                publish_pipeline_testing_results(pipeline.plan, spark_session=pipeline.spark)
            finally:
                pipeline.refresh()
        if pipeline.report is None:
            print(f"FabricOps Pipeline · {pipeline.plan.run_result['status']}\nPipeline ID: {pipeline.pipeline_id}")
        return pipeline.plan.run_result
