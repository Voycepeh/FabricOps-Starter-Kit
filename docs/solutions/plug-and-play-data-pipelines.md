# Plug-and-Play Data Pipelines with Data Contract Enforcement

<span class="fabricops-release-status fabricops-release-status--preview">Preview</span>

![Development to Production pipeline promotion](../assets/05/PipelinesDeploymentOverview.png)

## The problem

Building a governed data pipeline involves much more than reading a table, transforming a DataFrame, and writing the result. Engineers also need to handle environment resolution, incremental processing, load strategies, metadata, profiling, Data Contracts, Guardrails, validation, lineage, and the differences between Fabric Lakehouses and Warehouses.

A new engineer should not need to understand or rebuild all of that governance and engineering plumbing before they can create a reliable pipeline. At the same time, the framework should not hide so much that nobody can understand what the pipeline is doing.

FabricOps abstracts the repeatable plumbing behind a small, readable notebook interface: **choose how each source is read, write the project transformation in normal PySpark, choose how each target is written, and let FabricOps apply the governed lifecycle around it.**

## The solution

FabricOps provides a **clonable two-notebook engineering stack**:

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
            DEV_CONTRACT["Select Data Contract context"]
            DEV_READ["orchestrate_read() × N<br/>Full / Incremental"]
            DEV_TRANSFORM["Project-specific<br/>PySpark transformation"]
            DEV_WRITE["orchestrate_write() × N<br/>Overwrite / Append / SCD1 / SCD2"]
            DEV_CONTRACT --> DEV_READ --> DEV_TRANSFORM --> DEV_WRITE
        end
        DEV_ENV --> DEV_PIPE
        DEV_PIPE --> DEV_RES["Development<br/>Fabric Store locations"]
    end

    subgraph PROD["Production — same notebook stack"]
        direction TB
        PROD_ENV["00 Env Config<br/>resolves Production<br/>Fabric Store locations"]
        subgraph PROD_PIPE["02 Pipeline"]
            direction TB
            PROD_CONTRACT["Select Data Contract context"]
            PROD_READ["orchestrate_read() × N<br/>Full / Incremental"]
            PROD_TRANSFORM["Project-specific<br/>PySpark transformation"]
            PROD_WRITE["orchestrate_write() × N<br/>Overwrite / Append / SCD1 / SCD2"]
            PROD_CONTRACT --> PROD_READ --> PROD_TRANSFORM --> PROD_WRITE
        end
        PROD_ENV --> PROD_PIPE
        PROD_PIPE --> PROD_RES["Production<br/>Fabric Store locations"]
    end

    DEV ==>|"Promote 1:1"| PROD
```

The picture has four important parts working together:

1. **Environment-aware configuration.** Each environment has its own `00_env_config`, which resolves the logical Fabric Stores to the correct Development or Production locations.
2. **A portable pipeline.** `02_pipeline` keeps the same governed shape: **Read → project-owned PySpark → Write**. The engineer changes the project logic, not the surrounding operating pattern.
3. **Executable governance.** Governance defines the Data Contract and Guardrails. Engineering selects and validates that contract in Development; after approval, Production resolves the active contract and enforces it through the same pipeline boundaries.
4. **A shared evidence layer.** Reads and writes continuously produce the Catalogue, profiles, processing state, Guardrail results, and lineage that connect the physical pipeline back to Governance.

Once the Development implementation and Data Contract agree, the validated `02_pipeline` is promoted unchanged. Production uses its own environment configuration and the active contract, so the same engineering definition runs against Production Fabric Stores without embedding environment-specific locations in the pipeline.

This is the core FabricOps pipeline model: **the engineer owns the transformation; Governance owns the governed definition; FabricOps makes the surrounding lifecycle repeatable and executable across environments.**

## How it works

### What the engineer configures

- The logical sources and targets used by the pipeline.
- How each source is read and each target is written.
- The project-specific PySpark transformation.
- The Data Contract context for governed tables.

### What AI can support

AI is optional. Microsoft Fabric Copilot or another coding agent can help write or refactor the project-specific PySpark, but AI is not part of pipeline execution or enforcement.

### What FabricOps handles deterministically

- Resolving environment-specific Fabric locations.
- Running governed Read and Write orchestration.
- Applying the selected Data Contract and executable Guardrails.
- Capturing the metadata, profiling, lineage, and processing state needed by the governed lifecycle.

## Under the hood

FabricOps deliberately leaves project logic visible while standardising the boundaries around it.

```mermaid
flowchart LR
    ENV["00 Env Config"] --> READ["Governed Read"]
    READ --> TRANSFORM["Your PySpark"]
    TRANSFORM --> WRITE["Governed Write"]

    CONTRACT["Data Contract"] --> READ
    CONTRACT --> WRITE

    READ --> META["Metadata + Profile + State"]
    WRITE --> META
    WRITE --> LINEAGE["Lineage"]
```

The orchestrators provide the stable framework boundary. Lower-level implementation details such as Full versus Incremental reads, load strategies, validation behaviour, and deployment are documented separately so this page can stay focused on the overall solution.

## Example

??? example "Orders + Products → Curated Orders"

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
- [Guided Demo Step 5](../guided-demo/05-activate-data-contract-and-promote.md) — activate the contract and promote the pipeline to Production.
- [Function Reference](../reference/index.md) — lower-level FabricOps APIs and orchestrators.
