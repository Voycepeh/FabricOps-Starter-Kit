"""Public governed data-quality runtime check."""

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.pipeline.shared import check_dq_runtime, resolve_catalogue_table_identity


def check_dq(
    dataframe,
    *,
    table_id: str,
    dataset_name: str = "",
    run_id: str = "",
    row_identity_columns: list[str] | None = None,
    enabled: bool = True,
    raise_on_failure: bool = False,
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
        Whether Data Contract validation is enabled for this notebook run.
        ``False`` returns a continuation-safe skipped result without metadata IO.
    raise_on_failure : bool, default=False
        Raise ``RuntimeError`` when a blocking DQ result cannot continue.

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
    Production resolves the physical table through the Catalogue and evaluates
    frozen DQ rules from its active Data Contract. Development evaluates current
    active approved authoring rules in ``METADATA_GUARDRAIL``.
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
    check_schema, check_freshness, check_changes

    """
    if not enabled:
        return {"status": "skipped", "can_continue": True, "checks": []}
    config, env, context = resolve_fabric_context()
    spark_session = getattr(dataframe, "sparkSession", None)
    identity = resolve_catalogue_table_identity(
        config, env, table_id, spark_session=spark_session, context=context,
    )
    result = check_dq_runtime(
        dataframe, config, env, identity["table_name"], table_id=identity["table_id"],
        target=identity["target"], store_type=identity["store_type"], schema_name=identity["schema"],
        dataset_name=dataset_name, run_id=run_id,
        row_identity_columns=row_identity_columns, context=context,
    )
    if raise_on_failure and not result["can_continue"]:
        raise RuntimeError(f"A blocking DQ Guardrail failed for table_id {identity['table_id']!r}.")
    return result
