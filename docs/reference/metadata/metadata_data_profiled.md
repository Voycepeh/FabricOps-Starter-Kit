# METADATA_DATA_PROFILED

**Purpose:** Metadata Data Profiled metadata table.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `metadata_table_key` | `string` | No | FabricOps workflow | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `metadata_column_key` | `string` | No | FabricOps workflow | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `environment_name` | `string` | No | FabricOps workflow | Metadata Data Profiled field `environment_name`. |
| `store_type` | `string` | No | FabricOps workflow | Metadata Data Profiled field `store_type`. |
| `layer` | `string` | No | FabricOps workflow | Metadata Data Profiled field `layer`. |
| `schema_name` | `string` | Yes | FabricOps workflow | Metadata Data Profiled field `schema_name`. |
| `table_name` | `string` | No | FabricOps workflow | Metadata Data Profiled field `table_name`. |
| `column_name` | `string` | No | FabricOps workflow | Metadata Data Profiled field `column_name`. |
| `data_type` | `string` | No | FabricOps workflow | Metadata Data Profiled field `data_type`. |
| `row_count` | `long` | No | FabricOps workflow | Metadata Data Profiled field `row_count`. |
| `non_null_count` | `long` | No | FabricOps workflow | Metadata Data Profiled field `non_null_count`. |
| `null_count` | `long` | No | FabricOps workflow | Metadata Data Profiled field `null_count`. |
| `null_percent` | `double` | No | FabricOps workflow | Metadata Data Profiled field `null_percent`. |
| `distinct_count` | `long` | No | FabricOps workflow | Metadata Data Profiled field `distinct_count`. |
| `distinct_percent` | `double` | No | FabricOps workflow | Metadata Data Profiled field `distinct_percent`. |
| `mean_value` | `double` | Yes | FabricOps workflow | Metadata Data Profiled field `mean_value`. |
| `stddev_value` | `double` | Yes | FabricOps workflow | Metadata Data Profiled field `stddev_value`. |
| `min_value` | `string` | Yes | FabricOps workflow | Metadata Data Profiled field `min_value`. |
| `percentile_25_value` | `double` | Yes | FabricOps workflow | Metadata Data Profiled field `percentile_25_value`. |
| `median_value` | `double` | Yes | FabricOps workflow | Metadata Data Profiled field `median_value`. |
| `percentile_75_value` | `double` | Yes | FabricOps workflow | Metadata Data Profiled field `percentile_75_value`. |
| `max_value` | `string` | Yes | FabricOps workflow | Metadata Data Profiled field `max_value`. |
| `is_sampled` | `boolean` | No | FabricOps workflow | Metadata Data Profiled field `is_sampled`. |
| `frequency_json` | `string` | Yes | FabricOps workflow | Metadata Data Profiled field `frequency_json`. |
| `schema_fingerprint` | `string` | No | FabricOps workflow | Metadata Data Profiled field `schema_fingerprint`. |
| `profiled_at` | `timestamp` | No | FabricOps workflow | Metadata Data Profiled field `profiled_at`. |
| `_committed_by` | `string` | No | Runtime audit context | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | No | Runtime audit context | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | No | Runtime audit context | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | No | Runtime audit context | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | No | Runtime audit context | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | No | Runtime audit context | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | No | Runtime audit context | Fabric execution activity identifier for the current notebook or pipeline run. |
