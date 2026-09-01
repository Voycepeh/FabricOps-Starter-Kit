# FabricOps Guided Demo

**The Guided Demo is a learning path that takes one FabricOps workflow from initial Fabric preparation through Governance, Engineering Development validation, Engineering Production, and downstream consumption.**

Read [How FabricOps Works](how-fabricops-works.md) first for the architecture and operating model. Use [Notebook Templates](notebook-templates.md) for the notebook downloads.

!!! tip "New to Microsoft Fabric?"

    Start with [Microsoft Learn: Fabric fundamentals](https://learn.microsoft.com/en-us/fabric/fundamentals/) for the platform concepts used throughout the demo. When you reach the engineering parts, continue with [Microsoft Learn: Fabric Data Engineering](https://learn.microsoft.com/en-us/fabric/data-engineering/) for Lakehouse, notebooks, Spark, and Data Engineering workflows.

    FabricOps documentation remains the source of truth for how this starter kit is designed and used.

## What you'll build

You will progressively take the same governed pipeline through the FabricOps lifecycle:

```text
Prepare → Configure → Govern → Engineer → Enrich → Validate → Freeze/Test/Activate → Promote/Run → Consume
```

The learning path deliberately introduces governance in stages. Step 2 runs the full ETL before Guardrails exist. Step 3 reads the `METADATA_DATA_CATALOGUE` and `METADATA_DATA_PROFILED` records written by Engineering, then writes `METADATA_ENRICHMENT` and `METADATA_GUARDRAIL`. Step 4 reruns the same `02_pipeline` with those Guardrails or a selected frozen Data Contract. Step 5 freezes an immutable Data Contract version, tests the frozen version in Development, and activates the approved version for Production. Step 6 promotes the validated `02_pipeline` into Engineering Production, resolves the active Data Contract, and runs the governed Production pipeline. Step 7 consumes only approved Production data from the project-specific consumer workspace.

!!! info "Four FabricOps concepts to know first"

    **FabricOps Starter Kit**, **Metadata**, **Governance as Code**, and **Configuration-driven Engineering** appear throughout this demo.

    Hover over a glossary term for its canonical short definition. Use the [FabricOps Glossary](glossary.md) when you want the full definition, category, aliases, or Microsoft Learn source where applicable.

## Learning path

Select a module name to continue through the demo in order.

| Module | Workspace | Notebook | What you do |
| --- | --- | --- | --- |
| [0A. Prepare Fabric artifacts](guided-demo/00A-setup-fabric-artifacts.md) | Governance, Engineering Development, Engineering Production, and required consumer workspaces | — | Create the Fabric items needed by the demo. |
| [0B. Set up the operating environment](guided-demo/00B-run-environment-setup.md) | Governance, Engineering Development, Engineering Production | `00_env_config` | Configure environment-aware Fabric routing and create or validate the Governance metadata tables. |
| [1. Data Stewards and Data Agreement](guided-demo/01-create-agreement.md) | Governance | `01_governance` | Create Data Stewards and a Data Agreement. |
| [2. ETL, Profile, and Catalogue](guided-demo/02-run-pipeline.md) | Engineering Development | `02_pipeline` | Run the complete ETL and write Data Catalogue, Data Profiled, Data Profiled Frequency where applicable, and Data Lineage records. |
| [3. Enrich Catalogue and define Guardrails](guided-demo/03-enrich-guardrails.md) | Governance | `01_governance` | Read Data Catalogue and Data Profiled records, add Enrichment, and author Guardrails. |
| [4. Validate with Guardrails / Data Contract](guided-demo/04-run-pipeline-with-guardrails.md) | Engineering Development | `02_pipeline` | Rerun the same ETL with current Guardrails or a selected frozen Data Contract and write Guardrail Results. |
| [5. Freeze, test, and activate the Data Contract](guided-demo/05-create-data-contract.md) | Governance + Engineering Development | `01_governance` + `02_pipeline` | Freeze an immutable Data Contract version, test the frozen version in Development, obtain governance sign-off, and activate the approved version. |
| [6. Run the Production pipeline](guided-demo/06-promote-to-production.md) | Engineering Production | `02_pipeline` | Promote the validated pipeline, resolve the active Data Contract, and run the governed Production pipeline. |
| [7. Consume approved Production data](guided-demo/99-explore-via-notebook.md) | Project-Specific Consumer | `99_explore` | Consume only approved Production data without duplicating the Production engineering workflow. |

## How the same pipeline matures

![FabricOps role workflow](assets/fabricops-role-workflow.png)

### Step 2: baseline engineering

`02_pipeline` runs a complete Extract → Transform → Load flow and writes `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY` where applicable, and `METADATA_DATA_LINEAGE`. Guardrails are not expected yet because they have not been authored.

### Steps 3 and 4: enrich, govern, then validate

Step 3 reads `METADATA_DATA_CATALOGUE` and `METADATA_DATA_PROFILED`, then writes `METADATA_ENRICHMENT` and `METADATA_GUARDRAIL`. Step 4 returns to the same `02_pipeline`, evaluates current Guardrails or a selected frozen Data Contract, and writes `METADATA_GUARDRAIL_RESULTS` plus `METADATA_GUARDRAIL_ROW_RESULTS` where row-level failures are recorded.

### Steps 5 and 6: freeze, test, activate, promote, then run

Step 5 freezes an immutable Data Contract version, tests that frozen version in Development, records governance sign-off, and activates the approved version for Production. Step 6 promotes the validated `02_pipeline` into Engineering Production, resolves the active Data Contract, and runs the governed Production pipeline against those frozen expectations.

### Step 7: consume approved Production data

Project-specific consumer workspaces use `99_explore` to consume approved data from Engineering Production for Power BI, AI, data science, exploration, and other project-level use without recreating the Production pipeline.

!!! note "Promotion mechanism"

    The canonical **Promote** stage remains part of FabricOps. The standardised promotion mechanism is planned and may use Fabric deployment or pipeline approval, Git-based CI/CD, or a controlled manual approval-and-ferry process. The current demo assumes the validated `02_pipeline` is made available in Engineering Production through the organisation's current Fabric process before the Production run.

## Live, Preview, and Planned content

Action pages use these maturity labels where implementation status matters:

???+ success "Live — validated demo component"

    Expanded by default. These components are part of the currently validated Guided Demo path.

??? info "Preview — implemented capability"

    Collapsed by default. These components are implemented and part of the intended FabricOps workflow, but are not yet part of the fully validated baseline demo path.

??? note "Planned — workflow direction"

    Collapsed by default. These items describe planned operating workflow that is not yet implemented end to end in the demo.
