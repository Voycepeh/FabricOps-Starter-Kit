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
    notebook_registry_id: str = "",
    notebook_id: str = "",
    pipeline_name: str = "",
    table_role: str = "",
    mode: str = "profile",
    stop_on_failure: bool | None = None,
) -> dict[str, Any]:
    """Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails.

    Runtime outcomes remain separated for ``"schema"``, ``"freshness"``, and
    ``"dq"`` result-table writes while the owning workflow performs the
    orchestration through ``_write_guardrail_result_row``.
    """
    return _run_table_guardrails_workflow(
        table_configs,
        run_id=run_id,
        context=context,
        spark_session=spark_session,
        agreement_id=agreement_id,
        agreement_version=agreement_version,
        notebook_registry_id=notebook_registry_id,
        notebook_id=notebook_id,
        pipeline_name=pipeline_name,
        table_role=table_role,
        mode=mode,
        stop_on_failure=stop_on_failure,
    )


run_table_guardrails.__doc__ = _run_table_guardrails_workflow.__doc__
