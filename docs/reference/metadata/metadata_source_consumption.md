# METADATA_SOURCE_CONSUMPTION

Store the source observation last successfully consumed by one logical notebook when writing one governed target.

## Writer functions

No public writer function is traced in the current implementation.

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One accepted source observation for one notebook_name, source_table_id, target_table_id, and successful run.

**Primary key:** `source_consumption_id`

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `source_table_id` + `target_table_id`

`METADATA_SOURCE_OBSERVATION` **(N → 1)**
via `observation_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 15 |
| Business columns | 7 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `source_consumption_id` | `string` | Identifier stored for `source_consumption_id`. |
| `notebook_name` | `string` | Fabric notebook name captured for the lineage row. |
| `source_table_id` | `string` | Identifier stored for `source_table_id`. |
| `target_table_id` | `string` | Identifier stored for `target_table_id`. |
| `observation_id` | `string` | Identifier stored for `observation_id`. |
| `run_id` | `string` | Identifier stored for `run_id`. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
