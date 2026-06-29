"""Public widget entrypoint for ``widget_enrich_table_metadata``."""

from __future__ import annotations

from typing import Any, Mapping

from fabricops_kit.governance_review import _table_metadata_enrichment_widget_workflow


def widget_enrich_table_metadata(
    guardrail_state: Mapping[str, Any],
    *,
    spark_session: Any,
    context: dict[str, Any] | None = None,
    source_notebook_type: str = "02_pipeline",
    created_by_role: str = "engineering",
) -> dict[str, Any]:
    """Render governed table metadata enrichment controls.

    Parameters
    ----------
    guardrail_state : Mapping[str, Any]
        Guardrail target state containing table identity and catalogue profile
        rows for enrichment.
    spark_session : Any
        Fabric Spark session used when committing enrichment metadata rows.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context.
    source_notebook_type : str, default="02_pipeline"
        Notebook role recorded on authored metadata rows.
    created_by_role : str, default="engineering"
        Actor role recorded on authored metadata rows.

    Returns
    -------
    dict[str, Any]
        Rendered controls and save actions for notebook automation.

    """
    return _table_metadata_enrichment_widget_workflow(
        guardrail_state,
        spark_session=spark_session,
        context=context,
        source_notebook_type=source_notebook_type,
        created_by_role=created_by_role,
    )
