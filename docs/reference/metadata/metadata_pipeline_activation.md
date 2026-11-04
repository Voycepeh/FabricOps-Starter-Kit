# METADATA_PIPELINE_ACTIVATION

Retains immutable accepted submission packages and independent Governance decision history.

## Writer functions

* [`widget_activate_pipeline`](../../api/reference/widget_activate_pipeline.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `governance`

**Default physical schema:** `governance`

**Grain:** One append-only import or decision event; revision is monotonic per execution workspace/Pipeline ID.

**Primary key:** `approval_id`

**Relationships:**

No immediate table relationship is defined in the current implementation.

**Implementation details:** Governance imports complete JSON packages under its own identity. Digests establish content identity, not truth of engineer-provided testing claims. Conditional decisions bind the exact snapshot, parameters, physical bindings and independently reviewed policy. Approval never deploys a notebook. Engineering has read-only access; runtime independently verifies this authority. Governance owns all metadata in its workspace, including Engineering records.

## Column summary

<div class="metadata-column-kpis" aria-label="Column counts by responsibility">
<div class="metadata-column-kpi metadata-column-kpi--total"><span class="metadata-column-kpi__label">Total columns</span><strong class="metadata-column-kpi__value">24</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--engineering"><span class="metadata-column-kpi__label">Engineering columns</span><strong class="metadata-column-kpi__value">0</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--governance"><span class="metadata-column-kpi__label">Governance columns</span><strong class="metadata-column-kpi__value">16</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--audit"><span class="metadata-column-kpi__label">Standard audit columns</span><strong class="metadata-column-kpi__value">8</strong></div>
</div>

## Implemented schema

Blue rows are Engineering columns; purple rows are Governance columns. Neutral rows are standard audit columns.

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr class="metadata-column--governance"><td><code>approval_id</code></td><td><code>string</code></td><td>Identifier stored for <code>approval_id</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>submission_id</code></td><td><code>string</code></td><td>Identifier stored for <code>submission_id</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>submission_sha256</code></td><td><code>string</code></td><td>Metadata Pipeline Activation field <code>submission_sha256</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>execution_workspace_id</code></td><td><code>string</code></td><td>Identifier stored for <code>execution_workspace_id</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>pipeline_id</code></td><td><code>string</code></td><td>Identifier stored for <code>pipeline_id</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>revision</code></td><td><code>integer</code></td><td>Metadata Pipeline Activation field <code>revision</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>status</code></td><td><code>string</code></td><td>Pipeline run status recorded with the run summary.</td></tr>
<tr class="metadata-column--governance"><td><code>decision_kind</code></td><td><code>string</code></td><td>Metadata Pipeline Activation field <code>decision_kind</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>package_json</code></td><td><code>string</code></td><td>JSON payload stored for <code>package_json</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>policy_json</code></td><td><code>string</code></td><td>JSON payload stored for <code>policy_json</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>expected_active_version</code></td><td><code>integer</code></td><td>Metadata Pipeline Activation field <code>expected_active_version</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>restores_promotion_id</code></td><td><code>string</code></td><td>Identifier stored for <code>restores_promotion_id</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>expires_at</code></td><td><code>timestamp</code></td><td>Timestamp when access expires.</td></tr>
<tr class="metadata-column--governance"><td><code>decided_by</code></td><td><code>string</code></td><td>Metadata Pipeline Activation field <code>decided_by</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>decided_at</code></td><td><code>timestamp</code></td><td>Timestamp stored for <code>decided_at</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>review_note</code></td><td><code>string</code></td><td>Metadata Pipeline Activation field <code>review_note</code>.</td></tr>
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
