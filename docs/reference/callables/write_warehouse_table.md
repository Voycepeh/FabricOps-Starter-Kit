# write_warehouse_table

**Module:** `fabric_input_output`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Write a DataFrame to a configured Fabric warehouse target.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def write_warehouse_table(df, config, env, target, schema, table, mode='append')
```

## Parameters

df : pyspark.sql.DataFrame
    Spark DataFrame to write.
config : FrameworkConfig | dict
    FabricOps FrameworkConfig or compatible config object.
env : str
    Environment name in the config mapping, for example `"Sandbox"` or `"DE"`.
target : str
    Warehouse target name under the selected environment, for example
    `"Warehouse"` or `"wh_Bronze"`.
schema : str
    Warehouse schema name, for example `"dbo"`.
table : str
    Warehouse table name.
mode : str, default "append"
    Spark write mode, for example `"append"` or `"overwrite"`.

## Returns

None
    The DataFrame is written to the target warehouse table.

## Raises

RuntimeError
    If the Microsoft Fabric Spark connector is unavailable.
ValueError
    If the selected environment or target is missing from the config.

## Side effects

Not documented yet

## FabricOps context

Starter template: `02_pipeline`; segment: `Fabric IO`.

## AI implementation contract

Not documented yet

## Related functions

- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>

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
