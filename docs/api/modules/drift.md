# `drift` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 9</span><span class="reference-chip">Internal helpers: 19</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 0</span></div>

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
      <td>9</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>19</td>
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
      <td><a href="../../reference/check_schema/"><code>check_schema</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Check a dataframe has the expected pipeline-local columns and datatypes before continuing.</td>
      <td><a href="../../reference/internal/drift/_actual_schema/"><code>_actual_schema</code></a> (internal), <a href="../../reference/internal/drift/_normalize_datatype/"><code>_normalize_datatype</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/assert_no_blocking_profile_drift/"><code>assert_no_blocking_profile_drift</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Raise when profile drift check results should block notebook execution.</td>
      <td>—</td>
    </tr>
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
      <td><a href="../../reference/internal/drift/_categorical_distance/"><code>_categorical_distance</code></a> (internal), <a href="../../reference/internal/drift/_normalize_profile/"><code>_normalize_profile</code></a> (internal), <a href="../../reference/internal/drift/_numeric_psi/"><code>_numeric_psi</code></a> (internal), <a href="../../reference/internal/drift/_profile_check_status/"><code>_profile_check_status</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/default_profile_drift_policy/"><code>default_profile_drift_policy</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Return lightweight default thresholds for profile-based data drift checks.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/extract_numeric_distribution_bin_edges/"><code>extract_numeric_distribution_bin_edges</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Extract baseline numeric bin edges so current profiles can produce comparable PSI distributions.</td>
      <td><a href="../../reference/internal/drift/_normalize_profile/"><code>_normalize_profile</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/load_latest_profile/"><code>load_latest_profile</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Load the latest previous successful source or target profile from existing profile metadata.</td>
      <td><a href="../../reference/internal/drift/_is_missing_table_error/"><code>_is_missing_table_error</code></a> (internal), <a href="../../reference/internal/drift/_normalize_profile/"><code>_normalize_profile</code></a> (internal), <a href="../../reference/internal/drift/_safe_spark_collect/"><code>_safe_spark_collect</code></a> (internal)</td>
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
<a class="reference-chip" href="../../reference/assert_no_blocking_profile_drift/"><code>assert_no_blocking_profile_drift</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/check_partition_drift/"><code>check_partition_drift</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#build_partition_snapshot"><code>build_partition_snapshot</code></a>, <a class="reference-chip" href="#compare_partition_snapshots"><code>compare_partition_snapshots</code></a>, <a class="reference-chip" href="#default_incremental_safety_policy"><code>default_incremental_safety_policy</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/check_profile_drift/"><code>check_profile_drift</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_categorical_distance"><code>_categorical_distance</code></a>, <a class="reference-chip" href="#_normalize_profile"><code>_normalize_profile</code></a>, <a class="reference-chip" href="#_numeric_psi"><code>_numeric_psi</code></a>, <a class="reference-chip" href="#_profile_check_status"><code>_profile_check_status</code></a>, <a class="reference-chip" href="../../reference/default_profile_drift_policy/"><code>default_profile_drift_policy</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/check_schema/"><code>check_schema</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_actual_schema"><code>_actual_schema</code></a>, <a class="reference-chip" href="#_normalize_datatype"><code>_normalize_datatype</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/default_profile_drift_policy/"><code>default_profile_drift_policy</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/extract_numeric_distribution_bin_edges/"><code>extract_numeric_distribution_bin_edges</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_normalize_profile"><code>_normalize_profile</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/load_latest_profile/"><code>load_latest_profile</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_is_missing_table_error"><code>_is_missing_table_error</code></a>, <a class="reference-chip" href="#_normalize_profile"><code>_normalize_profile</code></a>, <a class="reference-chip" href="#_safe_spark_collect"><code>_safe_spark_collect</code></a>
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
      <td><a href="../../reference/internal/drift/_actual_schema/"><code>_actual_schema</code></a></td>
      <td><a href="../../reference/check_schema/"><code>check_schema</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_build_pandas_partition_snapshot/"><code>_build_pandas_partition_snapshot</code></a></td>
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
      <td><a href="../../reference/internal/drift/_categorical_distance/"><code>_categorical_distance</code></a></td>
      <td><a href="../../reference/check_profile_drift/"><code>check_profile_drift</code></a></td>
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
      <td><a href="../../reference/load_latest_profile/"><code>load_latest_profile</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_json_dumps/"><code>_json_dumps</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_normalize_datatype/"><code>_normalize_datatype</code></a></td>
      <td><a href="../../reference/check_schema/"><code>check_schema</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_normalize_profile/"><code>_normalize_profile</code></a></td>
      <td><a href="../../reference/check_profile_drift/"><code>check_profile_drift</code></a>, <a href="../../reference/extract_numeric_distribution_bin_edges/"><code>extract_numeric_distribution_bin_edges</code></a>, <a href="../../reference/load_latest_profile/"><code>load_latest_profile</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_numeric_psi/"><code>_numeric_psi</code></a></td>
      <td><a href="../../reference/check_profile_drift/"><code>check_profile_drift</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_parse_distribution/"><code>_parse_distribution</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_profile_check_status/"><code>_profile_check_status</code></a></td>
      <td><a href="../../reference/check_profile_drift/"><code>check_profile_drift</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_proportions/"><code>_proportions</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_row_get/"><code>_row_get</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_safe_spark_collect/"><code>_safe_spark_collect</code></a></td>
      <td><a href="../../reference/load_latest_profile/"><code>load_latest_profile</code></a></td>
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
<a class="reference-chip" href="#_actual_schema"><code>_actual_schema</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_normalize_datatype"><code>_normalize_datatype</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_pandas_partition_snapshot"><code>_build_pandas_partition_snapshot</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_build_partition_hash"><code>_build_partition_hash</code></a>, <a class="reference-chip" href="#_hash"><code>_hash</code></a>
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
<a class="reference-chip" href="#_categorical_distance"><code>_categorical_distance</code></a>
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
<a class="reference-chip" href="#_normalize_datatype"><code>_normalize_datatype</code></a>
</li>
<li>
<a class="reference-chip" href="#_normalize_profile"><code>_normalize_profile</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_normalize_profile"><code>_normalize_profile</code></a>, <a class="reference-chip" href="#_parse_distribution"><code>_parse_distribution</code></a>, <a class="reference-chip" href="#_row_get"><code>_row_get</code></a>
</li>
<li>
<a class="reference-chip" href="#_numeric_psi"><code>_numeric_psi</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_proportions"><code>_proportions</code></a>
</li>
<li>
<a class="reference-chip" href="#_parse_distribution"><code>_parse_distribution</code></a>
</li>
<li>
<a class="reference-chip" href="#_profile_check_status"><code>_profile_check_status</code></a>
</li>
<li>
<a class="reference-chip" href="#_proportions"><code>_proportions</code></a>
</li>
<li>
<a class="reference-chip" href="#_row_get"><code>_row_get</code></a>
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
