# FabricOps Guided Demo

**The Guided Demo is a learning path that takes one FabricOps workflow from initial Fabric preparation through Development, governance, Production, and downstream consumption.**

Read [How FabricOps Works](how-fabricops-works.md) first for the architecture and operating model. Use [Notebook Templates](notebook-templates.md) for the notebook downloads.

## What you'll build

You will progressively take the same engineering pipeline through the FabricOps lifecycle:

```text
Set up → Govern → Engineer → Govern → Validate → Contract → Production → Consume
```

The learning path deliberately introduces governance in stages. Step 2 runs the full ETL before Guardrails exist. Step 3 reads the `METADATA_DATA_CATALOGUE` and `METADATA_DATA_PROFILED` records written by Engineering, then writes `METADATA_ENRICHMENT` and `METADATA_GUARDRAIL`. Step 4 reruns the same ETL with those Guardrails. Step 5 freezes approved expectations into a Data Contract. Step 6 runs the same engineering template in Production against the active contract.

!!! info "Four FabricOps concepts to know first"

    **FabricOps Starter Kit**, **Metadata**, **Governance as Code**, and **Configuration-driven Engineering** appear throughout this demo.

    Hover over a glossary term for its canonical short definition. Use the [FabricOps Glossary](glossary.md) when you want the full definition, category, aliases, or Microsoft Learn source where applicable.

## Learning path

| Module | Workspace | Notebook | What you do |
| --- | --- | --- | --- |
| 0A. Prepare Fabric artifacts | Governance, Engineering Development, Engineering Production, and required consumer workspaces | — | Create the Fabric items needed by the demo. |
| 0B. Set up the environment | Governance, Engineering Development, Engineering Production | `00_env_config` | Configure environment-aware Fabric routing. |
| 1. Establish governance context | Governance | `01_governance` | Create Data Stewards and a Data Agreement. |
| 2. Engineer and run a data pipeline | Engineering Development | `02_pipeline` | Run the complete ETL and write Data Catalogue, Data Profiled, Data Profiled Frequency where applicable, and Data Lineage records. |
| 3. Define Guardrails | Governance | `01_governance` | Read Data Catalogue and Data Profiled records, add Enrichment, and author Guardrails. |
| 4. Validate with Guardrails | Engineering Development | `02_pipeline` | Rerun the same ETL; the authored Guardrails now execute and write Guardrail Results. |
| 5. Create the Data Contract | Governance | `01_governance` | Freeze approved expectations into a versioned Data Contract and activate the Production version. |
| 6. Run Production with the active contract | Engineering Production | `02_pipeline` | Run the same engineering template against the frozen Production contract. |
| 99. Explore the data product | Project-Specific Consumer | `99_explore` | Consume governed Production data without duplicating the Production engineering workflow. |

## Start here

1. [Prepare Fabric artifacts](guided-demo/00A-setup-fabric-artifacts.md)
2. [Set up the operating environment](guided-demo/00B-run-environment-setup.md)
3. [Create data stewards and a data agreement](guided-demo/01-create-agreement.md)
4. [Module 2: Engineer and run a data pipeline](guided-demo/02-run-pipeline.md)
5. [Enrich the Data Catalogue and define Guardrails](guided-demo/03-enrich-guardrails.md)
6. [Rerun the Development pipeline with Guardrails](guided-demo/04-run-pipeline-with-guardrails.md)
7. [Create and activate the Data Contract](guided-demo/05-create-data-contract.md)
8. [Run Production with the active Data Contract](guided-demo/06-promote-to-production.md)
9. [Explore governed Production data](guided-demo/99-explore-via-notebook.md)

## How the same pipeline matures

![FabricOps role workflow](assets/fabricops-role-workflow.png)

### Step 2: baseline engineering

`02_pipeline` runs a complete Extract → Transform → Load flow and writes `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY` where applicable, and `METADATA_DATA_LINEAGE`. Guardrails are not expected yet because they have not been authored.

### Steps 3 and 4: add governance, then rerun

Step 3 reads `METADATA_DATA_CATALOGUE` and `METADATA_DATA_PROFILED`, then writes `METADATA_ENRICHMENT` and `METADATA_GUARDRAIL`. Step 4 returns to the same `02_pipeline`, evaluates those Guardrails, and writes `METADATA_GUARDRAIL_RESULTS` plus `METADATA_GUARDRAIL_ROW_RESULTS` where row-level failures are recorded.

### Steps 5 and 6: freeze and enforce Production expectations

Step 5 assembles a versioned Data Contract and activates the Production version. Step 6 runs Production against that frozen contract, keeping mutable Development authoring separate from Production enforcement.

!!! note "Promotion mechanism"

    The canonical **Promote** stage remains part of FabricOps. The standardised promotion mechanism is planned and may use Fabric deployment or pipeline approval, Git-based CI/CD, or a controlled manual approval-and-ferry process. The current demo assumes the Production notebook and data are made available through the organisation's current Fabric process.

## Live, Preview, and Planned content

Action pages use these maturity labels where implementation status matters:

???+ success "Live — validated demo component"

    Expanded by default. These components are part of the currently validated Guided Demo path.

??? info "Preview — implemented capability"

    Collapsed by default. These components are implemented and part of the intended FabricOps workflow, but are not yet part of the fully validated baseline demo path.

??? note "Planned — workflow direction"

    Collapsed by default. These items describe planned operating workflow that is not yet implemented end to end in the demo.
