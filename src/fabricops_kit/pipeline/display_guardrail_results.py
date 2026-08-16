"""Public notebook-facing pipeline callable."""

from __future__ import annotations

from typing import Any, Mapping

from fabricops_kit.pipeline.shared import _display_guardrail_results_workflow


def display_guardrail_results(
    result_bundle: Mapping[str, Any] | None = None,
    mode: str = "summary",
    spark_session: Any | None = None,
    *,
    metadata_table_key: str | None = None,
    run_id: str | None = None,
    target: str = "metadata",
    schema: str | None = None,
) -> Any:
    """Prepare in-memory or persisted guardrail results for notebook display."""
    return _display_guardrail_results_workflow(
        result_bundle,
        mode=mode,
        spark_session=spark_session,
        metadata_table_key=metadata_table_key,
        run_id=run_id,
        target=target,
        schema=schema,
    )


display_guardrail_results.__doc__ = _display_guardrail_results_workflow.__doc__
