<!-- Generated file. Edit docs/releases/manifests/0.1.0.yml or the authoritative source metadata and regenerate. -->

# `METADATA_DATA_CATALOGUE`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.1.0`

Source path: `src/fabricops_kit/config/metadata_schemas.py`

Managed by: `fabricops_kit.config.metadata_schemas.metadata_table_schema_registry`

Description: Supported FabricOps metadata table for data catalogue.

## Schema

| Column name | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `metadata_table_key` | `string` | No | FabricOps metadata schema registry | `metadata_table_key` field in `METADATA_DATA_CATALOGUE`. |
| `metadata_column_key` | `string` | No | FabricOps metadata schema registry | `metadata_column_key` field in `METADATA_DATA_CATALOGUE`. |
| `environment_name` | `string` | No | FabricOps metadata schema registry | `environment_name` field in `METADATA_DATA_CATALOGUE`. |
| `dataset_name` | `string` | No | FabricOps metadata schema registry | `dataset_name` field in `METADATA_DATA_CATALOGUE`. |
| `table_name` | `string` | No | FabricOps metadata schema registry | `table_name` field in `METADATA_DATA_CATALOGUE`. |
| `column_name` | `string` | Yes | FabricOps metadata schema registry | `column_name` field in `METADATA_DATA_CATALOGUE`. |
| `layer` | `string` | Yes | FabricOps metadata schema registry | `layer` field in `METADATA_DATA_CATALOGUE`. |
| `fabric_store_target` | `string` | Yes | FabricOps metadata schema registry | `fabric_store_target` field in `METADATA_DATA_CATALOGUE`. |
| `asset_kind` | `string` | Yes | FabricOps metadata schema registry | `asset_kind` field in `METADATA_DATA_CATALOGUE`. |
| `profile_stage` | `string` | No | FabricOps metadata schema registry | `profile_stage` field in `METADATA_DATA_CATALOGUE`. |
| `profile_status` | `string` | No | FabricOps metadata schema registry | `profile_status` field in `METADATA_DATA_CATALOGUE`. |
| `profiled_at` | `timestamp` | No | FabricOps metadata schema registry | `profiled_at` field in `METADATA_DATA_CATALOGUE`. |
| `evidence_role` | `string` | Yes | FabricOps metadata schema registry | `evidence_role` field in `METADATA_DATA_CATALOGUE`. |
| `data_type` | `string` | Yes | FabricOps metadata schema registry | `data_type` field in `METADATA_DATA_CATALOGUE`. |
| `row_count` | `long` | Yes | FabricOps metadata schema registry | `row_count` field in `METADATA_DATA_CATALOGUE`. |
| `null_count` | `long` | Yes | FabricOps metadata schema registry | `null_count` field in `METADATA_DATA_CATALOGUE`. |
| `null_percent` | `double` | Yes | FabricOps metadata schema registry | `null_percent` field in `METADATA_DATA_CATALOGUE`. |
| `distinct_count` | `long` | Yes | FabricOps metadata schema registry | `distinct_count` field in `METADATA_DATA_CATALOGUE`. |
| `distinct_percent` | `double` | Yes | FabricOps metadata schema registry | `distinct_percent` field in `METADATA_DATA_CATALOGUE`. |
| `min_value` | `string` | Yes | FabricOps metadata schema registry | `min_value` field in `METADATA_DATA_CATALOGUE`. |
| `max_value` | `string` | Yes | FabricOps metadata schema registry | `max_value` field in `METADATA_DATA_CATALOGUE`. |
| `distribution_type` | `string` | Yes | FabricOps metadata schema registry | `distribution_type` field in `METADATA_DATA_CATALOGUE`. |
| `distribution_json` | `string` | Yes | FabricOps metadata schema registry | `distribution_json` field in `METADATA_DATA_CATALOGUE`. |
| `profile_mode` | `string` | Yes | FabricOps metadata schema registry | `profile_mode` field in `METADATA_DATA_CATALOGUE`. |
| `watermark_column` | `string` | Yes | FabricOps metadata schema registry | `watermark_column` field in `METADATA_DATA_CATALOGUE`. |
| `watermark_value` | `string` | Yes | FabricOps metadata schema registry | `watermark_value` field in `METADATA_DATA_CATALOGUE`. |
| `profile_hash` | `string` | Yes | FabricOps metadata schema registry | `profile_hash` field in `METADATA_DATA_CATALOGUE`. |
| `profile_payload_json` | `string` | Yes | FabricOps metadata schema registry | `profile_payload_json` field in `METADATA_DATA_CATALOGUE`. |
| `governance_mode` | `string` | Yes | FabricOps metadata schema registry | `governance_mode` field in `METADATA_DATA_CATALOGUE`. |
| `approval_policy` | `string` | Yes | FabricOps metadata schema registry | `approval_policy` field in `METADATA_DATA_CATALOGUE`. |
| `bypass_allowed` | `boolean` | Yes | FabricOps metadata schema registry | `bypass_allowed` field in `METADATA_DATA_CATALOGUE`. |
| `policy_reason` | `string` | Yes | FabricOps metadata schema registry | `policy_reason` field in `METADATA_DATA_CATALOGUE`. |
| `agreement_id` | `string` | Yes | FabricOps metadata schema registry | `agreement_id` field in `METADATA_DATA_CATALOGUE`. |
| `agreement_version` | `string` | Yes | FabricOps metadata schema registry | `agreement_version` field in `METADATA_DATA_CATALOGUE`. |
| `_committed_by` | `string` | No | FabricOps metadata schema registry | `_committed_by` field in `METADATA_DATA_CATALOGUE`. |
| `_committed_at` | `timestamp` | No | FabricOps metadata schema registry | `_committed_at` field in `METADATA_DATA_CATALOGUE`. |
| `_workspace_id` | `string` | No | FabricOps metadata schema registry | `_workspace_id` field in `METADATA_DATA_CATALOGUE`. |
| `_workspace_name` | `string` | No | FabricOps metadata schema registry | `_workspace_name` field in `METADATA_DATA_CATALOGUE`. |
| `_notebook_id` | `string` | No | FabricOps metadata schema registry | `_notebook_id` field in `METADATA_DATA_CATALOGUE`. |
| `_notebook_name` | `string` | No | FabricOps metadata schema registry | `_notebook_name` field in `METADATA_DATA_CATALOGUE`. |
| `_metadata_lakehouse_name` | `string` | No | FabricOps metadata schema registry | `_metadata_lakehouse_name` field in `METADATA_DATA_CATALOGUE`. |
| `_activity_id` | `string` | No | FabricOps metadata schema registry | `_activity_id` field in `METADATA_DATA_CATALOGUE`. |

[Back to 0.1.0 metadata tables](index.md)
