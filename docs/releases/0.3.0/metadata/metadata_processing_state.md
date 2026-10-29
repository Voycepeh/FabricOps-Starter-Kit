<!-- Generated file. Edit docs/releases/manifests/0.3.0.yml or the authoritative source metadata and regenerate. -->

# `METADATA_PROCESSING_STATE`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.3.0`

Live since: `0.3.0`

Schema since: `0.3.0`

Schema fingerprint: `6b14daca178993fdf5c82723b8bf7418462eae9c1b2605d6ce2417a3d417557d`

Source path: `src/fabricops_kit/config/metadata_schemas.py`

Frozen source ref: `v0.3.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.3.0/src/fabricops_kit/config/metadata_schemas.py)

Managed by: `fabricops_kit.config.metadata_schemas.metadata_table_schema_registry`

Description: Supported FabricOps metadata table for processing state.

## Schema

| Column name | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `record_id` | `string` | No | FabricOps metadata schema registry | `record_id` field in `METADATA_PROCESSING_STATE`. |
| `record_type` | `string` | No | FabricOps metadata schema registry | `record_type` field in `METADATA_PROCESSING_STATE`. |
| `status` | `string` | No | FabricOps metadata schema registry | `status` field in `METADATA_PROCESSING_STATE`. |
| `observation_id` | `string` | Yes | FabricOps metadata schema registry | `observation_id` field in `METADATA_PROCESSING_STATE`. |
| `run_id` | `string` | Yes | FabricOps metadata schema registry | `run_id` field in `METADATA_PROCESSING_STATE`. |
| `pipeline_id` | `string` | Yes | FabricOps metadata schema registry | `pipeline_id` field in `METADATA_PROCESSING_STATE`. |
| `source_table_id` | `string` | Yes | FabricOps metadata schema registry | `source_table_id` field in `METADATA_PROCESSING_STATE`. |
| `source_table_name` | `string` | Yes | FabricOps metadata schema registry | `source_table_name` field in `METADATA_PROCESSING_STATE`. |
| `target_table_id` | `string` | Yes | FabricOps metadata schema registry | `target_table_id` field in `METADATA_PROCESSING_STATE`. |
| `target_table_name` | `string` | Yes | FabricOps metadata schema registry | `target_table_name` field in `METADATA_PROCESSING_STATE`. |
| `workspace_id` | `string` | No | FabricOps metadata schema registry | `workspace_id` field in `METADATA_PROCESSING_STATE`. |
| `observed_at` | `timestamp` | Yes | FabricOps metadata schema registry | `observed_at` field in `METADATA_PROCESSING_STATE`. |
| `accepted_at` | `timestamp` | Yes | FabricOps metadata schema registry | `accepted_at` field in `METADATA_PROCESSING_STATE`. |
| `partition_column` | `string` | Yes | FabricOps metadata schema registry | `partition_column` field in `METADATA_PROCESSING_STATE`. |
| `change_column` | `string` | Yes | FabricOps metadata schema registry | `change_column` field in `METADATA_PROCESSING_STATE`. |
| `watermark_type` | `string` | Yes | FabricOps metadata schema registry | `watermark_type` field in `METADATA_PROCESSING_STATE`. |
| `partition_value` | `string` | Yes | FabricOps metadata schema registry | `partition_value` field in `METADATA_PROCESSING_STATE`. |
| `row_count` | `long` | Yes | FabricOps metadata schema registry | `row_count` field in `METADATA_PROCESSING_STATE`. |
| `min_change_value` | `string` | Yes | FabricOps metadata schema registry | `min_change_value` field in `METADATA_PROCESSING_STATE`. |
| `max_change_value` | `string` | Yes | FabricOps metadata schema registry | `max_change_value` field in `METADATA_PROCESSING_STATE`. |
| `content_fingerprint` | `string` | Yes | FabricOps metadata schema registry | `content_fingerprint` field in `METADATA_PROCESSING_STATE`. |
| `is_present` | `boolean` | Yes | FabricOps metadata schema registry | `is_present` field in `METADATA_PROCESSING_STATE`. |
| `publication_id` | `string` | Yes | FabricOps metadata schema registry | `publication_id` field in `METADATA_PROCESSING_STATE`. |
| `publication_batch_id` | `string` | Yes | FabricOps metadata schema registry | `publication_batch_id` field in `METADATA_PROCESSING_STATE`. |
| `publication_activity_id` | `string` | Yes | FabricOps metadata schema registry | `publication_activity_id` field in `METADATA_PROCESSING_STATE`. |
| `publication_at` | `timestamp` | Yes | FabricOps metadata schema registry | `publication_at` field in `METADATA_PROCESSING_STATE`. |
| `publication_input_rows` | `long` | Yes | FabricOps metadata schema registry | `publication_input_rows` field in `METADATA_PROCESSING_STATE`. |
| `publication_strategy` | `string` | Yes | FabricOps metadata schema registry | `publication_strategy` field in `METADATA_PROCESSING_STATE`. |
| `_committed_by` | `string` | No | FabricOps metadata schema registry | `_committed_by` field in `METADATA_PROCESSING_STATE`. |
| `_committed_at` | `timestamp` | No | FabricOps metadata schema registry | `_committed_at` field in `METADATA_PROCESSING_STATE`. |
| `_workspace_id` | `string` | No | FabricOps metadata schema registry | `_workspace_id` field in `METADATA_PROCESSING_STATE`. |
| `_workspace_name` | `string` | No | FabricOps metadata schema registry | `_workspace_name` field in `METADATA_PROCESSING_STATE`. |
| `_notebook_id` | `string` | No | FabricOps metadata schema registry | `_notebook_id` field in `METADATA_PROCESSING_STATE`. |
| `_notebook_name` | `string` | No | FabricOps metadata schema registry | `_notebook_name` field in `METADATA_PROCESSING_STATE`. |
| `_metadata_lakehouse_name` | `string` | No | FabricOps metadata schema registry | `_metadata_lakehouse_name` field in `METADATA_PROCESSING_STATE`. |
| `_activity_id` | `string` | No | FabricOps metadata schema registry | `_activity_id` field in `METADATA_PROCESSING_STATE`. |

[Back to release overview](../index.md)
