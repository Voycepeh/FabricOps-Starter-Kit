<!-- Generated file. Edit docs/releases/manifests/0.3.0.yml or the authoritative source metadata and regenerate. -->

# `METADATA_DATA_AGREEMENT`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.3.0`

Live since: `0.2.0`

Schema since: `0.2.5`

Schema fingerprint: `fbd7de85fc0d881516613bb1e162b99558cb9ba1a95ace5e6f9aafefe49a5689`

Source path: `src/fabricops_kit/config/metadata_schemas.py`

Frozen source ref: `v0.3.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.3.0/src/fabricops_kit/config/metadata_schemas.py)

Managed by: `fabricops_kit.config.metadata_schemas.metadata_table_schema_registry`

Description: Supported FabricOps metadata table for data agreement.

## Schema

| Column name | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `agreement_id` | `string` | No | FabricOps metadata schema registry | `agreement_id` field in `METADATA_DATA_AGREEMENT`. |
| `agreement_version` | `string` | No | FabricOps metadata schema registry | `agreement_version` field in `METADATA_DATA_AGREEMENT`. |
| `agreement_name` | `string` | No | FabricOps metadata schema registry | `agreement_name` field in `METADATA_DATA_AGREEMENT`. |
| `domain` | `string` | No | FabricOps metadata schema registry | `domain` field in `METADATA_DATA_AGREEMENT`. |
| `provider_steward_id` | `string` | No | FabricOps metadata schema registry | `provider_steward_id` field in `METADATA_DATA_AGREEMENT`. |
| `provider_steward_name` | `string` | Yes | FabricOps metadata schema registry | `provider_steward_name` field in `METADATA_DATA_AGREEMENT`. |
| `recipient_steward_id` | `string` | No | FabricOps metadata schema registry | `recipient_steward_id` field in `METADATA_DATA_AGREEMENT`. |
| `recipient_steward_name` | `string` | Yes | FabricOps metadata schema registry | `recipient_steward_name` field in `METADATA_DATA_AGREEMENT`. |
| `start_date` | `date` | No | FabricOps metadata schema registry | `start_date` field in `METADATA_DATA_AGREEMENT`. |
| `expiry_date` | `date` | No | FabricOps metadata schema registry | `expiry_date` field in `METADATA_DATA_AGREEMENT`. |
| `business_purpose` | `string` | No | FabricOps metadata schema registry | `business_purpose` field in `METADATA_DATA_AGREEMENT`. |
| `supporting_documents_json` | `string` | Yes | FabricOps metadata schema registry | `supporting_documents_json` field in `METADATA_DATA_AGREEMENT`. |
| `approved_usage_json` | `string` | No | FabricOps metadata schema registry | `approved_usage_json` field in `METADATA_DATA_AGREEMENT`. |
| `custom_fields_json` | `string` | Yes | FabricOps metadata schema registry | `custom_fields_json` field in `METADATA_DATA_AGREEMENT`. |
| `_committed_by` | `string` | No | FabricOps metadata schema registry | `_committed_by` field in `METADATA_DATA_AGREEMENT`. |
| `_committed_at` | `timestamp` | No | FabricOps metadata schema registry | `_committed_at` field in `METADATA_DATA_AGREEMENT`. |
| `_workspace_id` | `string` | No | FabricOps metadata schema registry | `_workspace_id` field in `METADATA_DATA_AGREEMENT`. |
| `_workspace_name` | `string` | No | FabricOps metadata schema registry | `_workspace_name` field in `METADATA_DATA_AGREEMENT`. |
| `_notebook_id` | `string` | No | FabricOps metadata schema registry | `_notebook_id` field in `METADATA_DATA_AGREEMENT`. |
| `_notebook_name` | `string` | No | FabricOps metadata schema registry | `_notebook_name` field in `METADATA_DATA_AGREEMENT`. |
| `_metadata_lakehouse_name` | `string` | No | FabricOps metadata schema registry | `_metadata_lakehouse_name` field in `METADATA_DATA_AGREEMENT`. |
| `_activity_id` | `string` | No | FabricOps metadata schema registry | `_activity_id` field in `METADATA_DATA_AGREEMENT`. |

[Back to release overview](../index.md)
