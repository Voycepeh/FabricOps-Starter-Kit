"""Public schema guardrail check."""

from fabricops_kit.config.shared import get_store, resolve_fabric_context
from fabricops_kit.io.shared import (
    get_spark_session,
    read_lakehouse_table_core,
    read_warehouse_query_core,
    resolve_lakehouse_table_location,
    resolve_warehouse_table_location,
)
from fabricops_kit.pipeline.shared import (
    load_table_guardrail_rules,
    resolve_catalogue_table_identity,
    schema_check_core,
    select_table_guardrail_rule,
)
from fabricops_kit.pipeline.shared import stop_if_failed, write_guardrail_result_row


def check_schema(
    table_id: str,
    *,
    dataframe=None,
) -> dict:
    """Check a persisted or supplied schema against configured schema intent.

    Parameters
    ----------
    table_id : str
        Canonical identity of an active registered Catalogue table.
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

    Notes
    -----
    Production resolves the physical table through the Catalogue and uses its
    active frozen Data Contract. Development uses mutable authoring metadata.

    Examples
    --------
    >>> result = check_schema(table_id="lakehouse||source||dbo||orders")
    >>> result["can_continue"]
    True

    """
    config, env, context = resolve_fabric_context()
    spark = get_spark_session()
    identity = resolve_catalogue_table_identity(
        config, env, table_id, spark_session=spark, context=context,
    )
    target = identity["target"]
    schema = identity["schema"]
    table_name = identity["table_name"]
    store = get_store(config, env, target)
    store_type = str(store.kind).lower()
    if store_type != identity["store_type"]:
        raise ValueError(
            f"Catalogue table_id {table_id!r} declares store_type {identity['store_type']!r}, "
            f"but configured target {target!r} resolves to {store_type!r}."
        )
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
    rules_df = load_table_guardrail_rules(
        config, env, spark_session=spark, table_id=table_id, context=context,
    )
    selected_rule = select_table_guardrail_rule(
        rules_df, guardrail_type="schema", table_id=table_id,
        environment_name=env,
    )
    if selected_rule is None:
        raise ValueError(f"No active approved schema rule exists for {table_id!r}.")
    result = schema_check_core(
        dataframe, rules_df=rules_df, table_name=resolved_table,
        environment_name=env, table_id=table_id,
    )
    if selected_rule is not None:
        result.setdefault("guardrail_rule_id", str(selected_rule.get("guardrail_rule_id") or ""))
        result.setdefault("guardrail_version", int(selected_rule.get("guardrail_version") or 1))
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
