"""Public notebook-facing pipeline callable."""

from __future__ import annotations

from typing import Any, Mapping

from fabricops_kit.pipeline.shared import _display_guardrail_results_workflow


def display_guardrail_results(
    result_bundle: Mapping[str, Any], mode: str = "summary", spark_session: Any | None = None
) -> Any:
    """Return guardrail results prepared for summary, detailed, or debug display."""
    return _display_guardrail_results_workflow(result_bundle, mode=mode, spark_session=spark_session)


display_guardrail_results.__doc__ = _display_guardrail_results_workflow.__doc__
