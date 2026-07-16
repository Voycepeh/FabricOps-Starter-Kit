# FabricOps Starter Kit

FabricOps (Fabric Operations) is a plug-and-play, lightweight starter kit that helps data teams quickly set up and adopt a standardized notebook workflow in Microsoft Fabric.

It is designed for teams working across governance, data engineering, and AI and BI analytics. FabricOps combines a Python package of ready-to-use helper and orchestrator functions, standardized notebook templates, shared metadata tables, a Guided Demo, and technical reference documentation.

By standardizing the workflow, FabricOps weaves essential metadata and governance processes into everyday notebook development. This gives teams a consistent foundation for data quality, lineage, handover, and AI-assisted development without having to build every supporting process from scratch.

<div align="center">

[![Open Documentation](https://img.shields.io/badge/Documentation-Start_Here-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/)
[![How FabricOps Works](https://img.shields.io/badge/How_FabricOps-Works-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/how-fabricops-works/)
[![Guided Demo](https://img.shields.io/badge/Guided-Demo-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/guided-demo/)
[![Releases](https://img.shields.io/badge/View-Releases-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/releases/)

</div>

## Start here

Follow the documentation in this order:

1. [Documentation Home](https://voycepeh.github.io/FabricOps-Starter-Kit/) explains why FabricOps exists, who it supports, and what is included.
2. [How FabricOps Works](https://voycepeh.github.io/FabricOps-Starter-Kit/how-fabricops-works/) shows how the notebooks, Python package, roles, and metadata tables work together.
3. [Guided Demo](https://voycepeh.github.io/FabricOps-Starter-Kit/guided-demo/) takes you through the workflow in Microsoft Fabric.
4. Use the [Notebook Templates](https://voycepeh.github.io/FabricOps-Starter-Kit/notebook-templates-implementation-guide/), [Function Reference](https://voycepeh.github.io/FabricOps-Starter-Kit/reference/), [Metadata Table Reference](https://voycepeh.github.io/FabricOps-Starter-Kit/reference/metadata/), and [DQ Rule Reference](https://voycepeh.github.io/FabricOps-Starter-Kit/reference/dq-rules/) when implementing your own project.

Maintainers should use the [FabricOps Maintainer Guide](https://voycepeh.github.io/FabricOps-Starter-Kit/maintainer/) for repository maintenance and release preparation.

## Notebook workflow

Download the notebooks and open them directly in Microsoft Fabric. The main workflow uses:

1. [`00_env_config`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb) for shared environment and metadata configuration.
2. [`01_agreement`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_agreement.ipynb) for steward and agreement context.
3. [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb) for governed source-to-target processing, profiling, lineage, and guardrail enforcement.
4. [`03_governance`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/03_governance.ipynb) for metadata enrichment and guardrail review.
5. [`99_explore`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/99_explore.ipynb) for optional exploration and troubleshooting.

The [Notebook Templates guide](https://voycepeh.github.io/FabricOps-Starter-Kit/notebook-templates-implementation-guide/) explains the role of each notebook. The Guided Demo remains the step-by-step execution guide.

## Documentation and release status

The [published documentation site](https://voycepeh.github.io/FabricOps-Starter-Kit/) contains the complete operating guidance and technical reference. FabricOps also publishes an [`llms.txt`](https://voycepeh.github.io/FabricOps-Starter-Kit/llms.txt) navigation file for AI agents and documentation tooling.

FabricOps is developed and tested around Microsoft Fabric notebook workflows. See [Releases](https://voycepeh.github.io/FabricOps-Starter-Kit/releases/) for the functions and capabilities available in each version.
