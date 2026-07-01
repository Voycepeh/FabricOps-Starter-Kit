"""Public notebook-facing pipeline run summary callable."""

from __future__ import annotations

from typing import Any, Mapping

from fabricops_kit.pipeline.shared import METADATA_PIPELINE_RUNS_TABLE, _write_pipeline_run_summary_workflow


def write_pipeline_run_summary(
    *,
    spark: Any | None = None,
    run_id: str | None = None,
    context: dict[str, Any] | None = None,
    agreement_id: str = "",
    agreement_contract_version: str = "",
    notebook_registry_id: str = "",
    notebook_id: str = "",
    notebook_type: str = "02_pipeline",
    pipeline_name: str = "",
    started_at: str | None = None,
    completed_at: str | None = None,
    status: str = "completed",
    source_definitions: Mapping[str, Mapping[str, Any]] | None = None,
    target_definitions: Mapping[str, Mapping[str, Any]] | None = None,
    source_schema_results: Mapping[str, Mapping[str, Any]] | None = None,
    target_schema_results: Mapping[str, Mapping[str, Any]] | None = None,
    source_freshness_results: Mapping[str, Mapping[str, Any]] | None = None,
    target_freshness_results: Mapping[str, Mapping[str, Any]] | None = None,
    source_stability_results: Mapping[str, Mapping[str, Any]] | None = None,
    target_stability_results: Mapping[str, Mapping[str, Any]] | None = None,
    source_dq_results: Mapping[str, Mapping[str, Any]] | None = None,
    target_dq_results: Mapping[str, Mapping[str, Any]] | None = None,
    lineage_status: str = "not_run",
    catalogue_status: str = "not_run",
    message: str = "",
    source_guardrail_results: Mapping[str, Any] | None = None,
    target_guardrail_results: Mapping[str, Any] | None = None,
    target_write_status: Mapping[str, Any] | None = None,
    lineage_result: Mapping[str, Any] | None = None,
    metadata_table: str = METADATA_PIPELINE_RUNS_TABLE,
    mode: str = "append",
) -> dict[str, Any]:
    """Write a pipeline runtime summary to metadata."""
    return _write_pipeline_run_summary_workflow(
        spark=spark,
        run_id=run_id,
        context=context,
        agreement_id=agreement_id,
        agreement_contract_version=agreement_contract_version,
        notebook_registry_id=notebook_registry_id,
        notebook_id=notebook_id,
        notebook_type=notebook_type,
        pipeline_name=pipeline_name,
        started_at=started_at,
        completed_at=completed_at,
        status=status,
        source_definitions=source_definitions,
        target_definitions=target_definitions,
        source_schema_results=source_schema_results,
        target_schema_results=target_schema_results,
        source_freshness_results=source_freshness_results,
        target_freshness_results=target_freshness_results,
        source_stability_results=source_stability_results,
        target_stability_results=target_stability_results,
        source_dq_results=source_dq_results,
        target_dq_results=target_dq_results,
        lineage_status=lineage_status,
        catalogue_status=catalogue_status,
        message=message,
        source_guardrail_results=source_guardrail_results,
        target_guardrail_results=target_guardrail_results,
        target_write_status=target_write_status,
        lineage_result=lineage_result,
        metadata_table=metadata_table,
        mode=mode,
    )


write_pipeline_run_summary.__doc__ = _write_pipeline_run_summary_workflow.__doc__
