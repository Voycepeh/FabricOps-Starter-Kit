# METADATA_DATA_CONTRACT

Defines one global immutable table contract history. Workspace observations supply authoring evidence; workspace activation selects exact frozen versions.

## Writer functions

* [`widget_data_contract`](../../api/reference/widget_data_contract.md)

## Used in Workflow Template

* [`01_governance`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Data Contract authoring

## Model

**Authoritative writer:** `governance`

**Default physical schema:** `governance`

**Grain:** One Draft or Frozen version of a Data Contract for a table.

**Primary key:** `contract_id` + `contract_version`

**Relationships:**

`METADATA_PIPELINE_RUN` **(N → M)**
via Not defined in the current implementation.

`METADATA_DATA_CATALOGUE` **(N → M)**
via `table_id`

**Implementation details:** Reusable immutable frozen table definition with Enrichment, executable Guardrails and independent profiling policies. table_id is a global logical reference across workspace observations, not a unique physical Catalogue foreign key. Agreement linkage belongs to Activated Pipeline.

## Column summary

<div class="metadata-column-kpis" aria-label="Column counts by responsibility">
<div class="metadata-column-kpi metadata-column-kpi--total"><span class="metadata-column-kpi__label">Total columns</span><strong class="metadata-column-kpi__value">15</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--engineering"><span class="metadata-column-kpi__label">Engineering columns</span><strong class="metadata-column-kpi__value">0</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--governance"><span class="metadata-column-kpi__label">Governance columns</span><strong class="metadata-column-kpi__value">7</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--audit"><span class="metadata-column-kpi__label">Standard audit columns</span><strong class="metadata-column-kpi__value">8</strong></div>
</div>

## Implemented schema

Blue rows are Engineering columns; purple rows are Governance columns. Neutral rows are standard audit columns.

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr class="metadata-column--governance"><td><code>contract_id</code></td><td><code>string</code></td><td>Stable identifier for the contract row.</td></tr>
<tr class="metadata-column--governance"><td><code>contract_version</code></td><td><code>integer</code></td><td>Version recorded for the contract row.</td></tr>
<tr class="metadata-column--governance"><td><code>table_id</code></td><td><code>string</code></td><td>Stable governed data asset key that identifies a table across workspace, dataset, and table context.</td></tr>
<tr class="metadata-column--governance"><td><code>table_name</code></td><td><code>string</code></td><td>Table name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it.</td></tr>
<tr class="metadata-column--governance"><td><code>evidence_workspace_id</code></td><td><code>string</code></td><td>Workspace observation used to author this global Contract version; never part of Contract identity.</td></tr>
<tr class="metadata-column--governance"><td><code>contract_payload_json</code></td><td><code>string</code></td><td>String column containing the JSON definition for this exact table/contract version and authoring workspace, including Enrichment, Guardrails, and Processing; editable while draft and immutable once frozen. This is not a separate physical table.</td></tr>
<tr class="metadata-column--governance"><td><code>status</code></td><td><code>string</code></td><td>Pipeline run status recorded with the run summary.</td></tr>
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
