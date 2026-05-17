# `data_lineage` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

| Essential | Optional | Internal | Depends On | Used By |
|---:|---:|---:|---:|---:|
| 2 | 0 | 13 | 0 | 0 |

## Essential callables

| Callable | Type | Summary | Related helpers |
|---|---|---|---|
| [`build_lineage_handover_markdown`](../../reference/build_lineage_handover_markdown/) | function | Build a concise markdown handover summary from lineage execution results. | — |
| [`build_lineage_records`](../../reference/build_lineage_records/) | function | Build compact lineage records for downstream metadata sinks. | — |

## Optional callables

No advanced helpers listed for this module.

## Related internal helpers

<details>
<summary>Expand internal helper table</summary>

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

</details>

## Module internal callable graph

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

## Cross-module callable graph

```mermaid
flowchart LR
  no_cross_edges[No cross-module callable edges detected]
```

## Cross-module references

No cross-module references detected.
