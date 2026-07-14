# METADATA_DATA_CONTRACT

**Purpose:** Metadata Data Contract metadata table.

## Implemented schema

| Column | Data type | Nullable | Managed by | Description |
| --- | --- | --- | --- | --- |
| `contract_id` | `string` | No | FabricOps workflow | Metadata Data Contract field `contract_id`. |
| `agreement_id` | `string` | No | FabricOps workflow | Metadata Data Contract field `agreement_id`. |
| `metadata_table_key` | `string` | No | FabricOps workflow | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `schema_fingerprint` | `string` | No | FabricOps workflow | Metadata Data Contract field `schema_fingerprint`. |
| `contract_version` | `string` | Yes | FabricOps workflow | Metadata Data Contract field `contract_version`. |
| `contract_status` | `string` | Yes | FabricOps workflow | Metadata Data Contract field `contract_status`. |
| `effective_from` | `date` | Yes | FabricOps workflow | Metadata Data Contract field `effective_from`. |
| `effective_to` | `date` | Yes | FabricOps workflow | Metadata Data Contract field `effective_to`. |
| `contract_payload_json` | `string` | Yes | FabricOps workflow | Metadata Data Contract field `contract_payload_json`. |
| `_committed_by` | `string` | No | Runtime audit context | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | No | Runtime audit context | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | No | Runtime audit context | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | No | Runtime audit context | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | No | Runtime audit context | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | No | Runtime audit context | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | No | Runtime audit context | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | No | Runtime audit context | Fabric execution activity identifier for the current notebook or pipeline run. |
