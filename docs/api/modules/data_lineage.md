# `data_lineage` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 2</span><span class="reference-chip">Internal helpers: 13</span><span class="reference-chip">Outbound: 0</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns source-to-target lineage and transformation evidence.

## Module manifest

<table>
  <thead>
    <tr>
      <th>Field</th>
      <th>Value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Module name</td>
      <td><code>data_lineage</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns source-to-target lineage and transformation evidence.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>2</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>13</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td>—</td>
    </tr>
    <tr>
      <td>External callees</td>
      <td>—</td>
    </tr>
  </tbody>
</table>

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

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>data_lineage</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/build_lineage_handover_markdown/"><code>build_lineage_handover_markdown</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/build_lineage_records/"><code>build_lineage_records</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<span>None.</span>
</li>
</ul>
</section>

### Related internal helpers

<details>
<summary>Show internal helpers</summary>

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

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_build_lineage_record_from_steps"><code>_build_lineage_record_from_steps</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="#_validate_lineage_steps"><code>_validate_lineage_steps</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_lineage_records"><code>_build_lineage_records</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="#_build_lineage_record_from_steps"><code>_build_lineage_record_from_steps</code></a>
</li>
<li>
<a class="reference-chip" href="#_call_name"><code>_call_name</code></a>
</li>
<li>
<a class="reference-chip" href="#_enrich_lineage_steps_with_ai"><code>_enrich_lineage_steps_with_ai</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="#_fallback_copilot_lineage_prompt"><code>_fallback_copilot_lineage_prompt</code></a>
</li>
<li>
<a class="reference-chip" href="#_fallback_copilot_lineage_prompt"><code>_fallback_copilot_lineage_prompt</code></a>
</li>
<li>
<a class="reference-chip" href="#_flatten_chain"><code>_flatten_chain</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="#_name"><code>_name</code></a>
</li>
<li>
<a class="reference-chip" href="#_literal"><code>_literal</code></a>
</li>
<li>
<a class="reference-chip" href="#_name"><code>_name</code></a>
</li>
<li>
<a class="reference-chip" href="#_resolve_write_target"><code>_resolve_write_target</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="#_literal"><code>_literal</code></a>
</li>
<li>
<a class="reference-chip" href="#_scan_notebook_cells"><code>_scan_notebook_cells</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="#_scan_notebook_lineage"><code>_scan_notebook_lineage</code></a>
</li>
<li>
<a class="reference-chip" href="#_scan_notebook_lineage"><code>_scan_notebook_lineage</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="#_call_name"><code>_call_name</code></a>, <a class="reference-chip" href="#_flatten_chain"><code>_flatten_chain</code></a>, <a class="reference-chip" href="#_name"><code>_name</code></a>, <a class="reference-chip" href="#_resolve_write_target"><code>_resolve_write_target</code></a>, <a class="reference-chip" href="#_step"><code>_step</code></a>
</li>
<li>
<a class="reference-chip" href="#_step"><code>_step</code></a>
</li>
<li>
<a class="reference-chip" href="#_validate_lineage_steps"><code>_validate_lineage_steps</code></a>
</li>
</ul>
</details>

### External callers

None.
### External callees

None.
