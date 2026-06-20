# `data_lineage` module (internal)

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 0</span><span class="reference-chip">Internal helpers: 2</span><span class="reference-chip">Uses 1 external module</span><span class="reference-chip">Used by 0 external modules</span></div>

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
      <td>0</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>2</td>
    </tr>
    <tr>
      <td>Used by external module count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Uses external module count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>External modules using this module</td>
      <td>—</td>
    </tr>
    <tr>
      <td>External modules this module uses</td>
      <td><code>config</code></td>
    </tr>
  </tbody>
</table>

## Public callables

No public exports in this module.

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>data_lineage</h5>
<h6>Public callables</h6>
<p>None.</p>
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
      <td><code>_build_lineage_records</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_validate_lineage_steps</code></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<span class="reference-chip"><code>_build_lineage_records</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_validate_lineage_steps</code></span>
</li>
<li>
<span class="reference-chip"><code>_validate_lineage_steps</code></span>
</li>
</ul>
</details>

### External callers

None.
### External callees

**config**
<a class="reference-chip" href="config/#_current_audit_timestamp"><code>_current_audit_timestamp</code></a>
