# METADATA_DATA_CONTRACT

**Purpose:** Machine-readable dataset-level delivery promises governed by Data Agreements, including authorised catalogue tables and schema fingerprints.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 11 |
| Business columns | 3 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `agreement_id` | `string` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | Stable identifier for the agreement lifecycle. |
| `metadata_table_key` | `string` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `schema_fingerprint` | `string` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | Deterministic fingerprint for the observed or governed schema snapshot. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |
