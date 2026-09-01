# METADATA_DATA_LINEAGE

See which registered tables participated as sources and targets in pipeline activities.

## Writer functions

* [`read_pipeline_prep`](../../api/reference/read_pipeline_prep.md)

## Used in Workflow Template

* [`02_pipeline`](../../notebook-templates.md) — Source preparation

## Model

**Grain:** One registered table participating as a source or target in one pipeline activity.

**Primary key:** `lineage_id`

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
| `lineage_id` | `string` | Identifier stored for `lineage_id`. |
| `table_id` | `string` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `pipeline_role` | `string` | Metadata Data Lineage field `pipeline_role`. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
