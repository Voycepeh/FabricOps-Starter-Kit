<!-- Generated file. Edit docs/releases/manifests/0.3.1.yml or the authoritative source metadata and regenerate. -->

# `METADATA_PIPELINE_REGISTRY`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.3.1`

Live since: `0.3.0`

Schema since: `0.3.0`

Schema fingerprint: `3b63effcb689a0b1575971c47c9817b81f25ac71273c1e4ff1673197718d2ecb`

Source path: `src/fabricops_kit/config/metadata_schemas.py`

Frozen source ref: `v0.3.1`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.3.1/src/fabricops_kit/config/metadata_schemas.py)

Managed by: `fabricops_kit.config.metadata_schemas.metadata_table_schema_registry`

Description: Supported FabricOps metadata table for pipeline registry.

## Schema

| Column name | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `authority_id` | `string` | No | FabricOps metadata schema registry | `authority_id` field in `METADATA_PIPELINE_REGISTRY`. |
| `token` | `string` | No | FabricOps metadata schema registry | `token` field in `METADATA_PIPELINE_REGISTRY`. |
| `registrations` | `array<struct<pipeline_id:string,workspace_id:string,notebook_id:string,notebook_name:string,registered_at:timestamp,registered_by:string,registration_status:string,_committed_by:string,_committed_at:timestamp,_workspace_id:string,_workspace_name:string,_notebook_id:string,_notebook_name:string,_metadata_lakehouse_name:string,_activity_id:string>>` | No | FabricOps metadata schema registry | `registrations` field in `METADATA_PIPELINE_REGISTRY`. |
| `revisions` | `array<struct<workspace_id:string,revision:string>>` | No | FabricOps metadata schema registry | `revisions` field in `METADATA_PIPELINE_REGISTRY`. |
| `approvals` | `array<struct<approval_id:string,pipeline_id:string,workspace_id:string,pipeline_name:string,pipeline_version:string,testing_run_id:string,testing_evidence_sha256:string,agreement_id:string,agreement_version:string,agreement_sha256:string,warnings:array<string>,_committed_by:string,_committed_at:timestamp,_workspace_id:string,_workspace_name:string,_notebook_id:string,_notebook_name:string,_metadata_lakehouse_name:string,_activity_id:string>>` | No | FabricOps metadata schema registry | `approvals` field in `METADATA_PIPELINE_REGISTRY`. |
| `selections` | `array<struct<workspace_id:string,pipeline_id:string,approval_id:string>>` | No | FabricOps metadata schema registry | `selections` field in `METADATA_PIPELINE_REGISTRY`. |
| `table_ownership` | `array<struct<workspace_id:string,table_id:string,contract_id:string,contract_version:int,payload_sha256:string,writer:string,readers:array<string>,destination:struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>>` | No | FabricOps metadata schema registry | `table_ownership` field in `METADATA_PIPELINE_REGISTRY`. |
| `reservations` | `array<struct<workspace_id:string,reservation_id:string,pipeline_id:string,mode:string,tables:array<string>,revision:string,destinations:array<struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>>>` | No | FabricOps metadata schema registry | `reservations` field in `METADATA_PIPELINE_REGISTRY`. |
| `_committed_by` | `string` | No | FabricOps metadata schema registry | `_committed_by` field in `METADATA_PIPELINE_REGISTRY`. |
| `_committed_at` | `timestamp` | No | FabricOps metadata schema registry | `_committed_at` field in `METADATA_PIPELINE_REGISTRY`. |
| `_workspace_id` | `string` | No | FabricOps metadata schema registry | `_workspace_id` field in `METADATA_PIPELINE_REGISTRY`. |
| `_workspace_name` | `string` | No | FabricOps metadata schema registry | `_workspace_name` field in `METADATA_PIPELINE_REGISTRY`. |
| `_notebook_id` | `string` | No | FabricOps metadata schema registry | `_notebook_id` field in `METADATA_PIPELINE_REGISTRY`. |
| `_notebook_name` | `string` | No | FabricOps metadata schema registry | `_notebook_name` field in `METADATA_PIPELINE_REGISTRY`. |
| `_metadata_lakehouse_name` | `string` | No | FabricOps metadata schema registry | `_metadata_lakehouse_name` field in `METADATA_PIPELINE_REGISTRY`. |
| `_activity_id` | `string` | No | FabricOps metadata schema registry | `_activity_id` field in `METADATA_PIPELINE_REGISTRY`. |

[Back to release overview](../index.md)
