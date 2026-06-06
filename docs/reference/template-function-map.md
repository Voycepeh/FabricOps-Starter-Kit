# Template Function Map

Template-first view of public callables and their main delegated helpers.

## `00_env_config`

Shared environment bootstrap and metadata table setup.

### Environment setup

<table>
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
      <td>`setup_notebook`</td>
      <td>Callable orchestration wrapper</td>
      <td>Shared environment setup and runtime validation for notebook templates.</td>
      <td>`_get_store`, `_run_config_smoke_tests`, `_validate_framework_config`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`setup_data_agreement_tables`</td>
      <td>Callable orchestration wrapper</td>
      <td>Create or validate data-agreement metadata tables during environment setup.</td>
      <td>`_ensure_metadata_tables`, `_list_data_stewards`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`setup_notebook_registry_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Create or validate notebook registry metadata during environment setup.</td>
      <td>`_coerce_row_dicts`, `_column_context_rows_for_spark`, `_column_names`, `_get_notebook_registry_schema`, `_notebook_registration_key`, `_safe_str`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`setup_governance_metadata_tables`</td>
      <td>Callable orchestration wrapper</td>
      <td>Create or validate governance metadata tables during environment setup.</td>
      <td>`_coerce_rows`, `_get_governance_metadata_schemas`, `_is_table_not_found_error`, `_schema_field_names`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

## `01_da_agreement_template`

Agreement, steward, and evidence intake.

### Agreement intake

<table>
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
      <td>`widget_render_agreement_intake_app`</td>
      <td>Callable orchestration wrapper</td>
      <td>Render the combined steward, agreement, and evidence intake app.</td>
      <td>`_render_maintenance_widget`, `_require_ipywidgets`, `_widget_render_agreement_evidence`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

## `02_ex_agreement_topic`

Explore approved agreement data and profile sources.

### Exploration

<table>
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
      <td>`widget_select_agreement`</td>
      <td>Callable orchestration wrapper</td>
      <td>Render an agreement selector and optionally register the active notebook.</td>
      <td>`_current_notebook_active_registrations`, `_html_escape`, `_latest_agreement_versions`, `_load_agreements`, `_refresh_registration_status`, `_register_current_notebook`, `_render_searchable_selector`, `_require_ipywidgets`, `_selected_row`, `_status_message`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`read_lakehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read a table from a configured Fabric lakehouse target.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`read_lakehouse_csv`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read a CSV file from a configured Fabric lakehouse Files path.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`read_lakehouse_parquet`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read a Parquet path from a configured Fabric lakehouse Files path.</td>
      <td>`_convert_single_parquet_ns_to_us`, `_get_spark`, `_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`read_lakehouse_excel`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read an Excel file from a configured Fabric lakehouse Files path.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`read_warehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read a table from a configured Fabric warehouse target.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`profile_dataframe`</td>
      <td>Callable orchestration wrapper</td>
      <td>Profile a source or target DataFrame for schema, quality, and catalogue evidence.</td>
      <td>`_build_distribution_summaries`, `_get_profiled_columns`, `_is_min_max_supported_type`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

## `03_pc_agreement_pipeline_template`

Production pipeline guardrails, IO, lineage, and publishing.

### Pipeline run

<table>
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
      <td>`setup_notebook`</td>
      <td>Callable orchestration wrapper</td>
      <td>Shared environment setup and runtime validation for notebook templates.</td>
      <td>`_get_store`, `_run_config_smoke_tests`, `_validate_framework_config`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`widget_select_agreement`</td>
      <td>Callable orchestration wrapper</td>
      <td>Render an agreement selector and optionally register the active notebook.</td>
      <td>`_current_notebook_active_registrations`, `_html_escape`, `_latest_agreement_versions`, `_load_agreements`, `_refresh_registration_status`, `_register_current_notebook`, `_render_searchable_selector`, `_require_ipywidgets`, `_selected_row`, `_status_message`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`get_selected_agreement`</td>
      <td>Callable orchestration wrapper</td>
      <td>Return the agreement selected by widget_select_agreement.</td>
      <td>—</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`read_lakehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read a table from a configured Fabric lakehouse target.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`read_lakehouse_csv`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read a CSV file from a configured Fabric lakehouse Files path.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`read_lakehouse_parquet`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read a Parquet path from a configured Fabric lakehouse Files path.</td>
      <td>`_convert_single_parquet_ns_to_us`, `_get_spark`, `_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`read_warehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read a table from a configured Fabric warehouse target.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`validate_schema`</td>
      <td>Callable orchestration wrapper</td>
      <td>Validate a DataFrame schema using strict, allow-new-columns, or monitor-only presets.</td>
      <td>`_actual_schema`, `_check_schema`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`monitor_data_changes`</td>
      <td>Callable orchestration wrapper</td>
      <td>Profile data, compare against the approved baseline, and return a drift guardrail result.</td>
      <td>`_as_monitor_only_result`, `_check_profile_drift`, `_data_change_preset_config`, `_extract_categorical_distribution_categories`, `_extract_numeric_distribution_bin_edges`, `_load_latest_profile`, `_normalize_profile`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`stop_if_failed`</td>
      <td>Callable orchestration wrapper</td>
      <td>Stop a notebook when a schema or data-change guardrail result blocks continuation.</td>
      <td>—</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`write_lakehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Write a DataFrame to a configured Fabric lakehouse target.</td>
      <td>`_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`write_warehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Write a DataFrame to a configured Fabric warehouse target.</td>
      <td>`_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`build_lineage_records`</td>
      <td>Callable orchestration wrapper</td>
      <td>Build source-to-target lineage evidence records for a pipeline run.</td>
      <td>—</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

## `04_gov_dataset_table`

Table-scoped governance review and approved metadata recording.

### Governance review

<table>
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
      <td>`widget_select_catalogue_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Render a searchable selector for latest successful catalogue profiles.</td>
      <td>`_catalogue_table_options`, `_coerce_rows`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`get_selected_catalogue_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Return the table selected by widget_select_catalogue_table.</td>
      <td>—</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`load_catalogue_profile_rows`</td>
      <td>Callable orchestration wrapper</td>
      <td>Load column profile rows for the selected catalogue table.</td>
      <td>`_coerce_rows`, `_is_success`, `_row_metadata_table_key`, `_value`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`widget_review_table_governance`</td>
      <td>Callable orchestration wrapper</td>
      <td>Render non-persistent human review guidance for context, DQ rules, and classification.</td>
      <td>`_value`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`record_table_governance`</td>
      <td>Callable orchestration wrapper</td>
      <td>Persist approved table-governance context, DQ-rule, and classification evidence in one v1 commit action.</td>
      <td>`_build_classification_records`, `_build_column_context_records`, `_build_dq_rule_records`, `_commit_column_classification`, `_commit_column_context`, `_commit_dq_rules`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

