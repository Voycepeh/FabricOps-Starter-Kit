# METADATA_DATA_CONTRACT

Author and freeze one table-centric schema, processing, Enrichment, and Guardrail snapshot; link an exact Data Agreement version only when activating it for Production.

## Writer functions

* [`widget_activate_data_contract`](../../api/reference/widget_activate_data_contract.md)
* [`widget_author_data_contract`](../../api/reference/widget_author_data_contract.md)

## Used in Workflow Template

* [`01_governance`](../../notebook-templates.md) — Contract activation
* [`01_governance`](../../notebook-templates.md) — Data Contract authoring

## Model

**Authoritative writer:** `governance`

**Default physical schema:** `governance`

**Grain:** One Data Contract lifecycle version for one governed table; its payload becomes immutable when frozen and its Data Agreement linkage is populated at activation.

**Primary key:** `contract_id` + `contract_version`

**Relationships:**

`METADATA_DATA_AGREEMENT` **(N → 1)**
via `agreement_id` + `agreement_version`

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `table_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 17 |
| Business columns | 9 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `contract_id` | `string` | Stable identifier for the contract row. |
| `contract_version` | `integer` | Version recorded for the contract row. |
| `agreement_id` | `string` | Stable identifier for the agreement lifecycle. |
| `agreement_version` | `string` | Canonical agreement version associated with the row. |
| `table_id` | `string` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
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
