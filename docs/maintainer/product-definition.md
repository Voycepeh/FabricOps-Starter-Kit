# FabricOps product definition

**This is the maintainer-facing source of truth for the FabricOps operating model, product meaning, boundaries, and product decisions.**

Public-facing documentation may shorten, visualize, or reorganize this content, but it must not introduce a conflicting product story or change the workflow meaning without first updating this page. Canonical term definitions are maintained in `docs/reference/_data/glossary.json` and surfaced through the [FabricOps Glossary](../glossary.md).

## What is FabricOps?

FabricOps, short for Fabric Operations, is a plug-and-play Data Engineering and Governance practice for Microsoft Fabric.

It gives teams a ready-to-adopt operating workflow across three main roles:

- Governance
- Data engineering
- AI and BI analytics

FabricOps combines planned workflows, standardized notebook templates, reusable notebook-facing functions, and a shared metadata model so Governance and Engineering activity is captured as part of the work itself rather than reconstructed afterwards.

The templates and functions guide users through the intended workflow while recording Data Agreements, Catalogue metadata, profiles, lineage, source observations, resolved read strategies, governed load strategies and parameters, Enrichment, Guardrails and their results, and Data Contracts in the configured Fabric workspaces and metadata tables where those capabilities are implemented.

### Four high-level FabricOps concepts

- [**FabricOps Starter Kit**](../glossary.md#fabricops-starter-kit) — the overall governed Data Engineering and Governance practice.
- [**Metadata**](../glossary.md#metadata) — the structured information that connects Governance intent with Engineering activity.
- [**Governance as Code**](../glossary.md#governance-as-code) — governance rules expressed in structured, repeatable form so they can be reviewed and consistently applied.
- [**Configuration-driven Engineering**](../glossary.md#configuration-driven-engineering) — reusable engineering behaviour controlled through configuration rather than repeatedly rewriting implementation code.

The [FabricOps Glossary](../glossary.md) carries the detailed FabricOps, Governance, and Engineering definitions. This page stays focused on what the product is and how it is intended to operate.

### What FabricOps includes

- a Python package containing helper and orchestrator functions
- standardized Python notebook templates that weave those functions into reusable workflows
- a shared metadata model connecting Governance intent with recorded profiles, lineage, source observations, resolved read strategies, governed load strategies and parameters, and Guardrail Results
- an operating model for Engineering Development, Engineering Production, Governance, and Project-Specific Consumer workspaces
- a Guided Demo for learning and adopting the workflow
- technical documentation for notebook templates, metadata tables, data-quality rules, and individual functions

**The core product idea is to make the desired data practice executable.** Governance, metadata capture, quality checks, profiling, lineage, contract context, and governed persistence are designed into the planned workflow instead of being treated as separate after-the-fact documentation tasks.

This gives AI and BI consumers a stable, governed, and reusable Production data foundation.

## Canonical workflow

**Author → Freeze → Select → Validate → Link Data Agreement → Activate → Promote → Run Production**

| Step | Stage | Canonical workflow step |
| --- | --- | --- |
| 0 | Set up the operating environment | Create the Fabric workspaces and required stores, configure `00_env_config`, and create the metadata tables in Governance. |
| 1 | Governance — Create Data Stewards and Data Agreements | In `01_governance`, create Data Stewards and establish Data Agreements between accountable stewards. |
| 2 | Engineering Development — ETL, profile, and catalogue | Build and run `02_pipeline`, profile and catalogue governed tables, and capture Data Lineage and technical observations. |
| 3 | Governance — Author and freeze the Data Contract | Select the governed `table_id`, author descriptive Enrichment and enforced Guardrails, review the schema and processing definition, and freeze an immutable table-centric version. Do not link a Data Agreement at authoring time. |
| 4 | Engineering Development — Select and validate | Use the current notebook's `METADATA_DATA_LINEAGE` to discover linked `table_id` values, select one frozen version independently per table, and validate the ETL. Failed validation returns to Step 3 for a new frozen version. |
| 5 | Governance — Link the Data Agreement and activate | Select the tested frozen version, explicitly link the required exact Data Agreement version, and activate the contract for Production. |
| 6 | Engineering Production — Promote, run, and hand off access | Promote and run the validated `02_pipeline`. Production automatically resolves the active Data Contract, publishes governed outputs, and approved consumers receive access through native Fabric controls. |
| 7 | Consumption — Consume and productize governed data | Use `99_explore` as the consumer and analytics-engineering handoff: review governed context, discover existing consumption products, consume data directly, or publish to a target such as a Fabric Data Agent. |

## Canonical operating decisions

| Area | Canonical decision |
| --- | --- |
| Workspaces | FabricOps uses Governance, Engineering Development, Engineering Production, and Project-Specific Consumer workspaces where needed. |
| Governance | Governance defines ownership, Data Agreements, Enrichment, Guardrails, Data Contracts, and promotion approval. |
| Development | Engineering Development supports exploration, pipeline development, profiling, testing, and review. |
| Production | Engineering Production contains approved recurring pipelines and durable Production outputs. |
| Standard pipeline approach | PySpark is the standard for repeatable `02_pipeline` workflows. |
| Consumption | Approved consumers can use native Fabric permissions and interfaces directly. `99_explore` is the governed handoff for analytics and AI consumers, exposing reusable context and consumption accelerators without replacing native Fabric access. |
| Consumption products | FabricOps should surface existing products that use the same or overlapping governed tables before creating another. Data Agent publishing is the first automated target; Power BI and other consumers remain parallel paths. |

## Canonical engineering boundary

`02_pipeline` is the repeatable engineering workflow. FabricOps governs the boundaries around the engineer's transformation rather than replacing the transformation itself.

- **Read:** resolve the governed source, apply source-side checks, read the data, and capture the applicable profile, lineage, and source evidence.
- **Transform:** remains project-specific engineering logic.
- **Write:** apply target-side checks and the governed load strategy, persist the target, then capture the resulting profile, lineage, and runtime evidence.
- **Ownership:** one governed target `table_id` has one owning pipeline/notebook writer.

Detailed read/write sequencing, source-observation behaviour, load-strategy mechanics, and API contracts belong in the Guided Demo and technical/reference documentation rather than this product definition.

## Product components

### Python package

Provides reusable FabricOps helpers and orchestrators for Fabric notebook workflows.

### Notebook templates

Provide the user-facing implementation pattern for configuring workspaces, creating Governance records, building pipelines, and reviewing Data Catalogue, profile, lineage, source observation, Guardrail Result, and contract records. The templates make the planned FabricOps workflow visible and repeatable rather than hiding it behind a separate orchestration layer.

### Shared metadata model

Connects Governance intent with recorded Engineering metadata. Data Catalogue, Data Profiled, Data Profiled Frequency, Data Lineage, Source Observation, Enrichment, Guardrails, Guardrail Results, and Data Agreement records feed the normal operating workflow. A Data Contract version freezes the governed expectation for one table, including its processing definition. Development validates frozen versions; Governance links the tested version to an exact Data Agreement version and activates it; the validated engineering artifact is promoted through the Fabric Deployment Pipeline; Production resolves the active contract.

The metadata model is not only documentation. It is the persistent context that allows Governance, Engineering, Production validation, downstream consumers, and future AI-assisted workflows to reason from the recorded Catalogue structure, profiles, lineage, source observations, Guardrail definitions and results, Data Agreements, Data Contracts, and governance decisions.

### Guided Demo and technical documentation

The Guided Demo owns maintained execution instructions and contextual implementation rationale. Technical documentation owns detailed notebook, metadata, and Python API contracts. The Glossary owns user-facing term definitions and organizes them into FabricOps, Governance, and Engineering concepts.

## AI-assisted capabilities

AI augments governed human decisions rather than replacing them.

Implemented capabilities include:

- **AI-assisted Data Contract authoring:** governed schema and profile evidence can be used to suggest descriptions, grain, and sensitive-data context for human review.
- **Business Rules to Data Quality:** plain-language requirements can be translated into supported deterministic DQ rules, with constrained custom PySpark boolean expressions only when needed.
- **Single-table Fabric Data Agent publishing:** an activated Production `table_id` can be resolved into deterministic consumer context and used to create and configure a native Fabric Data Agent without copying governed metadata by hand.

Classification, treatment, contract approval, activation, promotion, and Production decisions remain human-governed.

## Active product direction

The active next product direction is **governed consumption**.

`99_explore` keeps its current name and evolves into the handoff from governed Production data to analytics and AI consumers. Native Fabric permissions remain the access mechanism; FabricOps adds reusable consumer-facing context derived from existing authoritative metadata.

The first implemented automated accelerator is **single-table Fabric Data Agent publishing**: select an activated Production table, assemble its governed context, configure the native Data Agent, and leave it ready for review and testing. Consumption-product registration and overlap discovery remain later work.

Multi-table consumption will require explicit, reusable relationship context. FabricOps can provide deterministic relationship evidence, but a human confirms relationship intent. Consumption-product discovery should surface overlap without assuming that overlapping products are automatically duplicates.

Data Agents are the first planned automated destination, not the definition of consumption. Direct notebooks, SQL, Lakehouses, Warehouses, Power BI, reporting, and future consumers can reuse the same governed Production foundation.

## Documentation page ownership

| Page | Owns |
| --- | --- |
| Product Definition | Canonical product meaning, operating workflow, boundaries, and product decisions. |
| Glossary | Canonical user-facing term definitions and the FabricOps / Governance / Engineering concept grouping. |
| README | Repository orientation. |
| Documentation home | Product introduction and navigation. |
| How FabricOps Works | Architecture and operating model. |
| Notebook Templates | Notebook responsibilities and downloads. |
| Guided Demo | Maintained execution instructions, step-specific concept guidance, and contextual rationale. |
| Metadata and function reference | Detailed technical contracts. |

!!! important "Canonical terminology rule"

    Durable term definitions come from `docs/reference/_data/glossary.json`. Public pages may shorten a definition for context, but they must use the canonical term and must not introduce a conflicting meaning. Product workflow and operating decisions remain governed by this Product Definition.
