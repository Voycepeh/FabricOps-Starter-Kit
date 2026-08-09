# FabricOps product definition

This document is the maintainer-facing source of truth for the FabricOps product definition, terminology, operating model, and product decisions. Public-facing documentation may shorten, visualize, or reorganize this content for its intended audience, but it must not introduce a conflicting product story or change the meaning of the workflow without first updating this document.

## What is FabricOps?

FabricOps, short for Fabric Operations, is a plug-and-play, lightweight starter kit that helps data teams across three main roles:

- Governance
- Data engineering
- AI and BI analytics

It helps these teams quickly set up and adopt an out-of-the-box workflow within the Microsoft Fabric platform.

FabricOps consists of:

- A Python package containing out-of-the-box helper and orchestrator functions
- Standardized Python notebook templates that weave these functions into reusable workflows
- A shared metadata model that connects governance and engineering activities
- A guided demo to help teams understand and adopt the workflow quickly
- Technical documentation for the notebook templates, metadata tables, and individual functions

By standardizing these workflows, FabricOps ensures that essential metadata and governance processes are built directly into engineering pipelines. This provides the AI and BI consumption layer with a stable, governed, and reusable data foundation to work from.

## Canonical operating decisions

| Area | Canonical decision |
| ---- | ------------------ |
| Workspaces | FabricOps uses three core workspaces: Governance, Engineering Development, and Engineering Production. |
| Governance | Governance defines ownership, agreements, enrichment, guardrails, contracts, and promotion approval. |
| Development | Engineering Development supports exploration, pipeline development, profiling, testing, and review. |
| Production | Engineering Production contains approved recurring pipelines and durable production outputs. |
| Standard pipeline approach | PySpark is the standard for repeatable "02_pipeline" workflows. |
| Consumption | Smaller teams may consume Production directly; a separate consumption workspace is optional at larger scale. |
| One-off analysis | Development is disposable, so important analysis must be preserved when reproducibility is required. |

## Canonical workflow

FabricOps shows the operating flow through the three core workspaces only: Governance, Engineering Development, and Engineering Production.

| Step | Stage | Canonical workflow step |
| ---- | ----- | ----------------------- |
| 0 | Set up the operating environment | Create the Fabric workspaces, create the required lakehouses and warehouses, configure "00_env_config" in every workspace, and create the metadata tables in Governance. |
| 1 | Governance — Create Data Stewards and Data Agreements | In `01_governance`, create Data Stewards and establish Data Agreements between two accountable stewards. |
| 2 | Engineering — ETL, profile data, and build the Data Catalogue | In Engineering Development, use `02_pipeline` for ETL, profiling, and Data Catalogue and technical evidence creation. |
| 3 | Governance — Enrich the Data Catalogue and define guardrails | In `01_governance`, read the evidence written by `02_pipeline`, enrich the Data Catalogue, and define guardrails. |
| 4 | Engineering — Re-validate ETL with guardrails | Rerun `02_pipeline` and confirm warning, blocking, and validation behaviour. |
| 5 | Governance — Create the Data Contract and prepare for promotion | In `01_governance`, link governed Data Catalogues to the Data Agreement and prepare the ETL contract and governance sign-off for release management. |
| 6 | Engineering — Promote to Production | Promote the validated `02_pipeline` workflow from Development to Production. |
| 7 | Consumer — Use approved Production data directly | Use `99_explore` to consume approved Production data for analytics, AI, BI, or downstream project use. |

## Product components

The FabricOps Python package provides reusable helpers and orchestrators for Fabric notebook workflows. The notebook templates are the user-facing implementation pattern for configuring workspaces, creating agreements and contracts, building pipelines, reviewing evidence, and exploring data when needed.

The shared metadata model connects governance intent with engineering evidence. Governance and metadata processes are not after-the-fact documentation tasks; they are embedded into engineering pipelines so evidence, guardrail results, and approval context are captured as part of normal delivery.

The guided demo provides maintained execution instructions for learning the workflow. The technical documentation provides detailed contracts for notebook templates, metadata tables, and Python APIs.

## Future product direction: analysis preservation

The Engineering Development workspace is intentionally disposable. When important "99_explore" work must be reproduced later, FabricOps should support an analysis archive or analysis packet that preserves enough context to understand and rerun the work. This is a future product direction, not a fully implemented production capability.

The purpose of this future capability is reproducibility: preserving the notebook, execution context, input references or extracts, outputs, ownership, and related governance context at an appropriate level for the analysis.

## Documentation page ownership

- The Product Definition owns canonical terminology, workflow, and product meaning.
- The README owns repository orientation.
- The documentation home owns product introduction and navigation.
- How FabricOps Works owns architecture and the operating model.
- The Notebook Templates guide owns notebook responsibilities and downloads.
- The Guided Demo owns maintained execution instructions.
- Metadata and function reference pages own detailed technical contracts.

Public pages may shorten the product definition but must not introduce a conflicting workflow or terminology.
