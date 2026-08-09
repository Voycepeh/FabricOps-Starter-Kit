# FabricOps Guided Demo

The Guided Demo is the canonical step-by-step execution guide for FabricOps. It explains what to create, configure, open, run, and inspect from initial Fabric preparation through Production promotion and project-specific consumption.

Read [How FabricOps Works](how-fabricops-works.md) first for the architecture and operating model. Use [Notebook Templates](notebook-templates.md) as the notebook download and implementation handoff.

## Required execution sequence

| Step | Workspace | Notebook | Maintained action page |
| ---- | --------- | -------- | ---------------------- |
| 0A | Governance, Engineering Development, Engineering Production, and any required Project-Specific Consumer workspaces | — | [Prepare Fabric artifacts](guided-demo/00A-setup-fabric-artifacts.md) |
| 0B | Governance, Engineering Development, and Engineering Production | `00_env_config` | [Set up the operating environment](guided-demo/00B-run-environment-setup.md) |
| 1 | Governance | `01_governance` | [Create data stewards and a data agreement](guided-demo/01-create-agreement.md) |
| 2 | Engineering Development | `02_pipeline` | [Run the first Development pipeline](guided-demo/02-run-pipeline.md) |
| 3 | Governance | `01_governance` | [Review catalogue evidence and define guardrails](guided-demo/03-enrich-guardrails.md) |
| 4 | Engineering Development | `02_pipeline` | [Rerun the Development pipeline with guardrails](guided-demo/04-run-pipeline-with-guardrails.md) |
| 5 | Governance | `01_governance` | [Create the Data Contract and record steward sign-off](guided-demo/05-create-data-contract.md) |
| 6 | Engineering Production | Promoted `02_pipeline` | [Promote the validated pipeline to Production](guided-demo/06-promote-to-production.md) |
| 7 | Project-Specific Consumer | `99_explore` | [Consume approved Production data with FabricOps IO and profiling](guided-demo/99-explore-via-notebook.md) |

![FabricOps role workflow](assets/fabricops-role-workflow.png)

Step 0 is split into two preparation stages. Step 0A creates the required Fabric workspaces, lakehouses, warehouses, Environment, installed FabricOps wheel, and copied notebook templates. Step 0B configures `00_env_config` and creates or validates the Governance metadata tables.

Approval and promotion occur only after the Data Contract is signed off in Step 5. Step 6 promotes the validated `02_pipeline` from Engineering Development into Engineering Production.

After approved Production outputs are available, Step 7 uses `99_explore` in one or more project-specific consumer workspaces for exploration, AI, and BI consumption. Consumer workspaces read approved Engineering Production data and do not replace or duplicate the governed production pipeline.