# `data_agreement` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 12</span><span class="reference-chip">Internal helpers: 8</span><span class="reference-chip">Outbound: 2</span><span class="reference-chip">Inbound: 0</span></div>

## Module purpose

Owns agreement metadata capture, audited record building, metadata commit helpers, and agreement selection helpers used to anchor notebook workflows to approved business agreements.

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
      <td>12</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>8</td>
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
      <td><a href="../../reference/agreement_dropdown_options/"><code>agreement_dropdown_options</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Build selector options that preserve stable and version keys.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/collect_agreement_metadata/"><code>collect_agreement_metadata</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Build one validated append-only agreement-version row from intake values.</td>
      <td><a href="../../reference/internal/data_agreement/_context_get/"><code>_context_get</code></a> (internal), <a href="../../reference/internal/data_agreement/_derive_agreement_status/"><code>_derive_agreement_status</code></a> (internal), <a href="../../reference/internal/data_agreement/_to_iso_date/"><code>_to_iso_date</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/commit_agreement_metadata/"><code>commit_agreement_metadata</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Append one agreement-version row by configured OneLake path.</td>
      <td><a href="../../reference/internal/data_agreement/_ensure_delta_table/"><code>_ensure_delta_table</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/create_agreement_form/"><code>create_agreement_form</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Render the standalone ``01_da`` intake form with ``ipywidgets``.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/get_selected_agreement/"><code>get_selected_agreement</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Return the selected agreement row, including its stable and version keys.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/latest_agreement_versions/"><code>latest_agreement_versions</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Return only the latest contract version for each stable agreement ID.</td>
      <td><a href="../../reference/internal/data_agreement/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/load_active_data_steward_profiles/"><code>load_active_data_steward_profiles</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Load active steward profiles from the configured metadata lakehouse.</td>
      <td><a href="../../reference/internal/data_agreement/_coerce_row_dicts/"><code>_coerce_row_dicts</code></a> (internal), <a href="../../reference/internal/data_agreement/_ensure_delta_table/"><code>_ensure_delta_table</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/load_agreements/"><code>load_agreements</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Load latest versioned agreement rows from the configured metadata lakehouse.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/read_agreement_form/"><code>read_agreement_form</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Return human-entered values from an ``01_da`` intake form.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/render_agreement_intake_app/"><code>render_agreement_intake_app</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Render and wire the default agreement-intake form application.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/select_agreement/"><code>select_agreement</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Render a widget dropdown and store selected agreement metadata row in module state.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/setup_data_agreement_tables/"><code>setup_data_agreement_tables</code></a></td>
      <td>Essential</td>
      <td>function</td>
      <td>Create empty agreement and steward Delta tables when they do not exist.</td>
      <td><a href="../../reference/internal/data_agreement/_ensure_delta_table/"><code>_ensure_delta_table</code></a> (internal)</td>
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
<a class="reference-chip" href="../../reference/agreement_dropdown_options/"><code>agreement_dropdown_options</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="../../reference/latest_agreement_versions/"><code>latest_agreement_versions</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/collect_agreement_metadata/"><code>collect_agreement_metadata</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_context_get"><code>_context_get</code></a>, <a class="reference-chip" href="#_derive_agreement_status"><code>_derive_agreement_status</code></a>, <a class="reference-chip" href="#_to_iso_date"><code>_to_iso_date</code></a>, <a class="reference-chip" href="#resolve_agreement_identity"><code>resolve_agreement_identity</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/commit_agreement_metadata/"><code>commit_agreement_metadata</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_ensure_delta_table"><code>_ensure_delta_table</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/create_agreement_form/"><code>create_agreement_form</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="../../reference/agreement_dropdown_options/"><code>agreement_dropdown_options</code></a>, <a class="reference-chip" href="../../reference/load_active_data_steward_profiles/"><code>load_active_data_steward_profiles</code></a>, <a class="reference-chip" href="../../reference/load_agreements/"><code>load_agreements</code></a>, <a class="reference-chip" href="#next_minor_version"><code>next_minor_version</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/get_selected_agreement/"><code>get_selected_agreement</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span>None.</span>
</li>
<li>
<a class="reference-chip" href="../../reference/latest_agreement_versions/"><code>latest_agreement_versions</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>, <a class="reference-chip" href="#parse_contract_version"><code>parse_contract_version</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/load_active_data_steward_profiles/"><code>load_active_data_steward_profiles</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>, <a class="reference-chip" href="#_ensure_delta_table"><code>_ensure_delta_table</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/load_agreements/"><code>load_agreements</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="../../reference/latest_agreement_versions/"><code>latest_agreement_versions</code></a>
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
<a class="reference-chip" href="../../reference/agreement_dropdown_options/"><code>agreement_dropdown_options</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/setup_data_agreement_tables/"><code>setup_data_agreement_tables</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_ensure_delta_table"><code>_ensure_delta_table</code></a>
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
      <td><a href="../../reference/latest_agreement_versions/"><code>latest_agreement_versions</code></a>, <a href="../../reference/load_active_data_steward_profiles/"><code>load_active_data_steward_profiles</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_context_get/"><code>_context_get</code></a></td>
      <td><a href="../../reference/collect_agreement_metadata/"><code>collect_agreement_metadata</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_derive_agreement_status/"><code>_derive_agreement_status</code></a></td>
      <td><a href="../../reference/collect_agreement_metadata/"><code>collect_agreement_metadata</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_ensure_delta_table/"><code>_ensure_delta_table</code></a></td>
      <td><a href="../../reference/commit_agreement_metadata/"><code>commit_agreement_metadata</code></a>, <a href="../../reference/load_active_data_steward_profiles/"><code>load_active_data_steward_profiles</code></a>, <a href="../../reference/setup_data_agreement_tables/"><code>setup_data_agreement_tables</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_generate_agreement_id/"><code>_generate_agreement_id</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_parse_required_date/"><code>_parse_required_date</code></a></td>
      <td>—</td>
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
<a class="reference-chip" href="#_context_get"><code>_context_get</code></a>
</li>
<li>
<a class="reference-chip" href="#_derive_agreement_status"><code>_derive_agreement_status</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_parse_required_date"><code>_parse_required_date</code></a>
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
<a class="reference-chip" href="../metadata/#_runtime_context"><code>_runtime_context</code></a>
