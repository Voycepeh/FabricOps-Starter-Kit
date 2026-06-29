"""Public widget entrypoint for ``widget_review_guardrail_governance``."""

from __future__ import annotations

from typing import Any, Mapping

from fabricops_kit.governance_review import _guardrail_governance_review_widget_workflow


def widget_review_guardrail_governance(
    state: Mapping[str, Any],
    *,
    spark_session: Any = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Render governance policy and shared rule-review controls.

    Parameters
    ----------
    state : Mapping[str, Any]
        Guardrail state with existing enrichment and guardrail rule records to
        review.
    spark_session : Any, optional
        Fabric Spark session used when saving governance review decisions.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context.

    Returns
    -------
    dict[str, Any]
        Rendered controls and review actions for notebook automation.

    """
    return _guardrail_governance_review_widget_workflow(state, spark_session=spark_session, context=context)
