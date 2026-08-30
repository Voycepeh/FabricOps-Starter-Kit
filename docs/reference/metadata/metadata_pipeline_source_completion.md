# METADATA_PIPELINE_SOURCE_COMPLETION

Mark all incremental-source checkpoints for one governed target publication as logically successful.

## Writer functions

* [`read_pipeline_prep`](../../api/reference/read_pipeline_prep.md)

## Used in Workflow Template

* [`02_pipeline`](../../notebook-templates.md) — Source preparation

## Model

**Grain:** One successful source-progress completion for one governed target publication.

**Primary key:** `completion_id`

**Relationships:**

No immediate table relationship is defined in the current implementation.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 11 |
| Business columns | 3 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `completion_id` | `string` | Identifier stored for `completion_id`. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `target_table_id` | `string` | Identifier stored for `target_table_id`. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
