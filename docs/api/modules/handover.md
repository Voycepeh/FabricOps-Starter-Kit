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

### Callable relationships

<div class="module-mermaid-scroll module-diagram-desktop">
```mermaid
flowchart TB
  classDef currentModule fill:#ffe8cc,stroke:#e65100,stroke-width:4px,color:#3e2723;
  classDef externalModule fill:#f7f7f7,stroke:#b0bec5,stroke-width:1px,color:#607d8b;
  classDef currentCallable fill:#ffd180,stroke:#ef6c00,stroke-width:2px;
  classDef externalCallable fill:#eceff1,stroke:#b0bec5,stroke-width:1px,color:#455a64;
  subgraph m_handover[handover]
    fabricops_kit_handover__status_of["_status_of"]
    fabricops_kit_handover_build_handover_record["build_handover_record"]
    fabricops_kit_handover_render_handover_markdown["render_handover_markdown"]
  end
  fabricops_kit_handover_build_handover_record --> fabricops_kit_handover__status_of
  fabricops_kit_handover_build_handover_record --> fabricops_kit_handover_render_handover_markdown
  fabricops_kit_handover_render_handover_markdown --> fabricops_kit_handover__status_of
  linkStyle 0,1,2 stroke:#ef6c00,stroke-width:2.2px;
  class m_handover currentModule;
  class fabricops_kit_handover__status_of,fabricops_kit_handover_build_handover_record,fabricops_kit_handover_render_handover_markdown currentCallable;
```
</div>

<div class="module-relationship-list module-diagram-mobile">
#### Inside this module

<div class="callable-chip-group">
<a class="reference-chip" href="../modules/handover/#build_handover_record"><code>build_handover_record</code></a> → <a class="reference-chip" href="../modules/handover/#_status_of"><code>_status_of</code></a>
<a class="reference-chip" href="../modules/handover/#build_handover_record"><code>build_handover_record</code></a> → <a class="reference-chip" href="../../reference/render_handover_markdown/"><code>render_handover_markdown</code></a>
<a class="reference-chip" href="../../reference/render_handover_markdown/"><code>render_handover_markdown</code></a> → <a class="reference-chip" href="../modules/handover/#_status_of"><code>_status_of</code></a>
</div>
#### Used by other modules

None.
#### Uses other modules

None.
</div>
