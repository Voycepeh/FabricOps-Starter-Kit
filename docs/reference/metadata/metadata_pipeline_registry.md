# METADATA_PIPELINE_REGISTRY

Stores workspace pipeline activations and independent workspace/Table ID Contract activations in one transactional Registry.

## Writer functions

* [`activate_data_contract`](../../api/reference/activate_data_contract.md)
* [`finalize_pipeline`](../../api/reference/finalize_pipeline.md)
* [`orchestrate_write`](../../api/reference/orchestrate_write.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One pipeline activation per workspace/Pipeline ID, one Contract activation per workspace/Table ID, plus one control row.

**Primary key:** `record_id`

**Relationships:**

`METADATA_DATA_AGREEMENT` **(N → 1)**
via `agreement_id` + `agreement_version`

`METADATA_DATA_CONTRACT` **(N → 1)**
via `contract_id` + `contract_version`

**Implementation details:** All fields are SQL-compatible scalars. A Serializable whole-table Delta transaction commits all activation and control changes together. operations_json contains the activated read/write descriptors; leases_json holds transient policy leases. Exact frozen Contracts remain in Data Contract. Migrated selections are requires_reactivation candidates, with complete historical evidence retained in the checksummed migration archive. Pipeline activation and Governed publication remain blocked pending trusted deployment verification. Ungoverned cannot publish to protected tables or destination aliases. Tenant metadata writers are trusted; UI confirmation is not authentication.

## Column summary

<div class="metadata-column-kpis" aria-label="Column counts by responsibility">
<div class="metadata-column-kpi metadata-column-kpi--total"><span class="metadata-column-kpi__label">Total columns</span><strong class="metadata-column-kpi__value">40</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--engineering"><span class="metadata-column-kpi__label">Engineering columns</span><strong class="metadata-column-kpi__value">5</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--governance"><span class="metadata-column-kpi__label">Governance columns</span><strong class="metadata-column-kpi__value">27</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--audit"><span class="metadata-column-kpi__label">Standard audit columns</span><strong class="metadata-column-kpi__value">8</strong></div>
</div>

## Implemented schema

Blue rows are Engineering columns; purple rows are Governance columns. Neutral rows are standard audit columns.

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr class="metadata-column--engineering"><td><code>record_id</code></td><td><code>string</code></td><td>Deterministic workspace/record-kind/logical-ID key; the sole control key is central.</td></tr>
<tr class="metadata-column--engineering"><td><code>record_type</code></td><td><code>string</code></td><td>pipeline_activation, table_contract_activation or control. Filter business kinds for reporting.</td></tr>
<tr class="metadata-column--engineering"><td><code>schema_version</code></td><td><code>integer</code></td><td>Explicit Registry layout version 2.</td></tr>
<tr class="metadata-column--governance"><td><code>workspace_id</code></td><td><code>string</code></td><td>Stable Fabric workspace ID defining the physical observation or runtime authority scope; independent of audit writer workspace.</td></tr>
<tr class="metadata-column--governance"><td><code>pipeline_id</code></td><td><code>string</code></td><td>Identifier stored for <code>pipeline_id</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>pipeline_name</code></td><td><code>string</code></td><td>Human-readable name stored for <code>pipeline_name</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>table_id</code></td><td><code>string</code></td><td>Stable governed data asset key that identifies a table across workspace, dataset, and table context.</td></tr>
<tr class="metadata-column--governance"><td><code>activation_id</code></td><td><code>string</code></td><td>Immutable UUID for one activated governance decision; null on migration candidates.</td></tr>
<tr class="metadata-column--governance"><td><code>status</code></td><td><code>string</code></td><td>active or requires_reactivation; candidates grant no execution authority.</td></tr>
<tr class="metadata-column--governance"><td><code>activated_by</code></td><td><code>string</code></td><td>Actor who activated the row.</td></tr>
<tr class="metadata-column--governance"><td><code>notebook_id</code></td><td><code>string</code></td><td>Fabric notebook identifier captured for the lineage row.</td></tr>
<tr class="metadata-column--governance"><td><code>git_repository</code></td><td><code>string</code></td><td>Metadata Pipeline Registry field <code>git_repository</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>git_commit_sha</code></td><td><code>string</code></td><td>Repository-qualified immutable revision provenance; a supplied string alone is not verified evidence.</td></tr>
<tr class="metadata-column--governance"><td><code>deployment_id</code></td><td><code>string</code></td><td>Trusted deployment artifact correlation; null when not applicable.</td></tr>
<tr class="metadata-column--governance"><td><code>deployment_manifest_uri</code></td><td><code>string</code></td><td>Metadata Pipeline Registry field <code>deployment_manifest_uri</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>deployment_manifest_sha256</code></td><td><code>string</code></td><td>Metadata Pipeline Registry field <code>deployment_manifest_sha256</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>verification_method</code></td><td><code>string</code></td><td>Reserved trusted deployment assurance method; caller assertions never enable Governed.</td></tr>
<tr class="metadata-column--governance"><td><code>operations_json</code></td><td><code>string</code></td><td>Validated JSON STRING containing read/write descriptors, physical destinations and source associations, without copied Contract definitions.</td></tr>
<tr class="metadata-column--governance"><td><code>agreement_id</code></td><td><code>string</code></td><td>Stable identifier for the agreement lifecycle.</td></tr>
<tr class="metadata-column--governance"><td><code>agreement_version</code></td><td><code>string</code></td><td>Canonical agreement version associated with the row.</td></tr>
<tr class="metadata-column--governance"><td><code>agreement_sha256</code></td><td><code>string</code></td><td>Metadata Pipeline Registry field <code>agreement_sha256</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>contract_id</code></td><td><code>string</code></td><td>Stable identifier for the contract row.</td></tr>
<tr class="metadata-column--governance"><td><code>payload_sha256</code></td><td><code>string</code></td><td>Metadata Pipeline Registry field <code>payload_sha256</code>.</td></tr>
<tr class="metadata-column--governance"><td><code>destination_json</code></td><td><code>string</code></td><td>Validated JSON STRING containing the reviewed physical workspace_id, item_id, kind, schema and table_name for a table Contract activation. Alias protection uses this frozen binding independently of caller workspace mappings.</td></tr>
<tr class="metadata-column--engineering"><td><code>token</code></td><td><code>string</code></td><td>Control-only shared CAS token; every Registry mutation replaces it under Serializable isolation.</td></tr>
<tr class="metadata-column--engineering"><td><code>leases_json</code></td><td><code>string</code></td><td>Control-only validated JSON array of transient policy leases. Crashed leases require cancellation/reconciliation; they do not expire automatically.</td></tr>
<tr class="metadata-column--governance"><td><code>last_governance_change_id</code></td><td><code>string</code></td><td>Most recent committed governance decision identity; lease churn preserves it.</td></tr>
<tr class="metadata-column--governance"><td><code>last_governance_audit_uri</code></td><td><code>string</code></td><td>Durable before/after governance snapshot referenced by the committed transaction.</td></tr>
<tr class="metadata-column--governance"><td><code>migration_archive_uri</code></td><td><code>string</code></td><td>Immutable pre-cutover audit snapshot URI retaining all six original collections, schema, table identity/version and registration IDs.</td></tr>
<tr class="metadata-column--governance"><td><code>migration_archive_sha256</code></td><td><code>string</code></td><td>SHA256 of the exact durable migration archive bytes.</td></tr>
<tr class="metadata-column--governance"><td><code>activated_at</code></td><td><code>timestamp</code></td><td>Timestamp captured when a rule or enrichment record becomes active.</td></tr>
<tr class="metadata-column--governance"><td><code>contract_version</code></td><td><code>integer</code></td><td>Version recorded for the contract row.</td></tr>
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
