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
| 1 | Governance workflow 1 | In Governance, use "01_agreement" to create data stewards and create a data agreement between data stewards. |
| 2 | Engineering workflow 1 | In Engineering Development, use "02_pipeline" for ETL between data stores, then profile source and target tables and write data catalogue, data profiled, and data lineage metadata. |
| 3 | Governance workflow 2 | In Governance, use "03_review" to pick from the data catalogue table, add descriptions and classifications, and define guardrails such as schema enforcement and data quality. |
| 4 | Engineering workflow 2 | In Engineering Development, use "02_pipeline" to wire in the guardrail rules and make sure the pipeline fails or warns users as configured. |
| 5 | Governance workflow 3 | In Governance, use "01_agreement" to pick from the data catalogue table, create a data contract linking the data tables to the data agreement, and get data steward sign-off. |
| 6 | Engineering workflow 3 | In Engineering Production, promote the "02_pipeline" that was completed in Engineering Development. |

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
