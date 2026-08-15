"""Public governed data-quality runtime check."""

from fabricops_kit.config.shared import get_store, resolve_fabric_context
from fabricops_kit.pipeline.guardrails_shared import check_dq_runtime


def check_dq(
    dataframe,
    table_name: str,
    *,
    target: str = "source",
    schema: str | None = None,
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
    table_name : str
        Physical table name used to select current active DQ rules.
    target : str, default="source"
        Configured FabricOps store target that owns the table.
    schema : str, optional
        Physical schema containing the table.
    dataset_name : str, optional
        Governed dataset identity used to further scope rules when supplied.
    run_id : str, optional
        Pipeline run identity persisted with failed-row evidence.
    row_identity_columns : list[str], optional
        Business-key columns used for row identity. When omitted, an existing
        row UUID/ID is preferred and a deterministic content hash is the
        fallback.

    Returns
    -------
    dict
        Overall status and continuation decision, one check per evaluated rule,
        aggregate counts, and the original DataFrame with DQ status columns.

    Raises
    ------
    ValueError
        If configured identity columns are absent or governed rule metadata is
        invalid.
    RuntimeError
        If Spark is unavailable in the Microsoft Fabric runtime.

    Notes
    -----
    Only current active approved rules in ``METADATA_GUARDRAIL`` are evaluated.
    Every evaluated rule/run is appended to ``METADATA_GUARDRAIL_RESULTS``;
    only failed row/rule pairs are appended to
    ``METADATA_GUARDRAIL_ROW_RESULTS``. Error failures block continuation while
    warning failures do not.

    Examples
    --------
    >>> result = check_dq(source_df, "orders", row_identity_columns=["order_id"])
    >>> result["can_continue"]
    True

    See Also
    --------
    check_schema, check_freshness, check_changes

    """
    config, env, _context = resolve_fabric_context()
    store = get_store(config, env, target)
    return check_dq_runtime(
        dataframe, config, env, table_name, target=target,
        store_type=str(store.kind).lower(), schema_name=schema,
        dataset_name=dataset_name, run_id=run_id,
        row_identity_columns=row_identity_columns,
    )
