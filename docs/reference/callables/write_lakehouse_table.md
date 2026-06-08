# write_lakehouse_table

**Module:** `fabric_input_output`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use when publishing a Spark DataFrame to a configured Fabric lakehouse table.

## When not to use this

Do not use for metadata evidence tables unless the helper explicitly routes metadata, and do not use for warehouse tables.

## Quick example

write_lakehouse_table(curated_df, CONFIG, env="Sandbox", target="Unified", table="orders_curated", mode="overwrite")

## Signature

```python
def write_lakehouse_table(df, config, env, target, table, mode='append', partition_by=None, repartition_by=None, overwrite_schema=True)
```

## Parameters

df, config, env, target, table, optional schema, mode, and partitioning/write options.

## Returns

None; the DataFrame is written to the configured lakehouse table.

## Raises

Raises configuration, Spark, or write errors when the target cannot be resolved or the write fails.

## Side effects

Writes data to a Fabric lakehouse table using the selected write mode.

## FabricOps context

Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.

## AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** df, config, env, target, table, optional schema, mode, and partitioning/write options.
- **output:** None; the DataFrame is written to the configured lakehouse table.
- **side_effects:** Writes data to a Fabric lakehouse table using the selected write mode.
- **failure_modes:** Raises configuration, Spark, or write errors when the target cannot be resolved or the write fails.
- **verification:** Verify upstream guardrails passed, confirm target routing from CONFIG, and check the intended write mode before generating code that calls this helper.

## Related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source reference: <a href="../../api/modules/fabric_input_output/#write_lakehouse_table">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.write_lakehouse_table`
- Short name: `write_lakehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Inbound references count: 7
- Outbound references count: 1

## Inbound references
- <a href="../internal/data_agreement__ensure_metadata_tables/"><code>fabricops_kit.data_agreement._ensure_metadata_tables</code></a>
- <a href="../internal/data_agreement__write_row/"><code>fabricops_kit.data_agreement._write_row</code></a>
- <a href="../internal/governance_review__setup_governance_metadata_tables/"><code>fabricops_kit.governance_review._setup_governance_metadata_tables</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>
- <a href="../review_pipeline_run/"><code>fabricops_kit.governance_review.review_pipeline_run</code></a>
- <a href="../internal/metadata__register_current_notebook/"><code>fabricops_kit.metadata._register_current_notebook</code></a>
- <a href="../internal/metadata__setup_notebook_registry_table/"><code>fabricops_kit.metadata._setup_notebook_registry_table</code></a>

## Outbound references
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
