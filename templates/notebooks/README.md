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

The lifecycle is **Author → Test → Activate → Live**. `setup_pipeline()` is interactive for Testing and headless for Live. Declare a stable `pipeline_id` and every source and target. A notebook rename does not change pipeline identity.

For Testing, choose any frozen Data Contract version belonging to each global `table_id`. Choose contracts for every participant, or No Contract for all. Partial selection fails. Contract-free exploration is recorded as `ungoverned_completed` and cannot be activated. There is no Bootstrap execution mode.

Testing evaluates without business publication by default. `testing_writes=True` explicitly authorizes real writes, mappings and checkpoints to the declared destinations. The interactive selector displays those destinations and requires confirmation. Physical destinations referenced by any Live pipeline are protected, including read-only consumers in another environment. Separate DEV and PROD destinations remain independent. A real Testing write reserves its destinations against activation until the run ends.

### Whole-run completion

Execute the complete project inside the plan's context manager:

```python
plan = setup_pipeline(
    pipeline_id="example-orders", sources=PIPELINE_SOURCES, targets=PIPELINE_TARGETS,
    execution_mode="testing", interactive=False, selections=EXACT_SELECTIONS,
    dependencies={}, configuration={},
)
with plan:
    source = orchestrate_read(execution_plan=plan, **READ_CONFIGURATION)
    transformed = transform(source["dataframe"])
    result = orchestrate_write(transformed, execution_plan=plan, sources=[source], **WRITE_CONFIGURATION)
print(plan.run_result["status"])
```

Every declared source must complete one Read and every target one Write. The boundary includes transformations and works for read-only pipelines. Its exit persists the whole-run outcome automatically; an individual successful operation never completes a run. Missing operations, propagated transformation exceptions, blocking checks or persistence failures cannot authorize activation. A stopped notebook remains incomplete. Start a fresh plan for retries; duplicate operations and sealed-plan reuse fail. If project code catches an exception and continues, FabricOps cannot detect the hidden failure: propagate it outside the boundary.

The standard template defines Read, Transform and Write functions in separate cells, preserving their configuration surfaces. Its final execution cell invokes all steps inside one boundary. This is an intentional scaffold change: defining a function does not execute that stage. There is no manual finalization call.

`METADATA_PIPELINE_RUN` records the exact global table-contract mappings, participating operations, configuration hashes, results, physical bindings, environment and warnings. Qualifying Testing also requires the actual deployed notebook executable fingerprint, exact installed project dependencies (explicit `{}` for none), runtime dependency versions and transformation configuration (`{}` for none). Missing or unverifiable identity leaves the run incomplete. Guardrail diagnostics persist independently in `METADATA_GUARDRAIL_RESULTS`; business writes and run records are separate transactions.

## Activate, deploy and run unattended

Use `widget_activate_pipeline()` in `01_governance`. Select a successful Testing run in the activation environment, its immutable release version, exported tested executable and exact effective Agreement. The widget shows current/proposed contracts, writer ownership, affected pipelines, available tests and blockers. Include compatible successful candidates for every directly affected active pipeline. Downstream pipelines require replacement tests when a selected replacement changes their input table's contract or writer expectations; unchanged output expectations stop propagation. There is no inferred compatibility engine.

Review the complete release and explicitly approve it once. The backend independently rechecks every selected candidate, complete operation/rule results, executable, dependencies, contract payloads and Agreement. It checks the current authority token again at commit. Failed validation, missing tests, competing writers, inconsistent contracts, stale review or a failed commit expose no partial release. Refresh and review again after a conflict.

`METADATA_ACTIVATION_STATE` is the single authoritative central row. Its `snapshot_json` contains environment revisions, active pipeline manifests, immutable approval history, active table contracts, readers/writers and running execution reservations. One serializable Delta compare-and-swap updates this row. The central row intentionally serializes concurrent metadata changes; disjoint environments are isolated in policy but may experience a stale-token conflict and require review again. There is no cross-table atomicity claim.

Within each environment, distinct table identities cannot alias the same physical destination. One contract version and at most one writer own a table; multiple readers may share its exact contract. One approved configuration exists per pipeline. DEV and PROD reference the same global contract history and can approve different versions. `METADATA_DATA_CONTRACT.environment_name` records authoring provenance, not version identity. All Metadata targets must resolve to the same central Lakehouse.

### Live cutover and deployment

Live setup automatically resolves the approved environment configuration and reserves the run in the same authority transaction. It pins one activation revision for its lifetime. Approval affecting a running pipeline or reserved destination is blocked until that execution completes. New runs cannot mix revisions during cutover. Runs for unrelated pipelines may continue. No lease expires automatically: after a notebook crash, operators must confirm the execution is stopped before removing its run reservation from the authority through a reviewed metadata repair. Never clear a reservation merely because it is old.

Deploy notebooks through Fabric or CI separately. Approval never deploys a notebook or writes business data. Optional `package_activated_pipeline()` and `verify_pipeline_deployment()` utilities remain available for artifact management; deployment sidecars are not Live authority. Live verifies the actual deployed notebook definition, exact global tables, environment destinations, dependencies and transformation settings. An undeployed or changed executable fails safely.

```python
plan = setup_pipeline(
    execution_mode="live", pipeline_id="example-orders",
    sources=PIPELINE_SOURCES, targets=PIPELINE_TARGETS, configuration={},
)
with plan:
    run_project_steps(plan)
```

Profiling options, diagnostic detail and repartitioning may differ from the tested operation; Live emits warnings and records tested and actual values. Contract mappings, table identities, roles, destinations, source relationships, SQL settings, read/write strategies and transformation settings require approval. Changing the FabricOps engine requires retesting because its source digest contributes to candidate identity.

### Upgrade boundary and limitations

Run `setup_metadata_tables()` once under controlled metadata administration to create the singleton authority. Existing per-pipeline approvals are not imported or trusted. Existing environment-specific contract histories need deliberate reconciliation into one global lifecycle per table, followed by complete Testing and activation; no compatibility shim or automatic migration is provided. Old tables are not deleted automatically.

The authority uses a single JSON snapshot to guarantee metadata atomicity, trading scalability for a conservative first implementation. Large estates may need a transactional metadata service later. Actual Fabric/Delta runtime validation remains required before deployment. Managed token-vault and caller-owned mapping dependencies without verifiable immutable identities remain ineligible for activation. Notebook deployments, business-table transactions, guardrail diagnostics and run evidence retain separate failure boundaries.
