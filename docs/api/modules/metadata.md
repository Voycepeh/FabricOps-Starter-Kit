# `metadata` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 6</span><span class="reference-chip">Internal helpers: 15</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 5</span></div>

## Module purpose

Owns metadata evidence persistence, stable keys, notebook registry, catalogue keys, and runtime audit helpers.

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
      <td><code>metadata</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns metadata evidence persistence, stable keys, notebook registry, catalogue keys, and runtime audit helpers.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>6</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>15</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td><code>business_context</code>, <code>data_agreement</code>, <code>data_governance</code>, <code>data_quality</code>, <code>governance_review</code></td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>fabric_input_output</code></td>
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
      <td><a href="../../reference/build_runtime_audit_fields/"><code>build_runtime_audit_fields</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Build shared runtime audit values; 03_pc uses notebook and committed-by context while adding dataframe audit columns inline.</td>
      <td><a href="../../reference/internal/metadata/_context_get/"><code>_context_get</code></a> (internal), <a href="../../reference/internal/metadata/_runtime_context/"><code>_runtime_context</code></a> (internal), <a href="../../reference/internal/metadata/_safe_str/"><code>_safe_str</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/load_notebook_registry/"><code>load_notebook_registry</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Load notebook registration metadata rows for agreement notebook traceability.</td>
      <td><a href="../../reference/internal/metadata/_latest_registration_events/"><code>_latest_registration_events</code></a> (internal), <a href="../../reference/internal/metadata/_registry_rows_with_defaults/"><code>_registry_rows_with_defaults</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Register current notebook metadata evidence for agreement traceability.</td>
      <td><a href="../../reference/internal/metadata/_context_get/"><code>_context_get</code></a> (internal), <a href="../../reference/internal/metadata/_notebook_registration_key/"><code>_notebook_registration_key</code></a> (internal), <a href="../../reference/internal/metadata/_runtime_context/"><code>_runtime_context</code></a> (internal), <a href="../../reference/internal/metadata/_safe_str/"><code>_safe_str</code></a> (internal), <a href="../../reference/internal/metadata/_write_metadata_rows_legacy/"><code>_write_metadata_rows_legacy</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/setup_notebook_registry_table/"><code>setup_notebook_registry_table</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Create or validate notebook registry metadata before workflow notebooks register themselves.</td>
      <td><a href="../../reference/internal/metadata/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a> (internal), <a href="../../reference/internal/metadata/_column_names/"><code>_column_names</code></a> (internal), <a href="../../reference/internal/metadata/_notebook_registration_key/"><code>_notebook_registration_key</code></a> (internal), <a href="../../reference/internal/metadata/_safe_str/"><code>_safe_str</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/current_notebook_active_registrations/"><code>current_notebook_active_registrations</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Return active latest agreement registrations for the running notebook.</td>
      <td><a href="../../reference/internal/metadata/_context_get/"><code>_context_get</code></a> (internal), <a href="../../reference/internal/metadata/_runtime_context/"><code>_runtime_context</code></a> (internal), <a href="../../reference/internal/metadata/_safe_str/"><code>_safe_str</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/get_notebook_registry_schema/"><code>get_notebook_registry_schema</code></a></td>
      <td>Optional</td>
      <td>function</td>
      <td>Return the required notebook registry metadata columns.</td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>metadata</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../../reference/build_runtime_audit_fields/"><code>build_runtime_audit_fields</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_context_get"><code>_context_get</code></a>, <a class="reference-chip" href="#_runtime_context"><code>_runtime_context</code></a>, <a class="reference-chip" href="#_safe_str"><code>_safe_str</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/current_notebook_active_registrations/"><code>current_notebook_active_registrations</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_context_get"><code>_context_get</code></a>, <a class="reference-chip" href="#_runtime_context"><code>_runtime_context</code></a>, <a class="reference-chip" href="#_safe_str"><code>_safe_str</code></a>, <a class="reference-chip" href="../../reference/load_notebook_registry/"><code>load_notebook_registry</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/get_notebook_registry_schema/"><code>get_notebook_registry_schema</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/load_notebook_registry/"><code>load_notebook_registry</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_latest_registration_events"><code>_latest_registration_events</code></a>, <a class="reference-chip" href="#_registry_rows_with_defaults"><code>_registry_rows_with_defaults</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_context_get"><code>_context_get</code></a>, <a class="reference-chip" href="#_notebook_registration_key"><code>_notebook_registration_key</code></a>, <a class="reference-chip" href="#_runtime_context"><code>_runtime_context</code></a>, <a class="reference-chip" href="#_safe_str"><code>_safe_str</code></a>, <a class="reference-chip" href="#_write_metadata_rows_legacy"><code>_write_metadata_rows_legacy</code></a>, <a class="reference-chip" href="#column_context_rows_for_spark"><code>column_context_rows_for_spark</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/setup_notebook_registry_table/"><code>setup_notebook_registry_table</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>, <a class="reference-chip" href="#_column_names"><code>_column_names</code></a>, <a class="reference-chip" href="#_notebook_registration_key"><code>_notebook_registration_key</code></a>, <a class="reference-chip" href="#_safe_str"><code>_safe_str</code></a>, <a class="reference-chip" href="#column_context_rows_for_spark"><code>column_context_rows_for_spark</code></a>, <a class="reference-chip" href="../../reference/get_notebook_registry_schema/"><code>get_notebook_registry_schema</code></a>
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
      <td><a href="../../reference/internal/metadata/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a></td>
      <td><a href="../../reference/setup_notebook_registry_table/"><code>setup_notebook_registry_table</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_column_names/"><code>_column_names</code></a></td>
      <td><a href="../../reference/setup_notebook_registry_table/"><code>setup_notebook_registry_table</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_context_get/"><code>_context_get</code></a></td>
      <td><a href="../../reference/build_runtime_audit_fields/"><code>build_runtime_audit_fields</code></a>, <a href="../../reference/current_notebook_active_registrations/"><code>current_notebook_active_registrations</code></a>, <a href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_extract_columns_from_profile/"><code>_extract_columns_from_profile</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_key_part/"><code>_key_part</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_latest_registration_events/"><code>_latest_registration_events</code></a></td>
      <td><a href="../../reference/load_notebook_registry/"><code>load_notebook_registry</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_notebook_registration_key/"><code>_notebook_registration_key</code></a></td>
      <td><a href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a>, <a href="../../reference/setup_notebook_registry_table/"><code>setup_notebook_registry_table</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_notebook_registry_base_schema/"><code>_notebook_registry_base_schema</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_now_utc_iso/"><code>_now_utc_iso</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_registry_rows_with_defaults/"><code>_registry_rows_with_defaults</code></a></td>
      <td><a href="../../reference/load_notebook_registry/"><code>load_notebook_registry</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_resolve_action_by/"><code>_resolve_action_by</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_runtime_context/"><code>_runtime_context</code></a></td>
      <td><a href="../../reference/build_runtime_audit_fields/"><code>build_runtime_audit_fields</code></a>, <a href="../../reference/current_notebook_active_registrations/"><code>current_notebook_active_registrations</code></a>, <a href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_safe_str/"><code>_safe_str</code></a></td>
      <td><a href="../../reference/build_runtime_audit_fields/"><code>build_runtime_audit_fields</code></a>, <a href="../../reference/current_notebook_active_registrations/"><code>current_notebook_active_registrations</code></a>, <a href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a>, <a href="../../reference/setup_notebook_registry_table/"><code>setup_notebook_registry_table</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_sha256_key/"><code>_sha256_key</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_write_metadata_rows_legacy/"><code>_write_metadata_rows_legacy</code></a></td>
      <td><a href="../../reference/register_current_notebook/"><code>register_current_notebook</code></a></td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>
</li>
<li>
<a class="reference-chip" href="#_column_names"><code>_column_names</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>
</li>
<li>
<a class="reference-chip" href="#_context_get"><code>_context_get</code></a>
</li>
<li>
<a class="reference-chip" href="#_extract_columns_from_profile"><code>_extract_columns_from_profile</code></a>
</li>
<li>
<a class="reference-chip" href="#_key_part"><code>_key_part</code></a>
</li>
<li>
<a class="reference-chip" href="#_latest_registration_events"><code>_latest_registration_events</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_notebook_registration_key"><code>_notebook_registration_key</code></a>, <a class="reference-chip" href="#_registry_rows_with_defaults"><code>_registry_rows_with_defaults</code></a>
</li>
<li>
<a class="reference-chip" href="#_notebook_registration_key"><code>_notebook_registration_key</code></a>
</li>
<li>
<a class="reference-chip" href="#_notebook_registry_base_schema"><code>_notebook_registry_base_schema</code></a>
</li>
<li>
<a class="reference-chip" href="#_now_utc_iso"><code>_now_utc_iso</code></a>
</li>
<li>
<a class="reference-chip" href="#_registry_rows_with_defaults"><code>_registry_rows_with_defaults</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>, <a class="reference-chip" href="#_notebook_registration_key"><code>_notebook_registration_key</code></a>, <a class="reference-chip" href="#_safe_str"><code>_safe_str</code></a>
</li>
<li>
<a class="reference-chip" href="#_resolve_action_by"><code>_resolve_action_by</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_context_get"><code>_context_get</code></a>, <a class="reference-chip" href="#_runtime_context"><code>_runtime_context</code></a>
</li>
<li>
<a class="reference-chip" href="#_runtime_context"><code>_runtime_context</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_context_get"><code>_context_get</code></a>
</li>
<li>
<a class="reference-chip" href="#_safe_str"><code>_safe_str</code></a>
</li>
<li>
<a class="reference-chip" href="#_sha256_key"><code>_sha256_key</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_key_part"><code>_key_part</code></a>
</li>
<li>
<a class="reference-chip" href="#_write_metadata_rows_legacy"><code>_write_metadata_rows_legacy</code></a>
</li>
</ul>
</details>

### External callers

**business_context**
<a class="reference-chip" href="../../reference/widget_review_business_context/"><code>widget_review_business_context</code></a>, <a class="reference-chip" href="../../reference/write_business_context/"><code>write_business_context</code></a>

**data_agreement**
<a class="reference-chip" href="../data_agreement/#_create_or_update_data_agreement"><code>_create_or_update_data_agreement</code></a>, <a class="reference-chip" href="../data_agreement/#_create_or_update_data_steward"><code>_create_or_update_data_steward</code></a>, <a class="reference-chip" href="../data_agreement/#_save_agreement_evidence_records"><code>_save_agreement_evidence_records</code></a>, <a class="reference-chip" href="../../reference/widget_select_agreement/"><code>widget_select_agreement</code></a>

**data_governance**
<a class="reference-chip" href="../data_governance/#_approved_widget_rows"><code>_approved_widget_rows</code></a>, <a class="reference-chip" href="../../reference/widget_review_governance/"><code>widget_review_governance</code></a>

**data_quality**
<a class="reference-chip" href="../data_quality/#_attach_rule_metadata_keys"><code>_attach_rule_metadata_keys</code></a>, <a class="reference-chip" href="../data_quality/#_build_dq_rule_deactivation_metadata_df"><code>_build_dq_rule_deactivation_metadata_df</code></a>, <a class="reference-chip" href="../data_quality/#_build_dq_rule_deactivations"><code>_build_dq_rule_deactivations</code></a>, <a class="reference-chip" href="../data_quality/#_build_dq_rule_history"><code>_build_dq_rule_history</code></a>, <a class="reference-chip" href="../data_quality/#_build_dq_rules_metadata_df"><code>_build_dq_rules_metadata_df</code></a>

**governance_review**
<a class="reference-chip" href="../governance_review/#_audit"><code>_audit</code></a>, <a class="reference-chip" href="../../reference/build_classification_records/"><code>build_classification_records</code></a>, <a class="reference-chip" href="../../reference/build_column_context_records/"><code>build_column_context_records</code></a>, <a class="reference-chip" href="../../reference/build_dq_rule_records/"><code>build_dq_rule_records</code></a>, <a class="reference-chip" href="../../reference/catalogue_table_options/"><code>catalogue_table_options</code></a>

### External callees

**fabric_input_output**
<a class="reference-chip" href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a>, <a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>
