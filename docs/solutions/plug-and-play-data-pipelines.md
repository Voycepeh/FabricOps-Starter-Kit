# Plug-and-Play Data Pipelines with Data Contract Enforcement

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

![Development to Production pipeline promotion](../assets/05/PipelinesDeploymentOverview.png){ .fabricops-solution-hero }

## The problem

Building a governed data pipeline involves much more than reading a table, transforming a DataFrame, and writing the result. Engineers also need to handle environment resolution, incremental processing, load strategies, metadata, profiling, Data Contracts, Guardrails, validation, lineage, and the differences between Fabric Lakehouses and Warehouses.

A new engineer should not need to understand or rebuild all of that governance and engineering plumbing before they can create a reliable pipeline. At the same time, the framework should not hide so much that nobody can understand what the pipeline is doing.

FabricOps abstracts the repeatable plumbing behind a small, readable notebook interface: **set up the pipeline, choose how each source is read, write the project transformation in normal PySpark, choose how each target is written, then finalize the run, and let FabricOps apply the governed lifecycle around it.**

## The solution

<div class="fabricops-mascot-callout">
  <span style="display:inline-flex;align-items:center;gap:0.4rem;flex-shrink:0">
    <img src="/FabricOps-Starter-Kit/assets/mascots/robot-dev.png" alt="Development mascot" loading="eager">
    <img src="/FabricOps-Starter-Kit/assets/mascots/robot-prod.png" alt="Production mascot" loading="eager">
  </span>
  <div><p>FabricOps provides a <strong>clonable two-notebook engineering stack</strong>:</p></div>
</div>

- [`00_env_config.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb) maps logical Fabric Stores to the correct environment-specific Fabric locations.
- [`02_pipeline.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb) keeps the pipeline definition portable between environments, with governed Read and Write boundaries around ordinary project-owned PySpark.

The result is a pipeline pattern that engineers can clone and adapt without rebuilding the governance and engineering plumbing each time.

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

The picture has four important parts working together:

1. **Environment-aware configuration.** Each environment has its own `00_env_config`, which resolves the logical Fabric Stores to the correct Development or Production locations.
2. **A portable pipeline.** `02_pipeline` keeps the same governed shape: **Setup → Read → project-owned PySpark → Write → Finalize**. The engineer changes the project logic, not the surrounding operating pattern.
3. **Executable governance.** Governance defines the Data Contract and Guardrails. Engineering selects and validates that contract in Development; after approval, Production resolves the approved whole-pipeline manifest and enforces it through the same pipeline boundaries.
4. **A shared evidence layer.** Reads and writes continuously produce the Catalogue, profiles, processing state, Guardrail results, and lineage that connect the physical pipeline back to Governance.

Once the Development implementation and Data Contract agree, the validated `02_pipeline` is promoted unchanged. Production uses its own environment configuration and the active contract, so the same engineering definition runs against Production Fabric Stores without embedding environment-specific locations in the pipeline.

This is the core FabricOps pipeline model: **the engineer owns the transformation; Governance owns the governed definition; FabricOps makes the surrounding lifecycle repeatable and executable across environments.**

## How it works

| Responsibility | What happens |
| --- | --- |
| **Engineer configures** | Chooses logical sources and targets, Read and Write modes, the project-specific PySpark transformation, and the Data Contract context for governed tables. |
| **AI can support** | Microsoft Fabric Copilot or another coding agent can help write or refactor project-specific PySpark. AI is optional and is not part of pipeline execution or enforcement. |
| **FabricOps handles deterministically** | Resolves environment-specific Fabric locations, runs governed Read and Write orchestration, applies the selected Data Contract and Guardrails, and records metadata, profiling, lineage, processing state and the complete run outcome. |

## Under the hood

<div class="fabricops-mascot-callout">
  <img src="/FabricOps-Starter-Kit/assets/mascots/robot-coding.png" alt="Coding mascot" loading="lazy">
  <div><p>Trace setup, governed Read and Write boundaries around your PySpark transformation, and finalization of the complete run.</p></div>
</div>

??? info "What happens in a standard FabricOps Pipeline"

    [![Setup, governed Read and Write around project PySpark, then finalization](../assets/pipeline-boundaries-implementation.svg){ .fabricops-solution-diagram }](../assets/pipeline-boundaries-implementation.svg)

    Open the SVG at full size to follow the implementation links.

    ### Setup Pipeline

    **Call `setup_pipeline()` once after Environment Configuration.** It resolves the current environment and central Governance authority, selects the applicable Data Contracts and initializes `METADATA_PIPELINE_RUN`. Interactive Testing offers exact frozen versions or No Contract for all participants; Live resolves the approved environment revision.

    ### Read side

    **`orchestrate_read()` checks the source before returning its DataFrame to your PySpark transformation.**

    1. Resolve the table and its Data Contract, then read the requested rows.
    2. Run the configured Freshness, Schema, Grain, and Data Quality checks.
    3. On a Full read, profile the returned dataset. Incremental batches skip Profile.

    The Grain check covers the returned rows: the full read result or the incremental batch. It does not compare an incremental batch with historical rows.

    ### Write side

    **`orchestrate_write()` checks the prepared input before publishing the target.**

    1. Run configured Schema and Sensitive Data checks, then Source Drift checks for participating sources.
    2. Check Grain and Data Quality after Sensitive Data treatment, enforcing the selected Data Contract policies before publication.
    3. In Live mode, publish through the selected Write strategy, record lineage in `METADATA_DATA_LINEAGE`, and profile the complete persisted target.

    Evaluation-only Testing runs checks and profiles prepared input without business publication; run records and Guardrail diagnostics still persist centrally. Explicit `testing_writes=True` can publish to reviewed safe destinations protected from Live ownership. Explicit `finalize_pipeline()` records complete-run status after all declared operations. The Grain check covers prepared input; it does not guarantee resulting-table uniqueness for Append or SCD strategies.

    ### Finalize Pipeline

    **Call `finalize_pipeline(plan)` once after every declared operation and project transformation.** It consolidates recorded outcomes and exact contract versions, persists the final `METADATA_PIPELINE_RUN` snapshot and releases existing execution reservations. It does not count business DataFrames. Stopped runs remain incomplete; use `failed=True` for a caught project error. Repeated finalization returns the same result. Optional Read/Write inspection stays available afterwards.

    Engineering and Microsoft Fabric own executable integrity, source control, CI/CD and deployment. FabricOps requires no packaging or deployment verification call.

    ### Both sides

    - **Contract enforcement:** Both Live and Testing persist `METADATA_GUARDRAIL_RESULTS` and retain diagnostics for inspection. Discovering possible keys is separate from enforcing the contract's selected Grain key.
    - **Profiling:** when the lifecycle reaches Profile, `profile_table()` calculates statistics and can also calculate frequency distributions and discover candidate Grain keys.
    - **Caller controls:** Read and Write accept the same profiling switches and discovery limits. Your notebook or external scheduler chooses when to enable them; FabricOps does not apply a discovery schedule.

??? info "How frequency profiling and Grain discovery work"

    ### Frequency distributions

    **Frequency answers “which values occur most often in this column?”** FabricOps groups values, counts occurrences, and ranks them. Null can appear as a frequency value.

    Automatic selection uses eligible scalar columns and skips columns whose distinct-per-non-null percentage exceeds 80% by default. `frequency_top_n=5` retains the five highest-ranked values per selected column; `None` retains all. Top N limits retained output, but exact frequencies still require grouped counts across the input data.

    Statistics are saved in `METADATA_DATA_PROFILED`; frequency rows are saved in `METADATA_DATA_PROFILED_FREQUENCY` and linked to the profile snapshot. Turning frequency off skips its calculations for that call. Existing snapshots from earlier activities remain available.

    ### Grain key discovery

    **Discovery answers “which column or combination uniquely identifies every row in this dataset?”** It uses exact data checks, without AI or column-name guesses.

    1. Check eligible scalar columns for nulls and exact distinct counts. If single-column keys exist, return those candidates.
    2. Otherwise test combinations of null-free columns, starting with pairs and widening up to `grain_discovery_max_columns`.
    3. Stop at the smallest width with valid keys, retaining up to `grain_discovery_max_candidates` suggestions.

    Candidates are stored in the table row's `METADATA_DATA_CATALOGUE.profile_key_candidates_json` for contract authoring. Governance reviews and chooses the intended Grain key. A unique combination in today's data is a candidate for that decision, not a guarantee about future data.

    ### Where the compute runs

    **The orchestrators invoke profiling; the data engine performs the calculations.** Supplied DataFrames and physical Lakehouse tables use PySpark. Complete physical Warehouse tables use SQL pushdown, including frequency and key-discovery queries.

    Each composite-key test performs an exact distinct-count operation. With 20 eligible null-free columns and no single-column key, a search through triples can require 190 pair checks and 1,140 triple checks. Large inputs can add scans and shuffles; deterministic discovery can still be expensive. The candidate limit helps when keys are found but does not cap the search when none qualify.

    ### Choose when to run each calculation

    Both orchestrators and `profile_table()` accept these controls:

    ```python
    source = orchestrate_read(
        execution_plan=plan,
        store="Bronze", schema="demo", table_name="orders",
        grain_discovery_enabled=True,
        grain_discovery_max_columns=3,
        grain_discovery_max_candidates=8,
        frequency_enabled=True,
        frequency_top_n=5,
    )
    ```

    - **First run or meaningful data changes:** enable discovery to refresh candidate keys. A maximum of `1` checks singles only; `2` also checks pairs.
    - **Routine runs:** set `grain_discovery_enabled=False` to skip discovery and preserve saved candidates. Independently set `frequency_enabled=False` to skip frequency calculations.
    - **After the Data Contract is defined:** discovery can stay off until you choose to revisit the key. Configured Grain checks still validate the contract's key on each applicable Read or Write call.

    These switches leave statistical profiling enabled whenever the lifecycle runs Profile. Incremental Read skips Profile. Testing Write profiles its prepared input without persistence. Scheduling belongs to the caller.

    See [`profile_table()`](../api/reference/profile_table.md) for exact parameters, direct column selection, and persistence behavior.

## Example

??? info "Orders + Products → Curated Orders"

    A project can read an Orders source and a Products reference table through governed Read boundaries, join and transform them using ordinary PySpark, then publish a Curated Orders table through a governed Write boundary.

    The engineer owns the transformation. FabricOps handles the repeatable environment, governance, metadata, and enforcement plumbing around it.

    See [Guided Demo Step 2: Build and run the ETL](../guided-demo/02-build-and-run-etl.md) for the working pipeline example.

## Go deeper

Use [How FabricOps Works](../how-fabricops-works.md) for the wider Governance and Engineering lifecycle.

For implementation details:

- [Read & Write Modes](../reference/read-and-load-strategies.md) — Full and Incremental reads, Overwrite, Append, SCD1, SCD2, and processing semantics.
- [PySpark Transformation](../reference/pyspark-transformation.md) — project-owned transformation patterns and performance guidance.
- [Guided Demo Step 2](../guided-demo/02-build-and-run-etl.md) — build and run the canonical pipeline.
- [Guided Demo Step 4](../guided-demo/04-validate-frozen-data-contract.md) — validate the frozen Data Contract against the pipeline.
- [Guided Demo Step 5](../guided-demo/05-activate-data-contract-and-promote.md) — activate the whole pipeline and promote the pipeline to Production.
- [`orchestrate_read()`](../api/reference/orchestrate_read.md) and [`orchestrate_write()`](../api/reference/orchestrate_write.md) — lifecycle stages and per-call profiling controls.
- [`profile_table()`](../api/reference/profile_table.md) — statistical profiling, frequency distributions, and Grain discovery limits.
- [Function Reference](../reference/index.md) — lower-level FabricOps APIs and orchestrators.
