# METADATA_SOURCE_OBSERVATION

See what FabricOps previously observed about the source data.

## Writer functions

No public writer function is traced in the current implementation.

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Grain:** One partition observation within one source-table observation.

**Primary key:** `observation_id` + `partition_value`

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `table_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 16 |
| Business columns | 8 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `observation_id` | `string` | Identifier stored for `observation_id`. |
| `table_id` | `string` | Identifier for the accessed table or object. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `partition_value` | `string` | String representation of the observed partition value. |
| `row_count` | `long` | Number of rows observed in the partition, or zero for a removal tombstone. |
| `min_change_value` | `string` | Earliest observed change-column value, or null for a removal tombstone. |
| `max_change_value` | `string` | Latest observed change-column value, or null for a removal tombstone. |
| `is_present` | `boolean` | Whether the partition exists in this observation; false identifies a removal tombstone. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
