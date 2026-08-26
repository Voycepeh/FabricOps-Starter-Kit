# METADATA_SOURCE_WATERMARK_CHECKPOINT

Record how far a successfully completed watermark pipeline has processed.

## Writer functions

* [`commit_pipeline_checkpoint`](../../api/reference/commit_pipeline_checkpoint.md)
* [`read_pipeline_prep`](../../api/reference/read_pipeline_prep.md)

## Used in Workflow Template

* [`02_pipeline`](../../notebook-templates.md) — Source preparation
* [`02_pipeline`](../../notebook-templates.md) — Target persistence

## Model

**Grain:** One successfully committed watermark for one source table and watermark column.

**Primary key:** `environment_name` + `table_id` + `watermark_column` + `_committed_at`

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `table_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 12 |
| Business columns | 4 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `table_id` | `string` | Identifier for the accessed table or object. |
| `watermark_column` | `string` | Metadata Source Watermark Checkpoint field `watermark_column`. |
| `watermark_value` | `string` | Metadata Source Watermark Checkpoint field `watermark_value`. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
