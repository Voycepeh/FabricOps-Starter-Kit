"""Public end boundary for Data Contract governed pipeline execution."""
from fabricops_kit.pipeline.shared import PipelineExecutionPlan, finalize_pipeline_run


def finalize_pipeline(execution_plan, *, failed=False, spark_session=None):
    """Consolidate orchestration outcomes and finalize the pipeline tracking record.

    Call after every declared Read, transformation and Write, including read-only
    runs. Reuses setup context and recorded results without counting DataFrames.
    Set failed=True for a caught project exception; orchestrator failures are
    recorded automatically. A stopped notebook remains incomplete.

    Returns the persisted METADATA_PIPELINE_RUN summary with exact Data Contract
    versions, status and activation revision. Repeated finalization returns the
    original snapshot without another write. Existing execution reservations are
    released after persistence. Metadata failure raises RuntimeError; invalid
    execution_plan raises ValueError. Business writes and metadata remain separate
    transactions. This function neither activates contracts nor verifies code.

    Examples
    --------
    >>> pipeline_result = finalize_pipeline(pipeline)
    >>> pipeline_result["status"]
    'succeeded'

    """
    if not isinstance(execution_plan, PipelineExecutionPlan):
        raise ValueError("An explicit PipelineExecutionPlan is required.")
    with execution_plan.lock:
        if not execution_plan.evidence.get("sealed"):
            execution_plan.evidence["boundary_completed"] = not failed
        return finalize_pipeline_run(execution_plan, failed=failed,
            spark_session=spark_session if spark_session is not None else execution_plan.runtime_context.get("_pipeline_spark"))
