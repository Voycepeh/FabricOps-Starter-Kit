# Metadata v2: target model and migration boundaries

**Status (2026-10-26):** Processing State [#1698](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1698) and Pipeline Run [#1700](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1700) are merged. Activation-only [#1704](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1704) is closed without merging and superseded by the [joint pipeline metadata redesign](#joint-pipeline-metadata-redesign). Plan Registry, Activation State, Pipeline Run and participation together before starting one fresh implementation PR. This document proposes the replacement; it does not describe an implemented replacement schema or prove its transaction design.

## Goal and constraints

Treat FabricOps metadata as an operational application database, not a reporting star schema. Prefer queryable typed records and explicit relationships over large nested state documents, but do not normalize flexible configuration for its own sake.

- Keep **one metadata Lakehouse** and exactly the two existing logical ownership schemas: `governance` and `engineering`. Respect configured physical schema names.
- Retain the six published Live metadata contracts unchanged unless a separate decision demonstrates a substantial long-term benefit.
- Preview contracts may change without deprecated aliases, dual writes, or transitional API wrappers. Operational checkpoints, frozen contracts, and approval history still need a deliberate migration or safe cutover.
- Do not introduce Azure SQL, extra metadata schemas, or a separate control-plane database.
- Do not require the physical table count to decrease. A `record_type` discriminator is appropriate only when row types have compatible identity, lifecycle, and transaction semantics.
- Preserve public notebook workflows: Test operations stay in memory; explicit finalization persists the allowed Test run and Guardrail diagnostics for activation, as implemented by #1697. The proposed joint design may additionally seal its immutable tested definition at finalization; it must not enable business, checkpoint, Catalogue or Lineage commits from Test.

## Current table ownership and scope

The historical `docs/releases/manifests/0.2.5.yml` lists six Live, six Preview and six discontinued tables. Its names differ from the current canonical registry: Enrichment and Guardrail tables were retired, and Source Observation was replaced by Processing State. Registry, Activation State and Pipeline Run are absent from that manifest. Use Preview breaking-change rules for their proposed redesign, while preserving required history and reservations. Update lifecycle declarations in a future release; do not rewrite the historical manifest.

The ownership column below describes current physical routing. Joint Engineering/Governance responsibility and any replacement routing must be specified by the new design.

| Canonical table | Current physical owner | v0.2.5 classification | Current scope |
| --- | --- | --- | --- |
| `METADATA_DATA_STEWARD` | governance | Live | Keep schema and steward grain |
| `METADATA_DATA_AGREEMENT` | governance | Live | Keep schema and versioned agreement grain |
| `METADATA_DATA_CONTRACT` | governance | Preview | Keep global version identity and immutable Frozen content; audit reference integrity for the joint model |
| `METADATA_ACTIVATION_STATE` | governance | Not listed | Existing atomic authority; propose absorbing its responsibilities into versioned Pipeline Registry only after transaction proof |
| `METADATA_DATA_CATALOGUE` | engineering | Live | Keep existing `metadata_level` table/column discriminator |
| `METADATA_DATA_PROFILED` | engineering | Live | Keep one observed column per profile snapshot |
| `METADATA_DATA_PROFILED_FREQUENCY` | engineering | Live | Keep one frequency value per column snapshot; profile-to-frequency is one-to-many |
| `METADATA_DATA_LINEAGE` | engineering | Live | Audit overlap with declared and observed participation; preserve existing rows and consumers unless a tested supported Live migration is approved |
| `METADATA_DATA_ACCESS` | engineering | Preview | Keep observed-grant grain; distinguish observed access from computed effective access |
| `METADATA_PIPELINE_REGISTRY` | engineering | Not listed | Proposed versioned pipeline hub with field-level Engineering/Governance responsibility; physical ownership remains a design decision |
| `METADATA_PIPELINE_RUN` | engineering | Not listed | Merged #1700 is the baseline; jointly redesign configuration references and execution facts while preserving whole-run finalization |
| `METADATA_GUARDRAIL_RESULTS` | engineering | Preview | Keep per-rule aggregate result grain and exact finalized Test/run/contract links |
| `METADATA_PROCESSING_STATE` | engineering | Not listed; replaces Preview Source Observation | Already implemented by #1698; preserve physical schema, accepted progress and publication recovery |

## Relational design rules

1. **Stable identities:** use `table_id`, `contract_id + contract_version`, `pipeline_id + environment_name`, `run_id`, and immutable approved-version identifiers. Document composite keys where a record has multiple dimensions.
2. **Actual grains:** a catalogue column, a frequency value, a Guardrail result, a pipeline operation, and a publication receipt are different facts. Do not collapse them into one generic JSON blob.
3. **Explicit parent links:** run operations reference `run_id`; approval participants reference the exact approved version and `table_id`; Guardrail results reference run and contract version. Enforce integrity in application code because Delta tables do not provide ordinary relational foreign-key enforcement.
4. **Typed records, not a universal table:** use `record_type` for closely related rows; require type-specific validation and explicit uniqueness rules. Avoid dozens of unrelated nullable fields.
5. **JSON boundary:** retain authored expressions, extensible contract settings, and variable diagnostics in JSON. Extract stable IDs, statuses, timestamps, counters, approval participants, and checkpoints where querying or integrity requires it.
6. **Historical correctness:** a frozen contract, approved pipeline version, or completed run must not be retroactively rewritten by subsequent edits.
7. **Transaction boundaries first:** physical normalization is subordinate to atomic activation and successful-write checkpoint semantics.

## Current implementation and preserved guarantees

### Processing state (engineering)

`engineering.METADATA_PROCESSING_STATE` replaces Preview `METADATA_SOURCE_OBSERVATION` as the canonical Processing State table. Its four record types separate captured source state from accepted progress and physical publication evidence. The six Live schemas and the existing governance/engineering ownership routing are unchanged.

| Record type | Grain and lifecycle |
| --- | --- |
| `source_observation` | One captured source snapshot partition (or explicit empty-source row), `status=observed`; no target or publication link and never read as accepted progress |
| `incremental_checkpoint` | One source/target/environment observation partition bound to a publication, `staged` → `committed` after verification |
| `drift_baseline` | One source/target/environment observation partition or removal tombstone, `staged` → `committed` after verification and a continuing Guardrail decision |
| `publication_receipt` | One exact target/environment publication attempt, including source-free writes, `staged` → `committed` with all source members |

The canonical [Processing State physical reference](../reference/metadata/metadata_processing_state.md) is generated from `metadata_schemas.py`. Its schema and recovery protocol are outside the joint redesign. Preserve these guarantees:

1. Read observations alone never advance accepted checkpoints or Source Drift baselines. Stage one exact publication receipt and all source members atomically before target mutation; accept them together only after physical publication is verified.
2. Lakehouse recovery requires the exact Delta receipt and applicable target markers. Warehouse append/overwrite requires the full prepared row count with exact activity/time markers; partial or unprovable empty publication blocks recovery. Warehouse SCD retains its existing SQL transaction and latest-publication checks. One target's writers remain serialized.
3. Lost acknowledgements and retries recover the original persisted member set, run identities and publication, including across process restarts. They never accept a newer Read snapshot or replay a completed append. Keep target evidence and required Delta history.
4. Preserve lossless bounds/types, UTC versus wall-time timestamps, SQL NULL versus empty-string partitions, empty-source headers and removal tombstones. Repeated staging cannot regress committed progress.
5. Catalogue and Lineage finalization are separate commits. Recovery of Processing State does not imply those commits succeeded; retry their exact publication finalization when needed. There is no cross-table transaction or independent-concurrent-Warehouse exactly-once claim.

Primary integration points are `capture_source_observation`, `resolve_incremental_source_scope`, `check_source_drift_for_target`, `PublicationBatch`, `stage_pipeline_write_observations`, `commit_pipeline_write_success` and `_recover_completed_source_observations`. Audit their links to pipeline/run identity and writer admission without redesigning their persistence.

### Processing State upgrade

This existing cutover procedure applies only to deployments still using the pre-#1698 layout: `METADATA_SOURCE_OBSERVATION` → `METADATA_PROCESSING_STATE`. There is no legacy alias or fallback reader. Setup permits the old physical table to remain, including alongside the canonical table, and returns an advisory retirement alert. A fresh canonical table does not establish valid operational progress for populated targets. `observation_status` and `publication_payload_json` are removed. Old rows must **not** be additive-evolved into typed progress. Setup and runtime still reject an incompatible layout under the canonical `METADATA_PROCESSING_STATE` name, including an empty table. No compatibility reader, automatic migration, reset, or discard is performed.

1. Stop/drain writers and take a durable backup of the existing `METADATA_SOURCE_OBSERVATION` table plus the code/version needed to read it. Retain target data, target audit markers, and Delta history. Inventory all source/target/environment relationships, accepted progress and unresolved publications.
2. Reconcile every staged publication against the physical target before cutover. In the old layout, `committed` corresponds to `incremental_checkpoint`; `drift_committed` to `drift_baseline`; `publication_observed`/`publication_committed` to staged/committed receipts. Old target-bound `observed`/`drift_observed` rows are staged candidates, never automatically accepted checkpoints. Decode and deduplicate exact receipt JSON into typed receipt rows; retain originating run/audit identities. Column/type evidence missing from old records must be supplied from the verified original processing definition, not inferred silently from current configuration.
3. Choose an explicit, reviewed cutover: an offline migration into the complete canonical schema with deterministic IDs and validated receipt references; or a reset only after reconciling/archiving progress and preparing a governed target rebuild or idempotent replay. A populated append target without an accepted baseline is intentionally rejected. Dropping only the metadata table and continuing incremental append is unsafe.
4. For a deliberate reset, preserve a durable archive of the reconciled old Preview table, run `setup_metadata_tables()` to create `METADATA_PROCESSING_STATE`, then execute the reviewed target rebuild/replay. This Processing State cutover does not replace or reset Live metadata, Pipeline Run, Registry or Activation State; use the separate joint-redesign procedure for any approved pipeline metadata replacement. For migration, populate `METADATA_PROCESSING_STATE` with the validated complete schema, then archive/remove the old physical name and run setup validation before restarting writers. A physical rename alone is valid only after verifying the complete new schema, record-key uniqueness, receipt references and empty-header semantics. Older empty-source sentinels must be reconciled against real NULL/empty-string partitions before transformation; do not infer whether they represent a removed partition or a dataset header. Older layouts require the field transformation above. Both physical names may remain during reconciliation; the retired name produces an advisory alert and is never read by runtime.
5. Validate first/subsequent incremental execution, unchanged/empty reads, Source Drift baseline decisions, lost-acknowledgement retries and environment/target isolation. Keep the backup until these checks finish. Rollback requires stopping writers and restoring both a compatible code/schema pair and a reconciled checkpoint/target boundary; restoring metadata alone after new publications is unsafe.

The current exact receipt includes its physical strategy. Old Delta commit metadata cannot be rewritten into new physical proof: retain old receipts for reconciliation, and use a reviewed target rebuild/replay to establish new-format receipts wherever automatic retry verification is needed. Migrating accepted progress alone does not retrofit old physical receipts. Recovery restores Processing State; replay the exact prepared Write if separate Catalogue or Lineage finalization also needs retry.

No automatic conversion is supplied because old rows can lack watermark types, column identities or exact physical publication proof. Operators decide archival retention after reconciliation. Existing Processing State tests are regression requirements for the joint redesign; their local results do not validate an actual Fabric Warehouse deployment.

### Pipeline execution (engineering)

Merged [#1700](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1700) is the current baseline. `METADATA_PIPELINE_RUN` has one row per execution with typed `operations`/stages, `boundary_completed`, candidate identity/content and `run_details_json`. See its generated [physical reference](../reference/metadata/metadata_pipeline_run.md); these fields are being reconsidered together in the [field disposition](#current-field-disposition-to-verify), rather than frozen as the replacement schema.

Preserve the behavioral guarantees while changing where configuration lives:

- Publish each run outcome and its complete observed operation/stage set atomically. Unique first publication, full-previous-row CAS, terminal immutability and exact read-back after lost acknowledgement prevent duplicate or stale run updates.
- Independent runs may proceed concurrently; retry only established aborted metadata transactions. Do not replay business publication, regress a failed run to success or introduce per-update DDL.
- Require explicit whole-run finalization, exact participant/contract/configuration coverage, valid stages and matching required Guardrail Results. A successful Write or cell event cannot establish a successful whole Test. Interrupted Live remains incomplete; unfinished Test cannot authorize approval.
- Keep supported notebook result shapes through domain reconstruction. Audit `pipeline_run_row`, `pipeline_run_result`, `persist_pipeline_run`, `publish_pipeline_testing_results`, `finalize_pipeline_run`, activation readers and `profiling_completion_history` together.

#### Earlier Pipeline Run layout conversion

`scripts/migrate_pipeline_runs.py`, already on main, converts only the older `operation_summary_json` layout into the current #1700 schema. It requires a stopped deployment, pinned source Delta version, matching package and a separate unused destination. It validates complete logical reconstruction and refuses ambiguous identities or invented successful outcomes. It does not convert #1704 or the proposed joint model.

For an operator deliberately upgrading only to the #1700 baseline, the [version-pinned conversion and rollout procedure](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5c80587930ea127e22b0dc739406c9c74a393c23/docs/maintainer/metadata-v2-target-model.md#offline-conversion-and-rollout) retains the exact command, validation and rollback steps. For the replacement model, use the [joint rollout policy](#joint-redesign-rollout-and-reset-policy); do not extend that converter merely to preserve disposable Preview history.

### Activation authority (governance)

On main, the central `snapshot_json` and `token` are committed using Serializable Delta compare-and-swap, protecting immutable approvals, complete participants, writer ownership, activation revisions, Live reservations, notebook/workspace rebind barriers and profiling claims. The eight-record physical normalization in closed #1704 is withdrawn as the target. Its successful local tests are prior design evidence, not validation of a replacement.

**Required invariants remain:** approval publication is atomic; incomplete or stale revisions never become executable; Live runs pin the correct approved revision; writer ownership and rebind barriers are enforced; stale CAS conflicts fail closed; lost acknowledgement is recoverable. Multiple independent Delta writes are not an atomic replacement for the existing singleton. Do not remove this authority until the joint model has passed the publication proof below.

## Joint pipeline metadata redesign

**Proposed outcome:** make `METADATA_PIPELINE_REGISTRY` the versioned connector for available pipelines, declared Read/Write participants, orchestration configuration and exact contract/Agreement approval references. Absorb Activation State responsibilities into that authority if the transaction proof succeeds. Keep `METADATA_PIPELINE_RUN` as execution history referencing the exact definition it ran. Decide the physical layout after the lifecycle and ownership audit; do not start by assigning one column to every old nested field.

### Logical grains and responsibility

These are logical facts, not a commitment to one physical table per row in this matrix. Proposed version-reference names below are illustrative, not new public terms or approved schema columns.

| Fact | Grain / identity | Responsible writer and lifecycle |
| --- | --- | --- |
| Pipeline registration | Stable `pipeline_id`, with binding per environment | Engineering registers, retires and rebinds; registration alone never permits Live |
| Immutable pipeline definition | Pipeline + exact definition version, bound to the tested environment configuration | Engineering captures project/operation configuration, logical participants, roles, physical bindings and exact frozen contract references; sealed content cannot change |
| Declared participant | Definition version + logical participant + role | Engineering declares `table_id` and source/target role; contract identity resolves through Data Contract, not a second contract lifecycle in Registry |
| Governance decision | Exact definition version + successful finalized Test + exact Agreement version | Governance approves; preserve independent decision history if repeated decisions are meaningful rather than inventing another pipeline identity |
| Current Live selection | Pipeline + environment | Governance selects an approved version in a coordinated environment revision; affected pipelines and table ownership change together |
| Reservation / barrier / profiling claim | Exact owner and existing domain scope | Execution or maintenance acquires, renews where supported, completes and releases; recovery cannot silently remove another owner's claim |
| Execution | `run_id`, referencing stable pipeline and exact definition/approval | Runtime records actual operation/stage outcomes, timing, finalization and safe failure/profiling diagnostics |
| Observed participation | Actual publication/activity + table + role, with existing environment scope | Successful physical publication records what participated; a later run failure does not erase publication history |

Engineering and Governance ownership describe who may change a fact. A consolidated Registry has one configured physical schema home in the existing two-schema model, one canonical writer path per mutation and explicit Governance confirmation for approval. Select and document the physical home and permissions before implementation; do not create duplicate authorities under both schemas.

`METADATA_DATA_CONTRACT` remains the owner of `table_id` → `contract_id + contract_version` and immutable authored content. Its lifecycle is global per table, with environment provenance. The joint authority must enforce **one active frozen contract version and physical binding per table in each environment across all active pipelines**, while retaining draft and historical versions. Each target still has at most one owning writer. `METADATA_DATA_AGREEMENT` remains the owner of Agreement versions; Registry references them rather than copying their authored document by default. Processing State retains its checkpoint, baseline and physical publication-recovery responsibilities unchanged.

### Definition, Test, approval and Live lifecycle

1. `setup_pipeline` resolves permanent identity and binding. Test continues discovering configuration and participants through the existing notebook calls; do not require a new authoring UI or a predeclared immutable definition before those calls exist.
2. Read, Transform and Write execute under one in-memory Test plan. No durable approvable definition or successful run is inferred from an isolated operation or notebook cell event.
3. Explicit `finalize_pipeline` validates complete participant/operation/stage coverage and seals the exact tested definition. Persist the immutable definition and required Guardrail results before marking its Test run successfully finalized. Separate-table intermediate records are non-authorizing; orphaned definitions/results cannot grant approval. Specify failure and lost-acknowledgement handling for each step before coding.
4. Governance revalidates the finalized run, current notebook/workspace binding, exact frozen contracts, required Guardrail results and currently effective Agreement. Publish the decision, complete references, current selections, ownership and affected environment revision in one guarded authority transaction. Preserve the current combined approval/activation workflow and widget behavior.
5. Live atomically checks that authority and acquires its reservation against the exact selected version and revision. Runtime resolves immutable configuration/contracts by reference and rejects changed notebook arguments or bindings. Later approvals cannot alter an already pinned execution.
6. Completion, interruption, reservation release, rebind and profiling recovery retain their existing fail-closed semantics. A run row alone does not prove that a reservation may be released or a business publication may be replayed.

Before replacing embedded documents with references, prove that referenced versions are unique, immutable, retained and hash-verifiable for the entire approval/run lifetime. Audit every writer, including foundational metadata writes. Missing or altered references must block execution with actionable reconciliation guidance; never fall back to the current/latest version. If an existing reference cannot provide historical content, document the minimum retained representation and its reason instead of claiming that IDs alone preserve history.

### Current field disposition to verify

| Current field / content | Proposed disposition and reason |
| --- | --- |
| Run `pipeline_id` | Retain the stable logical pipeline reference; document whether any repeated parent identity is necessary for querying or integrity |
| Run `activated_pipeline_id` | Replace the ambiguous internal name with an exact approved-version reference in the joint design; it is not a second pipeline identity. Preserve supported notebook result shapes through the domain reader |
| Run `candidate_json` | Move canonical reusable configuration into the immutable definition; Run references it rather than copying a full candidate |
| Run `candidate_fingerprint` | Place content-integrity hashing with the immutable definition; retain a run-side copy only if a concrete integrity requirement justifies it |
| Run `operations` | Keep actual operation/stage status and timing as typed execution facts; move expected configuration and participant/contract declarations to the definition and validate actual membership against it |
| Run `boundary_completed` | Preserve its whole-notebook finalization guarantee. Choose either the explicit marker or an equally strict typed finalization lifecycle; operation success alone is insufficient |
| Run `run_details_json` | Extract stable revisions, references, bindings and profiling state into their owning facts; retain only variable sanitized diagnostics justified field by field |
| Activation `snapshot_json` | Replace only after all approvals, participants, selections, ownership, reservations, barriers and profiling claims have an identified owner and proven transaction protocol |
| Registry `registry_token` and Activation `token` | Replace competing serialization domains with the minimum authority/CAS scheme that protects registration, rebind, cutover and admission together; a business identifier is not a concurrency token |
| Authored contract / Agreement payloads | Keep in their existing owner tables with exact version/hash references; do not duplicate into every approval and run |
| Project and operation configuration | Store once per immutable definition. JSON is acceptable for variable settings/expressions; stable IDs, roles, status, versions and relationships remain typed |
| Warnings and errors | Use native arrays/fields for stable shapes; JSON only for variable diagnostics, with no hidden approval or reservation authority |

Every proposed column must identify its owning fact, reader/writer, query or enforcement purpose, nullability and derivation. Every remaining JSON field must list allowed content and explain why it is variable. Do not persist the same operational document under a new name.

### Lineage decision

Declared participants belong to the definition and can supply planned participation queries. Actual `METADATA_DATA_LINEAGE` rows currently record source/target participation after successful Live target publication; they are keyed by Fabric activity/table/role with environment matching, not by framework `run_id`. They do not prove individual source-to-target transformation edges. Publication can succeed before profiling or final run completion fails, so deriving observed history only from successful runs would lose facts.

Audit all package readers, widgets, references and externally consumed queries. Prefer deriving new declared participation from the Registry and preserving the existing Live observed-participation table unless a complete absorption provides a demonstrated benefit. If absorption is selected, include a concrete automatic migration preserving all existing rows and identities, repeat-safe validation, consumer updates and a rollback boundary in the same implementation. Do not infer run mappings that old activity-level history cannot establish. Keeping the Live table is an explicit supported decision, not a second source of pipeline configuration.

### Transaction design and proof before persistence changes

The starting candidate is **one Registry authority publication** for approval/admission/rebind decisions with exact immutable definition references. A shared serialization point protects cross-pipeline contract and writer constraints. Run updates have their own per-run concurrency control; they do not republish the whole Registry. Select the smallest native-row/struct layout that supports these grains without a universal metadata table or the eight-payload layout from #1704 by default.

Before changing persistence, record the exact Delta statements, transaction boundaries, CAS predicate, insert/delete behavior, retention constraints and reader validation. Prove approval and its complete participant set become authoritative in one transaction: either store them together in that publication, or reference a previously sealed immutable complete definition whose publication/retention protocol cannot expose a partial version. If children insert in the authority MERGE, a stale guard must roll back unmatched inserts as well as updates/deletes. Prechecking a token outside MERGE is insufficient.

Use persisted Delta tests for simultaneous publishers, stale tokens, transaction rollback, unmatched inserts, missing/duplicate/altered references, complete participants, immutable approvals, exact content read-back after lost acknowledgement and idempotent retry. Race activation against Live acquisition, writer changes, rebind and profiling claims. Prove unrelated mutations preserve existing history/reservations and environments/pipelines remain isolated. Do not claim cross-table transactions for definitions, Run, Guardrail Results, Lineage or business data; document which partially published states are harmless and why readers fail closed.

If a simple consolidated physical design cannot prove these properties, keep the current authority in service and revise this plan before implementation. Do not ship a second writable authority or query projections as a completed consolidation.

## Deployment and migration contract

Before a structural implementation PR, document for **every changed table**: old and new fields with Spark types/nullability, logical key, `record_type` values, all readers and writers, transformation mapping, retained records, discard policy, cutover preconditions, rollback boundary, and test coverage.

- Existing Live tables must remain readable without a rebuild.
- Preview breaking changes do not need compatibility shims, but deployed state must be classified as safely migratable or explicitly resettable.
- Never reset incremental checkpoints, publication receipts, active reservations, or approval history casually. Drain in-flight Live runs before a breaking cutover.
- `setup_metadata_tables()` should fail clearly on incompatible physical schemas; no silent data loss or accidental schema evolution.
- A PR must not merge if it leaves `main` with incompatible metadata readers/writers.
- Retain existing two-schema routing; no new metadata schema or storage service.

### Joint redesign rollout and reset policy

This procedure governs the proposed joint replacement. The existing Processing State cutover and earlier Run converter have distinct source/target layouts; neither migrates to this model. Do not add a standalone Preview converter merely to preserve disposable history.

1. **Inventory the deployed layout.** Record package versions and physical schemas for Registry, Activation State, Run and any affected participation table. Include exact reference counts, immutable approvals and finalized Tests, active/interrupted reservations, rebind barriers and profiling claims. Closed #1704 was not merged; an independently deployed copy requires separate reconciliation rather than assumed support.
2. **Stop and drain.** Disable schedulers and new Test/Live starts, registration/rebind and profiling acquisition. Let existing work finish and reconcile interrupted work against actual publication evidence. Never clear a reservation merely to make replacement possible. Back up all affected Delta tables at pinned versions, their referenced contracts/Agreements/results, and the matching reader package. Preserve Processing State and business-target recovery evidence.
3. **Fresh setup.** Create only the final canonical model with strict schema validation; then register, finalize a complete Test, explicitly approve and select Live. Registration, an empty Registry or an orphaned definition cannot authorize execution.
4. **Disposable Preview state.** If operators explicitly choose to discard state and establish that no approval history, run history or outstanding claims must be retained, archive it and deliberately recreate only the affected Preview tables. Re-register pipelines with a documented identity choice, rerun Test and reapprove. Do not erase Live metadata or reset Processing State/checkpoints/publication receipts. Setup never drops tables, deletes approvals, releases reservations or recreates incompatible canonical tables automatically.
5. **Retained Preview state.** Where approvals/history/claims matter, preserve the old stopped deployment until an explicit reviewed reconciliation maps every retained identity and content hash into the complete new model. Validate counts, exact contract/Agreement/Test links, whole-run outcomes, decision history, participants, ownership and claim ownership before cutover. Do not invent missing historical content, infer success or automatically transfer unverified active work. If correctness cannot be established, retain the old deployment/archive and resolve it before enabling Live; a disposable reset is not a substitute for preservation.
6. **Supported Live participation.** If the implementation changes or absorbs `METADATA_DATA_LINEAGE`, its migration must preserve existing rows automatically, validate repeat execution without duplicates or loss, and define cutover and rollback explicitly. No drop/rebuild instruction is acceptable for this Live table. If it stays unchanged, assert its schema and rows remain unchanged and document its observed-participation role.
7. **Physical cutover and validation.** Replace only validated affected layouts at their actual configured Lakehouse paths while stopped; catalogue registration alone is insufficient for path-based readers. Switch all affected readers/writers together. Setup rejects incompatible canonical schemas with a clear repair action. Differently named retired Preview tables may remain unused without blocking setup; use the retirement registry for actionable archival/cleanup notices. Never automatically delete them.
8. **Rollback.** Before new writes, restore the backed-up affected metadata and matching package as a unit. After new runs, approvals, claims or business publications, stop and reconcile the new records and recovery boundaries before rollback. An old metadata snapshot alone can erase history or authorize unsafe replay. Keep backups until deployment validation and the agreed retention boundary complete.

Select and document the physical model before implementing any required conversion code; this planning change supplies none.

## Completed foundations and remaining work

| Foundation | Current status | Consequence for this plan |
| --- | --- | --- |
| Metadata audit and reference fixes (#1695, #1696) | Merged | Recheck changed facts against authoritative source; no broad reference cleanup workstream |
| Finalized Test results (#1697) | Merged | Preserve complete Test/Guardrail prerequisites for approval |
| Processing State (#1698) | Merged | Integration and recovery regression coverage; no new schema redesign |
| Pipeline Run (#1700) and Registry audit timestamp (#1702) | Merged | Current baselines to audit jointly; no duplication of their implementation |
| Activation-only normalization (#1704) | Closed unmerged | Withdrawn physical target; do not cherry-pick its implementation |

The remaining work is one joint pipeline metadata implementation: inventory and lifecycle design, physical-schema/transaction proof, all-consumer changes, table-specific rollout instructions, focused validation and affected generation. The [fresh-session sequence](#fresh-session-implementation-sequence) defines its order. Contract/Guardrail/Access normalization is outside the planned replacement; change those owners only where required for verified references or affected consumers. A merged foundation does not establish that actual Microsoft Fabric deployment validation has completed.

## Acceptance tests

- Fresh setup and incompatible existing schema detection.
- Day 1/Day 2 incremental reads, no-change reruns, drift, failed write, lost acknowledgement, and idempotent publication recovery.
- Live versus Test persistence, interrupted run, failed operation, repeated finalization, and authoritative run status.
- Concurrent activation, stale revision, approval immutability, reservation release, rebind barriers, and lost CAS acknowledgement using persisted Delta where transaction semantics matter.
- Definition sealing, orphaned intermediate records, complete finalized Test → approval → Live, exact immutable reference resolution, conflicting active contracts per table/environment, and unchanged supported notebook signatures/result shapes.
- Reservation acquisition, supported renewal, owner-specific release and interrupted execution; profiling claims/completion recovery; activation/admission/rebind races without losing unrelated history.
- Declared versus observed participation, including successful target publication followed by run failure. If Live Lineage changes, automatic migration preserves rows and passes repeat-safety/rollback validation.
- Live table schema fingerprints unchanged unless separately approved.
- No extra metadata schemas, compatibility wrappers, or unrelated generated refreshes.
- All relevant generators run from their authoritative source; generated reference pages are not manually edited, and a second generation run is clean.

## Fresh-session implementation sequence

The current change is planning/documentation only. Start replacement implementation in a fresh Codex session after plan review; this planning branch is the handoff, not an implementation PR.

1. Fetch latest `main` into a new branch/check-out. Read `AGENTS.md`, relevant skills, this plan, canonical schemas, glossary and the affected public call-flow slices. Confirm #1700 remains merged and #1704 remains closed. Bring forward this documentation change if it has not merged; do not bring forward #1704's implementation.
2. Produce the complete reader/writer and field inventory across Registry, Activation State, Run, Guardrail Results, Data Contract, Data Agreement, Lineage, profiling claims and Processing State integration. Include widget and notebook result consumers, CAS and lost-acknowledgement paths.
3. Settle immutable-definition sealing, approval identity, physical Registry home, typed participant storage and observed Lineage retention/absorption. Compare the simplest viable physical layouts and justify every identifier, column and remaining JSON field. Document exact schemas and the single-transaction authority protocol before replacing persistence.
4. Prove that protocol with persisted Delta tests, then update every affected consumer together. Preserve setup → Read → Transform → Write → finalize, Test/Live behavior, activation widget, exact contract/binding checks, finalized whole-run proof, Processing State and public result shapes. Remove displaced private implementations; do not keep parallel legacy readers or dual writers.
5. Complete the table-specific upgrade/reconciliation instructions above and any approved supported Live migration. Update `AGENTS.md` responsibilities and directly affected glossary/docs from their authoritative owners to match the final implementation.
6. Run relevant lint, focused lifecycle/public-contract tests, persisted Delta concurrency/recovery tests, compile/import checks and strict MkDocs. Generate only directly affected references, call-flow JSON and metadata diagrams from source; run affected generators twice and confirm a clean second pass. Exclude timestamp-only, dashboard, release, notebook and unrelated static output changes. Compare all six Live schemas and Processing State with latest main; any approved Lineage exception must have its preservation tests.
7. Review the complete diff for unnecessary abstractions, duplicated authority/configuration, migration machinery and unrelated changes. Open **one fresh implementation PR** targeting latest main, recording the final physical schema/JSON, transaction evidence, breaking Preview instructions, validation results and remaining runtime limits. Do not merge.

Local persisted Spark/Delta validation is required and does not prove actual Microsoft Fabric behavior. Record separate deployment checks for Fabric Lakehouse concurrency/cutover, notebook permissions and Warehouse transport. Prior #1704 test results must not be presented as successful validation of a new implementation.

## Retirement declarations and Live upgrade policy

`RETIRED_PREVIEW_METADATA_TABLES` in `src/fabricops_kit/config/metadata_schemas.py` is the authoritative retirement registry: declare the retirement version and intentional current-model guidance when removing a released Preview table. The inventory consistency test compares historical release manifests and the current canonical registry; it excludes supported Live tables. Setup probes only these names in both configured Governance and Engineering schemas through the configured Metadata Lakehouse, without collecting historical rows. Missing tables produce no alert; access/storage failures produce advisory diagnostics. Cleanup requires preserving required definitions, progress or history before deleting a table or explicitly mapping/migrating retained records. Similar names do not establish a safe conversion, and old rows must not be blindly appended to current models. Setup does not migrate or delete Preview data.

`AGENTS.md` defines the supported Live upgrade policy. Keep all six Live schemas unchanged by default. If Lineage absorption requires an approved Live removal, rename or type change, include an explicit automatic migration that preserves rows, validates results, supports safe repeated execution and defines a rollback boundary. Users must not be asked to drop/rebuild supported Live tables or guess conversions. The current planning change modifies no physical schema; it does not prejudge that implementation decision.
