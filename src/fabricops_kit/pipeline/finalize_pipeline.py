"""Public owner for complete pipeline run finalization."""

from fabricops_kit.pipeline.shared import finalize_pipeline_run


def finalize_pipeline(execution_plan, *, failed=False, spark_session=None):
    """Seal and persist one logical pipeline run after all declared operations.

    Parameters
    ----------
    execution_plan : PipelineExecutionPlan
        Shared plan returned by setup_pipeline. Use after all Reads, transforms and
        Writes, including Read-only runs. No Write or Guardrail row finalizes a run.
    failed : bool, optional
        Set True when project transformation or notebook logic failed. Orchestration
        failures are recorded automatically. Unfinalized runs remain incomplete.
    spark_session : object, optional
        Spark session for configured Engineering metadata persistence.

    Returns
    -------
    dict
        Persisted METADATA_PIPELINE_RUN snapshot. Only a complete Testing run with
        an available candidate fingerprint and no blocking or persistence failure
        has status="succeeded". Bootstrap completes as "bootstrap_completed". This does not activate
        anything; Live references its exact Activated Pipeline version.
        Repeated finalization returns the same snapshot without another write.

    Raises
    ------
    RuntimeError
        If evidence cannot be persisted; create a new plan for a retry. A final
        write with a lost acknowledgement is confirmed by exact read-back when
        possible. Unavailable read-back reports an unknown client outcome. The
        committed Delta snapshot is authoritative, independent of acknowledgement. Metadata and business stores are separate transactions
        without cross-store atomicity.
    ValueError
        If execution_plan is invalid.

    Examples
    --------
    >>> run = finalize_pipeline(plan)
    >>> run["status"]
    'succeeded'

    """
    return finalize_pipeline_run(execution_plan, failed=failed, spark_session=spark_session)
