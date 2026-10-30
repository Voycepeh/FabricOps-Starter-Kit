<!-- Generated file. Edit docs/releases/manifests/0.3.0.yml or the authoritative source metadata and regenerate. -->

# `METADATA_PIPELINE_RUN`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.3.0`

Live since: `0.3.0`

Schema since: `0.3.0`

Schema fingerprint: `40990a1514e5116e46107c4a3e84ec48aab826880e2ff0c66dbca851c1a818d1`

Source path: `src/fabricops_kit/config/metadata_schemas.py`

Frozen source ref: `v0.3.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.3.0/src/fabricops_kit/config/metadata_schemas.py)

Managed by: `fabricops_kit.config.metadata_schemas.metadata_table_schema_registry`

Description: Supported FabricOps metadata table for pipeline run.

## Schema

| Column name | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `run_id` | `string` | No | FabricOps metadata schema registry | `run_id` field in `METADATA_PIPELINE_RUN`. |
| `approval_id` | `string` | Yes | FabricOps metadata schema registry | `approval_id` field in `METADATA_PIPELINE_RUN`. |
| `pipeline_id` | `string` | No | FabricOps metadata schema registry | `pipeline_id` field in `METADATA_PIPELINE_RUN`. |
| `execution_mode` | `string` | No | FabricOps metadata schema registry | `execution_mode` field in `METADATA_PIPELINE_RUN`. |
| `workspace_id` | `string` | No | FabricOps metadata schema registry | `workspace_id` field in `METADATA_PIPELINE_RUN`. |
| `started_at` | `timestamp` | No | FabricOps metadata schema registry | `started_at` field in `METADATA_PIPELINE_RUN`. |
| `completed_at` | `timestamp` | Yes | FabricOps metadata schema registry | `completed_at` field in `METADATA_PIPELINE_RUN`. |
| `status` | `string` | No | FabricOps metadata schema registry | `status` field in `METADATA_PIPELINE_RUN`. |
| `activation_revision` | `string` | Yes | FabricOps metadata schema registry | `activation_revision` field in `METADATA_PIPELINE_RUN`. |
| `boundary_completed` | `boolean` | No | FabricOps metadata schema registry | `boundary_completed` field in `METADATA_PIPELINE_RUN`. |
| `operations` | `array<struct<operation_key:string,table_id:string,pipeline_role:string,contract_id:string,contract_version:int,payload_sha256:string,destination:struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>,read_mode:string,write_mode:string,query_sha256:string,source_table_ids:array<string>,incremental_target_table_id:string,status:string,started_at:timestamp,completed_at:timestamp,stages:array<struct<stage:string,status:string,evaluation_status:string>>>>` | No | FabricOps metadata schema registry | `operations` field in `METADATA_PIPELINE_RUN`. |
| `profiling` | `array<struct<context_key:string,activity:string,status:string,results_persisted:boolean,empty_result:boolean,profile_snapshot_id:string,completed_at:string,reason:string,table_id:string,row_count:bigint,trigger:string,workspace_id:string,pipeline_run_id:string,executed_at:string,physical:struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>>` | No | FabricOps metadata schema registry | `profiling` field in `METADATA_PIPELINE_RUN`. |
| `warnings_json` | `string` | No | FabricOps metadata schema registry | `warnings_json` field in `METADATA_PIPELINE_RUN`. |
| `failures` | `array<struct<code:string,exception_type:string>>` | No | FabricOps metadata schema registry | `failures` field in `METADATA_PIPELINE_RUN`. |
| `_committed_by` | `string` | No | FabricOps metadata schema registry | `_committed_by` field in `METADATA_PIPELINE_RUN`. |
| `_committed_at` | `timestamp` | No | FabricOps metadata schema registry | `_committed_at` field in `METADATA_PIPELINE_RUN`. |
| `_workspace_id` | `string` | No | FabricOps metadata schema registry | `_workspace_id` field in `METADATA_PIPELINE_RUN`. |
| `_workspace_name` | `string` | No | FabricOps metadata schema registry | `_workspace_name` field in `METADATA_PIPELINE_RUN`. |
| `_notebook_id` | `string` | No | FabricOps metadata schema registry | `_notebook_id` field in `METADATA_PIPELINE_RUN`. |
| `_notebook_name` | `string` | No | FabricOps metadata schema registry | `_notebook_name` field in `METADATA_PIPELINE_RUN`. |
| `_metadata_lakehouse_name` | `string` | No | FabricOps metadata schema registry | `_metadata_lakehouse_name` field in `METADATA_PIPELINE_RUN`. |
| `_activity_id` | `string` | No | FabricOps metadata schema registry | `_activity_id` field in `METADATA_PIPELINE_RUN`. |

[Back to release overview](../index.md)
