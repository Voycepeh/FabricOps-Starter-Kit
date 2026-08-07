<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `METADATA_DATA_PROFILED`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Live since: `0.2.0`

Schema since: `0.2.0`

Schema fingerprint: `29054258497f6bc8d6ead1f709752c552ccda9688f879cb17fb7de11443e06e0`

Source path: `src/fabricops_kit/config/metadata_schemas.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/config/metadata_schemas.py)

Managed by: `fabricops_kit.config.metadata_schemas.metadata_table_schema_registry`

Description: Supported FabricOps metadata table for data profiled.

## Schema

| Column name | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `metadata_table_key` | `string` | No | FabricOps metadata schema registry | `metadata_table_key` field in `METADATA_DATA_PROFILED`. |
| `metadata_column_key` | `string` | No | FabricOps metadata schema registry | `metadata_column_key` field in `METADATA_DATA_PROFILED`. |
| `environment_name` | `string` | No | FabricOps metadata schema registry | `environment_name` field in `METADATA_DATA_PROFILED`. |
| `store_type` | `string` | No | FabricOps metadata schema registry | `store_type` field in `METADATA_DATA_PROFILED`. |
| `layer` | `string` | No | FabricOps metadata schema registry | `layer` field in `METADATA_DATA_PROFILED`. |
| `schema_name` | `string` | Yes | FabricOps metadata schema registry | `schema_name` field in `METADATA_DATA_PROFILED`. |
| `table_name` | `string` | No | FabricOps metadata schema registry | `table_name` field in `METADATA_DATA_PROFILED`. |
| `column_name` | `string` | No | FabricOps metadata schema registry | `column_name` field in `METADATA_DATA_PROFILED`. |
| `data_type` | `string` | No | FabricOps metadata schema registry | `data_type` field in `METADATA_DATA_PROFILED`. |
| `row_count` | `long` | No | FabricOps metadata schema registry | `row_count` field in `METADATA_DATA_PROFILED`. |
| `non_null_count` | `long` | No | FabricOps metadata schema registry | `non_null_count` field in `METADATA_DATA_PROFILED`. |
| `null_count` | `long` | No | FabricOps metadata schema registry | `null_count` field in `METADATA_DATA_PROFILED`. |
| `null_percent` | `double` | No | FabricOps metadata schema registry | `null_percent` field in `METADATA_DATA_PROFILED`. |
| `distinct_count` | `long` | No | FabricOps metadata schema registry | `distinct_count` field in `METADATA_DATA_PROFILED`. |
| `distinct_percent` | `double` | No | FabricOps metadata schema registry | `distinct_percent` field in `METADATA_DATA_PROFILED`. |
| `mean_value` | `double` | Yes | FabricOps metadata schema registry | `mean_value` field in `METADATA_DATA_PROFILED`. |
| `stddev_value` | `double` | Yes | FabricOps metadata schema registry | `stddev_value` field in `METADATA_DATA_PROFILED`. |
| `min_value` | `string` | Yes | FabricOps metadata schema registry | `min_value` field in `METADATA_DATA_PROFILED`. |
| `percentile_25_value` | `double` | Yes | FabricOps metadata schema registry | `percentile_25_value` field in `METADATA_DATA_PROFILED`. |
| `median_value` | `double` | Yes | FabricOps metadata schema registry | `median_value` field in `METADATA_DATA_PROFILED`. |
| `percentile_75_value` | `double` | Yes | FabricOps metadata schema registry | `percentile_75_value` field in `METADATA_DATA_PROFILED`. |
| `max_value` | `string` | Yes | FabricOps metadata schema registry | `max_value` field in `METADATA_DATA_PROFILED`. |
| `schema_fingerprint` | `string` | No | FabricOps metadata schema registry | `schema_fingerprint` field in `METADATA_DATA_PROFILED`. |
| `profiled_at` | `timestamp` | No | FabricOps metadata schema registry | `profiled_at` field in `METADATA_DATA_PROFILED`. |
| `_committed_by` | `string` | No | FabricOps metadata schema registry | `_committed_by` field in `METADATA_DATA_PROFILED`. |
| `_committed_at` | `timestamp` | No | FabricOps metadata schema registry | `_committed_at` field in `METADATA_DATA_PROFILED`. |
| `_workspace_id` | `string` | No | FabricOps metadata schema registry | `_workspace_id` field in `METADATA_DATA_PROFILED`. |
| `_workspace_name` | `string` | No | FabricOps metadata schema registry | `_workspace_name` field in `METADATA_DATA_PROFILED`. |
| `_notebook_id` | `string` | No | FabricOps metadata schema registry | `_notebook_id` field in `METADATA_DATA_PROFILED`. |
| `_notebook_name` | `string` | No | FabricOps metadata schema registry | `_notebook_name` field in `METADATA_DATA_PROFILED`. |
| `_metadata_lakehouse_name` | `string` | No | FabricOps metadata schema registry | `_metadata_lakehouse_name` field in `METADATA_DATA_PROFILED`. |
| `_activity_id` | `string` | No | FabricOps metadata schema registry | `_activity_id` field in `METADATA_DATA_PROFILED`. |

[Back to release overview](../index.md)
