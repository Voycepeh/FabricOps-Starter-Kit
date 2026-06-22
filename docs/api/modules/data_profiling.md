# `data_profiling` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 1</span><span class="reference-chip">Internal helpers: 0</span><span class="reference-chip">Uses 1 external module</span><span class="reference-chip">Used by 3 external modules</span></div>

## Module purpose

Owns deterministic profiling evidence such as schema, nulls, distincts, min/max, and optional lightweight distributions.

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
      <td><code>data_profiling</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns deterministic profiling evidence such as schema, nulls, distincts, min/max, and optional lightweight distributions.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Used by external module count</td>
      <td>3</td>
    </tr>
    <tr>
      <td>Uses external module count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>External modules using this module</td>
      <td><code>governance_review</code>, <code>guardrails</code>, <code>pipeline</code></td>
    </tr>
    <tr>
      <td>External modules this module uses</td>
      <td><code>_profiling_workflows</code></td>
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
      <td><a href="../reference/profile_dataframe/"><code>profile_dataframe</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Profile a source or target DataFrame for schema, quality, and catalogue evidence.</td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>data_profiling</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../reference/profile_dataframe/"><code>profile_dataframe</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>profile_dataframe_core</code></span>
</li>
</ul>
</section>

### Related internal helpers

No module-level internal helpers detected.

### External callers

**governance_review**
<a class="reference-chip" href="governance_review/#_prepare_dq_profile_input_rows"><code>_prepare_dq_profile_input_rows</code></a>

**guardrails**
<a class="reference-chip" href="guardrails/#enforce_profile_behavior"><code>enforce_profile_behavior</code></a>

**pipeline**
<a class="reference-chip" href="pipeline/#_run_table_guardrails_workflow"><code>_run_table_guardrails_workflow</code></a>

### External callees

**_profiling_workflows**
<a class="reference-chip" href="_profiling_workflows/#profile_dataframe_core"><code>profile_dataframe_core</code></a>
