# `drift` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 4</span><span class="reference-chip">Internal helpers: 14</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns schema/profile/data drift checks as engineering guardrails during pipeline runs.

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
      <td><code>drift</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns schema/profile/data drift checks as engineering guardrails during pipeline runs.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>4</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>14</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td>—</td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>_utils</code></td>
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
      <td><a href="../../reference/check_partition_drift/"><code>check_partition_drift</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Check partition-level drift using keys, partitions, and optional watermark baselines.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/check_profile_drift/"><code>check_profile_drift</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Compare profile metrics against a baseline profile and drift thresholds.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/check_schema_drift/"><code>check_schema_drift</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Compare a current dataframe schema against a baseline schema snapshot.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/summarize_drift_results/"><code>summarize_drift_results</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Summarize schema, partition, and profile drift outcomes into one decision.</td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>drift</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/check_partition_drift/"><code>check_partition_drift</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#build_partition_snapshot"><code>build_partition_snapshot</code></a>, <a class="reference-chip" href="#compare_partition_snapshots"><code>compare_partition_snapshots</code></a>, <a class="reference-chip" href="#default_incremental_safety_policy"><code>default_incremental_safety_policy</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/check_profile_drift/"><code>check_profile_drift</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/check_schema_drift/"><code>check_schema_drift</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#build_schema_snapshot"><code>build_schema_snapshot</code></a>, <a class="reference-chip" href="#compare_schema_snapshots"><code>compare_schema_snapshots</code></a>, <a class="reference-chip" href="#default_schema_drift_policy"><code>default_schema_drift_policy</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/summarize_drift_results/"><code>summarize_drift_results</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
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
      <td><a href="../../reference/internal/drift/_build_pandas_partition_snapshot/"><code>_build_pandas_partition_snapshot</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_build_pandas_schema_snapshot/"><code>_build_pandas_schema_snapshot</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_build_partition_hash/"><code>_build_partition_hash</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_build_spark_partition_snapshot/"><code>_build_spark_partition_snapshot</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_build_spark_schema_snapshot/"><code>_build_spark_schema_snapshot</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_column_hash/"><code>_column_hash</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_hash/"><code>_hash</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_is_closed_partition/"><code>_is_closed_partition</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_is_missing_table_error/"><code>_is_missing_table_error</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_json_dumps/"><code>_json_dumps</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_resolve_change_behavior/"><code>_resolve_change_behavior</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_safe_spark_collect/"><code>_safe_spark_collect</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_utc_now_iso/"><code>_utc_now_iso</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_write_metadata_rows/"><code>_write_metadata_rows</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_build_pandas_partition_snapshot"><code>_build_pandas_partition_snapshot</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_build_partition_hash"><code>_build_partition_hash</code></a>, <a class="reference-chip" href="#_hash"><code>_hash</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_pandas_schema_snapshot"><code>_build_pandas_schema_snapshot</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_column_hash"><code>_column_hash</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_partition_hash"><code>_build_partition_hash</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_hash"><code>_hash</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_spark_partition_snapshot"><code>_build_spark_partition_snapshot</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_build_partition_hash"><code>_build_partition_hash</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_spark_schema_snapshot"><code>_build_spark_schema_snapshot</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_column_hash"><code>_column_hash</code></a>
</li>
<li>
<a class="reference-chip" href="#_column_hash"><code>_column_hash</code></a>
</li>
<li>
<a class="reference-chip" href="#_hash"><code>_hash</code></a>
</li>
<li>
<a class="reference-chip" href="#_is_closed_partition"><code>_is_closed_partition</code></a>
</li>
<li>
<a class="reference-chip" href="#_is_missing_table_error"><code>_is_missing_table_error</code></a>
</li>
<li>
<a class="reference-chip" href="#_json_dumps"><code>_json_dumps</code></a>
</li>
<li>
<a class="reference-chip" href="#_resolve_change_behavior"><code>_resolve_change_behavior</code></a>
</li>
<li>
<a class="reference-chip" href="#_safe_spark_collect"><code>_safe_spark_collect</code></a>
</li>
<li>
<a class="reference-chip" href="#_utc_now_iso"><code>_utc_now_iso</code></a>
</li>
<li>
<a class="reference-chip" href="#_write_metadata_rows"><code>_write_metadata_rows</code></a>
</li>
</ul>
</details>

### External callers

None.
### External callees

**_utils**
<a class="reference-chip" href="../_utils/#_to_jsonable"><code>_to_jsonable</code></a>
