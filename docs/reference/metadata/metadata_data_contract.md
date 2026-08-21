# METADATA_DATA_CONTRACT

Define what the data is, how it looks, its sensitivity, quality requirements, schema, freshness, approved usages, and link it to the Data Agreement.

## Writer functions

* [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md)

## Model

**Grain:** One immutable Data Contract version for one governed table under one exact Data Agreement version.

**Primary key:** `contract_id` + `contract_version`

**Relationships:**

`METADATA_DATA_AGREEMENT` **(N → 1)**
via `agreement_id` + `agreement_version`

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `table_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 16 |
| Business columns | 8 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `contract_id` | `string` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | Stable identifier for the contract row. |
| `contract_version` | `integer` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | Version recorded for the contract row. |
| `agreement_id` | `string` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | Stable identifier for the agreement lifecycle. |
| `agreement_version` | `string` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | Canonical agreement version associated with the row. |
| `table_id` | `string` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | Identifier for the accessed table or object. |
| `contract_payload_json` | `string` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | Serialized contract payload stored for the row. |
| `status` | `string` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | Pipeline run status recorded with the run summary. |
| `is_active` | `boolean` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | Whether the row is currently active. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |
