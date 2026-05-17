# `handover` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-summary-cards"><span class="reference-chip">Callable count: 2</span><span class="reference-chip">Outbound: 0</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns generated maintainer-facing handover and contract narrative output.

## Public callables

<div class="module-table-scroll">
<table>
  <thead>
    <tr>
      <th>Callable</th>
      <th>Tier</th>
      <th>Type</th>
      <th>Summary</th>
      <th>Related helpers</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="../../reference/build_handover/"><code>build_handover</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Build a handover-friendly summary for one data product run.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/render_handover_markdown/"><code>render_handover_markdown</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Render a handover summary dictionary into Markdown for handover notes.</td>
      <td><a href="../../reference/internal/handover/_status_of/"><code>_status_of</code></a> (internal)</td>
    </tr>
  </tbody>
</table>
</div>

## Advanced dependency sections


### Related internal helpers

<div class="module-table-scroll">
<table>
  <thead>
    <tr>
      <th>Helper</th>
      <th>Related public callables</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="../../reference/internal/handover/_status_of/"><code>_status_of</code></a></td>
      <td><a href="../../reference/render_handover_markdown/"><code>render_handover_markdown</code></a></td>
    </tr>
  </tbody>
</table>
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

### Outbound

No outbound references detected.
