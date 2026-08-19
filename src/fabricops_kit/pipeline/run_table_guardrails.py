"""Public orchestration for governed table guardrails."""

from __future__ import annotations

from typing import Any

from fabricops_kit.pipeline.check_changes import check_changes
from fabricops_kit.pipeline.check_dq import check_dq
from fabricops_kit.pipeline.check_freshness import check_freshness
from fabricops_kit.pipeline.check_schema import check_schema
from fabricops_kit.pipeline.guardrails_shared import SchemaDriftError
from fabricops_kit.pipeline.observe_table import observe_table


def _overall_status(results: dict[str, dict[str, Any]]) -> str:
    if any(not bool(result.get("can_continue", True)) for result in results.values()):
        return "failed"
    if any(str(result.get("status") or "").lower() == "warning" for result in results.values()):
        return "warning"
    return "passed"


def run_table_guardrails(
    dataframe: Any,
    table_name: str,
    *,
    target: str = "source",
    schema: str | None = None,
    observation: Any = None,
    dataset_name: str = "",
    run_id: str = "",
    row_identity_columns: list[str] | None = None,
) -> dict[str, Any]:
    """Run Schema, Freshness, Changes, and DQ guardrails for one table.

    The focused public checks remain independently callable. This function only
    coordinates them, derives the combined continuation decision, and exposes
    the DQ evaluated rows as normal-flow and blocking-failure quarantine
    DataFrames. Guardrail result persistence remains owned by the individual
    checks.

    Parameters
    ----------
    dataframe : pyspark.sql.DataFrame
        Rows to evaluate for Schema and DQ guardrails.
    table_name : str
        Physical table name within the configured target.
    target : str, default="source"
        Logical FabricOps Lakehouse or Warehouse target.
    schema : str, optional
        Physical schema containing the configured table.
    observation : pyspark.sql.DataFrame, optional
        Canonical evidence returned by :func:`observe_table`. When omitted,
        the orchestrator collects one observation before Freshness and Changes.
    dataset_name : str, optional
        Governed dataset identity forwarded to :func:`check_dq`.
    run_id : str, optional
        Pipeline run identity forwarded to :func:`check_dq`.
    row_identity_columns : list[str], optional
        Business-key columns used for DQ row-result identity.

    Returns
    -------
    dict
        Combined ``status`` and ``can_continue`` decision, individual check
        results, the canonical observation, the DQ-tagged ``dataframe``,
        ``passing_dataframe`` for normal pipeline flow, and
        ``quarantine_dataframe`` containing only blocking DQ failures.

    Notes
    -----
    Schema, Freshness, and Changes are table-level Guardrails and never create
    quarantine rows. Warning-only DQ failures remain in normal flow. Only rows
    with ``_dq_check_status = 'failed'`` are exposed through the quarantine
    DataFrame. This function does not introduce a separate quarantine storage
    convention.

    """
    resolved_observation = observation
    if resolved_observation is None:
        resolved_observation = observe_table(table_name, target=target, schema=schema)

    try:
        schema_result = check_schema(
            table_name,
            target=target,
            schema=schema,
            dataframe=dataframe,
        )
    except SchemaDriftError as exc:
        schema_result = {
            "status": "failed",
            "can_continue": False,
            "check_type": "schema",
            "severity": "blocking",
            "message": str(exc),
            "reason": str(exc),
        }

    freshness_result = check_freshness(resolved_observation)
    changes_result = check_changes(resolved_observation)
    dq_result = check_dq(
        dataframe,
        table_name,
        target=target,
        schema=schema,
        dataset_name=dataset_name,
        run_id=run_id,
        row_identity_columns=row_identity_columns,
    )

    evaluated = dq_result.get("dataframe")
    passing_dataframe = None
    quarantine_dataframe = None
    if evaluated is not None and hasattr(evaluated, "filter"):
        quarantine_dataframe = evaluated.filter("_dq_check_status = 'failed'")
        passing_dataframe = evaluated.filter(
            "_dq_check_status <> 'failed' OR _dq_check_status IS NULL"
        )

    checks = {
        "schema": schema_result,
        "freshness": freshness_result,
        "changes": changes_result,
        "dq": dq_result,
    }
    status = _overall_status(checks)
    return {
        "status": status,
        "can_continue": status != "failed",
        "checks": checks,
        "observation": resolved_observation,
        "dataframe": evaluated,
        "passing_dataframe": passing_dataframe,
        "quarantine_dataframe": quarantine_dataframe,
    }
