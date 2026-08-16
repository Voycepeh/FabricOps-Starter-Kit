# METADATA_DATA_ACCESS

See who can use the data and how it can be used.

## Model

**Grain:** One access review record for one user and governed scope.

**Primary key:** Not defined in the current implementation.

**Relationships:**

* No immediate logical relationship is defined in the current implementation.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 22 |
| Business columns | 14 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `user_principal` | `string` | Implemented schema registry only | User principal recorded for the access row. |
| `role_name` | `string` | Implemented schema registry only | Role name recorded for the access row. |
| `permission` | `string` | Implemented schema registry only | Permission recorded for the access row. |
| `access_purpose` | `string` | Implemented schema registry only | Reason the access row exists. |
| `approval_status` | `string` | Implemented schema registry only | Approval status recorded for the access row. |
| `access_scope` | `string` | Implemented schema registry only | Scope of the recorded access entry. |
| `table_id` | `string` | Implemented schema registry only | Identifier for the accessed table or object. |
| `metadata_table_key` | `string` | Implemented schema registry only | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `metadata_column_key` | `string` | Implemented schema registry only | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `granted_date` | `date` | Implemented schema registry only | Date when access was granted. |
| `expires_at` | `timestamp` | Implemented schema registry only | Timestamp when access expires. |
| `approved_by` | `string` | Implemented schema registry only | Actor who approved the access row. |
| `approved_at` | `timestamp` | Implemented schema registry only | Timestamp when the access row was approved. |
| `notes` | `string` | Implemented schema registry only | Free-text notes recorded for the row. |
| `_committed_by` | `string` | Implemented schema registry only | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Implemented schema registry only | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Implemented schema registry only | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Implemented schema registry only | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Implemented schema registry only | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Implemented schema registry only | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Implemented schema registry only | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Implemented schema registry only | Fabric execution activity identifier for the current notebook or pipeline run. |
