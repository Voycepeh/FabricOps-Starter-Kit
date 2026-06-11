# _get_active_metadata_tables

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
- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

## Purpose

Return the canonical active metadata tables prepared by ``00_env_config``.

## Signature if available

```python
def _get_active_metadata_tables(config: FrameworkConfig | dict[str, Any]) -> list[str]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.config._get_active_metadata_tables`
- Short name: `_get_active_metadata_tables`
- Module: `config`
- Classification: Internal
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a80b5a6ddb4de14056095d4da916cd452e478ff8/src/fabricops_kit/config.py#L889-L916">View source on GitHub</a>
- Inbound references count: 2
- Outbound references count: 2

## Inbound references
- <a href="../internal/config__validate_metadata_table_registration/"><code>fabricops_kit.config._validate_metadata_table_registration</code></a>
- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

## Outbound references
- <a href="../internal/config__validate_framework_config/"><code>fabricops_kit.config._validate_framework_config</code></a>
- <a href="../internal/governance_review__get_governance_metadata_schemas/"><code>fabricops_kit.governance_review._get_governance_metadata_schemas</code></a>
