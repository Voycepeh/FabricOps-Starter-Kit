# Metadata tables

FabricOps metadata tables live in the Governance workspace `metadata_lakehouse`. They coordinate the notebook workflow and keep metadata evidence available for review, support, and visibility.

`00_env_config` contains the metadata setup call as an optional commented block. Uncomment and run that block manually once per environment to create the current active metadata tables, then comment it back before normal use. Rerun it only after metadata schema/table changes. Keeping setup commented makes downstream `%run 00_env_config` calls fast for `01_agreement`, `02_pipeline`, and `03_governance`. The setup creates missing metadata tables by building empty Spark DataFrames from the known schemas and writing them through the configured `metadata` lakehouse target; the notebook does **not** need a default lakehouse attachment for metadata setup. `METADATA_DATA_ACCESS` remains documented as optional access-capture metadata, but it is not created by the standard setup until an access-capture workflow enables it. Most users should not create or edit these schemas by hand.

A healthy metadata table is rooted directly at `Tables/<metadata_table>/_delta_log`; it should not be created as a nested path such as `Tables/<metadata_table>/Unidentified/_delta_log`. FabricOps does not automatically migrate older or malformed metadata tables. If schema validation reports missing columns or you find an older nested folder, recreate the affected table or manually migrate the data before rerunning setup. If you choose to inspect the metadata lakehouse catalog manually, run catalog checks against the configured metadata lakehouse rather than relying on a notebook default lakehouse.


## Classic and schema-enabled Lakehouse registration

FabricOps supports both Microsoft Fabric Lakehouse table registration models:

- **Classic/non-schema Lakehouses:** set `LAKEHOUSE_SCHEMAS_ENABLED = False` and keep target schemas unset or `None` in `00_env_config`. When you manually uncomment and run the setup block, metadata setup writes Delta tables under `Tables/<table_name>` in the configured metadata Lakehouse.
- **Schema-enabled Lakehouses:** keep `LAKEHOUSE_SCHEMAS_ENABLED = True` and set `METADATA_SCHEMA` to the configured schema such as `"dbo"` in `00_env_config`. The configured metadata target carries that schema into shared Lakehouse IO, so metadata setup writes physical Delta tables under `Tables/<schema>/<metadata_table_name>` (for example `Tables/dbo/METADATA_DATA_AGREEMENT`) while Spark identifiers resolve as `<schema>.<table>` when needed.

If you see `Unidentified` folders in a schema-enabled Lakehouse, the tables were likely written as path-based Delta folders instead of registered schema tables. FabricOps does not automatically delete, move, or migrate those folders. Confirm there is no needed data in the folders, then recreate the tables through the optional `00_env_config` setup block using the configured `METADATA_SCHEMA` or manually migrate the data using your normal Fabric administration process.

All workflow notebooks read and write metadata through the configured metadata route:

```python
read_lakehouse_table(CONFIG, env_name, "metadata", "<table_name>", schema=METADATA_SCHEMA)

write_lakehouse_table(
    df,
    CONFIG,
    env_name,
    "metadata",
    "<table_name>",
    schema=METADATA_SCHEMA,
    mode="append",
)
```

## Architecture

![Shared FabricOps metadata model connecting governance and engineering notebooks](../assets/fabricops-metadata-model.png){ .full-width }

| Metadata table | Main writer | Purpose |
| --- | --- | --- |
| `METADATA_DATA_STEWARD` | `01_agreement` | Stores steward identities used during agreement intake. |
| `METADATA_DATA_AGREEMENT` | `01_agreement` | Stores versioned data agreements and approved usage context. |
| `METADATA_DATA_AGREEMENT_EVIDENCE` | `01_agreement` | Stores file references that support an agreement version. |
| `METADATA_NOTEBOOK_REGISTRY` | `02_pipeline`, optional `99_explore` | Stores notebook-to-agreement relationships. |
| `METADATA_DATA_LINEAGE_TABLE` | `02_pipeline` | Stores current table-level lineage evidence for a notebook. |
| `METADATA_DATA_CATALOGUE` | `02_pipeline` | Profile evidence/history table: records table and column observations, profile snapshots, profile hashes/payloads, watermark context, and accepted/passed evidence used for guardrail comparison. |
| `METADATA_PIPELINE_RUNS` | `02_pipeline` | Stores one runtime summary row per pipeline run, tied to agreement and notebook registry context. |
| `METADATA_DATA_ACCESS` | Optional access capture process | Optional table-level access assignments when captured; not part of the current active setup registry. |
| `METADATA_COLUMN_CONTEXT` | `03_governance` | Stores reviewed business meaning for catalogue columns. |
| `METADATA_GUARDRAIL_RULES` | `03_governance` | Stores approved or proposed guardrail rules: what should be checked for `schema`, `freshness`, `profile_behavior`, and `dq` guardrails. DQ rows use `guardrail_type="dq"`. |
| `METADATA_GUARDRAIL_RESULTS` | Runtime evidence schema | Stores pass/warn/fail guardrail outcomes: what passed, warned, failed, or blocked continuation. |
| `METADATA_COLUMN_CLASSIFICATION` | `03_governance` | Stores reviewed sensitivity and PII classifications. |
| `METADATA_GOVERNANCE_REVIEWS` | `03_governance` | Stores final review outcomes such as approved, rejected, or needs remediation with blockers and warnings. |

`01_agreement` writes steward, agreement, and evidence metadata. `02_pipeline` writes registry, catalogue/profile evidence, lineage, run evidence, and guardrail result evidence when checks run. Baselines are derived from previous accepted or passed profile evidence in `METADATA_DATA_CATALOGUE`; FabricOps does not create separate guardrail profile or baseline event tables for now. `03_governance` writes reviewed metadata such as column context, guardrail rules, sensitivity, classification, and final governance review outcomes. `99_explore` can support investigation, but it is optional and is not a required gate.

For how schema, freshness, profile behavior, and DQ settings produce this evidence, see [Pipeline Guardrails](pipeline-guardrails.md).

## Callable references

Use these generated API references for helpers that create, read, or write metadata evidence:

- [setup_metadata_tables](../api/reference/setup_metadata_tables/) prepares the configured metadata tables.
- [write_catalogue_evidence](../api/reference/write_catalogue_evidence/), [write_pipeline_lineage](../api/reference/write_pipeline_lineage/), and [write_pipeline_run_summary](../api/reference/write_pipeline_run_summary/) write pipeline evidence.
- [record_table_governance](../api/reference/record_table_governance/) writes approved governance metadata.

## Standard runtime audit columns

Most metadata tables include these audit columns. They show who wrote the row, from where, and when. FabricOps defaults generated audit timestamps to UTC. You can set `FABRICOPS_AUDIT_TIMEZONE` in `00_env_config` to a valid IANA timezone such as `Asia/Singapore`; the setting applies to metadata audit timestamps and technical timestamp columns added by helper functions.

| Column | Purpose |
| --- | --- |
| `_committed_by` | User or service that committed the row. |
| `_committed_at` | Commit timestamp. |
| `_notebook_name` | Notebook that committed the row. |
| `_workspace_name` | Fabric workspace captured at runtime. |
| `_metadata_lakehouse_name` | Configured metadata lakehouse. |
| `_activity_id` | Fabric activity identifier. |

These fields are generated by the shared runtime audit helper and are not repeated in every table section below. `METADATA_NOTEBOOK_REGISTRY` uses explicit notebook runtime fields because notebook identity is the subject of that table.

## Logical keys

Fabric Delta tables do not enforce primary and foreign keys. FabricOps still uses stable logical keys for joins, validation, and latest-record selection.

| Metadata table | Logical primary key | Main relationship |
| --- | --- | --- |
| `METADATA_DATA_STEWARD` | `steward_id` | No parent table. |
| `METADATA_DATA_AGREEMENT` | `agreement_id`, `contract_version` | `steward_id` links to `METADATA_DATA_STEWARD`. |
| `METADATA_DATA_AGREEMENT_EVIDENCE` | `agreement_id`, `contract_version`, `file_path` | Links to one agreement version. |
| `METADATA_NOTEBOOK_REGISTRY` | `registration_id` | Links notebooks to agreement versions. |
| `METADATA_DATA_LINEAGE_TABLE` | `lineage_id` | Links lineage to notebook identity and catalogue table keys. |
| `METADATA_DATA_CATALOGUE` | `profile_run_id`, `profile_stage`, `metadata_column_key` | Provides stable table and column profile evidence/history used by review metadata and guardrail comparison. |
| `METADATA_PIPELINE_RUNS` | `run_id` | Links runtime summaries to agreements, notebook registrations, catalogue evidence, and lineage rows. |
| `METADATA_DATA_ACCESS` | `user_principal`, `table_id`, `granted_date` | `table_id` links to catalogue table keys. |
| `METADATA_COLUMN_CONTEXT` | `metadata_column_key`, `_committed_at` | Links reviewed context to a catalogue column. |
| `METADATA_GUARDRAIL_RULES` | `rule_key`, `_committed_at` | Links approved or proposed guardrail expectations to catalogue table or column keys. |
| `METADATA_GUARDRAIL_RESULTS` | `result_id` | Links runtime pass/fail outcomes to a guardrail rule, run, table, and optional column. |
| `METADATA_COLUMN_CLASSIFICATION` | `metadata_column_key`, `_committed_at` | Links reviewed classification to a catalogue column. |
| `METADATA_GOVERNANCE_REVIEWS` | `review_id` | Links the final `03_governance` outcome to agreement, pipeline run, catalogue profile, blockers, warnings, and evidence-summary context. |

## Table details

### `METADATA_DATA_STEWARD`

**For:** steward identities and effective periods used by `01_agreement`.

| Column | Purpose |
| --- | --- |
| `steward_id` | Stable generated steward identifier. |
| `steward_name` | Steward display name. |
| `steward_role` | Controlled steward role. |
| `contact` | Steward contact details. |
| `effective_from` | Optional assignment start date. |
| `effective_to` | Optional assignment end date. |
| `is_active` | Backend-derived active status. |
| `custom_fields_json` | Config-driven organisation-specific values. |

**Workflow connection:** agreements reference stewards through `steward_id`. Includes the standard runtime audit columns.

### `METADATA_DATA_AGREEMENT`

**For:** one append-only row per agreement version written by `01_agreement`.

| Column | Purpose |
| --- | --- |
| `agreement_id` | Stable generated agreement identifier. |
| `contract_version` | Generated agreement version. |
| `steward_id` | Reference to `METADATA_DATA_STEWARD`. |
| `agreement_name` | Agreement display name. |
| `domain` | Business or data domain. |
| `recipient` | Intended data recipient or consumer. |
| `start_date` | Agreement start date. |
| `expiry_date` | Agreement expiry date. |
| `business_purpose` | Approved business purpose. |
| `approved_usage_internal` | Approved internal usage. |
| `approved_usage_external` | Approved external usage. |
| `approved_usage_research` | Approved research usage. |
| `custom_fields_json` | Config-driven organisation-specific values. |

**Workflow connection:** `02_pipeline` can link to agreement versions through the notebook registry. Includes the standard runtime audit columns.

### `METADATA_DATA_AGREEMENT_EVIDENCE`

**For:** supporting file references for an agreement version, written by `01_agreement`.

| Column | Purpose |
| --- | --- |
| `agreement_id` | Referenced agreement. |
| `contract_version` | Referenced agreement version. |
| `file_path` | Metadata lakehouse `Files/...` path. |
| `evidence_type` | Evidence category selected by the user. |
| `file_name` | File name derived from the submitted path. |
| `mime_type` | MIME type derived from the file extension. |
| `file_size` | File size collected when available. |
| `uploaded_at` | Upload event timestamp generated by the widget. |
| `uploaded_by` | Uploading user generated by the widget. |

**Workflow connection:** agreement evidence helps reviewers and support teams understand why the agreement exists. Includes the standard runtime audit columns.

### `METADATA_NOTEBOOK_REGISTRY`

**For:** active and historical relationships between notebooks and data agreements. `02_pipeline` is the normal writer; optional `99_explore` can register support notebooks when useful.

| Column | Purpose |
| --- | --- |
| `registration_id` | Stable notebook-agreement relationship identifier. |
| `agreement_id` | Agreement linked to the notebook. |
| `agreement_contract_version` | Agreement version linked to the notebook. |
| `registration_role` | Relationship role such as `primary` or `additional`. |
| `registration_status` | `active`, `inactive` or `superseded`. |
| `notebook_id` | Fabric notebook identifier. |
| `notebook_name` | Fabric notebook name. |
| `notebook_type` | Notebook family such as `02_pipeline` or optional `99_explore`. |
| `workspace_id` | Fabric workspace identifier. |
| `workspace_name` | Fabric workspace name. |
| `notebook_url` | Fabric notebook URL. |
| `environment_name` | Environment context. |
| `dataset_name` | Dataset or data-product context. |
| `table_name` | Optional table context. |
| `topic` | Notebook topic. |
| `pipeline_name` | Pipeline or workflow name. |
| `user_name` | User who registered the relationship. |
| `user_id` | Registering user identifier. |
| `registered_at` | Registration timestamp. |
| `superseded_at` | Supersession timestamp. |
| `superseded_by_registration_id` | Replacement registration identifier. |

**Workflow connection:** one notebook can link to multiple agreements, and one agreement can link to multiple notebooks. This table does not store pipeline runs, lineage, profiles, or reviewed metadata.

### `METADATA_DATA_LINEAGE_TABLE`

**For:** current table-level lineage evidence written by `02_pipeline`.

| Column | Purpose |
| --- | --- |
| `lineage_id` | Stable lineage identifier. |
| `notebook_id` | Notebook that owns the lineage definition. |
| `environment_name` | Environment context. |
| `dataset_name` | Dataset context. |
| `pipeline_name` | Pipeline identity. |
| `source_tables_json` | JSON list of source tables and stable table keys. |
| `target_tables_json` | JSON list of target tables and stable table keys. |
| `transformation_summary` | Human-readable transformation summary. |
| `lineage_status` | `active` or `inactive`. |
| `captured_at` | Lineage capture timestamp. |
| `lineage_payload_json` | Optional extended lineage evidence. |

**Workflow connection:** lineage links to the catalogue through `metadata_table_key` values inside the source and target JSON arrays. A lineage record can include multiple source and target tables.

### `METADATA_DATA_CATALOGUE`

**For:** table and column profile evidence/history written by `02_pipeline` for each source or target profile run. The catalogue answers “what exists and what was profiled,” stores profile snapshots used for guardrail comparison, and provides previous accepted or passed evidence from which baselines can be derived. Guardrail rules remain in `METADATA_GUARDRAIL_RULES`; runtime outcomes remain in `METADATA_GUARDRAIL_RESULTS`.

| Column | Purpose |
| --- | --- |
| `profile_run_id` | Unique pipeline execution identifier. |
| `profile_stage` | `source` or `target`. |
| `metadata_table_key` | Stable table identifier. |
| `metadata_column_key` | Stable column identifier. |
| `table_name` | Table name emitted by the profiling function. |
| `column_name` | Profiled column name. |
| `data_type` | Observed data type. |
| `row_count` | Profiled row count. |
| `null_count` | Observed null count. |
| `null_percentage` | Observed null percentage. |
| `distinct_count` | Observed distinct count. |
| `distinct_percentage` | Observed distinct percentage. |
| `min_value` | Observed minimum value where supported. |
| `max_value` | Observed maximum value where supported. |
| `distribution_type` | Optional distribution summary type retained as profile evidence. |
| `distribution_json` | Compact distribution evidence. |
| `profiled_at` | Profiling timestamp. |
| `notebook_id` | Producing Fabric notebook identifier. |
| `environment_name` | Environment context. |
| `dataset_name` | Dataset or data-product context. |
| `pipeline_name` | Stable pipeline identity. |
| `evidence_role` | Source-profile or output-profile role. |
| `profile_status` | Profile status. |
| `baseline_status` | `observed` or `approved`. |
| `source_schema_check` | Source schema-check preset used by the pipeline. |
| `target_schema_check` | Target schema-check preset used by the pipeline. |
| `source_data_change_check` | Source `profile_mode` label used by the pipeline. |
| `target_data_change_check` | Target `profile_mode` label used by the pipeline. |
| `stability_check_enabled` | Whether profile behavior enforcement was enabled for this table. |
| `load_behavior` | Existing catalogue compatibility column populated with the current `profile_mode` value. |
| `watermark_column` | Watermark column used for `changing_data` profile group comparisons when configured. |
| `profile_payload_json` | Compact JSON payload with additional profile evidence used by comparison or review workflows. |
| `profile_hash` | Stable hash of the relevant profile observation used for comparison. |
| `watermark_value` | Watermark value for a grouped or incremental profile snapshot. |
| `freshness_column` | Column whose maximum value is checked by the freshness guardrail. |
| `freshness_max_lag_days` | Maximum allowed lag, in days, for the freshness guardrail. |
| `freshness_status` | Freshness guardrail result status. |
| `freshness_can_continue` | Whether the freshness result allows the pipeline to continue. |
| `freshness_message` | Human-readable freshness result. |
| `baseline_run_id` | Previous accepted catalogue run used as the comparison point. |
| `stability_status` | Profile behavior guardrail result status. |
| `stability_can_continue` | Whether the profile behavior result allows the pipeline to continue. |
| `stability_message` | Human-readable profile behavior result. |
| `stability_difference_summary` | Compact row-count or watermark comparison summary when profile behavior fails. |
| `source_change_signal_json` | Optional source-change signal containing schema, freshness, and profile behavior details. |
| `layer` | Source or target storage layer. |
| `asset_kind` | Lakehouse, warehouse, CSV or Parquet. |

**Workflow connection:** `03_governance` uses catalogue evidence to select tables and columns for reviewed metadata. Agreement context can be resolved through the notebook registry rather than stored directly on each catalogue row.

### `METADATA_PIPELINE_RUNS`

**For:** runtime evidence written by the thin `02_pipeline` orchestration template.

This table stores one summary row per pipeline run. It is tied to the selected agreement and notebook registration so support teams can connect a run to catalogue evidence and lineage without reading notebook implementation code.

| Column | Purpose |
| --- | --- |
| `run_id` | Runtime identifier from `setup_notebook` or the Fabric runtime. |
| `agreement_id` | Selected data agreement identifier. |
| `agreement_contract_version` | Agreement version used by the run. |
| `notebook_registry_id` | Active notebook registration row associated with the selected agreement. |
| `notebook_id` | Fabric notebook identifier when available. |
| `notebook_type` | Notebook workflow type, usually `02_pipeline`. |
| `pipeline_name` | User-friendly pipeline name. |
| `environment_name` | Environment key from `00_env_config`. |
| `started_at` | Audit timestamp captured when orchestration starts. |
| `completed_at` | Audit timestamp captured when summary evidence is written. |
| `status` | Overall pipeline status recorded by the notebook. |
| `source_count` | Number of registered source DataFrames. |
| `target_count` | Number of registered target DataFrames. |
| `source_guardrail_status` | Roll-up status for source schema and profile behavior guardrails. |
| `target_guardrail_status` | Roll-up status for target schema and profile behavior guardrails. |
| `dq_status` | Roll-up status for source and target DQ guardrails. |
| `lineage_status` | Status returned by lineage evidence writing. |
| `catalogue_status` | Status returned by catalogue evidence writing. |
| `message` | Human-readable run note. |
| `run_summary_json` | JSON payload with guardrail results and source/target table lists. |
| `created_at` | Audit timestamp when the metadata row was created. |

### `METADATA_DATA_ACCESS`

**For:** optional table-level access assignments when a team chooses to capture them. This table is documented for the metadata model but is not part of the current 11-table `00_env_config` setup registry.

| Column | Purpose |
| --- | --- |
| `user_principal` | User or group receiving access. |
| `table_id` | Stable table identifier from the catalogue. |
| `table_name` | Human-readable table name. |
| `access_level` | Assigned access level. |
| `granted_date` | Date access was granted. |
| `expiry_date` | Optional access expiry date. |
| `active` | Whether the access assignment is currently active. |

**Workflow connection:** one catalogue table can have many access-assignment rows. Includes the standard runtime audit columns.

### `METADATA_COLUMN_CONTEXT`

**For:** human-reviewed business context for catalogue columns, written by `03_governance`.

| Column | Purpose |
| --- | --- |
| `metadata_column_key` | Stable catalogue-column identifier. |
| `environment_name` | Environment context. |
| `dataset_name` | Dataset context. |
| `table_name` | Selected catalogue table. |
| `column_name` | Selected catalogue column. |
| `business_context` | Human-approved business meaning. |
| `notes` | Reviewer notes. |
| `review_status` | Review state. |
| `ai_suggestion_json` | Optional AI suggestion retained for traceability. |

**Workflow connection:** AI suggestions are advisory. A person must approve reviewed metadata before it is treated as trusted context. Includes the standard runtime audit columns.

### `METADATA_GUARDRAIL_RULES`

**For:** approved or proposed guardrail rules written by governance and consumed by runtime guardrails. This table generalizes the pre-cutover `METADATA_DQ_RULES` model so one rules table can describe `schema`, `freshness`, `profile_behavior`, and `dq` expectations. Supported `review_status` values include `draft`, `proposed`, `engineer_approved`, `governance_approved`, `rejected`, `superseded`, and `inactive`.

Supported `guardrail_type` values are `schema`, `freshness`, `profile_behavior`, and `dq`.

| Column | Purpose |
| --- | --- |
| `rule_key` | Stable generated rule key. |
| `rule_id` | Human-readable rule identifier. |
| `metadata_table_key` | Stable table identifier for table-wide rules. |
| `metadata_column_key` | Stable column identifier where applicable. |
| `table_name` | Selected table. |
| `column_name` | Selected column where applicable. |
| `guardrail_type` | Guardrail family: `schema`, `freshness`, `profile_behavior`, or `dq`. |
| `rule_type` | Specific rule type within the guardrail family. |
| `threshold` | Optional warning or failure threshold. |
| `severity` | Rule severity. |
| `description` | Human-readable rule description. |
| `allowed_values` | Optional accepted values. |
| `min_value` | Optional minimum value stored inside `rule_parameters_json`. |
| `max_value` | Optional maximum value stored inside `rule_parameters_json`. |
| `regex_pattern` | Optional regular expression. |
| `review_status` | Review state, such as `draft`, `proposed`, `engineer_approved`, `governance_approved`, `rejected`, `superseded`, or `inactive`. |
| `is_active` | Active rule state. |
| `action_type` | Lifecycle action. |
| `action_by` | User generated by the rule workflow. |
| `created_at` | Rule proposal/create timestamp. |
| `approved_at` | Approval timestamp when applicable. |
| `action_reason` | Reason for the action. |
| `source_notebook_type` | Notebook/workflow type that proposed the rule. |
| `source_notebook_id` | Source notebook identifier when available. |
| `source_workspace_id` | Source workspace identifier when available. |
| `superseded_by_rule_key` | Replacement rule key when this rule is superseded. |

**Workflow connection:** approved active `profile_behavior` expectations tell `02_pipeline` whether to compare the full table (`rule_type="static_data"`) or watermark groups (`rule_type="changing_data"`). Approved active `dq` expectations become runtime DQ guardrails when `02_pipeline` calls `enforce_dq_rules`. `enforce_dq_rules` reads `METADATA_GUARDRAIL_RULES` only and enforces active approved rows with `guardrail_type="dq"`. Includes the standard runtime audit columns.

### `METADATA_GUARDRAIL_RESULTS`

**For:** pass/fail outcomes: what passed, warned, failed, or blocked continuation. For profile behavior, this is the runtime outcome while `METADATA_DATA_CATALOGUE` remains the profile history and baseline source. Key fields include `result_id`, `run_id`, `rule_key`, `environment_name`, `dataset_name`, `table_name`, `column_name`, `guardrail_type`, `rule_type`, `status`, `can_continue`, `severity`, `reason`, `expected_value_json`, `actual_value_json`, `result_payload_json`, and `created_at`.

### `METADATA_DQ_RULES`

**For:** obsolete pre-cutover DQ metadata only. It is not part of the active setup registry, and runtime DQ enforcement no longer reads it. Migrate any needed approved rules into `METADATA_GUARDRAIL_RULES` with `guardrail_type="dq"` before relying on them in new runs.

### `METADATA_COLUMN_CLASSIFICATION`

**For:** human-reviewed sensitivity and PII decisions, written by `03_governance`.

| Column | Purpose |
| --- | --- |
| `metadata_table_key` | Stable selected-table identifier. |
| `metadata_column_key` | Stable selected-column identifier. |
| `environment_name` | Environment context. |
| `dataset_name` | Dataset context. |
| `table_name` | Selected table. |
| `column_name` | Selected column. |
| `ai_suggested_personal_identifier_classification` | Optional AI suggestion. |
| `approved_personal_identifier_classification` | Human-approved PII classification. |
| `confidentiality_label` | Human-approved sensitivity label. |
| `handling_requirement` | Approved handling instruction. |
| `masking_requirement` | Approved masking instruction where applicable. |
| `reviewer_notes` | Human reviewer notes. |
| `approval_status` | Review state. |
| `ai_suggestion_json` | Optional full AI suggestion payload. |

**Workflow connection:** classification supports review and support visibility. It does not enforce masking or access behavior unless a later `02_pipeline` or access process is built to use it. Includes the standard runtime audit columns.

### `METADATA_GOVERNANCE_REVIEWS`

**For:** final `03_governance` outcome rows that summarize whether a selected catalogue profile is approved, rejected, or needs remediation.

| Column | Purpose |
| --- | --- |
| `review_id` | Unique review-event identifier for the final governance outcome row. |
| `environment_name` | Environment key reviewed by `03_governance`. |
| `dataset_name` | Dataset associated with the selected catalogue profile. |
| `table_name` | Table associated with the selected catalogue profile. |
| `metadata_table_key` | Stable catalogue table key tying the outcome to profile and review evidence. |
| `profile_run_id` | Pipeline/profile run identifier selected from `METADATA_DATA_CATALOGUE`. |
| `profile_stage` | Profile stage reviewed, such as source or target. |
| `pipeline_run_id` | Pipeline run summary identifier from `METADATA_PIPELINE_RUNS`. |
| `agreement_id` | Agreement identifier linked through the catalogue and pipeline evidence. |
| `agreement_contract_version` | Agreement version reviewed for the outcome. |
| `outcome` | Final governance decision, such as `approved`, `rejected`, or `needs_remediation`. |
| `blocker_count` | Number of blocking findings that prevent approval. |
| `warning_count` | Number of non-blocking warnings that require remediation review or follow-up. |
| `blockers_json` | JSON array of blocker codes and messages, including missing agreement evidence or failed DQ evidence. |
| `warnings_json` | JSON array of warning codes and messages, including warning DQ or surfaced schema/profile behavior findings. |
| `evidence_summary_json` | JSON summary of agreement rows, agreement evidence, profile column counts, prior runs, and latest pipeline evidence used for the decision. |
| `reviewed_at` | UTC timestamp when the outcome row was written. |
| `reviewed_by` | Reviewer identity resolved from the runtime or explicit reviewer input. |

**Workflow connection:** `03_governance` writes one outcome row after reading metadata from the configured metadata lakehouse instead of relying on copied notebook-local state from `02_pipeline`. The row links the agreement version, pipeline run, selected catalogue profile, blocker and warning details, and reviewed evidence summary so support teams can understand why the output was approved, rejected, or marked as needing remediation. Includes the standard runtime audit columns.


Continue to [Metadata Dashboard](metadata-dashboard.md) to see the planned visibility layer over this metadata evidence.
