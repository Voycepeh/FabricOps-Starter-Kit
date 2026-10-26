# METADATA_PIPELINE_RUN

Records Test and Live operation participation, exact table contracts and execution outcomes.

## Writer functions

* [`finalize_pipeline`](../../api/reference/finalize_pipeline.md)

## Used in Workflow Template

No starter template or solution is traced for the public writer functions.

## Model

**Authoritative writer:** `engineering`

**Default physical schema:** `engineering`

**Grain:** One row per execution with native observed operation/stage status, timing, finalization, profiling and safe failures.

**Primary key:** `run_id`

**Relationships:**

`METADATA_PIPELINE_REGISTRY` **(N → 1)**
via `approval_id`

`METADATA_DATA_CONTRACT` **(N → M)**
via `operations`

**Nested references (application-enforced):**

| Local field | Referenced field | Meaning |
| --- | --- | --- |
| `approval_id` | `METADATA_PIPELINE_REGISTRY.approvals[].approval_id` | Live runs reference one nested immutable approval, not authority_id. Test runs have no approval. Pipeline and environment must match the approval. |
| `operations[].contract_id` | `METADATA_DATA_CONTRACT.contract_id` | Each contracted operation references one exact Contract using contract_id plus contract_version and verifies the payload hash. Test operations may be uncontracted; activation requires all contracts. |
| `operations[].contract_version` | `METADATA_DATA_CONTRACT.contract_version` | Composite reference with operations[].contract_id; neither field is independently unique. |

**Implementation details:** Whole-row CAS atomically publishes the parent and all operations/stages. Native operations retain table_id, source/target role, exact contract version/hash, destination, read/write mode, SQL hash and source associations. Live pins approval_id and compares these fields before operations. Profiling completion joins physical result snapshots. warnings_json contains variable sanitized diagnostics only. No project settings, full argument snapshots or configuration fingerprints are stored.

## Column summary

| Column category | Count |
| --- | ---: |
| Total columns | 22 |
| Business columns | 14 |
| Audit columns | 8 |

## Implemented schema

<div class="metadata-schema-table" markdown="1">

| Column | Data type | Description |
| --- | --- | --- |
| `run_id` | `string` | Unique execution attempt and physical merge key; one authoritative row contains every Read/Write. |
| `approval_id` | `string` | Exact Governance decision retained in the Registry authority; Live runs pin this decision. |
| `pipeline_id` | `string` | Identifier stored for `pipeline_id`. |
| `execution_mode` | `string` | Metadata Pipeline Run field `execution_mode`. |
| `environment_name` | `string` | Environment name recorded for the metadata row. |
| `started_at` | `timestamp` | Pipeline bootstrap timestamp captured when the pipeline context is initialized. |
| `completed_at` | `timestamp` | Timestamp captured when the pipeline run summary is written. Pipeline duration is derived from the difference between `started_at` and `completed_at`. |
| `status` | `string` | Whole-run outcome: incomplete, failed, succeeded or ungoverned_completed; operation success alone never completes a run. |
| `activation_revision` | `string` | Metadata Pipeline Run field `activation_revision`. |
| `boundary_completed` | `boolean` | Whether the explicit whole-run completion boundary finished; independent of operation success. |
| `operations` | <div class="metadata-structured-type"><span class="metadata-structured-type__label">Array of structs</span><table class="metadata-nested-type" aria-label="Fields in operations"><thead><tr><th scope="col">Field</th><th scope="col">Type</th></tr></thead><tbody><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>operation_key</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>table_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>pipeline_role</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>contract_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>contract_version</code></td><td><code>int</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>payload_sha256</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>destination</code></td><td><code>Struct</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>destination.workspace_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>destination.item_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>destination.kind</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>destination.schema</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>destination.table_name</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>read_mode</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>write_mode</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>query_sha256</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>source_table_ids</code></td><td><code>array&lt;string&gt;</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>incremental_target_table_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>status</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>started_at</code></td><td><code>timestamp</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>completed_at</code></td><td><code>timestamp</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>stages</code></td><td><code>Array of structs</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>stages.stage</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>stages.status</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>stages.evaluation_status</code></td><td><code>string</code></td></tr></tbody></table></div> | Native Read/Write operation facts: table ID, role, exact contract version/hash, destination, modes, source associations, status, timing and stages. Query directly with explode(operations); no configuration join is required. |
| `profiling` | <div class="metadata-structured-type"><span class="metadata-structured-type__label">Array of structs</span><table class="metadata-nested-type" aria-label="Fields in profiling"><thead><tr><th scope="col">Field</th><th scope="col">Type</th></tr></thead><tbody><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>context_key</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>activity</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>status</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>results_persisted</code></td><td><code>boolean</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>empty_result</code></td><td><code>boolean</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>profile_snapshot_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>completed_at</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>reason</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>table_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>row_count</code></td><td><code>bigint</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>trigger</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>environment</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>pipeline_run_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>executed_at</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>physical</code></td><td><code>Struct</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>physical.workspace_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>physical.item_id</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>physical.kind</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>physical.schema</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-1"><code>physical.table_name</code></td><td><code>string</code></td></tr></tbody></table></div> | Typed per-table activity outcomes and physical result snapshot completion markers. |
| `warnings_json` | `string` | Variable sanitized diagnostics; no configuration snapshots or activation authority. |
| `failures` | <div class="metadata-structured-type"><span class="metadata-structured-type__label">Array of structs</span><table class="metadata-nested-type" aria-label="Fields in failures"><thead><tr><th scope="col">Field</th><th scope="col">Type</th></tr></thead><tbody><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>code</code></td><td><code>string</code></td></tr><tr><td class="metadata-nested-field metadata-nested-field--depth-0"><code>exception_type</code></td><td><code>string</code></td></tr></tbody></table></div> | Native safe failure codes and exception class names; never raw exception messages. |
| `_committed_by` | `string` | User principal or runtime identity that committed the metadata row. |
| `_committed_at` | `timestamp` | Timestamp when the metadata row was committed. |
| `_workspace_id` | `string` | Fabric workspace identifier captured from runtime audit context. |
| `_workspace_name` | `string` | Fabric workspace name captured from runtime audit context. |
| `_notebook_id` | `string` | Fabric notebook identifier captured from runtime audit context. |
| `_notebook_name` | `string` | Fabric notebook name captured from runtime audit context. |
| `_metadata_lakehouse_name` | `string` | Configured metadata lakehouse name used for the write. |
| `_activity_id` | `string` | Fabric execution activity identifier for the current notebook or pipeline run. |

</div>
