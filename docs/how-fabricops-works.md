# How FabricOps works

**FabricOps connects Governance, Engineering Development, Engineering Production, and project-specific consumer workspaces through one governed operating model.**

![FabricOps operating model overview](assets/fabricops-operating-model-overview.png)

FabricOps is designed so Governance defines the rules, Engineering produces the evidence and governed data, Production runs the approved workflow, and consumers use trusted Production outputs without recreating the engineering pipeline.

## The operating model at a glance

| Area | What happens |
| --- | --- |
| Governance | Define Data Stewards, Data Agreements, Enrichment, Guardrails, Data Contracts, and promotion approval. |
| Engineering Development | Explore, develop, validate, profile, and test repeatable `02_pipeline` workflows. |
| Engineering Production | Run approved recurring pipelines using the governed Production definition. |
| Project-Specific Consumer | Use approved Production data for exploration, AI, BI, analysis, and data science. |

The flow is deliberately separated by responsibility:

**Governance → Engineering Development → Governance review and contract → Engineering Production → Consumption**

The [Guided Demo](guided-demo.md) owns the implementation walkthrough. This page explains how the pieces fit together.

## Workspace model

### Governance

The Governance workspace owns the shared metadata and governance workflow. `01_governance` is used to establish accountable ownership, Data Agreements, Enrichment, Guardrails, and Data Contracts.

Governance consumes Engineering evidence instead of recreating it. Data Catalogue, profiling, lineage, and Guardrail Results are produced through the engineering workflow and then used as inputs to governance decisions.

### Engineering Development

Engineering Development is where pipelines are built and tested. Teams use `02_pipeline` to read governed sources, apply Guardrails, transform data, validate targets, write outputs, and record engineering evidence.

Development can use current authoring to develop or test new Guardrails and load definitions, or test against a selected Data Contract where appropriate.

### Engineering Production

Engineering Production runs approved, repeatable pipelines and stores durable Production outputs.

Production uses the approved active Data Contract as the governed definition for the pipeline. Promoted notebooks should not silently fall back to Development authoring.

### Project-Specific Consumer

Project-specific consumer workspaces use approved Production data without duplicating the Production engineering workflow. `99_explore` provides the project-level entry point for exploration, AI, BI, and data science.

!!! note "Trusted Production source"

    Consumer workspaces should consume approved Production data rather than recreate source, unified, or product pipelines in each project workspace.

## Governance and Engineering work as a loop

**FabricOps uses a governed loop between Governance and Engineering Development before a validated pipeline is promoted to Engineering Production.**

![FabricOps role workflow](assets/fabricops-role-workflow.png)

The lifecycle is:

1. **Set up the environment** — create the required workspaces and stores, configure `00_env_config`, and create the Governance metadata tables.
2. **Establish Governance intent** — define Data Stewards and Data Agreements.
3. **Engineer and observe** — develop the ETL workflow, profile data, build the Data Catalogue, and record lineage and validation evidence.
4. **Add Governance controls** — enrich the catalogue and define Guardrails using the Engineering evidence.
5. **Re-validate** — rerun the engineering workflow and confirm the Guardrails behave as intended.
6. **Freeze the governed definition** — create a versioned Data Contract for the governed table and select the approved version for Production use.
7. **Promote** — move the validated `02_pipeline` workflow into Engineering Production.
8. **Consume** — use approved Production data from project-specific consumer workspaces.

The loop matters because FabricOps does not treat governance as an after-the-fact documentation exercise. Governance expectations are fed back into the engineering workflow before promotion.

## The engineering model inside `02_pipeline`

FabricOps standardizes the boundaries around ETL with a simple operating model:

**0. Environment → E. Extract → T. Transform → L. Load**

### 0. Environment

`00_env_config` establishes the active environment and configured Fabric stores.

- **Development** supports current authoring and testing, including testing selected Data Contracts where needed.
- **Production** uses the approved active Data Contract as the governed runtime definition.

### E. Extract

Engineering identifies one or more source table identities, resolves the applicable governed expectations, validates the source, reads the required data, and records source evidence.

At a high level this includes schema, freshness, change detection, Data Quality, profiling, and lineage. Full-table profiles are recorded only when the DataFrame represents the complete physical table; an incremental processing slice is not treated as a complete source profile.

### T. Transform

Transformation is user-defined business logic.

FabricOps intentionally does not prescribe how the engineer should join, derive, aggregate, enrich, or reshape the data. It standardizes the governed inputs and outputs around that transformation.

### L. Load

Engineering identifies one or more target table identities, resolves the target Guardrails and governed load strategy, validates the transformed output, prepares technical and audit fields, writes the target, then reads the persisted target back for complete profiling and registration.

The governed load vocabulary is **overwrite, append, SCD1, and SCD2** where the selected target supports the required execution semantics.

!!! note "FabricOps governs the ETL boundaries"

    FabricOps standardizes environment resolution, Guardrails, Data Contracts, metadata, profiling, lineage, and governed writes. The engineer still owns the business transformation itself.

## Metadata is the shared foundation

**The Data Catalogue connects Governance intent with Engineering evidence.**

![FabricOps metadata model](assets/fabricops-metadata-model.png)

Engineering records observed facts about the data and pipeline. Governance adds the approved meaning and controls around those facts.

Key relationships are:

- **Data Stewards and Data Agreements** establish accountable ownership and the governed relationship.
- **Data Catalogue** identifies governed tables and columns.
- **Data Profiled and Data Profiled Frequency** record observed profiling evidence.
- **Data Lineage** records how governed tables relate through the engineering workflow.
- **Enrichment** adds governed descriptive context to catalogue records.
- **Guardrails and Guardrail Results** define and record validation expectations.
- **Data Contracts** freeze the approved governed definition used for controlled execution and Production.

`02_pipeline` writes Engineering evidence into the shared metadata model. `01_governance` reads that evidence to enrich, define Guardrails, and create Data Contracts. Governance does not create a duplicate copy of the observed Engineering records.

## Development and Production use the same model differently

### Development

Development is flexible by design. Engineers can explore, author, profile, test, and refine a pipeline before it becomes durable Production logic.

This is where new Guardrails and load definitions can be developed and validated against the actual data.

### Production

Production is intentionally stricter. The promoted pipeline runs from the approved governed definition and produces durable outputs for downstream consumers.

!!! important "Production rule"

    Promoted `02_pipeline` notebooks should be tied to an approved Data Contract and should use that governed definition at runtime.

## Consumer workspaces stay downstream of Production

Project-specific consumer workspaces provide a safe place for exploration and analytical work without becoming an alternative Production pipeline.

There may be many consumer workspaces, each aligned to a project, analytical product, or business use case. They consume approved Engineering Production data and can use `99_explore` for AI, BI, analysis, and data science.

Important exploratory work should be preserved when reproducibility is required. Repeatable data preparation that becomes operational should move back into the governed Engineering Development and Engineering Production workflow.

## Where to go next

- Use the [Guided Demo](guided-demo.md) for the maintained step-by-step implementation.
- Use [Notebook Templates](notebook-templates.md) to understand the responsibility of each FabricOps notebook.
- Use the [Metadata reference](reference/metadata.md) for detailed metadata-table contracts.
- Use the [Function Reference](reference/index.md) for exact public callable behavior.
