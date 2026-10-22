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

The pipeline flow is **Setup Pipeline → Read → Transform → Write**. Environment routing is configured once by `00_env_config`. A stable `pipeline_id` identifies the logical pipeline independently of notebook names and paths.

```python
CONTRACTS = setup_pipeline(pipeline_id="example-orders", pipeline_mode="Test")
source = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
transformed = transform(source["dataframe"])
result = orchestrate_write(transformed, store="Gold", schema="demo",
                           table_name="customer_summary", write_mode="overwrite")
pipeline_result = finalize_pipeline(CONTRACTS)
```

`pipeline_mode` accepts exactly `Test` or `Live`. Test runs real reads, transformations and selected Guardrails without business or operational metadata commits during Read and Write. The explicit Finalize step publishes only run and Guardrail results for activation review. In a notebook, choose exact frozen contracts or No Contract in the setup interface before the first operation. Headless Test starts with No Contract; its returned session supports explicit `select_contract(table_id, contract_id, contract_version)` for automated diagnostics. Choices lock when operations start. The displayed report updates automatically, with red Test and green Live mode treatment and textual operation/Guardrail status.

Live resolves participants, frozen contracts, project configuration and physical bindings exclusively from the approved environment manifest. Every operation retains destination, strategy, contract and activation-revision validation. Spark and supported Fabric notebook context are resolved internally. Missing notebook audit identity is represented as absent, never fabricated or substituted for approval identity.

### Source participation and execution boundaries

Every successful Read registers with the current execution instance. Every subsequent Write receives that execution's registered sources. These associations describe pipeline participation, not proven DataFrame transformation lineage. Context-local state and unique run IDs isolate executions; failure, repeated setup and shutdown clear source references.

Run `finalize_pipeline(CONTRACTS)` after all Reads, transformations and Writes, including read-only pipelines. It records the complete outcome and releases Live reservations. Pass `failed=True` for a caught project exception. Test publishes `METADATA_GUARDRAIL_RESULTS` first and its authoritative `METADATA_PIPELINE_RUN` snapshot last; normal Test operations still commit no metadata. Publication requires complete runtime audit identity. Repeating finalization with the same session is idempotent, including retries after an interrupted diagnostic publication.

A successful Write or Fabric cell does not prove whole-notebook completion. Observed errors seal failure; repeated setup and shutdown seal unfinalized runs as **incomplete**. A killed process may retain an incomplete Live record and reservation. Operators must confirm execution stopped before repairing a reservation. Headless code must call Finalize after its full transformation workflow, or use `failed=True` when it catches a project failure.

Activation still requires a complete successful Testing record, exact frozen contracts for every participant, all required operation and Guardrail results, an effective Data Agreement and explicit Governance approval. Failed, incomplete, mixed-contract and No Contract runs cannot activate. Finalization never activates or deploys a pipeline.

## Activate, deploy and run unattended

Use `widget_activate_pipeline()` in `01_governance`. Select a successful Testing run in the activation environment, its immutable release version and exact effective Agreement. The widget shows current/proposed contracts, writer ownership, affected pipelines, available tests and blockers. Include compatible successful candidates for every directly affected active pipeline. Downstream pipelines require replacement tests when a selected replacement changes their input table's contract or writer expectations; unchanged output expectations stop propagation. There is no inferred compatibility engine.

Review the complete release and explicitly approve it once. The backend independently rechecks every selected candidate, complete operation/rule results, processing configuration, contract payloads and Agreement. It checks the current authority token again at commit. Failed validation, missing tests, competing writers, inconsistent contracts, stale review or a failed commit expose no partial release. Refresh and review again after a conflict.

`METADATA_ACTIVATION_STATE` is the single authoritative central row. Its `snapshot_json` contains environment revisions, active pipeline manifests, immutable approval history, active table contracts, readers/writers and running execution reservations. One serializable Delta compare-and-swap updates this row. The central row intentionally serializes concurrent metadata changes; disjoint environments are isolated in policy but may experience a stale-token conflict and require review again. There is no cross-table atomicity claim.

Within each environment, distinct table identities cannot alias the same physical destination. Reservations also protect physical destinations when a proposed activation uses another table identity in the same environment. Every Read and Write checks its actual resolved physical destination against the plan's frozen binding, including case variants of configured store keys. One contract version and at most one writer own a table; multiple readers may share its exact contract. One approved configuration exists per pipeline. DEV and PROD reference the same global contract history and can approve different versions. `METADATA_DATA_CONTRACT.environment_name` records authoring provenance, not version identity. All Metadata targets must resolve to the same central Lakehouse.

### Live cutover and deployment

Live setup automatically resolves the approved environment configuration and reserves the run in the same authority transaction. It pins one activation revision for its lifetime. Approval affecting a running pipeline or reserved destination is blocked until that execution completes. New runs cannot mix revisions during cutover. Runs for unrelated pipelines may continue. No lease expires automatically: after a notebook crash, operators must confirm the execution is stopped before removing its run reservation from the authority through a reviewed metadata repair. Never clear a reservation merely because it is old.

Deploy notebooks through Engineering source control, CI/CD and Microsoft Fabric tooling. Approval never deploys a notebook or writes business data. No FabricOps packaging or deployment verification call is required. Live validates exact global tables, environment destinations, Data Contract versions, ownership and transformation settings against central approval.

```python
CONTRACTS = setup_pipeline(pipeline_id="example-orders", pipeline_mode="Live")
# Read → Transform → Write; approved authority is resolved internally.
```

Profiling options, diagnostic detail and repartitioning may differ from the tested operation; Live emits warnings and records tested and actual values. Contract mappings, table identities, roles, destinations, source relationships, SQL settings, read/write strategies and transformation settings require approval. Retest changed Data Contract or processing configuration before coordinated approval. Prior approvals containing executable/dependency identity require fresh complete Testing and activation; frozen Data Contracts remain unchanged.

### Upgrade boundary and limitations

Run `setup_metadata_tables()` once under controlled metadata administration to create the singleton authority. Existing per-pipeline approvals are not imported or trusted. Existing environment-specific contract histories need deliberate reconciliation into one global lifecycle per table, followed by complete Testing and activation; no compatibility shim or automatic migration is provided. Old tables are not deleted automatically.

The authority uses a single JSON snapshot to guarantee metadata atomicity, trading scalability for a conservative first implementation. Large estates may need a transactional metadata service later. Actual Fabric/Delta runtime validation remains required before deployment. Managed token-vault and caller-owned mapping dependencies without verifiable immutable identities remain ineligible for activation. Notebook deployments, business-table transactions, guardrail diagnostics and run evidence retain separate failure boundaries.
