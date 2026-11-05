<!-- Generated file. Edit docs/releases/manifests/0.4.0.yml or the authoritative source metadata and regenerate. -->

# `METADATA_PIPELINE_ACTIVATION`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.4.0`

Live since: `0.4.0`

Schema since: `0.4.0`

Schema fingerprint: `47d975c6979f98602302a518aac587e2e8c6ba6672efce22e9f2524da9ecfeda`

Source path: `src/fabricops_kit/config/metadata_schemas.py`

Frozen source ref: `v0.4.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.4.0/src/fabricops_kit/config/metadata_schemas.py)

Managed by: `fabricops_kit.config.metadata_schemas.metadata_table_schema_registry`

Description: Stores immutable accepted pipeline submission packages and conditional Governance decision history.

## Schema

| Column name | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `approval_id` | `string` | No | FabricOps metadata schema registry | `approval_id` field in `METADATA_PIPELINE_ACTIVATION`. |
| `submission_id` | `string` | No | FabricOps metadata schema registry | `submission_id` field in `METADATA_PIPELINE_ACTIVATION`. |
| `submission_sha256` | `string` | No | FabricOps metadata schema registry | `submission_sha256` field in `METADATA_PIPELINE_ACTIVATION`. |
| `execution_workspace_id` | `string` | No | FabricOps metadata schema registry | `execution_workspace_id` field in `METADATA_PIPELINE_ACTIVATION`. |
| `pipeline_id` | `string` | No | FabricOps metadata schema registry | `pipeline_id` field in `METADATA_PIPELINE_ACTIVATION`. |
| `revision` | `integer` | No | FabricOps metadata schema registry | `revision` field in `METADATA_PIPELINE_ACTIVATION`. |
| `status` | `string` | No | FabricOps metadata schema registry | `status` field in `METADATA_PIPELINE_ACTIVATION`. |
| `decision_kind` | `string` | No | FabricOps metadata schema registry | `decision_kind` field in `METADATA_PIPELINE_ACTIVATION`. |
| `package_json` | `string` | No | FabricOps metadata schema registry | `package_json` field in `METADATA_PIPELINE_ACTIVATION`. |
| `policy_json` | `string` | No | FabricOps metadata schema registry | `policy_json` field in `METADATA_PIPELINE_ACTIVATION`. |
| `expected_active_version` | `integer` | Yes | FabricOps metadata schema registry | `expected_active_version` field in `METADATA_PIPELINE_ACTIVATION`. |
| `restores_promotion_id` | `string` | Yes | FabricOps metadata schema registry | `restores_promotion_id` field in `METADATA_PIPELINE_ACTIVATION`. |
| `expires_at` | `timestamp` | Yes | FabricOps metadata schema registry | `expires_at` field in `METADATA_PIPELINE_ACTIVATION`. |
| `decided_at` | `timestamp` | No | FabricOps metadata schema registry | `decided_at` field in `METADATA_PIPELINE_ACTIVATION`. |
| `review_note` | `string` | No | FabricOps metadata schema registry | `review_note` field in `METADATA_PIPELINE_ACTIVATION`. |
| `_committed_by` | `string` | No | FabricOps metadata schema registry | `_committed_by` field in `METADATA_PIPELINE_ACTIVATION`. |
| `_committed_at` | `timestamp` | No | FabricOps metadata schema registry | `_committed_at` field in `METADATA_PIPELINE_ACTIVATION`. |
| `_workspace_id` | `string` | No | FabricOps metadata schema registry | `_workspace_id` field in `METADATA_PIPELINE_ACTIVATION`. |
| `_workspace_name` | `string` | No | FabricOps metadata schema registry | `_workspace_name` field in `METADATA_PIPELINE_ACTIVATION`. |
| `_notebook_id` | `string` | No | FabricOps metadata schema registry | `_notebook_id` field in `METADATA_PIPELINE_ACTIVATION`. |
| `_notebook_name` | `string` | No | FabricOps metadata schema registry | `_notebook_name` field in `METADATA_PIPELINE_ACTIVATION`. |
| `_metadata_lakehouse_name` | `string` | No | FabricOps metadata schema registry | `_metadata_lakehouse_name` field in `METADATA_PIPELINE_ACTIVATION`. |
| `_activity_id` | `string` | No | FabricOps metadata schema registry | `_activity_id` field in `METADATA_PIPELINE_ACTIVATION`. |

[Back to release overview](../index.md)
