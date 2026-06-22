# `config` module

<div class="api-status-block">
  <span class="api-chip api-chip-module">Module overview</span>
</div>

Implementation modules document source-level behavior and internal helper relationships for maintainers. They support debugging and implementation traceability, but they are not the public v1 callable API.

The public v1 callable API is controlled by `src/fabricops_kit/__init__.py::__all__` and is browsed from the Function Reference catalogue.

## Module overview badges

<div class="module-summary-cards"><span class="reference-chip">Callable count: 2</span><span class="reference-chip">Internal helpers: 21</span><span class="reference-chip">Uses 3 external modules</span><span class="reference-chip">Used by 11 external modules</span></div>

## Module purpose

Owns environment setup, runtime initialization, paths, and notebook-wide configuration.

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
      <td><code>config</code></td>
    </tr>
    <tr>
      <td>Module purpose</td>
      <td>Owns environment setup, runtime initialization, paths, and notebook-wide configuration.</td>
    </tr>
    <tr>
      <td>Public callable count</td>
      <td>2</td>
    </tr>
    <tr>
      <td>Internal helper count</td>
      <td>21</td>
    </tr>
    <tr>
      <td>Used by external module count</td>
      <td>11</td>
    </tr>
    <tr>
      <td>Uses external module count</td>
      <td>3</td>
    </tr>
    <tr>
      <td>External modules using this module</td>
      <td><code>DataAgreementConfig</code>, <code>FrameworkConfig</code>, <code>GovernanceConfig</code>, <code>data_agreement</code>, <code>data_lineage</code>, <code>data_profiling</code>, <code>fabric_input_output</code>, <code>governance_review</code>, <code>io_core</code>, <code>metadata</code>, <code>pipeline</code></td>
    </tr>
    <tr>
      <td>External modules this module uses</td>
      <td><code>data_agreement</code>, <code>governance_review</code>, <code>io_core</code></td>
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
      <td><a href="../reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Create or validate all FabricOps metadata tables through one setup action.</td>
      <td><code>_get_metadata_table_schema_registry</code> (internal), <code>_metadata_schema_field_names</code> (internal), <code>_resolve_metadata_schema</code> (internal), <code>_setup_metadata_table_registry</code> (internal), <code>_validate_framework_config</code> (internal), <code>_validate_metadata_table_registration</code> (internal)</td>
    </tr>
    <tr>
      <td><a href="../reference/setup_notebook/"><code>setup_notebook</code></a></td>
      <td>Callable</td>
      <td>function</td>
      <td>Shared environment setup and runtime validation for notebook templates.</td>
      <td><code>_get_store</code> (internal), <code>_run_config_smoke_tests</code> (internal), <code>_validate_framework_config</code> (internal)</td>
    </tr>
  </tbody>
</table>
</div>

## Module relationships


### Callable relationships


#### Inside this module

<section class="callable-relationship-card">
<h5>config</h5>
<h6>Public callables</h6>
<ul class="callable-relationship-rows">
<li>
<a class="reference-chip" href="../reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_get_metadata_table_schema_registry</code></span>, <span class="reference-chip"><code>_metadata_schema_field_names</code></span>, <span class="reference-chip"><code>_resolve_metadata_schema</code></span>, <span class="reference-chip"><code>_setup_metadata_table_registry</code></span>, <span class="reference-chip"><code>_validate_framework_config</code></span>, <span class="reference-chip"><code>_validate_metadata_table_registration</code></span>
</li>
<li>
<a class="reference-chip" href="../reference/setup_notebook/"><code>setup_notebook</code></a>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_get_store</code></span>, <span class="reference-chip"><code>_run_config_smoke_tests</code></span>, <span class="reference-chip"><code>_validate_framework_config</code></span>
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
      <td><code>_audit_timestamp_expr</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_check_spark_session</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_coerce_row_dicts</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_current_audit_timestamp</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_detect_nested_metadata_delta_folders</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_get_active_metadata_tables</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_get_audit_timezone</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_get_fabric_runtime_metadata</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_get_metadata_table_schema_registry</code></td>
      <td><a href="../reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
    </tr>
    <tr>
      <td><code>_get_store</code></td>
      <td><a href="../reference/setup_notebook/"><code>setup_notebook</code></a></td>
    </tr>
    <tr>
      <td><code>_metadata_schema_field_names</code></td>
      <td><a href="../reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
    </tr>
    <tr>
      <td><code>_normalize_path_config</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_normalize_widget_config</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_resolve_metadata_schema</code></td>
      <td><a href="../reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
    </tr>
    <tr>
      <td><code>_run_config_smoke_tests</code></td>
      <td><a href="../reference/setup_notebook/"><code>setup_notebook</code></a></td>
    </tr>
    <tr>
      <td><code>_setup_metadata_table_registry</code></td>
      <td><a href="../reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
    </tr>
    <tr>
      <td><code>_string_metadata_schema</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_validate_audit_timezone</code></td>
      <td>—</td>
    </tr>
    <tr>
      <td><code>_validate_framework_config</code></td>
      <td><a href="../reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a>, <a href="../reference/setup_notebook/"><code>setup_notebook</code></a></td>
    </tr>
    <tr>
      <td><code>_validate_metadata_table_registration</code></td>
      <td><a href="../reference/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
    </tr>
    <tr>
      <td><code>_validate_notebook_name</code></td>
      <td>—</td>
    </tr>
  </tbody>
</table>
</div>

<h6>Internal helpers details</h6>
<ul class="callable-relationship-rows">
<li>
<span class="reference-chip"><code>_audit_timestamp_expr</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_get_audit_timezone</code></span>
</li>
<li>
<span class="reference-chip"><code>_check_spark_session</code></span>
</li>
<li>
<span class="reference-chip"><code>_coerce_row_dicts</code></span>
</li>
<li>
<span class="reference-chip"><code>_current_audit_timestamp</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_get_audit_timezone</code></span>
</li>
<li>
<span class="reference-chip"><code>_detect_nested_metadata_delta_folders</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_get_store</code></span>
</li>
<li>
<span class="reference-chip"><code>_get_active_metadata_tables</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_validate_framework_config</code></span>
</li>
<li>
<span class="reference-chip"><code>_get_audit_timezone</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_validate_audit_timezone</code></span>
</li>
<li>
<span class="reference-chip"><code>_get_fabric_runtime_metadata</code></span>
</li>
<li>
<span class="reference-chip"><code>_get_metadata_table_schema_registry</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_string_metadata_schema</code></span>, <span class="reference-chip"><code>_validate_framework_config</code></span>
</li>
<li>
<span class="reference-chip"><code>_get_store</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_normalize_path_config</code></span>
</li>
<li>
<span class="reference-chip"><code>_metadata_schema_field_names</code></span>
</li>
<li>
<span class="reference-chip"><code>_normalize_path_config</code></span>
</li>
<li>
<span class="reference-chip"><code>_normalize_widget_config</code></span>
</li>
<li>
<span class="reference-chip"><code>_resolve_metadata_schema</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_get_store</code></span>
</li>
<li>
<span class="reference-chip"><code>_run_config_smoke_tests</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_check_spark_session</code></span>, <span class="reference-chip"><code>_get_fabric_runtime_metadata</code></span>, <span class="reference-chip"><code>_get_store</code></span>, <span class="reference-chip"><code>_validate_notebook_name</code></span>
</li>
<li>
<span class="reference-chip"><code>_setup_metadata_table_registry</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_coerce_row_dicts</code></span>, <span class="reference-chip"><code>_metadata_schema_field_names</code></span>
</li>
<li>
<span class="reference-chip"><code>_string_metadata_schema</code></span>
</li>
<li>
<span class="reference-chip"><code>_validate_audit_timezone</code></span>
</li>
<li>
<span class="reference-chip"><code>_validate_framework_config</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_validate_audit_timezone</code></span>
</li>
<li>
<span class="reference-chip"><code>_validate_metadata_table_registration</code></span>
 <span class="callable-relationship-uses">uses:</span>
<span class="reference-chip"><code>_detect_nested_metadata_delta_folders</code></span>, <span class="reference-chip"><code>_get_active_metadata_tables</code></span>, <span class="reference-chip"><code>_get_store</code></span>, <span class="reference-chip"><code>_resolve_metadata_schema</code></span>, <span class="reference-chip"><code>_validate_framework_config</code></span>
</li>
<li>
<span class="reference-chip"><code>_validate_notebook_name</code></span>
</li>
</ul>
</details>

### External callers

**data_agreement**
<a class="reference-chip" href="../reference/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a>, <a class="reference-chip" href="../reference/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a>, <a class="reference-chip" href="../reference/widget_render_data_steward/"><code>widget_render_data_steward</code></a>, <a class="reference-chip" href="data_agreement/#widget_select_agreement"><code>widget_select_agreement</code></a>

**data_lineage**
<a class="reference-chip" href="data_lineage/#_build_lineage_records"><code>_build_lineage_records</code></a>

**data_profiling**
<a class="reference-chip" href="data_profiling/#profile_dataframe_core"><code>profile_dataframe_core</code></a>

**fabric_input_output**
<a class="reference-chip" href="fabric_input_output/#_read_lakehouse_csv_core"><code>_read_lakehouse_csv_core</code></a>, <a class="reference-chip" href="fabric_input_output/#_read_lakehouse_excel_core"><code>_read_lakehouse_excel_core</code></a>, <a class="reference-chip" href="fabric_input_output/#_read_lakehouse_parquet_core"><code>_read_lakehouse_parquet_core</code></a>, <a class="reference-chip" href="fabric_input_output/#_read_lakehouse_table_core"><code>_read_lakehouse_table_core</code></a>, <a class="reference-chip" href="fabric_input_output/#_read_warehouse_query_core"><code>_read_warehouse_query_core</code></a>, <a class="reference-chip" href="fabric_input_output/#_read_warehouse_table_core"><code>_read_warehouse_table_core</code></a>, <a class="reference-chip" href="fabric_input_output/#_write_lakehouse_table_core"><code>_write_lakehouse_table_core</code></a>, <a class="reference-chip" href="fabric_input_output/#_write_warehouse_table_core"><code>_write_warehouse_table_core</code></a>

**governance_review**
<a class="reference-chip" href="governance_review/#_dq_summary"><code>_dq_summary</code></a>, <a class="reference-chip" href="governance_review/#_prepare_dq_profile_input_rows"><code>_prepare_dq_profile_input_rows</code></a>, <a class="reference-chip" href="../reference/get_latest_metadata_catalogue/"><code>get_latest_metadata_catalogue</code></a>, <a class="reference-chip" href="../reference/widget_author_dq_rules/"><code>widget_author_dq_rules</code></a>, <a class="reference-chip" href="../reference/widget_author_schema_freshness_profile_rules/"><code>widget_author_schema_freshness_profile_rules</code></a>, <a class="reference-chip" href="../reference/widget_enrich_table_metadata/"><code>widget_enrich_table_metadata</code></a>, <a class="reference-chip" href="../reference/widget_review_guardrail_governance/"><code>widget_review_guardrail_governance</code></a>, <a class="reference-chip" href="../reference/widget_select_guardrail_target/"><code>widget_select_guardrail_target</code></a>

**io_core**
<a class="reference-chip" href="io_core/#configured_lakehouse_schema"><code>configured_lakehouse_schema</code></a>

**metadata**
<a class="reference-chip" href="metadata/#_build_runtime_audit_fields"><code>_build_runtime_audit_fields</code></a>, <a class="reference-chip" href="metadata/#_now_utc_iso"><code>_now_utc_iso</code></a>, <a class="reference-chip" href="metadata/#_register_current_notebook"><code>_register_current_notebook</code></a>

**pipeline**
<a class="reference-chip" href="pipeline/#_add_audit_columns"><code>_add_audit_columns</code></a>, <a class="reference-chip" href="pipeline/#_now_iso"><code>_now_iso</code></a>, <a class="reference-chip" href="../reference/run_table_guardrails/"><code>run_table_guardrails</code></a>, <a class="reference-chip" href="../reference/write_pipeline_lineage/"><code>write_pipeline_lineage</code></a>, <a class="reference-chip" href="../reference/write_pipeline_run_summary/"><code>write_pipeline_run_summary</code></a>

### External callees

**data_agreement**
<a class="reference-chip" href="data_agreement/#_list_data_stewards"><code>_list_data_stewards</code></a>

**governance_review**
<a class="reference-chip" href="governance_review/#_get_governance_metadata_schemas"><code>_get_governance_metadata_schemas</code></a>, <a class="reference-chip" href="governance_review/#_is_table_not_found_error"><code>_is_table_not_found_error</code></a>
