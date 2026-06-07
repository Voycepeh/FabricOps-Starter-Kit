# _load_latest_profile

**Module:** `drift`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../monitor_data_changes/"><code>fabricops_kit.drift.monitor_data_changes</code></a>

## Purpose

Load an explicit profile-drift baseline from profile metadata rows.

## Signature if available

```python
def _load_latest_profile(spark, metadata_table: str, dataset_name: str, table_name: str, profile_stage: str, exclude_run_id: str | None=None, baseline_mode: str='latest_successful') -> dict | None
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.drift._load_latest_profile`
- Short name: `_load_latest_profile`
- Module: `drift`
- Classification: Internal
- Related module: `drift`
- Source file path: `src/fabricops_kit/drift.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/drift.py#L410-L500">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 2

## Inbound references
- <a href="../monitor_data_changes/"><code>fabricops_kit.drift.monitor_data_changes</code></a>

## Outbound references
- <a href="../internal/drift__is_missing_table_error/"><code>fabricops_kit.drift._is_missing_table_error</code></a>
- <a href="../internal/drift__normalize_profile/"><code>fabricops_kit.drift._normalize_profile</code></a>
