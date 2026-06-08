# _setup_data_agreement_tables

**Module:** `data_agreement`  
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

Prepare intake tables and report whether agreement intake has a steward.

## Signature if available

```python
def _setup_data_agreement_tables(*, spark: Any, config: Any, env: str, require_active_steward: bool=False) -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._setup_data_agreement_tables`
- Short name: `_setup_data_agreement_tables`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c7049e78d915b93903574ea792043a66ebe62cee/src/fabricops_kit/data_agreement.py#L451-L485">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 2

## Inbound references
- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

## Outbound references
- <a href="../internal/data_agreement__ensure_metadata_tables/"><code>fabricops_kit.data_agreement._ensure_metadata_tables</code></a>
- <a href="../internal/data_agreement__list_data_stewards/"><code>fabricops_kit.data_agreement._list_data_stewards</code></a>
