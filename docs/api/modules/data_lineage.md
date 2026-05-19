# `data_lineage` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-summary-cards"><span class="reference-chip">Callable count: 2</span><span class="reference-chip">Outbound: 0</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns source-to-target lineage and transformation evidence.

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
      <td><a href="../../reference/build_lineage_handover_markdown/"><code>build_lineage_handover_markdown</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Build a concise markdown handover summary from lineage execution results.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/build_lineage_records/"><code>build_lineage_records</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Build compact lineage records for downstream metadata sinks.</td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

## Advanced dependency sections


### Related internal helpers

<details>
<summary>Expand internal helper table</summary>

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
      <td><a href="../../reference/internal/data_lineage/_build_lineage_record_from_steps/"><code>_build_lineage_record_from_steps</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_build_lineage_records/"><code>_build_lineage_records</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_call_name/"><code>_call_name</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_enrich_lineage_steps_with_ai/"><code>_enrich_lineage_steps_with_ai</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_fallback_copilot_lineage_prompt/"><code>_fallback_copilot_lineage_prompt</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_flatten_chain/"><code>_flatten_chain</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_literal/"><code>_literal</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_name/"><code>_name</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_resolve_write_target/"><code>_resolve_write_target</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_scan_notebook_cells/"><code>_scan_notebook_cells</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_scan_notebook_lineage/"><code>_scan_notebook_lineage</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_step/"><code>_step</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_lineage/_validate_lineage_steps/"><code>_validate_lineage_steps</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

</details>

### Callable relationships

<div class="module-mermaid-scroll module-diagram-desktop">
```mermaid
flowchart TB
  classDef currentModule fill:#ffe8cc,stroke:#e65100,stroke-width:4px,color:#3e2723;
  classDef externalModule fill:#f7f7f7,stroke:#b0bec5,stroke-width:1px,color:#607d8b;
  classDef currentCallable fill:#ffd180,stroke:#ef6c00,stroke-width:2px;
  classDef externalCallable fill:#eceff1,stroke:#b0bec5,stroke-width:1px,color:#455a64;
  subgraph m_data_lineage[data_lineage]
    fabricops_kit_data_lineage__build_lineage_record_from_steps["_build_lineage_record_from_steps"]
    fabricops_kit_data_lineage__build_lineage_records["_build_lineage_records"]
    fabricops_kit_data_lineage__call_name["_call_name"]
    fabricops_kit_data_lineage__enrich_lineage_steps_with_ai["_enrich_lineage_steps_with_ai"]
    fabricops_kit_data_lineage__fallback_copilot_lineage_prompt["_fallback_copilot_lineage_prompt"]
    fabricops_kit_data_lineage__flatten_chain["_flatten_chain"]
    fabricops_kit_data_lineage__literal["_literal"]
    fabricops_kit_data_lineage__name["_name"]
    fabricops_kit_data_lineage__resolve_write_target["_resolve_write_target"]
    fabricops_kit_data_lineage__scan_notebook_cells["_scan_notebook_cells"]
    fabricops_kit_data_lineage__scan_notebook_lineage["_scan_notebook_lineage"]
    fabricops_kit_data_lineage__step["_step"]
    fabricops_kit_data_lineage__validate_lineage_steps["_validate_lineage_steps"]
  end
  fabricops_kit_data_lineage__build_lineage_record_from_steps --> fabricops_kit_data_lineage__validate_lineage_steps
  fabricops_kit_data_lineage__build_lineage_records --> fabricops_kit_data_lineage__build_lineage_record_from_steps
  fabricops_kit_data_lineage__enrich_lineage_steps_with_ai --> fabricops_kit_data_lineage__fallback_copilot_lineage_prompt
  fabricops_kit_data_lineage__flatten_chain --> fabricops_kit_data_lineage__name
  fabricops_kit_data_lineage__resolve_write_target --> fabricops_kit_data_lineage__literal
  fabricops_kit_data_lineage__scan_notebook_cells --> fabricops_kit_data_lineage__scan_notebook_lineage
  fabricops_kit_data_lineage__scan_notebook_lineage --> fabricops_kit_data_lineage__call_name
  fabricops_kit_data_lineage__scan_notebook_lineage --> fabricops_kit_data_lineage__flatten_chain
  fabricops_kit_data_lineage__scan_notebook_lineage --> fabricops_kit_data_lineage__name
  fabricops_kit_data_lineage__scan_notebook_lineage --> fabricops_kit_data_lineage__resolve_write_target
  fabricops_kit_data_lineage__scan_notebook_lineage --> fabricops_kit_data_lineage__step
  linkStyle 0,1,2,3,4,5,6,7,8,9,10 stroke:#ef6c00,stroke-width:2.2px;
  class m_data_lineage currentModule;
  class fabricops_kit_data_lineage__build_lineage_record_from_steps,fabricops_kit_data_lineage__build_lineage_records,fabricops_kit_data_lineage__call_name,fabricops_kit_data_lineage__enrich_lineage_steps_with_ai,fabricops_kit_data_lineage__fallback_copilot_lineage_prompt,fabricops_kit_data_lineage__flatten_chain,fabricops_kit_data_lineage__literal,fabricops_kit_data_lineage__name,fabricops_kit_data_lineage__resolve_write_target,fabricops_kit_data_lineage__scan_notebook_cells,fabricops_kit_data_lineage__scan_notebook_lineage,fabricops_kit_data_lineage__step,fabricops_kit_data_lineage__validate_lineage_steps currentCallable;
```
</div>

<div class="module-relationship-list module-diagram-mobile">
#### Inside this module

<div class="callable-chip-group">
<a class="reference-chip" href="../modules/data_lineage/#_build_lineage_record_from_steps"><code>_build_lineage_record_from_steps</code></a> → <a class="reference-chip" href="../modules/data_lineage/#_validate_lineage_steps"><code>_validate_lineage_steps</code></a>
<a class="reference-chip" href="../modules/data_lineage/#_build_lineage_records"><code>_build_lineage_records</code></a> → <a class="reference-chip" href="../modules/data_lineage/#_build_lineage_record_from_steps"><code>_build_lineage_record_from_steps</code></a>
<a class="reference-chip" href="../modules/data_lineage/#_enrich_lineage_steps_with_ai"><code>_enrich_lineage_steps_with_ai</code></a> → <a class="reference-chip" href="../modules/data_lineage/#_fallback_copilot_lineage_prompt"><code>_fallback_copilot_lineage_prompt</code></a>
<a class="reference-chip" href="../modules/data_lineage/#_flatten_chain"><code>_flatten_chain</code></a> → <a class="reference-chip" href="../modules/data_lineage/#_name"><code>_name</code></a>
<a class="reference-chip" href="../modules/data_lineage/#_resolve_write_target"><code>_resolve_write_target</code></a> → <a class="reference-chip" href="../modules/data_lineage/#_literal"><code>_literal</code></a>
<a class="reference-chip" href="../modules/data_lineage/#_scan_notebook_cells"><code>_scan_notebook_cells</code></a> → <a class="reference-chip" href="../modules/data_lineage/#_scan_notebook_lineage"><code>_scan_notebook_lineage</code></a>
<a class="reference-chip" href="../modules/data_lineage/#_scan_notebook_lineage"><code>_scan_notebook_lineage</code></a> → <a class="reference-chip" href="../modules/data_lineage/#_call_name"><code>_call_name</code></a>
<a class="reference-chip" href="../modules/data_lineage/#_scan_notebook_lineage"><code>_scan_notebook_lineage</code></a> → <a class="reference-chip" href="../modules/data_lineage/#_flatten_chain"><code>_flatten_chain</code></a>
<a class="reference-chip" href="../modules/data_lineage/#_scan_notebook_lineage"><code>_scan_notebook_lineage</code></a> → <a class="reference-chip" href="../modules/data_lineage/#_name"><code>_name</code></a>
<a class="reference-chip" href="../modules/data_lineage/#_scan_notebook_lineage"><code>_scan_notebook_lineage</code></a> → <a class="reference-chip" href="../modules/data_lineage/#_resolve_write_target"><code>_resolve_write_target</code></a>
<a class="reference-chip" href="../modules/data_lineage/#_scan_notebook_lineage"><code>_scan_notebook_lineage</code></a> → <a class="reference-chip" href="../modules/data_lineage/#_step"><code>_step</code></a>
</div>
#### Used by other modules

None.
#### Uses other modules

None.
</div>
