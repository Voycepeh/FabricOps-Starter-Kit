# How FabricOps works

<div class="cta-center">
  <a class="md-button md-button--primary" href="../guided-demo/">Open the Guided Demo</a>
</div>

![FabricOps operating model overview](assets/fabricops-operating-model-overview.png)

FabricOps connects governance, data engineering, and AI and BI analytics through governed, quality-checked, Microsoft Fabric notebook workflows. The operating model keeps governance intent, engineering evidence, and production approval connected through shared metadata.

## The three-workspace operating model

| Workspace | Primary purpose | Main outcome |
| --------- | --------------- | ------------ |
| Governance | Define ownership, agreements, enrichment, guardrails, and approval | Governed intent |
| Engineering Development | Explore, develop, profile, test, and review | Evidence-backed pipeline |
| Engineering Production | Run approved pipelines and retain trusted outputs | Stable data product |

The three workspaces provide separation without creating disconnected handoffs. Governance defines the rules and approval context, Development builds and validates the pipeline, and Production runs the approved recurring workflow for downstream AI and BI use.

![FabricOps role workflow](assets/fabricops-role-workflow.png)

## The governance and engineering loop

The operating flow uses only the three core FabricOps workspaces: Governance, Engineering Development, and Engineering Production.

1. **Set up the operating environment** — Create the Fabric workspaces, create the required lakehouses and warehouses, configure a "00_env_config" notebook in every workspace, and create the metadata tables in the Governance workspace.

2. **Governance workflow 1** — In the Governance workspace, use "01_agreement" to create data stewards and create a data agreement between data stewards.

3. **Engineering workflow 1** — In the Engineering Development workspace, use "02_pipeline" to extract, transform, and load data from one data store to another. Profile source and target tables, then write data catalogue, data profiled, and data lineage metadata.

4. **Governance workflow 2** — In the Governance workspace, use "03_review" to pick from the data catalogue table, add descriptions and classifications to selected tables, and define guardrails such as schema enforcement and data quality.

5. **Engineering workflow 2** — In the Engineering Development workspace, use "02_pipeline" to wire in the guardrail rules defined during review, then run the pipeline and make sure it fails or warns users as configured.

6. **Governance workflow 3** — In the Governance workspace, use "01_agreement" to pick from the data catalogue table, create a data contract linking the data tables to the data agreement, and get the data steward to sign off on the contract.

7. **Engineering workflow 3** — In the Engineering Production workspace, promote the "02_pipeline" that was completed in Engineering Development.

## Metadata created through the workflow

![FabricOps metadata model](assets/fabricops-metadata-model.png)

FabricOps metadata is created for four connected purposes:

- **Governance intent** records stewards, agreements, intended data use, and approval context.
- **Engineering evidence** records what the pipeline observed and produced, including catalogue, profiling, schema, lineage, and guardrail outcomes.
- **Review and control** records business enrichment, classifications, descriptions, and guardrails that the pipeline must respect.
- **Production approval** connects the validated pipeline, governed dataset, responsible stewards, and expected outputs through a data contract.

This model means metadata is captured through the workflow instead of being recreated manually after delivery.

## Development and Production

Engineering Development is used for exploration, development, profiling, testing, and review. Development data and temporary notebooks may be cleaned regularly, so teams should avoid treating the workspace as durable production storage.

Engineering Production contains approved, stable, recurring pipelines and durable outputs. All promoted "02_pipeline" notebooks should be tied to a data contract. A recurring Production pipeline may run on any required operational schedule, including annually, when the process needs to remain stable and repeatable.

## PySpark standardization

Spark has startup overhead, and pandas may be better suited to smaller one-off analyses. FabricOps still uses PySpark as the standard for repeatable "02_pipeline" workflows because it supports larger datasets and provides a consistent engineering pattern for maintenance and handover.

This standard does not prevent teams from using pandas or other tools for appropriate exploration. It establishes the repeatable production pipeline pattern.

## Optional consumption and analysis preservation

Smaller implementations may consume Production outputs directly, subject to the appropriate access controls. Larger implementations may introduce a separate consumption workspace when AI, BI, semantic model, access, capacity, or product ownership requirements justify it.

Important "99_explore" work should be preserved when reproducibility is required. FabricOps may support an analysis archive or analysis packet in the future, but that should be treated as a future product direction rather than a current implemented production capability.

## Related documentation

- Use the [Notebook Templates guide](notebook-templates-implementation-guide/) for notebook responsibilities and downloads.
- Use the [Guided Demo](guided-demo/) for maintained execution instructions.
- Use the [metadata reference](reference/metadata/) for table-level details.
- Use the [function reference](reference/) for Python APIs.
