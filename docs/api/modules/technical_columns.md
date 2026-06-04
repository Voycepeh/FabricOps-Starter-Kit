# `technical_columns` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 2</span><span class="reference-chip">Internal helpers: 3</span><span class="reference-chip">Outbound: 0</span><span class="reference-chip">Inbound: 1</span></div>

## Module purpose

Owns lightweight runtime audit columns for pipeline outputs.

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
      <td><code>technical_columns</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns lightweight runtime audit columns for pipeline outputs.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>2</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>3</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td><code>data_profiling</code></td>
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
      <td><a href="../../reference/add_runtime_audit_columns/"><code>add_runtime_audit_columns</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Add lightweight runtime audit columns before writing pipeline output tables.</td>
      <td><a href="../../reference/internal/technical_columns/_context_value/"><code>_context_value</code></a> (internal), <a href="../../reference/internal/technical_columns/_get_fabric_runtime_context/"><code>_get_fabric_runtime_context</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/standardize_columns/"><code>standardize_columns</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Deprecated compatibility wrapper; use add_runtime_audit_columns for the standard runtime audit path.</td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>technical_columns</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/add_runtime_audit_columns/"><code>add_runtime_audit_columns</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_context_value"><code>_context_value</code></a>, <a class="reference-chip" href="#_get_fabric_runtime_context"><code>_get_fabric_runtime_context</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/standardize_columns/"><code>standardize_columns</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="../../reference/add_runtime_audit_columns/"><code>add_runtime_audit_columns</code></a>
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
      <td><a href="../../reference/internal/technical_columns/_context_value/"><code>_context_value</code></a></td>
      <td><a href="../../reference/add_runtime_audit_columns/"><code>add_runtime_audit_columns</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_default_technical_columns/"><code>_default_technical_columns</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_get_fabric_runtime_context/"><code>_get_fabric_runtime_context</code></a></td>
      <td><a href="../../reference/add_runtime_audit_columns/"><code>add_runtime_audit_columns</code></a></td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_context_value"><code>_context_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_default_technical_columns"><code>_default_technical_columns</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_fabric_runtime_context"><code>_get_fabric_runtime_context</code></a>
</li>
</ul>
</details>

### External callers

**data_profiling**
<a class="reference-chip" href="../data_profiling/#_get_profiled_columns"><code>_get_profiled_columns</code></a>

### External callees

None.
