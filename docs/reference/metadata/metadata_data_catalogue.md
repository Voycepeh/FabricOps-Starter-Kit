# METADATA_DATA_CATALOGUE

**Purpose:** Observed table and column profile evidence. This is runtime evidence, not approved guardrail intent.

## Starter Kit usage

- **Written by notebook/template:** 02_pipeline.ipynb, 03_governance.ipynb, 99_explore.ipynb
- **Written by function or widget:** [`run_table_guardrails`](../../api/reference/run_table_guardrails.md)
- **Read by function or widget:** [`get_latest_metadata_catalogue`](../../api/reference/get_latest_metadata_catalogue.md), [`widget_select_guardrail_target`](../../api/reference/widget_select_guardrail_target.md), [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md), [`run_table_guardrails`](../../api/reference/run_table_guardrails.md)
- **Related template step:** 02_pipeline.ipynb, 03_governance.ipynb, 99_explore.ipynb

## Implemented schema

| Column name | Data type | Nullable / required |
| --- | --- | --- |
| `metadata_table_key` | `string` | Nullable |
| `metadata_column_key` | `string` | Nullable |
| `environment_name` | `string` | Nullable |
| `dataset_name` | `string` | Nullable |
| `table_name` | `string` | Nullable |
| `column_name` | `string` | Nullable |
| `layer` | `string` | Nullable |
| `asset_kind` | `string` | Nullable |
| `pipeline_name` | `string` | Nullable |
| `profile_run_id` | `string` | Nullable |
| `profile_stage` | `string` | Nullable |
| `profile_status` | `string` | Nullable |
| `profiled_at` | `timestamp` | Nullable |
| `run_timestamp` | `timestamp` | Nullable |
| `evidence_role` | `string` | Nullable |
| `data_type` | `string` | Nullable |
| `row_count` | `long` | Nullable |
| `null_count` | `long` | Nullable |
| `null_percent` | `double` | Nullable |
| `distinct_count` | `long` | Nullable |
| `distinct_percent` | `double` | Nullable |
| `min_value` | `string` | Nullable |
| `max_value` | `string` | Nullable |
| `distribution_type` | `string` | Nullable |
| `distribution_json` | `string` | Nullable |
| `profile_mode` | `string` | Nullable |
| `watermark_column` | `string` | Nullable |
| `watermark_value` | `string` | Nullable |
| `profile_hash` | `string` | Nullable |
| `profile_payload_json` | `string` | Nullable |
| `governance_mode` | `string` | Nullable |
| `approval_policy` | `string` | Nullable |
| `bypass_allowed` | `boolean` | Nullable |
| `policy_reason` | `string` | Nullable |
| `policy_updated_by` | `string` | Nullable |
| `policy_updated_at` | `timestamp` | Nullable |
| `agreement_id` | `string` | Nullable |
| `contract_version` | `string` | Nullable |
| `notebook_registry_id` | `string` | Nullable |
| `notebook_id` | `string` | Nullable |
| `_committed_by` | `string` | Nullable |
| `_committed_at` | `timestamp` | Nullable |
| `_workspace_name` | `string` | Nullable |
| `_notebook_name` | `string` | Nullable |
| `_metadata_lakehouse_name` | `string` | Nullable |
| `_activity_id` | `string` | Nullable |

## Related function reference

- [`get_latest_metadata_catalogue`](../../api/reference/get_latest_metadata_catalogue.md)
- [`run_table_guardrails`](../../api/reference/run_table_guardrails.md)
- [`widget_review_guardrail_governance`](../../api/reference/widget_review_guardrail_governance.md)
- [`widget_select_guardrail_target`](../../api/reference/widget_select_guardrail_target.md)
