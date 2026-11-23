<!-- Generated file. Edit docs/releases/manifests/0.5.1.yml or the authoritative source metadata and regenerate. -->

# `METADATA_DATA_LINEAGE`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.5.1`

Live since: `0.2.0`

Schema since: `0.5.1`

Schema fingerprint: `95594ac5672ef71cefba6e62f923a9575a43fec1cf7e22ed2a9a1f46a662be2f`

Source path: `src/fabricops_kit/config/metadata_schemas.py`

Frozen source ref: `v0.5.1`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.5.1/src/fabricops_kit/config/metadata_schemas.py)

Managed by: `fabricops_kit.config.metadata_schemas.metadata_table_schema_registry`

Description: Supported FabricOps metadata table for data lineage.

## Schema

| Column name | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `lineage_id` | `string` | Yes | FabricOps metadata schema registry | `lineage_id` field in `METADATA_DATA_LINEAGE`. |
| `lineage_version` | `integer` | Yes | FabricOps metadata schema registry | `lineage_version` field in `METADATA_DATA_LINEAGE`. |
| `record_type` | `string` | Yes | FabricOps metadata schema registry | `record_type` field in `METADATA_DATA_LINEAGE`. |
| `run_id` | `string` | Yes | FabricOps metadata schema registry | `run_id` field in `METADATA_DATA_LINEAGE`. |
| `operation_key` | `string` | Yes | FabricOps metadata schema registry | `operation_key` field in `METADATA_DATA_LINEAGE`. |
| `publication_status` | `string` | Yes | FabricOps metadata schema registry | `publication_status` field in `METADATA_DATA_LINEAGE`. |
| `coverage` | `string` | Yes | FabricOps metadata schema registry | `coverage` field in `METADATA_DATA_LINEAGE`. |
| `target_asset_workspace_id` | `string` | Yes | FabricOps metadata schema registry | `target_asset_workspace_id` field in `METADATA_DATA_LINEAGE`. |
| `target_table_id` | `string` | Yes | FabricOps metadata schema registry | `target_table_id` field in `METADATA_DATA_LINEAGE`. |
| `target_asset_type` | `string` | Yes | FabricOps metadata schema registry | `target_asset_type` field in `METADATA_DATA_LINEAGE`. |
| `target_column_id` | `string` | Yes | FabricOps metadata schema registry | `target_column_id` field in `METADATA_DATA_LINEAGE`. |
| `target_column_name` | `string` | Yes | FabricOps metadata schema registry | `target_column_name` field in `METADATA_DATA_LINEAGE`. |
| `source_asset_workspace_id` | `string` | Yes | FabricOps metadata schema registry | `source_asset_workspace_id` field in `METADATA_DATA_LINEAGE`. |
| `source_table_id` | `string` | Yes | FabricOps metadata schema registry | `source_table_id` field in `METADATA_DATA_LINEAGE`. |
| `source_asset_type` | `string` | Yes | FabricOps metadata schema registry | `source_asset_type` field in `METADATA_DATA_LINEAGE`. |
| `source_column_id` | `string` | Yes | FabricOps metadata schema registry | `source_column_id` field in `METADATA_DATA_LINEAGE`. |
| `source_column_name` | `string` | Yes | FabricOps metadata schema registry | `source_column_name` field in `METADATA_DATA_LINEAGE`. |
| `dependency_type` | `string` | Yes | FabricOps metadata schema registry | `dependency_type` field in `METADATA_DATA_LINEAGE`. |
| `_committed_by` | `string` | No | FabricOps metadata schema registry | `_committed_by` field in `METADATA_DATA_LINEAGE`. |
| `_committed_at` | `timestamp` | No | FabricOps metadata schema registry | `_committed_at` field in `METADATA_DATA_LINEAGE`. |
| `_workspace_id` | `string` | No | FabricOps metadata schema registry | `_workspace_id` field in `METADATA_DATA_LINEAGE`. |
| `_workspace_name` | `string` | No | FabricOps metadata schema registry | `_workspace_name` field in `METADATA_DATA_LINEAGE`. |
| `_notebook_id` | `string` | No | FabricOps metadata schema registry | `_notebook_id` field in `METADATA_DATA_LINEAGE`. |
| `_notebook_name` | `string` | No | FabricOps metadata schema registry | `_notebook_name` field in `METADATA_DATA_LINEAGE`. |
| `_metadata_lakehouse_name` | `string` | No | FabricOps metadata schema registry | `_metadata_lakehouse_name` field in `METADATA_DATA_LINEAGE`. |
| `_activity_id` | `string` | No | FabricOps metadata schema registry | `_activity_id` field in `METADATA_DATA_LINEAGE`. |

[Back to release overview](../index.md)
