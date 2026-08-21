# METADATA_DATA_ACCESS

See who has row-level access to the data.

## Writer functions

No public writer function is traced in the current implementation.

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

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

| Column | Data type | Description |
| --- | --- | --- |
| `access_id` | `string` | Identifier stored for `access_id`. |
| `user_principal` | `string` | User principal recorded for the access row. |
| `table_id` | `string` | Identifier for the accessed table or object. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `access_level` | `string` | Metadata Data Access field `access_level`. |
| `access_value` | `string` | Metadata Data Access field `access_value`. |
| `access_state` | `string` | Metadata Data Access field `access_state`. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
