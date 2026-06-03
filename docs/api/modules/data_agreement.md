# `data_agreement` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module purpose

Owns agreement metadata capture, audited record building, metadata commit helpers, and agreement selection helpers used to anchor notebook workflows to approved business agreements.

## Intended notebook call flow

1. `00_env_config` assembles `CONFIG` and calls `setup_data_agreement_tables(...)` to create or check agreement metadata tables.
2. `01_da_<agreement>` calls `render_agreement_intake_app(...)` to render the framework-managed intake form.
3. Downstream notebooks call `select_agreement(CONFIG, ENV, spark_session=spark)` and `get_selected_agreement()` to bind work to a committed agreement version.

Non-exported schema, persistence, custom-field, and list helpers are implementation details and should not be imported from `fabricops_kit`.

Agreement technical audit fields are framework-managed through `metadata.build_runtime_audit_fields(...)`.

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
      <td>56</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>3</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td>—</td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>config</code>, <code>fabric_input_output</code>, <code>metadata</code></td>
    </tr>
  </tbody>
</table>

## Primary notebook API

Use these callables in standard FabricOps notebooks.

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
      <td><a href="../../reference/get_selected_agreement/"><code>get_selected_agreement</code></a></td>
      <td>Primary notebook API</td>
      <td>function</td>
      <td>Return the agreement selected by :func:`select_agreement`.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/render_agreement_intake_app/"><code>render_agreement_intake_app</code></a></td>
      <td>Primary notebook API</td>
      <td>function</td>
      <td>Render and wire the default agreement-intake form application.</td>
      <td><a href="../../reference/internal/data_agreement/_render_agreement_evidence_widget/"><code>_render_agreement_evidence_widget</code></a> (internal), <a href="../../reference/internal/data_agreement/_render_maintenance_widget/"><code>_render_maintenance_widget</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/render_data_agreement_widget/"><code>render_data_agreement_widget</code></a></td>
      <td>Primary notebook API</td>
      <td>function</td>
      <td>Render append-only agreement maintenance using active steward rows.</td>
      <td><a href="../../reference/internal/data_agreement/_render_maintenance_widget/"><code>_render_maintenance_widget</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/render_data_steward_widget/"><code>render_data_steward_widget</code></a></td>
      <td>Primary notebook API</td>
      <td>function</td>
      <td>Render append-only data steward maintenance.</td>
      <td><a href="../../reference/internal/data_agreement/_render_maintenance_widget/"><code>_render_maintenance_widget</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/select_agreement/"><code>select_agreement</code></a></td>
      <td>Primary notebook API</td>
      <td>function</td>
      <td>Render a widget dropdown and store selected agreement metadata row in module state.</td>
      <td><a href="../../reference/internal/data_agreement/_agreement_dropdown_options/"><code>_agreement_dropdown_options</code></a> (internal), <a href="../../reference/internal/data_agreement/_latest_agreement_versions/"><code>_latest_agreement_versions</code></a> (internal), <a href="../../reference/internal/data_agreement/_load_agreements/"><code>_load_agreements</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/setup_data_agreement_tables/"><code>setup_data_agreement_tables</code></a></td>
      <td>Primary notebook API</td>
      <td>function</td>
      <td>Create, validate, and report readiness for agreement metadata tables.</td>
      <td><a href="../../reference/internal/data_agreement/_ensure_metadata_tables/"><code>_ensure_metadata_tables</code></a> (internal), <a href="../../reference/internal/data_agreement/_list_data_stewards/"><code>_list_data_stewards</code></a> (internal)</td>
    </tr>
  </tbody>
</table>
</div>

## Internal helpers

These non-exported helpers support framework internals and diagnostics. Do not import them from `fabricops_kit`.

### Internal workflow helpers

<div class="module-table-scroll">
<table>
  <thead>
    <tr>
      <th>Helper</th>
      <th>Classification</th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>
</div>

### Private implementation helpers

<div class="module-table-scroll">
<table>
  <thead>
    <tr>
      <th>Helper</th>
      <th>Classification</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_active_steward/"><code>_active_steward</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_agreement_dropdown_options/"><code>_agreement_dropdown_options</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_agreement_identity_text/"><code>_agreement_identity_text</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_agreement_version_options/"><code>_agreement_version_options</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_build_steward_dropdown_options/"><code>_build_steward_dropdown_options</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_business_agreement_snapshot/"><code>_business_agreement_snapshot</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_collect_custom_fields/"><code>_collect_custom_fields</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_column_names/"><code>_column_names</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_config_value/"><code>_config_value</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_create_or_update_data_agreement/"><code>_create_or_update_data_agreement</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_create_or_update_data_steward/"><code>_create_or_update_data_steward</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_default_dropdown_value/"><code>_default_dropdown_value</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_deserialize_custom_fields/"><code>_deserialize_custom_fields</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_ensure_metadata_tables/"><code>_ensure_metadata_tables</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_field_label/"><code>_field_label</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_generate_agreement_id/"><code>_generate_agreement_id</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_generate_steward_id/"><code>_generate_steward_id</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_get_data_agreement_evidence_schema/"><code>_get_data_agreement_evidence_schema</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_get_data_agreement_schema/"><code>_get_data_agreement_schema</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_get_data_steward_schema/"><code>_get_data_steward_schema</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_get_standard_runtime_audit_columns/"><code>_get_standard_runtime_audit_columns</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_get_widget_visible_fields/"><code>_get_widget_visible_fields</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_latest_agreement_versions/"><code>_latest_agreement_versions</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_latest_by_key/"><code>_latest_by_key</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_list_all_data_agreement_rows/"><code>_list_all_data_agreement_rows</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_list_data_agreements/"><code>_list_data_agreements</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_list_data_stewards/"><code>_list_data_stewards</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_load_active_data_steward_profiles/"><code>_load_active_data_steward_profiles</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_load_agreements/"><code>_load_agreements</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_metadata_lakehouse_file_path/"><code>_metadata_lakehouse_file_path</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_next_minor_version/"><code>_next_minor_version</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_option_values/"><code>_option_values</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_parse_contract_version/"><code>_parse_contract_version</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_parse_iso_date/"><code>_parse_iso_date</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_render_agreement_evidence_widget/"><code>_render_agreement_evidence_widget</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_render_custom_fields/"><code>_render_custom_fields</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_render_maintenance_widget/"><code>_render_maintenance_widget</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_resolve_agreement_identity/"><code>_resolve_agreement_identity</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_safe_evidence_file_name/"><code>_safe_evidence_file_name</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_save_agreement_evidence_records/"><code>_save_agreement_evidence_records</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_serialize_custom_fields/"><code>_serialize_custom_fields</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_set_widget_value/"><code>_set_widget_value</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_standard_widget/"><code>_standard_widget</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_steward_active_value/"><code>_steward_active_value</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_steward_role_options/"><code>_steward_role_options</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_table_name/"><code>_table_name</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_to_bool/"><code>_to_bool</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_to_iso_date/"><code>_to_iso_date</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_uploaded_file_items/"><code>_uploaded_file_items</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_widget_common/"><code>_widget_common</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_widget_config/"><code>_widget_config</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_widget_field_value/"><code>_widget_field_value</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_widget_layout/"><code>_widget_layout</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_write_evidence_file/"><code>_write_evidence_file</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_write_row/"><code>_write_row</code></a></td>
      <td>Private implementation helper</td>
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
<a class="reference-chip" href="../../reference/get_selected_agreement/"><code>get_selected_agreement</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/render_agreement_intake_app/"><code>render_agreement_intake_app</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_render_agreement_evidence_widget"><code>_render_agreement_evidence_widget</code></a>, <a class="reference-chip" href="#_render_maintenance_widget"><code>_render_maintenance_widget</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/render_data_agreement_widget/"><code>render_data_agreement_widget</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_render_maintenance_widget"><code>_render_maintenance_widget</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/render_data_steward_widget/"><code>render_data_steward_widget</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_render_maintenance_widget"><code>_render_maintenance_widget</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/select_agreement/"><code>select_agreement</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_agreement_dropdown_options"><code>_agreement_dropdown_options</code></a>, <a class="reference-chip" href="#_latest_agreement_versions"><code>_latest_agreement_versions</code></a>, <a class="reference-chip" href="#_load_agreements"><code>_load_agreements</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/setup_data_agreement_tables/"><code>setup_data_agreement_tables</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_ensure_metadata_tables"><code>_ensure_metadata_tables</code></a>, <a class="reference-chip" href="#_list_data_stewards"><code>_list_data_stewards</code></a>
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
      <td><a href="../../reference/internal/data_agreement/_active_steward/"><code>_active_steward</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_agreement_dropdown_options/"><code>_agreement_dropdown_options</code></a></td>
      <td><a href="../../reference/select_agreement/"><code>select_agreement</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_agreement_identity_text/"><code>_agreement_identity_text</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_agreement_version_options/"><code>_agreement_version_options</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_build_steward_dropdown_options/"><code>_build_steward_dropdown_options</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_business_agreement_snapshot/"><code>_business_agreement_snapshot</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_collect_custom_fields/"><code>_collect_custom_fields</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_column_names/"><code>_column_names</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_config_value/"><code>_config_value</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_create_or_update_data_agreement/"><code>_create_or_update_data_agreement</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_create_or_update_data_steward/"><code>_create_or_update_data_steward</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_default_dropdown_value/"><code>_default_dropdown_value</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_deserialize_custom_fields/"><code>_deserialize_custom_fields</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_ensure_metadata_tables/"><code>_ensure_metadata_tables</code></a></td>
      <td><a href="../../reference/setup_data_agreement_tables/"><code>setup_data_agreement_tables</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_field_label/"><code>_field_label</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_generate_agreement_id/"><code>_generate_agreement_id</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_generate_steward_id/"><code>_generate_steward_id</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_get_data_agreement_evidence_schema/"><code>_get_data_agreement_evidence_schema</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_get_data_agreement_schema/"><code>_get_data_agreement_schema</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_get_data_steward_schema/"><code>_get_data_steward_schema</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_get_standard_runtime_audit_columns/"><code>_get_standard_runtime_audit_columns</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_get_widget_visible_fields/"><code>_get_widget_visible_fields</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_latest_agreement_versions/"><code>_latest_agreement_versions</code></a></td>
      <td><a href="../../reference/select_agreement/"><code>select_agreement</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_latest_by_key/"><code>_latest_by_key</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_list_all_data_agreement_rows/"><code>_list_all_data_agreement_rows</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_list_data_agreements/"><code>_list_data_agreements</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_list_data_stewards/"><code>_list_data_stewards</code></a></td>
      <td><a href="../../reference/setup_data_agreement_tables/"><code>setup_data_agreement_tables</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_load_active_data_steward_profiles/"><code>_load_active_data_steward_profiles</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_load_agreements/"><code>_load_agreements</code></a></td>
      <td><a href="../../reference/select_agreement/"><code>select_agreement</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_metadata_lakehouse_file_path/"><code>_metadata_lakehouse_file_path</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_next_minor_version/"><code>_next_minor_version</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_option_values/"><code>_option_values</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_parse_contract_version/"><code>_parse_contract_version</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_parse_iso_date/"><code>_parse_iso_date</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_render_agreement_evidence_widget/"><code>_render_agreement_evidence_widget</code></a></td>
      <td><a href="../../reference/render_agreement_intake_app/"><code>render_agreement_intake_app</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_render_custom_fields/"><code>_render_custom_fields</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_render_maintenance_widget/"><code>_render_maintenance_widget</code></a></td>
      <td><a href="../../reference/render_agreement_intake_app/"><code>render_agreement_intake_app</code></a>, <a href="../../reference/render_data_agreement_widget/"><code>render_data_agreement_widget</code></a>, <a href="../../reference/render_data_steward_widget/"><code>render_data_steward_widget</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_resolve_agreement_identity/"><code>_resolve_agreement_identity</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_safe_evidence_file_name/"><code>_safe_evidence_file_name</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_save_agreement_evidence_records/"><code>_save_agreement_evidence_records</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_serialize_custom_fields/"><code>_serialize_custom_fields</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_set_widget_value/"><code>_set_widget_value</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_standard_widget/"><code>_standard_widget</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_steward_active_value/"><code>_steward_active_value</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_steward_role_options/"><code>_steward_role_options</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_table_name/"><code>_table_name</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_to_bool/"><code>_to_bool</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_to_iso_date/"><code>_to_iso_date</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_uploaded_file_items/"><code>_uploaded_file_items</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_widget_common/"><code>_widget_common</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_widget_config/"><code>_widget_config</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_widget_field_value/"><code>_widget_field_value</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_widget_layout/"><code>_widget_layout</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_write_evidence_file/"><code>_write_evidence_file</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_write_row/"><code>_write_row</code></a></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_active_steward"><code>_active_steward</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_to_bool"><code>_to_bool</code></a>
</li>
<li>
<a class="reference-chip" href="#_agreement_dropdown_options"><code>_agreement_dropdown_options</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_latest_agreement_versions"><code>_latest_agreement_versions</code></a>
</li>
<li>
<a class="reference-chip" href="#_agreement_identity_text"><code>_agreement_identity_text</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_next_minor_version"><code>_next_minor_version</code></a>
</li>
<li>
<a class="reference-chip" href="#_agreement_version_options"><code>_agreement_version_options</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>, <a class="reference-chip" href="#_parse_contract_version"><code>_parse_contract_version</code></a>
</li>
<li>
<a class="reference-chip" href="#_build_steward_dropdown_options"><code>_build_steward_dropdown_options</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>
</li>
<li>
<a class="reference-chip" href="#_business_agreement_snapshot"><code>_business_agreement_snapshot</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_deserialize_custom_fields"><code>_deserialize_custom_fields</code></a>, <a class="reference-chip" href="#_serialize_custom_fields"><code>_serialize_custom_fields</code></a>
</li>
<li>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>
</li>
<li>
<a class="reference-chip" href="#_collect_custom_fields"><code>_collect_custom_fields</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_to_iso_date"><code>_to_iso_date</code></a>
</li>
<li>
<a class="reference-chip" href="#_column_names"><code>_column_names</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>
</li>
<li>
<a class="reference-chip" href="#_config_value"><code>_config_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_create_or_update_data_agreement"><code>_create_or_update_data_agreement</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_business_agreement_snapshot"><code>_business_agreement_snapshot</code></a>, <a class="reference-chip" href="#_generate_agreement_id"><code>_generate_agreement_id</code></a>, <a class="reference-chip" href="#_list_all_data_agreement_rows"><code>_list_all_data_agreement_rows</code></a>, <a class="reference-chip" href="#_list_data_stewards"><code>_list_data_stewards</code></a>, <a class="reference-chip" href="#_next_minor_version"><code>_next_minor_version</code></a>, <a class="reference-chip" href="#_parse_contract_version"><code>_parse_contract_version</code></a>, <a class="reference-chip" href="#_parse_iso_date"><code>_parse_iso_date</code></a>, <a class="reference-chip" href="#_serialize_custom_fields"><code>_serialize_custom_fields</code></a>, <a class="reference-chip" href="#_table_name"><code>_table_name</code></a>, <a class="reference-chip" href="#_write_row"><code>_write_row</code></a>
</li>
<li>
<a class="reference-chip" href="#_create_or_update_data_steward"><code>_create_or_update_data_steward</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_generate_steward_id"><code>_generate_steward_id</code></a>, <a class="reference-chip" href="#_parse_iso_date"><code>_parse_iso_date</code></a>, <a class="reference-chip" href="#_serialize_custom_fields"><code>_serialize_custom_fields</code></a>, <a class="reference-chip" href="#_steward_active_value"><code>_steward_active_value</code></a>, <a class="reference-chip" href="#_steward_role_options"><code>_steward_role_options</code></a>, <a class="reference-chip" href="#_table_name"><code>_table_name</code></a>, <a class="reference-chip" href="#_to_bool"><code>_to_bool</code></a>, <a class="reference-chip" href="#_write_row"><code>_write_row</code></a>
</li>
<li>
<a class="reference-chip" href="#_default_dropdown_value"><code>_default_dropdown_value</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_option_values"><code>_option_values</code></a>
</li>
<li>
<a class="reference-chip" href="#_deserialize_custom_fields"><code>_deserialize_custom_fields</code></a>
</li>
<li>
<a class="reference-chip" href="#_ensure_metadata_tables"><code>_ensure_metadata_tables</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_column_names"><code>_column_names</code></a>, <a class="reference-chip" href="#_get_data_agreement_evidence_schema"><code>_get_data_agreement_evidence_schema</code></a>, <a class="reference-chip" href="#_get_data_agreement_schema"><code>_get_data_agreement_schema</code></a>, <a class="reference-chip" href="#_get_data_steward_schema"><code>_get_data_steward_schema</code></a>, <a class="reference-chip" href="#_table_name"><code>_table_name</code></a>
</li>
<li>
<a class="reference-chip" href="#_field_label"><code>_field_label</code></a>
</li>
<li>
<a class="reference-chip" href="#_generate_agreement_id"><code>_generate_agreement_id</code></a>
</li>
<li>
<a class="reference-chip" href="#_generate_steward_id"><code>_generate_steward_id</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_data_agreement_evidence_schema"><code>_get_data_agreement_evidence_schema</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_data_agreement_schema"><code>_get_data_agreement_schema</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_data_steward_schema"><code>_get_data_steward_schema</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_standard_runtime_audit_columns"><code>_get_standard_runtime_audit_columns</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_widget_visible_fields"><code>_get_widget_visible_fields</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_get_standard_runtime_audit_columns"><code>_get_standard_runtime_audit_columns</code></a>, <a class="reference-chip" href="#_widget_config"><code>_widget_config</code></a>
</li>
<li>
<a class="reference-chip" href="#_latest_agreement_versions"><code>_latest_agreement_versions</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>, <a class="reference-chip" href="#_parse_contract_version"><code>_parse_contract_version</code></a>
</li>
<li>
<a class="reference-chip" href="#_latest_by_key"><code>_latest_by_key</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>
</li>
<li>
<a class="reference-chip" href="#_list_all_data_agreement_rows"><code>_list_all_data_agreement_rows</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>, <a class="reference-chip" href="#_table_name"><code>_table_name</code></a>
</li>
<li>
<a class="reference-chip" href="#_list_data_agreements"><code>_list_data_agreements</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_latest_agreement_versions"><code>_latest_agreement_versions</code></a>, <a class="reference-chip" href="#_list_all_data_agreement_rows"><code>_list_all_data_agreement_rows</code></a>
</li>
<li>
<a class="reference-chip" href="#_list_data_stewards"><code>_list_data_stewards</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_active_steward"><code>_active_steward</code></a>, <a class="reference-chip" href="#_latest_by_key"><code>_latest_by_key</code></a>, <a class="reference-chip" href="#_table_name"><code>_table_name</code></a>
</li>
<li>
<a class="reference-chip" href="#_load_active_data_steward_profiles"><code>_load_active_data_steward_profiles</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_build_steward_dropdown_options"><code>_build_steward_dropdown_options</code></a>, <a class="reference-chip" href="#_list_data_stewards"><code>_list_data_stewards</code></a>
</li>
<li>
<a class="reference-chip" href="#_load_agreements"><code>_load_agreements</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_list_data_agreements"><code>_list_data_agreements</code></a>
</li>
<li>
<a class="reference-chip" href="#_metadata_lakehouse_file_path"><code>_metadata_lakehouse_file_path</code></a>
</li>
<li>
<a class="reference-chip" href="#_next_minor_version"><code>_next_minor_version</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_parse_contract_version"><code>_parse_contract_version</code></a>
</li>
<li>
<a class="reference-chip" href="#_option_values"><code>_option_values</code></a>
</li>
<li>
<a class="reference-chip" href="#_parse_contract_version"><code>_parse_contract_version</code></a>
</li>
<li>
<a class="reference-chip" href="#_parse_iso_date"><code>_parse_iso_date</code></a>
</li>
<li>
<a class="reference-chip" href="#_render_agreement_evidence_widget"><code>_render_agreement_evidence_widget</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_agreement_version_options"><code>_agreement_version_options</code></a>, <a class="reference-chip" href="#_list_all_data_agreement_rows"><code>_list_all_data_agreement_rows</code></a>, <a class="reference-chip" href="#_save_agreement_evidence_records"><code>_save_agreement_evidence_records</code></a>, <a class="reference-chip" href="#_widget_common"><code>_widget_common</code></a>
</li>
<li>
<a class="reference-chip" href="#_render_custom_fields"><code>_render_custom_fields</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_default_dropdown_value"><code>_default_dropdown_value</code></a>, <a class="reference-chip" href="#_field_label"><code>_field_label</code></a>, <a class="reference-chip" href="#_to_bool"><code>_to_bool</code></a>, <a class="reference-chip" href="#_widget_common"><code>_widget_common</code></a>
</li>
<li>
<a class="reference-chip" href="#_render_maintenance_widget"><code>_render_maintenance_widget</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_agreement_identity_text"><code>_agreement_identity_text</code></a>, <a class="reference-chip" href="#_build_steward_dropdown_options"><code>_build_steward_dropdown_options</code></a>, <a class="reference-chip" href="#_collect_custom_fields"><code>_collect_custom_fields</code></a>, <a class="reference-chip" href="#_create_or_update_data_agreement"><code>_create_or_update_data_agreement</code></a>, <a class="reference-chip" href="#_create_or_update_data_steward"><code>_create_or_update_data_steward</code></a>, <a class="reference-chip" href="#_default_dropdown_value"><code>_default_dropdown_value</code></a>, <a class="reference-chip" href="#_deserialize_custom_fields"><code>_deserialize_custom_fields</code></a>, <a class="reference-chip" href="#_get_widget_visible_fields"><code>_get_widget_visible_fields</code></a>, <a class="reference-chip" href="#_list_data_agreements"><code>_list_data_agreements</code></a>, <a class="reference-chip" href="#_list_data_stewards"><code>_list_data_stewards</code></a>, <a class="reference-chip" href="#_option_values"><code>_option_values</code></a>, <a class="reference-chip" href="#_render_custom_fields"><code>_render_custom_fields</code></a>, <a class="reference-chip" href="#_set_widget_value"><code>_set_widget_value</code></a>, <a class="reference-chip" href="#_standard_widget"><code>_standard_widget</code></a>, <a class="reference-chip" href="#_steward_role_options"><code>_steward_role_options</code></a>, <a class="reference-chip" href="#_widget_common"><code>_widget_common</code></a>, <a class="reference-chip" href="#_widget_config"><code>_widget_config</code></a>, <a class="reference-chip" href="#_widget_field_value"><code>_widget_field_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_resolve_agreement_identity"><code>_resolve_agreement_identity</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_generate_agreement_id"><code>_generate_agreement_id</code></a>, <a class="reference-chip" href="#_next_minor_version"><code>_next_minor_version</code></a>
</li>
<li>
<a class="reference-chip" href="#_safe_evidence_file_name"><code>_safe_evidence_file_name</code></a>
</li>
<li>
<a class="reference-chip" href="#_save_agreement_evidence_records"><code>_save_agreement_evidence_records</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_safe_evidence_file_name"><code>_safe_evidence_file_name</code></a>, <a class="reference-chip" href="#_table_name"><code>_table_name</code></a>, <a class="reference-chip" href="#_uploaded_file_items"><code>_uploaded_file_items</code></a>, <a class="reference-chip" href="#_write_evidence_file"><code>_write_evidence_file</code></a>, <a class="reference-chip" href="#_write_row"><code>_write_row</code></a>
</li>
<li>
<a class="reference-chip" href="#_serialize_custom_fields"><code>_serialize_custom_fields</code></a>
</li>
<li>
<a class="reference-chip" href="#_set_widget_value"><code>_set_widget_value</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_default_dropdown_value"><code>_default_dropdown_value</code></a>, <a class="reference-chip" href="#_to_bool"><code>_to_bool</code></a>
</li>
<li>
<a class="reference-chip" href="#_standard_widget"><code>_standard_widget</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_default_dropdown_value"><code>_default_dropdown_value</code></a>, <a class="reference-chip" href="#_field_label"><code>_field_label</code></a>, <a class="reference-chip" href="#_to_bool"><code>_to_bool</code></a>, <a class="reference-chip" href="#_widget_common"><code>_widget_common</code></a>
</li>
<li>
<a class="reference-chip" href="#_steward_active_value"><code>_steward_active_value</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_active_steward"><code>_active_steward</code></a>
</li>
<li>
<a class="reference-chip" href="#_steward_role_options"><code>_steward_role_options</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_config_value"><code>_config_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_table_name"><code>_table_name</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_config_value"><code>_config_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_to_bool"><code>_to_bool</code></a>
</li>
<li>
<a class="reference-chip" href="#_to_iso_date"><code>_to_iso_date</code></a>
</li>
<li>
<a class="reference-chip" href="#_uploaded_file_items"><code>_uploaded_file_items</code></a>
</li>
<li>
<a class="reference-chip" href="#_widget_common"><code>_widget_common</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_widget_layout"><code>_widget_layout</code></a>
</li>
<li>
<a class="reference-chip" href="#_widget_config"><code>_widget_config</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_config_value"><code>_config_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_widget_field_value"><code>_widget_field_value</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_to_iso_date"><code>_to_iso_date</code></a>
</li>
<li>
<a class="reference-chip" href="#_widget_layout"><code>_widget_layout</code></a>
</li>
<li>
<a class="reference-chip" href="#_write_evidence_file"><code>_write_evidence_file</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_metadata_lakehouse_file_path"><code>_metadata_lakehouse_file_path</code></a>
</li>
<li>
<a class="reference-chip" href="#_write_row"><code>_write_row</code></a>
</li>
</ul>
</details>

### External callers

None.
### External callees

**fabric_input_output**
<a class="reference-chip" href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a>, <a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>

**metadata**
<a class="reference-chip" href="../../reference/build_runtime_audit_fields/"><code>build_runtime_audit_fields</code></a>
