# Notebook templates

Download these notebooks and import them into Microsoft Fabric.

| Notebook | Purpose |
| --- | --- |
| `00_env_config.ipynb` | Configure environments and Fabric stores. |
| `01_governance.ipynb` | Manage Governance metadata and Data Contracts. |
| `02_pipeline.ipynb` | Reusable governed Read → PySpark Transform → Write scaffold. |
| `99_explore.ipynb` | Explore approved Production data. |

Completed learning demos are kept separately under `templates/DemoData/`:

| Demo notebook | Purpose |
| --- | --- |
| `02A_full_refresh_demo.ipynb` | Orders, Products, and Order History Full → Overwrite example. |
| `02B_incremental_append_demo.ipynb` | Multi-day inventory Incremental → Append example. |
| `02C_scd_demo.ipynb` | Multi-day Product Master SCD1 and SCD2 example. |

> **Multiple Write blocks:** each `orchestrate_write()` publishes independently. If an earlier Write succeeds and a later Write fails, the pipeline is partially published. A retry runs the earlier Write again, which can duplicate or otherwise repeat non-idempotent writes such as Append. If partial publication or duplicate writes are unacceptable, use separate pipeline executions for each governed target.

For the end-to-end workflow, follow the [Guided Demo](https://voycepeh.github.io/FabricOps-Starter-Kit/guided-demo/).

## Pipeline execution mode

The scaffold declares participating sources/targets and defaults to `CONTRACT_TESTING = False`. Run all uses noninteractive Bootstrap to create/profile initial outputs with no contract choices. Bootstrap is allowed only while every participant has no frozen or active contract; unavailable metadata is an error.

After authoring frozen contracts, set `CONTRACT_TESTING = True`, choose exact versions in the Testing inspector, build the plan, continue through every Read and Write, and call `finalize_pipeline(EXECUTION_PLAN)` after the transform and all operations. Read-only pipelines also require finalization. Testing persists `METADATA_PIPELINE_RUN` and linked `METADATA_GUARDRAIL_RESULTS`; it does not publish business outputs or commit ordinary metadata. A new test requires a fresh setup; built selections remain locked.

Scheduled Testing uses `setup_pipeline(interactive=False, execution_mode="testing", sources=..., targets=..., selections=...)`. UI visibility does not decide publication permission. Saved Activated Pipeline selection, one active version per logical pipeline, manifest-pinned Live verification, and deployment bindings belong to the subsequent activation phase. Bootstrap must never be reported as approved Live execution.

### Complete-run evidence

`pipeline_id` is a stable project key carried unchanged across environments and notebook renames; `run_id` identifies one attempt. The standard `_activity_id` remains the actual Fabric activity ID: several attempts may belong to one activity. `_notebook_id` and `_notebook_name` record the deployed notebook copy and its current name; they do not replace logical pipeline identity. No identity registry or extra mapping table is introduced here. Set `executable_sha256` to the SHA-256 of the deployed project executable and supply project `dependencies` as installed Python distribution names mapped to exact versions (explicit `{}` declares no extra dependencies; omission cannot produce successful Testing evidence). Each declared version is compared with installed package metadata. The candidate retains both required and observed versions; a mismatch, missing distribution, or unsupported digest/URL leaves Testing incomplete. Dependency names such as `azure-keyvault-secrets` are package identities, not credential fields. Include all transformation/helper code in the executable artifact, and keep secrets and environment bindings outside it. The template leaves this digest unset during initial Bootstrap. Missing executable identity allows diagnostics but prevents qualifying successful Testing evidence.

Setup persists an incomplete run before execution. Every declared source requires one Read; every target requires one Write. Run `finalize_pipeline()` only after all operations and project transformations finish. A stopped notebook remains incomplete. A caught project exception can be recorded with `finalize_pipeline(plan, failed=True)`. Duplicate operations and failed persistence invalidate the run; rerun setup for a new run ID. Repeated finalization of a sealed plan returns its original snapshot. A per-plan lock serializes operation reservation, iterator consumption and finalization, so simultaneous retries cannot overwrite each other. Spark still processes DataFrame partitions in parallel; this is not a new notebook threading workflow.

Candidate format `fabricops.pipeline-candidate.v1` uses sorted-key, compact UTF-8 JSON with ordered arrays, no NaN, and no implicit string coercion, then SHA-256. It covers declared logical participants/roles, selected frozen contract versions and content, the project executable digest, FabricOps Python source digest, installed runtime dependency versions, required and observed project dependency versions, and actual Read/Write configuration hashes including contributing source identities, incremental target relationships, audit timezone and the behavior-changing Spark SQL settings. Missing runtime dependency versions prevent qualification. Configured token vaults also require content identity support before their runs can qualify. Dictionary order does not affect it; array order remains significant. Give participants explicit `logical_id` values when store/table names differ across environments (the default is logical store key/table name).

The candidate retains a `portable_fingerprint` of configuration with physical binding fields removed. The overall `candidate_fingerprint` additionally binds the exact frozen payload byte hashes; contract IDs and exact hashes are retained in `operation_summary_json`. Frozen contracts containing environment coordinates can therefore change the overall fingerprint across deployments while the portable projection stays stable. Neither projection includes secrets. Configuration keys indicating credentials are rejected; pass secrets only through configured environment routing, never in candidate inputs. Caller-owned token mappings and arbitrary Warehouse SQL queries have no complete portable dependency identity in this API and cannot qualify in this PR. Their Testing diagnostics are still recorded.

`METADATA_PIPELINE_RUN` is one Delta row per run, updated by run ID. Guardrail diagnostics append independently and retain rule-level details and the existing public Catalogue inspector. Business publication, run snapshots and Guardrail writes are separate transactions. There is no cross-store atomicity: interrupted work may leave an incomplete row or partial diagnostics. A metadata exception is fatal for that plan. If a final commit might have succeeded before its acknowledgement was lost, FabricOps attempts an idempotent failed replacement for the same run ID. If that replacement also cannot be confirmed, it raises an explicit unknown-outcome error. The persisted outcome then requires reconciliation in Fabric before any future authorization consumes the run; local memory cannot guarantee a durable invalidation while storage is unreachable. Do not retry the notebook with the same plan. An evidence error after completed Live publication retains `published=True` on the exception; it does not imply that business publication rolled back. This PR introduces no Activated Pipeline and does not change Live authority, which still uses active frozen Data Contracts.

### Why these run columns exist

`METADATA_PIPELINE_RUN` has **18 columns: ten lifecycle fields and the eight standard audit fields**. It contains no activation decision. A later authorization service must independently validate Testing mode, successful complete status, candidate identity and its other Governance requirements.

| Fields | Responsibility |
|---|---|
| `run_id` | Distinguish attempts, including retries within the same Fabric activity. |
| `pipeline_id` | Preserve logical identity across environment copies and notebook renames. Set this project key once; renaming changes the notebook audit name, never this key. |
| `execution_mode`, `environment_name` | Record execution policy and environment; an environment name never grants Live authority. |
| `started_at`, `completed_at` | Record execution timing independently of `_committed_at`, which changes as metadata snapshots are updated. |
| `status` | Record incomplete, failed, successful or Bootstrap completion. |
| `candidate_json`, `candidate_fingerprint` | Retain tested identity and support exact candidate lookup/comparison. |
| `operation_summary_json` | Retain operation progress, exact contract references and safe failure codes. Rule-level details stay in Guardrail Results. |
| Standard audit fields | `_committed_by`, `_committed_at`, `_workspace_id`, `_workspace_name`, `_notebook_id`, `_notebook_name`, `_metadata_lakehouse_name`, `_activity_id`. |

There is no stored `qualifies_for_activation` flag: it would duplicate lifecycle fields and pre-empt the later activation service. Failures live in the operation summary rather than a second JSON column. No extra pipeline-name or notebook-mapping columns are needed for this PR. Testing uses a run-specific transient cache namespace while durable audit fields preserve the actual Fabric activity.

This is an unmerged Preview schema revision. If an earlier PR #1663 schema was initialized in a Fabric test workspace, preserve any diagnostics you need and recreate that preview run table with the current schema before rerunning Testing. Previous preview runs are not approval authority. No historical release schema or snapshot is rewritten.
