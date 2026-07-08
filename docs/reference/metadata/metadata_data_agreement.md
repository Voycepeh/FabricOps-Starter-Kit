# METADATA_DATA_AGREEMENT

**Purpose:** Agreement records that describe approved use, steward, recipient, and lifecycle context.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `agreement_id` | `string` | No | Agreement widget | Metadata Data Agreement field `agreement_id`. |
| `agreement_version` | `string` | No | Agreement widget | Canonical agreement version associated with the row. |
| `agreement_name` | `string` | No | Agreement widget | Metadata Data Agreement field `agreement_name`. |
| `domain` | `string` | No | Agreement widget | Metadata Data Agreement field `domain`. |
| `steward_id` | `string` | No | Agreement widget | Metadata Data Agreement field `steward_id`. |
| `recipient` | `string` | No | Agreement widget | Metadata Data Agreement field `recipient`. |
| `start_date` | `date` | No | Agreement widget | Metadata Data Agreement field `start_date`. |
| `expiry_date` | `date` | No | Agreement widget | Metadata Data Agreement field `expiry_date`. |
| `business_purpose` | `string` | No | Agreement widget | Metadata Data Agreement field `business_purpose`. |
| `custom_fields_json` | `string` | Yes | Agreement widget | Metadata Data Agreement field `custom_fields_json`. |
| `_committed_by` | `string` | No | Runtime audit context | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | No | Runtime audit context | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | No | Runtime audit context | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | No | Runtime audit context | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | No | Runtime audit context | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | No | Runtime audit context | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | No | Runtime audit context | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`widget_render_data_agreement`](../../api/reference/widget_render_data_agreement.md)
- [`widget_pipeline_bootstrap`](../../api/reference/widget_pipeline_bootstrap.md)
- [`write_pipeline_run_summary`](../../api/reference/write_pipeline_run_summary.md)
