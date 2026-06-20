# FabricOps Guided Demo

Use this walkthrough to run the FabricOps Starter Kit demo from workspace setup through metadata inspection. It focuses on the user journey: what to open, what to run, and what evidence to expect.

For the detailed contents and configurable settings inside each notebook, use [Template Notebooks](notebook-templates-implementation-guide/index.md). The [API Reference](reference/index.md) remains the source for reusable functions and classes.

## Overview

The guided demo builds a governed, quality-checked Microsoft Fabric notebook workflow around deterministic order and customer source data. You build the FabricOps wheel, create Fabric runtime items, configure shared routes, capture an agreement, generate demo source tables, run the pipeline, enrich metadata, review guardrails, and inspect the metadata outputs.

Keep the default demo values for your first run so the notebooks and expected metadata evidence line up.

| Default | Value |
| ------- | ----- |
| Source schema | `DemoTest` |
| Generated source table prefix | `demo_` |
| Happy path source tables | `demo_src_orders_happy` and `demo_src_customers_happy` |
| Default unified outputs | `demo_unified_orders_enriched` and `demo_unified_orders_summary` |

## Guided demo flow

## Run sequence

| Order | Step | What you do | What you should have afterward |
| ----- | ---- | ----------- | ------------------------------ |
| 1 | [Create Wheel](guided-demo/create-wheel.md) | Build the FabricOps wheel locally. | A `.whl` file ready for Fabric Environment upload. |
| 2 | [Setup Fabric Artifacts](guided-demo/setup-fabric-artifacts.md) | Create or choose the Fabric workspace, data items, Environment, wheel install, and copied notebooks. | A workspace where copied notebooks can import `fabricops_kit` and route to named runtime targets. |
| 3 | [Run Environment Setup](guided-demo/run-environment-setup.md) | Run `00_env_config` setup cells. | Shared `CONFIG` and `ENV` values plus registered metadata tables. |
| 4 | [Register Agreement](guided-demo/create-agreement.md) | Run `01_agreement` to capture owner, purpose, readiness, and evidence. | Agreement metadata that the pipeline can select. |
| 5 | [Run Example Pipeline Demo](guided-demo/run-pipeline.md) | Run `example_pipeline_demo` to create deterministic demo source tables and demo-scoped rules. | Demo source data and starter rule intent ready for pipeline execution. |
| 6 | [Run Pipeline](guided-demo/run-pipeline.md) | Run `02_pipeline`. | Governed outputs, profiles, guardrail outcomes, lineage, and run summaries. |
| 7 | [Review Governance](guided-demo/review-guardrails.md) | Use governance review widgets to enrich metadata and approve or update guardrail intent, then rerun the pipeline when needed. | Approved rules, enriched metadata, and fresh runtime results from active checks. |
| 8 | [Explore Metadata](guided-demo/explore-metadata-outputs.md) | Inspect generated metadata reference pages or use `99_explore` for troubleshooting. | Traceable answers about agreements, profiles, rules, lineage, and runs. |

## Success criteria

After the walkthrough, you should be able to answer these questions from metadata rather than notebook memory.

| Question | Metadata-backed answer |
| -------- | ---------------------- |
| Who owns the data and what is it used for? | Agreement and steward metadata from `01_agreement`. |
| What was profiled? | Catalogue evidence captured by `02_pipeline`. |
| Which transformations created the outputs? | Pipeline registration, lineage, output records, and run summaries. |
| Which expectations were reviewed? | Approved governance rows in `METADATA_GUARDRAIL_RULES` and enrichment review metadata. |
| Which checks ran during execution? | Runtime outcomes in guardrail results and pipeline run metadata. |

## Where to go for details

- Use [Template Notebooks](notebook-templates-implementation-guide/index.md) to understand notebook internals, editable settings, advanced options, validations, and downstream dependencies.
- Use [Metadata Tables](reference/metadata.md) to inspect the shape of stored evidence.
- Use [Function Reference](reference/index.md) only when you need helper-level API details.
