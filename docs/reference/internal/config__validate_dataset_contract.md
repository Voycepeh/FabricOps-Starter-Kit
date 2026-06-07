# _validate_dataset_contract

**Module:** `config`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/config__assert_valid_dataset_contract/"><code>fabricops_kit.config._assert_valid_dataset_contract</code></a>
- <a href="../internal/config__load_and_validate_dataset_contract/"><code>fabricops_kit.config._load_and_validate_dataset_contract</code></a>

## Purpose

Validate a loaded dataset contract against the JSON schema.

## Signature if available

```python
def _validate_dataset_contract(contract: dict, schema_path: str | Path | None=None) -> list[str]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.config._validate_dataset_contract`
- Short name: `_validate_dataset_contract`
- Module: `config`
- Classification: Internal
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1171b98e11e7afc7b6351c6501d1c7050119657f/src/fabricops_kit/config.py#L867-L894">View source on GitHub</a>
- Inbound references count: 2
- Outbound references count: 2

## Inbound references
- <a href="../internal/config__assert_valid_dataset_contract/"><code>fabricops_kit.config._assert_valid_dataset_contract</code></a>
- <a href="../internal/config__load_and_validate_dataset_contract/"><code>fabricops_kit.config._load_and_validate_dataset_contract</code></a>

## Outbound references
- <a href="../internal/config__format_error_path/"><code>fabricops_kit.config._format_error_path</code></a>
- <a href="../internal/config__load_schema/"><code>fabricops_kit.config._load_schema</code></a>
