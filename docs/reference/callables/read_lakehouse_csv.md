# read_lakehouse_csv

**Module:** `fabric_input_output`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use when reading a CSV file from a configured Fabric lakehouse Files path.

## When not to use this

Do not use for Delta tables, Parquet files, Excel files, or warehouse SQL tables.

## Quick example

df = read_lakehouse_csv(CONFIG, env="Sandbox", target="Source", relative_path="raw/orders/orders.csv", header=True, spark_session=spark)

## Signature

```python
def read_lakehouse_csv(config, env, target, relative_path, spark_session=None, header=True)
```

## Parameters

config, env, target, relative_path, CSV read options, verbose flag, and optional spark_session.

## Returns

Spark DataFrame loaded from the lakehouse Files CSV path.

## Raises

Raises ValueError for invalid file paths and configuration/Spark errors when the file cannot be read.

## Side effects

Reads from lakehouse Files; it does not write metadata, tables, or files.

## FabricOps context

Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.

## AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** config, env, target, relative_path, CSV read options, verbose flag, and optional spark_session.
- **output:** Spark DataFrame loaded from the lakehouse Files CSV path.
- **side_effects:** Reads from lakehouse Files; it does not write metadata, tables, or files.
- **failure_modes:** Raises ValueError for invalid file paths and configuration/Spark errors when the file cannot be read.
- **verification:** Verify relative_path points under Files, then check row count and schema after reading.

## Related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source reference: <a href="../../api/modules/fabric_input_output/#read_lakehouse_csv">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_lakehouse_csv`
- Short name: `read_lakehouse_csv`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Inbound references count: 0
- Outbound references count: 3

## Outbound references
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
- <a href="../internal/fabric_input_output__lakehouse_file_path/"><code>fabricops_kit.fabric_input_output._lakehouse_file_path</code></a>
