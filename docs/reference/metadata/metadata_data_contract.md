# METADATA_DATA_CONTRACT

Establish a governed table version as a draft, then freeze its schema, processing, enrichment, Guardrails, approved usages, and Data Agreement relationship.

## Writer functions

* [`widget_activate_data_contract`](../../api/reference/widget_activate_data_contract.md)
* [`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md)

## Used in Workflow Template

* [`01_governance`](../../notebook-templates.md) — Contract activation
* [`01_governance`](../../notebook-templates.md) — Contract registration

## Model

**Authoritative writer:** `governance`

**Default physical schema:** `governance`

**Grain:** One Data Contract lifecycle version for one governed table under one exact Data Agreement version; its payload becomes immutable when frozen.

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

| Column | Data type | Description |
| --- | --- | --- |
| `contract_id` | `string` | Stable identifier for the contract row. |
| `contract_version` | `integer` | Version recorded for the contract row. |
| `agreement_id` | `string` | Stable identifier for the agreement lifecycle. |
| `agreement_version` | `string` | Canonical agreement version associated with the row. |
| `table_id` | `string` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `contract_payload_json` | `string` | Serialized contract payload stored for the row. |
| `status` | `string` | Pipeline run status recorded with the run summary. |
| `is_active` | `boolean` | Whether the row is currently active. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
