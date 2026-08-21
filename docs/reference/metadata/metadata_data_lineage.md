# METADATA_DATA_LINEAGE

See where the data came from and where it ends up.

## Writer functions

* [`profile_and_register_table`](../../api/reference/profile_and_register_table.md)

## Used in Workflow Template

* [`02_pipeline`](../../notebook-templates.md) — Profiling

## Model

**Grain:** One table participating as a source or target in one pipeline/profiling execution.

**Primary key:** `lineage_id`

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `table_id`

`METADATA_DATA_PROFILED` **(N → 1)**
via `profile_snapshot_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 13 |
| Business columns | 5 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `lineage_id` | `string` | Identifier stored for `lineage_id`. |
| `table_id` | `string` | Identifier for the accessed table or object. |
| `profile_snapshot_id` | `string` | Identifier stored for `profile_snapshot_id`. |
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
