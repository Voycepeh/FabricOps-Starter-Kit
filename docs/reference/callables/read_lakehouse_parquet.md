# read_lakehouse_parquet

**Module:** `fabric_input_output`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use when reading a Parquet file or path from a configured Fabric lakehouse Files path.

## When not to use this

Do not use for Delta tables, CSV files, Excel files, or warehouse SQL tables.

## Quick example

df = read_lakehouse_parquet(CONFIG, env="Sandbox", target="Source", relative_path="raw/orders/orders.parquet", spark_session=spark)

## Signature

```python
def read_lakehouse_parquet(config, env, target, relative_path, verbose=True, spark_session=None)
```

## Parameters

config, env, target, relative_path, verbose flag, and optional spark_session.

## Returns

Spark DataFrame loaded from the original Parquet path or timestamp-converted fallback path.

## Raises

Raises ValueError for invalid relative paths and Spark/read errors when the Parquet path cannot be loaded.

## Side effects

Reads from lakehouse Files and may create a local timestamp-converted fallback for single-file Parquet precision issues; it does not write metadata tables.

## FabricOps context

Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.

## AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** config, env, target, relative_path, verbose flag, and optional spark_session.
- **output:** Spark DataFrame loaded from the original Parquet path or timestamp-converted fallback path.
- **side_effects:** Reads from lakehouse Files and may create a local timestamp-converted fallback for single-file Parquet precision issues; it does not write metadata tables.
- **failure_modes:** Raises ValueError for invalid relative paths and Spark/read errors when the Parquet path cannot be loaded.
- **verification:** Verify the file path is a lakehouse Files Parquet path and check row count/schema after reading.

## Related functions

- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source reference: <a href="../../api/modules/fabric_input_output/#read_lakehouse_parquet">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_lakehouse_parquet`
- Short name: `read_lakehouse_parquet`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Inbound references count: 0
- Outbound references count: 4

## Outbound references
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__convert_single_parquet_ns_to_us/"><code>fabricops_kit.fabric_input_output._convert_single_parquet_ns_to_us</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
- <a href="../internal/fabric_input_output__lakehouse_file_path/"><code>fabricops_kit.fabric_input_output._lakehouse_file_path</code></a>
