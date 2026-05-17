# `data_profiling` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-table-scroll">
| Callable count | Internal helper count | Outbound references | Inbound references |
|---:|---:|---:|---:|
| 1 | 2 | 1 | 1 |
</div>

## Module purpose

Owns deterministic profiling evidence such as schema, nulls, distincts, min/max, and samples.

## Public callables

<div class="module-table-scroll">
| Callable | Tier | Type | Summary | Related helpers |
|---|---|---|---|---|
| [`profile_dataframe`](../../reference/profile_dataframe/) | Essential | function | Build canonical DQ-ready profiling rows from a Spark DataFrame. | [`_get_profiled_columns`](../../reference/internal/data_profiling/_get_profiled_columns/) (internal), [`_is_min_max_supported_type`](../../reference/internal/data_profiling/_is_min_max_supported_type/) (internal) |
</div>

## Advanced dependency sections


### Related internal helpers

<div class="module-table-scroll">
| Helper | Related public callables |
|---|---|
| [`_get_profiled_columns`](../../reference/internal/data_profiling/_get_profiled_columns/) | [`profile_dataframe`](../../reference/profile_dataframe/) |
| [`_is_min_max_supported_type`](../../reference/internal/data_profiling/_is_min_max_supported_type/) | [`profile_dataframe`](../../reference/profile_dataframe/) |
</div>

### Module internal callable dependencies

<div class="module-mermaid-scroll">
```mermaid
flowchart LR
  n1["data_profiling.profile_dataframe"] --> n1b["data_profiling._get_profiled_columns"]
  n2["data_profiling.profile_dataframe"] --> n2b["data_profiling._is_min_max_supported_type"]
```
</div>

### Cross-module references

Graph omitted because dependencies are simple one-to-one references.
<div class="module-table-scroll">
| Caller | Callee |
|---|---|
| `data_profiling._get_profiled_columns` | `technical_columns._default_technical_columns` |
</div>
