<!-- Generated file. Edit docs/releases/manifests/0.5.0.yml or the authoritative source metadata and regenerate. -->

# `METADATA_DATA_CONTRACT_ACTIVATION`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.5.0`

Live since: `0.4.0`

Schema since: `0.5.0`

Schema fingerprint: `ea73f57a265cbeab0e6d31ceabf755941969c11ad9f6480d30b63a243b167fe8`

Source path: `src/fabricops_kit/config/metadata_schemas.py`

Frozen source ref: `v0.5.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.5.0/src/fabricops_kit/config/metadata_schemas.py)

Managed by: `fabricops_kit.config.metadata_schemas.metadata_table_schema_registry`

Description: Supported FabricOps metadata table for data contract activation.

## Schema

| Column name | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `workspace_id` | `string` | No | FabricOps metadata schema registry | `workspace_id` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `table_id` | `string` | Yes | FabricOps metadata schema registry | `table_id` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `source_id` | `string` | Yes | FabricOps metadata schema registry | `source_id` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `contract_id` | `string` | No | FabricOps metadata schema registry | `contract_id` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `contract_version` | `integer` | No | FabricOps metadata schema registry | `contract_version` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `payload_sha256` | `string` | No | FabricOps metadata schema registry | `payload_sha256` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `activation_id` | `string` | No | FabricOps metadata schema registry | `activation_id` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `revision` | `integer` | No | FabricOps metadata schema registry | `revision` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `status` | `string` | No | FabricOps metadata schema registry | `status` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `destination_json` | `string` | No | FabricOps metadata schema registry | `destination_json` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `activated_at` | `timestamp` | No | FabricOps metadata schema registry | `activated_at` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `agreement_id` | `string` | Yes | FabricOps metadata schema registry | `agreement_id` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `agreement_version` | `string` | Yes | FabricOps metadata schema registry | `agreement_version` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `agreement_sha256` | `string` | Yes | FabricOps metadata schema registry | `agreement_sha256` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `_committed_by` | `string` | No | FabricOps metadata schema registry | `_committed_by` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `_committed_at` | `timestamp` | No | FabricOps metadata schema registry | `_committed_at` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `_workspace_id` | `string` | No | FabricOps metadata schema registry | `_workspace_id` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `_workspace_name` | `string` | No | FabricOps metadata schema registry | `_workspace_name` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `_notebook_id` | `string` | No | FabricOps metadata schema registry | `_notebook_id` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `_notebook_name` | `string` | No | FabricOps metadata schema registry | `_notebook_name` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `_metadata_lakehouse_name` | `string` | No | FabricOps metadata schema registry | `_metadata_lakehouse_name` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |
| `_activity_id` | `string` | No | FabricOps metadata schema registry | `_activity_id` field in `METADATA_DATA_CONTRACT_ACTIVATION`. |

[Back to release overview](../index.md)
