# _check_profile_drift

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

Compare profile metrics against a baseline profile and drift thresholds.

## Signature if available

```python
def _check_profile_drift(current_profile: dict, baseline_profile: dict | None=None, policy: dict | None=None) -> dict
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.drift._check_profile_drift`
- Short name: `_check_profile_drift`
- Module: `drift`
- Classification: Internal
- Related module: `drift`
- Source file path: `src/fabricops_kit/drift.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/drift.py#L319-L401">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 3

## Inbound references
- <a href="../monitor_data_changes/"><code>fabricops_kit.drift.monitor_data_changes</code></a>

## Outbound references
- <a href="../internal/drift__categorical_distance/"><code>fabricops_kit.drift._categorical_distance</code></a>
- <a href="../internal/drift__normalize_profile/"><code>fabricops_kit.drift._normalize_profile</code></a>
- <a href="../internal/drift__numeric_psi/"><code>fabricops_kit.drift._numeric_psi</code></a>
