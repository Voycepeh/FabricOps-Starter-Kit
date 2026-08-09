# How FabricOps works

![FabricOps operating model overview](assets/fabricops-operating-model-overview.png)

## The FabricOps workspace operating model

| Workspace | Primary Purpose | Main Fabric Stores |
| --------- | --------------- | ------------------ |
| Governance | Manage data stewards, data agreements, data contracts, catalogue enrichment, and guardrails | Development and Production metadata lakehouses |
| Engineering Development | Explore data and develop, profile, test, and review repeatable pipelines | Source, unified, and product lakehouses or warehouses |
| Engineering Production | Run approved and stable production pipelines on the required operational schedule | Production source, unified, and product lakehouses or warehouses |
| Project-Specific Consumer | Support project-level exploration, AI, and BI consumption without duplicating the production engineering workflow | Consumes approved data from the Engineering Production workspace |

FabricOps uses three shared core workspaces: Governance, Engineering Development, and Engineering Production. These workspaces establish the common governance and engineering workflow used to create, validate, govern, and operate data pipelines.

Teams may then create multiple project-specific consumer workspaces for exploration, AI, and BI consumption. Each consumer workspace uses the `99_explore` notebook to read approved data from the Engineering Production workspace into its own project environment.

Consumer workspaces do not reproduce the production pipeline or maintain their own production copies of the source, unified, or product lakehouses. The Engineering Production workspace remains the trusted production source, while consumer teams work independently in workspaces designed for their specific use cases.


![FabricOps role workflow](assets/fabricops-role-workflow.png)

Read this to execute this workflow [Guided Demo](guided-demo/)
Download the notebooks from [Notebook Templates](notebook-templates.md).

## The governance and engineering loop workflow 

The operating flow uses three core FabricOps workspaces: Governance, Engineering Development, and Engineering Production. Once an approved production pipeline is available, multiple project-specific consumer workspaces may consume its outputs for exploration, AI, and BI use cases.

0. **Set up the operating environment** — Create the Fabric workspaces, configure `00_env_config` in each workspace, and create the Governance metadata tables.

1. **Governance — Create Data Stewards and Data Agreements** — In `01_governance`, create the Data Stewards and establish Data Agreements between two accountable stewards.

2. **Engineering — ETL, profile the data, and build the Data Catalogue** — In Engineering Development, run `02_pipeline` to perform ETL, profile the data, and write the Data Catalogue and supporting profile and technical evidence.

3. **Governance — Enrich the Data Catalogue and define guardrails** — Return to `01_governance` to read the Catalogue and Profile evidence written by `02_pipeline`, enrich the Data Catalogue, and define guardrails for the ETL workflow.

4. **Engineering — Re-validate the ETL workflow with guardrail rules** — Rerun `02_pipeline` with the defined guardrails and confirm that warning, blocking, and validation behaviour works as intended.

5. **Governance — Create the Data Contract and prepare for promotion** — In `01_governance`, create the Data Contract linking the governed Data Catalogues to the Data Agreement, then finalise the ETL contract and governance sign-off in preparation for promotion and release management.

6. **Engineering — Promote to Production** — Promote the validated `02_pipeline` ETL workflow from Engineering Development to Engineering Production.

7. **Consumer — Use approved Production data directly** — Use `99_explore` to consume approved Production data directly for analytics, AI, BI, or downstream project use.

## Metadata stored supporting the workflow

![FabricOps metadata model](assets/fabricops-metadata-model.png)

FabricOps uses these connected [Metadata Tables](reference/metadata.md) to carry governance context through the workflow. Data Agreements establish the overarching governance relationship between producer and consumer parties. Machine-readable Data Contracts define the specific datasets and delivery promises authorised under each agreement.

The data catalogue sits at the centre of the model. It identifies each governed dataset and connects its profiling, lineage, access, enrichment, guardrails, and guardrail results.

A Data Contract then links authorised catalogue tables and their schema fingerprints to a parent Data Agreement. Related catalogue, enrichment, guardrail, profiling, and lineage metadata provide broader technical and quality context for those tables. One Data Agreement can govern multiple Data Contracts.

The `02_pipeline` workflow writes catalogue and profile evidence into metadata; `01_governance` reads that evidence for enrichment, guardrail definition, and Data Contract preparation. Governance does not create a second copy of the observed evidence.

## Development and Production

Engineering Development is used for exploration, development, profiling, testing, and review. Development data and temporary notebooks may be cleaned regularly, so teams should avoid treating the workspace as durable production storage.

Engineering Production contains approved, stable, recurring pipelines and durable outputs. All promoted "02_pipeline" notebooks should be tied to a data contract. A recurring Production pipeline may run on any required operational schedule, including annually, when the process needs to remain stable and repeatable.

Project-specific consumer workspaces provide a separate environment for exploration, AI, and BI consumption. Teams use `99_explore` in their own workspace to consume approved data from the Engineering Production workspace without changing or duplicating the production pipeline.

There may be multiple consumer workspaces, with each workspace aligned to a specific project, analytical product, or business use case. This separation allows consumer teams to work independently while keeping production pipelines, controls, and durable outputs centrally managed.

Important `99_explore` work should be preserved when reproducibility is required. Consumer notebooks support analysis and experimentation, but they should not become an alternative production pipeline. Repeatable data preparation that needs to be operationalised should be incorporated into the governed Engineering Development and Engineering Production workflow.

## Note ! FabricOps uses PySpark mainly 

Spark has startup overhead, and pandas may be better suited to smaller one-off analyses. FabricOps still uses PySpark as the standard for repeatable "02_pipeline" workflows because it supports larger datasets and provides a consistent engineering pattern for maintenance and handover.

This standard does not prevent teams from using pandas or other tools for appropriate exploration. It establishes the repeatable production pipeline pattern.
