# _active_steward

**Module:** `data_agreement`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/data_agreement__create_or_update_data_steward/"><code>fabricops_kit.data_agreement._create_or_update_data_steward</code></a>
- <a href="../internal/data_agreement__list_data_stewards/"><code>fabricops_kit.data_agreement._list_data_stewards</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _active_steward(row: dict[str, Any]) -> bool
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement._active_steward`
- Short name: `_active_steward`
- Module: `data_agreement`
- Classification: Internal
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/7671b3d58873b7627843d2a35ac9cb4dae15eb9a/src/fabricops_kit/data_agreement.py#L516-L526">View source on GitHub</a>
- Inbound references count: 2
- Outbound references count: 1

## Inbound references
- <a href="../internal/data_agreement__create_or_update_data_steward/"><code>fabricops_kit.data_agreement._create_or_update_data_steward</code></a>
- <a href="../internal/data_agreement__list_data_stewards/"><code>fabricops_kit.data_agreement._list_data_stewards</code></a>

## Outbound references
- <a href="../internal/data_agreement__to_bool/"><code>fabricops_kit.data_agreement._to_bool</code></a>
