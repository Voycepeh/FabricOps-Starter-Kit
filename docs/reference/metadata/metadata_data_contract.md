# METADATA_DATA_CONTRACT

Reusable immutable frozen table definition with Enrichment and executable Guardrails. Agreement linkage belongs to Activated Pipeline.

## Writer functions

* [`widget_data_contract`](../../api/reference/widget_data_contract.md)

## Used in Workflow Template

* [`01_governance`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Data Contract authoring

## Model

**Authoritative writer:** `governance`

**Default physical schema:** `governance`

**Grain:** One Draft or Frozen version of one table contract; Frozen contents are immutable.

**Primary key:** `contract_id` + `contract_version`

**Relationships:**

`METADATA_ACTIVATION_STATE` **(N → M)**
via Not defined in the current implementation.

`METADATA_DATA_CATALOGUE` **(N → 1)**
via `table_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 15 |
| Business columns | 7 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `contract_id` | `string` | Stable identifier for the contract row. |
| `contract_version` | `integer` | Version recorded for the contract row. |
| `table_id` | `string` | Stable governed data asset key that identifies a table across environment, dataset, and table context. |
| `table_name` | `string` | Table name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `contract_payload_json` | `string` | String column containing the JSON definition for this exact table/contract version and authoring environment, including Enrichment, Guardrails, and Processing; editable while draft and immutable once frozen. This is not a separate physical table. |
| `status` | `string` | Pipeline run status recorded with the run summary. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
