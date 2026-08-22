# How FabricOps works

**FabricOps connects Governance, Engineering Development, Engineering Production, and project-specific consumer workspaces through one governed workflow.**

![FabricOps operating model overview](assets/fabricops-operating-model-overview.png)

## Workspace model

| Workspace | Primary Purpose | Main Fabric Stores |
| --------- | --------------- | ------------------ |
| Governance | Manage data stewards, data agreements, data contracts, catalogue enrichment, and guardrails | Development and Production metadata lakehouses |
| Engineering Development | Explore data and develop, profile, test, and review repeatable pipelines | Source, unified, and product lakehouses or warehouses |
| Engineering Production | Run approved and stable production pipelines on the required operational schedule | Production source, unified, and product lakehouses or warehouses |
| Project-Specific Consumer | Support project-level exploration, AI, and BI consumption without duplicating the production engineering workflow | Consumes approved data from the Engineering Production workspace |

### Core workspaces

Governance, Engineering Development, and Engineering Production establish the shared governance and engineering workflow used to create, validate, govern, and operate data pipelines.

### Project-Specific Consumer workspaces

Teams may create multiple project-specific consumer workspaces for exploration, AI, and BI consumption. Each workspace uses `99_explore` to read approved data from Engineering Production into its own project environment.

!!! note "Trusted Production source"

    Consumer workspaces do not reproduce the production pipeline or maintain their own production copies of the source, unified, or product lakehouses. Engineering Production remains the trusted Production source.

## FabricOps uses PySpark mainly

**PySpark is the standard for repeatable `02_pipeline` workflows.**

Spark has startup overhead, and pandas may be better suited to smaller one-off analyses. FabricOps uses PySpark because it supports larger datasets and provides a consistent engineering pattern for maintenance and handover.

This does not prevent teams from using pandas or other tools for appropriate exploration.

## The ETL model inside `02_pipeline`

FabricOps uses a simple engineering model inside `02_pipeline`:

**0. Environment → E. Extract → T. Transform → L. Load**

### 0. Environment

`00_env_config` establishes whether the pipeline is running in Development or Production and resolves the configured Fabric stores.

- **Development** can use current authoring for Guardrails and processing definitions, or test a selected Data Contract where needed.
- **Production** uses the approved active Data Contract as the governed runtime definition.

### E. Extract

For one or more source table IDs, Engineering:

- resolves the applicable Guardrails from the Data Contract, or from the Guardrail metadata in Development
- determines the source read strategy as full or incremental
- checks schema, freshness, and change state before reading where possible
- reads the source table into a DataFrame using the resolved read strategy
- evaluates Data Quality Guardrails on the DataFrame
- profiles and registers the source only when the DataFrame represents the complete physical table, writing the observed profile and lineage evidence into FabricOps metadata

An incremental source DataFrame is a processing slice and must not replace the registered full-table source profile.

### T. Transform

Transformation is user-defined business logic. FabricOps does not prescribe how the engineer joins, derives, aggregates, enriches, or reshapes the data.

### L. Load

For one or more target table IDs, Engineering:

- resolves the target load strategy and Guardrails from the Data Contract, or from the Guardrail metadata in Development
- checks the transformed DataFrame against target schema and Data Quality Guardrails
- records the Data Quality outcome so it can be linked back to the corresponding Guardrail Results evidence
- prepares the DataFrame according to the governed load strategy and adds required audit and technical columns
- writes the target table
- reads the persisted target table back as a full DataFrame
- profiles and registers the complete persisted target, including the resulting profile and lineage evidence

This keeps the business transformation flexible while standardizing the governed checks, metadata evidence, and target write behavior around it.

## The governance and engineering loop workflow

**FabricOps uses a governed loop between Governance and Engineering Development before a validated pipeline is promoted to Engineering Production.**

![FabricOps role workflow](assets/fabricops-role-workflow.png)

Read the [Guided Demo](guided-demo.md) to execute the workflow. Download the notebooks from [Notebook Templates](notebook-templates.md).

### 0. Set up the operating environment

Create the Fabric workspaces, configure `00_env_config` in each workspace, and create the Governance metadata tables.

### 1. Governance — Create Data Stewards and Data Agreements

In `01_governance`, create the Data Stewards and establish Data Agreements between two accountable stewards.

### 2. Engineering — ETL, profile the data, and build the Data Catalogue

In Engineering Development, run `02_pipeline` to perform ETL, profile the data, and write Data Catalogue, Data Profiled, Data Profiled Frequency where applicable, and Data Lineage records.

### 3. Governance — Enrich the Data Catalogue and define Guardrails

Return to `01_governance` to read the Data Catalogue and Data Profiled records written by `02_pipeline`, write Enrichment, and define Guardrails for the ETL workflow.

### 4. Engineering — Re-validate the ETL workflow with Guardrails

Rerun `02_pipeline` with the approved Guardrails and confirm that warning, blocking, and validation behaviour works as intended.

### 5. Governance — Create the Data Contract and prepare for promotion

In `01_governance`, create the Data Contract linking the governed Data Catalogues to the Data Agreement, then finalise the ETL contract and governance sign-off in preparation for promotion and release management.

### 6. Engineering — Promote to Production

Promote the validated `02_pipeline` ETL workflow from Engineering Development to Engineering Production.

### 7. Consumer — Use approved Production data directly

Use `99_explore` to consume approved Production data directly for analytics, AI, BI, or downstream project use.

## Metadata stored supporting the workflow

**The Data Catalogue sits at the centre of the FabricOps metadata model.**

![FabricOps metadata model](assets/fabricops-metadata-model.png)

### Governance records

[FabricOps metadata tables](reference/metadata.md) carry Governance information through the workflow. Data Agreements establish the relationship between producer and consumer parties. Machine-readable Data Contracts define the specific datasets and delivery promises authorised under each agreement.

### Engineering records

The Data Catalogue identifies each dataset and connects Data Profiled, Data Profiled Frequency, Data Lineage, Data Access, Enrichment, Guardrail, and Guardrail Results records.

### Contract relationship

A Data Contract links authorised Data Catalogue tables and their schema fingerprints to a parent Data Agreement. Related Enrichment, Guardrail, Data Profiled, Data Profiled Frequency, and Data Lineage records describe those tables. One Data Agreement can govern multiple Data Contracts.

!!! note "Observed records stay with Engineering"

    `02_pipeline` writes Data Catalogue and Data Profiled records. `01_governance` reads those records for Enrichment, Guardrail definition, and Data Contract preparation. Governance does not create a second copy of those observed records.

## How the implemented pieces connect

**Engineering records what happened. Governance defines what is allowed. Production exposes the approved result.**

`02_pipeline` performs ETL, profiles source and target data, and writes Data Catalogue, Data Profiled, Data Profiled Frequency where applicable, and Data Lineage records.

Governance reads the Data Catalogue and Data Profiled records, then writes approved Enrichment and Guardrail records. `02_pipeline` reads those records, evaluates the Guardrails, and writes Guardrail Results.

Governance then creates the Data Contract. The validated `02_pipeline` is promoted from Engineering Development to Engineering Production, where AI and BI analytics consume approved Production data.

Downstream users therefore receive more than a table. Where relevant, they can inspect its Data Catalogue, Data Profiled, Data Profiled Frequency, Data Lineage, Enrichment, Guardrails, Guardrail Results, Data Agreement, and Data Contract.

## Development and Production

### Engineering Development

Used for exploration, development, profiling, testing, and review. Development data and temporary notebooks may be cleaned regularly, so teams should avoid treating the workspace as durable Production storage.

### Engineering Production

Contains approved, stable, recurring pipelines and durable outputs. A recurring Production pipeline may run on any required operational schedule, including annually, when the process needs to remain stable and repeatable.

!!! important "Production rule"

    All promoted `02_pipeline` notebooks should be tied to a Data Contract.

## Consumer workspaces

Project-specific consumer workspaces provide a separate environment for exploration, AI, and BI consumption. Teams use `99_explore` in their own workspace to consume approved data from Engineering Production without changing or duplicating the production pipeline.

There may be multiple consumer workspaces, with each workspace aligned to a specific project, analytical product, or business use case.

??? info "When consumer work should move into the governed pipeline"

    Important `99_explore` work should be preserved when reproducibility is required. Consumer notebooks support analysis and experimentation, but they should not become an alternative production pipeline.

    Repeatable data preparation that needs to be operationalised should be incorporated into the governed Engineering Development and Engineering Production workflow.
