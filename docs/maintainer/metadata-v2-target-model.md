# Pipeline activation metadata and controlled cutover

Pipeline governance uses a workspace pipeline deployment activation and an independent workspace/Table ID frozen Data Contract activation. Both live in the existing Engineering Pipeline Registry. There are still twelve canonical metadata tables.

## Current implementation and security boundary

The Registry has three scalar record types:

| Record type | Key | Responsibility |
| --- | --- | --- |
| pipeline_activation | Workspace + stable Pipeline ID | Deployed notebook, operation manifest, Agreement and deployment provenance |
| table_contract_activation | Workspace + Table ID | Exact globally frozen Contract ID/version/payload hash and reviewed physical destination JSON |
| control | central | Shared CAS token, transient policy leases and durable audit references |

The generated [Registry reference](../reference/metadata/metadata_pipeline_registry.md) lists physical columns and types. All canonical metadata fields are SQL endpoint compatible. Run and Catalogue JSON STRING columns retain their logical Python interfaces and expandable logical-schema documentation.

**Governed execution and pipeline activation remain unavailable until trusted deployment verification is proven in Fabric and integrated.** Neither an old successful Test, a migration candidate, a notebook-supplied Git SHA nor a raw activation field proves executing code identity. No deployment verifier is implemented; see the [provenance investigation and blocker](#deployment-provenance-investigation-and-blocker).

A new Contract can be frozen and activated independently through activate_data_contract, using the exact frozen identity, reviewed Registry token, explicit target workspace and Governance confirmation. Metadata write principals must be trusted under tenant permissions; confirmation is not authentication. Central Metadata routing remains separate from the target execution workspace. Each Contract activation pins its reviewed physical destination in destination_json; alias checks use that stored binding without requiring every notebook to configure foreign environments. Migration copies the exact destination from validated legacy ownership. Missing or malformed bindings fail closed. A later Catalogue/configuration move does not move the protected destination; reactivate explicitly after draining affected executions.

Consumers still need unambiguous, exact and effective Agreement context. Contract activation alone does not authorize data consumption. With pipeline activation blocked, new consumer provisioning that depends on active pipeline Agreement context also remains blocked.

## Execution modes and identity

| Mode | Publication | Contracts | Identity |
| --- | --- | --- | --- |
| Dry Run | Disabled; no durable Run, profile, checkpoint or Registry mutations | Optional preview | Explicit saved Pipeline ID or session-only UUID |
| Ungoverned | Existing publication/profiling/recovery behavior | No activated Contract required; protected targets and aliases are blocked | Explicit saved Pipeline ID required |
| Governed | Blocked pending trusted deployment assurance | Requires independently activated exact Contracts | Explicit saved Pipeline ID and verified activated deployment required |

A Pipeline ID is a lowercase logical UUIDv4, independent of workspace, Notebook ID and Run ID. Generate it once and retain it in version-controlled source. Registration recovery, approval/version history, selection pointers, workspace release revisions, ownership aggregates and rebind APIs are removed. setup_pipeline now accepts only pipeline_id and pipeline_mode.

Pipeline Run records keep their existing JSON operations, statuses, finalization and whole-row CAS. New nullable provenance columns are pipeline_activation_id, deployment_id, git_commit_sha, deployment_verification_status and run_schema_version. New records use version 2. Old/null versions use exactly the original hash-bearing fields, excluding additive null provenance. Unexpected non-null new provenance on old evidence is rejected rather than stripped to make a hash pass. Historical approval_id and activation_revision remain audit columns only.

## Atomic consistency and protection

Every Registry mutation pins the whole small table in a Delta transaction, reads and validates the unique control/business identities, checks the reviewed token, stages replacement files, and commits all rows and the new token together under Serializable isolation. Runtime writers never recreate missing control. Independent MERGEs or untracked overwrite are not used.

Blind appends and phantom activation inserts conflict with tracked whole-table replacement. A stale human review requires refresh and review. A unique mutation marker plus exact historical-version readback resolves lost acknowledgement; a newer unrelated head is not proof that a failed attempt should be replayed.

Governance changes first write a durable before/after audit snapshot, then reference it in the same Registry transaction. Committed receipts beside each archive preserve exact version/content proof beyond Delta log retention. Snapshots link to the previous committed governance archive. Setup repairs a missing post-commit receipt only from exact retained history; conflicting or missing evidence blocks the next mutation. An orphan archive does not prove a committed decision. Raw Metadata/Files writers remain trusted; use tenant permissions and retention to prevent alteration or deletion of referenced evidence.

Ungoverned target admission takes a minimal policy lease in the same CAS domain, held through run finalization. Contract activation drains affected leases, including physical destination aliases, before replacing policy. This lease changes neither publication identity nor processing progress. A crash leaves coordination closed: cancel/fence the old execution, reconcile its publication receipts and explicitly review recovery. Leases never expire merely because time passed. A metadata token is not a storage-enforced fence against a still-running privileged writer.

Multiple governed writers remain blocked at activation review, including Append, until writer-scoped progress/receipt work is implemented separately. Overwrite remains exclusive; Merge/Upsert aliases and declared-but-unenforced SCD scopes are rejected.

## Automatic Registry migration

Stop all old Registry writers, activation actions and pipeline executions before cutover. Drain and reconcile all old reservations; setup never clears them as a shortcut. Record the package revision, Delta table IDs/versions/properties and retention settings. Do not vacuum recovery files during acceptance.

setup_metadata_tables recognizes only the supported six-collection singleton schema. It:

1. Pins the exact Registry Delta snapshot and rejects duplicate/missing singleton, identities, unknown layouts/extensions and unresolved reservations.
2. Validates retained successful Test operations, rule-level diagnostics, Contract hashes and exact Agreement content, including nonselected approvals.
3. Checks every selection against its retained approval and notebook binding, then reconstructs exact table participation and compares it with old ownership. Missing, changed or conflicting evidence blocks migration.
4. Writes a checksummed durable archive outside canonical SQL tables containing the complete original row, all six collections, original schema, table metadata/version and registration IDs. Delta time travel alone is not the archive.
5. Maps selected pipeline and table Contract configurations to requires_reactivation candidates with null activation decision/provenance. Nonselected/retired registration and approval history remains in the archive, never active authority. No Git proof is fabricated.
6. Atomically replaces Registry schema/files and sets Serializable isolation while retaining table identity/properties and existing transaction facts. It verifies exact committed row contents/types. Repeat setup validates target state without changing tokens, IDs or audit.

Setup reports the archive/checksum, source and committed versions, saved Pipeline IDs and candidate identities. Structural readiness is separate from governed_execution.status, which remains blocked. All migration evidence and historical execution records remain inspectable. Malformed history must be restored/reconciled explicitly; no arbitrary latest-version fallback or automatic business replay is allowed.

Registry extensions or unsupported physical layouts require review before conversion. The migration deliberately pauses old Governed authorization; uninterrupted use of the old trust model requires retaining the previous package/schema until reviewed cutover is possible.

## Recovery and rollback

Before commit, source data is authoritative; failed staging/audit files cannot authorize anything. After commit, including lost acknowledgement, inspect the recorded transaction and rerun setup. Post-commit verification failure blocks readiness and requires inspection. No automatic restore occurs.

Clean orphan staging/audit files only after confirming no active attempt owns them and no committed transaction references them. Retain committed archives and receipts outside ordinary Delta-log/vacuum retention.

An offline rollback is permitted only with stopped writers and verified current heads matching the recorded upgrade boundaries, before subsequent governance or business changes. Restore a mutually compatible package/schema set; never restore only Registry while keeping incompatible writers. After subsequent writes, use reviewed forward reconciliation. Blind RESTORE can discard valid activations, Run evidence or Processing State progress.

## Preserved processing behavior

Full Read/Overwrite, watermark Source Observation incremental reads, Append, SCD1/SCD2, Source Drift, profiling, lineage, Run finalization, publication receipts, retry recovery and checkpoints retain their existing owners and algorithms. The order-independent prepared-business-row fingerprint remains unchanged, including suppression of an identical full overwrite.

This PR adds no partition fingerprinting, persisted row hashes, reporting projection tables, writer namespace redesign or Git deployment verifier.

## Validation and deployment gates

Local real-Delta tests cover stale/overlapping Registry changes, blind append phantoms, missing control, exact lost-ack recovery, independent Contract activation, target-policy leases, migration idempotence, tampered history rejection and historical Run hash stability. Publication regression tests cover current strategies and retry/fingerprint behavior.

Before Live rollout, a Fabric canary must validate the internal Delta transaction API/version, effective Serializable conflict behavior, archive permissions/retention, column mapping and actual SQL endpoint visibility. Passing local tests is not Fabric execution proof. The next deployment-assurance stage must prove trusted deployment barriers, dependency provenance and job/session correlation before enabling any Governed path.

## Deployment provenance investigation and blocker

**Decision on 3 November 2026: stop Governed enablement.** Investigation of the documented Microsoft Fabric interfaces has not established an independently trustworthy binding between approved deployment bytes, dependencies and the actual execution session before admission. This is a blocker for completing #1766, not a claim that Fabric can never support such a binding. No tenant Fabric validation was performed. The baseline includes merged #1768 (`c07817c23`) and #1770 (`3477c3123`).

### Documented capabilities and remaining gaps

| Microsoft interface | What it supplies | Why it does not establish the required binding |
| --- | --- | --- |
| [Get Notebook Definition](https://learn.microsoft.com/en-us/rest/api/fabric/notebook/items/get-notebook-definition) | Public notebook definition parts retrieved through Fabric REST, supporting a separate verifier identity | A saved definition is not documented as the immutable code revision consumed by a particular running session. Definition retrieval and job submission are separate operations. |
| [Run On Demand Notebook](https://learn.microsoft.com/en-us/rest/api/fabric/notebook/background-jobs/run-on-demand-notebook) | Job submission, session configuration, environment references and dependency paths | The documented request does not condition execution on an approved notebook content digest and complete dependency digest. Referencing a mutable item or path does not pin its bytes. |
| [Core Get Item Job Instance](https://learn.microsoft.com/en-us/rest/api/fabric/core/job-scheduler/get-item-job-instance) and [notebook job instance details](https://learn.microsoft.com/en-us/rest/api/fabric/notebook/background-jobs/get-notebook-job-instance%28beta%29) | Job identity/status; notebook details include Livy/application correlation and an execution snapshot URL | No reviewed response contract supplies a verified code-and-dependency manifest bound to that job before admission. A snapshot URL alone is not such a manifest. In high concurrency, the session creator item can differ from the executing item. |
| [NotebookUtils runtime context](https://learn.microsoft.com/en-us/fabric/data-engineering/notebookutils/notebookutils-runtime) | Read-only runtime properties including workspace, notebook, activity and environment identity | Read-only service properties aid correlation, but values forwarded through notebook Python code do not independently authenticate the caller of FabricOps or attest imported code. Reference run IDs are context-specific. |
| [Environment library management](https://learn.microsoft.com/en-us/fabric/data-engineering/environment-manage-library) | Full publishing creates a stable library snapshot; Quick publishing installs at session startup | Environment identity alone does not attest all executing bytes. Quick packages can override Full packages, and notebook Resources and inline installs are outside environment publishing. |

The missing guarantee is security-critical: verifying a saved notebook, starting a job, then verifying the saved notebook again does not prove the intervening executed revision. A change followed by restoration can pass both checks. Even an exact notebook digest would omit referenced notebooks, resources, wheels, transitive packages and session overrides unless those are also independently pinned and bound to the job.

No reviewed documentation establishes an atomic deployment-to-execution barrier or a pre-admission attestation covering that dependency closure. No authenticated Fabric tenant or independently operated verification authority was available to test one. An external deployment service with restricted permissions may be a future design, but it is not an implemented or validated security mechanism here. A service token returned to arbitrary notebook code would also need protection against replay from a different execution.

### Behavior while blocked

`build_governed_pipeline_plan` and `verify_governed_plan` in `src/fabricops_kit/activated_pipeline/shared.py` reject execution unconditionally. `setup_pipeline()` and the persistence checks used by pipeline reads, writes and finalization retain this gate. The activation widget reports verification unavailability; editing deployment IDs, verification flags or in-memory plans cannot satisfy the gate. Historical approval records and migration candidates remain non-authorizing.

Separate workspace/Table ID Contract activation, exact frozen Contract validation, Agreement checks and Registry CAS remain as implemented in #1770. Dry Run and Ungoverned retain their current behavior. Shared-target Append support and writer-scoped progress/receipts are **not implemented by this investigation**; no concurrent-writer safety claim follows from it. Overwrite and unsupported concurrent modes retain existing restrictions. Fingerprints, checkpoints, publication recovery and Run metadata are unchanged.

### Evidence required before resuming implementation

1. Identify a supported Fabric mechanism or independently operated authority that authenticates the actual execution and binds its workspace, Notebook ID, logical Pipeline ID, job/activity and session to approved notebook and dependency bytes. Record the API contract, trust principals, permissions and retention requirements. Evidence must exist before Governed admission, not only after publication.
2. Demonstrate how edits, dependency replacement, session reuse, replay and direct public API calls cannot bypass that binding. The notebook must not hold authority to mint its own verification or modify the verifier, Registry authority or retained verification records.
3. Specify how that independently verified deployment binds to the current pipeline activation while separate Contract activations pin exact frozen ID/version/hash. Pin those versions throughout execution; reject missing, stale, ambiguous, revoked or mismatched authority. Retained historical approvals cannot substitute for current activation.
4. Only after proving the boundary, implement admission and compatible Append publication with pipeline/source/target-scoped progress, operation-scoped transaction identities and receipts, and finalization ownership checks. Add the requested unit, contract and real Delta concurrency/recovery tests. Successful Governed execution cannot be tested honestly against the current blocked implementation.

### Required Fabric canaries

Run in disposable workspaces with synthetic data and independently captured service responses. Record tenant runtime/package revisions, API versions, principals, job/session identities and exact Delta table versions; keep secrets out of retained reports.

| Canary | Required result before enabling the corresponding capability |
| --- | --- |
| Deployment provenance | Independently inspect the executed revision and dependency closure. Change notebook content, referenced notebook, resource and wheel separately, including change-and-restore between checks. Every unapproved execution is denied before admission. If evidence is unavailable until completion, keep Governed blocked. |
| Runtime identity | Exercise scheduled, API, interactive, reference and reused high-concurrency sessions. Substitute workspace, Notebook ID, Pipeline ID, job ID and session ID; replay evidence from another execution. Reject every mismatch without relying on notebook-reported flags or exit values. Unsupported contexts remain blocked. |
| Activation and finalization | Race pipeline/Contract reactivation against admission and an active run; verify exact version pinning and stale-review rejection. Fail transformation/publication and attempt forged-plan finalization. No failed execution receives successful finalization or advances another writer's progress. |
| Delta transactions and recovery | Once Append multiwriter support exists, race two pipelines against one target and verify each retains independent progress and receipts. Retry each operation, inject commit conflicts and drop commit acknowledgements. Reconcile exact transaction/target markers before accepting progress; verify no duplicates or cross-writer finalization. Confirm conflicting Overwrite, Merge, SCD1 and SCD2 admission remains rejected. |
| SQL analytics endpoint | After supported metadata setup and representative runs, query the actual endpoint for Registry/Run/Catalogue/Processing State scalar columns and JSON values. Check discovery delay, Unicode, long payloads, timestamps and visibility after migration/commit; do not assume Spark readback proves SQL availability. |

Local unit or Spark/Delta results cannot satisfy these Fabric canaries. Until the provenance canaries establish the trust boundary, preserve the unconditional Governed gate and report this stage as blocked.

## Processing State upgrade

This existing cutover procedure applies only to deployments still using the pre-#1698 layout: `METADATA_SOURCE_OBSERVATION` → `METADATA_PROCESSING_STATE`. There is no legacy alias or fallback reader. Setup permits the old physical table to remain, including alongside the canonical table, and returns an advisory retirement alert. A fresh canonical table does not establish valid operational progress for populated targets. `observation_status` and `publication_payload_json` are removed. Old rows must **not** be additive-evolved into typed progress. Setup and runtime still reject an incompatible layout under the canonical `METADATA_PROCESSING_STATE` name, including an empty table. No compatibility reader, automatic migration, reset, or discard is performed.

1. Stop/drain writers and take a durable backup of the existing `METADATA_SOURCE_OBSERVATION` table plus the code/version needed to read it. Retain target data, target audit markers, and Delta history. Inventory all source/target/environment relationships, accepted progress and unresolved publications.
2. Reconcile every staged publication against the physical target before cutover. In the old layout, `committed` corresponds to `incremental_checkpoint`; `drift_committed` to `drift_baseline`; `publication_observed`/`publication_committed` to staged/committed receipts. Old target-bound `observed`/`drift_observed` rows are staged candidates, never automatically accepted checkpoints. Decode and deduplicate exact receipt JSON into typed receipt rows; retain originating run/audit identities. Column/type evidence missing from old records must be supplied from the verified original processing definition, not inferred silently from current configuration.
3. Choose an explicit, reviewed cutover: an offline migration into the complete canonical schema with deterministic IDs and validated receipt references; or a reset only after reconciling/archiving progress and preparing a governed target rebuild or idempotent replay. A populated append target without an accepted baseline is intentionally rejected. Dropping only the metadata table and continuing incremental append is unsafe.
4. For a deliberate reset, preserve a durable archive of the reconciled old Preview table, run `setup_metadata_tables()` to create `METADATA_PROCESSING_STATE`, then execute the reviewed target rebuild/replay. This Processing State cutover does not replace or reset Live metadata, Pipeline Run, Registry or Activation State; use the separate joint-redesign procedure for any approved pipeline metadata replacement. For migration, populate `METADATA_PROCESSING_STATE` with the validated complete schema, then archive/remove the old physical name and run setup validation before restarting writers. A physical rename alone is valid only after verifying the complete new schema, record-key uniqueness, receipt references and empty-header semantics. Older empty-source sentinels must be reconciled against real NULL/empty-string partitions before transformation; do not infer whether they represent a removed partition or a dataset header. Older layouts require the field transformation above. Both physical names may remain during reconciliation; the retired name produces an advisory alert and is never read by runtime.
5. Validate first/subsequent incremental execution, unchanged/empty reads, Source Drift baseline decisions, lost-acknowledgement retries and environment/target isolation. Keep the backup until these checks finish. Rollback requires stopping writers and restoring both a compatible code/schema pair and a reconciled checkpoint/target boundary; restoring metadata alone after new publications is unsafe.

The current exact receipt includes its physical strategy. Old Delta commit metadata cannot be rewritten into new physical proof: retain old receipts for reconciliation, and use a reviewed target rebuild/replay to establish new-format receipts wherever automatic retry verification is needed. Migrating accepted progress alone does not retrofit old physical receipts. Recovery restores Processing State; replay the exact prepared Write if separate Catalogue or Lineage finalization also needs retry.

No automatic conversion is supplied because old rows can lack watermark types, column identities or exact physical publication proof. Operators decide archival retention after reconciliation. Existing Processing State tests are regression requirements for the joint redesign; their local results do not validate an actual Fabric Warehouse deployment.
