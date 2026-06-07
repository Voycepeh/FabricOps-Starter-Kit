# profile_dataframe

**Module:** `data_profiling`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Profile a source or target DataFrame for schema, quality, and catalogue evidence.

## When not to use this

Not documented yet

## Quick example

Not documented yet

## Signature

```python
def profile_dataframe(df, table_name: str, *, exclude_columns=None, run_timestamp_timezone='Asia/Singapore', include_distributions: bool=False, distribution_columns: list[str] | set[str] | tuple[str, ...] | None=None, distribution_bin_edges: dict[str, list[float]] | None=None, categorical_categories: dict[str, list[str]] | None=None, categorical_top_n: int=20)
```

## Parameters

df : Any
    Spark DataFrame to profile.
table_name : str
    Logical table name written into each profile row.
exclude_columns : list[str] or set[str], optional
    Additional columns to skip, on top of the standard technical columns.
run_timestamp_timezone : str, default="Asia/Singapore"
    Time zone used for the ``RUN_TIMESTAMP`` evidence field.
include_distributions : bool, default=False
    When true, add lightweight distribution summaries for suitable numeric
    and categorical columns. The default preserves the existing lightweight
    profile shape and behavior.
distribution_columns : list[str] or set[str] or tuple[str, ...], optional
    Optional allow-list of important columns for distribution summaries.
    ``None`` profiles every suitable business column.
distribution_bin_edges : dict[str, list[float]], optional
    Optional numeric bin edges keyed by column name. Pass baseline edges to
    make the current profile directly comparable with a previous profile.
categorical_categories : dict[str, list[str]], optional
    Optional baseline category vocabulary keyed by column name. When
    supplied, those categories are counted explicitly and all other non-null
    values are rolled into ``other_count`` so the current profile remains
    comparable with the baseline.
categorical_top_n : int, default=20
    Maximum number of non-null category values to keep per categorical
    column before rolling the remainder into ``other_count``.

## Returns

Any
    Spark DataFrame containing one profile row per eligible business
    column. Existing columns are preserved; distribution-enabled runs also
    include ``DISTRIBUTION_TYPE`` and ``DISTRIBUTION_JSON``.

## Raises

Not documented yet

## Side effects

Not documented yet

## FabricOps context

Starter template: `02_pipeline / optional 99_explore`; segment: `Profiling`.

## AI implementation contract

Not documented yet

## Related functions

- <a href="../monitor_data_changes/"><code>fabricops_kit.drift.monitor_data_changes</code></a>
- <a href="../internal/governance_review__prepare_dq_profile_input_rows/"><code>fabricops_kit.governance_review._prepare_dq_profile_input_rows</code></a>
- <a href="../internal/data_profiling__build_distribution_summaries/"><code>fabricops_kit.data_profiling._build_distribution_summaries</code></a>
- <a href="../internal/data_profiling__get_profiled_columns/"><code>fabricops_kit.data_profiling._get_profiled_columns</code></a>
- <a href="../internal/data_profiling__is_min_max_supported_type/"><code>fabricops_kit.data_profiling._is_min_max_supported_type</code></a>

## Source and tests

- Source file path: `src/fabricops_kit/data_profiling.py`
- Source reference: <a href="../../api/modules/data_profiling/#profile_dataframe">Module source anchor</a>
- Tests: Not documented yet

## Function manifest

- Fully qualified function name: `fabricops_kit.data_profiling.profile_dataframe`
- Short name: `profile_dataframe`
- Module: `data_profiling`
- Classification: Callable
- Related module: `data_profiling`
- Inbound references count: 2
- Outbound references count: 3

## Inbound references
- <a href="../monitor_data_changes/"><code>fabricops_kit.drift.monitor_data_changes</code></a>
- <a href="../internal/governance_review__prepare_dq_profile_input_rows/"><code>fabricops_kit.governance_review._prepare_dq_profile_input_rows</code></a>

## Outbound references
- <a href="../internal/data_profiling__build_distribution_summaries/"><code>fabricops_kit.data_profiling._build_distribution_summaries</code></a>
- <a href="../internal/data_profiling__get_profiled_columns/"><code>fabricops_kit.data_profiling._get_profiled_columns</code></a>
- <a href="../internal/data_profiling__is_min_max_supported_type/"><code>fabricops_kit.data_profiling._is_min_max_supported_type</code></a>
