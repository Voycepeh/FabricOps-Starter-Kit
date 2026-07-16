"""Public notebook-facing pipeline callable."""

from __future__ import annotations

from typing import Any, Mapping

from fabricops_kit.pipeline.shared import _run_table_guardrails_workflow


def run_table_guardrails(
    table_configs: list[dict[str, Any]],
    *,
    run_id: str | None = None,
    context: dict[str, Any] | None = None,
    spark_session: Any | None = None,
    agreement_id: str = "",
    agreement_version: str = "",
    table_role: str = "",
    mode: str = "profile",
    stop_on_failure: bool | None = None,
) -> dict[str, Any]:
    """Run approved checks for configured source or target tables.

    Runs schema, freshness, profile-change, and DQ checks for each prepared
    table configuration, saves runtime outcomes where configured, and returns
    whether the notebook can continue.
    """
    return _run_table_guardrails_workflow(
        table_configs,
        run_id=run_id,
        context=context,
        spark_session=spark_session,
        agreement_id=agreement_id,
        agreement_version=agreement_version,
        table_role=table_role,
        mode=mode,
        stop_on_failure=stop_on_failure,
    )


run_table_guardrails.__doc__ = _run_table_guardrails_workflow.__doc__
