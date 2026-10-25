# Pipeline Run normalization: Workstream D

`engineering.METADATA_PIPELINE_RUN` stores a typed `run` parent and its `operation` records in one canonical Delta table. This implements the [Workstream D handoff in #1699](https://github.com/Voycepeh/FabricOps-Starter-Kit/pull/1699), using merged #1697 and #1698 as the baseline. Activation State authority and Processing State recovery are unchanged.

## Decision and inventory

Stable operation IDs, roles, table IDs, exact frozen contracts, configuration hashes, statuses and timing are scalar columns. Operators can inspect Reads/Writes and join Guardrail Results without exploding a broad summary document. Extensible processing configuration and sanitized stage lists remain per-operation JSON. Exact candidate content remains on the parent for fingerprint verification; it is not an alternative execution-status authority. Run details retain frozen contract references, physical bindings, activation revision, profiling events, warnings and safe failures. No extra public callable, schema or metadata table is introduced.

| Reader / writer | Previous assumption | Typed implementation |
| --- | --- | --- |
| `build_pipeline_execution_plan`, Live setup, `PipelineOperation`, profiling journal, `finalize_pipeline_run` | `persist_pipeline_run` replaced one row keyed by run_id | Same journal owner encodes one run and all operations; one atomic publication |
| `publish_pipeline_testing_results`, `finalize_pipeline` | Explicit Test finalization publishes stable diagnostics before run | Same order; typed parent and operations publish together after diagnostic commits |
| `_merge_pipeline_run_row` | Unconditional merge on run_id | Initial idempotent Delta append; subsequent Serializable CAS merge on record_id |
| Persistence exception read-back | At most one physical row | One collected snapshot; validate all matching rows and the attempted token |
| `activated_pipeline.shared.metadata_records` / `tested_pipeline_manifest` | One run row containing summary operations | Reconstruct notebook-facing results only after token, membership, digest, identity and provenance verification |
| `widget_activate_pipeline` | Logical run candidate and operation summaries | Uses the same verified domain reader; review details and notebook controls unchanged |
| Activation candidate/contract review | candidate_json, operations, frozen_contracts, boundary_completed, physical_bindings, stages and provenance | All preserved; exact frozen contract columns also permit direct operation/result joins; existing frozen payload, candidate, stage, binding and rule checks retained |
| `profiling_completion_history` | Exploded summary.profiling | Filters record_type=run and reads run_details_json.profiling; joins actual persisted profile snapshots as before |
| Guardrail Results writer / activation join | Per-rule result keyed by stable result ID and run/contract | Grain unchanged; activation checks exact run, environment, notebook, workspace and activity provenance before rule coverage |
| Metadata setup / registry | Old physical run layout allowed additive evolution | Rejects old or partial typed layout, including empty old tables; explicit offline conversion required |
| Reference, explorer and ERD generators | run_id as physical primary key | record_id as physical primary key; typed grain, fields and ownership generated from canonical sources |
| Release contracts | Six Live metadata schemas | Unchanged; no historical release snapshot edits |

Repository searches covered all direct `METADATA_PIPELINE_RUN` and `operation_summary_json` usages in package source, scripts and tests. The summary field remains a supported notebook-facing result, not a second persisted layout or legacy physical reader. Immutable historical activation manifests retain their original embedded Testing results and are not rewritten.

The cost is that each publication still rewrites the full operation set, and Delta retains one transaction identity per run. This preserves one atomic status owner while moving operational inspection and joins to scalar fields; it does not claim fewer writes or remove the exact candidate document. No cross-table operation store or runtime compatibility path is needed.

## Physical schema and keys

Only `METADATA_PIPELINE_RUN` changes. The old schema had required strings run_id, pipeline_id, execution_mode, environment_name, status, candidate_json and operation_summary_json; required started_at timestamp; nullable activated_pipeline_id/candidate_fingerprint strings and completed_at timestamp; and the eight required audit fields. The new schema is below. Spark physical readers can report nullable fields even when the canonical writer schema is required; type-specific application validation supplies the stronger constraints.

| New field | Spark type | Nullable | Source / meaning |
| --- | --- | --- | --- |
| `record_id` | `string` | No | New SHA-256 of `[run_id, "run"]` or `[run_id, "operation", operation_key]`. |
| `record_type` | `string` | No | New `run` or `operation` discriminator. |
| `snapshot_token` | `string` | No | New publication UUID; offline conversion uses `offline:<run_id>`. |
| `run_id` | `string` | No | Preserve original execution attempt on every row. |
| `activated_pipeline_id` | `string` | Yes | Preserve exact activated release on every row; null for Test. |
| `pipeline_id` | `string` | No | Preserve permanent Pipeline Registry UUID on every row. |
| `execution_mode` | `string` | No | Preserve `testing` or `live` on every row. |
| `environment_name` | `string` | No | Preserve environment on every row. |
| `started_at` | `timestamp` | No | Preserve original run start on every row; not an operation start. |
| `completed_at` | `timestamp` | Yes | Preserve on run row; null on operation rows. |
| `status` | `string` | No | Preserve run outcome on parent; copy each operation status from summary. |
| `candidate_fingerprint` | `string` | Yes | Preserve on run row; null on operation rows. |
| `candidate_json` | `string` | Yes | Preserve exact serialized candidate on run row; null on operation rows. |
| `run_details_json` | `string` | Yes | Original summary excluding `operations` and `boundary_completed`; all other fields retained losslessly on run row. |
| `boundary_completed` | `boolean` | Yes | Original summary completion boundary on run row; null on operation rows. |
| `operation_count` | `long` | Yes | New exact count of declared role-qualified operation keys on run row. |
| `operations_digest` | `string` | Yes | New SHA-256 of sorted typed operation identities, statuses, contract/configuration references, stage payloads and timing on run row. |
| `operation_id` | `string` | Yes | New SHA-256 of `[run_id, operation_key]`; operation rows only. |
| `operation_key` | `string` | Yes | Preserve summary operation map key (`source:<participant>` or `target:<participant>`). |
| `role` | `string` | Yes | Exact source/target role resolved from candidate participant; operation rows only. |
| `table_id` | `string` | Yes | Exact candidate global table identity for operation; missing or ambiguous mapping rejects conversion. |
| `operation_type` | `string` | Yes | Read for source; Write for target. |
| `contract_id` | `string` | Yes | Exact summary frozen contract ID for operation participant; null for No Contract. |
| `contract_version` | `integer` | Yes | Exact summary frozen contract version; null for No Contract. |
| `contract_payload_sha256` | `string` | Yes | Exact summary frozen payload hash; null for No Contract. |
| `operation_started_at` | `timestamp` | Yes | Original operation start when available; null for unknown historical timing. Never substitute run start. |
| `operation_completed_at` | `timestamp` | Yes | Original operation completion when available; null for unknown historical timing. |
| `configuration_sha256` | `string` | Yes | Preserve operation configuration identity; null when not yet known. |
| `configuration_json` | `string` | Yes | Losslessly serialize one operation configuration; null when not yet configured. |
| `stages_json` | `string` | Yes | Losslessly serialize one operation stage list; operation rows only. |
| `failure_code` | `string` | Yes | Derived `blocked` for a blocking stage, otherwise `failed` for failed operation, otherwise null. |
| `_committed_by` | `string` | No | Preserve original required audit value on every row; no invented provenance. |
| `_committed_at` | `timestamp` | No | Preserve original required audit value on every row; no invented provenance. |
| `_workspace_id` | `string` | No | Preserve original required audit value on every row; no invented provenance. |
| `_workspace_name` | `string` | No | Preserve original required audit value on every row; no invented provenance. |
| `_notebook_id` | `string` | No | Preserve original required audit value on every row; no invented provenance. |
| `_notebook_name` | `string` | No | Preserve original required audit value on every row; no invented provenance. |
| `_metadata_lakehouse_name` | `string` | No | Preserve original required audit value on every row; no invented provenance. |
| `_activity_id` | `string` | No | Preserve original required audit value on every row; no invented provenance. |

`record_id` is the physical unique key. `(run_id, record_type, operation_key)` is the logical composite key, with null operation_key only for the sole run row. `(run_id, operation_id)` uniquely identifies a Read/Write. Operation IDs are deterministic per run and logical role; the role-qualified operation key is stable across attempts. Registry joins use pipeline_id + environment_name. Live release joins use exact activated_pipeline_id. Guardrail joins use run_id + environment_name + table_id + contract_id + contract_version; rule IDs remain at the separate rule-result grain. Do not join results to every row on run_id alone and multiply counts.

## Atomic publication and recovery

1. The first publication appends the complete row set in **one Delta transaction**, with `txnAppId=fabricops-pipeline-run:<run_id>` and txnVersion=0. Competing first writers cannot duplicate it. A read first rejects an existing run ID. Delta transaction identity retention must remain unbounded (the default); an explicitly configured retention duration is rejected.
2. Each later publication merges the complete row set on record_id in **one Serializable Delta transaction**. Its parent and every existing child must match the previous snapshot token. A stale token raises inside the merge expression, aborting child updates and unmatched inserts together. A failed parent cannot regress to success. Any parent with completed_at is immutable, including failed/incomplete terminal runs. Repeated finalization returns the sealed result without a new mutation.
3. There is no last-row publication ordering: the parent and every operation become visible at the **same Delta commit boundary**. A successful operation never sets parent success. Missing operations, failures, unresolved/duplicate stages or a missing explicit whole-run boundary cannot assert successful authority. Readers collect all selected rows from one DataFrame action and verify matching provenance/tokens, operation count, deterministic identities and content digest. A partial or corrupt snapshot fails closed.
4. Test operations remain in memory. Only explicitly finalized Test publishes the allowed run and Guardrail diagnostic records. Testing does not publish business tables, checkpoints, Catalogue or Lineage. Live retains approved-version and existing publication enforcement.
5. Guardrail Results commit first, then the entire typed run snapshot. There is no cross-table atomicity claim. A crash before run publication leaves diagnostics without approving authority. Activation independently verifies the exact frozen contracts, required stages, candidate/bindings and complete exact rule-result set. Missing, foreign or blocking results prevent approval.
6. After an exception, read-back verifies the complete row set, attempted token and logical content. A physically committed matching snapshot confirms a lost acknowledgement. Unconfirmed or unreadable outcomes poison the plan; inspect the persisted snapshot and start a new run, without replaying business publication from this plan. An interrupted unfinalized Live run stays incomplete; unfinished Test has no approving persisted snapshot.

## Offline conversion and rollout

**Breaking Preview physical-layout change. Public notebook callables and result shapes remain supported.** Setup fails on old layouts instead of additive-evolving history. No dual writer or compatibility reader exists.

1. Stop/drain Test and Live writers, readers and profiling jobs. Inventory in-flight runs, exact candidate/contract mappings, approvals and diagnostic retention. Take a durable backup of the old run table, record its Delta version and retain the old code/schema pair. Also retain Guardrail Results, frozen contracts, Registry bindings and Activation State history. No records are deliberately discarded.
2. Install the new package in an isolated Spark/Delta session. Convert a **version-pinned** source to a **separate new location** in the configured Metadata Lakehouse using:

   ```bash
   python scripts/migrate_pipeline_runs.py \
     --source-path <configured-old-run-delta-path> \
     --source-version <backed-up-version> \
     --destination-path <new-staging-delta-path>
   ```

   The script reads source only, rejects duplicate run IDs, forces validation of every row before writing, and refuses an existing destination. It preserves run IDs, timestamps, status, provenance, frozen references, activation links and every summary detail. It reconstructs each run and compares it with the original before accepting it. Unknown operation fields, missing/ambiguous operation membership or unprovable successful authority stop conversion. No success is inferred from isolated rule results or fabricated from run status. Older history without exact participant table IDs or whole-run boundaries requires explicit operator reconciliation; retain it in backup until resolved. Never replace it with an empty table.
3. Validate the converted parent counts against source run count, operation membership/digests, exact candidate fingerprints, Registry/release references, profiling history and Guardrail coverage. Re-review previously eligible finalized Test runs with current bindings; do not reinterpret ineligible historical runs as successful tests. In-flight runs remain historical incomplete/failed records and must resume as new execution attempts.
4. While all writers remain stopped, cut over the canonical `engineering.METADATA_PIPELINE_RUN` registration/path to the verified typed Delta table using the configured Metadata Lakehouse. Keep the physical canonical name and configured ownership schema. Run setup and targeted Test/Live smoke checks before resuming. Do not use attached-default shortcuts or overwrite the source as a conversion step.
5. Before new executions, rollback may restore the old table registration and matching old package from backup. After new typed runs or new approvals exist, stop writers again and reconcile/archive those new runs and references before rollback; simply restoring the old table would erase execution history. Preserve Activation State history and Processing State receipts/checkpoints throughout. Keep the old backup through deployment validation and the agreed operational retention period.

The new migration utility is an offline deployment tool, not a runtime fallback. Fabric Lakehouse registration/cutover, Fabric Warehouse transport, notebook deployment permissions and live runtime concurrency require separate deployment validation; local persisted Delta tests do not establish those results.

## Query examples

```sql
-- Inspect Read/Write outcomes without parsing the run summary.
SELECT run_id, operation_id, operation_type, table_id, status,
       contract_id, contract_version, configuration_sha256,
       operation_started_at, operation_completed_at, failure_code
FROM engineering.METADATA_PIPELINE_RUN
WHERE record_type = 'operation' AND environment_name = 'DEV';

-- Whole-run outcomes: operation success never substitutes for this parent.
SELECT run_id, pipeline_id, activated_pipeline_id, status, completed_at
FROM engineering.METADATA_PIPELINE_RUN
WHERE record_type = 'run' AND environment_name = 'DEV';
```
