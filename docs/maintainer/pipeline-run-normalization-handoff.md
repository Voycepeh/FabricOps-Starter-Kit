# Codex handoff: Workstream D — Pipeline Run normalization

**Status:** Implementation requested; this file is a handoff, not an implemented schema.
**Source of truth:** [Metadata v2 target model](metadata-v2-target-model.md), Workstream D.
**Target:** One focused implementation PR against latest `main` after resolving/merging [#1697](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1697). Do not merge automatically.

## Objective

Inspect and, **only if demonstrably simpler and correct**, normalize `engineering.METADATA_PIPELINE_RUN` from the current one-row-per-run structure (with `operation_summary_json`) into a queryable, typed `run` + `operation` record model **within the same canonical table**. Keep one authoritative whole-run outcome, stable per-operation identity, and exact links to Pipeline Registry and activated versions. Make the persisted model useful for inspecting each Read/Write without unpacking broad operational JSON. Do not introduce another schema, a new metadata database, a separate `METADATA_PIPELINE_OPERATION` table, or an extra public notebook function.

If an audit shows typed records increase operational complexity or compromise correctness, **stop and report evidence**, rather than force the proposal into production.

## Prerequisite and branch discipline

1. Read `AGENTS.md` and `docs/maintainer/metadata-v2-target-model.md`; use the task-specific repository skills for any affected API or notebook changes.
2. Inspect current `main`, the existing run/finalization writers and readers, metadata registry and schema setup, profiling consumers, release contracts, and associated tests.
3. **Reconcile #1697 first.** It changes finalized Test execution evidence: explicit `finalize_pipeline()` persists exact successful Test run and Guardrail results to be verified by Activation. The old docs on `main` saying Test results stay only in memory are superseded by that in-flight PR, not design instructions for D. Do not base D on the stale one-row Live-only assumption.
4. Do not alter #1697's governance semantics, reuse a stale branch, or silently revert its new Test persistence. If #1697 remains open, limit this task to a design/audit PR or report the blocked dependency; do not merge a conflicting runtime PR.

Related context:
- [#1693](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1693) — permanent UUID Pipeline Registry, merged.
- [#1695](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1695) — Metadata v2 architecture, merged.
- [#1698](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1698) — Processing State redesign, merged.
- [#1697](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1697) — durable Test evidence for Activation, currently open when this handoff was prepared.

## Inventory before implementation

Inspect these entry points and search all usages rather than assuming this list is exhaustive:

- `src/fabricops_kit/config/metadata_schemas.py`: `METADATA_PIPELINE_RUN` schema and physical grain.
- `src/fabricops_kit/pipeline/shared.py`: `persist_pipeline_run`, `_merge_pipeline_run_row`, `finalize_pipeline_run`, operation journal and session evidence.
- `src/fabricops_kit/pipeline/finalize_pipeline.py`: public completion boundary.
- `src/fabricops_kit/activated_pipeline/shared.py`, `src/fabricops_kit/widgets/widget_activate_pipeline.py`: exact candidate, operation/contract and completed-Test evidence validation.
- Profiling schedule/activity readers, `METADATA_GUARDRAIL_RESULTS` joins and all direct `operation_summary_json` queries.
- `scripts/reference_docs_metadata.py`, reference/schema/ERD generators and current `docs/reference/metadata/metadata_pipeline_run.md`.
- `tests/unit/test_pipeline_run_evidence.py`, `tests/unit/test_pipeline_session.py`, `tests/unit/test_activated_pipeline.py`, activation Delta integration tests and profiling tests.

Produce a concise inventory in the implementation PR description covering **every reader/writer**, their existing assumptions and how each moves to typed records. In particular, identify the activation reader's current reliance on `candidate_json`, `operation_summary_json.operations`, `frozen_contracts`, `boundary_completed`, `physical_bindings`, operation stages and provenance, plus profiling events read from `operation_summary_json.profiling`.

## Candidate storage design (validate, do not blindly assume)

Retain the canonical `METADATA_PIPELINE_RUN` physical name and the existing engineering ownership schema. Consider one table with:

- `record_type = 'run'`: exactly one authoritative row per `run_id`; `pipeline_id` (permanent UUID), `environment_name`, `execution_mode`, activation/release reference for Live, candidate identity/fingerprint, start and completion time, final status, whole-run completion boundary, audit identity and compact bounded diagnostics.
- `record_type = 'operation'`: one durable row per operation identity per run with parent `run_id`, deterministic `operation_id`/logical key, source/target role, table identity, operation type, status, timing, configuration identity/hash, failure/blocking classification, and only necessary bounded stage/detail JSON.
- A separate, **documented internal record key** for Delta Merge (e.g., deterministic over `run_id` + `record_type` + operation identity); do not use `run_id` alone as the physical upsert key once multiple rows share it.
- Candidate/frozen-contract identity, exact Test evidence, guardrail result linkage, profiling events and activation provenance must remain queryable and losslessly reconstructable. Do **not** simply delete JSON that current consumers require.

The above is a candidate; propose exact Spark types/nullability, unique and composite keys, field-level mapping from the old schema, authoritative status ordering and query patterns **before modifying persistence**. Choose the smallest maintainable solution. Prefer scalar columns for stable fields; keep extensible configuration, variable warnings and sanitized diagnostics in bounded JSON only when sensible.

## Atomicity, evidence and lifecycle invariants

1. **Whole-run authority:** only a terminal, successfully finalized `run` row can assert a complete successful run. A successful Read/Write operation cannot make the parent successful. Missing/failed/blocked/in-flight operations, unresolved stages, missing finalization, or errors must not authorize activation.
2. **Ordering and atomic publication:** changing to multiple rows cannot make a successful parent visible without the complete, matching operation set and required Guardrail evidence. Design and test staged writes or a single Delta transaction/atomic publication boundary as appropriate. Show exactly which row is written last and why that is sufficient under concurrent readers/retries; reject an unproven multi-transaction design.
3. **Test versus Live:** the successful, explicitly finalized Test evidence that #1697 defines remains durable and activation-readable; **Testing never publishes business data, target checkpoints, catalogue/lineage updates or other operational effects**. Only the explicitly allowed Test diagnostic evidence should commit. Live retains activation/pinned-version enforcement and existing publication semantics.
4. **Identity and provenance:** distinguish registered `pipeline_id`, execution `run_id`, exact `activated_pipeline_id` and stable operation ID. Preserve workspace/environment/notebook binding and exact frozen contract/candidate fingerprint checks; stale or foreign evidence must fail closed.
5. **Idempotence and crash safety:** repeated finalization, lost acknowledgement, duplicate operation writes, retries and recovery must not duplicate rows, regress a final status or silently turn an interrupted run into success. Test both errors before authority publication and after a successful physical Delta commit.
6. **Readers:** migrate Activation and profiling consumers in the same PR; ensure each can read a complete verified snapshot and that a missing/partial operation row prevents approval. Keep `METADATA_GUARDRAIL_RESULTS` at its own one-row-per-rule-result grain and preserve per-run/contract attribution.
7. **Avoid cross-table atomicity claims:** Delta provides a transaction per table; a run row and Guardrail Results are not automatically committed atomically across separate tables. Protect activation by explicit completeness/provenance checks and documented fail-closed sequencing.

## Migration and release boundaries

- Treat Pipeline Run as a persisted canonical table with real operational history. No silent deletion or incompatible additive evolution of existing rows.
- Document old/new columns with Spark types and nullability, source-to-target transformation, preservation of `run_id`, provenance, retained/discarded payloads, operator-facing cutover steps, backup and rollback boundary.
- Decide whether an offline migration of previously persisted run rows is necessary. If not safely provable from historical JSON, stop or require explicit reconciliation; never fabricate operation success evidence.
- Keep six published Live metadata schemas unchanged. Respect existing two-schema `governance`/`engineering` routing and use configured Metadata Lakehouse paths, never attached-default shortcuts.
- No backward-compatibility adapter for Preview physical shapes unless a documented deployment need requires it, but do not break any supported Live public callable or accidentally remove activation history.
- Do not refactor `METADATA_ACTIVATION_STATE` or its Serializable Delta compare-and-swap authority in this PR. Workstream E owns that separately.
- `METADATA_PROCESSING_STATE` publication receipts/checkpoint recovery from #1698 must remain unchanged.
- Avoid unrelated UI changes, demo redesigns, release snapshots, dashboard rebuilds and broad reference regeneration.

## Tests and acceptance criteria

Require targeted unit and **persisted Delta** integration tests proving:

- One parent and the correct uniquely identified operation records for read-only, single-Read/Write and multi-source/multi-target pipelines; exact recorded table IDs and stages.
- Explicit complete successful finalized Test → correct persisted evidence → activation eligible only with full frozen contracts/Guardrail checks and current binding, per #1697.
- Test read/write dry-run has zero business publication/checkpoint updates; Live writes still require activated version.
- Missing/failed/blocked/duplicate operation or stage, failed project transform, interrupted notebook, unfinalized run, and ungoverned execution cannot qualify for activation.
- Parent/child correctness under reordered writes, partial commits, conflicting writers, lost acknowledgement and repeated finalization; no authoritative success before complete evidence.
- Stable joins for profiling, Guardrail results, Registry and exact activated release; no duplicate results or wrong-environment leakage.
- Existing physical schema incompatibility surfaces a clear setup error; verified offline conversion retains valid history and rejects ambiguous evidence.
- No schema drift in six Live tables or accidental changes to Processing State and Activation State.
- Ruff, relevant pytest suites, compile/import checks, strict MkDocs, generated-artifact freshness and two consecutive clean generator runs. Declare any Fabric Warehouse/runtime checks not executed; do not claim cloud Fabric validation from simulated Delta tests.

## Output and merge contract

Open **one focused implementation PR** linked to this handoff, with:
1. Exact inventory and schema decision, including an explicit explanation of why typed rows improve queryability/maintenance over the existing summary JSON.
2. Field-by-field migration and recovery plan (or a documented blocker if safe conversion cannot be proven).
3. Implementation plus all affected readers/writers and direct source-owned reference changes, with generated outputs changed only as required.
4. Test commands and results, especially actual persisted Delta and fail-closed activation evidence scenarios.
5. A concise breaking-change and rollout section, and separate remaining Fabric deployment validation.

Do not merge automatically; leave review of the implementation and PR CI to the maintainer. If a prerequisite or proof is missing, report it clearly and propose a narrower safe PR instead of weakening invariants.
