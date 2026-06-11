# _detect_nested_metadata_delta_folders

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

Best-effort warning detector for legacy nested metadata Delta folders.

## Signature if available

```python
def _detect_nested_metadata_delta_folders(*, config: FrameworkConfig | dict[str, Any], env: str, expected_tables: list[str]) -> list[str]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.config._detect_nested_metadata_delta_folders`
- Short name: `_detect_nested_metadata_delta_folders`
- Module: `config`
- Classification: Internal
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/config.py#L971-L991">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 1

## Inbound references
- <a href="../internal/config__validate_metadata_table_registration/"><code>fabricops_kit.config._validate_metadata_table_registration</code></a>

## Outbound references
- <a href="../internal/config__get_store/"><code>fabricops_kit.config._get_store</code></a>
