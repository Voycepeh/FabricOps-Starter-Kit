# Metadata tables

FabricOps metadata tables are governed evidence tables stored in the configured `metadata` target from `00_env_config`. Workflow notebooks should read and write them through the shared Lakehouse IO helpers, not through an attached/default Lakehouse.

Run the optional `setup_metadata_tables` block in `00_env_config` once per environment, and rerun it only after active metadata schema changes. Setup creates or validates active metadata tables through the configured metadata target, supports classic Lakehouse paths and schema-enabled Lakehouse paths, validates missing columns, and warns about legacy nested metadata Delta folders such as `Tables/<metadata_table>/Unidentified/_delta_log`.

`METADATA_DATA_ACCESS` is part of the active public-safe metadata model for access context.

## Runtime routing

Classic and schema-enabled Lakehouses are both supported:

- **Classic Lakehouses:** metadata tables are written under `Tables/<table_name>` when no metadata schema is configured.
- **Schema-enabled Lakehouses:** metadata tables are written under `Tables/<schema>/<table_name>` when the configured metadata target has a schema such as `dbo`.

Use configured metadata routing for metadata operations:

```python
read_lakehouse_table(CONFIG, env_name, "metadata", "<metadata_table>")
write_lakehouse_table(df, CONFIG, env_name, "metadata", "<metadata_table>", mode="append")
```

## Architecture

![Shared FabricOps metadata model connecting governance and engineering notebooks](../assets/fabricops-metadata-model.svg){ .full-width }

The architecture image shows the high-level metadata coordination pattern across agreement, pipeline, governance, and runtime evidence. The active metadata table map below lists the implemented table ownership used by the starter kit. Relationships described on this page are logical joins used by notebooks, helpers, dashboards, and reviews.

## Active metadata table map

| Metadata table | Main writer | Contains |
| --- | --- | --- |
| `METADATA_DATA_STEWARD` | `01_agreement` | Steward identities and active periods. |
| `METADATA_DATA_AGREEMENT` | `01_agreement` | Versioned agreements and approved usage context. |
| `METADATA_DATA_AGREEMENT_EVIDENCE` | `01_agreement` | Supporting agreement evidence file references. |
| `METADATA_NOTEBOOK_REGISTRY` | `02_pipeline`, optional `99_explore` | Notebook-to-agreement registrations. |
| `METADATA_DATA_CATALOGUE` | `02_pipeline` | Observed table/profile evidence plus current table governance policy fields. |
| `METADATA_DATA_LINEAGE_TABLE` | `02_pipeline` | Source-to-target lineage rows for pipeline runs. |
| `METADATA_PIPELINE_RUNS` | `02_pipeline` | One runtime summary row per pipeline run. |
| `METADATA_ENRICHMENT_RULES` | `03_governance` and optional `02_pipeline` authoring | Reviewable enrichment intent for business context, descriptions, classification, sensitivity, PII, ownership, usage, and quality notes. |
| `METADATA_GUARDRAIL_RULES` | `03_governance` | Proposed or approved schema, freshness, profile-behavior, and DQ guardrail rules. |
| `METADATA_GUARDRAIL_RESULTS` | Pipeline guardrail runtime | Pass, warn, fail, and continuation outcomes for guardrail checks. |

The active table map intentionally excludes planned, project-specific, or manually collected metadata that is not currently written by the standard notebooks. For schema, freshness, profile behavior, and DQ evidence flow, see [Pipeline Guardrails](pipeline-guardrails.md).

## Offline and manually collected access metadata

`METADATA_DATA_ACCESS` stores public-safe access context. The starter kit records it as active metadata context but does not enforce access decisions from this table yet.

| Table name | Status | Description | Relationship |
| --- | --- | --- | --- |
| `METADATA_DATA_ACCESS` | Offline governance input; not currently written by `01_agreement`, `02_pipeline`, or `03_governance`. | Stores user, role, permission, access purpose, approval status, and access scope linked to governed catalogue entries. | `METADATA_DATA_CATALOGUE` 1 to many `METADATA_DATA_ACCESS`. |

One catalogue entry can have many access records because access decisions may differ by user, group, role, purpose, or approval period. Treat the relationship as a logical governance relationship for collection and reporting, not as a Fabric-enforced database constraint.

## Writer ownership

FabricOps writers follow the same ownership rule in functions, notebooks, and widgets:

| Writer group | Destination table | Writes | Must not write |
| --- | --- | --- | --- |
| Catalogue writers | `METADATA_DATA_CATALOGUE` | Observed physical/profile evidence, including profile rows, profile hashes, profile payloads, profile modes, watermark columns, and watermark values generated from pipeline profiling. | Guardrail rules, approval intent, schema/freshness/DQ/stability pass-fail summaries, or runtime continuation decisions. |
| Rule writers | `METADATA_GUARDRAIL_RULES` | Proposed or approved guardrail intent, including schema expectations, freshness rules, profile-behavior rules, and DQ rules. Governance review and rule approval widgets belong in this group. | Observed profile rows or runtime pass/fail outcomes. |
| Result writers | `METADATA_GUARDRAIL_RESULTS` | Runtime outcomes from executed guardrails, including schema, freshness, profile behavior, and DQ status, severity, continuation decisions, reasons, and expected/actual payloads. | Physical profile evidence or proposed/approved rule definitions. |

Widgets follow the same split. `widget_select_guardrail_target` is catalogue-based and reads `METADATA_DATA_CATALOGUE`; target DataFrames become selectable after profiling/catalogue evidence exists, even before or independently of physical target table existence. `widget_enrich_table_metadata` writes enrichment intent to `METADATA_ENRICHMENT_RULES`. A widget that proposes, approves, supersedes, or deactivates guardrail rules writes those rule events to `METADATA_GUARDRAIL_RULES`. Approval logs are derived from append-only rows in the enrichment and guardrail rule tables. A widget or dashboard that displays latest execution status reads `METADATA_GUARDRAIL_RESULTS` rather than deriving pass/fail state from catalogue rows. Runtime enforcement writes `METADATA_GUARDRAIL_RESULTS` from `02_pipeline`, not from `03_governance`.

## Standard runtime audit columns

Most metadata tables include the shared runtime audit columns below. They are generated by the shared runtime audit helper and are not repeated in every table section.

- `_committed_by`
- `_committed_at`
- `_notebook_name`
- `_workspace_name`
- `_metadata_lakehouse_name`
- `_activity_id`

## Logical keys

Fabric Delta tables do not enforce primary keys, but FabricOps uses logical keys for joins, latest-record selection, and validation.

| Metadata table | Logical key | Main relationship |
| --- | --- | --- |
| `METADATA_DATA_STEWARD` | `steward_id` | Referenced by agreement rows. |
| `METADATA_DATA_AGREEMENT` | `agreement_id`, `contract_version` | References a steward. |
| `METADATA_DATA_AGREEMENT_EVIDENCE` | `agreement_id`, `contract_version`, `file_path` | References one agreement version. |
| `METADATA_NOTEBOOK_REGISTRY` | `registration_id` | Links notebooks to agreement versions. |
| `METADATA_DATA_CATALOGUE` | `profile_run_id`, `profile_stage`, `metadata_table_key`, `metadata_column_key` | Feeds reviews, profile comparisons, and lineage joins without storing runtime outcomes. |
| `METADATA_DATA_LINEAGE_TABLE` | `lineage_id` | Links one source table to one target table in a run. |
| `METADATA_PIPELINE_RUNS` | `run_id` | Links runtime summaries to agreement, notebook, lineage, catalogue, and guardrail evidence. |
| `METADATA_ENRICHMENT_RULES` | `enrichment_rule_id`, `table_key`, `column_key`, `_committed_at` | Stores append-only enrichment intent for a table or column. |
| `METADATA_GUARDRAIL_RULES` | `rule_key`, `_committed_at` | Defines reviewed expectations for a table or column. |
| `METADATA_GUARDRAIL_RESULTS` | `result_id` | Records a runtime outcome for a rule, run, table, and optional column. |
| `METADATA_DATA_ACCESS` | `user_principal`, `table_id`, `granted_date` | Active access-capture context metadata. |

`metadata_table_key` identifies a profiled table. `metadata_column_key` identifies a profiled column within that table; catalogue evidence currently writes it as `metadata_table_key + "::" + column_name`.

## Table groups and implemented fields

### Agreement intake tables

`METADATA_DATA_STEWARD` fields:

- `steward_id`, `steward_name`, `steward_role`, `contact`, `effective_from`, `effective_to`, `is_active`, `custom_fields_json`
- Standard runtime audit columns

`METADATA_DATA_AGREEMENT` fields:

- `agreement_id`, `contract_version`, `agreement_name`, `domain`, `steward_id`, `recipient`, `start_date`, `expiry_date`, `business_purpose`, `approved_usage_internal`, `approved_usage_external`, `approved_usage_research`, `custom_fields_json`
- Standard runtime audit columns

`METADATA_DATA_AGREEMENT_EVIDENCE` fields:

- `agreement_id`, `contract_version`, `evidence_type`, `file_name`, `file_path`, `mime_type`, `file_size`, `uploaded_at`, `uploaded_by`
- Standard runtime audit columns

### Notebook registry

`METADATA_NOTEBOOK_REGISTRY` fields:

- Agreement and dataset context: `agreement_id`, `agreement_contract_version`, `environment_name`, `dataset_name`, `table_name`, `topic`, `pipeline_name`
- Notebook context: `notebook_type`, `workspace_id`, `workspace_name`, `notebook_id`, `notebook_name`, `notebook_url`
- Registration state: `registration_id`, `registration_role`, `registration_status`, `registered_at`, `superseded_at`, `superseded_by_registration_id`
- User context: `user_name`, `user_id`

### Pipeline evidence tables

`METADATA_DATA_CATALOGUE` fields include observed physical/profile evidence only:

- Identity and context: `metadata_table_key`, `metadata_column_key`, `environment_name`, `dataset_name`, `table_name`, `column_name`, `layer`, `asset_kind`, `pipeline_name`
- Profile run state: `profile_run_id`, `profile_stage`, `profile_status`, `profiled_at`, `run_timestamp`, `evidence_role`
- Profile metrics: `data_type`, `row_count`, `null_count`, `null_percent`, `distinct_count`, `distinct_percent`, `min_value`, `max_value`, `distribution_type`, `distribution_json`
- Profile behavior evidence: `profile_mode`, `watermark_column`, `watermark_value`, `profile_hash`, `profile_payload_json`
- Agreement and notebook context: `agreement_id`, `contract_version`, `notebook_registry_id`, `notebook_id`
- Standard runtime audit columns

Schema, freshness, profile-behavior pass/fail, stability, and DQ outcomes are runtime results and belong in `METADATA_GUARDRAIL_RESULTS`, not in the catalogue.

`METADATA_DATA_LINEAGE_TABLE` fields:

- `lineage_id`, `dataset_name`, `run_id`, `source_table`, `target_table`, `source_table_key`, `target_table_key`, `transformation_steps_json`, `created_at`
- Standard runtime audit columns

`METADATA_PIPELINE_RUNS` fields:

- `run_id`, `agreement_id`, `agreement_contract_version`, `notebook_registry_id`, `notebook_id`, `notebook_type`, `pipeline_name`, `environment_name`, `started_at`, `completed_at`, `status`, `source_count`, `target_count`, `source_guardrail_status`, `target_guardrail_status`, `dq_status`, `lineage_status`, `catalogue_status`, `message`, `run_summary_json`, `created_at`

### Governance review tables

`METADATA_ENRICHMENT_RULES` fields:

- Identity and scope: `enrichment_rule_id`, `table_key`, `column_key`, `workspace_name`, `lakehouse_name`, `schema_name`, `table_name`, `column_name`, `enrichment_scope`, `enrichment_type`
- Payload: `enrichment_payload_json`, `business_name`, `business_description`, `business_meaning`, `column_description`, `classification`, `sensitivity_label`, `pii_flag`, `pii_type`, `data_domain`, `data_owner`, `data_steward`, `usage_notes`, `quality_notes`
- Shared lifecycle: `rule_status`, `review_status`, `is_active`, `approval_policy`, `governance_mode`, `submitted_by`, `submitted_at`, `reviewed_by`, `reviewed_at`, `review_decision`, `review_comment`, `bypass_reason`, `requires_post_review`, `supersedes_enrichment_rule_id`, `effective_from`, `effective_to`
- Audit and traceability: `created_at`, `created_by`, `updated_at`, `updated_by`, `run_id`, `notebook_id`, `notebook_registry_id`
- Standard runtime audit columns

`METADATA_GUARDRAIL_RULES` fields:

- `rule_key`, `rule_id`, `metadata_column_key`, `metadata_table_key`, `environment_name`, `dataset_name`, `table_name`, `column_name`, `guardrail_type`, `rule_type`, `rule_parameters_json`, `severity`, `description`, `is_active`, `review_status`, `author_role`, `created_by`, `created_at`, `approved_by`, `approved_at`, `ai_suggestion_json`, `action_type`, `source_notebook_type`, `source_notebook_id`, `source_workspace_id`, `superseded_by_rule_key`, `notes`
- Standard runtime audit columns

`METADATA_GUARDRAIL_RESULTS` fields:

- `result_id`, `run_id`, `rule_key`, `environment_name`, `dataset_name`, `table_name`, `column_name`, `guardrail_type`, `rule_type`, `status`, `can_continue`, `severity`, `reason`, `expected_value_json`, `actual_value_json`, `result_payload_json`, `created_at`
- Standard runtime audit columns

### Optional documented tables

`METADATA_DATA_ACCESS` is an offline/manual access governance table that may be used by a future or project-specific access-capture workflow. It stores user, role, permission, access purpose, approval status, and access scope linked to governed catalogue entries. `setup_metadata_tables` creates or validates it as part of the active metadata registry, but the starter kit does not enforce it yet.

## Callable references

- [setup_metadata_tables](../api/reference/setup_metadata_tables/) prepares the active metadata tables.
- [write_catalogue_evidence](../api/reference/write_catalogue_evidence/), [write_pipeline_lineage](../api/reference/write_pipeline_lineage/), and [write_pipeline_run_summary](../api/reference/write_pipeline_run_summary/) write pipeline evidence.
- Current governance widgets use configured metadata routing: catalogue-based selection reads `METADATA_DATA_CATALOGUE`, enrichment writes `METADATA_ENRICHMENT_RULES`, guardrail governance review writes `METADATA_GUARDRAIL_RULES`, and runtime enforcement in `02_pipeline` writes `METADATA_GUARDRAIL_RESULTS`.
