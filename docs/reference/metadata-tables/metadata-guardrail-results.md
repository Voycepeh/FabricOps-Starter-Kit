# METADATA_GUARDRAIL_RESULTS

**Purpose:** Runtime guardrail outcomes written by pipeline enforcement.

## Notebook usage

- **Written by notebook/template:** 02_pipeline.ipynb
- **Written by function or widget:** [`run_table_guardrails`](../../api/reference/run_table_guardrails.md)
- **Read by function or widget:** [`display_guardrail_results`](../../api/reference/display_guardrail_results.md), [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md)
- **Related template step:** 02_pipeline.ipynb

## Implemented schema

| Column name | Data type | Nullable / required |
| --- | --- | --- |
| `result_id` | `string` | Nullable |
| `run_id` | `string` | Nullable |
| `rule_key` | `string` | Nullable |
| `environment_name` | `string` | Nullable |
| `dataset_name` | `string` | Nullable |
| `table_name` | `string` | Nullable |
| `column_name` | `string` | Nullable |
| `guardrail_type` | `string` | Nullable |
| `rule_type` | `string` | Nullable |
| `status` | `string` | Nullable |
| `can_continue` | `boolean` | Nullable |
| `severity` | `string` | Nullable |
| `reason` | `string` | Nullable |
| `expected_value_json` | `string` | Nullable |
| `actual_value_json` | `string` | Nullable |
| `result_payload_json` | `string` | Nullable |
| `created_at` | `string` | Nullable |
| `_committed_at` | `string` | Nullable |
| `_committed_by` | `string` | Nullable |
| `_workspace_name` | `string` | Nullable |
| `_notebook_name` | `string` | Nullable |
| `_metadata_lakehouse_name` | `string` | Nullable |
| `_activity_id` | `string` | Nullable |

## Related function reference

- [`display_guardrail_results`](../../api/reference/display_guardrail_results.md)
- [`run_table_guardrails`](../../api/reference/run_table_guardrails.md)
- [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md)
