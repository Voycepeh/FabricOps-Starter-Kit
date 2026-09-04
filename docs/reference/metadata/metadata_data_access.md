# METADATA_DATA_ACCESS

See the SQL permissions observed for governed tables, including direct and role-based access.

## Writer functions

No public writer function is traced in the current implementation.

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Grain:** One observed SQL permission row for one principal and one governed table within one access snapshot.

**Primary key:** `access_id`

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `table_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 23 |
| Business columns | 15 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `access_id` | `string` | Stable identifier for one observed SQL permission row. |
| `user_principal` | `string` | SQL principal name observed for the permission row. |
| `table_id` | `string` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `access_level` | `string` | SQL permission class or scope, such as SCHEMA or OBJECT_OR_COLUMN. |
| `access_value` | `string` | SQL permission name, such as SELECT. |
| `access_state` | `string` | Observed SQL permission state, such as GRANT or DENY. |
| `access_snapshot_id` | `string` | Identifier grouping permission rows captured in the same access inventory snapshot. |
| `user_type` | `string` | SQL principal type observed for the permission row. |
| `role_name` | `string` | Database role through which the permission is inherited when applicable. |
| `permission_source` | `string` | Whether the observed permission is direct or inherited through a database role. |
| `database_name` | `string` | Database containing the observed permission scope. |
| `schema_name` | `string` | Lakehouse or warehouse schema name recorded for the dataset when available. |
| `object_name` | `string` | Database object name covered by the observed permission when applicable. |
| `object_type` | `string` | Database object type covered by the observed permission when applicable. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
