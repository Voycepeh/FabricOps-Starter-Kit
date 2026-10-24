# METADATA_DATA_AGREEMENT

Records who is sharing data, with whom, why it is shared, and the conditions of that sharing.

## Writer functions

* [`widget_render_data_agreement`](../../api/reference/widget_render_data_agreement.md)

## Used in Workflow Template

* [`01_governance`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Agreement intake

## Model

**Authoritative writer:** `governance`

**Default physical schema:** `governance`

**Grain:** One version of a Data Agreement.

**Primary key:** `agreement_id` + `agreement_version`

**Relationships:**

`METADATA_DATA_STEWARD` **(N → 1)**
via `provider_steward_id` + `recipient_steward_id`

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 22 |
| Business columns | 14 |
| Audit columns | 8 |

## Implemented schema

| Column | Data type | Description |
| --- | --- | --- |
| `agreement_id` | `string` | Stable identifier for the agreement lifecycle. |
| `agreement_version` | `string` | Canonical agreement version associated with the row. |
| `agreement_name` | `string` | Human-readable name for the agreement. |
| `domain` | `string` | Business domain recorded for the metadata row. |
| `provider_steward_id` | `string` | Steward identifier recorded for the provider side of the agreement. |
| `provider_steward_name` | `string` | Provider steward name captured when this Data Agreement version was written; later steward renames do not change it. |
| `recipient_steward_id` | `string` | Steward identifier recorded for the recipient side of the agreement. |
| `recipient_steward_name` | `string` | Recipient steward name captured when this Data Agreement version was written; later steward renames do not change it. |
| `start_date` | `date` | Date stored for `start_date`. |
| `expiry_date` | `date` | Date stored for `expiry_date`. |
| `business_purpose` | `string` | Business purpose recorded for the agreement or access request. |
| `supporting_documents_json` | `string` | JSON payload stored for `supporting_documents_json`. |
| `approved_usage_json` | `string` | JSON payload stored for `approved_usage_json`. |
| `custom_fields_json` | `string` | JSON payload stored for `custom_fields_json`. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |
