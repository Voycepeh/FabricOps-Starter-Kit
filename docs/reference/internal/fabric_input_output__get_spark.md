# _get_spark

**Module:** `fabric_input_output`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../read_warehouse_table/"><code>fabricops_kit.fabric_input_output.read_warehouse_table</code></a>

## Purpose

Return an explicit Spark session or the active notebook global `spark`.

## Signature if available

```python
def _get_spark(spark_session=None)
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output._get_spark`
- Short name: `_get_spark`
- Module: `fabric_input_output`
- Classification: Internal
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/cb8dad0bc076c72220f65712e627dcc0b38043e0/src/fabricops_kit/fabric_input_output.py#L87-L117">View source on GitHub</a>
- Inbound references count: 5
- Outbound references count: 0

## Inbound references
- <a href="../read_lakehouse_csv/"><code>fabricops_kit.fabric_input_output.read_lakehouse_csv</code></a>
- <a href="../read_lakehouse_excel/"><code>fabricops_kit.fabric_input_output.read_lakehouse_excel</code></a>
- <a href="../read_lakehouse_parquet/"><code>fabricops_kit.fabric_input_output.read_lakehouse_parquet</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../read_warehouse_table/"><code>fabricops_kit.fabric_input_output.read_warehouse_table</code></a>
