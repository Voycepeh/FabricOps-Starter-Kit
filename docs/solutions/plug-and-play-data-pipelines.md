# Plug-and-Play Data Pipelines with Data Contract Enforcement

![Development to Production pipeline promotion](../assets/05/PipelinesDeploymentOverview.png)

## The problem

Building a governed data pipeline involves much more than reading a table, transforming a DataFrame, and writing the result. Engineers also need to handle environment resolution, incremental processing, load strategies, metadata, profiling, Data Contracts, Guardrails, validation, lineage, and the differences between Fabric Lakehouses and Warehouses.

A new engineer should not need to understand or rebuild all of that governance and engineering plumbing before they can create a reliable pipeline. At the same time, the framework should not hide so much that nobody can understand what the pipeline is doing.

FabricOps abstracts the repeatable plumbing behind a small, readable notebook interface: **choose how each source is read, write the project transformation in normal PySpark, choose how each target is written, and let FabricOps apply the governed lifecycle around it.**

## The solution

FabricOps provides a **clonable two-notebook engineering stack**:

- [`00_env_config.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb) resolves the logical Fabric stores to the physical resources for the current Development or Production environment.
- [`02_pipeline.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb) is the pipeline you promote unchanged between environments. It provides two plug-and-play governed ETL boundaries: [`orchestrate_read()`](../api/reference/orchestrate_read.md) and [`orchestrate_write()`](../api/reference/orchestrate_write.md).

Everything project-specific stays visible between those boundaries as ordinary PySpark transformation code.

## The big picture

```mermaid
flowchart LR
    subgraph DEV["Development — clonable notebook stack"]
        direction TB
        DEV_ENV["00 Env Config<br/>resolves Development resources"]
        subgraph DEV_PIPE["02 Pipeline"]
            direction TB
            DEV_CONTRACT["Select Data Contract context"]
            DEV_READ["orchestrate_read() × N<br/>Full / Incremental"]
            DEV_TRANSFORM["Project-specific<br/>PySpark transformation"]
            DEV_WRITE["orchestrate_write() × N<br/>Overwrite / Append / SCD1 / SCD2"]
            DEV_CONTRACT --> DEV_READ --> DEV_TRANSFORM --> DEV_WRITE
        end
        DEV_ENV --> DEV_PIPE
        DEV_PIPE --> DEV_RES["Development resources"]
    end

    subgraph PROD["Production — same notebook stack"]
        direction TB
        PROD_ENV["00 Env Config<br/>resolves Production resources"]
        subgraph PROD_PIPE["02 Pipeline"]
            direction TB
            PROD_CONTRACT["Select Data Contract context"]
            PROD_READ["orchestrate_read() × N<br/>Full / Incremental"]
            PROD_TRANSFORM["Project-specific<br/>PySpark transformation"]
            PROD_WRITE["orchestrate_write() × N<br/>Overwrite / Append / SCD1 / SCD2"]
            PROD_CONTRACT --> PROD_READ --> PROD_TRANSFORM --> PROD_WRITE
        end
        PROD_ENV --> PROD_PIPE
        PROD_PIPE --> PROD_RES["Production resources"]
    end

    DEV ==>|"Promote 1:1"| PROD
```

The same notebook stack exists in Development and Production. `00_env_config` resolves the stack to the resources for its environment, while `02_pipeline` is promoted unchanged from Development to Production. Inside each pipeline, Data Contract context is selected before the governed ETL flow. A pipeline can use multiple `orchestrate_read()` calls, each choosing Full or Incremental, transform the resulting DataFrames with normal project-specific PySpark, and use multiple `orchestrate_write()` calls, each independently choosing Overwrite, Append, SCD1, or SCD2.

## Read recipes

Each source has its **own** `orchestrate_read()` call. Read strategy is therefore a per-table decision, not a setting for the whole pipeline.

A pipeline can, for example, incrementally read a high-volume Orders table while fully reading a smaller Products reference table:

```python
orders = orchestrate_read(
    name="orders",
    store="Bronze",
    schema="demo",
    table_name="orders",
    read_mode="incremental",
    target_table_id=target_table_id,
    spark_session=spark,
)

products = orchestrate_read(
    name="products",
    store="Bronze",
    schema="demo",
    table_name="products",
    read_mode="full",
    spark_session=spark,
)
```

The same governed boundary resolves the environment-aware source and runs the standard FabricOps Read lifecycle. The lower-level read, freshness, schema, data-quality, profiling, and routing capabilities remain behind the orchestrator. Advanced users can still compose those public capabilities directly when they genuinely need a custom lifecycle.

## Transform in the notebook

FabricOps deliberately does not hide project business logic behind a framework DSL. Once the sources return PySpark DataFrames, the middle of `02_pipeline` belongs to the project.

```python
orders_df = orders["dataframe"]
products_df = products["dataframe"]

transformed_df = (
    orders_df
    .join(products_df, "product_id")
    # project-specific filters, derivations, joins, aggregations...
)
```

This is also the natural place to use Microsoft Fabric Copilot or another coding assistant. FabricOps standardizes the governed boundaries while the transformation remains normal PySpark.

## Write recipes

Each target independently chooses its publication strategy through `orchestrate_write()`. The same canonical `02_pipeline` can therefore express the supported patterns without requiring a different notebook template for each one.

| Recipe | Orchestrator choice | Typical intent |
| --- | --- | --- |
| Replace target | `load_strategy="overwrite"` | Publish the complete target state |
| Add new rows | `load_strategy="append"` | Append a new batch |
| Merge current state | `load_strategy="scd1"` | Update matching business keys and insert new rows |
| Preserve history | `load_strategy="scd2"` | Maintain historical versions as records change |

For example:

```python
write_result = orchestrate_write(
    transformed_df,
    name="curated_orders",
    sources=[orders, products],
    store="Silver",
    schema="demo",
    table_name="curated_orders",
    load_strategy="scd1",
    contracts=CONTRACTS,
    spark_session=spark,
)
```

Read and Write choices are independent. One pipeline may mix full and incremental sources, then publish multiple targets using different supported write strategies.

## Data Contract enforcement is wired into the same pipeline

The canonical `02_pipeline` selects Data Contract context before the ETL blocks. Contract mode is resolved **per table**, so different governed tables in the same notebook can be at different lifecycle stages.

```mermaid
flowchart LR
    SELECT["Select Data Contract<br/>context per table"] --> READ["orchestrate_read()"]
    READ --> TRANSFORM["Project transformation"]
    TRANSFORM --> WRITE["orchestrate_write()"]
    WRITE --> MODE{"Contract mode"}
    MODE -->|Validate| VALIDATE["Run guardrails<br/>do not publish"]
    MODE -->|Enforce / Active| PUBLISH["Run guardrails<br/>publish and profile"]
```

Before an applicable Data Contract exists, the same standard notebook can bootstrap normally and contract-backed checks that do not apply are visibly skipped. Once a frozen contract is selected for validation, the same pre-publication guardrails run but the target is not published. Once the approved contract is activated for enforcement, the same notebook and orchestrators enforce it and continue through publication.

The important point is that governance is not a second pipeline implementation. **The Data Contract is wired into the same Read → Transform → Write workflow that Engineering already promotes.**

## Promotion

`00_env_config` owns the environment-specific resolution. `02_pipeline` owns the pipeline definition.

That separation means Engineering promotes the same `02_pipeline` from Development to Production while `00_env_config` resolves logical stores such as Bronze, Silver, Gold, and Metadata to the correct physical Fabric resources for that environment.

```mermaid
flowchart LR
    DEVENV["00 Env Config<br/>DEV"] --> PIPE["02 Pipeline"]
    PIPE --> DEV["Development resources"]
    PRODENV["00 Env Config<br/>PROD"] --> SAME["Same 02 Pipeline"]
    SAME --> PROD["Production resources"]
```

## Why one canonical pipeline template

FabricOps does not need a separate notebook architecture for full refresh, incremental append, SCD1, SCD2, or combinations of them. Those are **recipes expressed through the orchestrators**.

The stable model is:

```text
00 Env Config
      ↓
02 Pipeline
  select Data Contract context
      ↓
  orchestrate_read(...)   ← one per source; full or incremental
      ↓
  project PySpark transformation
      ↓
  orchestrate_write(...)  ← one per target; overwrite / append / SCD1 / SCD2
```

This keeps the template easy to clone, the transformation easy to understand, promotion environment-aware, and the governed runtime behavior centralized in FabricOps rather than copied into every project notebook.

## Go deeper

Follow the [Guided Demo](../guided-demo.md) to build the pipeline step by step. Use the [Function Reference](../reference/index.md) when you need the lower-level capabilities behind the orchestrators.
