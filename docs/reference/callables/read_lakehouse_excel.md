# read_lakehouse_excel

**Module:** `fabric_input_output`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use when reading .xlsx files from a configured Fabric lakehouse Files path, especially small reference files, mapping tables, or manually maintained business inputs.

## When not to use this

Do not use for Delta tables, CSV files, Parquet files, or warehouse SQL tables.

## Quick example

mapping_df = read_lakehouse_excel(CONFIG, env="Sandbox", target="Source", relative_path="reference/faculty_mapping.xlsx", sheet_name=0, spark_session=spark)

## Signature

```python
def read_lakehouse_excel(config, env, target, relative_path, sheet_name=0, spark_session=None, **read_excel_kwargs)
```

## Parameters

config, env, target, relative_path, optional sheet_name, optional spark_session, and pandas read_excel keyword arguments.

## Returns

Spark DataFrame converted from the selected Excel worksheet.

## Raises

Raises ValueError for invalid or non-Excel paths and Fabric/Spark/pandas errors when the file cannot be read.

## Side effects

Reads from lakehouse Files through a temporary local Excel file; it does not write metadata, tables, or files.

## FabricOps context

Requires 00_env_config config/env/target context for resolving the configured lakehouse Files path.

## AI implementation contract

- **required_context:** Requires 00_env_config config/env/target context for resolving the configured lakehouse Files path.
- **inputs:** config, env, target, relative_path, optional sheet_name, optional spark_session, and pandas read_excel keyword arguments.
- **output:** Spark DataFrame converted from the selected Excel worksheet.
- **side_effects:** Reads from lakehouse Files through a temporary local Excel file; it does not write metadata, tables, or files.
- **failure_modes:** Raises ValueError for invalid or non-Excel paths and Fabric/Spark/pandas errors when the file cannot be read.
- **verification:** Verify the DataFrame row count and schema after reading, and confirm the Excel file is appropriate for a small reference-style input.

## Related functions

- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source reference: <a href="../../api/modules/fabric_input_output/#read_lakehouse_excel">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.read_lakehouse_excel`
- Short name: `read_lakehouse_excel`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Inbound references count: 0
- Outbound references count: 3

## Outbound references
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
- <a href="../internal/fabric_input_output__get_spark/"><code>fabricops_kit.fabric_input_output._get_spark</code></a>
- <a href="../internal/fabric_input_output__lakehouse_file_path/"><code>fabricops_kit.fabric_input_output._lakehouse_file_path</code></a>
