# Pipeline Promotion architecture — v0.3.2

This maintainer reference defines the current metadata authority, execution invariants and concurrency guarantees. Governed admission remains blocked until the [Fabric acceptance checklist](governed-pipeline-fabric-acceptance.md) is complete.

## Canonical authority

The canonical inventory contains 13 tables. Metadata routes through the configured Metadata Lakehouse; the attached Lakehouse is not an implicit metadata destination.

| Table | Grain | Responsibility |
| --- | --- | --- |
| METADATA_DATA_CONTRACT | Contract ID/version | Immutable global frozen definitions; authoring workspace is evidence only |
| METADATA_DATA_CONTRACT_ACTIVATION | Physical workspace/Table ID | Exact active Contract ID/version/payload SHA and reviewed physical binding |
| METADATA_PIPELINE_REGISTRY | Execution workspace/Pipeline ID/version | Immutable notebook promotion, snapshot pointers/hashes, operation definitions and Agreement where applicable |
| METADATA_PIPELINE_RUN | Run ID | Actual operation outcomes, exact Contracts and captured promotion/execution provenance |
| METADATA_DATA_CATALOGUE | Workspace/table/column identity | Registered structures and processing definitions |
| METADATA_PROCESSING_STATE | Typed record ID | Source observations, accepted checkpoints, baselines and verified publication receipts |

Data Steward, Agreement, Profiled, Profiled Frequency, Lineage, Access and Guardrail Results retain their domain ownership. Contract Activation is Governance-owned. Registry contains only per-version pipeline records; coordination claims are held in Metadata Files.

## Setup and data preservation

`setup_metadata_tables()` creates missing tables and applies supported schema evolution directly. Compatible Catalogue and Pipeline Run collection fields are normalized to validated JSON strings in a pinned atomic Delta transaction. Missing nullable Run provenance columns are additive. Existing Run content/hash projections remain unchanged when added provenance is null. Existing Catalogue values, audit fields, extension columns, Delta identity/properties and transaction identities are retained.

Processing State checkpoints, source observations, accepted baselines and publication receipts remain unchanged. Setup never deletes metadata or business targets, empties checkpoints or infers missing accepted progress. Structurally incompatible schemas, malformed payloads and duplicate Run identities produce explicit errors while preserving existing data. No separate operator utility is part of setup.

## Promotion and exact physical routing

A completed manual Dry Run retains operation evidence and the complete saved notebook in memory without durable publication. Review binds the complete notebook, destination workspace, exact source/target physical bindings and effective Agreement where applicable. Every participant requires a separately activated frozen Contract in its physical workspace.

Operation definitions retain the requested schema choice separately from the resolved physical schema. `None` selects the destination store's configured default; explicit schema names stay explicit. Destination Table IDs and source/incremental target references are resolved consistently. Consumer context must match the entire activated physical workspace/item/kind/schema/table binding before a Data Agent can be provisioned.

Promotion archives complete source and promoted ipynb files with write-once semantics and exact readback checks. It creates a separate physical Governed notebook, including within one workspace. Metadata Files snapshots are distinct from mutable notebook items. Only approved startup choices are frozen into the setup call; the remaining notebook is retained. Imported packages and referenced notebooks are not frozen.

## Concurrency and replay

Registry mutation tracks a whole-table read under Serializable Delta isolation. Expected active version checks reject stale reviews. Superseding the old version and inserting the new active version occur in one transaction. A naive MERGE does not establish conditional uniqueness. Versions are scoped by execution workspace and Pipeline ID; superseded records remain.

Promotion IDs are replay-safe: exact retries return the recorded event, while changed content cannot reuse the ID. Lost acknowledgements are recovered from the exact transaction marker and versioned readback. Staging/clone failures do not alter prior authority; staged artifacts contain their promotion ID and confer no authority independently.

Ungoverned and Governed publication use the same exclusive physical-target claim protocol in `Files/fabricops/publication_coordination`. Contract Activation takes the same claim when changing table protection. Claims do not expire after a crash. Successful per-target release is recorded immediately; retries never remove another owner's claim or strand unrelated claims after a partial release.

New Governed starts must use the active physical notebook. Already admitted versions retain captured implementation and Contract references. The target claim prevents conflicting old/new writers from publishing concurrently. Next-run Contract resolution may adopt independently activated versions subject to validation.

## Integrity and runtime boundaries

Managed Governed boundaries verify immutable archives, saved executable content, destination configuration, exact physical bindings and Agreement effectiveness. Code, SQL, approved parameter or binding changes reject; Markdown-only edits may pass the executable digest. Missing/ambiguous authority, corrupt archives, unavailable APIs and inconsistent provenance fail closed without fallback to Ungoverned.

A preserved-copy integrity repair verifies the approved archived definition and saved readback. Immutable approval rows are not rewritten. Engineers own schedules and explicitly select their intended active notebook; promotion never changes schedules automatically. A schedule pinned to a superseded item rejects admission.

Saved-definition verification has TOCTOU limits: it cannot prove the executing kernel's code identity or prevent privileged direct Spark bypass. A Governed folder is organizational, not a permission boundary. Actual tenant permissions must restrict governance metadata and archives. These limitations and actual Fabric API behavior are mandatory acceptance evidence before enabling Governed admission.
