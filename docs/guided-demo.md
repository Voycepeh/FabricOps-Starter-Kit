# FabricOps Guided Demo

**The Guided Demo is the step-by-step execution path from initial Fabric preparation to Data Contract-backed validation in Development and Production.**

Read [How FabricOps Works](how-fabricops-works.md) first for the architecture and operating model. Use [Notebook Templates](notebook-templates.md) for the notebook downloads.

## Required execution sequence

| Lifecycle stage | Workspace | Notebook | Maintained action page |
| ---- | --------- | -------- | ---------------------- |
| 0A | Governance, Engineering Development, Engineering Production, and any required Project-Specific Consumer workspaces | — | [Prepare Fabric artifacts](guided-demo/00A-setup-fabric-artifacts.md) |
| 0B | Governance, Engineering Development, and Engineering Production | `00_env_config` | [Set up the operating environment](guided-demo/00B-run-environment-setup.md) |
| 1. Governance — Create Data Stewards and Data Agreements | Governance | `01_governance` | [Create data stewards and a data agreement](guided-demo/01-create-agreement.md) |
| 2. Engineering — ETL, profile data, and build the Data Catalogue | Engineering Development | `02_pipeline` | [Run the first Development pipeline](guided-demo/02-run-pipeline.md) |
| 3. Governance — Enrich the Data Catalogue and define Guardrails | Governance | `01_governance` | [Enrich catalogue evidence and define Guardrails](guided-demo/03-enrich-guardrails.md) |
| 4. Engineering — Validate with current or frozen Guardrails | Engineering Development | `02_pipeline` | [Rerun the Development pipeline with Guardrails](guided-demo/04-run-pipeline-with-guardrails.md) |
| 5. Governance — Assemble and activate a Data Contract | Governance | `01_governance` | [Create and activate the Data Contract](guided-demo/05-create-data-contract.md) |
| 6. Engineering — Run Production against the active Data Contract | Engineering Production | `02_pipeline` | [Run Production with the active Data Contract](guided-demo/06-promote-to-production.md) |
| 7. Consumer — Use Production data directly | Project-Specific Consumer | `99_explore` | [Consume Production data with FabricOps IO and profiling](guided-demo/99-explore-via-notebook.md) |

## Workflow overview

**Governance and Engineering Development work in a loop until the table is ready to be frozen into a Data Contract. Production then evaluates Guardrails from the one active Data Contract for that table.**

![FabricOps role workflow](assets/fabricops-role-workflow.png)

### Preparation

Step 0 is split into two stages:

- **0A** creates the required Fabric workspaces, lakehouses, warehouses, Environment, installed FabricOps wheel, and copied notebook templates.
- **0B** configures `00_env_config` and creates or validates the Governance metadata tables.

### Development validation

Development normally evaluates the current authored Guardrails in `METADATA_GUARDRAIL`. After a Data Contract exists, `widget_select_data_contract()` can select an exact frozen Data Contract version for that table so the same `check_schema()`, `check_freshness()`, `check_changes()`, and `check_dq()` calls can test the frozen expectations before Production use.

### Data Contract and Production validation

Step 5 assembles one versioned Data Contract for one governed `table_id` and uses the current manual activation widget to choose the version Production is authorised to use. Step 6 demonstrates the implemented Production rule: each governed table resolves exactly one active Data Contract and evaluates the frozen Guardrails from that contract.

!!! note "Approval and promotion are deferred"

    FabricOps does not yet provide the end-to-end approval and Development-to-Production promotion workflow in this demo. Use your current Fabric process to make the Production notebook and data available. We will return to approval and promotion when the Fabric GUI workflow is ready to be configured and demonstrated end to end.

### Consumption

After Production outputs are available, Step 7 uses `99_explore` in one or more Project-Specific Consumer workspaces for exploration, AI, and BI consumption.

!!! note "Consumer workspaces stay downstream"

    Consumer workspaces read Engineering Production data. They do not replace or duplicate the governed Production pipeline.

## Start the demo

[Prepare Fabric artifacts](guided-demo/00A-setup-fabric-artifacts.md)
