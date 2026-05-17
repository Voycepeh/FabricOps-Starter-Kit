# `metadata` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

- **Essential:** 2
- **Optional:** 0
- **Internal:** 8
- **Depends On:** 1 modules
- **Used By:** 3 modules

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
  build_evidence_row --> _now_utc_iso
  _resolve_action_by --> _runtime_context
  _resolve_action_by --> _context_get
  _sha256_key --> _key_part
  build_metadata_table_key --> _sha256_key
  build_metadata_column_key --> _sha256_key
  build_dq_rule_key --> _sha256_key
  write_metadata_rows --> column_context_rows_for_spark
  write_column_business_context --> write_metadata_rows
  write_column_governance_context --> write_metadata_rows
  _runtime_context --> _context_get
  register_current_notebook --> _runtime_context
  register_current_notebook --> _context_get
  register_current_notebook --> _context_get
  register_current_notebook --> _context_get
  register_current_notebook --> _context_get
  register_current_notebook --> _context_get
  register_current_notebook --> write_metadata_rows
  register_current_notebook --> _context_get
  register_current_notebook --> _safe_str
  register_current_notebook --> _safe_str
  register_current_notebook --> _safe_str
  register_current_notebook --> _safe_str
  register_current_notebook --> _safe_str
  register_current_notebook --> _safe_str
  register_current_notebook --> _safe_str
  register_current_notebook --> _safe_str
  register_current_notebook --> _safe_str
  register_current_notebook --> _safe_str
  register_current_notebook --> _safe_str
  register_current_notebook --> _safe_str
  register_current_notebook --> _safe_str
  register_current_notebook --> _safe_str
```

## Cross-module callable graph

```mermaid
flowchart LR
  fabricops_kit_metadata_write_metadata_rows --> fabricops_kit_fabric_input_output_write_lakehouse_table
```
