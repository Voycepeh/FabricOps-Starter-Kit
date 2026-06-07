# How FabricOps Works

FabricOps Starter Kit is a lightweight way to run governed, quality-checked, AI-ready notebooks in Microsoft Fabric.
It gives teams a practical notebook path for agreeing what to build, running a repeatable pipeline, recording metadata evidence, and reviewing that evidence before operational support.

FabricOps is not a full governance platform or a standalone data quality product. It is a starter kit that helps Fabric notebooks stay understandable, reusable, and easier to support.

## Normal workflow

```mermaid
flowchart LR
    ENV["00_env_config<br/>Environment config<br/>Configures paths and metadata routing"] --> DA["01_agreement<br/>Agreement<br/>Defines what should be built, who owns it,<br/>what rules apply, and what readiness means"]
    DA --> PC["02_pipeline<br/>Pipeline<br/>Builds, transforms, validates,<br/>and publishes the data product"]
    PC --> REV["03_review<br/>Review<br/>Checks evidence, metadata, ownership,<br/>rules, and readiness"]
    EXP["99_explore<br/>Optional support<br/>Discovery, profiling, troubleshooting,<br/>investigation, and ad hoc analysis"] -. supports .-> DA
    EXP -. supports .-> PC
    EXP -. supports .-> REV
```

Run the notebooks in this order for the standard path:

| Step | Notebook | What it does |
| --- | --- | --- |
| 1 | `00_env_config` | Sets workspace paths, lakehouse and warehouse targets, and the `metadata_lakehouse` used by the other notebooks. |
| 2 | `01_agreement` | Captures the agreed purpose, owner, steward, and supporting agreement evidence. |
| 3 | `02_pipeline` | Builds the data product, applies pipeline guardrails, writes outputs, and records metadata evidence. |
| 4 | `03_review` | Reviews the metadata evidence and saves reviewed metadata such as business context, DQ expectations, sensitivity, and classification. |
| Optional | `99_explore` | Supports discovery or troubleshooting. It is not required for the normal workflow. |

The core handoff is simple: `01_agreement` says what should be built, `02_pipeline` builds it and records evidence, and `03_review` adds approved context that people can trust.

## Workspace model

FabricOps works best when shared metadata is kept separate from development and production processing.
A common setup uses three Fabric workspaces:

| Workspace | Typical items | Purpose |
| --- | --- | --- |
| Governance workspace | `metadata_lakehouse` | Stores agreements, metadata evidence, and reviewed metadata for support. |
| Engineering Dev workspace | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` | Develops and tests `02_pipeline` notebooks before production. |
| Engineering Prod workspace | `source_lakehouse`, `unified_lakehouse`, `product_warehouse` | Runs approved production `02_pipeline` notebooks and publishes production outputs. |

![FabricOps Starter Kit operating model with Governance, Engineering Dev, and Engineering Prod workspaces](../assets/fabricops-operating-model-overview.png)

## Where metadata lives

`00_env_config` defines where metadata tables live. The shared metadata target is the Governance workspace `metadata_lakehouse`.

The notebooks use that metadata target to coordinate the workflow:

- `01_agreement` writes agreement, steward, and agreement evidence records.
- `02_pipeline` writes metadata evidence such as profiles, lineage, guardrail results, and notebook run context.
- `03_review` writes reviewed metadata after human review.

Most users should not manually create or maintain the metadata table schemas. `00_env_config` creates and validates the active metadata tables so the other notebooks can read and write them consistently.

## Promotion and production use

Keep production promotion lightweight:

1. Build and test the production-ready `02_pipeline` in Engineering Dev.
2. Promote the notebook to Engineering Prod.
3. Run it with the production `00_env_config`.
4. Let the production notebook create production outputs and production metadata evidence.

Do not copy development outputs into production. Production pipelines should read production configuration and approved production metadata.

## Which page should I read next?

| Page | Use it when you want to... |
| --- | --- |
| [Notebook Templates](notebook-templates.md) | Choose the right notebook and understand the handoff between notebooks. |
| [Metadata Tables](metadata-tables.md) | See the lightweight map of metadata tables and what each table is for. |
| [Pipeline Guardrails](../schema-and-data-drift.md) | Understand the checks that `02_pipeline` can run before writing outputs. |
| [Governance Review](../governance-review.md) | Understand what `03_review` adds and who approves reviewed metadata. |
| [Metadata Dashboard](metadata-dashboard.md) | Understand the planned post-v1.0.0 visibility layer. |
