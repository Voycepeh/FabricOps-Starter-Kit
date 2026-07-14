# FabricOps Starter Kit

FabricOps Starter Kit helps data teams build Microsoft Fabric notebook solutions with a consistent structure for configuration, data processing, governance, lineage, data quality, and operational handover.

It provides:

- reusable Fabric notebook templates
- public Python functions for common Fabric operations
- metadata and governance tables
- data quality and pipeline run tracking
- guided examples for implementing the complete workflow

<div align="center">

[![Open Documentation](https://img.shields.io/badge/Documentation-Open-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/)
[![Guided Demo](https://img.shields.io/badge/Guided-Demo-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/guided-demo/)
[![Releases](https://img.shields.io/badge/View-Releases-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/releases/)

</div>

## Start here

**New to FabricOps**

Follow the [Guided Demo](https://voycepeh.github.io/FabricOps-Starter-Kit/guided-demo/) to set up the required Fabric artifacts and implement the notebook workflow.

**Building a Fabric notebook solution**

Use the notebook templates below as the starting structure for your project.

**Maintaining or releasing FabricOps**

Use the [FabricOps Maintainer Guide](https://voycepeh.github.io/FabricOps-Starter-Kit/maintainer/) for repository maintenance and release preparation.

## Notebook workflow

Download the notebooks and open them directly in Microsoft Fabric for the best experience.

1. [`00_env_config`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb)  
   Configure the Fabric workspace, lakehouses, warehouses, and shared environment settings.

2. [`01_agreement`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/01_agreement.ipynb)  
   Define the data agreement and register the governed source.

3. [`02_pipeline`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb)  
   Read, transform, validate, and write data through the FabricOps pipeline workflow.

4. [`03_governance`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/03_governance.ipynb)  
   Review and publish governance, lineage, data quality, and operational evidence.

5. [`99_explore`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/99_explore.ipynb)  
   Optional utilities for exploring FabricOps metadata and outputs.

## Documentation

The [published documentation site](https://voycepeh.github.io/FabricOps-Starter-Kit/) contains the complete user guides, notebook implementation guidance, metadata reference, public function reference, architecture information, and release documentation.

For AI agents and documentation tooling, FabricOps also publishes an [`llms.txt`](https://voycepeh.github.io/FabricOps-Starter-Kit/llms.txt) navigation file.

## Project status

FabricOps is developed and tested around Microsoft Fabric notebook workflows. See the [release pages](https://voycepeh.github.io/FabricOps-Starter-Kit/releases/) for the functions and capabilities available in each version.
