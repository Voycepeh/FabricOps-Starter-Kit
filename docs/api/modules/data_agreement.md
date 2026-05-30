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
      <td>9</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>14</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>2</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td>—</td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>fabric_input_output</code>, <code>metadata</code></td>
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
      <td>Return the selected agreement row, including its stable and version keys.</td>
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
      <td><a href="../../reference/internal/data_agreement/_column_names/"><code>_column_names</code></a> (internal), <a href="../../reference/internal/data_agreement/_ensure_delta_table/"><code>_ensure_delta_table</code></a> (internal)</td>
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
      <td>Build one validated append-only agreement-version row from intake values.</td>
      <td><a href="../../reference/internal/data_agreement/_parse_required_date/"><code>_parse_required_date</code></a> (internal), <a href="../../reference/internal/data_agreement/_to_iso_date/"><code>_to_iso_date</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/commit_agreement_metadata/"><code>commit_agreement_metadata</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Append one agreement-version row by configured OneLake path.</td>
      <td><a href="../../reference/internal/data_agreement/_ensure_delta_table/"><code>_ensure_delta_table</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/create_agreement_form/"><code>create_agreement_form</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Render the standalone ``01_da`` intake form with ``ipywidgets``.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/read_agreement_form/"><code>read_agreement_form</code></a></td>
      <td>Optional / advanced customization</td>
      <td>function</td>
      <td>Return human-entered values from an ``01_da`` intake form.</td>
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
      <td><a href="../../reference/internal/data_agreement/metadata_lakehouse_root/"><code>metadata_lakehouse_root</code></a></td>
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
      <td><a href="../../reference/internal/data_agreement/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_column_names/"><code>_column_names</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_ensure_delta_table/"><code>_ensure_delta_table</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_generate_agreement_id/"><code>_generate_agreement_id</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_parse_required_date/"><code>_parse_required_date</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_table_path/"><code>_table_path</code></a></td>
      <td>Private implementation helper</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_to_iso_date/"><code>_to_iso_date</code></a></td>
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
<a class="reference-chip" href="#_parse_required_date"><code>_parse_required_date</code></a>, <a class="reference-chip" href="#_to_iso_date"><code>_to_iso_date</code></a>, <a class="reference-chip" href="#resolve_agreement_identity"><code>resolve_agreement_identity</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/commit_agreement_metadata/"><code>commit_agreement_metadata</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_ensure_delta_table"><code>_ensure_delta_table</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/create_agreement_form/"><code>create_agreement_form</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#agreement_dropdown_options"><code>agreement_dropdown_options</code></a>, <a class="reference-chip" href="#load_active_data_steward_profiles"><code>load_active_data_steward_profiles</code></a>, <a class="reference-chip" href="../../reference/load_agreements/"><code>load_agreements</code></a>, <a class="reference-chip" href="#next_minor_version"><code>next_minor_version</code></a>, <a class="reference-chip" href="../../reference/setup_data_agreement_tables/"><code>setup_data_agreement_tables</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/get_selected_agreement/"><code>get_selected_agreement</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/load_agreements/"><code>load_agreements</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#latest_agreement_versions"><code>latest_agreement_versions</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/read_agreement_form/"><code>read_agreement_form</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/render_agreement_intake_app/"><code>render_agreement_intake_app</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="../../reference/collect_agreement_metadata/"><code>collect_agreement_metadata</code></a>, <a class="reference-chip" href="../../reference/commit_agreement_metadata/"><code>commit_agreement_metadata</code></a>, <a class="reference-chip" href="../../reference/create_agreement_form/"><code>create_agreement_form</code></a>, <a class="reference-chip" href="../../reference/load_agreements/"><code>load_agreements</code></a>, <a class="reference-chip" href="../../reference/read_agreement_form/"><code>read_agreement_form</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/select_agreement/"><code>select_agreement</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#agreement_dropdown_options"><code>agreement_dropdown_options</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/setup_data_agreement_tables/"><code>setup_data_agreement_tables</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_column_names"><code>_column_names</code></a>, <a class="reference-chip" href="#_ensure_delta_table"><code>_ensure_delta_table</code></a>, <a class="reference-chip" href="#load_active_data_steward_profiles"><code>load_active_data_steward_profiles</code></a>
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
      <td><a href="../../reference/internal/data_agreement/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_column_names/"><code>_column_names</code></a></td>
      <td><a href="../../reference/setup_data_agreement_tables/"><code>setup_data_agreement_tables</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_ensure_delta_table/"><code>_ensure_delta_table</code></a></td>
      <td><a href="../../reference/commit_agreement_metadata/"><code>commit_agreement_metadata</code></a>, <a href="../../reference/setup_data_agreement_tables/"><code>setup_data_agreement_tables</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_generate_agreement_id/"><code>_generate_agreement_id</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_parse_required_date/"><code>_parse_required_date</code></a></td>
      <td><a href="../../reference/collect_agreement_metadata/"><code>collect_agreement_metadata</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_table_path/"><code>_table_path</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_to_iso_date/"><code>_to_iso_date</code></a></td>
      <td><a href="../../reference/collect_agreement_metadata/"><code>collect_agreement_metadata</code></a></td>
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
</li>
<li>
<a class="reference-chip" href="#_ensure_delta_table"><code>_ensure_delta_table</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_table_path"><code>_table_path</code></a>
</li>
<li>
<a class="reference-chip" href="#_generate_agreement_id"><code>_generate_agreement_id</code></a>
</li>
<li>
<a class="reference-chip" href="#_parse_required_date"><code>_parse_required_date</code></a>
</li>
<li>
<a class="reference-chip" href="#_table_path"><code>_table_path</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#metadata_lakehouse_root"><code>metadata_lakehouse_root</code></a>
</li>
<li>
<a class="reference-chip" href="#_to_iso_date"><code>_to_iso_date</code></a>
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
