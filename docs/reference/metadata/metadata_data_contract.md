# METADATA_DATA_CONTRACT

Defines one immutable table or file dataset contract history. Workspace observations supply authoring evidence; physical activation selects exact frozen versions.

## Writer functions

* [`widget_data_contract`](../../api/reference/widget_data_contract.md)

## Used in Workflow Template

* [`01_governance`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Data Contract authoring

## Model

**Authoritative writer:** `governance`

**Default physical schema:** `governance`

**Grain:** One Draft or Frozen version of a Data Contract for a table or file-backed dataset.

**Primary key:** `contract_id` + `contract_version`

**Relationships:**

`METADATA_PIPELINE_RUN` **(N → M)**
via Not defined in the current implementation.

`METADATA_DATA_CATALOGUE` **(N → 0..1)**
via `evidence_workspace_id` + `table_id` + `asset_type`

**Implementation details:** Reusable immutable frozen dataset definition with Enrichment and executable Guardrails. evidence_workspace_id records the physical workspace of the Catalogue asset selected at draft creation. The Catalogue supplies asset_workspace_name. Draft creation matches Catalogue asset_workspace_id to evidence_workspace_id and Catalogue table_id and asset_type to the same Contract fields. New drafts require one active Catalogue asset with an observed schema. Frozen versions retain their captured schema and remain usable independently of the current Catalogue row. Contract Activation records where the frozen version applies. Engineering owns processing and profiling through the pipeline. Files retain their stable selector identity in table_id with asset_type FILE. New payloads use format_version 2; frozen historical payload bytes and hashes remain unchanged. Their exact selector, format and reader options are frozen in the payload. Exact Agreement linkage belongs to the physical Contract Activation in Governance metadata.

## Column summary

<div class="metadata-column-kpis" aria-label="Column counts by responsibility">
<div class="metadata-column-kpi metadata-column-kpi--total"><span class="metadata-column-kpi__label">Total columns</span><strong class="metadata-column-kpi__value">16</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--engineering"><span class="metadata-column-kpi__label">Engineering columns</span><strong class="metadata-column-kpi__value">0</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--governance"><span class="metadata-column-kpi__label">Governance columns</span><strong class="metadata-column-kpi__value">8</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--audit"><span class="metadata-column-kpi__label">Standard audit columns</span><strong class="metadata-column-kpi__value">8</strong></div>
</div>

## Implemented schema

Blue rows are Engineering columns; purple rows are Governance columns. Neutral rows are standard audit columns.

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr class="metadata-column--governance"><td><code>contract_id</code></td><td><code>string</code></td><td>Stable identifier for the contract row.</td></tr>
<tr class="metadata-column--governance"><td><code>contract_version</code></td><td><code>integer</code></td><td>Version recorded for the contract row.</td></tr>
<tr class="metadata-column--governance"><td><code>table_id</code></td><td><code>string</code></td><td>Common operational asset key for TABLE or FILE assets across workspace, dataset, and table context.</td></tr>
<tr class="metadata-column--governance"><td><code>asset_type</code></td><td><code>string</code></td><td>Explicit asset discriminator: TABLE or FILE. Historical null values with table_id are TABLE.</td></tr>
<tr class="metadata-column--governance"><td><code>table_name</code></td><td><code>string</code></td><td>Table name captured from the authoritative Catalogue or contract when this metadata row was written; later renames do not change it.</td></tr>
<tr class="metadata-column--governance"><td><code>evidence_workspace_id</code></td><td><code>string</code></td><td>ID of the workspace whose Catalogue observation supplied the authoring evidence for this Contract version. The Contract version is identified by contract_id and contract_version.</td></tr>
<tr class="metadata-column--governance"><td><code>contract_payload_json</code></td><td><code>string</code></td><td>JSON definition for the exact Contract version, including schema, Enrichment, and Guardrails. A draft is editable and a frozen payload is immutable. File Contracts retain the physical file selector in source.</td></tr>
<tr class="metadata-column--governance"><td><code>status</code></td><td><code>string</code></td><td>Pipeline run status recorded with the run summary.</td></tr>
<tr class="metadata-column--audit"><td><code>_committed_by</code></td><td><code>string</code></td><td>User principal or runtime identity that committed the metadata row.</td></tr>
<tr class="metadata-column--audit"><td><code>_committed_at</code></td><td><code>timestamp</code></td><td>Timestamp when the metadata row was committed.</td></tr>
<tr class="metadata-column--audit"><td><code>_workspace_id</code></td><td><code>string</code></td><td>ID of the executing notebook’s Fabric workspace, captured when the metadata row was written.</td></tr>
<tr class="metadata-column--audit"><td><code>_workspace_name</code></td><td><code>string</code></td><td>Display name of the executing notebook’s Fabric workspace, captured when the metadata row was written.</td></tr>
<tr class="metadata-column--audit"><td><code>_notebook_id</code></td><td><code>string</code></td><td>Fabric notebook identifier captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_notebook_name</code></td><td><code>string</code></td><td>Fabric notebook name captured from runtime audit context.</td></tr>
<tr class="metadata-column--audit"><td><code>_metadata_lakehouse_name</code></td><td><code>string</code></td><td>Configured metadata lakehouse name used for the write.</td></tr>
<tr class="metadata-column--audit"><td><code>_activity_id</code></td><td><code>string</code></td><td>Fabric execution activity identifier for the current notebook or pipeline run.</td></tr>
</tbody></table>
</div>

## Automatic column cleanup

`setup_metadata_tables()` removes only the explicitly retired columns below. It preserves canonical rows, all eight audit columns and other extension columns. If a populated value cannot be proved redundant, setup fails for this table with data preserved.

| Retired column | Removal condition |
| --- | --- |
| `source_id` | SQL NULL or equal to `table_id` |

See [`setup_metadata_tables`](../../api/reference/setup_metadata_tables.md) for transaction results and the Delta recovery boundary.
