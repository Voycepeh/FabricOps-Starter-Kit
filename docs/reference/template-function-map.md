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
      <td data-label="Function"><a class="function-chip" href="../callables/setup_notebook/">setup_notebook</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Shared environment setup and runtime validation for notebook templates.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/config/_get_store/">_get_store</a><a class="function-chip" href="../internal/config/_run_config_smoke_tests/">_run_config_smoke_tests</a><a class="function-chip" href="../internal/config/_validate_framework_config/">_validate_framework_config</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/setup_metadata_tables/">setup_metadata_tables</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Create or validate all FabricOps metadata tables through one setup action.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/data_agreement/_setup_data_agreement_tables/">_setup_data_agreement_tables</a><a class="function-chip" href="../internal/governance_review/_setup_governance_metadata_tables/">_setup_governance_metadata_tables</a><a class="function-chip" href="../internal/metadata/_setup_notebook_registry_table/">_setup_notebook_registry_table</a></span></td>
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
      <td data-label="Function"><a class="function-chip" href="../callables/widget_render_data_steward/">widget_render_data_steward</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Render the standalone data-steward intake widget.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/data_agreement/_render_maintenance_widget/">_render_maintenance_widget</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/widget_render_data_agreement/">widget_render_data_agreement</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Render the standalone data-agreement intake widget.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/data_agreement/_render_maintenance_widget/">_render_maintenance_widget</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/widget_render_agreement_evidence/">widget_render_agreement_evidence</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Render the standalone agreement-evidence widget.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/data_agreement/_render_agreement_evidence_widget/">_render_agreement_evidence_widget</a></span></td>
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
      <td data-label="Function"><a class="function-chip" href="../callables/widget_select_agreement/">widget_select_agreement</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Render an agreement selector and optionally register the active notebook.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/metadata/_current_notebook_active_registrations/">_current_notebook_active_registrations</a><a class="function-chip" href="../internal/data_agreement/_html_escape/">_html_escape</a><a class="function-chip" href="../internal/data_agreement/_latest_agreement_versions/">_latest_agreement_versions</a><a class="function-chip" href="../internal/data_agreement/_list_data_agreements/">_list_data_agreements</a><a class="function-chip" href="../internal/metadata/_register_current_notebook/">_register_current_notebook</a><a class="function-chip" href="../internal/data_agreement/_render_searchable_selector/">_render_searchable_selector</a><a class="function-chip" href="../internal/data_agreement/_require_ipywidgets/">_require_ipywidgets</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_lakehouse_table/">read_lakehouse_table</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read a table from a configured Fabric lakehouse target.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_get_spark/">_get_spark</a><a class="function-chip" href="../internal/config/_get_store/">_get_store</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_lakehouse_csv/">read_lakehouse_csv</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read a CSV file from a configured Fabric lakehouse Files path.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_get_spark/">_get_spark</a><a class="function-chip" href="../internal/config/_get_store/">_get_store</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_lakehouse_parquet/">read_lakehouse_parquet</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read a Parquet path from a configured Fabric lakehouse Files path.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_convert_single_parquet_ns_to_us/">_convert_single_parquet_ns_to_us</a><a class="function-chip" href="../internal/fabric_input_output/_get_spark/">_get_spark</a><a class="function-chip" href="../internal/config/_get_store/">_get_store</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_lakehouse_excel/">read_lakehouse_excel</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read an Excel file from a configured Fabric lakehouse Files path.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_get_spark/">_get_spark</a><a class="function-chip" href="../internal/config/_get_store/">_get_store</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_warehouse_table/">read_warehouse_table</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read a table from a configured Fabric warehouse target.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_get_spark/">_get_spark</a><a class="function-chip" href="../internal/config/_get_store/">_get_store</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/profile_dataframe/">profile_dataframe</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Profile a source or target DataFrame for schema, quality, and catalogue evidence.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/data_profiling/_build_distribution_summaries/">_build_distribution_summaries</a><a class="function-chip" href="../internal/data_profiling/_get_profiled_columns/">_get_profiled_columns</a><a class="function-chip" href="../internal/data_profiling/_is_min_max_supported_type/">_is_min_max_supported_type</a></span></td>
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
      <td data-label="Function"><a class="function-chip" href="../callables/widget_select_agreement/">widget_select_agreement</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Render an agreement selector and optionally register the active notebook.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/metadata/_current_notebook_active_registrations/">_current_notebook_active_registrations</a><a class="function-chip" href="../internal/data_agreement/_html_escape/">_html_escape</a><a class="function-chip" href="../internal/data_agreement/_latest_agreement_versions/">_latest_agreement_versions</a><a class="function-chip" href="../internal/data_agreement/_list_data_agreements/">_list_data_agreements</a><a class="function-chip" href="../internal/metadata/_register_current_notebook/">_register_current_notebook</a><a class="function-chip" href="../internal/data_agreement/_render_searchable_selector/">_render_searchable_selector</a><a class="function-chip" href="../internal/data_agreement/_require_ipywidgets/">_require_ipywidgets</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/get_selected_agreement/">get_selected_agreement</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Return the agreement selected by widget_select_agreement.</td>
      <td data-label="Delegates to">—</td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_lakehouse_table/">read_lakehouse_table</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read a table from a configured Fabric lakehouse target.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_get_spark/">_get_spark</a><a class="function-chip" href="../internal/config/_get_store/">_get_store</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_lakehouse_csv/">read_lakehouse_csv</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read a CSV file from a configured Fabric lakehouse Files path.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_get_spark/">_get_spark</a><a class="function-chip" href="../internal/config/_get_store/">_get_store</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_lakehouse_parquet/">read_lakehouse_parquet</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read a Parquet path from a configured Fabric lakehouse Files path.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_convert_single_parquet_ns_to_us/">_convert_single_parquet_ns_to_us</a><a class="function-chip" href="../internal/fabric_input_output/_get_spark/">_get_spark</a><a class="function-chip" href="../internal/config/_get_store/">_get_store</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_lakehouse_excel/">read_lakehouse_excel</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read an Excel file from a configured Fabric lakehouse Files path.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_get_spark/">_get_spark</a><a class="function-chip" href="../internal/config/_get_store/">_get_store</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/read_warehouse_table/">read_warehouse_table</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Read a table from a configured Fabric warehouse target.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/fabric_input_output/_get_spark/">_get_spark</a><a class="function-chip" href="../internal/config/_get_store/">_get_store</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/validate_schema/">validate_schema</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/drift/_actual_schema/">_actual_schema</a><a class="function-chip" href="../internal/drift/_normalize_datatype/">_normalize_datatype</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/monitor_data_changes/">monitor_data_changes</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Profile data, compare against the approved baseline, and return a drift guardrail result.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/drift/_check_profile_drift/">_check_profile_drift</a><a class="function-chip" href="../internal/drift/_data_change_preset_config/">_data_change_preset_config</a><a class="function-chip" href="../internal/drift/_extract_categorical_distribution_categories/">_extract_categorical_distribution_categories</a><a class="function-chip" href="../internal/drift/_extract_numeric_distribution_bin_edges/">_extract_numeric_distribution_bin_edges</a><a class="function-chip" href="../internal/drift/_load_latest_profile/">_load_latest_profile</a><a class="function-chip" href="../internal/drift/_normalize_profile/">_normalize_profile</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/stop_if_failed/">stop_if_failed</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Stop a notebook only when a schema or data-change guardrail result blocks continuation.</td>
      <td data-label="Delegates to">—</td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/write_lakehouse_table/">write_lakehouse_table</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Write a DataFrame to a configured Fabric lakehouse target.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/config/_get_store/">_get_store</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/write_warehouse_table/">write_warehouse_table</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Write a DataFrame to a configured Fabric warehouse target.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/config/_get_store/">_get_store</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/build_lineage_records/">build_lineage_records</a></td>
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
      <td data-label="Function"><a class="function-chip" href="../callables/widget_select_catalogue_table/">widget_select_catalogue_table</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Render a searchable selector for latest successful catalogue profiles.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/governance_review/_catalogue_table_options/">_catalogue_table_options</a><a class="function-chip" href="../internal/governance_review/_coerce_rows/">_coerce_rows</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/get_selected_catalogue_table/">get_selected_catalogue_table</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Return the table selected by widget_select_catalogue_table.</td>
      <td data-label="Delegates to">—</td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/load_catalogue_profile_rows/">load_catalogue_profile_rows</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Load column profile rows for the selected catalogue table.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/metadata/_build_metadata_table_key/">_build_metadata_table_key</a><a class="function-chip" href="../internal/governance_review/_coerce_rows/">_coerce_rows</a><a class="function-chip" href="../internal/governance_review/_is_success/">_is_success</a><a class="function-chip" href="../internal/governance_review/_value/">_value</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/widget_review_column_context/">widget_review_column_context</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Render standalone business-context review guidance for selected profile rows.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/governance_review/_display_review_guidance/">_display_review_guidance</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/widget_review_dq_rules/">widget_review_dq_rules</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Render standalone DQ-rule review guidance for selected profile rows.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/governance_review/_display_review_guidance/">_display_review_guidance</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/widget_review_column_classification/">widget_review_column_classification</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Render standalone sensitivity and PII classification review guidance for selected profile rows.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/governance_review/_display_review_guidance/">_display_review_guidance</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td data-label="Function"><a class="function-chip" href="../callables/record_table_governance/">record_table_governance</a></td>
      <td data-label="Role">Callable orchestration wrapper</td>
      <td data-label="What it does">Persist approved table-governance context, DQ-rule, and classification evidence in one v1 commit action.</td>
      <td data-label="Delegates to"><span class="function-chip-wrap"><a class="function-chip" href="../internal/governance_review/_build_classification_records/">_build_classification_records</a><a class="function-chip" href="../internal/governance_review/_build_column_context_records/">_build_column_context_records</a><a class="function-chip" href="../internal/governance_review/_build_dq_rule_records/">_build_dq_rule_records</a></span></td>
      <td data-label="Debug when">Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

