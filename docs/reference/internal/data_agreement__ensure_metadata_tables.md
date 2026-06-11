# _ensure_metadata_tables

**Module:** `data_agreement`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/data_agreement__setup_data_agreement_tables/"><code>fabricops_kit.data_agreement._setup_data_agreement_tables</code></a>

## Purpose

Idempotently create or validate lightweight ``01_agreement`` metadata tables.

## Signature if available

```python
def _ensure_metadata_tables(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._ensure_metadata_tables`
- Short name: `_ensure_metadata_tables`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/8f8ba1a4c1e063896508520952dedc3eda348629/src/fabricops_kit/data_agreement.py#L405-L448">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 4

## Inbound references
- <a href="../internal/data_agreement__setup_data_agreement_tables/"><code>fabricops_kit.data_agreement._setup_data_agreement_tables</code></a>

## Outbound references
- <a href="../internal/data_agreement__coerce_row_dicts/"><code>fabricops_kit.data_agreement._coerce_row_dicts</code></a>
- <a href="../internal/data_agreement__config_value/"><code>fabricops_kit.data_agreement._config_value</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
