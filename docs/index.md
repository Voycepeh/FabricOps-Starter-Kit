# FabricOps Starter Kit
FabricOps Starter Kit is a lightweight Microsoft Fabric notebook starter kit.

We adopt a Fabric notebook-first approach for data exploration, data pipelines, and governance.

It helps governance teams, analysts, and engineers work from a shared structure without adding a large platform around Fabric.

These notebooks capture agreements, profiling results, governance review metadata, lineage, data-change checks, and production evidence. The evidence is stored in a metadata lakehouse and can support handover and future dashboard visibility.

The result is a self-contained Fabric workflow for governed notebook delivery without adding a separate platform.

<div class="home-cta" markdown="1">

[Quick Start](quick-start.md){ .md-button .md-button--primary }

[How FabricOps Works](how-fabricops-works/index.md){ .md-button }

</div>

## Where to go

| Page                                                | Use it for                                                                                      |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| [Quick Start](quick-start.md)                       | Install the helper wheel, copy the templates, and configure Fabric.                             |
| [How FabricOps Works](how-fabricops-works/index.md) | Start here to understand the v1.0.0 metadata enabled workflow, production guardrails, governance review, and handover process. |
| [Production Guardrails Workflow](schema-and-data-drift.md) | Learn how `03_pc` owns schema checks, data-change monitoring, notebook-defined checks, output writes, lineage, and run evidence. |
| [Governance Review Workflow](data-quality-rules-system.md) | Learn how `04_gov` reviews profile evidence and commits column context, DQ expectations, and classifications. |
| [Function Reference](reference/index.md)            | Look up helper functions used by the notebooks.                                                 |

## Recommended path

New users should start with **Quick Start**, then read **How FabricOps Works** before editing the notebook templates.
