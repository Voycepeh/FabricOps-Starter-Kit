# Metadata v2: target model and migration boundaries

**Status (2026-10-25):** Processing State implemented by [#1698](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1698). A typed Pipeline Run operations array is implemented in open [#1700](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1700), with review outstanding. Activation State physical redesign remains a proposal. Merged [#1697](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1697) persists explicitly finalized Test execution and Guardrail results for activation; D preserves this contract.

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
| `METADATA_PIPELINE_RUN` | engineering | Not listed | One run row with a typed operations array in open #1700; preserve whole-run authority and exact Test results |
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

This Preview layout and table name are a breaking replacement: `METADATA_SOURCE_OBSERVATION` → `METADATA_PROCESSING_STATE`. There is no legacy alias or fallback reader. Setup permits the old physical table to remain, including alongside the canonical table, and returns an advisory retirement alert. A fresh canonical table does not establish valid operational progress for populated targets. `observation_status` and `publication_payload_json` are removed. Old rows must **not** be additive-evolved into typed progress. Setup and runtime still reject an incompatible layout under the canonical `METADATA_PROCESSING_STATE` name, including an empty table. No compatibility reader, automatic migration, reset, or discard is performed.

1. Stop/drain writers and take a durable backup of the existing `METADATA_SOURCE_OBSERVATION` table plus the code/version needed to read it. Retain target data, target audit markers, and Delta history. Inventory all source/target/environment relationships, accepted progress and unresolved publications.
2. Reconcile every staged publication against the physical target before cutover. In the old layout, `committed` corresponds to `incremental_checkpoint`; `drift_committed` to `drift_baseline`; `publication_observed`/`publication_committed` to staged/committed receipts. Old target-bound `observed`/`drift_observed` rows are staged candidates, never automatically accepted checkpoints. Decode and deduplicate exact receipt JSON into typed receipt rows; retain originating run/audit identities. Column/type evidence missing from old records must be supplied from the verified original processing definition, not inferred silently from current configuration.
3. Choose an explicit, reviewed cutover: an offline migration into the complete canonical schema with deterministic IDs and validated receipt references; or a reset only after reconciling/archiving progress and preparing a governed target rebuild or idempotent replay. A populated append target without an accepted baseline is intentionally rejected. Dropping only the metadata table and continuing incremental append is unsafe.
4. For a deliberate reset, preserve a durable archive of the reconciled old Preview table, run `setup_metadata_tables()` to create `METADATA_PROCESSING_STATE`, then execute the reviewed target rebuild/replay. Never reset the six Live tables, Pipeline Run, or Activation State. For migration, populate `METADATA_PROCESSING_STATE` with the validated complete schema, then archive/remove the old physical name and run setup validation before restarting writers. A physical rename alone is valid only after verifying the complete new schema, record-key uniqueness, receipt references and empty-header semantics. Older empty-source sentinels must be reconciled against real NULL/empty-string partitions before transformation; do not infer whether they represent a removed partition or a dataset header. Older layouts require the field transformation above. Both physical names may remain during reconciliation; the retired name produces an advisory alert and is never read by runtime.
5. Validate first/subsequent incremental execution, unchanged/empty reads, Source Drift baseline decisions, lost-acknowledgement retries and environment/target isolation. Keep the backup until these checks finish. Rollback requires stopping writers and restoring both a compatible code/schema pair and a reconciled checkpoint/target boundary; restoring metadata alone after new publications is unsafe.

The new exact receipt includes its physical strategy. Old Delta commit metadata cannot be rewritten into new physical proof: retain old receipts for reconciliation, and use a reviewed target rebuild/replay to establish new-format receipts wherever automatic retry verification is needed. Migrating accepted progress alone does not retrofit old physical receipts. Recovery restores Processing State; replay the exact prepared Write if separate Catalogue or Lineage finalization also needs retry.

No automatic conversion is supplied because old rows can lack watermark types, column identities or exact physical publication proof. The retained backup is the explicit record-retention policy; operators decide archival retention after reconciliation. Focused unit tests cover schema rejection and classification; Delta integration tests cover persisted source checkpoints, lost acknowledgements, retries and atomic multi-source acceptance. Warehouse transport is simulated against real Delta business rows; Fabric Warehouse itself still requires deployment validation.

### Pipeline execution (engineering)

`engineering.METADATA_PIPELINE_RUN` retains **one authoritative row per run**. Open [#1700](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1700) replaces broad operational JSON with a native typed `operations` array and typed nested stages, using merged #1697 and #1698 as its baseline. The earlier multirow proposal is superseded: no operation table, record discriminator, duplicate IDs, snapshot token, operation count or content digest is needed.

#### Storage decision and inventory

The complete operation set is part of the run row and publishes in the same Delta transaction. Operators query stable table/contract identities, statuses, timestamps and stages through `explode(operations)`, without JSON parsing. Role and operation type derive from the role-qualified operation key rather than duplicate columns. `(run_id, operation_key)` identifies an operation. Flexible processing configuration stays in each operation's configuration_json. Exact candidate content remains in candidate_json for fingerprint verification; run_details_json retains frozen references, profiling events, bindings, warnings, activation revision and sanitized failures.

| Reader / writer | Previous assumption → implementation |
| --- | --- |
| Plan setup, `PipelineOperation`, profiling journal, `finalize_pipeline_run` | One logical journal → one physical run row with a native operation/stage array; actual operation timing retained |
| `persist_pipeline_run`, `_merge_pipeline_run_row`, exception read-back | Unconditional run_id upsert → run_id key retained, complete-previous-row CAS, terminal immutability and exact read-back |
| `finalize_pipeline`, `publish_pipeline_testing_results` | Stable Test diagnostics before final run → same order; the operation array commits with the authoritative run outcome |
| `metadata_records`, `tested_pipeline_manifest`, activation widget | Candidate and summary operation/contract/binding/stage data → validated typed fields reconstruct the supported notebook result; exact contract, candidate, binding, stage, provenance and rule checks remain |
| `profiling_completion_history` | summary.profiling → run_details_json.profiling; physical profile/frequency snapshot joins unchanged |
| Guardrail writer / activation reader | Stable result IDs and per-rule run/contract grain unchanged; exact environment, notebook, workspace and activity provenance required |
| Setup and offline converter | Old summary layout → reject incompatible layouts and require verified conversion; no runtime fallback or additive reinterpretation |
| Metadata/reference/ERD generators | Source-owned fields → run_id remains the physical key; nested Spark types and directly affected references are generated |

The supported notebook return shape still includes operation_summary_json, reconstructed from typed storage. It is not a persisted legacy reader. Historical approval manifests retain their embedded Test results without rewriting Activation State. Public callable signatures and the six Live schemas remain unchanged.

#### Physical fields and historical mapping

The old table had 19 columns: run_id, activated_pipeline_id, pipeline_id, execution_mode, environment_name, started_at, completed_at, status, candidate_fingerprint, candidate_json, operation_summary_json and the eight audit fields. The new table has **21 top-level columns**: remove operation_summary_json and add boundary_completed, operations and run_details_json. All retained scalar columns keep their types and nullability.

| Top-level fields | Spark type / nullability | Historical mapping |
| --- | --- | --- |
| run_id, pipeline_id, execution_mode, environment_name, status | Required string | Preserve original run identity, context and whole-run outcome |
| activated_pipeline_id, candidate_fingerprint | Nullable string | Preserve exact Live release and candidate identity |
| started_at | Required timestamp | Preserve original run start |
| completed_at | Nullable timestamp | Preserve finalization time; a completed row is immutable |
| candidate_json | Required string | Preserve exact candidate serialization and fingerprint contract |
| boundary_completed | Required boolean | Extract summary.boundary_completed |
| operations | Required array of non-null structs | Transform every summary.operations entry using exact candidate/frozen-contract participant mappings |
| run_details_json | Required string | Preserve all other summary fields, excluding operations and boundary_completed |
| _committed_by, _workspace_id, _workspace_name, _notebook_id, _notebook_name, _metadata_lakehouse_name, _activity_id | Required string | Preserve the seven existing audit identities on the single run row |
| _committed_at | Required timestamp | Preserve original audit instant |

Each `operations` element contains:

| Nested field | Spark type / nullability | Mapping / purpose |
| --- | --- | --- |
| operation_key | Required string | Original `source:<logical-participant>` or `target:<logical-participant>` key; stable within a run |
| table_id | Required string | Exact global table identity from the candidate; ambiguous mappings stop conversion |
| status | Required string | Preserve operation status |
| started_at, completed_at | Nullable timestamp | Actual operation timing when recorded; unknown historical times stay null |
| configuration_sha256 | Nullable string | Preserve exact processing configuration identity |
| configuration_json | Nullable string | Losslessly serialize that operation's flexible configuration |
| contract_id | Nullable string | Exact frozen contract ID; null for No Contract |
| contract_version | Nullable integer | Exact frozen contract version; null for No Contract |
| contract_payload_sha256 | Nullable string | Exact frozen payload hash; null for No Contract |
| stages | Required array of non-null structs | Preserve stages as native typed fields: required stage/status strings and nullable evaluation_status string |

The schema in `metadata_schemas.py` is authoritative, including nested field nullability. Spark may report looser physical nullability; readers enforce membership, unique keys, exact table/contract/configuration identity and successful-boundary constraints. Registry joins use pipeline_id + environment_name, release joins use exact activated_pipeline_id, and Guardrail joins use run_id + environment_name + operation.table_id + exact contract/version. Explode once before operation/rule joins to avoid multiplying counts.

#### Atomicity, concurrency and recovery

1. First publication appends **one complete row** with Delta txnAppId=fabricops-pipeline-run:<run_id> and txnVersion=0. Existing run IDs are rejected. Concurrent identical first-publication acknowledgements may confirm the same row, but cannot duplicate it. Transaction identity expiration must remain unconfigured; the default unbounded retention is required.
2. Later publications merge on run_id and compare the **entire previous row** inside the transaction. The expected struct exists only in the source DataFrame and in the plan's memory, not in the persisted schema. Stale rows raise inside MERGE. Failed outcomes cannot regress to success; completed rows cannot be replaced. Repeated finalization returns the sealed result without another mutation.
3. Delta's normal optimistic write conflict detection protects same-row mutation. A bounded retry handles only Delta exceptions that establish an aborted data-write transaction, covering unrelated runs sharing a data file. The exact previous-row guard remains on every retry. Business publication is never replayed by this retry. Runtime performs **no ALTER TABLE or table-property mutation**; removing the per-update DDL fixes the reproduced independent-run MetadataChangedException.
4. Parent outcome and all operations/stages become visible at one row-commit boundary. A successful operation never sets parent success. Readers reject missing/duplicate operation keys, foreign table/contract/configuration mappings, failed/blocked/unresolved/duplicate stages and a missing whole-run boundary. Activation additionally verifies exact frozen payloads, required stages, current notebook/workspace/environment bindings and complete required rule results.
5. Test Read/Write remains in memory. Only explicit Test finalization commits allowed run and Guardrail diagnostics, without business data, checkpoints, Catalogue or Lineage publication. Guardrail Results commit first; the run and its full operation array commit afterward. There is no cross-table atomicity claim: diagnostics without run authority, or a run without required matching diagnostics, cannot authorize activation.
6. After lost acknowledgement, read-back validates the single row and compares the complete logical result, normalizing timestamp instants. An exact committed result confirms completion. Unknown outcomes poison the plan and require inspection; do not replay business publication. An interrupted Live run remains incomplete and unfinished Test has no approving persisted run.

#### Offline conversion and rollout

**This is a Preview physical-layout change.** Setup rejects old summary rows, the superseded multirow layout and incomplete typed schemas rather than adding columns to reinterpret history. No compatibility reader, dual writer or silent reset is supplied.

1. Stop/drain readers and Test/Live writers. Back up the old run Delta table and matching package; pin its version. Retain Guardrail Results, frozen contracts, Registry bindings, approval history and Processing State. No run history is deliberately discarded.
2. In an isolated configured Spark/Delta session, convert the old summary layout to a new, separate location using the matching package:

   ```bash
   python scripts/migrate_pipeline_runs.py \
     --source-path <configured-old-run-delta-path> \
     --source-version <backed-up-version> \
     --destination-path <new-staging-delta-path>
   ```

   The converter reads source only, rejects duplicate run IDs, validates every transformation before destination publication and refuses an existing destination. It reconstructs and compares each logical run with its original. Missing/ambiguous operation mappings, unknown historical fields or unprovable success stop conversion for explicit reconciliation. Preserve unknown timing as null; never infer successful operation facts from run status or isolated rule results. The superseded multirow design was not merged or deployed by this PR and is not supported by this converter; any independently deployed copy requires explicit reconciliation first.
3. Verify one destination row per source run; exact candidate/status/provenance retention; complete operation/stage arrays; Registry/release links; profiling history; and required Guardrail coverage. Current bindings still govern Test eligibility. In-flight historical runs remain incomplete/failed and continue only as new attempts.
4. While stopped, replace the Delta contents at the canonical configured Metadata Lakehouse table path with the verified typed table, retaining a rollback backup and correct registration. Readers derive the physical path from the configured Lakehouse/schema/table name; **changing only a catalogue registration's location is insufficient**. Use the actual Fabric path/cutover procedure and retain the canonical engineering ownership/name. Run setup and Test/Live smoke checks before resuming.
5. Before new executions, rollback restores the backed-up table and matching package. After new runs or approvals, stop and reconcile those new records/references before rollback; restoring an old metadata copy alone would erase history. Preserve Activation State and Processing State throughout, and keep backups through deployment validation and agreed retention.

#### Queries and verification

```sql
SELECT r.run_id, op.operation_key, op.table_id, op.status,
       op.contract_id, op.contract_version, op.started_at, op.completed_at
FROM engineering.METADATA_PIPELINE_RUN r
LATERAL VIEW explode(r.operations) expanded AS op
WHERE r.environment_name = 'DEV';
```

Persisted tests cover finalized Test → activation with exact contracts/rules/bindings, missing/duplicate/foreign operations and stages, lost acknowledgements immediately after physical commit, immutable final rows, stale and simultaneous same-run writers, **independent concurrent runs sharing a data file**, direct native operation/stage queries and the executable offline converter. Retain Test dry-run, Live pinned-version, profiling and failure regressions. Compare all other 12 canonical schemas with baseline; do not change Processing State recovery or Activation State CAS.

Run Ruff, targeted pytest, compile/import checks, strict MkDocs and affected generators with two clean repeated passes. Fabric Lakehouse cutover, Warehouse transport, notebook deployment permissions and actual Fabric concurrency remain separate deployment checks; local persisted Delta tests do not claim cloud validation. Maintainer review and CI remain required; do not merge automatically.

### Activation authority (governance)

Workstream E replaces `snapshot_json` with native `authority`, `environment`, `approval`, `activation`, `participant`, `ownership`, `reservation` and `profiling_claim` records in the same governance table. One guarded Delta MERGE publishes the entire set atomically, including unmatched child inserts and removals. Readers validate publication count/hash, tokens, keys, parents, exact frozen participants and ownership before reconstructing notebook results.

See [Activation State records](activation-state-records.md) for the exact physical model, reader/writer inventory, transaction proof, retained configuration/diagnostic JSON, Preview reset/reconciliation procedure and operational limits. Processing State and Pipeline Run schemas and recovery remain unchanged. No compatibility reader, dual write or automatic migration is introduced.

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
| D. Pipeline Run normalization | Merged | Codex | [#1700](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1700); [implementation and migration](#pipeline-execution-engineering) | Includes merged #1697 and #1698; preserve finalized Test results; verified offline cutover required |
| E. Activation authority redesign | Implemented; review pending | Codex | Related foundation [#1693](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1693); evidence change [#1697](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1697) merged | See [typed records and transaction proof](activation-state-records.md); one central guarded publication, no independent child writes |
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

Processing State is implemented on main; Pipeline Run #1700 has merged. Activation State implementation and its reviewed deployment boundary are documented in [Activation State records](activation-state-records.md). Any further structural change requires a field-by-field schema and proof of benefit without weakening correctness. Multiple independent commits to one Delta table do not provide atomic publication of typed activation records.

## Retirement declarations and Live upgrade policy

`RETIRED_PREVIEW_METADATA_TABLES` in `src/fabricops_kit/config/metadata_schemas.py` is the authoritative retirement registry: declare the retirement version and intentional current-model guidance when removing a released Preview table. The inventory consistency test compares historical release manifests and the current canonical registry; it excludes supported Live tables. Setup probes only these names in both configured Governance and Engineering schemas through the configured Metadata Lakehouse, without collecting historical rows. Missing tables produce no alert; access/storage failures produce advisory diagnostics. Cleanup requires preserving required definitions, progress or history before deleting a table or explicitly mapping/migrating retained records. Similar names do not establish a safe conversion, and old rows must not be blindly appended to current models. Setup does not migrate or delete Preview data.

Preserve supported Live tables and existing rows. Compatible additive columns may be applied automatically without replacing data. An approved Live column removal, rename or type change must ship with an explicit, tested automatic migration. It must preserve required data, validate results, support safe repeated execution and define a rollback boundary. Users must not be asked to drop/rebuild supported Live tables or guess conversions. This cutover changes no Live schemas and introduces no hypothetical conversions.
