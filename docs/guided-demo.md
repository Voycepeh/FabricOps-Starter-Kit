# FabricOps Guided Demo

<div class="demo-hero" markdown>

Use this page as the journey map for the FabricOps Starter Kit guided demo in Microsoft Fabric. The detailed instructions now live on the individual step pages in the guided demo sidebar.

## Demo at a glance

This demo builds a governed, quality-checked Microsoft Fabric notebook workflow around deterministic order and customer source data. You prepare Fabric workspace items, configure notebook routing, create agreement metadata, generate demo source tables, run the pipeline template, enrich and review metadata, rerun with active guardrails, and inspect the evidence that explains what happened.

It is for data engineers, analytics engineers, data stewards, governance reviewers, and junior team members who need a practical handover path through FabricOps. Plan for a focused half-day the first time if you are also setting up Fabric workspaces and wheel installation; the notebook flow itself is shorter once your Fabric workspace, lakehouses, warehouse, and Environment are ready.

By the end, you should understand how FabricOps uses Fabric workspaces, lakehouses, notebooks, and metadata tables to make delivery traceable from data agreement through governed pipeline review. For the full operating model, read [How FabricOps Works](how-fabricops-works/index.md).

</div>

<div class="demo-learning-outcomes" markdown>

## What the guided demo teaches

- How `00_env_config` centralizes environment-specific Fabric routes and metadata targets.
- How `01_agreement` captures steward, agreement, and evidence metadata.
- How `example_pipeline_demo.ipynb` creates deterministic source scenarios for repeatable learning.
- How `02_pipeline` reads, transforms, validates, profiles, and writes governed outputs.
- How enrichment and governance review separate observed metadata from approved guardrail intent.
- How active guardrails are evaluated during later pipeline runs.
- How metadata outputs explain ownership, transformations, controls, lineage, and run outcomes.

</div>

<div class="demo-defaults" markdown>

## Demo defaults

Keep these defaults for your first pass so notebooks and expected metadata evidence line up.

| Default | Value |
| ------- | ----- |
| Source schema | `DemoTest` |
| Generated source table prefix | `demo_` |
| Happy path source tables | `demo_src_orders_happy` and `demo_src_customers_happy` |
| Default unified outputs | `demo_unified_orders_enriched` and `demo_unified_orders_summary` |
| Demo generator behavior | `example_pipeline_demo.ipynb` is safe to rerun and overwrites demo tables only. |

</div>

## Guided demo flow

Follow the pages in this order. Each page focuses on the work to perform in Fabric and the output or evidence produced by that step.

| Order | Page | Notebook or Fabric item | What it produces |
| ----- | ---- | ----------------------- | ---------------- |
| 1 | [Setup Fabric Workspace](guided-demo/setup-fabric-workspace.md) | Fabric workspaces, lakehouses, warehouse, Environment, and copied notebook templates | Fabric runtime items, installed FabricOps wheel, and editable notebook copies ready for the demo. |
| 2 | [Configure Environment](guided-demo/configure-environment.md) | `00_env_config` | Shared `CONFIG` and `ENV` values, configured metadata routing, and registered `METADATA_*` tables. |
| 3 | [Create Agreement](guided-demo/create-agreement.md) | `01_agreement` | Steward, agreement, and agreement evidence metadata for the demo workflow. |
| 4 | [Run Pipeline](guided-demo/run-pipeline.md) | `example_pipeline_demo` and `02_pipeline` | Deterministic demo source tables, governed unified outputs, profiles, guardrail outcomes, lineage, and run summaries. |
| 5 | [Enrich Metadata](guided-demo/enrich-metadata.md) | `02_pipeline` or `03_governance` enrichment widgets | Business context, classifications, and enrichment intent tied to observed catalogue evidence. |
| 6 | [Review Guardrails](guided-demo/review-guardrails.md) | `03_governance`, then optional `02_pipeline` rerun | Approved guardrail intent and runtime evidence from active guardrail enforcement. |
| 7 | [Explore Metadata Outputs](guided-demo/explore-metadata-outputs.md) | `99_explore` and generated metadata reference pages | Traceable answers about agreements, profiles, rules, lineage, pipeline runs, and final outputs. |

## What success looks like

After the full demo, the flow should replace tribal knowledge with metadata-backed answers.

| Question | Where the answer should come from |
| -------- | --------------------------------- |
| Who owns the data and what is it used for? | Agreement and steward metadata captured in `01_agreement`. |
| What source and target data was profiled? | Source and target profiles captured by `02_pipeline`, plus `99_explore` notes when used. |
| What transformations created the output? | Pipeline registration, lineage, and output metadata captured in `02_pipeline`. |
| Which schema, freshness, profile, DQ, or enrichment expectations were reviewed? | Governance metadata from `03_governance`, especially active rows in `METADATA_GUARDRAIL_RULES`. |
| Which production guardrails ran? | Runtime evidence from `02_pipeline` guardrail checks, DQ enforcement, output writes, lineage, and run summaries. |
| What should support use after production? | Stored production notebook export, metadata evidence, final output tables, run summaries, and support notes. |

The goal is that support and review should no longer depend on memory or side conversations. The metadata should explain who owns the data, how it was transformed, which controls were approved, what evidence exists from the run, and which final outputs were published.

## Next reads

| Page | Why read it |
| ---- | ----------- |
| [Setup Fabric Workspace](guided-demo/setup-fabric-workspace.md) | Prepare the Fabric workspace items, Environment, wheel, and copied notebooks before the notebook flow. |
| [Environment Configuration](how-fabricops-works/environment-config.md) | Understand how `00_env_config` controls configured runtime targets and metadata routing. |
| [List of Templates](how-fabricops-works/notebook-templates.md) | Learn each notebook responsibility and handoff. |
| [Pipeline Guardrails](how-fabricops-works/pipeline-guardrails.md) | Learn how `02_pipeline` owns schema, freshness, DQ, profile behavior, and run evidence. |
| [Governance Review](how-fabricops-works/governance-review.md) | Learn how `03_governance` reviews and records approved guardrail intent. |
| [List of Metadata Tables](reference/metadata-tables/index.md) | See how observed evidence, approved intent, and runtime outcomes stay separated. |
| [Function Reference](reference/index.md) | Review the reusable helper APIs used by the notebook templates. |
