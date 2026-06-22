# `guardrails` module (internal)

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 0</span><span class="reference-chip">Internal helpers: 25</span><span class="reference-chip">Uses 3 external modules</span><span class="reference-chip">Used by 1 external module</span></div>

## Module purpose

Owns schema, freshness, and profile behavior checks as pipeline guardrails during enforcement.

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
      <td><code>guardrails</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns schema, freshness, and profile behavior checks as pipeline guardrails during enforcement.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>25</td>
    </tr>
    <tr>
      <td>Used by external module count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>Uses external module count</td>
      <td>3</td>
    </tr>
    <tr>
      <td>External modules using this module</td>
      <td><code>pipeline</code></td>
    </tr>
    <tr>
      <td>External modules this module uses</td>
      <td><code>data_profiling</code>, <code>fabric_input_output</code>, <code>metadata</code></td>
    </tr>
  </tbody>
</table>

## Public callables

No public exports in this module.

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>guardrails</h5>
<h6>Public callables</h6>
<p>None.</p>
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
      <td><code>_accepted_profile_rows</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_actual_schema</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_apply_bypass_post_review_warning</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_catalogue_value</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_check_schema_rule_runtime</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_check_schema_runtime</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_coerce_date</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_guardrail_exclude_columns</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_is_active_guardrail_rule</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_is_missing_table_error</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_iso_date_value</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_json_dumps_stable</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_max_column_value</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_normalize_datatype</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_normalize_profile</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_parse_rule_parameters</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_profile_hash</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_profile_payload_from_profile</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_profile_row_count</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_row_to_dict</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_rule_review_status</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_schema_signature</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_select_profile_behavior_rule</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_select_table_guardrail_rule</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_string_value</code></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<span class="reference-chip"><code>_accepted_profile_rows</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_catalogue_value</code></span>, <span class="reference-chip"><code>_row_to_dict</code></span>, <span class="reference-chip"><code>_string_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_actual_schema</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_normalize_datatype</code></span>
</li>
<li>
<span class="reference-chip"><code>_apply_bypass_post_review_warning</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_rule_review_status</code></span>
</li>
<li>
<span class="reference-chip"><code>_catalogue_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_check_schema_rule_runtime</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_apply_bypass_post_review_warning</code></span>, <span class="reference-chip"><code>_catalogue_value</code></span>, <span class="reference-chip"><code>_check_schema_runtime</code></span>, <span class="reference-chip"><code>_parse_rule_parameters</code></span>, <span class="reference-chip"><code>_select_table_guardrail_rule</code></span>, <span class="reference-chip"><code>_string_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_check_schema_runtime</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_actual_schema</code></span>, <span class="reference-chip"><code>_normalize_datatype</code></span>
</li>
<li>
<span class="reference-chip"><code>_coerce_date</code></span>
</li>
<li>
<span class="reference-chip"><code>_guardrail_exclude_columns</code></span>
</li>
<li>
<span class="reference-chip"><code>_is_active_guardrail_rule</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_catalogue_value</code></span>, <span class="reference-chip"><code>_rule_review_status</code></span>, <span class="reference-chip"><code>_string_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_is_missing_table_error</code></span>
</li>
<li>
<span class="reference-chip"><code>_iso_date_value</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_coerce_date</code></span>
</li>
<li>
<span class="reference-chip"><code>_json_dumps_stable</code></span>
</li>
<li>
<span class="reference-chip"><code>_max_column_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_normalize_datatype</code></span>
</li>
<li>
<span class="reference-chip"><code>_normalize_profile</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_normalize_profile</code></span>
</li>
<li>
<span class="reference-chip"><code>_parse_rule_parameters</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_catalogue_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_profile_hash</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_json_dumps_stable</code></span>
</li>
<li>
<span class="reference-chip"><code>_profile_payload_from_profile</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_normalize_profile</code></span>, <span class="reference-chip"><code>_profile_row_count</code></span>, <span class="reference-chip"><code>_schema_signature</code></span>, <span class="reference-chip"><code>_string_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_profile_row_count</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_normalize_profile</code></span>
</li>
<li>
<span class="reference-chip"><code>_row_to_dict</code></span>
</li>
<li>
<span class="reference-chip"><code>_rule_review_status</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_catalogue_value</code></span>, <span class="reference-chip"><code>_string_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_schema_signature</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_actual_schema</code></span>
</li>
<li>
<span class="reference-chip"><code>_select_profile_behavior_rule</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_catalogue_value</code></span>, <span class="reference-chip"><code>_is_active_guardrail_rule</code></span>, <span class="reference-chip"><code>_row_to_dict</code></span>, <span class="reference-chip"><code>_string_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_select_table_guardrail_rule</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_catalogue_value</code></span>, <span class="reference-chip"><code>_is_active_guardrail_rule</code></span>, <span class="reference-chip"><code>_row_to_dict</code></span>, <span class="reference-chip"><code>_string_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_string_value</code></span>
</li>
</ul>
</details>

### External callers

**pipeline**
<a class="reference-chip" href="../reference/run_table_guardrails/"><code>run_table_guardrails</code></a>

### External callees

**data_profiling**
<a class="reference-chip" href="../reference/profile_dataframe/"><code>profile_dataframe</code></a>

**fabric_input_output**
<a class="reference-chip" href="fabric_input_output/#_configured_lakehouse_schema"><code>_configured_lakehouse_schema</code></a>, <a class="reference-chip" href="../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a>

**metadata**
<a class="reference-chip" href="metadata/#_write_guardrail_result_row"><code>_write_guardrail_result_row</code></a>
