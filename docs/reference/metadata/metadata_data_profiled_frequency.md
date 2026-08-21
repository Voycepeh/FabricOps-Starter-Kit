# METADATA_DATA_PROFILED_FREQUENCY

See the frequency distribution captured for a profiled column.

## Writer functions

* [`profile_and_register_table`](../../api/reference/profile_and_register_table.md)
* [`profile_frequency_distribution`](../../api/reference/profile_frequency_distribution.md)

## Used in Workflow Template

* [`02_pipeline`](../../notebook-templates.md) — Profiling
* [`02_pipeline / optional 99_explore`](../../notebook-templates.md) — Profiling

## Model

**Grain:** One flattened ranked value within one logical frequency distribution for a column Profile.

**Primary key:** `frequency_id`

**Relationships:**

`METADATA_DATA_PROFILED` **(1 → 1)**
via `profile_id` + `profile_snapshot_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 17 |
| Business columns | 9 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `frequency_id` | `string` | Identifier stored for `frequency_id`. |
| `profile_id` | `string` | Identifier stored for `profile_id`. |
| `profile_snapshot_id` | `string` | Identifier stored for `profile_snapshot_id`. |
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
