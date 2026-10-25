# Metadata v2: target model and migration boundaries

**Status:** Processing State implemented; Pipeline Run and Activation State directions remain proposals.

## Goal and constraints

Treat FabricOps metadata as an operational application database, not a reporting star schema. Prefer queryable typed records and explicit relationships over large nested state documents, but do not normalize flexible configuration for its own sake.

- Keep **one metadata Lakehouse** and exactly the two existing logical ownership schemas: `governance` and `engineering`. Respect configured physical schema names.
- Retain the six published Live metadata contracts unchanged unless a separate decision demonstrates a substantial long-term benefit.
- Preview contracts may change without deprecated aliases, dual writes, or transitional API wrappers. Operational checkpoints, frozen contracts, and approval history still need a deliberate migration or safe cutover.
- Do not introduce Azure SQL, extra metadata schemas, or a separate control-plane database.
- Do not require the physical table count to decrease. A `record_type` discriminator is appropriate only when row types have compatible identity, lifecycle, and transaction semantics.
- Preserve public notebook workflows and the distinction between in-memory Test results and persisted Live results.

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
| `METADATA_PIPELINE_RUN` | engineering | Not listed | Evaluate typed `run` and `operation` rows instead of opaque operation summaries |
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

Investigate typed `run` and `operation` records within `METADATA_PIPELINE_RUN`. The parent `run` row is the sole authoritative final outcome; operation rows carry stable operation identity, type, participating table, status, and timing. Keep variable diagnostics in JSON only where justified.

**Required invariants:** interrupted notebooks cannot be finalized as successful; Test does not unexpectedly persist Live run evidence; retries and repeated finalization are idempotent; a successful operation does not imply a successful run. Prove whether a shared table actually simplifies persistence before committing to this shape.

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

| Workstream | Executor | Dependencies | Merge boundary |
| --- | --- | --- | --- |
| A. Architecture and lifecycle audit (this document) | ChatGPT | latest main | Documentation only |
| B. Focused metadata reference fixes | ChatGPT | A | Small generator/source or docs PR; no schema change |
| C. Processing State redesign | Codex | A; writer/reader inventory | Self-contained backend PR, targeted Delta recovery tests |
| D. Pipeline Run normalization | Codex | A; run/finalization inventory | Separate backend PR, targeted persistence tests |
| E. Activation authority redesign | Codex | A; concurrency design proof | Isolated PR with persisted Delta CAS/conflict tests |
| F. Contract/Guardrail/Access cleanup | ChatGPT for bounded fixes, otherwise Codex | A; demonstrated benefit | Skip if no justified change |
| G. Final integration/reference generation | Appropriate owner of affected source | C–F | Only directly affected artifacts |

C and D may be developed in parallel on separate branches **only** if shared `metadata_schemas.py`, setup logic, and reference generation are coordinated. Prefer a tiny shared foundation PR or a sequential merge/rebase to competing edits. Keep E isolated.

## Acceptance tests

- Fresh setup and incompatible existing schema detection.
- Day 1/Day 2 incremental reads, no-change reruns, drift, failed write, lost acknowledgement, and idempotent publication recovery.
- Live versus Test persistence, interrupted run, failed operation, repeated finalization, and authoritative run status.
- Concurrent activation, stale revision, approval immutability, reservation release, rebind barriers, and lost CAS acknowledgement using persisted Delta where transaction semantics matter.
- Live table schema fingerprints unchanged unless separately approved.
- No extra metadata schemas, compatibility wrappers, or unrelated generated refreshes.
- All relevant generators run from their authoritative source; generated reference pages are not manually edited, and a second generation run is clean.

## Decisions intentionally deferred to implementation audit

The proposed new names, columns, and record types are **candidates**, not approved physical contracts. Before implementation, Codex must produce the exact field-by-field schema and prove that each change reduces complexity without compromising correctness. In particular, do not assume that a single Delta table of typed activation rows is atomic across multiple independent commits.
