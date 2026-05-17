# `technical_columns` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

- **Essential:** 1
- **Optional:** 0
- **Internal:** 10
- **Depends On:** 0 modules
- **Used By:** 1 modules

## Essential callables

| Callable | Type | Summary | Related helpers |
|---|---|---|---|
| [`standardize_columns`](../../reference/standardize_columns/) | function | Apply canonical technical/audit enrichment in one notebook-facing wrapper. | — |

## Optional callables

No advanced helpers listed for this module.

## Related internal helpers

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

## Module internal callable graph

```mermaid
flowchart LR
  _non_technical_columns --> _default_technical_columns
  _hash_row --> _safe_string
  _bucket_values_pandas --> _safe_string
  __add_datetime_features --> _assert_columns_exist
  __add_audit_columns --> _get_fabric_runtime_context
  __add_audit_columns --> _assert_columns_exist
  __add_audit_columns --> _assert_columns_exist
  __add_audit_columns --> _bucket_values_pandas
  __add_hash_columns --> _assert_columns_exist
  __add_hash_columns --> _assert_columns_exist
  __add_hash_columns --> _non_technical_columns
  __add_hash_columns --> _hash_row
  __add_hash_columns --> _hash_row
```

## Cross-module callable graph

```mermaid
flowchart LR
  no_cross_edges[No cross-module callable edges detected]
```
