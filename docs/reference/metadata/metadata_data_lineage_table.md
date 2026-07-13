# METADATA_DATA_LINEAGE_TABLE

**Purpose:** Source-to-target lineage rows written by pipeline runs.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `metadata_table_key` | `string` | No | Pipeline lineage writer | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `profile_role` | `string` | No | Pipeline lineage writer | Metadata Data Lineage Table field `profile_role`. |
| `_committed_by` | `string` | No | Runtime audit context | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | No | Runtime audit context | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | No | Runtime audit context | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | No | Runtime audit context | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | No | Runtime audit context | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | No | Runtime audit context | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | No | Runtime audit context | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md)
