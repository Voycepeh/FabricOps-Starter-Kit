<!-- Generated file. Edit docs/releases/manifests/0.3.1.yml or the authoritative source metadata and regenerate. -->

# `METADATA_GUARDRAIL_RESULTS`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.3.1`

Live since: `0.3.0`

Schema since: `0.3.0`

Schema fingerprint: `9be7b544c43b0b8e05a70902e887e68f043de9fc3dc5b3c110f440c04054652f`

Source path: `src/fabricops_kit/config/metadata_schemas.py`

Frozen source ref: `v0.3.1`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.3.1/src/fabricops_kit/config/metadata_schemas.py)

Managed by: `fabricops_kit.config.metadata_schemas.metadata_table_schema_registry`

Description: Supported FabricOps metadata table for guardrail results.

## Schema

| Column name | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `guardrail_result_id` | `string` | No | FabricOps metadata schema registry | `guardrail_result_id` field in `METADATA_GUARDRAIL_RESULTS`. |
| `guardrail_rule_id` | `string` | No | FabricOps metadata schema registry | `guardrail_rule_id` field in `METADATA_GUARDRAIL_RESULTS`. |
| `guardrail_version` | `integer` | No | FabricOps metadata schema registry | `guardrail_version` field in `METADATA_GUARDRAIL_RESULTS`. |
| `table_id` | `string` | No | FabricOps metadata schema registry | `table_id` field in `METADATA_GUARDRAIL_RESULTS`. |
| `table_name` | `string` | Yes | FabricOps metadata schema registry | `table_name` field in `METADATA_GUARDRAIL_RESULTS`. |
| `contract_id` | `string` | No | FabricOps metadata schema registry | `contract_id` field in `METADATA_GUARDRAIL_RESULTS`. |
| `contract_version` | `integer` | No | FabricOps metadata schema registry | `contract_version` field in `METADATA_GUARDRAIL_RESULTS`. |
| `execution_type` | `string` | No | FabricOps metadata schema registry | `execution_type` field in `METADATA_GUARDRAIL_RESULTS`. |
| `run_id` | `string` | No | FabricOps metadata schema registry | `run_id` field in `METADATA_GUARDRAIL_RESULTS`. |
| `workspace_id` | `string` | No | FabricOps metadata schema registry | `workspace_id` field in `METADATA_GUARDRAIL_RESULTS`. |
| `status` | `string` | No | FabricOps metadata schema registry | `status` field in `METADATA_GUARDRAIL_RESULTS`. |
| `can_continue` | `boolean` | No | FabricOps metadata schema registry | `can_continue` field in `METADATA_GUARDRAIL_RESULTS`. |
| `severity` | `string` | No | FabricOps metadata schema registry | `severity` field in `METADATA_GUARDRAIL_RESULTS`. |
| `guardrail_type` | `string` | Yes | FabricOps metadata schema registry | `guardrail_type` field in `METADATA_GUARDRAIL_RESULTS`. |
| `rule_id` | `string` | Yes | FabricOps metadata schema registry | `rule_id` field in `METADATA_GUARDRAIL_RESULTS`. |
| `rule_type` | `string` | Yes | FabricOps metadata schema registry | `rule_type` field in `METADATA_GUARDRAIL_RESULTS`. |
| `action` | `string` | Yes | FabricOps metadata schema registry | `action` field in `METADATA_GUARDRAIL_RESULTS`. |
| `reason` | `string` | Yes | FabricOps metadata schema registry | `reason` field in `METADATA_GUARDRAIL_RESULTS`. |
| `result_payload_json` | `string` | No | FabricOps metadata schema registry | `result_payload_json` field in `METADATA_GUARDRAIL_RESULTS`. |
| `_committed_by` | `string` | No | FabricOps metadata schema registry | `_committed_by` field in `METADATA_GUARDRAIL_RESULTS`. |
| `_committed_at` | `timestamp` | No | FabricOps metadata schema registry | `_committed_at` field in `METADATA_GUARDRAIL_RESULTS`. |
| `_workspace_id` | `string` | No | FabricOps metadata schema registry | `_workspace_id` field in `METADATA_GUARDRAIL_RESULTS`. |
| `_workspace_name` | `string` | No | FabricOps metadata schema registry | `_workspace_name` field in `METADATA_GUARDRAIL_RESULTS`. |
| `_notebook_id` | `string` | No | FabricOps metadata schema registry | `_notebook_id` field in `METADATA_GUARDRAIL_RESULTS`. |
| `_notebook_name` | `string` | No | FabricOps metadata schema registry | `_notebook_name` field in `METADATA_GUARDRAIL_RESULTS`. |
| `_metadata_lakehouse_name` | `string` | No | FabricOps metadata schema registry | `_metadata_lakehouse_name` field in `METADATA_GUARDRAIL_RESULTS`. |
| `_activity_id` | `string` | No | FabricOps metadata schema registry | `_activity_id` field in `METADATA_GUARDRAIL_RESULTS`. |

[Back to release overview](../index.md)
