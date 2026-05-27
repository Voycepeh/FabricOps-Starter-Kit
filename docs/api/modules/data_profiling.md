# `data_profiling` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 1</span><span class="reference-chip">Internal helpers: 2</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 1</span></div>

## Module purpose

Owns deterministic profiling evidence such as schema, nulls, distincts, min/max, and samples.

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
      <td>Owns deterministic profiling evidence such as schema, nulls, distincts, min/max, and samples.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>2</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td><code>data_quality</code></td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>technical_columns</code></td>
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
      <td>Build canonical DQ-ready profiling rows from a Spark DataFrame.</td>
      <td><a href="../../reference/internal/data_profiling/_get_profiled_columns/"><code>_get_profiled_columns</code></a> (internal), <a href="../../reference/internal/data_profiling/_is_min_max_supported_type/"><code>_is_min_max_supported_type</code></a> (internal)</td>
    </tr>
  </tbody>
</table>
</div>

## Module relationships


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
      <td><a href="../../reference/internal/data_profiling/_get_profiled_columns/"><code>_get_profiled_columns</code></a></td>
      <td><a href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_profiling/_is_min_max_supported_type/"><code>_is_min_max_supported_type</code></a></td>
      <td><a href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a></td>
    </tr>
  </tbody>
</table>
</div>

</details>

### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>data_profiling</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="#_get_profiled_columns"><code>_get_profiled_columns</code></a>, <a class="reference-chip" href="#_is_min_max_supported_type"><code>_is_min_max_supported_type</code></a>
</li>
</ul>
<details>
<summary>Internal helpers details</summary>
<h6>Internal helpers</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_get_profiled_columns"><code>_get_profiled_columns</code></a>
</li>
<li>
<a class="reference-chip" href="#_is_min_max_supported_type"><code>_is_min_max_supported_type</code></a>
</li>
</ul>
</details>
</section>

### External callers

**data_quality**
<a class="reference-chip" href="../data_quality/#_prepare_dq_profile_input_rows"><code>_prepare_dq_profile_input_rows</code></a>

### External callees

**technical_columns**
<a class="reference-chip" href="../technical_columns/#_default_technical_columns"><code>_default_technical_columns</code></a>

