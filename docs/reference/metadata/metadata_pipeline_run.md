# METADATA_PIPELINE_RUN

Records actual pipeline execution outcomes and exact per-operation Contract versions.

## Writer functions

* [`finalize_pipeline`](../../api/reference/finalize_pipeline.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One authoritative execution with validated JSON operations, profiling, failures and versioned provenance.

**Primary key:** `run_id`

**Relationships:**

`METADATA_PIPELINE_REGISTRY` **(N → 1)**
via `promotion_id`

`METADATA_DATA_CONTRACT` **(N → M)**
via `operations`

**Nested references (application-enforced):**

| Local field | Referenced field | Meaning |
| --- | --- | --- |
| `operations[].contract_id` | `METADATA_DATA_CONTRACT.contract_id` | Composite exact per-operation Contract identity with version and payload SHA. |
| `operations[].contract_version` | `METADATA_DATA_CONTRACT.contract_version` | Exact frozen version used by the operation. |

**Implementation details:** Fresh runs use schema version 3 and pin execution workspace, Pipeline version, promotion ID, Governed notebook and execution identity. Operations retain exact Contract ID/version/payload hash. Run JSON/content hashing and whole-row CAS remain. Historical null provenance is excluded from original hash projections. Explicit development reset discards old Run history and Processing State; normal setup never deletes either.

## Column summary

<div class="metadata-column-kpis" aria-label="Column counts by responsibility">
<div class="metadata-column-kpi metadata-column-kpi--total"><span class="metadata-column-kpi__label">Total columns</span><strong class="metadata-column-kpi__value">28</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--engineering"><span class="metadata-column-kpi__label">Engineering columns</span><strong class="metadata-column-kpi__value">20</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--governance"><span class="metadata-column-kpi__label">Governance columns</span><strong class="metadata-column-kpi__value">0</strong></div>
<div class="metadata-column-kpi metadata-column-kpi--audit"><span class="metadata-column-kpi__label">Standard audit columns</span><strong class="metadata-column-kpi__value">8</strong></div>
</div>

## Implemented schema

Blue rows are Engineering columns; purple rows are Governance columns. Neutral rows are standard audit columns.

<div class="metadata-schema-table">
<table class="metadata-schema-table"><thead><tr><th scope="col">Column</th><th scope="col">Data type</th><th scope="col">Description</th></tr></thead><tbody>
<tr class="metadata-column--engineering"><td><code>run_id</code></td><td><code>string</code></td><td>Unique execution attempt and physical merge key; one authoritative row contains every Read/Write.</td></tr>
<tr class="metadata-column--engineering"><td><code>approval_id</code></td><td><code>string</code></td><td>Nullable historical approval reference retained unchanged for audit; never new activation authority.</td></tr>
<tr class="metadata-column--engineering"><td><code>pipeline_id</code></td><td><code>string</code></td><td>Identifier stored for <code>pipeline_id</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>execution_mode</code></td><td><code>string</code></td><td>Metadata Pipeline Run field <code>execution_mode</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>workspace_id</code></td><td><code>string</code></td><td>Stable Fabric workspace ID defining the physical observation or runtime authority scope; independent of audit writer workspace.</td></tr>
<tr class="metadata-column--engineering"><td><code>started_at</code></td><td><code>timestamp</code></td><td>Pipeline bootstrap timestamp captured when the pipeline context is initialized.</td></tr>
<tr class="metadata-column--engineering"><td><code>completed_at</code></td><td><code>timestamp</code></td><td>Timestamp captured when the pipeline run summary is written. Pipeline duration is derived from the difference between <code>started_at</code> and <code>completed_at</code>.</td></tr>
<tr class="metadata-column--engineering"><td><code>status</code></td><td><code>string</code></td><td>Whole-run outcome: incomplete, failed, succeeded or ungoverned_completed; operation success alone never completes a run.</td></tr>
<tr class="metadata-column--engineering"><td><code>activation_revision</code></td><td><code>string</code></td><td>Nullable historical workspace revision; retained for old Run audit only.</td></tr>
<tr class="metadata-column--engineering"><td><code>boundary_completed</code></td><td><code>boolean</code></td><td>Whether the explicit whole-run completion boundary finished; independent of operation success.</td></tr>
<tr class="metadata-column--engineering"><td><code>execution_workspace_id</code></td><td><code>string</code></td><td>Actual execution workspace captured for this Run.</td></tr>
<tr class="metadata-column--engineering"><td><code>pipeline_version</code></td><td><code>integer</code></td><td>Frozen per-workspace Pipeline version captured at Governed admission.</td></tr>
<tr class="metadata-column--engineering"><td><code>promotion_id</code></td><td><code>string</code></td><td>Exact immutable promotion ID captured at admission; superseded versions remain retained.</td></tr>
<tr class="metadata-column--engineering"><td><code>governed_notebook_id</code></td><td><code>string</code></td><td>Physical Governed notebook item that started this Run.</td></tr>
<tr class="metadata-column--engineering"><td><code>execution_identity</code></td><td><code>string</code></td><td>Actual runtime principal identity captured independently of the promotion author.</td></tr>
<tr class="metadata-column--engineering"><td><code>run_schema_version</code></td><td><code>integer</code></td><td>Version 3 includes notebook Pipeline Promotion provenance. Null retains the original Run hash projection.</td></tr>
<tr class="metadata-column--engineering"><td><code>operations</code></td><td><code>string</code><details class="metadata-structured-type"><summary>Logical JSON schema: <code>Array</code></summary><table class="metadata-nested-type" aria-label="Fields in operations"><thead><tr><th scope="col">Field</th><th scope="col">Type</th></tr></thead><tbody><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>operation_key</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>table_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>pipeline_role</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>contract_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>contract_version</code></td><td><code>int</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>payload_sha256</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>destination</code></td><td><code>Struct</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>destination.workspace_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>destination.item_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>destination.kind</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>destination.schema</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>destination.table_name</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>read_mode</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>write_mode</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>query_sha256</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>source_table_ids</code></td><td><code>array&lt;string&gt;</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>incremental_target_table_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>status</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>started_at</code></td><td><code>timestamp</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>completed_at</code></td><td><code>timestamp</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>stages</code></td><td><code>Array</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>stages.stage</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>stages.status</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>stages.evaluation_status</code></td><td><code>string</code></td></tr></tbody></table><p>Representative JSON value (optional fields omitted):</p><pre><code class="language-json">[
  {
    &quot;operation_key&quot;: &quot;write:orders&quot;,
    &quot;table_id&quot;: &quot;orders&quot;,
    &quot;pipeline_role&quot;: &quot;target&quot;,
    &quot;destination&quot;: {
      &quot;workspace_id&quot;: &quot;example-workspace&quot;,
      &quot;item_id&quot;: &quot;example-lakehouse&quot;,
      &quot;kind&quot;: &quot;lakehouse&quot;,
      &quot;schema&quot;: &quot;demo&quot;,
      &quot;table_name&quot;: &quot;orders&quot;
    },
    &quot;write_mode&quot;: &quot;append&quot;,
    &quot;source_table_ids&quot;: [
      &quot;source-orders&quot;
    ],
    &quot;status&quot;: &quot;succeeded&quot;,
    &quot;stages&quot;: [
      {
        &quot;stage&quot;: &quot;Processing&quot;,
        &quot;status&quot;: &quot;passed&quot;
      }
    ]
  }
]</code></pre></details></td><td>Validated JSON STRING containing Read/Write operation facts: table ID, role, exact contract version/hash, destination, modes, source associations, status, timing and stages; decoded to a logical array in application code. Parse JSON before expanding operations in Spark or Power Query; no configuration join is required.</td></tr>
<tr class="metadata-column--engineering"><td><code>profiling</code></td><td><code>string</code><details class="metadata-structured-type"><summary>Logical JSON schema: <code>Array</code></summary><table class="metadata-nested-type" aria-label="Fields in profiling"><thead><tr><th scope="col">Field</th><th scope="col">Type</th></tr></thead><tbody><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>context_key</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>activity</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>status</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>results_persisted</code></td><td><code>boolean</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>empty_result</code></td><td><code>boolean</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>profile_snapshot_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>completed_at</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>reason</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>table_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>row_count</code></td><td><code>bigint</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>trigger</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>workspace_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>pipeline_run_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>executed_at</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>physical</code></td><td><code>Struct</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>physical.workspace_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>physical.item_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>physical.kind</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>physical.schema</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>physical.table_name</code></td><td><code>string</code></td></tr></tbody></table><p>Representative JSON value (optional fields omitted):</p><pre><code class="language-json">[
  {
    &quot;context_key&quot;: &quot;example-context&quot;,
    &quot;activity&quot;: &quot;standard&quot;,
    &quot;status&quot;: &quot;passed&quot;,
    &quot;results_persisted&quot;: true,
    &quot;profile_snapshot_id&quot;: &quot;example-snapshot&quot;,
    &quot;table_id&quot;: &quot;orders&quot;,
    &quot;row_count&quot;: 100
  }
]</code></pre></details></td><td>Validated JSON STRING containing per-table activity outcomes and physical result snapshot completion markers; decoded to a logical array in application code.</td></tr>
<tr class="metadata-column--engineering"><td><code>warnings_json</code></td><td><code>string</code></td><td>Variable sanitized diagnostics; no configuration snapshots or activation authority.</td></tr>
<tr class="metadata-column--engineering"><td><code>failures</code></td><td><code>string</code><details class="metadata-structured-type"><summary>Logical JSON schema: <code>Array</code></summary><table class="metadata-nested-type" aria-label="Fields in failures"><thead><tr><th scope="col">Field</th><th scope="col">Type</th></tr></thead><tbody><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>code</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>exception_type</code></td><td><code>string</code></td></tr></tbody></table><p>Representative JSON value (optional fields omitted):</p><pre><code class="language-json">[
  {
    &quot;code&quot;: &quot;evidence_persistence_failed&quot;,
    &quot;exception_type&quot;: &quot;RuntimeError&quot;
  }
]</code></pre></details></td><td>Validated JSON STRING containing safe failure codes and exception class names; decoded to a logical array in application code. Never raw exception messages.</td></tr>
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
