# Plug-and-Play Data Pipelines with Optional Data Contract Enforcement

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

![Development to Production pipeline promotion](../assets/05/PipelinesDeploymentOverview.png){ .fabricops-solution-hero }

## The problem

Building a reliable data pipeline involves much more than reading a table, transforming a DataFrame, and writing the result. Engineers also need to handle environment resolution, incremental processing, load strategies, metadata, profiling, Data Contracts, Guardrails, validation, lineage, and the differences between Fabric Lakehouses and Warehouses.

A new engineer should not need to understand or rebuild all of that governance and engineering plumbing before they can create a reliable pipeline. At the same time, the framework should not hide so much that nobody can understand what the pipeline is doing.

FabricOps keeps that work behind a readable notebook flow: **Setup → Read → Transform → Write → Finalize**. Engineers own the PySpark transformation; FabricOps handles the repeatable pipeline operations and applies Data Contract enforcement when Governed mode is selected.

## The solution

<div class="fabricops-mascot-callout">
  <span style="display:inline-flex;align-items:center;gap:0.4rem;flex-shrink:0">
    <img src="/FabricOps-Starter-Kit/assets/mascots/robot-dev.png" alt="Development mascot" loading="eager">
    <img src="/FabricOps-Starter-Kit/assets/mascots/robot-prod.png" alt="Production mascot" loading="eager">
  </span>
  <div><p>FabricOps provides a <strong>clonable two-notebook engineering stack</strong>:</p></div>
</div>

- [`00_env_config.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb) maps logical Fabric Stores to the correct environment-specific Fabric locations.
- [`02_pipeline.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb) keeps the pipeline definition portable between environments, with FabricOps Read and Write boundaries around ordinary project-owned PySpark.

The result is a pipeline pattern that engineers can clone and adapt without rebuilding the governance and engineering plumbing each time.

Inside `02_pipeline.ipynb`, four functions frame the engineer's own transformation:

| Pipeline function | Purpose |
| --- | --- |
| `setup_pipeline()` | Establish the pipeline run and selected execution mode. |
| `orchestrate_read()` | Read each source using its chosen Read Mode. |
| `orchestrate_write()` | Publish each prepared target using its chosen Write Mode (or preview in Dry Run). |
| `finalize_pipeline()` | Complete run tracking after the project work finishes. |

**Between Read and Write, the PySpark logic belongs to the project.** Engineers can join, filter, enrich, or aggregate DataFrames as needed; FabricOps does not prescribe the transformation. The same pipeline can read multiple sources and write multiple targets.


### The big picture

```mermaid
flowchart LR
    subgraph DEV["Development — clonable notebook stack"]
        direction TB
        DEV_ENV["00 Env Config<br/>resolves Development<br/>Fabric Store locations"]
        subgraph DEV_PIPE["02 Pipeline"]
            direction TB
            DEV_CONTRACT["setup_pipeline()<br/>Configure Data Contracts"]
            DEV_READ_FULL["Read Table 1<br/>Full"]
            DEV_READ_INC["Read Table 2<br/>Incremental"]
            DEV_TRANSFORM["Project-specific<br/>PySpark transformation"]
            DEV_WRITE_OVERWRITE["Write Table 1<br/>Overwrite"]
            DEV_WRITE_APPEND["Write Table 2<br/>Append"]
            DEV_WRITE_SCD1["Write Table 3<br/>SCD1"]
            DEV_WRITE_SCD2["Write Table 4<br/>SCD2"]
            DEV_FINALIZE["finalize_pipeline()<br/>Complete run tracking"]
            DEV_CONTRACT --> DEV_READ_FULL --> DEV_TRANSFORM
            DEV_CONTRACT --> DEV_READ_INC --> DEV_TRANSFORM
            DEV_TRANSFORM --> DEV_WRITE_OVERWRITE
            DEV_WRITE_OVERWRITE --> DEV_FINALIZE
            DEV_TRANSFORM --> DEV_WRITE_APPEND
            DEV_WRITE_APPEND --> DEV_FINALIZE
            DEV_TRANSFORM --> DEV_WRITE_SCD1
            DEV_WRITE_SCD1 --> DEV_FINALIZE
            DEV_TRANSFORM --> DEV_WRITE_SCD2
            DEV_WRITE_SCD2 --> DEV_FINALIZE
        end
        DEV_ENV --> DEV_PIPE
        DEV_PIPE --> DEV_RES["Development<br/>Fabric Store locations"]
    end

    subgraph PROD["Production — same notebook stack"]
        direction TB
        PROD_ENV["00 Env Config<br/>resolves Production<br/>Fabric Store locations"]
        subgraph PROD_PIPE["02 Pipeline"]
            direction TB
            PROD_CONTRACT["setup_pipeline()<br/>Resolve approved Data Contracts"]
            PROD_READ_FULL["Read Table 1<br/>Full"]
            PROD_READ_INC["Read Table 2<br/>Incremental"]
            PROD_TRANSFORM["Project-specific<br/>PySpark transformation"]
            PROD_WRITE_OVERWRITE["Write Table 1<br/>Overwrite"]
            PROD_WRITE_APPEND["Write Table 2<br/>Append"]
            PROD_WRITE_SCD1["Write Table 3<br/>SCD1"]
            PROD_WRITE_SCD2["Write Table 4<br/>SCD2"]
            PROD_FINALIZE["finalize_pipeline()<br/>Complete run tracking"]
            PROD_CONTRACT --> PROD_READ_FULL --> PROD_TRANSFORM
            PROD_CONTRACT --> PROD_READ_INC --> PROD_TRANSFORM
            PROD_TRANSFORM --> PROD_WRITE_OVERWRITE
            PROD_WRITE_OVERWRITE --> PROD_FINALIZE
            PROD_TRANSFORM --> PROD_WRITE_APPEND
            PROD_WRITE_APPEND --> PROD_FINALIZE
            PROD_TRANSFORM --> PROD_WRITE_SCD1
            PROD_WRITE_SCD1 --> PROD_FINALIZE
            PROD_TRANSFORM --> PROD_WRITE_SCD2
            PROD_WRITE_SCD2 --> PROD_FINALIZE
        end
        PROD_ENV --> PROD_PIPE
        PROD_PIPE --> PROD_RES["Production<br/>Fabric Store locations"]
    end

    DEV ==>|"Promote 1:1"| PROD
```

The same pipeline definition can move between Development and Production: each workspace resolves its own Fabric Stores, while Governed execution enforces the activated Data Contracts.

### Choose an execution mode

| Capability | Dry Run | Ungoverned | Governed |
| --- | --- | --- | --- |
| Automatic profiling | Yes | Yes | Yes |
| Publish data | No | Yes | Yes |
| Persist observations | No | Yes | Yes |
| Activated Data Contract required | No | No | Yes |
| Enforce contract guardrails | Yes | No | Yes |

**Ungoverned** runs without Data Contracts. **Dry Run** previews without writing. **Governed** enforces activated Data Contracts. Pipeline source participation and reporting are automatic.

## From Dry Run to Governed execution

Start with **Dry Run** to inspect the pipeline's Read, transformation, and Write results without publishing data or persisting observations. An optional frozen Data Contract can be evaluated during this preview; Dry Run does not activate it.

A **Data Contract** defines the agreed schema, Grain, Data Quality rules, and Sensitive Data expectations for a table. Governance authors and freezes a version, and engineers validate the pipeline against that version. When it is ready for use, Governance **activates the Data Contract for the relevant table in the target workspace's environment**. That activation selects the contract version that Governed runs must enforce there.

**Ungoverned** remains available for pipelines without an activated Data Contract, while **Governed** requires the applicable active contracts and enforces their rules at the Read and Write boundaries. Activation is a **table-and-environment decision**, not a separate activation for every pipeline that uses the table. Pipelines sharing a table in the same environment therefore use its same active contract version.

This section describes validation and activation within a workspace; deployment and promotion are outside its scope.

## Read & Write Modes

Read Mode controls **which source rows to process**. Write Mode controls **how the prepared rows update the target**. They are selected independently for each Read and Write operation.

| Side | Mode | What it does |
| --- | --- | --- |
| Read | **Full** | Read the complete source. |
| Read | **Incremental** | Read unprocessed source changes for the target. |
| Write | **Overwrite** | Replace the target with the prepared result. |
| Write | **Append** | Add prepared rows to the target. |
| Write | **SCD1** | Update the latest state by business key. |
| Write | **SCD2** | Preserve historical versions of changes by business key. |

A common pattern is **Full → Overwrite** for rebuilding a target or **Incremental → Append** for adding new records. SCD1 and SCD2 support changing records. See [Read & Write Modes](../reference/read-and-load-strategies.md) for detailed behavior and examples.

## How it works

| Responsibility | What happens |
| --- | --- |
| **Engineer configures** | Chooses logical sources and targets, Read and Write modes, the project-specific PySpark transformation, and whether to run in Dry Run, Ungoverned or Governed mode. |
| **AI can support** | Microsoft Fabric Copilot or another coding agent can help write or refactor project-specific PySpark. AI is optional and is not part of pipeline execution or enforcement. |
| **FabricOps handles deterministically** | Resolves environment-specific Fabric locations, runs Read and Write orchestration, enforces activated Data Contracts in Governed mode, and records the applicable metadata, profiling, lineage, processing state and run outcome for persisting modes. |

## What FabricOps Takes Care of for You

Reliable pipelines need more than a successful write. These six engineering decisions explain how FabricOps handles the difficult cases. Expand a title for the implementation, stored evidence and trade-off.

??? info "A failed run shouldn't mean writing everything twice"
    A successful write followed by a metadata failure should not silently duplicate the same publication on retry.

    **How it works:** [`orchestrate_write()`](../api/reference/orchestrate_write.md) delegates to internal `pipeline_write()` and `PublicationBatch`. FabricOps checks the batch identity, saved receipt and physical target before recovering. Lakehouse verification uses Delta commit evidence; Warehouse verification checks the exact publication audit-marker row count. Unverifiable or partial writes fail closed.

    **Where to look:** [`METADATA_PROCESSING_STATE`](../reference/metadata/metadata_processing_state.md) records `record_type = publication_receipt`, `publication_id`, `publication_batch_id`, `publication_activity_id`, `publication_input_rows`, `target_table_id` and `status`. Implementation: `src/fabricops_kit/pipeline/shared.py`.

    **Trade-off:** Fingerprinting and physical verification cost compute. Recovery requires evidence, not a best-effort guess.

??? info "Incremental runs don't lose track of unfinished work"
    Reading a record does not mean it has reached the destination, and records arriving during a run should not shift the current processing boundary.

    **How it works:** [`pipeline_read()`](../api/reference/pipeline_read.md), called by `orchestrate_read()`, resolves the accepted source-to-target watermark and captures an upper bound for the current read. Lakehouse filtering uses Spark; Warehouse filtering uses FabricOps-owned SQL. Internal `pipeline_write()` commits progress only after verified publication. First-time incremental reads bootstrap from the source, subject to target safety checks.

    **Where to look:** [`METADATA_PROCESSING_STATE`](../reference/metadata/metadata_processing_state.md) records `record_type = source_observation` or `incremental_checkpoint`, `source_table_id`, `target_table_id`, `watermark_type`, `min_change_value`, `max_change_value`, `status` and `accepted_at`.

    **Trade-off:** Each source-to-target pair needs its own checkpoint; later arrivals wait for another run. Correctness depends on a reliable source change value.

??? info "Different kinds of changes need different write behaviour"
    An event log may need every record, while another target should ignore repeated rows or maintain the latest state of each business key.

    **How it works:** [`orchestrate_read()`](../api/reference/orchestrate_read.md) selects Full or Incremental independently of [`orchestrate_write()`](../api/reference/orchestrate_write.md). Internal `pipeline_write()` supports Overwrite, Append All, Append New Only, SCD1 and SCD2. `add_row_hash()` and `row_hash_expression()` calculate a mandatory SHA256 `_row_hash` after transformation and Sensitive Data treatment. `append_new_only` uses `filter_unpublished_rows()` to remove repeated incoming hashes and anti-join target hashes; SCD strategies use business keys. A separate `PublicationBatch` fingerprint supports retry recovery.

    **Where to look:** The **published target table** stores `_row_hash`; [`METADATA_PROCESSING_STATE`](../reference/metadata/metadata_processing_state.md) stores `publication_batch_id`, `publication_input_rows` and `publication_strategy`. See [Read & Write Modes](../reference/read-and-load-strategies.md) for the exact strategy rules.

    **Trade-off:** Hashing and target comparison add compute. Append New Only does not update or delete existing rows, and changed ingestion values can change the hash. Existing targets with missing or invalid hashes require reviewed migration or overwrite.

??? info "We can see beyond the rows processed today"
    An incremental batch might look healthy even when records elsewhere in the full source have changed or disappeared.

    **How it works:** [`setup_pipeline()`](../api/reference/setup_pipeline.md) configures `observe_source` and `source_observation_days`. Internal `observe_full_source()` can fingerprint the complete physical source independently of the incremental read; `orchestrate_read()` exposes `full_source_observation`. The baseline is accepted after verified publication. Separately, `orchestrate_read()` and `orchestrate_write()` schedule whole-table profiling for row counts, missing values and common values.

    **Where to look:** [`METADATA_PROCESSING_STATE`](../reference/metadata/metadata_processing_state.md) records `record_type = full_source_baseline`, `source_table_id`, `row_count`, `content_fingerprint`, `publication_id` and `accepted_at`. [`METADATA_DATA_PROFILED`](../reference/metadata/metadata_data_profiled.md) records `profile_snapshot_id`, `table_id`, `column_id`, `row_count` and `non_null_count`; [`METADATA_DATA_PROFILED_FREQUENCY`](../reference/metadata/metadata_data_profiled_frequency.md) records `frequency_id`, `column_id` and `value`.

    **Trade-off:** Full-source observation and profiling both scan beyond the incremental batch, so they are scheduled. A changed source fingerprint provides evidence, not automatic deletion or a publication block.

??? info "Unsafe changes are stopped rather than guessed through"
    A failed rule, inconsistent target or competing writer should not silently produce an unreliable result.

    **How it works:** `orchestrate_read()` and `orchestrate_write()` apply relevant schema, grain, Data Quality, freshness and Sensitive Data checks. Internal `pipeline_write()` validates checkpoints, existing target hashes and publication ownership. A target lease in the Serializable Pipeline Registry prevents competing **managed** writers from publishing concurrently; `finalize_pipeline()` releases it. Governed deployment verification currently fails closed pending trusted verification.

    **Where to look:** [`METADATA_GUARDRAIL_RESULTS`](../reference/metadata/metadata_guardrail_results.md) stores `guardrail_type`, `status`, `can_continue`, `reason` and `result_payload_json`. [`METADATA_PIPELINE_REGISTRY`](../reference/metadata/metadata_pipeline_registry.md) stores managed lease state in `leases_json`; [`METADATA_PROCESSING_STATE`](../reference/metadata/metadata_processing_state.md) holds checkpoints and publication receipts.

    **Trade-off:** Extra validation and exclusive leases require coordination. Interrupted leases or inconsistent targets can need manual reconciliation; external writers are not protected by FabricOps leases.

??? info "Every completed run has an explanation"
    Engineers need to know which tables participated, what happened and whether the entire notebook finished, not just whether one write succeeded.

    **How it works:** [`setup_pipeline()`](../api/reference/setup_pipeline.md) starts the session; the orchestrators collect operation results and timings; [`finalize_pipeline()`](../api/reference/finalize_pipeline.md) persists the run outcome in persistent modes. Dry Run keeps results in memory. Multiple target writes remain independent rather than one atomic transaction.

    **Where to look:** [`METADATA_PIPELINE_RUN`](../reference/metadata/metadata_pipeline_run.md) stores `run_id`, `pipeline_id`, `execution_mode`, `status`, `operations`, `boundary_completed` and `completed_at`. [`METADATA_DATA_LINEAGE`](../reference/metadata/metadata_data_lineage.md) stores `lineage_id`, `table_id`, `pipeline_role` and `workspace_id`.

    **Trade-off:** Explicit finalization is required. A successful individual publication does not mean the entire pipeline completed.

## Get started

See [Guided Demo Step 2: Build and run the ETL](../guided-demo/02-build-and-run-etl.md) for an Orders + Products → Curated Orders example using the standard pipeline template.

## Go deeper

For the wider lifecycle, see [How FabricOps Works](../how-fabricops-works.md). For implementation details, use [PySpark Transformation](../reference/pyspark-transformation.md) and the [Function Reference](../reference/index.md).
