# Module 2: Engineer and run a data pipeline

**Use the pre-wired `02_pipeline` template to run a complete FabricOps ETL in Engineering Development.**

**Approx. 30 min · 5 units · Engineering Development**

The goal of this module is not to assemble FabricOps function by function. The `02_pipeline` template already wires the standard pipeline lifecycle around your project-specific source, transformation, target, and processing configuration.

At the end of this module, you will have run a complete ETL and produced the observed metadata that Governance uses in Step 3.

!!! info "Why Guardrails are skipped in this first run"

    No Guardrails or Data Contract have been created for the demo table yet. That is expected.

    The ETL still runs end to end. In Step 3 you define Guardrails from the observed metadata, Step 4 reruns this same pipeline with those Guardrails, Step 5 freezes approved expectations into a Data Contract, and Step 6 runs the same pipeline in Production against the active contract.

## Learning objectives

By the end of this module, you'll be able to:

- understand what the `02_pipeline` template already handles for you,
- run a complete Extract → Transform → Load flow with demo data,
- configure Lakehouse or Warehouse sources and targets,
- keep project-specific transformation logic visible in the intended notebook section,
- choose Full Dataset, Incremental Watermark, or Incremental Partition processing when required,
- review the target, profile, catalogue, and lineage evidence produced by the run.

## Prerequisites

Before starting this module:

- complete [Step 0A: Prepare Fabric artifacts](00A-setup-fabric-artifacts.md),
- complete [Step 0B: Set up the operating environment](00B-run-environment-setup.md),
- complete [Step 1: Create data stewards and a data agreement](01-create-agreement.md),
- upload the demo source files to the Source Lakehouse under `Files/DemoData/`.

## Module units

| Unit | What you'll learn |
| --- | --- |
| [1. Understand the `02_pipeline` template](02-run-pipeline/understand-template.md) | See what FabricOps wires automatically and what remains project-owned. |
| [2. Run the baseline ETL](02-run-pipeline/run-baseline-etl.md) | Execute the complete development ETL before any Guardrails exist. |
| [3. Configure sources](02-run-pipeline/configure-sources.md) | Use Lakehouse files/tables or Warehouse tables/SQL without hardcoded Fabric routing. |
| [4. Transform and load](02-run-pipeline/transform-and-load.md) | Add project logic and write to Lakehouse or Warehouse targets. |
| [5. Choose processing behaviour and review results](02-run-pipeline/processing-and-results.md) | Understand full/incremental processing and inspect the metadata handoff to Governance. |

## The learning-path story

```text
Step 2
Run the full ETL
No Guardrails exist yet
        ↓
Step 3
Review observed metadata
Define Guardrails
        ↓
Step 4
Run the same ETL again
Guardrails now execute
        ↓
Step 5
Freeze approved expectations
into a Data Contract
        ↓
Step 6
Run the same ETL in Production
against the active contract
```

The important point is that FabricOps does not require a separate basic pipeline, Guardrail pipeline, and Production pipeline. The same engineering template progresses through a governed lifecycle as governance state is added around it.

## Start the module

[Start Unit 1: Understand the `02_pipeline` template](02-run-pipeline/understand-template.md)

Need an exact function signature or parameter instead of the learning path? Use the [Function Reference](../reference/index.md).

**Previous:** [Step 1: Create data stewards and a data agreement](01-create-agreement.md)  
**Next after completing this module:** [Step 3: Enrich the Data Catalogue and define Guardrails](03-enrich-guardrails.md)
