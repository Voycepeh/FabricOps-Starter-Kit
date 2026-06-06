# `handover` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 2</span><span class="reference-chip">Internal helpers: 2</span><span class="reference-chip">Outbound: 0</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns final handover assembly and notebook-friendly rendering/export.

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
      <td>Owns final handover assembly and notebook-friendly rendering/export.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>2</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>2</td>
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
      <td>Callable</td>
      <td>function</td>
      <td>Assemble final handover evidence for reviewed notebook work.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/render_handover_markdown/"><code>render_handover_markdown</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render handover evidence as notebook-friendly Markdown.</td>
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
      <td><a href="../../reference/internal/handover/_build_handover_record/"><code>_build_handover_record</code></a></td>
      <td>—</td>
    </tr>
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
<a class="reference-chip" href="#_build_handover_record"><code>_build_handover_record</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_status_of"><code>_status_of</code></a>, <a class="reference-chip" href="../../reference/render_handover_markdown/"><code>render_handover_markdown</code></a>
</li>
<li>
<a class="reference-chip" href="#_status_of"><code>_status_of</code></a>
</li>
</ul>
</details>

### External callers

None.
### External callees

None.
