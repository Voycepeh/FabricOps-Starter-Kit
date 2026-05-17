# `technical_columns` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-table-scroll">
| Callable count | Internal helper count | Outbound references | Inbound references |
|---:|---:|---:|---:|
| 1 | 10 | 0 | 1 |
</div>

## Module purpose

Owns standard output/audit columns for pipeline outputs.

## Public callables

<div class="module-table-scroll">
| Callable | Tier | Type | Summary | Related helpers |
|---|---|---|---|---|
| [`standardize_columns`](../../reference/standardize_columns/) | Essential | function | Apply canonical technical/audit enrichment in one notebook-facing wrapper. | — |
</div>

## Advanced dependency sections


### Related internal helpers

<details>
<summary>Expand internal helper table</summary>

<div class="module-table-scroll">
| Helper | Related public callables |
|---|---|
| [`__add_audit_columns`](../../reference/internal/technical_columns/__add_audit_columns/) | — |
| [`__add_datetime_features`](../../reference/internal/technical_columns/__add_datetime_features/) | — |
| [`__add_hash_columns`](../../reference/internal/technical_columns/__add_hash_columns/) | — |
| [`_assert_columns_exist`](../../reference/internal/technical_columns/_assert_columns_exist/) | — |
| [`_bucket_values_pandas`](../../reference/internal/technical_columns/_bucket_values_pandas/) | — |
| [`_default_technical_columns`](../../reference/internal/technical_columns/_default_technical_columns/) | — |
| [`_get_fabric_runtime_context`](../../reference/internal/technical_columns/_get_fabric_runtime_context/) | — |
| [`_hash_row`](../../reference/internal/technical_columns/_hash_row/) | — |
| [`_non_technical_columns`](../../reference/internal/technical_columns/_non_technical_columns/) | — |
| [`_safe_string`](../../reference/internal/technical_columns/_safe_string/) | — |
</div>

</details>

### Module internal callable dependencies

<details>
<summary>Expand module internal callable graph</summary>

<div class="module-mermaid-scroll">
```mermaid
flowchart LR
  n1["technical_columns.__add_audit_columns"] --> n1b["technical_columns._assert_columns_exist"]
  n2["technical_columns.__add_audit_columns"] --> n2b["technical_columns._bucket_values_pandas"]
  n3["technical_columns.__add_audit_columns"] --> n3b["technical_columns._get_fabric_runtime_context"]
  n4["technical_columns.__add_datetime_features"] --> n4b["technical_columns._assert_columns_exist"]
  n5["technical_columns.__add_hash_columns"] --> n5b["technical_columns._assert_columns_exist"]
  n6["technical_columns.__add_hash_columns"] --> n6b["technical_columns._hash_row"]
  n7["technical_columns.__add_hash_columns"] --> n7b["technical_columns._non_technical_columns"]
  n8["technical_columns._bucket_values_pandas"] --> n8b["technical_columns._safe_string"]
  n9["technical_columns._hash_row"] --> n9b["technical_columns._safe_string"]
  n10["technical_columns._non_technical_columns"] --> n10b["technical_columns._default_technical_columns"]
```
</div>

</details>

### Cross-module references

No cross-module references detected.
