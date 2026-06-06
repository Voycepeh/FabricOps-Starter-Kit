# Template Function Map

Template-first view of public callables and their main delegated helpers.

## `00_env_config`

Shared environment bootstrap and validation before agreement intake, exploration, or pipeline notebooks run.

### Segment 1: Explain the shared environment role

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
      <td>`print_runtime_banner`</td>
      <td>Callable orchestration wrapper</td>
      <td>Print the installed package version and matching documentation links in a notebook-friendly banner.</td>
      <td>—</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

### Segment 2: Define environment targets and notebook policy

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
      <td>`FabricStore`</td>
      <td>Callable orchestration wrapper</td>
      <td>Fabric lakehouse or warehouse connection details.</td>
      <td>—</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

### Segment 5: Run startup checks and show resolved paths

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
      <td>Run consolidated FabricOps startup for exploration and pipeline notebooks.</td>
      <td>`_get_store`, `_run_config_smoke_tests`, `_validate_framework_config`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

## `01_da_<agreement>`

Form notebook that supports two agreement-intake layouts for A/B testing. Option A renders a compact section switcher through `widget_render_agreement_intake_app(...)`. Option B renders separate widget cells for Data Steward, Data Agreement, and Agreement Evidence through `widget_render_data_steward(...)`, `widget_render_data_agreement(...)`, and `widget_render_agreement_evidence(...)`. Both layouts write append-only metadata and agreement intake selects active steward rows.

### Segment 1: Option A compact app

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
      <td>Render and wire the compact agreement-intake section switcher application.</td>
      <td>`_render_maintenance_widget`, `_require_ipywidgets`, `_widget_render_agreement_evidence`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

### Segment 2: Option B separate widgets

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
      <td>`widget_render_data_steward`</td>
      <td>Callable orchestration wrapper</td>
      <td>Render append-only data steward maintenance.</td>
      <td>`_render_maintenance_widget`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`widget_render_data_agreement`</td>
      <td>Callable orchestration wrapper</td>
      <td>Render append-only agreement maintenance using active steward rows.</td>
      <td>`_render_maintenance_widget`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`widget_render_agreement_evidence`</td>
      <td>Callable orchestration wrapper</td>
      <td>Render standalone agreement evidence upload controls for an existing agreement version.</td>
      <td>`_widget_render_agreement_evidence`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

## `02_ex_<agreement>_<topic>`

Exploration notebook flow used to profile source data and draft advisory AI outputs for human review.

### Segment 1: Load shared config and runtime

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
      <td>Run consolidated FabricOps startup for exploration and pipeline notebooks.</td>
      <td>`_get_store`, `_run_config_smoke_tests`, `_validate_framework_config`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

### Segment 2: Profile source and capture evidence

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
      <td>`read_lakehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read a Delta table from a Fabric lakehouse.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`read_warehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read a table from a Microsoft Fabric warehouse.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`profile_dataframe`</td>
      <td>Callable orchestration wrapper</td>
      <td>Build canonical DQ-ready profiling rows from a Spark DataFrame.</td>
      <td>`_build_distribution_summaries`, `_get_profiled_columns`, `_is_min_max_supported_type`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

### Segment 3: AI-assisted drafting (advisory only)

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
      <td>`draft_dq_rules`</td>
      <td>Callable orchestration wrapper</td>
      <td>Draft candidate DQ rules from metadata profiles or raw DataFrame fallback.</td>
      <td>`_extract_dq_rules`, `_prepare_dq_profile_input_rows`, `_suggest_dq_rules`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`widget_review_dq_rules`</td>
      <td>Callable orchestration wrapper</td>
      <td>Review AI-suggested DQ rules sequentially with explicit approve/reject decisions.</td>
      <td>`_require_ipywidgets`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`write_dq_rules`</td>
      <td>Callable orchestration wrapper</td>
      <td>Validate, build, and persist approved DQ rules.</td>
      <td>`_build_dq_rule_history`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

### Segment 4: Human review and write approved DQ rules

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
      <td>`write_dq_rules`</td>
      <td>Callable orchestration wrapper</td>
      <td>Validate, build, and persist approved DQ rules.</td>
      <td>`_build_dq_rule_history`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

## `03_pc_<agreement>_<pipeline>`

Core production pipeline flow for clean evidence creation, preset-driven source and target guardrails, inline runtime audit columns, large-table write tuning, and controlled publishing. 03_pc uses validate_schema, monitor_data_changes, and stop_if_failed so users choose intent while FabricOps handles profiling, baseline selection, comparison, and enforcement mechanics internally. Audit columns are always useful; hashes, datetime features, and bucket columns are specialized patterns outside the default path.

### Segment 1: Runtime setup, parameters, agreement selection, and registration

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
      <td>Run consolidated FabricOps startup for exploration and pipeline notebooks.</td>
      <td>`_get_store`, `_run_config_smoke_tests`, `_validate_framework_config`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`widget_select_agreement`</td>
      <td>Callable orchestration wrapper</td>
      <td>Render a searchable agreement selector and store selected agreement metadata row in module state.</td>
      <td>`_html_escape`, `_latest_agreement_versions`, `_load_agreements`, `_refresh_registration_status`, `_render_searchable_selector`, `_require_ipywidgets`, `_selected_row`, `_status_message`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`get_selected_agreement`</td>
      <td>Callable orchestration wrapper</td>
      <td>Return the agreement selected by :func:`widget_select_agreement`.</td>
      <td>—</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`current_notebook_active_registrations`</td>
      <td>Callable orchestration wrapper</td>
      <td>Return active latest agreement registrations for the running notebook.</td>
      <td>`_context_get`, `_runtime_context`, `_safe_str`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

### Segment 2: Read source data

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
      <td>`read_lakehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read a Delta table from a Fabric lakehouse.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`read_warehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read a table from a Microsoft Fabric warehouse.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`read_lakehouse_csv`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read a CSV file from a Fabric lakehouse Files path.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`read_lakehouse_parquet`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read a Parquet file from a Fabric lakehouse Files path.</td>
      <td>`_convert_single_parquet_ns_to_us`, `_get_spark`, `_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`validate_schema`</td>
      <td>Callable orchestration wrapper</td>
      <td>Validate a dataframe schema using strict, allow_new_columns, or monitor_only presets.</td>
      <td>`_actual_schema`, `_check_schema`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`monitor_data_changes`</td>
      <td>Callable orchestration wrapper</td>
      <td>Profile a dataframe, select the appropriate baseline, compare distributions, and return a data-change result from a preset.</td>
      <td>`_as_monitor_only_result`, `_check_profile_drift`, `_data_change_preset_config`, `_extract_categorical_distribution_categories`, `_extract_numeric_distribution_bin_edges`, `_load_latest_profile`, `_normalize_profile`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`stop_if_failed`</td>
      <td>Callable orchestration wrapper</td>
      <td>Raise the shared guardrail error only when a schema or data-change result cannot continue.</td>
      <td>—</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

### Segment 3: Write reusable catalogue evidence from monitored profiles

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
      <td>`write_lakehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Write a Spark DataFrame to a Fabric lakehouse Delta table.</td>
      <td>`_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

### Segment 4: Transform, add runtime audit columns, and publish outputs

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
      <td>`validate_schema`</td>
      <td>Callable orchestration wrapper</td>
      <td>Validate a dataframe schema using strict, allow_new_columns, or monitor_only presets.</td>
      <td>`_actual_schema`, `_check_schema`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`monitor_data_changes`</td>
      <td>Callable orchestration wrapper</td>
      <td>Profile a dataframe, select the appropriate baseline, compare distributions, and return a data-change result from a preset.</td>
      <td>`_as_monitor_only_result`, `_check_profile_drift`, `_data_change_preset_config`, `_extract_categorical_distribution_categories`, `_extract_numeric_distribution_bin_edges`, `_load_latest_profile`, `_normalize_profile`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`stop_if_failed`</td>
      <td>Callable orchestration wrapper</td>
      <td>Raise the shared guardrail error only when a schema or data-change result cannot continue.</td>
      <td>—</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`build_runtime_audit_fields`</td>
      <td>Callable orchestration wrapper</td>
      <td>Build shared runtime audit values; 03_pc uses notebook and committed-by context while adding dataframe audit columns inline.</td>
      <td>`_context_get`, `_first_non_blank`, `_runtime_context`, `_safe_str`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`write_lakehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Write a Spark DataFrame to a Fabric lakehouse Delta table.</td>
      <td>`_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`write_warehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Write a Spark DataFrame to a Microsoft Fabric warehouse table.</td>
      <td>`_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

### Segment 5: Read back output and write lineage

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
      <td>`read_lakehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read a Delta table from a Fabric lakehouse.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`read_warehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read a table from a Microsoft Fabric warehouse.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`build_lineage_records`</td>
      <td>Callable orchestration wrapper</td>
      <td>Build compact lineage records for downstream metadata sinks.</td>
      <td>—</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`write_lakehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Write a Spark DataFrame to a Fabric lakehouse Delta table.</td>
      <td>`_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

