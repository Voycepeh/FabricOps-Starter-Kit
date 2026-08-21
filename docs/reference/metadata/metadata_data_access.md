# METADATA_DATA_ACCESS

See who has row-level access to the data.

## Model

**Grain:** One RLS assignment for one user and one Catalogue table in one environment.

**Primary key:** `access_id`

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `table_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 15 |
| Business columns | 7 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `access_id` | `string` | Implemented schema registry only | Identifier stored for `access_id`. |
| `user_principal` | `string` | Implemented schema registry only | User principal recorded for the access row. |
| `table_id` | `string` | Implemented schema registry only | Identifier for the accessed table or object. |
| `environment_name` | `string` | Implemented schema registry only | Environment name recorded for the metadata row. |
| `access_level` | `string` | Implemented schema registry only | Metadata Data Access field `access_level`. |
| `access_value` | `string` | Implemented schema registry only | Metadata Data Access field `access_value`. |
| `access_state` | `string` | Implemented schema registry only | Metadata Data Access field `access_state`. |
| `_committed_by` | `string` | Implemented schema registry only | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Implemented schema registry only | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Implemented schema registry only | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Implemented schema registry only | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Implemented schema registry only | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Implemented schema registry only | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Implemented schema registry only | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Implemented schema registry only | Fabric execution activity identifier for the current notebook or pipeline run. |
