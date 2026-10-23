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

## Workspace configuration

Deploy the same `00_env_config.ipynb` template in each workspace that runs FabricOps notebooks, named `00_env_config` in Fabric. Both Governance and Engineering load their current workspace's configuration by default.

Populate `ENVIRONMENT_WORKSPACES` with one unique workspace ID per environment and fill the existing `FrameworkConfig` store mappings. Each workspace resolves its environment automatically; engineers do not select an environment. Keep every Metadata mapping pointed at the same central Metadata Lakehouse. Unknown workspace IDs and duplicate workspace assignments fail setup.

For advanced cross-workspace use, deploy a shared `00_env_config` in Central Engineering and pass its workspace ID explicitly:

```python
# Optional: load configuration from another workspace.
CONFIG_WORKSPACE_ID = "<configuration-workspace-id>"
context = setup_notebook(config_workspace_id=CONFIG_WORKSPACE_ID)
# Or in an Engineering pipeline:
pipeline = setup_pipeline(config_workspace_id=CONFIG_WORKSPACE_ID)
```

The shared deployment must register the caller workspace in `ENVIRONMENT_WORKSPACES`. The execution identity needs permission to run the remote notebook and access its configured stores. No environment variable or separate configuration file is required. Omitting `config_workspace_id` always uses the caller workspace.

`setup_notebook()` passes Fabric `currentWorkspaceId` to the config notebook through `notebookutils.notebook.run(..., workspaceId=...)`. The config notebook resolves that caller ID and returns JSON using `notebookutils.notebook.exit()`. Setup reconstructs the existing `FrameworkConfig`, validates it, applies the audit timezone, and initializes the shared context using the caller's runtime identity.

```python
# 01 Governance
from fabricops_kit import setup_notebook
context = setup_notebook()

# 02 Pipeline
from fabricops_kit import setup_pipeline, finalize_pipeline
pipeline = setup_pipeline()  # Notebook name supplies pipeline_id; Test is the default.
# Read → Transform → Write
finalize_pipeline()
```

An explicit `pipeline_id` remains useful when notebook names can change; `pipeline_mode="Live"` retains the existing approved-manifest behavior. Neither requires an environment argument. Explicit `setup_notebook(CONFIG, env=...)` remains supported for local validation and advanced callers.

Configuration loads do not create metadata tables. At deployment, run the Governance config notebook directly with `INITIALIZE_METADATA = True` once, then restore `False` before ordinary use.

## Pipeline execution mode

The pipeline flow is **Setup Pipeline → Read → Transform → Write**. Environment routing is resolved automatically from the caller workspace by the selected `00_env_config`. A stable `pipeline_id` identifies the logical pipeline independently of notebook names and paths.

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

## Shared table profiling

Profiling policies belong to `METADATA_DATA_CONTRACT.contract_payload_json.profiling`. The **Profiling** section in Data Contract Authoring edits the selected draft through the normal Save action. Freeze, complete Testing and activate the new version before Live uses it. Frozen payloads and existing activation snapshots are immutable. A profiling change changes the contract fingerprint and requires the existing approval workflow. Profiling policies remain separate from `guardrails` and never enable, disable or change enforcement.

| Activity | Default frequency | Trigger |
| --- | --- | --- |
| Standard Profiling | First eligible run after 1 day | Read or Write |
| Grain Discovery | First eligible run only | Read or Write |
| Frequency Profiling | First eligible run only | Read or Write |

Each activity independently supports `every`, `first` or `interval` (a positive integer `days`), and `read`, `write` or `read_or_write`. Intervals measure elapsed time from successful completion. For example:

```json
{"profiling":{"standard":{"frequency":"interval","days":1,"trigger":"read_or_write"},"grain":{"frequency":"first","trigger":"read_or_write"},"frequency":{"frequency":"first","trigger":"read_or_write"}}}
```

Explicit No Contract execution uses these fixed defaults without creating a contract. Existing frozen versions without a profiling section use the same defaults; they are never rewritten. New drafts and newly frozen versions contain explicit policies. Activation continues to require frozen contracts for all participants.

Read-triggered profiling scans the complete persisted table, including when the Read uses a query, filter or incremental scope. Write-triggered profiling follows successful publication. Failed, blocked and empty nonpublishing Writes do not consume intervals. Read-only Testing computes eligible diagnostics without claims or metadata writes; it cannot consume a schedule or profile an unpublished target as published data.

`METADATA_PIPELINE_RUN.operation_summary_json.profiling` records independent activity events with Table ID, environment, physical workspace/item/schema/table bindings, context key, activity, trigger, Pipeline Run ID, timestamp, status, safe failure/skip reason and result snapshot ID. Running events distinguish attempts from completion. Skips distinguish trigger mismatch, first-only completion, an unelapsed interval and claim contention. Pipeline completion remains a separate field; a skipped activity permits pipeline success. Multiple tables retain independent activity events in the same logical run row.

Successful Standard and nonempty Frequency history is derived by joining confirmed successful activity events to `METADATA_DATA_PROFILED` and `METADATA_DATA_PROFILED_FREQUENCY` snapshots. Missing results or an unconfirmed/failed attempt cannot consume an interval. Catalogue candidate-key JSON is overwritten and cannot reliably establish per-destination historical Grain completion, including successful discovery with no candidates. Grain therefore uses a minimal durable success marker in the Pipeline Run activity event. Frequency with no eligible columns uses the same marker rather than inventing distribution rows. A failed pipeline may still contain an earlier successfully completed profiling activity.

Spark filters activity events to the exact physical context, joins result snapshots and aggregates the latest completion before collecting at most three activity timestamps. Claiming checks each activity once; trigger mismatches require no history query. History is shared across pipelines using the same Table ID, environment and physical destination. Pipeline ID is never a schedule key. Development, Production, other workspaces and other physical items remain isolated. Independent Frequency snapshots retain their own snapshot ID and leave `profile_id` null. Existing metrics, snapshots and Catalogue candidates are preserved. Source Observation retains incremental source-state responsibility; profiling never advances watermarks or changes Guardrails.

Renewable claims use the existing `METADATA_ACTIVATION_STATE` serializable Delta compare-and-swap authority. Its `profiling_claims` contains only active reservations, not policies or copied success history. Claims expire after five minutes, renew every thirty seconds and before persistence, and reject expired or replaced owners. Expired entries are pruned during subsequent claims. After results persist, the worker stops its heartbeat and checks for renewal failures. A final owned compare-and-swap authorizes completion and captures its timestamp before Pipeline Run can publish success. The reservation remains until the journal commit finishes or its lease expires; an interrupted finalization can conservatively retry after expiry. Failed journal writes are removed from the in-memory journal so later run snapshots cannot publish unconfirmed success. A lost acknowledgement uses the existing run-row read-back verification. Failures and abandoned attempts remain eligible after release or expiry. Metadata transactions across result tables, Catalogue, Pipeline Run and Activation State are separate; lease checks at persistence boundaries cannot provide an atomic transaction under a paused process or network partition. Isolated snapshot IDs preserve outputs, and an unconfirmed completion is conservatively retried.

After upgrading, run `setup_metadata_tables()` under controlled administration. No profiling table is initialized. Existing deployments may retain `METADATA_TABLE_PROFILING` as an archive; runtime and authoring never read or mutate it. Do not copy its mutable policies into active contracts: author a new draft, freeze, test and activate deliberately. Older snapshots without a confirmed physical binding and independent activity completion remain historical records and cannot safely suppress a destination's schedule. The first eligible run establishes confirmed history. Standalone `profile_table()` retains its existing outputs and history; without a Pipeline Run physical binding it does not suppress scheduled work.

### Upgrade boundary and limitations

Run `setup_metadata_tables()` once under controlled metadata administration to create the singleton authority. Existing per-pipeline approvals are not imported or trusted. Existing environment-specific contract histories need deliberate reconciliation into one global lifecycle per table, followed by complete Testing and activation; no compatibility shim or automatic migration is provided. Old tables are not deleted automatically.

The authority uses a single JSON snapshot to guarantee metadata atomicity, trading scalability for a conservative first implementation. Large estates may need a transactional metadata service later. Actual Fabric/Delta runtime validation remains required before deployment. Managed token-vault and caller-owned mapping dependencies without verifiable immutable identities remain ineligible for activation. Notebook deployments, business-table transactions, guardrail diagnostics and run evidence retain separate failure boundaries.
