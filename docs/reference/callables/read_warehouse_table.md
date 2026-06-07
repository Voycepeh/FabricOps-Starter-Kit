# read_warehouse_table

**Module:** `fabric_input_output`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use when reading a table from a configured Fabric warehouse target.

## When not to use this

Do not use for lakehouse Delta tables or lakehouse Files CSV, Parquet, or Excel paths.

## Quick example

df = read_warehouse_table(CONFIG, env="Sandbox", target="Warehouse", schema="dbo", table="orders", spark_session=spark)

## Signature

```python
def read_warehouse_table(config, env, target, schema, table, spark_session=None)
```

## Parameters

config, env, target, schema, table, optional verbose flag, and optional spark_session.

## Returns

Spark DataFrame loaded from the configured warehouse table.

## Raises

Raises configuration, Spark SQL, or warehouse-read errors when the target/table cannot be resolved/read.

## Side effects

Reads from a warehouse table; it does not write metadata, tables, or files.

## FabricOps context

Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.

## AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** config, env, target, schema, table, optional verbose flag, and optional spark_session.
- **output:** Spark DataFrame loaded from the configured warehouse table.
- **side_effects:** Reads from a warehouse table; it does not write metadata, tables, or files.
- **failure_modes:** Raises configuration, Spark SQL, or warehouse-read errors when the target/table cannot be resolved/read.
- **verification:** Verify the warehouse target/schema/table are configured and inspect the resulting DataFrame schema before downstream use.

## Related functions

- <a href="../write_warehouse_table/"><code>fabricops_kit.fabric_input_output.write_warehouse_table</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source reference: <a href="../../api/modules/fabric_input_output/#read_warehouse_table">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_warehouse_table`
- Short name: `read_warehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Inbound references count: 0
- Outbound references count: 2

## Outbound references
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
