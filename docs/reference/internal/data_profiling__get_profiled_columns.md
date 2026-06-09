# _get_profiled_columns

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

Return non-technical column names from a Spark DataFrame.

## Signature if available

```python
def _get_profiled_columns(df, exclude_columns: list[str] | set[str] | None=None) -> list[str]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_profiling._get_profiled_columns`
- Short name: `_get_profiled_columns`
- Module: `data_profiling`
- Classification: Internal
- Related module: `data_profiling`
- Source file path: `src/fabricops_kit/data_profiling.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/15f1799b713dde469e690b3bbdf35ffe588ff83c/src/fabricops_kit/data_profiling.py#L57-L79">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 0

## Inbound references
- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
