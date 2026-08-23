# FabricOps Guided Demo

**The Guided Demo is the step-by-step execution path from initial Fabric preparation to governed Development, Production, and downstream consumption.**

Read [How FabricOps Works](how-fabricops-works.md) first for the architecture and operating model. Use [Notebook Templates](notebook-templates.md) for the notebook downloads.

## How to read the demo

Every action page uses the same maturity pattern so you can scan the complete workflow without expanding every implementation detail.

???+ success "Live — validated demo component"

    Expanded by default. These components are part of the currently validated Guided Demo path.

??? info "Preview — implemented capability"

    Collapsed by default. These components are implemented and part of the intended FabricOps workflow, but are not yet part of the fully validated baseline demo path.

??? note "Planned — workflow direction"

    Collapsed by default. These items describe planned operating workflow that is not yet implemented end to end in the demo.

## Required execution sequence

| Lifecycle stage | Workspace | Notebook | Maintained action page |
| ---- | --------- | -------- | ---------------------- |
| 0A | Governance, Engineering Development, Engineering Production, and any required Project-Specific Consumer workspaces | — | [Prepare Fabric artifacts](guided-demo/00A-setup-fabric-artifacts.md) |
| 0B | Governance, Engineering Development, and Engineering Production | `00_env_config` | [Set up the operating environment](guided-demo/00B-run-environment-setup.md) |
| 1. Governance — Create Data Stewards and Data Agreements | Governance | `01_governance` | [Create data stewards and a data agreement](guided-demo/01-create-agreement.md) |
| 2. Engineering — ETL, profile data, and build the Data Catalogue | Engineering Development | `02_pipeline` | [Run the Development pipeline](guided-demo/02-run-pipeline.md) |
| 3. Governance — Enrich the Data Catalogue and define Guardrails | Governance | `01_governance` | [Enrich catalogue evidence and define Guardrails](guided-demo/03-enrich-guardrails.md) |
| 4. Engineering — Validate with current or frozen Guardrails | Engineering Development | `02_pipeline` | [Rerun the Development pipeline with Guardrails](guided-demo/04-run-pipeline-with-guardrails.md) |
| 5. Governance — Assemble and activate a Data Contract | Governance | `01_governance` | [Create and activate the Data Contract](guided-demo/05-create-data-contract.md) |
| 6. Engineering — Run Production against the active Data Contract | Engineering Production | `02_pipeline` | [Run Production with the active Data Contract](guided-demo/06-promote-to-production.md) |
| 7. Consumer — Use Production data directly | Project-Specific Consumer | `99_explore` | [Consume Production data with FabricOps IO and profiling](guided-demo/99-explore-via-notebook.md) |

## Workflow overview

**Set up → Govern → Engineer → Govern → Validate → Contract → Promote → Consume**

![FabricOps role workflow](assets/fabricops-role-workflow.png)

???+ success "Live — Preparation and baseline engineering"

    Step 0A prepares Fabric artifacts. Step 0B configures `00_env_config`. Step 1 establishes Data Stewards and a Data Agreement. Step 2 executes the currently validated IO, transformation, profiling, registration, and lineage patterns inside the canonical `02_pipeline` lifecycle.

???+ success "Live — Governance authoring"

    Step 3 reads Engineering evidence, adds Enrichment, and authors Guardrails for the governed workflow.

??? info "Preview — Guarded Development lifecycle"

    Step 4 applies the newer governed runtime path around the same visible ETL flow: source observation, schema/freshness/change checks, `skip`/`full`/`incremental` preparation, DQ checks, governed target preparation, and selected frozen Data Contract testing.

??? info "Preview — Data Contract activation and Production runtime"

    Step 5 creates the versioned Data Contract and currently uses manual activation for the Production version. Step 6 demonstrates active-contract Production resolution and frozen Guardrail/processing behaviour.

??? note "Planned — Promotion workflow"

    The canonical **Promote** stage remains part of FabricOps. The standardised promotion mechanism is planned and may use Fabric deployment or pipeline approval, Git-based CI/CD, or a controlled manual approval-and-ferry process. The current demo assumes the Production notebook and data are made available through the organisation's current Fabric process.

???+ success "Live — Consumption"

    Step 7 uses `99_explore` in a Project-Specific Consumer workspace to read governed Production data for exploration, AI, BI, and analysis without duplicating the Production engineering workflow.

## Start the demo

[Prepare Fabric artifacts](guided-demo/00A-setup-fabric-artifacts.md)
