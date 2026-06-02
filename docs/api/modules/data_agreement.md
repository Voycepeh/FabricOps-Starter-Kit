# `data_agreement` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module purpose

Owns agreement metadata capture, audited record building, metadata commit helpers, and agreement selection helpers used to anchor notebook workflows to approved business agreements.

## Intended notebook call flow

1. `00_env_config` assembles `CONFIG` and calls `setup_data_agreement_tables(...)` to create or check agreement metadata tables.
2. `01_da_<agreement>` calls `render_agreement_intake_app(...)` to render the framework-managed intake form.
3. Downstream notebooks call `load_agreements(...)`, `select_agreement(...)`, and `get_selected_agreement()` to bind work to a committed agreement version.

Lower-level form, collection, and commit functions remain supported only for advanced custom workflows. Non-exported helpers are implementation details and should not be imported from `fabricops_kit`.

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
      <td>24</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>18</td>
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
      <td><a href="../../reference/load_agreements/"><code>load_agreements</code></a></td>
      <td>Primary notebook API</td>
      <td>function</td>
      <td>Load latest versioned agreement rows from the configured metadata lakehouse.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/render_agreement_intake_app/"><code>render_agreement_intake_app</code></a></td>
      <td>Primary notebook API</td>
      <td>function</td>
      <td>Render and wire the default agreement-intake form application.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/select_agreement/"><code>select_agreement</code></a></td>
      <td>Primary notebook API</td>
      <td>function</td>
      <td>Render a widget dropdown and store selected agreement metadata row in module state.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/setup_data_agreement_tables/"><code>setup_data_agreement_tables</code></a></td>
      <td>Primary notebook API</td>
      <td>function</td>
      <td>Create, validate, and report readiness for agreement metadata tables.</td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

## Optional advanced customization API

Normal notebook users should not call these lower-level functions. Use them only when intentionally customizing the agreement-intake workflow.

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
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Build a validated append-only agreement row without writing it.</td>
      <td><a href="../../reference/internal/data_agreement/_generate_agreement_id/"><code>_generate_agreement_id</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/collect_custom_fields/"><code>collect_custom_fields</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Collect and validate configured JSON-backed custom-field values.</td>
      <td><a href="../../reference/internal/data_agreement/_to_iso_date/"><code>_to_iso_date</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/commit_agreement_metadata/"><code>commit_agreement_metadata</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Append a row returned by :func:`collect_agreement_metadata`.</td>
      <td><a href="../../reference/internal/data_agreement/_table_name/"><code>_table_name</code></a> (internal), <a href="../../reference/internal/data_agreement/_write_row/"><code>_write_row</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/create_agreement_form/"><code>create_agreement_form</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Render the agreement maintenance widget for advanced custom notebooks.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/create_or_update_data_agreement/"><code>create_or_update_data_agreement</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Append a created agreement or a new semantic version with runtime audit fields.</td>
      <td><a href="../../reference/internal/data_agreement/_generate_agreement_id/"><code>_generate_agreement_id</code></a> (internal), <a href="../../reference/internal/data_agreement/_table_name/"><code>_table_name</code></a> (internal), <a href="../../reference/internal/data_agreement/_write_row/"><code>_write_row</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/create_or_update_data_steward/"><code>create_or_update_data_steward</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Append a created or updated steward assignment with runtime audit fields.</td>
      <td><a href="../../reference/internal/data_agreement/_table_name/"><code>_table_name</code></a> (internal), <a href="../../reference/internal/data_agreement/_write_row/"><code>_write_row</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/deserialize_custom_fields/"><code>deserialize_custom_fields</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Deserialize stored custom-field JSON for widget display.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/ensure_metadata_tables/"><code>ensure_metadata_tables</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Idempotently create or validate the lightweight 01_da metadata tables.</td>
      <td><a href="../../reference/internal/data_agreement/_column_names/"><code>_column_names</code></a> (internal), <a href="../../reference/internal/data_agreement/_table_name/"><code>_table_name</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/get_data_agreement_schema/"><code>get_data_agreement_schema</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Return the lightweight agreement metadata-table schema.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/get_data_steward_schema/"><code>get_data_steward_schema</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Return the lightweight steward metadata-table schema.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/get_standard_runtime_audit_columns/"><code>get_standard_runtime_audit_columns</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Return backend-only runtime audit columns shared by intake tables.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/get_widget_visible_fields/"><code>get_widget_visible_fields</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Return configured editable widget fields without backend audit columns.</td>
      <td><a href="../../reference/internal/data_agreement/_widget_config/"><code>_widget_config</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/list_data_agreements/"><code>list_data_agreements</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>List latest agreement versions from the configured metadata lakehouse.</td>
      <td><a href="../../reference/internal/data_agreement/_table_name/"><code>_table_name</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/list_data_stewards/"><code>list_data_stewards</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>List latest steward assignments, optionally filtering to active rows.</td>
      <td><a href="../../reference/internal/data_agreement/_active_steward/"><code>_active_steward</code></a> (internal), <a href="../../reference/internal/data_agreement/_latest_by_key/"><code>_latest_by_key</code></a> (internal), <a href="../../reference/internal/data_agreement/_table_name/"><code>_table_name</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/read_agreement_form/"><code>read_agreement_form</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Read user-facing and custom values from an agreement widget form.</td>
      <td><a href="../../reference/internal/data_agreement/_to_iso_date/"><code>_to_iso_date</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/render_custom_fields/"><code>render_custom_fields</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Render configured JSON-backed custom intake widgets.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/render_data_agreement_widget/"><code>render_data_agreement_widget</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Render append-only agreement maintenance using active steward rows.</td>
      <td><a href="../../reference/internal/data_agreement/_render_maintenance_widget/"><code>_render_maintenance_widget</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/render_data_steward_widget/"><code>render_data_steward_widget</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Render append-only data steward maintenance.</td>
      <td><a href="../../reference/internal/data_agreement/_render_maintenance_widget/"><code>_render_maintenance_widget</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/serialize_custom_fields/"><code>serialize_custom_fields</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Serialize organization-specific intake values to deterministic JSON.</td>
      <td>—</td>
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
    <tr>
      <td><a href="../../reference/internal/data_agreement/agreement_dropdown_options/"><code>agreement_dropdown_options</code></a></td>
      <td>Internal helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/latest_agreement_versions/"><code>latest_agreement_versions</code></a></td>
      <td>Internal helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/load_active_data_steward_profiles/"><code>load_active_data_steward_profiles</code></a></td>
      <td>Internal helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/next_minor_version/"><code>next_minor_version</code></a></td>
      <td>Internal helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/parse_contract_version/"><code>parse_contract_version</code></a></td>
      <td>Internal helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/resolve_agreement_identity/"><code>resolve_agreement_identity</code></a></td>
      <td>Internal helper</td>
    </tr>
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
      <td><a href="../../reference/internal/data_agreement/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a></td>
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
      <td><a href="../../reference/internal/data_agreement/_generate_agreement_id/"><code>_generate_agreement_id</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_latest_by_key/"><code>_latest_by_key</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_render_maintenance_widget/"><code>_render_maintenance_widget</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_standard_widget/"><code>_standard_widget</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_table_name/"><code>_table_name</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_to_iso_date/"><code>_to_iso_date</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_widget_config/"><code>_widget_config</code></a></td>
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
<a class="reference-chip" href="../../reference/collect_agreement_metadata/"><code>collect_agreement_metadata</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_generate_agreement_id"><code>_generate_agreement_id</code></a>, <a class="reference-chip" href="#next_minor_version"><code>next_minor_version</code></a>, <a class="reference-chip" href="../../reference/serialize_custom_fields/"><code>serialize_custom_fields</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/collect_custom_fields/"><code>collect_custom_fields</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_to_iso_date"><code>_to_iso_date</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/commit_agreement_metadata/"><code>commit_agreement_metadata</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_table_name"><code>_table_name</code></a>, <a class="reference-chip" href="#_write_row"><code>_write_row</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/create_agreement_form/"><code>create_agreement_form</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="../../reference/render_data_agreement_widget/"><code>render_data_agreement_widget</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/create_or_update_data_agreement/"><code>create_or_update_data_agreement</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_generate_agreement_id"><code>_generate_agreement_id</code></a>, <a class="reference-chip" href="#_table_name"><code>_table_name</code></a>, <a class="reference-chip" href="#_write_row"><code>_write_row</code></a>, <a class="reference-chip" href="../../reference/list_data_stewards/"><code>list_data_stewards</code></a>, <a class="reference-chip" href="#next_minor_version"><code>next_minor_version</code></a>, <a class="reference-chip" href="../../reference/serialize_custom_fields/"><code>serialize_custom_fields</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/create_or_update_data_steward/"><code>create_or_update_data_steward</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_table_name"><code>_table_name</code></a>, <a class="reference-chip" href="#_write_row"><code>_write_row</code></a>, <a class="reference-chip" href="../../reference/serialize_custom_fields/"><code>serialize_custom_fields</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/deserialize_custom_fields/"><code>deserialize_custom_fields</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/ensure_metadata_tables/"><code>ensure_metadata_tables</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_column_names"><code>_column_names</code></a>, <a class="reference-chip" href="#_table_name"><code>_table_name</code></a>, <a class="reference-chip" href="../../reference/get_data_agreement_schema/"><code>get_data_agreement_schema</code></a>, <a class="reference-chip" href="../../reference/get_data_steward_schema/"><code>get_data_steward_schema</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/get_data_agreement_schema/"><code>get_data_agreement_schema</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/get_data_steward_schema/"><code>get_data_steward_schema</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/get_selected_agreement/"><code>get_selected_agreement</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/get_standard_runtime_audit_columns/"><code>get_standard_runtime_audit_columns</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/get_widget_visible_fields/"><code>get_widget_visible_fields</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_widget_config"><code>_widget_config</code></a>, <a class="reference-chip" href="../../reference/get_standard_runtime_audit_columns/"><code>get_standard_runtime_audit_columns</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/list_data_agreements/"><code>list_data_agreements</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_table_name"><code>_table_name</code></a>, <a class="reference-chip" href="#latest_agreement_versions"><code>latest_agreement_versions</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/list_data_stewards/"><code>list_data_stewards</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_active_steward"><code>_active_steward</code></a>, <a class="reference-chip" href="#_latest_by_key"><code>_latest_by_key</code></a>, <a class="reference-chip" href="#_table_name"><code>_table_name</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/load_agreements/"><code>load_agreements</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="../../reference/list_data_agreements/"><code>list_data_agreements</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/read_agreement_form/"><code>read_agreement_form</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_to_iso_date"><code>_to_iso_date</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/render_agreement_intake_app/"><code>render_agreement_intake_app</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="../../reference/render_data_agreement_widget/"><code>render_data_agreement_widget</code></a>, <a class="reference-chip" href="../../reference/render_data_steward_widget/"><code>render_data_steward_widget</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/render_custom_fields/"><code>render_custom_fields</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
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
<a class="reference-chip" href="#agreement_dropdown_options"><code>agreement_dropdown_options</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/serialize_custom_fields/"><code>serialize_custom_fields</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/setup_data_agreement_tables/"><code>setup_data_agreement_tables</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="../../reference/ensure_metadata_tables/"><code>ensure_metadata_tables</code></a>, <a class="reference-chip" href="../../reference/list_data_stewards/"><code>list_data_stewards</code></a>
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
      <td><a href="../../reference/list_data_stewards/"><code>list_data_stewards</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_column_names/"><code>_column_names</code></a></td>
      <td><a href="../../reference/ensure_metadata_tables/"><code>ensure_metadata_tables</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_config_value/"><code>_config_value</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_generate_agreement_id/"><code>_generate_agreement_id</code></a></td>
      <td><a href="../../reference/collect_agreement_metadata/"><code>collect_agreement_metadata</code></a>, <a href="../../reference/create_or_update_data_agreement/"><code>create_or_update_data_agreement</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_latest_by_key/"><code>_latest_by_key</code></a></td>
      <td><a href="../../reference/list_data_stewards/"><code>list_data_stewards</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_render_maintenance_widget/"><code>_render_maintenance_widget</code></a></td>
      <td><a href="../../reference/render_data_agreement_widget/"><code>render_data_agreement_widget</code></a>, <a href="../../reference/render_data_steward_widget/"><code>render_data_steward_widget</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_standard_widget/"><code>_standard_widget</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_table_name/"><code>_table_name</code></a></td>
      <td><a href="../../reference/commit_agreement_metadata/"><code>commit_agreement_metadata</code></a>, <a href="../../reference/create_or_update_data_agreement/"><code>create_or_update_data_agreement</code></a>, <a href="../../reference/create_or_update_data_steward/"><code>create_or_update_data_steward</code></a>, <a href="../../reference/ensure_metadata_tables/"><code>ensure_metadata_tables</code></a>, <a href="../../reference/list_data_agreements/"><code>list_data_agreements</code></a>, <a href="../../reference/list_data_stewards/"><code>list_data_stewards</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_to_iso_date/"><code>_to_iso_date</code></a></td>
      <td><a href="../../reference/collect_custom_fields/"><code>collect_custom_fields</code></a>, <a href="../../reference/read_agreement_form/"><code>read_agreement_form</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_widget_config/"><code>_widget_config</code></a></td>
      <td><a href="../../reference/get_widget_visible_fields/"><code>get_widget_visible_fields</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_write_row/"><code>_write_row</code></a></td>
      <td><a href="../../reference/commit_agreement_metadata/"><code>commit_agreement_metadata</code></a>, <a href="../../reference/create_or_update_data_agreement/"><code>create_or_update_data_agreement</code></a>, <a href="../../reference/create_or_update_data_steward/"><code>create_or_update_data_steward</code></a></td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="#_active_steward"><code>_active_steward</code></a>
</li>
<li>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>
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
<a class="reference-chip" href="#_generate_agreement_id"><code>_generate_agreement_id</code></a>
</li>
<li>
<a class="reference-chip" href="#_latest_by_key"><code>_latest_by_key</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>
</li>
<li>
<a class="reference-chip" href="#_render_maintenance_widget"><code>_render_maintenance_widget</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_standard_widget"><code>_standard_widget</code></a>, <a class="reference-chip" href="#_to_iso_date"><code>_to_iso_date</code></a>, <a class="reference-chip" href="#_widget_config"><code>_widget_config</code></a>, <a class="reference-chip" href="../../reference/collect_custom_fields/"><code>collect_custom_fields</code></a>, <a class="reference-chip" href="../../reference/create_or_update_data_agreement/"><code>create_or_update_data_agreement</code></a>, <a class="reference-chip" href="../../reference/create_or_update_data_steward/"><code>create_or_update_data_steward</code></a>, <a class="reference-chip" href="../../reference/deserialize_custom_fields/"><code>deserialize_custom_fields</code></a>, <a class="reference-chip" href="../../reference/get_widget_visible_fields/"><code>get_widget_visible_fields</code></a>, <a class="reference-chip" href="../../reference/list_data_agreements/"><code>list_data_agreements</code></a>, <a class="reference-chip" href="../../reference/list_data_stewards/"><code>list_data_stewards</code></a>, <a class="reference-chip" href="../../reference/render_custom_fields/"><code>render_custom_fields</code></a>
</li>
<li>
<a class="reference-chip" href="#_standard_widget"><code>_standard_widget</code></a>
</li>
<li>
<a class="reference-chip" href="#_table_name"><code>_table_name</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_config_value"><code>_config_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_to_iso_date"><code>_to_iso_date</code></a>
</li>
<li>
<a class="reference-chip" href="#_widget_config"><code>_widget_config</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_config_value"><code>_config_value</code></a>
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
