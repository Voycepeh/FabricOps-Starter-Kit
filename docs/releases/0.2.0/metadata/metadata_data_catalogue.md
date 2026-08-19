<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `METADATA_DATA_CATALOGUE`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Live since: `0.2.0`

Schema since: `0.2.0`

Schema fingerprint: `f47b4691ed781db150777327efdaf179273aa603d8e41dc9db20f186e407a49a`

Source path: `src/fabricops_kit/config/metadata_schemas.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/config/metadata_schemas.py)

Managed by: `fabricops_kit.config.metadata_schemas.metadata_table_schema_registry`

Description: Supported FabricOps metadata table for data catalogue.

## Schema

| Column name | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `metadata_level` | `string` | Yes | FabricOps metadata schema registry | `metadata_level` field in `METADATA_DATA_CATALOGUE`. |
| `table_id` | `string` | Yes | FabricOps metadata schema registry | `table_id` field in `METADATA_DATA_CATALOGUE`. |
| `column_id` | `string` | Yes | FabricOps metadata schema registry | `column_id` field in `METADATA_DATA_CATALOGUE`. |
| `environment_name` | `string` | Yes | FabricOps metadata schema registry | `environment_name` field in `METADATA_DATA_CATALOGUE`. |
| `store_type` | `string` | Yes | FabricOps metadata schema registry | `store_type` field in `METADATA_DATA_CATALOGUE`. |
| `layer` | `string` | Yes | FabricOps metadata schema registry | `layer` field in `METADATA_DATA_CATALOGUE`. |
| `schema_name` | `string` | Yes | FabricOps metadata schema registry | `schema_name` field in `METADATA_DATA_CATALOGUE`. |
| `table_name` | `string` | Yes | FabricOps metadata schema registry | `table_name` field in `METADATA_DATA_CATALOGUE`. |
| `column_name` | `string` | Yes | FabricOps metadata schema registry | `column_name` field in `METADATA_DATA_CATALOGUE`. |
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
