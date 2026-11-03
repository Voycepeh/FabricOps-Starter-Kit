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

**Governed execution and pipeline activation remain unavailable until trusted deployment verification is proven in Fabric and integrated.** Neither an old successful Test, a migration candidate, a notebook-supplied Git SHA nor a raw activation field proves executing code identity. This PR introduces no verifier, attestation service or custom notebook hashing.

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

## Processing State upgrade

This existing cutover procedure applies only to deployments still using the pre-#1698 layout: `METADATA_SOURCE_OBSERVATION` → `METADATA_PROCESSING_STATE`. There is no legacy alias or fallback reader. Setup permits the old physical table to remain, including alongside the canonical table, and returns an advisory retirement alert. A fresh canonical table does not establish valid operational progress for populated targets. `observation_status` and `publication_payload_json` are removed. Old rows must **not** be additive-evolved into typed progress. Setup and runtime still reject an incompatible layout under the canonical `METADATA_PROCESSING_STATE` name, including an empty table. No compatibility reader, automatic migration, reset, or discard is performed.

1. Stop/drain writers and take a durable backup of the existing `METADATA_SOURCE_OBSERVATION` table plus the code/version needed to read it. Retain target data, target audit markers, and Delta history. Inventory all source/target/environment relationships, accepted progress and unresolved publications.
2. Reconcile every staged publication against the physical target before cutover. In the old layout, `committed` corresponds to `incremental_checkpoint`; `drift_committed` to `drift_baseline`; `publication_observed`/`publication_committed` to staged/committed receipts. Old target-bound `observed`/`drift_observed` rows are staged candidates, never automatically accepted checkpoints. Decode and deduplicate exact receipt JSON into typed receipt rows; retain originating run/audit identities. Column/type evidence missing from old records must be supplied from the verified original processing definition, not inferred silently from current configuration.
3. Choose an explicit, reviewed cutover: an offline migration into the complete canonical schema with deterministic IDs and validated receipt references; or a reset only after reconciling/archiving progress and preparing a governed target rebuild or idempotent replay. A populated append target without an accepted baseline is intentionally rejected. Dropping only the metadata table and continuing incremental append is unsafe.
4. For a deliberate reset, preserve a durable archive of the reconciled old Preview table, run `setup_metadata_tables()` to create `METADATA_PROCESSING_STATE`, then execute the reviewed target rebuild/replay. This Processing State cutover does not replace or reset Live metadata, Pipeline Run, Registry or Activation State; use the separate joint-redesign procedure for any approved pipeline metadata replacement. For migration, populate `METADATA_PROCESSING_STATE` with the validated complete schema, then archive/remove the old physical name and run setup validation before restarting writers. A physical rename alone is valid only after verifying the complete new schema, record-key uniqueness, receipt references and empty-header semantics. Older empty-source sentinels must be reconciled against real NULL/empty-string partitions before transformation; do not infer whether they represent a removed partition or a dataset header. Older layouts require the field transformation above. Both physical names may remain during reconciliation; the retired name produces an advisory alert and is never read by runtime.
5. Validate first/subsequent incremental execution, unchanged/empty reads, Source Drift baseline decisions, lost-acknowledgement retries and environment/target isolation. Keep the backup until these checks finish. Rollback requires stopping writers and restoring both a compatible code/schema pair and a reconciled checkpoint/target boundary; restoring metadata alone after new publications is unsafe.

The current exact receipt includes its physical strategy. Old Delta commit metadata cannot be rewritten into new physical proof: retain old receipts for reconciliation, and use a reviewed target rebuild/replay to establish new-format receipts wherever automatic retry verification is needed. Migrating accepted progress alone does not retrofit old physical receipts. Recovery restores Processing State; replay the exact prepared Write if separate Catalogue or Lineage finalization also needs retry.

No automatic conversion is supplied because old rows can lack watermark types, column identities or exact physical publication proof. Operators decide archival retention after reconciliation. Existing Processing State tests are regression requirements for the joint redesign; their local results do not validate an actual Fabric Warehouse deployment.
