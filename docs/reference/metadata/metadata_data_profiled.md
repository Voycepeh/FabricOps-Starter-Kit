# METADATA_DATA_PROFILED

See the column-level profile metrics captured for a dataset snapshot.

## Writer functions

* [`profile_and_register_table`](../../api/reference/profile_and_register_table.md)

## Used in Workflow Template

* [`02_pipeline`](../../notebook-templates.md) — Profiling

## Model

**Grain:** One observed column in one profiling snapshot.

**Primary key:** `profile_id`

**Relationships:**

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `table_id` + `column_id`

`METADATA_DATA_PROFILED_FREQUENCY` **(1 → 1)**
via `profile_id` + `profile_snapshot_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 27 |
| Business columns | 19 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `profile_id` | `string` | Identifier stored for `profile_id`. |
| `profile_snapshot_id` | `string` | Identifier stored for `profile_snapshot_id`. |
| `table_id` | `string` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `column_id` | `string` | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `data_type` | `string` | Stable data type label recorded for the column. |
| `row_count` | `long` | Observed total row count in the profiled dataset snapshot. |
| `non_null_count` | `long` | Observed non-null value count for the column. |
| `null_count` | `long` | Observed null value count for the column. |
| `null_percent` | `double` | Observed null percentage for the column. |
| `distinct_count` | `long` | Observed distinct value count for the column. |
| `distinct_percent` | `double` | Observed distinct percentage for the column. |
| `mean_value` | `double` | Observed mean value for numeric columns when available. |
| `stddev_value` | `double` | Observed standard deviation for numeric columns when available. |
| `min_value` | `string` | Observed minimum value captured as text. |
| `percentile_25_value` | `double` | Observed 25th percentile for numeric columns when available. |
| `median_value` | `double` | Observed median value for numeric columns when available. |
| `percentile_75_value` | `double` | Observed 75th percentile for numeric columns when available. |
| `max_value` | `string` | Observed maximum value captured as text. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
