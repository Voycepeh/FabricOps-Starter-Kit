"""Public notebook-facing pipeline callable."""

from __future__ import annotations

from typing import Any, Mapping

from fabricops_kit.pipeline.shared import LINEAGE_TABLE, _write_pipeline_lineage_workflow


def write_pipeline_lineage(
    *,
    spark: Any,
    run_id: str,
    context: dict[str, Any] | None = None,
    source_definitions: Mapping[str, Mapping[str, Any]],
    target_definitions: Mapping[str, Mapping[str, Any]],
    relationships: list[Mapping[str, Any]] | None = None,
    dataset_name: str = "",
    agreement_id: str = "",
    agreement_contract_version: str = "",
    notebook_registry_id: str = "",
    notebook_id: str = "",
    pipeline_name: str = "",
    metadata_table: str = LINEAGE_TABLE,
    mode: str = "append",
) -> dict[str, Any]:
    """Write many-to-many source-to-target lineage evidence."""
    return _write_pipeline_lineage_workflow(
        spark=spark,
        run_id=run_id,
        context=context,
        source_definitions=source_definitions,
        target_definitions=target_definitions,
        relationships=relationships,
        dataset_name=dataset_name,
        agreement_id=agreement_id,
        agreement_contract_version=agreement_contract_version,
        notebook_registry_id=notebook_registry_id,
        notebook_id=notebook_id,
        pipeline_name=pipeline_name,
        metadata_table=metadata_table,
        mode=mode,
    )


write_pipeline_lineage.__doc__ = _write_pipeline_lineage_workflow.__doc__
