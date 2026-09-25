# METADATA_GUARDRAIL_RESULTS

Store aggregate enforce and validate Guardrail summaries and continuation decisions; caller-owned failed business rows are not persisted here. Existing Preview installations may require this table to be recreated or updated through metadata setup because FabricOps does not automatically migrate missing columns.

## Writer functions

* [`check_dq`](../../api/reference/check_dq.md)
* [`check_freshness`](../../api/reference/check_freshness.md)
* [`check_schema`](../../api/reference/check_schema.md)
* [`check_source_drift`](../../api/reference/check_source_drift.md)

## Used in Workflow Template

* [`02_pipeline`](../../notebook-templates.md) — Source guardrails

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One Guardrail outcome for one exact Data Contract version in one enforce or validate execution.

**Primary key:** `guardrail_result_id`

**Relationships:**

`METADATA_GUARDRAIL` **(N → 1)**
via `guardrail_rule_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 22 |
| Business columns | 14 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `guardrail_result_id` | `string` | Stable identifier for the aggregate Guardrail result row. |
| `guardrail_rule_id` | `string` | Stable identifier for the guardrail rule row. |
| `guardrail_version` | `integer` | Metadata Guardrail Results field `guardrail_version`. |
| `table_id` | `string` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `contract_id` | `string` | Stable identifier for the contract row. |
| `contract_version` | `integer` | Version recorded for the contract row. |
| `execution_type` | `string` | Whether the Guardrail outcome came from enforce or validate contract execution. |
| `run_id` | `string` | Identifier stored for `run_id`. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `status` | `string` | Pipeline run status recorded with the run summary. |
| `can_continue` | `boolean` | Metadata Guardrail Results field `can_continue`. |
| `severity` | `string` | Severity recorded for a Guardrail result. |
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
