"""Public Direct PII guardrail check."""

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
    select_table_guardrail_rule,
    stop_if_failed,
    write_guardrail_result_row,
)
from fabricops_kit.security.shared import (
    load_token_vault_rows,
    pii_guardrail_core,
    resolve_direct_pii_columns,
)


def check_pii_guardrail(table_id: str, *, dataframe=None) -> dict:
    """Check that governed Direct PII is absent or represented by approved tokens.

    Parameters
    ----------
    table_id : str
        Canonical identity of an active registered Catalogue table.
    dataframe : DataFrame, optional
        Incoming DataFrame to check. When omitted, FabricOps reads the
        configured physical table without silently detokenising it.

    Returns
    -------
    dict
        Guardrail status, continuation decision, and classified, present, and
        untreated column names. When an active PII Guardrail rule exists, its
        outcome is appended to ``METADATA_GUARDRAIL_RESULTS``.

    Raises
    ------
    ValueError
        If the registered table or configured store is unsupported.
    SchemaDriftError
        If a blocking PII Guardrail rejects untreated Direct PII.

    Notes
    -----
    Development uses mutable ``METADATA_ENRICHMENT`` classification. Production
    uses the active frozen Data Contract enrichment. Approved tokens are checked
    against the separately configured, table-isolated ``pii_token_vault`` target;
    reversible mappings never enter ordinary governance metadata.

    Examples
    --------
    >>> result = check_pii_guardrail("lakehouse:source:dbo:customers")
    >>> result["can_continue"]
    True

    See Also
    --------
    check_schema, write_pipeline_prep

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
                f"SELECT * FROM [{schema_name}].[{resolved_table}]",
                target=target, spark_session=spark, context=context,
            )
    elif store_type == "lakehouse":
        resolved_table, schema_name, _ = resolve_lakehouse_table_location(store, table_name, schema)
        if dataframe is None:
            dataframe = read_lakehouse_table_core(
                resolved_table, target=target, schema=schema_name,
                spark_session=spark, context=context,
            )
    else:
        raise ValueError(f"Target {target!r} must resolve to a Lakehouse or Warehouse.")

    direct_columns = resolve_direct_pii_columns(
        config, env, identity["table_id"], spark_session=spark, context=context,
    )
    selected_rule = None
    if direct_columns:
        rules_df = load_table_guardrail_rules(
            config, env, spark_session=spark, table_id=identity["table_id"], context=context,
        )
        selected_rule = select_table_guardrail_rule(
            rules_df,
            guardrail_type="pii",
            table_id=identity["table_id"],
            environment_name=env,
        )
    severity = str((selected_rule or {}).get("severity") or "blocking")
    vault_rows = (
        load_token_vault_rows(
            config, env, identity["table_id"], spark_session=spark, context=context,
        )
        if direct_columns else []
    )
    result = pii_guardrail_core(
        dataframe,
        direct_pii_columns=direct_columns,
        vault_rows=vault_rows,
        severity=severity,
    )
    if selected_rule is not None:
        result["guardrail_rule_id"] = str(selected_rule.get("guardrail_rule_id") or "")
        result["guardrail_version"] = int(
            selected_rule.get("guardrail_version")
            or selected_rule.get("configuration_version")
            or 1
        )
        result["expected"] = {"direct_pii": "absent_or_approved_token"}
        result["actual"] = {"untreated_columns": result["untreated_columns"]}
        write_guardrail_result_row(
            spark_session=spark,
            config=config,
            env=env,
            run_id="",
            dataset_name="",
            table_name=resolved_table,
            store_type=store_type,
            layer=target,
            schema_name=schema_name,
            guardrail_type="pii",
            rule_type=str(selected_rule.get("rule_type") or "direct_pii_tokenised"),
            result=result,
        )
    stop_if_failed(result)
    return result
