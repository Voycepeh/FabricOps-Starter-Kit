# `drift` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 6</span><span class="reference-chip">Internal helpers: 18</span><span class="reference-chip">Outbound: 3</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns schema and catalogue profile stability checks as engineering guardrails during pipeline runs.

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
      <td>Owns schema and catalogue profile stability checks as engineering guardrails during pipeline runs.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>6</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>18</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>3</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td>—</td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>config</code>, <code>data_profiling</code>, <code>fabric_input_output</code></td>
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
      <td><a href="../../reference/display_schema_profile/"><code>display_schema_profile</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Display current schema columns, Spark datatypes, nullable flags, and proposed guardrail datatypes.</td>
      <td><a href="../../reference/internal/drift/_schema_profile_rows/"><code>_schema_profile_rows</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/enforce_catalogue_stability/"><code>enforce_catalogue_stability</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Compare deterministic profile hashes against append-only catalogue evidence and return a source stability guardrail result.</td>
      <td><a href="../../reference/internal/drift/_filter_watermark_slice/"><code>_filter_watermark_slice</code></a> (internal), <a href="../../reference/internal/drift/_is_missing_table_error/"><code>_is_missing_table_error</code></a> (internal), <a href="../../reference/internal/drift/_latest_catalogue_stability_row/"><code>_latest_catalogue_stability_row</code></a> (internal), <a href="../../reference/internal/drift/_max_watermark_value/"><code>_max_watermark_value</code></a> (internal), <a href="../../reference/internal/drift/_profile_hash/"><code>_profile_hash</code></a> (internal), <a href="../../reference/internal/drift/_profile_row_count/"><code>_profile_row_count</code></a> (internal), <a href="../../reference/internal/drift/_schema_hash_from_dataframe/"><code>_schema_hash_from_dataframe</code></a> (internal), <a href="../../reference/internal/drift/_stability_exclude_columns/"><code>_stability_exclude_columns</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/generate_schema_guardrail_config/"><code>generate_schema_guardrail_config</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Generate a reviewed starter expected_schema dictionary from a DataFrame schema.</td>
      <td><a href="../../reference/internal/drift/_schema_profile_rows/"><code>_schema_profile_rows</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/print_schema_guardrail_config/"><code>print_schema_guardrail_config</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Print copy-paste-ready starter expected_schema code from a DataFrame schema.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/stop_if_failed/"><code>stop_if_failed</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Stop a notebook only when a schema, stability, or DQ guardrail result blocks continuation.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/validate_schema/"><code>validate_schema</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.</td>
      <td><a href="../../reference/internal/drift/_actual_schema/"><code>_actual_schema</code></a> (internal), <a href="../../reference/internal/drift/_normalize_datatype/"><code>_normalize_datatype</code></a> (internal)</td>
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
<a class="reference-chip" href="../../reference/display_schema_profile/"><code>display_schema_profile</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_schema_profile_rows"><code>_schema_profile_rows</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/enforce_catalogue_stability/"><code>enforce_catalogue_stability</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_filter_watermark_slice"><code>_filter_watermark_slice</code></a>, <a class="reference-chip" href="#_is_missing_table_error"><code>_is_missing_table_error</code></a>, <a class="reference-chip" href="#_latest_catalogue_stability_row"><code>_latest_catalogue_stability_row</code></a>, <a class="reference-chip" href="#_max_watermark_value"><code>_max_watermark_value</code></a>, <a class="reference-chip" href="#_profile_hash"><code>_profile_hash</code></a>, <a class="reference-chip" href="#_profile_row_count"><code>_profile_row_count</code></a>, <a class="reference-chip" href="#_schema_hash_from_dataframe"><code>_schema_hash_from_dataframe</code></a>, <a class="reference-chip" href="#_stability_exclude_columns"><code>_stability_exclude_columns</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/generate_schema_guardrail_config/"><code>generate_schema_guardrail_config</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_schema_profile_rows"><code>_schema_profile_rows</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/print_schema_guardrail_config/"><code>print_schema_guardrail_config</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="../../reference/generate_schema_guardrail_config/"><code>generate_schema_guardrail_config</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/stop_if_failed/"><code>stop_if_failed</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/validate_schema/"><code>validate_schema</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_actual_schema"><code>_actual_schema</code></a>, <a class="reference-chip" href="#_normalize_datatype"><code>_normalize_datatype</code></a>
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
      <td><a href="../../reference/validate_schema/"><code>validate_schema</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_canonical_hash_value/"><code>_canonical_hash_value</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_canonical_json_hash/"><code>_canonical_json_hash</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_filter_watermark_slice/"><code>_filter_watermark_slice</code></a></td>
      <td><a href="../../reference/enforce_catalogue_stability/"><code>enforce_catalogue_stability</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_is_missing_table_error/"><code>_is_missing_table_error</code></a></td>
      <td><a href="../../reference/enforce_catalogue_stability/"><code>enforce_catalogue_stability</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_is_stability_excluded_column/"><code>_is_stability_excluded_column</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_latest_catalogue_stability_row/"><code>_latest_catalogue_stability_row</code></a></td>
      <td><a href="../../reference/enforce_catalogue_stability/"><code>enforce_catalogue_stability</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_max_watermark_value/"><code>_max_watermark_value</code></a></td>
      <td><a href="../../reference/enforce_catalogue_stability/"><code>enforce_catalogue_stability</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_normalize_datatype/"><code>_normalize_datatype</code></a></td>
      <td><a href="../../reference/validate_schema/"><code>validate_schema</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_normalize_profile/"><code>_normalize_profile</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_profile_hash/"><code>_profile_hash</code></a></td>
      <td><a href="../../reference/enforce_catalogue_stability/"><code>enforce_catalogue_stability</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_profile_row_count/"><code>_profile_row_count</code></a></td>
      <td><a href="../../reference/enforce_catalogue_stability/"><code>enforce_catalogue_stability</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_row_to_dict/"><code>_row_to_dict</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_schema_guardrail_type/"><code>_schema_guardrail_type</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_schema_hash_from_dataframe/"><code>_schema_hash_from_dataframe</code></a></td>
      <td><a href="../../reference/enforce_catalogue_stability/"><code>enforce_catalogue_stability</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_schema_profile_rows/"><code>_schema_profile_rows</code></a></td>
      <td><a href="../../reference/display_schema_profile/"><code>display_schema_profile</code></a>, <a href="../../reference/generate_schema_guardrail_config/"><code>generate_schema_guardrail_config</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_stability_exclude_columns/"><code>_stability_exclude_columns</code></a></td>
      <td><a href="../../reference/enforce_catalogue_stability/"><code>enforce_catalogue_stability</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_stable_profile_payload/"><code>_stable_profile_payload</code></a></td>
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
<a class="reference-chip" href="#_canonical_hash_value"><code>_canonical_hash_value</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_canonical_hash_value"><code>_canonical_hash_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_canonical_json_hash"><code>_canonical_json_hash</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_canonical_hash_value"><code>_canonical_hash_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_filter_watermark_slice"><code>_filter_watermark_slice</code></a>
</li>
<li>
<a class="reference-chip" href="#_is_missing_table_error"><code>_is_missing_table_error</code></a>
</li>
<li>
<a class="reference-chip" href="#_is_stability_excluded_column"><code>_is_stability_excluded_column</code></a>
</li>
<li>
<a class="reference-chip" href="#_latest_catalogue_stability_row"><code>_latest_catalogue_stability_row</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_is_missing_table_error"><code>_is_missing_table_error</code></a>, <a class="reference-chip" href="#_row_to_dict"><code>_row_to_dict</code></a>
</li>
<li>
<a class="reference-chip" href="#_max_watermark_value"><code>_max_watermark_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_normalize_datatype"><code>_normalize_datatype</code></a>
</li>
<li>
<a class="reference-chip" href="#_normalize_profile"><code>_normalize_profile</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_normalize_profile"><code>_normalize_profile</code></a>
</li>
<li>
<a class="reference-chip" href="#_profile_hash"><code>_profile_hash</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_canonical_json_hash"><code>_canonical_json_hash</code></a>, <a class="reference-chip" href="#_stable_profile_payload"><code>_stable_profile_payload</code></a>
</li>
<li>
<a class="reference-chip" href="#_profile_row_count"><code>_profile_row_count</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_stable_profile_payload"><code>_stable_profile_payload</code></a>
</li>
<li>
<a class="reference-chip" href="#_row_to_dict"><code>_row_to_dict</code></a>
</li>
<li>
<a class="reference-chip" href="#_schema_guardrail_type"><code>_schema_guardrail_type</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_normalize_datatype"><code>_normalize_datatype</code></a>
</li>
<li>
<a class="reference-chip" href="#_schema_hash_from_dataframe"><code>_schema_hash_from_dataframe</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_actual_schema"><code>_actual_schema</code></a>, <a class="reference-chip" href="#_canonical_json_hash"><code>_canonical_json_hash</code></a>, <a class="reference-chip" href="#_is_stability_excluded_column"><code>_is_stability_excluded_column</code></a>, <a class="reference-chip" href="#_stability_exclude_columns"><code>_stability_exclude_columns</code></a>
</li>
<li>
<a class="reference-chip" href="#_schema_profile_rows"><code>_schema_profile_rows</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_actual_schema"><code>_actual_schema</code></a>, <a class="reference-chip" href="#_schema_guardrail_type"><code>_schema_guardrail_type</code></a>
</li>
<li>
<a class="reference-chip" href="#_stability_exclude_columns"><code>_stability_exclude_columns</code></a>
</li>
<li>
<a class="reference-chip" href="#_stable_profile_payload"><code>_stable_profile_payload</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_normalize_datatype"><code>_normalize_datatype</code></a>, <a class="reference-chip" href="#_normalize_profile"><code>_normalize_profile</code></a>
</li>
</ul>
</details>

### External callers

None.
### External callees

**data_profiling**
<a class="reference-chip" href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a>

**fabric_input_output**
<a class="reference-chip" href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a>
