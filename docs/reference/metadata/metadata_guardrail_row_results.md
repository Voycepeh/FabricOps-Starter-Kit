# METADATA_GUARDRAIL_ROW_RESULTS

See the individual records that failed a Data Quality rule.

## Writer functions

* [`check_dq`](../../api/reference/check_dq.md)

## Used in Workflow Template

* [`02_pipeline`](../../notebook-templates.md) — Source guardrails

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One failed record belonging to one Guardrail Result.

**Primary key:** `guardrail_row_result_id`

**Relationships:**

`METADATA_GUARDRAIL_RESULTS` **(N → 1)**
via `guardrail_result_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 14 |
| Business columns | 6 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `guardrail_row_result_id` | `string` | Identifier stored for `guardrail_row_result_id`. |
| `guardrail_result_id` | `string` | Stable identifier for the runtime guardrail result row. |
| `row_identity` | `string` | Metadata Guardrail Row Results field `row_identity`. |
| `involved_columns_json` | `string` | JSON payload stored for `involved_columns_json`. |
| `failed_values_json` | `string` | JSON payload stored for `failed_values_json`. |
| `failure_reason` | `string` | Metadata Guardrail Row Results field `failure_reason`. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
