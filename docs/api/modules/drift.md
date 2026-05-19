# `drift` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module dependency summary

<div class="module-summary-cards"><span class="reference-chip">Callable count: 4</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns schema/profile/data drift checks as engineering guardrails during pipeline runs.

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

</details>

### Callable relationships

<div class="module-relationship-list">
#### Module relationships
#### Functions in this module

<div class="callable-chip-group">
<a class="reference-chip" href="../modules/drift/#_build_pandas_partition_snapshot"><code>_build_pandas_partition_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_build_partition_hash"><code>_build_partition_hash</code></a>
<a class="reference-chip" href="../modules/drift/#_build_pandas_partition_snapshot"><code>_build_pandas_partition_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_hash"><code>_hash</code></a>
<a class="reference-chip" href="../modules/drift/#_build_pandas_schema_snapshot"><code>_build_pandas_schema_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_column_hash"><code>_column_hash</code></a>
<a class="reference-chip" href="../modules/drift/#_build_partition_hash"><code>_build_partition_hash</code></a> → <a class="reference-chip" href="../modules/drift/#_hash"><code>_hash</code></a>
<a class="reference-chip" href="../modules/drift/#_build_spark_partition_snapshot"><code>_build_spark_partition_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_build_partition_hash"><code>_build_partition_hash</code></a>
<a class="reference-chip" href="../modules/drift/#_build_spark_schema_snapshot"><code>_build_spark_schema_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_column_hash"><code>_column_hash</code></a>
<a class="reference-chip" href="../modules/drift/#build_and_write_partition_snapshot"><code>build_and_write_partition_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_json_dumps"><code>_json_dumps</code></a>
<a class="reference-chip" href="../modules/drift/#build_and_write_partition_snapshot"><code>build_and_write_partition_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_utc_now_iso"><code>_utc_now_iso</code></a>
<a class="reference-chip" href="../modules/drift/#build_and_write_partition_snapshot"><code>build_and_write_partition_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_write_metadata_rows"><code>_write_metadata_rows</code></a>
<a class="reference-chip" href="../modules/drift/#build_and_write_partition_snapshot"><code>build_and_write_partition_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#build_partition_snapshot"><code>build_partition_snapshot</code></a>
<a class="reference-chip" href="../modules/drift/#build_and_write_schema_snapshot"><code>build_and_write_schema_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_json_dumps"><code>_json_dumps</code></a>
<a class="reference-chip" href="../modules/drift/#build_and_write_schema_snapshot"><code>build_and_write_schema_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_utc_now_iso"><code>_utc_now_iso</code></a>
<a class="reference-chip" href="../modules/drift/#build_and_write_schema_snapshot"><code>build_and_write_schema_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_write_metadata_rows"><code>_write_metadata_rows</code></a>
<a class="reference-chip" href="../modules/drift/#build_and_write_schema_snapshot"><code>build_and_write_schema_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#build_schema_snapshot"><code>build_schema_snapshot</code></a>
<a class="reference-chip" href="../modules/drift/#build_drift_evidence_record"><code>build_drift_evidence_record</code></a> → <a class="reference-chip" href="../modules/drift/#_json_dumps"><code>_json_dumps</code></a>
<a class="reference-chip" href="../modules/drift/#build_drift_evidence_record"><code>build_drift_evidence_record</code></a> → <a class="reference-chip" href="../modules/drift/#_utc_now_iso"><code>_utc_now_iso</code></a>
<a class="reference-chip" href="../modules/drift/#build_partition_snapshot"><code>build_partition_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_build_pandas_partition_snapshot"><code>_build_pandas_partition_snapshot</code></a>
<a class="reference-chip" href="../modules/drift/#build_partition_snapshot"><code>build_partition_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_build_spark_partition_snapshot"><code>_build_spark_partition_snapshot</code></a>
<a class="reference-chip" href="../modules/drift/#build_partition_snapshot"><code>build_partition_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#detect_dataframe_engine"><code>detect_dataframe_engine</code></a>
<a class="reference-chip" href="../modules/drift/#build_schema_snapshot"><code>build_schema_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_build_pandas_schema_snapshot"><code>_build_pandas_schema_snapshot</code></a>
<a class="reference-chip" href="../modules/drift/#build_schema_snapshot"><code>build_schema_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_build_spark_schema_snapshot"><code>_build_spark_schema_snapshot</code></a>
<a class="reference-chip" href="../modules/drift/#build_schema_snapshot"><code>build_schema_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#detect_dataframe_engine"><code>detect_dataframe_engine</code></a>
<a class="reference-chip" href="../../reference/check_partition_drift/"><code>check_partition_drift</code></a> → <a class="reference-chip" href="../modules/drift/#build_partition_snapshot"><code>build_partition_snapshot</code></a>
<a class="reference-chip" href="../../reference/check_partition_drift/"><code>check_partition_drift</code></a> → <a class="reference-chip" href="../modules/drift/#compare_partition_snapshots"><code>compare_partition_snapshots</code></a>
<a class="reference-chip" href="../../reference/check_partition_drift/"><code>check_partition_drift</code></a> → <a class="reference-chip" href="../modules/drift/#default_incremental_safety_policy"><code>default_incremental_safety_policy</code></a>
<a class="reference-chip" href="../../reference/check_schema_drift/"><code>check_schema_drift</code></a> → <a class="reference-chip" href="../modules/drift/#build_schema_snapshot"><code>build_schema_snapshot</code></a>
<a class="reference-chip" href="../../reference/check_schema_drift/"><code>check_schema_drift</code></a> → <a class="reference-chip" href="../modules/drift/#compare_schema_snapshots"><code>compare_schema_snapshots</code></a>
<a class="reference-chip" href="../../reference/check_schema_drift/"><code>check_schema_drift</code></a> → <a class="reference-chip" href="../modules/drift/#default_schema_drift_policy"><code>default_schema_drift_policy</code></a>
<a class="reference-chip" href="../modules/drift/#compare_partition_snapshots"><code>compare_partition_snapshots</code></a> → <a class="reference-chip" href="../modules/drift/#_is_closed_partition"><code>_is_closed_partition</code></a>
<a class="reference-chip" href="../modules/drift/#compare_partition_snapshots"><code>compare_partition_snapshots</code></a> → <a class="reference-chip" href="../modules/drift/#default_incremental_safety_policy"><code>default_incremental_safety_policy</code></a>
<a class="reference-chip" href="../modules/drift/#compare_schema_snapshots"><code>compare_schema_snapshots</code></a> → <a class="reference-chip" href="../modules/drift/#_resolve_change_behavior"><code>_resolve_change_behavior</code></a>
<a class="reference-chip" href="../modules/drift/#compare_schema_snapshots"><code>compare_schema_snapshots</code></a> → <a class="reference-chip" href="../modules/drift/#default_schema_drift_policy"><code>default_schema_drift_policy</code></a>
<a class="reference-chip" href="../modules/drift/#load_latest_partition_snapshot"><code>load_latest_partition_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_is_missing_table_error"><code>_is_missing_table_error</code></a>
<a class="reference-chip" href="../modules/drift/#load_latest_partition_snapshot"><code>load_latest_partition_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_safe_spark_collect"><code>_safe_spark_collect</code></a>
<a class="reference-chip" href="../modules/drift/#load_latest_schema_snapshot"><code>load_latest_schema_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_is_missing_table_error"><code>_is_missing_table_error</code></a>
<a class="reference-chip" href="../modules/drift/#load_latest_schema_snapshot"><code>load_latest_schema_snapshot</code></a> → <a class="reference-chip" href="../modules/drift/#_safe_spark_collect"><code>_safe_spark_collect</code></a>
</div>
#### External callers

None.
#### External callees

<div class="callable-chip-group">
<a class="reference-chip" href="../modules/_utils/#_to_jsonable"><code>_utils._to_jsonable</code></a>
<a class="reference-chip" href="../modules/_utils/#_to_jsonable"><code>_utils._to_jsonable</code></a>
<a class="reference-chip" href="../modules/_utils/#_to_jsonable"><code>_utils._to_jsonable</code></a>
<a class="reference-chip" href="../modules/_utils/#_to_jsonable"><code>_utils._to_jsonable</code></a>
<a class="reference-chip" href="../modules/_utils/#_to_jsonable"><code>_utils._to_jsonable</code></a>
</div>
</div>
