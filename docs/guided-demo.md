# FabricOps Guided Demo

**The Guided Demo is the step-by-step execution path from initial Fabric preparation to governed Production consumption.**

Read [How FabricOps Works](how-fabricops-works.md) first for the architecture and operating model. Use [Notebook Templates](notebook-templates.md) for the notebook downloads.

## Required execution sequence

| Lifecycle stage | Workspace | Notebook | Maintained action page |
| ---- | --------- | -------- | ---------------------- |
| 0A | Governance, Engineering Development, Engineering Production, and any required Project-Specific Consumer workspaces | — | [Prepare Fabric artifacts](guided-demo/00A-setup-fabric-artifacts.md) |
| 0B | Governance, Engineering Development, and Engineering Production | `00_env_config` | [Set up the operating environment](guided-demo/00B-run-environment-setup.md) |
| 1. Governance — Create Data Stewards and Data Agreements | Governance | `01_governance` | [Create data stewards and a data agreement](guided-demo/01-create-agreement.md) |
| 2. Engineering — ETL, profile data, and build the Data Catalogue | Engineering Development | `02_pipeline` | [Run the first Development pipeline](guided-demo/02-run-pipeline.md) |
| 3. Governance — Enrich the Data Catalogue and define guardrails | Governance | `01_governance` | [Enrich catalogue evidence and define guardrails](guided-demo/03-enrich-guardrails.md) |
| 4. Engineering — Re-validate ETL with guardrails | Engineering Development | `02_pipeline` | [Rerun the Development pipeline with guardrails](guided-demo/04-run-pipeline-with-guardrails.md) |
| 5. Governance — Create the Data Contract and prepare for promotion | Governance | `01_governance` | [Create the Data Contract and prepare for promotion](guided-demo/05-create-data-contract.md) |
| 6. Engineering — Promote to Production | Engineering Production | Promoted `02_pipeline` | [Promote the validated pipeline to Production](guided-demo/06-promote-to-production.md) |
| 7. Consumer — Use approved Production data directly | Project-Specific Consumer | `99_explore` | [Consume approved Production data with FabricOps IO and profiling](guided-demo/99-explore-via-notebook.md) |

## Workflow overview

**Prepare → Govern → Engineer → Validate → Contract → Promote → Consume**

![FabricOps role workflow](assets/fabricops-role-workflow.png)

### Preparation

Step 0 is split into two stages:

- **0A** creates the required Fabric workspaces, lakehouses, warehouses, Environment, installed FabricOps wheel, and copied notebook templates.
- **0B** configures `00_env_config` and creates or validates the Governance metadata tables.

### Promotion

Governance creates the Data Contract in Step 5 and prepares the ETL contract and governance sign-off. Step 6 promotes the validated `02_pipeline` from Engineering Development into Engineering Production.

### Consumption

After approved Production outputs are available, Step 7 uses `99_explore` in one or more project-specific consumer workspaces for exploration, AI, and BI consumption.

!!! note "Consumer workspaces stay downstream"

    Consumer workspaces read approved Engineering Production data. They do not replace or duplicate the governed production pipeline.

## Start the demo

[Prepare Fabric artifacts](guided-demo/00A-setup-fabric-artifacts.md)
