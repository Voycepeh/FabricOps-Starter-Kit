# Source projection matrix

Every loaded field supports an implemented page, relationship, filter, measure, or drillthrough. Derived model tables created from JSON are listed against their physical source.

| Metadata table | Selected columns / JSON attributes | Purpose | Required page |
|---|---|---|---|
| `METADATA_PIPELINE_REGISTRY` | `execution_workspace_id`, `pipeline_id`, `pipeline_version`, `promotion_id`, `status`, `governed_notebook_id`, `promoted_at` | Registered pipelines, stable pipeline identity, current promotion context | Overview, Pipeline Detail |
| `METADATA_PIPELINE_RUN` | `run_id`, `pipeline_id`, `execution_mode`, `workspace_id`, `started_at`, `completed_at`, `status`, `boundary_completed`, `pipeline_version`, `promotion_id`, `governed_notebook_id`; `operations` only for the attributes below; `failures.code`, `failures.exception_type` | History, performance baseline, latest status, run drillthrough, safe failures | Overview, Maintainer, Pipeline Detail, Table Detail |
| `METADATA_PIPELINE_RUN.operations` | `operation_key`, `table_id`, `pipeline_role`, `contract_id`, `contract_version`, `status`, `started_at`, `completed_at`, `destination.workspace_id`, `destination.item_id`, `destination.kind`, `destination.schema`, `destination.table_name` | Affected tables and operation diagnostics | Pipeline Detail, Table Detail |
| `METADATA_PIPELINE_RUN.operations[].stages` | `stage`, `status`, `evaluation_status` | Recorded stage diagnostics; no stage duration is inferred | Pipeline Detail |
| `METADATA_GUARDRAIL_RESULTS` | `guardrail_result_id`, `run_id`, `table_id`, `table_name`, `workspace_id`, `contract_id`, `contract_version`, `status`, `can_continue`, `severity`, `guardrail_type`, `rule_type`, `action`, `reason`, `_committed_at` | Current violations and investigation context; `result_payload_json` is deliberately excluded | Overview, Maintainer, Table Detail |
| `METADATA_DATA_CATALOGUE` | `metadata_level`, `table_id`, `column_id`, `workspace_id`, `store_type`, `layer`, `schema_name`, `table_name`, `column_name`, `data_type`, `load_strategy`, `first_profiled_at`, `last_profiled_at`, `is_active` | Workspace-aware table/column identities, monitored tables, catalogue and profile navigation | Overview, Data Owner, Table Detail |
| `METADATA_DATA_PROFILED` | `profile_snapshot_id`, `table_id`, `column_id`, `workspace_id`, `row_count`, `null_count`, `null_percent`, `distinct_count`, `distinct_percent`, `min_value`, `median_value`, `max_value`, `_committed_at` | Latest per-column profile snapshot | Data Owner, Table Detail |
| `METADATA_DATA_CONTRACT` | `contract_id`, `contract_version`, `table_id`, `table_name`, `evidence_workspace_id`, `status`; JSON paths `table.processing.load_strategy`, count of `guardrails`, table-level Description enrichment | Readable current Contract context without loading the full payload | Data Owner, Table Detail |
| `METADATA_DATA_CONTRACT_ACTIVATION` | `workspace_id`, `table_id`, `contract_id`, `contract_version`, `activation_id`, `revision`, `status`, `activated_at`, `agreement_id`, `agreement_version` | Latest exact physical Contract and Agreement selection | Overview, Data Owner, Table Detail |
| `METADATA_DATA_AGREEMENT` | `agreement_id`, `agreement_version`, `agreement_name`, `domain`, `provider_steward_id`, `recipient_steward_id`, `start_date`, `expiry_date`, `business_purpose` | Versioned governance context and steward participation bridge | Data Owner, Table Detail |
| `METADATA_DATA_STEWARD` | `steward_id`, `steward_name`, `contact`, `steward_role`, `is_active` | Steward name/contact slicer, defaulting to all active stewards | Data Owner |

## Evaluated but not loaded

| Metadata table | Decision |
|---|---|
| `METADATA_DATA_PROFILED_FREQUENCY` | Not needed by an implemented v1 user journey; current summary metrics already answer profiling questions. Excluding it avoids a high-cardinality value distribution. |
| `METADATA_DATA_LINEAGE` | The current schema records table participation and role but no Pipeline ID. Run operations provide the verified pipeline-to-table association required by detail pages, so loading Lineage would be redundant and could imply an unsupported join. |
| `METADATA_PIPELINE_ACTIVATION` | Not needed for the agreed operational and table journeys; Registry already carries exact approval/promotion context used here. |
| `METADATA_DATA_ACCESS`, `METADATA_PROCESSING_STATE` | Explicitly outside v1 (no access scanning or processing-state remediation UI). |

Pipeline and Guardrail records are restricted at source by `HistoryWindowDays` and optional `WorkspaceFilter`. Contract Activation and Profiled data are reduced to the latest record at their reporting grain. The complete Contract, result, warning, profiling-event, and operations JSON strings are never loaded into the model.

