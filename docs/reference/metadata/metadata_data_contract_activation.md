# METADATA_DATA_CONTRACT_ACTIVATION

Selects one exact globally frozen Contract for each physical table or file source.

## Writer functions

* [`widget_activate_data_contract`](../../api/reference/widget_activate_data_contract.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `governance`

**Default physical schema:** `governance`

**Grain:** One retained activation revision per workspace and Table ID or file source_id; one current active selection.

**Primary key:** `activation_id`

**Relationships:**

`METADATA_DATA_AGREEMENT` **(N → 1)**
via `agreement_id` + `agreement_version`

`METADATA_DATA_CONTRACT` **(N → 1)**
via `contract_id` + `contract_version`

**Implementation details:** Governance-owned activation is independent of Pipeline Promotion. activation_id is a replay-safe operation ID. destination_json is the exact reviewed physical table binding or file selector, format and reader configuration. Files have source_id and no Table ID. No extra metadata table is required. Protected aliases reject Ungoverned writes. Actual tenant storage permissions authorize writes; UI confirmation is not authentication.

## Column summary

<div class="metadata-column-kpis" aria-label="Column counts by responsibility">
<div class="metadata-column-kpi metadata-column-kpi--total"><span class="metadata-column-kpi__label">Total columns</span><strong class="metadata-column-kpi__value">22</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--engineering"><span class="metadata-column-kpi__label">Engineering columns</span><strong class="metadata-column-kpi__value">0</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--governance"><span class="metadata-column-kpi__label">Governance columns</span><strong class="metadata-column-kpi__value">14</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--audit"><span class="metadata-column-kpi__label">Standard audit columns</span><strong class="metadata-column-kpi__value">8</strong></div>
</div>

## Implemented schema

Blue rows are Engineering columns; purple rows are Governance columns. Neutral rows are standard audit columns.

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr class="metadata-column--governance"><td><code>workspace_id</code></td><td><code>string</code></td><td>Stable Fabric workspace ID defining the physical observation or runtime authority scope; independent of audit writer workspace.</td></tr>
<tr class="metadata-column--governance"><td><code>table_id</code></td><td><code>string</code></td><td>Stable governed data asset key that identifies a table across workspace, dataset, and table context.</td></tr>
<tr class="metadata-column--governance"><td><code>source_id</code></td><td><code>string</code></td><td>Identifier stored for <code>source_id</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>contract_id</code></td><td><code>string</code></td><td>Stable identifier for the contract row.</td></tr>
<tr class="metadata-column--governance"><td><code>contract_version</code></td><td><code>integer</code></td><td>Version recorded for the contract row.</td></tr>
<tr class="metadata-column--governance"><td><code>payload_sha256</code></td><td><code>string</code></td><td>Metadata Data Contract Activation field <code>payload_sha256</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>activation_id</code></td><td><code>string</code></td><td>Identifier stored for <code>activation_id</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>revision</code></td><td><code>integer</code></td><td>Metadata Data Contract Activation field <code>revision</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>status</code></td><td><code>string</code></td><td>Pipeline run status recorded with the run summary.</td></tr>
<tr class="metadata-column--governance"><td><code>destination_json</code></td><td><code>string</code></td><td>Validated JSON STRING containing the reviewed physical workspace_id, item_id, kind, schema and table_name for a table Contract activation. Alias protection uses this frozen binding independently of caller workspace mappings.</td></tr>
<tr class="metadata-column--governance"><td><code>activated_at</code></td><td><code>timestamp</code></td><td>Timestamp captured when a rule or enrichment record becomes active.</td></tr>
<tr class="metadata-column--governance"><td><code>agreement_id</code></td><td><code>string</code></td><td>Stable identifier for the agreement lifecycle.</td></tr>
<tr class="metadata-column--governance"><td><code>agreement_version</code></td><td><code>string</code></td><td>Canonical agreement version associated with the row.</td></tr>
<tr class="metadata-column--governance"><td><code>agreement_sha256</code></td><td><code>string</code></td><td>Metadata Data Contract Activation field <code>agreement_sha256</code>.</td></tr>
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
