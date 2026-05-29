# `data_agreement` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 6</span><span class="reference-chip">Internal helpers: 21</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns agreement metadata capture, audited record building, metadata commit helpers, and agreement selection helpers used to anchor notebook workflows to approved business agreements.

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
      <td><code>data_agreement</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns agreement metadata capture, audited record building, metadata commit helpers, and agreement selection helpers used to anchor notebook workflows to approved business agreements.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>6</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>21</td>
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
      <td><code>metadata</code></td>
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
      <td><a href="../../reference/collect_agreement_metadata/"><code>collect_agreement_metadata</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Collect widget values and build audited agreement metadata records.</td>
      <td><a href="../../reference/internal/data_agreement/_build_agreement_record/"><code>_build_agreement_record</code></a> (internal), <a href="../../reference/internal/data_agreement/_normalise_widget_values/"><code>_normalise_widget_values</code></a> (internal), <a href="../../reference/internal/data_agreement/_read_agreement_widget_values/"><code>_read_agreement_widget_values</code></a> (internal), <a href="../../reference/internal/data_agreement/_record_base/"><code>_record_base</code></a> (internal), <a href="../../reference/internal/data_agreement/_resolve_committed_at/"><code>_resolve_committed_at</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/commit_agreement_metadata/"><code>commit_agreement_metadata</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Commit agreement metadata records to append-friendly Delta tables.</td>
      <td><a href="../../reference/internal/data_agreement/_safe_table_prefix/"><code>_safe_table_prefix</code></a> (internal), <a href="../../reference/internal/data_agreement/_write_record/"><code>_write_record</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/create_agreement_widgets/"><code>create_agreement_widgets</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Create Fabric widgets for data sharing agreement metadata capture.</td>
      <td><a href="../../reference/internal/data_agreement/_agreement_widget_specs/"><code>_agreement_widget_specs</code></a> (internal), <a href="../../reference/internal/data_agreement/_get_fabric_widgets/"><code>_get_fabric_widgets</code></a> (internal), <a href="../../reference/internal/data_agreement/_widget_dropdown/"><code>_widget_dropdown</code></a> (internal), <a href="../../reference/internal/data_agreement/_widget_text/"><code>_widget_text</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/get_selected_agreement/"><code>get_selected_agreement</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Return selected agreement from widget flow.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/load_agreements/"><code>load_agreements</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Load latest distinct agreement metadata rows for widget selection.</td>
      <td><a href="../../reference/internal/data_agreement/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a> (internal), <a href="../../reference/internal/data_agreement/_latest_distinct_agreements/"><code>_latest_distinct_agreements</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/select_agreement/"><code>select_agreement</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Render a widget dropdown and store selected agreement metadata row in module state.</td>
      <td><a href="../../reference/internal/data_agreement/_agreement_option_label/"><code>_agreement_option_label</code></a> (internal), <a href="../../reference/internal/data_agreement/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a> (internal)</td>
    </tr>
  </tbody>
</table>
</div>

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>data_agreement</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/collect_agreement_metadata/"><code>collect_agreement_metadata</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_build_agreement_record"><code>_build_agreement_record</code></a>, <a class="reference-chip" href="#_normalise_widget_values"><code>_normalise_widget_values</code></a>, <a class="reference-chip" href="#_read_agreement_widget_values"><code>_read_agreement_widget_values</code></a>, <a class="reference-chip" href="#_record_base"><code>_record_base</code></a>, <a class="reference-chip" href="#_resolve_committed_at"><code>_resolve_committed_at</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/commit_agreement_metadata/"><code>commit_agreement_metadata</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_safe_table_prefix"><code>_safe_table_prefix</code></a>, <a class="reference-chip" href="#_write_record"><code>_write_record</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/create_agreement_widgets/"><code>create_agreement_widgets</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_agreement_widget_specs"><code>_agreement_widget_specs</code></a>, <a class="reference-chip" href="#_get_fabric_widgets"><code>_get_fabric_widgets</code></a>, <a class="reference-chip" href="#_widget_dropdown"><code>_widget_dropdown</code></a>, <a class="reference-chip" href="#_widget_text"><code>_widget_text</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/get_selected_agreement/"><code>get_selected_agreement</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/load_agreements/"><code>load_agreements</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>, <a class="reference-chip" href="#_latest_distinct_agreements"><code>_latest_distinct_agreements</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/select_agreement/"><code>select_agreement</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_agreement_option_label"><code>_agreement_option_label</code></a>, <a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>
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
      <td><a href="../../reference/internal/data_agreement/_agreement_option_label/"><code>_agreement_option_label</code></a></td>
      <td><a href="../../reference/select_agreement/"><code>select_agreement</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_agreement_widget_specs/"><code>_agreement_widget_specs</code></a></td>
      <td><a href="../../reference/create_agreement_widgets/"><code>create_agreement_widgets</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_build_agreement_record/"><code>_build_agreement_record</code></a></td>
      <td><a href="../../reference/collect_agreement_metadata/"><code>collect_agreement_metadata</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a></td>
      <td><a href="../../reference/load_agreements/"><code>load_agreements</code></a>, <a href="../../reference/select_agreement/"><code>select_agreement</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_derive_agreement_status/"><code>_derive_agreement_status</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_get_fabric_widgets/"><code>_get_fabric_widgets</code></a></td>
      <td><a href="../../reference/create_agreement_widgets/"><code>create_agreement_widgets</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_latest_distinct_agreements/"><code>_latest_distinct_agreements</code></a></td>
      <td><a href="../../reference/load_agreements/"><code>load_agreements</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_non_empty_options/"><code>_non_empty_options</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_normalise_widget_values/"><code>_normalise_widget_values</code></a></td>
      <td><a href="../../reference/collect_agreement_metadata/"><code>collect_agreement_metadata</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_normalize_optional_date/"><code>_normalize_optional_date</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_parse_date/"><code>_parse_date</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_read_agreement_widget_values/"><code>_read_agreement_widget_values</code></a></td>
      <td><a href="../../reference/collect_agreement_metadata/"><code>collect_agreement_metadata</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_record_base/"><code>_record_base</code></a></td>
      <td><a href="../../reference/collect_agreement_metadata/"><code>collect_agreement_metadata</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_require_fields/"><code>_require_fields</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_resolve_committed_at/"><code>_resolve_committed_at</code></a></td>
      <td><a href="../../reference/collect_agreement_metadata/"><code>collect_agreement_metadata</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_safe_table_prefix/"><code>_safe_table_prefix</code></a></td>
      <td><a href="../../reference/commit_agreement_metadata/"><code>commit_agreement_metadata</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_select_record_fields/"><code>_select_record_fields</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_validate_yes_no/"><code>_validate_yes_no</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_widget_dropdown/"><code>_widget_dropdown</code></a></td>
      <td><a href="../../reference/create_agreement_widgets/"><code>create_agreement_widgets</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_widget_text/"><code>_widget_text</code></a></td>
      <td><a href="../../reference/create_agreement_widgets/"><code>create_agreement_widgets</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_write_record/"><code>_write_record</code></a></td>
      <td><a href="../../reference/commit_agreement_metadata/"><code>commit_agreement_metadata</code></a></td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_agreement_option_label"><code>_agreement_option_label</code></a>
</li>
<li>
<a class="reference-chip" href="#_agreement_widget_specs"><code>_agreement_widget_specs</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_non_empty_options"><code>_non_empty_options</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_agreement_record"><code>_build_agreement_record</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_select_record_fields"><code>_select_record_fields</code></a>
</li>
<li>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>
</li>
<li>
<a class="reference-chip" href="#_derive_agreement_status"><code>_derive_agreement_status</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_parse_date"><code>_parse_date</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_fabric_widgets"><code>_get_fabric_widgets</code></a>
</li>
<li>
<a class="reference-chip" href="#_latest_distinct_agreements"><code>_latest_distinct_agreements</code></a>
</li>
<li>
<a class="reference-chip" href="#_non_empty_options"><code>_non_empty_options</code></a>
</li>
<li>
<a class="reference-chip" href="#_normalise_widget_values"><code>_normalise_widget_values</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_derive_agreement_status"><code>_derive_agreement_status</code></a>, <a class="reference-chip" href="#_normalize_optional_date"><code>_normalize_optional_date</code></a>, <a class="reference-chip" href="#_parse_date"><code>_parse_date</code></a>, <a class="reference-chip" href="#_require_fields"><code>_require_fields</code></a>, <a class="reference-chip" href="#_validate_yes_no"><code>_validate_yes_no</code></a>
</li>
<li>
<a class="reference-chip" href="#_normalize_optional_date"><code>_normalize_optional_date</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_parse_date"><code>_parse_date</code></a>
</li>
<li>
<a class="reference-chip" href="#_parse_date"><code>_parse_date</code></a>
</li>
<li>
<a class="reference-chip" href="#_read_agreement_widget_values"><code>_read_agreement_widget_values</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_get_fabric_widgets"><code>_get_fabric_widgets</code></a>
</li>
<li>
<a class="reference-chip" href="#_record_base"><code>_record_base</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_resolve_committed_at"><code>_resolve_committed_at</code></a>
</li>
<li>
<a class="reference-chip" href="#_require_fields"><code>_require_fields</code></a>
</li>
<li>
<a class="reference-chip" href="#_resolve_committed_at"><code>_resolve_committed_at</code></a>
</li>
<li>
<a class="reference-chip" href="#_safe_table_prefix"><code>_safe_table_prefix</code></a>
</li>
<li>
<a class="reference-chip" href="#_select_record_fields"><code>_select_record_fields</code></a>
</li>
<li>
<a class="reference-chip" href="#_validate_yes_no"><code>_validate_yes_no</code></a>
</li>
<li>
<a class="reference-chip" href="#_widget_dropdown"><code>_widget_dropdown</code></a>
</li>
<li>
<a class="reference-chip" href="#_widget_text"><code>_widget_text</code></a>
</li>
<li>
<a class="reference-chip" href="#_write_record"><code>_write_record</code></a>
</li>
</ul>
</details>

### External callers

None.
### External callees

**metadata**
<a class="reference-chip" href="../metadata/#_resolve_action_by"><code>_resolve_action_by</code></a>, <a class="reference-chip" href="../metadata/#_runtime_context"><code>_runtime_context</code></a>
