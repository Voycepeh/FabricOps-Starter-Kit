# `handover` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 2</span><span class="reference-chip">Internal helpers: 1</span><span class="reference-chip">Outbound: 0</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns generated maintainer-facing handover and contract narrative output.

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
      <td><code>handover</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns generated maintainer-facing handover and contract narrative output.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>2</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>1</td>
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

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>handover</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/build_handover/"><code>build_handover</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/render_handover_markdown/"><code>render_handover_markdown</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="#_status_of"><code>_status_of</code></a>
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
      <td><a href="../../reference/internal/handover/_status_of/"><code>_status_of</code></a></td>
      <td><a href="../../reference/render_handover_markdown/"><code>render_handover_markdown</code></a></td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_status_of"><code>_status_of</code></a>
</li>
</ul>
</details>

### External callers

None.
### External callees

None.
