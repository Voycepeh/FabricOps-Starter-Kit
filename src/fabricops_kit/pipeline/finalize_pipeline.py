"""Public completion and Testing-result publication boundary for a pipeline."""

from fabricops_kit.pipeline.shared import (
    PipelineSession,
    current_pipeline_session,
    publish_pipeline_testing_results,
)


def finalize_pipeline(pipeline=None, *, failed=False):
    """Complete the pipeline and publish its run and Guardrail results.

    Call once after all Reads, transformations and Writes, including read-only
    runs. Pass the session returned by setup_pipeline, or omit it to use the
    current execution. Set failed=True when a project exception was caught.
    A successful Write or cell never completes the whole pipeline by itself.

    Test Read/Write operations do not commit business or operational metadata.
    This explicit boundary publishes only METADATA_GUARDRAIL_RESULTS and
    METADATA_PIPELINE_RUN, with strict runtime audit identity. Complete governed
    Testing can then be reviewed for activation. Failed, partial and No Contract
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
        If another task owns the execution or metadata publication fails. Retry
        with the same session after a publication failure; result IDs are stable.

    Examples
    --------
    >>> pipeline = setup_pipeline(pipeline_id="orders", pipeline_mode="Test")
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
            pipeline.plan.evidence["boundary_completed"] = not failed
            pipeline.close(failed=failed)
        if pipeline.plan.execution_mode == "testing":
            publish_pipeline_testing_results(pipeline.plan, spark_session=pipeline.spark)
        return pipeline.plan.run_result
