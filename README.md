# FabricOps Starter Kit

FabricOps Starter Kit helps teams run governed Fabric notebook workflows by turning governance intent, profiling evidence, DQ rules, pipeline outputs, and lineage into a metadata-backed data contract.

<div align="center">

[![Open Documentation](https://img.shields.io/badge/Start%20Here-FabricOps%20Starter%20Kit-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/)

</div>


## Documentation deployment configuration

Docs deployment uses a branch-based GitHub Pages flow that publishes the generated MkDocs `site/` output to the `gh-pages` branch. In repository **Settings → Pages**, set:

- **Source**: Deploy from a branch
- **Branch**: `gh-pages`
- **Folder**: `/` (root)

## Why this starter kit exists

![Before vs after using the starter kit](docs/assets/before-after.png)

Fabric notebooks often begin as analysis work and then become recurring operations. This starter kit gives teams a role-based operating model where governance is defined once, analysts validate DQ rule validity, engineers enforce approved metadata, and handover/data contract outputs are generated from metadata and evidence.

Read more: [Quick Start](https://voycepeh.github.io/FabricOps-Starter-Kit/quick-start/) · [Workflow](https://voycepeh.github.io/FabricOps-Starter-Kit/workflow/) · [Functions](https://voycepeh.github.io/FabricOps-Starter-Kit/reference/) · [Data contracts](https://voycepeh.github.io/FabricOps-Starter-Kit/metadata-and-contracts/)

## What users get

![Benefits of the FabricOps Starter Kit](docs/assets/framework-benefits.png)

Reusable templates and callable functions for a runnable end-to-end flow: 01 governance agreement, 02 profiling/DQ validation, 03 pipeline enforcement, and handover/data contract export.

<div align="center">

[![Config Template](https://img.shields.io/badge/Template-Env%20Config-blue?style=for-the-badge)](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks/00_env_config.ipynb)

[![Da Template](https://img.shields.io/badge/Template-Agreement%20Template-blue?style=for-the-badge)](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks/01_da_agreement_template.ipynb)

[![Exploration Notebook Template](https://img.shields.io/badge/Template-Exploration%20Template-blue?style=for-the-badge)](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks/02_ex_agreement_topic.ipynb)
[![Pipeline Contract Template](https://img.shields.io/badge/Template-Pipeline%20Template-blue?style=for-the-badge)](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks/03_pc_agreement_pipeline_template.ipynb)

[![Gov Template](https://img.shields.io/badge/Template-Governance%20Template-blue?style=for-the-badge)](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks/04_gov_agreement_dataset_table.ipynb)

[![Function Reference](https://img.shields.io/badge/Reference-Callable%20Functions-purple?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/reference/)
</div>

## Design choices

### Fabric-first

FabricOps Starter Kit is inspired by open data contracts, DQX-style data quality checks, metadata registries, and lineage patterns, but adapts those ideas to Microsoft Fabric realities.

In Fabric, teams must operate across Lakehouses, Warehouses, OneLake paths, workspace separation, dev-to-prod promotion, and cross-store or cross-workspace movement that often needs explicit notebook code.

### Notebook-first

Many Fabric data products begin as notebooks. This kit does not try to replace notebooks with a full orchestration, governance, or data platform product; it makes notebooks more repeatable, reviewable, and handover-ready.

The model separates exploration notebooks that capture profiling, reasoning, and AI-assisted suggestions from pipeline notebooks that enforce approved logic, quality checks, classifications, and output contracts.

### Contract-first and metadata-first

Contracts are not standalone documents only. In this kit, contracts connect to notebook naming, approved usage, schema expectations, data quality rules, sensitivity review, metadata profiling, and output registration.

This pattern is inspired by open data contract approaches, adapted to Fabric-native storage and execution.

### DQX-inspired, Fabric-native quality checks

The quality-check model is inspired by DQX-style reusable rule definitions and rule application, but implemented for Fabric notebooks, Spark DataFrames, and metadata tables.

AI may help suggest rules, humans approve them, and pipeline notebooks enforce them.

### AI-assisted with human approval

- Step 2 Governance: AI suggests, human approves.
- Step 4 DQ: AI applies/suggests, human validates rule validity.
- Step 6 Handover: AI generates from approved metadata and evidence.

### Handover-first

The goal is not only to make one notebook run. The goal is to make the data product understandable to the next engineer, analyst, reviewer, or owner.

## Scope

This is a Fabric-first notebook starter kit.
It is not a full data platform, orchestration system, or governance product.
