# METADATA_DATA_CONTRACT

Define what the data is, how it looks, its sensitivity, quality requirements, schema, freshness, approved usages, and link it to the Data Agreement.

## Model

**Grain:** One authorised catalogue table and schema fingerprint governed by one Data Agreement.

**Primary key:** `agreement_id` + `metadata_table_key` + `schema_fingerprint`

**Relationships:**

* `agreement_id` → `METADATA_DATA_AGREEMENT.agreement_id` (**N:1**). Many Data Contract rows can belong to one Data Agreement lifecycle; the current schema does not store agreement_version on the contract row.
* `metadata_table_key` → `METADATA_DATA_CATALOGUE.table_id` (**N:1**). The current Data Contract column retains its pre-Stage-2 name, but its stable hash value identifies the same logical table now exposed by Catalogue as table_id. Data Contract redesign is deferred to Stage 5.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 12 |
| Business columns | 4 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Managed by | Description |
| --- | --- | --- | --- |
| `agreement_id` | `string` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | Stable identifier for the agreement lifecycle. |
| `metadata_table_key` | `string` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `schema_fingerprint` | `string` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | Deterministic fingerprint for the observed or governed schema snapshot. |
| `approved_usage_json` | `string` | [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md) | JSON payload stored for `approved_usage_json`. |
| `_committed_by` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | `fabricops_kit.config.audit.build_runtime_audit_fields` | Fabric execution activity identifier for the current notebook or pipeline run. |
