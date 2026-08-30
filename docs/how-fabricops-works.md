# How FabricOps works

<style>
.md-typeset .fabricops-section-block {
  margin: 1.25rem 0;
  padding: 1.1rem 1.2rem;
  border: 1px solid var(--md-default-fg-color--lightest);
  border-radius: 0.4rem;
  background-color: var(--md-default-bg-color);
  box-shadow: 0 0.12rem 0.45rem rgba(0, 0, 0, 0.04);
}

.md-typeset .fabricops-section-block > :first-child {
  margin-top: 0;
}

.md-typeset .fabricops-section-block > :last-child {
  margin-bottom: 0;
}
</style>

<div class="fabricops-section-block" markdown>

**FabricOps connects Governance, Engineering Development, Engineering Production, and project-specific consumer workspaces through one governed workflow.**

![FabricOps operating model overview](assets/fabricops-operating-model-overview.png)

</div>

<div class="fabricops-section-block" markdown>

## Four ideas to know before you start

**FabricOps Starter Kit**, **Metadata**, **Governance as Code**, and **Configuration-driven Engineering** are the four high-level ideas used throughout the workflow.

Hover over a glossary term for its canonical short definition. Use the [FabricOps Glossary](glossary.md) for the full definition, category, aliases, and Microsoft Learn source where applicable. The glossary is the terminology source of truth for this repository.

### Where the key terms enter the workflow

| Term | Role in the FabricOps workflow |
| ---- | ------------------------------ |
| Data Steward | Provides the accountable provider or recipient role used by a Data Agreement. |
| Data Agreement | Establishes the governed sharing relationship between one provider Data Steward and one recipient Data Steward. |
| Profile | Records observed characteristics of a dataset at a point in time. |
| Enrichment | Adds business and governance meaning to the Data Catalogue. |
| Guardrails | Express the governed rules FabricOps evaluates for a table or column. |
| Enforcement | Applies active Guardrails during execution and acts on the outcome. |
| Guardrail Result | Records what happened when a Guardrail was evaluated. |
| Data Contract | Freezes the governed expectations for one `table_id` under one exact Data Agreement version. |
| Configuration | Controls environment targets and pipeline behaviour without rewriting implementation code. |
| Data Quality | Defines whether data is fit for its intended use and meets the quality expectations that apply. |

</div>

<div class="fabricops-section-block" markdown>

## Workspace model

| Workspace | Primary Purpose | Main Fabric Stores |
| --------- | --------------- | ------------------ |
| Governance | Manage Data Stewards, Data Agreements, Data Contracts, Catalogue Enrichment, and Guardrails | Development and Production metadata Lakehouses |
| Engineering Development | Explore data and develop, profile, test, and review repeatable pipelines | Configured Development data layers using Lakehouses, Warehouses, or both |
| Engineering Production | Run governed and stable Production pipelines on the required operational schedule | Configured Production data layers using Lakehouses, Warehouses, or both |
| Project-Specific Consumer | Support project-level exploration, AI, and BI consumption without duplicating the Production engineering workflow | Consumes governed data from the Engineering Production workspace |

??? info "Read more about the workspace model"

    **Core workspaces**

    Governance, Engineering Development, and Engineering Production establish the shared governance and engineering workflow used to create, validate, govern, and operate data pipelines.

    **Project-Specific Consumer workspaces**

    Teams may create multiple project-specific consumer workspaces for exploration, AI, and BI consumption. Each workspace uses `99_explore` to read governed data directly from Engineering Production for its own project work.

    **Trusted Production source**

    Consumer workspaces do not reproduce the Production pipeline or maintain their own Production copies of the governed data layers. Engineering Production remains the trusted Production source.

### Data layers and Medallion Architecture

FabricOps adopts the Microsoft Fabric **Medallion Architecture** principle of progressively refining data from raw to validated and enriched to curated consumption-ready forms.

Microsoft describes the familiar layers as **Bronze → Silver → Gold**. FabricOps does not require those literal store names. The `00_env_config` notebook defines the logical stores available to a project, so teams can use `bronze` / `silver` / `gold`, keep the starter example names `source` / `unified` / `product`, or introduce additional organisation-specific layers where the architecture needs them.

The starter configuration maps approximately like this:

| Starter example | Medallion role | Typical intent |
| --- | --- | --- |
| `source` | Bronze | Land source-oriented or raw data. |
| `unified` | Silver | Standardize, validate, integrate, or enrich data. |
| `product` | Gold | Publish curated data for downstream analytics, AI, and BI. |
| `metadata` | Not a Medallion layer | Store FabricOps governance and engineering metadata. |

This mapping is an example, not a fixed FabricOps contract. `REQUIRED_TARGETS` and `ENV_PATHS` in `00_env_config` define the store keys the project uses, while `FabricStore` records the actual Fabric item behind each key.

</div>

<div class="fabricops-section-block" markdown>

## The governance and engineering loop workflow

**FabricOps uses a loop between Governance and Engineering Development to validate a pipeline before it runs in Engineering Production.**

![FabricOps role workflow](assets/fabricops-role-workflow.png)

Read the [Guided Demo](guided-demo.md) to execute the workflow. Download the notebooks from [Notebook Templates](notebook-templates.md).

??? info "Read the workflow step by step"

    **0. Set up the operating environment**

    Create the Fabric workspaces, configure `00_env_config` in each workspace, and create the Governance metadata tables.

    **1. Governance: Create Data Stewards and a Data Agreement**

    In `01_governance`, create the provider and recipient Data Stewards and establish the Data Agreement between them.

    **2. Engineering: ETL, profile data, and build the Data Catalogue**

    In Engineering Development, run `02_pipeline` to perform ETL and write `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY` where applicable, and `METADATA_DATA_LINEAGE` records.

    **3. Governance: Enrich the Data Catalogue and define Guardrails**

    Return to `01_governance` to read `METADATA_DATA_CATALOGUE` and `METADATA_DATA_PROFILED`, write `METADATA_ENRICHMENT`, and author `METADATA_GUARDRAIL` records for the governed table or column.

    **4. Engineering: Validate with current or frozen Guardrails**

    Rerun `02_pipeline` with current authored Guardrails, or with Guardrails from a selected frozen Data Contract. Engineering evaluates the rules and writes `METADATA_GUARDRAIL_RESULTS` plus `METADATA_GUARDRAIL_ROW_RESULTS` where row-level failures are recorded.

    **5. Governance: Freeze a Data Contract and choose the active Production version**

    In `01_governance`, save one immutable Data Contract version for one governed `table_id` under one exact Data Agreement version. Development can test any saved frozen version. Activation chooses the frozen version Production can use.

    **6. Engineering: Run Production against the active Data Contract**

    Run `02_pipeline` in Engineering Production using the active Data Contract. Moving the approved notebook into Engineering Production is handled separately by the organisation's deployment process.

    **7. Consumer: Use Production data directly**

    Use `99_explore` to consume governed Production data directly for analytics, AI, BI, or downstream project use.

</div>

<div class="fabricops-section-block" markdown>

## Development and Production

### Engineering Development

Engineering Development is used for exploration, development, profiling, testing, and review. `02_pipeline` performs ETL and writes `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY` where applicable, and `METADATA_DATA_LINEAGE` records.

Governance reads `METADATA_DATA_CATALOGUE` and `METADATA_DATA_PROFILED`, then writes `METADATA_ENRICHMENT` and `METADATA_GUARDRAIL`. `02_pipeline` reads those Guardrails, evaluates them, and writes `METADATA_GUARDRAIL_RESULTS` plus `METADATA_GUARDRAIL_ROW_RESULTS` where applicable. Development can use current authoring or a selected frozen Data Contract.

Development data and temporary notebooks may be cleaned regularly, so teams should avoid treating the workspace as durable Production storage.

### Data Agreement and Data Contract

A Data Agreement is created between one provider Data Steward and one recipient Data Steward. It establishes the governed sharing relationship, including business purpose, approved usages, validity, supporting documents, and other governance context.

A Data Contract is for one canonical `table_id` under one exact Data Agreement version. Each saved version is immutable. Development can select and test a frozen version before it is active. Activation chooses which frozen version Production can resolve.

### What a Data Contract freezes

`widget_register_data_contract()` builds the contract from the current `METADATA_DATA_AGREEMENT`, `METADATA_DATA_STEWARD`, `METADATA_DATA_CATALOGUE`, `METADATA_ENRICHMENT`, and active `METADATA_GUARDRAIL` records for the selected table.

| Frozen item | What is captured |
| --- | --- |
| Exact Data Agreement version | Agreement identity and version plus its name, domain, business purpose, validity dates, provider and recipient Steward IDs, and approved usages. |
| Provider and recipient Data Stewards | The selected Stewards' IDs, names, roles, and contacts. |
| Governed `table_id` | The canonical table identity used to match the same governed table across Development and Production. |
| Recorded table location | The contract payload records the environment, store type, layer, schema, and table name from `METADATA_DATA_CATALOGUE` when the version is frozen. Production still resolves its own configured physical table and uses the canonical `table_id` to find the active contract. |
| Table structure / schema | The active Catalogue columns with their `column_id`, column name, and data type. |
| Enrichment | Current table- and column-level `METADATA_ENRICHMENT` values, including enrichment level, type, and value. |
| Active Guardrails | Active `METADATA_GUARDRAIL` rules, including the exact Guardrail version, type, rule identity, severity, and rule parameters. |
| Target load strategy | The Catalogue `load_strategy`, such as `overwrite`, `append`, `scd1`, or `scd2`, when configured. |
| Load-strategy parameters | The configured `load_strategy_parameters_json` values required by the selected target strategy. |
| Governed usages | The selected approved-usage subset, which must remain within the parent Data Agreement's approved usages. |

`METADATA_GUARDRAIL_RESULTS`, `METADATA_GUARDRAIL_ROW_RESULTS`, source observations, successful-processing checkpoints, and run/audit fields are not frozen. They record what happened during individual runs.

### Freeze, activate, and promote

| Action | What it means |
| --- | --- |
| **Freeze** | Save an immutable Data Contract version. |
| **Activate** | Choose the frozen version Production is allowed to resolve. |
| **Promote** | Move the approved `02_pipeline` notebook into Engineering Production using the organisation's deployment process. |

A Data Agreement covers the provider-to-recipient sharing relationship. A Data Contract freezes the approved definition for one table under one exact Data Agreement version.

In Production, `02_pipeline` resolves the active Data Contract for the table and uses its frozen Guardrails, target load strategy, and load-strategy parameters.

### Engineering Production

Engineering Production contains governed, stable, recurring pipelines and durable outputs. In Production, `02_pipeline` uses the active Data Contract for each governed table.

A recurring Production pipeline may run on any required operational schedule, including annually, when the process needs to remain stable and repeatable.

!!! important "Production rule"

    A Production `02_pipeline` should use the active Data Contract for each governed table it reads or writes. Activating a contract does not copy or deploy the notebook.

</div>

<div class="fabricops-section-block" markdown>

## The ETL model inside `02_pipeline`

FabricOps standardizes the boundaries around ETL with a simple operating model:

**0. Environment → E. Extract → T. Transform → L. Load**

!!! abstract "0. Environment"

    Determine Development or Production from `00_env_config`.

    In Development, use current authoring or a selected Data Contract. In Production, use the active Data Contract.

!!! info "E. Extract"

    Define one or more source table IDs. Resolve source Guardrails and Data Contract context, or current Guardrail metadata in Development. Check schema, freshness, and change state.

    Configure the source-read strategy as Full Dataset, Incremental Watermark, or Incremental Partition. FabricOps then resolves the runtime read mode as `skip`, `full_dataset`, or `incremental_subset`.

    Run Data Quality checks on the DataFrame actually being processed. Profile and register only when the DataFrame represents the complete physical table, then write the applicable `METADATA_DATA_PROFILED` and `METADATA_DATA_LINEAGE` records.

??? note "Warehouse sources should normally land in the configured raw/source layer first"

    For large or repeatedly processed Warehouse sources, use the Warehouse primarily as an ingestion boundary. Land the required full or incremental extract into the configured raw/source layer as Delta, then perform profiling, Data Quality checks, transformations, and governed processing from the Lakehouse. This keeps repeated Spark processing in OneLake and avoids using the external Warehouse as the normal processing layer.

!!! abstract "T. Transform"

    Apply user-defined business transformation. Join, derive, aggregate, enrich, and reshape as required. FabricOps governs the inputs and outputs, not the business logic.

!!! success "L. Load"

    Define one governed target table ID. A pipeline may read one or many upstream sources, but the governed `02_pipeline` pattern publishes exactly one target table. If another persisted output is required, create a separate downstream pipeline rather than adding another governed target write to the same pipeline.

    Resolve target Guardrails and governed load strategy from the Data Contract, or Development definition. Check schema and Data Quality, add audit and technical columns, prepare load-strategy execution, write the target table, then read back and profile/register the complete persisted target.

??? note "Full-table profiling"

    Incremental processing may use an Incremental Subset for execution, but a partial DataFrame must not replace the registered Profile of the complete physical table.

??? info "Why FabricOps uses PySpark mainly"

    **PySpark is the standard for repeatable `02_pipeline` workflows.**

    Spark has startup overhead, and pandas may be better suited to smaller one-off analyses. FabricOps uses PySpark because it supports larger datasets and provides a consistent engineering pattern for maintenance and handover.

    This does not prevent teams from using pandas or other tools for appropriate exploration.

</div>

<div class="fabricops-section-block" markdown>

## Metadata stored supporting the workflow

**The Data Catalogue sits at the centre of the FabricOps metadata model.**

![FabricOps metadata model](assets/fabricops-metadata-model.png)

Metadata is the broader information used to describe, understand, manage, and govern the data. The individual FabricOps metadata tables record the specific Governance and Engineering context used by the operating workflow.

??? info "Read how the metadata records connect"

    **Governance records**

    [FabricOps metadata tables](reference/metadata.md) carry Governance information through the workflow. A Data Agreement records the relationship between one provider Data Steward and one recipient Data Steward. A Data Contract then freezes the governed definition for one `table_id` under one exact Data Agreement version.

    **Engineering records**

    `METADATA_DATA_CATALOGUE` identifies each governed table and column and connects `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY`, `METADATA_DATA_LINEAGE`, `METADATA_DATA_ACCESS`, `METADATA_ENRICHMENT`, `METADATA_GUARDRAIL`, and `METADATA_GUARDRAIL_RESULTS` records.

    **Contract relationship**

    A Data Contract is tied to one canonical `table_id`. It freezes the current Catalogue table/column identity and schema, target load strategy and parameters, Enrichment, active Guardrails and their versions, approved usages, and the relevant Data Agreement and Data Stewards. One Data Agreement can support multiple table-level Data Contracts.

    **Data Catalogue and Profiled records stay with Engineering**

    `02_pipeline` writes `METADATA_DATA_CATALOGUE` and `METADATA_DATA_PROFILED`. `01_governance` reads those tables for `METADATA_ENRICHMENT`, `METADATA_GUARDRAIL`, and Data Contract preparation. Governance does not create a second copy of the Engineering-written records.

??? info "How the implemented pieces connect"

    **Engineering and Governance write different metadata tables around the same governed table identity.**

    `02_pipeline` performs ETL and writes `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY` where applicable, and `METADATA_DATA_LINEAGE`.

    `01_governance` reads `METADATA_DATA_CATALOGUE` and `METADATA_DATA_PROFILED`, then writes `METADATA_ENRICHMENT` and `METADATA_GUARDRAIL`. `02_pipeline` evaluates those Guardrails and writes `METADATA_GUARDRAIL_RESULTS` plus `METADATA_GUARDRAIL_ROW_RESULTS` where applicable.

    Governance freezes a Data Contract version for the table. Engineering Development can test that frozen version. Governance can then activate the frozen version Production should use. Moving the validated `02_pipeline` notebook into Engineering Production is handled separately by the organisation's deployment process.

    Downstream users therefore receive more than a table. Where relevant, they can inspect its Data Catalogue, Profiles, Data Lineage, Enrichment, Guardrails, Guardrail Results, Data Agreement, and Data Contract context.

</div>

<div class="fabricops-section-block" markdown>

## Consumer workspaces

Project-specific consumer workspaces provide a separate environment for exploration, AI, and BI consumption. Teams use `99_explore` in their own workspace to read governed data directly from Engineering Production without changing or duplicating the Production pipeline.

There may be multiple consumer workspaces, with each workspace aligned to a specific project, analytical product, or business use case.

??? info "When consumer work should move into the governed pipeline"

    Important `99_explore` work should be preserved when reproducibility is required. Consumer notebooks support analysis and experimentation, but they should not become an alternative Production pipeline.

    Repeatable data preparation that needs to be operationalised should be incorporated into the governed Engineering Development and Engineering Production workflow.

</div>