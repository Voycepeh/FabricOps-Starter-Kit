"""Canonical Guardrail result persistence helpers."""

from __future__ import annotations

import json
from typing import Any
from uuid import uuid4

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types
from fabricops_kit.io.shared import configured_lakehouse_schema, write_lakehouse_table_core


def write_guardrail_result_row(
    *,
    spark_session: Any,
    config: Any,
    env: str,
    run_id: str,
    dataset_name: str,
    table_name: str,
    store_type: str,
    layer: str,
    schema_name: str | None = None,
    guardrail_type: str,
    rule_type: str,
    result: dict[str, Any],
    rule_key: str = "",
    column_name: str = "",
    results_table: str = "METADATA_GUARDRAIL_RESULTS",
) -> None:
    """Append one runtime outcome for one exact Guardrail revision."""
    del (
        dataset_name,
        table_name,
        store_type,
        layer,
        schema_name,
        guardrail_type,
        rule_type,
        rule_key,
        column_name,
    )
    if spark_session is None or not hasattr(spark_session, "createDataFrame"):
        return
    guardrail_rule_id = str(result.get("guardrail_rule_id") or "").strip()
    if not guardrail_rule_id:
        return
    guardrail_version = int(result.get("guardrail_version") or 0)
    if guardrail_version <= 0:
        raise ValueError("guardrail_version is required to persist a Guardrail result.")
    audit = build_runtime_audit_fields(config=config, env=env)
    resolved_run_id = str(run_id or "").strip() or str(audit["_activity_id"])
    payload = {key: value for key, value in result.items() if key != "dataframe"}
    row = {
        "guardrail_result_id": str(uuid4()),
        "guardrail_rule_id": guardrail_rule_id,
        "guardrail_version": guardrail_version,
        "run_id": resolved_run_id,
        "environment_name": env,
        "status": str(result.get("status") or "not_run"),
        "can_continue": bool(result.get("can_continue", True)),
        "severity": str(result.get("severity") or "blocking"),
        "reason": str(result.get("reason") or result.get("message") or ""),
        "result_payload_json": json.dumps(
            payload,
            default=str,
            sort_keys=True,
            separators=(",", ":"),
        ),
        **audit,
    }
    write_lakehouse_table_core(
        spark_session.createDataFrame(
            [coerce_metadata_row_types(results_table, row)]
        ),
        results_table,
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
        mode="append",
    )
