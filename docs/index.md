# FabricOps Starter Kit

FabricOps Starter Kit helps engineering and analytics teams quickly bootstrap governance and engineering practices in Microsoft Fabric.

It provides a simple starting point for metadata-driven processing, data lineage, data quality checks, and notebook standardisation within the team’s existing Fabric environment.

<div class="home-cta" markdown="1">

[Start Quickly](quick-start.md){ .md-button .md-button--primary }
[How FabricOps Works](how-fabricops-works/index.md){ .md-button }

</div>

## The problem it solves

Analysts, engineers, and governance teams often work differently.

FabricOps Starter Kit gives them a shared structure through role-based notebooks and metadata tables, so analysis, engineering standards, data quality checks, lineage, and governance evidence stay connected as the work is done.

<figure markdown>
  ![FabricOps Starter Kit operating model with Governance, Engineering Dev, and Engineering Prod workspaces](assets/fabricops-operating-model-overview.png){ .full-width }
  <figcaption>FabricOps Starter Kit uses one config notebook, role-based templates, and shared metadata to coordinate governance and engineering delivery.</figcaption>
</figure>

## What you get

| Outcome | What FabricOps provides |
| --- | --- |
| Clear role handoffs | `00_env_config`, `01_da`, `02_ex`, `03_pc`, and `04_gov` give each role a focused notebook. |
| Reusable metadata | Agreements, profiles, lineage, rules, classifications, and business context are stored as shared evidence. |
| Lightweight enforcement | Production notebooks consume approved metadata and apply repeatable DQ and drift checks. |
| AI-ready documentation | Approved metadata and notebook evidence can generate handover summaries, AI manifests, and support notes. |
| Practical Fabric adoption | Uses normal Fabric workspaces, lakehouses, warehouses, and notebooks instead of adding a large platform. |

## How it works

1. Configure the Fabric environment with `00_env_config`.
2. Create steward and agreement records with `01_da`.
3. Explore and profile data with `02_ex`.
4. Build repeatable transformations with `03_pc`.
5. Enrich and approve governance metadata with `04_gov`.
6. Rerun production pipelines with approved metadata and generate handover evidence.

The [How FabricOps Works](how-fabricops-works/index.md) section explains the workspace setup, notebook templates, metadata tables, assembled views, role handoffs, and production handover as one guided story.

## Start here

- [Quick Start](quick-start.md): install the helper wheel, copy the templates, and configure Fabric.
- [How FabricOps Works](how-fabricops-works/index.md): follow the complete lightweight story from workspace setup to handover.
- [Notebook Templates](how-fabricops-works/notebook-templates.md): understand the role-based notebook sequence.
- [Data Quality Rules](data-quality-rules-system.md): apply approved checks in pipeline notebooks.
