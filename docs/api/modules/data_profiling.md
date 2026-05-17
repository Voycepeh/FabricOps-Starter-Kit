# `data_profiling` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

- **Essential:** 1
- **Optional:** 0
- **Internal:** 2
- **Depends On:** 1 modules
- **Used By:** 1 modules

## Essential callables

| Callable | Type | Summary | Related helpers |
|---|---|---|---|
| [`profile_dataframe`](../../reference/profile_dataframe/) | function | Build canonical DQ-ready profiling rows from a Spark DataFrame. | [`_get_profiled_columns`](../../reference/internal/data_profiling/_get_profiled_columns/) (internal), [`_is_min_max_supported_type`](../../reference/internal/data_profiling/_is_min_max_supported_type/) (internal) |

## Optional callables

No advanced helpers listed for this module.

## Related internal helpers

| Helper | Related public callables |
|---|---|
| [`_get_profiled_columns`](../../reference/internal/data_profiling/_get_profiled_columns/) | [`profile_dataframe`](../../reference/profile_dataframe/) |
| [`_is_min_max_supported_type`](../../reference/internal/data_profiling/_is_min_max_supported_type/) | [`profile_dataframe`](../../reference/profile_dataframe/) |

## Module internal callable graph

```mermaid
flowchart LR
  profile_dataframe --> _get_profiled_columns
  profile_dataframe --> _is_min_max_supported_type
```

## Cross-module callable graph

```mermaid
flowchart LR
  fabricops_kit_data_profiling__get_profiled_columns --> fabricops_kit_technical_columns__default_technical_columns
```
