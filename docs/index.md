# FabricOps Starter Kit

FabricOps Starter Kit is a lightweight Microsoft Fabric notebook starter kit for governed, quality-checked, AI-ready notebooks.

FabricOps enables a metadata-backed notebook workflow from agreement, to production, to governance review, to handover:

- `01_da` captures agreement, steward, and evidence context.
- `03_pc` produces guarded production outputs and evidence.
- `04_gov` reviews evidence into approved governance metadata.
- Handover uses collected evidence instead of memory or side conversations.

FabricOps v1.0.0 is not a full governance platform and not a standalone data quality product. It keeps the operating model small so teams can use Fabric notebooks, shared metadata, and reviewed evidence without adding a separate platform.

<div class="home-cta" markdown="1">

[Quick Start](quick-start.md){ .md-button .md-button--primary }

[How FabricOps Works](how-fabricops-works/index.md){ .md-button }

</div>

## Where to go

| Page | Use it for |
| --- | --- |
| [How FabricOps Works](how-fabricops-works/index.md) | Start here to understand how the v1.0.0 system is structured across workspaces, notebooks, metadata, and handover evidence. |
| [Production Guardrails Workflow](schema-and-data-drift.md) | Read after How FabricOps Works; explains how `03_pc` owns schema checks, data-change monitoring, notebook-defined checks, output writes, lineage, and run evidence. |
| [Governance Review Workflow](data-quality-rules-system.md) | Read after How FabricOps Works; explains how `04_gov` reviews profile evidence and commits column context, DQ expectations, and classifications. |
| [Quick Start](quick-start.md) | Install the helper wheel, copy the templates, and run a Fabric smoke test. |
| [Function Reference](reference/index.md) | Look up helper functions used by the notebooks. |

## Recommended path

New users should read **How FabricOps Works**, then the two **Workflow Guides**, then use **Quick Start** to test the notebook flow in Fabric.
