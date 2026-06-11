# _build_categorical_distribution

**Module:** `data_profiling`  
**Classification:** Internal

## Status

Internal helper used by the package implementation.

## Function type: Internal helper

Internal helper

## Direct use: No

Do not call this helper directly from notebooks; use the public callable helpers instead.

## Used by

- <a href="../internal/data_profiling__build_distribution_summaries/"><code>fabricops_kit.data_profiling._build_distribution_summaries</code></a>

## Purpose

No summary available.

## Signature if available

```python
def _build_categorical_distribution(df, column_name: str, *, top_n: int=20, categories: list[str] | set[str] | tuple[str, ...] | None=None) -> dict[str, Any] | None
```

## Side effects

Not documented yet

## Maintainer notes

Maintain this helper through the owning implementation module and keep generated references in sync.

## AI implementation contract

Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks.

## Function manifest

- Fully qualified function name: `fabricops_kit.data_profiling._build_categorical_distribution`
- Short name: `_build_categorical_distribution`
- Module: `data_profiling`
- Classification: Internal
- Related module: `data_profiling`
- Source file path: `src/fabricops_kit/data_profiling.py`
- Source reference: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/a212c94775e71b6e429e41b51fbc57ac733903cb/src/fabricops_kit/data_profiling.py#L150-L187">View source on GitHub</a>
- Inbound references count: 1
- Outbound references count: 0

## Inbound references
- <a href="../internal/data_profiling__build_distribution_summaries/"><code>fabricops_kit.data_profiling._build_distribution_summaries</code></a>
