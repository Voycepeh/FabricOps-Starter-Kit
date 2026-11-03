# Governed Pipeline Promotion v3 — implementation contract

> **Status:** Implementation specification for an unreleased breaking redesign. This document does **not** enable Governed execution by itself. Do not merge a specification-only PR as a completed feature.

## Decision record

Replace the unreleased #1774 Registry/activation design, including the deployment-attestation gate and its Git/manifest/lease/recovery state machine, with notebook-based Pipeline Promotion and a separate Data Contract Activation authority. Preserve existing released execution semantics, all historical business evidence, and `_row_hash` / `append_all` / `append_new_only` / overwrite / SCD1 / SCD2 behavior. No compatibility promise for unreleased #1774 callers, but do not silently overwrite existing tenant data.

- Dry Run: manual, preview-only, no physical publication or durable run/checkpoint/profiling/lineage/registry mutations.
- Ungoverned: engineer-owned development and execution; no Contract activation required unless accessing a protected physical target. Must never bypass active Contract protection through an alias.
- Governed: only a promoted notebook implementation with active Contract versions for **every approved source and target**, validated Agreement where applicable, exact approved physical bindings, and fail-closed integrity checks. No fallback to Ungoverned.
- Engineers can run promoted notebooks manually and own/change Fabric schedules. Schedule timing changes do not require promotion; changes to behavior-affecting parameters do.
- Promotion creates a **separate Governed notebook** even within the same workspace; same-workspace copies live in an organizational `Governed/` folder. Folders are not security boundaries. Strong edit prevention requires permissions in a separate workspace or on separate resources. Do not overstate ability to block privileged users outside FabricOps.
- Promote from a development notebook to the same or a different workspace, resolving logical stores through the **destination execution workspace's** configuration. Governance must review resolved physical source/target workspace, item, kind, schema and table. Snapshot these bindings, and reject subsequent drift.
- Logical `pipeline_id` is stable across versions and workspaces; immutable `pipeline_version` identifies one frozen implementation *within a destination workspace*. A `promotion_id` identifies each approval. Physical `governed_notebook_id` differs from the development notebook ID and is associated with the exact version.
- Existing runs may complete using their captured old version after a promotion. New runs must use the new active version, and starts against superseded notebook versions fail closed. The implementation must not let incompatible old/new writers concurrently publish to the same target; use the existing writer/publication coordination semantics, not a made-up database lock.
- Only the notebook itself is frozen, not imported packages or referenced notebooks. Document this limitation prominently. Record the complete saved `.ipynb`; derive an executable-content hash from canonical code cells and behavior-relevant parameters. Markdown-only edits are allowed where a verifier can distinguish them; neither a changed code cell nor a changed approved binding is allowed.
- Once a promoted notebook differs from the frozen executable definition, **block new Governed starts and managed operations** and show an integrity-mismatch explanation. Changed implementation must go through manual Dry Run and new Governance promotion. An exact archived-snapshot restoration, including verification, may reinstate the *existing* approval without a new version; preserve changed copy before repair. No auto-overwrite.
- The *security boundary* is limited: a user with enough Fabric permissions can bypass notebook/library checks and invoke Spark independently. A notebook-self-check or separate preflight cannot prove code identity at execution time; document TOCTOU explicitly. Make the strongest verifiable fail-closed claim supported by the implementation and test actual Fabric APIs before advertising Governed as production-safe.
- Active Data Contract versions are resolved by the **physical table workspace** (including cross-workspace reads/writes), and may change independently. Every Run records exact Contract ID/version/payload SHA used for each operation; a newer active Contract is adopted on the next run, subject to validation, without notebook re-promotion.

## Canonical metadata and grains

Target **13 canonical tables**: keep the existing 12, add `METADATA_DATA_CONTRACT_ACTIVATION` under Governance ownership. The Registry is exclusively pipeline-specific.

### METADATA_DATA_CONTRACT_ACTIVATION

Grain: `(workspace_id, table_id)`, at most one active frozen Contract per physical table workspace and logical table identity.

Fields (final exact types chosen consistently with established metadata conventions):
`workspace_id`, `table_id`, `contract_id`, `contract_version`, `payload_sha256`, `activation_id`, `status`, `destination` (exact physical binding), `activated_by`, `activated_at`, standard audit columns. Include a concurrency revision or expected-current-activation precondition if needed to reject stale approval. Protect physical alias matches for Ungoverned writes.

Contract definitions in `METADATA_DATA_CONTRACT` remain globally frozen at `(contract_id, contract_version)`. `evidence_workspace_id` is authoring evidence, *not* activation scope.

### METADATA_PIPELINE_REGISTRY

Grain: `(execution_workspace_id, pipeline_id, pipeline_version)`. One row per immutable frozen implementation/promotion version, with **at most one active version** per `(execution_workspace_id, pipeline_id)`. Superseded rows are preserved, not overwritten or deleted.

Business columns: execution workspace, logical Pipeline ID, pipeline version, `promotion_id`, status (active/superseded/retired or precisely defined equivalent), source notebook identity/workspace, Governed notebook ID, immutable snapshot URI, full-snapshot SHA-256, executable-content SHA-256, exact reviewed operations (nested JSON or existing native representation: preserve semantic fields), binding digest, Agreement ID/version/digest where required, promoted_by/at, standard audit columns. Avoid Git SHA, deployment ID, manifest, verification method, per-run leases and whole-table governance archive receipts. Avoid duplicating Contract activation rows inside Registry.

A version may be active in one workspace and superseded in another; never key the active identity only by `pipeline_id`. One active row is not guaranteed by a Delta `UNIQUE` index: enforce it with a verified serializable mutation + expected-active-version optimistic concurrency, plus replay-safe operation IDs. **Do not assume sequential updates or a naïve MERGE provide atomic conditional uniqueness**. Test simultaneous promotions and phantom insert attempts. Keep the minimal proven transactional coordination necessary; deleting an overbuilt state machine does not justify race conditions.

### METADATA_PIPELINE_RUN

Preserve the existing durable Run content hash and historical rows. Add/repurpose provenance for execution workspace, Pipeline ID, frozen version, promotion ID, Governed notebook ID, actual execution identity, and exact resolved Contract ID/version/payload hash per operation. Old rows must still validate against their historical hash schema; do not recompute old hashes with newly added fields.

## Snapshot storage and permissions

Use Metadata Lakehouse Files, not Delta BLOB rows, for full notebook `.ipynb` snapshots. Illustrative URI:

`Files/fabricops/pipeline_snapshots/<execution-workspace-guid>/<pipeline-id>/v<version>/notebook.ipynb`

Registry stores the exact URI and expected SHA, not merely a filename-derived active marker. Create archive with write-once semantics: refuse overwrite; read back and verify before activating. Retain superseded versions. Protect archive from normal Engineering writes through actual tenant permissions; a directory name alone is not protection. Restrict Governance/metadata mutations independently of user-supplied `governance_confirmed` flags.

The snapshot and the physically cloned Governed notebook are distinct: never regard a mutable notebook item as the immutable archive. Keep Governed copies per version if needed for in-flight old runs; keep folders navigable and ensure schedules reference the intended active notebook. Promotion **must not silently migrate** engineer-owned schedules. Validate/how schedule targets are rebound to the new notebook and how stale schedules fail closed.

## Promotion state machine and recovery

1. Start from a **manually executed Dry Run** with relevant operation evidence. Snapshot complete development notebook, not only operation declarations; strip/ignore mutable execution outputs only in the executable digest, while retaining the original full snapshot.
2. Resolve logical resources through the destination workspace configuration, including intentional cross-workspace physical resources. Verify actual physical bindings and active Contracts for all sources/targets; validate Agreement context. Show Governance review of exactly what will execute and where.
3. Stage immutable archive in Metadata Files, verify by readback and SHA. Prepare new physical Governed notebook through supported Fabric APIs, verify retrieved saved definition. Ensure startup mode and governed runtime configuration cannot be tampered with through ordinary parameters; prevent startup with unapproved parameter overrides.
4. Compare expected currently active `pipeline_version`; reject stale governance approval. Atomically switch the prior active row to superseded and candidate row to active. Never expose two active versions, and do not lose previous authority if staging/clone fails.
5. Existing in-flight runs retain the version captured at admission; *new* runs directed to the old notebook refuse authorization. Validate writer coordination so simultaneous old/new versions cannot corrupt target or checkpoints.
6. On integrity mismatch, block Governed admission with a specific error (changed code, changed physical binding, missing snapshot, or verifier unavailable). Never fall back to Ungoverned.
7. Restore **exact active snapshot** by preserving the modified copy, replacing Governed notebook definition through Fabric API, readback-checking hash and approved bindings; reuse existing promotion only if byte/executable equivalence is proven. A different implementation goes via Dry Run + new promotion.
8. Rollback to a prior implementation is a **new reviewed promotion event** (prefer a new monotonically increasing version that points to/copied exact prior code; never mutate an old immutable approval row). Record lineage to the restored snapshot.
9. Fail closed on ambiguous missing/duplicate Registry identity, API failures, absent source/target Contracts, version mismatch, drift, races, stale schedule target, unavailable verifier, and missing/altered archives. Define how failed partial staged artifacts are identified without treating them as active.
10. If a privileged actor bypasses FabricOps and executes raw Spark, do not falsely claim the framework prevented it; distinguish policy-gated managed publication from tenant security.

## Migration: unreleased #1774 is breaking

- Replace the unreleased `record_type = control / pipeline_activation / table_contract_activation` Registry layout. No need to support #1774 callers indefinitely.
- **Do not silently destroy tenant data** even though #1774 has not shipped. Provide an explicit dry-run/report/backup-and-cutover procedure for any users running prerelease builds. Stop writers, preserve original rows/audit/snapshot evidence, map valid table Contract activations into the new Governance activation table, map pipeline candidates to `requires_review` (not active—no notebook snapshot attestation exists), and reject unsupported or ambiguous records.
- Never manufacture trusted notebook snapshots or mark migrated candidates active from Git SHAs, legacy deployment manifests, or old status flags.
- Keep released metadata tables, run histories, processing checkpoints, hashes, writer modes, and physical paths intact. Re-running setup must be idempotent.
- Update schema registration, setup/migration, API exports, source code, metadata docs generator, table diagrams, Governance and Engineering widgets, demos, release/upgrade instructions and PBIP consumer where required. Existing open docs/Power BI PRs (#1778/#1764 at planning time) may overlap generated files; coordinate/rebase rather than overwriting unrelated edits.

## Required acceptance and regression tests

- Canonical table count/ownership/schema and documented relationships.
- Global Contract definition immutability and independent per-physical-workspace activation; same Table ID activated at different versions in two workspaces; missing/ambiguous Contract and physical aliases reject.
- Same-workspace and cross-workspace promotion; destination config and full source/target physical binding review; config drift rejects; no accidental routing back to developer workspace.
- Frozen full notebook file retained; hash/readback/permission/API failure blocks; Markdown-only edit doesn't change executable digest; code, query, parameters and operation changes do.
- One active version per workspace/pipeline with racing approval, retry after lost acknowledgment, stale expected version and phantom insert tests.
- Manual and engineer-owned scheduled Governed starts use same admission; stale schedule pinned to superseded notebook rejects; change of schedule time allowed, change of behavior-affecting parameters rejected.
- Old in-flight runs complete under old captured version after promotion; new old-version starts blocked; collision of writes to same destination serialized or rejected using proven publication constraints.
- Full snapshot restoration without new promotion, changed-copy preservation and readback verification; modified code requires Dry Run/new version.
- Fail closed on API unavailable, snapshot missing/corrupt, verifier not authoritative, Contract mismatch, config drift, Agreement expiry; no fallback to Ungoverned.
- Historical Run validation/hash stability and exact Contracts per operation.
- Preserve `_row_hash`, `append_all`, `append_new_only`, overwrite, incremental, SCD1/SCD2, profiling, lineage, source observation, retries/publication receipts and Processing State.
- Fabric signed-in verification: notebook Get/Update/Create Definition, notebook ID stability and behavior under Run/schedule, identity permissions, OneLake File write/read, live Delta concurrent promotions, manual Run vs API preflight timing and TOCTOU limitations. Unit tests alone must not constitute a claim of secured Governed execution.

## Definition of done

The PR must contain functioning implementation, migration, widget updates, docs, tests, and a Fabric integration checklist. `Governed` cannot be advertised enabled merely by removing `DEPLOYMENT_PENDING` unless trusted checks actually work. Until then, keep it fail closed. Do not merge on green CI alone if Fabric-only security assumptions remain untested.
