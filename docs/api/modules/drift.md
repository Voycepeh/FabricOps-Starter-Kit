# `drift` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 3</span><span class="reference-chip">Internal helpers: 14</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 0</span></div>

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
      <td>3</td>
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
      <td><code>data_profiling</code></td>
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
      <td><a href="../../reference/monitor_data_changes/"><code>monitor_data_changes</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Profile data, compare against the approved baseline, and return a drift guardrail result.</td>
      <td><a href="../../reference/internal/drift/_check_profile_drift/"><code>_check_profile_drift</code></a> (internal), <a href="../../reference/internal/drift/_data_change_preset_config/"><code>_data_change_preset_config</code></a> (internal), <a href="../../reference/internal/drift/_extract_categorical_distribution_categories/"><code>_extract_categorical_distribution_categories</code></a> (internal), <a href="../../reference/internal/drift/_extract_numeric_distribution_bin_edges/"><code>_extract_numeric_distribution_bin_edges</code></a> (internal), <a href="../../reference/internal/drift/_load_latest_profile/"><code>_load_latest_profile</code></a> (internal), <a href="../../reference/internal/drift/_normalize_profile/"><code>_normalize_profile</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/stop_if_failed/"><code>stop_if_failed</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Stop a notebook only when a schema or data-change guardrail result blocks continuation.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/validate_schema/"><code>validate_schema</code></a></td>
      <td>Essential</td>
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
<a class="reference-chip" href="../../reference/monitor_data_changes/"><code>monitor_data_changes</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_check_profile_drift"><code>_check_profile_drift</code></a>, <a class="reference-chip" href="#_data_change_preset_config"><code>_data_change_preset_config</code></a>, <a class="reference-chip" href="#_extract_categorical_distribution_categories"><code>_extract_categorical_distribution_categories</code></a>, <a class="reference-chip" href="#_extract_numeric_distribution_bin_edges"><code>_extract_numeric_distribution_bin_edges</code></a>, <a class="reference-chip" href="#_load_latest_profile"><code>_load_latest_profile</code></a>, <a class="reference-chip" href="#_normalize_profile"><code>_normalize_profile</code></a>
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
      <td><a href="../../reference/internal/drift/_categorical_distance/"><code>_categorical_distance</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_check_profile_drift/"><code>_check_profile_drift</code></a></td>
      <td><a href="../../reference/monitor_data_changes/"><code>monitor_data_changes</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_data_change_preset_config/"><code>_data_change_preset_config</code></a></td>
      <td><a href="../../reference/monitor_data_changes/"><code>monitor_data_changes</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_extract_categorical_distribution_categories/"><code>_extract_categorical_distribution_categories</code></a></td>
      <td><a href="../../reference/monitor_data_changes/"><code>monitor_data_changes</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_extract_numeric_distribution_bin_edges/"><code>_extract_numeric_distribution_bin_edges</code></a></td>
      <td><a href="../../reference/monitor_data_changes/"><code>monitor_data_changes</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_is_missing_table_error/"><code>_is_missing_table_error</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_load_latest_profile/"><code>_load_latest_profile</code></a></td>
      <td><a href="../../reference/monitor_data_changes/"><code>monitor_data_changes</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_normalize_datatype/"><code>_normalize_datatype</code></a></td>
      <td><a href="../../reference/validate_schema/"><code>validate_schema</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_normalize_profile/"><code>_normalize_profile</code></a></td>
      <td><a href="../../reference/monitor_data_changes/"><code>monitor_data_changes</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_numeric_psi/"><code>_numeric_psi</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_parse_distribution/"><code>_parse_distribution</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_proportions/"><code>_proportions</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/drift/_row_get/"><code>_row_get</code></a></td>
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
<a class="reference-chip" href="#_categorical_distance"><code>_categorical_distance</code></a>
</li>
<li>
<a class="reference-chip" href="#_check_profile_drift"><code>_check_profile_drift</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_categorical_distance"><code>_categorical_distance</code></a>, <a class="reference-chip" href="#_normalize_profile"><code>_normalize_profile</code></a>, <a class="reference-chip" href="#_numeric_psi"><code>_numeric_psi</code></a>
</li>
<li>
<a class="reference-chip" href="#_data_change_preset_config"><code>_data_change_preset_config</code></a>
</li>
<li>
<a class="reference-chip" href="#_extract_categorical_distribution_categories"><code>_extract_categorical_distribution_categories</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_normalize_profile"><code>_normalize_profile</code></a>
</li>
<li>
<a class="reference-chip" href="#_extract_numeric_distribution_bin_edges"><code>_extract_numeric_distribution_bin_edges</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_normalize_profile"><code>_normalize_profile</code></a>
</li>
<li>
<a class="reference-chip" href="#_is_missing_table_error"><code>_is_missing_table_error</code></a>
</li>
<li>
<a class="reference-chip" href="#_load_latest_profile"><code>_load_latest_profile</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_is_missing_table_error"><code>_is_missing_table_error</code></a>, <a class="reference-chip" href="#_normalize_profile"><code>_normalize_profile</code></a>
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
<a class="reference-chip" href="#_proportions"><code>_proportions</code></a>
</li>
<li>
<a class="reference-chip" href="#_row_get"><code>_row_get</code></a>
</li>
</ul>
</details>

### External callers

None.
### External callees

**data_profiling**
<a class="reference-chip" href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a>
