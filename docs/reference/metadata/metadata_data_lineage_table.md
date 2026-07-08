# METADATA_DATA_LINEAGE_TABLE

**Purpose:** Source-to-target lineage rows written by pipeline runs.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `lineage_id` | `string` | No | Pipeline lineage writer | Metadata Data Lineage Table field `lineage_id`. |
| `dataset_name` | `string` | No | Pipeline lineage writer | Metadata Data Lineage Table field `dataset_name`. |
| `source_table` | `string` | No | Pipeline lineage writer | Metadata Data Lineage Table field `source_table`. |
| `target_table` | `string` | No | Pipeline lineage writer | Metadata Data Lineage Table field `target_table`. |
| `source_table_key` | `string` | No | Pipeline lineage writer | Metadata Data Lineage Table field `source_table_key`. |
| `target_table_key` | `string` | No | Pipeline lineage writer | Metadata Data Lineage Table field `target_table_key`. |
| `transformation_steps_json` | `string` | Yes | Pipeline lineage writer | Metadata Data Lineage Table field `transformation_steps_json`. |
| `_committed_by` | `string` | No | Runtime audit context | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | No | Runtime audit context | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | No | Runtime audit context | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | No | Runtime audit context | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | No | Runtime audit context | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | No | Runtime audit context | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | No | Runtime audit context | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`write_pipeline_lineage`](../../api/reference/write_pipeline_lineage.md)
