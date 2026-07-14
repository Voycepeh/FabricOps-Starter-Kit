# METADATA_DATA_CONTRACT

**Purpose:** Contract rows reserved for implemented data contract lifecycle evidence.

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `contract_id` | `string` | Implemented schema registry only | Stable identifier for the contract row. |
| `agreement_id` | `string` | Implemented schema registry only | Stable identifier for the agreement lifecycle. |
| `metadata_table_key` | `string` | Implemented schema registry only | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `schema_fingerprint` | `string` | Implemented schema registry only | Deterministic fingerprint for the observed or governed schema snapshot. |
| `contract_version` | `string` | Implemented schema registry only | Version recorded for the contract row. |
| `contract_status` | `string` | Implemented schema registry only | Lifecycle status recorded for the contract row. |
| `effective_from` | `date` | Implemented schema registry only | Date when the record becomes effective. |
| `effective_to` | `date` | Implemented schema registry only | Date when the record stops being effective. |
| `contract_payload_json` | `string` | Implemented schema registry only | Serialized contract payload stored for the row. |
| `_committed_by` | `string` | Implemented schema registry only | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Implemented schema registry only | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Implemented schema registry only | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Implemented schema registry only | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Implemented schema registry only | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Implemented schema registry only | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Implemented schema registry only | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Implemented schema registry only | Fabric execution activity identifier for the current notebook or pipeline run. |
