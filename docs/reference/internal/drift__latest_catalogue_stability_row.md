# _latest_catalogue_stability_row

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
def _latest_catalogue_stability_row(spark, metadata_table: str, dataset_name: str, table_name: str, profile_stage: str, exclude_run_id: str | None=None) -> dict | None
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.drift._latest_catalogue_stability_row`
- Short name: `_latest_catalogue_stability_row`
- Module: `drift`
- Classification: Internal
- Related module: `drift`
- Source file path: `src/fabricops_kit/drift.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/6e744d11e5f3081af2c7f10e6b37ccaaba97dd6d/src/fabricops_kit/drift.py#L542-L598">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 2

## Inbound references
- <a href="../enforce_catalogue_stability/"><code>fabricops_kit.drift.enforce_catalogue_stability</code></a>

## Outbound references
- <a href="../internal/drift__is_missing_table_error/"><code>fabricops_kit.drift._is_missing_table_error</code></a>
- <a href="../internal/drift__row_to_dict/"><code>fabricops_kit.drift._row_to_dict</code></a>
