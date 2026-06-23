# `io_core` module (internal)

<div class="api-status-block">
  <span class="api-chip api-chip-internal">Internal-only module</span>
  <div class="api-chip-subtitle">Not intended as a primary user-facing API surface.</div>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 0</span><span class="reference-chip">Internal helpers: 28</span><span class="reference-chip">Uses 1 external module</span><span class="reference-chip">Used by 8 external modules</span></div>

## Module purpose

Owns lower-level Fabric IO implementations shared by package internals.

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
      <td><code>io_core</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns lower-level Fabric IO implementations shared by package internals.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>0</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>28</td>
    </tr>
    <tr>
      <td>Used by external module count</td>
      <td>8</td>
    </tr>
    <tr>
      <td>Uses external module count</td>
      <td>1</td>
    </tr>
    <tr>
      <td>External modules using this module</td>
      <td><code>config</code>, <code>data_agreement</code>, <code>governance_review</code>, <code>guardrails</code>, <code>io</code>, <code>metadata</code>, <code>pipeline</code>, <code>shared</code></td>
    </tr>
    <tr>
      <td>External modules this module uses</td>
      <td><code>config</code></td>
    </tr>
  </tbody>
</table>

## Public callables

No public exports in this module.

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>io_core</h5>
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
      <td><code>_build_warehouse_object_name</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_convert_single_parquet_ns_to_us</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_get_spark</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_join_lakehouse_area_path</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_lakehouse_file_path</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_load_pandas</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_normalize_schema_name</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_normalize_table_name</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_normalize_write_mode</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_read_csv_path</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_read_delta_path</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_read_excel_file</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_read_warehouse_synapsesql</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_require_fabric_connector</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_resolve_lakehouse_file_location</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_resolve_lakehouse_schema</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_resolve_lakehouse_table_identifier</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_resolve_lakehouse_table_location</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_resolve_lakehouse_table_path</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_resolve_target_store</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_resolve_warehouse_table_location</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_validate_dataframe_writer</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_validate_lakehouse_store</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_validate_relative_path</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_validate_select_query</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_validate_warehouse_store</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_write_delta_path</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_write_warehouse_synapsesql</code></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<span class="reference-chip"><code>_build_warehouse_object_name</code></span>
</li>
<li>
<span class="reference-chip"><code>_convert_single_parquet_ns_to_us</code></span>
</li>
<li>
<span class="reference-chip"><code>_get_spark</code></span>
</li>
<li>
<span class="reference-chip"><code>_join_lakehouse_area_path</code></span>
</li>
<li>
<span class="reference-chip"><code>_lakehouse_file_path</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_join_lakehouse_area_path</code></span>, <span class="reference-chip"><code>_validate_relative_path</code></span>
</li>
<li>
<span class="reference-chip"><code>_load_pandas</code></span>
</li>
<li>
<span class="reference-chip"><code>_normalize_schema_name</code></span>
</li>
<li>
<span class="reference-chip"><code>_normalize_table_name</code></span>
</li>
<li>
<span class="reference-chip"><code>_normalize_write_mode</code></span>
</li>
<li>
<span class="reference-chip"><code>_read_csv_path</code></span>
</li>
<li>
<span class="reference-chip"><code>_read_delta_path</code></span>
</li>
<li>
<span class="reference-chip"><code>_read_excel_file</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_load_pandas</code></span>
</li>
<li>
<span class="reference-chip"><code>_read_warehouse_synapsesql</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_require_fabric_connector</code></span>
</li>
<li>
<span class="reference-chip"><code>_require_fabric_connector</code></span>
</li>
<li>
<span class="reference-chip"><code>_resolve_lakehouse_file_location</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_lakehouse_file_path</code></span>, <span class="reference-chip"><code>_validate_relative_path</code></span>
</li>
<li>
<span class="reference-chip"><code>_resolve_lakehouse_schema</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_normalize_schema_name</code></span>
</li>
<li>
<span class="reference-chip"><code>_resolve_lakehouse_table_identifier</code></span>
</li>
<li>
<span class="reference-chip"><code>_resolve_lakehouse_table_location</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_normalize_table_name</code></span>, <span class="reference-chip"><code>_resolve_lakehouse_schema</code></span>, <span class="reference-chip"><code>_resolve_lakehouse_table_path</code></span>
</li>
<li>
<span class="reference-chip"><code>_resolve_lakehouse_table_path</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_join_lakehouse_area_path</code></span>
</li>
<li>
<span class="reference-chip"><code>_resolve_target_store</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_validate_lakehouse_store</code></span>, <span class="reference-chip"><code>_validate_warehouse_store</code></span>
</li>
<li>
<span class="reference-chip"><code>_resolve_warehouse_table_location</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_build_warehouse_object_name</code></span>, <span class="reference-chip"><code>_normalize_schema_name</code></span>, <span class="reference-chip"><code>_normalize_table_name</code></span>
</li>
<li>
<span class="reference-chip"><code>_validate_dataframe_writer</code></span>
</li>
<li>
<span class="reference-chip"><code>_validate_lakehouse_store</code></span>
</li>
<li>
<span class="reference-chip"><code>_validate_relative_path</code></span>
</li>
<li>
<span class="reference-chip"><code>_validate_select_query</code></span>
</li>
<li>
<span class="reference-chip"><code>_validate_warehouse_store</code></span>
</li>
<li>
<span class="reference-chip"><code>_write_delta_path</code></span>
</li>
<li>
<span class="reference-chip"><code>_write_warehouse_synapsesql</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_require_fabric_connector</code></span>
</li>
</ul>
</details>

### External callers

**config**
<a class="reference-chip" href="config/#_setup_metadata_table_registry"><code>_setup_metadata_table_registry</code></a>, <a class="reference-chip" href="config/#_validate_metadata_table_registration"><code>_validate_metadata_table_registration</code></a>

**data_agreement**
<a class="reference-chip" href="data_agreement/#_list_all_data_agreement_rows"><code>_list_all_data_agreement_rows</code></a>, <a class="reference-chip" href="data_agreement/#_list_data_stewards"><code>_list_data_stewards</code></a>, <a class="reference-chip" href="data_agreement/#_write_row"><code>_write_row</code></a>

**governance_review**
<a class="reference-chip" href="governance_review/#_latest_metadata_catalogue_lookup_workflow"><code>_latest_metadata_catalogue_lookup_workflow</code></a>, <a class="reference-chip" href="governance_review/#_read_guardrail_rule_metadata"><code>_read_guardrail_rule_metadata</code></a>, <a class="reference-chip" href="governance_review/#_read_metadata_rows"><code>_read_metadata_rows</code></a>, <a class="reference-chip" href="governance_review/#_read_metadata_table_or_empty"><code>_read_metadata_table_or_empty</code></a>, <a class="reference-chip" href="governance_review/#_write_rule_records"><code>_write_rule_records</code></a>, <a class="reference-chip" href="governance_review/#_write_table_metadata_enrichment_records"><code>_write_table_metadata_enrichment_records</code></a>, <a class="reference-chip" href="governance_review/#load_catalogue_profile_rows"><code>load_catalogue_profile_rows</code></a>, <a class="reference-chip" href="governance_review/#record_table_governance"><code>record_table_governance</code></a>

**guardrails**
<a class="reference-chip" href="guardrails/#enforce_profile_behavior"><code>enforce_profile_behavior</code></a>

**io**
<a class="reference-chip" href="io/#convert_single_parquet_ns_to_us"><code>convert_single_parquet_ns_to_us</code></a>, <a class="reference-chip" href="io/#get_spark_session"><code>get_spark_session</code></a>, <a class="reference-chip" href="io/#normalize_write_mode"><code>normalize_write_mode</code></a>, <a class="reference-chip" href="io/#read_csv_path"><code>read_csv_path</code></a>, <a class="reference-chip" href="io/#read_delta_path"><code>read_delta_path</code></a>, <a class="reference-chip" href="io/#read_excel_file"><code>read_excel_file</code></a>, <a class="reference-chip" href="io/#read_warehouse_synapsesql"><code>read_warehouse_synapsesql</code></a>, <a class="reference-chip" href="io/#resolve_configured_file_path"><code>resolve_configured_file_path</code></a>, <a class="reference-chip" href="io/#resolve_configured_lakehouse_table"><code>resolve_configured_lakehouse_table</code></a>, <a class="reference-chip" href="io/#resolve_configured_warehouse_query_target"><code>resolve_configured_warehouse_query_target</code></a>, <a class="reference-chip" href="io/#resolve_configured_warehouse_table"><code>resolve_configured_warehouse_table</code></a>, <a class="reference-chip" href="io/#resolve_lakehouse_file_location"><code>resolve_lakehouse_file_location</code></a>, <a class="reference-chip" href="io/#resolve_lakehouse_file_path"><code>resolve_lakehouse_file_path</code></a>, <a class="reference-chip" href="io/#resolve_lakehouse_table_location"><code>resolve_lakehouse_table_location</code></a>, <a class="reference-chip" href="io/#resolve_target_store"><code>resolve_target_store</code></a>, <a class="reference-chip" href="io/#resolve_warehouse_table_location"><code>resolve_warehouse_table_location</code></a>, <a class="reference-chip" href="io/#convert_single_parquet_ns_to_us"><code>convert_single_parquet_ns_to_us</code></a>, <a class="reference-chip" href="io/#get_spark_session"><code>get_spark_session</code></a>, <a class="reference-chip" href="io/#normalize_write_mode"><code>normalize_write_mode</code></a>, <a class="reference-chip" href="io/#read_csv_path"><code>read_csv_path</code></a>, <a class="reference-chip" href="io/#read_delta_path"><code>read_delta_path</code></a>, <a class="reference-chip" href="io/#read_excel_file"><code>read_excel_file</code></a>, <a class="reference-chip" href="io/#read_warehouse_synapsesql"><code>read_warehouse_synapsesql</code></a>, <a class="reference-chip" href="io/#resolve_configured_file_path"><code>resolve_configured_file_path</code></a>, <a class="reference-chip" href="io/#resolve_configured_lakehouse_table"><code>resolve_configured_lakehouse_table</code></a>, <a class="reference-chip" href="io/#resolve_configured_warehouse_query_target"><code>resolve_configured_warehouse_query_target</code></a>, <a class="reference-chip" href="io/#resolve_configured_warehouse_table"><code>resolve_configured_warehouse_table</code></a>, <a class="reference-chip" href="io/#resolve_lakehouse_file_location"><code>resolve_lakehouse_file_location</code></a>, <a class="reference-chip" href="io/#resolve_lakehouse_file_path"><code>resolve_lakehouse_file_path</code></a>, <a class="reference-chip" href="io/#resolve_lakehouse_table_location"><code>resolve_lakehouse_table_location</code></a>, <a class="reference-chip" href="io/#resolve_target_store"><code>resolve_target_store</code></a>, <a class="reference-chip" href="io/#resolve_warehouse_table_location"><code>resolve_warehouse_table_location</code></a>, <a class="reference-chip" href="io/#validate_dataframe_writer"><code>validate_dataframe_writer</code></a>, <a class="reference-chip" href="io/#validate_select_query"><code>validate_select_query</code></a>, <a class="reference-chip" href="io/#write_delta_path"><code>write_delta_path</code></a>, <a class="reference-chip" href="io/#write_warehouse_synapsesql"><code>write_warehouse_synapsesql</code></a>, <a class="reference-chip" href="io/#validate_dataframe_writer"><code>validate_dataframe_writer</code></a>, <a class="reference-chip" href="io/#validate_select_query"><code>validate_select_query</code></a>, <a class="reference-chip" href="io/#write_delta_path"><code>write_delta_path</code></a>, <a class="reference-chip" href="io/#write_warehouse_synapsesql"><code>write_warehouse_synapsesql</code></a>

**metadata**
<a class="reference-chip" href="metadata/#_load_notebook_registry"><code>_load_notebook_registry</code></a>, <a class="reference-chip" href="metadata/#_register_current_notebook"><code>_register_current_notebook</code></a>, <a class="reference-chip" href="metadata/#_write_guardrail_result_row"><code>_write_guardrail_result_row</code></a>

**pipeline**
<a class="reference-chip" href="pipeline/#_write_pipeline_lineage_workflow"><code>_write_pipeline_lineage_workflow</code></a>, <a class="reference-chip" href="pipeline/#_write_pipeline_run_summary_workflow"><code>_write_pipeline_run_summary_workflow</code></a>, <a class="reference-chip" href="pipeline/#write_catalogue_evidence"><code>write_catalogue_evidence</code></a>

### External callees

**config**
<a class="reference-chip" href="config/#_get_store"><code>_get_store</code></a>, <a class="reference-chip" href="config/#resolve_fabric_context"><code>resolve_fabric_context</code></a>
