# FabricOps documentation

FabricOps connects governance, data engineering, and AI or BI analytics through one standardized Microsoft Fabric workflow.

Governance defines ownership, agreements, enrichment, and guardrails. Engineering develops pipelines and captures metadata evidence. Approved pipelines are promoted to Production, where they provide stable and governed data products for downstream AI and BI consumption.

**Define governance requirements → Develop the pipeline → Capture metadata evidence → Review and enrich the catalogue → Enforce guardrails → Create a data contract → Promote to production → Consume the trusted data**

## Understand FabricOps

- [What is FabricOps?](#what-is-fabricops)
- [How FabricOps works](how-fabricops-works.md)
- [Architecture and workspace setup](how-fabricops-works.md#three-workspace-setup)

## Get started

- [Installation](guided-demo/setup-fabric-artifacts.md#4-upload-and-install-the-fabricops-wheel)
- [Workspace configuration](guided-demo/setup-fabric-artifacts.md)
- [Guided demo](guided-demo.md)

## Use the workflow

- [`00_env_config`](notebook-templates-implementation-guide/index.md#00_env_config)
- [`01_agreement`](notebook-templates-implementation-guide/index.md#01_agreement)
- [`02_pipeline`](notebook-templates-implementation-guide/index.md#02_pipeline)
- [`03_review`](notebook-templates-implementation-guide/index.md#03_governance)
- [`99_explore`](notebook-templates-implementation-guide/index.md#99_explore)
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
- [Guardrail](reference/metadata/metadata_guardrail.md)
- [Guardrail Results](reference/metadata/metadata_guardrail_results.md)

## What is FabricOps?

FabricOps, short for Fabric Operations, is a plug-and-play, lightweight starter kit that helps data teams across three main roles:

- Governance
- Data engineering
- AI and BI analytics

It helps these teams quickly set up and adopt an out-of-the-box workflow within the Microsoft Fabric platform.

FabricOps consists of a Python package, standardized Python notebook templates, a shared metadata model, a guided demo, and technical documentation. Together, these components build essential metadata and governance processes directly into engineering pipelines and provide downstream AI and BI consumers with a stable, governed, and reusable data foundation.
