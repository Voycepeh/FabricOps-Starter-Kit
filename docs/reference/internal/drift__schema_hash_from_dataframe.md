# _schema_hash_from_dataframe

**Module:** `drift`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../enforce_catalogue_stability/"><code>fabricops_kit.drift.enforce_catalogue_stability</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _schema_hash_from_dataframe(dataframe, exclude_columns: list[str] | set[str] | tuple[str, ...] | None=None) -> str
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.drift._schema_hash_from_dataframe`
- Short name: `_schema_hash_from_dataframe`
- Module: `drift`
- Classification: Internal
- Related module: `drift`
- Source file path: `src/fabricops_kit/drift.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/031081c64115c5424552b6af13bbaeb983c852dd/src/fabricops_kit/drift.py#L351-L355">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 4

## Inbound references
- <a href="../enforce_catalogue_stability/"><code>fabricops_kit.drift.enforce_catalogue_stability</code></a>

## Outbound references
- <a href="../internal/drift__actual_schema/"><code>fabricops_kit.drift._actual_schema</code></a>
- <a href="../internal/drift__canonical_json_hash/"><code>fabricops_kit.drift._canonical_json_hash</code></a>
- <a href="../internal/drift__is_stability_excluded_column/"><code>fabricops_kit.drift._is_stability_excluded_column</code></a>
- <a href="../internal/drift__stability_exclude_columns/"><code>fabricops_kit.drift._stability_exclude_columns</code></a>
