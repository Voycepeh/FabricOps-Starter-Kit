# METADATA_DATA_CONTRACT_SNAPSHOT

**Purpose:** Immutable agreement inventory snapshot headers, including intentional empty inventories.

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `contract_snapshot_id` | `string` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | Identifier stored for `contract_snapshot_id`. |
| `agreement_id` | `string` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | Stable identifier for the agreement lifecycle. |
| `snapshot_saved_at` | `timestamp` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | Timestamp stored for `snapshot_saved_at`. |
| `linked_dataset_count` | `long` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | Metadata Data Contract Snapshot field `linked_dataset_count`. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |
