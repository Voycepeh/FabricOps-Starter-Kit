# How FabricOps Works

FabricOps Starter Kit is a Fabric-native notebook operating model for metadata setup, agreement intake, exploration, production notebook guardrails, profiling evidence, lineage, governance review, and handover.

It is not a full data product platform. It gives teams a small, reusable structure for running quality-checked notebooks in Microsoft Fabric and storing the evidence needed for governance and support.

## v1.0.0 scope

In v1.0.0, the production control boundary is each `03_pc` notebook. That notebook owns the implemented guardrails for its pipeline: schema checks, data-change checks, notebook-defined DQ checks, output writes, lineage records, profiling evidence, and run summaries.

Separate data contracts are not required for v1.0.0. Data agreements remain part of `01_da`, but they are intake and stewardship metadata rather than a separate enforcement layer.

`04_gov` is a human review workflow for column context, DQ expectations, and classification metadata. It does not enforce production rules. Governance DQ rules stored in metadata are reviewed expectations and advisory metadata unless a team manually implements them as guardrails inside the relevant `03_pc` notebook.

AI suggestions are optional and advisory only. A human must review and commit governance metadata.

## Implemented in v1.0.0

| Capability | Primary template or component |
| --- | --- |
| Metadata lakehouse setup | `00_env_config` |
| Data agreement, steward, and evidence tables | `01_da` |
| Notebook registry | `00_env_config`, `02_ex`, `03_pc` |
| Production notebook template with schema validation and data-change monitoring | `03_pc` |
| Lakehouse and warehouse IO helpers | `fabricops_kit` helper wheel |
| Profiling/catalogue evidence | `02_ex`, `03_pc` |
| Lineage records | `03_pc` |
| Table-scoped governance review | `04_gov` |
| Human-reviewed column context, DQ expectation, and classification metadata | `04_gov` |
| Handover summary support | Handover helpers and stored notebook evidence |

## Planned after v1.0.0

| Planned enhancement | Notes |
| --- | --- |
| Full Fabric validation notes from real workspace testing | Expand release evidence from representative workspaces. |
| Governance dashboard improvements | Improve dashboard starter assets and reporting guidance. |
| Optional metadata-driven DQ rule execution | Allow pipelines to opt into executing reviewed metadata rules. |
| Rule promotion workflow | Promote reviewed expectations into implemented `03_pc` guardrails. |
| Richer AI-assisted governance suggestions | Keep AI optional, advisory, and human-reviewed. |
| More complete operational monitoring | Add broader run health and support views. |

## Notebook flow

| Step | Notebook | What it does |
| ---: | --- | --- |
| 0 | `00_env_config` | Prepares environment paths and creates or validates metadata tables. |
| 1 | `01_da` | Captures agreement, steward, and evidence metadata. |
| 2 | `02_ex` | Demonstrates example source/topic setup, exploration, profiling, and catalogue evidence. |
| 3 | `03_pc` | Runs the production-control flow with schema/data-change guardrails, writes outputs, records profiles, writes lineage, and produces run evidence. |
| 4 | `04_gov` | Reviews and commits governance metadata for column context, DQ expectations, and classifications. |
| 5 | Rerun `03_pc` | Confirms the production notebook still passes its implemented guardrails; manually implemented governance expectations can be enforced here. |

## Metadata evidence

FabricOps stores metadata evidence in a configured metadata lakehouse. `00_env_config` owns metadata target routing and table setup. Workflow notebooks append or read metadata; they do not create their own separate metadata stores.

Key metadata themes are:

- agreement, steward, and evidence metadata;
- notebook registration and run traceability;
- profiling/catalogue evidence;
- lineage records;
- reviewed column context;
- reviewed DQ expectations;
- reviewed classification metadata;
- handover summaries.

## What to read next

| Page | Use it for |
| --- | --- |
| [Workspace Operating Model](workspace-operating-model.md) | Set up Fabric workspaces and promotion boundaries. |
| [Notebook Templates](notebook-templates.md) | Understand what each template owns. |
| [Metadata Tables](metadata-tables.md) | Review metadata table responsibilities. |
| [Table-Scoped Governance](table-scoped-governance.md) | Understand `04_gov` human review. |
| [Metadata Dashboard](metadata-dashboard.md) | See planned dashboard/reporting guidance. |
