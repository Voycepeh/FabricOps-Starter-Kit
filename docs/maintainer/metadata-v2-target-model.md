# Metadata v2: target model and migration boundaries

**Status:** proposed architecture; no schema or runtime change in this document.

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
| `METADATA_SOURCE_OBSERVATION` | engineering | Preview | Consider `METADATA_PROCESSING_STATE` with typed observation/checkpoint/baseline/publication records |

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

Investigate renaming Preview `METADATA_SOURCE_OBSERVATION` to `METADATA_PROCESSING_STATE`. Proposed record types are `source_observation`, `incremental_checkpoint`, `drift_baseline`, and `publication_receipt`. Preserve source/target/environment/partition identities, `run_id`, source fingerprint, observed and committed status, and publication recovery identifiers as typed fields where stable.

**Required invariants:** observation is not commitment; no failed write advances a watermark; successful writes with lost acknowledgement can be recovered; retry does not duplicate published data; a target's accepted checkpoint has one authoritative source. Validate Warehouse publication receipts separately from Lakehouse incremental commits. Choose final keys and columns only after tracing actual writers and readers.

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
