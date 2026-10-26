# Pipeline metadata: Run-based activation

**Implementation:** pipeline activation selects an exact finalized Test Run. Registry and Run are the only pipeline metadata tables; there is no separate Definition or Configuration table.

## Automatic Catalogue nested-type upgrade

Install the new package and run the normal `setup_metadata_tables()` call before
resuming Catalogue writers. Fresh tables immediately use the canonical native
Spark schema. Existing `METADATA_DATA_CATALOGUE` tables are upgraded at their
configured Metadata Lakehouse and engineering schema location; no table rebuild,
column rename, parallel replacement column or manual conversion is required.

The exact names `load_strategy_parameters_json`, `scheduled_refresh_json` and
`profile_key_candidates_json` are retained. **Their `_json` suffix is historical:
all three contain native structs after setup.** Runtime code reads dictionaries
and ordered arrays and writes structured values. Contract documents and external
transport still use JSON. See the [current Catalogue schema](../reference/metadata/metadata_data_catalogue.md)
for every field and nested type.

### Conversion rules

The target fields match the current producers and the `v0.2.5` tag's
`pipeline_write.py`, `profile_table.py` and `scheduled_refresh.py`. Processing
retains all four optional parameter fields. Scheduled Refresh retains status,
all schedules, enabled flags, frequency, ordered times and timezone. Discovery
retains its status (including `resolved`, `unresolved` and `not_evaluated`),
maximum combination width and all six metrics for every ordered candidate.
No status or optional setting is inferred from the presence of candidates.

| Historical value | Native value |
| --- | --- |
| SQL null, JSON `null`, empty or whitespace-only string | SQL null (uncaptured) |
| `{}` | Non-null struct with null members |
| Explicit null member | Null member |
| Empty string member | Empty string member |
| Empty array member | Empty array, preserving its distinction from null |
| List-only key-candidate JSON, including `[]` | Struct with `status=null`, `max_combination_width=null`, and the original ordered `candidates` array |
| Discovery object | Original status, width and ordered candidates; absent members become null |

List-only candidates must be objects with the documented candidate fields, not
bare column names. Missing metrics stay null. Setup rejects unknown fields at
any depth, duplicate JSON keys, malformed JSON, invalid scalar/element types,
null array elements, non-finite numbers and integer overflow. Unsupported
physical types fail setup rather than being coerced. A mixture of string and
canonical struct columns is supported; native values are validated too.

### Atomicity, retries and recovery

Setup pins a Delta transaction snapshot and registers a whole-table read. It
strictly validates all three values and unrelated canonical types, then writes
the complete replacement to a separate durable staging path. All rows and
physical columns are retained, including inactive table/column rows, unexpected
extension columns and existing audit values. Setup never recreates row audit
timestamps. Table identity, existing properties, field metadata and configured
location are preserved. Mapped Delta tables retain existing physical column IDs
and names; Delta advances its internal ID allocator for the new struct members.

The transaction changes schema and replaces data files together in one atomic
Delta commit. Delta's metadata-changing whole-table transaction rejects
concurrent appends, updates and competing setup commits, including writers that
do not participate in a FabricOps lock. A stale replacement cannot overwrite a
newer row. Retry normal setup after a reported conflict.

The `evolved` Catalogue result clearly reports the automatic upgrade and includes
`pre_upgrade_version`, `upgrade_version` and `converted_columns`. Delta history
also records `fabricops_catalogue_upgrade` and `pre_upgrade_version` in commit
`userMetadata`. Setup reads the exact committed version back and verifies schema
and every replacement row, including duplicates and unaffected values.

An interruption before commit leaves the original Catalogue intact. An
interruption after commit, including lost acknowledgement, leaves the native
Catalogue authoritative: rerun setup to validate it without conversion or another
commit. Temporary staging files from a terminated process may be removed once no
upgrade attempt is using them. Failed transactions can leave unreferenced Delta
data files; use the normal retention-aware Delta maintenance process.

**Rollback boundary:** automatic rollback is never performed. Retain Delta
history and files until the upgrade has been accepted. If recovery requires the
pre-upgrade version, stop all Catalogue writers, confirm that the current head
is exactly the recorded upgrade commit, and restore the pre-upgrade version with
the matching older package. If any later valid write exists, restoring the old
version would discard it: reconcile those writes into a separately reviewed
recovery instead. Do not restore over subsequent writes or run an old package
against the native schema.

This upgrade changes only Catalogue's three structured fields. Steward and
Agreement `custom_fields_json`, other Agreement fields, profile calculations,
statistical/frequency tables, Pipeline Run, Activation State and Processing State
are unchanged.

## Responsibilities

| Owner | Stored facts |
| --- | --- |
| `engineering.METADATA_PIPELINE_REGISTRY` | Permanent pipeline/notebook registrations, immutable approvals of finalized Tests, environment selections/revisions, table ownership, Live/rebind reservations and profiling claims |
| `engineering.METADATA_PIPELINE_RUN` | One execution with native table operations, exact contract references, locations, read/write modes, statuses, stages, timing, profiling and safe failures |
| `governance.METADATA_DATA_CONTRACT` | Versioned table-level schema, grain, quality, sensitive-data, processing and profiling policies |
| `governance.METADATA_DATA_AGREEMENT` | Versioned authored Agreements referenced by approvals |
| `engineering.METADATA_GUARDRAIL_RESULTS` | Exact rule-level results tied to `run_id`, table and contract version |
| `engineering.METADATA_DATA_LINEAGE` | Observed source/target participation following successful Live publication; this Live schema is unchanged |
| `engineering.METADATA_PROCESSING_STATE` | Accepted incremental checkpoints, drift baselines and publication recovery; this schema/protocol is unchanged |

Governance owns approval decisions even though Registry is physically in Engineering. The confirmation in the activation widget is an explicit workflow action, not an authenticated Governance role check. Configure Fabric permissions and notebook execution identities deliberately; schema placement and atomic transactions do not establish independent approval authorization.

## What an operation records

Each Run operation records `operation_key`, `table_id`, `pipeline_role`, nullable exact `contract_id`/`contract_version`/`payload_sha256`, physical `destination`, `read_mode` or `write_mode`, nullable `query_sha256`, `incremental_target_table_id`, and `source_table_ids`, plus actual status, timing and stages. The SQL hash protects an approved Warehouse Read without retaining SQL text. Source associations describe pipeline participation, not proven DataFrame transformation edges.

These are the fields Live checks. Do not retain project configuration, arbitrary Read/Write argument dictionaries, Spark settings, diagnostics options or configuration fingerprints. Processing keys, watermarks and write-strategy rules remain owned and validated by the selected table contract. Profiling/discovery schedules come from that contract and physical table completion history. Grain Guardrails execute independently of optional grain discovery.

No Contract remains valid for exploratory Test. Every operation needs a valid frozen contract before activation. Test operations are in memory; explicit `finalize_pipeline` publishes allowed Test results and Guardrail diagnostics, never business writes, checkpoints, Catalogue or Lineage.

## Test, approval and Live

1. Setup resolves a permanent pipeline UUID and notebook binding. Test discovers source/target participation through actual orchestrator calls.
2. Each operation records its table, exact selected contract, binding, mode and outcome. The notebook still executes its own transformation code.
3. Explicit finalization requires all discovered operations to complete and records the whole-run boundary. Parent status and native operations publish in one Run transaction. A partial diagnostic write cannot make a Test approvable.
4. The activation widget lists successful finalized Tests by pipeline/environment. Governance selects an exact Test and Agreement version and supplies an immutable pipeline approval label.
5. Approval revalidates required stages, complete rule-level diagnostics, exact contracts, Test notebook binding and Agreement effectiveness. Registry retains the Test ID and result integrity hash, Agreement version/hash, decision labels and audit. No second configuration document is created.
6. One Registry compare-and-swap publishes approvals, active selections, coordinated table/contract/writer mappings and the environment revision atomically. Shared tables must use one exact contract/binding per environment; each target has at most one writer. Affected running pipelines drain before cutover.
7. Live setup resolves the exact retained Test and approved contracts and reserves the execution under the same Registry token. Before each operation, the orchestrator validates table, location, source associations, mode, SQL hash and incremental target. A materially different call fails before the operation executes.
8. Live records actual outcomes and releases only its own pinned reservation. Explicit finalization checks completion; it does not undo earlier business publications. Observed Lineage remains recorded if publication succeeds before a later stage fails.

**Approval does not verify arbitrary notebook transformation code, scan future cells or replace notebook code with stored configuration.** No notebook-code fingerprint is claimed. Changed notebook bindings require a new finalized Test and approval. The kernel's cell-completion hook detects failures; it cannot prove whole-notebook success.

## Querying actual table and contract participation

```sql
SELECT r.run_id, r.pipeline_id, r.environment_name,
       op.table_id, op.pipeline_role, op.contract_id, op.contract_version,
       op.read_mode, op.write_mode, op.status
FROM engineering.METADATA_PIPELINE_RUN r
LATERAL VIEW explode(r.operations) observed AS op;
```

Use the configured physical Engineering schema. No Definition/Configuration join is required. For per-rule outcomes, join Guardrail Results by `run_id` and exact table/contract/rule identity without multiplying operation counts.

## Transactions and retained history

Registry has one setup-seeded central row. Registration, approval, admission, rebind and renewable profiling claims use one matched-only Delta MERGE with an expected token. There are no runtime child inserts or per-update DDL. Missing/duplicate authority fails closed. Approved decision history and permanent registrations are retained. A lost acknowledgement is accepted only after exact complete-content read-back.

Run has one native row per `run_id`. First publication uses a stable Delta transaction identity; subsequent updates compare the complete previous row. Terminal outcomes are immutable and failed runs cannot regress to success. Parent, operations/stages, profiling and safe failures publish together. This preserves the existing whole-run concurrency and recovery guarantees without a Definition append or join.

Approved Tests, frozen contracts, Agreements and rule results must remain retained and unchanged. Approval hashes protect result integrity, not notebook configuration identity. Missing, duplicated or changed retained references block approval/Live; there is no latest-version fallback.

## Preserved Processing State protocol

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

## Joint redesign rollout and reset policy

This is a breaking Preview layout change. The six supported Live schemas and Processing State remain unchanged. Setup refuses incompatible Registry/Run layouts; it never adds columns to reinterpret history, drops tables or automatically resets checkpoints.

1. Stop Test/Live producers and activation; drain reservations and profiling claims. Back up affected tables with their exact Delta versions and package revision.
2. For disposable Preview Registry/Run history, make an explicit reset decision. Create the new Registry and Run tables only after the old layout is backed up. Do not drop or rebuild supported Live tables or Processing State.
3. For retained approvals/history, reconcile each old run's operation membership, exact contract references, bindings and modes into the new native operation array. Revalidate retained Test diagnostics and Agreement versions; old definition/candidate IDs cannot be relabeled as run IDs. Do not invent missing successful operations or notebook bindings. If required facts cannot be established, rerun Test and approve a new run rather than asserting equivalence.
4. Old `METADATA_ACTIVATION_STATE` snapshots and the unmerged #1707 Definition layout are not runtime readers or aliases. Preserve any required history before explicit cleanup. The former Run converter applies only with its historical #1700 package/layout and must not run against this schema.
5. Validate unique run/approval identities, immutable terminal history, exact result hashes, table/contract/writer mappings and empty reconciled reservations before enabling Live. Retain backups and the previous package/schema boundary for rollback; never mix writers from the two layouts.

## Verification and deployment boundaries

Regression coverage exercises actual operation capture, selective Live rejection, finalized Test approval, shared-table/writer conflicts, rebind and admission races, immutable history, stale transactions, lost acknowledgements, profiling claims and unchanged supported Live schemas. Local Spark/Delta checks do not prove actual Fabric permissions, Lakehouse concurrency/cutover or Warehouse recovery. Validate those in the deployment environment before enabling Live.

## Metadata retirement guidance

`RETIRED_PREVIEW_METADATA_TABLES` in `metadata_schemas.py` remains the source for advisory cleanup notices. Setup probes known names in the configured schemas without collecting old rows or migrating/deleting their data. Retired Preview tables do not authorize execution.

### Logical keys and schema ownership

Registry remains physically in the configured Engineering schema. Governance owns approval decisions; Engineering executes registration, admission, reservations and profiling coordination against the same atomic row. Its position beside Governance tables in the diagram shows that shared responsibility and does not introduce a third physical schema.

Registry's row key is `authority_id` (the singleton `central`); Run's row key is `run_id`. Registry collection keys are validated separately: registrations and selections use `(environment_name, pipeline_id)`, approvals use `approval_id`, revisions use `environment_name`, ownership uses `(environment_name, table_id)`, reservations use `(environment_name, reservation_id)`, and profiling claims use `claim_key`. A Run operation is unique by both `operation_key` and `(table_id, pipeline_role)` within its Run.

Registry approvals reference `Run.run_id` through `testing_run_id` and Agreement's composite `(agreement_id, agreement_version)`. Run's nullable `approval_id` references a nested Registry approval; Test runs have no approval. Run operations and Registry ownership reference Contract's composite `(contract_id, contract_version)`. Retained hashes verify content as well as identity. These are application-enforced references; Delta does not enforce SQL primary or foreign key constraints. Table IDs refer to logical table identities; Catalogue's physical row key also includes environment and column identity, so `table_id` alone is not a foreign key to its full row key.
