# METADATA_DATA_PROFILED_FREQUENCY

Shows which values appear most often in a column and how frequently they occur.

## Writer functions

* [`orchestrate_read`](../../api/reference/orchestrate_read.md)
* [`orchestrate_write`](../../api/reference/orchestrate_write.md)
* [`profile_table`](../../api/reference/profile_table.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One recorded value and its frequency for a column in a profiling snapshot.

**Primary key:** `frequency_id`

**Relationships:**

`METADATA_DATA_PROFILED` **(N → 1)**
via `profile_id`

**Implementation details:** Frequency distributions retain Table ID, Column ID, environment, captured names and datatype. Independently scheduled Frequency Profiling owns its activity snapshot and leaves profile_id null; combined standalone profiling may link a statistical Profile. Captured names do not follow later renames.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 23 |
| Business columns | 15 |
| Audit columns | 8 |

## Implemented schema

<div class="metadata-schema-table" markdown="1">

| Column | Data type | Description |
| --- | --- | --- |
| `frequency_id` | `string` | Identifier stored for `frequency_id`. |
| `profile_id` | `string` | Identifier stored for `profile_id`. |
| `profile_snapshot_id` | `string` | Identifier stored for `profile_snapshot_id`. |
| `table_id` | `string` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `column_id` | `string` | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `table_name` | `string` | Table name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it. |
| `column_name` | `string` | Column name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it. |
| `data_type` | `string` | Stable data type label recorded for the column. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `value` | `string` | Metadata Data Profiled Frequency field `value`. |
| `frequency_count` | `long` | Metadata Data Profiled Frequency field `frequency_count`. |
| `frequency_percent` | `double` | Metadata Data Profiled Frequency field `frequency_percent`. |
| `frequency_rank` | `integer` | Metadata Data Profiled Frequency field `frequency_rank`. |
| `profiled_row_count` | `long` | Metadata Data Profiled Frequency field `profiled_row_count`. |
| `profiled_non_null_count` | `long` | Metadata Data Profiled Frequency field `profiled_non_null_count`. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |

</div>
