# Notebook templates

Download these notebooks and import them into Microsoft Fabric.

| Notebook | Purpose |
| --- | --- |
| `00_env_config.ipynb` | Configure workspaces and Fabric stores. |
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

Populate `ENGINEERING_WORKSPACES` with one unique workspace ID per workspace and fill the existing `FrameworkConfig` store mappings. Setup derives the caller workspace ID automatically. Keep every Metadata mapping pointed at the same central Metadata Lakehouse. Unknown workspace IDs and duplicate workspace assignments fail setup.

For advanced cross-workspace use, deploy a shared `00_env_config` in Central Engineering and pass its workspace ID explicitly:

```python
# Optional: load configuration from another workspace.
CONFIG_WORKSPACE_ID = "<configuration-workspace-id>"
context = setup_notebook(config_workspace_id=CONFIG_WORKSPACE_ID)
# Then, in an Engineering pipeline:
pipeline = setup_pipeline(pipeline_mode="Ungoverned")
PIPELINE_ID = pipeline.pipeline_id
```

The shared deployment must register the caller workspace in `ENGINEERING_WORKSPACES`. The execution identity needs permission to run the remote notebook and access its configured stores. No process environment variable or separate configuration file is required. Omitting `config_workspace_id` always uses the caller workspace.

`setup_notebook()` passes Fabric `currentWorkspaceId` to the config notebook through `notebookutils.notebook.run(..., workspace=...)`. The config notebook resolves that caller ID and returns JSON using `notebookutils.notebook.exit()`. Setup reconstructs the existing `FrameworkConfig`, validates it, applies the audit timezone, and initializes the shared context using the caller's runtime identity.

```python
# 01 Governance
from fabricops_kit import setup_notebook
context = setup_notebook()

# 02 Pipeline
from fabricops_kit import setup_notebook, setup_pipeline, finalize_pipeline
context = setup_notebook()
pipeline = setup_pipeline()  # Register or recover the notebook binding; default Ungoverned.
PIPELINE_ID = pipeline.pipeline_id
# Read → Transform → Write
finalize_pipeline()
```

Omit `pipeline_id` on the first Ungoverned execution to register or recover a permanent UUIDv4. Dry Run never writes registration state and may use a session-only UUID. The notebook automatically assigns `PIPELINE_ID = pipeline.pipeline_id`; retain that UUID in source only for cross-workspace promotion. Neither setup function requires a workspace argument.

Configuration loads do not create metadata tables. At deployment, run the Governance config notebook directly with `INITIALIZE_METADATA = True` once, then restore `False` before ordinary use.

## Logical aliases and physical Fabric names

Store keys such as `Gold` select FabricOps configuration, contracts and metadata.
`FabricStore.name` supplies the actual Fabric item name; for example, an alias
`Gold` with `name="wh_Example_Product"` routes Warehouse reads and writes to
`wh_Example_Product.dbo.orders`. Query `DatabaseName`, staging and cleanup use
that same physical Warehouse name. Workspace and item UUIDs still select the
Fabric workspace and item. Lakehouse storage paths continue to use those UUIDs.

Set `name` when the Warehouse name differs from its alias. Existing configurations
without `name` continue to use the alias as the physical name. The new field is
optional and keyword-only, so existing positional constructors retain their meaning.
Workspace labels and store aliases are project choices: Development / Test / Production
and Bronze / Silver / Gold are examples, and custom aliases such as `Source`,
`Unified` and `Product` remain supported. Replace every ID/name placeholder in
`00_env_config` before running it; the template validates them before deployment IO.
See the [Microsoft Fabric Spark Warehouse connector documentation](https://learn.microsoft.com/en-us/fabric/data-engineering/spark-data-warehouse-connector) for query and three-part target semantics.

## Governance configuration

**Run simply → Govern deliberately → Enforce consistently.**

`00_env_config` uses `ENGINEERING_WORKSPACES` and compiles `WORKSPACE_PATHS`, keyed by stable workspace ID. Store names such as Bronze, Silver and Gold are configurable aliases. Business stores belong to their Engineering workspace; Metadata always points to the same central Governance Lakehouse.

Governance has only the Metadata target. Its runtime workspace remains its audit identity. In the Data Contract widget, deliberately select a Table and Workspace to create a draft from that workspace's current observation. Contract history is global for the selected table. Workspace appears at the far right and filters bidirectionally with Table. No arbitrary workspace or table is selected.

On first setup, run the complete notebook in Ungoverned mode, including `pipeline_result = finalize_pipeline(pipeline)`. Read and Write automatically calculate due profiles and persist operational metadata around the real publication. Dry Run is available when you need a non-persistent preview. No manual `profile_table()` calls or duplicated observation coordinates are needed.

New drafts capture every current observed column once. Columns default to required presence; optional presence is distinct from nullability. Missing required columns, uncontracted extra columns and normalized datatype differences block Governed execution. New profiles never mutate contracts. Unprofiled columns remain governable and display “Not yet profiled”.

In Pipeline Activation, select the Engineering workspace, pipeline and reviewed activation evidence. The workspace independently activates the selected release and frozen contracts. Other workspaces can use other versions. Deployment belongs to Fabric/CI tooling; no promotion sequence is enforced.

`01_governance` uses `setup_notebook(required_targets=["Metadata"])`. Ordinary Engineering notebooks use `setup_notebook()` and `setup_pipeline()` without workspace arguments. Explicit local setup supplies `workspace_id`; the returned setup object exposes `workspace_id`.

## Pipeline execution mode

The pipeline flow is **Setup Notebook → Setup Pipeline → Read → Transform → Write → Finalize**. `setup_notebook()` initializes configuration and displays readiness; `setup_pipeline()` reuses that configuration and displays only pipeline details. Call notebook setup first; missing, failed or outdated setup produces an actionable error. Rerunning notebook setup closes the current pipeline and invalidates its old configuration before attempting a reload. Workspace routing is resolved automatically from the caller workspace by the selected `00_env_config`. A stable `pipeline_id` identifies the logical pipeline independently of notebook names and paths.

```python
context = setup_notebook()
pipeline = setup_pipeline(pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52", pipeline_mode="Ungoverned")
source = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
transformed = transform(source["dataframe"])
result = orchestrate_write(transformed, store="Gold", schema="demo",
                           table_name="customer_summary", write_mode="overwrite")
pipeline_result = finalize_pipeline(pipeline)
```

`pipeline_mode` accepts exactly three values:

| Mode | What it does | Data Contract |
| --- | --- | --- |
| `"Dry Run"` | Reads and transforms real data, profiles and validates where applicable, but never writes target data or operational state. | Optional |
| `"Ungoverned"` | Runs real reads and writes with profiling, lineage and operational metadata, without contract-dependent checks. | Not required |
| `"Governed"` | Runs real reads and writes while enforcing the exact activated contracts and workspace authority. | Activated contract required |

Dry Run contract choices lock when operations start. Ungoverned does not offer contract selection and fails if a target is already governed, so an activated Sensitive Data rule or other protection cannot be bypassed. Governed revalidates activation, contract versions, ownership, destinations and operation settings at setup and again during execution.

`METADATA_PIPELINE_RUN.execution_mode` remains a string, so no metadata schema migration is required. New runs store `dry_run`, `ungoverned` or `governed` (Dry Run summaries are session-only and therefore are not normally present). Historical `testing` and `live` rows remain readable for retained approvals and profiling history; new setup calls do not accept the old display names.

### Source participation and execution boundaries

Every successful Read registers with the current execution instance. Every subsequent Write receives that execution's registered sources. These associations describe pipeline participation, not proven DataFrame transformation lineage. Context-local state and unique run IDs isolate executions; failure, repeated setup and shutdown clear source references.

Run `finalize_pipeline(pipeline)` after all Reads, transformations and Writes, including read-only pipelines. It returns the complete outcome and releases Governed reservations. Pass `failed=True` for a caught project exception. Dry Run returns a session-only summary; Ungoverned and Governed persist their real execution mode and outcome. Repeating finalization with the same session is idempotent.

A successful Write or Fabric cell does not prove whole-notebook completion. Observed errors seal failure; repeated setup and shutdown seal unfinalized runs as **incomplete**. A killed process may retain an incomplete Governed record and reservation. Operators must confirm execution stopped before repairing a reservation. Headless code must call Finalize after its full transformation workflow, or use `failed=True` when it catches a project failure.

Activation still requires exact frozen contracts for every participant, complete accepted validation evidence, an effective Data Agreement and explicit Governance approval. Failed, incomplete, mixed-contract and No Contract evidence cannot activate. Finalization never activates or deploys a pipeline.

## Activate, deploy and run unattended

Open `widget_activate_pipeline()` in Governance to review the retained activation evidence for the current workspace. Select the immutable pipeline version and exact Agreement. Every source and target must have its exact frozen contract; warnings may permit completion, while blocking results, failures and incomplete operations prevent activation. Include compatible accepted candidates for affected dependent pipelines.

Review the complete release and explicitly approve it once. The backend independently rechecks every selected candidate, complete operation/rule results, processing configuration, contract payloads and Agreement. It checks the current authority token again at commit. Failed validation, missing tests, competing writers, inconsistent contracts, stale review or a failed commit expose no partial release. Refresh and review again after a conflict.

`METADATA_PIPELINE_REGISTRY` is the single authoritative central row. Its native collections contain workspace revisions, active pipeline manifests, immutable approval history, active table contracts, readers/writers and running execution reservations. One serializable Delta compare-and-swap updates this row. The central row intentionally serializes concurrent metadata changes; disjoint workspaces are isolated in policy but may experience a stale-token conflict and require review again. There is no cross-table atomicity claim.

Within each workspace, distinct table identities cannot alias the same physical destination. Reservations also protect physical destinations when a proposed activation uses another table identity in the same workspace. Every Read and Write checks its actual resolved physical destination against the plan's frozen binding, including case variants of configured store keys. One contract version and at most one writer own a table; multiple readers may share its exact contract. One approved configuration exists per pipeline. DEV and PROD reference the same global contract history and can approve different versions. `METADATA_DATA_CONTRACT.workspace_id` records authoring provenance, not version identity. All Metadata targets must resolve to the same central Lakehouse.

### Governed cutover and deployment

Governed setup automatically resolves the activated workspace configuration and reserves the run in the same authority transaction. It pins one activation revision for its lifetime. Activation changes affecting a running pipeline or reserved destination are blocked until that execution completes. New runs cannot mix revisions during cutover. Runs for unrelated pipelines may continue. No lease expires automatically: after a notebook crash, operators must confirm the execution is stopped before removing its run reservation through a reviewed metadata repair.

Deploy notebooks through Engineering source control, CI/CD and Microsoft Fabric tooling. Activation never deploys a notebook or writes business data. Governed validates exact global tables, workspace destinations, Data Contract versions, ownership and transformation settings against central authority.

```python
context = setup_notebook()
pipeline = setup_pipeline(pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52", pipeline_mode="Governed")
# Read → Transform → Write; approved authority is resolved internally.
```

Profiling options, diagnostic detail and repartitioning may differ from the approved operation; Governed execution emits warnings and records approved and actual values. Contract mappings, table identities, roles, destinations, source relationships, SQL settings, read/write strategies and transformation settings require approval. Revalidate a changed Data Contract or processing configuration before coordinated approval. Prior approvals containing executable/dependency identity require fresh complete validation and activation; frozen Data Contracts remain unchanged.

## Shared table profiling

Profiling policies belong to `METADATA_DATA_CONTRACT.contract_payload_json.profiling`. The **Profiling** section in Data Contract Authoring edits the selected draft through the normal Save action. Freeze, validate and activate the new version before Governed execution uses it. Frozen payloads and existing activation snapshots are immutable. A profiling change changes the contract fingerprint and requires the existing approval workflow. Profiling policies remain separate from `guardrails` and never enable, disable or change enforcement.

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

Read-triggered profiling scans the complete persisted table, including when the Read uses a query, filter or incremental scope. Write-triggered profiling follows successful publication. Failed, blocked and empty nonpublishing Writes do not consume intervals. Dry Run computes eligible diagnostics without claims or metadata writes; it cannot consume a schedule or profile an unpublished target as published data.

`METADATA_PIPELINE_RUN.profiling` records independent activity events with Table ID, workspace, physical workspace/item/schema/table bindings, context key, activity, trigger, Pipeline Run ID, timestamp, status, safe failure/skip reason and result snapshot ID. Running events distinguish attempts from completion. Skips distinguish trigger mismatch, first-only completion, an unelapsed interval and claim contention. Pipeline completion remains a separate field; a skipped activity permits pipeline success. Multiple tables retain independent activity events in the same logical run row.

Successful Standard and nonempty Frequency history is derived by joining confirmed successful activity events to `METADATA_DATA_PROFILED` and `METADATA_DATA_PROFILED_FREQUENCY` snapshots. Missing results or an unconfirmed/failed attempt cannot consume an interval. Catalogue candidate-key JSON is overwritten and cannot reliably establish per-destination historical Grain completion, including successful discovery with no candidates. Grain therefore uses a minimal durable success marker in the Pipeline Run activity event. Frequency with no eligible columns uses the same marker rather than inventing distribution rows. A failed pipeline may still contain an earlier successfully completed profiling activity.

Spark filters activity events to the exact physical context, joins result snapshots and aggregates the latest completion before collecting at most three activity timestamps. Claiming checks each activity once; trigger mismatches require no history query. History is shared across pipelines using the same Table ID, workspace and physical destination. Pipeline ID is never a schedule key. Development, Production, other workspaces and other physical items remain isolated. Independent Frequency snapshots retain their own snapshot ID and leave `profile_id` null. Existing metrics, snapshots and Catalogue candidates are preserved. Source Observation retains incremental source-state responsibility; profiling never advances watermarks or changes Guardrails.

Profiling eligibility uses the configured trigger and frequency policy together with successful completion history in `METADATA_PIPELINE_RUN`. Profiling does not reserve or update `METADATA_PIPELINE_REGISTRY`. Concurrent executions are allowed and use isolated snapshot IDs; Delta merges make each snapshot write idempotent, and only a successfully journaled Pipeline Run completion advances first-run or periodic scheduling. A failed or unconfirmed attempt remains eligible for retry. Two executions can both observe profiling as due and publish duplicate snapshots. Metadata transactions across profile results, Catalogue and Pipeline Run remain separate, so an interrupted attempt can leave an unreferenced snapshot that later history ignores; this bounded duplication is preferred to a profiling lock or lease framework.

After upgrading, run `setup_metadata_tables()` under controlled administration. No profiling table is initialized. Existing deployments may retain `METADATA_TABLE_PROFILING` as an archive; runtime and authoring never read or mutate it. Do not copy its mutable policies into active contracts: author a new draft, freeze, test and activate deliberately. Older snapshots without a confirmed physical binding and independent activity completion remain historical records and cannot safely suppress a destination's schedule. The first eligible run establishes confirmed history. Standalone `profile_table()` retains its existing outputs and history; without a Pipeline Run physical binding it does not suppress scheduled work.

### Upgrade boundary and limitations

Run `setup_metadata_tables()` once under controlled metadata administration to create the singleton authority. Existing per-pipeline approvals are not imported or trusted. Existing workspace-specific contract histories need deliberate reconciliation into one global lifecycle per table, followed by complete validation and activation; no compatibility shim or automatic migration is provided. Old tables are not deleted automatically.

The authority uses a single JSON snapshot to guarantee metadata atomicity, trading scalability for a conservative first implementation. Large estates may need a transactional metadata service later. Actual Fabric/Delta runtime validation remains required before deployment. Managed token-vault and caller-owned mapping dependencies without verifiable immutable identities remain ineligible for activation. Notebook deployments, business-table transactions, guardrail diagnostics and run evidence retain separate failure boundaries.


### Permanent pipeline identity

`setup_pipeline(pipeline_mode="Ungoverned")` resolves the caller workspace and notebook IDs, recovers their exact Active registration, or allocates a UUIDv4 in `engineering.METADATA_PIPELINE_REGISTRY`. Assign `PIPELINE_ID = pipeline.pipeline_id` immediately after setup, as the templates do. Dry Run does not persist a new registration. Governed requires an existing registered and activated identity. The returned session exposes `pipeline.pipeline_id`; its execution ID remains separate.

Notebook names are informational. A rename preserves identity. After reupload, call `setup_pipeline(pipeline_id=PIPELINE_ID, pipeline_mode="Ungoverned", previous_workspace_id=..., previous_notebook_id=...)` to approve moving the existing workspace binding to the caller. For an independent notebook copy, omit the copied UUID and call `setup_pipeline(pipeline_mode="Ungoverned", new_pipeline=True)`. Neither action changes activated authority.

`pipeline_result = finalize_pipeline(pipeline)` records the accurate completion status for persisting modes and returns a session-only summary for Dry Run. Governance validates the current workspace/notebook registration, complete accepted evidence, exact contracts per table, configuration and Agreement, then freezes the approved manifest in `engineering.METADATA_PIPELINE_REGISTRY`. Dry Run does not commit business tables; Governed execution exercises the activated publication permissions and target transaction.
