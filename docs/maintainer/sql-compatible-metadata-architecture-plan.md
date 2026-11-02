# SQL-compatible metadata architecture and migration plan

Planning proposal for review; no runtime change is authorized by this document.

## 1. Executive summary

Recommend **B: an atomic operational Registry with relational reporting projections**. Keep `METADATA_PIPELINE_REGISTRY` as the singleton authority and keep `METADATA_PIPELINE_RUN` as one authoritative snapshot per execution. Convert their nine top-level nested columns, and Catalogue's three nested columns, to physical Spark `string` containing validated JSON. Preserve application dictionaries/lists through centralized codecs at persistence boundaries. Extract reportable collections into physical relational Delta tables. Live authorization and profiling eligibility continue to read authoritative committed state.

The benefit is SQL endpoint visibility without replacing the existing concurrency protocol. A fully relational authority would require a new distributed transaction/admission design; JSON alone would leave core Power BI questions unanswered. Projections introduce explicit eventual consistency, storage and repair work. Publish complete reporting generations and expose their source versions so a partial refresh cannot look current.

Keep all current relational tables, especially `METADATA_DATA_PROFILED` and `METADATA_DATA_PROFILED_FREQUENCY`. Do not duplicate Run headers, Contracts, Agreements, Lineage, Guardrail Results, Processing State or Data Access. Keep Scheduled Refresh discovery and stored values. Do not introduce aliases or runtime readers for old layouts. Supported historical physical representations are migration inputs only.

**Implementation requires approval of the physical schema change, projection set, publication protocol, maintenance window and reporting freshness policy in section 10.** No application code, generators, metadata stores, release snapshots or implementation PRs are changed by this audit.

## 2. Audit scope and verified current state

### Baseline and evidence

Audited GitHub `origin/main`, fetched on 2 November 2026, commit `389b04ebf9ebf4f67e945326c9cc87c42bf90c55` (v0.3.1 preparation). The checked-out source matched that fetched head and began clean. This is a source audit, not an inspection of a deployed Lakehouse or a Fabric SQL endpoint.

Primary source anchors (paths relative to repository root):

| Source | Verified responsibility |
| --- | --- |
| `AGENTS.md`; `.agents/skills/fabricops-docs-maintenance/SKILL.md` | Live data preservation, configured metadata routing, source ownership, generated-artifact and planning boundaries |
| `src/fabricops_kit/config/metadata_schemas.py` | Twelve canonical tables; physical schemas, logical nested fields, coercion and strict Catalogue validation |
| `src/fabricops_kit/config/setup_metadata_tables.py` | Creation, schema validation, additive evolution, Registry seeding, atomic Catalogue string-to-native migration, per-table partial-failure reporting |
| `src/fabricops_kit/activated_pipeline/shared.py` | Registry read/validation, retained Test/Agreement verification, activation, CAS, reservations, consumer contract resolution |
| `src/fabricops_kit/pipeline/shared.py` | Registration, session setup, operation capture, Run persistence, canonical JSON/hashes, profiling history, profile/frequency/Catalogue persistence |
| `src/fabricops_kit/pipeline/setup_pipeline.py`; `finalize_pipeline.py` | Public lifecycle boundaries, explicit Test publication, display-only summaries |
| `src/fabricops_kit/pipeline/orchestrate_read.py`; `orchestrate_write.py`; `pipeline_read.py`; `pipeline_write.py`; `check_source_drift.py` | Execution admission, read/write checks, publication recovery, target processing and schedule capture |
| `src/fabricops_kit/widgets/widget_activate_pipeline.py`; `widget_data_contract.py` | Exact Test approval and release review; Catalogue key-candidate consumption |
| `src/fabricops_kit/data_contract/shared.py`; `scheduled_refresh.py`; `src/fabricops_kit/data_agent/shared.py` | Draft processing seed, schedule discovery/normalization, deliberate schedule exclusion from contract payloads, residual agent freshness consumption |
| `tests/unit/test_catalogue_nested_types.py`; `tests/integration/test_catalogue_upgrade_delta.py` | Strict values; historical JSON/list conversions; real Delta staging, conflict, recovery, extra-column and column-mapping coverage |
| `tests/integration/test_pipeline_registry_delta.py`; `test_pipeline_run_delta.py`; `test_joint_pipeline_metadata_delta.py` | Registry stale-CAS/races; whole-run atomicity and terminal immutability; exact retained approval references and lost acknowledgements |
| `docs/reference/_data/glossary.json`; `docs/maintainer/metadata-v2-target-model.md`; `docs/reference/metadata/*.md` | Canonical terminology and documented current model, cross-checked against source |
| `scripts/generate_individual_function_reference_pages.py` (`generate_metadata_reference_pages`); `scripts/reference_docs_metadata.py` | Owning generator and source metadata for affected references |

Source is decisive where documentation/tests differ. In particular, portions of `metadata-v2-target-model.md` still refer to `environment_name`; current physical Registry/Run identity uses `workspace_id`. Some Catalogue integration tests still expect schedule hydration in the widget, while current contract-authoring code and unit tests explicitly remove `table.scheduled_refresh`. These are existing inconsistencies to reconcile in the scoped implementation documentation/tests, not reasons to remove stored schedules.

### Transaction boundaries that must survive

- Registry: exactly one `authority_id='central'` row; setup seeds it with `errorifexists`. Missing/duplicate authority fails closed. `commit_pipeline_authority` uses a matched-only MERGE and raises inside the transaction on a stale token. All six collections, token and audit publish together. Permanent registrations and approval history are retained. Lost acknowledgement is accepted only on exact complete-content read-back.
- Approval: exact finalized successful Test, required operation stages, rule-level diagnostics, current notebook binding, exact frozen Contract hashes and exact Agreement version/hash. Registration alone grants no activation. Governance confirmation is a workflow confirmation, not an independently authenticated role check.
- Current public mode boundary: `setup_pipeline` accepts Dry Run, Ungoverned and Governed. `finalize_pipeline` preserves explicit publication for historical `testing` plans; this audit does not establish a current public path to create a new Testing plan. Retained Testing runs remain approval dependencies. Confirm the intended Test producer before rollout; adding a new mode is separate API scope.
- Governed admission: `build_live_pipeline_plan` reads registration and authority consistently, pins approval/revision/contracts/physical bindings, then reserves under the same Registry CAS. `verify_live_plan` rechecks authority during execution. Activation/rebind conflict checks share this domain.
- Run: first publication uses a stable Delta transaction identity, with no bounded `delta.setTransactionRetentionDuration`; updates compare the entire previous row. Terminal outcomes are immutable, stale writers fail, failure cannot become success. Operations, stages, profiling and failures commit with the parent. Projection failure must not enter `plan.evidence['failures']` or make a committed Test unapprovable.
- Profiling: `profiling_completion_history` explodes authoritative Run `profiling` in Spark and verifies actual summary/frequency snapshots. Empty-frequency and grain completion markers matter. `record_profiling_outcome` rolls back an in-memory event if authoritative persistence fails. This is execution scheduling state, not reporting.
- Profile history: summary/frequency rows have snapshot identities; replacement is limited to one snapshot. Frequency may exist without summary metrics (`profile_id` null). Preserve these cases and existing snapshot history.
- Catalogue and Lineage are separate from business publication and Processing State commits. No new cross-table atomicity claim is introduced.

### All twelve affected physical columns: decisions and dependency matrix

`C` = `METADATA_DATA_CATALOGUE`, `R` = `METADATA_PIPELINE_REGISTRY`, `U` = `METADATA_PIPELINE_RUN`. Every row below converts the physical column to `string`; “Extract” additionally means a derived physical table, never a second authority. Exact current types are recorded in Appendix A.

| Column; current Spark type | Purpose and authoritative writer | Readers/dependencies | Power BI field need | Decision; migration/concurrency risk |
| --- | --- | --- | --- | --- |
| C.`load_strategy_parameters_json`; struct | Watermark, processing keys, effective and tracked columns. `pipeline_write._persist_target_processing`; profile Catalogue merge preserves existing processing | `catalogue_authored_processing`, `check_source_drift`, `data_contract.shared` draft seed; Catalogue consumers | Scalar `load_strategy` already supports strategy counts; key membership is not required by minimum reporting questions | **Convert**, retain internal processing JSON; decode before `.items()` and existing validation. Preserve arrays/order and coalesce semantics; malformed values must not become defaults |
| C.`scheduled_refresh_json`; struct | Discovered writer notebook schedules/status. `pipeline_write._writer_scheduled_refresh` + `_persist_target_processing`; Catalogue profile merge preserves it | Stored Catalogue readers; current authoring deliberately strips contract schedule; older tests expect widget hydration; agent reads historical contract `table.scheduled_refresh`, a different field | No schedule analysis requested in minimum model | **Keep / Convert**; retain discovery, enabled flags, local times, zones and unavailable/not-configured distinction. No schedule removal or invented agent integration |
| C.`profile_key_candidates_json`; struct | Grain-discovery status/width and candidate metrics. `_persist_profile_observation`, `_persist_grain_candidates`, Catalogue upsert | `widget_data_contract` discovery suggestions; draft/UI workflows | Minimum profiling charts use summary/frequency. Candidate ranking could be a later requirement | **Keep / Convert**; preserve large counts, doubles, array ordering, null versus empty. Update direct Spark struct literal update |
| R.`registrations`; array of structs | Permanent pipeline/workspace/notebook bindings and registration audit. `commit_pipeline_registration` through Registry CAS | `read_pipeline_registry`, registration resolution, `start_pipeline_session`, approval/current-binding checks, activation widget | Yes: identities, names, status, registered date | **Convert / Extract** registration; preserve timestamps, identity uniqueness and permanent history; compare decoded content |
| R.`revisions`; array of structs | Workspace activation revision. `pipeline_authority_row` through CAS during activation | `read_pipeline_authority`, pinned admission, reservation checks | Yes: workspace even with zero active pipelines; activation revision | **Convert / Extract** workspace revision; not an ordered integer, not the Registry token |
| R.`approvals`; array of structs | Immutable decision labels and exact Test/Agreement references, warnings and audit. `approve_pipeline_release` → CAS | `approval_record`, `testing_run_evidence`, activation, Live, consumer contract resolution, widget | Yes: who approved which Test/version/Agreement | **Convert / Extract** approval; retain all hashes and timestamps byte/semantic equivalence; migration must not recompute IDs/hashes |
| R.`selections`; array of structs | Current approval selected per workspace/pipeline. `approve_pipeline_release` → CAS | `read_pipeline_authority`, activation impact, Live, consumer resolution | Yes: active pipelines and authorizing approvals | **Convert / Extract** selection with joined workspace revision. Current state only; cannot reconstruct full activation timeline |
| R.`table_ownership`; array of structs | Exact shared Contract and binding, optional writer, reader pipeline set. `activation_impact` → CAS | activation conflicts, Live plan validation, approved consumer resolution, Ungoverned admission safeguards | Yes: writer, readers, shared tables, active table Contract | **Convert / Extract** ownership and reader bridge; keep one writer and one binding/Contract per workspace/table |
| R.`reservations`; array of structs | Live/governed/rebind/profiling coordination, table sets, physical destinations, pinned revision. Admission/release/rebind and profiling routines → CAS | conflict/rebind/drain checks, `verify_live_plan`, session cleanup | Not required for governance/operations dashboards; short-lived reservations are not run history | **Keep / Convert**, internal JSON only; never clear reservations to migrate. Preserve exact pinned data and stale-CAS behavior |
| U.`operations`; array of structs | Actual Read/Write membership, exact Contracts/bindings/modes/SQL hash, sources, status, clocks and stages. `pipeline_run_row` → `persist_pipeline_run`/`_merge_pipeline_run_row` | approval validation, live approved-operation comparison, summaries, widget, Test integrity hash | Yes: failed/slow operations, sources and stage outcomes | **Convert / Extract** operation, source bridge and stage. Keep authoritative parent snapshot; independent child writes cannot authorize success |
| U.`profiling`; array of structs | Context-specific activity/outcome, snapshot link, empty/grain markers and physical location. `record_profiling_outcome` → Run commit | **Operational** `profiling_completion_history`, profile scheduling and Test publication; completion reports | Yes for completion/history, gaps and snapshot relationship; metrics already relational | **Convert / Extract** profile event; runtime parses authoritative JSON in Spark, never projection; physical descriptor/context must survive |
| U.`failures`; array of structs | Safe code/exception type only. Operation/session failure paths and finalization → Run commit | run validation, summaries, approval eligibility | Yes: failure reasons and counts | **Convert / Extract** failure; preserve ordered occurrences, including duplicate codes; never persist raw exception messages |

**Remove: none of the business structures.** Replace the contradictory Catalogue string-to-native upgrade implementation and its current-schema expectations; retain its historical fixtures and safeguards. Do not remove historical release snapshots, retained Tests, Contracts, Agreements or diagnostics.

### Nested members beyond the twelve top-level columns

A recursive review finds **no thirteenth top-level nested column and no MapType in the twelve canonical schemas**. `*_json` strings elsewhere are already scalar even when their logical contents are nested. Subtrees that a top-level-only inventory can miss are:

| Parent | Additional complex paths (`[]` denotes array element) | Treatment |
| --- | --- | --- |
| C.load strategy | `.key_columns`, `.tracked_columns` | Ordered arrays inside JSON |
| C.schedule | `.schedules`, `.schedules[]` struct, `.schedules[].times` | Preserve JSON and local schedule semantics |
| C.candidates | `.candidates`, `.candidates[]` struct, `.candidates[].columns` | Preserve JSON and candidate order |
| R.all collections | Every collection element is itself a struct | Flatten reportable element scalars |
| R.approvals | `[].warnings` | JSON string plus warning count in approval projection; no warning dimension required |
| R.ownership | `[].readers`, `[].destination` struct | Reader bridge and flattened destination fields |
| R.reservations | `[].tables`, `[].destinations`, `[].destinations[]` struct | Internal JSON only |
| U.operations | `[].destination` struct, `[].source_table_ids`, `[].stages`, `[].stages[]` struct | Flatten destination, source bridge, stage child |
| U.profiling | `[].physical` struct | Flatten physical fields in profile event |

Preserve extra user extension columns. If they themselves are nested, report the table as still having SQL-invisible columns; do not silently convert unrelated data or claim whole-table SQL compatibility. Retired tables are advisory inventory, not automatic migration inputs.

## 3. Target physical schemas

### Operational storage and serialization

Retain the twelve existing table names, routing, scalar fields and audit fields. Change only the twelve inventoried physical types to `StringType`, retaining column names (including Registry/Run names without `_json`). Logical schemas remain separate typed contracts for validation and Spark `from_json`; do not change logical arrays into strings throughout application code.

Use shared architecture-visible codec functions in `config/metadata_schemas.py` (or the existing owning shared modules if that avoids cross-domain dependencies), with no compatibility wrappers. Encode once on physical write, decode once on physical read. Audit all direct DataFrame reads/writes, `createDataFrame`, coercion, Spark literals, `.items()`, `.get()`, `explode`, `event.*`, full-row CAS and exact read-back. `coerce_metadata_row_types` must not silently convert dictionaries to Python `str(dict)`.

Codec rules: strict JSON, duplicate-key rejection, finite numbers, schema/type/range validation, deterministic object-key encoding, preserve array ordering, explicit null fields, ISO microsecond timestamps with UTC instant normalization matching `pipeline_record_content`. Decode typed Registry timestamps to datetimes where existing callers require them; Run profile `completed_at`/`executed_at` are logically strings today and must remain strings in hash-bearing logical objects. Do not change `canonical_pipeline_json`, `manifest_digest`, Contract payload bytes, approval IDs or existing Test/Agreement hashes as a side effect. Test these with retained pre-conversion approvals.

Add **one proposed scalar** to Run: `reporting_snapshot_sha256:string`, digest of normalized committed Run content excluding this digest itself. Compute it in the same authoritative Run commit; include it in physical CAS/read-back. This is a reporting join fence, not approval authority or a replacement for Test hashes. Do not expose it in existing public Run return dictionaries or include it in `pipeline_record_content` used for legacy approval hashes. Separate physical encoding from logical return values explicitly. Historical rows are populated atomically during supported migration, including JSON-only Run schemas missing this new field.

This additive fence costs a schema change but avoids a duplicate Run header table and prevents children from a previous Run state joining a newer authoritative header. Without approval of this field, use a complete versioned Run reporting snapshot including a duplicated header; do not pretend direct joins to the current parent are coherent.

### SQL type contract

All proposed fields use only Spark `string` → SQL `varchar`, `integer` → `int`, `long` → `bigint`, `boolean` → `bit`, `timestamp` → `datetime2`, `double` → `float`, or existing `date` → `date`. No physical Array, Struct, Map, binary, variant or timestamp-NTZ in new tables. Use UTC for timestamp instants; retain schedule timezone and local times in strings. Hash/key values remain strings; do not infer UUID SQL types. Validate actual SQL endpoint lengths and Unicode behavior on Fabric before release, especially long JSON and arbitrary operation keys. A SQL string mapping does not guarantee unrestricted payload length.

Keys below are **logical, application-validated uniqueness/FKs**, not enforced Lakehouse constraints. All new tables live in the configured Engineering metadata schema and use the configured Metadata Lakehouse. Proposed names below are proposals, not existing canonical tables.

Common projection columns: `generation_id:string`, `source_delta_version:long`, `projected_at:timestamp`, `projection_schema_version:integer`. A Registry row also carries `registry_token:string`; each Run child carries `run_id:string`, `reporting_snapshot_sha256:string`. Include `generation_id` in every physical projection key. All unspecified IDs/names/status/hash/mode/reason fields are strings; counts/ordinals/booleans/times have explicit types below. Registry generation is global for that physical singleton, not one independent publication per workspace.

### Registry projections: six tables

| Proposed table | Grain and key within generation | Physical business columns |
| --- | --- | --- |
| `METADATA_PIPELINE_REGISTRATION` | `(workspace_id,pipeline_id)` | All scalar `REGISTRATION_FIELDS`, including `registered_at:timestamp` and all eight original audit fields (audit `_committed_at:timestamp`, others string) |
| `METADATA_PIPELINE_WORKSPACE` | `workspace_id` | `workspace_id`, `activation_revision` (from `revisions[].revision`) |
| `METADATA_PIPELINE_APPROVAL` | `approval_id` | All approval scalars: approval/pipeline/workspace IDs, pipeline name/version, testing run ID/hash, Agreement ID/version/hash, original audit; replace nested warnings with `warnings_json:string`, `warning_count:integer` |
| `METADATA_PIPELINE_SELECTION` | `(workspace_id,pipeline_id)` | `workspace_id`, `pipeline_id`, `approval_id`, `activation_revision` |
| `METADATA_TABLE_OWNERSHIP` | `(workspace_id,table_id)` | `workspace_id`, `table_id`, `contract_id`, `contract_version:integer`, `payload_sha256`, `writer_pipeline_id` (nullable), `reader_count:integer`, `is_shared:boolean`, `activation_revision`; flattened destination below |
| `METADATA_TABLE_READER` | `(workspace_id,table_id,reader_pipeline_id)` | Workspace/table/reader IDs and `activation_revision` |

Destination flattening: `destination_workspace_id`, `destination_item_id`, `destination_kind`, `destination_schema`, `destination_table_name` (all strings; schema may be null). Do not confuse destination workspace with execution workspace.

`is_shared` means more than one **distinct participating pipeline** in union of writer and readers; a pipeline both reading and writing the same table counts once. It does not mean data-access permissions or external sharing. Reader-only shared tables are valid.

Selections carry their revision to simplify reporting; workspace rows preserve environments with no selections. Do not add a separate activation event or revision-history table: the authority retains current revisions/selections and approval history, not every past selection transition. The selection's approval is the authorizing decision; the approval label is not a workspace revision. If activation history is required later, approve a separate committed event-history design rather than inventing dates from current-state snapshots.

Existing Lineage records observed source/target participation, often after successful publication, with notebook audit; it cannot replace active ownership/readers or an approval-linked registration. Do not overload it with proposed activation authority.

### Run children: five tables, reusing the existing Run header

| Proposed table | Key within one Run generation | Physical business columns |
| --- | --- | --- |
| `METADATA_PIPELINE_RUN_OPERATION` | `(run_id,operation_key)` | `operation_key`, `table_id`, `pipeline_role`, nullable exact Contract ID/version:int/hash; flattened destination; `read_mode`, `write_mode`, `query_sha256`, `incremental_target_table_id`, `status`, `started_at:timestamp`, `completed_at:timestamp`, `duration_seconds:double` |
| `METADATA_PIPELINE_RUN_SOURCE` | `(run_id,operation_key,source_table_id)` | `operation_key`, `source_table_id`; application FK to the source-role operation in that Run by table ID |
| `METADATA_PIPELINE_RUN_STAGE` | `(run_id,operation_key,stage_ordinal)` | `operation_key`, `stage_ordinal:integer`, `stage`, `status`, nullable `evaluation_status` |
| `METADATA_PIPELINE_RUN_PROFILE` | `(run_id,event_ordinal)` | `event_ordinal:integer`, context key, activity/status, `results_persisted:boolean`, `empty_result:boolean`, snapshot ID, `completed_at_text`, `executed_at_text`, parsed nullable `completed_at:timestamp`, `executed_at:timestamp`, reason, table ID, `row_count:long`, trigger, workspace ID, pipeline run ID, flattened `physical_*` destination fields |
| `METADATA_PIPELINE_RUN_FAILURE` | `(run_id,failure_ordinal)` | `failure_ordinal:integer`, code, nullable exception type |

Retain event ordinals from the authoritative array, not a potentially nonunique context key. Stages preserve order and unsuccessful historical occurrences; do not deduplicate. No raw failure text or full SQL. Duration is elapsed operation wall clock when both timestamps are valid, otherwise null; flag invalid/negative clocks in synchronization diagnostics instead of fabricating zero. Current persisted stage fields lack durations, and Run lacks persisted row-throughput metrics shown in same-session summaries. Slow **operations** are supported; historical stage duration/throughput claims are not. Adding those measurements is separate scope.

Normalize profile event/status and failures because operational completion gaps and failure-code analysis cannot be answered from existing metric tables. Summary/frequency remain the sole physical metric facts. Warnings remain JSON; add scalar counts only where useful. This avoids new warning, destination, Contract payload, processing-key, schedule or key-candidate tables until concrete reporting requirements justify them.

### Reporting synchronization manifest

Propose `METADATA_REPORTING_SYNC`, with logical key `(source_table_id,scope_id)` where source_table_id is the physical Delta table identity (not a business table ID), and scope_id is `central` for Registry or a Run ID. Fields:

- Strings: `source_table_id`, `scope_id`, `source_table_name`, `generation_id`, `source_registry_token` (Registry only), `source_run_sha256` (Run only), `status` (`ready`/`stale`/`failed`/`building`), `last_error_code` (safe), `publication_token` (manifest CAS).
- Longs: `source_delta_version`, `observed_delta_version`, `projected_row_count` (total across child tables).
- Integer: `projection_schema_version`.
- Timestamps: `source_committed_at`, `last_observed_at`, `synchronized_at`, `last_attempt_at`, `last_failure_at`, `sql_verified_at` (nullable).

`generation_id` and its source fields always describe the last **complete published** generation. Before first publication they are null. Attempts/failures never advance that pointer or overwrite the last complete source identity. A status is a stored observation, not a live freshness guarantee; last-observed age must always be visible. Store per-child row counts/checksums in each projection table's Delta commit metadata and validate them before publication; zero-row tables still have a validated completion marker in that commit. Do not require an extra nested manifest column.

## 4. Authority and reporting synchronization protocol

### Registry family

1. Read the Registry's exact committed Delta snapshot at version V and decode/validate the singleton. Retain token T, source physical table identity and source commit time. Do not synchronize from the caller's uncommitted state or from a CAS request that later failed.
2. Build a deterministic generation ID from source table identity, V and projection-schema version. Flatten the six projections. Validate uniqueness, selection → approval → registration/workspace links, ownership/readers/contracts and source counts. Registry mutations may advance the token without changing an activation revision.
3. Idempotently write each generation as a bounded generation replacement/MERGE, including removal of surplus rows **only within that unpublished generation**. Never overwrite the live whole reporting tables. Verify every table against its expected data and completion marker, including empty projections. A retry after a crash reconstructs the same output.
4. Publish the manifest pointer in one matched CAS (initial row creation must be concurrency-safe). Reject lower V, conflicting output for the same generation, stale publication tokens and incompatible transform versions. Delta version orders committed snapshots; random Registry tokens/revision strings cannot order freshness. A superseded builder cannot move the pointer backwards.
5. Read the current Registry head to record observed lag. The published generation remains valid as an **as-of snapshot** even if newer authority exists. Retry/coalesce to the newest head on the next synchronization; no need to materialize every short-lived reservation-only commit.

Atomicity spans each Delta table and the manifest pointer, not all tables. Completed rows precede pointer publication, so Spark readers following the pointer see a complete generation. Raw unfiltered tables intentionally contain old/unpublished generations; their names must not imply “current”. Readers must filter to the manifest generation.

### Run family

Read committed Run snapshots, validate and flatten all five children for each changed Run. Generation is deterministic from source table identity, Run ID, committed `reporting_snapshot_sha256` and transform version; include source Delta V as provenance. Publish one manifest pointer per Run only after every child is complete. A new incomplete/failed Run state is legitimate reportable state; do not wait only for successful terminal runs. Explicitly finalized Tests use their committed Run after diagnostics publication.

Join existing Run header to manifest on Run ID **and** `reporting_snapshot_sha256=source_run_sha256`, then children on Run ID and generation. A newer parent with old children is “awaiting synchronization”, not zero operations or success. Parent-only failure/status reports can use the existing scalar Run independently while displaying child freshness. A missing manifest must remain visible through a left join.

For initial implementation use a distributed, batched scan of Run IDs/digests versus published manifests; no driver collection of all Run history. Full rebuild is supported from current committed rows without Change Data Feed. Incremental CDF can be a measured optimization later, with full-scan fallback after retention gaps. Terminal runs need no regeneration unless transform version changes. A rebuild at the same source version may replace output only under an explicitly ordered new transform version, never an arbitrary competing builder.

### Invocation, failures and recovery

Use a single domain-owned synchronization implementation shared by setup/rebuild and an explicitly runnable repair path. Planned owner: architecture-visible functions in `activated_pipeline/shared.py` for Registry projections and `pipeline/shared.py` for Run projections, reusing configured I/O and schemas. Do not add a generic mutation framework. A maintainer-facing repair callable, if approved, needs its own public owner file and exports, not a shim.

After confirmed authority commits, attempt synchronization as a best-effort reporting step. It must be outside Registry CAS/Run commit exception scopes and outside lost-acknowledgement content comparisons. In particular, reporting failure must not replay admission, leave a false authoritative failure, invalidate Test hashes or hide a successful activation. Return/log a safe reporting-lag diagnostic through existing setup/warnings conventions. If even manifest failure recording fails, age/source-version comparison still exposes missing freshness.

Post-commit hooks alone are insufficient: a process can die between authority commit and hook. Initial proposal: a separately scheduled repair sweep every five minutes, plus explicit setup/rebuild and post-commit attempts; scheduling infrastructure and freshness SLA need approval. Coalesce Registry work and rate-limit post-commit attempts to avoid eleven child writes on every reservation/Run update. No projection catch-up on the authorization critical path is required.

Retention: retain current and previous complete Registry generations plus generations pinned by an active report refresh, and a configurable grace period exceeding the longest report refresh/SQL synchronization delay. For Run, retain the published generation and the same grace protection. Cleanup is a separate reviewed maintenance operation, never deletion of authoritative rows. Failed/unpublished generations can be rebuilt; do not use a timeout alone to delete an active builder's staging files.

### SQL endpoint and Power BI consistency

SQL endpoint table synchronization is asynchronous and independent for each table. A manifest row becoming visible in SQL does **not** prove all child files/rows are visible there. `sql_verified_at` records a bounded observation only; it is not a distributed commit barrier.

For the first release, use Power BI **Import with controlled refresh** for consistent multi-table reports. The refresh controller captures Registry generation and per-Run pointers once, checks SQL visibility/schema and expected per-table keys/counts against pinned Spark output, imports all tables filtered to those captured identities, then atomically publishes the semantic-model refresh. If verification fails/times out, keep the previous successful model and show its as-of time. Do not reread “latest generation” independently for each table. Use typed physical columns, not Power Query JSON expansion.

Direct Lake/DirectQuery may expose temporary stale/partial discovery across SQL tables. They need a tested generation-pinning/visibility strategy before claiming consistent dashboards. Simple latest-manifest views can be convenient SQL adapters over these physical tables but are not a replacement for physical facts, and do not alone solve endpoint visibility races. Live never uses any of these paths.

## 5. Minimum Power BI model and question coverage

Build stable composite relationship keys in the semantic model (or approved scalar hash keys if needed); Power BI relationships are not composite SQL FKs. Avoid ambiguous automatic many-to-many paths and bidirectional filtering. Every Registry relationship includes the same generation; Run child relationships include Run ID and generation/hash fence.

| Question | Physical facts and join path |
| --- | --- |
| Registered pipelines | Registration; logical key workspace + pipeline; use a distinct pipeline dimension in the semantic model for cross-workspace identity |
| Active per workspace | Workspace → Selection → Registration; Selection → Approval. Left join from Workspace preserves zero-active environments. Use configured workspace identity; display environment labels from existing configuration/semantic dimension, not an invented persisted environment field |
| Authorizing approvals | Selection.approval_id → Approval → existing Run by testing_run_id; Approval → Agreement by `(agreement_id,agreement_version)`; retain hashes as verification fields |
| Active table Contract | Ownership `(workspace_id,table_id)` → Contract `(contract_id,contract_version)`; compare stored payload hash. Contract status alone does not mean active |
| Writer/readers/shared | Ownership.writer_pipeline_id → Registration in same workspace; Reader → Ownership and Registration; use `is_shared` definition above. Reader membership comes from committed active authority, not historical operations |
| Failing pipelines | Existing Run scalar status/workspace/pipeline, completion time; include incomplete and currently running separately from terminal failed. Define “latest” with started_at plus run_id tie-breaker, never assume run IDs sort by execution time |
| Failed/slow operations | Run → fenced Operation; status and duration; Stage drilldown; Failure for run-level code. No fabricated operation-level failure code FK because current failures do not retain operation identity |
| Source associations | Operation → Run Source → source-role Operation by table ID within the same Run. This is declared participation, not proven DataFrame transformation lineage |
| Profile distributions | Existing Profiled (`profile_id`, snapshot, workspace/table/column) and Frequency (`frequency_id`, snapshot + workspace/table/column, nullable profile_id); profile event joins via snapshot and context/workspace/table |
| Last synchronized | Reporting Sync: source/observed versions, last attempt, last complete sync, failure code, SQL verification and last report refresh time |

Use a semantic Table dimension from Catalogue **table-level** rows only; column rows form a separate table/column dimension. Catalogue has multiple physical rows per table across columns/workspaces; never join `table_id` directly to the unfiltered full Catalogue as a one-side dimension. Observed Lineage remains a separate historical participation fact and Data Access a separate permission snapshot fact.

Profiled key is `profile_id` (derived from snapshot + column); Frequency key is `frequency_id`. Standard relationship uses non-null `profile_id` plus matched snapshot/workspace/table/column checks. For frequency-only profiles, use a distinct snapshot/table/column dimension and left joins; never invent summary rows or drop distributions for a null profile_id. Run Profile can have multiple activities/events for one snapshot, so aggregate it before joining metric facts to avoid multiplication. Guardrail Results are rule-level: aggregate or drill through by Run/table/Contract/rule rather than multiplying operation/profile measures.

Preserve original audit timestamps and source timestamps. `projected_at` and `synchronized_at` are reporting transport times and must not be used as original registration/approval/execution dates.

## 6. Idempotent setup migration and recovery

### Supported inputs and preflight

`setup_metadata_tables()` becomes the automatic entrypoint for the approved conversion; no manual drop/reset is required. It recognizes **enumerated** physical schema signatures, not arbitrary coercible data:

| Input | Action |
| --- | --- |
| Missing table | Create canonical string schema with `errorifexists`; seed Registry once with six encoded empty arrays, existing authority ID/token/audit rules. On creation race, reread and validate the winner; never overwrite it |
| Current native schema | Strictly validate logical values; convert affected fields and data in a pinned transaction; preserve all scalar/audit values |
| Already target JSON schema | Validate all documents and Run digest if present; no schema/data rewrite when canonical/valid |
| Supported historical JSON without Run digest | Preserve documents/decoded meaning; atomically populate digest without changing existing evidence hashes |
| Mixed native/string affected columns | Classify each field independently, decode/validate, encode canonical target; one commit per affected table |
| Historical Catalogue blank JSON or list-only candidates | Retain existing documented interpretation: blank/whitespace → SQL null; candidates list → object with null status/max width, ordered candidates. Do not apply this exception to Registry/Run |
| Unknown types, missing required Registry/Run collections, retired authority layouts, corrupt documents, duplicate identities | Fail closed with table/column/reason and recovery guidance; no inference from current latest Contracts, no automatic reset |

At setup start, preflight all three affected authoritative tables and configured routes before mutation. Record source table IDs, versions, protocol, properties and schema signatures. Registry/Run require exact supported field sets (except explicitly allowed migration additions); Catalogue retains additive evolution and unrelated extensions. Missing required facts in old Preview models remain an explicit reconciliation task under existing guidance. This conversion does not reinterpret retired Activation State or Processing State schemas.

### Writer coordination and commit design

A Delta metadata-changing commit conflicts with concurrent writers at that commit; it does not permanently fence an old notebook that starts a later transaction. Therefore **drain/pause all affected writers and activation and restart them with the new package before resumption**. This deployment prerequisite must be documented; automatic setup conversion does not imply zero-downtime mixed-version support.

No reliable cross-table deployment lock currently exists. Do not infer quiescence from an empty reservation list, and do not automatically clear abandoned reservations. Before conversion reconcile existing live/rebind reservations and in-flight writes. Runtime schema guards in the new package reject old physical types and instruct setup; old packages are not allowed to coexist. Retain deployment access controls through the conversion window.

1. Pin the transaction's source snapshot, `readWholeTable`, source files, schema and table identity; reread from that exact version, not the earlier probe.
2. Validate **all rows** and logical nested types, including preserved strings. Materialize durable staging at a unique configured-Metadata sibling path. Staging severs read lineage before replacement. Validate row multiset, preserved scalar/audit fields, semantic nested equality, uniqueness/reference rules and digest/evidence invariance before commit.
3. Change physical schema and remove/add all replacement files in the **same optimistic Delta transaction**. Preserve Delta identity, properties, protocol, partitioning and unrelated column mapping IDs/physical names; changed nested subfields are removed from the physical schema only as part of their parent string conversion. Include migration ID/version, pre-upgrade Delta version and target schema version in commit metadata.
4. Preserve all existing transaction identity actions, especially Run's first-publication deduplication history. Do not clone-and-swap tables, alter table IDs, or use a normal overwrite after a check. Verify Fabric's Delta transaction API for supported runtime versions before release; existing Catalogue code uses internal JVM APIs and Delta constructor-version handling, not a portable multi-table transaction service.
5. On Delta conflicts, discard/revalidate the stale attempt and reread committed head. If another setup already completed, validate and no-op. Retry only bounded, recognized conflicts; malformed data/auth/storage failures stop. Never retry an uncertain commit by replaying pipeline/business operations.
6. Read the exact committed version back and compare schema plus before/after semantic **multisets**, preserving duplicate Catalogue rows and unrelated extensions. Then compare current head for intervening writes. Only verified authority may initialize projections.

Do not add automatic schema merging to Registry/Run that silently reintroduces native columns. All direct writers and readers must move with the same package release. Setup can commit Catalogue, Registry and Run separately: no global atomicity is claimed. A partial upgrade leaves data preserved but operational readiness blocked until every required authority has the target schema and validation succeeds. Existing per-table setup results should retain created/evolved/validated/failure distinctions and add migration versions/reporting warnings without renaming public fields.

### Value preservation rules

- SQL null means absent/uncaptured. JSON `[]` means an explicitly empty collection; `{}` means an empty object, interpreted with the logical contract's nullable fields. Never serialize SQL null as the text `"null"`, and never turn empty lists into SQL null. Required Registry/Run collections must remain arrays; null is invalid. Preserve historical scalar empty strings where they are valid.
- Reject duplicate JSON keys, trailing data, unknown unsupported fields, wrong root types, null elements where forbidden, booleans presented as integers, overflow, NaN/Infinity and invalid timestamps. Do not let permissive Spark `from_json` silently turn invalid values into null; use strict validation first and fail-fast decoding thereafter.
- Preserve order of arrays, all nested null fields, long counts beyond 2^53, integer bounds, finite floating-point values and Unicode. No lossy intermediate conversion through JavaScript/float for integer counts.
- TimestampType values use UTC instant/microsecond normalization consistent with existing hash/read-back logic; fix Spark session timezone during conversion. Keep timezone offsets/local schedule intent and existing string timestamp semantics. Compare pre/post decoded content and all retained Test hashes. JSON text itself need not equal historical whitespace/key order unless referenced by an existing hash; Contract payload JSON bytes are never rewritten.
- Catalogue `coalesce(source,target)` behavior must preserve its current null-versus-explicit-empty distinctions. Update `_persist_grain_candidates` to write a validated encoded string instead of using the old struct schema. Decode Catalogue before draft/source-drift/widget consumers.

### Recovery, rollback and repeated setup

Before commit interruption: source remains authoritative, staging is disposable after confirming no live builder uses it. Commit with lost acknowledgement: inspect table identity/history/schema and migration metadata, validate committed data and rerun setup; never assume failure means no commit. A bad-data/unsupported-schema failure performs no commit on that table. Post-commit verification failure blocks readiness and retains recovery data; no automatic restore.

Record per-table pre-upgrade and committed versions and retain durable backups/files beyond the acceptance period; suspend vacuum that would remove recovery data. No automatic rollback over later writes. An offline restore is permitted only after stopping writers, confirming the head is exactly the migration commit, and deploying a mutually compatible previous package/schema pair. Because migration spans three tables, rollback/recovery must reconcile the entire package/schema set. If later valid writes exist, use a reviewed forward repair from retained versions and new writes; a blanket Delta RESTORE would lose them. Business target/Processing State boundaries must remain intact.

Repeated successful setup validates target documents without re-encoding/recommitting authority. Validate complete projections and reuse their generation when source/transform is unchanged. On partial projection initialization, rebuild/retry only derived output. Setup operational readiness and reporting readiness must be distinguishable; a projection failure cannot masquerade as fresh reporting or corrupt operational authority.

### Fabric acceptance gate

In a representative schema-enabled Lakehouse with custom configured governance/engineering schemas: migrate fresh/native/string/mixed copies; validate SQL endpoint discovery of all scalar columns; compare SQL types, row counts, Unicode/large JSON, keys and typed timestamps against Spark. Check actual endpoint propagation and empty-table visibility, then exercise controlled Power BI refresh with an interrupted projection generation. Fail the rollout on missing fields/truncation or unverified Delta conflict semantics. Local tests cannot establish these Fabric properties.

## 7. Tradeoff analysis

| Criterion | A. Relational authoritative Registry | B. Atomic Registry + projections (recommended) | C. JSON-only Registry |
| --- | --- | --- | --- |
| Implementation complexity | Highest: replace coordination across registrations/approvals/ownership/admission | Moderate: codec/migration plus replayable projection publisher | Lowest persistence change; decoder audit still substantial |
| Operational safety | Depends on new transactional protocol | Preserves existing singleton and whole-Run invariants | Preserves existing invariants |
| Concurrency | Could scale by workspace/entity, but cross-table ownership/admission needs transactional storage or a serialized coordinator | Existing singleton contention remains; reporting never blocks authorization | Same singleton contention |
| Data consistency | Atomic only with redesigned coordination; separate Delta MERGEs are insufficient | Strong within authority, explicit eventual consistency to generation-pinned reports | Strong authority; consumers implement parsing independently |
| Reporting latency | Low after commits plus endpoint lag | Projection/sweep delay plus endpoint/semantic refresh | Endpoint lag plus per-consumer parse work |
| Power BI usability | Excellent relational facts | Excellent typed relational facts with freshness contract | Poor for reader/source/stage relationships; fails stated requirement |
| Migration risk | Highest: changes authority and transaction boundaries | Medium: lossless type conversion with retained authority/projection rebuild | Medium-low, still breaking physical types and hash/decoder risk |
| Maintenance burden | New coordination/transaction architecture | One codec contract, explicit publisher/rebuild, generation retention | Low library code; duplicated downstream JSON models and correctness burden |
| Volume/extensibility | Best potential if authority storage redesigned carefully | Singleton rewrite/approval validation grows; Run projections scale incrementally | Same authority growth, increasingly costly reporting parsing |

B is the simplest option that satisfies both safety and physical reporting requirements. Its projections do not solve the singleton's scalability. Today each Registry mutation serializes retained approvals and `read_pipeline_authority` reconstructs/verifies retained references; admission can scale poorly as history grows. Measure Registry JSON bytes, CAS conflict rate, admission latency, approval count, projection lag and Run scan costs. Establish tested limits during Fabric validation. Do not silently archive approval references still needed by Live or prune permanent registrations. Revisit A with measured pressure and an explicit new transaction service/partition strategy, rather than pretending independent relational Delta tables can share current CAS guarantees.

## 8. Ordered implementation PR plan

No PR is opened by this planning task. Each PR must keep `main` deployable; do not merge canonical schema flips separately from their migration and all required consumers. Proposed new files are explicitly labeled. Paths below are repository-relative.

### PR 1 — Logical codecs and authoritative read/write boundaries

- **Objective:** centralize logical/physical serialization while keeping current native schemas and behavior on main until the cutover PR. No transitional public API. Dependency: architecture decisions approved.
- **Files:** `src/fabricops_kit/config/metadata_schemas.py`; `src/fabricops_kit/activated_pipeline/shared.py`; `src/fabricops_kit/pipeline/shared.py`; `src/fabricops_kit/pipeline/pipeline_write.py`; `src/fabricops_kit/pipeline/check_source_drift.py`; `src/fabricops_kit/data_contract/shared.py`; `src/fabricops_kit/widgets/widget_data_contract.py`. Change public owner files only where source audit shows a direct physical boundary. Codec string mode is used for tests, not dual-schema runtime fallback.
- **Source:** separate logical validation from physical schema, route native boundary encoding/decoding through shared owners, add strict JSON codec and golden fixtures; retain native output until PR 2. Explicitly cover `authority_records`, `_read_pipeline_run_rows`, `metadata_records`, `start_pipeline_session` direct Registry reads, Spark profiling-history decode, Catalogue literals and draft/widget readers.
- **Tests:** `tests/unit/test_catalogue_nested_types.py`, `test_pipeline_registry.py`, `test_pipeline_run_records.py`, `test_pipeline_run_evidence.py`, `test_table_profiling_schedules.py`, `test_contract_authoring_services.py`, `test_widget_data_contract.py`; new `tests/unit/test_metadata_serialization.py`. Retained approval/Test hash equivalence, timestamp and numeric round trips, corrupt JSON rejection. Native-path regression remains required.
- **Migration validation/acceptance:** no physical migration yet; golden logical content/hashes and public dictionaries match. Native Registry stale-CAS/Run terminal tests pass.
- **Generated:** directly affected function references and call-flow artifacts only under ownership procedure below; no metadata physical reference flip yet.
- **Rollback:** revert code-only PR with native schema unchanged.

### PR 2 — Atomic setup conversion and canonical string cutover

- **Objective:** ship all twelve physical conversions, supported automatic migration and Run reporting digest together. Dependency: PR 1 and validated Delta runtime approach.
- **Files:** `config/metadata_schemas.py`, `config/setup_metadata_tables.py`, `activated_pipeline/shared.py`, `pipeline/shared.py`, `pipeline/pipeline_write.py` under `src/fabricops_kit/`; any direct boundary owners identified in PR 1; `scripts/reference_docs_metadata.py`; `AGENTS.md` (replace native physical descriptions); `docs/maintainer/metadata-v2-target-model.md`. Preserve historical release documents/manifests.
- **Source:** replace Catalogue's canonical migration direction in its existing owner; no competing old conversion path. Add enumerated Registry/Run migration, logical/physical digest separation, strict target guards, fresh creation race handling, readiness blocking for partial schema upgrade. Keep current setup public parameters/results and Run return shape.
- **Tests:** update `tests/unit/test_config.py`, `test_metadata_schemas.py`, `test_catalogue_nested_types.py`, `test_metadata_writer_ownership.py`, `test_scheduled_refresh.py`, `test_pipeline_profile_observations.py`, `test_finalize_pipeline_summary.py`; extend `tests/integration/test_catalogue_upgrade_delta.py`, `test_pipeline_registry_delta.py`, `test_pipeline_run_delta.py`, `test_joint_pipeline_metadata_delta.py`; new `tests/integration/test_sql_metadata_upgrade_delta.py`. Update native SQL-explode expectations to decoded authoritative Spark and later relational report queries.
- **Migration validation:** fresh/native/string/mixed including each individual mixed column; blank/list-only Catalogue; unchanged repeated setup; null/empty, UTC microseconds, large longs, duplicate rows/extensions, column mapping/properties/transaction IDs; corrupt/unsupported schema before mutation; setup/writer races, blind appends, lost acknowledgements, pre/post staging interruption, partial three-table recovery. Run exact preexisting approval/Live/profiling scheduling fixtures after conversion.
- **Acceptance:** row multiset and exact retained approval hashes preserved; no reset; migration rerun no authority commit; stale-CAS/immutable terminal/run first-publication semantics unchanged; targeted real-Delta tests pass and Fabric canary completes before general rollout.
- **Generated:** metadata schema pages plus directly affected individual function references; machine call-flow output only if its content changes; glossary only if a canonical definition actually changes.
- **Rollback:** pre-write offline compatible package/schema restoration at exact migration heads; otherwise forward repair. Do not revert to old physical writers while new schemas remain.

### PR 3 — Registry relational projections and generation publication

- **Objective:** publish six Registry reporting tables and the synchronization manifest without changing authorization. Dependency: PR 2.
- **Files:** `src/fabricops_kit/config/metadata_schemas.py`; `config/setup_metadata_tables.py`; `activated_pipeline/shared.py`; `pipeline/shared.py` (registration post-commit integration); `scripts/reference_docs_metadata.py`; `docs/maintainer/metadata-v2-target-model.md`; `tests/unit/test_metadata_schemas.py`, `test_metadata_writer_ownership.py`, `test_activation_state_commit.py`, `test_widget_activate_pipeline.py`; new `tests/unit/test_metadata_reporting.py`, `tests/integration/test_metadata_reporting_delta.py`.
- **Source:** schemas/routing, pinned snapshot builder, complete-generation validation, manifest CAS, safe post-commit diagnostics, setup initialize/rebuild. No projection reads in admission/activation validation.
- **Tests/migration:** populated Registry backfill; zero selections/readers; reader-only tables; same pipeline read/write; reference integrity; midway crash; empty projection completion; stale/out-of-order builders; repeated same generation; lost pointer acknowledgement; rejected CAS never projected; synchronization failure after successful activation/registration never changes authority outcome.
- **Acceptance:** all six physical tables reconstruct one committed Registry snapshot and stale-data status is visible. Custom metadata routing and full rebuild after deleting only disposable test projections work.
- **Generated:** new metadata references/ownership descriptions and affected function references via owning generator; call-flow output if changed.
- **Rollback:** disable projection hooks/refresh; preserve authority. Prior projection generation can be reselected only as explicitly stale reporting, never rollback operational state. New derived tables may remain inert; cleanup is separate.

### PR 4 — Run children, repair sweep and Power BI model

- **Objective:** five Run child tables, scalable per-Run synchronization and controlled reporting refresh. Dependency: PR 3 (shared manifest publication contract).
- **Files:** `src/fabricops_kit/config/metadata_schemas.py`; `config/setup_metadata_tables.py`; `pipeline/shared.py`; `activated_pipeline/shared.py` (shared manifest integration if required); `scripts/reference_docs_metadata.py`; new `docs/maintainer/sql-metadata-reporting.md`; approved repair public owner `src/fabricops_kit/config/synchronize_metadata_reporting.py` and `config/__init__.py`, `public_api.py` only if a public repair API is approved. No dashboard frontend changes.
- **Source:** operations/source/stage/profile/failure schemas, digest-fenced joins, batched digest scan, retries/rebuild, repair invocation and documented scheduling deployment; pinned SQL/Power BI import queries and semantic relationship definitions. No second physical Run header table.
- **Tests:** extend `tests/unit/test_metadata_reporting.py`, `tests/integration/test_metadata_reporting_delta.py`, `test_pipeline_run_delta.py`, `test_joint_pipeline_metadata_delta.py`, `test_table_profiling_schedules.py`, `test_pipeline_profile_observations.py`; verify partial Running→failed/final updates, superseded Run generation, duplicate failure/profile events, nullable contracts, frequency-only snapshots, query hashes and destination workspace separation.
- **Migration validation:** full retained Run backfill, digest discovery after lost hook, terminal skip, rebuild at new transform version, no driver history collection; simulate parent advance between child writes and pointer publication. Regression proves runtime profiling still ignores projections.
- **Acceptance:** every minimum question in section 5 answered from typed physical tables; no JSON expansion in Power BI; failed refresh preserves previous model; source/SQL/report freshness visible; timed Fabric concurrency/propagation canary and chosen SLA pass.
- **Generated:** new schema references, directly affected public/internal function references and call-flow contract as applicable; no dashboard or release regeneration.
- **Rollback:** stop reporting repair/refresh, revert projection-specific behavior with operational codec/schema retained, rebuild derived output using last approved projection version. Never revert an approved operational migration as a reporting rollback.

### Generator and validation procedure for all implementation PRs

Retrieve relevant callable slices using `scripts/query_public_function_call_flow.py` before function-level edits. Update canonical schema/docstrings and `scripts/reference_docs_metadata.py`, never generated reference pages manually. If callable structure/source locations/relationships change, run `PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py`; commit `docs/reference/_data/public-function-call-flows.json` and its `generated-artifacts.json` timestamp only when contract content changes.

Run `PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py` for directly affected references, including its metadata-page output, then run it **again and confirm no second-run diff**. Expected directly affected outputs include `docs/reference/metadata.md`, `docs/reference/metadata/*.md`, affected `docs/api/reference/*.md`, `docs/reference/index.md`. `AGENTS.md` also lists `docs/reference/function-call-graph.md`, but that path is absent at this baseline; the existing explanatory page is `docs/function-call-graph.md`. Verify actual owning-generator outputs rather than creating or hand-editing the absent path. Exclude unrelated output churn. Validate affected metadata/reference freshness tests and targeted runtime/Delta tests, Ruff/syntax as appropriate and `uv run mkdocs build --strict` using a temporary site directory. Do not regenerate `docs/assets/public-function-call-flows-dashboard.html`. Do not update release snapshots/manifests/versioning or generated timestamps for validation alone.

The current planning change must run **none** of those generators. Its verification is source/schema inventory, document links/structure, diff scope and a documentation build only if that build can respect the no-generator boundary.

## 9. Risks and unresolved deployment facts

| Risk | Required resolution before rollout |
| --- | --- |
| Hash drift from timestamps, missing fields or physical digest leakage | Golden retained approvals, exact Test/Agreement verification after migration; separate logical objects from physical encoding |
| Old writers after schema conversion | Enforced maintenance/restart plan; no claim of mixed-version concurrent operation |
| Independent SQL propagation of tables/manifest | Fabric visibility checks and controlled pinned Import refresh; no unsupported Direct Lake consistency claim |
| Existing docs and stale schedule-related integration assertions | Reconcile with current source, preserve discovery/storage, correct documentation to workspace IDs and current contract ownership |
| Internal Delta JVM transaction API/protocol differences | Test supported Fabric runtime versions, column mapping and transaction identity retention; fail unsupported runtime without mutation |
| Singleton and retained approval growth | Measure serialized size, CAS conflicts and admission latency; choose deployment limits before production expansion |
| Five-minute repair/sync SLA may be too slow or costly | Confirm cadence, scheduling owner, coalescing, operational budget and acceptable stale age |
| Long JSON/string or operation keys exceed endpoint limits | Validate real endpoint types, lengths and Unicode; do not truncate authoritative JSON or join keys |
| Raw projection tables queried without generation filter | Document pinned query contract; semantic model applies filters and visibility validation |
| Nested user extension columns remain | Preserve data and report incomplete SQL visibility; separately review extension conversions |
| Run digest changes public/hash-bearing content | Keep digest physical-only, add regression tests for return shapes/hashes; approval is required for the added field |
| Current public Test-production path is unclear | Confirm how new approvable Tests are produced; preserve retained historical testing behavior and avoid silently adding a new public mode |
| Historical activation timeline absent | Report current active state plus retained approvals only; request new event authority separately if needed |

No actual metadata volumes, workspace permissions, schedules or endpoint capabilities were available in this source audit. These are deployment acceptance facts, not reasons to invent defaults or claim validation already passed.

## 10. Recommended decisions for approval

1. Approve B: keep singleton Registry and whole-Run authority; convert the twelve physical nested columns to validated JSON strings with unchanged logical/public contracts.
2. Approve six Registry projections, five Run child projections and one synchronization manifest; keep all existing relational facts and avoid duplicate Run/Contract/Profile headers. Keep revisions and selections logically separate but include revision in selection rows; extract readers separately from ownership.
3. Approve the physical-only Run digest fence, including exclusion from public return objects and existing approval hashes. If rejected, choose the explicitly duplicated versioned Run reporting header alternative before implementation.
4. Approve eventual reporting consistency, generation publication, best-effort hooks plus scheduled repair, initial five-minute sweep target, and controlled Power BI Import refresh with SQL visibility checks. Confirm final stale threshold and scheduling owner before PR 4.
5. Approve a coordinated drain/restart maintenance window and retention-backed recovery boundary. Setup conversion is automatic; supported Live data is never reset/dropped/truncated. Preserve historical release snapshots.
6. Preserve Scheduled Refresh and Catalogue candidate/processing payloads as JSON for this scope; do not add their relational children until users require field-level analytics. No removal of these functions or values is proposed.

Proceed in the four focused PRs only after these decisions are reviewed. Fabric canary validation remains a release gate; local source inspection cannot approve a production cutover.

## Appendix A. Exact current nested Spark type inventory

The following inventory was read from the canonical schema registry at the audited commit, including its no-PySpark fallback. It describes the existing schema, not the proposed target.

### METADATA_DATA_CATALOGUE.load_strategy_parameters_json

```text
struct<watermark_column:string,key_columns:array<string>,effective_column:string,tracked_columns:array<string>>
```

### METADATA_DATA_CATALOGUE.scheduled_refresh_json

```text
struct<status:string,schedules:array<struct<enabled:boolean,frequency:string,times:array<string>,timezone:string>>>
```

### METADATA_DATA_CATALOGUE.profile_key_candidates_json

```text
struct<status:string,max_combination_width:int,candidates:array<struct<columns:array<string>,column_count:int,row_count:bigint,distinct_count:bigint,uniqueness_percent:double,null_count:bigint>>>
```

### METADATA_PIPELINE_REGISTRY.registrations

```text
array<struct<pipeline_id:string,workspace_id:string,notebook_id:string,notebook_name:string,registered_at:timestamp,registered_by:string,registration_status:string,_committed_by:string,_committed_at:timestamp,_workspace_id:string,_workspace_name:string,_notebook_id:string,_notebook_name:string,_metadata_lakehouse_name:string,_activity_id:string>>
```

### METADATA_PIPELINE_REGISTRY.revisions

```text
array<struct<workspace_id:string,revision:string>>
```

### METADATA_PIPELINE_REGISTRY.approvals

```text
array<struct<approval_id:string,pipeline_id:string,workspace_id:string,pipeline_name:string,pipeline_version:string,testing_run_id:string,testing_evidence_sha256:string,agreement_id:string,agreement_version:string,agreement_sha256:string,warnings:array<string>,_committed_by:string,_committed_at:timestamp,_workspace_id:string,_workspace_name:string,_notebook_id:string,_notebook_name:string,_metadata_lakehouse_name:string,_activity_id:string>>
```

### METADATA_PIPELINE_REGISTRY.selections

```text
array<struct<workspace_id:string,pipeline_id:string,approval_id:string>>
```

### METADATA_PIPELINE_REGISTRY.table_ownership

```text
array<struct<workspace_id:string,table_id:string,contract_id:string,contract_version:int,payload_sha256:string,writer:string,readers:array<string>,destination:struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>>
```

### METADATA_PIPELINE_REGISTRY.reservations

```text
array<struct<workspace_id:string,reservation_id:string,pipeline_id:string,mode:string,tables:array<string>,revision:string,destinations:array<struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>>>
```

### METADATA_PIPELINE_RUN.operations

```text
array<struct<operation_key:string,table_id:string,pipeline_role:string,contract_id:string,contract_version:int,payload_sha256:string,destination:struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>,read_mode:string,write_mode:string,query_sha256:string,source_table_ids:array<string>,incremental_target_table_id:string,status:string,started_at:timestamp,completed_at:timestamp,stages:array<struct<stage:string,status:string,evaluation_status:string>>>>
```

### METADATA_PIPELINE_RUN.profiling

```text
array<struct<context_key:string,activity:string,status:string,results_persisted:boolean,empty_result:boolean,profile_snapshot_id:string,completed_at:string,reason:string,table_id:string,row_count:bigint,trigger:string,workspace_id:string,pipeline_run_id:string,executed_at:string,physical:struct<workspace_id:string,item_id:string,kind:string,schema:string,table_name:string>>>
```

### METADATA_PIPELINE_RUN.failures

```text
array<struct<code:string,exception_type:string>>
```

## Appendix B. Planning verification

- Fetched `origin/main` and verified the audited commit against the clean checkout.
- Read canonical schema definitions and verified all twelve exact nested type entries, source paths and proposed-file labels.
- Strict MkDocs build passed using isolated documentation dependencies and a temporary site directory; no reference/dashboard/release generator was executed.
- Document structure and whitespace checks passed; the sole repository change is this planning Markdown file. Runtime/Delta tests and Fabric endpoint checks were not executed because no implementation or deployed metadata was changed.
