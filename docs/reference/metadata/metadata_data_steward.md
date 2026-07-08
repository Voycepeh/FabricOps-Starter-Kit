# METADATA_DATA_STEWARD

**Purpose:** Active and historical data steward records used by agreement intake.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `steward_id` | `string` | Yes | Data steward widget | Metadata Data Steward field `steward_id`. |
| `steward_name` | `string` | Yes | Data steward widget | Metadata Data Steward field `steward_name`. |
| `steward_role` | `string` | Yes | Data steward widget | Metadata Data Steward field `steward_role`. |
| `contact` | `string` | Yes | Data steward widget | Metadata Data Steward field `contact`. |
| `effective_from` | `date` | Yes | Data steward widget | Metadata Data Steward field `effective_from`. |
| `effective_to` | `date` | Yes | Data steward widget | Metadata Data Steward field `effective_to`. |
| `is_active` | `boolean` | Yes | Data steward widget | Metadata Data Steward field `is_active`. |
| `custom_fields_json` | `string` | Yes | Data steward widget | Metadata Data Steward field `custom_fields_json`. |
| `_committed_by` | `string` | No | Runtime audit context | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | No | Runtime audit context | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | No | Runtime audit context | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | No | Runtime audit context | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | No | Runtime audit context | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | No | Runtime audit context | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | No | Runtime audit context | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`widget_render_data_steward`](../../api/reference/widget_render_data_steward.md)
