# FabricOps Guided Demo

**Run the current FabricOps operating workflow using the four notebook templates that ship with the starter kit: `00_env_config`, `01_governance`, `02_pipeline`, and `99_explore`.**

Read [How FabricOps Works](how-fabricops-works.md) first if you want the operating model before the hands-on walkthrough. This Guided Demo stays practical and follows the notebooks as they exist today.

## The current notebook flow

FabricOps does not use a separate notebook for every governance or engineering stage. The workflow is intentionally concentrated into four reusable notebooks.

| Notebook | Where it runs | What you do |
| --- | --- | --- |
| [`00_env_config`](guided-demo/00-env-config.md) | Governance, Engineering Development, Engineering Production | Configure the Fabric Environment, logical stores, metadata target, and reusable runtime context. Seed the demo data used by the walkthrough. |
| [`01_governance`](guided-demo/01-governance.md) | Governance | Create Data Stewards and a Data Agreement. After Engineering produces catalogue and profile evidence, return here to author, freeze, and later activate the Data Contract. |
| [`02_pipeline`](guided-demo/02-run-pipeline.md) | Engineering Development, then Engineering Production | Run the full-read governed pipeline: select the contract context, read complete governed sources, run checks and profiling, transform in PySpark, enforce target guardrails, write using the governed load strategy, and profile the persisted target. |
| [`99_explore`](guided-demo/99-explore.md) | Optional support / project-specific exploration | Read and inspect configured Fabric data, use exploratory profiling and catalogue views, and troubleshoot without replacing the governed delivery path. |

The required delivery loop is:

**`01_governance` → `02_pipeline` → `01_governance`**

`00_env_config` supplies the shared environment context used by those notebooks. `99_explore` is optional support.

## What you will do

1. Configure the Fabric workspaces, stores, Environment, metadata target, and demo inputs through the `00_env_config` walkthrough.
2. Open `01_governance` and establish the steward and agreement context.
3. Run `02_pipeline` in Engineering Development so the real governed tables are read, checked, profiled, transformed, and published.
4. Return to `01_governance`, select the resulting `table_id`, author Enrichment, Guardrails, and processing requirements, then freeze the immutable Data Contract version.
5. Return to `02_pipeline`, select the frozen version in Development, rerun the pipeline, and validate it against the governed definition.
6. Return to `01_governance`, link the tested contract version to the required Data Agreement version and activate it for Production.
7. Promote the validated `02_pipeline` through your organisation's Fabric deployment process and run it in Engineering Production. Production resolves the active contract automatically.
8. Use `99_explore` only when you need read-oriented discovery, profiling, catalogue inspection, or troubleshooting around the governed workflow.

This is one Governance ↔ Engineering lifecycle, not a chain of separate FabricOps notebooks for each state change.

## Before you start

Prepare the Fabric items required by your environment. For the full workspace pattern this normally means Governance, Engineering Development, Engineering Production, and any project-specific consumer workspaces. A small demo can place the required items in one workspace.

For the supplied demo story, create or configure:

- a Governance metadata Lakehouse,
- a Source Lakehouse,
- a Unified Lakehouse,
- a Product Warehouse,
- the Fabric Environment containing the FabricOps wheel,
- copies of the four notebook templates from [`templates/notebooks`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks),
- the demo files from [`templates/DemoData`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/DemoData).

The walkthrough uses logical store names such as `source`, `unified`, `product`, and `metadata`. They are examples configured in `00_env_config`, not mandatory FabricOps naming conventions.

## Start the walkthrough

[Start with `00_env_config`](guided-demo/00-env-config.md)

Need conceptual context instead of instructions? Read [How FabricOps Works](how-fabricops-works.md). Need an exact function signature? Use the [Function Reference](reference/index.md).
