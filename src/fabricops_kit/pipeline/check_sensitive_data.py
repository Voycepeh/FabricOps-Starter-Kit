"""Public preparation-first Sensitive Data Guardrail enforcement."""

from __future__ import annotations

import json
from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.data_contract.shared import validate_sensitive_data_parameters
from fabricops_kit.pipeline.shared import (
    load_table_guardrail_rules,
    resolve_pipeline_data_contract,
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


def _tokenize_column(dataframe, *, column_name, column_id, table_id, existing_mapping):
    """Return a tokenized DataFrame and its validated caller-owned mapping."""
    from pyspark.sql import functions as F

    required = {"table_id", "column_id", "original_value", "token_value"}
    if existing_mapping is None:
        established = None
    else:
        missing = sorted(required - set(existing_mapping.columns))
        if missing:
            raise ValueError(
                "existing_mapping is missing required column(s): " + ", ".join(missing) + "."
            )
        established = existing_mapping.where(
            (F.col("table_id") == table_id) & (F.col("column_id") == column_id)
        ).select("table_id", "column_id", "original_value", "token_value").dropDuplicates()
        if established.where(
            F.col("original_value").isNull() | F.col("token_value").isNull()
        ).limit(1).count():
            raise ValueError("Existing token mappings must contain non-null original and token values.")
        if established.groupBy("original_value").agg(
            F.countDistinct("token_value").alias("count")
        ).where(F.col("count") > 1).limit(1).count():
            raise ValueError("Existing mapping assigns multiple tokens to one original value.")
        if established.groupBy("token_value").agg(
            F.countDistinct("original_value").alias("count")
        ).where(F.col("count") > 1).limit(1).count():
            raise ValueError("Existing mapping reuses one token for multiple original values.")

    original_type = dataframe.schema[column_name].dataType.simpleString()
    originals = dataframe.where(F.col(column_name).isNotNull()).select(
        F.col(column_name).cast("string").alias("original_value")
    ).dropDuplicates()
    unmatched = originals if established is None else originals.join(
        established.select("original_value"), on="original_value", how="left_anti"
    )
    generated = unmatched.withColumn("token_value", F.expr("uuid()"))
    generated = generated.withColumn("table_id", F.lit(table_id)).withColumn(
        "column_id", F.lit(column_id)
    ).select("table_id", "column_id", "original_value", "token_value")
    available_mapping = generated if established is None else established.unionByName(generated)
    mapping = available_mapping.join(originals, on="original_value", how="inner").withColumn(
        "original_data_type", F.lit(original_type)
    ).cache()
    mapping.count()  # Materialize opaque UUID assignments once for this returned mapping/run.
    original_temp = "__fabricops_sensitive_original"
    token_temp = "__fabricops_sensitive_token"
    while original_temp in dataframe.columns or token_temp in dataframe.columns:
        original_temp += "_"
        token_temp += "_"
    lookup = mapping.select(
        F.col("original_value").alias(original_temp),
        F.col("token_value").alias(token_temp),
    )
    tokenized = dataframe.withColumn(original_temp, F.col(column_name).cast("string")).join(
        F.broadcast(lookup), on=original_temp, how="left"
    ).withColumn(
        column_name,
        F.when(F.col(original_temp).isNull(), F.lit(None)).otherwise(F.col(token_temp)),
    ).drop(original_temp, token_temp)
    return tokenized, mapping


def _mask_column(dataframe, *, column_name, parameters):
    """Return rows with the configured middle characters obscured."""
    from pyspark.sql import functions as F

    preserve_start = parameters["preserve_start"]
    preserve_end = parameters["preserve_end"]
    value = F.col(column_name).cast("string")
    length = F.length(value)
    mask_literal = "'" + parameters["mask_character"].replace("'", "''") + "'"
    hidden = F.expr(
        f"repeat({mask_literal}, greatest(length(cast(`{column_name.replace('`', '``')}` as string)) "
        f"- {preserve_start} - {preserve_end}, 0))"
    )
    if preserve_start:
        start = F.substring(value, 1, preserve_start)
    else:
        start = F.lit("")
    if preserve_end:
        end = F.reverse(F.substring(F.reverse(value), 1, preserve_end))
    else:
        end = F.lit("")
    masked = F.when(
        length <= preserve_start + preserve_end + 1, value
    ).otherwise(
        F.concat(
            start,
            hidden,
            end,
        )
    )
    return dataframe.withColumn(
        column_name, F.when(F.col(column_name).isNull(), F.lit(None)).otherwise(masked)
    )


def _bucket_column(dataframe, *, column_name, parameters):
    """Return rows with exact numeric values replaced by coarse labels."""
    from pyspark.sql import functions as F
    from pyspark.sql.types import NumericType

    if not isinstance(dataframe.schema[column_name].dataType, NumericType):
        raise ValueError("Sensitive Data bucket treatment requires a numeric column.")
    bins = parameters["bins"]
    labels = parameters["labels"]
    value = F.col(column_name)
    bucket = F.lit(labels[0])
    for boundary, label in zip(bins[1:], labels[1:]):
        bucket = F.when(value >= F.lit(boundary), F.lit(label)).otherwise(bucket)
    return dataframe.withColumn(
        column_name, F.when(value.isNull(), F.lit(None)).otherwise(bucket)
    )


def check_sensitive_data(
    dataframe,
    *,
    table_id: str,
    run_id: str = "",
    existing_mapping=None,
) -> dict:
    """Apply exact-contract Sensitive Data Guardrails before a governed write.

    Parameters
    ----------
    dataframe : pyspark.sql.DataFrame
        Prepared business rows whose governed sensitive columns must be treated.
    table_id : str
        Canonical identity used to resolve the applicable exact Data Contract version.
    run_id : str, optional
        Pipeline run identity recorded with Guardrail summary evidence.
    existing_mapping : pyspark.sql.DataFrame, optional
        Previously persisted mappings to reuse. Rows are scoped by ``table_id``
        and ``column_id``; established original-to-token assignments are preserved.

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
    never triggers a transformation. ``tokenize`` creates opaque UUID tokens
    that are consistent within the returned mapping/run and preserves nulls;
    supplying ``existing_mapping`` preserves established assignments. Cross-run
    stability otherwise requires the project to persist and supply the mapping.
    ``mask`` preserves configured leading and trailing characters and replaces
    each hidden character. ``bucket`` replaces numeric values with row-preserving
    labels: values below the first bin use the first label, each later bin is an
    inclusive lower boundary, and values at or above the final bin use the final
    label. Bucket does not aggregate rows. ``remove`` drops the governed column.
    Warn failures leave the input unchanged
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
    contract = resolve_pipeline_data_contract(
        config, env, table_id, spark_session=spark_session, context=context
    )
    if contract is None:
        return {
            "status": "skipped",
            "can_continue": True,
            "dataframe": dataframe,
            "support_mapping": None,
            "checks": [],
            "reason": "No Data Contract selected; Development only.",
        }
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
    for rule in rules:
        action = str(rule.get("action") or "Warn").strip().title()
        column_id = str(rule.get("column_id") or "").strip()
        column_name = str(rule.get("column_name") or "").strip()
        treatment = ""
        error = ""
        try:
            params = validate_sensitive_data_parameters(_parameters(rule))
            treatment = params["treatment"]
            if action not in {"Warn", "Block"}:
                raise ValueError("Sensitive Data action must be Warn or Block.")
            if not column_id or not column_name:
                raise ValueError("Sensitive Data Guardrail has an unresolved column identity or invalid scope.")
            if column_name not in transformed.columns:
                raise ValueError(f"Sensitive Data column {column_name!r} is missing from the DataFrame.")
            if treatment == "remove":
                transformed = transformed.drop(column_name)
            elif treatment == "tokenize":
                transformed, mapping = _tokenize_column(
                    transformed, column_name=column_name, column_id=column_id,
                    table_id=identity["table_id"], existing_mapping=existing_mapping,
                )
                mappings.append(mapping)
            elif treatment == "mask":
                transformed = _mask_column(
                    transformed, column_name=column_name, parameters=params
                )
            else:
                transformed = _bucket_column(
                    transformed, column_name=column_name, parameters=params
                )
        except ValueError as exc:
            error = str(exc)
        except Exception:
            error = f"{treatment.title() or 'Sensitive Data'} treatment could not be applied."
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
