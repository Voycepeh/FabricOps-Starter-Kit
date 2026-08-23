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

## Workspace model

| Workspace | Primary Purpose | Main Fabric Stores |
| --------- | --------------- | ------------------ |
| Governance | Manage data stewards, data agreements, data contracts, catalogue enrichment, and guardrails | Development and Production metadata lakehouses |
| Engineering Development | Explore data and develop, profile, test, and review repeatable pipelines | Source, unified, and product lakehouses or warehouses |
| Engineering Production | Run governed and stable production pipelines on the required operational schedule | Production source, unified, and product lakehouses or warehouses |
| Project-Specific Consumer | Support project-level exploration, AI, and BI consumption without duplicating the production engineering workflow | Consumes governed data from the Engineering Production workspace |

### Core workspaces

Governance, Engineering Development, and Engineering Production establish the shared governance and engineering workflow used to create, validate, govern, and operate data pipelines.

### Project-Specific Consumer workspaces

Teams may create multiple project-specific consumer workspaces for exploration, AI, and BI consumption. Each workspace uses `99_explore` to read governed data from Engineering Production into its own project environment.

!!! note "Trusted Production source"

    Consumer workspaces do not reproduce the production pipeline or maintain their own production copies of the source, unified, or product lakehouses. Engineering Production remains the trusted Production source.

</div>

<div class="fabricops-section-block" markdown>

## FabricOps uses PySpark mainly

**PySpark is the standard for repeatable `02_pipeline` workflows.**

Spark has startup overhead, and pandas may be better suited to smaller one-off analyses. FabricOps uses PySpark because it supports larger datasets and provides a consistent engineering pattern for maintenance and handover.

This does not prevent teams from using pandas or other tools for appropriate exploration.

</div>

<div class="fabricops-section-block" markdown>

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

Rerun `02_pipeline` with the current authored Guardrails, or with Guardrails from a selected frozen Data Contract, and confirm that warning, blocking, and validation behaviour works as intended.

### 5. Governance — Create the Data Contract and prepare for promotion

In `01_governance`, create the Data Contract linking the governed Data Catalogues to the Data Agreement, then finalise the ETL contract and governance sign-off in preparation for promotion and release management.

### 6. Engineering — Promote to Production

Promote the validated `02_pipeline` ETL workflow from Engineering Development to Engineering Production.

### 7. Consumer — Use governed Production data directly

Use `99_explore` to consume governed Production data directly for analytics, AI, BI, or downstream project use.

</div>

<div class="fabricops-section-block" markdown>

## The ETL model inside `02_pipeline`

FabricOps standardizes the boundaries around ETL with a simple operating model:

**0. Environment → E. Extract → T. Transform → L. Load**

!!! abstract "0. Environment"

    - Determine Development or Production from `00_env_config`.
    - **Development:** use current authoring or a selected Data Contract.
    - **Production:** use the active Data Contract.

!!! info "E. Extract"

    - Define one or more source table IDs.
    - Resolve source Guardrails and Data Contract context, or Guardrail metadata in Development.
    - Check schema, freshness, and change state.
    - Read each source using the required **full or incremental** read strategy.
    - Run Data Quality checks.
    - Profile and register only when the DataFrame represents the **full physical table**.
    - Record Data Lineage and Data Profile evidence.

!!! abstract "T. Transform"

    - Apply user-defined business transformation.
    - Join, derive, aggregate, enrich, and reshape as required.
    - FabricOps governs the inputs and outputs, not the business logic.

!!! success "L. Load"

    - Define one or more target table IDs.
    - Resolve target Guardrails and governed load strategy from the Data Contract, or Development definition.
    - Check schema and Data Quality.
    - Attach Data Quality result linkage for runtime evidence.
    - Add audit and technical columns.
    - Prepare load-strategy execution.
    - Write the target table.
    - Read back the full persisted target.
    - Profile and register the full written table into Data Lineage and Data Profile records.

!!! note "Full-table profiling"

    Incremental processing may use a partial source slice for execution, but a partial DataFrame must not replace the registered profile of the full physical table.

</div>

<div class="fabricops-section-block" markdown>

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

</div>

<div class="fabricops-section-block" markdown>

## How the implemented pieces connect

**Engineering records what happened. Governance defines what is allowed. Production exposes the governed result.**

`02_pipeline` performs ETL, profiles source and target data, and writes Data Catalogue, Data Profiled, Data Profiled Frequency where applicable, and Data Lineage records.

Governance reads the Data Catalogue and Data Profiled records, then writes Enrichment and Guardrail records. `02_pipeline` reads those records, evaluates the Guardrails, and writes Guardrail Results.

Governance then creates the Data Contract. The validated `02_pipeline` is promoted from Engineering Development to Engineering Production, where AI and BI analytics consume governed Production data.

Downstream users therefore receive more than a table. Where relevant, they can inspect its Data Catalogue, Data Profiled, Data Profiled Frequency, Data Lineage, Enrichment, Guardrails, Guardrail Results, Data Agreement, and Data Contract.

</div>

<div class="fabricops-section-block" markdown>

## Development and Production

### Engineering Development

Used for exploration, development, profiling, testing, and review. Development data and temporary notebooks may be cleaned regularly, so teams should avoid treating the workspace as durable Production storage.

### Engineering Production

Contains governed, stable, recurring pipelines and durable outputs. A recurring Production pipeline may run on any required operational schedule, including annually, when the process needs to remain stable and repeatable.

!!! important "Production rule"

    All promoted `02_pipeline` notebooks should be tied to a Data Contract.

</div>

<div class="fabricops-section-block" markdown>

## Consumer workspaces

Project-specific consumer workspaces provide a separate environment for exploration, AI, and BI consumption. Teams use `99_explore` in their own workspace to consume governed data from Engineering Production without changing or duplicating the production pipeline.

There may be multiple consumer workspaces, with each workspace aligned to a specific project, analytical product, or business use case.

??? info "When consumer work should move into the governed pipeline"

    Important `99_explore` work should be preserved when reproducibility is required. Consumer notebooks support analysis and experimentation, but they should not become an alternative production pipeline.

    Repeatable data preparation that needs to be operationalised should be incorporated into the governed Engineering Development and Engineering Production workflow.

</div>
