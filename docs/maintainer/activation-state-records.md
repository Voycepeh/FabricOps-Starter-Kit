# Activation State records

`governance.METADATA_ACTIVATION_STATE` publishes typed approval and execution records in one Delta transaction. It remains the only activation authority. Governance and engineering ownership schemas are unchanged.

## Physical model

Previously one `authority_id = central` row held a CAS `token` and all operational state in `snapshot_json`. That physical layout is incompatible with this Preview version. The new table has 21 top-level columns: five common identity/publication columns, eight nullable native record structs, and eight standard audit columns. There is no authority snapshot JSON.

`metadata_schemas.py` defines exact Spark types and nullability. Common `record_id`, `record_type`, and `token` are required strings; `environment_name` and `parent_id` are nullable strings. The eight standard audit fields retain their existing types, including required timestamp `_committed_at`. Exactly the struct matching `record_type` is present; all other record structs are null. All fields below are required unless marked **nullable**. Arrays contain non-null structs. Spark can report looser physical nullability; domain readers enforce the required fields.

| Record / grain | Deterministic key inputs | Parent | Native struct fields |
| --- | --- | --- | --- |
| `authority`: one publication control record | Literal `central` | None | `record_count: long` (excludes central); `content_sha256: string` |
| `environment`: one environment revision | environment, null | central | `revision: string` |
| `approval`: one immutable approved pipeline version per environment | environment, activated_pipeline_id | environment | pipeline_id, activated_pipeline_id, pipeline_name, pipeline_version, testing_run_id, agreement_id, agreement_version, candidate_fingerprint, portable_fingerprint: strings; project_configuration_json, agreement_json, testing_evidence_json, warnings_json: strings; operations: array of operation/configuration_sha256/configuration_json string structs |
| `activation`: one currently approved version per environment and pipeline | environment, pipeline_id | exact approval | pipeline_id, activated_pipeline_id: strings |
| `participant`: one exact logical participant per approval | environment, [activated_pipeline_id, participant] | exact approval | participant, table_id, contract_id, payload_sha256, contract_environment, contract_status, contract_payload_json, candidate_contract_json: strings; contract_version: integer; is_source, is_target: booleans; destination: struct |
| `ownership`: one active table mapping per environment | environment, table_id | environment | table_id, contract_id, payload_sha256: strings; contract_version: integer; writer: **nullable string**; readers: array of pipeline_id string structs; destination: struct |
| `reservation`: one Live run or notebook-rebind barrier | environment, reservation_id | Live: exact approval; rebind: environment | reservation_id, pipeline_id, mode: strings; revision, activated_pipeline_id: **nullable strings**; tables: array of table_id string structs; destinations: **nullable array of destination structs** |
| `profiling_claim`: one renewable table/activity claim | environment, claim_key | central | claim_key, token (lease ownership), key (physical context hash), table_id, activity, trigger, execution_id: strings; expires_at: timestamp; completed_at: **nullable timestamp**; physical: destination struct |

A destination struct has required string workspace_id, item_id, kind, table_name and **nullable string schema**. Participant contract_status must be frozen. Approval activity is represented by a separate `activation` record, so replacing the active version never modifies the old approval content. Reservation mode is `live` or `rebind`; revision and approved ID are required for Live, absent for rebind. Live tables and destinations must exactly cover the pinned approved participants. Rebind tables remain empty. Profiling claims retain their existing expiry, token ownership and interrupted-work recovery protocol, including the completion decision timestamp held until the Pipeline Run journal confirms success.

Except central, record IDs are `record_type + ':' + SHA256(canonical_json([environment, key_inputs]))`. Parent IDs use that same construction. A publication contains exactly one central row and unique record IDs. Each environment/pipeline has one activation; each approval/logical participant has one participant; each active environment/table has one ownership record. Approvals with the same pipeline/version cannot change content. The codec and existing manifest validation enforce these constraints; Delta does not supply uniqueness constraints.

Publication tokens and non-approval audit fields describe the current publication. Approval content, its exact participant definitions and the approval's original audit remain immutable.

Environment records persist their revisions. Approvals and all their participants persist indefinitely. Active links and ownership change only through coordinated approval. Live reservations remain until explicit completion/release; they do not expire automatically. A failed or interrupted run continues to block cutover/rebind until operators establish its disposition. Rebind barriers release only by exact pipeline/lease ownership. Profiling claims renew/release by lease token, or become reclaimable after expiry; completion history remains in Pipeline Run and profile tables.

## Readers and writers

All physical reads use `metadata_records` through the configured Metadata Lakehouse route, followed by `activation_state_from_records`. All physical mutations use `commit_activation_state`; setup alone seeds central using error-if-exists creation. There is no legacy reader or alternate writer.

| Domain functions / consumers | Authority responsibility |
| --- | --- |
| `review_pipeline_release`, `tested_pipeline_manifest`, `approve_pipeline_release`; activation widget | Complete finalized Test evidence, exact Agreement and immutable approved versions; dependency and writer ownership checks; atomic environment revision, history, active links and table mappings |
| `activation_version`, `resolve_approved_consumer_contract`; widget review/history | Exact immutable release and frozen contract reconstruction; environment isolation |
| `build_live_pipeline_plan`, `verify_live_plan`; `setup_pipeline`, Read/Transform/Write and `finalize_pipeline` | Pin exact approved candidate/contracts/bindings/revision; validate reservation and current notebook/workspace binding; release on completion/failure |
| `release_pipeline_lease` | Remove only the completed run reservation; bounded fresh-read CAS retry; repeated release has no mutation |
| `reserve_pipeline_rebind`, `release_pipeline_rebind`; Pipeline Registry registration/rebind | Drain Live runs and hold a persisted barrier while notebook/workspace binding changes; Registry registration never grants activation |
| `claim_table_profile`, `maintain_table_profile_claim`; profiling completion and publication | Claim, renewal, completion authorization, expiry and token-owned release, serialized against every other authority mutation |
| `setup_metadata_tables` | Seed one complete initial publication; reject incompatible canonical layouts without additive evolution |

The existing domain state and notebook result shapes reconstruct in memory. The supported `setup_pipeline → Read → Transform → Write → finalize_pipeline` workflow, Test/Live distinction, widgets and public callable signatures remain unchanged. Processing State recovery and Pipeline Run persistence are unchanged, including #1700 (merged before this branch).

## Transaction and concurrency proof

1. Read the previous complete publication once. Check the expected CAS token and forbid changes/removals to any existing immutable approval. Encode and reconstruct the proposed records before writing; reject any lossy transformation or inconsistent ownership/participants.
2. One Delta `MERGE` matches deterministic record IDs, updates retained records, inserts new approval/participant/reservation records and deletes records absent from the new state. The matched central row assigns its new token only if its **transaction-time** token still equals the expected token; otherwise `raise_error` aborts the transaction. No child records commit independently. A stale publisher that passed preflight therefore cannot insert unmatched children or delete newer history/reservations.
3. Every publisher updates the seeded central record. Delta optimistic write conflict detection prevents overlapping writers from overwriting that same record, including under the default WriteSerializable isolation. Runtime performs no DDL, table-property mutation, automatic activation retry or business-data replay. Setup must precede runtime; runtime never creates a missing authority.
4. Each record carries the same publication token. Central records the complete child count and SHA-256 over sorted typed record content, excluding audit fields and publication tokens. Readers require one central row, unique keys, matching tokens, exact count/hash, valid required fields, allowed record types, deterministic parent/key reconstruction, immutable manifest and candidate hashes, complete participants and consistent active table ownership. Missing, mixed, orphaned or corrupt records cannot authorize Live. The checksum detects accidental physical damage; it is not a security boundary against authorized table editors.
5. After success or an exception, read back a complete validated publication. Confirm the exact generated token **and** complete normalized logical content. A post-commit lost acknowledgement is confirmed without another publication. A conflict with a later publication remains unconfirmed and fails closed; inspect and refresh rather than replaying an approval. Repeating an already released Live reservation returns without publishing. There is no general stale-token success alias.
6. Approval and its participants become visible at the same Delta version. An old reader may see the complete prior version, never a partially published approval. Live acquisition checks active approval, exact frozen contracts, current physical bindings and Registry binding before reserving; CAS prevents an intervening approval/rebind from accepting a stale reservation. Cutover checks all touched pipelines/tables against existing Live and rebind reservations. Unrelated releases retain reservations and immutable history through a fresh full read plus CAS.

Persisted regressions exercise native participant queries, simultaneous publishers, stale preflight and transaction-time CAS, rollback of unmatched child inserts/deletes with unchanged Delta version, post-execute acknowledgement loss, immutable history, isolated environments/pipelines, Test finalization and exact contract pinning, interrupted Live reservation/release, writer ownership, rebind barriers, profiling claim retention/renewal/release, and corrupted publications. Domain tests additionally cover competing writers, changed bindings, missing Test operations/rules and claim ownership/expiry.

## Retained JSON

JSON is restricted to immutable authored content or diagnostics: project and per-operation variable configuration, full Data Agreement content, frozen executable/descriptive contract payloads, their portable candidate form, frozen Test evidence and warnings. These values preserve exact fingerprints and review results. They do not encode mutable environment revisions, active pipeline selection, participant relationships, table ownership or reservations. Operation keys/configuration hashes, exact contract/version/hash, table IDs and all physical binding fields are native columns/struct fields. The historical Test diagnostic copy is not a second authorization path; active approval reconstruction and manifest integrity checks use the typed records.

```sql
SELECT environment_name, parent_id AS approval_record_id,
       participant.table_id, participant.contract_id,
       participant.contract_version, participant.destination.workspace_id
FROM governance.METADATA_ACTIVATION_STATE
WHERE record_type = 'participant';
```

## Preview upgrade and reset

1. **Fresh setup:** install the matching package and run `setup_metadata_tables` against the configured schema-enabled Metadata Lakehouse. It seeds central; register, run complete finalized Test and approve before Live.
2. **Incompatible canonical table:** stop/drain notebook readers, Live/Test writers, profiling activities and registration/rebind operations. Disable schedules and verify all active reservations and publication progress. Back up the old Delta table, its version, matching package and related frozen contracts, Agreement, Registry and Test references. Setup gives a clear error; it never evolves, drops or resets incompatible Activation State.
3. **Disposable Preview state:** only after explicitly establishing that approvals/history may be discarded and no active reservations remain, operators may replace the canonical Activation State at its configured physical path with the fresh layout, rerun setup, finalized Test and Governance approval. Do not discard Processing State or Pipeline Run tables. No automatic migration, standalone history-preservation utility, dual write or compatibility reader is supplied.
4. **Real retained history or reservations:** preserve the old table/package and keep executions stopped. Explicitly reconcile each immutable approval, complete participant set, current environment revision/mapping and live/rebind/profiling reservation with the new documented model, validating lossless domain reconstruction and references before a reviewed offline cutover. If that cannot be established, retain the old deployment. Never infer that an interrupted reservation can be released just because its notebook disappeared.
5. **Replacement and rollback:** runtime derives the physical path from the configured Lakehouse/schema/table name. Changing only a catalogue registration location is insufficient. Verify the replacement at that path and correct registration while stopped; run setup and Fabric smoke checks before resuming schedules. Before any new writes, rollback restores the backed-up authority and matching package. After new approvals/reservations, stop and reconcile them before rollback; restoring an older copy alone loses authority.
6. **Obsolete differently named Activation State tables:** they remain unused and need not be deleted for setup. Archive retained history and resolve outstanding obligations before manually removing obsolete tables/registrations. Their existence does not authorize Live or substitute for canonical state.

The whole authority remains a bounded, centrally serialized control plane. It still reconstructs all environments/history in memory and rewrites one complete publication per mutation; this work improves queryability, not control-plane throughput or history retention policy. Direct physical edits are unsupported. Local persisted Spark/Delta validation does **not** prove Microsoft Fabric Lakehouse execution, notebook permissions, Warehouse transport or actual Fabric concurrency; validate these in the target Fabric runtime before rollout.
