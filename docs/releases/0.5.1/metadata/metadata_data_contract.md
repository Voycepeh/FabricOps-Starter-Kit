<!-- Generated file. Edit docs/releases/manifests/0.5.1.yml or the authoritative source metadata and regenerate. -->

# `METADATA_DATA_CONTRACT`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.5.1`

Live since: `0.3.0`

Schema since: `0.5.1`

Schema fingerprint: `e3392a76886e806ff66f843c4ffe11c2486e5b8263775f6392d672eac709d14d`

Source path: `src/fabricops_kit/config/metadata_schemas.py`

Frozen source ref: `v0.5.1`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.5.1/src/fabricops_kit/config/metadata_schemas.py)

Managed by: `fabricops_kit.config.metadata_schemas.metadata_table_schema_registry`

Description: Supported FabricOps metadata table for data contract.

## Schema

| Column name | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `contract_id` | `string` | No | FabricOps metadata schema registry | `contract_id` field in `METADATA_DATA_CONTRACT`. |
| `contract_version` | `integer` | No | FabricOps metadata schema registry | `contract_version` field in `METADATA_DATA_CONTRACT`. |
| `table_id` | `string` | Yes | FabricOps metadata schema registry | `table_id` field in `METADATA_DATA_CONTRACT`. |
| `asset_type` | `string` | Yes | FabricOps metadata schema registry | `asset_type` field in `METADATA_DATA_CONTRACT`. |
| `table_name` | `string` | Yes | FabricOps metadata schema registry | `table_name` field in `METADATA_DATA_CONTRACT`. |
| `asset_workspace_id` | `string` | No | FabricOps metadata schema registry | `asset_workspace_id` field in `METADATA_DATA_CONTRACT`. |
| `contract_payload_json` | `string` | Yes | FabricOps metadata schema registry | `contract_payload_json` field in `METADATA_DATA_CONTRACT`. |
| `status` | `string` | No | FabricOps metadata schema registry | `status` field in `METADATA_DATA_CONTRACT`. |
| `_committed_by` | `string` | No | FabricOps metadata schema registry | `_committed_by` field in `METADATA_DATA_CONTRACT`. |
| `_committed_at` | `timestamp` | No | FabricOps metadata schema registry | `_committed_at` field in `METADATA_DATA_CONTRACT`. |
| `_workspace_id` | `string` | No | FabricOps metadata schema registry | `_workspace_id` field in `METADATA_DATA_CONTRACT`. |
| `_workspace_name` | `string` | No | FabricOps metadata schema registry | `_workspace_name` field in `METADATA_DATA_CONTRACT`. |
| `_notebook_id` | `string` | No | FabricOps metadata schema registry | `_notebook_id` field in `METADATA_DATA_CONTRACT`. |
| `_notebook_name` | `string` | No | FabricOps metadata schema registry | `_notebook_name` field in `METADATA_DATA_CONTRACT`. |
| `_metadata_lakehouse_name` | `string` | No | FabricOps metadata schema registry | `_metadata_lakehouse_name` field in `METADATA_DATA_CONTRACT`. |
| `_activity_id` | `string` | No | FabricOps metadata schema registry | `_activity_id` field in `METADATA_DATA_CONTRACT`. |

[Back to release overview](../index.md)
