# METADATA_GUARDRAIL_RESULTS

Store aggregate enforce and validate Guardrail summaries and completed pipeline-validation records for exact participating contract versions, captured table name, readable rule context, and continuation decisions; caller-owned failed business rows are not persisted here. Captured context does not follow later table or rule changes.

## Writer functions

* [`orchestrate_read`](../../api/reference/orchestrate_read.md)
* [`orchestrate_write`](../../api/reference/orchestrate_write.md)

## Used in Workflow Template

* [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Standard Read orchestration
* [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Standard Write orchestration

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One Guardrail outcome for one exact Data Contract version in one enforce or validate execution.

**Primary key:** `guardrail_result_id`

**Relationships:**

`METADATA_DATA_CONTRACT` **(N → 1)**
via `contract_id` + `contract_version`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 27 |
| Business columns | 19 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `guardrail_result_id` | `string` | Stable identifier for the aggregate Guardrail result row. |
| `guardrail_rule_id` | `string` | Stable authored Guardrail identifier, or the synthetic completion-record identifier when rule_type is contract_validation. |
| `guardrail_version` | `integer` | Metadata Guardrail Results field `guardrail_version`. |
| `table_id` | `string` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `table_name` | `string` | Table name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it. |
| `contract_id` | `string` | Stable identifier for the contract row. |
| `contract_version` | `integer` | Version recorded for the contract row. |
| `execution_type` | `string` | Whether the runtime record came from enforce or validate contract execution. Completed pipeline-validation records use validate and require all checks plus Guardrail Coverage to pass. |
| `run_id` | `string` | Identifier stored for `run_id`. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `status` | `string` | Pipeline run status recorded with the run summary. |
| `can_continue` | `boolean` | Metadata Guardrail Results field `can_continue`. |
| `severity` | `string` | Severity recorded for a Guardrail result. |
| `guardrail_type` | `string` | Guardrail family recorded for the row. |
| `rule_id` | `string` | Rule identity stored by the authoring workflow. |
| `rule_type` | `string` | Specific rule type recorded within the guardrail family. |
| `action` | `string` | Warn or Block action applied when an authored Guardrail fails. |
| `reason` | `string` | Human-readable reason recorded for the Guardrail outcome. |
| `result_payload_json` | `string` | Serialized aggregate result payload written for the Guardrail outcome. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
