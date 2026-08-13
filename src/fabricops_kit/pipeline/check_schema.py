"""Public schema guardrail check."""

from fabricops_kit.pipeline.guardrails_shared import schema_check_core


def check_schema(
    dataframe,
    expected_schema: dict[str, str] | None = None,
    *,
    preset: str = "strict",
    rules_df=None,
    dataset_name: str = "",
    table_name: str = "",
    environment_name: str = "",
    metadata_table_key: str = "",
) -> dict:
    """Check a table's observed schema against configured schema intent.

    Parameters
    ----------
    dataframe : Any
        Spark, pandas, or dataframe-like object with schema metadata.
    expected_schema : dict[str, str], optional
        Expected column-to-datatype mapping for a direct check.
    preset : {"strict", "allow_new_columns", "monitor_only"}, default="strict"
        Direct schema comparison behavior.
    rules_df : DataFrame or iterable of mappings, optional
        Approved guardrail rules. When supplied, the applicable schema rule is
        selected using the table context instead of ``expected_schema``.
    dataset_name, table_name, environment_name, metadata_table_key : str, optional
        Table identity used to select an approved rule.

    Returns
    -------
    dict
        Structured guardrail status, continuation decision, checks, and schema
        differences.

    Raises
    ------
    ValueError
        If the preset is invalid or neither rule data nor an expected schema is
        supplied.

    Examples
    --------
    >>> result = check_schema(df, {"order_id": "bigint"})
    >>> result["can_continue"]
    True

    """
    if rules_df is not None:
        return schema_check_core(
            dataframe,
            rules_df=rules_df,
            dataset_name=dataset_name,
            table_name=table_name,
            environment_name=environment_name,
            metadata_table_key=metadata_table_key,
        )
    if expected_schema is None:
        raise ValueError("expected_schema is required when rules_df is not supplied")
    return schema_check_core(dataframe, expected_schema, preset=preset)
