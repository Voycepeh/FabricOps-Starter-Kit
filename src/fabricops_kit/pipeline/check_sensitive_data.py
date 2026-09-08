"""Public preparation-first Sensitive Data Guardrail enforcement."""

from __future__ import annotations

import json
from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.pipeline.shared import (
    build_token_map_frame,
    load_table_guardrail_rules,
    resolve_catalogue_table_identity,
    write_guardrail_result_row,
)


def _rows(value) -> list[dict[str, Any]]:
    source = value.collect() if hasattr(value, "collect") else value
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in source or []]


def _parameters(rule: dict[str, Any]) -> dict[str, Any]:
    raw = rule.get("rule_parameters_json") or "{}"
    try:
        parsed = json.loads(raw) if isinstance(raw, str) else dict(raw)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Sensitive Data rule_parameters_json must contain a JSON object.") from exc
    if not isinstance(parsed, dict):
        raise ValueError("Sensitive Data rule_parameters_json must contain a JSON object.")
    return parsed


def check_sensitive_data(dataframe, *, table_id: str, run_id: str = "") -> dict:
    """Apply exact-contract Sensitive Data Guardrails before a governed write.

    Parameters
    ----------
    dataframe : pyspark.sql.DataFrame
        Prepared business rows whose governed sensitive columns must be treated.
    table_id : str
        Canonical identity used to resolve the applicable exact Data Contract version.
    run_id : str, optional
        Pipeline run identity recorded with Guardrail summary evidence.

    Returns
    -------
    dict
        ``dataframe`` contains every successfully applied treatment;
        ``support_mapping`` contains caller-owned token mappings, or ``None``;
        ``checks`` contains sanitized outcomes; and ``can_continue`` is false
        only when a Block treatment fails. No mapping is persisted automatically.

    Raises
    ------
    RuntimeError
        If ``dataframe`` is not a Spark DataFrame in the Fabric runtime.

    Notes
    -----
    Only active ``sensitive_data`` Guardrails from the exact applicable Data
    Contract version are processed. Classification Enrichment is never read and
    never triggers a transformation. ``tokenize`` uses deterministic SHA-256
    tokens scoped by ``table_id`` and ``column_id`` and preserves nulls;
    ``remove`` drops the governed column. Warn failures leave the input unchanged
    for that rule and permit continuation, while Block failures require callers
    to stop before writing. Raw values exist only in the returned support mapping
    and are excluded from ``METADATA_GUARDRAIL_RESULTS``.

    Examples
    --------
    >>> result = check_sensitive_data(transformed_df, table_id=TARGET_TABLE_ID)
    >>> stop_if_failed(result)
    >>> write_prep = write_pipeline_prep(result["dataframe"], target_table_id=TARGET_TABLE_ID, source_preps=sources)

    See Also
    --------
    write_pipeline_prep, write_pii_token_map, stop_if_failed

    """
    spark_session = getattr(dataframe, "sparkSession", None)
    if spark_session is None or not hasattr(spark_session, "createDataFrame"):
        raise RuntimeError("check_sensitive_data requires a Spark DataFrame in the active Microsoft Fabric runtime.")
    config, env, context = resolve_fabric_context()
    identity = resolve_catalogue_table_identity(
        config, env, table_id, spark_session=spark_session, context=context
    )
    rules = [
        row
        for row in _rows(load_table_guardrail_rules(
            config, env, spark_session=spark_session, table_id=identity["table_id"], context=context
        ))
        if str(row.get("guardrail_type") or "").strip().lower() == "sensitive_data"
        and row.get("is_active", True) is not False
    ]
    transformed = dataframe
    mappings = []
    checks = []
    from pyspark.sql import functions as F

    for index, rule in enumerate(rules):
        action = str(rule.get("action") or "Warn").strip().title()
        column_id = str(rule.get("column_id") or "").strip()
        column_name = str(rule.get("column_name") or "").strip()
        treatment = ""
        error = ""
        try:
            params = _parameters(rule)
            treatment = str(params.get("treatment") or "").strip().lower()
            if action not in {"Warn", "Block"}:
                raise ValueError("Sensitive Data action must be Warn or Block.")
            if params.get("scope") != "column" or not column_id or not column_name:
                raise ValueError("Sensitive Data Guardrail has an unresolved column identity or invalid scope.")
            if treatment not in {"tokenize", "remove"}:
                raise ValueError(f"Unsupported Sensitive Data treatment: {treatment or '<blank>'}.")
            if column_name not in transformed.columns:
                raise ValueError(f"Sensitive Data column {column_name!r} is missing from the DataFrame.")
            if treatment == "remove":
                transformed = transformed.drop(column_name)
            else:
                original_temp = f"__fabricops_sensitive_original_{index}"
                token_temp = f"__fabricops_sensitive_token_{index}"
                staged = transformed.withColumn(original_temp, F.col(column_name)).withColumn(
                    token_temp,
                    F.when(F.col(original_temp).isNull(), F.lit(None)).otherwise(
                        F.sha2(F.concat_ws("|", F.lit(identity["table_id"]), F.lit(column_id), F.col(original_temp).cast("string")), 256)
                    ),
                )
                non_null = staged.where(F.col(original_temp).isNotNull())
                mapping = build_token_map_frame(
                    non_null, table_id=identity["table_id"], column_id=column_id,
                    original_column=original_temp, token_column=token_temp, context=context,
                )
                mappings.append(mapping)
                transformed = staged.withColumn(column_name, F.col(token_temp)).drop(original_temp, token_temp)
        except Exception as exc:
            error = str(exc)
        passed = not error
        can_continue = passed or action == "Warn"
        check = {
            "guardrail_rule_id": str(rule.get("guardrail_rule_id") or rule.get("rule_id") or ""),
            "guardrail_version": int(rule.get("guardrail_version") or 1),
            "contract_id": str(rule.get("contract_id") or ""),
            "contract_version": int(rule.get("contract_version") or 0),
            "table_id": identity["table_id"], "column_id": column_id,
            "treatment": treatment, "action": action,
            "status": "passed" if passed else ("warning" if can_continue else "failed"),
            "can_continue": can_continue,
            "severity": "warning" if action == "Warn" else "blocking",
            "reason": "Treatment applied." if passed else error,
        }
        checks.append(check)
        write_guardrail_result_row(
            spark_session=spark_session, config=config, env=env, run_id=run_id,
            dataset_name="", table_name=identity["table_name"], store_type=identity["store_type"],
            layer="", schema_name=identity["schema"], guardrail_type="sensitive_data",
            rule_type=treatment, result=check, column_name=column_name,
        )
    support_mapping = None
    if mappings:
        support_mapping = mappings[0]
        for mapping in mappings[1:]:
            support_mapping = support_mapping.unionByName(mapping)
    can_continue = all(check["can_continue"] for check in checks)
    return {
        "status": "passed" if all(check["status"] == "passed" for check in checks) else ("warning" if can_continue else "failed"),
        "can_continue": can_continue,
        "dataframe": transformed,
        "support_mapping": support_mapping,
        "checks": checks,
    }
