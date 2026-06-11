# _normalize_table_name

**Module:** `fabric_input_output`
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/fabric_input_output__registered_table_identifier/"><code>fabricops_kit.fabric_input_output._registered_table_identifier</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>

## Purpose

Return a safe Spark table name, never a nested folder path.

## Signature if available

```python
def _normalize_table_name(table: str) -> str
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output._normalize_table_name`
- Short name: `_normalize_table_name`
- Module: `fabric_input_output`
- Classification: Internal
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/fabric_input_output.py#L81-L90">View source on GitHub</a>
- Inbound references count: 3
- Outbound references count: 0

## Inbound references
- <a href="../internal/fabric_input_output__registered_table_identifier/"><code>fabricops_kit.fabric_input_output._registered_table_identifier</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
