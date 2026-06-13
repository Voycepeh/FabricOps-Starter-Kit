# `governance_review` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 8</span><span class="reference-chip">Internal helpers: 46</span><span class="reference-chip">Outbound: 4</span><span class="reference-chip">Inbound: 2</span></div>

## Module purpose

Owns table-scoped 03_governance catalogue selection, business context review, DQ-rule review guidance, classification review, AI-assisted internal drafting helpers, and approved metadata commit through record_table_governance.

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
      <td>Owns table-scoped 03_governance catalogue selection, business context review, DQ-rule review guidance, classification review, AI-assisted internal drafting helpers, and approved metadata commit through record_table_governance.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>8</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>46</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>2</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>4</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td><code>config</code>, <code>pipeline</code></td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>config</code>, <code>data_profiling</code>, <code>fabric_input_output</code>, <code>metadata</code></td>
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
      <td><a href="../../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Enforce approved active DQ rules as a target-write guardrail without filtering rows.</td>
      <td><code>_dq_failed_row_count</code> (internal), <code>_dq_summary</code> (internal), <code>_dq_tagged_dataframe</code> (internal), <code>_load_active_dq_rules</code> (internal), <code>_run_dq_guardrail_checks</code> (internal), <code>_summarize_dq_guardrail</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/get_selected_catalogue_table/"><code>get_selected_catalogue_table</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Return the table selected by widget_select_catalogue_table.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Load column profile rows for the selected catalogue table.</td>
      <td><code>_coerce_rows</code> (internal), <code>_is_success</code> (internal), <code>_value</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/record_table_governance/"><code>record_table_governance</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Persist approved table-governance context, DQ-rule, and classification evidence in one v1 commit action.</td>
      <td><code>_build_classification_records</code> (internal), <code>_build_column_context_records</code> (internal), <code>_build_dq_rule_records</code> (internal), <code>_review_governance_evidence</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_review_column_classification/"><code>widget_review_column_classification</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render standalone sensitivity and PII classification review guidance for selected profile rows.</td>
      <td><code>_display_review_guidance</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_review_column_context/"><code>widget_review_column_context</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render standalone business-context review guidance for selected profile rows.</td>
      <td><code>_display_review_guidance</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render standalone DQ-rule review guidance for selected profile rows.</td>
      <td><code>_canonical_dq_rule_type</code> (internal), <code>_dq_parameter_fields_for_rule_type</code> (internal), <code>_dq_rule_display_rows</code> (internal), <code>_draft_dq_rules</code> (internal), <code>_validate_dq_rules</code> (internal), <code>_value</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_select_catalogue_table/"><code>widget_select_catalogue_table</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render a searchable selector for latest successful catalogue profiles.</td>
      <td><code>_catalogue_table_options</code> (internal), <code>_coerce_rows</code> (internal)</td>
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
<a class="reference-chip" href="../../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_dq_failed_row_count</code></span>, <span class="reference-chip"><code>_dq_summary</code></span>, <span class="reference-chip"><code>_dq_tagged_dataframe</code></span>, <span class="reference-chip"><code>_load_active_dq_rules</code></span>, <span class="reference-chip"><code>_run_dq_guardrail_checks</code></span>, <span class="reference-chip"><code>_summarize_dq_guardrail</code></span>
</li>
<li>
<a class="reference-chip" href="../../reference/get_selected_catalogue_table/"><code>get_selected_catalogue_table</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_coerce_rows</code></span>, <span class="reference-chip"><code>_is_success</code></span>, <span class="reference-chip"><code>_value</code></span>
</li>
<li>
<a class="reference-chip" href="../../reference/record_table_governance/"><code>record_table_governance</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_build_classification_records</code></span>, <span class="reference-chip"><code>_build_column_context_records</code></span>, <span class="reference-chip"><code>_build_dq_rule_records</code></span>, <span class="reference-chip"><code>_review_governance_evidence</code></span>
</li>
<li>
<a class="reference-chip" href="../../reference/widget_review_column_classification/"><code>widget_review_column_classification</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_display_review_guidance</code></span>
</li>
<li>
<a class="reference-chip" href="../../reference/widget_review_column_context/"><code>widget_review_column_context</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_display_review_guidance</code></span>
</li>
<li>
<a class="reference-chip" href="../../reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_canonical_dq_rule_type</code></span>, <span class="reference-chip"><code>_dq_parameter_fields_for_rule_type</code></span>, <span class="reference-chip"><code>_dq_rule_display_rows</code></span>, <span class="reference-chip"><code>_draft_dq_rules</code></span>, <span class="reference-chip"><code>_validate_dq_rules</code></span>, <span class="reference-chip"><code>_value</code></span>
</li>
<li>
<a class="reference-chip" href="../../reference/widget_select_catalogue_table/"><code>widget_select_catalogue_table</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_catalogue_table_options</code></span>, <span class="reference-chip"><code>_coerce_rows</code></span>
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
      <td><code>_approved_column_identity</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_approved_review_context</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_build_classification_records</code></td>
      <td><a href="../../reference/record_table_governance/"><code>record_table_governance</code></a></td>
    </tr>
    <tr>
      <td><code>_build_column_context_records</code></td>
      <td><a href="../../reference/record_table_governance/"><code>record_table_governance</code></a></td>
    </tr>
    <tr>
      <td><code>_build_dq_rule_records</code></td>
      <td><a href="../../reference/record_table_governance/"><code>record_table_governance</code></a></td>
    </tr>
    <tr>
      <td><code>_canonical_dq_rule_type</code></td>
      <td><a href="../../reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_catalogue_table_options</code></td>
      <td><a href="../../reference/widget_select_catalogue_table/"><code>widget_select_catalogue_table</code></a></td>
    </tr>
    <tr>
      <td><code>_coerce_rows</code></td>
      <td><a href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a>, <a href="../../reference/widget_select_catalogue_table/"><code>widget_select_catalogue_table</code></a></td>
    </tr>
    <tr>
      <td><code>_display_review_guidance</code></td>
      <td><a href="../../reference/widget_review_column_classification/"><code>widget_review_column_classification</code></a>, <a href="../../reference/widget_review_column_context/"><code>widget_review_column_context</code></a></td>
    </tr>
    <tr>
      <td><code>_dq_check_status</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_dq_failed_expression</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_dq_failed_row_count</code></td>
      <td><a href="../../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_dq_parameter_fields_for_rule_type</code></td>
      <td><a href="../../reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_dq_rule_display_rows</code></td>
      <td><a href="../../reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_dq_rule_parameter_payload</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_dq_rule_parameters_summary</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_dq_summary</code></td>
      <td><a href="../../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_dq_tagged_dataframe</code></td>
      <td><a href="../../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_draft_business_context</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_draft_dq_rules</code></td>
      <td><a href="../../reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_draft_governance</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_extract_assignment_payload</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_get_governance_metadata_schemas</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_is_success</code></td>
      <td><a href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a></td>
    </tr>
    <tr>
      <td><code>_is_table_not_found_error</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_json</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_latest_dq_rule_versions</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_latest_row</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_load_active_dq_rules</code></td>
      <td><a href="../../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_parse_ai_dict_response</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_parse_dq_ai_suggestions</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_prepare_dq_profile_input_rows</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_read_metadata_rows</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_review_governance_evidence</code></td>
      <td><a href="../../reference/record_table_governance/"><code>record_table_governance</code></a></td>
    </tr>
    <tr>
      <td><code>_run_dq_guardrail_checks</code></td>
      <td><a href="../../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_run_fabric_ai_drafting</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_schema</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_schema_field_names</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_spark_sql_helpers</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_spark_types</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_status_is_failed</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_status_is_warning</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_summarize_dq_guardrail</code></td>
      <td><a href="../../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_validate_dq_rules</code></td>
      <td><a href="../../reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_validate_schema_field_names</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_value</code></td>
      <td><a href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a>, <a href="../../reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<span class="reference-chip"><code>_approved_column_identity</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_approved_review_context</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_build_classification_records</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_approved_column_identity</code></span>, <span class="reference-chip"><code>_approved_review_context</code></span>, <span class="reference-chip"><code>_json</code></span>
</li>
<li>
<span class="reference-chip"><code>_build_column_context_records</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_approved_column_identity</code></span>, <span class="reference-chip"><code>_approved_review_context</code></span>, <span class="reference-chip"><code>_json</code></span>
</li>
<li>
<span class="reference-chip"><code>_build_dq_rule_records</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_approved_column_identity</code></span>, <span class="reference-chip"><code>_approved_review_context</code></span>, <span class="reference-chip"><code>_canonical_dq_rule_type</code></span>, <span class="reference-chip"><code>_dq_rule_parameter_payload</code></span>, <span class="reference-chip"><code>_json</code></span>, <span class="reference-chip"><code>_validate_dq_rules</code></span>
</li>
<li>
<span class="reference-chip"><code>_canonical_dq_rule_type</code></span>
</li>
<li>
<span class="reference-chip"><code>_catalogue_table_options</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_is_success</code></span>, <span class="reference-chip"><code>_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_coerce_rows</code></span>
</li>
<li>
<span class="reference-chip"><code>_display_review_guidance</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_dq_check_status</code></span>
</li>
<li>
<span class="reference-chip"><code>_dq_failed_expression</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_spark_sql_helpers</code></span>, <span class="reference-chip"><code>_validate_dq_rules</code></span>
</li>
<li>
<span class="reference-chip"><code>_dq_failed_row_count</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_dq_failed_expression</code></span>, <span class="reference-chip"><code>_spark_sql_helpers</code></span>
</li>
<li>
<span class="reference-chip"><code>_dq_parameter_fields_for_rule_type</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_canonical_dq_rule_type</code></span>
</li>
<li>
<span class="reference-chip"><code>_dq_rule_display_rows</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_canonical_dq_rule_type</code></span>, <span class="reference-chip"><code>_dq_rule_parameters_summary</code></span>
</li>
<li>
<span class="reference-chip"><code>_dq_rule_parameter_payload</code></span>
</li>
<li>
<span class="reference-chip"><code>_dq_rule_parameters_summary</code></span>
</li>
<li>
<span class="reference-chip"><code>_dq_summary</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_summarize_dq_guardrail</code></span>
</li>
<li>
<span class="reference-chip"><code>_dq_tagged_dataframe</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_dq_failed_expression</code></span>, <span class="reference-chip"><code>_spark_sql_helpers</code></span>
</li>
<li>
<span class="reference-chip"><code>_draft_business_context</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_run_fabric_ai_drafting</code></span>
</li>
<li>
<span class="reference-chip"><code>_draft_dq_rules</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_canonical_dq_rule_type</code></span>, <span class="reference-chip"><code>_extract_assignment_payload</code></span>, <span class="reference-chip"><code>_prepare_dq_profile_input_rows</code></span>, <span class="reference-chip"><code>_run_fabric_ai_drafting</code></span>, <span class="reference-chip"><code>_validate_dq_rules</code></span>
</li>
<li>
<span class="reference-chip"><code>_draft_governance</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_run_fabric_ai_drafting</code></span>
</li>
<li>
<span class="reference-chip"><code>_extract_assignment_payload</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_coerce_rows</code></span>, <span class="reference-chip"><code>_parse_ai_dict_response</code></span>
</li>
<li>
<span class="reference-chip"><code>_get_governance_metadata_schemas</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_schema</code></span>, <span class="reference-chip"><code>_spark_types</code></span>
</li>
<li>
<span class="reference-chip"><code>_is_success</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_is_table_not_found_error</code></span>
</li>
<li>
<span class="reference-chip"><code>_json</code></span>
</li>
<li>
<span class="reference-chip"><code>_latest_dq_rule_versions</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_spark_sql_helpers</code></span>
</li>
<li>
<span class="reference-chip"><code>_latest_row</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_load_active_dq_rules</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_canonical_dq_rule_type</code></span>, <span class="reference-chip"><code>_coerce_rows</code></span>, <span class="reference-chip"><code>_latest_dq_rule_versions</code></span>, <span class="reference-chip"><code>_spark_sql_helpers</code></span>, <span class="reference-chip"><code>_validate_dq_rules</code></span>
</li>
<li>
<span class="reference-chip"><code>_parse_ai_dict_response</code></span>
</li>
<li>
<span class="reference-chip"><code>_parse_dq_ai_suggestions</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_canonical_dq_rule_type</code></span>, <span class="reference-chip"><code>_extract_assignment_payload</code></span>, <span class="reference-chip"><code>_validate_dq_rules</code></span>
</li>
<li>
<span class="reference-chip"><code>_prepare_dq_profile_input_rows</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_spark_sql_helpers</code></span>
</li>
<li>
<span class="reference-chip"><code>_read_metadata_rows</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_coerce_rows</code></span>
</li>
<li>
<span class="reference-chip"><code>_review_governance_evidence</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_latest_row</code></span>, <span class="reference-chip"><code>_read_metadata_rows</code></span>, <span class="reference-chip"><code>_status_is_failed</code></span>, <span class="reference-chip"><code>_status_is_warning</code></span>, <span class="reference-chip"><code>_value</code></span>, <a class="reference-chip" href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a>
</li>
<li>
<span class="reference-chip"><code>_run_dq_guardrail_checks</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_dq_check_status</code></span>, <span class="reference-chip"><code>_dq_failed_expression</code></span>, <span class="reference-chip"><code>_spark_sql_helpers</code></span>, <span class="reference-chip"><code>_validate_dq_rules</code></span>
</li>
<li>
<span class="reference-chip"><code>_run_fabric_ai_drafting</code></span>
</li>
<li>
<span class="reference-chip"><code>_schema</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_spark_types</code></span>, <span class="reference-chip"><code>_validate_schema_field_names</code></span>
</li>
<li>
<span class="reference-chip"><code>_schema_field_names</code></span>
</li>
<li>
<span class="reference-chip"><code>_spark_sql_helpers</code></span>
</li>
<li>
<span class="reference-chip"><code>_spark_types</code></span>
</li>
<li>
<span class="reference-chip"><code>_status_is_failed</code></span>
</li>
<li>
<span class="reference-chip"><code>_status_is_warning</code></span>
</li>
<li>
<span class="reference-chip"><code>_summarize_dq_guardrail</code></span>
</li>
<li>
<span class="reference-chip"><code>_validate_dq_rules</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_canonical_dq_rule_type</code></span>
</li>
<li>
<span class="reference-chip"><code>_validate_schema_field_names</code></span>
</li>
<li>
<span class="reference-chip"><code>_value</code></span>
</li>
</ul>
</details>

### External callers

**config**
<a class="reference-chip" href="../config/#_get_active_metadata_tables"><code>_get_active_metadata_tables</code></a>, <a class="reference-chip" href="../config/#_get_metadata_table_schema_registry"><code>_get_metadata_table_schema_registry</code></a>, <a class="reference-chip" href="../config/#_setup_metadata_table_registry"><code>_setup_metadata_table_registry</code></a>, <a class="reference-chip" href="../../reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>

**pipeline**
<a class="reference-chip" href="../../reference/run_table_guardrails/"><code>run_table_guardrails</code></a>

### External callees

**config**
<a class="reference-chip" href="../config/#_current_audit_timestamp"><code>_current_audit_timestamp</code></a>

**data_profiling**
<a class="reference-chip" href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a>

**fabric_input_output**
<a class="reference-chip" href="../fabric_input_output/#_configured_lakehouse_schema"><code>_configured_lakehouse_schema</code></a>, <a class="reference-chip" href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a>, <a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>

**metadata**
<a class="reference-chip" href="../metadata/#_build_dq_rule_key"><code>_build_dq_rule_key</code></a>, <a class="reference-chip" href="../metadata/#_build_metadata_column_key"><code>_build_metadata_column_key</code></a>, <a class="reference-chip" href="../metadata/#_build_metadata_table_key"><code>_build_metadata_table_key</code></a>, <a class="reference-chip" href="../metadata/#_build_runtime_audit_fields"><code>_build_runtime_audit_fields</code></a>, <a class="reference-chip" href="../metadata/#_now_utc_iso"><code>_now_utc_iso</code></a>, <a class="reference-chip" href="../metadata/#_resolve_action_by"><code>_resolve_action_by</code></a>
