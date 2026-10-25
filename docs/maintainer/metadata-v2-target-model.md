# Metadata v2: target model and migration boundaries

**Status (2026-10-25):** Processing State [#1698](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1698) and Pipeline Run [#1700](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1700) are merged. Activation-only [#1704](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1704) is closed without merging and superseded by the [joint pipeline metadata redesign](#joint-pipeline-metadata-redesign). Plan Registry, Activation State, Pipeline Run and participation together before starting one fresh implementation PR. This document proposes the replacement; it does not describe an implemented replacement schema or prove its transaction design.

## Goal and constraints

Treat FabricOps metadata as an operational application database, not a reporting star schema. Prefer queryable typed records and explicit relationships over large nested state documents, but do not normalize flexible configuration for its own sake.

- Keep **one metadata Lakehouse** and exactly the two existing logical ownership schemas: `governance` and `engineering`. Respect configured physical schema names.
- Retain the six published Live metadata contracts unchanged unless a separate decision demonstrates a substantial long-term benefit.
- Preview contracts may change without deprecated aliases, dual writes, or transitional API wrappers. Operational checkpoints, frozen contracts, and approval history still need a deliberate migration or safe cutover.
- Do not introduce Azure SQL, extra metadata schemas, or a separate control-plane database.
- Do not require the physical table count to decrease. A `record_type` discriminator is appropriate only when row types have compatible identity, lifecycle, and transaction semantics.
- Preserve public notebook workflows: Test operations stay in memory; explicit finalization persists the allowed Test run and Guardrail diagnostics for activation, as implemented by #1697. The proposed joint design may additionally seal its immutable tested definition at finalization; it must not enable business, checkpoint, Catalogue or Lineage commits from Test.

## Release classification versus current canonical registry

The published `docs/releases/manifests/0.2.5.yml` classifies six tables as Live and four as Preview. Three newer canonical tables are absent from that release manifest. **Absence is not permission to discard their persisted state.** Reconcile their lifecycle classification in the appropriate future release manifest rather than rewriting the historical v0.2.5 manifest.

| Canonical table | Owner | Published lifecycle | v2 direction |
| --- | --- | --- | --- |
| `METADATA_DATA_STEWARD` | governance | Live | Keep schema and steward grain |
| `METADATA_DATA_AGREEMENT` | governance | Live | Keep schema and versioned agreement grain |
| `METADATA_DATA_CONTRACT` | governance | Preview | Keep version identity and immutable Frozen contracts; retain flexible rule payload unless independently queryable records are justified |
| `METADATA_ACTIVATION_STATE` | governance | Not listed | Existing atomic authority; propose absorbing its responsibilities into versioned Pipeline Registry only after transaction proof |
| `METADATA_DATA_CATALOGUE` | engineering | Live | Keep existing `metadata_level` table/column discriminator |
| `METADATA_DATA_PROFILED` | engineering | Live | Keep one observed column per profile snapshot |
| `METADATA_DATA_PROFILED_FREQUENCY` | engineering | Live | Keep one frequency value per column snapshot; profile-to-frequency is one-to-many |
| `METADATA_DATA_LINEAGE` | engineering | Live | Audit overlap with declared and observed participation; preserve existing rows and consumers unless a tested supported Live migration is approved |
| `METADATA_DATA_ACCESS` | engineering | Preview | Keep observed-grant grain; distinguish observed access from computed effective access |
| `METADATA_PIPELINE_REGISTRY` | engineering | Not listed | Proposed versioned pipeline hub with field-level Engineering/Governance responsibility; physical ownership remains a design decision |
| `METADATA_PIPELINE_RUN` | engineering | Not listed | Merged #1700 is the baseline; jointly redesign configuration references and execution facts while preserving whole-run finalization |
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

`engineering.METADATA_PIPELINE_RUN` currently retains **one authoritative row per run**. Merged [#1700](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1700) replaced broad operational JSON with a native typed `operations` array and typed nested stages, using merged #1697 and #1698 as its baseline. The following sections document that implemented baseline and its existing converter, not the future joint redesign. The earlier multirow proposal was superseded.

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

On main, the central `snapshot_json` and `token` are committed using Serializable Delta compare-and-swap, protecting immutable approvals, complete participants, writer ownership, activation revisions, Live reservations, notebook/workspace rebind barriers and profiling claims. The eight-record physical normalization in closed #1704 is withdrawn as the target. Its successful local tests are prior design evidence, not validation of a replacement.

**Required invariants remain:** approval publication is atomic; incomplete or stale revisions never become executable; Live runs pin the correct approved revision; writer ownership and rebind barriers are enforced; stale CAS conflicts fail closed; lost acknowledgement is recoverable. Multiple independent Delta writes are not an atomic replacement for the existing singleton. Do not remove this authority until the joint model has passed the publication proof below.

### Joint pipeline metadata redesign

**Proposed outcome:** make `METADATA_PIPELINE_REGISTRY` the versioned connector for available pipelines, declared Read/Write participants, orchestration configuration and exact contract/Agreement approval references. Absorb Activation State responsibilities into that authority if the transaction proof succeeds. Keep `METADATA_PIPELINE_RUN` as execution history referencing the exact definition it ran. Decide the physical layout after the lifecycle and ownership audit; do not start by assigning one column to every old nested field.

#### Logical grains and responsibility

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

#### Definition, Test, approval and Live lifecycle

1. `setup_pipeline` resolves permanent identity and binding. Test continues discovering configuration and participants through the existing notebook calls; do not require a new authoring UI or a predeclared immutable definition before those calls exist.
2. Read, Transform and Write execute under one in-memory Test plan. No durable approvable definition or successful run is inferred from an isolated operation or notebook cell event.
3. Explicit `finalize_pipeline` validates complete participant/operation/stage coverage and seals the exact tested definition. Persist the immutable definition and required Guardrail results before marking its Test run successfully finalized. Separate-table intermediate records are non-authorizing; orphaned definitions/results cannot grant approval. Specify failure and lost-acknowledgement handling for each step before coding.
4. Governance revalidates the finalized run, current notebook/workspace binding, exact frozen contracts, required Guardrail results and currently effective Agreement. Publish the decision, complete references, current selections, ownership and affected environment revision in one guarded authority transaction. Preserve the current combined approval/activation workflow and widget behavior.
5. Live atomically checks that authority and acquires its reservation against the exact selected version and revision. Runtime resolves immutable configuration/contracts by reference and rejects changed notebook arguments or bindings. Later approvals cannot alter an already pinned execution.
6. Completion, interruption, reservation release, rebind and profiling recovery retain their existing fail-closed semantics. A run row alone does not prove that a reservation may be released or a business publication may be replayed.

Before replacing embedded documents with references, prove that referenced versions are unique, immutable, retained and hash-verifiable for the entire approval/run lifetime. Audit every writer, including foundational metadata writes. Missing or altered references must block execution with actionable reconciliation guidance; never fall back to the current/latest version. If an existing reference cannot provide historical content, document the minimum retained representation and its reason instead of claiming that IDs alone preserve history.

#### Current field disposition to verify

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

#### Lineage decision

Declared participants belong to the definition and can supply planned participation queries. Actual `METADATA_DATA_LINEAGE` rows currently record source/target participation after successful Live target publication; they are keyed by Fabric activity/table/role with environment matching, not by framework `run_id`. They do not prove individual source-to-target transformation edges. Publication can succeed before profiling or final run completion fails, so deriving observed history only from successful runs would lose facts.

Audit all package readers, widgets, references and externally consumed queries. Prefer deriving new declared participation from the Registry and preserving the existing Live observed-participation table unless a complete absorption provides a demonstrated benefit. If absorption is selected, include a concrete automatic migration preserving all existing rows and identities, repeat-safe validation, consumer updates and a rollback boundary in the same implementation. Do not infer run mappings that old activity-level history cannot establish. Keeping the Live table is an explicit supported decision, not a second source of pipeline configuration.

#### Transaction design and proof before persistence changes

The starting candidate is **one Registry authority publication** for approval/admission/rebind decisions with exact immutable definition references. A shared serialization point protects cross-pipeline contract and writer constraints. Run updates have their own per-run concurrency control; they do not republish the whole Registry. Select the smallest native-row/struct layout that supports these grains without a universal metadata table or the eight-payload layout from #1704 by default.

Before changing persistence, record the exact Delta statements, transaction boundaries, CAS predicate, insert/delete behavior, retention constraints and reader validation. Prove approval and its complete participant set become authoritative in one transaction: either store them together in that publication, or reference a previously sealed immutable complete definition whose publication/retention protocol cannot expose a partial version. If children insert in the authority MERGE, a stale guard must roll back unmatched inserts as well as updates/deletes. Prechecking a token outside MERGE is insufficient.

Use persisted Delta tests for simultaneous publishers, stale tokens, transaction rollback, unmatched inserts, missing/duplicate/altered references, complete participants, immutable approvals, exact content read-back after lost acknowledgement and idempotent retry. Race activation against Live acquisition, writer changes, rebind and profiling claims. Prove unrelated mutations preserve existing history/reservations and environments/pipelines remain isolated. Do not claim cross-table transactions for definitions, Run, Guardrail Results, Lineage or business data; document which partially published states are harmless and why readers fail closed.

If a simple consolidated physical design cannot prove these properties, keep the current authority in service and revise this plan before implementation. Do not ship a second writable authority or query projections as a completed consolidation.

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

### Joint redesign rollout and reset policy

The Pipeline Run converter documented above belongs to merged #1700. It converts the older summary layout into main's current run schema; **it does not migrate to the proposed joint model**. Do not reuse it for a different layout or add a standalone Preview converter just to preserve disposable history. The replacement PR must clearly distinguish its new upgrade guidance from this baseline procedure.

1. **Inventory the deployed layout.** Record package versions and physical schemas for Registry, Activation State, Run and any affected participation table. Include exact reference counts, immutable approvals and finalized Tests, active/interrupted reservations, rebind barriers and profiling claims. Closed #1704 was not merged; an independently deployed copy requires separate reconciliation rather than assumed support.
2. **Stop and drain.** Disable schedulers and new Test/Live starts, registration/rebind and profiling acquisition. Let existing work finish and reconcile interrupted work against actual publication evidence. Never clear a reservation merely to make replacement possible. Back up all affected Delta tables at pinned versions, their referenced contracts/Agreements/results, and the matching reader package. Preserve Processing State and business-target recovery evidence.
3. **Fresh setup.** Create only the final canonical model with strict schema validation; then register, finalize a complete Test, explicitly approve and select Live. Registration, an empty Registry or an orphaned definition cannot authorize execution.
4. **Disposable Preview state.** If operators explicitly choose to discard state and establish that no approval history, run history or outstanding claims must be retained, archive it and deliberately recreate only the affected Preview tables. Re-register pipelines with a documented identity choice, rerun Test and reapprove. Do not erase Live metadata or reset Processing State/checkpoints/publication receipts. Setup never drops tables, deletes approvals, releases reservations or recreates incompatible canonical tables automatically.
5. **Retained Preview state.** Where approvals/history/claims matter, preserve the old stopped deployment until an explicit reviewed reconciliation maps every retained identity and content hash into the complete new model. Validate counts, exact contract/Agreement/Test links, whole-run outcomes, decision history, participants, ownership and claim ownership before cutover. Do not invent missing historical content, infer success or automatically transfer unverified active work. If correctness cannot be established, retain the old deployment/archive and resolve it before enabling Live; a disposable reset is not a substitute for preservation.
6. **Supported Live participation.** If the implementation changes or absorbs `METADATA_DATA_LINEAGE`, its migration must preserve existing rows automatically, validate repeat execution without duplicates or loss, and define cutover and rollback explicitly. No drop/rebuild instruction is acceptable for this Live table. If it stays unchanged, assert its schema and rows remain unchanged and document its observed-participation role.
7. **Physical cutover and validation.** Replace only validated affected layouts at their actual configured Lakehouse paths while stopped; catalogue registration alone is insufficient for path-based readers. Switch all affected readers/writers together. Setup rejects incompatible canonical schemas with a clear repair action. Differently named retired Preview tables may remain unused without blocking setup; use the retirement registry for actionable archival/cleanup notices. Never automatically delete them.
8. **Rollback.** Before new writes, restore the backed-up affected metadata and matching package as a unit. After new runs, approvals, claims or business publications, stop and reconcile the new records and recovery boundaries before rollback. An old metadata snapshot alone can erase history or authorize unsafe replay. Keep backups until deployment validation and the agreed retention boundary complete.

For every changed physical table, the replacement must include a reviewed field-by-field mapping with Spark types/nullability, deterministic keys, lifecycle/uniqueness, retained JSON, discard/preservation policy, exact cutover steps and failure recovery. This plan deliberately supplies no hypothetical conversion code before that physical model is selected.

## Implementation workstreams and sequencing

| Workstream | Status at 2026-10-25 | Executor | PR / implementation | Dependencies and merge boundary |
| --- | --- | --- | --- | --- |
| A. Architecture and lifecycle audit | Merged | ChatGPT | [#1695](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1695) | Documentation baseline; no runtime changes |
| B. Focused metadata reference fixes | Merged (initial fixes) | ChatGPT | [#1696](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1696); metadata explorer [#1692](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1692) | Additional fixes only when a concrete discrepancy is found |
| C. Processing State redesign | Merged | Codex | [#1698](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1698) | Implemented `METADATA_PROCESSING_STATE`; keep its recovery protocol isolated |
| D. Pipeline Run normalization | Merged baseline | Codex | [#1700](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1700); [implemented model and migration](#pipeline-execution-engineering) | Preserve its finalized Test, immutable outcome and concurrency guarantees during the joint replacement |
| E. Joint pipeline metadata redesign | Plan first; replacement implementation not started | Codex in a fresh session | Activation-only [#1704](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1704) closed unmerged; [joint plan](#joint-pipeline-metadata-redesign) | Registry + Activation State + Run + participation audit in one coherent design and one focused replacement implementation PR; transaction proof before persistence changes |
| F. Contract/Guardrail/Access cleanup | Conditional / targeted prior work | ChatGPT for bounded fixes; otherwise Codex | Contract cleanup [#1649](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1649) and Guardrail integration [#1645](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1645) merged | Skip additional physical normalization without a demonstrated benefit |
| G. Final integration/reference generation | Pending final review | Owner of affected source | After relevant backend work | Regenerate only artifacts directly affected by C–F; verify clean second generation |

**Coordination:** C and D are merged baselines, including #1697 durable finalized Test results. The replacement E intentionally revisits Registry, Activation State and Run together; the earlier instruction to keep D/E as separate redesigns is superseded. Keep Processing State recovery isolated. Closed #1704 is not a schema dependency and must not be cherry-picked as the starting implementation. A merged PR denotes merged scope, not a claim that Microsoft Fabric deployment validation has completed.

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

Preserve supported Live tables and existing rows. Compatible additive columns may be applied automatically without replacing data. An approved Live column removal, rename or type change must ship with an explicit, tested automatic migration. It must preserve required data, validate results, support safe repeated execution and define a rollback boundary. Users must not be asked to drop/rebuild supported Live tables or guess conversions. This cutover changes no Live schemas and introduces no hypothetical conversions.
