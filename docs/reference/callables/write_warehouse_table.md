# write_warehouse_table

**Module:** `fabric_input_output`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use when publishing a Spark DataFrame to a configured Fabric warehouse table.

## When not to use this

Do not use for lakehouse table writes, lakehouse Files writes, or metadata evidence writes.

## Quick example

write_warehouse_table(serving_df, CONFIG, env="Sandbox", target="Warehouse", schema="dbo", table="orders_serving", mode="append")

## Signature

```python
def write_warehouse_table(df, config, env, target, schema, table, mode='append')
```

## Parameters

df, config, env, target, schema, table, and write mode.

## Returns

None; the DataFrame is written to the configured warehouse table.

## Raises

Raises configuration, Spark connector, or warehouse write errors when the target/table cannot be written.

## Side effects

Writes data to a Fabric warehouse table using the selected mode.

## FabricOps context

Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.

## AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** df, config, env, target, schema, table, and write mode.
- **output:** None; the DataFrame is written to the configured warehouse table.
- **side_effects:** Writes data to a Fabric warehouse table using the selected mode.
- **failure_modes:** Raises configuration, Spark connector, or warehouse write errors when the target/table cannot be written.
- **verification:** Verify guardrails passed, confirm schema/table routing from CONFIG, and check the intended write mode before calling.

## Related functions

- <a href="../read_warehouse_table/"><code>fabricops_kit.fabric_input_output.read_warehouse_table</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.drift.stop_if_failed</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source reference: <a href="../../api/modules/fabric_input_output/#write_warehouse_table">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.write_warehouse_table`
- Short name: `write_warehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Inbound references count: 0
- Outbound references count: 1

## Outbound references
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
