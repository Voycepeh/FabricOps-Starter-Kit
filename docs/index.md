# FabricOps documentation

FabricOps connects governance, data engineering, and AI or BI analytics through one standardized Microsoft Fabric workflow.

Governance defines ownership, agreements, enrichment, and guardrails. Engineering develops pipelines and captures metadata evidence. Approved pipelines are promoted to Production, where they provide stable and governed data products for downstream AI and BI consumption.

## Understand FabricOps

- [What is FabricOps?](#what-is-fabricops)
- [How FabricOps works](how-fabricops-works.md)
- [Architecture and workspace setup](how-fabricops-works.md#how-fabricops-works)

## Get started

- [Installation](guided-demo/setup-fabric-artifacts.md)
- [Workspace configuration](guided-demo/run-environment-setup.md)
- [Guided demo](guided-demo.md)

## Use the workflow

- [`00_env_config`](guided-demo/run-environment-setup.md)
- [`01_agreement`](guided-demo/create-agreement.md)
- [`02_pipeline`](guided-demo/run-pipeline.md)
- [`03_review`](guided-demo/review-guardrails.md)
- [`99_explore`](guided-demo/explore-metadata-outputs.md)
- [Production promotion](how-fabricops-works.md#engineering-production-workspace)

## Understand the metadata

- [Metadata model](reference/metadata.md)
- [Data Steward](reference/metadata/metadata_data_steward.md)
- [Data Agreement](reference/metadata/metadata_data_agreement.md)
- [Data Contract](reference/metadata/metadata_data_contract.md)
- [Data Catalogue](reference/metadata/metadata_data_catalogue.md)
- [Data Profiled](reference/metadata/metadata_data_profiled.md)
- [Lineage](reference/metadata/metadata_data_lineage.md)
- [Enrichment](reference/metadata/metadata_enrichment.md)
- [Guardrails](reference/metadata/metadata_guardrail.md)
- [Guardrail Results](reference/metadata/metadata_guardrail_results.md)
- [Data Access](reference/metadata/metadata_data_access.md)

## Technical reference

- [Public functions](reference/index.md)
- [Function call architecture](function-call-graph.md)
- [Notebook templates](notebook-templates-implementation-guide/index.md)
- [Troubleshooting](guided-demo/explore-metadata-outputs.md)

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

By standardizing these workflows, FabricOps ensures that essential metadata and governance processes are built directly into engineering pipelines.

This provides the AI and BI consumption layer with a stable, governed, and reusable data foundation to work from.
