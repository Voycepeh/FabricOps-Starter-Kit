# `metadata` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

| Essential | Optional | Internal | Depends On | Used By |
|---:|---:|---:|---:|---:|
| 2 | 0 | 8 | 1 | 3 |

## Essential callables

| Callable | Type | Summary | Related helpers |
|---|---|---|---|
| [`load_notebook_registry`](../../reference/load_notebook_registry/) | function | Load notebook registration metadata rows for agreement notebook traceability. | — |
| [`register_current_notebook`](../../reference/register_current_notebook/) | function | Register current notebook metadata evidence for agreement traceability. | [`_context_get`](../../reference/internal/metadata/_context_get/) (internal), [`_runtime_context`](../../reference/internal/metadata/_runtime_context/) (internal), [`_safe_str`](../../reference/internal/metadata/_safe_str/) (internal) |

## Optional callables

No advanced helpers listed for this module.

## Related internal helpers

| Helper | Related public callables |
|---|---|
| [`_context_get`](../../reference/internal/metadata/_context_get/) | [`register_current_notebook`](../../reference/register_current_notebook/) |
| [`_extract_columns_from_profile`](../../reference/internal/metadata/_extract_columns_from_profile/) | — |
| [`_key_part`](../../reference/internal/metadata/_key_part/) | — |
| [`_now_utc_iso`](../../reference/internal/metadata/_now_utc_iso/) | — |
| [`_resolve_action_by`](../../reference/internal/metadata/_resolve_action_by/) | — |
| [`_runtime_context`](../../reference/internal/metadata/_runtime_context/) | [`register_current_notebook`](../../reference/register_current_notebook/) |
| [`_safe_str`](../../reference/internal/metadata/_safe_str/) | [`register_current_notebook`](../../reference/register_current_notebook/) |
| [`_sha256_key`](../../reference/internal/metadata/_sha256_key/) | — |

## Module internal callable graph

```mermaid
flowchart LR
  n1["metadata._resolve_action_by"] --> n1b["metadata._context_get"]
  n2["metadata._resolve_action_by"] --> n2b["metadata._runtime_context"]
  n3["metadata._runtime_context"] --> n3b["metadata._context_get"]
  n4["metadata._sha256_key"] --> n4b["metadata._key_part"]
  n5["metadata.build_dq_rule_key"] --> n5b["metadata._sha256_key"]
  n6["metadata.build_evidence_row"] --> n6b["metadata._now_utc_iso"]
  n7["metadata.build_metadata_column_key"] --> n7b["metadata._sha256_key"]
  n8["metadata.build_metadata_table_key"] --> n8b["metadata._sha256_key"]
  n9["metadata.register_current_notebook"] --> n9b["metadata._context_get"]
  n10["metadata.register_current_notebook"] --> n10b["metadata._runtime_context"]
  n11["metadata.register_current_notebook"] --> n11b["metadata._safe_str"]
  n12["metadata.register_current_notebook"] --> n12b["metadata.write_metadata_rows"]
  n13["metadata.write_column_business_context"] --> n13b["metadata.write_metadata_rows"]
  n14["metadata.write_column_governance_context"] --> n14b["metadata.write_metadata_rows"]
  n15["metadata.write_metadata_rows"] --> n15b["metadata.column_context_rows_for_spark"]
```

## Cross-module callable graph

```mermaid
flowchart LR
  c1[metadata.write_metadata_rows] --> d1[fabric_input_output.write_lakehouse_table]
```

## Cross-module references

| Caller | Callee |
|---|---|
| `metadata.write_metadata_rows` | `fabric_input_output.write_lakehouse_table` |
