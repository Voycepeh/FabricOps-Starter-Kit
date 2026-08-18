"""Public schema guardrail check."""

from fabricops_kit.config.shared import build_metadata_table_key, get_store, resolve_fabric_context
from fabricops_kit.io.shared import (
    get_spark_session,
    read_lakehouse_table_core,
    read_warehouse_query_core,
    resolve_lakehouse_table_location,
    resolve_warehouse_table_location,
)
from fabricops_kit.pipeline.guardrail_metadata import (
    load_table_guardrail_rules,
    schema_check_core,
    select_table_guardrail_rule,
    write_guardrail_result_row,
)
from fabricops_kit.pipeline.guardrails_shared import stop_if_failed


def check_schema(
    table_name: str,
    *,
    target: str = "source",
    schema: str | None = None,
    dataframe=None,
) -> dict:
    """Check a persisted or supplied schema against configured schema intent.

    Parameters
    ----------
    table_name : str
        Physical table name within the configured target.
    target : str, default="source"
        Logical FabricOps target containing the configured physical table.
    schema : str, optional
        Physical schema containing the configured table.
    dataframe : DataFrame, optional
        Incoming DataFrame whose schema should be checked. When omitted, the
        schema of the configured physical table is checked.

    Returns
    -------
    dict
        Structured guardrail status, continuation decision, checks, and schema
        differences. Governed configured-table checks append the outcome to
        ``METADATA_GUARDRAIL_RESULTS``.

    Raises
    ------
    ValueError
        If the target is unsupported or no active approved Schema guardrail
        exists for the resolved table.
    SchemaDriftError
        If an active blocking schema guardrail rejects the checked schema.

    Examples
    --------
    >>> result = check_schema("orders", target="source", schema="dbo")
    >>> result["can_continue"]
    True

    """
    config, env, context = resolve_fabric_context()
    store = get_store(config, env, target)
    spark = get_spark_session()
    store_type = str(store.kind).lower()
    if store_type == "warehouse":
        schema_name, resolved_table, _ = resolve_warehouse_table_location(
            store, schema or getattr(store, "schema", None), table_name,
        )
        if dataframe is None:
            dataframe = read_warehouse_query_core(
                f"SELECT TOP (0) * FROM [{schema_name}].[{resolved_table}]",
                target=target, spark_session=spark, context=context,
            )
    elif store_type == "lakehouse":
        resolved_table, schema_name, _ = resolve_lakehouse_table_location(store, table_name, schema)
        if dataframe is None:
            dataframe = read_lakehouse_table_core(
                resolved_table, target=target, schema=schema_name,
                spark_session=spark, context=context,
            ).limit(0)
    else:
        raise ValueError(f"Target {target!r} must resolve to a Lakehouse or Warehouse.")
    metadata_table_key = build_metadata_table_key(store_type, target, schema_name, resolved_table)
    rules_df = load_table_guardrail_rules(config, env, spark_session=spark)
    if select_table_guardrail_rule(
        rules_df, guardrail_type="schema", metadata_table_key=metadata_table_key,
        environment_name=env,
    ) is None:
        raise ValueError(f"No active approved schema rule exists for {metadata_table_key!r}.")
    result = schema_check_core(
        dataframe, rules_df=rules_df, table_name=resolved_table,
        environment_name=env, metadata_table_key=metadata_table_key,
    )
    if result.get("guardrail_rule_id"):
        result["expected"] = {"schema_rule": result.get("rule_type")}
        result["actual"] = {
            name: result.get(name, [])
            for name in ("missing_columns", "unexpected_columns", "datatype_mismatches")
        }
        write_guardrail_result_row(
            spark_session=spark, config=config, env=env, run_id="", dataset_name="",
            table_name=resolved_table, store_type=store_type, layer=target,
            schema_name=schema_name, guardrail_type="schema",
            rule_type=str(result.get("rule_type")), result=result,
        )
    stop_if_failed(result)
    return result
