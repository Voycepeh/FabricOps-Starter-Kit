# Template Function Map

Template-first view of public callables and their main delegated helpers.

## `00_env_config`

Shared environment bootstrap and validation before exploration or pipeline notebooks run.

### Segment 1: Explain the shared environment role


### Segment 2: Define environment targets and notebook policy

- `FabricStore`: Fabric lakehouse or warehouse connection details. Delegates to No direct internal helpers detected.
- `load_config`: Validate and return a user-supplied framework configuration. Delegates to `_validate_framework_config`

### Segment 3: Set AI, quality, governance, and lineage defaults


### Segment 4: Assemble and validate framework config

- `load_config`: Validate and return a user-supplied framework configuration. Delegates to `_validate_framework_config`

### Segment 5: Run startup checks and show resolved paths

- `setup_notebook`: Run consolidated FabricOps startup for exploration and pipeline notebooks. Delegates to `_get_store`, `_run_config_smoke_tests`

## `01_da_<agreement>`

Captures approved usage, business context, stewardship notes, DQ approvals, governance approvals, and agreement-level controls reused by exploration and pipeline notebooks.

### Segment 1: Capture agreement context and approved usage


### Segment 2: Prepare governance input from approved business context


### Segment 3: Suggest AI-assisted PII and sensitivity labels


### Segment 4: Human review and approve governance controls

- `review_governance`: Display governance review widget and capture approve/reject decisions in module state. Delegates to `_now_utc_iso`, `_undo_last_action`
- `write_governance`: Persist approved governance rows to metadata table. Delegates to `_approved_widget_rows`

### Segment 5: Load approved governance metadata for downstream notebooks

- `load_governance`: Load approved governance metadata as read-only agreement context. Delegates to `_coerce_row_dicts`

## `02_ex_<agreement>_<topic>`

Exploration notebook flow used to profile source data and draft advisory AI outputs for human review.

### Segment 1: Load shared config and runtime

- `setup_notebook`: Run consolidated FabricOps startup for exploration and pipeline notebooks. Delegates to `_get_store`, `_run_config_smoke_tests`
- `load_config`: Validate and return a user-supplied framework configuration. Delegates to `_validate_framework_config`

### Segment 2: Profile source and capture evidence

- `read_lakehouse_table`: Read a Delta table from a Fabric lakehouse. Delegates to `_get_spark`, `_get_store`
- `read_warehouse_table`: Read a table from a Microsoft Fabric warehouse. Delegates to `_get_spark`, `_get_store`
- `profile_dataframe`: Build canonical DQ-ready profiling rows from a Spark DataFrame. Delegates to `_get_profiled_columns`, `_is_min_max_supported_type`

### Segment 3: AI-assisted drafting (advisory only)

- `draft_dq_rules`: Draft candidate DQ rules from metadata profiles or raw DataFrame fallback. Delegates to `_extract_dq_rules`, `_prepare_dq_profile_input_rows`, `_suggest_dq_rules`
- `review_dq_rules`: Review AI-suggested DQ rules sequentially with explicit approve/reject decisions. Delegates to `_require_ipywidgets`
- `write_dq_rules`: Validate, build, and persist approved DQ rules. Delegates to `_build_dq_rule_history`

### Segment 4: Human review and write approved DQ rules

- `write_dq_rules`: Validate, build, and persist approved DQ rules. Delegates to `_build_dq_rule_history`

### Optional lineage notes


## `03_pc_<agreement>_<pipeline>`

Pipeline notebook flow for deterministic enforcement and controlled publishing.

### Segment 1: Load shared config and runtime context

- `setup_notebook`: Run consolidated FabricOps startup for exploration and pipeline notebooks. Delegates to `_get_store`, `_run_config_smoke_tests`
- `load_config`: Validate and return a user-supplied framework configuration. Delegates to `_validate_framework_config`

### Segment 2: Load source data and validate required columns

- `read_lakehouse_table`: Read a Delta table from a Fabric lakehouse. Delegates to `_get_spark`, `_get_store`
- `read_warehouse_table`: Read a table from a Microsoft Fabric warehouse. Delegates to `_get_spark`, `_get_store`

### Segment 3: Transform and apply runtime standards

- `standardize_columns`: Apply canonical technical/audit enrichment in one notebook-facing wrapper. Delegates to `_add_audit_columns`, `_add_datetime_features`, `_add_hash_columns`
- `validate_dq_rules`: Validate canonical DQ rules before enforcement. Delegates to No direct internal helpers detected.

### Segment 4: Run DQ, split outputs, and publish

- `enforce_dq`: Enforce approved DQ rules and return structured deterministic outputs. Delegates to `_load_active_dq_rules`, `_run_dq_rules`, `_split_dq_rows`
- `assert_dq_passed`: Raise only after evidence materialization when error-severity rules fail. Delegates to No direct internal helpers detected.
- `write_lakehouse_table`: Write a Spark DataFrame to a Fabric lakehouse Delta table. Delegates to `_get_store`
- `write_warehouse_table`: Write a Spark DataFrame to a Microsoft Fabric warehouse table. Delegates to `_get_store`

### Optional profiling, drift, governance, lineage, and handover

- `profile_dataframe`: Build canonical DQ-ready profiling rows from a Spark DataFrame. Delegates to `_get_profiled_columns`, `_is_min_max_supported_type`
- `check_schema_drift`: Compare a current dataframe schema against a baseline schema snapshot. Delegates to No direct internal helpers detected.
- `check_partition_drift`: Check partition-level drift using keys, partitions, and optional watermark baselines. Delegates to No direct internal helpers detected.
- `check_profile_drift`: Compare profile metrics against a baseline profile and drift thresholds. Delegates to No direct internal helpers detected.
- `summarize_drift_results`: Summarize schema, partition, and profile drift outcomes into one decision. Delegates to No direct internal helpers detected.
- `write_governance`: Persist approved governance rows to metadata table. Delegates to `_approved_widget_rows`
- `write_governance`: Persist approved governance rows to metadata table. Delegates to `_approved_widget_rows`
- `load_governance`: Load approved governance metadata as read-only agreement context. Delegates to `_coerce_row_dicts`
- `build_lineage_records`: Build compact lineage records for downstream metadata sinks. Delegates to No direct internal helpers detected.
- `build_lineage_handover_markdown`: Build a concise markdown handover summary from lineage execution results. Delegates to No direct internal helpers detected.
- `build_handover`: Build a handover-friendly summary for one data product run. Delegates to No direct internal helpers detected.
- `render_handover_markdown`: Render a handover summary dictionary into Markdown for handover notes. Delegates to `_status_of`

