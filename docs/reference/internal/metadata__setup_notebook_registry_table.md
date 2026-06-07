# _setup_notebook_registry_table

**Module:** `metadata`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

## Purpose

Create or validate the notebook registry metadata table.

## Signature if available

```python
def _setup_notebook_registry_table(*, spark: Any, config: Any, env: str, metadata_table: str=NOTEBOOK_REGISTRY_TABLE) -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.metadata._setup_notebook_registry_table`
- Short name: `_setup_notebook_registry_table`
- Module: `metadata`
- Classification: Internal
- Related module: `metadata`
- Source file path: `src/fabricops_kit/metadata.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4c16c62a2fd27c5a88a51c78e285c4b6e922580a/src/fabricops_kit/metadata.py#L60-L129">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 5

## Inbound references
- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

## Outbound references
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../internal/metadata__coerce_row_dicts/"><code>fabricops_kit.metadata._coerce_row_dicts</code></a>
- <a href="../internal/metadata__registry_rows_with_defaults/"><code>fabricops_kit.metadata._registry_rows_with_defaults</code></a>
- <a href="../internal/metadata__rows_for_spark/"><code>fabricops_kit.metadata._rows_for_spark</code></a>
