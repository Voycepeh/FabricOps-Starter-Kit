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
| Engineering columns | 0 |
| Governance columns | 14 |
| Standard audit columns | 8 |

## Implemented schema

Blue rows are Engineering columns; purple rows are Governance columns. Neutral rows are standard audit columns.

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr class="metadata-column--governance"><td><code>agreement_id</code></td><td><code>string</code></td><td>Stable identifier for the agreement lifecycle.</td></tr>
<tr class="metadata-column--governance"><td><code>agreement_version</code></td><td><code>string</code></td><td>Canonical agreement version associated with the row.</td></tr>
<tr class="metadata-column--governance"><td><code>agreement_name</code></td><td><code>string</code></td><td>Human-readable name for the agreement.</td></tr>
<tr class="metadata-column--governance"><td><code>domain</code></td><td><code>string</code></td><td>Business domain recorded for the metadata row.</td></tr>
<tr class="metadata-column--governance"><td><code>provider_steward_id</code></td><td><code>string</code></td><td>Steward identifier recorded for the provider side of the agreement.</td></tr>
<tr class="metadata-column--governance"><td><code>provider_steward_name</code></td><td><code>string</code></td><td>Provider steward name captured when this Data Agreement version was written; later steward renames do not change it.</td></tr>
<tr class="metadata-column--governance"><td><code>recipient_steward_id</code></td><td><code>string</code></td><td>Steward identifier recorded for the recipient side of the agreement.</td></tr>
<tr class="metadata-column--governance"><td><code>recipient_steward_name</code></td><td><code>string</code></td><td>Recipient steward name captured when this Data Agreement version was written; later steward renames do not change it.</td></tr>
<tr class="metadata-column--governance"><td><code>start_date</code></td><td><code>date</code></td><td>Date stored for <code>start_date</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>expiry_date</code></td><td><code>date</code></td><td>Date stored for <code>expiry_date</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>business_purpose</code></td><td><code>string</code></td><td>Business purpose recorded for the agreement or access request.</td></tr>
<tr class="metadata-column--governance"><td><code>supporting_documents_json</code></td><td><code>string</code></td><td>JSON payload stored for <code>supporting_documents_json</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>approved_usage_json</code></td><td><code>string</code></td><td>JSON payload stored for <code>approved_usage_json</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>custom_fields_json</code></td><td><code>string</code></td><td>JSON payload stored for <code>custom_fields_json</code>.</td></tr>
<tr class="metadata-column--audit"><td><code>_committed_by</code></td><td><code>string</code></td><td>User principal or runtime identity that committed the metadata row.</td></tr>
<tr class="metadata-column--audit"><td><code>_committed_at</code></td><td><code>timestamp</code></td><td>Timestamp when the metadata row was committed.</td></tr>
<tr class="metadata-column--audit"><td><code>_workspace_id</code></td><td><code>string</code></td><td>Fabric workspace identifier captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_workspace_name</code></td><td><code>string</code></td><td>Fabric workspace name captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_notebook_id</code></td><td><code>string</code></td><td>Fabric notebook identifier captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_notebook_name</code></td><td><code>string</code></td><td>Fabric notebook name captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_metadata_lakehouse_name</code></td><td><code>string</code></td><td>Configured metadata lakehouse name used for the write.</td></tr>
<tr class="metadata-column--audit"><td><code>_activity_id</code></td><td><code>string</code></td><td>Fabric execution activity identifier for the current notebook or pipeline run.</td></tr>
</tbody></table>
</div>
