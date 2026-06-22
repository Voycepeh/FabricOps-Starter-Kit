# `data_agreement` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 3</span><span class="reference-chip">Internal helpers: 37</span><span class="reference-chip">Uses 3 external modules</span><span class="reference-chip">Used by 2 external modules</span></div>

## Module purpose

Owns agreement metadata capture, audited record building, metadata commit helpers, agreement intake widgets, and 02_pipeline agreement selection/registration helpers.

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
      <td>Owns agreement metadata capture, audited record building, metadata commit helpers, agreement intake widgets, and 02_pipeline agreement selection/registration helpers.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>3</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>37</td>
    </tr>
    <tr>
      <td>Used by external module count</td>
      <td>2</td>
    </tr>
    <tr>
      <td>Uses external module count</td>
      <td>3</td>
    </tr>
    <tr>
      <td>External modules using this module</td>
      <td><code>config</code>, <code>pipeline</code></td>
    </tr>
    <tr>
      <td>External modules this module uses</td>
      <td><code>config</code>, <code>io_core</code>, <code>metadata</code></td>
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
      <td><a href="../reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render the standalone agreement-evidence widget.</td>
      <td><code>_render_agreement_evidence_widget_workflow</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render the standalone data-agreement intake widget.</td>
      <td><code>_render_data_agreement_widget_workflow</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render the standalone data-steward intake widget.</td>
      <td><code>_render_data_steward_widget_workflow</code> (internal)</td>
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
<a class="reference-chip" href="../reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_render_agreement_evidence_widget_workflow</code></span>
</li>
<li>
<a class="reference-chip" href="../reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_render_data_agreement_widget_workflow</code></span>
</li>
<li>
<a class="reference-chip" href="../reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_render_data_steward_widget_workflow</code></span>
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
      <td><code>_active_steward</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_agreement_identity_text</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_business_agreement_snapshot</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_coerce_row_dicts</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_collect_custom_fields</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_config_value</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_create_or_update_data_agreement</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_create_or_update_data_steward</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_deserialize_custom_fields</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_generate_agreement_id</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_generate_steward_id</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_get_notebookutils</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_get_widget_visible_fields</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_html_escape</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_latest_agreement_versions</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_latest_by_key</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_list_all_data_agreement_rows</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_list_data_agreements</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_list_data_stewards</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_next_minor_version</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_parse_contract_version</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_parse_iso_date</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_prepare_evidence_file_references</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_render_agreement_evidence_widget_workflow</code></td>
      <td><a href="../reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></td>
    </tr>
    <tr>
      <td><code>_render_custom_fields</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_render_data_agreement_widget_workflow</code></td>
      <td><a href="../reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a></td>
    </tr>
    <tr>
      <td><code>_render_data_steward_widget_workflow</code></td>
      <td><a href="../reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
    </tr>
    <tr>
      <td><code>_render_maintenance_widget_workflow</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_render_searchable_selector</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_require_ipywidgets</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_save_agreement_evidence_records</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_serialize_custom_fields</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_standard_widget</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_to_bool</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_to_iso_date</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_widget_common</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_write_row</code></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<span class="reference-chip"><code>_active_steward</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_to_bool</code></span>
</li>
<li>
<span class="reference-chip"><code>_agreement_identity_text</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_next_minor_version</code></span>
</li>
<li>
<span class="reference-chip"><code>_business_agreement_snapshot</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_deserialize_custom_fields</code></span>, <span class="reference-chip"><code>_serialize_custom_fields</code></span>
</li>
<li>
<span class="reference-chip"><code>_coerce_row_dicts</code></span>
</li>
<li>
<span class="reference-chip"><code>_collect_custom_fields</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_to_iso_date</code></span>
</li>
<li>
<span class="reference-chip"><code>_config_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_create_or_update_data_agreement</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_business_agreement_snapshot</code></span>, <span class="reference-chip"><code>_config_value</code></span>, <span class="reference-chip"><code>_generate_agreement_id</code></span>, <span class="reference-chip"><code>_list_all_data_agreement_rows</code></span>, <span class="reference-chip"><code>_list_data_stewards</code></span>, <span class="reference-chip"><code>_next_minor_version</code></span>, <span class="reference-chip"><code>_parse_contract_version</code></span>, <span class="reference-chip"><code>_parse_iso_date</code></span>, <span class="reference-chip"><code>_serialize_custom_fields</code></span>, <span class="reference-chip"><code>_write_row</code></span>
</li>
<li>
<span class="reference-chip"><code>_create_or_update_data_steward</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_active_steward</code></span>, <span class="reference-chip"><code>_config_value</code></span>, <span class="reference-chip"><code>_generate_steward_id</code></span>, <span class="reference-chip"><code>_parse_iso_date</code></span>, <span class="reference-chip"><code>_serialize_custom_fields</code></span>, <span class="reference-chip"><code>_to_bool</code></span>, <span class="reference-chip"><code>_write_row</code></span>
</li>
<li>
<span class="reference-chip"><code>_deserialize_custom_fields</code></span>
</li>
<li>
<span class="reference-chip"><code>_generate_agreement_id</code></span>
</li>
<li>
<span class="reference-chip"><code>_generate_steward_id</code></span>
</li>
<li>
<span class="reference-chip"><code>_get_notebookutils</code></span>
</li>
<li>
<span class="reference-chip"><code>_get_widget_visible_fields</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_config_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_html_escape</code></span>
</li>
<li>
<span class="reference-chip"><code>_latest_agreement_versions</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_coerce_row_dicts</code></span>, <span class="reference-chip"><code>_parse_contract_version</code></span>
</li>
<li>
<span class="reference-chip"><code>_latest_by_key</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_coerce_row_dicts</code></span>
</li>
<li>
<span class="reference-chip"><code>_list_all_data_agreement_rows</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_coerce_row_dicts</code></span>, <span class="reference-chip"><code>_config_value</code></span>
</li>
<li>
<span class="reference-chip"><code>_list_data_agreements</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_latest_agreement_versions</code></span>, <span class="reference-chip"><code>_list_all_data_agreement_rows</code></span>
</li>
<li>
<span class="reference-chip"><code>_list_data_stewards</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_active_steward</code></span>, <span class="reference-chip"><code>_config_value</code></span>, <span class="reference-chip"><code>_latest_by_key</code></span>
</li>
<li>
<span class="reference-chip"><code>_next_minor_version</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_parse_contract_version</code></span>
</li>
<li>
<span class="reference-chip"><code>_parse_contract_version</code></span>
</li>
<li>
<span class="reference-chip"><code>_parse_iso_date</code></span>
</li>
<li>
<span class="reference-chip"><code>_prepare_evidence_file_references</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_get_notebookutils</code></span>
</li>
<li>
<span class="reference-chip"><code>_render_agreement_evidence_widget_workflow</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_list_all_data_agreement_rows</code></span>, <span class="reference-chip"><code>_render_searchable_selector</code></span>, <span class="reference-chip"><code>_require_ipywidgets</code></span>, <span class="reference-chip"><code>_save_agreement_evidence_records</code></span>, <span class="reference-chip"><code>_widget_common</code></span>
</li>
<li>
<span class="reference-chip"><code>_render_custom_fields</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_require_ipywidgets</code></span>, <span class="reference-chip"><code>_to_bool</code></span>, <span class="reference-chip"><code>_widget_common</code></span>
</li>
<li>
<span class="reference-chip"><code>_render_data_agreement_widget_workflow</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_render_maintenance_widget_workflow</code></span>
</li>
<li>
<span class="reference-chip"><code>_render_data_steward_widget_workflow</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_render_maintenance_widget_workflow</code></span>
</li>
<li>
<span class="reference-chip"><code>_render_maintenance_widget_workflow</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_agreement_identity_text</code></span>, <span class="reference-chip"><code>_collect_custom_fields</code></span>, <span class="reference-chip"><code>_config_value</code></span>, <span class="reference-chip"><code>_create_or_update_data_agreement</code></span>, <span class="reference-chip"><code>_create_or_update_data_steward</code></span>, <span class="reference-chip"><code>_deserialize_custom_fields</code></span>, <span class="reference-chip"><code>_get_widget_visible_fields</code></span>, <span class="reference-chip"><code>_list_data_agreements</code></span>, <span class="reference-chip"><code>_list_data_stewards</code></span>, <span class="reference-chip"><code>_render_custom_fields</code></span>, <span class="reference-chip"><code>_render_searchable_selector</code></span>, <span class="reference-chip"><code>_require_ipywidgets</code></span>, <span class="reference-chip"><code>_standard_widget</code></span>, <span class="reference-chip"><code>_to_bool</code></span>, <span class="reference-chip"><code>_to_iso_date</code></span>
</li>
<li>
<span class="reference-chip"><code>_render_searchable_selector</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_html_escape</code></span>, <span class="reference-chip"><code>_widget_common</code></span>
</li>
<li>
<span class="reference-chip"><code>_require_ipywidgets</code></span>
</li>
<li>
<span class="reference-chip"><code>_save_agreement_evidence_records</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_config_value</code></span>, <span class="reference-chip"><code>_prepare_evidence_file_references</code></span>, <span class="reference-chip"><code>_write_row</code></span>
</li>
<li>
<span class="reference-chip"><code>_serialize_custom_fields</code></span>
</li>
<li>
<span class="reference-chip"><code>_standard_widget</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_require_ipywidgets</code></span>, <span class="reference-chip"><code>_to_bool</code></span>, <span class="reference-chip"><code>_widget_common</code></span>
</li>
<li>
<span class="reference-chip"><code>_to_bool</code></span>
</li>
<li>
<span class="reference-chip"><code>_to_iso_date</code></span>
</li>
<li>
<span class="reference-chip"><code>_widget_common</code></span>
</li>
<li>
<span class="reference-chip"><code>_write_row</code></span>
</li>
</ul>
</details>

### External callers

**config**
<a class="reference-chip" href="config/#_setup_metadata_tables_workflow"><code>_setup_metadata_tables_workflow</code></a>

**pipeline**
<a class="reference-chip" href="../reference/start_pipeline_run/"><code>start_pipeline_run</code></a>

### External callees

**config**
<a class="reference-chip" href="config/#resolve_fabric_context"><code>resolve_fabric_context</code></a>

**io_core**
<a class="reference-chip" href="io_core/#configured_lakehouse_schema"><code>configured_lakehouse_schema</code></a>, <a class="reference-chip" href="io_core/#read_lakehouse_table_core"><code>read_lakehouse_table_core</code></a>, <a class="reference-chip" href="io_core/#write_lakehouse_table_core"><code>write_lakehouse_table_core</code></a>

**metadata**
<a class="reference-chip" href="metadata/#_build_runtime_audit_fields"><code>_build_runtime_audit_fields</code></a>, <a class="reference-chip" href="metadata/#_current_notebook_active_registrations"><code>_current_notebook_active_registrations</code></a>, <a class="reference-chip" href="metadata/#_register_current_notebook"><code>_register_current_notebook</code></a>
