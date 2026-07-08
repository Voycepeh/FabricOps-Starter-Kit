# METADATA_DATA_CATALOGUE

**Purpose:** Observed table and column profiles used for catalogue review and runtime comparisons.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `metadata_table_key` | `string` | No | Catalogue evidence writers | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `metadata_column_key` | `string` | No | Catalogue evidence writers | Stable governed data asset key that identifies a column across environment, dataset, table, and column context. |
| `environment_name` | `string` | No | Catalogue evidence writers | Metadata Data Catalogue field `environment_name`. |
| `dataset_name` | `string` | No | Catalogue evidence writers | Metadata Data Catalogue field `dataset_name`. |
| `table_name` | `string` | No | Catalogue evidence writers | Metadata Data Catalogue field `table_name`. |
| `column_name` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `column_name`. |
| `layer` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `layer`. |
| `fabric_store_target` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `fabric_store_target`. |
| `asset_kind` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `asset_kind`. |
| `profile_stage` | `string` | No | Catalogue evidence writers | Metadata Data Catalogue field `profile_stage`. |
| `profile_status` | `string` | No | Catalogue evidence writers | Metadata Data Catalogue field `profile_status`. |
| `profiled_at` | `timestamp` | No | Catalogue evidence writers | Metadata Data Catalogue field `profiled_at`. |
| `evidence_role` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `evidence_role`. |
| `data_type` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `data_type`. |
| `row_count` | `long` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `row_count`. |
| `null_count` | `long` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `null_count`. |
| `null_percent` | `double` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `null_percent`. |
| `distinct_count` | `long` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `distinct_count`. |
| `distinct_percent` | `double` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `distinct_percent`. |
| `min_value` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `min_value`. |
| `max_value` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `max_value`. |
| `distribution_type` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `distribution_type`. |
| `distribution_json` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `distribution_json`. |
| `profile_mode` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `profile_mode`. |
| `watermark_column` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `watermark_column`. |
| `watermark_value` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `watermark_value`. |
| `profile_hash` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `profile_hash`. |
| `profile_payload_json` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `profile_payload_json`. |
| `governance_mode` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `governance_mode`. |
| `approval_policy` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `approval_policy`. |
| `bypass_allowed` | `boolean` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `bypass_allowed`. |
| `policy_reason` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `policy_reason`. |
| `agreement_id` | `string` | Yes | Catalogue evidence writers | Metadata Data Catalogue field `agreement_id`. |
| `agreement_version` | `string` | Yes | Catalogue evidence writers | Canonical agreement version associated with the row. |
| `_committed_by` | `string` | No | Runtime audit context | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | No | Runtime audit context | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | No | Runtime audit context | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | No | Runtime audit context | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | No | Runtime audit context | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | No | Runtime audit context | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | No | Runtime audit context | Fabric execution activity identifier for the current notebook or pipeline run. |

## Related function reference

- [`profile_dataframe`](../../api/reference/profile_dataframe.md)
- [`widget_enrich_table_metadata`](../../api/reference/widget_enrich_table_metadata.md)
