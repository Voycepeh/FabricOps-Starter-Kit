# `data_profiling` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-summary-cards"><span class="reference-chip">Callable count: 1</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 1</span></div>

## Module purpose

Owns deterministic profiling evidence such as schema, nulls, distincts, min/max, and samples.

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

## Advanced dependency sections


### Related internal helpers

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

### Callable relationships

<p><a href="../../reference/call-graph/?module=fabricops_kit.data_profiling" class="md-button md-button--primary">Open interactive module graph</a></p>

#### Inside this module

<section class="callable-relationship-card">
<h5>data_profiling</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="../modules/data_profiling/#_get_profiled_columns"><code>_get_profiled_columns</code></a>, <a class="reference-chip" href="../modules/data_profiling/#_is_min_max_supported_type"><code>_is_min_max_supported_type</code></a>
</li>
</ul>
<h6>Internal helpers</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../modules/data_profiling/#_get_profiled_columns"><code>_get_profiled_columns</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../modules/data_profiling/#_is_min_max_supported_type"><code>_is_min_max_supported_type</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<span>None.</span>
</li>
</ul>
</section>

#### External callers

**data_quality**
<a class="reference-chip" href="../modules/data_quality/#_prepare_dq_profile_input_rows"><code>_prepare_dq_profile_input_rows</code></a>

#### External callees

**technical_columns**
<a class="reference-chip" href="../modules/technical_columns/#_default_technical_columns"><code>_default_technical_columns</code></a>

