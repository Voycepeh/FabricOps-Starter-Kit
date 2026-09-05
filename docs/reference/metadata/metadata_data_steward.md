# METADATA_DATA_STEWARD

Know who is responsible for the data.

## Writer functions

* [`widget_render_data_steward`](../../api/reference/widget_render_data_steward.md)

## Used in Workflow Template

* [`01_governance`](../../notebook-templates.md) — Agreement intake

## Model

**Authoritative writer:** `governance`

**Default physical schema:** `governance`

**Grain:** One registered Data Steward.

**Primary key:** `steward_id`

**Relationships:**

No immediate table relationship is defined in the current implementation.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 14 |
| Business columns | 6 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `steward_id` | `string` | Stable identifier for the steward row. |
| `steward_name` | `string` | Human-readable steward name. |
| `steward_role` | `string` | Configured steward role captured for the row. |
| `contact` | `string` | Contact detail captured for the steward record. |
| `is_active` | `boolean` | Whether the row is currently active. |
| `custom_fields_json` | `string` | JSON payload stored for `custom_fields_json`. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
