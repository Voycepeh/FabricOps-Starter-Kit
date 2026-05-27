# Template Function Map

Template-first view of public callables and their main delegated helpers.

## `00_env_config`

Shared environment bootstrap and validation before exploration or pipeline notebooks run.

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
    <tr>
      <td>`load_config`</td>
      <td>Callable orchestration wrapper</td>
      <td>Loads and validates environment configuration used by downstream notebooks.</td>
      <td>`_validate_framework_config`</td>
      <td>resolved paths are incorrect; environment mapping is missing</td>
    </tr>
  </tbody>
</table>

### Segment 4: Assemble and validate framework config

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
      <td>`load_config`</td>
      <td>Callable orchestration wrapper</td>
      <td>Loads and validates environment configuration used by downstream notebooks.</td>
      <td>`_validate_framework_config`</td>
      <td>resolved paths are incorrect; environment mapping is missing</td>
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
      <td>Template entrypoint</td>
      <td>Bootstraps notebook runtime checks and shared FabricOps context.</td>
      <td>`_get_store`, `_run_config_smoke_tests`</td>
      <td>notebook startup checks fail; runtime capabilities are missing</td>
    </tr>
  </tbody>
</table>

## `01_da_<agreement>`

Captures approved usage, business context, stewardship notes, DQ approvals, governance approvals, and agreement-level controls reused by exploration and pipeline notebooks.

### Segment 4: Human review and approve governance controls

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
      <td>`review_governance`</td>
      <td>Callable orchestration wrapper</td>
      <td>Display governance review widget and capture approve/reject decisions in module state.</td>
      <td>`_now_utc_iso`, `_undo_last_action`</td>
      <td>Check dependency outputs and metadata writes.</td>
    </tr>
    <tr>
      <td>`write_governance`</td>
      <td>Evidence writer</td>
      <td>Writes approved governance or classification evidence.</td>
      <td>`_approved_widget_rows`</td>
      <td>governance evidence was not written</td>
    </tr>
  </tbody>
</table>

### Segment 5: Load approved governance metadata for downstream notebooks

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
      <td>`load_governance`</td>
      <td>Callable utility</td>
      <td>Loads approved governance outputs for downstream notebook use.</td>
      <td>`_coerce_row_dicts`</td>
      <td>governance metadata fails to load</td>
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
      <td>Template entrypoint</td>
      <td>Bootstraps notebook runtime checks and shared FabricOps context.</td>
      <td>`_get_store`, `_run_config_smoke_tests`</td>
      <td>notebook startup checks fail; runtime capabilities are missing</td>
    </tr>
    <tr>
      <td>`load_config`</td>
      <td>Callable orchestration wrapper</td>
      <td>Loads and validates environment configuration used by downstream notebooks.</td>
      <td>`_validate_framework_config`</td>
      <td>resolved paths are incorrect; environment mapping is missing</td>
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
      <td>Callable utility</td>
      <td>Reads source or metadata tables from configured lakehouse targets.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>metadata table was not read; table path resolution fails</td>
    </tr>
    <tr>
      <td>`read_warehouse_table`</td>
      <td>Callable utility</td>
      <td>Reads warehouse tables through configured Fabric workspace routing.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>warehouse relation not found; warehouse query returns unexpected schema</td>
    </tr>
    <tr>
      <td>`profile_dataframe`</td>
      <td>Validation/check function</td>
      <td>Profiles dataframe structure and quality indicators for evidence and review.</td>
      <td>`_get_profiled_columns`, `_is_min_max_supported_type`</td>
      <td>profile metrics look inconsistent; profile output schema changed unexpectedly</td>
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
      <td>AI-assisted suggestion function</td>
      <td>Drafts candidate data quality rules from business context and profile evidence.</td>
      <td>`_extract_dq_rules`, `_prepare_dq_profile_input_rows`, `_suggest_dq_rules`</td>
      <td>AI-generated rules do not match business expectations; suggested rules are too generic</td>
    </tr>
    <tr>
      <td>`review_dq_rules`</td>
      <td>Review/approval function</td>
      <td>Supports human review of drafted quality rules before approval.</td>
      <td>`_require_ipywidgets`</td>
      <td>review workflow misses required rule fields</td>
    </tr>
    <tr>
      <td>`write_dq_rules`</td>
      <td>Evidence writer</td>
      <td>Persists approved quality rules to metadata targets.</td>
      <td>`_build_dq_rule_history`</td>
      <td>metadata table was not written; rule versioning appears wrong</td>
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
      <td>Evidence writer</td>
      <td>Persists approved quality rules to metadata targets.</td>
      <td>`_build_dq_rule_history`</td>
      <td>metadata table was not written; rule versioning appears wrong</td>
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
      <td>Template entrypoint</td>
      <td>Bootstraps notebook runtime checks and shared FabricOps context.</td>
      <td>`_get_store`, `_run_config_smoke_tests`</td>
      <td>notebook startup checks fail; runtime capabilities are missing</td>
    </tr>
    <tr>
      <td>`load_config`</td>
      <td>Callable orchestration wrapper</td>
      <td>Loads and validates environment configuration used by downstream notebooks.</td>
      <td>`_validate_framework_config`</td>
      <td>resolved paths are incorrect; environment mapping is missing</td>
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
      <td>Callable utility</td>
      <td>Reads source or metadata tables from configured lakehouse targets.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>metadata table was not read; table path resolution fails</td>
    </tr>
    <tr>
      <td>`read_warehouse_table`</td>
      <td>Callable utility</td>
      <td>Reads warehouse tables through configured Fabric workspace routing.</td>
      <td>`_get_spark`, `_get_store`</td>
      <td>warehouse relation not found; warehouse query returns unexpected schema</td>
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
      <td>Callable utility</td>
      <td>Applies canonical technical column naming and formatting standards.</td>
      <td>`_add_audit_columns`, `_add_datetime_features`, `_add_hash_columns`</td>
      <td>standardized output columns are missing</td>
    </tr>
    <tr>
      <td>`validate_dq_rules`</td>
      <td>Validation/check function</td>
      <td>Validates DQ rules before enforcement against pipeline data.</td>
      <td>—</td>
      <td>rule parsing fails; validation rejects expected rules</td>
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
      <td>Executes DQ checks and splits pass/quarantine records.</td>
      <td>`_load_active_dq_rules`, `_run_dq_rules`, `_split_dq_rows`</td>
      <td>DQ rules look wrong; quarantine split is unexpected</td>
    </tr>
    <tr>
      <td>`assert_dq_passed`</td>
      <td>Validation/check function</td>
      <td>Raises enforcement failures after evidence is materialized.</td>
      <td>—</td>
      <td>pipeline succeeds when DQ should fail</td>
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
      <td>Validation/check function</td>
      <td>Profiles dataframe structure and quality indicators for evidence and review.</td>
      <td>`_get_profiled_columns`, `_is_min_max_supported_type`</td>
      <td>profile metrics look inconsistent; profile output schema changed unexpectedly</td>
    </tr>
    <tr>
      <td>`check_schema_drift`</td>
      <td>Validation/check function</td>
      <td>Detects schema drift against approved baseline evidence.</td>
      <td>—</td>
      <td>schema drift was not detected</td>
    </tr>
    <tr>
      <td>`check_partition_drift`</td>
      <td>Validation/check function</td>
      <td>Detects partition-level drift against expected partition behavior.</td>
      <td>—</td>
      <td>partition freshness or counts look wrong</td>
    </tr>
    <tr>
      <td>`check_profile_drift`</td>
      <td>Validation/check function</td>
      <td>Compares profile metrics with baseline thresholds.</td>
      <td>—</td>
      <td>profile drift alerts are missing or noisy</td>
    </tr>
    <tr>
      <td>`summarize_drift_results`</td>
      <td>Callable orchestration wrapper</td>
      <td>Combines drift checks into one decision and summary output.</td>
      <td>—</td>
      <td>drift summary decision contradicts check outputs</td>
    </tr>
    <tr>
      <td>`write_governance`</td>
      <td>Evidence writer</td>
      <td>Writes approved governance or classification evidence.</td>
      <td>`_approved_widget_rows`</td>
      <td>governance evidence was not written</td>
    </tr>
    <tr>
      <td>`load_governance`</td>
      <td>Callable utility</td>
      <td>Loads approved governance outputs for downstream notebook use.</td>
      <td>`_coerce_row_dicts`</td>
      <td>governance metadata fails to load</td>
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
      <td>Builds run handover package from governance, quality, and lineage outputs.</td>
      <td>—</td>
      <td>handover summary misses required sections</td>
    </tr>
    <tr>
      <td>`render_handover_markdown`</td>
      <td>Callable utility</td>
      <td>Renders handover evidence into markdown for maintainers.</td>
      <td>`_status_of`</td>
      <td>markdown rendering fails; JSON serialization failed</td>
    </tr>
  </tbody>
</table>

