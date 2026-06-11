# _load_and_validate_dataset_contract

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

Load a dataset contract file and return schema validation findings.

## Signature if available

```python
def _load_and_validate_dataset_contract(path: str | Path, schema_path: str | Path | None=None) -> tuple[dict, list[str]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.config._load_and_validate_dataset_contract`
- Short name: `_load_and_validate_dataset_contract`
- Module: `config`
- Classification: Internal
- Related module: `config`
- Source file path: `src/fabricops_kit/config.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1bac7913a070db1a771a2991ff5421c37ffc9d94/src/fabricops_kit/config.py#L1262-L1286">View source on GitHub</a>
- Inbound references count: 0
- Outbound references count: 2

## Outbound references
- <a href="../internal/config__load_dataset_contract/"><code>fabricops_kit.config._load_dataset_contract</code></a>
- <a href="../internal/config__validate_dataset_contract/"><code>fabricops_kit.config._validate_dataset_contract</code></a>
