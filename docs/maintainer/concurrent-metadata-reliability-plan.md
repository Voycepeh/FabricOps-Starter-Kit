# Concurrent pipeline metadata and publication claims

Status: Implementation required. This design note is a blocking checklist for the accompanying draft PR; it is not a production fix.

## Failures reproduced in Fabric

1. Parallel, independent pipeline runs update `engineering.METADATA_PIPELINE_RUN` using a full-row Delta MERGE for each stage. A MERGE with a different run ID can fail with `DELTA_CONCURRENT_APPEND.WITHOUT_HINT`. The current four immediate retries are insufficient under real concurrency. The observed failure occurred while recording Profile evidence for `VW_PERPERSONAL_FREEZE`.
2. Ungoverned publication tries `DeltaTable.isDeltaTable` on `Files/fabricops/publication_coordination` in the central Metadata Lakehouse. OneLake returned HTTP 403 on its `_delta_log`. This is a hidden, noncatalogued Delta dataset with independent Files access, despite the documented metadata-table inventory.

## Required implementation

### Run evidence: remove shared mutable stage MERGEs

* Preserve a stable logical `run_id` and existing consumer-facing `METADATA_PIPELINE_RUN` contract or supply an explicitly versioned migration.
* Use uniquely identified append-only execution evidence per run/stage transition, with idempotent event IDs and deterministic ordering. Expose current status via a projection that can be queried from Fabric SQL endpoint and Power BI. Do not introduce a new mutable aggregate that MERGEs all unrelated runs back together at each stage.
* Maintain terminal-state and compare-and-set protections. A stale attempt must not silently move a terminal or later stage backward.
* A Delta append is **not** guaranteed conflict-free. Implement bounded, jittered retries for transient Delta concurrency errors only, with commit acknowledgement/read-back and duplicate suppression. Never blindly replay a business publication.
* Clarify exactly which event is authoritative after an interrupted or ambiguous acknowledgement.

### Publication coordination: remove undocumented Files Delta dependency

* No operational Delta ledger silently created underneath `Files/fabricops/publication_coordination`.
* Model publication claims as an explicit, provisioned and documented catalogued metadata table, **or** safely reuse an existing registered mechanism after proving atomic acquire/release and independent target concurrency. Avoid a new table if the existing structure can meet the requirements without conflating approval and execution.
* Claims are keyed by normalized **physical target**, not globally by workspace or metadata lakehouse. Independent destinations never compete for the same logical lease. The same target and aliases must remain mutually exclusive across Ungoverned writers and Contract Activation.
* Claims must be atomic and fail closed on conflicting owners. A crashed writer must require explicit reconciliation; do not simply expire its claim.
* Migrate existing `Files` claims safely: first read and reconcile old claims under an authorized identity, then cut over; never silently abandon a potentially active claim. Do not remove an existing ledger until its claims have been reconciled.
* Document the narrow OneLake permissions required by engineering and governance identities; do not require blanket Metadata Lakehouse Contributor access.

### Audit other metadata writers

Review `METADATA_PROCESSING_STATE`, profiling, Source Observation, Lineage, Guardrail results, Registry and Contract Activation for the same shared-table conflicts. Preserve checkpoint consistency and exactly-once publication evidence where needed.

## Mandatory verification

* 5, 10, and 20 independent pipelines, each with distinct targets, run simultaneously against a shared Metadata Lakehouse: all complete and retain complete evidence.
* Two writers targeting the same table, including aliases and mixed governed/ungoverned flows: at most one publication owner; the loser fails safely.
* Concurrent stage transitions for different Run IDs do not cause persistent `ConcurrentAppendException`.
* Same Run ID replay, stale stage update, terminal-state update, lost acknowledgement, and driver crash: no duplicate or regressed evidence.
* Empty and pre-existing ledger migration, cross-workspace narrow permissions, and absence of broad `Files/fabricops/publication_coordination` dependency.
* Existing Power BI-facing metadata columns and frozen release templates remain compatible or are deliberately migrated with tests.
* Fabric integration tests are required; local mocks alone do not establish OneLake/Delta concurrency guarantees.

## Release gate

Do not merge this PR based on this design note alone. Ship working code, migration/rollback documentation, and passing Fabric concurrency tests before marking ready for review.
