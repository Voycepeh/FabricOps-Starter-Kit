# `guardrails` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 4</span><span class="reference-chip">Internal helpers: 18</span><span class="reference-chip">Outbound: 2</span><span class="reference-chip">Inbound: 1</span></div>

## Module purpose

Owns schema, freshness, and profile behavior checks as pipeline guardrails during runtime enforcement.

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
      <td>Owns schema, freshness, and profile behavior checks as pipeline guardrails during runtime enforcement.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>4</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>18</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>2</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td><code>pipeline</code></td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>data_profiling</code>, <code>fabric_input_output</code></td>
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
      <td><a href="../../reference/enforce_freshness/"><code>enforce_freshness</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Enforce whether the latest data arrived within the configured freshness lag.</td>
      <td><a href="../../reference/internal/guardrails/_coerce_date/"><code>_coerce_date</code></a> (internal), <a href="../../reference/internal/guardrails/_iso_date_value/"><code>_iso_date_value</code></a> (internal), <a href="../../reference/internal/guardrails/_max_column_value/"><code>_max_column_value</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Enforce append, overwrite, or skip profile behavior against accepted catalogue profile evidence.</td>
      <td><a href="../../reference/internal/guardrails/_catalogue_value/"><code>_catalogue_value</code></a> (internal), <a href="../../reference/internal/guardrails/_guardrail_exclude_columns/"><code>_guardrail_exclude_columns</code></a> (internal), <a href="../../reference/internal/guardrails/_is_greater_than/"><code>_is_greater_than</code></a> (internal), <a href="../../reference/internal/guardrails/_is_less_than/"><code>_is_less_than</code></a> (internal), <a href="../../reference/internal/guardrails/_is_missing_table_error/"><code>_is_missing_table_error</code></a> (internal), <a href="../../reference/internal/guardrails/_latest_catalogue_behavior_profile_row/"><code>_latest_catalogue_behavior_profile_row</code></a> (internal), <a href="../../reference/internal/guardrails/_profile_row_count/"><code>_profile_row_count</code></a> (internal), <a href="../../reference/internal/guardrails/_profile_watermark_bounds/"><code>_profile_watermark_bounds</code></a> (internal), <a href="../../reference/internal/guardrails/_string_value/"><code>_string_value</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/stop_if_failed/"><code>stop_if_failed</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Stop a notebook only when a schema, freshness, profile behavior, or DQ guardrail result blocks continuation.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/validate_schema/"><code>validate_schema</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.</td>
      <td><a href="../../reference/internal/guardrails/_actual_schema/"><code>_actual_schema</code></a> (internal), <a href="../../reference/internal/guardrails/_normalize_datatype/"><code>_normalize_datatype</code></a> (internal)</td>
    </tr>
  </tbody>
</table>
</div>

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>guardrails</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/enforce_freshness/"><code>enforce_freshness</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_date"><code>_coerce_date</code></a>, <a class="reference-chip" href="#_iso_date_value"><code>_iso_date_value</code></a>, <a class="reference-chip" href="#_max_column_value"><code>_max_column_value</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_catalogue_value"><code>_catalogue_value</code></a>, <a class="reference-chip" href="#_guardrail_exclude_columns"><code>_guardrail_exclude_columns</code></a>, <a class="reference-chip" href="#_is_greater_than"><code>_is_greater_than</code></a>, <a class="reference-chip" href="#_is_less_than"><code>_is_less_than</code></a>, <a class="reference-chip" href="#_is_missing_table_error"><code>_is_missing_table_error</code></a>, <a class="reference-chip" href="#_latest_catalogue_behavior_profile_row"><code>_latest_catalogue_behavior_profile_row</code></a>, <a class="reference-chip" href="#_profile_row_count"><code>_profile_row_count</code></a>, <a class="reference-chip" href="#_profile_watermark_bounds"><code>_profile_watermark_bounds</code></a>, <a class="reference-chip" href="#_string_value"><code>_string_value</code></a>
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
      <td><a href="../../reference/internal/guardrails/_actual_schema/"><code>_actual_schema</code></a></td>
      <td><a href="../../reference/validate_schema/"><code>validate_schema</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/guardrails/_catalogue_value/"><code>_catalogue_value</code></a></td>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/guardrails/_coerce_date/"><code>_coerce_date</code></a></td>
      <td><a href="../../reference/enforce_freshness/"><code>enforce_freshness</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/guardrails/_comparable_value/"><code>_comparable_value</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/guardrails/_guardrail_exclude_columns/"><code>_guardrail_exclude_columns</code></a></td>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/guardrails/_is_greater_than/"><code>_is_greater_than</code></a></td>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/guardrails/_is_guardrail_excluded_column/"><code>_is_guardrail_excluded_column</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/guardrails/_is_less_than/"><code>_is_less_than</code></a></td>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/guardrails/_is_missing_table_error/"><code>_is_missing_table_error</code></a></td>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/guardrails/_iso_date_value/"><code>_iso_date_value</code></a></td>
      <td><a href="../../reference/enforce_freshness/"><code>enforce_freshness</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/guardrails/_latest_catalogue_behavior_profile_row/"><code>_latest_catalogue_behavior_profile_row</code></a></td>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/guardrails/_max_column_value/"><code>_max_column_value</code></a></td>
      <td><a href="../../reference/enforce_freshness/"><code>enforce_freshness</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/guardrails/_normalize_datatype/"><code>_normalize_datatype</code></a></td>
      <td><a href="../../reference/validate_schema/"><code>validate_schema</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/guardrails/_normalize_profile/"><code>_normalize_profile</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/guardrails/_profile_row_count/"><code>_profile_row_count</code></a></td>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/guardrails/_profile_watermark_bounds/"><code>_profile_watermark_bounds</code></a></td>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/guardrails/_row_to_dict/"><code>_row_to_dict</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/guardrails/_string_value/"><code>_string_value</code></a></td>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
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
<a class="reference-chip" href="#_catalogue_value"><code>_catalogue_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_coerce_date"><code>_coerce_date</code></a>
</li>
<li>
<a class="reference-chip" href="#_comparable_value"><code>_comparable_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_guardrail_exclude_columns"><code>_guardrail_exclude_columns</code></a>
</li>
<li>
<a class="reference-chip" href="#_is_greater_than"><code>_is_greater_than</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_comparable_value"><code>_comparable_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_is_guardrail_excluded_column"><code>_is_guardrail_excluded_column</code></a>
</li>
<li>
<a class="reference-chip" href="#_is_less_than"><code>_is_less_than</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_comparable_value"><code>_comparable_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_is_missing_table_error"><code>_is_missing_table_error</code></a>
</li>
<li>
<a class="reference-chip" href="#_iso_date_value"><code>_iso_date_value</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_date"><code>_coerce_date</code></a>
</li>
<li>
<a class="reference-chip" href="#_latest_catalogue_behavior_profile_row"><code>_latest_catalogue_behavior_profile_row</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_catalogue_value"><code>_catalogue_value</code></a>, <a class="reference-chip" href="#_is_missing_table_error"><code>_is_missing_table_error</code></a>, <a class="reference-chip" href="#_row_to_dict"><code>_row_to_dict</code></a>, <a class="reference-chip" href="#_string_value"><code>_string_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_max_column_value"><code>_max_column_value</code></a>
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
<a class="reference-chip" href="#_profile_row_count"><code>_profile_row_count</code></a>
</li>
<li>
<a class="reference-chip" href="#_profile_watermark_bounds"><code>_profile_watermark_bounds</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_normalize_profile"><code>_normalize_profile</code></a>, <a class="reference-chip" href="#_string_value"><code>_string_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_row_to_dict"><code>_row_to_dict</code></a>
</li>
<li>
<a class="reference-chip" href="#_string_value"><code>_string_value</code></a>
</li>
</ul>
</details>

### External callers

**pipeline**
<a class="reference-chip" href="../../reference/run_table_guardrails/"><code>run_table_guardrails</code></a>

### External callees

**data_profiling**
<a class="reference-chip" href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a>

**fabric_input_output**
<a class="reference-chip" href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a>
