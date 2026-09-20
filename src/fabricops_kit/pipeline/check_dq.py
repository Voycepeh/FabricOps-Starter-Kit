"""Public governed data-quality runtime check."""

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.get_spark_session import get_spark_session
from fabricops_kit.pipeline.shared import (
    check_dq_runtime,
    resolve_catalogue_table_identity,
    resolve_pipeline_data_contract,
    print_guardrail_result,
)


def check_dq(
    dataframe,
    *,
    table_id: str,
    dataset_name: str = "",
    run_id: str = "",
    row_identity_columns: list[str] | None = None,
    enabled: bool = True,
    raise_on_failure: bool = False,
    spark_session=None,
    verbose: bool = True,
) -> dict:
    """Evaluate active governed DQ rules and persist runtime evidence.

    Parameters
    ----------
    dataframe : pyspark.sql.DataFrame
        Source or target rows to evaluate.
    table_id : str
        Canonical identity of an active registered Catalogue table.
    dataset_name : str, optional
        Governed dataset identity used to further scope rules when supplied.
    run_id : str, optional
        Pipeline run identity persisted with summary evidence. When omitted,
        the current Fabric activity identity is used.
    row_identity_columns : list[str], optional
        Business-key columns used for row identity. When omitted, an existing
        row UUID/ID is preferred and a deterministic content hash is the
        fallback.
    enabled : bool, default=True
        Explicitly disable this check when ``False``. Normally omit this value;
        FabricOps enforces the resolved pipeline Data Contract automatically.
    raise_on_failure : bool, default=False
        Raise ``RuntimeError`` when a blocking DQ result cannot continue.
    spark_session : object, optional
        Spark session to use. When omitted, FabricOps uses the supplied
        DataFrame session or resolves the active session.
    verbose : bool, default=True
        Print the concise normalized check outcome when ``True``.

    Returns
    -------
    dict
        Overall ``status`` and ``can_continue`` decision, concise ``summary``,
        one check per evaluated rule, the original DataFrame with DQ status columns,
        and a normalized ``failed_values`` DataFrame. Failure detail has one
        row per failed rule, involved column, and source record, with a shared
        ``failure_event_id``, row and rule identities, action, column role,
        string ``raw_value``, original ``raw_value_type``, and reason. It does
        not copy unrelated source columns. Evaluated rules also include the
        resolved ``run_id``.

    Raises
    ------
    ValueError
        If configured identity columns are absent or governed rule metadata is
        invalid.
    RuntimeError
        If Spark is unavailable in the Microsoft Fabric runtime, or
        ``raise_on_failure=True`` and a blocking DQ result cannot continue.

    Notes
    -----
    Production evaluates frozen DQ rules from the active Data Contract.
    Development uses an explicitly selected immutable version, or safely skips
    when no contract is selected.
    Every evaluated rule/run is appended to ``METADATA_GUARDRAIL_RESULTS``.
    Failed values are returned to the caller and are never persisted automatically.
    Block failures prevent continuation while Warn failures do not.

    Examples
    --------
    >>> result = check_dq(source_df, table_id="lakehouse||source||dbo||orders", row_identity_columns=["order_id"])
    >>> result["can_continue"]
    True
    >>> result["failed_values"].select("rule_id", "column_name", "raw_value").show()

    See Also
    --------
    check_schema, check_freshness, check_source_drift

    """
    if not enabled:
        result = {"status": "skipped", "can_continue": True, "checks": []}
        print_guardrail_result("Data Quality", result, verbose=verbose, table_id=table_id)
        if verbose:
            print("  Evaluation skipped by caller; no rules evaluated or evidence written.")
        return result
    config, env, context = resolve_fabric_context()
    if spark_session is None:
        spark_session = getattr(dataframe, "sparkSession", None)
    if spark_session is None:
        spark_session = get_spark_session()
    contract = resolve_pipeline_data_contract(
        config,
        env,
        table_id,
        spark_session=spark_session,
        context=context,
    )
    if contract is None:
        result = {
            "status": "skipped",
            "can_continue": True,
            "checks": [],
            "reason": "No Data Contract selected; Development only.",
            "table_id": table_id,
            "environment_name": env,
        }
        print_guardrail_result("Data Quality", result, verbose=verbose, table_id=table_id)
        if verbose:
            print(f"  Reason {result['reason']}")
        return result
    identity = resolve_catalogue_table_identity(
        config,
        env,
        table_id,
        spark_session=spark_session,
        context=context,
    )
    result = check_dq_runtime(
        dataframe,
        config,
        env,
        identity["table_name"],
        table_id=identity["table_id"],
        store=identity["store"],
        store_type=identity["store_type"],
        schema_name=identity["schema"],
        dataset_name=dataset_name,
        run_id=run_id,
        row_identity_columns=row_identity_columns,
        context=context,
    )
    print_guardrail_result("Data Quality", result, verbose=verbose, table_id=table_id)
    if verbose:
        checks = list(result.get("checks") or [])
        failed = [check for check in checks if str(check.get("status") or "").lower() not in {"passed", "pass"}]
        print(f"  Contract selected; evaluated {len(checks)} active DQ rule(s).")
        print(f"  Rule outcomes {len(checks) - len(failed)} passed, {len(failed)} warning/failed.")
        print("  Evidence appended to METADATA_GUARDRAIL_RESULTS for each evaluated rule.")
        print("  Failed values stay caller-visible only and are not persisted automatically.")
    if raise_on_failure and not result["can_continue"]:
        raise RuntimeError(f"A blocking DQ Guardrail failed for table_id {identity['table_id']!r}.")
    return result
