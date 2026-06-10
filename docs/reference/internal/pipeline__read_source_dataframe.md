# _read_source_dataframe

**Module:** `pipeline`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../prepare_source_table_configs/"><code>fabricops_kit.pipeline.prepare_source_table_configs</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _read_source_dataframe(source_config: Mapping[str, Any], *, config: Any, env: str, spark_session: Any)
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.pipeline._read_source_dataframe`
- Short name: `_read_source_dataframe`
- Module: `pipeline`
- Classification: Internal
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/pipeline.py#L124-L173">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 6

## Inbound references
- <a href="../prepare_source_table_configs/"><code>fabricops_kit.pipeline.prepare_source_table_configs</code></a>

## Outbound references
- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../read_warehouse_table/"><code>fabricops_kit.fabric_input_output.read_warehouse_table</code></a>
- <a href="../internal/pipeline__source_read_type/"><code>fabricops_kit.pipeline._source_read_type</code></a>
