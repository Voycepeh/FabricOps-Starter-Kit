# FabricOps documentation

FabricOps connects governance, data engineering, and AI or BI analytics through one standardized Microsoft Fabric workflow.

Governance defines ownership, agreements, enrichment, and guardrails. Engineering develops pipelines and captures metadata evidence. Approved pipelines are promoted to Production, where they provide stable and governed data products for downstream AI and BI consumption.

## What is FabricOps?

FabricOps, short for Fabric Operations, is a plug-and-play, lightweight starter kit that helps data teams across three main roles:

- Governance
- Data engineering
- AI and BI analytics

It helps these teams quickly set up and adopt an out-of-the-box workflow within the Microsoft Fabric platform.

## What is included?

FabricOps consists of:

- A Python package containing out-of-the-box helper and orchestrator functions
- Standardized Python notebook templates that weave these functions into reusable workflows
- A shared metadata model that connects governance and engineering activities
- A guided demo to help teams understand and adopt the workflow quickly
- Technical documentation for the notebook templates, metadata tables, and individual functions

## What problem does it solve?

By standardizing these workflows, FabricOps ensures that essential metadata and governance processes are built directly into engineering pipelines.

This provides the AI and BI consumption layer with a stable, governed, and reusable data foundation to work from.

## Choose what to open next

### Understand the operating model

Read [How FabricOps Works](how-fabricops-works.md) for the three-workspace architecture, notebook responsibilities, metadata handoffs, governance review, production promotion, and downstream consumption.

### Run the workflow

Follow the [Guided Demo](guided-demo.md), the canonical step-by-step execution guide for what to create, configure, open, run, and inspect.

### Implement with notebook templates

Use the [Notebook Templates](notebook-templates-implementation-guide/index.md) guide to download `00_env_config`, `01_agreement`, `02_pipeline`, `03_review`, and `99_explore` and understand each notebook's responsibility.

### Look up technical details

- [Metadata Table Reference](reference/metadata.md): table purposes, schemas, and ownership
- [DQ Rule Reference](reference/dq-rules/index.md): supported rule types and parameters
- [Function Reference](reference/index.md): callable behaviour and implementation detail

### Maintain or release FabricOps

Use the [Maintainer Guide](maintainer/index.md) for repository maintenance and release preparation. Maintainers should preserve the terminology and workflow defined in the [canonical product narrative](maintainer/product-narrative.md).
