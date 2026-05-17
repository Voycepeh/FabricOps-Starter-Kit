# `data_lineage` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-table-scroll">
| Callable count | Internal helper count | Outbound references | Inbound references |
|---:|---:|---:|---:|
| 2 | 13 | 0 | 0 |
</div>

## Module purpose

Owns source-to-target lineage and transformation evidence.

## Public callables

<div class="module-table-scroll">
| Callable | Tier | Type | Summary | Related helpers |
|---|---|---|---|---|
| [`build_lineage_handover_markdown`](../../reference/build_lineage_handover_markdown/) | Essential | function | Build a concise markdown handover summary from lineage execution results. | — |
| [`build_lineage_records`](../../reference/build_lineage_records/) | Essential | function | Build compact lineage records for downstream metadata sinks. | — |
</div>

## Advanced dependency sections


### Related internal helpers

<details>
<summary>Expand internal helper table</summary>

<div class="module-table-scroll">
| Helper | Related public callables |
|---|---|
| [`_build_lineage_record_from_steps`](../../reference/internal/data_lineage/_build_lineage_record_from_steps/) | — |
| [`_build_lineage_records`](../../reference/internal/data_lineage/_build_lineage_records/) | — |
| [`_call_name`](../../reference/internal/data_lineage/_call_name/) | — |
| [`_enrich_lineage_steps_with_ai`](../../reference/internal/data_lineage/_enrich_lineage_steps_with_ai/) | — |
| [`_fallback_copilot_lineage_prompt`](../../reference/internal/data_lineage/_fallback_copilot_lineage_prompt/) | — |
| [`_flatten_chain`](../../reference/internal/data_lineage/_flatten_chain/) | — |
| [`_literal`](../../reference/internal/data_lineage/_literal/) | — |
| [`_name`](../../reference/internal/data_lineage/_name/) | — |
| [`_resolve_write_target`](../../reference/internal/data_lineage/_resolve_write_target/) | — |
| [`_scan_notebook_cells`](../../reference/internal/data_lineage/_scan_notebook_cells/) | — |
| [`_scan_notebook_lineage`](../../reference/internal/data_lineage/_scan_notebook_lineage/) | — |
| [`_step`](../../reference/internal/data_lineage/_step/) | — |
| [`_validate_lineage_steps`](../../reference/internal/data_lineage/_validate_lineage_steps/) | — |
</div>

</details>

### Module internal callable dependencies

<details>
<summary>Expand module internal callable graph</summary>

<div class="module-mermaid-scroll">
```mermaid
flowchart LR
  n1["data_lineage._build_lineage_record_from_steps"] --> n1b["data_lineage._validate_lineage_steps"]
  n2["data_lineage._build_lineage_records"] --> n2b["data_lineage._build_lineage_record_from_steps"]
  n3["data_lineage._enrich_lineage_steps_with_ai"] --> n3b["data_lineage._fallback_copilot_lineage_prompt"]
  n4["data_lineage._flatten_chain"] --> n4b["data_lineage._name"]
  n5["data_lineage._resolve_write_target"] --> n5b["data_lineage._literal"]
  n6["data_lineage._scan_notebook_cells"] --> n6b["data_lineage._scan_notebook_lineage"]
  n7["data_lineage._scan_notebook_lineage"] --> n7b["data_lineage._call_name"]
  n8["data_lineage._scan_notebook_lineage"] --> n8b["data_lineage._flatten_chain"]
  n9["data_lineage._scan_notebook_lineage"] --> n9b["data_lineage._name"]
  n10["data_lineage._scan_notebook_lineage"] --> n10b["data_lineage._resolve_write_target"]
  n11["data_lineage._scan_notebook_lineage"] --> n11b["data_lineage._step"]
```
</div>

</details>

### Cross-module references

No cross-module references detected.
