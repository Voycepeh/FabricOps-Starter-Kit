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

Form notebook that supports two agreement-intake layouts for A/B testing. Option A renders a compact section switcher through `render_agreement_intake_app(...)`. Option B renders separate widget cells for Data Steward, Data Agreement, and Agreement Evidence through `render_data_steward_widget(...)`, `render_data_agreement_widget(...)`, and `render_agreement_evidence_widget(...)`. Both layouts write append-only metadata and agreement intake selects active steward rows.

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
      <td>`render_agreement_intake_app`</td>
      <td>Callable orchestration wrapper</td>
      <td>Render and wire the compact agreement-intake section switcher application.</td>
      <td>`_render_agreement_evidence_widget`, `_render_maintenance_widget`</td>
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
      <td>`render_data_steward_widget`</td>
      <td>Callable orchestration wrapper</td>
      <td>Render append-only data steward maintenance.</td>
      <td>`_render_maintenance_widget`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`render_data_agreement_widget`</td>
      <td>Callable orchestration wrapper</td>
      <td>Render append-only agreement maintenance using active steward rows.</td>
      <td>`_render_maintenance_widget`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`render_agreement_evidence_widget`</td>
      <td>Callable orchestration wrapper</td>
      <td>Render standalone agreement evidence upload controls for an existing agreement version.</td>
      <td>`_render_agreement_evidence_widget`</td>
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
      <td>`_get_profiled_columns`, `_is_min_max_supported_type`</td>
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
      <td>`review_dq_rules`</td>
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

Core production pipeline flow for clean evidence creation, schema guardrails, inline runtime audit columns, large-table write tuning, and controlled publishing. 03_pc applies source schema guardrails after read and target schema guardrails before audit columns/write.

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
      <td>`select_agreement`</td>
      <td>Callable orchestration wrapper</td>
      <td>Render a searchable agreement selector and store selected agreement metadata row in module state.</td>
      <td>`_html_escape`, `_latest_agreement_versions`, `_load_agreements`, `_refresh_registration_status`, `_render_searchable_selector`, `_selected_row`, `_status_message`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`get_selected_agreement`</td>
      <td>Callable orchestration wrapper</td>
      <td>Return the agreement selected by :func:`select_agreement`.</td>
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
  </tbody>
</table>

### Segment 3: Apply schema guardrails, profile, and write reusable catalogue evidence

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
      <td>`apply_schema_guardrail`</td>
      <td>Callable orchestration wrapper</td>
      <td>Load the approved dataset contract, validate schema drift, enforce observe/warn/fail behavior, and write evidence.</td>
      <td>`_build_schema_validation_evidence`, `_enforce_schema_result`, `_get_active_spark`, `_load_schema_contract`, `_write_schema_validation_evidence`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`profile_dataframe`</td>
      <td>Callable orchestration wrapper</td>
      <td>Build canonical DQ-ready profiling rows from a Spark DataFrame.</td>
      <td>`_get_profiled_columns`, `_is_min_max_supported_type`</td>
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

### Segment 4: Transform, apply target guardrail, add runtime audit columns, and publish outputs

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

### Segment 5: Read back output, profile output, and write lineage

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
      <td>`_get_profiled_columns`, `_is_min_max_supported_type`</td>
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
