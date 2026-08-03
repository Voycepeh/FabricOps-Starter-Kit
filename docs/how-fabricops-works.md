# How FabricOps works

![FabricOps operating model overview](assets/fabricops-operating-model-overview.png)

## The FabricOps workspace operating model

| Workspace | Primary Purpose | Main Fabric Stores |
| --------- | --------------- | ------------------ |
| Governance | Manage data stewards, data agreements, data contracts, catalogue enrichment, and guardrails | Development and Production metadata lakehouses |
| Engineering Development | Explore data and develop, profile, test, and review repeatable pipelines | Source, unified, and product lakehouses or warehouses |
| Engineering Production | Run approved and stable production pipelines on the required operational schedule | Production source, unified, and product lakehouses or warehouses |
| Project-Specific Consumer | Support project-level exploration, AI, and BI consumption without duplicating the production engineering workflow | Consumes approved data from the Engineering Production workspace |

FabricOps uses three shared core workspaces: Governance, Engineering Development, and Engineering Production. These workspaces establish the common governance and engineering workflow used to create, review, approve, and operate data pipelines.

Teams may then create multiple project-specific consumer workspaces for exploration, AI, and BI consumption. Each consumer workspace uses the `99_explore` notebook to read approved data from the Engineering Production workspace into its own project environment.

Consumer workspaces do not reproduce the production pipeline or maintain their own production copies of the source, unified, or product lakehouses. The Engineering Production workspace remains the trusted production source, while consumer teams work independently in workspaces designed for their specific use cases.


![FabricOps role workflow](assets/fabricops-role-workflow.png)

Read this to execute this workflow [Guided Demo](guided-demo/)
Download the notebooks from [Notebook Templates](notebook-templates.md).

## The governance and engineering loop workflow 

The operating flow uses three core FabricOps workspaces: Governance, Engineering Development, and Engineering Production. Once an approved production pipeline is available, multiple project-specific consumer workspaces may consume its outputs for exploration, AI, and BI use cases.

0. **Set up the operating environment** — Create the Fabric workspaces, create the required lakehouses and warehouses, configure a "00_env_config" notebook in every workspace, and create the metadata tables in the Governance workspace.

1. **Governance workflow 1** — In the Governance workspace, use "01_agreement" to create data stewards and create a data agreement between data stewards.

2. **Engineering workflow 1** — In the Engineering Development workspace, use "02_pipeline" to extract, transform, and load data from one data store to another. Profile source and target tables, then write data catalogue, data profiled, and data lineage metadata.

3. **Governance workflow 2** — In the Governance workspace, use "03_review" to pick from the data catalogue table, add descriptions and classifications to selected tables, and define guardrails such as schema enforcement and data quality.

4. **Engineering workflow 2** — In the Engineering Development workspace, use "02_pipeline" to wire in the guardrail rules defined during review, then run the pipeline and make sure it fails or warns users as configured.

5. **Governance workflow 3** — In the Governance workspace, use "01_agreement" to pick from the data catalogue table, create a data contract linking the data tables to the data agreement, and get the data steward to sign off on the contract.

6. **Engineering workflow 3** — In the Engineering Production workspace, promote the "02_pipeline" that was completed in Engineering Development.

7. **Project consumption** — Create one or more project-specific consumer workspaces as required. In each workspace, use `99_explore` to consume approved data from the Engineering Production workspace for project-level exploration, AI development, or BI analysis.

## Metadata stored supporting the workflow

![FabricOps metadata model](assets/fabricops-metadata-model.png)

FabricOps uses these connected [Metadata Tables](../reference/metadata/) to carry governance context through the workflow.

The data catalogue sits at the centre of the model. It identifies each governed dataset and connects its profiling, lineage, access, enrichment, guardrails, and guardrail results.

A data contract then binds the validated catalogue entry to a data agreement, connecting what engineering produced to its approved purpose, owners, and production expectations.

The "02_pipeline" workflow creates and reviews this metadata during exploration. The "03_review" workflow applies the approved controls and produces the repeatable production pipeline.

## Development and Production

Engineering Development is used for exploration, development, profiling, testing, and review. Development data and temporary notebooks may be cleaned regularly, so teams should avoid treating the workspace as durable production storage.

Engineering Production contains approved, stable, recurring pipelines and durable outputs. All promoted "02_pipeline" notebooks should be tied to a data contract. A recurring Production pipeline may run on any required operational schedule, including annually, when the process needs to remain stable and repeatable.

Project-specific consumer workspaces provide a separate environment for exploration, AI, and BI consumption. Teams use `99_explore` in their own workspace to consume approved data from the Engineering Production workspace without changing or duplicating the production pipeline.

There may be multiple consumer workspaces, with each workspace aligned to a specific project, analytical product, or business use case. This separation allows consumer teams to work independently while keeping production pipelines, controls, and durable outputs centrally managed.

Important `99_explore` work should be preserved when reproducibility is required. Consumer notebooks support analysis and experimentation, but they should not become an alternative production pipeline. Repeatable data preparation that needs to be operationalised should be incorporated into the governed Engineering Development and Engineering Production workflow.

## Note ! FabricOps uses PySpark mainly 

Spark has startup overhead, and pandas may be better suited to smaller one-off analyses. FabricOps still uses PySpark as the standard for repeatable "02_pipeline" workflows because it supports larger datasets and provides a consistent engineering pattern for maintenance and handover.

This standard does not prevent teams from using pandas or other tools for appropriate exploration. It establishes the repeatable production pipeline pattern.
