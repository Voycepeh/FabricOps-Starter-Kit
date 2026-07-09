<!-- Generated file. Edit docs/releases/manifests/0.1.0.yml or the authoritative source metadata and regenerate. -->

# `METADATA_DATA_AGREEMENT`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.1.0`

Live since: `0.1.0`

Schema since: `0.1.0`

Schema fingerprint: `2603c56ecfa7e797050ad0b2cdfc880821dfefb3136b0737c9aa7aa2e9f6017d`

Source path: `src/fabricops_kit/config/metadata_schemas.py`

Managed by: `fabricops_kit.config.metadata_schemas.metadata_table_schema_registry`

Description: Supported FabricOps metadata table for data agreement.

## Schema

| Column name | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `agreement_id` | `string` | No | FabricOps metadata schema registry | `agreement_id` field in `METADATA_DATA_AGREEMENT`. |
| `agreement_version` | `string` | No | FabricOps metadata schema registry | `agreement_version` field in `METADATA_DATA_AGREEMENT`. |
| `agreement_name` | `string` | No | FabricOps metadata schema registry | `agreement_name` field in `METADATA_DATA_AGREEMENT`. |
| `domain` | `string` | No | FabricOps metadata schema registry | `domain` field in `METADATA_DATA_AGREEMENT`. |
| `steward_id` | `string` | No | FabricOps metadata schema registry | `steward_id` field in `METADATA_DATA_AGREEMENT`. |
| `recipient` | `string` | No | FabricOps metadata schema registry | `recipient` field in `METADATA_DATA_AGREEMENT`. |
| `start_date` | `date` | No | FabricOps metadata schema registry | `start_date` field in `METADATA_DATA_AGREEMENT`. |
| `expiry_date` | `date` | No | FabricOps metadata schema registry | `expiry_date` field in `METADATA_DATA_AGREEMENT`. |
| `business_purpose` | `string` | No | FabricOps metadata schema registry | `business_purpose` field in `METADATA_DATA_AGREEMENT`. |
| `custom_fields_json` | `string` | Yes | FabricOps metadata schema registry | `custom_fields_json` field in `METADATA_DATA_AGREEMENT`. |
| `_committed_by` | `string` | No | FabricOps metadata schema registry | `_committed_by` field in `METADATA_DATA_AGREEMENT`. |
| `_committed_at` | `timestamp` | No | FabricOps metadata schema registry | `_committed_at` field in `METADATA_DATA_AGREEMENT`. |
| `_workspace_id` | `string` | No | FabricOps metadata schema registry | `_workspace_id` field in `METADATA_DATA_AGREEMENT`. |
| `_workspace_name` | `string` | No | FabricOps metadata schema registry | `_workspace_name` field in `METADATA_DATA_AGREEMENT`. |
| `_notebook_id` | `string` | No | FabricOps metadata schema registry | `_notebook_id` field in `METADATA_DATA_AGREEMENT`. |
| `_notebook_name` | `string` | No | FabricOps metadata schema registry | `_notebook_name` field in `METADATA_DATA_AGREEMENT`. |
| `_metadata_lakehouse_name` | `string` | No | FabricOps metadata schema registry | `_metadata_lakehouse_name` field in `METADATA_DATA_AGREEMENT`. |
| `_activity_id` | `string` | No | FabricOps metadata schema registry | `_activity_id` field in `METADATA_DATA_AGREEMENT`. |

[Back to 0.1.0 metadata tables](index.md)
