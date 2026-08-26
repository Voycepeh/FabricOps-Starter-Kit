# METADATA_SOURCE_PARTITION_CHECKPOINT

Record which source partition observation was successfully published downstream.

## Writer functions

* [`read_pipeline_prep`](../../api/reference/read_pipeline_prep.md)

## Used in Workflow Template

* [`02_pipeline`](../../notebook-templates.md) — Source preparation

## Model

**Grain:** One successfully processed observation for one source table.

**Primary key:** `environment_name` + `table_id` + `_committed_at`

**Relationships:**

`METADATA_SOURCE_OBSERVATION` **(N → 1)**
via `observation_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 11 |
| Business columns | 3 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `table_id` | `string` | Identifier for the accessed table or object. |
| `observation_id` | `string` | Identifier stored for `observation_id`. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
