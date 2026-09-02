# FabricOps Guided Demo

**The Guided Demo is the practical, step-by-step path for running the FabricOps workflow from initial Fabric preparation through Governance, Engineering Development validation, Engineering Production, and downstream consumption.**

Read [How FabricOps Works](how-fabricops-works.md) first for the operating model and the Governance ↔ Engineering workflow. Use the [FabricOps Engineering Guide](reference/engineering-cheat-sheet.md) when you want the deeper reasoning behind `00_env_config`, I/O, Lakehouse/Warehouse choices, PySpark, and processing patterns.

!!! tip "New to Microsoft Fabric?"

    Start with [Microsoft Learn: Fabric fundamentals](https://learn.microsoft.com/en-us/fabric/fundamentals/) for the platform concepts used throughout the demo. When you reach the engineering parts, continue with [Microsoft Learn: Fabric Data Engineering](https://learn.microsoft.com/en-us/fabric/data-engineering/) for Lakehouse, notebooks, Spark, and Data Engineering workflows.

    **Useful visual reference:** [Microsoft Fabric Visual Notes](https://www.slideshare.net/slideshow/microsoft-fabric-complete-handwritten-notes-pdf/289496813) — a visual community reference covering Fabric architecture, PySpark, pipelines, incremental loading, data quality, CI/CD, monitoring, and related concepts.

    FabricOps documentation remains the source of truth for how this starter kit is designed and used.

## What you'll build

You will progressively take the same governed pipeline through the FabricOps lifecycle. **Steps 1–7 are the core FabricOps workflow; 0A and 0B prepare and configure the environment before that workflow begins.**

```mermaid
flowchart TB
    S0A["0A · Prepare<br/>Fabric artifacts"] --> S0B["0B · Configure<br/>00_env_config"]
    S0B --> S1["1 · Govern<br/>Data Stewards + Data Agreement"]
    S1 --> S2["2 · Engineer<br/>ETL + Profile + Catalogue + Lineage"]
    S2 --> S3["3 · Enrich<br/>Enrichment + Guardrails"]
    S3 --> S4["4 · Validate<br/>02_pipeline tests governed expectations"]
    S4 --> PASS{"Ready to freeze?"}
    PASS -- "No · refine" --> S3
    PASS -- "Yes" --> S5["5 · Data Contract lifecycle<br/>Freeze → Test → Activate"]
    S5 --> FROZEN{"Frozen version passes?"}
    FROZEN -- "No · refine and freeze a new version" --> S3
    FROZEN -- "Yes" --> S6["6 · Promote / Run<br/>Engineering Production"]
    S6 --> S7["7 · Consume<br/>99_explore from Production"]

    classDef focal fill:#f2eff8,stroke:#6750a4,stroke-width:2px,color:#20242d;
    class S3,S4,S5 focal;
```

The diagram makes the non-linear part explicit: **Steps 3, 4, and 5 form the Governance ↔ Engineering iteration.** Governance refines the governed definition in Step 3, Engineering validates it in Step 4, and Step 5 freezes and tests an immutable version. If either validation shows the definition is not ready, the workflow returns to Governance for refinement before a new version is frozen. Only an approved activated version continues to Production.

The demo is intentionally action-oriented. Each module tells you what to do, what you should see, and what FabricOps records at that stage.

<!-- SCREEN-RECORDING SLOT: Optional 20-30 second demo orientation -->

## Learning path

| Module | Workspace | Notebook | What you do | What FabricOps records / proves |
| --- | --- | --- | --- | --- |
| [0A. Prepare Fabric artifacts](guided-demo/00A-setup-fabric-artifacts.md) | Governance, Engineering Development, Engineering Production, and required consumer workspaces | — | Create the Fabric items needed by the demo. | The operating environment exists and is ready for the notebook workflow. |
| [0B. Set up the operating environment](guided-demo/00B-run-environment-setup.md) | Governance, Engineering Development, Engineering Production | `00_env_config` | Configure environment-aware Fabric routing and create or validate the Governance metadata tables. | Logical stores resolve to the correct environment-specific Fabric items. |
| [1. Data Stewards and Data Agreement](guided-demo/01-create-agreement.md) | Governance | `01_governance` | Create provider and recipient Data Stewards and a Data Agreement. | The governed sharing relationship is established. |
| [2. ETL, Profile, and Catalogue](guided-demo/02-run-pipeline.md) | Engineering Development | `02_pipeline` | Run the complete ETL for the governed target. | Data Catalogue, Data Profiled, Data Profiled Frequency where applicable, and Data Lineage records are written for the governed `table_id`. |
| [3. Enrich Catalogue and define Guardrails](guided-demo/03-enrich-guardrails.md) | Governance | `01_governance` | Read the Engineering metadata, add Enrichment, and author Guardrails. | The governed definition for the same `table_id` is enriched with business context and enforceable expectations. |
| [4. Validate with Guardrails / Data Contract](guided-demo/04-run-pipeline-with-guardrails.md) | Engineering Development | `02_pipeline` | Rerun the same ETL with current Guardrails or a selected frozen Data Contract. | Guardrail Results and row-level results where applicable prove whether the governed expectations pass. |
| [5. Freeze, test, and activate the Data Contract](guided-demo/05-create-data-contract.md) | Governance + Engineering Development | `01_governance` + `02_pipeline` | Freeze an immutable version, test it in Development, obtain governance sign-off, and activate the approved version. | One approved frozen Data Contract version is selected for Production resolution. |
| [6. Run the Production pipeline](guided-demo/06-promote-to-production.md) | Engineering Production | `02_pipeline` | Promote the validated pipeline using the organisation's deployment process, resolve the active Data Contract, and run the governed Production pipeline. | Production executes against the active frozen contract. |
| [7. Consume approved Production data](guided-demo/99-explore-via-notebook.md) | Project-Specific Consumer | `99_explore` | Consume approved Production data without duplicating the Production engineering workflow. | Downstream BI, AI, data science, and exploration use the trusted Production source. |

## How to use each module

Each action page should stay practical and use the same rhythm:

1. **What you are doing** — the purpose of the step in one sentence.
2. **Do this** — the actual notebook, widget, or Fabric action.
3. **What you should see** — the expected result, supported by a screenshot or short real screen recording where motion matters.
4. **What FabricOps recorded** — the metadata, result, or governed state created by the step.
5. **Go deeper** — link back to [How FabricOps Works](how-fabricops-works.md) for the operating concept or the [Engineering Guide](reference/engineering-cheat-sheet.md) for technical reasoning.

The Guided Demo should not repeat long architecture or engineering explanations. Those concepts live on the pages above so this path can stay focused on doing the work.

## The iterative part of the demo

The same Step 3 → Step 4 → Step 5 loop shown above is the part of the demo that may repeat while the governed definition is being refined:

```mermaid
flowchart TB
    G["3 · Governance refines<br/>Enrichment + Guardrails"] --> E["4 · Engineering validates<br/>in 02_pipeline"]
    E --> D{"Governed expectations pass?"}
    D -- "No" --> G
    D -- "Yes" --> F["5 · Freeze immutable<br/>Data Contract version"]
    F --> T["Test frozen version<br/>in Engineering Development"]
    T --> FD{"Frozen version passes?"}
    FD -- "No · refine and freeze a new version" --> G
    FD -- "Yes" --> A["Governance activates<br/>approved version"]
    A --> P["6 · Engineering Production"]

    classDef focal fill:#f2eff8,stroke:#6750a4,stroke-width:2px,color:#20242d;
    class F,A focal;
```

Repeat the author-and-validate loop until the governed expectations are ready to freeze, test, approve, and activate.

For the conceptual explanation of this loop and the Data Contract lifecycle, see [How FabricOps Works](how-fabricops-works.md#the-governance-and-engineering-loop).

## Promotion mechanism

!!! note "Promotion remains separate from contract activation"

    The canonical **Promote** stage remains part of FabricOps. The standardised promotion mechanism is planned and may use Fabric deployment or pipeline approval, Git-based CI/CD, or a controlled manual approval-and-ferry process.

    The current demo assumes the validated `02_pipeline` is made available in Engineering Production through the organisation's current Fabric process before the Production run.

## Live, Preview, and Planned content

Action pages use these maturity labels where implementation status matters:

???+ success "Live — validated demo component"

    Expanded by default. These components are part of the currently validated Guided Demo path.

??? info "Preview — implemented capability"

    Collapsed by default. These components are implemented and part of the intended FabricOps workflow, but are not yet part of the fully validated baseline demo path.

??? note "Planned — workflow direction"

    Collapsed by default. These items describe planned operating workflow that is not yet implemented end to end in the demo.
