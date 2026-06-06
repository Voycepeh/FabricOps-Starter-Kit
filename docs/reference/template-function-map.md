# Template Function Map

Template-first view of public callables and their main delegated helpers.

## `00_env_config`

Shared environment bootstrap and metadata table setup.

### Environment setup

<table class="reference-template-table">
  <thead>
    <tr>
      <th>Function</th>
      <th>Role</th>
      <th>What it does</th>
      <th>Delegates to</th>
      <th>Debug when</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/setup_notebook/"><code>setup_notebook</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Shared environment setup and runtime validation for notebook templates.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/config/_get_store/"><code>_get_store</code></a><a class="function-chip" href="../internal/config/_run_config_smoke_tests/"><code>_run_config_smoke_tests</code></a><a class="function-chip" href="../internal/config/_validate_framework_config/"><code>_validate_framework_config</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/setup_metadata_tables/"><code>setup_metadata_tables</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Create or validate all FabricOps metadata tables through one setup action.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/data_agreement/_setup_data_agreement_tables/"><code>_setup_data_agreement_tables</code></a><a class="function-chip" href="../internal/governance_review/_setup_governance_metadata_tables/"><code>_setup_governance_metadata_tables</code></a><a class="function-chip" href="../internal/metadata/_setup_notebook_registry_table/"><code>_setup_notebook_registry_table</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

## `01_da_agreement_template`

Standalone steward, agreement, and evidence widgets for Fabric stability.

### Agreement intake

<table class="reference-template-table">
  <thead>
    <tr>
      <th>Function</th>
      <th>Role</th>
      <th>What it does</th>
      <th>Delegates to</th>
      <th>Debug when</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/widget_render_data_steward/"><code>widget_render_data_steward</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Render the standalone data-steward intake widget.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/data_agreement/_render_maintenance_widget/"><code>_render_maintenance_widget</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/widget_render_data_agreement/"><code>widget_render_data_agreement</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Render the standalone data-agreement intake widget.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/data_agreement/_render_maintenance_widget/"><code>_render_maintenance_widget</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/widget_render_agreement_evidence/"><code>widget_render_agreement_evidence</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Render the standalone agreement-evidence widget.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/data_agreement/_render_agreement_evidence_widget/"><code>_render_agreement_evidence_widget</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

## `02_ex_agreement_topic`

Explore approved agreement data and profile sources.

### Exploration

<table class="reference-template-table">
  <thead>
    <tr>
      <th>Function</th>
      <th>Role</th>
      <th>What it does</th>
      <th>Delegates to</th>
      <th>Debug when</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/widget_select_agreement/"><code>widget_select_agreement</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Render an agreement selector and optionally register the active notebook.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/metadata/_current_notebook_active_registrations/"><code>_current_notebook_active_registrations</code></a><a class="function-chip" href="../internal/data_agreement/_html_escape/"><code>_html_escape</code></a><a class="function-chip" href="../internal/data_agreement/_latest_agreement_versions/"><code>_latest_agreement_versions</code></a><a class="function-chip" href="../internal/data_agreement/_list_data_agreements/"><code>_list_data_agreements</code></a><a class="function-chip" href="../internal/metadata/_register_current_notebook/"><code>_register_current_notebook</code></a><a class="function-chip" href="../internal/data_agreement/_render_searchable_selector/"><code>_render_searchable_selector</code></a><a class="function-chip" href="../internal/data_agreement/_require_ipywidgets/"><code>_require_ipywidgets</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_lakehouse_table/"><code>read_lakehouse_table</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read a table from a configured Fabric lakehouse target.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a><a class="function-chip" href="../internal/config/_get_store/"><code>_get_store</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read a CSV file from a configured Fabric lakehouse Files path.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a><a class="function-chip" href="../internal/config/_get_store/"><code>_get_store</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read a Parquet path from a configured Fabric lakehouse Files path.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_convert_single_parquet_ns_to_us/"><code>_convert_single_parquet_ns_to_us</code></a><a class="function-chip" href="../internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a><a class="function-chip" href="../internal/config/_get_store/"><code>_get_store</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read an Excel file from a configured Fabric lakehouse Files path.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a><a class="function-chip" href="../internal/config/_get_store/"><code>_get_store</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_warehouse_table/"><code>read_warehouse_table</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read a table from a configured Fabric warehouse target.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a><a class="function-chip" href="../internal/config/_get_store/"><code>_get_store</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/profile_dataframe/"><code>profile_dataframe</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Profile a source or target DataFrame for schema, quality, and catalogue evidence.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/data_profiling/_build_distribution_summaries/"><code>_build_distribution_summaries</code></a><a class="function-chip" href="../internal/data_profiling/_get_profiled_columns/"><code>_get_profiled_columns</code></a><a class="function-chip" href="../internal/data_profiling/_is_min_max_supported_type/"><code>_is_min_max_supported_type</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

## `03_pc_agreement_pipeline_template`

Production pipeline guardrails, IO, lineage, and publishing.

### Pipeline run

<table class="reference-template-table">
  <thead>
    <tr>
      <th>Function</th>
      <th>Role</th>
      <th>What it does</th>
      <th>Delegates to</th>
      <th>Debug when</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/widget_select_agreement/"><code>widget_select_agreement</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Render an agreement selector and optionally register the active notebook.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/metadata/_current_notebook_active_registrations/"><code>_current_notebook_active_registrations</code></a><a class="function-chip" href="../internal/data_agreement/_html_escape/"><code>_html_escape</code></a><a class="function-chip" href="../internal/data_agreement/_latest_agreement_versions/"><code>_latest_agreement_versions</code></a><a class="function-chip" href="../internal/data_agreement/_list_data_agreements/"><code>_list_data_agreements</code></a><a class="function-chip" href="../internal/metadata/_register_current_notebook/"><code>_register_current_notebook</code></a><a class="function-chip" href="../internal/data_agreement/_render_searchable_selector/"><code>_render_searchable_selector</code></a><a class="function-chip" href="../internal/data_agreement/_require_ipywidgets/"><code>_require_ipywidgets</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/get_selected_agreement/"><code>get_selected_agreement</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Return the agreement selected by widget_select_agreement.</td>
      <td data-label="Delegates to">—</td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_lakehouse_table/"><code>read_lakehouse_table</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read a table from a configured Fabric lakehouse target.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a><a class="function-chip" href="../internal/config/_get_store/"><code>_get_store</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_lakehouse_csv/"><code>read_lakehouse_csv</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read a CSV file from a configured Fabric lakehouse Files path.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a><a class="function-chip" href="../internal/config/_get_store/"><code>_get_store</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_lakehouse_parquet/"><code>read_lakehouse_parquet</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read a Parquet path from a configured Fabric lakehouse Files path.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_convert_single_parquet_ns_to_us/"><code>_convert_single_parquet_ns_to_us</code></a><a class="function-chip" href="../internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a><a class="function-chip" href="../internal/config/_get_store/"><code>_get_store</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_lakehouse_excel/"><code>read_lakehouse_excel</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read an Excel file from a configured Fabric lakehouse Files path.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a><a class="function-chip" href="../internal/config/_get_store/"><code>_get_store</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_warehouse_table/"><code>read_warehouse_table</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read a table from a configured Fabric warehouse target.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_get_spark/"><code>_get_spark</code></a><a class="function-chip" href="../internal/config/_get_store/"><code>_get_store</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/validate_schema/"><code>validate_schema</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/drift/_actual_schema/"><code>_actual_schema</code></a><a class="function-chip" href="../internal/drift/_normalize_datatype/"><code>_normalize_datatype</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/monitor_data_changes/"><code>monitor_data_changes</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Profile data, compare against the approved baseline, and return a drift guardrail result.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/drift/_check_profile_drift/"><code>_check_profile_drift</code></a><a class="function-chip" href="../internal/drift/_data_change_preset_config/"><code>_data_change_preset_config</code></a><a class="function-chip" href="../internal/drift/_extract_categorical_distribution_categories/"><code>_extract_categorical_distribution_categories</code></a><a class="function-chip" href="../internal/drift/_extract_numeric_distribution_bin_edges/"><code>_extract_numeric_distribution_bin_edges</code></a><a class="function-chip" href="../internal/drift/_load_latest_profile/"><code>_load_latest_profile</code></a><a class="function-chip" href="../internal/drift/_normalize_profile/"><code>_normalize_profile</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/stop_if_failed/"><code>stop_if_failed</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Stop a notebook only when a schema or data-change guardrail result blocks continuation.</td>
      <td data-label="Delegates to">—</td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/write_lakehouse_table/"><code>write_lakehouse_table</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Write a DataFrame to a configured Fabric lakehouse target.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/config/_get_store/"><code>_get_store</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/write_warehouse_table/"><code>write_warehouse_table</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Write a DataFrame to a configured Fabric warehouse target.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/config/_get_store/"><code>_get_store</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/build_lineage_records/"><code>build_lineage_records</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Build source-to-target lineage evidence records for a pipeline run.</td>
      <td data-label="Delegates to">—</td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

## `04_gov_dataset_table`

Table-scoped governance review and approved metadata recording.

### Governance review

<table class="reference-template-table">
  <thead>
    <tr>
      <th>Function</th>
      <th>Role</th>
      <th>What it does</th>
      <th>Delegates to</th>
      <th>Debug when</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/widget_select_catalogue_table/"><code>widget_select_catalogue_table</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Render a searchable selector for latest successful catalogue profiles.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/governance_review/_catalogue_table_options/"><code>_catalogue_table_options</code></a><a class="function-chip" href="../internal/governance_review/_coerce_rows/"><code>_coerce_rows</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/get_selected_catalogue_table/"><code>get_selected_catalogue_table</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Return the table selected by widget_select_catalogue_table.</td>
      <td data-label="Delegates to">—</td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/load_catalogue_profile_rows/"><code>load_catalogue_profile_rows</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Load column profile rows for the selected catalogue table.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/metadata/_build_metadata_table_key/"><code>_build_metadata_table_key</code></a><a class="function-chip" href="../internal/governance_review/_coerce_rows/"><code>_coerce_rows</code></a><a class="function-chip" href="../internal/governance_review/_is_success/"><code>_is_success</code></a><a class="function-chip" href="../internal/governance_review/_value/"><code>_value</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/widget_review_column_context/"><code>widget_review_column_context</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Render standalone business-context review guidance for selected profile rows.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/governance_review/_display_review_guidance/"><code>_display_review_guidance</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/widget_review_dq_rules/"><code>widget_review_dq_rules</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Render standalone DQ-rule review guidance for selected profile rows.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/governance_review/_display_review_guidance/"><code>_display_review_guidance</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/widget_review_column_classification/"><code>widget_review_column_classification</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Render standalone sensitivity and PII classification review guidance for selected profile rows.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/governance_review/_display_review_guidance/"><code>_display_review_guidance</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/record_table_governance/"><code>record_table_governance</code></a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Persist approved table-governance context, DQ-rule, and classification evidence in one v1 commit action.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/governance_review/_build_classification_records/"><code>_build_classification_records</code></a><a class="function-chip" href="../internal/governance_review/_build_column_context_records/"><code>_build_column_context_records</code></a><a class="function-chip" href="../internal/governance_review/_build_dq_rule_records/"><code>_build_dq_rule_records</code></a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

