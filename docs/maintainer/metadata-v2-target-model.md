# Metadata v2: target model and migration boundaries

**Implementation (2026-10-26):** the joint redesign starts from `65675b31` (merged #1705), including #1700 and #1702. It replaces the two serialization domains with one native `METADATA_PIPELINE_REGISTRY` authority, seals reusable configuration in `METADATA_PIPELINE_DEFINITION`, and stores execution facts in `METADATA_PIPELINE_RUN`. Closed #1704 was not used. Local persisted Delta tests prove the transactions described here; actual Fabric deployment checks remain separate.

## Goal and constraints

Metadata is an operational application database. One configured Metadata Lakehouse and the existing Governance/Engineering schemas remain. All six supported Live schemas and Processing State are unchanged. Preview pipeline persistence changes deliberately, without compatibility readers, dual writers or aliases. Public notebook signatures and result shapes remain; `candidate_json`, `candidate_fingerprint`, `activated_pipeline_id` and `operation_summary_json` in notebook results are reconstructed domain values, not duplicate persisted documents.

Registration never authorizes Live. Test operations remain in memory; only explicit finalization may commit the sealed definition, allowed Run and Guardrail diagnostics. Test never publishes business data, checkpoints, Catalogue or Lineage. An interrupted run cannot approve a definition.

## Ownership audit and layout decision

The audit covers package readers/writers, setup, foundational I/O, widgets, profiling, migration and generated references. Historical release manifests are unchanged. Registry, Activation State and Run were not listed in v0.2.5; breaking Preview rules apply, while retained history and outstanding claims still require reconciliation.

| Owner / fact | Readers and writers audited | Final disposition |
| --- | --- | --- |
| Registry registration | `read_pipeline_registry`, `resolve_pipeline_registration`, `commit_pipeline_registration`, `setup_pipeline`, startup/widget readers | Typed `registrations` in one Engineering Registry row. UUID/environment and active notebook uniqueness; original registration and latest binding audit retained. |
| Authority and Governance decisions | `review_pipeline_release`, `approve_pipeline_release`, `activation_impact`, `activation_version`, `resolve_approved_consumer_contract`, activation widget | `read_pipeline_authority` / `commit_pipeline_authority`; typed immutable approvals, selections/revisions and table ownership in the same Registry publication. Governance owns approval; Engineering remains the physical home to preserve routing and registration ownership. |
| Live execution and rebind | `build_live_pipeline_plan`, `verify_live_plan`, `release_pipeline_lease`, rebind reservation/release, `resolve_pipeline_registration` | Shared authority CAS fences binding changes, admission, cutover and reservations. Rebinding is one guarded binding mutation with an idle check; an independently acquired transient rebind barrier still blocks starts and rebinding. No second registration token. |
| Immutable configuration | `pipeline_candidate`, definition codecs, `seal_pipeline_definition`, `read_pipeline_definition`, Run/domain readers | Separate Engineering Definition table; content-addressed complete rows, exact contract references, native participants and bindings. No mutable definition head or latest-version fallback. |
| Run authority | `persist_pipeline_run`, `_merge_pipeline_run_row`, `pipeline_run_row`, `pipeline_run_result`, `publish_pipeline_testing_results`, `finalize_pipeline_run`, `finalize_pipeline` | One atomic native Run row; expected configuration lives in Definition. Parent, operations/stages, profiling, warnings and failures publish together. |
| Frozen contracts | `create_contract_draft`, `save_contract_draft`, `freeze_contract`, exact-version resolver, contract widget, activation and pipeline consumers | Existing Governance Data Contract schema and authored payload owner retained. Domain frozen-content protection remains; every definition resolution requires unique exact version, Frozen status, global table identity and payload SHA-256. |
| Agreements | `widget_render_data_agreement._create_or_update_data_agreement`, `agreement_definition`, `validate_agreement`, activation/Live verification | Existing Live Governance Agreement retained. Approvals reference version plus content hash; current effectiveness is checked for approval and Live. Owner edits to the selected version block Live until exact content is restored or a new Test/decision is approved. No embedded Agreement copies. |
| Guardrail Results | `write_guardrail_result_row`, `publish_pipeline_testing_results`, `tested_pipeline_manifest`, approval resolution | Existing per-rule aggregate grain and stable finalized-Test IDs retained. Exact rule coverage, continuation, contracts and workspace/notebook/activity provenance remain required. Approval stores a hash of reconstructed complete Test plus ordered diagnostics; later removal/alteration fails closed. |
| Profiling | `profiling_completion_history`, `record_profiling_outcome`, `claim_table_profile`, `maintain_table_profile_claim`, `schedule_table_profiling` | Renewable claims in Registry; native Run activity facts joined to physical profile/frequency snapshots. No profiling progress hidden in JSON. Owner-specific renewal/completion/release and expiry recovery remain. |
| Observed Lineage | `persist_lineage_participation`, `_finalize_committed_target_metadata`, lineage readers/plotters and `widgets.shared` Catalogue/Lineage consumers | Live `METADATA_DATA_LINEAGE` unchanged, including activity/table/role/environment identity and existing rows. Declared participation comes from Definition. Publication followed by later profiling/run failure still records observed participation. No invented source-to-target edges or inferred framework run IDs. |
| Processing State | source capture, incremental/drift resolution, `PublicationBatch`, staging/commit/recovery and target admission | #1698 schema and recovery unchanged. Pipeline and run IDs remain exact integration references; no reset or implicit publication replay. |
| Physical writes and external queries | `read_lakehouse_table`, `write_lakehouse_table`, configured path/session helpers, setup and SQL consumers | Generic I/O can physically alter metadata and is not an immutable-version API. Supported domain writers never replace sealed definitions or completed runs; readers hash-check referenced content and reject missing/duplicate/altered rows even after foundational writes. Operators must retain exact owner content for the entire history lifetime. SQL queries join Run → Definition; Registry collections are exploded for decisions and reservations. |
| Reference generators | canonical schemas, column ownership metadata, callable graph, metadata explorer, SVG, glossary | Source-first regeneration of affected outputs; no dashboard, release or notebook refresh. |

Three layouts were compared. Keeping the two old authorities leaves a registration/admission race and duplicate serialization. Flattening independent authority/child rows requires an insertion/deletion fence and a more complex whole-publication proof; #1704's eight-payload design is withdrawn. The chosen single native row commits all related authority facts together, while the separate immutable Definition table prevents every Run update from rewriting shared authority. There is no `record_type` discriminator: Registry key is `authority_id='central'`, Definition key is `definition_id`, Run key is `run_id`. Array members have the logical keys documented below. Table count remains 13; it is not an optimization target.

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

#1700's one-row outcome, first-publication uniqueness, complete-previous-row CAS, terminal immutability, bounded aborted-transaction retry and exact lost-acknowledgement read-back remain. The replacement removes persisted candidate/configuration/contract copies from Run. Native operations carry only observed status, timing and stages; their expected table, role, contract and configuration resolve by exact `definition_id` and `operation_key`.

A Live run references its approved definition from admission onward, including not-started operations. Allowed operational parameter differences retain tested and actual values in sanitized warnings; the definition remains pinned. Configuration and physical-binding checks still occur before each operation. A failed or rejected operation persists a safe failure, never a new approved configuration. Finalized Test seals its actual complete configuration; incomplete/failed finalized Tests may retain diagnostics but cannot approve.

#### Earlier Pipeline Run layout conversion

The former `scripts/migrate_pipeline_runs.py` converted only pre-#1700 summary rows into #1700's candidate/typed-operation layout. It is removed from this model because its imports would otherwise target an incompatible schema. To deliberately upgrade only to that historical baseline, use the package and converter pinned to [#1700](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1700), before #1705's successor implementation. It does not convert to this joint model. The Processing State procedure above has its own distinct source/target layouts.

## Joint pipeline metadata redesign

### Immutable lifecycle and references

1. Engineering registers a UUID/environment notebook binding. There is no selected approval yet.
2. Test declares participants/configuration in memory; operations cannot mutate business or operational state.
3. Explicit finalization writes allowed Guardrail diagnostics, seals a complete content-addressed definition row, then atomically publishes the Run with its complete observed operation/stage set and whole-run boundary. A definition can be orphaned if the Run write fails; this grants no authority. Repeated sealing uses the same Delta transaction identity and verifies exact content.
4. Governance revalidates the exact successful finalized Test, complete required stages and rules, current binding, frozen contracts, immutable definition and currently effective Agreement. A native approval references `definition_id`, Test ID/hash and Agreement version/hash. Decision identity remains the complete domain manifest digest; `pipeline_name`/`pipeline_version` remain independent Governance labels, unique per pipeline/environment/version. Repeating the same decision retains its original audit, while a new label creates independent decision history over the same definition.
5. One Registry CAS publishes new decisions, complete selections, table/contract/writer mappings and the environment revision. Referenced definitions were already sealed; their complete participant set cannot be partially published.
6. Live validates registration and approval under the same token, requires the registered workspace/notebook to match the finalized Test audit, resolves exact retained content and acquires its reservation through the same CAS. Rebinding requires a new finalized Test and decision before Live. Subsequent decisions cannot mutate that pinned definition; affected busy pipelines must drain before cutover. Completion releases only its own pipeline/revision reservation after the Run outcome is confirmed.
7. Profiling retains finite owner-token claims, renewal and completion authorization; a completion claim remains until the physical result and Run marker are confirmed. Interrupted claims recover by the existing expiry rules, never by assuming publication failed.

Referenced versions must be unique, hash-verifiable and retained for the entire approval/run lifetime. Definition identity hashes the complete candidate plus environment. Its candidate fingerprint remains the notebook identity contract; it is nullable only when the candidate was incomplete/unqualifiable. Exact Frozen payloads reconstruct portable candidate content rather than copying authored contract documents. Agreement and finalized Test content hashes cover the content used to reconstruct decisions. No reader falls back to current/latest configuration. Arbitrary external deletion or mutation is detected and blocks execution; a shared authority read validates retained approval references, so corruption can require reconciliation before unrelated authority mutations too.

### Current-field disposition and column/JSON justification

The full exact new Spark types/nullability, including nested members, are generated from `metadata_schemas.py` in the linked references. Arrays and their struct elements are required unless explicitly nullable; Spark may physically report looser nullability, so domain readers enforce keys, membership, hashes and authority consistency.

| Table / columns | Owning fact, derivation and reader/writer purpose |
| --- | --- |
| Registry `authority_id`, `token` | Required strings: singleton identity and fresh concurrency token. Setup seeds the row; every authority mutation CASes token. A business ID is never the fence. |
| `registrations` | Required typed array keyed by pipeline/environment: UUID, notebook/workspace binding, display name, original registration time/principal, Active/Retired and eight audit fields. Engineering recovery/rebind and activation eligibility read these. Latest audit belongs to the binding; the authority row audit identifies the whole mutation. Permanent bindings are retained, explicitly retired rather than removed. |
| `revisions` | Required typed array keyed by environment: required environment/revision strings, derived from coordinated selection publication and pinned by Live. |
| `approvals` | Required typed array keyed by approval ID: required approval/definition/pipeline/environment IDs, pipeline labels, finalized Test ID/hash, Agreement ID/version/hash, native warning strings and eight audit fields. Governance publishes append-only history; domain readers reconstruct manifests and verify every reference. No embedded candidate, Test, Agreement or contract documents. |
| `selections` | Required typed array keyed by environment/pipeline: approval ID references retained history. The current executable selection is distinct from the immutable decision. |
| `table_ownership` | Required typed array keyed by environment/table: exact contract ID/version/hash, typed physical destination, nullable writer and required reader UUID array. Derived from the entire selected definition set by `activation_impact`; conflicting contracts, aliases or writers block publication. |
| `reservations` | Required typed array keyed by environment/reservation ID: pipeline, mode, table IDs; nullable revision/destinations are absent only for a transient rebind barrier. Live carries its exact revision and typed destinations. Acquisition, cutover and owner-specific release all use Registry CAS. |
| `profiling_claims` | Required typed array keyed by claim key: context key, token, table/environment, typed physical destination, activity/trigger, execution owner, expiry and nullable completion time. Lease timestamps retain the existing offset-qualified string representation for exact scheduler comparisons and result joins. These are typed fields, not JSON. |
| Definition `definition_id`, `pipeline_id`, `environment_name`, `candidate_fingerprint` | Required content ID and logical parent/environment; nullable candidate hash preserves existing qualification semantics. The ID covers environment as well as content; the hash preserves notebook candidate identity. Run-side pipeline/environment remain useful for filtering and are checked against Definition to reject foreign links. |
| Definition `participants` | Required typed array keyed by logical participant; exact global table ID and nonempty unique source/target roles; nullable contract ID/version/hash only as an all-null explicit No Contract. There is no second contract lifecycle. Sealing and approval validate complete membership and exact Frozen owner content. |
| Definition `physical_bindings` | Nullable typed array for configurations that have not resolved bindings; otherwise complete table-keyed workspace/item/kind/schema/table destinations. Only schema may be null within a resolved destination. Hashes and Live verify physical identity. |
| Definition `operation_configurations` | Required typed array keyed by role/logical operation; nullable configuration hash/settings only for unstarted/unqualifiable diagnostics. The hash preserves operation identity; settings JSON contains variable read modes, processing parameters, SQL/dependency hashes and Spark settings. Stable operation identity remains native. |
| Definition `project_configuration_json` | Required string containing a sanitized variable settings object: project transformation/dependency configuration. No participants, approvals, statuses or reservations. Retained once per immutable definition; variable authored keys justify JSON. |
| Run `run_id`, `definition_id`, `pipeline_id`, `environment_name`, `execution_mode` | Required strings for attempt identity, exact definition join, partition/filter context and Test/Live policy. Parent/environment copies are enforcement checks, not independent configuration. |
| Run `approval_id`, `activation_revision` | Nullable strings: exact decision and environment revision for Live; null/empty for Test. Replaces the persisted ambiguous `activated_pipeline_id`; that supported notebook result name is reconstructed. |
| Run `started_at`, `completed_at`, `status`, `boundary_completed` | Required start timestamp/status/boolean and nullable completion timestamp. Preserve actual attempt lifecycle and explicit whole-notebook completion; operation success alone never completes Test. |
| Run `operations` | Required array keyed by operation key: required status/stages, nullable actual start/end timestamps. Stage name/status are required, evaluation status nullable. No repeated expected table/contract/configuration declarations. `pipeline_run_result` validates exact membership, success and stage constraints against Definition. |
| Run `profiling` | Required native activity array: context/table/environment/destination, activity/status/trigger, attempt/snapshot IDs, execution/completion times, persisted/empty flags, count and safe reason/exception fields. Context key/activity/status required; other facts nullable for skipped/failed work. Schedule history joins native completed markers to actual profile/frequency snapshots. |
| Run `failures` | Required native array of required safe code and nullable exception class; raw exception messages are excluded. Failure cannot regress to success. |
| Run `warnings_json` | Required JSON array of variable sanitized diagnostics: operational parameter names with tested/actual values, warning codes and variable diagnostic attributes. No approvals, bindings, profiling state or reservations. Preserves diagnostic variability without a new operational snapshot document. |
| All three tables' eight audit columns | Existing required string identities plus required `_committed_at` timestamp. Runtime audit owner remains `build_runtime_audit_fields`. Definition audit records first seal; repeat sealing checks content without replacing it. Run audit records its last accepted publication; approval/member audit remains immutable. |

No `snapshot_json`, `registry_token`, `candidate_json`, `candidate_fingerprint` copy on Run, `run_details_json`, operation configuration/contract copy, or persisted `operation_summary_json` remains. Candidate hashing belongs to Definition. JSON is limited to project settings, operation settings and variable sanitized warnings. Authored contract/Agreement flexible payloads stay in their existing owner tables.

### Exact physical schema changes

- Registry: old required `pipeline_id`, `environment_name`, `registration_status` strings; nullable workspace/notebook/name/principal/status-token strings and registration timestamp; eight required audit fields. New singleton layout is [Registry](../reference/metadata/metadata_pipeline_registry.md). Old binding fields move losslessly into `registrations`; old control row/token is superseded by the joint authority token, never transferred as business identity.
- Activation State: old required `authority_id`, `token`, `snapshot_json` strings plus eight audit fields. Removed from the canonical registry and declared retired. All logical responsibilities are mapped to the native Registry collections above. Its physical rows are never read at runtime or automatically deleted.
- Definition: new [Definition](../reference/metadata/metadata_pipeline_definition.md), one sealed content row, no discriminator. Candidate participants, exact references, configurations and bindings are transformed explicitly; candidate/definition hashes are verified after reconstruction.
- Run: old required run/pipeline/mode/environment/status/candidate strings, start timestamp, completion/approval/fingerprint nullable fields, boolean boundary, native configured operations, details JSON and eight audit fields. New [Run](../reference/metadata/metadata_pipeline_run.md) retains attempt/status/timing/audit and observed stages, moves candidate/configuration/contracts into Definition, replaces approval reference name, and extracts profiling, activation revision and safe failures. Warning JSON retains only variable diagnostics. No source row is safely additive-evolved.

<details markdown="1"><summary>Exact baseline and replacement field types/nullability</summary>

The following inventory was captured from #1705's merge commit and the canonical replacement schemas. `!` means required; `?` means nullable. Nested types are native Spark structs/arrays, not JSON strings.

**METADATA_PIPELINE_REGISTRY**

| Layout | Field | Spark type | Nullability |
| --- | --- | --- | --- |
| Baseline | `pipeline_id` | `string` | ! |
| Baseline | `environment_name` | `string` | ! |
| Baseline | `workspace_id` | `string` | ? |
| Baseline | `notebook_id` | `string` | ? |
| Baseline | `notebook_name` | `string` | ? |
| Baseline | `registered_at` | `timestamp` | ? |
| Baseline | `registered_by` | `string` | ? |
| Baseline | `registration_status` | `string` | ! |
| Baseline | `registry_token` | `string` | ? |
| Baseline | `_committed_by` | `string` | ! |
| Baseline | `_committed_at` | `timestamp` | ! |
| Baseline | `_workspace_id` | `string` | ! |
| Baseline | `_workspace_name` | `string` | ! |
| Baseline | `_notebook_id` | `string` | ! |
| Baseline | `_notebook_name` | `string` | ! |
| Baseline | `_metadata_lakehouse_name` | `string` | ! |
| Baseline | `_activity_id` | `string` | ! |
| Replacement | `authority_id` | `string` | ! |
| Replacement | `token` | `string` | ! |
| Replacement | `registrations` | `array<struct<pipeline_id:string,environment_name:string,workspace_id:string,notebook_id:string,notebook_name:string,registered_at:timestamp,registered_by:string,registration_status:string,_committed_by:string,_committed_at:timestamp,_workspace_id:string,_workspace_name:string,_notebook_id:string,_notebook_name:string,_metadata_lakehouse_name:string,_activity_id:string>>` | ! |
| Replacement | `revisions` | `array<struct<environment_name:string,revision:string>>` | ! |
| Replacement | `approvals` | `array<struct<approval_id:string,definition_id:string,pipeline_id:string,environment_name:string,pipeline_name:string,pipeline_version:string,testing_run_id:string,testing_evidence_sha256:string,agreement_id:string,agreement_version:string,agreement_sha256:string,warnings:array<string>,_committed_by:string,_committed_at:timestamp,_workspace_id:string,_workspace_name:string,_notebook_id:string,_notebook_name:string,_metadata_lakehouse_name:string,_activity_id:string>>` | ! |
| Replacement | `selections` | `array<struct<environment_name:string,pipeline_id:string,approval_id:string>>` | ! |
| Replacement | `table_ownership` | `array<struct<environment_name:string,table_id:string,contract_id:string,contract_version:int,payload_sha256:string,writer:string,readers:array<string>,destination:struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>>` | ! |
| Replacement | `reservations` | `array<struct<environment_name:string,reservation_id:string,pipeline_id:string,mode:string,tables:array<string>,revision:string,destinations:array<struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>>>` | ! |
| Replacement | `profiling_claims` | `array<struct<claim_key:string,token:string,key:string,table_id:string,environment:string,physical:struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>,activity:string,trigger:string,expires_at:string,execution_id:string,completed_at:string>>` | ! |
| Replacement | `_committed_by` | `string` | ! |
| Replacement | `_committed_at` | `timestamp` | ! |
| Replacement | `_workspace_id` | `string` | ! |
| Replacement | `_workspace_name` | `string` | ! |
| Replacement | `_notebook_id` | `string` | ! |
| Replacement | `_notebook_name` | `string` | ! |
| Replacement | `_metadata_lakehouse_name` | `string` | ! |
| Replacement | `_activity_id` | `string` | ! |



**METADATA_ACTIVATION_STATE**

| Layout | Field | Spark type | Nullability |
| --- | --- | --- | --- |
| Baseline | `authority_id` | `string` | ! |
| Baseline | `token` | `string` | ! |
| Baseline | `snapshot_json` | `string` | ! |
| Baseline | `_committed_by` | `string` | ! |
| Baseline | `_committed_at` | `timestamp` | ! |
| Baseline | `_workspace_id` | `string` | ! |
| Baseline | `_workspace_name` | `string` | ! |
| Baseline | `_notebook_id` | `string` | ! |
| Baseline | `_notebook_name` | `string` | ! |
| Baseline | `_metadata_lakehouse_name` | `string` | ! |
| Baseline | `_activity_id` | `string` | ! |
| Replacement | — | Absent | — |



**METADATA_PIPELINE_DEFINITION**

| Layout | Field | Spark type | Nullability |
| --- | --- | --- | --- |
| Baseline | — | Absent | — |
| Replacement | `definition_id` | `string` | ! |
| Replacement | `pipeline_id` | `string` | ! |
| Replacement | `environment_name` | `string` | ! |
| Replacement | `candidate_fingerprint` | `string` | ? |
| Replacement | `project_configuration_json` | `string` | ! |
| Replacement | `participants` | `array<struct<participant:string,table_id:string,roles:array<string>,contract_id:string,contract_version:int,payload_sha256:string>>` | ! |
| Replacement | `operation_configurations` | `array<struct<operation_key:string,configuration_sha256:string,configuration_json:string>>` | ! |
| Replacement | `physical_bindings` | `array<struct<table_id:string,workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>` | ? |
| Replacement | `_committed_by` | `string` | ! |
| Replacement | `_committed_at` | `timestamp` | ! |
| Replacement | `_workspace_id` | `string` | ! |
| Replacement | `_workspace_name` | `string` | ! |
| Replacement | `_notebook_id` | `string` | ! |
| Replacement | `_notebook_name` | `string` | ! |
| Replacement | `_metadata_lakehouse_name` | `string` | ! |
| Replacement | `_activity_id` | `string` | ! |



**METADATA_PIPELINE_RUN**

| Layout | Field | Spark type | Nullability |
| --- | --- | --- | --- |
| Baseline | `run_id` | `string` | ! |
| Baseline | `activated_pipeline_id` | `string` | ? |
| Baseline | `pipeline_id` | `string` | ! |
| Baseline | `execution_mode` | `string` | ! |
| Baseline | `environment_name` | `string` | ! |
| Baseline | `started_at` | `timestamp` | ! |
| Baseline | `completed_at` | `timestamp` | ? |
| Baseline | `status` | `string` | ! |
| Baseline | `candidate_fingerprint` | `string` | ? |
| Baseline | `candidate_json` | `string` | ! |
| Baseline | `boundary_completed` | `boolean` | ! |
| Baseline | `operations` | `array<struct<operation_key:string,table_id:string,status:string,started_at:timestamp,completed_at:timestamp,configuration_sha256:string,configuration_json:string,contract_id:string,contract_version:int,contract_payload_sha256:string,stages:array<struct<stage:string,status:string,evaluation_status:string>>>>` | ! |
| Baseline | `run_details_json` | `string` | ! |
| Baseline | `_committed_by` | `string` | ! |
| Baseline | `_committed_at` | `timestamp` | ! |
| Baseline | `_workspace_id` | `string` | ! |
| Baseline | `_workspace_name` | `string` | ! |
| Baseline | `_notebook_id` | `string` | ! |
| Baseline | `_notebook_name` | `string` | ! |
| Baseline | `_metadata_lakehouse_name` | `string` | ! |
| Baseline | `_activity_id` | `string` | ! |
| Replacement | `run_id` | `string` | ! |
| Replacement | `approval_id` | `string` | ? |
| Replacement | `definition_id` | `string` | ! |
| Replacement | `pipeline_id` | `string` | ! |
| Replacement | `execution_mode` | `string` | ! |
| Replacement | `environment_name` | `string` | ! |
| Replacement | `started_at` | `timestamp` | ! |
| Replacement | `completed_at` | `timestamp` | ? |
| Replacement | `status` | `string` | ! |
| Replacement | `activation_revision` | `string` | ? |
| Replacement | `boundary_completed` | `boolean` | ! |
| Replacement | `operations` | `array<struct<operation_key:string,status:string,started_at:timestamp,completed_at:timestamp,stages:array<struct<stage:string,status:string,evaluation_status:string>>>>` | ! |
| Replacement | `profiling` | `array<struct<context_key:string,activity:string,status:string,results_persisted:boolean,empty_result:boolean,profile_snapshot_id:string,completed_at:string,reason:string,table_id:string,row_count:bigint,trigger:string,environment:string,pipeline_run_id:string,executed_at:string,physical:struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>>` | ! |
| Replacement | `warnings_json` | `string` | ! |
| Replacement | `failures` | `array<struct<code:string,exception_type:string>>` | ! |
| Replacement | `_committed_by` | `string` | ! |
| Replacement | `_committed_at` | `timestamp` | ! |
| Replacement | `_workspace_id` | `string` | ! |
| Replacement | `_workspace_name` | `string` | ! |
| Replacement | `_notebook_id` | `string` | ! |
| Replacement | `_notebook_name` | `string` | ! |
| Replacement | `_metadata_lakehouse_name` | `string` | ! |
| Replacement | `_activity_id` | `string` | ! |



</details>

### Nested field nullability inventory

This completes the top-level inventory above. Array element nulls are forbidden for every new collection. Struct fields use their own declared nullability; Spark storage can report relaxed nullability, so runtime validation is also required.

| Layout / table | Nested field path | Spark type | Nullable |
| --- | --- | --- | --- |
| New REGISTRY | `registrations[]` | `struct` element | False |
| New REGISTRY | `registrations[].pipeline_id` | `string` | False |
| New REGISTRY | `registrations[].environment_name` | `string` | False |
| New REGISTRY | `registrations[].workspace_id` | `string` | False |
| New REGISTRY | `registrations[].notebook_id` | `string` | False |
| New REGISTRY | `registrations[].notebook_name` | `string` | False |
| New REGISTRY | `registrations[].registered_at` | `timestamp` | False |
| New REGISTRY | `registrations[].registered_by` | `string` | False |
| New REGISTRY | `registrations[].registration_status` | `string` | False |
| New REGISTRY | `registrations[]._committed_by` | `string` | False |
| New REGISTRY | `registrations[]._committed_at` | `timestamp` | False |
| New REGISTRY | `registrations[]._workspace_id` | `string` | False |
| New REGISTRY | `registrations[]._workspace_name` | `string` | False |
| New REGISTRY | `registrations[]._notebook_id` | `string` | False |
| New REGISTRY | `registrations[]._notebook_name` | `string` | False |
| New REGISTRY | `registrations[]._metadata_lakehouse_name` | `string` | False |
| New REGISTRY | `registrations[]._activity_id` | `string` | False |
| New REGISTRY | `revisions[]` | `struct` element | False |
| New REGISTRY | `revisions[].environment_name` | `string` | False |
| New REGISTRY | `revisions[].revision` | `string` | False |
| New REGISTRY | `approvals[]` | `struct` element | False |
| New REGISTRY | `approvals[].approval_id` | `string` | False |
| New REGISTRY | `approvals[].definition_id` | `string` | False |
| New REGISTRY | `approvals[].pipeline_id` | `string` | False |
| New REGISTRY | `approvals[].environment_name` | `string` | False |
| New REGISTRY | `approvals[].pipeline_name` | `string` | False |
| New REGISTRY | `approvals[].pipeline_version` | `string` | False |
| New REGISTRY | `approvals[].testing_run_id` | `string` | False |
| New REGISTRY | `approvals[].testing_evidence_sha256` | `string` | False |
| New REGISTRY | `approvals[].agreement_id` | `string` | False |
| New REGISTRY | `approvals[].agreement_version` | `string` | False |
| New REGISTRY | `approvals[].agreement_sha256` | `string` | False |
| New REGISTRY | `approvals[].warnings` | `array<string>` | False |
| New REGISTRY | `approvals[]._committed_by` | `string` | False |
| New REGISTRY | `approvals[]._committed_at` | `timestamp` | False |
| New REGISTRY | `approvals[]._workspace_id` | `string` | False |
| New REGISTRY | `approvals[]._workspace_name` | `string` | False |
| New REGISTRY | `approvals[]._notebook_id` | `string` | False |
| New REGISTRY | `approvals[]._notebook_name` | `string` | False |
| New REGISTRY | `approvals[]._metadata_lakehouse_name` | `string` | False |
| New REGISTRY | `approvals[]._activity_id` | `string` | False |
| New REGISTRY | `selections[]` | `struct` element | False |
| New REGISTRY | `selections[].environment_name` | `string` | False |
| New REGISTRY | `selections[].pipeline_id` | `string` | False |
| New REGISTRY | `selections[].approval_id` | `string` | False |
| New REGISTRY | `table_ownership[]` | `struct` element | False |
| New REGISTRY | `table_ownership[].environment_name` | `string` | False |
| New REGISTRY | `table_ownership[].table_id` | `string` | False |
| New REGISTRY | `table_ownership[].contract_id` | `string` | False |
| New REGISTRY | `table_ownership[].contract_version` | `int` | False |
| New REGISTRY | `table_ownership[].payload_sha256` | `string` | False |
| New REGISTRY | `table_ownership[].writer` | `string` | True |
| New REGISTRY | `table_ownership[].readers` | `array<string>` | False |
| New REGISTRY | `table_ownership[].destination` | `struct` | False |
| New REGISTRY | `table_ownership[].destination.workspace_id` | `string` | False |
| New REGISTRY | `table_ownership[].destination.item_id` | `string` | False |
| New REGISTRY | `table_ownership[].destination.kind` | `string` | False |
| New REGISTRY | `table_ownership[].destination.schema` | `string` | True |
| New REGISTRY | `table_ownership[].destination.table_name` | `string` | False |
| New REGISTRY | `reservations[]` | `struct` element | False |
| New REGISTRY | `reservations[].environment_name` | `string` | False |
| New REGISTRY | `reservations[].reservation_id` | `string` | False |
| New REGISTRY | `reservations[].pipeline_id` | `string` | False |
| New REGISTRY | `reservations[].mode` | `string` | False |
| New REGISTRY | `reservations[].tables` | `array<string>` | False |
| New REGISTRY | `reservations[].revision` | `string` | True |
| New REGISTRY | `reservations[].destinations` | `array<struct>` | True |
| New REGISTRY | `reservations[].destinations[]` | `struct` element | False |
| New REGISTRY | `reservations[].destinations[].workspace_id` | `string` | False |
| New REGISTRY | `reservations[].destinations[].item_id` | `string` | False |
| New REGISTRY | `reservations[].destinations[].kind` | `string` | False |
| New REGISTRY | `reservations[].destinations[].schema` | `string` | True |
| New REGISTRY | `reservations[].destinations[].table_name` | `string` | False |
| New REGISTRY | `profiling_claims[]` | `struct` element | False |
| New REGISTRY | `profiling_claims[].claim_key` | `string` | False |
| New REGISTRY | `profiling_claims[].token` | `string` | False |
| New REGISTRY | `profiling_claims[].key` | `string` | False |
| New REGISTRY | `profiling_claims[].table_id` | `string` | False |
| New REGISTRY | `profiling_claims[].environment` | `string` | False |
| New REGISTRY | `profiling_claims[].physical` | `struct` | False |
| New REGISTRY | `profiling_claims[].physical.workspace_id` | `string` | False |
| New REGISTRY | `profiling_claims[].physical.item_id` | `string` | False |
| New REGISTRY | `profiling_claims[].physical.kind` | `string` | False |
| New REGISTRY | `profiling_claims[].physical.schema` | `string` | True |
| New REGISTRY | `profiling_claims[].physical.table_name` | `string` | False |
| New REGISTRY | `profiling_claims[].activity` | `string` | False |
| New REGISTRY | `profiling_claims[].trigger` | `string` | False |
| New REGISTRY | `profiling_claims[].expires_at` | `string` | False |
| New REGISTRY | `profiling_claims[].execution_id` | `string` | False |
| New REGISTRY | `profiling_claims[].completed_at` | `string` | True |
| New DEFINITION | `participants[]` | `struct` element | False |
| New DEFINITION | `participants[].participant` | `string` | False |
| New DEFINITION | `participants[].table_id` | `string` | False |
| New DEFINITION | `participants[].roles` | `array<string>` | False |
| New DEFINITION | `participants[].contract_id` | `string` | True |
| New DEFINITION | `participants[].contract_version` | `int` | True |
| New DEFINITION | `participants[].payload_sha256` | `string` | True |
| New DEFINITION | `operation_configurations[]` | `struct` element | False |
| New DEFINITION | `operation_configurations[].operation_key` | `string` | False |
| New DEFINITION | `operation_configurations[].configuration_sha256` | `string` | True |
| New DEFINITION | `operation_configurations[].configuration_json` | `string` | True |
| New DEFINITION | `physical_bindings[]` | `struct` element | False |
| New DEFINITION | `physical_bindings[].table_id` | `string` | False |
| New DEFINITION | `physical_bindings[].workspace_id` | `string` | False |
| New DEFINITION | `physical_bindings[].item_id` | `string` | False |
| New DEFINITION | `physical_bindings[].kind` | `string` | False |
| New DEFINITION | `physical_bindings[].schema` | `string` | True |
| New DEFINITION | `physical_bindings[].table_name` | `string` | False |
| New RUN | `operations[]` | `struct` element | False |
| New RUN | `operations[].operation_key` | `string` | False |
| New RUN | `operations[].status` | `string` | False |
| New RUN | `operations[].started_at` | `timestamp` | True |
| New RUN | `operations[].completed_at` | `timestamp` | True |
| New RUN | `operations[].stages` | `array<struct>` | False |
| New RUN | `operations[].stages[]` | `struct` element | False |
| New RUN | `operations[].stages[].stage` | `string` | False |
| New RUN | `operations[].stages[].status` | `string` | False |
| New RUN | `operations[].stages[].evaluation_status` | `string` | True |
| New RUN | `profiling[]` | `struct` element | False |
| New RUN | `profiling[].context_key` | `string` | False |
| New RUN | `profiling[].activity` | `string` | False |
| New RUN | `profiling[].status` | `string` | False |
| New RUN | `profiling[].results_persisted` | `boolean` | True |
| New RUN | `profiling[].empty_result` | `boolean` | True |
| New RUN | `profiling[].profile_snapshot_id` | `string` | True |
| New RUN | `profiling[].completed_at` | `string` | True |
| New RUN | `profiling[].reason` | `string` | True |
| New RUN | `profiling[].table_id` | `string` | True |
| New RUN | `profiling[].row_count` | `bigint` | True |
| New RUN | `profiling[].trigger` | `string` | True |
| New RUN | `profiling[].environment` | `string` | True |
| New RUN | `profiling[].pipeline_run_id` | `string` | True |
| New RUN | `profiling[].executed_at` | `string` | True |
| New RUN | `profiling[].physical` | `struct` | True |
| New RUN | `profiling[].physical.workspace_id` | `string` | False |
| New RUN | `profiling[].physical.item_id` | `string` | False |
| New RUN | `profiling[].physical.kind` | `string` | False |
| New RUN | `profiling[].physical.schema` | `string` | True |
| New RUN | `profiling[].physical.table_name` | `string` | False |
| New RUN | `failures[]` | `struct` element | False |
| New RUN | `failures[].code` | `string` | False |
| New RUN | `failures[].exception_type` | `string` | True |
| Baseline RUN | `operations[]` | `struct` element | False |
| Baseline RUN | `operations[].operation_key` | `string` | False |
| Baseline RUN | `operations[].table_id` | `string` | False |
| Baseline RUN | `operations[].status` | `string` | False |
| Baseline RUN | `operations[].started_at` | `timestamp` | True |
| Baseline RUN | `operations[].completed_at` | `timestamp` | True |
| Baseline RUN | `operations[].configuration_sha256` | `string` | True |
| Baseline RUN | `operations[].configuration_json` | `string` | True |
| Baseline RUN | `operations[].contract_id` | `string` | True |
| Baseline RUN | `operations[].contract_version` | `int` | True |
| Baseline RUN | `operations[].contract_payload_sha256` | `string` | True |
| Baseline RUN | `operations[].stages` | `array<struct>` | False |
| Baseline RUN | `operations[].stages[]` | `struct` element | False |
| Baseline RUN | `operations[].stages[].stage` | `string` | False |
| Baseline RUN | `operations[].stages[].status` | `string` | False |
| Baseline RUN | `operations[].stages[].evaluation_status` | `string` | True |

### Lineage decision

Keep `METADATA_DATA_LINEAGE` as the supported Live observed-participation owner. Catalogue, plotting and widget readers continue to consume its original activity/table/role identities. Definition supplies new declared participation. A successful target publication followed by failed profiling/finalization remains a real observed participation fact; successful Run filtering cannot replace it. There is no Live structural change, automatic Lineage migration, row rewrite or inferred historical run mapping.

### Transaction design and proof before persistence changes

The authority protocol uses **one existing native Registry row**, with all approvals, complete selections, table ownership and reservations committed together. Definition and Run have their own commit boundaries.

```sql
MERGE INTO delta.`<configured-registry-path>` target
USING <one complete native authority row> source
ON target.authority_id = source.authority_id
WHEN MATCHED THEN UPDATE SET
  token = CASE WHEN target.token = '<expected token>' THEN source.token
               ELSE CAST(raise_error('Stale Pipeline Registry authority; refresh') AS STRING) END,
  -- every native collection and audit field = source field
  approvals = source.approvals, selections = source.selections,
  table_ownership = source.table_ownership, reservations = source.reservations;
```

The actual production update also includes registrations, environment revisions, profiling claims and audit. There is **no WHEN NOT MATCHED**, child insertion, deletion, precheck-only fence or runtime DDL. Setup alone creates the singleton with create-if-absent semantics. A missing/duplicate singleton blocks writes. There is no unmatched-child branch that could escape a stale guard: new members are inside the same guarded update. Delta optimistic conflict detection fences overlapping updates to this same row; default WriteSerializable already detects conflicting same-row rewrites. No per-update property change is necessary. Lost acknowledgement succeeds only after exact token **and complete native content** read-back, normalizing native timestamp instants; an unknown outcome remains failed/inspectable.

Definition sealing writes one full row using append with `txnAppId=fabricops-definition:<definition_id>`, `txnVersion=0`. Readers require exactly one content-addressed row, complete operation/participant membership, exact Frozen references and a reconstructed full hash match. Repeated/concurrent sealing is idempotent. `delta.setTransactionRetentionDuration` must remain unconfigured (unbounded transaction identity retention). Retain referenced owner rows and Delta transaction identities; an expired identity or manual append is not a supported sealer. Orphaned definitions are harmless because neither registration nor definition existence selects Live.

Run first publication retains `txnAppId=fabricops-pipeline-run:<run_id>`, version 0 and the same unbounded retention constraint. Updates MERGE on run ID, comparing the complete previous native row with null-safe struct equality inside the transaction. A stale/terminal/regressing outcome raises; bounded retries apply only to Delta exceptions proving an aborted metadata transaction, including unrelated runs sharing a data file. No business publication is replayed. Complete outcomes, observed operations and stages commit at one row boundary.

There is no cross-table transaction over Definition, Run, Guardrail Results, Contract, Agreement, Lineage or business data. Diagnostics/definitions without an approving complete Run are inert. A complete Run without matching required diagnostics cannot approve. Authority resolves and hash-checks already sealed complete references before publication and execution. Missing/duplicate/altered content fails closed rather than choosing another version. Processing State alone proves publication progress using its own target evidence; a Run or reservation never substitutes for it.

Persisted proofs use the new production code, not #1704 results: stale and simultaneous authority publishers; singleton absence; collection rollback; no unmatched insert path; exact lost-acknowledgement read-back; unique concurrent definition sealing; orphaned definitions; missing/duplicate/altered definition/contract/Agreement/Test references; finalized Test → independent approval history → Live; immutable history; shared-CAS admission races against approval, rebind and profiling; renewable profile owner fencing/completion; independent concurrent Run updates and terminal/lost-ack behavior. Unit lifecycle tests retain complete rule/stage/binding and dry-run failure coverage. The CI persisted job includes the joint suite and rejects skipped Spark proofs.

### Querying declarations and observed execution

```sql
SELECT r.run_id, r.approval_id, p.table_id, p.roles, op.status,
       p.contract_id, p.contract_version, op.started_at, op.completed_at
FROM engineering.METADATA_PIPELINE_RUN r
JOIN engineering.METADATA_PIPELINE_DEFINITION d ON r.definition_id = d.definition_id
LATERAL VIEW explode(d.participants) declared AS p
LATERAL VIEW explode(r.operations) observed AS op
WHERE r.environment_name = 'DEV'
  AND array_contains(p.roles, split(op.operation_key, ':', 2)[0])
  AND substring(op.operation_key, instr(op.operation_key, ':') + 1) = p.participant;
```

Explode a collection at its actual grain before joining rule/profile facts; avoid multiplying counts across participant and diagnostic arrays. Use configured physical schema names. Observed historical participation still comes from Live Lineage.

## Deployment and migration contract

### Joint redesign rollout and reset policy

This procedure governs the native Registry/Definition/Run replacement. The existing Processing State cutover and earlier Run converter have distinct source/target layouts; neither migrates to this model. No standalone Preview converter is supplied.

1. **Inventory the deployed layout.** Record package versions and physical schemas for Registry, Activation State, Run and any affected participation table. Include exact reference counts, immutable approvals and finalized Tests, active/interrupted reservations, rebind barriers and profiling claims. Closed #1704 was not merged; an independently deployed copy requires separate reconciliation rather than assumed support.
2. **Stop and drain.** Disable schedulers and new Test/Live starts, registration/rebind and profiling acquisition. Let existing work finish and reconcile interrupted work against actual publication evidence. Never clear a reservation merely to make replacement possible. Back up all affected Delta tables at pinned versions, their referenced contracts/Agreements/results, and the matching reader package. Preserve Processing State and business-target recovery evidence.
3. **Fresh setup.** Create only the final canonical model with strict schema validation; then register, finalize a complete Test, explicitly approve and select Live. Registration, an empty Registry or an orphaned definition cannot authorize execution.
4. **Disposable Preview state.** If operators explicitly choose to discard state and establish that no approval history, run history or outstanding claims must be retained, archive it and deliberately recreate only the affected Preview tables. Re-register pipelines with a documented identity choice, rerun Test and reapprove. Do not erase Live metadata or reset Processing State/checkpoints/publication receipts. Setup never drops tables, deletes approvals, releases reservations or recreates incompatible canonical tables automatically.
5. **Retained Preview state.** Where approvals/history/claims matter, preserve the old stopped deployment until an explicit reviewed reconciliation maps every retained identity and content hash into the complete new model. Validate counts, exact contract/Agreement/Test links, whole-run outcomes, decision history, participants, ownership and claim ownership before cutover. Do not invent missing historical content, infer success or automatically transfer unverified active work. If correctness cannot be established, retain the old deployment/archive and resolve it before enabling Live; a disposable reset is not a substitute for preservation.
6. **Supported Live participation.** If the implementation changes or absorbs `METADATA_DATA_LINEAGE`, its migration must preserve existing rows automatically, validate repeat execution without duplicates or loss, and define cutover and rollback explicitly. No drop/rebuild instruction is acceptable for this Live table. If it stays unchanged, assert its schema and rows remain unchanged and document its observed-participation role.
7. **Physical cutover and validation.** Replace only validated affected layouts at their actual configured Lakehouse paths while stopped; catalogue registration alone is insufficient for path-based readers. Switch all affected readers/writers together. Setup rejects incompatible canonical schemas with a clear repair action. Differently named retired Preview tables may remain unused without blocking setup; use the retirement registry for actionable archival/cleanup notices. Never automatically delete them.
8. **Rollback.** Before new writes, restore the backed-up affected metadata and matching package as a unit. After new runs, approvals, claims or business publications, stop and reconcile the new records and recovery boundaries before rollback. An old metadata snapshot alone can erase history or authorize unsafe replay. Keep backups until deployment validation and the agreed retention boundary complete.

The physical model and retained-state transformation are specified below. The six supported Live tables, including Lineage, remain unchanged; no Live migration is required.

### Retained-state transformation and rollback boundary

For retained history, a reviewed reconciliation must preserve the exact source identities and required data; it is not an automatic converter or a reset instruction.

| Source | Complete target mapping / validation |
| --- | --- |
| Old Registry binding rows | One native registration per UUID/environment, original registration and latest audit intact; discard only the obsolete technical control row after backup. Validate active notebook uniqueness and canonical UUIDs. |
| Each old Run candidate | Seal one Definition for its exact pipeline/environment/content; transform roles, exact contract/version/hash references, settings and physical destinations. Reconstruct and compare original candidate identity. Partial historical configurations stay partial and nonapproving; never infer missing contracts or successful stages. |
| Old Run row | Same run/pipeline/environment/mode/start/end/status/audit, observed operation timing/stages and whole-run boundary. Move exact approval ID to `approval_id`; extract revision/profiling/failures/warnings. Preserve operation membership and permitted operational differences explicitly; validate whole logical reconstruction before any cutover. |
| Old approval manifest/history | Preserve decision ID, labels, audit, complete Test/diagnostic and Agreement links/hashes; reference the matching sealed definition. Embedded historical contract/Test/Agreement content must be reconciled with retained owner versions. Missing or mutated owner content requires verified restoration, not silently using current rows. Verify reconstructed decision digest and complete participant set. |
| Old environment authority | Preserve revision, selections, table contracts, readers/writer ownership, every independently retained decision, Live reservations/rebind barriers and profiling claims. New token establishes the stopped deployment's serialization boundary; source tokens remain in backup records. Active work is never transferred without reconciling exact target publication and ownership. |
| Live metadata and Processing State | No schema or row transformation. Preserve Catalogue, Lineage, profiles/frequencies, Steward/Agreement, frozen contracts, Guardrail Results, target markers, checkpoints and publication receipts at the correct recovery boundary. |

Verify counts and exact content, global identities, all references, rule coverage, complete Test outcomes, decision history, unique active bindings and physical destinations. Pin source Delta versions and retain the old reader package. If exact historical reconstruction cannot be established, keep the stopped old deployment/archive and resolve it before enabling Live. Disposable Preview state may be reset only under the explicit policy above. Setup rejects old or partially shaped Registry/Run/Definition schemas; it never adds columns to reinterpret them. Retired differently named Activation State may remain archived and produces advisory cleanup guidance.

Before new writes, rollback restores the backed-up affected table set and matching package together at the actual configured paths. After new decisions/runs/claims/publications, stop and reconcile their history and target/Processing State boundaries before rollback. Restoring metadata alone could erase approvals or authorize replay. No compatibility alias or legacy reader ships with the replacement.

## Validation and deployment checks

Run targeted lifecycle/public-contract tests and Ruff, compile/import checks, persisted Spark/Delta tests and strict MkDocs. Regenerate callable architecture, individual references, metadata explorer/diagram and glossary from authoritative source, then verify a clean second pass. Commit the architecture timestamp only with its changed contract. Compare the six Live schemas and Processing State with latest main; all remain identical. Exclude unrelated dashboards, release snapshots and notebook assets.

Local Spark/Delta 3.5.9/3.3.2 tests do not prove actual Microsoft Fabric behavior. Before deployment validate configured Lakehouse path cutover, native nested queries, actual concurrent authority/run writes, notebook deployment permissions and Warehouse transport/recovery. Recheck Day 1/Day 2 incremental reads, no-change/empty reruns, drift, failed writes and lost publication acknowledgements using the retained Processing State protocol. Maintainer review and CI remain required. Open one implementation PR; do not merge automatically.

## Retirement declarations and Live upgrade policy

`RETIRED_PREVIEW_METADATA_TABLES` remains the source for archival/cleanup notices. Activation State is explicitly marked as an unreleased Preview retirement because it was absent from historical manifests. Setup only probes retired names in configured Governance/Engineering schemas and never collects or migrates their history. Missing tables produce no warning; access/storage failures remain advisory. No retired table is deleted automatically.

`AGENTS.md` preserves all six supported Live schemas. Any future Live removal, rename or type change still requires a separately approved, tested automatic data-preserving migration with repeat safety and rollback. This implementation changes no Live layout and introduces no hypothetical Live conversion.
