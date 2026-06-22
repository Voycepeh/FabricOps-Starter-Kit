# `metadata` module (internal)

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 0</span><span class="reference-chip">Internal helpers: 17</span><span class="reference-chip">Uses 2 external modules</span><span class="reference-chip">Used by 4 external modules</span></div>

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
      <td>0</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>17</td>
    </tr>
    <tr>
      <td>Used by external module count</td>
      <td>4</td>
    </tr>
    <tr>
      <td>Uses external module count</td>
      <td>2</td>
    </tr>
    <tr>
      <td>External modules using this module</td>
      <td><code>data_agreement</code>, <code>governance_review</code>, <code>guardrails</code>, <code>pipeline</code></td>
    </tr>
    <tr>
      <td>External modules this module uses</td>
      <td><code>config</code>, <code>io_core</code></td>
    </tr>
  </tbody>
</table>

## Public callables

No public exports in this module.

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>metadata</h5>
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
      <td><code>_build_dq_rule_key</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_build_metadata_column_key</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_build_metadata_table_key</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_build_runtime_audit_fields</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_coerce_row_dicts</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_context_get</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_current_notebook_active_registrations</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_load_notebook_registry</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_notebook_registration_key</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_now_utc_iso</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_register_current_notebook</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_resolve_action_by</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_rows_for_spark</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_runtime_context</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_safe_str</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_stable_metadata_key</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_write_guardrail_result_row</code></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<span class="reference-chip"><code>_build_dq_rule_key</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_stable_metadata_key</code></span>
</li>
<li>
<span class="reference-chip"><code>_build_metadata_column_key</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_stable_metadata_key</code></span>
</li>
<li>
<span class="reference-chip"><code>_build_metadata_table_key</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_stable_metadata_key</code></span>
</li>
<li>
<span class="reference-chip"><code>_build_runtime_audit_fields</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_context_get</code></span>, <span class="reference-chip"><code>_runtime_context</code></span>, <span class="reference-chip"><code>_safe_str</code></span>
</li>
<li>
<span class="reference-chip"><code>_coerce_row_dicts</code></span>
</li>
<li>
<span class="reference-chip"><code>_context_get</code></span>
</li>
<li>
<span class="reference-chip"><code>_current_notebook_active_registrations</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_context_get</code></span>, <span class="reference-chip"><code>_load_notebook_registry</code></span>, <span class="reference-chip"><code>_runtime_context</code></span>, <span class="reference-chip"><code>_safe_str</code></span>
</li>
<li>
<span class="reference-chip"><code>_load_notebook_registry</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_coerce_row_dicts</code></span>, <span class="reference-chip"><code>_notebook_registration_key</code></span>
</li>
<li>
<span class="reference-chip"><code>_notebook_registration_key</code></span>
</li>
<li>
<span class="reference-chip"><code>_now_utc_iso</code></span>
</li>
<li>
<span class="reference-chip"><code>_register_current_notebook</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_context_get</code></span>, <span class="reference-chip"><code>_notebook_registration_key</code></span>, <span class="reference-chip"><code>_rows_for_spark</code></span>, <span class="reference-chip"><code>_runtime_context</code></span>, <span class="reference-chip"><code>_safe_str</code></span>
</li>
<li>
<span class="reference-chip"><code>_resolve_action_by</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_context_get</code></span>, <span class="reference-chip"><code>_runtime_context</code></span>
</li>
<li>
<span class="reference-chip"><code>_rows_for_spark</code></span>
</li>
<li>
<span class="reference-chip"><code>_runtime_context</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_context_get</code></span>
</li>
<li>
<span class="reference-chip"><code>_safe_str</code></span>
</li>
<li>
<span class="reference-chip"><code>_stable_metadata_key</code></span>
</li>
<li>
<span class="reference-chip"><code>_write_guardrail_result_row</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_build_runtime_audit_fields</code></span>, <span class="reference-chip"><code>_now_utc_iso</code></span>
</li>
</ul>
</details>

### External callers

**data_agreement**
<a class="reference-chip" href="data_agreement/#_create_or_update_data_agreement"><code>_create_or_update_data_agreement</code></a>, <a class="reference-chip" href="data_agreement/#_create_or_update_data_steward"><code>_create_or_update_data_steward</code></a>, <a class="reference-chip" href="data_agreement/#_save_agreement_evidence_records"><code>_save_agreement_evidence_records</code></a>, <a class="reference-chip" href="data_agreement/#widget_select_agreement"><code>widget_select_agreement</code></a>

**governance_review**
<a class="reference-chip" href="governance_review/#_approved_column_identity"><code>_approved_column_identity</code></a>, <a class="reference-chip" href="governance_review/#_approved_review_context"><code>_approved_review_context</code></a>, <a class="reference-chip" href="governance_review/#_authoring_lifecycle"><code>_authoring_lifecycle</code></a>, <a class="reference-chip" href="governance_review/#_base_guardrail_rule_record"><code>_base_guardrail_rule_record</code></a>, <a class="reference-chip" href="governance_review/#_build_dq_rule_records"><code>_build_dq_rule_records</code></a>, <a class="reference-chip" href="governance_review/#_catalogue_physical_identity"><code>_catalogue_physical_identity</code></a>, <a class="reference-chip" href="governance_review/#_evaluate_governance_readiness"><code>_evaluate_governance_readiness</code></a>, <a class="reference-chip" href="governance_review/#_run_active_dq_guardrail"><code>_run_active_dq_guardrail</code></a>, <a class="reference-chip" href="governance_review/#apply_governance_enrichment_action"><code>apply_governance_enrichment_action</code></a>, <a class="reference-chip" href="governance_review/#apply_governance_rule_action"><code>apply_governance_rule_action</code></a>, <a class="reference-chip" href="governance_review/#build_enrichment_rule_records"><code>build_enrichment_rule_records</code></a>, <a class="reference-chip" href="governance_review/#build_table_governance_policy_record"><code>build_table_governance_policy_record</code></a>, <a class="reference-chip" href="governance_review/#record_table_governance"><code>record_table_governance</code></a>, <a class="reference-chip" href="../reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a>

**guardrails**
<a class="reference-chip" href="guardrails/#enforce_profile_behavior"><code>enforce_profile_behavior</code></a>

**pipeline**
<a class="reference-chip" href="pipeline/#_runtime_audit_fields"><code>_runtime_audit_fields</code></a>, <a class="reference-chip" href="../reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a class="reference-chip" href="pipeline/#write_catalogue_evidence"><code>write_catalogue_evidence</code></a>, <a class="reference-chip" href="../reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>

### External callees

**config**
<a class="reference-chip" href="config/#_current_audit_timestamp"><code>_current_audit_timestamp</code></a>, <a class="reference-chip" href="config/#_get_store"><code>_get_store</code></a>

**io_core**
<a class="reference-chip" href="io_core/#configured_lakehouse_schema"><code>configured_lakehouse_schema</code></a>, <a class="reference-chip" href="io_core/#read_lakehouse_table_core"><code>read_lakehouse_table_core</code></a>, <a class="reference-chip" href="io_core/#write_lakehouse_table_core"><code>write_lakehouse_table_core</code></a>
