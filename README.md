# FabricOps Starter Kit

Lightweight, notebook-centric starter kit for governed, quality-checked, AI-ready notebooks in Microsoft Fabric.

FabricOps Starter Kit helps teams bootstrap Fabric-native metadata setup, agreement intake, notebook registry, production notebook guardrails, profiling evidence, lineage, governance review, and handover without adding a separate platform.

## v1.0.0 scope

FabricOps v1.0.0 uses each `03_pc` production-control notebook as the production boundary. Schema checks, data-change checks, notebook-defined DQ checks, output writes, lineage, profiling evidence, and run summaries live inside the relevant `03_pc` notebook.

Separate data contracts are not required for v1.0.0. `04_gov` is a human review workflow for column context, DQ expectations, and classification metadata; it does not enforce production rules. Governance DQ rules stored in metadata are reviewed expectations and advisory metadata unless a team manually implements them as guardrails inside the relevant `03_pc` notebook.

<div align="center">

[![Open Documentation](https://img.shields.io/badge/Docs-Open%20FabricOps-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/dev/)
[![Start](https://img.shields.io/badge/Start-Use%20Templates-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/dev/quick-start/)
[![Install](https://img.shields.io/badge/Install-Wheel-blue?style=for-the-badge)](https://voycepeh.github.io/FabricOps-Starter-Kit/dev/install/)

</div>

## Documentation map

- [Home](https://voycepeh.github.io/FabricOps-Starter-Kit/dev/)
- [Quick Start](https://voycepeh.github.io/FabricOps-Starter-Kit/dev/quick-start/)
- [How FabricOps Works](https://voycepeh.github.io/FabricOps-Starter-Kit/dev/how-fabricops-works/)
  - [Workspace Operating Model](https://voycepeh.github.io/FabricOps-Starter-Kit/dev/how-fabricops-works/workspace-operating-model/)
  - [Notebook Templates](https://voycepeh.github.io/FabricOps-Starter-Kit/dev/how-fabricops-works/notebook-templates/)
  - [Metadata Tables](https://voycepeh.github.io/FabricOps-Starter-Kit/dev/how-fabricops-works/metadata-tables/)
  - [Table-Scoped Governance](https://voycepeh.github.io/FabricOps-Starter-Kit/dev/how-fabricops-works/table-scoped-governance/)
  - [Metadata Dashboard](https://voycepeh.github.io/FabricOps-Starter-Kit/dev/how-fabricops-works/metadata-dashboard/)
- [Data Quality Rules](https://voycepeh.github.io/FabricOps-Starter-Kit/dev/data-quality-rules-system/)
- [Schema and Data-Change Guardrails](https://voycepeh.github.io/FabricOps-Starter-Kit/dev/schema-and-data-drift/)
- [Setup](https://voycepeh.github.io/FabricOps-Starter-Kit/dev/install/)
- [Function Reference](https://voycepeh.github.io/FabricOps-Starter-Kit/dev/reference/)

## Template quick links

Download and open the templates in Microsoft Fabric for the best experience.

- [`00_env_config`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks/00_env_config.ipynb)
- [`01_da_agreement_template`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks/01_da_agreement_template.ipynb)
- [`02_ex_agreement_topic`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks/02_ex_agreement_topic.ipynb)
- [`03_pc_agreement_pipeline_template`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks/03_pc_agreement_pipeline_template.ipynb)
- [`04_gov_agreement_dataset_table`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks/04_gov_agreement_dataset_table.ipynb)
