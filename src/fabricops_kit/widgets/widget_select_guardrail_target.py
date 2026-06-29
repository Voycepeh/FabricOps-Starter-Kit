"""Public widget entrypoint for ``widget_select_guardrail_target``."""

from __future__ import annotations

from typing import Any

from fabricops_kit.governance_review import _guardrail_target_selection_widget_workflow


def widget_select_guardrail_target(*, spark_session: Any, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Render an interactive guardrail target selector.

    Parameters
    ----------
    spark_session : Any
        Fabric Spark session used to read metadata catalogue, enrichment, and
        guardrail rule rows.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context.

    Returns
    -------
    dict[str, Any]
        Handover state for downstream enrichment, authoring, and governance
        review widgets.

    """
    return _guardrail_target_selection_widget_workflow(spark_session=spark_session, context=context)
