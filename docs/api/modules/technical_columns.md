# `technical_columns` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-summary-cards"><span class="reference-chip">Callable count: 1</span><span class="reference-chip">Outbound: 0</span><span class="reference-chip">Inbound: 1</span></div>

## Module purpose

Owns standard output/audit columns for pipeline outputs.

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
      <td><a href="../../reference/standardize_columns/"><code>standardize_columns</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Apply canonical technical/audit enrichment in one notebook-facing wrapper.</td>
      <td><a href="../../reference/internal/technical_columns/_add_audit_columns/"><code>_add_audit_columns</code></a> (internal), <a href="../../reference/internal/technical_columns/_add_datetime_features/"><code>_add_datetime_features</code></a> (internal), <a href="../../reference/internal/technical_columns/_add_hash_columns/"><code>_add_hash_columns</code></a> (internal)</td>
    </tr>
  </tbody>
</table>
</div>

## Advanced dependency sections


### Related internal helpers

<details>
<summary>Expand internal helper table</summary>

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
      <td><a href="../../reference/internal/technical_columns/_add_audit_columns/"><code>_add_audit_columns</code></a></td>
      <td><a href="../../reference/standardize_columns/"><code>standardize_columns</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_add_datetime_features/"><code>_add_datetime_features</code></a></td>
      <td><a href="../../reference/standardize_columns/"><code>standardize_columns</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_add_hash_columns/"><code>_add_hash_columns</code></a></td>
      <td><a href="../../reference/standardize_columns/"><code>standardize_columns</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_assert_columns_exist/"><code>_assert_columns_exist</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_bucket_values_pandas/"><code>_bucket_values_pandas</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_default_technical_columns/"><code>_default_technical_columns</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_get_fabric_runtime_context/"><code>_get_fabric_runtime_context</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_hash_row/"><code>_hash_row</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_non_technical_columns/"><code>_non_technical_columns</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/technical_columns/_safe_string/"><code>_safe_string</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

</details>

### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>technical_columns</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/standardize_columns/"><code>standardize_columns</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="../modules/technical_columns/#_add_audit_columns"><code>_add_audit_columns</code></a>, <a class="reference-chip" href="../modules/technical_columns/#_add_datetime_features"><code>_add_datetime_features</code></a>, <a class="reference-chip" href="../modules/technical_columns/#_add_hash_columns"><code>_add_hash_columns</code></a>
</li>
</ul>
<h6>Internal helpers</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../modules/technical_columns/#_add_audit_columns"><code>_add_audit_columns</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="../modules/technical_columns/#_assert_columns_exist"><code>_assert_columns_exist</code></a>, <a class="reference-chip" href="../modules/technical_columns/#_bucket_values_pandas"><code>_bucket_values_pandas</code></a>, <a class="reference-chip" href="../modules/technical_columns/#_get_fabric_runtime_context"><code>_get_fabric_runtime_context</code></a>
</li>
<li>
<a class="reference-chip" href="../modules/technical_columns/#_add_datetime_features"><code>_add_datetime_features</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="../modules/technical_columns/#_assert_columns_exist"><code>_assert_columns_exist</code></a>
</li>
<li>
<a class="reference-chip" href="../modules/technical_columns/#_add_hash_columns"><code>_add_hash_columns</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="../modules/technical_columns/#_assert_columns_exist"><code>_assert_columns_exist</code></a>, <a class="reference-chip" href="../modules/technical_columns/#_hash_row"><code>_hash_row</code></a>, <a class="reference-chip" href="../modules/technical_columns/#_non_technical_columns"><code>_non_technical_columns</code></a>
</li>
<li>
<a class="reference-chip" href="../modules/technical_columns/#_assert_columns_exist"><code>_assert_columns_exist</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../modules/technical_columns/#_bucket_values_pandas"><code>_bucket_values_pandas</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="../modules/technical_columns/#_safe_string"><code>_safe_string</code></a>
</li>
<li>
<a class="reference-chip" href="../modules/technical_columns/#_default_technical_columns"><code>_default_technical_columns</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../modules/technical_columns/#_get_fabric_runtime_context"><code>_get_fabric_runtime_context</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../modules/technical_columns/#_hash_row"><code>_hash_row</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="../modules/technical_columns/#_safe_string"><code>_safe_string</code></a>
</li>
<li>
<a class="reference-chip" href="../modules/technical_columns/#_non_technical_columns"><code>_non_technical_columns</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<a class="reference-chip" href="../modules/technical_columns/#_default_technical_columns"><code>_default_technical_columns</code></a>
</li>
<li>
<a class="reference-chip" href="../modules/technical_columns/#_safe_string"><code>_safe_string</code></a>
 <span class="callable-relationship-uses">uses:</span> 
<span>None.</span>
</li>
</ul>
</section>

#### External callers

**data_profiling**
<a class="reference-chip" href="../modules/data_profiling/#_get_profiled_columns"><code>_get_profiled_columns</code></a>

#### External callees

None.
