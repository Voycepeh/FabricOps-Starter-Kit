"""Read-only validation of one exact immutable Data Contract version."""

from __future__ import annotations

from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.shared import get_store, resolve_fabric_context
from fabricops_kit.io import read_lakehouse_table, read_warehouse_table
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.pipeline.shared import (
    check_dq_runtime,
    contract_guardrail_rows,
    resolve_catalogue_table_identity,
    resolve_data_contract_version,
    schema_check_core,
    write_guardrail_result_row,
)


def _validate_data_contract(
    *,
    table_id: str,
    contract_id: str,
    contract_version: int,
    dataframe=None,
    spark_session=None,
    run_id: str = "",
    verbose: bool = True,
) -> dict[str, Any]:
    """Validate one exact frozen Data Contract against target data without writing it.

    Parameters
    ----------
    table_id : str
        Canonical Catalogue identity of the target table.
    contract_id : str
        Exact Data Contract lifecycle identity.
    contract_version : int
        Exact immutable version to validate. Draft versions are rejected.
    dataframe : pyspark.sql.DataFrame, optional
        Target data to evaluate. When omitted, the registered table is read.
    spark_session : object, optional
        Spark session to use. When omitted, FabricOps uses the supplied
        DataFrame session or resolves the active Microsoft Fabric session.
    run_id : str, optional
        Validation execution identity. The Fabric activity identity is used
        when omitted.
    verbose : bool, default=True
        Print one concise validation summary when ``True``.

    Returns
    -------
    dict
        Exact contract, table, environment, and run identities; aggregate rule
        counts; individual outcomes; and ``can_activate``. Failed-value
        DataFrames remain caller-visible and are never written to Metadata.

    Raises
    ------
    ValueError
        If the Catalogue target or exact immutable contract is missing,
        ambiguous, malformed, still draft, or belongs to another table.
    RuntimeError
        If a Spark session is unavailable.

    Notes
    -----
    This Engineering/data-plane operation only reads business data. It writes
    aggregate outcomes to ``METADATA_GUARDRAIL_RESULTS`` with
    ``execution_type='validate'`` and never calls ``pipeline_write``. Schema
    and Data Quality use the same evaluator cores as normal enforcement checks.
    Freshness, Source Drift, and Sensitive Data are reported as
    ``not_applicable`` because validation lacks the legitimate enforcement
    pipeline observation or transformation context they require. This
    applicability state is neither a pass nor an activation blocker.

    Examples
    --------
    >>> result = validate_data_contract(
    ...     table_id="lakehouse||silver||dbo||orders",
    ...     contract_id="4f41a6a0-79ce-4d56-9872-b6775de6bb55",
    ...     contract_version=2,
    ... )
    >>> result["can_activate"]
    True

    See Also
    --------
    check_schema, check_dq

    """
    config, env, context = resolve_fabric_context()
    spark = spark_session or getattr(dataframe, "sparkSession", None) or get_spark_session()
    identity = resolve_catalogue_table_identity(
        config, env, table_id, spark_session=spark, context=context,
    )
    contract = resolve_data_contract_version(
        config,
        env,
        table_id,
        str(contract_id or "").strip(),
        contract_version,
        spark_session=spark,
        context=context,
    )
    rules = contract_guardrail_rows(contract, environment_name=env, table_id=table_id)
    rules_df = spark.createDataFrame(rules) if rules else []
    effective_run_id = str(run_id or "").strip() or str(
        build_runtime_audit_fields(config=config, env=env, runtime_context=context)["_activity_id"]
    )

    if dataframe is None:
        store = get_store(config, env, identity["store"])
        if identity["store_type"] == "lakehouse":
            dataframe = read_lakehouse_table(
                identity["table_name"], store=identity["store"], schema=identity["schema"],
                spark_session=spark, context=context,
            )
        else:
            dataframe = read_warehouse_table(
                identity["schema"] or getattr(store, "schema", None), identity["table_name"],
                store=identity["store"], spark_session=spark, context=context,
            )

    outcomes: list[dict[str, Any]] = []
    failed_values = None
    schema_rules = [rule for rule in rules if str(rule.get("guardrail_type") or "").lower() == "schema"]
    if schema_rules:
        schema_result = schema_check_core(
            dataframe,
            rules_df=rules_df,
            environment_name=env,
            table_id=table_id,
        )
        schema_result.update(
            table_id=table_id,
            contract_id=contract["contract_id"],
            contract_version=int(contract["contract_version"]),
        )
        write_guardrail_result_row(
            spark_session=spark, config=config, env=env, run_id=effective_run_id,
            dataset_name="", table_name=identity["table_name"],
            store_type=identity["store_type"], layer=identity["store"],
            schema_name=identity["schema"], guardrail_type="schema",
            rule_type=str(schema_result.get("rule_type") or ""), result=schema_result,
            table_id=table_id, contract_id=contract["contract_id"],
            contract_version=int(contract["contract_version"]), execution_type="validate",
        )
        outcomes.append(schema_result)

    dq_rules = [rule for rule in rules if str(rule.get("guardrail_type") or "").lower() == "data_quality"]
    if dq_rules:
        dq_result = check_dq_runtime(
            dataframe, config, env, identity["table_name"], table_id=table_id,
            store=identity["store"], store_type=identity["store_type"],
            schema_name=identity["schema"], run_id=effective_run_id, context=context,
            rules_df=spark.createDataFrame(dq_rules), contract_id=contract["contract_id"],
            contract_version=int(contract["contract_version"]), execution_type="validate",
        )
        failed_values = dq_result.get("failed_values")
        outcomes.extend(dq_result.get("checks") or [])

    for rule in rules:
        guardrail_type = str(rule.get("guardrail_type") or "").lower()
        if guardrail_type in {"schema", "data_quality"}:
            continue
        outcome = {
            "guardrail_rule_id": str(rule.get("guardrail_rule_id") or ""),
            "guardrail_version": int(rule.get("guardrail_version") or 1),
            "table_id": table_id,
            "contract_id": contract["contract_id"],
            "contract_version": int(contract["contract_version"]),
            "guardrail_type": guardrail_type,
            "status": "not_applicable",
            "can_continue": True,
            "validation_applicability": "enforcement_only",
            "severity": "warning" if str(rule.get("action") or "").casefold() == "warn" else "blocking",
            "reason_code": "enforcement_context_required",
            "reason": f"{guardrail_type} requires enforcement pipeline context.",
        }
        write_guardrail_result_row(
            spark_session=spark, config=config, env=env, run_id=effective_run_id,
            dataset_name="", table_name=identity["table_name"],
            store_type=identity["store_type"], layer=identity["store"],
            schema_name=identity["schema"], guardrail_type=guardrail_type,
            rule_type=str(rule.get("rule_type") or ""), result=outcome,
            table_id=table_id, contract_id=contract["contract_id"],
            contract_version=int(contract["contract_version"]), execution_type="validate",
        )
        outcomes.append(outcome)

    statuses = [str(item.get("status") or "not_applicable").lower() for item in outcomes]
    passed = sum(status in {"pass", "passed"} for status in statuses)
    warnings = sum(status in {"warn", "warning"} for status in statuses)
    blocked = sum(status in {"fail", "failed", "block", "blocked"} for status in statuses)
    not_applicable = sum(status == "not_applicable" for status in statuses)
    result = {
        "table_id": table_id,
        "contract_id": contract["contract_id"],
        "contract_version": int(contract["contract_version"]),
        "environment_name": env,
        "execution_type": "validate",
        "run_id": effective_run_id,
        "rule_count": len(outcomes),
        "passed": passed,
        "warnings": warnings,
        "blocked": blocked,
        "not_applicable": not_applicable,
        "can_activate": bool(outcomes) and blocked == 0,
        "status": "passed" if outcomes and blocked == 0 else "failed",
        "outcomes": outcomes,
        "failed_values": failed_values,
    }
    if verbose:
        print("FabricOps Data Contract Validation")
        print(f"  Table {table_id}")
        print(f"  Contract {contract['contract_id']} v{contract['contract_version']} | Environment {env}")
        print(
            f"  Result {'PASS' if result['can_activate'] else 'BLOCK'} | "
            f"passed={passed} warnings={warnings} blocked={blocked} not_applicable={not_applicable}"
        )
        print("  Business data was read only; aggregate evidence was written to METADATA_GUARDRAIL_RESULTS.")
    return result
