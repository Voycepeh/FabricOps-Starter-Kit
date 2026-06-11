# `governance_review` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 8</span><span class="reference-chip">Internal helpers: 47</span><span class="reference-chip">Outbound: 4</span><span class="reference-chip">Inbound: 2</span></div>

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
      <td>47</td>
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
      <td><a href="../../reference/internal/governance_review/_dq_failed_row_count/"><code>_dq_failed_row_count</code></a> (internal), <a href="../../reference/internal/governance_review/_dq_summary/"><code>_dq_summary</code></a> (internal), <a href="../../reference/internal/governance_review/_dq_tagged_dataframe/"><code>_dq_tagged_dataframe</code></a> (internal), <a href="../../reference/internal/governance_review/_load_active_dq_rules/"><code>_load_active_dq_rules</code></a> (internal), <a href="../../reference/internal/governance_review/_run_dq_guardrail_checks/"><code>_run_dq_guardrail_checks</code></a> (internal), <a href="../../reference/internal/governance_review/_summarize_dq_guardrail/"><code>_summarize_dq_guardrail</code></a> (internal)</td>
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
      <td><a href="../../reference/internal/governance_review/_coerce_rows/"><code>_coerce_rows</code></a> (internal), <a href="../../reference/internal/governance_review/_is_success/"><code>_is_success</code></a> (internal), <a href="../../reference/internal/governance_review/_value/"><code>_value</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/record_table_governance/"><code>record_table_governance</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Persist approved table-governance context, DQ-rule, and classification evidence in one v1 commit action.</td>
      <td><a href="../../reference/internal/governance_review/_build_classification_records/"><code>_build_classification_records</code></a> (internal), <a href="../../reference/internal/governance_review/_build_column_context_records/"><code>_build_column_context_records</code></a> (internal), <a href="../../reference/internal/governance_review/_build_dq_rule_records/"><code>_build_dq_rule_records</code></a> (internal), <a href="../../reference/internal/governance_review/_review_governance_evidence/"><code>_review_governance_evidence</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_review_column_classification/"><code>widget_review_column_classification</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render standalone sensitivity and PII classification review guidance for selected profile rows.</td>
      <td><a href="../../reference/internal/governance_review/_display_review_guidance/"><code>_display_review_guidance</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_review_column_context/"><code>widget_review_column_context</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render standalone business-context review guidance for selected profile rows.</td>
      <td><a href="../../reference/internal/governance_review/_display_review_guidance/"><code>_display_review_guidance</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render standalone DQ-rule review guidance for selected profile rows.</td>
      <td><a href="../../reference/internal/governance_review/_canonical_dq_rule_type/"><code>_canonical_dq_rule_type</code></a> (internal), <a href="../../reference/internal/governance_review/_dq_parameter_fields_for_rule_type/"><code>_dq_parameter_fields_for_rule_type</code></a> (internal), <a href="../../reference/internal/governance_review/_dq_rule_display_rows/"><code>_dq_rule_display_rows</code></a> (internal), <a href="../../reference/internal/governance_review/_draft_dq_rules/"><code>_draft_dq_rules</code></a> (internal), <a href="../../reference/internal/governance_review/_validate_dq_rules/"><code>_validate_dq_rules</code></a> (internal), <a href="../../reference/internal/governance_review/_value/"><code>_value</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_select_catalogue_table/"><code>widget_select_catalogue_table</code></a></td>
      <td>Callable</td>
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
<a class="reference-chip" href="../../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_dq_failed_row_count"><code>_dq_failed_row_count</code></a>, <a class="reference-chip" href="#_dq_summary"><code>_dq_summary</code></a>, <a class="reference-chip" href="#_dq_tagged_dataframe"><code>_dq_tagged_dataframe</code></a>, <a class="reference-chip" href="#_load_active_dq_rules"><code>_load_active_dq_rules</code></a>, <a class="reference-chip" href="#_run_dq_guardrail_checks"><code>_run_dq_guardrail_checks</code></a>, <a class="reference-chip" href="#_summarize_dq_guardrail"><code>_summarize_dq_guardrail</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/get_selected_catalogue_table/"><code>get_selected_catalogue_table</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>, <a class="reference-chip" href="#_is_success"><code>_is_success</code></a>, <a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/record_table_governance/"><code>record_table_governance</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_build_classification_records"><code>_build_classification_records</code></a>, <a class="reference-chip" href="#_build_column_context_records"><code>_build_column_context_records</code></a>, <a class="reference-chip" href="#_build_dq_rule_records"><code>_build_dq_rule_records</code></a>, <a class="reference-chip" href="#_review_governance_evidence"><code>_review_governance_evidence</code></a>
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
<a class="reference-chip" href="#_canonical_dq_rule_type"><code>_canonical_dq_rule_type</code></a>, <a class="reference-chip" href="#_dq_parameter_fields_for_rule_type"><code>_dq_parameter_fields_for_rule_type</code></a>, <a class="reference-chip" href="#_dq_rule_display_rows"><code>_dq_rule_display_rows</code></a>, <a class="reference-chip" href="#_draft_dq_rules"><code>_draft_dq_rules</code></a>, <a class="reference-chip" href="#_validate_dq_rules"><code>_validate_dq_rules</code></a>, <a class="reference-chip" href="#_value"><code>_value</code></a>
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
      <td><a href="../../reference/internal/governance_review/_approved_column_identity/"><code>_approved_column_identity</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_approved_review_context/"><code>_approved_review_context</code></a></td>
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
      <td><a href="../../reference/internal/governance_review/_canonical_dq_rule_type/"><code>_canonical_dq_rule_type</code></a></td>
      <td><a href="../../reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></td>
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
      <td><a href="../../reference/internal/governance_review/_display_review_guidance/"><code>_display_review_guidance</code></a></td>
      <td><a href="../../reference/widget_review_column_classification/"><code>widget_review_column_classification</code></a>, <a href="../../reference/widget_review_column_context/"><code>widget_review_column_context</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_dq_check_status/"><code>_dq_check_status</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_dq_failed_expression/"><code>_dq_failed_expression</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_dq_failed_row_count/"><code>_dq_failed_row_count</code></a></td>
      <td><a href="../../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_dq_parameter_fields_for_rule_type/"><code>_dq_parameter_fields_for_rule_type</code></a></td>
      <td><a href="../../reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_dq_rule_display_rows/"><code>_dq_rule_display_rows</code></a></td>
      <td><a href="../../reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_dq_rule_parameter_payload/"><code>_dq_rule_parameter_payload</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_dq_rule_parameters_summary/"><code>_dq_rule_parameters_summary</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_dq_summary/"><code>_dq_summary</code></a></td>
      <td><a href="../../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_dq_tagged_dataframe/"><code>_dq_tagged_dataframe</code></a></td>
      <td><a href="../../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_draft_business_context/"><code>_draft_business_context</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_draft_dq_rules/"><code>_draft_dq_rules</code></a></td>
      <td><a href="../../reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_draft_governance/"><code>_draft_governance</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_extract_assignment_payload/"><code>_extract_assignment_payload</code></a></td>
      <td>—</td>
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
      <td><a href="../../reference/internal/governance_review/_latest_dq_rule_versions/"><code>_latest_dq_rule_versions</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_latest_row/"><code>_latest_row</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_load_active_dq_rules/"><code>_load_active_dq_rules</code></a></td>
      <td><a href="../../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_parse_ai_dict_response/"><code>_parse_ai_dict_response</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_parse_dq_ai_suggestions/"><code>_parse_dq_ai_suggestions</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_prepare_dq_profile_input_rows/"><code>_prepare_dq_profile_input_rows</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_read_metadata_rows/"><code>_read_metadata_rows</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_review_governance_evidence/"><code>_review_governance_evidence</code></a></td>
      <td><a href="../../reference/record_table_governance/"><code>record_table_governance</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_run_dq_guardrail_checks/"><code>_run_dq_guardrail_checks</code></a></td>
      <td><a href="../../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_run_fabric_ai_drafting/"><code>_run_fabric_ai_drafting</code></a></td>
      <td>—</td>
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
      <td><a href="../../reference/internal/governance_review/_spark_sql_helpers/"><code>_spark_sql_helpers</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_spark_types/"><code>_spark_types</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_status_is_failed/"><code>_status_is_failed</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_status_is_warning/"><code>_status_is_warning</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_summarize_dq_guardrail/"><code>_summarize_dq_guardrail</code></a></td>
      <td><a href="../../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_validate_dq_rules/"><code>_validate_dq_rules</code></a></td>
      <td><a href="../../reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_validate_schema_field_names/"><code>_validate_schema_field_names</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/governance_review/_value/"><code>_value</code></a></td>
      <td><a href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a>, <a href="../../reference/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_approved_column_identity"><code>_approved_column_identity</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_approved_review_context"><code>_approved_review_context</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_classification_records"><code>_build_classification_records</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_approved_column_identity"><code>_approved_column_identity</code></a>, <a class="reference-chip" href="#_approved_review_context"><code>_approved_review_context</code></a>, <a class="reference-chip" href="#_json"><code>_json</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_column_context_records"><code>_build_column_context_records</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_approved_column_identity"><code>_approved_column_identity</code></a>, <a class="reference-chip" href="#_approved_review_context"><code>_approved_review_context</code></a>, <a class="reference-chip" href="#_json"><code>_json</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_dq_rule_records"><code>_build_dq_rule_records</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_approved_column_identity"><code>_approved_column_identity</code></a>, <a class="reference-chip" href="#_approved_review_context"><code>_approved_review_context</code></a>, <a class="reference-chip" href="#_canonical_dq_rule_type"><code>_canonical_dq_rule_type</code></a>, <a class="reference-chip" href="#_dq_rule_parameter_payload"><code>_dq_rule_parameter_payload</code></a>, <a class="reference-chip" href="#_json"><code>_json</code></a>, <a class="reference-chip" href="#_validate_dq_rules"><code>_validate_dq_rules</code></a>
</li>
<li>
<a class="reference-chip" href="#_canonical_dq_rule_type"><code>_canonical_dq_rule_type</code></a>
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
<a class="reference-chip" href="#_display_review_guidance"><code>_display_review_guidance</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_dq_check_status"><code>_dq_check_status</code></a>
</li>
<li>
<a class="reference-chip" href="#_dq_failed_expression"><code>_dq_failed_expression</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_spark_sql_helpers"><code>_spark_sql_helpers</code></a>, <a class="reference-chip" href="#_validate_dq_rules"><code>_validate_dq_rules</code></a>
</li>
<li>
<a class="reference-chip" href="#_dq_failed_row_count"><code>_dq_failed_row_count</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_dq_failed_expression"><code>_dq_failed_expression</code></a>, <a class="reference-chip" href="#_spark_sql_helpers"><code>_spark_sql_helpers</code></a>
</li>
<li>
<a class="reference-chip" href="#_dq_parameter_fields_for_rule_type"><code>_dq_parameter_fields_for_rule_type</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_canonical_dq_rule_type"><code>_canonical_dq_rule_type</code></a>
</li>
<li>
<a class="reference-chip" href="#_dq_rule_display_rows"><code>_dq_rule_display_rows</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_canonical_dq_rule_type"><code>_canonical_dq_rule_type</code></a>, <a class="reference-chip" href="#_dq_rule_parameters_summary"><code>_dq_rule_parameters_summary</code></a>
</li>
<li>
<a class="reference-chip" href="#_dq_rule_parameter_payload"><code>_dq_rule_parameter_payload</code></a>
</li>
<li>
<a class="reference-chip" href="#_dq_rule_parameters_summary"><code>_dq_rule_parameters_summary</code></a>
</li>
<li>
<a class="reference-chip" href="#_dq_summary"><code>_dq_summary</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_summarize_dq_guardrail"><code>_summarize_dq_guardrail</code></a>
</li>
<li>
<a class="reference-chip" href="#_dq_tagged_dataframe"><code>_dq_tagged_dataframe</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_dq_failed_expression"><code>_dq_failed_expression</code></a>, <a class="reference-chip" href="#_spark_sql_helpers"><code>_spark_sql_helpers</code></a>
</li>
<li>
<a class="reference-chip" href="#_draft_business_context"><code>_draft_business_context</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_run_fabric_ai_drafting"><code>_run_fabric_ai_drafting</code></a>
</li>
<li>
<a class="reference-chip" href="#_draft_dq_rules"><code>_draft_dq_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_canonical_dq_rule_type"><code>_canonical_dq_rule_type</code></a>, <a class="reference-chip" href="#_extract_assignment_payload"><code>_extract_assignment_payload</code></a>, <a class="reference-chip" href="#_prepare_dq_profile_input_rows"><code>_prepare_dq_profile_input_rows</code></a>, <a class="reference-chip" href="#_run_fabric_ai_drafting"><code>_run_fabric_ai_drafting</code></a>, <a class="reference-chip" href="#_validate_dq_rules"><code>_validate_dq_rules</code></a>
</li>
<li>
<a class="reference-chip" href="#_draft_governance"><code>_draft_governance</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_run_fabric_ai_drafting"><code>_run_fabric_ai_drafting</code></a>
</li>
<li>
<a class="reference-chip" href="#_extract_assignment_payload"><code>_extract_assignment_payload</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>, <a class="reference-chip" href="#_parse_ai_dict_response"><code>_parse_ai_dict_response</code></a>
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
<a class="reference-chip" href="#_latest_dq_rule_versions"><code>_latest_dq_rule_versions</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_spark_sql_helpers"><code>_spark_sql_helpers</code></a>
</li>
<li>
<a class="reference-chip" href="#_latest_row"><code>_latest_row</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_load_active_dq_rules"><code>_load_active_dq_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_canonical_dq_rule_type"><code>_canonical_dq_rule_type</code></a>, <a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>, <a class="reference-chip" href="#_latest_dq_rule_versions"><code>_latest_dq_rule_versions</code></a>, <a class="reference-chip" href="#_spark_sql_helpers"><code>_spark_sql_helpers</code></a>, <a class="reference-chip" href="#_validate_dq_rules"><code>_validate_dq_rules</code></a>
</li>
<li>
<a class="reference-chip" href="#_parse_ai_dict_response"><code>_parse_ai_dict_response</code></a>
</li>
<li>
<a class="reference-chip" href="#_parse_dq_ai_suggestions"><code>_parse_dq_ai_suggestions</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_canonical_dq_rule_type"><code>_canonical_dq_rule_type</code></a>, <a class="reference-chip" href="#_extract_assignment_payload"><code>_extract_assignment_payload</code></a>, <a class="reference-chip" href="#_validate_dq_rules"><code>_validate_dq_rules</code></a>
</li>
<li>
<a class="reference-chip" href="#_prepare_dq_profile_input_rows"><code>_prepare_dq_profile_input_rows</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_spark_sql_helpers"><code>_spark_sql_helpers</code></a>
</li>
<li>
<a class="reference-chip" href="#_read_metadata_rows"><code>_read_metadata_rows</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_rows"><code>_coerce_rows</code></a>
</li>
<li>
<a class="reference-chip" href="#_review_governance_evidence"><code>_review_governance_evidence</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_latest_row"><code>_latest_row</code></a>, <a class="reference-chip" href="#_read_metadata_rows"><code>_read_metadata_rows</code></a>, <a class="reference-chip" href="#_status_is_failed"><code>_status_is_failed</code></a>, <a class="reference-chip" href="#_status_is_warning"><code>_status_is_warning</code></a>, <a class="reference-chip" href="#_value"><code>_value</code></a>, <a class="reference-chip" href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a>
</li>
<li>
<a class="reference-chip" href="#_run_dq_guardrail_checks"><code>_run_dq_guardrail_checks</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_dq_check_status"><code>_dq_check_status</code></a>, <a class="reference-chip" href="#_dq_failed_expression"><code>_dq_failed_expression</code></a>, <a class="reference-chip" href="#_spark_sql_helpers"><code>_spark_sql_helpers</code></a>, <a class="reference-chip" href="#_validate_dq_rules"><code>_validate_dq_rules</code></a>
</li>
<li>
<a class="reference-chip" href="#_run_fabric_ai_drafting"><code>_run_fabric_ai_drafting</code></a>
</li>
<li>
<a class="reference-chip" href="#_schema"><code>_schema</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_spark_types"><code>_spark_types</code></a>, <a class="reference-chip" href="#_validate_schema_field_names"><code>_validate_schema_field_names</code></a>
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
<a class="reference-chip" href="#_spark_sql_helpers"><code>_spark_sql_helpers</code></a>
</li>
<li>
<a class="reference-chip" href="#_spark_types"><code>_spark_types</code></a>
</li>
<li>
<a class="reference-chip" href="#_status_is_failed"><code>_status_is_failed</code></a>
</li>
<li>
<a class="reference-chip" href="#_status_is_warning"><code>_status_is_warning</code></a>
</li>
<li>
<a class="reference-chip" href="#_summarize_dq_guardrail"><code>_summarize_dq_guardrail</code></a>
</li>
<li>
<a class="reference-chip" href="#_validate_dq_rules"><code>_validate_dq_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_canonical_dq_rule_type"><code>_canonical_dq_rule_type</code></a>
</li>
<li>
<a class="reference-chip" href="#_validate_schema_field_names"><code>_validate_schema_field_names</code></a>
</li>
<li>
<a class="reference-chip" href="#_value"><code>_value</code></a>
</li>
</ul>
</details>

### External callers

**config**
<a class="reference-chip" href="../config/#_get_active_metadata_tables"><code>_get_active_metadata_tables</code></a>, <a class="reference-chip" href="../../reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>

**pipeline**
<a class="reference-chip" href="../../reference/run_table_guardrails/"><code>run_table_guardrails</code></a>

### External callees

**config**
<a class="reference-chip" href="../config/#_current_audit_timestamp"><code>_current_audit_timestamp</code></a>, <a class="reference-chip" href="../config/#_get_audit_timezone"><code>_get_audit_timezone</code></a>

**data_profiling**
<a class="reference-chip" href="../../reference/profile_dataframe/"><code>profile_dataframe</code></a>

**fabric_input_output**
<a class="reference-chip" href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a>, <a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>

**metadata**
<a class="reference-chip" href="../metadata/#_build_dq_rule_key"><code>_build_dq_rule_key</code></a>, <a class="reference-chip" href="../metadata/#_build_metadata_column_key"><code>_build_metadata_column_key</code></a>, <a class="reference-chip" href="../metadata/#_build_metadata_table_key"><code>_build_metadata_table_key</code></a>, <a class="reference-chip" href="../metadata/#_build_runtime_audit_fields"><code>_build_runtime_audit_fields</code></a>, <a class="reference-chip" href="../metadata/#_now_utc_iso"><code>_now_utc_iso</code></a>, <a class="reference-chip" href="../metadata/#_resolve_action_by"><code>_resolve_action_by</code></a>
