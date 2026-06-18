# Metadata Tables

Metadata tables are the shared memory of the FabricOps notebook handshake. `00_env_config` prepares the configured metadata target, `01_agreement` records approved context, `02_pipeline` writes execution evidence, and `03_governance` reviews intent and lifecycle state. The tables are intentionally separated: catalogue rows are observed evidence, guardrail rows are approved or pending intent, and result rows are runtime outcomes.

![FabricOps metadata architecture](../assets/fabricops-metadata-model.png)

*Figure: FabricOps metadata architecture. Metadata is the handoff layer between the notebook templates, governed rules, runtime checks, lineage, and dashboard visibility.*

## Inventory summary

| Metadata table | Purpose | Written by | Read by | Primary notebook(s) |
| --- | --- | --- | --- | --- |
| `METADATA_DATA_STEWARD` | Active and historical data steward records used by agreements. | [`widget_render_data_steward`](../api/reference/widget_render_data_steward.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md), [`widget_select_agreement`](../api/reference/widget_select_agreement.md), dashboard | `01_agreement.ipynb` |
| `METADATA_DATA_AGREEMENT` | Agreement/contract rows that describe approved use and recipient context. | [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | [`widget_select_agreement`](../api/reference/widget_select_agreement.md), [`get_selected_agreement`](../api/reference/get_selected_agreement.md), pipeline summary writers | `01_agreement.ipynb` |
| `METADATA_DATA_AGREEMENT_EVIDENCE` | Supporting agreement files and evidence metadata. | [`widget_render_agreement_evidence`](../api/reference/widget_render_agreement_evidence.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | agreement selection, dashboard, handover review | `01_agreement.ipynb` |
| `METADATA_NOTEBOOK_REGISTRY` | Links the active notebook to agreement, environment, dataset, and pipeline context. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) → [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | [`get_selected_agreement`](../api/reference/get_selected_agreement.md), lineage/run-summary helpers | `02_pipeline.ipynb` agreement-selection step |
| `METADATA_DATA_CATALOGUE` | Observed physical and profile evidence for tables and columns. This is evidence, not approved intent. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) → [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md); [`profile_dataframe`](../api/reference/profile_dataframe.md) builds profile columns | [`widget_select_guardrail_target`](../api/reference/widget_select_guardrail_target.md), [`run_table_guardrails`](../api/reference/run_table_guardrails.md), [`widget_review_table_governance`](../api/reference/widget_review_table_governance.md), dashboard | `02_pipeline.ipynb` profiling and guardrail steps |
| `METADATA_GUARDRAIL_RULES` | Append-only guardrail intent and lifecycle state for schema, freshness, profile behaviour, and DQ rules. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md), [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md), [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md), [`widget_review_table_governance`](../api/reference/widget_review_table_governance.md) → [`_append_guardrail_rule_records`](../api/reference/widget_review_table_governance.md) | [`run_table_guardrails`](../api/reference/run_table_guardrails.md), [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md), [`widget_review_table_governance`](../api/reference/widget_review_table_governance.md), dashboard | `02_pipeline.ipynb` optional authoring and `03_governance.ipynb` |
| `METADATA_GUARDRAIL_RESULTS` | Runtime outcomes from guardrail enforcement. This is outcome evidence, not rule intent. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) → guardrail enforcement helpers → [`_write_guardrail_result_row`](../api/reference/run_table_guardrails.md); [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) for DQ outcomes | [`display_guardrail_results`](../api/reference/display_guardrail_results.md), [`widget_review_table_governance`](../api/reference/widget_review_table_governance.md), dashboard | `02_pipeline.ipynb` guardrail execution |
| `METADATA_PIPELINE_RUNS` | One-row summary per pipeline run with agreement, status, counts, guardrail rollups, and JSON detail. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | dashboard, support handover, governance review context | `02_pipeline.ipynb` final evidence step |
| `METADATA_DATA_LINEAGE_TABLE` | Source-to-target lineage relationships for pipeline outputs. | [`write_pipeline_lineage`](../api/reference/write_pipeline_lineage.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | dashboard, support handover, governance review context | `02_pipeline.ipynb` final evidence step |
| `METADATA_ENRICHMENT_RULES` | Append-only descriptive table/column enrichment intent and lifecycle decisions. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) → [`_append_enrichment_records`](../api/reference/widget_enrich_table_metadata.md); [`widget_review_table_governance`](../api/reference/widget_review_table_governance.md) updates lifecycle rows | [`widget_review_table_governance`](../api/reference/widget_review_table_governance.md), dashboard | `02_pipeline.ipynb` optional enrichment and `03_governance.ipynb` |
| `METADATA_DATA_ACCESS` | Public-safe access context table prepared by metadata setup for governance/access reporting when used. | [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) creates/validates the table schema | dashboard/access review workflows when surfaced | `00_env_config.ipynb` setup creates schema; rows are populated by access/governance workflows when implemented |

## Routing rule

All `METADATA_*` reads and writes must use the configured `metadata` target from `00_env_config`, not an attached/default Lakehouse. The setup helper [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) creates or validates the active registry through `read_lakehouse_table(..., target="metadata")` and `write_lakehouse_table(..., target="metadata")`.

## Detailed table catalogue

### METADATA_DATA_STEWARD

Active and historical data steward records used by agreements.

**Notebook/template context**: `01_agreement.ipynb`.

**Write chain**
- Public/helper function(s): [`widget_render_data_steward`](../api/reference/widget_render_data_steward.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md).
- Physical write helper: `write_lakehouse_table(..., target="metadata")` through the configured metadata route.

**Read/consumer chain**
- [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md), [`widget_select_agreement`](../api/reference/widget_select_agreement.md), dashboard.

**Columns**

| Column | Meaning | Written by function(s) | Notes |
| --- | --- | --- | --- |
| `steward_id` | Stable identifier for the related record or runtime entity. | [`widget_render_data_steward`](../api/reference/widget_render_data_steward.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `steward_name` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_data_steward`](../api/reference/widget_render_data_steward.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `steward_role` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_data_steward`](../api/reference/widget_render_data_steward.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `contact` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_data_steward`](../api/reference/widget_render_data_steward.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `effective_from` | Timestamp/date for this lifecycle or runtime event. | [`widget_render_data_steward`](../api/reference/widget_render_data_steward.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `effective_to` | Timestamp/date for this lifecycle or runtime event. | [`widget_render_data_steward`](../api/reference/widget_render_data_steward.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `is_active` | Lifecycle, runtime, approval, or continuation state. | [`widget_render_data_steward`](../api/reference/widget_render_data_steward.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `custom_fields_json` | JSON payload for detailed or extensible metadata. | [`widget_render_data_steward`](../api/reference/widget_render_data_steward.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `_committed_by` | Runtime user/audit principal. | runtime audit helper | Defined in the active metadata setup schema. |
| `_committed_at` | Runtime audit timestamp from FabricOps audit helpers. | runtime audit helper | Defined in the active metadata setup schema. |
| `_notebook_name` | Notebook name captured at write time. | runtime audit helper | Defined in the active metadata setup schema. |
| `_workspace_name` | Fabric workspace name captured at write time. | runtime audit helper | Defined in the active metadata setup schema. |
| `_metadata_lakehouse_name` | Configured metadata Lakehouse target. | runtime audit helper | Defined in the active metadata setup schema. |
| `_activity_id` | Fabric activity/run id where available. | runtime audit helper | Defined in the active metadata setup schema. |

### METADATA_DATA_AGREEMENT

Agreement/contract rows that describe approved use and recipient context.

**Notebook/template context**: `01_agreement.ipynb`.

**Write chain**
- Public/helper function(s): [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md).
- Physical write helper: `write_lakehouse_table(..., target="metadata")` through the configured metadata route.

**Read/consumer chain**
- [`widget_select_agreement`](../api/reference/widget_select_agreement.md), [`get_selected_agreement`](../api/reference/get_selected_agreement.md), pipeline summary writers.

**Columns**

| Column | Meaning | Written by function(s) | Notes |
| --- | --- | --- | --- |
| `agreement_id` | Stable identifier for the related record or runtime entity. | [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `contract_version` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `agreement_name` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `domain` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `steward_id` | Stable identifier for the related record or runtime entity. | [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `recipient` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `start_date` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `expiry_date` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `business_purpose` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `approved_usage_internal` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `approved_usage_external` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `approved_usage_research` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `custom_fields_json` | JSON payload for detailed or extensible metadata. | [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `_committed_by` | Runtime user/audit principal. | runtime audit helper | Defined in the active metadata setup schema. |
| `_committed_at` | Runtime audit timestamp from FabricOps audit helpers. | runtime audit helper | Defined in the active metadata setup schema. |
| `_notebook_name` | Notebook name captured at write time. | runtime audit helper | Defined in the active metadata setup schema. |
| `_workspace_name` | Fabric workspace name captured at write time. | runtime audit helper | Defined in the active metadata setup schema. |
| `_metadata_lakehouse_name` | Configured metadata Lakehouse target. | runtime audit helper | Defined in the active metadata setup schema. |
| `_activity_id` | Fabric activity/run id where available. | runtime audit helper | Defined in the active metadata setup schema. |

### METADATA_DATA_AGREEMENT_EVIDENCE

Supporting agreement files and evidence metadata.

**Notebook/template context**: `01_agreement.ipynb`.

**Write chain**
- Public/helper function(s): [`widget_render_agreement_evidence`](../api/reference/widget_render_agreement_evidence.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md).
- Physical write helper: `write_lakehouse_table(..., target="metadata")` through the configured metadata route.

**Read/consumer chain**
- agreement selection, dashboard, handover review.

**Columns**

| Column | Meaning | Written by function(s) | Notes |
| --- | --- | --- | --- |
| `agreement_id` | Stable identifier for the related record or runtime entity. | [`widget_render_agreement_evidence`](../api/reference/widget_render_agreement_evidence.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `contract_version` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_agreement_evidence`](../api/reference/widget_render_agreement_evidence.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `evidence_type` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_agreement_evidence`](../api/reference/widget_render_agreement_evidence.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `file_name` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_agreement_evidence`](../api/reference/widget_render_agreement_evidence.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `file_path` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_agreement_evidence`](../api/reference/widget_render_agreement_evidence.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `mime_type` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_agreement_evidence`](../api/reference/widget_render_agreement_evidence.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `file_size` | Implementation-backed field from the setup schema for this metadata table. | [`widget_render_agreement_evidence`](../api/reference/widget_render_agreement_evidence.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `uploaded_at` | Timestamp/date for this lifecycle or runtime event. | [`widget_render_agreement_evidence`](../api/reference/widget_render_agreement_evidence.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `uploaded_by` | User, role, or owner associated with this action/context. | [`widget_render_agreement_evidence`](../api/reference/widget_render_agreement_evidence.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md) | Defined in the active metadata setup schema. |
| `_committed_by` | Runtime user/audit principal. | runtime audit helper | Defined in the active metadata setup schema. |
| `_committed_at` | Runtime audit timestamp from FabricOps audit helpers. | runtime audit helper | Defined in the active metadata setup schema. |
| `_notebook_name` | Notebook name captured at write time. | runtime audit helper | Defined in the active metadata setup schema. |
| `_workspace_name` | Fabric workspace name captured at write time. | runtime audit helper | Defined in the active metadata setup schema. |
| `_metadata_lakehouse_name` | Configured metadata Lakehouse target. | runtime audit helper | Defined in the active metadata setup schema. |
| `_activity_id` | Fabric activity/run id where available. | runtime audit helper | Defined in the active metadata setup schema. |

### METADATA_NOTEBOOK_REGISTRY

Links the active notebook to agreement, environment, dataset, and pipeline context.

**Notebook/template context**: `02_pipeline.ipynb` agreement-selection step.

**Write chain**
- Public/helper function(s): [`widget_select_agreement`](../api/reference/widget_select_agreement.md) → [`_register_current_notebook`](../api/reference/widget_select_agreement.md).
- Physical write helper: `write_lakehouse_table(..., target="metadata")` through the configured metadata route.

**Read/consumer chain**
- [`get_selected_agreement`](../api/reference/get_selected_agreement.md), lineage/run-summary helpers.

**Columns**

| Column | Meaning | Written by function(s) | Notes |
| --- | --- | --- | --- |
| `agreement_id` | Stable identifier for the related record or runtime entity. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `environment_name` | Physical/workflow context used to locate and explain the metadata row. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `dataset_name` | Physical/workflow context used to locate and explain the metadata row. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `table_name` | Physical/workflow context used to locate and explain the metadata row. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `topic` | Implementation-backed field from the setup schema for this metadata table. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `pipeline_name` | Physical/workflow context used to locate and explain the metadata row. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `notebook_type` | Physical/workflow context used to locate and explain the metadata row. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `workspace_id` | Stable identifier for the related record or runtime entity. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `workspace_name` | Implementation-backed field from the setup schema for this metadata table. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `notebook_id` | Stable identifier for the related record or runtime entity. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `notebook_name` | Physical/workflow context used to locate and explain the metadata row. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `notebook_url` | Implementation-backed field from the setup schema for this metadata table. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `user_name` | Implementation-backed field from the setup schema for this metadata table. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `user_id` | Stable identifier for the related record or runtime entity. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `registered_at` | Timestamp/date for this lifecycle or runtime event. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `registration_id` | Stable identifier for the related record or runtime entity. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `agreement_contract_version` | Implementation-backed field from the setup schema for this metadata table. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `registration_role` | Implementation-backed field from the setup schema for this metadata table. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `registration_status` | Lifecycle, runtime, approval, or continuation state. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `superseded_at` | Timestamp/date for this lifecycle or runtime event. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |
| `superseded_by_registration_id` | Stable identifier for the related record or runtime entity. | [`widget_select_agreement`](../api/reference/widget_select_agreement.md) / [`_register_current_notebook`](../api/reference/widget_select_agreement.md) | Defined in the active metadata setup schema. |

### METADATA_DATA_CATALOGUE

Observed physical and profile evidence for tables and columns. This is evidence, not approved intent.

**Notebook/template context**: `02_pipeline.ipynb` profiling and guardrail steps.

**Write chain**
- Public/helper function(s): [`run_table_guardrails`](../api/reference/run_table_guardrails.md) → [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md); [`profile_dataframe`](../api/reference/profile_dataframe.md) builds profile columns.
- Physical write helper: `write_lakehouse_table(..., target="metadata")` through the configured metadata route.

**Read/consumer chain**
- [`widget_select_guardrail_target`](../api/reference/widget_select_guardrail_target.md), [`run_table_guardrails`](../api/reference/run_table_guardrails.md), [`widget_review_table_governance`](../api/reference/widget_review_table_governance.md), dashboard.

**Columns**

| Column | Meaning | Written by function(s) | Notes |
| --- | --- | --- | --- |
| `metadata_table_key` | Stable metadata key used to join related table/column/rule records. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `metadata_column_key` | Stable metadata key used to join related table/column/rule records. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `environment_name` | Physical/workflow context used to locate and explain the metadata row. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `dataset_name` | Physical/workflow context used to locate and explain the metadata row. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `table_name` | Physical/workflow context used to locate and explain the metadata row. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `column_name` | Physical/workflow context used to locate and explain the metadata row. | [`profile_dataframe`](../api/reference/profile_dataframe.md) / [`_canonical_catalogue_profile_df`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `layer` | Physical/workflow context used to locate and explain the metadata row. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `asset_kind` | Physical/workflow context used to locate and explain the metadata row. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `pipeline_name` | Physical/workflow context used to locate and explain the metadata row. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `profile_run_id` | Stable identifier for the related record or runtime entity. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `profile_stage` | Implementation-backed field from the setup schema for this metadata table. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `profile_status` | Implementation-backed field from the setup schema for this metadata table. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `profiled_at` | Timestamp/date for this lifecycle or runtime event. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `run_timestamp` | Implementation-backed field from the setup schema for this metadata table. | [`profile_dataframe`](../api/reference/profile_dataframe.md) / [`_canonical_catalogue_profile_df`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `evidence_role` | Implementation-backed field from the setup schema for this metadata table. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `data_type` | Implementation-backed field from the setup schema for this metadata table. | [`profile_dataframe`](../api/reference/profile_dataframe.md) / [`_canonical_catalogue_profile_df`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `row_count` | Implementation-backed field from the setup schema for this metadata table. | [`profile_dataframe`](../api/reference/profile_dataframe.md) / [`_canonical_catalogue_profile_df`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `null_count` | Implementation-backed field from the setup schema for this metadata table. | [`profile_dataframe`](../api/reference/profile_dataframe.md) / [`_canonical_catalogue_profile_df`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `null_percent` | Implementation-backed field from the setup schema for this metadata table. | [`profile_dataframe`](../api/reference/profile_dataframe.md) / [`_canonical_catalogue_profile_df`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `distinct_count` | Implementation-backed field from the setup schema for this metadata table. | [`profile_dataframe`](../api/reference/profile_dataframe.md) / [`_canonical_catalogue_profile_df`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `distinct_percent` | Implementation-backed field from the setup schema for this metadata table. | [`profile_dataframe`](../api/reference/profile_dataframe.md) / [`_canonical_catalogue_profile_df`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `min_value` | Implementation-backed field from the setup schema for this metadata table. | [`profile_dataframe`](../api/reference/profile_dataframe.md) / [`_canonical_catalogue_profile_df`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `max_value` | Implementation-backed field from the setup schema for this metadata table. | [`profile_dataframe`](../api/reference/profile_dataframe.md) / [`_canonical_catalogue_profile_df`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `distribution_type` | Implementation-backed field from the setup schema for this metadata table. | [`profile_dataframe`](../api/reference/profile_dataframe.md) / [`_canonical_catalogue_profile_df`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `distribution_json` | JSON payload for detailed or extensible metadata. | [`profile_dataframe`](../api/reference/profile_dataframe.md) / [`_canonical_catalogue_profile_df`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `profile_mode` | Implementation-backed field from the setup schema for this metadata table. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `watermark_column` | Implementation-backed field from the setup schema for this metadata table. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `watermark_value` | Implementation-backed field from the setup schema for this metadata table. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `profile_hash` | Implementation-backed field from the setup schema for this metadata table. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `profile_payload_json` | JSON payload for detailed or extensible metadata. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `governance_mode` | Implementation-backed field from the setup schema for this metadata table. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `approval_policy` | Implementation-backed field from the setup schema for this metadata table. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `bypass_allowed` | Implementation-backed field from the setup schema for this metadata table. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `policy_reason` | Implementation-backed field from the setup schema for this metadata table. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `policy_updated_by` | User, role, or owner associated with this action/context. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `policy_updated_at` | Timestamp/date for this lifecycle or runtime event. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `agreement_id` | Stable identifier for the related record or runtime entity. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `contract_version` | Implementation-backed field from the setup schema for this metadata table. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `notebook_registry_id` | Stable identifier for the related record or runtime entity. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `notebook_id` | Stable identifier for the related record or runtime entity. | [`write_catalogue_evidence`](../api/reference/run_table_guardrails.md) | Defined in the active metadata setup schema. |
| `_committed_at` | Runtime audit timestamp from FabricOps audit helpers. | runtime audit helper | Defined in the active metadata setup schema. |
| `_committed_by` | Runtime user/audit principal. | runtime audit helper | Defined in the active metadata setup schema. |
| `_workspace_name` | Fabric workspace name captured at write time. | runtime audit helper | Defined in the active metadata setup schema. |
| `_notebook_name` | Notebook name captured at write time. | runtime audit helper | Defined in the active metadata setup schema. |
| `_metadata_lakehouse_name` | Configured metadata Lakehouse target. | runtime audit helper | Defined in the active metadata setup schema. |
| `_activity_id` | Fabric activity/run id where available. | runtime audit helper | Defined in the active metadata setup schema. |

### METADATA_GUARDRAIL_RULES

Append-only guardrail intent and lifecycle state for schema, freshness, profile behaviour, and DQ rules.

**Notebook/template context**: `02_pipeline.ipynb` optional authoring and `03_governance.ipynb`.

**Write chain**
- Public/helper function(s): [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md), [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md), [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md), [`widget_review_table_governance`](../api/reference/widget_review_table_governance.md) → [`_append_guardrail_rule_records`](../api/reference/widget_review_table_governance.md).
- Physical write helper: `write_lakehouse_table(..., target="metadata")` through the configured metadata route.

**Read/consumer chain**
- [`run_table_guardrails`](../api/reference/run_table_guardrails.md), [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md), [`widget_review_table_governance`](../api/reference/widget_review_table_governance.md), dashboard.

**Columns**

| Column | Meaning | Written by function(s) | Notes |
| --- | --- | --- | --- |
| `rule_key` | Stable metadata key used to join related table/column/rule records. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `rule_id` | Stable identifier for the related record or runtime entity. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `metadata_column_key` | Stable metadata key used to join related table/column/rule records. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `metadata_table_key` | Stable metadata key used to join related table/column/rule records. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `environment_name` | Physical/workflow context used to locate and explain the metadata row. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `dataset_name` | Physical/workflow context used to locate and explain the metadata row. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `table_name` | Physical/workflow context used to locate and explain the metadata row. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `column_name` | Physical/workflow context used to locate and explain the metadata row. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `guardrail_type` | Implementation-backed field from the setup schema for this metadata table. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `rule_type` | Implementation-backed field from the setup schema for this metadata table. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `rule_parameters_json` | JSON payload for detailed or extensible metadata. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `severity` | Lifecycle, runtime, approval, or continuation state. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `description` | Implementation-backed field from the setup schema for this metadata table. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `activation_state` | Lifecycle, runtime, approval, or continuation state. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `is_active` | Lifecycle, runtime, approval, or continuation state. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `review_status` | Lifecycle, runtime, approval, or continuation state. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `review_state` | Lifecycle, runtime, approval, or continuation state. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `created_by_role` | Implementation-backed field from the setup schema for this metadata table. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `author_role` | Implementation-backed field from the setup schema for this metadata table. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `created_by` | User, role, or owner associated with this action/context. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `created_at` | Timestamp/date for this lifecycle or runtime event. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `approved_by` | User, role, or owner associated with this action/context. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `approved_at` | Timestamp/date for this lifecycle or runtime event. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `suggestion_json` | JSON payload for detailed or extensible metadata. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `action_type` | Implementation-backed field from the setup schema for this metadata table. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `source_notebook_type` | Implementation-backed field from the setup schema for this metadata table. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `source_notebook_id` | Stable identifier for the related record or runtime entity. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `source_workspace_id` | Stable identifier for the related record or runtime entity. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `activation_reason` | Implementation-backed field from the setup schema for this metadata table. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `activated_by` | User, role, or owner associated with this action/context. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `activated_at` | Timestamp/date for this lifecycle or runtime event. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `superseded_by_rule_key` | Stable metadata key used to join related table/column/rule records. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `notes` | Implementation-backed field from the setup schema for this metadata table. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `approval_required` | Implementation-backed field from the setup schema for this metadata table. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `approval_bypassed` | Implementation-backed field from the setup schema for this metadata table. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `requires_governance_review` | Implementation-backed field from the setup schema for this metadata table. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `requires_post_review` | Implementation-backed field from the setup schema for this metadata table. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `bypass_reason` | Implementation-backed field from the setup schema for this metadata table. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `bypassed_by` | User, role, or owner associated with this action/context. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `bypassed_at` | Timestamp/date for this lifecycle or runtime event. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `governance_mode` | Implementation-backed field from the setup schema for this metadata table. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `approval_policy` | Implementation-backed field from the setup schema for this metadata table. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `submitted_by` | User, role, or owner associated with this action/context. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `submitted_at` | Timestamp/date for this lifecycle or runtime event. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `reviewed_by` | User, role, or owner associated with this action/context. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `reviewed_at` | Timestamp/date for this lifecycle or runtime event. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `review_decision` | Implementation-backed field from the setup schema for this metadata table. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `review_comment` | Implementation-backed field from the setup schema for this metadata table. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `supersedes_rule_id` | Stable identifier for the related record or runtime entity. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `supersedes_record_id` | Stable identifier for the related record or runtime entity. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `superseded_by_record_id` | Stable identifier for the related record or runtime entity. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `effective_from` | Timestamp/date for this lifecycle or runtime event. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `effective_to` | Timestamp/date for this lifecycle or runtime event. | [`widget_author_guardrail_rules`](../api/reference/widget_author_guardrail_rules.md) / [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) / [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `_committed_at` | Runtime audit timestamp from FabricOps audit helpers. | runtime audit helper | Defined in the active metadata setup schema. |
| `_committed_by` | Runtime user/audit principal. | runtime audit helper | Defined in the active metadata setup schema. |
| `_workspace_name` | Fabric workspace name captured at write time. | runtime audit helper | Defined in the active metadata setup schema. |
| `_notebook_name` | Notebook name captured at write time. | runtime audit helper | Defined in the active metadata setup schema. |
| `_metadata_lakehouse_name` | Configured metadata Lakehouse target. | runtime audit helper | Defined in the active metadata setup schema. |
| `_activity_id` | Fabric activity/run id where available. | runtime audit helper | Defined in the active metadata setup schema. |

### METADATA_GUARDRAIL_RESULTS

Runtime outcomes from guardrail enforcement. This is outcome evidence, not rule intent.

**Notebook/template context**: `02_pipeline.ipynb` guardrail execution.

**Write chain**
- Public/helper function(s): [`run_table_guardrails`](../api/reference/run_table_guardrails.md) → guardrail enforcement helpers → [`_write_guardrail_result_row`](../api/reference/run_table_guardrails.md); [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) for DQ outcomes.
- Physical write helper: `write_lakehouse_table(..., target="metadata")` through the configured metadata route.

**Read/consumer chain**
- [`display_guardrail_results`](../api/reference/display_guardrail_results.md), [`widget_review_table_governance`](../api/reference/widget_review_table_governance.md), dashboard.

**Columns**

| Column | Meaning | Written by function(s) | Notes |
| --- | --- | --- | --- |
| `result_id` | Stable identifier for the related record or runtime entity. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) / [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) result writers | Defined in the active metadata setup schema. |
| `run_id` | Stable identifier for the related record or runtime entity. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) / [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) result writers | Defined in the active metadata setup schema. |
| `rule_key` | Stable metadata key used to join related table/column/rule records. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) / [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) result writers | Defined in the active metadata setup schema. |
| `environment_name` | Physical/workflow context used to locate and explain the metadata row. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) / [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) result writers | Defined in the active metadata setup schema. |
| `dataset_name` | Physical/workflow context used to locate and explain the metadata row. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) / [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) result writers | Defined in the active metadata setup schema. |
| `table_name` | Physical/workflow context used to locate and explain the metadata row. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) / [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) result writers | Defined in the active metadata setup schema. |
| `column_name` | Physical/workflow context used to locate and explain the metadata row. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) / [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) result writers | Defined in the active metadata setup schema. |
| `guardrail_type` | Implementation-backed field from the setup schema for this metadata table. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) / [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) result writers | Defined in the active metadata setup schema. |
| `rule_type` | Implementation-backed field from the setup schema for this metadata table. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) / [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) result writers | Defined in the active metadata setup schema. |
| `status` | Lifecycle, runtime, approval, or continuation state. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) / [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) result writers | Defined in the active metadata setup schema. |
| `can_continue` | Lifecycle, runtime, approval, or continuation state. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) / [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) result writers | Defined in the active metadata setup schema. |
| `severity` | Lifecycle, runtime, approval, or continuation state. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) / [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) result writers | Defined in the active metadata setup schema. |
| `reason` | Implementation-backed field from the setup schema for this metadata table. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) / [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) result writers | Defined in the active metadata setup schema. |
| `expected_value_json` | JSON payload for detailed or extensible metadata. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) / [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) result writers | Defined in the active metadata setup schema. |
| `actual_value_json` | JSON payload for detailed or extensible metadata. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) / [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) result writers | Defined in the active metadata setup schema. |
| `result_payload_json` | JSON payload for detailed or extensible metadata. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) / [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) result writers | Defined in the active metadata setup schema. |
| `created_at` | Timestamp/date for this lifecycle or runtime event. | [`run_table_guardrails`](../api/reference/run_table_guardrails.md) / [`enforce_dq_rules`](../api/reference/enforce_dq_rules.md) result writers | Defined in the active metadata setup schema. |
| `_committed_at` | Runtime audit timestamp from FabricOps audit helpers. | runtime audit helper | Defined in the active metadata setup schema. |
| `_committed_by` | Runtime user/audit principal. | runtime audit helper | Defined in the active metadata setup schema. |
| `_workspace_name` | Fabric workspace name captured at write time. | runtime audit helper | Defined in the active metadata setup schema. |
| `_notebook_name` | Notebook name captured at write time. | runtime audit helper | Defined in the active metadata setup schema. |
| `_metadata_lakehouse_name` | Configured metadata Lakehouse target. | runtime audit helper | Defined in the active metadata setup schema. |
| `_activity_id` | Fabric activity/run id where available. | runtime audit helper | Defined in the active metadata setup schema. |

### METADATA_PIPELINE_RUNS

One-row summary per pipeline run with agreement, status, counts, guardrail rollups, and JSON detail.

**Notebook/template context**: `02_pipeline.ipynb` final evidence step.

**Write chain**
- Public/helper function(s): [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md).
- Physical write helper: `write_lakehouse_table(..., target="metadata")` through the configured metadata route.

**Read/consumer chain**
- dashboard, support handover, governance review context.

**Columns**

| Column | Meaning | Written by function(s) | Notes |
| --- | --- | --- | --- |
| `run_id` | Stable identifier for the related record or runtime entity. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `agreement_id` | Stable identifier for the related record or runtime entity. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `agreement_contract_version` | Implementation-backed field from the setup schema for this metadata table. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `notebook_registry_id` | Stable identifier for the related record or runtime entity. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `notebook_id` | Stable identifier for the related record or runtime entity. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `notebook_type` | Physical/workflow context used to locate and explain the metadata row. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `pipeline_name` | Physical/workflow context used to locate and explain the metadata row. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `environment_name` | Physical/workflow context used to locate and explain the metadata row. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `started_at` | Timestamp/date for this lifecycle or runtime event. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `completed_at` | Timestamp/date for this lifecycle or runtime event. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `status` | Lifecycle, runtime, approval, or continuation state. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `source_count` | Implementation-backed field from the setup schema for this metadata table. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `target_count` | Implementation-backed field from the setup schema for this metadata table. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `source_guardrail_status` | Implementation-backed field from the setup schema for this metadata table. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `target_guardrail_status` | Implementation-backed field from the setup schema for this metadata table. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `dq_status` | Implementation-backed field from the setup schema for this metadata table. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `lineage_status` | Implementation-backed field from the setup schema for this metadata table. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `catalogue_status` | Implementation-backed field from the setup schema for this metadata table. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `message` | Implementation-backed field from the setup schema for this metadata table. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `run_summary_json` | JSON payload for detailed or extensible metadata. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |
| `created_at` | Timestamp/date for this lifecycle or runtime event. | [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) | Defined in the active metadata setup schema. |

### METADATA_DATA_LINEAGE_TABLE

Source-to-target lineage relationships for pipeline outputs.

**Notebook/template context**: `02_pipeline.ipynb` final evidence step.

**Write chain**
- Public/helper function(s): [`write_pipeline_lineage`](../api/reference/write_pipeline_lineage.md) → [`write_lakehouse_table`](../api/reference/setup_metadata_tables.md).
- Physical write helper: `write_lakehouse_table(..., target="metadata")` through the configured metadata route.

**Read/consumer chain**
- dashboard, support handover, governance review context.

**Columns**

| Column | Meaning | Written by function(s) | Notes |
| --- | --- | --- | --- |
| `lineage_id` | Stable identifier for the related record or runtime entity. | [`write_pipeline_lineage`](../api/reference/write_pipeline_lineage.md) | Defined in the active metadata setup schema. |
| `dataset_name` | Physical/workflow context used to locate and explain the metadata row. | [`write_pipeline_lineage`](../api/reference/write_pipeline_lineage.md) | Defined in the active metadata setup schema. |
| `run_id` | Stable identifier for the related record or runtime entity. | [`write_pipeline_lineage`](../api/reference/write_pipeline_lineage.md) | Defined in the active metadata setup schema. |
| `source_table` | Implementation-backed field from the setup schema for this metadata table. | [`write_pipeline_lineage`](../api/reference/write_pipeline_lineage.md) | Defined in the active metadata setup schema. |
| `target_table` | Implementation-backed field from the setup schema for this metadata table. | [`write_pipeline_lineage`](../api/reference/write_pipeline_lineage.md) | Defined in the active metadata setup schema. |
| `source_table_key` | Stable metadata key used to join related table/column/rule records. | [`write_pipeline_lineage`](../api/reference/write_pipeline_lineage.md) | Defined in the active metadata setup schema. |
| `target_table_key` | Stable metadata key used to join related table/column/rule records. | [`write_pipeline_lineage`](../api/reference/write_pipeline_lineage.md) | Defined in the active metadata setup schema. |
| `transformation_steps_json` | JSON payload for detailed or extensible metadata. | [`write_pipeline_lineage`](../api/reference/write_pipeline_lineage.md) | Defined in the active metadata setup schema. |
| `created_at` | Timestamp/date for this lifecycle or runtime event. | [`write_pipeline_lineage`](../api/reference/write_pipeline_lineage.md) | Defined in the active metadata setup schema. |
| `_committed_at` | Runtime audit timestamp from FabricOps audit helpers. | runtime audit helper | Defined in the active metadata setup schema. |
| `_committed_by` | Runtime user/audit principal. | runtime audit helper | Defined in the active metadata setup schema. |
| `_workspace_name` | Fabric workspace name captured at write time. | runtime audit helper | Defined in the active metadata setup schema. |
| `_notebook_name` | Notebook name captured at write time. | runtime audit helper | Defined in the active metadata setup schema. |
| `_metadata_lakehouse_name` | Configured metadata Lakehouse target. | runtime audit helper | Defined in the active metadata setup schema. |
| `_activity_id` | Fabric activity/run id where available. | runtime audit helper | Defined in the active metadata setup schema. |

### METADATA_ENRICHMENT_RULES

Append-only descriptive table/column enrichment intent and lifecycle decisions.

**Notebook/template context**: `02_pipeline.ipynb` optional enrichment and `03_governance.ipynb`.

**Write chain**
- Public/helper function(s): [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) → [`_append_enrichment_records`](../api/reference/widget_enrich_table_metadata.md); [`widget_review_table_governance`](../api/reference/widget_review_table_governance.md) updates lifecycle rows.
- Physical write helper: `write_lakehouse_table(..., target="metadata")` through the configured metadata route.

**Read/consumer chain**
- [`widget_review_table_governance`](../api/reference/widget_review_table_governance.md), dashboard.

**Columns**

| Column | Meaning | Written by function(s) | Notes |
| --- | --- | --- | --- |
| `enrichment_rule_id` | Stable identifier for the related record or runtime entity. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `enrichment_rule_version` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `enrichment_rule_key` | Stable metadata key used to join related table/column/rule records. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `metadata_table_key` | Stable metadata key used to join related table/column/rule records. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `metadata_column_key` | Stable metadata key used to join related table/column/rule records. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `table_name` | Physical/workflow context used to locate and explain the metadata row. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `column_name` | Physical/workflow context used to locate and explain the metadata row. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `enrichment_scope` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `enrichment_type` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `enrichment_payload_json` | JSON payload for detailed or extensible metadata. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `business_name` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `business_description` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `business_meaning` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `column_description` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `classification` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `sensitivity_label` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `pii_flag` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `pii_type` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `data_domain` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `data_owner` | User, role, or owner associated with this action/context. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `data_steward` | User, role, or owner associated with this action/context. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `usage_notes` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `quality_notes` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `review_status` | Lifecycle, runtime, approval, or continuation state. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `review_state` | Lifecycle, runtime, approval, or continuation state. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `activation_state` | Lifecycle, runtime, approval, or continuation state. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `is_active` | Lifecycle, runtime, approval, or continuation state. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `created_by_role` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `source_notebook_type` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `source_notebook_id` | Stable identifier for the related record or runtime entity. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `activation_reason` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `activated_by` | User, role, or owner associated with this action/context. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `activated_at` | Timestamp/date for this lifecycle or runtime event. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `requires_governance_review` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `approval_policy` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `governance_mode` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `submitted_by` | User, role, or owner associated with this action/context. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `submitted_at` | Timestamp/date for this lifecycle or runtime event. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `reviewed_by` | User, role, or owner associated with this action/context. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `reviewed_at` | Timestamp/date for this lifecycle or runtime event. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `review_decision` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `review_comment` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `bypass_reason` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `requires_post_review` | Implementation-backed field from the setup schema for this metadata table. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `supersedes_enrichment_rule_id` | Stable identifier for the related record or runtime entity. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `supersedes_record_id` | Stable identifier for the related record or runtime entity. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `superseded_by_record_id` | Stable identifier for the related record or runtime entity. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `effective_from` | Timestamp/date for this lifecycle or runtime event. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `effective_to` | Timestamp/date for this lifecycle or runtime event. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `created_at` | Timestamp/date for this lifecycle or runtime event. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `created_by` | User, role, or owner associated with this action/context. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `updated_at` | Timestamp/date for this lifecycle or runtime event. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `updated_by` | User, role, or owner associated with this action/context. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `run_id` | Stable identifier for the related record or runtime entity. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `notebook_id` | Stable identifier for the related record or runtime entity. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `notebook_registry_id` | Stable identifier for the related record or runtime entity. | [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) builders and review lifecycle helpers | Defined in the active metadata setup schema. |
| `_committed_at` | Runtime audit timestamp from FabricOps audit helpers. | runtime audit helper | Defined in the active metadata setup schema. |
| `_committed_by` | Runtime user/audit principal. | runtime audit helper | Defined in the active metadata setup schema. |
| `_workspace_name` | Fabric workspace name captured at write time. | runtime audit helper | Defined in the active metadata setup schema. |
| `_notebook_name` | Notebook name captured at write time. | runtime audit helper | Defined in the active metadata setup schema. |
| `_metadata_lakehouse_name` | Configured metadata Lakehouse target. | runtime audit helper | Defined in the active metadata setup schema. |
| `_activity_id` | Fabric activity/run id where available. | runtime audit helper | Defined in the active metadata setup schema. |

### METADATA_DATA_ACCESS

Public-safe access context table prepared by metadata setup for governance/access reporting when used.

**Notebook/template context**: `00_env_config.ipynb` setup creates schema; rows are populated by access/governance workflows when implemented.

**Write chain**
- Public/helper function(s): [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) creates/validates the table schema.
- Physical write helper: `write_lakehouse_table(..., target="metadata")` through the configured metadata route.

**Read/consumer chain**
- dashboard/access review workflows when surfaced.

**Columns**

| Column | Meaning | Written by function(s) | Notes |
| --- | --- | --- | --- |
| `user_principal` | Implementation-backed field from the setup schema for this metadata table. | [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) schema; access workflows populate rows | Defined in the active metadata setup schema. |
| `role_name` | Implementation-backed field from the setup schema for this metadata table. | [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) schema; access workflows populate rows | Defined in the active metadata setup schema. |
| `permission` | Implementation-backed field from the setup schema for this metadata table. | [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) schema; access workflows populate rows | Defined in the active metadata setup schema. |
| `access_purpose` | Implementation-backed field from the setup schema for this metadata table. | [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) schema; access workflows populate rows | Defined in the active metadata setup schema. |
| `approval_status` | Lifecycle, runtime, approval, or continuation state. | [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) schema; access workflows populate rows | Defined in the active metadata setup schema. |
| `access_scope` | Implementation-backed field from the setup schema for this metadata table. | [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) schema; access workflows populate rows | Defined in the active metadata setup schema. |
| `table_id` | Stable identifier for the related record or runtime entity. | [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) schema; access workflows populate rows | Defined in the active metadata setup schema. |
| `metadata_table_key` | Stable metadata key used to join related table/column/rule records. | [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) schema; access workflows populate rows | Defined in the active metadata setup schema. |
| `metadata_column_key` | Stable metadata key used to join related table/column/rule records. | [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) schema; access workflows populate rows | Defined in the active metadata setup schema. |
| `granted_date` | Timestamp/date for this lifecycle or runtime event. | [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) schema; access workflows populate rows | Defined in the active metadata setup schema. |
| `expires_at` | Timestamp/date for this lifecycle or runtime event. | [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) schema; access workflows populate rows | Defined in the active metadata setup schema. |
| `approved_by` | User, role, or owner associated with this action/context. | [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) schema; access workflows populate rows | Defined in the active metadata setup schema. |
| `approved_at` | Timestamp/date for this lifecycle or runtime event. | [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) schema; access workflows populate rows | Defined in the active metadata setup schema. |
| `notes` | Implementation-backed field from the setup schema for this metadata table. | [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) schema; access workflows populate rows | Defined in the active metadata setup schema. |
| `_committed_at` | Runtime audit timestamp from FabricOps audit helpers. | runtime audit helper | Defined in the active metadata setup schema. |
| `_committed_by` | Runtime user/audit principal. | runtime audit helper | Defined in the active metadata setup schema. |
| `_workspace_name` | Fabric workspace name captured at write time. | runtime audit helper | Defined in the active metadata setup schema. |
| `_notebook_name` | Notebook name captured at write time. | runtime audit helper | Defined in the active metadata setup schema. |
| `_metadata_lakehouse_name` | Configured metadata Lakehouse target. | runtime audit helper | Defined in the active metadata setup schema. |
| `_activity_id` | Fabric activity/run id where available. | runtime audit helper | Defined in the active metadata setup schema. |
