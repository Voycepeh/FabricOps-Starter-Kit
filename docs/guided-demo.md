# FabricOps Guided Demo

**The Guided Demo is the step-by-step execution path from initial Fabric preparation to governed Development, Production, and downstream consumption.**

Read [How FabricOps Works](how-fabricops-works.md) first for the architecture and operating model. Use [Notebook Templates](notebook-templates.md) for the notebook downloads.

!!! info "Four FabricOps concepts to know first"

    **FabricOps Starter Kit** — the governed Data Engineering practice you are following through this demo.  
    **Metadata** — the structured information FabricOps records as the workflow runs.  
    **Governance as Code** — governance rules expressed in structured, repeatable form.  
    **Configuration-driven Engineering** — pipeline behaviour controlled through reusable configuration instead of repeatedly rewriting implementation code.

    You do **not** need to read the whole glossary before starting. Each demo step below highlights only the terms that matter for that step. Use the [FabricOps Glossary](glossary.md) whenever you need a definition.

## How to read the demo

Every action page uses the same maturity pattern so you can scan the complete workflow without expanding every implementation detail.

???+ success "Live — validated demo component"

    Expanded by default. These components are part of the currently validated Guided Demo path.

??? info "Preview — implemented capability"

    Collapsed by default. These components are implemented and part of the intended FabricOps workflow, but are not yet part of the fully validated baseline demo path.

??? note "Planned — workflow direction"

    Collapsed by default. These items describe planned operating workflow that is not yet implemented end to end in the demo.

## Required execution sequence

| Lifecycle stage | Workspace | Notebook | Key concepts | Maintained action page |
| ---- | --------- | -------- | ------------ | ---------------------- |
| 0A | Governance, Engineering Development, Engineering Production, and any required Project-Specific Consumer workspaces | — | [Microsoft Fabric](glossary.md#microsoft-fabric), [Workspace](glossary.md#workspace), [Lakehouse](glossary.md#lakehouse), [Warehouse](glossary.md#warehouse) | [Prepare Fabric artifacts](guided-demo/00A-setup-fabric-artifacts.md) |
| 0B | Governance, Engineering Development, and Engineering Production | `00_env_config` | [Configuration](glossary.md#configuration), [Configuration-driven Engineering](glossary.md#configuration-driven-engineering), [Notebook](glossary.md#notebook) | [Set up the operating environment](guided-demo/00B-run-environment-setup.md) |
| 1. Governance — Create Data Stewards and Data Agreements | Governance | `01_governance` | [Data Steward](glossary.md#data-steward), [Data Agreement](glossary.md#data-agreement), [Metadata](glossary.md#metadata) | [Create data stewards and a data agreement](guided-demo/01-create-agreement.md) |
| 2. Engineering — ETL, profile data, and build the Data Catalogue | Engineering Development | `02_pipeline` | [Pipeline](glossary.md#pipeline), [Profile](glossary.md#profile), [Schema](glossary.md#schema), [Data Quality](glossary.md#data-quality) | [Run the Development pipeline](guided-demo/02-run-pipeline.md) |
| 3. Governance — Enrich the Data Catalogue and define Guardrails | Governance | `01_governance` | [Enrichment](glossary.md#enrichment), [Data Sensitivity](glossary.md#data-sensitivity), [Data Quality](glossary.md#data-quality), [Guardrails](glossary.md#guardrails) | [Enrich the Data Catalogue and define Guardrails](guided-demo/03-enrich-guardrails.md) |
| 4. Engineering — Validate with current or frozen Guardrails | Engineering Development | `02_pipeline` | [Guardrails](glossary.md#guardrails), [Enforcement](glossary.md#enforcement), [Guardrail Result](glossary.md#guardrail-result), [Incremental Load](glossary.md#incremental-load) | [Rerun the Development pipeline with Guardrails](guided-demo/04-run-pipeline-with-guardrails.md) |
| 5. Governance — Assemble and activate a Data Contract | Governance | `01_governance` | [Data Agreement](glossary.md#data-agreement), [Data Contract](glossary.md#data-contract), [Guardrails](glossary.md#guardrails), [Governance as Code](glossary.md#governance-as-code) | [Create and activate the Data Contract](guided-demo/05-create-data-contract.md) |
| 6. Engineering — Run Production against the active Data Contract | Engineering Production | `02_pipeline` | [Data Contract](glossary.md#data-contract), [Enforcement](glossary.md#enforcement), [Guardrail Result](glossary.md#guardrail-result) | [Run Production with the active Data Contract](guided-demo/06-promote-to-production.md) |
| 7. Consumer — Use Production data directly | Project-Specific Consumer | `99_explore` | [Data Access](glossary.md#data-access), [Workspace](glossary.md#workspace), [Profile](glossary.md#profile) | [Consume Production data with FabricOps IO and profiling](guided-demo/99-explore-via-notebook.md) |

## Workflow overview

**Set up → Govern → Engineer → Govern → Validate → Contract → Promote → Consume**

![FabricOps role workflow](assets/fabricops-role-workflow.png)

???+ success "Live — Preparation and baseline engineering"

    Step 0A prepares Fabric artifacts. Step 0B configures `00_env_config`. Step 1 establishes Data Stewards and a Data Agreement. Step 2 executes the currently validated IO, transformation, profiling, registration, and lineage patterns inside the canonical `02_pipeline` lifecycle.

???+ success "Live — Governance authoring"

    Step 3 reads Data Catalogue, Data Profiled, and Data Lineage records written by Engineering, adds Enrichment, and authors Guardrails for the governed workflow.

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
