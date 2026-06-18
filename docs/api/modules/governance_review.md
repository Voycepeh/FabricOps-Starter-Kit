# `governance_review` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 8</span><span class="reference-chip">Internal helpers: 59</span><span class="reference-chip">Outbound: 4</span><span class="reference-chip">Inbound: 2</span></div>

## Module purpose

Owns current guardrail authoring and governance review widgets plus internal review helpers required by the template-driven workflow.

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
      <td>Owns current guardrail authoring and governance review widgets plus internal review helpers required by the template-driven workflow.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>8</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>59</td>
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
      <td><a href="../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Enforce approved active DQ rules as a target-write guardrail without filtering rows.</td>
      <td><code>_dq_failed_row_count</code> (internal), <code>_dq_summary</code> (internal), <code>_dq_tagged_dataframe</code> (internal), <code>_load_active_dq_rules</code> (internal), <code>_read_guardrail_rule_metadata</code> (internal), <code>_run_dq_guardrail_checks</code> (internal), <code>_summarize_dq_guardrail</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render interactive manual DQ guardrail authoring controls.</td>
      <td><code>_dq_records_from_selection</code> (internal), <code>_latest_rule</code> (internal), <code>_rule_params</code> (internal), <code>_write_rule_records</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../reference/widget_author_guardrail_rules/"><code>widget_author_guardrail_rules</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render combined guardrail authoring controls for the selected table.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render interactive schema, freshness, and profile-behavior guardrail authoring controls.</td>
      <td><code>_latest_rule</code> (internal), <code>_rule_params</code> (internal), <code>_schema_freshness_profile_records_from_selection</code> (internal), <code>_write_rule_records</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render a consolidated column enrichment widget.</td>
      <td><code>_collect_enrichment_extra_fields</code> (internal), <code>_enrichment_options</code> (internal), <code>_render_enrichment_extra_fields</code> (internal), <code>_selected_catalogue_rows_for_enrichment</code> (internal), <code>_value</code> (internal), <code>_write_table_metadata_enrichment_records</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render interactive controls for reviewing proposed and bypassed guardrail rules.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../reference/widget_review_table_governance/"><code>widget_review_table_governance</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render 03-only formal review controls for enrichment and guardrail records.</td>
      <td><code>_assert_governance_review_context</code> (internal), <code>_dq_rule_parameters_summary</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render an interactive target selector for guardrail authoring and governance review.</td>
      <td><code>_filter_table_rows</code> (internal), <code>_read_metadata_table_or_empty</code> (internal)</td>
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
<a class="reference-chip" href="../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_dq_failed_row_count</code></span>, <span class="reference-chip"><code>_dq_summary</code></span>, <span class="reference-chip"><code>_dq_tagged_dataframe</code></span>, <span class="reference-chip"><code>_load_active_dq_rules</code></span>, <span class="reference-chip"><code>_read_guardrail_rule_metadata</code></span>, <span class="reference-chip"><code>_run_dq_guardrail_checks</code></span>, <span class="reference-chip"><code>_summarize_dq_guardrail</code></span>
</li>
<li>
<a class="reference-chip" href="../reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_dq_records_from_selection</code></span>, <span class="reference-chip"><code>_latest_rule</code></span>, <span class="reference-chip"><code>_rule_params</code></span>, <span class="reference-chip"><code>_write_rule_records</code></span>
</li>
<li>
<a class="reference-chip" href="../reference/widget_author_guardrail_rules/"><code>widget_author_guardrail_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="../reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a class="reference-chip" href="../reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>
</li>
<li>
<a class="reference-chip" href="../reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_latest_rule</code></span>, <span class="reference-chip"><code>_rule_params</code></span>, <span class="reference-chip"><code>_schema_freshness_profile_records_from_selection</code></span>, <span class="reference-chip"><code>_write_rule_records</code></span>
</li>
<li>
<a class="reference-chip" href="../reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_collect_enrichment_extra_fields</code></span>, <span class="reference-chip"><code>_enrichment_options</code></span>, <span class="reference-chip"><code>_render_enrichment_extra_fields</code></span>, <span class="reference-chip"><code>_selected_catalogue_rows_for_enrichment</code></span>, <span class="reference-chip"><code>_value</code></span>, <span class="reference-chip"><code>_write_table_metadata_enrichment_records</code></span>, <span class="reference-chip"><code>build_enrichment_rule_records</code></span>
</li>
<li>
<a class="reference-chip" href="../reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>apply_governance_enrichment_action</code></span>, <span class="reference-chip"><code>apply_governance_rule_action</code></span>, <span class="reference-chip"><code>load_rule_review_history</code></span>
</li>
<li>
<a class="reference-chip" href="../reference/widget_review_table_governance/"><code>widget_review_table_governance</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_assert_governance_review_context</code></span>, <span class="reference-chip"><code>_dq_rule_parameters_summary</code></span>, <span class="reference-chip"><code>apply_governance_enrichment_action</code></span>, <span class="reference-chip"><code>apply_governance_rule_action</code></span>, <span class="reference-chip"><code>load_rule_review_history</code></span>
</li>
<li>
<a class="reference-chip" href="../reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_filter_table_rows</code></span>, <span class="reference-chip"><code>_read_metadata_table_or_empty</code></span>, <span class="reference-chip"><code>resolve_table_governance_policy</code></span>
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
      <td><code>_assert_governance_review_context</code></td>
      <td><a href="../reference/widget_review_table_governance/"><code>widget_review_table_governance</code></a></td>
    </tr>
    <tr>
      <td><code>_authoring_lifecycle</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_base_guardrail_rule_record</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_build_dq_rule_records</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_canonical_dq_rule_type</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_catalogue_physical_identity</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_catalogue_profile_target_model</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_check_metadata_schema_field_names</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_coerce_rows</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_collect_enrichment_extra_fields</code></td>
      <td><a href="../reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
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
      <td><a href="../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_dq_records_from_selection</code></td>
      <td><a href="../reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_dq_rule_display_rows</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_dq_rule_parameter_payload</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_dq_rule_parameters_summary</code></td>
      <td><a href="../reference/widget_review_table_governance/"><code>widget_review_table_governance</code></a></td>
    </tr>
    <tr>
      <td><code>_dq_summary</code></td>
      <td><a href="../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_dq_tagged_dataframe</code></td>
      <td><a href="../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_enrichment_options</code></td>
      <td><a href="../reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
    </tr>
    <tr>
      <td><code>_enrichment_payload_from_review</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_evaluate_governance_readiness</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_filter_table_rows</code></td>
      <td><a href="../reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a></td>
    </tr>
    <tr>
      <td><code>_first_present</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_get_governance_metadata_schemas</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_is_no_approval_required</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_is_success</code></td>
      <td>—</td>
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
      <td><code>_latest_rule</code></td>
      <td><a href="../reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_lifecycle_fields</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_load_active_dq_rules</code></td>
      <td><a href="../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_normalize_dq_severity</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_prepare_dq_profile_input_rows</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_profile_sort_key</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_read_guardrail_rule_metadata</code></td>
      <td><a href="../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_read_metadata_rows</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_read_metadata_table_or_empty</code></td>
      <td><a href="../reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a></td>
    </tr>
    <tr>
      <td><code>_record_identity</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_render_enrichment_extra_fields</code></td>
      <td><a href="../reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
    </tr>
    <tr>
      <td><code>_rule_params</code></td>
      <td><a href="../reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_run_dq_guardrail_checks</code></td>
      <td><a href="../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_schema</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_schema_freshness_profile_records_from_selection</code></td>
      <td><a href="../reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_selected_catalogue_rows_for_enrichment</code></td>
      <td><a href="../reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
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
      <td><a href="../reference/enforce_dq_rules/"><code>enforce_dq_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_validate_dq_rules</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_value</code></td>
      <td><a href="../reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
    </tr>
    <tr>
      <td><code>_write_enrichment_records</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_write_rule_records</code></td>
      <td><a href="../reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a href="../reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a></td>
    </tr>
    <tr>
      <td><code>_write_table_metadata_enrichment_records</code></td>
      <td><a href="../reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a></td>
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
<span class="reference-chip"><code>_assert_governance_review_context</code></span>
</li>
<li>
<span class="reference-chip"><code>_authoring_lifecycle</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_is_no_approval_required</code></span>, <span class="reference-chip"><code>_lifecycle_fields</code></span>
</li>
<li>
<span class="reference-chip"><code>_base_guardrail_rule_record</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>guardrail_authoring_status</code></span>
</li>
<li>
<span class="reference-chip"><code>_build_dq_rule_records</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_approved_column_identity</code></span>, <span class="reference-chip"><code>_approved_review_context</code></span>, <span class="reference-chip"><code>_canonical_dq_rule_type</code></span>, <span class="reference-chip"><code>_dq_rule_parameter_payload</code></span>, <span class="reference-chip"><code>_json</code></span>, <span class="reference-chip"><code>_normalize_dq_severity</code></span>, <span class="reference-chip"><code>_validate_dq_rules</code></span>
</li>
<li>
<span class="reference-chip"><code>_canonical_dq_rule_type</code></span>
</li>
<li>
<span class="reference-chip"><code>_catalogue_physical_identity</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_first_present</code></span>, <span class="reference-chip"><code>_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_catalogue_profile_target_model</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_catalogue_physical_identity</code></span>, <span class="reference-chip"><code>_is_success</code></span>, <span class="reference-chip"><code>_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_check_metadata_schema_field_names</code></span>
</li>
<li>
<span class="reference-chip"><code>_coerce_rows</code></span>
</li>
<li>
<span class="reference-chip"><code>_collect_enrichment_extra_fields</code></span>
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
<span class="reference-chip"><code>_dq_records_from_selection</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_base_guardrail_rule_record</code></span>
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
<span class="reference-chip"><code>_dq_failed_expression</code></span>, <span class="reference-chip"><code>_normalize_dq_severity</code></span>, <span class="reference-chip"><code>_spark_sql_helpers</code></span>
</li>
<li>
<span class="reference-chip"><code>_enrichment_options</code></span>
</li>
<li>
<span class="reference-chip"><code>_enrichment_payload_from_review</code></span>
</li>
<li>
<span class="reference-chip"><code>_evaluate_governance_readiness</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_latest_row</code></span>, <span class="reference-chip"><code>_read_metadata_rows</code></span>, <span class="reference-chip"><code>_status_is_failed</code></span>, <span class="reference-chip"><code>_status_is_warning</code></span>, <span class="reference-chip"><code>_value</code></span>, <span class="reference-chip"><code>load_catalogue_profile_rows</code></span>
</li>
<li>
<span class="reference-chip"><code>_filter_table_rows</code></span>
</li>
<li>
<span class="reference-chip"><code>_first_present</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_get_governance_metadata_schemas</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_schema</code></span>, <span class="reference-chip"><code>_spark_types</code></span>
</li>
<li>
<span class="reference-chip"><code>_is_no_approval_required</code></span>
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
<span class="reference-chip"><code>_latest_rule</code></span>
</li>
<li>
<span class="reference-chip"><code>_lifecycle_fields</code></span>
</li>
<li>
<span class="reference-chip"><code>_load_active_dq_rules</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_canonical_dq_rule_type</code></span>, <span class="reference-chip"><code>_coerce_rows</code></span>, <span class="reference-chip"><code>_latest_dq_rule_versions</code></span>, <span class="reference-chip"><code>_normalize_dq_severity</code></span>, <span class="reference-chip"><code>_spark_sql_helpers</code></span>, <span class="reference-chip"><code>_validate_dq_rules</code></span>
</li>
<li>
<span class="reference-chip"><code>_normalize_dq_severity</code></span>
</li>
<li>
<span class="reference-chip"><code>_prepare_dq_profile_input_rows</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_spark_sql_helpers</code></span>
</li>
<li>
<span class="reference-chip"><code>_profile_sort_key</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_read_guardrail_rule_metadata</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_spark_sql_helpers</code></span>
</li>
<li>
<span class="reference-chip"><code>_read_metadata_rows</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_coerce_rows</code></span>
</li>
<li>
<span class="reference-chip"><code>_read_metadata_table_or_empty</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_coerce_rows</code></span>, <span class="reference-chip"><code>_is_table_not_found_error</code></span>
</li>
<li>
<span class="reference-chip"><code>_record_identity</code></span>
</li>
<li>
<span class="reference-chip"><code>_render_enrichment_extra_fields</code></span>
</li>
<li>
<span class="reference-chip"><code>_rule_params</code></span>
</li>
<li>
<span class="reference-chip"><code>_run_dq_guardrail_checks</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_dq_check_status</code></span>, <span class="reference-chip"><code>_dq_failed_expression</code></span>, <span class="reference-chip"><code>_normalize_dq_severity</code></span>, <span class="reference-chip"><code>_spark_sql_helpers</code></span>, <span class="reference-chip"><code>_validate_dq_rules</code></span>
</li>
<li>
<span class="reference-chip"><code>_schema</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_check_metadata_schema_field_names</code></span>, <span class="reference-chip"><code>_spark_types</code></span>
</li>
<li>
<span class="reference-chip"><code>_schema_freshness_profile_records_from_selection</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_base_guardrail_rule_record</code></span>
</li>
<li>
<span class="reference-chip"><code>_selected_catalogue_rows_for_enrichment</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_value</code></span>
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
<span class="reference-chip"><code>_canonical_dq_rule_type</code></span>, <span class="reference-chip"><code>_normalize_dq_severity</code></span>
</li>
<li>
<span class="reference-chip"><code>_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_write_enrichment_records</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_write_table_metadata_enrichment_records</code></span>
</li>
<li>
<span class="reference-chip"><code>_write_rule_records</code></span>
</li>
<li>
<span class="reference-chip"><code>_write_table_metadata_enrichment_records</code></span>
</li>
</ul>
</details>

### External callers

**config**
<a class="reference-chip" href="config/#_get_active_metadata_tables"><code>_get_active_metadata_tables</code></a>, <a class="reference-chip" href="config/#_get_metadata_table_schema_registry"><code>_get_metadata_table_schema_registry</code></a>, <a class="reference-chip" href="config/#_setup_metadata_table_registry"><code>_setup_metadata_table_registry</code></a>, <a class="reference-chip" href="../reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>

**pipeline**
<a class="reference-chip" href="../reference/run_table_guardrails/"><code>run_table_guardrails</code></a>

### External callees

**config**
<a class="reference-chip" href="config/#_current_audit_timestamp"><code>_current_audit_timestamp</code></a>, <a class="reference-chip" href="config/#resolve_fabric_context"><code>resolve_fabric_context</code></a>

**data_profiling**
<a class="reference-chip" href="../reference/profile_dataframe/"><code>profile_dataframe</code></a>

**fabric_input_output**
<a class="reference-chip" href="fabric_input_output/#_configured_lakehouse_schema"><code>_configured_lakehouse_schema</code></a>, <a class="reference-chip" href="fabric_input_output/#read_lakehouse_table"><code>read_lakehouse_table</code></a>, <a class="reference-chip" href="fabric_input_output/#write_lakehouse_table"><code>write_lakehouse_table</code></a>

**metadata**
<a class="reference-chip" href="metadata/#_build_dq_rule_key"><code>_build_dq_rule_key</code></a>, <a class="reference-chip" href="metadata/#_build_metadata_column_key"><code>_build_metadata_column_key</code></a>, <a class="reference-chip" href="metadata/#_build_metadata_table_key"><code>_build_metadata_table_key</code></a>, <a class="reference-chip" href="metadata/#_build_runtime_audit_fields"><code>_build_runtime_audit_fields</code></a>, <a class="reference-chip" href="metadata/#_now_utc_iso"><code>_now_utc_iso</code></a>, <a class="reference-chip" href="metadata/#_resolve_action_by"><code>_resolve_action_by</code></a>, <a class="reference-chip" href="metadata/#_write_guardrail_result_row"><code>_write_guardrail_result_row</code></a>
