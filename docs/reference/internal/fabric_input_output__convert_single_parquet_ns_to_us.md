# _convert_single_parquet_ns_to_us

**Module:** `fabric_input_output`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>

## Purpose

Convert one Parquet file from nanosecond to microsecond timestamps.

## Signature if available

```python
def _convert_single_parquet_ns_to_us(local_in_path, local_out_path, verbose=True)
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output._convert_single_parquet_ns_to_us`
- Short name: `_convert_single_parquet_ns_to_us`
- Module: `fabric_input_output`
- Classification: Internal
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4c16c62a2fd27c5a88a51c78e285c4b6e922580a/src/fabricops_kit/fabric_input_output.py#L452-L504">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 0

## Inbound references
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
