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

Core production pipeline template for clean evidence creation and controlled publishing. The base flow intentionally avoids governance enforcement until `04_gov` has approved the metadata that a later enhanced production pipeline should enforce.

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
      <td>Run consolidated FabricOps startup for non-sample pipeline notebooks.</td>
      <td>`_get_store`, `_run_config_smoke_tests`, `_validate_framework_config`</td>
      <td>Check environment target names and metadata routing.</td>
    </tr>
    <tr>
      <td>`select_agreement`</td>
      <td>Callable orchestration wrapper</td>
      <td>Select the agreement and render notebook-registration controls for `03_pc`.</td>
      <td>`_load_agreements`, `current_notebook_active_registrations`, `register_current_notebook`</td>
      <td>No active agreement appears or registration status is unexpected.</td>
    </tr>
    <tr>
      <td>`get_selected_agreement`</td>
      <td>Callable context accessor</td>
      <td>Expose the selected agreement row for catalogue and lineage evidence.</td>
      <td>—</td>
      <td>The selected agreement context is missing.</td>
    </tr>
    <tr>
      <td>`current_notebook_active_registrations`</td>
      <td>Callable metadata lookup</td>
      <td>Read active notebook-registration rows and expose `registration_id` when available.</td>
      <td>`load_notebook_registry`</td>
      <td>Lineage or catalogue rows need notebook registry traceability.</td>
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
      <td>The source or target lakehouse table cannot be read.</td>
    </tr>
    <tr>
      <td>`read_warehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read a table from a Microsoft Fabric warehouse.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>The source or target warehouse table cannot be read.</td>
    </tr>
    <tr>
      <td>`read_lakehouse_csv`</td>
      <td>Callable file reader</td>
      <td>Read a CSV file from a Fabric lakehouse `Files/...` path.</td>
      <td>`_get_spark`, `_resolve_lakehouse_files_path`</td>
      <td>Landing-zone or reference-file inputs are stored as CSV.</td>
    </tr>
    <tr>
      <td>`read_lakehouse_parquet`</td>
      <td>Callable file reader</td>
      <td>Read a Parquet file or folder from a Fabric lakehouse `Files/...` path.</td>
      <td>`_get_spark`, `_resolve_lakehouse_files_path`</td>
      <td>Landing-zone inputs are stored as Parquet.</td>
    </tr>
  </tbody>
</table>

### Segment 3: Profile and write reusable catalogue evidence

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
      <td>`profile_dataframe`</td>
      <td>Callable orchestration wrapper</td>
      <td>Build source and output profiling rows for reusable catalogue evidence.</td>
      <td>`_get_profiled_columns`, `_is_min_max_supported_type`</td>
      <td>Profile rows are empty or include unexpected columns.</td>
    </tr>
    <tr>
      <td>`write_lakehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Write catalogue and lineage metadata through the configured metadata target.</td>
      <td>`_get_store`</td>
      <td>Metadata writes do not land in the metadata lakehouse route from `00_env_config`.</td>
    </tr>
  </tbody>
</table>

### Segment 4: Transform, add technical columns, and publish

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
      <td>`standardize_columns`</td>
      <td>Callable orchestration wrapper</td>
      <td>Apply lightweight technical columns such as run id, pipeline name, environment, source table, processed timestamp, record hash, and business-key hash.</td>
      <td>`_add_audit_columns`, `_add_hash_columns`</td>
      <td>Technical columns or hash fields are missing from the published target.</td>
    </tr>
    <tr>
      <td>`write_lakehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Write a Spark DataFrame to a Fabric lakehouse Delta table.</td>
      <td>`_get_store`</td>
      <td>Lakehouse publishing fails.</td>
    </tr>
    <tr>
      <td>`write_warehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Write a Spark DataFrame to a Microsoft Fabric warehouse table.</td>
      <td>`_get_store`</td>
      <td>Warehouse publishing fails.</td>
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
      <td>Read the published lakehouse table back for output profiling.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>The written output cannot be read back.</td>
    </tr>
    <tr>
      <td>`read_warehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Read the published warehouse table back for output profiling.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>The written output cannot be read back.</td>
    </tr>
    <tr>
      <td>`build_lineage_records`</td>
      <td>Callable orchestration wrapper</td>
      <td>Build compact source-to-target lineage rows before metadata persistence.</td>
      <td>—</td>
      <td>Lineage payloads need source, target, agreement, run, pipeline, environment, and notebook registration context.</td>
    </tr>
  </tbody>
</table>

Governance-only helpers such as `enforce_dq`, `assert_dq_passed`, `write_governance`, `load_governance`, sensitivity enforcement, classification enforcement, quarantine publishing, and fail-fast guardrail execution are not part of the base `03_pc` flow. Use them only in an enhanced production pipeline after `04_gov` has approved the governing metadata.
