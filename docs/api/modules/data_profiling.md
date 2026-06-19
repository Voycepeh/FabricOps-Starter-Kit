# `data_profiling` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 1</span><span class="reference-chip">Internal helpers: 6</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 3</span></div>

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
      <td>6</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>3</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td><code>governance_review</code>, <code>guardrails</code>, <code>pipeline</code></td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>config</code></td>
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
      <td><code>_build_distribution_summaries</code> (internal), <code>_get_profiled_columns</code> (internal), <code>_is_min_max_supported_type</code> (internal)</td>
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
<span class="reference-chip"><code>_build_distribution_summaries</code></span>, <span class="reference-chip"><code>_get_profiled_columns</code></span>, <span class="reference-chip"><code>_is_min_max_supported_type</code></span>
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
      <td><code>_build_categorical_distribution</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_build_distribution_summaries</code></td>
      <td><a href="../reference/profile_dataframe/"><code>profile_dataframe</code></a></td>
    </tr>
    <tr>
      <td><code>_build_numeric_distribution</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_get_profiled_columns</code></td>
      <td><a href="../reference/profile_dataframe/"><code>profile_dataframe</code></a></td>
    </tr>
    <tr>
      <td><code>_is_min_max_supported_type</code></td>
      <td><a href="../reference/profile_dataframe/"><code>profile_dataframe</code></a></td>
    </tr>
    <tr>
      <td><code>_numeric_bin_edges</code></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<span class="reference-chip"><code>_build_categorical_distribution</code></span>
</li>
<li>
<span class="reference-chip"><code>_build_distribution_summaries</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_build_categorical_distribution</code></span>, <span class="reference-chip"><code>_build_numeric_distribution</code></span>, <span class="reference-chip"><code>_numeric_bin_edges</code></span>
</li>
<li>
<span class="reference-chip"><code>_build_numeric_distribution</code></span>
</li>
<li>
<span class="reference-chip"><code>_get_profiled_columns</code></span>
</li>
<li>
<span class="reference-chip"><code>_is_min_max_supported_type</code></span>
</li>
<li>
<span class="reference-chip"><code>_numeric_bin_edges</code></span>
</li>
</ul>
</details>

### External callers

**governance_review**
<a class="reference-chip" href="governance_review/#_prepare_dq_profile_input_rows"><code>_prepare_dq_profile_input_rows</code></a>

**guardrails**
<a class="reference-chip" href="guardrails/#enforce_profile_behavior"><code>enforce_profile_behavior</code></a>

**pipeline**
<a class="reference-chip" href="../reference/run_table_guardrails/">
<code>run_table_guardrails</code></a>

### External callees

**config**
<a class="reference-chip" href="config/#_audit_timestamp_expr"><code>_audit_timestamp_expr</code></a>, <a class="reference-chip" href="config/#_get_audit_timezone"><code>_get_audit_timezone</code></a>
