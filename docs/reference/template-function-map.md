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

Pipeline notebook flow for deterministic enforcement and controlled publishing.

### Segment 1: Load shared config and runtime context

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

### Segment 2: Load source data and validate required columns

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
  </tbody>
</table>

### Segment 3: Transform and apply runtime standards

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
      <td>Apply canonical technical/audit enrichment in one notebook-facing wrapper.</td>
      <td>`_add_audit_columns`, `_add_datetime_features`, `_add_hash_columns`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`validate_dq_rules`</td>
      <td>Callable orchestration wrapper</td>
      <td>Validate canonical DQ rules before enforcement.</td>
      <td>—</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

### Segment 4: Run DQ, split outputs, and publish

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
      <td>`enforce_dq`</td>
      <td>Callable orchestration wrapper</td>
      <td>Enforce approved DQ rules and return structured deterministic outputs.</td>
      <td>`_load_active_dq_rules`, `_run_dq_rules`, `_split_dq_rows`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`assert_dq_passed`</td>
      <td>Callable orchestration wrapper</td>
      <td>Raise only after evidence materialization when error-severity rules fail.</td>
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
    <tr>
      <td>`write_warehouse_table`</td>
      <td>Callable orchestration wrapper</td>
      <td>Write a Spark DataFrame to a Microsoft Fabric warehouse table.</td>
      <td>`_get_store`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

### Optional profiling, drift, governance, lineage, and handover

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
      <td>Build canonical DQ-ready profiling rows from a Spark DataFrame.</td>
      <td>`_get_profiled_columns`, `_is_min_max_supported_type`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`check_schema_drift`</td>
      <td>Callable orchestration wrapper</td>
      <td>Compare a current dataframe schema against a baseline schema snapshot.</td>
      <td>—</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`check_partition_drift`</td>
      <td>Callable orchestration wrapper</td>
      <td>Check partition-level drift using keys, partitions, and optional watermark baselines.</td>
      <td>—</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`check_profile_drift`</td>
      <td>Callable orchestration wrapper</td>
      <td>Compare profile metrics against a baseline profile and drift thresholds.</td>
      <td>—</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`summarize_drift_results`</td>
      <td>Callable orchestration wrapper</td>
      <td>Summarize schema, partition, and profile drift outcomes into one decision.</td>
      <td>—</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`write_governance`</td>
      <td>Callable orchestration wrapper</td>
      <td>Persist approved governance rows to metadata table.</td>
      <td>`_approved_widget_rows`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`load_governance`</td>
      <td>Callable orchestration wrapper</td>
      <td>Load approved governance metadata as read-only agreement context.</td>
      <td>`_coerce_row_dicts`</td>
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
      <td>`build_lineage_handover_markdown`</td>
      <td>Callable orchestration wrapper</td>
      <td>Build a concise markdown handover summary from lineage execution results.</td>
      <td>—</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`build_handover`</td>
      <td>Callable orchestration wrapper</td>
      <td>Build a handover-friendly summary for one data product run.</td>
      <td>—</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`render_handover_markdown`</td>
      <td>Callable orchestration wrapper</td>
      <td>Render a handover summary dictionary into Markdown for handover notes.</td>
      <td>`_status_of`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
  </tbody>
</table>

