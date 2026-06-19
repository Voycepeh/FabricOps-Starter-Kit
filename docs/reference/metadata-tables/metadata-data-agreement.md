# METADATA_DATA_AGREEMENT

**Purpose:** Agreement records that describe approved use, steward, recipient, and lifecycle context.

## Workflow usage

- **Written by notebook/template:** 01_agreement.ipynb, 02_pipeline.ipynb
- **Written by function or widget:** [`widget_render_data_agreement`](../../api/reference/widget_render_data_agreement.md)
- **Read by function or widget:** [`widget_select_agreement`](../../api/reference/widget_select_agreement.md), [`write_pipeline_run_summary`](../../api/reference/write_pipeline_run_summary.md)
- **Related template step:** 01_agreement.ipynb, 02_pipeline.ipynb

## Implemented schema

| Column name | Data type | Nullable / required |
| --- | --- | --- |
| `agreement_id` | `string` | Nullable |
| `contract_version` | `string` | Nullable |
| `agreement_name` | `string` | Nullable |
| `domain` | `string` | Nullable |
| `steward_id` | `string` | Nullable |
| `recipient` | `string` | Nullable |
| `start_date` | `string` | Nullable |
| `expiry_date` | `string` | Nullable |
| `business_purpose` | `string` | Nullable |
| `approved_usage_internal` | `string` | Nullable |
| `approved_usage_external` | `string` | Nullable |
| `approved_usage_research` | `string` | Nullable |
| `custom_fields_json` | `string` | Nullable |
| `_committed_by` | `string` | Nullable |
| `_committed_at` | `string` | Nullable |
| `_notebook_name` | `string` | Nullable |
| `_workspace_name` | `string` | Nullable |
| `_metadata_lakehouse_name` | `string` | Nullable |
| `_activity_id` | `string` | Nullable |

## Related function reference

- [`widget_render_data_agreement`](../../api/reference/widget_render_data_agreement.md)
- [`widget_select_agreement`](../../api/reference/widget_select_agreement.md)
- [`write_pipeline_run_summary`](../../api/reference/write_pipeline_run_summary.md)
