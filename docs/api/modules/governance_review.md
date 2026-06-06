# `governance_review` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 7</span><span class="reference-chip">Internal helpers: 24</span><span class="reference-chip">Outbound: 2</span><span class="reference-chip">Inbound: 1</span></div>

## Module purpose

Owns table-scoped 04_gov catalogue selection, explicit approval record builders, and metadata commit helpers.

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
      <td><code>governance_review</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns table-scoped 04_gov catalogue selection, explicit approval record builders, and metadata commit helpers.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>7</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>24</td>
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
      <td><code>config</code></td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>fabric_input_output</code>, <code>metadata</code></td>
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
      <td><a href="../../reference/get_selected_catalogue_table/"><code>get_selected_catalogue_table</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Return the table selected by widget_select_catalogue_table.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Load column profile rows for the selected catalogue table.</td>
      <td><a href="../../reference/internal/governance_review/_coerce_rows/"><code>_coerce_rows</code></a> (internal), <a href="../../reference/internal/governance_review/_is_success/"><code>_is_success</code></a> (internal), <a href="../../reference/internal/governance_review/_row_metadata_table_key/"><code>_row_metadata_table_key</code></a> (internal), <a href="../../reference/internal/governance_review/_value/"><code>_value</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/record_table_governance/"><code>record_table_governance</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Persist approved table-governance context, DQ-rule, and classification evidence in one v1 commit action.</td>
      <td><a href="../../reference/internal/governance_review/_build_classification_records/"><code>_build_classification_records</code></a> (internal), <a href="../../reference/internal/governance_review/_build_column_context_records/"><code>_build_column_context_records</code></a> (internal), <a href="../../reference/internal/governance_review/_build_dq_rule_records/"><code>_build_dq_rule_records</code></a> (internal), <a href="../../reference/internal/governance_review/_commit_column_classification/"><code>_commit_column_classification</code></a> (internal), <a href="../../reference/internal/governance_review/_commit_column_context/"><code>_commit_column_context</code></a> (internal), <a href="../../reference/internal/governance_review/_commit_dq_rules/"><code>_commit_dq_rules</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_review_column_classification/"><code>widget_review_column_classification</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Render standalone sensitivity and PII classification review guidance for selected profile rows.</td>
      <td><a href="../../reference/internal/governance_review/_display_review_guidance/"><code>_display_review_guidance</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_review_column_context/"><code>widget_review_column_context</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Render standalone business-context review guidance for selected profile rows.</td>
      <td><a href="../../reference/internal/governance_review/_display_review_guidance/"><code>_display_review_guidance</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Render standalone DQ-rule review guidance for selected profile rows.</td>
      <td><a href="../../reference/internal/governance_review/_display_review_guidance/"><code>_display_review_guidance</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_select_catalogue_table/"><code>widget_select_catalogue_table</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Render a searchable selector for latest successful catalogue profiles.</td>
      <td><a href="../../reference/internal/governance_review/_catalogue_table_options/"><code>_catalogue_table_options</code></a> (internal), <a href="../../reference/internal/governance_review/_coerce_rows/"><code>_coerce_rows</code></a> (internal)</td>
    </tr>
  </tbody>
</table>
</div>

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>governance_review</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/get_selected_catalogue_table/"><code>get_selected_catalogue_table</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>, <a class="reference-chip" href="#_is_success"><code>_is_success</code></a>, <a class="reference-chip" href="#_row_metadata_table_key"><code>_row_metadata_table_key</code></a>, <a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/record_table_governance/"><code>record_table_governance</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_build_classification_records"><code>_build_classification_records</code></a>, <a class="reference-chip" href="#_build_column_context_records"><code>_build_column_context_records</code></a>, <a class="reference-chip" href="#_build_dq_rule_records"><code>_build_dq_rule_records</code></a>, <a class="reference-chip" href="#_commit_column_classification"><code>_commit_column_classification</code></a>, <a class="reference-chip" href="#_commit_column_context"><code>_commit_column_context</code></a>, <a class="reference-chip" href="#_commit_dq_rules"><code>_commit_dq_rules</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/widget_review_column_classification/"><code>widget_review_column_classification</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_display_review_guidance"><code>_display_review_guidance</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/widget_review_column_context/"><code>widget_review_column_context</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_display_review_guidance"><code>_display_review_guidance</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_display_review_guidance"><code>_display_review_guidance</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/widget_select_catalogue_table/"><code>widget_select_catalogue_table</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_catalogue_table_options"><code>_catalogue_table_options</code></a>, <a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>
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
      <td><a href="../../reference/internal/governance_review/_audit/"><code>_audit</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_build_classification_records/"><code>_build_classification_records</code></a></td>
      <td><a href="../../reference/record_table_governance/"><code>record_table_governance</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_build_column_context_records/"><code>_build_column_context_records</code></a></td>
      <td><a href="../../reference/record_table_governance/"><code>record_table_governance</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_build_dq_rule_records/"><code>_build_dq_rule_records</code></a></td>
      <td><a href="../../reference/record_table_governance/"><code>record_table_governance</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_build_profile_summary/"><code>_build_profile_summary</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_catalogue_table_options/"><code>_catalogue_table_options</code></a></td>
      <td><a href="../../reference/widget_select_catalogue_table/"><code>widget_select_catalogue_table</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_coerce_rows/"><code>_coerce_rows</code></a></td>
      <td><a href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a>, <a href="../../reference/widget_select_catalogue_table/"><code>widget_select_catalogue_table</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_commit_column_classification/"><code>_commit_column_classification</code></a></td>
      <td><a href="../../reference/record_table_governance/"><code>record_table_governance</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_commit_column_context/"><code>_commit_column_context</code></a></td>
      <td><a href="../../reference/record_table_governance/"><code>record_table_governance</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_commit_dq_rules/"><code>_commit_dq_rules</code></a></td>
      <td><a href="../../reference/record_table_governance/"><code>record_table_governance</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_display_review_guidance/"><code>_display_review_guidance</code></a></td>
      <td><a href="../../reference/widget_review_column_classification/"><code>widget_review_column_classification</code></a>, <a href="../../reference/widget_review_column_context/"><code>widget_review_column_context</code></a>, <a href="../../reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_get_governance_metadata_schemas/"><code>_get_governance_metadata_schemas</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_is_success/"><code>_is_success</code></a></td>
      <td><a href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_is_table_not_found_error/"><code>_is_table_not_found_error</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_json/"><code>_json</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_latest_by_column/"><code>_latest_by_column</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_optional_ai_generate_response/"><code>_optional_ai_generate_response</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_row_metadata_table_key/"><code>_row_metadata_table_key</code></a></td>
      <td><a href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_schema/"><code>_schema</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_schema_field_names/"><code>_schema_field_names</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_setup_governance_metadata_tables/"><code>_setup_governance_metadata_tables</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_spark_types/"><code>_spark_types</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_value/"><code>_value</code></a></td>
      <td><a href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_widget_review_table_governance/"><code>_widget_review_table_governance</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_audit"><code>_audit</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_classification_records"><code>_build_classification_records</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_audit"><code>_audit</code></a>, <a class="reference-chip" href="#_json"><code>_json</code></a>, <a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_column_context_records"><code>_build_column_context_records</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_audit"><code>_audit</code></a>, <a class="reference-chip" href="#_json"><code>_json</code></a>, <a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_dq_rule_records"><code>_build_dq_rule_records</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_audit"><code>_audit</code></a>, <a class="reference-chip" href="#_json"><code>_json</code></a>, <a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_profile_summary"><code>_build_profile_summary</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_catalogue_table_options"><code>_catalogue_table_options</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_is_success"><code>_is_success</code></a>, <a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>
</li>
<li>
<a class="reference-chip" href="#_commit_column_classification"><code>_commit_column_classification</code></a>
</li>
<li>
<a class="reference-chip" href="#_commit_column_context"><code>_commit_column_context</code></a>
</li>
<li>
<a class="reference-chip" href="#_commit_dq_rules"><code>_commit_dq_rules</code></a>
</li>
<li>
<a class="reference-chip" href="#_display_review_guidance"><code>_display_review_guidance</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_governance_metadata_schemas"><code>_get_governance_metadata_schemas</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_schema"><code>_schema</code></a>, <a class="reference-chip" href="#_spark_types"><code>_spark_types</code></a>
</li>
<li>
<a class="reference-chip" href="#_is_success"><code>_is_success</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_is_table_not_found_error"><code>_is_table_not_found_error</code></a>
</li>
<li>
<a class="reference-chip" href="#_json"><code>_json</code></a>
</li>
<li>
<a class="reference-chip" href="#_latest_by_column"><code>_latest_by_column</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>
</li>
<li>
<a class="reference-chip" href="#_optional_ai_generate_response"><code>_optional_ai_generate_response</code></a>
</li>
<li>
<a class="reference-chip" href="#_row_metadata_table_key"><code>_row_metadata_table_key</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_schema"><code>_schema</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_spark_types"><code>_spark_types</code></a>
</li>
<li>
<a class="reference-chip" href="#_schema_field_names"><code>_schema_field_names</code></a>
</li>
<li>
<a class="reference-chip" href="#_setup_governance_metadata_tables"><code>_setup_governance_metadata_tables</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>, <a class="reference-chip" href="#_get_governance_metadata_schemas"><code>_get_governance_metadata_schemas</code></a>, <a class="reference-chip" href="#_is_table_not_found_error"><code>_is_table_not_found_error</code></a>, <a class="reference-chip" href="#_schema_field_names"><code>_schema_field_names</code></a>
</li>
<li>
<a class="reference-chip" href="#_spark_types"><code>_spark_types</code></a>
</li>
<li>
<a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_widget_review_table_governance"><code>_widget_review_table_governance</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
</ul>
</details>

### External callers

**config**
<a class="reference-chip" href="../../reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>

### External callees

**fabric_input_output**
<a class="reference-chip" href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a>, <a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>

**metadata**
<a class="reference-chip" href="../metadata/#_build_dq_rule_key"><code>_build_dq_rule_key</code></a>, <a class="reference-chip" href="../metadata/#_build_metadata_column_key"><code>_build_metadata_column_key</code></a>, <a class="reference-chip" href="../metadata/#_build_metadata_table_key"><code>_build_metadata_table_key</code></a>, <a class="reference-chip" href="../metadata/#_build_runtime_audit_fields"><code>_build_runtime_audit_fields</code></a>, <a class="reference-chip" href="../metadata/#_now_utc_iso"><code>_now_utc_iso</code></a>, <a class="reference-chip" href="../metadata/#_resolve_action_by"><code>_resolve_action_by</code></a>
