# METADATA_GUARDRAIL_RESULTS

**Purpose:** Runtime guardrail outcomes written by pipeline enforcement.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `guardrail_result_id` | `string` | No | Pipeline guardrail writers | Metadata Guardrail Results field `guardrail_result_id`. |
| `guardrail_rule_id` | `string` | No | Pipeline guardrail writers | Metadata Guardrail Results field `guardrail_rule_id`. |
| `result_id` | `string` | No | Pipeline guardrail writers | Metadata Guardrail Results field `result_id`. |
| `rule_key` | `string` | No | Pipeline guardrail writers | Metadata Guardrail Results field `rule_key`. |
| `metadata_table_key` | `string` | Yes | Pipeline guardrail writers | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `environment_name` | `string` | Yes | Pipeline guardrail writers | Metadata Guardrail Results field `environment_name`. |
| `dataset_name` | `string` | Yes | Pipeline guardrail writers | Metadata Guardrail Results field `dataset_name`. |
| `table_name` | `string` | Yes | Pipeline guardrail writers | Metadata Guardrail Results field `table_name`. |
| `column_name` | `string` | Yes | Pipeline guardrail writers | Metadata Guardrail Results field `column_name`. |
| `guardrail_type` | `string` | Yes | Pipeline guardrail writers | Metadata Guardrail Results field `guardrail_type`. |
| `rule_type` | `string` | Yes | Pipeline guardrail writers | Metadata Guardrail Results field `rule_type`. |
| `status` | `string` | Yes | Pipeline guardrail writers | Pipeline run status recorded with the run summary. |
| `can_continue` | `boolean` | Yes | Pipeline guardrail writers | Metadata Guardrail Results field `can_continue`. |
| `severity` | `string` | Yes | Pipeline guardrail writers | Metadata Guardrail Results field `severity`. |
| `reason` | `string` | Yes | Pipeline guardrail writers | Metadata Guardrail Results field `reason`. |
| `expected_value_json` | `string` | Yes | Pipeline guardrail writers | Metadata Guardrail Results field `expected_value_json`. |
| `actual_value_json` | `string` | Yes | Pipeline guardrail writers | Metadata Guardrail Results field `actual_value_json`. |
| `result_payload_json` | `string` | Yes | Pipeline guardrail writers | Metadata Guardrail Results field `result_payload_json`. |
| `_committed_by` | `string` | No | Runtime audit context | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | No | Runtime audit context | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | No | Runtime audit context | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | No | Runtime audit context | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | No | Runtime audit context | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | No | Runtime audit context | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | No | Runtime audit context | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`run_table_guardrails`](../../api/reference/run_table_guardrails.md)
- [`display_guardrail_results`](../../api/reference/display_guardrail_results.md)
