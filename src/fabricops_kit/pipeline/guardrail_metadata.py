"""Canonical Guardrail metadata readers, writers, and runtime adapters."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from typing import Any, Mapping
from uuid import uuid4

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types
from fabricops_kit.config.shared import build_metadata_table_key, get_current_audit_timestamp, is_table_not_found_error
from fabricops_kit.io.shared import configured_lakehouse_schema, read_lakehouse_table_core, write_lakehouse_table_core
from fabricops_kit.pipeline import guardrails_shared as runtime

GUARDRAIL_TABLE = "METADATA_GUARDRAIL"
GUARDRAIL_RESULTS_TABLE = "METADATA_GUARDRAIL_RESULTS"
GUARDRAIL_ROW_RESULTS_TABLE = "METADATA_GUARDRAIL_ROW_RESULTS"


def _stable_json(value: Any) -> str:
    return json.dumps(value, default=str, sort_keys=True, separators=(",", ":"))


def _row_to_dict(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        return dict(row)
    if hasattr(row, "asDict"):
        return row.asDict(recursive=True)
    return dict(row)


def _parse_parameters(row: Mapping[str, Any]) -> dict[str, Any]:
    raw = row.get("rule_parameters_json") or "{}"
    try:
        return json.loads(raw) if isinstance(raw, str) else dict(raw or {})
    except (TypeError, json.JSONDecodeError):
        return {}


def canonical_guardrail_rule_record(
    record: Mapping[str, Any],
    *,
    config: Any,
    env: str,
) -> dict[str, Any]:
    """Return one authored rule using only the Stage 4A physical contract."""
    audit = build_runtime_audit_fields(config=config, env=env)
    parameters = _parse_parameters(record)
    return {
        "guardrail_rule_id": str(record.get("guardrail_rule_id") or ""),
        "guardrail_version": int(record.get("guardrail_version") or 1),
        "table_id": str(record.get("table_id") or ""),
        "column_id": str(record.get("column_id") or ""),
        "environment_name": str(record.get("environment_name") or env),
        "guardrail_type": str(record.get("guardrail_type") or ""),
        "rule_id": str(record.get("rule_id") or ""),
        "rule_type": str(record.get("rule_type") or ""),
        "rule_parameters_json": _stable_json(parameters),
        "severity": str(record.get("severity") or "warning"),
        "is_active": bool(record.get("is_active", True)),
        **audit,
    }


def load_table_guardrail_rules(config: Any, env: str, *, spark_session: Any = None):
    """Load canonical Guardrail rules from the configured metadata target."""
    try:
        return read_lakehouse_table_core(
            GUARDRAIL_TABLE,
            target="metadata",
            schema=configured_lakehouse_schema(config, env, "metadata"),
            spark_session=spark_session,
            context={"config": config, "env": env},
        )
    except Exception as exc:
        if is_table_not_found_error(exc):
            raise ValueError("No guardrail rules exist; Governance must author and activate the required rule first.") from exc
        raise


def _select_rule(
    rules_df: Any,
    *,
    guardrail_type: str,
    table_id: str,
    environment_name: str = "",
) -> dict[str, Any] | None:
    if rules_df is None:
        return None
    rows = rules_df.collect() if hasattr(rules_df, "collect") else ([rules_df] if isinstance(rules_df, dict) else rules_df)
    candidates: list[dict[str, Any]] = []
    for raw in rows or []:
        row = _row_to_dict(raw)
        if str(row.get("guardrail_type") or "").lower() != guardrail_type.lower():
            continue
        if str(row.get("table_id") or "") != table_id:
            continue
        rule_environment = str(row.get("environment_name") or "")
        if environment_name and rule_environment != environment_name:
            continue
        if row.get("is_active") is not True:
            continue
        candidates.append(row)
    if not candidates:
        return None
    candidates.sort(
        key=lambda row: (int(row.get("guardrail_version") or 0), str(row.get("_committed_at") or "")),
        reverse=True,
    )
    return candidates[0]


def select_table_guardrail_rule(
    rules_df: Any,
    *,
    guardrail_type: str,
    metadata_table_key: str,
    environment_name: str = "",
) -> dict[str, Any] | None:
    """Select the latest active rule for one canonical Catalogue table identity."""
    return _select_rule(
        rules_df,
        guardrail_type=guardrail_type,
        table_id=metadata_table_key,
        environment_name=environment_name,
    )


def resolve_change_rule_observation_columns(rule: Mapping[str, Any]) -> tuple[str, str]:
    """Return the observation columns configured by one source-change rule."""
    return runtime.resolve_change_rule_observation_columns(dict(rule))


write_guardrail_result_row = runtime.write_guardrail_result_row


def schema_check_core(
    dataframe: Any,
    expected_schema: dict[str, str] | None = None,
    *,
    preset: str = "strict",
    rules_df: Any = None,
    dataset_name: str = "",
    table_name: str = "",
    environment_name: str = "",
    metadata_table_key: str = "",
) -> dict[str, Any]:
    """Evaluate schema intent using the normalized Guardrail rule contract."""
    del dataset_name, table_name
    if rules_df is None:
        return runtime.schema_check_core(dataframe, expected_schema, preset=preset)
    rule = _select_rule(
        rules_df,
        guardrail_type="schema",
        table_id=metadata_table_key,
        environment_name=environment_name,
    )
    if rule is None:
        return runtime.schema_check_core(dataframe, {}, preset="monitor_only")
    params = _parse_parameters(rule)
    expected = params.get("data_types") or {}
    selected_columns = params.get("columns") or list(expected)
    expected_schema = {str(column): str(expected.get(column, "")) for column in selected_columns}
    rule_type = str(rule.get("rule_type") or "relaxed").lower()
    resolved_preset = {"strict": "strict", "minimum_required": "allow_new_columns", "relaxed": "allow_new_columns", "skip": "monitor_only"}.get(
        rule_type,
        "allow_new_columns",
    )
    result = runtime.schema_check_core(dataframe, expected_schema, preset=resolved_preset)
    severity = str(rule.get("severity") or "blocking").lower()
    if result.get("status") == "failed" and severity == "warning":
        result["status"] = "warning"
        result["can_continue"] = True
    result.update(
        guardrail_type="schema",
        guardrail_rule_id=str(rule.get("guardrail_rule_id") or ""),
        guardrail_version=int(rule.get("guardrail_version") or 1),
        rule_id=str(rule.get("rule_id") or ""),
        rule_type=rule_type,
        severity=severity,
    )
    return result


def _coerce_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=None) if value.tzinfo else value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    try:
        parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
        return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed
    except ValueError:
        return None


def freshness_check_core(
    dataframe: Any,
    freshness_column: str | None = None,
    max_lag_days: int | str | None = None,
    severity: str = "blocking",
    *,
    reference_date: date | datetime | str | None = None,
    rules_df: Any = None,
    dataset_name: str = "",
    table_name: str = "",
    environment_name: str = "",
    metadata_table_key: str = "",
) -> dict[str, Any]:
    """Evaluate freshness intent using the normalized Guardrail rule contract."""
    del dataset_name, table_name
    rule = None
    maximum_age_seconds: float | None = None
    rule_type = ""
    if rules_df is not None:
        rule = _select_rule(
            rules_df,
            guardrail_type="freshness",
            table_id=metadata_table_key,
            environment_name=environment_name,
        )
        if rule is not None:
            params = _parse_parameters(rule)
            rule_type = str(rule.get("rule_type") or "max_lag_days").lower()
            if rule_type != "skip":
                freshness_column = str(params.get("freshness_column") or "")
                if params.get("maximum_age") not in (None, ""):
                    unit = str(params.get("maximum_age_unit") or "days").lower()
                    factors = {"minutes": 60, "hours": 3600, "days": 86400}
                    if unit not in factors:
                        raise ValueError("maximum_age_unit must be minutes, hours, or days")
                    maximum_age_seconds = float(params["maximum_age"]) * factors[unit]
                else:
                    max_lag_days = params.get("max_lag_days")
                severity = str(rule.get("severity") or "blocking")

    dataframe_columns = set(getattr(dataframe, "columns", ()))
    if not dataframe_columns and isinstance(dataframe, (list, tuple)) and dataframe:
        dataframe_columns = set(_row_to_dict(dataframe[0]))
    if {"table_id", "partition_value", "change_column", "max_change_value", "_committed_at"} <= dataframe_columns and rule_type != "skip":
        rows = dataframe.collect() if hasattr(dataframe, "collect") else dataframe
        change_columns = {str(_row_to_dict(row).get("change_column") or "") for row in rows or []}
        change_columns.discard("")
        if len(change_columns) != 1:
            raise ValueError("Observation evidence must contain one authoritative change_column.")
        configured = str(freshness_column or "").strip()
        observed = next(iter(change_columns))
        if configured and configured != observed:
            raise ValueError(
                "Active freshness rule is invalid for observation evidence: "
                f"freshness_column {configured!r} does not match change_column {observed!r}."
            )
        freshness_column = "max_change_value"

    column = str(freshness_column or "").strip()
    normalized_severity = str(severity or "blocking").lower().strip()
    if normalized_severity not in {"blocking", "warning"}:
        raise ValueError("severity must be one of: blocking, warning")
    base_result = {
        "status": "skipped",
        "can_continue": True,
        "check_type": "freshness",
        "freshness_column": column,
        "freshness_max_lag_days": "" if max_lag_days in (None, "") else max_lag_days,
        "freshness_severity": normalized_severity,
        "latest_value": "",
        "required_min_value": "",
        "freshness_status": "skipped",
        "freshness_can_continue": True,
        "freshness_message": "Freshness check skipped because no freshness column is configured.",
        "message": "Freshness check skipped because no freshness column is configured.",
    }
    if rule is not None:
        base_result.update(
            guardrail_type="freshness",
            guardrail_rule_id=str(rule.get("guardrail_rule_id") or ""),
            guardrail_version=int(rule.get("guardrail_version") or 1),
            rule_id=str(rule.get("rule_id") or ""),
            rule_type=rule_type,
        )
    if not column or rule_type == "skip":
        return base_result
    if maximum_age_seconds is None and (max_lag_days is None or str(max_lag_days).strip() == ""):
        raise ValueError("max_lag_days is required when freshness_column is set")
    lag_days = int(max_lag_days or 0)
    if lag_days < 0:
        raise ValueError("max_lag_days must be greater than or equal to zero")
    base_result["freshness_max_lag_days"] = lag_days
    reference = _coerce_datetime(reference_date) if reference_date is not None else datetime.now()
    if reference is None:
        raise ValueError("reference_date must be a date, datetime, or ISO date string")
    required_min = reference - timedelta(seconds=maximum_age_seconds) if maximum_age_seconds is not None else reference - timedelta(days=lag_days)
    latest_raw = runtime._max_column_value(dataframe, column)
    latest = _coerce_datetime(latest_raw)
    latest_display = latest.isoformat() if latest is not None else ("" if latest_raw is None else str(latest_raw))
    required_display = required_min.isoformat() if maximum_age_seconds is not None else required_min.date().isoformat()
    base_result.update(latest_value=latest_display, required_min_value=required_display)
    if latest is not None and latest >= required_min:
        base_result.update(
            status="passed",
            can_continue=True,
            freshness_status="passed",
            freshness_can_continue=True,
            freshness_message="Freshness check passed.",
            message="Freshness check passed.",
        )
        return base_result
    status = "failed" if normalized_severity == "blocking" else "warning"
    message = f"Freshness check failed: latest {column} is older than allowed lag."
    base_result.update(
        status=status,
        can_continue=normalized_severity == "warning",
        freshness_status=status,
        freshness_can_continue=normalized_severity == "warning",
        freshness_message=message,
        message=message,
    )
    return base_result


def evaluate_changes_guardrail(
    result: dict[str, Any],
    *,
    rules_df: Any,
    dataset_name: str = "",
    table_name: str = "",
    environment_name: str = "",
    metadata_table_key: str = "",
) -> dict[str, Any]:
    """Apply normalized source-change intent to an observation result."""
    del dataset_name, table_name
    rule = _select_rule(
        rules_df,
        guardrail_type="change",
        table_id=metadata_table_key,
        environment_name=environment_name,
    )
    if rule is None:
        raise ValueError(
            f"No active approved source-change rule exists for {metadata_table_key!r}; "
            "Governance must author and activate one first."
        )
    params = _parse_parameters(rule)
    behaviour = str(params.get("change_behaviour") or "")
    if behaviour:
        rule_type, source_pattern = runtime.resolve_guardrail_change_behaviour(behaviour)
    else:
        rule_type = str(params.get("expected_change") or rule.get("rule_type") or "monitor_only").lower()
        source_pattern = str(params.get("source_pattern") or result.get("source_pattern") or "snapshot").lower()
    severity = str(rule.get("severity") or "blocking").lower()
    if severity not in {"blocking", "warning"}:
        raise ValueError("severity must be one of: blocking, warning")
    result.update(
        guardrail_rule_id=str(rule.get("guardrail_rule_id") or ""),
        guardrail_version=int(rule.get("guardrail_version") or 1),
        rule_id=str(rule.get("rule_id") or ""),
        rule_type=rule_type,
        source_pattern=source_pattern,
        severity=severity,
    )
    if rule_type not in {"change_required", "no_change_required", "monitor_only"}:
        raise ValueError("expected_change must be one of: change_required, no_change_required, monitor_only")
    changed = bool(result.get("changed"))
    result["expected"] = {"expected_change": rule_type}
    result["actual"] = {
        "changed": changed,
        **{name: result.get(name, []) for name in ("new_partitions", "changed_partitions", "removed_partitions", "reappeared_partitions")},
    }
    if result.get("first_observation"):
        result.update(
            status="baseline_created",
            can_continue=True,
            changed=False,
            reason="First observation baseline created; change intent was not evaluated.",
        )
        result["actual"]["changed"] = None
        result["message"] = result["reason"]
        return result
    append_violation = source_pattern == "incremental_append" and int(result.get("append_violation_count") or 0) > 0
    passed = not append_violation and (
        rule_type == "monitor_only"
        or (rule_type == "change_required" and changed)
        or (rule_type == "no_change_required" and not changed)
    )
    if passed:
        result.update(status="passed", can_continue=True, reason=f"Source change expectation {rule_type!r} satisfied.")
    else:
        blocking = severity == "blocking"
        result.update(
            status="failed" if blocking else "warning",
            can_continue=not blocking,
            reason=f"Source change expectation {rule_type!r} was not satisfied.",
        )
    result["message"] = result["reason"]
    return result


def _load_active_dq_rules(metadata_df: Any, table_id: str, env: str | None = None) -> list[dict[str, Any]]:
    """Load current active DQ rules from the normalized rule table."""
    _, F, Window = runtime._spark_sql_helpers()
    columns = set(getattr(metadata_df, "columns", []))
    required = {"guardrail_rule_id", "guardrail_version", "table_id", "rule_id", "rule_type", "rule_parameters_json", "severity", "is_active"}
    missing = sorted(required - columns)
    if missing:
        raise ValueError(f"DQ metadata is missing canonical Guardrail columns: {', '.join(missing)}")
    latest = metadata_df.filter(F.col("table_id") == table_id)
    if env is not None and "environment_name" in columns:
        latest = latest.filter(F.col("environment_name") == env)
    order = [F.col("guardrail_version").desc_nulls_last()]
    if "_committed_at" in columns:
        order.append(F.col("_committed_at").desc_nulls_last())
    window = Window.partitionBy(F.col("guardrail_rule_id")).orderBy(*order)
    latest = latest.withColumn("_rn", F.row_number().over(window)).filter(F.col("_rn") == 1).drop("_rn")
    latest = latest.filter(F.col("is_active") == True)
    rules: list[dict[str, Any]] = []
    for row in (_row_to_dict(item) for item in latest.collect()):
        params = _parse_parameters(row)
        columns_value = params.pop("columns", [])
        rule_columns = [str(value) for value in columns_value] if isinstance(columns_value, (list, tuple)) else [str(columns_value)]
        rules.append(
            {
                "rule_id": str(row.get("rule_id") or ""),
                "guardrail_rule_id": str(row.get("guardrail_rule_id") or ""),
                "guardrail_version": int(row.get("guardrail_version") or 1),
                "rule_type": str(row.get("rule_type") or ""),
                "columns": [value for value in rule_columns if value],
                "severity": runtime._normalize_dq_severity(row.get("severity")),
                **params,
            }
        )
    return runtime._validate_dq_rules(rules)


def _read_dq_rule_metadata(config: Any, env: str, *, spark_session: Any = None):
    frame = load_table_guardrail_rules(config, env, spark_session=spark_session)
    if "guardrail_type" in set(getattr(frame, "columns", [])):
        _, F, _ = runtime._spark_sql_helpers()
        return frame.filter(F.lower(F.coalesce(F.col("guardrail_type"), F.lit(""))) == "dq")
    return frame


def check_dq_runtime(
    dataframe: Any,
    config: Any,
    env: str,
    table_name: str,
    *,
    target: str,
    store_type: str,
    schema_name: str | None,
    dataset_name: str = "",
    run_id: str = "",
    row_identity_columns: list[str] | None = None,
) -> dict[str, Any]:
    """Evaluate DQ rules and persist normalized rule and failed-row evidence."""
    del dataset_name
    spark_session = getattr(dataframe, "sparkSession", None)
    if spark_session is None or not hasattr(spark_session, "createDataFrame"):
        raise RuntimeError("check_dq requires a Spark DataFrame in the active Microsoft Fabric runtime.")
    source_columns = list(getattr(dataframe, "columns", []))
    identities = list(row_identity_columns or [])
    if not identities:
        identities = [name for name in ("row_uuid", "_row_uuid", "row_id") if name in source_columns][:1]
    missing_identities = [name for name in identities if name not in source_columns]
    if missing_identities:
        raise ValueError(f"row_identity_columns not found in dataframe: {', '.join(missing_identities)}")

    table_id = build_metadata_table_key(store_type, target, schema_name, table_name)
    metadata_df = _read_dq_rule_metadata(config, env, spark_session=spark_session)
    rules = _load_active_dq_rules(metadata_df, table_id, env=env)
    checks = runtime._run_dq_guardrail_checks(dataframe, table_name, rules) if rules else []
    result = runtime._summarize_dq_guardrail(checks)
    result["dataframe"] = runtime._dq_tagged_dataframe(dataframe, rules)
    total_count = int(dataframe.count())
    failed_row_count = 0
    if rules:
        _, F, _ = runtime._spark_sql_helpers()
        any_failure = F.lit(False)
        for rule in rules:
            any_failure = any_failure | runtime._dq_failed_expression(dataframe, rule)
        failed_row_count = int(dataframe.filter(any_failure).count())
    result["summary"] = {
        "DQ_STATUS": result["status"],
        "DQ_RULE_COUNT": len(checks),
        "DQ_FAILED_RULE_COUNT": sum(not check["passed"] for check in checks),
        "DQ_WARNING_RULE_COUNT": sum(check["status"] == "warning" for check in checks),
        "DQ_ERROR_RULE_COUNT": sum(check["status"] == "failed" for check in checks),
        "DQ_FAILED_ROW_COUNT": failed_row_count,
        "DQ_FAILED_ROW_PERCENT": float(round((failed_row_count / total_count) * 100, 4)) if total_count else 0.0,
        "DQ_CHECKED_AT": get_current_audit_timestamp(config=config, drop_microseconds=False),
    }
    if not rules:
        return result

    audit = build_runtime_audit_fields(config=config, env=env)
    resolved_run_id = str(run_id or "").strip() or str(audit["_activity_id"]).strip()
    result["run_id"] = resolved_run_id
    check_by_id = {check["rule_id"]: check for check in checks}
    result_ids = {rule["rule_id"]: str(uuid4()) for rule in rules}
    summary_rows = []
    for rule in rules:
        check = check_by_id[rule["rule_id"]]
        rule_payload = {
            key: value
            for key, value in rule.items()
            if key not in {"guardrail_rule_id", "guardrail_version", "severity"}
        }
        summary_rows.append(
            {
                "guardrail_result_id": result_ids[rule["rule_id"]],
                "guardrail_rule_id": rule["guardrail_rule_id"],
                "guardrail_version": rule["guardrail_version"],
                "run_id": resolved_run_id,
                "environment_name": env,
                "status": check["status"],
                "can_continue": check["status"] != "failed",
                "severity": rule["severity"],
                "reason": "Rule passed." if check["passed"] else f"{check['failed_count']} row(s) failed {rule['rule_type']}.",
                "result_payload_json": _stable_json({"rule": rule_payload, "result": check}),
                **audit,
            }
        )
    context = {"config": config, "env": env}
    write_lakehouse_table_core(
        spark_session.createDataFrame(
            [coerce_metadata_row_types(GUARDRAIL_RESULTS_TABLE, row) for row in summary_rows]
        ),
        GUARDRAIL_RESULTS_TABLE,
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        context=context,
        mode="append",
    )

    _, F, _ = runtime._spark_sql_helpers()
    if identities:
        row_identity = F.to_json(
            F.struct(*[F.col(name).alias(name) for name in identities]),
            {"ignoreNullFields": "false"},
        )
    else:
        canonical_row = F.to_json(
            F.struct(*[F.col(name).alias(name) for name in sorted(source_columns)]),
            {"ignoreNullFields": "false"},
        )
        row_identity = F.sha2(canonical_row, 256)
    evidence_frames = []
    for rule in rules:
        involved = list(dict.fromkeys([*rule["columns"], str(rule.get("condition_column") or "")]))
        involved = [name for name in involved if name and name in source_columns]
        evidence_frames.append(
            dataframe.filter(runtime._dq_failed_expression(dataframe, rule)).select(
                F.expr("uuid()").alias("guardrail_row_result_id"),
                F.lit(result_ids[rule["rule_id"]]).alias("guardrail_result_id"),
                row_identity.alias("row_identity"),
                F.lit(_stable_json(involved)).alias("involved_columns_json"),
                F.to_json(
                    F.struct(*[F.col(name).alias(name) for name in involved]),
                    {"ignoreNullFields": "false"},
                ).alias("failed_values_json"),
                F.lit(f"Row failed {rule['rule_type']} rule {rule['rule_id']}.").alias("failure_reason"),
                *[
                    F.lit(value).cast("timestamp" if key == "_committed_at" else "string").alias(key)
                    for key, value in audit.items()
                ],
            )
        )
    evidence = evidence_frames[0]
    for frame in evidence_frames[1:]:
        evidence = evidence.unionByName(frame)
    if evidence.limit(1).count():
        write_lakehouse_table_core(
            evidence,
            GUARDRAIL_ROW_RESULTS_TABLE,
            target="metadata",
            schema=configured_lakehouse_schema(config, env, "metadata"),
            context=context,
            mode="append",
        )
    return result
