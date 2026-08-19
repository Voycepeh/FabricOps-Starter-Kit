<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `METADATA_DATA_LINEAGE`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Live since: `0.2.0`

Schema since: `0.2.0`

Schema fingerprint: `f57bb30d25d4ef9a49e4bacf1d6c65542d337b6ae0c62c332b8ebdcc49e86eff`

Source path: `src/fabricops_kit/config/metadata_schemas.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/config/metadata_schemas.py)

Managed by: `fabricops_kit.config.metadata_schemas.metadata_table_schema_registry`

Description: Supported FabricOps metadata table for data lineage.

## Schema

| Column name | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `lineage_id` | `string` | Yes | FabricOps metadata schema registry | `lineage_id` field in `METADATA_DATA_LINEAGE`. |
| `table_id` | `string` | Yes | FabricOps metadata schema registry | `table_id` field in `METADATA_DATA_LINEAGE`. |
| `profile_snapshot_id` | `string` | Yes | FabricOps metadata schema registry | `profile_snapshot_id` field in `METADATA_DATA_LINEAGE`. |
| `environment_name` | `string` | Yes | FabricOps metadata schema registry | `environment_name` field in `METADATA_DATA_LINEAGE`. |
| `pipeline_role` | `string` | Yes | FabricOps metadata schema registry | `pipeline_role` field in `METADATA_DATA_LINEAGE`. |
| `recorded_at` | `timestamp` | Yes | FabricOps metadata schema registry | `recorded_at` field in `METADATA_DATA_LINEAGE`. |
| `_committed_by` | `string` | No | FabricOps metadata schema registry | `_committed_by` field in `METADATA_DATA_LINEAGE`. |
| `_committed_at` | `timestamp` | No | FabricOps metadata schema registry | `_committed_at` field in `METADATA_DATA_LINEAGE`. |
| `_workspace_id` | `string` | No | FabricOps metadata schema registry | `_workspace_id` field in `METADATA_DATA_LINEAGE`. |
| `_workspace_name` | `string` | No | FabricOps metadata schema registry | `_workspace_name` field in `METADATA_DATA_LINEAGE`. |
| `_notebook_id` | `string` | No | FabricOps metadata schema registry | `_notebook_id` field in `METADATA_DATA_LINEAGE`. |
| `_notebook_name` | `string` | No | FabricOps metadata schema registry | `_notebook_name` field in `METADATA_DATA_LINEAGE`. |
| `_metadata_lakehouse_name` | `string` | No | FabricOps metadata schema registry | `_metadata_lakehouse_name` field in `METADATA_DATA_LINEAGE`. |
| `_activity_id` | `string` | No | FabricOps metadata schema registry | `_activity_id` field in `METADATA_DATA_LINEAGE`. |

[Back to release overview](../index.md)
