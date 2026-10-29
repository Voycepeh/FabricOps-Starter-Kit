<!-- Generated file. Edit docs/releases/manifests/0.3.0.yml or the authoritative source metadata and regenerate. -->

# `METADATA_DATA_CATALOGUE`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.3.0`

Live since: `0.2.0`

Schema since: `0.3.0`

Schema fingerprint: `14937d66c052e4e41226c0dc2b072cb6afb659316fa23b65c1daf50c0693ca08`

Source path: `src/fabricops_kit/config/metadata_schemas.py`

Frozen source ref: `v0.3.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.3.0/src/fabricops_kit/config/metadata_schemas.py)

Managed by: `fabricops_kit.config.metadata_schemas.metadata_table_schema_registry`

Description: Supported FabricOps metadata table for data catalogue.

## Schema

| Column name | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `metadata_level` | `string` | Yes | FabricOps metadata schema registry | `metadata_level` field in `METADATA_DATA_CATALOGUE`. |
| `table_id` | `string` | Yes | FabricOps metadata schema registry | `table_id` field in `METADATA_DATA_CATALOGUE`. |
| `column_id` | `string` | Yes | FabricOps metadata schema registry | `column_id` field in `METADATA_DATA_CATALOGUE`. |
| `workspace_id` | `string` | Yes | FabricOps metadata schema registry | `workspace_id` field in `METADATA_DATA_CATALOGUE`. |
| `store_type` | `string` | Yes | FabricOps metadata schema registry | `store_type` field in `METADATA_DATA_CATALOGUE`. |
| `layer` | `string` | Yes | FabricOps metadata schema registry | `layer` field in `METADATA_DATA_CATALOGUE`. |
| `schema_name` | `string` | Yes | FabricOps metadata schema registry | `schema_name` field in `METADATA_DATA_CATALOGUE`. |
| `table_name` | `string` | Yes | FabricOps metadata schema registry | `table_name` field in `METADATA_DATA_CATALOGUE`. |
| `column_name` | `string` | Yes | FabricOps metadata schema registry | `column_name` field in `METADATA_DATA_CATALOGUE`. |
| `data_type` | `string` | Yes | FabricOps metadata schema registry | `data_type` field in `METADATA_DATA_CATALOGUE`. |
| `load_strategy` | `string` | Yes | FabricOps metadata schema registry | `load_strategy` field in `METADATA_DATA_CATALOGUE`. |
| `load_strategy_parameters_json` | `struct<watermark_column:string,key_columns:array<string>,effective_column:string,tracked_columns:array<string>>` | Yes | FabricOps metadata schema registry | `load_strategy_parameters_json` field in `METADATA_DATA_CATALOGUE`. |
| `writer_workspace_id` | `string` | Yes | FabricOps metadata schema registry | `writer_workspace_id` field in `METADATA_DATA_CATALOGUE`. |
| `writer_notebook_id` | `string` | Yes | FabricOps metadata schema registry | `writer_notebook_id` field in `METADATA_DATA_CATALOGUE`. |
| `writer_notebook_name` | `string` | Yes | FabricOps metadata schema registry | `writer_notebook_name` field in `METADATA_DATA_CATALOGUE`. |
| `scheduled_refresh_json` | `struct<status:string,schedules:array<struct<enabled:boolean,frequency:string,times:array<string>,timezone:string>>>` | Yes | FabricOps metadata schema registry | `scheduled_refresh_json` field in `METADATA_DATA_CATALOGUE`. |
| `profile_key_candidates_json` | `struct<status:string,max_combination_width:int,candidates:array<struct<columns:array<string>,column_count:int,row_count:bigint,distinct_count:bigint,uniqueness_percent:double,null_count:bigint>>>` | Yes | FabricOps metadata schema registry | `profile_key_candidates_json` field in `METADATA_DATA_CATALOGUE`. |
| `first_profiled_at` | `timestamp` | Yes | FabricOps metadata schema registry | `first_profiled_at` field in `METADATA_DATA_CATALOGUE`. |
| `last_profiled_at` | `timestamp` | Yes | FabricOps metadata schema registry | `last_profiled_at` field in `METADATA_DATA_CATALOGUE`. |
| `is_active` | `boolean` | Yes | FabricOps metadata schema registry | `is_active` field in `METADATA_DATA_CATALOGUE`. |
| `_committed_by` | `string` | No | FabricOps metadata schema registry | `_committed_by` field in `METADATA_DATA_CATALOGUE`. |
| `_committed_at` | `timestamp` | No | FabricOps metadata schema registry | `_committed_at` field in `METADATA_DATA_CATALOGUE`. |
| `_workspace_id` | `string` | No | FabricOps metadata schema registry | `_workspace_id` field in `METADATA_DATA_CATALOGUE`. |
| `_workspace_name` | `string` | No | FabricOps metadata schema registry | `_workspace_name` field in `METADATA_DATA_CATALOGUE`. |
| `_notebook_id` | `string` | No | FabricOps metadata schema registry | `_notebook_id` field in `METADATA_DATA_CATALOGUE`. |
| `_notebook_name` | `string` | No | FabricOps metadata schema registry | `_notebook_name` field in `METADATA_DATA_CATALOGUE`. |
| `_metadata_lakehouse_name` | `string` | No | FabricOps metadata schema registry | `_metadata_lakehouse_name` field in `METADATA_DATA_CATALOGUE`. |
| `_activity_id` | `string` | No | FabricOps metadata schema registry | `_activity_id` field in `METADATA_DATA_CATALOGUE`. |

[Back to release overview](../index.md)
