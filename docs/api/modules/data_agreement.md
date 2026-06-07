# `data_agreement` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 5</span><span class="reference-chip">Internal helpers: 37</span><span class="reference-chip">Outbound: 3</span><span class="reference-chip">Inbound: 1</span></div>

## Module purpose

Owns agreement metadata capture, audited record building, metadata commit helpers, and agreement selection helpers used to anchor notebook workflows to approved business agreements. Standard notebooks create or check agreement metadata tables in `00_env_config`, render agreement intake in `01_agreement`, and bind downstream work with `widget_select_agreement(...)` and `get_selected_agreement()`.

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
      <td>Owns agreement metadata capture, audited record building, metadata commit helpers, and agreement selection helpers used to anchor notebook workflows to approved business agreements. Standard notebooks create or check agreement metadata tables in `00_env_config`, render agreement intake in `01_agreement`, and bind downstream work with `widget_select_agreement(...)` and `get_selected_agreement()`.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>37</td>
    </tr>
    <tr>
      <td>Inbound module count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>Outbound module count</td>
      <td>3</td>
    </tr>
    <tr>
      <td>External callers</td>
      <td><code>config</code></td>
    </tr>
    <tr>
      <td>External callees</td>
      <td><code>config</code>, <code>fabric_input_output</code>, <code>metadata</code></td>
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
      <td><a href="../../reference/get_selected_agreement/"><code>get_selected_agreement</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Return the agreement selected by widget_select_agreement.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render the standalone agreement-evidence widget.</td>
      <td><a href="../../reference/internal/data_agreement/_render_agreement_evidence_widget/"><code>_render_agreement_evidence_widget</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render the standalone data-agreement intake widget.</td>
      <td><a href="../../reference/internal/data_agreement/_render_maintenance_widget/"><code>_render_maintenance_widget</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render the standalone data-steward intake widget.</td>
      <td><a href="../../reference/internal/data_agreement/_render_maintenance_widget/"><code>_render_maintenance_widget</code></a> (internal)</td>
    </tr>
    <tr>
      <td><a href="../../reference/widget_select_agreement/"><code>widget_select_agreement</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Render an agreement selector and optionally register the active notebook.</td>
      <td><a href="../../reference/internal/data_agreement/_html_escape/"><code>_html_escape</code></a> (internal), <a href="../../reference/internal/data_agreement/_latest_agreement_versions/"><code>_latest_agreement_versions</code></a> (internal), <a href="../../reference/internal/data_agreement/_list_data_agreements/"><code>_list_data_agreements</code></a> (internal), <a href="../../reference/internal/data_agreement/_render_searchable_selector/"><code>_render_searchable_selector</code></a> (internal), <a href="../../reference/internal/data_agreement/_require_ipywidgets/"><code>_require_ipywidgets</code></a> (internal)</td>
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
<a class="reference-chip" href="../../reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_render_agreement_evidence_widget"><code>_render_agreement_evidence_widget</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_render_maintenance_widget"><code>_render_maintenance_widget</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_render_maintenance_widget"><code>_render_maintenance_widget</code></a>
</li>
<li>
<a class="reference-chip" href="../../reference/widget_select_agreement/"><code>widget_select_agreement</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_html_escape"><code>_html_escape</code></a>, <a class="reference-chip" href="#_latest_agreement_versions"><code>_latest_agreement_versions</code></a>, <a class="reference-chip" href="#_list_data_agreements"><code>_list_data_agreements</code></a>, <a class="reference-chip" href="#_render_searchable_selector"><code>_render_searchable_selector</code></a>, <a class="reference-chip" href="#_require_ipywidgets"><code>_require_ipywidgets</code></a>
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
      <td><a href="../../reference/internal/data_agreement/_agreement_identity_text/"><code>_agreement_identity_text</code></a></td>
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
      <td><a href="../../reference/internal/data_agreement/_deserialize_custom_fields/"><code>_deserialize_custom_fields</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_ensure_metadata_tables/"><code>_ensure_metadata_tables</code></a></td>
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
      <td><a href="../../reference/internal/data_agreement/_get_notebookutils/"><code>_get_notebookutils</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_get_widget_visible_fields/"><code>_get_widget_visible_fields</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_html_escape/"><code>_html_escape</code></a></td>
      <td><a href="../../reference/widget_select_agreement/"><code>widget_select_agreement</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_latest_agreement_versions/"><code>_latest_agreement_versions</code></a></td>
      <td><a href="../../reference/widget_select_agreement/"><code>widget_select_agreement</code></a></td>
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
      <td><a href="../../reference/widget_select_agreement/"><code>widget_select_agreement</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_list_data_stewards/"><code>_list_data_stewards</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_next_minor_version/"><code>_next_minor_version</code></a></td>
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
      <td><a href="../../reference/internal/data_agreement/_prepare_evidence_file_references/"><code>_prepare_evidence_file_references</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_render_agreement_evidence_widget/"><code>_render_agreement_evidence_widget</code></a></td>
      <td><a href="../../reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_render_custom_fields/"><code>_render_custom_fields</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_render_maintenance_widget/"><code>_render_maintenance_widget</code></a></td>
      <td><a href="../../reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a href="../../reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_render_searchable_selector/"><code>_render_searchable_selector</code></a></td>
      <td><a href="../../reference/widget_select_agreement/"><code>widget_select_agreement</code></a></td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_require_ipywidgets/"><code>_require_ipywidgets</code></a></td>
      <td><a href="../../reference/widget_select_agreement/"><code>widget_select_agreement</code></a></td>
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
      <td><a href="../../reference/internal/data_agreement/_setup_data_agreement_tables/"><code>_setup_data_agreement_tables</code></a></td>
      <td>—</td>
    </tr>
    <tr>
      <td><a href="../../reference/internal/data_agreement/_standard_widget/"><code>_standard_widget</code></a></td>
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
      <td><a href="../../reference/internal/data_agreement/_widget_common/"><code>_widget_common</code></a></td>
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
<a class="reference-chip" href="#_agreement_identity_text"><code>_agreement_identity_text</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_next_minor_version"><code>_next_minor_version</code></a>
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
<a class="reference-chip" href="#_config_value"><code>_config_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_create_or_update_data_agreement"><code>_create_or_update_data_agreement</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_business_agreement_snapshot"><code>_business_agreement_snapshot</code></a>, <a class="reference-chip" href="#_config_value"><code>_config_value</code></a>, <a class="reference-chip" href="#_generate_agreement_id"><code>_generate_agreement_id</code></a>, <a class="reference-chip" href="#_list_all_data_agreement_rows"><code>_list_all_data_agreement_rows</code></a>, <a class="reference-chip" href="#_list_data_stewards"><code>_list_data_stewards</code></a>, <a class="reference-chip" href="#_next_minor_version"><code>_next_minor_version</code></a>, <a class="reference-chip" href="#_parse_contract_version"><code>_parse_contract_version</code></a>, <a class="reference-chip" href="#_parse_iso_date"><code>_parse_iso_date</code></a>, <a class="reference-chip" href="#_serialize_custom_fields"><code>_serialize_custom_fields</code></a>, <a class="reference-chip" href="#_write_row"><code>_write_row</code></a>
</li>
<li>
<a class="reference-chip" href="#_create_or_update_data_steward"><code>_create_or_update_data_steward</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_active_steward"><code>_active_steward</code></a>, <a class="reference-chip" href="#_config_value"><code>_config_value</code></a>, <a class="reference-chip" href="#_generate_steward_id"><code>_generate_steward_id</code></a>, <a class="reference-chip" href="#_parse_iso_date"><code>_parse_iso_date</code></a>, <a class="reference-chip" href="#_serialize_custom_fields"><code>_serialize_custom_fields</code></a>, <a class="reference-chip" href="#_to_bool"><code>_to_bool</code></a>, <a class="reference-chip" href="#_write_row"><code>_write_row</code></a>
</li>
<li>
<a class="reference-chip" href="#_deserialize_custom_fields"><code>_deserialize_custom_fields</code></a>
</li>
<li>
<a class="reference-chip" href="#_ensure_metadata_tables"><code>_ensure_metadata_tables</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>, <a class="reference-chip" href="#_config_value"><code>_config_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_generate_agreement_id"><code>_generate_agreement_id</code></a>
</li>
<li>
<a class="reference-chip" href="#_generate_steward_id"><code>_generate_steward_id</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_notebookutils"><code>_get_notebookutils</code></a>
</li>
<li>
<a class="reference-chip" href="#_get_widget_visible_fields"><code>_get_widget_visible_fields</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_config_value"><code>_config_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_html_escape"><code>_html_escape</code></a>
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
<a class="reference-chip" href="#_coerce_row_dicts"><code>_coerce_row_dicts</code></a>, <a class="reference-chip" href="#_config_value"><code>_config_value</code></a>
</li>
<li>
<a class="reference-chip" href="#_list_data_agreements"><code>_list_data_agreements</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_latest_agreement_versions"><code>_latest_agreement_versions</code></a>, <a class="reference-chip" href="#_list_all_data_agreement_rows"><code>_list_all_data_agreement_rows</code></a>
</li>
<li>
<a class="reference-chip" href="#_list_data_stewards"><code>_list_data_stewards</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_active_steward"><code>_active_steward</code></a>, <a class="reference-chip" href="#_config_value"><code>_config_value</code></a>, <a class="reference-chip" href="#_latest_by_key"><code>_latest_by_key</code></a>
</li>
<li>
<a class="reference-chip" href="#_next_minor_version"><code>_next_minor_version</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_parse_contract_version"><code>_parse_contract_version</code></a>
</li>
<li>
<a class="reference-chip" href="#_parse_contract_version"><code>_parse_contract_version</code></a>
</li>
<li>
<a class="reference-chip" href="#_parse_iso_date"><code>_parse_iso_date</code></a>
</li>
<li>
<a class="reference-chip" href="#_prepare_evidence_file_references"><code>_prepare_evidence_file_references</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_get_notebookutils"><code>_get_notebookutils</code></a>
</li>
<li>
<a class="reference-chip" href="#_render_agreement_evidence_widget"><code>_render_agreement_evidence_widget</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_list_all_data_agreement_rows"><code>_list_all_data_agreement_rows</code></a>, <a class="reference-chip" href="#_render_searchable_selector"><code>_render_searchable_selector</code></a>, <a class="reference-chip" href="#_require_ipywidgets"><code>_require_ipywidgets</code></a>, <a class="reference-chip" href="#_save_agreement_evidence_records"><code>_save_agreement_evidence_records</code></a>, <a class="reference-chip" href="#_widget_common"><code>_widget_common</code></a>
</li>
<li>
<a class="reference-chip" href="#_render_custom_fields"><code>_render_custom_fields</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_require_ipywidgets"><code>_require_ipywidgets</code></a>, <a class="reference-chip" href="#_to_bool"><code>_to_bool</code></a>, <a class="reference-chip" href="#_widget_common"><code>_widget_common</code></a>
</li>
<li>
<a class="reference-chip" href="#_render_maintenance_widget"><code>_render_maintenance_widget</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_agreement_identity_text"><code>_agreement_identity_text</code></a>, <a class="reference-chip" href="#_collect_custom_fields"><code>_collect_custom_fields</code></a>, <a class="reference-chip" href="#_config_value"><code>_config_value</code></a>, <a class="reference-chip" href="#_create_or_update_data_agreement"><code>_create_or_update_data_agreement</code></a>, <a class="reference-chip" href="#_create_or_update_data_steward"><code>_create_or_update_data_steward</code></a>, <a class="reference-chip" href="#_deserialize_custom_fields"><code>_deserialize_custom_fields</code></a>, <a class="reference-chip" href="#_get_widget_visible_fields"><code>_get_widget_visible_fields</code></a>, <a class="reference-chip" href="#_list_data_agreements"><code>_list_data_agreements</code></a>, <a class="reference-chip" href="#_list_data_stewards"><code>_list_data_stewards</code></a>, <a class="reference-chip" href="#_render_custom_fields"><code>_render_custom_fields</code></a>, <a class="reference-chip" href="#_render_searchable_selector"><code>_render_searchable_selector</code></a>, <a class="reference-chip" href="#_require_ipywidgets"><code>_require_ipywidgets</code></a>, <a class="reference-chip" href="#_standard_widget"><code>_standard_widget</code></a>, <a class="reference-chip" href="#_to_bool"><code>_to_bool</code></a>, <a class="reference-chip" href="#_to_iso_date"><code>_to_iso_date</code></a>
</li>
<li>
<a class="reference-chip" href="#_render_searchable_selector"><code>_render_searchable_selector</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_html_escape"><code>_html_escape</code></a>, <a class="reference-chip" href="#_widget_common"><code>_widget_common</code></a>
</li>
<li>
<a class="reference-chip" href="#_require_ipywidgets"><code>_require_ipywidgets</code></a>
</li>
<li>
<a class="reference-chip" href="#_save_agreement_evidence_records"><code>_save_agreement_evidence_records</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_config_value"><code>_config_value</code></a>, <a class="reference-chip" href="#_prepare_evidence_file_references"><code>_prepare_evidence_file_references</code></a>, <a class="reference-chip" href="#_write_row"><code>_write_row</code></a>
</li>
<li>
<a class="reference-chip" href="#_serialize_custom_fields"><code>_serialize_custom_fields</code></a>
</li>
<li>
<a class="reference-chip" href="#_setup_data_agreement_tables"><code>_setup_data_agreement_tables</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_ensure_metadata_tables"><code>_ensure_metadata_tables</code></a>, <a class="reference-chip" href="#_list_data_stewards"><code>_list_data_stewards</code></a>
</li>
<li>
<a class="reference-chip" href="#_standard_widget"><code>_standard_widget</code></a>
 <span class="callable-relationship-uses">uses:</span>
<a class="reference-chip" href="#_require_ipywidgets"><code>_require_ipywidgets</code></a>, <a class="reference-chip" href="#_to_bool"><code>_to_bool</code></a>, <a class="reference-chip" href="#_widget_common"><code>_widget_common</code></a>
</li>
<li>
<a class="reference-chip" href="#_to_bool"><code>_to_bool</code></a>
</li>
<li>
<a class="reference-chip" href="#_to_iso_date"><code>_to_iso_date</code></a>
</li>
<li>
<a class="reference-chip" href="#_widget_common"><code>_widget_common</code></a>
</li>
<li>
<a class="reference-chip" href="#_write_row"><code>_write_row</code></a>
</li>
</ul>
</details>

### External callers

**config**
<a class="reference-chip" href="../../reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>

### External callees

**fabric_input_output**
<a class="reference-chip" href="../../reference/read_lakehouse_table/"><code>read_lakehouse_table</code></a>, <a class="reference-chip" href="../../reference/write_lakehouse_table/"><code>write_lakehouse_table</code></a>

**metadata**
<a class="reference-chip" href="../metadata/#_build_runtime_audit_fields"><code>_build_runtime_audit_fields</code></a>, <a class="reference-chip" href="../metadata/#_current_notebook_active_registrations"><code>_current_notebook_active_registrations</code></a>, <a class="reference-chip" href="../metadata/#_register_current_notebook"><code>_register_current_notebook</code></a>
