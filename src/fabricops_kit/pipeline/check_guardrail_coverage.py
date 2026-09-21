"""Public pre-write Guardrail lifecycle-readiness validation."""

from __future__ import annotations

import json
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import metadata_table_physical_schema
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io import read_lakehouse_table
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.pipeline.shared import (
    load_table_guardrail_rules,
    resolve_catalogue_table_identity,
    resolve_pipeline_data_contract,
)

_GUARDRAIL_RESULTS_TABLE = "METADATA_GUARDRAIL_RESULTS"
_SOURCE_GUARDRAILS = {"freshness", "schema", "data_quality", "source_drift"}
_TARGET_GUARDRAILS = {"schema", "sensitive_data", "data_quality"}
_LABELS = {
    "freshness": "Freshness",
    "schema": "Schema",
    "data_quality": "Data Quality",
    "source_drift": "Source Drift",
    "sensitive_data": "Sensitive Data",
}


def _rows(value: Any) -> list[dict[str, Any]]:
    source = value.collect() if hasattr(value, "collect") else value
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in source or []]


def _rules(config: Any, env: str, table_id: str, *, spark, context) -> list[dict[str, Any]]:
    rows = _rows(load_table_guardrail_rules(config, env, spark_session=spark, table_id=table_id, context=context))
    return [row for row in rows if row.get("is_active", True) is not False]


def _payload(row: dict[str, Any]) -> dict[str, Any]:
    raw = row.get("result_payload_json") or "{}"
    try:
        parsed = json.loads(raw) if isinstance(raw, str) else dict(raw)
    except (TypeError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _label(config: Any, env: str, table_id: str, *, spark, context) -> str:
    try:
        identity = resolve_catalogue_table_identity(config, env, table_id, spark_session=spark, context=context)
    except Exception:
        return table_id
    parts = (identity.get("store"), identity.get("schema"), identity.get("table_name"))
    label = ".".join(str(part).strip() for part in parts if str(part or "").strip())
    return label or table_id


def _current_activity_results(*, config: Any, env: str, context: Any, spark: Any, activity_id: str) -> list[dict[str, Any]]:
    from pyspark.sql import functions as F

    return _rows(
        read_lakehouse_table(
            _GUARDRAIL_RESULTS_TABLE,
            store="Metadata",
            schema=metadata_table_physical_schema(config, _GUARDRAIL_RESULTS_TABLE),
            spark_session=spark,
            context=context,
        ).where(
            (F.col("environment_name") == F.lit(env)) & (F.col("_activity_id") == F.lit(activity_id))
        )
    )


def _contract(config: Any, env: str, table_id: str, *, spark: Any, context: Any) -> dict[str, Any] | None:
    return resolve_pipeline_data_contract(
        config,
        env,
        table_id,
        spark_session=spark,
        context=context,
    )


def check_guardrail_coverage(
    *,
    target_table_id: str,
    source_table_ids: list[str] | tuple[str, ...],
    spark_session=None,
    verbose: bool = True,
) -> dict[str, Any]:
    """Verify that the governed pipeline is ready to publish its target.

    Development may still perform a contract-free baseline run so Engineering
    can populate Catalogue and Profile metadata before Governance authors the
    first Data Contracts. Once any Data Contract is selected, every participating
    source and target must have a selected contract with at least one active
    Guardrail that applies to its pipeline role. Every applicable configured
    Guardrail must also have current-activity evidence before publication.

    FabricOps does not require a fixed Guardrail bundle. Governance can choose
    the Guardrails appropriate to each table; Schema is a common minimal choice.
    """
    target_id = str(target_table_id or "").strip()
    source_ids = list(dict.fromkeys(str(value or "").strip() for value in source_table_ids or ()))
    if not target_id:
        raise ValueError("target_table_id must be a non-empty canonical table_id.")
    if not source_ids or any(not value for value in source_ids):
        raise ValueError("source_table_ids must contain at least one non-empty canonical table_id.")

    config, env, context = resolve_fabric_context()
    spark = get_spark_session() if spark_session is None else spark_session
    is_production = str(env).strip().lower() in {"prod", "production"}

    participants: list[dict[str, Any]] = []
    for source_id in source_ids:
        rules = _rules(config, env, source_id, spark=spark, context=context)
        applicable = [
            rule for rule in rules
            if str(rule.get("guardrail_type") or "").strip().lower() in _SOURCE_GUARDRAILS
        ]
        participants.append({
            "scope": "source",
            "table_id": source_id,
            "table_name": _label(config, env, source_id, spark=spark, context=context),
            "contract": _contract(config, env, source_id, spark=spark, context=context),
            "rules": rules,
            "applicable_rules": applicable,
        })

    target_rules = _rules(config, env, target_id, spark=spark, context=context)
    target_applicable = [
        rule for rule in target_rules
        if str(rule.get("guardrail_type") or "").strip().lower() in _TARGET_GUARDRAILS
    ]
    target_label = _label(config, env, target_id, spark=spark, context=context)
    participants.append({
        "scope": "target",
        "table_id": target_id,
        "table_name": target_label,
        "contract": _contract(config, env, target_id, spark=spark, context=context),
        "rules": target_rules,
        "applicable_rules": target_applicable,
    })

    selected_count = sum(item["contract"] is not None for item in participants)
    if selected_count == 0 and not is_production:
        result = {
            "status": "skipped",
            "can_continue": True,
            "environment_name": env,
            "activity_id": None,
            "target_table_id": target_id,
            "source_table_ids": source_ids,
            "readiness": [],
            "coverage": [],
            "missing": [],
            "issues": [],
            "reason": "No Data Contracts selected; Development baseline run.",
        }
        if verbose:
            print("FabricOps Contract Coverage")
            print("Result: SKIP (Development baseline run without selected Data Contracts)")
        return result

    readiness: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for item in participants:
        contract_selected = item["contract"] is not None
        active_count = len(item["rules"])
        applicable_count = len(item["applicable_rules"])
        ready = contract_selected and applicable_count > 0
        readiness.append({
            "scope": item["scope"],
            "table_id": item["table_id"],
            "table_name": item["table_name"],
            "contract_selected": contract_selected,
            "active_guardrail_count": active_count,
            "applicable_guardrail_count": applicable_count,
            "ready": ready,
        })
        if not contract_selected:
            issues.append({
                "scope": item["scope"],
                "table_id": item["table_id"],
                "table_name": item["table_name"],
                "reason": "missing_contract",
            })
        elif active_count == 0:
            issues.append({
                "scope": item["scope"],
                "table_id": item["table_id"],
                "table_name": item["table_name"],
                "reason": "no_active_guardrail",
            })
        elif applicable_count == 0:
            issues.append({
                "scope": item["scope"],
                "table_id": item["table_id"],
                "table_name": item["table_name"],
                "reason": "no_applicable_guardrail",
            })

    audit = build_runtime_audit_fields(config=config, env=env, runtime_context=context)
    activity_id = str(audit.get("_activity_id") or "").strip()
    if not activity_id:
        raise ValueError("Current Fabric activity_id is required to validate Guardrail coverage.")

    result_rows = _current_activity_results(
        config=config,
        env=env,
        context=context,
        spark=spark,
        activity_id=activity_id,
    )
    evidence_by_rule: dict[str, list[dict[str, Any]]] = {}
    for row in result_rows:
        evidence_by_rule.setdefault(str(row.get("guardrail_rule_id") or ""), []).append(row)

    coverage: list[dict[str, Any]] = []
    for item in participants:
        for rule in item["applicable_rules"]:
            guardrail_type = str(rule.get("guardrail_type") or "").strip().lower()
            rule_id = str(rule.get("guardrail_rule_id") or rule.get("rule_id") or "").strip()
            matches = evidence_by_rule.get(rule_id, [])
            scope = item["scope"]
            if scope == "source" and guardrail_type == "source_drift":
                matches = [
                    row for row in matches
                    if str(_payload(row).get("source_table_id") or item["table_id"]).strip() == item["table_id"]
                    and str(_payload(row).get("target_table_id") or "").strip() == target_id
                ]
                scope = "source_target"
            coverage.append({
                "scope": scope,
                "table_id": item["table_id"],
                "table_name": item["table_name"],
                "target_table_id": target_id if scope == "source_target" else None,
                "guardrail_type": guardrail_type,
                "guardrail_rule_id": rule_id,
                "evaluated": bool(matches),
            })

    missing = [item for item in coverage if not item["evaluated"]]
    can_continue = not issues and not missing
    result = {
        "status": "passed" if can_continue else "blocked",
        "can_continue": can_continue,
        "environment_name": env,
        "activity_id": activity_id,
        "target_table_id": target_id,
        "source_table_ids": source_ids,
        "readiness": readiness,
        "coverage": coverage,
        "missing": missing,
        "issues": issues,
    }

    if verbose:
        print("FabricOps Contract Coverage")
        for item in readiness:
            mark = "✓" if item["ready"] else "✗"
            print(
                f"{mark} {item['table_name']}: contract + "
                f"{item['applicable_guardrail_count']} applicable Guardrail(s)"
            )
        for item in coverage:
            scope_label = item["table_name"]
            if item["scope"] == "source_target":
                scope_label = f"{scope_label} → {target_label}"
            mark = "✓" if item["evaluated"] else "✗"
            print(f"{mark} {scope_label}: {_LABELS.get(item['guardrail_type'], item['guardrail_type'])}")
        print(f"Result: {'PASS' if can_continue else 'BLOCK'} ({env})")

    if not can_continue:
        detail: list[str] = []
        for item in issues:
            if item["reason"] == "missing_contract":
                reason = "no selected Data Contract"
            elif item["reason"] == "no_active_guardrail":
                reason = "no active Guardrail"
            else:
                reason = "no Guardrail applicable to this pipeline role"
            detail.append(f"{item['table_name']} / {reason}")
        detail.extend(
            f"{item['table_name']} / {_LABELS.get(item['guardrail_type'], item['guardrail_type'])} not evaluated"
            for item in missing
        )
        raise RuntimeError("Pipeline is not Guardrail-ready for publication: " + ", ".join(detail) + ".")
    return result
