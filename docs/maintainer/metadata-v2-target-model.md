# Metadata v2: target model and migration boundaries

**Status (2026-10-25):** Processing State implemented by [#1698](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1698). Typed Pipeline Run records are implemented in open [#1700](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1700), with review outstanding. Activation State physical redesign remains a proposal. Merged [#1697](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1697) persists explicitly finalized Test execution and Guardrail results for activation; D preserves this contract.

## Goal and constraints

Treat FabricOps metadata as an operational application database, not a reporting star schema. Prefer queryable typed records and explicit relationships over large nested state documents, but do not normalize flexible configuration for its own sake.

- Keep **one metadata Lakehouse** and exactly the two existing logical ownership schemas: `governance` and `engineering`. Respect configured physical schema names.
- Retain the six published Live metadata contracts unchanged unless a separate decision demonstrates a substantial long-term benefit.
- Preview contracts may change without deprecated aliases, dual writes, or transitional API wrappers. Operational checkpoints, frozen contracts, and approval history still need a deliberate migration or safe cutover.
- Do not introduce Azure SQL, extra metadata schemas, or a separate control-plane database.
- Do not require the physical table count to decrease. A `record_type` discriminator is appropriate only when row types have compatible identity, lifecycle, and transaction semantics.
- Preserve public notebook workflows: Test operations stay in memory; explicit finalization persists only the allowed Test run and Guardrail diagnostics for activation, as implemented by #1697.

## Release classification versus current canonical registry

The published `docs/releases/manifests/0.2.5.yml` classifies six tables as Live and four as Preview. Three newer canonical tables are absent from that release manifest. **Absence is not permission to discard their persisted state.** Reconcile their lifecycle classification in the appropriate future release manifest rather than rewriting the historical v0.2.5 manifest.

| Canonical table | Owner | Published lifecycle | v2 direction |
| --- | --- | --- | --- |
| `METADATA_DATA_STEWARD` | governance | Live | Keep schema and steward grain |
| `METADATA_DATA_AGREEMENT` | governance | Live | Keep schema and versioned agreement grain |
| `METADATA_DATA_CONTRACT` | governance | Preview | Keep version identity and immutable Frozen contracts; retain flexible rule payload unless independently queryable records are justified |
| `METADATA_ACTIVATION_STATE` | governance | Not listed | Redesign nested authority cautiously; prove atomic publication before removing snapshot state |
| `METADATA_DATA_CATALOGUE` | engineering | Live | Keep existing `metadata_level` table/column discriminator |
| `METADATA_DATA_PROFILED` | engineering | Live | Keep one observed column per profile snapshot |
| `METADATA_DATA_PROFILED_FREQUENCY` | engineering | Live | Keep one frequency value per column snapshot; profile-to-frequency is one-to-many |
| `METADATA_DATA_LINEAGE` | engineering | Live | Keep source/target *participation* grain; do not mislabel as source-to-target edges |
| `METADATA_DATA_ACCESS` | engineering | Preview | Keep observed-grant grain; distinguish observed access from computed effective access |
| `METADATA_PIPELINE_REGISTRY` | engineering | Not listed | Keep stable pipeline/environment notebook binding and its serialization control |
| `METADATA_PIPELINE_RUN` | engineering | Not listed | Typed `run` and `operation` records implemented in open #1700; preserve whole-run authority and exact Test results |
| `METADATA_GUARDRAIL_RESULTS` | engineering | Preview | Keep per-rule aggregate result grain; normalize only useful stable metrics |
| `METADATA_PROCESSING_STATE` | engineering | Preview | Rename Preview METADATA_SOURCE_OBSERVATION to this typed Processing State table |

## Relational design rules

1. **Stable identities:** use `table_id`, `contract_id + contract_version`, `pipeline_id + environment_name`, `run_id`, and immutable approved-version identifiers. Document composite keys where a record has multiple dimensions.
2. **Actual grains:** a catalogue column, a frequency value, a Guardrail result, a pipeline operation, and a publication receipt are different facts. Do not collapse them into one generic JSON blob.
3. **Explicit parent links:** run operations reference `run_id`; approval participants reference the exact approved version and `table_id`; Guardrail results reference run and contract version. Enforce integrity in application code because Delta tables do not provide ordinary relational foreign-key enforcement.
4. **Typed records, not a universal table:** use `record_type` for closely related rows; require type-specific validation and explicit uniqueness rules. Avoid dozens of unrelated nullable fields.
5. **JSON boundary:** retain authored expressions, extensible contract settings, and variable diagnostics in JSON. Extract stable IDs, statuses, timestamps, counters, approval participants, and checkpoints where querying or integrity requires it.
6. **Historical correctness:** a frozen contract, approved pipeline version, or completed run must not be retroactively rewritten by subsequent edits.
7. **Transaction boundaries first:** physical normalization is subordinate to atomic activation and successful-write checkpoint semantics.

## Candidate changes and required invariants

### Processing state (engineering)

`engineering.METADATA_PROCESSING_STATE` replaces Preview `METADATA_SOURCE_OBSERVATION` as the canonical Processing State table. Its four record types separate captured source state from accepted progress and physical publication evidence. The six Live schemas and the existing governance/engineering ownership routing are unchanged.

| Record type | Grain and lifecycle |
| --- | --- |
| `source_observation` | One captured source snapshot partition (or explicit empty-source row), `status=observed`; no target or publication link and never read as accepted progress |
| `incremental_checkpoint` | One source/target/environment observation partition bound to a publication, `staged` → `committed` after verification |
| `drift_baseline` | One source/target/environment observation partition or removal tombstone, `staged` → `committed` after verification and a continuing Guardrail decision |
| `publication_receipt` | One exact target/environment publication attempt, including source-free writes, `staged` → `committed` with all source members |

**Physical fields:** `record_id`, `record_type`, `status` and `environment_name` are required strings. Nullable strings are `observation_id`, `run_id`, `pipeline_id`, `source_table_id`, `source_table_name`, `target_table_id`, `target_table_name`, `partition_column`, `change_column`, `watermark_type`, `partition_value`, `min_change_value`, `max_change_value`, `content_fingerprint`, `publication_id`, `publication_batch_id`, `publication_activity_id`, and `publication_strategy`. `observed_at`, `accepted_at`, and `publication_at` are nullable timestamps; `row_count` and `publication_input_rows` are nullable longs; `is_present` is a nullable boolean. The eight existing required audit fields remain unchanged. The generated [physical reference](../reference/metadata/metadata_processing_state.md) comes from `metadata_schemas.py`.

Bounds use lossless scalar text plus an explicit source type rather than a floating-point conversion that would lose decimal or integer precision. `timestamp` bounds use UTC instants; `timestamp_ntz` retains wall time. Observation column names and watermark type now survive persistence. Publication identities, timestamps and row counts are ordinary columns, with no operational JSON payload. Source content fingerprints remain partition evidence; prepared schema/processing/content are bound into `publication_batch_id`.

`record_id` is a SHA-256 key over explicit, JSON-framed identity components. Captured observations key environment/source/snapshot/partition; accepted members key publication/type/source/snapshot/partition. The publication ID binds environment, target, prepared batch, physical activity and timestamp, permitting repeated SCD content at different publication boundaries. Status is outside the key: acceptance updates the existing staged records and a repeated stage cannot regress committed records. `observation_id` groups source snapshot partitions; `run_id` retains logical-attempt identity while `_activity_id` retains real Fabric activity.

**Reader/writer inventory:** `capture_source_observation` captures and persists observations. `resolve_incremental_source_scope` reads only committed checkpoints; `check_source_drift_for_target` reads only committed baselines and discards blocked candidates. `PublicationBatch` resolves linked receipts and verifies the exact physical target. `stage_pipeline_write_observations` and `commit_pipeline_write_success` use one private record builder and one Delta merge each. `_recover_completed_source_observations` accepts every staged source member and the receipt of a verified target publication in one merge, including cross-run recovery. The public Read/Write orchestrator signatures and return contracts are unchanged.

#### Publication and checkpoint recovery

1. Read captures an observation without advancing a checkpoint. A no-change or empty incremental read leaves accepted progress intact; empty incremental publication is skipped.
2. Write freezes the source observations and prepared batch, then stages one typed receipt and all checkpoint/baseline members in a **single metadata Delta transaction**, before any target mutation.
3. Lakehouse publication writes its exact receipt into Delta commit metadata and stamps activity/time on business rows. Append also uses Delta transaction identity to suppress concurrent identical appends. Warehouse publication stamps the same pair in its physical target operation; SCD mutations retain their existing Warehouse SQL transaction.
4. Verify physical completion before metadata acknowledgement. Lakehouse requires the exact Delta receipt and target markers (the commit alone attests an empty overwrite). Warehouse append/overwrite requires the **full prepared row count** with the exact marker pair; a nonzero partial count blocks retry and progress. Warehouse SCD relies on its atomic SQL mutation and requires the latest publication for retry suppression. An empty Warehouse write has no durable row receipt and fails closed, requiring reconciliation.
5. Commit the typed receipt and all checkpoint/baseline members in **one metadata Delta merge**. Lineage and Catalogue are separate commits; their failure leaves staged Processing State recoverable. No cross-table atomicity is claimed.
6. Exact prepared-batch retries freeze the original persisted publication membership, including every source and drift baseline, even after a process restart loses all pending caches. They acknowledge those original record IDs and run identities together with the receipt. A pre-existing receipt-only acknowledgement is recoverable: the committed receipt remains in the same merge as its staged members. Empty-source drift headers use is_present=null and a separate record identity from is_present=false removal tombstones. SQL-null partition values stay null, distinct from empty strings; headers are excluded from partition comparison. Baselines retain absent-partition tombstones so repeated empty reads and reappearance checks preserve their meaning.
7. If interrupted before publication, staged records are not accepted. If physical publication succeeds but acknowledgement is lost, a subsequent Read or exact prepared-batch retry verifies the staged receipt, accepts its entire member set, and avoids a duplicate append. Older receipts never accept a newer Read snapshot. A failed metadata merge can be retried with the same record IDs.

Warehouse attempts for one target must remain serialized under the existing writer-ownership contract. A partial publication, missing retained Delta commit evidence, missing/ambiguous receipt reference, or unprovable empty Warehouse publication requires operator reconciliation; retry must not guess completion. This PR does not introduce distributed transactions or claim exactly-once publication for independent concurrent Warehouse writers. Source Drift warns/blocks as configured, and observed structural/content changes never become baselines merely because they were captured.

### Processing State upgrade

This Preview layout and table name are a breaking replacement: `METADATA_SOURCE_OBSERVATION` → `METADATA_PROCESSING_STATE`. There is no legacy alias or fallback reader. Setup fails while the old physical table still exists, even if the new table also exists, so an empty new table cannot silently hide old operational progress. `observation_status` and `publication_payload_json` are removed. Old rows must **not** be additive-evolved into typed progress. Setup and runtime reject the old physical layout, including an empty old table. No compatibility reader, automatic migration, reset, or discard is performed.

1. Stop/drain writers and take a durable backup of the existing `METADATA_SOURCE_OBSERVATION` table plus the code/version needed to read it. Retain target data, target audit markers, and Delta history. Inventory all source/target/environment relationships, accepted progress and unresolved publications.
2. Reconcile every staged publication against the physical target before cutover. In the old layout, `committed` corresponds to `incremental_checkpoint`; `drift_committed` to `drift_baseline`; `publication_observed`/`publication_committed` to staged/committed receipts. Old target-bound `observed`/`drift_observed` rows are staged candidates, never automatically accepted checkpoints. Decode and deduplicate exact receipt JSON into typed receipt rows; retain originating run/audit identities. Column/type evidence missing from old records must be supplied from the verified original processing definition, not inferred silently from current configuration.
3. Choose an explicit, reviewed cutover: an offline migration into the complete canonical schema with deterministic IDs and validated receipt references; or a reset only after reconciling/archiving progress and preparing a governed target rebuild or idempotent replay. A populated append target without an accepted baseline is intentionally rejected. Dropping only the metadata table and continuing incremental append is unsafe.
4. For reset, archive the reconciled old Preview table outside its original physical name through the configured Metadata Lakehouse/schema, run `setup_metadata_tables()` to create `METADATA_PROCESSING_STATE`, then execute the reviewed target rebuild/replay. Never reset the six Live tables, Pipeline Run, or Activation State. For migration, populate `METADATA_PROCESSING_STATE` with the validated complete schema, then archive/remove the old physical name and run setup validation before restarting writers. A physical rename alone is valid only after verifying the complete new schema, record-key uniqueness, receipt references and empty-header semantics. Older empty-source sentinels must be reconciled against real NULL/empty-string partitions before transformation; do not infer whether they represent a removed partition or a dataset header. Older layouts require the field transformation above. Leaving both physical names present intentionally blocks setup.
5. Validate first/subsequent incremental execution, unchanged/empty reads, Source Drift baseline decisions, lost-acknowledgement retries and environment/target isolation. Keep the backup until these checks finish. Rollback requires stopping writers and restoring both a compatible code/schema pair and a reconciled checkpoint/target boundary; restoring metadata alone after new publications is unsafe.

The new exact receipt includes its physical strategy. Old Delta commit metadata cannot be rewritten into new physical proof: retain old receipts for reconciliation, and use a reviewed target rebuild/replay to establish new-format receipts wherever automatic retry verification is needed. Migrating accepted progress alone does not retrofit old physical receipts. Recovery restores Processing State; replay the exact prepared Write if separate Catalogue or Lineage finalization also needs retry.

No automatic conversion is supplied because old rows can lack watermark types, column identities or exact physical publication proof. The retained backup is the explicit record-retention policy; operators decide archival retention after reconciliation. Focused unit tests cover schema rejection and classification; Delta integration tests cover persisted source checkpoints, lost acknowledgements, retries and atomic multi-source acceptance. Warehouse transport is simulated against real Delta business rows; Fabric Warehouse itself still requires deployment validation.

### Pipeline execution (engineering)

`engineering.METADATA_PIPELINE_RUN` stores a typed `run` parent and its `operation` records in one canonical Delta table. Implementation is under review in [#1700](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1700), using merged #1697 and #1698 as the baseline. Activation State authority and Processing State recovery remain isolated.

#### Decision and inventory

Stable operation IDs, roles, table IDs, exact frozen contracts, configuration hashes, statuses and timing are scalar columns. Operators can inspect Reads/Writes and join Guardrail Results without exploding a broad summary document. Extensible processing configuration and sanitized stage lists remain per-operation JSON. Exact candidate content remains on the parent for fingerprint verification; it is not an alternative execution-status authority. Run details retain frozen contract references, physical bindings, activation revision, profiling events, warnings and safe failures. No extra public callable, schema or metadata table is introduced.

| Reader / writer | Previous assumption | Typed implementation |
| --- | --- | --- |
| `build_pipeline_execution_plan`, Live setup, `PipelineOperation`, profiling journal, `finalize_pipeline_run` | `persist_pipeline_run` replaced one row keyed by run_id | Same journal owner encodes one run and all operations; one atomic publication |
| `publish_pipeline_testing_results`, `finalize_pipeline` | Explicit Test finalization publishes stable diagnostics before run | Same order; typed parent and operations publish together after diagnostic commits |
| `_merge_pipeline_run_row` | Unconditional merge on run_id | Initial idempotent Delta append; subsequent Serializable CAS merge on record_id |
| Persistence exception read-back | At most one physical row | One collected snapshot; validate all matching rows and the attempted token |
| `activated_pipeline.shared.metadata_records` / `tested_pipeline_manifest` | One run row containing summary operations | Reconstruct notebook-facing results only after token, membership, digest, identity and provenance verification |
| `widget_activate_pipeline` | Logical run candidate and operation summaries | Uses the same verified domain reader; review details and notebook controls unchanged |
| Activation candidate/contract review | candidate_json, operations, frozen_contracts, boundary_completed, physical_bindings, stages and provenance | All preserved; exact frozen contract columns also permit direct operation/result joins; existing frozen payload, candidate, stage, binding and rule checks retained |
| `profiling_completion_history` | Exploded summary.profiling | Filters record_type=run and reads run_details_json.profiling; joins actual persisted profile snapshots as before |
| Guardrail Results writer / activation join | Per-rule result keyed by stable result ID and run/contract | Grain unchanged; activation checks exact run, environment, notebook, workspace and activity provenance before rule coverage |
| Metadata setup / registry | Old physical run layout allowed additive evolution | Rejects old or partial typed layout, including empty old tables; explicit offline conversion required |
| Reference, explorer and ERD generators | run_id as physical primary key | record_id as physical primary key; typed grain, fields and ownership generated from canonical sources |
| Release contracts | Six Live metadata schemas | Unchanged; no historical release snapshot edits |

Repository searches covered all direct `METADATA_PIPELINE_RUN` and `operation_summary_json` usages in package source, scripts and tests. The summary field remains a supported notebook-facing result, not a second persisted layout or legacy physical reader. Immutable historical activation manifests retain their original embedded Testing results and are not rewritten.

The cost is that each publication still rewrites the full operation set, and Delta retains one transaction identity per run. This preserves one atomic status owner while moving operational inspection and joins to scalar fields; it does not claim fewer writes or remove the exact candidate document. No cross-table operation store or runtime compatibility path is needed.

#### Physical schema and keys

Only `METADATA_PIPELINE_RUN` changes. The old schema had required strings run_id, pipeline_id, execution_mode, environment_name, status, candidate_json and operation_summary_json; required started_at timestamp; nullable activated_pipeline_id/candidate_fingerprint strings and completed_at timestamp; and the eight required audit fields. The new schema is below. Spark physical readers can report nullable fields even when the canonical writer schema is required; type-specific application validation supplies the stronger constraints.

| New field | Spark type | Nullable | Source / meaning |
| --- | --- | --- | --- |
| `record_id` | `string` | No | New SHA-256 of `[run_id, "run"]` or `[run_id, "operation", operation_key]`. |
| `record_type` | `string` | No | New `run` or `operation` discriminator. |
| `snapshot_token` | `string` | No | New publication UUID; offline conversion uses `offline:<run_id>`. |
| `run_id` | `string` | No | Preserve original execution attempt on every row. |
| `activated_pipeline_id` | `string` | Yes | Preserve exact activated release on every row; null for Test. |
| `pipeline_id` | `string` | No | Preserve permanent Pipeline Registry UUID on every row. |
| `execution_mode` | `string` | No | Preserve `testing` or `live` on every row. |
| `environment_name` | `string` | No | Preserve environment on every row. |
| `started_at` | `timestamp` | No | Preserve original run start on every row; not an operation start. |
| `completed_at` | `timestamp` | Yes | Preserve on run row; null on operation rows. |
| `status` | `string` | No | Preserve run outcome on parent; copy each operation status from summary. |
| `candidate_fingerprint` | `string` | Yes | Preserve on run row; null on operation rows. |
| `candidate_json` | `string` | Yes | Preserve exact serialized candidate on run row; null on operation rows. |
| `run_details_json` | `string` | Yes | Original summary excluding `operations` and `boundary_completed`; all other fields retained losslessly on run row. |
| `boundary_completed` | `boolean` | Yes | Original summary completion boundary on run row; null on operation rows. |
| `operation_count` | `long` | Yes | New exact count of declared role-qualified operation keys on run row. |
| `operations_digest` | `string` | Yes | New SHA-256 of sorted typed operation identities, statuses, contract/configuration references, stage payloads and timing on run row. |
| `operation_id` | `string` | Yes | New SHA-256 of `[run_id, operation_key]`; operation rows only. |
| `operation_key` | `string` | Yes | Preserve summary operation map key (`source:<participant>` or `target:<participant>`). |
| `role` | `string` | Yes | Exact source/target role resolved from candidate participant; operation rows only. |
| `table_id` | `string` | Yes | Exact candidate global table identity for operation; missing or ambiguous mapping rejects conversion. |
| `operation_type` | `string` | Yes | Read for source; Write for target. |
| `contract_id` | `string` | Yes | Exact summary frozen contract ID for operation participant; null for No Contract. |
| `contract_version` | `integer` | Yes | Exact summary frozen contract version; null for No Contract. |
| `contract_payload_sha256` | `string` | Yes | Exact summary frozen payload hash; null for No Contract. |
| `operation_started_at` | `timestamp` | Yes | Original operation start when available; null for unknown historical timing. Never substitute run start. |
| `operation_completed_at` | `timestamp` | Yes | Original operation completion when available; null for unknown historical timing. |
| `configuration_sha256` | `string` | Yes | Preserve operation configuration identity; null when not yet known. |
| `configuration_json` | `string` | Yes | Losslessly serialize one operation configuration; null when not yet configured. |
| `stages_json` | `string` | Yes | Losslessly serialize one operation stage list; operation rows only. |
| `failure_code` | `string` | Yes | Derived `blocked` for a blocking stage, otherwise `failed` for failed operation, otherwise null. |
| `_committed_by` | `string` | No | Preserve original required audit value on every row; no invented provenance. |
| `_committed_at` | `timestamp` | No | Preserve original required audit value on every row; no invented provenance. |
| `_workspace_id` | `string` | No | Preserve original required audit value on every row; no invented provenance. |
| `_workspace_name` | `string` | No | Preserve original required audit value on every row; no invented provenance. |
| `_notebook_id` | `string` | No | Preserve original required audit value on every row; no invented provenance. |
| `_notebook_name` | `string` | No | Preserve original required audit value on every row; no invented provenance. |
| `_metadata_lakehouse_name` | `string` | No | Preserve original required audit value on every row; no invented provenance. |
| `_activity_id` | `string` | No | Preserve original required audit value on every row; no invented provenance. |

`record_id` is the physical unique key. `(run_id, record_type, operation_key)` is the logical composite key, with null operation_key only for the sole run row. `(run_id, operation_id)` uniquely identifies a Read/Write. Operation IDs are deterministic per run and logical role; the role-qualified operation key is stable across attempts. Registry joins use pipeline_id + environment_name. Live release joins use exact activated_pipeline_id. Guardrail joins use run_id + environment_name + table_id + contract_id + contract_version; rule IDs remain at the separate rule-result grain. Do not join results to every row on run_id alone and multiply counts.

#### Atomic publication and recovery

1. The first publication appends the complete row set in **one Delta transaction**, with `txnAppId=fabricops-pipeline-run:<run_id>` and txnVersion=0. Competing first writers cannot duplicate it. A read first rejects an existing run ID. Delta transaction identity retention must remain unbounded (the default); an explicitly configured retention duration is rejected.
2. Each later publication merges the complete row set on record_id in **one Serializable Delta transaction**. Its parent and every existing child must match the previous snapshot token. A stale token raises inside the merge expression, aborting child updates and unmatched inserts together. A failed parent cannot regress to success. Any parent with completed_at is immutable, including failed/incomplete terminal runs. Repeated finalization returns the sealed result without a new mutation.
3. There is no last-row publication ordering: the parent and every operation become visible at the **same Delta commit boundary**. A successful operation never sets parent success. Missing operations, failures, unresolved/duplicate stages or a missing explicit whole-run boundary cannot assert successful authority. Readers collect all selected rows from one DataFrame action and verify matching provenance/tokens, operation count, deterministic identities and content digest. A partial or corrupt snapshot fails closed.
4. Test operations remain in memory. Only explicitly finalized Test publishes the allowed run and Guardrail diagnostic records. Testing does not publish business tables, checkpoints, Catalogue or Lineage. Live retains approved-version and existing publication enforcement.
5. Guardrail Results commit first, then the entire typed run snapshot. There is no cross-table atomicity claim. A crash before run publication leaves diagnostics without approving authority. Activation independently verifies the exact frozen contracts, required stages, candidate/bindings and complete exact rule-result set. Missing, foreign or blocking results prevent approval.
6. After an exception, read-back verifies the complete row set, attempted token and logical content. A physically committed matching snapshot confirms a lost acknowledgement. Unconfirmed or unreadable outcomes poison the plan; inspect the persisted snapshot and start a new run, without replaying business publication from this plan. An interrupted unfinalized Live run stays incomplete; unfinished Test has no approving persisted snapshot.

#### Offline conversion and rollout

**Breaking Preview physical-layout change. Public notebook callables and result shapes remain supported.** Setup fails on old layouts instead of additive-evolving history. No dual writer or compatibility reader exists.

1. Stop/drain Test and Live writers, readers and profiling jobs. Inventory in-flight runs, exact candidate/contract mappings, approvals and diagnostic retention. Take a durable backup of the old run table, record its Delta version and retain the old code/schema pair. Also retain Guardrail Results, frozen contracts, Registry bindings and Activation State history. No records are deliberately discarded.
2. Install the new package in an isolated Spark/Delta session. Convert a **version-pinned** source to a **separate new location** in the configured Metadata Lakehouse using:

   ```bash
   python scripts/migrate_pipeline_runs.py \
     --source-path <configured-old-run-delta-path> \
     --source-version <backed-up-version> \
     --destination-path <new-staging-delta-path>
   ```

   The script reads source only, rejects duplicate run IDs, forces validation of every row before writing, and refuses an existing destination. It preserves run IDs, timestamps, status, provenance, frozen references, activation links and every summary detail. It reconstructs each run and compares it with the original before accepting it. Unknown operation fields, missing/ambiguous operation membership or unprovable successful authority stop conversion. No success is inferred from isolated rule results or fabricated from run status. Older history without exact participant table IDs or whole-run boundaries requires explicit operator reconciliation; retain it in backup until resolved. Never replace it with an empty table.
3. Validate the converted parent counts against source run count, operation membership/digests, exact candidate fingerprints, Registry/release references, profiling history and Guardrail coverage. Re-review previously eligible finalized Test runs with current bindings; do not reinterpret ineligible historical runs as successful tests. In-flight runs remain historical incomplete/failed records and must resume as new execution attempts.
4. While all writers remain stopped, cut over the canonical `engineering.METADATA_PIPELINE_RUN` registration/path to the verified typed Delta table using the configured Metadata Lakehouse. Keep the physical canonical name and configured ownership schema. Run setup and targeted Test/Live smoke checks before resuming. Do not use attached-default shortcuts or overwrite the source as a conversion step.
5. Before new executions, rollback may restore the old table registration and matching old package from backup. After new typed runs or new approvals exist, stop writers again and reconcile/archive those new runs and references before rollback; simply restoring the old table would erase execution history. Preserve Activation State history and Processing State receipts/checkpoints throughout. Keep the old backup through deployment validation and the agreed operational retention period.

The new migration utility is an offline deployment tool, not a runtime fallback. Fabric Lakehouse registration/cutover, Fabric Warehouse transport, notebook deployment permissions and live runtime concurrency require separate deployment validation; local persisted Delta tests do not establish those results.

#### Query examples

```sql
-- Inspect Read/Write outcomes without parsing the run summary.
SELECT run_id, operation_id, operation_type, table_id, status,
       contract_id, contract_version, configuration_sha256,
       operation_started_at, operation_completed_at, failure_code
FROM engineering.METADATA_PIPELINE_RUN
WHERE record_type = 'operation' AND environment_name = 'DEV';

-- Whole-run outcomes: operation success never substitutes for this parent.
SELECT run_id, pipeline_id, activated_pipeline_id, status, completed_at
FROM engineering.METADATA_PIPELINE_RUN
WHERE record_type = 'run' AND environment_name = 'DEV';
```

#### Verification and review boundary

Require unit and persisted Delta coverage for read-only, single-Read/Write and multi-source/multi-target runs; exact table/contract/stage identity; explicitly finalized Test eligibility with complete Guardrail coverage and current bindings; and zero Test business/checkpoint/Catalogue/Lineage publication. Live continues to require its exact activated version.

Missing, failed, blocked, duplicated or unresolved operations/stages, project failures and interrupted or unfinalized runs cannot authorize activation. Exercise reordered or partial writes, stale and simultaneous writers, **concurrent independent runs**, lost acknowledgements before and after physical commit, repeated finalization, profiling/Registry/Guardrail joins and wrong-environment isolation. Verify the offline converter retains valid history and rejects ambiguous mappings; setup must reject incompatible physical layouts.

Keep all six Live schemas, Processing State recovery and Activation State CAS unchanged. Run Ruff, relevant pytest suites, compile/import checks, strict MkDocs and affected generator freshness checks, including two clean repeated generations. Record actual commands/results in the implementation PR and distinguish persisted local Delta tests from unexecuted Fabric Lakehouse/Warehouse deployment checks. Maintainer review and CI remain required; do not merge automatically.

### Activation authority (governance)

Investigate queryable `authority`, `approval`, `activation`, `participant`, and `reservation` records. The existing central `snapshot_json` and `token` are currently committed using Serializable Delta compare-and-swap, protecting approvals, writer ownership, activation revisions, and running/rebind reservations.

**Required invariants:** approval publication is atomic; incomplete or stale revisions never become executable; Live runs pin the correct approved revision; writer ownership and rebind barriers are enforced; stale CAS conflicts fail closed; lost acknowledgement is recoverable. Multiple independent Delta writes are **not** an atomic replacement for the existing singleton. If the proposed typed-row layout cannot prove equivalent guarantees, retain the authority snapshot and improve only safe read/query projections.

### Contract, Guardrail, and Access (governance / engineering)

Do not split contract rule expressions into separate physical tables by default. Keep `METADATA_GUARDRAIL_RESULTS` one row per rule outcome and retain exact contract/run attribution. Keep `METADATA_DATA_ACCESS` as observations from Workspace, OneLake, and SQL surfaces, not an unverified effective-access calculation. Make targeted changes only when an identified reader, query, or correctness issue justifies them.

## Deployment and migration contract

Before a structural implementation PR, document for **every changed table**: old and new fields with Spark types/nullability, logical key, `record_type` values, all readers and writers, transformation mapping, retained records, discard policy, cutover preconditions, rollback boundary, and test coverage.

- Existing Live tables must remain readable without a rebuild.
- Preview breaking changes do not need compatibility shims, but deployed state must be classified as safely migratable or explicitly resettable.
- Never reset incremental checkpoints, publication receipts, active reservations, or approval history casually. Drain in-flight Live runs before a breaking cutover.
- `setup_metadata_tables()` should fail clearly on incompatible physical schemas; no silent data loss or accidental schema evolution.
- A PR must not merge if it leaves `main` with incompatible metadata readers/writers.
- Retain existing two-schema routing; no new metadata schema or storage service.

## Implementation workstreams and sequencing

| Workstream | Status at 2026-10-25 | Executor | PR / implementation | Dependencies and merge boundary |
| --- | --- | --- | --- | --- |
| A. Architecture and lifecycle audit | Merged | ChatGPT | [#1695](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1695) | Documentation baseline; no runtime changes |
| B. Focused metadata reference fixes | Merged (initial fixes) | ChatGPT | [#1696](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1696); metadata explorer [#1692](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1692) | Additional fixes only when a concrete discrepancy is found |
| C. Processing State redesign | Merged | Codex | [#1698](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1698) | Implemented `METADATA_PROCESSING_STATE`; keep its recovery protocol isolated |
| D. Pipeline Run normalization | Implemented in open PR; review outstanding | Codex | [#1700](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1700); [implementation and migration](#pipeline-execution-engineering) | Includes merged #1697 and #1698; preserve finalized Test results; verified offline cutover required |
| E. Activation authority redesign | Pending separate design proof | Codex | Related foundation [#1693](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1693); evidence change [#1697](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1697) merged | Keep authority CAS, approvals and reservations isolated from D; no unsafe split of the atomic authority snapshot |
| F. Contract/Guardrail/Access cleanup | Conditional / targeted prior work | ChatGPT for bounded fixes; otherwise Codex | Contract cleanup [#1649](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1649) and Guardrail integration [#1645](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1645) merged | Skip additional physical normalization without a demonstrated benefit |
| G. Final integration/reference generation | Pending final review | Owner of affected source | After relevant backend work | Regenerate only artifacts directly affected by C–F; verify clean second generation |

**Coordination:** C has merged, so D uses the latest canonical metadata schema, including the #1698 Processing State redesign. #1697 has merged and changes D's Test-evidence readers/writers. D preserves this durable finalized Test evidence for activation. D and E remain separate implementation PRs; do not split the atomic Activation State authority while working on Pipeline Run. A merged PR denotes merged scope, **not** a claim that live Microsoft Fabric deployment validation has completed.

## Acceptance tests

- Fresh setup and incompatible existing schema detection.
- Day 1/Day 2 incremental reads, no-change reruns, drift, failed write, lost acknowledgement, and idempotent publication recovery.
- Live versus Test persistence, interrupted run, failed operation, repeated finalization, and authoritative run status.
- Concurrent activation, stale revision, approval immutability, reservation release, rebind barriers, and lost CAS acknowledgement using persisted Delta where transaction semantics matter.
- Live table schema fingerprints unchanged unless separately approved.
- No extra metadata schemas, compatibility wrappers, or unrelated generated refreshes.
- All relevant generators run from their authoritative source; generated reference pages are not manually edited, and a second generation run is clean.

## Decisions intentionally deferred to implementation audit

Processing State is implemented on main; Pipeline Run implementation is documented above and remains under review in #1700. Remaining Activation State names, columns and record types are candidates, not approved physical contracts. Any further structural change requires a field-by-field schema and proof of benefit without weakening correctness. Multiple independent commits to one Delta table do not provide atomic publication of typed activation records.
