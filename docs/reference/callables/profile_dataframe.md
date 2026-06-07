# profile_dataframe

**Module:** `data_profiling`  
**Classification:** Callable

## Status

Public callable helper intended for notebook authors.

## When to use this

Use to create schema, null, distinct, min/max, and optional distribution evidence from a Spark DataFrame.

## When not to use this

Do not use as a data-quality enforcement step or as a persistence helper; it builds profile rows but does not approve governance evidence.

## Quick example

profile_rows_df = profile_dataframe(df, table_name="orders", include_distributions=True, distribution_columns=["status"] )

## Signature

```python
def profile_dataframe(df, table_name: str, *, exclude_columns=None, run_timestamp_timezone='Asia/Singapore', include_distributions: bool=False, distribution_columns: list[str] | set[str] | tuple[str, ...] | None=None, distribution_bin_edges: dict[str, list[float]] | None=None, categorical_categories: dict[str, list[str]] | None=None, categorical_top_n: int=20)
```

## Parameters

df, table_name, optional exclude_columns, timezone, distribution options, bin edges, category baselines, and top-N settings.

## Returns

Spark DataFrame containing one profile row per eligible business column.

## Raises

Raises Spark/DataFrame errors when profiling expressions cannot be evaluated.

## Side effects

Computes profiling aggregations on the provided DataFrame; it does not write metadata, tables, or files.

## FabricOps context

Use after reading source/target data and before metadata persistence or governance review workflows that need profile evidence.

## AI implementation contract

- **required_context:** Use after reading source/target data and before metadata persistence or governance review workflows that need profile evidence.
- **inputs:** df, table_name, optional exclude_columns, timezone, distribution options, bin edges, category baselines, and top-N settings.
- **output:** Spark DataFrame containing one profile row per eligible business column.
- **side_effects:** Computes profiling aggregations on the provided DataFrame; it does not write metadata, tables, or files.
- **failure_modes:** Raises Spark/DataFrame errors when profiling expressions cannot be evaluated.
- **verification:** Verify the profile row count matches expected business columns and inspect key schema/profile fields before writing evidence.

## Related functions

- <a href="../monitor_data_changes/"><code>fabricops_kit.drift.monitor_data_changes</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

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
