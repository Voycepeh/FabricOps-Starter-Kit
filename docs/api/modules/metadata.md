# `metadata` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-table-scroll">
| Callable count | Internal helper count | Outbound references | Inbound references |
|---:|---:|---:|---:|
| 2 | 8 | 1 | 3 |
</div>

## Module purpose

Owns metadata/contract store access, evidence persistence, agreement metadata, notebook evidence, and contract assembly inputs.

## Public callables

<div class="module-table-scroll">
| Callable | Tier | Type | Summary | Related helpers |
|---|---|---|---|---|
| [`load_notebook_registry`](../../reference/load_notebook_registry/) | Essential | function | Load notebook registration metadata rows for agreement notebook traceability. | — |
| [`register_current_notebook`](../../reference/register_current_notebook/) | Essential | function | Register current notebook metadata evidence for agreement traceability. | [`_context_get`](../../reference/internal/metadata/_context_get/) (internal), [`_runtime_context`](../../reference/internal/metadata/_runtime_context/) (internal), [`_safe_str`](../../reference/internal/metadata/_safe_str/) (internal) |
</div>

## Advanced dependency sections


### Related internal helpers

<div class="module-table-scroll">
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
</div>

### Module internal callable dependencies

<details>
<summary>Expand module internal callable graph</summary>

<div class="module-mermaid-scroll">
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
</div>

</details>

### Cross-module references

Graph omitted because dependencies are simple one-to-one references.
<div class="module-table-scroll">
| Caller | Callee |
|---|---|
| `metadata.write_metadata_rows` | `fabric_input_output.write_lakehouse_table` |
</div>
