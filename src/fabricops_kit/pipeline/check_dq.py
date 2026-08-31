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
) -> dict:
    """Evaluate active governed DQ rules and persist runtime evidence.

    Parameters
    ----------
    dataframe : pyspark.sql.DataFrame
        Source or target rows to evaluate without filtering or copying complete
        rows into metadata.
    table_id : str
        Canonical identity of an active registered Catalogue table.
    dataset_name : str, optional
        Governed dataset identity used to further scope rules when supplied.
    run_id : str, optional
        Pipeline run identity persisted with failed-row evidence. When omitted,
        the current Fabric activity identity is used.
    row_identity_columns : list[str], optional
        Business-key columns used for row identity. When omitted, an existing
        row UUID/ID is preferred and a deterministic content hash is the
        fallback.

    Returns
    -------
    dict
        Overall ``status`` and ``can_continue`` decision, concise ``summary``,
        one check per evaluated rule, and the original DataFrame with DQ status
        columns. Evaluated rules also include the resolved ``run_id``.

    Raises
    ------
    ValueError
        If configured identity columns are absent or governed rule metadata is
        invalid.
    RuntimeError
        If Spark is unavailable in the Microsoft Fabric runtime.

    Notes
    -----
    Production resolves the physical table through the Catalogue and evaluates
    frozen DQ rules from its active Data Contract. Development evaluates current
    active approved authoring rules in ``METADATA_GUARDRAIL``.
    Every evaluated rule/run is appended to ``METADATA_GUARDRAIL_RESULTS``;
    only failed row/rule pairs are appended to
    ``METADATA_GUARDRAIL_ROW_RESULTS``. Error failures block continuation while
    warning failures do not.

    Examples
    --------
    >>> result = check_dq(source_df, table_id="lakehouse||source||dbo||orders", row_identity_columns=["order_id"])
    >>> result["can_continue"]
    True

    See Also
    --------
    check_schema, check_freshness, check_changes

    """
    config, env, context = resolve_fabric_context()
    spark_session = getattr(dataframe, "sparkSession", None)
    identity = resolve_catalogue_table_identity(
        config, env, table_id, spark_session=spark_session, context=context,
    )
    return check_dq_runtime(
        dataframe, config, env, identity["table_name"], table_id=identity["table_id"],
        target=identity["target"], store_type=identity["store_type"], schema_name=identity["schema"],
        dataset_name=dataset_name, run_id=run_id,
        row_identity_columns=row_identity_columns, context=context,
    )
