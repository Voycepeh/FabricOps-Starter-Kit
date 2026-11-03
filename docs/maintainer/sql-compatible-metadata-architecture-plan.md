# Simplify Pipeline Registry and Governed execution

Planning proposal for PR #1766: activation authorizes a deployed pipeline version; an independently activated Data Contract governs each environment and Table ID.

## 1. Recommendation and review boundary

**Replace the previous hybrid Registry/reporting architecture in this PR.** Keep the three execution modes, remove registration/approval/selection lifecycles from operational authority, and store one current pipeline activation per `(workspace_id, pipeline_id)`. Keep SQL-compatible JSON for operation configuration and runtime coordination. Add **no physical reporting tables** initially: Power Query can expand JSON into model-only operation, source and stage tables.

Recommend retaining **one transactional governance store**, the existing `METADATA_PIPELINE_REGISTRY` Delta table, with two kinds of business record: pipeline activation and table-contract activation. An internal control row coordinates mutations and live executions in that same table. This is a deliberate replacement of the singleton's six collections, not their redistribution into six tables. The user-facing model is:

1. Develop in Dry Run or Ungoverned using a stable Pipeline ID.
2. Freeze and activate a table's Data Contract for an environment.
3. Deploy a known pipeline artifact and activate that deployment for the environment.
4. Governed runs pin both activations, verify the deployment, enforce the contracts and publish safely.

**Code verification is conditional, not solved by a commit field.** The Microsoft interfaces audited here expose saved definitions, Git synchronization state and runtime identity, but do not document an attestation binding executing notebook bytes to a Git SHA. Recommend a trusted CI/CD deployment and externally gated batch execution model in a protected production workspace. Validate its assumptions in Fabric before enabling Governed publication. If the required assurance cannot be established, Governed must remain unavailable for that deployment; do not label a self-reported SHA “verified.” No custom notebook hashing framework is proposed.

This document is an architecture and migration plan, not implementation approval. Only this Markdown file and PR metadata are updated. No runtime/schema code, business or metadata tables, notebook templates, generators, dashboard artifacts or release snapshots change now.

## 2. Verified baseline and current dependencies

### Sources and revision

Audited latest fetched `main` on 3 November 2026: [`c6bda1d5e0fa259cf18171edac39f2f47f8ee086`](https://github.com/Voycepeh/FabricOps-Starter-Kit/commit/c6bda1d5e0fa259cf18171edac39f2f47f8ee086). This supersedes the earlier audit of v0.3.1 preparation. Read `AGENTS.md`, the repository documentation-maintenance skill, canonical schema source, authoritative writers/readers and tests. Current conventions describe the implemented six-collection authority; changing that behavior requires the explicit breaking migration below, not preserving it as a new architecture constraint.

Also inspected [dashboard PR #1764](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1764), head `b5965f44671f6ee4786a557f5ed5c001af518b47`: its generator, source-to-model mapping and Registry/Run TMDL partitions. It remains open at this audit. The dashboard uses Import, twelve canonical source tables and semantic dimensions; it creates no persisted reporting copies. Its explicit SQL projections currently omit nested Registry/Run fields and Catalogue structs. Current-source `frozen` status is not proof of activation.

### Current lifecycle and replacement dependency matrix

Paths in this document are relative to repository root. Function names identify source owners rather than relying on generated documentation.

| Current state or boundary | Actual writers and readers | Replacement decision |
| --- | --- | --- |
| `registrations` | `pipeline/shared.py`: `resolve_pipeline_registration`, `read_pipeline_registry`, `commit_pipeline_registration`, `start_pipeline_session`; `activated_pipeline/shared.py`: Test review and Governed notebook-binding checks | Remove permanent registration authority. Stable Pipeline ID comes from version-controlled pipeline metadata; active deployment comes from the pipeline activation row |
| `approvals` and version-label history | `tested_pipeline_run`, `testing_run_evidence`, `approval_record`, `review_pipeline_release`, `approve_pipeline_release`, `activation_version`; activation widget; retained Test/Agreement/Contract hash verification | Replace with one direct activation decision, its deployment provenance and audit. Retain historical decisions/evidence, not an operational approval lifecycle |
| `selections` | `read_pipeline_authority`, `workspace_activation`, activation widget and Governed plan construction | Remove. The current pipeline activation row is the selection; no second pointer from selection to approval |
| `revisions` | Activation computes a workspace digest; admission, verification, release and rebind pin it | Remove workspace release-history entity. Keep transaction token for stale writes and per-record activation IDs for run pinning; unrelated lease changes do not invalidate a run |
| `table_ownership` | `activation_impact` derives one writer, readers, binding and Contract; `build_live_pipeline_plan`, `verify_live_plan`, Ungoverned target checks and `resolve_approved_consumer_contract` depend on it | Remove persisted writer/readers aggregate. Derive participation from active operation configurations; use independent table-contract activation for the one active Contract |
| `reservations` | Governed admission/release and registration rebind use the shared CAS; activation checks affected running executions | Keep only current run/admission and publication coordination needed for safety, in one internal JSON value. Remove rebind lifecycle: deployment replacement is activation replacement after drain |
| Singleton CAS | `authority_records`, `validate_authority_collections`, `pipeline_authority_row`, `commit_pipeline_authority` in `activated_pipeline/shared.py` | Replace the physical singleton contract with a transaction over the one Registry table. Preserve atomic stale-update rejection, exact lost-acknowledgement confirmation and fail-closed missing/duplicate control |
| Actual Run facts | `pipeline_run_row`, `validate_pipeline_run`, `_read_pipeline_run_rows`, `_merge_pipeline_run_row`, `persist_pipeline_run`, `publish_pipeline_testing_results`, `finalize_pipeline_run`; setup/finalization, widget and contract runtime views | Keep one authoritative row per Run and atomic parent/operation outcomes. Convert its three nested physical fields to JSON strings; retain historical Test records and hashes |
| Profiling eligibility | `profiling_completion_history` Spark-explodes authoritative Run profiling and checks existing Profiled/Frequency snapshots; `record_profiling_outcome` persists completion markers | Keep authoritative source and scheduling semantics. Decode Run JSON with typed Spark expressions; do not authorize/schedule from Power BI-expanded tables |
| Publication/checkpoints | `PublicationBatch`, `_latest_source_target_observation`, `_previous_source_target_observation`, `_find_applied_publication`, `_recover_completed_source_observations`, `stage_pipeline_write_observations`, `commit_pipeline_write_success` | Preserve staged receipts, physical verification and accepted progress. Fix writer-scope assumptions before allowing multiple append writers; section 7 |
| Catalogue | `pipeline_write._persist_target_processing`, Catalogue profile/upsert/grain writers; `catalogue_authored_processing`, `check_source_drift`, contract draft seed and contract widget | Preserve existing fields, schedules, candidate discovery and processing meaning. Convert three physical structs to JSON and update every direct consumer/literal writer |
| Consumer contracts | `data_agent/shared.py` calls `resolve_approved_consumer_contract`; `data_contract/shared.py` loads pipeline usage for authoring | Resolve the independently active table Contract; preserve explicit Agreement context and ambiguity rejection. Do not infer consumer authorization from any writer's activation |
| Metadata routing | `metadata_records`, activation widget and contract authoring now distinguish target workspace from central `metadata_workspace_id` | Preserve the latest-main central Metadata routing fix. Environment workspace, deployment workspace and physical destination are not interchangeable |

Current `METADATA_DATA_CONTRACT` stores globally frozen versions with `evidence_workspace_id`, **not** independent environment activation or a global `is_active` field. Today's active Contract is inferred from approved pipeline participation. `activation_impact` currently rejects a second writer universally. The public setup modes are already Dry Run, Ungoverned and Governed; old `testing` plans remain recognized by Run/finalization code, but the current public setup does not offer a new Testing mode. Do not recreate a Testing lifecycle to activate the new model.

The repository release workflow builds versioned wheels and SHA256 checksums; it does not currently establish a tenant-specific pipeline notebook deployment attestation. That CI/CD integration is an implementation prerequisite, not an existing capability.

### Current physical schema inventory

There are twelve canonical metadata tables and twelve top-level native nested columns, with no additional top-level Map/Array/Struct found in their canonical schemas:

| Table and physical fields | Current type | Target decision |
| --- | --- | --- |
| Registry: `registrations`, `revisions`, `approvals`, `selections`, `table_ownership`, `reservations` | Six `array<struct<...>>` columns; inner warnings/readers/tables/destinations also contain arrays/structs | **Remove from active schema after verified archival/mapping.** Replace with scalar activation records and one JSON coordination field, not six renamed JSON collections |
| Run: `operations`, `profiling`, `failures` | Three `array<struct<...>>`; operations contain destination, stages and source associations; profiling contains physical descriptor | **Keep / Convert** physical types to validated `string`; keep logical dictionaries/lists and historical evidence |
| Catalogue: `load_strategy_parameters_json` | Struct with watermark/effective columns and key/tracked arrays | **Keep / Convert** to validated JSON string |
| Catalogue: `scheduled_refresh_json` | Struct with status, schedule array and local-time arrays | **Keep / Convert**; successful writes still discover/persist schedules; current contract authoring strips them from contract payloads |
| Catalogue: `profile_key_candidates_json` | Struct with discovery status/width, candidate arrays and long/double metrics | **Keep / Convert**; preserve widget discovery and large counts |

Keep existing relational Steward, Agreement, Contract, Profiled, Frequency, Lineage, Guardrail Results, Processing State and Data Access designs. Contract payload and other existing JSON strings remain scalar. Preserve unrelated extension columns; report any unsupported nested extensions rather than silently rewriting user data or claiming full SQL visibility.

## 3. Three execution modes and identity

### Responsibilities

| Capability | Dry Run | Ungoverned | Governed |
| --- | --- | --- | --- |
| Transformations and physical reads | Yes | Yes | Yes |
| Publish business data | No | Yes | Yes |
| Profiling | Yes, preview/in-memory as today | Yes, persisted under current policies | Yes, persisted under activated Contract policies |
| Require Data Contract | No | No | Yes, independently active for every participating Table ID |
| Guardrails | Optional selected Contract preview; report blocking outcomes without implying publication permission | No activated-Contract enforcement; retain existing structural/publication safety checks | Enforce exact pinned Contract; block noncontinuing results before publication |
| Pipeline activation | No | No | Required for workspace + Pipeline ID |
| Verified deployment | No | No | Required, subject to the externally verified assurance gate in section 5 |
| Operational persistence | Preserve current Dry Run prohibition on Registry, Run, checkpoint and profile mutations | Run, profiles, Catalogue, Lineage and Processing State as applicable | Same operational facts plus pinned activation/deployment identities |

No target-publication or checkpoint advancement may occur from Dry Run. Successful writes still do not prove whole-notebook completion; retain explicit `finalize_pipeline`, incomplete/failed outcomes and safe failure summaries. Arbitrary user Python/SQL with direct write credentials cannot be sandboxed by a mode flag: these guarantees apply to FabricOps-controlled publication. Production permissions and deployed code must prevent bypass.

**Keep the existing Ungoverned protection by default:** it cannot write a table reserved for governed publication in that environment. Extend the check to an active table-contract binding as well as governed pipeline participation, and compare physical destination aliases. This does not require Ungoverned to have a Contract; it prevents it bypassing governance on a protected target. Allowing Ungoverned writes to protected targets would be a separate weakening requiring explicit approval.

### Identity semantics and deliberate API changes

- **Pipeline ID:** existing lowercase UUIDv4 logical identity, generated once and stored in version-controlled pipeline metadata/source. It survives promotion, redeployment and notebook ID changes. It is not derived from Git commit, workspace, read/write combination or notebook ID.
- **Notebook ID:** physical deployment identity within a Fabric workspace. Replacing it requires new activation, not permanent registration/rebind history. One notebook may contain multiple explicitly identified pipeline entrypoints; do not impose universal notebook-ID or Read/Write-combination uniqueness across pipelines.
- **Activation ID:** new immutable UUID for one committed pipeline or table-contract activation. Replacing current state changes this ID; leases pin it. This is not a separately approved pipeline version lifecycle.
- **Git commit:** repository-qualified full object ID recorded by trusted CI/CD. A moving branch/tag or notebook-supplied string is not proof. **Deployment ID** identifies the CI/CD release into Fabric, including its environment/dependency artifact.
- **Run ID:** execution identity allocated once; independent of activation ID and Fabric job/activity/reference IDs. Persist their correlation where available; do not assume runtime `currentRunId` exists in every context.

Recommend requiring the stable Pipeline ID for persistent Ungoverned and Governed calls. Dry Run may allocate a session-only ID. Remove registration-only `new_pipeline`, `previous_workspace_id`, `previous_notebook_id` and rebind outputs in the approved breaking release; provide a one-time migration report listing existing IDs to put into source. Do not replace registration history with automatic re-registration under a new name. This loses automatic recovery of an unactivated notebook's UUID from Registry and must be approved/documented.

## 4. Minimal Registry and independent Contract activation

### One physical table, three record kinds

Retain `engineering.METADATA_PIPELINE_REGISTRY` at its configured location, replacing its schema through the controlled migration. Governance authorization is a service/permission responsibility, not a consequence of the physical Engineering schema name. Keep twelve canonical tables overall.

| `record_type` | Logical grain / record key | Authority |
| --- | --- | --- |
| `pipeline_activation` | One current row per `(workspace_id,pipeline_id)`; deterministic `record_id` from kind and those IDs | Activated deployment and operation configuration |
| `table_contract_activation` | One current row per `(workspace_id,table_id)`; deterministic `record_id` from kind and those IDs | Exact active frozen Contract, independent of any pipeline |
| `control` | Exactly one row, `record_id='central'` | Global transaction token and transient leases only |

Using the same Delta table is intentional: independent Contract activation is a separate governance action, while its publication, compatibility checks and execution drain must be atomic with pipeline admission. A separate Contract-activation table would require a new cross-table protocol. Do not modify globally frozen Contract rows to mark environment activation, and do not duplicate Contract definitions in Registry.

The sparse row kinds are a tradeoff: SQL/Power BI filters `record_type` into two business datasets; internal control is hidden. They add two business entities and one implementation record, not six lifecycle collections. If maintainers reject mixed record kinds, reconsider an explicitly coordinated authoritative store; do not split them into independently maintained Delta tables as a cosmetic simplification.

### Proposed physical columns

Every field below is SQL endpoint compatible. Fields unused for a record kind are SQL null. The application enforces required fields and logical PKs/FKs; Lakehouse SQL constraints do not enforce them.

| Fields | Spark physical type / SQL endpoint type | Applicable rows / meaning |
| --- | --- | --- |
| `record_id`, `record_type` | `string` / `varchar` | All; stable unambiguous row identity and kind |
| `workspace_id` | `string` / `varchar` | Both business kinds; canonical execution environment key |
| `pipeline_id`, `pipeline_name` | `string` / `varchar` | Pipeline; logical identity and display name |
| `table_id` | `string` / `varchar` | Table-contract; logical governed table |
| `activation_id`, `status` | `string` / `varchar` | Business kinds; status `active` or `requires_reactivation`. Migration candidates never grant authority |
| `activated_at`, `activated_by` | `timestamp` / `datetime2`; `string` / `varchar` | Business kinds; original governance decision audit; null for an unactivated migration candidate |
| `notebook_id`, `git_repository`, `git_commit_sha`, `deployment_id` | `string` / `varchar` | Pipeline; deployment workspace is `workspace_id` initially; cross-workspace notebook execution requires separate approved support |
| `deployment_manifest_uri`, `deployment_manifest_sha256`, `verification_method` | `string` / `varchar` | Pipeline; immutable trusted CI/CD artifact reference/digest and verified method, not a caller assertion |
| `operations_json` | `string` / `varchar` | Pipeline; one ordered validated array of read/write descriptors; no duplicate source/target lists |
| `agreement_id`, `agreement_version`, `agreement_sha256` | `string` / `varchar` | Pipeline; preserve exact current Agreement/effectiveness safeguards rather than silently removing them |
| `contract_id`, `payload_sha256` | `string` / `varchar` | Table-contract; existing exact frozen version reference and immutable payload hash |
| `contract_version` | `integer` / `int` | Table-contract; exact version |
| `token` | `string` / `varchar` | Control only; opaque CAS token changed on every Registry mutation |
| `leases_json` | `string` / `varchar` | Control only; validated transient coordination array, initially `[]` |
| `last_governance_change_id`, `last_governance_audit_uri` | `string` / `varchar` | Control; most recent committed governance change and its durable audit snapshot; lease churn does not replace these |
| `migration_archive_uri`, `migration_archive_sha256` | `string` / `varchar` | Control; immutable pre-cutover evidence archive, not runtime authority |
| `schema_version` | `integer` / `int` | All; explicit canonical layout |
| Existing eight audit fields | `_committed_at:timestamp`, others `string` | All; preserve configured audit owner and physical-routing semantics |

Do not store pipeline version label history, `approval_id`, `testing_run_id`, workspace revision, copied Contract payloads, or permanent registration arrays in new active authority. Optional CI test evidence belongs in the deployment manifest and activation audit, not a new approval entity.

### Logical operation configuration in `operations_json`

Each descriptor contains `operation_key`, `table_id`, `pipeline_role` (`source`/`target`), resolved `destination` (`workspace_id`, `item_id`, `kind`, nullable `schema`, `table_name`), nullable `read_mode`, `write_mode`, `query_sha256`, `incremental_target_table_id`, ordered `source_table_ids`, and a bounded `write_scope` declaration when required. Use existing operation-key and one-operation-per-table-role validation initially. Identical configurations across different Pipeline IDs are permitted.

Read query hashes retain current integrity checks without storing SQL text. Source associations mean pipeline participation, not proven transformation lineage. Processing keys/watermark/history rules remain in the frozen Contract, not copied into the pipeline record. Descriptor write strategy must agree with that Contract. No complete arguments/settings snapshot or generic configuration fingerprint is introduced.

`write_scope` is either absent (whole target) or a validated declarative scope supported by the writer; an arbitrary SQL predicate or engineer assertion is not accepted as proof of disjointness. Initially scoped Merge/SCD multiwriter activation is blocked until the writer can enforce that scope on both incoming rows and target mutation. Declaring a field does not create scoped-write support.

### Contract activation and enforcement

Freeze remains global and immutable in `METADATA_DATA_CONTRACT`. Activate a Contract by publishing/replacing its table-contract row for exactly one environment/Table ID. No pipeline need be active to activate a Contract. Activating a pipeline requires already active Contracts for all participating Table IDs and compatible operation definitions.

Contract activation reviews all affected active pipeline descriptors, drains their pinned runs and validates compatibility with the new frozen processing/Guardrail expectations. If incompatible, require a coordinated transaction replacing/deactivating the affected pipelines; never silently switch their write strategy. A compatible Contract activation need not create a new pipeline deployment activation, but subsequent runs pin the new exact Contract activation. Current in-flight runs cannot observe a changed Contract.

For every Governed read/write, use the run-pinned Contract version/hash and resolved destination; require publication configuration to match the activated descriptor. Contract payloads remain immutable and separately readable, so no cross-table transaction is required to publish a pointer to an already frozen version. Concurrent draft editing cannot affect it. Protect deletion/change of referenced frozen Contracts/Agreements through permissions, validation and retention.

Consumer/Data Agent resolution uses the active table-contract row, not an arbitrary writer's Contract. Preserve the existing Agreement/effectiveness requirement: a consumer must have unambiguous applicable Agreement context; multiple pipeline Agreements must not be treated as interchangeable. Keep ambiguity fail-closed and design any new explicit consumer-Agreement input as a separately reviewed public contract change.

## 5. Git/deployment verification: evidence, limits and smallest mechanism

### What Microsoft's documented interfaces establish

| Capability audited | Establishes | Does not establish |
| --- | --- | --- |
| [Notebook source control and deployment](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-source-control-deployment) | Versionable notebook source; dependent bindings may be remapped during deployment | A commit string embedded in code is not execution attestation; raw source bytes may legitimately differ because of environment binding metadata |
| [Git Get Status](https://learn.microsoft.com/en-us/rest/api/fabric/core/git/get-status) | Workspace sync head and item change/conflict observations; requires contributor-or-higher role and configured Git credentials | A returned `workspaceHead` is not an immutable per-run notebook revision. `remoteCommitHash` is branch state, not the deployed execution version |
| [Get Notebook Definition](https://learn.microsoft.com/en-us/rest/api/fabric/notebook/items/get-notebook-definition) | Saved public notebook definition in native Git source or ipynb format | Executing kernel contents, imported modules or a no-change guarantee after the request. It requires read/write notebook permissions, making an external verifier preferable to granting these privileges to every run |
| [NotebookUtils runtime context](https://learn.microsoft.com/en-us/fabric/data-engineering/notebookutils/notebookutils-runtime) | Read-only notebook/workspace/environment identity and context-dependent run/activity correlation | No documented Git commit/content attestation property. `currentRunId` is documented for reference runs, not a universal job identifier |
| [Run On Demand Item Job](https://learn.microsoft.com/en-us/rest/api/fabric/core/job-scheduler/run-on-demand-item-job) | Starts a job against an item; [notebook API guidance](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-public-api) describes execution settings and monitoring | Audited contract has no documented “execute notebook at this Git commit” selector or signed running-code digest. Caller-overridden execution settings can change the effective environment |
| [Environment Git and deployment](https://learn.microsoft.com/en-us/fabric/data-engineering/environment-git-and-deployment-pipeline) | Versionable libraries/runtime settings; Git sync stages environment changes which require publishing | Git sync alone does not prove the published execution environment matches that commit |
| [Manage environment libraries](https://learn.microsoft.com/en-us/fabric/data-engineering/environment-manage-library) | Full publish produces a stable library snapshot for new sessions; Quick/inline installs can change effective packages | An attached Environment ID alone does not prove loaded dependency versions or prevent a notebook override |
| [Notebook permissions/modes](https://learn.microsoft.com/en-us/fabric/data-engineering/how-to-use-notebook) | Read/execute can be separated from write; effective workspace/item permissions determine capabilities | “Run only” UI mode does not remove inherited Contributor write access or protect from administrators |

These are documentation observations checked on 3 November 2026, not tests in the user's tenant. **Inference:** there is no established native proof of exact running notebook bytes in the interfaces audited. This is not a claim that no other Fabric capability could ever supply one.

### Recommended deployment assurance contract

Use existing Git/CI provenance and native Fabric operations instead of an in-notebook hashing service:

1. CI resolves a protected repository commit and deployment artifact. Its retained manifest records Pipeline ID, commit/repository, notebook artifact/entrypoint, target workspace/item, operation manifest, published Environment identity, exact FabricOps wheel version/checksum and all custom module/resource/dependent-notebook artifact versions.
2. A trusted deployer deploys and checks the resulting saved item against its known deployment output using the chosen supported deployment/Git tools. For a Git-synchronized production workspace, record its workspace head and item-change state after synchronization; do not equate a moving remote branch head with the activated commit. For a deployment-pipeline/import target, require the deployer's verified output/provenance; Git status of a different source workspace is insufficient.
3. Store the immutable manifest in CI artifact storage or a protected deployment artifact location. Governance reads it through the trusted producer and binds its digest/reference in activation. A manifest written by the notebook or a URI/digest pasted by an engineer is insufficient.
4. Allow Governed batch runs only through a trusted launcher that verifies activation/deployment and relevant current saved state before submission. Serialize deploy/update and execution admission through the **same externally enforced deployment barrier**; drain running/queued jobs before changing notebook or dependencies. Every deployment writer must honor the barrier. A preflight API call alone has a time-of-check/time-of-use race.
5. Use a fresh, noninteractive execution session with the approved published environment; disable reused interactive/high-concurrency sessions for the initial assurance model. No unpinned `%pip`, `%conda`, remote imports, mutable workspace files or unversioned `%run` dependencies. Required imported Python modules are deployed as versioned wheels/resources with artifact checksums, not inferred from the top-level notebook SHA.
6. Correlate the Fabric job instance and observed runtime notebook/workspace/environment identity to launcher-controlled admission. Job arguments must be allowlisted and must not override the environment, lakehouse routing, mode or activation identity. A user-supplied `verification_ok` or invocation nonce alone cannot authorize publication. If platform job-to-runtime correlation cannot be verified externally in a supported way, the gate remains blocked; do not build a bespoke token/attestation service to conceal that gap.
7. Before the first publication, validate pinned activation/Contracts, the admitted job binding, actual operation and target. Keep the deployment barrier through run termination; normal Registry lease release does not release protection for an otherwise still-running job. Preserve safe outcome/provenance in Run.

This yields **process-verified deployment assurance under trusted deployment/permission controls**, not cryptographic proof of the interpreter's executed bytes. Administrators and principals with direct publication/metadata write permissions remain trusted. A self-check in code cannot defend against code allowed to remove that check. If the review requires stronger immutability against those actors, reject this assurance level and keep Governed disabled until a suitable native or external trusted execution facility is selected.

A release-specific notebook/Environment item can reduce update races, but is still mutable by privileged writers and increases item management. Prefer protected deployment plus drain first; approve per-release items only if tenant tests show they are necessary. No custom cell canonicalizer, AST scanner or notebook hashing framework is justified at planning time. Ordinary artifact checksums are retained for provenance, not marketed as running-code attestation.

### Fabric feasibility gate before runtime implementation

Run an isolated tenant experiment with manual edits/unsaved interactive cells, stale/reused sessions, Git sync, deployment rebinding, Environment staging/publish, dependency modification, queued jobs, job setting overrides and an attempted deployment during a run. Verify effective workspace/item roles and service identity support; `Git Get Status`/definition retrieval need stronger permissions than basic execution. Prove an externally enforced deployment barrier and job/session correlation, or document failure and block the Governed implementation PR. This experiment uses test artifacts only and requires its own approved tenant execution scope; none is performed in this planning task.

## 6. Activation transaction, pinning and runtime concurrency

### One-table atomic protocol

The new Registry is relational, but **not** a set of independent authoritative Delta tables. All pipeline activations, independent table-contract pointers and control/lease state commit in one Delta transaction.

Proposed implementation uses the existing domain-specific Delta transaction approach (already present in Catalogue migration), adapted for one governance table:

1. Start a transaction and pin its read version. Read the entire small Registry through that transaction, including the control row and all compatibility/lease predicates. Require exactly one valid control record, unique business keys and the caller's expected token. Never synthesize missing authority at runtime.
2. Compute the complete resulting activation/Contract/lease set from that snapshot. Validate active references, physical destinations, strategy compatibility, affected-run drain, immutable provenance, operation uniqueness and authenticated governance action. Compatibility is recalculated from current active descriptors, not a separately stored ownership map.
3. Stage replacement data at an isolated path, retain a whole-table read dependency and atomically commit file removals/additions with the new token. No check-then-overwrite, untracked source read or independent control MERGE followed by activation MERGEs. Start with a full small-table replacement transaction; optimize touched-file replacement only after correctness and measured volume require it.
4. Use the runtime's validated Serializable conflict behavior. Microsoft's [Fabric concurrency guidance](https://learn.microsoft.com/en-us/fabric/data-engineering/delta-lake-concurrency-control) describes Serializable isolation and read/write conflicts; the repository's Catalogue comment currently mentions default WriteSerializable. Do not copy that assumption into the new protocol: verify effective behavior on every supported local/Fabric runtime, including blind appends and phantom activation rows.
5. On conflict, abort all proposed changes, reread and revalidate; stale human activation review requires refresh/review rather than silently applying a changed proposal. Bound recognized transient retries. Keep a logical mutation ID and stable attempted token; confirm lost acknowledgement through its committed transaction/history and exact proposed state before another mutation. Later unrelated commits must not cause a committed operation to be replayed.

This changes the persistence algorithm, so it requires real-Delta race tests and a Fabric gate. Internal JVM transaction APIs/version support must be established. If they cannot provide tracked reads and the required conflict semantics, stop and choose a reviewed transactional implementation; do not fall back to independently committed MERGEs. No per-update schema/property DDL is required.

Initial centralized serialization is a conscious safety tradeoff, similar to today's shared token, but no retained approval history is reconstructed on admission. Measure Registry row/JSON size, mutation latency and conflict rate before scaling; this is a starter-kit design, not a claim of unlimited control-plane throughput.

### Minimal leases and changes during runs

The control's `leases_json` contains only transient records:

- **Run admission:** lease ID, Run/Pipeline/workspace IDs, pinned pipeline activation ID, exact table-contract activation IDs/versions/hashes, physical participant identities and trusted deployment/job reference. It protects policy and deployed dependencies for the full run. It does not grant write permission by itself.
- **Publication slot:** owner Run/lease, normalized physical target, and publication identity/state. Acquire immediately before receipt/retry resolution and publication; hold through physical verification and Processing State acknowledgement. Keep required Catalogue/Lineage finalization retry identity. Default to one publication at a time per physical target even when multiple compatible pipelines are activated.

Use one array with a strict lease kind, not a new reservation-history lifecycle. Release only the caller's exact lease after terminal/cancelled execution; a crashed client leaves fail-closed coordination. Do not expire a lease on time alone: cancel/fence the old Fabric job/session, verify it cannot still write, reconcile target receipts, then release through CAS. A token in metadata is not a storage-enforced fence against an already authorized stale writer.

Activation/contract changes must drain all affected leases; unrelated pipelines can continue. A run pins record activation IDs and contracts, not the global token that changes during unrelated operations. Replacing/deactivating the pipeline or any pinned Contract is blocked until it finishes; never let a governance edit silently change an execution's policy. Deployment/dependency changes are additionally blocked by the external barrier because they happen outside Delta.

Shared target publication slots are keyed by normalized physical destination, not merely Table ID or environment label. Reject aliases mapping multiple logical Table IDs to the same physical target unless explicitly reconciled; otherwise “separate environments” could bypass coordination. Preserve existing configured route/binding verification before every mutation.

Governance authorization must be authenticated and separated from ordinary run/lease mutations through the chosen trusted execution/permission boundary. The current widget checkbox is confirmation, not role enforcement. Delta does not offer column-level permissions separating activation edits from lease updates in this one table: principals with raw write access are trusted. If tenant security requires untrusted execution principals to be technically unable to alter governance, approve a service boundary or a different authoritative store before implementation.

## 7. Multiple writers: compatibility, progress and idempotency

### Strategy compatibility policy

All Governed participants reference the **same independently active frozen Contract** for an environment/Table ID. Today's Contract has one exact processing definition; keep it initially. Different write strategies cannot share that Contract by silently broadening it to an allowed-strategy list. Source Table IDs and identical Read/Write descriptors neither prove conflict nor establish identity.

| Writer strategy/pair | Activation-time decision | Runtime/publication requirement |
| --- | --- | --- |
| Append + Append | Allow multiple Pipeline IDs when both satisfy the active Contract, destination, append semantics and progress/idempotency scope. Overlapping rows may be intentional; uniqueness/business-key guarantees must still be demonstrably enforceable | Initially serialize publication/receipt acknowledgement per target; isolate writer progress and retry suppression. Parallel Delta appends are a later measured optimization, not required to permit multiple active writers |
| Overwrite + any other target writer | Reject by default; whole-target replacement is exclusive. A documented coordinated owner may be proposed, but a schedule string is insufficient | Exclusive publication slot and drain conflicting in-flight writers; no blind retry that replaces a newer valid publication |
| Merge/Upsert + Merge/Upsert | Compatible only with the same Contract/keys, deterministic conflict policy and enforced nonoverlapping key/partition scopes, or an explicit ordering coordinator | Generic Merge/Upsert is **not** a current `load_strategy` value. Do not add an alias to `scd1`. Scope enforcement/strategy support is separate approval; reject unsupported cases |
| SCD1 + SCD1 | Multiple active writers only after enforceable disjoint key domains or explicit deterministic ownership/ordering is implemented and tested; otherwise exclusive | Serialized publication initially; same key definition and audit semantics; retries must not replace a later winner. A mutex alone does not resolve contradictory business updates |
| SCD2 + SCD2 | Strongest restriction: compatible keys, effective-time/tracked-column rules and proven disjoint history domains/order. Otherwise exclusive | Preserve temporal history, late-arrival and latest-publication checks; table-level serialization alone cannot make two conflicting histories valid |
| Mixed strategies, same target | Reject under the initial exact-processing Contract model | Any future coexistence requires explicit Contract semantics and tested publication protocol, not “Delta is ACID” |
| Readers with writers | Multiple readers permitted; all use active Contracts; reader dependencies participate in Contract-change drain | Keep actual source/target associations and read snapshots. Do not claim a cross-table business snapshot or dataflow graph |

A physical table relationship child is not needed for integrity at this volume: the tracked transaction validates decoded active descriptors. If measured Registry scans or dashboard refresh are too expensive, consider **one** `(workspace_id,pipeline_id,activation_id,table_id,role,operation_key)` relationship table. If derived, it cannot authorize; if authoritative, it must move into the same transactional storage/protocol. No such table is recommended initially.

### Hidden single-writer assumptions that must change first

Removing `activation_impact`'s writer check alone is unsafe:

1. `_latest_source_target_observation` and `_previous_source_target_observation` select accepted progress by workspace/source/target, without filtering the existing `pipeline_id` column. Two pipelines sharing the same Read/Write pair can consume each other's watermark or Source Drift baseline. Scope accepted checkpoints/baselines and recovery to stable Pipeline ID as well as current workspace/source/target; keep existing physical Processing State columns and IDs for historical records.
2. `PublicationBatch` currently computes content/processing/source/target batch identity without Pipeline ID. Delta append transaction ID uses that batch ID, and `_find_applied_publication` searches batch IDs without writer identity. Identical legitimate outputs from two pipelines can therefore suppress one pipeline's append. Namespace new retry identity by stable Pipeline ID + target operation, not Run ID, and verify the same scope in persisted receipt lookup and physical proof. Retries across runs of the **same** logical pipeline still recover the original publication.
3. Receipt acknowledgement, Source Drift/incremental staging and Warehouse recovery were designed with target writer serialization. Acquire the shared publication slot before retry lookup/staging/mutation and keep it until acknowledgement. Retain exact-batch membership, row-count/audit markers and no-replay guarantees. No generic concurrent-Warehouse exactly-once guarantee is claimed.
4. New writer bootstrap against a populated append target still cannot invent a baseline. Require an explicitly established source-specific baseline or safe reviewed full/partition load. This may block some incremental multiwriter activations until progress is prepared; it is not a uniqueness rule on pipeline Read/Write combinations.

Reuse `METADATA_PROCESSING_STATE.pipeline_id`; no new physical checkpoint table is needed. New receipt metadata should carry a receipt schema version and writer/operation scope. Legacy receipt interpretation is limited to exact retained evidence with one proven original Pipeline ID; this is necessary persisted-format recovery, not an obsolete lifecycle API. Ambiguous ownerless/shared historical receipts require reconciliation before cutover. Do not rewrite historical Delta commit proof or retroactively declare old receipts to have new scope.

Implementation must define a tested legacy retry bridge using the original batch identity plus proven owner from retained Processing State, so the original pipeline does not replay a previously published batch after namespacing changes. If original ownership/publication cannot be established, fail closed and reconcile; do not copy one checkpoint to every new writer. Approve this narrowly necessary historical receipt decoder explicitly; no general old-runtime fallback is proposed.

## 8. SQL endpoint and Power BI plan, coordinated with #1764

**No reporting projection publisher, generation manifest, reporting Run digest or twelve-table expansion remains in this proposal.** Canonical tables are the persisted source; Import-mode Power Query creates model-only children. Complex JSON is consciously accepted for bounded, infrequently queried activation operations and Run details.

Use Spark scalar `string`, `integer`, `long`, `boolean`, `timestamp`, `double` and existing `date`, corresponding to SQL string/int/bigint/bit/datetime2/float/date. Validate actual Fabric SQL endpoint string length/Unicode/type exposure; never truncate authoritative JSON to make a report load. Use UTC timestamp instants, preserve schedule local times and timezone names, and avoid nested physical types in all canonical fields.

| Reporting need | Canonical source / Power Query expansion |
| --- | --- |
| Activated pipelines, environments, deployment and Git version | Registry scalar `pipeline_activation` rows; activation/verification status plainly visible |
| Active Contracts by environment/Table ID | Registry scalar `table_contract_activation` rows → Contract `(contract_id,contract_version)`; frozen ≠ active |
| Sources, targets, strategies and shared tables | Parse pipeline `operations_json`, expand descriptor and destination records in the semantic model; group distinct pipeline participation rather than requiring an owner table |
| Failing/slow runs and operations | Existing Run scalars plus JSON-expanded operations; derive elapsed operation time from actual timestamps. No historical stage-duration claim: current persisted stage fields have no duration |
| Stage outcomes, failure codes and profile execution | Model-only expansion of Run operations/stages, failures and profiling; preserve event ordinals and duplicate safe failure occurrences |
| Profile/frequency history | Existing Profiled and Frequency; preserve independent frequency snapshots with null `profile_id`; joins by actual snapshot/table/column grain |
| Guardrails, Lineage, permissions and progress | Existing respective relational tables; aggregate at their actual grains, avoid fact fan-out and treat access as observations |
| Freshness | Semantic refresh time and maximum observed source commit times; show SQL propagation delay and refresh failure. No falsely precise “all metadata synchronized” global timestamp |

Required coordination changes in #1764's owner/follow-up PR, **not made by this document**:

- Update `scripts/generate_fabricops_powerbi_project.py` and `scripts/validate_fabricops_powerbi_project.py` for the new Registry schema/kinds and JSON parsing. The existing generator explicitly selects scalar columns and will not automatically import the new JSON just because Spark types change.
- Regenerate affected TMDL partitions/relationships/measures and PBIR visuals from their owning dashboard generator only when dashboard work is approved. Files include `powerbi/FabricOpsMetadata/FabricOpsMetadata.SemanticModel/definition/tables/METADATA_PIPELINE_REGISTRY.tmdl`, `METADATA_PIPELINE_RUN.tmdl`, `METADATA_DATA_CONTRACT.tmdl`, `DimPipeline.tmdl`, `expressions.tmdl`, `relationships.tmdl`, relevant model-only child definitions and report page definitions.
- Update `powerbi/FabricOpsMetadata/SOURCE_TO_MODEL.md` and `README.md`: remove old singleton-grain assumptions, distinguish frozen versions from active bindings, and replace scalar-only exclusions with explicit JSON projections. Evaluate removing `pLoadComplexBearingTables` for the all-scalar target after signed-in endpoint validation; do not add hidden legacy lifecycle aliases to the runtime to keep an old report working.
- Load each imported Run/Registry source once per refresh and derive JSON children from that cached/staged import so headers and their arrays represent the same row snapshot. Do not issue independent “latest” queries for every child. Cross-table endpoint propagation remains asynchronous: display as-of limits and retain the previous successful model if required references are unavailable.
- Fail refresh visibly on malformed non-null JSON; do not turn parser errors into empty operation lists. Type bigint fields carefully, retain null versus empty arrays and handle arrays without Cartesian multiplication. Use semantic composite keys and single-direction relationships. A duplicate Reader/Writer dimension is not an authority.

Power Query JSON expansion is suitable for Import, not a claim of JSON query folding or Direct Lake support. Measure Run history size/refresh cost and implement bounded/date-filtered import where appropriate. Only measured performance or a concrete reporting gap should justify a new physical relationship table.

## 9. Automatic migration, evidence retention and rollback

### Keep authorization changes explicit

A current approval proves old Test/Contract/Agreement facts, **not** an immutable deployed code revision. Automatic migration cannot manufacture that missing proof. Default recommendation is an offline, reviewable cutover: preserve existing evidence and map active configurations as `requires_reactivation`, then activate after trusted deployment verification. **This intentionally pauses existing Governed authorization and requires explicit approval before rollout.** Setup must report that readiness gap, not silently say ready. Do not automatically authorize an old approval under the stronger new semantics, and do not allow fallback to the old approval engine.

If uninterrupted operation under the old trust model is required, defer cutover and run the old package/schema until reviewed redeployment is ready. A parallel legacy authorization mode would preserve the complexity being removed and is not proposed.

### Exact legacy mapping

| Existing fact | New state / retention |
| --- | --- |
| Stable registration Pipeline ID and notebook deployment | Preserve IDs in migration report and map selected active pipelines to candidate activation rows; put IDs into version-controlled pipeline metadata. Unactivated/retired registration history goes to immutable archive, not active rows |
| Selected approval and its retained Test operations | Validate exact references/hashes; populate candidate operations and exact Agreement fields from committed selected state. Preserve old approval ID and all historical fields in archive; no fabricated Git/deployment evidence |
| Nonselected approvals/version labels | Preserve complete archive and original Run references; no runtime approval/version history |
| Selection + workspace revision | One candidate pipeline row; preserve original revision/selection provenance in archive. Generate new activation ID only on the new governance action |
| Ownership/readers/Contract binding | Reconstruct independently per workspace/Table ID and compare with selected operations. If every applicable selected reference agrees, create `requires_reactivation` table-contract candidate. Do not infer activation from global frozen status or arbitrarily choose a version |
| Reservations | Drain and reconcile before cutover; never clear as a shortcut. Existing unresolved leases block the migration |
| Historical Run/Guardrail/Processing State/Profiled/Frequency/Lineage | Preserve existing rows/IDs/audit/evidence; convert Run/Catalogue physical nested fields losslessly. Existing Run approval references remain historical, resolved through archive for audit rather than active runtime |
| Legacy accepted progress/receipts | Preserve existing IDs and ownership; migrate reader scoping only after proven Pipeline ID attribution. No checkpoint reset, no automatic target replay or rewriting old physical receipt proof |

There is **no existing generic activation/registration audit table** in the canonical twelve. Run and Guardrail Results already contain execution/quality evidence and should retain it; do not fabricate run rows to store governance decisions or put activation events into Processing State. Preserve non-run registration/approval history in a durable immutable migration archive under the configured Metadata Lakehouse `Files` or approved audit storage, with exact source table identity/version, schema, raw JSON/typed timestamps, package commit and checksums. Delta time travel alone is insufficient archival retention after vacuum. A SQL-queryable activation-history table is an optional future requirement, not silently introduced here.

For new governance changes, write an immutable audit snapshot first, then reference its change ID/URI in the same committed Registry transaction and Delta commit metadata. It contains before/after activations and trusted actor/deployment provenance. A failed transaction may leave an orphan audit file; the file alone never proves a committed activation. Retain committed transaction/change receipts with the archive so deactivation/replacement can be audited after ordinary log retention. Audit history is not a second authorization lifecycle.

### `setup_metadata_tables()` upgrade state machine

1. **Preflight the entire supported input set.** Resolve central Metadata routes and all three affected tables. Recognize fresh, current native, known JSON-string and supported mixed native/string layouts by exact signatures; inspect table IDs/properties/protocol/column mapping. Reject unknown types, missing required authority facts, duplicate identities, corrupt JSON and retired Preview layouts without changing that table. Inventory unsupported nested extensions separately.
2. **Prepare and drain.** Stop Test/Run producers, governance updates, deployers and scheduled jobs. Reconcile in-flight receipts/leases against physical targets; retain target audit markers and Delta history. Block automatic migration if any ownership, receipt or selected-Contract ambiguity remains. Document deployment permissions/barriers; an empty lease list does not prove all old writers are stopped.
3. **Archive and validate mapping.** Materialize immutable full legacy Registry and reference/receipt provenance archives. Check row counts, IDs, all retained Test/Agreement/Contract hashes, registrations and approval cardinalities. Produce deterministic candidate mappings. Derive archive/migration identity from source table ID/version so reruns do not create differing authority.
4. **Convert Catalogue and Run in pinned transactions.** Replace the existing Catalogue string-to-native canonical direction with native-or-supported-string to string; never leave contradictory upgrade paths. Use snapshot-pinned reads, durable staging and one atomic schema+file commit per table, preserving all rows, unrelated columns, audit, properties, column-mapping identities, partitioning and Run transaction-deduplication state. Real schema-change conflicts must protect against concurrent old writers; a normal overwrite after a check is unsafe.
5. **Replace Registry last.** After other required schemas and archive/mapping validation succeed, atomically replace the old singleton layout with control + candidate rows in the same Delta table, retaining physical table identity. A fresh installation instead creates control and no business activations with `errorifexists`; a concurrent creator is reread/validated. Existing target schemas validate without reseeding or changing activations. No new empty Registry may silently override populated authority.
6. **Validate and report.** Read exact committed versions back, compare lossless logical contents and preserved row multisets, verify archive digest and all historical hashes, validate target PKs/kinds and readiness. Partial table conversion is resumable but operational cutover remains blocked until all required schemas/processing scope checks pass. Setup returns operational schema status separately from activation/deployment readiness.
7. **Reactivate and restart.** Governance explicitly activates independent Contracts and verified deployed pipelines; run Fabric/SQL/Power BI canaries, then enable schedules under the new package. New runtime schema guards reject incompatible layouts; no mixed-version writers or old lifecycle fallback readers.

### JSON and repeated-setup rules

Central codecs must separate physical strings from existing application dictionaries/lists. Decode every direct reader, including Spark `explode`/field selections and registry startup/consumer reads; encode every direct DataFrame/literal write. Validate duplicate keys, roots, null elements, unknown fields, numeric ranges/finite doubles and timestamp precision. Do not rely on permissive Spark parsing that silently returns null for invalid JSON.

Preserve SQL null (uncaptured), JSON `[]` (known empty collection), object emptiness, array order and nullable fields. Required collections cannot become null. Preserve long values above 2^53 and finite numeric semantics without a float/JavaScript roundtrip. Normalize native timestamp instants consistently with existing `pipeline_record_content`, including UTC/microseconds, and preserve existing string timestamp semantics. Never rewrite frozen Contract payload bytes or recompute old approval/Test hashes as a migration side effect.

Retain Catalogue's documented historical exception: blank/whitespace strings mean SQL null, and list-only key candidates become the known candidate object with null status/maximum width. Do not apply that permissiveness to Registry/Run. Preserve Scheduled Refresh values/discovery and key-candidate order. Direct `_persist_grain_candidates` struct literals and Catalogue coalesce behavior must be updated, not left to implicit Spark coercion.

On target schemas, repeated setup validates without rewriting valid JSON, mutating authority/token, changing candidate status, reactivating anything or rescoping historical evidence. On recognized Delta conflict, reread/revalidate boundedly; a competing completed migration becomes a no-op. On lost acknowledgement, inspect committed migration identity/version rather than replaying target/business actions. New runtime refuses unsupported old schemas; migration input handling is not a general compatibility API.

### Rollback and recovery boundary

Retain backups and Delta files/history through acceptance; suspend vacuum that removes recovery versions. An interruption before a table commit leaves its source intact; staging is disposable only after confirming no active attempt owns it. An interruption after commit is recovered by inspecting history and rerunning setup validation. Post-commit verification failures block readiness and require inspection; never automatically RESTORE.

Before any new business publication, an offline rollback can restore the compatible old package and the full pre-upgrade metadata/schema set after checking current heads and reconciling any new activation actions. Do not restore only Registry while leaving incompatible Run/Catalogue code. After new publications, metadata-only restore can lose checkpoints, scoped receipts and policy history: perform a reviewed forward repair or fully reconcile target/publication boundaries first. Never drop/truncate/reset Live metadata or blindly restore over valid later writes.

## 10. Complexity comparison and choices rejected

| Dimension | Current `main` | Previous #1766 proposal | Simplified recommendation |
| --- | --- | --- | --- |
| Canonical physical metadata tables | 12 | 24 (12 existing + 6 Registry projections + 5 Run children + sync manifest) | **12**, no reporting copies; optional relationship table only after demonstrated need |
| Registry physical grain | One singleton with six nested arrays | Same singleton encoded as JSON, plus reporting generations | Current pipeline row per environment + current table-contract row per environment + one internal control row |
| User-facing governance entities | Registration, Test candidate, approval/version history, selection, workspace revision, ownership | Same lifecycle plus projection/synchronization concepts | Table Contract freeze/activation and deployed pipeline activation; execution modes remain three |
| Persisted coordination collection | Reservations; revision/token; histories rebuilt on reads | Same plus reporting generations/freshness | One transient lease array + CAS token + activation IDs; external deployment barrier is a new prerequisite |
| Read/write participation | Approved Run operations plus derived ownership | Same plus several reporting relationship tables | One activated operation JSON value; model-only expansion; no duplicated ownership aggregate |
| Reporting cost | Complex fields unavailable through SQL | Projection publisher, repairs, retention and refresh consistency | Power Query expansion/refresh cost, no projection synchronization service |
| Code version assurance | Explicitly does not verify notebook transformation code | Unchanged | Conditional external deployment assurance; no unsupported immutability claim |
| Migration cost | No simplification | Twelve physical conversions plus projection backfill | Breaking authority migration and reactivation, scoped progress/receipt work, six Run/Catalogue conversions; higher governance change risk made explicit |

Rejected: recreating all six lifecycle collections as JSON; treating a notebook SHA argument as proof; preserving Test/approval APIs as wrappers; separate independently updated authoritative tables; generic Merge→SCD aliases; universal single writer; unrestricted SCD multiwriters; reporting copies solely to expand JSON; using Run/Processing State as a catch-all governance audit log.

A one-row all-JSON workspace Registry is transactionally simpler but does not give the requested relational grain. Fully splitting pipelines, Contracts and leases into independent Delta tables would look cleaner but require cross-table coordination. The mixed-record single-table design is the smallest relational authority with an explicit atomic boundary; its performance/security limits must be accepted, not hidden.

## 11. Minimal ordered implementation PR plan

The plan below is conditional on architecture approval and the deployment feasibility gate. Keep each PR focused and deployable; never merge half of a breaking schema/protocol cutover. All paths are relative to repository root; proposed files are labeled. No implementation PR is opened now.

### PR 1 — SQL-safe logical/physical metadata boundaries and lossless conversions

**Objective:** independently deliver SQL-compatible existing Run/Catalogue fields and centralized codecs without changing governance authorization yet. Dependency: approval of preservation/migration rules. This uses the current Registry unchanged; it is not a dual-lifecycle runtime adapter.

**Exact source owners:** `src/fabricops_kit/config/metadata_schemas.py`, `config/setup_metadata_tables.py`, `activated_pipeline/shared.py`, `pipeline/shared.py`, `pipeline/pipeline_write.py`, `pipeline/check_source_drift.py`, `data_contract/shared.py`, `widgets/widget_data_contract.py` under the same `src/fabricops_kit/` prefix. Inspect `widgets/widget_activate_pipeline.py`, `pipeline/finalize_pipeline.py` and `data_agent/shared.py` for direct Run/Catalogue consumers; change them only where their read boundary requires it. Keep public dictionaries/lists and old evidence hashes unchanged.

**Tests:** `tests/unit/test_catalogue_nested_types.py`, `test_metadata_schemas.py`, `test_config.py`, `test_pipeline_run_records.py`, `test_pipeline_run_evidence.py`, `test_table_profiling_schedules.py`, `test_contract_authoring_services.py`, `test_widget_data_contract.py`; `tests/integration/test_catalogue_upgrade_delta.py`, `test_pipeline_run_delta.py`, `test_joint_pipeline_metadata_delta.py`; new `tests/unit/test_metadata_serialization.py` and `tests/integration/test_sql_metadata_upgrade_delta.py`.

**Migration validation/acceptance:** fresh/native/string/mixed inputs; corrupt values fail before commit; null/empty, duplicate Catalogue rows/extensions, numeric/timestamp precision, column mapping/properties and Run transaction identities preserved; writer/setup/blind-append conflicts; lost acknowledgement/interruption; rerun no-op; retained Test hashes and profiling eligibility identical.

**Affected docs/generated owners:** `scripts/reference_docs_metadata.py`, `AGENTS.md` native physical descriptions, existing `docs/maintainer/metadata-v2-target-model.md`, directly affected generated metadata/function references. No dashboard or release generation. **Rollback:** offline compatible schema/package pair before later writes; otherwise forward reconciliation, no reset.

### PR 2 — Direct activation authority, mode/identity changes and automatic cutover

**Objective:** replace old lifecycle and introduce independent table-contract activation with atomic pinning. Dependency: PR 1, approved schema/protocol/legacy evidence policy, and a passed deployment feasibility experiment. Until runtime deployment verification is integrated, migrated pipelines remain `requires_reactivation` and Governed publication is blocked.

**Exact owners:** `src/fabricops_kit/config/metadata_schemas.py`, `config/setup_metadata_tables.py`, `activated_pipeline/shared.py`, `pipeline/shared.py`, `pipeline/setup_pipeline.py`, `pipeline/finalize_pipeline.py`, `pipeline/orchestrate_read.py`, `pipeline/orchestrate_write.py`, `pipeline/pipeline_write.py`, `data_contract/shared.py`, `widgets/widget_activate_pipeline.py`, `widgets/widget_data_contract.py`, `data_agent/shared.py`, and public export files only if approved callable ownership changes demand them. Replace obsolete internal APIs outright; do not keep approval/rebind aliases. Add a focused Contract activation public owner (proposed `src/fabricops_kit/data_contract/activate_data_contract.py`) and exports if callable activation is selected, or add the action directly to the owning Contract widget; do not create both wrappers.

**Source:** transactional mixed-record Registry, active-pointer resolution, activation review/Agreement checks, shared control token, run pins/leases, protection for governed targets, stable Pipeline ID public behavior, audit archive, source/target configuration validation. Update current Run snapshots with scalar `pipeline_activation_id:string`, `deployment_id:string`, repository-qualified `git_commit_sha:string`, `deployment_verification_status:string`, and `run_schema_version:integer` for new runs; retain old `approval_id`/`activation_revision` columns as nullable historical evidence, not runtime aliases. Historical frozen Test contents cannot be changed. Preserve a versioned logical Run representation for historical hash verification: old/null run schema version uses exactly the original hash-bearing fields, excluding new physical provenance columns, even when Spark exposes them as null. New versioned Run hashes include the new provenance. Reject unexpected non-null new provenance on a legacy frozen Test; do not silently erase it to make a hash pass. Golden archived Test hashes must validate after additive schema changes. This is retained-evidence format handling, not a legacy authorization fallback. Contract pins remain in operation facts; no duplicated Contract definitions.

**Tests:** `tests/unit/test_pipeline_registry.py`, `test_setup_pipeline.py`, `test_pipeline_session.py`, `test_pipeline_execution_modes.py`, `test_activation_state_commit.py`, `test_activated_pipeline.py`, `test_widget_activate_pipeline.py`, `test_contract_authoring_services.py`, `test_data_agent.py`, `test_metadata_writer_ownership.py`; `tests/integration/test_pipeline_registry_delta.py`, `test_activation_state_delta.py`, `test_joint_pipeline_metadata_delta.py`; new `tests/integration/test_pipeline_activation_migration_delta.py`. Test stale review, simultaneous activation/admission/Contract update/deactivation, phantom inserts/control corruption, exact lost-ack recovery, same notebook/logical IDs, deployment replacement drain, no-Contract failure before publication and unrelated token changes not invalidating pins.

**Migration acceptance:** full legacy record counts/hashes archived; candidate mapping deterministic; no approval upgraded into code proof; zero automatic business replay; repeated setup leaves state unchanged; historical Run evidence queryable; deliberate reactivation pause reported. **Generated/docs:** directly affected schema/function references, glossary (intentional concept changes), `AGENTS.md`, maintainer model and living `templates/notebooks/00_env_config.ipynb`/`02_pipeline.ipynb` only where current examples need the approved mode/identity contract. Follow notebook skill; never update historical release snapshots. **Rollback:** pre-publication package/schema restoration only; after publications use section 9 recovery.

### PR 3 — Trusted deployment gate and writer-safe publication

**Objective:** enable Governed only with verified deployment assurance and support compatible append writers without cross-pipeline progress/retry leakage. Dependency: PR 2 and tenant-proven external gate. These are required safety pieces for the new Governed behavior, not optional follow-up fixes.

**Owners:** `src/fabricops_kit/activated_pipeline/shared.py`, `pipeline/shared.py`, `pipeline/pipeline_write.py`, `pipeline/pipeline_read.py`, `pipeline/orchestrate_read.py`, `pipeline/orchestrate_write.py`, `config/shared.py` for native runtime/job correlation if necessary; proposed tenant deployment integration files `scripts/verify_pipeline_deployment.py` and `docs/maintainer/governed-pipeline-deployment.md`. CI workflow location must follow the selected tenant deployment tool; do not repurpose `.github/workflows/release.yml` package publishing into an unreviewed production deployer. Versioned manifests/built artifacts stay outside canonical runtime tables except their references/required Run scalars.

**Source:** external verification/job binding and fresh session restrictions; publication slots across all active writers; Pipeline-ID-scoped existing checkpoints/baselines; writer-namespaced new receipt/append deduplication; narrowly necessary legacy receipt recovery; strategy-aware activation validation. Multiple append activations can be enabled only when these changes and cross-pipeline tests pass. Keep unsupported Merge/scoped SCD multiwriters rejected; add those capabilities in a separately justified PR if required.

**Tests:** new `tests/unit/test_pipeline_deployment_verification.py`, `tests/integration/test_multiwriter_publication_delta.py`; extend `tests/integration/test_publication_batches.py`, `test_joint_pipeline_metadata_delta.py`, `tests/unit/test_incremental_pipeline.py`, `test_pipeline_execution_modes.py`, `test_table_profiling_schedules.py`. Cover identical and different Read/Write pairs across Pipeline IDs, same-content append not incorrectly deduplicated, same-pipeline cross-run retry, independent watermarks, legacy receipts, first-writer bootstrap, incompatible keys/scopes, physical aliases, Warehouse serial recovery and late stale writer.

**Acceptance/Fabric:** all adversarial deployment cases in section 5; forged SHA/manifest/parameters rejected, denied external verification fails before publication, deployment blocked during active/queued run, actual packages/runtime match allowed artifacts, no old kernel reuse. Append writer coexistence and receipt correctness proven; no claim of parallel Warehouse exactly-once. **Rollback:** stop new admissions, drain/cancel and reconcile publications; disable new Governed/multiwriter capability without replaying or rescoping receipts. Never revert just the writer namespace after new publications.

### PR 4 — Dashboard model alignment with #1764 and rollout validation

**Objective:** make the existing canonical-source dashboard show actual pipeline/Contract activation and bounded JSON operation detail. Dependency: approved schema plus runtime rollout readiness; can be prepared alongside PRs 2–3 but deployed against their verified target schema.

**Owners:** #1764's `scripts/generate_fabricops_powerbi_project.py`, `scripts/validate_fabricops_powerbi_project.py`, `powerbi/FabricOpsMetadata/SOURCE_TO_MODEL.md`, `README.md`, and their owned semantic/report definitions listed in section 8. Add focused JSON/model contract tests under a proposed `tests/unit/test_powerbi_metadata_model.py`. If #1764 is unmerged, align on its branch/follow-up rather than generate a competing dashboard project.

**Acceptance:** twelve canonical physical sources; filtered two business Registry kinds; malformed JSON visible; correct composite keys, no fan-out, independent Frequency facts retained; signed-in SQL endpoint types/lengths/timestamps and Desktop refresh; actual active Contract counts rather than frozen proxy; source/refresh age displayed. Measure refresh size/time before proposing a physical relationship table. **Rollback:** retain previous compatible semantic model/report and clearly mark missing activation detail; no runtime/schema rollback for report failure.

### Generated-artifact discipline across implementation PRs

Query relevant callable slices using `scripts/query_public_function_call_flow.py` before changing functions. Canonical schema/docstrings/`scripts/reference_docs_metadata.py` own references. Regenerate only affected `docs/reference/metadata.md`, `docs/reference/metadata/*.md`, `docs/api/reference/*.md` and reference index outputs through `scripts/generate_individual_function_reference_pages.py`; run it twice and require no second-run diff. Regenerate `public-function-call-flows.json` only if its content contract changes, retaining its timestamp update only with content changes. Do not manually edit generated files or regenerate the call-flow HTML dashboard. Actual graph explainer is `docs/function-call-graph.md`; the alternative path listed in AGENTS is absent at baseline.

Dashboard model changes in PR 4 use their own generator/validator; they do not authorize call-flow dashboard or unrelated release churn. All implementation PRs need targeted tests, real Delta concurrency tests when applicable, relevant Ruff/syntax checks and strict docs build. Preserve historical release snapshots. None of these implementation generators runs for this planning update.

## 12. Decisions requiring approval

1. **Authority shape:** zero new physical tables; pipeline/table-contract/control rows in the one Registry transaction. Accept sparse kinds and global serialization, or select another explicitly transactional store before coding.
2. **Lifecycle/API break:** activation replaces registration/approval/selection/version-label history. Stable explicit Pipeline ID for persistent runs; remove old registration/rebind arguments and aliases. Independent table-contract activation is a new behavior.
3. **Code assurance:** approve the external deployment/barrier/job-correlation assurance and its trusted-actor limits only after Fabric feasibility validation. Exact interpreter-byte immutability is not established. No verified gate means no Governed publication.
4. **Security boundary:** confirm trusted deployer/governance/execution identities and effective permissions. If untrusted run principals must be isolated from raw governance writes, approve a service/authoritative-store boundary; a checkbox or Delta row kind cannot provide that security.
5. **Multiwriter scope:** compatible Append allowed after writer-scoped progress/receipts and publication serialization. Overwrite exclusive; Merge not currently supported; scoped Merge/SCD remain blocked without enforceable policies. Confirm whether serialized publication meets initial performance needs.
6. **Historical receipt compatibility:** approve only the direct persisted-format decoder needed to preserve exact legacy retry evidence; no obsolete workflow wrappers. Ambiguous progress/receipt ownership must be reconciled, not copied to multiple writers.
7. **Cutover pause and evidence retention:** approve drain/redeployment/reactivation for old approvals, durable non-SQL governance archive, original Run/Guardrail/Processing State preservation and rollback boundary. Existing approvals cannot become proof of frozen code automatically.
8. **Agreement/consumer semantics:** preserve existing Agreement checks and explicit ambiguity failure; approve any new consumer Agreement input separately. Contract activation never implies permission to consume data.
9. **Reporting:** expand JSON within #1764's Import model; no projection table farm. Only measured need can authorize one physical relationship table later.

Recommended next action is architecture review of these decisions, followed by the isolated Fabric verification experiment. Runtime implementation remains blocked pending that review and the experiment's result.

## Planning validation

This is a source/documentation audit, not a successful tenant deployment or concurrency test. Verified latest-main source, existing Registry readers/writers and checkpoint/receipt scope assumptions; inspected #1764 source contracts; consulted Microsoft's documented Fabric APIs and permissions. Document structure/source-reference checks passed, including all twelve canonical tables and all twelve legacy nested fields. `UV_PROJECT_ENVIRONMENT=/workspace/work/docs-env uv run --no-sync mkdocs build --strict --site-dir /workspace/work/simplified-governance-docs-site` passed. Repository review confirmed that only this planning Markdown file changes; no runtime, generated, notebook or release files changed. PR title/body are updated to this final scope. Runtime and Fabric validation belong to the approved implementation/feasibility gates above.
