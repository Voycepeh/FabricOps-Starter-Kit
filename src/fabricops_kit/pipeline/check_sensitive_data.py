"""Public preparation-first Sensitive Data Guardrail enforcement."""

from __future__ import annotations

from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.pipeline.shared import (
    check_sensitive_data_rules,
    load_table_guardrail_rules,
    resolve_pipeline_data_contract,
    resolve_catalogue_table_identity,
    write_guardrail_result_row,
    print_guardrail_result,
)


def _rows(value) -> list[dict[str, Any]]:
    source = value.collect() if hasattr(value, "collect") else value
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in source or []]


def check_sensitive_data(
    dataframe,
    *,
    table_id: str,
    run_id: str = "",
    existing_mapping=None,
    enabled: bool = True,
    raise_on_failure: bool = False,
    spark_session=None,
    verbose: bool = True,
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
    enabled : bool, default=True
        Explicitly skip the check and return the supplied DataFrame when ``False``.
    raise_on_failure : bool, default=False
        Raise ``RuntimeError`` when a blocking treatment cannot continue.
    spark_session : object, optional
        Spark session to use. When omitted, FabricOps uses the supplied
        DataFrame session or resolves the active session.
    verbose : bool, default=True
        Print the concise normalized check outcome when ``True``.

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
    >>> result = check_sensitive_data(
    ...     transformed_df,
    ...     table_id=TARGET_TABLE_ID,
    ...     raise_on_failure=True,
    ... )
    >>> write_result = pipeline_write(
    ...     result["dataframe"],
    ...     table_id=TARGET_TABLE_ID,
    ... )

    See Also
    --------
    pipeline_write, write_lakehouse_table, write_warehouse_table

    """
    if not enabled:
        result = {
            "status": "skipped",
            "can_continue": True,
            "dataframe": dataframe,
            "support_mapping": None,
            "checks": [],
        }
        print_guardrail_result("Sensitive Data", result, verbose=verbose, table_id=table_id)
        if verbose:
            print("  Evaluation skipped by caller; no treatment applied or evidence written.")
        return result
    if spark_session is None:
        spark_session = getattr(dataframe, "sparkSession", None)
    if spark_session is None:
        spark_session = get_spark_session()
    if not hasattr(spark_session, "createDataFrame"):
        raise RuntimeError("check_sensitive_data requires a Spark DataFrame in the active Microsoft Fabric runtime.")
    config, env, context = resolve_fabric_context()
    contract = resolve_pipeline_data_contract(config, env, table_id, spark_session=spark_session, context=context)
    if contract is None:
        result = {
            "status": "skipped",
            "can_continue": True,
            "dataframe": dataframe,
            "support_mapping": None,
            "checks": [],
            "reason": "No Data Contract selected; Development only.",
        }
        print_guardrail_result(
            "Sensitive Data",
            result,
            verbose=verbose,
            table_id=table_id,
            config=config,
            env=env,
            spark_session=spark_session,
            context=context,
        )
        if verbose:
            print(f"  Reason {result['reason']}")
        return result
    identity = resolve_catalogue_table_identity(config, env, table_id, spark_session=spark_session, context=context)
    rules = [
        row
        for row in _rows(
            load_table_guardrail_rules(
            config, env, spark_session=spark_session, table_id=identity["table_id"], context=context
            )
        )
        if str(row.get("guardrail_type") or "").strip().lower() == "sensitive_data"
        and row.get("is_active", True) is not False
    ]
    result = check_sensitive_data_rules(
        dataframe,
        rules=rules,
        identity=identity,
        config=config,
        env=env,
        spark_session=spark_session,
        run_id=run_id,
        existing_mapping=existing_mapping,
        execution_type="enforce",
    )
    print_guardrail_result(
        "Sensitive Data",
        result,
        verbose=verbose,
        table_id=table_id,
        config=config,
        env=env,
        spark_session=spark_session,
        context=context,
    )
    if verbose:
        checks = result["checks"]
        treatments = [str(check.get("treatment") or "unknown") for check in checks]
        print(f"  Contract selected; evaluated {len(checks)} active Sensitive Data rule(s).")
        print(f"  Treatments applied/evaluated: {', '.join(treatments) if treatments else 'none'}.")
        print("  Evidence appended to METADATA_GUARDRAIL_RESULTS without raw sensitive values.")
        print(
            "  Token support mapping returned to caller and not persisted automatically."
            if result["support_mapping"] is not None
            else "  No token support mapping produced."
        )
    if raise_on_failure and not result["can_continue"]:
        raise RuntimeError(f"A blocking Sensitive Data Guardrail failed for table_id {table_id!r}.")
    return result
