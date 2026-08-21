# METADATA_DATA_CATALOGUE

The current structural registry of known table and column assets. table_id identifies the logical table, and column_id identifies the logical column while its normalized column name remains the same. data_type stores the current structural datatype, and is_active indicates whether the asset currently exists. Datatype changes preserve column_id, removed columns become inactive, and returning columns reuse their deterministic ID. METADATA_DATA_PROFILED retains historical observations.

## Writer functions

* [`profile_and_register_table`](../../api/reference/profile_and_register_table.md)

## Used in Workflow Template

* [`02_pipeline`](../../notebook-templates.md) — Profiling

## Model

**Grain:** One table or column asset in one environment.

**Primary key:** `environment_name` + `table_id` + `column_id`

**Relationships:**

No immediate table relationship is defined in the current implementation.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 23 |
| Business columns | 15 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `metadata_level` | `string` | Metadata Data Catalogue field `metadata_level`. |
| `table_id` | `string` | Identifier for the accessed table or object. |
| `column_id` | `string` | Identifier stored for `column_id`. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `store_type` | `string` | Configured Fabric store type recorded for the profiled dataset. |
| `layer` | `string` | The configured medallion layer where the table is stored. |
| `schema_name` | `string` | Lakehouse or warehouse schema name recorded for the dataset when available. |
| `table_name` | `string` | Physical table name recorded for the metadata row. |
| `column_name` | `string` | Physical column name recorded for the metadata row. |
| `data_type` | `string` | Stable data type label recorded for the column. |
| `load_strategy` | `string` | Metadata Data Catalogue field `load_strategy`. |
| `load_strategy_parameters_json` | `string` | JSON payload stored for `load_strategy_parameters_json`. |
| `first_profiled_at` | `timestamp` | Timestamp stored for `first_profiled_at`. |
| `last_profiled_at` | `timestamp` | Timestamp stored for `last_profiled_at`. |
| `is_active` | `boolean` | Whether the row is currently active. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
