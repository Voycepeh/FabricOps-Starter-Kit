# FabricOps product definition

**This is the maintainer-facing source of truth for FabricOps terminology, operating model, and product decisions.**

Public-facing documentation may shorten, visualize, or reorganize this content, but it must not introduce a conflicting product story or change the workflow meaning without first updating this page.

## What is FabricOps?

FabricOps, short for Fabric Operations, is a plug-and-play Data Engineering and Governance practice for Microsoft Fabric.

It gives teams a ready-to-adopt operating workflow across three main roles:

- Governance
- Data engineering
- AI and BI analytics

FabricOps combines planned workflows, standardized notebook templates, reusable notebook-facing functions, and a shared metadata model so Governance and Engineering activity is captured as part of the work itself rather than reconstructed afterwards.

The templates and functions guide users through the intended workflow while writing the relevant data products and supporting evidence into the configured Fabric workspaces, Lakehouses, Warehouses, and metadata tables. This includes governed context such as Data Agreements, Catalogue metadata, profiling, lineage, Enrichment, Guardrails, Guardrail Results, and Data Contracts where those capabilities are implemented in the workflow.

### What FabricOps includes

- a Python package containing helper and orchestrator functions
- standardized Python notebook templates that weave those functions into reusable workflows
- a shared metadata model connecting Governance intent with Engineering evidence
- an operating model for Engineering Development, Engineering Production, Governance, and Project-Specific Consumer workspaces
- a Guided Demo for learning and adopting the workflow
- technical documentation for notebook templates, metadata tables, data-quality rules, and individual functions

**The core product idea is to make the desired data practice executable.** Governance, metadata capture, quality checks, profiling, lineage, contract context, and governed persistence are designed into the planned workflow instead of being treated as separate after-the-fact documentation tasks.

This gives AI and BI consumers a stable, governed, and reusable Production data foundation.

## Canonical workflow

**Set up → Govern → Engineer → Govern → Validate → Contract → Promote → Consume**

| Step | Stage | Canonical workflow step |
| --- | --- | --- |
| 0 | Set up the operating environment | Create the Fabric workspaces and required stores, configure `00_env_config`, and create the metadata tables in Governance. |
| 1 | Governance — Create Data Stewards and Data Agreements | In `01_governance`, create Data Stewards and establish Data Agreements between accountable stewards. |
| 2 | Engineering — ETL, profile data, and build the Data Catalogue | In Engineering Development, use `02_pipeline` for ETL, profiling, Data Catalogue creation, and supporting Engineering evidence. |
| 3 | Governance — Enrich the Data Catalogue and define Guardrails | In `01_governance`, read the evidence written by `02_pipeline`, add Enrichment, and define Guardrails. |
| 4 | Engineering — Re-validate ETL with Guardrails | Rerun `02_pipeline` and confirm warning, blocking, and validation behaviour. |
| 5 | Governance — Create the Data Contract and prepare for promotion | In `01_governance`, assemble one complete, versioned Data Contract per governed table from an exact Data Agreement version and the governed metadata already produced through FabricOps. Governance currently selects one saved version as active through a manual interim activation step. |
| 6 | Engineering — Promote to Production | Promote the validated `02_pipeline` workflow from Engineering Development to Engineering Production through the organisation's approved promotion mechanism. The standardised FabricOps promotion mechanism is planned and may use Fabric deployment or pipeline approval, Git-based CI/CD, or a controlled manual approval-and-ferry process. |
| 7 | Consumer — Use approved Production data directly | Use `99_explore` in a Project-Specific Consumer workspace to consume approved Production data. |

## Canonical operating decisions

| Area | Canonical decision |
| --- | --- |
| Workspaces | FabricOps uses Governance, Engineering Development, Engineering Production, and Project-Specific Consumer workspaces where needed. |
| Governance | Governance defines ownership, Data Agreements, Enrichment, Guardrails, Data Contracts, and promotion approval. |
| Development | Engineering Development supports exploration, pipeline development, profiling, testing, and review. |
| Production | Engineering Production contains approved recurring pipelines and durable Production outputs. |
| Standard pipeline approach | PySpark is the standard for repeatable `02_pipeline` workflows. |
| Consumption | Project-Specific Consumer workspaces consume approved Production data for project-level AI, BI, analysis, and data science. |
| One-off analysis | Important `99_explore` work must be preserved when reproducibility is required. |

## Canonical `02_pipeline` operating model

FabricOps standardizes the governed boundaries around ETL without taking ownership of the engineer's business transformation logic.

**0. Environment → E. Extract → T. Transform → L. Load**

### 0. Environment

`00_env_config` establishes whether the pipeline is running in Engineering Development or Engineering Production and therefore which governed definitions apply.

- **Development** supports current authoring and testing, including testing a selected Data Contract.
- **Production** uses the approved active Data Contract as the governed runtime definition.

### E. Extract

Extract establishes the governed source inputs before transformation.

For one or more source table IDs, the pipeline:

- defines the source tables in play and whether each read is full or incremental
- resolves the applicable source Guardrails from the selected or active Data Contract, or from current Guardrail metadata during Development authoring
- checks source schema, freshness, and change state before the business-data read
- reads each source table into a DataFrame using the prepared read scope
- runs data-quality checks on the DataFrame being processed
- profiles and registers a source only when the DataFrame represents the complete physical table, updating the relevant Data Profiled and Data Lineage evidence

The governed preparation and check functions are table-scoped. Engineers compose multiple governed source and target flows by repeating the same pattern for each relevant table relationship, so one `02_pipeline` can contain multiple reads, transformations, and writes without requiring a single multi-table orchestration call.

A partial or incremental source DataFrame is processing scope, not a complete table profile. It must not replace the latest valid full-table source profile.

### T. Transform

Transform is intentionally user-defined.

The engineer applies the business logic required to turn validated source DataFrames into one or more target DataFrames. FabricOps governs the inputs and outputs around this step without prescribing the transformation itself.

When a transformation combines multiple source DataFrames, the engineer remains responsible for the business semantics of that combination. FabricOps continues to govern each source and target boundary independently, including the applicable Guardrails, processing scope, and persistence behaviour.

### L. Load

Load establishes the governed target outputs and persists them.

For one or more target table IDs, the pipeline:

- defines the target tables in play
- resolves the applicable target Guardrails and governed load strategy from the selected or active Data Contract, or from current Development authoring
- validates target schema and data quality before persistence
- records DQ outcomes so written data can be traced back to the relevant Guardrail Results evidence
- prepares the DataFrame for the governed load strategy and adds FabricOps audit, lifecycle, and other required technical columns
- writes the target using the applicable governed load behaviour
- reads the persisted target back as a complete table
- profiles and registers that complete persisted target, updating the relevant Data Profiled and Data Lineage evidence

Each governed target is prepared and written under its own resolved processing definition. The same table-scoped pattern can therefore be repeated for multiple targets in one notebook.

The governed load strategy controls how the target is maintained. It does not define the engineer's business transformation logic.

**FabricOps governs the boundaries around ETL rather than replacing ETL.** It standardizes environment resolution, contracts, Guardrails, metadata, profiling, lineage, and governed persistence while leaving transformation logic with the engineer.

## Product components

### Python package

Provides reusable FabricOps helpers and orchestrators for Fabric notebook workflows.

### Notebook templates

Provide the user-facing implementation pattern for configuring workspaces, creating Governance records, building pipelines, reviewing evidence, and exploring approved data. The templates make the planned FabricOps workflow visible and repeatable rather than hiding it behind a separate orchestration layer.

### Shared metadata model

Connects Governance intent with Engineering evidence. Data Catalogue, Data Profiled, Data Profiled Frequency, Data Lineage, Enrichment, Guardrails, Guardrail Results, and Data Agreement records feed the normal operating workflow. A Data Contract version freezes the governed expectation for one table; one version can be manually selected as active, and Production checks resolve their expectations from that active version. A standardised approval and promotion mechanism remains planned. Candidate implementation paths are Fabric deployment or pipeline approval, Git-based CI/CD, or a controlled manual approval-and-ferry process.

The metadata model is not only documentation. It is the persistent context that allows Governance, Engineering, Production validation, downstream consumers, and future AI-assisted workflows to reason from the same recorded evidence and decisions.

### Guided Demo and technical documentation

The Guided Demo owns maintained execution instructions and contextual implementation rationale. Technical documentation owns detailed notebook, metadata, and Python API contracts.

## Future product direction: AI-augmented workflows

**AI-assisted FabricOps workflows should augment governed human decisions, not replace them.** FabricOps is not itself an AI model or agent framework. Its opportunity is to use the structured context already captured through the workflow to make Governance, Engineering, and Consumption faster and more consistent.

Potential future AI-augmented workflows include:

- **Enrichment suggestions:** propose business names, descriptions, classifications, sensitivity or PII hints, domains, and usage notes from schema, profile, and governed context for steward review.
- **Data Quality and Guardrail authoring:** suggest relevant rule types and parameters from schema, profile distributions, source observations, and previous Guardrail Results while keeping authoring and approval human-controlled.
- **Data Contract review:** summarize what changed between contract versions, highlight changed Guardrails or processing definitions, and identify items requiring explicit review before activation.
- **Pipeline review:** inspect the planned `02_pipeline` flow and its resolved metadata to identify missing validation, profiling, lineage, or unsafe processing patterns before Production.
- **Failure explanation:** turn Guardrail Results and runtime evidence into a concise explanation of what failed, which governed rule caused it, and what Engineering should inspect next.
- **Change-impact analysis:** use contracts, lineage, profile history, and source observations to explain likely downstream impact before a source, target, or processing definition changes.
- **Governed discovery:** answer questions such as what produces a table, which assets depend on a source, or which governed datasets have quality issues using FabricOps metadata rather than inferred notebook context alone.
- **Consumer context preparation:** assemble a compact governed context package from active contracts, Catalogue metadata, lineage, profiles, and approved Production data for `99_explore`, BI, Data Agents, analytics, and data science work.

These capabilities are future direction unless separately implemented and documented. Human owners remain responsible for approval, activation, promotion, and Production decisions.

## Future product direction: analysis preservation

Engineering Development is intentionally disposable. When important `99_explore` work must be reproduced later, FabricOps should support an analysis archive or analysis packet that preserves enough context to understand and rerun the work.

!!! note "Future direction"

    This is not a fully implemented Production capability. The intended purpose is reproducibility: preserving the notebook, execution context, input references or extracts, outputs, ownership, and related Governance context at an appropriate level.

## Documentation page ownership

| Page | Owns |
| --- | --- |
| Product Definition | Canonical terminology, workflow, and product meaning. |
| README | Repository orientation. |
| Documentation home | Product introduction and navigation. |
| How FabricOps Works | Architecture and operating model. |
| Notebook Templates | Notebook responsibilities and downloads. |
| Guided Demo | Maintained execution instructions and contextual rationale. |
| Metadata and function reference | Detailed technical contracts. |

!!! important "Canonical terminology rule"

    Public pages may shorten or reorganize the Product Definition, but they must not introduce a conflicting workflow or terminology.
