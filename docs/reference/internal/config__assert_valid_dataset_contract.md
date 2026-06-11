# _assert_valid_dataset_contract

**Module:** `config`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

Not documented yet

## Purpose

Raise when a dataset contract violates the expected schema.

## Signature if available

```python
def _assert_valid_dataset_contract(contract: dict, schema_path: str | Path | None=None) -> None
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.config._assert_valid_dataset_contract`
- Short name: `_assert_valid_dataset_contract`
- Module: `config`
- Classification: Internal
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/031081c64115c5424552b6af13bbaeb983c852dd/src/fabricops_kit/config.py#L1009-L1030">View source on GitHub</a>
- Inbound references count: 0
- Outbound references count: 2

## Outbound references
- <a href="../internal/config_DatasetContractValidationError/"><code>fabricops_kit.config.DatasetContractValidationError</code></a>
- <a href="../internal/config__validate_dataset_contract/"><code>fabricops_kit.config._validate_dataset_contract</code></a>
