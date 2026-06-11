# _lakehouse_table_identifier

**Module:** `fabric_input_output`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>

## Purpose

Return a Spark SQL table identifier qualified by lakehouse/database name.

## Signature if available

```python
def _lakehouse_table_identifier(store: FabricStore, table: str) -> str
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output._lakehouse_table_identifier`
- Short name: `_lakehouse_table_identifier`
- Module: `fabric_input_output`
- Classification: Internal
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b37a3d3a2b947b2e265229d7ea688a0bac6a5396/src/fabricops_kit/fabric_input_output.py#L97-L100">View source on GitHub</a>
- Inbound references count: 2
- Outbound references count: 2

## Inbound references
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>

## Outbound references
- <a href="../internal/fabric_input_output__normalize_table_name/"><code>fabricops_kit.fabric_input_output._normalize_table_name</code></a>
- <a href="../internal/fabric_input_output__quote_identifier/"><code>fabricops_kit.fabric_input_output._quote_identifier</code></a>
