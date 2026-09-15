# FabricOps Guided Demo

**Use the Guided Demo to experience the complete FabricOps operating loop, not just the notebook templates in isolation.**

`00A` and `00B` prepare the Fabric environment and load the demo data. The seven numbered steps then follow the same lifecycle described in [How FabricOps Works](how-fabricops-works.md): Governance establishes context, Engineering builds the real pipeline, Governance turns observed tables into a Data Contract, Engineering validates it, Governance activates it, Production runs it, and consumers use the approved output.

!!! tip "New to Microsoft Fabric?"

    Start with [Microsoft Learn: Fabric fundamentals](https://learn.microsoft.com/en-us/fabric/fundamentals/) for the platform concepts used throughout the demo. When you reach the engineering parts, continue with [Microsoft Learn: Fabric Data Engineering](https://learn.microsoft.com/en-us/fabric/data-engineering/) for Lakehouse, notebooks, Spark, and Data Engineering workflows.

    **Useful visual reference:** [Microsoft Fabric Visual Notes](https://www.slideshare.net/slideshow/microsoft-fabric-complete-handwritten-notes-pdf/289496813) — a visual community reference covering Fabric architecture, PySpark, pipelines, incremental loading, data quality, CI/CD, monitoring, and related concepts.

    FabricOps documentation remains the source of truth for how this starter kit is designed and used.

## Foundation setup

| Setup | What you do | Why it matters |
| --- | --- | --- |
| [0A. Prepare Fabric artifacts](guided-demo/00A-setup-fabric-artifacts.md) | Create the workspaces, stores, Fabric Environment, notebook copies, schemas, and upload the supplied demo files. | Everything required by the walkthrough exists physically in Fabric. |
| [0B. Configure the environment and load demo data](guided-demo/00B-run-environment-setup.md) | Configure `00_env_config`, create the metadata tables, then land the baseline managed source tables. | `01_governance` and `02_pipeline` can work against real configured Fabric stores and real managed tables. |

The baseline Orders source starts with the 120 rows in `orders.csv`. Keep `orders_incremental.csv` aside as the later **Day 2** arrival used to demonstrate how the same full-read pipeline behaves when source data changes.

## The seven-step FabricOps workflow

| Step | Notebook | What you learn |
| --- | --- | --- |
| [1. Establish Governance context](guided-demo/01-create-agreement.md) | `01_governance` | Create Data Stewards and a Data Agreement, then inspect the rows FabricOps persisted in the Governance metadata Lakehouse. |
| [2. Build and run the ETL](guided-demo/02-run-pipeline.md) | `02_pipeline` | Run the real full-read Read → Transform → Write workflow before any Data Contract exists. See checks safely skip in Development, multiple sources feed multiple targets, and each target remains independently publishable. |
| [3. Author and freeze the Data Contract](guided-demo/03-enrich-guardrails.md) | `01_governance` | Select the real `table_id`, add Enrichment, Guardrails, and Processing, review the complete definition, then freeze an immutable version. |
| [4. Select and validate the Data Contract](guided-demo/04-run-pipeline-with-guardrails.md) | `02_pipeline` | Select the frozen version and rerun the same pipeline so the checks that previously skipped now enforce the authored contract. |
| [5. Link the Data Agreement and activate](guided-demo/05-create-data-contract.md) | `01_governance` | Link the tested contract version to the correct Data Agreement version and activate it for Production. |
| [6. Promote and run Production](guided-demo/06-promote-to-production.md) | `02_pipeline` | Promote the validated pipeline logic and run it with Production `00_env_config`; FabricOps resolves the active contract automatically. |
| [7. Consume approved Production data](guided-demo/99-explore.md) | `99_explore` | Read approved Production outputs without recreating the Production engineering workflow. |

The core loop is therefore:

**Governance → Engineering → Governance → Engineering → Governance → Production → Consume**

The notebooks remain only `00_env_config`, `01_governance`, `02_pipeline`, and `99_explore`. The seven steps describe how those notebooks are reused through the lifecycle.

## Why Step 2 is the centrepiece

The Guided Demo deliberately teaches `02_pipeline` before introducing a Data Contract. This makes the value of FabricOps visible in layers:

1. Engineering can already use the reusable orchestrators and configured stores.
2. `pipeline_read()` resolves each source and its canonical `table_id`.
3. Guardrail checks are still called, but in Development they safely return `skipped` when no Data Contract is selected.
4. `profile_table()` records the real physical table evidence Governance needs.
5. Project transformation stays normal PySpark.
6. Independent Write blocks publish different targets and record exact source-to-target Lineage.
7. Governance then authors the Data Contract against tables that actually exist.
8. The same `02_pipeline` is rerun and the previously skipped checks become governed enforcement.

By the end of the demo, the user should understand not only which functions to call, but **how FabricOps connects environment configuration, engineering, metadata, governance, Data Contracts, validation, Production, and consumption into one repeatable operating practice.**

## The demo data story

Use the supplied Orders fixtures as a simple two-run story:

```text
Day 1
orders.csv = 120 rows
        ↓
02_pipeline full read
        ↓
multiple transformed targets

Day 2
append orders_incremental.csv = 12 new source rows
        ↓
source.demo.orders = 132 rows
        ↓
02_pipeline still performs a full read
        ↓
target behaviour depends on each target's load strategy
```

This separation is important: **full read describes how `02_pipeline` reads governed sources. Load strategy describes how each target is published.** An overwrite target replaces its persisted result, an append target adds rows, and governed SCD strategies apply their own key and history semantics.

The main walkthrough uses sequential independent Write blocks because that is the canonical and easiest-to-debug notebook pattern. Where independent target writes are orchestrated concurrently by Fabric or Spark, treat that as execution optimisation around the same Write blocks rather than a different FabricOps contract.

## Start

[Begin with 0A: Prepare Fabric artifacts](guided-demo/00A-setup-fabric-artifacts.md)
