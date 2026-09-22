<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `METADATA_DATA_LINEAGE`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Live since: `0.2.0`

Schema since: `0.2.0`

Schema fingerprint: `8118c4fca47e8f9ea8c60b69659c43854f07852324f365cddaf58d151b6f6757`

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
| `environment_name` | `string` | Yes | FabricOps metadata schema registry | `environment_name` field in `METADATA_DATA_LINEAGE`. |
| `pipeline_role` | `string` | Yes | FabricOps metadata schema registry | `pipeline_role` field in `METADATA_DATA_LINEAGE`. |
| `_committed_by` | `string` | No | FabricOps metadata schema registry | `_committed_by` field in `METADATA_DATA_LINEAGE`. |
| `_committed_at` | `timestamp` | No | FabricOps metadata schema registry | `_committed_at` field in `METADATA_DATA_LINEAGE`. |
| `_workspace_id` | `string` | No | FabricOps metadata schema registry | `_workspace_id` field in `METADATA_DATA_LINEAGE`. |
| `_workspace_name` | `string` | No | FabricOps metadata schema registry | `_workspace_name` field in `METADATA_DATA_LINEAGE`. |
| `_notebook_id` | `string` | No | FabricOps metadata schema registry | `_notebook_id` field in `METADATA_DATA_LINEAGE`. |
| `_notebook_name` | `string` | No | FabricOps metadata schema registry | `_notebook_name` field in `METADATA_DATA_LINEAGE`. |
| `_metadata_lakehouse_name` | `string` | No | FabricOps metadata schema registry | `_metadata_lakehouse_name` field in `METADATA_DATA_LINEAGE`. |
| `_activity_id` | `string` | No | FabricOps metadata schema registry | `_activity_id` field in `METADATA_DATA_LINEAGE`. |

[Back to release overview](../index.md)
