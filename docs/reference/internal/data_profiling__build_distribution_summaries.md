# _build_distribution_summaries

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

No summary available.

## Signature if available

```python
def _build_distribution_summaries(df, eligible_columns: list[str], dtype_map: dict[str, str], *, include_distributions: bool, distribution_columns: list[str] | set[str] | tuple[str, ...] | None, distribution_bin_edges: dict[str, list[float]] | None, categorical_categories: dict[str, list[str]] | None, categorical_top_n: int) -> dict[str, tuple[str, dict[str, Any]]]
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_profiling._build_distribution_summaries`
- Short name: `_build_distribution_summaries`
- Module: `data_profiling`
- Classification: Internal
- Related module: `data_profiling`
- Source file path: `src/fabricops_kit/data_profiling.py`
- Source reference: <a href="../../api/modules/data_profiling/#_build_distribution_summaries">Module source anchor</a>
- Inbound references count: 1
- Outbound references count: 3

## Inbound references
- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>

## Outbound references
- <a href="../internal/data_profiling__build_categorical_distribution/"><code>fabricops_kit.data_profiling._build_categorical_distribution</code></a>
- <a href="../internal/data_profiling__build_numeric_distribution/"><code>fabricops_kit.data_profiling._build_numeric_distribution</code></a>
- <a href="../internal/data_profiling__numeric_bin_edges/"><code>fabricops_kit.data_profiling._numeric_bin_edges</code></a>
