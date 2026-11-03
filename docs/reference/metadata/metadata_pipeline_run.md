# METADATA_PIPELINE_RUN

Records Test and Live operation participation, exact table contracts and execution outcomes.

## Writer functions

* [`finalize_pipeline`](../../api/reference/finalize_pipeline.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One row per execution with JSON-encoded observed operation/stage status, timing, finalization, profiling and safe failures.

**Primary key:** `run_id`

**Relationships:**

`METADATA_PIPELINE_REGISTRY` **(N → 1)**
via `approval_id`

`METADATA_DATA_CONTRACT` **(N → M)**
via `operations`

**Nested references (application-enforced):**

| Local field | Referenced field | Meaning |
| --- | --- | --- |
| `approval_id` | `METADATA_PIPELINE_REGISTRY.approvals[].approval_id` | Live runs reference one nested immutable approval, not authority_id. Test runs have no approval. Pipeline and workspace must match the approval. |
| `operations[].contract_id` | `METADATA_DATA_CONTRACT.contract_id` | Each contracted operation references one exact Contract using contract_id plus contract_version and verifies the payload hash. Test operations may be uncontracted; activation requires all contracts. |
| `operations[].contract_version` | `METADATA_DATA_CONTRACT.contract_version` | Composite reference with operations[].contract_id; neither field is independently unique. |

**Implementation details:** Whole-row CAS atomically publishes the parent and all operations/stages. Validated JSON operations retain table_id, source/target role, exact contract version/hash, destination, read/write mode, SQL hash and source associations. Live pins approval_id and compares these fields before operations. Profiling completion joins physical result snapshots. warnings_json contains variable sanitized diagnostics only. No project settings, full argument snapshots or configuration fingerprints are stored.

## Column summary

<div class="metadata-column-kpis" aria-label="Column counts by responsibility">
<div class="metadata-column-kpi metadata-column-kpi--total"><span class="metadata-column-kpi__label">Total columns</span><strong class="metadata-column-kpi__value">22</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--engineering"><span class="metadata-column-kpi__label">Engineering columns</span><strong class="metadata-column-kpi__value">14</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--governance"><span class="metadata-column-kpi__label">Governance columns</span><strong class="metadata-column-kpi__value">0</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--audit"><span class="metadata-column-kpi__label">Standard audit columns</span><strong class="metadata-column-kpi__value">8</strong></div>
</div>

## Implemented schema

Blue rows are Engineering columns; purple rows are Governance columns. Neutral rows are standard audit columns.

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr class="metadata-column--engineering"><td><code>run_id</code></td><td><code>string</code></td><td>Unique execution attempt and physical merge key; one authoritative row contains every Read/Write.</td></tr>
<tr class="metadata-column--engineering"><td><code>approval_id</code></td><td><code>string</code></td><td>Exact Governance decision retained in the Registry authority; Live runs pin this decision.</td></tr>
<tr class="metadata-column--engineering"><td><code>pipeline_id</code></td><td><code>string</code></td><td>Identifier stored for <code>pipeline_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>execution_mode</code></td><td><code>string</code></td><td>Metadata Pipeline Run field <code>execution_mode</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>workspace_id</code></td><td><code>string</code></td><td>Stable Fabric workspace ID defining the physical observation or runtime authority scope; independent of audit writer workspace.</td></tr>
<tr class="metadata-column--engineering"><td><code>started_at</code></td><td><code>timestamp</code></td><td>Pipeline bootstrap timestamp captured when the pipeline context is initialized.</td></tr>
<tr class="metadata-column--engineering"><td><code>completed_at</code></td><td><code>timestamp</code></td><td>Timestamp captured when the pipeline run summary is written. Pipeline duration is derived from the difference between <code>started_at</code> and <code>completed_at</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>status</code></td><td><code>string</code></td><td>Whole-run outcome: incomplete, failed, succeeded or ungoverned_completed; operation success alone never completes a run.</td></tr>
<tr class="metadata-column--engineering"><td><code>activation_revision</code></td><td><code>string</code></td><td>Metadata Pipeline Run field <code>activation_revision</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>boundary_completed</code></td><td><code>boolean</code></td><td>Whether the explicit whole-run completion boundary finished; independent of operation success.</td></tr>
<tr class="metadata-column--engineering"><td><code>operations</code></td><td><code>string</code></td><td>Native Read/Write operation facts: table ID, role, exact contract version/hash, destination, modes, source associations, status, timing and stages. Query directly with explode(operations); no configuration join is required.</td></tr>
<tr class="metadata-column--engineering"><td><code>profiling</code></td><td><code>string</code></td><td>Typed per-table activity outcomes and physical result snapshot completion markers.</td></tr>
<tr class="metadata-column--engineering"><td><code>warnings_json</code></td><td><code>string</code></td><td>Variable sanitized diagnostics; no configuration snapshots or activation authority.</td></tr>
<tr class="metadata-column--engineering"><td><code>failures</code></td><td><code>string</code></td><td>Native safe failure codes and exception class names; never raw exception messages.</td></tr>
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
