<!-- Generated file. Edit docs/releases/manifests/0.1.0.yml or the authoritative source metadata and regenerate. -->

# `METADATA_DATA_STEWARD`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.1.0`

Live since: `0.1.0`

Schema since: `0.1.0`

Schema fingerprint: `664c637c222e7abf02b70a6c1da5177b49f122a5105956f853842df77b1bb913`

Source path: `src/fabricops_kit/config/metadata_schemas.py`

Managed by: `fabricops_kit.config.metadata_schemas.metadata_table_schema_registry`

Description: Supported FabricOps metadata table for data steward.

## Schema

| Column name | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `steward_id` | `string` | Yes | FabricOps metadata schema registry | `steward_id` field in `METADATA_DATA_STEWARD`. |
| `steward_name` | `string` | Yes | FabricOps metadata schema registry | `steward_name` field in `METADATA_DATA_STEWARD`. |
| `steward_role` | `string` | Yes | FabricOps metadata schema registry | `steward_role` field in `METADATA_DATA_STEWARD`. |
| `contact` | `string` | Yes | FabricOps metadata schema registry | `contact` field in `METADATA_DATA_STEWARD`. |
| `effective_from` | `date` | Yes | FabricOps metadata schema registry | `effective_from` field in `METADATA_DATA_STEWARD`. |
| `effective_to` | `date` | Yes | FabricOps metadata schema registry | `effective_to` field in `METADATA_DATA_STEWARD`. |
| `is_active` | `boolean` | Yes | FabricOps metadata schema registry | `is_active` field in `METADATA_DATA_STEWARD`. |
| `custom_fields_json` | `string` | Yes | FabricOps metadata schema registry | `custom_fields_json` field in `METADATA_DATA_STEWARD`. |
| `_committed_by` | `string` | No | FabricOps metadata schema registry | `_committed_by` field in `METADATA_DATA_STEWARD`. |
| `_committed_at` | `timestamp` | No | FabricOps metadata schema registry | `_committed_at` field in `METADATA_DATA_STEWARD`. |
| `_workspace_id` | `string` | No | FabricOps metadata schema registry | `_workspace_id` field in `METADATA_DATA_STEWARD`. |
| `_workspace_name` | `string` | No | FabricOps metadata schema registry | `_workspace_name` field in `METADATA_DATA_STEWARD`. |
| `_notebook_id` | `string` | No | FabricOps metadata schema registry | `_notebook_id` field in `METADATA_DATA_STEWARD`. |
| `_notebook_name` | `string` | No | FabricOps metadata schema registry | `_notebook_name` field in `METADATA_DATA_STEWARD`. |
| `_metadata_lakehouse_name` | `string` | No | FabricOps metadata schema registry | `_metadata_lakehouse_name` field in `METADATA_DATA_STEWARD`. |
| `_activity_id` | `string` | No | FabricOps metadata schema registry | `_activity_id` field in `METADATA_DATA_STEWARD`. |

[Back to 0.1.0 metadata tables](index.md)
