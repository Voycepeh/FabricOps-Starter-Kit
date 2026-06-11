# _stability_exclude_columns

**Module:** `drift`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/drift__schema_hash_from_dataframe/"><code>fabricops_kit.drift._schema_hash_from_dataframe</code></a>
- <a href="../enforce_catalogue_stability/"><code>fabricops_kit.drift.enforce_catalogue_stability</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _stability_exclude_columns(exclude_columns: list[str] | set[str] | tuple[str, ...] | None=None) -> set[str]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.drift._stability_exclude_columns`
- Short name: `_stability_exclude_columns`
- Module: `drift`
- Classification: Internal
- Related module: `drift`
- Source file path: `src/fabricops_kit/drift.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/031081c64115c5424552b6af13bbaeb983c852dd/src/fabricops_kit/drift.py#L339-L343">View source on GitHub</a>
- Inbound references count: 2
- Outbound references count: 0

## Inbound references
- <a href="../internal/drift__schema_hash_from_dataframe/"><code>fabricops_kit.drift._schema_hash_from_dataframe</code></a>
- <a href="../enforce_catalogue_stability/"><code>fabricops_kit.drift.enforce_catalogue_stability</code></a>
