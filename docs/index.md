# FabricOps Starter Kit

FabricOps Starter Kit is a lightweight Microsoft Fabric notebook starter kit for governed, quality-checked, AI-ready notebooks.

It helps governance teams, analysts, and engineers use a shared notebook flow for metadata setup, agreement intake, exploration, production guardrails, profiling evidence, lineage, governance review, and handover. The kit stays Fabric-native: notebooks run in Fabric, metadata is stored in a metadata lakehouse, and production checks live in the production-control notebook.

## v1.0.0 scope

In v1.0.0, the production control boundary is each `03_pc` notebook. Schema checks, data-change checks, notebook-defined DQ checks, output writes, lineage records, profiling evidence, and run summaries act as the pipeline guardrails.

Separate data contracts are not required for v1.0.0. Data agreements from `01_da` remain part of the operating flow, but the enforceable production rules are the checks implemented in the relevant `03_pc` notebook.

`04_gov` is a human review workflow for column context, DQ expectations, and classification metadata. It does not enforce production rules. Governance DQ rules stored in metadata are reviewed expectations and advisory metadata unless a team manually implements them as `03_pc` guardrails. AI suggestions are optional and advisory only.

## Implemented in v1.0.0

| Capability | Where it lives |
| --- | --- |
| Metadata lakehouse setup | `00_env_config` |
| Data agreement, steward, and evidence tables | `01_da` |
| Notebook registry | `00_env_config` and workflow notebooks |
| Production notebook template with schema validation and data-change monitoring | `03_pc` |
| Lakehouse and warehouse IO helpers | `fabricops_kit` helper wheel |
| Profiling/catalogue evidence | `02_ex` and `03_pc` |
| Lineage records | `03_pc` |
| Table-scoped governance review | `04_gov` |
| Human-reviewed column context, DQ expectation, and classification metadata | `04_gov` |
| Handover summary support | Handover helpers and production notebook evidence |

## Planned after v1.0.0

| Planned enhancement | Notes |
| --- | --- |
| Full Fabric validation notes from real workspace testing | Capture release evidence from representative Fabric workspaces. |
| Governance dashboard improvements | Improve reporting views and Power BI starter assets. |
| Optional metadata-driven DQ rule execution | Let pipelines opt into reviewed metadata rules. |
| Rule promotion workflow | Promote approved expectations into enforceable notebook checks. |
| Richer AI-assisted governance suggestions | Keep AI advisory and human-reviewed. |
| More complete operational monitoring | Add broader run health and support visibility. |

<div class="home-cta" markdown="1">

[Quick Start](quick-start.md){ .md-button .md-button--primary }

[How FabricOps Works](how-fabricops-works/index.md){ .md-button }

</div>

## Where to go

| Page | Use it for |
| --- | --- |
| [Quick Start](quick-start.md) | Install the helper wheel, copy templates, and smoke test the v1 notebook flow in Fabric. |
| [How FabricOps Works](how-fabricops-works/index.md) | Understand the workspace model, notebook flow, metadata layer, governance review, and handover process. |
| [Schema and Data-Change Guardrails](schema-and-data-drift.md) | Learn how `03_pc` notebook guardrails stop schema or data-change failures. |
| [Data Quality Rules](data-quality-rules-system.md) | Learn how reviewed DQ expectations are stored for advisory metadata and future enforcement patterns. |
| [Function Reference](reference/index.md) | Look up helper functions used by the notebooks. |

New users should start with **Quick Start**, then read **How FabricOps Works** before editing the notebook templates.
