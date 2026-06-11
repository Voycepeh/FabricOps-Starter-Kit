# _show_tables_for_metadata_lakehouse

**Module:** `config`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/config__validate_metadata_table_registration/"><code>fabricops_kit.config._validate_metadata_table_registration</code></a>

## Purpose

Run SHOW TABLES for the configured metadata lakehouse when available.

## Signature if available

```python
def _show_tables_for_metadata_lakehouse(*, spark: Any, config: FrameworkConfig | dict[str, Any], env: str) -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.config._show_tables_for_metadata_lakehouse`
- Short name: `_show_tables_for_metadata_lakehouse`
- Module: `config`
- Classification: Internal
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b37a3d3a2b947b2e265229d7ea688a0bac6a5396/src/fabricops_kit/config.py#L833-L868">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 1

## Inbound references
- <a href="../internal/config__validate_metadata_table_registration/"><code>fabricops_kit.config._validate_metadata_table_registration</code></a>

## Outbound references
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
