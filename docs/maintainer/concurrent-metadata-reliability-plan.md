# Shared Metadata Lakehouse concurrency

Multiple engineers and pipelines in different workspaces write to the same
Governance-owned Metadata Lakehouse. Distinct business targets do not prevent
Delta file conflicts inside those shared metadata tables.

## Target ownership and storage

Each business target has one owning pipeline. Schedules prevent overlapping
writes, including overlaps between old and new notebook versions. Stop that
pipeline before changing its Contract Activation. Ungoverned writes still reject
active protected Table IDs and physical destination aliases.

Publication claims and `Files/fabricops/publication_coordination` are no longer
part of runtime execution. No new claim table, Run event table, SQL view or consumer
migration is introduced. All 14 existing canonical schemas, Run JSON contracts,
checkpoint receipts and Power BI-facing columns remain unchanged.

Deploy the same updated package to every writer after stopping old executions.
Any old Files ledger is left untouched; archive or remove it only after confirming
that no old package still uses it. Runtime does not probe that location and needs
no access to its Delta log. Existing Engineering notebook snapshot/submission Files
permissions are independent and remain required.

## Retry contract

`fabricops_kit.io.shared.retry_delta_metadata` retries up to 32 attempts with
exponential, jittered backoff capped at eight seconds per delay. It recognizes
Delta's five aborted concurrency exception classes and structured Fabric error
conditions, including `DELTA_CONCURRENT_APPEND.WITHOUT_HINT`. It does not infer
retryability from exception messages.

Each attempt creates a fresh statement or pinned conditional transaction.
Metadata rows and intended scope stay fixed. Registry and Governance decisions
re-read the latest snapshot and re-evaluate their original expected revision;
a stale decision fails rather than overriding a newer one. Run stage MERGEs keep
the exact previous-row comparison and terminal-state protection. Existing Run and
Governance exact read-back protocols handle lost acknowledgements.

Permission failures, stale approvals, schema/protocol changes, and unknown commit
outcomes are not retried. Business target publication, SCD processing, sensitive
mapping writes and complete multi-step workflows are never wrapped in metadata
retry handling. An uncertain target commit must be reconciled, not replayed.

## Writer coverage

| Canonical table | Write path and preserved boundary |
| --- | --- |
| `METADATA_PIPELINE_RUN` | Retry first insert and stage MERGE; preserve transaction identity, exact previous-row comparison, terminal state and read-back. |
| `METADATA_DATA_CATALOGUE` | Retry scoped workspace/Table ID MERGEs and profiling marker updates; missing-column deactivation stays scoped. |
| `METADATA_DATA_PROFILED` | Retry deterministic snapshot/row-ID replacement MERGE and uncommitted-snapshot cleanup. |
| `METADATA_DATA_PROFILED_FREQUENCY` | Retry snapshot-scoped replacement and deletion; never retry the entire profiling workflow. |
| `METADATA_PROCESSING_STATE` | Retry one atomic record-ID MERGE; checkpoint/baseline progress still requires its publication receipt and physical target marker. |
| `METADATA_DATA_LINEAGE` | Retry workspace/lineage-ID MERGE. |
| `METADATA_GUARDRAIL_RESULTS` | Retry canonical Metadata append of aggregate results. |
| `METADATA_DATA_ACCESS` | Retry canonical Metadata append of scanner observations. |
| `METADATA_DATA_STEWARD` | Retry canonical Metadata append from authoring widgets. |
| `METADATA_DATA_AGREEMENT` | Retry canonical Metadata append of authored versions. |
| `METADATA_DATA_CONTRACT` | Retry authored-version append and conditional draft-save/freeze MERGEs; frozen versions remain immutable. |
| `METADATA_DATA_CONTRACT_ACTIVATION` | Retry a fresh Serializable transaction and recheck expected activation identity. |
| `METADATA_PIPELINE_ACTIVATION` | Retry a fresh Serializable submission/decision transaction and recheck exact expected review revision. |
| `METADATA_PIPELINE_REGISTRY` | Retry a fresh Serializable promotion transaction and recheck expected active version. |

Canonical Metadata append retries require both the configured `Metadata` store and
an exact canonical table name. Arbitrary business-table append/overwrite calls
retain their existing single-attempt behavior. Metadata setup/schema evolution
remains a maintenance task; it must complete before concurrent pipeline execution.

## Verification and Fabric acceptance

Local tests exercise structured conflict classification, retry exhaustion,
non-retryable failures, all canonical append routes and business-write isolation.
Real Delta tests exercise Run/stale-state/lost-acknowledgement behavior and shared
Run, Catalogue, profiling, Frequency, Lineage and Processing State records at
5/10/20 simultaneous workspace identities. Governance tests preserve stale-review
rejection and independent-workspace mutations.

Local Spark cannot establish Fabric/OneLake runtime or identity authorization.
Before production acceptance, run the following in signed-in Fabric:

1. Start 5, then 10, then 20 distinct-target pipelines with different engineers
   and execution workspaces sharing the configured Metadata Lakehouse.
2. Verify all Run operations/stages, exact Contract references, Profile/Frequency
   snapshots, Catalogue rows, Lineage, Guardrail results and Processing State
   receipts/checkpoints. Confirm no workspace's records were overwritten.
3. Exercise concurrent independent Governance decisions/promotions and scanner
   appends while the pipelines run. Verify same-record stale decisions reject.
4. Inject a transient Delta conflict and a lost acknowledgement; confirm metadata
   recovery does not replay target writes. Check interrupted target commits using
   existing physical publication markers and Processing State receipts.
5. Use the actual narrow Engineering/Governance OneLake permissions. Verify
   canonical table writes work and ordinary pipelines never request the removed
   publication coordination Files path. Re-run with SQL/Power BI consumers and
   confirm the unchanged table schemas and retained historical rows.

Sustained conflicts beyond the bounded retry budget still fail visibly. Record
actual Fabric outcomes before claiming production concurrency acceptance.

### Local results

The expanded shared-Delta workload passed at 5, 10 and 20 concurrent synthetic
workspace/user identities, retaining every Run, Catalogue, Profile, Frequency,
Lineage, Guardrail and Processing State record. The forced 20-workspace Registry
collision test passed, as did independent checkpoint/receipt package commits and
same-record stale-review rejection. The initial 12-attempt budget was insufficient
at width 20; the final bounded 32-attempt policy passed those workloads.

The domain unit suite passed 238 tests; the reference/architecture suite passed
159 checks (one existing release-dependent check was skipped). Ruff, Python
compilation, diff checks and a second no-diff reference generation passed. These
are local Delta and mocked-identity results. No signed-in Fabric identity is
configured in the implementation environment, so Fabric acceptance above remains
outstanding.
