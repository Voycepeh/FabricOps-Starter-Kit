# `metadata` module (internal)

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 0</span><span class="reference-chip">Internal helpers: 18</span><span class="reference-chip">Outbound: 1</span><span class="reference-chip">Inbound: 4</span></div>

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
      <td>18</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>4</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td><code>config</code>, <code>data_agreement</code>, <code>governance_review</code>, <code>pipeline</code></td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>fabric_input_output</code></td>
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
      <td><a href="../../reference/internal/metadata/_build_dq_rule_key/"><code>_build_dq_rule_key</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_build_metadata_column_key/"><code>_build_metadata_column_key</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_build_metadata_table_key/"><code>_build_metadata_table_key</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_build_runtime_audit_fields/"><code>_build_runtime_audit_fields</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_context_get/"><code>_context_get</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_current_notebook_active_registrations/"><code>_current_notebook_active_registrations</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_load_notebook_registry/"><code>_load_notebook_registry</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_notebook_registration_key/"><code>_notebook_registration_key</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_now_utc_iso/"><code>_now_utc_iso</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_register_current_notebook/"><code>_register_current_notebook</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_registry_rows_with_defaults/"><code>_registry_rows_with_defaults</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_resolve_action_by/"><code>_resolve_action_by</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_rows_for_spark/"><code>_rows_for_spark</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_runtime_context/"><code>_runtime_context</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_safe_str/"><code>_safe_str</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_setup_notebook_registry_table/"><code>_setup_notebook_registry_table</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/metadata/_stable_metadata_key/"><code>_stable_metadata_key</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_build_dq_rule_key"><code>_build_dq_rule_key</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_stable_metadata_key"><code>_stable_metadata_key</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_metadata_column_key"><code>_build_metadata_column_key</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_stable_metadata_key"><code>_stable_metadata_key</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_metadata_table_key"><code>_build_metadata_table_key</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_stable_metadata_key"><code>_stable_metadata_key</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_runtime_audit_fields"><code>_build_runtime_audit_fields</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_context_get"><code>_context_get</code></a>, <a class="reference-chip" href="#_runtime_context"><code>_runtime_context</code></a>, <a class="reference-chip" href="#_safe_str"><code>_safe_str</code></a>
</li>
<li>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>
</li>
<li>
<a class="reference-chip" href="#_context_get"><code>_context_get</code></a>
</li>
<li>
<a class="reference-chip" href="#_current_notebook_active_registrations"><code>_current_notebook_active_registrations</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_context_get"><code>_context_get</code></a>, <a class="reference-chip" href="#_load_notebook_registry"><code>_load_notebook_registry</code></a>, <a class="reference-chip" href="#_runtime_context"><code>_runtime_context</code></a>, <a class="reference-chip" href="#_safe_str"><code>_safe_str</code></a>
</li>
<li>
<a class="reference-chip" href="#_load_notebook_registry"><code>_load_notebook_registry</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_notebook_registration_key"><code>_notebook_registration_key</code></a>, <a class="reference-chip" href="#_registry_rows_with_defaults"><code>_registry_rows_with_defaults</code></a>
</li>
<li>
<a class="reference-chip" href="#_notebook_registration_key"><code>_notebook_registration_key</code></a>
</li>
<li>
<a class="reference-chip" href="#_now_utc_iso"><code>_now_utc_iso</code></a>
</li>
<li>
<a class="reference-chip" href="#_register_current_notebook"><code>_register_current_notebook</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_context_get"><code>_context_get</code></a>, <a class="reference-chip" href="#_notebook_registration_key"><code>_notebook_registration_key</code></a>, <a class="reference-chip" href="#_rows_for_spark"><code>_rows_for_spark</code></a>, <a class="reference-chip" href="#_runtime_context"><code>_runtime_context</code></a>, <a class="reference-chip" href="#_safe_str"><code>_safe_str</code></a>
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
<a class="reference-chip" href="#_rows_for_spark"><code>_rows_for_spark</code></a>
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
<a class="reference-chip" href="#_setup_notebook_registry_table"><code>_setup_notebook_registry_table</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>, <a class="reference-chip" href="#_registry_rows_with_defaults"><code>_registry_rows_with_defaults</code></a>, <a class="reference-chip" href="#_rows_for_spark"><code>_rows_for_spark</code></a>
</li>
<li>
<a class="reference-chip" href="#_stable_metadata_key"><code>_stable_metadata_key</code></a>
</li>
</ul>
</details>

### External callers

**config**
<a class="reference-chip" href="../../reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>

**data_agreement**
<a class="reference-chip" href="../data_agreement/#_create_or_update_data_agreement"><code>_create_or_update_data_agreement</code></a>, <a class="reference-chip" href="../data_agreement/#_create_or_update_data_steward"><code>_create_or_update_data_steward</code></a>, <a class="reference-chip" href="../data_agreement/#_save_agreement_evidence_records"><code>_save_agreement_evidence_records</code></a>, <a class="reference-chip" href="../../reference/widget_select_agreement/"><code>widget_select_agreement</code></a>

**governance_review**
<a class="reference-chip" href="../governance_review/#_approved_column_identity"><code>_approved_column_identity</code></a>, <a class="reference-chip" href="../governance_review/#_approved_review_context"><code>_approved_review_context</code></a>, <a class="reference-chip" href="../governance_review/#_build_dq_rule_records"><code>_build_dq_rule_records</code></a>, <a class="reference-chip" href="../governance_review/#_catalogue_table_options"><code>_catalogue_table_options</code></a>, <a class="reference-chip" href="../governance_review/#_review_governance_evidence"><code>_review_governance_evidence</code></a>, <a class="reference-chip" href="../../reference/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a>

**pipeline**
<a class="reference-chip" href="../pipeline/#_runtime_audit_fields"><code>_runtime_audit_fields</code></a>, <a class="reference-chip" href="../../reference/write_catalogue_evidence/"><code>write_catalogue_evidence</code></a>, <a class="reference-chip" href="../../reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>

### External callees

**fabric_input_output**
<a class="reference-chip" href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a>, <a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>
