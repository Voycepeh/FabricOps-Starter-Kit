"""Public schema guardrail check."""

from fabricops_kit.config.shared import get_store, resolve_fabric_context
from fabricops_kit.io.shared import (
    get_spark_session,
    read_lakehouse_table_core,
    read_warehouse_query_core,
    resolve_lakehouse_table_location,
    resolve_warehouse_table_location,
)
from fabricops_kit.pipeline.guardrails_shared import schema_check_core


def check_schema(
    dataframe=None,
    expected_schema: dict[str, str] | None = None,
    *,
    preset: str = "strict",
    rules_df=None,
    dataset_name: str = "",
    table_name: str = "",
    environment_name: str = "",
    metadata_table_key: str = "",
    target: str = "source",
    schema: str | None = None,
) -> dict:
    """Check a table's observed schema against configured schema intent.

    Parameters
    ----------
    dataframe : Any
        Spark, pandas, or dataframe-like object with schema metadata. Omit it
        and pass ``target``, ``schema``, and ``table_name`` to inspect a
        configured physical table without reading its business rows.
    expected_schema : dict[str, str], optional
        Expected column-to-datatype mapping for a direct check.
    preset : {"strict", "allow_new_columns", "monitor_only"}, default="strict"
        Direct schema comparison behavior.
    rules_df : DataFrame or iterable of mappings, optional
        Approved guardrail rules. When supplied, the applicable schema rule is
        selected using the table context instead of ``expected_schema``.
    dataset_name, table_name, environment_name, metadata_table_key : str, optional
        Table identity used to select an approved rule.
    target : str, default="source"
        Logical FabricOps target used when ``dataframe`` is omitted.
    schema : str, optional
        Physical schema used when ``dataframe`` is omitted.

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
    if dataframe is None:
        if not table_name:
            raise ValueError("table_name is required when dataframe is omitted")
        config, env, context = resolve_fabric_context()
        store = get_store(config, env, target)
        spark = get_spark_session()
        if str(store.kind).lower() == "warehouse":
            schema_name, resolved_table, _ = resolve_warehouse_table_location(
                store, schema or getattr(store, "schema", None), table_name,
            )
            dataframe = read_warehouse_query_core(
                f"SELECT TOP (0) * FROM [{schema_name}].[{resolved_table}]",
                target=target, spark_session=spark, context=context,
            )
        elif str(store.kind).lower() == "lakehouse":
            resolved_table, schema_name, _ = resolve_lakehouse_table_location(store, table_name, schema)
            dataframe = read_lakehouse_table_core(
                resolved_table, target=target, schema=schema_name,
                spark_session=spark, context=context,
            ).limit(0)
        else:
            raise ValueError(f"Target {target!r} must resolve to a Lakehouse or Warehouse.")
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
