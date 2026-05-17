# `handover` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-table-scroll">
| Callable count | Internal helper count | Outbound references | Inbound references |
|---:|---:|---:|---:|
| 2 | 1 | 0 | 0 |
</div>

## Module purpose

Owns generated maintainer-facing handover and contract narrative output.

## Public callables

<div class="module-table-scroll">
| Callable | Tier | Type | Summary | Related helpers |
|---|---|---|---|---|
| [`build_handover`](../../reference/build_handover/) | Essential | function | Build a handover-friendly summary for one data product run. | — |
| [`render_handover_markdown`](../../reference/render_handover_markdown/) | Essential | function | Render a handover summary dictionary into Markdown for handover notes. | [`_status_of`](../../reference/internal/handover/_status_of/) (internal) |
</div>

## Advanced dependency sections


### Related internal helpers

<div class="module-table-scroll">
| Helper | Related public callables |
|---|---|
| [`_status_of`](../../reference/internal/handover/_status_of/) | [`render_handover_markdown`](../../reference/render_handover_markdown/) |
</div>

### Module internal callable dependencies

<div class="module-mermaid-scroll">
```mermaid
flowchart LR
  n1["handover.build_handover_record"] --> n1b["handover._status_of"]
  n2["handover.build_handover_record"] --> n2b["handover.render_handover_markdown"]
  n3["handover.render_handover_markdown"] --> n3b["handover._status_of"]
```
</div>

### Cross-module references

No cross-module references detected.
