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

*These are the high-level FabricOps concepts. You do not need to learn the full glossary before reading this page.*

- **[FabricOps Starter Kit](glossary.md#fabricops-starter-kit)**: a plug-and-play Data Engineering and Governance practice for Microsoft Fabric.
- **[Metadata](glossary.md#metadata)**: information about the data. In FabricOps this includes its structure, Profile, ownership, business meaning, sensitivity, Guardrails, lineage, Data Agreement, Data Contract, and other information used to understand and govern it.
- **[Governance as Code](glossary.md#governance-as-code)**: defining governance rules in a structured, version-controlled form that can be applied consistently.
- **[Configuration-driven Engineering](glossary.md#configuration-driven-engineering)**: controlling repeatable engineering behaviour through configuration instead of rewriting pipeline code.

As unfamiliar terms appear, use the [FabricOps Glossary](glossary.md). It follows the operating workflow and separates FabricOps, Governance, and Engineering concepts.

### Key glossary terms in the workflow

These terms appear repeatedly as Governance and Engineering move from agreement through Development, validation, Data Contract activation, Production, and consumption.

| Term | FabricOps meaning |
| ---- | ----------------- |
| **[Data Steward](glossary.md#data-steward)** | The person or role responsible for reviewing and maintaining the governance context for data. |
| **[Data Agreement](glossary.md#data-agreement)** | The governed record that establishes who is sharing what data, with whom, and why. |
| **[Profile](glossary.md#profile)** | A summary of the data at a point in time. |
| **[Enrichment](glossary.md#enrichment)** | Business and governance information added to the Data Catalogue after technical metadata has been captured. |
| **[Guardrails](glossary.md#guardrails)** | Governed rules FabricOps applies to data and pipelines. |
| **[Enforcement](glossary.md#enforcement)** | Applying active Guardrails during a pipeline run and acting on the result. |
| **[Guardrail Result](glossary.md#guardrail-result)** | The recorded outcome after FabricOps evaluates a Guardrail during a pipeline run. |
| **[Data Contract](glossary.md#data-contract)** | The approved definition of what is expected from governed Production data. |
| **[Configuration](glossary.md#configuration)** | Settings that define how FabricOps or a pipeline should behave without changing the underlying code. |
| **[Data Quality](glossary.md#data-quality)** | Whether data meets the expectations required for its intended use. |

</div>

<div class="fabricops-section-block" markdown>

## Workspace model

| Workspace | Primary Purpose | Main Fabric Stores |
| --------- | --------------- | ------------------ |
| Governance | Manage data stewards, data agreements, data contracts, catalogue enrichment, and guardrails | Development and Production metadata lakehouses |
| Engineering Development | Explore data and develop, profile, test, and review repeatable pipelines | Source, unified, and product lakehouses or warehouses |
| Engineering Production | Run governed and stable production pipelines on the required operational schedule | Production source, unified, and product lakehouses or warehouses |
| Project-Specific Consumer | Support project-level exploration, AI, and BI consumption without duplicating the production engineering workflow | Consumes governed data from the Engineering Production workspace |

??? info "Read more about the workspace model"

    **Core workspaces**

    Governance, Engineering Development, and Engineering Production establish the shared governance and engineering workflow used to create, validate, govern, and operate data pipelines.

    **Project-Specific Consumer workspaces**

    Teams may create multiple project-specific consumer workspaces for exploration, AI, and BI consumption. Each workspace uses `99_explore` to read governed data from Engineering Production into its own project environment.

    **Trusted Production source**

    Consumer workspaces do not reproduce the production pipeline or maintain their own production copies of the source, unified, or product lakehouses. Engineering Production remains the trusted Production source.

</div>

<div class="fabricops-section-block" markdown>

## The governance and engineering loop workflow

**FabricOps uses a governed loop between Governance and Engineering Development before a validated pipeline is promoted to Engineering Production.**

![FabricOps role workflow](assets/fabricops-role-workflow.png)

Read the [Guided Demo](guided-demo.md) to execute the workflow. Download the notebooks from [Notebook Templates](notebook-templates.md).

??? info "Read the workflow step by step"

    **0. Set up the operating environment**

    Create the Fabric workspaces, configure `00_env_config` in each workspace, and create the Governance metadata tables.

    **1. Governance: Create Data Stewards and Data Agreements**

    In `01_governance`, create the Data Stewards and establish Data Agreements between two accountable stewards.

    **2. Engineering: ETL, profile data, and build the Data Catalogue**

    In Engineering Development, run `02_pipeline` to perform ETL, profile the data, and write Data Catalogue, Data Profiled, Data Profiled Frequency where applicable, and Data Lineage records.

    **3. Governance: Enrich the Data Catalogue and define Guardrails**

    Return to `01_governance` to read the Data Catalogue and Data Profiled records written by `02_pipeline`, write Enrichment, and define Guardrails for the ETL workflow.

    **4. Engineering: Validate with current or frozen Guardrails**

    Rerun `02_pipeline` with the current authored Guardrails, or with Guardrails from a selected frozen Data Contract, and confirm that warning, blocking, and validation behaviour works as intended.

    **5. Governance: Assemble and activate a Data Contract**

    In `01_governance`, create the versioned Data Contract linking the governed Data Catalogues to the Data Agreement and activate the Production version in preparation for Production.

    **6. Engineering: Run Production against the active Data Contract**

    Run `02_pipeline` in Engineering Production against the active Data Contract.

    **7. Consumer: Use Production data directly**

    Use `99_explore` to consume governed Production data directly for analytics, AI, BI, or downstream project use.

</div>

<div class="fabricops-section-block" markdown>

## Development and Production

### Engineering Development

Engineering Development is used for exploration, development, profiling, testing, and review. `02_pipeline` performs ETL, profiles source and target data, and writes Data Catalogue, Data Profiled, Data Profiled Frequency where applicable, and Data Lineage records.

Governance reads the Data Catalogue and Data Profiled records, then writes Enrichment and Guardrail records. `02_pipeline` reads those records, evaluates the Guardrails, and writes Guardrail Results. Development can use current authoring or a selected Data Contract.

Development data and temporary notebooks may be cleaned regularly, so teams should avoid treating the workspace as durable Production storage.

### Data Agreement and Data Contract

A [Data Agreement](glossary.md#data-agreement) establishes the governed context before Engineering proceeds. It captures who is sharing what data, with whom, and why.

A [Data Contract](glossary.md#data-contract) is the approved definition of the structure, meaning, quality expectations, ownership, processing expectations, and governance requirements for governed Production data.

In Governance, `01_governance` assembles and activates the Data Contract after the Development and Governance loop. This is where the approved governance rules are represented in the structured, version-controlled form described by [Governance as Code](glossary.md#governance-as-code), while Production behaviour is resolved through the [Configuration-driven Engineering](glossary.md#configuration-driven-engineering) model.

### Engineering Production

Engineering Production contains governed, stable, recurring pipelines and durable outputs. In Production, `02_pipeline` uses the active Data Contract.

A recurring Production pipeline may run on any required operational schedule, including annually, when the process needs to remain stable and repeatable.

!!! important "Production rule"

    All promoted `02_pipeline` notebooks should be tied to a Data Contract.

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
    - Write Data Profiled and Data Lineage records.

??? note "Warehouse sources should land in the Source Lakehouse first"

    For large or repeatedly processed Warehouse sources, use the Warehouse primarily as an ingestion boundary. Land the required full or incremental extract into the Source Lakehouse as Delta, then perform profiling, Data Quality checks, transformations, and governed processing from the Lakehouse. This keeps repeated Spark processing in OneLake and avoids using the external Warehouse as the normal processing layer.

!!! abstract "T. Transform"

    - Apply user-defined business transformation.
    - Join, derive, aggregate, enrich, and reshape as required.
    - FabricOps governs the inputs and outputs, not the business logic.

!!! success "L. Load"

    - Define one or more target table IDs.
    - Resolve target Guardrails and governed load strategy from the Data Contract, or Development definition.
    - Check schema and Data Quality.
    - Attach the relevant Guardrail Result linkage to the written data.
    - Add audit and technical columns.
    - Prepare load-strategy execution.
    - Write the target table.
    - Read back the full persisted target.
    - Profile and register the full written table into Data Lineage and Data Profile records.

??? note "Full-table profiling"

    Incremental processing may use a partial source slice for execution, but a partial DataFrame must not replace the registered profile of the full physical table.

??? info "Why FabricOps uses PySpark mainly"

    **[PySpark](glossary.md#pyspark) is the standard for repeatable `02_pipeline` workflows.**

    Spark has startup overhead, and pandas may be better suited to smaller one-off analyses. FabricOps uses PySpark because it supports larger datasets and provides a consistent engineering pattern for maintenance and handover.

    This does not prevent teams from using pandas or other tools for appropriate exploration.

</div>

<div class="fabricops-section-block" markdown>

## Metadata stored supporting the workflow

**The Data Catalogue sits at the centre of the FabricOps metadata model.**

![FabricOps metadata model](assets/fabricops-metadata-model.png)

The metadata model shows how the records introduced through the workflow connect. [Metadata](glossary.md#metadata) includes the information used to understand and govern the data, while the individual metadata tables record specific Governance and Engineering information.

??? info "Read how the metadata records connect"

    **Governance records**

    [FabricOps metadata tables](reference/metadata.md) carry Governance information through the workflow. Data Agreements establish the relationship between producer and consumer parties. Machine-readable Data Contracts define the specific datasets and delivery promises authorised under each agreement.

    **Engineering records**

    The Data Catalogue identifies each dataset and connects Data Profiled, Data Profiled Frequency, Data Lineage, Data Access, Enrichment, Guardrail, and Guardrail Results records.

    **Contract relationship**

    A Data Contract links authorised Data Catalogue tables and their schema fingerprints to a parent Data Agreement. Related Enrichment, Guardrail, Data Profiled, Data Profiled Frequency, and Data Lineage records describe those tables. One Data Agreement can govern multiple Data Contracts.

    **Observed records stay with Engineering**

    `02_pipeline` writes Data Catalogue and Data Profiled records. `01_governance` reads those records for Enrichment, Guardrail definition, and Data Contract preparation. Governance does not create a second copy of those observed records.

??? info "How the implemented pieces connect"

    **Engineering records what happened. Governance defines what is allowed. Production exposes the governed result.**

    `02_pipeline` performs ETL, profiles source and target data, and writes Data Catalogue, Data Profiled, Data Profiled Frequency where applicable, and Data Lineage records.

    Governance reads the Data Catalogue and Data Profiled records, then writes Enrichment and Guardrail records. `02_pipeline` reads those records, evaluates the Guardrails, and writes Guardrail Results.

    Governance then creates the Data Contract. The validated `02_pipeline` is promoted from Engineering Development to Engineering Production, where AI and BI analytics consume governed Production data.

    Downstream users therefore receive more than a table. Where relevant, they can inspect its Data Catalogue, Data Profiled, Data Profiled Frequency, Data Lineage, Enrichment, Guardrails, Guardrail Results, Data Agreement, and Data Contract.

</div>

<div class="fabricops-section-block" markdown>

## Consumer workspaces

Project-specific consumer workspaces provide a separate environment for exploration, AI, and BI consumption. Teams use `99_explore` in their own workspace to consume governed data from Engineering Production without changing or duplicating the production pipeline.

There may be multiple consumer workspaces, with each workspace aligned to a specific project, analytical product, or business use case.

??? info "When consumer work should move into the governed pipeline"

    Important `99_explore` work should be preserved when reproducibility is required. Consumer notebooks support analysis and experimentation, but they should not become an alternative production pipeline.

    Repeatable data preparation that needs to be operationalised should be incorporated into the governed Engineering Development and Engineering Production workflow.

</div>
