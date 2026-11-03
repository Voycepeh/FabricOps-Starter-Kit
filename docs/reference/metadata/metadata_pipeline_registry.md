# METADATA_PIPELINE_REGISTRY

Retains immutable per-workspace Pipeline Promotion versions and the active Governed notebook identity.

## Writer functions

* [`promote_pipeline`](../../api/reference/promote_pipeline.md)
* [`widget_activate_pipeline`](../../api/reference/widget_activate_pipeline.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One immutable version per execution workspace/Pipeline ID/version; at most one active version per workspace/Pipeline ID.

**Primary key:** `execution_workspace_id` + `pipeline_id` + `pipeline_version`

**Relationships:**

`METADATA_DATA_AGREEMENT` **(N → 1)**
via `agreement_id` + `agreement_version`

**Implementation details:** Serializable whole-table conditional replacement rejects stale approvals and phantom inserts. Superseded versions remain. Complete ipynb snapshots are write-once Metadata Lakehouse Files; Registry stores exact URIs and full/executable hashes. Logical stores resolve through destination configuration. No Contract Activation rows, Git/deployment attestation, control rows or per-run leases belong in Registry. Imported dependencies are not frozen. Saved-definition checks have TOCTOU limits; Governed admission remains blocked pending signed-in Fabric validation.

## Column summary

<div class="metadata-column-kpis" aria-label="Column counts by responsibility">
<div class="metadata-column-kpi metadata-column-kpi--total"><span class="metadata-column-kpi__label">Total columns</span><strong class="metadata-column-kpi__value">30</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--engineering"><span class="metadata-column-kpi__label">Engineering columns</span><strong class="metadata-column-kpi__value">22</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--governance"><span class="metadata-column-kpi__label">Governance columns</span><strong class="metadata-column-kpi__value">0</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--audit"><span class="metadata-column-kpi__label">Standard audit columns</span><strong class="metadata-column-kpi__value">8</strong></div>
</div>

## Implemented schema

Blue rows are Engineering columns; purple rows are Governance columns. Neutral rows are standard audit columns.

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr class="metadata-column--engineering"><td><code>execution_workspace_id</code></td><td><code>string</code></td><td>Destination workspace whose configuration resolves the approved logical stores.</td></tr>
<tr class="metadata-column--engineering"><td><code>pipeline_id</code></td><td><code>string</code></td><td>Stable logical Pipeline ID shared across versions and workspaces.</td></tr>
<tr class="metadata-column--engineering"><td><code>pipeline_version</code></td><td><code>integer</code></td><td>Monotonically increasing immutable implementation version within an execution workspace.</td></tr>
<tr class="metadata-column--engineering"><td><code>promotion_id</code></td><td><code>string</code></td><td>Unique reviewed promotion operation ID, retained for safe replay.</td></tr>
<tr class="metadata-column--engineering"><td><code>status</code></td><td><code>string</code></td><td>active, superseded or retired; at most one active version per execution workspace/Pipeline ID.</td></tr>
<tr class="metadata-column--engineering"><td><code>source_workspace_id</code></td><td><code>string</code></td><td>Workspace containing the manually tested development notebook.</td></tr>
<tr class="metadata-column--engineering"><td><code>source_notebook_id</code></td><td><code>string</code></td><td>Development notebook identity; distinct from the Governed copy.</td></tr>
<tr class="metadata-column--engineering"><td><code>governed_notebook_id</code></td><td><code>string</code></td><td>Separate physical notebook item for this exact frozen version.</td></tr>
<tr class="metadata-column--engineering"><td><code>snapshot_uri</code></td><td><code>string</code></td><td>Exact write-once full promoted ipynb snapshot in Metadata Lakehouse Files.</td></tr>
<tr class="metadata-column--engineering"><td><code>snapshot_sha256</code></td><td><code>string</code></td><td>SHA256 of complete archived promoted notebook bytes.</td></tr>
<tr class="metadata-column--engineering"><td><code>source_snapshot_uri</code></td><td><code>string</code></td><td>Exact write-once complete saved development notebook snapshot.</td></tr>
<tr class="metadata-column--engineering"><td><code>source_snapshot_sha256</code></td><td><code>string</code></td><td>SHA256 of complete saved development notebook bytes.</td></tr>
<tr class="metadata-column--engineering"><td><code>executable_sha256</code></td><td><code>string</code></td><td>Digest of canonical code cells and behavior metadata; Markdown and execution outputs are excluded.</td></tr>
<tr class="metadata-column--engineering"><td><code>operations_json</code></td><td><code>string</code></td><td>Reviewed source/target operations with exact physical bindings and execution strategies.</td></tr>
<tr class="metadata-column--engineering"><td><code>bindings_sha256</code></td><td><code>string</code></td><td>Canonical digest of exact approved operation bindings and execution descriptors.</td></tr>
<tr class="metadata-column--engineering"><td><code>parameters_json</code></td><td><code>string</code></td><td>Exact approved behavior-affecting setup parameters; runtime overrides reject.</td></tr>
<tr class="metadata-column--engineering"><td><code>agreement_id</code></td><td><code>string</code></td><td>Stable identifier for the agreement lifecycle.</td></tr>
<tr class="metadata-column--engineering"><td><code>agreement_version</code></td><td><code>string</code></td><td>Canonical agreement version associated with the row.</td></tr>
<tr class="metadata-column--engineering"><td><code>agreement_sha256</code></td><td><code>string</code></td><td>Metadata Pipeline Registry field <code>agreement_sha256</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>restored_from_version</code></td><td><code>integer</code></td><td>Prior implementation version when a reviewed rollback promotion declares its lineage.</td></tr>
<tr class="metadata-column--engineering"><td><code>promoted_by</code></td><td><code>string</code></td><td>Actual runtime audit identity responsible for the promotion.</td></tr>
<tr class="metadata-column--engineering"><td><code>promoted_at</code></td><td><code>timestamp</code></td><td>Time the promotion was prepared for atomic activation.</td></tr>
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
