# `data_profiling` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 1</span><span class="reference-chip">Internal helpers: 9</span><span class="reference-chip">Outbound: 0</span><span class="reference-chip">Inbound: 2</span></div>

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
      <td>9</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>2</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td><code>data_quality</code>, <code>drift</code></td>
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
      <td><a href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Profile a source or target DataFrame for schema, quality, and catalogue evidence.</td>
      <td><a href="../../reference/internal/data_profiling/_build_distribution_summaries/"><code>_build_distribution_summaries</code></a> (internal), <a href="../../reference/internal/data_profiling/_get_profiled_columns/"><code>_get_profiled_columns</code></a> (internal), <a href="../../reference/internal/data_profiling/_is_min_max_supported_type/"><code>_is_min_max_supported_type</code></a> (internal)</td>
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
<a class="reference-chip" href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_build_distribution_summaries"><code>_build_distribution_summaries</code></a>, <a class="reference-chip" href="#_get_profiled_columns"><code>_get_profiled_columns</code></a>, <a class="reference-chip" href="#_is_min_max_supported_type"><code>_is_min_max_supported_type</code></a>
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
      <td><a href="../../reference/internal/data_profiling/_build_categorical_distribution/"><code>_build_categorical_distribution</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_profiling/_build_distribution_summaries/"><code>_build_distribution_summaries</code></a></td>
      <td><a href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_profiling/_build_numeric_distribution/"><code>_build_numeric_distribution</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_profiling/_dedupe_edges/"><code>_dedupe_edges</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_profiling/_get_profiled_columns/"><code>_get_profiled_columns</code></a></td>
      <td><a href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_profiling/_is_categorical_type/"><code>_is_categorical_type</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_profiling/_is_min_max_supported_type/"><code>_is_min_max_supported_type</code></a></td>
      <td><a href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_profiling/_is_numeric_type/"><code>_is_numeric_type</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_profiling/_numeric_bin_edges/"><code>_numeric_bin_edges</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_build_categorical_distribution"><code>_build_categorical_distribution</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_distribution_summaries"><code>_build_distribution_summaries</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_build_categorical_distribution"><code>_build_categorical_distribution</code></a>, <a class="reference-chip" href="#_build_numeric_distribution"><code>_build_numeric_distribution</code></a>, <a class="reference-chip" href="#_is_categorical_type"><code>_is_categorical_type</code></a>, <a class="reference-chip" href="#_is_numeric_type"><code>_is_numeric_type</code></a>, <a class="reference-chip" href="#_numeric_bin_edges"><code>_numeric_bin_edges</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_numeric_distribution"><code>_build_numeric_distribution</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_dedupe_edges"><code>_dedupe_edges</code></a>
</li>
<li>
<a class="reference-chip" href="#_dedupe_edges"><code>_dedupe_edges</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_profiled_columns"><code>_get_profiled_columns</code></a>
</li>
<li>
<a class="reference-chip" href="#_is_categorical_type"><code>_is_categorical_type</code></a>
</li>
<li>
<a class="reference-chip" href="#_is_min_max_supported_type"><code>_is_min_max_supported_type</code></a>
</li>
<li>
<a class="reference-chip" href="#_is_numeric_type"><code>_is_numeric_type</code></a>
</li>
<li>
<a class="reference-chip" href="#_numeric_bin_edges"><code>_numeric_bin_edges</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_dedupe_edges"><code>_dedupe_edges</code></a>
</li>
</ul>
</details>

### External callers

**data_quality**
<a class="reference-chip" href="../data_quality/#_prepare_dq_profile_input_rows"><code>_prepare_dq_profile_input_rows</code></a>

**drift**
<a class="reference-chip" href="../../reference/monitor_data_changes/"><code>monitor_data_changes</code></a>

### External callees

None.
