# _validate_metadata_table_registration

**Module:** `config`
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

Validate that active metadata tables are registered in the Spark catalog.

## Signature if available

```python
def _validate_metadata_table_registration(*, spark: Any, config: FrameworkConfig | dict[str, Any], env: str, expected_tables: list[str] | None=None) -> dict[str, Any]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.config._validate_metadata_table_registration`
- Short name: `_validate_metadata_table_registration`
- Module: `config`
- Classification: Internal
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1bac7913a070db1a771a2991ff5421c37ffc9d94/src/fabricops_kit/config.py#L994-L1032">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 4

## Inbound references
- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

## Outbound references
- <a href="../internal/config__detect_nested_metadata_delta_folders/"><code>fabricops_kit.config._detect_nested_metadata_delta_folders</code></a>
- <a href="../internal/config__get_active_metadata_tables/"><code>fabricops_kit.config._get_active_metadata_tables</code></a>
- <a href="../internal/config__show_tables_for_metadata_lakehouse/"><code>fabricops_kit.config._show_tables_for_metadata_lakehouse</code></a>
- <a href="../internal/config__validate_framework_config/"><code>fabricops_kit.config._validate_framework_config</code></a>
