# How FabricOps works

![FabricOps operating model overview](assets/fabricops-operating-model-overview.png)

## The three-workspace operating model

| Workspace | Primary Purpose | Main FabricStores |
| --------- | --------------- | ------------ |
| Governance | Data agreement, data contracts and enrichment of data catalogues| Dev and Prod Metadata lakehouses only|
| Engineering Development | Exploration of data, standard ETL with Guardrails | bronze, silver , gold lakehouse or warehouse|
| Engineering Production | Promoted ETL pipelines running on scheduled refresh| bronze, silver ,gold lakehouse or warehouse|


![FabricOps role workflow](assets/fabricops-role-workflow.png)

Read this to execute this workflow [Guided Demo](guided-demo/)
Download the notebooks from [Notebook Templates](notebook-templates.md).

## The governance and engineering loop workflow 

The operating flow uses only the three core FabricOps workspaces: Governance, Engineering Development, and Engineering Production.

0. **Set up the operating environment** — Create the Fabric workspaces, create the required lakehouses and warehouses, configure a "00_env_config" notebook in every workspace, and create the metadata tables in the Governance workspace.

1. **Governance workflow 1** — In the Governance workspace, use "01_agreement" to create data stewards and create a data agreement between data stewards.

2. **Engineering workflow 1** — In the Engineering Development workspace, use "02_pipeline" to extract, transform, and load data from one data store to another. Profile source and target tables, then write data catalogue, data profiled, and data lineage metadata.

3. **Governance workflow 2** — In the Governance workspace, use "03_review" to pick from the data catalogue table, add descriptions and classifications to selected tables, and define guardrails such as schema enforcement and data quality.

4. **Engineering workflow 2** — In the Engineering Development workspace, use "02_pipeline" to wire in the guardrail rules defined during review, then run the pipeline and make sure it fails or warns users as configured.

5. **Governance workflow 3** — In the Governance workspace, use "01_agreement" to pick from the data catalogue table, create a data contract linking the data tables to the data agreement, and get the data steward to sign off on the contract.

6. **Engineering workflow 3** — In the Engineering Production workspace, promote the "02_pipeline" that was completed in Engineering Development.

## Metadata stored supporting the workflow

![FabricOps metadata model](assets/fabricops-metadata-model.png)

FabricOps uses these connected [Metadata Tables](reference/metadata/) to carry governance context through the workflow.

The data catalogue sits at the centre of the model. It identifies each governed dataset and connects its profiling, lineage, access, enrichment, guardrails, and guardrail results.

A data contract then binds the validated catalogue entry to a data agreement, connecting what engineering produced to its approved purpose, owners, and production expectations.

The "02_pipeline" workflow creates and reviews this metadata during exploration. The "03_review" workflow applies the approved controls and produces the repeatable production pipeline.

## Development and Production

Engineering Development is used for exploration, development, profiling, testing, and review. Development data and temporary notebooks may be cleaned regularly, so teams should avoid treating the workspace as durable production storage.

Engineering Production contains approved, stable, recurring pipelines and durable outputs. All promoted "02_pipeline" notebooks should be tied to a data contract. A recurring Production pipeline may run on any required operational schedule, including annually, when the process needs to remain stable and repeatable.

Important "99_explore" work should be preserved when reproducibility is required. FabricOps may support an analysis archive or analysis packet in the future, but that should be treated as a future product direction rather than a current implemented production capability.

## Note ! FabricOps uses PySpark mainly 

Spark has startup overhead, and pandas may be better suited to smaller one-off analyses. FabricOps still uses PySpark as the standard for repeatable "02_pipeline" workflows because it supports larger datasets and provides a consistent engineering pattern for maintenance and handover.

This standard does not prevent teams from using pandas or other tools for appropriate exploration. It establishes the repeatable production pipeline pattern.
