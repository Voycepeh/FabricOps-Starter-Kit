# FabricOps Starter Kit

FabricOps, short for **Fabric Operations**, is a plug-and-play, lightweight starter kit that helps governance, data engineering, and AI or BI analytics teams quickly set up and adopt an out-of-the-box workflow within Microsoft Fabric.

It combines a Python package containing helper and orchestrator functions, standardized Python notebook templates, a shared metadata model, and a guided demo.

By standardizing these workflows, FabricOps ensures that essential metadata and governance processes are built directly into engineering pipelines. This provides the AI and BI consumption layer with a stable, governed, and reusable data foundation to work from.

<div align="center">

[![Documentation Home](https://img.shields.io/badge/1._Documentation-Home-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/)

[![Notebook Templates](https://img.shields.io/badge/4._Notebook-Templates-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/notebook-templates-implementation-guide/)

[![View Releases](https://img.shields.io/badge/View-Releases-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/releases/)

</div>

## Who this is for?

- Governance
- Data engineering
- AI and BI analytics

## What the starter kit includes

- A Python package containing out-of-the-box helper and orchestrator functions
- Standardized Python notebook templates that weave these functions into reusable workflows
- A shared metadata model that connects governance and engineering activities
- A guided demo to help teams understand and adopt the workflow quickly
- Technical documentation for the notebook templates, metadata tables, and individual functions

## Three-workspace setup

1. **Governance workspace** defines ownership, agreements, enrichment, and guardrails.
2. **Engineering Development workspace** is where pipelines are developed, tested, profiled, and reviewed.
3. **Engineering Production workspace** contains promoted and stable pipelines that produce trusted data for downstream AI and BI consumption.

## Complete workflow

**Define governance requirements → Develop the pipeline → Capture metadata evidence → Review and enrich the catalogue → Enforce guardrails → Create a data contract → Promote to production → Consume the trusted data**
