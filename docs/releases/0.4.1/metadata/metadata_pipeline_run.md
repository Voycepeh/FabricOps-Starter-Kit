<!-- Generated file. Edit docs/releases/manifests/0.4.1.yml or the authoritative source metadata and regenerate. -->

# `METADATA_PIPELINE_RUN`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.4.1`

Live since: `0.3.0`

Schema since: `0.4.0`

Schema fingerprint: `c57b4097c6ebb97434512384a3172275c867345afb022e3b2a5f39fb4542a0c0`

Source path: `src/fabricops_kit/config/metadata_schemas.py`

Frozen source ref: `v0.4.1`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.4.1/src/fabricops_kit/config/metadata_schemas.py)

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
| `pipeline_version` | `integer` | Yes | FabricOps metadata schema registry | `pipeline_version` field in `METADATA_PIPELINE_RUN`. |
| `promotion_id` | `string` | Yes | FabricOps metadata schema registry | `promotion_id` field in `METADATA_PIPELINE_RUN`. |
| `governed_notebook_id` | `string` | Yes | FabricOps metadata schema registry | `governed_notebook_id` field in `METADATA_PIPELINE_RUN`. |
| `execution_identity` | `string` | Yes | FabricOps metadata schema registry | `execution_identity` field in `METADATA_PIPELINE_RUN`. |
| `run_schema_version` | `integer` | Yes | FabricOps metadata schema registry | `run_schema_version` field in `METADATA_PIPELINE_RUN`. |
| `operations` | `string` | No | FabricOps metadata schema registry | `operations` field in `METADATA_PIPELINE_RUN`. |
| `profiling` | `string` | No | FabricOps metadata schema registry | `profiling` field in `METADATA_PIPELINE_RUN`. |
| `warnings_json` | `string` | No | FabricOps metadata schema registry | `warnings_json` field in `METADATA_PIPELINE_RUN`. |
| `failures` | `string` | No | FabricOps metadata schema registry | `failures` field in `METADATA_PIPELINE_RUN`. |
| `_committed_by` | `string` | No | FabricOps metadata schema registry | `_committed_by` field in `METADATA_PIPELINE_RUN`. |
| `_committed_at` | `timestamp` | No | FabricOps metadata schema registry | `_committed_at` field in `METADATA_PIPELINE_RUN`. |
| `_workspace_id` | `string` | No | FabricOps metadata schema registry | `_workspace_id` field in `METADATA_PIPELINE_RUN`. |
| `_workspace_name` | `string` | No | FabricOps metadata schema registry | `_workspace_name` field in `METADATA_PIPELINE_RUN`. |
| `_notebook_id` | `string` | No | FabricOps metadata schema registry | `_notebook_id` field in `METADATA_PIPELINE_RUN`. |
| `_notebook_name` | `string` | No | FabricOps metadata schema registry | `_notebook_name` field in `METADATA_PIPELINE_RUN`. |
| `_metadata_lakehouse_name` | `string` | No | FabricOps metadata schema registry | `_metadata_lakehouse_name` field in `METADATA_PIPELINE_RUN`. |
| `_activity_id` | `string` | No | FabricOps metadata schema registry | `_activity_id` field in `METADATA_PIPELINE_RUN`. |

[Back to release overview](../index.md)
