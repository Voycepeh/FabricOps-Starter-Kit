# _is_min_max_supported_type

**Module:** `data_profiling`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>

## Purpose

Return whether min/max aggregation is safe for a Spark type string.

## Signature if available

```python
def _is_min_max_supported_type(data_type: str) -> bool
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_profiling._is_min_max_supported_type`
- Short name: `_is_min_max_supported_type`
- Module: `data_profiling`
- Classification: Internal
- Related module: `data_profiling`
- Source file path: `src/fabricops_kit/data_profiling.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L72-L92">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 0

## Inbound references
- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
