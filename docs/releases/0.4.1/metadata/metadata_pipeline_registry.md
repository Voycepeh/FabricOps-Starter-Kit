<!-- Generated file. Edit docs/releases/manifests/0.4.1.yml or the authoritative source metadata and regenerate. -->

# `METADATA_PIPELINE_REGISTRY`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.4.1`

Live since: `0.3.0`

Schema since: `0.4.0`

Schema fingerprint: `66428aff485a04641fb6845b5f23f9690c0918a5120e67e93c5744f5d4782d2a`

Source path: `src/fabricops_kit/config/metadata_schemas.py`

Frozen source ref: `v0.4.1`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.4.1/src/fabricops_kit/config/metadata_schemas.py)

Managed by: `fabricops_kit.config.metadata_schemas.metadata_table_schema_registry`

Description: Supported FabricOps metadata table for pipeline registry.

## Schema

| Column name | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `execution_workspace_id` | `string` | No | FabricOps metadata schema registry | `execution_workspace_id` field in `METADATA_PIPELINE_REGISTRY`. |
| `pipeline_id` | `string` | No | FabricOps metadata schema registry | `pipeline_id` field in `METADATA_PIPELINE_REGISTRY`. |
| `pipeline_version` | `integer` | No | FabricOps metadata schema registry | `pipeline_version` field in `METADATA_PIPELINE_REGISTRY`. |
| `promotion_id` | `string` | No | FabricOps metadata schema registry | `promotion_id` field in `METADATA_PIPELINE_REGISTRY`. |
| `status` | `string` | No | FabricOps metadata schema registry | `status` field in `METADATA_PIPELINE_REGISTRY`. |
| `source_workspace_id` | `string` | No | FabricOps metadata schema registry | `source_workspace_id` field in `METADATA_PIPELINE_REGISTRY`. |
| `source_notebook_id` | `string` | No | FabricOps metadata schema registry | `source_notebook_id` field in `METADATA_PIPELINE_REGISTRY`. |
| `governed_notebook_id` | `string` | No | FabricOps metadata schema registry | `governed_notebook_id` field in `METADATA_PIPELINE_REGISTRY`. |
| `snapshot_uri` | `string` | No | FabricOps metadata schema registry | `snapshot_uri` field in `METADATA_PIPELINE_REGISTRY`. |
| `snapshot_sha256` | `string` | No | FabricOps metadata schema registry | `snapshot_sha256` field in `METADATA_PIPELINE_REGISTRY`. |
| `source_snapshot_uri` | `string` | No | FabricOps metadata schema registry | `source_snapshot_uri` field in `METADATA_PIPELINE_REGISTRY`. |
| `source_snapshot_sha256` | `string` | No | FabricOps metadata schema registry | `source_snapshot_sha256` field in `METADATA_PIPELINE_REGISTRY`. |
| `executable_sha256` | `string` | No | FabricOps metadata schema registry | `executable_sha256` field in `METADATA_PIPELINE_REGISTRY`. |
| `operations_json` | `string` | No | FabricOps metadata schema registry | `operations_json` field in `METADATA_PIPELINE_REGISTRY`. |
| `bindings_sha256` | `string` | No | FabricOps metadata schema registry | `bindings_sha256` field in `METADATA_PIPELINE_REGISTRY`. |
| `parameters_json` | `string` | No | FabricOps metadata schema registry | `parameters_json` field in `METADATA_PIPELINE_REGISTRY`. |
| `approval_id` | `string` | No | FabricOps metadata schema registry | `approval_id` field in `METADATA_PIPELINE_REGISTRY`. |
| `submission_id` | `string` | No | FabricOps metadata schema registry | `submission_id` field in `METADATA_PIPELINE_REGISTRY`. |
| `submission_sha256` | `string` | No | FabricOps metadata schema registry | `submission_sha256` field in `METADATA_PIPELINE_REGISTRY`. |
| `restored_from_version` | `integer` | Yes | FabricOps metadata schema registry | `restored_from_version` field in `METADATA_PIPELINE_REGISTRY`. |
| `promoted_at` | `timestamp` | No | FabricOps metadata schema registry | `promoted_at` field in `METADATA_PIPELINE_REGISTRY`. |
| `_committed_by` | `string` | No | FabricOps metadata schema registry | `_committed_by` field in `METADATA_PIPELINE_REGISTRY`. |
| `_committed_at` | `timestamp` | No | FabricOps metadata schema registry | `_committed_at` field in `METADATA_PIPELINE_REGISTRY`. |
| `_workspace_id` | `string` | No | FabricOps metadata schema registry | `_workspace_id` field in `METADATA_PIPELINE_REGISTRY`. |
| `_workspace_name` | `string` | No | FabricOps metadata schema registry | `_workspace_name` field in `METADATA_PIPELINE_REGISTRY`. |
| `_notebook_id` | `string` | No | FabricOps metadata schema registry | `_notebook_id` field in `METADATA_PIPELINE_REGISTRY`. |
| `_notebook_name` | `string` | No | FabricOps metadata schema registry | `_notebook_name` field in `METADATA_PIPELINE_REGISTRY`. |
| `_metadata_lakehouse_name` | `string` | No | FabricOps metadata schema registry | `_metadata_lakehouse_name` field in `METADATA_PIPELINE_REGISTRY`. |
| `_activity_id` | `string` | No | FabricOps metadata schema registry | `_activity_id` field in `METADATA_PIPELINE_REGISTRY`. |

[Back to release overview](../index.md)
