# METADATA_DATA_ACCESS

**Purpose:** Externally collected access inventory for workspace, object, schema, and table access review.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `user_principal` | `string` | Yes | External access inventory | Metadata Data Access field `user_principal`. |
| `role_name` | `string` | Yes | External access inventory | Metadata Data Access field `role_name`. |
| `permission` | `string` | Yes | External access inventory | Metadata Data Access field `permission`. |
| `access_purpose` | `string` | Yes | External access inventory | Metadata Data Access field `access_purpose`. |
| `approval_status` | `string` | Yes | External access inventory | Metadata Data Access field `approval_status`. |
| `access_scope` | `string` | Yes | External access inventory | Metadata Data Access field `access_scope`. |
| `table_id` | `string` | Yes | External access inventory | Metadata Data Access field `table_id`. |
| `metadata_table_key` | `string` | Yes | External access inventory | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `metadata_column_key` | `string` | Yes | External access inventory | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `granted_date` | `date` | Yes | External access inventory | Metadata Data Access field `granted_date`. |
| `expires_at` | `timestamp` | Yes | External access inventory | Metadata Data Access field `expires_at`. |
| `approved_by` | `string` | Yes | External access inventory | Metadata Data Access field `approved_by`. |
| `approved_at` | `timestamp` | Yes | External access inventory | Metadata Data Access field `approved_at`. |
| `notes` | `string` | Yes | External access inventory | Metadata Data Access field `notes`. |
| `_committed_by` | `string` | Yes | Future access widget | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Yes | Future access widget | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Yes | Future access widget | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Yes | Future access widget | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Yes | Future access widget | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Yes | Future access widget | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Yes | Future access widget | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Yes | Future access widget | Fabric execution activity identifier for the current notebook or pipeline run. |
