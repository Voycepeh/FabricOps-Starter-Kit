"""Pipeline-owned metadata evidence writers."""

from __future__ import annotations

import json
import uuid
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.shared import build_metadata_table_key
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types
from fabricops_kit.io.shared import configured_lakehouse_schema, write_lakehouse_table_core


def _write_guardrail_result_row(
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
    """Append one runtime guardrail outcome to ``METADATA_GUARDRAIL_RESULTS``."""
    if spark_session is None or not hasattr(spark_session, "createDataFrame"):
        return
    audit = build_runtime_audit_fields(config=config, env=env)
    row = {
        "guardrail_result_id": str(uuid.uuid4()),
        "result_id": str(uuid.uuid4()),
        "guardrail_rule_id": str(result.get("guardrail_rule_id") or rule_key or result.get("rule_key") or f"{guardrail_type}_default"),
        "rule_key": str(rule_key or result.get("rule_key") or f"{guardrail_type}_default"),
        "guardrail_level": "column" if column_name else "table",
        "metadata_table_key": str(
            result.get("metadata_table_key")
            or build_metadata_table_key(store_type, layer, schema_name, table_name)
        ),
        "metadata_column_key": result.get("metadata_column_key") or None,
        "environment_name": env,
        "dataset_name": dataset_name,
        "table_name": table_name,
        "column_name": column_name,
        "guardrail_type": guardrail_type,
        "rule_type": rule_type,
        "status": str(result.get("status") or "not_run"),
        "can_continue": bool(result.get("can_continue", True)),
        "severity": str(result.get("severity") or "blocking"),
        "reason": str(result.get("message") or result.get("reason") or ""),
        "expected_value_json": json.dumps(result.get("expected") or result.get("expected_value_json") or {}, default=str, sort_keys=True),
        "actual_value_json": json.dumps(result.get("actual") or result.get("actual_value_json") or {}, default=str, sort_keys=True),
        "result_payload_json": json.dumps(
            {key: value for key, value in result.items() if key not in {"dataframe", "row_changes"}},
            default=str,
            sort_keys=True,
        ),
        **audit,
    }
    context = {"config": config, "env": env}
    write_lakehouse_table_core(
        spark_session.createDataFrame([coerce_metadata_row_types(results_table, row)]),
        results_table,
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        context=context,
        mode="append",
    )
