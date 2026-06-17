# Metadata tables

FabricOps metadata tables are governed evidence tables stored in the configured `metadata` target from `00_env_config`. The active metadata table registry is prepared by [setup_metadata_tables](../api/reference/setup_metadata_tables/), which calls `_get_metadata_table_schema_registry` and then creates or validates every registered table through the configured metadata route. Setup creates or validates empty schemas; it does not populate business rows.

The setup registry combines agreement tables from `DataAgreementConfig`, notebook registration fields from `NOTEBOOK_REGISTRY_FIELDS`, and governance tables from `_get_governance_metadata_schemas`. Agreement and notebook registry tables are all `string` columns because `_string_metadata_schema` wraps every listed field in `StringType`; governance tables use the explicit Spark types declared by `_get_governance_metadata_schemas`.

> **Maintenance note:** When metadata schemas change, update this page from the same setup registry used by `setup_metadata_tables`. Do not document optional or planned tables unless they are part of `_get_metadata_table_schema_registry`.

## Conceptual overview

The metadata model still has four simple groups: agreement and context, observed catalogue/profile evidence, governance rules, and runtime execution evidence. This page is primarily the physical table dictionary for the active setup registry, so each section below lists the columns that setup creates or validates.

## Architecture

![Shared FabricOps metadata model connecting governance and engineering notebooks](../assets/fabricops-metadata-model.png){ .full-width }

## Summary table

| Metadata table | Purpose | Main writer or producer | Main consumer |
| --- | --- | --- | --- |
| `METADATA_DATA_STEWARD` | Steward identities, contacts, roles, active windows, and audit context used by agreements. | `widget_render_data_steward → _create_or_update_data_steward` | Agreement intake |
| `METADATA_DATA_AGREEMENT` | Versioned business agreement records and approved usage context selected by notebooks. | `widget_render_data_agreement → _create_or_update_data_agreement` | Notebook registration and governance context |
| `METADATA_DATA_AGREEMENT_EVIDENCE` | File-reference evidence that supports one agreement version. | `widget_render_agreement_evidence → _save_agreement_evidence_records` | Governance readiness |
| `METADATA_NOTEBOOK_REGISTRY` | Notebook-to-agreement registration events used to prove which notebook is operating under which agreement. | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | Pipeline/governance context |
| `METADATA_DATA_CATALOGUE` | Observed physical/profile evidence for tables and columns, plus table governance policy context. | `run_table_guardrails → write_catalogue_evidence` | Governance selectors and readiness checks |
| `METADATA_ENRICHMENT_RULES` | Reviewed enrichment intent for business meaning, ownership, classification, sensitivity, and usage context. | `record_table_governance → build_enrichment_rule_records` | Governance review and handover |
| `METADATA_GUARDRAIL_RULES` | Approved schema, freshness, profile behavior, and DQ rule intent for enforcement. | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | Pipeline enforcement |
| `METADATA_GUARDRAIL_RESULTS` | Runtime outcomes from executed guardrail/DQ checks. | `run_table_guardrails / enforce_dq_rules(write_results=True) → _write_guardrail_result_row` | Readiness checks and runtime evidence review |
| `METADATA_DATA_LINEAGE_TABLE` | Run-specific source-to-target lineage evidence. | [write_pipeline_lineage](../api/reference/write_pipeline_lineage/) | Readiness checks and handover |
| `METADATA_PIPELINE_RUNS` | One-row runtime summary for a pipeline execution. | `write_pipeline_run_summary` | Governance readiness |
| `METADATA_DATA_ACCESS` | Public-safe access context table included in setup; standard notebooks do not currently populate it. | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | Manual/offline access review |

## Physical table dictionary

### `METADATA_DATA_STEWARD`

Steward identities, contacts, roles, active windows, and audit context used by agreements.

| Column | Data type | Written by | Why it exists |
| --- | --- | --- | --- |
| `steward_id` | string | `_generate_steward_id` | identity key |
| `steward_name` | string | `widget_render_data_steward → _create_or_update_data_steward` | business intake field |
| `steward_role` | string | `widget_render_data_steward → _create_or_update_data_steward` | business intake field |
| `contact` | string | `widget_render_data_steward → _create_or_update_data_steward` | business intake field |
| `effective_from` | string | `widget_render_data_steward → _create_or_update_data_steward` | version tracking |
| `effective_to` | string | `widget_render_data_steward → _create_or_update_data_steward` | version tracking |
| `is_active` | string | `widget_render_data_steward → _create_or_update_data_steward` | rule lifecycle |
| `custom_fields_json` | string | `widget_render_data_steward → _create_or_update_data_steward` | business intake field |
| `_committed_by` | string | `_build_runtime_audit_fields` | runtime audit |
| `_committed_at` | string | `_build_runtime_audit_fields` | runtime audit |
| `_notebook_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_workspace_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_metadata_lakehouse_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_activity_id` | string | `_build_runtime_audit_fields` | runtime audit |

### `METADATA_DATA_AGREEMENT`

Versioned business agreement records and approved usage context selected by notebooks.

| Column | Data type | Written by | Why it exists |
| --- | --- | --- | --- |
| `agreement_id` | string | `_generate_agreement_id` | identity key |
| `contract_version` | string | `_next_minor_version` | version tracking |
| `agreement_name` | string | `widget_render_data_agreement → _create_or_update_data_agreement` | business intake field |
| `domain` | string | `widget_render_data_agreement → _create_or_update_data_agreement` | business intake field |
| `steward_id` | string | `widget_render_data_agreement → _create_or_update_data_agreement` | identity key |
| `recipient` | string | `widget_render_data_agreement → _create_or_update_data_agreement` | business intake field |
| `start_date` | string | `widget_render_data_agreement → _create_or_update_data_agreement` | business intake field |
| `expiry_date` | string | `widget_render_data_agreement → _create_or_update_data_agreement` | business intake field |
| `business_purpose` | string | `widget_render_data_agreement → _create_or_update_data_agreement` | business intake field |
| `approved_usage_internal` | string | `widget_render_data_agreement → _create_or_update_data_agreement` | business intake field |
| `approved_usage_external` | string | `widget_render_data_agreement → _create_or_update_data_agreement` | business intake field |
| `approved_usage_research` | string | `widget_render_data_agreement → _create_or_update_data_agreement` | business intake field |
| `custom_fields_json` | string | `widget_render_data_agreement → _create_or_update_data_agreement` | business intake field |
| `_committed_by` | string | `_build_runtime_audit_fields` | runtime audit |
| `_committed_at` | string | `_build_runtime_audit_fields` | runtime audit |
| `_notebook_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_workspace_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_metadata_lakehouse_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_activity_id` | string | `_build_runtime_audit_fields` | runtime audit |

### `METADATA_DATA_AGREEMENT_EVIDENCE`

File-reference evidence that supports one agreement version.

| Column | Data type | Written by | Why it exists |
| --- | --- | --- | --- |
| `agreement_id` | string | `widget_render_agreement_evidence → _save_agreement_evidence_records` | identity key |
| `contract_version` | string | `widget_render_agreement_evidence → _save_agreement_evidence_records` | version tracking |
| `evidence_type` | string | `widget_render_agreement_evidence → _save_agreement_evidence_records` | business intake field |
| `file_name` | string | `widget_render_agreement_evidence → _save_agreement_evidence_records` | business intake field |
| `file_path` | string | `widget_render_agreement_evidence → _save_agreement_evidence_records` | business intake field |
| `mime_type` | string | `widget_render_agreement_evidence → _save_agreement_evidence_records` | business intake field |
| `file_size` | string | `widget_render_agreement_evidence → _save_agreement_evidence_records` | business intake field |
| `uploaded_at` | string | `widget_render_agreement_evidence → _save_agreement_evidence_records` | business intake field |
| `uploaded_by` | string | `widget_render_agreement_evidence → _save_agreement_evidence_records` | business intake field |
| `_committed_by` | string | `_build_runtime_audit_fields` | runtime audit |
| `_committed_at` | string | `_build_runtime_audit_fields` | runtime audit |
| `_notebook_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_workspace_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_metadata_lakehouse_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_activity_id` | string | `_build_runtime_audit_fields` | runtime audit |

### `METADATA_NOTEBOOK_REGISTRY`

Notebook-to-agreement registration events used to prove which notebook is operating under which agreement.

| Column | Data type | Written by | Why it exists |
| --- | --- | --- | --- |
| `agreement_id` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | identity key |
| `environment_name` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | lineage traceability |
| `dataset_name` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | lineage traceability |
| `table_name` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | lineage traceability |
| `topic` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | business intake field |
| `pipeline_name` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | lineage traceability |
| `notebook_type` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | business intake field |
| `workspace_id` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | identity key |
| `workspace_name` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | business intake field |
| `notebook_id` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | identity key |
| `notebook_name` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | business intake field |
| `notebook_url` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | business intake field |
| `user_name` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | business intake field |
| `user_id` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | identity key |
| `registered_at` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | business intake field |
| `registration_id` | string | `_notebook_registration_key` | identity key |
| `agreement_contract_version` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | version tracking |
| `registration_role` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | business intake field |
| `registration_status` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | business intake field |
| `superseded_at` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | version tracking |
| `superseded_by_registration_id` | string | `widget_select_agreement(register_notebook=True) → _register_current_notebook` | identity key |

### `METADATA_DATA_CATALOGUE`

Observed physical/profile evidence for tables and columns, plus table governance policy context.

| Column | Data type | Written by | Why it exists |
| --- | --- | --- | --- |
| `metadata_table_key` | string | `_build_metadata_table_key` | identity key |
| `metadata_column_key` | string | `_build_metadata_column_key` | identity key |
| `environment_name` | string | `run_table_guardrails → write_catalogue_evidence` | lineage traceability |
| `dataset_name` | string | `run_table_guardrails → write_catalogue_evidence` | lineage traceability |
| `table_name` | string | `run_table_guardrails → write_catalogue_evidence` | lineage traceability |
| `column_name` | string | `run_table_guardrails → write_catalogue_evidence` | lineage traceability |
| `layer` | string | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `asset_kind` | string | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `pipeline_name` | string | `run_table_guardrails → write_catalogue_evidence` | lineage traceability |
| `profile_run_id` | string | `run_table_guardrails → write_catalogue_evidence` | identity key |
| `profile_stage` | string | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `profile_status` | string | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `profiled_at` | string | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `run_timestamp` | timestamp | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `evidence_role` | string | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `data_type` | string | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `row_count` | long | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `null_count` | long | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `null_percent` | double | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `distinct_count` | long | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `distinct_percent` | double | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `min_value` | string | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `max_value` | string | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `distribution_type` | string | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `distribution_json` | string | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `profile_mode` | string | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `watermark_column` | string | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `watermark_value` | string | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `profile_hash` | string | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `profile_payload_json` | string | `run_table_guardrails → write_catalogue_evidence` | schema/profile evidence |
| `governance_mode` | string | `run_table_guardrails → write_catalogue_evidence` | governance policy |
| `approval_policy` | string | `run_table_guardrails → write_catalogue_evidence` | governance policy |
| `bypass_allowed` | boolean | `run_table_guardrails → write_catalogue_evidence` | governance policy |
| `policy_reason` | string | `run_table_guardrails → write_catalogue_evidence` | governance policy |
| `policy_updated_by` | string | `run_table_guardrails → write_catalogue_evidence` | governance policy |
| `policy_updated_at` | string | `run_table_guardrails → write_catalogue_evidence` | governance policy |
| `agreement_id` | string | `run_table_guardrails → write_catalogue_evidence` | identity key |
| `contract_version` | string | `run_table_guardrails → write_catalogue_evidence` | version tracking |
| `notebook_registry_id` | string | `run_table_guardrails → write_catalogue_evidence` | identity key |
| `notebook_id` | string | `run_table_guardrails → write_catalogue_evidence` | identity key |
| `_committed_at` | string | `_build_runtime_audit_fields` | runtime audit |
| `_committed_by` | string | `_build_runtime_audit_fields` | runtime audit |
| `_workspace_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_notebook_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_metadata_lakehouse_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_activity_id` | string | `_build_runtime_audit_fields` | runtime audit |

### `METADATA_ENRICHMENT_RULES`

Reviewed enrichment intent for business meaning, ownership, classification, sensitivity, and usage context.

| Column | Data type | Written by | Why it exists |
| --- | --- | --- | --- |
| `enrichment_rule_id` | string | `record_table_governance → build_enrichment_rule_records` | identity key |
| `enrichment_rule_version` | string | `record_table_governance → build_enrichment_rule_records` | version tracking |
| `enrichment_rule_key` | string | `record_table_governance → build_enrichment_rule_records` | identity key |
| `metadata_table_key` | string | `_build_metadata_table_key` | identity key |
| `metadata_column_key` | string | `_build_metadata_column_key` | identity key |
| `table_name` | string | `record_table_governance → build_enrichment_rule_records` | lineage traceability |
| `column_name` | string | `record_table_governance → build_enrichment_rule_records` | lineage traceability |
| `enrichment_scope` | string | `record_table_governance → build_enrichment_rule_records` | business intake field |
| `enrichment_type` | string | `record_table_governance → build_enrichment_rule_records` | business intake field |
| `enrichment_payload_json` | string | `record_table_governance → build_enrichment_rule_records` | business intake field |
| `business_name` | string | `record_table_governance → build_enrichment_rule_records` | business intake field |
| `business_description` | string | `record_table_governance → build_enrichment_rule_records` | business intake field |
| `business_meaning` | string | `record_table_governance → build_enrichment_rule_records` | business intake field |
| `column_description` | string | `record_table_governance → build_enrichment_rule_records` | business intake field |
| `classification` | string | `record_table_governance → build_enrichment_rule_records` | business intake field |
| `sensitivity_label` | string | `record_table_governance → build_enrichment_rule_records` | business intake field |
| `pii_flag` | boolean | `record_table_governance → build_enrichment_rule_records` | business intake field |
| `pii_type` | string | `record_table_governance → build_enrichment_rule_records` | business intake field |
| `data_domain` | string | `record_table_governance → build_enrichment_rule_records` | business intake field |
| `data_owner` | string | `record_table_governance → build_enrichment_rule_records` | business intake field |
| `data_steward` | string | `record_table_governance → build_enrichment_rule_records` | business intake field |
| `usage_notes` | string | `record_table_governance → build_enrichment_rule_records` | business intake field |
| `quality_notes` | string | `record_table_governance → build_enrichment_rule_records` | business intake field |
| `review_status` | string | `record_table_governance → build_enrichment_rule_records` | governance policy |
| `is_active` | boolean | `record_table_governance → build_enrichment_rule_records` | rule lifecycle |
| `approval_policy` | string | `record_table_governance → build_enrichment_rule_records` | governance policy |
| `governance_mode` | string | `record_table_governance → build_enrichment_rule_records` | governance policy |
| `submitted_by` | string | `record_table_governance → build_enrichment_rule_records` | governance policy |
| `submitted_at` | string | `record_table_governance → build_enrichment_rule_records` | governance policy |
| `reviewed_by` | string | `record_table_governance → build_enrichment_rule_records` | governance policy |
| `reviewed_at` | string | `record_table_governance → build_enrichment_rule_records` | governance policy |
| `review_decision` | string | `record_table_governance → build_enrichment_rule_records` | governance policy |
| `review_comment` | string | `record_table_governance → build_enrichment_rule_records` | governance policy |
| `bypass_reason` | string | `record_table_governance → build_enrichment_rule_records` | governance policy |
| `requires_post_review` | boolean | `record_table_governance → build_enrichment_rule_records` | governance policy |
| `supersedes_enrichment_rule_id` | string | `record_table_governance → build_enrichment_rule_records` | identity key |
| `effective_from` | string | `record_table_governance → build_enrichment_rule_records` | version tracking |
| `effective_to` | string | `record_table_governance → build_enrichment_rule_records` | version tracking |
| `created_at` | string | `record_table_governance → build_enrichment_rule_records` | lineage traceability |
| `created_by` | string | `record_table_governance → build_enrichment_rule_records` | runtime audit |
| `updated_at` | string | `record_table_governance → build_enrichment_rule_records` | runtime audit |
| `updated_by` | string | `record_table_governance → build_enrichment_rule_records` | runtime audit |
| `run_id` | string | `record_table_governance → build_enrichment_rule_records` | identity key |
| `notebook_id` | string | `record_table_governance → build_enrichment_rule_records` | identity key |
| `notebook_registry_id` | string | `record_table_governance → build_enrichment_rule_records` | identity key |
| `_committed_at` | string | `_build_runtime_audit_fields` | runtime audit |
| `_committed_by` | string | `_build_runtime_audit_fields` | runtime audit |
| `_workspace_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_notebook_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_metadata_lakehouse_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_activity_id` | string | `_build_runtime_audit_fields` | runtime audit |

### `METADATA_GUARDRAIL_RULES`

Approved schema, freshness, profile behavior, and DQ rule intent for enforcement.

| Column | Data type | Written by | Why it exists |
| --- | --- | --- | --- |
| `rule_key` | string | `_build_dq_rule_key` | identity key |
| `rule_id` | string | `_build_dq_rule_key` | identity key |
| `metadata_column_key` | string | `_build_metadata_column_key` | identity key |
| `metadata_table_key` | string | `_build_metadata_table_key` | identity key |
| `environment_name` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | lineage traceability |
| `dataset_name` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | lineage traceability |
| `table_name` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | lineage traceability |
| `column_name` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | lineage traceability |
| `guardrail_type` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | rule lifecycle |
| `rule_type` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | rule lifecycle |
| `rule_parameters_json` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | DQ enforcement parameter |
| `severity` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | DQ enforcement parameter |
| `description` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | rule lifecycle |
| `is_active` | boolean | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | rule lifecycle |
| `review_status` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | governance policy |
| `author_role` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | rule lifecycle |
| `created_by` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | runtime audit |
| `created_at` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | lineage traceability |
| `approved_by` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | governance policy |
| `approved_at` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | governance policy |
| `suggestion_json` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | runtime audit |
| `action_type` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | rule lifecycle |
| `source_notebook_type` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | rule lifecycle |
| `source_notebook_id` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | identity key |
| `source_workspace_id` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | identity key |
| `superseded_by_rule_key` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | identity key |
| `notes` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | rule lifecycle |
| `approval_required` | boolean | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | governance policy |
| `approval_bypassed` | boolean | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | governance policy |
| `requires_post_review` | boolean | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | governance policy |
| `bypass_reason` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | governance policy |
| `bypassed_by` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | governance policy |
| `bypassed_at` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | governance policy |
| `governance_mode` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | governance policy |
| `approval_policy` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | governance policy |
| `submitted_by` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | governance policy |
| `submitted_at` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | governance policy |
| `reviewed_by` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | governance policy |
| `reviewed_at` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | governance policy |
| `review_decision` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | governance policy |
| `review_comment` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | governance policy |
| `supersedes_rule_id` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | identity key |
| `effective_from` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | version tracking |
| `effective_to` | string | `record_table_governance → _build_dq_rule_records`; `widget_author_schema_freshness_profile_rules → _write_rule_records`; `widget_author_dq_rules → _write_rule_records` | version tracking |
| `_committed_at` | string | `_build_runtime_audit_fields` | runtime audit |
| `_committed_by` | string | `_build_runtime_audit_fields` | runtime audit |
| `_workspace_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_notebook_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_metadata_lakehouse_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_activity_id` | string | `_build_runtime_audit_fields` | runtime audit |

### `METADATA_GUARDRAIL_RESULTS`

Runtime outcomes from executed guardrail/DQ checks.

| Column | Data type | Written by | Why it exists |
| --- | --- | --- | --- |
| `result_id` | string | `run_table_guardrails / enforce_dq_rules(write_results=True) → _write_guardrail_result_row` | identity key |
| `run_id` | string | `run_table_guardrails / enforce_dq_rules(write_results=True) → _write_guardrail_result_row` | identity key |
| `rule_key` | string | `run_table_guardrails / enforce_dq_rules(write_results=True) → _write_guardrail_result_row` | identity key |
| `environment_name` | string | `run_table_guardrails / enforce_dq_rules(write_results=True) → _write_guardrail_result_row` | lineage traceability |
| `dataset_name` | string | `run_table_guardrails / enforce_dq_rules(write_results=True) → _write_guardrail_result_row` | lineage traceability |
| `table_name` | string | `run_table_guardrails / enforce_dq_rules(write_results=True) → _write_guardrail_result_row` | lineage traceability |
| `column_name` | string | `run_table_guardrails / enforce_dq_rules(write_results=True) → _write_guardrail_result_row` | lineage traceability |
| `guardrail_type` | string | `run_table_guardrails / enforce_dq_rules(write_results=True) → _write_guardrail_result_row` | rule lifecycle |
| `rule_type` | string | `run_table_guardrails / enforce_dq_rules(write_results=True) → _write_guardrail_result_row` | rule lifecycle |
| `status` | string | `run_table_guardrails / enforce_dq_rules(write_results=True) → _write_guardrail_result_row` | runtime result evidence |
| `can_continue` | boolean | `run_table_guardrails / enforce_dq_rules(write_results=True) → _write_guardrail_result_row` | runtime result evidence |
| `severity` | string | `run_table_guardrails / enforce_dq_rules(write_results=True) → _write_guardrail_result_row` | DQ enforcement parameter |
| `reason` | string | `run_table_guardrails / enforce_dq_rules(write_results=True) → _write_guardrail_result_row` | runtime result evidence |
| `expected_value_json` | string | `run_table_guardrails / enforce_dq_rules(write_results=True) → _write_guardrail_result_row` | runtime result evidence |
| `actual_value_json` | string | `run_table_guardrails / enforce_dq_rules(write_results=True) → _write_guardrail_result_row` | runtime result evidence |
| `result_payload_json` | string | `run_table_guardrails / enforce_dq_rules(write_results=True) → _write_guardrail_result_row` | runtime result evidence |
| `created_at` | string | `run_table_guardrails / enforce_dq_rules(write_results=True) → _write_guardrail_result_row` | lineage traceability |
| `_committed_at` | string | `_build_runtime_audit_fields` | runtime audit |
| `_committed_by` | string | `_build_runtime_audit_fields` | runtime audit |
| `_workspace_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_notebook_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_metadata_lakehouse_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_activity_id` | string | `_build_runtime_audit_fields` | runtime audit |

### `METADATA_DATA_LINEAGE_TABLE`

Run-specific source-to-target lineage evidence.

| Column | Data type | Written by | Why it exists |
| --- | --- | --- | --- |
| `lineage_id` | string | `write_pipeline_lineage` | identity key |
| `dataset_name` | string | `write_pipeline_lineage` | lineage traceability |
| `run_id` | string | `write_pipeline_lineage` | identity key |
| `source_table` | string | `write_pipeline_lineage` | lineage traceability |
| `target_table` | string | `write_pipeline_lineage` | lineage traceability |
| `source_table_key` | string | `_build_metadata_table_key` | identity key |
| `target_table_key` | string | `_build_metadata_table_key` | identity key |
| `transformation_steps_json` | string | `write_pipeline_lineage` | lineage traceability |
| `created_at` | string | `write_pipeline_lineage` | lineage traceability |
| `_committed_at` | string | `_build_runtime_audit_fields` | runtime audit |
| `_committed_by` | string | `_build_runtime_audit_fields` | runtime audit |
| `_workspace_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_notebook_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_metadata_lakehouse_name` | string | `_build_runtime_audit_fields` | runtime audit |
| `_activity_id` | string | `_build_runtime_audit_fields` | runtime audit |

### `METADATA_PIPELINE_RUNS`

One-row runtime summary for a pipeline execution.

| Column | Data type | Written by | Why it exists |
| --- | --- | --- | --- |
| `run_id` | string | `write_pipeline_run_summary` | identity key |
| `agreement_id` | string | `write_pipeline_run_summary` | identity key |
| `agreement_contract_version` | string | `write_pipeline_run_summary` | version tracking |
| `notebook_registry_id` | string | `write_pipeline_run_summary` | identity key |
| `notebook_id` | string | `write_pipeline_run_summary` | identity key |
| `notebook_type` | string | `write_pipeline_run_summary` | business intake field |
| `pipeline_name` | string | `write_pipeline_run_summary` | lineage traceability |
| `environment_name` | string | `write_pipeline_run_summary` | lineage traceability |
| `started_at` | string | `write_pipeline_run_summary` | runtime result evidence |
| `completed_at` | string | `write_pipeline_run_summary` | runtime result evidence |
| `status` | string | `write_pipeline_run_summary` | runtime result evidence |
| `source_count` | long | `write_pipeline_run_summary` | runtime result evidence |
| `target_count` | long | `write_pipeline_run_summary` | runtime result evidence |
| `source_guardrail_status` | string | `write_pipeline_run_summary` | runtime result evidence |
| `target_guardrail_status` | string | `write_pipeline_run_summary` | runtime result evidence |
| `dq_status` | string | `write_pipeline_run_summary` | runtime result evidence |
| `lineage_status` | string | `write_pipeline_run_summary` | runtime result evidence |
| `catalogue_status` | string | `write_pipeline_run_summary` | runtime result evidence |
| `message` | string | `write_pipeline_run_summary` | runtime result evidence |
| `run_summary_json` | string | `write_pipeline_run_summary` | runtime result evidence |
| `created_at` | string | `write_pipeline_run_summary` | lineage traceability |

### `METADATA_DATA_ACCESS`

Public-safe access context table included in setup; standard notebooks do not currently populate it.

| Column | Data type | Written by | Why it exists |
| --- | --- | --- | --- |
| `user_principal` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | access context |
| `role_name` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | access context |
| `permission` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | access context |
| `access_purpose` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | access context |
| `approval_status` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | access context |
| `access_scope` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | access context |
| `table_id` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | identity key |
| `metadata_table_key` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | identity key |
| `metadata_column_key` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | identity key |
| `granted_date` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | access context |
| `expires_at` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | access context |
| `approved_by` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | governance policy |
| `approved_at` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | governance policy |
| `notes` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | rule lifecycle |
| `_committed_at` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | runtime audit |
| `_committed_by` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | runtime audit |
| `_workspace_name` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | runtime audit |
| `_notebook_name` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | runtime audit |
| `_metadata_lakehouse_name` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | runtime audit |
| `_activity_id` | string | No standard starter-kit writer found; setup_metadata_tables creates or validates the empty schema only | runtime audit |
