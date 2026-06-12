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
      <td><code>_coerce_date</code> (internal), <code>_iso_date_value</code> (internal), <code>_max_column_value</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Enforce append, overwrite, or skip profile behavior against accepted catalogue profile evidence.</td>
      <td><code>_catalogue_value</code> (internal), <code>_guardrail_exclude_columns</code> (internal), <code>_is_greater_than</code> (internal), <code>_is_less_than</code> (internal), <code>_is_missing_table_error</code> (internal), <code>_latest_catalogue_behavior_profile_row</code> (internal), <code>_profile_row_count</code> (internal), <code>_profile_watermark_bounds</code> (internal), <code>_string_value</code> (internal)</td>
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
      <td><code>_actual_schema</code> (internal), <code>_normalize_datatype</code> (internal)</td>
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
<span class="reference-chip"><code>_coerce_date</code></span>, <span class="reference-chip"><code>_iso_date_value</code></span>, <span class="reference-chip"><code>_max_column_value</code></span>
</li>
<li>
<a class="reference-chip" href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_catalogue_value</code></span>, <span class="reference-chip"><code>_guardrail_exclude_columns</code></span>, <span class="reference-chip"><code>_is_greater_than</code></span>, <span class="reference-chip"><code>_is_less_than</code></span>, <span class="reference-chip"><code>_is_missing_table_error</code></span>, <span class="reference-chip"><code>_latest_catalogue_behavior_profile_row</code></span>, <span class="reference-chip"><code>_profile_row_count</code></span>, <span class="reference-chip"><code>_profile_watermark_bounds</code></span>, <span class="reference-chip"><code>_string_value</code></span>
</li>
<li>
<a class="reference-chip" href="../../reference/stop_if_failed/"><code>stop_if_failed</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/validate_schema/"><code>validate_schema</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_actual_schema</code></span>, <span class="reference-chip"><code>_normalize_datatype</code></span>
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
      <td><code>_actual_schema</code></td>
      <td><a href="../../reference/validate_schema/"><code>validate_schema</code></a></td>
    </tr>
    <tr>
      <td><code>_catalogue_value</code></td>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
    </tr>
    <tr>
      <td><code>_coerce_date</code></td>
      <td><a href="../../reference/enforce_freshness/"><code>enforce_freshness</code></a></td>
    </tr>
    <tr>
      <td><code>_comparable_value</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_guardrail_exclude_columns</code></td>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
    </tr>
    <tr>
      <td><code>_is_greater_than</code></td>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
    </tr>
    <tr>
      <td><code>_is_guardrail_excluded_column</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_is_less_than</code></td>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
    </tr>
    <tr>
      <td><code>_is_missing_table_error</code></td>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
    </tr>
    <tr>
      <td><code>_iso_date_value</code></td>
      <td><a href="../../reference/enforce_freshness/"><code>enforce_freshness</code></a></td>
    </tr>
    <tr>
      <td><code>_latest_catalogue_behavior_profile_row</code></td>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
    </tr>
    <tr>
      <td><code>_max_column_value</code></td>
      <td><a href="../../reference/enforce_freshness/"><code>enforce_freshness</code></a></td>
    </tr>
    <tr>
      <td><code>_normalize_datatype</code></td>
      <td><a href="../../reference/validate_schema/"><code>validate_schema</code></a></td>
    </tr>
    <tr>
      <td><code>_normalize_profile</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_profile_row_count</code></td>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
    </tr>
    <tr>
      <td><code>_profile_watermark_bounds</code></td>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
    </tr>
    <tr>
      <td><code>_row_to_dict</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_string_value</code></td>
      <td><a href="../../reference/enforce_profile_behavior/"><code>enforce_profile_behavior</code></a></td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<span class="reference-chip"><code>_actual_schema</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_normalize_datatype</code></span>
</li>
<li>
<span class="reference-chip"><code>_catalogue_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_coerce_date</code></span>
</li>
<li>
<span class="reference-chip"><code>_comparable_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_guardrail_exclude_columns</code></span>
</li>
<li>
<span class="reference-chip"><code>_is_greater_than</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_comparable_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_is_guardrail_excluded_column</code></span>
</li>
<li>
<span class="reference-chip"><code>_is_less_than</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_comparable_value</code></span>
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
<span class="reference-chip"><code>_latest_catalogue_behavior_profile_row</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_catalogue_value</code></span>, <span class="reference-chip"><code>_is_missing_table_error</code></span>, <span class="reference-chip"><code>_row_to_dict</code></span>, <span class="reference-chip"><code>_string_value</code></span>
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
<span class="reference-chip"><code>_profile_row_count</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_normalize_profile</code></span>
</li>
<li>
<span class="reference-chip"><code>_profile_watermark_bounds</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_normalize_profile</code></span>, <span class="reference-chip"><code>_string_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_row_to_dict</code></span>
</li>
<li>
<span class="reference-chip"><code>_string_value</code></span>
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
