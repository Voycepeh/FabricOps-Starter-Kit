# `handover` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

- **Essential:** 2
- **Optional:** 0
- **Internal:** 1
- **Depends On:** 0 modules
- **Used By:** 0 modules

## Essential callables

| Callable | Type | Summary | Related helpers |
|---|---|---|---|
| [`build_handover`](../../reference/build_handover/) | function | Build a handover-friendly summary for one data product run. | — |
| [`render_handover_markdown`](../../reference/render_handover_markdown/) | function | Render a handover summary dictionary into Markdown for handover notes. | [`_status_of`](../../reference/internal/handover/_status_of/) (internal) |

## Optional callables

No advanced helpers listed for this module.

## Related internal helpers

| Helper | Related public callables |
|---|---|
| [`_status_of`](../../reference/internal/handover/_status_of/) | [`render_handover_markdown`](../../reference/render_handover_markdown/) |

## Module internal callable graph

```mermaid
flowchart LR
  render_handover_markdown --> _status_of
  render_handover_markdown --> _status_of
  render_handover_markdown --> _status_of
  render_handover_markdown --> _status_of
  build_handover_record --> _status_of
  build_handover_record --> _status_of
  build_handover_record --> _status_of
  build_handover_record --> _status_of
  build_handover_record --> render_handover_markdown
```

## Cross-module callable graph

```mermaid
flowchart LR
  no_cross_edges[No cross-module callable edges detected]
```
