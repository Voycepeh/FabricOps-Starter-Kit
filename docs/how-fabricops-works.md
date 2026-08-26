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

??? info "Key FabricOps concepts — optional quick reference"

    This quick reference surfaces the curated user-facing terms from the canonical glossary. Open a group to scan its terms, then expand only the definition you need. The canonical source remains `docs/reference/_data/glossary.json`.

    <details>
    <summary><strong>FabricOps concepts</strong> — 15 terms</summary>

    <details>
    <summary><strong>FabricOps Starter Kit</strong></summary>
    <p>A plug-and-play Data Engineering and Governance practice for Microsoft Fabric, implemented through a planned operating workflow, standardized notebook templates, reusable notebook-facing functions, and a shared metadata model.</p>
    </details>

    <details>
    <summary><strong>Profile</strong></summary>
    <p>A Profile is a summary of the data at a point in time. It shows things like row count, columns, data types, nulls, distinct values, minimum and maximum values, and value distributions. In FabricOps, this is stored in Data Profiled and Data Profiled Frequency metadata.</p>
    </details>

    <details>
    <summary><strong>Enrichment</strong></summary>
    <p>Enrichment is the business and governance information added to the Data Catalogue after the technical metadata has been captured. It includes descriptions, ownership, sensitivity, classification, and how the data is intended to be used.</p>
    </details>

    <details>
    <summary><strong>Guardrails</strong></summary>
    <p>Guardrails are the governed rules FabricOps applies to data and pipelines. Today, they can check schema, freshness, profile behaviour, change over time, and data quality. In future they can also cover governance requirements such as stricter handling for sensitive data, masking or restricted access for PII, and additional controls for specific classifications.</p>
    </details>

    <details>
    <summary><strong>Enforcement</strong></summary>
    <p>Enforcement is when FabricOps applies the active Guardrails during a pipeline run and acts on the result. Depending on the Guardrail, the pipeline can continue, continue with a warning, or stop.</p>
    </details>

    <details>
    <summary><strong>Guardrail Result</strong></summary>
    <p>A Guardrail Result is the recorded outcome after FabricOps evaluates a Guardrail during a pipeline run. It records whether the check passed, warned, or failed, what was checked, and whether the pipeline is allowed to continue.</p>
    </details>

    <details>
    <summary><strong>Data Steward</strong></summary>
    <p>A Data Steward is the person or role responsible for reviewing and maintaining the governance context for data, including its meaning, ownership, sensitivity, intended use, and governance decisions.</p>
    </details>

    <details>
    <summary><strong>Data Agreement</strong></summary>
    <p>A Data Agreement establishes the governed context for a dataset before engineering proceeds. It captures the parties involved, steward context, intended use, and expectations that guide the FabricOps workflow.</p>
    </details>

    <details>
    <summary><strong>Data Contract</strong></summary>
    <p>A Data Contract is the approved definition of the structure, meaning, quality expectations, ownership, processing expectations, and governance requirements for governed Production data.</p>
    </details>

    <details>
    <summary><strong>Metadata</strong></summary>
    <p>Metadata is information about the data. In FabricOps this includes its structure, Profile, ownership, business meaning, sensitivity, Guardrails, lineage, Data Agreement, Data Contract, and other information used to understand and govern it.</p>
    </details>

    <details>
    <summary><strong>Configuration-driven Engineering</strong></summary>
    <p>Configuration-driven Engineering means defining reusable pipeline behaviour through configuration so teams can change settings, targets, strategies, and governed parameters without duplicating or rewriting the underlying engineering logic.</p>
    </details>

    <details>
    <summary><strong>Governance as Code</strong></summary>
    <p>Governance as Code means defining governance rules in a structured, version-controlled way so they can be reviewed, repeated, and applied consistently by FabricOps. This can include Guardrails, data quality rules, sensitivity and PII requirements, access rules, approvals, governance states, and other policies that can be expressed as configuration or executable checks. Policy as Code is treated as an alias within this concept.</p>
    </details>

    <details>
    <summary><strong>Data Access</strong></summary>
    <p>Data Access describes who is allowed to access governed data and the conditions or restrictions that apply. It provides the governance context that can be implemented through platform security controls such as RLS, OLS, permissions, or other access mechanisms.</p>
    </details>

    <details>
    <summary><strong>Data Sensitivity</strong></summary>
    <p>Data Sensitivity describes how carefully data should be handled based on confidentiality, privacy, business risk, or regulatory requirements. It can influence access, masking, sharing, and other governance controls.</p>
    </details>

    <details>
    <summary><strong>PII</strong></summary>
    <p>PII, or personally identifiable information, is data that can identify or be linked to an individual. In a governed workflow it may require additional controls such as restricted access, masking, or stricter handling.</p>
    </details>

    </details>

    <details>
    <summary><strong>Microsoft Fabric basics</strong> — 5 terms</summary>

    <details>
    <summary><strong>Microsoft Fabric</strong></summary>
    <p>Microsoft Fabric is the analytics platform FabricOps runs on, providing workspaces, Lakehouses, Warehouses, notebooks, Spark, SQL, and other data capabilities.</p>
    </details>

    <details>
    <summary><strong>Workspace</strong></summary>
    <p>A Workspace is a Microsoft Fabric container used to organize and secure related items such as notebooks, Lakehouses, Warehouses, semantic models, and reports.</p>
    </details>

    <details>
    <summary><strong>Lakehouse</strong></summary>
    <p>A Lakehouse in Microsoft Fabric stores files and managed Delta tables in OneLake and is commonly used with Spark, notebooks, and SQL analytics endpoints.</p>
    </details>

    <details>
    <summary><strong>Warehouse</strong></summary>
    <p>A Warehouse in Microsoft Fabric provides relational tables and SQL-based querying for structured analytics and data warehousing workloads.</p>
    </details>

    <details>
    <summary><strong>Notebook</strong></summary>
    <p>A Notebook is an interactive Microsoft Fabric document where users can run Python, PySpark, SQL, and other supported code for data engineering, analysis, experimentation, and operational workflows.</p>
    </details>

    </details>

    <details>
    <summary><strong>Data Engineering basics</strong> — 11 terms</summary>

    <details>
    <summary><strong>Pipeline</strong></summary>
    <p>A Pipeline is a repeatable sequence of data-processing steps that can read source data, transform it, apply checks, and write results to a target.</p>
    </details>

    <details>
    <summary><strong>PySpark</strong></summary>
    <p>PySpark lets Python code use Apache Spark to process data across a distributed compute engine. It is commonly used in Fabric notebooks for large-scale transformations and data engineering.</p>
    </details>

    <details>
    <summary><strong>Parallel Processing</strong></summary>
    <p>Parallel Processing divides work so multiple tasks or data partitions can be processed at the same time, which can reduce elapsed processing time when the workload and compute resources support it.</p>
    </details>

    <details>
    <summary><strong>Incremental Load</strong></summary>
    <p>An Incremental Load processes only the new or changed portion of a source since the previous successful processing point, reducing unnecessary reads and writes compared with a full load.</p>
    </details>

    <details>
    <summary><strong>Slowly Changing Dimensions (SCD)</strong></summary>
    <p>Slowly Changing Dimensions are data-modelling patterns for handling changes to descriptive records. Common approaches include SCD Type 1, which replaces the previous value, and SCD Type 2, which keeps history by creating versioned records.</p>
    </details>

    <details>
    <summary><strong>Data Modelling</strong></summary>
    <p>Data Modelling is the practice of designing tables, fields, keys, relationships, and structures so data supports its intended analytical, operational, or reporting use.</p>
    </details>

    <details>
    <summary><strong>Schema</strong></summary>
    <p>A Schema describes the structure of a dataset or table, including column names, data types, and other structural expectations.</p>
    </details>

    <details>
    <summary><strong>Data Quality</strong></summary>
    <p>Data Quality describes whether data meets expected rules for things such as completeness, validity, consistency, uniqueness, accuracy, and other requirements needed for its intended use.</p>
    </details>

    <details>
    <summary><strong>Partitioning</strong></summary>
    <p>Partitioning divides data into groups, often using a column such as date, so engines can process or replace only the relevant parts rather than scanning or rewriting the entire dataset.</p>
    </details>

    <details>
    <summary><strong>Append</strong></summary>
    <p>Append adds new rows to an existing target while leaving existing rows unchanged. It is appropriate only when incoming data is additive and existing records do not need to be changed or removed.</p>
    </details>

    <details>
    <summary><strong>Overwrite</strong></summary>
    <p>Overwrite replaces existing target data with the newly prepared data. Depending on the implementation, it can replace a whole table or only a governed partition scope.</p>
    </details>

    </details>

    <details>
    <summary><strong>Security and access basics</strong> — 3 terms</summary>

    <details>
    <summary><strong>Row-Level Security (RLS)</strong></summary>
    <p>Row-Level Security limits the rows returned to a user based on identity, role, or access rules while allowing the same table or model to serve different audiences.</p>
    </details>

    <details>
    <summary><strong>Object-Level Security (OLS)</strong></summary>
    <p>Object-Level Security restricts access to specific data objects, such as tables or columns, so unauthorized users cannot see those objects even when they can access the wider model or dataset.</p>
    </details>

    <details>
    <summary><strong>Access Control</strong></summary>
    <p>Access Control is the broader set of rules and mechanisms used to decide who can access datasets, tables, columns, workspaces, files, or other resources and what actions they are allowed to perform.</p>
    </details>

    </details>

    <details>
    <summary><strong>File and configuration basics</strong> — 1 term</summary>

    <details>
    <summary><strong>Configuration</strong></summary>
    <p>Configuration is the set of named settings used to control environment targets, processing choices, rules, parameters, and other behaviour without rewriting the implementation.</p>
    </details>

    </details>

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
    - Write Data Profiled and Data Lineage records.

!!! note "Warehouse sources should land in the Source Lakehouse first"

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
