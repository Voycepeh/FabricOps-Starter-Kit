# Notebook templates

Download these notebooks and import them into Microsoft Fabric.

| Notebook | Purpose |
| --- | --- |
| `00_env_config.ipynb` | Configure environments and Fabric stores. |
| `01_governance.ipynb` | Manage Governance metadata and Data Contracts. |
| `02_pipeline.ipynb` | Reusable governed Read → PySpark Transform → Write scaffold. |

Completed learning demos are kept separately under `templates/DemoData/`:

| Demo notebook | Purpose |
| --- | --- |
| `02A_full_refresh_demo.ipynb` | Orders, Products, and Order History Full → Overwrite example. |
| `02B_incremental_append_demo.ipynb` | Multi-day inventory Incremental → Append example. |
| `02C_scd_demo.ipynb` | Multi-day Product Master SCD1 and SCD2 example. |

> **Multiple Write blocks:** each `orchestrate_write()` publishes independently. If an earlier Write succeeds and a later Write fails, the pipeline is partially published. A retry runs the earlier Write again, which can duplicate or otherwise repeat non-idempotent writes such as Append. If partial publication or duplicate writes are unacceptable, use separate pipeline executions for each governed target.

For the end-to-end workflow, follow the [Guided Demo](https://voycepeh.github.io/FabricOps-Starter-Kit/guided-demo/).

## Pipeline execution mode

The scaffold declares participating sources/targets and defaults to `PIPELINE_CONTRACT_TESTING=False` in external runtime configuration. Run all uses noninteractive Bootstrap to create/profile initial outputs with no contract choices. Bootstrap is allowed only while every participant has no frozen contract; unavailable metadata is an error.

After authoring frozen contracts, set `PIPELINE_CONTRACT_TESTING=True` in `00_env_config` or notebook parameters, choose exact versions in the Testing inspector, build the plan, continue through every Read and Write, and call `finalize_pipeline(EXECUTION_PLAN)` after the transform and all operations. Read-only pipelines also require finalization. Testing persists `METADATA_PIPELINE_RUN` and linked `METADATA_GUARDRAIL_RESULTS`; it does not publish business outputs or commit ordinary metadata. A new test requires a fresh setup; built selections remain locked.

Scheduled Testing uses `setup_pipeline(interactive=False, execution_mode="testing", sources=..., targets=..., selections=...)`. UI visibility does not decide publication permission. Live uses a saved exact Activated Pipeline selection, verified manifest and explicit deployment bindings; no per-contract activation or manual override authorizes Live. Bootstrap must never be reported as approved Live execution.

### Complete-run evidence

`pipeline_id` is a stable project key carried unchanged across environments and notebook renames; `run_id` identifies one attempt. The standard `_activity_id` remains the actual Fabric activity ID: several attempts may belong to one activity. `_notebook_id` and `_notebook_name` record the deployed notebook copy and its current name; they do not replace logical pipeline identity. No identity registry or extra mapping table is introduced here. Fabric verifies the deployed notebook definition through its API, excluding outputs, display metadata and physical bindings from executable identity. Keep transformation and helper code in the notebook; only the shared `00_env_config` may be loaded with `%run`. Optionally pin `executable_sha256` to the expected normalized executable fingerprint and supply project `dependencies` as installed Python distribution names mapped to exact versions (explicit `{}` declares no extra dependencies; omission cannot produce successful Testing evidence). Each declared version is compared with installed package metadata. Declare external behavior-changing transformation settings through `configuration=...` (`{}` explicitly declares none), supplied by `PIPELINE_PROJECT_CONFIGURATION` in the canonical notebooks. Missing configuration identity prevents successful Testing, and Live must supply the tested values. The candidate retains both required and observed versions; a mismatch, missing distribution, or unsupported digest/URL leaves Testing incomplete. Dependency names such as `azure-keyvault-secrets` are package identities, not credential fields. Include all transformation/helper code in the executable artifact, and keep secrets and environment bindings outside it. The template leaves the optional pin unset and automatically observes the deployed definition in Testing. Missing executable identity allows diagnostics but prevents qualifying successful Testing evidence.

Setup persists an incomplete run before execution. Every declared source requires one Read; every target requires one Write. Run `finalize_pipeline()` only after all operations and project transformations finish. A stopped notebook remains incomplete. A caught project exception can be recorded with `finalize_pipeline(plan, failed=True)`. Duplicate operations and failed persistence invalidate the run; rerun setup for a new run ID. Repeated finalization of a sealed plan returns its original snapshot. A per-plan lock serializes operation reservation, iterator consumption and finalization, so simultaneous retries cannot overwrite each other. Spark still processes DataFrame partitions in parallel; this is not a new notebook threading workflow.

Candidate format `fabricops.pipeline-candidate.v1` uses sorted-key, compact UTF-8 JSON with ordered arrays, no NaN, and no implicit string coercion, then SHA-256. It covers declared logical participants/roles, selected frozen contract versions and content, the project executable digest, FabricOps Python source digest, installed runtime dependency versions, required and observed project dependency versions, and actual Read/Write configuration hashes including contributing source identities, incremental target relationships, audit timezone and the behavior-changing Spark SQL settings. Missing runtime dependency versions prevent qualification. Caller-owned mappings and configured token vaults require immutable mapping-dependency identity support before their runs can qualify; these paths remain diagnostic-only and cannot be activated in this PR. SQL references must resolve unambiguously to declared participants; query identity is hashed without persisting SQL literals. Dictionary order does not affect it; array order remains significant. Give participants explicit `logical_id` values when store/table names differ across environments (the default is logical store key/table name).

The candidate retains a `portable_fingerprint` of configuration with physical binding fields removed. The overall `candidate_fingerprint` additionally binds the exact frozen payload byte hashes; contract IDs and exact hashes are retained in `operation_summary_json`. Frozen contracts containing environment coordinates can therefore change the overall fingerprint across deployments while the portable projection stays stable. Neither projection includes secrets. Configuration keys indicating credentials are rejected; pass secrets only through configured environment routing, never in candidate inputs. Caller-owned token mappings and arbitrary Warehouse SQL queries have no complete portable dependency identity in this API and cannot qualify in this PR. Their Testing diagnostics are still recorded.

`METADATA_PIPELINE_RUN` is one Delta row per run, updated by run ID. Guardrail diagnostics append independently and retain rule-level details. Business publication, run snapshots and Guardrail writes are separate transactions. There is no cross-store atomicity: interrupted work may leave an incomplete row or partial diagnostics. The committed Delta snapshot is authoritative, independently of client acknowledgement. After a write exception, FabricOps confirms the exact snapshot by read-back; a confirmed commit completes normally. A missing or different snapshot fails the plan. Unavailable read-back reports an unknown client outcome and closes the local plan to replay; inspect the committed row to determine the durable outcome. No compensating update attempts to undo a potentially successful commit. The activation service validates the complete committed snapshot, candidate integrity and linked Guardrail diagnostics, never a client return value. An evidence error after completed Live publication retains `published=True` on the exception; it does not imply that business publication rolled back. Activated Pipeline is Live authority; contracts remain reusable Draft → Frozen definitions without direct Agreement linkage.

### Why these run columns exist

`METADATA_PIPELINE_RUN` has **19 columns: eleven lifecycle fields and the eight standard audit fields**. It contains no activation decision. The activation service independently validates Testing mode, successful complete status, candidate identity and exact Agreement plus explicit Governance confirmation.

| Fields | Responsibility |
|---|---|
| `activated_pipeline_id` | Reference the immutable approved version for Live; empty for Bootstrap/Testing. |
| `run_id` | Distinguish attempts, including retries within the same Fabric activity. |
| `pipeline_id` | Preserve logical identity across environment copies and notebook renames. Set this project key once; renaming changes the notebook audit name, never this key. |
| `execution_mode`, `environment_name` | Record execution policy and environment; an environment name never grants Live authority. |
| `started_at`, `completed_at` | Record execution timing independently of `_committed_at`, which changes as metadata snapshots are updated. |
| `status` | Record incomplete, failed, successful or Bootstrap completion. |
| `candidate_json`, `candidate_fingerprint` | Retain tested identity and support exact candidate lookup/comparison. |
| `operation_summary_json` | Retain operation progress, exact contract references and safe failure codes. Rule-level details stay in Guardrail Results. |
| Standard audit fields | `_committed_by`, `_committed_at`, `_workspace_id`, `_workspace_name`, `_notebook_id`, `_notebook_name`, `_metadata_lakehouse_name`, `_activity_id`. |

There is no stored `qualifies_for_activation` flag: it would duplicate lifecycle fields and duplicate the activation service decision. Failures live in the operation summary rather than a second JSON column. No extra pipeline-name or notebook-mapping columns are needed for this PR. Testing uses a run-specific transient cache namespace while durable audit fields preserve the actual Fabric activity.

Existing metadata needs the explicit migration in [Guided Demo Step 5](https://voycepeh.github.io/FabricOps-Starter-Kit/guided-demo/05-activate-data-contract-and-promote/#migrate-existing-metadata). Old individual contract activations never become pipeline approval automatically. Rerun complete Testing with this engine; historical releases remain unchanged.

## Activate, deploy and run unattended

Use `widget_activate_pipeline()` in `01_governance` or headless `activate_pipeline(...)` to approve one complete successful run. The service rechecks every operation, exact frozen contract/payload hash, current executable and dependencies, linked Guardrail diagnostics, exact effective Agreement and explicit confirmation. One immutable version may be active per logical pipeline. Use `set_pipeline_active(..., expected_active_id=..., governance_confirmed=True)` for explicit switching/deactivation. Switching does not edit saved Live selections.

Package with `package_activated_pipeline(...)`, deploy the unchanged executable and package with your Fabric/CI tooling, then call `verify_pipeline_deployment(...)` in the destination notebook to record separate physical bindings. Governance metadata must remain reachable through the explicitly configured authority environment; Fabric Deployment Pipelines are not assumed to copy metadata rows. `approved.json` contains the exact reusable definitions; `deployment.json` records environment bindings, separately from identity, only after the actual Fabric notebook definition matches the approved executable. An unavailable export or changed notebook fails verification without writing bindings. Keep this explicit deployment directory on a shared mounted durable volume accessible to scheduled runs.

Every project configuration key and nested Read/Write parameter contributes to candidate identity, including names such as `schema`, `store` and `table_name`; only explicit top-level orchestration routing arguments are excluded. After an engine upgrade, rerun complete Testing and activation because the engine source hash is part of the approval.

`setup_pipeline(execution_mode="live", pipeline_id=..., deployment_path=..., activated_pipeline_id=...)` verifies the approval and saves that exact selection once. Subsequent scheduled/manual Live calls omit the activated ID and UI; they use the saved version. A different approved deployment never silently replaces selection. Use `replace_selection=True` only for a deliberate verified switch. Missing/mismatched approvals, dependencies, executable, bindings or selections fail closed. Environment names never imply Live and failed Live never falls back to Bootstrap.

Change mode and deployment settings in `00_env_config` or notebook parameters, not by editing the tested notebook. All behavior-changing Read/Write arguments must match the tested manifest. Business transactions, operational metadata and run evidence retain separate commit boundaries and Warn/Block behavior; no cross-store atomicity is claimed.
