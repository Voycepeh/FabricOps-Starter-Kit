## FabricOps Starter Kit

Lightweight, notebook centric, plug and play starter kit for Microsoft Fabric.

FabricOps Starter Kit helps teams quickly bootstrap governed Fabric notebook delivery using reusable templates and a lightweight helper wheel.

It supports a metadata backed workflow from agreement, to pipeline, to governance review, then back into pipeline enforcement.

- 01_da captures the agreement, steward, and context.

- 03_pc pipes data from source to target while capturing key metadata such as data profile, lineage, schema, and data drift details.

- 04_gov uses that metadata to add business context, data quality rules, data sensitivity, and classification.

The approved data quality rules, sensitivity rules, and classification rules are then used by 03_pc when the pipeline runs again, alongside schema and data drift guardrails.


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


-
